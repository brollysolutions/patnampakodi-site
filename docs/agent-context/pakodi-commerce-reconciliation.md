# Patnam Pakodi commerce: reconciled delivery brief

Derived on 2026-09-09 from the three user-supplied documents. This is a build
proposal and conflict register, not evidence of implemented features or approval
of unresolved choices. The user supplied the documents and live URL with
"cook it"; the first-delivery scope and private-page indexing clarification
were requested during the session and remain unanswered as of this revision.

## Authority and source preservation

The [MVP v4.1](frab-foods-mvp-features-v4.1.md) defines **50 features: 45 P0
and 5 P1**. The [design v0.2](patnam-pakodi-design-brief-v0.2.md) is authoritative
only for its explicitly locked identity rules. The
[integration v1.0](frab-foods-razorpay-whatsapp-plan-v1.0.md) supplies proposed
implementation safeguards, assumptions and external claims; it does not change
the [approved technology stack](technology-stack.md). Originals are unchanged.

Both contributor and upstream repositories were verified PRIVATE before copying
the documents for delivery. Preserve their confidentiality designation. No
credentials, customer records or account onboarding material are included.

| Source as supplied | Repository copy | SHA-256 |
| --- | --- | --- |
| Patnam-Pakodi-Design-Brief (2).md | `patnam-pakodi-design-brief-v0.2.md` | `79d3a656a75462965c190c48d9f3f1e1f62a1d704cc4c79c613a0613a40b32c7` |
| FRAB-Foods-MVP-Application-Features-v4.1 (1).md | `frab-foods-mvp-features-v4.1.md` | `9b2165c6ec174d09e009b4c48cee0858714152fe2b75dcd061162e07f8269e91` |
| FRAB-Foods-Razorpay-WhatsApp-Implementation-Plan-v1.0 (1).md | `frab-foods-razorpay-whatsapp-plan-v1.0.md` | `de7fddd20ab1550905ea43949fa45a9d00f7dc3e22bb8028aea42065cdfd5983` |

The adjacent Downloads file `Patnam-Pakodi-Brand-Document.md` v1.1 was consulted
because the design brief names it as its companion. It was not one of the three
explicitly supplied sources and is not archived or promoted to approved seed
data. Its data-quality warnings inform the unresolved-content checklist below;
its business claims were not independently verified in this session.

## Current implementation and migration baseline

At upstream commit `b01ebcf`, `AGENTS.md`, `SECURITY.md`, `scripts/`, workflow
tests, and `.github/` describe and implement developer workflow only. There are
no web routes, client API wrappers, generated contracts, FastAPI handlers, auth
dependencies, services, models, migrations, RLS policies or product jobs to trace.
Those layers must be introduced and tested; examples in the SEO playbook are
reference patterns rather than runnable application code.

The live WordPress site is a separate system. On 2026-09-09 its homepage returned
HTTP 200, a self-referencing canonical and **`noindex, nofollow`**. Its navigation
links to `/`, `/about-us/`, `/menu/`, `/branches/`, `/franchise/`, `/shop/` and
`/contact/`. This is a homepage-derived inventory, not a complete crawl or proof
that all destination pages work. Read [the baseline](pakodi-live-site-baseline.md)
before planning redirects. Do not change production during this documentation
delivery.

## Product direction and first delivery

Customers need to explore food, find an outlet, buy packaged products and track
an order. Prospective franchisees need clear investment information and a
reliable enquiry path. Named administrators need to manage content, stock,
orders and enquiries. The public site must earn trust through accurate food
information and terms rather than unverified growth or return claims.

Recommended approach: deliver a **stored-content storefront vertical slice**
first, then add checkout and operational integrations in independently verified
PRs. Keep all 50 features in the roadmap; a storefront preview is not the MVP.
Build the first slice against the approved stack so it does not require a second
rewrite to meet stored-content requirement 1.1.

