#!/usr/bin/env python3
"""Static site generator for velkoprevorskypalac.eu. Python 3.10+, standard library only.

    python3 build.py                 preview build into dist/ (noindex, content-status labels shown)
    python3 build.py --production    production build (indexable, no status labels)
    python3 build.py serve [port]    preview build, then serve dist/ with _headers and _redirects applied

Content: content/site.json (facts: contact, rooms, capacities, plans), content/<lang>.json (all text).
Photos: static/media/<room>-<nn>-{480,800,1600}.webp; a room's gallery is every file with its prefix.
"""
import html
import json
import re
import shutil
import struct
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT, STATIC, DIST = ROOT / "content", ROOT / "static", ROOT / "dist"
PRODUCTION = "--production" in sys.argv
SITE = json.loads((CONTENT / "site.json").read_text(encoding="utf-8"))
LANGS = SITE["languages"]
L = {l: json.loads((CONTENT / f"{l}.json").read_text(encoding="utf-8")) for l in LANGS}
ROOMS = [r["key"] for r in SITE["rooms"]]
ROOM = {r["key"]: r for r in SITE["rooms"]}
PLAN = {p["key"]: p for p in SITE["plans"]}
PHOTOS = {k: sorted(p.name[:-9] for p in (STATIC / "media").glob(f"{k}-[0-9][0-9]-800.webp")) for k in ROOMS}
ASSET_VERSION = datetime.now().strftime("%Y%m%d%H%M")
esc = lambda s: html.escape(str(s or ""), quote=True)


def url_of(key, lang):
    t = L[lang]
    return t["rooms"][key]["url"] if key in t["rooms"] else t["pages"][key]["url"]


def title_of(key, lang):
    t = L[lang]
    return t["rooms"][key]["title"] if key in t["rooms"] else t["pages"][key]["title"]


# ---------------------------------------------------------------- helpers


def image_size(rel_url):
    """Width/height of a local PNG or WebP (for layout-stable <img>)."""
    try:
        b = (STATIC / rel_url.lstrip("/")).read_bytes()[:64]
    except OSError:
        return None
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", b[16:24])
    if b[:4] == b"RIFF" and b[8:12] == b"WEBP":
        c = b[12:16]
        if c == b"VP8 ":
            w, h = struct.unpack("<HH", b[26:30])
            return w & 0x3FFF, h & 0x3FFF
        if c == b"VP8L":
            v = int.from_bytes(b[21:25], "little")
            return (v & 0x3FFF) + 1, ((v >> 14) & 0x3FFF) + 1
        if c == b"VP8X":
            return int.from_bytes(b[24:27], "little") + 1, int.from_bytes(b[27:30], "little") + 1
    return None


def photo(name, alt, sizes="100vw", eager=False, cls=""):
    """/media/<name>-800.webp plus the 480 and 1600 px versions."""
    src, small, big = (f"/media/{name}-{w}.webp" for w in (800, 480, 1600))
    srcset = f' srcset="{small} 480w, {src} 800w' + (f', {big} 1600w' if (STATIC / big.lstrip("/")).exists() else "") + f'" sizes="{esc(sizes)}"'
    w, h = image_size(src)
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return f'<img class="ph-img {cls}" src="{src}"{srcset} alt="{esc(alt)}" width="{w}" height="{h}" {load} decoding="async">'


def plain(html_text, n=180):
    t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", html_text))).strip()
    return t if len(t) <= n else t[: t.rfind(" ", 0, n)] + "…"


def fill(s, **kw):
    return re.sub(r"\{(\w+)\}", lambda m: str(kw.get(m.group(1), m.group(0))), s)


def num(x, lang):
    return f"{x:g}".replace(".", ",") if lang == "cs" else f"{x:g}"


def cover(key):
    return f"{key}-{ROOM[key]['cover']:02d}"


# ---------------------------------------------------------------- layout

FONTS_PRELOAD = ["asap-latin-400-normal", "eb-garamond-latin-500-normal"]
# inlined in every page (about 7 kB compressed): no render-blocking stylesheet request
CSS = re.sub(r"\s*([{}:;,>])\s*", r"\1", re.sub(r"/\*.*?\*/|\n\s*", "", (STATIC / "css" / "site.css").read_text(encoding="utf-8"), flags=re.S)).replace(";}", "}")


