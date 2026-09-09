# Conditional audit extensions

Load the relevant sections only. A full audit means complete coverage of the
actual site, not applying every business model's rules to every page.

## Local businesses and service areas

Verify real locations/service areas, business identity, contact details, hours,
offerings and booking/order/enquiry paths from supplied or public sources.
Audit consistency across the site and accessible official profiles. Suggest
profile corrections without claiming account ownership or making edits.

Research local organic results and map packs separately with explicit location
limitations. Relevance, distance and prominence are documented local factors;
the business cannot manufacture proximity by adding city keywords. Location
pages need real distinct service information, not mass-swapped city names.
Do not invent an address, opening hours, menu, delivery radius, allergen claims,
customer ratings or accessibility facilities. No fake reviews or review gating.
[Google local guidance](https://support.google.com/business/answer/7091).

## Ecommerce, menus and product catalogs

Trace category discovery, filters, product/detail pages, variants, pagination,
availability and action. Inspect actual URLs and crawlable links. Identify
unbounded facets/sorts and inconsistent canonicals without blanket noindexing
useful categories. Product variants can require different treatment depending
on distinct content and search value. Verify price/currency, units, availability,
shipping/returns and structured data against visible confirmed facts.

Out-of-stock and retired items need a business/content decision: keep useful
information, show alternatives or retire with an appropriate destination/status.
Do not redirect all unavailable products to the homepage. Never test purchase
completion or alter catalog/feed settings without scope for that action.
[Ecommerce URL guidance](https://developers.google.com/search/docs/specialty/ecommerce/designing-a-url-structure-for-ecommerce-sites).

## Multilingual and international sites

Map actual language/region URLs. Check reciprocal and self hreflang annotations,
supported language/region codes, appropriate x-default when used, valid targets
and canonical consistency. Distinct translations should not all canonicalize
to one language by default. Verify navigation lets users change language without
forcing location redirects that prevent access. Audit intent, terminology and
commercial details per market; do not reuse metrics as though translation alone
established demand. [Localized-page guidance](https://developers.google.com/search/docs/specialty/international/localized-versions).

## Migrations and major redesigns

Inventory existing valuable URLs from available crawl, search, analytics and
links before proposing the new map. Preserve intent, useful content, metadata,
internal links and canonical consistency. Provide old URL, disposition, new URL,
reason, expected status and validation for each affected path. Redirect to an
equivalent page, not an unrelated category. Keep previews protected; validate
production rules separately. Preserve baseline and define rollback/monitoring.

A design audit does not authorize a migration, canonical policy change or
redirect deployment. Surface the plan and risk in audit mode; in authorized
implementation mode follow the repository's release workflow.

## Consequential or regulated information

For health, financial, legal or safety-sensitive claims, use current authoritative
sources and qualified review when needed. Preserve caveats and jurisdiction or
audience limits. Do not convert marketing copy into individualized professional
advice, or manufacture expert credentials to satisfy a trust checklist.
