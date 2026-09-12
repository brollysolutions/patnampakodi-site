#!/usr/bin/env python3
"""Set up or update Pakodi on a Linux Docker server; never remove deployment data."""

from __future__ import annotations

import argparse
import base64
import errno
import inspect
import ipaddress
import json
import os
import re
import secrets
import socket
import stat
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULTS = {
    "PAKODI_HOST": "patnampakodi.com",
    "PAKODI_SECRETS_DIR": "/srv/pakodi-secrets",
    "DEPLOYMENT_ENV": "preview",
    "SITE_INDEXABLE": "false",
    "META_PHONE_ID": "",
    "META_GRAPH_VERSION": "",
    "GA4_MEASUREMENT_ID": "",
}
KEYS = {*DEFAULTS, "PAKODI_NETWORK_PREFIX"}
CORE_FILES = (
    "owner/postgres_password",
    "owner/migration_database_url",
    "api/database_url",
    "api/commerce_database_url",
    "api/redis_url",
    "api/data_encryption_key",
    "redis.conf",
)
PROVIDER_FILES = tuple(
    "api/" + name
    for name in (
        "razorpay_key_id",
        "razorpay_key_secret",
        "razorpay_webhook_secret",
        "meta_access_token",
        "meta_app_secret",
        "meta_verify_token",
    )
)


def check_runtime():
    """Run inside the migration image; never output a secret or a connection URL."""
    import psycopg
    from app.config import setting, validate_runtime
    from redis import Redis

    validate_runtime()
    for name, expected in (
        ("DATABASE_URL", "pakodi_reader"),
        ("COMMERCE_DATABASE_URL", "pakodi_app"),
    ):
        with psycopg.connect(setting(name), connect_timeout=5) as connection:
            role = connection.execute(
                "SELECT current_user, rolsuper, rolbypassrls FROM pg_roles WHERE rolname=current_user"
            ).fetchone()
            if role != (expected, False, False):
                raise RuntimeError("Restricted runtime role required")
    if not Redis.from_url(
        setting("REDIS_URL"), socket_connect_timeout=5, socket_timeout=5
    ).ping():
        raise RuntimeError("Redis authentication/readiness check failed")


class DeploymentError(RuntimeError):
    """An operator-actionable failure without credentials in the message."""


def environment(options=None):
    # Files are parsed as data, never sourced. Ambient overrides cannot redirect
    # this command to another Compose project or inject extra application config.
    result = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("COMPOSE_") and key not in KEYS
    }
    result["COMPOSE_DISABLE_ENV_FILE"] = "1"
    result.update(options or {})
    return result


def run(args, *, env=None, visible=False):
    result = subprocess.run(
        args,
        cwd=ROOT,
        env=env or environment(),
        check=False,
        text=True,
        capture_output=not visible,
    )
    if result.returncode:
        # A provider or database exception can contain credentials. Do not echo
        # captured container output or include it in an exception traceback.
        raise DeploymentError(
            f"Command failed (exit {result.returncode}); deployment stopped."
        )
    return result.stdout or ""


def docker(*args):
    return run(["docker", *args])


def compose(options, *args, visible=False):
    return run(
        [
            "docker",
            "compose",
            "-p",
            "pakodi",
            "-f",
            str(ROOT / "compose.production.yaml"),
            "--profile",
            "operations",
            *args,
        ],
        env=environment(options),
        visible=visible,
    )


def preflight():
    if os.environ.get("DOCKER_CONTEXT"):
        raise DeploymentError(
            "Unset DOCKER_CONTEXT and select the server's local Docker context explicitly."
        )
    try:
        version = docker("compose", "version", "--short").strip().lstrip("v")
    except (DeploymentError, FileNotFoundError) as exc:
        raise DeploymentError(
            "Install Docker Engine and the Docker Compose plugin first. "
            "The command 'docker compose version' must succeed; legacy docker-compose is unsupported."
        ) from exc
    match = re.match(r"(\d+)\.(\d+)\.(\d+)", version)
    if not match or tuple(map(int, match.groups())) < (2, 20, 0):
        raise DeploymentError("Docker Compose 2.20.0 or newer is required.")
    endpoint = os.environ.get("DOCKER_HOST") or json.loads(
        docker(
            "context",
            "inspect",
            "--format",
            "{{json .Endpoints.docker.Host}}",
        )
    )
    if not isinstance(endpoint, str) or not endpoint.startswith("unix://"):
        raise DeploymentError(
            "Run this command on the deployment server using its local Docker socket."
        )
    if docker("info", "--format", "{{.OSType}}").strip() != "linux":
        raise DeploymentError("A running Linux Docker Engine is required.")


