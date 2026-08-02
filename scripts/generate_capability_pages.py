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


@dataclass(frozen=True)
class Expert:
    plugin: str
    profession_zh: str
    profession_en: str
    description_zh: str
    description_en: str
    prompts_zh: tuple[str, str, str]
    prompts_en: tuple[str, str, str]


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


EXPERTS = OrderedDict(
    (item.plugin, item)
    for item in [
        Expert(
            "soia-pkm-vault", "Soia · 知识库管家", "Soia · Knowledge Vault Curator",
            "把网页、公众号与云盘资料收进本地知识库，按元数据与主题双链整理，再转换成解读、演示稿与长图。",
            "Archives web, WeChat, and cloud-drive material into a local vault, organizes it, then turns it into interpretations, decks, and long-form visuals.",
            ("把这些分散资料收进本地 Markdown 知识库。", "归档这篇文章，再判断是否值得细读。", "把这篇文章转换成演示稿和长图。"),
            ("Bring these scattered sources into a local Markdown vault.", "Archive this article, then assess whether it merits a close read.", "Turn this article into a deck and a long-form visual."),
        ),
        Expert(
            "soia-env", "Soia · 环境安装工程师", "Soia · Environment Engineer",
            "面向新手安装并验证 Node、Python 与常用 AI CLI，只读诊断网络故障，并只在授权后清理空间。",
            "Installs and verifies Node, Python, and common AI CLIs, diagnoses network failures read-only, and reclaims space only when authorized.",
            ("帮我规划并验证一套新的 AI 开发环境。", "判断安装超时来自 DNS、代理还是证书。", "检查哪些 AI CLI 需要升级，我批准后再执行。"),
            ("Plan and verify a new AI development environment.", "Determine whether install timeouts come from DNS, proxy, or certificates.", "Check which AI CLIs need updates, then wait for my approval."),
        ),
        Expert(
            "soia-dev", "Soia · 研发工程师", "Soia · Software Engineer",
            "按工程契约改代码：先划边界再动手，改完验证，并配对抗复核、修复闭环、测试设计与发版清单。",
            "Works to an engineering contract: scope first, verify after, with adversarial review, fix loops, test design, and release checklists.",
            ("按有边界、有验证、有复核的流程完成这个改动。", "从多个对抗角度复核这个 diff。", "把需求转成测试计划与验收清单。"),
            ("Complete this change with explicit scope, validation, and review.", "Review this diff from several adversarial angles.", "Turn this requirement into a test plan and acceptance checklist."),
        ),
        Expert(
            "soia-media-content", "Soia · 新媒体运营", "Soia · New Media Operator",
            "把你的观点写成成文草稿并配图，再适配公众号、小红书与 X；只创建草稿，不自动发布。",
            "Turns your viewpoint into a complete draft with imagery, then adapts it for WeChat, Rednote, and X without auto-publishing.",
            ("把这个观点写成文章并适配多个平台，只建草稿。", "把这篇文章改成小红书笔记并配标签。", "为文章生成封面图和小结卡片。"),
            ("Turn this viewpoint into an article and platform drafts only.", "Adapt this article into a Rednote post with tags.", "Generate a cover and recap cards for this article."),
        ),
        Expert(
            "soia-dev-design", "Soia · 产品设计与文档", "Soia · Product Design & Docs",
            "从一句话需求形成 PRD、高保真原型与架构图，并能在安全边界内处理 Office 文档。",
            "Takes a one-line need to a PRD, high-fidelity prototype, and architecture diagrams, with bounded Office document operations.",
            ("把这句话需求做成有验收标准的 PRD 和原型。", "为这个系统画架构图和时序图。", "把 Visio 文件迁移为可编辑的 draw.io 图。"),
            ("Turn this one-line need into a PRD and prototype with acceptance criteria.", "Draw architecture and sequence diagrams for this system.", "Migrate these Visio files into editable draw.io diagrams."),
        ),
        Expert(
            "soia-meta", "Soia · 技能生态管家", "Soia · Skill Ecosystem Manager",
            "按需求检索全生态技能并载入，同步到用户选择的 AI 工具，执行发布收尾，并起草或诊断提示词。",
            "Finds and loads the right capability, syncs it into selected AI tools, closes releases, and drafts or diagnoses prompts.",
            ("我说需求，你帮我找到并载入合适的 Skill。", "把这些 Skills 同步到我使用的 AI 工具。", "改动合并后完成发布并更新客户端。"),
            ("Find and load the right Skill from my description.", "Sync these Skills into the AI tools I use.", "Close the release after merge and update my clients."),
        ),
        Expert(
            "soia-cwork-office", "Soia · 办公资料助手", "Soia · Workplace Docs Aide",
            "以最小权限只读调研飞书知识库与云文档，同步为本地 Markdown，并按授权导出归档图表。",
            "Researches Feishu read-only with least privilege, syncs knowledge bases to local Markdown, and exports diagrams when authorized.",
            ("只读调研飞书和 ProcessOn，并同步可复核副本。", "把飞书知识库同步成本地 Markdown。", "盘点 ProcessOn 图表，导出我批准的项目。"),
            ("Research Feishu and ProcessOn read-only and create a reviewable copy.", "Sync this Feishu knowledge base into local Markdown.", "Inventory ProcessOn diagrams and export only approved items."),
        ),
        Expert(
            "soia-edu-course", "Soia · 课程设计师", "Soia · Course Designer",
            "根据主题、受众和课时约束设计课程大纲与目标，再形成可执行教案、讲义结构与课堂活动。",
            "Designs course outlines and objectives from topic, audience, and hours, then builds executable lesson plans and activities.",
            ("根据受众和课时先设计课程大纲与目标。", "把大纲写成带课堂活动的可执行教案。", "为这节课起草讲义结构。"),
            ("Design the course outline and objectives from audience and hours.", "Turn the outline into an executable lesson plan with activities.", "Draft the handout structure for this lesson."),
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
    trigger_zh: str = ""

    @property
    def title_en(self) -> str:
        parts = self.name.split("-")[2:]
        return " ".join(TOKEN_LABELS.get(part, part.capitalize()) for part in parts)

    @property
    def summary_en(self) -> str:
        return FEATURED_EN.get(
            self.name,
            f"Public capability for {self.title_en.lower()}, with documented inputs, outputs, and safety boundaries.",
        )


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
            name = row.group("name")
            trigger = ""
            detail = source_root / "docs" / "skills" / f"{name}.md"
            if detail.exists():
                for detail_line in detail.read_text(encoding="utf-8").splitlines():
                    candidate = detail_line.strip()
                    if candidate.startswith("「") and candidate.endswith("」"):
                        trigger = candidate
                        break
            skills.append(Skill(name, row.group("summary").strip(), current, trigger))
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
    <link rel="stylesheet" href="/assets/styles.css?v=levels3-20260802" />
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
    <script src="/assets/site.js?v=levels3-20260802" defer></script>
  </body>
</html>
"""


def domain_path(locale: str, domain: Domain) -> str:
    return route(locale, f"open/{domain.slug}/")


def skill_path(locale: str, skill: Skill) -> str:
    return route(locale, f"open/{skill.domain.slug}/{skill.name}/")


def expert_path(locale: str, expert: Expert) -> str:
    domain = DOMAINS[expert.plugin]
    return route(locale, f"open/experts/{domain.slug}/")


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
    expert = EXPERTS[domain.plugin]
    rows = []
    for index, skill in enumerate(skills, start=1):
        skill_summary = skill.summary_en if en else skill.summary_zh
        rows.append(
            f"""              <li class="catalog-row" data-catalog-card>
                <a href="{skill_path(locale, skill)}">
                  <span class="catalog-row-index">{index:03d}</span>
                  <span class="catalog-row-thumb" aria-hidden="true">{escape(domain.code)}</span>
                  <span class="catalog-row-body"><strong>{escape(skill.name)}</strong><span>{escape(skill_summary)}</span></span>
                  <span class="catalog-row-meta"><i>{"Skill" if en else "公开 Skill"}</i><i>{escape(domain.code)}</i></span>
                  <span class="catalog-row-arrow" aria-hidden="true">→</span>
                </a>
              </li>"""
        )
    open_path = route(locale, "open/")
    breadcrumb_label = "Breadcrumb" if en else "面包屑"
    back = "Open ecosystem" if en else "开放生态"
    search = "Search skills in this domain…" if en else "搜索这个能力域里的 Skills……"
    profession = expert.profession_en if en else expert.profession_zh
    expert_description = expert.description_en if en else expert.description_zh
    main = f"""      <div class="catalog-level-page capability-domain-page">
        <section class="catalog-page-hero">
          <div class="catalog-page-narrow">
            <nav class="catalog-breadcrumb" aria-label="{breadcrumb_label}">
              <a href="{open_path}">{back}</a><span aria-hidden="true">·</span><span aria-current="page">{escape(title)}</span>
            </nav>
            <p class="catalog-page-label">{escape(domain.code)} · {escape(domain.plugin)}</p>
            <h1>{escape(title)}<span>.</span></h1>
            <p class="catalog-page-lead">{escape(summary)}</p>
            <div class="catalog-page-actions">
              <a class="button button--ink" href="#skills">{"Browse Skills" if en else "浏览 Skills"} →</a>
              <a class="button button--ghost" href="https://github.com/soia-team/{domain.repo}" target="_blank" rel="noreferrer">GitHub ↗</a>
            </div>
          </div>
        </section>
        <section class="catalog-page-meta"><div class="catalog-page-wide">
          <dl><div><dt>{"Type" if en else "类型"}</dt><dd>{"Public domain" if en else "公开能力域"}</dd></div><div><dt>Skills</dt><dd>{len(skills)}</dd></div><div><dt>Expert</dt><dd>{escape(profession)}</dd></div><div><dt>{"Snapshot" if en else "目录快照"}</dt><dd>{escape(commit[:10])} · {escape(commit_date)}</dd></div></dl>
        </div></section>
        <section class="catalog-list-section" id="skills"><div class="catalog-page-wide" data-catalog>
          <header class="catalog-list-head"><div><p class="catalog-page-label">SKILL CATALOG</p><h2>{"Choose by outcome." if en else "按结果选择。"}</h2></div><p>{"Every row opens a dedicated page with purpose, installation, boundaries, and public evidence." if en else "每一行都进入独立详情页，说明用途、安装方式、边界与公开证据。"}</p></header>
          <label class="catalog-search"><span class="sr-only">{search}</span><input type="search" placeholder="{search}" aria-label="{search}" data-catalog-search /></label>
          <ol class="catalog-row-list">
{chr(10).join(rows)}
          </ol>
          <p class="empty-state" hidden data-catalog-empty>{"No matching Skill. Try a task keyword instead." if en else "没有匹配的 Skill，可以换一个任务关键词。"}</p>
        </div></section>
        <section class="domain-expert-section"><div class="catalog-page-wide">
          <a class="domain-expert-card" href="{expert_path(locale, expert)}">
            <span class="domain-expert-code">EXPERT · {escape(domain.code)}</span>
            <span><strong>{escape(profession)}</strong><small>{escape(expert_description)}</small></span>
            <span aria-hidden="true">→</span>
          </a>
        </div></section>
      </div>"""
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
    trigger = (
        f'“Use {skill.title_en} for this task.”'
        if en
        else (skill.trigger_zh or f'「请使用 {skill.name} 完成这个任务。」')
    )
    claude, codex, single = install_commands(skill)
    docs_url = (
        "https://github.com/soia-team/soia-open-skills/blob/main/docs/skills/"
        f"{skill.name}.md"
    )
    source_url = (
        f"https://github.com/soia-team/{skill.domain.repo}/tree/main/skills/{skill.name}"
    )
    breadcrumb_label = "Breadcrumb" if en else "面包屑"
    main = f"""      <article class="capability-detail-page capability-detail-page--skill">
        <header class="capability-detail-head">
          <nav class="catalog-breadcrumb" aria-label="{breadcrumb_label}"><a href="{route(locale, 'open/')}">{"Open ecosystem" if en else "开放生态"}</a><span aria-hidden="true">·</span><a href="{domain_path(locale, skill.domain)}">{escape(domain_title)}</a><span aria-hidden="true">·</span><span aria-current="page">Skill</span></nav>
          <p class="catalog-page-label">PUBLIC SKILL · {escape(skill.domain.code)}</p>
          <h1>{escape(skill.name)}<span>.</span></h1>
          <p class="capability-detail-lead">{escape(summary)}</p>
          <div class="capability-detail-actions"><a class="button button--ink" href="#install">{"Install this Skill" if en else "安装这个 Skill"} →</a><a class="button button--ghost" href="{source_url}" target="_blank" rel="noreferrer">GitHub ↗</a></div>
        </header>

        <figure class="capability-preview capability-preview--skill">
          <div class="capability-preview-top"><span>SOIA / {escape(skill.domain.code)}</span><span>AVAILABLE · PUBLIC</span></div>
          <div class="capability-preview-main"><div><small>SKILL</small><strong>{escape(skill.name)}</strong><p>{escape(summary)}</p></div><div class="capability-preview-flow"><span><i>01</i>{"Input" if en else "输入"}</span><span><i>02</i>{"Run" if en else "执行"}</span><span><i>03</i>{"Receipt" if en else "回执"}</span></div></div>
          <figcaption>{"A public capability with a visible source and bounded delivery contract." if en else "公开能力、公开来源，以及边界清楚的交付契约。"}</figcaption>
        </figure>

        <dl class="capability-meta">
          <div><dt>{"Type" if en else "类型"}</dt><dd>Skill</dd></div>
          <div><dt>{"Domain" if en else "能力域"}</dt><dd>{escape(skill.domain.plugin)}</dd></div>
          <div><dt>{"Status" if en else "状态"}</dt><dd>Available</dd></div>
          <div><dt>{"Snapshot" if en else "目录快照"}</dt><dd>{escape(commit[:10])} · {escape(commit_date)}</dd></div>
        </dl>

        <section class="capability-tags" aria-label="Tags"><span>Skill</span><span>{escape(skill.domain.code)}</span><span>Public source</span><span>Human controlled</span></section>

        <div class="capability-detail-copy">
          <section class="capability-copy-block"><div><p class="catalog-page-label">01 / {"PURPOSE" if en else "用途"}</p><h2>{"One focused responsibility." if en else "一个聚焦的职责。"}</h2></div><div><p>{escape(summary)}</p><aside class="capability-trigger"><span>{"NATURAL-LANGUAGE TRIGGER" if en else "自然语言触发"}</span><strong>{escape(trigger)}</strong></aside><ul><li>{"Start from a natural-language outcome and the minimum authorised input." if en else "从自然语言结果与最小必要的授权输入开始。"}</li><li>{"Load the canonical instruction only when the intent matches." if en else "只有意图命中时，才加载规范 Skill 指令。"}</li><li>{"Finish with artifacts, checks, blockers, and decisions that still belong to the user." if en else "以产物、检查、阻塞项和仍归用户决定的事项收尾。"}</li></ul></div></section>

          <section class="capability-contract-section"><p class="catalog-page-label">02 / {"DELIVERY CONTRACT" if en else "交付契约"}</p><h2>{"What a complete run should contain." if en else "一次完整运行应该包含什么。"}</h2><div class="capability-contract-grid"><article><span>01</span><h3>{"Clear input" if en else "清楚输入"}</h3><p>{"An authorised file, URL, repository, workspace, or concrete goal." if en else "有权使用的文件、URL、仓库、工作区或明确目标。"}</p></article><article><span>02</span><h3>{"Bounded run" if en else "有界执行"}</h3><p>{"Small reliable steps, previews, and approval gates where risk increases." if en else "最小可靠步骤、必要预览，以及风险上升处的批准门。"}</p></article><article><span>03</span><h3>{"Reviewable receipt" if en else "可复核回执"}</h3><p>{"Changed files, generated artifacts, validation, limitations, and next actions." if en else "文件变化、生成产物、验证结果、已知限制和下一步。"}</p></article></div></section>

          <section class="capability-install-section" id="install"><div class="capability-install-head"><p class="catalog-page-label">03 / INSTALL</p><h2>{"Install one Skill or its domain plugin." if en else "安装单个 Skill，或安装整个领域。"}</h2><p>{"Choose the smallest package that matches the task." if en else "只选择与当前任务匹配的最小能力包。"}</p></div><div class="capability-install-list"><article><div><span>Claude Code</span><small>{"Domain plugin" if en else "领域插件"}</small></div><pre><code>{escape(claude)}</code></pre></article><article><div><span>Codex</span><small>{"Domain plugin" if en else "领域插件"}</small></div><pre><code>{escape(codex)}</code></pre></article><article><div><span>npx</span><small>{"Individual Skill" if en else "单个 Skill"}</small></div><pre><code>{escape(single)}</code></pre></article></div></section>

          <section class="capability-copy-block"><div><p class="catalog-page-label">04 / {"BOUNDARY" if en else "边界"}</p><h2>{"Public instructions do not make private data public." if en else "指令公开，不等于数据公开。"}</h2></div><div><p>{"Keep passwords, tokens, cookies, customer files, and restricted material out of public issues and repositories. Deletion, publishing, payment, external writes, and permission changes require explicit authorization." if en else "密码、Token、Cookie、客户文件和受限制资料不得进入公共 Issue 或仓库。删除、发布、付款、外部写入和权限变更必须获得明确授权。"}</p><div class="capability-evidence-links"><a href="{docs_url}" target="_blank" rel="noreferrer">{"Canonical documentation" if en else "规范文档"} ↗</a><a href="{source_url}" target="_blank" rel="noreferrer">{"Skill source" if en else "Skill 源码"} ↗</a><a href="{domain_path(locale, skill.domain)}">{"Back to domain" if en else "返回能力域"} →</a></div></div></section>
        </div>
      </article>"""
    return document(
        locale,
        "open",
        f"{skill.title_en} — {skill.name} | SOIA Open" if en else f"{skill.name} | SOIA Open",
        summary,
        skill_path(locale, skill),
        main,
    )


def render_open(
    locale: str,
    domains: dict[str, list[Skill]],
    commit: str,
    commit_date: str,
) -> str:
    en = locale == "en"
    total = sum(len(items) for items in domains.values())
    domain_rows = []
    expert_rows = []
    for index, (plugin, domain) in enumerate(DOMAINS.items(), start=1):
        expert = EXPERTS[plugin]
        domain_title = domain.title_en if en else domain.title_zh
        domain_summary = domain.summary_en if en else domain.summary_zh
        profession = expert.profession_en if en else expert.profession_zh
        expert_description = expert.description_en if en else expert.description_zh
        domain_rows.append(
            f"""            <li class="ecosystem-row"><a href="{domain_path(locale, domain)}"><span class="catalog-row-index">{index:02d}</span><span class="ecosystem-row-code">{escape(domain.code)}</span><span class="ecosystem-row-body"><strong>{escape(domain_title)}</strong><span>{escape(domain_summary)}</span></span><span class="ecosystem-row-meta"><b>{len(domains[plugin])}</b><small>Skills</small></span><span class="catalog-row-arrow" aria-hidden="true">→</span></a></li>"""
        )
        expert_rows.append(
            f"""            <li class="ecosystem-row ecosystem-row--expert"><a href="{expert_path(locale, expert)}"><span class="catalog-row-index">{index:02d}</span><span class="ecosystem-row-code">{escape(domain.code)}</span><span class="ecosystem-row-body"><strong>{escape(profession)}</strong><span>{escape(expert_description)}</span></span><span class="ecosystem-row-meta"><b>{len(domains[plugin])}</b><small>{"included Skills" if en else "个领域 Skills"}</small></span><span class="catalog-row-arrow" aria-hidden="true">→</span></a></li>"""
        )
    main = f"""      <div class="ecosystem-catalog-page">
        <header class="ecosystem-catalog-head">
          <p class="catalog-page-label">SOIA OPEN ECOSYSTEM</p>
          <h1>{"Open Skills and Experts" if en else "开放 Skills 与 Experts"}<span>.</span></h1>
          <p>{"Browse public capability by outcome and domain. Every Skill and WorkBuddy Expert keeps a visible source, install path, and delivery boundary." if en else "按结果与领域浏览公开能力。每个 Skill 与 WorkBuddy Expert 都保留公开来源、安装入口和交付边界。"}</p>
          <div class="catalog-page-actions"><a class="button button--ink" href="#skills">{"Browse Skills" if en else "浏览 Skills"} →</a><a class="button button--ghost" href="#experts">{"Browse Experts" if en else "浏览 Experts"} →</a></div>
        </header>
        <nav class="catalog-switch" aria-label="{"Open catalog" if en else "开放目录"}"><a href="#skills">Skills <span>{total}</span></a><a href="#experts">Experts <span>{len(EXPERTS)}</span></a><a href="https://github.com/soia-team/soia-open-skills" target="_blank" rel="noreferrer">GitHub ↗</a></nav>
        <section class="ecosystem-catalog-section" id="skills"><header><div><p class="catalog-page-label">01 / CAPABILITY DOMAINS</p><h2>{"Find the domain, then the Skill." if en else "先找到领域，再找到 Skill。"}</h2></div><p>{"Eight public domains lead to every documented Skill without inventing another product layer." if en else "八个公开能力域直接通向全部 Skill，不再重复包装成另一套产品。"}</p></header><ol class="ecosystem-row-list">
{chr(10).join(domain_rows)}
        </ol></section>
        <aside class="ecosystem-contribute"><div><p class="catalog-page-label">PUBLIC SOURCE</p><h2>{"Read the source before relying on the claim." if en else "先读源码，再相信能力说明。"}</h2><p>{"The public catalog and marketplace manifest remain the authority for installable versions." if en else "公开目录与 marketplace manifest 是安装版本的事实真源。"}</p></div><a class="button button--ghost" href="https://github.com/soia-team/soia-open-skills" target="_blank" rel="noreferrer">GitHub ↗</a></aside>
        <section class="ecosystem-catalog-section" id="experts"><header><div><p class="catalog-page-label">02 / WORKBUDDY EXPERTS</p><h2>{"The same public source, organized as a role." if en else "同一份公开能力，组织成角色入口。"}</h2></div><p>{"Each domain repository can be installed as a WorkBuddy Expert. The Expert adds role context; it does not hide its Skills." if en else "每个领域仓都能作为 WorkBuddy Expert 安装。Expert 增加角色上下文，但不隐藏它包含的 Skills。"}</p></header><ol class="ecosystem-row-list">
{chr(10).join(expert_rows)}
        </ol></section>
        <footer class="catalog-snapshot">SOIA Public Catalog · {escape(commit[:10])} · {escape(commit_date)} · {total} Skills · {len(EXPERTS)} Experts</footer>
      </div>"""
    return document(
        locale, "open",
        "SOIA Open | Public Skills and Experts" if en else "SOIA Open｜开放 Skills 与 Experts",
        "Browse SOIA public Skills and WorkBuddy Experts by domain." if en else "按领域浏览 SOIA 公开 Skills 与 WorkBuddy Experts。",
        route(locale, "open/"), main,
    )


def render_experts_index(
    locale: str,
    domains: dict[str, list[Skill]],
    commit: str,
    commit_date: str,
) -> str:
    en = locale == "en"
    rows = []
    for index, (plugin, expert) in enumerate(EXPERTS.items(), start=1):
        domain = DOMAINS[plugin]
        profession = expert.profession_en if en else expert.profession_zh
        description = expert.description_en if en else expert.description_zh
        rows.append(f"""              <li class="catalog-row"><a href="{expert_path(locale, expert)}"><span class="catalog-row-index">{index:03d}</span><span class="catalog-row-thumb" aria-hidden="true">{escape(domain.code)}</span><span class="catalog-row-body"><strong>{escape(profession)}</strong><span>{escape(description)}</span></span><span class="catalog-row-meta"><i>WorkBuddy</i><i>{len(domains[plugin])} Skills</i></span><span class="catalog-row-arrow" aria-hidden="true">→</span></a></li>""")
    main = f"""      <div class="catalog-level-page expert-directory-page">
        <section class="catalog-page-hero"><div class="catalog-page-narrow"><nav class="catalog-breadcrumb" aria-label="{"Breadcrumb" if en else "面包屑"}"><a href="{route(locale, 'open/')}">{"Open ecosystem" if en else "开放生态"}</a><span aria-hidden="true">·</span><span aria-current="page">Experts</span></nav><p class="catalog-page-label">WORKBUDDY EXPERT CATALOG</p><h1>{"Role-based public capability" if en else "角色化公开能力"}<span>.</span></h1><p class="catalog-page-lead">{"Eight domain packages organize public Skills as WorkBuddy role entries while preserving the source and boundaries." if en else "八个领域包将公开 Skills 组织为 WorkBuddy 角色入口，同时保留来源和边界。"}</p></div></section>
        <section class="catalog-list-section"><div class="catalog-page-wide"><header class="catalog-list-head"><div><p class="catalog-page-label">EXPERT INDEX</p><h2>{"Choose the role that matches the work." if en else "按工作选择角色。"}</h2></div><p>{"Open an Expert to see its included domain, example tasks, install route, and evidence." if en else "打开 Expert 查看所属领域、典型任务、安装入口与公开证据。"}</p></header><ol class="catalog-row-list">
{chr(10).join(rows)}
        </ol><footer class="catalog-snapshot">SOIA Public Catalog · {escape(commit[:10])} · {escape(commit_date)}</footer></div></section>
      </div>"""
    return document(locale, "open", "WorkBuddy Experts | SOIA Open" if en else "WorkBuddy Experts｜SOIA Open", "Public WorkBuddy Experts backed by SOIA domain Skills." if en else "由 SOIA 领域 Skills 支撑的公开 WorkBuddy Experts。", route(locale, "open/experts/"), main)


def render_expert(
    locale: str,
    expert: Expert,
    skills: list[Skill],
    commit: str,
    commit_date: str,
) -> str:
    en = locale == "en"
    domain = DOMAINS[expert.plugin]
    profession = expert.profession_en if en else expert.profession_zh
    description = expert.description_en if en else expert.description_zh
    prompts = expert.prompts_en if en else expert.prompts_zh
    source_url = f"https://github.com/soia-team/{domain.repo}/blob/main/.codebuddy-plugin/plugin.json"
    repo_url = f"https://github.com/soia-team/{domain.repo}"
    install_docs = "https://github.com/soia-team/soia-open-skills/blob/main/docs/install/workbuddy.md"
    visible_skills = "".join(f"<span>{escape(item.name)}</span>" for item in skills[:6])
    if len(skills) > 6:
        visible_skills += f"<span>+{len(skills) - 6}</span>"
    prompt_cards = "".join(f"<article><span>{index:02d}</span><p>{escape(prompt)}</p></article>" for index, prompt in enumerate(prompts, start=1))
    main = f"""      <article class="capability-detail-page capability-detail-page--expert">
        <header class="capability-detail-head"><nav class="catalog-breadcrumb" aria-label="{"Breadcrumb" if en else "面包屑"}"><a href="{route(locale, 'open/')}">{"Open ecosystem" if en else "开放生态"}</a><span aria-hidden="true">·</span><a href="{route(locale, 'open/experts/')}">Experts</a><span aria-hidden="true">·</span><span aria-current="page">{escape(domain.code)}</span></nav><p class="catalog-page-label">WORKBUDDY EXPERT · {escape(domain.code)}</p><h1>{escape(profession)}<span>.</span></h1><p class="capability-detail-lead">{escape(description)}</p><div class="capability-detail-actions"><a class="button button--ink" href="#install">{"Install this Expert" if en else "安装这个 Expert"} →</a><a class="button button--ghost" href="{repo_url}" target="_blank" rel="noreferrer">GitHub ↗</a></div></header>

        <figure class="capability-preview capability-preview--expert"><div class="capability-preview-top"><span>SOIA / WORKBUDDY</span><span>PUBLIC EXPERT · {escape(domain.code)}</span></div><div class="capability-preview-main"><div><small>EXPERT</small><strong>{escape(profession)}</strong><p>{escape(description)}</p></div><div class="capability-preview-flow"><span><i>01</i>{"Role" if en else "角色"}</span><span><i>02</i>Skills</span><span><i>03</i>{"Tasks" if en else "任务"}</span></div></div><figcaption>{"A role entry backed by a public domain package, not a hidden cloud workflow." if en else "由公开领域包支撑的角色入口，不是隐藏在云端的黑盒流程。"}</figcaption></figure>

        <dl class="capability-meta"><div><dt>{"Type" if en else "类型"}</dt><dd>WorkBuddy Expert</dd></div><div><dt>{"Domain" if en else "能力域"}</dt><dd>{escape(domain.plugin)}</dd></div><div><dt>{"Included" if en else "包含"}</dt><dd>{len(skills)} Skills</dd></div><div><dt>{"Snapshot" if en else "目录快照"}</dt><dd>{escape(commit[:10])} · {escape(commit_date)}</dd></div></dl>
        <section class="capability-tags" aria-label="Tags"><span>Expert</span><span>WorkBuddy</span><span>{escape(domain.code)}</span><span>Public package</span></section>

        <div class="capability-detail-copy">
          <section class="capability-copy-block"><div><p class="catalog-page-label">01 / {"ROLE" if en else "角色"}</p><h2>{"A domain entry for repeated work." if en else "面向重复工作的领域入口。"}</h2></div><div><p>{escape(description)}</p><p>{"The Expert adds a role, recommended tasks, and a selected Skill set. The canonical Skills remain individually inspectable." if en else "Expert 增加角色、推荐任务与一组 Skills；每个规范 Skill 仍然可以单独审查。"}</p><div class="expert-skill-chips">{visible_skills}</div></div></section>
          <section class="expert-prompts-section"><p class="catalog-page-label">02 / {"EXAMPLE TASKS" if en else "典型任务"}</p><h2>{"Start with a real request." if en else "从一个真实请求开始。"}</h2><div class="expert-prompt-grid">{prompt_cards}</div></section>
          <section class="capability-install-section" id="install"><div class="capability-install-head"><p class="catalog-page-label">03 / INSTALL</p><h2>{"Install the public domain as a WorkBuddy Expert." if en else "把公开领域安装为 WorkBuddy Expert。"}</h2><p>{"WorkBuddy has no plugin CLI. Use the public installer, then restart the desktop client and verify the Expert under My Experts." if en else "WorkBuddy 没有插件 CLI。使用公开安装器后重启桌面客户端，再到“我的专家”验证可见性。"}</p></div><div class="capability-install-list"><article><div><span>{"Natural language" if en else "自然语言"}</span><small>{"Recommended" if en else "推荐"}</small></div><pre><code>{escape(f'Install {expert.plugin} into WorkBuddy' if en else f'帮我把 {expert.plugin} 安装到 WorkBuddy')}</code></pre></article><article><div><span>{"Public installer" if en else "公开安装器"}</span><small>{"Advanced" if en else "高级"}</small></div><pre><code>{escape(f"python3 <soia-open-skills>/skills/soia-meta-skill-release/scripts/install_workbuddy_experts.py {expert.plugin}")}</code></pre></article></div></section>
          <section class="capability-copy-block"><div><p class="catalog-page-label">04 / {"EVIDENCE" if en else "证据"}</p><h2>{"Role context without hiding the source." if en else "增加角色上下文，但不隐藏来源。"}</h2></div><div><p>{"The repository manifest, Agent file, and included Skill paths are public. Local user data, credentials, and restricted material remain outside the public package." if en else "仓库清单、Agent 文件和所含 Skill 路径均公开；本地用户数据、凭据与受限制资料不进入公共包。"}</p><div class="capability-evidence-links"><a href="{source_url}" target="_blank" rel="noreferrer">{"Expert manifest" if en else "Expert 清单"} ↗</a><a href="{install_docs}" target="_blank" rel="noreferrer">{"Install guide" if en else "安装指南"} ↗</a><a href="{domain_path(locale, domain)}">{"Browse included Skills" if en else "浏览所含 Skills"} →</a></div></div></section>
        </div>
      </article>"""
    return document(locale, "open", f"{profession} | SOIA Open", description, expert_path(locale, expert), main)


def render_legacy_skill_alias(
    locale: str,
    legacy_name: str,
    replacement: Skill,
    commit: str,
    commit_date: str,
) -> str:
    """Keep one legacy public route explicit and visually consistent.

    A legacy URL is not silently repurposed as a current catalog entry. It
    remains a small compatibility page pointing to the current public Skill.
    """
    en = locale == "en"
    path = route(locale, f"open/{replacement.domain.slug}/{legacy_name}/")
    target = skill_path(locale, replacement)
    summary = (
        f"Compatibility route for the current public Skill: {replacement.name}."
        if en
        else f"保留的兼容路径，当前公开 Skill 为：{replacement.name}。"
    )
    headline = "This public path has moved." if en else "这个公开路径已更新。"
    body_copy = (
        "The earlier name is kept so old public links do not become a dead end. "
        "Use the current Skill page for instructions, installation, evidence, and releases."
        if en
        else "旧名称被保留，避免已有公开链接变成死链。请使用当前 Skill 页面查看指令、安装、证据与发布状态。"
    )
    main = f"""      <div class="skill-story-v3">
        <section class="skill-story-hero"><div class="shell"><div class="skill-story-head">
          <a class="skill-story-back" href="{domain_path(locale, replacement.domain)}">← {"Back to domain" if en else "返回能力域"}</a>
          <p class="skill-story-category">PUBLIC COMPATIBILITY ROUTE · {escape(replacement.domain.plugin)}</p>
          <h1>{escape(legacy_name)}</h1>
          <p class="skill-story-summary">{escape(summary)}</p>
          <p class="skill-story-byline">SOIA Public Catalog · {escape(commit[:10])} · {escape(commit_date)}</p>
        </div><div class="skill-story-figure" aria-label="{"Compatibility route" if en else "兼容路径"}"><div class="skill-story-figure-grid">
          <div><span>LEGACY</span><strong>{escape(legacy_name)}</strong></div><div><span>STATUS</span><strong>{"Moved<br />with intent" if en else "已更新<br />保留入口"}</strong></div><div><span>CURRENT</span><strong>{escape(replacement.name)}</strong></div>
        </div></div></div></section>
        <section><div class="shell skill-story-layout"><article class="skill-story-body"><section><p class="kicker">COMPATIBILITY</p><h2>{headline}</h2><p>{body_copy}</p><p><a href="{target}">{"Open the current Skill →" if en else "打开当前 Skill →"}</a></p></section></article><aside class="skill-story-aside"><p class="mono-label">CURRENT PUBLIC SKILL</p><p>{escape(replacement.summary_en if en else replacement.summary_zh)}</p><a class="button button--ink" href="{target}">{"Open current Skill" if en else "打开当前 Skill"} →</a></aside></div></section>
      </div>"""
    return document(
        locale,
        "open",
        f"{legacy_name} ({'moved' if en else '已更新'}) | SOIA Open",
        summary,
        path,
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

    # Most top-level pages remain curated editorial surfaces. The Open entry
    # and its Expert directory are generated from the same public catalog as
    # domain and Skill pages so level 2–4 never drift apart.
    generated_paths = [
        "/", "/open/", "/products/", "/pricing/", "/showcase/", "/docs/", "/spec/", "/course/", "/services/", "/about/", "/blog/", "/blog/codex-open-design/",
        "/en/", "/en/open/", "/en/products/", "/en/pricing/", "/en/showcase/", "/en/docs/", "/en/spec/", "/en/course/", "/en/services/", "/en/about/", "/en/blog/", "/en/blog/codex-open-design/",
        # Compatibility routes for five catalog entries renamed upstream.
        "/open/pkm-vault/soia-pkm-extract-vault-knowledge/", "/open/pkm-vault/soia-pkm-log-agent-sessions/", "/open/pkm-vault/soia-pkm-maintain-vault-health/", "/open/pkm-vault/soia-pkm-manage-vault-lifecycle/", "/open/pkm-vault/soia-pkm-query-vault/",
        "/en/open/pkm-vault/soia-pkm-extract-vault-knowledge/", "/en/open/pkm-vault/soia-pkm-log-agent-sessions/", "/en/open/pkm-vault/soia-pkm-maintain-vault-health/", "/en/open/pkm-vault/soia-pkm-manage-vault-lifecycle/", "/en/open/pkm-vault/soia-pkm-query-vault/",
    ]
    for public_path in generated_paths:
        page = ROOT / public_path.lstrip("/") / "index.html"
        if public_path == "/":
            page = ROOT / "index.html"
        if not page.exists():
            raise SystemExit(f"missing curated top-level page: {page}")

    for locale in ("zh", "en"):
        open_path = route(locale, "open/")
        write_page(
            ROOT / open_path.lstrip("/") / "index.html",
            render_open(locale, by_domain, commit, commit_date),
        )
        experts_path = route(locale, "open/experts/")
        write_page(
            ROOT / experts_path.lstrip("/") / "index.html",
            render_experts_index(locale, by_domain, commit, commit_date),
        )
        generated_paths.extend([open_path, experts_path])
        for plugin, expert in EXPERTS.items():
            path = expert_path(locale, expert)
            write_page(
                ROOT / path.lstrip("/") / "index.html",
                render_expert(locale, expert, by_domain[plugin], commit, commit_date),
            )
            generated_paths.append(path)

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

    # A previous public route remains a compatibility page instead of an
    # invisible stale file. The current Skill page remains the canonical place
    # for instructions and installation.
    skills_by_name = {skill.name: skill for skill in skills}
    legacy_aliases = {
        "soia-pkm-maintain": "soia-pkm-maintain-vault-health",
    }
    for legacy_name, replacement_name in legacy_aliases.items():
        replacement = skills_by_name.get(replacement_name)
        if replacement is None:
            raise SystemExit(f"missing replacement Skill for legacy route: {replacement_name}")
        for locale in ("zh", "en"):
            path = route(locale, f"open/{replacement.domain.slug}/{legacy_name}/")
            write_page(
                ROOT / path.lstrip("/") / "index.html",
                render_legacy_skill_alias(locale, legacy_name, replacement, commit, commit_date),
            )
            generated_paths.append(path)

    write_sitemap(generated_paths, max(commit_date, date.today().isoformat()))
    print(
        f"generated {len(skills)} bilingual Skill pages, "
        f"{len(DOMAINS)} bilingual domain pages, "
        f"and {len(EXPERTS)} bilingual Expert pages "
        f"from {commit[:12]}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
