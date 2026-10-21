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
| T2 | OLBG fixture harvest — Tennis, Darts, Snooker | done | arena-ebfbd966 | `data/matches.json` |
| T3 | OLBG fixture harvest — Basketball, Baseball, Ice Hockey | done | arena-ebfbd966 | `data/matches.json` |
| T4 | OLBG fixture harvest — Cricket, Rugby U/L, Volleyball, Handball, Gaelic Football | done | arena-ebfbd966 | `data/matches.json` |
| T5 | Line-origination model + confidence rules (documented, deterministic) | done | arena-ebfbd966 | `docs/methodology.html`, `scripts/originate.py` |
| T6 | Official-source verification (ATP/WTA, PDC, WST, NBA, NHL, MLB, ICC, World Rugby, etc.) | done (see caveats) | arena-ebfbd966 | `data/matches.json` |
| T7 | High-confidence write-ups (≥30 words, unique, verified facts only) | done | arena-ebfbd966 | `data/matches.json` |
| T8 | Site build — dashboard + per-sport subpages + Flagged for Review | done | arena-ebfbd966 | `docs/`, `scripts/build_site.py` |
| T9 | Validation — every row sourced, word counts, broken-link check | done | arena-ebfbd966 | `scripts/validate.py` |
| T10 | Integration — PR to main, merge, verify GitHub Pages deploy | in progress | arena-ebfbd966 | — |

All T2–T10 tasks are claimed by session `arena-ebfbd966` on branch `arena/ebfbd966-olbg1` (single active session; no overlapping scopes). Another session must not start a claimed task; log requests below instead.

## Change / handoff log
- 2026-10-21 — arena-ebfbd966 created this board; repo was empty except `README.md` (`# OLBG1`). No prior work to conflict with.

## Verification log
- 2026-10-21 (arena-ebfbd966) — Fixtures transcribed line by line from OLBG sport feeds (Tennis/3, Basketball/4, Cricket/7, Snooker/8, Rugby Union/9, Rugby League/10, Baseball/12, Ice Hockey/13, Darts/15, Handball/20, Volleyball/21, Gaelic Football/25). 133 matches. Tip counts cut off on 3 rows (TEN-14, RGU-15, VOL-15) left blank + flagged.
- Official cross-checks fetched: PDC draw article (pdc.tv 2026-10-18) — darts all 16 ties VERIFIED; WST Match Centre — snooker 3 VERIFIED, 2 CONTESTED (SNO-01/04), 1 OLBG-ONLY; MLB official WS schedule — BBA-01 VERIFIED (Rays 98-64 @ Brewers 103-59, 23 Oct); ICC NZ schedule — CRI-04 VERIFIED; ICC ODI ratings 19 Oct (AFG 92 #8, BAN 82 #9, via republished ICC table); URC official fixtures — RGU-04/07/11/14 VERIFIED; NBA official — 2026-27 start 20 Oct + Antetokounmpo Miami debut; ATP official calendar — 19-25 Oct events.
- Origination: scripts/originate.py (deterministic). Result: 4 HIGH (DAR-02 Zonneveld, DAR-13 Littler, SNO-02 Pang, CRI-01 Afghanistan), 29 MEDIUM, 100 LOW. Writeups 117-130 words each, uniqueness + no-template checks in validator.
- Validator (scripts/validate.py): PASSED — every row has OLBG + official links, HIGH rules enforced, probabilities sum to 1, contested/unverified forced LOW, excluded sports absent, no broken internal links across 18 pages, CSV matches JSON.

## Flagged irregularities
_(mirrored on the site's Flagged for Review page; do not block merge)_
1. SNO-01/SNO-04: OLBG snooker pairings not reconcilable with official WST Match Centre at harvest — CONTESTED, LOW.
2. DAR-12/DAR-14: OLBG crowd majority opposes official seeding gap (Reyes over #6 Aspinall; Schindler over #2 Nijman) — forced LOW.
3. HND-06/08/09/10: most-tipped selection is the Tie (base rate <10%) — winner pick falls back to home side, LOW.
4. TEN-14/RGU-15/VOL-15: tip counts cut off in page fetch — blank, UNVERIFIED.
5. Seed/rank provenance beyond PDC-stated seeds is from published draw summaries (PDC/WST linked per row); SNO-02 HIGH partly rests on secondary rank listing — re-confirm on WST.
6. No ATP/WTA per-player ranking gaps or domestic-league standings verified this pass — tennis capped below HIGH; several totals tagged MODEL-BASELINE.
7. MLB Game 1 starters + NHL goalies unconfirmed at harvest — blank.
8. OLBG 'Load More' tail (zero-tip fixtures) not enumerable; OLBG times carry no timezone in fetched text, reproduced as shown.
- 2026-10-21 — arena-ebfbd966: harvest complete (133 matches), origination engine + site built, validator passing. See Verification log.
