/* =========================================================================
   Aarchi's by Archana Soni — interactions + content data
   No dependencies, no build step. Respects prefers-reduced-motion.
   ========================================================================= */

/* ----------------------------------------------------------------------
   COLLECTIONS — single source of truth for the lookbook.
   Categories AND photos are REAL — from the studio's own Instagram (see
   assets/img/SOURCES.md for per-image source posts + credits). To swap a
   photo, replace the file in assets/img/ or change `img`. Set `img: null`
   to fall back to a styled "photo" placeholder tile. Add/remove = copy/delete.
   ---------------------------------------------------------------------- */
const COLLECTIONS = [
  { name: "Bridal Lehengas",        tagline: "Handcrafted zari, zardozi & khat work", img: "/assets/img/bridal-lehengas.webp" },
  { name: "Sarees",                 tagline: "Silk, paithani & bandhej drapes",       img: "/assets/img/sarees.webp" },
  { name: "Ethnic & Festive Wear",  tagline: "Navratri and occasion ensembles",        img: "/assets/img/ethnic-festive.webp" },
  { name: "Baby Shower & Maternity",tagline: "Bespoke outfits for the mom-to-be",       img: "/assets/img/baby-shower.webp" },
  { name: "Men's Ethnic Wear",      tagline: "Festive & wedding looks",                 img: "/assets/img/mens-ethnic.webp" },
  { name: "Custom Couture",         tagline: "Made to measure, designed around you",    img: "/assets/img/custom-couture.webp" },
];

function collCard(c, i) {
  const n = String(i + 1).padStart(2, "0");
  const media = c.img
    ? `<div class="coll-media"><img src="${c.img}" alt="${c.name} — Aarchi's by Archana Soni" loading="lazy" width="600" height="800"></div>`
    : `<div class="coll-media"><div class="ph" role="img" aria-label="${c.name} photo placeholder"></div></div>`;
  return `<a class="coll-card" href="/catalogue/" data-reveal style="--i:${i % 3}">
    ${media}
    <span class="coll-index">${n}</span>
    <div class="coll-cap">
      <h3>${c.name}</h3>
      <p>${c.tagline}</p>
      <span class="coll-link">View collection <i>&rarr;</i></span>
    </div>
  </a>`;
}

function renderCollections(targetId, limit) {
  const el = document.getElementById(targetId);
  if (!el) return;
  const items = limit ? COLLECTIONS.slice(0, limit) : COLLECTIONS;
  el.innerHTML = items.map(collCard).join("");
}

/* ---------------------- reveal-on-scroll (with stagger) ---------------------- */
/* Robustness: content is never left hidden. Elements already in view are
   revealed synchronously on load (so above-the-fold never flashes blank);
   the observer only animates elements as they scroll into view; and if there
   is no observer support / no measurable viewport, everything is shown. */
function initReveal() {
  const els = Array.from(document.querySelectorAll("[data-reveal]"));
  const show = (n) => n.classList.add("in");
  const vh = window.innerHeight;
  if (!("IntersectionObserver" in window) || !vh) { els.forEach(show); return; }
  // Reveal anything already on screen right now (don't wait for async IO).
  els.forEach(n => { if (n.getBoundingClientRect().top < vh * 0.95) show(n); });
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) { show(e.target); io.unobserve(e.target); } });
  }, { threshold: 0.12, rootMargin: "0px 0px -8% 0px" });
  els.forEach(n => { if (!n.classList.contains("in")) io.observe(n); });
  // Last-resort self-heal for odd headless/timing states.
  setTimeout(() => { if (!document.querySelector("[data-reveal].in")) els.forEach(show); }, 800);
}

