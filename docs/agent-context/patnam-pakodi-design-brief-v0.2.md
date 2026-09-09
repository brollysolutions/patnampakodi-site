# Patnam Pakodi
## Website Design Brief

**Version** 0.2 (draft — open questions in §9) · **Date** 4 September 2026
**Parent** FRAB Foods India · **Platform** FRAB multi-brand platform (Next.js / TailwindCSS / shadcn/ui, CSS custom-property theming)
**Companion document** Patnam Pakodi Brand Data Document v1.1 (content and facts). This brief covers visual identity only.

---

## 1. Status of this brief

| Section | Status |
|---|---|
| Typography (§3) | **Locked** — confirmed by FRAB, 4 Sep 2026 |
| Primary colours (§4.1) | **Locked** — confirmed by FRAB, 4 Sep 2026 |
| Brand name spelling | **Locked** — "Patnam Pakodi", confirmed by FRAB, 4 Sep 2026 |
| Button text colour | **Locked** — white on orange, with size rule (§4.2), confirmed by FRAB, 4 Sep 2026 |
| Third brand colour (§4.5) | **Proposed** — FRAB asked for a recommendation; needs sign-off |
| Supporting colours, states, tokens (§4.2–4.4) | **Proposed** — derived from the locked colours; needs sign-off |
| Logo, imagery, layout, motion (§5–8) | **Open** — no source material supplied yet |

Nothing marked *Proposed* or *Open* should be treated as final. Where a value had to be chosen to make the brief usable (e.g. a neutral grey), it is labelled as an assumption.

---

## 2. Confirmed facts, assumptions, unknowns

### 2.1 Confirmed (from FRAB)
- Body / UI typeface: **Archivo** (Google Fonts, free version).
- Heading / display typeface: **Abril Fatface** (Google Fonts, free version).
- Primary brand colour: **Mandarin Orange `#EB6637`**.
- Primary dark colour: **Zinnwaldite Brown `#2B1406`**.
- These are to be held constant for the website going forward.
- Brand name is spelled **Patnam Pakodi** in all tokens, titles and metadata (resolves the "Pattnam" variant in the original request).
- Primary buttons use **white text on orange**, accepting the size constraint in §4.2.

### 2.2 Confirmed (from audit of patnampakodi.com, 4 Sep 2026)
The live WordPress/Elementor site uses **none** of the above. It currently loads:

| Asset | Live site today | New spec |
|---|---|---|
| Fonts loaded | Poppins (all 18 weights), Roboto (all 18 weights), Roboto Slab (all 18 weights), Inter, Raleway | Archivo, Abril Fatface |
| Font applied to most content | Poppins | Archivo |
| Elementor global "primary" | `#FF6210` | `#EB6637` |
| Elementor global "secondary" | `#F15808` | — (no secondary defined yet) |
| Most-used accent in page CSS | `#C0392B` (a red, ~180 occurrences) | `#EB6637` |
| Dark / text colours | `#1C0D0A`, `#140B06`, `#222222`, `#353535`, `#0A0E27`, `#14182F` | `#2B1406` |
| Warm background tints | `#FEF1E4`, `#E5D7D1`, `#FAF3E0` | — (proposed in §4.2) |

**Implication:** every colour and font on the current site is a conflict with the new spec. There is nothing on the live site to carry forward; the new site is a clean re-theme, not a touch-up. The Brand Data Document v1.1 deliberately excludes visual identity, so it contains no conflicting values and needs no edit.

### 2.3 Assumptions (labelled, reversible)
- A1. Archivo will be used in its standard width. Google Fonts also ships Archivo Narrow, Expanded and Black as separate families; none of these are in scope unless FRAB says otherwise.
- A2. Abril Fatface is used for headings only. It has one weight (400) and no italic, so body copy, labels and UI text cannot use it.
- A3. Fonts will be self-hosted via `next/font/google` rather than loaded from the Google Fonts CDN at runtime. See §3.3 for why.
- A4. A neutral grey scale and a functional colour set (success / warning / error) are needed for an e-commerce site and are proposed in §4.2. FRAB has not specified these.

