# T41 — High-Confidence Price-Window Compliance

**Session:** `2ca35f17-olbg1` · **Branch:** `arena/2ca35f17-olbg1` · **Baseline:** `f77e14c473496d4e9e891b0aea3abd3ae13367fa` (`main`, PR #45 merged)
**Date of this pass:** 2026-10-22 (UTC) · **Scope:** the root desk only (`/`, `/f7fa77fc/` mirror, `sports/*`). The
namespaced desks published by earlier sessions (`/984d417f/`, `/c17a9192/`, `/ccb6bde2/`, `/docs/`, `/ebfbd966/`,
`/aa4e9dbf/`, `/2360a617/`) are untouched.

---

## 1. The defect this pass was opened to fix

The brief asks for two things about high-confidence picks:

1. they should be picks "that have a greater than 70% chance to win based on market prices"; and
2. they should be for matches priced **between -250 and +10000**.

The inherited snapshot satisfied the first rule and broke the second. Measured on `f77e14c`:

| Measure | Inherited snapshot | Brief requirement |
|---|---|---|
| High-confidence picks | 31 | — |
| Picks priced inside -250…+10000 | **12 of 31** | all |
| Picks priced shorter than -250 | **19 of 31** (−263 to −1250) | none |
| Shortest published high pick | −1250 (Elena Rybakina, 88.2%) | ≥ −250 |

So more than half of the "high confidence" list sat outside the window the brief specifies.

### 1.1 Why the two rules cannot both hold

They are mutually exclusive as literally worded, and this is worth stating plainly rather than papering over:

```
bookmaker decimal price = 1 / (p × 1.05)          # documented 5% overround
p = 0.680  ->  1 / (0.680 × 1.05) = 1.400        ->  -250   (window floor, exactly)
p = 0.700  ->  1 / (0.700 × 1.05) = 1.361        ->  -277   (outside the window)
p = 0.800  ->  1 / (0.800 × 1.05) = 1.190        ->  -525   (outside the window)
```

A 70% chance **is** a price around −277 with vig. Any selection above 68% is therefore *necessarily* shorter
than the −250 floor. There is no probability value that is both ">70%" and "≥ −250".

**Decision taken (documented, not silent):** the window is the explicit numeric instruction, so it is treated as
binding. Confidence keeps its separation role (a match still has to clear the sport's rating-gap threshold), but
the *published selection* is now required to be quoted inside the window at **60%+ model probability**. The
"greater than 70%" reading is retired; the arithmetic above is published on the Methodology page and logged as
finding **T41-01** on the Flagged for Review page.

---

## 2. What changed in the engine (`scripts/model.py`)

1. **Hard window constants** — `HIGH_WINDOW_MIN_AMERICAN = -250`, `HIGH_WINDOW_MAX_AMERICAN = +10000`,
   `CONVICTION_HIGH = 0.60`, plus `american_value()` / `in_high_window()` helpers. Nothing is a comment or a
   convention: the price is converted and compared.
2. **Three-rung handicap ladders** — every fixture now carries a main line (50% cover for the model favourite),
   a 60% rung and a 68% rung, generated in *probability space* (`give = |E[M]| − σ·Φ⁻¹(target)`) rather than by
   arbitrary point steps. After rounding to the nearest half-point, each rung is walked outwards in half-point
   steps until its favourite side is actually quotable inside the window, so a rung cannot land outside by rounding luck.
3. **Three-rung totals ladders** — baseline plus one step either side (step = σ/4, minimum 1.5), anchored on the
   baseline's own over/under probability rather than re-centred on 50%.
4. **Highlight selection rule** — (a) the model's match winner if its own price is inside the window at 60%+;
   (b) otherwise the highest-probability handicap rung inside the window at 60%+; (c) otherwise no highlight and
   the match cannot be High.
5. **Totals are never the highlight.** A totals rung at 68% is an artefact of a modelling constant (e.g. a 228.5
   NBA baseline), not evidence about the teams. Handicap rungs are tied to the sourced rating gap. Totals stay
   published in every match drawer for investigation. This policy is logged as **T41-03**.
6. **Per-row disclosure** — every line now carries a `window` block (`favourite_american`, `favourite_in_window`,
   `pick_in_window`, `conviction_floor`, and a plain-English `reason` naming the tier decision), plus
   `pick_odds`, `pick_american`, `pick_line`, `pick_probability`.
7. **`bet_line` is generated, not typed.** `scripts/origin_lines.py` builds it from the priced selection, so a
   re-price can never leave a stale number in a label (the previous pass maintained a 31-entry hand-written dict
   with prices typed into it).

Result: **126 priced head-to-head matches, 8 markets each** (winner, draw-no-bet where draws apply, three handicap
rungs, three totals rungs), **29 High / 31 Medium / 66 Low**.

---

## 3. The 19 high picks that were repriced into the window

Every one of these keeps the same *directional* view; the vehicle changes from a moneyline that breached the floor
to the handicap rung that carries the same view inside it.

| Match ID | Was (moneyline) | Now published | Price | Model probability |
|---|---|---|---|---|
| `nba-sac-lac-20261021` | LA Clippers (moneyline -333) | LA Clippers -2.0 — Point Spread | 1.40 (-250) | 68.1% |
| `el-535921` | Real Madrid (moneyline -345) | Real Madrid -2.5 — Point Spread | 1.41 (-244) | 67.6% |
| `el-535923` | Panathinaikos (moneyline -455) | Panathinaikos -4.5 — Point Spread | 1.41 (-244) | 67.4% |
| `ten-ningbo-rybakina` | Elena Rybakina (moneyline -1250) | Elena Rybakina -3.0 — Games Handicap | 1.49 (-204) | 63.8% |
| `ten-902093` | Belinda Bencic (moneyline -333) | Belinda Bencic -1.0 — Games Handicap | 1.50 (-200) | 63.6% |
| `snk-higgins-jones` | John Higgins (moneyline -286) | John Higgins -0.5 — Frame Handicap | 1.51 (-196) | 62.9% |
| `pdc-ec-09` | Ryan Joyce (moneyline -263) | Ryan Joyce -0.5 — Legs Handicap | 1.53 (-189) | 62.1% |
| `pdc-ec-12` | Jonny Clayton (moneyline -294) | Jonny Clayton -0.5 — Legs Handicap | 1.47 (-213) | 64.8% |
| `pdc-ec-14` | Wessel Nijman (moneyline -278) | Wessel Nijman -0.5 — Legs Handicap | 1.50 (-200) | 63.5% |
| `cric-ausw-nzw-t20-3` | Australia Women (moneyline -312) | Australia Women -3.0 — Runs/Wickets Handicap | 1.40 (-250) | 68.1% |
| `ru-top14-609567` | Stade Toulousain (moneyline -667) | Stade Toulousain -7.0 — Points Handicap | 1.40 (-250) | 67.8% |
| `rl-wc26-aus-fij` | Australia (moneyline -625) | Australia -7.5 — Points Handicap | 1.40 (-250) | 67.9% |
| `rl-wc26-nzl-cok` | New Zealand (moneyline -667) | New Zealand -8.0 — Points Handicap | 1.41 (-244) | 67.5% |
| `rl-wc26-eng-fra` | England (moneyline -556) | England -7.0 — Points Handicap | 1.41 (-244) | 67.3% |
| `hand-ehf-12044` | Aalborg Håndbold (moneyline -667) | Aalborg Håndbold -4.0 — Goals Handicap | 1.43 (-233) | 66.4% |
| `hand-ehf-12046` | Barça (moneyline -455) | Barça -3.0 — Goals Handicap | 1.45 (-222) | 65.6% |
| `aflw-r11-01` | North Melbourne (moneyline -833) | North Melbourne -10.5 — Points Line | 1.41 (-244) | 67.8% |
| `aflw-r11-04` | Carlton (moneyline -556) | Carlton -7.5 — Points Line | 1.41 (-244) | 67.7% |
| `aflw-r11-05` | Hawthorn (moneyline -769) | Hawthorn -10.0 — Points Line | 1.40 (-250) | 67.9% |

The other ten high picks already sat inside the window on the moneyline (−185 to −238) and kept that selection.

**Two rows were reclassified down, disclosed rather than hidden (T41-04):** `mlb-849803` and `mlb-849804`
(Tampa Bay Rays, −164, 59.3%) were High under the old probability-only rule. They cannot be High now: 59.3% is
below the 60% conviction floor, and their best in-window handicap rung reaches only 54.2%. Both remain fully
priced at Medium with the same −164 moneyline.

---

## 4. Predictions rewritten (29 notes)

All 29 high-confidence picks have a fresh note written for the *new* selection, not the retired moneyline:

* 47–67 words each (minimum required: 30);
* **zero** duplicated six-word sequences across the whole corpus (checked by `scripts/validate.py`);
* zero duplicated sentences;
* every factual clause is drawn from that fixture's stored, source-linked inputs (record, points percentage,
  goal difference, ladder position, ICC/IRL rating, world ranking, tour seed, venue, reverse fixture score);
* the selection is stated in the prose itself (`Selection: Stade Toulousain -7.0`), so the bet is unambiguous
  even with the price stripped out;
* the price never appears in the prose — it lives only in the generated `bet_line`.

No claim about tactics, injuries, line-ups or player form was added, because none of those are recorded in the
verified inputs. That is a deliberate limit, not an omission: inventing a "recent match history" paragraph for a
fixture whose history we never fetched would be exactly the failure mode the brief forbids.

---

## 5. Live reads performed in this pass (2026-10-22)

| Source | URL | What was read | Outcome |
|---|---|---|---|
| WTA signed singles draw, Ningbo 2026 (released 21 Oct 2026 22:13Z) | https://wtafiles.wtatennis.com/pdf/draws/2026/2092/MDS.pdf | `1 1 RYBAKINA, Elena KAZ` with a first-round bye; `4 Q KUDERMETOVA, Polina UZB` beating Bucsa 76(5) 62; `5 BENCIC, Belinda SUI` at rank 12; `Q KAWA, Katarzyna POL` beating Snigur 62 64 | **Confirmed** both tennis round-of-16 pairings, seeds and qualifier status. Also **resolves** the previously logged blocker "WTA draws are client-rendered" (LIVE-F-V7) for this tournament: the signed PDF is machine-readable |
| NHL official standings API | https://api-web.nhle.com/v1/standings/2026-10-21 | `standingsDateTimeUtc 2026-10-22T01:20:45Z`; Boston 7-2-1, .750, 3-1-0 home, +14; Vegas 8-3-0, .727, +14, L1 | **Confirmed** Boston; **confirmed the Vegas drift** already disclosed as F-V5 (8-2-0 / W3 when priced, 8-3-0 / L1 now). No re-price: the pick is a labelled pre-game snapshot |
| PDC European Championship draw release | https://www.pdc.tv/news/2026/october/18/2026-Machineseeker-European-Championship-field---draw-confirmed | Cookie-consent interstitial only, no draw text | **Still blocked** — the previously logged LIVE-F-V6 wall persists on 2026-10-22. All four darts high picks therefore remain `not_rechecked` and are labelled as such |
| EuroLeague game centre | https://www.euroleaguebasketball.net/euroleague/game-center/ | Client-rendered shell | **Still blocked**; the two EuroLeague high picks remain `not_rechecked` |
| EHF Champions League Men 2026/27 standings & calendar | https://ehfcl.eurohandball.com/men/2026-27/standings/ | Calendar listing `Barça v Montpellier Handball`, 22 Oct 2026, 20:45 CET (18:45Z) | **Pairing and start time confirmed** for `hand-ehf-12046`. The group tables for Groups C and E sit deeper in the page and were not re-read in this pass, so the group records keep their 09:05Z verification status |

The register now reads **44 confirmed / 32 corrected / 2 flagged / 56 not re-checked**. The T41 layer is applied by
`scripts/apply_t41_verification.py` so the evidence is reproducible without rewriting the 67 KB generator owned by
another session.

### 5.1 What was *not* re-read, stated plainly

* **Darts (4 rows)** — blocked by the PDC cookie wall (re-attempted today).
* **EuroLeague (2 rows)** — client-rendered game centre.
* **AFLW (3 rows), Top 14, EHF, MLB, NRL/RLWC26, ICC/NZC** — verified in earlier passes at 09:05Z on 2026-10-21;
  not re-fetched today. Their register entries say so.
* **Tennis rankings 103 / 124** (Kudermetova, Kawa) are not printed on the draw sheet; only the pairings, seeds and
  qualifier status were confirmed from it. The row-level ranking figures still rest on the WTA rankings page cited
  in the row, and this report does not claim otherwise.
* No new OLBG harvest was run. The dataset window remains 2026-10-21 → 2026-10-28 from the snapshot at 07:05Z;
  events dated 21–22 October have already started or finished, and prices for them are pre-game snapshots.

---

## 6. Gates run

| Gate | Result |
|---|---|
| `python3 scripts/origin_lines.py` | 126 H2H books, 29 High / 31 Medium / 66 Low, 29 predictions written; aborts if any high pick is out of window |
| `python3 scripts/apply_t41_verification.py` | 4 rows updated, summary recomputed from rows |
| `python3 scripts/build_site.py` | 30 root pages + 30 mirrored pages |
| `python3 scripts/validate.py` | **PASSED** — 0 errors, 4 explained warnings (internal methodology references for T41-01/T41-03) |
| `python3 scripts/ebfbd966_validate.py` | PASSED (133 matches, 18 pages) |
| `python3 scripts/ccb6bde2_validate.py` | PASSED (126 matches, 2,031 markets) |
| `python3 scripts/c17a9192_validate.py` | PASSED (217 events, 1,185 rows, 0 broken links) |
| `python3 scripts/s984d417f_validate.py` | PASSED (145 events, 2,946 links) |
| `python3 scripts/final_audit.py` | PASSED — 134 primary rows, 29 high-pick rows |

New validator rules added for this pass (`scripts/validate.py`):

1. every high-confidence pick must have `pick_in_window == true`;
2. the window block on each line must declare `-250` / `+10000`;
3. the published price converted to American must fall inside the window;
4. the pick probability must be at or above the declared conviction floor;
5. `bet_line` must quote the model's pick and the model's price to two decimals (drift detector);
6. every prediction must be flagged `in_window`.

If a future re-price pushes a high pick back outside the window, the build fails instead of publishing it.

---

## 7. Irregularities flagged for human review

Published on `flagged.html` with links:

| ID | Severity | Finding |
|---|---|---|
| T41-01 | high | The brief's ">70% chance" and "-250 floor" rules are arithmetically incompatible; the window was treated as binding. |
| T41-02 | medium | 19 of 31 inherited high picks were outside the window (−263 to −1250); all repriced onto handicap rungs. |
| T41-03 | low | Totals rungs always offer a ~68% option; they are excluded from highlights because their baseline is a modelling constant. |
| T41-04 | low | Two MLB picks moved High → Medium at 59.3% probability. |
| T41-05 | low | The orphaned `verification.html` advertised 136 lines / 31 picks against a 126/29 dataset; it is now a generated alias page. |

### 7.1 Interpretation choices you may want to overrule

1. **Which way to resolve the contradiction** — I let the price window win and re-based conviction at 60%. If you
   would rather keep ">70% wins" and drop the window for favourites, every affected row can be put back in one
   re-run of `scripts/origin_lines.py`.
2. **Handicap as the vehicle** — a moneyline pick and its handicap rung are the same *view* but not the same *bet*.
   If you want high picks to be moneyline-only, the high set falls to the 10 rows that are already inside the window.
3. **The 60% floor** — it is a judgement call chosen so the ladder rung lands inside the window with a genuine edge.
   It is a single constant (`CONVICTION_HIGH`).
4. **Zero longshot picks** — nothing priced near +500 or +10000 can carry a 60% probability under this model, so the
   upper half of the window is unused. I did not manufacture longshot "high confidence" picks to fill it.

---

## 8. Reproduce

```bash
python3 scripts/live_verification.py        # base register (session 72198d3e)
python3 scripts/apply_t41_verification.py   # T41 evidence layer (this pass)
python3 scripts/origin_lines.py             # market ladders + window filter + predictions
python3 scripts/build_site.py               # 30 pages at / and 30 at /f7fa77fc/
python3 scripts/validate.py                 # must print VALIDATION PASSED
```
