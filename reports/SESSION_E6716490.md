# Session `e6716490-olbg1` — consolidated desk, live verification and publication record

**Task** T55 · **Branch** `arena/e6716490-olbg1` · **Base** `main` @ `425b63f` · **Read date** 22 October 2026
**Published site** `/e6716490/` (25 pages) · **Gate** `scripts/se6716490_validate.py` + repo-wide `scripts/validate.py`

---

## 1. What this session produced

| Artefact | Path | Contents |
|---|---|---|
| Fixture register | `data/e6716490/fixtures.json` | 122 fixtures, 17 in-scope sports, merged from two source registers, 10 cross-desk conflicts recorded |
| Originated lines | `data/e6716490/lines.json` | 105 priced matches, 1,575 markets, 1,722 priced selections, 9 High picks |
| Live verification ledger | `data/e6716490/verification.json` | 3 official endpoints re-read, 22 row-side comparisons |
| Predictions | `data/e6716490/predictions.json` | 9 hand-written High picks (74–89 words, 0 shared six-grams) + 105-row band-excluded ledger |
| Site | `e6716490/**` | landing dashboard, 17 sport pages, predictions, markets, verification, flagged, methodology, sources, repo audit |
| Generators | `scripts/se6716490_{dataset,model,verify,predictions,build_site,validate}.py` | six dependency-free scripts, run in that order |

Counts are reproduced by the validator on every run and appear on the landing page.

---

## 2. Sources used, and what was actually re-read

Only official governing-body, league, tour or organiser pages are used. OLBG is never used to verify a fact.

### 2.1 Re-read live in this session (22 October 2026)

| # | Authority | URL | What it confirmed |
|---|---|---|---|
| V1 | National Hockey League | https://api-web.nhle.com/v1/standings/2026-10-22 | Points percentage, W-L-OTL, goal differential and streak for Carolina, Vegas, Edmonton and Boston — 11 of the 12 ice-hockey rows |
| V2 | Major League Baseball | https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsTypes=regularSeason | Brewers 103-59 (home 55-26, away 48-33, W5) and Rays 98-64 (home 55-26, away 43-38, 736 runs scored / 650 allowed) — all 4 baseball rows |
| V3 | EuroLeague Basketball | https://www.euroleaguebasketball.net/en/euroleague/standings/ | Games played, W-L and points for/against for all 20 clubs, of which 10 are priced here — all 13 EuroLeague rows |

Both V1 and V2 return multi-page payloads. This session read the pages shown above and recorded **only the
fields it actually saw**; clubs and clubs' totals that appeared on unread pages are marked `carried`, not
verified. That distinction is printed row by row on `/e6716490/verification.html`.

### 2.2 Carried from the registers this desk merged

These official hosts are cited on the rows that came from `data/984d417f/fixtures.json` and
`data/f71557b5/fixtures.json`. Each of those registers records its own read date (22 October 2026); this session
did not re-fetch them and says so on every table.

`api-web.nhle.com`, `statsapi.mlb.com`, `www.euroleaguebasketball.net`, `www.nba.com`, `www.pdc.tv`,
`www.wst.tv`, `wtafiles.wtatennis.com`, `www.icc-cricket.com`, `scoring.nzc.nz`, `www.afl.com.au`,
`www.nrl.com`, `top14.lnr.fr`, `www.lnr.fr`, `ehfcl.eurohandball.com`, `www.plusliga.pl`, `lolesports.com`,
`www.galwaygaa.ie`, `gaacork.ie`, `munster.gaa.ie`, `www.formula1.com`, `www.europeantour.com`,
`www.gbgb.org.uk`.

Full per-domain register with row counts: `/e6716490/sources.html`.

---

## 3. Method (reproducible)

1. `se6716490_dataset.py` — load both registers, keep fixtures dated 22 October or later, reconcile club-name
   variants (`Panathinaikos` / `Panathinaikos AKTOR Athens`, `Montpellier HB` / `Montpellier Handball`, …),
   union their source lists and flags, and record every disagreement rather than dropping one reading.
2. `se6716490_model.py` — logistic win probability from the verified strength gap, draw share where the sport
   can draw, normal margin distribution for seven-rung half-line handicap ladders, baseball-only totals, fair
   prices with a 5% book-equivalent shown alongside. No line is nudged to move a price into the confidence band.
3. `se6716490_verify.py` — apply the three live re-reads, compare the register's own words with the fields read,
   stamp each row `re-fetched` or `carried`, and put the page actually read at the front of that row's sources.
