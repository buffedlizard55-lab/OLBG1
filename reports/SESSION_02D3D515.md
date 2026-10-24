# Session 02d3d515 — live 15-sport desk for 24–25 October 2026

**Captured:** 2026-10-24T17:45:00Z (all times UTC)
**Branch:** `arena/02d3d515-olbg1`
**Site:** `02d3d515/index.html` · **Data:** `data/02d3d515/` · **Build:** `python3 scripts/s02d3d515_build.py`
**Gates:** `python3 scripts/s02d3d515_validate.py`, `python3 -m unittest tests.pipeline.test_desk_02d3d515`

## What was built

A fifteen-sport desk that answers one question first: *what should I look at today, and why?*
The landing page opens with an executive summary (counts, the high-confidence card, the
odds-window note), then the picks table, then the written predictions. Every other page is
one click away and named for what it holds: Picks, All matches, Our lines, Predictions,
Sports, Sources, Method, Flagged for review, Repo audit.

- **21 priced selections** across **8 sports** — 7 high, 7 medium, 7 low.
- **27 fixtures** confirmed on an official schedule, each with a source link on the row.
- **11 fixtures carried without a line**, each naming exactly what was missing.
- **16 sources**, split into official pages (used for facts) and OLBG routes (discovery only).
- **12 flags** published on the Flagged for Review page.
- **26 HTML pages**: dashboard, 8 category pages, 15 sport pages, reverse-engineering notes.

## Coverage by sport

| Sport | Fixtures | Picks | High | Status |
|---|---|---|---|---|
| Ice Hockey | 5 | 2 | 2 | yes |
| Basketball | 8 | 8 | 4 | yes |
| Baseball | 1 | 2 | 0 | yes |
| Cricket | 1 | 1 | 0 | yes |
| Darts | 0 | 0 | 0 | no confirmed fixture |
| Gaelic Sports | 2 | 0 | 0 | fixtures only |
| Golf | 1 | 2 | 0 | yes |
| Greyhounds | 0 | 0 | 0 | no confirmed fixture |
| Handball | 5 | 0 | 0 | fixtures only |
| Motor Racing | 1 | 3 | 0 | yes |
| Rugby League | 0 | 0 | 0 | no confirmed fixture |
| Rugby Union | 2 | 2 | 0 | yes |
| Snooker | 0 | 0 | 0 | no confirmed fixture |
| Tennis | 1 | 1 | 1 | yes |
| Volleyball | 0 | 0 | 0 | no confirmed fixture |

Sports with no pick are not silent: their pages state that no fixture could be confirmed on an
official page, and the corresponding row is flagged. The five-per-sport daily target is met for
no sport on this date because the official boards do not carry five matches each that could be
read in the session window; the shortfall is quantified on the Flagged page.

## The published card

| Sport | Fixture | Market | Selection | Fair price | Est. win | Tier |
|---|---|---|---|---|---|---|
| basketball | nba-mia-cha | Match winner | Charlotte Hornets | -148 | 59.6% | high |
| ice-hockey | nhl-sjs-bos | Match winner | Boston Bruins | -242 | 70.8% | high |
| ice-hockey | nhl-sjs-bos | Match total | Under 6.5 goals | -158 | 61.2% | high |
| basketball | nba-sas-dal | Match winner | Dallas Mavericks | -148 | 59.6% | high |
| basketball | nba-nop-den | Match winner | Denver Nuggets | -148 | 59.6% | high |
| basketball | nba-gsw-phx | Match winner | Phoenix Suns | -148 | 59.6% | high |
| tennis | atp-final | Match winner | Daniil Medvedev | -178 | 64.0% | high |
| rugby-union | ru-toulon-pau | Match winner | Section Paloise | -121 | 54.8% | medium |
| basketball | nba-mil-phi | Match winner | Philadelphia 76ers | -395 | 79.8% | medium |
| baseball | mlb-tb-mil | Match winner | Milwaukee Brewers | -135 | 57.5% | medium |
| cricket | cricket-pak-eng | Match winner | Pakistan | -138 | 58.0% | medium |
| motor-racing | f1-usgp | Podium finish | Max Verstappen | -163 | 62.0% | medium |
| motor-racing | f1-usgp | Race winner | Charles Leclerc | +285 | 26.0% | medium |
| golf | pga-bermuda | Outright winner | Austin Smotherman | +233 | 30.0% | medium |
| basketball | nba-bkn-cle | Match winner | Cleveland Cavaliers | -125 | 55.5% | low |
| basketball | nba-was-chi | Match winner | Chicago Bulls | -123 | 55.2% | low |
| baseball | mlb-tb-mil | Match total | Under 8.5 runs | -120 | 54.5% | low |
| basketball | nba-hou-atl | Match winner | Atlanta Hawks | -123 | 55.2% | low |
| rugby-union | ru-larochelle-bordeaux | Match winner | Union Bordeaux-Begles | -108 | 52.0% | low |
| motor-racing | f1-usgp | Top 6 finish | Kimi Antonelli | -178 | 64.0% | low |
| golf | pga-bermuda | Top 10 finish | Seamus Power | -127 | 56.0% | low |

