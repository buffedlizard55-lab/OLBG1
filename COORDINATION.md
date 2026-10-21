# COORDINATION.md — Shared Task Board

This is the shared task board for all agent sessions working on this repo.
Read this before starting any work. Claim a task by writing your session ID
and file scope, then commit and push immediately.

## Rules

- One task per session at a time. Never start a task another session has claimed
  with a claim less than 60 minutes old and recent commits.
- Keep scopes non-overlapping. If a task requires changing a file owned by
  another session, log the request in the "Cross-session requests" section
  instead of editing it.
- Make small, frequent commits. Run `git pull --rebase` before every push.
- Never mark anything verified without checking it against an official source,
  and link that source in the task record.
- Shared outputs (site index, navigation, combined data) are changed only by the
  final integration session once all other tasks are done.
- If a session crashes or its claim is more than 60 minutes old with no commits,
  another session may take over the task and note the handoff in the log.

## Session registry

| Session ID | Branch | Notes |
|---|---|---|
| arena-aa4e9dbf | `arena/aa4e9dbf-olbg1` | Primary session (this one). Platform fixes this branch name for the session; all its tasks run sequentially on this branch. This session also acts as the final integration session. |

## Task board

Legend: unclaimed | in progress (owner) | done (owner) | needs review

| # | Task | Status | Owner | Files in scope |
|---|---|---|---|---|
| T1 | Reverse-engineer OLBG.com structure (sport taxonomy, URL patterns, market types, exclusion mapping) | in progress | arena-aa4e9dbf | `docs/methodology.html`, `data/olbg-structure.json` |
| T2 | Harvest current match/event list for all covered sports from OLBG | in progress | arena-aa4e9dbf | `data/raw/olbg-<sport>.json` |
| T3 | Verify every match against official sources (dates, teams, venues, context) | in progress | arena-aa4e9dbf | `data/matches.json`, `data/matches.csv` |
| T4 | Originate betting lines (money line / handicap / total) for every verified match | in progress | arena-aa4e9dbf | `data/lines.json` |
| T5 | Assign pick + confidence (low/medium/high) for every match | in progress | arena-aa4e9dbf | `data/picks.json` |
| T6 | Write 30+ word unique predictions for high-confidence picks, facts verified from official sources | in progress | arena-aa4e9dbf | `data/predictions.json` |
| T7 | Build per-sport data tables with source links; flag anything unverified | in progress | arena-aa4e9dbf | `data/sports/<sport>.json` |
| T8 | Build GitHub Pages site (landing page, sport subpages, dashboard UI, Flagged for Review page) | in progress | arena-aa4e9dbf | `docs/` |
| T9 | Final integration: line-by-line re-verification, link check, build check | in progress | arena-aa4e9dbf | all |
| T10 | PR to main, merge, confirm Pages deploy, record result | in progress | arena-aa4e9dbf | `COORDINATION.md` |

Note: this first session is executing all tasks itself in sequence (no other
sessions have registered). Each task's detailed record (sources, verification,
irregularities) is logged below as it completes.

## Covered sports (from OLBG sitemap, exclusions applied)

Exclusions requested: soccer, boxing, UFC, MMA, football, American football,
hurling, horse racing, cycling, specials.

| OLBG sport (sport id) | Coverage decision |
|---|---|
| Tennis (3) | COVERED |
| Golf (5) | COVERED |
| Rugby Union (9) | COVERED |
| Rugby League (10) | COVERED |
| Cricket (7) | COVERED |
| Basketball (4) | COVERED |
| Baseball (12) | COVERED |
| Darts (15) | COVERED |
| Snooker (8) | COVERED |
| Ice Hockey (13) | COVERED |
| Motor Racing (14) | COVERED (not on exclusion list) |
| Handball (20) | COVERED |
| Volleyball (21) | COVERED |
| eSports (23) | COVERED (not on exclusion list) |
| Greyhounds (28) | EXCLUDED by analogy to horse racing (animal racing, no "match" markets) — FLAGGED for review |
| Aussie Rules (22) | EXCLUDED (code of football) — FLAGGED for review |
| Gaelic Football (25) | EXCLUDED (code of football) — FLAGGED for review |
| Football (1) | EXCLUDED (soccer) |
| Horse Racing (2) | EXCLUDED |
| Boxing (16) / UFC / MMA | EXCLUDED |
| American Football (11) | EXCLUDED |
| Cycling (17) | EXCLUDED |
| Hurling | EXCLUDED (GAA code listed under Gaelic sports on OLBG) |
| Specials | EXCLUDED |

## Task records

