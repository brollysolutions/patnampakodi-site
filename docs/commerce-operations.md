# Commerce operations and Docker handoff

New purchases use immediate guest checkout: the server checks the selected mode,
stock, approved seller details and the PIN/state delivery rule, then returns the
full total for review. Reviews last 15 minutes. Fresh orders are ASAP from one
configured pilot outlet during its weekly IST hours; staff can pause new orders.
Packaged and fresh carts stay separate. Legacy requests retain their staff delivery
quote and 24-hour quote lifetime. Payment initiation reserves stock for 15 minutes.
Only verified captures mark an order paid; browser callbacks remain provisional.
A late or extra capture is reconciled and, when fulfilment is unavailable,
refunded against that exact payment.

## Local use

For the approved local Docker review environment with simulated providers, follow [local staging](local-staging.md). Its fixtures cannot make real payments or send real messages.

Follow [local development](storefront-development.md). Run PostgreSQL and Redis,
migrate, seed the reviewed public content, then start API, web and **one** worker
(`python -m app.jobs`). Use `python -m app.admin_cli create <username>` interactively
to provision a named admin. The command prompts for a password; administrators sign
in with their username and password. `recover <username>` resets the password and
revokes existing sessions after the operator verifies identity.

Deploy the API and web sign-in form together when moving to password-only login.
Existing administrators keep their passwords and no authenticator code is needed.
If rolling back to an older MFA release, an operator must recover accounts created
or reset after this change to provision authenticator credentials for that release.

In admin, configure verified seller details, GSTIN/state, invoice prefix and the
delivery tax rate. Add one SKU per sellable pack/variant, complete all food facts,
upload an image and record initial stock with a reason. Publish only approved
records. Website content management is excluded from the admin panel at the user's
request. Coordinate approved page, outlet and policy updates with the development
team. Policy slugs
are `policies/shipping`, `policies/returns`, `policies/refunds`, `policies/privacy`
and `policies/terms`; they are added to the footer/sitemap only after publication.

Configure the Delivery tab with approved PIN codes, states and fixed fees. For fresh food,
select the pilot outlet, preparation estimate and weekly hours. An enabled flag alone
does not bypass seller, stock, PIN or opening checks. Product mode and outlet are
immutable after creation. New orders reach payment without a staff quote.

For historical staff requests, confirm delivery to the supplied Indian address, and enter the
tax-inclusive delivery fee. Customers keep their private link; WhatsApp is
optional. Public order-number/phone lookup deliberately returns only status.
Use replacement-link recovery only after independently verifying identity; it
revokes every old link. Never put a private link into analytics, logs or tickets.

Customer cancellation ends when fresh preparation starts, or before dispatch for
packaged orders. Preparation and cancellation hold the same order lock. Cancellation
before preparation restores physical stock once and requests the remaining captured
balance, including delivery. Staff can stop a fresh order during preparation after
confirming with the kitchen; that action refunds the remaining balance and does not
return the food to sellable stock. Dispatch prevents cancellation in either flow.
Staff refunds do not return
physical stock. Record a separate stock adjustment only for an actual return.
Even a full staff refund preserves delivery progress. Cancel an unshipped order
separately to close it; only cancellation before preparation returns stock.
Cancellation recognizes an already processed refund
and never submits the same money again. Orders, enquiries and provider jobs have
page controls so older records remain accessible.
The invoice/CSV ledger is based on the paid snapshot. CSV order-level totals
repeat per product row; reconcile refunds/credit notes with the accountant before
filing. Approved tax rates, invoice presentation and legal content remain release
inputs. The ledger is not a direct GSTR filing integration.

## Provider setup

Use Razorpay test credentials in staging; never enter credentials in admin forms.
Configure automatic capture in the provider account. Register the HTTPS webhook
`/api/v1/webhooks/razorpay` with a separate webhook secret and payment-captured
and refund events. The receiver validates the raw-body HMAC, persists an encrypted
inbox and deduplicates event IDs. The worker reconciles unconfirmed payments every
two minutes. Refunds retain one UUID idempotency key across retries.

An ambiguous create-order POST is **not** blindly repeated, including after an
admin retry. The worker first finds the exact receipt through the provider API.
If it cannot establish the result, investigate the provider dashboard. The
customer can retry after reservation expiry; any older capture is still handled
without overselling or changing a fulfilled order.

For Meta Cloud API, configure a reviewed supported Graph version, phone-number
ID, access token, app secret and webhook verification token. Register
`/api/v1/webhooks/meta`. Approve English utility templates:

- `order_update_v1`: order reference, update text, private management URL.
- `franchise_enquiry_alert_v1`: enquiry ID, city and admin URL. Customer contact
  details remain in admin. Only explicitly consenting staff numbers receive it.

Customer consent is unchecked by default. Private-link opt-out and inbound
`STOP`/`UNSUBSCRIBE` suppress queued customer messages. A send already in flight
may finish. Notifications are at least once: Meta does not provide the same
refund-style idempotency guarantee, so a crash after send may produce a repeat.
Delivered/read receipts are monotonic, including receipts arriving before the
worker stores a message ID. No shared inbox, SMS, customer email or rider module
is included.

Check admin **Messages** during operations. It shows failed/overdue work, retries,
worker heartbeat and settlement comparison. The worker fetches current/previous
month settlement rows daily, compares amounts and flags unknown/changed rows.
Resolve mismatches against Razorpay; use its historical exports after a longer
outage. Do not treat a missing heartbeat or unavailable check as a passing check.
The scheduler holds a PostgreSQL advisory lock to reject a second instance.

