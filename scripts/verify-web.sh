#!/usr/bin/env bash
# Database fixture must already exist; the full root gate prepares it via API tests.
set -euo pipefail
MODE="${1:-full}"
MODE="${MODE#--}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
uv --cache-dir .uv-cache run --no-project --python ">=3.11" python scripts/verify_application.py web "$MODE"