def lang_switch(lang, key):
    return "".join(f'<a href="{url_of(key, l)}" lang="{l}" hreflang="{l}"{" aria-current=" + chr(34) + "true" + chr(34) if l == lang else ""}'
                   f' title="{esc(L[l]["langName"])}">{l.upper()}</a>' for l in LANGS)


def nav_html(lang, key):
    t = L[lang]
    top = "prostory" if key in ROOMS else key
    lis = []
    for k in t["nav"]:
        cur = ' aria-current="page"' if k == key else (' class="is-active"' if k == top else "")
        sub = ""
        if k == "prostory":
            items = "".join(f'<li><a href="{url_of(r, lang)}">{esc(title_of(r, lang))}</a></li>' for r in ROOMS)
            sub = (f'<button class="sub-toggle" type="button" aria-expanded="false" aria-label="{esc(title_of(k, lang))}: {esc(t["ui"]["inSection"])}">'
                   f'<span aria-hidden="true"></span></button><ul class="sub">{items}</ul>')
        lis.append(f'<li class="{"has-sub" if sub else ""}"><a href="{url_of(k, lang)}"{cur}>{esc(title_of(k, lang))}</a>{sub}</li>')
    return f'<ul class="nav-list">{"".join(lis)}</ul>'


def lockup(lang):
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', (STATIC / "img" / "lockup" / f"{lang}.svg").read_text()).group(1).split()]
    return (f'<img class="lockup" src="/img/lockup/{lang}.svg" alt="{esc(L[lang]["ui"]["lockup"])}" width="{vb[2]:.0f}" height="{vb[3]:.0f}"'
            f' style="--h:{vb[3] / 126:.4f};--t:{vb[1] / 126:.4f}">')


def mailto(lang):
    return f'mailto:{SITE["contact"]["email"]}?subject={esc(L[lang]["ui"]["rentSubject"]).replace(" ", "%20")}'


def tel(n):
    return f'<a href="tel:{n.replace(" ", "")}">{esc(n)}</a>'