### T1 — Reverse-engineer OLBG.com (owner: arena-aa4e9dbf) — DONE
- Sitemap index `https://www.olbg.com/sitemap.xml` → `sitemap-betting-tips.xml` lists all sport hubs with stable sport IDs (see table above).
- Event URL pattern: `https://www.olbg.com/betting-tips/{Sport}/{Region}/{Competition}/{Match}/{market_id}?event_id={id}`; hub pattern `/betting-tips/{Sport}/{sport_id}`.
- Per-sport market maps extracted from OLBG help text + a sample tennis event page (Win Match, Set Betting, 1st Set Winner, Games handicap, Total Games) → saved in `data/olbg-structure.json`.
- Irregularity found: OLBG displayed start times are unreliable across sports (wrong for NBA/NHL/F1/darts/snooker; correct for ICEHL/tennis). Documented on Flagged page with examples.

### T2 — Harvest match list (owner: arena-aa4e9dbf) — DONE
- All 14 covered-sport hub pages read 2026-10-21 ~05:00-08:00 UTC; 131 events recorded with OLBG event URLs (see `data/matches.json`, `tools/data_*.py`).
- Findings: eSports hub empty ("No tips found"); Rugby League has no match events (2027 futures only); Baseball lists only World Series G1.

### T3 — Verify matches against official sources (owner: arena-aa4e9dbf) — DONE
- 31 events verified directly on official sources (NBA.com, NHL.com, MLB.com, ATP/WTA, EHF/eurohandball.com, hapoelbc.com, EuroCup official calendar PDF, LNR (top14/prod2), kac.at, formula1.com, lpga.com, internationalseries.com, stifelcharityclassic.com, pgatourmedia, womensindianopen.com, cricket.com.au, nhl.com gamecenter, euroleaguebasketball.com standings).
- 78 partial (competition/date cross-checked via multiple listings; official league page linked).
- 22 unverified → fields left blank and flagged (KBL game, 4 CSA domestic T20s, 4 Scandinavian domestic handball, some volleyball/tennis/golf rows, Cluj–London Lions conflict).
- Key verified facts used for picks/predictions are embedded in `tools/data_*.py` with per-fact source URLs.

### T4 — Originate lines (owner: arena-aa4e9dbf) — DONE
- 113 of 131 events carry our own fair (vig-free) lines across money line / handicap / total (and outright boards for golf/F1). Unverified fixtures intentionally have blank lines. Methodology documented on the site's Methodology page (power ratings from verified standings/results/H2H/seedings + home advantage).

### T5 — Picks + confidence (owner: arena-aa4e9dbf) — DONE
- Every verified/partial event has a pick with low/medium/high label; unverified events have no pick (blank + flag). 9 high-confidence picks: MLB WS G1 Under 6.5; Panathinaikos ML; Veszprem ML; PSG Handball ML; Aalborg ML; van Veen ML; Higgins ML; Australia Women ML; Toulouse ML.

### T6 — High-confidence predictions (owner: arena-aa4e9dbf) — DONE
- 9 written predictions, 66-92 words each, each stating the betting selection explicitly, with per-fact source links (see `docs/predictions.html`).

### T7 — Data tables with source links (owner: arena-aa4e9dbf) — DONE
- `data/sports/*.json` (14 files) + `data/matches.json` generated from `tools/data_*.py`.

### T8 — GitHub Pages site (owner: arena-aa4e9dbf) — DONE
- `docs/`: landing dashboard, 14 sport subpages, predictions.html, flagged.html, methodology.html, assets/style.css. Pure static HTML/CSS (no build deps). Internal link check: 18 HTML files, 0 broken links; 187 distinct external URLs, all pattern-valid.

### T9 — Final integration & verification (owner: arena-aa4e9dbf) — DONE
- Line-by-line re-check of the generated tables against the captured sources; verification badges per row (verified/partial/unverified); blanks confirmed blank; review-flag classification implemented; site builds reproducibly via `python3 tools/build_site.py`.

### T10 — PR, merge, Pages deploy (owner: arena-aa4e9dbf) — see final status below

## Cross-session requests

- (none)

## Final integration report (arena-aa4e9dbf, acting as final integration session)

- Branch: `arena/aa4e9dbf-olbg1` (this session's fixed branch) → PR to `main`.
- Combined data re-verified; site built; internal links checked (0 broken); Pages served from `/docs` on `main`.
- PR link and deploy result recorded below when complete.

## Change log

- 2026-10-21: arena-aa4e9dbf created board, claimed T1–T10 (no other sessions registered).
- 2026-10-21: arena-aa4e9dbf completed T1–T9 (see task records for sources, verification and irregularities). T10 in progress.

