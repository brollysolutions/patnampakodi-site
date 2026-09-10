"""Reproducible local application gate; test data stays in the Docker fixture."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
from urllib.request import urlopen
from urllib.parse import urlparse
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "apps/api"
WEB = ROOT / "apps/web"
PYTHON = API / (".venv/Scripts/python.exe" if os.name == "nt" else ".venv/bin/python")
NPM = shutil.which("npm.cmd" if os.name == "nt" else "npm") or "npm"
OWNER = "postgresql://pakodi_owner:local-owner-only@127.0.0.1:54339/pakodi_mvp_test"
READER = "postgresql://pakodi_reader:local-reader-only@127.0.0.1:54339/pakodi_mvp_test"
ENV = {**os.environ, "NEXT_TELEMETRY_DISABLED": "1", "SITE_INDEXABLE": "true",
       "DEPLOYMENT_ENV": "test", "APP_ENV": "test", "DATABASE_URL": READER,
       "MIGRATION_DATABASE_URL": OWNER, "CONTENT_API_URL": "http://127.0.0.1:8010",
       "COMMERCE_DATABASE_URL": OWNER.replace("pakodi_owner:local-owner-only", "pakodi_app:local-app-only"),
       "REDIS_URL": "redis://127.0.0.1:63799/15", "PUBLIC_ORIGIN": "http://127.0.0.1:3010",
       "API_HOST": "127.0.0.1", "API_PORT": "8010"}
REPORTS = ROOT / ".agent-workflow/reports"


def run(args, cwd=ROOT, capture=False):
    print("==> " + " ".join(str(arg) for arg in args), flush=True)
    return subprocess.run(args, cwd=cwd, env=ENV, check=True, text=True,
                          capture_output=capture)


def api_checks():
    run([PYTHON, "-m", "ruff", "check", "app", "migrations", "tests"], API)
    run([PYTHON, "-m", "ruff", "format", "--check", "app", "migrations", "tests"], API)
    run([PYTHON, "-m", "pytest", "-q"], API)
    heads = run([PYTHON, "-m", "alembic", "heads"], API, capture=True).stdout.strip().splitlines()
    if len(heads) != 1 or "(head)" not in heads[0]:
        raise RuntimeError(f"Expected exactly one migration head, got {heads}")
    print("==> Exactly one migration head: " + heads[0], flush=True)
    contract = ROOT / "packages/contracts/openapi.json"
    expected = json.loads(contract.read_text(encoding="utf-8"))
    run([PYTHON, "-m", "app.export_openapi"], API)
    if json.loads(contract.read_text(encoding="utf-8")) != expected:
        raise RuntimeError("OpenAPI contract was stale; review and commit regeneration")


def require_free_port(port):
    with socket.socket() as probe:
        try:
            probe.bind(("127.0.0.1", port))
        except OSError as error:
            raise RuntimeError(f"Port {port} is occupied; stop its owner before verification") from error


def start(args, cwd, url, log_name):
    log = (REPORTS / log_name).open("w", encoding="utf-8")
    process = subprocess.Popen(args, cwd=cwd, env=ENV, stdout=log, stderr=subprocess.STDOUT,
                               creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
    try:
        for _ in range(120):
            if process.poll() is not None:
                raise RuntimeError(f"Server exited with {process.returncode}; see {log.name}")
            try:
                with urlopen(url, timeout=2) as response:
                    if response.status == 200:
                        return process, log
            except OSError:
                time.sleep(0.5)
        raise RuntimeError(f"Server readiness timed out; see {log.name}")
    except BaseException:
        stop(process, log)
        raise


def stop(process, log):
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)
    log.close()


def web_checks(mode, browsers_only=False):
    REPORTS.mkdir(parents=True, exist_ok=True)
    if not browsers_only:
        generated = ROOT / "packages/contracts/schema.d.ts"
        expected = generated.read_text(encoding="utf-8")
        run([NPM, "run", "contracts"], WEB)
        if generated.read_text(encoding="utf-8") != expected:
            raise RuntimeError("Typed client was stale; review and commit regeneration")
        for script in ("lint", "format:check", "typecheck", "test", "build"):
            run([NPM, "run", script], WEB)
    if mode == "fast":
        print("==> Browser/performance/live SEO checks SKIPPED (--fast)", flush=True)
        return
    require_free_port(8010)
    require_free_port(3010)
    run([PYTHON, "tests/browser_fixture.py", "reset"], API)
    api = start([str(PYTHON), "-m", "app.serve"], API, "http://127.0.0.1:8010/health", "api.log")
    web = None
    try:
        web = start([shutil.which("node") or "node", "node_modules/next/dist/bin/next", "start",
                     "--hostname", "127.0.0.1", "--port", "3010"], WEB, "http://127.0.0.1:3010", "web.log")
        run([NPM, "run", "test:e2e"], WEB)
        manifest = run(["node", "--input-type=module", "-e",
                        "import {PUBLIC_SLUGS,pathFor} from './src/lib/policy.mjs'; "
                        "console.log(JSON.stringify(PUBLIC_SLUGS.map(pathFor)))"], WEB, capture=True)
        routes = json.loads(manifest.stdout)
        with urlopen("http://127.0.0.1:3010/sitemap.xml", timeout=5) as response:
            sitemap = ElementTree.fromstring(response.read())
        routes = sorted(set(routes) | {
            urlparse(node.text).path
            for node in sitemap.findall("{*}url/{*}loc") if node.text
        })
        run([sys.executable, "scripts/check_seo.py", "http://127.0.0.1:3010", *routes,
             "--canonical-origin", "https://patnampakodi.com", "--json", str(REPORTS / "seo.json")])
    finally:
        if web:
            stop(*web)
        stop(*api)
    # Measure the pinned Linux standalone images delivered to the operator.
    # Native browser/SEO results above remain separate from container/Lighthouse evidence.
    run([sys.executable, "scripts/verify_containers.py", "--lighthouse"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("layer", choices=["all", "api", "web", "browsers"])
    parser.add_argument("mode", choices=["full", "fast", "ci"], default="full", nargs="?")
    args = parser.parse_args()
    if args.mode == "ci":
        run(["uv", "sync", "--frozen"], API)
        if args.layer != "api":
            run([NPM, "ci"], WEB)
    if args.layer in {"all", "api"}:
        api_checks()
    if args.layer in {"all", "web", "browsers"}:
        web_checks(args.mode, browsers_only=args.layer == "browsers")
    print("==> Requested application checks passed", flush=True)


if __name__ == "__main__":
    try:
        main()
    except (subprocess.CalledProcessError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1) from error
