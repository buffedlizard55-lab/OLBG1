# Session `4c4968fc` — OLBG fifteen-sport research desk (captured 2026-10-23 21:30 UTC)

**Live desk:** [`../4c4968fc/index.html`](../4c4968fc/index.html)
**Data:** [`../data/4c4968fc/summary.json`](../data/4c4968fc/summary.json) — fixtures.json · markets.json · picks.json · predictions.json · flagged.json · elapsed.json · sources.json · summary.json · matches.csv · markets.csv · predictions.csv
**Gate:** `python3 scripts/s4c4968fc_validate.py` (0 failures) · `python3 -m pipeline.validate --site .` (0 errors) · `tests/pipeline/test_desk_4c4968fc.py` (17 tests)

## Scope

Exactly the fifteen sports named in the brief: Golf, Volleyball, Rugby Union, Cricket, Snooker, Darts,
Baseball, Gaelic Sports, Greyhounds, Tennis, Motor Racing, Handball, Ice Hockey, Basketball, Rugby League.
Soccer/football, American football, boxing, UFC/MMA, hurling, cycling, horse racing and specials are excluded.

## What was built

1. **OLBG reverse-engineering.** The fifteen sport hubs were mapped (`/betting-tips/<Slug>/<id>`, case-sensitive
   slugs). Both hubs read this session returned "No tips found", so OLBG supplied the taxonomy only and fixture
   enumeration ran off the official competition calendars. That is stated on the desk rather than dressed up.
2. **Official-source reading.** 34 pages, 32 of them official governing-body, league, tour or club pages. Each fixture
   row republishes the exact facts that page stated and links it for manual review.
3. **Originated lines.** 15,848 two-sided prices across 43 fixtures. Every pair is complementary and sums to 1.000 at
   1/p with no margin, no clipping and no bookmaker copy.
4. **High-confidence picks.** 51 selections in 13 sports, each clearing both conditions of the brief — strike rate above
   70% and a fair American price inside −250…+10000 — capped at five per sport, each with a unique hand-written
   prediction of 34–60 words that names the event and states the side.
5. **Flagged page.** 12 items with the page that failed to yield the value, so a reader can check by hand.

## Counts (as captured)

| Metric | Value |
|---|---|
| Fixtures captured (14 of 15 sports) | 43 |
| Sports listed | 14 / 15 (greyhounds flagged, not invented) |
| Originated prices | 15,848 |
| High-confidence picks | 51 |
| Unique predictions | 51 |
| Sports at the five-pick cap | 6 (basketball, cricket, darts, ice hockey, rugby league, rugby union) |
| Sources | 34 (32 official, 2 OLBG taxonomy) |
| Flagged items | 12 |
| Pages published | 25 |

Per-sport picks: ice hockey 5, basketball 5, rugby union 5, rugby league 5, cricket 5, darts 5, baseball 4,
tennis 4, Gaelic sports 4, handball 2, volleyball 2, golf 2, motor racing 2, snooker 1, greyhounds 0.

The five-pick target was not met in eight sports. Each shortfall is disclosed on the sport page; the cap there is
evidence, not effort — every rung outside the gate is published as Medium or Low in `markets.csv` rather than promoted.

## Confidence policy

High is a conjunction, not a vibe:

* strike rate **> 0.70**, and
* fair American price **inside −250 … +10000**.

A 70% chance implies about −233, so the band's short end binds and qualifying selections cluster near −250. Anything
that would price at −285 (about 74%) is published as Medium, not relabelled. Medium covers 50–70%, Low below 50%.
The arithmetic is in `scripts/s4c4968fc_model.py` (`tier_for`, `in_band`) and the same functions run inside the gate
script and the test suite, so a build cannot ship a pick that fails either condition.

## Line-setting method

* Match-level estimates come from published records, standings and tables — NHL records on the capture stamp, the
  URC table after Round 3, MLB final standings, the NBA opening-week standings, the WTA/ATP draw seeds and round-one
  scorelines, the PGA leaderboard, the GBGB-less greyhound gap, and FP1 times at COTA.
* Two-way markets are complementary pairs at 1/p; spreads and totals are normal ladders around the expected margin and
  total with the sport's own scale, stepped on the natural grid (quarter-point for Asian handicaps, half-point for
  totals, 0.25 for games/points ladders).
* Set sports invert a best-of-three or best-of-five structure into a per-set probability and price set handicaps,
  set totals and games/points ladders from it.
* Matchup sports (golf, Formula 1) price head-to-head plus a stroke or position ladder.

## Disclosures and known limits

* **Greyhounds** — GBGB's results grid is script-rendered and returned no card; no runner, trap or race was invented.
* **Times** — the URC site renders venue-local time; conversions are flagged per fixture. NBA times are ET as published.
* **NBA sample** — one or two games per team, so basketball ratings are deliberately near-even and the picks lean on
  totals rather than sides.
* **Snooker** — the second semi-final had no named players at capture, so only one match is priced.
* **Darts** — Saturday evening pairings were unpublished at capture; the four afternoon ties are priced.
* **Tennis** — ATP ranking positions were not on the fetched schedule pages, so seeds and bracket path are cited instead.

## Repository review

`4c4968fc/repo-audit.html` records six findings from this session's line-by-line read of the canonical pipeline
(`pipeline/config.py` scope drift, stale root snapshot, the peer desk's sub-70% High-B tier, archive ordering with no
readiness signal, the tolerated f7fa77fc validator warnings, and route tests that can pass with JSON but no HTML).
Two pre-existing suite failures were confirmed against a clean checkout before this session's work was added:
`test_desk_8a900c04` (audit parse error) and a test module that fails to import on a leading-zero integer literal.
Both predate this branch and are reported, not touched.

## Files touched by this session

`scripts/s4c4968fc_{data,model,predictions,build,build_data,validate}.py` · `data/4c4968fc/**` · `4c4968fc/**` ·
`reports/SESSION_4C4968FC.{md,html}` · `tests/pipeline/test_desk_4c4968fc.py` · `COORDINATION.md` §75 (claim, receipts).
No peer desk file was edited.
