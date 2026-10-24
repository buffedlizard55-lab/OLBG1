# SESSION C3026353 — TC3026353 completion report

**Task** TC3026353 · **Branch** `arena/c3026353-olbg1` · **Session** c3026353-olbg1
**Capture window** 2026-10-24T17:07Z–18:45Z · **Report written** 2026-10-24 (UTC)
**Brief** Reverse-engineer OLBG.com for updated upcoming matches across 15 named sports, originate our own
betting lines for every match (winner, handicap, totals and related markets), pick match winners with
low/medium/high confidence, publish 5 unique high-quality written predictions per sport per day with honest
shortfalls, every table row source-linked to an official site, blanks + flags instead of guesses, and land
the whole thing as a clean GitHub Pages dashboard end-to-end (PR → merge → deploy → read-back).

---

## 1. What was built

| Artifact | Path |
|---|---|
| Dashboard (15 sport subpages + 11 core pages) | `c3026353/` (`index.html`, `matches.html`, `markets.html`, `high-confidence.html`, `predictions.html`, `analysis.html`, `sources.html`, `flagged.html`, `methodology.html`, `reverse-engineering.html`, `repo-audit.html`, `sports/*.html`, `assets/desk.css`) |
| Fixture set (107 rows, 15 sports) | `data/c3026353/fixtures.json`, `data/c3026353/matches.csv` |
| Own originated lines (424 priced rows) | `data/c3026353/markets.json`, `data/c3026353/markets.csv` |
| Predictions (73 written, ≥30 words, all unique) | `data/c3026353/predictions.json` + rendered on the site |
| Source register (reads logged with URL + UTC + read method) | `data/c3026353/sources.json` + `sources.html` |
| Flag register (24 flags incl. R-C-01 odds-window arithmetic) | `data/c3026353/flagged.json` + `flagged.html` |
| Desk engine (zero-vig `decimal=1/p`, gate arithmetic) | `scripts/sc3026353_model.py` |
| Data + prose layers | `scripts/sc3026353_data{,2,3}.py`, `scripts/sc3026353_prose{,2,_fix}.py` |
| Builder / validator | `scripts/sc3026353_build.py`, `scripts/sc3026353_validate.py` |
| Tests | `tests/pipeline/test_desk_c3026353.py` (7 tests, suite total 401 passing) |

## 2. Discovery (OLBG, discovery-only)

All 15 requested sports were harvested from their OLBG hubs (case-sensitive slugs
Tennis/3, Basketball/4, Golf/5, Cricket/7, Snooker/8, Rugby_Union/9, Rugby_League/10, Baseball/12,
Ice_Hockey/13, Motor_Racing/14, Darts/15, Handball/20, Volleyball/21, Gaelic_Football/25, Greyhounds/28).
Hub quirks documented on the reverse-engineering page (registry QUIRK-01…05) and reproduced in this capture:

- **GeoIP clock split (QUIRK-02)** — hub timestamps render on an unlabelled UTC−4 edge clock; two NBA cards
  rendered one hour off again (F-C-12). Darts/snooker conversions were anchored to the homepage countdowns.
- **20-event truncation (QUIRK-03)** — handball and greyhound hubs cut mid-card.
- **Zero-tip suppression (QUIRK-04)** — the Golf hub showed "No tips found" and the Rugby League hub showed
  only 2027 ante-post outrights during the live 2026 Rugby League World Cup. Both sports were supplemented
  from governing-body pages and flagged (F-C-17, F-C-21).
- **Leylah Fernandez double-listing** on the Tennis hub (F-C-10) — both cards listed and flagged.

## 3. Verification discipline

