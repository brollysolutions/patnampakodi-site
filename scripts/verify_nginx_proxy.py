"""Exercise the internal proxy's trusted and untrusted clients with synthetic data."""

from __future__ import annotations

import ipaddress
import json
import subprocess
import tempfile
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = "python:3.13-slim-bookworm@sha256:ed86c82274b3c69b52fb5820f358f0bd7df0b603332063cb5c6e32bd220c3e6e"
CADDY = "caddy:2-alpine@sha256:5f5c8640aae01df9654968d946d8f1a56c497f1dd5c5cda4cf95ab7c14d58648"
BACKEND = """
import json, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
class Echo(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps({"path": self.path, "headers": dict(self.headers)}).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def log_message(self, *args): pass
threading.Thread(target=ThreadingHTTPServer(("0.0.0.0", 3500), Echo).serve_forever, daemon=True).start()
ThreadingHTTPServer(("0.0.0.0", 8500), Echo).serve_forever()
"""
CLIENT = """
import json, sys, time
from urllib.request import Request, urlopen
address, expected = sys.argv[1:]
headers = {"Host": "patnampakodi.com", "X-Forwarded-For": "203.0.113.8",
           "X-Forwarded-Proto": "http", "X-Forwarded-Host": "forged.invalid"}
for path, upstream_path in (("/api/echo?sample=1", "/echo?sample=1"), ("/shop/", "/shop/")):
    for attempt in range(30):
        try:
            with urlopen(Request("http://" + address + path, headers=headers), timeout=2) as response:
                assert response.headers.get("Strict-Transport-Security") == "max-age=31536000"
                result = json.load(response)
            break
        except OSError:
            if attempt == 29: raise
            time.sleep(0.2)
    forwarded = {key.lower(): value for key, value in result["headers"].items()}
    assert result["path"] == upstream_path, result
    assert forwarded["x-forwarded-for"] == expected, result
    assert forwarded["x-forwarded-proto"] == "https", result
    assert forwarded["x-forwarded-host"] == "patnampakodi.com", result
print("Verified proxy client", expected)
"""


def docker(*args, check=True):
    return subprocess.run(
        ["docker", *args], check=check, text=True, capture_output=True
    )


def main():
    identifiers = docker("network", "ls", "-q").stdout.split()
    networks = (
        json.loads(docker("network", "inspect", *identifiers).stdout)
        if identifiers
        else []
    )
    occupied = [
        ipaddress.ip_network(config["Subnet"])
        for network in networks
        for config in network.get("IPAM", {}).get("Config") or []
        if config.get("Subnet")
    ]
    subnet = next(
        ipaddress.ip_network(f"10.251.{index}.0/24")
        for index in range(256)
        if not any(
            ipaddress.ip_network(f"10.251.{index}.0/24").overlaps(other)
            for other in occupied
        )
    )
    prefix = str(subnet.network_address).rsplit(".", 1)[0]
    name = "pakodi-proxy-fixture-" + uuid.uuid4().hex[:10]
    containers = []
    # Reserve .1 for the synthetic trusted upstream; production uses its host
    # bridge gateway there. No host ports or real application data are used.
    docker(
        "network", "create", "--subnet", str(subnet), "--gateway", prefix + ".254", name
    )
    try:
        with tempfile.TemporaryDirectory(prefix="pakodi-proxy-config-") as directory:
            config = Path(directory) / "Caddyfile"
            config.write_bytes((ROOT / "infra/Caddyfile.nginx").read_bytes())
            backend, edge = name + "-backend", name + "-edge"
            containers.append(backend)
            docker(
                "run",
                "-d",
                "--name",
                backend,
                "--network",
                name,
                "--ip",
                prefix + ".20",
                "--network-alias",
                "api",
                "--network-alias",
                "web",
                PYTHON,
                "python",
                "-c",
                BACKEND,
            )
            containers.append(edge)
            docker(
                "run",
                "-d",
                "--name",
                edge,
                "--network",
                name,
                "--ip",
                prefix + ".10",
                "-e",
                "PAKODI_HOST=patnampakodi.com",
                "-e",
                "PAKODI_NETWORK_PREFIX=" + prefix,
                "--mount",
                f"type=bind,source={config},target=/etc/caddy/Caddyfile,readonly",
                CADDY,
            )
            result = docker(
                "exec", backend, "python", "-c", CLIENT, prefix + ".10", prefix + ".20"
            )
            print(result.stdout.strip())
            trusted = name + "-trusted"
            containers.append(trusted)
            result = docker(
                "run",
                "--rm",
                "--name",
                trusted,
                "--network",
                name,
                "--ip",
                prefix + ".1",
                PYTHON,
                "python",
                "-c",
                CLIENT,
                prefix + ".10",
                "203.0.113.8",
            )
            print(result.stdout.strip())
            print(
                "API prefix stripping, web routing, HTTPS/host headers and spoof rejection passed."
            )
    finally:
        for container in reversed(containers):
            docker("rm", "-f", container, check=False)
        docker("network", "rm", name)


if __name__ == "__main__":
    main()
