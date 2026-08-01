#!/usr/bin/env python3
"""Generate bilingual domain and Skill pages from SOIA's public catalog."""

from __future__ import annotations

import argparse
from collections import OrderedDict
from dataclasses import dataclass
from datetime import date
from html import escape
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://soia-team.github.io"


@dataclass(frozen=True)
class Domain:
    plugin: str
    slug: str
    code: str
    title_zh: str
    title_en: str
    summary_zh: str
    summary_en: str
    repo: str


DOMAINS = OrderedDict(
    (item.plugin, item)
    for item in [
        Domain(
            "soia-pkm-vault", "pkm-vault", "PKM",
            "个人知识与内容资产", "Knowledge & Content Systems",
            "采集网页与平台内容，整理 Markdown / Obsidian 知识库，提炼观点，并转换为可复用的学习与表达产物。",
            "Capture sources, maintain Markdown and Obsidian vaults, distill knowledge, and transform it into reusable learning and publishing assets.",
            "soia-open-pkm-vault-skills",
        ),
        Domain(
            "soia-env", "environment", "ENV",
            "AI 工作环境", "AI Work Environments",
            "面向新手安装、验证和诊断 AI CLI、本地运行时、网络与存储环境，危险动作保留人工确认。",
            "Install, verify, and diagnose AI CLIs, local runtimes, networking, and storage with explicit approval gates.",
            "soia-open-env-skills",
        ),
        Domain(
            "soia-dev", "development", "DEV",
            "软件工程交付", "Software Delivery",
            "把代码改动、测试、审查、修复、发版和仓库运维组织成证据完整的工程闭环。",
            "Turn coding, testing, review, fixes, releases, and repository operations into evidence-backed delivery loops.",
            "soia-open-dev-skills",
        ),
        Domain(
            "soia-media-content", "media-content", "MEDIA",
            "内容生产与发布草稿", "Content Production",
            "把已有观点与资料转成文章、配图和多平台草稿；发布动作默认由用户最终确认。",
            "Turn owned ideas and source material into articles, visuals, and channel-ready drafts while keeping final publishing under user control.",
            "soia-open-media-content-skills",
        ),
        Domain(
            "soia-dev-design", "development-design", "DESIGN",
            "产品与技术设计", "Product & Technical Design",
            "覆盖 PRD、设计探索、Open Design、架构图、draw.io / Visio 与 Office 文档工作流。",
            "Cover product requirements, design exploration, Open Design, architecture diagrams, draw.io / Visio, and Office workflows.",
            "soia-open-dev-design-skills",
        ),
        Domain(
            "soia-meta", "meta", "META",
            "技能生态管理", "Skill Ecosystem",
            "按需求寻找能力、同步技能、完成版本发布，并把含糊请求整理成可执行提示词。",
            "Find the right capability, synchronize skills, close release loops, and turn vague requests into executable prompts.",
            "soia-open-skills",
        ),
        Domain(
            "soia-cwork-office", "collaborative-office", "CWORK",
            "协作办公资料", "Collaborative Office",
            "以最小权限处理飞书知识库、云文档和 ProcessOn 图表，将授权资料沉淀为本地可复核文件。",
            "Work with Feishu knowledge bases, cloud documents, and ProcessOn diagrams under least privilege, preserving reviewable local artifacts.",
            "soia-open-cwork-office-skills",
        ),
        Domain(
            "soia-edu-course", "education-course", "EDU",
            "课程与教案", "Course Design",
            "从主题、受众和课时约束设计课程大纲，再落成可执行教案与讲义结构。",
            "Design course outlines from audience and time constraints, then turn them into executable lesson plans and teaching materials.",
            "soia-open-edu-course-skills",
        ),
    ]
)


