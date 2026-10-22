# Session `f71557b5-olbg1` — task T54

**Live 22 October 2026 OLBG harvest across all 17 in-scope sports, line-by-line repository audit,
official-source verification, own multi-market line origination, strict −250…+10000 high-confidence
predictions, and a 30-page dashboard at `/f71557b5/`.**

Branch `arena/f71557b5-olbg1`. Claimed 2026-10-22T02:51Z as `T46`, renumbered **T50** at 03:05Z and then **T54 / §39** at 03:45Z
after an identical-scope claim (`T46`–`T49` / `§36` (later merged as `T50`–`T53` / `§38`)) was found on the unmerged branch
`arena/a570c470-olbg1` (`a2bc33a`). Their rows are preserved untouched.

---

## 1. Scope discipline

Everything written by this session is inside its own namespace. No other session's dataset, generator or
page was modified:

| Path | Purpose |
|---|---|
| `data/f71557b5/*.json`, `matches.csv` | harvest, fixtures, sources, coverage, flags, lines, window, audit, highs |
| `scripts/sf71557b5_{data,model,prose,audit,site,validate}.py` | the whole pipeline, reproducible in order |
| `f71557b5/**` | 30 published pages (13 desk pages + 17 sport pages) |
| `reports/SESSION_F71557B5_AUDIT.md` | this file |
| `COORDINATION.md` | append-only: one task row, one §4 entry, one §39 |

Root `index.html`, `scripts/build_site.py`, `scripts/validate.py` and `README.md` were **not** edited.
`arena/26be136b-olbg1` (`42f66c8`) is mid-flight rewriting the entire root dashboard into
`data/final/bundle.json` + `scripts/final_site.py` and archiving the 21 October board, so the single
companion-bar link this desk needs is **requested in `COORDINATION.md` §4** rather than written by hand:

> add one companion-bar entry `f71557b5/index.html` — "f71557b5 · 22 Oct verified desk" — to the generated
> root navigation.

---

## 2. What was harvested and what was verified

All 17 in-scope OLBG hubs were opened live on 2026-10-22 (121 upstream cards counted), plus the NBA,
EuroLeague, EuroCup, WNBA and NHL sub-routes and `sitemap-betting-tips.xml`. A card was only counted as
**verified** once the governing body's own page had been read in this session.

| Sport | OLBG id | OLBG cards | Rows verified | Priced | Outcome |
|---|---|---|---|---|---|
| Tennis | 3 | 21 | 0 | 0 | all five signed supervisor draws show Round of 32 complete — nothing upcoming to source |
| Basketball | 4 | 12 | 7 | 7 | NBA (2) + EuroLeague Round 7 (5); KBL and NBB cards unverified |
| Golf | 5 | 4 | 3 | 0 | three events verified as cards; no entry list, so no outright priced |
| Cricket | 7 | 7 | 4 | 2 | tri-series ODI and 1st T20I priced; two rows verified but one-sided |
| Snooker | 8 | 2 | 8 | 8 | all eight WST Round 3 ties — OLBG lists only two |
| Rugby Union | 9 | 15 | 3 | 3 | three LNR fixtures, each with LNR's own published 3-way probabilities |
| Rugby League | 10 | 3 | 4 | 0 | four RLWC2026 Round 2 fixtures verified; no sourced rating pair, so unpriced |
| Baseball | 12 | 1 | 3 | 3 | World Series games 1–3 from the MLB Stats API |
| Ice Hockey | 13 | 4 | 12 | 12 | the full 12-game NHL slate; OLBG's NHL sub-route is empty |
| Motor Racing | 14 | 3 | 1 | 0 | US GP verified as an event card; no entry list |
| Darts | 15 | 17 | 16 | 16 | all 16 European Championship Round One ties, seeds and Order of Merit |
| Handball | 20 | 18 | 2 | 2 | the two EHF Champions League matches on the official playing-times PDF |
| Volleyball | 21 | 9 | 1 | 0 | one fixture verified; the men's league URL now serves the women's site |
| Aussie Rules | 22 | 0 | 3 | 3 | harvested from AFL.com.au — OLBG's hub is empty during AFLW Round 11 |
| eSports | 23 | 0 | 1 | 0 | Worlds 2026 structure verified; Swiss pairings are drawn on 23 October |
| Gaelic Football | 25 | 6 | 5 | 5 | five county finals with semi-final scores |
| Greyhounds | 28 | 0 | 0 | 0 | verified zero upstream; GBGB unreachable |