### 2.4 Unknowns (blocking — see §9)
- Logo source files (vector), clear-space and minimum-size rules.
- Sign-off on the proposed third colour (§4.5).
- Imagery direction (photography vs illustration; existing photo library).
- Any existing print collateral (menu boards, packaging, cart branding) the website must match.

---

## 3. Typography — LOCKED

### 3.1 Typefaces

| Role | Family | Weights to load | Google Fonts | Notes |
|---|---|---|---|---|
| Display / headings | **Abril Fatface** | 400 only (only weight available) | fonts.google.com/specimen/Abril+Fatface | SIL Open Font License. No italic, no bold. |
| Body, UI, navigation, buttons, forms, tables | **Archivo** | 400, 500, 600, 700 (+ 400 italic) | fonts.google.com/specimen/Archivo | SIL Open Font License. Variable font available. |

**Why this pairing works:** Abril Fatface is a high-contrast Didone display face; it carries the "premium" and "iconic, playful" positioning the brand already claims. Archivo is a grotesque with a large x-height and tabular figures, which suits prices, menus, order tables and franchise pricing.

### 3.2 Scale (proposed, mobile-first)

| Token | Family | Size (mobile / desktop) | Weight | Line-height | Use |
|---|---|---|---|---|---|
| `display` | Abril Fatface | 40 / 64 px | 400 | 1.05 | Hero H1 only |
| `h1` | Abril Fatface | 32 / 48 px | 400 | 1.1 | Page titles |
| `h2` | Abril Fatface | 26 / 36 px | 400 | 1.15 | Section headings |
| `h3` | Archivo | 20 / 24 px | 600 | 1.3 | Card and block titles |
| `body` | Archivo | 16 / 17 px | 400 | 1.6 | Paragraphs |
| `small` | Archivo | 14 px | 400 | 1.5 | Captions, meta, legal |
| `label` | Archivo | 13 px, +0.04em tracking, uppercase | 600 | 1.2 | Eyebrows, badges, tab labels |
| `price` | Archivo | 16–24 px, tabular figures | 600 | 1.2 | Menu and product prices |

**Rules**
- Abril Fatface never below 24 px — its thin hairlines break up at small sizes and on low-DPI screens.
- Abril Fatface never in all-caps blocks longer than three words; hairlines make caps hard to read.
- H3 and below use Archivo, not Abril Fatface, so that card grids (51 menu items, 7 SKUs, 6 outlets) stay scannable.
- Telugu text (tagline "Life Lo Spice Undali" is Roman-script, but any future Telugu-script copy) needs a Telugu-capable fallback; neither locked font has Telugu glyphs. See §9.

### 3.3 Loading — proposed

Use `next/font/google` for both families. This downloads the free Google Fonts files at build time and serves them from the site's own domain.

Why this matters:
- No runtime request to Google — removes a third-party dependency and a render-blocking round trip, which the current site pays five times over (five separate Google Fonts stylesheets).
- Zero layout shift: `next/font` generates `size-adjust` fallbacks automatically.
- Satisfies the platform's "no deployment per brand" goal: the font files ship once with the platform build; each brand's theme only sets `--font-display` and `--font-body`.

Load only the weights listed in §3.1. The current site loads 54 weight/style files across three families; the new site should load six.

---

## 4. Colour

### 4.1 Primary colours — LOCKED

| Name | Hex | RGB | Role |
|---|---|---|---|
| Mandarin Orange | `#EB6637` | 235, 102, 55 | Primary brand colour. CTAs, links, active states, highlights, brand accents. |
| Zinnwaldite Brown | `#2B1406` | 43, 20, 6 | Primary dark. Body text, headings, footer background, dark sections. |

### 4.2 Contrast — verified (WCAG 2.1)

| Foreground | Background | Ratio | AA normal text (4.5) | AA large text / UI (3.0) |
|---|---|---|---|---|
| `#2B1406` | `#FFFFFF` | 17.4 | Pass | Pass |
| `#FFFFFF` | `#2B1406` | 17.4 | Pass | Pass |
| `#EB6637` | `#FFFFFF` | 3.24 | **Fail** | Pass |
| `#FFFFFF` | `#EB6637` | 3.24 | **Fail** | Pass |
| `#2B1406` | `#EB6637` | 5.38 | Pass | Pass |
| `#EB6637` | `#2B1406` | 5.38 | Pass | Pass |

