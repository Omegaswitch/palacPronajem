# Graph Report - palacpronajem  (2026-10-19)

## Corpus Check
- 15 files · ~1,343,439 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 19 file(s) not represented in the graph (top: .woff2 16, (none) 1, .css 1)

## Summary
- 83 nodes · 158 edges · 13 communities (10 shown, 3 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e48790f9`
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
- page
- serve
- velkoprevorskypalac.eu
- CLAUDE.md

## God Nodes (most connected - your core abstractions)
1. `layout()` - 12 edges
2. `url_of()` - 10 edges
3. `build()` - 10 edges
4. `page()` - 9 edges
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
- `crumbs_html()` --calls--> `url_of()`  [EXTRACTED]
  build.py → build.py  _Bridges community 4 → community 7_
- `render_home()` --calls--> `url_of()`  [EXTRACTED]
  build.py → build.py  _Bridges community 4 → community 5_
- `capacity_table()` --calls--> `title_of()`  [EXTRACTED]
  build.py → build.py  _Bridges community 7 → community 6_

## Import Cycles
- None detected.

## Communities (13 total, 3 thin omitted)

### Community 0 - "check.py"
Cohesion: 0.14
Nodes (5): plain(), main(), Page, redirect_sources(), resolves()

### Community 1 - "photo"
Cohesion: 0.22
Nodes (6): cover(), fill(), gallery(), image_size(), photo(), room_list()

### Community 2 - "vercel.json"
Cohesion: 0.20
Nodes (9): buildCommand, cleanUrls, framework, headers, installCommand, outputDirectory, redirects, $schema (+1 more)

### Community 3 - "build.py"
Cohesion: 0.39
Nodes (4): build(), render_404(), render_downloads(), write()

### Community 4 - "layout"
Cohesion: 0.38
Nodes (6): lang_switch(), layout(), lockup(), nav_html(), tel(), url_of()

### Community 5 - "render_home"
Cohesion: 0.60
Nodes (5): contact_card(), links(), mailto(), render_contact(), render_home()

### Community 6 - "render_room"
Cohesion: 0.67
Nodes (4): capacity_table(), num(), render_room(), render_spaces()

### Community 7 - "page"
Cohesion: 0.83
Nodes (4): crumbs_html(), page(), side_nav(), title_of()

### Community 8 - "serve"
Cohesion: 0.67
Nodes (4): serve(), do_GET(), end_headers(), guess_type()

### Community 9 - "velkoprevorskypalac.eu"
Cohesion: 0.50
Nodes (3): Content, Hosting, velkoprevorskypalac.eu

## Knowledge Gaps
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `serve()` connect `serve` to `build.py`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Should `check.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14035087719298245 - nodes in this community are weakly interconnected._