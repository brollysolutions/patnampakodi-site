#!/usr/bin/env python3
"""Agent workflow engine: lifecycle hooks, deterministic delivery, and self-checks.

Implements the shared contract in AGENTS.md and docs/partner-workflow-guide.md.

Standard library only, so it runs under `uv run --no-project python` with no
project environment, no lockfile, and no network. Python 3.11+ (``tomllib``).

Subcommands
    hook --agent <claude|codex>   read a hook payload on stdin, print a decision
    finish                        commit, push, create/update the pull request
    state                         print the workflow state the Stop hook sees
    validate                      config parses, skill parity, hooks path
    setup                         wire core.hooksPath, report tool availability
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tomllib
import traceback
from collections.abc import Iterable, Iterator, Sequence
from datetime import datetime
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants (section 7.4)
# ---------------------------------------------------------------------------

PROTECTED_BRANCHES = {"main", "master", "prod"}
MUTATING_TOOLS = {"apply_patch", "Edit", "Write", "MultiEdit", "NotebookEdit"}
CONVENTIONAL_TITLE = re.compile(
    r"^(?:feat|fix|security|docs|refactor|test|chore|perf|build|ci)"
    r"(?:\([a-z0-9._/-]+\))?!?: .+"
)

# Sensitive paths ----------------------------------------------------------
SENSITIVE_BASENAMES = frozenset(
    {
        ".npmrc",
        ".pypirc",
        "credentials.json",
        "service-account.json",
        "id_rsa",
        "id_ed25519",
    }
)
SENSITIVE_SUFFIXES = frozenset(
    {".pem", ".key", ".p12", ".pfx", ".keystore", ".dump", ".backup"}
)

# Tool names that may execute arbitrary code in a live browser session.
BLOCKED_TOOL_FRAGMENTS = ("browser_evaluate", "browser_run_code_unsafe")

# Shell verbs ---------------------------------------------------------------
READ_COMMANDS = frozenset(
    {"cat", "type", "get-content", "gc", "more", "less", "head", "tail", "select-string", "sls"}
)
WRITE_COMMANDS = frozenset(
    {"cp", "copy", "mv", "move", "rm", "del", "erase", "touch", "tee", "truncate", "shred"}
)
MUTATING_SHELL_COMMANDS = frozenset(
    {"touch", "mkdir", "rmdir", "cp", "copy", "mv", "move", "rm", "del", "erase", "tee"}
)
MUTATING_GIT_SUBCOMMANDS = frozenset(
    {"add", "commit", "merge", "rebase", "reset", "restore", "clean", "cherry-pick", "tag"}
)
POWERSHELL_MUTATORS = re.compile(r"^(?:set|add|clear|new|remove|copy|move|rename)-(?:content|item)$")

# Base ref preference order (section 7.4, finish step 5).
BASE_REF_ORDER = ("upstream/main", "origin/main", "main", "master")

READ_FIRST = (
    "AGENTS.md",
    "the closest nested AGENTS.md",
    "SECURITY.md",
    "docs/agent-context/INDEX.md",
    "docs/agent-context/implementation-plan.md",
    "docs/agent-context/feature-status.md",
)

ROUTER_REMINDER = (
    "Route the request: build/change -> $work-feature; broken -> $systematic-debug; "
    "decide -> $brainstorm; review -> $review-pr; secure? -> $security-review; "
    "deliver -> $ship. Every implementation chain ends at review-pr then ship."
)


# ---------------------------------------------------------------------------
# Pure predicates - no subprocess, unit-tested directly
# ---------------------------------------------------------------------------


def is_sensitive_path(path: str) -> bool:
    """True when `path` names a secret, key, dump, or backup artefact."""
    if not path:
        return False
    normalized = path.strip().strip("'\"").replace("\\", "/")
    if not normalized:
        return False
    lowered = normalized.lower()
    if lowered.endswith(".example"):
        return False
    segments = [segment for segment in lowered.split("/") if segment not in ("", ".", "..")]
    if "secrets" in segments:
        return True
    if not segments:
        return False
    basename = segments[-1]
    if basename == ".env" or basename.startswith(".env."):
        return True
    if basename in SENSITIVE_BASENAMES:
        return True
    return any(basename.endswith(suffix) for suffix in SENSITIVE_SUFFIXES)


_TOKEN_RE = re.compile(r"\"([^\"]*)\"|'([^']*)'|([^\s]+)")


def tokenize(segment: str) -> list[str]:
    """Split one shell segment into tokens, stripping matched quotes."""
    tokens: list[str] = []
    for double, single, bare in _TOKEN_RE.findall(segment):
        tokens.append(double or single or bare)
    return tokens


def iter_segments(command: str) -> Iterator[str]:
    """Yield each command in a compound shell line."""
    for segment in re.split(r"\|\||&&|[;|\n]", command):
        segment = segment.strip()
        if segment:
            yield segment


def _verb(tokens: Sequence[str]) -> str:
    """Normalised name of the executable in a token list."""
    if not tokens:
        return ""
    head = tokens[0].replace("\\", "/").rsplit("/", 1)[-1].lower()
    return head[:-4] if head.endswith(".exe") else head


def _has_sensitive_token(tokens: Sequence[str]) -> str | None:
    for token in tokens[1:]:
        if not token.startswith("-") and is_sensitive_path(token):
            return token
    return None


def _push_targets_protected(tokens: Sequence[str]) -> str | None:
    for token in tokens[2:]:
        if token.startswith("-"):
            continue
        ref = token.lstrip("+")
        if ":" in ref:
            ref = ref.rsplit(":", 1)[-1]
        if ref.startswith("refs/heads/"):
            ref = ref[len("refs/heads/") :]
        if ref in PROTECTED_BRANCHES:
            return ref
    return None


def command_is_blocked(command: str, branch: str | None = None) -> str | None:
    """Return a refusal reason for a Bash command, or None when it is allowed.

    `branch` is the current branch; the protected-branch categories are skipped
    when it is None or not protected.
    """
    if not command or not command.strip():
        return None
    protected = branch in PROTECTED_BRANCHES if branch else False

    for segment in iter_segments(command):
        tokens = tokenize(segment)
        if not tokens:
            continue
        verb = _verb(tokens)
        rest = [token.lower() for token in tokens[1:]]

        # 1. Merging or closing a pull request is never automatic.
        if verb in {"gh", "hub"} and "pr" in rest[:1] and any(
            action in rest[1:2] for action in ("merge", "close")
        ):
            return (
                "Merging or closing a pull request is a user-only action. "
                "Open or update the PR and let a human decide."
            )

        # 2. Commands that destroy uncommitted user work.
        if verb == "git":
            sub = rest[0] if rest else ""
            if sub == "reset" and "--hard" in rest:
                return "`git reset --hard` discards user work. Use a safer reset or ask the user."
            if sub == "clean" and any(token.startswith("-f") for token in rest[1:]):
                return "`git clean -f` deletes untracked user files. Ask the user instead."
            if sub == "checkout" and "--" in rest[1:]:
                return "`git checkout --` discards uncommitted changes. Ask the user instead."
            if sub == "restore":
                return "`git restore` discards uncommitted changes. Ask the user instead."

        # 3. Reading a secret.
        if verb in READ_COMMANDS:
            hit = _has_sensitive_token(tokens)
            if hit:
                return f"Reading the sensitive path '{hit}' is denied. Use an .example file instead."

        # 4. Writing, moving, deleting, or staging a secret.
        if verb in WRITE_COMMANDS or POWERSHELL_MUTATORS.match(verb):
            hit = _has_sensitive_token(tokens)
            if hit:
                return f"Writing to the sensitive path '{hit}' is denied."
        if verb == "sed" and any(token == "-i" or token.startswith("-i") for token in tokens[1:]):
            hit = _has_sensitive_token(tokens)
            if hit:
                return f"In-place edit of the sensitive path '{hit}' is denied."
        if verb == "git" and rest[:1] == ["add"]:
            hit = _has_sensitive_token(tokens[1:])
            if hit:
                return f"Staging the sensitive path '{hit}' is denied."

        # 5. Pushing to a protected ref, or pushing at all from a protected branch.
        if verb == "git" and rest[:1] == ["push"]:
            hit = _push_targets_protected(tokens)
            if hit:
                return f"Direct pushes to protected ref '{hit}' are blocked. Open a PR."
            if protected:
                return (
                    f"Pushing from protected branch '{branch}' is blocked. "
                    "Move the work to a task branch first."
                )

        # 6. Any mutating shell command while on a protected branch.
        if protected:
            if verb == "git" and rest[:1] and rest[0] in MUTATING_GIT_SUBCOMMANDS:
                return (
                    f"`git {rest[0]}` is blocked on protected branch '{branch}'. "
                    "Create a task branch first."
                )
            if verb in MUTATING_SHELL_COMMANDS or POWERSHELL_MUTATORS.match(verb):
                return (
                    f"`{verb}` mutates the working tree on protected branch '{branch}'. "
                    "Create a task branch first."
                )
            if verb == "sed" and any(token.startswith("-i") for token in tokens[1:]):
                return (
                    f"`sed -i` mutates files on protected branch '{branch}'. "
                    "Create a task branch first."
                )
    return None


def iter_input_strings(value: Any) -> Iterator[str]:
    """Yield every string leaf in a nested tool_input structure."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from iter_input_strings(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from iter_input_strings(item)


