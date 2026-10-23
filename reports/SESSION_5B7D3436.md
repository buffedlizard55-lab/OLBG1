# T5B7D — 23 October 2026 evidence-first OLBG desk

## Release status

Independent, isolated release at **`/OLBG1/5b7d3436/`**. The observation registry is timestamped **2026-10-23T21:36:17Z** and expires at **2026-10-24T03:36:17Z**. The dashboard is static, source-linked and makes no browser API calls. It is not affiliated with OLBG and does not offer wagering.

This release covers exactly the requested 15 sports: Golf, Volleyball, Rugby Union, Cricket, Snooker, Darts, Baseball, Gaelic Sports, Greyhounds, Tennis, Motor Racing, Handball, Ice Hockey, Basketball and Rugby League. Australian Rules and eSports were not added.

## What the fresh reads established

- **59 source records:** 25 official and 34 OLBG-discovery records, with URL, publisher, retrieval method and observation notes.
- **20 official watchlist rows:** 19 upcoming and one in progress. Every fixture card has at least one official source link.
- **15 OLBG hubs and five competition subroutes** inspected. The main page displayed “No tips found” / “No tournaments tips found.”
- **11 event samples:** every displayed selection was labeled Expired. Therefore this release establishes **zero open OLBG markets**. An officially upcoming opponent does not reopen an expired OLBG listing.
- **64 flagged findings** disclose unavailable listings, unresolved clocks, missing runners/pairings/fields, retrieval limitations, pricing gaps and repository observations.

Official fixture evidence includes NHL schedule and standings, MLB schedule and standings, the NBA game page and 5:15 PM injury PDF, ICC match/injury pages, WTA Ningbo order of play and draw, URC team announcements, an official-domain PDC article, Cork GAA, Formula 1, NRL, WST, PGA Tour, THW Kiel, GBGB and TAURON Liga. OLBG remains discovery only.

## Coverage and pricing outcome

| Sport | Official watchlist rows | Experimentally priced |
|---|---:|---:|
| Golf | 1 | 0 |
| Volleyball | 1 | 0 |
| Rugby Union | 1 | 0 |
| Cricket | 1 | 0 |
| Snooker | 1 | 0 |
| Darts | 1 | 0 |
| Baseball | 2 | 2 |
| Gaelic Sports | 1 | 0 |
| Greyhounds | 1 | 0 |
| Tennis | 1 | 0 |
| Motor Racing | 1 | 0 |
| Handball | 1 | 0 |
| Ice Hockey | 5 | 5 |
| Basketball | 1 | 0 |
| Rugby League | 1 | 0 |
| **Total** | **20** | **7** |

The pricing script produced **21 two-way markets / 42 outcomes** across those seven NHL/MLB fixtures: moneyline, puck/run line and total. Every book is reproducible from the recorded official totals and disclosed assumptions; each two-way raw probability mass is 1.0. These are fair-line calculations, not bookmaker quotes, available wagers or claims of an edge.

### Research preferences — not published picks

| Fixture | Preference | Probability | Fair American | Research tier |
|---|---|---:|---:|---|
| BB01 | Milwaukee Brewers to win | 63.8479% | −177 | Medium |
| BB02 | Milwaukee Brewers to win | 63.8479% | −177 | Medium |
| IH01 | Montréal Canadiens to win | 58.2856% | −140 | Low |
| IH02 | Colorado Avalanche to win | 55.3506% | −124 | Low |
| IH03 | Anaheim Ducks to win | 57.0160% | −133 | Low |
| IH04 | New Jersey Devils to win | 67.6240% | −209 | Medium |
| IH05 | Boston Bruins to win | 76.8725% | −332 | Medium |

Boston exceeds 70% but is shorter than −250, so it fails the required band. Every preference also fails the open-market and complete-availability gates. The 13 unpriced fixtures have explicit withholding reasons rather than invented numerical inputs.

## High selections and prediction prose

**High selections: 0. Published prediction articles: 0.**

The five-per-sport figure is an evidence-capped target, not a quota. A release would require an open non-expired OLBG market, official fixture evidence, sufficient official availability information, unrounded probability strictly above 70%, fair American odds from −250 through +10000, and unique natural prose of at least 30 words naming the participants and selection and using supported form, history/statistics and availability. No row passes that conjunction, so no prose was manufactured. Research-only fair lines are not relabeled as predictions.

## Material limitations and irregularities

- NHL starting goalies and complete availability packages were not captured. Montréal’s confirmed Nick Suzuki absence is disclosed without an invented numerical adjustment.
- MLB probable pitchers are named, but pitcher statistics are absent. Games 1 and 2 therefore share a team-total baseline and are not pitcher-specific handicaps.
- Basketball has an official injury report and schedule, but no compatible current numerical team-strength package; its winner line is withheld.
- Cricket’s “Your time,” NRL’s conflicting heading/card clocks, WST’s conflicting official displays and Handball’s newer-preview/older-schedule conflict remain flagged rather than silently resolved.
- WTA’s draw is not treated as an order of play. The bare PlusLiga URL redirected to TAURON Liga. PDC direct extraction returned consent content, so the official-domain indexed article method is disclosed.
- Exact per-URL network timestamps were unavailable; all reads use a common post-read registration timestamp. Runtime code suppresses prices at the earlier of evidence expiry or official start. With JavaScript disabled, estimates are hidden because freshness cannot be checked.

