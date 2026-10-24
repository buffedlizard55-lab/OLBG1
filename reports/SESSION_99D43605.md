# Session 99d43605 — T99D4 — Independent 15-sport research desk (24 Oct 2026)

## Scope claimed
Reverse-engineer OLBG.com's match-market coverage for exactly the 15 sports in the
brief (Golf, Volleyball, Rugby Union, Cricket, Snooker, Darts, Baseball, Gaelic
Sports, Greyhounds, Tennis, Motor Racing, Handball, Ice Hockey, Basketball,
Rugby League) and originate an independent card: fair lines on every match,
a graded pick per match, written predictions for High picks, and a flagged-for-review
register. No overlap with any other claimed task code.

## Deliverables (commit 75173b5 on arena/99d43605-olbg1)
- `99d43605/` — 25 pages: index (executive summary), picks, predictions, markets,
  matches, flagged, sources, methodology, olbg (discovery log), sports index +
  15 sport pages. Picks-first layout; every tbody row has >=1 official https link.
- `data/99d43605/` — fixtures, lines, picks, predictions, flags, sources, coverage,
  olbg, manifest (json mirrors of the module of record).
- `scripts/s99d43605_model.py` — estimator: Beta(2,2) shrinkage + Bradley-Terry/log5
  (canonical, no home/player/market adjustments), Poisson totals/handicaps from
  officially published goals-for/against, darts seed pricing (rate = 1/seed),
  tier gate: High iff probability strictly above 70.00% AND fair American inside
  -250..+10000, match market, upcoming, both sides measured from official sources.
- `scripts/s99d43605_data.py` — 48 fixtures with numeric inputs copied only from
  the official reads; source ledger (33 entries w/ observed UTC stamps); OLBG
  discovery log held at arms-length (discovery only).
- `scripts/s99d43605_build.py`, `scripts/s99d43605_validate.py` (0 errors),
  `tests/pipeline/test_desk_99d43605.py` (23 tests, passing).
- `index.html` root landing: start-here strip and latest-desk panel repointed to
  this desk (2-line touch, peer convention).

## Results summary
- Priced books: 35 fixtures, 59 market lines (winner + totals + handicaps where
  official attack/defence rates were readable; NBA handicap/total intentionally
  unpriced and disclosed).
- Tiers: 1 High / 16 Medium / 18 Low. High = Edmonton Oilers ML v Toronto at
  exactly -250 (the band's inclusive edge), written prediction on
  `99d43605/predictions.html`.
- Documented near-misses (deliberately NOT High): Vegas at precisely 0.7000
  (rule is strictly above 70.00%) and New Jersey at -267 (outside band). Logged
  as F-99-01/F-99-02 against the five-per-sport aim: the quota is never made up
  by stretching prices.
- Excluded/time-state: NHL Ducks-Flyers (in play at read), URC derbies, Top 14
  Toulon-Pau, snooker semi-finals, HBL Balingen, darts evening session — kept in
  the tracker with states, no pre-match prices.
- Withheld rather than guessed: snooker final (finalists unknown), volleyball
  round (nav-walled calendar), greyhound race cards (GBGB cards are script-rendered),
  WTA Wuhan semifinal (site returned a JS shell), Premiership Quins game
  (fixtures page unreadable), GAA hurling final pick (pairing official but no
  official form digits), NBA totals/handicaps (no official team PPG read).

## Gates run locally (all green before PR)
- `python -m unittest discover -s tests/pipeline -v` — 505 tests OK (incl. 23 new).
- `python -m pipeline.validate --site .` — 0 errors.
- `python scripts/validate.py` — PASSED (3 pre-existing warnings in f7fa77fc only).
- `python -m pipeline.build --out _site` — builds; desk copied into _site.
- `python -m pipeline.validate --site _site` — 0 errors.
- `python scripts/s99d43605_validate.py` — DESK VALIDATION PASSED.

## Publication receipts
- PR #273 merged (gates run 40123801235 green incl. browser gates); follow-up PR #275 merged
  (executive table accuracy + PCB source URL). Main runs green incl. `Publish canonical
  GitHub Pages` (run 40124604358). Live read-back of
  https://buffedlizard55-lab.github.io/OLBG1/99d43605/ confirmed the executive summary, the
  High table (Edmonton -250) and the predictions page bytes.
- Canonical-publisher note for successors: post-#271 the artifact copies only `ARCHIVE`-registered
  desks; this desk's registration line lives in `pipeline/build.py`.

## Notes for the next session
- High-window honesty: with Beta(2,2)+log5 the (70%, 71.43%] corridor is narrow;
  expect 0-3 Highs per night. Shortfall vs "5 per sport" is recorded on the
  Flagged page and in F-99-01 — do not "fix" by widening prices.
- If totals/handicaps are wanted for NBA, read an official team-ratings page
  (nba.com/stats renders client-side; consider the official WNBA/NBA stats
  JSON if reachable) and blend the same way as NHL.
- COORDINATION.md entry: section 84.1 beneath.
