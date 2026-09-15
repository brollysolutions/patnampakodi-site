# Four-flavour informational launch

Authority: user instruction and approved plan, 2026-09-15. This supersedes the
shopping-led public design in the earlier ecommerce plan. Navigation is Menu,
Our Story, Franchise, Branches and Contact; the logo links home. Remove delivery
PIN checks, public search, favourites, cart, Shop Packaged, Order Fresh and Track
Orders from public navigation. Fully pause new ordering while preserving existing
records and staff/historical order operations.

The menu shows only Erra Karam Kodi Pakodi, Pachi Mirchi Kodi Pakodi, Miriyala Kodi
Pakodi and Chettinad Kodi Pakodi. The user confirmed the names. Show flavour
descriptions and images without food prices. This editorial menu is independent
of sellable stock and product publication. Preserve the existing peach/orange,
Poppins/Inter identity and use no additional animation.

## Brochure provenance and reconciliation

User-supplied source: `Ptanam pakodi_03.pdf`, ten landscape pages, 20,354,321 bytes.
Source SHA-256: `7ccf024872cf1af7af4a8f96cdf0dbff3976876738feaf2fd7ed062e94a3554c`.
All ten image-only pages were visually inspected. The tracked PDF at
`apps/api/content/patnam-pakodi-brochure.pdf` preserves all ten pages and order,
using compressed page images for the existing download endpoint. It is not a
newly authored brochure or a replacement source of business claims.
Optimized file: 2,187,230 bytes; SHA-256
`f069e01003eeb002d5c72167e6d4779a44c86d44a22a76325935474ad56ad346`.

Page 2 supplies Brand-Only Rs 69,000, Cart Rs 99,000, Cabin Rs 1,50,000 and Shop
Setup Rs 3,00,000; pages 3-6 supply their equipment, branding and kit details.
Page 10 supplies +91 90003 65219, patnampakodi@gmail.com, @patnampakodi and the
central address: 3rd Floor, Dr Atmaram Estates, beside Sri Bhramaramba Theatre,
Metro Pillar No. A689, near JNTU Metro Station, Nizampet X Roads, Hyderabad,
Telangana 500072. These supersede old central marketing contact details. Existing
published branch records remain their own source; the brochure does not establish
new branch addresses or hours. No sales, margin, revenue or return claims added.

## Artwork

Four representative food illustrations were generated with the built-in imagegen
tool at the user's request. They share an overhead bowl composition, warm neutral
background and natural light, differentiated by red chilli, green chilli, pepper
and Chettinad spices. No private source image or code was sent for generation.
They are illustrative, not photographs of verified portions. Visible menu copy
and alt text identify that limitation. Original 1254px PNGs remain in the local
generation output; web assets are 1024px WebP at quality 80, about 95-107 KB each.
The hero uses prebuilt responsive 384/768/1024px versions. Existing pinned Sharp
performs asset optimization; no dependency, tracker or animation library added.

## Acceptance and delivery

Public routes retain server rendering, titles, canonical URLs and informational
links. Paused commerce URLs return 307 to Menu and are absent from the sitemap.
The private tracking page remains noindex. API authorization, stock accounting,
signed callbacks, idempotency and refunds remain enforced.

Verification must cover default-paused public navigation, four menu items even
with published products and stale browser storage, denied direct order/payment
requests without side effects, historical orders, persisted enquiries and PDF
download. The retained commerce browser suite runs sequentially with explicit
ordering enabled in the isolated fixture. See `feature-status.md` for fresh
verification and PR evidence. Production rollout and native Safari are separate.

The existing Docker staging acceptance also opts into ordering only in its unique
synthetic test project, so signed replay and worker recovery stay covered. Normal
staging and production retain the default pause.
