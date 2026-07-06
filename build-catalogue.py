#!/usr/bin/env python3
"""
Aarchi's catalogue generator.
Reads data/designs.json and emits, from a shared template (no runtime build):
  /catalogue/index.html                 — filterable liquid-glass catalogue
  /catalogue/<slug>/index.html          — one SEO page per design + enquiry form
Run after editing data/designs.json or adding images:  python3 build-catalogue.py
"""
import json, pathlib, html, datetime

ROOT = pathlib.Path(__file__).parent
WA = "919879390731"
SITE = "Aarchi's by Archana Soni"
DOMAIN = "https://www.aarchisbyarchanasoni.com"  # primary host (www); apex forwards to www at GoDaddy
GA4_ID = "G-BZNX9QFSGD"
GTAG = '''  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-BZNX9QFSGD"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-BZNX9QFSGD');
  </script>
'''

designs = json.loads((ROOT / "data" / "designs.json").read_text())
SITECFG = json.loads((ROOT / "data" / "site.json").read_text())
EXTRA_PAGES = ["/how-it-works/", "/nri-brides/", "/nri-brides/usa/", "/nri-brides/uk/"]

def _live(v):
    """A config value is live once it no longer carries a TODO marker."""
    return bool(v) and "TODO" not in str(v)

LIVE_TESTIMONIALS = [t for t in SITECFG.get("testimonials", [])
                     if _live(t.get("name")) and _live(t.get("quote"))]

def wa_cta_label():
    rh = SITECFG.get("replyHours", "")
    return (f"Get a quote on WhatsApp — replies within {rh} hours"
            if _live(rh) else "Get a quote on WhatsApp")

def price_from(cat):
    p = SITECFG.get("pricing", {}).get(cat, {})
    if _live(p.get("inr")) and _live(p.get("usd")):
        return (f'<p class="price-from">{CAT_LABEL.get(cat, "Pieces")} from &#8377;{esc(str(p["inr"]))} / '
                f'${esc(str(p["usd"]))} &middot; final quote on enquiry</p>')
    return f'<!-- TODO: pricing for "{cat}" unset in data/site.json — price anchor hidden -->'

def testimonials_html(compact=False):
    if not LIVE_TESTIMONIALS:
        return '<!-- TODO: real testimonials unset in data/site.json — section hidden until filled -->'
    items = LIVE_TESTIMONIALS[:2] if compact else LIVE_TESTIMONIALS
    cards = "".join(
        f'<figure class="tst-card{" tst-mini" if compact else ""}" data-reveal>'
        f'<blockquote>&ldquo;{esc(t["quote"])}&rdquo;</blockquote>'
        f'<figcaption>{esc(t["name"])}<span>{esc(t.get("place",""))}</span></figcaption></figure>'
        for t in items)
    if compact:
        return f'<div class="tst-strip">{cards}</div>'
    return f"""  <section class="section-soft tst">
    <div class="wrap center">
      <p class="eyebrow" data-reveal>Real Brides</p>
      <h2 data-reveal style="font-size:clamp(28px,4.4vw,48px);margin-top:8px">Loved, worn, remembered</h2>
      <div class="tst-grid">{cards}</div>
    </div>
  </section>"""

CATS = [("bridal","Bridal Lehengas"),("saree","Sarees"),("dupatta","Dupattas"),
        ("dressmaterial","Dress Material"),("ethnic","Ethnic & Festive"),
        ("festive","Festive Wear"),("mens","Men's Ethnic"),("babyshower","Baby Shower & Maternity")]
CAT_LABEL = {"bridal":"Bridal lehengas","saree":"Sarees","dupatta":"Dupattas","dressmaterial":"Dress material",
             "ethnic":"Ethnic & festive wear","festive":"Festive wear","mens":"Men's ethnic wear",
             "babyshower":"Baby-shower outfits"}
OCCASIONS = sorted({o for d in designs for o in d["occasions"]})
STYLES = sorted({s for d in designs for s in d["styles"]})

def esc(s): return html.escape(s, quote=True)

BIZ_SCHEMA = json.dumps({"@context":"https://schema.org","@type":"ClothingStore",
  "@id":DOMAIN+"/#business","name":SITE,"url":DOMAIN+"/",
  "image":DOMAIN+"/assets/og.jpg","logo":DOMAIN+"/assets/logo-mark.png",
  "telephone":"+91-98793-90731",
  "address":{"@type":"PostalAddress","addressLocality":"Ahmedabad","addressRegion":"Gujarat","addressCountry":"IN"},
  "priceRange":"$$",
  "areaServed":[{"@type":"Country","name":n} for n in ["India","United States","United Kingdom","Canada","Australia","United Arab Emirates"]],
  "sameAs":["https://www.instagram.com/aarchis.byarchanasoni/",
            "https://www.facebook.com/aarchis.byearchanasonii/",
            "https://in.pinterest.com/aarchisbyarchanasoni/",
            "https://in.linkedin.com/company/aarchi-s-by-archana-soni"]}, ensure_ascii=False)



def head(title, desc, canonical_path, og_img, schema=None):
    cn = (f'  <link rel="canonical" href="{DOMAIN}{canonical_path}">\n') if DOMAIN else f'  <!-- canonical TODO (set DOMAIN): {canonical_path} -->\n'
    ogi = f"{DOMAIN}{og_img}" if DOMAIN else og_img
    sc = f'  <script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>\n' if schema else ""
    sc += f'  <script type="application/ld+json">{BIZ_SCHEMA}</script>\n'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}">
{cn}  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(desc)}">
  <meta property="og:image" content="{ogi}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{SITE}">
  <meta property="og:url" content="{DOMAIN}{canonical_path}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(desc)}">
  <meta name="twitter:image" content="{ogi}">
  <link rel="icon" href="/assets/favicon.png">
  <link rel="apple-touch-icon" href="/assets/favicon.png">
  <link rel="stylesheet" href="/styles.css?v=23">
  <link rel="stylesheet" href="/catalogue.css?v=23">
  <script>document.documentElement.classList.add("js")</script>
{GTAG}{sc}</head>
<body>
"""

def nav(active=""):
    def a(href,label,key):
        cls = ' class="active"' if key==active else ''
        return f'<a href="{href}"{cls}>{label}</a>'
    return f"""  <header class="nav">
    <div class="wrap nav-in">
      <a href="/" class="brand"><img class="brand-mark" src="/assets/logo-mark.png" alt="Aarchi's" width="36" height="36"><span class="brand-wm">Aarchi's<small>by Archana Soni</small></span></a>
      <nav class="nav-links">
        {a("/","Home","home")}
        {a("/catalogue/","Catalogue","cat")}
        {a("/how-it-works/","How it works","how")}
        {a("/about/","About","about")}
        {a("/contact/","Contact","contact")}
        <a href="/contact/" class="nav-cta">Book a Consultation</a>
      </nav>
      <button class="burger" aria-label="Menu"><span></span><span></span><span></span></button>
    </div>
  </header>
