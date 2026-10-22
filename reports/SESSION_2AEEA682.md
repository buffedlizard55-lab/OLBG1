# Session 2aeea682-olbg1 — T2AEE fresh evidence desk

**Evidence read:** 2026-10-22T20:55:00Z  
**Branch:** `arena/2aeea682-olbg1` (pinned Arena work and integration branch)  
**Site namespace:** `/2aeea682/`  
**Status at this commit:** implementation and local verification complete; PR/merge/Pages receipts pending.

## 1. Delivered scope and honest coverage boundary

This is a fresh, source-linked snapshot, not a re-stamp of the expired historical desks. OLBG was used for taxonomy/discovery and observed market labels only. Official league, governing-body, tour and federation pages supplied the sporting fields. The retrieval layer returned parsed page excerpts rather than complete raw HTTP captures; the dataset is a manual transcription of fields actually read, with source URLs and limitations. It is not represented as a raw-packet archive.

The brief’s requested full worldwide list is **not claimed**. The desk publishes 71 officially read listings across 10 sports, 17 category pages, and named gaps for every other category. Sixty-four listings are unpriced because compatible paired official inputs were not read. This is preferable to filling values from memory or stale files.

| Metric | Result |
|---|---:|
| Officially read listings | 71 |
| Sports with listings | 10 of 17 |
| Priced fixtures | 7 |
| Unpriced / blank-and-flag listings | 64 |
| Originated markets | 87 |
| Originated outcome prices | 178 |
| Winner tiers | 5 Medium / 2 Low / 0 High |
| Featured High selections | 4 |
| Unique High predictions | 4 (75–77 words) |
| Official source records (including failed attempts) | 27 |
| OLBG discovery reads (not official) | 5 |
| Data/source flags | 21 |
| Repository findings | 6 |
| Static HTML pages | 30 |

### Per-sport coverage

