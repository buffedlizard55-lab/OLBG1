# Session 546fc70f-olbg1 — T546F independent namespaced desk (22 Oct 2026)

Desk: `/546fc70f/` (landing, matches, markets, high-confidence gate, predictions, analysis, sources, Flagged for Review, 17 sport subpages).
Branch: `arena/546fc70f-olbg1` (Arena-pinned). Data: `data/546fc70f/`. Scripts: `scripts/s546fc70f_{model,build,validate}.py`.

## Scope actually covered (be precise)

| Sport (in scope) | Status | Why |
|---|---|---|
| Basketball — EuroLeague only | 14 upcoming games priced (rounds 7–8) | Official EuroLeague API read in full (66 played games, 14 upcoming) |
| Ice Hockey — NHL | 4 games priced (official feed), 8 OLBG-listed games NOT priced | Official standings read in full (32 teams); official score/schedule feed read for 4 games only |
| Baseball — MLB | No games on 22 Oct | `statsapi.mlb.com` sportId=1 returned `totalGames: 0` |
| Basketball — NBA | Not covered | `cdn.nba.com` scoreboard returned HTTP 500 |
| Tennis (ATP) | Not covered | Scores/rankings pages read as coverage check only; no match priced |
| Other 13 in-scope categories | Not covered | No official source read in this session |

Out of scope by client brief (not touched): soccer/football, boxing, UFC/MMA, American football, hurling, horse racing, cycling, specials.

## Verification performed (line by line)

* EuroLeague results: all 66 played games were transcribed into `data/546fc70f/euroleague_e2026_results.csv` with game numbers and scores. The count check matches the feed (games 1–65 and 67 played, 66 and 68–70 unplayed in round 7).
* EuroLeague schedule: the 14 unplayed games in rounds 7–8 were transcribed into `euroleague_e2026_upcoming.csv`. Team names are checked against the results file (the model asserts every fixture team has played games).
* NHL standings: all 32 teams transcribed into `nhl_standings_2026-10-22.csv`. Internal check: wins + losses + OT losses = games played for all 32 teams (passed). Records for BOS, NSH, NYR, TOR also agree with the score feed's own `record` field.
* NHL games: four games confirmed from the official schedule/score feed (2026020154–2026020157), start 23:00 UTC each.
* Every prediction names its game ID, teams, selection, tier and official sources. Team facts (records, points, last three results) were re-checked against the CSVs by hand before publication. Several wording corrections were made before publication, including one unsupported Nashville record claim (removed) and two EuroLeague home/away phrasings (fixed).
* `scripts/s546fc70f_validate.py`: PASSED (26 pages, 9 predictions, 320 market rows, 0 broken relative links, every data table row carries an official-host link, prediction numbers match the model, High label only when the strict gate passes).
* Existing repository gates re-run: `python -m pipeline.validate --site .` (0 errors), `python scripts/validate.py` (PASSED), `unittest discover -s tests/pipeline` (OK), `unittest discover -s tests -p 'test*.py'` (OK).

## Results

* 18 official-fixture winner picks: **0 High**, 10 Medium, 8 Low (strict gate).
* The brief's price window and the >70% rule only overlap for p in (70.0%, 71.4%]. No winner pick falls in that band. The closest is Valencia at −253 (71.7%), three points outside. Probabilities above 71.4% are priced beyond −250 and are labelled Medium, flagged as outside the window.
* Five EuroLeague and four NHL predictions were written. Each is labelled with its real tier (Medium or Low) and none is labelled High.
* EuroLeague walk-forward backtest (46 games, rounds 3–7): log loss 0.635 against 0.693 for a coin flip; accuracy 65.2%. The 60–70% favourite band won 80% of 20 games against a mean probability of 63.7%, which suggests under-rating. The 70%+ band has four games, too few to conclude anything.

## Irregularities and unverified items (published on `/546fc70f/flagged.html`)

See the Flagged page for the full list with links (F-546-01 to F-546-11). Headline items:
* OLBG lists NSH @ BOS at 19:07; the official NHL feed gives 23:00 UTC (19:00 Eastern). A 7-minute discrepancy on the discovery source.
* EuroLeague feed has two time columns with no time-zone label. Times are shown as published.
* EuroLeague game 66 shows as unplayed, but its published time may already have passed.
* Eight of twelve OLBG-listed NHL games are not confirmed by the official feed read here, so they are not priced.
* 15 of 17 in-scope categories have no official source read. This is the largest coverage gap.
* Model: no home term, no injuries, no player data for EuroLeague, NHL not backtested. All fair prices are our own estimates, not bookmaker prices.
* Repository state: T97DC and T-FEC are listed in progress with no recent commits; PRs #40 and #63 are open. Left untouched (not in this session's scope).

## Scope compliance

Only `data/546fc70f/**`, `scripts/s546fc70f_*.py`, `546fc70f/**`, `reports/SESSION_546FC70F.md` and append-only additions to `COORDINATION.md` were written. No root page, `pipeline/**`, workflow, `data/current/**`, `data/lines.json`, `data/predictions.json` or other session's desk was modified.
