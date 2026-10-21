# OLBG1 — Independent Match Coverage, Lines & Picks

This repo reverse-engineers **OLBG.com**'s sport/event structure, harvests the current
match list for every covered sport, verifies each fixture against official sources,
originates its **own** betting lines (no bookmaker prices), and publishes everything as a
static dashboard on GitHub Pages.

## Scope

**Covered sports** (OLBG taxonomy, exclusions applied): Tennis, Golf, Rugby Union, Rugby
League, Cricket, Basketball, Baseball, Darts, Snooker, Ice Hockey, Motor Racing,
Handball, Volleyball, eSports.

**Excluded per requirements:** soccer/football, boxing, UFC/MMA, American football,
hurling, horse racing, cycling, specials — plus (flagged judgment calls) Gaelic Football,
Aussie Rules (football codes) and Greyhounds (animal racing). See the site's
*Flagged for Review* page.

## Repo layout

- `tools/data_a.py`, `tools/data_b.py`, `tools/data_c.py` — the dataset (single source of truth)
- `tools/build_site.py` — builds JSON data + the static site
- `data/matches.json`, `data/sports/*.json` — generated datasets
- `data/olbg-structure.json` — reverse-engineered OLBG structure (sports, URL patterns, market maps)
- `docs/` — GitHub Pages site (landing dashboard, one subpage per sport, Predictions, Flagged for Review, Methodology)
- `COORDINATION.md` — shared multi-session task board

## Rebuild

```bash
python3 tools/build_site.py
```

## Verification standard

- **verified** — fixture confirmed on an official source (league/tour/federation/club).
- **partial** — competition/date confirmed via multiple listings; official league page linked.
- **unverified** — could not be confirmed officially: values left **blank** and flagged. Never inferred.

Every row on the site links to an official source where one was captured; high-confidence
picks include written predictions whose facts each carry their own source link.

## Notes

- Lines are independently originated fair (vig-free) prices derived from verified
  standings/results/H2H/seedings — see the site's Methodology page.
- Dataset captured 2026-10-21 (~05:00–08:00 UTC).
- 18+ only. Betting analysis, not guarantees.