4. `se6716490_predictions.py` — attach one hand-written write-up per High pick; enforce 30+ words and
   uniqueness by six-gram; build the band-excluded ledger.
5. `se6716490_build_site.py` / `se6716490_validate.py` — build the 25 pages and gate them.

---

## 4. The confidence band, stated plainly

The brief asks for picks with a greater than 70% chance **and** odds between −250 and +10000. At fair odds −250
is a 71.43% chance, so the qualifying window is 70.00%–71.43% — 1.43 percentage points wide.

* 537 selections on this desk carry a model probability of 70% or more.
* 42 of those also fall inside the price window.
* 9 fixtures publish a High pick after the desk's own limits (one High per fixture, max three per sport, cap 24).

The other 105 fixtures with a ≥70% selection are listed in the **band-excluded ledger** on
`/e6716490/markets.html#band` with their true (shorter) prices. They are not relabelled High, and no line was
moved to manufacture a qualifying price.

---

## 5. Verification performed, and its limits

* 22 row-side comparisons, each with the official URL beside it: 2 `match` (every field the page published
  appears in the register value) and 20 `partial` (the register corroborates the fields it quotes and does not
  quote the rest). **No contradiction was found in this pass** — no value had to be corrected.
* 12 of 122 fixtures are `re-fetched`; 110 are `carried`.
* Twelve sports were **not** re-read this session (tennis, golf, cricket, snooker, rugby union, rugby league,
  handball, volleyball, aussie rules, esports, gaelic football, greyhounds). No row from those sports is
  described as verified by this session anywhere on the site.
* The validator checks structure, links, prices, the band and the prose. It does not re-read the internet, and a
  passing gate is not a claim that a publisher has not since changed its page.

---

## 6. Irregularities flagged for review

| # | Item | Detail |
|---|---|---|
| F-E67-01 | 10 cross-desk conflicts | Two repository registers describe the same fixture differently: Florida Panthers 5-2-2 (.667) vs 5-3-2 (.600); Zalgiris/ASVEL seeds differ; Brewers home/road labels swap between registers; Toulouse/Perpignan form is phrased against different rounds. Both readings and both source lists are published on `/e6716490/flagged.html`. |
| F-E67-02 | World Series game five date | One register dates it 27 October, the other 28 October. The desk publishes 28 October (the later register) and logs the disagreement. |
| F-E67-03 | Barça v Montpellier head-to-head | One register records the earlier meeting as 28-27, the other as 34-27, both citing the EHF. The prediction quotes no scoreline. |
| F-E67-04 | Player-level detail missing | 6 of 9 High write-ups are team-level: the standings, ladder and draw pages read publish team aggregates only. Player figures are used only for the EuroLeague Bayern/Dubai pick, where the register carries them. |
| F-E67-05 | 17 cards published unpriced | 7 golf field cards, 3 motor-racing/F1 rows, 2 eSports Swiss-stage cards, 1 greyhound field, plus fixtures lacking a two-sided strength input. Reasons are printed per row. |
| F-E67-06 | Clocks not published | Darts, snooker, golf and one tennis match publish a session window or rolling order of play; those rows show “clock not published” and carry no kick-off. |
| F-E67-07 | 7 fixtures already started | Dropped from the priced set at the desk cut-off of 2026-10-22T07:2xZ rather than priced in play. |
| F-E67-08 | Repo-wide duplication | 14 published desks; 180 pairings priced in two or more registers, some with different constants and therefore different prices for the same match. Detailed on `/e6716490/audit.html`. |
| F-E67-09 | Stale pricing on older desks | The root register still prices 44 fixtures dated before 22 October 2026. Not corrected here — those files belong to earlier sessions. |
| F-E67-10 | README drift | The root README's headline counts (134 events, 160 pages) no longer match the tree (319 pages before this desk). Logged, not rewritten beyond this session's own section. |

None of these blocked publication. All are linked from `/e6716490/flagged.html` and `/e6716490/audit.html`.

---

## 7. Gates

```
python3 scripts/se6716490_validate.py  → VALIDATION PASSED
  pages 25 | fixtures 122 | priced 105 | markets 1575 | High 9 | predictions 9 | live re-checks 22
  data, band, prose and links are consistent

python3 scripts/validate.py            → VALIDATION PASSED (whole-tree links, source allowlists, writing rules)
python3 scripts/final_audit.py         → regenerated reports/FINAL_INTEGRATION_AUDIT.md byte-identically
```

## 8. Publication

See §40 of `COORDINATION.md` for the pull request, merge commit and the GitHub Pages deployment check.
