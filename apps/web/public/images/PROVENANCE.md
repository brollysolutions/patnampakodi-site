# Storefront asset provenance

Recorded 2026-09-10. These assets support the first storefront preview. Final
logo/product photography and business content require owner confirmation.

## Serving illustration

`pakodi-illustration.png` was generated with the built-in `image_gen.imagegen`
tool for this task and saved unaltered. It is visibly captioned “Serving
inspiration · illustration”; it does not claim to photograph a sold product.
`scripts/images.mjs` creates responsive 384/750/1122px AVIF (quality 25) and WebP
(quality 45) derivatives before development/build, using the same pinned Sharp
0.35.4 already required by Next.js. The original raster is retained unchanged.
The generated directory is ignored in Git and included in the Docker build.
The hero uses explicit high priority and responsive preload; it needs no runtime
image conversion or client image component. Other images use Next.js optimization.

SHA-256: `f3bea6a7b6c8f6c488a3b7e79d96702b9fe8be7b9c08b6a334147fdcced8ada0`.

Generation prompt:

> Use case: illustration-story. Asset type: premium Indian food storefront hero illustration, portrait 4:5 composition. Create a richly textured editorial culinary illustration of golden brown South Indian chicken pakodi piled in a shallow brushed stainless-steel plate lined with paper, with crisp curry leaves, two fresh green chillies and a cut lime. Very appetising, tactile, carefully observed craggy fried batter texture. Three-quarter overhead view. Warm cream paper background, afternoon side light, muted burnt orange linen peeking from one corner, deep warm brown shadows. Painterly realism with a subtle printed illustration texture, visibly an illustration rather than a documentary photo. Food fills the central and lower 80 percent of the frame, natural asymmetry and intimate framing. No words, letters, logos, packaging, labels, watermarks, people, floating ingredients or decorative line graphics. This is serving inspiration, not a photograph of an exact commercial product.

## Existing franchise illustrations

Downloaded from the user-supplied business website during this task; used only
to show its existing format concepts. They are not evidence of confirmed
investment, inclusions or a particular operating outlet. No hotlinking occurs.

| File | Original business source | SHA-256 |
| --- | --- | --- |
| `franchise-display.png` | [Display model](https://patnampakodi.com/wp-content/uploads/2026/07/Patnam-Padkodi-Franchise-Display-Model-768x1024.png) | `4712f892df492f9a78c1c8f825da76a34920b190d941c53ef7de143672ac4cdd` |
| `franchise-cart.png` | [Cart model](https://patnampakodi.com/wp-content/uploads/2026/07/Patnam-Pakodi-Franchise-Cart-Model-768x1024.png) | `16122584985c01a5f07aac0f80611b55390eed09719018a73a7afbf2a6cc63cc` |
| `franchise-cabin.png` | [Cabin model](https://patnampakodi.com/wp-content/uploads/2026/07/Patnam-Pakodi-Franchise-Cabin-Model-771x1024.png) | `9b4b29f6a3787d178cdfb999c69f6a77851169de31dc38a7dff2c356f12c2e70` |
| `franchise-shop.png` | [Premium shop model](https://patnampakodi.com/wp-content/uploads/2026/07/Patnam-Pakodi-Premium-shop-Model-Exterior-819x1024.png) | `82d51aa27cb4308058be61942eedcd66f04b8311cd0ef757f330cd3b118e036b` |

## Typography and identity

The locked fonts are self-hosted from exact npm packages:
`@fontsource/abril-fatface@5.3.0` and `@fontsource-variable/archivo@5.3.0`.
Their packages include the SIL Open Font License 1.1 and respective
TypeTogether/Archivo Project copyright notices. The original license files
are copied unchanged into `apps/web/licenses/` and included in the final Docker
image, as well as remaining in the integrity-locked npm packages.
Only Latin regular display and the body weight axis are loaded by the site.
The share image uses the packaged Abril WOFF. No runtime font CDN is requested.

The typeset brand name and simple P favicon are interim text treatments,
not replacements for an approved official vector logo.