"""

FOOTER = f"""  <footer class="foot">
    <div class="wrap">
      <div class="foot-top">
        <div>
          <a href="/" class="brand"><img class="brand-mark" src="/assets/logo-mark.png" alt="Aarchi's" width="36" height="36"><span class="brand-wm">Aarchi's<small>by Archana Soni</small></span></a>
          <p style="margin-top:14px;max-width:34ch;color:#b8a89c;font-size:14.5px">Custom fashion designer, Ahmedabad. Where tradition meets trend.</p>
        </div>
        <div><h4>Explore</h4><ul>
          <li><a href="/catalogue/">Catalogue</a></li>
          <li><a href="/how-it-works/">How it works</a></li>
          <li><a href="/nri-brides/">For NRI brides</a></li>
          <li><a href="/navratri-outfits-ahmedabad/">Navratri edit</a></li>
          <li><a href="/about/">About</a></li>
          <li><a href="/contact/">Contact</a></li>
        </ul></div>
        <div><h4>Visit</h4><ul>
          <li>Ahmedabad, India</li>
          <li><a href="https://wa.me/{WA}">WhatsApp: +91 98793 90731</a></li>
        </ul></div>
      </div>
      <div class="foot-bot">
        <span>© <span id="year">2026</span> Aarchi's by Archana Soni. All rights reserved.</span>
        <span>Crafted in Ahmedabad.</span>
      </div>
    </div>
  </footer>
  <a href="https://wa.me/{WA}" class="wa-fab" aria-label="Chat on WhatsApp" rel="noopener">
    <svg viewBox="0 0 24 24"><path d="M.06 24l1.68-6.13A11.83 11.83 0 010 11.98C0 5.37 5.37 0 11.98 0a11.9 11.9 0 018.41 3.49 11.82 11.82 0 013.49 8.41c0 6.6-5.38 11.97-11.98 11.97a12 12 0 01-5.73-1.46L.06 24zM6.6 20.2c1.67.99 3.27 1.58 5.38 1.58 5.48 0 9.95-4.46 9.95-9.95 0-5.5-4.45-9.95-9.94-9.95C6.5 1.88 2.04 6.33 2.04 11.82c0 2.22.65 3.88 1.74 5.62l-1 3.62 3.82-1zm11.39-5.55c-.07-.12-.27-.2-.57-.35-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.96-.94 1.16-.17.2-.35.22-.65.07-.3-.15-1.26-.46-2.4-1.48-.88-.79-1.48-1.76-1.65-2.06-.17-.3-.02-.46.13-.61.13-.13.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.02-.52-.07-.15-.67-1.62-.92-2.22-.24-.58-.49-.5-.67-.51l-.57-.01c-.2 0-.52.07-.8.37-.27.3-1.04 1.02-1.04 2.48 0 1.46 1.07 2.88 1.22 3.08.15.2 2.1 3.2 5.08 4.49.71.3 1.26.49 1.69.63.71.22 1.36.19 1.87.12.57-.09 1.76-.72 2-1.42.25-.69.25-1.28.18-1.41z"/></svg>
  </a>
"""

def chips(items, cls): return "".join(f'<span class="chip {cls}">{esc(i)}</span>' for i in items)

def card(d):
    occ = " ".join(d["occasions"]); sty = " ".join(d["styles"])
    price_badge = f'<span class="dcard-price">&#8377;{d["priceINR"]:,}</span>' if d.get("priceINR") else ""
    return f"""      <a class="dcard glass-card" href="/catalogue/{d['slug']}/" data-cat="{d['category']}" data-occ="{esc(occ)}" data-sty="{esc(sty)}">
        <div class="dcard-media">{'<span class="dcard-badge">New arrival</span>' if d.get('isNew') else ''}<img src="{d['img']}" alt="{esc(d['name'])} — {esc(d['categoryLabel'])} by {SITE}" loading="lazy" width="600" height="750"></div>
        <div class="dcard-body">
          <span class="dcard-cat">{esc(d['categoryLabel'])}</span>
          <h3>{esc(d['name'])}</h3>
          <div class="dcard-tags">{chips(d['occasions'][:2],'occ')}</div>
          {price_badge}
          <span class="dcard-link">View &amp; customise <i>&rarr;</i></span>
        </div>
      </a>
