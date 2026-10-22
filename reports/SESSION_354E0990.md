# Session 354e0990 — T354E expiry-aware desk (2026-10-22T12:05Z)

## Scope claimed
Isolated namespace only: `data/354e0990/**`, `scripts/s354e0990_*.py`, `354e0990/**`, this report, append-only `COORDINATION.md` §49. No canonical root, `pipeline/**`, `data/current/**` or other session's files edited.

## What was done
1. Read `COORDINATION.md`, claimed T354E and pushed the claim before implementation (`fd30198`).
2. Re-checked the canonical snapshot (`data/current/snapshot.json`, generated 2026-10-22T10:27:50Z, 108 listings / 24 priced / 49 markets / 98 outcomes / 0 High) at 12:05Z, keeping only fixtures still upcoming and with unexpired evidence for the priced table.
3. Fresh official reads (retrieval tool, 12:01–12:02Z):
   - NHL schedule 2026-10-22 — https://api-web.nhle.com/v1/schedule/2026-10-22 — 12 games, IDs 2026020154–165, all FUT, matching snapshot.
   - NHL schedule 2026-10-23 — https://api-web.nhle.com/v1/schedule/2026-10-23 — found games 2026020166/167 absent from snapshot → flagged F-354-09, not priced.
   - NHL standings 2026-10-21 — https://api-web.nhle.com/v1/standings/2026-10-21 — payload timestamp 2026-10-22T12:01:00Z.
   - MLB schedule — https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-22&endDate=2026-10-29&hydrate=team,venue — 5 World Series games, matching snapshot gamePks/venues/times.
   - EuroLeague Game Center — https://www.euroleaguebasketball.net/en/euroleague/game-center/ — Round 7 clubs present, no cancellation read.
4. Originated/confirmed markets: winner market for all 24 priced matches; MLB handicap (±1.5) and total ladders retained from the sealed Poisson model; NHL/EuroLeague handicap/total/team-total/period markets investigated and **withheld with reasons** (no sealed score distribution) — see `354e0990/markets.html`.
5. Confidence: applied the brief's two rules strictly (>70% AND −250…+10000). **Zero** selections pass both, and evidence-v1.0 is uncalibrated with no sealed player/form/history context, so all 24 selections stay Low, 0 Medium, 0 High. Eight unique ≥30-word hand-written analyses for the nearest candidates are published as Low analyses, each naming its selection and the exact blocking reason — no High prose was fabricated.
6. Built 7-page dashboard at `/354e0990/` (Dashboard, Matches, Markets, Predictions & analysis, Flagged for Review, Methodology, Sources & coverage) plus `data/354e0990/desk.json` + `priced.csv`.

## Key irregularities (all on Flagged page)
F-354-01 zero picks satisfy both brief rules; F-354-02 exactly-70.0% cases (Barcelona, Vegas); F-354-03 Boston −252 misses window by 2; F-354-04 withheld handicap/totals; F-354-05 81 time-unverified listings + Paris–Valencia quarantine; F-354-06 MLB five identical probabilities; F-354-07 darts/greyhounds unverified; F-354-08 evidence expiry; F-354-09 two NHL games missing from canonical snapshot.

## Gates
- `python3 scripts/s354e0990_validate.py` → PASSED (probs sum to 1, fair=1/p, every priced row official https source, predictions ≥30 words, selection named, no shared 6-grams, no broken local links)
- `python3 -m unittest discover -s tests/pipeline` → 95 OK
- `python3 scripts/validate.py` → VALIDATION PASSED (pre-existing warnings only)

## Limits
This desk is an as-of 2026-10-22T12:05Z snapshot. Sealed evidence expires per row (EuroLeague 13:17Z); recheck official sources after expiry. Prices are originated fair prices — no bookmaker quote, availability or edge is claimed.
