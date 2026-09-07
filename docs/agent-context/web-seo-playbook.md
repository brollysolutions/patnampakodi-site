# Web SEO and quality playbook

Distilled on 2026-09-07 from the BrollyAI website workflow: its UI playbook,
homepage SEO brief, the SEO audits of 2026-09-05 and 2026-09-06, the web gate
(`scripts/verify-web.sh`, `lighthouserc.json`, the Playwright suites) and the site
code (`routes.ts`, `seo.ts`, `jsonld.ts`, `robots.ts`, `sitemap.ts`,
`redirects.ts`, `next.config.ts`). Authoritative for every public page once the
project owner adopts it; later explicit user instructions take precedence and
must be folded back into this file. Read it with `website-design-decisions.md`
before creating or revising a public page. `$seo-review` audits against it.

## Priorities

Search visibility, qualified enquiries and speed govern design choices, in that
order. A design change that costs a ranking URL, a server-rendered heading, a
canonical, or a Lighthouse budget is not a design change; it is a regression.

## Non-negotiables for every public page

1. **URLs are permanent.** Preserve every existing URL and slug. Clean, lower-case
   paths with a trailing slash (or without, but consistently); never a hash
   fragment as a destination, never a query parameter to select content. A URL
   that must move gets a redirect: `308` when the destination is final, `307`
   while the content is still to be ported, so browsers do not cache a redirect
   that later becomes a page. Retired endpoints return `404` or `410`.
2. **One route manifest.** Navigation, breadcrumbs, the sitemap, the smoke tests,
   the accessibility sweep and the launch gate all read the same list. A page
   that is not in the manifest is not linked, not indexed and not tested. Typed
   routes (`typedRoutes: true`) make a link to an unconfirmed URL a type error.
3. **Metadata per route.** Unique title (≤ 60 characters, templated with the
   site name), unique description (≤ 160 characters), a self-referencing
   canonical, Open Graph title/description/url/image, `twitter:card`. Open
   Graph copy may differ from the search copy when the share card should invite
   a conversation rather than carry the keyword. Titles and descriptions are
   unit-tested for length and uniqueness.
4. **Exactly one H1**, rendered on the server, that carries the page's primary
   keyword. Heading order is semantic; a display statement above the H1 is a
   `<p>`, not a heading. No eyebrows or overlines that compete with headings.
5. **Server-rendered content.** Every heading, paragraph, curriculum module, FAQ
   answer and link is in the HTML response. Native `<details>` disclosures for
   curricula and FAQs work without JavaScript. Nothing that matters for ranking
   is loaded by script, and no content depends on a fragment being present.
6. **Indexability is an environment property.** Production is crawlable except
   the API; every other host (previews, dev, local builds) carries
   `X-Robots-Tag: noindex, nofollow` and a robots.txt that disallows `/`. The
   verification gate builds with `SITE_INDEXABLE=true` so Lighthouse's SEO audit
   sees the production header set. A deploy job for a non-production host
   asserts the noindex header after every deploy.
7. **Sitemap and robots are generated from the manifest.** Draft pages are
   excluded; `lastModified` reflects real content revisions; robots.txt
   advertises the canonical sitemap URL.
8. **Structured data tells the truth.** JSON-LD is built by a small set of
   reviewed builders (Organization, WebSite, WebPage, BreadcrumbList, Service,
   Course, ContactPage) with an allow-list of keys enforced by a unit test. No
   ratings, reviews, awards, counts, addresses, social profiles or scheduled
   instances that the business has not confirmed in writing. The only component
   that injects raw HTML is the JSON-LD component, and it escapes `<`.
9. **Internal links resolve.** Every internal link returns `200` with no
   redirect hop; descriptive anchor text; crawlable HTML links (no JavaScript
   navigation for content). Marketing links set `prefetch={false}` so idle
   fetches do not compete with the current page.
10. **Images earn their bytes.** Local, optimised sources (AVIF/WebP), intrinsic
    dimensions, responsive `sizes`, lazy loading below the fold, descriptive
    `alt` on informative images and empty `alt` on decorative ones. No hotlinked
    publisher artwork; keep provenance beside the assets.