"""

def catalogue_index():
    present = [(k, lbl) for k, lbl in CATS if any(d["category"] == k for d in designs)]
    occ_opts = "".join(f'<option value="{esc(o)}">{esc(o)}</option>' for o in OCCASIONS)
    sty_opts = "".join(f'<option value="{esc(s)}">{esc(s)}</option>' for s in STYLES)

    navlinks = "".join(
        f'<a class="catnav-link" href="#cat-{k}" data-sec="cat-{k}">{esc(lbl)}'
        f'<i>{sum(1 for d in designs if d["category"]==k)}</i></a>'
        for k, lbl in present)

    secs = []
    for i, (k, lbl) in enumerate(present, 1):
        items = [d for d in designs if d["category"] == k]
        n = len(items); nlabel = "design" if n == 1 else "designs"
        cards = "".join(card(d) for d in items)
        secs.append(f"""  <section class="catsec" id="cat-{k}" data-cat="{k}">
    <div class="wrap">
      <header class="catsec-head">
        <span class="catsec-num" data-reveal>{i:02d}</span>
        <div class="catsec-head-main">
          <h2 data-reveal style="--i:1">{esc(lbl)}</h2>
          <p class="lead" data-reveal style="--i:2">{esc(SCENE_DESC.get(k, ''))}</p>
          {price_from(k)}
        </div>
        <span class="catsec-count" data-reveal style="--i:1">{n} {nlabel}</span>
      </header>
      <div class="dgrid">
{cards}      </div>
    </div>
  </section>""")
    sections = "\n".join(secs)

    schema = {"@context":"https://schema.org","@type":"CollectionPage","name":f"Catalogue — {SITE}",
              "about":"Bespoke bridal, saree, festive and custom fashion designs, made to measure in Ahmedabad."}
    title = "Custom Bridal Lehengas, Sarees & Festive Wear Catalogue | Aarchi's"
    desc = "Browse 40+ custom bridal lehengas, designer sarees, festive, men's ethnic and baby-shower outfits — made to measure in Ahmedabad, shipped worldwide. Customise colour, fabric and size."
    return head(title, desc, "/catalogue/", designs[0]["img"], schema) + nav("cat") + f"""
  <section class="cat-hero">
    <div class="cat-hero-bg" data-parallax data-speed="0.16"></div>
    <div class="wrap center">
      <p class="eyebrow" data-reveal style="--i:0">The Catalogue</p>
      <h1 data-reveal style="--i:1">Designs, made <em>for you</em></h1>
      <p class="lead center" data-reveal style="--i:2">Every piece is handcrafted and made to measure — browse by category,
        refine by occasion &amp; style, then enquire to tailor it to you.</p>
      <p class="cat-stats" data-reveal style="--i:3">{len(designs)} designs &middot; {len(present)} categories &middot; made to measure in Ahmedabad</p>
    </div>
  </section>

  <nav class="catnav glass" id="catnav" aria-label="Browse categories">
    <div class="wrap catnav-in">
      <div class="catnav-links">{navlinks}</div>
      <div class="catnav-refine">
        <span class="cat-count" id="cat-count" aria-live="polite"></span>
        <select id="f-occ" aria-label="Filter by occasion"><option value="all">Any occasion</option>{occ_opts}</select>
        <select id="f-sty" aria-label="Filter by style"><option value="all">Any style</option>{sty_opts}</select>
        <button id="f-clear" class="fclear">Reset</button>
      </div>
    </div>
  </nav>

  <div class="catsecs" id="catsecs">
{sections}
  </div>
  <p class="cat-empty" id="cat-empty" hidden><span class="wrap">No designs match those filters — <a href="https://wa.me/{WA}">message us</a> and we&#39;ll create one for you.</span></p>
""" + FOOTER + '  <script src="/app.js?v=23" defer></script>\n  <script src="/catalogue.js?v=23" defer></script>\n</body>\n</html>\n'

SOCIAL_ICONS = ('<a href="https://www.instagram.com/aarchis.byarchanasoni/" target="_blank" rel="noopener">Instagram</a>'
  '<a href="https://www.facebook.com/aarchis.byearchanasonii/" target="_blank" rel="noopener">Facebook</a>'
  '<a href="https://in.pinterest.com/aarchisbyarchanasoni/" target="_blank" rel="noopener">Pinterest</a>')

def _exists(webpath):
    return bool(webpath) and (ROOT / webpath.lstrip("/")).exists()

def editorial_html(d, related):
    """Flagship editorial — full self-contained story slides (each carries its own
    baked-in copy), a cross-sell strip and an owner/atelier promo band. Renders only
    when a design has an `editorial.slides` block; missing images are skipped so the
    page degrades gracefully before photography lands."""
    ed = d.get("editorial")
    if not ed:
        return ""
    all_slides = ed.get("slides", [])
    slides = [s for s in all_slides if _exists(s.get("img", ""))]
    if not slides:
        return ""
    def fig(s):
        cap = ""
        if s.get("caption"):
            kick = f'<span class="eslide-kicker">{esc(s["kicker"])}</span>' if s.get("kicker") else ""
            cap = f'<figcaption class="eslide-cap">{kick}<p>{esc(s["caption"])}</p></figcaption>'
        return (f'      <figure class="eslide" data-reveal><img src="{s["img"]}" '
                f'alt="{esc(s.get("alt",""))}" loading="lazy" width="562" height="1000">{cap}</figure>')
    figs = "\n".join(fig(s) for s in slides)
    story_title = esc(ed.get("storyTitle", "Up close"))
    story_lead = esc(ed.get("storyLead",
        "From the first sketch to the final drape — every detail is hand-worked, "
        "made to measure, and shipped worldwide."))
    intro = f"""  <section class="estory-intro">
    <div class="wrap center">
      <p class="eyebrow" data-reveal>The Story</p>
      <h2 data-reveal style="font-size:clamp(28px,4vw,50px);margin-top:6px">{story_title}</h2>
      <p class="lead center" data-reveal>{story_lead}</p>
    </div>
  </section>"""
    gallery = f'  <section class="estory"><div class="eslides">\n{figs}\n    </div>\n  </section>'
    cross = ""
    if related and any(s.get("crosssell") for s in all_slides):
        cross = ('\n  <section class="estory-cross-sec"><div class="wrap center">'
                 '<p class="estory-crosslabel" data-reveal>Complete the look</p>'
                 '<div class="estory-cross">' + "".join(card(r) for r in related[:3]) +
                 "</div></div></section>")
    promo = f"""
  <section class="section-soft eowner">
    <div class="wrap center">
      <p class="eyebrow" data-reveal>The Atelier</p>
      <h2 data-reveal style="font-size:clamp(28px,4vw,46px);margin-top:6px">Designed by Archana Soni</h2>
      <p class="lead center" data-reveal>Every Aarchi's piece is designed and made to measure by Archana Soni in Ahmedabad — and shipped worldwide. Custom colours, fabrics and sizing, tailored to your story.</p>
      <div class="hero-actions" data-reveal style="justify-content:center;margin-top:24px">
        <a href="https://wa.me/{WA}" class="btn btn-primary" rel="noopener">{wa_cta_label()}</a>
        <a href="/about/" class="btn btn-ghost">Meet Archana</a>
      </div>
      <div class="esocials" data-reveal>{SOCIAL_ICONS}</div>
    </div>
  </section>"""
    return "\n" + intro + "\n" + gallery + cross + promo + "\n"

def design_page(d, related):
    hero_img = d["editorial"]["heroImg"] if (d.get("editorial") and _exists(d["editorial"].get("heroImg",""))) else d["img"]
    title = f"{d['name']} — Custom {d['categoryLabel']}, Ahmedabad | Aarchi's"
    occ_opts = "".join(f'<option{" selected" if o==d["occasions"][0] else ""}>{esc(o)}</option>' for o in OCCASIONS)
    sty_opts = "".join(f'<option{" selected" if s==d["styles"][0] else ""}>{esc(s)}</option>' for s in STYLES)
    sizes = ["XS","S","M","L","XL","XXL","Made-to-measure"]
    size_opts = "".join(f'<option{" selected" if s=="Made-to-measure" else ""}>{esc(s)}</option>' for s in sizes)
    imgs = [(DOMAIN+d["img"]) if DOMAIN else d["img"]]
    for s in (d.get("editorial") or {}).get("slides", []):
        if _exists(s.get("img","")): imgs.append((DOMAIN+s["img"]) if DOMAIN else s["img"])
    schema = {"@context":"https://schema.org","@type":"Product","name":d["name"],
              "image":imgs,"description":d["description"],
              "category":d["categoryLabel"],"brand":{"@type":"Brand","name":SITE}}
    if d.get("priceINR"):
        schema["offers"] = {"@type":"Offer","priceCurrency":"INR","price":str(d["priceINR"]),
                             "availability":"https://schema.org/InStock",
                             "url":(DOMAIN+f"/catalogue/{d['slug']}/") if DOMAIN else f"/catalogue/{d['slug']}/"}
    bc = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Catalogue","item":(DOMAIN+"/catalogue/") if DOMAIN else "/catalogue/"},
        {"@type":"ListItem","position":2,"name":d["name"]}]}
    rel_cards = "".join(card(r) for r in related)
    return head(title, d["metaDescription"], f"/catalogue/{d['slug']}/", d["img"], [schema, bc]) + nav("cat") + f"""
  <section class="design">
    <div class="wrap design-in">
      <div class="design-media glass" data-reveal="left">
        <img src="{hero_img}" alt="{esc(d['name'])} — {esc(d['categoryLabel'])} by {SITE}" width="800" height="1000">
      </div>
      <div class="design-info" data-reveal="right">
        <nav class="crumbs"><a href="/catalogue/">Catalogue</a> <span>/</span> {esc(d['categoryLabel'])}</nav>
        <h1>{esc(d['name'])}</h1>
        <div class="design-tags">{'<span class="chip new">New arrival</span>' if d.get('isNew') else ''}{chips(d['occasions'],'occ')}{chips(d['styles'],'sty')}</div>
        <p class="design-desc">{esc(d['detail'])}</p>
        <ul class="design-meta">
          <li><b>Category</b> {esc(d['categoryLabel'])}</li>
          <li><b>Crafting</b> Handcrafted, made to measure in Ahmedabad</li>
          <li><b>Pricing</b> {f'&#8377;{d["priceINR"]:,}' if d.get("priceINR") else "On enquiry — every piece is customised"}</li>
        </ul>

        <form class="enquiry glass" id="design-enquiry"
              data-name="{esc(d['name'])}" data-cat="{esc(d['categoryLabel'])}" data-slug="{d['slug']}"{f' data-price="₹{d["priceINR"]:,}"' if d.get("priceINR") else ""}>
          <h2>Enquire &amp; customise</h2>
          {price_from(d["category"])}
          <div class="erow">
            <label>Occasion<select name="occasion">{occ_opts}</select></label>
            <label>Size<select name="size">{size_opts}</select></label>
          </div>
          <div class="erow">
            <label>Style preference<select name="style">{sty_opts}</select></label>
            <label>Your name<input name="name" placeholder="Name"></label>
          </div>
          <label class="efull">Customisation notes
            <textarea name="notes" placeholder="Colour, fabric, sleeves, timeline, budget…"></textarea></label>
          <button type="submit" class="btn btn-primary ebtn">{wa_cta_label()}</button>
          <p class="form-note">Opens WhatsApp with your details pre-filled for this design.</p>
        {testimonials_html(compact=True)}
        </form>
      </div>
    </div>
  </section>
