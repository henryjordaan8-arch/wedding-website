#!/usr/bin/env python3
"""
Build a complete wedding website from a client's order file.

    python3 builder/build.py builder/clients/<slug>/order.json

Input  : builder/clients/<slug>/order.json   (the "build file" from the order form)
         builder/clients/<slug>/photos/      (optional: hero.jpg + gallery photos)
Output : builder/sites/<slug>/               (static site, ready to host)

The script prints a checklist of anything missing so it can be chased up.
Only the standard library is required; Pillow is used to resize photos if present.
"""
import argparse
import hashlib
import html
import json
import re
import shutil
import sys
import unicodedata
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "template"

try:
    from PIL import Image, ImageOps
except ImportError:  # photos are copied as-is without Pillow
    Image = None

# --------------------------------------------------------------------------
# Themes
# --------------------------------------------------------------------------
PALETTES = {
    "navy":       dict(bg="#faf7f0", bg_alt="#f2ede2", bg_deep="#e2dacb", primary="#1c2d4a", primary_dark="#111e33", primary_light="#3d5276", secondary="#a88a5c", secondary_dark="#86693f", secondary_light="#cdb68e", text="#1e2635", text_light="#5a6271"),
    "burgundy":   dict(bg="#f9f4ea", bg_alt="#f1e9d8", bg_deep="#e8dcc4", primary="#722f37", primary_dark="#551f26", primary_light="#9a4b53", secondary="#2f4f3c", secondary_dark="#1f3529", secondary_light="#6a8f7a", text="#3b2f28", text_light="#6b5f54"),
    "sage":       dict(bg="#f7f5ee", bg_alt="#eceee2", bg_deep="#d9ddca", primary="#55664a", primary_dark="#3d4b35", primary_light="#7d8f6e", secondary="#b0955f", secondary_dark="#8c7443", secondary_light="#d2bf94", text="#2f342b", text_light="#646a5d"),
    "dusty-blue": dict(bg="#f7f8f9", bg_alt="#eaeff3", bg_deep="#d5dee6", primary="#4a6580", primary_dark="#344a60", primary_light="#7590a9", secondary="#8e959c", secondary_dark="#6c737a", secondary_light="#b8bec4", text="#26313b", text_light="#5e6a75"),
    "blush":      dict(bg="#fcf7f4", bg_alt="#f7ebe6", bg_deep="#ecd6ce", primary="#a45f5a", primary_dark="#7f4440", primary_light="#d9a5a0", secondary="#b8924f", secondary_dark="#93733a", secondary_light="#dcc394", text="#3d2e2b", text_light="#76625d"),
    "terracotta": dict(bg="#faf5ee", bg_alt="#f2e7d9", bg_deep="#e5d3bd", primary="#a5532f", primary_dark="#7d3c20", primary_light="#c97c58", secondary="#6b5a3e", secondary_dark="#4f412b", secondary_light="#a4916f", text="#3a2b20", text_light="#6f5e50"),
    "classic":    dict(bg="#fbfbfa", bg_alt="#f1f1ef", bg_deep="#dcdcd8", primary="#1d1d1d", primary_dark="#000000", primary_light="#4a4a4a", secondary="#8a8a8a", secondary_dark="#666666", secondary_light="#b5b5b5", text="#222222", text_light="#5f5f5f"),
}

FONTS = {
    # key: (google fonts query, heading, body, names)
    "classic":  ("family=Playfair+Display:ital,wght@0,500;0,700;1,500&family=Lato:wght@300;400;700",
                 "'Playfair Display', Georgia, serif", "'Lato', 'Helvetica Neue', Arial, sans-serif", "'Playfair Display', Georgia, serif"),
    "modern":   ("family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Jost:wght@300;400;500",
                 "'Cormorant Garamond', Georgia, serif", "'Jost', 'Helvetica Neue', Arial, sans-serif", "'Cormorant Garamond', Georgia, serif"),
    "romantic": ("family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Great+Vibes&family=Lato:wght@300;400;700",
                 "'Cormorant Garamond', Georgia, serif", "'Lato', 'Helvetica Neue', Arial, sans-serif", "'Great Vibes', 'Cormorant Garamond', cursive"),
}

