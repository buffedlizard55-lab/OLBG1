# Session 40214dfd-olbg1 — T402E report

**Desk:** `40214dfd/` · **Data:** `data/40214dfd/` · **Generators:** `scripts/s40214dfd_{model,data,prose,build,validate}.py`
**Claim:** `COORDINATION.md`, section “Session `40214dfd-olbg1` — T402E claim” (written as §50; the number shifts at every merge, so sections are named here rather than numbered), committed before implementation. **Baseline:** `f255eef` (PR #109).
**Read window:** 2026-10-22T12:12Z → 2026-10-22T12:45Z. **As-of:** 2026-10-22T12:45:00Z.

## 1. What was asked, and the arithmetic that constrains it

The brief asks for picks with a **greater than 70%** chance to win whose price sits in the
**−250…+10000** window.

* American −250 = decimal 1.40 = implied 71.4286%.
* A 70% chance = decimal 1.4286.
* A 75% chance = decimal 1.3333 = −300.

Because price is 1/p, every probability above 71.4286% prices **shorter** than −250. The two rules
therefore overlap only on **70.0000% < p ≤ 71.4286%**. This is not a modelling choice; it is
arithmetic, and it is why earlier desks in this repository reported zero High selections and left
near misses at −251 and −252.

This session resolves it the only honest way available: High is issued **inside the intersection**,
the desk **authors the lines** that express an eligible probability (alternate totals, team totals,
puck lines in half-point steps), and every selection that clears 70% but prices shorter than −250 is
published on the Flagged for review page with its true price. No probability was shaded and no
label was borrowed.

## 2. Official sources read

| Source | URL | Window (UTC) | Fields read |
|---|---|---|---|
| NHL.com | https://www.nhl.com/scores/2026-10-22 | 12:12–12:19 | 12 games, W-L-OTL records, displayed moneylines, team leaders |
| NHL.com standings | https://www.nhl.com/standings/2026-10-21/wildcard | 12:15–12:19 | GP, W, L, OT, PTS, GF, GA, L10, streak |
| NHL schedule API | https://api-web.nhle.com/v1/schedule/2026-10-22 | 12:12 | startTimeUTC for games 2026020154–157 |
| MLB.com | https://www.mlb.com/postseason | 12:20–12:29 | World Series games 1–5, gamePk, clocks, home club |
| MLB.com standings | https://www.mlb.com/standings/ | 12:20–12:29 | final regular-season W-L, RS, RA, L10, streak |
| EuroLeague | game-center-round-7-el2627 | 12:24–12:31 | 9 fixtures, records, preview scoring averages |
| WST | https://www.wst.tv/ | 12:36–12:41 | 8 Round 3 pairings, clocks **without a timezone** |
| GAA | https://www.gaa.ie/fixtures-results | 12:43–12:44 | one fixture, shinty-hurling (excluded category) |

No media outlet, aggregator, tipster or sportsbook is used as a source. No bookmaker price is
fetched; the moneylines printed by NHL.com are recorded as that site's odds partner and labelled.

## 3. Output

* **26 priced fixtures** — NHL 12, MLB World Series 5, EuroLeague 9.
* **299 originated markets / 598 priced outcomes** — match winner, handicap (puck line / run line),
  total, team total.
* **7 High selections across 6 fixtures**, each with a hand-written prediction: Over 4.5 (TOR–NYR,
  −236), Vegas team total under 4.5 (−238), Dallas team total under 3.5 (−244), Carolina +1.5
  (−242), Over 5.5 (UTA–SEA, −247), Utah team total under 4.5 (−241), Detroit team total under 4.5
  (−242).
* **8 snooker fixtures listed without a price** — no timezone on the official clock, no ranking table
  read, so no line and no tier.
* **7 findings** published on the Flagged for review page, including the −252 Boston miss that is
  one American point outside the window.
* **13 of 17 in-scope sports produced no row**, each with the official URL attempted and the specific
  reason (see `40214dfd/coverage.html`).

## 4. Model and its declared assumptions

1. Win rate: Beta(2,2) shrinkage of the season record, then log5 between the two shrunk rates. No
   home-field term.
2. Goals/runs: independent Poisson per side, each side's rate averaging its own scoring rate and the
   opponent's conceding rate, taken from the official standings table.
3. Basketball handicaps: Normal margin with **assumed** σ = 12.0 points, mean set to reproduce the
   log5 win probability. Because σ is assumed, **no basketball row can be High**.
4. Only half-point lines are originated, so nothing pushes.
5. Fair decimal = 1/p with no margin; American = standard conversion from that decimal.

## 5. Verification performed

| Gate | Result |
|---|---|
| `python3 -m unittest discover -s tests/pipeline` | 121 tests OK (includes the 4 desk guards below) |
| `python3 -m unittest discover -s tests -p 'test*.py'` | 38 tests OK |
| `python3 -m pipeline.validate --site .` | 0 errors |
| `python3 scripts/validate.py` (legacy) | PASSED, 0 errors, 3 pre-existing mirror warnings in `f7fa77fc/` |
| `python3 -m pipeline.build --out _site` | 77 canonical pages built |
| `python3 -m pipeline.validate --site _site` | see §7 — passes once the desk is tracked |
| `python3 scripts/s40214dfd_validate.py` | PASSED, 0 errors, 0 warnings |

The desk validator enforces, mechanically: price = 1/p to 4 dp; American consistent with that
decimal; the in-window flag recomputed from the price; every High inside 70.00–71.43% **and** backed
by a prediction; ≥30 words per prediction; an explicit `Selection:` opener; both participants named;
no 12-word phrase reused anywhere in the desk; **every number in every prediction must exist in a
harvest file** (ints, decimals, and number words); every fixture and source on an official host;
every source carrying an observation window and an explicit "not read" statement; 17 coverage rows
with the eight excluded sports listed; no broken internal link or fragment; no literal `%%`; balanced
table markup.

## 6. Irregularities flagged for review

| ID | Severity | Summary |
|---|---|---|
| F-402-01 | high | The brief's two High rules intersect only on 70.00–71.43%; 139 outcomes clear 70%, 10 sit in the window, 3 depend on an assumed spread, 7 are High |
| F-402-02 | medium | High selections are authored alternate lines, not the model's single strongest view |
| F-402-03 | medium | Basketball handicaps rest on an assumed σ and are capped below High |
| F-402-04 | medium | WST publishes no timezone; eight snooker matches stay unpriced and untiered |
| F-402-05 | low | Los Angeles and Calgary goals-for/against were absent from the retrieved standings chunk; those two games have a winner market only |
| F-402-06 | low | Baseball lines ignore pitchers, bullpens, park and rest; all five rows are Low |
| F-402-07 | medium | Eleven in-scope sports have no verified fixture; each is listed with the URL attempted |

## 7. Build note recorded honestly

The canonical builder copies git-*tracked* namespaced directories into `_site`. Before this desk was
committed, `pipeline.validate --site _site` reported exactly one error — `archive.html: broken link
40214dfd/index.html` — because `archive.html` had already auto-listed the untracked directory while
the artifact did not contain it. After the first commit the directory is tracked and the error
disappears; the check is re-run below.

## 8. Cross-desk findings, and a correction about the red gate

The first CI run on PR #116 failed at `python scripts/validate.py` with **98 errors, all in
`53674ac8/`**, all `link escapes repository root -> /53674ac8/...`. That desk merged in PR #111 and had
left the canonical gate red on `main` since. This session prepared a page-level repair of those hrefs,
then found on rebasing that session `ee3c3e8f-olbg1` had already fixed the same 98 links **and** their
generator in `f132b6e` (`scripts/s53674ac8_build_site.py`, `BASE = "./"`). That fix is better than a
page rewrite because it survives regeneration, so this session **dropped its duplicate page edits**
(verified byte-identical to `main`, `git diff HEAD -- 53674ac8` empty) and kept theirs. Credit for the
repair belongs to `ee3c3e8f-olbg1`; The “red gate on `main`” subsection of this session's `COORDINATION.md` entry records this explicitly.

Two findings were raised while reading that desk and are published, not fixed, because the claims
belong to its owner:

* **F-402-08** — all 12 rows it labels High state a model probability of 63–70%, none above the
  brief's 70% threshold.
* **F-402-09** — two of its snooker predictions are the same template sentence with the name swapped.

A repo-wide automated sweep for the same pattern was run but is **not** published: it produced clear
false positives on rows mixing several selections, so only the one desk read row by row is named.

## 9. Late additions in the same session

Three items were added after the first draft of this report and are part of the same PR:

1. **`tests/pipeline/test_desk_40214dfd.py`** (4 tests, ~0.1 s): runs the desk validator as a
   subprocess, then re-asserts from the JSON that every High probability is strictly above 0.70 and
   at most 1/1.4, that every High American price sits inside −250…+10000, and that every prediction
   clears 30 words with no duplicate body. A hand edit to `desk.json` can no longer pass silently.
2. **Two more official routes were tried and recorded as failures**, not as data:
   * tennis — `atptour.com/en/scores/current/stockholm/429/daily-schedule` redirected to the **2025
     archive results** page (completed 2025 matches), so it is not evidence of today's schedule;
   * darts — `pdc.tv/tournament/2026-european-championship` returned a **cookie-consent wall** with no
     round, pairing, clock or result markup.
   Both are now written into `coverage.html` with the URL and the exact failure, and nothing was
   priced for either sport.
3. **F-402-10 was corrected.** The first draft of the flagged register credited *this* session with
   repairing the 98 site-absolute links. That was wrong: session `ee3c3e8f-olbg1` had already fixed
   them and their generator in `f132b6e` (PR #112). The entry now says so, and this branch's own
   page-level edits were dropped during rebase rather than double-claimed.

## 10. Publication record

| Item | Value |
|---|---|
| PR | #116 → `main`, <https://github.com/buffedlizard55-lab/OLBG1/pull/116> |
| Result | **MERGED** 2026-10-22T12:29:33Z, merge commit `f3e0e61` |
| CI on the branch | run `39778393001` — all gates green (evidence/model/site, historical structural gate, field integrity, browser) |
| Deploy | Pages run `39778774282` (push, `main` @ `f3e0e61`), publish job `119825526923`, 30 s, green |
| Live URL | <https://buffedlizard55-lab.github.io/OLBG1/40214dfd/index.html> |

**Counts read back from the deployed bytes** (12:36Z, not from a local build): 26 priced fixtures,
299 markets, 598 priced outcomes, 7 High selections, 7 predictions, 10 flagged findings. The seven
High rows show −236/70.26%, −238/70.43%, −244/70.92%, −242/70.80%, −247/71.19%, −241/70.64%,
−242/70.72%. `flagged.html` was fetched too: the cross-desk table lists all twelve `53674ac8` rows
and F-402-10 credits `ee3c3e8f-olbg1` rather than this session.

**Known limits at publication.** Fourteen of the seventeen in-scope sports carry no priced row (12 not verified at all, Snooker listed without a price, Gaelic football with no in-scope fixture), each with
the official URL attempted and the specific failure; the desk's own `README`/`coverage.html` list
them. Basketball handicaps rest on an assumed σ = 12.0 and are capped below High. Baseball lines use
regular-season aggregates only and stay Low. Snooker pairings are listed with a blank clock because
WST publishes no timezone.
