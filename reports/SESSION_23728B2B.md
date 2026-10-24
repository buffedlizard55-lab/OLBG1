# SESSION 23728B2B — 24 October 2026 OLBG research desk

## Scope and snapshot

- Branch: `arena/23728b2b-olbg1`; desk claim: `T23728B2B`.
- Research cut-off: **2026-10-24T17:56:39Z**. Events were upcoming at that cut-off unless expressly excluded or withheld. This is not a live tracker; Ospreys–Dragons is specifically time-sensitive.
- Exactly 15 requested sport pages.
- 55 official-source fixture rows: **53 priced**, one withheld darts pairing, and one rugby-league official-context row.
- **138 independently originated lines**: 53 primary selections and 85 alternatives.
- **Seven High selections**, 42 Medium and four Low among primary selections.
- **63 source records**: 48 official sporting sources and 15 discovery-only OLBG hubs.
- **19 Flagged for Review items**.

## Evidence and price policy

OLBG is used only for discovery and market context. Official leagues, governing bodies, clubs and tours substantiate sporting facts. Every fixture and every rendered match/ladder table row has an official review link. Unsupported CSA, Swiss NLA, Pato–Botafogo and Toronto Kings–Vancouver Guardians discoveries are excluded and disclosed.

Prices are independently calculated from editorial probabilities: decimal = `1 / p`; American = `100 × (decimal − 1)` at decimal 2.0 or higher, otherwise `−100 / (decimal − 1)`. Display rounding is half away from zero. No bookmaker quote is represented as an originated line. High requires probability strictly above 70% and an unrounded fair American price from −250 through +10000. Higher-probability selections outside that window remain Medium.

Every primary prediction is unique and at least 30 words. High prose also passes a repeated-six-word-phrase check, explicit-selection check, both-side evidence check and banned-vocabulary check.

## Material corrections and evidence limits

- The motor event is the **United States Grand Prix**, not Mexico.
- Live Anaheim–Philadelphia and the removed Ratajski–Doets darts listing are excluded.
- Price–Bunting remains withheld until official second-round qualification is established.
- CSA's current pagination does not substantiate the two 25 October domestic listings; team naming remains unresolved.
- USA–Australia A has conflicting official kick-off publications, so exact UTC is blank.
- Ningbo's official preview contains a weekday/date inconsistency; the discrepancy is disclosed.
- Tokyo order-of-play times, the ATP final start, EHF start times, two volleyball start times and greyhound off-time/traps remain blank.
- Golf, Snooker and Rugby League have no priced selection. The five-per-sport aim is evidence-capped, not force-filled.

## Repository outputs

- `23728b2b/`: executive dashboard, full match list, 15 sport pages, sources, methodology, Flagged for Review, repository audit, CSS and JavaScript.
- `data/23728b2b/`: structured evidence, fixtures, lines, predictions, flags, methodology, summary and validation record.
- `scripts/s23728b2b_*`: source records, shared arithmetic, builder and validator.
- `tests/pipeline/test_desk_23728b2b.py`: focused arithmetic, confidence, provenance, content and archive-registration tests.
- `pipeline/build.py`: one separately claimed `ARCHIVE` registration line; no other canonical logic changed. Desk JavaScript is inlined for archive-safe deployment.

## Local gate log — passed

| Gate | Result |
| --- | --- |
| Desk build | 21 HTML pages plus structured JSON; 55 fixture rows and 138 lines |
| Desk validator | 5/5 groups passed; 57 tables and 203 body rows have official links |
| Focused desk unit tests | 19/19 passed with `unittest`, including canonical archive registration |
| Preserved pipeline tests | 578/578 passed |
| Upstream audit tests | 38/38 passed |
| Canonical root validator | 0 errors |
| Historical structural validator | 0 errors; three pre-existing warnings in `f7fa77fc/flagged.html` only |
| Canonical staged build and validator | 25 canonical pages; 0 errors; desk HTML/CSS and inline controller present |
| Canonical browser gate | Desktop/mobile, project prefix, filters, downloads, deep links, expiry and no-JS behavior passed |
| Dedicated desk browser gate | 15 sport routes, seven High anchors, 55-row filters, empty state, audit, mobile navigation/overflow and local resources passed |

The local canonical refresh preserved unavailable-feed gaps and modified only generated canonical artifacts; those two byproducts were restored and are not part of this desk. Pinned browser packages were installed under `/tmp`, matching the workflow, with no production dependency added.

## Publication log

Pull-request checks, merge and GitHub Pages served-content read-back are pending at this pre-publication revision. This report does not yet claim deployment success; the final publication receipt will be appended after those steps complete.
