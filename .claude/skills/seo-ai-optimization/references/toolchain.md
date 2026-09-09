# Free local audit tools

Reviewed package sources and procedures as of 2026-09-09. Follow the repository's
`docs/seo-toolkit-guide.md` to prepare a local plugin. Source files in a clone do
not establish installation or runtime success. Use configured paths and collect
current evidence for the requested site.

## Components

| Component | Version/source | Purpose |
| --- | --- | --- |
| Shared skill | `seo-ai-optimization` in both repository skill trees | Research, content audits, writing, technical and SEO/UI/UX review |
| Optional local plugin | Prepared by `tools/seo-audit-tools/configure.py` | Packages the local browser MCP and Lighthouse operating skill |
| Lighthouse | `13.4.1`, official GoogleChrome project, Apache-2.0 | Mobile/desktop performance, accessibility, best-practices and SEO lab reports |
| Chrome DevTools MCP | `1.9.0`, official ChromeDevTools project, Apache-2.0 | Browser snapshots, screenshots, network/console inspection, Lighthouse and traces |
| Existing Playwright MCP | Existing pinned configuration preserved | Use when available and appropriate for browser journeys; do not bypass its permissions |
| Web search | Existing session capability | Current competitor and intent research; no paid SERP API required |
| HTML inventory | Bundled Python standard-library helper | Source-only metadata/headings/link/media/schema inventory |

Exact package inputs and plugin source live in `tools/seo-audit-tools/`.
The configuration command requires installed packages and a reviewed browser;
it writes a new local plugin with absolute paths. It never installs packages,
registers a marketplace, modifies client settings or replaces an existing plugin.

No SEO subscription, hosted crawl provider, paid AI writer, trial or credit
purchase is needed. Search Console/Trends/Keyword Planner or other account data
remain optional and subject to actual access and free entitlement. Open-source
browser tools do not supply a proprietary keyword-volume or backlink database.

## Run Lighthouse

Use the plugin's `lighthouse-audit` skill when loaded. From a shell with the
installed Python runner, replace the example URL with the authorized target:

```text
python <prepared-plugin>/scripts/run_lighthouse.py <authorized-url> --device both --runs 3
```

Reports go to a new directory under `~/seo-audits/`. Each run retains
HTML, JSON and a log; `summary.json` records environment, category scores, lab
metrics and execution status. Use `--runs 1` for a quick smoke check and repeated
runs for a baseline. An explicit `--output-dir` must be new to preserve evidence.

Inspect final URL, errors/warnings and intended page before interpreting results.
Exit 0 means report generation completed; compare the actual metrics and failed
audits with the project's requirements separately. Field CWV, rankings and full
accessibility conformance remain separate checks. Do not upload reports to a
public viewer or temporary hosting as part of the default workflow.

## Use the MCP

After installation, a new Codex thread picks up the plugin's skills and tools.
Discover the actual schemas there; do not invent callable tools in an existing
thread. For installation verification a local stdio client can establish the
handshake and invoke tools, but that is separate from active-thread availability.

The configured server uses isolated headless Chrome, with usage telemetry,
automatic update checks and automatic CrUX URL lookup disabled. Network-header
redaction is enabled. It does not attach to the signed-in browser or grant
unrestricted filesystem access. User-agent page requests still reach the audited
website and its resources; the audit is not network-free for live URLs.

The MCP Lighthouse operation currently excludes performance; use the local CLI
for full repeatable category reports and browser traces to investigate causes.
Do not confuse an accessibility snapshot with an accessibility conformance test.

## Maintenance and evidence

Use exact npm versions, the resolved lockfile and disabled package lifecycle
scripts when installing. Review future updates before installing them; run
dependency checks and repeat the synthetic smoke test. The lockfile records
transitive versions; a pin on the top-level package alone is insufficient for
reproducibility. Local package vulnerability scans are point-in-time evidence,
not a proof that all code is safe.

To retest setup using only a synthetic loopback page:

```text
python <prepared-plugin>/scripts/smoke_test.py --output-dir <new-local-directory>
```

The test creates and closes its own local HTTP server and headless browser,
checks MCP navigation/snapshot/Lighthouse, then runs CLI mobile/desktop audits.
Its reports validate the toolchain, not the production website. For new machines,
install reviewed compatible prerequisites and generate `toolchain.json` and
the MCP executable paths locally. The source does not bundle Node or Chrome.

The Windows runner owns its isolated Chrome profile, uses a loopback debugging
port, and waits for graceful browser shutdown before bounded profile cleanup.
Only validated task-owned temporary directories are removed. Browser launch
controls are recorded in each summary; failures remain nonzero even if some
reports were saved.
