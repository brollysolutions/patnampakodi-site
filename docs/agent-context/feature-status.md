# Feature status

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
