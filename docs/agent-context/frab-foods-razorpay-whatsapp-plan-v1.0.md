# FRAB Foods India — Patnam Pakodi Commerce Platform
## Implementation Plan — Razorpay, WhatsApp (Meta layer), WhatsApp (BSP layer)

**Version 1.0** · Date: 9 September 2026 · Companion to MVP Application Features v4.1

---

## 1. Scope

This plan covers three integrations and the cascading consequences of the three v4.1 feature removals:

1. **Razorpay** — payments, refunds, reconciliation (features 2.8, 2.10, 3.8, 5.6, 5.13)
2. **WhatsApp — Meta layer** — Business Portfolio, WABA, phone number, INR billing, templates (features 3.6, 4.2)
3. **WhatsApp — BSP platform layer** — whether to buy one at all, and what changes if you do

Out of scope: Shiprocket, SES, Cloudflare R2, 2Factor, Zoho Books — except where the v4.1 removals change their status.

---

## 2. Confirmed facts, assumptions, unknowns

### 2.1 Confirmed (verified 9 September 2026)

| # | Fact | Source |
|---|---|---|
| C1 | Razorpay standard plan: 2% platform fee + 18% GST on the fee, for domestic cards, UPI, netbanking and wallets. No setup fee, no AMC. | Razorpay pricing blog, updated 26 Aug 2026 |
| C2 | Razorpay is running a **0% platform fee offer for new merchants** who complete KYC and activate on or after 1 July 2026, capped at **₹5 lakh cumulative GMV or 90 days from activation, whichever comes first**. One-time KYC fee ₹199 + tax. GST at 18% still applies, calculated on the standard 2% rate. Excludes prepaid cards, corporate cards, Amex, Diners, all EMI, and international. Not available to anyone who transacted on Razorpay before 1 July 2026. | Razorpay pricing blog + Razorpay 0% offer guide, Aug 2026 |
| C3 | Razorpay domestic settlement is typically **T+2 business days**. Credit Card on UPI (RuPay) is 2.15%, not 2%. EMI, corporate cards, Amex and Diners are 3%. | Razorpay pricing blog |
| C4 | UPI zero-MDR is a mandate on **banks**, not on the gateway. Razorpay still charges its 2% platform fee on UPI. "Free UPI" is not available on the standard plan. | Razorpay pricing blog, FAQ 8 |
| C5 | Meta charges **per delivered template message** since 1 July 2025, by category (marketing / utility / authentication) and by the **recipient's** country calling code. Non-template messages inside an open 24-hour customer service window are currently free. Utility templates inside an open window are currently free. | Meta developer docs, WhatsApp Business Platform pricing |
| C6 | **A business-initiated template does not open a customer service window.** Only an inbound message from the user does. | Meta developer docs, charge example |
| C7 | India INR billing localisation launched **1 January 2026**. Eligible customers (Sold-To country India) must migrate all WABAs in their business portfolio to INR by **31 December 2026**; from 1 January 2027 Meta will not deliver messages from non-INR WABAs of eligible customers. **WABA Currency Migration APIs have been available since 1 June 2026.** | Meta developer docs, billing localisation |
| C8 | From **1 October 2026**, Meta begins charging for service messages (free-form replies inside the 24-hour window) and for utility templates sent inside that window. Rates were to be published by 1 September 2026. | Meta developer docs pricing calendar; Zendesk, Wati, SendPulse advisories |
| C9 | Meta may change pricing only on the first day of a quarter — 1 Jan, 1 Apr, 1 Jul, 1 Oct — with minimum one month's notice for rate-card updates. | Meta developer docs, pricing calendar |
| C10 | Volume tiers for utility and authentication accrue **at business portfolio level across all WABAs**, and reset monthly. | Meta developer docs, volume tiers |
| C11 | DPDP Rules 2025 were notified 13 Nov 2025. Data Protection Board penalty powers commence **13 Nov 2026**; substantive obligations (notice, consent, rights, retention, security safeguards) commence **13 May 2027**. Maximum penalty ₹250 crore for failure to take reasonable security safeguards. | MeitY notifications, as reported by Indian law firms Aug–Nov 2025 |

### 2.2 Correction to a previously held assumption

**Previous position:** "WABA currency selection is irreversible — INR billing must be locked at WABA creation; one-way door."

**Current position:** This is no longer accurate. Meta published WABA Currency Migration APIs on 1 June 2026, and for India-domiciled customers INR is now **mandatory by 31 December 2026** rather than optional-and-permanent. The risk has changed shape: it is no longer "choose wrong and you are stuck", it is "**be on INR before 31 December 2026 or Meta stops delivering your messages**". Still time-sensitive, but recoverable.

**Practical effect:** create the WABA in INR from the start (it will be the default if your Billing Hub Sold-To country is India), and verify the currency on the WABA after creation rather than assuming.

### 2.3 Working assumptions (flagged — replace with real figures)

