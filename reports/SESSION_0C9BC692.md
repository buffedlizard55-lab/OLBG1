# Session 0c9bc692-olbg1 — T0C9

## 24 October evidence-first desk

- **Observation window:** 24 Oct 2026, 17:09 UTC (single session)
- **Scope:** the exact 15 requested sports only.
- **Retained fixture/event rows:** 19 (17 direct official schedule rows; 2 OLBG discovery-only rows, held blank).
- **Market investigation rows:** 58; one explicitly Low own fair display; all remaining lines withheld.
- **Executive High picks:** 0. The requested five-per-sport High target is short by 75 and is published on the Flagged page rather than filled with weak claims.

## Source boundary

The Sources page and `data/0c9bc692/sources.json` list every official page read and a short note of the fields retained. Official links are manual-review links for every table row. OLBG links are clearly labelled discovery only: community tip counts and labels were not treated as official facts or bookmaker prices.

## Clear outcome

The dashboard makes the executive outcome explicit: there are no High-confidence picks. The only selection is a **Low** Mark Williams research line, accompanied by an 83-word source-bounded explanation. It is not an executive recommendation. Darts and Gaelic OLBG discoveries remain unconfirmed; several sports have a source-status record but no exact fixture in the retained response.

## Reproducibility

```sh
python3 scripts/s0c9bc692_build.py
python3 scripts/s0c9bc692_validate.py
```

The validator checks local source IDs/URLs, row linking, market linkage, prediction length and prohibited prediction wording, the one disclosed fair-price arithmetic, generated routes, and no conflict markers. It cannot substitute for re-reading dynamic official pages.