def sensitive_tool_input(tool_input: Any) -> str | None:
    """Return the first sensitive path found anywhere in a tool payload.

    Only whitespace-free leaves are considered: prose describing a file is not a
    file reference, and treating it as one produces false denials.
    """
    for leaf in iter_input_strings(tool_input):
        candidate = leaf.strip()
        if candidate and not any(char.isspace() for char in candidate):
            if is_sensitive_path(candidate):
                return candidate
    return None


def slugify(text: str, max_length: int = 48) -> str:
    """Kebab-case slug suitable for a branch name."""
    slug = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip("-")
    return slug or "task"


def branch_name(agent: str, prompt: str, now: datetime | None = None) -> str:
    """`<agent>/<YYYYmmdd-HHMMSS>-<prompt-slug>`."""
    stamp = (now or datetime.now()).strftime("%Y%m%d-%H%M%S")
    prefix = agent if agent in {"claude", "codex"} else "claude"
    return f"{prefix}/{stamp}-{slugify(prompt)}"


def conventional_ok(text: str) -> bool:
    return bool(CONVENTIONAL_TITLE.match(text or ""))


def remote_slug(url: str) -> str | None:
    """Extract `owner/repo` from an https or ssh GitHub remote URL."""
    if not url:
        return None
    cleaned = url.strip()
    if cleaned.endswith(".git"):
        cleaned = cleaned[:-4]
    match = re.search(r"(?:[:/])([^/:]+)/([^/]+)$", cleaned)
    return f"{match.group(1)}/{match.group(2)}" if match else None


