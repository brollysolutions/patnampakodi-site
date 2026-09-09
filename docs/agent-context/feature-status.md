# Feature status

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
not applicable; no credentials or infrastructure were added. PR delivery is
pending. Older sections below retain
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
