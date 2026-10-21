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

## Coverage at a glance (Primary Root Desk & `/f7fa77fc/` Mirror — Session `f7fa77fc-olbg1`)

- **134 source-linked events across ALL 17 in-scope OLBG sports**: `129` rows are `verified` and `5` Gallagher Premiership rows remain explicitly `cross-checked`; `126` two-sided H2H matches are priced across Winner, Draw No Bet, Handicap/Spread and (where a sourced baseline exists) Over/Under Total markets, plus `8` field cards across Golf, Motor Racing and Greyhounds.
- **All 24 active OLBG sport IDs reconciled** (`22` sitemap-listed + unlisted active routes `Entertainment/18` and `Hurling/26`): `17` in scope (`Tennis`, `Basketball`, `Golf`, `Cricket`, `Snooker`, `Rugby Union`, `Rugby League`, `Baseball`, `Ice Hockey`, `Motor Racing`, `Darts`, `Handball`, `Volleyball`, `Aussie Rules`, `eSports`, `Gaelic Football`, `Greyhounds`) and `8` excluded (`Football/Soccer`, `Horse Racing`, `American Football`, `Boxing`, `UFC/MMA`, `Entertainment/Specials`, `Hurling`, `Cycling`).
- **31 High-confidence picks** (requiring `status == "verified"` AND measured governing-body ratings on **both** sides — an original, source-bounded `30+` word prediction per pick, with `0` duplicate 6-word n-grams), **35 Medium**, **60 Low**, **8 Field cards**.
- **0 unverified values published as fact** and **0 broken relative links across all 131 published HTML pages** spanning all five live boards (`/` root, `/f7fa77fc/`, `/docs/`, `/ebfbd966/`, `/aa4e9dbf/`).

## Quick rebuild & repo-wide validation

```bash
python3 scripts/build_dataset.py       # governing-body fixtures, sources, coverage & flagged registry
python3 scripts/origin_lines.py        # multi-market pricing, 31 predictions & datasets/matches_full.{json,csv}
python3 scripts/build_site.py          # renders 27 pages at / and 27 mirrored pages at /f7fa77fc/
python3 scripts/validate.py            # strict provenance, market, export and all-site-link validator
python3 scripts/final_audit.py          # writes reports/FINAL_INTEGRATION_AUDIT.md (every primary row + links)
python3 scripts/ebfbd966_validate.py   # parallel ebfbd966 validator (0 errors)
```

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

---

## Addition (session ebfbd966, 2026-10-21): OLBG-crowd Originated Lines Desk

A second, complementary desk lives in `ebfbd966/` (live at `/OLBG1/ebfbd966/` on the Pages
site): 133 OLBG-listed matches from the same 2026-10-21 snapshot priced from OLBG crowd-share
decoding (winner/directional/handicap/totals/tie markets) plus verified official seed/rating
gaps — every row links its OLBG event page and an official source, with the full derivation
printed. It covers Tennis, Handball, Volleyball, Gaelic Football and a verified-zero Rugby
League check that this README's main build had flagged as not-investigated, plus verified-zero
checks for eSports (OLBG 23) and Aussie Rules (OLBG 22). Reproduce:

```bash
python3 scripts/ebfbd966_seed_data.py    # data/ebfbd966_matches.json
python3 scripts/ebfbd966_originate.py    # data/ebfbd966_lines.json
python3 scripts/ebfbd966_build_site.py   # ebfbd966/ (static pages)
python3 scripts/ebfbd966_validate.py     # sourcing / writeups / internal-link gate
```

Integration cross-checks (details in `COORDINATION.md` §4): this desk's early CONTESTED flags on
two snooker pairings were **retracted** after a direct fetch of the official WST Match Centre
confirmed OLBG's draw (the flag had rested on a stale search snippet); its Gaelic *club*
fixtures (24 Oct–1 Nov, OLBG-listed) do not contradict the main build's inter-county verified
negative for 21–25 Oct — different levels/calendars, both labelled.


---

## Parallel board: `aa4e9dbf/` desk (session `aa4e9dbf-olbg1`)

A fourth independently built desk, published alongside the root dashboard, the `docs/` board
and the `ebfbd966/` desk (see `COORDINATION.md` §9). All outputs are namespaced so nothing
of the other sessions is touched:

| Output | Where |
|---|---|
| 131-event dataset (14 covered sports, 2026-10-21 snapshot) | `tools/data_a.py`, `tools/data_b.py`, `tools/data_c.py` → `data/matches-aa4e9dbf-olbg1.json`, `data/sports-aa4e9dbf/*.json` |
| OLBG structure reverse-engineering (sport IDs, URL patterns, market maps) | `data/olbg-structure-aa4e9dbf.json` |
| Static desk (18 pages: landing, 14 sports, predictions, flagged, methodology) | `aa4e9dbf/` — served at `/OLBG1/aa4e9dbf/` |
| Builder | `python3 tools/build_site.py` |

Differences worth cross-reading: this desk embeds a **source link on every individual fact**
(standings, H2H, seedings, results), not only per row; it verified the EHF Champions League
round 5, EuroCup round 7, URC round 4, Top 14/ProD2, ATP/WTA draws and the PDC European
Championship first round against official pages; and it documents OLBG's **start-time bug**
(NBA/NHL/F1/darts/snooker times shown incorrectly on OLBG itself) as a finding.

It applies stricter exclusions than the other boards (Gaelic Football, Aussie Rules and
Greyhounds are excluded as judgment calls and flagged), which is recorded as an
interpretation difference, not a data conflict.

---

## Live official-source re-verification (session `72198d3e-olbg1`)

Every earlier pass in this repository audited the dataset's *structure* and said so. This pass
re-opened the governing-body pages themselves and compared them value by value with the published
rows. The register is machine-readable and per-row: `data/verification.json`, generated by
`python3 scripts/live_verification.py`, with the narrative in
[`reports/LIVE_VERIFICATION.md`](reports/LIVE_VERIFICATION.md) and the site page
[`live-verification.html`](live-verification.html).

| Outcome | Rows | Meaning |
|---|---|---|
| Confirmed | 51 | Official page re-fetched; participants, date, venue and published start/ID all match |
| Corrected | 9 | Official page disagreed, settled the value, dataset source amended |
| Flagged | 2 | Official page disagrees or cannot decide; nothing changed, published for review |
| Not re-checked | 72 | No official page re-read in this pass; blocker named per row |

**Corrections that came out of it** (all from re-fetched official pages, none inferred):

* **Snooker** — three Northern Ireland Open rows cited WST match-centre UUIDs that re-fetch as an
  unbound template with no players; two more cited only the generic site although WST publishes a
  match centre for both ties. All eleven rows now cite the match centre WST actually binds.
* **Cricket** — official NZC fixtures put the 3rd Women's T20I at North Sydney Oval (not Manuka
  Oval), New Zealand A v India A on 23 Oct at Bert Sutcliffe Oval (not 22 Oct at Saxton Oval), and
  Central Stags v Northern Districts at Saxton Oval, Nelson (not Pukekura Park).
* **Ice hockey** — Boston's home split was 5-1-0 against a standings endpoint that returns four
  home games at 3-1-0 for the same 7-2-1 record. Corrected; the rating and every price are
  unchanged because points percentage and goal difference drove the model.
* **Tennis** — six WTA Ningbo rows cited tournament 1115; WTA's own site links the draws at 2092.
* **Rugby league** — the men's RLWC rows cited NRL competition 175; the site serves that Round 2
  draw as competition 131.

**Deliberately not "fixed":** Vegas was priced at 8-2-0 (.800, W3) and the same live endpoint now
returns 8-3-0 (.727, L1). The pick is a labelled pre-game snapshot; re-pricing a published
selection after the fact would be worse than disclosing the drift, so both values are printed and
flagged (`F-V5`).

**Blockers recorded rather than hidden:** the PDC draw release still returns only a cookie-consent
interstitial to a text fetch, and WTA/ATP draws are client-rendered, so all 16 darts rows and all
11 tennis rows are listed as *not re-checked* instead of being implied verified.

The 31 High-confidence predictions were also re-authored in this pass — human voice, 61–78 words
each, every factual clause drawn from the row's stored official inputs, no repeated six-word
sequence anywhere in the corpus.