| Approach | User experience and scope | Data, security and operations | Verification and reversibility |
| --- | --- | --- | --- |
| Stored-content storefront, then commerce (recommended) | Early review of real page structure; commerce remains visibly unavailable until complete | Next.js + FastAPI + PostgreSQL from the first slice; reviewed published-content boundary; more initial infrastructure than a mock | Test each slice and retain existing URLs; design can change before financial workflows exist |
| Entire MVP in one delivery | All journeys arrive together; no early working slice | Same stack and full PII, inventory, financial and provider surface in one review; largest dependency and onboarding bottleneck | Largest regression matrix and rollback surface; difficult to isolate content decisions |
| Design prototype first | Fast visual feedback; synthetic/local content only | No live collection, payments or providers; lowest initial operational cost | Browser review only; prototype is not evidence of 1.1 or commerce readiness and needs later integration |

## Conflicts and decisions

Do not silently resolve open business/security decisions by rewriting the source.
The proposal column below is a recommendation unless existing authority is named.

| ID | Conflict or gap | Disposition / decision needed | Blocks |
| --- | --- | --- | --- |
| D1 | Integration plan assumes Celery + Valkey and an existing backend | Keep explicitly approved APScheduler + Redis. Propose a dedicated scheduler process and PostgreSQL outbox; no Celery/Valkey dependency | Final worker design, not source ingestion |
| D2 | v4.1 6.1 says all pages indexable and noindex impossible; private commerce pages contain sensitive information | Ask to limit this to published public storefront pages. Keep private routes authenticated/authorized and `noindex`; noindex is not access control. Previews remain non-indexable | Production indexing contract |
| D3 | Integration plan says 5.1 was removed and assumes mandatory 2FA | v4.1 explicitly retains admin login with one role. Named accounts and server-side authentication are required; recommend TOTP, with enrollment/recovery design to confirm | Auth implementation |
| D4 | Integration plan describes email as guaranteed, while v4.1 3.5 specifies WhatsApp only | Confirm mandatory checkout email and an email fallback; keep franchise operational failure alerts distinct from customer/lead notifications | Checkout contact schema and notification provider |
| D5 | Direct Meta API is recommended, but shared inbox need is unknown | Recommend direct API for outbound templates only; choose a BSP only if shared staff replies are required. No provider subscription/account change now | Provider selection |
| D6 | Primary colors/fonts locked; cream, supporting tokens, logo and photos remain proposed/open | See the concrete [visual proposal](website-design-decisions.md). Confirm cream and temporary text identity pending approved logo; request approved imagery before final launch | Visual implementation direction / final brand assets |
| D7 | Live-derived companion contains conflicting contact details, office addresses, outlet counts, franchise inclusions and royalties | FRAB must supply canonical values. Do not choose a phone/address or publish claimed ratings, profits, counts or territorial promises from inconsistent copies | Contact, franchise/outlet content and structured data |
| D8 | Food compliance fields, SKU weights/taxes and menu prices are missing in the companion | Obtain an approved record per SKU/menu item. Missing fields block publishing/selling; absence is not an empty string default | 1.4, 1.5, 2.5–2.7, 5.3 |
| D9 | Provider prices, offer eligibility, billing deadlines and legal dates are described as verified in the integration source | Preserve as source claims only. Recheck official terms at procurement/launch; do not encode rates, promotions or legal deadlines from this document | Budgets, onboarding, legal/privacy sign-off |
| D10 | Integration document assumes Shiprocket, SES, R2, Zoho Books and 2Factor | v4.1 specifies capabilities, not these providers. Select only necessary integrations with dependency/security review; keep accounting export separate from unrequested Zoho integration | Shipping, email, storage selection |
| D11 | Deployment capabilities remain unknown; SFTP is mentioned in earlier context | Obtain host/container/SSH or managed-runtime capabilities, domain control, backups and staging plan. Do not request credentials in documentation | Staging deployment and production cutover |
| D12 | Refund completion is equated to stock restoration | Track physical reservation/release separately from financial refunds. An expiry or pre-dispatch cancellation releases once; a refund alone must not restock shipped goods | Inventory/refund invariants |
| D13 | Raw provider events and consent IPs are proposed for storage without retention limits | Define minimal encrypted/restricted records, redaction, retention and deletion rules; do not put raw PII/events/tokens into logs or browser analytics | Data schema/security review |

