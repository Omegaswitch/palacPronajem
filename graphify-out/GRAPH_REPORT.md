# Graph Report - palacpronajem  (2026-11-13)

## Corpus Check
- 16 files · ~15,681 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 19 file(s) not represented in the graph (top: .woff2 16, (none) 1, .css 1)

## Summary
- 94 nodes · 174 edges · 13 communities (9 shown, 4 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c6477787`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- check.py
- photo
- vercel.json
- build.py
- layout
- render_home
- render_room
- serve
- velkoprevorskypalac.eu
- CLAUDE.md
- make_og.py

## God Nodes (most connected - your core abstractions)
1. `layout()` - 12 edges
2. `build()` - 11 edges
3. `url_of()` - 10 edges
4. `page()` - 10 edges
5. `render_home()` - 9 edges
6. `title_of()` - 8 edges
7. `render_room()` - 8 edges
8. `photo()` - 7 edges
9. `room_list()` - 7 edges
10. `capacity_table()` - 7 edges

## Surprising Connections (you probably didn't know these)
- `build()` --calls--> `url_of()`  [EXTRACTED]
  build.py → build.py  _Bridges community 4 → community 3_
- `capacity_table()` --calls--> `url_of()`  [EXTRACTED]
  build.py → build.py  _Bridges community 4 → community 6_
- `render_home()` --calls--> `url_of()`  [EXTRACTED]
  build.py → build.py  _Bridges community 4 → community 5_
- `gallery()` --calls--> `photo()`  [EXTRACTED]
  build.py → build.py  _Bridges community 1 → community 6_
- `render_home()` --calls--> `photo()`  [EXTRACTED]
  build.py → build.py  _Bridges community 1 → community 5_

## Import Cycles
- None detected.

## Communities (13 total, 4 thin omitted)

### Community 0 - "check.py"
Cohesion: 0.15
Nodes (5): plain(), main(), Page, redirect_sources(), resolves()

### Community 1 - "photo"
Cohesion: 0.33
Nodes (3): image_size(), photo(), render_downloads()

### Community 2 - "vercel.json"
Cohesion: 0.20
Nodes (9): buildCommand, cleanUrls, framework, headers, installCommand, outputDirectory, redirects, $schema (+1 more)

### Community 3 - "build.py"
Cohesion: 0.29
Nodes (4): build(), render_404(), render_history(), write()

### Community 4 - "layout"
Cohesion: 0.38
Nodes (9): crumbs_html(), lang_switch(), layout(), lockup(), nav_html(), page(), side_nav(), title_of() (+1 more)

### Community 5 - "render_home"
Cohesion: 0.47
Nodes (6): contact_card(), links(), mailto(), render_contact(), render_home(), tel()

### Community 6 - "render_room"
Cohesion: 0.31
Nodes (8): capacity_table(), cover(), fill(), gallery(), num(), render_room(), render_spaces(), room_list()

### Community 8 - "serve"
Cohesion: 0.67
Nodes (4): serve(), do_GET(), end_headers(), guess_type()

### Community 9 - "velkoprevorskypalac.eu"
Cohesion: 0.50
Nodes (3): Content, Hosting, velkoprevorskypalac.eu

## Knowledge Gaps
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `serve()` connect `serve` to `build.py`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._