def safe_path(path):
    path = Path(os.path.abspath(path))
    if path.resolve() != path or path.is_symlink():
        raise DeploymentError("Deployment paths must not contain symbolic links.")
    return path


def read_options(path):
    safe_path(path)
    values = {}
    if not path.exists():
        return values
    for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, value = line.partition("=")
        key, value = key.strip(), value.strip()
        if not separator or key not in KEYS or key in values:
            raise DeploymentError(
                f"Invalid or duplicate non-secret runtime option at line {number}."
            )
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if re.search(r"[\s$`#\"'\\]", value):
            raise DeploymentError(
                f"Use a literal value without shell expansion at line {number}."
            )
        values[key] = value
    return values


def network_inventory():
    identifiers = docker("network", "ls", "-q").split()
    networks = (
        json.loads(docker("network", "inspect", *identifiers)) if identifiers else []
    )
    routes = json.loads(run(["ip", "-j", "-4", "route", "show", "table", "all"]))
    return networks, routes


def choose_prefix(configured, networks, routes):
    existing = next(
        (network for network in networks if network["Name"] == "pakodi_private"), None
    )
    if existing:
        labels = existing.get("Labels") or {}
        if labels.get("com.docker.compose.project") != "pakodi":
            raise DeploymentError(
                "The pakodi_private network belongs to another application."
            )
        subnets = [
            entry["Subnet"]
            for entry in existing["IPAM"].get("Config") or []
            if ":" not in entry.get("Subnet", "") and entry.get("Subnet")
        ]
        if len(subnets) != 1 or ipaddress.ip_network(subnets[0]).prefixlen != 24:
            raise DeploymentError("The existing Pakodi network needs operator review.")
        current = subnets[0].split("/")[0].rsplit(".", 1)[0]
        if configured and configured != current:
            raise DeploymentError(
                "Configured subnet differs from the existing Pakodi network; use the documented maintenance procedure."
            )
        return current
    occupied = [
        ipaddress.ip_network(entry["Subnet"], strict=False)
        for network in networks
        for entry in (network.get("IPAM", {}).get("Config") or [])
        if entry.get("Subnet") and ":" not in entry["Subnet"]
    ]
    occupied += [
        ipaddress.ip_network(route["dst"], strict=False)
        for route in routes
        if route.get("dst") and route["dst"] != "default"
    ]
    candidates = list(
        dict.fromkeys(
            ([configured] if configured else [])
            + ["10.253.91", "172.29.91", "10.254.91", "192.168.251"]
        )
    )
    for prefix in candidates:
        try:
            subnet = ipaddress.ip_network(prefix + ".0/24")
        except ValueError as exc:
            raise DeploymentError(
                "PAKODI_NETWORK_PREFIX must contain three IPv4 octets."
            ) from exc
        private_ranges = ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")
        if not any(
            subnet.subnet_of(ipaddress.ip_network(block)) for block in private_ranges
        ):
            raise DeploymentError("Use an RFC1918 private Docker subnet.")
        if not any(subnet.overlaps(other) for other in occupied):
            return prefix
    raise DeploymentError(
        "No free configured/candidate Docker subnet. Set PAKODI_NETWORK_PREFIX to a free private /24 prefix in runtime.env."
    )


def exclusive_write(path, value, mode=0o600):
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
        if os.name == "posix":
            os.fchmod(stream.fileno(), mode)
        stream.write(value)


