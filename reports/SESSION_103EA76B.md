# Session 103ea76b — 26 October 2026 fifteen-sport desk

Session: `103ea76b-olbg1`. Claim: §98 of `COORDINATION.md`, committed and pushed before any work.

## What was built

A fifteenth-sport desk and its own release gate.

| Item | Value |
| --- | --- |
| Sports captured from OLBG | 15 of 15 |
| Fixtures priced | 33 (NHL 3, MLB 3, NBA 9, EuroLeague 6, EHF Champions League 12) |
| Originated markets | 81 |
| Originated outcome prices | 162 |
| Markets investigated and withheld | 93 |
| Graded picks | 24 — 16 High, 8 Medium, 0 Low |
| Written predictions | 24, 54–80 words each, all naming their selection |
| Sources | 26 (11 official, 15 OLBG listing hubs) |
| Gaps flagged | 20 |
| Repository audit findings | 6 |
| OLBG listings recorded without a price | 26 |

## The rule applied

High = originated probability ≥ 0.60 **and** fair American price inside −250…+10000. Medium = 0.55–0.60.
Nothing shorter than −250 is published, which is the brief's objection to short-priced favourites written as a filter.
The longest price published is −124; the shortest is −236 (70.2%).

## Files

- `scripts/s103ea76b_data.py` — fixtures, sources, models, market origination, pick policy, flags, audit; writes `data/103ea76b/desk.json`.
- `data/103ea76b/prose.json` — the 24 written predictions, keyed by fixture id.
- `scripts/s103ea76b_build.py` — the 25-page desk in `103ea76b/`, plus `103ea76b/data/desk/{desk.json,manifest.json}`.
- `scripts/s103ea76b_validate.py` — the desk gate (provenance, arithmetic, band, prose uniqueness, link and fragment integrity, count reconciliation).
- `pipeline/build.py` — one new `ARCHIVE` row and the front-door banner; the root `index.html` mirror is regenerated from the same build.

## Deviations from `pipeline.validate.validate_desk`, and why

1. **Blank start times are permitted when disclosed.** Fifteen fixtures (nine NBA, six EuroLeague) carry no
   official tip-off time: `cdn.nba.com` returned HTTP 500, and the EuroLeague feed publishes dates, not times.
   Each of those rows carries `start_time_status` and `start_time_note`, and flag F06 records the gap. The
   alternative — converting an OLBG relative clock reading into a UTC time — would have invented a fact.
2. **Both clubs' records are checked directly.** `TEAMS_OK` in `pipeline/validate.py` knows only the NHL and
   MLB tables; this desk also prices EuroLeague, NBA and EHF fixtures, so the gate reads the record object
   stored on each fixture instead of one league table.

Everything else — two-way books summing to one, `fair_decimal = 1/p`, `american_from_prob`, band flag,
confidence tier, ≥30-word prose with no banned words and no shared six-word phrase, official-host source
links on every table row, resolving relative links and fragments, and count reconciliation — is enforced
exactly as the canonical gate does it.

## Gates run

- `python scripts/s103ea76b_data.py` — 33/33 priced, 24 picks, 0 errors.
- `python scripts/s103ea76b_build.py` — 25 pages.
- `python scripts/s103ea76b_validate.py` — 0 errors, 0 warnings.
- `python -m pipeline.validate --site .` — 0 errors.
- `python scripts/validate.py` — 0 errors, 3 pre-existing warnings.
- `python -m pipeline.build --out _site` then `python -m pipeline.validate --site _site` — 0 errors.
- `python -m unittest discover -s tests/pipeline` and `-s tests` — OK.