# ---------------------------------------------------------------------------
# Git layer
# ---------------------------------------------------------------------------


class GitError(RuntimeError):
    pass


def run(args: Sequence[str], cwd: Path | None = None, check: bool = False,
        input_text: str | None = None) -> subprocess.CompletedProcess:
    argv = list(args)
    # Resolve bare names through PATHEXT so Windows shims (gh.cmd, pnpm.cmd) are
    # found. CreateProcess does not apply PATHEXT the way a shell does.
    resolved = shutil.which(argv[0]) if argv and not Path(argv[0]).is_absolute() else None
    if resolved:
        argv[0] = resolved
    try:
        result = subprocess.run(
            argv,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            input=input_text,
        )
    except (FileNotFoundError, OSError) as exc:
        result = subprocess.CompletedProcess(argv, 127, "", f"{argv[0]}: not executable ({exc})")
    if check and result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise GitError(f"{' '.join(args)} failed: {detail}")
    return result


def git(args: Sequence[str], cwd: Path, check: bool = False) -> str:
    return run(["git", *args], cwd=cwd, check=check).stdout.strip()


def repo_root(start: Path) -> Path:
    result = run(["git", "rev-parse", "--show-toplevel"], cwd=start)
    if result.returncode != 0:
        raise GitError("not inside a Git repository")
    return Path(result.stdout.strip())


