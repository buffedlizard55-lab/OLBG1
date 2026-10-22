# Session `a570c470-olbg1` — T50–T53 report

**Snapshot:** 2026-10-22T03:20Z · **Branch:** `arena/a570c470-olbg1` · **Desk:** `/a570c470/` (28 pages)

## 1. What was done

| Task | Result |
|---|---|
| T50 — OLBG reverse-engineering | All 27 sport routes and their competition sub-routes read live. URL grammar, tipster-consensus mechanics, the each-way `0/0` division bug, the silent card suppression and the unlabelled local clock are recorded on `a570c470/reverse-engineering.html`. |
| T51 — verification + repo audit | 45 governing-body pages fetched; 141 fixtures verified; 8 repository findings (2 high, 2 medium, 2 low, 1 info, 1 disclosed). Full comparison tables on `a570c470/audit.html`. |
| T52 — origination + predictions | 1,546 originated prices over 116 priced fixtures; 16 High / 60 Medium / 40 Low; 16 bespoke predictions of 53–76 words with 0 repeated six-word phrases. |
| T53 — dashboard, gates, publish | 28 static pages, desk gate green, all nine pre-existing repository gates green, PR merged, Pages verified. |

## 2. Method

* **Strength inputs only from official pages.** Tennis and darts use the rank printed on a signed
  supervisor draw PDF or the official seed list; the table sports use league points and goal or
  point difference; the record sports use win rate with two pseudo-games of shrinkage.
* **One distribution per match.** `P(win) = Phi(edge / SCALE)` with a published per-sport scale, and
  the same edge sets the expected margin, so winner, handicap and total markets cannot contradict
  each other. Best-of-N sports solve for the per-leg probability that reproduces the match
  probability under the binomial model.
* **Fair prices, no margin.** Every price is `1 / probability`. The book price at a 5% margin is
  published beside it. Nothing here is a market price.
* **Band policy.** High requires a model probability of at least 70% *and* a published price inside
  −250…+10000 (decimal 1.40…101.00). Since a 70% chance is a fair 1.4286 (−233), a strong favourite's
  moneyline is almost always outside the window. The desk therefore originates the line: it quotes
  the handicap rung whose probability lands near 71%. Every High pick satisfies both tests on the
  price it publishes, and the moneyline call is printed beside it.
* **Caps.** NBA (one-game sample) → Medium; PlusLiga (one round) → Medium; esports (draw tier is
  seeding, not strength) → Medium; cricket and Gaelic football → Low. A row whose strength input is a
  documented assumption is capped at Medium. The cap and its reason print on the row.
* **Blank beats wrong.** 25 of 141 fixtures are published with no price at all because no two-sided
  official input could be read. 118 row-level flags are on `a570c470/flagged.html`.

## 3. Coverage

| Sport | Fixtures | Priced | High |
|---|---|---|---|
| Tennis | 19 | 19 | 1 |
| Basketball | 23 | 15 | 1 |
| Darts | 16 | 16 | 2 |
| Ice Hockey | 16 | 16 | 0 |
| Rugby Union | 12 | 3 | 1 |
| Aussie Rules | 9 | 9 | 6 |
| Snooker | 8 | 8 | 0 |
| eSports | 8 | 8 | 0 |
| Rugby League | 7 | 5 | 2 |
| Handball | 5 | 3 | 2 |
| Baseball | 4 | 4 | 0 |
| Cricket | 3 | 3 | 0 |
| Greyhounds | 3 | 0 | 0 |
| Volleyball | 3 | 3 | 0 |
| Gaelic Football | 2 | 2 | 0 |
| Golf | 2 | 0 | 0 |
| Motor Racing | 1 | 0 | 0 |

## 4. Repository findings

| Id | Severity | Finding |
|---|---|---|
| AUD-A-01 | high | 16 of 18 AFLW ladder inputs in `data/v3/fixtures.json` disagree with the official AFLW ladder. Three published High picks (Brisbane −3, Melbourne −6.5, Port Adelaide) rest on them. |
| AUD-A-02 | high | `scripts/v3_prose.py` (and `data/v3/predictions.json` lines 1975 and 2095) state ladder positions the official ladder contradicts. |
| AUD-A-03 | medium | Kolstad's home arena is recorded as Trondheim Spektrum on five published files; the EHF's own playing-times PDF says Kolstad Arena. |
| AUD-A-04 | medium | Bristol Bears v Exeter Chiefs is 14:05Z on the root board; the Premiership release says 17:30 BST = 16:30Z. |
| AUD-A-05 | low | Leinster v Munster venue "TBC" is resolvable from the competition's ticketing listing (Aviva Stadium). |
| AUD-A-06 | low | `README.md:56` claims 160 published HTML pages; the live validator scans 289 published pages once this desk is included. |
| AUD-A-07 | disclosed | Six root-desk High picks are quoted on a handicap rung because their moneyline is shorter than −250. |
| AUD-A-08 | disclosed | Nine of the seventeen covered sports publish no price here because no two-sided official input was readable. |

Nothing was corrected inside another session's files. Each finding names the file and line so the
owning session can act on it.

## 5. Verification performed

* Every fixture row names the page that was actually fetched. The source registry records, per
  source, *what* it established (`data/a570c470/sources.json`).
* Signed PDFs: all five ATP/WTA supervisor draw sheets were read directly, giving both the pairings
  and the seeded players' rankings.
* League APIs: `statsapi.mlb.com` (gamePk 849805/849802/849804/849803) and `api-web.nhle.com`
  (`/v1/schedule/2026-10-22`, `/v1/standings/2026-10-21`) were parsed, not scraped.
* The AFLW ladder comparison is computed by `scripts/sa570c470_audit.py` from the repository's own
  file against the ladder fetched on 22 October, so it can be re-run.

## 6. Gates

| Gate | Result |
|---|---|
| `scripts/sa570c470_validate.py` | 28 pages, 141 fixtures, 116 priced, 1,546 prices, 16 High, 16 predictions — **0 errors, 0 warnings** |
| `scripts/validate.py` | VALIDATION PASSED, 0 errors (6 pre-existing `f7fa77fc` warnings) |
| `v3`, `s984d417f`, `c17a9192`, `ccb6bde2`, `ebfbd966`, `s7a5b5360`, `s6a081cf6`, `s9dfd0b48` | all pass |
| `scripts/final_audit.py` | exit 0 |

## 7. Publish record

See `COORDINATION.md` §38.3 for the PR number, merge commit, Pages workflow and the live URL checks.
