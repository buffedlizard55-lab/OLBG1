# Session `3ee30bba-olbg1` (`T3EE30`) — Live 22 Oct ~21:10Z 17-Sport Audit, Multi-Market Origination & Dashboard Report

- **Branch:** `arena/3ee30bba-olbg1` (Arena-pinned per `COORDINATION.md` §0.2)
- **Task ID:** `T3EE30` (`COORDINATION.md` §1 & §60)
- **Observation Window:** `2026-10-22T20:50:00Z` – `2026-10-22T21:10:00Z` UTC
- **Published Dashboard:** `/OLBG1/3ee30bba/` (`28` static HTML pages + `2` CSV exports + `3` JSON artifacts)

---

## 1. Scope & Non-Overlapping Architecture

Per `COORDINATION.md` §0.2–§0.5, this session works exclusively inside its isolated namespace (`3ee30bba/**`, `data/3ee30bba/**`, `scripts/s3ee30bba_*.py`, `reports/SESSION_3EE30BBA.md`, `tests/pipeline/test_desk_3ee30bba.py`, and append-only entries in `COORDINATION.md`). Zero shared canonical root files, `pipeline/**`, `data/current/**`, workflows, or peer session `<id>/` desks are edited. The canonical builder (`pipeline/build.py`) automatically stages all committed `3ee30bba/**` files into `_site/` and links `3ee30bba/index.html` on `archive.html`.

All **7 excluded OLBG sport routes** (`Football/1`, `Horse_Racing/2`, `American_Football/11`, `Boxing/16` incl. UFC/MMA, `Cycling/17`, `Specials/18`, and `Hurling/26`) are strictly excluded (`0` rows imported). All **17 in-scope OLBG sports** (`Tennis/3`, `Basketball/4`, `Golf/5`, `Cricket/7`, `Snooker/8`, `Rugby_Union/9`, `Rugby_League/10`, `Baseball/12`, `Ice_Hockey/13`, `Motor_Racing/14`, `Darts/15`, `Handball/20`, `Volleyball/21`, `Aussie_Rules/22`, `eSports/23`, `Gaelic_Football/25`, `Greyhounds/28`) were audited live on both `olbg.com` (discovery/telemetry only) and their official governing-body portals.

---

## 2. Key Live Findings at ~21:10Z UTC (vs Midday Snapshots)

1. **OLBG 5-Hour Unlabeled Split-Timezone Cache (`F-3EE-01`):** Fetched simultaneously at `20:56Z`, OLBG served unlabeled `EDT (UTC-4)` times on `Ice_Hockey/13` (`NSH@BOS Today 19:07` vs official `23:00Z`), `Baseball/12`, `Rugby_Union/9`, `Darts/15`, and `Motor_Racing/14`, while serving unlabeled `BST (UTC+1)` times on `Basketball/4` (`Zalgiris vs ASVEL Tomorrow 18:00` vs official `17:00Z`) and `Gaelic_Football/25` — a silent 5-hour discrepancy with zero timezone label.
2. **16 Midday Matches Elapsed / Completed (`F-3EE-06`, `AUD-3EE-01`..`08`):** Between `12:30Z` and `21:05Z` on 22 Oct 2026:
   - Five Thursday EuroLeague Round 7 games finished (`Anadolu Efes 89-80 Besiktas`, `Bayern 91-107 Dubai`, `Maccabi 99-113 Real Madrid`, `Panathinaikos 85-79 Baskonia`, `Milan 81-89 Barcelona`) and `Partizan vs Crvena Zvezda` was in-play;
   - All five Thursday EHF Champions League Men Round 5 games finished (`MT Melsungen 28-26 Plock`, `Szeged 33-33 GOG`, `Sporting CP 42-40 Kristianstad`, `Barça 40-34 Montpellier`, `Kolstad 32-35 Magdeburg`);
   - French Pro D2 `Montauban vs Oyonnax` finished (`Montauban V, Oyonnax Bd`);
   - PDC European Championship Day 1 R1 elapsed, with **Luke Humphries withdrawn due to gastroenteritis** and replaced by Kim Huybrechts (`F-3EE-05`, `AUD-3EE-04`);
   - ATP Almaty (`9410`), ATP Brussels (`7485`), WTA Ningbo (`2092`), WTA Osaka (`405`), and WST Northern Ireland Open advanced to **Friday Oct 23 Quarter-Finals**;
   - MLB StatsAPI added confirmed Tampa Bay Rays World Series starters **Nick Martinez** (Game 1) and **Drew Rasmussen** (Game 2) (`AUD-3EE-05`).
