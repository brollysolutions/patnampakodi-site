#!/usr/bin/env python3
"""Run pinned local Lighthouse on one authorized URL; retain every report and failure."""

import argparse
import json
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit


# Background/occlusion controls from the installed chrome-launcher defaults.
# Keep browser sandboxing, certificate checks and web security enabled.
CHROME_AUDIT_FLAGS = (
    "--headless=new", "--no-first-run", "--no-default-browser-check",
    "--disable-background-networking", "--disable-component-update", "--disable-sync",
    "--metrics-recording-only", "--disable-extensions",
    "--disable-component-extensions-with-background-pages", "--disable-default-apps",
    "--disable-backgrounding-occluded-windows", "--disable-renderer-backgrounding",
    "--disable-background-timer-throttling", "--mute-audio",
    "--disable-features=Translate,OptimizationHints,MediaRouter,DialMediaRouteProvider,"
    "CalculateNativeWinOcclusion,InterestFeedContentSuggestions,AutofillServerCommunication,"
    "PrivacySandboxSettings4,RenderDocument",
)


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def stop_owned_process(proc, log):
    if proc.poll() is None:
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                           stdout=log, stderr=subprocess.STDOUT, timeout=30,
                           creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            proc.terminate()
    try:
        proc.wait(timeout=30)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=10)


def clean_owned_profile(profile):
    # Never recursively remove an arbitrary configured or user profile path.
    temp_root = Path(tempfile.gettempdir()).resolve()
    resolved = profile.resolve()
    if resolved.parent != temp_root or not resolved.name.startswith("seo-lighthouse-"):
        raise ValueError("Refusing cleanup outside the task-owned temporary profile")
    for attempt in range(120):
        try:
            shutil.rmtree(resolved)
            return
        except FileNotFoundError:
            return
        except OSError:
            if attempt == 119:
                raise
            time.sleep(0.25)


def run_with_owned_chrome(command, config, env, log, timeout):
    """Own Chrome separately so Lighthouse attaches and does not race profile cleanup."""
    profile = Path(tempfile.mkdtemp(prefix="seo-lighthouse-"))
    chrome = None
    proc = None
    port = None
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    try:
        chrome = subprocess.Popen([
            config["chrome"], *CHROME_AUDIT_FLAGS, "--remote-debugging-address=127.0.0.1",
            "--remote-debugging-port=0", f"--user-data-dir={profile}",
            "about:blank"], stdout=log, stderr=subprocess.STDOUT, creationflags=flags)
        deadline = time.monotonic() + 60
        while True:
            port_file = profile / "DevToolsActivePort"
            try:
                content = port_file.read_text(encoding="utf-8").splitlines()
            except (FileNotFoundError, PermissionError):
                # Chrome can briefly hold this file open while publishing its port.
                content = []
            if content and content[0].isdigit() and 1 <= int(content[0]) <= 65535:
                port = int(content[0])
                break
            if chrome.poll() is not None:
                raise ValueError("Isolated Chrome exited before opening its debug port")
            if time.monotonic() >= deadline:
                raise ValueError("Isolated Chrome did not become ready within 60 seconds")
            time.sleep(0.1)
        proc = subprocess.Popen([*command, f"--port={port}", "--hostname=127.0.0.1"],
                                stdout=log, stderr=subprocess.STDOUT, env=env, creationflags=flags)
        return proc.wait(timeout=timeout)
    finally:
        # Wait for only the processes this run started before deleting its profile.
        try:
            if proc is not None:
                stop_owned_process(proc, log)
        finally:
            try:
                if chrome is not None:
                    if port is not None and chrome.poll() is None:
                        try:
                            subprocess.run([config["node"], str(Path(__file__).with_name("close_chrome.mjs")), str(port)],
                                           stdout=log, stderr=subprocess.STDOUT, timeout=25,
                                           creationflags=flags, check=True)
                            chrome.wait(timeout=15)
                        except subprocess.SubprocessError as exc:
                            log.write(f"Graceful close unavailable; stopping the audit-owned process: {exc}\n")
                    stop_owned_process(chrome, log)
            finally:
                clean_owned_profile(profile)