def current_branch(root: Path) -> str | None:
    """Branch name, or None on a detached HEAD."""
    result = run(["git", "symbolic-ref", "--quiet", "--short", "HEAD"], cwd=root)
    return result.stdout.strip() if result.returncode == 0 and result.stdout.strip() else None


def is_dirty(root: Path) -> bool:
    return bool(git(["status", "--porcelain"], root))


def has_remote(root: Path, name: str) -> bool:
    return name in git(["remote"], root).splitlines()


def ref_exists(root: Path, ref: str) -> bool:
    return run(["git", "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"], cwd=root).returncode == 0


def base_ref(root: Path) -> str | None:
    for ref in BASE_REF_ORDER:
        if ref_exists(root, ref):
            return ref
    return None


def commits_ahead(root: Path, base: str | None) -> int:
    if not base:
        return 0
    result = run(["git", "rev-list", "--count", f"{base}..HEAD"], cwd=root)
    try:
        return int(result.stdout.strip() or 0)
    except ValueError:
        return 0


def upstream_of(root: Path, branch: str) -> str | None:
    result = run(
        ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", f"{branch}@{{upstream}}"],
        cwd=root,
    )
    return result.stdout.strip() if result.returncode == 0 and result.stdout.strip() else None


def unpushed(root: Path, branch: str) -> bool:
    """True when the branch has commits its tracking ref does not have."""
    tracking = upstream_of(root, branch)
    if not tracking:
        return True
    result = run(["git", "rev-list", "--count", f"{tracking}..{branch}"], cwd=root)
    try:
        return int(result.stdout.strip() or 0) > 0
    except ValueError:
        return True


def pr_url_for(root: Path, branch: str) -> str | None:
    value = git(["config", "--get", f"branch.{branch}.aiPrUrl"], root)
    return value or None


def set_pr_url(root: Path, branch: str, url: str) -> None:
    run(["git", "config", f"branch.{branch}.aiPrUrl", url], cwd=root)


def ensure_hooks_path(root: Path) -> None:
    if git(["config", "--get", "core.hooksPath"], root) != ".githooks":
        run(["git", "config", "core.hooksPath", ".githooks"], cwd=root, check=True)


def changed_paths(root: Path, args: Sequence[str]) -> list[str]:
    return [
        line.strip()
        for line in git(["diff", "--name-only", "--diff-filter=ACMR", *args], root).splitlines()
        if line.strip()
    ]


def working_tree_paths(root: Path) -> list[str]:
    """Every path with a pending change, including untracked files."""
    paths: list[str] = []
    # Preserve the leading status column: git() strips it from the first row.
    result = run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=root, check=True)
    for line in result.stdout.splitlines():
        entry = line[3:].strip() if len(line) > 3 else ""
        if " -> " in entry:  # renames
            entry = entry.split(" -> ", 1)[1]
        entry = entry.strip('"')
        if entry:
            paths.append(entry)
    return paths


def workflow_state(root: Path) -> dict[str, Any]:
    branch = current_branch(root)
    base = base_ref(root)
    return {
        "root": str(root),
        "branch": branch,
        "detached": branch is None,
        "dirty": is_dirty(root),
        "base_ref": base,
        "commits_ahead_of_base": commits_ahead(root, base),
        "upstream": upstream_of(root, branch) if branch else None,
        "pr_url": pr_url_for(root, branch) if branch else None,
    }


# ---------------------------------------------------------------------------
# Hook decisions (section 7.4 JSON contract)
# ---------------------------------------------------------------------------


def allow() -> dict[str, Any]:
    return {}


def add_context(event: str, text: str) -> dict[str, Any]:
    return {"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}


def block(reason: str) -> dict[str, Any]:
    return {"decision": "block", "reason": reason}


def deny_tool(reason: str) -> dict[str, Any]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }


