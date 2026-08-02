#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import re
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://soia-team.github.io"
REQUIRED_FILES = [
    Path("index.html"),
    Path("open/index.html"),
    Path("products/index.html"),
    Path("pricing/index.html"),
    Path("blog/index.html"),
    Path("blog/codex-open-design/index.html"),
    Path("showcase/index.html"),
    Path("docs/index.html"),
    Path("spec/index.html"),
    Path("course/index.html"),
    Path("services/index.html"),
    Path("about/index.html"),
    Path("en/index.html"),
    Path("en/open/index.html"),
    Path("en/products/index.html"),
    Path("en/pricing/index.html"),
    Path("en/blog/index.html"),
    Path("en/blog/codex-open-design/index.html"),
    Path("en/showcase/index.html"),
    Path("en/docs/index.html"),
    Path("en/spec/index.html"),
    Path("en/course/index.html"),
    Path("en/services/index.html"),
    Path("en/about/index.html"),
    Path("404.html"),
    Path("assets/styles.css"),
    Path("assets/site.js"),
    Path("assets/fonts/public-sans-latin.woff2"),
    Path("assets/fonts/space-grotesk-latin.woff2"),
    Path("assets/fonts/jetbrains-mono-latin.woff2"),
    Path("robots.txt"),
    Path("sitemap.xml"),
    Path("favicon.ico"),
    Path(".nojekyll"),
]
PLACEHOLDERS = ["TODO", "lorem ipsum", "YOUR_", "example.com"]
INTERNAL_TERMS = [
    "第一桶金", "收入目标", "营收目标", "价格实验", "定价实验",
    "价格是首轮验证假设", "渠道策略", "获客策略", "转化策略",
    "lead scoring", "线索评分", "客户笔记", "客户名单", "私有仓结构",
    "私有仓库结构", "私有插件产品库", "私有专家", "private expert",
    "一客户一私有 overlay", "内部任务板", "任务看板", "人工权益表",
    "验证续费", "自动授权",
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
        self.alternates = {}
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
            if href and "alternate" in rel and data.get("hreflang"):
                self.alternates[data["hreflang"]] = href
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


def page_url(relative_path: Path) -> str:
    if relative_path == Path("index.html"):
        return f"{BASE_URL}/"
    return f"{BASE_URL}/{relative_path.parent.as_posix()}/"


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
    return ROOT / relative / "index.html" if path.endswith("/") else ROOT / relative


def expected_lang(relative_path: Path) -> str:
    return "en" if relative_path.parts and relative_path.parts[0] == "en" else "zh-CN"


def expected_page(relative_path: Path) -> str:
    parts = list(relative_path.parts[:-1])
    if parts and parts[0] == "en":
        parts.pop(0)
    if not parts:
        return "home"
    return "open" if parts[0] == "open" else parts[0]


def validate_html(relative_path: Path, require_canonical=True):
    status = 0
    path = ROOT / relative_path
    html = path.read_text(encoding="utf-8")
    parser = SiteParser()
    parser.feed(html)
    label = relative_path.as_posix()

    if parser.lang != expected_lang(relative_path):
        status |= fail(f"{label}: unexpected html lang {parser.lang!r}")
    if not parser.title:
        status |= fail(f"{label}: missing non-empty title")
    if len(parser.descriptions) != 1 or not parser.descriptions[0]:
        status |= fail(f"{label}: requires one non-empty meta description")
    if parser.main_count != 1:
        status |= fail(f"{label}: requires exactly one main landmark")
    if parser.header_mounts != 1 or parser.footer_mounts != 1:
        status |= fail(f"{label}: requires shared header and footer mounts")
    if len(parser.stylesheets) != 1 or urlsplit(parser.stylesheets[0]).path != "/assets/styles.css":
        status |= fail(f"{label}: must use only /assets/styles.css")
    if len(parser.scripts) != 1 or urlsplit(parser.scripts[0]).path != "/assets/site.js":
        status |= fail(f"{label}: must use only /assets/site.js")
    if require_canonical:
        if parser.canonicals != [page_url(relative_path)]:
            status |= fail(f"{label}: canonical URL mismatch")
        if set(parser.alternates) != {"zh-CN", "en", "x-default"}:
            status |= fail(f"{label}: requires zh-CN, en and x-default alternates")
    if relative_path != Path("404.html") and parser.body_page != expected_page(relative_path):
        status |= fail(f"{label}: body data-page mismatch")
    if LEGACY_ASSET_RE.search(html):
        status |= fail(f"{label}: references legacy root assets")

    lowered = html.casefold()
    for needle in PLACEHOLDERS + INTERNAL_TERMS:
        if needle.casefold() in lowered:
            status |= fail(f"{label}: prohibited or placeholder text found: {needle}")

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


def validate_sitemap(pages: list[Path]):
    status = 0
    try:
        tree = ET.parse(ROOT / "sitemap.xml")
    except ET.ParseError as error:
        return fail(f"sitemap.xml: invalid XML: {error}")
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    actual = {
        (node.text or "").strip()
        for node in tree.findall("sm:url/sm:loc", namespace)
    }
    expected = {page_url(page) for page in pages}
    if actual != expected:
        status |= fail(
            f"sitemap.xml: route mismatch; missing={len(expected - actual)}, "
            f"extra={len(actual - expected)}"
        )
    return status


def main():
    status = 0
    for relative_path in REQUIRED_FILES:
        if not (ROOT / relative_path).exists():
            status |= fail(f"missing {relative_path.as_posix()}")
    if (ROOT / "styles.css").exists() or (ROOT / "script.js").exists():
        status |= fail("legacy root assets must be removed")
    if status:
        return status

    pages = sorted(
        path.relative_to(ROOT)
        for path in ROOT.rglob("index.html")
        if ".git" not in path.parts
    )
    titles = {}
    total_links = 0
    for relative_path in pages:
        page_status, title, link_count = validate_html(relative_path)
        status |= page_status
        total_links += link_count
        if title in titles:
            status |= fail(
                f"{relative_path.as_posix()}: duplicate title also used by {titles[title]}"
            )
        else:
            titles[title] = relative_path.as_posix()

    page_status, _, link_count = validate_html(
        Path("404.html"), require_canonical=False
    )
    status |= page_status
    total_links += link_count
    status |= validate_sitemap(pages)

    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if f"Sitemap: {BASE_URL}/sitemap.xml" not in robots:
        status |= fail("robots.txt: missing canonical sitemap URL")
    if status == 0:
        print(
            f"[OK] validated {len(pages)} routed pages, 404, shared assets, "
            f"{total_links} links, robots.txt and sitemap.xml"
        )
    return status


if __name__ == "__main__":
    sys.exit(main())
