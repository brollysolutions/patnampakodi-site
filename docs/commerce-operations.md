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
records. The Products screen lists saved records first, including drafts and
zero-stock items, with name/SKU search, range/publication filters and pagination.
Field information buttons explain every product-editor input. An unused product
can be deleted after confirmation; the server prevents deletion of reserved
products and any product referenced by an order, including historical orders.
Unpublish those products to stop new orders. Deletion retains the unpublished
content record, uploaded media and append-only audit history.

Deploy migration `0007_product_deletion` before the updated API/web: it grants
DELETE on variants only, retaining brand RLS and existing permissions on orders,
content and audit data. Application rollback does not restore deleted unused
products; restore data only through the approved backup procedure when required.

Website content management is excluded from the admin panel at the user's
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

### One-command Linux server setup

On the deployment server, from the checked-out repository, run:

```sh
sudo python3 scripts/deploy.py
```

Prerequisites: Python 3.11+, Docker Engine with Compose 2.20 or newer,
`iproute2`, DNS for `patnampakodi.com` pointing to this server, and inbound TCP
80/443 available for this stack. The helper checks prerequisites; it does not
install packages, change DNS/firewalls or stop another application's web server.
If 80/443 already belong to host Nginx, use the integration below. Application
ports in other stacks do not identify their Docker subnet ranges.

The helper prefers a supported `docker compose` plugin and automatically falls
back to a modern `docker-compose` executable, including v5.1.2. It checks the
version and uses the selected command throughout deployment. Compose v1 and
versions below 2.20 are unsupported; the hyphenated command name alone does not
mean the installed version is legacy. No plugin symlink or package change is
needed when a supported standalone executable is already available to `sudo`.

Deployment builds exclude Codex/Claude configuration, agent skills and instruction
files, MCP settings, private agent state, Git/CI hooks, and root workflow scripts
and tools through `.dockerignore`. Required application scripts (such as the web
image generator) remain build inputs. The runtime images copy only application
artifacts and do not run agent workflows. These exclusions do not delete tracked
files from a server Git checkout; the development workflow stays available in
Git. Running `scripts/deploy.py` directly does not invoke that workflow.

#### Existing host Nginx

For this server, diagnostics show Nginx owns 80/443 and already has an enabled
`/etc/nginx/sites-enabled/patnampakodi` site referencing a Certbot certificate.
Keep its certificate and HTTP/HTTPS listeners. From the repository root, run:

```sh
sudo python3 scripts/deploy.py --behind-nginx
```

The flag persists `PAKODI_PROXY_MODE=nginx` in runtime options, so future updates
can use the plain deployment command. Nginx mode requires Compose 2.24.4+ for
the reviewed `!override` merge. `compose.nginx.yaml` replaces both public Docker
bindings with **127.0.0.1:3502 -> proxy:80**. It does not claim 80/443, expose the
API/database/cache, stop Nginx, install packages, or edit the host's site files.
If 3502 is occupied, set a free `PAKODI_PROXY_PORT` in runtime options and update
the Nginx upstream to the same port before routing traffic.

Integrate the reviewed `infra/nginx/pakodi-proxy.inc` into the existing site's
HTTPS `server` block. Replace its previous application `location` blocks with
the include; more-specific old API/static locations would otherwise override
the new route. Remove duplicate server-level `client_max_body_size` and
`access_log` settings supplied by the snippet. Keep ACME challenge handling and
existing HTTP-to-HTTPS redirects.
The included fixed host is `patnampakodi.com`; use the existing site's canonical
redirect for `www` if configured. For a different domain, adapt the fixed host
headers to `PAKODI_HOST` as part of site review.

After reviewing the existing routing and checking its certificate, these are
the host-side preparation and validation commands (the backup is outside enabled
Nginx directories and cannot be loaded as a duplicate site):

```sh
sudo cp -L --no-clobber /etc/nginx/sites-enabled/patnampakodi /root/patnampakodi-nginx.before-pakodi.conf
sudo install -d -m 755 /etc/nginx/snippets
sudo install -m 644 infra/nginx/pakodi-proxy.inc /etc/nginx/snippets/pakodi-proxy.conf
sudoedit /etc/nginx/sites-enabled/patnampakodi
# At HTTPS server scope, replace the old app locations with:
# include /etc/nginx/snippets/pakodi-proxy.conf;
sudo nginx -t && sudo systemctl reload nginx
```

