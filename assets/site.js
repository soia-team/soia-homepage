document.documentElement.classList.add("js");

const NAV_GROUPS = {
  zh: [
    {
      id: "products",
      label: "产品",
      pages: ["products", "course"],
      columns: [
        { title: "产品", items: [["产品体系", "/products/", "Skill 到 Expert"], ["课程", "/course/", "亲手完成一个工作流"], ["产品规格", "/spec/", "交付与版本边界"]] },
        { title: "交付形态", items: [["Skill", "/open/?tab=skill", "最小能力单元"], ["Workflow", "/products/#catalog", "可复跑的任务链"], ["Plugin", "/products/#catalog", "Codex / Claude Code 入口"], ["Expert", "/products/#catalog", "WorkBuddy 角色系统"]] },
      ],
    },
    {
      id: "solutions",
      label: "解决方案",
      pages: ["services", "showcase", "spec"],
      columns: [
        { title: "从任务开始", items: [["内容与知识", "/open/pkm-vault/", "归档、提炼与发布"], ["设计与演示", "/open/development-design/", "原型、图表与演示"], ["工程与交付", "/open/development/", "编码、测试与发版"]] },
        { title: "落地方式", items: [["免费验证", "/open/", "先运行公开能力"], ["自己构建", "/course/", "学习完整方法"], ["共同落地", "/services/", "私有 Pilot 与交接"], ["查看成品", "/showcase/", "了解交付结果"]] },
      ],
    },
    {
      id: "open",
      label: "开放生态",
      pages: ["open"],
      columns: [
        { title: "能力目录", items: [["全部 Skills", "/open/?tab=skill", "按结果与领域查找"], ["知识库与内容", "/open/pkm-vault/", "资料进入可复用系统"], ["内容生产", "/open/media-content/", "文章、配图与发布草稿"], ["开发与设计", "/open/development-design/", "产品与技术设计"]] },
        { title: "宿主与生态", items: [["Codex", "/open/environment/soia-env-codex-setup-support/", "配置与运行支持"], ["Claude Code", "/open/environment/soia-env-claude-cli-install/", "安装与能力加载"], ["WorkBuddy", "/open/environment/soia-env-workbuddy-install/", "Expert 入口"], ["GitHub 源码", "https://github.com/soia-team/soia-open-skills", "审查公开能力"]] },
      ],
    },
    { id: "pricing", label: "价格", pages: ["pricing"], href: "/pricing/" },
    {
      id: "resources",
      label: "资源",
      pages: ["docs", "blog", "about"],
      columns: [
        { title: "阅读", items: [["博客", "/blog/", "方法、案例与更新"], ["Codex × Open Design", "/blog/codex-open-design/", "从截图到生产页面"], ["文档", "/docs/", "安装、使用与边界"], ["课程详情", "/course/", "课程结构与交付"]] },
        { title: "了解 SOIA", items: [["服务与合作", "/services/", "私有流程落地"], ["成品展示", "/showcase/", "交付形态与结果"], ["关于", "/about/", "原则与团队"], ["GitHub", "https://github.com/soia-team", "公开组织与仓库"]] },
      ],
    },
  ],
  en: [
    {
      id: "products",
      label: "Products",
      pages: ["products", "course"],
      columns: [
        { title: "Products", items: [["Product system", "/en/products/", "Skill to Expert"], ["Course", "/en/course/", "Build one real workflow"], ["Product spec", "/en/spec/", "Delivery and version boundaries"]] },
        { title: "Delivery forms", items: [["Skill", "/en/open/?tab=skill", "Smallest capability"], ["Workflow", "/en/products/#catalog", "Repeatable task chain"], ["Plugin", "/en/products/#catalog", "Codex / Claude Code entry"], ["Expert", "/en/products/#catalog", "WorkBuddy role system"]] },
      ],
    },
    {
      id: "solutions",
      label: "Solutions",
      pages: ["services", "showcase", "spec"],
      columns: [
        { title: "Start from work", items: [["Knowledge", "/en/open/pkm-vault/", "Capture, distill, publish"], ["Design", "/en/open/development-design/", "Prototypes and presentations"], ["Engineering", "/en/open/development/", "Code, test, release"]] },
        { title: "Ways to begin", items: [["Validate free", "/en/open/", "Run public capabilities"], ["Build it", "/en/course/", "Learn the full method"], ["Deliver together", "/en/services/", "Private pilot and handoff"], ["View outcomes", "/en/showcase/", "See delivery examples"]] },
      ],
    },
    {
      id: "open",
      label: "Open ecosystem",
      pages: ["open"],
      columns: [
        { title: "Capability catalog", items: [["All Skills", "/en/open/?tab=skill", "Browse by outcome"], ["Knowledge", "/en/open/pkm-vault/", "Turn material into a system"], ["Media", "/en/open/media-content/", "Articles and channel drafts"], ["Dev & design", "/en/open/development-design/", "Product and technical design"]] },
        { title: "Hosts", items: [["Codex", "/en/open/environment/soia-env-codex-setup-support/", "Setup and runtime support"], ["Claude Code", "/en/open/environment/soia-env-claude-cli-install/", "Install and load capabilities"], ["WorkBuddy", "/en/open/environment/soia-env-workbuddy-install/", "Expert entry"], ["GitHub source", "https://github.com/soia-team/soia-open-skills", "Inspect public capability"]] },
      ],
    },
    { id: "pricing", label: "Pricing", pages: ["pricing"], href: "/en/pricing/" },
    {
      id: "resources",
      label: "Resources",
      pages: ["docs", "blog", "about"],
      columns: [
        { title: "Learn", items: [["Blog", "/en/blog/", "Methods, cases, updates"], ["Codex × Open Design", "/en/blog/codex-open-design/", "Screenshot to production page"], ["Docs", "/en/docs/", "Install, use, boundaries"], ["Course", "/en/course/", "Structure and outcomes"]] },
        { title: "About SOIA", items: [["Services", "/en/services/", "Private workflow delivery"], ["Showcase", "/en/showcase/", "Delivery forms and results"], ["About", "/en/about/", "Principles and team"], ["GitHub", "https://github.com/soia-team", "Public repositories"]] },
      ],
    },
  ],
};