def layout(*, lang, key, title, body, description="", image="/media/palac-1600.webp", status=None):
    t, u, c = L[lang], L[lang]["ui"], SITE["contact"]
    url = url_of(key, lang) if key else "/404.html"
    full_title = title if key == "home" else f"{title} | {u['site']}"
    canonical = SITE["baseUrl"] + url
    robots = '<meta name="robots" content="noindex, nofollow">' if not PRODUCTION else ""
    alt_links = "".join(f'<link rel="alternate" hreflang="{l}" href="{SITE["baseUrl"]}{url_of(key, l)}">' for l in LANGS) + \
        f'<link rel="alternate" hreflang="x-default" href="{SITE["baseUrl"]}{url_of(key, "cs")}">' if key else ""
    hero = '<link rel="preload" as="image" href="/media/palac-800.webp" imagesrcset="/media/palac-480.webp 480w, /media/palac-800.webp 800w, /media/palac-1600.webp 1600w" imagesizes="100vw" fetchpriority="high">' if key == "home" else ""
    lockups = "".join(f'<link rel="prefetch" href="/img/lockup/{l}.svg" as="image">' for l in LANGS if l != lang)
    preload = hero + lockups + "".join(f'<link rel="preload" href="/fonts/{f}.woff2" as="font" type="font/woff2" crossorigin>' for f in FONTS_PRELOAD) + \
        '<link rel="preload" href="/img/banner/banner-photo.webp" as="image" fetchpriority="high">'
    ld = ""
    if key == "home":  # what the place is, for search engines (data only, not executed)
        ld = '<script type="application/ld+json">' + json.dumps({
            "@context": "https://schema.org", "@type": "EventVenue", "name": u["site"], "url": canonical, "image": SITE["baseUrl"] + image,
            "email": c["email"], "telephone": c["phone"],
            "address": {"@type": "PostalAddress", "streetAddress": "Velkopřevorské náměstí 4", "postalCode": "118 00", "addressLocality": "Praha 1", "addressCountry": "CZ"},
        }, ensure_ascii=False).replace("</", "<\\/") + "</script>"
    status_bar = f'<p class="content-status content-status--{esc(status)}"><span>{esc(u["status"].get(status, status))}</span></p>' if status and not PRODUCTION else ""
    footer_nav = "".join(f'<li><a href="{url_of(k, lang)}">{esc(title_of(k, lang))}</a></li>' for k in t["nav"][1:] + ROOMS)
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(plain(description or body, 160))}">
{robots}
{f'<link rel="canonical" href="{canonical}">' if key else ''}
{alt_links}
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(u['site'])}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(plain(description or body, 160))}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE['baseUrl']}{image}">
<meta property="og:locale" content="{t['locale']}">
<meta name="twitter:card" content="summary_large_image">
{ld}
<meta name="theme-color" content="#e31a18">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/img/favicon/favicon-32x32.png">
<link rel="apple-touch-icon" href="/img/favicon/apple-touch-icon-180x180.png">
{preload}
<style>{CSS}</style>
<script src="/js/head.js?v={ASSET_VERSION}"></script>
<script src="/js/site.js?v={ASSET_VERSION}" defer></script>
</head>
<body>
<a class="skip" href="#main">{esc(u['skip'])}</a>
<header class="site-header">
 <div class="topbar"><div class="wrap">
  <a class="topbar-home" href="{url_of('home', lang)}">{esc(u['orderShort'])} · {esc(u['entity'])}</a>
  <nav class="lang" aria-label="{esc(u['langLabel'])}">{lang_switch(lang, key or 'home')}</nav>
 </div></div>
 <div class="banner"><div class="wrap">
  <a class="banner-home" href="{url_of('home', lang)}">{lockup(lang)}</a>
  <p class="fullname">{esc(u['siteFull'])}<span>{esc(u['siteFullSub'])}</span></p>
 </div></div>
 <nav class="mainnav" aria-label="{esc(u['menu'])}"><div class="wrap">
  <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="menu">{esc(u['menu'])}</button>
  <div id="menu" class="menu">{nav_html(lang, key)}</div>
 </div></nav>
</header>
<main id="main" tabindex="-1">
{status_bar}
{body}
</main>
<footer class="site-footer">
 <div class="f-nav"><div class="wrap"><ul>{footer_nav}</ul></div></div>
 <div class="f-id"><div class="wrap">
  <p class="f-name">{esc(u['siteFull'])}</p>
  <p>{esc(u['contactOrg'])}</p>
  <p>{esc(' '.join(u['contactAddress']))} · <a href="mailto:{c['email']}">{c['email']}</a> · {tel(c['phone'])}</p>
 </div></div>
 <div class="f-red"><div class="wrap">
  <p>{esc(u['maltezskyrad'])}: <a href="https://www.maltezskyrad.cz/">www.maltezskyrad.cz</a></p>
  <p>{esc(u['orderofmalta'])}: <a href="https://www.orderofmalta.int/">www.orderofmalta.int</a></p>
  <p>{esc(u['mobile'])}: {tel(c['mobile'])}</p>
 </div></div>
</footer>
</body>
</html>
"""


def crumbs_html(key, lang):
    u = L[lang]["ui"]
    trail = [("home", u["home"])] + ([("prostory", title_of("prostory", lang))] if key in ROOMS else []) + [(key, title_of(key, lang))]
    items = "".join(f'<li><span aria-current="page">{esc(x)}</span></li>' if k == key else f'<li><a href="{url_of(k, lang)}">{esc(x)}</a></li>' for k, x in trail)
    return f'<nav class="crumbs" aria-label="{esc(u["breadcrumb"])}"><ol>{items}</ol></nav>'


def side_nav(key, lang):
    if key not in ROOMS:
        return ""
    items = "".join(f'<li><a href="{url_of(k, lang)}"{" aria-current=" + chr(34) + "page" + chr(34) if k == key else ""}>{esc(title_of(k, lang))}</a></li>' for k in ROOMS)
    return (f'<div class="page-side"><nav class="side-nav" aria-label="{esc(L[lang]["ui"]["inSection"])}"><p class="label">'
            f'<a href="{url_of("prostory", lang)}">{esc(title_of("prostory", lang))}</a></p><ul>{items}</ul></nav></div>')


def page(key, lang, inner, lead="", image=None):
    side = side_nav(key, lang)
    body = f"""