FEATURED_EN = {
    "soia-env-ai-cli-upgrade": "Audit multiple AI CLIs and, when authorized, upgrade them after a dry run and verify the result.",
    "soia-env-antigravity-cli-install": "Help a newcomer install, sign in to, migrate, or explicitly update Google's Antigravity CLI (agy).",
    "soia-env-claude-cli-install": "Help a newcomer install, sign in to, or explicitly update Anthropic's Claude Code CLI.",
    "soia-env-codex-setup-support": "Diagnose and support installation, sign-in, performance, and storage issues for the Codex desktop app and CLI.",
    "soia-env-deepcode-cli-install": "Help a newcomer install, configure, or explicitly update the open-source Deep Code Agent CLI from lessweb.",
    "soia-env-environment-setup": "Plan and verify a development environment from scratch for a newcomer, coordinating the installation skills it requires.",
    "soia-env-kimi-cli-install": "Check, install, sign in to, or explicitly update Moonshot AI's Kimi Code CLI while distinguishing official and npm installations and otherwise reporting only version and auto-update state.",
    "soia-env-network-diagnose": "Diagnose tool-installation network problems read-only across DNS, HTTPS, proxies, certificates, official sources, and timeouts, then report causes and results in a fixed seven-column format.",
    "soia-env-node-install": "Help a newcomer install, verify, or explicitly update Node.js and npm.",
    "soia-env-opencode-cli-install": "Help a newcomer install, sign in to, configure, or explicitly update the OpenCode CLI.",
    "soia-env-python-install": "Help a newcomer install, verify, or explicitly update Python and pip.",
    "soia-env-qoder-cli-install": "Check, install, sign in to, or explicitly update the Qoder CLI while distinguishing standalone, Homebrew, and npm sources and otherwise reporting only version and auto-update settings.",
    "soia-env-storage-cleanup": "Inventory SOIA-managed configuration, state, cache, and temporary storage, propose a cleanup list with risks, and delete only after the user reviews the latest list and gives explicit approval.",
    "soia-env-workbuddy-install": "Help a newcomer install, verify, or explicitly update the WorkBuddy desktop client.",
    "soia-dev-agent-cli-dispatch": "Route bounded work to external AI CLIs and selected models while returning controlled execution and usage receipts.",
    "soia-dev-agent-md-advisor": "Diagnose, draft, and revise AI project instructions and configuration files.",
    "soia-dev-coding-protocol": "Apply a minimal-scope, verification-first, anti-fake-fix, and post-write review contract to routine fixes, refactors, implementations, and reviews.",
    "soia-dev-doc-sync": "Audit and repair drift between a repository's documentation, README, changelog, version files, and declared sources of truth, updating derived documents in dependency order.",
    "soia-dev-fix-loop": "Resolve review or test findings through a five-step loop of reproduction, decision, repair, regression testing, and an evidence-backed receipt.",
    "soia-dev-github-ops": "Operate GitHub through the gh CLI and review or repair pull-request compliance.",
    "soia-dev-project-scaffold": "Create a minimal AI-collaboration baseline for a new Git project with an editable AGENTS.md and docs navigation after confirming the target path.",
    "soia-dev-release-plan-checklist": "Create release checklists with preflight gates, staged validation, post-release checks, and rollback planning for software delivery.",
    "soia-dev-terminal-ops": "Manage long-running POSIX, macOS, or Linux jobs, tmux sessions, logs, stall diagnosis, and safe recovery, requiring multiple signals before a TERM-to-KILL shutdown sequence.",
    "soia-dev-test-draft-doc": "Produce a test plan, test cases, and acceptance mapping from requirements, a PRD, or a change description.",
    "soia-dev-archify-diagrams": "Use Archify to turn architecture, data-flow, or process descriptions into maintainable JSON diagrams and PNG previews.",
    "soia-dev-design-draft-prd": "Draft a general software PRD and user stories from a short request, clarifying functional scope and acceptance criteria.",
    "soia-dev-drawio-visio-diagrams": "Safely convert, inventory, and selectively upgrade Visio VSDX files into editable draw.io diagrams.",
    "soia-dev-officecli-ops": "Use OfficeCLI to read Office files safely, modify copies, and validate DOCX, XLSX, and PPTX outputs.",
    "soia-media-generate-article-image": "Design prompts for article covers, recap cards, study notes, visual-metaphor posters, or information-dense skill-library cards, then validate facts, text, and rendered pixels.",
    "soia-media-publish-wechat-draft": "Format a finished article as mechanically validated inline-styled HTML and send it only to the WeChat Official Account draft box, never to automatic broadcast.",
    "soia-media-publish-x-article": "Upload a Markdown article to X Articles, validate its formatting, and save it only as a draft.",
    "soia-media-publish-x-thread": "Adapt a finished article into a numbered X thread within length limits and, when authorized, save it as a draft.",
    "soia-meta-prompt-clarity": "Draft, diagnose, and specify Chinese or English prompts while preserving the user's intent, language, and safety boundaries.",
    "soia-meta-skill-release": "After a skill pull request is merged, complete installation, old-name cleanup, multi-agent symlink and lock reconciliation, marketplace refresh, client updates, and WorkBuddy expert installation.",
    "soia-meta-sync-skills": "Synchronize one shared skill source into user-selected AI tool directories with a preview, per-item selection, hard-dependency closure, and constrained cleanup.",
    "soia-cwork-feishu-cli": "Use Feishu's official lark-cli with least-privilege read-only access to research Wiki, Drive, and document content.",
    "soia-cwork-processon-diagrams": "Safely inventory and, when authorized, export, validate, and archive ProcessOn diagrams.",
    "soia-edu-compose-lesson-plan": "Turn an approved course outline into an executable lesson plan and teaching-material structure, including classroom activities where needed.",
    "soia-pkm-alipan-curator": "Plan and organize Aliyun Drive resources into a reviewable collection index and learning plan.",
    "soia-pkm-alipan-drive-ops": "Handle Aliyun Drive sign-in, browsing, and file operations as the low-level capability for resource organization.",
    "soia-pkm-baidu-netdisk-ops": "Provide atomic Baidu Netdisk operations and a read-only JSONL scanning adapter.",
    "soia-pkm-bootstrap-vault-base": "Initialize a platform-neutral AI-native Markdown vault with plan-first, create-only operations, inspectable structure rules, lifecycle conventions, templates, and multi-agent adapters.",
    "soia-pkm-bootstrap-vault-ima": "Connect an existing local Markdown vault to Tencent ima by installing the client, mapping folders, configuring official Skills for folder monitoring, and verifying retrieval.",
    "soia-pkm-bootstrap-vault-obsidian": "Configure an existing Markdown vault for Obsidian through dry-run and structure-aware merges that preserve unknown settings, with Bases and optional wide-page CSS.",
    "soia-pkm-clip-douyin": "Archive a single Douyin video into an Obsidian vault while preserving a local media index.",
    "soia-pkm-clip-drive": "Batch-import existing cloud or local PDF, Word, and document files into an Obsidian vault by extracting text, creating source notes, and handing them off for organization.",
    "soia-pkm-clip-github-repo": "Archive an open-source GitHub repository as a project record and research note in an Obsidian vault.",
    "soia-pkm-clip-rednote": "Archive a single Xiaohongshu image, text, or video post into an Obsidian vault.",
    "soia-pkm-clip-wechat-account": "Batch-archive published articles from a WeChat Official Account managed by the user through the official API, console endpoints, or an authenticated cookie, with URL deduplication.",
    "soia-pkm-clip-wechat-article": "Archive one WeChat Official Account article by extracting its title, author, body, publication time, and images from static HTML, with Obsidian preferred for optional PDF export.",
    "soia-pkm-distill-article-opinion": "Use one-question-at-a-time Socratic prompts to turn the user's responses to a vault article into their own viewpoint or a topic synthesis.",
    "soia-pkm-extract-vault-knowledge": "Extract reusable, source-linked long-term knowledge from active work, frozen evidence, articles, project research, or historical imports while preserving originals and isolating sensitive material.",
    "soia-pkm-interpret-article-analysis": "Create a separate AI interpretation of a long vault article or paper to help assess whether it merits deeper study without changing the source or speaking for the user.",
    "soia-pkm-library-book-catalog": "Maintain an Obsidian book library locally and idempotently by creating missing reading records and regenerating library, reading-log, and type views without relying on WeRead.",
    "soia-pkm-library-weread-sync": "Synchronize finished books and highlights from WeRead into an Obsidian library and use the WeRead API to complete individual book details.",
    "soia-pkm-log-agent-sessions": "Record minimal vault-change snapshots for local agents such as Claude Code and Codex, with deduplication, dry-run, safe notify-hook merging, and uninstall support.",
    "soia-pkm-manage-vault-lifecycle": "Plan and safely execute the routing of inbox items, active work, frozen evidence, durable knowledge, and historical archives in a Markdown or Obsidian vault.",
    "soia-pkm-organize-article-moc": "Organize an Obsidian article library through normalized metadata, topic links, monthly grouping, and two-level maps of content.",
    "soia-pkm-query-vault": "Search a Markdown or Obsidian vault read-only across filenames, content, frontmatter, tags, backlinks, and sections, prioritizing current state, stable knowledge, evidence, and archives.",
    "soia-pkm-reading-plan": "Turn a book list, topic, or viewpoint map into a word-count-based reading schedule and save it as an actionable Obsidian note.",
    "soia-pkm-transform-article-notebooklm": "Use NotebookLM to turn an article into learning materials.",
    "soia-pkm-transform-article-visual": "Turn an article into a long-form graphic, infographic, poster, cover, or illustration, using local HTML/CSS capture by default with optional Open Design or Codex image generation.",
    "soia-pkm-transform-obsidian-pdf": "Export a Markdown note inside a vault to PDF through Obsidian's native export, with pandoc or WeasyPrint as the fallback for material outside the vault.",
    "soia-pkm-translate-article-zh": "Translate a non-Chinese article into a separate Chinese draft in quick, normal, or refined mode while keeping terminology consistent and preserving the source.",
    "soia-pkm-clip-web": "Archive a web article into a Markdown or Obsidian vault with a consistent record, source trail, and reviewable output.",
    "soia-pkm-clip-x": "Capture a single X post, thread, or Article into the user's vault while preserving source context.",
    "soia-pkm-transform-article-ppt": "Turn an article, outline, or topic into an editable PowerPoint-centered media package with validation and privacy boundaries.",
    "soia-pkm-maintain-vault-health": "Audit a Markdown or Obsidian vault for broken links, ambiguous names, tag drift, and stale content before authorized maintenance.",
    "soia-env-open-skills-install": "Install or update SOIA open skills for Claude Code, Codex, or WorkBuddy at domain or individual-skill granularity.",
    "soia-env-codex-install": "Help a newcomer install, verify, or explicitly update the OpenAI Codex CLI using the official path.",
    "soia-dev-task-execute": "Run a bounded engineering task from scope and implementation through verification, independent review, and delivery receipt.",
    "soia-dev-review-panel": "Perform a read-only adversarial review of a code diff or skill package from multiple perspectives.",
    "soia-media-compose-article-draft": "Turn distilled user viewpoints and owned source notes into an article draft ready for channel-specific adaptation.",
    "soia-media-publish-rednote-card": "Adapt a finished draft into a Xiaohongshu-ready text package with title options, short sections, tags, and image guidance.",
    "soia-dev-design-explorer": "Use Open Design to explore high-fidelity prototypes, variants, decks, motion, and design reviews with reproducible evidence.",
    "soia-dev-open-design-ops": "Provide the environment checks and atomic operations required by higher-level Open Design workflows.",
    "soia-meta-find-skill": "Resolve a natural-language goal to the smallest relevant SOIA skill and explain which domain plugin provides it.",
    "soia-cwork-feishu-doc-git-sync": "Synchronize authorized Feishu knowledge-base or cloud-document content into local Markdown with source and sync metadata.",
    "soia-edu-design-course-outline": "Design a course outline from the topic, audience, learning goals, duration, and delivery constraints.",
}


