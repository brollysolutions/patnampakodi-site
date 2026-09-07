---
name: private-project-workflow
description: Maintain this checkout's private decision, execution-flow, session, and design context. Use before implementing, debugging, reviewing, or designing in this repository when local working memory would help; do not use for a simple factual answer.
---

# Private Project Workflow

1. Read the tracked `AGENTS.md`, closest nested instructions, `SECURITY.md`, and relevant tracked context first.
2. Read `.agent-workflow/WORKFLOW.md` as a non-authoritative local supplement.
3. Before editing, decide whether the task creates a durable decision or materially changes an execution flow.
4. If so, update `.agent-workflow/DECISIONS.md` or `.agent-workflow/FLOW.md` with concise evidence and code anchors.
5. After making changes, update `.agent-workflow/SESSION.md` with the actual changed scope and verification status.
6. Never stage or commit private workflow artifacts. Verify Git ignores them before shipping tracked work.
7. If private notes conflict with tracked sources, follow the tracked sources and correct the note.