<div class="wrap">{crumbs_html(key, lang)}</div>
<article class="wrap page{' page--with-side' if side else ''}">
 <header class="page-head"><h1 class="display">{esc(title_of(key, lang))}</h1>{f'<p class="lead-s">{esc(lead)}</p>' if lead else ''}</header>
 <div class="page-main">{inner}</div>
 {side}
</article>"""
    desc = L[lang]["rooms"][key]["lead"] if key in ROOMS else L[lang]["pages"][key].get("description", "")
    return layout(lang=lang, key=key, title=title_of(key, lang), body=body, description=desc, status="new" if lang == "cs" else "translation",
                  **({"image": image} if image else {}))


# ---------------------------------------------------------------- blocks


def room_list(lang, heading="h3"):
    """Rooms as hairline rows: photo, name, other name, floor, number of photographs."""
    u = L[lang]["ui"]
    rows = []
    for k in ROOMS:
        r, meta = L[lang]["rooms"][k], []
        if r["aka"]:
            meta.append(f'{u["aka"]} {r["aka"]}')
        if ROOM[k].get("floor"):
            meta.append(u["floors"][ROOM[k]["floor"]])
        meta.append(fill(u["photos"], n=len(PHOTOS[k])))
        rows.append(f'<li><a href="{r["url"]}"><span class="r-photo">{photo(cover(k), "", sizes="(min-width: 641px) 220px, 100vw")}</span>'
                    f'<span class="r-text"><{heading} class="r-title">{esc(r["title"])}</{heading}><span class="r-meta">{esc(" · ".join(meta))}</span></span></a></li>')
    return f'<ul class="rooms">{"".join(rows)}</ul>'


def capacity_table(lang, only=None):
    u, keys = L[lang]["ui"], [only] if only else SITE["capacityOrder"]
    cols = ["reception", "theatre", "classroom", "banquet"]
    head = "".join(f'<th scope="col">{esc(u[c])}</th>' for c in cols) + f'<th scope="col">{esc(u["size"])} (m)</th><th scope="col">{esc(u["area"])} (m²)</th>'
    rows = ""
    for k in keys:
        c = SITE["capacity"][k]
        cells = "".join(f'<td>{c[x] if c[x] else "–"}</td>' for x in cols)
        size = " × ".join(num(x, lang) for x in c["size"])
        name = esc(title_of(k, lang)) if only else f'<a href="{url_of(k, lang)}">{esc(title_of(k, lang))}</a>'
        rows += f'<tr><th scope="row">{name}</th>{cells}<td>{size}</td><td>{c["area"]}</td></tr>'
    return (f'<div class="table-wrap" tabindex="0" role="region" aria-label="{esc(u["capacityTitle"])}"><table class="capacity">'
            f'<thead><tr><th scope="col">{esc(u["room"])}</th>{head}</tr></thead><tbody>{rows}</tbody></table></div>'
            f'<p class="small">{esc(u["capacityNote"])}</p>')


def contact_card(lang):
    u, c = L[lang]["ui"], SITE["contact"]
    return f"""<dl class="contact-card">
 <div><dt>{esc(u['person'])}</dt><dd>{esc(u['contactPerson'])}</dd></div>
 <div><dt>{esc(u['email'])}</dt><dd><a href="{mailto(lang)}">{c['email']}</a></dd></div>
 <div><dt>{esc(u['mobile'])}</dt><dd>{tel(c['mobile'])}</dd></div>
 <div><dt>{esc(u['phone'])}</dt><dd>{tel(c['phone'])}</dd></div>
 <div><dt>{esc(u['post'])}</dt><dd>{esc(u['contactOrg'])}<br>{'<br>'.join(esc(x) for x in u['contactAddress'])}</dd></div>
