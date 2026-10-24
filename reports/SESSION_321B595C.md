# Session 321b595c — fifteen-sport desk, 24 October 2026

**Desk:** [`/321b595c/index.html`](https://buffedlizard55-lab.github.io/OLBG1/321b595c/index.html) ·
**Picks:** [`/321b595c/picks.html`](https://buffedlizard55-lab.github.io/OLBG1/321b595c/picks.html) ·
**Flags:** [`/321b595c/flagged.html`](https://buffedlizard55-lab.github.io/OLBG1/321b595c/flagged.html)

**One line:** 93 upcoming fixtures across all fifteen brief sports, seven originated
match-winner lines with a published probability and fair price, seven written predictions,
fifteen flags — and an explicit statement that the brief's five-high-picks-per-sport target
cannot be met honestly on a Saturday slate whose true favourites top out near 65%.

## 1. What was built

| Page | What it holds |
|---|---|
| `321b595c/index.html` | Executive summary: the seven picks in a table above the fold, then the strongest five, the three biggest disagreements with the published market, and a fifteen-sport status table |
| `picks.html` | Every pick with probability, fair price, best official price, edge, confidence, start time and source links |
| `predictions.html` | The seven written predictions, 73–107 words each, with the selection restated and sources beneath each one |
| `matches.html` | All 93 fixtures, including the 86 we refused to price and why |
| `markets.html` | 31 originated market rows: moneyline, puck line ±1.5, total 5.5/6.5 |
| `coverage.html` | Sport-by-sport: OLBG count, priced count, predictions vs the 5 target, and the exact URL that blocked the rest |
| `sources.html` | 35 reads with UTC timestamps, 20 of them official |
| `flagged.html` | All 15 flags with evidence links |
| `methodology.html` | The formulas, the bands, the 2,862-check validator |
| `repo-review.html` | Line-by-line review of the tree: stale root, duplicate clocks, market-implied "confidence", templated predictions |
| `sports/*.html` (15) | One page per brief sport, including the two that have no matches on OLBG |

Machine-readable: `data/321b595c/{summary,sources,fixtures,predictions,flags,coverage}.json`.
Code: `scripts/s321b595c_data.py`, `scripts/s321b595c_build.py`,
`scripts/s321b595c_validate.py`, `tests/pipeline/test_desk_321b595c.py`.

## 2. The picks as published

| Sport | Match | Selection | Our chance | Fair | Best official | Edge | Label |
|---|---|---|---|---:|---:|---:|---:|---|
| Baseball | Rays @ Brewers (WS G2) | Milwaukee Brewers | 65.1% | −187 | — | — | High |
| Ice Hockey | Sharks @ Bruins | Boston Bruins | 61.8% | −162 | −182 | −2.8 | Medium |
| Ice Hockey | Kings @ Devils | New Jersey Devils | 60.6% | −154 | −192 | −5.2 | Medium |
| Ice Hockey | Sabres @ Capitals | Washington Capitals | 56.7% | −131 | −102 | +6.2 | Low |
| Ice Hockey | Golden Knights @ Blue Jackets | Vegas Golden Knights | 55.7% | −126 | −132 | −1.2 | Low |
| Ice Hockey | Rangers @ Senators | Ottawa Senators | 52.8% | −112 | −109 | +0.6 | Low |
| Ice Hockey | Predators @ Penguins | Pittsburgh Penguins | 52.6% | −111 | +125 | +8.2 | Low |

Confidence bands: **High ≥ 65%**, Medium ≥ 57.5%, else Low; every published fair price sits
inside −250…+10000. The strict reading of the brief — *greater than 70%* **and** inside the
band — admits only probabilities between 70.0% and 71.4%, and **zero** selections qualified.
That is published as flag F-321-01, not papered over.

## 3. Sources read live (all with UTC timestamps on `sources.html`)

Official: `api-web.nhle.com/v1/schedule/2026-10-24` (12 games, partner prices, UTC starts),
`api-web.nhle.com/v1/standings/2026-10-24`, `api.nhle.com/stats/rest/en/team/summary`
(32-club aggregates: points %, GF/GA, PP%, PK%, shots), `statsapi.mlb.com` schedule
(World Series G1–G5 with probable pitchers and UTC first pitch), `statsapi.mlb.com`
standings (Brewers 103-59, 55-26 home, 8-2 last ten, +214; Rays 98-64, 43-38 away, +86),
`nba.com/standings`, `formula1.com/racing/2026/united-states`, `wst.tv/matches`,
`nrl.com/draw` (RLWC26 Round 2 incl. venues and two completed results).

Discovery only: the fifteen OLBG sport hubs.

Blocked, with the URL recorded on `coverage.html`: `unitedrugby.com/fixtures` (404),
`gbgb.org.uk/racecards` (404), `pdc.tv/calendar` (cookie wall), `legavolley.it` (video shell),
`premrugby.com/fixtures` (navigation only), `pcb.com.pk` (home page only),
`wta/atp` (shell or notifications only), `pgatour.com/schedule` (stopped in March).

## 4. Verification performed this session

* Re-checked every MLB figure in the headline prediction against `statsapi.mlb.com`
  standings: Brewers 103-59, home 55-26, away 48-33, last ten 8-2, 832 runs scored,
  618 allowed (+214) — all confirmed; Rays 98-64, away 43-38, last ten 5-5, +86 — confirmed.
* Re-checked the series state: Game 1 finished 2-3 to Milwaukee; Game 2 first pitch
  `2026-10-25T00:00Z`, Henderson vs Rasmussen — confirmed.
* Re-checked the NHL slate: 12 games, `startTimeUTC` for each, partner prices present for
  seven games; **removed Anaheim @ Philadelphia** because the feed showed it LIVE at 0-2
  (flag F-321-14).
* **Removed the book names** previously attached to NHL price feeds. The feed exposes
  `providerId` numbers only; naming them Tipsport/Veikkaus/FanDuel was an unsupported
  attribution (flag F-321-13). Prices are unchanged; labels now read "feed 3", "feed 9", etc.
* Re-ran the desk validator (`scripts/s321b595c_validate.py`): **2,862 checks, 0 errors** —
  source-register integrity, official source on every priced row, price↔probability
  recomputation, confidence-band recomputation, ≥30-word predictions, banned vocabulary
  (no "model", no "verified"), no shared eight-word run, zero broken links or fragments.
* `python3 -m pipeline.validate --site .` → **0 errors**; the canonical root page is untouched
  except for its single "start here" bar, which now points at `321b595c/`.

## 5. Flags that matter

| Flag | Severity | Point |
|---|---|---|
| F-321-01 | high | The two pick rules intersect only between 70.0% and 71.4% |
| F-321-02 | high | No selection cleared 70% on today's readable data (best 65.1%) |
| F-321-03 | high | Thirteen sports produced no priced pick; each blocker is linked |
| F-321-06 | high | NBA is one or two games old; a line from that sample would be invention |
| F-321-13 | medium | League odds feed identifies books by number, not name — attribution removed |
| F-321-15 | medium | NRL draw does not state the time zone behind its kick-off clock |

## 6. Honest gaps

* **Five predictions per sport was not delivered** — 7 were published against a 75 target.
  Eleven sports had no readable official fixture detail or no placeable market; two have no
  matches at all (Golf on OLBG, Rugby League on OLBG). Each is named with its blocking URL.
* **No injury designation** could be read from an official source for any priced match
  (F-321-11); the predictions say so rather than invent one.
* **No handicap or total price** is published as a pick: the originated puck-line and total
  rows exist on `markets.html`, but OLBG carries no placeable price for them, so none is
  labelled a pick.