/* ---------------------- scroll engine: progress bar + parallax ---------------------- */
function initScroll() {
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

  const bar = document.createElement("div");
  bar.className = "scrollbar";
  document.body.appendChild(bar);

  const px = reduce ? [] : Array.from(document.querySelectorAll("[data-parallax]"));
  const scrub = reduce ? [] : Array.from(document.querySelectorAll("[data-scrub]"));
  let ticking = false;

  function update() {
    const doc = document.documentElement;
    const vh = window.innerHeight;
    const max = doc.scrollHeight - doc.clientHeight;
    bar.style.width = (max > 0 ? (doc.scrollTop / max) * 100 : 0) + "%";
    if (px.length) {
      const mid = vh / 2;
      for (const el of px) {
        const r = el.getBoundingClientRect();
        const speed = parseFloat(el.dataset.speed || "0.1");
        const y = (mid - (r.top + r.height / 2)) * speed;
        el.style.transform = `translate3d(0, ${y.toFixed(1)}px, 0)`;
      }
    }
    // Apple-style scrub: --p goes 0→1 as the element crosses the viewport
    // (enters bottom = 0, leaves top = 1). Drives scale/parallax in CSS only —
    // never opacity, so content is always visible regardless of scroll.
    for (const el of scrub) {
      const r = el.getBoundingClientRect();
      const p = (vh - r.top) / (vh + r.height);
      el.style.setProperty("--p", Math.max(0, Math.min(1, p)).toFixed(4));
    }
    ticking = false;
  }
  function onScroll() { if (!ticking) { ticking = true; requestAnimationFrame(update); } }

  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll, { passive: true });
  update();
}

/* ---------------------- magnetic buttons (pointer-fine only) ---------------------- */
function initMagnetic() {
  if (matchMedia("(prefers-reduced-motion: reduce)").matches || matchMedia("(hover: none)").matches) return;
  document.querySelectorAll("[data-magnetic]").forEach(b => {
    b.addEventListener("mousemove", (e) => {
      const r = b.getBoundingClientRect();
      b.style.transform = `translate(${(e.clientX - r.left - r.width / 2) * 0.22}px, ${(e.clientY - r.top - r.height / 2) * 0.3}px)`;
    });
    b.addEventListener("mouseleave", () => { b.style.transform = ""; });
  });
}

/* ---------------------- mobile nav ---------------------- */
function initNav() {
  const burger = document.querySelector(".burger");
  const links = document.querySelector(".nav-links");
  if (!burger || !links) return;
  burger.addEventListener("click", () => { links.classList.toggle("open"); burger.classList.toggle("x"); });
  links.querySelectorAll("a").forEach(a => a.addEventListener("click", () => { links.classList.remove("open"); burger.classList.remove("x"); }));
}

/* ---------------------- contact form (placeholder) ---------------------- */
/* Wire `ENQUIRY_ENDPOINT` to a backend (e.g. API Gateway → Lambda → SES like
   the SCS site) OR keep WhatsApp-only and delete the form. */
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