# --------------------------------------------------------------------------
# Wording (English / Afrikaans)
# --------------------------------------------------------------------------
T = {
    "en": dict(
        lang="en", months="January February March April May June July August September October November December",
        nav=dict(index="Home", details="Details", venue="Venue", accommodation="Stay", gallery="Gallery", registry="Registry", faq="FAQ", rsvp="RSVP"),
        toggle="Toggle navigation", and_word="&amp;",
        tagline="are getting married!", date="Date", place="Venue", dress="Dress code",
        days="Days", hours="Hours", minutes="Minutes", seconds="Seconds", countdown="Countdown to the wedding",
        rsvp_now="RSVP now", welcome="Welcome",
        welcome_text="We are so excited to celebrate our wedding day with the people we love most. Here you'll find everything you need to know about the day &mdash; from the programme and venue to places to stay. Have a look around, and don't forget to RSVP!",
        cards=dict(details="Ceremony, reception &amp; programme.", venue="How to get there.", accommodation="Places to stay nearby.",
                   gallery="Our photos.", registry="Gifts &amp; contributions.", faq="Good to know.", rsvp="Let us know if you can make it."),
        details_eyebrow="Details", details_title="Ceremony &amp; Reception", programme="Programme of the Day",
        reception="Reception", venue_eyebrow="Venue", map_open="Open in Google Maps", map_title="Map to",
        stay_eyebrow="Accommodation", stay_title="Where to Stay", stay_intro="Here are a few suggestions for places to stay near {venue}.",
        book="Visit website", gallery_eyebrow="Gallery", gallery_title="Our Photos",
        gate_intro="Answer the question(s) below to unlock our photos.", unlock="Unlock",
        gate_error="One or more answers are wrong &mdash; please try again.", photos_soon="Photos coming soon!",
        registry_eyebrow="Gifts", registry_title="Gifts &amp; Registry",
        registry_text="Your presence at our wedding is the greatest gift of all. For those who would like to give something extra, you'll find the details below.",
        contribute="Contribute", view_registry="View registry",
        faq_eyebrow="Questions", faq_title="Frequently Asked Questions",
        rsvp_eyebrow="RSVP", rsvp_title="We Hope You Can Join Us",
        rsvp_intro="Please let us know whether you'll be celebrating with us by {deadline}. It only takes a minute!",
        rsvp_intro_nodl="Please let us know whether you'll be celebrating with us. It only takes a minute!",
        f_name="Full name(s)", f_attending="Will you be attending?", f_yes="Joyfully accepts", f_no="Regretfully declines",
        f_guests="Number of guests (including you)", f_dietary="Dietary requirements", f_meal="Meal preference",
        f_song="Song request", f_message="Message for the couple", f_phone="Phone number", f_send="Send RSVP",
        sending="Sending&hellip;", thanks="Thank you! Your RSVP has been sent.",
        fallback="We've opened WhatsApp with your RSVP &mdash; just press send.",
        error="Something went wrong. Please contact us directly.",
        rsvp_help="Trouble with the form? Contact us at", rsvp_whatsapp="RSVP on WhatsApp",
        whatsapp_intro="Send us your RSVP on WhatsApp &mdash; tap the button below.",
        footer_note="We can't wait to celebrate with you.",
        invited="Together with their families", tap_open="Tap to open", skip="Skip",
    ),
    "af": dict(
        lang="af", months="Januarie Februarie Maart April Mei Junie Julie Augustus September Oktober November Desember",
        nav=dict(index="Tuis", details="Besonderhede", venue="Venue", accommodation="Verblyf", gallery="Foto's", registry="Geskenklys", faq="Vrae", rsvp="RSVP"),
        toggle="Wissel navigasie", and_word="en",
        tagline="gaan trou!", date="Datum", place="Plek", dress="Kleredrag",
        days="Dae", hours="Ure", minutes="Minute", seconds="Sekondes", countdown="Aftelling tot die troue",
        rsvp_now="RSVP nou", welcome="Welkom",
        welcome_text="Ons is opgewonde om ons troudag saam met die mense wat ons die meeste liefhet, te vier. Hier vind jy alles wat jy moet weet oor ons viering &mdash; van die program en die plek tot verblyf. Blaai gerus deur die bladsye, en moenie vergeet om te RSVP nie!",
        cards=dict(details="Seremonie, onthaal &amp; program.", venue="Hoe om daar te kom.", accommodation="Waar om te bly.",
                   gallery="Ons foto's.", registry="Geskenke &amp; bydraes.", faq="Goed om te weet.", rsvp="Laat weet ons of jy kom."),
        details_eyebrow="Besonderhede", details_title="Seremonie &amp; Onthaal", programme="Program vir die Dag",
        reception="Onthaal", venue_eyebrow="Venue", map_open="Maak oop in Google Maps", map_title="Kaart na",
        stay_eyebrow="Verblyf", stay_title="Waar om te Bly", stay_intro="Hieronder is 'n paar voorstelle vir plekke om naby {venue} te bly.",
        book="Besoek webwerf", gallery_eyebrow="Foto's", gallery_title="Ons Foto's",
        gate_intro="Beantwoord die vra(e) hieronder om ons foto's te ontsluit.", unlock="Ontsluit",
        gate_error="Een of meer antwoorde is verkeerd &mdash; probeer weer.", photos_soon="Foto's kom binnekort!",
        registry_eyebrow="Geskenklys", registry_title="Geskenke &amp; Geskenklys",
        registry_text="Jou teenwoordigheid by ons troue is die grootste geskenk vir ons. Vir diegene wat iets ekstra wil gee, is die besonderhede hieronder.",
        contribute="Bydrae", view_registry="Sien geskenklys",
        faq_eyebrow="Vrae", faq_title="Gereelde Vrae",
        rsvp_eyebrow="RSVP", rsvp_title="Ons Hoop Jy Kan By Ons Aansluit",
        rsvp_intro="Laat weet ons asseblief teen {deadline} of jy saam met ons gaan vier. Dit neem net 'n minuut!",
        rsvp_intro_nodl="Laat weet ons asseblief of jy saam met ons gaan vier. Dit neem net 'n minuut!",
        f_name="Volle naam/name", f_attending="Sal jy die troue bywoon?", f_yes="Ja, ek sal daar wees", f_no="Ongelukkig nie",
        f_guests="Aantal gaste (jy ingesluit)", f_dietary="Dieetvereistes", f_meal="Maaltydkeuse",
        f_song="Liedjieversoek", f_message="Boodskap vir die paartjie", f_phone="Telefoonnommer", f_send="Stuur RSVP",
        sending="Besig om te stuur&hellip;", thanks="Dankie! Jou RSVP is gestuur.",
        fallback="Ons het WhatsApp met jou RSVP oopgemaak &mdash; druk net stuur.",
        error="Iets het verkeerd gegaan. Kontak ons asseblief direk.",
        rsvp_help="Sukkel met die vorm? Kontak ons by", rsvp_whatsapp="RSVP op WhatsApp",
        whatsapp_intro="Stuur vir ons jou RSVP op WhatsApp &mdash; druk die knoppie hieronder.",
        footer_note="Ons kan nie wag om saam met jou te vier nie.",
        invited="Saam met hul families", tap_open="Tik om oop te maak", skip="Slaan oor",
    ),
}

