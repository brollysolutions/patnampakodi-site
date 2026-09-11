# Approved classic ecommerce redesign

Authority: user planning answers followed by "Start cooking" on 2026-09-11.
This supersedes the franchise-led composition and staff quote requirement for new
purchases. Original Poppins/Inter, logo and peach/orange/charcoal/red/gold identity
remain. Planning and implementation: gpt-6-astra / Extra High recommended;
recommendations do not change selected settings. No delegation is authorized.

## Customer and operational decisions

- Classic food store; fresh and packaged shopping equally visible on home.
- Two modes with independently retained carts; guest checkout and device-local
  favourites, private tracking and reorder against current stock/prices.
- Immediate Razorpay checkout with complete server-calculated total; PIN-code
  delivery rules and fixed fees configured by central staff. No fabricated rates.
- Fresh delivery ASAP from one enabled pilot outlet; weekly India-time hours,
  preparation estimate and pause control. No scheduling, pickup, maps dependency
  or outlet-specific accounts. Existing own-team fulfilment remains.
- Fresh self-cancellation ends when preparation starts; serialize both actions.
  Staff handles later exceptions. Existing packaged cancellation remains.
- Full public and admin redesign. Refine copy, preserve facts and genuine assets.
- Later user correction: remove website content management from the admin panel.
  Keep its navigation focused on store operations.
- Subsequent correction: improve the admin UI and make navigation sticky. Use a
  compact admin header, desktop sidebar/mobile tabs, clearer section and order
  hierarchy, current-view counts, and keyboard/focus clearance under sticky chrome.
  The storefront header is also sticky. Keep actions immediate and preserve all
  operational behaviour and the original identity.
- Use existing referenced images and original logos first. Built-in ChatGPT image
  generation/editing only for a demonstrated asset gap, using inspected references,
  preserving product/brand facts and recording provenance. Keep SVG icons native.

## Page coverage and design procedure

Taste defines identity/composition; Impeccable defines structure/states; Kowalski
defines immediate feedback and brief interruptible CSS transitions, with reduced
motion; Apple Design verifies the browser result. Reuse the stack and dependencies.

Home: hero with both modes, categories, fresh and packaged selections, ordering
explanation, story, outlets, franchise, FAQ, footer. Header has search, mode, PIN,
favourites and cart; mobile has labelled navigation. Fresh menu includes outlet,
opening/paused status and ordering availability. Packaged shop has search/filter/
sort and clear product grid. Details include images, price/portion, ingredients,
allergens and applicable food facts. Cart/checkout show delivery and itemised
totals, recoverable errors and explicit payment confirmation. Tracking includes
timeline, invoice, cancellation, support and reorder. Complete About, Branches,
Franchise, Contact and policy layouts. Admin covers orders, products,
enquiries, messages, reports, media, settings and fulfilment controls.

Every surface covers keyboard/focus, touch, small screens, long content, loading,
empty, error, unavailable and success states. No invented ratings, discounts,
delivery promises or business facts. Original URLs and server-rendered public
content remain; favourites/checkout are noindex.

## Implementation and acceptance

Additive mode/outlet fields and fulfilment rules; automatic checkout quote and
idempotent order creation; server authority over eligibility, totals and stock.
Keep legacy orders and payment links compatible. Reuse 15-minute reservations,
payment ownership, durable signed webhooks, reconciliation and RLS. Contracts are
generated from the server. Exactly one migration head. Never relax security gates.

Sequence: baseline/asset audit, shared system and discovery, commerce and admin,
remaining page coverage, design/security/SEO/code review, full verification and PR.
Investigate existing contact-500/performance failures without relaxing budgets.
Verify fresh/packaged purchases, stale totals, unsupported/closed/pause cases,
independent carts/favourites, replay/races/refunds/recovery, authorization and RLS.
Run full repository gates, browser/axe at desktop/tablet/mobile including 320px and
200% zoom, SEO, Docker acceptance and Lighthouse. Performance >=90, accessibility
and SEO 100, LCP <=2500ms, CLS <=0.1, TBT <=200ms. Record failures honestly.

Approved catalog/seller/tax details, pilot outlet, PINs, fees, hours and estimates
are operator inputs. Persistent staging is never seeded with invented sellable
data. Disposable fixtures may demonstrate populated states and test payments.
Produce a client walkthrough, demo procedure and launch-input checklist, with
clear distinctions between measured readiness and outstanding live acceptance.
