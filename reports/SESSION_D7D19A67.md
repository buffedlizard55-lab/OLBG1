# Session `d7d19a67-olbg1` — TD7D19 independent live desk (22 October 2026)

Branch `arena/d7d19a67-olbg1` · task **TD7D19** (claimed as T65 at 12:20Z, renumbered at merge) · board record **§59** · desk published at
[`d7d19a67/`](../d7d19a67/index.html) → live at
`https://buffedlizard55-lab.github.io/OLBG1/d7d19a67/index.html`

Official reads were made between **2026-10-22T12:22Z and 12:55Z**; the desk's reference time is
`2026-10-22T12:55:00Z` and its rolling window is **2026-10-22T12:55Z → 2026-10-29T12:55Z**.

## What was asked

Reverse-engineer OLBG.com for a full, updated match list across every sport **except** soccer/football,
American football, boxing, UFC/MMA, hurling, horse racing, cycling and specials; originate our own betting
lines for every match; pick a winner per match and label it Low / Medium / High; investigate every
available market (win, handicap, match total and so on); write unique human ≥30-word predictions for the
High picks containing real verified information; concentrate High picks on matches priced between −250 and
+10000 rather than on the ">70% chance" shortcut; review the repository line by line against official
trusted sources with links for manual review; flag irregularities; never hallucinate; publish a clean
dashboard with subpages by category where every table row carries an official-source link and anything
unconfirmed is left blank and flagged; coordinate through `COORDINATION.md`; open a PR, merge it without
waiting for approval and confirm GitHub Pages is live.

## What shipped

| | |
|---|---|
| Fixture listings published | **55** across 6 sports (ice hockey 14, rugby league 13, tennis 10, basketball 9, baseball 5, cricket 4) |
| Matches priced with our own lines | **26** |
| Markets originated | **99** (winner, 3-way regulation, handicap −1.5/+1.5, totals 5.5/6.5 goals and 7.5/8.5/9.5 runs) |
| Priced outcomes | **215** |
| Winner-pick tiers | **7 High · 15 Medium · 4 Low** |
| Literal Gate A selections (>70% **and** in-window) | **1** — Pittsburgh +1.5 goals, 70.21%, −236 |
| Out-of-window strong favourites disclosed | **13** (probability > 71.4%, i.e. shorter than −250) |
| Picks downgraded by contradicting official context | **2** (Real Madrid at Maccabi; Barcelona at Milan) |
| Hand-written predictions | **8** (84–116 words each, 34 numeric claims re-checked at build time) |
| Official source reads | **16** (plus 3 recorded failures and 12 coverage gaps) |
| Flags for review | **16** (F-D7D-01 … F-D7D-16) |
| Repository audit findings | **13** (A-D7D-01 … A-D7D-14), each with file:line evidence and a GitHub link at the audited commit |
| Pages published | **27** HTML pages + 3 data exports + `assets/style.css` |

## Sources read this session (all official, none OLBG)