**Totals:** 72 rows — 61 with a sourced rating on both sides, 6 published at a neutral baseline under rule 4,
5 event cards — carrying **1,622 originated prices** from **100 official source URLs** read today: 811
market rungs across 60 tips (**15 High / 28 Medium / 17 Low**), 7 no-bet cards and 454 rejected rungs.
Match-winner calls are published separately for all 67 priced fixtures (**3 High / 38 Medium / 26 Low**),
so every match carries the explicit winner pick the brief requires. **19 rows** carry a rule-4 cap because
only one side has a sourced rating.

---

## 3. Resolving the brief's high-confidence contradiction

The brief asks for High picks **above 70%** to win *and* **inside −250…+10000**. Four earlier sessions
recorded the same wall (`F-7A-01`, `T41-01`, `F-6A-04`). The arithmetic:

* at a **5% overround**, 0.700 prices at 1.3606 → **−277**, already through the floor. The two rules are
  unsatisfiable on a margined line.
* at **zero vig**, 0.700 prices at 1.4286 → **−233**, and 0.7143 prices at exactly 1.40 → **−250**. The
  rules are jointly satisfiable in the band **0.700 ≤ p ≤ 0.7143**.

This desk therefore originates at **zero vig** and publishes the 5% book-equivalent beside every price for
comparison only; the window is tested against the fair price. Recorded as **F-F7-01**.

Two further rules keep that band honest:

1. **The tightest qualifying rung wins, not the highest probability.** A 71% call on a 3.5-point handicap is
   a real bet; a 71% call on a 66.5-point alternate is an artefact of the ladder. No model-calibrated
   alternate lines are generated. Rungs outside 5%–95% are dropped entirely.
2. **Rejected Highs are published, not hidden.** 20 fixtures produced a match-winner above 70% whose fair
   price is shorter than −250 — Panathinaikos 0.913 (−1000), Stade Toulousain 0.857 (−588), Barça 0.829
   (−476), India 0.803 (−417), Boston Bruins 0.779 (−357) and 15 more. They appear on
   `f71557b5/window.html` with their prices. These are exactly the "trivial favourite" picks the brief asks
   us not to dress up as high confidence.

### The 15 High-confidence selections (all −233 … −250, all ≥ 70.0%)

| Fixture | Selection | Market | Model | Fair | US |
|---|---|---|---|---|---|
| Devils v Ducks (NHL, 22 Oct) | New Jersey Devils | Match winner | 70.3% | 1.42 | −238 |
| Efes v Besiktas (EL R7) | Besiktas Istanbul +6.5 | Points handicap | 70.9% | 1.41 | −244 |
| Bayern v Dubai (EL R7) | Dubai Basketball +2.5 | Points handicap | 70.0% | 1.43 | −233 |
| Maccabi v Real Madrid (EL R7) | Real Madrid +3.5 | Points handicap | 70.9% | 1.41 | −244 |
| Panathinaikos v Baskonia (EL R7) | Panathinaikos −10.5 | Points handicap | 70.9% | 1.41 | −244 |
| Zonneveld v Menzies (PDC EC R1) | Cameron Menzies +3.5 | Legs handicap | 71.0% | 1.41 | −244 |
| Noppert v Bunting (PDC EC R1) | Danny Noppert | Match winner | 70.9% | 1.41 | −244 |
| Toulouse v Perpignan (Top 14 J7) | Stade Toulousain −6.5 | Points handicap | 70.1% | 1.43 | −233 |
| La Rochelle v Bordeaux (Top 14 J7) | Union Bordeaux-Bègles +5.5 | Points handicap | 70.2% | 1.42 | −238 |
| Barça v Montpellier (EHFCL) | Barça −2.5 | Goals handicap | 70.3% | 1.42 | −238 |
| Sri Lanka v England (ODI tri-series) | England | Match winner | 71.1% | 1.41 | −244 |
| Port Adelaide v Collingwood (AFLW R11) | Port Adelaide −10.5 | Points handicap | 71.3% | 1.40 | −250 |
| North Melbourne v Adelaide (AFLW R11) | North Melbourne −35.5 | Points handicap | 70.6% | 1.42 | −238 |
| Hawthorn v Essendon (AFLW R11) | Hawthorn −21.5 | Points handicap | 71.2% | 1.40 | −250 |
| Rathgormack v The Nire (Waterford SFC final) | The Nire +3.5 | Points handicap | 70.1% | 1.43 | −233 |

Each carries a hand-written preview of **58–81 words**, naming the side, its current form and its recent match
history, with **zero repeated six-word sequences** across the corpus and every factual clause drawn from an
official page read today. Three fixtures also produce a High **match-winner** call outright (Devils,
Noppert, England); the rest publish their match-winner call separately at Medium or Low, so every match
still carries the explicit winner pick the brief asks for.

---

## 4. Markets investigated

