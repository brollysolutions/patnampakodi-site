---
name: design-create
description: Build or redesign an approved public-facing or marketing web page against the project's existing design system. Use when the visual direction is already settled and the user asks to create, build, or redesign a page, landing section, or marketing surface.
---

# Design Create

Implement an approved direction with the system that already exists.

Use one visual reference when it helps: `design-taste-frontend` for marketing pages, or `frontend-design` for other interfaces. Follow `docs/agent-context/design-skills.md` for scope and source precedence. Existing user approval remains valid.

1. Read `.agent-workflow/DESIGN.md`, the affected route end to end, and the existing tokens, fonts, spacing scale, and component primitives. Find the closest existing page and match it before inventing anything.
2. State one design read before editing: page kind, audience, the trust constraint the page carries, and the visual language in use. If the direction is not settled, stop and invoke `$design-reference`/`/design-reference` instead.
3. Reuse existing tokens, fonts, and primitives. Introducing a new token, font, animation library, or UI dependency is a reviewed decision, not a detail — raise it and justify it before adding it.
4. Ship the smallest complete change. Complete means every state is handled: loading, empty, error, long content, and truncation.
5. Build responsively from the smallest supported viewport up. Verify the layout at narrow, medium, and wide widths rather than assuming the grid holds.
6. Keep it accessible by construction: semantic landmarks and heading order, labelled controls, visible focus, adequate contrast, real alt text, and no meaning carried by color alone. Respect reduced-motion preferences.
7. Do not expose secrets through public environment variables, and do not embed third-party trademarks, logos, or brand assets the project has no license to use.
8. Inspect the result in a real browser at each verified width, then run the web gate from `AGENTS.md`: lint, typecheck, tests, and build.
9. Invoke `$design-review`/`/design-review` before shipping, address valid findings, then continue the chain to `$review-pr` and `$ship`.