const FOOTER_GROUPS = {
  zh: [
    { title: "产品", items: [["产品体系", "/products/"], ["课程", "/course/"], ["价格", "/pricing/"], ["服务与合作", "/services/"]] },
    { title: "能力形态", items: [["Skill", "/open/?tab=skill"], ["Workflow", "/products/#catalog"], ["Plugin", "/products/#catalog"], ["Expert", "/products/#catalog"]] },
    { title: "开放生态", items: [["全部 Skills", "/open/?tab=skill"], ["知识库与内容", "/open/pkm-vault/"], ["内容生产", "/open/media-content/"], ["开发与设计", "/open/development-design/"]] },
    { title: "运行宿主", items: [["Codex", "/open/environment/soia-env-codex-setup-support/"], ["Claude Code", "/open/environment/soia-env-claude-cli-install/"], ["WorkBuddy", "/open/environment/soia-env-workbuddy-install/"], ["GitHub", "https://github.com/soia-team"]] },
    { title: "资源", items: [["博客", "/blog/"], ["文档", "/docs/"], ["成品展示", "/showcase/"], ["产品规格", "/spec/"]] },
    { title: "SOIA", items: [["关于", "/about/"], ["公开方法", "/open/"], ["服务边界", "/services/"], ["公开仓库", "https://github.com/soia-team/soia-open-skills"]] },
  ],
  en: [
    { title: "Products", items: [["Product system", "/en/products/"], ["Course", "/en/course/"], ["Pricing", "/en/pricing/"], ["Services", "/en/services/"]] },
    { title: "Capability", items: [["Skill", "/en/open/?tab=skill"], ["Workflow", "/en/products/#catalog"], ["Plugin", "/en/products/#catalog"], ["Expert", "/en/products/#catalog"]] },
    { title: "Open ecosystem", items: [["All Skills", "/en/open/?tab=skill"], ["Knowledge", "/en/open/pkm-vault/"], ["Media", "/en/open/media-content/"], ["Dev & design", "/en/open/development-design/"]] },
    { title: "Hosts", items: [["Codex", "/en/open/environment/soia-env-codex-setup-support/"], ["Claude Code", "/en/open/environment/soia-env-claude-cli-install/"], ["WorkBuddy", "/en/open/environment/soia-env-workbuddy-install/"], ["GitHub", "https://github.com/soia-team"]] },
    { title: "Resources", items: [["Blog", "/en/blog/"], ["Docs", "/en/docs/"], ["Showcase", "/en/showcase/"], ["Product spec", "/en/spec/"]] },
    { title: "SOIA", items: [["About", "/en/about/"], ["Open methods", "/en/open/"], ["Service boundary", "/en/services/"], ["Repositories", "https://github.com/soia-team/soia-open-skills"]] },
  ],
};

