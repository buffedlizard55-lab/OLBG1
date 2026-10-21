# OLBG1 — reverse-engineering OLBG, with our own lines

An independent reconstruction of **OLBG.com**'s sport taxonomy and match coverage, combined with a
transparent pricing model that originates our own betting lines for every fixture we can verify.

**Live dashboard:** https://buffedlizard55-lab.github.io/OLBG1/

---

## What this repository produces

| Output | Where |
|---|---|
| Sport taxonomy + URL grammar for all 22 OLBG sports | `data/olbg_taxonomy.json`, `reverse-engineering.html` |
| Verified fixture set, 21–27 October 2026 | `data/fixtures.json` |
| Originated lines (winner, handicap, total) + confidence tier per match | `data/lines.json` |
| Written predictions for every high-confidence pick | `data/predictions.json`, `predictions.html` |
| Source register with status per source | `data/sources.json`, `sources.html` |
| Every unverified value and coverage gap | `flagged.html` |
| Static dashboard (GitHub Pages source, served from repo root) | `index.html`, `*.html`, `sports/`, `assets/` |

## Quick start

```bash
python3 scripts/origin_lines.py    # fixtures -> priced markets (writes data/lines.json)
python3 scripts/build_site.py      # data -> static site (writes the repo root)
python3 scripts/validate.py        # link + data integrity gate; must print VALIDATION PASSED
```

No third-party dependencies. Python 3.10+.

## The rules this repo is built on

1. **Official sources only.** A fixture, record or ranking is confirmed against the governing body —
   league API, tour site, federation calendar. Aggregators, news outlets and Wikipedia are never
   used to verify a fact.
2. **Blank beats wrong.** If a value cannot be confirmed on an official page it is left empty and
   flagged. Nothing is inferred, interpolated or filled from memory.
3. **Assumptions are labelled as assumptions.** Home-advantage constants, variance scales and
   baseline totals are modelling choices, printed in full on the Methodology page. They are never
   presented as statistics.
4. **One-sided ratings are refused.** The model only applies a strength edge when *both* participants
   have a sourced input. Otherwise it falls back to a neutral baseline and caps confidence at low.
5. **Every high-confidence pick gets its own written prediction** — 30+ words, stating the selection,
   built only from sourced facts.

## Coverage at a glance

- **49 matches priced** across 7 sports: MLB, NHL, NBA, snooker, darts, cricket and Premiership rugby.
- **17 sports in scope** after the brief's exclusions; 9 have no priced rows and the reason for each is
  stated rather than hidden.
- **8 high-confidence picks**, **3 medium**, **38 low**. The low tier is large on purpose — see
  `methodology.html` for why.
- **0 unverified values published as fact.**

## Repository layout

```
data/            machine-readable dataset (fixtures, lines, predictions, taxonomy, sources)
index.html, *.html, sports/, assets/   the published static site (generated — do not hand-edit)
scripts/         model.py, origin_lines.py, build_site.py, validate.py
site_src/        stylesheet and small progressive-enhancement script
COORDINATION.md  shared task board and verification log
```

## Rebuilding after a data change

Edit `data/fixtures.json`, then run the three commands above in order. `validate.py` fails the build
on a broken internal link, a fixture with no source, a prediction under 30 words, a prediction that
disagrees with the model's pick, or a probability that does not sum to 1.

## Disclaimer

Prices in this repository are **our own model output**, not market prices and not betting advice.
They are estimates derived from published league records and world rankings, with a documented
5% overround. Do not treat them as a recommendation.

---

## Second board (parallel session `4f44f7d9`) — OLBG tip-share snapshot

A second agent session completed the same brief in parallel by a different route; both results
are kept (integration logged in `COORDINATION.md` §6). Where the root dashboard prices 49
officially-verified fixtures with a strength model, this companion board snapshots **all 164
events listed on OLBG's tip pages** on 2026-10-21 (15 of the 17 in-scope sports — Aussie Rules
and eSports, found via sitemap by the first session, are a logged gap) and originates fair
prices from verified OLBG tip counts.

| Output | Where |
|---|---|
| 164-event table (winner pick + confidence + originated price per row) | `data/matches.csv`, `data/matches.json` |
| Board site (20 pages) | `docs/` — live at https://buffedlizard55-lab.github.io/OLBG1/docs/ |
| Method, markets, verification | `research/methodology.md`, `research/markets.md`, `research/verification-log.md` |
| Irregularities F-01…F-13 | `docs/flagged.html` |

Rebuild: `python3 scripts/build_data.py && python3 scripts/build_board.py`
(5 High / 25 Medium / 134 Low; High picks checked against NBA.com, ICC, PDC, WTA.)
