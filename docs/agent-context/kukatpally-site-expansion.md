# Kukatpally website expansion

Authority: owner's 2026-09-15 instruction to expand each page, enhance the logo,
keep FAQs open, consult the live website and brochure, and ask for more details.
Only Kukatpally is currently serving. This supersedes the earlier preservation
of six published outlet listings in four-flavour-menu.md.

## Sources and conflicts

- Retrieved https://patnampakodi.com/ and /about-us/, /menu/, /franchise/,
  /branches/, /contact/ directly on 2026-09-15. The external web reader failed;
  direct HTTPS returned 200. The site is the older shopping-led implementation.
- The live story describes Guntur-style chicken pakodi, Hyderabad roots and a
  standardized preparation/training model. Use those themes without repeating
  fastest-growing, guaranteed quality/profits or invented founder milestones.
- Live six-branch listings, 25+ branches, ratings/testimonials, 50+/60+ menu
  counts, delivery availability and future cities are superseded or unverified.
- The supplied brochure is the ten-page PDF documented in four-flavour-menu.md.
  Pages 2-6 support Brand-Only Rs 69,000, Cart Rs 99,000, Cabin Rs 1,50,000 and
  Shop Rs 3,00,000 with setup, equipment and branding inclusions. Pages 7-8
  illustrate brand materials; page 9 is a proposed space plan, not an actual
  Kukatpally floor plan. Page 10 supplies central contact information.
- Brochure food expansions and menu-board prices do not establish the current
  menu. Only the four approved pakodis appear as food offerings. Franchise
  equipment examples are clearly package details, not extra menu items.
- Live Kukatpally listing: Plot 42, KPHB Main Road, Kukatpally, Hyderabad 500072;
  11 AM-11 PM; +919000366219. Owner asked to confirm address, map pin, hours
  and phone. Until corrected, label these as the current website listing and
  encourage a call before travel. Do not confuse the brochure's central office
  at Dr Atmaram Estates with the food branch.
- Ask about founder/year, unique food details and franchise terms. Omit missing
  facts, fixed launch times, financial returns, royalty and territory promises
  until the owner supplies current details.

## Design and behavior

The owner selected **Premium editorial** after requesting stronger design and
research across the installed design skills. Use warm peach/orange, existing
Poppins/Inter, generous editorial spacing and large photographic menu features.
Review covered Taste direction, Impeccable layout/craft/adaptation, frontend-design
composition/copy, Kowalski motion decisions and Apple accessibility/color/layout/
typography. Dishoom's live homepage was inspected for narrative pacing and food
imagery only; its content, assets and design are not copied. Refine the existing rooster identity and header
lockup. No extra motion or dependencies. Reuse representative food illustrations
and identify them as illustrations. Do not fabricate branch/team photography.

Native FAQ disclosures render open by default and may each be closed/reopened
independently. Answers and links are server-rendered. Preserve historical outlet
URLs with a truthful noindex notice and link to Kukatpally; omit them from current
branch discovery and sitemap. Private operations remain unchanged.

The owner clarified that the pakodi is **dry** after asking whether the generated
images matched the flavours. A fresh live-image comparison found the homepage's
Pachi Mirchi label on a reddish glossy generic picture, with no reliable visual
reference for all four current flavours. The earlier product observations reused
one staff-serving image across three products. These do not establish actual
flavour appearances. Four images remain explicitly representative; the new table
scene was revised for a dry, crisp coating. Exact colours, garnish and portions
remain unverified rather than inferred as recipe facts.

The refined badge and responsive table image are local WebP assets. The full
generation prompts and input references are recorded in
[editorial image provenance](../../apps/web/public/images/live/EDITORIAL-PROVENANCE.md).
The final hero uses the dry-coating correction; the initial composition is not
served. No new image processing dependency was added.

## Update procedure

Use `python -m app.seed --site-expansion` for an existing database. The explicit
transaction validates and applies 16 approved brand/page/menu/franchise/Kukatpally
records, and unpublishes other outlet listings without deleting their payloads.
It preserves products, stock, orders, legal content and private operational data.
The older `--menu-launch` command retains its narrower behavior. New installs
seed only Kukatpally as published. No schema or generated contract change.

## Delivery evidence

Implementation and review are complete. Fresh verification passes 132 API tests,
27 web unit tests, 76 browser tests, seven-page technical SEO and all six
Lighthouse medians in the final 18-run container batch. Workflow checks pass
150 tests and 22-skill validation. Intentional skips: two browser viewport
duplicates and three platform-specific workflow cases. See feature-status.md for
the exact results, initial failures and retained outliers. Implementation
`f91ce5a` is in [PR #23](https://github.com/brollysolutions/patnampakodi-site/pull/23).

Code/security/design review found no unresolved defect. Chromium review includes
1440/768/390/320px, all food images, keyboard toggles and open no-JavaScript FAQs.
Native Safari, deployment and field vitals are unverified. The generated food
appearance and listed branch details still need owner confirmation.