## Deployment preparation

`compose.production.yaml` packages web, API, worker, PostgreSQL, Redis and Caddy.
Images are pinned by digest. Only Caddy exposes ports. API/worker run as UID 10001;
web runs as `node`. Runtime database roles cannot bypass RLS or modify audit rows.
The API trusts forwarded client IPs only from Caddy at `172.29.91.10`, which
overwrites client-supplied forwarding headers. Adjust both network and trust
configuration together if the chosen host already uses that subnet. Access logs
are disabled; monitor status codes/health without request bodies or private URLs.

Choose a host and DNS/TLS setup separately. Start from
[`infra/runtime.env.example`](../infra/runtime.env.example) for **non-secret**
options. An operator must prepare a restricted directory outside the checkout:

| File | Contents |
| --- | --- |
| `owner/postgres_password` | Strong PostgreSQL owner password |
| `owner/migration_database_url` | Owner connection URL to `postgres:5432/pakodi` |
| `api/database_url` | Restricted `pakodi_reader` connection URL |
| `api/commerce_database_url` | Restricted `pakodi_app` connection URL |
| `api/redis_url` | Authenticated URL to `redis:6379/0` |
| `api/data_encryption_key` | Fernet key; retain securely for restoring encrypted records |
| `api/razorpay_key_id`, `api/razorpay_key_secret`, `api/razorpay_webhook_secret` | Environment-specific Razorpay values |
| `api/meta_access_token`, `api/meta_app_secret`, `api/meta_verify_token` | Environment-specific Meta values |
| `redis.conf` | `appendonly yes`, `maxmemory-policy noeviction`, a strong `requirepass` |

URL-encode database/Redis passwords in URLs. Runtime files must be readable by
the container user and inaccessible to unrelated host users; never print them
with `docker compose config`, command tracing or support logs. Blank provider
files keep that provider unavailable while staging is prepared. Production startup
rejects absent core secrets and development database passwords. Protect the media
volume and database disk with host encryption. Mounts keep owner credentials out
of API/worker containers.

With operator-supplied non-secret environment options, run sequentially:

```text
docker compose -f compose.production.yaml build
docker compose -f compose.production.yaml up -d --wait postgres redis
docker compose -f compose.production.yaml run --rm migrate python -m app.bootstrap_roles
docker compose -f compose.production.yaml run --rm migrate
docker compose -f compose.production.yaml run --rm migrate python -m app.seed
docker compose -f compose.production.yaml up -d api worker web proxy
docker compose -f compose.production.yaml exec api python -m app.admin_cli create operator-name
```

Role bootstrap is first-install only and refuses existing roles. Later releases
run reviewed additive migrations, then replace API/worker/web together. Back up
first; never use migration downgrade as a routine financial-data rollback. Keep
the previous image digest for application rollback when schema compatibility
allows it. Rotate compromised admin factors using the CLI; rotate provider
secrets through provider consoles and the protected mounted files. Data-key
rotation requires re-encryption of stored outbox/inbox records; do not simply
replace that key and lose access to existing data.

## Backup, recovery and release gates

Schedule encrypted PostgreSQL custom-format backups and matching media snapshots
off-host. Back up role provisioning/configuration and the encryption key separately.
Restore into a new database/volume first, provision restricted roles, use
`pg_restore --exit-on-error`, verify migration head, row counts, RLS and invoices,
then reconcile providers before allowing orders. `python scripts/verify_restore.py`
exercises this process against the fixed synthetic fixture only. Never point
tests or seed replacement at a production database.
Fixture commands reject runtime secret-file overrides before accessing them.
Run the gates in a local development shell without production configuration.

Processed raw webhook bodies are cleared after seven days. Delivered/suppressed
notification payloads are cleared after seven days; retryable payloads are retained
for recovery. Management links expire after 180 days, capped at 90 days after
delivery. Orders/invoices and audit history remain restricted business records;
FRAB must approve its legal retention/deletion procedure before collecting live
data. Backups need the same retention and access policy.

Before enabling live sales: approve product/menu/outlet details and five policies;
validate invoice samples with the accountant; test password reset, provider capture,
webhook retries, refunds, consent and WhatsApp templates with the configured
accounts; test mail-free recovery with staff; verify TLS, proxy trust and restored
backups on the chosen host. Production transactions and notifications were not
performed by this implementation task.

For GA4, disable Enhanced Measurement in the property, use a public-only property,
and configure `GA4_MEASUREMENT_ID`. The code requests consent before loading the
tag, removes query/fragment/referrer data, and disables advertising signals.
Private navigation creates a fresh document and private CSP excludes Google.
Leave the ID blank until privacy approval. Public indexing requires a build with
`SITE_INDEXABLE=true` and `DEPLOYMENT_ENV=production`; previews remain noindex.
The seven observed old URLs are preserved. Obtain a complete WordPress/Search
Console URL export before cutover; do not invent redirects for unobserved URLs.

Provider references checked during implementation: [Razorpay webhook validation](https://razorpay.com/docs/webhooks/validate-test/),
[refund idempotency](https://razorpay.com/docs/api/refunds/normal-refunds-idempotent/),
[settlement reconciliation](https://razorpay.com/docs/api/settlements/fetch-recon/),
[Meta business messaging policy](https://whatsappbusiness.com/policy/), and
[GA4 manual page views](https://developers.google.com/analytics/devguides/collection/ga4/views).