def handle_session_start(root: Path, payload: dict[str, Any], agent: str) -> dict[str, Any]:
    ensure_hooks_path(root)
    branch = current_branch(root)
    where = f"branch '{branch}'" if branch else "a detached HEAD"
    protected_note = (
        " This is a protected branch; a task branch is created automatically at the first prompt."
        if branch in PROTECTED_BRANCHES
        else ""
    )
    return add_context(
        "SessionStart",
        f"Repository workflow loaded for {agent}. You are on {where}.{protected_note} "
        f"Read first, as relevant: {', '.join(READ_FIRST)}. "
        "Never edit a protected branch, never merge or force-push, and do not claim "
        "completion while work is uncommitted, unpushed, or missing a PR.",
    )


def handle_user_prompt_submit(root: Path, payload: dict[str, Any], agent: str) -> dict[str, Any]:
    branch = current_branch(root)

    if branch is None:
        return block(
            "HEAD is detached, so work cannot be tracked or shipped. Check out a task "
            "branch (or ask the user which branch to use) before continuing."
        )

    if branch in PROTECTED_BRANCHES:
        if is_dirty(root):
            return block(
                f"Protected branch '{branch}' has uncommitted changes. Those are the "
                "user's work and must not be moved, stashed, or discarded. Ask the user "
                "how to handle them, then continue on a task branch."
            )
        new_branch = branch_name(agent, payload.get("prompt", ""))
        result = run(["git", "checkout", "-b", new_branch], cwd=root)
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()
            return block(
                f"Could not create task branch '{new_branch}' from protected branch "
                f"'{branch}': {detail}"
            )
        return add_context(
            "UserPromptSubmit",
            f"Created and switched to task branch '{new_branch}' so protected branch "
            f"'{branch}' is never written to. Do all work here. {ROUTER_REMINDER}",
        )

    return add_context(
        "UserPromptSubmit",
        f"Continue the current task on non-protected branch '{branch}'. {ROUTER_REMINDER}",
    )


def handle_pre_tool_use(root: Path, payload: dict[str, Any], agent: str) -> dict[str, Any]:
    tool_name = payload.get("tool_name") or ""
    tool_input = payload.get("tool_input") or {}

    if any(fragment in tool_name for fragment in BLOCKED_TOOL_FRAGMENTS):
        return deny_tool(
            f"'{tool_name}' executes arbitrary code in a live browser session and is "
            "denied by repository policy. Use the scoped browser tools instead."
        )

    hit = sensitive_tool_input(tool_input)
    if hit:
        return deny_tool(
            f"'{hit}' is a secret, key, dump, or backup path. Reading, writing, or "
            "staging it is denied. Use the matching .example file instead."
        )

    branch = current_branch(root)

    if tool_name in MUTATING_TOOLS and branch in PROTECTED_BRANCHES:
        return deny_tool(
            f"'{tool_name}' would modify protected branch '{branch}'. Create a task "
            "branch first; repository changes are never made on a protected branch."
        )

    if tool_name == "Bash":
        command = tool_input.get("command") if isinstance(tool_input, dict) else None
        reason = command_is_blocked(command or "", branch)
        if reason:
            return deny_tool(reason)

    return allow()


def handle_stop(root: Path, payload: dict[str, Any], agent: str) -> dict[str, Any]:
    if payload.get("stop_hook_active"):
        return allow()

    branch = current_branch(root)
    if branch is None or branch in PROTECTED_BRANCHES:
        return allow()

    if is_dirty(root):
        return block(
            f"Branch '{branch}' still has uncommitted changes, so the work is not "
            "delivered. Invoke the ship skill: run the applicable verification, review "
            "the diff, then commit, push, and open or update the PR. If nothing here is "
            "meant to ship, tell the user what is left and why."
        )

    base = base_ref(root)
    ahead = commits_ahead(root, base)
    if ahead <= 0:
        return allow()

    if unpushed(root, branch):
        return block(
            f"Branch '{branch}' has {ahead} commit(s) ahead of '{base}' that are not "
            "pushed. Invoke the ship skill to push and open or update the PR."
        )

    if not pr_url_for(root, branch):
        return block(
            f"Branch '{branch}' is pushed with {ahead} commit(s) ahead of '{base}' but "
            "has no recorded PR. Invoke the ship skill to open or update the pull "
            "request; never merge it."
        )

    return allow()