**Consequences — these are hard rules, not preferences:**
1. **Orange text on white** is only permitted at large sizes (≥ 24 px regular or ≥ 18.66 px bold). Body copy and small links must not be orange.
2. **White text on orange buttons — LOCKED by FRAB.** This passes WCAG AA only as "large text", so it comes with a hard rule: **every orange-filled button uses Archivo 700 at ≥ 19 px** (rounded up from the 18.66 px threshold). This applies to the primary CTA, "Add to cart", "Enquire now", checkout and form submit buttons.
   For any control that must be smaller than 19 px bold (compact table actions, chips, mobile secondary buttons, pagination), do **not** use an orange fill. Use one of:
   - **Brown fill, white text** (`#FFFFFF` on `#2B1406` = 17.4) — the default secondary button.
   - **Orange outline (2 px), brown text** on white — tertiary / ghost button. The orange border only needs 3.0, which it passes.
   Why: this keeps the brand's white-on-orange look on every prominent CTA while never shipping an inaccessible small control.
3. Orange on brown and brown on orange are both safe at all sizes — use this pairing for hero and footer sections.
4. Orange is fine for icons, borders, focus rings, underlines and fills (non-text UI needs only 3.0).

Why this matters: an accessibility failure on the primary CTA colour is the single most common re-work item on brand re-themes, and it is cheaper to decide now than after 140 features are built against a token.

### 4.3 Supporting palette — PROPOSED, needs sign-off

Derived from the two locked colours so the palette stays two-hue. Each value is a tint or shade of the locked pair, not a new colour.

| Token | Hex | Derivation | Use |
|---|---|---|---|
| `orange-600` | `#C94F24` | Orange darkened ~15% | Hover / pressed state for primary buttons |
| `orange-100` | `#FDEAE2` | Orange at ~12% on white | Highlight backgrounds, selected rows, badges |
| `orange-050` | `#FFF6F2` | Orange at ~5% on white | Section tints, alternating bands |
| `brown-700` | `#4A2A16` | Brown lightened | Secondary text, table headers |
| `brown-500` | `#7A5A44` | Brown lightened further | Placeholder text, disabled labels, metadata |
| `neutral-200` | `#EAE3DD` | Brown at ~10% on white | Borders, dividers, card outlines |
| `neutral-100` | `#F6F2EE` | Brown at ~5% on white | Page background alternative, input backgrounds |
| `white` | `#FFFFFF` | — | Primary page background |

Functional colours (required for cart, checkout, order status, form validation — not brand colours, kept deliberately generic):

| Token | Hex | Use |
|---|---|---|
| `success` | `#1E7F4F` | Order placed, in-stock, payment success |
| `warning` | `#B7791F` | Low stock, pending payment, unsaved changes |
| `error` | `#B42318` | Validation errors, failed payment, out of stock |
| `info` | `#2B1406` (brown) | Neutral notices — reuse the brand dark rather than adding a blue |

### 4.4 Colour rules
- Orange is an accent, not a background. Target ≤ 10% of any viewport in solid orange; large orange fills belong in the hero and nothing else.
- Never place orange and the red-based `error` colour side by side — they read as one colour to red-green colour-blind users. Use an icon plus text for error states.
- Do not introduce the live site's `#C0392B` red, `#FF6210`, `#F15808` or any of the navy/blue values (`#0A0E27`, `#3B82F6`) on the new site. They are listed here only so they can be recognised and removed.

### 4.5 Third brand colour — PROPOSED

FRAB asked for a recommendation. Three candidates were tested against the locked pair; contrast ratios below are measured, not estimated.

| Candidate | Hex | Rationale | Brown text on it | White text on it | Verdict |
|---|---|---|---|---|---|
| **Pakodi Cream** | `#FBEFD9` | Warm off-white; the colour of the batter and paper packaging. Works as a full-page or section background. | 15.3 (pass) | 1.1 (fail — never put white on it) | **Recommended** |
| Chilli-Leaf Green | `#2F5D3A` | Nods to Pachi Mirchi / Kothimeera, the two signature items. | 2.3 (fail) | 7.6 (pass) | Not recommended |
| Turmeric | `#F2B632` | Warm, energetic, common in Indian QSR. | 9.6 (pass) | 1.8 (fail) | Not recommended |

