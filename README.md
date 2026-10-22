# OLBG1 — an independent multi-sport betting desk, built from official sources

A reverse-engineered rebuild of **OLBG.com**'s sport coverage, with our own lines on every match we can
verify, a confidence grade on every selection, and a written prediction wherever the number is strong
enough to defend.

**Live dashboard:** https://buffedlizard55-lab.github.io/OLBG1/

Snapshot: **22 October 2026, 03:30 UTC** — 127 fixtures and event cards across the 17 in-scope sports,
120 priced head-to-heads, 3,176 originated prices, 10 high-confidence picks.

---

## What the site contains

| Page | What it is |
|---|---|
| `index.html` | Landing dashboard: counts, the 10 high-confidence picks, and the 17 categories |
| `picks.html` | One row per priced match — date, venue, desk selection, price, grade, match-winner call, official source |
| `markets.html` | All 3,176 prices, match by match (winner, handicap, total, correct score) |
| `predictions.html` | The 10 high-confidence predictions, each a unique 30+ word write-up |
| `sports.html` + `sports/<slug>.html` | The 17 categories, each with its own match table and notes |
| `analysis.html` | Measured analysis: market coverage, price-window distribution, confidence rates |
| `flagged.html` | Everything not certified, plus the defects this pass found and fixed |
| `verification.html` | Which official page was read, when, by which session, and what could not be checked |
| `sources.html` | The official-source register: every host and URL used |
| `methodology.html` | Model, per-sport assumptions, confidence rules, known limits |
| `archive.html` | Every earlier board in the repository, preserved |

## Scope

**Covered (17):** Tennis, Basketball, Golf, Cricket, Snooker, Rugby Union, Rugby League, Baseball,
Ice Hockey, Motor Racing, Darts, Handball, Volleyball, Aussie Rules, eSports, Gaelic Football, Greyhounds.

**Excluded by the brief (7):** Football/Soccer, Horse Racing, American Football, Boxing (which houses
UFC/MMA on OLBG), Cycling, Specials, Hurling. Their OLBG ids are recorded in `data/olbg_taxonomy.json`
and listed on the site, but nothing in them is priced.

## The rules the desk is built on

1. **Official sources only.** A fixture, record, ranking or seed is confirmed against the governing body,
   league, tour or organiser. Aggregators, news outlets and Wikipedia never verify a fact. OLBG is used
   only to discover the taxonomy and the event list.
2. **Blank beats wrong.** If a value cannot be confirmed it is left empty and flagged. Nothing is
   inferred, interpolated or filled from memory.
3. **Model outputs are labelled.** Prices are the desk's own fair-value estimates (1 / probability, no
   margin), printed with the assumptions used, and never presented as quoted market odds.
4. **One grading scale.** High = at least 70% on the model *and* inside the brief's −250 to +10,000
   window *and* verified on the snapshot date *and* both sides measured. Carried or unrated rows are
   capped at Medium. Where nothing in the window clears 52%, the match is published as **no bet** — but
   it still carries a labelled match-winner call.
5. **Every high-confidence pick gets its own prediction** — 30+ words, unique, quoting only figures that
   appear in that row's sourced input, stating the selection and its price.

## Rebuild and validate

```bash
python3 scripts/rebuild.sh        # or run the steps below in order
python3 scripts/v3_build.py       # re-price the snapshot -> data/v3/*.json + /v3 pages
python3 scripts/final_site.py     # join, export data/final/*, render the root dashboard
python3 scripts/final_validate.py # dashboard gate: counts, prices, prose, sources, tables, links
python3 scripts/validate.py       # legacy primary-data + whole-tree link gate
python3 scripts/v3_validate.py    # snapshot gate
```

Eight gates run green on this commit: `final_validate.py`, `validate.py`, `v3_validate.py`,
`c17a9192_validate.py`, `ccb6bde2_validate.py`, `ebfbd966_validate.py`, `s7a5b5360_validate.py`,
`s984d417f_validate.py`.

`scripts/final_site.py` is idempotent. On a checkout that still has the 21 October board at the root it
moves that board into `archive/root-20261021/` and repoints its links; on a checkout that already has the
archive it leaves it alone.

## Verification status — read this before trusting a row

Every row carries the official URL it came from and the date it was read. The 22 October snapshot was
read by the session that built it: **99 rows verified on 22 October, 28 carried from 21 October**. Carried
rows keep their official link and are capped at Medium.

**The integration pass that consolidated this site could not re-fetch any official page**: its sandbox
reaches `github.com`, `api.github.com` and the package registries only. It therefore re-certifies nothing
and says so on `verification.html` and in `COORDINATION.md` §34. What it does verify is internal and
re-runnable: price arithmetic, the price window, source-URL shape and allowlist, prose rules, table
integrity, and every internal link.

## Repository layout

```
data/v3/          the 22 October snapshot (fixtures, lines, predictions, sources, coverage)
data/final/       the joined bundle + CSV that the dashboard renders
data/             the 21 October primary dataset (still validated by scripts/validate.py)
scripts/          generators and gates (v3_* = snapshot, final_* = dashboard, others = legacy boards)
archive/          earlier root board, preserved verbatim
sports/, *.html   the published dashboard (generated - do not hand-edit)
v3/, 7a5b5360/, 984d417f/, c17a9192/, ccb6bde2/, ebfbd966/, aa4e9dbf/, 2360a617/, docs/, f7fa77fc/
                  earlier boards, each kept exactly as its session published it
COORDINATION.md   the shared task board and verification log
```

## Honest limitations

* **No market prices are loaded.** These are our own lines; nothing here is a value bet against a bookmaker
  and no profit-and-loss can be computed.
* **Draws are not priced.** Every non-binomial sport is priced two-way, so a favourite's probability is
  slightly overstated in draw-capable sports. Disclosed as F-26B-06 and left for the next pricing pass.
* **Nothing is settled.** No fixture in the snapshot had been played when it was taken.
* **Seven cards have no market at all** (four golf tournaments, F1, League of Legends, GBGB) because no
  entry list or fixture could be captured. They are listed as event cards with the reason.
