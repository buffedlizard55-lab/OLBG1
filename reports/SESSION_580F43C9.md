# Session 580f43c9 — 24/25 October 2026 desk

Evidence frozen: **2026-10-24T18:20:00Z**. Picks: **13** across **5** sports (0 high / 6 medium / 7 low).

## Picks

| Sport | Match | Pick | Market | Confidence | Fair | Start | Source |
|---|---|---|---|---|---|---|---|
| Basketball | Miami Heat v Charlotte Hornets | **Charlotte Hornets** | Match winner (money line) | medium | -225 (69.2%) | 24 Oct 2026 · 22:00 UTC | https://www.nba.com/games |
| Ice Hockey | Toronto Maple Leafs v Edmonton Oilers | **Edmonton Oilers** | Match winner (money line) | medium | -306 (75.4%) | 24 Oct 2026 · 23:00 UTC | https://api-web.nhle.com/v1/schedule/2026-10-24 |
| Ice Hockey | San Jose Sharks v Boston Bruins | **Boston Bruins** | Match winner (money line) | medium | -225 (69.2%) | 24 Oct 2026 · 23:00 UTC | https://api-web.nhle.com/v1/schedule/2026-10-24 |
| Basketball | Milwaukee Bucks v Philadelphia 76ers | **Philadelphia 76ers** | Match winner (money line) | medium | -375 (78.9%) | 24 Oct 2026 · 23:30 UTC | https://www.nba.com/games |
| Basketball | San Antonio Spurs v Dallas Mavericks | **Dallas Mavericks** | Match winner (money line) | medium | -225 (69.2%) | 25 Oct 2026 · 00:00 UTC | https://www.nba.com/games |
| Gaelic Sports | Nemo Rangers v St Finbarrs | **Nemo Rangers** | Match winner | medium | -178 (64.0%) | Sunday 25 October, 16:00 local (Irish time); UTC conversion not published | https://gaacork.ie/ |
| Ice Hockey | New York Rangers v Ottawa Senators | **Ottawa Senators** | Match winner (money line) | low | -124 (55.3%) | 24 Oct 2026 · 23:00 UTC | https://api-web.nhle.com/v1/schedule/2026-10-24 |
| Basketball | Brooklyn Nets v Cleveland Cavaliers | **Cleveland Cavaliers** | Match winner (money line) | low | -135 (57.4%) | 24 Oct 2026 · 23:30 UTC | https://www.nba.com/games |
| Baseball | Tampa Bay Rays v Milwaukee Brewers | **Milwaukee Brewers** | Match winner (money line) | low | -128 (56.1%) | 25 Oct 2026 · 00:00 UTC | https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-10-24&hydrate=team,linescore,probablePitcher |
| Basketball | Houston Rockets v Atlanta Hawks | **Atlanta Hawks** | Match winner (money line) | low | -135 (57.4%) | 25 Oct 2026 · 00:30 UTC | https://www.nba.com/games |
| Ice Hockey | Tampa Bay Lightning v Utah Mammoth | **Tampa Bay Lightning** | Match winner (money line) | low | -102 (50.5%) | 25 Oct 2026 · 01:00 UTC | https://api-web.nhle.com/v1/schedule/2026-10-24 |
| Tennis | Nikoloz Basilashvili v Daniil Medvedev | **Daniil Medvedev** | Match winner | low | -178 (64.0%) | Sunday 25 October; time not published on the official scores page (flagged F-06) | https://www.atptour.com/en/scores/current |
| Ice Hockey | Minnesota Wild v Seattle Kraken | **Seattle Kraken** | Match winner (money line) | low | -140 (58.3%) | Start time not read from the official schedule block (flagged F-05) | https://api-web.nhle.com/v1/schedule/2026-10-24 |

## Gaps

* **Golf** — OLBG golf hub returned "No tips found" at 17:50Z, so there is no golf market on the site to originate against. Source: https://www.olbg.com/betting-tips/Golf/5
* **Volleyball** — Fixtures are listed, but neither legavolley.it (SuperLega) nor plusliga.pl served a readable fixture or standings block; tauronliga.pl returned the Polish women's site instead. Source: https://ww2.legavolley.it/lvc/
* **Rugby Union** — URC Round 4 was readable for completed matches only; the remaining fixtures did not render, lnr.fr returned 404 and premrugby.com served a JavaScript shell with no fixture rows. Source: https://stats.unitedrugby.com/match-centre/2026-27/4
* **Cricket** — OLBG lists Pakistan v England and several CSA T20 games, but pcb.com.pk's fixtures routes returned its 404 page and no other official board schedule was read. Source: https://www.pcb.com.pk/404page.html
* **Snooker** — The only snooker listing (Mark Williams v Jak Jones, 14:05) had already started at read time, so no future match exists to price. Source: https://www.olbg.com/betting-tips/Snooker/8
* **Darts** — pdc.tv served a consent wall with no readable tournament, draw or order of play. Source: https://www.pdc.tv/tournaments
* **Greyhounds** — Only graded races with single tips are listed; no official runner, trap or result feed was readable, so no runner-level line can be originated. Source: https://www.olbg.com/betting-tips/Greyhounds/28
* **Motor Racing** — The United States Grand Prix weekend was mid-practice at read time; formula1.com carried no qualifying classification, so no grid-based line could be originated. Source: https://www.formula1.com/en/racing/2026/united-states
* **Handball** — ehfcl.eurohandball.com/en/matches/ and eurohandball.com/en/matches/ both returned 404; no HBL or LNH fixture/standings block was readable. Source: https://ehfcl.eurohandball.com/en/matches/
* **Rugby League** — OLBG lists only 2027 outright markets (State of Origin, Super League and NRL Grand Final); no 2026 match market is open, so nothing can be priced. Source: https://www.olbg.com/betting-tips/Rugby_League/10