**Recommendation: Pakodi Cream `#FBEFD9`.**

Why cream and not green or turmeric:
- **The palette is missing a surface, not another accent.** Orange already carries all the energy; brown carries all the weight. What the site lacks is a warm, non-white background so the two locked colours are not always sitting on stark white. Cream fills that gap; green or turmeric would compete with orange for attention.
- **Cream is the safest with Abril Fatface.** Didone display faces on cream read as "premium / editorial" — the positioning the brand claims. On saturated green or yellow they read as posters.
- **Green carries a specific meaning in Indian food.** The green dot means vegetarian. A chicken brand adopting green as a brand colour invites mislabelling risk on packaging and menu cards, which is exactly the compliance layer the platform is being built to get right.
- **Turmeric fails with white text and clashes with orange** (1.8 contrast between the two) so it could only be used as a background for brown text — a narrower role than cream, with more visual noise.
- **Zero new accessibility exceptions.** Cream behaves like white for every rule already in §4.2 except one: orange text on cream is 2.84, so orange text is not permitted on cream at any size (orange *fills* and *buttons* on cream are fine — the button rule in §4.2 is about white text on orange, not orange on its background).

**Usage rules for cream (if approved)**
- Section backgrounds (alternating bands with white), hero background behind the orange CTA, menu and product card backgrounds, testimonial blocks, footer top band above the brown footer.
- Never as a text colour and never under white text.
- Replace the proposed `--color-surface-alt: #F6F2EE` in §5 with `#FBEFD9`; `neutral-100` in §4.3 becomes the input-background only.

---

## 5. Theme tokens for the FRAB platform — PROPOSED

The platform themes each brand through CSS custom properties (locked architecture decision). This is the Patnam Pakodi theme record as it should be stored — once — in the Brand entity and rendered everywhere.

```css
:root[data-brand="patnam-pakodi"] {
  /* Typography */
  --font-display: "Abril Fatface", Georgia, "Times New Roman", serif;
  --font-body:    "Archivo", system-ui, -apple-system, "Segoe UI", sans-serif;

  /* Brand — LOCKED */
  --color-primary:        #EB6637;   /* Mandarin Orange */
  --color-primary-fg:     #FFFFFF;   /* white on orange — buttons must be Archivo 700 ≥ 19px (§4.2 rule 2) */
  --color-secondary:      #2B1406;   /* brown-filled secondary button */
  --color-secondary-fg:   #FFFFFF;
  --color-dark:           #2B1406;   /* Zinnwaldite Brown */
  --color-dark-fg:        #FFFFFF;

  /* Supporting — PROPOSED */
  --color-primary-hover:  #C94F24;
  --color-primary-soft:   #FDEAE2;
  --color-primary-tint:   #FFF6F2;
  --color-text:           #2B1406;
  --color-text-muted:     #7A5A44;
  --color-border:         #EAE3DD;
  --color-surface:        #FFFFFF;
  --color-surface-alt:    #FBEFD9;   /* Pakodi Cream — PROPOSED third colour (§4.5) */
  --color-input-bg:       #F6F2EE;

  /* Functional — PROPOSED */
  --color-success:        #1E7F4F;
  --color-warning:        #B7791F;
  --color-error:          #B42318;

  /* Shape — OPEN (see §9) */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 16px;

  /* Button sizing — LOCKED consequence of white-on-orange */
  --btn-primary-font-size:   19px;
  --btn-primary-font-weight: 700;
}
```

shadcn/ui `Button` variants map as: `default` → orange fill / white text, forced to the primary size (no `sm` variant permitted on `default`); `secondary` → brown fill / white text (all sizes); `outline` → orange border / brown text (all sizes).

Tailwind reads these via `theme.extend.colors` using `var(--color-*)` so utility classes stay brand-agnostic. shadcn/ui components map `--primary`, `--primary-foreground`, `--background`, `--foreground`, `--muted`, `--border`, `--destructive` onto the tokens above; no component is edited per brand.

