# Session `2988bd19-olbg1` — T2988 independent live desk, 22 October 2026

**Desk:** `/2988bd19/` · **Data:** `data/2988bd19/desk.json` · **Task:** T2988 (board §62)

## 1. What was built

A namespaced, source-linked desk for the 22 October 2026 slate, built from **28 official or
discovery reads** performed during this session and nothing else.

| Measure | Count |
|---|---|
| Listings in the snapshot | 43 |
| Fixtures confirmed on an official league page | 20 |
| Priced fixtures (our own lines) | 18 |
| Originated market lines | 90 |
| Priced selections | 600 |
| High picks (both rules + written case) | 2 |
| Written predictions (≥30 words, unique) | 2 |
| Flags published | 13 |
| Sources with URL and read window | 28 |

Coverage: ice hockey 12/12 NHL games verified and priced; baseball 6/6 World Series fixtures verified and
priced; basketball 2 NBA fixtures verified but unpriced, 3 EuroLeague fixtures discovery-only; tennis 14,
cricket 3 and darts 3 discovery-only; eleven in-scope sports published as gaps with reasons.

## 2. Sources actually read (one window: 20:48–20:59Z, 22 Oct 2026)

Official governing-body / league sources:

- `api-web.nhle.com/v1/schedule/2026-10-22` — 12 games, ids, venues, `startTimeUTC`
- `api.nhle.com/stats/rest/en/team/summary` — 26 club rows: GP, W-L-OTL, points, GF, GA, PP%
- single-club re-reads for Nashville (teamId 18) and Winnipeg (teamId 52)
- `api.nhle.com/stats/rest/en/skater/summary` — top three skaters for TOR, NYR, SJS, BOS
- `api-web.nhle.com/v1/scoreboard/2026-10-22` — final scores for 19 and 20 October
- `api-web.nhle.com/v1/standings/2026-10-22` — standings stamp 2026-10-22T20:49:30Z
- `statsapi.mlb.com` schedule 18–30 Oct, 2026 standings, Milwaukee hitting and pitching splits
- `nba.com/schedule?date=10/22/2026` and `nba.com/standings`
- `euroleaguebasketball.net/en/euroleague/standings/` — all 20 clubs

Discovery and failed reads (recorded, not used as fact):

- OLBG home, ice hockey, baseball, basketball, tennis, cricket and snooker hubs
- `pdc.tv` returned a cookie-consent wall
- `atptour.com/en/scores/current` returned completed matches only
- `unitedrugby.com/fixtures` returned the site's 404
- `euroleaguebasketball.net/en/euroleague/game-center/` rendered no fixture rows

## 3. The High gate, applied literally

A selection must have **p > 70%** *and* a fair price inside **−250…+10000**. Those conditions can only
both hold for 70.00% < p ≤ 71.4286% — a 1.43-point window.

- 127 of 600 prices are above 70%.
- 7 fall inside the window.
- 2 have the player-, form- and result-level evidence the brief requires:
  - **Toronto +1.5** vs NY Rangers — 70.64%, fair −241 (P-2988-01)
  - **San Jose over 1.5 team goals** at Ottawa — 71.27%, fair −248 (P-2988-02)
- 5 in-window selections are capped at Medium and published with the reason.
- 120 selections are above 70% but priced shorter than −250, including the slate's strongest favourite
  (Minnesota 73.08%, −271), which the price floor excludes.

## 4. Verification performed

- Every priced fixture has a governing-body URL, and its venue and UTC start were transcribed from that page.
- Team totals were transcribed, not recalculated from match lists.
- Source timestamps: the fetch tool does not expose per-request HTTP metadata, so the desk publishes one
  observation window (20:48–20:59Z) and the read order rather than invented per-read stamps (F-2988-13).
- Every published probability is re-derived from the published lambdas by
  `scripts/s2988bd19_validate.py`; a mismatch of more than 2×10⁻⁶ fails the build.
- Fair decimal = 1/p and the American price is derived from it; both are re-checked.
- Each prediction's numeric claims are listed with the source id they came from, and the two bodies are
  checked for shared eight-word phrases (none).
- No price is published on an event whose fixture was not officially read.

## 5. Irregularities (published on `/2988bd19/flagged.html`)

F-2988-01 the 1.43-point window · F-2988-02 NBA unpriced · F-2988-03 EuroLeague fixtures unconfirmed ·
F-2988-04 PDC consent wall · F-2988-05 ATP page showed completed matches only · F-2988-06 MLB model lacks
postseason inputs · F-2988-07 NHL model lacks goaltender/injury/rest · F-2988-08 Anaheim +1.5 misses the band
by 0.05 points · F-2988-09 later World Series games are conditional · F-2988-10 OLBG tip shares are votes ·
F-2988-11 eleven in-scope sports had no official read · F-2988-12 prices are estimates, not offers ·
F-2988-13 read timestamps replaced by one honest observation window.

Three defects were found by reading the **deployed** bytes rather than the build status and are fixed in the
final follow-up: the coverage register printed `High = 0` for ice hockey (the helper counted fixtures, not
High selections), F-2988-05 still said fifteen tennis listings after the source row was corrected to
fourteen, and F-2988-13 was ordered before F-2988-12.

Repository findings (`/2988bd19/repo-review.html`): duplicate section numbers in `COORDINATION.md` (§4 at
lines 185/2330, §13 at 722/729, §43 at 2160/2525), duplicate task ids (T63 at 123/125, T64 at 129/2941,
T1–T7 in two tables), six rows still `in progress` beyond the 60-minute rule, and 17 pages over 200 KB
(largest 1,064,556 B). None was patched: those files belong to other sessions or to final integration.

## 6. Gates

```
python3 scripts/s2988bd19_validate.py
  → T2988 VALIDATION PASSED — 0 errors, 1 warning (San Jose pick is within 0.01 of the −250 decimal floor)
python3 scripts/validate.py
  → VALIDATION PASSED — 0 errors, 3 pre-existing warnings in f7fa77fc/flagged.html (793 pages link-checked)
python3 -m pipeline.validate --site .
  → Canonical validation: 0 errors
python3 -m unittest discover -s tests/pipeline -q
  → OK
```

## 7. Honest limits

This is not worldwide coverage. Eleven in-scope sports have no verified fixture in this snapshot, the NHL
sample is 7–12 games per club, and the MLB model ignores starting pitchers. The desk publishes its own fair
prices; it does not quote, and cannot confirm, any bookmaker's available odds, and nothing here is betting
advice.
