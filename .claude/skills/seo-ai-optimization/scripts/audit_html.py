#!/usr/bin/env python3
"""Passively inventory one supplied HTML file; no requests or page execution."""

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

MAX_BYTES = 2 * 1024 * 1024


def clean(text):
    return " ".join(text.split())


def schema_types(value):
    """Walk iteratively: arbitrary JSON-LD is data, never code or remote context."""
    found = set()
    pending = [value]
    while pending:
        item = pending.pop()
        if isinstance(item, dict):
            types = item.get("@type", [])
            if isinstance(types, str):
                found.add(types)
            elif isinstance(types, list):
                found.update(t for t in types if isinstance(t, str))
            pending.extend(item.values())
        elif isinstance(item, list):
            pending.extend(item)
    return sorted(found)


class Inventory(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.result = {
            "document_markers": [],
            "titles": [],
            "descriptions": [],
            "canonicals": [],
            "robots": [],
            "headings": [],
            "links": [],
            "images": [],
            "json_ld": [],
            "limitations": [
                "Source inventory only; CSS, JavaScript and visibility are not evaluated.",
                "No HTTP, index status, ranking, speed, schema eligibility or AI citation checks.",
                "Template contents are omitted; malformed HTML may differ from browser parsing.",
            ],
        }
        self.captures = []
        self.template_depth = 0
        self.raw_tag = None
        self.raw_json = None

    def handle_starttag(self, tag, attrs):
        if self.raw_tag:
            return
        if tag == "template":
            self.template_depth += 1
        if self.template_depth:
            return
        attrs = dict(attrs)
        line = self.getpos()[0]
        if tag in {"script", "style"}:
            self.raw_tag = tag
            if tag == "script" and (attrs.get("type") or "").lower().strip() == "application/ld+json":
                self.raw_json = {"line": line, "parts": []}
            return
        if tag in {"html", "head", "body"}:
            self.result["document_markers"].append({"tag": tag, "line": line})
        if tag == "title" or re.fullmatch(r"h[1-6]", tag) or tag == "a":
            self.captures.append({"tag": tag, "line": line, "attrs": attrs, "parts": []})
        if tag == "meta":
            name = (attrs.get("name") or "").lower()
            if name == "description":
                self.result["descriptions"].append({"line": line, "content": attrs.get("content")})
            if name == "robots" or name.startswith(("googlebot", "bingbot")):
                self.result["robots"].append({"line": line, "agent": name, "content": attrs.get("content")})
        if tag == "link" and "canonical" in (attrs.get("rel") or "").lower().split():
            self.result["canonicals"].append({"line": line, "href": attrs.get("href")})
        if tag == "img":
            self.result["images"].append({
                "line": line, "src": attrs.get("src"), "alt": attrs.get("alt"),
                "alt_present": "alt" in attrs,
            })

    def handle_endtag(self, tag):
        if self.raw_tag:
            if tag == self.raw_tag:
                if self.raw_json is not None:
                    entry = {"line": self.raw_json["line"]}
                    try:
                        parsed = json.loads("".join(self.raw_json["parts"]))
                        entry.update(json_valid=True, types=schema_types(parsed))
                    except (ValueError, RecursionError):
                        entry.update(json_valid=False, types=[], error="Invalid or excessively nested JSON")
                    self.result["json_ld"].append(entry)
                self.raw_tag = self.raw_json = None
            return
        if self.template_depth:
            if tag == "template":
                self.template_depth -= 1
            return
        for index in range(len(self.captures) - 1, -1, -1):
            if self.captures[index]["tag"] == tag:
                self.finish_capture(self.captures.pop(index))
                break

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_data(self, data):
        if self.raw_tag:
            if self.raw_json is not None:
                self.raw_json["parts"].append(data)
            return
        if not self.template_depth:
            for capture in self.captures:
                capture["parts"].append(data)

    def finish_capture(self, capture, closed=True):
        tag = capture["tag"]
        entry = {"line": capture["line"], "text": clean("".join(capture["parts"]))}
        if not closed:
            entry["unclosed_in_source"] = True
        if tag == "title":
            self.result["titles"].append(entry)
        elif tag == "a":
            entry["href"] = capture["attrs"].get("href")
            self.result["links"].append(entry)
        else:
            entry["level"] = int(tag[1])
            self.result["headings"].append(entry)

    def inventory(self):
        for capture in self.captures:
            self.finish_capture(capture, closed=False)
        self.captures.clear()
        if self.raw_json is not None:
            self.result["json_ld"].append({
                "line": self.raw_json["line"], "json_valid": False,
                "error": "Unclosed JSON-LD script in source", "types": [],
            })
            self.raw_json = None
        for key in ("titles", "headings", "links"):
            self.result[key].sort(key=lambda item: item["line"])
        return self.result


def audit_file(path):
    path = Path(path).resolve(strict=True)
    if path.suffix.lower() not in {".html", ".htm"} or not path.is_file():
        raise ValueError("Provide one HTML or HTM file.")
    with path.open("rb") as source:
        raw = source.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("HTML input exceeds the 2 MiB limit.")
    parser = Inventory()
    parser.feed(raw.decode("utf-8-sig"))
    parser.close()
    return {"file": str(path), "bytes": len(raw), **parser.inventory()}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("path", help="Supplied UTF-8 HTML/HTM file (maximum 2 MiB)")
    args = cli.parse_args()
    try:
        result = audit_file(args.path)
    except (OSError, ValueError, RecursionError) as exc:
        print(f"Cannot inventory HTML: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
