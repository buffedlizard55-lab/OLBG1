# Session cf2699ba-olbg1 — T67, fifteen-sport desk, 23 October 2026

Snapshot window **2026-10-23T16:20Z – 16:40Z**. One capture, no automatic refresh.
Deliverable: `cf2699ba/` (24 pages), data in `data/cf2699ba/`, pipeline in `scripts/scf2699ba_*.py`.

## The brief, and what this desk did with it

| Requirement | Outcome |
|---|---|
| Complete updated match list for the fifteen named sports | 134 OLBG listings, all fifteen hubs swept, every row kept and shown |
| Own betting lines across every discoverable market | 133 prices: 16 from official inputs, 117 indicative; 28 markets examined and withheld with a written reason |
| Pick a winner per match | Every priced row carries a selection; withheld rows say why they have none |
| Low / medium / high confidence | 0 High, 1 Medium, 132 Low, graded by a rule the build re-checks |
| Five high-confidence picks per sport per day | **Not achievable today.** Six fixtures confirmed, none priced in the 70.0–71.4% window the rule allows. Documented, not filled |
| Unique human prediction of 30+ words per high pick | 7 write-ups, 58–71 words, each clause tied to a source |
| No "model" or "verified" in published prose | Absent from all 24 pages, checked by the gate |
| Confirm every row against an official source, link it | 9 sources, each with the timestamp it was read and its limits; 6 fixtures confirmed |
| Leave unconfirmable values blank and flag them | 129 discovery-only rows, 21 flags, 28 withheld markets |
| Flag irregularities | 21, with 10 high severity |
| Clean dashboard plus category subpages | Summary, matches, markets, confidence, predictions, analysis, flagged, sources, method, plus 15 sport pages |

## Sources read

| Publisher | Page | Read | What it gave |
|---|---|---|---|
| NHL | `api-web.nhle.com/v1/schedule/2026-10-23` | 16:24Z | Two games, UTC starts, venues, game ids, per-provider quotes |
| NHL | `api-web.nhle.com/v1/standings/2026-10-23` | 16:26Z | Top of the table only; none of tonight's four clubs |
| MLB | `statsapi.mlb.com/.../schedule` | 16:27Z | World Series Game 1 (gamePk 849805) and Game 2, probable pitchers |
| MLB | `statsapi.mlb.com/.../standings?leagueId=103` | 16:29Z | Tampa Bay 98-64, 43-38 away, 736 scored, 650 allowed |
| MLB capture | repository `data/current/evidence/mlb-records-2026.json` | 2026-10-22 | Milwaukee 103-59, 832 scored, 618 allowed |
| URC | `stats.unitedrugby.com/match-centre/2026-27/4` | 16:31Z | Three Friday fixtures with local times and venues, eight Round 3 results |
| Formula 1 | `formula1.com/en/racing/2026/united-states` | 16:33Z | COTA, 5.513 km, 56 laps; practice, qualifying and race times |
| World Snooker Tour | `wst.tv/matches` | 16:35Z | Round 1 results to 19 October; today's ties not reached |
| OLBG | fifteen sport hubs | 16:20–16:36Z | Discovery only: names, competitions, printed times, tip shares |

Blocked or unusable, each recorded as a flag: PDC European Championship (consent wall), EuroLeague game
centre (client-rendered), NBA scoreboard (HTTP 500), ATP and WTA score pages (different matches), Cricket
Australia (filters only), Munster GAA (navigation only), NHL standings (top of table only), MLB National
League standings (American League block returned instead).

## Prices

**From official inputs, 16 rows on 6 fixtures.**

| Fixture | Market | Selection | p | Fair price | Grade |
|---|---|---|---|---|---|
| Montreal at Chicago | Money line | Montreal | 0.600 | −150 | Low |
| Montreal at Chicago | Money line | Chicago | 0.400 | +150 | Low |
| Tampa Bay at Colorado | Money line | Tampa Bay | 0.464 | +115 | Low |
| Tampa Bay at Colorado | Money line | Colorado | 0.536 | −115 | Low |
| Rays at Brewers | Money line | Milwaukee | 0.561 | −128 | Low |
| Rays at Brewers | Money line | Tampa Bay | 0.439 | +128 | Low |
| Rays at Brewers | Run line −1.5 | Milwaukee | 0.406 | +146 | Low |
| Rays at Brewers | Run line +1.5 | Tampa Bay | 0.594 | −146 | Low |
| Rays at Brewers | Total 8.5 | Over | 0.511 | −105 | Low |
| Rays at Brewers | Total 8.5 | Under | 0.489 | +105 | Low |
| Cardiff v Sharks | Money line | Cardiff | 0.536 | −115 | Low |
| Cardiff v Sharks | Money line | Sharks | 0.464 | +115 | Low |
| Connacht v Zebre | Money line | Connacht | 0.585 | −141 | Low |
| Connacht v Zebre | Money line | Zebre | 0.415 | +141 | Low |
| Edinburgh v Lions | Money line | Edinburgh | 0.850 | −567 | Medium |
| Edinburgh v Lions | Money line | Lions | 0.150 | +567 | Low |

