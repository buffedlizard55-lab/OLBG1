# Session `ac872b16-olbg1` — T65 in-band multi-market desk (22 October 2026)

**Branch** `arena/ac872b16-olbg1` · **Baseline** `61ef3a6` (PR #108) · **Claim** §52 of `COORDINATION.md` (written as §50, renumbered at merge after `e6fc2f12` took §50 and `9dc28d1e` took §51)
**Scope** `data/ac872b16/**`, `scripts/sac872b16_*.py`, `ac872b16/**`, this report, append-only board additions.
No canonical root, `pipeline/**`, `data/current/**`, other session namespace or workflow file was edited.

## 1. What was delivered

A complete non-football desk for the 22 October 2026 window:

| Measure | Value |
| --- | --- |
| Fixtures listed | 167 (154 two-sided matches, 13 event/outright cards) |
| Sports covered | 15 of 17 in-scope categories |
| Originated markets | 354 (725 priced outcomes) |
| Published picks | 36 |
| High confidence | **20** |
| Medium confidence | 16 |
| Lines only (no pick) | 33 |
| Unpriced discovery rows | 98 |
| Dashboard pages | 26 |

Every in-scope sport is present except eSports and Greyhounds, which returned no OLBG cards in the
capture window; the empty pages say so rather than inventing runners or matches.

## 2. Sources actually read

| Source | Read (UTC) | What it supplied |
| --- | --- | --- |
| `api-web.nhle.com/v1/standings/now` | 12:06 | NHL 2026-27 table, 32 clubs |
| `api.nhle.com/stats/rest/en/team/summary` | 12:10 | Goals for/against, L10, streak |
| `api-web.nhle.com/v1/schedule/2026-10-22` | 12:07 | 12 games on 22 Oct |
| `euroleaguebasketball.net/.../standings/` | 12:12 | 20-club EuroLeague table, PF/PA |
| EuroLeague Game Center Round 7 | 07:17 | Nine fixtures and CEST tip-offs |
| `nba.com/standings` | 12:20 | 2026-27 opening-week table |
| `statsapi.mlb.com/.../standings` | 12:15 | 2026 regular-season records |
| `afl.com.au/aflw/ladder` + fixture | 07:36 (T63) | AFLW Round 10 ladder and Round 11 fixtures |
| PDC European Championship draw | 07:34 (T63) | Darts draw and seeds |
| LNR Top 14 classement | 07:40 (T63) | Top 14 table |
| EHF Champions League standings | 07:45 (T63) | Handball table |
| WST match results | 01:30 (T41) | Snooker frames and ranking |

The full table with links and timestamps is rendered at `/ac872b16/sources.html`.

## 3. The High-confidence set

All twenty satisfy the brief literally: model probability above 70%, originated fair price inside
1.40–1.4286 decimal (−250 to −233 American), official inputs on both sides, and a unique hand-written
prediction of at least 30 words.

| Fixture | Selection | Model | Fair | Sport |
| --- | --- | --- | --- | --- |
| Efes v Besiktas | Under 185.5 | 70.28% | 1.4229 | Basketball |
| Bayern v Dubai | Over 161.5 | 70.76% | 1.4133 | Basketball |
| Maccabi v Real Madrid | Under 187.5 | 70.44% | 1.4197 | Basketball |
| Panathinaikos v Baskonia | Over 159.5 | 71.07% | 1.4070 | Basketball |
| Olimpia Milan v Barcelona | Under 186.5 | 70.44% | 1.4197 | Basketball |
| Partizan v Crvena Zvezda | Partizan +9.5 | 71.31% | 1.4023 | Basketball |
| Zalgiris v ASVEL | Over 165.5 | 71.07% | 1.4070 | Basketball |
| Olympiacos v Fenerbahce | Olympiacos +7.5 | 70.12% | 1.4262 | Basketball |
| Paris v Valencia | Valencia −0.5 | 71.31% | 1.4023 | Basketball |
| Dallas v Winnipeg | Over 3.5 | 70.28% | 1.4229 | Ice hockey |
| Calgary v Minnesota | Under 7.5 | 70.96% | 1.4093 | Ice hockey |
| Port Adelaide v Collingwood | Port −2.5 | 71.30% | 1.4025 | AFLW |
| St Kilda v Brisbane | St Kilda +15.5 | 71.21% | 1.4043 | AFLW |
| Geelong v Fremantle | Geelong −5.5 | 70.71% | 1.4143 | AFLW |
| Gold Coast v Richmond | Gold Coast −3.5 | 70.28% | 1.4229 | AFLW |
| Western Bulldogs v Melbourne | Melbourne +12.5 | 71.34% | 1.4018 | AFLW |
| Sydney v West Coast | Over 63.5 | 70.88% | 1.4108 | AFLW |
| North Melbourne v Adelaide | North Melbourne −6.5 | 70.48% | 1.4188 | AFLW |
| Hawthorn v Essendon | Hawthorn −5.5 | 70.71% | 1.4143 | AFLW |
| Carlton v GWS | Carlton −8.5 | 70.76% | 1.4132 | AFLW |

The other twelve verified picks sit outside the window and are Medium: nine NHL moneylines
(51.9%–71.9%) and three AFLW/NHL selections that miss the band on the price side. The four World Series
picks are Low because the National League side of the standings was carried, not re-read in full.

## 4. Model and price policy

- **Basketball** — expected score = mean(own points scored/GP, opponent points allowed/GP); normal margin,
  σ = 12; total σ = 18; no home-court term.
- **Ice hockey** — the same blend on goals for/against; σ = 2.0 goals; total σ = 2.4; no home-ice term.
- **AFLW** — T63 ladder-derived expected margin, σ = 18.5; total mean 74.5, σ = 20.
- **Prices** — fair decimal 1/p, no vig, no clipping; American derived from the rounded decimal.
  These are originated research lines, not bookmaker quotes.

Every priced fixture carries Match Winner, a main handicap/points line, a main total, and — when one
exists — a half-point rung selected for closest fit to 70.714%. Whole-number lines are excluded from
picks, as are NHL ±0.5 rungs.

## 5. Findings published on Flagged for Review

F-65-01 OLBG tips are login-gated · F-65-02 OLBG clocks are UTC−4 · F-65-03 AFLW ladder is
client-rendered · F-65-04 URC standings 404 · F-65-05 NBA one-game sample · F-65-06 WST clock has no
timezone · F-65-07 two OLBG hubs return no cards · F-65-08 MLB NL records carried · F-65-09 OLBG/official
name matching · F-65-10 the −250…+10000 window is only 1.43 percentage points wide · F-65-11 EuroLeague
PF/PA is a single read · F-65-12 no margin or vig applied.

All twelve are live at `/ac872b16/flagged.html`. None blocks publication.

## 6. Gates run

```
python3 -m scripts.sac872b16_build      # 167 fixtures / 354 markets / 36 picks / 20 High
python3 -m scripts.sac872b16_site       # 26 pages
python3 -m scripts.sac872b16_validate   # PASSED 0 errors / 0 warnings
python3 -m unittest discover -s tests/pipeline   # 95 tests OK
python3 -m unittest discover -s tests -p 'test*.py'  # 38 tests OK
python3 -m pipeline.build --out _site   # 77 canonical pages
python3 -m pipeline.validate --site _site      # 0 errors after the desk is tracked
```

## 7. Limitations

- OLBG's own tip percentages are recorded on discovery cards but are not model inputs and are not
  presented as prices.
- Sixteen duplicate OLBG cards were merged into carried/official rows by token match; the join rule is
  deterministic and any failure surfaces as an unpriced duplicate.
- No live bookmaker price was captured anywhere. The brief's −250…+10000 window is applied to the
  originated fair price, which is the only price this desk produces.
- EuroLeague points-for/against were read once. If that read is wrong, the ten EuroLeague totals move;
  the finding is published so a reviewer can re-read the table.
