# Session `8fc47dcb-olbg1` — T57 fresh 22-Oct future-only desk

**Cutoff:** 2026-10-22T07:30:00Z · **Desk:** https://buffedlizard55-lab.github.io/OLBG1/8fc47dcb/
**Scope (non-overlapping):** `8fc47dcb/**`, `data/8fc47dcb/**`, `scripts/s8fc47dcb_*.py`, this report, append-only `COORDINATION.md` (§42), plus one additive companion link line in `scripts/build_site.py` at final integration (+1 generated line × 61 root/mirror pages). No other session's data, generator or pages were edited; `data/fixtures.json` was read-only input. Open PRs #40, #63, #76 were not touched (note: PR #76 also labels itself “T56”, which was already taken by `cccb414e` PR #74/#75 — this session therefore claimed **T57**).

## What was done, against the brief

1. **Reverse engineer OLBG.com.** Re-read `https://www.olbg.com/sitemap-betting-tips.xml` live on 2026-10-22: all 17 in-scope hubs still publish with the committed sport IDs (Tennis/3, Basketball/4, Golf/5, Cricket/7, Snooker/8, Rugby Union/9, Rugby League/10, Baseball/12, Ice Hockey/13, Motor Racing/14, Darts/15, Handball/20, Volleyball/21, Aussie Rules/22, eSports/23, Gaelic Football/25, Greyhounds/28); excluded per brief: Football/Soccer (1), Horse Racing (2), American Football (11), Boxing/UFC-MMA (16), Cycling (17), Specials (18, unlisted), Hurling (26, unlisted). Read the live Basketball hub end-to-end: cards carry pairing, competition sub-route, an unlabelled local-clock start, tipster selection, market name (“Money Line”) and win-tips consensus (e.g. `event_id=535921` Maccabi Tel Aviv vs Real Madrid “Today 14:05”, 4/6 = 67%). Published at `8fc47dcb/reverse-engineering.html`. OLBG values verify no sporting fact on this desk.
2. **Full updated match list.** Primary 134 rows re-cut: **73 dated future** (72 two-sided priced + 1 event card), **29 expired**, **32 undated** (tennis 11, snooker 11, cricket 5, golf 4, eSports 1 — no official start recorded, so not listed as upcoming). Expired/undated rows are published on Flagged for Review, never silently dropped.
3. **Own lines for every match + winner call + confidence.** Reused the root model's published constants, extended the handicap ladder to 50/60/70/80% half-point rungs and totals to 5 rungs, priced at **fair (0%) odds with the 5%-vig equivalent printed**. Every priced row states a match-winner call. Markets investigated but not priced (correct score, player props, period sub-markets, unsupported totals) are named per row with the missing official input. Tiers: **7 High / 34 Medium / 31 Low**.
4. **High = >70% inside −250…+10000, enforced exactly.** High requires: verified status, measured ratings both sides, two-way win probability ≥60% (no manufactured plus-handicap Highs), exact selected-line probability **70.00%–71.4286%** at fair odds **1.40–101.00**, and an in-session official-page re-read. Panathinaikos (71.5% rung) and England RL (71.7%) were *rejected* by the exact-probability ceiling despite rounding to 1.40 — both sit at Medium with the reason printed.
5. **Predictions.** 7 original hand-written previews (58–97 words, 0 shared 6-grams), each naming team, current form and the exact selection, built only from facts read today. No prices inside prose.
6. **Site.** 21 clean pages: landing KPIs, all-picks table with expandable market books, predictions, 12 sport subpages, methodology (full window arithmetic), reverse-engineering, sources register, line-by-line verification register, Flagged for Review.

## The 7 strict High picks (all re-verified in-session)

| Start (UTC) | Selection (market) | p | Fair | US | Winner call | Official page read |
|---|---|---|---|---|---|---|
| 2026-10-22 18:45 | SC Magdeburg -1.5 (Goals Handicap) | 71.4% | 1.40 | -250 | SC Magdeburg | EHF standings |
| 2026-10-22 23:00 | Boston Bruins +0.5 (Puck Line) | 70.5% | 1.42 | -238 | Boston Bruins | NHL schedule + standings APIs |
| 2026-10-22 23:00 | Florida Panthers +0.5 (Puck Line) | 71.2% | 1.41 | -244 | Florida Panthers | NHL schedule + standings APIs |
| 2026-10-23 09:05 | Tonga -10.5 (Points Handicap) | 70.1% | 1.43 | -233 | Tonga | IRL rankings + NRL draw |
| 2026-10-24 09:05 | Australia Jillaroos -15.5 (Points Handicap) | 71.2% | 1.40 | -250 | Australia Jillaroos | IRL rankings + NRL women's draw |
| 2026-10-24 14:35 | Aviron Bayonnais +1.5 (Points Handicap) | 71.2% | 1.40 | -250 | Aviron Bayonnais | LNR Top 14 classement J6 |
| 2026-10-25 09:05 | Australia -17.5 (Points Handicap) | 70.7% | 1.41 | -244 | Australia | IRL rankings + NRL draw |

