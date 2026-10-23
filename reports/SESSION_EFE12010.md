# Session efe12010-olbg1 — TEFE12 / §67 report

**Task.** Reverse-engineer OLBG.com for fifteen named sports, originate our own lines for every
market available, pick a winner for each fixture with a low/medium/high label, write unique
≥30-word predictions for the high-confidence selections inside the −250 / +10000 band, confirm
every published fact against an official source, flag everything that could not be confirmed, and
ship it as a GitHub Pages dashboard.

**Branch:** `arena/efe12010-olbg1` · **Harvest stamp:** `2026-10-23T16:26:40Z` ·
**Build stamp:** `2026-10-23T17:05:00Z`

**Scope claimed (and not exceeded):** `efe12010/**`, `data/efe12010/**`,
`scripts/sefe12010_*.py`, `tests/pipeline/test_desk_efe12010.py`, `reports/SESSION_EFE12010.md`,
and append-only edits to `COORDINATION.md` (§1 row TEFE12, §67). No root page, no shared asset and
no other session's desk was touched.

---

## 1. Headline numbers

| Measure | Value |
|---|---|
| Sports in scope | 15 (all covered by a page) |
| Fixtures discovered on OLBG | 100 across 15 hubs (106 raw cards) |
| Fixtures confirmed on an official source | 26 (19 fully, 7 fixture-only) |
| Fixtures priced by this desk | 19 |
| Markets originated | 78 |
| Individual priced outcomes | 180 |
| High-confidence selections (in band) | 13 |
| Medium selections | 6 |
| Written calls (≥30 words, unique) | 19 — one per priced fixture |
| Fixtures published blank and flagged | 74 |
| Fixture-level flags raised | 94 |
| Markets deliberately left blank | 22 |
| Official sources read | 16 |
| Official sources attempted and refused | 10 |
| Published pages | 28 (13 desk + 15 sport) |
| Regression tests added | 20, all passing |

## 2. What was built

| Artefact | Path |
|---|---|
| Official inputs + OLBG harvest, as literals with read stamps | `scripts/sefe12010_data.py` |
| Odds maths, bands, distributions | `scripts/sefe12010_engine.py` |
| Fixtures and originated markets per sport | `scripts/sefe12010_lines.py` |
| Hand-written call copy, one entry per priced fixture | `scripts/sefe12010_predictions.py` |
| Site renderer and exports | `scripts/sefe12010_build.py` |
| Published desk | `efe12010/` (own `assets/style.css`, `assets/app.js`) |
| Machine-readable exports | `data/efe12010/{fixtures,predictions,flags,sources,olbg_harvest}.json`, `{matches,markets}.csv` |
| Regression gate | `tests/pipeline/test_desk_efe12010.py` |

Pages: `index`, `executive-summary`, `high-confidence`, `predictions`, `matches`, `markets`,
`sports`, `coverage`, `sources`, `flagged`, `analysis`, `reverse-engineering`, `methodology`,
plus `sports/<slug>.html` for all fifteen sports.

## 3. Two-layer evidence model

**Discovery layer — OLBG.** 106 cards harvested from the fifteen sport hubs, with the rendered
clock, the tip counts, the market and the crowd consensus. OLBG tells the desk an event exists; it
is never allowed to establish a fact. A test asserts no fixture cites an `olbg.com` URL as evidence.

**Confirmation layer — governing bodies.** Seven of the fifteen sports were re-sourced:

| Sport | Official source | What it established |
|---|---|---|
| Ice hockey | `api-web.nhle.com` schedule + NHL stats team summary | 6 games, start times, venues, 12 team records with goals for/against |
| Baseball | `statsapi.mlb.com` schedule + standings | 3 World Series games, both full-season records |
| Basketball | `api-live.euroleague.net` schedules + standings | 3 Round 7 games, all 20 standings rows |
| Tennis | `atptour.com` daily schedules + singles rankings | 5 pre-match cards, 8 players' ranking points |
| Snooker | `wst.tv` tournament draw | 3 pre-match matches with earlier-round frame scores |
| Motor racing | `formula1.com` event page, drivers' standings, race results | Session times, 8 drivers' points, last 5 race winners |
| Cricket | `cricket.com.au` matches index | 5 fixtures with venues and UTC starts |

Eight sports plus NBA basketball could not be confirmed and ship blank: darts, rugby union,
rugby league, handball, volleyball, golf, Gaelic sports, greyhounds.

## 4. The timezone finding

