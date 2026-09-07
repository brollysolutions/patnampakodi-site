#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec uv --cache-dir "$repo_root/.uv-cache" run --no-project python "$repo_root/scripts/setup_workflow.py"