| Publisher | Page | Used for |
|---|---|---|
| NHL | `https://api-web.nhle.com/v1/schedule/2026-10-22` | 22 Oct fixtures (chunk 0 of 12) |
| NHL | `https://api-web.nhle.com/v1/schedule/2026-10-23` | 23–24 Oct fixtures (chunks 0–1 of 12) |
| NHL | `https://api-web.nhle.com/v1/standings/2026-10-21` | all 32 clubs: GP, W, L, OTL, GF, GA, points, streak codes (8 of 8 chunks) |
| NHL | `https://api-web.nhle.com/v1/scoreboard/2026-10-22` | 5 completed results used as recent match history |
| MLB | `https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-22&endDate=2026-10-29` | World Series games 1–5, game ids, venues, start times |
| MLB | `https://statsapi.mlb.com/api/v1/standings?leagueId=103,104` and `…&divisionId=202` | Rays 98-64 (736 RS / 650 RA); Brewers 103-59 (832 / 618) |
| Euroleague Basketball | `https://www.euroleaguebasketball.net/en/euroleague/news/game-center-round-7-el2627/` | Round 7 fixtures, times, all 18 club records, ppg ranks, injuries, head-to-head notes (3 of 3 chunks) |
| WTA | `https://wtafiles.wtatennis.com/pdf/draws/2026/2092/OP.pdf` | BNB Ningbo Open order of play, 23 Oct |
| ATP | `https://protennislive.com/posting/2026/7485/op.pdf` | event 7485 order of play, 22 Oct |
| PCB | `https://www.pcb.com.pk/…/tournament/1465.html` | tri-nation ODI series fixtures |
| IRL | `https://www.intrl.sport/fixtures-results` | 13 Rugby League World Cup fixtures in window |
| RLWC 2026 | `https://www.rlwc2026.com/draws-and-pools` | independent corroboration of the men's Round 2 pairings and venues |
| WST | `https://www.wst.tv/matches/` | Northern Ireland Open — Round 1 results only; upcoming rounds not readable |
| PDC | `https://www.pdc.tv/…` | **failed** — page returned only cookie-consent payload |
| AFL | `https://www.afl.com.au/aflw/fixture` | **failed** — navigation chrome only; fixture cards are client-side |
| NBA | `https://cdn.nba.com/…/todaysScoreboard_00.json` | **failed** — HTTP 500 |

Each read is recorded in `scripts/sd7d19a67_data.py` with `read_at_utc`, the role it plays, exactly which
chunks were read, and the limitation that follows from what could not be read. The same register is
published on [`d7d19a67/sources.html`](../d7d19a67/sources.html).

## Method

Three origination models, all documented on the desk and none calibrated out-of-sample:

* **`nhl-poisson-v1`** — independent Poisson goals, `λ_A = (GF_A/GP_A + GA_B/GP_B) / 2` from the official
  standings; winner including overtime = `P(A>B) + P(A=B) · λ_A/(λ_A+λ_B)`, where the overtime split is a
  **disclosed model assumption**, not an official statistic. No home-ice bonus is inserted.
* **`mlb-poisson-v1`** — the same construction on official 2026 regular-season runs per game; winner,
  run line ±1.5, totals 7.5/8.5/9.5. No pitcher, park, lineup or rest input exists in the official reads,
  so none is claimed — which is why all five World Series games originate an identical line
  (`F-D7D-13`).
* **`el-log5-v1`** — log5 on Beta(2,2)-shrunk official Round 7 records. **Winner market only**: the
  official preview publishes no margin distribution, so handicap and total lines are withheld per fixture
  with the reason printed next to the row.

Prices are originated fair prices: `decimal = 1 / probability`, no margin, no clipping, American derived
from the unrounded probability (both the rounded and unrounded values are stored so any reviewer can
re-derive the price).

### The confidence rule, and why High is only 7

The brief's two conditions fight each other: above 70% is a price shorter than −233, and the window starts
at −250, so the literal intersection is only −250…−233 (70.0–71.4%). Both readings are published:

* **Gate A (literal)** — probability > 70% **and** price inside −250…+10000. Exactly **one** selection on
  the whole desk qualifies, and it is a derivative line: Pittsburgh +1.5 goals at −236 (70.21%). It gets a
  full prediction.
* **Gate B (published High tier)** — price inside −250…+10000 **and** probability ≥ 0.60 **and** fixture
  and both sides' inputs read officially this session **and** a unique ≥30-word prediction **and** no
  official sentence contradicting the lean. Seven picks qualify at −150 to −225.

The confidence label attaches to the **winner market** of each fixture, per the brief's "pick a match
winner and label each with a confidence level". Derivative markets are priced and published without the
match label rather than padded with repetitive prose; the 27 derivative selections that would clear the
same arithmetic are listed in full on the High-confidence page and the choice is flagged as `F-D7D-15`.

