# Our Patnam Pakodi development workflow

## A message you can share with your partner

We have put our coding workflow inside the GitHub repository so we both use the
same rules, checks, and project context. You can work in Codex or Claude Code.
Each task goes on its own branch, gets checked, and becomes a pull request for
review. Pushing a branch does not change the shared main branch or deploy a site.

The agent should study the relevant files, implement the task, run checks, update
our shared progress records, and provide the PR link. We review the result before
merging. For questions, diagnosis, or reviews, it should inspect and explain;
ask explicitly when you want it to make changes.

You do not need the original Desktop workflow-kit folder. The reusable files are
in GitHub. You do need to run setup once in your own clone and log in with your
own GitHub and coding-assistant accounts.

## What is ready today

The workflow is installed; the website itself has not been built. The approved
stack is Next.js, Python/FastAPI, PostgreSQL, APScheduler, Redis and Docker, with
SEO-friendly public pages. See the [stack decision](agent-context/technology-stack.md).
There is no running development server, production domain or deployment
configuration. Hosting and SFTP/SSH access remain unconfirmed.
Website/browser/SEO checks will become applicable when
the website is added. Passing workflow tests is not a website launch approval.

## Get the files

The shared repository is
[brollysolutions/patnampakodi-site](https://github.com/brollysolutions/patnampakodi-site).
Mahan's contribution fork is
[vamshisaideep9/patnampakodi-site](https://github.com/vamshisaideep9/patnampakodi-site).

The original setup [PR #1](https://github.com/brollysolutions/patnampakodi-site/pull/1)
and Astra delivery safeguards [PR #2](https://github.com/brollysolutions/patnampakodi-site/pull/2)
are merged. Contributors with shared-repository write access can use:

```bash
git clone https://github.com/brollysolutions/patnampakodi-site.git
cd patnampakodi-site
```

Otherwise create your own fork on GitHub and clone it. Its `origin` is where you
push; setup adds the shared repository as `upstream`. Existing remotes are
preserved. Inspect `git remote -v` before publishing anything.

## One-time setup on your machine

1. Install [Git](https://git-scm.com/downloads), [GitHub CLI](https://cli.github.com/),
   and [uv](https://docs.astral.sh/uv/getting-started/installation/).
   On Windows include Git Bash with Git for Windows. Reopen your terminal after
   installation. Node, pnpm, browsers, and external plugins are not needed yet.
2. Install/open your preferred Codex or Claude Code client and sign in yourself.
   Use the client's official installation instructions. Do not copy someone
   else's home-directory configuration, tokens, hook trust hashes, or logins.
3. In your repository terminal, check the tools and your Git identity:

   ```bash
   git --version
   gh --version
   uv --version
   git config user.name
   git config user.email
   gh auth login
   gh auth status
   uv python install 3.13
   uv --cache-dir .uv-cache run --no-project --python ">=3.11" python --version
   ```

   Python must be 3.11 or newer. If identity is missing, set your own name/email
   with `git config user.name "Your Name"` and
   `git config user.email "your GitHub email"` inside this clone.
   Skip `gh auth login` if already authenticated as the correct account.
4. Run setup from this repository:

   Windows PowerShell:

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/setup-agent-workflow.ps1
   ```

   macOS, Linux, or Git Bash:

   ```bash
   bash scripts/setup-agent-workflow.sh
   ```

   Setup connects local Git hooks, adds `upstream` for a fork when absent,
   creates ignored private notes, and runs verification. It preserves existing
   notes and returns a failure if a required command fails. It does not commit,
   push, install plugins, grant account access, or approve client hooks.
   It is safe to rerun after workflow updates or in every new clone.
5. Confirm the result:

   ```bash
   git config --get core.hooksPath
   uv --cache-dir .uv-cache run --no-project --python ">=3.11" python scripts/agent_workflow.py validate
   git status --short --branch
   ```

   Expect `.githooks`, `{"status": "valid", "skill_count": 18}`, and no new
   tracked changes from setup. Private notes should not appear in Git status.
6. Open a fresh agent session in the repository. Review its hook configuration.
   In Codex CLI, `/hooks` shows hooks requiring trust; approve only the reviewed
   project hooks. Project hooks run only after project and hook trust, as
   described in the [official Codex hook documentation](https://learn.chatgpt.com/docs/hooks).
   For Claude Code, inspect `/hooks` and its project settings. On Windows make
   sure Claude's Bash resolves to Git Bash, not the Windows WSL launcher.

The engine and shims can be tested from a terminal; that does not prove the
client loaded them. In a fresh session, confirm it sees `AGENTS.md`, the project
skills, and the configured hooks. On clean `main`, the first prompt creates a
task branch when the lifecycle hook is active. This can happen even for a
read-only prompt; it should not cause a commit or PR without changes.

## How we work together each day

1. Keep separate clones and separate task branches. Agree who owns each task,
   especially before touching the same files. Do not run two editing sessions
   in one working directory.
2. Start from a clean working tree. Update your
   local `main` from the shared repository:

   Fork clone:

   ```bash
   git status --short
   git fetch upstream
   git switch main
   git merge --ff-only upstream/main
   git switch -c feat/short-task-name
   ```

   Direct shared-repository clone:

   ```bash
   git status --short
   git switch main
   git pull --ff-only origin main
   git switch -c feat/short-task-name
   ```

   If you have unfinished changes, finish that task or use a separate clone.
   If a fast-forward fails, inspect divergence before choosing a resolution.
3. Give the agent an outcome and any boundaries. For example:
   "Read the project context, propose the website scope, and stop before coding."
   Or: "Implement the agreed menu page, verify it, update the records, and open
   a PR." Use "diagnose only" or "review only" when you want an explanation.
4. The agent recommends effort without switching your model. The preference is
   `gpt-6-astra`, with a personal default of `xhigh`: Medium for routine tasks,
   High for cross-layer work, Extra High for difficult debugging/security.
   Keep your selected model and effort unless you choose to change them. If your
   requested model is unavailable, the agent reports it instead of substituting.
   Max or deeper modes and subagent delegation require your explicit choice.
   The repository does not override your model or effort settings.
5. Review the PR's changes and fresh verification evidence. One of us merges
   through GitHub after review. The workflow does not automatically merge or
   deploy. Then repeat from updated `main` for the next task.

## What each part does

| Part | Purpose | Travels through GitHub? |
| --- | --- | --- |
| `AGENTS.md`, `CLAUDE.md`, `SECURITY.md` | Shared rules and current project boundaries | Yes |
| `.agents/skills/`, `.claude/skills/` | Matching task procedures for both clients | Yes |
| `.codex/hooks.json`, `.claude/settings.json` | Client lifecycle hook definitions | Yes; each user reviews/trusts locally |
| `.githooks/` | Reject protected-branch commits/pushes and run checks | Yes; setup activates them per clone |
| `.github/workflows/` | PR metadata policy and workflow test jobs | Yes |
| `docs/agent-context/` | Shared plan, status, decisions, and quality guidance | Yes |
| `.agent-workflow/`, `CLAUDE.local.md` | Personal working notes | No |
| `.claude/settings.local.json`, credentials, client trust | Local permissions and account state | No |

The main procedure is `work-feature`, then relevant implementation/review skills,
then `review-pr` and `ship`. Diagnosis and review requests stay read-only unless
you request a fix. Codex discovers project skills under `.agents/skills`, per
its [official skill documentation](https://learn.chatgpt.com/docs/build-skills).
You can explicitly invoke `$work-feature`, `$review-pr`, or `$ship` in Codex;
Claude Code uses `/work-feature`, `/review-pr`, or `/ship`.

Both skill trees must stay identical. When changing a skill, update both copies
and run validation. Server, generated-contract, and design skills are included
for later use; their stack-specific steps apply only after those layers exist.

Taste (`design-taste-frontend`) and Anthropic (`frontend-design`) are shared design
references. The router chooses the appropriate one for a task. Apple Design is
an optional local HIG reference installed separately for each contributor; it is
already installed for this checkout's user in Codex and Claude Code. See
[design skill research and pinned sources](agent-context/design-skills.md).

Our shared plan and feature-status records must accompany changes to scripts or
product code. The co-change check proves the files were included, not that the
claims in them are true; reviewers check the evidence.

## Checks and delivery

Full applicable gate:

```bash
bash scripts/verify.sh --ci
```

PowerShell equivalent:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1 --ci
```

Ask the agent to ship after verification. The `ship` skill uses
`scripts/agent_workflow.py finish` to commit, push to `origin`, and create/update
a PR against `upstream/main` when configured, otherwise `origin/main`. For pending
changes, pass `--paths` followed by exact reviewed task filenames relative to the
repository root. Include both old and new paths for renames; do not pass directories
or globs. Unselected working files remain untouched; unrelated staged files cause
a refusal before staging. Omit `--paths` when retrying an already committed clean
branch. The helper checks sensitive filenames across all outgoing commits,
including files removed before the final diff. Use a conventional title such as
`chore(workflow): update setup`.
The PR includes Summary, Verification, and Security sections.

The helper verifies the PR's current repository, base/head branches, open state,
and head commit against local HEAD before recording its URL and reporting
success. It requires a clean final worktree and checks the `origin` tracking branch. An OS
lock prevents overlapping finish invocations across this clone's worktrees and
releases when the process exits, including crashes. Keep the lock file in the
Git directory; do not delete it while a process could still be running.

A stop hook notices dirty/unpushed work, a missing recorded PR, or remote
evidence that does not match the branch. An exact matching merged PR can end an
old task; new delivery requires an open PR. GitHub reads have a 15-second timeout.
Network/auth failures leave delivery unverified. The stop hook's existing
recursion guard still limits repeat prompts; it is not a delivery certificate.

Read local state without network access, or request a fresh remote check:

```bash
uv --cache-dir .uv-cache run --no-project --python ">=3.11" python scripts/agent_workflow.py state
uv --cache-dir .uv-cache run --no-project --python ">=3.11" python scripts/agent_workflow.py state --remote
```

The remote command returns nonzero when PR evidence cannot be verified. A saved
URL alone is not proof. Collect every command's terminal result before retrying;
keep its session/job identifier, `session_id`, and `exit_code` when available.
Report failed, skipped, running, and unverified checks separately from passes.
Never start a second commit/push/PR process while the first is running.

Explicitly local workflow tasks stay in already-ignored files such as
`.agent-workflow/`. Review them and record local verification without a PR.
The shared instructions, skills, hooks, tests, and CI remain tracked here; do
not adopt another checkout's private-scaffolding exclusions. The
[Astra workflow adaptation](agent-context/astra-workflow-reference.md) records
the supplied reference and the differences that apply to this repository.

## Troubleshooting and limits

| Symptom | What to do |
| --- | --- |
| `uv` missing / Python too old | Install the prerequisites, reopen the terminal, and verify Python is 3.11+ |
| `bash` starts WSL on Windows | Use Git Bash; PowerShell setup locates Bash beside Git for Windows |
| Setup says permission denied for `.git/config` | Allow the scoped local setup operation in your client and rerun it |
| Protected branch is dirty | Preserve the files and resolve task ownership; do not reset or discard them |
| Commit asks for plan/status | Update and stage both living records with the script/product change |
| Skill parity fails | Make the corresponding skill files identical in both trees, then revalidate |
| GitHub permission/auth error | Check `gh auth status`, `git remote -v`, and write access to `origin` |
| PR checks await approval | A shared-repository maintainer may need to approve the fork's first Actions run |
| Stop hook says the PR is missing | Run `state`; use the ship helper to find/update the existing PR and record its URL |
| Hooks do not run in the agent | Restart in the repository, inspect hook support/trust, and check the Python runtime |

Hooks are guardrails with limited command parsing. They are not a complete
security boundary and cannot detect every embedded secret. The agent hook shims
allow execution if no runtime works, with a stderr warning. Fix the runtime;
do not treat an absent block as evidence that something is safe.

GitHub Actions report checks. Making them mandatory before merge requires an
admin to configure branch protection/rulesets; this setup does not change those
repository settings. No external plugins or MCP servers are required or enabled.
Add one later only for a concrete task after reviewing access and pinned versions.
