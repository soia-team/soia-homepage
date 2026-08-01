const tabs = Array.from(document.querySelectorAll(".capability-tab"));
const panels = Array.from(document.querySelectorAll("[data-panel]"));

function activateCapability(name) {
  tabs.forEach((tab) => {
    const active = tab.dataset.target === name;
    tab.classList.toggle("is-active", active);
    tab.setAttribute("aria-selected", String(active));
    tab.tabIndex = active ? 0 : -1;
  });

  panels.forEach((panel) => {
    panel.hidden = panel.dataset.panel !== name;
  });
}

tabs.forEach((tab, index) => {
  tab.addEventListener("click", () => activateCapability(tab.dataset.target));
  tab.addEventListener("keydown", (event) => {
    if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
    event.preventDefault();
    let next = index;
    if (event.key === 'ArrowLeft') next = (index - 1 + tabs.length) % tabs.length;
    if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = tabs.length - 1;
    tabs[next].focus();
    activateCapability(tabs[next].dataset.target);
  });
});

const year = document.getElementById("year");
if (year) year.textContent = String(new Date().getFullYear());