## Flags

* **F-01** (high) The High tier is empty because the brief's two rules intersect in a 1.4-point window — The brief defines a high-confidence pick as better than 70% and also requires the fair price to be no shorter than -250. A -250 price is 71.43%, so only selections between 70.00% and 71.43% can satisfy both rules. No selection originated on this card lands in that window, so zero High picks are published rather than one being manufactured to fill the tier. [OLBG betting-tips index (discovery)](https://www.olbg.com/betting-tips)
* **F-02** (medium) Three selections clear 70% but are excluded by the -250 floor — Philadelphia (78.9%, fair -375) and Edmonton (75.4%, fair -306) both exceed 70% on our numbers, but their fair prices are shorter than -250, which the brief excludes, so they are published at medium tier. No selection landed between 70.00% and 71.43%, the only span that could satisfy both of the brief's rules. [NBA games (records used)](https://www.nba.com/games)
* **F-03** (high) Injury fields are blank everywhere — No official injury, suspension or availability report was read for any of the 13 priced matches (NBA, NHL, MLB, Cork GAA, ATP). Nothing has been inferred or filled in. Every injury column is empty by design. [NBA games page (no injury report on it)](https://www.nba.com/games)
* **F-04** (high) Ten of the fifteen requested sports carry no priced selection — Golf, Volleyball, Rugby Union, Cricket, Snooker, Darts, Greyhounds, Motor Racing, Handball and Rugby League are published as gaps with the exact blocking source on the sports pages and on the Flagged page. The five sports with prices are Basketball, Ice Hockey, Baseball, Gaelic Sports and Tennis. [OLBG betting-tips index](https://www.olbg.com/betting-tips)
* **F-05** (low) Minnesota Wild at Seattle Kraken start time not read — The official schedule's timing block for game 2026020179 was not reached before the read stopped, so the row carries a blank start rather than a guessed one. [NHL schedule API](https://api-web.nhle.com/v1/schedule/2026-10-24)
* **F-06** (low) Vienna final pairing and start are partly derived — Both semi-finals are confirmed on the official ATP scores page, so the final pairing follows from them; the start time is not published there. The only time available was OLBG's listing (06:00), which is discovery and is not used as a fixture fact. [ATP Tour scores](https://www.atptour.com/en/scores/current)
* **F-07** (medium) Four governing-body sites were unreadable from this environment — pdc.tv (consent wall), ehfcl.eurohandball.com and eurohandball.com (404), legavolley.it (landing page only) and lnr.fr (404) could not supply fixtures, so those sports carry no lines. The dead ends are listed on the sources page rather than skipped silently. [PDC tournaments (consent wall)](https://www.pdc.tv/tournaments)
* **F-08** (medium) NBA season-leader block on the official games page is not citable — The games page labels a Milwaukee player under Miami and a Charlotte player under Charlotte with mismatched club codes. Because the labels are internally inconsistent, no player-level statistic from that block is used in any write-up. [NBA games](https://www.nba.com/games)
* **F-09** (medium) Five-per-sport quota not met — The desk publishes 13 selections across five sports (Basketball 5, Ice Hockey 5, Baseball 1, Gaelic Sports 1, Tennis 1). Ten sports produced none because no official fixture-and-form source was readable. Nothing was written to reach a quota. [OLBG betting-tips index](https://www.olbg.com/betting-tips)
* **F-10** (low) COORDINATION.md contains two sections numbered 78 — Sections by sessions 7a9b24e5-olbg1 and 37003e61-olbg1 are both headed '## 78.', and the second appears after sections 79 and 80. Numbering is not sequential; content is not affected, but cross-references by section number are ambiguous. [COORDINATION.md](https://github.com/buffedlizard55-lab/OLBG1/blob/main/COORDINATION.md)
* **F-11** (low) Six desk directories have no namespaced data directory — 2360a617, 6a081cf6, aa4e9dbf, ccb6bde2, ebfbd966 and f7fa77fc publish pages without a matching data/<id>/ folder. Some store JSON as flat suffixed files or under datasets/, so this is a layout inconsistency, not proven data loss. [Repository root](https://github.com/buffedlizard55-lab/OLBG1)

## Repo audit

* **A-01** Root navigation: Every local href in the root index.html resolves on disk → 75 local links, 0 missing (pass) — Checked with a filesystem resolution pass; anchors stripped before testing.
* **A-02** Canonical data: count fields equal the length of the list they describe → data/lines.json count 126 with 126 rows; data/fixtures.json count 134 with 134 rows; data/predictions.json count 30 with 30 rows (pass) — Internal consistency only.
* **A-03** Canonical data: Behaviour of the canonical High tier in data/lines.json → confidence_counts reports 30 high / 30 medium / 66 low (flag) — The canonical file's 30 high rows are not re-verified here. Desk 02d3d515 recorded that some of its high rows sit below 70%; this desk did not re-read every row and makes no claim either way.
* **A-04** Scope: /sports contains one page per covered sport → 17 pages for a 15-sport brief (flag) — The extra two are Australian rules and eSports, which the brief does not list.
* **A-05** Coordination: Section numbering in COORDINATION.md is unique → two '## 78.' headings (flag) — See F-10.
* **A-06** Desk layout: Every desk directory has a namespaced data folder → 6 of 60 desk directories have none (flag) — See F-11.
* **A-07** Ignored artefacts: .gitignore excludes build output and raw responses → ignores _site/, node_modules/, .output/, .cache/, data/current/raw/, data/release/raw/, *.pyc (pass) — Read directly from .gitignore.
