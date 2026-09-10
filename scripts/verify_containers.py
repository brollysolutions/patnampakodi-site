"""Build and smoke-test containers against a fresh synthetic local database."""
from __future__ import annotations

from pathlib import Path
import argparse
import os
import shutil
import ssl
import subprocess
import time
from urllib.request import urlopen
import uuid

ROOT = Path(__file__).resolve().parents[1]


def run(*args, capture=False):
    return subprocess.run(["docker", *args], cwd=ROOT, check=True, text=True,
                          capture_output=capture)


def wait(url):
    for _ in range(60):
        try:
            with urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return response
        except OSError:
            time.sleep(0.5)
    raise RuntimeError("Container readiness timed out")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lighthouse", action="store_true",
                        help="Audit the indexable build with unchanged Lighthouse budgets")
    args = parser.parse_args()
    for layer in ("api", "web"):
        options = ["--build-arg", "SITE_INDEXABLE=true", "--build-arg", "DEPLOYMENT_ENV=test"] if args.lighthouse and layer == "web" else []
        run("build", "-f", f"apps/{layer}/Dockerfile", "-t", f"pakodi-mvp-{layer}:review", *options, ".")
    suffix = uuid.uuid4().hex[:10]
    database = "pakodi_container_fixture_" + suffix
    network = "pakodi-mvp_default"
    owner = f"postgresql://pakodi_owner:local-owner-only@postgres:5432/{database}"
    reader = owner.replace("pakodi_owner:local-owner-only", "pakodi_reader:local-reader-only")
    app = owner.replace("pakodi_owner:local-owner-only", "pakodi_app:local-app-only")
    environment = ["-e", "APP_ENV=test", "-e", "DATABASE_URL=" + reader,
                   "-e", "COMMERCE_DATABASE_URL=" + app, "-e", "REDIS_URL=redis://redis:6379/14"]
    containers = []
    proxy_config = ROOT / ".agent-workflow" / ("Caddyfile-" + suffix)
    run("compose", "exec", "-T", "postgres", "createdb", "-U", "pakodi_owner", database)
    try:
        for command in (("alembic", "upgrade", "head"), ("app.seed",)):
            run("run", "--rm", "--network", network, *environment,
                "-e", "MIGRATION_DATABASE_URL=" + owner,
                "pakodi-mvp-api:review", "python", "-m", *command)
        api_name = "pakodi-review-api-" + suffix
        run("run", "-d", "--name", api_name, "--network", network,
            "-p", "127.0.0.1::8000", *environment, "pakodi-mvp-api:review", capture=True)
        containers.append(api_name)
        address = run("port", api_name, "8000/tcp", capture=True).stdout.strip()
        wait("http://" + address + "/health")
        worker = "pakodi-review-worker-" + suffix
        run("run", "-d", "--name", worker, "--network", network, *environment,
            "pakodi-mvp-api:review", "python", "-m", "app.jobs", capture=True)
        containers.append(worker)
        web = "pakodi-review-web-" + suffix
        options = ["-e", "SITE_INDEXABLE=true", "-e", "DEPLOYMENT_ENV=test"] if args.lighthouse else []
        run("run", "-d", "--name", web, "--network", network, "-p", "127.0.0.1::3000",
            "-e", f"CONTENT_API_URL=http://{api_name}:8000", *options, "pakodi-mvp-web:review", capture=True)
        containers.append(web)
        address = run("port", web, "3000/tcp", capture=True).stdout.strip()
        response = wait("http://" + address + "/")
        noindex = "noindex" in response.headers.get("X-Robots-Tag", "")
        if noindex == args.lighthouse:
            raise RuntimeError("Container indexing does not match the selected build")
        with urlopen("http://" + address + "/robots.txt", timeout=5) as robots:
            text = robots.read().decode()
            if args.lighthouse and "Sitemap:" not in text:
                raise RuntimeError("Indexable container must advertise its sitemap")
        with urlopen("http://" + address + "/admin/", timeout=5) as private:
            if "nonce-" not in private.headers.get("Content-Security-Policy", ""):
                raise RuntimeError("Private container page is missing nonce CSP")
        run("exec", api_name, "python", "-c",
            "import os,time,psycopg\n"
            "for attempt in range(20):\n"
            " with psycopg.connect(os.environ['COMMERCE_DATABASE_URL']) as c:\n"
            "  c.execute(\"SELECT set_config('app.brand_id','patnam-pakodi',true)\")\n"
            "  ready=c.execute(\"SELECT status FROM operation_checks WHERE name='worker'\").fetchone()==('running',)\n"
            " if ready: break\n"
            " time.sleep(0.5)\n"
            "else: raise RuntimeError('Worker heartbeat missing')")
        print("Container migration, seed, API, web, indexing/private headers and worker heartbeat passed")
        if args.lighthouse:
            # Exercise the shipping proxy and HTTP/2, using only an ephemeral local CA.
            proxy_config.parent.mkdir(parents=True, exist_ok=True)
            proxy_config.write_text(
                "{\n admin off\n auto_https disable_redirects\n}\n" +
                (ROOT / "infra/Caddyfile").read_text().replace("api:8000", api_name + ":8000")
                .replace("web:3000", web + ":3000"), encoding="utf-8")
            proxy = "pakodi-review-proxy-" + suffix
            run("run", "-d", "--name", proxy, "--network", network,
                "-p", "127.0.0.1::443", "-e", "PAKODI_HOST=localhost",
                "-v", str(proxy_config) + ":/etc/caddy/Caddyfile:ro",
                "caddy:2-alpine@sha256:5f5c8640aae01df9654968d946d8f1a56c497f1dd5c5cda4cf95ab7c14d58648",
                capture=True)
            containers.append(proxy)
            port = run("port", proxy, "443/tcp", capture=True).stdout.strip().rsplit(":", 1)[1]
            proxy_url = "https://localhost:" + port
            # This context is scoped to the disposable loopback certificate, never a provider.
            fixture_tls = ssl._create_unverified_context()
            for attempt in range(60):
                try:
                    with urlopen(proxy_url + "/", timeout=2, context=fixture_tls) as response:
                        if response.status == 200:
                            if "max-age=" not in response.headers.get("Strict-Transport-Security", ""):
                                raise RuntimeError("Proxy is missing its transport security header")
                            break
                except OSError:
                    time.sleep(0.5)
            else:
                raise RuntimeError("Local TLS proxy readiness timed out")
            with urlopen(proxy_url + "/api/health", timeout=5, context=fixture_tls) as response:
                if response.status != 200:
                    raise RuntimeError("Proxy API routing failed")
            subprocess.run([shutil.which("npm.cmd" if os.name == "nt" else "npm") or "npm",
                            "run", "audit:performance"], cwd=ROOT / "apps/web", check=True,
                           env={**os.environ, "NEXT_TELEMETRY_DISABLED": "1",
                                "LIGHTHOUSE_BASE_URL": proxy_url})
    except BaseException:
        for name in containers:
            run("logs", name)
        raise
    finally:
        for name in reversed(containers):
            run("rm", "-f", "-v", name, capture=True)
        run("compose", "exec", "-T", "postgres", "dropdb", "-U", "pakodi_owner", database)
        proxy_config.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
