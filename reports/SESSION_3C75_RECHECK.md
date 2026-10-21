# Session `3c7579ed-olbg1` — independent re-check after T20 (task T21)

**Date:** 2026-10-21. **Branch:** `arena/3c7579ed-olbg1`. **Task:** T22 (claim renumbered twice; see §1).

This is a second, independent read of the primary desk, run after session `72198d3e` published T20. It does
not replace T20's register: it corrects what T20 left wrong and discloses what neither pass could confirm.

## 1. Claim collision (disclosed, not hidden)

This session claimed "T17 independent verification" on its own branch at 07:40Z. While the branch was open,
`main` advanced through four merges — `76950c25` (live OLBG re-harvest, T17–T19), `72198d3e` (T20, live
re-verification, PRs #27/#29) and `4f8d032d` (claimed T21, PR #32). The number was therefore taken twice.
Rather than publish a parallel page and a duplicate claim, this session rebased onto `main`, kept those
sessions' register, pages and corrected inputs intact, and reduced its scope to what they had not fixed. The
task is recorded as **T22** in `COORDINATION.md` §1 and the collision is written up in §19.

## 2. What was re-read, and what it settled

| Sport | Official page | Rows | Outcome |
|---|---|---|---|
| Rugby league | [IRL fixtures & results](https://www.intrl.sport/fixtures-results) plus match records 2569, 2570, 2571, 2572, 2573, 2586, 2588 | 7 | Venue and venue-local kick-off confirmed for every tie; stored UTC values match |
| Rugby league | [NRL women's Round 2 draw](https://www.nrl.com/draw/womens-rugby-league-world-cup/2026/round-2/) · [NRL men's Round 2 draw](https://www.nrl.com/draw/rugby-league-world-cup/2026/round-2/) | 7 | Both resolve at their own tournament URL; the stored `competition=175/176` links did not |
| Tennis | [ATP Almaty results](https://www.atptour.com/en/scores/current/almaty/9410/results) · [ATP Lyon results](https://www.atptour.com/en/scores/current/lyon/496/results) | 6 | Round-of-32 winners confirmed; the Round-of-16 pairings cannot be confirmed |
| Snooker | [WST live rankings](https://www.wst.tv/rankings/abfba8fe-1423-5a2a-a96b-d77e8b413ca8?showLive=false) | 2 High inputs | Higgins 6, Williams 8, Bingham 19, Zhang Anda 21, Slessor 23, Jak Jones 24 — all match |
| Darts | [PDC draw release](https://www.pdc.tv/news/2026/october/18/2026-Machineseeker-European-Championship-field---draw-confirmed) | 16 | Still a consent wall; no seed re-read (T20's F-V6 stands) |

Confirmed match times, from the IRL records (venue-local → UTC):

| Fixture | IRL record | Local | UTC |
|---|---|---|---|
| Tonga v Lebanon | 2569 | Fri 23 Oct 20:05, CommBank | 2026-10-23T09:05Z |
| Samoa W v Wales W | 2586 | Fri 23 Oct 17:50, CommBank | 06:50Z (stored 06:45Z — see §3.2) |
| PNG v Samoa | 2570 | Sat 24 Oct 14:25, Port Moresby | 2026-10-24T04:25Z |
| England v France | 2571 | Sat 24 Oct 14:35, HBF Park | 06:35Z |
| Australia W v England W | 2588 | Sat 24 Oct 17:05, HBF Park | 09:05Z |
| New Zealand v Cook Islands | 2572 | Sun 25 Oct 18:05, Christchurch | 2026-10-25T05:05Z |
| Australia v Fiji | 2573 | Sun 25 Oct 19:05, Suncorp | 09:05Z |

## 3. Corrections

### 3.1 RLWC26 source URLs (7 rows)
`nrl.com/draw/?competition=175` (men) and `?competition=176` (women) both render the page at
`competition=131`, the **men's** tournament. The women's rows therefore pointed at the wrong competition and
no row pointed at its own fixture. Each row now cites its tournament's Round 2 draw plus the IRL match
record. `scripts/dataset_rows_b.py` was updated so a rebuild reproduces the fix.

### 3.2 Samoa Women v Wales Women (1 row)
The NRL draw publishes 2:45am AEDT — 06:45Z. The IRL record publishes 17:50 local — 06:50Z. Five minutes,
two governing bodies, no tie-breaker. Both values are now printed on the row; nothing was inferred.

### 3.3 Tennis pairing provenance (11 rows)
Mannarino–Rublev, Tsitsipas–Kukushkin, Duckworth–Darderi, Bonzi–Paul and the other seven pairings are
consistent with the completed Round-of-32 results plus byes (Mannarino d. Vukic 7-6(4) 4-6 6-3, Kukushkin d.
Sakellaridis 7-6(4) 7-6(3), Duckworth d. Kecmanovic 6-4 6-3, Tsitsipas d. Kovacevic 7-6(9) 3-6 6-3, Bonzi d.
Norrie 6-3 3-6 6-3). But the Round-of-16 matches have not been played, so no results feed lists them, and the
draw widgets are client-rendered. Every tennis row now carries a "reconstructed, not draw-verified" flag and
keeps a blank start time. They are **not** claimed as verified.

### 3.4 High-prediction prose (31)
27 of 31 notes ended with `: {selection}`, pasting the price onto the end of the sentence, which produced a
near-identical closer across the corpus. The price is now confined to `bet_line`; the prose keeps the
corrected inputs (Buffalo −7, Philadelphia −19, Boston 3-1-0 at home) and ends on a varied sentence naming
the side. 49–82 words, zero duplicated six-word sequences, and `scripts/validate.py` enforces the 30-word
floor, pick presence and six-gram uniqueness.

## 4. Findings added to the shared register

* **F-V11** — NRL competition-ID redirects (medium, corrected).
* **F-V12** — tennis pairings unconfirmable from any official page (medium, flagged).
* **F-V13** — five-minute RLWC kick-off disagreement (low, disclosed).

These extend `data/verification.json` (rendered on `live-verification.html`) rather than adding a parallel
register: the page now reads 44 confirmed, 19 corrected, 2 flagged, 69 not re-checked.

## 5. Gates

| Gate | Result |
|---|---|
| `python3 scripts/origin_lines.py` | 126 H2H books, 31 predictions |
| `python3 scripts/build_dataset.py` | 134 rows, 126 H2H, 8 field cards |
| `python3 scripts/live_verification.py` | 44 confirmed / 19 corrected / 2 flagged / 69 not re-checked |
| `python3 scripts/build_site.py` | 29 pages at `/` + 29 mirrored in `/f7fa77fc/` (135 validated) |
| `python3 scripts/validate.py` | 0 errors, 0 warnings |
| `python3 scripts/ebfbd966_validate.py` | passed |
| `python3 scripts/final_audit.py` | regenerated (134 rows, 31 high picks) |

## 6. Boundary

No model price, handicap or total was re-derived. 69 rows were not re-opened in this pass and the earlier
passes' named blockers stand for them. Nothing here was inferred, interpolated or filled from memory.
