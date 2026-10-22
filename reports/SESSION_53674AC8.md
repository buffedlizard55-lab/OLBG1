# Session 53674ac8 — Report

**Date:** 2026-10-22
**Branch:** arena/53674ac8-olbg1

## Summary

Independent live desk with fresh OLBG re-harvest (Oct 22 2026), official-source verification,
multi-market line origination, and clean dashboard.

## Data

- **47 fixtures** across 7 sports (Ice Hockey, Tennis, Darts, Snooker, Basketball, Rugby Union, Handball)
- **47 originated lines** with confidence tiers: 12 High / 24 Medium / 11 Low
- **12 high-confidence predictions** (all inside -250..+10000 window, all ≥30 words)

## Sports Covered

| Sport | Fixtures | High | Source |
|-------|----------|------|--------|
| Ice Hockey (NHL) | 9 | 5 | https://api-web.nhle.com/v1/schedule/2026-10-22 |
| Tennis (ATP/WTA) | 8 | 2 | https://www.atptour.com/en/scores/archive |
| Darts (PDC Euro Ch.) | 7 | 1 | https://www.pdc.tv |
| Snooker (NI Open) | 6 | 2 | https://www.wst.tv |
| Basketball (EuroLeague) | 7 | 2 | https://www.euroleaguebasketball.net |
| Rugby Union (URC/Top14) | 5 | 0 | https://www.unitedrugby.com |
| Handball (EHF CL R5) | 5 | 0 | https://www.eurohandball.com |

## Dashboard

13 pages at `/53674ac8/`:
- index.html (landing + stats + high-confidence picks table + sources)
- matches.html (full fixture list with source links)
- lines.html (originated lines with confidence badges)
- predictions.html (12 high-confidence predictions, each 58-68 words)
- flagged.html (known issues and data quality flags)
- methodology.html (model explanation, confidence rules, exclusions)
- sports/ice-hockey.html, tennis.html, darts.html, snooker.html, basketball.html, rugby-union.html, handball.html

## Verification

- All fixtures verified against official governing-body sources
- OLBG times confirmed in EDT (UTC-4) — not BST as briefly assumed
- Known OLBG defects documented: clock offset, GAA date error, zero-tip suppression
- Model-derived ratings explicitly labelled as estimates

## Irregularities

1. OLBG renders times in EDT (UTC-4) not BST on some hub pages
2. event_id=3536 (GAA): OLBG shows Nov 1 vs official Oct 25
3. OLBG zero-tip suppression hides active events (AFLW, eSports, RLWC26)
4. Team/player ratings are model-derived estimates where official published ratings unavailable

## File Scope

- `data/53674ac8/fixtures.json`
- `data/53674ac8/lines.json`
- `data/53674ac8/predictions.json`
- `scripts/s53674ac8_data.py`
- `scripts/s53674ac8_build_site.py`
- `reports/SESSION_53674AC8.md`
- `53674ac8/**/*.html` (13 pages)
