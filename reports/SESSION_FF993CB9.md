# Session FF993CB9 (TFF99) — 24 Oct 2026

**Snapshot:** 2026-10-24T22:32Z · **Branch:** `arena/ff993cb9-olbg1` · **Desk:** `/ff993cb9/` ·
**Live after merge:** https://buffedlizard55-lab.github.io/OLBG1/ff993cb9/index.html

## What was delivered

- A clarity-first desk whose first page **is** the executive summary: High table first,
  best-pick-per-sport table second, “where everything is” boxes above both.
- **80 written picks** (3 High / 67 Medium / 10 Low), each with a unique 45–95-word prediction
  naming the selection, across **66 priced matches**, plus **27 tracked no-pick rows** with reasons
  and **14 flagged-for-review items** (F-FF-01…14) with official links for manual review.
- Per-sport picks: Golf 5 · Volleyball 7 · Rugby Union 4 · Cricket 7 · Snooker 2 · Darts 5 ·
  Baseball 6 · Gaelic Sports 5 · Greyhounds 0 (5 meetings tracked) · Tennis 7 · Motor Racing 7 ·
  Handball 5 · Ice Hockey 7 · Basketball 6 · Rugby League 7.
- Markets originated: match winner, handicaps (puck line, points, sets, legs, goals), match/team
  totals, total sets/frames, outrights, podium and top-3/5/6 finishes, draw-no-bet.
- Pages (26): executive summary, all picks, written predictions, every match, our lines
  (both sides of each two-way line), sports index + 15 sport pages, flagged for review, sources
  (36 official pages with UTC read times), method, OLBG route reverse-engineering, repo audit.

## Method in one paragraph

OLBG hubs were read live for discovery only (sport IDs and event routes documented on the
Inside OLBG page). Every fact in every prediction comes from the governing body/league/tour page
linked on its row (NHL, MLB, NPB, NBA, ATP, Volleyball World, Prem Rugby, LNR, ICC, WST, PDC,
GAA counties, Formula 1, MotoGP event, EHF, NRL/RLWC, PGA TOUR, DP World Tour). Prices are
originated fair (no-vig) conversions of probabilities estimated from those official figures.
**High = probability ≥70% AND fair American price inside −250…+10000** (therefore 70.0–71.4%,
i.e. −250…−233); stronger favourites were re-expressed as handicap/team-total lines inside the
window rather than promoted. Anything not read from an official source is blank and flagged.

## The 3 High picks

| ID | Pick | Prob | Fair price |
|---|---|---|---|
| IH-03 | Montreal Canadiens +1.5 goals vs Winnipeg (Heritage Classic) | 70.5% | −239 |
| CR-02 | Netherlands to beat UAE (World Cup League 2, Dubai) | 70.2% | −236 |
| VB-04 | Cucine Lube Civitanova −1.5 sets vs Padova (SuperLega) | 70.3% | −237 |

## Known shortfalls (all on the Flagged page, none blocking)

Greyhounds 0 picks (no official racecard form read); Snooker 2 picks on 1 match (only the final
exists; opponent undecided at snapshot); Rugby Union 4 picks on 2 matches (next block is the
6 Nov Nations Championship, tracked unpriced); Baseball 6 picks across 2 series (Japan Series
Game 1 score not quoted — not on the official pages read); Handball Groups B/D/F unpriced
(table did not render); LPGA not priced (leaderboard not read from lpga.com); OLBG's Basel
listing disagrees with the ATP draw (F-FF-10) — this desk follows the ATP everywhere.

## Verification performed

- `scripts/sff993cb9_validate.py` — PASS (band both directions, ≥30 words, no internal
  vocabulary in predictions, selection named, zero shared 6-grams across 80 predictions,
  official-source-per-row, 26 pages, all internal links/anchors resolve, one `<h1>` per page).
- `python -m unittest discover -s tests/pipeline` — 619 tests OK (incl. 8 new TFF99 tests).
- `python scripts/validate.py` — PASS (3 pre-existing f7fa77fc warnings untouched).
- `python -m pipeline.build --out _site` + `python -m pipeline.validate --site _site` — 0 errors;
  the canonical artifact contains the full `ff993cb9/` folder via one additive `ARCHIVE` line
  in `pipeline/build.py` (declared in §95 of COORDINATION.md, T99D4 precedent).
- Local HTTP smoke test: index and sport pages return 200 with the executive-summary content.

## Files

`ff993cb9/**` (generated site) · `data/ff993cb9/desk.json` + `picks.csv` · `scripts/sff993cb9_data.py`,
`scripts/sff993cb9_data2.py`, `scripts/sff993cb9_build.py`, `scripts/sff993cb9_validate.py` ·
`tests/pipeline/test_desk_ff993cb9.py` · this report · append-only `COORDINATION.md` §95 (renumbered from §93 at rebase) ·
one additive line in `pipeline/build.py` (`ARCHIVE`).
Rebuild any time with `python3 scripts/sff993cb9_build.py`.