## Repository audit

The isolated source/input inventory records path, line count, byte count and SHA-256 in `data/5b7d3436/repo-inventory.json`; generated page hashes are in `site-manifest.json`. The audit page explicitly distinguishes this scoped inventory from a false claim that every historical repository fact was manually recertified.

Shared observations carried into the review register:

1. `COORDINATION.md` contains duplicate numbering and stale statuses; this session uses collision-resistant `T5B7D` and append-only updates.
2. The canonical root still describes an older 22 October, 17-sport release. It was not overwritten because shared canonical outputs are integration-only.
3. Historical desks were used only for schemas and URL leads, never as fresh sporting evidence.
4. The legacy validator reports three pre-existing warnings for internal-policy citations in `f7fa77fc/flagged.html`; there are zero errors.
5. A required rebase onto advancing `main` produced two coordination-board conflicts. Only six conflict-marker lines were removed; both sides’ entries were retained. No peer source or data file was edited.

## Delivered files

- `5b7d3436/`: 28 HTML pages, including overview, matches, markets, High gate, analysis, discovery, sources, flagged review, methodology, predictions, repository audit, all 15 sport pages and 404.
- `data/5b7d3436/`: source registry, fixtures, discovery, flags, fair lines, summary, predictions register, CSV exports and manifests.
- `scripts/s5b7d3436_data.py`, `s5b7d3436_lines.py`, `s5b7d3436_build.py`: reproducible observation, pricing and rendering pipeline.
- `tests/pipeline/test_desk_5b7d3436.py`: 29 desk-specific regression tests.

## Executed validation

| Check | Result |
|---|---|
| Desk unit tests | **29 passed** |
| Full `tests/pipeline` suite on rebased `main` | **311 passed** |
| Full root `tests` suite | **38 passed** |
| `python3 -m pipeline.validate --site .` | **0 errors** |
| `python3 scripts/validate.py` | **0 errors; 3 pre-existing warnings** |
| Canonical `pipeline.build --out _site` | **92 pages built** |
| `python3 -m pipeline.validate --site _site` | **0 errors** |
| Canonical Chromium suite | **PASS** |
| Isolated Chromium desktop/mobile check | **PASS** |

The isolated browser check exercised the preview redirect, 15 sport cards, 20 match rows, seven books, 59 source rows, source filters, CSV export, mobile navigation, overflow, simulated expiry and no-JavaScript suppression. A screenshot review also caught and corrected reversed KPI labels/values. The canonical browser suite passed its project-subpath, filter, sort, odds-toggle, CSV, deep-link, expiry and no-JavaScript checks.

## Rebuild

```bash
python3 scripts/s5b7d3436_data.py
python3 scripts/s5b7d3436_lines.py
python3 scripts/s5b7d3436_build.py
python3 -m unittest tests.pipeline.test_desk_5b7d3436 -v
```

The data script contains only facts read in this session; rerunning it does not claim a new live fetch or extend the observation expiry.

## Pull request, merge and deployment

- **PR:** [#204 — fresh 15-sport evidence desk with strict release gates](https://github.com/buffedlizard55-lab/OLBG1/pull/204).
- **Merge:** merged at **2026-10-23T21:57:08Z**; merge commit **`41031096cd292aeff57f517ae96882204d1fde09`**, head **`02cd563943fbd5f0d0be9399ef28ecb00c1e0b3a`**.
- **Final local pre-merge repeat:** 328 pipeline tests and 38 root tests passed; both validators returned zero errors, with the same three archived-desk warnings; 2,687 published HTML pages were link-checked.
- **PR checks:** runs `40029671327` and `40029916311` passed. Further rebases were needed only because concurrent main-branch updates repeatedly appended to the coordination board.
- **Superseded run:** main run `40030375574` on the merge commit was cancelled by a newer main push; it was not a test failure.
- **Successful deployment:** [run `40030414514`](https://github.com/buffedlizard55-lab/OLBG1/actions/runs/40030414514) on `74e9d5adeaf69219d7bc8fa3447ec3fc7c0936d8`, which contains the PR #204 merge. Evidence/site/browser job `120677307743` and Pages job `120677959812` both succeeded, completing at **2026-10-23T22:03:09Z**.
- **Live read-back:** the overview, matches, High gate and Flagged for Review pages returned the expected content at `https://buffedlizard55-lab.github.io/OLBG1/5b7d3436/`. The live `summary.json` returned 15 sports, 20 fixtures, 21 markets, zero High picks and 64 findings.
- **Export read-back limitation:** the text-page fetcher returned HTTP 500 for both CSV endpoints while succeeding for HTML and JSON. The same CSVs were present in the tested staged artifact, and the canonical Chromium CSV download passed; this is recorded as a fetch-tool limitation, not misreported as a failed Pages deployment.