### Correct feature references

Use the v4.1 identifiers by meaning; never perform a blind global renumbering.

| Meaning in integration document | v4.1 reference |
| --- | --- |
| Refund processing, sometimes called 3.8 | 3.7 |
| Customer cancellation, sometimes called 3.7 | 3.6 |
| Order lifecycle WhatsApp, sometimes called 3.6 | 3.5 |
| Order management/refund, sometimes called 5.6 | 5.4; v4.1 5.6 is franchise enquiry management |
| GST report, called 5.13 | 5.8 |
| Settlement reconciliation | Supporting integration safeguard, no standalone v4.1 feature |
| TOTP 2FA, email fallback, audit log, dead-letter alarm | Proposed safeguards/extensions; do not claim explicitly listed v4.1 features |

## Architecture proposal

Proposed paths are new implementation boundaries, not existing files:

| Boundary | Responsibility and behavior |
| --- | --- |
| `apps/web/` | Next.js App Router, server-rendered public pages, typed API wrapper, accessible forms and admin UI; retain existing public slugs |
| `apps/api/` | FastAPI thin async routes, server-side session/brand context, validation and services; authoritative stock, shipping, tax and payment totals |
| `packages/contracts/` | Generated OpenAPI and TypeScript client from FastAPI schemas; generation/parity gate, never handwritten contract fixes |
| PostgreSQL | Brand/content, catalog/food facts, outlets, admin/session, enquiries, inventory/reservations, order snapshots, payments/refunds, invoice allocation, outbox, audit and tracking token hashes |
| Redis | Distributed rate limiting and optional cache; fail safely for sensitive requests if limits cannot be enforced; no sole copy of stock or business events |
| Dedicated APScheduler process | Poll due outbox work, reclaim expired leases, reconcile providers, expire reservations and raise overdue-delivery alarms; do not start a scheduler per API worker |
| Docker | Reproducible web, API, scheduler, PostgreSQL and Redis services with health checks; reviewed version pins, persistent volumes and migration command |