def audit(args):
    parsed = urlsplit(args.url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Use an HTTP(S) URL without embedded credentials.")
    if not 1 <= args.runs <= 5:
        raise ValueError("Runs must be between 1 and 5 per device.")
    root = Path(__file__).resolve().parents[1]
    config = json.loads((root / "toolchain.json").read_text(encoding="utf-8"))
    for key in ("node", "lighthouse_cli", "chrome"):
        if not Path(config[key]).is_file():
            raise ValueError(f"Configured {key} executable/file is unavailable.")
    output = Path(args.output_dir).resolve()
    # Require a new directory so previous evidence cannot be silently overwritten.
    output.mkdir(parents=True, exist_ok=False)
    manifest = {
        "started_at": timestamp(), "requested_url": args.url,
        "tool_versions": config["versions"], "runs_per_device": args.runs,
        "environment": {"platform": sys.platform, "chrome": config["chrome"],
                        "browser_launch_flags": list(CHROME_AUDIT_FLAGS)},
        "scope": "Lab navigation audit only; no field CWV or ranking verdict.",
        "runs": [], "status": "running",
    }
    manifest_path = output / "summary.json"

    def save():
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    save()
    profiles = ("mobile", "desktop") if args.device == "both" else (args.device,)
    failed = False
    for device in profiles:
        for index in range(1, args.runs + 1):
            stem = output / f"{device}-{index}"
            command = [config["node"], config["lighthouse_cli"], args.url,
                       "--output=html", "--output=json", f"--output-path={stem}",
                       "--chrome-flags=--headless=new", "--no-enable-error-reporting",
                       "--only-categories=performance,accessibility,best-practices,seo", "--quiet"]
            if device == "desktop":
                command.append("--preset=desktop")
            env = {**os.environ, "CHROME_PATH": config["chrome"], "CI": "1"}
            entry = {"device": device, "run": index, "started_at": timestamp(), "status": "running"}
            manifest["runs"].append(entry)
            save()
            print(f"Running {device} audit {index}/{args.runs}", flush=True)
            start = time.monotonic()
            try:
                with stem.with_suffix(".log").open("w", encoding="utf-8") as log:
                    entry["exit_code"] = run_with_owned_chrome(command, config, env, log, args.timeout)
                entry["duration_seconds"] = round(time.monotonic() - start, 2)
                report_path = stem.with_suffix(".report.json")
                html_path = stem.with_suffix(".report.html")
                entry["log"] = str(stem.with_suffix(".log"))
                if entry["exit_code"] != 0 or "error" in entry:
                    raise ValueError(entry.get("error", "Lighthouse process failed; inspect retained log"))
                report = json.loads(report_path.read_text(encoding="utf-8"))
                if report.get("runtimeError"):
                    raise ValueError(f"Lighthouse runtime error: {report['runtimeError'].get('code', 'unknown')}")
                if not html_path.is_file():
                    raise ValueError("Lighthouse HTML report is missing")
                entry.update(status="completed", json_report=str(report_path), html_report=str(html_path),
                             final_url=report.get("finalDisplayedUrl", report.get("finalUrl")),
                             lighthouse_version=report.get("lighthouseVersion"),
                             user_agent=report.get("userAgent"),
                             config_settings=report.get("configSettings"),
                             run_warnings=report.get("runWarnings", []),
                             scores={k: v.get("score") for k, v in report.get("categories", {}).items()},
                             metrics={k: report.get("audits", {}).get(k, {}).get("numericValue") for k in
                                      ("first-contentful-paint", "largest-contentful-paint", "total-blocking-time",
                                       "cumulative-layout-shift", "speed-index")})
                # Audit errors can coexist with a successful CLI exit.
                entry["audit_errors"] = [k for k, v in report.get("audits", {}).items()
                                         if v.get("scoreDisplayMode") == "error"]
                if entry["audit_errors"] or any(entry["scores"].get(k) is None for k in
                                                ("performance", "accessibility", "best-practices", "seo")):
                    entry["status"] = "incomplete"
                    failed = True
            except (OSError, ValueError, subprocess.SubprocessError) as exc:
                entry.update(status="failed", error=str(exc))
                failed = True
            save()
            print(f"{device} {index}: {entry['status']}", flush=True)
    manifest["medians"] = {}
    for device in profiles:
        completed = [r for r in manifest["runs"] if r["device"] == device and r["status"] == "completed"]
        manifest["medians"][device] = {
            "completed_runs": len(completed),
            "scores": {key: statistics.median(r["scores"][key] for r in completed)
                       for key in ("performance", "accessibility", "best-practices", "seo")} if completed else {},
        }
    manifest.update(status="incomplete" if failed else "completed", finished_at=timestamp())
    save()
    print(f"Reports: {output}\nSummary: {manifest_path}", flush=True)
    return 1 if failed else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--device", choices=("mobile", "desktop", "both"), default="both")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=240, help="Seconds per run")
    default_output = Path.home() / "seo-audits" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:6])
    parser.add_argument("--output-dir", default=str(default_output), help="New output directory; must not already exist")
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("Timeout must be positive")
    try:
        return audit(args)
    except (OSError, ValueError, KeyError) as exc:
        print(f"Cannot run audit: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
