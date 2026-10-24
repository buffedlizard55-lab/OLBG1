# Session report — `350700b0-olbg1`, task `T3507B0`

**Window:** 2026-10-24, 17:50–19:10 UTC
**Scope:** clarity rebuild of the published site, fresh 15-sport pass, originated prices, written
predictions, validator and browser gates, PR, merge and Pages read-back.
**Result:** 21 matches listed, 13 priced, 33 markets, 11 picks (6 High, 5 Medium), 11 written
predictions, 6 review flags, 0 validator errors, 482 unit tests passing.

---

## 1. The problem this session set out to fix

The published site had grown to **1,559 HTML pages** across more than eighty parallel desks because
`stage_existing()` copied every tracked repository file into the `_site` artifact. The landing page was
a research workspace with no picks on it, and the previous three desks had all published **zero**
high-confidence selections, because their High gate required both `p > 0.70` *and* a fair price inside
−250…+10000 — a 1.4-point overlap that almost nothing can satisfy (their own flag F-3D-09).

Two changes fix that at the root:

1. the artifact now contains **this desk only** — 25 pages;
2. the band is the hard rule, with a 60% floor for High, and the reason is written on the methodology
   page rather than buried in a coordination log.

## 2. Sources read this session (all UTC)

| ID | Publisher | URL | Read | Used for |
| --- | --- | --- | --- | --- |
| `nhl-schedule-2410` | NHL | <https://api-web.nhle.com/v1/schedule/2026-10-24> | 17:52 | Game IDs, exact UTC starts, venues, neutral-site flag, partner moneylines for the twelve games of 24 Oct |
| `nhl-schedule-2510` | NHL | <https://api-web.nhle.com/v1/schedule/2026-10-25> | 17:53 | Starts, venues, Heritage Classic neutral-site flag for 25 Oct |
| `nhl-standings-2410` | NHL | <https://api-web.nhle.com/v1/standings/2026-10-24> | 17:42 | Club records, GF/GA, home/road splits, last ten, streaks (league stamp 2026-10-24T17:42:15Z) |
| `mlb-schedule` | MLB | <https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-24&endDate=2026-10-31> | 17:55 | World Series games 2–7 with gamePk, UTC starts, venues, if-necessary flags |
| `mlb-result-2310` | MLB | <https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-10-23> | 17:56 | Game 1 final: Milwaukee 3, Tampa Bay 2 |
| `mlb-standings-al` | MLB | <https://statsapi.mlb.com/api/v1/standings?leagueId=103&season=2026&standingsTypes=regularSeason> | 17:56 | Tampa Bay 98-64, home 55-26, road 43-38, last ten 5-5 |
| `mlb-standings-nl` | MLB | <https://statsapi.mlb.com/api/v1/standings?leagueId=104&season=2026&standingsTypes=regularSeason> | 17:57 | Milwaukee 103-59, home 55-26, road 48-33, last ten 8-2 |
| `olbg-ice-hockey` | OLBG (discovery) | <https://www.olbg.com/betting-tips/Ice_Hockey/13> | 17:47 | Which match markets OLBG lists today; tip shares recorded as votes only |

Reads that failed and were **not** worked around:

* `https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json` — HTTP 500.
* `https://www.nba.com/games?date=2026-10-25` — the schedule grid rendered game counts (7 games on
  25 Oct) but the game list failed to load; "Sorry, something went wrong."
* `https://www.atptour.com/en/scores/current` — returned matches already in progress or finished
  (semifinals across four events). No future fixture with a start time could be read.

## 3. What was originated

Method (documented on `methodology.html`): shrunk scoring rates (ten-game prior at the league mean of
3.10 goals), home advantage of 0.30 goals, normal margin with σ = 1.85, totals with σ = 2.40, log5 on
shrunk win rates for MLB with a 0.025 home adjustment.

