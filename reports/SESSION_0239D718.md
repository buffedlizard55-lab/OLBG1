# Session 0239D718 — fresh 15-sport OLBG clarity desk

- Snapshot: 2026-10-24T22:40:00Z
- Branch: `arena/0239d718-olbg1`
- Counts: {"sports": 15, "matches": 57, "picks": 75, "high": 28, "medium": 29, "low": 18, "lines": 228, "sources": 50, "discovery_sources": 2, "flags": 22, "audit_findings": 120, "predictions": 75}

## Scope

All work is namespaced under `data/0239d718/**`, `scripts/s0239d718_*.py`, `0239d718/**`, `reports/SESSION_0239D718.md`, `tests/pipeline/test_desk_0239d718.py`, plus append-only `COORDINATION.md` receipts. Canonical changes are one `ARCHIVE` row, one generated front-door banner in `pipeline/build.py`, and the committed `index.html` mirror.

## Source work

Read 50 official source pages and the OLBG sitemap/main hub plus all 15 sport hubs. OLBG was used only for discovery and market-family mapping. Exact UTC starts from official feeds were retained; unlabeled site-local times were left blank in that field. Tip percentages were not used as probability inputs.

## Irregularities

- **F-001 Discovery gap** — Golf, Snooker, Motor Racing and Rugby League hubs showed no open match tips; official calendars were used for coverage.
- **F-002 Partial OLBG coverage** — Greyhounds hub exposed one daily race; official GBGB open-race reports were used for the remaining selections.
- **F-003 Time zone** — OLBG hub times have no visible timezone; exact UTC starts were left blank unless an official feed published them.
- **F-004 Tip share** — OLBG tip percentages are community shares and were never used as probabilities or official facts.
- **F-005 Source shell** — WTA Tokyo and Guangzhou draws pages were client-side notification shells; WTA rows remain flagged or excluded.
- **F-006 Index drift** — CSA's official search index exposed 25 Oct T20 fixtures but the live paginated page had moved to later dates.
- **F-007 404 / redirect** — Premiership fixtures path returned 404; the official match-centre standings page was used instead.
- **F-008 Partial official page** — USA Rugby confirms an Australia XV October series but not the exact USA v Australia A date, venue or lineup.
- **F-009 Availability gap** — NBA's 1:30PM ET injury issue marks several teams NOT YET SUBMITTED; those availability fields stayed blank.
- **F-010 Legacy route** — Earlier session discovery JSON uses /tips/ routes while live hubs resolve to /betting-tips/.
- **F-011 Stale task board** — COORDINATION.md contains older in-progress and queued rows from completed sessions; this session appended receipts rather than rewriting them.
- **F-012 Snooker final opponent** — WST lists Kyren Wilson v Winner of match 62; the second finalist was blank until the semifinal completed.
- **F-013 Short slate** — Baseball has one official MLB game in the window, so five picks are five market families on that one game.
- **F-014 Short slate** — Rugby League has two official RLWC fixtures on the NRL draw; five picks span win, handicap and total families.
- **F-015 Short slate** — Motor Racing has one official Grand Prix; five picks are driver-market families from the same race.
- **F-016 Blank official stats** — Gaelic county-board fixtures publish dates, venues and referees but no team form or scoring inputs; predictions say so explicitly.
- **F-017 Blank official stats** — CSA provincial T20 rows have no official form or recent score on the source read; those fields stayed blank.
- **F-018 Official racecard gap** — GBGB's static open-race and racing pages did not expose the full Sunday racecard, so runner form stayed blank for the daily race.
- **F-019 Time blank** — Snooker, darts, handball, volleyball and several rugby pages publish site-local times without a timezone; UTC fields stayed blank.
- **F-020 Odd-looking official roster** — Prior desk data and the official NBA injury issue both show LeBron James under Philadelphia; it is unusual but retained because the official PDF corroborates it.
- **F-021 Banned internal vocabulary** — Published prediction prose excludes internal build vocabulary; the check is enforced by the desk validator.
- **F-022 Canonical front door** — The canonical root still reports its older 18:00Z snapshot; the new front-door banner links to this namespaced 22:40Z desk without changing canonical counts.

## Repo audit

Scanned 122 tracked text files and 7045 lines; 120 findings are published on `0239d718/audit.html` with official recheck links.

## Validation

Run `python -m unittest discover -s tests/pipeline -v`, `python -m unittest discover -s tests -p 'test*.py' -v`, `python -m pipeline.validate --site .`, `python scripts/validate.py`, `python -m pipeline.build --out _site`, `python -m pipeline.validate --site _site`, and the browser gates before merge.
