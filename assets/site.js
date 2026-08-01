const NAV_ITEMS = {
  zh: [
    ["home", "首页", "/"],
    ["open", "开源能力", "/open/"],
    ["products", "产品", "/products/"],
    ["course", "课程", "/course/"],
    ["services", "服务", "/services/"],
    ["about", "关于", "/about/"],
  ],
  en: [
    ["home", "Home", "/en/"],
    ["open", "Open", "/en/open/"],
    ["products", "Products", "/en/products/"],
    ["course", "Course", "/en/course/"],
    ["services", "Services", "/en/services/"],
    ["about", "About", "/en/about/"],
  ],
};

const REQUEST_URL =
  "https://github.com/soia-team/soia-open-skills/issues/new?title=%5BSOIA%20%E6%B5%81%E7%A8%8B%E8%AF%8A%E6%96%AD%5D&body=%E8%AF%B7%E5%8F%AA%E5%A1%AB%E5%86%99%E9%9D%9E%E6%95%8F%E6%84%9F%E4%BF%A1%E6%81%AF%EF%BC%9A%0A-%20%E6%83%B3%E8%A6%81%E6%94%B9%E9%80%A0%E7%9A%84%E5%B7%A5%E4%BD%9C%EF%BC%9A%0A-%20%E5%BD%93%E5%89%8D%E8%BE%93%E5%85%A5%E4%B8%8E%E8%BE%93%E5%87%BA%EF%BC%9A%0A-%20%E4%BD%BF%E7%94%A8%E7%9A%84%E5%AE%BF%E4%B8%BB%EF%BC%9A%0A-%20%E8%B5%84%E6%96%99%E6%95%8F%E6%84%9F%E5%BA%A6%EF%BC%9A";
const COURSE_URL =
  "https://github.com/soia-team/soia-open-skills/issues/new?title=%5BSOIA%20%E8%AF%BE%E7%A8%8B%E9%A6%96%E6%9C%9F%E7%94%B3%E8%AF%B7%5D&body=%E8%AF%B7%E5%8F%AA%E5%A1%AB%E5%86%99%E9%9D%9E%E6%95%8F%E6%84%9F%E4%BF%A1%E6%81%AF%EF%BC%9A%0A-%20%E4%BD%A0%E6%83%B3%E5%B0%81%E8%A3%85%E7%9A%84%E9%87%8D%E5%A4%8D%E5%B7%A5%E4%BD%9C%EF%BC%9A%0A-%20%E7%9B%AE%E5%89%8D%E4%BD%BF%E7%94%A8%E7%9A%84%20AI%20%E5%B7%A5%E5%85%B7%EF%BC%9A%0A-%20%E6%98%AF%E5%90%A6%E6%9C%89%E5%8F%AF%E7%94%A8%E7%9A%84%20SOP%EF%BC%9A";

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
    ? { home: "SOIA home", menu: "Menu", nav: "Primary navigation", start: "Start with Open", language: "中文", languageLabel: "切换到中文" }
    : { home: "SOIA 首页", menu: "菜单", nav: "主导航", start: "从 Open 开始", language: "EN", languageLabel: "Switch to English" };
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
      <div class="shell footer-grid">
        <div>
          <a class="brand brand--footer" href="${en ? "/en/" : "/"}">
            <span class="brand-mark" aria-hidden="true"><i></i><i></i><i></i></span>
            <span>SOIA</span>
          </a>
          <p>System · Orchestration · Intelligence · Assurance</p>
        </div>
        <div><strong>${en ? "Explore" : "探索"}</strong><a href="${en ? "/en/open/" : "/open/"}">Open</a><a href="${en ? "/en/products/" : "/products/"}">Products</a><a href="${en ? "/en/course/" : "/course/"}">Course</a></div>
        <div><strong>${en ? "Work with us" : "合作"}</strong><a href="${en ? "/en/services/" : "/services/"}">Services</a><a href="${en ? "/en/about/" : "/about/"}">About</a><a href="https://github.com/soia-team" target="_blank" rel="noreferrer">GitHub ↗</a></div>
        <div><strong>${en ? "Boundaries" : "边界"}</strong><span>Local-first</span><span>Human-controlled</span><span>Evidence-backed</span></div>
      </div>
      <div class="shell footer-bottom">
        <span>© <span data-year></span> SOIA Team</span>
        <span>${en ? "MIT licensed website · No passwords, tokens, or cookies collected" : "MIT licensed website · 不收集密码、Token 或 Cookie"}</span>
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

renderHeader();
renderFooter();
wireLinks();
wireCatalog();
wireResponsiveTables();
