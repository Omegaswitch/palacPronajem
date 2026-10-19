# velkoprevorskypalac.eu

Rental of the rooms and garden of the Grand Priory Palace (Velkopřevorský palác) in Prague's Lesser Town, the seat of the Czech Grand Priory of the Order of Malta.
The site is in Czech, English, French, Italian and German.
It is built with the same engine and Grand Magistry frame as maltezskyrad.cz and lurdy.eu: a static generator in plain Python (standard library only), hosted on Vercel.

```
python3 build.py              # preview build → dist/ (noindex, content-status labels)
python3 build.py serve 8000   # preview on http://127.0.0.1:8000 (headers and redirects applied)
python3 build.py --production # production build
python3 check.py              # checks the build: links, one <h1> per page, titles, descriptions, brand files
```

## Content

| File | What |
|---|---|
| `content/site.json` | Facts: contact, rooms (cover photo, floor, plan), capacity table, floor-plan files |
| `content/cs.json` | All Czech text: pages, rooms, plan titles, interface |
| `content/en.json` … `de.json` | The same keys, translated (labelled "translation – awaiting review" in preview builds) |
| `static/media/` | Photos, WebP at 480, 800 and 1600 px. A room's gallery is every `<room>-NN-800.webp`; add or remove files to change it. |
| `static/files/` | Floor plans and garden layout (PDF) |

**Sources.** Text, photographs, plans and the capacity table come from the previous WordPress site (velkoprevorskypalac.eu, October 2026). The short room descriptions are new (from the photographs and plans; the staircase line follows maltezskyrad.cz) and await approval.

## Hosting

`vercel.json` holds the build command, the security headers (CSP, HSTS and others), cache rules, and redirects from the old WordPress addresses, including the query-string ones (`/?page_id=506`, `/?rl_gallery=repre-2`). `build.py` also writes `_headers` and `_redirects` for other hosts.