def check_proxy_ports():
    """Fail before builds/stops when another web server owns a required port."""
    own_ports = set()
    identifiers = docker(
        "ps",
        "--filter",
        "label=com.docker.compose.project=pakodi",
        "--filter",
        "label=com.docker.compose.service=proxy",
        "-q",
    ).split()
    for identifier in identifiers:
        ports = json.loads(
            docker("inspect", "--format", "{{json .NetworkSettings.Ports}}", identifier)
        )
        own_ports.update(
            int(binding["HostPort"])
            for bindings in (ports or {}).values()
            for binding in bindings or []
        )
    for port in (80, 443):
        if port in own_ports:
            continue
        families = [(socket.AF_INET, "0.0.0.0")]
        if socket.has_ipv6:
            families.append((socket.AF_INET6, "::"))
        for family, address in families:
            try:
                with socket.socket(family, socket.SOCK_STREAM) as probe:
                    if family == socket.AF_INET6:
                        probe.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
                    probe.bind((address, port))
            except OSError as exc:
                if family == socket.AF_INET6 and exc.errno in {
                    errno.EAFNOSUPPORT,
                    errno.EADDRNOTAVAIL,
                }:
                    continue
                raise DeploymentError(
                    f"Host TCP port {port} is already in use. Keep the existing server running; "
                    "this stack needs an operator-reviewed reverse-proxy integration before deployment."
                ) from exc


def prepare_options(path):
    values = read_options(path)
    options = {**DEFAULTS, **values}
    host = options["PAKODI_HOST"]
    if len(host) > 253 or not re.fullmatch(
        r"(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,63}", host
    ):
        raise DeploymentError(
            "PAKODI_HOST must be a domain without a scheme, port or path."
        )
    if options["DEPLOYMENT_ENV"] not in {"preview", "production"} or options[
        "SITE_INDEXABLE"
    ] not in {"true", "false"}:
        raise DeploymentError("Invalid deployment environment or indexability setting.")
    secret_path = Path(options["PAKODI_SECRETS_DIR"])
    if not secret_path.is_absolute():
        raise DeploymentError(
            "PAKODI_SECRETS_DIR must be an absolute directory outside the checkout."
        )
    secret_path = safe_path(secret_path)
    if (
        secret_path == Path(secret_path.anchor)
        or secret_path.is_relative_to(ROOT)
        or ROOT.is_relative_to(secret_path)
    ):
        raise DeploymentError(
            "Keep the secrets directory outside the checkout in a dedicated directory."
        )
    options["PAKODI_NETWORK_PREFIX"] = choose_prefix(
        values.get("PAKODI_NETWORK_PREFIX"), *network_inventory()
    )
    if not path.exists():
        exclusive_write(
            path,
            "# Server-specific non-secret options; do not commit.\n"
            + "".join(f"{key}={value}\n" for key, value in options.items()),
        )
        print(f"Created {path.name} for {host}.", flush=True)
    elif set(options) - set(values):
        # Preserve every supplied value, comment and byte. Append only missing
        # defaults, so retries retain the selected free subnet.
        with path.open("a", encoding="utf-8") as stream:
            stream.write(
                "\n"
                + "".join(
                    f"{key}={options[key]}\n" for key in options if key not in values
                )
            )
    if (
        values.get("PAKODI_NETWORK_PREFIX")
        and values["PAKODI_NETWORK_PREFIX"] != options["PAKODI_NETWORK_PREFIX"]
    ):
        # Only reached when no Pakodi network exists. Preserve other options and
        # comments, while replacing the overlapping subnet in one atomic rename.
        revised = re.sub(
            r"(?m)^\s*PAKODI_NETWORK_PREFIX\s*=.*$",
            "PAKODI_NETWORK_PREFIX=" + options["PAKODI_NETWORK_PREFIX"],
            path.read_text(encoding="utf-8-sig"),
        )
        temporary = path.with_name(path.name + "." + secrets.token_hex(6) + ".tmp")
        exclusive_write(temporary, revised)
        os.replace(temporary, path)
        print(
            "Selected free private subnet "
            + options["PAKODI_NETWORK_PREFIX"]
            + ".0/24; saved runtime options.",
            flush=True,
        )
    return options