| Market | Priced | Where |
|---|---|---|
| Match winner / draw-no-bet | **67 fixtures** (67 markets) | every non-event-card row, including the six published at a neutral baseline |
| Handicap ladders | **63 fixtures** (729 rung markets) | sport-native unit: goals, points, runs, frames, legs. 0.5-step rungs, kept only inside 5%–95% |
| Match totals | **3 fixtures** (15 rung markets) | **MLB only** — the one competition where both clubs' 162-game runs scored and allowed were read on an official page. The 12 NHL games would have been the other; their totals were withdrawn, see §5 |
| Correct score / frame score / set score | 0 | investigated, not priced: format or scoreline distribution not published on a page read today |
| Player props, first try, first touchdown | 0 | investigated, not priced |
| Golf / F1 / eSports outrights | 0 | investigated, not priced: no entry list, qualifying order or drawn pairing published yet |

Every omission names the exact missing official input rather than being filled from a league-average
constant — see finding **F-F7-14** and the per-sport coverage page.

---

## 5. Repository audit — 14 findings, 4 high severity

Computed from tracked files (line numbers printed) or from a disagreement with an official page read today
(URL printed). Full register on `f71557b5/audit.html` and in `data/f71557b5/repo_audit.json`.

| Code | Sev | Finding | Official source |
|---|---|---|---|
| **AUD-F7-04** | HIGH | The root desk still carries a High-confidence **John Higgins −0.5 frame handicap** (`data/predictions.json:351`, `data/fixtures.json:1679`). WST's own Day Four report records **Jak Jones beating John Higgins 4-2** on 21 October, so the market is already decided. | wst.tv |
| **AUD-F7-04** | HIGH | The root desk prices **Luciano Darderi** in Almaty (`data/fixtures.json:1176`, selection at `:1209`). The ATP's Live Race To Turin records "Darderi — Lost to J. Duckworth in the R16". | atptour.com |
| **AUD-F7-06** | HIGH | Two desks publish **England −9.5** as High. The IRL match record shows England **lost 12-30 to Tonga** on 17 October, and no official ranking pair or France Round 1 result exists, so rule 4 refuses the edge here and the fixture is capped at Low. | intrl.sport/match-details/2566 |
| **AUD-F7-07** | MED | **Tonga −2.5** graded High on one-sided evidence: Tonga's 30-12 win is verified, Lebanon's Round 1 result is not published on any official page read today. | intrl.sport/match-details/2569 |
| **AUD-F7-08** | MED | Seven datasets describe overlapping windows with different row counts (root 134, v3 127, 984d417f 145, c17a9192 217, 7a5b5360 32, 6a081cf6 9, this desk 72) and there is still no canonical board. | — |
| **AUD-F7-10** | MED | The generated root `index.html` carries a hand-patched "Latest snapshot" banner; a rebuild of the root desk drops it. Same defect class 2ca35f17 fixed in the generator for `7a5b5360`. | — |
| **AUD-F7-01** | INFO | `README.md:56` claims "160 published HTML pages"; `scripts/validate.py` counts **279** on this commit. | — |
| **AUD-F7-02** | INFO | No `.pyc` artefacts are tracked; all tracked JSON parses. | — |
| **AUD-F7-03** | INFO | `COORDINATION.md`'s header timestamp lags the newest entry in its own body. | — |
| **AUD-F7-05** | INFO | All priced root predictions now sit inside −250…+10000 after the T42 pass. | — |
| **AUD-F7-09** | INFO | Three concurrent sessions were live during this pass (`a570c470`, `9dfd0b48`, `26be136b`); scopes were kept disjoint and the task id was renumbered. | — |
| **AUD-F7-11** | INFO | PR #40 has been open and conflicting since 2026-10-21 and is out of every session's scope. | — |

### Findings about this desk's own inputs (self-audit)

**F-F7-NHL-01 — every NHL goals-for/against value was discarded.** The standings payload was read through a
paginated text extraction. Points, games played, wins, losses and overtime losses reconcile for all 24
clubs used here (`points / (2 × games played)` equals the published `pointPctg`, and `W + L + OTL` equals
games played). Season goals for and against **do not**: the New York Rangers object prints 17 season goals
for alongside 33 in its own last-ten block. Rather than trust some goals values and not others, all were
discarded, the NHL model was rebuilt on points-per-game alone, and **no NHL match total is priced**. A
first pass of this desk did produce two High picks on NHL Under 6.5 totals from those numbers; they were
withdrawn when the reconciliation failed.

---

## 6. Upstream OLBG defects found today

