# Advanced SEO and browser audit toolkit

The shared `seo-ai-optimization` skill covers SEO, AEO, GEO and LLMO, competitor
analysis, keyword research, existing-content audits, natural writing and SEO/UI/UX.
The companion `lighthouse-audit` skill provides measured browser checks. Both
skills are mirrored for Codex and Claude Code.

This guide describes the reusable toolkit prepared on 2026-09-09. Pulling the
repository does not install packages, enable a plugin or audit a production site.

## Capabilities and outputs

| Mode | Evidence and output |
| --- | --- |
| Competitors | Actual search competitors and page comparisons; content, proof, navigation, UX and link opportunities |
| Keywords | Audience tasks, observed intent, demand provenance, clusters, keyword-to-URL ownership and priorities |
| Existing content | Section-level findings, decay diagnosis, claim checks and keep/refresh/consolidate/split/retire proposals |
| Natural writing | Fact-led brief, useful original copy, metadata, internal links and separate missing-evidence requests |
| SEO and UI/UX | Search-promise consistency, mobile/desktop journeys, hierarchy, navigation, forms, accessibility and performance |
| Technical SEO | Source/render/HTTP/account evidence; indexing, canonicals, redirects, sitemaps and structured data |
| AEO | Direct, complete, independently understandable answers and an answer-gap matrix |
| GEO | Original evidence, citation passages, source attribution and observed answer-source comparisons |
| LLMO | Entity identity, relationships, offer scope, qualifications, retrieval controls and factual-fidelity benchmarks |
| Special cases | Local businesses, catalogs, multilingual sites and migrations where applicable |
| Reporting | Evidence ledger, confidence, impact, prioritized fixes, acceptance checks and measurement plan |

Start with [the main skill](../.agents/skills/seo-ai-optimization/SKILL.md), which
links the detailed procedures. Reuse the
[audit report](../.agents/skills/seo-ai-optimization/assets/audit-report.md) and
[content brief](../.agents/skills/seo-ai-optimization/assets/content-brief.md).
The [AI discovery procedure](../.agents/skills/seo-ai-optimization/references/ai-discovery-audit.md)
separates answer quality, citation evidence, entity clarity, search retrieval,
training crawlers and user-requested fetching.

Metrics require actual evidence. Free authorized Search Console/Trends exports
are optional; unknown volumes, difficulty, backlinks and conversions stay unknown.
Ordinary web results do not prove AI-answer visibility. AI benchmarks record the
product, prompt, date, citations, successful-response denominator and failures.

## Invocation examples

```text
Use $seo-ai-optimization to audit [URL] in detail.
Audience: ...; market/language: ...; primary conversion: ...
Cover competitors, keywords, existing content, technical SEO, UI/UX,
Lighthouse, AEO, GEO and LLMO. Use only free tools. Audit only.
Return cited findings, keyword-to-URL mapping and prioritized fixes.
```

```text
Use $seo-ai-optimization to audit this existing page section by section.
Check intent, factual support, originality, clarity, missing questions,
internal links and conversion usefulness. Preserve the source.
```

```text
Use $seo-ai-optimization to research and write this page using confirmed
facts and brand voice. Remove generic AI language. Deliver the brief,
metadata, complete copy, internal links and separate evidence requests.
```

URLs, HTML, Markdown and supplied copy are supported. Screenshots alone cannot
prove DOM semantics, measured contrast or performance. Audit requests stay
read-only; implementation follows the repository's review and PR workflow.

## Optional tool installation

