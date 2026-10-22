# Session 9dfd0b48-olbg1 — matchday desk 22–24 October 2026 (task T44)

**Board:** https://buffedlizard55-lab.github.io/OLBG1/9dfd0b48/ · **Data:** `data/9dfd0b48/` · **Build:** `python3 scripts/s9dfd0b48_build.py && python3 scripts/s9dfd0b48_validate.py`

## What was done
1. All 17 in-scope OLBG hubs harvested at 2026-10-22 03:10Z (event IDs, listed times, visible tip consensus). OLBG renders hub times in US Eastern (UTC-4) without a label; the finding from `reports/OLBG_REVERSE_ENGINEERING.md` was re-confirmed against ATP local orders of play (Lyon 14:00 CEST = OLBG 08:00; Almaty 11:30 ALMT = OLBG 02:30).
2. Fixtures re-read from governing bodies before pricing: ATP Tour orders of play (Almaty, Brussels, Lyon) and the 19 Oct ATP ranking list (ranks 1–191); World Snooker Tour match list and official ranking list (top 36); EuroLeague Game Center Round 7 and standings; MLB Stats API World Series schedule and 2026 standings.
3. 29 verified fixtures, 27 priced (81 two-way markets = 162 selections), 27 picks, 3 High with written predictions, 70 flag-register items. Two ATP fixtures (Herbert v Fritz, Goffin v Michelsen) are published blank because one player sits outside the 191 ranks read.
4. Everything OLBG listed that could not be read from an official page (WTA Osaka, NBA, PDC European Championship, SHL/Liiga, cricket, rugby, handball, volleyball, golf, F1, Gaelic football) is on the Flagged page with the reason and the official endpoint that failed or was not reached.

