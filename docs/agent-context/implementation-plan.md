# Implementation plan

Update this file and `feature-status.md` with product/workflow script changes.
Record one in-progress item per task branch; independent contributors may each
have a different task branch. Preserve the other contributor's records when
resolving a conflict. Use the selected model; do not switch or delegate silently.

| Item | Status | Planning model / effort | Implementation model / effort |
| --- | --- | --- | --- |
| 1. Shared agent workflow and partner onboarding | Delivered for review in [PR #1](https://github.com/brollysolutions/patnampakodi-site/pull/1) | User-selected model; High recommended | User-selected model; High recommended |
| 2. Define website scope and choose stack | Not started | Select when scoped | Select when scoped |

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
All 59 tests pass. Fork CI passed for the initial implementation in
[run 34091277143](https://github.com/vamshisaideep9/patnampakodi-site/actions/runs/34091277143).
The workflow is available on `chore/shared-agent-workflow`; merge remains a human
review action. The next product task is item 2 above.