| # | Assumption | Used for | If wrong |
|---|---|---|---|
| A1 | ~500 orders/month at launch, AOV ~₹500 → ~₹2.5 lakh monthly GMV | Cost model, Razorpay offer timing | The ₹5 lakh GMV cap on the Razorpay offer is hit sooner; offer value drops |
| A2 | ~4 WhatsApp utility messages per order (confirm, dispatch, delivery, plus one exception) | Meta message cost | Linear scaling; low absolute impact either way |
| A3 | No shared WhatsApp inbox is required at MVP — v4.1 contains no inbox, chatbot or broadcast feature | BSP vs direct recommendation | **This is the single assumption that flips the BSP decision.** See §4 |
| A4 | Marketing broadcasts are not in MVP scope (no feature in v4.1 covers them) | Cost model, template categories | Adds ₹0.86/message + GST and changes BSP value |
| A5 | Admin 2FA (v4.1 item 5.1) will be TOTP/authenticator-app based, not SMS | Whether 2Factor survives as a vendor | If SMS 2FA, 2Factor stays and DLT registration may be needed |

### 2.4 Unknowns that block final decisions

Listed in §12. These are questions, not assumptions — nothing below silently guesses at them.

---

## 3. Consequences of the three v4.1 removals

### 3.1 Removing OTP from order tracking (3.1)

**What changes:** order lookup is now protected by order number + phone number only. Both are low-entropy if order numbers are sequential.

**Risk:** enumeration. `PP-1001`, `PP-1002` with a common phone prefix is brute-forceable, and every successful hit exposes a delivery address, items and order value — personal data under DPDP.

**Required mitigations (all three, not one):**

1. **Non-sequential order numbers.** Format `PP-` + 8 characters from a Crockford base32 alphabet, generated from a CSPRNG, uniqueness-checked on insert. Keep a separate internal sequential ID for accounting; never expose it.
2. **Rate limiting.** Per-IP: 5 lookup attempts per minute, 30 per hour. Per-order-number: 5 failed attempts then a 30-minute lock. Per-phone: 20 per hour. Implemented in Valkey with a sliding window. Return an identical generic failure message for "not found" and "phone mismatch" — never confirm that an order number exists.
3. **Signed tracking link as the primary path.** Every order confirmation email and WhatsApp message carries `/track/<opaque-token>`, where the token is a 128-bit random value stored against the order, expiring 90 days after delivery. This becomes the route 95% of customers use; the manual form becomes the fallback. This is what actually removes the friction OTP was providing, rather than just removing the security.

**Vendor consequence:** with OTP gone from 3.1, and assuming TOTP-based admin 2FA (A5), **v4.1 contains no SMS use case at all**. 2Factor can be dropped from the vendor stack, along with the TRAI DLT template and header registration overhead that SMS would have required. Confirm A5 before removing.

**Also affected:** partial-order-number logging. Do not log full order numbers in application logs that ops can read casually.

### 3.2 Removing email from the franchise alert (4.2)

**What changes:** WhatsApp is now the only push channel telling the franchise team a lead has arrived.

**Risk:** a WhatsApp delivery failure — expired access token, template paused for quality, number quality-rated Red, team member's phone off WhatsApp, Meta outage — becomes a silently lost lead. Franchise leads are the highest-value conversion on the site.

**Required mitigations:**

1. **The database is the system of record, not the message.** The enquiry is written and committed before any notification is attempted. Feature 4.4 (pipeline) already gives the team a place to see leads independently of the alert.
2. **Delivery-status reconciliation.** Meta returns `sent` → `delivered` → `read` webhooks. Store the message status against the enquiry. Any enquiry with no `delivered` status after 10 minutes raises an internal alarm.
3. **A second channel for the alarm only.** Since email is removed from 4.2 as a lead-alert channel, route the *failure alarm* somewhere non-WhatsApp — an ops email via SES, or a daily digest. This is not re-adding 4.2's email; it is monitoring the channel that replaced it.
4. **Unassigned-lead SLA report** in the admin panel: any enquiry still in `new` after 4 working hours is highlighted.

**Template-category risk:** an internal alert to your own staff is not a transaction *with that recipient*. Meta may classify a "new franchise enquiry" template as marketing rather than utility, at roughly 7.5× the per-message rate and with no in-window exemption. Volume is trivial (a few hundred a month), so the cost is immaterial — but a marketing-categorised template is also subject to stricter quality enforcement. Write the template in strictly operational language and monitor its assigned category after approval.

### 3.3 Removing role-based login (5.1)

**What changes (under the stated interpretation):** one admin role. Everyone who can log in can see orders, customer names, phone numbers, delivery addresses, refunds, franchise leads and integration credentials.

**Risks:**

1. **Credential blast radius.** A compromised or shared login is now a full-platform compromise, including the Settings screen holding Razorpay and Meta credentials.
2. **DPDP posture.** Substantive obligations including reasonable security safeguards commence 13 May 2027 (C11). Least-privilege access control is a standard element of "reasonable security safeguards". This is not a live breach today, but it is technical debt with a dated deadline, and it is far cheaper to build the role column now than to retrofit it into a live admin panel later.
3. **Franchise sales access.** The removed role list included "franchise sales" — a function often staffed by external or commission-based people. Under a single role they get order and refund access.