| Package | Pin | Source and license |
| --- | --- | --- |
| Lighthouse | 13.4.1 | [GoogleChrome](https://github.com/GoogleChrome/lighthouse), Apache-2.0 |
| Chrome DevTools MCP | 1.9.0 | [ChromeDevTools](https://github.com/ChromeDevTools/chrome-devtools-mcp), Apache-2.0 |

Requirements: Node **22.19+**, Python **3.11+**, and an installed, reviewed
Chrome/Chromium executable. Browser binaries are not bundled. Existing browser
integrations are preserved. Lighthouse includes automated axe checks, so a
second overlapping accessibility CLI is not required.

With tooling installation authorized, run from the repository root:

```text
npm ci --prefix tools/seo-audit-tools --ignore-scripts --no-fund --no-audit
npm audit --prefix tools/seo-audit-tools --omit=dev
```

The first command installs the resolved lockfile with lifecycle scripts disabled.
The second checks known vulnerabilities. Review findings before enabling tools.
These commands are not run by ordinary repository setup or CI.

Prepare a new local plugin using the actual browser executable path:

```text
uv run --no-project --python ">=3.11" python tools/seo-audit-tools/configure.py --chrome "ABSOLUTE-PATH-TO-CHROME"
```

`--node` selects Node when it is not on PATH. `--packages` can reuse a reviewed
installation containing the pinned `node_modules` packages. Output defaults to
`~/plugins/seo-audit-tools`. `--output-dir` selects another new directory whose
final name is `seo-audit-tools`. Existing directories are always refused.

The command validates files/package versions and copies the reviewed scripts,
skill and manifest, then generates local `toolchain.json` and `.mcp.json` paths.
It does not download, register a marketplace, edit global settings or enable tools.
If copying fails, partial new output remains available for inspection. For updates,
prepare a separate copy and use the client's reviewed plugin-update workflow.

Run the generated plugin's synthetic check before enabling it:

```text
python <prepared-plugin>/scripts/smoke_test.py --output-dir <new-private-evidence-directory>
```

Keep generated plugins and evidence under ignored `.agent-workflow/` or outside
the repository. Never commit runtime configuration or reports. For Codex, ask its
`plugin-creator` workflow to register and enable the prepared plugin in the
personal marketplace; use its validated source-path and installation procedure.
Existing explicit setup authorization persists. Start a new thread afterward.
Other MCP clients can use the generated server entry through their documented
configuration workflow; enclosing configuration formats may differ.

## Lighthouse usage and interpretation

```text
python <prepared-plugin>/scripts/run_lighthouse.py <authorized-url> --device both --runs 3
```

- `--device`: mobile, desktop or both (default).
- `--runs`: one for a smoke check; default three per device; maximum five.
- `--timeout`: each Lighthouse process limit; startup/cleanup have separate bounded waits.
- `--output-dir`: new directory only; default unique folder under `~/seo-audits/`.

Every run retains HTML, JSON and a log. The summary records versions, browser
controls, settings, scores, metrics, warnings, errors and device-specific medians.
Exit 0 means report generation completed, not that budgets passed. Exit 1 means
failed/incomplete execution; exit 2 means invalid input/configuration. Retain
session IDs and collect terminal results.

The MCP Lighthouse tool excludes performance scoring. Use the CLI for full
reports and browser traces for diagnosis. Compare matched environments and
variation; lab TBT is not field INP. Field Core Web Vitals, rankings, conversions
and accessibility conformance require separate evidence.

## Security, maintenance and verification limits

The generated MCP uses isolated headless Chrome and disables usage statistics,
automatic update checks and automatic CrUX requests. Network-header redaction
is enabled; Lighthouse error reporting is disabled. It never attaches to the
signed-in browser profile. Live audits request the target and its assets; reports
can contain page content and screenshots and remain private by default.

The runner owns its temporary profile, connects through loopback, requests
graceful browser shutdown and waits before bounded cleanup. Cleanup validates
its temporary directory and targets only its own processes. Browser sandboxing,
web security and certificate validation stay enabled.

The initial personal setup passed synthetic browser and mobile/desktop checks on
Windows with Node 22.23.1 and Chrome 152.0.7977.82 after fixing Windows startup
and cleanup races. Current shared-package checks are in
[feature status](agent-context/feature-status.md). Personal reports and absolute
paths are not redistributed. Windows success does not establish macOS/Linux
browser support; standard CI tests remain hermetic and do not install npm tools.

Review releases, licenses, engines and resolved dependencies before updating pins;
rerun the synthetic smoke check. A clean vulnerability audit is point-in-time
evidence, not a complete third-party code review. No production URL or accounts
were supplied; live SEO, field performance and external AI visibility remain
unverified. No application or deployment stack is introduced by this toolkit.
