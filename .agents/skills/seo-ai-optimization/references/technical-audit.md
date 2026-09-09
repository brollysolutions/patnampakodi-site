# HTML and production checks

## Passive local inventory

Read a supplied HTML file before rendering it. The bundled helper inventories
source evidence using Python's standard library:

```text
python <skill-directory>/scripts/audit_html.py <supplied-page.html>
```

Use the environment's existing Python runner (for example `uv run --no-project
python`) when required. It prints JSON, never edits the input, never loads
remote assets and never executes page scripts. It accepts one UTF-8 HTML/HTM
file up to 2 MiB. A successful exit means extraction succeeded, not SEO passed.

The inventory includes title, description, canonical and robots declarations,
headings, links, image alt attributes and JSON-LD syntax/types with source
lines. Source elements are not proof of rendered visibility. Review the raw
file for templates, hidden content, competing metadata and malformed markup;
the helper is not a browser, HTML conformance checker or structured-data
eligibility validator. Do not feed it unrelated private files.

For Markdown/prose, inspect headings, links, facts and frontmatter directly.
Do not call Markdown metadata rendered HTML or infer production responses from
it. Preserve frontmatter and code fences when editing; snippets containing HTML
are examples unless the user identifies them as page source.

## Check only what the evidence can establish

| Area | Local/content check | Live/build evidence when available |
| --- | --- | --- |
| Title/snippet | Accurate distinct title/description, heading agrees with offer | Rendered head and actual search appearance; engines may rewrite snippets |
| Page structure | Clear main heading, useful hierarchy and readable answers | Mobile DOM, accessibility and important content without interaction |
| Index eligibility | Canonical and robots declarations | HTTP/redirect chain, X-Robots-Tag, robots.txt, status, CDN behavior, Search Console inspection |
| URLs/links | Existing route mapping, descriptive internal links and relevant destinations | Broken links, redirect loops, sitemap/canonical consistency and crawlable anchors |
| Schema | Parse JSON-LD; match facts and type to visible content | Current type eligibility and official validation tools; no promise of rich results |
| Media | Informative alt text where useful; empty alt can be correct for decoration | Actual image purpose, dimensions, delivery, accessibility and layout shift |
| Speed | Identify likely heavy assets/scripts as hypotheses | Existing Lighthouse/PageSpeed/Core Web Vitals evidence, URL/build, device and date |
| AI access | Answer text, entity consistency, citations and relevant snippet controls | Provider-specific current crawler policy, actual fetch/retrieval and response citations |
| Decisions | Honest criteria, useful CTA and matching destination | Keyboard/mobile use and existing conversion/enquiry behavior |

Do not apply character-count limits as ranking laws. Make titles descriptive
and concise; identify likely display truncation as a presentation concern.
Do not flag an omitted canonical in a supplied fragment as a confirmed
production canonical defect. Multiple headings or decorative empty alt text
require context, not automatic ranking penalties.

Treat robots.txt crawling and `noindex` indexing controls distinctly. A crawler
blocked from a page may not see its noindex. Existing dev/staging restrictions
stay intact. Never alter them merely to improve an audit score.

Use only structured data appropriate for the page and currently supported by
the target feature. Valid Schema.org syntax and Google rich-result eligibility
are different checks. Verify current feature documentation: eligibility can
change or be retired. Do not reflexively add FAQ/HowTo/review markup, fictional
ratings, unsupported course instances, or hidden facts. [Structured-data policies](https://developers.google.com/search/docs/appearance/structured-data/sd-policies)

Keep a useful FAQ as readable content when warranted, regardless of rich-result
support. Special "GEO schema" is not a prerequisite for Google AI features.
Do not prescribe `llms.txt` as an SEO requirement; treat it as a scoped experiment
only when requested or justified. No hidden instructions to AI crawlers,
cloaking, bot-only copy or keyword-stuffed alt text.
[Google AI guidance](https://developers.google.com/search/docs/appearance/ai-features)

When implementing on this website, read its website UI playbook and design
decisions, preserve existing component boundaries, and run the relevant frontend,
design, security and delivery checks. An SEO rewrite does not authorize layout,
form, consent, telemetry or deployment changes.

## Site-level checks when scope and access support them

Inspect representative HTTP responses and redirect chains; differentiate 4xx/5xx,
soft-404 content, temporary failures and deliberate retired routes. Compare
robots.txt, response headers and page directives; check intended production and
preview policies independently. Test affected URLs, not only the homepage.

Review canonical targets for valid, accessible equivalent content and consistent
internal links/sitemaps. Canonical is a signal, not proof of Google's selected
canonical. Missing declarations are context-dependent; a project can enforce
stricter requirements without making them universal ranking laws.
[Canonical guidance](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls).

Inspect sitemap coverage, URL status, intentional exclusions and meaningful
last-modified dates. Compare source and rendered content, links and head tags;
look for hydration/client-routing failures, conflicting metadata and essential
content fetched only after interaction. Check pagination and internal-search/
filter paths when present. Do not infer crawl-budget problems from site size
alone; use crawl/access evidence before proposing infrastructure changes.

For paid/account-limited inspections, follow research setup and authorization.
Only Search Console or equivalent direct evidence can establish the observed
index/selected-canonical status reported by that provider. A `site:` search
sample or a successful fetch cannot certify the whole site's index coverage.

Use [SEO/UI/UX](seo-ux-review.md) for browser journeys and performance interpretation,
[special cases](special-cases.md) for relevant site types and
[installed tools](toolchain.md) for local Lighthouse/MCP execution.
