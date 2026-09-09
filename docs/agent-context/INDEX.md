# Agent context index

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

| Reference | Source / as of | Authority | Affected paths | Known differences |
| --- | --- | --- | --- | --- |
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