Why this matters: it is the direct application of the platform's governing principle — a colour or font stated in one place, rendered everywhere. Changing the brand colour later is a one-field edit in the admin panel, not a code change.

---

## 6. Logo — OPEN

Known: a raster logo exists on the live site (`Patnam-Pakodi-Logo-e1764972225563-130x126.png`, 130×126 px). This is too small for retina hero use and is not vector.

Required before design work can proceed: SVG master, versions for light and dark backgrounds, minimum size, clear-space rule, and whether the logo colours match `#EB6637` / `#2B1406` or carry their own values. If the logo uses different oranges or browns, that conflict must be resolved — the website cannot show a logo in one orange next to buttons in another.

---

## 7. Imagery and iconography — OPEN

No direction supplied. Decisions needed:
- Photography style (the live site currently reuses one staff photo across three products — the new site needs at least one hero, one per menu section, one per SKU and one per outlet).
- Whether icons are line or filled; recommend a single library (Lucide ships with shadcn/ui) tinted with `--color-primary` or `--color-text`.
- Treatment of the Telugu tagline "Life Lo Spice Undali" — typeset in Abril Fatface, or a lettered graphic asset.

---

## 8. Layout and motion — OPEN (defaults stated)

Defaults if FRAB has no preference: 12-column grid, 1280 px max content width, 8 px spacing scale, `--radius-md` 8 px on cards and inputs, `--radius-lg` on hero cards, motion limited to 150–250 ms opacity/transform transitions with `prefers-reduced-motion` respected. These are platform defaults shared by all FRAB brands, not Patnam Pakodi decisions.

---

## 9. Questions for FRAB — answers needed to move §4.3–§8 from Proposed/Open to Locked

**Resolved 4 Sep 2026:** spelling = Patnam Pakodi · button text = white on orange with the ≥ 19 px bold rule · third colour = FRAB asked for a proposal (see §4.5).

**Blocking**
1. **Logo files.** Can you supply the SVG master and any existing logo guidelines? Do the logo's colours exactly match `#EB6637` and `#2B1406`?
2. **Third colour sign-off.** Approve Pakodi Cream `#FBEFD9` as proposed in §4.5, or choose another candidate.
3. **Small-button fallback.** Confirm that controls smaller than 19 px bold will use brown fill or orange outline (never orange fill). If you would rather have *no* small buttons at all and keep every button at the primary size, say so — that is simpler but constrains dense screens such as the cart and admin tables.

**Important**
4. **Existing collateral.** Do menu boards, packaging, cart wraps or the franchise brochure already use these fonts/colours? If so, please share photos or files so the website matches physical touchpoints.
5. **Font weights.** Is Archivo 400/500/600/700 sufficient, or do you want the heavier Archivo Black for display-adjacent uses (e.g. price callouts, "₹69,000" stat blocks)?
6. **Telugu script.** Will any page carry Telugu-script text? If yes, a Telugu font (e.g. Noto Sans Telugu, also free) must be added as a fallback — neither locked font has Telugu glyphs.
7. **Dark sections.** Should the footer and hero use Zinnwaldite Brown as a full-bleed background (recommended — 17.4 contrast with white text), or stay light?

**Nice to have**
8. Corner radius preference — sharp (0–4 px, more "premium/editorial", suits Abril Fatface), or rounded (12–16 px, more "playful/QSR")?
9. Imagery — do you have a photo library, and is illustration acceptable for sections where no photography exists?
10. Do these tokens apply to FRAB Foods India's own site too, or only to Patnam Pakodi? (FRAB's own theme is a separate Brand record on the platform.)

---

## 10. Change log

| Version | Date | Change |
|---|---|---|
| 0.2 | 4 Sep 2026 | Spelling locked (Patnam). White-on-orange button text locked with ≥ 19 px bold rule and secondary/outline fallbacks. Third colour proposed: Pakodi Cream `#FBEFD9`, with green and turmeric rejected on measured contrast and veg-mark grounds. Tokens and questions updated. |
| 0.1 | 4 Sep 2026 | Initial brief. Typography and primary colours locked per FRAB. Live-site audit of fonts/colours recorded. Supporting palette proposed. Questions raised. |