Nginx overwrites `X-Forwarded-For` with its observed client address. Internal
Caddy trusts only the Pakodi bridge gateway (`PAKODI_NETWORK_PREFIX.1`), forwards
the parsed client address, and pins the upstream scheme/host to HTTPS and the
configured domain. The API still trusts only Caddy (`PAKODI_NETWORK_PREFIX.10`).
An existing network with a different gateway stops setup pending proxy review.
Host Nginx must terminate public HTTPS; the internal HTTP port is loopback-only.
Host-local processes and users with Docker control are inside this trust boundary.
The snippet disables access logging to keep private order URLs out of access logs.
Do not replace the fixed client-address header with an appended untrusted chain.

After application startup and Nginx reload, verify the public domain, admin
login, API routing and certificate validity on the server. Public HTTPS timed
out from the development environment during this task; an enabled certificate
path is not evidence of a valid certificate or successful public cutover.

Verification tools use synthetic data:
`python scripts/verify_deploy_context.py` checks Docker's actual context
exclusions, and `python scripts/verify_nginx_proxy.py` exercises internal Caddy
routing and trusted/untrusted forwarded addresses. The latter simulates the
trusted upstream address; it does not certify the host's Nginx configuration.
The configuration follows Docker's
[override rules](https://docs.docker.com/reference/compose-file/merge/), Caddy's
[proxy trust options](https://caddyserver.com/docs/caddyfile/options#trusted-proxies),
and Nginx's [proxy header controls](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_set_header).

The command uses the fixed existing `pakodi` Compose project. It creates
`runtime.env` in the repository root when absent, defaulting to
`PAKODI_HOST=patnampakodi.com`. An existing root file is preserved; if only
`infra/runtime.env` exists it is reused. Use `--runtime-file /absolute/path`
for another non-secret options file. Files accept literal `KEY=value` entries
for the keys in `infra/runtime.env.example`, with optional enclosing quotes;
shell expressions and unknown keys are rejected. No real secrets belong in
this file. Runtime files are ignored by Git and excluded from Docker builds.
Ambient Compose options and `.env` files are not loaded; custom Compose project
names are outside this helper's scope. It supplies parsed values directly to
Compose, so there is no manual `--env-file` flag to place.

Before allocating a new Pakodi network, the helper checks every Docker IPv4
subnet and the host's IPv4 routing tables. If the configured prefix overlaps,
it selects a free candidate and saves that prefix while preserving other
runtime values. An existing Pakodi network retains its subnet; changing that
network still requires the maintenance procedure below. Network allocation can
still fail if another process claims a range after the check; retry after
reviewing the new allocation. The helper never deletes networks or volumes.

On a fresh server with no existing Pakodi containers or data volumes, missing
core credentials are generated under `/srv/pakodi-secrets` with restricted
permissions and container-readable mounts. The PostgreSQL role passwords,
Redis password and Fernet key are independent random values. Provider files
start blank, keeping real payments and messaging unavailable. Existing secrets
are never replaced; an incomplete directory or missing secrets alongside
existing data stops setup and requires operator recovery. Keep this directory
backed up securely outside Git; it is required to recover encrypted records.

The helper builds images, stops this stack's application services, starts
PostgreSQL/Redis, inspects database initialization, provisions restricted roles
only for an empty database, applies migrations, and seeds published source
content without replacing existing records. It then starts API/worker/web/Caddy
and prompts for the first administrator's username and password if none exists.
Use an interactive terminal for first installation. No password is passed on
the command line or stored in the repository. Default preview/noindex settings
remain until the normal release gates are met.

For subsequent releases, pull the reviewed changes and run the same command.
Existing deployments require typing `BACKUP READY` after verifying a backup of
database, media and secrets and arranging a maintenance window. Automation may
pass `--backup-confirmed` only after that independent verification. The helper
does not create or verify backups. It holds one host-wide deployment lock;
failed commands stop the sequence and do not restart writers after a failed
migration. There is no automatic rollback: inspect the failed stage and retry
after resolving it. It does not automate the separate legacy 5432/6379 port
migration described below; existing connection files must already use 5433/6380.

Container startup is local process/health evidence, not proof of public TLS,
provider readiness or field SEO. Complete the deployment and live sales gates
below before enabling orders or indexability. Manual steps remain available
for operator-controlled releases.

`compose.production.yaml` packages web, API, worker, PostgreSQL, Redis and Caddy.
Images are pinned by digest. Only Caddy exposes ports. API/worker run as UID 10001;
web runs as `node`. Runtime database roles cannot bypass RLS or modify audit rows.
The API trusts forwarded client IPs only from Caddy at `172.29.91.10` by default,
which overwrites client-supplied forwarding headers. `PAKODI_NETWORK_PREFIX`
sets the first three IPv4 octets: Compose derives the private `/24` subnet and
both Caddy's `.10` address and the API's exact trusted address from it. Access logs
are disabled; monitor status codes/health without request bodies or private URLs.

For the DigitalOcean Droplet Docker deployment, Caddy publishes TCP 80/443.
Inside Docker, web uses 3500, API uses 8500, PostgreSQL uses **5433** and Redis
uses **6380**. PostgreSQL and Redis have no host port mappings. Their production
listeners are pinned in Compose; PostgreSQL health checks and container CLI
defaults also use 5433. Redis still loads the protected `redis.conf`; its command
line selects 6380 while retaining authentication, persistence and eviction policy.
Local development and local staging keep their separate existing port settings.

Choose a host and DNS/TLS setup separately. Start from
[`infra/runtime.env.example`](../infra/runtime.env.example) for **non-secret**
options. An operator must prepare a restricted directory outside the checkout:

| File | Contents |
| --- | --- |
| `owner/postgres_password` | Strong PostgreSQL owner password |
| `owner/migration_database_url` | Owner connection URL to `postgres:5433/pakodi` |
| `api/database_url` | Restricted `pakodi_reader` connection URL to `postgres:5433/pakodi` |
| `api/commerce_database_url` | Restricted `pakodi_app` connection URL to `postgres:5433/pakodi` |
| `api/redis_url` | Authenticated URL to `redis:6380/0` |
| `api/data_encryption_key` | Fernet key; retain securely for restoring encrypted records |
| `api/razorpay_key_id`, `api/razorpay_key_secret`, `api/razorpay_webhook_secret` | Environment-specific Razorpay values |
| `api/meta_access_token`, `api/meta_app_secret`, `api/meta_verify_token` | Environment-specific Meta values |
| `redis.conf` | `port 6380`, `appendonly yes`, `maxmemory-policy noeviction`, a strong `requirepass` |

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

When upgrading an existing deployment from PostgreSQL 5432 / Redis 6379, use a
maintenance window and a verified backup. Stop API and worker before changing
listeners. The operator must update the port in the three database URL files and
the Redis URL file listed above, preserving each role, password, database name
and Redis database index. Recreate PostgreSQL and Redis with the new Compose
configuration, then replace API/worker/web/proxy using the normal release steps.
Keep the existing named volumes; do not run `down --volumes` or first-install
role bootstrap. Rolling back these ports requires reverting both listeners and
all four connection files together. No schema migration is required for this
port change.

Run `python scripts/verify_production_ports.py` locally to verify the rendered
production listener commands, health check, authenticated connections, absence
of published database/cache ports, and fixture persistence across restart. It
uses a unique disposable Docker project and synthetic files; it does not access
operator secrets, existing volumes or a DigitalOcean server.

### Docker address-pool overlap

If startup reports `failed to create network pakodi_private` with `Pool overlaps`,
inspect the deployment server's allocated Docker ranges and host routes:

```sh
docker network inspect $(docker network ls -q) --format '{{.Name}} {{range .IPAM.Config}}{{.Subnet}} {{end}}'
ip -4 route
```

Choose a private `/24` that does not overlap any listed Docker, host, VPC or VPN
range. A containing `/16` also conflicts: `172.29.0.0/16` includes the default
`172.29.91.0/24`. Record the first three octets in the operator's non-secret
runtime options. For example, **only if `10.253.91.0/24` is free on that server**:

```sh
export PAKODI_NETWORK_PREFIX=10.253.91
docker compose -f compose.production.yaml config --quiet
docker compose -f compose.production.yaml up -d --wait postgres redis
```

Retain the same host, secret-directory and `--env-file` options used for the
original deployment on every command. Persist the prefix in those non-secret
options so later deployments use the same network. Resume the appropriate
first-install or upgrade steps above after PostgreSQL/Redis start; rebuilding
images is unnecessary for this network-only setting.

If an existing **Pakodi** network must change subnet, use a maintenance window:
stop this stack with `docker compose -f compose.production.yaml down` (retain all
original project/env options), then recreate it with the chosen prefix and the
normal upgrade steps. Preserve named volumes: never add `--volumes`, prune Docker
networks globally or delete another application's network to solve this conflict.
Do not rerun first-install role bootstrap on an initialized database.

The configuration uses Docker's documented [Compose interpolation](https://docs.docker.com/reference/compose-file/interpolation/)
and [IPAM subnet settings](https://docs.docker.com/reference/compose-file/networks/#ipam).

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
