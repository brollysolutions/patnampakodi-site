# Implementation plan

Update this file and `feature-status.md` with product/workflow script changes.
Record one in-progress item per task branch; independent contributors may each
have a different task branch. Preserve the other contributor's records when
resolving a conflict. Use the selected model; do not switch or delegate silently.

| Item | Status | Planning model / effort | Implementation model / effort |
| --- | --- | --- | --- |
| 1. Shared agent workflow and partner onboarding | Merged in [PR #1](https://github.com/brollysolutions/patnampakodi-site/pull/1); state verified 2026-09-07 | User-selected model; High recommended | User-selected model; High recommended |
| 2. Define website scope and choose stack | Not started | Select when scoped | Select when scoped |
| 3. Adopt Astra workflow and verify delivery evidence | Merged in [PR #2](https://github.com/brollysolutions/patnampakodi-site/pull/2) | `gpt-6-astra` / High recommended; selected settings preserved | `gpt-6-astra` / High recommended; selected settings preserved |
| 4. Audit and repair workflow enforcement and onboarding | Delivered for review in [PR #3](https://github.com/brollysolutions/patnampakodi-site/pull/3) | User-selected model; High recommended | User-selected model; High recommended |
| 5. Reconcile PR #3 with upstream delivery safeguards | Resolved and verified for review in [PR #3](https://github.com/brollysolutions/patnampakodi-site/pull/3) | User-selected model; Medium recommended | User-selected model; Medium recommended |

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
