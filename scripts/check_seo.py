#!/usr/bin/env python3
"""Technical SEO smoke check for a built site. Standard library only (Python 3.10+).

Fetches each PATH from BASE_URL and asserts the page-level invariants that
`docs/agent-context/web-seo-playbook.md` requires:

  * HTTP 200 with no redirect
  * exactly one <h1>
  * a title and a meta description within snippet limits
  * one self-referencing canonical (== --canonical-origin + PATH when given)
  * Open Graph title/description/image (og:url and twitter:card as warnings)
  * no noindex signal in the X-Robots-Tag header or the robots meta
    (--allow-noindex turns this into a note for preview and dev hosts)
  * an alt attribute and a source on every <img>
  * every JSON-LD block parses, carries no rating/review keys
    (--allow-ratings to permit them) and includes each --require-type
  * every --expect-text substring is present in the server-rendered text
  * robots.txt advertises a sitemap and sitemap.xml lists the page
  * every internal link resolves 200 with no redirect (--no-links to skip)

Security headers (CSP, nosniff, referrer policy) and fragment links are reported
as warnings. Exit status is 1 when any check fails.

Usage:
  python scripts/check_seo.py http://localhost:3000 / /services/ \
      --canonical-origin https://example.com
  python scripts/check_seo.py https://preview.example.com /about/ --allow-noindex --no-links
  python scripts/check_seo.py https://example.com / --expect-text "Working systems" --json seo.json

Derived from the BrollyAI course-page audit scripts (2026-09-05/06); generalised
for the agent workflow kit on 2026-09-07.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from html.parser import HTMLParser
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

USER_AGENT = "check-seo/1.0 (agent-workflow-kit)"
FORBIDDEN_JSONLD_KEYS = ("aggregateRating", "review", "reviews", "reviewRating", "ratingValue")
SECURITY_HEADERS = ("content-security-policy", "x-content-type-options", "referrer-policy")


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D401 - urllib hook
        return None


_OPENER = build_opener(_NoRedirect())


@dataclass
class Response:
    status: int
    headers: dict[str, str]
    body: str = ""
    location: str | None = None
    error: str | None = None


def fetch(url: str, timeout: float = 20.0, read_body: bool = True) -> Response:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,*/*"})
    try:
        with _OPENER.open(request, timeout=timeout) as raw:
            headers = {key.lower(): value for key, value in raw.headers.items()}
            body = raw.read().decode("utf-8", "replace") if read_body else ""
            return Response(raw.status, headers, body)
    except HTTPError as exc:
        headers = {key.lower(): value for key, value in exc.headers.items()}
        body = ""
        if read_body:
            try:
                body = exc.read().decode("utf-8", "replace")
            except Exception:  # noqa: BLE001 - body is optional on an error response
                body = ""
        return Response(exc.code, headers, body, location=headers.get("location"))
    except (URLError, OSError, ValueError) as exc:
        return Response(0, {}, "", error=str(exc))


class Page(HTMLParser):
    """Collects the head and body facts the checks need."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.lang: str | None = None
        self.title = ""
        self.meta: dict[str, str] = {}
        self.canonical: list[str] = []
        self.h1: list[str] = []
        self.links: list[str] = []
        self.images: list[dict[str, str | None]] = []
        self.jsonld: list[str] = []
        self.text: list[str] = []
        self._in_title = False
        self._in_h1 = False
        self._in_jsonld = False
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {key.lower(): value for key, value in attrs}
        if tag == "html":
            self.lang = a.get("lang")
        elif tag == "title":
            self._in_title = True
        elif tag == "meta":
            key = a.get("name") or a.get("property") or a.get("http-equiv")
            if key:
                self.meta[key.lower()] = a.get("content") or ""
        elif tag == "link" and "canonical" in (a.get("rel") or "").lower().split():
            self.canonical.append(a.get("href") or "")
        elif tag == "h1":
            self._in_h1 = True
            self.h1.append("")
        elif tag == "a" and a.get("href"):
            self.links.append(a["href"] or "")
        elif tag == "img":
            self.images.append(a)
        elif tag == "script":
            if (a.get("type") or "").lower() == "application/ld+json":
                self._in_jsonld = True
                self.jsonld.append("")
            else:
                self._skip_depth += 1
        elif tag in ("style", "noscript", "template"):
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        elif tag == "h1":
            self._in_h1 = False
        elif tag == "script":
            if self._in_jsonld:
                self._in_jsonld = False
            elif self._skip_depth:
                self._skip_depth -= 1
        elif tag in ("style", "noscript", "template") and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        if self._in_jsonld:
            self.jsonld[-1] += data
            return
        if self._skip_depth:
            return
        if self._in_h1:
            self.h1[-1] += data
        self.text.append(data)


@dataclass
class Check:
    name: str
    level: str  # PASS | FAIL | WARN | NOTE
    detail: str = ""


