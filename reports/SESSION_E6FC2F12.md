# Session `e6fc2f12-olbg1` — T64 independent live desk

**Published:** `/e6fc2f12/` · **Branch:** `arena/e6fc2f12-olbg1` · **PR:** #110
**Claim:** T64, 2026-10-22T12:05Z, board section §50 (renumbered from §49 at merge)

## What was asked

An independent, live desk that covers every in-scope OLBG sport except soccer, horse racing,
American football, boxing, UFC/MMA, specials, hurling and cycling — with today's fixtures pulled from
OLBG, each fixture verified against the league, governing body or tour itself, our own multi-market
lines rather than copied bookmaker prices, a high-confidence tier restricted to the brief's
−250…+10000 band, and a unique, hand-written prediction for every high-confidence pick.

## What shipped

| | |
|---|---|
| Fixtures | **91** — 73 priced, 18 unpriced with a stated reason each |
| Sports | NHL 60 · rugby union 8 (URC R4) · snooker 8 (NI Open) · MLB 5 (World Series) · rugby league 5 (RLWC) · F1 5 sessions |
| Markets | **1098** — match winner, handicap ladders, match totals, team totals |
| Tiers | High **18** · Medium **239** · Low **841** (sum 1098) |
| Sources | **20** official, each with URL, publisher, kind, purpose, read timestamp |
| Predictions | **18**, one per High selection, all ≥30 words, no template reuse |
| Pages | **26** HTML + `fixtures.csv` + `markets.csv` |
| Gaps | **11** in-scope sports published as gaps with the attempted URL and the specific failure |

## The rule, and why High is only 18

A High pick required both a model probability above 70% and a fair price that expresses inside the
brief's −250…+10000 window. Those two conditions intersect at a single narrow slice:

- 70.0% → fair 1.4286 → −233
- 71.43% → fair 1.4000 → −250

So a High pick is a genuine favourite in the 70.0–71.4% band, never an odds-on shot at −500. A team
the model rates at 85% is graded Medium — not because the model dislikes it, but because the brief's
price window cannot express an 85% chance. Widening the tier to manufacture more High picks would
have violated the brief, so the narrowness is disclosed on the landing page, the High-confidence page
and Methodology instead.

## Method

- **Probability.** Official win/loss records, Beta(2,2)-shrunk toward .500, combined with the log5
  identity for match-winner markets. No home edge is inserted (no verified venue-level split was
  read this session), and that omission is stated rather than papered over.
- **Totals and handicaps.** NHL and MLB goals/runs are modelled as independent Poisson with each
  side's rate set to the mean of its own scoring rate and the opponent's concession rate; rugby
  totals use a normal approximation on the combined scoring rate. Handicap ladders extend to ±1.5,
  ±3.5, ±6.5 and ±9.5 so the reader can see where the price crosses fair.
- **American conversion.** Prices are generated from the probability (100·p/(1−p) above even money,
  100·(1−p)/p below), then rounded to the nearest integer — never the reverse, so no probability is
  reverse-engineered from a quoted price.
- **Withholding.** MLB markets are capped below High because no starters, parks, lineups or bullpens
  were read. Dallas Stars totals are withheld because their goals for/against were not visible in
  the official table. Unpriced fixtures carry no market at all — the validator rejects that state.

## Verification

`python3 scripts/se6fc2f12_model.py && python3 scripts/se6fc2f12_build_site.py && \
python3 scripts/se6fc2f12_validate.py` → **VALIDATION PASSED — 0 errors, 0 warnings**.

The gate checks: tier arithmetic, American/decimal/probability agreement, High price-window
compliance, prediction length, uniqueness and selection naming, duplicate fixture and market keys,
unpriced fixtures carrying markets, source traceability for every fixture, broken internal links and
anchors, pages unreachable from `index.html`, and render artefacts (`None`, `nan`, `%%`).

## Gaps, published not hidden

Eleven in-scope sports have no fixture on this desk because their official pages could not be read:
basketball (EuroLeague client-rendered, NBA scoreboard HTTP 500), tennis (ATP feed in-play only),
darts (PDC cookie wall), golf (PGA schedule grid client-rendered), cricket (no fixture list at the
read URL), handball, volleyball, esports, greyhounds, AFLW (ladder client-rendered) and GAA
(near-empty fixture page). Each is listed on `flagged.html` with the exact URL and reason, plus the
assumptions that could bias a price (no home edge, no calibration, no player-level input).

## Publication

- PR #110 merged 2026-10-22T12:09:47Z as `a8c2775`; canonical checks `39776109024` and pages
  `39776109134` both green. Live page read back from the deployed bytes: 91 fixtures / 1098 markets /
  18 High / 20 sources.
- PR #113 merged 12:19Z as `e5d832a` (pages `39776645701` green). Corrects three OLBG hub ids
  (Handball 22→20, Volleyball 23→21, Greyhounds 31→28) and names the fixture in the homepage pick
  list; verified again on the deployed page with a cache-busting query string.
- The canonical `scripts/validate.py` gate is red on `main` since PR #111 (`53674ac8`): 40 errors, all
  from that desk's site-absolute links, none from this one. Logged in §50 as an integrator note; no
  other session's files were edited.

## Files

```
data/e6fc2f12/    fixtures · markets · predictions · ratings · sources · coverage · model (.json)
scripts/          se6fc2f12_data.py · _model.py · _predictions.py · _build_site.py · _validate.py
e6fc2f12/         26 HTML pages, assets/style.css, assets/app.js, fixtures.csv, markets.csv
```
