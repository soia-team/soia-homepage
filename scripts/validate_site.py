#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import re
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://soia-team.github.io"
FORMAL_PAGES = {
    "home": Path("index.html"),
    "open": Path("open/index.html"),
    "products": Path("products/index.html"),
    "course": Path("course/index.html"),
    "services": Path("services/index.html"),
    "about": Path("about/index.html"),
}
REQUIRED_FILES = [
    *FORMAL_PAGES.values(),
    Path("404.html"),
    Path("assets/styles.css"),
    Path("assets/site.js"),
    Path("robots.txt"),
    Path("sitemap.xml"),
    Path("favicon.ico"),
    Path(".nojekyll"),
]
PLACEHOLDERS = ["TODO", "lorem ipsum", "YOUR_", "example.com"]
INTERNAL_TERMS = [
    "第一桶金",
    "收入目标",
    "营收目标",
    "价格实验",
    "定价实验",
    "价格是首轮验证假设",
    "渠道策略",
    "获客策略",
    "转化策略",
    "lead scoring",
    "线索评分",
    "客户笔记",
    "客户名单",
    "私有仓结构",
    "私有仓库结构",
    "私有插件产品库",
    "私有专家",
    "private expert",
    "一客户一私有 overlay",
    "内部任务板",
    "任务看板",
    "人工权益表",
    "验证续费",
    "自动授权",
]
LEGACY_ASSET_RE = re.compile(
    r"(?:href|src)\s*=\s*([\"'])(?:/)?(?:styles\.css|script\.js)\1",
    re.IGNORECASE,
)