**Required mitigations:**

1. **Keep authentication and 2FA.** Confirm this reading (see §12 Q1).
2. **Do not delete the schema.** Keep a `role` column on the admin user table, defaulted to `admin`, unused at MVP. Zero cost now; makes the Phase 2 restoration a migration rather than a rebuild.
3. **Credential isolation.** Do not store Razorpay or Meta secrets in a database table rendered by the Settings screen. Keep them in environment variables / a secrets store; let Settings show masked last-4 and a "rotate" action only.
4. **Audit log carries the weight.** With roles gone, feature 5.10 is the only accountability control. It must record actor user ID, timestamp, IP, entity, before and after values, on every write — including refunds and stock adjustments — and must not be deletable from the UI.
5. **Named accounts, no shared login.** Enforce one account per person. A shared `admin@` login makes the audit log worthless.

---

## 4. Decision: WhatsApp direct on Meta Cloud API, or through a BSP?

### 4.1 What each layer actually is

- **Meta layer (unavoidable).** The WhatsApp Business Platform. Meta hosts the Cloud API, charges per delivered template message, approves templates, verifies the business, rates number quality. Every route goes through this.
- **BSP layer (optional).** AiSensy, Interakt, Wati, Gupshup, Twilio, 360dialog and others resell access and wrap it in software — shared inbox, campaign builder, chatbot, contact management, onboarding help. **The underlying API is identical whichever you choose.** You are buying software and hand-holding, not capability.

Meta permits both partner-mediated and **directly-integrated clients**; its own billing localisation documentation addresses the two on equal terms.

### 4.2 Comparison against this project

| Dimension | Meta Cloud API direct | BSP (packaged, e.g. AiSensy / Interakt tier) | Thin BSP (e.g. 360dialog) |
|---|---|---|---|
| Platform fee | ₹0 | roughly ₹999–₹2,499/month + GST at entry tiers (published figures vary by month — get a written quote) | flat per-number hosting fee, low or no per-message markup |
| Per-message markup | none — Meta rate only | some plans add a markup on marketing messages | typically pass-through |
| Engineering effort for v4.1 scope | ~3–5 days: template send, status webhooks, retry | ~1–2 days: SDK or REST wrapper | ~3–5 days, similar to direct |
| Shared team inbox | none | included | none |
| Campaign / broadcast UI | none | included | none |
| Template management | Graph API or Business Manager UI | vendor UI | vendor UI |
| Onboarding help | self-serve | assisted | limited |
| Extra vendor in the stack | no | yes — another contract, another DPA, another credential | yes |
| Fit with FastAPI + Celery + Valkey | native — this is exactly the shape of the existing stack | wrapper over an API you could call directly | native |
| Multi-brand future (brand 2, 3…) | you own the abstraction; add a WABA per brand under one portfolio | per-number or per-workspace pricing multiplies | per-number fee multiplies |

### 4.3 Recommendation — **Meta Cloud API direct**

**Why, in order of weight:**

1. **v4.1 contains no feature a BSP would provide.** 3.6 is templated outbound. 4.2 is templated outbound. There is no inbox feature, no broadcast feature, no chatbot feature. You would be paying ₹12,000–₹30,000 a year for software that no requirement asks for. (This inverts if A3 is wrong — see §12 Q4.)
2. **The stack already does this work.** Celery + Valkey is exactly the retry-and-queue infrastructure a message sender needs. A BSP's value is largest for teams with no backend; you have one.
3. **Cost structure is right for multi-brand.** BSP pricing is generally per-number or per-workspace. Every new brand entity multiplies it. Direct integration means brand two costs one more WABA under the same portfolio and no new licence — and volume tiers accrue at portfolio level across all WABAs (C10), so keeping brands in one portfolio compounds the benefit.
4. **Fewer credentials to hold** in an admin panel that, post-5.1-removal, has no role separation (§3.3).

**What you give up, honestly:** assisted onboarding through Meta business verification, which is genuinely fiddly the first time; a ready-made inbox if the franchise team later wants to converse with leads on WhatsApp rather than call them; and a support desk to shout at when a template gets rejected.

**Switching cost if you change your mind:** real but bounded — migrating a verified number to a BSP requires re-verification and re-approval of every template. Since MVP has fewer than fifteen templates, this is a day's work, not a rebuild. That asymmetry is what makes starting direct the low-regret choice.

**When to revisit:** if and when the franchise team asks to *reply* on WhatsApp at volume, or marketing broadcasts enter scope. At that point re-evaluate, and price the thin-BSP option (360dialog-style pass-through) before the packaged ones.

---

## 5. Razorpay implementation

### 5.1 Account and activation — the timing decision

The 0% offer (C2) burns from **activation**, on a **90-day or ₹5 lakh GMV, whichever first** basis. At assumption A1 (₹2.5 lakh/month), ₹5 lakh GMV arrives in roughly two months — so the GMV cap, not the 90 days, is the binding constraint.

