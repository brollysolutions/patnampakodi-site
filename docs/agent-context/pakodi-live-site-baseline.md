# Live-site migration baseline

Read-only retrieval on 2026-09-09. Source: the user-supplied
[Patnam Pakodi homepage](https://patnampakodi.com/). This records observed public
HTML only; it is not business approval or a complete technical SEO audit.

## Observed in this session

- HEAD and GET succeeded with HTTP 200. Response identifies Apache and links to
  WordPress REST page 660. No hosting/container capability can be inferred from
  an HTTP response.
- Homepage HTML contains `<meta name='robots' content='noindex, nofollow' />`.
  This is an immediate indexability defect if the public site is intended to
  appear in search. Do not claim all pages share it without checking them.
- Canonical: `https://patnampakodi.com/`; H1 extracted as `Patnam Pakodi`.
- Navigation links establish the following migration candidates:

| Observed path | Proposed treatment | Verification status |
| --- | --- | --- |
| `/` | Preserve homepage URL; remove accidental noindex only in an authorized production change | HTTP 200 and HTML inspected |
| `/about-us/` | Preserve story page | Link observed; destination not fetched |
| `/menu/` | Preserve outlet menu | Link observed; destination not fetched |
| `/branches/` | Preserve locator entry point | Link observed; destination not fetched |
| `/franchise/` | Preserve franchise page | Link observed; destination not fetched |
| `/shop/` | Preserve packaged-product shop | Link observed; destination not fetched |
| `/contact/` | Preserve contact page | Link observed; destination not fetched |

The homepage also links to WordPress feeds, REST endpoints and uploaded logo
icons. Those are system/asset URLs, not automatically replacement public pages.
Inventory usage before deciding whether to retain or retire each.

## Still required before a replacement launches

Fetch robots.txt and all sitemap indexes; enumerate pages, products, categories,
pagination, policy URLs and media landing pages. Reconcile with an authorized
WordPress export and Search Console landing-page data if supplied. Check every
URL status/canonical/indexability and relevant backlinks. Keep matching slugs
where possible; create specific approved permanent redirects otherwise. Do not
redirect every retired URL to the homepage or claim this seven-path list covers
all existing URLs.

Reconfirm canonical contact, legal and product facts with FRAB. The adjacent
Brand Data Document's warnings are historical source reports, not fresh
verification of all listed pages, menu counts, SKU values or outlets.

## Evidence and limits

The public homepage response is retained only in the ignored local
`.agent-workflow/pakodi-live-home.html`; source HTML and third-party assets are
not redistributed. The standard web fetch failed, and the Playwright navigation
attempt did not provide usable browser evidence; curl retrieval succeeded after
network escalation. No rendered layout, accessibility, Lighthouse, Search
Console, field performance or production configuration was verified or changed.
