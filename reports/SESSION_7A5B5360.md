# Session `7a5b5360-olbg1` — T41 fresh matchday desk, 22–26 October 2026

**Run:** 2026-10-22, 00:00Z–02:00Z. Branch `arena/7a5b5360-olbg1`.
**Published at:** https://buffedlizard55-lab.github.io/OLBG1/7a5b5360/

This session added a new desk rather than editing another session's data. Nothing in
`data/fixtures.json`, `data/lines.json`, `data/predictions.json`, `datasets/**`, `docs/**`,
`c17a9192/**`, `984d417f/**` or any other desk's page tree was modified. The only shared files
touched are three additive lines: one nav link in `index.html`, one README section, and this
append-only coordination entry.

---

## 1. What was harvested, and from where

Every URL below was fetched during this session. The full register, including failures, is in
`data/7a5b5360/sources.json` and on `7a5b5360/sources.html`.

| Sport | Official page | What it gave |
|---|---|---|
| Baseball | `statsapi.mlb.com/api/v1/schedule` (21–27 Oct, field-filtered) | 4 World Series games: gamePk, gameDate, venue, participants |
| Baseball | `statsapi.mlb.com/api/v1/standings` (NL and AL) | Milwaukee 103-59 (.636), Tampa Bay 98-64 (.605) |
| Ice Hockey | `api-web.nhle.com/v1/scoreboard/2026-10-24` | All 12 games on the 22–23 Oct slate with both clubs' W-L-OTL records, start times and venues |
| Rugby Union | `unitedrugby.com/latest/news/2026-27-fixtures-in-full/` | Round 4: 8 fixtures, venues, published local kick-offs |
| Snooker | `wst.tv/matches` | Round 3 board (8 matches) plus every completed Round 1/Round 2 score |
| Snooker | `wst.tv/rankings/…?showLive=false` | World ranking positions 1–36 with prize money |
| Motor Racing | `formula1.com/en/racing/2026` and `/2026/united-states` | Round 18, United States GP, 23–25 Oct, session times, 56 laps, 5.513 km |
| Motor Racing | `formula1.com/en/results/2026/drivers` | All 23 drivers and their championship points after Round 17 |
| Gaelic Football | `gaa.ie/fixtures-results` | Read: no senior football fixture in the window (one hurling match, excluded) |

Attempted and blocked, recorded rather than silently skipped: `pdc.tv` (consent wall),
`ehfcl.com` (404), `unitedrugby.com/urc/table` and `/standings` (404), `icc-cricket.com`
(client-rendered), `euroleaguebasketball.net` (client-rendered), `afl.com.au/aflw/fixture`
(client-rendered), `cdn.nba.com` (HTTP 500), `gbgb.org.uk` (HTTP 500).

## 2. What was produced

| Output | Count |
|---|---|
| Verified fixtures | 32 (baseball 3, ice hockey 12, rugby union 8, snooker 8, motor racing 1) |
| Originated selections | 231 |
| Match-winner picks | 32 — 4 High, 14 Medium, 14 Low |
| Written predictions | 18, all ≥30 words, zero shared 6-word phrases |
| Selections at 70% or better | 26 (16 of them price shorter than -250) |
| Flags published | 14 |
| Repository findings | 6 |
| Pages built | 14 |

## 3. The one finding about the brief

`F-7A-01`. The brief asks for picks that are simultaneously **70%+** and priced between **-250 and
+10000**. Those cannot both hold. A 70% chance is a 1.4286 fair price, which is about -233; add any
bookmaker margin and it quotes near 1.37, about -270. So a genuinely 70% selection is already
shorter than the -250 floor.

This desk does not drop either rule. Every selection on the site carries its model probability, its
fair decimal price, its book-equivalent price and an **in-band yes/no**. On this board 26 selections
clear 70% and 16 of them sit outside the brief's range; the 10 that are inside are listed on the
Markets page and in `data/7a5b5360/high_probability.json`.

## 4. Verification actually performed

* Every fixture row names the official page its facts came from, and the desk validator refuses to
  build if a row has no `https://` source.
* Values the official page did not publish are blank, not inferred: 8 snooker `start_utc` fields
  (timezone-less clock), 1 venue (`TBC, Dublin`), 10 snooker world rankings (the table served only
  positions 1–36).
* Rugby union carries **no handicap and no total** because no official table was readable; a line
  would have been invented. Those eight matches are priced from a neutral baseline and capped at Low.
* No starting pitcher was published in the MLB payload used, so the pitching matchup is not modelled
  and the baseball prices are the softest on the board (`F-7A-13`).
* Gates run on the finished tree:
  * `python3 scripts/s7a5b5360_validate.py` → **PASSED** — 14 pages, 32 fixtures, 231 markets,
    18 predictions, 26 70%+ selections, 0 errors.
  * `python3 scripts/validate.py` (repository-wide) → **VALIDATION PASSED** — 222 published HTML
    pages, 0 errors, 0 warnings (baseline before this session was 208 pages, 0 errors).
  * `python3 scripts/final_audit.py` → exits 0.

## 5. Repository review findings

Full text and evidence on `7a5b5360/flagged.html`; summarised here.

| ID | Where | Finding |
|---|---|---|
| R-01 | `README.md:56` | Claims "160 published HTML pages"; the validator counts 222 today. The 0-broken-link claim is true, the page count is stale. |
| R-02 | `README.md:51-53` | Headline counts (134 events, 126 H2H books, 31 High picks) match today's validator output. |
| R-03 | `COORDINATION.md:7` | Header still reads "Last updated 2026-10-21T08:01:32Z" although the board runs to §30 and T40. |
| R-04 | `data/`, `datasets/` | 18 tracked datasets across 5 namespaces with different counts (134 / 217 / 145). No single canonical dataset; this desk adds a sixth namespace and touches none of the others. |
| R-05 | `COORDINATION.md` §1 | T35 (AFLW re-price), T19 and T10 remain open from earlier sessions and are outside this session's scope. |
| R-06 | whole tree | Every tracked JSON parses, no `.pyc` tracked, `.gitignore` covers `__pycache__/` and `*.pyc`. |

## 6. Deviations and limitations

1. **Coverage is 5 of 17 in-scope sports.** The other twelve are published as unverified with the URL
   that was tried (`F-7A-14`). This is a fresh snapshot, not a replacement for the older desks.
2. **The NHL total-goal line is a documented baseline** (6.0 goals, sd 2.0), not a team-specific
   scoring rate, so total prices repeat across the slate. Stated on the Markets page.
3. **F1 start time is derived** from the two clocks the official page prints (`F-7A-12`).
4. **No injury, team-news, weather or head-to-head claim is made anywhere**, because none was read on
   an official page today.
