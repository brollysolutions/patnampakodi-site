---
name: frontend-change
description: Implement a client-side change — route, component, state, or API wrapper — against generated contract types, with accessibility and server/client boundaries intact. Use for any web UI or client data work, including as a sub-step of work-feature or systematic-debug.
---

# Frontend Change

Apply only to layers that exist. This repository has no application yet; discover
and document the chosen stack before using the examples below. Contract generation
and migration commands apply only when configured; do not create a stack to satisfy
this procedure. Use the actual verification commands recorded in AGENTS.md.

1. Trace the path before editing: route entry, feature/component, state or hook, API wrapper, generated contract type, backing endpoint, and nearby tests. Find an analogous screen before inventing a pattern.
2. Keep server and client component boundaries intentional. Add a client directive only where browser state or effects require it.
3. Use the generated contract types and existing API wrappers. Never hand-write wire types the generated schema already covers, and never edit generated files.
4. Treat decoded tokens and client-side role checks as navigation hints only. The server remains the authorization boundary; a hidden control is not an access control.
5. Preserve keyboard access, labels, focus behavior, semantic markup, loading/empty/error states, responsive layout, and the established visual system.
6. Do not expose secrets through public environment variables, logs, rendered errors, browser storage, or analytics.
7. For user-visible changes, inspect the result in a real browser and cover the critical path with a unit or end-to-end test when practical.
8. Run targeted tests while iterating, then the web gate from `AGENTS.md`: lint, typecheck, tests, and build. Run the end-to-end suite for changed journeys, or state exactly why it could not run.
9. Invoke `$design-review` for a user-visible change.