| Code | Defect |
|---|---|
| **F-F7-02** | OLBG lists **21 completed tennis matches as "Tomorrow"**. All five signed supervisor draws read today (ATP Almaty 9410, Lyon 496, Brussels 7485; WTA Ningbo 2092, Osaka 405) show the Round of 32 fully scored, and the ATP Live Race confirms the survivors "will play next in the R16". |
| **F-F7-03** | OLBG's `/betting-tips/Ice_Hockey/NHL/13` sub-route prints **"No tips found"** on a 12-game NHL night; the parent hub shows three SHL games and one Liiga game. All 12 NHL games here were harvested from the league, not from OLBG. |
| **F-F7-04** | OLBG's Aussie Rules hub is **empty during AFLW Round 11**, and its copy calls the women's competition "WAFL" — that is the West Australian Football League; the women's league is AFLW. |
| **F-F7-05** | OLBG's rugby league hub publishes **no RLWC2026 match card at all** mid-tournament — only three 2027 outrights. |
| **F-F7-06** | OLBG lists **two of the eight** official WST Round 3 ties. |
| **F-F7-07** | OLBG prints "TB Rays @ MIL Brewers, 23 Oct 20:00"; the MLB Stats API schedules gamePk 849805 at `2026-10-24T00:00:00Z` with `officialDate 2026-10-23`. OLBG's clock carries no timezone label. |
| **F-F7-08** | OLBG lists "Afghanistan vs Zimbabwe One Day Match, 23 Oct 07:30". The series opens with a **T20I at Sharjah on 27 October** and no board publishes a 23 October ODI. Unverified, unpriced, blank. |
| **F-F7-PDC-CLOCK** | OLBG prints afternoon clocks (13:15–16:45) for European Championship Round One ties that the PDC's own schedule places in a single **1900–2300 CEST evening session** on each day. |

Data conflicts recorded rather than resolved: **F-F7-09** (plusliga.pl now serves the women's TAURON Liga
site, and the same Skra v Projekt fixture appears at both 18:00 and 12:00), **F-F7-10** (formula1.com gives
the championship gap as both 102 and 119 points in two articles published the same day), **F-F7-11**
(maighcuilinn.com gives Dessie Conneely's semi-final tally as 2-14 in the body and 2-16 in the scoring list
on the same page), **F-F7-12** (OLBG tips Kanturk 4/5 against the verified championship record, which has
Éire Óg unbeaten and top of their group).

---

## 7. Gates

```
python3 scripts/sf71557b5_data.py       # 72 rows, 100 official source URLs, 15 register flags
python3 scripts/sf71557b5_model.py      # 1,622 prices, 15 High, 7 no-bet, 454 rejected rungs
python3 scripts/sf71557b5_audit.py      # 14 findings (4 high)
python3 scripts/sf71557b5_site.py       # 30 pages
python3 scripts/sf71557b5_validate.py   # PASS, 0 errors
```

Repository-wide, on the merged tree:

| Gate | Result |
|---|---|
| `scripts/sf71557b5_validate.py` | **PASS**, 0 errors, 30 pages checked |
| `scripts/validate.py` | **VALIDATION PASSED**, 0 errors, 279 pages (6 pre-existing warnings on `flagged.html` / `f7fa77fc/flagged.html`, not authored here) |
| `scripts/v3_validate.py` | PASS, 0 errors |
| `scripts/s6a081cf6_validate.py` | PASS — 9 strict-band picks |
| `scripts/s7a5b5360_validate.py` | PASSED — 14 pages, 0 errors |
| `scripts/s984d417f_validate.py` | PASSED — 145 events, 2,946 links, 0 errors |
| `scripts/c17a9192_validate.py` | PASS — 217 events, 0 broken links |
| `scripts/ccb6bde2_validate.py` | PASSED — 126 matches, 2,031 markets |
| `scripts/ebfbd966_validate.py` | PASSED — 133 matches |
| `scripts/final_audit.py` | exit 0, `reports/FINAL_INTEGRATION_AUDIT.md` regenerated byte-identically |

`git diff --diff-filter=D origin/main` on this branch is empty — nothing owned by another session was
removed or rewritten.

---

## 8. What this desk does not claim

* No validator re-reads the live web. Verification is recorded per row (`status`, `sources`, `evidence`);
  the gate checks structure, arithmetic, provenance and links.
* Prices are model output at zero vig — not market prices, not betting advice.
* Rows whose ratings are one-sided (four RLWC2026 fixtures, two NBA games, the EHF Kolstad tie, Namibia v
  Ireland, Australia Women v New Zealand Women) are published at a **neutral baseline, capped at Low, with
  no High pick**, per repository rule 4. That is a deliberate refusal, not a gap.
* Tennis, golf, Formula 1 and eSports produced **no priced head-to-head** because no official page read
  today publishes an upcoming pairing or a field. Each is recorded with the exact missing input.
