# Session f840c28a-olbg1 — task TF840C

**Desk:** `/f840c28a/` · **Captured:** 2026-10-24T22:55Z · **Branch:** `arena/f840c28a-olbg1`

---

## 1. What was asked

Fifteen sports on OLBG — Golf, Volleyball, Rugby Union, Cricket, Snooker, Darts, Baseball,
Gaelic Sports, Greyhounds, Tennis, Motor Racing, Handball, Ice Hockey, Basketball, Rugby League.
For each: find the upcoming matches, originate our own lines across the available markets, grade a
selection, write unique human predictions of at least thirty words for the high-confidence ones, and
publish the whole lot as a clean dashboard with an executive summary, with every row traced to an
official source and anything unconfirmed left blank and flagged.

## 2. What was found

| | |
| --- | --- |
| OLBG hubs read | 15 (plus the Snooker "All Events" sub-route) |
| OLBG event listings served | 85 across the fifteen sports |
| Sports with no market at all | 3 — Golf, Snooker, Motor Racing (all rendered "No tips found.") |
| Sports with outrights only | 1 — Rugby League (2027 futures only) |
| Fixtures confirmed on a governing body | 18 |
| Fixtures priced | 16 |
| Markets originated | 104 (208 individual prices) |
| Picks published | 16 — 3 High, 4 Medium, 9 Low |
| Written predictions | 10 (53–66 words each) |
| Flagged items | 13 on the Flagged page, plus 6 repository findings |
| Sources logged with URL and UTC read time | 24 |

## 3. The two things worth reading first

**A. The brief's two High-pick rules barely intersect.** A 70% chance is a fair price of −233. The
band's shortest allowed price is −250, which is 71.4%. Requiring both "more than 70%" and "inside
−250…+10000" therefore leaves a 1.4-point window. Of the 208 prices set here, exactly three land in
it, and those three are the High picks: Buffalo @ Washington Under 7.5 (−250, 71.4%), Tampa Bay @
Utah Under 7.5 (−234, 70.1%) and Carolina +1 at St Louis (−234, 70.0%). Nothing was re-priced by
hand to manufacture more. This is a property of the instruction, not of the board — it is worth
deciding which of the two rules is meant to dominate.

**B. Ten of the fifteen sports have no price.** Only ice hockey and basketball produced enough
published data. Cricket has six fixtures confirmed on Cricket South Africa's own site but no
competition record was read; baseball has one confirmed fixture with both starting pitchers named
and no season rate for Milwaukee. The other six sports were found on OLBG and nowhere else. All of
it is on the Flagged page rather than hidden.

## 4. Method

* **Ice hockey** — independent Poisson goals. Each club's goals-for and goals-against rate is
  regressed onto the league average of 3.00 with twelve games of prior weight, then the home side's
  expectation is the mean of its own scoring rate and the visitor's conceding rate times 1.03 (the
  visitor's, mirrored, times 0.97). One grid produces the moneyline, the ±1.5 and ±2.5 puck lines,
  the −1/+1 and −2/+2 Asian handicaps with pushes voided, and totals from 4.5 to 7.5.
* **Basketball** — win rate shrunk with a ten-win, ten-loss prior at .500; logistic win probability
  from the rating gap plus a 3% home edge; expected margin is the probit times a 12.5-point standard
  deviation; the spread ladder comes off the same distribution. **Totals are withheld** — no official
  NBA scoring figure was read.
* **Fair prices** — each market is normalised so its two sides sum to 100%, then converted to
  American odds.
* **Grading** — High above 70%, Medium 60–70%, Low 52–60%, and no pick at all for a selection priced
  shorter than −250.

**Calibration check.** The NHL feed prints a partner moneyline beside each fixture. It was not used
to set any price. Comparing our home-side probability with the publisher's margin-free line, the
largest divergence is 6.6 points (Carolina at St Louis) and most rows are within 3.5 points. That is
the check that the goal expectations are not producing fantasy prices.

## 5. Sources

Official: `api.nhle.com` team summary (all 32 clubs) · `api-web.nhle.com` schedule for 24 October
(12 games, start times, venues, publisher moneylines) · `api-web.nhle.com` standings ·
`statsapi.mlb.com` schedule with probable pitchers · `ak-static.cms.nba.com` injury report, 1:00 PM ET
filing · `nba.com/standings` 2026-27 · `cricket.co.za` fixtures and upcoming.

Discovery only: the fifteen OLBG hubs plus the Snooker sub-route. OLBG is used to learn which markets
exist; it is never the authority for a fixture, a time or a statistic, and its tip shares (member
votes) never enter a price.

Attempted and refused: Lega Pallavolo Serie A table (navigation only in the returned slices),
Handball-Bundesliga table (empty shell) and fixture plan (404), Premiership Rugby fixtures (404),
PDC European Championship (consent wall).

## 6. Repo review

Six findings, published on `/f840c28a/repo-review.html`:

* **R-01** — 90 session desk directories exist; the publisher's allowlist carries 16. 74 desks are
  tracked but have no published entry point, while the README still promises they stay published.
* **R-02** — `README.md:50` defines High as ≥60% probability, the brief says >70%. Desks in this
  repository are therefore not comparable to each other.
* **R-03** — `data/current/audit.json` is 10,473,214 bytes and tracked; 3,032 files total.
* **R-04** — clean result: all twenty root pages parsed, zero broken relative links.
* **R-05** — `COORDINATION.md` is 849 KB, append-only, and carries duplicate section numbers (74
  twice, 75 twice, 84 twice, 85 twice), so cross-references are ambiguous.
* **R-06** — clean result: the existing suite and `scripts/validate.py` pass at branch head.

## 7. What this session changed

Additive only, inside its own namespace: `data/f840c28a/`, `scripts/sf840c28a_*.py`, `f840c28a/`
(25 pages), `tests/pipeline/test_desk_f840c28a.py`, this report, and an append to `COORDINATION.md`.
Two deliberate shared touches, both with peer precedent: one `ARCHIVE` entry in `pipeline/build.py`
so GitHub Pages will serve the desk, and nothing else.

## 8. Gates

| Gate | Result |
| --- | --- |
| `python3 -m unittest discover -s tests/pipeline` | 641 tests, OK |
| `python3 -m unittest tests.pipeline.test_desk_f840c28a` | 30 tests, OK |
| `python3 scripts/sf840c28a_validate.py` | 1,049/1,049 checks passed |
| `python3 -m pipeline.build --out /tmp/sitecheck` | 25 pages; `f840c28a/` present with 15 sport pages |
| `python3 -m pipeline.validate --site /tmp/sitecheck` | 0 errors |
| `python3 -m pipeline.validate --site .` | 0 errors |
| `python3 scripts/validate.py` | PASSED (three pre-existing `f7fa77fc` warnings untouched) |

## 9. Honest limits

* No starting goaltender was read for any hockey fixture. It is the largest unmeasured input on the
  board.
* No injury report was read outside the NBA.
* The NBA records are one to two games deep; the shrinkage is heavy and the picks that depend on it
  are graded Low for that reason.
* One of the league's twelve hockey games (MIN @ SEA per OLBG) could not be individually confirmed in
  the returned schedule slice, and MTL @ WPG on 25 October comes from a different schedule date.
  Both are published with no price and no pick.