/* ---------------------- GA4 behavior events ---------------------- */
/* Fires custom events into GA4 (gtag). No-ops safely if gtag isn't present. */
function track(name, params) { try { if (window.gtag) gtag("event", name, params || {}); } catch (e) {} }
function initAnalytics() {
  // WhatsApp clicks (delegated — covers FAB, buttons, inline links, quiz)
  document.addEventListener("click", (e) => {
    const t = e.target.closest ? e.target.closest('a[href*="wa.me"]') : null;
    if (t) track("whatsapp_click", { location: location.pathname });
  });
  // Primary CTAs
  document.querySelectorAll(".btn-primary, .nav-cta, .scene-cta").forEach(el => {
    el.addEventListener("click", () => track("cta_click", {
      cta_text: (el.textContent || "").trim().slice(0, 60), location: location.pathname }));
  });
  // Catalogue: refine filters + category jumps
  const occ = document.getElementById("f-occ"), sty = document.getElementById("f-sty");
  if (occ) occ.addEventListener("change", () => track("catalogue_filter", { filter_type: "occasion", filter_value: occ.value }));
  if (sty) sty.addEventListener("change", () => track("catalogue_filter", { filter_type: "style", filter_value: sty.value }));
  document.querySelectorAll(".catnav-link").forEach(l =>
    l.addEventListener("click", () => track("category_nav", { category: (l.dataset.sec || "").replace("cat-", "") })));
  // Design page view (which specific pieces get attention)
  const m = location.pathname.match(/^\/catalogue\/([^\/]+)\/$/);
  if (m) { const h1 = document.querySelector(".design-info h1"); track("design_view", { design_slug: m[1], design_name: h1 ? h1.textContent.trim() : m[1] }); }
  // Scroll-depth milestones
  const seen = {}; const marks = [25, 50, 75, 100];
  const onScroll = () => {
    const d = document.documentElement, st = d.scrollTop || window.scrollY;
    const h = d.scrollHeight - d.clientHeight, pct = h > 0 ? Math.round(st / h * 100) : 100;
    marks.forEach(mk => { if (pct >= mk && !seen[mk]) { seen[mk] = 1; track("scroll_depth", { percent: mk, page: location.pathname }); } });
  };
  window.addEventListener("scroll", onScroll, { passive: true }); onScroll();
}

/* ---------------------- boot ---------------------- */

/* Campaign slider — native scroll-snap + autoplay, swipe-friendly, GA4-tracked */
function initSlider() {
  const track = document.getElementById("hsTrack");
  if (!track) return;
  const slides = [...track.querySelectorAll(".hs-slide")];
  const dotsBox = document.getElementById("hsDots");
  const prev = document.getElementById("hsPrev"), next = document.getElementById("hsNext");
  if (!slides.length) return;
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  let active = 0, timer = null, pauseUntil = 0;

  const dots = slides.map((_, i) => {
    const b = document.createElement("button");
    b.className = "hs-dot" + (i ? "" : " on");
    b.setAttribute("aria-label", "Go to slide " + (i + 1));
    b.addEventListener("click", () => { hold(); goTo(i); });
    dotsBox.appendChild(b);
    return b;
  });

  function setActive(i) {
    if (i === active) return;
    active = i;
    slides.forEach((s, j) => s.classList.toggle("is-active", j === i));
    dots.forEach((d, j) => d.classList.toggle("on", j === i));
    track_evt();
  }
  let tracked = {};
  function track_evt() { if (!tracked[active]) { tracked[active] = 1; track("slider_view", { slide_index: active + 1 }); } }
  function goTo(i) {
    const n = (i + slides.length) % slides.length;
    track.scrollTo({ left: n * track.clientWidth, behavior: reduced ? "auto" : "smooth" });
  }
  function hold() { pauseUntil = Date.now() + 12000; }

  slides[0].classList.add("is-active");
  let st;
  track.addEventListener("scroll", () => {
    clearTimeout(st);
    st = setTimeout(() => setActive(Math.round(track.scrollLeft / track.clientWidth)), 80);
  }, { passive: true });

  prev.addEventListener("click", () => { hold(); goTo(active - 1); });
  next.addEventListener("click", () => { hold(); goTo(active + 1); });
  track.addEventListener("pointerdown", hold, { passive: true });
  track.addEventListener("keydown", e => {
    if (e.key === "ArrowRight") { hold(); goTo(active + 1); }
    if (e.key === "ArrowLeft") { hold(); goTo(active - 1); }
  });

  if (!reduced) {
    timer = setInterval(() => {
      if (document.hidden || Date.now() < pauseUntil) return;
      const r = track.getBoundingClientRect();
      if (r.bottom < 0 || r.top > innerHeight) return;
      goTo(active + 1);
    }, 5200);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  initReveal();
  initSlider();
  initScroll();
  initMagnetic();
  initNav();
  initForm();
  initAnalytics();
  const y = document.getElementById("year"); if (y) y.textContent = new Date().getFullYear();
});
