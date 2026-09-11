"""Exercise Docker staging with a unique disposable project and synthetic data."""

from __future__ import annotations

import json
import os
import re
import shutil
import socket
import subprocess
import uuid
from pathlib import Path

import staging

ROOT = Path(__file__).resolve().parents[1]


def main():
    staging.require_local_engine()
    project = "pakodi_stage_fixture_" + uuid.uuid4().hex[:12]
    assert re.fullmatch(r"pakodi_stage_fixture_[a-f0-9]{12}", project)
    folder = ROOT / ".agent-workflow/reports" / project
    folder.mkdir(parents=True)
    config = json.loads(
        staging.command(
            "--profile", "operations", "config", "--format", "json", capture=True
        ).stdout
    )
    staging.validate_config(config)
    # Build the exact staging images before creating any disposable resources.
    staging.command("build", "api", "web")
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    origin = "http://127.0.0.1:" + str(port)
    config["name"] = project
    for name, volume in config["volumes"].items():
        volume["name"] = project + "_" + name
    for name, network in config["networks"].items():
        network["name"] = project + "_" + name
    for name, service in config["services"].items():
        service.pop("build", None)
        values = service.get("environment", {})
        if "APP_ENV" in values:
            values["APP_ENV"] = "test"
        if "PUBLIC_ORIGIN" in values:
            values["PUBLIC_ORIGIN"] = origin
        for key in ["DATABASE_URL", "COMMERCE_DATABASE_URL", "MIGRATION_DATABASE_URL"]:
            if key in values:
                values[key] = values[key].rsplit("/", 1)[0] + "/" + project
        if name == "web":
            service["ports"] = [
                {
                    "target": 3000,
                    "published": str(port),
                    "host_ip": "127.0.0.1",
                    "protocol": "tcp",
                }
            ]
    config["services"]["api"]["volumes"].append(
        {
            "type": "bind",
            "source": str(ROOT / "apps/api/tests/staging_fixture.py"),
            "target": "/tmp/staging_fixture.py",
            "read_only": True,
        }
    )
    filename = folder / "compose.json"
    filename.write_text(json.dumps(config, indent=2), encoding="utf8")
    base = ["docker", "compose", "-f", str(filename), "-p", project]

    def command(*args, capture=False):
        return subprocess.run(
            [*base, *args],
            cwd=ROOT,
            env=staging.environment(),
            check=True,
            text=True,
            capture_output=capture,
        )

    def verify_labels():
        identifiers = command("ps", "-aq", capture=True).stdout.split()
        for identifier in identifiers:
            value = subprocess.run(
                [
                    "docker",
                    "inspect",
                    "--format",
                    '{{index .Config.Labels "com.docker.compose.project"}}',
                    identifier,
                ],
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
            if value != project:
                raise RuntimeError("Refusing another project resource")

    try:
        command("up", "-d", "--wait", "postgres", "redis")
        verify_labels()
        command("exec", "-T", "postgres", "createdb", "-U", "pakodi_owner", project)
        command("run", "--rm", "migrate")
        command("run", "--rm", "seed")
        command("up", "-d", "--wait", "api", "fixture-provider", "worker", "web")
        staging.wait_for_web(origin)
        data = command(
            "exec",
            "-T",
            "-e",
            "PYTHONPATH=/app",
            "api",
            "python",
            "/tmp/staging_fixture.py",
            capture=True,
        ).stdout
        json.loads(data)
        environment = {
            **staging.environment(),
            "STAGING_FIXTURE_PROJECT": project,
            "STAGING_FIXTURE_COMPOSE": str(filename),
            "STAGING_FIXTURE_URL": origin,
            "STAGING_FIXTURE_DATA": data,
        }
        subprocess.run(
            [
                shutil.which("npm.cmd" if os.name == "nt" else "npm") or "npm",
                "exec",
                "--",
                "playwright",
                "test",
                "--config=playwright.staging.config.ts",
            ],
            cwd=ROOT / "apps/web",
            env=environment,
            check=True,
        )
        checks = {
            "one_invoice": "SELECT count(*)=1 FROM orders WHERE invoice_number IS NOT NULL",
            "one_processed_capture": "SELECT count(*)=1 AND bool_and(processed) FROM provider_events WHERE provider='razorpay'",
            "one_primary_payment": "SELECT count(*)=1 FROM payments WHERE status='captured'",
            "one_processed_refund": "SELECT count(*)=1 AND sum(amount)=2000 FROM refunds WHERE status='processed'",
            "delivery_preserved": "SELECT bool_and(status='delivered') FROM orders",
        }
        for name, query in checks.items():
            result = command(
                "exec",
                "-T",
                "postgres",
                "psql",
                "-U",
                "pakodi_owner",
                "-d",
                project,
                "-At",
                "-c",
                query,
                capture=True,
            ).stdout.strip()
            if result != "t":
                raise RuntimeError("Staging invariant failed: " + name)
        (folder / "summary.json").write_text(
            json.dumps(
                {
                    "project": project,
                    "browser": "passed",
                    "invariants": list(checks),
                    "real_providers": False,
                },
                indent=2,
            ),
            encoding="utf8",
        )
        print(
            "Docker checkout, signed replay, provider/worker restart, invoice, delivery, partial refund and messaging fixtures passed."
        )
    except BaseException:
        # Fixtures contain synthetic data only; retain diagnosis locally.
        result = subprocess.run(
            [*base, "logs", "--no-color", "--tail", "100"],
            check=False,
            cwd=ROOT,
            env=staging.environment(),
            text=True,
            capture_output=True,
        )
        (folder / "containers.log").write_text(
            result.stdout + result.stderr, encoding="utf8"
        )
        raise
    finally:
        verify_labels()
        # This generated project and all names above are unique, prefix checked and label verified.
        command("down", "--volumes", "--remove-orphans")


if __name__ == "__main__":
    main()