ICONS = {
    "details": '<rect x="3.5" y="5" width="17" height="15" rx="1.5"/><path d="M3.5 9.5h17M8 3v4M16 3v4M7.5 13h3M13.5 13h3M7.5 16.5h3"/>',
    "venue": '<path d="M12 21s-6.5-6-6.5-11a6.5 6.5 0 0 1 13 0c0 5-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.3"/>',
    "accommodation": '<path d="M3 20.5h18M5 20.5V8.5l7-4.5 7 4.5v12M9.5 20.5v-5h5v5M8.5 11h1M14.5 11h1"/>',
    "gallery": '<rect x="3" y="7" width="18" height="13" rx="1.5"/><circle cx="12" cy="13.5" r="3.5"/><path d="M8.5 7l1.5-2.5h4L15.5 7"/>',
    "registry": '<rect x="3.5" y="9" width="17" height="11.5" rx="1"/><path d="M2.5 9h19M12 9v11.5M12 9c-1.5-3-5-4-5-1.5S10 9 12 9zM12 9c1.5-3 5-4 5-1.5S14 9 12 9z"/>',
    "faq": '<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .8-1 1.5v.7M12 17h.01"/>',
    "rsvp": '<rect x="3" y="6" width="18" height="13" rx="1.5"/><path d="M3.5 7l8.5 6.5L20.5 7"/>',
    "dress": '<path d="M9 3l3 3 3-3M9 3L6 6l2 3-2 12h12L16 9l2-3-3-3"/>',
}
INTROS = {"none", "envelope", "monogram"}
PAGE_ORDER = ["details", "venue", "accommodation", "gallery", "registry", "faq", "rsvp"]


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def esc(s):
    return html.escape(str(s or "").strip())


def para(s):
    """Escape multi-line text and keep line breaks."""
    return "<br>".join(esc(line) for line in str(s or "").strip().splitlines())


def slugify(*parts):
    s = "-".join(p for p in parts if p)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "wedding"


def nice_date(iso, t):
    try:
        d = date.fromisoformat(iso)
    except (TypeError, ValueError):
        return esc(iso)
    return f"{d.day} {t['months'].split()[d.month - 1]} {d.year}"


def whatsapp_number(phone):
    digits = re.sub(r"\D", "", phone or "")
    if digits.startswith("0") and len(digits) == 10:  # South African local format
        digits = "27" + digits[1:]
    return digits


def svg(name):
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


def sha(text):
    norm = re.sub(r"\s+", " ", text.strip().lower())
    return hashlib.sha256(norm.encode()).hexdigest()


def rows(items, *required):
    """Drop repeater rows that are empty or miss a required key."""
    out = []
    for it in items or []:
        if not isinstance(it, dict):
            continue
        if any(str(v).strip() for v in it.values()) and all(str(it.get(k, "")).strip() for k in required):
            out.append(it)
    return out


# --------------------------------------------------------------------------
# Photos
# --------------------------------------------------------------------------
IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".heic"}


def process_photos(src_dir, out_dir, warn):
    """Return (hero, [gallery]) as lists of dicts {src, w, h}."""
    files = sorted(p for p in src_dir.glob("*") if p.suffix.lower() in IMG_EXT) if src_dir.is_dir() else []
    if not files:
        return None, []
    (out_dir / "images" / "gallery").mkdir(parents=True, exist_ok=True)

    def save(src, dest_rel, max_side):
        dest = out_dir / dest_rel
        if Image is None:
            shutil.copy2(src, dest.with_suffix(src.suffix.lower()))
            return {"src": str(Path(dest_rel).with_suffix(src.suffix.lower())), "w": None, "h": None}
        try:
            im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        except Exception as e:  # unreadable (e.g. HEIC without plugin)
            warn(f"Could not read photo {src.name}: {e}. Convert it to JPG.")
            return None
        im.thumbnail((max_side, max_side))
        im.save(dest.with_suffix(".jpg"), "JPEG", quality=82, optimize=True, progressive=True)
        return {"src": str(Path(dest_rel).with_suffix(".jpg")), "w": im.width, "h": im.height}

    hero_file = next((p for p in files if p.stem.lower() == "hero"), files[0])
    hero = save(hero_file, "images/hero.jpg", 1800)
    gallery_files = [p for p in files if p != hero_file] or [hero_file]
    gallery = []
    for i, p in enumerate(gallery_files, 1):
        g = save(p, f"images/gallery/photo-{i:02d}.jpg", 1600)
        if g:
            gallery.append(g)
    return hero, gallery