The trap: activating in, say, October to "get set up early" while the site launches in December means the entire offer expires before the first real rupee is processed. Value forfeited at A1 volumes: roughly ₹10,000 in platform fees.

**Recommendation:**

- Build the entire integration on **test mode keys**. Test mode needs no KYC and no activation. Nothing in development requires a live account.
- Submit KYC only when the launch date is inside a 4-week window and the storefront is deployable, because Razorpay's activation review inspects the live website — it needs working policy pages (feature 1.11), visible pricing, contact details and a functioning product listing. **Feature 1.11 is a hard dependency on Razorpay activation, not a nice-to-have.**
- Confirm in writing with Razorpay support whether the offer clock starts at activation approval or first transaction, before submitting. Do not rely on this document or on the blog wording for a decision worth ₹10,000.
- Note the odd condition in C2: GST at 18% is stated to continue applying, calculated on the standard 2% rate, even during the 0% period. Verify this with Razorpay — it materially changes what "0%" means (roughly ₹900/month rather than ₹0 at A1 volumes).

**Do not** let anyone transact on a Razorpay account under the same PAN before 1 July 2026 eligibility is confirmed — prior-merchant status disqualifies the offer entirely.

### 5.2 Payment flow

Server-authoritative throughout. The browser never decides anything financial.

1. Client posts the cart. Server recalculates line items, GST (2.5), shipping (2.6) and validates stock (2.7). **Never trust a client-supplied amount.**
2. Server reserves stock with a TTL of 15 minutes in Valkey, keyed to an internal order draft.
3. Server calls Razorpay **Orders API**, storing `razorpay_order_id` against the draft. Set capture to **automatic** — manually-captured payments are auto-refunded by Razorpay if not captured in time, which is a silent revenue leak nobody notices for weeks.
4. Client opens Razorpay Checkout with the order ID.
5. On checkout callback, verify the returned signature and show the customer a result page. **This display is provisional.** Show "payment received, order confirming" — never a confirmed order number sourced from the callback alone.
6. **The webhook decides.** `payment.captured` (or `order.paid`) transitions the draft to a confirmed order, converts the stock reservation to a decrement, generates the invoice number and enqueues notifications.

This preserves the existing principle: **webhooks are the sole source of truth for payment state.** The redirect is a UX signal only. A customer whose browser dies after paying still gets a confirmed order.

### 5.3 Webhook handling

**Subscribe to:** `payment.captured`, `payment.failed`, `order.paid`, `refund.created`, `refund.processed`, `refund.failed`. Optionally `payment.dispute.created`.

**Endpoint contract:**

- Verify `X-Razorpay-Signature` (HMAC-SHA256 over the raw body with the webhook secret) **before parsing**. Reject with 400 on mismatch. Use a constant-time comparison.
- Read the raw request body for signature verification. A JSON round-trip changes the bytes and breaks the HMAC — this is the single most common integration failure.
- Persist the raw event to a `payment_webhook_events` table with a unique constraint on the Razorpay event ID. A duplicate insert means a redelivery: return 200 and stop.
- Return **200 within a couple of seconds**. Do the work in Celery. Razorpay retries on non-2xx, and a slow endpoint produces a storm of duplicate events.
- Handle **out-of-order delivery**. Do not write state transitions blindly; use an explicit state machine (`draft → pending → paid → shipped → delivered`, plus `failed`, `cancelled`, `refunded`) and reject transitions that go backwards. `refund.processed` can and does arrive before `refund.created`.
- Row-lock the order (`SELECT … FOR UPDATE`) inside the transaction that applies a payment event.
- Keep the endpoint out of the brand-scoped RLS path or ensure the webhook worker has an explicit brand context — Razorpay does not know about `brand_id`. Resolve the brand from the stored order, never from the payload.

### 5.4 Refunds (3.8) and cancellations (3.7)

- Cancellation before dispatch (3.7) triggers a refund via the Refunds API against the payment ID, `speed: normal` — instant refunds carry a fee and MVP does not need them.
- Refund state is driven by `refund.processed`, not by the API call's response.
- Restore stock **on `refund.processed`**, not on refund initiation, to avoid restoring inventory for a refund that later fails.
- Surface a customer-visible expectation of 5–7 working days for the money to reach the bank; this is the single largest source of support contacts in Indian e-commerce refunds.
- Partial refunds: model refunds as a child table with amounts, never as a boolean on the order.

### 5.5 Reconciliation and accounting

- Settlement is **T+2 business days** (C3). Model the working-capital gap against Shiprocket's prepaid wallet — courier charges are payable before Razorpay settles the money that funds them. Keep a float.
- Pull the Settlements API daily into a `settlements` table and reconcile: sum of captured payments minus fees minus refunds should equal the settled amount. Flag any mismatch older than three days.
- Razorpay's fee and its GST are deducted at source. Book the gross sale, the fee and the input GST on the fee separately, or the GST report (feature 5.13) will misreport. Feed this to Zoho Books.
- The tax invoice (3.2) is generated on payment capture with a gapless invoice series. Do not reuse or skip numbers on failed payments — use a separate sequence from order numbers.