</dl>"""


def links(lang):
    u = L[lang]["ui"]
    return (f'<ul class="plain-links"><li><a href="{u["historyUrl"]}">{esc(u["historyLink"])}</a></li>'
            f'<li><a href="https://www.maltezskyrad.cz/">{esc(u["maltezskyrad"])} – www.maltezskyrad.cz</a></li>'
            f'<li><a href="https://www.orderofmalta.int/">{esc(u["orderofmalta"])} – www.orderofmalta.int</a></li></ul>')


def gallery(key, lang):
    u, n, title = L[lang]["ui"], len(PHOTOS[key]), title_of(key, lang)
    items = "".join(f'<li><a class="g-photo" href="/media/{p}-1600.webp" data-i="{i}" aria-label="{esc(u["openPhoto"])}: {esc(fill(u["photoAlt"], room=title, i=i, n=n))}">'
                    f'{photo(p, fill(u["photoAlt"], room=title, i=i, n=n), sizes="(min-width: 961px) 280px, (min-width: 641px) 33vw, 50vw")}</a></li>'
                    for i, p in enumerate(PHOTOS[key], 1))
    return (f'<ul class="room-gallery" data-close="{esc(u["close"])}" data-prev="{esc(u["prev"])}" data-next="{esc(u["next"])}">{items}</ul>')


# ---------------------------------------------------------------- pages


def render_home(lang):
    t, u, c = L[lang], L[lang]["ui"], SITE["contact"]
    body = f"""
<section class="hero" aria-labelledby="home-title">
 <div class="hero-media">{photo('palac', '', sizes='100vw', eager=True)}</div>
 <div class="wrap hero-grid">
  <div class="hero-text">
   <p class="kicker">{esc(u['kicker'])}</p>
   <h1 id="home-title" class="display">{esc(u['site'])}</h1>
   <p class="lead">{esc(u['heroLead'])}</p>
  </div>
  <div class="next">
   <h2 class="display-s">{esc(u['rentTitle'])}</h2>
   <p class="next-reg">{esc(u['rentText'])}</p>
   <p class="next-links"><a class="btn" href="{mailto(lang)}">{esc(u['rentButton'])}</a> <a class="link-strong" href="{url_of('prostory', lang)}">{esc(u['spaces'])}</a></p>
  </div>
 </div>
</section>

<section class="band" aria-labelledby="about-title"><div class="wrap split">
 <div class="split-head"><h2 id="about-title" class="display-m">{esc(u['aboutTitle'])}</h2><p>{esc(u['aboutText'])}</p>
  <p><a class="link-strong" href="{u['historyUrl']}">{esc(u['historyLink'])}</a></p></div>
 <dl class="contact-card facts">
  <div><dt>{esc(u['factsEvents'])}</dt><dd>{esc(u['factsEventsValue'])}</dd></div>
  <div><dt>{esc(u['factsPrices'])}</dt><dd>{esc(u['factsPricesValue'])}</dd></div>
  <div><dt>{esc(u['factsCatering'])}</dt><dd>{esc(u['factsCateringValue'])}</dd></div>
  <div><dt>{esc(u['factsAddress'])}</dt><dd>{'<br>'.join(esc(x) for x in u['contactAddress'])}</dd></div>
 </dl>
</div></section>

<section class="band band-grey" aria-labelledby="spaces-title"><div class="wrap split">
 <div class="split-head"><h2 id="spaces-title" class="display-m">{esc(u['spacesTitle'])}</h2><p>{esc(u['spacesText'])}</p></div>
 {room_list(lang)}
</div></section>

<section class="band" aria-labelledby="capacity-title"><div class="wrap split">
 <div class="split-head"><h2 id="capacity-title" class="display-m">{esc(u['capacityTitle'])}</h2>
  <p><a class="link-strong" href="{url_of('ke-stazeni', lang)}">{esc(u['plansTitle'])}</a></p></div>
 <div>{capacity_table(lang)}</div>
</div></section>

