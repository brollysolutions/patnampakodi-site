# SEO-focused UI/UX review

Review the journey from a search promise to understanding and action. Use the
existing design system and page constraints. A visual preference is not an SEO
defect; distinguish crawl/retrieval, usability, accessibility and conversion
mechanisms. Good Core Web Vitals matter, but a perfect score does not guarantee
rankings. [Google page experience](https://developers.google.com/search/docs/appearance/page-experience).

## Establish what can be observed

Record URL/build, device/viewport, browser, date and state. Inspect source and
rendered output when available. Screenshots support visual observations; DOM,
keyboard and browser behavior require their own checks. Mark unavailable layers
unverified instead of claiming a visual mockup passes accessibility or SEO.

For each important template, follow representative journeys: search landing to
answer, comparison to decision, and CTA to the next meaningful step. Do not
submit real enquiries/orders, send messages or enter private data just to test
a public page. Use an existing test environment for end-to-end submission.

## Information architecture and content layout

| Area | Review | Evidence or acceptance criterion |
| --- | --- | --- |
| Arrival | Title/snippet promise agrees with heading, offer and location | Reader can identify the subject and next step without hunting through slogans |
| Main content | Useful answer, context and caveats appear in a sensible order | Key text exists in readable DOM; no text-only-in-image replacement |
| Headings | Visual hierarchy and semantic hierarchy agree | Headings label real sections; CSS is not used to disguise heading purpose |
| Navigation | Descriptive links, breadcrumbs where useful and relevant related pages | Important destinations use crawlable links and have an understandable path |
| Long content | Helpful sections, anchored contents when warranted, readable measure | Reader can find a section; sticky UI does not conceal the destination |
| Comparisons | Same dimensions, units, caveats and genuine tradeoffs | Table headers/relationships survive responsive presentation |
| Disclosures/tabs | Content remains accessible and controls convey state | Do not require interaction to fetch essential indexable facts; verify actual rendering |
| Trust and decisions | Confirmed identity, terms, evidence and suitable next action | Qualifications stay beside claims; fake badges/social proof are absent |
| CTA | Label describes outcome and destination matches the promise | Action remains usable on narrow screens and with keyboard navigation |

Ordinary accessible accordions are not automatically hidden-text spam. Test
whether content is present and reachable before recommending their removal.
Google can render JavaScript; source-only absence is a rendering concern to
investigate, not proof that indexing is impossible. Prefer robust server/static
content when it fits the architecture. Do not introduce a framework rewrite
solely to satisfy a checklist.

## Responsive and accessibility checks

Use WCAG 2.2 AA as the review target unless the project specifies otherwise.
Consult the criterion and exceptions when making a conformance finding. Check
keyboard operation, visible/unobscured focus, accessible names, labels/errors,
contrast, zoom/reflow, image purpose and modal behavior. Common numeric anchors
are 4.5:1 text contrast (3:1 for large text), reflow at 320 CSS pixels with
exceptions for content requiring two dimensions, and 24 by 24 CSS-pixel target
size or the criterion's exceptions. Automated scans cover only part of a review.
[WCAG 2.2](https://www.w3.org/TR/WCAG22/).

Use narrow mobile, a representative mobile viewport, tablet and desktop when
relevant to the layout; include zoom and long-content/error states. A viewport
list alone is not evidence: record the action and observed result. Check sticky
headers/CTAs, consent notices, menus, tables and form errors for overlap. Respect
reduced motion and avoid motion that obstructs the task.

Evaluate font loading, text size/line length and spacing as usability choices
with the project's design system. Avoid declaring one font size, whitespace
amount, “above the fold” formula or number of clicks a universal ranking rule.

## Performance and media

Use Lighthouse for repeatable lab diagnostics, and field data when available.
Record environment and artifact paths; use the installed toolchain procedure.
Current good Core Web Vitals thresholds are LCP <= 2.5 s, INP <= 200 ms and
CLS <= 0.1 at the 75th percentile, segmented by device. Missing field data stays
unknown. Lab TBT is a diagnostic, not measured field INP.
[Core Web Vitals](https://web.dev/articles/vitals).

Trace actual problems: large LCP image, late discovery, blocking font/script,
long task, layout shift or excessive work. Suggest a measured fix and rerun the
same conditions. Size images to prevent shifts; reserve space for embeds; avoid
lazy-loading the observed LCP image while using appropriate below-fold loading.
Keep budgets specific to the project. Do not invent a universal Lighthouse
score requirement or claim one run proves production performance.

## Conversion without misleading ranking claims

Review required fields, instructions, error recovery, clear inclusions/exclusions,
comparison fairness and CTA relevance. Preserve consent/legal requirements.
No fake urgency, fabricated scarcity, deceptive buttons or forced lead capture
before a promised answer. Do not treat bounce rate, dwell time or conversion
rate as a proven direct ranking mechanism.

Use existing aggregated conversion data when available. A proposed layout lift
is a hypothesis until measured. New trackers, events, session recordings or
experiments are separate implementation work, not an incidental audit step.

## Finding format

Record page/component, viewport/state, screenshot/DOM/metric evidence, the
affected task, mechanism, severity/confidence, smallest appropriate change and
observable verification. Deduplicate shared-template defects and list affected
URLs. Explain when layout tradeoffs need a user choice; finish all independent
analysis first. Audit mode reports findings; implementation mode follows the
target project's frontend, design, SEO, security and delivery procedures.