""" + editorial_html(d, related) + (f"""
  <section class="section-soft related">
    <div class="wrap">
      <p class="eyebrow center" data-reveal>You may also like</p>
      <h2 class="center" data-reveal style="margin-top:6px;font-size:clamp(26px,3.4vw,40px)">More {esc(d['categoryLabel'])}</h2>
      <div class="dgrid">{rel_cards}</div>
    </div>
  </section>
""" if related else "") + FOOTER + '  <script src="/app.js?v=23" defer></script>\n  <script src="/catalogue.js?v=23" defer></script>\n</body>\n</html>\n'

SCENE_DESC = {
    "bridal":     "Heirloom lehengas in zari, zardozi and khat work — crafted for the moment you've always pictured.",
    "saree":      "Silk, paithani and bandhej drapes, hand-finished and styled for every celebration.",
    "dupatta":    "Hand-worked gharchola, bandhej and net dupattas — the finishing layer for bridal and festive looks.",
    "dressmaterial": "Pure silk suit pieces with a matching dupatta — unstitched, and tailored to your measurements.",
    "ethnic":     "Festive and Navratri ensembles that turn a little tradition into a statement.",
    "festive":    "Occasion-ready festive wear, designed and made to measure.",
    "mens":       "Sharp, regal ethnic wear for grooms and the men of the celebration.",
    "babyshower": "Bespoke baby-shower and maternity outfits to make the mum-to-be glow.",
}

def home_showcase():
    scenes, i = [], 0
    for key, label in CATS:
        items = [d for d in designs if d["category"] == key]
        if not items: continue
        i += 1
        hero = items[0]
        rev = " rev" if i % 2 == 0 else ""
        strip = "".join(
            f'<a class="strip-card" href="/catalogue/{esc(d["slug"])}/"><img src="{d["img"]}" alt="{esc(d["name"])}" loading="lazy" width="240" height="320"><span>{esc(d["name"])}</span></a>'
            for d in items[:10])
        nlabel = "design" if len(items) == 1 else "designs"
        scenes.append(f"""  <div class="scene{rev}">
    <div class="wrap">
      <div class="scene-row">
        <div class="scene-media" data-scrub>
          <img src="{hero['img']}" alt="{esc(hero['name'])} — {esc(label)} by {SITE}" loading="lazy" width="720" height="900">
        </div>
        <div class="scene-info">
          <span class="scene-num" data-reveal>{i:02d}</span>
          <h2 data-reveal style="--i:1">{esc(label)}</h2>
          <p class="lead" data-reveal style="--i:2">{esc(SCENE_DESC.get(key, ''))}</p>
          <a class="scene-cta" href="/catalogue/#cat-{key}" data-reveal style="--i:3">Explore {len(items)} {nlabel} <i>&rarr;</i></a>
        </div>
      </div>
      <div class="strip" data-reveal>{strip}</div>
    </div>
  </div>""")
    return f"""  <section class="showcase">
    <div class="wrap showcase-intro center">
      <p class="eyebrow" data-reveal>The Signature Edit</p>
      <h2 data-reveal style="font-size:clamp(30px,5vw,56px);margin-top:8px">Explore by occasion</h2>
      <p class="lead center" data-reveal>Every piece is made to measure — laid out across the moments you dress for.</p>
    </div>
{chr(10).join(scenes)}
    <div class="wrap center" style="margin-top:clamp(56px,8vw,100px)">
      <a href="/catalogue/" class="btn btn-primary" data-reveal>View the full catalogue</a>
    </div>
  </section>"""

def home_campaign():
    """Homepage campaign slider — one slide per design that has an editorial story.
    The last editorial photo (the finale portrait) fronts each slide."""
    eds = [d for d in designs if d.get("editorial") and
           any(_exists(s.get("img","")) for s in d["editorial"].get("slides",[]))]
    pri = {"bridal":0,"saree":1,"ethnic":2,"festive":3,"mens":4,"babyshower":5}
    eds.sort(key=lambda d: pri.get(d["category"], 9))
    if not eds:
        return ""
    slides = []
    for i, d in enumerate(eds):
        s = [s for s in d["editorial"]["slides"] if _exists(s.get("img",""))][-1]
        eager = ' fetchpriority="low"' if i else ''
        lazy = ' loading="lazy"' if i else ''
        slides.append(f"""      <article class="hs-slide" role="group" aria-label="{i+1} of {len(eds)}">
        <div class="hs-media"><img src="{s['img']}" alt="{esc(s.get('alt', d['name']))}"{lazy}{eager} width="562" height="1000"></div>
        <div class="hs-text">
          <span class="hs-num">{i+1:02d} / {len(eds):02d}</span>
          <span class="eyebrow">{esc(d['categoryLabel'])}</span>
          <h3>{esc(d['name'])}</h3>
          <p>{esc(d['editorial'].get('storyTitle',''))} — {esc(d['detail'])}</p>
          <div class="hs-actions">
            <a class="btn btn-primary" href="/catalogue/{d['slug']}/">View the story</a>
            <a class="btn btn-ghost" href="https://wa.me/{WA}" rel="noopener">Get a quote</a>
          </div>
        </div>
      </article>""")
    return f"""  <section class="hslider" aria-label="Signature campaign stories">
    <div class="wrap center hslider-head">
      <p class="eyebrow" data-reveal>The Campaign</p>
      <h2 data-reveal style="font-size:clamp(30px,5vw,56px);margin-top:8px">Signature stories</h2>
      <p class="lead center" data-reveal>Our flagship pieces, shot detail by detail — swipe through the collection.</p>
    </div>
    <div class="hs-track" id="hsTrack" tabindex="0">
{chr(10).join(slides)}
    </div>
    <div class="hs-ctl" aria-hidden="false">
      <button class="hs-btn" id="hsPrev" aria-label="Previous slide">&larr;</button>
      <div class="hs-dots" id="hsDots"></div>
      <button class="hs-btn" id="hsNext" aria-label="Next slide">&rarr;</button>
    </div>
  </section>"""


def navratri_page():
    items = [d for d in designs if d["category"] in ("ethnic", "festive")]
    cards = "".join(card(d) for d in items)
    faqs = [
      ("Do you design custom chaniya cholis for Navratri?",
       "Yes — Navratri and garba-night ensembles are made to order at the Ahmedabad studio. Pick a design from the festive edit or bring a reference, and it's cut to your measurements with the colours and work you choose."),
      ("How early should I order before Navratri?",
       "The earlier the better — festive season slots fill fast. Message us on WhatsApp with your date and we'll confirm what's possible for your timeline."),
      ("Can I customise the colours or mirror work?",
       "Absolutely. Colours, fabrics, embroidery and mirror work are all tailored to you — every piece is a starting point."),
      ("I'm not in Ahmedabad — can you still make my Navratri outfit?",
       "Yes. Measurements are guided over WhatsApp video and finished outfits ship across India and worldwide."),
    ]
    faq_html = "".join(
        f'<details class="faq-item"><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in faqs)
    faq_schema = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q, a in faqs]}
    bc = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":DOMAIN+"/"},
        {"@type":"ListItem","position":2,"name":"Navratri Outfits Ahmedabad"}]}
    title = "Navratri Chaniya Choli & Festive Outfits, Ahmedabad | Aarchi's"
    desc = ("Custom Navratri chaniya cholis and garba-night festive wear, made to measure in Ahmedabad by "
            "Archana Soni. Choose a design, customise colours and mirror work, enquire on WhatsApp.")
    return head(title, desc, "/navratri-outfits-ahmedabad/", items[0]["img"] if items else "/assets/og.jpg",
                [faq_schema, bc]) + nav("cat") + f"""
  <section class="cat-hero">
    <div class="cat-hero-bg" data-parallax data-speed="0.16"></div>
    <div class="wrap center">
      <p class="eyebrow" data-reveal style="--i:0">Festive Edit &middot; Ahmedabad</p>
      <h1 data-reveal style="--i:1">Navratri, made <em>to twirl</em></h1>
      <p class="lead center" data-reveal style="--i:2">Custom chaniya cholis and festive ensembles for garba nights —
        designed and made to measure in Ahmedabad by Archana Soni. Nine nights deserve better than off-the-rack.</p>
      <div class="hero-actions" data-reveal style="--i:3" style="justify-content:center">
        <a href="https://wa.me/{WA}" class="btn btn-primary" rel="noopener">{wa_cta_label()}</a>
        <a href="/catalogue/#cat-ethnic" class="btn btn-ghost">Full festive catalogue</a>
      </div>
    </div>
  </section>
  <section class="catsec">
    <div class="wrap">
      <header class="catsec-head">
        <div class="catsec-head-main">
          <h2 data-reveal>The festive edit</h2>
          <p class="lead" data-reveal style="--i:1">Navratri-ready ensembles from the catalogue — every one customisable in colour, fabric and mirror work.</p>
          {price_from("ethnic")}
        </div>
        <span class="catsec-count" data-reveal>{len(items)} designs</span>
      </header>
      <div class="dgrid">
{cards}      </div>
    </div>
  </section>
  <section class="faq section-soft">
    <div class="wrap">
      <div class="center">
        <p class="eyebrow" data-reveal>Good to know</p>
        <h2 data-reveal style="font-size:clamp(26px,4vw,42px);margin-top:8px">Navratri orders, answered</h2>
      </div>
      <div class="faq-list">{faq_html}</div>
      <div class="hero-actions" style="justify-content:center;margin-top:30px" data-reveal>
        <a href="https://wa.me/{WA}" class="btn btn-primary" rel="noopener">{wa_cta_label()}</a>
      </div>
    </div>
  </section>