| Sport | Listings | Priced | Originated markets | Official recheck |
|---|---:|---:|---:|---|
| Tennis | 5 | 0 | 0 | [official](https://wtafiles.wtatennis.com/pdf/draws/2026/2092/OP.pdf) |
| Basketball | 3 | 3 | 3 | [official](https://www.euroleaguebasketball.net/en/euroleague/news/game-center-round-7-el2627/) |
| Golf | 0 | 0 | 0 | [official](https://www.pgatour.com/tournaments/2026/butterfield-bermuda-championship/R2026528/overview) |
| Cricket | 3 | 0 | 0 | [official](https://www.pcb.com.pk/pakistan-england-and-sri-lanka-trination-odi-series-202627/tournament/1465.html) |
| Snooker | 3 | 0 | 0 | [official](https://www.wst.tv/matches/) |
| Rugby union | 8 | 0 | 0 | [official](https://www.unitedrugby.com/latest/news/2026-27-fixtures-in-full/) |
| Rugby league | 13 | 0 | 0 | [official](https://www.intrl.sport/fixtures-results) |
| Baseball | 5 | 4 | 84 | [official](https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-22&endDate=2026-10-29) |
| Ice hockey | 19 | 0 | 0 | [official](https://api-web.nhle.com/v1/schedule/2026-10-23) |
| Motor racing | 1 | 0 | 0 | [official](https://www.formula1.com/en/racing/2026/united-states) |
| Darts | 0 | 0 | 0 | [official](https://www.pdc.tv/news/2026/october/19/2026-machineseeker-european-championship-schedule-confirmed/) |
| Handball | 11 | 0 | 0 | [official](https://www.eurohandball.com/en/) |
| Volleyball | 0 | 0 | 0 | [official](https://www.plusliga.pl/games/tour/47.html) |
| Aussie rules | 0 | 0 | 0 | [official](https://www.afl.com.au/aflw/fixture) |
| eSports | 0 | 0 | 0 | [official](https://lolesports.com/en-US/schedule?leagues=worlds) |
| Gaelic football | 0 | 0 | 0 | [official](https://www.gaa.ie/fixtures-results) |
| Greyhounds | 0 | 0 | 0 | [official](https://www.gbgb.org.uk/racing/) |

## 2. Origination and High-confidence result

**Prices are experimental, zero-margin fair estimates—not bookmaker quotes, available offers or guaranteed returns.**

* **MLB:** independent Poisson score grids from official 2026 regular-season runs scored/allowed. Markets: winner, nine-inning 1X2, ±1.5/±2.5 run lines, half-run totals, integer push-refund totals and team totals. Conditional Game 5 (`ifNecessary=Y`) is unpriced.
* **EuroLeague:** Beta(2,2)-shrunk official records and log5, winner only. Exact 50/50 games show “No winner preference.” Handicap and total inputs are incomplete and withheld.
* **All other listings:** no synthetic fallback rating, so no price or winner preference is published.

The strict High rule is `p > 0.70` **and** unrounded fair American price in `−250…+10000`. Four outcomes qualify, all the same model line on four separate World Series fixtures: **Under 10 runs, push refunded at ten**, conditional probability **0.700400**, fair **−234**. Each has a unique 75–77 word prediction with team, active-roster player, current-form and recent-result evidence. No repeated eight-word passage occurs across the four texts.

This is a narrow and fragile result: only 0.04 percentage points above the gate. The model omits starting pitchers, bullpens, lineups, park, weather, rest and postseason effects. Games 1–4 share the same inputs and therefore identical numbers; they are not independent confirmations. Match-winner preference is separately Medium for Milwaukee at 55.54% / fair −125.

### High prediction manual-review links

| Prediction | Fixture | Selection | Official fixture |
|---|---|---|---|
| P-2AEE-01 | Tampa Bay Rays v Milwaukee Brewers | Under 10 runs (push refunded at 10) | [official](https://www.mlb.com/gameday/849805) |
| P-2AEE-02 | Tampa Bay Rays v Milwaukee Brewers | Under 10 runs (push refunded at 10) | [official](https://www.mlb.com/gameday/849802) |
| P-2AEE-03 | Milwaukee Brewers v Tampa Bay Rays | Under 10 runs (push refunded at 10) | [official](https://www.mlb.com/gameday/849804) |
| P-2AEE-04 | Milwaukee Brewers v Tampa Bay Rays | Under 10 runs (push refunded at 10) | [official](https://www.mlb.com/gameday/849803) |

## 3. Official source register

Every published fixture and market row links to an official source. The following reads were performed in this session. OLBG discovery reads are listed separately below and are never used as official confirmation.

| Publisher | Role | Actually observed | Limitation | URL |
|---|---|---|---|---|
| National Hockey League | official fixtures | Chunks 0-4: all two games on 23 October, 12 on 24 October and five on 25 October; game IDs, FUT state, venue, UTC start and explicitly labelled home/away teams. | 26-29 October chunks were not transcribed; this is not a whole-week NHL census. | [open](https://api-web.nhle.com/v1/schedule/2026-10-23) |
| Major League Baseball | official fixtures and conditional-game status | Five World Series games (849805, 849802, 849804, 849803, 849799), scheduled status, dates, venues, teams and ifNecessary flags. Game 5 is ifNecessary=Y; games 1-4 are N. |  | [open](https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-22&endDate=2026-10-29) |
| Major League Baseball | official statistical input | Tampa Bay: 98-64, 736 runs scored, 650 allowed; 55-26 home, 43-38 away, last-ten 5-5. |  | [open](https://statsapi.mlb.com/api/v1/standings?leagueId=103&season=2026&standingsTypes=regularSeason&fields=records,teamRecords,team,id,name,wins,losses,runsScored,runsAllowed,leagueRecord) |
| Major League Baseball | official statistical input | Milwaukee: 103-59, 832 runs scored, 618 allowed; 55-26 home, 48-33 away, last-ten 8-2. |  | [open](https://statsapi.mlb.com/api/v1/standings?leagueId=104&season=2026&standingsTypes=regularSeason&fields=records,teamRecords,team,id,name,wins,losses,runsScored,runsAllowed,leagueRecord) |
| Major League Baseball | official recent results | Eight final postseason games. NLCS: 2-1, 7-4, 6-2 and 6-4 wins over the Dodgers; preceding NLDS scores against San Diego. |  | [open](https://statsapi.mlb.com/api/v1/schedule?sportId=1&teamId=158&startDate=2026-10-01&endDate=2026-10-22&fields=dates,date,games,gamePk,gameDate,officialDate,status,detailedState,teams,away,home,team,id,name,score,isWinner,seriesDescription,venue,name) |
| Major League Baseball | official recent results | Ten listed postseason games plus one postponed entry. Last three finals: 7-3 and 3-1 at Cleveland, then 7-3 over Cleveland at Tropicana Field on 19 October. |  | [open](https://statsapi.mlb.com/api/v1/schedule?sportId=1&teamId=139&startDate=2026-10-01&endDate=2026-10-22&fields=dates,date,games,gamePk,gameDate,officialDate,status,detailedState,teams,away,home,team,id,name,score,isWinner,seriesDescription,venue,name) |
| Major League Baseball | official active roster | Christian Yelich, Jackson Chourio, William Contreras, Brice Turang, Jacob Misiorowski and other active-roster entries. | Roster presence does not confirm a starting role or availability for a particular game. | [open](https://statsapi.mlb.com/api/v1/teams/158/roster?rosterType=active&season=2026&fields=roster,person,id,fullName,position,abbreviation) |
| Major League Baseball | official active roster | Junior Caminero, Yandy Díaz, Jonathan Aranda, Drew Rasmussen, Cedric Mullins and other active-roster entries. | Roster presence does not confirm a starting role or availability for a particular game. | [open](https://statsapi.mlb.com/api/v1/teams/139/roster?rosterType=active&season=2026&fields=roster,person,id,fullName,position,abbreviation) |
| Euroleague Basketball | official fixtures, records, form and player context | Updated article separates completed Thursday results from Friday fixtures. Friday: Zalgiris-ASVEL (both 2-4), Olympiacos-Fenerbahce (both 5-1), Paris-Valencia (1-5 v 5-1), with club/player context and CEST start times. |  | [open](https://www.euroleaguebasketball.net/en/euroleague/news/game-center-round-7-el2627/) |
| WTA Tour | official order of play | BNB Ningbo Open, Friday 23 October: five Centre Court quarter-finals, seeds, published clock order and hard/Plexipave surface. | PDF has no timezone label; 'followed by' has no clock time. No ranking or form input was read. | [open](https://wtafiles.wtatennis.com/pdf/draws/2026/2092/OP.pdf) |
| International Rugby League | official fixtures | Thirteen fixtures dated 23-25 October with competition, round, venue, published clock and direct match-details link. | Clock timezone is not stated; no team form/rating input was read. | [open](https://www.intrl.sport/fixtures-results) |
| Pakistan Cricket Board | official tournament fixtures | Seven-match tri-nation list; upcoming named matches 4-6 on 25, 27 and 29 October at Gaddafi Stadium, Lahore. | Dates only; no start time or current team rating was read. TBC final excluded. | [open](https://www.pcb.com.pk/pakistan-england-and-sri-lanka-trination-odi-series-202627/tournament/1465.html) |
| World Snooker Tour | official fixtures and recent results | Northern Ireland Open scheduled quarter-finals 57-59 on 23 October: McGill-Wilson, Craigie-Slessor, Gilbert-Williams. Match 60 still says Winner of match 55 v Winner of match 56 and is not promoted to a named fixture. | Displayed clock has no timezone label; match 60 participants remain blank/flagged in coverage findings. | [open](https://www.wst.tv/matches/) |
| United Rugby Championship | official fixtures | Round 4: three fixtures on 23 October and five on 24 October, with venues and dual IRE & UK / ITA & SA publication clocks. |  | [open](https://www.unitedrugby.com/latest/news/2026-27-fixtures-in-full/) |
| United Rugby Championship | official fixture correction | Ospreys v Dragons moved from 19:45 to 19:00 UK on 24 October; St Helen's and S4C host broadcaster confirmed. |  | [open](https://www.unitedrugby.com/latest/news/adjustments-to-2026-27-bkt-united-rugby-championship-fixture-broadcast-for-rounds-2-4-6-15/) |
| United Rugby Championship | official match-centre cross-check | Round 4 page and direct IDs 292608-292610 for Friday matches; page says all times are Local and also displays a viewer-local 14:45 for the Friday games. | Viewer-local rendering is not converted to UTC. Later Saturday rows retain the official fixture-article link. | [open](https://stats.unitedrugby.com/match-centre/2026-27/4) |
| United Rugby Championship | official player context | Friday team announcements name full line-ups and replacements for Cardiff-Sharks, Connacht-Zebre and Edinburgh-Lions. | No paired current rating model was built from team sheets alone. | [open](https://www.unitedrugby.com/latest/team-news/round-4-team-announcements/) |
| European Handball Federation | official fixtures | Official live-score calendar: three 23 October and eight 24 October fixtures transcribed with competition, displayed clock and direct EHF match URL. | Only the first returned chunk was transcribed; venues and timezone are blank. This is not a complete EHF daily census. | [open](https://www.eurohandball.com/en/) |
| Formula 1 | official event schedule | United States Grand Prix schedule: practice 23 October, qualifying 24 October, race 25 October at 16:00 track time; Circuit of the Americas, 56 laps. | Event already has sessions before race day; no pre-event outright price is originated and track time is not converted to UTC. | [open](https://www.formula1.com/en/racing/2026/united-states) |
| NBA | official schedule attempt | Calendar reports 12 games on 23 October and eight on 24 October. | Match cards failed to render ('Sorry, something went wrong'), so no NBA pairing was promoted from OLBG into the verified match table. | [open](https://www.nba.com/games?date=2026-10-23) |
| PGA TOUR | official event status | Butterfield Bermuda Championship at Port Royal, 22-25 October; page status R1 In Progress. | Already in progress, so excluded from pre-match rows and prices. | [open](https://www.pgatour.com/tournaments/2026/butterfield-bermuda-championship/R2026528/overview) |
| AFL | official fixture attempt | Official AFLW fixture navigation and page shell returned. | No match cards were present in either extracted chunk; no AFLW fixture was invented from historical desks. | [open](https://www.afl.com.au/aflw/fixture) |
| GAA | official fixture check | 24 October listing contains Ireland v Scotland in the Shinty-Hurling International. | That event is excluded as hurling/shinty; no eligible Gaelic football match was observed on the returned page. Not a worldwide zero-fixture claim. | [open](https://www.gaa.ie/fixtures-results) |
| Greyhound Board of Great Britain | official racing check | Official racing search shell and 22 October race reports returned. | No future race/runner card was exposed in the extracted page, so no selection was constructed. | [open](https://www.gbgb.org.uk/racing/) |
| Professional Darts Corporation | official schedule attempt | Official PDC URL returned a privacy/cookie interstitial. | Article body and draw were not read; no darts fixture is marked verified. | [open](https://www.pdc.tv/news/2026/october/19/2026-machineseeker-european-championship-schedule-confirmed/) |
| TAURON Liga / PlusLiga | official fixture attempt | Request redirected to tauronliga.pl and returned match content, but its title says 2024/2025 while displayed matches are dated October 2026. | Competition/season labelling is irregular; no volleyball row is published until the correct current competition page is isolated. | [open](https://www.plusliga.pl/games/tour/47.html) |
| LoL Esports | official schedule attempt | Official schedule/league shell and Worlds tournament link returned. | No pairing was present in the extracted schedule content; no eSports match was imported from memory. | [open](https://lolesports.com/en-US/schedule?leagues=worlds) |

### Discovery-only reads

| Discovery page | Observed | Boundary | URL |
|---|---|---|---|
| OLBG (discovery only) | Sport routes and numeric IDs; page lastmod 2026-10-22. | Not an official sporting body; never used to verify a fixture. | [open](https://www.olbg.com/sitemap-betting-tips.xml) |
| OLBG (discovery only) | TB Rays @ MIL Brewers; Money Line 16/20 (80%); official explanatory text lists Money Line, Run Line and Game Totals. | Tip share is not a market price or model probability. | [open](https://www.olbg.com/betting-tips/Baseball/12) |
| OLBG (discovery only) | NBA, NBB and EuroLeague cards; Money Line and Pointspread labels; Friday EuroLeague cards match the official schedule. | First visible screen plus Load More only; not a complete event census. | [open](https://www.olbg.com/betting-tips/Basketball/4) |
| OLBG (discovery only) | Win Match, Set Betting, Games Won and Total Games labels; current WTA cards and additional ATP/WTA leads. | Additional leads remain unverified unless an official row appears in this desk. | [open](https://www.olbg.com/betting-tips/Tennis/3) |
| OLBG (discovery only) | NHL and European cards; Money Line, Game Totals and Puck Line labels. | Displayed clocks are not used; several 22 October cards were already live/completed at read time. | [open](https://www.olbg.com/betting-tips/Ice_Hockey/13) |

## 4. Verification performed

1. Read the current COORDINATION board, claimed a non-overlapping namespace and pushed the claim before implementation.
2. Re-read official pages for each published row; expired desks were not treated as fresh evidence.
3. Removed elapsed Thursday EuroLeague games after the official article updated them to results.
4. Preserved blanks for 47 missing exact UTC starts and 23 missing venues; no timezone or venue was inferred.
5. Excluded the conditional fifth World Series game from all pricing and winner selection.
6. Re-derived all 178 outcome prices from unrounded probabilities and checked market probability sums.
7. Checked every featured High against both the probability and price-window rules and attached bespoke evidence-bounded prose.
8. Checked all 30 local HTML pages, every rendered table row’s review link, CSV joins, local fragments and source-link shapes.
9. Ran desktop/mobile browser checks, including the 71-row and 178-row filters, reset behaviour, evidence disclosure and resource errors.
10. Probed derived external link formats. This caught and corrected 19 NHL game-center links: dashed dates redirect to `/errors/not-found`; official slash-date URLs work. MLB gameday redirect was also confirmed.

### Local and repository-wide gates

| Gate | Result |
|---|---|
| `python3 scripts/s2aeea682_validate.py` | **PASS — 5,220 checks, 0 errors / 0 warnings** |
| `python3 -m unittest discover -s tests/pipeline -v` | **PASS — 135 tests** |
| `python3 -m unittest discover -s tests -p "test*.py" -v` | **PASS — 38 preserved tests** |
| `python3 -m pipeline.validate --site .` | **PASS — 0 errors** |
| `python3 scripts/validate.py` | **PASS — 0 errors, 3 pre-existing warnings in `f7fa77fc/flagged.html`; 823 HTML pages link-checked** |
| `python3 -m pipeline.build --out _site` | **PASS — 83 canonical pages; `/2aeea682/` and its data staged; archive link present** |
| `python3 -m pipeline.validate --site _site` | **PASS — 0 errors** |
| Canonical Chromium suite | **PASS — desktop/mobile, project subpath, filters, expiry, downloads, no-JS** |
| Desk Chromium suite | **PASS — desktop/mobile, filters/reset, prediction details, resources; 0 JS errors** |
| `git diff --check` and scope sweep | **PASS — no whitespace errors or out-of-scope file changes** |

### Data hashes at verification checkpoint

| File | SHA-256 |
|---|---|
| `data/2aeea682/desk.json` | `7333b35abbd921f9eb54b8823a065db58607273a5363d34ae534cab28f1fb7e0` |
| `data/2aeea682/fixtures.csv` | `2dc6eb0b12c037f2ee6069106e934c0d271d4a207a744127485389d6d2a7e038` |
| `data/2aeea682/markets.csv` | `fbb6c83e91244e89c2f06e637b85f4eb78045f6a82d692f6595bfb836e1a6cb6` |

## 5. Flagged irregularities

These are published on `/2aeea682/flagged.html`; they do not block publication.

| ID | Severity | Finding | Official review |
|---|---|---|---|
| F-2AEE-01 | high | **Coverage is verified but partial** — 71 listings across 10 sports are published; seven category pages have no verified rows and 64 listings are unpriced. This is not a worldwide full-list claim. Empty categories and missing prices remain visible rather than backfilled. | [source](https://www.nba.com/games?date=2026-10-23) |
| F-2AEE-02 | high | **Most fixtures cannot be priced responsibly** — Only four non-conditional MLB games and three EuroLeague fixtures have paired official model inputs. Every other winner, handicap and total is blank/withheld with a row-level reason. | [source](https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-22&endDate=2026-10-29) |
| F-2AEE-03 | medium | **NHL coverage stops after 25 October** — All 19 NHL games on 23-25 October were transcribed, but 26-29 October schedule chunks were not. No zero-game inference is made for those dates. | [source](https://api-web.nhle.com/v1/schedule/2026-10-23) |
| F-2AEE-04 | medium | **NBA pairings did not render** — The official NBA calendar reports 12 games on 23 October and eight on 24 October, but its match-card area returned an error. OLBG-only pairings were not promoted. | [source](https://www.nba.com/games?date=2026-10-23) |
| F-2AEE-05 | medium | **PDC schedule is behind a privacy interstitial** — The official PDC article returned consent text rather than the draw, so no darts fixture or price is claimed as verified. | [source](https://www.pdc.tv/news/2026/october/19/2026-machineseeker-european-championship-schedule-confirmed/) |
| F-2AEE-06 | medium | **Volleyball competition/season needs reconciliation** — The PlusLiga URL redirected to TAURON Liga; its title says 2024/2025 while displayed matches are dated October 2026. Rows are withheld until the correct competition page is isolated. | [source](https://www.plusliga.pl/games/tour/47.html) |
| F-2AEE-07 | low | **AFLW match cards absent from extraction** — Two official page chunks returned navigation and footer content but no fixtures. No historical AFLW rows were re-stamped. | [source](https://www.afl.com.au/aflw/fixture) |
| F-2AEE-08 | low | **eSports pairings absent from extraction** — The official LoL Esports schedule shell and Worlds link returned without match pairings in the extracted content. | [source](https://lolesports.com/en-US/schedule?leagues=worlds) |
| F-2AEE-09 | low | **No eligible Gaelic football row observed** — The GAA page displayed a Shinty-Hurling International, which is excluded. This is not evidence of a worldwide zero-fixture schedule. | [source](https://www.gaa.ie/fixtures-results) |
| F-2AEE-10 | low | **Greyhound runner card unavailable** — GBGB's page exposed its racing search interface and reports, not a future field. No dog, trap or price was inferred. | [source](https://www.gbgb.org.uk/racing/) |
| F-2AEE-11 | medium | **Bermuda event is already in progress** — PGA TOUR marks Round 1 In Progress, so the tournament is excluded from pre-event picks. The correct Bermuda tournament ID is R2026528; R2026028 resolves to the BMW Championship. | [source](https://www.pgatour.com/tournaments/2026/butterfield-bermuda-championship/R2026528/overview) |
| F-2AEE-12 | medium | **World Series Game 5 is conditional** — MLB labels game 849799 ifNecessary=Y. Its fixture remains visible but all prices and winner preference are blank. | [source](https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-22&endDate=2026-10-29) |
| F-2AEE-13 | medium | **High clearance is only 0.04 percentage points** — Under 10 with a push has conditional probability 0.700400, just above the strict 70% gate, and fair -234. The model is not calibrated out-of-sample and omits pitchers, lineups, park and postseason effects; High is a rules label, not a guarantee. | [source](https://statsapi.mlb.com/api/v1/standings?leagueId=103&season=2026&standingsTypes=regularSeason&fields=records,teamRecords,team,id,name,wins,losses,runsScored,runsAllowed,leagueRecord) |
| F-2AEE-14 | medium | **Games 1-4 have identical MLB model numbers** — The same two regular-season team inputs and no venue adjustment produce identical lines for all four non-conditional games. They are separate fixtures, not independent confirmations or four separate betting edges. | [source](https://statsapi.mlb.com/api/v1/standings?leagueId=104&season=2026&standingsTypes=regularSeason&fields=records,teamRecords,team,id,name,wins,losses,runsScored,runsAllowed,leagueRecord) |
| F-2AEE-15 | low | **WST fourth quarter-final is not yet named** — Match 60 is officially Winner of match 55 v Winner of match 56. It is excluded from the named match table until the players are official. | [source](https://www.wst.tv/matches/) |
| F-2AEE-16 | low | **Leinster venue is TBC** — The official URC fixture list says TBC for Leinster v Munster; venue is blank. | [source](https://www.unitedrugby.com/latest/news/2026-27-fixtures-in-full/) |
| F-2AEE-17 | info | **Ospreys kick-off correction applied** — The older full fixture list says 19:45; a later official adjustment says 19:00 UK. The desk uses 19:00 and links the correction. | [source](https://www.unitedrugby.com/latest/news/adjustments-to-2026-27-bkt-united-rugby-championship-fixture-broadcast-for-rounds-2-4-6-15/) |
| F-2AEE-18 | medium | **EHF calendar extraction is incomplete** — Eleven fixtures were transcribed from the first EHF calendar chunk. Later chunks were not read, and venue/timezone remain blank on every handball row. | [source](https://www.eurohandball.com/en/) |
| F-2AEE-19 | medium | **Unlabelled publication clocks are not converted** — WTA, IRL, PCB, WST and EHF rows keep the publisher's display value; UTC remains blank where no timezone is stated. URC keeps its explicitly labelled local-zone clock. | [source](https://wtafiles.wtatennis.com/pdf/draws/2026/2092/OP.pdf) |
| F-2AEE-20 | info | **F1 is an event card, not a match prediction** — The race has practice and qualifying before it. No driver line is originated from the schedule alone and track-local time is not converted. | [source](https://www.formula1.com/en/racing/2026/united-states) |
| F-2AEE-21 | info | **OLBG tip share is not a market price** — The baseball hub showed 16/20 (80%) for Milwaukee, while this desk's independent winner estimate is 55.54%. Tip share was not used as a probability or bookmaker quote. | [source](https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-22&endDate=2026-10-29) |

### Repository findings

This was a bounded review of current coordination/canonical claims and fresh source issues, not a claim that every historical repository sentence was recertified.

| ID | Severity | File:line | Finding | Review |
|---|---|---|---|---|
| A-2AEE-01 | high | `COORDINATION.md:77` | **Stale task-board claims remain open** — T9 started on 21 October and remains 'in progress'. Other old open rows are also present. This session uses a collision-resistant ID and does not edit those claims; a later board cleanup should reconcile status with merged PRs. | [immutable file](https://github.com/buffedlizard55-lab/OLBG1/blob/cf187e20299b72aa29c3537a9cc624953aaa703b/COORDINATION.md#L77) |
| A-2AEE-02 | medium | `COORDINATION.md:133` | **A completed desk is still labelled in progress** — The row begins DONE but its status column remains in progress. It is retained verbatim under the append-only coordination rule and flagged for board maintenance. | [immutable file](https://github.com/buffedlizard55-lab/OLBG1/blob/cf187e20299b72aa29c3537a9cc624953aaa703b/COORDINATION.md#L133) |
| A-2AEE-03 | medium | `COORDINATION.md:3723` | **Previous fresh desk has expired** — The d7d19a67 handoff states a six-hour fixture expiry after 12:55Z. At this session's 20:55Z read it must not be presented as current without new official reads. | [immutable file](https://github.com/buffedlizard55-lab/OLBG1/blob/cf187e20299b72aa29c3537a9cc624953aaa703b/COORDINATION.md#L3723) |
| A-2AEE-04 | info | `README.md:11` | **Canonical root deliberately has no High picks** — The canonical README says its compatible inputs support only Low preferences. This desk does not overwrite that release; it publishes a separate, fresh evidence window and its own model limitations. | [immutable file](https://github.com/buffedlizard55-lab/OLBG1/blob/cf187e20299b72aa29c3537a9cc624953aaa703b/README.md#L11) |
| A-2AEE-05 | medium | `README.md:13` | **Historical evidence is not blanket recertification** — The repository explicitly says worldwide coverage, all markets, current player context and calibration are incomplete. Any site-wide claim of a fully verified complete list would contradict this limitation. | [immutable file](https://github.com/buffedlizard55-lab/OLBG1/blob/cf187e20299b72aa29c3537a9cc624953aaa703b/README.md#L13) |
| A-2AEE-06 | high | `scripts/sd7d19a67_data.py:354` | **Historical NHL game-center links use a broken date format** — A fresh read of this dashed-date URL redirected to NHL /errors/not-found. The official schedule's slash-date form /2026/10/23/ works. This session corrected all 19 of its own links; the historical desk is left untouched and flagged for its owner. | [immutable file](https://github.com/buffedlizard55-lab/OLBG1/blob/cf187e20299b72aa29c3537a9cc624953aaa703b/scripts/sd7d19a67_data.py#L354) |

## 6. Rebase and coordination record

During implementation, PR #141 (`2988bd19-olbg1`) merged with its own T2988 row and §60. `git pull --rebase origin main` conflicted in `COORDINATION.md`. Resolution retained the other session’s row and §60 verbatim and moved only this session’s own record to §61. No other session’s files or text were discarded. The rewritten session branch was pushed with `--force-with-lease` after rebase; subsequent pushes were ordinary fast-forwards.

## 7. Reproduction

```sh
python3 scripts/s2aeea682_model.py
python3 scripts/s2aeea682_audit.py
python3 scripts/s2aeea682_build_site.py
python3 scripts/s2aeea682_validate.py
python3 -m pipeline.build --out _site
python3 -m pipeline.validate --site _site
```

The model/build scripts are deterministic for the checked-in transcribed observations. They do **not** fetch or re-stamp official pages. A rebuild is not a fresh verification.

## 8. PR, merge and Pages receipts

Pending at this checkpoint. This section will be appended with the PR URL, merge result, workflow run and direct live-byte read-back before the task is marked done.