Inference from the [APScheduler 3.x FAQ](https://apscheduler.readthedocs.io/en/3.x/faq.html):
a dedicated scheduler avoids the documented shared-job-store multiprocess
hazard. Revalidate against the version selected during implementation; this is
not a package pin or a claim of exactly-once delivery.

Use PostgreSQL transactions and conditional updates/row locks for stock,
reservation consumption and invoice allocation. Lock behavior is documented in
[PostgreSQL explicit locking](https://www.postgresql.org/docs/current/explicit-locking.html).
An outbox worker claims a bounded lease, commits, calls the provider outside the
transaction and records the result. Retries and crash recovery require stable
idempotency keys, provider reconciliation and unique business-event constraints;
an outbox alone cannot guarantee that a remote side effect happens exactly once.

### Critical flows and failure acceptance

- Public content: verified host/brand resolution → published content query →
  server-rendered page. Draft/incomplete product content must not leak through
  direct URLs, search, APIs, metadata, sitemap, previews or media references.
- Admin: named login → secure server session → authorization on every operation →
  validated write and actor audit. Include CSRF protection, session expiry,
  throttling and recovery. No shared passwords or readable provider secrets.
- Checkout: server re-reads prices, food-publish eligibility, tax, shipping,
  pincode and stock; accepts positive bounded quantities and integer paise.
  Create a durable, expiring reservation under concurrent stock checks, then a
  test-mode provider order. Repeated requests must not create duplicate orders.
- Payment: browser callback is provisional. Verify raw webhook bytes before
  parsing; persist an event durably before acknowledging it. Deduplicate event
  IDs and business transitions; match stored provider order, merchant, currency
  and expected amount. A failed attempt must not roll back a later capture.
  Late capture after reservation expiry needs explicit fulfillment/refund
  reconciliation; never silently oversell or drop paid money.
- Recovery: verified provider API reconciliation repairs missed webhooks using
  the same transition service. Razorpay distinguishes browser callbacks from
  server webhooks and documents supplemental API verification in its
  [webhook overview](https://razorpay.com/docs/webhooks/).
- Tracking: non-sequential public order identifiers, generic lookup failures and
  the proposed IP/order/phone limits from the integration source. Use an opaque
  CSPRNG bearer token with only a hash stored, expiry/revocation and minimal
  status output. Never log full tokens, include them in analytics or leak them
  via referrers. Tracking access alone should not expose an invoice/address or
  authorize a refund; define a separate scoped verification step for those.
- Franchise: validate/rate-limit → commit enquiry plus attribution and outbox in
  one transaction → acknowledge persistence → notify asynchronously. Preserve
  leads during provider outage and show retry/dead-letter status to staff.
- Cancellation/refund: serialize against dispatch; bound aggregate refunds to
  captured money; maintain child refund records. Restore inventory only from
  a justified physical stock transition, at most once. Duplicate or out-of-order
  refund events must not duplicate refunds or inventory.
- WhatsApp: explicit unselected opt-in and wording/version record, verified
  provider webhooks, status reconciliation, backoff and off-channel failure
  alarm. Do not represent HTTP acceptance as customer delivery.

## Phases and acceptance gates

Every phase is currently **planned, not implemented**. Work sequentially with
one in-progress plan item per task branch. Each phase ends in fresh verification,
security/design/SEO review as applicable, and its own PR. Recommendations below
do not change the active model/effort or authorize subagents.

| Phase | Observable acceptance | Planning model / effort | Implementation model / effort |
| --- | --- | --- | --- |
| A. Foundation and stored public content | Docker services start; one migration head; typed contract regenerates cleanly; published brand content reaches an SSR homepage; preview is private; cross-brand/draft-denial tests pass | `gpt-6-astra` / High | `gpt-6-astra` / High |
| B. Storefront and publishing | Existing seven public paths implemented; published catalog detail/filter/menu/outlets, policies and franchise models render from stored records; incomplete food records cannot publish; responsive/no-JS/browser/SEO gates pass | `gpt-6-astra` / High | `gpt-6-astra` / High |
| C. Admin and franchise pipeline | Named secure login and recovery; product/media/stock tools and enquiry form/pipeline; actor audit, spam controls and CSV safety; anonymous and cross-brand writes denied | `gpt-6-astra` / Extra High | `gpt-6-astra` / Extra High |
| D. Cart, checkout and test payments | Guest cart, pincode, shipping/tax, durable inventory reservations, Razorpay sandbox flow and retry; amount tampering, last-item race, late capture and duplicate/out-of-order events tested | `gpt-6-astra` / Extra High | `gpt-6-astra` / Extra High |
| E. Fulfillment and notifications | Restricted tracking/invoice access, courier booking/status, cancellation/refunds, WhatsApp consent/outbox/alarms and settlement reconciliation; outage/restart/replay tests pass | `gpt-6-astra` / Extra High | `gpt-6-astra` / Extra High |
| F. Reports, discovery and launch | GST report, P1 search/FAQ/testimonials/brochure/CSV/sales; GA4 approved and PII-safe; complete URL mapping, staging restore/launch checks and provider acceptance evidence | `gpt-6-astra` / High; Extra High for final security review | `gpt-6-astra` / High; Extra High for final security fixes |

Supporting published-content administration may begin in B; C completes admin
journeys and authentication must exist before any admin route is exposed.
External live-account setup can be prepared by FRAB while development proceeds;
no automatic account creation, real transaction, message sending or production
cutover is authorized by this plan.

### Complete v4.1 traceability

Rows group only adjacent features with the same phase. P0/P1 priorities are
preserved; no feature is implemented by this documentation PR.

| v4.1 IDs | Priority | Capability | Phase |
| --- | --- | --- | --- |
| 1.1 | P0 | Stored homepage hero, story, USPs, statistics | A–B |
| 1.2–1.4 | P0 | Category/price filtering, product detail and mandatory food facts | B |
| 1.5–1.8 | P0 | Priced dietary menu, franchise models, city/pincode map locator and outlet pages | B |
| 1.9–1.10 | P1 | Product search, FAQs and verified testimonials | F |
| 1.11–1.12 | P0 | Five policy pages and mobile responsiveness | B; all phases |
| 2.1–2.10 | P0 | Cart, guest checkout, serviceability, address, GST split, shipping, stock, Razorpay, confirmation and retry | D |
| 3.1–3.7 | P0 | Order/phone tracking, tax invoice, AWB booking, live tracking, WhatsApp, cancellation and refunds | E |
| 4.1 | P0 | Franchise enquiry fields | C |
| 4.2 | P0 | Staff WhatsApp notification | E |
| 4.3–4.5 | P0 | Source/campaign attribution, pipeline, spam and rate limits | C |
| 4.6–4.7 | P1 | Real brochure download and enquiry CSV export | F |
| 5.1–5.7 | P0 | Single-role named admin login; product/variant CSV; publish gate; orders/refunds/invoices; reason-coded stock; enquiries; reusable media | C, with payment/fulfillment operations completed in D–E |
| 5.8 | P0 | GST filing report | F |
| 5.9 | P1 | Sales summary by period | F |
| 6.1–6.4 | P0 | Public indexability (D2 pending), generated sitemap, truthful structured data and legacy redirects | A–B; complete inventory/launch validation in F |
| 6.5 | P0 | GA4 with approved property and privacy/consent behavior | F |

## Content and launch dependencies

FRAB supplies approved logo/food photos and use rights; one canonical legal
entity/contact/address set; verified outlet hours/coordinates; menu prices and
dietary/allergen details; product label/compliance packs, HSN/GST/weights; stock;
franchise investment/inclusion/royalty terms; policy text; shipping/serviceability
rules; brochure; notification recipients and consent; launch date and host.
Draft preview content may identify omissions; customer-facing production must
not publish invented values or claim that an inert form/payment succeeded.

No jurisdictional compliance or tax opinion is established by this plan. The
source's legal dates, GST treatment and fee arithmetic remain to be verified
against current official materials and business-approved policy before use.
Meta's pricing page returned HTTP 429 during this session, so its rate-card and
deadline claims remain unverified. This does not convert secondary sources into
authority. Official review entrypoint:
[Meta WhatsApp pricing](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing/).

## Verification and rollout contract

Introduce application gates with the corresponding layers; do not report the
current workflow tests as application coverage. Future checks include:

- Fresh API/service/contract tests; migration and restore tests against actual
  PostgreSQL/Redis; auth isolation, CSRF, upload and CSV-formula negative cases.
- Concurrent last-item purchase, abandoned checkout expiry, late capture,
  duplicate webhook, refunded/created reversal, provider timeout, worker crash,
  expired lease, duplicate courier booking and notification recovery scenarios.
- Server-rendered content without JavaScript, complete form error/empty/loading
  states, keyboard/touch/reduced-motion and axe at 360/390, 768 and 1280/1440.
- Production-build Lighthouse: performance ≥ 90, accessibility 100, best
  practices ≥ 90, SEO 100; LCP ≤ 2.5s, CLS ≤ 0.1, TBT ≤ 200ms. Keep budgets intact.
- Crawl/redirect manifest, sitemap/robots/canonicals/JSON-LD, direct draft route
  denial, sensitive-page authorization/noindex and analytics PII exclusions.
- Staging provider tests first. Production cutover requires complete approved
  content, host/runtime verification, backups/restore, current vendor onboarding
  checks and separately authorized live payment/refund/notification checks.

Retain the WordPress site until the replacement passes launch checks. A rollback
must preserve orders/webhook receipts and prevent two systems from accepting
independent payments for the same order. DNS/deployment changes and PR merging
require their own explicit instruction.
