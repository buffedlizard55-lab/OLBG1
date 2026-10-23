# Session e58210b8-olbg1 — T5821 report

**Desk:** `e58210b8/` · **Data:** `data/e58210b8/` · **Generators:** `scripts/se58210b8_{data,model,predictions,build,validate}.py`
**Claim:** `COORDINATION.md` task `T5821` with receipt section `§73`, committed and pushed (`681382d`) before any
implementation file was written. **Baseline:** `87a39e3` (branch `arena/e58210b8-olbg1`).
**Read window:** 2026-10-23T18:40Z → 2026-10-23T19:40Z. **Evidence snapshot:** `2026-10-23T19:35:00Z`.

## 1. What was asked, and the arithmetic that constrains it

The brief asks for high-confidence calls **above 70%** whose price sits in the **−250…+10000** band.

* American −250 = decimal 1.400 = implied **71.4286%**.
* Price is fair decimal = 1/p with zero margin, so any probability above 71.4286% prices **shorter**
  than −250 and therefore falls outside the band.
* The two rules only overlap on **70.0000% ≤ p ≤ 71.4286%**.

On this slate that intersection is empty. Four calls clear 70% — Vegas 77.12%, New Jersey 76.46%,
Boston 76.02%, Edmonton 72.25% — and each originates a price shorter than −250 (−337, −325, −317,
−260). Nothing sits between 70% and 71.4286%.

Resolution applied: **confidence derives from probability alone** (≥0.70 high, ≥0.60 medium, else
low) and the price window is reported as a separate field on every call
(`band`, `pick_in_window`, `high_and_in_window`). The desk publishes the conflict on
`high-confidence.html` and as flag `F-5821-03` instead of shading a probability or promoting a
medium call into the band. The strongest calls *inside* the band are Anaheim at Philadelphia
(68.13%, −214), Detroit at Calgary (67.72%, −210) and Florida at Chicago (66.69%, −200), all medium.

## 2. Official sources read

| Source | URL | Read (UTC) | What it gave |
|---|---|---|---|
| NHL schedule | https://api-web.nhle.com/v1/schedule/2026-10-23 | 18:52 | 2 games, ids 2026020166–167, venues, UTC starts |
| NHL schedule | https://api-web.nhle.com/v1/schedule/2026-10-24 | 19:08 | 12 games, ids 2026020168–179, all `gameState: FUT` |
| NHL schedule | https://api-web.nhle.com/v1/schedule/2026-10-25 | 19:11 | `numberOfGames: 5`; only 2026020180 (FLA @ CHI) enumerated |
| NHL standings | https://api-web.nhle.com/v1/standings/now | 18:58–19:05 | all 32 clubs: GP, W, L, OTL, PTS, GF, GA, L10, streak, home/road splits, `standingsDateTimeUtc 2026-10-23T19:29:30Z` |
| MLB schedule | https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-23&endDate=2026-10-28&hydrate=team | 19:03 | 2026 World Series Rays @ Brewers, gamePks 849805 / 849802 / 849804, venues |
| MLB standings | https://statsapi.mlb.com/api/v1/standings?leagueId=104&season=2026 | 19:14 | NL table: Brewers 103-59, RS 832 / RA 618 |
| ATP scores | https://www.atptour.com/en/scores/current | 19:24 | quarter-final results only; no order of play for 24 Oct |
| WST tournaments | https://www.wst.tv/tournaments/ | 19:27 | Northern Ireland Open, Belfast, 18–25 Oct 2026 |
| WST matches | https://www.wst.tv/matches/b4533c9e-8d2c-4ecc-8dfd-c6b284705578 | 19:30 | Round 1 results, session clocks with no timezone label |
| OLBG sitemap | https://www.olbg.com/sitemap-betting-tips.xml | 18:44 | hub routes and sport ids for all 15 in-scope sports |
| OLBG hubs | https://www.olbg.com/betting-tips/Tennis/3 · /Ice_Hockey/13 · /Ice_Hockey/NHL/13 | 18:46–18:49 | all three returned the literal empty state "No tips found." |
| OLBG robots | https://www.olbg.com/robots.txt | 18:43 | `/api/` and `/storage/app/json_data/` disallowed; neither requested |

No media outlet, aggregator, tipster or sportsbook is used as a source. No bookmaker price is used as
a model input. `robots.txt` was read before any OLBG path was requested.

## 3. Coverage: what is published and what is not

| Sport | Rows | Status |
|---|---|---|
| Ice Hockey | 15 | priced, three originated markets each |
| Baseball | 3 | listed, **unpriced** — only Milwaukee's official record was read |
| Tennis | 0 | results only; no 24–25 Oct order of play was read |
| Snooker | 0 | Round 1 results only; session clocks carry no timezone |
| Golf, Cricket, Rugby Union, Rugby League, Motor Racing, Darts, Handball, Volleyball, Gaelic Sports, Greyhounds, Basketball | 0 | official fixture list not read this pass |