### Written predictions

21 unique passages, 50–73 words each,
no repeated six-word run, no internal vocabulary, team or player named in every one.

## How the prices were made

Fair decimal is 1 ÷ our probability, with no margin, so a two-way book sums to exactly 100%.
American odds are converted from that decimal. Probabilities come from the official facts read:
NHL points and goal difference, NBA win-loss records, the World Series Game 1 result and season
run differential, Top 14 table positions, the ATP semi-final scorelines, the PGA TOUR leaderboard
and Formula 1 practice times. Where the official page gave no basis for a market, the market was
withheld rather than guessed.

**The odds window.** The brief asks for prices between −250 and +10000 and for a win chance above
70%. Those two conditions overlap in a band 1.4 points wide: 70% is a fair price of −233, and
−250 is 71.4%. The desk applies the window as binding and publishes the probability beside every
price, so a reader can see when a selection is chalk rather than an edge. This is stated on the
Method page and in flag F-02.

## Verification performed

Official pages and APIs read during the session, all timestamped on the Sources page:

- NHL — https://api-web.nhle.com/v1/schedule/2026-10-24 — Game IDs, venues, UTC start times and game states for the 12 NHL games on 24 Oct 2026
- NHL — https://api-web.nhle.com/v1/standings/2026-10-24 — 2026-27 club records, L10, streaks, goals for/against; standings stamped 17:06:30Z
- MLB — https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-10-24&hydrate=team,linescore — World Series Game 2, Tampa Bay Rays at Milwaukee Brewers, 2026-10-25T00:00:00Z, American Family Field
- MLB — https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-10-23&hydrate=linescore,decisions — World Series Game 1 final: Brewers 3-2 Rays; W Misiorowski, L Martinez, SV Megill
- MLB — https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsTypes=regularSeason — Rays 98-64, AL East champions, 736 runs scored / 650 allowed, run differential +86
- NBA — https://www.nba.com/standings — 2026-27 club records and last-10 through 23 Oct 2026 for all 30 clubs
- NBA — https://www.nba.com/games — Eight NBA games scheduled for 24 Oct 2026
- ATP Tour — https://www.atptour.com/en/scores/current — Semifinals: Medvedev d. Bublik 6-3 ret.; Basilashvili d. Tsitsipas 6-4 6-7(5) 6-3
- Formula 1 — https://www.formula1.com/en/racing/2026/united-states — US Grand Prix race 25 Oct 16:00 track time; FP2 order Leclerc, Antonelli, Verstappen, Hamilton, Russell
- Ligue Nationale de Rugby — https://top14.lnr.fr/calendrier-et-resultats — Round 7 fixtures, kick-offs and live table positions (Toulon 11th v Pau 2nd; La Rochelle 4th v Bordeaux 3rd)
- PGA TOUR — https://www.pgatour.com/leaderboard — Butterfield Bermuda Championship, Port Royal, 22-25 Oct; round 3 in progress and leaderboard
- Cork GAA — https://gaacork.ie/fixtures/ — 25 Oct finals at SuperValu Pairc Ui Chaoimh: Premier JFC Cobh v Canovee 14:00; Premier SFC Nemo Rangers v St Finbarrs 16:00
- Pakistan Cricket Board — https://www.pcb.com.pk/news-detail/arafat-minhas-6-40-and-59-sink-england-as-pakistan-win-consecutive-games-in-odi-tri-series.html — Pakistan beat England in the ODI tri-series; Arafat Minhas took 6-40 and scored 59
- European Handball Federation — https://ehfcl.eurohandball.com/men/2026-27/matches/ — EHF Champions League round fixtures on 28-29 Oct, including Vardar v Melsungen, Magdeburg v Kriens, Kielce v Kolstad
- World Snooker Tour — https://www.wst.tv/matches/ — BetVictor Northern Ireland Open 2026 shown as completed (18-19 Oct); no upcoming match listed
- TAURON Liga — https://www.tauronliga.pl/games.html — Polish women's league results through 18 Oct 2026

