# Implementation plan

## Shared Nginx deployment and packaging - 2026-09-12

| Item | Status | Planning model / effort | Implementation model / effort |
| --- | --- | --- | --- |
| 23. Deploy behind host Nginx and exclude AI workflows from builds | Implemented and verified in PR #20; live host acceptance unverified | `gpt-6-astra` / High recommended for deployment/proxy work | `gpt-6-astra` / High recommended; selected settings preserved |

Exclude Codex/Claude configuration, agent skills and instructions, MCP settings,
Git/CI hooks and repository workflow tooling from Docker build contexts. Preserve
required web/API build inputs and development workflows in Git. Verify Docker's
actual ignore behavior with synthetic files. This does not delete files from a
server Git checkout. Server diagnostics identify host Nginx on 80/443 and an
existing enabled `patnampakodi` site with Certbot certificate paths. Preserve
those host settings and other sites. Add a persisted host-Nginx mode that replaces
public Docker port bindings with loopback 3502, retains API trust in the internal
Caddy address, and trusts forwarded client addresses only from the bridge gateway.
Verify route handling, header spoof rejection, Compose merge behavior, port and
version guards, and existing-network compatibility. Host edits, certificate
validity and public TLS acceptance require server-side evidence.

Fresh verification: 38 deployment tests pass in the pinned Linux container.
The workflow-only gate passes 150 tests with three Linux-only skips, 22-skill
validation and shell checks. Ruff check/format passes. A real Docker context
build excludes 39 synthetic workflow/cache files and retains 15 required app
inputs. Standalone Compose renders exactly one loopback proxy binding with
private app/data services, the selected Caddyfile and unchanged API trust.
The pinned Caddy image validates its configuration, and a disposable network
test passes API prefix stripping, web routing, pinned HTTPS/host headers,
trusted client forwarding and untrusted forwarded-address rejection. Its
containers/network are removed afterward. Review found no unresolved defect.

Public HTTPS timed out locally; sandbox DNS/network probes also failed. Pulling
the official Nginx test image failed on Docker registry DNS, so actual Nginx
syntax/runtime and host certificate acceptance remain unverified. The Caddy
test simulates the trusted upstream address; it does not run host Nginx.
Full browser/Lighthouse and live deployment are not claimed. Next priority:
review the existing site's routing, merge the PR, deploy with `--behind-nginx`,
then validate/reload only the reviewed Nginx site integration. Development
workflows remain tracked; only deployment build contexts/images exclude them.