| Match | Market | Our price | Probability | Publisher price | Tier |
| --- | --- | --- | --- | --- | --- |
| San Jose @ Boston | Boston ML | −214 | 68.1% | −192 / +160 | High |
| Buffalo @ Washington | Washington ML | −161 | 61.7% | −125 / +105 | High |
| Carolina @ St. Louis | Over 5.5 | −186 | 65.0% | none published | High |
| Toronto @ Edmonton | Edmonton ML | −166 | 62.4% | −166 / +140 | High |
| Montreal vs Winnipeg (Heritage Classic) | Over 5.5 | −160 | 61.5% | none published | High |
| Colorado @ Nashville | Over 5.5 | −187 | 65.1% | none published | High |
| NY Rangers @ Ottawa | Over 5.5 | −125 | 55.6% | none published | Medium |
| Nashville @ Pittsburgh | Pittsburgh ML | −149 | 59.8% | −125 / +105 | Medium |
| Tampa Bay @ Utah | Utah ML | −129 | 56.3% | −142 / +120 | Medium |
| NY Islanders @ Dallas | Dallas ML | −138 | 58.0% | none published | Medium |
| Tampa Bay @ Milwaukee (WS Game 2) | Milwaukee ML | −123 | 55.2% | none published | Medium |

Where our price is the **longer** of the two (Boston −214 against a market −192; Washington −161
against −125; Pittsburgh −149 against −125) there is no value edge at the market price, and the site
says so: the tier is a statement about how likely the selection is, not a claim of profit.

## 4. Verification performed

* `python3 -m pipeline.validate --site _site` → **0 errors**. It checks: every source is HTTPS and on
  an official-host allowlist; every fixture carries a source and an exact UTC start; priced fixtures
  have both clubs' records; every two-way book sums to one; fair decimal is the reciprocal of the
  probability; the American price follows from the probability; the band flag matches the price;
  every pick clears 55%, sits inside −250…+10000, and its tier follows the published threshold; every
  prediction is at least 30 words, names its selection, contains none of `model`, `verified`,
  `verification`, `algorithm`, `machine learning`; no two predictions share a six-word phrase; the
  counts reconcile with the rows; every page has one `h1`, a matching snapshot marker, unique ids,
  no broken relative links or fragments, and an official source link on every table row.
* `python3 -m unittest discover -s tests/pipeline` → **482 tests, OK**, including the new site gates
  (orphan root page, band breach, short prediction, banned vocabulary, unnamed selection, count
  drift, threshold check).
* `python3 scripts/validate.py` → **0 errors, 3 pre-existing warnings** owned by desk `f7fa77fc`
  (they are unchanged and unrelated to this release).
* Line-by-line re-read of all eleven write-ups against the captured data. Four claims were withdrawn
  during that pass because the source did not support them:
  * "three of eight available road points" for Buffalo — the 1-1-2 road split is four points, corrected;
  * "has not lost since 18 October" for Dallas — no dated game log was read, removed;
  * "not conceded more than three in any of its ten games" for Dallas — no game-by-game log, removed;
  * "the liveliest scoring record on this slate" for Carolina — Colorado's 81 goals in 11 games is
    higher than Carolina's 80 in 12, removed.

## 5. Irregularities flagged (published on `flagged.html`)

* **F-3507-01** — the brief's two High conditions contradicted each other; the band now governs. Resolved.
* **F-3507-02** — thirteen of fifteen sports carry no priced match today.
* **F-3507-03** — two NHL games on the official slate were not captured (Minnesota @ Seattle on 24 Oct
  and one 25 Oct game).
* **F-3507-04** — no injury, lineup or starting-pitcher feed was read, so no write-up mentions team news
  and the MLB totals are withheld rather than estimated.
* **F-3507-05** — the "publisher price" is the league feed's partner price, not a bookmaker screenshot.
* **F-3507-06** — Anaheim, Columbus, Calgary, Chicago and Los Angeles have fixtures but no price, because
  their season records sit beyond the portion of the standings page read.

## 6. Repository changes

`pipeline/desk.py` (new), `pipeline/build.py` (rewritten), `pipeline/validate.py` (desk gates),
`tests/pipeline/browser.cjs` and `tests/pipeline/test_routes.py` (rewritten for the new contract),
root HTML regenerated (25 pages plus `assets/desk.css` and `data/desk/*`), `README.md`,
this report, and an append-only entry in `COORDINATION.md`.

Untouched: `data/fixtures.json`, `data/lines.json`, `data/predictions.json`, `data/current/**`,
`scripts/validate.py`, `scripts/s*.py`, `.github/workflows/**` and every peer `<id>/` desk.
