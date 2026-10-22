# Session 9dc28d1e — v2 desk, 22 October 2026

**What this is.** A second, independent build of the `9dc28d1e` desk, produced after PR #114/#120 were
merged. It replaces the earlier dashboard in the same namespace with one built from a re-read of the
official feeds, a recalibrated EuroLeague model, four High-confidence picks instead of three, and a gate
analysis that states plainly what the brief's odds window does to the selection.

## Counts

| Quantity | Value |
| --- | --- |
| Fixtures listed | 107 |
| Priced fixtures | 23 (12 NHL, 9 EuroLeague, 2 World Series) |
| Originated markets | 405 |
| Priced selections | 682 |
| High / Medium / Low | 4 / 206 / 472 |
| Above 70% but outside the price window | 162 |
| Written predictions | 4 |
| Flagged findings | 10 |
| Pages | 26 (9 desk pages + 17 category pages) |

## The gate, and why it matters more than the picks

The brief asks for picks with **more than 70%** probability **and** odds **between −250 and +10000**.
Those conditions are nearly disjoint:

* more than 70% implies a fair American price shorter than **−233.33**;
* the −250 floor allows no price shorter than −250, i.e. no probability above **71.43%**;
* the intersection is **70.00% < p ≤ 71.43%** — 1.43 percentage points wide;
* +10000 corresponds to 0.99%, which no two-way match market can reach.

Applied literally to 682 priced selections, 167 clear 70%, five sit inside the window, four carry the
player-level evidence the brief also requires. The strongest line on the slate — Panathinaikos at home to
Baskonia, 81.8%, fair −451 — is excluded by the floor. That is flagged as F-9DC-01/F-9DC-03 rather than
quietly relabelled.

## High-confidence picks

| Fixture | Selection | Probability | Fair price | Sensitivity |
| --- | --- | --- | --- | --- |
| Boston Bruins v Nashville Predators | Nashville over 1.5 goals | 71.1% | −246 | 65.5–75.7% |
| New Jersey Devils v Anaheim Ducks | Under 7.5 goals | 70.0% | −234 | 65.0–74.0% |
| Seattle Kraken v Utah Mammoth | Utah +1.5 | 70.5% | −239 | 67.0–75.0% |
| Ottawa Senators v San Jose Sharks | San Jose over 1.5 goals | 70.4% | −238 | 64.7–75.2% |

Each has a written case naming at least one player whose season totals were read from the NHL stats feed
during this session (Stamkos/Forsberg/Josi, Hughes/Bratt/Hischier and Carlsson/Sennecke/Granlund,
Schmaltz/Keller/Sergachev, Celebrini/Smith/Stenberg).

## Sources (all read 22 October 2026, 12:05Z–12:26Z)

| Feed | URL | Used for |
| --- | --- | --- |
| NHL team summary | `api.nhle.com/stats/rest/en/team/summary?cayenneExp=seasonId=20262027 and gameTypeId=2` | all 32 clubs' GP/W/L/OTL/points/GF/GA |
| NHL schedule | `api-web.nhle.com/v1/schedule/2026-10-22` | 12 games, home designation, start times, 5 venues |
| NHL skater summary | `api.nhle.com/stats/rest/en/skater/summary?...teamAbbrevs="NSH"` (also UTA, SJS, NJD, ANA) | player facts in the four predictions |
| EuroLeague standings | `api-live.euroleague.net/v1/standings?seasonCode=E2026` | all 20 clubs' W/L/PF/PA |
| MLB schedule | `statsapi.mlb.com/api/v1/schedule?...startDate=2026-10-23&endDate=2026-10-30&hydrate=probablePitcher` | six World Series games, venues, the Game 1 starter |
| MLB standings | `statsapi.mlb.com/api/v1/standings?leagueId=104&divisionId=205&season=2026` | Brewers 103-59, 832/618 |

Integrity checks run on import: every NHL row satisfies `GP = W+L+OTL` and `P = 2W+OTL`, and league-wide
goals for equal goals against exactly (942 = 942). EuroLeague points for and against agree to within nine
points across clubs with unequal games played.

## Honest weaknesses

* **No game-level recent results.** The club schedule feeds return a full season (24 chunks) and were not
  read. Form is season-to-date, not a list of scorelines (F-9DC-05).
* **One in-band pick has no write-up.** Anadolu Efes v Besiktas over 166.5 (71.2%, −247) is capped at
  Medium because no official EuroLeague player-level source was available (F-9DC-02).
* **Fourteen of seventeen categories are empty.** No verified input was obtained for tennis, snooker, darts,
  golf, cricket, rugby union, rugby league, handball, volleyball, motor racing, esports, Gaelic football,
  greyhounds or Aussie rules. They are published as empty pages rather than filled from memory (F-9DC-06).
* **Calibration is untested.** No fixture had started when the desk was built. Sensitivity ranges are two to
  three times wider than the 1.43-point gate window (F-9DC-09).
* **The EuroLeague model was recalibrated by judgement.** A multiplicative version priced Panathinaikos at
  97.5%; the published version shrinks differentials and applies half the remaining gap, giving 81.8%. The
  0.50 weight is documented as a choice (F-9DC-10).
* **Seven NHL venues are blank** because only five were visible in the read (F-9DC-07).

## Gates

```
python3 scripts/s9dc28d1e_build.py --now 2026-10-22T12:30:00Z
python3 scripts/s9dc28d1e_validate.py
python3 scripts/validate.py
python3 -m pipeline.validate --site .
python3 -m unittest discover -s tests/pipeline -q
```

Expected output of the desk gate:

```
9DC28D1E VALIDATION PASSED: priced=23 outcomes=682 high=4 predictions=4 pages=26 errors=0 warnings=0
```

## Reproduction

The builder is deterministic given `--now`. `data/9dc28d1e/desk.json` is the machine-readable truth:
fixtures, markets, every priced selection with its tier, reason and sensitivity range, the predictions with
their fact tables, and the ten findings. `priced.csv` and `predictions.csv` are flat exports of the same
content for anyone who wants to check the numbers in a spreadsheet.
