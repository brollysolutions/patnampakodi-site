# Implementation plan

Update this file and `feature-status.md` with product/workflow script changes.
Record one in-progress item per task branch; independent contributors may each
have a different task branch. Preserve the other contributor's records when
resolving a conflict. Use the selected model; do not switch or delegate silently.

## Approved four-PR delivery

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
| 10. Live-site content and franchise entry points (PR 1/4) | Delivered as draft [PR #8](https://github.com/brollysolutions/patnampakodi-site/pull/8); functional checks pass, CI performance pending | `gpt-6-astra` / High recommended | `gpt-6-astra` / High implementation and Extra High final security review recommended; selected settings preserved |
| 11. Complete customer ecommerce (PR 2/4) | In progress; functional/browser/container checks pass; local mobile performance fails, depends on draft PR #8 | `gpt-6-astra` / Extra High recommended | `gpt-6-astra` / Extra High recommended |
| 12. Complete admin and reporting (PR 3/4) | Planned; depends on item 11 | `gpt-6-astra` / High recommended | `gpt-6-astra` / Extra High recommended |
| 13. Repeatable Docker staging acceptance (PR 4/4) | Planned; depends on item 12 | `gpt-6-astra` / High recommended | `gpt-6-astra` / Extra High recommended |
| 9. Approved commerce MVP and Docker handoff | Delivered for review in [PR #7](https://github.com/brollysolutions/patnampakodi-site/pull/7); see approved-mvp-plan.md | `gpt-6-astra` / High recommended | `gpt-6-astra` / Extra High recommended; selected settings preserved |
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