class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.hrefs = []
        self.stylesheets = []
        self.scripts = []
        self.canonicals = []
        self.descriptions = []
        self.title_parts = []
        self.in_title = False
        self.lang = None
        self.body_page = None
        self.main_count = 0
        self.header_mounts = 0
        self.footer_mounts = 0

    @staticmethod
    def attr_map(attrs):
        return {key: value for key, value in attrs}

    def inspect_tag(self, tag, attrs):
        data = self.attr_map(attrs)
        if tag == "html":
            self.lang = data.get("lang")
        elif tag == "body":
            self.body_page = data.get("data-page")
        elif tag == "title":
            self.in_title = True
        elif tag == "main":
            self.main_count += 1

        if "data-site-header" in data:
            self.header_mounts += 1
        if "data-site-footer" in data:
            self.footer_mounts += 1
        if data.get("id"):
            self.ids.add(data["id"])
        if tag == "a" and data.get("href"):
            self.hrefs.append(data["href"])
        if tag == "link":
            rel = (data.get("rel") or "").casefold().split()
            href = data.get("href")
            if href and "stylesheet" in rel:
                self.stylesheets.append(href)
            if href and "canonical" in rel:
                self.canonicals.append(href)
        if tag == "script" and data.get("src"):
            self.scripts.append(data["src"])
        if tag == "meta" and (data.get("name") or "").casefold() == "description":
            self.descriptions.append((data.get("content") or "").strip())

    def handle_starttag(self, tag, attrs):
        self.inspect_tag(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        self.inspect_tag(tag, attrs)

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title_parts.append(data)

    @property
    def title(self):
        return " ".join(part.strip() for part in self.title_parts if part.strip())


def fail(message):
    print(f"[FAIL] {message}")
    return 1


def local_target(href):
    parts = urlsplit(href)
    if parts.scheme or parts.netloc or not parts.path:
        return None
    path = parts.path
    if not path.startswith("/"):
        return None
    if path == "/":
        return ROOT / "index.html"
    relative = path.lstrip("/")
    if path.endswith("/"):
        return ROOT / relative / "index.html"
    return ROOT / relative


def validate_html(relative_path, expected_page=None, require_canonical=True):
    status = 0
    path = ROOT / relative_path
    html = path.read_text(encoding="utf-8")
    parser = SiteParser()
    parser.feed(html)
    label = relative_path.as_posix()

    if parser.lang != "zh-CN":
        status |= fail(f"{label}: must declare lang=zh-CN")
    if not parser.title:
        status |= fail(f"{label}: missing non-empty title")
    if len(parser.descriptions) != 1 or not parser.descriptions[0]:
        status |= fail(f"{label}: requires one non-empty meta description")
    if parser.main_count != 1:
        status |= fail(f"{label}: requires exactly one main landmark")
    if parser.header_mounts != 1:
        status |= fail(f"{label}: requires one data-site-header mount")
    if parser.footer_mounts != 1:
        status |= fail(f"{label}: requires one data-site-footer mount")
    if parser.stylesheets != ["/assets/styles.css"]:
        status |= fail(f"{label}: must use only /assets/styles.css")
    if parser.scripts != ["/assets/site.js"]:
        status |= fail(f"{label}: must use only /assets/site.js")
    if require_canonical and len(parser.canonicals) != 1:
        status |= fail(f"{label}: requires one canonical link")
    if expected_page is not None and parser.body_page != expected_page:
        status |= fail(f"{label}: body data-page must be {expected_page!r}")
    if LEGACY_ASSET_RE.search(html):
        status |= fail(f"{label}: references legacy styles.css or script.js")

    lowered = html.casefold()
    for needle in PLACEHOLDERS:
        if needle.casefold() in lowered:
            status |= fail(f"{label}: placeholder found: {needle}")
    for needle in INTERNAL_TERMS:
        if needle.casefold() in lowered:
            status |= fail(f"{label}: internal-only term found: {needle}")

    for href in parser.hrefs:
        if href.startswith("#"):
            if len(href) == 1 or href[1:] not in parser.ids:
                status |= fail(f"{label}: broken local anchor: {href}")
            continue
        if href.casefold().startswith("javascript:"):
            status |= fail(f"{label}: javascript link is not allowed")
            continue
        target = local_target(href)
        if target is not None and not target.exists():
            status |= fail(f"{label}: missing local target for {href}")

    return status, parser.title, len(parser.hrefs)


def validate_sitemap():
    status = 0
    sitemap_path = ROOT / "sitemap.xml"
    try:
        tree = ET.parse(sitemap_path)
    except ET.ParseError as error:
        return fail(f"sitemap.xml: invalid XML: {error}")

    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    actual = {
        (node.text or "").strip()
        for node in tree.findall("sm:url/sm:loc", namespace)
    }
    expected = {
        f"{BASE_URL}/",
        f"{BASE_URL}/open/",
        f"{BASE_URL}/products/",
        f"{BASE_URL}/course/",
        f"{BASE_URL}/services/",
        f"{BASE_URL}/about/",
    }
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        status |= fail(f"sitemap.xml: route mismatch; missing={missing}, extra={extra}")
    return status


def main():
    status = 0
    for relative_path in REQUIRED_FILES:
        if not (ROOT / relative_path).exists():
            status |= fail(f"missing {relative_path.as_posix()}")
    if (ROOT / "styles.css").exists():
        status |= fail("legacy root styles.css must be removed")
    if (ROOT / "script.js").exists():
        status |= fail("legacy root script.js must be removed")
    if status:
        return status

    titles = {}
    total_links = 0
    for page_name, relative_path in FORMAL_PAGES.items():
        page_status, title, link_count = validate_html(relative_path, page_name)
        status |= page_status
        total_links += link_count
        if title in titles:
            status |= fail(
                f"{relative_path.as_posix()}: duplicate title also used by {titles[title]}"
            )
        else:
            titles[title] = relative_path.as_posix()

    page_status, _, link_count = validate_html(
        Path("404.html"), expected_page=None, require_canonical=False
    )
    status |= page_status
    total_links += link_count
    status |= validate_sitemap()

    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    expected_sitemap_line = f"Sitemap: {BASE_URL}/sitemap.xml"
    if expected_sitemap_line not in robots:
        status |= fail("robots.txt: missing canonical sitemap URL")

    if status == 0:
        print(
            f"[OK] validated {len(FORMAL_PAGES)} formal pages, 404, shared assets, "
            f"{total_links} links, robots.txt and sitemap.xml"
        )
    return status


if __name__ == "__main__":
    sys.exit(main())