""" + FOOTER + '  <script src="/app.js?v=23" defer></script>\n  <script src="/catalogue.js?v=23" defer></script>\n</body>\n</html>\n'


PROCESS_STEPS = [
  ("Consultation on WhatsApp", "Tell us the occasion, your ideas and budget — share reference photos or pick a catalogue design as the starting point."),
  ("Design & fabric", "Archana works out the silhouette, fabrics, colours and embroidery with you, with photos and swatches shared on chat."),
  ("Measurements at home", "A video-guided measurement session on WhatsApp — all you need is a measuring tape and a helper."),
  ("Crafted in Ahmedabad", "Your outfit is cut, embroidered and finished at the studio, with progress photos as it comes together."),
  ("Fitting review", "You see the finished piece on photos and video before it ships — tweaks are agreed right there."),
  ("Delivered to your door", "Carefully packed and shipped — across India and worldwide."),
]

def process_html():
    return '<div class="svc-grid">' + "".join(
        f'<article class="svc-card" data-reveal style="--i:{i}"><span class="svc-num">{i+1:02d}</span>'
        f'<h3>{esc(t)}</h3><p>{esc(b)}</p></article>'
        for i, (t, b) in enumerate(PROCESS_STEPS)) + "</div>"

def _nri_fact(label, key_path, fallback):
    """Renders a fact line when its site.json value is live; else a generic honest line + TODO comment."""
    node = SITECFG.get("nri", {})
    for k in key_path.split("."):
        node = node.get(k, "") if isinstance(node, dict) else ""
    if _live(node):
        return f'<li><strong>{esc(label)}:</strong> {esc(str(node))}</li>'
    return f'<li><strong>{esc(label)}:</strong> {esc(fallback)}</li><!-- TODO: set nri.{key_path} in data/site.json -->'

def _faq_block(faqs):
    faq_html = "".join(f'<details class="faq-item"><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in faqs)
    schema = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q, a in faqs]}
    return faq_html, schema

def how_it_works_page():
    title = "How It Works — Custom Outfits, Made to Measure | Aarchi's"
    desc = ("From a WhatsApp consultation to your door: how Aarchi's designs, measures, crafts and delivers "
            "made-to-measure Indian outfits from the Ahmedabad studio — locally and worldwide.")
    faqs = [
      ("Do I need to visit the studio?",
       "No — the whole process runs on WhatsApp if you prefer: consultation, video-guided measurements, progress photos and a fitting review before shipping. Studio visits in Ahmedabad are welcome by appointment."),
      ("How are measurements taken remotely?",
       "On a short WhatsApp video call, Archana guides you through each measurement step by step. You need a measuring tape and ideally someone to help."),
      ("Can I customise a catalogue design?",
       "Yes — every catalogue piece is a starting point. Colours, fabrics, embroidery and silhouettes are tailored to you."),
      ("How is the price decided?",
       "Each piece is quoted individually based on fabric, hand-work and construction. Share your budget in the first chat and the design is worked around it."),
    ]
    faq_html, schema = _faq_block(faqs)
    bc = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":DOMAIN+"/"},
        {"@type":"ListItem","position":2,"name":"How It Works"}]}
    return head(title, desc, "/how-it-works/", "/assets/og.jpg", [schema, bc]) + nav("how") + f"""
  <section class="cat-hero">
    <div class="cat-hero-bg" data-parallax data-speed="0.16"></div>
    <div class="wrap center">
      <p class="eyebrow" data-reveal style="--i:0">The Process</p>
      <h1 data-reveal style="--i:1">Made for you, <em>step by step</em></h1>
      <p class="lead center" data-reveal style="--i:2">Every Aarchi's piece is made to measure — here's exactly how a
        custom outfit comes to life, whether you're in Ahmedabad or across the world.</p>
    </div>
  </section>
  <section class="section-soft" style="padding-block:clamp(50px,7vw,90px)">
    <div class="wrap center">{process_html()}</div>
  </section>
  <section class="faq">
    <div class="wrap">
      <div class="center"><p class="eyebrow" data-reveal>Good to know</p>
      <h2 data-reveal style="font-size:clamp(26px,4vw,42px);margin-top:8px">Common questions</h2></div>
      <div class="faq-list">{faq_html}</div>
      <div class="hero-actions" style="justify-content:center;margin-top:30px" data-reveal>
        <a href="https://wa.me/{WA}" class="btn btn-primary" rel="noopener">{wa_cta_label()}</a>
        <a href="/catalogue/" class="btn btn-ghost">Browse the catalogue</a>
      </div>
      <p class="center" style="margin-top:22px;color:var(--ink-soft);font-size:14.5px">Ordering from outside India?
        See <a href="/nri-brides/" style="color:var(--gold-deep);font-weight:600">how it works for NRI brides</a>.</p>
    </div>
  </section>
