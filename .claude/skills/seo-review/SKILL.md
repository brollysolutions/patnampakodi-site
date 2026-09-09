---
name: seo-review
description: Audit a public web page change for search visibility, indexability, metadata, structured data, internal linking, and speed regressions before it ships. Use after any change to a public route, page copy, heading, metadata, sitemap, robots, redirect, structured data, image, font, script or performance budget, and whenever the user asks for an SEO review, a ranking check, or whether a page is search-ready.
---

# SEO Review

Read-only audit of what a crawler will actually receive. Rankings cannot be
verified from a checkout; indexability, metadata, content rendering, links and
speed can.

For competitor/keyword research, existing-content strategy, writing or
AEO/GEO/LLMO analysis, use the shared `seo-ai-optimization` skill's relevant
procedures. Use `lighthouse-audit` for measured browser checks when configured.
These extend the audit; they do not replace this project's public-page gates.

1. Read `docs/agent-context/web-seo-playbook.md`, the route manifest, the changed
   files, and the redirect table. List every public URL the diff touches, including
   pages that inherit the change through the layout or shared components.
2. Build the indexable production build (`SITE_INDEXABLE=true`) and serve it. Run
   `python scripts/check_seo.py <base-url> <paths...> --canonical-origin <production-origin>`
   for every touched URL, adding `--expect-text` for copy the change introduced and
   `--require-type` for structured data it promises. Run the web smoke, accessibility
   and Lighthouse suites when the change can affect them, or say exactly why not.
3. Audit against the playbook and report each hit as `file:line` or `URL`:
   - **URLs and redirects** — preserved slugs; no fragment or query destinations;
     308 only for final destinations, 307 while content is pending; retired paths
     404/410; every internal link resolves 200 without a redirect hop.
   - **Metadata** — unique title within 60 characters and description within 160,
     self-referencing canonical, Open Graph title/description/url/image, Twitter card,
     the route registered in the manifest and the sitemap with a real `lastModified`.
   - **Content** — exactly one server-rendered H1 carrying the primary keyword,
     semantic heading order, curricula/FAQs readable without JavaScript, no
     placeholder or draft markers, only confirmed facts.
   - **Indexability** — production crawlable except the API; previews and dev hosts
     carry `X-Robots-Tag: noindex` and a closed robots.txt; page metadata never
     sets noindex on production.
   - **Structured data** — built only from the reviewed builders; allow-listed
     keys; no ratings, reviews, awards, counts, addresses or scheduled instances the
     business has not confirmed; every block parses.
   - **Speed** — Lighthouse budgets unchanged and met on the production build; no new
     font, animation library, UI dependency, tracker or autoplay media; images local,
     optimised, sized and lazy below the fold; marketing links `prefetch={false}`;
     no `content-visibility` containment without verified no-JavaScript journeys.
   - **Interstitials** — enquiry prompts small, non-modal, closable, never covering
     the page on arrival.
4. Hand accessibility, responsive and design findings to `$design-review`; do not
   duplicate them here.
5. Separate the findings into two ordered lists: **indexability and correctness
   defects** (a crawler or a budget will fail; not negotiable) and **search
   optimisation suggestions** (a judgment against the playbook). Each finding needs
   the location, what renders now, what the playbook expects, and the smallest fix.
6. State plainly what was not verified: budgets not measured, hosts not checked,
   field Core Web Vitals unknown. Never claim a ranking outcome; say "technical
   SEO checks pass" when they do.
7. If there are no findings, say so explicitly and list the URLs, commands and
   evidence reviewed.

Do not edit during a review-only request. Inside `$work-feature`,
`$systematic-debug` or `$design-create`, fix valid findings, re-run the affected
checks, and repeat this review before continuing to `$review-pr` and `$ship`.