const REQUEST_URL = "https://github.com/soia-team/soia-open-skills/issues/new";
const COURSE_URL = "https://github.com/soia-team/soia-open-skills/issues/new";

function getLocale() {
  return document.documentElement.lang.toLowerCase().startsWith("en") ? "en" : "zh";
}

function languageTarget(locale) {
  const path = window.location.pathname;
  if (locale === "en") {
    const target = path.replace(/^\/en(?=\/|$)/, "") || "/";
    return target.startsWith("/") ? target : `/${target}`;
  }
  return path === "/" ? "/en/" : `/en${path}`;
}

function renderHeader() {
  const host = document.querySelector("[data-site-header]");
  if (!host) return;
  host.classList.add("site-header-host");
  const current = document.body.dataset.page || "home";
  const locale = getLocale();
  const copy = locale === "en"
    ? { home: "SOIA home", menu: "Menu", nav: "Primary navigation", start: "Explore ecosystem", language: "中文", languageLabel: "切换到中文" }
    : { home: "SOIA 首页", menu: "菜单", nav: "主导航", start: "进入开放生态", language: "EN", languageLabel: "Switch to English" };
  const links = NAV_GROUPS[locale].map((group) => {
    const active = group.pages?.includes(current);
    if (group.href) {
      return `<a class="nav-direct${active ? " is-active" : ""}" href="${group.href}" ${active ? 'aria-current="page"' : ""}>${group.label}</a>`;
    }
    const menuId = `nav-menu-${group.id}`;
    const columns = group.columns.map((column) => `
      <section class="mega-column">
        <p>${column.title}</p>
        ${column.items.map(([label, href, description]) => `<a class="mega-link" href="${href}"><span>${label}</span><small>${description}</small></a>`).join("")}
      </section>`).join("");
    return `<div class="nav-item nav-item--menu${active ? " is-active" : ""}" data-nav-menu>
      <button class="nav-menu-trigger" type="button" aria-expanded="false" aria-controls="${menuId}">${group.label}<span aria-hidden="true">⌄</span></button>
      <div class="mega-menu" id="${menuId}" hidden><div class="mega-menu-grid">${columns}</div></div>
    </div>`;
  }).join("");

  host.innerHTML = `
    <header class="site-header site-header--floating">
      <div class="header-inner header-inner--floating">
        <a class="brand" href="${locale === "en" ? "/en/" : "/"}" aria-label="${copy.home}">
          <span class="brand-mark" aria-hidden="true"><i></i><i></i><i></i></span>
          <span>SOIA</span>
        </a>
        <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">
          <span>${copy.menu}</span><i aria-hidden="true"></i>
        </button>
        <nav class="site-nav" id="site-nav" aria-label="${copy.nav}">${links}</nav>
        <div class="header-actions">
          <a class="language-switch" href="${languageTarget(locale)}" hreflang="${locale === "en" ? "zh-CN" : "en"}" aria-label="${copy.languageLabel}">${copy.language}</a>
          <a class="button button--small button--ink header-action" href="${locale === "en" ? "/en/open/" : "/open/"}">${copy.start}</a>
        </div>
      </div>
    </header>`;

  const button = host.querySelector(".nav-toggle");
  const nav = host.querySelector(".site-nav");
  const menuItems = [...host.querySelectorAll("[data-nav-menu]")];
  const desktop = () => window.matchMedia("(min-width: 861px)").matches;
  const setMenu = (item, open) => {
    const trigger = item.querySelector(".nav-menu-trigger");
    const panel = item.querySelector(".mega-menu");
    trigger?.setAttribute("aria-expanded", String(open));
    item.classList.toggle("is-open", open);
    if (panel) panel.hidden = !open;
  };
  const closeMenus = (except = null) => menuItems.forEach((item) => {
    if (item !== except) setMenu(item, false);
  });

  menuItems.forEach((item) => {
    const trigger = item.querySelector(".nav-menu-trigger");
    trigger?.addEventListener("click", (event) => {
      event.stopPropagation();
      const open = trigger.getAttribute("aria-expanded") !== "true";
      closeMenus(item);
      setMenu(item, open);
    });
    item.addEventListener("mouseenter", () => {
      if (!desktop()) return;
      closeMenus(item);
      setMenu(item, true);
    });
    item.addEventListener("mouseleave", () => {
      if (desktop()) setMenu(item, false);
    });
    item.addEventListener("keydown", (event) => {
      if (event.key === "ArrowDown" && event.target === trigger) {
        event.preventDefault();
        closeMenus(item);
        setMenu(item, true);
        window.requestAnimationFrame(() => item.querySelector(".mega-link")?.focus());
      }
      if (event.key === "Escape") {
        setMenu(item, false);
        trigger?.focus();
      }
    });
  });

  document.addEventListener("click", (event) => {
    if (!host.contains(event.target)) closeMenus();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeMenus();
  });
  button?.addEventListener("click", () => {
    const open = button.getAttribute("aria-expanded") === "true";
    button.setAttribute("aria-expanded", String(!open));
    nav?.classList.toggle("is-open", !open);
    document.body.classList.toggle("menu-locked", !open);
    if (open) closeMenus();
  });
  const updateHeader = () => host.querySelector(".site-header")?.classList.toggle("is-scrolled", window.scrollY > 8);
  updateHeader();
  window.addEventListener("scroll", updateHeader, { passive: true });
}