def prepare_secrets(folder, data_exists):
    folder = safe_path(folder)
    if folder.exists():
        for relative in (*CORE_FILES, *PROVIDER_FILES):
            path = safe_path(folder / relative)
            if not path.is_file() or (
                relative in CORE_FILES and path.stat().st_size == 0
            ):
                raise DeploymentError(
                    f"Existing secrets are incomplete: {relative}. Restore/provision them; nothing was overwritten."
                )
        print("Preserving existing secret files.", flush=True)
        return
    if data_exists:
        raise DeploymentError(
            "Deployment volumes already exist but the secrets directory is missing. Restore the original secrets; credentials will not be regenerated."
        )
    # A crash leaves a partial directory and the next run fails closed. Never
    # regenerate a password/key that could already be attached to persisted data.
    folder.mkdir(mode=0o700)
    for name in ("owner", "api"):
        (folder / name).mkdir(mode=0o750)
        (folder / name).chmod(0o750)
        os.chown(folder / name, 0, 10001)
    passwords = {
        name: secrets.token_urlsafe(36) for name in ("owner", "reader", "app", "redis")
    }
    contents = {
        "owner/postgres_password": passwords["owner"],
        "owner/migration_database_url": f"postgresql://pakodi_owner:{passwords['owner']}@postgres:5433/pakodi",
        "api/database_url": f"postgresql://pakodi_reader:{passwords['reader']}@postgres:5433/pakodi",
        "api/commerce_database_url": f"postgresql://pakodi_app:{passwords['app']}@postgres:5433/pakodi",
        "api/redis_url": f"redis://:{passwords['redis']}@redis:6380/0",
        "api/data_encryption_key": base64.urlsafe_b64encode(
            secrets.token_bytes(32)
        ).decode(),
        "redis.conf": "port 6380\nappendonly yes\nmaxmemory-policy noeviction\nrequirepass "
        + passwords["redis"]
        + "\n",
        **dict.fromkeys(PROVIDER_FILES, ""),
    }
    for relative, value in contents.items():
        path = folder / relative
        exclusive_write(path, value, 0o640)
        os.chown(path, 0, 10001)
    # Redis drops to its image-owned UID. The enclosing host directory is 0700;
    # only this file is mounted in Redis, so it must be readable inside it.
    (folder / "redis.conf").chmod(0o644)
    print(
        "Generated restricted core credentials. Live provider files are blank.",
        flush=True,
    )


def confirm_backup(confirmed):
    if confirmed:
        return
    if (
        not sys.stdin.isatty()
        or input(
            "Existing deployment: confirm a verified database/media/secret backup and a maintenance window. Type BACKUP READY: "
        )
        != "BACKUP READY"
    ):
        raise DeploymentError(
            "Update cancelled before service changes. Prepare a verified backup; use --backup-confirmed only after verification."
        )