OLBG prints every event clock with **no timezone marker** and renders it in the reader's own zone,
which resolved to Eastern Daylight Time for this session. Three independent cross-checks settled it:

1. Towcester greyhound race shown as "Today 12:12" and already expired — 17:12 BST = 16:12 UTC.
2. World Series Game 1 shown as "Today 20:00" against the MLB Stats API's `2026-10-24T00:00:00Z`.
3. Fils v Michelsen shown as "Today 12:30" against the ATP's "Not Before 18:30" Brussels time.

All three give **UTC−4**. Two official sites were then found to geo-render the same way:
**wst.tv** and **cricket.com.au**. That resolved an apparent conflict between the OLBG snooker clock
and the World Snooker Tour draw — both read Eastern, both mean `18:00Z`, and the Belfast
quarter-finals are the 19:00 BST evening session. This single conversion affects every start time
on the desk.

## 5. Pricing

Fair price = 1/p with no margin; quoted price adds 4.5% (two-way), 6.0% (three-way) or 8.0%
(outright). The desk leads with the fair price everywhere because that is the number the
−250 / +10000 band is measured against.

| Market family | Method | Official input |
|---|---|---|
| NHL winner | shrunk win rate `(W+3)/(GP+6)`, log5, +3.0pp home ice | NHL team summary |
| NHL totals / puck line / team totals / both-teams-2+ | Poisson `λ = (own GF/g + opp GA/g)/2`, Skellam for the difference | NHL team summary |
| MLB money line | 50/50 actual W% and Pythagorean (exp 1.83), log5, +3.5pp home | MLB standings |
| MLB run line, total | Poisson run counts | MLB standings |
| EuroLeague winner, handicap | point differential/game, +2.5 home court, normal σ = 11.0 | EuroLeague standings |
| EuroLeague total | symmetric PF/PA blend, normal σ = 16.0 | EuroLeague standings |
| ATP winner | `p = RP_a^0.70 / (RP_a^0.70 + RP_b^0.70)` | ATP singles rankings |
| ATP set betting, set handicap, total sets | per-set probability inverted from the match price | ATP singles rankings |
| Snooker winner, frame handicap, frame total | frame rate `(fw+5)/(fw+fl+10)`, log5, negative-binomial race to six | WST draw |
| F1 win / podium / points | 0.5 × points share + 0.5 × last-five-wins share, Harville expansion | F1 standings + results |

**Confidence policy.** Band = fair American in `[−250, +10000]`, i.e. `0.99% ≤ p ≤ 71.43%`.
High-A `p ≥ 70%`; High-B `62% ≤ p < 70%`; Medium `50% ≤ p < 62%` **or** price-capped `p > 71.43%`;
Low below that; Unrated where two officially sourced inputs do not exist.

Three fixtures produced a favourite shorter than −250 and were therefore held at Medium with the
published selection moved to an in-band derivative — New Jersey v Los Angeles, Paris v Valencia, and
Williams v Gilbert. A test asserts a price-capped favourite is never published as a High.

## 6. The thirteen high-confidence selections

| # | Sport | Fixture | Start (UTC) | Selection | Fair | Chance |
|---|---|---|---|---|---|---|
| 1 | Ice Hockey | Anaheim @ Philadelphia | 2026-10-24 17:00Z | Under 6.5 goals | −247 | 71.2% |
| 2 | Motor Racing | United States Grand Prix | 2026-10-25 20:00Z | Max Verstappen — podium | −246 | 71.1% |
| 3 | Ice Hockey | Los Angeles @ New Jersey | 2026-10-24 19:30Z | Under 7.5 goals | −241 | 70.7% |
| 4 | Ice Hockey | Montreal @ Chicago | 2026-10-24 00:00Z | Both teams 2+ goals — Yes | −238 | 70.4% |
| 5 | Tennis | Cobolli v Nakashima (Lyon QF) | 2026-10-23 17:00Z | Nakashima +1.5 sets | −231 | 69.8% |
| 6 | Ice Hockey | NY Rangers @ Ottawa | 2026-10-24 23:00Z | Under 6.5 goals | −230 | 69.7% |
| 7 | Basketball | Zalgiris v ASVEL (EuroLeague R7) | 2026-10-23 17:00Z | Zalgiris Kaunas | −224 | 69.2% |
| 8 | Snooker | Jak Jones v Donaldson (NI Open QF) | 2026-10-23 18:00Z | Scott Donaldson | −189 | 65.4% |
| 9 | Tennis | Fils v Michelsen (Brussels QF) | 2026-10-23 16:30Z | Arthur Fils | −186 | 65.0% |
| 10 | Ice Hockey | San Jose @ Boston | 2026-10-24 23:00Z | Boston Bruins | −185 | 65.0% |
| 11 | Baseball | Tampa Bay @ Milwaukee, WS Game 1 | 2026-10-24 00:00Z | Rays +1.5 | −185 | 64.9% |
| 12 | Baseball | Tampa Bay @ Milwaukee, WS Game 2 | 2026-10-25 00:00Z | Rays +1.5 | −185 | 64.9% |
| 13 | Ice Hockey | Tampa Bay @ Colorado | 2026-10-24 01:00Z | Tampa Bay Lightning | −175 | 63.7% |