function renderFooter() {
  const host = document.querySelector("[data-site-footer]");
  if (!host) return;
  const locale = getLocale();
  const en = locale === "en";
  host.classList.add("site-footer-host");
  const groups = FOOTER_GROUPS[locale].map((group) => `
    <section class="footer-directory-column">
      <h2>${group.title}</h2>
      <ul>${group.items.map(([label, href]) => {
        const external = href.startsWith("http");
        return `<li><a href="${href}"${external ? ' target="_blank" rel="noreferrer"' : ""}>${label}${external ? '<span aria-hidden="true">↗</span>' : ""}</a></li>`;
      }).join("")}</ul>
    </section>`).join("");
  host.innerHTML = `
    <footer class="site-footer site-footer--directory">
      <div class="footer-directory-shell">
        <div class="footer-directory-top">
          <div class="footer-directory-brand">
            <a class="brand" href="${en ? "/en/" : "/"}"><span class="brand-mark" aria-hidden="true"><i></i><i></i><i></i></span><span>SOIA</span></a>
            <p>${en ? "Open capabilities for real work, with a clear boundary for private delivery." : "让公开能力先被看见、安装和验证，再把私有流程按边界落地。"}</p>
          </div>
          <nav class="footer-directory-grid" aria-label="${en ? "Footer navigation" : "页脚导航"}">${groups}</nav>
        </div>
        <div class="footer-directory-legal">
          <span>© <span data-year></span> SOIA Team</span>
          <span>${en ? "Open methods · Scoped private delivery" : "公开方法 · 有边界的私有交付"}</span>
          <a href="https://github.com/soia-team" target="_blank" rel="noreferrer">GitHub ↗</a>
        </div>
        <p class="footer-directory-wordmark" aria-hidden="true">SOIA<span>.</span></p>
      </div>
    </footer>`;
}

function wireLinks() {
  document.querySelectorAll("[data-request-link]").forEach((link) => {
    link.href = REQUEST_URL;
  });
  document.querySelectorAll("[data-course-link]").forEach((link) => {
    link.href = COURSE_URL;
  });
  document.querySelectorAll("[data-year]").forEach((node) => {
    node.textContent = String(new Date().getFullYear());
  });
}

function wireCatalog() {
  const input = document.querySelector("[data-catalog-search]");
  if (!input) return;
  const cards = [...document.querySelectorAll("[data-catalog-card]")];
  const empty = document.querySelector("[data-catalog-empty]");
  input.addEventListener("input", () => {
    const query = input.value.trim().toLowerCase();
    let shown = 0;
    cards.forEach((card) => {
      const match = !query || card.textContent.toLowerCase().includes(query);
      card.hidden = !match;
      if (match) shown += 1;
    });
    if (empty) empty.hidden = shown !== 0;
  });
}

