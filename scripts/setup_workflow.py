#!/usr/bin/env python3
"""Install this repository's per-clone workflow without changing tracked files."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = "https://github.com/brollysolutions/patnampakodi-site.git"


def run(*args: str) -> None:
    print("==> " + " ".join(args), flush=True)
    subprocess.run(args, cwd=ROOT, check=True)


def git_bash_near(git_exe: str) -> str | None:
    # Includes Git/cmd, Git/mingw64/bin, and Git/mingw64/libexec/git-core
    # (the executable location exposed while Git itself runs a hook).
    for parent in Path(git_exe).resolve().parents:
        candidate = parent / "bin" / "bash.exe"
        if candidate.is_file() and (parent / "cmd" / "git.exe").is_file():
            return str(candidate)
    return None


def find_bash() -> str:
    # Windows' system32/bash.exe may launch WSL; Git hooks need Git Bash.
    if os.name == "nt":
        git_exe = shutil.which("git")
        if git_exe:
            candidate = git_bash_near(git_exe)
            if candidate:
                return candidate
        raise RuntimeError("Install Git for Windows with Git Bash available.")
    candidate = shutil.which("bash")
    if not candidate:
        raise RuntimeError("bash is required for Git hooks.")
    return candidate


def initialize_private_notes(root: Path) -> None:
    templates = root / "docs/workflow-templates"
    sources = [(templates / "CLAUDE.local.md", root / "CLAUDE.local.md")]
    sources.extend((source, root / ".agent-workflow" / source.name)
                   for source in sorted((templates / "private").glob("*.md")))
    for source, destination in sources:
        if destination.exists():
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive creation also protects against concurrent setup.
        try:
            with destination.open("x", encoding="utf-8", newline="\n") as output:
                output.write(source.read_text(encoding="utf-8"))
        except FileExistsError:
            pass


def main() -> int:
    if sys.version_info < (3, 11):
        raise RuntimeError("Python 3.11+ is required.")
    for tool in ("git", "uv"):
        if not shutil.which(tool):
            raise RuntimeError(f"{tool} is required on PATH.")
    bash = find_bash()
    run(bash, "--version")
    run("git", "config", "--local", "core.hooksPath", ".githooks")
    remotes = subprocess.check_output(["git", "remote"], cwd=ROOT, text=True).split()
    origin = subprocess.check_output(["git", "remote", "get-url", "origin"],
                                     cwd=ROOT, text=True).strip() if "origin" in remotes else ""
    from agent_workflow import remote_slug
    if "upstream" not in remotes and remote_slug(origin) != "brollysolutions/patnampakodi-site":
        run("git", "remote", "add", "upstream", UPSTREAM)
    initialize_private_notes(ROOT)
    if os.name != "nt":
        for path in [*(ROOT / ".githooks").iterdir(), *(ROOT / "scripts").glob("*.sh")]:
            path.chmod(path.stat().st_mode | 0o111)
    run(sys.executable, "scripts/verify_workflow.py", "--ci")
    print("Setup complete. Git hooks are configured for this clone.")
    print("GitHub CLI authentication is separate: run gh auth status before shipping.")
    print("Start a fresh agent session and review/trust its project hooks.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, subprocess.CalledProcessError, OSError) as error:
        print(f"Setup failed: {error}", file=sys.stderr)
        raise SystemExit(1)