### 5.6 Not in MVP but worth knowing

**Razorpay Route** (split payments) is the mechanism you would use if franchisee-owned outlets ever receive a share of an online order. It is not needed for MVP and should not be enabled now. Note it in the Phase 2 backlog for the franchise expansion, and raise it in the same conversation as any custom-pricing negotiation — split-settlement volume strengthens the negotiating position.

**Custom pricing:** the 2% list rate is negotiable at sustained volume. Do not open that conversation at launch with no volume history. Diarise it for month four, armed with three months of actual GMV.

---

## 6. WhatsApp — Meta layer setup

### 6.1 Prerequisites (gather before touching the console)

| Item | Note |
|---|---|
| Meta Business Portfolio | Use a company-owned portfolio, not an employee's personal Facebook account. This is a recurring cause of losing access when someone leaves. |
| Business verification documents | Legal entity name must match exactly across GST certificate / CIN / Udyam, the website footer and the portfolio name. FRAB Foods India vs Patnam Pakodi naming needs deciding — see §12 Q5. |
| A dedicated phone number | Must **not** be active on a personal WhatsApp or WhatsApp Business app account. Given four numbers are currently in circulation on the live site, procure a **fresh number** reserved solely for the API rather than reusing a published one. Deleting an existing WhatsApp account to free a number loses that chat history permanently. |
| Business email on the company domain | Generic Gmail addresses slow verification. |
| Live website | Must show the business name, address and contact details consistent with the verification documents. |
| Billing Hub Sold-To country = India | Drives INR billing (C7). Verify after WABA creation; do not assume. |

### 6.2 Sequence

1. Create / confirm the Meta Business Portfolio; add at least two admins.
2. Submit **business verification**. Allow 2–10 working days; longer if documents mismatch. Start this first — it gates everything else and is the longest pole.
3. Create the **WABA**. Confirm currency is **INR** (C7). If it is not, use the Currency Migration APIs before going live, and in any case before 31 December 2026.
4. Register the phone number; complete the display-name review. Display name must relate to the business — "Patnam Pakodi" is compliant.
5. Add a payment method to the WABA. **Set a billing alert.** An expired card silently stops message delivery, which after the 4.2 change means silently losing franchise leads.
6. Generate a **System User** token, not a user token. User tokens die when the person leaves or changes password. Grant `whatsapp_business_messaging` and `whatsapp_business_management`. Store in the secrets store, never in the Settings table (§3.3).
7. Configure the webhook endpoint with a verify token; subscribe to `messages` (for delivery statuses) and `account_update`.
8. Submit templates for approval (§6.4). Allow up to 24 hours each; budget for one rejection round.
9. Green tick (Official Business Account) is free and optional. Apply after launch; do not let it block go-live and do not pay anyone claiming to fast-track it.

### 6.3 Cost model at MVP volume (assumptions A1, A2, A4)

Meta INR list rates reported as effective 1 July 2026: marketing ₹0.8631, utility ₹0.1150, authentication ₹0.1150 per delivered message, before 18% GST. **These are secondary-source figures — verify against the INR rate-card CSV linked from Meta's pricing documentation before budgeting.**

| Line | Volume/month | Rate | Cost |
|---|---|---|---|
| Utility templates (order lifecycle) | 2,000 | ₹0.1150 | ₹230 |
| Utility templates (franchise alerts, if utility-categorised) | ~300 | ₹0.1150 | ₹35 |
| Meta subtotal | | | **₹265** |
| + 18% GST | | | ₹313 |
| BSP platform fee — direct route | | | **₹0** |
| BSP platform fee — packaged BSP for comparison | | ₹999–₹2,499 + GST | ₹1,179–₹2,949 |

**The finding that should drive the decision:** at MVP volume, Meta's messaging charge is roughly ₹300 a month. A packaged BSP subscription costs **four to nine times the messages themselves**. Optimising the message mix is not where the money is; the platform fee is.

**Exposure to the 1 October 2026 change (C8) is low.** Because a business-initiated template does not open a customer service window (C6), Patnam Pakodi's order notifications are almost all sent *outside* any open window and are therefore already billable today. The in-window exemption being withdrawn changes little here. This would be a different conversation if a shared inbox and live agent replies were in scope — another reason the BSP question and the October change are the same question.

### 6.4 Template catalogue

Submit these; keep the names stable, version by suffix when content changes.

| Template | Category | Trigger | Variables |
|---|---|---|---|
| `order_confirmed_v1` | Utility | `payment.captured` webhook | order no, item count, amount, tracking URL |
| `order_dispatched_v1` | Utility | Shiprocket AWB generated (3.3) | order no, courier, AWB, tracking URL |
| `order_delivered_v1` | Utility | Shiprocket delivery status (3.4) | order no |
| `order_cancelled_v1` | Utility | Cancellation confirmed (3.7) | order no, refund amount, expected days |
| `refund_processed_v1` | Utility | `refund.processed` webhook | order no, amount |
| `payment_failed_v1` | Utility | `payment.failed` webhook | order no, retry URL |
| `franchise_enquiry_alert_v1` | Utility (monitor assigned category — §3.2) | Enquiry committed (4.1) | name, city, preferred model, phone |
| `franchise_enquiry_ack_v1` | Utility | Enquiry committed | name, callback window |