HANDLERS = {
    "SessionStart": handle_session_start,
    "UserPromptSubmit": handle_user_prompt_submit,
    "PreToolUse": handle_pre_tool_use,
    "Stop": handle_stop,
}


def dispatch_hook(payload: dict[str, Any], agent: str, root: Path) -> dict[str, Any]:
    handler = HANDLERS.get(payload.get("hook_event_name") or "")
    return handler(root, payload, agent) if handler else allow()


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------


def resolve_root(payload: dict[str, Any]) -> Path:
    """Locate the repository, preferring the payload's cwd.

    A harness may report a cwd this interpreter cannot resolve (a POSIX-style
    path handed to a Windows Python, for example). Falling back to the process
    working directory keeps the guards active instead of failing open.
    """
    candidates = [payload.get("cwd"), Path.cwd()]
    for candidate in candidates:
        if not candidate:
            continue
        try:
            return repo_root(Path(candidate))
        except GitError:
            continue
    raise GitError("not inside a Git repository")


def cmd_hook(args: argparse.Namespace) -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
        root = resolve_root(payload)
        decision = dispatch_hook(payload, args.agent, root)
    except Exception:  # noqa: BLE001 - a crashing hook must not brick the session
        traceback.print_exc(file=sys.stderr)
        decision = allow()
    print(json.dumps(decision))
    return 0


def cmd_state(args: argparse.Namespace) -> int:
    root = repo_root(Path(args.cwd or Path.cwd()))
    print(json.dumps(workflow_state(root), indent=2))
    return 0


def cmd_setup(args: argparse.Namespace) -> int:
    root = repo_root(Path(args.cwd or Path.cwd()))
    ensure_hooks_path(root)
    tools = {}
    for tool, probe in (
        ("git", ["git", "--version"]),
        ("gh", ["gh", "--version"]),
        ("uv", ["uv", "--version"]),
        ("node", ["node", "--version"]),
        ("pnpm", ["pnpm", "--version"]),
    ):
        result = run(probe, cwd=root)
        tools[tool] = result.stdout.strip().splitlines()[0] if result.returncode == 0 else None
    print(
        json.dumps(
            {
                "status": "ok",
                "root": str(root),
                "hooks_path": git(["config", "--get", "core.hooksPath"], root),
                "remotes": git(["remote"], root).split(),
                "tools": tools,
                "missing": sorted(name for name, version in tools.items() if version is None),
            },
            indent=2,
        )
    )
    return 0


def _parses(path: Path, loader) -> str | None:
    if not path.exists():
        return f"missing: {path.name}"
    try:
        loader(path)
    except Exception as exc:  # noqa: BLE001
        return f"unparseable: {path.name} ({exc})"
    return None


