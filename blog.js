"use strict";

const search = document.querySelector("#note-search");
const rows = [...document.querySelectorAll("[data-note]")];
function filterNotes() {
  if (!search) return;
  const query = search.value.trim().toLocaleLowerCase();
  let count = 0;
  for (const row of rows) {
    row.hidden = !row.dataset.search.toLocaleLowerCase().includes(query);
    if (!row.hidden) count++;
  }
  const en = document.documentElement.lang === "en";
  search.placeholder = en ? "Title, summary, or tag" : "标题、简介或标签";
  document.querySelector("#note-count").textContent = en ? `${count} note${count === 1 ? "" : "s"}` : `${count} 篇随笔`;
  document.querySelector("#search-empty").hidden = count !== 0;
}
search?.addEventListener("input", filterNotes);
document.addEventListener("languagechange", filterNotes);
filterNotes();
