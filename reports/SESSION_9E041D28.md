# Session `9e041d28-olbg1` — 15-sport OLBG desk, 24 October 2026

**Status:** delivered · **Snapshot:** `2026-10-24T18:20:00Z` · **Branch:** `arena/9e041d28-olbg1`
**Desk URL after deploy:** `https://buffedlizard55-lab.github.io/OLBG1/desk/index.html`

---

## 1. What was asked

Reverse-engineer OLBG for fifteen named sports, publish an updated match list, originate our own
lines on every available market, attach a low/medium/high confidence match-winner pick, write a
unique ≥30-word prediction for each High pick, ship an organised dashboard with sport subpages, a
flagged-for-review page with source links, review the repository line by line, then open a PR,
merge it and confirm the Pages deployment.

## 2. What was delivered

| Item | Result |
| --- | --- |
| Sports covered | **15 of 15** |
| Fixtures confirmed by a governing body | **8** |
| Priced fixtures (line books originated) | **8** |
| Markets originated | **24** |
| Priced outcomes | **48** |
| Picks published | **8** (1 High · 6 Medium · 1 Low) |
| Written predictions | **8**, shortest 70 words, all unique |
| OLBG listing rows captured | **78** across 13 sports (unpriced watchlist) |
| Official / discovery sources logged | **30** |
| Flags for review | **14** |

The gap between "eight priced fixtures" and the brief's "five per sport per day" is the central
finding, not an omission. It is stated on the dashboard, on the Flagged page (F-9E01, F-9E13) and
in §6 below.

## 3. The eight priced fixtures

| ID | Fixture | Start (UTC) | Selection | Fair price | Chance | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| B1 | Tampa Bay Rays at Milwaukee Brewers — World Series G2 | 25 Oct 00:00 | Milwaukee Brewers | −187 | 65.1% | **High** |
| B2 | Milwaukee Brewers at Tampa Bay Rays — G3 | 27 Oct 00:00 | Tampa Bay Rays | −145 | 59.2% | Medium |
| B3 | Milwaukee Brewers at Tampa Bay Rays — G4 | 28 Oct 00:00 | Tampa Bay Rays | −145 | 59.2% | Medium |
| N1 | San Jose Sharks at Boston Bruins | 24 Oct 23:00 | Boston Bruins | −320 | 76.2% | Medium |
| N2 | New York Rangers at Ottawa Senators | 24 Oct 23:00 | New York Rangers | −168 | 62.7% | Medium |
| N3 | Nashville Predators at Pittsburgh Penguins | 24 Oct 23:00 | Nashville Predators | −133 | 57.1% | Medium |
| N4 | Buffalo Sabres at Washington Capitals | 24 Oct 23:00 | Washington Capitals | −188 | 65.2% | Medium |
| N5 | New York Islanders at Dallas Stars | 25 Oct 22:00 | Dallas Stars | +100 | 50.0% | Low |

Only B1 clears every condition the brief sets for a High pick: complete official inputs, a checkable
availability statement, a fair probability above 62 %, and a price inside −250…+10000. N1 is the
strongest form case on the slate but prices at −320, outside the band, and has no official
availability report, so it is Medium on two counts.

## 4. Price construction

All prices are zero-vig (`decimal = 1 / p`), so the band test and the probability test are never in
conflict.

* **Baseball moneyline** — venue-split log5: the home club's home win rate against the away club's
  road win rate. No invented home-field constant.
* **Ice hockey moneyline** — log5 on the regulation-plus-overtime win percentage published by the
  NHL, so a shootout result cannot inflate a side.
* **Totals** — independent Poisson with means built from each side's scoring rate and the
  opponent's conceding rate; the half-line closest to a 50/50 split is the one published.
* **Handicaps** — read off the same score grid (−1.5 puck/run line in every book here).
* **Confidence** — High needs complete inputs *and* an availability check *and* ≥62 % *and* a price
  inside −250…+10000. Medium is 55–62 %, or a stronger number that fails the band or the
  availability test. Low is everything else. This is why one pick carries High.

## 5. Per-sport coverage