**Rules:**

- Every customer-facing template carries the signed tracking link from §3.1 — this is what replaces the removed OTP.
- Do not put marketing language ("try our new…") in a utility template. Meta re-categorises on content, and a re-categorised template is charged at the marketing rate and can be paused.
- Store the template name, language and variable order in code, not in the database, so a template change is a reviewed deploy.

### 6.5 Opt-in, consent and quality

- Meta requires opt-in before business-initiated messaging. Add a checkbox at checkout: *"Send my order updates on WhatsApp to this number."* Record the exact wording version, timestamp and IP against the order — this is the evidence trail DPDP will expect from 13 May 2027 (C11), and Meta will ask for it if quality is challenged.
- Do **not** pre-tick it. A pre-ticked consent box is weak evidence of freely given consent and is the first thing an auditor questions.
- **Email (3.5) remains the guaranteed channel.** Make email mandatory at guest checkout (2.2, 2.4) since it is the fallback when WhatsApp consent is declined or delivery fails.
- New WABAs start at a limited messaging tier (typically 250 unique recipients per 24 hours) and scale with quality and volume. At A1 volumes this is not a constraint, but check it before any first-time bulk send.
- Monitor number quality rating in Business Manager weekly. A drop to Red throttles delivery. The main causes are blocks and reports, which are driven by unwanted marketing — a further argument for keeping marketing out of MVP.
- For future brands: one WABA per brand, all under **one business portfolio**, so utility volume aggregates toward the same tiers (C10).

---

## 7. If the BSP route is chosen instead

Only if §12 Q4 resolves toward a shared inbox or broadcasts being in scope.

- **Shortlist by what you actually need**, not by feature-list length: a thin, pass-through BSP if you only want managed infrastructure; a packaged Indian BSP if the franchise team genuinely wants a UI to converse in.
- **Get every quote in writing** with: monthly platform fee, per-message markup by category, number of agent seats included, setup fee, contract term, and whether Meta charges are passed through at cost or marked up. Published pricing pages move frequently and often exclude the markup.
- **Confirm INR billing and a GST invoice from an Indian entity**, so input credit is available. Ask your CA to confirm treatment for both the BSP fee and the Meta charge.
- **Ask about number portability up front**: can you take your verified number and templates to another BSP or to direct Cloud API, and what does it cost? Ask before signing, not after.
- **Keep the abstraction.** Whichever way this goes, write the application against an internal `NotificationChannel` interface with a WhatsApp implementation behind it. This is a few hours' work and makes the direct↔BSP decision reversible instead of structural.
- Sign a DPA covering customer phone numbers and order data.

---

## 8. Application architecture for both integrations

**Transactional outbox.** Both Razorpay webhooks and WhatsApp sends go through one pattern:

1. Business event commits to PostgreSQL, writing a row to `outbox_messages` in the **same transaction**.
2. A Celery worker polls the outbox and dispatches.
3. Dispatch result and provider message ID are written back; failures retry with exponential backoff (1m, 5m, 30m, 2h), then dead-letter.

This is what prevents the two failure modes that matter: an order that is paid but never notified, and a notification sent for an order that rolled back.

**Tables to add:**

| Table | Purpose |
|---|---|
| `payment_webhook_events` | Raw Razorpay events, unique on provider event ID — idempotency |
| `payments`, `refunds` | Payment and refund state, unique on provider IDs |
| `settlements` | Daily settlement pull for reconciliation |
| `outbox_messages` | Pending and sent notifications, with attempt count |
| `whatsapp_messages` | Provider message ID, template name, recipient, status timeline |
| `consent_records` | Channel, wording version, timestamp, IP — DPDP evidence |
| `order_tracking_tokens` | Opaque token, order ID, expiry (§3.1) |

**Secrets:** Razorpay key/secret, Razorpay webhook secret, Meta system user token, Meta webhook verify token — environment or secrets store, masked in the admin UI, rotatable without a deploy.

**Observability:** alert on webhook signature failures (attack or misconfiguration), on outbox dead-letters, on any WhatsApp message without a `delivered` status after 10 minutes, and on Razorpay settlement mismatches.

---

## 9. Step-by-step execution plan

Dependencies matter more than dates here; sequence is fixed, calendar is yours.

### Phase 0 — Decisions and paperwork (start immediately, runs in parallel with build)

