#!/usr/bin/env python3
"""Self-tests for scripts/check_seo.py.

Hermetic: an in-process HTTP server on an ephemeral port serves a good page and
a bad page from a temporary directory. No network, no browser. Run directly:

    uv run --no-project python scripts/tests/test_check_seo.py
"""

from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import threading
import unittest
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import check_seo  # noqa: E402


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args) -> None:  # noqa: D401 - silence the request log
        pass


GOOD = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Good Page | Kit</title>
<meta name="description" content="A short description well within the one hundred and sixty character limit.">
<link rel="canonical" href="{origin}/">
<meta property="og:title" content="Good Page">
<meta property="og:description" content="Share copy">
<meta property="og:image" content="{origin}/og.png">
<meta property="og:url" content="{origin}/">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebPage","name":"Good Page"}}</script>
<script>window.__x = "client script text must not count as content";</script>
</head><body><h1>Good Page</h1><p>Server rendered proof text.</p>
<img src="/a.png" alt="Described"><img src="/b.png" alt="">
<a href="/">Home</a><a href="/second/">Second</a><a href="mailto:x@example.com">Mail</a>
</body></html>"""

SECOND = '<!doctype html><html lang="en"><head><title>Second</title></head><body><h1>Second</h1></body></html>'

BAD = """<!doctype html><html><head><title>{long_title}</title>
<link rel="canonical" href="{origin}/elsewhere/">
<meta name="robots" content="noindex">
<script type="application/ld+json">{{"@type":"Course","aggregateRating":{{"ratingValue":5}}}}</script>
<script type="application/ld+json">{{not json</script>
</head><body><h1>One</h1><h1>Two</h1><img src="/x.png">
<a href="/missing/">Missing</a><a href="/second">No slash</a><a href="#top">Top</a>
</body></html>"""


class CheckSeoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        root = Path(cls.tmp.name)
        handler = partial(QuietHandler, directory=str(root))
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        port = cls.server.server_address[1]
        cls.origin = f"http://127.0.0.1:{port}"
        (root / "index.html").write_text(GOOD.format(origin=cls.origin), encoding="utf-8")
        (root / "second").mkdir()
        (root / "second" / "index.html").write_text(SECOND, encoding="utf-8")
        (root / "bad").mkdir()
        (root / "bad" / "index.html").write_text(
            BAD.format(origin=cls.origin, long_title="T" * 70), encoding="utf-8"
        )
        (root / "robots.txt").write_text(
            f"User-agent: *\nAllow: /\nSitemap: {cls.origin}/sitemap.xml\n", encoding="utf-8"
        )
        (root / "sitemap.xml").write_text(
            '<?xml version="1.0"?><urlset>'
            f"<url><loc>{cls.origin}/</loc></url><url><loc>{cls.origin}/second/</loc></url>"
            "</urlset>",
            encoding="utf-8",
        )
        for name in ("a.png", "b.png"):
            (root / name).write_bytes(b"\x89PNG")
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.tmp.cleanup()

    def run_main(self, *args: str) -> tuple[int, str]:
        out = io.StringIO()
        err = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = check_seo.main([self.origin, *args])
        return code, out.getvalue() + err.getvalue()

    def test_good_page_passes(self) -> None:
        code, out = self.run_main(
            "/",
            "--canonical-origin", self.origin,
            "--expect-text", "Server rendered proof",
            "--require-type", "WebPage",
        )
        self.assertEqual(code, 0, out)
        self.assertIn("0 failure(s)", out)
        self.assertIn("WARN security headers", out)  # http.server sends none
        self.assertIn("PASS internal links resolve 200 without redirects: 2 unique path(s)", out)

    def test_client_script_text_is_not_content(self) -> None:
        code, out = self.run_main("/", "--no-links", "--expect-text", "client script text")
        self.assertEqual(code, 1)
        self.assertIn("FAIL text present", out)

    def test_bad_page_fails_on_every_defect(self) -> None:
        code, out = self.run_main("/bad/", "--canonical-origin", self.origin)
        self.assertEqual(code, 1)
        for name in (
            "one h1",
            "title <= 60 chars",
            "meta description present",
            "self-canonical",
            "og:title",
            "indexable (no noindex)",
            "images have src and alt",
            "json-ld block 2 parses",
            "json-ld carries no rating/review keys",
            "sitemap.xml lists the page",
            "internal links resolve 200 without redirects",
        ):
            self.assertIn(f"FAIL {name}", out, name)
        self.assertIn("WARN html lang attribute", out)
        self.assertIn("WARN no fragment destinations", out)
        self.assertIn("/missing/ -> 404", out)
        self.assertIn("/second -> 301", out)

    def test_allow_noindex_and_no_links(self) -> None:
        code, out = self.run_main("/bad/", "--allow-noindex", "--no-links", "--allow-ratings")
        self.assertEqual(code, 1)
        self.assertIn("NOTE noindex: present (allowed)", out)
        self.assertIn("NOTE internal links", out)
        self.assertNotIn("robots.txt", out)
        self.assertIn("PASS json-ld carries no rating/review keys: allowed", out)

    def test_json_report(self) -> None:
        path = Path(self.tmp.name) / "report.json"
        code, _ = self.run_main("/", "--canonical-origin", self.origin, "--json", str(path))
        self.assertEqual(code, 0)
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data[0]["path"], "/")
        self.assertEqual(data[0]["status"], 200)
        self.assertTrue(any(check["name"] == "one h1" for check in data[0]["checks"]))

    def test_missing_page_reports_status_only(self) -> None:
        code, out = self.run_main("/nowhere/", "--no-links")
        self.assertEqual(code, 1)
        self.assertIn("FAIL status: status 404", out)

    def test_rejects_relative_paths(self) -> None:
        code, out = self.run_main("about")
        self.assertEqual(code, 2)
        self.assertIn("must start with a slash", out)


if __name__ == "__main__":
    unittest.main(verbosity=1)
