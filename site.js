"use strict";

const root = document.documentElement;
const languageButton = document.querySelector("#language");
const themeButton = document.querySelector("#theme");
const menuButton = document.querySelector("#menu");
const navigation = document.querySelector("#navigation");
const translations = [...document.querySelectorAll("[data-en]")];
const accessibleTranslations = [...document.querySelectorAll("[data-en-aria]")];
const chineseText = new Map(translations.map(node => [node, node.innerHTML]));
const chineseAria = new Map(accessibleTranslations.map(node => [node, node.getAttribute("aria-label")]));
let language = "zh";

function remember(key, value) {
  try { localStorage.setItem(key, value); } catch (_) { /* The page also works without browser storage. */ }
}

function syncControls() {
  const isDark = root.dataset.theme === "dark";
  const themeLabel = language === "en"
    ? `Switch to ${isDark ? "light" : "dark"} mode`
    : `切换到${isDark ? "浅" : "深"}色模式`;
  themeButton.setAttribute("aria-label", themeLabel);
  themeButton.title = themeLabel;
  themeButton.setAttribute("aria-pressed", String(isDark));
  menuButton.setAttribute("aria-label", language === "en"
    ? (navigation.classList.contains("open") ? "Close navigation" : "Open navigation")
    : (navigation.classList.contains("open") ? "关闭导航菜单" : "打开导航菜单"));
}

function setLanguage(next) {
  language = next === "en" ? "en" : "zh";
  root.lang = language === "en" ? "en" : "zh-CN";
  for (const node of translations) {
    if (language === "en") node.textContent = node.dataset.en;
    else node.innerHTML = chineseText.get(node);
  }
  for (const node of accessibleTranslations) {
    node.setAttribute("aria-label", language === "en" ? node.dataset.enAria : chineseAria.get(node));
  }
  languageButton.textContent = language === "en" ? "中" : "EN";
  languageButton.setAttribute("aria-label", language === "en" ? "切换到中文" : "Switch to English");
  languageButton.title = languageButton.getAttribute("aria-label");
  document.title = language === "en" ? "Junbo Zhou · Full-stack Developer" : "周俊博 · 全栈开发工程师";
  syncControls();
  remember("canoe-language", language);
}

languageButton.addEventListener("click", () => setLanguage(language === "zh" ? "en" : "zh"));
themeButton.addEventListener("click", () => {
  root.dataset.theme = root.dataset.theme === "dark" ? "light" : "dark";
  document.querySelector('meta[name="theme-color"]').content = root.dataset.theme === "dark" ? "#111112" : "#f7f5f1";
  remember("canoe-theme", root.dataset.theme);
  syncControls();
});

function closeMenu() {
  navigation.classList.remove("open");
  menuButton.setAttribute("aria-expanded", "false");
  syncControls();
}
menuButton.addEventListener("click", () => {
  const open = navigation.classList.toggle("open");
  menuButton.setAttribute("aria-expanded", String(open));
  syncControls();
});
navigation.addEventListener("click", event => { if (event.target.closest("a")) closeMenu(); });
document.addEventListener("keydown", event => {
  if (event.key === "Escape" && navigation.classList.contains("open")) { closeMenu(); menuButton.focus(); }
});
document.addEventListener("click", event => {
  if (!event.target.closest(".header")) closeMenu();
});

const navigationLinks = [...navigation.querySelectorAll("a")];
const sections = navigationLinks.map(link => document.querySelector(link.hash));
let scrollScheduled = false;
function updateScroll() {
  const top = window.scrollY;
  const total = root.scrollHeight - window.innerHeight;
  document.querySelector(".reading-progress").style.width = `${total > 0 ? Math.min(100, top / total * 100) : 0}%`;
  let current = "";
  for (const section of sections) {
    if (section.getBoundingClientRect().top <= 160) current = section.id;
  }
  if (total > 0 && top >= total - 20) current = "contact";
  for (const link of navigationLinks) {
    if (link.hash === `#${current}`) link.setAttribute("aria-current", "location");
    else link.removeAttribute("aria-current");
  }
  scrollScheduled = false;
}
window.addEventListener("scroll", () => {
  if (!scrollScheduled) { scrollScheduled = true; requestAnimationFrame(updateScroll); }
}, { passive: true });
window.addEventListener("resize", updateScroll, { passive: true });

let detailsBeforePrint;
window.addEventListener("beforeprint", () => {
  detailsBeforePrint = [...document.querySelectorAll("details")].map(node => [node, node.open]);
  for (const [node] of detailsBeforePrint) node.open = true;
});
window.addEventListener("afterprint", () => {
  if (detailsBeforePrint) for (const [node, open] of detailsBeforePrint) node.open = open;
});
document.querySelector("#print").addEventListener("click", () => window.print());

let toastTimeout;
document.querySelector("#copy-email").addEventListener("click", async () => {
  const toast = document.querySelector("#toast");
  try {
    await navigator.clipboard.writeText("760548276@qq.com");
    toast.textContent = language === "en" ? "Email copied." : "邮箱地址已复制。";
  } catch (_) {
    toast.textContent = language === "en" ? "Please select and copy the email above." : "请选中上方邮箱地址手动复制。";
  }
  clearTimeout(toastTimeout);
  toast.classList.add("visible");
  toastTimeout = setTimeout(() => toast.classList.remove("visible"), 3000);
});

try { if (localStorage.getItem("canoe-language") === "en") setLanguage("en"); } catch (_) { /* Optional preference. */ }
syncControls();
updateScroll();
