---
name: design-create
description: Build or redesign requested web UI/UX against the approved direction and existing design system. Use for public pages, marketing surfaces, product interfaces and components when the direction is settled. Apply Taste, Impeccable and Kowalski, then Apple Design verification.
---

# Design Create

Implement an approved direction with the system that already exists.

Use all three requested skills: `design-taste-frontend` for direction,
`impeccable` for structure/refinement, and `kowalski-animation` for the motion
decision and behavior. Follow `docs/agent-context/design-skills.md`; use relevant
sections and preserve existing user approval. No added motion is a valid outcome.

1. Read `.agent-workflow/DESIGN.md`, the affected route end to end, and the existing tokens, fonts, spacing scale, and component primitives. Find the closest existing page and match it before inventing anything.
2. State one design read before editing: page kind, audience, the trust constraint the page carries, and the visual language in use. If the direction is not settled, stop and invoke `$design-reference`/`/design-reference` instead.
3. Reuse existing tokens, fonts, and primitives. Introducing a new token, font, animation library, or UI dependency is a reviewed decision, not a detail — raise it and justify it before adding it.
4. Ship the smallest complete change. Complete means every state is handled: loading, empty, error, long content, and truncation.
5. Build responsively from the smallest supported viewport up. Verify the layout at narrow, medium, and wide widths rather than assuming the grid holds.
6. Keep it accessible by construction: semantic landmarks and heading order, labelled controls, visible focus, adequate contrast, real alt text, and no meaning carried by color alone. Respect reduced-motion preferences.
7. Do not expose secrets through public environment variables, and do not embed third-party trademarks, logos, or brand assets the project has no license to use.
8. Inspect the result in a real browser at each verified width, then run the web gate from `AGENTS.md`: lint, typecheck, tests, and build.
9. Invoke `$design-review`/`/design-review` with the installed `apple-design` skill,
   address supported findings, run `$seo-review` for public surfaces, then continue
   to `$review-pr` and `$ship`. State browser/device or Apple evidence gaps.