TOKEN_LABELS = {
    "ai": "AI", "api": "API", "cli": "CLI", "codex": "Codex",
    "claude": "Claude", "workbuddy": "WorkBuddy", "pkm": "PKM",
    "ppt": "PowerPoint", "pdf": "PDF", "x": "X", "github": "GitHub",
    "git": "Git", "wechat": "WeChat", "rednote": "Xiaohongshu",
    "feishu": "Feishu", "processon": "ProcessOn", "drawio": "draw.io",
    "visio": "Visio", "officecli": "OfficeCLI", "notebooklm": "NotebookLM",
}


@dataclass(frozen=True)
class Skill:
    name: str
    summary_zh: str
    domain: Domain

    @property
    def title_en(self) -> str:
        parts = self.name.split("-")[2:]
        return " ".join(TOKEN_LABELS.get(part, part.capitalize()) for part in parts)

    @property
    def summary_en(self) -> str:
        return FEATURED_EN[self.name]


def source_commit(source_root: Path) -> tuple[str, str]:
    commit = subprocess.check_output(
        ["git", "-C", str(source_root), "rev-parse", "HEAD"], text=True
    ).strip()
    commit_date = subprocess.check_output(
        ["git", "-C", str(source_root), "show", "-s", "--format=%cs", "HEAD"],
        text=True,
    ).strip()
    return commit, commit_date


def parse_catalog(source_root: Path) -> list[Skill]:
    index = source_root / "docs" / "skills" / "README.md"
    if not index.exists():
        raise SystemExit(f"missing public catalog index: {index}")
    tick = chr(96)
    section_re = re.compile(
        r"^## " + tick + r"(soia-[^" + tick + r"]+)" + tick + r"[　 ]+([0-9]+) 个技能$"
    )
    row_re = re.compile(
        r"^\| \[" + tick + r"(?P<name>soia-[^" + tick + r"]+)" + tick
        + r"\]\([^)]+\) \| (?P<summary>.+) \|$"
    )
    current: Domain | None = None
    skills: list[Skill] = []
    for line in index.read_text(encoding="utf-8").splitlines():
        section = section_re.match(line)
        if section:
            plugin = section.group(1)
            if plugin not in DOMAINS:
                raise SystemExit(f"unknown domain in catalog: {plugin}")
            current = DOMAINS[plugin]
            continue
        row = row_re.match(line)
        if row and current:
            skills.append(Skill(row.group("name"), row.group("summary").strip(), current))
    names = [skill.name for skill in skills]
    if not skills or len(names) != len(set(names)):
        raise SystemExit("catalog is empty or contains duplicate skill names")
    return skills


def route(locale: str, suffix: str = "") -> str:
    prefix = "/en" if locale == "en" else ""
    return f"{prefix}/{suffix.lstrip('/')}" if suffix else f"{prefix}/"


def head(locale: str, title: str, description: str, path: str) -> str:
    is_en = locale == "en"
    zh_path = path.replace("/en", "", 1) if is_en else path
    en_path = path if is_en else ("/en/" if path == "/" else f"/en{path}")
    canonical = f"{BASE_URL}{path}"
    return f"""  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="color-scheme" content="light" />
    <meta name="theme-color" content="#fbfaf7" />
    <title>{escape(title)}</title>
    <meta name="description" content="{escape(description, quote=True)}" />
    <meta property="og:title" content="{escape(title, quote=True)}" />
    <meta property="og:description" content="{escape(description, quote=True)}" />
    <meta property="og:type" content="website" />
    <meta property="og:url" content="{canonical}" />
    <meta property="og:image" content="{BASE_URL}/assets/og.png" />
    <meta property="og:image:alt" content="SOIA · Agent workflows for real-world delivery" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:image" content="{BASE_URL}/assets/og.png" />
    <link rel="canonical" href="{canonical}" />
    <link rel="alternate" hreflang="zh-CN" href="{BASE_URL}{zh_path}" />
    <link rel="alternate" hreflang="en" href="{BASE_URL}{en_path}" />
    <link rel="alternate" hreflang="x-default" href="{BASE_URL}{zh_path}" />
    <link rel="stylesheet" href="/assets/styles.css" />
  </head>"""


def document(locale: str, page: str, title: str, description: str, path: str, main: str) -> str:
    skip = "Skip to content" if locale == "en" else "跳到正文"
    lang = "en" if locale == "en" else "zh-CN"
    return f"""<!doctype html>
<html lang="{lang}">
{head(locale, title, description, path)}
  <body data-page="{page}">
    <a class="skip-link" href="#main">{skip}</a>
    <div data-site-header></div>
    <main id="main">
{main}
    </main>
    <div data-site-footer></div>
    <script src="/assets/site.js" defer></script>
  </body>
</html>
"""


def domain_path(locale: str, domain: Domain) -> str:
    return route(locale, f"open/{domain.slug}/")


def skill_path(locale: str, skill: Skill) -> str:
    return route(locale, f"open/{skill.domain.slug}/{skill.name}/")


def domain_card(locale: str, domain: Domain, count: int) -> str:
    en = locale == "en"
    title = domain.title_en if en else domain.title_zh
    summary = domain.summary_en if en else domain.summary_zh
    status = f"{count} catalog skills" if en else f"目录收录 {count} 个 Skills"
    action = "Explore domain" if en else "进入能力域"
    return f"""            <a class="plugin-card" data-catalog-card href="{domain_path(locale, domain)}">
              <div class="plugin-icon" aria-hidden="true">{domain.code}</div>
              <div>
                <span class="status status--available">{escape(status)}</span>
                <h3>{escape(title)}</h3>
                <p>{escape(summary)}</p>
                <span class="card-link">{action} →</span>
              </div>
            </a>"""


# -- RENDERERS --


