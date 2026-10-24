# Session 3507B0 — 24 October 2026 desk

Scope: the fifteen sports named in the brief, with the site rebuilt as one dashboard and every price
originated here rather than copied. This file is the paper trail: what was read, when, what it said,
what was priced from it, what was withheld, and what is still wrong.

## 1. Sources read (all times UTC, 24 October 2026)

| # | Source | URL | Read at | What it supplied |
|---|---|---|---|---|
| 1 | NHL schedule, 24 Oct | <https://api-web.nhle.com/v1/schedule/2026-10-24> | 17:52 | 12 games; exact UTC start, venue, game ID, partner moneyline for each |
| 2 | NHL schedule, 25 Oct | <https://api-web.nhle.com/v1/schedule/2026-10-25> | 17:58 | FLA@CHI 19:00, NYI@DAL 22:00, MTL@WPG 23:00 (Heritage Classic, neutral, Princess Auto Stadium), COL@NSH 26 Oct 00:00 |
| 3 | NHL standings, 24 Oct | <https://api-web.nhle.com/v1/standings/2026-10-24> | 17:42 | All 32 clubs: W-OTL-L, goals for/against, home and road splits, last ten, streak |
| 4 | MLB post-season schedule | <https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-24&endDate=2026-10-31> | 17:44 | World Series games 849802, 849804, 849803, 849799, 849801, 849800 |
| 5 | MLB results, 23 Oct | <https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-10-23> | 17:45 | Final, game 849805: Rays 2, Brewers 3 — Milwaukee leads the series 1-0 |
| 6 | MLB standings (NL) | <https://statsapi.mlb.com/api/v1/standings?leagueId=104&season=2026&standingsTypes=regularSeason> | 17:46 | Brewers 103-59, home 55-26, away 48-33, last ten 8-2 |
| 7 | MLB standings (AL) | <https://statsapi.mlb.com/api/v1/standings?leagueId=103&season=2026&standingsTypes=regularSeason> | 17:47 | Rays 98-64, home 55-26, away 43-38, last ten 5-5 |
| 8 | OLBG ice hockey hub | <https://www.olbg.com/betting-tips/Ice_Hockey/13> | 17:39 | Discovery only: which matches OLBG lists, and its member tip shares (votes, never used as probabilities) |
| 9 | ATP Tour live scores | <https://www.atptour.com/en/scores/current> | 18:02 | Semifinal results in progress — no machine-readable list of *upcoming* matches |

The fourteen OLBG hubs for the other sports are linked from each sport page
(`/betting-tips/{Sport}/{id}`); they were not re-read in this session, and no fixture was invented to
fill the gap.

## 2. Prices

One model, documented on `methodology.html` and implemented in `pipeline/desk.py`:

* Each club's scoring and conceding rate is shrunk toward the league rate (prior worth ten games at
  2.90 goals), so an eleven-game sample cannot outvote the rest of the league.
* Expected goals per side = average of that side's attack and the opponent's defence, with a 0.15
  home adjustment (no adjustment at a neutral site).
* Match winner, from a normal approximation of the goal difference (σ = 1.9).
* Puck line, from the same distribution shifted by the line.
* Total goals, from σ = 2.4.
* Baseball: log-5 on the two clubs' season win rates, home edge +0.025.

Picks are chosen per fixture in a fixed order: the match winner first, and only if that market has no
selection at 55% or better, the best of the other investigated markets. Puck-line selections are never
picked, because a +1.5 cushion converts a coin flip into a near-certainty and makes a cheap "high
confidence" pick that says nothing.

| Tier | Rule | Count today |
|---|---|---|
| High | originated chance ≥ 60% and fair price in [−250, +10000] | 6 |
| Medium | originated chance 55–60% in the same band | 5 |
| Withheld | below 55%, outside the band, or an input is missing | the rest of the board |

Worked example (San Jose at Boston): Boston 42 GF / 22 GA in 11 games, San Jose 33 / 37 in 11.
Shrunk rates give Boston 3.48 attack and 2.52 defence, San Jose 2.91 / 3.09; adding home ice, Boston
projects 0.87 goals clear, which is 68.1% and a fair −214. The NHL feed's partner price for the same
game is −192, so our number is the shorter of the two — recorded on the row rather than hidden.

## 3. Verification log

Every row of every table on the site carries the official page it came from, and the source table
gives the exact read time. Four claims were withdrawn during the build and are not on the site:

1. "Carolina keeps the biggest goals-for column here" — false: Colorado has 81 goals to Carolina's 80.
2. "Dallas has won four consecutive games" written twice in one paragraph — the duplication was cut,
   not the fact.
3. "Nashville's thinnest attack on this slate" — Philadelphia (20 goals in 12) scores less, but is not
   priced, so the claim was narrowed to "of any club priced here".
4. "Neither club keeps opponents below three on average" — false: Carolina concedes 2.75. Replaced with
   the two actual rates.

Two arithmetic errors were also caught on a second pass: Buffalo has taken four of eight road points,
not three, and Nashville's 3.33 goals against is a season rate, not a road rate.

## 4. Flagged for review (published on `flagged.html`)

| ID | Item |
|---|---|
| F-3507-01 | The brief's two High-confidence conditions contradict each other; resolved by treating the band as the rule |
| F-3507-02 | 13 of 15 sports have no official fixture captured today |
| F-3507-03 | One NHL game on the OLBG list (MIN@SEA) was not in the parts of the official feed read; it is not listed |
| F-3507-04 | No injury report was read for any match, so no write-up claims one |
| F-3507-05 | The prices in the "publisher price" column are the NHL feed's partner prices, not a market survey |
| F-3507-06 | Five clubs (Anaheim, Columbus, Calgary, Chicago, Los Angeles) have fixtures but no price because their record was not read |

## 5. Repository changes

* `pipeline/desk.py` — new: the captured facts, the pricing method, the picks and the eleven write-ups.
* `pipeline/build.py` — rewritten as a 25-page builder with one stylesheet and no JavaScript.
* `pipeline/validate.py` — `validate_desk` enforces the band, the tier thresholds, the 30-word floor,
  the banned vocabulary, one source link per row, and every local link.
* `tests/pipeline/test_routes.py`, `tests/pipeline/browser.cjs` — rewritten for the new page contract.
* `README.md`, `reports/SESSION_3507B0.md`, `COORDINATION.md` — updated.

Gates: `python3 -m pipeline.build` (25 pages) · `python3 -m pipeline.validate --site .` (0 errors) ·
`python3 scripts/validate.py` (0 errors) · `python3 -m unittest discover -s tests/pipeline` ·
`node tests/pipeline/browser.cjs`.