| # | Action | Owner | Blocks |
|---|---|---|---|
| 0.1 | Answer the open questions in §12 — particularly Q1 (5.1 intent) and Q4 (shared inbox) | FRAB | Everything below |
| 0.2 | Procure a fresh, unused phone number for the WABA | FRAB | 6.2 step 4 |
| 0.3 | Confirm the legal entity name and consolidate the four circulating phone numbers and two office addresses into one canonical set | FRAB | Business verification, and features 1.8, 1.11 |
| 0.4 | Submit Meta business verification | FRAB + dev | WABA creation |
| 0.5 | Confirm Razorpay 0% offer mechanics in writing (clock start, GST treatment) | FRAB | 5.1 activation timing |
| 0.6 | Confirm whether admin 2FA is TOTP or SMS (A5) → decide 2Factor's fate | FRAB | Vendor doc update |

### Phase 1 — Build against test/sandbox

| # | Action | Depends on |
|---|---|---|
| 1.1 | Razorpay test-mode integration: Orders API, checkout, signature verification | — |
| 1.2 | Webhook endpoint with signature verification, raw-body handling, idempotency table | 1.1 |
| 1.3 | Order state machine, stock reservation and release | 1.2 |
| 1.4 | Non-sequential order numbers + tracking tokens (§3.1) | — |
| 1.5 | Rate limiting on order lookup in Valkey (§3.1) | 1.4 |
| 1.6 | Transactional outbox + Celery dispatch (§8) | — |
| 1.7 | Notification channel abstraction; email (SES) implementation first | 1.6 |
| 1.8 | Refund and cancellation flows | 1.3 |
| 1.9 | Invoice generation with its own gapless series | 1.3 |
| 1.10 | Consent capture at checkout, `consent_records` | — |
| 1.11 | Admin audit log with actor on every write (§3.3) | — |

### Phase 2 — Meta layer live

| # | Action | Depends on |
|---|---|---|
| 2.1 | Create WABA, confirm INR currency, register number, display-name review | 0.4, 0.2 |
| 2.2 | System user token, webhook subscription, billing method + alert | 2.1 |
| 2.3 | Submit all templates in §6.4; budget one rejection round | 2.1 |
| 2.4 | WhatsApp channel implementation behind the §1.7 abstraction | 1.7, 2.2 |
| 2.5 | Delivery-status webhook handling and the 10-minute undelivered alarm | 2.4 |
| 2.6 | Franchise alert path end-to-end, including the failure alarm (§3.2) | 2.4 |

### Phase 3 — Razorpay live

| # | Action | Depends on |
|---|---|---|
| 3.1 | Deploy storefront with policy pages (feature 1.11) publicly reachable | Storefront build |
| 3.2 | Submit Razorpay KYC — **only once launch is within ~4 weeks** (§5.1) | 3.1, 0.5 |
| 3.3 | Swap to live keys; register live webhook URL and secret | 3.2 |
| 3.4 | Two real low-value end-to-end transactions: UPI and card | 3.3 |
| 3.5 | Two real refunds; verify money movement and `refund.processed` | 3.4 |
| 3.6 | Settlement reconciliation job running against real settlements | 3.4 |

### Phase 4 — Pre-launch verification

| # | Action |
|---|---|
| 4.1 | Kill the webhook worker mid-payment; confirm the order still confirms on retry |
| 4.2 | Replay a duplicate webhook; confirm no double order, no double refund |
| 4.3 | Send an out-of-order refund event pair; confirm the state machine holds |
| 4.4 | Attempt order-lookup enumeration; confirm rate limiting and generic errors |
| 4.5 | Expire the Meta token deliberately; confirm the franchise-alert alarm fires |
| 4.6 | Verify every template renders correctly on a real device, including the tracking link |
| 4.7 | Confirm WABA currency is INR (deadline 31 December 2026) |
| 4.8 | Re-check Meta's INR rate card and the 1 October 2026 service-message rates against the budget |

---

## 10. Mistakes to avoid

| # | Mistake | Cost |
|---|---|---|
| 1 | Treating the Razorpay redirect response as payment confirmation | Orders lost when the browser closes; orders created for failed payments |
| 2 | Parsing the webhook body before verifying the signature, or verifying against re-serialised JSON | Signature checks that always fail, or an endpoint that accepts forged events |
| 3 | Doing work synchronously inside the webhook handler | Timeouts, Razorpay retries, duplicate processing |
| 4 | Assuming webhooks arrive in order or exactly once | Refunds double-processed; stock restored twice |
| 5 | Activating Razorpay months before launch | Forfeits the 0% offer — roughly ₹10,000 at A1 volumes |
| 6 | Sequential order numbers now that OTP is gone from 3.1 | Order enumeration exposing customer addresses |
| 7 | Distinguishing "order not found" from "phone doesn't match" in the error message | Confirms valid order numbers to an attacker |
| 8 | Registering the WABA on a number already used on personal WhatsApp | Number unusable, or history destroyed to free it |
| 9 | Using a personal Facebook account or a user access token | Access lost when someone leaves; messages silently stop |
| 10 | No billing alert on the Meta payment method | Expired card stops delivery; with 4.2's email gone, franchise leads vanish silently |
| 11 | Marketing language inside a utility template | Re-categorisation at ~7.5× the rate, plus quality risk |
| 12 | Pre-ticked WhatsApp consent | Weak DPDP consent evidence; higher block rate; quality-rating damage |
| 13 | Making WhatsApp the only notification channel because it is cheaper | Email is the fallback that keeps 3.5 meaningful when consent is declined |
| 14 | Storing Razorpay/Meta secrets in a Settings table readable by every admin | With roles removed (§3.3), one compromised login exposes payment credentials |
| 15 | Buying a BSP subscription before any feature needs one | ₹12,000–₹30,000/year against ~₹300/month of actual messaging |
| 16 | Deleting the `role` column because 5.1 was removed | Turns a Phase 2 migration into a rebuild, ahead of DPDP's 13 May 2027 date |
| 17 | Booking Razorpay's fee net against revenue | Misstated GST report (feature 5.13) |
| 18 | Ignoring the 31 December 2026 INR migration deadline | Meta stops delivering messages from 1 January 2027 |

