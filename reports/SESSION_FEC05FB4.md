# Session fec05fb4 — non-excluded OLBG board, rebuilt from official sources

**Branch** `arena/fec05fb4-olbg1` · **Desk snapshot** 2026-10-22 12:45 UTC · **Pages** `/fec05fb4/`

## What this session produced

| Artefact | Path | Contents |
| --- | --- | --- |
| Desk dataset | `data/fec05fb4/desk.json` | 87 upcoming rows, 62 listing-only rows, 14 flags, 11 sources, 443 markets (900 outcomes) |
| Flat exports | `data/fec05fb4/rows.csv`, `data/fec05fb4/picks.csv` | one line per row / per High prediction |
| Generator | `scripts/sfec05fb4_data.py` | rebuilds every number from the constants and the official figures recorded in the file |
| Site builder | `scripts/sfec05fb4_build.py` | renders 25 HTML pages |
| Validator | `scripts/sfec05fb4_validate.py` | 9,099 assertions: JSON invariants, market arithmetic, High gate, prediction uniqueness, HTML audit |
| Site | `fec05fb4/` | overview, categories index, 17 category pages, High selections, Flagged, line-by-line review, sources, method, coverage |

## Headline numbers

- **87** upcoming fixtures with a verified start time; **66** priced; **21** unpriced because no verified rating exists for both sides.
- **2 High**, **37 Medium**, **27 Low**.
- **26** rows on evidence this session read itself (12 NHL, 9 EuroLeague, 5 MLB); **61** on carried evidence, all capped below High.
- **62** listing-only rows (tennis, snooker, cricket, golf, greyhounds, eSports) carry no verified clock time and are never priced.

## The gate, and why only two Highs

A High must satisfy all five tests:

1. model probability strictly above 70.00% and at most 71.4286%, so the zero-vig fair price is inside −250…+10000;
2. an official source read by **this** session;
3. **both** clubs' availability confirmed in that read;
4. the selection agrees with the model's own view of the match;
5. a unique prediction of at least 30 words naming the selection and its price.

Only Efes–Besiktas and Milan–Barcelona have club-confirmed Round 7 availability reports. The other seven EuroLeague games are in the same numeric band but had no filed report at 12:36Z, so they are Medium with the reason printed on the row and on the match panel.

| High | Selection | Model p | Fair | Words |
| --- | --- | --- | --- | --- |
| el-535918 Anadolu Efes v Besiktas | Besiktas +5.0 | 71.11% | −246 | 81 |
| el-535922 Milan v Barcelona | Under 185.5 | 70.56% | −240 | 88 |

## Official reads performed today

| Source | Read (UTC) | Used for |
| --- | --- | --- |
| `nhl.com/standings/2026-10-21/league` | 12:47 | all 32 clubs: GP, W‑L‑OT, P%, GF/GA, home/away, L10, streak |
| `nhl.com/scores/2026-10-22` | 12:24 | 12 games, EDT times, DraftKings reference moneyline |
| `euroleaguebasketball.net/.../standings/` | 12:30 | all 20 clubs, points scored/allowed per game |
| `euroleaguebasketball.net/.../game-center-round-7-el2627/` | 12:33 | Round 7 pairings, CEST times, form notes |
| `euroleaguebasketball.net/.../injury-report-round-7-fantasy/` | 12:36 | club-by-club availability |
| `statsapi.mlb.com/.../schedule?...2026-10-22...29` | 12:28 | World Series gamePk, UTC starts, venues |
| `statsapi.mlb.com/.../standings?leagueId=103,104` | 12:29 | Rays 98‑64, Yankees 93‑68, Red Sox 87‑75 |
| `statsapi.mlb.com/.../standings?leagueId=104` | 12:51 | Brewers 103‑59, home 55‑26, L10 8‑2, W5 |

Carried (not re-read this session): PDC European Championship draw and schedule (07:44Z), AFLW ladder after Round 10 (07:36Z), WST match centre (07:46Z). PDC re-fetch hit a cookie wall; the AFLW ladder is client-rendered and returned an empty table.

## Findings worth a reviewer's time

1. **The brief's two rules barely overlap.** −250 is exactly 71.4286% at zero vig. Anything above that prices shorter than −250; anything at or below 70% fails the probability test. A 5% bookmaker margin removes the overlap entirely, so the band test uses the fair price and the offered price is published separately (F‑FEC‑01).
2. **EuroLeague's preview contradicts its own table.** Valencia 5‑1 in prose vs 4‑2 in the table; Real Madrid 1‑4 vs 1‑3 away; Olympiacos 98.2 ppg vs 94.0; Valencia 98.3 vs 97.17. The table wins and the conflict is flagged (F‑FEC‑04).
3. **NHL record-only pricing is not trustworthy against a market.** The model disagrees with the de-vigged DraftKings reference by up to 21 points (LAK at NYI), so no NHL row can be High (F‑FEC‑08).
4. **MLB postseason data is empty.** The schedule payload reports 0‑0 for both clubs; the model falls back to final regular-season records and says so (F‑FEC‑09).
5. **Two sports could not be re-read at all** (PDC cookie wall, AFLW JS ladder), so their near-band picks stay Medium (F‑FEC‑02, F‑FEC‑05, F‑FEC‑06).

## Reproduction

```bash
python3 scripts/sfec05fb4_data.py      # rebuild data/fec05fb4/desk.json + CSVs
python3 scripts/sfec05fb4_build.py     # render fec05fb4/ (25 pages)
python3 scripts/sfec05fb4_validate.py  # 9,099 assertions, exit 1 on any failure
```

`scripts/validate.py` and `python -m pipeline.validate --site .` both pass with the new directory present (the three warnings reported by `scripts/validate.py` belong to `f7fa77fc/flagged.html`, not to this session).

## Limits stated on the site

No calibration study, no closing-line comparison, no bookmaker feed, and no claim that a 71% label is a measured strike rate. Carried evidence is capped at Medium. Blank cells mean "not verified", never "assumed".
