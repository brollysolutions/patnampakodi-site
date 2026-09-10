# Local Docker review environment

This environment reproduces the public site, commerce and admin application at
`http://127.0.0.1:3100/`, using the project's fonts and colours. It runs only local
provider fixtures. It is noindex and cannot charge money or send a real WhatsApp
message. Hosting, production TLS and real provider acceptance remain separate.

## Start and stop

From the repository root, with Docker Desktop running:

```text
uv --cache-dir .uv-cache run --no-project --python ">=3.11" python scripts/staging.py up
uv --cache-dir .uv-cache run --no-project --python ">=3.11" python scripts/staging.py status
uv --cache-dir .uv-cache run --no-project --python ">=3.11" python scripts/staging.py down
```

Startup builds the pinned application images, waits for its PostgreSQL/Redis,
runs additive migrations, imports only published reviewed source records and
starts API, web, one scheduler and the fixture provider. Existing content is
preserved. Stop preserves the database, media and fixture-provider volumes.
The helper disables default `.env` loading and ambient Compose file/project/env
overrides. The fixed project is `pakodi-stage`; only web port 3100 is exposed on
loopback through a web-only entry network. PostgreSQL, Redis, API, worker and
providers stay on an internal backend network; only web joins both. Startup
checks the published port from the host after container health checks.
The helper requires a local Docker socket/context and rejects remote endpoints.

The static infrastructure credentials and encryption fallback are local fixture
values. Do not reuse this configuration for a public host or real transactions.

## Named administrator and approved content

No test customer, product, seller or administrator is inserted into persistent
staging. The operator creates their own named admin interactively:

Set `COMPOSE_DISABLE_ENV_FILE=1` before direct Compose commands. In PowerShell:

```powershell
$env:COMPOSE_DISABLE_ENV_FILE = '1'
docker compose -f compose.staging.yaml -p pakodi-stage exec api python -m app.admin_cli create your.name
```

Enter the password at its prompt, add the displayed setup key to an
authenticator and save recovery codes in a password manager. Complete the first
login at `/admin/` with the authenticator code. Do not put these credentials in
the repository, chat, scripts or screenshots.

In Settings, enter the approved seller name/address, GSTIN/state, invoice prefix
and delivery tax rate before approving sales. In Products, enter approved SKU,
pack price, GST/HSN, required food information, image and stock. Keep incomplete
products unpublished. The seven original product URL observations are recorded
in `apps/api/content/catalog-source-inventory.json`; this file is not seed data
or approval of historical prices/taxes.

Content controls the copied public pages, menus, outlets, FAQ/testimonial blocks
and published policy pages. Enquiries supports phone-first leads, staff details,
pipeline status and dated CSV exports. Reports shows gross invoices, processed
primary-payment refunds to date and net sales for an inclusive India-date cohort,
plus the existing GST ledger. A staff refund does not reverse physical delivery
or restock goods automatically.

The approved brochure PDF, complete product food/tax information, seller details
and policy text remain business inputs. Brochure download returns unavailable
until its operator-supplied file is configured; no replacement is fabricated.
Staging reserves `/media/brochure.pdf` for that approved PDF (at most 5 MB).
After reviewing the real document, the operator can copy it into the API's media
volume with `docker compose -f compose.staging.yaml -p pakodi-stage cp approved-brochure.pdf api:/media/brochure.pdf`.
The endpoint checks that a PDF exists before offering the download.

## Local checkout and acceptance

A published, complete product can enter the guest cart. Staff quotes delivery;
the quote lasts 24 hours. Payment setup reserves stock for 15 minutes. The local
checkout explicitly asks to **Confirm test payment**. Its signed fixture webhook
enters the normal durable inbox; the worker verifies the capture and issues the
invoice. Refresh status for confirmation. Staff can mark dispatch/delivery and
request refunds through the same controls used by the normal application.
Opt-in messages receive local delivery receipts and never reach Meta.

Run disposable acceptance separately from persistent staging:

```text
uv --cache-dir .uv-cache run --no-project --python ">=3.11" python scripts/verify_staging.py
```

This creates a unique `pakodi_stage_fixture_*` project, database, network and
volumes, binds a temporary loopback port and inserts synthetic test data only
there. Its browser journey exercises checkout, a repeated signed capture after
provider restart, worker recovery, invoice, own-team delivery, partial refund and
message receipts. Independent database checks require one invoice/capture/refund.
Cleanup checks project labels before deleting only that disposable project's
volumes. Reports remain in `.agent-workflow/reports/`.

Run the repository's full application gate and synthetic backup/restore check
sequentially; never run database-mutating suites together. Passing fixture checks
does not establish live Razorpay/Meta acceptance, production backup restoration,
production deployment or field performance. Current measured evidence belongs in
`docs/agent-context/feature-status.md`.

The network and environment behavior follows the official
[Docker network reference](https://docs.docker.com/engine/network/#connecting-to-multiple-networks)
and [Compose environment settings](https://docs.docker.com/compose/how-tos/environment-variables/envvars/).
