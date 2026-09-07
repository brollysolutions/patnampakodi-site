# Private project workflow

Status: local-only working agreement; never commit

This file supplements the repository workflow for this checkout. It never
overrides `AGENTS.md`, nested instructions, `SECURITY.md`, product references,
current code, tests, or explicit user decisions.

## Task lifecycle

1. Classify the request as read-only, brainstorm, diagnose, implement, review, or ship.
2. For implementation, follow the repository orientation and branch gates before
   editing tracked files.
3. Record only durable decision rationale in `DECISIONS.md`; do not record hidden
   chain-of-thought.
4. Update `FLOW.md` only when a material execution path is discovered or changed.
5. Update `SESSION.md` with a concise, evidence-based description of what the
   agent changed.
6. For web design work, route through the private design skills:
   - `design-reference` before an unsettled visual direction;
   - `design-create` for approved public/marketing UI creation or redesign;
   - `design-review` after user-visible web changes.
7. Before concluding tracked work, follow the repository's verification, review,
   commit, push, and PR contract.

## Local artifact rules

- Keep every file under `.agent-workflow/` private and ignored.
- Never treat these files as product authority or fresh test evidence.
- Never copy secrets, customer data, KYC material, production data, private
  prompts, or complete source files here.
- Prefer repository-relative code anchors and the verified commit SHA over pasted
  implementation details.
- If private notes conflict with tracked sources, discard or correct the note.
- Local workflow changes need no commit or PR. Any tracked repository change still
  follows `AGENTS.md`.

## Decision threshold

Record a decision only when it affects architecture, security, product behavior,
data/API contracts, dependencies, migrations, rollout, or a hard-to-reverse UI
system choice. Routine implementation details belong in the diff or PR.

## Flow threshold

Document the important path from entry point to side effects. Do not attempt an
exhaustive function-by-function call graph. Include authorization, tenancy, state
transitions, external calls, failure behavior, and relevant tests when present.