@dataclass
class PageReport:
    path: str
    url: str
    status: int = 0
    checks: list[Check] = field(default_factory=list)

    def add(self, name: str, ok: bool, detail: str = "", warn: bool = False) -> None:
        level = "PASS" if ok else ("WARN" if warn else "FAIL")
        self.checks.append(Check(name, level, detail))

    def note(self, name: str, detail: str) -> None:
        self.checks.append(Check(name, "NOTE", detail))

    @property
    def failures(self) -> int:
        return sum(1 for check in self.checks if check.level == "FAIL")

    @property
    def warnings(self) -> int:
        return sum(1 for check in self.checks if check.level == "WARN")


def _collect_keys(value: Any, into: set[str]) -> set[str]:
    if isinstance(value, dict):
        for key, nested in value.items():
            into.add(str(key))
            _collect_keys(nested, into)
    elif isinstance(value, list):
        for item in value:
            _collect_keys(item, into)
    return into


def _collect_types(value: Any, into: set[str]) -> set[str]:
    if isinstance(value, dict):
        kind = value.get("@type")
        if isinstance(kind, str):
            into.add(kind)
        elif isinstance(kind, list):
            into.update(str(item) for item in kind)
        for nested in value.values():
            _collect_types(nested, into)
    elif isinstance(value, list):
        for item in value:
            _collect_types(item, into)
    return into


def _normalise_text(chunks: list[str]) -> str:
    return re.sub(r"\s+", " ", " ".join(chunks)).strip()


def _internal_paths(links: list[str]) -> tuple[list[str], int, int]:
    """Return (unique internal paths, fragment-only count, fragment-carrying count)."""
    paths: list[str] = []
    fragment_only = 0
    with_fragment = 0
    for href in links:
        href = href.strip()
        if not href or href.startswith(("//", "mailto:", "tel:", "javascript:")):
            continue
        if href.startswith("#"):
            fragment_only += 1
            continue
        if not href.startswith("/"):
            continue
        parts = urlsplit(href)
        if parts.fragment:
            with_fragment += 1
        path = parts.path or "/"
        if path not in paths:
            paths.append(path)
    return paths, fragment_only, with_fragment


def check_page(base: str, path: str, opts: argparse.Namespace) -> PageReport:
    url = base.rstrip("/") + path
    report = PageReport(path=path, url=url)
    response = fetch(url, timeout=opts.timeout)
    report.status = response.status

    if response.status != 200:
        detail = response.error or f"status {response.status}"
        if response.location:
            detail += f" -> {response.location}"
        report.add("status", False, detail)
        return report
    report.add("status", True, "200")

    page = Page()
    page.feed(response.body)
    page.close()

    # Headings, title, description.
    h1_detail = f"{len(page.h1)} found"
    if len(page.h1) == 1:
        h1_detail += f": {page.h1[0].strip()[:80]!r}"
    report.add("one h1", len(page.h1) == 1, h1_detail)
    title = page.title.strip()
    report.add("title present", bool(title), title[:120])
    if title:
        report.add(f"title <= {opts.title_max} chars", len(title) <= opts.title_max, f"{len(title)} chars")
    description = (page.meta.get("description") or "").strip()
    report.add("meta description present", bool(description), description[:160])
    if description:
        report.add(
            f"description <= {opts.description_max} chars",
            len(description) <= opts.description_max,
            f"{len(description)} chars",
        )
    report.add("html lang attribute", bool(page.lang), page.lang or "missing", warn=True)

    # Canonical.
    if opts.canonical_origin:
        expected = opts.canonical_origin.rstrip("/") + path
        ok = page.canonical == [expected]
        report.add("self-canonical", ok, f"expected {expected}, found {page.canonical}")
    else:
        ok = len(page.canonical) == 1 and page.canonical[0].endswith(path)
        expected = page.canonical[0] if ok else ""
        report.add("self-canonical", ok, f"found {page.canonical}")

    # Open Graph and Twitter.
    for key in ("og:title", "og:description", "og:image"):
        report.add(key, bool(page.meta.get(key)), (page.meta.get(key) or "missing")[:120])
    report.add("og:url", bool(page.meta.get("og:url")), page.meta.get("og:url") or "missing", warn=True)
    report.add(
        "twitter:card",
        bool(page.meta.get("twitter:card")),
        page.meta.get("twitter:card") or "missing",
        warn=True,
    )

    # Indexability.
    robots_signal = (
        response.headers.get("x-robots-tag", "") + " " + page.meta.get("robots", "")
    ).lower()
    has_noindex = "noindex" in robots_signal
    if opts.allow_noindex:
        report.note("noindex", "present (allowed)" if has_noindex else "absent")
    else:
        report.add("indexable (no noindex)", not has_noindex, robots_signal.strip() or "no robots directive")

    # Images.
    bad_images = [
        (image.get("src") or image.get("srcset") or "<no src>")
        for image in page.images
        if "alt" not in image or not (image.get("src") or image.get("srcset"))
    ]
    report.add(
        "images have src and alt",
        not bad_images,
        f"{len(page.images)} images" + (f"; offenders: {bad_images[:5]}" if bad_images else ""),
    )

    # Structured data.
    parsed: list[Any] = []
    for index, block in enumerate(page.jsonld):
        try:
            parsed.append(json.loads(block))
        except json.JSONDecodeError as exc:
            report.add(f"json-ld block {index + 1} parses", False, str(exc))
    if page.jsonld and len(parsed) == len(page.jsonld):
        report.add("json-ld parses", True, f"{len(parsed)} block(s)")
    keys = _collect_keys(parsed, set())
    forbidden = sorted(key for key in keys if key in FORBIDDEN_JSONLD_KEYS)
    if forbidden and not opts.allow_ratings:
        report.add("json-ld carries no rating/review keys", False, ", ".join(forbidden))
    elif parsed:
        report.add("json-ld carries no rating/review keys", True, "allowed" if forbidden else "")
    types = _collect_types(parsed, set())
    for required in opts.require_type or []:
        report.add(f"json-ld has @type {required}", required in types, f"found {sorted(types)}")

    # Server-rendered content.
    text = _normalise_text(page.text)
    for expected_text in opts.expect_text or []:
        report.add(f"text present: {expected_text[:50]!r}", expected_text in text)

    # Security headers (informational).
    missing_headers = [name for name in SECURITY_HEADERS if name not in response.headers]
    report.add(
        "security headers",
        not missing_headers,
        f"missing {missing_headers}" if missing_headers else "",
        warn=True,
    )

    # Robots and sitemap.
    if not opts.allow_noindex:
        robots = fetch(base.rstrip("/") + "/robots.txt", timeout=opts.timeout)
        report.add(
            "robots.txt advertises a sitemap",
            robots.status == 200 and "sitemap:" in robots.body.lower(),
            f"status {robots.status}",
        )
        sitemap = fetch(base.rstrip("/") + "/sitemap.xml", timeout=opts.timeout)
        wanted = expected or url
        report.add(
            "sitemap.xml lists the page",
            sitemap.status == 200 and f"<loc>{wanted}</loc>" in sitemap.body,
            f"status {sitemap.status}; looked for <loc>{wanted}</loc>",
        )

    # Internal links.
    paths, fragment_only, with_fragment = _internal_paths(page.links)
    if fragment_only or with_fragment:
        report.add(
            "no fragment destinations",
            False,
            f"{fragment_only} fragment-only link(s), {with_fragment} link(s) carrying a fragment",
            warn=True,
        )
    else:
        report.add("no fragment destinations", True)
    if opts.no_links:
        report.note("internal links", f"{len(paths)} unique path(s), not checked (--no-links)")
    else:

        def probe(target: str) -> tuple[str, Response]:
            return target, fetch(base.rstrip("/") + target, timeout=opts.timeout, read_body=False)

        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(probe, paths))
        broken = [
            f"{target} -> {resp.status}{(' ' + resp.location) if resp.location else ''}"
            for target, resp in results
            if resp.status != 200
        ]
        report.add(
            "internal links resolve 200 without redirects",
            not broken,
            f"{len(paths)} unique path(s)" + (f"; broken: {broken[:8]}" if broken else ""),
        )
    return report


