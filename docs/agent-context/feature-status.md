# Feature status

CI follow-up: Ubuntu AppArmor blocked the downloaded browser. Install the already-pinned Chromium companion SUID helper as root-owned mode 4755 on the ephemeral CI runner and validate those properties before launch. The sandbox and budgets remain enabled. Shell syntax passes; Linux runtime/performance verification is pending. OpenAPI generation now explicitly writes LF, avoiding Windows-only delivery-state churn.


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

## Four-PR completion — 2026-09-10

The user approved the full website/ecommerce/admin plan. Item 10 is in progress:
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
