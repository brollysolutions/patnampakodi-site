---
name: ship
description: Finish a completed change by verifying it, reviewing the diff, committing, pushing to the contributor fork, and creating or updating the upstream pull request. Use whenever changed work is ready, the user asks to commit/push/open a PR, or a stop hook says delivery is incomplete.
---

# Ship

Convert verified work into a reviewable PR. Never merge it.

For an explicitly local task confined to already-ignored workflow files, review
and verify locally, record evidence in `.agent-workflow/`, and finish without a
commit or PR. Do not force-add private artifacts. Tracked changes use the steps
below. Preserve unrelated work; the helper stages only explicitly selected task
files and requires a clean worktree before it can report delivery complete.

1. Confirm the current branch is a non-protected task branch and that unrelated user changes are absent. Inspect `git status`, `git diff`, and `git diff --cached`.
2. Run the full applicable checks from `AGENTS.md` with fresh output. Include contract generation, migration-head checks, browser verification, and security review when triggered by the change.
3. Run `git diff --check`. Search the changed file list for env files, secrets, keys, dumps, generated caches, debug artifacts, or unrelated files.
4. Choose a conventional title and commit message such as `feat(scope): summary`, `fix(scope): summary`, or `security(scope): summary`.
5. Summarize user-visible/technical changes, exact verification commands, security impact, migration/contract implications, and known limitations.
6. Run the deterministic helper from the repository root:

   ```text
   uv --cache-dir .uv-cache run --no-project --python ">=3.11" python scripts/agent_workflow.py finish --title "<type(scope): summary>" --commit-message "<type(scope): summary>" --verification "<commands and results>" --security "<review result or not applicable>"
   ```

   For pending changes, add `--paths <file> [<file> ...]` with the exact reviewed task files relative to the root, including both sides of renames. Directories and globs are refused. The helper preserves unselected working files and refuses an index containing unrelated staged files. Omit `--paths` when retrying delivery of an already clean, committed branch.

   Add `--body-file <path>` only when a richer prepared PR body is needed.
7. Retain the command's session/job identifier and collect its terminal result, including `session_id` and `exit_code` in code mode. Run only one delivery process at a time; the helper's OS lock spans this clone's worktrees and releases on process exit. If it fails, preserve completed steps, inspect current Git/PR state, and retry safely. Never force-push, bypass verification, or create a second PR for the same head branch.
8. Confirm the final worktree is clean, the branch tracks `origin`, and no commits are ahead locally. Run `uv --cache-dir .uv-cache run --no-project --python ">=3.11" python scripts/agent_workflow.py state --remote` to check the recorded PR's current repository, base/head branches, state, and head SHA against local HEAD. A cached URL alone is not delivery evidence. Report failed, skipped, running, and unverified checks distinctly.
9. Return the PR URL, commit, base/head branches, checks run, and any residual risk.