## Picks
| ID | Start (UTC) | Fixture | Pick | P | Price | Conf. | Featured | Source |
|---|---|---|---|---|---|---|---|---|
| T01 | 2026-10-22T06:30Z | Terence Atmane v Mattia Bellucci | Mattia Bellucci | 53.8% | -127 | Low | Mattia Bellucci -127 | [official](https://www.atptour.com/en/scores/current/almaty/9410/daily-schedule) |
| T02 | 2026-10-22T08:00Z | Tomas Machac v Karen Khachanov | Karen Khachanov | 62.6% | -185 | Medium | Karen Khachanov -185 | [official](https://www.atptour.com/en/scores/current/almaty/9410/daily-schedule) |
| T03 | 2026-10-22T09:30Z | Daniil Medvedev v Sho Shimabukuro | Daniil Medvedev | 73.8% | -318 | High | Daniil Medvedev -4.5 -123 | [official](https://www.atptour.com/en/scores/current/almaty/9410/daily-schedule) |
| T04 | 2026-10-22T14:30Z | Alexander Bublik v Fabian Marozsan | Alexander Bublik | 63.1% | -188 | Medium | Alexander Bublik -188 | [official](https://www.atptour.com/en/scores/current/almaty/9410/daily-schedule) |
| T05 | 2026-10-22T11:30Z | Raphael Collignon v Jiri Lehecka | Jiri Lehecka | 61.2% | -173 | Medium | Jiri Lehecka -173 | [official](https://www.atptour.com/en/scores/current/brussels/7485/daily-schedule) |
| T07 | 2026-10-22T15:00Z | Damir Dzumhur v Zizou Bergs | Zizou Bergs | 57.4% | -148 | Low | Zizou Bergs -148 | [official](https://www.atptour.com/en/scores/current/brussels/7485/daily-schedule) |
| T08 | 2026-10-22T12:00Z | Valentin Vacherot v Luca Van Assche | Valentin Vacherot | 54.5% | -131 | Low | Valentin Vacherot -131 | [official](https://www.atptour.com/en/scores/current/lyon/496/daily-schedule) |
| T10 | 2026-10-22T17:00Z | Flavio Cobolli v Stan Wawrinka | Flavio Cobolli | 77.1% | -384 | High | Flavio Cobolli -5.5 -125 | [official](https://www.atptour.com/en/scores/current/lyon/496/daily-schedule) |
| T11 | 2026-10-22T18:30Z | Kyrian Jacquet v Brandon Nakashima | Brandon Nakashima | 66.1% | -216 | Medium | Brandon Nakashima -216 | [official](https://www.atptour.com/en/scores/current/lyon/496/daily-schedule) |
| S01 | 2026-10-22T12:00Z | Matthew Selt v Sam Craigie | Matthew Selt | 50.0% | -109 | Low | Matthew Selt -109 | [official](https://www.wst.tv/matches) |
| S02 | 2026-10-22T12:00Z | Kyren Wilson v Pang Junxu | Kyren Wilson | 60.7% | -170 | Medium | Kyren Wilson -170 | [official](https://www.wst.tv/matches) |
| S03 | 2026-10-22T13:00Z | Anthony McGill v Mateusz Baranowski | Anthony McGill | 50.0% | -109 | Low | Anthony McGill -109 | [official](https://www.wst.tv/matches) |
| S04 | 2026-10-22T13:00Z | Elliot Slessor v Ricky Walden | Elliot Slessor | 55.7% | -138 | Low | Elliot Slessor -138 | [official](https://www.wst.tv/matches) |
| S05 | 2026-10-22T18:00Z | Mark Williams v Martin O'Donnell | Mark Williams | 64.5% | -201 | Medium | Mark Williams -201 | [official](https://www.wst.tv/matches) |
| S06 | 2026-10-22T18:00Z | David Gilbert v Ka Wai Cheung | David Gilbert | 51.2% | -115 | Low | David Gilbert -115 | [official](https://www.wst.tv/matches) |
| S07 | 2026-10-22T19:00Z | Jordan Brown v Scott Donaldson | Jordan Brown | 50.0% | -109 | Low | Jordan Brown -109 | [official](https://www.wst.tv/matches) |
| S08 | 2026-10-22T19:00Z | Jak Jones v Daniel Wells | Jak Jones | 55.3% | -136 | Low | Jak Jones -136 | [official](https://www.wst.tv/matches) |
| B01 | 2026-10-22T17:30Z | Anadolu Efes Istanbul v Besiktas Istanbul | Anadolu Efes Istanbul | 54.5% | -131 | Low | Anadolu Efes Istanbul -131 | [official](https://www.euroleaguebasketball.net/en/euroleague/game-center/) |
| B02 | 2026-10-22T18:00Z | FC Bayern Munich v Dubai Basketball | FC Bayern Munich | 50.7% | -113 | Low | FC Bayern Munich -113 | [official](https://www.euroleaguebasketball.net/en/euroleague/game-center/) |
| B03 | 2026-10-22T18:05Z | Maccabi Rapyd Tel Aviv v Real Madrid | Real Madrid | 58.3% | -153 | Medium | Real Madrid -153 | [official](https://www.euroleaguebasketball.net/en/euroleague/game-center/) |
| B04 | 2026-10-22T18:15Z | Panathinaikos AKTOR Athens v Kosner Baskonia Vitoria-Gasteiz | Panathinaikos AKTOR Athens | 94.1% | -2657 | High | Panathinaikos AKTOR Athens -18.5 -119 | [official](https://www.euroleaguebasketball.net/en/euroleague/game-center/) |
| B05 | 2026-10-22T18:30Z | Armani Olimpia Milan v FC Barcelona | FC Barcelona | 61.6% | -177 | Medium | FC Barcelona -177 | [official](https://www.euroleaguebasketball.net/en/euroleague/game-center/) |
| B06 | 2026-10-22T18:45Z | Partizan Mozzart Bet Belgrade v Crvena Zvezda Meridianbet Belgrade | Crvena Zvezda Meridianbet Belgrade | 51.0% | -114 | Low | Crvena Zvezda Meridianbet Belgrade -114 | [official](https://www.euroleaguebasketball.net/en/euroleague/game-center/) |
| B07 | 2026-10-23T17:00Z | Zalgiris Kaunas v LDLC ASVEL Villeurbanne | Zalgiris Kaunas | 66.2% | -217 | Medium | Zalgiris Kaunas -217 | [official](https://www.euroleaguebasketball.net/en/euroleague/game-center/) |
| B08 | 2026-10-23T18:15Z | Olympiacos Piraeus v Fenerbahce Tarfin Istanbul | Olympiacos Piraeus | 55.5% | -137 | Low | Olympiacos Piraeus -137 | [official](https://www.euroleaguebasketball.net/en/euroleague/game-center/) |
| B09 | 2026-10-23T18:45Z | Paris Basketball v Valencia Basket | Valencia Basket | 69.0% | -248 | Medium | Valencia Basket -248 | [official](https://www.euroleaguebasketball.net/en/euroleague/game-center/) |
| M01 | 2026-10-24T00:00Z | Milwaukee Brewers v Tampa Bay Rays | Milwaukee Brewers | 61.4% | -175 | Medium | Milwaukee Brewers -175 | [official](https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-22&endDate=2026-10-28) |

## High-confidence write-ups
- **Daniil Medvedev v Sho Shimabukuro** — Daniil Medvedev -4.5 (-123), 84 words. Sources: https://www.atptour.com/en/scores/current/almaty/9410/daily-schedule, https://www.atptour.com/en/rankings/singles?rankRange=0-100, https://www.atptour.com/en/rankings/singles?rankRange=101-200
- **Flavio Cobolli v Stan Wawrinka** — Flavio Cobolli -5.5 (-125), 75 words. Sources: https://www.atptour.com/en/scores/current/lyon/496/daily-schedule, https://www.atptour.com/en/rankings/singles?rankRange=0-100, https://www.atptour.com/en/rankings/singles?rankRange=101-200
- **Panathinaikos AKTOR Athens v Kosner Baskonia Vitoria-Gasteiz** — Panathinaikos AKTOR Athens -18.5 (-119), 72 words. Sources: https://www.euroleaguebasketball.net/en/euroleague/game-center/, https://www.euroleaguebasketball.net/en/euroleague/standings/

## Flag register (70)
ATP-NOTSEEN: 1, ATP-QF: 1, CLOCK: 1, EMPTY: 4, NBA: 4, NHL-PARTIAL: 1, NOSRC: 28, PDC: 16, REPO: 5, UNPRICED: 2, WTA: 7

Key reasons: PDC pages are a CookieYes consent wall for the fetch client (16 darts matches unpriced); cdn.nba.com returned HTTP 500 (4 NBA games unpriced); the WTA Osaka draw page did not render match data (7 WTA matches unpriced; OLBG labels the event "Tokyo" while the WTA calendar lists Osaka — taxonomy irregularity); NHL schedule confirmed 12 games but only five matchups were read, so the slate was left unpriced rather than half-listed.

## Repository review findings
- COORDINATION §1 T41 row still shows PR/merge as "—" while §33 records the merge (table/section mismatch).
- 7a5b5360 NI Open R3 pairings and session times re-checked on wst.tv 22 Oct: no drift.
- OLBG Basketball hub: Maccabi v Real Madrid is staged in Belgrade (Aleksandar Nikolic Hall); OLBG does not surface the neutral venue.

## Sources
See `data/9dfd0b48/sources.json` / `9dfd0b48/sources.html` — 18 official/attempted pages and 17 OLBG hubs with fetch times.

## Gates
`scripts/s9dfd0b48_validate.py` OK · `scripts/validate.py` VALIDATION PASSED · `scripts/final_audit.py` OK (222+ pages, every table row carries an HTTPS source link).
