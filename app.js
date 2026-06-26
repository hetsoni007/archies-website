/* =========================================================================
   Aarchi's by Archana Soni — interactions + content data
   No dependencies, no build step. ~3kb.
   ========================================================================= */

/* ----------------------------------------------------------------------
   COLLECTIONS — single source of truth for the lookbook.
   Categories below are REAL — derived from the studio's own Instagram posts.
   `img` is still null (no photos yet) so a styled "photo" placeholder tile
   renders; set `img` to a path under assets/img/... once real photography
   is added. To add/remove a category, copy or delete a block.
   ---------------------------------------------------------------------- */
const COLLECTIONS = [
  { name: "Bridal Lehengas",        tagline: "Handcrafted zari, zardozi & khat work", img: null },
  { name: "Sarees",                 tagline: "Silk, paithani & bandhej drapes",       img: null },
  { name: "Ethnic & Festive Wear",  tagline: "Navratri and occasion ensembles",        img: null },
  { name: "Baby Shower & Maternity",tagline: "Bespoke outfits for the mom-to-be",       img: null },
  { name: "Men's Ethnic Wear",      tagline: "Festive & wedding looks",                 img: null },
  { name: "Custom Couture",         tagline: "Made to measure, designed around you",    img: null },
];

function renderCollections(targetId, limit) {
  const el = document.getElementById(targetId);
  if (!el) return;
  const items = limit ? COLLECTIONS.slice(0, limit) : COLLECTIONS;
  el.innerHTML = items.map(c => `
    <article class="coll-card" data-reveal>
      ${c.img
        ? `<img src="${c.img}" alt="${c.name} — Aarchi's by Archana Soni" loading="lazy" width="600" height="800">`
        : `<div class="ph" role="img" aria-label="${c.name} photo placeholder"></div>`}
      <div class="cap">
        <h3>${c.name}</h3>
        <span>${c.tagline}</span>
      </div>
    </article>`).join("");
  observeReveals();
}

/* ---------------------- reveal-on-scroll ---------------------- */
let _io;
function observeReveals() {
  if (!_io) {
    _io = new IntersectionObserver((entries) => {
      entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add("in"); _io.unobserve(e.target); } });
    }, { threshold: 0.12, rootMargin: "0px 0px -8% 0px" });
  }
  document.querySelectorAll("[data-reveal]:not(.in)").forEach(n => _io.observe(n));
}

/* ---------------------- mobile nav ---------------------- */
function initNav() {
  const burger = document.querySelector(".burger");
  const links = document.querySelector(".nav-links");
  if (!burger || !links) return;
  burger.addEventListener("click", () => links.classList.toggle("open"));
  links.querySelectorAll("a").forEach(a => a.addEventListener("click", () => links.classList.remove("open")));
}

/* ---------------------- contact form (placeholder) ---------------------- */
/* Currently a no-op stub. Wire `ENQUIRY_ENDPOINT` to a backend (e.g. an
   API Gateway → Lambda → SES like the SCS site) OR keep WhatsApp-only and
   delete the form. */
const ENQUIRY_ENDPOINT = null; // TODO: set when backend exists
function initForm() {
  const form = document.getElementById("enquiry-form");
  if (!form) return;
  form.addEventListener("submit", (ev) => {
    ev.preventDefault();
    const note = form.querySelector(".form-note");
    if (!ENQUIRY_ENDPOINT) {
      if (note) note.textContent = "Form backend not connected yet — for now please reach us on WhatsApp. (Dev note: set ENQUIRY_ENDPOINT in app.js.)";
      return;
    }
    /* fetch(ENQUIRY_ENDPOINT, { method: "POST", body: new FormData(form) }) ... */
  });
}

/* ---------------------- boot ---------------------- */
document.addEventListener("DOMContentLoaded", () => {
  renderCollections("coll-featured", 3);
  renderCollections("coll-all");
  observeReveals();
  initNav();
  initForm();
  const y = document.getElementById("year"); if (y) y.textContent = new Date().getFullYear();
});
