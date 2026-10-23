# Session report — `7a9b24e5-olbg1`

**Window:** 2026-10-23T21:05Z – 2026-10-23T21:55Z read; site built 2026-10-23T22:05Z; evidence expires 2026-10-24T03:55Z.
**Branch:** `arena/7a9b24e5-olbg1` · **Desk:** `/7a9b24e5/index.html` · **Claim:** `COORDINATION.md` §1 row `T7A9B`, §75.

## 1. What was produced

| Artefact | Path | Count |
|---|---|---|
| Fixtures read from official pages | `data/7a9b24e5/desk.json` | 36 (35 eligible, `BB05` withheld) |
| Source register | `data/7a9b24e5/desk.json` → `reads` | 30 reads (23 official, 7 discovery) |
| Originated outcomes | `data/7a9b24e5/markets.json` | 624 |
| Promoted picks | `data/7a9b24e5/picks.json` | 14 |
| Capped (shorter than −250) | `data/7a9b24e5/capped.json` | 168 |
| Hand-written predictions | `data/7a9b24e5/predictions.json` | 14, all ≥30 words, all unique |
| Pages | `7a9b24e5/**` | 26 (dashboard + 15 sport pages + 10 desk pages) |
| Desk gate | `tests/pipeline/test_desk_7a9b24e5.py` | 15 checks |

## 2. Coverage against the brief's 15 sports

| Sport | Fixtures | Promoted | State |
|---|---|---|---|
| Baseball | 5 | 4 | MLB World Series Games 1–4 priced; Game 5 withheld (`ifNecessary=Y`) |
| Ice Hockey | 5 | 5 | NHL 24–25 Oct slate, all priced |
| Rugby Union | 5 | 5 | URC Round 4, all priced |
| Basketball | 5 | 0 | NBA one game into the season — no defensible strength input, unpriced |
| Rugby League | 4 | 0 | RLWC Round 2 — Round 1 results share no opponents across pools, unpriced |
| Cricket | 5 | 0 | ICC fixtures confirmed; no form input in the page read, unpriced |
| Golf | 5 | 0 | Genesis Championship Round 3 leaderboard read; a scoreboard is not a probability input |
| Motor Racing | 2 | 0 | Mexico City GP sessions; drivers' standings body did not render |
| Tennis, Snooker, Darts, Handball, Volleyball, Gaelic Sports, Greyhounds | 0 | 0 | documented gaps in `desk.json` → `gaps`, attempted URLs on `flagged.html` |

**Covered:** 8 of 15. **Gaps:** 7 of 15, each with the attempted URLs.

## 3. The confidence gate, stated precisely

The brief's band is a *price* window: −250 is a probability of 250/350 = 71.43%, and +10000 is 0.01%. "Inside
−250…+10000" therefore means *no shorter than −250*, i.e. p ≤ 71.43%. This desk pairs that with a 62% floor so that
"high confidence" means something, giving a promoted window of **62.00% – 71.43%**. Anything above 71.43% would
price shorter than −250 and is published in `capped.json` — disclosed, never promoted.

Promoted selections, all of which name a side:

```
P7A9B-001 Baseball    BB01  Milwaukee Brewers +1.25        71.26%  -248
P7A9B-002 Baseball    BB02  Milwaukee Brewers +1.25        71.26%  -248
P7A9B-003 Baseball    BB03  Over 6.25 runs                 71.10%  -246
P7A9B-004 Baseball    BB04  Over 6.25 runs                 71.10%  -246
P7A9B-005 Ice Hockey  IH01  Philadelphia Flyers Over 2     71.37%  -249
P7A9B-006 Ice Hockey  IH03  Boston Bruins Over 3           71.37%  -249
P7A9B-007 Ice Hockey  IH04  Ottawa Senators Over 2         71.37%  -249
P7A9B-008 Ice Hockey  IH02  Los Angeles Kings Over 3       70.42%  -238
P7A9B-009 Ice Hockey  IH05  Dallas Stars +0.5              70.07%  -234
P7A9B-010 Rugby Union RU04  Leinster +1.75                 71.41%  -250
P7A9B-011 Rugby Union RU01  Vodacom Bulls -8               71.21%  -247
P7A9B-012 Rugby Union RU02  DHL Stormers -2.5              71.21%  -247
P7A9B-013 Rugby Union RU05  Ospreys +10                    71.21%  -247
P7A9B-014 Rugby Union RU03  Benetton +9.25                 71.01%  -245
```

## 4. Origination inputs (official only)

* **Baseball** — 162-game scoring rates from the MLB Stats API: Milwaukee 832/618, Tampa Bay 736/650; expected runs
  per side = mean of own scoring rate and opponent's conceding rate; margin sd 3.2, total sd 4.5, home edge +0.15.
* **Ice hockey** — goals for/against per game from the NHL standings read this session; margin sd 1.9, total sd 2.0,
  team-total sd 1.45, home edge +0.15.
* **Rugby union** — half of each club's league-table points difference per game (50% shrinkage) plus three points of
  home advantage; margin sd 14.
* **Not originated** — basketball, rugby league, cricket, golf, motor racing. Reasons are on `flagged.html`.

## 5. Verification method and limits

* Every fixture row links the official page it was read from; second sources are linked where two were read.
* Start times are published only where the official page gave an explicit UTC clock. The five URC fixtures and five
  ICC fixtures print "Local"/"Your time" with no zone, so their UTC column is blank and each is flagged.
* No injury, lineup, weather, travel or referee claim appears anywhere, because none was read from an official page.
* The OLBG tips tables are client-rendered: every hub read returned "No tips found." OLBG is therefore cited for
  market vocabulary only, never for a fixture or a price. `robots.txt` disallowed paths were not used.
* The words "model" and "verified" are absent from all 26 published pages (enforced by the desk test).

## 6. Repository audit

Eight findings: seven from the structural review, plus one high-severity repair made here.

* **RA-08 (high).** `scripts/se58210b8_predictions.py` reached `main` with unresolved merge-conflict markers
  (nested `<<<<<<<`/`=======`/`>>>>>>>`). Python could not parse the file, so `test_desk_e58210b8` errored and the
  tree-wide parse audit recorded one parse error, which also failed `test_desk_8a900c04`. This session hit the failure,
  removed the markers locally (keeping the newer PR #184 prose), and then found on rebasing that peer PR #194 had
  already repaired the file on `main` in the same way. The branch therefore carries no difference in that file, and the
  suite is green: 241 tests, no failures.
* RA-01 … RA-07 are recorded on `7a9b24e5/repo-audit.html` with the exact command used to check each one.

## 7. Gates

```
python3 -m unittest discover -s tests/pipeline -v     241 tests, OK (before the repair: 1 failure, 1 error)
python3 scripts/s7a9b24e5_model.py                    624 markets, 14 picks, 168 capped
python3 scripts/s7a9b24e5_build.py                    26 pages
python3 -m pipeline.build --out _site                 canonical pages built
python3 -m pipeline.validate --site _site             0 errors
python3 scripts/validate.py                           0 errors (3 pre-existing f7fa77fc warnings, untouched)
```

Nothing outside `data/7a9b24e5/**`, `scripts/s7a9b24e5_*.py`, `7a9b24e5/**`, `reports/SESSION_7A9B24E5.md`,
`tests/pipeline/test_desk_7a9b24e5.py` and append-only `COORDINATION.md` differs from `main` in the final diff.

## 8. Receipts

Recorded in `COORDINATION.md` §76 after the merge: PR number, merge commit, Pages run id and the live read-back of
`/OLBG1/7a9b24e5/index.html`.