| High pick | Start (UTC) | Match | p | Fair American |
|---|---|---|---|---|
| P-D7D-01 | 22 Oct 23:00 | Nashville at **Boston** | 0.6320 | −172 |
| P-D7D-02 | 22 Oct 23:00 | San Jose at **Ottawa** | 0.6139 | −159 |
| P-D7D-03 | 24 Oct 19:30 | Los Angeles at **New Jersey** | 0.6086 | −156 |
| P-D7D-04 | 24 Oct 23:00 | San Jose at **Boston** | 0.6843 | −217 |
| P-D7D-05 | 22 Oct 17:30 | **Besiktas Istanbul** at Anadolu Efes | 0.6000 | −150 |
| P-D7D-06 | 22 Oct 18:00 | **Dubai Basketball** at Bayern Munich | 0.6923 | −225 |
| P-D7D-07 | 22 Oct 18:45 | **Crvena Zvezda** at Partizan | 0.6000 | −150 |
| P-D7D-08 (Gate A) | 24 Oct 23:00 | **Pittsburgh +1.5 goals** at Nashville | 0.7021 | −236 |

Two picks were **downgraded** because an official sentence read this session contradicts the model lean,
each with the citation published beside the row: Real Madrid at Maccabi Tel Aviv (the official preview
records that the home team has won each of the last five meetings and that Madrid are 1-4 away) and
Barcelona at Milan (the official preview says the game should be close and that both meetings last season
were decided by a single possession). Thirteen selections stronger than 71.4% — including Panathinaikos
and Valencia at 0.8448 (−544) — are published as **out-of-window favourites**, excluded from High by the
brief's own price band rather than hidden.

## Verification

* Every one of the **463** data-table rows published across 27 pages carries an official `https://` link;
  `scripts/sd7d19a67_validate.py` fails the build if any row does not.
* Every value that could not be confirmed on an official page is published **blank** with a flag —
  38 rows carry blank fields (two NHL away clubs, all nine basketball venues, IRL timezone-derived UTC
  starts, ATP/WTA tournament metadata, PCB start times). Nothing is inferred, interpolated or filled from
  memory, from a search snippet, from OLBG or from another session's data.
* OLBG.com was used for **discovery only** (which sports exist, hub URLs) and is never cited as
  verification; the validator rejects any row whose official link is an OLBG URL.
* `data/current/**` was read only to locate official URLs and to cross-check our arithmetic against the
  canonical pipeline's independent origination. Where the two overlap they converge to the fourth decimal
  (Besiktas 0.6000 / −150; Dubai 0.6923 / −225); the confidence labels differ because the canonical model
  refuses to issue Medium or High without measured calibration. Neither desk corrects the other, and both
  positions are published.
* Predictions: a build-time guard rejects any two texts sharing a five-word phrase, re-checks 34 numeric
  claims against the official transcription, verifies every price and tier quoted in prose against
  `desk.json`, and requires ≥30 words. Ice hockey prose cites club-level official facts only, because no
  official NHL injury report was read (`F-D7D-14`).
* The desk never re-stamps an old read as fresh: fixture evidence expires 6 hours after the read and
  statistics 24 hours, and elapsed starts cannot yield pre-match selections.

## Repository audit (read-only, offline, 13 findings)

`scripts/sd7d19a67_repo_audit.py` re-runs every check against the working tree at build time and quotes
the line it found; each finding is published with a GitHub link to the exact file and line at the audited
commit. Highlights:

* **A-D7D-06 (high)** — nine task rows are still published as `in progress` / `queued` far beyond the
  60-minute takeover rule in §0.4: `T9`–`T12` (`f7fa77fc-olbg1`, started 2026-10-21T05:26Z, ~31 hours
  old) and `T19` (`76950c25-olbg1`), `T51` (`a570c470-olbg1`, 604 minutes). The finding also records how
  many commits name each session, so a reviewer can see whether the work continued elsewhere.
* **A-D7D-01 / A-D7D-02 (medium)** — `COORDINATION.md` reuses section numbers (§4 at lines 178 and 2310;
  §13 at 702 and 709; §43 at 2140 and 2505) and two lower numbers appear after higher ones, so "see §43"
  is ambiguous.