The delivery helper returned exit 0 and verified implementation commit `d858ef0`
in open [PR #20](https://github.com/brollysolutions/patnampakodi-site/pull/20),
from the contributor's `feat/docker-staging` to upstream `main`, with matching
remote head and a clean worktree. Mandatory commit/fast push gates passed.
Final header comparison found that the internal mode also needed the original
HSTS response header. A new proxy assertion failed before restoring that header;
the follow-up retains `max-age=31536000` for both API and web responses.
The final disposable proxy run returned exit 0 with the HSTS assertion, trusted
and untrusted clients, path handling and HTTPS/host headers all passing. Ruff
and diff checks pass. Final review leaves no unresolved code finding; host
Nginx/TLS acceptance remains separate from the simulated upstream fixture.

## Modern standalone Compose compatibility - 2026-09-12

| Item | Status | Planning model / effort | Implementation model / effort |
| --- | --- | --- | --- |
| 22. Accept modern `docker-compose` in server deployment | Implemented; verified and delivered in PR #19, server acceptance unverified | `gpt-6-astra` / Medium recommended | `gpt-6-astra` / Medium recommended; selected settings preserved |

Accept a working `docker compose` plugin or modern `docker-compose` executable
(including the server's v5.1.2), requiring version 2.20.0 or newer. Select once
before deployment mutations and reuse that command for every Compose operation.
Verify preference, fallback, unsupported/missing versions, command propagation
and retained local-engine checks. No package installation, dependency, application,
schema, credential, network or data-policy changes. Delivery follows review and
fresh targeted/workflow verification; server acceptance remains separate.

Fresh evidence: 32/32 deployment tests pass in the pinned Linux Python container;
Windows passes with three Linux-only skips. The workflow-only gate passes 144
tests with three skips, 22-skill validation and shell checks. Ruff check/format
passes, and the actual local standalone Compose v5.4.0 renders the production
configuration through the helper with synthetic options. v5.1.2 selection is
covered by regression fixtures; deployment on the user's server is unverified.
The initial Windows test attempt was blocked by sandbox temporary-file access;
the approved rerun passed. Code review found no outstanding defect; command
arguments remain separate from the shell, and project/environment/local-engine
guards are retained. No full application/browser/Lighthouse run is claimed for
this CLI-only change. Next priority: merge the compatibility PR and retry setup
on the prepared server. Delivery continues on `feat/docker-staging` after PR #18.

The delivery helper returned exit 0 and verified implementation commit `d8c6e67`
in open [PR #19](https://github.com/brollysolutions/patnampakodi-site/pull/19),
from the contributor's `feat/docker-staging` to upstream `main`. Mandatory commit
checks and the fast application push gate passed; the remote head matched and
the worktree was clean. This documentation follow-up records that readback.

## One-command server deployment - 2026-09-12

| Item | Status | Planning model / effort | Implementation model / effort |
| --- | --- | --- | --- |
| 21. Provide one command for server setup and updates | Implemented; targeted verification passed, server acceptance unverified | `gpt-6-astra` / High recommended | `gpt-6-astra` / High recommended; selected settings preserved |

Provide `sudo python3 scripts/deploy.py` for the Linux Docker server, defaulting
to the owner's `patnampakodi.com`. Acceptance: create missing non-secret runtime
options, check Compose before mutations, generate restricted first-install
credentials only when no deployment data exists, avoid conflicting new subnets,
preserve existing configuration and volumes, bootstrap only an empty database,
and stop on failed setup or migrations. Existing deployments require a confirmed
backup before service/database changes. Serialize deployments and test failure/retry paths with
synthetic fixtures. No automatic Docker installation, DNS change, provider
activation, secret rotation, volume deletion or live-host acceptance claim.
Application routes, schemas, contracts and UI are outside this change.

The helper creates/reuses ignored runtime options without requiring manual
Compose flags. For a new network it replaces an overlapping configured prefix
with an available private candidate and persists it; an existing Pakodi subnet
is never silently changed. Checks cover Compose/local-engine availability,
IPv4/IPv6 web-port conflicts, restricted core credential generation and reuse,
role/Redis authentication, bootstrap versus migration, preserving seed behavior,
failure propagation, first-admin prompts, and deployment lock/permissions.

Fresh verification: all 26 deployment cases pass in a Linux container; the
Windows workflow gate runs 138 tests with three Linux-specific skips and passes
22-skill validation and shell checks. Ruff and production Compose rendering
pass. The full CI attempt passes all 112 API tests, migration/contract parity,
web lint/format/types, 27 units and the production build. Its additional browser
run was intentionally stopped after 22 passing desktop tests (command exit 1);
remaining browser/technical SEO/Lighthouse checks are unverified, not a full
release pass. Security and code review find no unresolved defect. The branch
continues `feat/docker-staging` after merged PR #17; delivery targets upstream
`main`. Next priority is the prepared Linux server's setup and host/provider
acceptance, including shared-proxy integration if another server owns 80/443.

A separate uniquely named Docker fixture passes actual backend fresh setup and
a second deployment with generated credentials: role bootstrap, restricted
logins, Redis authentication, migration, seed, API health, worker startup and
admin creation. Edited content, the admin count and secret hashes survive the
second deployment. Only fixture-owned volumes are removed afterward. This
check reuses the reviewed API image and excludes web/proxy/public TLS.

Final review reproduced a blank-prefix persistence defect: the first run chose
a free range but left an existing empty runtime entry unchanged. The regression
failed against `90b40d6`; the correction saves that chosen range and preserves
it on retry. The interrupted initial delivery left that implementation commit
local only; process inspection and GitHub readback confirmed it was no longer
running and the remote still held `594dc2f` before delivery resumed. Its missing
terminal result is unverified, not a successful push.

Delivery resumed successfully: the helper returned exit 0, pushed implementation
head `0476c4b`, and verified open
[PR #18](https://github.com/brollysolutions/patnampakodi-site/pull/18) from the
contributor's `feat/docker-staging` to shared `main`, with matching remote head
and a clean worktree. The mandatory fast push gate passed. This documentation
follow-up records that observed delivery; current remote state is read again
after publication. Live server and full browser/Lighthouse acceptance remain
outside the verified outcome above.

## Production Docker network overlap - 2026-09-12

| Item | Status | Planning model / effort | Implementation model / effort |
| --- | --- | --- | --- |
| 20. Allow a deployment-specific private Docker subnet | Implemented; local configuration/runtime checks pass, server rollout unverified | `gpt-6-astra` / High recommended | `gpt-6-astra` / High recommended; selected settings preserved |

The deployment server rejects `pakodi_private` because its fixed subnet overlaps
an existing Docker pool. Add one non-secret IPv4 prefix option deriving the /24,
Caddy's .10 address and the API's exact trusted proxy together. Preserve the
default for existing deployments. Acceptance: default, blank and custom options
render consistently; disposable Docker checks reproduce overlapping allocation
and verify a free alternative with the fixed proxy address. Keep data-service
ports private and volumes intact. Non-goals: remote host access, secret edits,
network pruning, application/API/schema/UI changes or a live deployment claim.
Regression: the custom-prefix rendering assertion fails against the original
Compose file because the subnet stays at `172.29.91.0/24`.

The operator's network inventory confirms `brollyjuniors_default` owns
`172.29.0.0/16`, which contains Pakodi's default /24. `10.253.91.0/24` avoids all
listed Docker ranges and the operator's subsequently supplied host/VPC routes.
Default, blank and custom Compose rendering pass. A disposable local check
reproduces Docker's overlap error, then allocates a free alternative and runs the
proxy image at the exact trusted IP. PostgreSQL/Redis authentication, private
ports and restart persistence pass; 112 workflow tests, 22-skill parity, shell
checks and verifier Ruff pass. Security/PR review finds no actionable defect.
Application handlers, generated contracts, schema and UI are outside this change;
browser/SEO/Lighthouse and live deployment are not claimed as verified.

Delivery continues `feat/docker-staging` against upstream `main` after merged
PR #16. Commit `6b04233` is pushed in open
[PR #17](https://github.com/brollysolutions/patnampakodi-site/pull/17), with the
remote head verified at that commit. The initial push failed when local test
fixtures were stopped; after starting them, all 112 API tests and the required
fast push gate passed, including web lint/format/types, units and production build.
The fast gate skips browser/performance/live SEO; no full release claim is made.
Next priority: persist `PAKODI_NETWORK_PREFIX=10.253.91` in the server's non-secret
runtime options and retry deployment without removing other networks.

## Production PostgreSQL and Redis ports - 2026-09-12

| Item | Status | Planning model / effort | Implementation model / effort |
| --- | --- | --- | --- |
| 19. Use PostgreSQL 5433 and Redis 6380 in production | Implemented; disposable runtime checks pass, live deployment unverified | `gpt-6-astra` / High recommended | `gpt-6-astra` / High recommended; selected settings preserved |

Pin production PostgreSQL to 5433 and Redis to 6380 on the Docker network, align
PostgreSQL health/CLI defaults and document all operator-managed connection URL
files. Keep only Caddy 80/443 public. Acceptance: rendered production commands
start the new listeners; authenticated TCP clients connect; old listener ports
are closed; PostgreSQL health passes; synthetic records survive restart; neither
data service has host port bindings. Verify with disposable Docker containers and
the applicable workflow/application gates, then security review and PR delivery.
Non-goals: local development/staging port changes, public database exposure,
schema/API/UI changes, credential rotation or accessing/deploying a live host.
Rollout risk: server ports and all four connection files must change together;
retain volumes and use a maintenance window. PR #15 is merged; this follow-up
continues the instructed `feat/docker-staging` branch with a new upstream PR.

Fresh verification: the rendered production configuration passes isolated Docker
checks for PostgreSQL 5433 health/TCP/CLI connections, Redis 6380 authentication
and legacy-config override, closed old ports, no published data-service ports,
and PostgreSQL/Redis data preservation across restart. All 112 workflow tests,
22-skill parity and the new verifier's Ruff check pass. No application source,
contracts, schema or public assets change; browser/SEO/Lighthouse are not rerun
for this deployment-only adjustment. Existing public performance acceptance is
still open. Next priority: coordinate the operator's connection-file update and
DigitalOcean release acceptance; no production files or host were accessed.

Delivered implementation commit `5d6cb14` in
[PR #16](https://github.com/brollysolutions/patnampakodi-site/pull/16), from
`feat/docker-staging` to upstream `main`; fresh remote readback confirms the open
PR at that commit. The required pre-push fast gate also passes API/RLS tests,
one migration head, generated-contract parity, web lint/format/types, unit tests
and the production build. That gate skips browser/performance/live SEO checks;
it is not full release acceptance. This documentation follow-up records the
verified delivery without changing runtime behavior.

## Saved product visibility and CRUD - 2026-09-11

| Item | Status | Planning model / effort | Implementation model / effort |
| --- | --- | --- | --- |
| 18. Make saved products visible and complete product CRUD | Implemented; functional checks pass, public performance acceptance remains open | `gpt-6-astra` / High recommended | `gpt-6-astra` / High recommended; Extra High final deletion review; selected settings preserved |

The saved product exists in local staging; its catalogue is below the large
menu-preparation panel. Put saved products first, add name/SKU
search and publication/range filters with pagination, preserve create/edit and
stock controls, and collapse menu suggestions and CSV tools. Use the existing
fonts, palette and form controls, with explicit empty/loading/error states and
keyboard focus after selecting a product. No added animation or dependency.
The user's follow-up also requires an information button beside every field in
the product editor, with concise field-specific help usable by keyboard/touch.

Complete deletion through the authenticated API and browser proxy. Delete only
products with no order references or reservations, after UI confirmation; keep
order/audit history and attached media. Use the normal RLS transaction, serialize
deletion with edits/checkout, and add only the required variant DELETE privilege
through an additive migration. The delete operation unpublishes its content record.
Products with order history remain editable and can be unpublished.

Acceptance: saved published and draft products appear immediately; search and
pagination find existing products; create/read/update/delete survive reload;
deletion rejects unauthenticated, cross-origin, bad-CSRF, other-brand and ordered/
reserved products; concurrent edits cannot recreate a deleted ID. Verify API,
migration/contracts, browser CRUD/axe/reflow and the applicable full gate.
Non-goals: changing the user's product values/stock/publication, inventing sale
data, changing order/payment behavior, or changing the existing origin policy.
PR #14 is merged; create a new upstream PR for this follow-up on the instructed
`feat/docker-staging` branch. Existing performance acceptance remains open.

Fresh functional acceptance on 12 September passes 112 API tests (eight new),
112 workflow tests, 27 web units, one migration head, generated contracts,
lint/format/types and production builds. All six admin browser journeys pass
after correcting exact-label and renamed-notice expectations; the initial broad
run retains its 58 passes, two intentional skips and six failed assertions.
CRUD/reload, all field help, publication synchronization, axe and 320px reflow
are covered. Technical SEO passes 13 routes. Local staging is refreshed and
healthy; a read-only digest confirms the saved product is unchanged. Container
migration/seed, runtime/private headers, worker and local Caddy HTTPS checks pass.
All 18 Lighthouse reports complete, but speed budgets fail: home/menu/contact
performance medians are mobile 57/66/73 and desktop 89/94/83. Accessibility,
best-practices and SEO score 100. Keep the PR in draft while that acceptance is
open. [PR #15](https://github.com/brollysolutions/patnampakodi-site/pull/15)
delivers the contributor's `feat/docker-staging` branch against upstream `main`,
following merged PR #14. Commit `b923765` contains the implementation; the
commit/push hooks passed. Next priority: meet public speed budgets
and complete operator-approved inventory and live-provider launch acceptance.

## Local PostgreSQL port and password-only admin sign-in - 2026-09-11

| Item | Status | Planning model / effort | Implementation model / effort |
| --- | --- | --- | --- |
| 17. Move local PostgreSQL to available port 5434 and use password-only admin sign-in | Implemented; authentication and port checks pass, performance acceptance remains open | `gpt-6-astra` / Extra High recommended | `gpt-6-astra` / Extra High recommended; selected settings preserved |

Change only the loopback PostgreSQL mapping and the local URLs that consume it:
`127.0.0.1:5434` maps to the existing container port `5432`. The user authorized
an alternative because another project owns 5433. Production remains
private at `postgres:5432`; it must not publish PostgreSQL. Simplify admin sign-in
to username and password only, while retaining Argon2 password verification,
per-IP/per-username rate limits, server-side sessions, CSRF checks, strict cookies,
account disablement, session revocation on password reset, audit logging and RLS.
The legacy migration is immutable, so unused TOTP/recovery columns remain for
compatibility rather than being rewritten or exposed.

Acceptance: local development and verification connect through port 5434; no
active source still directs local PostgreSQL clients to 55450; the API contract and
admin form accept only username/password; password resets revoke sessions; and
anonymous, invalid-password, CSRF and cross-origin requests remain denied.
Non-goals: changing the in-container PostgreSQL port, publishing PostgreSQL in
production, changing customer/order authentication, or altering financial flows.
Fresh verification passes 112 workflow tests, 104 API tests, contract generation,
one migration head, web lint/format/types, 27 unit tests and the production build.
The broad browser run has 60 passes and two intentional skips; its one checkout
navigation timeout passes an unchanged focused rerun. All three admin/axe journeys
and 13 technical SEO routes pass. Container smoke and Caddy HTTPS checks pass;
the 18-report Lighthouse audit fails unchanged speed budgets (mobile medians
54/58/70, desktop 92/92/85 for home/menu/contact). Accessibility, best practices
and SEO score 100. Keep delivery in draft while performance acceptance remains
open. Docker staging passes two browser tests and five database invariants; its
optional presentation prompt ends with EOF after successful acceptance. Persistent
preview refresh and four-width login accessibility/keyboard/error checks pass.
The user-requested local account is provisioned and its login/session/logout are
verified without storing credentials in repository artifacts. Next priority is
performance acceptance and approved launch data from item 16.
Delivery: [draft PR #14](https://github.com/brollysolutions/patnampakodi-site/pull/14),
from `vamshisaideep9:feat/docker-staging` to `brollysolutions:main`. Commit/push/PR
delivery and the required pre-push gate exit 0; remote head readback is verified.
PR #13 is already merged. Performance acceptance remains open.

## Port migration and food catalogue preparation - 2026-09-11

| Item | Status | Planning model / effort | Implementation model / effort |
| --- | --- | --- | --- |
| 16. Move local services to new ports and prepare the complete food catalogue | Implemented and locally verified; sales activation awaits approved data | `gpt-6-astra` / High recommended | `gpt-6-astra` / High recommended; selected settings preserved |

The user requests new ports, including 8500 and 3500, and all referenced foods
and flavours for a planned launch today. Continue on the instructed
`feat/docker-staging` branch and update [PR #13](https://github.com/brollysolutions/patnampakodi-site/pull/13).
Use Docker website 3500, native web 3501, API 8500, browser fixtures 3510/8510,
local PostgreSQL 55450 and Redis 6450. Align server URLs, Origin checks, health
checks, containers, test runners and current setup documentation. Preserve
loopback bindings, private Docker networks, existing volumes and other projects.
Database/Redis container protocol ports and public production HTTP/TLS ports
remain standard; dynamic disposable ports remain allocated by the fixture.

Catalogue scope: 51 saved menu items reconciled with the seven original product
URLs yield 57 distinct entries: 53 fresh foods and four ready-mix flavours. The
Pachi Mirchi menu flavour retains its original product URL. Reuse recorded names,
categories and images through an authenticated admin setup endpoint and searchable
Products list; existing variant records and stock must never be overwritten.
Launch prices, portions/pack sizes, stock and complete food/tax details are not
present in the saved sources; the user has been asked for those inputs. Prepare
the catalogue without inventing those business facts or changing publication,
payment or stock safeguards. No live deployment or provider activation is included.

Acceptance: the preview loads on 3500, service and fixture URLs agree, no previous
fixed local ports remain in active configuration, and source foods are ready for
completion/publication using confirmed information. Verify workflow/port guards,
API and generated contracts, browser/SEO, Docker checkout and retained data.
Performance acceptance from item 15 remains open and PR #13 stays draft.

Implementation evidence: 111 workflow tests, 97 API tests, five catalogue
regressions after image curation, one migration head and fresh contracts pass.
Web lint/format/types, 27 units and production build pass. The broad browser run
passes 58 checks and skips two duplicate reflow projects; its three admin failures
are the same dietary-select test locator. The semantic combobox correction passes
all three affected admin/axe journeys. Technical SEO passes 13 routes. Source-photo
review restricts automatic product artwork to the seven product-specific records;
other prepared foods use neutral icons. Docker smoke and Caddy routing pass;
18 Lighthouse reports complete with accessibility/best-practices/SEO 100, while
the unchanged speed budgets fail on mobile and home desktop (see feature-status).
Both disposable Docker acceptance tests and all five database invariants pass;
the presentation fixture is cleaned up successfully. Manual review covers the
setup list and product form at 1440, 768, 390 and 320px, range/name filtering,
focus, sticky navigation and saving a synthetic unpublished product. Its stock
remains zero, existing stock is unchanged, and the setup count falls from 57 to 56.
The persistent preview is refreshed to port 3500 with web image `3838f013` and
API image `aa6670ac`, preserving all four named volumes. Home, admin and the
storefront API return 200 with noindex; the old port 3100 is no longer listening.
No synthetic sale or admin records were inserted into the persistent preview.
Native Safari, physical devices and manual browser zoom remain unverified.
Delivery is through draft PR #13; final remote readback accompanies the handoff.
Live business/provider/hosting and performance acceptance remain the next release
priorities. See the updated [client presentation guide](../client-presentation.md).

## Classic ecommerce redesign - 2026-09-11

| Item | Status | Planning model / effort | Implementation model / effort |
| --- | --- | --- | --- |
| 15. Classic storefront, immediate checkout and pilot fresh ordering | Implemented; functional acceptance passes; draft for performance | `gpt-6-astra` / Extra High recommended | `gpt-6-astra` / Extra High recommended; selected settings preserved |

The user approved [the complete redesign](commerce-redesign-plan.md) and asked
for implementation and a client presentation guide. Continue on the explicitly
instructed `feat/docker-staging` branch. PR #12 was merged at fdf22ab; its
historical draft/performance evidence below remains evidence, not current PR state.
New acceptance: original identity, every public/admin surface, independent fresh
and packaged carts, device favourites, PIN-based immediate checkout, one pilot
outlet, preparation/cancellation serialization, and a repeatable client walkthrough.
Reuse existing assets; built-in image generation only for a demonstrated gap.
Later user correction removes website content management from the admin panel;
Orders, Products, Enquiries, Messages, Reports, Delivery, Settings and Media remain.
This bounded correction recommends gpt-6-astra / Medium for planning and
implementation; the selected session settings remain unchanged.
The follow-up requests a better admin dashboard and sticky navigation. Extend this
same item with a compact dedicated admin header, desktop sidebar/mobile tabs,
clear section descriptions, readable order cards and current-view status counts.
Make storefront navigation sticky too, with focus/anchor clearance. Planning and
implementation recommendation for this UI pass: gpt-6-astra / High. Acceptance:
all eight operational sections remain accessible, Content is absent, navigation
stays reachable while scrolling and keyboard focus reveals the selected section.
Use existing tokens/icons, instant navigation and no new dependencies or data APIs.
Preserve historical orders, private links, RLS, durable payment/refund invariants,
SEO URLs and quality budgets. Live business inputs and deployment remain separate.
Verification: API/security/concurrency, generated contracts, web units/build,
responsive browser/axe/SEO, Docker commerce recovery, and Lighthouse. Interim checks:
95 API tests, one migration head, regenerated contracts, 27 web units and production
build pass. The broad admin-refinement run passed 58 browser checks, with three
failures and two duplicate reflow skips. Corrected the mobile grid's minimum
width and skip-link stacking; a fresh rebuilt run of all 12 affected admin,
staff-approval, sticky-header and keyboard checks passes across desktop/mobile/
tablet. Technical SEO passes 13 routes with the documented skip-link warnings.
The 320px/720px CSS-width sweep covers reflow, not manual browser zoom. Final review
adds an admin-only preparation cancellation: refund the remaining balance once,
keep customer cancellation blocked and do not restock food being prepared. The
95-test API run covers concurrent retries, CSRF and stock/refund preservation.
The final error callback refreshes server data before retrying. Both Docker
acceptance tests and five SQL invariants pass, covering checkout/recovery/refund,
missing photos and an actual public API outage with a successful retry. The
disposable presentation also verifies fresh payment, preparation, blocked customer
cancellation, staff cancellation and completed refund. The last admin navigation
correction passes separate frontend and browser verification. The final Docker
rebuild passes both acceptance tests and all five SQL invariants; its disposable
project was cleaned up successfully. Manual review covers all eight admin sections
and 320px, 390px, 768px and 1440px layouts. The persistent preview at port 3100 is
refreshed to web image `a84155fb` and API image `689efa6d`, preserving its data.
Container smoke checks pass. Lighthouse completes all 18 reports without another
Contact HTTP 500; accessibility/best-practices/SEO score 100 throughout, but mobile
and home-desktop speed fail the unchanged budgets (details in feature-status.md).
The measured image precedes the final retry callback, staff-cancellation and
admin navigation changes.
Review target: `vamshisaideep9:feat/docker-staging` to upstream `main`, in draft;
[current branch PR lookup](https://github.com/brollysolutions/patnampakodi-site/pulls?q=is%3Aopen+is%3Apr+head%3Afeat%2Fdocker-staging).
The [client presentation guide](../client-presentation.md) provides the repeatable
demo and ten-minute walkthrough. Next priority: final-head CI/performance
acceptance and approved business/provider/hosting inputs. No merge or live deployment.

## Original identity and ordering access - 2026-09-11

User correction: keep the original site's colors and fonts and provide the full
ecommerce journey. This supersedes the previous replacement-brand styling.

| Item | Status | Planning model / effort | Implementation model / effort |
| --- | --- | --- | --- |
| 14. Restore original identity and verify ordering access | Implemented; functional acceptance passes; draft for performance/HTTP 500 acceptance | `gpt-6-astra` / High recommended | `gpt-6-astra` / High recommended; Extra High security review; selected settings unchanged |

Acceptance: locally served original Poppins body/editorial typography and Inter
commerce headings; observed peach, dark, orange, red and gold palette; visible
Shop and Cart navigation at mobile and desktop sizes; existing catalog, guest
request, staff quote, payment, tracking and admin journeys pass fresh checks.
Keep public URLs, server content, accessibility and performance budgets intact.
No invented sellable products, shipping prices or seller/tax details. Immediate
checkout is an open user question; retain the approved staff quote flow until
resolved. Live providers and production deployment require separate acceptance.
Review the font package provenance/license and lockfile; verify browser/axe,
technical SEO, full application gate and disposable Docker order acceptance.
Fresh evidence: 110 workflow tests, 86 API tests, 20 web units, 54 browser/axe
tests, 13 technical SEO routes, production build and container smoke pass.
Final Docker checkout/capture/replay/restart/invoice/delivery/refund/message
acceptance passes; six final preview identity/dialog checks and fallback heading
contrast pass. Local preview is refreshed at port 3100 with no test catalog/admin
insertions. Ten repeated contact requests return HTTP 200 and retain noindex.
Lighthouse failed timing budgets, then stopped on a contact HTTP 500; the full
gate is not passed. See feature-status.md for exact results and limitations.

Review target: `vamshisaideep9:feat/docker-staging` to upstream `main`, kept in
draft; [current branch PR lookup](https://github.com/brollysolutions/patnampakodi-site/pulls?q=is%3Aopen+is%3Apr+head%3Afeat%2Fdocker-staging).
No merge or production deployment. Next priority: resolve performance and HTTP
500 acceptance, receive approved catalog/seller/provider inputs and settle the
open immediate-checkout question. Functional verification does not enable live
sales or waive those release prerequisites.

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


CI correction: chrome-launcher 1.2.1 implicitly disabled the Linux SUID sandbox. Lighthouse now supplies every pinned default explicitly while avoiding that implicit flag, so the installed companion helper can be used. The regression reproduces the old Linux flags and verifies retained sandbox/defaults. No budgets or throttling changed; new Linux runtime/performance acceptance is pending.


Update this file and `feature-status.md` with product/workflow script changes.
Record one in-progress item per task branch; independent contributors may each
have a different task branch. Preserve the other contributor's records when
resolving a conflict. Use the selected model; do not switch or delegate silently.

## Approved four-PR delivery

The admin/staging verification now exercises an exact consumed TOTP across a
controlled clock boundary; the old test incorrectly expected a fresh code to be
a replay. Auth behavior is unchanged. Three rendering experiments did not show consistent
improvement and were rejected; no experimental UI change is retained. Linux
mobile timing acceptance remains pending on the corrected commits.

Admin CI now passes sandbox launch and functional checks. Run 34535340526
fails mobile timing budgets; failed-run CPU/script/layout diagnostics are added
to identify the remaining cause. No thresholds or throttling change.

Admin delivery also closes the proven commit-before-response race and restores
keyboard access to horizontally scrolling reports. Ubuntu Lighthouse now has
diagnostics, the pinned Chromium companion SUID helper and a launch configuration
that preserves its sandbox. Linux runtime/performance verification passes for PRs #8 and #9;
PR #10 passes functional checks but still fails mobile timing budgets. Staging uses a web-only entry bridge and an internal backend
network; page metadata follows the existing deployment indexing policy.

Target: local Docker staging by **11 September 2026, 23:59 IST**. Preserve the
live site's copy, images, layout and permanent URLs with our existing Abril
Fatface/Archivo fonts and orange/brown/cream palette. Each PR includes its own
verification, review and delivery records. Human review controls merging.

1. **Public website and enquiries (item 10).** Reproduce all seven public entry
   pages, original assets, footer, FAQs and testimonials; retain search and outlet
   discovery; store phone-only enquiries once on retries; expose an approved PDF
   download when configured; make copied content editable through admin.
2. **Customer ecommerce (item 11).** Preserve original product/category/tag URLs;
   add product search, categories and sorting; verify catalog, cart, guest request,
   staff quote, private payment, expiry, cancellation, invoice and tracking flows.
   Keep incomplete products unpublished and server-authoritative price/stock rules.
3. **Admin completion (item 12).** Complete lead enrichment and safe enquiry CSV,
   dated sales summaries, product/content/media management and existing order,
   stock, fulfilment, refund, GST and messaging controls. Verify TOTP, CSRF, RLS,
   audit trails and customer-data access on each affected path.
4. **Docker staging acceptance (item 13).** Provide repeatable local startup and
   provider fixtures, verify complete customer/admin journeys and durable recovery,
   run synthetic backup/restore plus full browser/SEO/container/performance gates,
   and document exact operator steps and outstanding real-business inputs.

Only approved real business data may populate staging. Product food information,
seller/tax details, policies and brochure remain required inputs; neither source
prices alone nor automated-test fixtures authorize publication. Test fixtures use
isolated disposable databases. Live money movement, customer messaging, production
deployment, courier integration and customer accounts are outside this delivery.
The existing approved 24-hour quote, 15-minute reservation, own-team dispatch,
Razorpay, opt-in Meta WhatsApp and named TOTP-admin decisions remain in force.

| Item | Status | Planning model / effort | Implementation model / effort |
| --- | --- | --- | --- |
| 10. Live-site content and franchise entry points (PR 1/4) | Merged in PR #8 at upstream d5ab5c5 | `gpt-6-astra` / High recommended | `gpt-6-astra` / High implementation and Extra High final security review recommended; selected settings preserved |
| 11. Complete customer ecommerce (PR 2/4) | Merged in PR #9 at upstream 1544478 | `gpt-6-astra` / Extra High recommended | `gpt-6-astra` / Extra High recommended |
| 12. Complete admin and reporting (PR 3/4) | Merged in PR #10 at upstream f93edde; earlier performance failures remain recorded | `gpt-6-astra` / High recommended | `gpt-6-astra` / Extra High recommended |
| 13. Repeatable Docker staging acceptance (PR 4/4) | Conflicts resolved; workflow checks pass; remains draft for mobile performance | `gpt-6-astra` / High recommended | `gpt-6-astra` / Extra High recommended |
| 9. Approved commerce MVP and Docker handoff | Merged in [PR #7](https://github.com/brollysolutions/patnampakodi-site/pull/7) on 2026-09-10; fresh remote readback confirmed 2026-09-11 | `gpt-6-astra` / High recommended | `gpt-6-astra` / Extra High recommended; selected settings preserved |
| 8. Build the first stored-content storefront | Source snapshot included in item 9; original `feat/pakodi-storefront` work preserved | `gpt-6-astra` / High recommended; selected settings preserved | `gpt-6-astra` / High recommended; selected settings preserved |
| 1. Shared agent workflow and partner onboarding | Merged in [PR #1](https://github.com/brollysolutions/patnampakodi-site/pull/1); state verified 2026-09-07 | User-selected model; High recommended | User-selected model; High recommended |
| 2. Define website scope using the approved stack | Source reconciliation and phased decision brief delivered in [PR #6](https://github.com/brollysolutions/patnampakodi-site/pull/6); scope and visuals resolved by item 9; hosting remains a release input | `gpt-6-astra` / High recommended; selected settings preserved | `gpt-6-astra` / High recommended; selected settings preserved |
| 3. Adopt Astra workflow and verify delivery evidence | Merged in [PR #2](https://github.com/brollysolutions/patnampakodi-site/pull/2) | `gpt-6-astra` / High recommended; selected settings preserved | `gpt-6-astra` / High recommended; selected settings preserved |
| 4. Audit and repair workflow enforcement and onboarding | Delivered for review in [PR #3](https://github.com/brollysolutions/patnampakodi-site/pull/3) | User-selected model; High recommended | User-selected model; High recommended |
| 5. Reconcile PR #3 with upstream delivery safeguards | Resolved and verified for review in [PR #3](https://github.com/brollysolutions/patnampakodi-site/pull/3) | User-selected model; Medium recommended | User-selected model; Medium recommended |
| 6. Share advanced SEO, Lighthouse and the requested design workflow | Delivered for review in [PR #4](https://github.com/brollysolutions/patnampakodi-site/pull/4) | `gpt-6-astra` / High recommended; selected settings preserved | `gpt-6-astra` / High recommended; selected settings preserved |
| 7. Preserve the approved stack and SEO requirement | Delivered for review in [PR #5](https://github.com/brollysolutions/patnampakodi-site/pull/5) | `gpt-6-astra` / Medium recommended; selected settings preserved | `gpt-6-astra` / Medium recommended; selected settings preserved |

## Item 9 acceptance — 2026-09-10

Implement the [approved P0 MVP](approved-mvp-plan.md): preserved public storefront,
packaged catalog, guest requests, staff delivery quotes, timed reservations,
private Razorpay payment/cancellation/invoices, own-team fulfilment, opt-in Meta
notifications, named password/TOTP admins, stock/content/media/enquiry tools,
GST ledger, durable recovery and Docker/Caddy handoff. Financial refunds remain
independent of physical delivery status. P1 and the superseded courier module
remain outside this delivery.

The source storefront snapshot is included; its original uncommitted worktree
and the three archived briefs are preserved. Planning recommendation remains
gpt-6-astra / High; implementation and financial/security review remain
gpt-6-astra / Extra High. Selected settings were preserved; no subagents were used.

Fresh verification and residual limits are recorded in
[MVP verification](mvp-verification.md). All required components have fresh passing evidence; earlier complete-command
failures and the corrected audit are distinguished there. Delivery additionally
fixes hook-local Git environment leakage into test fixtures, verified by a real
linked-worktree regression and the 105-test workflow gate. Initial delivery `2b7acc4` was pushed and verified against open [PR #7](https://github.com/brollysolutions/patnampakodi-site/pull/7),
with matching head SHA and a clean worktree. This records that point in time;
subsequent delivery must verify the new head again. Next priority is configured staging acceptance with approved
catalog/legal/tax inputs, vendor accounts/templates and a chosen host, using
[commerce operations](../commerce-operations.md). Real provider transactions,
messages, production TLS/cutover and field performance are not claimed.

## Item 8 acceptance — 2026-09-09

Build the approved cream storefront and published-content foundation: preserve
the seven public entry paths, deliver responsive server-rendered content from
FastAPI/PostgreSQL through generated types, provide usable menu filtering and
outlet discovery states, and centralize metadata/sitemap/robots. Keep unpublished
content inaccessible and private page prefixes out of search. Record content
gaps without inventing prices, policies or contact details. Docker and local
developer commands must be reviewable and repeatable.

Non-goals for this first slice: payments, customer accounts, order processing,
admin mutation, live messages, final policy approval and production deployment.
APScheduler/Redis jobs follow when a business job is introduced; do not add
placeholder jobs. Verify API/schema/publication/isolation behavior, generation,
web build, browser interaction/no-JS/accessibility, SEO, Lighthouse and the
existing workflow gate. Review dependencies and the complete diff before PR.

## Item 2: supplied commerce briefs — 2026-09-09

The user supplied Patnam Pakodi design v0.2, FRAB MVP v4.1 and the Razorpay/
WhatsApp integration v1.0 documents with the live URL and requested action.
Preserve all three sources byte-for-byte, index their authority, trace all
50 features (45 P0 / 5 P1), reconcile the approved stack and prepare concrete
phased acceptance and visual proposals. Read-only live retrieval establishes
the homepage's noindex/nofollow and seven linked page paths; it does not prove
a complete URL inventory. Both GitHub repositories were verified private.

See [commerce reconciliation](pakodi-commerce-reconciliation.md),
[visual proposal](website-design-decisions.md) and
[live-site baseline](pakodi-live-site-baseline.md). Each future phase carries
its own recommended planning/implementation model and effort. This session
preserved selected settings and used no subagents.

Completed scope: source ingestion and reviewable delivery/design proposals.
No application, dependencies, database, provider setup or deployment was added.
Source conflicts remain explicit, particularly public/private indexability,
email fallback, TOTP, content facts and design assets. The first delivery scope
and privacy clarification were requested and remain unanswered. No proposal
is recorded as an approved product decision.

Fresh verification: full PowerShell CI gate passed on Python 3.13 (104 tests,
22 matching skills, configuration and shell checks). A local document check
passed source byte/hash equality, complete nonduplicated feature mapping,
priority totals and relative links. Diff whitespace check passed. Security and
PR self-review found no actionable defects in the documentation delivery;
application/provider/browser/design verification remains not applicable or
unverified as specified in the records. Initial sandbox execution was denied;
the approved verification rerun exited 0.

Initial delivery `54dc9ba` was committed and pushed from task branch
`feat/pakodi-commerce-briefs`; the helper verified open
[PR #6](https://github.com/brollysolutions/patnampakodi-site/pull/6) against shared
`main`, matching head SHA and a clean worktree. This follow-up records that
point-in-time observation; the current head must be checked again.
Next priority: resolve the proposed
first slice and open visual/indexability decisions, then implement phase A
with B's public design using the approved stack. Hosting, canonical content and
vendor decisions can be prepared alongside the build; live operations wait for
their own authorized acceptance checks.

## Item 7 acceptance

Preserve the user's stack/SEO instruction in `technology-stack.md`, index its
authority and reconcile current guidance. Distinguish selected technology from
implemented services and retain the unresolved SFTP/hosting question.
Non-goals: application scaffolding, dependency installation, credentials,
deployment configuration or deployment. Verify documentation links, review the
diff, run the full applicable workflow gate and deliver a documentation PR.
Next priority: item 2, website scope and hosting capabilities using the approved
Next.js, Python/FastAPI, PostgreSQL, APScheduler, Redis and Docker stack.

Fresh verification: full PowerShell CI gate passed 104 tests, 22-skill parity,
configuration and shell syntax checks. Documentation/diff review found no
actionable defects. Application, browser and deployment checks are not
applicable because those layers do not exist. Initial delivery `d1ec065` was
pushed and verified against open [PR #5](https://github.com/brollysolutions/patnampakodi-site/pull/5).

## Item 6 acceptance

Publish the user's locally prepared SEO/AEO/GEO/LLMO toolkit as a reviewable
repository change. Share detailed competitor, keyword, content-writing,
existing-content and UI/UX procedures in identical Codex/Claude skill trees.
Include the verified Lighthouse runner, isolated Chrome DevTools MCP plugin
builder, exact open-source package lock, synthetic verification and setup guide.
Generate machine-specific paths only into a new local plugin directory.

Include the follow-up request: install pinned Impeccable and Kowalski animation
guidance, reuse Taste, and apply all three during requested UI/UX work followed
by Apple Design verification. Retain licenses/provenance and adapt upstream
instructions to existing project permissions, model choice and delivery rules.

Non-goals: production-site auditing, choosing the application stack, connecting
accounts, automatic package/plugin installation, publishing personal reports,
changing global client settings, or merging the PR. No application, API,
database, contract, migration or deployment layers exist.

Security invariants: preserve existing plugin directories and browser profiles;
keep reports/configuration private; disable usage statistics and automatic CrUX
requests; retain dependency pins and failure statuses; treat page data as data.

Verification matrix: package/configuration and preservation tests, passive HTML
tests, skill parity, full workflow gate, synthetic MCP/browser/Lighthouse smoke,
dependency review, diff/security review, and fresh remote PR/head-SHA readback.

Fresh local results: full gate passed 104 tests and 22-skill parity; eight skill
entrypoints and the generated plugin validated; the complete synthetic browser
and mobile/desktop Lighthouse smoke passed; npm audit found zero known issues.
Generated-bytecode parity was reproduced and corrected without excluding source
files. Design source hashes and personal installations match the pinned bundles.
Security/PR self-review found no unresolved actionable defects. See feature status
for scope limits. Initial implementation `c756df9` was pushed and verified against
the open [PR #4](https://github.com/brollysolutions/patnampakodi-site/pull/4).
Item 2 remains the next product task.

## Item 3 acceptance

Apply the supplied 2026-09-07 workflow to this checkout's existing architecture.
Document command-result collection, model/effort preferences, and local-only
scope without changing personal settings or making shared tooling private.
Keep all 16 skills mirrored. Serialize finish invocations across worktrees and
require fresh PR identity, state, and head-SHA evidence before reporting success.
The state command exposes explicit remote verification; the stop hook checks
remote evidence when tracked delivery is pending.

Non-goals: application code, new dependencies/integrations, session setting
changes, hiding shared scaffolding, automatic merging, or broader shell parsing.
Security invariants: preserve user work, keep private notes ignored, keep PR
metadata as data, fail on unverified delivery, and retain existing hook gates.

Verification matrix: regression tests for stale/closed/wrong PRs, network and
Git failures, overlapping delivery, and lock release; full workflow gate for
configuration, mirrored skills, shell syntax, and existing behavior; live GitHub
readback after publication. Website scope/stack remains the next product task.

Original PR #2 delivery evidence: the full PowerShell gate passed all 77 tests, config/parity
validation (16 skills), and shell syntax checks. Security and PR self-review
found no unresolved actionable defects. Windows process contention and crash
release are exercised. Initial delivery `c286031` passed the new helper's live
open-PR/head-SHA readback for PR #2; the pushed fork branch tracks `origin`.
GitHub had not reported CI results at that readback. See `feature-status.md` for
the scope and environment limits. Item 2 remains the next product priority.

## Item 4 acceptance

Audit setup, both agent hook shims, Git hooks, delivery, CI, and shared guidance.
Include the user's follow-up: install Taste and Apple Design, research established
alternatives, and integrate suitable design references with the existing router.
Reproduce confirmed failures before fixing them. Select a supported Python even
when an older system interpreter is first on PATH; preserve user files and
private notes; prevent sensitive paths from entering delivery; keep hook commands
working from nested directories. Verify with regression tests, both shell entry
points, real temporary Git repositories, and the full applicable gate.

Non-goals: website code, external plugins, personal model changes, repository
ruleset changes, and PR merging. No application/API/database/contracts/jobs or
browser layers exist. Delivery is a reviewed task-branch PR to `upstream/main`.

Implementation `90574b6` is pushed to `origin/fix/workflow-audit` with
[PR #3](https://github.com/brollysolutions/patnampakodi-site/pull/3) targeting the
shared `main`. Local verification passed 71 tests, both setup entrypoints,
18-skill parity, individual skill validation, and staged checks. Existing private
notes survived repeated setup. The next priority is item 2, website scope and stack.

## Item 5 acceptance

Merge upstream `6b2fc7a` into the existing PR #3 branch, preserving explicit
file selection and history checks together with delivery locking and fresh
remote verification. Reconcile both contributors' records and mirrored skills.
Run the combined test suite, full workflow gate, diff review, and remote PR
readback. No application layers exist. Do not merge PR #3 into main.

The merge preserves both delivery implementations. The combined suite initially
exposed incompatible test fixtures: audit tests lacked a lock fixture, and the
incoming finish tests lacked explicit file selection. Updated those fixtures and
added coverage for selected-file delivery with fresh remote evidence. The full
PowerShell gate passed **90 tests**, configuration/parity for **18 shared skills**,
and shell checks on 2026-09-08. Security and PR self-review found no unresolved
integration defects. The next product priority remains item 2.

## Item 1 acceptance

A fresh clone can run setup on Windows or Bash, enable Git hooks, create private
notes without overwriting existing notes, validate mirrored skills, and pass the
workflow/SEO tests. PR CI checks the workflow and delivery evidence. The partner
guide explains both contributors' clone/branch/PR process. Publish to the fork
and open a PR against `brollysolutions/patnampakodi-site:main`.

Non-goals: website implementation, deployment, production configuration, installing
external plugins, changing personal models, or merging the PR.

Security invariants: no credentials/local approvals committed; no deployment
permissions in CI; preserve existing files; setup failures return nonzero.

Verification: setup twice, complete applicable gate, clean-clone setup, hook
payload smoke tests, diff review, and GitHub PR/check readback. Results are
recorded in `feature-status.md`.

The setup was also checked from a fresh clone with both shell entry points.
Delivery found a Windows Git-hook executable lookup issue; the corrected lookup
now has regression coverage for terminal and internal Git-hook paths.
Repeated delivery also exposed the CLI's unsupported owner-qualified head filter;
the helper now uses GitHub's exact REST head/base filters to update the existing PR.

Initial implementation: `e239ce0`; subsequent delivery fixes are in this PR.
At the original delivery, all 59 tests passed. Fork CI passed for that implementation in
[run 34091277143](https://github.com/vamshisaideep9/patnampakodi-site/actions/runs/34091277143).
PR #1 was merged into shared `main` on 2026-09-07 (GitHub readback during the
audit). The next product task is item 2 above. Current audit evidence is in
`workflow-audit.md` and `feature-status.md`.

## Earlier catalog integration record

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
