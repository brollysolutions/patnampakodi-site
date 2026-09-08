# Workflow audit — 2026-09-08

Scope: shared instructions, skills, per-clone setup, Codex/Claude hook shims,
Git hooks, Python delivery engine, CI, and onboarding. The checkout began clean
at `847e6ff` on `main`; fixes use `fix/workflow-audit`. There is no application,
API, database, generated contract, job, deployment, or browser flow to audit.

The protected assets are local user work, repository history, and credentials.
Inputs include tool payloads, filenames, commands, and commit history. Hooks are
local guardrails rather than a security sandbox. Findings below were reproduced
with synthetic filenames and test content; no real secret files were read.

| Priority / confidence | Confirmed trigger and impact | Fix and evidence |
| --- | --- | --- |
| High / high | A sensitive file added in one outgoing commit and removed later vanished from the final diff, allowing the delivery helper to push the earlier blob. | Inspect paths in every outgoing commit, including merges. A real temporary Git history reproduces the add/remove case; delivery test verifies no push. |
| High / high | Failed `git diff` returned an empty list, indistinguishable from a safe diff. | Propagate Git failures; invalid-ref regression test now raises. |
| Medium / high | `finish` used `git add --all`, absorbing unrelated pending user files. | Require exact `--paths`, pass literal pathspecs, and refuse unrelated staged files. Tests verify no implicit staging and preservation of unselected files. |
| Medium / high | Text-mode Git status quoting lost Unicode paths and rename sources. | Use NUL-delimited status/diff output; real Git tests cover Unicode, spaces and both rename paths. |
| Medium / high | Secret paths inside `apply_patch` headers or explicit file fields containing spaces escaped the hook checks. | Inspect path fields and patch headers, including move destinations. Positive and negative regression cases verify denial without blocking documentation prose. |
| Medium / high | Force pushes to task branches were allowed by the command predicate despite the shared contract. | Deny common force flags and forced refspecs; regression cases cover each. General shell parsing remains deliberately limited. |
| Medium / high | Codex invoked relative script paths, so starting under `scripts/` failed before reaching the shim. | Resolve the Git root in both configured commands. Tests run the actual configured Bash and Windows commands from a subdirectory. See [official hook working-directory guidance](https://learn.chatgpt.com/docs/hooks). |
| Medium / high | This checkout had no configured Git hooks, no `uv`, and Python 3.10 on PATH. Entrypoints did not constrain uv's interpreter selection. | Installed uv and Python 3.13 locally, ran per-clone setup, and required Python >=3.11 in wrappers and Git hooks. Agent shims disallow runtime downloads during tool calls. |
| Medium / high | Push CI covered only `main` and the old setup branch, leaving new fork task branches without push verification. | Run verification on branch pushes and explicitly provision Python 3.11 and 3.13 on Ubuntu/Windows with an immutable official action reference. |
| Low / high | Onboarding still described PR #1 as unmerged. | GitHub reports it merged on 2026-09-07. Updated clone instructions and marked the old verification record as historical. |

## Verification

The original suite passed 59 tests before new coverage. New tests then failed
for the intended defects, including both configured hook entrypoints. The
expanded suite passes **71 tests** locally under Python 3.13. Setup enables
`.githooks`, preserves private notes, and validates **18 identical shared skills**.
The normal gate includes shell syntax checks. `design-skills.md` documents the
separate installation review and research into six design-skill repositories.

CI provisions a supported interpreter using
[`actions/setup-python`](https://github.com/actions/setup-python/tree/ece7cb06caefa5fff74198d8649806c4678c61a1),
pinned to an immutable revision with read-only repository permission and no
dependency cache. Checkout also remains pinned with credentials persistence
disabled. PR metadata continues to enter the policy job as data in environment
variables, never as shell source. No merge, deployment, or ruleset changes occur.

## Remaining limits

No validated finding remains in the changed paths after regression verification
and diff review. These checks do not prove live client hook trust or exhaustively
parse arbitrary shell/interpreter code. Filename checks do not scan secret values
hidden in ordinary source files. `finish` is the guarded delivery route; manual
Git operations still rely on human review and the existing Git hooks. A user can
edit local guards. GitHub required checks/rulesets remain an administrator setting.
No product/browser/SEO runtime or design-output benchmark is applicable yet.

Delivery and live CI evidence are recorded in `feature-status.md`; do not treat a
configured CI matrix as evidence that all hosted jobs have passed.
