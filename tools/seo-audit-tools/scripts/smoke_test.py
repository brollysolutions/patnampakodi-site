#!/usr/bin/env python3
"""Verify local MCP/browser and Lighthouse against a synthetic loopback page."""

import argparse
import json
import os
import queue
import re
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PAGE = b'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="A synthetic local audit fixture for tool verification.">
<title>SEO toolkit verification</title><style>body{font:20px system-ui;margin:2rem;color:#111;background:#fff}
a{color:#003c80}main{max-width:60ch}</style></head><body><main>
<h1>SEO toolkit verification</h1><p>This synthetic page tests the local audit tools.</p>
<a href="#details">Read verification details</a><h2 id="details">Verification details</h2>
<p>No customer data or external resources are used.</p></main></body></html>'''


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/robots.txt":
            content, kind = b"User-agent: *\nAllow: /\n", "text/plain"
        elif self.path == "/":
            content, kind = PAGE, "text/html; charset=utf-8"
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, *args):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, help="New directory for synthetic evidence")
    args = parser.parse_args()
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=False)
    root = Path(__file__).resolve().parents[1]
    cfg = json.loads((root / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]["chrome-devtools-seo"]
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}/"
    print(f"Synthetic fixture: {url}", flush=True)
    proc = None
    result = {"fixture_url": url, "scope": "Synthetic local setup verification only", "checks": []}
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    try:
        with (output / "mcp-stderr.log").open("w", encoding="utf-8") as log:
            proc = subprocess.Popen([cfg["command"], *cfg["args"]], stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE, stderr=log, text=True, encoding="utf-8",
                                    env={**os.environ, **cfg.get("env", {})}, creationflags=flags)
            incoming = queue.Queue()

            def read():
                for line in proc.stdout:
                    incoming.put(line)
                incoming.put(None)

            threading.Thread(target=read, daemon=True).start()
            counter = 0

            def request(method, params):
                nonlocal counter
                counter += 1
                proc.stdin.write(json.dumps({"jsonrpc": "2.0", "id": counter, "method": method, "params": params}) + "\n")
                proc.stdin.flush()
                while True:
                    line = incoming.get(timeout=120)
                    if line is None:
                        raise RuntimeError("MCP ended before a response; inspect mcp-stderr.log")
                    message = json.loads(line)
                    if message.get("id") != counter:
                        continue
                    if "error" in message or message.get("result", {}).get("isError"):
                        raise RuntimeError(json.dumps(message))
                    return message["result"]

            initialized = request("initialize", {"protocolVersion": "2024-11-05", "capabilities": {},
                                                   "clientInfo": {"name": "seo-local-smoke", "version": "1.0.0"}})
            result["server_info"] = initialized.get("serverInfo")
            proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
            proc.stdin.flush()
            tools = request("tools/list", {})["tools"]
            schemas = {tool["name"]: tool.get("inputSchema", {}) for tool in tools}
            (output / "mcp-tools.json").write_text(json.dumps(tools, indent=2), encoding="utf-8")
            for required in ("new_page", "take_snapshot", "lighthouse_audit", "performance_start_trace"):
                if required not in schemas:
                    raise RuntimeError(f"Required MCP tool missing: {required}")
            result["checks"].append({"check": "MCP initialize/tools/list", "status": "passed", "tool_count": len(tools)})
            opened = request("tools/call", {"name": "new_page", "arguments": {"url": url}})
            (output / "mcp-navigation.json").write_text(json.dumps(opened, indent=2), encoding="utf-8")
            page_text = "\n".join(part.get("text", "") for part in opened.get("content", []))
            matches = [match.group(1) for line in page_text.splitlines()
                       if url in line and (match := re.match(r"^(\d+):\s+", line))]
            if not matches:
                raise RuntimeError("Could not identify synthetic page ID from navigation response")
            page_id = int(matches[-1])
            snapshot = request("tools/call", {"name": "take_snapshot", "arguments": {"pageId": page_id}})
            (output / "mcp-snapshot.json").write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
            if "SEO toolkit verification" not in json.dumps(snapshot):
                raise RuntimeError("Synthetic heading absent from browser accessibility snapshot")
            result["checks"].append({"check": "MCP browser navigation and accessibility snapshot", "status": "passed"})
            print("MCP browser and snapshot: passed", flush=True)
            trace = request("tools/call", {"name": "performance_start_trace", "arguments": {
                "pageId": page_id, "reload": True, "autoStop": True}})
            (output / "mcp-trace.json").write_text(json.dumps(trace, indent=2), encoding="utf-8")
            result["checks"].append({"check": "MCP performance trace", "status": "passed"})
            print("MCP performance trace: passed", flush=True)
            audited = request("tools/call", {"name": "lighthouse_audit", "arguments": {"pageId": page_id, "device": "desktop"}})
            (output / "mcp-lighthouse.json").write_text(json.dumps(audited, indent=2), encoding="utf-8")
            result["checks"].append({"check": "MCP Lighthouse tool invocation", "status": "passed"})
            print("MCP Lighthouse invocation: passed", flush=True)
            # Close only the server process tree created by this test.
            if os.name == "nt":
                subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                               stdout=log, stderr=subprocess.STDOUT, creationflags=flags, timeout=30)
            else:
                proc.terminate()
            proc.wait(timeout=30)
            result["mcp_terminal_exit_code"] = proc.returncode
            result["mcp_shutdown"] = "Test-owned server stopped after checks"
            proc = None
        completed = subprocess.run([sys.executable, str(root / "scripts/run_lighthouse.py"), url,
                                    "--device", "both", "--runs", "1", "--output-dir", str(output / "lighthouse")],
                                   creationflags=flags, timeout=600)
        result["checks"].append({"check": "Lighthouse CLI mobile/desktop", "status": "passed" if completed.returncode == 0 else "failed",
                                 "exit_code": completed.returncode})
        result["status"] = "passed" if completed.returncode == 0 else "failed"
        return completed.returncode
    except (OSError, ValueError, RuntimeError, queue.Empty, subprocess.SubprocessError) as exc:
        result.update(status="failed", error=str(exc) or type(exc).__name__)
        print(f"Smoke failed: {result['error']}", file=sys.stderr, flush=True)
        return 1
    finally:
        if proc is not None and proc.poll() is None:
            if os.name == "nt":
                subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL, creationflags=flags, timeout=30)
            else:
                proc.kill()
            proc.wait(timeout=30)
        server.shutdown()
        server.server_close()
        (output / "smoke-result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"Evidence: {output}", flush=True)


if __name__ == "__main__":
    sys.exit(main())
