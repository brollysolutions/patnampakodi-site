# Patnam Pakodi

Patnam Pakodi's cream storefront and commerce MVP, built with Next.js, FastAPI,
PostgreSQL, APScheduler and Redis. Customers request delivery, staff confirm a
quote, and payment follows through Razorpay. Named admins manage products, stock,
content and orders; customer updates use opt-in WhatsApp.

See [commerce operations and Docker handoff](docs/commerce-operations.md).
Hosting, approved business content and live provider acceptance remain release
prerequisites; no production deployment is implied.

See [local storefront setup](docs/storefront-development.md) to run the app.

Start with the [partner workflow guide](docs/partner-workflow-guide.md) for
installation, day-to-day collaboration, and troubleshooting.

- [Shared engineering rules](AGENTS.md)
- [Implementation plan](docs/agent-context/implementation-plan.md)
- [Feature status and verification](docs/agent-context/feature-status.md)
- [Security guidance](SECURITY.md)
- [Workflow audit](docs/agent-context/workflow-audit.md)
- [Design skills and research](docs/agent-context/design-skills.md)
- [Advanced SEO, AEO, GEO, LLMO and Lighthouse toolkit](docs/seo-toolkit-guide.md)

Requested UI/UX work uses Taste for direction, Impeccable for structure and
refinement, Kowalski for motion, and the installed Apple Design skill for review.
The design guide records the pinned sources and evidence requirements.

From a clone containing these files, run one setup command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/setup-agent-workflow.ps1
```

Or on macOS/Linux/Git Bash:

```bash
bash scripts/setup-agent-workflow.sh
```

Requires Git, Bash (Git Bash on Windows), uv, and Python 3.11+. GitHub CLI
authentication and repository access are needed to publish PRs. See the guide
before opening your first agent session.
