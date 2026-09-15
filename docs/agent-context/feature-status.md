# Feature status

## Kukatpally website expansion - 2026-09-15

Item 26 implements the approved Premium editorial expansion across Home, Menu,
Our Story, Franchise, Branches, Contact and Kukatpally details. The refined rooster
logo, large dry-pakodi artwork and varied page layouts retain Poppins/Inter and
the peach/orange palette. FAQs start open and remain operable without JavaScript.
Only Kukatpally is published; five older branch URLs show noindex notices linking
to the current branch. Source facts, brochure inclusions and artwork provenance
are recorded in [kukatpally-site-expansion.md](kukatpally-site-expansion.md).

The explicit `--site-expansion` seed validates and updates 16 approved records,
preserving historical payloads, products, stock, orders and legal content. Its
repeatability/preservation regression passes. No migration, contract, dependency,
authentication or financial-transition change. Ordering remains paused.

Fresh verification: 132 API tests, one migration head, unchanged generated
contracts, web lint/format/types, 27 unit tests and production build pass. Browser
verification passes 58 public and 18 retained commerce/admin tests with two
existing viewport skips. Native open FAQs, no-JavaScript navigation, enquiries,
keyboard/reduced motion, 320px/200% reflow and axe are covered. Technical SEO
passes on all seven current URLs; seven intentional skip-link warnings remain.
Additional current/retired branch axe checks pass at 320px and 1440px. Food images
decode and layouts were visually reviewed at 1440/768/390/320px. Workflow checks
pass 150 tests with three platform skips and validate 22 mirrored skills.

Container migration, seed, API/web, indexing/private headers and worker heartbeat
pass. All six Lighthouse medians pass the unchanged budgets in the final 18-run
batch: mobile performance 95/98/98 for home/menu/contact; desktop 100 throughout.
Accessibility, SEO and best practices are 100. Home mobile median LCP is 2493 ms,
close to the 2500 ms limit. Two individual outliers are retained. The initial
batch's home mobile median failed during low machine benchmarks; the unchanged
build passed the complete repeat. Reports: `lighthouse-1789474485133` and
`lighthouse-1789474992681`, plus `editorial-performance-repeat.log`.

Initial formatting, brochure-link redirects and source-coupled legacy unit
fixtures were corrected. One checkout test returned 503, then passed in isolation
and in the full 132-test API rerun without service changes. Evidence is retained
in `editorial-application-full.log` and `editorial-web-full-3.log`. Code, security,
design and SEO review have no unresolved finding. Native Safari, field vitals,
production deployment, owner confirmation of branch details and exact flavour
appearance remain unverified.