""" + FOOTER + '  <script src="/app.js?v=23" defer></script>\n</body>\n</html>\n'

def nri_hub_page():
    title = "Custom Indian Bridal Outfits for NRI Brides — Made in India, Delivered Worldwide | Aarchi's"
    desc = ("Custom bridal lehengas and Indian wedding outfits for NRI brides — designed on WhatsApp, made to "
            "measure in Ahmedabad, shipped to the USA, UK, Canada, Australia and UAE.")
    faqs = [
      ("Can I order a custom bridal lehenga from India to the USA or UK?",
       "Yes — that's exactly what we do. The consultation, design and measurements all happen on WhatsApp, the outfit is handcrafted in Ahmedabad, and it ships to your door in the USA, UK, Canada, Australia, UAE and beyond."),
      ("How do made-to-measure outfits work online?",
       "Measurements are taken on a video-guided WhatsApp call, and you review the finished outfit on photos and video before it ships — so nothing is left to chance."),
      ("What if it doesn't fit when it arrives?",
       "Made-to-measure cuts fit risk dramatically, and every piece is checked against your measurements before shipping. If something needs adjusting, message us and we'll guide the alteration with a local tailor."),
      ("Do you understand what NRI brides need?",
       "Many of our clients order from abroad for weddings in India or celebrations overseas. Timezone-friendly chats, clear progress photos and honest timelines are part of the service."),
    ]
    faq_html, schema = _faq_block(faqs)
    bc = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":DOMAIN+"/"},
        {"@type":"ListItem","position":2,"name":"NRI Brides"}]}
    facts = "".join([
      _nri_fact("Typical timeline", "timeline", "confirmed on enquiry — share your wedding date first"),
      _nri_fact("Payment", "payment", "discussed and confirmed on WhatsApp before work begins"),
    ])
    return head(title, desc, "/nri-brides/", "/assets/og.jpg", [schema, bc]) + nav("") + f"""
  <section class="cat-hero">
    <div class="cat-hero-bg" data-parallax data-speed="0.16"></div>
    <div class="wrap center">
      <p class="eyebrow" data-reveal style="--i:0">For NRI Brides</p>
      <h1 data-reveal style="--i:1">Made in India,<br><em>delivered worldwide</em></h1>
      <p class="lead center" data-reveal style="--i:2">Custom Indian bridal outfits designed over WhatsApp, handcrafted
        in Ahmedabad, and shipped to the USA, UK, Canada, Australia and UAE — made to your measurements, not a size chart.</p>
      <div class="hero-actions" data-reveal style="--i:3;justify-content:center">
        <a href="https://wa.me/{WA}" class="btn btn-primary" rel="noopener">{wa_cta_label()}</a>
        <a href="/how-it-works/" class="btn btn-ghost">How it works</a>
      </div>
    </div>
  </section>
  <section class="section-soft" style="padding-block:clamp(50px,7vw,90px)">
    <div class="wrap center">
      <p class="eyebrow" data-reveal>The Remote Process</p>
      <h2 data-reveal style="font-size:clamp(26px,4vw,44px);margin:8px 0 30px">Six steps, zero guesswork</h2>
      {process_html()}
      <ul class="nri-facts" data-reveal>{facts}</ul>
    </div>
  </section>
  <section style="padding-block:clamp(46px,6vw,80px)">
    <div class="wrap center">
      <p class="eyebrow" data-reveal>Your Country</p>
      <h2 data-reveal style="font-size:clamp(26px,4vw,42px);margin-top:8px">Ordering from&hellip;</h2>
      <div class="hero-actions" style="justify-content:center;margin-top:24px" data-reveal>
        <a href="/nri-brides/usa/" class="btn btn-ghost">United States</a>
        <a href="/nri-brides/uk/" class="btn btn-ghost">United Kingdom</a>
        <a href="https://wa.me/{WA}" class="btn btn-ghost" rel="noopener">Canada &middot; Australia &middot; UAE — ask us</a>
      </div>
    </div>
  </section>
  <!-- TESTIMONIALS slot: fills automatically once data/site.json testimonials are real -->
{testimonials_html()}
  <section class="faq section-soft">
    <div class="wrap">
      <div class="center"><p class="eyebrow" data-reveal>Good to know</p>
      <h2 data-reveal style="font-size:clamp(26px,4vw,42px);margin-top:8px">NRI orders, answered</h2></div>
      <div class="faq-list">{faq_html}</div>
      <div class="hero-actions" style="justify-content:center;margin-top:30px" data-reveal>
        <a href="https://wa.me/{WA}" class="btn btn-primary" rel="noopener">{wa_cta_label()}</a>
        <a href="/catalogue/" class="btn btn-ghost">Browse designs</a>
      </div>
    </div>
  </section>