def render_domain(
    locale: str,
    domain: Domain,
    skills: list[Skill],
    commit: str,
    commit_date: str,
) -> str:
    en = locale == "en"
    title = domain.title_en if en else domain.title_zh
    summary = domain.summary_en if en else domain.summary_zh
    cards = []
    for skill in skills:
        skill_summary = skill.summary_en if en else skill.summary_zh
        action = "View detail" if en else "查看详情"
        cards.append(
            f"""          <a class="catalog-row" data-catalog-card href="{skill_path(locale, skill)}">
            <code>{escape(skill.name)}</code>
            <p>{escape(skill_summary)}</p>
            <span class="row-action">{action} →</span>
          </a>"""
        )
    open_path = route(locale, "open/")
    services_path = route(locale, "services/")
    breadcrumb_label = "Breadcrumb" if en else "面包屑"
    back = "Open capabilities" if en else "开源能力"
    source_label = "CATALOG SNAPSHOT" if en else "公开目录快照"
    count_label = "documented skills" if en else "个已记录 Skills"
    search = "Search skills in this domain…" if en else "搜索这个能力域里的 Skills……"
    warning = (
        "This page mirrors the public documentation catalog. Installable marketplace "
        "versions can lag the docs while a release is being completed."
        if en
        else "本页镜像公开文档目录。发布过程中，插件市场的可安装版本可能暂时落后于文档；安装状态以公开 marketplace manifest 为准。"
    )
    main = f"""      <section class="domain-hero">
        <div class="shell">
          <nav class="breadcrumb" aria-label="{breadcrumb_label}">
            <a href="{route(locale)}">SOIA</a><span aria-hidden="true">/</span>
            <a href="{open_path}">{back}</a><span aria-hidden="true">/</span>
            <span aria-current="page">{escape(title)}</span>
          </nav>
          <div class="domain-hero-grid">
            <div>
              <p class="eyebrow">PUBLIC CAPABILITY DOMAIN · {escape(domain.plugin)}</p>
              <h1>{escape(title)}</h1>
              <p class="page-lead">{escape(summary)}</p>
              <div class="route-map" aria-label="{"Page level" if en else "页面层级"}">
                <span>L1 · SOIA</span><span>L2 · Open</span><span>L3 · {escape(domain.code)}</span>
              </div>
            </div>
            <aside class="domain-stat">
              <span>{source_label}</span>
              <strong>{len(skills)}</strong>
              <span>{count_label}</span>
            </aside>
          </div>
          <p class="catalog-warning">{escape(warning)}</p>
        </div>
      </section>

      <section class="section">
        <div class="shell">
          <div class="section-header">
            <div><p class="kicker">SKILL INDEX</p><h2>{"Choose by outcome, not by memory." if en else "按结果选择，不必背名字。"}</h2></div>
            <p>{"Each detail page explains capability, delivery shape, safety boundary, install path, and public evidence." if en else "每个详情页都说明能力、交付形式、安全边界、安装入口与公开证据。"}</p>
          </div>
          <div class="catalog-toolbar">
            <input class="search-field" type="search" placeholder="{search}" aria-label="{search}" data-catalog-search />
            <span class="catalog-note">{escape(commit[:10])} · {escape(commit_date)}</span>
          </div>
          <div class="catalog-list">
{chr(10).join(cards)}
          </div>
          <p class="empty-state" hidden data-catalog-empty>{"No matching skill." if en else "没有匹配的 Skill，可以换一个任务关键词。"}</p>
        </div>
      </section>

      <section class="section section--compact">
        <div class="shell cta-panel">
          <div><p class="kicker">SOURCE BEFORE CLAIMS</p><h2>{"Read the public instructions before you install." if en else "先看公开指令与边界，再决定安装。"}</h2></div>
          <div class="hero-actions">
            <a class="button button--orange" href="https://github.com/soia-team/{domain.repo}" target="_blank" rel="noreferrer">{"Open source repository" if en else "查看公开仓"} ↗</a>
            <a class="button button--ghost" href="{services_path}">{"Need a proprietary workflow?" if en else "需要专有流程？"}</a>
          </div>
        </div>
      </section>"""
    return document(
        locale,
        "open",
        f"{title} | SOIA Open",
        summary,
        domain_path(locale, domain),
        main,
    )


def install_commands(skill: Skill) -> tuple[str, str, str]:
    plugin = skill.domain.plugin
    claude = (
        "claude plugin marketplace add soia-team/soia-open-skills && "
        f"claude plugin install {plugin}@soia"
    )
    codex = (
        "codex plugin marketplace add soia-team/soia-open-skills && "
        f"codex plugin add {plugin}@soia"
    )
    single = (
        f"npx skills add soia-team/{skill.domain.repo} -g -a '*' "
        f"-s {skill.name} -y"
    )
    return claude, codex, single


