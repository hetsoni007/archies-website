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
    const price = form.dataset.price ? `\nPrice: ${form.dataset.price}` : "";
    const msg =
      `Hi Aarchi's! I'd like to enquire about this design:\n` +
      `*${form.dataset.name}* (${form.dataset.cat})` +
      price + `\n` +
      `Occasion: ${f.get("occasion")}\n` +
      `Size: ${f.get("size")}\n` +
      `Style preference: ${f.get("style")}` +
      notes + name +
      `\n\n(via website — ${location.origin}${location.pathname})`;
    window.open(`https://wa.me/${WA_NUMBER}?text=${encodeURIComponent(msg)}`, "_blank", "noopener");
  });
}

/* ---------------------- per-design share (native sheet + fallback menu) --- */
function initShare() {
  const wrap = document.querySelector(".design-share");
  if (!wrap) return;
  const btn = wrap.querySelector(".share-btn");
  const menu = wrap.querySelector(".share-menu");
  const backdrop = wrap.querySelector(".share-backdrop");
  const toast = wrap.querySelector(".share-toast");
  const slug = (location.pathname.match(/\/catalogue\/([^/]+)\//) || [])[1] || "";
  const ev = (name, params) => { try { if (window.track) track(name, params); } catch (e) {} };

  function openMenu() { menu.hidden = false; backdrop.hidden = false; btn.setAttribute("aria-expanded", "true"); }
  function closeMenu() { menu.hidden = true; backdrop.hidden = true; btn.setAttribute("aria-expanded", "false"); }

  // Pre-fetch the product image in the background (not on tap) so a native share can
  // attach it as a file. Fetching it *after* the tap and awaiting it before calling
  // navigator.share() was the bug: browsers require share() to run on the same user
  // gesture, and an await in between drops that activation, so navigator.share()
  // silently rejects and the button looks unresponsive. Fetching ahead of time keeps
  // the actual share() call synchronous with the click.
  const shareTitle = btn.dataset.shareTitle, shareUrl = btn.dataset.shareUrl;
  let sharedFile = null;
  if (navigator.share && navigator.canShare && btn.dataset.shareImg) {
    fetch(btn.dataset.shareImg)
      .then(res => res.blob())
      .then(blob => {
        const file = new File([blob], "aarchis-design.webp", { type: blob.type || "image/webp" });
        // Validate the FULL shape (title + url + files together) up front — sharing just
        // {files} was the other bug: it silently dropped the product URL from every
        // native share once an image was attached, since {title, files} alone was sent.
        if (navigator.canShare({ title: shareTitle, url: shareUrl, files: [file] })) sharedFile = file;
      })
      .catch(() => { /* prefetch failed — link-only share still works */ });
  }

  function nativeShare() {
    const data = sharedFile
      ? { title: shareTitle, url: shareUrl, files: [sharedFile] }
      : { title: shareTitle, url: shareUrl };
    navigator.share(data)
      .then(() => ev("share_click", { method: "native", design_slug: slug }))
      .catch(() => { /* user cancelled the share sheet — no-op */ });
  }

  btn.addEventListener("click", () => {
    // Fires on every tap, regardless of whether a share is completed — the
    // top-of-funnel signal for "Share was opened", distinct from share_click below
    // which only fires once a destination is actually used.
    ev("share_open", { design_slug: slug });
    if (navigator.share) { nativeShare(); return; }
    menu.hidden ? openMenu() : closeMenu();
  });

  menu.querySelectorAll("a.share-opt").forEach(a =>
    a.addEventListener("click", () => ev("share_click", { method: a.dataset.net, design_slug: slug })));

  const copyBtn = menu.querySelector('[data-net="copy"]');
  if (copyBtn) copyBtn.addEventListener("click", async () => {
    let ok = true;
    try { await navigator.clipboard.writeText(btn.dataset.shareUrl); }
    catch (e) { ok = false; }
    toast.textContent = ok ? "Link copied" : "Couldn't copy — long-press the address bar";
    toast.hidden = false;
    ev("share_click", { method: "copy_link", design_slug: slug });
    closeMenu();
    setTimeout(() => { toast.hidden = true; }, 2400);
  });

  const closeBtn = menu.querySelector(".share-close");
  if (closeBtn) closeBtn.addEventListener("click", closeMenu);
  backdrop.addEventListener("click", closeMenu);
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeMenu(); });
}

document.addEventListener("DOMContentLoaded", () => {
  initCatalogue();
  initDesignEnquiry();
  initShare();
});