""" + FOOTER + '  <script src="/app.js?v=23" defer></script>\n</body>\n</html>\n'

COUNTRY_META = {
  "usa": {
    "label": "the USA", "cur": "USD",
    "title": "Custom Bridal Lehengas from India to the USA — Made to Measure, Shipped to Your Door | Aarchi's",
    "desc": ("Order a custom bridal lehenga from India to the USA. Designed on WhatsApp, made to measure in "
             "Ahmedabad, shipped across the United States. For NRI brides who want it made right."),
    "h1": "From Ahmedabad<br>to <em>the USA</em>",
    "lead": ("Custom bridal lehengas and Indian wedding outfits for NRI brides across the United States — "
             "designed together on WhatsApp despite the timezones, crafted in Ahmedabad, delivered to your door."),
    "faqs": [
      ("How do I order a custom bridal lehenga from India to the USA?",
       "Start a WhatsApp chat with your date and ideas. Design and fabric choices happen on chat, measurements on a guided video call, and the finished lehenga ships from Ahmedabad to your US address."),
      ("Do you work across US timezones?",
       "Yes — chats are asynchronous by nature and calls are scheduled to suit EST to PST."),
      ("What about customs and duties in the US?",
       "Any applicable US import duties are confirmed with your quote before you commit, so there are no surprises at delivery."),
      ("Is made-to-measure safe to order online?",
       "Measurements are video-guided and the finished piece is reviewed on photos and video before shipping — a fitting, minus the flight."),
    ]},
  "uk": {
    "label": "the UK", "cur": "GBP",
    "title": "Custom Bridal Lehengas from India to the UK — Made to Measure, Shipped to Your Door | Aarchi's",
    "desc": ("Order a custom bridal lehenga from India to the UK. Designed on WhatsApp, made to measure in "
             "Ahmedabad, shipped across the United Kingdom. For British-Indian brides who want it made right."),
    "h1": "From Ahmedabad<br>to <em>the UK</em>",
    "lead": ("Custom bridal lehengas and Indian wedding outfits for brides across the United Kingdom — designed "
             "together on WhatsApp, handcrafted in Ahmedabad, delivered to your door."),
    "faqs": [
      ("How do I order a custom bridal lehenga from India to the UK?",
       "Message us on WhatsApp with your date and ideas. Design and fabric choices happen on chat, measurements on a guided video call, and the finished lehenga ships from Ahmedabad to your UK address."),
      ("Do UK brides really order bridal wear from India?",
       "Constantly — made-to-measure from the source is often better made and better value than off-the-peg abroad, and it's genuinely yours."),
      ("What about UK customs and VAT?",
       "Any applicable UK import charges are confirmed with your quote before you commit, so there are no surprises at delivery."),
      ("Is made-to-measure safe to order online?",
       "Measurements are video-guided and the finished piece is reviewed on photos and video before shipping — a fitting, minus the flight."),
    ]},
}

def nri_country_page(cc):
    m = COUNTRY_META[cc]
    faq_html, schema = _faq_block(m["faqs"])
    bc = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":DOMAIN+"/"},
        {"@type":"ListItem","position":2,"name":"NRI Brides","item":DOMAIN+"/nri-brides/"},
        {"@type":"ListItem","position":3,"name":m["label"].replace("the ","").upper() if cc!="usa" else "USA"}]}
    facts = "".join([
      _nri_fact("Shipping", f"shipping.{cc}", "carrier, time and cost confirmed with your quote"),
      _nri_fact("Bridal range", f"priceRange.{cc}", "quoted per design — share your budget in the first chat"),
      _nri_fact("Payment", "payment", "discussed and confirmed on WhatsApp before work begins"),
      _nri_fact("Typical timeline", "timeline", "confirmed on enquiry — share your wedding date first"),
    ])
    bridal = [d for d in designs if d["category"] == "bridal"][:6]
    cards = "".join(card(d) for d in bridal)
    return head(m["title"], m["desc"], f"/nri-brides/{cc}/", "/assets/og.jpg", [schema, bc]) + nav("") + f"""
  <section class="cat-hero">
    <div class="cat-hero-bg" data-parallax data-speed="0.16"></div>
    <div class="wrap center">
      <p class="eyebrow" data-reveal style="--i:0">NRI Brides &middot; {esc(m["label"].title().replace("The ","The "))}</p>
      <h1 data-reveal style="--i:1">{m["h1"]}</h1>
      <p class="lead center" data-reveal style="--i:2">{esc(m["lead"])}</p>
      <div class="hero-actions" data-reveal style="--i:3;justify-content:center">
        <a href="https://wa.me/{WA}" class="btn btn-primary" rel="noopener">{wa_cta_label()}</a>
        <a href="/how-it-works/" class="btn btn-ghost">How it works</a>
      </div>
    </div>
  </section>
  <section class="section-soft" style="padding-block:clamp(46px,6vw,80px)">
    <div class="wrap center">
      <p class="eyebrow" data-reveal>Ordering from {esc(m["label"])}</p>
      <h2 data-reveal style="font-size:clamp(26px,4vw,42px);margin:8px 0 22px">The practical details</h2>
      <ul class="nri-facts" data-reveal>{facts}</ul>
    </div>
  </section>
  <section class="catsec">
    <div class="wrap">
      <header class="catsec-head">
        <div class="catsec-head-main">
          <h2 data-reveal>Bridal designs to start from</h2>
          <p class="lead" data-reveal style="--i:1">Every piece customisable in colour, fabric and embroidery — or bring your own reference.</p>
          {price_from("bridal")}
        </div>
      </header>
      <div class="dgrid">
{cards}      </div>
      <div class="center" style="margin-top:30px"><a href="/catalogue/" class="btn btn-ghost" data-reveal>View the full catalogue</a></div>
    </div>
  </section>
  <section class="faq section-soft">
    <div class="wrap">
      <div class="center"><p class="eyebrow" data-reveal>Good to know</p>
      <h2 data-reveal style="font-size:clamp(26px,4vw,42px);margin-top:8px">Questions from {esc(m["label"])}</h2></div>
      <div class="faq-list">{faq_html}</div>
      <div class="hero-actions" style="justify-content:center;margin-top:30px" data-reveal>
        <a href="https://wa.me/{WA}" class="btn btn-primary" rel="noopener">{wa_cta_label()}</a>
        <a href="/nri-brides/" class="btn btn-ghost">All NRI info</a>
      </div>
    </div>
  </section>
