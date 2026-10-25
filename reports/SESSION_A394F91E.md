# Session A394F91E — 25 October 2026 fifteen-sport desk

Session `a394f91e-olbg1`, pinned branch `arena/a394f91e-olbg1`, base
`31654d812b70a1cf8f1bdcf7cab5b9b6775e1e32` (tip of `main` after PR #296).

## What was asked

Reverse-engineer OLBG for the fifteen named sports, collect the full list of updated matches,
originate our own lines on every market, grade a pick on each with low/medium/high confidence,
write unique 30-word-plus predictions for the High picks using facts from official sources, and
publish all of it on a clean GitHub Pages dashboard with a Flagged for Review page.

## What was produced

| Measure | Value |
| --- | --- |
| Sports covered | 15 of 15 |
| Pages | 25 |
| Official fixtures priced | 9 (4 NHL, 5 NBA) |
| Official fixtures listed unpriced | 2 (1 MLB, 1 truncated NHL) |
| Originated markets | 17 (3 per NHL game, 1 per NBA game) |
| Originated outcome prices | 34 |
| Graded picks | 3 — 2 High, 1 Medium |
| Written predictions | 3, 78–96 words each |
| OLBG match markets recorded | 82 across 11 sports |
| OLBG outright markets recorded | 13 |
| Sources read | 29 (22 official, 4 official-and-unusable, 16 discovery) |
| Flags published | 22 |
| Repo audit findings | 10 (3 high) |
| Validator checks | 945, 0 errors |
| Unit tests added | 8, all passing |

## Sources, by role

Official and usable: `api-web.nhle.com/v1/schedule/2026-10-25`,
`api-web.nhle.com/v1/scoreboard/2026-10-25`, `www.nhl.com/standings/2026-10-24/wildcard`,
`statsapi.mlb.com` schedule for 25 October and for the 25 Oct – 8 Nov window,
`www.nba.com/schedule?date=10/25/2026`, `www.nba.com/standings`, `www.nba.com/games`,
`www.formula1.com/en/racing/2026`, `www.formula1.com/en/results/2026/drivers`.

Official, fetched, returned nothing usable: `www.pdc.tv/tournaments/machineseeker-european-championship`
(consent wall), `www.premrugby.com/fixtures-results` and `www.premiershiprugby.com/league-table`
(client-rendered / 404), `www.icc-cricket.com/fixtures-results` (placeholder text only).

Discovery only, sixteen OLBG hub pages, listed in full on `sources.html`.

## The method, in one paragraph

NHL: goals for and against per game, shrunk toward the league mean with a ten-game prior. The
league mean is not assumed — it is 3.1506 goals per team per game, computed from the goals-for
column and the 352 team-games in the official 24 October standings. Attack against defence gives
expected goals, 0.18 goals of home advantage split evenly, and a normal approximation
(sigma 1.85 margin, 2.40 total) gives win, puck-line and total probabilities. NBA: record shrunk
to .500 with a twenty-game prior, log-5, plus a home-court logit shift.

## The decisions worth arguing about

1. **The band, resolved.** The brief asks for High picks between −250 and +10000 and says the
   >70% market favourites are not wanted. Read as a conjunction those instructions leave a
   1.4-point window (−250 to −233). The band is applied as the hard rule with a 60% floor for
   High and 55% for Medium inside it. The band's own ceiling of −250 (71.4% implied) already
   excludes the trivial favourite, so no second, contradictory filter is needed.

2. **No NBA pick, on purpose.** Five NBA games carry our own money-line prices. Not one of them
   carries a pick. Three games into a season the only official input is a win-loss record, so the
   price lands within a few points of a league-average home-court number every time. Recommending
   the Utah Jazz over a 2-0 Lakers side on that evidence would be a coin toss dressed as analysis.
   The prices are published, the picks are withheld, and F06 says so.

3. **No spread and no NBA total.** No official per-game scoring, pace or rating figure was
   captured, so either number would have been invented.

4. **No player named, no injury claimed.** No injury report, lineup or player page was read for any
   fixture. F08 and F09 record the blank. This is the one place the desk knowingly falls short of
   the brief's request for player and injury detail, and it falls short rather than guesses.

5. **Tip shares are not probabilities.** Every OLBG tip share is reproduced as
   "votes for / votes in market (percentage)" and is used for nothing.

## Verification performed

* Every published record, goal total, streak and split is quoted from
  `www.nhl.com/standings/2026-10-24/wildcard` or `www.nba.com/standings`, with the source linked
  on the same row and the exact read time on `sources.html`.
* Every fixture id, venue and start time is from the official league feed, not from OLBG.
* `scripts/sa394f91e_validate.py` runs 945 checks: 25 pages, one `h1` each, zero broken local
  links, no placeholder tokens, the band and grade rule on every pick, 30-word floor, six-word
  overlap between predictions, banned internal vocabulary, official-only provenance hosts, exact
  UTC read times on every source, and byte-identical rebuild.
* `python -m pipeline.validate --site .` → 0 errors.
* `python -m unittest discover -s tests/pipeline` → 749 tests, OK (757 with the 8 added here).
* `python -m pipeline.build --out _site` → 25 pages plus the desk's 25 at `_site/a394f91e/`,
  0 broken links in the artifact.

## Irregularities

Published in full on `flagged.html` (22 items) and `audit.html` (10 repo findings). The three repo
findings rated high:

* 78 eight-hex desk directories are committed but only 22 are registered in `pipeline/build.py`'s
  ARCHIVE list.
* `data/current/snapshot.json` reports `captured_listings: 108` against `current_listings: 0`,
  `priced_matches: 0` and `originated_markets: 0` — the canonical pipeline resolves none of what
  it captures.
* The repository tracks 3,340 files and 148 MB, of which 2,061 are HTML.

No irregularity blocks publication. Every one is a blank that says why it is blank.
