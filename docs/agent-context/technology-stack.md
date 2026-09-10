# Approved technology stack and SEO requirement

Source: project owner's conversation instruction, 2026-09-09.
Authority: authoritative for technology selection and the SEO requirement.
Status: selected components implemented for the approved MVP; see
[approved decisions](approved-mvp-plan.md) and [operations](../commerce-operations.md).
Docker handoff is included. Hosting/cutover and live provider acceptance are separate.

## Supplied instruction

> Our techstack is Nextjs, python fastapi for backend, postgres, APscheduler, redis, Docker. save it to memory. Site should be SEO friendly, and will this for sftp credentials deployment?

## Recorded decision (derived summary)

| Component | Selected technology | Intended responsibility |
| --- | --- | --- |
| Website | Next.js | Public pages and frontend |
| Backend | Python with FastAPI | API and business logic |
| Database | PostgreSQL | Persistent application data |
| Scheduling | APScheduler | One scheduler with PostgreSQL leases, reconciliation and reservation expiry |
| Redis | Redis | Atomic distributed rate limits; never authoritative stock |
| Containers | Docker | Package and run application services |

The site must be SEO friendly. Apply the existing
[web SEO playbook](web-seo-playbook.md): public content available in initial HTML
through prerendering or server rendering, route metadata and canonicals,
crawlable links, sitemap/robots, truthful structured data, accessible responsive
pages, and measured production-build performance. These are acceptance
requirements, not evidence that a website currently passes them.

Versions and package managers are now pinned: npm for the web, uv for the API,
and a digest-pinned PostgreSQL Docker fixture. Approved business content, hosting
provider and deployment access remain partly unresolved. The later 2026-09-09 request
supplies `https://patnampakodi.com/` and the MVP/design/integration briefs;
[commerce reconciliation](pakodi-commerce-reconciliation.md) now records the
requested feature inventory and approved first-delivery scope. The original
stack-memory task did not authorize dependency installation or deployment.
The new build request does not establish production access or cutover approval.

## Deployment question (unresolved)

The user asked about SFTP credentials; this does not confirm an SFTP-only host
or authorize credential storage. Confirm whether the host provides only file
transfer or also shell/container execution or managed application runtimes.

Technical assessment, checked against official documentation on 2026-09-09:

- [SFTP](https://man.openbsd.org/sftp) transfers files over SSH transport;
  SFTP access alone does not establish permission to run remote services.
- [Next.js deployment](https://nextjs.org/docs/app/getting-started/deploying)
  supports Node.js or Docker for full features. A static export can be uploaded
  to a static web host, with limitations on features requiring a server.
- [FastAPI containers](https://fastapi.tiangolo.com/deployment/docker/) require
  a running application process. The full selected stack therefore needs
  execution and service hosting beyond file upload, including database, Redis
  and scheduled-job operation. Static frontend hosting would require the
  backend services to run elsewhere.

No credentials were supplied, requested for storage, or saved. Follow
`../../SECURITY.md` when deployment is designed.

## Reconciliation with this repository

This decision supersedes current statements that the stack is unchosen in
`../../AGENTS.md`, `../partner-workflow-guide.md` and item 2 of
`implementation-plan.md`. Earlier dated setup/toolkit records remain historical.
The first storefront now adds web/API routes, public content schemas, an Alembic
migration with RLS, generated contracts and a local Docker database. No business
jobs or deployment configuration are implemented. See `../storefront-development.md`.
