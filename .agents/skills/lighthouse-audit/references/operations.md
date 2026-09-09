# Local operations

The repository's `docs/seo-toolkit-guide.md` explains local preparation. A prepared
plugin's `toolchain.json` records actual paths and reviewed versions; do not assume
those paths on another machine. Runtime packages live separately from the plugin
cache, installed from `tools/seo-audit-tools/package-lock.json` or an existing
reviewed installation of those versions.

The plugin's MCP launches the installed Chrome DevTools server using Node,
without npx or a floating version at startup. It uses isolated headless Chrome,
disables usage statistics/update checks/automatic CrUX requests and enables
network-header redaction. It does not add a remote paid SEO service.

To diagnose an unavailable executable, check the configured files and versions
before installing anything. A missing MCP in an already-running conversation can
require a new thread after plugin activation; configuration alone is not runtime
proof. Do not repeatedly install or duplicate the server to work around that.

For package maintenance, review official releases/license/engine requirements,
inspect package lifecycle scripts and resolved dependency changes, retain exact
versions/lockfile, scan the resolved dependency tree and rerun local browser and
Lighthouse smoke checks. Do not silently upgrade a working toolchain.

On Windows, automatic Chrome-launcher cleanup can encounter locked profile
files. The bundled runner owns a temporary Chrome profile and connects Lighthouse
through a loopback debugging port. It closes Chrome through its protocol, waits
for shutdown, and uses bounded cleanup retries only after validating the temporary
path. A failed audit or cleanup remains a nonzero result; saved reports alone do
not establish successful completion.

Reports may include page content, URLs and screenshots. Keep them local unless
the task authorizes sharing. Do not use temporary public storage/upload commands
to make a report accessible. A browser audit makes requests to the target and its
page assets; “local tools” does not mean a live-page audit is network-free.

Reference implementations and terms:

- [Lighthouse](https://github.com/GoogleChrome/lighthouse), Apache-2.0.
- [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp), Apache-2.0.
- [MCP configuration](https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/docs/configuration.md).
- [Browser tool reference](https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/docs/tool-reference.md).

Test existing accessibility tooling first. Lighthouse includes automated axe
checks, so a second accessibility CLI is not required merely to repeat them.
Use more targeted axe/browser checks only when interaction-state coverage needs it.