def render_skill(
    locale: str,
    skill: Skill,
    commit: str,
    commit_date: str,
) -> str:
    en = locale == "en"
    domain_title = skill.domain.title_en if en else skill.domain.title_zh
    summary = skill.summary_en if en else skill.summary_zh
    claude, codex, single = install_commands(skill)
    docs_url = (
        "https://github.com/soia-team/soia-open-skills/blob/main/docs/skills/"
        f"{skill.name}.md"
    )
    source_url = (
        f"https://github.com/soia-team/{skill.domain.repo}/tree/main/skills/{skill.name}"
    )
    if en:
        sections = f"""            <section>
              <p class="kicker">WHAT IT DOES</p>
              <h2>A focused capability with a visible boundary.</h2>
              <p>{escape(summary)}</p>
              <ul class="detail-list">
                <li>Starts from a natural-language outcome and the minimum required input.</li>
                <li>Loads the canonical public instructions only when the intent matches.</li>
                <li>Reports artifacts, checks, blockers, and any decision still owned by the user.</li>
              </ul>
            </section>
            <section>
              <p class="kicker">DELIVERY CONTRACT</p>
              <h2>What you should expect to receive.</h2>
              <div class="grid-3">
                <article class="card"><span class="card-index">INPUT</span><h3>Clear starting material</h3><p>A file, URL, repository, workspace, or goal that you are authorized to use.</p></article>
                <article class="card"><span class="card-index">PROCESS</span><h3>Bounded execution</h3><p>The smallest reliable steps, with previews and approval gates where risk increases.</p></article>
                <article class="card"><span class="card-index">RECEIPT</span><h3>Reviewable outcome</h3><p>Changed files, generated artifacts, validation results, limitations, and next actions.</p></article>
              </div>
            </section>
            <section>
              <p class="kicker">INSTALL</p>
              <h2>Install the domain or this one Skill.</h2>
              <h3>Claude Code domain plugin</h3><pre class="code-block">{escape(claude)}</pre>
              <h3>Codex domain plugin</h3><pre class="code-block">{escape(codex)}</pre>
              <h3>Individual Skill</h3><pre class="code-block">{escape(single)}</pre>
              <p>For WorkBuddy, ask the agent to install the matching domain Expert and verify it after the desktop client restarts.</p>
            </section>
            <section>
              <p class="kicker">SAFETY & EVIDENCE</p>
              <h2>Instructions are public. Your data is not.</h2>
              <p>Keep passwords, tokens, cookies, customer files, and restricted business material out of public issues and repositories. High-risk writes, deletion, publishing, payment, or permission changes require explicit authorization.</p>
            </section>"""
    else:
        sections = f"""            <section>
              <p class="kicker">这个 Skill 能做什么</p>
              <h2>一个职责聚焦、边界可见的能力。</h2>
              <p>{escape(summary)}</p>
              <ul class="detail-list">
                <li>从自然语言目标和最小必要输入开始，不要求先记住技能名。</li>
                <li>只有意图命中时才载入公开指令正文，避免把整个技能库塞进上下文。</li>
                <li>执行结束后汇总产物、检查、阻塞项，以及仍需用户决定的动作。</li>
              </ul>
            </section>
            <section>
              <p class="kicker">交付契约</p>
              <h2>你应该看到什么结果。</h2>
              <div class="grid-3">
                <article class="card"><span class="card-index">INPUT</span><h3>清楚的起点</h3><p>你有权使用的文件、URL、仓库、工作区或结果目标。</p></article>
                <article class="card"><span class="card-index">PROCESS</span><h3>受边界控制的执行</h3><p>先走最小可靠步骤；能预览就先预览，风险上升就保留人工确认。</p></article>
                <article class="card"><span class="card-index">RECEIPT</span><h3>可复核回执</h3><p>文件变化、生成产物、验证结果、已知限制和下一步。</p></article>
              </div>
            </section>
            <section>
              <p class="kicker">安装</p>
              <h2>可以安装整个领域，也可以只装这一个 Skill。</h2>
              <h3>Claude Code 领域插件</h3><pre class="code-block">{escape(claude)}</pre>
              <h3>Codex 领域插件</h3><pre class="code-block">{escape(codex)}</pre>
              <h3>单 Skill 安装</h3><pre class="code-block">{escape(single)}</pre>
              <p>WorkBuddy 可让 Agent 安装对应领域 Expert，重启桌面客户端后再做一次可见性与调用验证。</p>
            </section>
            <section>
              <p class="kicker">安全与证据</p>
              <h2>指令可以公开，你的数据不需要公开。</h2>
              <p>密码、Token、Cookie、客户文件和受限制业务资料不得进入公共 Issue 或仓库。删除、发布、付款、外部写入和权限变更等高风险动作必须获得明确授权。</p>
            </section>"""

    breadcrumb_label = "Breadcrumb" if en else "面包屑"
    main = f"""      <section class="skill-hero">
        <div class="shell">
          <nav class="breadcrumb" aria-label="{breadcrumb_label}">
            <a href="{route(locale)}">SOIA</a><span aria-hidden="true">/</span>
            <a href="{route(locale, "open/")}">Open</a><span aria-hidden="true">/</span>
            <a href="{domain_path(locale, skill.domain)}">{escape(domain_title)}</a><span aria-hidden="true">/</span>
            <span aria-current="page">{escape(skill.name)}</span>
          </nav>
          <div class="skill-hero-grid">
            <div>
              <p class="eyebrow">PUBLIC SKILL · {escape(skill.domain.plugin)}</p>
              <h1>{escape(skill.name)}</h1>
              <p class="page-lead">{escape(summary)}</p>
              <div class="route-map" aria-label="{"Page level" if en else "页面层级"}">
                <span>L1 · SOIA</span><span>L2 · Open</span><span>L3 · {escape(skill.domain.code)}</span><span>L4 · Skill</span>
              </div>
            </div>
            <aside class="skill-receipt">
              <div><span>{"Domain" if en else "领域"}</span><strong>{escape(skill.domain.plugin)}</strong></div>
              <div><span>{"Catalog status" if en else "目录状态"}</span><strong>{"Public documentation" if en else "已进入公开文档目录"}</strong></div>
              <div><span>{"Snapshot" if en else "快照"}</span><strong>{escape(commit[:10])} · {escape(commit_date)}</strong></div>
            </aside>
          </div>
        </div>
      </section>

      <section class="section">
        <div class="shell detail-layout">
          <div class="detail-prose">
{sections}
          </div>
          <aside class="side-panel">
            <p class="mono-label">PUBLIC EVIDENCE</p>
            <h2>{"Inspect before installing" if en else "安装前先审查"}</h2>
            <p>{"The catalog page is generated from public Skill documentation. Source instructions remain the authority." if en else "本站详情页由公开 Skill 文档生成；技能源码与公开指令始终是事实真源。"}</p>
            <a class="button button--ink" href="{docs_url}" target="_blank" rel="noreferrer">{"Read canonical docs" if en else "查看规范详情"} ↗</a>
            <a class="button button--ghost" href="{source_url}" target="_blank" rel="noreferrer">{"Inspect source" if en else "审查 Skill 源码"} ↗</a>
            <a class="button button--text" href="{domain_path(locale, skill.domain)}">← {"Back to domain" if en else "返回能力域"}</a>
          </aside>
        </div>
      </section>"""
    return document(
        locale,
        "open",
        f"{skill.title_en} — {skill.name} | SOIA Open" if en else f"{skill.name} | SOIA Open",
        summary,
        skill_path(locale, skill),
        main,
    )