Against the five-a-day target: ice hockey 6/5 (met), baseball 2/5, tennis 2/5, basketball 1/5,
snooker 1/5, motor racing 1/5, and nine sports with none. Every shortfall is itemised on
`efe12010/coverage.html` with the source that failed.

## 7. Flagged for review

94 fixture-level flags, 22 deliberately blank markets and 10 refused sources, all on
`efe12010/flagged.html`. The substantive ones:

* **Colorado Avalanche goals for/against** were not returned in the chunk of the official NHL team
  summary that was read, so that game's total, puck line and team totals are blank. The money line
  is still priced from the points column.
* **Jan-Lennard Struff and Nikoloz Basilashvili** sit outside the portion of the official ATP
  rankings that was read, so their two matches carry no price at all.
* **Almaty's Day 8 order of play** is not published, so Basilashvili v Tsitsipas has no official
  start time. The OLBG-derived instant is not published as fact.
* **Jak Jones's second-round frame line** is absent from the WST draw page, so his frame prior
  carries more weight than his opponent's. Disclosed on the fixture rather than back-filled.
* **All five cricket fixtures** are confirmed in full but carry no market: Cricket Australia's
  matches index publishes no ladder, squad or form data.
* **No official feed read for this desk publishes an injury list**, so every written call says so
  explicitly instead of reaching for a secondary report.
* **Elapsed events.** Twelve OLBG cards were already in play or complete at harvest time — five ATP
  matches and two snooker quarter-finals among them. None is published as a pick.

### OLBG's own irregularities (reverse-engineering findings)

1. Clocks render in the viewer's zone with no label anywhere in the markup.
2. The golf hub answers `No tips found.` under a normal 200, so status-code monitoring records a
   healthy scrape of an empty sport.
3. Rugby league returned three ante-post outrights and zero match cards — indistinguishable from a
   broken selector without parsing the card type.
4. The T20 Blast 2027 outright (event 188350) renders `0/0` tipsters with an empty percentage while
   still reporting a non-zero tip count — a divide-by-zero waiting to happen.
5. Expired cards stay listed on the hub alongside live ones.

## 8. Disagreement with the crowd

OLBG's motor racing hub makes Verstappen the most-tipped driver for Austin (13 of 38 tips). This
desk makes **Antonelli** the narrow favourite at 30.1% to Verstappen's 26.6%, because Antonelli
leads the championship 340–221 while Verstappen leads on recent wins. The two inputs cancel almost
exactly. Rather than resolve a disagreement the evidence cannot settle, the published motor racing
call is a **Verstappen podium** at −246, which is in band and does not depend on who wins.

## 9. Gates run

```
python3 -m unittest tests.pipeline.test_desk_efe12010 -v      20 tests, OK
python3 -m unittest discover -s tests/pipeline -v             165 tests, OK
python3 -m unittest discover -s tests -p 'test*.py' -v        38 tests, OK
python3 -m pipeline.build --out _site                         86 canonical pages
python3 -m pipeline.validate --site _site                     0 errors
python3 -m pipeline.validate --site .                         0 errors
python3 scripts/validate.py                                   0 errors, 3 known f7fa77fc warnings
```

`scripts/validate.py` checks relative links across every published HTML page in the repository;
all 28 new pages resolve and every external link is HTTPS. `pipeline.build` picks the desk up
automatically and adds `efe12010/index.html` to the canonical `archive.html` index, so no shared
navigation file had to be edited.

## 10. Honest limits

* Scoring inputs for the World Series are full-season team rates. No probable starter was published
  on the schedule endpoint, so the run line and total are capped at Medium.
* The F1 field is priced eight deep, because the official standings page was read to eighth place.
  Drivers outside the top eight get no price rather than a guessed one.
* Qualifying for Austin had not run at build time, so no grid position informs any F1 price.
* This is a snapshot, not a live feed. Every row carries the UTC instant at which it was read.
