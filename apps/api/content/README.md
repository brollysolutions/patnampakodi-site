# Initial public content

## Current editorial update — 2026-09-15

The owner now focuses on four dry chicken pakodi flavours and Kukatpally as the
only serving branch. This supersedes the historical menu and six-branch notes
below. The expanded pages and franchise inclusions use the live site and supplied
brochure with conflicts recorded in
[`kukatpally-site-expansion.md`](../../../docs/agent-context/kukatpally-site-expansion.md).

For an existing database, run `python -m app.seed --site-expansion`. It validates
and updates the 16 approved brand, page, menu, franchise and Kukatpally records,
unpublishes other menu/outlet listings, and preserves historical payloads,
products, stock, orders and legal content. Repeating it is safe. The general
seed still preserves existing records unless an explicit update flag is used.

## Historical source observations

Update 2026-09-10: the user explicitly requested the existing public site's copy,
images, page order and interactions with this project's fonts/colors. The page
`blocks` now preserve that observed source copy, including its conflicting body
and footer contact details. They supersede the earlier rewritten composition.
The source facts are observational, not independent verification; no copied
review/rating claims are promoted to aggregate-rating structured data. The
publication gates for sellable products and approved seller settings remain.
Original images are recorded under `apps/web/public/images/live/PROVENANCE.json`.

`catalog-source-inventory.json` preserves the seven original product URLs and
their category/tag paths, titles and artwork. It is an observation inventory,
not seed data. The source's displayed prices and body tax notes conflict, and
required food/seller information is incomplete. An operator must supply approved
product and tax records before publication. Four original pack images are kept
locally with hashes; adding an image does not approve its printed claims.

The private `/v1/admin/catalog-drafts` endpoint combines these seven observations
with the 51 published menu records into **57 setup templates**: 53 fresh foods
and four ready mixes. The Pachi Mirchi menu flavour reuses its original product
URL, avoiding a duplicate. Templates contain known identity and artwork only;
they do not insert purchasable variants or invent prices, stock or food/tax data.
Only the seven product-specific source observations supply automatic images.
The menu cards repeat generic pakodi photographs for other foods, including
drinks and dips; those photographs must not become their sale images. Other setup
entries use neutral icons until an operator chooses an approved photo in Media.
The admin Products form requires the remaining information. Existing variants
are filtered using the request's normal brand-scoped database connection and
are never overwritten. The public storefront still reads its published database
records and does not use these templates as fallback content.
Menu cards and branch sections bind to their published CMS records. The branch
contact details displayed in the source are imported as editable editorial
content; they do not establish verified locations and are not promoted to
FoodEstablishment structured data. Earlier withholding notes below describe the
initial MVP snapshot, before the user's exact-content instruction.

`storefront.json` is the reviewed initial content input, not a runtime fallback.
`python -m app.seed` validates it and inserts into PostgreSQL, preserving existing
records. `--replace` explicitly overwrites the matching seed records. The web
application reads only the API and never imports this seed file.

Source: user-supplied patnampakodi.com, its homepage/menu retrieved 2026-09-09,
and the design brief's adjacent Brand Data Document v1.1. Names/categories and
published outlet localities/pincodes are carried forward; page descriptions and
editorial copy were written for this design. Contact email was freshly observed
in the homepage's mailto link. Ambiguous phones, street addresses, hours,
franchise prices/terms, ratings, statistics, policy text and food-commerce data
are withheld pending business confirmation. No FoodEstablishment/Product
structured data is emitted from these incomplete records.

The six published locality records support map search, not a promise of current
opening hours or verified coordinates. The menu remains display-only, with
unknown prices, dips/drinks dietary facts and allergens explicitly directed to
the store. Junnu remains in the source's Drinks category until taxonomy is
approved. This is not completion of the priced/compliant commerce catalog.

The unpublished product is an explicit non-customer fixture exercising the draft
boundary. Production product publication requires schema validation, complete
food information and separately approved data. The commerce MVP adds authenticated
editorial controls and staff-approved delivery requests; this seed does not enable
sales or populate approved seller/tax settings.
