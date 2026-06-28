/* =========================================================================
   Aarchi's — catalogue filtering + per-design WhatsApp enquiry
   ========================================================================= */
const WA_NUMBER = "919879390731";

/* ---------------------- catalogue: category sections + refine + scroll-spy --------------- */
function initCatalogue() {
  const wrap = document.getElementById("catsecs");
  if (!wrap) return;
  const secs = Array.from(wrap.querySelectorAll(".catsec"));
  const cards = Array.from(wrap.querySelectorAll(".dcard"));
  const links = Array.from(document.querySelectorAll(".catnav-link"));
  const occSel = document.getElementById("f-occ");
  const stySel = document.getElementById("f-sty");
  const clear = document.getElementById("f-clear");
  const countEl = document.getElementById("cat-count");
  const emptyEl = document.getElementById("cat-empty");
  const state = { occ: "all", sty: "all" };

  function apply() {
    let shown = 0;
    cards.forEach(c => {
      const okOcc = state.occ === "all" || (" " + c.dataset.occ + " ").includes(" " + state.occ + " ");
      const okSty = state.sty === "all" || (" " + c.dataset.sty + " ").includes(" " + state.sty + " ");
      const ok = okOcc && okSty;
      c.hidden = !ok;
      if (ok) shown++;
    });
    // hide whole category sections (and dim their nav link) when they have no matches
    secs.forEach(s => {
      const any = s.querySelector(".dcard:not([hidden])");
      s.hidden = !any;
      if (any) s.querySelectorAll("[data-reveal]").forEach(e => e.classList.add("in"));
      const link = links.find(l => l.dataset.sec === s.id);
      if (link) link.classList.toggle("off", !any);
    });
    const filtering = state.occ !== "all" || state.sty !== "all";
    if (countEl) countEl.textContent = filtering ? shown + (shown === 1 ? " design" : " designs") : "";
    if (emptyEl) emptyEl.hidden = shown !== 0;
  }

  if (occSel) occSel.addEventListener("change", () => { state.occ = occSel.value; apply(); });
  if (stySel) stySel.addEventListener("change", () => { state.sty = stySel.value; apply(); });
  if (clear) clear.addEventListener("click", () => {
    state.occ = state.sty = "all";
    if (occSel) occSel.value = "all";
    if (stySel) stySel.value = "all";
    apply();
  });

  // scroll-spy: highlight the catnav link for the section currently in view
  if ("IntersectionObserver" in window && links.length) {
    const spy = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          links.forEach(l => l.classList.remove("active"));
          const l = links.find(x => x.dataset.sec === e.target.id);
          if (l) l.classList.add("active");
        }
      });
    }, { rootMargin: "-45% 0px -50% 0px", threshold: 0 });
    secs.forEach(s => spy.observe(s));
  }

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
