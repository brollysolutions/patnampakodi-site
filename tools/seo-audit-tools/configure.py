#!/usr/bin/env python3
"""Prepare a new local plugin using reviewed installed packages; install nothing."""

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
VERSIONS = {"lighthouse": "13.4.1", "chrome-devtools-mcp": "1.9.0"}
ENTRIES = {
    "lighthouse": "cli/index.js",
    "chrome-devtools-mcp": "build/src/bin/chrome-devtools-mcp.js",
}


def build_plugin(node, chrome, packages, output):
    node, chrome, packages, output = (Path(p).expanduser().resolve()
                                      for p in (node, chrome, packages, output))
    if output.name != "seo-audit-tools":
        raise ValueError("The new output directory must be named seo-audit-tools")
    if output.exists():
        raise ValueError("Output already exists; existing plugins are never overwritten")
    for name, path in (("Node", node), ("Chrome", chrome)):
        if not path.is_file():
            raise ValueError(f"{name} executable is unavailable: {path}")
    entries = {}
    for package, version in VERSIONS.items():
        directory = packages / "node_modules" / package
        metadata = json.loads((directory / "package.json").read_text(encoding="utf-8"))
        if metadata.get("version") != version:
            raise ValueError(f"Expected installed {package} {version}")
        entry = directory / ENTRIES[package]
        if not entry.is_file():
            raise ValueError(f"Installed package entrypoint is missing: {entry}")
        entries[package] = str(entry)

    # All preconditions above are read-only. Never replace or recursively remove output.
    output.mkdir(parents=True, exist_ok=False)
    (output / ".codex-plugin").mkdir()
    shutil.copyfile(ROOT / "plugin.json", output / ".codex-plugin/plugin.json")
    shutil.copytree(REPO / ".agents/skills/lighthouse-audit", output / "skills/lighthouse-audit",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    (output / "scripts").mkdir()
    for name in ("run_lighthouse.py", "close_chrome.mjs", "smoke_test.py"):
        shutil.copyfile(ROOT / "scripts" / name, output / "scripts" / name)
    config = {"node": str(node), "chrome": str(chrome),
              "lighthouse_cli": entries["lighthouse"], "versions": VERSIONS,
              "package_reviewed_at": "2026-09-09"}
    mcp = {"mcpServers": {"chrome-devtools-seo": {
        "command": str(node),
        "args": [entries["chrome-devtools-mcp"], "--headless", "--isolated",
                 "--no-usage-statistics", "--no-performance-crux", "--redact-network-headers",
                 f"--executable-path={chrome}"],
        "env": {"CHROME_DEVTOOLS_MCP_NO_USAGE_STATISTICS": "1",
                "CHROME_DEVTOOLS_MCP_NO_UPDATE_CHECKS": "1"},
    }}}
    for name, value in (("toolchain.json", config), (".mcp.json", mcp)):
        (output / name).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--node", default=shutil.which("node"), help="Node 22.19+ executable")
    parser.add_argument("--chrome", required=True, help="Reviewed Chrome/Chromium executable")
    parser.add_argument("--packages", default=str(ROOT), help="Directory containing installed node_modules")
    parser.add_argument("--output-dir", default=str(Path.home() / "plugins/seo-audit-tools"),
                        help="New local directory named seo-audit-tools; existing directories refused")
    args = parser.parse_args()
    if not args.node:
        parser.error("Node is not on PATH; provide --node")
    try:
        output = build_plugin(args.node, args.chrome, args.packages, args.output_dir)
    except (OSError, ValueError) as exc:
        print(f"Cannot configure plugin: {exc}", file=sys.stderr)
        return 2
    print(f"Prepared local plugin: {output}\nRun its smoke_test.py before enabling it in a client.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
