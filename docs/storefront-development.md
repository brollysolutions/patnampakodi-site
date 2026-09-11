# Run the storefront locally

Requires Node.js 22.19+, Python 3.11+, uv 0.12.10, Docker Desktop/Engine,
and Git Bash on Windows. Dependencies and the PostgreSQL image are pinned.
These commands use local development fixtures; they do not deploy the site.

From the repository root:

```text
docker compose up -d --wait postgres redis
uv sync --project apps/api --frozen
```

In `apps/api`, migrate and load the reviewed initial content:

```text
uv run --frozen alembic upgrade head
uv run --frozen python -m app.seed
uv run --frozen python -m app.serve
```

In a second terminal, from `apps/web`:

```text
npm ci
npm run dev
```

Open `http://127.0.0.1:3501`. FastAPI listens on loopback port 8500;
PostgreSQL uses loopback port 55450 and Redis uses 6450. The separate persistent
Docker preview uses web port 3500. The API entry point explicitly selects
the event loop required by Psycopg on Windows. The defaults need no `.env` file.
Use `CONTENT_API_URL` on the Next.js server and `DATABASE_URL` on the API when
configuring another environment. Never use local fixture passwords in production.

The site is noindex by default. A production build for the canonical public
host must explicitly set `SITE_INDEXABLE=true`; `DEPLOYMENT_ENV=preview` always
disables indexing. Private prefixes remain noindex even on the public host.
The canonical origin is `https://patnampakodi.com`. Hosting/cutover is not configured.

## Verification

Keep ports 8510 and 3510 free for verification; normal development can remain on
8500/3501. Keep PostgreSQL and Redis running. Install the pinned test browser once from `apps/web`:

```text
npx playwright install chromium
```

Run the full gate from the root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1 --ci
```

Or `bash scripts/verify.sh --ci`. Linux needs Playwright's system dependencies;
CI installs them with `npx playwright install --with-deps chromium`.

The gate uses a dedicated `pakodi_mvp_test` database, checks commerce, authentication, payment races, publication and RLS
cases, regenerates and compares contracts, runs lint/format/type/unit/build checks,
then owns and stops its local API/web servers. Browser tests cover all seven
routes at 390, 768 and 1440 pixels plus filtering, no-JS, keyboard and private
routes. SEO checks run against the native production build. The gate then builds
the pinned Linux standalone images and verifies migrations, seed, API/web,
indexing/private headers and worker heartbeat in a unique synthetic database.
Lighthouse audits the standalone web image through the pinned Caddy configuration
over local HTTPS/HTTP/2. Each route/device gets three sequential cold-browser runs;
the unchanged performance budgets apply to their medians, and every run must
meet accessibility, SEO and best-practice thresholds. All individual failures
and reports remain visible. The runner selects the installed Playwright browser
through Lighthouse's supported `CHROME_PATH` environment variable and records
the observed browser user agent; it fails if that executable is missing. Its disposable
localhost certificate is allowed only in the isolated audit browser; no host
trust store or production TLS setting is changed. This does not validate a
production certificate. Containers, temporary CA volumes and their database are
cleaned up on exit.
Reports stay ignored under `.agent-workflow/reports`, `apps/web/test-results`
and `apps/web/playwright-report`. `fast` excludes browser/SEO/container/performance checks.

For focused API verification: `uv run --no-project python scripts/verify_application.py api`.
For web verification after API fixture setup: `bash scripts/verify-web.sh`.
For browser/SEO/performance reruns of the existing build:
`uv run --no-project python scripts/verify_application.py browsers`.

## Content and contract updates

The request path is Next.js route → server-only content loader → generated
schema → FastAPI dependency → service → PostgreSQL RLS. No seed JSON is imported
by the running frontend. Named admins manage food records in Products; website
content management is absent from the admin panel.
See [commerce operations](commerce-operations.md) for provisioning and the worker.

The initial [content input](../apps/api/content/README.md) preserves existing
database rows. `python -m app.seed --replace` explicitly replaces only matching
seed keys; review that data before using it. Publication of packaged products
requires complete food facts and a positive price. Products includes a searchable
setup list of 57 source foods and ready mixes with their recorded names and
available product-specific artwork.
The authenticated API derives these templates from the saved references; they are
not purchasable variants. Confirm missing prices, food/tax details, stock and
fresh preparation outlets before publication. Menu prices, precise outlet addresses/hours, legal
policies and franchise terms still require business confirmation.

After editing server schemas, run `uv run python -m app.export_openapi` from
`apps/api`, then `npm run contracts` from `apps/web`. Commit both generated files
in `packages/contracts` and reconcile consumers. Merged migrations are immutable.

`compose.yaml` is an isolated development database/Redis fixture.
`compose.production.yaml` and both Dockerfiles provide the container handoff;
see [operations](commerce-operations.md) for runtime files, TLS, backups and
provider acceptance. Hosting and real provider transactions remain separate.
