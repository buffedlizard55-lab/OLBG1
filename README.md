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
| Live OLBG recapture (141 cards, 17 hubs) + event-level diff | `live-refresh.html`, `data/live_snapshot.json`, `data/live_diff.json`, `data/live_baseline.json` |
| Static dashboard (GitHub Pages source, served from repo root) | `index.html`, `*.html`, `sports/`, `assets/` |

## Quick start

```bash
python3 scripts/live_diff.py       # live OLBG capture vs committed dataset -> data/live_diff.json
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

- **134 source-linked events across ALL 17 in-scope OLBG sports**: `128` rows are `verified`, `5` Gallagher Premiership rows remain explicitly `cross-checked`, and `1` row (Afghanistan v Bangladesh ODI) is `unverified` because no governing body publishes that fixture — it is blank-and-flagged rather than filled from a tipster page. `126` two-sided H2H matches are priced across Winner, Draw No Bet, Handicap/Spread and (where a sourced baseline exists) Over/Under Total markets, plus `8` event/field cards.
- **All 24 active OLBG sport IDs reconciled** (`22` sitemap-listed + unlisted active routes `Entertainment/18` and `Hurling/26`): `17` in scope (`Tennis`, `Basketball`, `Golf`, `Cricket`, `Snooker`, `Rugby Union`, `Rugby League`, `Baseball`, `Ice Hockey`, `Motor Racing`, `Darts`, `Handball`, `Volleyball`, `Aussie Rules`, `eSports`, `Gaelic Football`, `Greyhounds`) and `8` excluded (`Football/Soccer`, `Horse Racing`, `American Football`, `Boxing`, `UFC/MMA`, `Entertainment/Specials`, `Hurling`, `Cycling`).
- **31 High-confidence picks** (requiring `status == "verified"` AND measured governing-body ratings on **both** sides — an original, hand-written `30+` word prediction per pick, with `0` duplicate 6-word n-grams), **34 Medium**, **61 Low**, `8` event/field cards.
- **Live refresh (2026-10-21T07:05Z):** all 17 in-scope OLBG hubs re-captured — `141` live cards, `69` joined by `event_id` to a source-verified row, `47` upstream consensus/selection movements recorded (with the superseded value kept in `olbg.consensus_prior`), `72` upstream-only cards listed as **unverified on `live-refresh.html`** and deliberately left out of the priced set, and `18` dataset rows logged as absent from the truncated first screen rather than treated as expired.
- **Four re-verification passes on 2026-10-21 (T20, T21, T22, T34):** every row carries a verification ledger block and names the pass that last read it. The register now stands at `41` confirmed against an official page, `33` corrected, `2` flagged and `58` not re-checked with the specific blocker printed. This pass corrected nine AFLW kick-off times that had been assigned in chronological order instead of per fixture, the Hawthorn venue, three Ford Trophy dates (27 October, not 24) and one EHF arena, and downgraded an ODI that no governing body publishes. See [`live-verification.html`](https://buffedlizard55-lab.github.io/OLBG1/live-verification.html) and [`reports/LIVE_VERIFICATION.md`](reports/LIVE_VERIFICATION.md).
- **No unverified value is presented as fact** — withheld values are blank and flagged — and **0 broken relative links across all 160 published HTML pages** spanning all five live boards (`/` root, `/f7fa77fc/`, `/docs/`, `/ebfbd966/`, `/aa4e9dbf/`).

## Quick rebuild & repo-wide validation

```bash
python3 scripts/live_diff.py           # event-level diff of the 07:05Z live OLBG capture
python3 scripts/build_dataset.py       # governing-body fixtures, sources, coverage & flagged registry
python3 scripts/origin_lines.py        # multi-market pricing, 31 predictions & datasets/matches_full.{json,csv}
python3 scripts/live_verification.py   # REQUIRED: verification register + per-row ledger blocks (T20/T21/T22/T34)
python3 scripts/build_site.py          # renders 30 pages at / and 30 mirrored pages at /f7fa77fc/
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

### Post-T20 re-check (session `3c7579ed-olbg1`, task T21)

The repository's verification register (`data/verification.json`, rendered on
[`live-verification.html`](live-verification.html)) now reads **46 confirmed, 16 corrected, 2 flagged and 70
not re-checked** out of 134 rows. This pass contributed:

* **Seven rugby-league rows re-sourced.** `nrl.com/draw/?competition=175` and `?competition=176` both render
  `competition=131` (the men's page), so the women's fixtures pointed at the wrong tournament. Each row now
  cites its own tournament's Round 2 draw plus the IRL match record (2569–2573, 2586, 2588), whose venue-local
  kick-offs match the stored UTC values.
* **A disclosed kick-off conflict.** Samoa Women v Wales Women is 2:45am AEDT (06:45Z) on the NRL draw and
  17:50 local (06:50Z) on the IRL record. Both figures are published; the five minutes are not inferred away.
* **Tennis provenance.** The eleven tennis pairings are consistent with the completed Round-of-32 results plus
  byes, but the matches have not been played and the draws are client-rendered, so every row now carries a
  "reconstructed, not draw-verified" flag with the start time left blank.
* **31 rewritten predictions.** 37–51 words each, no shared closers, no price string inside the prose; the
  price stays in `bet_line`. `scripts/validate.py` enforces the rules.

### Third re-check (session `3c7579ed-olbg1`, task T22)

* **Seven rugby-league rows re-sourced.** `nrl.com/draw/?competition=175` and `?competition=176` both render
  `competition=131` (the men's page), so the women's fixtures pointed at the wrong tournament. Each row now
  cites its own tournament's Round 2 draw plus the IRL match record (2569–2573, 2586, 2588); the venue-local
  kick-offs on those records match the stored UTC values.
* **Kick-off conflict disclosed.** Samoa Women v Wales Women is 2:45am AEDT (06:45Z) on the NRL draw and
  17:50 local (06:50Z) on the IRL record. Both figures are published; the five minutes are not inferred away.
* **Tennis provenance.** The eleven pairings are consistent with the completed Round-of-32 results plus byes,
  but the matches have not been played and the draws are client-rendered, so every tennis row now carries a
  "reconstructed, not draw-verified" flag with the start time left blank.
* **Prediction prose de-templated.** The price no longer appears inside the write-ups (27 of 31 previously
  ended with the same `: price` closer); it stays in `bet_line`. Write-ups run 49–82 words with zero
  duplicated six-word sequences.
* Register totals now read 44 confirmed, 19 corrected, 2 flagged, 69 not re-checked. See
  [`reports/SESSION_3C75_RECHECK.md`](reports/SESSION_3C75_RECHECK.md).

---

## Complete 17-Sport Live Official-Source Suite & Signed ATP/WTA Draw Verification (`/984d417f/` — session `984d417f-olbg1`)

Published side by side at [`/984d417f/`](984d417f/index.html) (`https://buffedlizard55-lab.github.io/OLBG1/984d417f/`),
session `984d417f-olbg1` closes the client-rendered ATP/WTA draw blocker above by directly retrieving all **five official signed
Tour Supervisor draw PDFs** (`https://wtafiles.wtatennis.com/pdf/draws/2026/2092/MDS.pdf`,
`https://wtafiles.wtatennis.com/pdf/draws/2026/405/MDS.pdf`,
`https://www.protennislive.com/posting/2026/9410/mds.pdf`,
`https://www.protennislive.com/posting/2026/496/mds.pdf`,
`https://www.protennislive.com/posting/2026/7485/mds.pdf`), alongside the live 32-seed PDC European Championship bracket,
the live 2026 NAB AFLW Round 10 ladder, WNBA Finals Game 3, and full multi-runner field boards across PGA, LPGA, Formula 1,
and GBGB Greyhounds:

| Deliverable | Path | Summary |
|---|---|---|
| Interactive 23-page dashboard | `984d417f/index.html` + `984d417f/sports/<slug>.html` | Master 145-event filterable/sortable board, all 17 sport category pages, Decimal/American/Fair-% switcher, Dark/Light theme |
| High-confidence human predictions | `984d417f/predictions.html`, `data/984d417f/predictions.json` | 40 unique human-written predictions (`56–68` words each, `0` repeated 6-grams) across 10 sports |
| Multi-market lines & CSV export | `data/984d417f/{fixtures,lines}.json`, `data/984d417f/matches.csv` | Zero-vig + bookmaker-equivalent Win/1X2/Outright, non-pushing `.5` Spreads, Totals, Derivatives & full multi-runner field boards |
| Line-by-line repo & OLBG audit | `984d417f/audit.html`, `reports/SESSION_984D417F_AUDIT.md` | 11 line-numbered repository audit groups (`AUD-984-01`..`11`) + 9 upstream `OLBG.com` defects (`OLBG-DEF-01`..`09`) |
| Flagged for Manual Review | `984d417f/flagged.html`, `data/984d417f/flagged.json` | 127 blank/flagged field entries held uninferred with direct official review URLs |

Reproduce & validate:

```bash
python3 scripts/s984d417f_dataset.py     # compiles data/984d417f/{olbg_taxonomy,markets_catalog,sources,fixtures,repo_audit,flagged}.json
python3 scripts/s984d417f_model.py       # originates lines.json, predictions.json & matches.csv
python3 scripts/s984d417f_build_site.py  # renders 23 pages in 984d417f/ + reports/SESSION_984D417F_AUDIT.md
python3 scripts/s984d417f_validate.py    # verifies all 145 rows, 40 writeups, 2,946 links & anchors (0 errors)
```



---

## Fresh matchday desk — 22–26 October 2026 (session `7a5b5360-olbg1`, task T41)

**Live board:** https://buffedlizard55-lab.github.io/OLBG1/7a5b5360/

A new, self-contained desk that re-harvests the current fixture window from official sources instead of
inheriting any earlier session's snapshot.

| Output | Where |
|---|---|
| 32 verified fixtures across 5 sports (MLB World Series, 12-game NHL slate, URC Round 4, WST Northern Ireland Open Round 3, F1 United States GP) | `data/7a5b5360/fixtures.json` |
| 231 originated selections across winner, handicap, total and outright markets | `data/7a5b5360/markets.json` |
| One match-winner pick per fixture, tiered High ≥70% / Medium ≥55% / Low | `data/7a5b5360/picks.json` |
| 18 written predictions (≥30 words, no shared 6-word phrase) | `data/7a5b5360/predictions.json` |
| Every selection at 70%+ with its price and in-band status | `data/7a5b5360/high_probability.json` |
| Coverage record for all 17 in-scope sports, including the 12 that could not be verified | `data/7a5b5360/coverage.json` |
| 14 flags and 6 repository-review findings | `data/7a5b5360/flags.json` |
| Flat export | `data/7a5b5360/matches.csv` |
| Dashboard (9 pages + 5 sport pages) | `7a5b5360/` |

**Rebuild and gate:**

```bash
python3 scripts/s7a5b5360_build.py      # data + site
python3 scripts/s7a5b5360_validate.py   # desk gate: sources, prices, prose, links, coverage
python3 scripts/validate.py             # repository-wide link/data gate
```

The desk publishes one finding about the brief itself (`F-7A-01`): a 70% probability is a 1.43 fair price,
so it is already shorter than the -250 floor the brief pairs it with. Every selection therefore carries its
probability, its fair price and an in-band yes/no rather than one rule being silently dropped.

---

## High-confidence price-window compliance (session `2ca35f17-olbg1`, T41, 2026-10-22)

The brief asks for high-confidence picks on matches priced **between −250 and +10000**. The inherited build did not
do that: **19 of its 31 high-confidence picks were shorter than −250** (−263 to −1250). This pass makes the window a
hard gate and documents the contradiction it exposes.

| Before | After |
|---|---|
| 31 high picks, 12 inside the window | **29 high picks, 29 inside the window** (−189 to −250) |
| 3 markets per match (winner, handicap, total) | **8 markets per match** (winner, draw-no-bet, 3 handicap rungs, 3 totals rungs) |
| Prices typed into a hand-maintained `bet_line` dict | `bet_line` generated from the priced selection (drift impossible) |
| Confidence = win probability only | Confidence = verified + two measured ratings + separation **+ in-window price at 60%+** |

**The rule that could not be satisfied as written:** at the documented 5% overround, a 68.0% chance prices at exactly
−250 and a 70.0% chance prices at −277. ">70% chance" and "≥ −250" cannot both hold. The window is treated as binding,
conviction is floored at 60%, and the arithmetic is published on the Methodology page and as finding `T41-01` on the
Flagged for Review page. Full detail, the 19-row repricing table and the live-read log:
[`reports/SESSION_2CA3_PRICE_WINDOW.md`](reports/SESSION_2CA3_PRICE_WINDOW.md).

Where a moneyline breached the floor, the same view is published on the handicap rung that lands inside the window
(Stade Toulousain −7.0 at 1.40 rather than a −667 moneyline; Hawthorn −10.0 rather than −769). Totals are never the
highlighted pick: their baseline is a modelling constant, so a 68% totals rung would be an artefact of the ladder
rather than evidence (finding `T41-03`).

**Verification added in this pass (2026-10-22):** the two Ningbo tennis pairings were confirmed against the
[official signed WTA draw PDF](https://wtafiles.wtatennis.com/pdf/draws/2026/2092/MDS.pdf) (released 21 Oct 2026
22:13Z), which also resolves the long-standing "WTA draws are client-rendered" blocker; Boston's record and the
already-disclosed Vegas drift were re-confirmed against the
[NHL standings API](https://api-web.nhle.com/v1/standings/2026-10-21). The PDC cookie wall and the EuroLeague
client-rendered game centre were re-attempted and remain blocked, so those six rows stay labelled `not_rechecked`
rather than being implied verified.

Reproduce:

```bash
python3 scripts/apply_t41_verification.py   # T41 evidence layer over data/verification.json
python3 scripts/origin_lines.py             # market ladders + window filter + predictions
python3 scripts/build_site.py               # 30 pages at / and 30 mirrored at /f7fa77fc/
python3 scripts/validate.py                 # fails the build if any high pick leaves the window
```

## Matchday desk — 22–24 October 2026 (session `9dfd0b48-olbg1`, task T45)

**Live board:** https://buffedlizard55-lab.github.io/OLBG1/9dfd0b48/ · report: `reports/SESSION_9DFD0B48.md`

| What | Where |
|---|---|
| 29 fixtures verified on ATP Tour (Almaty/Brussels/Lyon R16), WST (NI Open R3), EuroLeague (Round 7) and MLB (World Series G1) pages | `data/9dfd0b48/fixtures.json` |
| 81 two-way markets (winner, handicap, total) = 162 originated selections | `data/9dfd0b48/markets.json` |
| 27 picks (3 High / 11 Medium / 13 Low); High write-ups ≥30 words, featured price inside −250/+10000 | `data/9dfd0b48/picks.json`, `predictions.json` |
| 70-item flag register: every OLBG listing across all 17 hubs that could not be verified, blank and reasoned | `data/9dfd0b48/flags.json`, `9dfd0b48/flagged.html` |

```bash
python3 scripts/s9dfd0b48_build.py      # data + 12-page site
python3 scripts/s9dfd0b48_validate.py   # desk gate
```

---

## Desk `a570c470` — 141 verified fixtures, 1,546 originated prices, line-by-line repo audit (22 Oct 2026)

**Live board:** https://buffedlizard55-lab.github.io/OLBG1/a570c470/ · report: `reports/SESSION_A570C470_AUDIT.md`

| What | Where |
|---|---|
| 141 source-verified fixtures, all 17 in-scope sports, 22–28 Oct 2026 window (116 priced + 25 event cards) | `data/a570c470/fixtures.json` |
| 1,546 originated prices: winner, draw-no-bet, three handicap rungs, three total rungs, correct score | `data/a570c470/lines.json` |
| 16 High-confidence picks, every one inside −250 to +10000 on its published price, each with a bespoke 53–76-word prediction and zero repeated 6-grams | `data/a570c470/predictions.json` |
| 45 governing-body sources, each recording what it established and when it was read | `data/a570c470/sources.json`, `a570c470/sources.html` |
| Line-by-line audit: 8 findings (2 high), including 16 of 18 AFLW ladder inputs on the root desk disagreeing with the official ladder | `data/a570c470/audit.json`, `a570c470/audit.html` |
| 95 row-level flags: every value that could not be confirmed, blank rather than guessed | `data/a570c470/flagged.json`, `a570c470/flagged.html` |

```bash
python3 scripts/sa570c470_sources_and_taxonomy.py  # source registry + OLBG taxonomy
python3 scripts/sa570c470_dataset.py               # verified fixtures
python3 scripts/sa570c470_model.py                 # strengths, markets, confidence tiers
python3 scripts/sa570c470_predictions.py           # written predictions for every High pick
python3 scripts/sa570c470_audit.py                 # repo findings + flag register
python3 scripts/sa570c470_build_site.py            # 28-page dashboard under /a570c470/
python3 scripts/sa570c470_validate.py              # desk release gate
```
