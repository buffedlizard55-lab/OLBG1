# T21 — Independent second-pass verification of the NHL inputs and the F1 start time

**Session:** `4f8d032d-olbg1` · **Date:** 2026-10-21 (UTC) · **Branch:** `arena/4f8d032d-olbg1`
**Base:** `main` @ `4a3f62a` (after rebasing onto the concurrent T17/T18/T20 work)
**Public register:** [`live-verification.html`](../live-verification.html) · [`data/verification.json`](../data/verification.json)

---

## 1. What this pass adds

An earlier session's T17 re-fetched 62 of the 134 rows and recorded 9 corrections. This session ran a
**second, independent read** of the official endpoints and found that four NHL input sub-values and one
Formula 1 start time were still wrong. It also tested two source URLs that had not been fetched at all.

The earlier session's two deliberate policy decisions were preserved rather than overturned:

- **Boston's home split** had already been corrected (`5-1-0` → `3-1-0`), so it was left alone.
- **Vegas** is treated as a labelled pre-game snapshot: the row keeps `8-2-0 / .800 / W3` and the drift to
  the official `8-3-0 / .727 / L1` is disclosed on the row, in the prediction and in the register. This pass
  **confirmed** that drift but did not re-price the pick, because re-pricing a published selection after
  the fact would be worse than disclosing it.

Consequently the High-pick count stays at **31**, and no prediction was retired.

---

## 2. Evidence (fetched 2026-10-21, 07:20–07:30Z)

Official endpoint: <https://api-web.nhle.com/v1/standings/2026-10-20> (payload generated 2026-10-21T07:05:30Z).

| Fixture | Field | Stored | Official | Reading |
|---|---|---|---|---|
| `nhl-2026020152` | Buffalo goal differential | `+2` | `-7` | club had played the same 9 games → transcription error, not drift |
| `nhl-2026020152` | Philadelphia road line | `0-4-2` | `0-4-1` | same 11 games played → error |
| `nhl-2026020152` | Philadelphia goal differential | `-14` | `-19` | same 11 games played → error |
| `nhl-2026020153` | Ottawa home split | `4-1-0` | `3-1-0` | `homeGamesPlayed = 4`; five home wins from four games is impossible |
| `nhl-2026020154` | Nashville goal differential | `0` | `-1` | same 8 games played → error |
| `nhl-2026020154` | Boston home split | `3-1-0` | `3-1-0` | already corrected by the earlier pass; confirmed here |
| `nhl-2026020160` | Vegas record / streak | `8-2-0, .800, W3` | `8-3-0, .727, L1` | one game played since the snapshot → drift, disclosed, not re-priced |
| `f1-usgp-2026` | Race start | `2026-10-25T20:00Z`, "EDT", "Round 18" | 25 Oct, 56 laps, 16:00 local at COTA = **21:00Z**, no round shown | error |

Formula 1 source: <https://www.formula1.com/en/racing/2026/united-states>. Austin is on CDT (UTC−5) on
25 October, so the stored "16:00 EDT" description and the 20:00Z start were each an hour out.

### Values that checked out unchanged

- **MLB** (4 fixtures): Rays 98-64 (.605), home 55-26 (.679), road 43-38 (.531); Brewers home 55-26 (.679),
  road 48-33 (.593); World Series order and venues (gamePk 849805/849802 at American Family Field,
  849804/849803 at Tropicana Field). Sources: `statsapi.mlb.com` standings and schedule.
- **EHF Champions League** (12 fixtures): every pairing on 21–22 October appears on
  <https://ehfcl.eurohandball.com/men/2026-27/>.
- **NHL**: every other record, points percentage, streak and the six game matchups/start times.

### Sources that failed the check

| Cited URL | What happened | Consequence |
|---|---|---|
| `plusliga.pl/table.html` | redirects to `tauronliga.pl`; returns a generic competition page, not the fixture list | 5 rows stay as published, listed as not re-checked with this blocker named |
| `munster.gaa.ie/fixtures/munster-gaa-fixtures/` | resolved to an April 2025 news post, "Munster GAA Fixtures – April 7th to 12th 2025" | 4 rows stay as published, listed as not re-checked |

AFLW (`afl.com.au/aflw/ladder`) and PDC (`pdc.tv/order-of-merit`) were also attempted. Both are
client-rendered or consent-gated and returned no table; this is now stated in the register rather than
implied.

---

## 3. Changes made

1. `scripts/dataset_rows_a.py` — Buffalo GD, Philadelphia road line and GD, Ottawa home split and Nashville
   GD corrected; each affected row carries a dated re-verification note. Boston's earlier correction kept.
2. `scripts/dataset_rows_b.py` — F1 start corrected to `2026-10-25T21:00:00Z`; "Round 18" removed as not
   displayed by the official page; the "EDT" description replaced with the CDT reasoning.
3. `scripts/live_verification.py` — three new `CORRECTED` entries (`nhl-2026020152`, `nhl-2026020153`,
   `f1-usgp-2026`), a new `f1_usgp` source, sharper blockers for the volleyball and Gaelic football rows,
   and three findings: `FEEDBACK-NHL-INPUTS`, `FEEDBACK-F1-START`, `FEEDBACK-SOURCE-REDIRECT`.
4. `scripts/high_predictions.py` — three affected write-ups updated to the corrected numbers
   (`nhl-2026020152`, `nhl-2026020154`, `nhl-2026020160`), with the Vegas drift disclosed in the prose.

**Register after the pass:** 134 rows — **49 confirmed, 12 corrected, 2 flagged, 71 not re-checked**.

---

## 4. Limits

- This pass re-read **16 fixtures' inputs** in detail (6 NHL, 4 MLB, 12 EHF, 1 F1 overlap) and **attempted
  9 more** that could not be read. The other rows were not fetched by this session.
- It did not re-price anything. Model probabilities still rest on the stored ratings; where a stored rating
  was itself derived from a corrected points percentage, no rating changed.
- No automated freshness monitor exists. A future pass should use per-fixture URLs (not hub pages) and a
  headless renderer for the client-side leagues.

---

## 5. Gates

```
python3 scripts/build_dataset.py       # 134 rows across 17 sports
python3 scripts/live_verification.py   # 134-row register, 12 corrected
python3 scripts/origin_lines.py        # 126 H2H books, 31 high picks
python3 scripts/build_site.py          # 29 pages at / and 29 at /f7fa77fc/
python3 scripts/validate.py            # VALIDATION PASSED — 135 pages, 0 errors, 0 warnings
```
