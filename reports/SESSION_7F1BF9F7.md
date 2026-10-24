# Session `7f1bf9f7-olbg1` — T7F1B clarity rebuild (24 October 2026)

## What was asked

The recurring complaint was presentational and evidentiary: the repository has 55 sibling
dashboards, the canonical root publishes zero picks, and nothing on the domain said *here is the
pick, here is the price, here is the source*. The brief also asks for five High-confidence picks per
sport per day, each with a unique human write-up of at least 30 words built from official facts.

## What was built

A single desk at `/today/`, 26 pages, no JavaScript, no remote assets:

| Page | Purpose |
| --- | --- |
| `index.html` | Executive summary. Picks are the first table on the page, highest confidence first. A "where the picks are" line names the two other pages that hold them. |
| `picks.html` | The same pick list plus the tier reason for each pick and an explicit list of picks deliberately not issued. |
| `predictions.html` | One written prediction per pick, each with its official fact block underneath. |
| `matches.html` | The seven matches that carry an official source link, with the fields actually read. |
| `discovery.html` | All 60 OLBG listings across the fifteen requested sports, labelled discovery-only. |
| `markets.html` | 13 originated prices with the formula and input behind each. |
| `sports.html` + 15 subpages | Per-sport counts and the specific reason for each gap. |
| `flagged.html` | Eight flags, each with a source link. |
| `repo-audit.html` | Seven repository findings with file paths. |
| `sources.html` | Nine official reads and fifteen discovery reads, with timestamps. |
| `methodology.html` | The tier rule, the pricing rule, and why the High tier is empty. |

The canonical builder (`pipeline/build.py`) gained two surgical additions: a "Today's picks (clear
view)" entry at the top of the workspace navigation and a one-line banner above the page heading on
every canonical page. Nothing else in the canonical pipeline, data or workflow was touched.

## Sources read this session (all official unless marked)

| Source | URL | Read at (UTC) | What it gave |
| --- | --- | --- | --- |
| NHL schedule | https://api-web.nhle.com/v1/schedule/2026-10-24 | 17:06 | Game IDs, venue, UTC start, six provider prices |
| NHL standings | https://api-web.nhle.com/v1/standings/2026-10-24 | 17:07 | Club records, L10, home split, goals for/against |
| NHL club stats (SJS) | https://api-web.nhle.com/v1/club-stats/SJS/20262027/2 | 17:26 | Skater games played only — club record not returned |
| MLB schedule 24 Oct | https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-10-24 | 17:08 | World Series Game 2, gamePk 849802, `ifNecessary=N` |
| MLB schedule 23 Oct | https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-10-23 | 17:33 | Game 1 final: Milwaukee 3, Tampa Bay 2 |
| MLB standings | https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026 | 17:34 | Regular-season W-L and runs for/against (AL clubs only in the segment read) |
| Formula 1 | https://www.formula1.com/en/racing/2026/united-states | 17:30 | Session times, 56 laps, FP2 classification |
| ATP scores | https://www.atptour.com/en/scores/current | 17:10 | Semi-final results and official seed numbers |
| OLBG hubs (15) | `https://www.olbg.com/betting-tips/<Sport>/<id>` | 17:09–17:20 | What each sport is advertising — discovery only |

Two official routes were attempted and failed, and are recorded rather than worked around:
`cdn.nba.com` returned HTTP 500 and `data.nba.com` returned AccessDenied, so no NBA team input
exists; `pdc.tv` returned a consent wall instead of a draw, so no darts match could be confirmed.

## Picks issued

| Match | Selection | Chance | Fair | Tier |
| --- | --- | --- | --- | --- |
| Medvedev vs Basilashvili (Almaty final) | Medvedev to win | 75.6% | 1.32 (-310) | Medium |
| Sharks at Bruins | Boston Bruins moneyline | 62.1% | 1.61 (-164) | Medium |
| Rays at Brewers (WS Game 2) | Rays to win | 54.5% | 1.83 (-120) | Low |
| United States GP | Leclerc to win | 31.0% | 3.23 (+223) | Low |
| United States GP | Verstappen to win | 29.0% | 3.45 (+245) | Low |

**No High picks.** The brief's band starts at -250, which is a 71.43% chance, and its High rule
starts at 70%. Satisfying both needs a probability inside a 1.43-point window. Nothing verified
today lands inside it, and the desk says so on the front page, on the method page and in flag
F-7F-03 rather than moving a number.

## Verification performed

* Every fixture row links to the publisher it was read from; the validator rejects any link to a
  host that is not on the official list.
* Every price carries a written basis string. Where only an official quote existed, the pair was
  de-vigged and the arithmetic is stated; where it did not, the formula is stated and the row is
  marked as a research line.
* Unread fields stay `None` in `scripts/today_data.py` and blank on the page. The test suite asserts
  the known gaps are still `None`, so a later session cannot quietly fill them in.
* Predictions: five, each ≥30 words, unique, naming its selection, with `model` and `verified`
  excluded by gate and by test.
* Gates run and passing: `scripts/today_validate.py` (26 pages, link/fragment/source/tier checks),
  `tests/pipeline/test_today_desk.py` (14 tests), `python -m unittest discover -s tests/pipeline`,
  `python -m unittest discover -s tests -p 'test*.py'`, `scripts/validate.py`,
  `python -m pipeline.build --out _site` + `python -m pipeline.validate --site _site` (0 errors).

## Repository findings (published on `/today/repo-audit.html`)

R-01 the 66 High picks in `data/8aede3ba/fixtures.json` all sit at one fair price, which means the
tier was set by the window rather than by the fixture; R-02 that file carries claims (a 38-point
Celtics debut for Paul George, New York as reigning champion) that no source in the repository
supports; R-03 the canonical root publishes zero High and zero Medium; R-04 55 sibling desks and
141 MB of tracked files with no index of which is current; R-05 duplicate section headings in
`COORDINATION.md`; R-06 the README and the sibling desks contradict each other; R-07 no root
navigation reached a page with actual picks.

## Honest limits

This is not the five-per-sport, 75-pick deliverable. It is 7 verified matches and 5 picks with full
write-ups, plus the complete 60-row OLBG inventory for the fifteen requested sports. The gap is
published sport by sport with the specific missing input. Four inputs would close most of it: goal
rates for both sides in hockey and handball, a published total or handicap quote, an official
availability feed, and an official tennis order of play.


## Publication receipts (2026-10-24T18:52Z)

* PR [#229](https://github.com/buffedlizard55-lab/OLBG1/pull/229) merged as `f36fcd8` after CI run `40116135980` passed.
* PR [#267](https://github.com/buffedlizard55-lab/OLBG1/pull/267) merged as `c7d9c88` after CI run `40121657089` passed. That PR exists because a later commit made the published artifact stage only a whitelisted list of desks, so `today/` had to be registered in `pipeline/build.py`'s `ARCHIVE` before it could be served.
* Pages build reported `built` for `c7d9c88`; live read-back confirmed `/today/index.html` (5 picks, 0 High, 7 matches, 60 listings), `/today/predictions.html` (five write-ups with official fact blocks) and `/today/repo-audit.html` (R-01…R-07).
* Root front page lists the desk under earlier desks and links to it.