<section class="band band-grey" aria-labelledby="contact-title"><div class="wrap split">
 <div class="split-head"><h2 id="contact-title" class="display-m">{esc(u['contactTitle'])}</h2>
  <p><a class="btn" href="{mailto(lang)}">{esc(u['rentButton'])}</a></p></div>
 <div>{contact_card(lang)}</div>
</div></section>
"""
    return layout(lang=lang, key="home", title=t["pages"]["home"]["title"], body=body, description=t["pages"]["home"]["description"],
                  status="new" if lang == "cs" else "translation")


def render_spaces(lang):
    u, p = L[lang]["ui"], L[lang]["pages"]["prostory"]
    inner = (f'{room_list(lang, "h2")}<section aria-labelledby="cap"><h2 id="cap" class="display-s">{esc(u["capacityTitle"])}</h2>{capacity_table(lang)}</section>'
             f'<p><a class="link-strong" href="{url_of("ke-stazeni", lang)}">{esc(u["plansTitle"])}</a></p>')
    return page("prostory", lang, inner, lead=p["lead"])


def render_room(key, lang):
    u, r = L[lang]["ui"], L[lang]["rooms"][key]
    facts = []
    if r["aka"]:
        facts.append((u["aka"], esc(r["aka"])))
    if ROOM[key].get("floor"):
        facts.append((u["floor"], esc(u["floors"][ROOM[key]["floor"]])))
    if key in SITE["capacity"]:
        c = SITE["capacity"][key]
        facts.append((u["size"], f'{" × ".join(num(x, lang) for x in c["size"])} m · {c["area"]} m²'))
    if ROOM[key].get("plan"):
        pl = PLAN[ROOM[key]["plan"]]
        facts.append((u["planLink"], f'<a href="{pl["file"]}">{esc(L[lang]["plans"][pl["key"]])}</a> <span class="file-meta">PDF</span>'))
    dl = "<dl class=\"contact-card\">" + "".join(f"<div><dt>{esc(a)}</dt><dd>{b}</dd></div>" for a, b in facts) + "</dl>" if facts else ""
    cap = capacity_table(lang, key) if key in SITE["capacity"] else ""
    inner = f'{dl}{cap}{gallery(key, lang)}<p><a class="btn" href="{mailto(lang)}">{esc(u["rentButton"])}</a></p>'
    return page(key, lang, inner, lead=r["lead"], image=f"/media/{cover(key)}-1600.webp")


def render_downloads(lang):
    t, u = L[lang], L[lang]["ui"]
    items = "".join(f"""<li>
 <a class="plan-figure" href="/media/{p['image']}-1600.webp">{photo(p['image'], t['plans'][p['key']], sizes='(min-width: 961px) 240px, 40vw')}</a>
 <div><h2 class="r-title">{esc(t['plans'][p['key']])}</h2>
 <p><a class="btn btn--ghost" href="{p['file']}" download>{esc(u['download'])} <span class="file-meta">PDF</span></a></p></div>
