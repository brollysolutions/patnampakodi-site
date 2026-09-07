# Patnam Pakodi

Shared repository for the Patnam Pakodi site. The application has not been
scaffolded yet; this repository currently provides the team's agent workflow.

Start with the [partner workflow guide](docs/partner-workflow-guide.md) for
installation, day-to-day collaboration, and troubleshooting.

- [Shared engineering rules](AGENTS.md)
- [Implementation plan](docs/agent-context/implementation-plan.md)
- [Feature status and verification](docs/agent-context/feature-status.md)
- [Security guidance](SECURITY.md)

From a clone containing these files, run one setup command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/setup-agent-workflow.ps1
```

Or on macOS/Linux/Git Bash:

```bash
bash scripts/setup-agent-workflow.sh
```

Requires Git, Bash (Git Bash on Windows), uv, and Python 3.11+. GitHub CLI
authentication and repository access are needed to publish PRs. See the guide
before opening your first agent session.
