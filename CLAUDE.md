@AGENTS.md

# Claude Code adapter

Read the shared contract above and use the project skills in `.claude/skills/`.
The hooks in `.claude/settings.json` call the shared Python engine through Bash;
on Windows, use Git Bash. Start a fresh session after setup and inspect `/hooks`.

No external plugin or MCP server is enabled by this repository. Add one only for
an actual task after reviewing its version, permissions, and data access.
Account credentials, local approvals, and personal model settings stay per user.
Private notes are optional and created by the setup script.
