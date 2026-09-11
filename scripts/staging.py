"""Start or inspect the fixed local Docker review environment; preserve its data."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = ROOT / "compose.staging.yaml"


def environment():
    # Do not let ambient Compose overrides select another project or env file.
    result = {
        key: value
        for key, value in os.environ.items()
        if key
        not in {
            "COMPOSE_FILE",
            "COMPOSE_PROJECT_NAME",
            "COMPOSE_PROFILES",
            "COMPOSE_ENV_FILES",
        }
    }
    result["COMPOSE_DISABLE_ENV_FILE"] = "1"
    return result


def command(*args, capture=False):
    return subprocess.run(
        ["docker", "compose", "-f", str(COMPOSE), "-p", "pakodi-stage", *args],
        cwd=ROOT,
        env=environment(),
        check=True,
        text=True,
        capture_output=capture,
    )


def require_local_engine():
    endpoint = os.environ.get("DOCKER_HOST", "")
    if endpoint and not endpoint.startswith(("unix://", "npipe://")):
        raise RuntimeError("Local staging requires a local Docker socket")
    result = subprocess.run(
        ["docker", "context", "inspect", "--format", "{{json .Endpoints.docker.Host}}"],
        env=environment(),
        check=True,
        text=True,
        capture_output=True,
    )
    endpoint = json.loads(result.stdout)
    if not isinstance(endpoint, str) or not endpoint.startswith(
        ("unix://", "npipe://")
    ):
        raise RuntimeError("Select a local Docker context before running local staging")


def validate_config(config):
    if set(config["networks"]) != {"private", "web-entry"} or not config["networks"][
        "private"
    ].get("internal"):
        raise RuntimeError("Local staging requires a private backend network")
    if not {"migrate", "seed"}.issubset(config["services"]):
        raise RuntimeError(
            "Include the operations profile when rendering staging configuration"
        )
    for name, service in config["services"].items():
        expected = {"private", "web-entry"} if name == "web" else {"private"}
        if set(service.get("networks", {})) != expected:
            raise RuntimeError(
                "Only the web entry may join the port-publishing network"
            )
        for port in service.get("ports", []):
            if (
                name != "web"
                or port.get("host_ip") != "127.0.0.1"
                or str(port.get("published")) != "3500"
                or port.get("target") != 3500
                or port.get("protocol", "tcp") != "tcp"
            ):
                raise RuntimeError("Only loopback web port 3500 may be published")
        values = service.get("environment", {})
        if name in {"api", "worker", "fixture-provider"} and (
            values.get("PROVIDER_MODE") != "fixtures"
            or values.get("APP_ENV") != "staging"
            or values.get("PUBLIC_ORIGIN") != "http://127.0.0.1:3500"
        ):
            raise RuntimeError("Local staging requires local provider fixtures")
    if config["services"]["web"]["environment"].get("SITE_INDEXABLE") != "false":
        raise RuntimeError("Local staging must be noindex")


def wait_for_web(origin):
    for _ in range(20):
        try:
            with urlopen(origin + "/", timeout=2) as response:
                if response.status == 200:
                    return
        except OSError:
            pass
        time.sleep(0.5)
    raise RuntimeError("Staging web port is not reachable from the local host")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["up", "down", "status"])
    args = parser.parse_args()
    require_local_engine()
    validate_config(
        json.loads(
            command(
                "--profile", "operations", "config", "--format", "json", capture=True
            ).stdout
        )
    )
    if args.action == "up":
        command("build", "api", "web")
        command("up", "-d", "--wait", "postgres", "redis")
        command("run", "--rm", "migrate")
        command("run", "--rm", "seed")
        command("up", "-d", "--wait", "api", "fixture-provider", "worker", "web")
        wait_for_web("http://127.0.0.1:3500")
        print("Local staging: http://127.0.0.1:3500/ (provider fixtures, noindex)")
        print(
            "No catalog or admin test fixtures were inserted. Follow docs/local-staging.md for operator setup."
        )
    elif args.action == "down":
        command("down")
        print("Local staging stopped; database and media volumes preserved.")
    else:
        command("ps")


if __name__ == "__main__":
    main()
