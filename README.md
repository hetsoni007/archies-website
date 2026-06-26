# Aarchi's by Archana Soni — website

Static marketing site for **Aarchi's by Archana Soni**, a women's fashion studio in
Ahmedabad ("Where tradition meets fashion"). **Catalog + enquiry** model — browse
collections, then enquire via WhatsApp / contact form. No online checkout.

- **Stack:** plain HTML/CSS/JS. **No build step.** The repo root is the deploy artifact.
- **Clean URLs** via `folder/index.html`.

## Layout
```
index.html            Home
collections/          Lookbook (grid driven by COLLECTIONS in app.js)
about/                Brand story + services
contact/              WhatsApp + enquiry form + studio details
styles.css            Design system — retheme via :root variables only
app.js                Reveal anims, mobile nav, collections renderer, form stub
assets/img/           Collection & studio photos (add real ones here)
assets/fonts/         Self-hosted display font (see "Fonts")
assets/favicon.svg    Monogram favicon (placeholder colours)
```

## ⚠️ This is a PREVIEW build — replace every placeholder before launch
A maroon **PREVIEW BUILD** banner sits at the top of each page. Delete those
`<div class="preview-banner">…</div>` blocks when the content is real.

Search the repo for these tokens and replace each:

| Token | What to put | Where |
|---|---|---|
| `[PLACEHOLDER]` | Real brand copy (hero, story, descriptions) | all pages |
| `COLLECTIONS = [...]` | Real collection names + tagline + `img` paths | `app.js` |
| `91XXXXXXXXXX` | Real WhatsApp number (country code, no `+`/spaces) | all pages (`wa.me/...`) |
| `+91 XXXXX XXXXX` | Display phone number | footers + contact |
| `hello@DOMAIN-TBD` | Real studio email | footers + contact |
| `[Studio address — Ahmedabad]` | Real address + hours | footers + contact |
| photo `.ph` tiles | Real photography (set `img` in COLLECTIONS / swap `.ph` divs) | everywhere |

**Real facts already wired in** (verified from public profiles, safe to keep):
Instagram, Facebook, Pinterest, LinkedIn links in the footers.

**Do NOT fabricate:** testimonials, pricing, metrics. The About page has a commented-out
testimonials slot — fill it only with real client quotes.

## Adding / editing collections
Edit the `COLLECTIONS` array in [`app.js`](app.js). Each entry:
```js
{ name: "Bridal Couture", tagline: "Heirloom lehengas", img: "assets/img/bridal.webp" }
```
Set `img` to a real photo path to replace the placeholder tile. Recommended image size
~600×800 (3:4), exported as **WebP**.

## Design / theming
All colours and fonts are CSS variables in `:root` at the top of `styles.css`.
Retune `--wine` / `--gold` / `--bg` to match the real logo once it's available.

### Fonts
Headings use a serif stack that falls back to Georgia. To self-host the intended
display face (e.g. Cormorant Garamond), drop the `.woff2` in `assets/fonts/`, add an
`@font-face` in `styles.css`, and it'll pick up automatically via `--font-display`.

## Local preview
Any static server, e.g.:
```bash
cd ~/Projects/Aarchis && python3 -m http.server 8080
# open http://localhost:8080
```

## Deploy (TBD)
Domain not yet chosen. Once decided: set canonical/OG URLs, add the `Sitemap:` line to
`robots.txt`, generate `sitemap.xml`, and host (e.g. AWS S3 + CloudFront, mirroring the
SCS pipeline). Wire the contact form by setting `ENQUIRY_ENDPOINT` in `app.js` to a
backend, or keep WhatsApp-only and remove the form.
