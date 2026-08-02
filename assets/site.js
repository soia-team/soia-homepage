document.documentElement.classList.add("js");

const NAV_ITEMS = {
  zh: [
    ["products", "产品体系", "/products/"],
    ["open", "开放生态", "/open/"],
    ["course", "课程", "/course/"],
    ["services", "服务与合作", "/services/"],
    ["docs", "资源", "/docs/"],
    ["about", "关于", "/about/"],
  ],
  en: [
    ["products", "Products", "/en/products/"],
    ["open", "Open ecosystem", "/en/open/"],
    ["course", "Course", "/en/course/"],
    ["services", "Services", "/en/services/"],
    ["docs", "Resources", "/en/docs/"],
    ["about", "About", "/en/about/"],
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
  const current = document.body.dataset.page || "home";
  const locale = getLocale();
  const copy = locale === "en"
    ? { home: "SOIA home", menu: "Menu", nav: "Primary navigation", start: "Explore ecosystem", language: "中文", languageLabel: "切换到中文" }
    : { home: "SOIA 首页", menu: "菜单", nav: "主导航", start: "进入开放生态", language: "EN", languageLabel: "Switch to English" };
  const links = NAV_ITEMS[locale].map(
    ([id, label, href]) =>
      `<a href="${href}" ${id === current ? 'aria-current="page"' : ""}>${label}</a>`
  ).join("");

  host.innerHTML = `
    <header class="site-header">
      <div class="shell header-inner">
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
  button?.addEventListener("click", () => {
    const open = button.getAttribute("aria-expanded") === "true";
    button.setAttribute("aria-expanded", String(!open));
    nav?.classList.toggle("is-open", !open);
  });
}

function renderFooter() {
  const host = document.querySelector("[data-site-footer]");
  if (!host) return;
  const locale = getLocale();
  const en = locale === "en";
  host.innerHTML = `
    <footer class="site-footer">
      <div class="shell footer-signal">
        <div class="footer-signal-title"><p class="eyebrow">SOIA / BUILD WITH CLARITY</p><h2>${en ? "One task can become a durable capability." : "从一个任务开始，做成可持续的能力。"}</h2></div>
        <div class="footer-signal-actions"><a class="button button--light" href="${en ? "/en/open/" : "/open/"}">${en ? "Explore the ecosystem" : "浏览开放生态"}</a><a class="footer-text-link" href="${en ? "/en/docs/" : "/docs/"}">${en ? "Read the docs" : "阅读资源"} <span aria-hidden="true">↗</span></a></div>
      </div>
      <div class="shell footer-bottom footer-bottom--signal">
        <a class="brand brand--footer" href="${en ? "/en/" : "/"}"><span class="brand-mark" aria-hidden="true"><i></i><i></i><i></i></span><span>SOIA</span></a>
        <span>© <span data-year></span> SOIA Team</span>
        <span>${en ? "Open methods · Scoped private delivery" : "公开方法 · 有边界的私有交付"}</span>
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
  const firstVisible = document.getElementById(target)?.hidden ? null : document.getElementById(target) || sections.find((section) => !section.hidden);
  if (firstVisible && target !== "overview") {
    window.requestAnimationFrame(() => firstVisible.scrollIntoView({ block: "start" }));
  }
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