def _tree_files(root: Path) -> dict[str, bytes]:
    return {
        str(path.relative_to(root)).replace("\\", "/"): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def cmd_validate(args: argparse.Namespace) -> int:
    root = repo_root(Path(args.cwd or Path.cwd()))
    problems: list[str] = []

    for relative in (".claude/settings.json", ".mcp.json", ".codex/hooks.json"):
        problem = _parses(root / relative, lambda p: json.loads(p.read_text(encoding="utf-8")))
        if problem:
            problems.append(problem)

    problem = _parses(root / ".codex/config.toml", lambda p: tomllib.loads(p.read_text(encoding="utf-8")))
    if problem:
        problems.append(problem)

    claude_skills = root / ".claude/skills"
    agents_skills = root / ".agents/skills"
    skill_count = 0
    if not claude_skills.is_dir():
        problems.append("missing: .claude/skills")
    else:
        skills = sorted(path for path in claude_skills.iterdir() if path.is_dir())
        skill_count = len(skills)
        for skill in skills:
            if not (skill / "SKILL.md").is_file():
                problems.append(f"missing: .claude/skills/{skill.name}/SKILL.md")

    if not agents_skills.is_dir():
        problems.append("missing: .agents/skills")
    elif claude_skills.is_dir():
        left, right = _tree_files(agents_skills), _tree_files(claude_skills)
        for name in sorted(set(left) | set(right)):
            if name not in left:
                problems.append(f"skill parity: .agents/skills is missing {name}")
            elif name not in right:
                problems.append(f"skill parity: .claude/skills is missing {name}")
            elif left[name] != right[name]:
                problems.append(f"skill parity: {name} differs between the two trees")

    hooks_path = git(["config", "--get", "core.hooksPath"], root)
    if hooks_path != ".githooks":
        problems.append(f"core.hooksPath is {hooks_path or 'unset'!r}, expected '.githooks'")

    if problems:
        print(json.dumps({"status": "invalid", "problems": problems}, indent=2))
        return 1
    print(json.dumps({"status": "valid", "skill_count": skill_count}))
    return 0


DEFAULT_BODY = """## Summary

- {title}

## Verification

{verification}

## Security

{security}

## Database / contracts

- [ ] Migration added or not applicable
- [ ] OpenAPI and generated TypeScript contracts updated or not applicable

## Review checklist

- [x] Work was completed on a task branch
- [x] Diff was reviewed for unrelated files and secrets
- [x] PR targets the upstream default branch
- [ ] Human review complete
"""


def _fail(message: str) -> int:
    print(json.dumps({"status": "error", "error": message}, indent=2), file=sys.stderr)
    return 1


def cmd_finish(args: argparse.Namespace) -> int:
    root = repo_root(Path(args.cwd or Path.cwd()))

    # 1. Tooling and hooks.
    for tool in ("git", "gh"):
        if run([tool, "--version"], cwd=root).returncode != 0:
            return _fail(f"'{tool}' is required on PATH to ship, and was not found.")
    ensure_hooks_path(root)

    # 2. Branch shape.
    branch = current_branch(root)
    if branch is None:
        return _fail("HEAD is detached. Check out a task branch before shipping.")
    if branch in PROTECTED_BRANCHES:
        return _fail(f"Refusing to ship from protected branch '{branch}'. Use a task branch.")

    # 3. Conventional title and commit message.
    if not conventional_ok(args.title):
        return _fail(f"PR title is not Conventional Commits format: {args.title!r}")
    if not conventional_ok(args.commit_message):
        return _fail(f"Commit message is not Conventional Commits format: {args.commit_message!r}")

    # 4. Refuse to stage secrets, then stage and commit.
    pending = working_tree_paths(root)
    sensitive = sorted(path for path in pending if is_sensitive_path(path))
    if sensitive:
        return _fail(f"Refusing to stage sensitive files: {', '.join(sensitive)}")

    commit_sha = ""
    if pending:
        result = run(["git", "add", "--all"], cwd=root)
        if result.returncode != 0:
            return _fail(f"git add failed: {(result.stderr or result.stdout).strip()}")
        result = run(["git", "commit", "-m", args.commit_message], cwd=root)
        if result.returncode != 0:
            return _fail(f"git commit failed: {(result.stderr or result.stdout).strip()}")
    commit_sha = git(["rev-parse", "HEAD"], root)

    # 5. Base ref.
    base = base_ref(root)
    if not base:
        return _fail(f"No base ref found. Tried: {', '.join(BASE_REF_ORDER)}")
    ahead = commits_ahead(root, base)
    if ahead <= 0:
        return _fail(f"Branch '{branch}' has no commits ahead of '{base}'; there is nothing to ship.")

    # 6. Refuse to push secrets.
    shipped = changed_paths(root, [f"{base}...HEAD"])
    sensitive = sorted(path for path in shipped if is_sensitive_path(path))
    if sensitive:
        return _fail(f"Refusing to push a diff containing sensitive files: {', '.join(sensitive)}")

    # 7. Push.
    result = run(["git", "push", "--set-upstream", "origin", branch], cwd=root)
    if result.returncode != 0:
        return _fail(f"git push failed: {(result.stderr or result.stdout).strip()}")

    # 8. Create or update the PR against upstream when it exists, else origin.
    target_remote = "upstream" if has_remote(root, "upstream") else "origin"
    target_slug = remote_slug(git(["remote", "get-url", target_remote], root))
    origin_slug = remote_slug(git(["remote", "get-url", "origin"], root))
    if not target_slug or not origin_slug:
        return _fail("Could not determine the GitHub owner/repo from the configured remotes.")
    base_branch = base.rsplit("/", 1)[-1]
    head_spec = branch if target_slug == origin_slug else f"{origin_slug.split('/')[0]}:{branch}"

    body = (
        Path(args.body_file).read_text(encoding="utf-8")
        if args.body_file
        else DEFAULT_BODY.format(
            title=args.title, verification=args.verification, security=args.security
        )
    )

    listed = run(
        ["gh", "pr", "list", "--repo", target_slug, "--head", head_spec,
         "--state", "open", "--json", "number,url", "--limit", "1"],
        cwd=root,
    )
    existing = []
    if listed.returncode != 0:
        return _fail(f"PR lookup failed; no PR created: {(listed.stderr or listed.stdout).strip()}")
    if listed.stdout.strip():
        try:
            existing = json.loads(listed.stdout)
        except json.JSONDecodeError:
            return _fail("PR lookup returned invalid JSON; no PR created.")

    if existing:
        number = str(existing[0]["number"])
        pr_url = existing[0]["url"]
        result = run(
            ["gh", "pr", "edit", number, "--repo", target_slug,
             "--title", args.title, "--body-file", "-"],
            cwd=root,
            input_text=body,
        )
        if result.returncode != 0:
            return _fail(f"gh pr edit failed: {(result.stderr or result.stdout).strip()}")
        action = "updated"
    else:
        result = run(
            ["gh", "pr", "create", "--repo", target_slug, "--base", base_branch,
             "--head", head_spec, "--title", args.title, "--body-file", "-"],
            cwd=root,
            input_text=body,
        )
        if result.returncode != 0:
            return _fail(f"gh pr create failed: {(result.stderr or result.stdout).strip()}")
        pr_url = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else ""
        action = "created"

    # 9. Record the URL the Stop hook reads.
    if pr_url:
        set_pr_url(root, branch, pr_url)

    # 10. Report.
    print(
        json.dumps(
            {
                "status": "ok",
                "action": action,
                "commit": commit_sha,
                "head": branch,
                "base": f"{target_slug}:{base_branch}",
                "pr_url": pr_url,
                "clean": not is_dirty(root),
                "ahead_of_upstream": unpushed(root, branch),
            },
            indent=2,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Agent workflow engine.")
    sub = parser.add_subparsers(dest="command", required=True)

    hook = sub.add_parser("hook", help="Handle a lifecycle hook payload from stdin.")
    hook.add_argument("--agent", choices=("claude", "codex"), required=True)
    hook.set_defaults(func=cmd_hook)

    finish = sub.add_parser("finish", help="Commit, push, and create or update the PR.")
    finish.add_argument("--title", required=True)
    finish.add_argument("--commit-message", required=True)
    finish.add_argument("--verification", required=True)
    finish.add_argument("--security", required=True)
    finish.add_argument("--body-file")
    finish.add_argument("--cwd")
    finish.set_defaults(func=cmd_finish)

    for name, func, help_text in (
        ("state", cmd_state, "Print the workflow state as JSON."),
        ("validate", cmd_validate, "Check config, skill parity, and hooks path."),
        ("setup", cmd_setup, "Wire core.hooksPath and report tool availability."),
    ):
        child = sub.add_parser(name, help=help_text)
        child.add_argument("--cwd")
        child.set_defaults(func=func)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except GitError as exc:
        return _fail(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