11. **Speed budgets never relax to pass.** Lighthouse assertions: performance
    ≥ 0.9, accessibility = 1, best practices ≥ 0.9, SEO = 1, LCP ≤ 2500 ms,
    CLS ≤ 0.1, TBT ≤ 200 ms, measured on the production build. No new font,
    animation library, UI dependency, tracker or autoplay media without a
    reviewed decision and a before/after measurement. Server components by
    default; CSS transform/opacity motion; respect reduced motion.
12. **No intrusive interstitials.** Enquiry or contact prompts are small,
    non-modal, closable, never cover the page on arrival, never capture focus
    or lock scroll, and never use a backdrop. The page's own content is what
    the crawler and the visitor see first.
13. **Accessibility is part of the gate.** axe (WCAG 2.1 AA + best practice)
    passes on every manifest route at narrow, medium and wide widths; skip link,
    landmarks, labelled controls, visible focus, contrast, and keyboard and
    touch operation all verified.
14. **Facts only.** No invented testimonials, ratings, fees, placement
    guarantees, addresses, people or project evidence. Qualified or proposed
    content stays visibly qualified. Withheld facts are recorded in `INDEX.md`
    as conflicts, not filled with assumptions.

## Implementation pattern (Next.js App Router)

Reference copies of every file named here live in the kit under
`reference/web-seo-patterns/`.

| Concern | Where | Rule |
| --- | --- | --- |
| Site facts | `src/content/site.ts` | name, URL, locale, language, verified contact channels; unconfirmed facts are `null`, never guessed |
| Route manifest | `src/lib/site/routes.ts` | `path`, `title`, `description`, optional `ogTitle`/`ogDescription`, `parent`, `lastModified`; unit-tested for trailing slashes, uniqueness, snippet limits and parent existence |
| Page metadata | `src/lib/site/seo.ts` → `routeMetadata(path)` | title, description, `alternates.canonical`, Open Graph, Twitter card; the OG image comes from the route's `opengraph-image.tsx` |
| Root metadata | `src/app/layout.tsx` | `metadataBase`, title template, `robots: { index: true, follow: true }` (environment noindex comes from the header, not page metadata) |
| Structured data | `src/lib/site/jsonld.ts` + `components/site/JsonLd.tsx` | builders with allow-listed keys; `serializeJsonLd` escapes `<`; ESLint restricts `dangerouslySetInnerHTML` to that one component |
| Indexability | `next.config.ts` headers + `src/app/robots.ts` | `indexable = VERCEL_ENV === "production" || SITE_INDEXABLE === "true"`; otherwise `X-Robots-Tag: noindex, nofollow` and `disallow: /` |
| Sitemap | `src/app/sitemap.ts` | manifest minus drafts; `changeFrequency`/`priority` by depth |
| Redirects | `src/lib/site/redirects.ts` | legacy table consumed by `next.config.ts`; `permanent: true` (308) only when final; retired paths listed for the launch gate |
| Security headers | `next.config.ts` | static CSP without third-party origins, HSTS, nosniff, referrer policy, permissions policy, frame denial; `poweredByHeader: false` |
| Smoke test | `tests/e2e/smoke.spec.ts` | every route: 200, security headers, one H1, title, canonical ends with the path, one `og:image` |
| Accessibility | `tests/e2e/a11y.spec.ts` | axe on every route with reduced motion so final states are audited |
| Launch gate | `tests/e2e/launch.spec.ts` (`@launch`) | against the deployed host: every route complete, JSON-LD parses, no noindex, homepage links resolve, redirects land per table, retired endpoints gone, sitemap/robots describe the live site, CSP has no third-party origins |
| Budgets | `lighthouserc.json` | the assertions above on `/`, the main index page and the contact page; reduced motion forced |
| Gate script | `scripts/verify-web.sh` | `SITE_INDEXABLE=true`, form test env, lint → typecheck → unit → build → Playwright → Lighthouse; `fast` skips browsers, `launch` runs the `@launch` gate against `PLAYWRIGHT_BASE_URL` |
| Per-page check | `scripts/check_seo.py` | stdlib script: status, H1, canonical, snippet limits, OG/Twitter, noindex, image alt, JSON-LD, robots, sitemap, internal links |

