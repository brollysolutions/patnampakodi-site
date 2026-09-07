---
name: design-reference
description: Choose a visual direction for a public or marketing web page before any UI is built. Use when the look, feel, or visual language of a page is unsettled, when the user asks for design options or inspiration, or when a redesign has no agreed direction yet.
---

# Design Reference

Settle the visual direction before code. This skill produces a decision, not an implementation.

1. Read `.agent-workflow/DESIGN.md` when it exists, the affected route, and the existing design tokens, fonts, spacing scale, and primitives. Establish what visual language already exists before proposing a new one.
2. State the design read in one short paragraph: page kind (marketing, product, docs, transactional), audience, the trust constraint the page carries, and the visual language currently in use.
3. Propose **at most three** directions. For each give a name, the principle behind it, the type and color treatment, layout rhythm, motion posture, and the kind of page it suits.
4. Describe transferable principles only — hierarchy, density, contrast, restraint, rhythm. Never copy or reproduce another company's trademarks, logos, wordmarks, distinctive brand assets, or overall trade dress, and never describe a direction as "make it look like <brand>".
5. Note for each direction what it costs: new tokens, new fonts, added dependencies, accessibility risk, and how reversible it is.
6. Recommend exactly one direction with a one-sentence reason grounded in the page's purpose, not in taste.
7. Record the accepted direction in `.agent-workflow/DESIGN.md` once the user approves.
8. Stop at the recommendation and ask for approval. Do not edit implementation files, commit, push, or open a PR during this skill.

After approval, hand the direction to `$design-create`/`/design-create`.