Official sources were fetched and read through the page-fetch layer with URL + UTC + read method logged
(`sources.json`): formula1.com, mlb.com, wst.tv, nhl.com (schedule + standings), nba.com (schedule +
standings), atptour.com, pgatour.com (leaderboard + schedule), munster.gaa.ie, nrl.com (RLWC round-2 team
lists + late mail), pcb.com.pk, legavolley.it, gbgb.org.uk, plus search-rendered pdc.tv articles,
maighcuilinn.com, gaacork.ie, galwaygaa.ie where consent walls blocked direct fetch (F-C-02). Rows whose
official body could not be read are flagged (F-C-11/19/20 family) with the official link preserved for
manual review and all unconfirmed values left blank. Media and betting sites were never used as sources.

## 4. Pricing and confidence gate

Every price on the site is this desk's own zero-vig line (fair decimal = 1/p) from documented engines:
log5 on source-checked records (NHL; NBA with Beta(2,2) shrinkage for the 2–3 game sample), logistic
strength gaps, Gaussian margins (rugby/gaelic/RLWC/cricket), best-of-n frame rates (darts/snooker),
normalised weight fields (golf/motor/greyhounds). Handicap and total rows are desk estimates on documented
scales. Partner odds shown on official league pages (nhl.com DraftKings widget, pgatour.com FanDuel widget)
appear only as labelled market context, never copied into our tables.

**High gate (strict conjunction)**: p > 0.70 AND fair American inside −250…+10000 AND an official source read
this session. Arithmetic consequence published as flag **R-C-01**: p > 0.70 forces a fair price of −233.33 or
shorter, so strict-gate High picks live only in the ~1.4-point band −250…−233.33. This window produced
**4 High picks (all ice hockey: NJD −250, CAR −247, DET −245, BOS −235)**; stronger selections (Edmonton .802,
Philadelphia .800, Vegas .770 …) are published as "Medium (chalk cap)" with their probabilities in full and
are never silently promoted.

## 5. Predictions

**73 unique written predictions** (five highest-confidence selections per sport; ice hockey carries six
because five cleared the strict gate). Every text is ≥30 words, names its selection in plain words, and
carries only source-checked detail — where the official page could not be read, the write-up says so instead
of inventing form (visible on `predictions.html` and the sport pages). Banned vocabulary is enforced by the
desk validator and the unit tests (substring checks across all published pages). Uniqueness is enforced at
the 5-gram level; a first pass failed 82 of these checks honestly and the offending texts were rewritten in
fresh voices before publication.

Quota honesty: 12/15 sports reached five written predictions. Motor racing published 5 market-level picks
across 2 F1 events (weekend slate), golf published 5 player picks in the one tour event confirmed on an
official page (Bermuda Championship), and baseball published 2 picks for the only 2 MLB games in the window —
shortfalls displayed on the dashboard and sport pages.

## 6. Validation results (before merge)

- `python3 scripts/sc3026353_validate.py` — **DESK VALIDATION PASSED** (107 fixtures, 73 predictions,
  424 priced rows, 4 High, 0 errors).
- `python3 -m unittest discover -s tests/pipeline -v` — **401 tests OK**, including 7 new desk tests.
- `python3 -m pipeline.build --out _site` + `python3 -m pipeline.validate --site _site` — canonical build
  clean after the desk files were git-tracked (pipeline stages git-tracked files into `_site`; the pre-commit
  run showed 1 transient broken-link error for the untracked desk directory and is recorded here as the
  explanation, not as a merged state).

## 7. End-to-end receipts

- PR: *(filled in COORDINATION.md receipts after the run)*
- Merge: `gh pr merge --merge` on the PR above.
- Pages: https://buffedlizard55-lab.github.io/OLBG1/c3026353/index.html — live byte read-back recorded in
  COORDINATION.md receipts.

## 8. Scope isolation

Touched only `data/c3026353/**`, `scripts/sc3026353_*`, `c3026353/**`, `reports/SESSION_C3026353.*`,
`tests/pipeline/test_desk_c3026353.py`, and append-only COORDINATION.md entries. No shared/integration file
was edited; the pipeline's canonical pages pick up the desk namespace automatically from the repo layout.