## Per-page checklist (new or changed public page)

1. Register the route in the manifest with title, description, parent and
   `lastModified`; add the catalogue or navigation entry so enquiry context and
   footer discovery stay correct.
2. Write the page with `routeMetadata(path)`, one H1, server-rendered sections in
   the recorded page order, shared primitives (section, FAQ, closing CTA owned by
   the layout), and only confirmed copy and assets.
3. Add `opengraph-image.tsx` from the shared OG template.
4. Add structured data only from the reviewed builders, and only for confirmed
   facts.
5. Add or extend tests: manifest unit tests pick the route up automatically;
   add content assertions for source-backed facts.
6. Verify without JavaScript, at 360/390, 768 and 1280/1440 widths, on short
   screens, with keyboard and touch, with form error states, and with axe.
7. Run the web gate on the production build, then `scripts/check_seo.py` for the
   page, then `$seo-review` and `$design-review`.
8. Record evidence in `implementation-plan.md` and `feature-status.md`, then ship.

## Verification commands

```bash
# Full web gate on the indexable production build
./scripts/verify-web.sh            # full: lint, typecheck, unit, build, Playwright, Lighthouse
./scripts/verify-web.sh fast       # no browsers
PLAYWRIGHT_BASE_URL=https://example.com ./scripts/verify-web.sh launch

# Technical SEO for specific pages against a running production build
SITE_INDEXABLE=true pnpm build && pnpm start &
python scripts/check_seo.py http://localhost:3000 / /services/ /contact/ \
  --canonical-origin https://example.com --expect-text "<a sentence from the page>"
```

## Honesty rules for SEO claims

- Lighthouse's SEO score covers technical checks; it does not measure ranking
  potential, authority or business credibility. Say "technical SEO checks pass",
  never "the page will rank".
- Local Lighthouse runs drift with host CPU; record them as indicative, keep the
  budgets unchanged, and let CI or a stable environment decide. Field Core Web
  Vitals need production traffic.
- Google may choose different titles and snippets; configured metadata does not
  guarantee how a result appears.
- Word counts and sentence counts are readability choices, not ranking factors.
- A hash fragment is not a ranking signal either way; the rule against fragment
  destinations is about crawlable content, not a promised benefit.
- No production cutover, Search Console submission, or external email is part
  of an implementation change unless the user asks for that exact action.

## Migration and cutover (replacing an existing site)

1. Inventory every ranking URL from the old site (export, Search Console
   landing pages) before designing the new tree.
2. Port each ranking page at its existing slug, or redirect it deliberately with
   the correct status; never let a ranking URL fall to a category page by
   default.
3. Keep the old site live until the new one is complete. Preserve legal pages by
   porting, not rewriting.
4. Cut over only after the launch gate passes against the deployed host: HTTPS,
   response codes, canonicals, redirects, robots, sitemap, security headers,
   enquiry configuration.
5. After cutover, submit the sitemap and inspect representative URLs in Search
   Console; measure field Core Web Vitals over time.

## Research, retrieved 2026-09-05 and 2026-09-06

- Google: URL structure — https://developers.google.com/search/docs/crawling-indexing/url-structure
- Google: JavaScript SEO basics — https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics
- Google: title links — https://developers.google.com/search/docs/appearance/title-link
- Google: avoid intrusive interstitials — https://developers.google.com/search/docs/appearance/avoid-intrusive-interstitials
- Google: people-first content — https://developers.google.com/search/docs/fundamentals/creating-helpful-content
- Google: image SEO — https://developers.google.com/search/docs/appearance/google-images
- Google: Course structured data — https://developers.google.com/search/docs/appearance/structured-data/course
- Google: fragments and content loading — https://developers.google.com/search/blog/2020/05/frequently-asked-questions-about
- web.dev: `content-visibility` — https://web.dev/articles/content-visibility (a trial of `content-visibility: auto` broke offscreen disclosures without JavaScript and mobile axe checks; do not reintroduce it without verifying those journeys)