Thirteen sports publish zero rows and say so on their own page and on `flagged.html`. The brief
covers 15 sports and asks for five high-confidence calls per covered sport per day; this release
carries **18 fixture rows, 6 written calls, all in ice hockey**. Rows and calls were not manufactured
to fill the table. The 13 gaps are itemised as `F-5821-01` with a per-sport reason string.

Harvesting stopped early for a mechanical reason: the page-fetch tool began returning
`SignatureDoesNotMatch` errors from its proxy for every subsequent request (ATP, WTA, WST, URC, AL
standings). That is recorded rather than worked around with remembered values.

## 4. Model

Per club, two estimators are averaged:

* binary record share `w / gp` (OT and SO losses count as losses);
* Pythagorean expectation `GF² / (GF² + GA²)`, exponent 2.

Sides are compared with `log5(pa, pb) = (pa − pa·pb) / (pa + pb − 2·pa·pb)`. No home-ice edge, no
default rating for a missing club, no bookmaker quote anywhere. Fair decimal is `1/p` with zero
margin. Published decimals and American prices are both derived from the **rounded published
probability**, so 1/p, the decimal and the American price always reconcile on the page.

Handicap and totals come from an independent Poisson goal distribution with
`λ_home = (GF_h/GP_h + GA_a/GP_a)/2`, truncated at 13 goals. Puck line −1.5 = P(regulation win by
≥2); total 5.5 = P(regulation goals ≥6). Overtime and shootout goals are excluded, which biases the
under side — disclosed on every totals row and as `F-5821-09`.

Output: **18 books · 45 markets · 90 outcome prices** in `data/e58210b8/lines.json`, with per-market
withheld families (player props, correct score, period betting) published with a reason.

## 5. Predictions

Six hand-written calls (`scripts/se58210b8_predictions.py`): Vegas, New Jersey, Boston, Edmonton
(above 70%), plus Anaheim at Philadelphia and Carolina at St. Louis (strongest in-window calls).
Every call is 59–83 words, unique, contains its own selection phrase verbatim, cites its sources,
and contains neither "model" nor "verified". No injury or line-up claim appears anywhere: no official
availability page was read, so none was inferred (`F-5821-08`).

## 6. Reverse-engineering findings worth carrying forward

1. **OLBG hubs render an empty state to non-browser clients.** `/betting-tips/Tennis/3`,
   `/Ice_Hockey/13` and `/Ice_Hockey/NHL/13` all returned SEO prose plus `No tips found.` with no
   event rows in the delivered HTML. OLBG therefore supplied route grammar only. This is a discovery
   limitation, not evidence that OLBG lists no events (`F-5821-05`).
2. **`api-web.nhle.com/v1/schedule/<date>` embeds an `odds[]` array per side** whose providers mix
   decimal and American formats and disagree on direction: for Montreal at Chicago provider 6 shows
   MTL 2.35 while provider 8 shows MTL −169 on the same side. Unusable as a price input; the desk
   discloses it instead (`F-5821-04`).
3. **WST prints session clocks with no timezone** (`05:00 Sun 18 Oct`) while Belfast is on BST until
   25 October, so no snooker start time is published (`F-5821-06`).
4. **`statsapi.mlb.com` standings need `leagueId`**; `?teamId=<single id>` returns an empty
   `records` array and `?teamId=139,158` returns "Invalid Request with value".

## 7. Repository review

* Shared pages, workflows and `pipeline/` were not touched. All new files live under `e58210b8/`,
  `data/e58210b8/`, `scripts/se58210b8_*.py`, `tests/pipeline/test_desk_e58210b8.py` and this report.
* `pipeline.build.stage_existing()` copies tracked files, so the desk serves from
  `/OLBG1/e58210b8/` with no shared navigation edit; it is committed before `_site` is built.
* `scripts/validate.py` link-checks every HTML file in the repository, including this desk.

## 8. Gates

| Gate | Result |
|---|---|
| `python3 -m unittest discover -s tests/pipeline` | 187 tests, OK (includes 10 new `test_desk_e58210b8` tests) |
| `python3 -m unittest discover -s tests -p 'test*.py'` | 38 tests, OK |
| `python3 -m pipeline.validate --site .` | 0 errors |
| `python3 scripts/validate.py` | 0 errors, 3 pre-existing warnings in `f7fa77fc/flagged.html`; 1157 pages link-checked |
| `python3 scripts/se58210b8_validate.py` | OK — 24 pages, 18 rows, 4 high calls, 388 unique 6-grams |
| `python3 -m pipeline.build --out _site` then `--site _site` | see release receipt in `COORDINATION.md` |

## 9. Flagged for review (10 items)

`F-5821-01` 13 sports carry no rows · `F-5821-02` baseball unpriced · `F-5821-03` all four high
calls price shorter than −250 · `F-5821-04` NHL odds array inconsistency · `F-5821-05` OLBG empty
state · `F-5821-06` unlabelled snooker clocks · `F-5821-07` 25 Oct games counted but not enumerated ·
`F-5821-08` no injury evidence · `F-5821-09` totals exclude OT/SO · `F-5821-10` 8–12 game sample.

None of these blocks publication; each shows a hole rather than filling it with a guess.