| Sport | Priced | Picks | OLBG rows | State |
| --- | --- | --- | --- | --- |
| Baseball | 3 | 3 | 1 | priced (World Series G2–G4) |
| Ice Hockey | 5 | 5 | 11 | priced (5 NHL games) |
| Basketball | 0 | 0 | 10 | listed only — two-game samples (F-9E06) |
| Cricket | 0 | 0 | 9 | listed only — no readable board feed |
| Handball | 0 | 0 | 10 | listed only — league sites blocked (F-9E08) |
| Volleyball | 0 | 0 | 8 | listed only — league sites blocked (F-9E08) |
| Greyhounds | 0 | 0 | 7 | listed only — no official racecard (F-9E09) |
| Tennis | 0 | 0 | 6 | listed only — rows stale vs ATP scores |
| Darts | 0 | 0 | 5 | listed only — PDC consent wall (F-9E07) |
| Rugby Union | 0 | 0 | 5 | listed only — URC fixtures 24 Oct already live/finished |
| Gaelic Sports | 0 | 0 | 4 | listed only — club fixtures, no official feed |
| Motor Racing | 0 | 0 | 1 | listed only — no official grid/result feed read |
| Snooker | 0 | 0 | 1 | listed only — final opponent undetermined (F-9E10) |
| Golf | 0 | 0 | 0 | **no OLBG event at all** (F-9E02) |
| Rugby League | 0 | 0 | 0 | **outrights only, no match** (F-9E03) |

## 6. Why the quota was not filled

Five picks per sport per day needs five fixtures per sport that are simultaneously (a) confirmed by a
governing body and (b) backed by enough official form data to price honestly. This session found
eight such fixtures in two sports. For the other thirteen sports the official route either failed to
render, published nothing, or published a board that cannot support a price:

* **Golf** — the OLBG hub returned "No tips found"; no field or tee sheet was retrieved.
* **Rugby League** — OLBG shows 2027 outright markets only.
* **Darts** — `pdc.tv` served a consent wall instead of a schedule.
* **Handball / Volleyball** — `opel-hbl.de`, `daikin-hbl.de` and `legavolley.it` served reCAPTCHA,
  404s or navigation only.
* **Basketball** — NBA standings cover two games per club; every shrunk rate lands on a coin flip.
* **Cricket / Tennis / Snooker / Rugby Union / Gaelic / Motor Racing** — OLBG rows exist but no
  official fixture board plus form inputs were obtained this session.

Padding those rows with guessed form, assumed line-ups or a tip percentage relabelled as a
probability would have produced a fuller-looking table and a worthless one. They are published as
unpriced watchlist rows instead, each with the OLBG link and the exact reason.

## 7. Verification and corrections made during the build

Every published number was re-read from the source during this session. Corrections applied to the
draft before publication:

1. **Game 2 orientation re-confirmed** from `statsapi` game feed 849802: Tampa Bay (away) at
   Milwaukee (home), American Family Field, first pitch `2026-10-25T00:00:00Z`; home probable Logan
   Henderson, away probable Drew Rasmussen.
2. **Game 3 probables re-read** rather than assumed: 849804 on `2026-10-27T00:00:00Z` lists
   **Freddy Peralta as the Tampa Bay home starter** and Robert Gasser for Milwaukee. The draft's
   team assignment was right; the ordering was rewritten to home-first.
3. **Game 4 has no published starters**, so the field stays blank and the game is flagged.
4. **A fabricated NHL game id was removed** from five source labels; they now cite the league
   schedule only.
5. **One greyhound listing id was wrong** (Doncaster 6:29) and was corrected to `689956`, two
   Expired rows were dropped and three missing rows were added after re-reading the hub.
6. **The Boston price** moved from "Medium because of the band" to "Medium because of the band and
   because no availability report exists", which is the honest pair of reasons.

Verification log by source, all read this session:

* `statsapi.mlb.com` schedule 20–28 Oct, standings (both leagues and NL-only), game feeds for
  849802 / 849803 / 849804 / 849799, and both clubs' active rosters.
* `api-web.nhle.com` schedule for 24 and 25 Oct, standings for 24 Oct, and the Ottawa roster
  endpoint (which returns biography only — no injury field, which is the documented gap).
