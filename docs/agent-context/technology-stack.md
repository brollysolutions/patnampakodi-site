# Approved technology stack and SEO requirement

Source: project owner's conversation instruction, 2026-09-09.
Authority: authoritative for technology selection and the SEO requirement.
Status: approved direction; application and deployment are not implemented.

## Supplied instruction

> Our techstack is Nextjs, python fastapi for backend, postgres, APscheduler, redis, Docker. save it to memory. Site should be SEO friendly, and will this for sftp credentials deployment?

## Recorded decision (derived summary)

| Component | Selected technology | Intended responsibility |
| --- | --- | --- |
| Website | Next.js | Public pages and frontend |
| Backend | Python with FastAPI | API and business logic |
| Database | PostgreSQL | Persistent application data |
| Scheduling | APScheduler | Scheduled Python jobs; execution model to be designed |
| Redis | Redis | Approved component; exact use to be scoped |
| Containers | Docker | Package and run application services |

The site must be SEO friendly. Apply the existing
[web SEO playbook](web-seo-playbook.md): public content available in initial HTML
through prerendering or server rendering, route metadata and canonicals,
crawlable links, sitemap/robots, truthful structured data, accessible responsive
pages, and measured production-build performance. These are acceptance
requirements, not evidence that a website currently passes them.

Versions, application package managers, page scope, business content, domain,
hosting provider, and deployment access remain undecided. Choosing this stack
does not authorize installing dependencies or deploying services in this task.

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
The scripts, skills and workflow tests remain the only implemented layers;
there are no web/API routes, database models, migrations, jobs, generated
contracts or deployment configuration to reconcile yet.
