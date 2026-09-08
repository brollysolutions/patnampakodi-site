# Implementation plan

Update this file and `feature-status.md` with product/workflow script changes.
Record one in-progress item per task branch; independent contributors may each
have a different task branch. Preserve the other contributor's records when
resolving a conflict. Use the selected model; do not switch or delegate silently.

| Item | Status | Planning model / effort | Implementation model / effort |
| --- | --- | --- | --- |
| 1. Shared agent workflow and partner onboarding | Merged in [PR #1](https://github.com/brollysolutions/patnampakodi-site/pull/1), 2026-09-07 | User-selected model; High recommended | User-selected model; High recommended |
| 2. Define website scope and choose stack | Not started | Select when scoped | Select when scoped |
| 3. Audit and repair workflow enforcement and onboarding | In progress on `fix/workflow-audit` | User-selected model; High recommended | User-selected model; High recommended |

## Item 3 acceptance

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
