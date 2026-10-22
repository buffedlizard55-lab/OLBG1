# data/40214dfd — desk data for session 40214dfd-olbg1

| Path | What it is |
|---|---|
| `harvest/nhl_2026-10-22.json` | Raw transcription of the 22 Oct NHL slate, records, team leaders and the 21 Oct standings rows actually retrieved. Missing fields are `null`, never inferred. |
| `harvest/mlb_worldseries.json` | World Series games 1–5 from the official bracket plus final regular-season records and run aggregates. |
| `harvest/euroleague_round7.json` | EuroLeague Round 7 fixtures with records, tip-off clocks (CEST) and the scoring averages quoted by the official preview. |
| `harvest/snooker_ni_open.json` | Eight Northern Ireland Open Round 3 pairings. Clocks are stored as displayed, with `start_utc: null`, because WST prints no timezone. |
| `desk.json` | Generated desk: fixtures, markets, priced outcomes, tiers, picks, High selections, near misses, predictions, findings, coverage. |
| `priced.csv` | Every priced outcome (598 rows) with fixture, market, selection, probability, fair price and tier. |
| `matches.csv` | Fixture-level export: one row per fixture with the headline selection and its tier. |

Regenerate with:

```sh
python3 scripts/s40214dfd_data.py      # rebuilds desk.json and both CSVs
python3 scripts/s40214dfd_build.py     # rebuilds 40214dfd/*.html
python3 scripts/s40214dfd_validate.py  # gate: exits non-zero on any inconsistency
```

`scripts/s40214dfd_prose.py` holds the seven hand-written predictions and the near-miss notes. Editing
a prediction re-runs through the validator, which fails if a quoted number cannot be found in a
harvest file.