function wireResponsiveTables() {
  document.querySelectorAll(".host-table, .course-table").forEach((table) => {
    const labels = [...table.querySelectorAll("thead th")].map((cell) => cell.textContent.trim());
    if (!labels.length) return;
    table.querySelectorAll("tbody tr").forEach((row) => {
      [...row.children].forEach((cell, index) => {
        if (labels[index]) cell.dataset.label = labels[index];
      });
    });
    table.classList.add("is-mobile-ready");
  });
}

function wireOpenTabs() {
  if (document.body.dataset.page !== "open") return;
  const tabs = [...document.querySelectorAll("[data-open-tab]")];
  if (!tabs.length) return;
  const param = new URLSearchParams(window.location.search).get("tab");
  const target = param === "skill" || param === "skills" ? "skills" : param === "workbench" || param === "expert" ? "workbench" : "overview";
  document.body.dataset.openView = target;
  tabs.forEach((tab) => tab.classList.toggle("is-active", tab.dataset.openTab === target));
  const sections = [...document.querySelectorAll("[data-open-section]")];
  sections.forEach((section) => {
    const allowed = (section.dataset.openSection || "").split(/\s+/).filter(Boolean);
    section.hidden = allowed.length > 0 && !allowed.includes(target);
  });
}

function wireSkillIndex() {
  const input = document.querySelector("[data-skill-search]");
  const cards = [...document.querySelectorAll("[data-skill-card]")];
  const filters = [...document.querySelectorAll("[data-skill-filter]")];
  const empty = document.querySelector("[data-skill-empty]");
  const count = document.querySelector("[data-skill-count]");
  if (!cards.length) return;
  let activeFilter = "all";
  const render = () => {
    const query = (input?.value || "").trim().toLowerCase();
    let shown = 0;
    cards.forEach((card) => {
      const matchesQuery = !query || card.textContent.toLowerCase().includes(query);
      const matchesFilter = activeFilter === "all" || card.dataset.skillType === activeFilter;
      card.hidden = !(matchesQuery && matchesFilter);
      if (!card.hidden) shown += 1;
    });
    if (count) count.textContent = String(shown);
    if (empty) empty.hidden = shown !== 0;
  };
  input?.addEventListener("input", render);
  filters.forEach((filter) => filter.addEventListener("click", () => {
    activeFilter = filter.dataset.skillFilter || "all";
    filters.forEach((item) => {
      const active = item === filter;
      item.classList.toggle("is-active", active);
      item.setAttribute("aria-pressed", String(active));
    });
    render();
  }));
  render();
}

function wireEditorialReveal() {
  const nodes = [...document.querySelectorAll("[data-reveal]")];
  if (!nodes.length) return;
  if (!("IntersectionObserver" in window)) {
    nodes.forEach((node) => node.classList.add("is-visible"));
    return;
  }
  const observer = new IntersectionObserver((entries, current) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("is-visible");
      current.unobserve(entry.target);
    });
  }, { threshold: 0.12 });
  nodes.forEach((node) => observer.observe(node));
}

function wireShowcase() {
  const root = document.querySelector("[data-showcase-carousel]");
  if (!root) return;
  const slides = [...root.querySelectorAll("[data-showcase-slide]")];
  const status = root.querySelector("[data-showcase-status]");
  const setSlide = (index) => {
    const current = (index + slides.length) % slides.length;
    slides.forEach((slide, item) => {
      const active = item === current;
      slide.hidden = !active;
      slide.setAttribute("aria-hidden", String(!active));
    });
    if (status) status.textContent = `${String(current + 1).padStart(2, "0")} / ${String(slides.length).padStart(2, "0")}`;
  };
  root.querySelector("[data-carousel-prev]")?.addEventListener("click", () => setSlide(slides.findIndex((slide) => !slide.hidden) - 1));
  root.querySelector("[data-carousel-next]")?.addEventListener("click", () => setSlide(slides.findIndex((slide) => !slide.hidden) + 1));
  setSlide(0);
}

renderHeader();
renderFooter();
wireLinks();
wireCatalog();
wireResponsiveTables();
wireOpenTabs();
wireSkillIndex();
wireEditorialReveal();
wireShowcase();
