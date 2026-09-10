#!/usr/bin/env python3
"""Run the applicable workflow gate; propagate every failed check."""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys

from setup_workflow import find_bash

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    if mode.lstrip("-") not in {"full", "fast", "ci", "launch", "workflow-only"}:
        print(f"Unknown verification mode: {mode}", file=sys.stderr)
        return 2
    commands = [
        [sys.executable, "-m", "unittest", "discover", "-s", "scripts/tests", "-v"],
        [sys.executable, "scripts/agent_workflow.py", "validate"],
    ]
    for command in commands:
        print("==> " + " ".join(command), flush=True)
        result = subprocess.run(command, cwd=ROOT)
        if result.returncode:
            return result.returncode
    bash = find_bash()
    scripts = [*(ROOT / "scripts").glob("*.sh"), *(ROOT / ".githooks").iterdir()]
    for script in scripts:
        result = subprocess.run([bash, "-n", str(script)], cwd=ROOT)
        if result.returncode:
            return result.returncode
    if mode.lstrip("-") == "workflow-only":
        print("==> Workflow-only gate complete; application gate runs in its dedicated CI job")
        return 0
    if (ROOT / "apps/api/pyproject.toml").is_file():
        result = subprocess.run(
            [sys.executable, "scripts/verify_application.py", "all", mode.lstrip("-")], cwd=ROOT
        )
        return result.returncode
    for name in ("verify-api.sh", "verify-web.sh", "check-migrations.sh"):
        script = ROOT / "scripts" / name
        if script.is_file():
            result = subprocess.run([bash, str(script), mode], cwd=ROOT)
            if result.returncode:
                return result.returncode
        else:
            print(f"==> {name}: not applicable; layer not configured", flush=True)
    print("==> Applicable verification complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
