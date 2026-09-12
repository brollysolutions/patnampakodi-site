"""Verify Docker build exclusions using synthetic files, never the real checkout."""

from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = (
    ".git/config",
    ".github/workflows/verify.yml",
    ".githooks/pre-push",
    "scripts/agent_workflow.py",
    "scripts/deploy.py",
    "tools/seo-audit-tools/toolchain.json",
    "docs/agent-context/implementation-plan.md",
    "runtime.env",
    "infra/runtime.env",
    "apps/api/.env",
    "apps/web/.env.production",
    "apps/web/node_modules/synthetic/index.js",
    "apps/web/.next/server.js",
    "apps/api/.venv/bin/python",
    "apps/api/__pycache__/synthetic.pyc",
    *(
        prefix + name
        for prefix in ("", "apps/web/", "apps/api/")
        for name in (
            ".agents/skills/example/SKILL.md",
            ".codex/hooks.json",
            ".claude/settings.json",
            ".agent-workflow/SESSION.md",
            ".mcp.json",
            "AGENTS.md",
            "CLAUDE.md",
            "CLAUDE.local.md",
        )
    ),
)
REQUIRED = (
    "apps/web/package.json",
    "apps/web/package-lock.json",
    "apps/web/src/app/page.tsx",
    "apps/web/public/logo.svg",
    "apps/web/scripts/images.mjs",
    "apps/web/licenses/fonts.txt",
    "apps/api/pyproject.toml",
    "apps/api/uv.lock",
    "apps/api/alembic.ini",
    "apps/api/app/main.py",
    "apps/api/migrations/env.py",
    "apps/api/content/pages.json",
    "packages/contracts/openapi.json",
    "packages/contracts/schema.d.ts",
    "infra/Caddyfile",
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ignore-file", type=Path, default=ROOT / ".dockerignore")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="pakodi-build-context-") as directory:
        root = Path(directory)
        context, output = root / "context", root / "output"
        context.mkdir()
        for name in (*EXCLUDED, *REQUIRED):
            path = context / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("synthetic fixture only\n", encoding="utf-8")
        (context / ".dockerignore").write_bytes(args.ignore_file.read_bytes())
        (context / "Dockerfile").write_text(
            "FROM scratch\nCOPY . /\n", encoding="utf-8"
        )
        subprocess.run(
            [
                "docker",
                "build",
                "--network=none",
                "--output",
                f"type=local,dest={output.as_posix()}",
                str(context),
            ],
            check=True,
        )
        leaked = [name for name in EXCLUDED if (output / name).exists()]
        missing = [name for name in REQUIRED if not (output / name).is_file()]
        if leaked or missing:
            raise RuntimeError(
                f"Build context leaked {leaked}; missing inputs {missing}"
            )
        print(
            f"Docker context verified: {len(EXCLUDED)} excluded fixtures absent; "
            f"{len(REQUIRED)} required build inputs retained."
        )


if __name__ == "__main__":
    main()
