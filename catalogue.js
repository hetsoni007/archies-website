/* =========================================================================
   Aarchi's — catalogue filtering + per-design WhatsApp enquiry
   ========================================================================= */
const WA_NUMBER = "919879390731";

/* ---------------------- catalogue filtering ---------------------- */
function initCatalogue() {
  const grid = document.getElementById("dgrid");
  if (!grid) return;
  const cards = Array.from(grid.querySelectorAll(".dcard"));
  const countEl = document.getElementById("cat-count");
  const emptyEl = document.getElementById("cat-empty");
  const state = { cat: "all", occ: "all", sty: "all" };

  function apply() {
    let shown = 0;
    cards.forEach(c => {
      const okCat = state.cat === "all" || c.dataset.cat === state.cat;
      const okOcc = state.occ === "all" || (" " + c.dataset.occ + " ").includes(" " + state.occ + " ");
      const okSty = state.sty === "all" || (" " + c.dataset.sty + " ").includes(" " + state.sty + " ");
      const ok = okCat && okOcc && okSty;
      c.hidden = !ok;
      if (ok) shown++;
    });
    if (countEl) countEl.textContent = shown + (shown === 1 ? " design" : " designs");
    if (emptyEl) emptyEl.hidden = shown !== 0;
  }

  grid.parentElement.parentElement; // noop
  document.querySelectorAll('.fpill[data-filter="cat"]').forEach(b => {
    b.addEventListener("click", () => {
      document.querySelectorAll('.fpill[data-filter="cat"]').forEach(x => x.classList.remove("active"));
      b.classList.add("active");
      state.cat = b.dataset.val;
      apply();
    });
  });
  const occSel = document.getElementById("f-occ");
  const stySel = document.getElementById("f-sty");
  if (occSel) occSel.addEventListener("change", () => { state.occ = occSel.value; apply(); });
  if (stySel) stySel.addEventListener("change", () => { state.sty = stySel.value; apply(); });
  const clear = document.getElementById("f-clear");
  if (clear) clear.addEventListener("click", () => {
    state.cat = state.occ = state.sty = "all";
    document.querySelectorAll('.fpill[data-filter="cat"]').forEach(x => x.classList.toggle("active", x.dataset.val === "all"));
    if (occSel) occSel.value = "all";
    if (stySel) stySel.value = "all";
    apply();
  });
  apply();
}

/* ---------------------- per-design enquiry → WhatsApp ---------------------- */
function initDesignEnquiry() {
  const form = document.getElementById("design-enquiry");
  if (!form) return;
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const f = new FormData(form);
    const name = f.get("name") ? `\nName: ${f.get("name")}` : "";
    const notes = f.get("notes") ? `\nCustomisation: ${f.get("notes")}` : "";
    const msg =
      `Hi Aarchi's! I'd like to enquire about this design:\n` +
      `*${form.dataset.name}* (${form.dataset.cat})\n` +
      `Occasion: ${f.get("occasion")}\n` +
      `Size: ${f.get("size")}\n` +
      `Style preference: ${f.get("style")}` +
      notes + name +
      `\n\n(via website — ${location.origin}${location.pathname})`;
    window.open(`https://wa.me/${WA_NUMBER}?text=${encodeURIComponent(msg)}`, "_blank", "noopener");
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initCatalogue();
  initDesignEnquiry();
});