def deploy(options, data_exists, backup_confirmed):
    print("Validating configuration and building images...", flush=True)
    compose(options, "config", "--quiet")
    compose(options, "build", visible=True)
    if data_exists:
        confirm_backup(backup_confirmed)
    print("Stopping application writers; preserving all volumes...", flush=True)
    compose(options, "stop", "proxy", "web", "api", "worker")
    compose(options, "up", "-d", "--wait", "--wait-timeout", "120", "postgres", "redis")
    state = compose(
        options,
        "exec",
        "-T",
        "postgres",
        "psql",
        "-U",
        "pakodi_owner",
        "-d",
        "pakodi",
        "-At",
        "-v",
        "ON_ERROR_STOP=1",
        "-c",
        "SELECT (SELECT count(*) FROM pg_roles WHERE rolname IN ('pakodi_reader','pakodi_app')) || '|' || (SELECT count(*) FROM pg_tables WHERE schemaname='public');",
    ).strip()
    if state == "0|0":
        print("Provisioning restricted database roles...", flush=True)
        compose(
            options,
            "run",
            "--rm",
            "--no-deps",
            "-T",
            "migrate",
            "python",
            "-m",
            "app.bootstrap_roles",
        )
    elif not re.fullmatch(r"2\|\d+", state):
        raise DeploymentError(
            "Database is partially initialized or unexpected. Restore/reconcile roles before retrying; no bootstrap or migration was run."
        )
    print("Checking credentials and applying migrations...", flush=True)
    compose(
        options,
        "run",
        "--rm",
        "--no-deps",
        "-T",
        "migrate",
        "python",
        "-c",
        inspect.getsource(check_runtime) + "\ncheck_runtime()\n",
    )
    compose(options, "run", "--rm", "--no-deps", "-T", "migrate")
    compose(
        options,
        "run",
        "--rm",
        "--no-deps",
        "-T",
        "migrate",
        "python",
        "-m",
        "app.seed",
        "--published-only",
    )
    print("Starting application and proxy...", flush=True)
    compose(
        options,
        "up",
        "-d",
        "--wait",
        "--wait-timeout",
        "180",
        "api",
        "worker",
        "web",
        "proxy",
    )
    compose(options, "ps", visible=True)
    admins = compose(
        options,
        "exec",
        "-T",
        "postgres",
        "psql",
        "-U",
        "pakodi_owner",
        "-d",
        "pakodi",
        "-At",
        "-v",
        "ON_ERROR_STOP=1",
        "-c",
        "SELECT count(*) FROM admins;",
    ).strip()
    if admins == "0":
        if sys.stdin.isatty():
            username = (
                input("First administrator username [operator]: ").strip() or "operator"
            )
            if not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9._-]{2,63}", username):
                raise DeploymentError(
                    "Use 3-64 letters, digits, dots, underscores or hyphens for the username."
                )
            compose(
                options,
                "exec",
                "api",
                "python",
                "-m",
                "app.admin_cli",
                "create",
                username,
                visible=True,
            )
        else:
            raise DeploymentError(
                "Containers started but no administrator exists. Rerun this command in an interactive terminal to create one."
            )
    print(
        f"Containers started for https://{options['PAKODI_HOST']}. DNS/public TLS and live providers still require server acceptance."
    )


@contextmanager
def deployment_lock(path="/var/lock/patnam-pakodi-deploy.lock"):
    import fcntl

    descriptor = os.open(
        path,
        os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW,
        0o600,
    )
    with os.fdopen(descriptor, "w") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_uid != 0:
            raise DeploymentError("Unsafe deployment lock file.")
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise DeploymentError("Another Pakodi deployment is running.") from exc
        yield


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--runtime-file",
        type=Path,
        help="Existing non-secret options file; defaults to repository-root runtime.env",
    )
    parser.add_argument(
        "--backup-confirmed",
        action="store_true",
        help="Operator has verified backups and approved the maintenance window",
    )
    args = parser.parse_args(argv)
    if not sys.platform.startswith("linux") or os.geteuid() != 0:
        print(
            "Run on the Linux deployment server: sudo python3 scripts/deploy.py",
            file=sys.stderr,
        )
        return 1
    try:
        with deployment_lock():
            preflight()
            check_proxy_ports()
            path = args.runtime_file or ROOT / "runtime.env"
            if (
                not args.runtime_file
                and not path.exists()
                and (ROOT / "infra/runtime.env").exists()
            ):
                path = ROOT / "infra/runtime.env"
            # Do not silently abandon custom-project data or operator options.
            containers = docker(
                "ps", "-a", "--filter", "label=com.docker.compose.project=pakodi", "-q"
            ).split()
            volumes = docker("volume", "ls", "--format", "{{.Name}}").split()
            data_exists = bool(
                containers
                or any(
                    name in volumes
                    for name in (
                        "pakodi_postgres",
                        "pakodi_redis",
                        "pakodi_media",
                        "pakodi_caddy_data",
                        "pakodi_caddy_config",
                    )
                )
            )
            options = prepare_options(path)
            prepare_secrets(Path(options["PAKODI_SECRETS_DIR"]), data_exists)
            deploy(options, data_exists, args.backup_confirmed)
        return 0
    except (DeploymentError, OSError, ValueError, EOFError) as exc:
        message = (
            str(exc)
            if isinstance(exc, DeploymentError)
            else "Host setup check failed; verify permissions, Docker and iproute2. No automatic rollback was attempted."
        )
        print(message, file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print(
            "Deployment interrupted. State and volumes retained; inspect before retrying.",
            file=sys.stderr,
        )
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
