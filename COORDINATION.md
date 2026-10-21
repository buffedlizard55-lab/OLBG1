# COORDINATION — OLBG Reverse-Engineering Project

Shared task board for all agent sessions. Read before starting. Claim before working. Small, frequent commits; `git pull --rebase` before every push.

> **Branch note (Arena platform rule):** This session is bound to branch `arena/ebfbd966-olbg1` and must not create/switch branches. That Arena rule takes precedence over the generic `session-<id>/<task>` branch naming in the brief. The final PR will be `arena/ebfbd966-olbg1` → `main`.

## Session registry
| Session ID | Branch | Status |
|---|---|---|
| arena-ebfbd966 | `arena/ebfbd966-olbg1` | active — 2026-10-21 |

## Scope (from brief)
- **Included sports (originate lines + pick + confidence):** Tennis, Basketball, Baseball, Cricket, Darts, Snooker, Ice Hockey, Rugby Union, Rugby League, Volleyball, Handball, Gaelic Football. Golf / Greyhounds / Motor Racing are covered by OLBG but are tournament/race outrights with no head-to-head match, handicap or match-total market — documented and flagged, no invented match lines.
- **Excluded (do NOT cover):** Soccer/Football, Boxing, UFC/MMA, American Football, Hurling, Horse Racing, Cycling, Specials.
- **Snapshot date:** 2026-10-21. Fixtures are the live upcoming OLBG events fetched on this date. Every row links its OLBG event page plus an official league/governing-body source. Unconfirmable values stay blank and are flagged `UNVERIFIED`.

## Task board
| # | Task | Status | Owner | Files |
|---|---|---|---|---|
| T1 | Coordination board + repo review | done | arena-ebfbd966 | `COORDINATION.md` |
| T2 | OLBG fixture harvest — Tennis, Darts, Snooker | in progress | arena-ebfbd966 | `data/matches.json` |
| T3 | OLBG fixture harvest — Basketball, Baseball, Ice Hockey | in progress | arena-ebfbd966 | `data/matches.json` |
| T4 | OLBG fixture harvest — Cricket, Rugby U/L, Volleyball, Handball, Gaelic Football | in progress | arena-ebfbd966 | `data/matches.json` |
| T5 | Line-origination model + confidence rules (documented, deterministic) | in progress | arena-ebfbd966 | `docs/methodology.html`, `scripts/originate.py` |
| T6 | Official-source verification (ATP/WTA, PDC, WST, NBA, NHL, MLB, ICC, World Rugby, etc.) | in progress | arena-ebfbd966 | `data/matches.json` |
| T7 | High-confidence write-ups (≥30 words, unique, verified facts only) | unclaimed | — | `data/matches.json` |
| T8 | Site build — dashboard + per-sport subpages + Flagged for Review | unclaimed | — | `docs/`, `scripts/build_site.py` |
| T9 | Validation — every row sourced, word counts, broken-link check | unclaimed | — | `scripts/validate.py` |
| T10 | Integration — PR to main, merge, verify GitHub Pages deploy | unclaimed | — | — |

All T2–T10 tasks are claimed by session `arena-ebfbd966` on branch `arena/ebfbd966-olbg1` (single active session; no overlapping scopes). Another session must not start a claimed task; log requests below instead.

## Change / handoff log
- 2026-10-21 — arena-ebfbd966 created this board; repo was empty except `README.md` (`# OLBG1`). No prior work to conflict with.

## Verification log
_(filled in per task as work completes — sources, checks performed, irregularities)_

## Flagged irregularities
_(mirrored on the site's Flagged for Review page; do not block merge)_
