# Session cf2699ba-olbg1 — 23 October 2026 desk

**Task T67.** Fresh 15-sport desk for the sports named in the brief: Golf, Volleyball, Rugby Union,
Cricket, Snooker, Darts, Baseball, Gaelic Sports, Greyhounds, Tennis, Motor Racing, Handball, Ice
Hockey, Basketball, Rugby League.

**Observation window.** 2026-10-23T16:17Z – 2026-10-23T16:40Z. Single snapshot, no automatic refresh.

## What was done

1. Read all 15 in-scope OLBG sport hubs (`https://www.olbg.com/betting-tips/{Slug}/{id}`) and captured
   **135 listings** with event id, competition label, printed time string, top pick, market, tip count
   and tip share (`data/cf2699ba/discovery.json`).
2. Fetched 16 sources (13 distinct hosts) trying to confirm those listings against governing bodies
   (`data/cf2699ba/sources.json`).
3. Confirmed **six fixtures** on official pages: two NHL games, MLB World Series Game 1, and three
   United Rugby Championship Round 4 matches (`data/cf2699ba/fixtures.json`).
4. Originated prices for **16 outcomes across those six fixtures** (money line, run line, game total)
   plus **107 clearly-labelled indicative prices** on discovery-only rows (`data/cf2699ba/lines.json`).
5. Wrote **seven predictions**, 62–77 words each, every clause source-linked
   (`data/cf2699ba/predictions.json`).
6. Published **19 flags** (`data/cf2699ba/flagged.json`) and a 24-page static dashboard in `cf2699ba/`.

## Official sources actually read this session

| ID | Organisation | URL | What it gave |
|---|---|---|---|
| src-nhl-schedule | NHL | `api-web.nhle.com/v1/schedule/2026-10-23` | 2 games, start times, venues, states, six per-provider price sets each |
| src-nhl-standings | NHL | `api-web.nhle.com/v1/standings/2026-10-23` | CAR/EDM/BOS/VGK records only (chunk 0); **none of tonight's clubs** |
| src-mlb-schedule | MLB | `statsapi.mlb.com/api/v1/schedule?...2026-10-23..25` | WS Game 1 and Game 2, pitchers, `ifNecessary=N`, venue |
| src-mlb-standings-al | MLB | `statsapi.mlb.com/api/v1/standings?leagueId=103,104...` | Tampa Bay 98-64, splits, RS/RA |
| src-mlb-standings-nl | MLB | same, `leagueId=104` | **read but unusable** — NL East only in chunk 0 |
| src-mlb-records-capture | MLB (repo capture) | `data/current/evidence/mlb-records-2026.json` | Milwaukee 103-59, RS 832 / RA 618, captured 2026-10-22 |
| src-urc-round4 | United Rugby Championship | `stats.unitedrugby.com/match-centre/2026-27/4` | 3 Friday fixtures with local times and venues; eight Round 3 results |
| src-f1-usgp | Formula 1 | `formula1.com/en/racing/2026/united-states` | US GP session times, COTA 5.513 km / 56 laps / 308.432 km |
| src-wst-matches | World Snooker Tour | `wst.tv/matches/` | Round 1 results only (18–19 Oct) — today's session not reached |
| src-cricket-au | Cricket Australia | `cricket.com.au/matches?...` | filter lists only, no fixtures |
| src-euroleague-gc | Euroleague Basketball | `euroleaguebasketball.net/.../game-center/` | club list only, grid client-rendered |
| src-pdc | PDC | `pdc.tv/tournament/2026-cazoo-european-championship` | consent wall, no content |
| src-munster-gaa | Munster GAA | `munster.gaa.ie/fixtures/` | index/navigation only |
| src-atp-scores | ATP Tour | `atptour.com/en/scores/current` | Brussels/Lyon QFs — different matches from OLBG's rows |
| src-wta-scores | WTA | `wtatennis.com/scores` | notifications only |
| src-olbg-hubs | OLBG | 15 hub pages | discovery only, never a fact source |

## Verification performed