* `wst.tv/matches`, `formula1.com` US GP, `atptour.com/en/scores/current`, `nba.com/standings`,
  `stats.unitedrugby.com` table and round 4, `gaa.ie/fixtures-results`, `pcb.com.pk`.
* All fifteen OLBG hubs, used for discovery only; six were re-read during the build to confirm the
  captured event ids verbatim.

## 8. Repository review

Six findings, published on `desk/repo-review.html`, each naming the file:

| ID | File | Severity | Finding |
| --- | --- | --- | --- |
| R-9E01 | `index.html` | medium | Freshness chip says "Snapshot 21 Oct 2026"; `data-snapshot` and the manifest say `2026-10-22T12:29:50Z`. |
| R-9E02 | `README.md` | medium | Prose quotes 42 statistical inputs; the manifest records 32 source checks. |
| R-9E03 | `data/*/fixtures.json` | high | 219 fixture ids appear in more than one desk; five appear in eight desks. One event can carry several different originated prices with nothing attributing them. |
| R-9E04 | `data/984d417f/predictions.json` | low | Row `pdc-ec-03` uses the word the brief keeps internal. |
| R-9E05 | `COORDINATION.md` | low | 733,636 bytes in one file; conflicts on almost every rebase. |
| R-9E06 | `.github/workflows/current-pages.yml` | low | The PR gate builds `_site` but never uploads it, so a pull request cannot prove the deployed artifact. |

No peer desk, canonical pipeline file, root page or workflow was modified. These are reported for
the owner rather than silently fixed, because every one of those files belongs to another session's
scope.

## 9. Gates run

| Gate | Result |
| --- | --- |
| `python3 scripts/s9e041d28_build.py` | 8 fixtures · 24 markets · 48 outcomes · 1 High |
| `python3 scripts/s9e041d28_validate.py` | **0 problems** (26 invariant classes) |
| `python3 -m unittest discover -s tests/pipeline` | **392 tests OK** (1 new) |
| `python3 -m pipeline.validate --site .` | **0 errors** |
| `python3 scripts/validate.py` | **0 errors**, 3 pre-existing `f7fa77fc` warnings, 1457 pages link-checked |

## 10. Scope

Written: `scripts/s9e041d28_{data,model,build,validate}.py`, `desk/**`,
`data/9e041d28/**`, `tests/pipeline/test_desk_9e041d28.py`, `reports/SESSION_9E041D28.md`, and
append-only additions to `COORDINATION.md`.

Untouched: `pipeline/**`, `data/current/**`, `.github/workflows/**`, `scripts/validate.py`, root
`*.html`, `sports/**`, `assets/**`, `README.md`, `datasets/**`, and every peer desk. The desk's pages
are staged into `_site/desk/**` by the canonical build's `stage_existing()` pass, so they publish
without a canonical-file edit.

## 11. Publication receipts

| Item | Value |
| --- | --- |
| Pull request | [#234](https://github.com/buffedlizard55-lab/OLBG1/pull/234) |
| PR gate | run [40117470581](https://github.com/buffedlizard55-lab/OLBG1/actions/runs/40117470581) — pass (1m09s) |
| Merged | 2026-10-24T17:47:30Z · merge commit `d27b12b` |
| Main gate + deploy | run [40117732096](https://github.com/buffedlizard55-lab/OLBG1/actions/runs/40117732096) — validate **success**, publish **success** |
| Live | `https://buffedlizard55-lab.github.io/OLBG1/desk/index.html` |

Live read-back confirmed the KPI ribbon (8 fixtures · 1 High · 6 Medium · 24 markets · 78 OLBG
listings · 14 flags) and the pick table rendering Milwaukee at −187 / 65.1% / High with a working
`statsapi.mlb.com` link.

One post-publication correction was made: the dashboard's blocked-work callout still said no
availability report had been retrieved for any fixture, which F-9E05 contradicts (both MLB rosters
were read and fully Active). It now names the hockey-only gap, and the method page states the
availability gate in the High and Medium definitions. No selection, price or label changed.