</li>""" for p in SITE["plans"])
    return page("ke-stazeni", lang, f'<ol class="plans">{items}</ol>', lead=t["pages"]["ke-stazeni"]["lead"])


def render_contact(lang):
    u = L[lang]["ui"]
    inner = f'{contact_card(lang)}<p><a class="btn" href="{mailto(lang)}">{esc(u["rentButton"])}</a></p><h2 class="display-s">{esc(u["linksTitle"])}</h2>{links(lang)}'
    return page("kontakt", lang, inner)


def render_404():
    u = L["cs"]["ui"]
    body = f'<div class="wrap page page--simple"><header class="page-head"><h1 class="display">{esc(u["notFound"])}</h1></header><div class="prose"><p>{esc(u["notFoundText"])}</p><p><a class="link-strong" href="/">{esc(u["home"])}</a></p></div></div>'
    return layout(lang="cs", key=None, title=u["notFound"], body=body, description=u["notFoundText"])


# ---------------------------------------------------------------- output


def write(url, html_text):
    path = DIST / url.lstrip("/") / "index.html" if url.endswith("/") else DIST / url.lstrip("/")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html_text, encoding="utf-8")


VERCEL = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))  # headers and redirects live here; other hosts get _headers and _redirects
HEADERS = "".join(h["source"].replace("(.*)", "*") + "\n" + "".join(f"  {x['key']}: {x['value']}\n" for x in h["headers"]) for h in VERCEL["headers"])
# old WordPress addresses are query strings (/?page_id=506); _redirects writes them in the Netlify form "/ page_id=506 /dest/"
REDIRECTS = [(r["source"].replace("(.*)", "*"), "".join(f" {h['key']}={h['value']}" for h in r.get("has", [])), r["destination"].replace("$1", ":splat"))
             for r in VERCEL.get("redirects", [])]


def build():
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(STATIC, DIST)
    urls = []
    for lang in LANGS:
        pages = {"home": render_home(lang), "prostory": render_spaces(lang), "ke-stazeni": render_downloads(lang), "kontakt": render_contact(lang)}
        pages |= {k: render_room(k, lang) for k in ROOMS}
        for k, h in pages.items():
            urls.append(url_of(k, lang))
            write(url_of(k, lang), h)
    write("/404.html", render_404())
    (DIST / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' +
                                      "".join(f"<url><loc>{SITE['baseUrl']}{u}</loc></url>" for u in urls) + "</urlset>", encoding="utf-8")
    (DIST / "robots.txt").write_text(("User-agent: *\nAllow: /\n\nSitemap: " + SITE["baseUrl"] + "/sitemap.xml\n") if PRODUCTION
                                     else "User-agent: *\nDisallow: /\n", encoding="utf-8")
    (DIST / "_headers").write_text(HEADERS + ("" if PRODUCTION else "/*\n  X-Robots-Tag: noindex, nofollow\n"), encoding="utf-8")
    (DIST / "_redirects").write_text("".join(f"{a}{q} {b} 301\n" for a, q, b in REDIRECTS), encoding="utf-8")
    print(f"built {len(urls)} pages in {', '.join(LANGS)}, {'production' if PRODUCTION else 'preview'} → {DIST}")


# ---------------------------------------------------------------- local preview server


def serve(port=8000):
    import functools
    import http.server
    from urllib.parse import parse_qsl, unquote
    rules = []  # (path, {query}, destination)
    for line in (DIST / "_redirects").read_text().splitlines():
        parts = line.split()
        if parts:
            rules.append((parts[0], dict(p.split("=", 1) for p in parts[1:-2]), parts[-2]))
    headers, types, block = {}, {}, None  # site-wide headers; exact-path Content-Type overrides
    for line in (DIST / "_headers").read_text().splitlines():
        if line and not line.startswith(" "):
            block = line.strip()
        elif line.strip():
            k, v = line.strip().split(":", 1)
            if block == "/*":
                headers[k] = v.strip()
            elif k == "Content-Type":
                types[block] = v.strip()

    class H(http.server.SimpleHTTPRequestHandler):
        def guess_type(self, path):
            return types.get(self.path.split("?")[0]) or super().guess_type(path)

        def end_headers(self):
            for k, v in headers.items():
                if k == "Strict-Transport-Security":
                    continue  # local server is plain HTTP
                self.send_header(k, v.replace("; upgrade-insecure-requests", ""))
            super().end_headers()

        def do_GET(self):
            path, _, qs = self.path.partition("?")
            query = dict(parse_qsl(qs))
            for src, need, dst in rules:
                if need and any(query.get(k) != v for k, v in need.items()):
                    continue
                if src.endswith("*") and path.startswith(src[:-1]):
                    dst = dst.replace(":splat", path[len(src) - 1:])
                elif src != path:
                    continue
                self.send_response(301)
                self.send_header("Location", dst)
                self.end_headers()
                return
            fs_path = unquote(path).lstrip("/")
            if not (DIST / fs_path).exists() and not (DIST / fs_path / "index.html").exists():
                self.send_response(404)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write((DIST / "404.html").read_bytes())
                return
            super().do_GET()

        do_HEAD = do_GET

    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(H, directory=str(DIST)))
    print(f"serving http://127.0.0.1:{port}/")
    httpd.serve_forever()


if __name__ == "__main__":
    build()
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        serve(int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 8000)
