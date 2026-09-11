# Implementation plan

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
