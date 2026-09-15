# Agent context index

- [Client presentation](../client-presentation.md): repeatable disposable checkout
  demo, ten-minute customer/operator walkthrough and live activation inputs.

## Workflow setup request — 2026-09-07

Authority: user instruction. Install the supplied agent-workflow-kit for this
repository, share it on GitHub, and provide a partner setup/explanation document.
Affected: workflow scripts, agent configuration, skills, CI, and documentation.
No application stack, production domain, deployment target, or business content
was specified.

## Shared workflow

`../../AGENTS.md` is the repository contract; `../../SECURITY.md` records
current security scope. `../partner-workflow-guide.md` explains installation and
daily collaboration. `implementation-plan.md` and `feature-status.md` are
operational evidence, updated with relevant changes.

## Public website guidance

`web-seo-playbook.md` is adapted from the supplied workflow kit dated 2026-09-07.
It records intended quality rules for future public pages; framework-specific
commands and budgets need implementation with the chosen stack. It is not
evidence of a working website or an approved production domain.

## Provenance

The 2026-09-09 rows below describe the sources at ingestion. Their pending choices
and then-unimplemented architecture are historical; the approved MVP decisions,
current feature status and verification record describe this delivery.

| Reference | Source / as of | Authority | Affected paths | Known differences |
| --- | --- | --- | --- | --- |
| [Kukatpally website expansion](kukatpally-site-expansion.md) | Owner correction, live six-page retrieval and supplied brochure, 2026-09-15 | Current serving branch and requested public design | Public content, outlet discovery, FAQ, logo, SEO | Kukatpally only; older live branch/menu/price claims superseded; branch contact and founder details asked |
| [Four-flavour menu and brochure](four-flavour-menu.md) | User-approved plan and supplied ten-page PDF, 2026-09-15 | Current public scope; supersedes shopping-led design | Public web, ordering gate, editorial seed, brochure and artwork | Four named pakodis without prices; five informational nav links; new ordering paused; existing order obligations preserved |
| [Classic ecommerce redesign](commerce-redesign-plan.md) | User planning answers and implementation instruction, 2026-09-11 | Approved current design and new-purchase behaviour | Full web/admin, commerce, additive schema/contracts | Two modes, immediate checkout, PIN fees, one fresh pilot; original identity and conditional reference-based image generation; live inputs remain separate |
| [Original identity correction](website-design-decisions.md) | Explicit user correction and homepage/shop browser inspection, 2026-09-11 | Preserve original fonts and colors; supersedes replacement brand direction | Shared web layout, fonts, palette, shopping navigation and sharing image | Poppins editorial/body and Inter commerce headings; accessible accent/text pairings; live sales still require approved catalog/provider inputs |
| [Local Docker staging](../local-staging.md) | User-approved local fixture environment, 2026-09-11 | Local operator and isolated acceptance procedure; live deployment remains separate | Docker, provider adapters, private checkout, acceptance tests | Persistent staging requires approved products, seller, policies, brochure and operator-created named admin |
| [MVP verification](mvp-verification.md) | Fresh local tests and self-review, 2026-09-10 | Point-in-time evidence; final gate and remote delivery readback recorded separately | Application, contracts, containers, public/private UI | Live providers, approved business inputs and production host acceptance remain separate |
| [Approved MVP decisions](approved-mvp-plan.md) | User planning answers and "Implement the plan", 2026-09-10; password-only admin correction, 2026-09-11 | Current authority over conflicting source proposals | Storefront, commerce, admin, jobs, Docker | Staff quotes, own delivery, WhatsApp only, password-only named admins, P0 first; production hosting separate |
| [Commerce operations](../commerce-operations.md) | Implemented service and deployment contract, 2026-09-10 | Operational guidance; live acceptance evidence is separate | API/web/worker/database/providers/deployment | Approved content, credentials, tax/privacy sign-off and production cutover still required |
| [Patnam Pakodi design brief v0.2](patnam-pakodi-design-brief-v0.2.md) | User-supplied `Patnam-Pakodi-Design-Brief (2).md`, dated 2026-09-04; copied unchanged on 2026-09-09 | Authoritative for explicitly locked identity; Proposed/Open sections remain pending | Future public pages, theme, fonts, controls | Cream/support palette, logo and imagery are not approved; source archive hash in reconciliation |
| [FRAB Foods MVP features v4.1](frab-foods-mvp-features-v4.1.md) | User-supplied file, dated/received 2026-09-09; copied unchanged | Authoritative requested feature inventory; conflicts require explicit resolution | Future storefront, checkout, orders, franchise, admin and SEO | 50 features, not implemented; blanket indexability conflicts with private customer/admin pages |
| [Razorpay and WhatsApp implementation source v1.0](frab-foods-razorpay-whatsapp-plan-v1.0.md) | User-supplied file, dated/received 2026-09-09; copied unchanged | Advisory implementation plan; external claims not independently established by copying | Payments, stock, outbox, messaging, tracking, admin | Assumes Celery/Valkey instead of approved APScheduler/Redis; stale feature numbering, email/TOTP assumptions, provider/pricing/legal claims need review |
| [Commerce reconciliation and phased acceptance](pakodi-commerce-reconciliation.md) | Derived from supplied briefs, repository inspection and limited official documentation checks, 2026-09-09 | Proposal; preserves explicit stack and source authority; unresolved choices remain open | Implementation plan, all future application layers | Scope/indexability clarification pending; tracks all 50 features and source hashes; no application delivery claimed |
| [Website visual proposal](website-design-decisions.md) | Derived from supplied design brief and pinned design guidance, 2026-09-09 | Locked source identity plus proposed direction; approval pending | Future public UI and design review | Recommends cream food-led layout; missing approved assets; no browser or Apple verification yet |
| [Live-site migration baseline](pakodi-live-site-baseline.md) | Read-only homepage retrieval from user-supplied domain, 2026-09-09 | Observational evidence, not authority for business facts | Future URL inventory, migration and launch checks | Homepage HTTP 200 with noindex/nofollow; seven linked page paths; full crawl/browser evidence outstanding |
| [Approved technology stack and SEO requirement](technology-stack.md) | User conversation, 2026-09-09; verbatim instruction and derived summary | Authoritative for selected stack and SEO requirement; deployment assessment advisory | AGENTS.md, future website/API/database/jobs/deployment, implementation plan, partner guide | Supersedes stack-unselected guidance; no application exists yet. SFTP hosting/access remains unconfirmed. |
| [Astra workflow adaptation](astra-workflow-reference.md) | User-supplied BrollyAI workflow, 2026-09-07; derived summary | Advisory; current AGENTS.md and explicit user instructions prevail | AGENTS.md, delivery engine/tests, mirrored skills, partner guide | BrollyAI's private scaffolding, existing application, and model config are not this checkout's architecture or settings. |

The provided kit describes its source as BrollyAI commit `eaffc65`, captured
2026-09-07. Its workflow engine, tests, skills, and SEO checker are adapted here.
No source project's application, deployment credentials, personal instructions,
account state, or reference documents are included.

## Workflow audit and design skills — 2026-09-08

Authority: user requested an audit with fixes, installation of Taste and Apple
Design, and research into other established design skills. `workflow-audit.md`
records confirmed gaps and verification; `design-skills.md` records the comparison,
exact upstream revisions, licenses, installation scope, and routing decisions.

## Advanced SEO and Lighthouse toolkit — 2026-09-09

Authority: user requested detailed SEO/AEO/GEO/LLMO, competitor/keyword research,
content writing/audits, UI/UX and free browser tooling, then requested a PR.
`../seo-toolkit-guide.md` describes the shared skills, pinned open-source packages,
local plugin preparation, evidence rules and account/runtime limits. Personal
client configuration and reports are not redistributed. This does not choose the
website stack or establish a production audit.

The same task includes the user's follow-up to use Taste, Impeccable and Emil
Kowalski's animation guidance whenever UI/UX design is requested, then verify with
Apple Design. `design-skills.md` records the active sequence, pinned official
sources, licenses, installed scope and differences from upstream execution flows.