def write_page(path: Path, html: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


# -- LEGACY TOP-LEVEL RENDERERS --
#
# Kept only as a compact reference for shared copy fragments. main() deliberately
# does not call these functions: top-level Chinese and English pages are curated.


def render_en_home() -> str:
    main = """      <section class="hero">
        <div class="shell hero-grid">
          <div>
            <p class="eyebrow">LOCAL-FIRST · OPEN SKILLS · HUMAN-CONTROLLED</p>
            <h1><span class="hero-title-line">Move AI into the</span><span class="hero-title-line"><em>workflow</em>, not just</span><span class="hero-title-line">the chat window.</span></h1>
            <p class="hero-copy">SOIA packages domain knowledge as reviewable Skills, multi-Skill workflows, installable plugins, and role-based Experts. Start with one repeated task and finish with an artifact you can run, inspect, and hand over.</p>
            <div class="hero-actions">
              <a class="button button--orange" href="/en/open/">Explore open capabilities</a>
              <a class="button button--ghost" href="/en/services/">Bring one workflow</a>
              <a class="button button--text" href="https://github.com/soia-team" target="_blank" rel="noreferrer">Inspect source on GitHub ↗</a>
            </div>
            <div class="proof-line"><span>8 public capability domains</span><span>Claude Code · Codex · WorkBuddy</span><span>Data stays local by default</span></div>
          </div>
          <aside class="evidence-card">
            <div class="evidence-head"><span>SOIA / WORKFLOW.RECEIPT</span><span class="evidence-state">VERIFIABLE</span></div>
            <div class="evidence-body"><h2>One workflow you can rerun</h2><p>Start from a real input. Finish with a reviewable output.</p><div class="receipt-list">
              <div class="receipt-row"><span>01</span><strong>Skill</strong><small>task + boundary</small></div>
              <div class="receipt-row"><span>02</span><strong>Workflow</strong><small>handoffs + failures</small></div>
              <div class="receipt-row"><span>03</span><strong>Plugin</strong><small>install + version</small></div>
              <div class="receipt-row"><span>04</span><strong>Expert</strong><small>role + acceptance</small></div>
            </div></div>
            <div class="evidence-foot"><span>INPUT · real work</span><span>OUTPUT · artifact + receipt</span></div>
          </aside>
        </div>
      </section>
      <section class="section"><div class="shell">
        <div class="section-header"><div><p class="kicker">WHY SOIA</p><h2>Answering a question is not the same as finishing a job.</h2></div><p>When context, steps, tools, and acceptance criteria live only in chat history, every run starts from zero. SOIA turns that hidden know-how into a reusable work asset.</p></div>
        <div class="grid-3">
          <article class="card problem-card"><strong>01 / CONTEXT</strong><h3>Stop repeating the background</h3><p>Keep relevant rules, sources, and constraints attached to the capability.</p></article>
          <article class="card problem-card"><strong>02 / DELIVERY</strong><h3>Make outcomes reviewable</h3><p>Define artifacts, checks, approval gates, and failure handling.</p></article>
          <article class="card problem-card"><strong>03 / PORTABILITY</strong><h3>Keep the method portable</h3><p>Separate the capability from a one-off prompt or a single host.</p></article>
        </div>
      </div></section>
      <section class="section"><div class="shell">
        <div class="section-header"><div><p class="kicker">CAPABILITY MODEL</p><h2>From one task to a governed work system.</h2></div><p>Each layer has one job. Public status labels show what is available today and what remains a preview.</p></div>
        <div class="layer-flow">
          <article class="card layer-card"><span class="layer-number">01 / SKILL</span><h3>Package one task</h3><p>Define inputs, outputs, steps, boundaries, and acceptance.</p><ul><li>Reviewable source</li><li>Focused responsibility</li><li>Independent validation</li></ul></article><div class="flow-arrow">→</div>
          <article class="card layer-card"><span class="layer-number">02 / WORKFLOW</span><h3>Connect capabilities</h3><p>Define order, handoffs, approval gates, and recovery.</p><ul><li>Outcome-oriented</li><li>Human-controlled</li><li>Replayable process</li></ul></article><div class="flow-arrow">→</div>
          <article class="card layer-card"><span class="layer-number">03 / EXPERT</span><h3>Enter a real role</h3><p>Combine a role, selected Skills, tools, references, and acceptance rules.</p><ul><li>Role-based entry</li><li>Domain context</li><li>Visible boundaries</li></ul></article>
        </div>
      </div></section>
      <section class="section section--compact"><div class="shell cta-panel"><div><p class="kicker">START WITH ONE OUTCOME</p><h2>Pick a repeated task. Build the smallest workflow that can prove itself.</h2></div><div class="hero-actions"><a class="button button--orange" href="/en/open/">Browse Open</a><a class="button button--ghost" href="/en/course/">Build it yourself</a></div></div></section>"""
    return document(
        "en", "home", "SOIA | AI workflows for real-world delivery",
        "SOIA turns domain knowledge into open Skills, workflows, plugins, and role-based Experts for Claude Code, Codex, and WorkBuddy.",
        "/en/", main,
    )


def render_en_open(domains: dict[str, list[Skill]]) -> str:
    cards = "\n".join(
        domain_card("en", DOMAINS[key], len(domains[key])) for key in DOMAINS
    )
    main = f"""      <section class="page-hero"><div class="shell">
        <p class="eyebrow">SOIA OPEN</p><h1>Eight public domains.<br /><em>One reviewable entry point.</em></h1>
        <p class="page-lead">Go from a focused Skill to a domain plugin and a role-based WorkBuddy Expert without hiding the public source behind a black box.</p>
        <div class="hero-actions"><a class="button button--orange" href="#domains">Explore 8 domains</a><a class="button button--ghost" href="https://github.com/soia-team/soia-open-skills" target="_blank" rel="noreferrer">Open ecosystem portal ↗</a></div>
        <div class="page-meta"><span>79 documented catalog entries</span><span>8 capability domains</span><span>3 host environments</span><span>MIT licensed</span></div>
        <p class="catalog-warning">Catalog documentation can lead marketplace releases during a rollout. Verify the current install manifest before relying on an exact count.</p>
      </div></section>
      <section class="section" id="domains"><div class="shell">
        <div class="section-header"><div><p class="kicker">PUBLIC DOMAINS</p><h2>Install by work domain.<br />Choose by outcome.</h2></div><p>Level 3 pages explain each domain. Level 4 pages document every cataloged Skill with install paths and public evidence.</p></div>
        <div class="catalog-toolbar"><input class="search-field" type="search" placeholder="Search vault, development, content, environment…" aria-label="Search public domains" data-catalog-search /><span class="catalog-note">Public catalog snapshot</span></div>
        <div class="plugin-grid">{cards}</div>
        <p class="empty-state" hidden data-catalog-empty>No matching domain.</p>
      </div></section>
      <section class="section"><div class="shell">
        <div class="section-header"><div><p class="kicker">SKILL → PLUGIN → EXPERT</p><h2>One source, three loading layers.</h2></div><p>The layer adds packaging and role context. It does not erase where the capability came from.</p></div>
        <div class="layer-flow">
          <article class="card layer-card"><span class="layer-number">01 / SKILL</span><span class="status status--available">Available</span><h3>Focused task</h3><p>A public instruction bundle with triggers, steps, limits, and outputs.</p></article><span class="flow-arrow">→</span>
          <article class="card layer-card"><span class="layer-number">02 / PLUGIN</span><span class="status status--available">Available</span><h3>Domain install</h3><p>Version and enable a coherent group of Skills for Claude Code or Codex.</p></article><span class="flow-arrow">→</span>
          <article class="card layer-card"><span class="layer-number">03 / EXPERT</span><span class="status status--preview">Public beta</span><h3>Role-based entry</h3><p>Organize the domain for WorkBuddy as a role that is summoned only when needed.</p></article>
        </div>
      </div></section>"""
    return document(
        "en", "open", "SOIA Open | Public Agent Skills",
        "Explore SOIA's eight public capability domains and per-Skill details for Claude Code, Codex, and WorkBuddy.",
        "/en/open/", main,
    )


def render_en_products() -> str:
    rows = [
        ("01 / SKILL", "Available", "Single Skill", "One bounded task with explicit inputs, outputs, steps, safety limits, and acceptance.", "/en/open/"),
        ("02 / WORKFLOW", "Service", "Multi-Skill workflow", "A result-oriented chain with handoffs, approval gates, and failure recovery.", "/en/services/"),
        ("03 / PLUGIN", "Available", "Domain plugin", "A versioned capability package for Claude Code and Codex.", "/en/open/"),
        ("04 / EXPERT", "Preview", "WorkBuddy Expert", "A role-based entry that assembles selected Skills, tools, references, and recommended tasks.", "/en/open/"),
        ("05 / RUNTIME", "Developer preview", "SOIA Agent Runtime", "A local-first, provider-neutral CLI and desktop runtime under active development.", "https://github.com/soia-team/soia"),
    ]
    product_rows = []
    for label, status, title, desc, href in rows:
        external = ' target="_blank" rel="noreferrer"' if href.startswith("http") else ""
        product_rows.append(
            f"""          <article class="product-row"><div><span class="product-index">{label}</span><div class="page-meta"><span class="status status--preview">{status}</span></div></div><div><h2>{title}</h2><p>{desc}</p></div><div class="product-meta"><div><span>Core promise</span><strong>Reviewable scope</strong></div><div><span>Control</span><strong>Human approval at risk boundaries</strong></div></div><div class="product-action"><a class="button button--ghost" href="{href}"{external}>Explore →</a></div></article>"""
        )
    main = f"""      <section class="page-hero"><div class="shell"><p class="eyebrow">SOIA PRODUCTS</p><h1>Package capability at the<br /><em>smallest useful layer.</em></h1><p class="page-lead">Start with one Skill. Add workflow, plugin, Expert, or runtime only when the delivery needs it.</p><div class="hero-actions"><a class="button button--orange" href="/en/open/">Browse public capabilities</a><a class="button button--ghost" href="/en/services/">Discuss a workflow</a></div></div></section>
      <section class="section"><div class="shell"><div class="section-header"><div><p class="kicker">PRODUCT LADDER</p><h2>Five layers, one source trail.</h2></div><p>Status and evidence matter more than feature volume. Preview capabilities are labeled as previews.</p></div><div class="product-stack">{''.join(product_rows)}</div></div></section>
      <section class="section section--compact"><div class="shell cta-panel"><div><p class="kicker">CHOOSE BY OUTCOME</p><h2>Unsure which layer you need? Start with the repeated task.</h2></div><div class="hero-actions"><a class="button button--orange" href="/en/services/">Bring one workflow</a><a class="button button--ghost" href="/en/course/">Learn the method</a></div></div></section>"""
    return document(
        "en", "products",
        "SOIA Products | Skills, workflows, plugins, and Experts",
        "Understand the SOIA product ladder from a focused Skill to workflows, domain plugins, WorkBuddy Experts, and the developer-preview runtime.",
        "/en/products/", main,
    )


def render_en_course() -> str:
    modules = [
        ("00 · Choose the workflow", "Score frequency, value, risk, and acceptance; define what not to automate.", "Pilot Brief"),
        ("01 · Skill fundamentals", "Write triggers, inputs, outputs, steps, tools, limits, and acceptance.", "Skill package"),
        ("02 · Multi-Skill workflow", "Model responsibilities, dependencies, handoffs, approval gates, and failure handling.", "Workflow Map"),
        ("03 · Claude / Codex plugins", "Package one domain with manifests, install, enablement, and versioning.", "Installable plugin"),
        ("04 · WorkBuddy Expert", "Choose an Agent or Team structure and assemble Skills, references, scripts, and tasks.", "Expert package"),
        ("05 · Protected delivery", "Separate public method from proprietary material, credentials, and access control.", "Delivery boundary"),
        ("06 · Test and maintain", "Create acceptance examples, regression checks, versioning, rollback, and handoff.", "Maintenance checklist"),
        ("07 · Capstone run", "Run one real input end to end and present artifacts, limits, and human decisions.", "Demonstrable delivery"),
    ]
    rows = "".join(
        f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in modules
    )
    main = f"""      <section class="page-hero"><div class="shell"><p class="eyebrow">COURSE · APPLICATION-ONLY PREVIEW</p><h1>Stop collecting AI tips.<br /><em>Build one working workflow.</em></h1><p class="page-lead">Bring one real SOP and leave with a Skill, a multi-Skill workflow, an installable plugin, a WorkBuddy Expert, and an acceptance-and-maintenance package. The first cohort is being prepared; dates and pricing are not yet published.</p><div class="hero-actions"><a class="button button--orange" data-course-link href="https://github.com/soia-team/soia-open-skills/issues/new" target="_blank" rel="noreferrer">Apply for the pilot cohort ↗</a><a class="button button--ghost" href="/en/open/">Inspect open Skills first</a></div></div></section>
      <section class="section section--compact"><div class="shell course-outcome"><div><p class="kicker">COURSE OUTCOME</p><h2 class="section-title">Completion means<br />running the workflow.</h2><p class="section-intro">Every module leaves a reviewable artifact that becomes part of the capstone delivery.</p></div><aside class="deliverable-panel"><h3>You will take away</h3><ul class="detail-list"><li>1 Skill built around a real task</li><li>1 workflow with human checkpoints</li><li>1 Claude Code / Codex plugin</li><li>1 WorkBuddy Agent or Team Expert</li><li>1 test, version, update, and handoff checklist</li></ul></aside></div></section>
      <section class="section"><div class="shell"><div class="section-header"><div><p class="kicker">CURRICULUM</p><h2>Eight modules along<br />one delivery path.</h2></div><p>Choose the right problem first. Package and validate only what the real workflow needs.</p></div><table class="course-table"><thead><tr><th>Module</th><th>Practice</th><th>Artifact</th></tr></thead><tbody>{rows}</tbody></table></div></section>
      <section class="section section--compact"><div class="shell"><div class="section-header"><div><p class="kicker">FIT & BOUNDARIES</p><h2>Project-based, not a promise of business results.</h2></div><p>The course does not provide third-party accounts, API credits, done-for-you development, or guarantees of traffic, revenue, or employment.</p></div><div class="grid-3"><article class="card"><h3>Bring a repeated task</h3><p>Prefer something that happens weekly and has a describable input and output.</p></article><article class="card"><h3>Use authorized material</h3><p>Bring only SOPs, templates, and examples you own or have permission to use.</p></article><article class="card"><h3>Define one acceptance example</h3><p>Know what completion looks like and where a human must decide.</p></article></div></div></section>"""
    return document(
        "en", "course", "SOIA Agent Workflow Course | Pilot cohort",
        "Build and validate a real Agent workflow from a Skill through plugin and WorkBuddy Expert delivery in an application-only pilot cohort.",
        "/en/course/", main,
    )


def render_en_services() -> str:
    services = [
        ("01", "Workflow assessment", "Clarify the outcome, inputs, risks, approvals, and whether the task is suitable for Agent-assisted delivery."),
        ("02", "Skill and workflow delivery", "Package an authorized process into focused Skills and an acceptance-ready multi-Skill workflow."),
        ("03", "Plugin and Expert packaging", "Deliver the approved capability through Claude Code, Codex, or a WorkBuddy Agent / Team entry."),
        ("04", "Installation and handoff", "Verify the chosen host, run a real example, and leave version, rollback, and maintenance instructions."),
    ]
    cards = "".join(
        f"""<article class="service-card"><span>{number}</span><div><h2>{title}</h2><p>{desc}</p></div><div class="product-meta"><div><span>Starts with</span><strong>One bounded workflow</strong></div><div><span>Ends with</span><strong>Artifacts + checks + handoff</strong></div></div></article>"""
        for number, title, desc in services
    )
    main = f"""      <section class="page-hero"><div class="shell"><p class="eyebrow">SOIA SERVICES</p><h1>From process knowledge<br /><em>to a working delivery.</em></h1><p class="page-lead">Bring a workflow you are authorized to use. We clarify its boundary, package the capability, install it in one primary host, run a real acceptance example, and hand over the evidence.</p><div class="hero-actions"><a class="button button--orange" data-request-link href="https://github.com/soia-team/soia-open-skills/issues/new" target="_blank" rel="noreferrer">Submit a non-sensitive brief ↗</a><a class="button button--ghost" href="/en/course/">Prefer to build it yourself?</a></div></div></section>
      <section class="section"><div class="shell"><div class="section-header"><div><p class="kicker">SERVICE PATH</p><h2>Four steps from scope<br />to handoff.</h2></div><p>Scope, schedule, and fees are confirmed only after the workflow and acceptance criteria are clear.</p></div><div class="service-list">{cards}</div></div></section>
      <section class="section section--compact"><div class="shell"><div class="section-header"><div><p class="kicker">BOUNDARIES</p><h2>What the service will not do.</h2></div><p>We deliver the agreed workflow and evidence. We do not promise uncontrollable business outcomes.</p></div><div class="grid-4"><article class="card problem-card"><strong>NO SECRETS</strong><h3>No credentials in public channels</h3><p>Passwords, tokens, cookies, and sessions stay in official user-controlled flows.</p></article><article class="card problem-card"><strong>NO BLIND AUTO</strong><h3>No bypassing approval</h3><p>Deletion, payment, publishing, and permission changes retain a human gate.</p></article><article class="card problem-card"><strong>NO FALSE PROMISE</strong><h3>No revenue or traffic guarantee</h3><p>We can improve a workflow, not guarantee the market outcome.</p></article><article class="card problem-card"><strong>NO DATA MIXING</strong><h3>No proprietary material in public repos</h3><p>Reusable method and client-owned material stay separated.</p></article></div></div></section>"""
    return document(
        "en", "services", "SOIA Services | Workflow and Expert delivery",
        "Assess, package, install, validate, and hand over protected Agent workflows for Claude Code, Codex, or WorkBuddy.",
        "/en/services/", main,
    )


def render_en_about() -> str:
    main = """      <section class="page-hero"><div class="shell"><p class="eyebrow">ABOUT SOIA</p><h1>AI creates value when it<br /><em>reliably finishes work.</em></h1><p class="page-lead">SOIA organizes task rules, domain knowledge, tool use, and acceptance criteria into work systems that can be installed, run, reviewed, and maintained.</p><div class="hero-actions"><a class="button button--orange" href="/en/open/">Start with Open</a><a class="button button--ghost" href="https://github.com/soia-team" target="_blank" rel="noreferrer">Inspect the GitHub organization ↗</a></div></div></section>
      <section class="section section--compact"><div class="shell"><p class="kicker">THE NAME</p><h2 class="section-title">SOIA stands for four commitments.</h2><div class="about-definition"><div><strong>S</strong><span><b>System</b><br />Facts, rules, and state have a durable home.</span></div><div><strong>O</strong><span><b>Orchestration</b><br />Roles, Skills, and tools work together.</span></div><div><strong>I</strong><span><b>Intelligence</b><br />AI assists understanding, generation, and judgment.</span></div><div><strong>A</strong><span><b>Assurance</b><br />Boundaries, approval, and evidence protect outcomes.</span></div></div></div></section>
      <section class="section"><div class="shell"><div class="section-header"><div><p class="kicker">OUR PRINCIPLES</p><h2>Four rules shape every surface.</h2></div><p>When speed conflicts with authorization, data boundaries, or verifiability, the boundary wins.</p></div><div class="grid-4 principle-grid"><article class="card"><span class="card-index">LOCAL-FIRST</span><h3>Keep data where it belongs</h3><p>Using an Agent should not require moving every file into a new center.</p></article><article class="card"><span class="card-index">PROVIDER-NEUTRAL</span><h3>Separate capability from model</h3><p>Keep the core method portable across hosts and providers where practical.</p></article><article class="card"><span class="card-index">HUMAN-CONTROLLED</span><h3>People own high-risk decisions</h3><p>Publishing, deletion, payment, and access changes require explicit approval.</p></article><article class="card"><span class="card-index">EVIDENCE-BACKED</span><h3>Let artifacts prove status</h3><p>Source, tests, receipts, and versions carry more weight than capability slogans.</p></article></div></div></section>
      <section class="section"><div class="shell"><div class="section-header"><div><p class="kicker">OPEN / PROPRIETARY</p><h2>Open the reusable method.<br />Protect owned workflows.</h2></div><p>Openness does not require users to publish their data. Shared capability and proprietary context remain separate.</p></div><div class="boundary-grid"><article class="is-open"><p class="mono-label">OPEN BY DEFAULT</p><h3>Reusable capability</h3><ul class="detail-list"><li>General-purpose Skills and methods</li><li>Public plugin manifests and versions</li><li>Templates without client facts</li><li>Public status, releases, and security channels</li></ul></article><article class="is-private"><p class="mono-label">PROTECTED BY DESIGN</p><h3>Owned context</h3><ul class="detail-list"><li>Client files and internal SOPs</li><li>Passwords, tokens, cookies, and sessions</li><li>Unreleased code and business data</li><li>Restricted templates and decisions</li></ul></article></div></div></section>"""
    return document(
        "en", "about", "About SOIA | Governed AI work systems",
        "Learn how SOIA combines local-first operation, provider-neutral capabilities, human control, and evidence-backed delivery.",
        "/en/about/", main,
    )


def write_sitemap(paths: list[str], lastmod: str) -> None:
    entries = []
    for path in sorted(set(paths), key=lambda item: (item.count("/"), item)):
        priority = "1.0" if path == "/" else "0.9" if path in {"/open/", "/en/", "/en/open/"} else "0.7"
        change = "weekly" if "/open/" in path or path in {"/", "/en/"} else "monthly"
        entries.append(
            f"""  <url>
    <loc>{BASE_URL}{path}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>{change}</changefreq>
    <priority>{priority}</priority>
  </url>"""
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )
    (ROOT / "sitemap.xml").write_text(xml, encoding="utf-8")


# -- MAIN --


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    args = parser.parse_args()
    source_root = args.source_root.expanduser().resolve()
    skills = parse_catalog(source_root)
    commit, commit_date = source_commit(source_root)

    by_domain = {plugin: [] for plugin in DOMAINS}
    for skill in skills:
        by_domain[skill.domain.plugin].append(skill)

    # Top-level pages are curated editorial surfaces. A catalog refresh must
    # not overwrite either the Chinese or English narrative.
    generated_paths = [
        "/", "/open/", "/products/", "/course/", "/services/", "/about/",
        "/en/", "/en/open/", "/en/products/", "/en/course/", "/en/services/", "/en/about/",
    ]
    for public_path in generated_paths:
        page = ROOT / public_path.lstrip("/") / "index.html"
        if public_path == "/":
            page = ROOT / "index.html"
        if not page.exists():
            raise SystemExit(f"missing curated top-level page: {page}")

    for plugin, domain in DOMAINS.items():
        domain_skills = by_domain[plugin]
        for locale in ("zh", "en"):
            path = domain_path(locale, domain)
            write_page(
                ROOT / path.lstrip("/") / "index.html",
                render_domain(locale, domain, domain_skills, commit, commit_date),
            )
            generated_paths.append(path)
        for skill in domain_skills:
            for locale in ("zh", "en"):
                path = skill_path(locale, skill)
                write_page(
                    ROOT / path.lstrip("/") / "index.html",
                    render_skill(locale, skill, commit, commit_date),
                )
                generated_paths.append(path)

    write_sitemap(generated_paths, max(commit_date, date.today().isoformat()))
    print(
        f"generated {len(skills)} bilingual Skill pages, "
        f"{len(DOMAINS)} bilingual domain pages "
        f"from {commit[:12]}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