3. **Closed-System Standings Conservation Verified (`0` Discrepancies):**
   - **NHL (32 clubs, `standings/2026-10-22`):** `GP = 306` (`153` games), `W = 153 = L + OTL`, `GF = 954 = GA` ($\bar{\mu} = 3.1176$ goals/team-game).
   - **EuroLeague (20 clubs, post-Thu R7):** `GP = 132` (`66` games), `W = 66 = L`, `PF = 11,459 = PA` ($\bar{\mu} = 86.8106$ pts/team-game).
   - **EHF Champions League Men (24 clubs, post-Thu R5):** `GP = 120` (`60` games), `W = 55 = L`, `D = 10`, `GF = 3,844 = GA` ($\bar{\mu} = 32.0333$ goals/team-game).

---

## 3. Multi-Market Origination & In-Window High-Confidence Picks

- **140 Upcoming/In-Window Verified Listings** across all 17 covered sports (`44` priced, `96` unpriced with explicit blank markers and withholding reasons) + **16 Elapsed Oct 21–22 Entries**.
- **294 Originated Zero-Vig Markets (`600` Outcomes):**
  - Ice Hockey (`26` NHL games × `7` markets = `182` markets)
  - Handball (`12` EHF CL R6 games × `6` markets = `72` markets, including 3-way `1X2`, `Draw No Bet`, `±2.5` handicaps, and goal totals)
  - Baseball (`4` non-conditional MLB World Series games × `7` markets = `28` markets; conditional Game 5 `ifNecessary=Y` withheld)
  - Basketball (`2` Friday EuroLeague R7 games × `6` markets = `12` markets; `Paris vs Valencia` quarantined for `5-1` vs `4-2` official cross-page record conflict)
- **Match Winner Tiers:** `2 High / 24 Medium / 18 Low` (`44` priced matches).
- **13 In-Window High-Confidence Picks (`p > 70.00%` AND Fair Odds in `−250…+10000`):**
  1. `P-3EE-01` · `Los Angeles Kings @ New York Islanders` — **New York Islanders ML** (`-243`, `1.4121`, `70.81%`, 94w)
  2. `P-3EE-02` · `Los Angeles Kings @ New York Islanders` — **New York Islanders Over 2.5 Goals** (`-245`, `1.4075`, `71.05%`, 89w)
  3. `P-3EE-03` · `Vegas Golden Knights @ St. Louis Blues` — **Vegas Golden Knights Over 2.5 Goals** (`-244`, `1.4105`, `70.90%`, 95w)
  4. `P-3EE-04` · `Winnipeg Jets @ Dallas Stars` — **Under 6.5 Goals** (`-249`, `1.4020`, `71.32%`, 101w)
  5. `P-3EE-05` · `Minnesota Wild @ Calgary Flames` — **Minnesota Wild ML** (`-240`, `1.4168`, `70.58%`, 98w)
  6. `P-3EE-06` · `Utah Mammoth @ Seattle Kraken` — **Utah Mammoth +1.5** (`-234`, `1.4265`, `70.10%`, 85w)
  7. `P-3EE-07` · `Utah Mammoth @ Seattle Kraken` — **Over 5.5 Goals** (`-249`, `1.4012`, `71.37%`, 90w)
  8. `P-3EE-08` · `Montréal Canadiens @ Chicago Blackhawks` — **Montréal Canadiens Over 2.5 Goals** (`-241`, `1.4154`, `70.65%`, 87w)
  9. `P-3EE-09` · `Toronto Maple Leafs @ Edmonton Oilers` — **Over 5.5 Goals** (`-247`, `1.4047`, `71.19%`, 92w)
  10. `P-3EE-10` · `Tampa Bay Lightning @ Utah Mammoth` — **Tampa Bay Lightning +1.5** (`-247`, `1.4047`, `71.19%`, 88w)
  11. `P-3EE-11` · `Minnesota Wild @ Seattle Kraken` — **Minnesota Wild +1.5** (`-246`, `1.4071`, `71.07%`, 93w)
  12. `P-3EE-12` · `HC Vardar 1961 vs MT Melsungen` — **HC Vardar 1961 +2.5** (`-240`, `1.4161`, `70.62%`, 97w)
  13. `P-3EE-13` · `Montpellier Handball vs Dinamo Bucuresti` — **Montpellier Handball +2.5** (`-243`, `1.4108`, `70.88%`, 90w)
- **57 Out-of-Window Chalk Outcomes (`p > 71.43%`, shorter than `−250`)** are capped at `Medium` and itemized on `/3ee30bba/high-confidence.html`.