Derivations: NHL by two-way de-vig of three mutually consistent provider quotes (the contradictory
decimal quotes are excluded and named); MLB by independent Poisson on season runs with ties removed and a
log5 cross-check at 0.533; URC by shrunk single-round margins (0.25) plus a declared three-point home
prior, normal CDF, capped at 0.85.

**Indicative, 117 rows.** OLBG vote share, halved toward a coin flip, capped at 90%, permanently Low.
Never counted as evidence.

## Why zero High

A 70% chance is about −233; a −250 price is 71.4%. The two halves of the brief's rule therefore overlap
only in a 1.4-point window. The strongest confirmed selection today (Edinburgh, about 85%) is far above
the chance floor and prices at −567, outside the price band. The next best confirmed side is 60.0%.
Publishing a High would have required re-grading, which the desk does not do; the ledger is instead shown
as its own table so the reader can see exactly which rows were excluded and why.

## Flags (21, ten high)

1. **F-CF-01** OLBG has no timezone and mixes conventions in one capture: a 17:12 greyhound race shown as
   12:12 (US Eastern), URC at 14:45 (local), MLB at 20:00 (Eastern), F1 at 16:00 (track local).
2. **F-CF-02** OLBG prints 20:07 for a game the NHL starts at 20:00; every on-the-hour NHL row carries `:07`.
3. **F-CF-03** The NHL feed's own quotes contradict each other about which side is favourite.
4. **F-CF-04** The URC names clubs two ways between its fixture and results blocks.
5. **F-CF-05** The hub carries several NHL fixtures; the league schedules two, only one of which is listed.
6. **F-CF-06/07** Golf returns no tips; Rugby League has 2027 outrights only.
7. **F-CF-08–13** Darts consent wall, snooker list stops before today, EuroLeague client-rendered, NBA
   HTTP 500, tennis pages list different matches, cricket filters only, Gaelic navigation only.
8. **F-CF-14** Milwaukee's record comes from the repository's 2026-10-22 capture.
9. **F-CF-15** NHL standings loaded the top of the table only.
10. **F-CF-16** No availability data anywhere, so no prediction mentions an injury.
11. **F-CF-17** Greyhound race names and displayed times disagree; no GBGB card read.
12. **F-CF-18** 117 indicative prices rest on tip-vote shares, not prices.
13. **F-CF-19** OLBG's Cardiff v Sharks price direction cannot be checked against a league, which publishes none.
14. **F-CF-20** An EHF tie with a +11.50 handicap, unconfirmed.
15. **F-CF-21** The High rule's 70.0–71.4% window, stated as a finding.

## Gates

```
python3 scripts/scf2699ba_data.py        15 sports / 9 sources / 134 rows / 6 fixtures
python3 scripts/scf2699ba_model.py       133 prices (16 official, 117 indicative), 28 withheld
python3 scripts/scf2699ba_predictions.py 7 write-ups (58-71 words), 21 flags
python3 scripts/scf2699ba_site.py        24 pages
python3 scripts/scf2699ba_validate.py    1,644 assertions -> VALIDATION PASSED (0 errors)
python3 scripts/validate.py              Errors 0, Warnings 3 (pre-existing f7fa77fc rows)
python3 -m unittest discover -s tests/pipeline   145 tests OK
python3 -m pipeline.build --out _site            includes _site/cf2699ba/
```

## Scope discipline

No pre-existing desk, data file, root page, shared navigation or `pipeline/` module was edited.
`COORDINATION.md` is append-only (71 added lines, 0 deleted). The desk is reachable at `/cf2699ba/` and is
auto-listed on `archive.html` by the canonical build; its auto-label ("additional historical namespace;
not recertified") is wrong for a current desk and is logged as a request for the integration session
rather than patched here.