## Corrections found by today's re-read (priced only on this desk; root data untouched)

- **EuroLeague records wrong/stale:** Real Madrid stored 4-2 → official **3-3**; Panathinaikos 4-2 → **5-1**; Baskonia 2-4 → **1-5**. Ratings (official win%) corrected and re-priced. Anadolu Efes v Besiktas had no ratings; official win% added.
- **Vegas Golden Knights** stored .800 (8-2-0, W3) → NHL standings 2026-10-20 now returns **.727 (8-3-0, L1)**; corrected (root already disclosed drift).
- **IRL world ranks superseded:** Lebanon men stored No. 11 → live **No. 23**; France men No. 8 → **No. 11**; Cook Islands No. 9 → **No. 8**; Wales Women No. 7 → **No. 9**; England Women No. 2 → **No. 3**. Ratings for all 7 future RL rows redefined as the official IRL ranking % and re-priced.
- **EHF:** Montpellier Handball are 4th, not 3rd (record/pts/GD stored correctly); MT Melsungen are 2-0-2 (4 pts), not 1-0-3 (2 pts).
- **ICC women's T20I points:** Australia 287→**292**, New Zealand 253→**248** (ranks unchanged; model ratings retained, disclosed).
- Confirmed exactly: Boston Bruins/Nashville Predators, Pittsburgh Penguins/Florida Panthers, Toronto Maple Leafs/New York Rangers points percentages; SC Magdeburg/Kolstad Håndball, Barça, OTP Bank-Pick Szeged/GOG records; Top 14 J6 positions/points for Toulouse, USA Perpignan, Bayonne, LOU, La Rochelle, Bordeaux; ICC men's T20I points (NZ 247, India 267); NZC fixtures (Australia Women v WHITE FERNS 3rd T20I North Sydney Oval 22 Oct; BLACKCAPS v India 2nd T20I Hagley Oval 24 Oct).

## Not re-checked — blockers named, capped below High

- **Darts (16 rows):** PDC page returned only its consent wall in all 7 fetched chunks.
- **AFLW (9 rows):** official ladder is client-rendered (no rows in either fetched chunk); root finding F-T34-01 unresolved. (T35 re-price therefore remains open — not attempted on invented ratings.)
- **Sporting CP v IFK Kristianstad:** EHF table read, but no rating exists and no handball rating formula is published; left unrated rather than invented.
- Remaining future rows (baseball, volleyball, Gaelic football, URC/Premiership, F1 card) keep their recorded governing-body sources as a dated snapshot; this is stated per row.

## Other irregularities flagged (on Flagged for Review)

- OLBG card clocks carry no timezone (EDT display vs official UTC tip-offs) — with today's two worked examples.
- Root desk's expired Buffalo prediction says “fourteen-goal swing” against its own −7/−19 inputs (12) — flagged for the root owner; no live pick affected.
- Every corrected/not-rechecked/expired/undated row (100+ items) with official links.

## Gates

- `python3 scripts/s8fc47dcb_validate.py` → **PASSED** (73 rows, 72 priced, 7 High, 7 predictions, 21 pages, 0 broken links)
- `python3 scripts/validate.py` (whole repo) → **PASSED**, 0 errors, 6 pre-existing warnings
- Parallel validators (`sf71557b5`, `v3`, `sa570c470`, `s984d417f`, `c17a9192`, `ccb6bde2`, `ebfbd966`, `s7a5b5360`, `s9dfd0b48`, `s6a081cf6`) → all PASSED; `tests/` 5/5 OK.

## Sources read this session (official only)

NHL `api-web.nhle.com/v1/schedule/2026-10-22`, `…/v1/standings/2026-10-20` · EuroLeague standings · EHF CL standings · LNR `top14.lnr.fr/classement` · IRL `intrl.sport/world-rankings` · NRL RLWC26 men's/women's Round 2 draws · ICC rankings · NZC `scoring.nzc.nz/fixtures` · OLBG sitemap + Basketball hub (taxonomy/observation only). Full register: `8fc47dcb/sources.html`; per-row evidence: `data/8fc47dcb/verification.json`.

Prices are model output, not betting advice.