---

## 11. Checklist

**Decisions**
- [ ] 5.1 intent confirmed — role separation removed, authentication retained
- [ ] Shared WhatsApp inbox confirmed out of MVP scope
- [ ] WhatsApp route confirmed: Meta Cloud API direct
- [ ] Admin 2FA method confirmed (TOTP vs SMS) → 2Factor retained or dropped
- [ ] Canonical phone numbers, addresses and legal entity name agreed

**Razorpay**
- [ ] Test-mode integration complete and passing Phase 4 tests
- [ ] Offer mechanics confirmed in writing with Razorpay
- [ ] Policy pages (1.11) live before KYC submission
- [ ] KYC submitted within ~4 weeks of launch
- [ ] Auto-capture enabled
- [ ] Webhook secret set; signature verification on raw body
- [ ] Idempotency table with unique constraint on event ID
- [ ] State machine rejects backwards transitions
- [ ] Refund flow tested with real money
- [ ] Settlement reconciliation job running
- [ ] Invoice series gapless and separate from order numbers
- [ ] T+2 working-capital float sized against Shiprocket wallet

**WhatsApp — Meta**
- [ ] Business verification approved
- [ ] WABA created; **currency confirmed INR**
- [ ] Fresh dedicated number registered; display name approved
- [ ] System user token issued and stored in secrets store
- [ ] Payment method added; billing alert configured
- [ ] All templates in §6.4 approved; assigned categories checked
- [ ] Delivery-status webhooks stored against orders and enquiries
- [ ] Undelivered-alert alarm tested by deliberate failure
- [ ] Messaging tier and quality rating checked
- [ ] Opt-in checkbox live, unticked, with consent records written

**v4.1 removals**
- [ ] Order numbers non-sequential
- [ ] Rate limiting live on order lookup
- [ ] Signed tracking links in every notification
- [ ] Generic error message on failed lookup
- [ ] Franchise pipeline confirmed as system of record
- [ ] Franchise alert failure alarm routed off-WhatsApp
- [ ] Audit log records actor on every write
- [ ] Named admin accounts only; no shared login
- [ ] `role` column retained, defaulted, unused
- [ ] Payment/Meta secrets outside the Settings table

**Documents**
- [ ] PRD, TRD, Feature List v3.2, App Flow updated for the three removals and section 5 renumbering
- [ ] Vendor documents updated for 2Factor status and the direct-Cloud-API decision

---

## 12. Open questions

| # | Question | Why it matters | Blocks |
|---|---|---|---|
| Q1 | On 5.1 — remove role *separation* but keep authentication and 2FA? Or something else? | If authentication itself were removed, the admin panel would be publicly accessible. The v4.1 line assumes the former. | Feature list finalisation, TRD |
| Q2 | How many people will have admin access at launch, and does that include anyone outside FRAB (agency, franchise consultant)? | Determines whether single-role access is tolerable or whether roles must return before launch | §3.3 mitigations |
| Q3 | Which WhatsApp numbers receive the 4.2 franchise alert, and are those staff numbers company-controlled? | Personal numbers mean leads leave with the employee; also affects opt-in | Template + routing |
| Q4 | Will the franchise team need to *reply* to leads on WhatsApp from a shared inbox, or will they call from the pipeline? | **The single question that decides direct vs BSP.** A shared inbox is not in v4.1 | §4 recommendation |
| Q5 | Which name goes on the WABA and Razorpay account — FRAB Foods India or Patnam Pakodi? | Must match verification documents; also affects multi-brand structure when brand two arrives | Phase 0.4, 3.2 |
| Q6 | Target launch date? | The Razorpay 0% offer is worth roughly ₹10,000 and is destroyed by activating too early | Phase 3 timing |
| Q7 | Are marketing broadcasts planned within six months of launch? | Changes the cost model by an order of magnitude and revisits Q4 | Budget, §4 |
| Q8 | Is email mandatory at guest checkout? | It is now the only guaranteed customer channel when WhatsApp consent is declined | Feature 2.4 |

---

*FRAB Foods India — Confidential*
