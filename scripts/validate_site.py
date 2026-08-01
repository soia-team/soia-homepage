#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    "index.html",
    "404.html",
    "styles.css",
    "script.js",
    "robots.txt",
    "sitemap.xml",
    ".nojekyll",
]


class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.hrefs = []
        self.has_title = False
        self.has_main = False
        self.lang = None

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == "html":
            self.lang = data.get("lang")
        if tag == "title":
            self.has_title = True
        if tag == "main":
            self.has_main = True
        if data.get("id"):
            self.ids.add(data["id"])
        if tag == "a" and data.get("href"):
            self.hrefs.append(data["href"])


def fail(message):
    print(f"[FAIL] {message}")
    return 1


def main():
    status = 0
    for name in REQUIRED_FILES:
        if not (ROOT / name).exists():
            status |= fail(f"missing {name}")

    if status:
        return status

    html = (ROOT / "index.html").read_text(encoding="utf-8")
    parser = SiteParser()
    parser.feed(html)

    if parser.lang != "zh-CN":
        status |= fail("index.html must declare lang=zh-CN")
    if not parser.has_title:
        status |= fail("index.html is missing a title")
    if not parser.has_main:
        status |= fail("index.html is missing a main landmark")

    for href in parser.hrefs:
        if href.startswith("#") and href[1:] not in parser.ids:
            status |= fail(f"broken local anchor: {href}")

    forbidden = ["TODO", "lorem ipsum", "YOUR_", "example.com"]
    for needle in forbidden:
        if needle.lower() in html.lower():
            status |= fail(f"placeholder found: {needle}")

    if status == 0:
        print(f"[OK] validated {len(REQUIRED_FILES)} files and {len(parser.hrefs)} links")
    return status


if __name__ == "__main__":
    sys.exit(main())