# --------------------------------------------------------------------------
# Page building
#
# Every section (details, venue, ...) is produced once as a dict:
#   {eyebrow, title, intro, html}
# and then wrapped either as its own page (layout "multi") or stacked
# into one long index.html (layout "single").
# --------------------------------------------------------------------------
class Site:
    def __init__(self, order, slug, out_dir, photos_dir):
        self.o = order
        self.slug = slug
        self.out = out_dir
        self.warnings = []
        c = order.get("couple", {})
        w = order.get("wedding", {})
        s = order.get("style", {})
        self.p1, self.p2 = c.get("partner1", "").strip(), c.get("partner2", "").strip()
        self.t = T.get(s.get("language", "en"), T["en"])
        self.w = w
        self.s = s
        self.single = s.get("layout") == "single"
        self.intro = s.get("intro") if s.get("intro") in INTROS else "none"
        self.animate = bool(s.get("animations"))
        self.pages = [p for p in PAGE_ORDER if p in (order.get("pages") or PAGE_ORDER)]
        self.date_str = nice_date(w.get("date"), self.t)
        self.place = ", ".join(x for x in [w.get("venue", "").strip(), w.get("town", "").strip()] if x)
        self.hero, self.gallery = process_photos(photos_dir, out_dir, self.warn)

    def warn(self, msg):
        self.warnings.append(msg)

    def href(self, page):
        if self.single:
            return "#top" if page == "index" else f"#{page}"
        return f"{page}.html"

    @property
    def reveal(self):
        return " reveal" if self.animate else ""

    # ---- shared layout ----
    def monogram(self):
        return f'{esc(self.p1[:1])} <span class="amp">&amp;</span> {esc(self.p2[:1])}'

    def intro_overlay(self):
        t = self.t
        names = f"{esc(self.p1)} <span class=\"amp\">&amp;</span> {esc(self.p2)}"
        if self.intro == "envelope":
            return f"""  <div class="opening opening-envelope" id="opening" aria-hidden="false">
    <div class="env-stage">
      <div class="env">
        <div class="env-back"></div>
        <div class="env-letter">
          <p class="env-small">{t['invited']}</p>
          <p class="env-names">{names}</p>
          <p class="env-date">{self.date_str}</p>
        </div>
        <div class="env-front"></div>
        <div class="env-flap"></div>
        <button type="button" class="env-seal" id="opening-open" aria-label="{t['tap_open']}">{esc(self.p1[:1])}<span>&amp;</span>{esc(self.p2[:1])}</button>
      </div>
      <p class="env-hint">{t['tap_open']}</p>
    </div>
    <button type="button" class="opening-skip" id="opening-skip">{t['skip']}</button>
  </div>
"""
        if self.intro == "monogram":
            return f"""  <div class="opening opening-monogram" id="opening" aria-hidden="false">
    <div class="mono-stage">
      <p class="mono-letters">{esc(self.p1[:1])}<span>&amp;</span>{esc(self.p2[:1])}</p>
      <span class="mono-line"></span>
      <p class="mono-names">{names}</p>
      <p class="mono-date">{self.date_str}</p>
    </div>
    <button type="button" class="opening-skip" id="opening-skip">{t['skip']}</button>
  </div>
"""
        return ""

    def layout(self, page, title, body):
        t, nav = self.t, self.t["nav"]
        rsvp_cls = ' class="nav-rsvp"'
        links = [("index", self.href("index"))] + [(p, self.href(p)) for p in self.pages]
        items = "\n".join(
            f'          <li><a href="{href}"{rsvp_cls if key == "rsvp" else ""}>{nav[key]}</a></li>'
            for key, href in links)
        fq, fh, fb, fn = FONTS.get(self.s.get("fonts"), FONTS["classic"])
        names = f"{esc(self.p1)} &amp; {esc(self.p2)}"
        desc = f"{names} &middot; {self.date_str}" + (f" &middot; {esc(self.place)}" if self.place else "")
        intro = self.intro_overlay() if page == "index" else ""
        # Runs before paint: enables reveal animations and hides the intro if already seen this visit
        head_js = "document.documentElement.classList.add('js');"
        if intro:
            head_js += ("try{if(sessionStorage.getItem('openingSeen')||matchMedia('(prefers-reduced-motion: reduce)').matches)"
                        "document.documentElement.classList.add('opening-seen')}catch(e){}")
        body_cls = ' class="one-page"' if self.single else ""
        return f"""<!DOCTYPE html>
<html lang="{t['lang']}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title + ' | ' if title else ''}{names} &middot; {self.date_str}</title>
  <meta name="description" content="{desc}">
  <meta property="og:title" content="{names}">
  <meta property="og:description" content="{desc}">
  {'<meta property="og:image" content="images/hero.jpg">' if self.hero else ''}
  <script>{head_js}</script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?{fq}&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="css/style.css">
</head>
<body{body_cls}>
{intro}
  <header class="site-header">
    <div class="header-inner">
      <a href="{self.href('index')}" class="logo">{self.monogram()}</a>
      <nav class="main-nav" id="main-nav">
        <ul>
{items}
        </ul>
      </nav>
      <button class="nav-toggle" id="nav-toggle" aria-label="{t['toggle']}" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
    </div>
  </header>

  <main id="top">
{body}
  </main>

  <footer class="site-footer">
    <p class="footer-monogram">{esc(self.p1[:1])} &amp; {esc(self.p2[:1])}</p>
    <p>{self.date_str}{' &middot; ' + esc(self.place) if self.place else ''}</p>
    <p class="footer-note">{t['footer_note']}</p>
  </footer>

  <script src="js/site.js"></script>
</body>
</html>
"""

    def page_hero(self, eyebrow, title, intro=""):
        intro = f'      <p class="intro">{intro}</p>\n' if intro else ""
        return f"""    <section class="hero page-hero">
      <p class="hero-monogram">{eyebrow}</p>
      <h1>{title}</h1>
      <div class="divider"><span>&#10070;</span></div>
{intro}    </section>
"""

    def info_strip(self):
        t = self.t
        items = [(t["date"], self.date_str)]
        if self.place:
            items.append((t["place"], esc(self.place)))
        if self.w.get("dress_code"):
            items.append((t["dress"], esc(self.w["dress_code"])))
        inner = "\n".join(
            f'      <div class="info-item">\n        <span class="info-label">{a}</span>\n        <span class="info-value">{b}</span>\n      </div>'
            for a, b in items)
        return f'    <div class="info-strip">\n{inner}\n    </div>\n'

    def block(self, inner, width=None, extra_cls=""):
        style = f' style="max-width:{width};"' if width else ""
        return f'      <div class="block{self.reveal}{extra_cls}"><div class="container"{style}>\n{inner}\n      </div></div>\n'

    # ---- sections ----
    def sec_details(self):
        t = self.t
        prog = rows(self.o.get("programme"), "title")
        if not prog:
            self.warn("Programme is empty — the Details section will show no timeline.")
        out = ""
        if prog:
            items = "\n".join(
                f'          <div class="timeline-item"><span class="timeline-time">{esc(i.get("time"))}</span><h3>{esc(i.get("title"))}</h3>'
                + (f'<p class="muted">{para(i.get("note"))}</p>' if i.get("note") else "") + "</div>"
                for i in prog)
            out += self.block(f'        <h2 class="section-title center">{t["programme"]}</h2>\n'
                              f'        <div class="timeline">\n{items}\n        </div>', "760px")
        cards = []
        if self.w.get("dress_code") or self.w.get("dress_notes"):
            notes = "<br>" + para(self.w.get("dress_notes")) if self.w.get("dress_notes") else ""
            cards.append(f'<div class="card"><div class="card-icon">{svg("dress")}</div><h3>{t["dress"]}</h3><p class="muted">{esc(self.w.get("dress_code"))}{notes}</p></div>')
        if self.w.get("reception_venue"):
            cards.append(f'<div class="card"><div class="card-icon">{svg("venue")}</div><h3>{t["reception"]}</h3><p class="muted">{para(self.w.get("reception_venue"))}</p></div>')
        if cards:
            out += self.block('        <div class="card-grid">\n          ' + "\n          ".join(cards) + "\n        </div>", "800px")
        return dict(eyebrow=t["details_eyebrow"], title=t["details_title"], intro="", html=out)

    def sec_venue(self):
        t, w = self.t, self.w
        query = w.get("address") or self.place
        if not query:
            self.warn("No venue name or address — the map can't be shown.")
        is_link = str(query).startswith("http")
        maps = query if is_link else "https://www.google.com/maps/search/?api=1&query=" + html.escape((query or "").replace(" ", "+"))
        embed_q = self.place if is_link else query
        embed = "https://www.google.com/maps?q=" + html.escape((embed_q or "").replace(" ", "+")) + "&output=embed"
        address = esc(w.get("address")) if w.get("address") and not is_link else ""
        inner = f"""        <div class="rsvp-form-wrap map-wrap">
          <iframe title="{t['map_title']} {esc(w.get('venue'))}" src="{embed}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
        </div>
        {f'<p class="venue-address">{address}</p>' if address else ''}
        <p class="center" style="margin-top:1.5rem;"><a class="btn btn-outline" href="{maps}" target="_blank" rel="noopener">{t['map_open']}</a></p>"""
        title = esc(w.get("venue")) or t["nav"]["venue"]
        return dict(eyebrow=t["venue_eyebrow"], title=title, intro=esc(w.get("town")), html=self.block(inner, "700px", " center"))

    def sec_accommodation(self):
        t = self.t
        places = rows(self.o.get("accommodation"), "name")
        if not places:
            self.warn("No accommodation listed — consider removing the Stay section or adding places.")
        cards = []
        for p in places:
            lines = []
            if p.get("note"):
                lines.append(para(p["note"]))
            if p.get("phone"):
                lines.append(f'<a href="tel:{re.sub(r"[^0-9+]", "", p["phone"])}">{esc(p["phone"])}</a>')
            if p.get("email"):
                lines.append(f'<a href="mailto:{esc(p["email"])}">{esc(p["email"])}</a>')
            web = p.get("website", "").strip()
            if web and not web.startswith("http"):
                web = "https://" + web
            btn = f'<a href="{esc(web)}" target="_blank" rel="noopener" class="btn btn-outline" style="margin-top:0.5rem;">{t["book"]}</a>' if web else ""
            cards.append(f'          <div class="card"><div class="card-icon">{svg("accommodation")}</div><h3>{esc(p["name"])}</h3><p class="muted">{"<br>".join(lines)}</p>{btn}</div>')
        intro = t["stay_intro"].format(venue=esc(self.w.get("venue")) or esc(self.place))
        return dict(eyebrow=t["stay_eyebrow"], title=t["stay_title"], intro=intro,
                    html=self.block('        <div class="card-grid">\n' + "\n".join(cards) + "\n        </div>"))

    def sec_gallery(self):
        t = self.t
        lock = rows((self.o.get("photos") or {}).get("gallery_lock"), "question", "answer")
        if not self.gallery:
            self.warn("No photos in photos/ — gallery shows 'coming soon' and the home page has no photo.")
            grid = f'<p class="intro">{t["photos_soon"]}</p>'
        else:
            imgs = "\n".join(
                f'            <a href="{g["src"]}" target="_blank" rel="noopener"><img src="{g["src"]}" alt="{esc(self.p1)} &amp; {esc(self.p2)}"'
                + (f' width="{g["w"]}" height="{g["h"]}"' if g["w"] else "")
                + f' loading="{"eager" if i < 4 and not self.single else "lazy"}" decoding="async"></a>'
                for i, g in enumerate(self.gallery))
            grid = f'<div class="gallery-masonry">\n{imgs}\n          </div>'
        gate = ""
        if lock:
            qs = "\n".join(
                f'            <label class="gate-label" for="gate-q{i}">{esc(q["question"])}</label>\n'
                f'            <input class="gate-input" type="text" id="gate-q{i}" autocomplete="off" data-hash="{sha(q["answer"])}">'
                for i, q in enumerate(lock, 1))
            gate = f"""        <div class="gallery-gate-card" id="gallery-gate" style="max-width:480px;margin:0 auto;">
          <p class="muted center" style="margin-bottom:1.6rem;">{t['gate_intro']}</p>
          <form id="gallery-gate-form" novalidate>
{qs}
            <button type="submit" class="btn" style="width:100%;margin-top:0.5rem;">{t['unlock']}</button>
            <p id="gate-error" class="gate-error" style="display:none;">{t['gate_error']}</p>
          </form>
        </div>
"""
        content = f'        <div id="gallery-content"{" style=\"display:none;\"" if lock else ""}>\n          {grid}\n        </div>'
        return dict(eyebrow=t["gallery_eyebrow"], title=t["gallery_title"], intro="", html=self.block(gate + content))

    def sec_registry(self):
        t = self.t
        reg = self.o.get("registry") or {}
        cards = []
        for l in rows(reg.get("links"), "url"):
            url = l["url"].strip()
            if not url.startswith("http"):
                url = "https://" + url
            cards.append(f'          <div class="card"><div class="card-icon">{svg("registry")}</div><h3>{esc(l.get("title")) or t["nav"]["registry"]}</h3>'
                         f'<a href="{esc(url)}" target="_blank" rel="noopener" class="btn btn-outline" style="margin-top:0.5rem;">{t["view_registry"]}</a></div>')
        if reg.get("bank_details"):
            cards.append(f'          <div class="card"><div class="card-icon">{svg("registry")}</div><h3>{t["contribute"]}</h3><p class="muted">{para(reg["bank_details"])}</p></div>')
        if not cards:
            self.warn("Registry section has no links or bank details.")
        width = "420px" if len(cards) == 1 else "800px"
        return dict(eyebrow=t["registry_eyebrow"], title=t["registry_title"], intro=para(reg.get("message")) or t["registry_text"],
                    html=self.block('        <div class="card-grid">\n' + "\n".join(cards) + "\n        </div>", width))

    def sec_faq(self):
        t = self.t
        faqs = rows(self.o.get("faqs"), "q", "a")
        if not faqs:
            self.warn("No FAQs with answers — consider removing the FAQ section.")
        items = "\n".join(f"""          <div class="faq-item">
            <button class="faq-question" aria-expanded="false"><span>{esc(f['q'])}</span><span class="faq-icon">+</span></button>
            <div class="faq-answer"><p>{para(f['a'])}</p></div>
          </div>""" for f in faqs)
        return dict(eyebrow=t["faq_eyebrow"], title=t["faq_title"], intro="",
                    html=self.block(f'        <div class="faq-list">\n{items}\n        </div>'))

    def sec_rsvp(self):
        t = self.t
        r = self.o.get("rsvp") or {}
        c = self.o.get("couple") or {}
        method = r.get("method") or "website"
        phone = c.get("phone", "")
        wa = whatsapp_number(phone)
        deadline = nice_date(self.w.get("rsvp_deadline"), t) if self.w.get("rsvp_deadline") else ""
        intro = t["rsvp_intro"].format(deadline=deadline) if deadline else t["rsvp_intro_nodl"]
        if not deadline:
            self.warn("No RSVP deadline given.")
        help_line = f'        <p class="rsvp-help">{t["rsvp_help"]} <a href="tel:{re.sub(r"[^0-9+]", "", phone)}">{esc(phone)}</a>.</p>' if phone else ""

        if method == "google_form" and r.get("google_form_url"):
            url = r["google_form_url"].strip()
            if "embedded=true" not in url:
                url += ("&" if "?" in url else "?") + "embedded=true"
            inner = f'        <div class="rsvp-form-wrap"><iframe title="RSVP" src="{esc(url)}" loading="lazy"></iframe></div>\n{help_line}'
        elif method == "whatsapp":
            if not wa:
                self.warn("RSVP by WhatsApp chosen but no phone number given.")
            inner = (f'        <p class="intro">{t["whatsapp_intro"]}</p>\n'
                     f'        <p class="center" style="margin-top:1.5rem;"><a class="btn" href="https://wa.me/{wa}?text=RSVP%20-%20" target="_blank" rel="noopener">{t["rsvp_whatsapp"]}</a></p>')
        else:
            if method == "google_form":
                self.warn("Google Form chosen but no form link given — using the built-in RSVP form instead.")
            email = (r.get("email") or c.get("email") or "").strip()
            if not email:
                self.warn("No email for RSVPs — they will only go to WhatsApp.")
            else:
                self.warn(f"RSVP emails go to {email} via FormSubmit: send one test RSVP, then the couple must click 'Activate' in the email FormSubmit sends them.")
            qs = set(r.get("questions") or ["guests", "dietary"])
            names = f"{self.p1} & {self.p2}"
            f = [
                f'<div class="field"><label for="r-name">{t["f_name"]}</label><input type="text" id="r-name" name="{t["f_name"]}" required></div>',
                f'<div class="field"><span class="label">{t["f_attending"]}</span><div class="choice-row"><label><input type="radio" name="{t["f_attending"]}" value="{t["f_yes"]}" required> {t["f_yes"]}</label><label><input type="radio" name="{t["f_attending"]}" value="{t["f_no"]}"> {t["f_no"]}</label></div></div>',
            ]
            if "guests" in qs:
                f.append(f'<div class="field"><label for="r-guests">{t["f_guests"]}</label><input type="number" id="r-guests" name="{t["f_guests"]}" min="1" max="10" value="1"></div>')
            f.append(f'<div class="field"><label for="r-phone">{t["f_phone"]}</label><input type="tel" id="r-phone" name="{t["f_phone"]}"></div>')
            for key, label, tag in [("dietary", "f_dietary", "input"), ("meal", "f_meal", "input"), ("song", "f_song", "input"), ("message", "f_message", "textarea")]:
                if key in qs:
                    field = f'<textarea id="r-{key}" name="{t[label]}"></textarea>' if tag == "textarea" else f'<input type="text" id="r-{key}" name="{t[label]}">'
                    f.append(f'<div class="field"><label for="r-{key}">{t[label]}</label>{field}</div>')
            endpoint = f"https://formsubmit.co/ajax/{email}" if email else ""
            fields = "\n          ".join(f)
            inner = f"""        <form class="rsvp-card" id="rsvp-form" data-endpoint="{esc(endpoint)}" data-whatsapp="{wa}"
              data-sending="{t['sending']}" data-thanks="{t['thanks']}" data-fallback="{t['fallback']}" data-error="{t['error']}">
          <input type="hidden" name="_subject" value="RSVP — {esc(names)}">
          <input type="hidden" name="_template" value="table">
          {fields}
          <button type="submit" class="btn" style="width:100%;">{t['f_send']}</button>
          <p class="rsvp-status" id="rsvp-status" role="status" aria-live="polite"></p>
        </form>
{help_line}"""
        return dict(eyebrow=t["rsvp_eyebrow"], title=t["rsvp_title"], intro=intro, html=self.block(inner))

    # ---- home ----
    def home_top(self):
        t, s = self.t, self.s
        headline = esc(s.get("headline")) or f'{esc(self.p1)} <span class="names-amp">{t["and_word"]}</span> {esc(self.p2)}'
        tagline = esc(s.get("tagline")) or t["tagline"]
        welcome = para(s.get("welcome")) or t["welcome_text"]
        time = (self.w.get("ceremony_time") or "15:00")[:5]
        target = f"{self.w.get('date')}T{time}:00+02:00"
        photo = f'      <div class="hero-photo">\n        <img src="{self.hero["src"]}" alt="{esc(self.p1)} &amp; {esc(self.p2)}">\n      </div>\n' if self.hero else ""
        countdown = "\n".join(
            f'        <div class="count-block"><span class="count-number" data-{k}>--</span><span class="count-label">{t[k]}</span></div>'
            for k in ["days", "hours", "minutes", "seconds"])
        rsvp_btn = f'      <a href="{self.href("rsvp")}" class="btn">{t["rsvp_now"]}</a>\n' if "rsvp" in self.pages else ""
        return f"""    <section class="hero home-hero">
      <h1 class="names" style="font-size:clamp(3rem, 6.8vw, 5.2rem);">{headline}</h1>
      <p class="tagline">{tagline}</p>
      <p class="event-line"><strong>{self.date_str}</strong>{' &middot; ' + esc(self.place) if self.place else ''}</p>
{photo}      <div class="countdown" id="countdown" data-target="{target}" aria-label="{t['countdown']}">
{countdown}
      </div>
{rsvp_btn}    </section>

{self.info_strip()}
    <section class="section{self.reveal}">
      <div class="container">
        <h2 class="section-title center">{t['welcome']}</h2>
        <div class="divider"><span>&#10070;</span></div>
        <p class="intro">{welcome}</p>
      </div>
    </section>
"""

    def home_cards(self):
        t = self.t
        cards = "\n".join(
            f'          <a href="{p}.html" class="card"><div class="card-icon">{svg(p)}</div><h3>{t["nav"][p]}</h3><p class="muted" style="font-size:0.95rem;">{t["cards"][p]}</p></a>'
            for p in self.pages)
        return f"""
    <section class="section section-alt">
      <div class="container">
        <div class="card-grid{self.reveal}">
{cards}
        </div>
      </div>
    </section>"""

    # ---- build ----
    def sections(self):
        makers = {"details": self.sec_details, "venue": self.sec_venue, "accommodation": self.sec_accommodation,
                  "gallery": self.sec_gallery, "registry": self.sec_registry, "faq": self.sec_faq, "rsvp": self.sec_rsvp}
        return {p: makers[p]() for p in self.pages}

    def build(self):
        o = self.o
        if not (self.p1 and self.p2):
            raise SystemExit("order.json needs couple.partner1 and couple.partner2")
        if not self.w.get("date"):
            raise SystemExit("order.json needs wedding.date (YYYY-MM-DD)")
        if self.s.get("palette") not in PALETTES:
            self.warn(f"Unknown palette '{self.s.get('palette')}', using navy.")
        if not self.s.get("welcome"):
            self.warn("Welcome message was blank — the default text was used. Personalise it if you like.")

        (self.out / "css").mkdir(parents=True, exist_ok=True)
        (self.out / "js").mkdir(parents=True, exist_ok=True)

        pal = PALETTES.get(self.s.get("palette"), PALETTES["navy"])
        _, fh, fb, fn = FONTS.get(self.s.get("fonts"), FONTS["classic"])
        theme = "\n  ".join(f"--{k.replace('_', '-')}: {v};" for k, v in pal.items())
        theme += f"\n  --white: #fffdf9;\n  --font-heading: {fh};\n  --font-body: {fb};\n  --font-names: {fn};"
        css = (TEMPLATE / "style.css").read_text().replace("/*THEME*/", theme)
        (self.out / "css" / "style.css").write_text(css)
        shutil.copy2(TEMPLATE / "site.js", self.out / "js" / "site.js")

        secs = self.sections()
        if self.single:
            parts = [self.home_top()]
            for i, (p, sec) in enumerate(secs.items()):
                strip = ""  # the date/venue strip already appears under the hero
                intro = f'        <p class="intro">{sec["intro"]}</p>\n' if sec["intro"] else ""
                parts.append(f"""
    <section id="{p}" class="one-sec{' one-sec-alt' if i % 2 == 0 else ''}">
      <div class="sec-head{self.reveal}">
        <p class="hero-monogram">{sec['eyebrow']}</p>
        <h2>{sec['title']}</h2>
        <div class="divider"><span>&#10070;</span></div>
{intro}      </div>
{strip}{sec['html']}    </section>""")
            (self.out / "index.html").write_text(self.layout("index", "", "".join(parts)))
        else:
            (self.out / "index.html").write_text(self.layout("index", "", self.home_top() + self.home_cards()))
            for p, sec in secs.items():
                body = self.page_hero(sec["eyebrow"], sec["title"], sec["intro"])
                if p == "details":
                    body += self.info_strip()
                body += f'\n    <section class="section page-body">\n{sec["html"]}    </section>'
                (self.out / f"{p}.html").write_text(self.layout(p, self.t["nav"][p], body))

        domain = ((o.get("domain") or {}).get("name") or "").strip().lower()
        domain = re.sub(r"^https?://", "", domain).strip("/")
        if domain and "." in domain:
            (self.out / "CNAME").write_text(domain + "\n")
        else:
            self.warn("No web address chosen yet.")
        return self.warnings


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("order", help="path to the client's order.json")
    ap.add_argument("--out", help="output folder (default: builder/sites/<slug>)")
    args = ap.parse_args()

    order_path = Path(args.order).resolve()
    order = json.loads(order_path.read_text())
    c = order.get("couple", {})
    slug = order.get("slug") or slugify(c.get("partner1", ""), c.get("partner2", ""))
    out = Path(args.out).resolve() if args.out else ROOT / "sites" / slug
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    site = Site(order, slug, out, order_path.parent / "photos")
    warnings = site.build()

    print(f"Built {slug} → {out.relative_to(Path.cwd()) if out.is_relative_to(Path.cwd()) else out}")
    layout = "one-page scroll" if site.single else "multi-page"
    print(f"Layout: {layout}  ·  intro: {site.intro}  ·  scroll animations: {'on' if site.animate else 'off'}")
    print(f"Sections: {', '.join(site.pages)}  ·  photos: {len(site.gallery)}")
    if warnings:
        print("\nChecklist:")
        for w in warnings:
            print(f"  - {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
