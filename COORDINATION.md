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

### T1 — Reverse-engineer OLBG.com (owner: arena-aa4e9dbf)
- Status: in progress
- Findings so far:
  - Sitemap index: https://www.olbg.com/sitemap.xml → sub-sitemaps incl. `sitemap-betting-tips.xml`
  - URL pattern for events: `https://www.olbg.com/betting-tips/{Sport}/{Region}/{Competition}/{Match}/{market_id}?event_id={event_id}`
  - Sport hub pages: `https://www.olbg.com/betting-tips/{Sport}/{sport_id}`
  - 20+ sports listed (see table above).
- (record updated as work proceeds)

## Cross-session requests

- (none)

## Change log

- 2026-10-21: arena-aa4e9dbf created board, claimed T1–T10 (no other sessions registered).