def print_report(report: PageReport) -> None:
    print(f"== {report.path}  ({report.url})")
    for check in report.checks:
        detail = f": {check.detail}" if check.detail else ""
        print(f"  {check.level:4} {check.name}{detail}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("base_url", help="Origin of the running site, e.g. http://localhost:3000")
    parser.add_argument("paths", nargs="+", help="Paths to check, each starting with /")
    parser.add_argument(
        "--canonical-origin",
        help="Production origin the canonical must point at, e.g. https://example.com",
    )
    parser.add_argument(
        "--allow-noindex",
        action="store_true",
        help="Preview/dev host: noindex is expected; skip robots/sitemap checks",
    )
    parser.add_argument("--allow-ratings", action="store_true", help="Permit rating/review keys in JSON-LD")
    parser.add_argument("--no-links", action="store_true", help="Do not probe internal links")
    parser.add_argument(
        "--expect-text",
        action="append",
        help="Substring that must appear in the server-rendered text (repeatable)",
    )
    parser.add_argument(
        "--require-type", action="append", help="JSON-LD @type that must be present (repeatable)"
    )
    parser.add_argument("--title-max", type=int, default=60)
    parser.add_argument("--description-max", type=int, default=160)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--json", dest="json_out", help="Write the full report as JSON to this file")
    return parser


def main(argv: list[str] | None = None) -> int:
    opts = build_parser().parse_args(argv)
    bad_paths = [path for path in opts.paths if not path.startswith("/")]
    if bad_paths:
        print(f"paths must start with a slash: {bad_paths}", file=sys.stderr)
        return 2

    reports = [check_page(opts.base_url, path, opts) for path in opts.paths]
    for report in reports:
        print_report(report)

    failures = sum(report.failures for report in reports)
    warnings = sum(report.warnings for report in reports)
    print(f"\n{len(reports)} page(s): {failures} failure(s), {warnings} warning(s)")

    if opts.json_out:
        with open(opts.json_out, "w", encoding="utf-8") as handle:
            json.dump([asdict(report) for report in reports], handle, indent=2)
        print(f"report written to {opts.json_out}")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