""" + FOOTER + '  <script src="/app.js?v=23" defer></script>\n  <script src="/catalogue.js?v=23" defer></script>\n</body>\n</html>\n'

def inject_showcase():
    import re
    idx = ROOT/"index.html"; src = idx.read_text()
    block = "<!-- SHOWCASE:START -->\n" + home_showcase() + "\n  <!-- SHOWCASE:END -->"
    new = re.sub(r"<!-- SHOWCASE:START -->.*?<!-- SHOWCASE:END -->", lambda m: block, src, flags=re.S)
    cblock = "<!-- CAMPAIGN:START -->\n" + home_campaign() + "\n  <!-- CAMPAIGN:END -->"
    new = re.sub(r"<!-- CAMPAIGN:START -->.*?<!-- CAMPAIGN:END -->", lambda m: cblock, new, flags=re.S)
    tblock = "<!-- TESTIMONIALS:START -->\n" + testimonials_html() + "\n  <!-- TESTIMONIALS:END -->"
    new = re.sub(r"<!-- TESTIMONIALS:START -->.*?<!-- TESTIMONIALS:END -->", lambda m: tblock, new, flags=re.S)
    idx.write_text(new)
    print("injected home showcase + campaign slider")

def write_sitemap_robots():
    if not DOMAIN:
        print("DOMAIN unset — skipping sitemap/robots"); return
    today = datetime.date.today().isoformat()
    urls = (["/", "/catalogue/", "/about/", "/contact/", "/navratri-outfits-ahmedabad/"]
            + EXTRA_PAGES + [f"/catalogue/{d['slug']}/" for d in designs])
    def row(u):
        pr = "1.0" if u == "/" else ("0.9" if u == "/catalogue/" else "0.7")
        cf = "weekly" if u in ("/", "/catalogue/") else "monthly"
        return f"  <url><loc>{DOMAIN}{u}</loc><lastmod>{today}</lastmod><changefreq>{cf}</changefreq><priority>{pr}</priority></url>"
    (ROOT/"sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(row(u) for u in urls) + "\n</urlset>\n")
    (ROOT/"robots.txt").write_text(
        "# Aarchi's by Archana Soni\nUser-agent: *\nAllow: /\n\n"
        f"Sitemap: {DOMAIN}/sitemap.xml\n")
    print(f"wrote sitemap.xml ({len(urls)} urls) + robots.txt")

def main():
    (ROOT/"catalogue").mkdir(exist_ok=True)
    (ROOT/"catalogue"/"index.html").write_text(catalogue_index())
    for d in designs:
        related = [r for r in designs if r["category"]==d["category"] and r["slug"]!=d["slug"]][:3]
        out = ROOT/"catalogue"/d["slug"]; out.mkdir(exist_ok=True)
        (out/"index.html").write_text(design_page(d, related))
    print(f"generated /catalogue/ + {len(designs)} design pages")
    nv = ROOT/"navratri-outfits-ahmedabad"; nv.mkdir(exist_ok=True)
    (nv/"index.html").write_text(navratri_page())
    hw = ROOT/"how-it-works"; hw.mkdir(exist_ok=True)
    (hw/"index.html").write_text(how_it_works_page())
    nb = ROOT/"nri-brides"; nb.mkdir(exist_ok=True)
    (nb/"index.html").write_text(nri_hub_page())
    for cc in COUNTRY_META:
        d = nb/cc; d.mkdir(exist_ok=True)
        (d/"index.html").write_text(nri_country_page(cc))
    inject_showcase()
    write_sitemap_robots()

if __name__ == "__main__":
    main()
