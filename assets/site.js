document.documentElement.classList.add("js");

const NAV_ITEMS = {
  zh: [
    ["products", "产品", "/products/"],
    ["showcase", "展示", "/showcase/"],
    ["pricing", "价格", "/pricing/"],
    ["docs", "文档", "/docs/"],
    ["spec", "规格", "/spec/"],
    ["about", "关于", "/about/"],
  ],
  en: [
    ["products", "Products", "/en/products/"],
    ["showcase", "Showcase", "/en/showcase/"],
    ["pricing", "Pricing", "/en/pricing/"],
    ["docs", "Docs", "/en/docs/"],
    ["spec", "Spec", "/en/spec/"],
    ["about", "About", "/en/about/"],
  ],
};

const REQUEST_URL = "/";
const COURSE_URL = "/";
const TEMPLATE_PAGES = new Set(["home", "products", "pricing", "showcase", "docs", "spec"]);

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
    ? { home: "Studio home", menu: "Menu", nav: "Primary navigation", start: "View prototype", language: "中文", languageLabel: "切换到中文" }
    : { home: "Studio 首页", menu: "菜单", nav: "主导航", start: "查看原型", language: "EN", languageLabel: "Switch to English" };
  const links = NAV_ITEMS[locale].map(
    ([id, label, href]) =>
      `<a href="${href}" ${id === current ? 'aria-current="page"' : ""}>${label}</a>`
  ).join("");

  host.innerHTML = `
    <header class="site-header">
      <div class="shell header-inner">
        <a class="brand" href="${locale === "en" ? "/en/" : "/"}" aria-label="${copy.home}">
          <span class="brand-mark" aria-hidden="true"><i></i><i></i><i></i></span>
          <span>STUDIO</span>
        </a>
        <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">
          <span>${copy.menu}</span><i aria-hidden="true"></i>
        </button>
        <nav class="site-nav" id="site-nav" aria-label="${copy.nav}">${links}</nav>
        <div class="header-actions">
          <a class="language-switch" href="${languageTarget(locale)}" hreflang="${locale === "en" ? "zh-CN" : "en"}" aria-label="${copy.languageLabel}">${copy.language}</a>
          <a class="button button--small button--ink header-action" href="${locale === "en" ? "/en/products/" : "/products/"}">${copy.start}</a>
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
      <div class="shell footer-grid">
        <div>
          <a class="brand brand--footer" href="${en ? "/en/" : "/"}">
            <span class="brand-mark" aria-hidden="true"><i></i><i></i><i></i></span>
            <span>STUDIO</span>
          </a>
          <p>${en ? "A neutral interface prototype" : "一个中性界面原型"}</p>
        </div>
        <div><strong>${en ? "Explore" : "浏览"}</strong><a href="${en ? "/en/products/" : "/products/"}">${en ? "Products" : "产品"}</a><a href="${en ? "/en/showcase/" : "/showcase/"}">${en ? "Showcase" : "展示"}</a><a href="${en ? "/en/pricing/" : "/pricing/"}">${en ? "Pricing" : "价格"}</a></div>
        <div><strong>${en ? "Reference" : "参考"}</strong><a href="${en ? "/en/docs/" : "/docs/"}">${en ? "Docs" : "文档"}</a><a href="${en ? "/en/spec/" : "/spec/"}">${en ? "Spec" : "规格"}</a><a href="${en ? "/en/about/" : "/about/"}">${en ? "About" : "关于"}</a></div>
        <div><strong>${en ? "Template status" : "模板状态"}</strong><span>${en ? "Content removed" : "业务内容已移除"}</span><span>${en ? "Ready for replacement" : "等待替换真实内容"}</span></div>
      </div>
      <div class="shell footer-bottom">
        <span>© <span data-year></span> Studio prototype</span>
        <span>${en ? "Temporary content-free presentation" : "临时无业务内容展示"}</span>
      </div>
    </footer>`;
}

function renderTemplateFallback() {
  const current = document.body.dataset.page || "home";
  if (TEMPLATE_PAGES.has(current)) return;
  const locale = getLocale();
  const en = locale === "en";
  const main = document.querySelector("main");
  if (!main) return;
  document.body.classList.add("template-mode");
  document.title = en ? "STUDIO | Interface prototype" : "STUDIO｜界面原型";
  document.querySelector('meta[name="description"]')?.setAttribute("content", en ? "A content-free interface prototype." : "暂时移除业务内容的界面原型。 ");
  main.innerHTML = `
    <section class="template-fallback" aria-labelledby="template-fallback-title">
      <div class="template-fallback-grid" aria-hidden="true"></div>
      <div class="shell template-fallback-content">
        <p class="eyebrow">${en ? "TEMPLATE MODE / CONTENT ON HOLD" : "模板状态 / 内容暂缓"}</p>
        <div class="template-fallback-plate"><h1 id="template-fallback-title">${en ? "This page is a frame." : "这一页目前只保留框架。"}</h1></div>
        <p>${en ? "The production copy, products, pricing, and case material are intentionally hidden while the site structure is being rebuilt." : "在站点结构重做期间，产品、价格、案例和业务说明均暂时隐藏；这里保留的是可继续替换的页面骨架。"}</p>
        <a class="button button--ink" href="${en ? "/en/" : "/"}">${en ? "Back to the prototype" : "返回原型首页"}</a>
      </div>
    </section>`;
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

renderTemplateFallback();
renderHeader();
renderFooter();
wireLinks();
wireCatalog();
wireResponsiveTables();
wireOpenTabs();
wireSkillIndex();
wireEditorialReveal();
wireShowcase();