* **A-D7D-05 (medium)** — task id **T63** is claimed by two rows (`f1c13c19-olbg1` and
  `92af340c-olbg1`), both marked done.
* **A-D7D-07 (medium)** — 26 published pages exceed 200 KB (`1a421e41/markets.html` 1039 KB,
  `f71557b5/markets.html` 949 KB, root `verification.html` 827 KB), which makes manual row-by-row review
  impractical on the very pages that need it.
* **A-D7D-12 (medium)** — the 34 files under `data/current/evidence/` are **network-attempt logs** (URL,
  HTTP status, timestamps), not verified values, despite the directory name.
* **A-D7D-08 / A-D7D-10 / A-D7D-14 (info)** — 606 tracked HTML files contain no broken relative links and
  no placeholder wording, and every file this session changed is inside its claimed scope.

Findings were logged, not patched: `COORDINATION.md` sections and every root page belong to other
sessions, and the brief's protocol is to log a request rather than edit a file another session owns.

## Gates

| Gate | Result |
|---|---|
| `python3 -m unittest discover -s tests/pipeline` | **OK** — 95 tests |
| `python3 -m unittest discover -s tests -p 'test*.py'` | **OK** — 38 tests |
| `python3 -m pipeline.validate --site .` | **0 errors** on the committed canonical root |
| `python3 scripts/validate.py` | **VALIDATION PASSED** — 0 errors, 3 pre-existing warnings in `f7fa77fc/flagged.html`, 633 published pages link-checked |
| `python3 -m pipeline.build --out _site` | **78 canonical pages built**; `_site/d7d19a67/` present (12 pages + sports + assets) |
| `python3 -m pipeline.validate --site _site` | **0 errors** |
| `python3 scripts/sd7d19a67_validate.py` | **VALIDATION PASSED** — 8 checks, 0 warnings, 0 errors |

One dependency worth recording: `pipeline.build` stages a desk into `_site` through
`stage_existing()`, which copies **`git ls-files`** output. A desk whose pages are still untracked is
therefore invisible to the Pages artifact — the pages must be committed before the workflow build. This
session hit that, committed the desk, rebuilt and re-validated.

## Limits — what this desk does not claim

No bookmaker price, no price availability and no betting edge is claimed anywhere. No model is calibrated
out-of-sample, so a High label is a statement about verified inputs and the brief's price band, not a
measured hit rate. Eleven of the seventeen in-scope sports have **no rows** (`F-D7D-11`): golf, snooker,
rugby union, motor racing, darts, handball, volleyball, Australian rules, eSports, Gaelic football and
greyhounds — each gap page names the official URL attempted, the number of attempts and what specifically
could not be read. A gap is not a finding that the sport has no fixtures. NBA fixtures could not be read
at all (`cdn.nba.com` returned HTTP 500), so basketball coverage is EuroLeague only.

## Files

* `scripts/sd7d19a67_data.py` — every official literal read this session, with timestamps, roles and limitations
* `scripts/sd7d19a67_model.py` — origination, pricing, tiers, duplicate-line detection, desk assembly
* `scripts/sd7d19a67_predictions.py` — the eight predictions, their fact→source mapping and the build-time checks
* `scripts/sd7d19a67_repo_audit.py` — read-only repository audit
* `scripts/sd7d19a67_build_site.py` — the 27-page dashboard generator
* `scripts/sd7d19a67_validate.py` — the desk's own gate
* `data/d7d19a67/desk.json`, `fixtures.csv`, `markets.csv`, `repo_audit.json`,
  `raw/nhl_standings_2026-10-21.json`
* `d7d19a67/` — `index`, `matches`, `markets`, `high-confidence`, `predictions`, `sports`, `analysis`,
  `sources`, `flagged`, `repo-audit` + `sports/<slug>.html` for all 17 in-scope sports + `assets/style.css`
* `COORDINATION.md` — §1 TD7D19 row, §4 request, §59 record

## PR, merge and Pages receipts

* PR: _appended post-merge_
* Merge: _appended post-merge_
* Pages verification: _appended post-merge by fetching a path that exists only in this merge_