* Every fixture's date, start, venue and status was read on the governing body's own page; nothing was
  copied from OLBG.
* Every fact attached to a prediction carries a source id that `scripts/scf2699ba_validate.py` resolves
  against `sources.json`.
* Tier arithmetic is recomputed from p and the American price on every row, and the validator fails on
  any mismatch.
* All 24 pages were re-walked for broken relative links, `<script>` tags, localhost references and the
  snapshot stamp.
* `scripts/validate.py` (repo historical gate): 0 errors, 3 pre-existing `f7fa77fc` warnings.
* `python -m unittest discover -s tests/pipeline`: 145 tests OK. Preserved suite: 38 OK.
* `python -m pipeline.build --out _site` + `pipeline.validate --site _site`: 85 pages, 0 errors once the
  desk files are tracked (the first run flagged `archive.html → cf2699ba/index.html` as broken only
  because the untracked desk had not been staged into `_site`).

## Headline results

| Metric | Value |
|---|---|
| OLBG listings captured | 135 |
| Fixtures confirmed officially | 6 |
| Priced outcomes from official input | 16 |
| Indicative prices (Low only) | 107 |
| High / Medium / Low | **0 / 1 / 122** |
| Predictions (≥30 words) | 7 |
| Flags | 19 (9 high) |

**High = 0 is the finding.** The brief's rule needs p ≥ 0.70 *and* a price no shorter than −250, which
bounds the eligible band to 70.0 %–71.4 %. The strongest confirmed selection (Edinburgh, ~85 %) prices
near −567 and is therefore a Medium. Nothing was reclassified to hit a target.

## Irregularities (full detail on `/cf2699ba/flagged.html`)

1. **F-CF-01** OLBG prints no timezone and mixes conventions in one capture: a 17:12 Towcester race shown
   as 12:12 (US Eastern), URC matches at 14:45 which the URC also prints as 14:45 local, and an F1 race at
   16:00 which is 16:00 at the circuit. Any fixed offset would be wrong for at least one of the three.
2. **F-CF-02** OLBG shows `20:07` for a game the NHL starts at 20:00 Eastern; every on-the-hour NHL row
   carries `:07` minutes.
3. **F-CF-03** The NHL feed's own odds arrays contradict each other: Montreal 2.35 / 1.60 / 2.03 on three
   providers versus −170 / −170 / −162 on three others, with Chicago 1.59 and +138 simultaneously.
4. **F-CF-04** OLBG lists 15+ NHL games "today"; the league schedules exactly 2.
5. **F-CF-05** The URC page names the same clubs two ways (fixtures "Hollywoodbets Sharks", results
   "Sharks"). A six-entry alias table is published with the code.
6. **F-CF-06 / 07** Golf returned "No tips found"; Rugby League had only 2027 outrights.
7. **F-CF-08 to 13** Access barriers: pdc.tv consent wall; WST capture stops before today; EuroLeague
   client-rendered and the NBA scoreboard endpoint returned HTTP 500; ATP/WTA list different matches;
   Cricket Australia filters only; Munster GAA index only.
8. **F-CF-14** Fresh MLB standings returned NL East in chunk 0, so Milwaukee's record comes from the
   repository's 2026-10-22 canonical capture of the same endpoint.
9. **F-CF-16** No injury, suspension or team-news data was obtainable anywhere.
10. **F-CF-19** 107 indicative prices exist and are not evidence; they are permanently Low.

## Reproduction

```sh
python3 scripts/scf2699ba_data.py        # sports, sources, discovery, fixtures
python3 scripts/scf2699ba_model.py       # originated lines -> data/cf2699ba/lines.json
python3 scripts/scf2699ba_predictions.py # prose + flags
python3 scripts/scf2699ba_site.py        # 24 pages -> cf2699ba/
python3 scripts/scf2699ba_validate.py    # gates, exit non-zero on failure
```

No edits were made to any pre-existing desk, data file, root page, `pipeline/` module or shared
navigation. `COORDINATION.md` is append-only.
