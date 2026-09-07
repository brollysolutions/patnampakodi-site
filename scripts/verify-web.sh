#!/usr/bin/env bash
# Web verification gate. Called by scripts/verify.sh (which forwards "--ci"), by CI, and
# directly. Modes: full (default), fast (no browser checks), ci (frozen install first),
# launch (the @launch gate against PLAYWRIGHT_BASE_URL, after the normal checks).
set -euo pipefail

MODE="${1:-full}"
MODE="${MODE#--}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ ! -f "$ROOT/apps/web/package.json" ]]; then
  echo "==> apps/web absent; web checks not applicable"
  exit 0
fi
command -v pnpm >/dev/null || { echo "pnpm not found on PATH" >&2; exit 1; }

cd "$ROOT/apps/web"

if [[ "$MODE" == "ci" ]]; then
  echo "==> install (frozen lockfile)"
  pnpm install --frozen-lockfile
fi

# Build with the production header set so Lighthouse's SEO audit sees an indexable site.
# Previews and local dev builds without this flag carry X-Robots-Tag: noindex.
export SITE_INDEXABLE=true

# Add non-secret application test configuration when the website is introduced.

echo "==> lint";      pnpm lint
echo "==> typecheck"; pnpm typecheck
echo "==> unit";      pnpm test
echo "==> build";     pnpm build

if [[ "$MODE" == "fast" ]]; then
  echo "==> fast mode: browser checks skipped"
  exit 0
fi

echo "==> playwright"; pnpm exec playwright test

if [[ "$MODE" == "launch" ]]; then
  # Against a deployed host: PLAYWRIGHT_BASE_URL=https://... ./scripts/verify-web.sh launch
  echo "==> launch gate"; pnpm exec playwright test --grep @launch --project desktop
  exit 0
fi

echo "==> lighthouse"
if [[ -z "${CHROME_PATH:-}" ]]; then
  CHROME_PATH="$(node -e "console.log(require('@playwright/test').chromium.executablePath())")"
  export CHROME_PATH
fi
pnpm lhci

echo "==> web verification complete"
