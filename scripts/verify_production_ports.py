"""Check production database/cache listeners in an isolated synthetic Docker project."""
from __future__ import annotations

import ipaddress
import json
import subprocess
import time
import uuid
from pathlib import Path

from staging import environment, require_local_engine

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / ".agent-workflow/reports"
PASSWORD = "synthetic-port-fixture-only"


def main():
    require_local_engine()
    project = "pakodi_ports_fixture_" + uuid.uuid4().hex[:12]
    folder = REPORTS / project
    folder.mkdir(parents=True)
    assert folder.resolve().is_relative_to(REPORTS.resolve())
    (folder / "owner").mkdir()
    (folder / "owner/postgres_password").write_text(PASSWORD, encoding="utf-8")
    # Retain a legacy config port to prove the production CLI override wins.
    (folder / "redis.conf").write_text(
        "port 6379\nappendonly yes\nmaxmemory-policy noeviction\nrequirepass " + PASSWORD + "\n",
        encoding="utf-8",
    )
    env = {
        **environment(),
        "PAKODI_HOST": "ports.example.invalid",
        "PAKODI_SECRETS_DIR": str(folder),
        "DEPLOYMENT_ENV": "preview",
        "SITE_INDEXABLE": "false",
        "GA4_MEASUREMENT_ID": "",
        "META_PHONE_ID": "",
        "META_GRAPH_VERSION": "",
    }

    def docker(*args, check=True):
        return subprocess.run(
            ["docker", *args], cwd=ROOT, env=env, check=check,
            capture_output=True, text=True,
        )

    # Render only synthetic options; never inherit the operator's network choice.
    rendered = None
    for prefix, expected in ((None, "172.29.91"), ("", "172.29.91"), ("10.253.91", "10.253.91")):
        env.pop("PAKODI_NETWORK_PREFIX", None)
        if prefix is not None:
            env["PAKODI_NETWORK_PREFIX"] = prefix
        rendered = json.loads(docker(
            "compose", "-f", "compose.production.yaml", "--profile", "operations",
            "config", "--format", "json",
        ).stdout)
        subnet = rendered["networks"]["private"]["ipam"]["config"][0]["subnet"]
        proxy = rendered["services"]["proxy"]["networks"]["private"]["ipv4_address"]
        trusted = rendered["services"]["api"]["environment"]["TRUSTED_PROXY_IPS"]
        assert subnet == expected + ".0/24", subnet
        assert proxy == trusted == expected + ".10", (proxy, trusted)
        assert ipaddress.ip_address(proxy) in ipaddress.ip_network(subnet)
    print("Production network rendering passed: default, empty/custom prefixes; exact proxy trust.")
    published = {
        name: [(str(port["published"]), port["target"]) for port in service.get("ports", [])]
        for name, service in rendered["services"].items() if service.get("ports")
    }
    assert published == {"proxy": [("80", 80), ("443", 443)]}, published
    services = {}
    for name in ("postgres", "redis"):
        original = rendered["services"][name]
        services[name] = {
            key: original[key] for key in ("image", "command", "environment", "healthcheck")
            if key in original
        }
        services[name]["networks"] = ["private"]
    services["postgres"]["volumes"] = [
        "postgres:/var/lib/postgresql",
        {"type": "bind", "source": str(folder / "owner/postgres_password"),
         "target": "/run/secrets/postgres_password", "read_only": True},
    ]
    services["redis"]["volumes"] = [
        "redis:/data",
        {"type": "bind", "source": str(folder / "redis.conf"),
         "target": "/run/secrets/redis.conf", "read_only": True},
    ]
    compose = folder / "compose.json"
    compose.write_text(json.dumps({
        "services": services, "volumes": {"postgres": {}, "redis": {}},
        "networks": {"private": {"internal": True}},
    }, indent=2), encoding="utf-8")

    def command(*args, check=True):
        return docker("compose", "-f", str(compose), "-p", project, *args, check=check)

    def sql(query):
        return command(
            "exec", "-T", "-e", "PGPASSWORD=" + PASSWORD, "postgres", "psql",
            "-h", "postgres", "-U", "pakodi_owner", "-d", "pakodi", "-Atc", query,
        ).stdout.strip()

    def redis(*args, authenticated=True, check=True):
        options = ["-e", "REDISCLI_AUTH=" + PASSWORD] if authenticated else []
        return command(
            "exec", "-T", *options, "redis", "redis-cli", "--raw", "-h", "redis",
            "-p", "6380", *args, check=check,
        ).stdout.strip()

    def ready():
        command("up", "-d", "--wait", "--wait-timeout", "90")
        for _ in range(30):
            if redis("PING", check=False) == "PONG":
                return
            time.sleep(0.5)
        raise RuntimeError("Fixture Redis readiness timed out")

    try:
        ready()
        assert sql("SELECT inet_server_port()") == "5433"
        assert "NOAUTH" in redis("PING", authenticated=False, check=False)
        assert redis("CONFIG", "GET", "appendonly") == "appendonly\nyes"
        assert redis("CONFIG", "GET", "maxmemory-policy") == "maxmemory-policy\nnoeviction"
        assert command(
            "exec", "-T", "postgres", "pg_isready", "-h", "postgres", "-p", "5432",
            check=False,
        ).returncode != 0
        assert command(
            "exec", "-T", "redis", "redis-cli", "-p", "6379", "PING", check=False,
        ).returncode != 0
        for identifier in command("ps", "-q").stdout.split():
            inspected = json.loads(docker("inspect", identifier).stdout)[0]
            assert not inspected["HostConfig"].get("PortBindings")
        sql("CREATE TABLE port_fixture(value text); INSERT INTO port_fixture VALUES('retained')")
        assert redis("SET", "port-fixture", "retained") == "OK"
        command("restart", "postgres", "redis")
        ready()
        assert sql("SELECT value FROM port_fixture") == "retained"
        assert redis("GET", "port-fixture") == "retained"
        (folder / "summary.json").write_text(json.dumps({
            "postgres_port": 5433, "redis_port": 6380, "postgres_health": "passed",
            "authenticated_clients": "passed", "old_ports_closed": "passed",
            "host_port_bindings": "none", "restart_persistence": "passed",
            "production_host_accessed": False,
        }, indent=2), encoding="utf-8")
        print("Production port fixtures passed: PostgreSQL 5433, Redis 6380; "
              "private, authenticated and persistent.")
        print("Evidence: " + str(folder / "summary.json"))
    finally:
        # Only this generated project's resources may be removed, including after failure.
        for identifier in command("ps", "-aq").stdout.split():
            inspected = json.loads(docker("inspect", identifier).stdout)[0]
            if inspected["Config"]["Labels"].get("com.docker.compose.project") != project:
                raise RuntimeError("Refusing cleanup of a different Docker project")
        command("down", "--volumes", "--remove-orphans")


if __name__ == "__main__":
    main()
