#!/usr/bin/env bash
# Thin shim from the agent harness to the workflow engine.
#
# Contract: always exit 0 and print exactly one JSON decision on stdout. A shim that
# cannot find a runtime fails open with `{}` (allow) plus a stderr note, never with a
# shell error, because a crashing hook is surfaced to the user on every tool call.
set -uo pipefail

AGENT_NAME="${1:-}"
if [[ "$AGENT_NAME" != "codex" && "$AGENT_NAME" != "claude" ]]; then
  echo "usage: agent-hook.sh <codex|claude>" >&2
  echo '{}'
  exit 0
fi

# Self-locate so the hook does not depend on the caller's working directory.
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$script_dir/.." && pwd)"
if [[ ! -f "$REPO_ROOT/scripts/agent_workflow.py" ]]; then
  REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
fi
ENGINE="$REPO_ROOT/scripts/agent_workflow.py"
if [[ -z "$REPO_ROOT" || ! -f "$ENGINE" ]]; then
  echo "agent-hook: workflow engine not found; allowing" >&2
  echo '{}'
  exit 0
fi

# Hook payloads are UTF-8 JSON. Without this a Windows Python decodes stdin with the
# ANSI code page and a prompt containing "ﬁ" or an emoji crashes the hook.
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8

# Buffer the payload so a failed first attempt can be retried with another runtime.
PAYLOAD="$(cat)"

# uv first: PATH, then the installer's default locations. A harness launched from a
# desktop app or IDE often has a shorter PATH than the user's terminal.
find_uv() {
  if command -v uv >/dev/null 2>&1; then
    command -v uv
    return 0
  fi
  local candidate
  for candidate in \
    "$HOME/.local/bin/uv" "$HOME/.local/bin/uv.exe" "$HOME/.cargo/bin/uv" \
    "${LOCALAPPDATA:-}/uv/uv.exe"; do
    if [[ -n "${candidate%/uv*}" && -x "$candidate" ]]; then
      echo "$candidate"
      return 0
    fi
  done
  return 1
}

run_engine() {
  printf '%s' "$PAYLOAD" | "$@" "$ENGINE" hook --agent "$AGENT_NAME"
}

if UV_BIN="$(find_uv)"; then
  if run_engine "$UV_BIN" --cache-dir "$REPO_ROOT/.uv-cache" run --no-project python; then
    exit 0
  fi
  echo "agent-hook: uv failed; trying a system Python" >&2
fi

# The engine uses tomllib, so Python 3.11+ is required. Skip the Windows
# Store stub, which is on PATH as python.exe but only prints an install prompt.
for py in python3 python; do
  if command -v "$py" >/dev/null 2>&1 &&
    "$py" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' >/dev/null 2>&1; then
    if run_engine "$py"; then
      exit 0
    fi
  fi
done

echo "agent-hook: no working Python runtime found; allowing" >&2
echo '{}'
exit 0
