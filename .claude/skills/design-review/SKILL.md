---
name: design-review
description: Audit changed user-visible web UI for design divergence, accessibility defects, and responsive or state-handling gaps. Use after any change to a page, component, or layout a user sees, and whenever the user asks for design or UI review.
---

# Design Review

Read-only audit of what the change actually renders.

1. Read `.agent-workflow/DESIGN.md` when it exists, the changed files, and the surrounding pages that establish the current visual system. Apply the rules already pinned in this repository; do not fetch replacement design rules at runtime and do not install anything.
2. Identify every user-visible surface the diff touches, including states the diff changes indirectly.
3. Audit against this checklist and report each hit as `file:line`:
   - **System divergence** — tokens, spacing, type scale, radius, shadow, or color used outside the established system; a new primitive that duplicates an existing one.
   - **Hierarchy and rhythm** — heading order, emphasis competing with itself, inconsistent density or alignment.
   - **States** — missing loading, empty, error, long-content, or truncation handling.
   - **Responsive** — overflow, cramped or stranded layout, or a tap target under the minimum size at any supported width.
   - **Accessibility** — heading order, landmarks, control labels, focus visibility and order, contrast, alt text, meaning carried by color alone, and reduced-motion handling.
   - **Correctness** — a control that does nothing, a link to nowhere, mismatched copy, or a hidden control mistaken for an access control.
4. Use the installed `apple-design` skill to verify the Taste/Impeccable/Kowalski
   result. Read relevant sections actually available in the skill. Check feedback,
   spatial continuity, interruption/reversal, gesture velocity, restraint,
   typography, layout and reduced motion where applicable. Verify control semantics
   and focus: press feedback must not change activation behavior. The brief, brand
   and approved design remain authoritative; native conventions are not automatic
   web requirements. If the skill or browser evidence is unavailable, label that
   verification unverified and name the missing layer. Do not claim it passed or
   install tools as an incidental review action. Existing setup approval persists.
5. Separate the findings into two ordered lists: **design divergence** (a judgment against this project's system) and **accessibility or correctness defects** (objectively wrong). Do not blur the two — the second list is not negotiable, the first is.
6. Each finding needs a precise location, what renders now, what the system expects, and the smallest fix. Skip anything you did not actually verify in the code or the browser.
7. If there are no findings, say so explicitly and list what was not verifiable — the widths not checked, the states not reachable, the browser not run.

Do not edit during a review-only request. Inside `$design-create` or `$work-feature`, fix valid findings, re-verify the affected widths and states, and repeat this review before shipping.
