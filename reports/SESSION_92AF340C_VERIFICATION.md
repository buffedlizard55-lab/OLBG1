# Session `92af340c-olbg1` — verification record (T63 / T35 takeover), 2026-10-22

Research only · 18+ · Do not bet money you cannot afford to lose.

This report records everything session `92af340c-olbg1` read live from official sources on
2026-10-22, what it changed in the repository as a result, and what remains open. Per the
standing brief: no value is inferred anywhere in this session's work — anything that could not
be confirmed against an official source is left blank and flagged. Coordination history
(claims, renumbering, conflict resolutions) lives in `COORDINATION.md` §4 and §48.

## 1. Task identity

| Item | Value |
| --- | --- |
| Session | `92af340c-olbg1` (branch `arena/92af340c-olbg1`) |
| Task board id | **T63** (renumbered T57→T59→T60→T62→T63 across five rebase collisions — T62/§47 was taken by `1a421e41` in PR #94 while this session's work was in flight; every merged row preserved verbatim) |
| Section | **§48** (renumbered §41→§44→§45→§47→§48) |
| Takeover | **T35** — "Re-price the nine AFLW Round 11 rows from the official 2026 ladder after Round 10", queued and unowned since 2026-10-21; taken over per §0.4 and logged in §4. T61 (`6ad5a3a8`, PR #84) had explicitly recorded that its AFLW extraction "did not return usable current facts" and that "T35 prices are not recertified" (`reports/RELEASE_T61.md`). |

## 2. Live official-source reads this session

| # | Read (UTC) | Official source | What it established |
| --- | --- | --- | --- |
| 1 | 2026-10-22 ~07:35Z | AFL official AFLW ladder — https://www.afl.com.au/aflw/ladder?Competition=3&Season=96&Round=1513 | Full 18-club ladder after Round 10, all clubs P=10 (table reproduced in §3). This is the input set for the T35 re-price and the evidence closing finding **T34-01**. |
| 2 | 2026-10-22T08:31Z–09:01Z | All 17 in-scope OLBG hubs, `https://www.olbg.com/betting-tips/{slug}/{id}` | Desk `92af340c` harvest: 130 event cards, per-hub page states, chunk coverage, defect reproductions (§5). OLBG is the reverse-engineering subject, not a pricing source. |
| 3 | 2026-10-22T07:28Z | https://www.olbg.com/betting-tips/Tennis/3 | Confirmed hub URL pattern and card anatomy before the full harvest. |

Earlier-session ledger reads (2026-10-21T07:20Z pass, findings LIVE-F-V1…V7, T41 rows) are
recorded in `reports/LIVE_VERIFICATION.md` and `data/verification.json`; this session ported the
four T41 ledger rows and five T41 registry findings from session `2ca35f17`'s direct-JSON edits
into the generators (`scripts/live_verification.py`, `scripts/build_dataset.py`) so no rebuild can
silently revert them. Ledger standing after this session's pass:
**134 rows — 44 confirmed, 32 corrected, 2 flagged, 56 not re-checked.**

## 3. T35 execution — AFLW re-price from the official ladder

Official afl.com.au ladder after Round 10 (read 2026-10-22; all clubs P=10):

| Pos | Club | Pts | % | W-L-D |
| --- | --- | --- | --- | --- |
| 1 | North Melbourne | 36 | 251.9 | 9-1-0 |
| 2 | Geelong | 36 | 167.2 | 9-1-0 |
| 3 | Melbourne | 32 | 177.2 | 8-2-0 |
| 4 | Western Bulldogs | 32 | 140.9 | 8-2-0 |
| 5 | Gold Coast | 28 | 138.9 | 7-3-0 |
| 6 | Carlton | 28 | 133.0 | 7-3-0 |
| 7 | Sydney | 28 | 112.9 | 7-3-0 |
| 8 | Fremantle | 20 | 104.9 | 5-5-0 |
| 9 | Adelaide | 20 | 102.4 | 5-5-0 |
| 10 | Hawthorn | 20 | 101.5 | 5-5-0 |
| 11 | Port Adelaide | 16 | 78.8 | 4-6-0 |
| 12 | West Coast | 16 | 75.2 | 4-6-0 |
| 13 | Richmond | 16 | 68.9 | 4-6-0 |
| 14 | Brisbane | 12 | 89.7 | 3-7-0 |
| 15 | GWS | 8 | 68.2 | 2-8-0 |
| 16 | Collingwood | 4 | 56.7 | 1-9-0 |
| 17 | Essendon | 4 | 55.6 | 1-9-0 |
| 18 | St Kilda | 4 | 45.1 | 1-9-0 |

Rating mapping (implemented in `scripts/dataset_rows_b.py`, documented in-file):
`base(pts) = round(31 + (pts − 4) × 65 / 36)`; equal-points clubs split by ladder position
(−1 per position step). Input label on every row: *"2026 AFLW R10 ladder (official afl.com.au,
read 2026-10-22)"*.

Superseded inputs (recorded, not silently dropped — full text in `COORDINATION.md` §48) and the
re-priced lines:

| Row | Match | Superseded inputs (pre-T35) | Official inputs (this session) | New line | Tier |
| --- | --- | --- | --- | --- | --- |
| aflw-r11-01 | North Melbourne v Adelaide Crows | NM "1st, 40 pts (10-0)"; ADE "9th, 20 pts (5-5)" | NM 1st 36 pts 9-1-0 251.9%; ADE 9th 20 pts 102.4% | North Melbourne −8.0 @1.41 (−244) | High |
| aflw-r11-02 | Geelong Cats v Fremantle | GEE "13th, 16 pts (4-6)"; FRE "7th, 24 pts (6-4)" | GEE 2nd 36 pts 167.2%; FRE 8th 20 pts 104.9% | Geelong Cats −7.0 @1.40 (−250) | High |
| aflw-r11-03 | Western Bulldogs v Melbourne | WBD "12th, 16 pts (4-6)"; MEL "3rd, 32 pts (8-2)" | WBD 4th 32 pts 140.9%; MEL 3rd 32 pts 177.2% | Western Bulldogs @1.75 (−133) | Low |
| aflw-r11-04 | Carlton v GWS GIANTS | CAR "6th, 24 pts (6-4)"; GWS "16th, 8 pts (2-8)" | CAR 6th 28 pts 133.0%; GWS 15th 8 pts 68.2% | Carlton −10.0 @1.40 (−250) | High |
| aflw-r11-05 | Hawthorn v Essendon | HAW "4th, 32 pts (8-2)"; ESS "14th, 14 pts (3-6-1)" | HAW 10th 20 pts 101.5%; ESS 17th 4 pts 55.6% | Hawthorn −7.0 @1.40 (−250) | High |
| aflw-r11-06 | Gold Coast SUNS v Richmond | GC "18th, 4 pts (1-9)"; RIC "17th, 8 pts (2-8)" | GC 5th 28 pts 138.9%; RIC 13th 16 pts 68.9% | Gold Coast SUNS −5.0 @1.41 (−244) | Medium |
| aflw-r11-07 | Port Adelaide v Collingwood | PORT "11th, 20 pts (5-5)"; COLL "15th, 12 pts (3-7)" | PORT 11th 16 pts 78.8%; COLL 16th 4 pts 56.7% | Port Adelaide −4.5 @1.41 (−244) | Medium |
| aflw-r11-08 | Sydney Swans v West Coast Eagles | SYD "5th, 26 pts (6-3-1)"; WCE "8th, 24 pts (6-4)" | SYD 7th 28 pts 112.9%; WCE 12th 16 pts 75.2% | Sydney Swans −3.5 @1.41 (−244) | Medium |
| aflw-r11-09 | St Kilda v Brisbane Lions | STK "10th, 20 pts (5-5)"; BRL "2nd, 32 pts (8-2)" | STK 18th 4 pts 45.1%; BRL 14th 12 pts 89.7% | Brisbane Lions @1.56 (−179) | Medium |

Knock-on effects, all regenerated through the published pipeline (never hand-edited):
legacy dataset totals **30 High / 30 Medium / 66 Low**, 30 predictions (AFLW High picks 3 → 4),
`v3/` rebuilt (10 High, 24 pages, AFLW Highs r11-06/07/08 in that desk's stricter band) and
`6a081cf6/` rebuilt (9 strict-band picks) — both desk validators PASS. Finding **T34-01 is
CLOSED** with the closure text, ladder evidence and superseded values recorded in the findings
registry (`data/verification.json`) rather than deleted.

## 4. Regime compliance after PR #84 (T61)

PR #84 made the root pages a canonical evidence-first research desk owned by
`scripts/release_build.py` + `data/release/**`, with the legacy primary desk archived under
`archive/pre-release-20261022/` behind a SHA-256 manifest. This session complied strictly:

* The canonical root, `sports/`, `data/release/**` and the archives were **not modified**.
  Pre-PR #88, the 30 conflicting root HTML files were resolved to main's canonical versions during
  the rebase and the canonical pages were restored byte-for-byte after any legacy-pipeline run.
  Post-PR #88 (T257E evidence-first integration) the root is `pipeline/` canonical output and this
  session's final diff touches **no** root `*.html`, `sports/`, `assets/`, `README.md` or workflow
  file; only the legacy `f7fa77fc/` mirror keeps regenerated pages, produced by the preserved
  legacy compiler path (`scripts/build_site.py::_legacy_main`, byte-identical to the pre-#88
  generator — the public entrypoint now delegates to `pipeline.build`).
* `reports/RELEASE_T61.md`'s note that "T35 prices are not recertified" is superseded by this
  report: the AFLW ladder extraction **did** succeed in this session (read #1 above). The
  canonical evidence ledger (`data/release/evidence.json`) was deliberately left untouched —
  ingesting the AFLW facts there requires re-running the T61 gates and belongs to the
  evidence-release owner; recommendation logged in `COORDINATION.md` §48.
* `README.md` keeps T61's structure verbatim; this session added one dated legacy-dataset note.

## 5. Desk `/92af340c/` — harvest and origination

* **Harvest:** all 17 in-scope hubs read live 2026-10-22T08:31Z–09:01Z (chunk 0 of each hub's
  text layer; per-hub chunk coverage and truncated boundary cards disclosed in
  `data/92af340c/harvest/*.json`). 130 event cards captured. Excluded hubs (Football/1, Horse
  Racing/2, American Football/11, Boxing/16, Cycling/17, Specials/18, Hurling/26) were not
  fetched, per the brief.
* **Findings reproduced live:** UTC−4 clock defect (`11:14 Kinsley` rendered `Today 06:14`,
  event 689570 — fresh proof of the BUG-OLBG-CLOCK-EDT family; motor racing renders local track
  time instead); zero-tip blind spots persist on Aussie_Rules/22 (nine official AFLW R11
  fixtures) and eSports/23 (LoL Worlds 2026 Swiss live); GAA date defect still live (event 3536
  shows `01 Nov 10:30` vs official Munster GAA 25 Oct 14:30 UTC); event_id recycling (535918
  carries a different tie than earlier this week); Gaelic hub renders no market labels; OLBG's
  Aussie Rules copy mislabels the women's league "WAFL" and its GF-winners table stops at 2023.
  All nine desk findings with sources: `92af340c/flagged.html`.
* **Origination:** 72 future rows priced from officially-sourced inputs; desk tiers are stricter
  than the root desk's — **High (13)** requires the strict −250..+10000 book window *and*
  measured official ratings both sides *and* a ledger-fresh row (confirmed/corrected ≤48h) *and*
  a hand-authored ≥30-word unique prediction; Medium 37, Low 21; expired 30 and undated 32
  publish untiered. High picks: 4 AFLW (NM −8.0, Geelong −7.0, Carlton −10.0, Hawthorn −7.0),
  3 RLWC26 (Australia −7.5, New Zealand −8.0, England −7.0), 2 World Series (Brewers ML G1+G2),
  Bruins ML, India ML (NZ v India 2nd T20I), Toulouse −7.0, Barça −3.0.
* **Validator:** `scripts/s92af340c_validate.py` PASS (harvest completeness, tier recomputation,
  window arithmetic, 30-word uniqueness, per-row official links, page-link integrity).

## 6. Gate results (final tree, PR #88 canonical regime)

| Gate | Result |
| --- | --- |
| `python3 -m unittest discover -s tests/pipeline` (canonical, PR #88) | 89/89 OK |
| `python3 -m pipeline.build --out _site` + `pipeline.validate --site _site` (canonical) | built 74 pages; snapshot counts identical to PR #88's published figures (108 listings / 25 priced books / 50 markets / 100 outcomes / 23 Low / 0 High); 0 validation errors; every tracked desk staged into the Pages artifact and `archive.html` auto-lists `/92af340c/` ("Preserved 92af340c") |
| `scripts/release_validate.py` (archived T61 gate; manual-dispatch `evidence-pages.yml` only) | FAILED — **identically on this tree and on a pristine `cd97302` worktree** (the same 439 "lacks an official review link" findings against the new canonical root pages): a pre-existing main-side consequence of the PR #88 regime change, not a regression of this session; referred to the T257E owner (§48 request 3) |
| `python3 -m unittest discover -s tests -p 'test*.py'` | 38/38 OK |
| `scripts/validate.py` (legacy whole-site) | PASSED — 0 errors / 3 warnings (all three pre-existing on main: `f7fa77fc/flagged.html` rows 43/45/47 cite the methodology page for internal policy findings) |
| `scripts/release_inventory.py` | refreshed — 1,015 files / 1,094,360 lines / 61,707 source locations |
| `scripts/release_audit.py` + `tests/test_release_audit.py` | regenerated pair (legacy_high 30, approved picks 0) byte-identical to the committed T61 pair — `data/release` untouched; test OK |
| `scripts/v3_validate.py` | PASS — 127 fixtures / 120 priced / High 10 / 24 pages |
| `scripts/s6a081cf6_validate.py` | PASS — 9 strict-band picks, all >70% implied, ≥30 words, sourced |
| `scripts/s92af340c_validate.py` | PASS — see §5 |
| Baseline control | The same gates were run on a clean `origin/main` worktree (`96f5606`) before and after: identical pass state, identical 3 warnings — no gate regression is attributable to this session. |

## 7. Conflict and coordination record

Six renumbering/rebuild collisions — plus a seventh append-only resolution against PR #98's §47 addendum (both texts preserved verbatim, no renumbering) — were absorbed without discarding anyone's work (full logs in §4/§48):
T56–T58/§41–43 (`cccb414e`, `3d2d578a`, `e6716490`; PRs #76–#79), T59/§44 (`7ad0d336`; PR #80),
T60–T61/§45–46 (`8fc47dcb`, `6ad5a3a8`; PRs #82–#89, #84), the post-merge publication records
(PR #90, #91), and finally PRs #92–#97 — in which `1a421e41` merged a desk of its own under
**T62/§47** (PR #94), `f1c13c19` merged its verified desk (PR #92), `8fc47dcb` published its
deployment record (PR #93) and `e6716490` re-read the AFLW ladder for its own namespace (PR #95,
#97) — forcing this session's final renumber to **T63/§48**. Because the fifth collision landed
mid-rebase with generated task-id strings on both sides, the integration was rebuilt
deterministically on the merged main (`1cd02e3`): this session's 117 files restored from its own
tip, all generated id references renumbered (T62→T63, §47→§48) in the generators, and every
derived artifact re-run through the published pipeline — no upstream file was hand-edited.
Immediately after, PR #88 (`257e6674`, **T257E**) merged the evidence-first canonical-regime change
(root = `pipeline/` output, T61 root archived, `build_site.py` delegating to `pipeline.build`, README
rewritten); the sixth collision was resolved by a **second deterministic rebuild** on merged main
`cd97302` — this session's 119 files restored from its own tip, no further renumbering needed
(T63/§48 still free), zero root-file edits, and all canonical gates re-run green (89 pipeline +
38 preserved tests, legacy validate 0 errors / 3 pre-existing warnings, `pipeline.build`/`validate`
0 errors with PR #88's exact snapshot counts, desk validators PASS). The
root-dataset T35 re-price remained unexecuted on main throughout (row `queued` on `cd97302` too), so the takeover
stayed valid; `e6716490`'s PR #95 ladder re-read touched only its own namespace. One cross-namespace edit was made and is
logged: `scripts/v3_prose.py` (owner `6a081cf6` merged as PR #60; `v3_data.py` imports the root
fixtures live, so the T35 re-price changed v3's High set and its prose module had to cover the
new AFLW Highs). After the third collision, every generated reference to this session's task and
section (T60→T63, §45→§48) was corrected in the generators and regenerated — no page or data
file cites the wrong task id.

## 8. Open items (published, not blocking)

| Item | Status | Where |
| --- | --- | --- |
| 56 ledger rows `not_rechecked` (client-rendered official pages; blank-where-unconfirmed policy holds) | open | `reports/LIVE_VERIFICATION.md` |
| 2 ledger rows `flagged` (NHL LIVE-F-V4 family) — excluded from desk High by the freshness gate | open | `data/verification.json` |
| OLBG blind spots (AFLW, LoL Worlds) and clock/date/id defects | upstream, disclosed | `92af340c/flagged.html`, root flagged register |
| AFLW facts not yet ingested into the canonical evidence ledger | re-addressed to T257E's `data/current/` adapter regime (`data/release` is frozen T61 scope) | §48 |
| Companion-bar link to `/92af340c/` on the canonical root | **superseded and withdrawn** — PR #88's `archive.html` auto-lists the desk and the Pages artifact stages it; a dashboard-level link is the T257E integrator's option | §48 |
| Archived `release_validate.py` fails against the new canonical root (439 findings, identical on pristine main) | referred to the T257E owner | §48 |
| 32 undated rows (multi-runner events without official start times) | published untiered | desk + root datasets |