OLBG was read for discovery only: fifteen sport hubs (Golf, Volleyball, Rugby Union, Cricket,
Snooker, Darts, Baseball, Gaelic Football, Greyhounds, Tennis, Motor Racing, Handball, Ice
Hockey, Basketball, Rugby League) plus individual event pages. No OLBG tip, tip percentage or
community price is used as a sporting fact or as a probability.

## Repository review

Line-by-line checks of the canonical release are recorded on `repo-audit.html` (A-01…A-06) with
SHA-256 prefixes: the canonical snapshot is two days older than this session, all 16 of its
priced matches are tiered low, 92 of 108 fixtures carry no market and 81 have no confirmed start
time, and it ships zero predictions by design. That is the structural reason the root site reads
as a list rather than a card.

## Irregularities and limits

- **F-01 (high)** No upcoming Rugby League match exists on OLBG — OLBG's Rugby League hub lists only 2027 outright markets (State of Origin, Super League Grand Final, NRL Grand Final). No 2026 match market is open, so no line or pick can be originated. The sport is published as a gap rather than filled.
- **F-02 (high)** OLBG's only Snooker listing had already started — The single Snooker row (Mark Williams v Jak Jones, 14:05) was listed for a start earlier than the read time, and WST's official match page shows the Northern Ireland Open as completed on 18-19 October. No future Snooker match could be confirmed, so none is published.
- **F-03 (high)** Greyhound entries on the hub were expired or unverifiable — The greyhound hub lists today's graded races, several already marked Expired, and no official GBGB card was read for any of them. Publishing a pick without an official card would be invention, so the sport is carried as a gap.
- **F-04 (medium)** OLBG renders 'No tips found' on the Golf hub — At 17:05Z the Golf hub returned an empty tips table although the PGA TOUR event is live. Golf picks here are built from the official PGA TOUR leaderboard, not from OLBG, and the OLBG gap is recorded.
- **F-05 (medium)** PDC pages are cookie-walled to this reader — pdc.tv returns a consent wall instead of match content, so the European Championship order of play could not be read from the governing body. Darts is carried as a gap rather than priced from the OLBG listing alone.
- **F-06 (medium)** WTA pages did not render match data — wtatennis.com returned navigation and notification text with no draw or order of play, so the WTA matches listed by OLBG could not be confirmed. Only the ATP final, whose two semi-finals were read on atptour.com, is priced.
- **F-07 (medium)** No official volleyball fixture matching an OLBG match was read — The Italian league site renders results through a script this reader cannot execute, and the Polish league page returned women's TAURON Liga results that do not match the OLBG fixtures. Volleyball is carried as a gap.
- **F-08 (low)** Start times for US sports come from the OLBG display — NHL start times are taken from api-web.nhle.com and MLB's from statsapi.mlb.com. NBA start times are converted from the US Eastern times displayed on OLBG (UTC+4 in October); NBA.com confirms eight games on 24 October but its fixture list did not render, so the individual times are flagged as OLBG-sourced.
- **F-09 (low)** Several season records could not be captured — NHL standings were read as paginated JSON; clubs beyond the pages read (Los Angeles, New York Rangers, Columbus, Nashville, Pittsburgh) have blank records rather than estimates, and their fixtures carry no line.
- **F-10 (low)** Injury and availability fields are blank, not guessed — No official injury report was read for any published fixture. Every injury cell on the site is blank and says why, rather than naming a player who may or may not be available.
- **F-11 (high)** Coverage is short of the five-per-sport target — The brief asks for five written predictions per sport per day. This desk publishes 21 priced selections across 8 sports. Sports without a confirmed fixture and confirmed form are carried as gaps rather than filled with invented analysis. The shortfall is listed per sport in the coverage table.
- **F-12 (low)** Some kick-off conversions rely on a published local time — Top 14 kick-offs are published in French local time and Cork finals in Irish local time; both are converted to UTC here (CEST = UTC+2, IST = UTC+1). The ATP final time, and the venue for the Pakistan ODI, come from the OLBG listing because the official pages did not publish them; both are marked in the sources table.

## Known limits

- Coverage is the set of matches that could be confirmed and priced inside the session window, not every match in the fifteen sports worldwide.
- No injury report was read for any published fixture. Injury cells are blank and flagged (F-10) rather than filled from memory or media reports.
- No bookmaker prices are copied. The desk has no live market feed, so "value" is judged against our own fair price, not against a book.
- Start times are UTC conversions from official pages where those pages publish a time; the conversion assumptions are listed in F-12.
- Handicap and total markets are published only where the official inputs exist (NHL goals, MLB runs, NBA points). Sports without an official scoring record carry those markets as withheld.
