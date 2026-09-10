# Approved MVP implementation — 2026-09-10

Authority: the user approved the reconciled plan with “Implement the plan”.
Original source documents remain unchanged. These decisions supersede conflicting
proposals in the older reconciliation, including its courier/email assumptions.

Customers request packaged products from one stock location. Any valid Indian
address may request delivery. Staff approve delivery and enter its fee before
payment. Quotes last 24 hours; inventory reservations start on payment initiation
and last 15 minutes. Payment uses Razorpay. Staff manually mark dispatched,
delivered or delivery issues; there is no courier, AWB, rider or GPS integration.

Customer notifications are opt-in WhatsApp only, through Meta Cloud API. No
shared inbox, broadcasts, SMS or email provider. Failed/overdue notifications
appear in admin with retry controls. Private order links authorize payment,
invoice download and pre-dispatch cancellation; order/phone lookup exposes only
basic status. Named admins require password + TOTP and recovery codes.

Keep the approved stack: Next.js, FastAPI, PostgreSQL, APScheduler, Redis, Docker.
Keep the approved cream design and public-only indexing. P0 is the first release;
P1 search, FAQs/testimonials, brochure, enquiry CSV and sales summary follow it.
Docker-ready handoff is included; production hosting/cutover and real provider
transactions/messages are separate. Approved content/tax/legal/provider inputs
remain release prerequisites, never invented production defaults.

## Acceptance and traceability

The original 50 feature IDs stay traceable in the reconciliation. 2.3 becomes
Indian-address validation without a serviceability allowlist; 2.6 becomes a staff
quoted delivery fee; 2.8 occurs after approval; 2.9 distinguishes request receipt
from paid confirmation; 3.3 is removed; 3.4 is manually updated delivery status.
Other P0 capabilities retain their meaning, with TOTP, scoped order links, audit,
idempotency, outbox and reconciliation as supporting safeguards.

Verify concurrency, expired quotes/reservations, late captures, duplicate and
reordered webhooks, refund/dispatch races, consent/notification failures, token
and admin access denial, RLS, uploads/CSV, contract generation, migrations,
browser/no-JS/axe, SEO and performance budgets, and Docker backup restoration.
Each delivery requires fresh gates, security/design/SEO/PR review and a PR.

## Working-copy preservation

Implementation occurs in the separate `feat/pakodi-mvp` worktree. The uncommitted
storefront was copied as a source snapshot; the original branch and files were
not staged, moved or modified. Its foundation must pass this task's fresh gates.
Planning: gpt-6-astra / High recommended. Implementation: gpt-6-astra / Extra High
recommended for financial/concurrency/security paths; selected settings unchanged.
