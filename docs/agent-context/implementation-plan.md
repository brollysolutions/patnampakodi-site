# Implementation plan

Update this file and `feature-status.md` with product/workflow script changes.
Record one in-progress item per task branch; independent contributors may each
have a different task branch. Preserve the other contributor's records when
resolving a conflict. Use the selected model; do not switch or delegate silently.

| Item | Status | Planning model / effort | Implementation model / effort |
| --- | --- | --- | --- |
| 1. Shared agent workflow and partner onboarding | Merged in [PR #1](https://github.com/brollysolutions/patnampakodi-site/pull/1); state verified 2026-09-07 | User-selected model; High recommended | User-selected model; High recommended |
| 2. Define website scope and choose stack | Not started | Select when scoped | Select when scoped |
| 3. Adopt Astra workflow and verify delivery evidence | In progress on `chore/astra-workflow` | `gpt-6-astra` / High recommended; selected settings preserved | `gpt-6-astra` / High recommended; selected settings preserved |

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

Current evidence: the full PowerShell gate passed all 77 tests, config/parity
validation (16 skills), and shell syntax checks. Security and PR self-review
found no unresolved actionable defects. Windows process contention and crash
release are exercised; Linux CI and live delivery readback are pending. See
`feature-status.md` for the scope and environment limits.

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
