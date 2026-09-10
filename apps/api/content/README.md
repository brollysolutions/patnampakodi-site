# Initial public content

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
