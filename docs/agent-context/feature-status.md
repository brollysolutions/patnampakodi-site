# Feature status

## Shared workflow — 2026-09-07

Delivered for review in [PR #1](https://github.com/brollysolutions/patnampakodi-site/pull/1),
branch `chore/shared-agent-workflow`. Initial implementation `e239ce0` plus the
delivery fixes in the same PR. Not merged.

| Requirement | Status | Evidence |
| --- | --- | --- |
| Shared Codex and Claude Code instructions/skills | Verified | `AGENTS.md`; validation passes with 16 identical skills |
| Per-clone setup and private templates | Verified | PowerShell then Git Bash setup in a fresh clone; notes preserved; clean status |
| Local Git and agent lifecycle hooks | Verified by terminal smoke tests | Both shims; protected edit/secret-read denial; automatic branch; stop checks; real Git hooks reject protected commits/pushes |
| Workflow verification and PR policy CI | Fork workflow CI passed; PR checks reported by GitHub | [Run 34091277143](https://github.com/vamshisaideep9/patnampakodi-site/actions/runs/34091277143); `.github/workflows/` |
| Partner explanation and installation guide | Complete | `docs/partner-workflow-guide.md`, linked from `README.md` |
| GitHub publication | Complete; awaiting human review | [PR #1](https://github.com/brollysolutions/patnampakodi-site/pull/1); fork branch pushed and tracking origin |

## Fresh verification

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
