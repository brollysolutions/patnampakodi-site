# Patnam Pakodi website design direction

## Superseding user correction - 2026-09-11

Keep the original site's colors and fonts as well as its content and layout.
The full ecommerce journey remains required. This replaces the earlier instruction
to apply our fonts/colors and the historical locked identity below.
Fresh browser computed styles on https://patnampakodi.com/ and /shop/ show:
Poppins for body, controls and editorial headings; Inter for shop headings;
peach `#FEF1E4`, body `#353535`, heading `#1C1C1C`, orange `#FF6210`,
red `#C0392B`, gold `#F39C12` and white. Use locally served licensed fonts.
Retain these colors while pairing orange/gold with dark text for accessible
controls; the source's small white-on-orange/gold labels fail contrast.
Taste: preserve source identity and composition. Impeccable: clear Shop/Cart
entry points and legible responsive type. Kowalski: instant feedback, no added
decorative motion. Verify through Apple guidance, browser/axe and SEO gates.

## Superseding instruction — 2026-09-10

The user approved reproducing patnampakodi.com in Next.js, keeping its original
copy, images, layout, sections, navigation and URLs, with **our fonts and colors
only**. This replaces the earlier food-led composition below. The scope includes
the whole ecommerce journey and admin dashboard. Keep the original logo and
franchise-led homepage; use Abril Fatface/Archivo and existing palette tokens.
Phone-first enquiry/brochure popups are explicitly approved; open only on user
activation, with native dialog semantics, escape dismissal and focus restoration.
This is an authorized exception to the generic no-modal design advice.

Taste: preserve the established franchise-led composition. Impeccable: retain
responsive hierarchy and complete interaction states. Kowalski: immediate state
changes, no decorative motion or new animation dependency. Apple/browser evidence
will be recorded after fresh review. Source contact discrepancies remain recorded
for owner correction; copying source copy does not verify factual claims.

Derived 2026-09-09 from the user-supplied
[design brief v0.2](patnam-pakodi-design-brief-v0.2.md).
Status: **The Pakodi Table direction approved by the user's proceed instruction
on 2026-09-09**, including cream, the first storefront slice and public-only
search indexing. Source business-data gaps remain unresolved. Implementation
and browser evidence are recorded separately from this approval.

## Design read

The 2026-09-10 MVP extends this direction to product, cart, private order and admin
screens. Reuse cream/white panels, existing local fonts and brown compact controls.
Use labelled native forms, visible waiting/error/success text, static status
changes, 48px inputs and stacked mobile layouts. No animation library is needed
for frequently repeated operational tasks. Policy/outlet/product pages inherit
public metadata; cart/tracking/admin remain private and use nonce CSP. Optional
analytics consent is a small, nonmodal footer preference, never an order overlay.

Public food storefront and franchise marketing for customers choosing a snack
or packaged mix and entrepreneurs considering an outlet. The trust requirement
is accurate food, price and franchise information. The proposed visual language
is warm, typographic and food-led, with Abril Fatface display headings, Archivo
controls, brown structure and restrained orange actions.

## Locked identity

- Brand spelling: **Patnam Pakodi**.
- Display: Abril Fatface 400; no simulated bold/italic and no text below 24px.
- Body/UI: Archivo 400/500/600/700, with 400 italic when used.
- Mandarin Orange `#EB6637`; Zinnwaldite Brown `#2B1406`.
- Orange-filled buttons: white Archivo 700 at **19px or larger**. Compact
  controls use brown/white or an orange outline with brown text.
- Small orange text is unsuitable on white. Orange text is unsuitable on the
  proposed cream surface at any size. Verify actual foreground/background
  combinations, focus outlines and component boundaries in the browser.

## Two viable directions

| Direction | Typography/color and composition | Motion | Costs and reversibility |
| --- | --- | --- | --- |
| **The Pakodi Table — recommended** | Large sentence-case display headline beside one approved close-up food image; cream/white surfaces, brown copy; orange for clear actions. Follow with a readable menu selection, packaged mixes, concise brand story and a distinct franchise section | Immediate content; restrained CSS feedback only where useful; reduced-motion alternative | Uses the brief's proposed cream/support tokens and needs approved food imagery. No motion dependency. CSS tokens make palette/layout adjustments reversible |
| Brown poster | Brown first viewport with white heading and a contained food photograph; orange CTA; white content below; more compact rhythm | Same restrained posture | Uses locked main colors, but full-bleed dark hero is still an open brief choice; higher visual weight and less daylight food context. Same fonts/assets, no extra library |

Recommend **The Pakodi Table** because it lets customers read food and actions
quickly while giving franchise information a distinct, credible place on the
same site. Pakodi Cream `#FBEFD9` is now approved for this storefront.

## Concrete first viewport and page sequence

Desktop: 1280px maximum content width with a 12-column grid and 8px spacing
scale. Header contains brand identity, Menu, Shop, Our story, Find a store and
Franchise links. First viewport uses a seven-column text region and five-column
food photograph. H1 names Patnam Pakodi and chicken pakodi in natural copy;
the roman-script tagline can be supporting text. Primary action: **Explore the
menu**. Secondary action: **Find a store**. Packaged purchasing becomes an active
primary shop action when product records and checkout are ready.

Mobile: identity and accessible navigation, one clear headline, compact food
image and both actions within a comfortable reading flow. Use at least 44px
touch targets, visible keyboard focus and no first-visit modal or scroll lock.

Homepage sequence:

1. Food-led hero and clear customer destinations.
2. Selected menu items with approved names, prices and dietary marks.
3. Packaged mixes with truthful food/price information and shop links.
4. Short brand story, using approved language and no unsupported growth claims.
5. Find an outlet, with link to the full locator.
6. Franchise formats and an enquiry destination, with approved terms.
7. Useful FAQs and contact/policy footer. Testimonials only with approved quotes
   and provenance; no invented stars or ratings.

Keep `/about-us/`, `/menu/`, `/shop/`, `/branches/`, `/franchise/` and `/contact/`
as first-class destinations. Product and outlet detail routes are added after
the complete old URL inventory. Menu and packaged-product purchase journeys
remain clearly labelled. Do not make every card a decorative action.

## Assets and states

The brief reports only a small raster logo and asks for a vector master. Proposed
preview fallback: a plain text brand name using the locked font, explicitly
subject to approval; do not invent an official logo. Final assets require owner
approval, suitable resolution and provenance. No staff photo substitutes for a
product image. Stock/synthetic food imagery must not misrepresent an exact item.

Default proposed shapes: 8px cards/inputs and 16px hero media; compact border
treatments instead of shadows on every section. Self-host the two locked font
families, load only required styles, and review font sources/licenses. No runtime
font CDN. If Telugu script is requested, select a reviewed Telugu-capable fallback.

Forms use real labels, inline error text and a status announcement. Success
means server persistence. Filter/search empty states offer a reset. Unpublished
items cannot be reached by direct URL. Cart updates preserve focus and explain
stock changes. Slow/payment-failure states retain a usable retry path.

## Motion and verification

Taste informed audience-specific typography/composition; Impeccable informed
task order, responsive structure and state coverage. The Kowalski decision is
**no decorative entrance animation, carousel, marquee or parallax**: visitors
need stable food information and fast actions. CSS feedback, if added later,
must have a purpose, support interruption, respect reduced motion and gate hover
by input capability. No motion library is proposed.

The implementation must go through `design-review` with the installed Apple
Design skill, keyboard/touch/no-JS/axe checks and the existing SEO/performance
budgets. Apple/browser/device checks are **not run** for this proposal; no
rendered interface exists. This is a direction for approval, not verified UI.
