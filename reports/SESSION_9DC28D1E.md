# Session 9dc28d1e — fresh evidence desk, 22 October 2026

Task **T9DC** (see `COORDINATION.md` §50). Branch `arena/9dc28d1e-olbg1`, baseline `f255eef`
(merge of PR #109). Everything below was produced in this session; nothing is inherited from an
earlier summary.

## What was asked

Collect and verify upcoming matches for the 17 in-scope sports, originate independent lines for every
covered match across winner / handicap / total markets, pick winners with Low / Medium / High
confidence, and write unique ≥30-word human predictions for the High tier, with High restricted to
selections above 70% confidence whose odds sit between −250 and +10000.

## What was delivered

| Item | Result |
|---|---|
| Fixtures in the desk | **108** — exactly the canonical count, fully reconciled |
| Re-read from official sources this session | **25** matches: 12 NHL, 9 EuroLeague, 4 MLB World Series |
| Originated markets | **391** |
| Priced outcomes | **782** |
| High confidence | **3** |
| In band but capped at Medium (no player-level source) | **8** |
| Over 70% but priced outside the brief's window | **169** |
| Written predictions | **3**, all ≥30 words, unique, player + form + selection |
| Findings published | **10** |
| Pages | **25** (dashboard, 6 analysis pages, 17 category pages) |

## Verification performed

Every rating input, fixture and start time in the priced set was read from the league's own feed
during 12:04Z–12:25Z on 22 October 2026:

* `api-web.nhle.com/v1/schedule/2026-10-22` — 12 games, away/home, `startTimeUTC`, venue, `gameState=FUT`
* `api.nhle.com/stats/rest/en/team/summary` — all 32 clubs, GP/W/L/OTL/GF/GA, identity GP = W+L+OTL asserted
* `api-live.euroleague.net/v1/standings?seasonCode=E2026` — all 20 clubs, W/L/PF/PA
* `statsapi.mlb.com` schedule + standings projections — World Series dates, UTC starts, records, probable pitcher
* `api-web.nhle.com/v1/club-stats/{NSH,SJS,MIN}` — the player-level facts used in the three predictions

The canonical snapshot's 108 fixture ids reconcile exactly with this desk's 108 rows (25 priced +
83 inherited). No id was invented, dropped or renamed.

## The central finding

The brief's High gate is self-limiting. A probability above 70% cannot price longer than −233.33
American, and the brief also forbids prices shorter than −250. The intersection is
**(70.00%, 71.43%]** — 1.43 percentage points wide. Applying it literally to 782 priced outcomes
leaves 3 High selections. Widening the interpretation would have produced dozens of "High" picks
that are simply heavy favourites outside the requested odds band. That choice is documented, not
hidden: 169 selections above 70% are published with the *outside window* label and their prices.

## Why three, and why NHL

The three High picks are NHL team totals. They are the only selections that satisfy all three
conditions:

1. model probability > 70%,
2. fair American inside [−250, +10000],
3. a prediction supported by verified player-level facts.

Eight EuroLeague selections satisfy (1) and (2) — as near as −249.8 — but the official EuroLeague
machine-readable source publishes standings only. No roster, minutes or availability data could be
verified, so those rows are capped at Medium and listed on the Flagged for Review page with their
prices. Manufacturing a player name to satisfy the template would have been worse than capping them.

## Honest weaknesses

* **All three Highs are fragile.** Re-running the model at shrinkage of 8/12/16 games and a home edge
  of 0.05/0.10/0.15 goals moves each probability across the 70% line (ranges 66.5%–73.7%). The desk
  publishes this per pick rather than hiding it.
* **No calibration.** There is no backtest against settled results, so these are model estimates,
  never measured frequencies.
* **Three sports priced, fourteen listed.** Darts, greyhounds, golf, eSports and motor racing
  produced no usable official draw today; tennis, snooker, handball, cricket, rugby, AFLW, GAA and
  volleyball were not re-read and carry no prices.
* **Overtime split 50/50** for NHL moneylines — an assumption, quantified in F-9DC-07.
* **MLB has one market per game.** Run line and totals were withheld because the 2026 league run
  environment was not verified (F-9DC-05).

## Gates

```
python3 scripts/s9dc28d1e_validate.py          # PASSED, 0 errors
python3 -m unittest discover -s tests/pipeline # 95 tests OK
python3 -m unittest discover -s tests -p 'test*.py'  # preserved suite OK
python3 scripts/validate.py                    # PASSED (3 pre-existing mirror warnings)
python3 -m pipeline.validate --site .          # 0 errors
```

## Reproduction

```
python3 scripts/s9dc28d1e_build.py --now 2026-10-22T12:30:00Z
python3 scripts/s9dc28d1e_validate.py
```

Outputs: `data/9dc28d1e/desk.json`, `data/9dc28d1e/priced.csv`,
`data/9dc28d1e/predictions.csv`, `9dc28d1e/**/*.html`.
