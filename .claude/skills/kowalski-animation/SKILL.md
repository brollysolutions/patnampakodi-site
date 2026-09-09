---
name: kowalski-animation
description: Apply Emil Kowalski's pinned web animation skill during requested UI/UX design and animation work. Decide whether motion helps, then choose tools, properties, timing, interruption, exit and reduced-motion behavior. Use with Taste and Impeccable, followed by Apple Design verification. Existing-motion reviews stay read-only unless fixes are requested.
---

# Kowalski animation for the shared design workflow

This is the MIT-licensed `animate` skill from `emilkowalski/skills`, adapted under
a discoverable name. `SOURCE.json` records the revision. Read relevant parts of
[the original skill](references/upstream.md) and use
[its recipes](references/RECIPES.md) for matching components.

Run the motion decision during every requested UI/UX design. Using this skill
does not require animation: frequent actions, reduced-motion preferences,
performance limits or a quiet direction may favor instant state changes.

1. Identify frequency and purpose: feedback, spatial continuity, state change,
   explanation or occasional delight. Motion must serve the actual user task.
2. Reuse component primitives and motion tokens. Choose the simplest suitable
   tool: CSS, WAAPI or an already reviewed spring/gesture library. References to
   other skills/packages do not authorize installing them or changing the stack.
3. Define properties, origin, easing and duration or spring behavior. Prefer
   inexpensive properties and verify performance. Source GPU/compositor claims
   and numeric ranges are guidance, not guarantees across browsers and versions.
4. Handle retriggering, interruption, reversal and exit coherently. Gesture
   feedback starts from the visible state and retains velocity where appropriate.
   Preserve focus management and semantic control activation.
5. Provide suitable reduced-motion behavior, including no animation when needed.
   Gate hover for appropriate input devices. Essential content remains usable
   without an entrance animation completing.
6. Check keyboard, pointer/touch, repeated actions, reduced motion and responsive
   states. A still screenshot cannot prove motion quality or interaction behavior.
7. Coordinate with Taste and Impeccable, then use Apple Design to verify feedback,
   continuity, interruption, restraint and accessibility.

Preserve the brief and design system when they differ from a source example.
No library, font, remote asset or tracking script is added solely for a recipe.
Keep SEO headings, content and links accessible and honor performance budgets.
Report the motion/no-motion decision and checks actually performed; missing
browser/device evidence remains unverified. Implementation finishes through
design-review, applicable SEO checks, review-pr and ship. Audits do not edit.