Implementation `f91ce5a` is pushed to origin and upstream in open
[PR #23](https://github.com/brollysolutions/patnampakodi-site/pull/23), from
`feat/kukatpally-site-expansion` into upstream `main`. Origin is an independent
copy, so the PR uses the matching upstream feature branch while local tracking
remains on origin. The helper's `state --remote` is unverified because it assumes
a fork head; direct GitHub repository/base/head/SHA readback confirms the PR.
No protected branch or verification guard was changed.

Two initial push attempts failed during API checks, including an intermittent
legacy order-helper failure. Additive local diagnostics preserved response and
test behavior; the subsequent origin and upstream push gates passed all 132 API
tests and remaining fast checks. The intermittent cause remains unverified; it
was not represented as a fixed application defect. Logs are retained locally.
The final documentation update does not change application code. Next priority:
owner content confirmation and review of PR #23, which builds on open PR #22/#21.

## Four-flavour menu and ordering pause - 2026-09-15

Item 25 implements the approved four-flavour informational launch. Public
navigation is Menu, Our Story, Franchise, Branches and Contact. PIN checking,
search, favourites, cart, shopping and order navigation are removed. Four locally
optimized food illustrations accompany the menu without food prices. Franchise
packages and central contact details follow the supplied ten-page brochure,
now bundled as a complete 2.2 MB download. Source and artwork provenance are in
[four-flavour-menu.md](four-flavour-menu.md).

Ordering defaults to disabled in the API. Direct quote/order/revision/payment
entry points reject new purchases before side effects; old shopping URLs return
307 to Menu. Existing private history, cancellation, invoices, signed callbacks,
refunds and staff workflows remain available. The targeted `--menu-launch` seed
preserves commerce/outlets while replacing only approved editorial records and
unpublishing the previous menu. No migration; contracts regenerated.

Fresh verification: 131 API tests, one migration head, contracts, lint/format/types,
27 web unit tests and production build pass. The complete browser continuation
passes 52 paused-site and 18 explicitly enabled commerce tests (two existing
viewport skips). Axe, keyboard/reduced-motion, 320px/200% reflow, no-JavaScript
content/navigation and technical SEO on all 12 public URLs pass. SEO warnings
are the 12 intentional skip links. Workflow verification passes 150 tests with
three platform skips and validates 22 mirrored skills. Existing lint/deprecation
warnings remain non-blocking; no security or performance gate was weakened.

The initial full gate stopped on formatting, then the first browser run found a
real tablet hero overflow and a navigation timeout. The inherited 390px minimum
image height forced an 813px page at a 768px viewport. Removing that constraint
restored 768px reflow; the complete rerun passes without changing timeouts.
Desktop/mobile/tablet screenshots and mobile navigation without JavaScript were
reviewed against the approved identity and Apple accessibility/layout guidance.

Container migration, seed, API/web, indexing/private headers and worker heartbeat
pass. A fresh container serves exactly the four approved names with ordering
false. All six Lighthouse medians pass the unchanged budgets across 18 runs:
mobile performance 97/99/97 for home/menu/contact; desktop 100. Accessibility,
SEO and best practices are 100 throughout. One homepage mobile outlier (94,
LCP 2642 ms) is retained; the median LCP is 2435 ms. Evidence is in this session's
`four-flavour-web-full.log` and `lighthouse-1789468333811` local reports.

Code/security review has no unresolved finding. Both isolated Docker staging
browser tests and the database recovery invariants pass, including signed replay,
provider/worker restart, invoice, delivery, partial refund and messaging fixtures.
All temporary staging resources were removed. Implementation `df96f57` is pushed
to origin and is in open [PR #22](https://github.com/brollysolutions/patnampakodi-site/pull/22),
from upstream `feat/four-flavour-menu` into `main`; the PR head SHA was read back
directly. Origin is an independent copy, so the helper's cross-repository PR
operation failed. Normal upstream push hooks passed, and GitHub created the PR
from the matching upstream feature branch. The helper's remote verifier assumes
a fork head; direct GitHub repository/base/head/SHA readback supplies the delivery
evidence for this layout. No protected branch, hook or gate was changed.

The local targeted seed applied 14 approved records, preserving product, order
and outlet counts. Managed API/web preview processes are healthy at ports
8500/3501. Browser inspection confirms four named items, no shopping links,
the corrected central phone and ordering disabled. Preview process sessions are
intentionally running; they are not completed verification commands. Native Safari, production
rollout, live providers and field vitals remain unverified. The branch preserves
the existing unmerged menu-stock commits from PR #21. Next priority is PR review,
then coordinated API/web deployment with the targeted seed and ordering paused.

## Menu starting stock - 2026-09-15

Item 24 fixes product creation leaving inventory at zero when an operator enters
a portion/pack quantity. The form now separates **Starting stock** from **Portion
or pack size**. A create-only, bounded integer field saves inventory and its audit
event in the product transaction. Existing clients default to zero; edits cannot
set starting stock or overwrite reservations. Further inventory changes retain
the existing audited stock adjustment flow. No migration or public template change.

Initial regression reproduced HTTP 422 for starting stock before implementation.
Fresh native verification passes 123 API tests, 27 web unit tests, 64 browser
tests (two existing project skips), lint/format/types/build, one migration head,
contract regeneration and technical SEO on 13 pages. Workflow checks pass 150
tests with three platform skips and validate 22 skills. The expanded browser
test covers creation with five units, edits preserving inventory, publication,
adding to cart and subsequent stock adjustment at desktop/mobile/tablet sizes.
Keyboard help, axe and 320px reflow pass; reviewed desktop/mobile screenshots.

The first full gate stopped at a running development server's locked Next.js
library. After stopping those local processes, the next run found an ambiguous
new test selector matching a related product too. Scoping it to the main product
resolved all three browser failures on a fresh full browser run. No gate weakened.
The browser/full continuation returned exit 0 with Docker migration, seed, API,
web, private/indexing headers, worker heartbeat and all six Lighthouse medians
passing. Eighteen runs cover home/menu/contact on mobile and desktop. Mobile
performance medians are 96/98/98; desktop 100; accessibility, SEO and best
practices 100 throughout. One homepage mobile LCP outlier (2686ms) remains in
the report; its three-run median is 2466ms and passes the unchanged budget.
Security/design/code review found no unresolved defect. Native Safari and live
deployment remain unverified.

Implementation `66d6ade` was pushed to origin and is in open
[PR #21](https://github.com/brollysolutions/patnampakodi-site/pull/21), with an
exact SHA readback. GitHub reports origin as an independent repository, so the
delivery helper's fork PR failed after its successful commit/push. With existing
upstream write access, the same commit was pushed through normal hooks to
`brollysolutions:fix/tejal-menu-starting-stock` and the PR targets its `main`.
Direct GitHub metadata verifies this topology; the helper's assumed origin-head
repository/branch does not fit it. No workflow checks were bypassed.

The local web/API services were restored. The reported bowl item has five units
through its audited adjustment; a browser check confirms Add to cart works on
the user's local product page. Next priority: review PR #21 and separately plan
live rollout. The repository-map assumption can be addressed as a workflow task.

## Shared Nginx deployment and packaging - 2026-09-12

Item 23 adds persisted `--behind-nginx` deployment mode for the server's existing
Nginx on 80/443. Compose 2.24.4+ replaces public proxy ports with loopback 3502;
API/web/database/cache remain private. The existing enabled `patnampakodi` site
and its Certbot certificate paths are confirmed by operator output. The helper
preserves host site configuration and certificates; a reviewed HTTPS-server
snippet forwards application traffic to the loopback port. The API still trusts
only internal Caddy, which trusts forwarded addresses only from the bridge
gateway and pins the HTTPS scheme/domain. Unexpected gateways, invalid ports,
occupied loopback ports and unsupported Compose versions stop setup.

Docker build contexts now exclude Codex/Claude configuration, agent skills and
instructions, MCP settings, private workflow state, Git/CI hooks and root
workflow scripts/tools. Application build scripts remain. Runtime images do
not invoke AI workflows; tracked files remain in development/server Git checkouts.

Fresh verification: 38/38 deployment tests pass in Linux; the workflow-only gate
passes 150 tests with three Linux-only skips, skill validation and shell checks.
Ruff passes. The synthetic Docker context excludes 39 fixtures while retaining
15 required inputs. Actual standalone Compose rendering confirms loopback-only
publication, private services, correct Caddy config and API trust. Pinned Caddy
validation and a disposable trusted/untrusted client test pass routing, API
prefix stripping, HTTPS/domain forwarding and spoof rejection; fixture cleanup
passes. Security/code review found no unresolved defect in the changed scope.

Public HTTPS probes timed out and registry DNS prevented obtaining a Nginx test
image. Host Nginx syntax/runtime, certificate validity, live deployment and full
browser/Lighthouse acceptance are unverified. The proxy fixture simulates the
trusted upstream address. Next: publish the task PR, review the existing Nginx
application routes, merge, deploy and perform server-side Nginx/TLS acceptance.

The delivery helper returned exit 0 and verified implementation commit `d858ef0`
in open [PR #20](https://github.com/brollysolutions/patnampakodi-site/pull/20),
targeting upstream `main` from the contributor's `feat/docker-staging`. Mandatory
commit/fast push gates passed, with a matching remote head and clean worktree.
A final response-header comparison found missing HSTS in the internal mode.
The new assertion failed before the fix; the follow-up restores the original
`Strict-Transport-Security: max-age=31536000` response header. The final proxy
verification returned exit 0 with HSTS, path handling, trusted/untrusted client
addresses and HTTPS/host headers passing. Ruff and diff checks pass; final
review has no unresolved finding. Remote readback follows publication.

## Modern standalone Compose compatibility - 2026-09-12

Item 22 fixes the deployment helper's rejection of a server with modern
`docker-compose` v5.1.2 but no `docker compose` plugin. It prefers a supported
plugin, falls back to the standalone executable, requires Compose >=2.20.0,
and reuses the selected command for all deployment operations. It prints the
selection and retains local-engine, fixed-project, runtime-environment and
data-preservation checks. No package installation or plugin symlink is required.

Fresh verification: all 32 deployment tests pass in the pinned Linux container;
Windows passes with three Linux-only skips. The workflow-only gate passes 144
tests with three skips, skill parity/validation and shell syntax checks. Ruff
check/format passes. Actual standalone Compose v5.4.0 successfully renders the
production configuration through the helper using synthetic options. Tests cover
the reported v5.1.2, unsupported/malformed versions, missing executables, command
propagation and local-engine guards. A Windows sandbox temporary-file failure
was resolved by an approved rerun. Review found no unresolved correctness or
security regression. Full application/browser/Lighthouse and live-server
deployment remain outside this compatibility check's evidence.

The delivery helper returned exit 0 and verified implementation commit `d8c6e67`
in open [PR #19](https://github.com/brollysolutions/patnampakodi-site/pull/19),
from the contributor's `feat/docker-staging` to upstream `main`. Mandatory commit
checks and the fast application push gate passed, with matching remote head and
a clean worktree. This documentation follow-up records that readback. Next
priority: merge this fix, pull on the prepared server and rerun
`sudo python3 scripts/deploy.py` for host acceptance.

## One-command server deployment - 2026-09-12

Item 21 adds `sudo python3 scripts/deploy.py` for the Linux deployment server.
The command defaults to the owner's `patnampakodi.com`, creates or reuses the
non-secret runtime options, checks Docker Compose and host web ports, chooses
and persists a free subnet before creating a new network, and retains an
existing Pakodi network. The reported pool overlap is an address-range conflict;
the supplied host-port list cannot identify subnet availability.

Fresh installations generate independent core secrets outside the checkout.
Existing credentials and volumes are preserved; partial secrets or ambiguous
database roles stop setup. Deployment is serialized, requires confirmed backups
for updates, validates restricted database logins and Redis authentication,
runs migrations and preserving content seeding, starts containers, and prompts
for the first administrator in an interactive terminal. Runtime files are
excluded from Git and Docker build contexts. No new dependencies or API/schema/UI
changes are introduced.

Fresh targeted verification: all 26 deployment tests pass in an isolated Linux
container, including actual UID/GID 10001 secret access under umask 077,
symlink rejection and lock contention/release. Windows passes 23 applicable
tests and skips those three Linux-specific cases. Ruff check/format passes.
The final workflow gate passes 138 tests (three Linux-only skips), 22-skill
validation and shell checks. Production Compose rendering with helper-supplied
options passes; the API image confirms UID/GID 10001. The full CI attempt passed
112 API tests, migration/contract checks, web lint/format/types, 27 unit tests
and the production build. Its additional browser run was deliberately stopped
after 22 passing desktop tests because no UI changed; the command exited 1.
The remaining browser cases, technical SEO and Lighthouse are unverified in
this run; it is not a full release pass. Initial Windows sandbox attempts failed
on temporary-directory access; approved explicit-exit reruns passed. A redirected
PowerShell wrapper also returned 1 despite passing workflow output; the direct
workflow rerun returned 0. Delivery linkage follows the fresh remote readback.

A disposable Docker backend check also passes fresh setup and a second
deployment through the helper's deployment stages using generated synthetic
credentials. Restricted logins, Redis authentication, migrations, seed, API
health, worker startup and admin creation succeed; edited content, the admin
count and secret hashes are preserved. Its uniquely owned containers/volumes
are cleaned up. Web/proxy and public TLS are outside that backend smoke check.

Final review also reproduces and fixes an existing blank network prefix not
being saved after range selection. The new regression fails against the initial
implementation and passes after the correction, including a preserving retry.
The initial delivery was interrupted with `90b40d6` committed locally; its
terminal result was unavailable on resumption. Process inspection found no
remaining delivery process and GitHub still held `594dc2f`, so no successful
push is inferred from that attempt. Delivery is resumed serially.

The resumed helper returned exit 0 and verified implementation head `0476c4b`
pushed in open [PR #18](https://github.com/brollysolutions/patnampakodi-site/pull/18),
targeting `brollysolutions/patnampakodi-site:main` from the contributor's
`feat/docker-staging`. Remote head, tracking and clean-worktree checks passed,
as did the mandatory fast push gate. This follow-up records that initial
delivery; the final documentation head requires a fresh remote readback.

Scope remains local code and synthetic verification. The helper does not
install Docker, change DNS, integrate an existing shared reverse proxy, generate
or verify backups, migrate legacy data-service ports, activate live providers,
or claim public TLS/field SEO acceptance. Next priority: run the reviewed helper
on the prepared server, then complete host/provider/release acceptance.

## Production Docker network overlap - 2026-09-12

Item 20 fixes the hard-coded production network range. The operator's server
inventory confirms `brollyjuniors_default` owns `172.29.0.0/16`, containing the
default `172.29.91.0/24`. The custom-prefix regression failed against the original
Compose file. `PAKODI_NETWORK_PREFIX` now derives the /24, Caddy's .10 address and
the API's exact trusted proxy together, retaining the default when unset/blank.
The operations guide documents range selection and volume-preserving recovery.

Fresh checks pass: default/blank/custom Compose rendering, disposable Docker
overlap reproduction, successful alternative allocation and proxy runtime IP,
PostgreSQL 5433/Redis 6380 authentication, private ports and restart persistence,
112 workflow tests, 22-skill parity, shell checks and verifier Ruff. The local
network harness initially failed on Docker host/none networks' null IPAM config;
the corrected harness passed and removed only its owned fixture networks. Initial
verifier lint failures were corrected; security and PR self-review found no
actionable defect in proxy trust, published ports, fixture isolation or recovery.

`10.253.91.0/24` avoids the supplied server Docker ranges and host/VPC routes;
actual server startup remains unverified. No deployment server, operator secrets or
production data were accessed. Browser/SEO/Lighthouse are not rerun for this
network-only change; prior public performance acceptance remains open. Delivery
continues `feat/docker-staging` after merged PR #16. Commit `6b04233` is pushed in
open [PR #17](https://github.com/brollysolutions/patnampakodi-site/pull/17), with
matching remote head verified. The first push failed with local database/cache
fixtures stopped. After starting them, all 112 API tests, migration head and
contract parity passed; the required fast push gate also passed web lint/format/
types, units and build. That gate skips browser/performance/live SEO. Next priority:
persist `PAKODI_NETWORK_PREFIX=10.253.91` in the server's non-secret runtime options
and resume deployment. This documentation follow-up records the verified delivery.

## Production PostgreSQL and Redis ports - 2026-09-12

Item 19 configures production PostgreSQL on 5433 and Redis on 6380, as requested.
Compose pins both private listeners, aligns PostgreSQL health checks and CLI
defaults, and retains Redis's protected configuration while overriding its port.
Only Caddy 80/443 is published. The operations guide specifies the three
PostgreSQL URL files and Redis URL file that the operator must update together,
plus maintenance, volume preservation and rollback requirements. Local
development/staging ports, authentication, RLS and application contracts are
unchanged. No schema migration or real secret-file edit is included.

`scripts/verify_production_ports.py` renders production Compose with synthetic
paths, then exercises only PostgreSQL and Redis in a unique, private Docker
project. The check passes: PostgreSQL 5433 health and TCP/CLI connectivity,
Redis 6380 authenticated access and denial without authentication, override of
a legacy Redis 6379 setting, closed old listener ports, no host bindings, retained
append-only/no-eviction settings and synthetic data persistence across restart.
Cleanup is constrained to the generated project and verified container labels.
All 112 workflow tests, 22-skill parity and verifier lint pass. The security/diff
review found no new exposure, credential leak or application behavior change.

Browser, SEO and Lighthouse are not rerun for this configuration-only change;
the prior public speed acceptance remains open. A DigitalOcean host, operator
connection files and production data were not accessed. Delivery follows merged
PR #15 on `feat/docker-staging` against upstream `main`. Next priority: coordinate
the operator's connection-file changes and complete live deployment acceptance.

Implementation commit `5d6cb14` is pushed in open
[PR #16](https://github.com/brollysolutions/patnampakodi-site/pull/16), targeting
upstream `main` from `feat/docker-staging`; the remote PR head was verified at
that commit. The required pre-push fast gate passes API/RLS tests, one migration
head, generated-contract parity, web lint/format/types, unit tests and production
build. Browser/performance/live SEO are explicitly skipped by that gate. This
documentation follow-up adds the confirmed PR and fresh gate evidence; production
deployment remains unverified.

## Saved product visibility and CRUD - 2026-09-11

Item 18 makes the saved catalogue the first Products panel. Published products,
drafts and zero-stock items are visible with a count, name/SKU search, range and
publication filters, pagination, details, create/edit, publication and stock
controls. Menu suggestions and CSV tools remain available in collapsed panels.
Every editor field has a labelled information button with field-specific help,
44px targets and keyboard/Escape support. Publication changes from the saved list
refresh the open editor's checkbox without discarding other field edits.

The new authenticated product page endpoint returns a bounded, filtered
`ProductPage`; the original variants list remains compatible. Confirmed deletion
locks the product and rejects reservations or any order reference, including
historical orders. It unpublishes the retained content record and preserves media,
orders and audit history. Updates and CSV imports lock before saving to prevent a
concurrent delete from being undone by an upsert. Additive migration
`0007_product_deletion` grants DELETE only on variants under existing brand RLS.
OpenAPI and TypeScript contracts were regenerated; the browser proxy forwards
DELETE with its existing same-origin and CSRF protections.

Fresh verification on 12 September: 112 workflow tests, 22-skill parity, 112 API
tests (including eight product/RLS/locking regressions), one migration head,
contract parity, web lint/format/types, 27 units and production build pass. The
initial broad browser run passed 58, skipped two duplicate reflow projects and
failed six admin assertions whose labels now also matched help buttons. After
correcting those selectors and a renamed success-message expectation, all six
admin journeys have fresh passing coverage across desktop, mobile and tablet.
Product CRUD survives reload; every help control, publication synchronization,
confirmed deletion, axe and 320px reflow pass. The original broad command remains
failed. Technical SEO passes 13 routes with 13 existing fragment-link warnings.

Local Docker staging was rebuilt and migration applied; all six services are
healthy and `/admin/` returns 200. A read-only before/after product digest is
identical: the existing published, zero-stock product was preserved. No test
products or credentials were inserted into persistent staging. Browser images
were reviewed at 1440px, 768px and 320px; no remaining product design or
accessibility defect was found. Screen-reader speech and other browsers remain
unverified. The refreshed catalogue service validates and returns the existing
product through the new page response without changing its data.

Container migration/seed, API/web, indexing/private headers, worker heartbeat
and local Caddy HTTPS/HTTP/2 checks pass. All 18 Lighthouse reports complete with
accessibility, best-practices and SEO scores of 100, but the unchanged public
speed budgets fail: home/menu/contact performance medians are mobile 57/66/73
and desktop 89/94/83. Container verification therefore exits 1; only desktop
menu meets every budget. The reports also flag host CPU calibration. No budget
or security gate was weakened. Keep the follow-up PR in draft. Production
deployment, live providers and field vitals remain unverified.

[PR #15](https://github.com/brollysolutions/patnampakodi-site/pull/15) delivers
`vamshisaideep9:feat/docker-staging` against upstream `main`, following merged
PR #14. Implementation commit `b923765` is pushed and its commit/push hooks pass;
the remote PR head was verified before linking this evidence. The PR remains
draft for the public speed failure. Next priority: meet the public speed budgets
and finish operator-approved inventory and live-provider launch acceptance.

## Local PostgreSQL port and password-only admin sign-in - 2026-09-11

Item 17 moves the local Docker PostgreSQL host mapping and every local consumer
to `127.0.0.1:5434`, while preserving internal Docker PostgreSQL at `5432` and
keeping production PostgreSQL unexposed. A regression test checks the compose
mapping and all local API/test/verification URLs stay synchronized.

Admin login now accepts only username and password. The OpenAPI contract and
generated TypeScript client no longer include a TOTP/recovery-code field; the web
form and disposable browser fixtures match it. Provisioning and password recovery
keep session revocation and audit logging, while previous TOTP/recovery columns
remain inert for immutable-migration compatibility. Argon2 verification,
per-IP/per-username limits, disabled-account checks, HttpOnly/SameSite Strict
cookies, CSRF/Origin checks, RLS and audit safeguards remain enforced. The direct
security review found and corrected the legacy `enrolled` session guard that would
otherwise reject sessions for password-only accounts. Login retains its account
row lock through session creation so a concurrent password reset cannot leave a
new session authenticated with the previous password.

The user authorized another port because `client1-pgbouncer` owns 5433. Local
PostgreSQL is healthy on 5434 with its existing volume; the other project remains
running. Eight focused authentication tests pass against PostgreSQL/Redis,
covering password-only login, invalid/unknown/disabled accounts, username-case
throttling, Redis fail-closed behaviour, login/reset locking, reset revocation,
legacy enrollment compatibility, CSRF/Origin and logout.

Fresh full-gate evidence: 112 workflow tests and 22-skill parity, 104 API tests,
lint/format, one migration head, regenerated contracts, web lint/format/types,
27 web units and native production build pass. The broad browser run passes 60
checks, intentionally skips two duplicate reflow projects and fails one desktop
checkout five-second navigation assertion. That unchanged test passes a focused
rerun; all three admin/axe journeys pass. Technical SEO passes 13 routes with
13 existing fragment-link warnings. The original broad command remains failed.

Container migration/seed, API/web, private/indexing headers, worker heartbeat and
Caddy local HTTPS/HTTP/2 routing pass. All 18 Lighthouse reports complete with
accessibility, best practices and SEO 100. The command exits 1 because unchanged
speed budgets fail; evidence is `lighthouse-1789142800448`.

| Page/device | Median performance | LCP (ms) | TBT (ms) | Budget |
| --- | ---: | ---: | ---: | --- |
| Home/mobile | 54 | 3961 | 2193 | Fail |
| Menu/mobile | 58 | 3449 | 1618 | Fail |
| Contact/mobile | 70 | 3291 | 903 | Fail |
| Home/desktop | 92 | 993 | 130 | Pass |
| Menu/desktop | 92 | 1185 | 120 | Pass |
| Contact/desktop | 85 | 1127 | 157 | Fail |

Docker staging acceptance passes both browser tests and all five database
invariants. Its first attempt stopped during PostgreSQL initialization; the
unchanged rerun completed acceptance and cleaned its disposable resources, then
reported EOF at the optional presentation prompt. This is not a zero-exit full
command. The persistent preview refresh exits 0 and preserves its volumes.
Anonymous login review passes keyboard order, generic errors, no overflow and
WCAG axe checks at 1440/768/390/320px; screenshots were inspected at desktop and
320px. A newly provisioned local named account passes login, session, logout and
revocation verification. Credentials are excluded from tracked/private artifacts.
Native Safari, physical devices and manual browser zoom remain unverified.

Security and code review find no remaining actionable defects in this change.
Removing the second factor is the user's explicit tradeoff. API and web must
roll out together; rolling back to an MFA release requires operator recovery
for accounts created/reset after this change. No schema migration or new
dependency is introduced. Production/provider acceptance remains unverified.
Delivered in [draft PR #14](https://github.com/brollysolutions/patnampakodi-site/pull/14),
from `vamshisaideep9:feat/docker-staging` to `brollysolutions:main`. The delivery
helper and required pre-push gate exit 0, with clean Git status, synchronized
origin tracking and verified remote PR head. PR #13 is already merged. PR #14
remains draft for performance acceptance. Next priority: speed budgets and the
approved launch product, food/tax and stock inputs recorded under item 16.

## Port migration and food catalogue preparation - 2026-09-11

Item 16 is implemented and locally verified on `feat/docker-staging` for
[PR #13](https://github.com/brollysolutions/patnampakodi-site/pull/13). The new local
map is Docker web 3500, native web 3501, API 8500, browser web/API 3510/8510,
PostgreSQL 55450 and Redis 6450. These ports were checked for active listeners;
another project's API already uses 8000 and is outside this change. Existing
project volumes, private network boundaries and public production TLS are preserved.

The saved references reconcile to **57 distinct setup entries: 53 fresh foods
and four ready mixes**. Products provides name search, range filtering, pagination
and a prefilled form. Pachi Mirchi retains its original product URL. The private
API uses the normal admin session and brand-scoped database connection; existing
variants and stock are preserved. Seven product-specific source images are reused.
Visual review found generic pakodi photos on menu drinks/dips, so other setup
entries use neutral icons until staff select approved Media. Confirmed launch
prices, portions, stock and required food/tax information remain requested inputs;
the templates do not create purchasable variants or approve packaging claims.

Fresh checks: 111 workflow tests and 22-skill parity; 97 API tests, lint/format,
one migration head and regenerated contracts. Five catalogue regressions pass
again after the source-photo correction. Web lint (two existing navigation
warnings), formatting, types, 27 unit tests and production build pass. The broad
browser run passed 58 checks, failed the same new dietary-select locator in all
three viewports, and skipped two duplicate reflow projects. Correcting the test
to locate the semantic combobox yields three passing admin/axe journeys on the
same build. Technical SEO passes 13 routes with the existing skip-link warnings.

Container migration/seed, API/web, private/indexing headers, worker heartbeat and
Caddy HTTPS routing pass with the new internal ports. Lighthouse completes all
18 reports with accessibility, best practices and SEO 100; no HTTP 500 occurs.
The overall command exits 1 because the unchanged timing budgets fail. Report:
`lighthouse-1789133177557`, web image `40798c15`, API image `bc2de2e2`.

| Page/device | Median performance | LCP (ms) | TBT (ms) | Budget |
| --- | ---: | ---: | ---: | --- |
| Home/mobile | 57 | 3663 | 1908 | Fail |
| Menu/mobile | 65 | 3250 | 1096 | Fail |
| Contact/mobile | 63 | 3602 | 897 | Fail |
| Home/desktop | 85 | 1197 | 222 | Fail |
| Menu/desktop | 94 | 888 | 150 | Pass |
| Contact/desktop | 91 | 869 | 136 | Pass |

The slow-CPU warning limits interpretation but does not waive a failed budget.
Historical CI for prior head `d5ce5de` also fails performance: homepage mobile
median LCP 2589 ms exceeds 2500 ms, with performance 94 and TBT 194 ms. Its other
five page/device medians and four workflow jobs pass
([run 34594368754](https://github.com/vamshisaideep9/patnampakodi-site/actions/runs/34594368754)).
That CI run is not evidence for this follow-up. Final-head CI remains unverified.

The final disposable Docker run passes both acceptance tests and all five SQL
invariants, including payment/replay, provider and worker recovery, invoice,
delivery, refund, messages and recovery from a real local API outage. Manual
review checks the setup list and form at 1440, 768, 390 and 320px, ready-mix and
name filters, focus and sticky controls. Saving a source ready mix with explicitly
synthetic details leaves it unpublished with stock zero, preserves existing stock
and removes its setup entry (57 to 56). The disposable project is cleaned up
successfully. Native Safari, physical devices and manual browser zoom are unverified.

The persistent preview refresh exits 0: website/admin on port 3500, web image
`3838f013`, API image `aa6670ac`; all four named volumes are retained. Home, admin
and the storefront API return 200 with noindex. Port 3100 is no longer listening;
the other project's services were not modified. No synthetic catalogue, sale or
admin fixtures were inserted into this preview. Draft PR #13 carries the reviewed
change; final remote delivery evidence belongs in the handoff. Next priority:
confirmed business activation data, hosting/live providers and passing unchanged
performance budgets. The [client guide](../client-presentation.md) supplies a
repeatable disposable demo and ten-minute buyer/operator walkthrough.

## Classic ecommerce redesign - 2026-09-11

Item 15 is implemented under the approved [redesign plan](commerce-redesign-plan.md),
with functional acceptance passing and draft status for performance acceptance.
Scope: original identity, shopping-first public pages and full admin, independent
fresh/packaged carts, guest favourites, server-priced immediate checkout and
PIN-based delivery, one pilot outlet with hours/pause, preparation and cancellation.
The user also requests a practical client presentation at delivery. Existing
photos/logos take precedence; image generation is conditional on a specific gap.
The latest user correction removes website content management from the admin
panel; the client walkthrough and operating guide reflect the remaining eight tabs.
The subsequent admin UI/sticky-navigation request is implemented in the same item:
compact branded admin header, desktop sidebar/mobile tabs, section introductions,
current-view order counts, clearer order cards and focused section navigation.
The storefront header is sticky as well. The broad refinement run passed 58
browser checks, failed three and skipped two duplicate reflow projects. Mobile
grid overflow and skip-link stacking were corrected. A fresh rebuild passes all
12 affected admin, staff-approval, sticky-header and keyboard checks across desktop,
mobile and tablet. Screenshot review confirms the mobile form now fits the screen.
PR #12 is merged at fdf22ab. Previous functional results below are historical;
current API regression coverage is 95 passing tests, including last-stock payment
and fresh preparation/cancellation races. Staff can stop fresh preparation and
refund the remaining balance without automatically restocking prepared food;
customer cancellation remains blocked. Concurrent retries and CSRF are covered.
One migration head and generated contracts pass. Workflow checks pass 110 tests
and 22-skill parity. Final frontend lint, formatting, types and 27 unit tests pass.
Technical SEO passes all 13 routes after the refinement. The 320px/720px sweep covers
CSS reflow; manual browser zoom and native Safari remain unverified. The final
branded error callback refreshes server data before retrying. Both Docker acceptance
tests and five SQL invariants pass, including an actual content outage, accessible
error title, successful retry, missing-photo layout and checkout/recovery/refund.
The disposable presentation confirms fresh payment, preparation, customer
cancellation blocked, staff cancellation and completed refund. The final admin
navigation correction passes separate frontend and browser verification. The final
Docker rebuild passes both acceptance tests and all five SQL invariants, then
cleans up its disposable project (exit 0). Manual browser review covers all eight
admin sections and 320px, 390px, 768px and 1440px layouts. The persistent preview
at port 3100 is refreshed successfully with web image `a84155fb` and API image
`689efa6d`; existing data is preserved, without synthetic sale/admin insertions.

Container migration/seed, API/web/private headers, proxy and worker checks pass.
Performance acceptance remains open: the last measured build **fails** unchanged
Lighthouse timing budgets. All 18 reports
completed with accessibility, best practices and SEO 100; no Contact HTTP 500 recurred.
Retained report: `lighthouse-1789116967943`.

| Page/device | Median performance | LCP (ms) | TBT (ms) | Budget |
| --- | ---: | ---: | ---: | --- |
| Home/mobile | 53 | 3978 | 2044 | Fail |
| Menu/mobile | 63 | 3372 | 1319 | Fail |
| Contact/mobile | 67 | 3124 | 934 | Fail |
| Home/desktop | 76 | 1391 | 266 | Fail |
| Menu/desktop | 95 | 960 | 135 | Pass |
| Contact/desktop | 93 | 955 | 115 | Pass |

CLS remains below 0.021. Slow-CPU warnings are an evidence limit, not proof that
the host explains the failure. No budget or throttling changed. The measured
web image `38fc23b5` precedes the final error retry callback, staff-cancellation
and admin navigation changes, which receive separate functional verification.
The latest broad web run stopped at the now-corrected browser defects; it did not
repeat Lighthouse. Final-head performance acceptance remains pending. Production/field performance,
live providers and approved business activation remain unverified.
See [client walkthrough](../client-presentation.md).
Review target: draft PR from `vamshisaideep9:feat/docker-staging` to upstream `main`;
[current branch PR lookup](https://github.com/brollysolutions/patnampakodi-site/pulls?q=is%3Aopen+is%3Apr+head%3Afeat%2Fdocker-staging).
Next priority: final-head CI/performance acceptance and approved operator inputs.

## Original identity and ordering access - 2026-09-11

Item 14 is implemented and functionally verified, with draft release status.
The user now requires the original fonts and colors.
Fresh read-only browser inspection of patnampakodi.com and its shop establishes
Poppins body/editorial text, Inter shop headings, peach `#FEF1E4`, body `#353535`,
orange `#FF6210`, red `#C0392B` and gold `#F39C12`. This supersedes replacement
Abril Fatface/Archivo styling. Existing commerce already supports guest requests,
staff delivery quotes, private payment/tracking and administration. Persistent
staging still needs approved sellable catalog and seller inputs; no live ordering
readiness is claimed.

Fresh verification: 110 workflow tests and 22 identical skills; 86 API tests,
one migration head and unchanged generated contracts; web lint (one existing
navigation warning), formatting, types, 20 unit tests and production build;
54 browser/axe tests across desktop/mobile/tablet; 13 technical SEO routes with
zero failures (the documented skip-link warnings remain). Initial localFont
array-key and stale sharing-image font-path failures were corrected and the
affected web checks rerun successfully. Container migration/seed, API/web,
private/indexing headers, worker heartbeat and proxy smoke checks passed.

The full web gate **failed** Lighthouse acceptance. Reports are retained locally
in `lighthouse-1789099512531`: home mobile median performance 62, LCP 3382 ms,
TBT 1282 ms; menu mobile 66, LCP 3282 ms, TBT 1303 ms. Home/menu desktop median
performance scores 89/80 also miss the 90 budget. Fourteen usable reports score
100 for accessibility, best practices and SEO. The third contact-mobile request
returned HTTP 500 and aborted the remaining contact-desktop measurements, so the
audit is incomplete as well as failing. Slow-CPU warnings and similar historical
local failures are evidence limits, not permission to relax budgets or attribute
the entire failure to the host. Production/field performance is unverified.

Final review also preserves white headings on the dark legacy fallback story
section and distributes the matching font license notices. The final staging
build and `scripts/verify_staging.py` pass (exit 0), including checkout, signed
replay, provider/worker recovery, invoice, delivery, partial refund and messaging
fixtures. Its disposable project was cleaned up. The local preview was refreshed
with `scripts/staging.py up` (exit 0), using final web image
`b80747741c2bc070359e7c04d053470ceb4233ef2f85e85331390e23517e8b9d`.
Six final identity/navigation/dialog browser checks pass across desktop/mobile/
tablet; an isolated DOM probe confirms the fallback heading remains white.
Ten sequential contact GETs returned 200 with noindex (0.17-3.16 seconds), so the
audit's HTTP 500 did not recur in that check; its cause remains unresolved.

Security/design/SEO/PR self-review found no unresolved change-specific security
or functional defect after fixing the fallback contrast and license notices.
Reviewed exact package pins, integrity and OFL notices; npm reports zero known
vulnerabilities. Native Safari, field vitals and live sales remain unverified.
Delivery target: draft PR from `vamshisaideep9:feat/docker-staging` to shared main;
[current branch PR lookup](https://github.com/brollysolutions/patnampakodi-site/pulls?q=is%3Aopen+is%3Apr+head%3Afeat%2Fdocker-staging).
Next priority: performance/HTTP 500 acceptance and approved catalog, seller and
provider inputs. The approved staff quote flow remains; immediate checkout is
an unanswered user question. No real payment, message or production deployment.

## PR #11 upstream integration - 2026-09-11

PR #10 is merged into upstream/main at f93edde, following PRs #8 and #9.
Item 13 conflicts are resolved in the existing
[PR #11](https://github.com/brollysolutions/patnampakodi-site/pull/11).
Only the two implementation records conflict. The resolution preserves both
upstream and staging history; all code, tests, contracts, migrations, Docker
configuration and CI match the previous staging head d198c04.
Acceptance: current upstream/main is an ancestor, the same PR receives a normal
push and GitHub reports no conflicts. No additional feature, PR or deployment.
Planning/implementation recommendation: gpt-6-astra / High; selected settings
remain unchanged. Fresh workflow verification passes 110 tests, 22-skill
parity and shell syntax. Diff review confirms only these two records differ
from d198c04 and no conflict markers remain. Delivery hooks run the API/web
fast gate; full browser/Lighthouse/Docker acceptance remains a CI check.
Next priority: review PR #11 with its existing performance and operator gates.

Previous-head Linux CI 34543506150 passed functional checks and independent
Docker checkout/recovery/refund acceptance, but contact-mobile performance
failed (91, LCP 2554 ms, TBT 296 ms). PR #11 remains draft for that separate
failure; budgets and the failed-gate result are preserved. Prior draft/pending
statements below are historical and do not override the current merge status.


## PR #10 upstream integration - 2026-09-11

PR #9 is merged into upstream/main at 1544478, following PR #8. Item 12
conflicts are resolved in the existing [PR #10](https://github.com/brollysolutions/patnampakodi-site/pull/10).
Only the two implementation records conflict; application code, tests, contracts,
migrations and CI merge without changing the previous admin head e6a4b2b.
Preserve the TOTP boundary regression, transaction tests, reporting behaviour and
all performance budgets. Acceptance: the current base is an ancestor, the same
PR is updated normally and GitHub reports no conflicts. No new feature or PR.
Planning/implementation recommendation: gpt-6-astra / High; selected settings
remain unchanged. Fresh workflow verification passes 106 tests, 22-skill
parity and shell syntax. Diff review confirms only these two records differ
from e6a4b2b and no conflict markers remain. The delivery hooks run the API/web
fast gate; browser/Lighthouse acceptance remains a separate CI check.
Next priority: review the updated PR #10 while retaining its performance gate.

The PR remains draft: previous-head Linux CI 34542851812 passed functional
checks but failed home/contact mobile performance. This integration does not
resolve that separate failure. Earlier draft/pending statements below are
historical checkpoints; current upstream state supersedes them.


## TOTP test boundary correction - 2026-09-11

Three controlled rendering experiments were rejected: replacing Next Link,
using mobile grid rows and deferring off-screen sections did not consistently
improve the failing pages; the layout experiments also changed section heights.
No experimental runtime code is retained. The original public layout, navigation,
fonts, colours, timing budgets and throttling remain unchanged. The TOTP test
correction passes all 74 admin-branch API tests, lint/format, migration-head and
contract checks. Fresh Linux checks on the corrected commits remain required.

The pre-push TOTP replay test had a reproduced 30-second boundary race:
calling TOTP.now() after fixture login sometimes generates a genuinely new,
valid code. A controlled next-window clock reproduced HTTP 200 versus the old
401 expectation. The test now reconstructs the exact consumed step and checks
its rejection while it remains in the valid time window, then checks recovery
code single use. The deterministic reproduction fails before the correction and
passes after it. Authentication code, accepted skew and rate limits are unchanged.
Planning/implementation recommendation for this bounded correction: gpt-6-astra /
High; the selected session settings remain unchanged.


## Four-PR remote acceptance readback - 2026-09-11

PR #8 is ready for review at `4dc5b6d`, with full fork CI
[34534326169](https://github.com/vamshisaideep9/patnampakodi-site/actions/runs/34534326169) passing:
63 API, 18 web unit and 45 browser tests; SEO/container checks; mobile
Lighthouse medians 99/98/96 and desktop 100 throughout.
PR #9 is ready for review at `000f945`, with full fork CI
[34534816171](https://github.com/vamshisaideep9/patnampakodi-site/actions/runs/34534816171) passing:
67 API, 20 web unit and 48 browser tests; mobile medians 98/99/97, desktop 100.
One individual menu-mobile observation misses its budget; the existing three-run
median policy passes. Accessibility, best-practices and SEO are 100 throughout.
No budgets, throttling or security controls were relaxed. These Linux results
do not erase the separately recorded failing Windows mobile measurements.
PR #10 remains draft: CI 34535340526 passes functional checks and sandbox launch
but fails home/contact mobile timing budgets. Diagnostics are being collected.
Merge order remains #8, #9, #10, then Docker staging; no PR was merged by the agent.
The older sections below retain their original delivery evidence.

## Docker staging acceptance - 2026-09-11

Initial fork CI 34539338452 passes functional/browser/SEO/container checks and
all four workflow matrix jobs. Its 18 Lighthouse runs complete: home mobile
95/LCP2358/TBT182 passes, menu 95/TBT230 and contact 93/LCP2544/TBT213 fail;
desktop profiles all score 100. Accessibility, best-practices and SEO are 100.
The later Docker acceptance step was skipped by the failed application step.
CI now runs that separate disposable acceptance after a completed application
step even if it failed; the earlier failure still fails the job. Cancelled runs
or a skipped application step do not proceed. No gate is bypassed.


Item 13 is implemented on `feat/docker-staging` in [PR #11](https://github.com/brollysolutions/patnampakodi-site/pull/11), stacked on PR #10. At initial publication it is draft pending Linux performance acceptance. Current remote checks and review status are recorded on the PR.
Acceptance: repeatable loopback-only noindex Docker startup, isolated fake providers,
private guest checkout through signed durable webhooks, provider/worker recovery,
one invoice/capture, manual delivery, partial refund and local messaging receipts.
Synthetic product/seller/admin data is confined to a uniquely named disposable
acceptance database; persistent staging imports only published approved source
content. No live provider requests or real business data are introduced.
Planning recommendation: gpt-6-astra / High; implementation and final security
review: gpt-6-astra / Extra High. Selected session settings remain unchanged.
Fresh checks pass 86 API tests, one migration head, generated contracts, 110 workflow tests, 22-skill parity, lint/format/types, 20 web unit tests and production build. Synthetic backup/restore matches all 19 table counts and the migration head. Docker mobile acceptance passes checkout, signed replay after provider restart, worker recovery, invoice, delivery, partial refund, populated sales and local message receipts. Independent database checks pass one invoice/capture/refund and preserved delivery. The disposable project `pakodi_stage_fixture_9e2299230e42` was cleaned. Public browser/SEO checks now pass. Persistent staging startup and readback pass at http://127.0.0.1:3100/.
All six services are healthy. The public site, shop and admin entry return 200
with noindex headers and metadata; robots disallows crawling and the sitemap
is empty. Exactly 70 published content records are present. There are zero
unpublished records, variants, admins, settings, orders, enquiries, payments or
refunds. Catalogue is empty and brochure returns 404 until approved input arrives.
The environment is left running for the operator; its data volumes are preserved.


Final local full gate (2026-09-11): 110 workflow tests and 22-skill parity,
86 API tests, one migration head, generated contracts, lint/format/types,
20 web unit tests, production build, 51 browser/axe tests, 13 SEO routes and
container migration/seed/health/worker checks pass. The gate exits 1.
Lighthouse completes 16 observations: mobile performance medians 62/71/69
fail, with slow-CPU warnings; home/menu desktop medians 92/94 pass. The second
contact-desktop observation receives HTTP 500 after the web content fetch's
five-second timeout; the last observation is skipped, so that profile has no
complete median. Reports remain in .agent-workflow/reports/lighthouse-1789079099725.
These failures are retained; no budget, throttling, timeout or sandbox is relaxed.
The added benchmark/script/layout diagnostics pass syntax, formatting and five
launcher/budget tests; a fresh Linux gate remains required for this PR.


CI diagnosis also proved chrome-launcher 1.2.1 adds --disable-setuid-sandbox on Linux. The Lighthouse wrapper preserves the pinned launcher defaults explicitly while omitting that implicit addition. Its regression reproduces the old launch flags and verifies sandbox preservation. Existing performance thresholds and throttling are unchanged; PRs #8/#9 now pass Ubuntu runtime acceptance. This staging PR awaits its own fresh Linux gate.
## Current Linux performance diagnosis - 2026-09-11

The pinned Chromium sandbox now launches successfully. Fork CI run
34535340526 passes functional/browser/SEO/container checks but fails the unchanged
mobile performance budgets: home performance 93 / TBT 265.5 ms; contact 91 /
LCP 2579 ms / TBT 281.5 ms. Desktop medians are 100. Public rendering files
are identical to the passing ecommerce head 000f945. That rules out a public
source difference, but does not establish runner variation as the cause.
The Lighthouse log now retains its CPU benchmark and, for failed observations,
main-thread categories, script bootup and long tasks. It changes no measurement,
budget, throttling or sandbox option. Fresh syntax and five launcher/budget tests
pass. This diagnostic update remains draft until Linux acceptance is verified.


CI correction: chrome-launcher 1.2.1 implicitly disabled the Linux SUID sandbox. Lighthouse now supplies every pinned default explicitly while avoiding that implicit flag, so the installed companion helper can be used. The regression reproduces the old Linux flags and verifies retained sandbox/defaults. No budgets or throttling changed; new Linux runtime/performance acceptance is pending.


## Admin completion — 2026-09-11

Item 12 is delivered in draft [PR #10](https://github.com/brollysolutions/patnampakodi-site/pull/10) on `feat/admin-completion`, stacked on PR #9. Acceptance:
staff can enrich a phone-first enquiry without changing its source/purpose,
export an inclusive India-date/status CSV safely, review invoiced gross/refunded/
net sales and select or preview an uploaded draft image. Existing product,
content, stock, order, fulfilment, GST, messaging and named-admin controls remain
the foundation. Reports must respect request-scoped authorization and brand RLS;
extra captures cannot inflate sales or reduce the invoice cohort's net totals.

Planning recommendation: gpt-6-astra / High; implementation and final security
review: gpt-6-astra / Extra High. Selected settings are unchanged. This slice
adds no live provider calls, synthetic persistent business data or dependencies.
Fresh checks pass 74 API tests, one migration head, generated contracts, 106 workflow tests, 22-skill parity, lint/format/types, 19 web unit tests and production build. All 51 browser/axe tests and 13 technical SEO routes pass (13 intentional fragment warnings). Container migration, seed, API/web/indexing and worker heartbeat pass. All 18 Lighthouse runs completed: desktop performance medians 94/96/97 pass; mobile 65/74/67 fail unchanged LCP/TBT budgets. Accessibility, best-practices and SEO score 100 throughout. Reports: `lighthouse-1789073180159`. Full gate fails on performance; Linux runtime/performance acceptance remains pending.

The shared commerce dependency now commits before exposing HTTP success. Its
ASGI regression first observed an old `requested` status at HTTP 200, then reads
`approved` with function scope. A commit-failure regression returns 503 and proves
rollback. Both tests pass. Mobile axe found an inaccessible horizontal GST table;
GST and daily-sales scroll regions now have keyboard focus and accessible names.
The corrected mobile report is included in the passing browser run.

Ubuntu Lighthouse diagnosis: the downloaded Chromium could not start its sandbox
under AppArmor. The preinstalled helper failed its ownership/permissions check.
CI now installs the companion helper from pinned Chromium 1243 as root-owned
mode 4755 on the ephemeral runner and validates those properties before launch.
Sandbox and budgets stay enabled; Bash syntax passes and Linux runtime evidence
is pending. OpenAPI now explicitly writes LF; Windows generation was checked for
stable LF bytes after a CRLF-only delivery-state mismatch on the catalog branch.

## Earlier upstream integration history

## PR #9 upstream integration - 2026-09-11

PR #8 was merged into upstream/main at d5ab5c5. Item 11 conflicts are resolved in the existing [PR #9](https://github.com/brollysolutions/patnampakodi-site/pull/9).
The resolution reconciles the implementation records and retains both
commit-before-response and rollback coverage. All application,
contract, migration, frontend and CI files match the previous PR #9 head.
Acceptance: upstream/main is an ancestor, no unresolved conflicts, retained tests
pass and the same PR receives a normal push. No new feature or PR is introduced.
Planning/implementation recommendation: gpt-6-astra / High; selected settings
remain unchanged. Fresh API verification passes all 67 tests, lint/format, one
migration head and unchanged generated contracts. The workflow gate passes
106 tests, 22-skill parity and shell syntax. Diff review found no unresolved
conflicts or code changes. Fresh browser/Lighthouse execution is left to CI;
previous CI 34534816171 passed at 000f945 and is historical evidence.
The next priority is PR #9 review, then the existing admin/staging PRs.
Earlier draft/pending statements below describe historical checkpoints.


## Earlier upstream verification history

## Commit-before-response correction — 2026-09-11

CI exposed an order-approval refresh failure. A deterministic ASGI regression
observed HTTP 200 while another database connection still read `requested`.
The commerce dependency now uses function scope so commit/rollback completes
before the response starts. The same regression then reads `approved`; all eight
targeted transaction/admin tests pass on the stacked admin branch. Full checks
on this branch follow. Planning/implementation/security recommendation remains
gpt-6-astra / Extra High; selected settings are unchanged.

The catalog branch's Ubuntu CI passes browser/SEO/container smoke, then its
Lighthouse subprocess exits before producing scores. Remove quiet logging to
retain the launch diagnosis; no browser flags or budgets are relaxed. PR #8
remains draft until full verification passes.

## PR1 CI correction ? 2026-09-11

Draft PR #8 is open at `efebb72`; its first fork CI passed all four workflow
matrix jobs and 43 browser tests, but two no-JavaScript menu navigations timed
out waiting for the whole page load. They now wait for DOMContentLoaded before
asserting the same 51 cards, category/search behavior and reset. No assertion,
timeout, performance budget or production behavior was relaxed. The same
correction passes desktop/mobile/tablet within the next branch's fresh 48-test
browser run. The full Ubuntu application/performance gate remains pending.


CI correction: chrome-launcher 1.2.1 implicitly disabled the Linux SUID sandbox, preventing use of the installed companion helper. The Lighthouse runner now supplies every pinned default explicitly while avoiding that implicit flag. The regression reproduces the old Linux flags and verifies retained sandbox/defaults. No performance budgets or throttling changed. Fresh Linux runtime/performance acceptance is pending.


## Catalog delivery and transaction follow-up — 2026-09-11

Item 11 is delivered as draft [PR #9](https://github.com/brollysolutions/patnampakodi-site/pull/9),
initial commit `920a058`. Ubuntu passes 48 browser tests, technical SEO and Docker
smoke, then Lighthouse exits before scores are produced. Launch logging is now
enabled; the budgets and browser flags are unchanged. The shared transaction
dependency now commits before HTTP success, with an ASGI regression proving
the previous stale-read window. A rollback regression checks failure responses.
This correction also ships in PR #8; admin reporting is the next slice.

Verbose CI diagnostics identify Ubuntu AppArmor denying Chromium's sandbox
startup. The runner's preinstalled helper failed its ownership/permissions check.
CI now installs the companion helper from pinned Playwright Chromium 1243 as a
root-owned mode-4755 file on that ephemeral runner, following Chromium's helper
instructions. The runtime guard remains; no sandbox-disable flag, global AppArmor
change, new package or performance-budget change is introduced. Bash syntax
passes; Linux execution remains pending. Both transaction boundary/rollback tests
pass locally. OpenAPI generation now explicitly writes LF, verified on Windows,
to avoid generated-file line-ending changes during delivery.


## Ecommerce completion ? 2026-09-11

Item 11 is delivered as draft PR #9 on `feat/commerce-catalog`, stacked on draft PR #8.
Acceptance: published-only original product/category/tag URLs and sitemap,
bounded combined catalog search/sorting, quantity/cart flow and admin/CSV
metadata round trips. Prices and stock remain server-authoritative. Incomplete
source products stay unpublished; real food/tax/seller inputs remain outstanding.
Fresh verification passes 65 API tests, one migration head, generated contracts,
19 web unit tests, lint/types/build, all 48 browser/axe tests and technical SEO
on 13 public routes. All 35 original asset hashes match. Docker build/migration,
seed, API/web/worker and local TLS proxy smoke pass. Windows Lighthouse completed
all 18 runs: desktop medians pass (94/96/97); mobile medians fail (71/70/74), with
slow-CPU warnings. Budgets remain unchanged. Reports are retained locally at
`lighthouse-1789067711968`. Ubuntu performance remains unverified: PR1 CI stopped
at two menu load waits, whose DOM-ready correction now passes all three widths.

Recommendation: gpt-6-astra / Extra High for planning, implementation and final
security review; selected settings are unchanged. No new provider integration,
customer accounts, courier, coupon or review system is included in this slice.

## Four-PR completion — 2026-09-10

The user approved the full website/ecommerce/admin plan. Item 10 is delivered
as draft [PR #8](https://github.com/brollysolutions/patnampakodi-site/pull/8),
commit `efebb72`; remote head and clean status verified. Its purpose:
preserve the live-site content, original images, section order and URLs, while
retaining Abril Fatface, Archivo and the project's orange/brown/cream tokens.
The phone-only entry form now has a retry-safe backend and a stored admin lead.
Real products must remain unpublished until their required business information
is approved. No substitute food/tax records or brochure are authorized for staging.

Items 11–13 finish ecommerce, the admin reporting backlog, and local Docker
staging respectively. Provider fixtures are authorized for verification; real
payments/messages and production cutover remain separate. Fresh Windows checks
pass 106 workflow tests, 22-skill parity, 62 API tests, one migration head,
generated contracts, lint/types, 17 web unit tests and the production build.
The corrected browser run passes **45 tests** across desktop/mobile/tablet;
technical SEO passes on **13 public routes**, with only intentional skip-link
fragment warnings. Original asset hashes/formats/dimensions pass for all 31 files.
The final native browser run passes **45 tests**, including the no-JavaScript
FAQ, delegated dialog/focus and CMS-bound source content at all three widths.
Technical SEO passes all **13 public routes**. The final container build passes;
its Windows Lighthouse mobile profiles still exceed the existing budgets and
report a slow test CPU. No budget, throttling or security gate was relaxed.
The branch will remain a draft review until the existing Ubuntu CI runs the
same full gate successfully; local performance is failed, not passed.

The renderer uses a fixed, escaped HTML serializer for static content and one
client enquiry handler. Tests exercise executable strings, unsafe destinations,
fixed element/attribute names and readable initial HTML. Menu/outlet bindings
cover staff edits, unpublishing and new published records. Branch contact copy
is editable source data, not independently verified location structured data.
Item 11 (catalogue URLs/search/admin metadata) is the next implementation slice.
The commit hook now always uses the repository's npm toolchain. A shell regression
confirms that an installed pnpm cannot trigger a second package installation;
the lint gate remains enabled. All 106 workflow tests pass after this repair.
PR linkage for this slice: `feat/live-site-parity` into `upstream/main`; the
verified remote PR URL is recorded by the delivery helper and the next slice.

Earlier browser runs exposed missing source FAQ answers/contact links, tablet
wrapping, combined-filter test assumptions and a multi-screen test timeout.
Those issues were corrected and the fresh browser run passes. The existing
commerce navigation lint warning is unchanged. Historical PR #7 evidence below
does not certify this change.

## Approved MVP implementation — 2026-09-10

Delivered for review in [PR #7](https://github.com/brollysolutions/patnampakodi-site/pull/7) from `feat/pakodi-mvp`,
isolated from the original uncommitted
`feat/pakodi-storefront` checkout. The approved source snapshot is included in
this delivery; original files were not staged, moved or discarded.

Implemented surfaces: stored-content public routes, packaged SKU listing/detail,
category/price filters, cart/request/private management, staff delivery quotes,
stock reservations, Razorpay adapters, refund/invoice lifecycle, opt-in Meta
notifications, named password/TOTP admins, stock/CSV/media/content/enquiry editors,
GST ledger, worker health/settlement comparison, private indexing boundaries,
optional consented public GA4 and Docker packaging. Single stock location and
manual own-team delivery; no courier/rider module or customer email provider.

P1 search, FAQs/testimonials, brochure, enquiry CSV and sales summaries are
deferred as approved. Complete approved product/food/menu/outlet/policy/tax inputs,
full old-site URL inventory, vendor account/template acceptance and the chosen
host's deployment/backup/privacy checks remain release prerequisites. The code
does not fabricate these business facts or claim production transactions.

Fresh checks passed 106 workflow tests, 53 backend integration tests, eight web
unit tests, 39 browser tests at three sizes and technical SEO checks for 13 routes.
The corrected Docker/Lighthouse gate passed all six three-run median profiles
(18 observations; one individual outlier retained), and restoration matched
all 19 table counts and the migration head. Earlier full CI commands failed at
the old audit runner; passing functional and corrected audit evidence is recorded
separately. A linked-worktree push-hook fixture leak was reproduced and fixed;
its new regression also preserves the protected-ref input stream. The delivery
helper exited 0 and verified initial head `2b7acc4`, an open PR against shared
`main`, a clean worktree and no unpushed commits. This is a point-in-time record;
current remote state must be checked again after this documentation update. See
[MVP verification](mvp-verification.md) for review coverage, retained failures,
measurement conditions and release prerequisites. Planning recommendation:
`gpt-6-astra` / High; implementation: `gpt-6-astra` / Extra High, selected settings
unchanged. No subagents were used. Next priority is configured staging acceptance
after this PR, followed by the approved P1 backlog.

## Commerce source ingestion and delivery proposal — 2026-09-09

Three user-supplied documents are archived unchanged and indexed. The
[reconciled delivery brief](pakodi-commerce-reconciliation.md) maps every one
of the MVP's 50 requirements (45 P0, 5 P1) into six proposed phases, with
acceptance tests and separate planning/implementation effort recommendations.
The [visual proposal](website-design-decisions.md) retains the locked fonts,
colors and button contrast rule; cream, imagery and layout remain proposals.

The limited [live-site baseline](pakodi-live-site-baseline.md) confirms HTTP 200,
homepage noindex/nofollow, its canonical and seven linked public page paths.
Only the homepage was retrieved; full migration inventory, browser inspection
and business-content verification remain outstanding. The Playwright attempt
did not provide usable browser evidence; HTTP retrieval succeeded.

No application features are implemented by this change. Celery/Valkey source
assumptions do not replace approved APScheduler/Redis. Stale feature references,
email/TOTP assumptions, blanket production indexability, business facts and
external fee/legal claims are documented without silently accepting them.
Next priority: confirm the first build slice and the proposed design/privacy
decisions, then implement the stored-content storefront foundation.

Fresh checks in this session:

- Full `scripts/verify.ps1 --ci` gate: exit 0, **104 tests**, **22 matching
  shared skills**, configuration and shell checks. The initial sandbox attempt
  failed to execute uv; the approved rerun passed using the installed runtime.
- Local source/traceability/link check: exit 0; three byte-identical source
  archives, recorded SHA-256 values, all 50 IDs covered once, correct P0/P1
  totals and resolving derived-document relative links.
- `git diff --check`: passed after an approved rerun following sandbox Git
  access failure. Documentation/security self-review: no actionable findings.
- API/web/migration checks: not applicable, those layers do not exist. Apple
  and rendered design, accessibility, Lighthouse and live integrations:
  unverified, not presented as passed.

Initial delivery `54dc9ba` was pushed to `origin/feat/pakodi-commerce-briefs`.
The helper returned exit 0 and verified open
[PR #6](https://github.com/brollysolutions/patnampakodi-site/pull/6), targeting
`brollysolutions/patnampakodi-site:main`, matching local/remote head SHA and a clean
worktree. This documentation follow-up records that observed initial delivery;
current remote state must be read again. Existing production and provider
accounts were not changed. Historical sections retain their original evidence.

## Approved stack and SEO requirement - 2026-09-09

Documented and verified: the user selected Next.js, Python/FastAPI,
PostgreSQL, APScheduler, Redis and Docker and required an SEO-friendly site.
`technology-stack.md` preserves the instruction and deployment question;
the index, repository contract, partner guide and plan now reflect the decision.
The stack is not implemented; hosting capabilities and SFTP/SSH access are
unconfirmed. Next priority: define website scope and hosting under item 2.
Fresh verification: full PowerShell CI gate passed (exit 0), with 104 tests,
22 matching skills, configuration and shell syntax checks. Documentation/diff
review found no actionable defects. Application/browser/deployment checks are
not applicable; no credentials or infrastructure were added. Initial delivery
`d1ec065` was pushed from `feat/advanced-seo-toolkit` to `origin`; the helper
verified open [PR #5](https://github.com/brollysolutions/patnampakodi-site/pull/5)
against shared `main`, matching head SHA and a clean worktree. The first helper
attempt was blocked by sandbox access to its Git lock; the approved rerun passed.
Older sections below retain
their original evidence and describe the state at their respective deliveries.

## Advanced SEO and design workflow — 2026-09-09

Delivered for review in [PR #4](https://github.com/brollysolutions/patnampakodi-site/pull/4)
from `vamshisaideep9:feat/advanced-seo-toolkit` to the shared `main`. Initial
implementation `c756df9` was pushed successfully; the delivery helper verified
the PR OPEN with head SHA matching local HEAD and a clean working tree. This
documentation follow-up records that observed delivery; subsequent remote state
must be checked again rather than inferred from this record.

The shared toolkit adds detailed SEO/AEO/GEO/LLMO, competitors, keywords,
existing-content audits, natural writing, SEO/UI/UX and reporting procedures.
The local-plugin builder reuses reviewed installed Lighthouse 13.4.1 and Chrome
DevTools MCP 1.9.0, refuses existing output, and keeps machine paths and reports
local. Exact dependency versions and the npm lockfile are tracked; no automatic
installation or client configuration change occurs on checkout/setup/CI.

The user's design workflow uses Taste, Impeccable and Kowalski for requested UI/UX,
then Apple Design verification. Impeccable and Kowalski are installed personally
and mirrored in the repository as pinned guidance adaptations with licenses,
notices and source hashes. Existing Taste and Apple Design installs are retained.
Upstream executable downloaders, hooks and agent configuration are excluded.

Fresh verification:

- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1 --ci`:
  exit 0; **104 tests**, **22 matching shared skills**, configuration and shell
  syntax checks. The new tests cover HTML extraction/preservation, plugin output
  preservation, package/executable failures, cleanup boundaries and source parity.
- Initial sandboxed tests failed because Windows denied temporary-directory
  access; the approved rerun passed. The first full gate then exposed generated
  Python bytecode being treated as skill source. A regression reproduced it;
  parity now excludes interpreter caches while still detecting source changes.
- Eight new/changed skill entrypoints passed the system skill validator. Design
  source hashes, personal copies and adapter links matched. The SEO guide's local
  links and Python syntax passed; the shared files contain no personal paths.
- The generated plugin passed manifest validation and its complete synthetic
  smoke test: MCP initialization (29 tools), browser snapshot, performance trace,
  MCP Lighthouse, and CLI mobile/desktop HTML/JSON reports, all successful. The
  harness's intentional MCP shutdown exit is recorded separately from test status.
- `npm audit --prefix tools/seo-audit-tools --package-lock-only --omit=dev --json`:
  exit 0, zero known vulnerabilities. Reviewed official source identity, engines,
  licenses, exact versions, resolved registry URLs and integrity values.
- Security and PR self-review covered the builder, browser ownership/cleanup,
  failure propagation, dependency changes, instruction adapters, provenance,
  generated-file exclusion and delivery impact; no unresolved actionable findings.

No production website, application UI, account metrics, field Core Web Vitals or
external AI-answer visibility was audited. Actual Apple Design verification of
an interface occurs when that interface exists. Browser smoke evidence is Windows
only; other operating systems and hosted CI are unverified until observed.
The next product priority remains item 2: website scope and stack. No merge or
deployment is part of this task.

## PR #3 upstream integration — 2026-09-08

Resolved [PR #3](https://github.com/brollysolutions/patnampakodi-site/pull/3)
against upstream `6b2fc7a`, the merged PR #2, on `fix/workflow-audit`.
Preserved explicit task-file selection and outgoing-history checks together with
the OS delivery lock, Git failure checks, and fresh remote PR verification.
Reconciled both contributors' implementation records and removed stale staging
instructions from the ship skill and partner/reference guides.

- The combined suite initially failed because two sets of test fixtures assumed
  the previous delivery interface. Corrected the fixtures without weakening the
  safeguards and added a selected-file delivery test with fresh PR evidence.
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1 --ci`:
  exit 0; **90 tests passed** on Windows/Python 3.13, **18 identical shared skills**,
  configuration validation, and shell syntax checks.
- Security and PR self-review covered the merged delivery engine, lock and remote
  failure paths, staging/history guards, fixtures, and mirrored guidance; no
  unresolved integration findings. No dependencies or integration permissions changed.
- Evidence in the older sections below is historical; their test counts describe
  the original separate deliveries. Current CI/remote state is recorded on PR #3.

No application, API, database, browser, or migration layer exists. The next
product priority is still item 2, website scope and stack. PR merging remains a
separate user decision; this task updates only the contributor branch and PR.

## Astra workflow adoption — 2026-09-07

Merged in [PR #2](https://github.com/brollysolutions/patnampakodi-site/pull/2)
from `chore/astra-workflow`. The evidence below records the original delivery,
before the PR #3 integration. Initial implementation `c286031`; the helper returned
exit 0 with fresh GitHub state OPEN and head SHA matching local HEAD and the
pushed `origin` branch. The original setup PR #1 is merged. Application work
remains unconfigured; next product priority is website scope and stack selection.

| Requirement | Status | Fresh evidence |
| --- | --- | --- |
| Astra guidance adapted to this checkout | Verified by diff review | `AGENTS.md`, `astra-workflow-reference.md`, partner guide; no model/config changes |
| Shared skills stay identical | Verified | Validation: 16 matching skills; narrow ship/work-feature/diagnosis updates in both trees |
| One delivery process per clone and its worktrees | Verified on Windows | Separate-process contention, shared Git directory, and crash-release tests |
| Current remote PR identity and head evidence | Regression tests and live delivery passed | Open/closed/merged PRs, wrong repo/branches/SHA, invalid metadata/URL, network timeout/failure; helper verified PR #2 against `c286031` |
| Failed Git/local evidence cannot claim success | Verified | Status/tracking failure and dirty/wrong-tracking finish tests |
| Existing workflow behavior | Verified | Full gate: 77 tests, configuration/parity and shell syntax checks |

Commands from the original PR #2 delivery:

- `uv --cache-dir .uv-cache run --no-project python -m unittest discover -s scripts/tests -p test_workflow_delivery.py -v`: 17 passed on the approved rerun. The initial sandboxed run failed because Windows denied temporary directories; it was not counted as passing.
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1 --ci`: passed, 77 tests; its terminal command result was collected (exit 0).
- `git diff --check`: passed. Private `.agent-workflow/` notes remain ignored.
- Security and PR self-review: no unresolved actionable findings in the changed delivery engine, adjacent hooks, tests, skills, and documentation. No dependencies, CI permissions, credentials, or integrations added.
- The optional system skill-creator `quick_validate.py .agents/skills/ship` could not run: PyYAML is absent. No dependency was added. Repository validation passed, and all three edited skill frontmatters match the validated base.

Limits: GitHub reported no CI results during initial PR readback, so Linux
execution remains unverified. The finish lock coordinates this helper,
not unrelated editors/Git commands. Remote PR evidence is a point-in-time read;
network/auth failures remain unverified. Live client hook loading is not proven
by terminal tests. No application/API/database/browser/SEO/migration gates apply.

## Shared workflow — 2026-09-07

Merged in [PR #1](https://github.com/brollysolutions/patnampakodi-site/pull/1) on 2026-09-07,
branch `chore/shared-agent-workflow`. Initial implementation `e239ce0` plus the
delivery fixes in the same PR. The table and verification below are historical
evidence from that delivery; the audit section records current verification.

| Requirement | Status | Evidence |
| --- | --- | --- |
| Shared Codex and Claude Code instructions/skills | Verified | `AGENTS.md`; validation passes with 16 identical skills |
| Per-clone setup and private templates | Verified | PowerShell then Git Bash setup in a fresh clone; notes preserved; clean status |
| Local Git and agent lifecycle hooks | Verified by terminal smoke tests | Both shims; protected edit/secret-read denial; automatic branch; stop checks; real Git hooks reject protected commits/pushes |
| Workflow verification and PR policy CI | Fork workflow CI passed; PR checks reported by GitHub | [Run 34091277143](https://github.com/vamshisaideep9/patnampakodi-site/actions/runs/34091277143); `.github/workflows/` |
| Partner explanation and installation guide | Complete | `docs/partner-workflow-guide.md`, linked from `README.md` |
| GitHub publication | Merged 2026-09-07 | [PR #1](https://github.com/brollysolutions/patnampakodi-site/pull/1); merge status read back from GitHub during the audit |

## Workflow audit and design additions — 2026-09-08

Delivered in [PR #3](https://github.com/brollysolutions/patnampakodi-site/pull/3),
initial implementation `90574b6`, branch `fix/workflow-audit` pushed to the user's
fork and targeting shared `main`. Confirmed findings, mitigations, and remaining
limits are in `workflow-audit.md`. Research and pinned installation sources are
in `design-skills.md`.

- Original 59-test suite passed; new regressions reproduced the identified gaps.
- Expanded **71 tests** pass under Python 3.13, including actual configured Bash
  and PowerShell hook commands invoked from a subdirectory.
- PowerShell and Bash setup passed and enabled `.githooks`; a hash comparison
  confirmed repeated setup preserved private notes. Templates remained ignored.
  uv and Python 3.13 were installed locally. The real pre-push gate also passed.
- **18 matching shared skills** validate. Taste and Anthropic entrypoints also
  pass the system skill validator. Apple Design is installed locally for Codex
  and Claude Code, outside the shared repository.
- CI now runs for branch pushes and provisions Python 3.11/3.13 on Ubuntu/Windows.
  All four jobs passed for `90574b6` in
  [fork run 34197977296](https://github.com/tejalsharma2023/patnampakodi-site/actions/runs/34197977296).
  PR #3 is open. At this readback, GitHub reported no upstream PR checks or
  upstream branch workflow runs; fork success is not presented as upstream approval.

Next priority remains item 2: agree website scope, content, and stack. These
design references do not choose or install a website framework.

## Original setup verification — 2026-09-07

- PowerShell `scripts/setup-agent-workflow.ps1`: passed.
- Git Bash `bash scripts/verify.sh --ci`: passed, **59 tests**, 16 matching skills,
  and shell syntax checks. Tests cover note preservation, setup/staging failures,
  failed PR lookup, and the first modified path's secret detection.
- Fresh staged-file snapshot cloned to a temporary directory: PowerShell and
  repeated Bash setup passed; private notes stayed ignored; real hook checks passed.
- `git diff --cached --check` and staged feature tracking: passed.

The first sandboxed test attempt failed because Windows denied temporary
directories; the approved rerun passed. Fresh-clone testing found and resolved a
template ignore rule and Git Bash discovery issue before publication.
The first push was blocked by the pre-push gate because Git's internal executable
path differed from its terminal path. Discovery now covers that location with a
regression test; the subsequent pre-push gate and publication both passed.
Repeated delivery now queries the exact fork head/base through the GitHub API;
the original CLI filter missed the existing PR. GitHub refused the duplicate
attempt, and the corrected lookup is covered by a regression test.

## Limits and next priority

Website, API, migrations, generated contracts, browser journeys, Lighthouse,
deployed SEO, and deployment are not applicable: no application exists yet.
Next priority: agree website scope, content, and stack before scaffolding it.

External plugins/MCP servers are not enabled. Each user must authenticate their
own tools and review/trust hooks in a fresh client session. Scripted validation
does not prove live client hooks have loaded. Branch protection/rulesets were
not changed. Hook parsing and sensitive-filename checks are limited guards;
see `SECURITY.md` and the partner guide.
