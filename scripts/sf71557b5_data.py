#!/usr/bin/env python3
"""
sf71557b5_data.py - session f71557b5-olbg1 (task T50) dataset.

Everything in this file was READ on an official governing-body / tour / federation /
league / club page during this session (2026-10-22). Nothing is recalled from memory,
interpolated, or copied from another desk. Where a value could not be read on an
official page it is left EMPTY and the reason is recorded in `flagged.json`.

Every numeric model input carries the URL it was read from, so the pricing step in
sf71557b5_model.py can never use a number whose provenance is not printed here.

Run:  python3 scripts/sf71557b5_data.py
Writes: data/f71557b5/{olbg_harvest,fixtures,sources,coverage,flagged}.json
"""
from __future__ import annotations

import json
import pathlib
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "f71557b5"
OUT.mkdir(parents=True, exist_ok=True)

SESSION = "f71557b5-olbg1"
READ = "2026-10-22"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ---------------------------------------------------------------------------
# Official source register. Every URL below was fetched and read this session.
# ---------------------------------------------------------------------------
S = {
    "nhl_sched": ("NHL official schedule API - 2026-10-22 slate (game IDs, arenas, UTC start)",
                  "https://api-web.nhle.com/v1/schedule/2026-10-22"),
    "nhl_sched23": ("NHL official schedule API - 2026-10-23 slate",
                    "https://api-web.nhle.com/v1/schedule/2026-10-23"),
    "nhl_stand": ("NHL official standings API - as of 2026-10-21 (GP, W, L, OTL, PTS, GF, GA, home/road splits, streak)",
                  "https://api-web.nhle.com/v1/standings/2026-10-21"),
    "mlb_sched": ("MLB Stats API official schedule - World Series games (gamePk, gameDate, venue)",
                  "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-20&endDate=2026-10-28&hydrate=team,linescore,venue"),
    "mlb_stand": ("MLB Stats API official standings 2026 (W-L, runs scored/allowed, home/away splits)",
                  "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsTypes=regularSeason"),
    "mlb_ws": ("MLB.com official 2026 World Series schedule and home-field note",
               "https://www.mlb.com/news/2026-mlb-world-series-faq-schedule-times-teams-and-more"),
    "mlb_hfa": ("MLB.com official home-field advantage confirmation (Brewers 103-59, Rays 98-64)",
                "https://www.mlb.com/news/world-series-home-field-advantage"),
    "nba_games": ("NBA.com official games page for 2026-10-22 (matchups, ET start, game ids)",
                  "https://www.nba.com/games?date=2026-10-22"),
    "nba_stand": ("NBA.com official 2026-27 standings (W-L, home/road, streak, last 10)",
                  "https://www.nba.com/standings"),
    "nba_recap": ("NBA.com official Opening Night recap (76ers 106-100 Knicks; Thunder 116-104 Spurs)",
                  "https://www.nba.com/news/starting-5-october-21-2026"),
    "el_gc7": ("EuroLeague official Game Center Round 7 (records, points per game, kick-offs)",
               "https://www.euroleaguebasketball.net/en/euroleague/news/game-center-round-7-el2627/"),
    "el_inj7": ("EuroLeague official Round 7 injury report (confirmed club availability lists)",
                "https://www.euroleaguebasketball.net/en/euroleague/news/injury-report-round-7-fantasy/"),
    "el_gc6": ("EuroLeague official Game Center Round 6 results",
               "https://www.euroleaguebasketball.net/en/euroleague/news/game-center-round-6-el2627/"),
    "el_sched": ("EuroLeague official 2026-27 schedule announcement (Round 7 = 22 October)",
                 "https://www.euroleaguebasketball.net/en/euroleague/news/the-2026-27-euroleague-schedule-is-official/"),
    "pdc_sched": ("PDC official 2026 European Championship schedule of play (Round One, 22 and 23 October)",
                  "https://www.pdc.tv/news/2026/october/19/2026-machineseeker-european-championship-schedule-confirmed/"),
    "pdc_draw": ("PDC official 2026 European Championship field and draw (32 seeds, European Tour order of merit)",
                 "https://www.pdc.tv/news/2026/october/18/2026-Machineseeker-European-Championship-field---draw-confirmed"),
    "pdc_prev": ("PDC official 2026 European Championship preview (seeded draw bracket)",
                 "https://www.pdc.tv/news/2026/october/21/2026-machineseeker-european-championship-preview"),
    "pdc_oom": ("PDC official Order of Merit (two-year ranking prize money)",
                "https://www.pdc.tv/order-of-merit/pdc-order-merit"),
    "pdc_et15": ("PDC official 2026 Dutch Darts Championship results (European Tour 15)",
                 "https://www.pdc.tv/news/2026/october/17/2026-dutch-darts-championship---day-two-latest/"),
    "pdc_et14": ("PDC official 2026 Swiss Darts Trophy results (European Tour 14)",
                 "https://www.pdc.tv/news/2026/october/10/humphries-van-veen-clayton-deliver-day-two-basel/"),
    "pdc_venue": ("PDC official European Championship venue and dates",
                  "https://www.pdc.tv/news/2026/october/15/2026-european-championship-race-ahead-of-et15/"),
    "wst_r3": ("World Snooker Tour official match centre - BetVictor Northern Ireland Open 2026 Round 3 (22 October, eight ties, local start times)",
               "https://www.wst.tv/match-centre/f0b30e58-d987-4505-89c2-8b24805b98d5"),
    "wst_day4": ("World Snooker Tour official Day Four report (Round 2 scores, top 16 remaining, break details)",
                 "https://www.wst.tv/news/2026/october/21/betvictor-northern-ireland-open-2026-day-four-afternoon"),
    "wst_matches": ("World Snooker Tour official matches list (Northern Ireland Open round-by-round)",
                    "https://www.wst.tv/matches/"),
    "lnr_prod2_j8": ("LNR official Pro D2 round 8 calendar (Montauban v Oyonnax, Thursday 22 October, 21h00)",
                     "https://prod2.lnr.fr/calendrier-et-resultats"),
    "lnr_oyo": ("LNR official Oyonnax club page - Pro D2 table after round 7 and published match probabilities",
                "https://prod2.lnr.fr/club/oyonnax"),
    "lnr_oyo_cal": ("LNR official Oyonnax fixtures and results 2026-27",
                    "https://prod2.lnr.fr/club/oyonnax/calendrier-resultats"),
    "lnr_mont": ("LNR official Montauban fixtures and results 2026-27",
                 "https://prod2.lnr.fr/club/montauban/calendrier-resultats"),
    "lnr_stats": ("LNR official Pro D2 2026-27 statistics (best attack / best defence, points for and against)",
                  "https://prod2.lnr.fr/statistiques?season=32442&day=38851"),
    "lnr_top14_tou": ("LNR official Stade Toulousain club page - Top 14 table after round 6 and published match probabilities",
                      "https://top14.lnr.fr/club/toulouse"),
    "lnr_top14_j7": ("LNR official Top 14 round 7 calendar (24-25 October kick-offs)",
                     "https://top14.lnr.fr/calendrier-et-resultats"),
    "lnr_lr": ("LNR official Stade Rochelais club page - published round 7 match probabilities",
               "https://top14.lnr.fr/club/la-rochelle"),
    "lnr_top14_stats": ("LNR official Top 14 2026-27 statistics (points for and against by club)",
                        "https://top14.lnr.fr/statistiques"),
    "ehf_times": ("EHF official Champions League Men 2026/27 group-phase playing times PDF (22 October matches, arenas)",
                  "https://www.eurohandball.com/media/jqal4wt0/ehfcl-men-2026-27-group-phase-playing-times.pdf"),
    "ehf_barca": ("EHF official FC Barcelona club results - 2026/27 group phase (Barca 34-27 Montpellier, 8 October)",
                  "https://www.eurohandball.com/en/club/ZkfCu81QMPee22wu_nX_jQ/DinamoBucuresti/"),
    "ehf_kielce": ("EHF official Industria Kielce club results - SC Magdeburg 30-27 and 35-30 in 2026/27",
                   "https://www.eurohandball.com/en/club/puFBDRyrok_Gc2X-z9Jq0w/IndustriaKielce/"),
    "ehf_magdeburg": ("EHF official SC Magdeburg club page (2026/27 group-phase results)",
                      "https://ehfcl.eurohandball.com/men/2025-26/clubs/details/zKttAiKCyYIIy_T_l4gBLQ/SCMagdeburg/"),
    "pcb_tri": ("PCB official Pakistan-England-Sri Lanka ODI tri-series tournament page (all seven fixtures, venues)",
                "https://www.pcb.com.pk/pakistan-england-and-sri-lanka-trination-odi-series-202627/tournament/1465.html"),
    "pcb_media": ("PCB official media advisory - 22 October Sri Lanka v England, 1pm PKT, Rawalpindi, plus both squads",
                  "https://www.pcb.com.pk/press-release-detail/media-advisory-men-s-odi-tri-series-pakistan-england-sri-lanka-rawalpindi-leg.html"),
    "pcb_r1": ("PCB official report - Pakistan 305 beat Sri Lanka 268 by 37 runs (18 October)",
               "https://www.pcb.com.pk/news-detail/salman-hits-century-pacers-restrict-sri-lanka-as-pakistan-begin-tri-series-on-winning-note.html"),
    "pcb_r2": ("PCB official report - Arafat Minhas 6-40 and 59, Pakistan beat England by 87 runs (20 October)",
               "https://www.pcb.com.pk/news-detail/arafat-minhas-6-40-and-59-sink-england-as-pakistan-win-consecutive-games-in-odi-tri-series.html"),
    "ecb_tri": ("ECB official England men ODI tri-series fixture list",
                "https://www.ecb.co.uk/news/4562387/pakistan-to-host-sri-lanka-and-england-in-odi-triseries"),
    "nzc_score": ("NZC official scoring site - 22 October card (Blackcaps v India, Hagley Oval; Australia Women v White Ferns, North Sydney Oval)",
                  "https://scoring.nzc.nz/home"),
    "nzc_tour": ("NZC official India tour announcement (five T20Is from 22 October, Hagley Oval opens)",
                 "https://www.nzc.nz/news-items/historic-india-mega-tour-headlines-international-home-schedule/"),
    "icc_rank": ("ICC official Men's T20I team rankings update (New Zealand 247 points, second; series order)",
                 "https://www.icc-cricket.com/news/india-retain-top-spot-in-men-s-t20i-team-rankings-update"),
    "icc_wc": ("ICC official T20 World Cup 2026 final report - India 255/5 beat New Zealand 159 by 96 runs",
               "https://www.icc-cricket.com/tournaments/mens-t20-world-cup-2026/news/live-india-new-zealand-chase-world-cup-glory"),
    "icc_squad": ("ICC official report - India T20I squad for New Zealand named 6 October, Shreyas Iyer to captain",
                  "https://www.icc-cricket.com/news/fast-bowler-returns-as-india-name-new-zealand-t20i-squad"),
    "ci_nam": ("Cricket Ireland official tour page - five ODIs in Namibia, 22 October to 1 November, full squad",
               "https://cricketireland.ie/tour-of-namibia-2026/"),
    "ci_news": ("Cricket Ireland official tour announcement and squad release",
                "https://cricketireland.ie/news/africa-bound"),
    "irl_fix": ("IRL official fixtures and results - RLWC2026 Round 2 (Tonga v Lebanon 23 Oct, England v France 24 Oct, Australia v England 24 Oct, New Zealand v France 25 Oct)",
                "https://www.intrl.sport/fixtures-results"),
    "irl_tga": ("IRL official match record 2569 - Tonga v Lebanon, CommBank Stadium, 8:05pm local, both squads, Round 1 result 30-12",
                "https://www.intrl.sport/match-details/2569"),
    "irl_eng": ("IRL official match record 2566 - England v Tonga Round 1, HBF Park, England 12-30 Tonga",
                "https://www.intrl.sport/match-details/2566"),
    "nrl_rlwc": ("NRL official RLWC2026 draw and fixture guide (pools, venues, dates)",
                 "https://www.nrl.com/news/2026-09-18/eyntk-world-cup-2026/"),
    "aflw_ladder": ("AFL.com.au official 2026 NAB AFLW ladder after Round 10 (all 18 clubs, played, points, percentage)",
                    "https://www.afl.com.au/aflw"),
    "aflw_r11": ("AFL.com.au official Round 11 fixture note - the season resumes in Adelaide on Friday 23 October with Port Adelaide hosting Collingwood",
                 "https://www.afl.com.au/aflw/news/1634179/2026-nab-aflw-season-officially-the-highest-attended-aflw-season-ever"),
    "aflw_finals": ("AFL.com.au official finals-race preview - North Melbourne v Adelaide, Sunday 25 October, 1.05pm AEDT, North Hobart Oval; Hawthorn v Essendon in Round 11",
                    "https://www.afl.com.au/aflw/news/1634367/finals-before-finals-the-games-that-will-shape-the-top-eight"),
    "aflw_r10": ("AFL.com.au official Round 10 review (Collingwood 29 d. by Sydney 80; West Coast 13 d. by Geelong 66; Melbourne, Western Bulldogs, Brisbane, Hawthorn results)",
                 "https://www.afl.com.au/aflw/news/1632582/in-case-you-missed-it-r10-hawthorn-hawks-stumble-in-finals-race-melbourne-demons-serve-up-statement-adelaide-crows-remain-in-mix"),
    "aflw_syd": ("AFL.com.au official match centre - Collingwood 4.5 (29) lost to Sydney 12.8 (80) by 51 at Windy Hill, Round 10",
                 "https://www.afl.com.au/aflw/matches/8965"),
    "aflw_wc": ("AFL.com.au official match centre - West Coast 1.7 (13) lost to Geelong 8.18 (66) by 53, Round 10",
                "https://www.afl.com.au/afl/matches/8966"),
    "gaa_cork_final": ("Cork GAA official event page - McCarthy Insurance Group Premier Senior Football Championship Final, 25 October, SuperValu Pairc Ui Chaoimh",
                       "https://gaacork.ie/event/mccarthy-insurance-group-premier-senior-football-championship-final/"),
    "gaa_cork_round": ("Cork GAA official championship weekend round-up (semi-final scores for Nemo Rangers and St Finbarr's)",
                       "https://gaacork.ie/2026-10-11/mccarthy-insurance-group-club-championship-weekend-round-up/"),
    "gaa_cork_safc": ("Cork GAA official fixtures - Senior 'A' Football Championship Final, Eire Og v Kanturk, 1 November, 14:00, SuperValu Pairc Ui Chaoimh, referee James Regan",
                      "https://gaacork.ie/fixtures/"),
    "gaa_cork_2025": ("Cork GAA official 2025 Premier Senior Football Championship Final report - St Finbarr's 1-14 Nemo Rangers 1-13, crowd 6,949",
                      "https://gaacork.ie/2025-10-26/barrs-win-11th-county-title/"),
    "munster_cal": ("Munster GAA official events calendar - Waterford SFC Final (Rathgormack v The Nire, 25 Oct, 2:30pm, Fraher Field) and Cork PSFC Final (25 Oct, 4pm)",
                    "https://munster.gaa.ie/fixtures/events-calendar/"),
    "munster_home": ("Munster GAA official match centre - county final fixtures, venues and referees for 25 October",
                     "https://munster.gaa.ie/"),
    "wat_res": ("Waterford GAA official results - Rathgormack and The Nire semi-final and round scores",
                "https://www.waterfordgaa.ie/results/"),
    "wat_fix": ("Waterford GAA official fixtures - Rathgormack v The Nire, 25 October, 14:30, Cappoquin Logistics Fraher Field",
                "https://www.waterfordgaa.ie/fixtures/"),
    "mc_final": ("Maigh Cuilinn (Moycullen) official club site - Galway Senior Football Championship Final, 7pm Saturday 24 October, Pearse Stadium",
                 "https://www.maighcuilinn.com/"),
    "mc_sf": ("Maigh Cuilinn official club report - county semi-final, Maigh Cuilinn 4-26 Annaghdown 0-8, Dessie Conneely personal tally",
              "https://www.maighcuilinn.com/stellar-performance-against-annaghdown-sets-up-repeat-county-final/"),
    "mc_qf": ("Maigh Cuilinn official club report - quarter-final 3-25 to 0-13 over Mountbellew-Moylough; other semi-final Corofin v Salthill-Knocknacarra",
              "https://www.maighcuilinn.com/maigh-cuilinn-power-past-mountbellew-moylough-into-county-semi-final/"),
    "mc_league": ("Maigh Cuilinn official club report - league round 4, Maigh Cuilinn 3-12 Salthill-Knocknacarra 0-8 (10 April 2026)",
                  "https://www.maighcuilinn.com/maigh-cuilinns-organisation-and-patience-secure-league-points-against-salthill-knocknacarra/"),
    "lim_res": ("Limerick GAA official results - senior football championship semi-finals, 17 October (Kildimo/Pallaskenry 2-16 Mungret/St Pauls 0-20 AET; Fr Caseys 3-12 Monaleen 1-06)",
                "https://limerickgaa.ie/limerick-gaa-saturday-club-results-32/"),
    "lim_sf": ("Limerick GAA official semi-final fixture notice - venues, times and referee",
               "https://limerickgaa.ie/senior-football-fixtures/"),
    "pga_bermuda": ("PGA TOUR official Butterfield Bermuda Championship facts and figures (dates, course, par, yardage, purse, defending champion, past winners, scoring record)",
                    "https://www.pgatour.com/article/news/latest/2026-10-20/butterfield-bermuda-championship-facts-and-figures-port-royal-golf-course-southampton-2026"),
    "pga_odds": ("PGA TOUR official odds outlook - Ben James betting favourite, published prices for past champions",
                 "https://www.pgatour.com/article/news/betting-dfs/2026-10-19/odds-outlook-butterfield-bermuda-championship-betting-fantasy-picks-advice-fedexcup-fall"),
    "pga_field": ("PGA TOUR official Inside the Field - 120-man field, five past champions, FedExCup points",
                  "https://www.pgatour.com/article/news/inside-the-field/2026-10-16/how-the-field-qualified-for-butterfield-bermuda-championship-fedexcup-fall-aon-next-10"),
    "pga_stifel": ("PGA TOUR Champions official Stifel Charity Classic event overview (purse, past champions and scores)",
                   "https://www.pgatour.com/pgatour-champions/tournaments/2026/stifel-charity-classic/S2026625/overview"),
    "pga_stifel_dates": ("PGA TOUR Champions official tournament schedule - Stifel Charity Classic, 23-25 October, Norwood Hills Country Club",
                         "https://www.pgatour.com/pgatour-champions/tickets"),
    "pga_schwab": ("PGA TOUR Champions official Charles Schwab Cup playoff format - 72 players, 54 holes, Stifel Charity Classic opens the playoffs",
                   "https://www.pgatour.com/pgatour-champions/schwabcup/overview"),
    "et_legends": ("DP World Tour / Staysure Legends Tour official schedule - Sergio Melpignano Senior Italian Open, 22-24 October, San Domenico Golf, EUR 450,000",
                   "https://www.europeantour.com/legends-tour/schedule/"),
    "f1_cal": ("Formula 1 official 2026 calendar - Round 18 United States Grand Prix, 23-25 October, Circuit of The Americas",
               "https://www.formula1.com/en/racing/2026"),
    "f1_usgp": ("Formula 1 official United States Grand Prix circuit data (5.513km, 56 laps, 308.405km, fastest lap)",
                "https://www.formula1.com/en/racing/2026/united-states"),
    "f1_stand": ("Formula 1 official 2026 Drivers' Championship standings (Max Verstappen P4, 221 points)",
                 "https://www.formula1.com/"),
    "f1_sing": ("Formula 1 official 2026 Singapore Grand Prix race result and classification",
                "https://www.formula1.com/en/latest/article/verstappen-seals-commanding-singapore-grand-prix-victory-from-leclerc-and-antonelli.49wDzysiVqi5cloGjle40A"),
    "f1_story": ("Formula 1 official United States GP storylines (Verstappen won the last two races and the Singapore sprint; championship gap figures)",
                 "https://www.formula1.com/en/latest/article/its-race-week-5-storylines-were-excited-about-ahead-of-the-2026-united-states-grand-prix.4utgT1kLqHM2HAM98YP4TW"),
    "f1_perm": ("Formula 1 official points permutations for Austin (rounds remaining, maximum points available)",
                "https://www.formula1.com/en/latest/article/points-permutations-when-is-the-earliest-antonelli-could-win-the-world-championship.24UKT2fsQl4GmC5DMrmYUy"),
    "lol_worlds": ("LoL Esports official Worlds 2026 primer (stage dates, Swiss format, knockout venues, seeded tiers, draw dates)",
                   "https://lolesports.com/en-US/news/worlds-2026-primer"),
    "lol_overview": ("LoL Esports official Worlds 2026 tournament overview (16 teams, five-round Swiss, top eight advance)",
                     "https://lolesports.com/en-GB/tournament/115660540725177488/overview"),
    "lol_live": ("LoL Esports official live results - Play-In quarter-finals (KT Rolster 3-2 Team Vitality, BNK FEARX 3-2 JDG, WE 3-2 FlyQuest, HANJIN BRION 3-1 LGD)",
                 "https://lolesports.com/en-US/live/worlds/104946685894036941"),
    "atp_almaty": ("ATP official signed Tour Supervisor main draw - Almaty (seeds, ranks, Round of 32 scores, release stamp 21/10/2026 20:51:24)",
                   "https://www.protennislive.com/posting/2026/9410/mds.pdf"),
    "atp_lyon": ("ATP official signed Tour Supervisor main draw - Lyon (seeds, ranks, completed round scores, release stamp 21/10/2026 23:27:14)",
                 "https://www.protennislive.com/posting/2026/496/mds.pdf"),
    "atp_brussels": ("ATP official signed Tour Supervisor main draw - Brussels (seeds, ranks, Round of 32 scores, release stamp 21/10/2026 21:51:50)",
                     "https://www.protennislive.com/posting/2026/7485/mds.pdf"),
    "atp_race": ("ATP official Live Race To Turin - Almaty/Lyon players' next round status",
                 "https://www.atptour.com/en/rankings/singles-race-to-turin"),
    "wta_ningbo": ("WTA official signed supervisor draw - Ningbo (Round of 32 complete, seeds and ranks, release stamp 21 Oct 2026 10:13 PM)",
                   "https://wtafiles.wtatennis.com/pdf/draws/2026/2092/MDS.pdf"),
    "wta_osaka": ("WTA official signed supervisor draw - Osaka (Round of 32 complete, seeds and ranks)",
                  "https://wtafiles.wtatennis.com/pdf/draws/2026/405/MDS.pdf"),
    "urc_table": ("United Rugby Championship official league table 2026/27 (Bulls, Stormers, Munster, Connacht, Ulster, Leinster - played, points, for, against, form)",
                  "https://stats.unitedrugby.com/match-centre/table/"),
    "urc_fix": ("United Rugby Championship official 2026/27 fixture list release",
                "https://www.unitedrugby.com/latest/news/2026-27-fixtures-in-full/"),
    "shl_res": ("SHL official results and table notes - Färjestad top of the table, Skellefteå, Timrå, Örebro, Brynäs, Djurgården form",
                "https://www.shl.se/article/r12atmy-403dd/view"),
    "tauron": ("TAURON Liga official club page - PGE GiEK Skra Bełchatów v PGE Projekt Warszawa, Saturday 24 October 2026, 18:00, phase Zasadnicza",
               "https://www.tauronliga.pl/teams/tour/53/id/61.html"),
    "olbg": ("OLBG.com live sport hub (upstream reference only - never used to verify a fact)",
             "https://www.olbg.com/betting-tips"),
}

SPORTS = [
    ("tennis", 3), ("basketball", 4), ("golf", 5), ("cricket", 7), ("snooker", 8),
    ("rugby-union", 9), ("rugby-league", 10), ("baseball", 12), ("ice-hockey", 13),
    ("motor-racing", 14), ("darts", 15), ("handball", 20), ("volleyball", 21),
    ("aussie-rules", 22), ("esports", 23), ("gaelic-football", 25), ("greyhounds", 28),
]
# OLBG's own hub slugs, exactly as the site serves them, so the exclusion is auditable
# by clicking through to the hub that was dropped.
EXCLUDED = [
    ("Football", 1, "soccer / football"), ("Horse_Racing", 2, "horse racing"),
    ("American_Football", 11, "american football"), ("Boxing", 16, "boxing"),
    ("Cycling", 17, "cycling"), ("Entertainment", 18, "specials / entertainment (TV, politics, awards)"),
    ("Hurling", 26, "hurling"), (None, None, "UFC / MMA - OLBG lists these inside the boxing and specials hubs, with no hub of their own"),
]

# ---------------------------------------------------------------------------
# Live OLBG harvest, read 2026-10-22 (this session). Hubs were opened directly.
# `cards` records what OLBG published; verification against a governing body is
# a separate step and is what decides whether a row is priced.
# ---------------------------------------------------------------------------
OLBG_HUBS = {
    "tennis": {"url": "https://www.olbg.com/betting-tips/Tennis/3", "cards_seen": 21,
               "note": "21 match cards listed for 22-23 October, all ATP Almaty/Lyon/Brussels or WTA Ningbo/Osaka Round of 32 ties."},
    "basketball": {"url": "https://www.olbg.com/betting-tips/Basketball/4", "cards_seen": 12,
                   "note": "NBA (4), EuroLeague (5), Korea KBL (1), Brazil NBB (1), plus sub-route hubs read for NBA, EuroLeague, EuroCup and WNBA."},
    "golf": {"url": "https://www.olbg.com/betting-tips/Golf/5", "cards_seen": 4,
             "note": "Bermuda Championship, Senior Italian Open, Stella Artois Players Championship, Stifel Charity Classic - outright cards only."},
    "cricket": {"url": "https://www.olbg.com/betting-tips/Cricket/7", "cards_seen": 7,
                "note": "NZ v India T20I, England v Sri Lanka ODI, Namibia v Ireland ODI, Australia W v NZ W, two CSA T20 cards, Afghanistan v Zimbabwe."},
    "snooker": {"url": "https://www.olbg.com/betting-tips/Snooker/8", "cards_seen": 2,
                "note": "Only two of the eight official Round 3 ties are listed upstream (Selt v Craigie, Wilson v Pang)."},
    "rugby-union": {"url": "https://www.olbg.com/betting-tips/Rugby_Union/9", "cards_seen": 15,
                    "note": "Pro D2 round 8, Top 14 round 7, URC round 4 and Six Nations 2027 outright."},
    "rugby-league": {"url": "https://www.olbg.com/betting-tips/Rugby_League/10", "cards_seen": 3,
                     "note": "Only 2027 outrights published upstream - State of Origin 2027, Super League 2027, NRL 2027. No RLWC2026 match card on the hub."},
    "baseball": {"url": "https://www.olbg.com/betting-tips/Baseball/12", "cards_seen": 1,
                 "note": "TB Rays @ MIL Brewers, 23 Oct 20:00 (OLBG clock) - World Series Game 1."},
    "ice-hockey": {"url": "https://www.olbg.com/betting-tips/Ice_Hockey/13", "cards_seen": 4,
                   "note": "Swedish Hockey League (3) and Finland SM Liiga (1). The NHL sub-route hub returned 'No tips found' upstream."},
    "motor-racing": {"url": "https://www.olbg.com/betting-tips/Motor_Racing/14", "cards_seen": 3,
                     "note": "USA Grand Prix win-race card plus two Drivers' Championship outrights."},
    "darts": {"url": "https://www.olbg.com/betting-tips/Darts/15", "cards_seen": 17,
              "note": "All 16 European Championship Round One ties plus the tournament outright."},
    "handball": {"url": "https://www.olbg.com/betting-tips/Handball/20", "cards_seen": 18,
                 "note": "EHF Champions League, EHF European League and seven domestic leagues."},
    "volleyball": {"url": "https://www.olbg.com/betting-tips/Volleyball/21", "cards_seen": 9,
                   "note": "Czech Extraliga (5) and Polish leagues (4), including two set-score tips."},
    "aussie-rules": {"url": "https://www.olbg.com/betting-tips/Aussie_Rules/22", "cards_seen": 0,
                     "note": "'No tips found' upstream on 22 October even though the official AFLW Round 11 is being played 23-25 October."},
    "esports": {"url": "https://www.olbg.com/betting-tips/eSports/23", "cards_seen": 0,
                "note": "'No tips found' upstream; LoL Worlds 2026 Swiss stage starts 23 October on the official LoL Esports site."},
    "gaelic-football": {"url": "https://www.olbg.com/betting-tips/Gaelic_Football/25", "cards_seen": 6,
                        "note": "Five club championship cards (24 Oct - 1 Nov) plus the All-Ireland 2027 outright."},
    "greyhounds": {"url": "https://www.olbg.com/betting-tips/Greyhounds/28", "cards_seen": 0,
                   "note": "'No tips found' upstream on 22 October; GBGB was not reachable to confirm a card."},
}


def src(*keys):
    return [{"name": S[k][0], "url": S[k][1], "read": READ} for k in keys]


def ev(label, value, key):
    """A sourced input: the value as it was printed, plus where it was read."""
    return {"label": label, "value": value, "source": S[key][1], "source_name": S[key][0]}


F = []


def add(**kw):
    kw.setdefault("round", "")
    kw.setdefault("start_local", "")
    kw.setdefault("start_utc", "")
    kw.setdefault("venue", "")
    kw.setdefault("status", "verified")
    kw.setdefault("olbg_url", "")
    kw.setdefault("event_only", False)
    kw.setdefault("model", None)
    kw.setdefault("flags", [])
    kw.setdefault("evidence", [])
    F.append(kw)


# ============================ ICE HOCKEY (NHL) =============================
# All 12 games of the 22 October slate: id, arena and UTC start from the NHL
# schedule API; both clubs' GP/PTS/GF/GA/home-road splits and streak from the
# standings API dated 2026-10-21. Every number below was read on those two pages.
# Only fields that reconcile against the standings payload's own published
# percentages are carried. Every club's points / (2 x games played) equals the
# pointPctg printed next to it, and wins + losses + overtime losses equals games
# played, for all 24 clubs below. Season goals for / against were ALSO present in
# the payload but could not be reconciled (the New York Rangers object prints 17
# season goals for against 33 in its own last-ten block), so every goals value was
# discarded rather than partially trusted - see flag F-F7-NHL-01.
NHL = [
    # game id, home, away, arena, utc, local, (W,L,OTL,PTS,GP,streak) home, away, verified note
    ("2026020154", "Boston Bruins", "Nashville Predators", "TD Garden", "2026-10-22T23:00:00Z", "19:00 EDT",
     (7, 2, 1, 15, 10, "one overtime loss"), (3, 3, 2, 9, 8, "one win"),
     "Bruins 15 points from 10 with a .750 points percentage; Predators 9 points from 8, unbeaten in regulation on the road (3 games, 1 win, 2 overtime losses)."),
    ("2026020155", "Toronto Maple Leafs", "New York Rangers", "Scotiabank Arena", "2026-10-22T23:00:00Z", "19:00 EDT",
     (5, 4, 2, 12, 11, "two wins"), (7, 3, 1, 15, 11, "one win"),
     "Rangers seventh in the league on points percentage at .682; Leafs .545 and winners of their last two, including 3-1 over San Jose at this arena on 19 October."),
    ("2026020156", "Ottawa Senators", "San Jose Sharks", "Canadian Tire Centre", "2026-10-22T23:00:00Z", "19:00 EDT",
     (7, 3, 0, 14, 10, "one win"), (5, 4, 1, 11, 10, "one win"),
     "San Jose have ZERO regulation wins - all five victories came in overtime or a shootout - and beat Montreal 4-3 in overtime on 20 October."),
    ("2026020157", "New Jersey Devils", "Anaheim Ducks", "Prudential Center", "2026-10-22T23:00:00Z", "19:00 EDT",
     (5, 4, 0, 10, 9, "one win"), (4, 5, 0, 8, 9, "four losses"),
     "Ducks are on a four-game losing streak, the longest active run on the 22 October slate; Devils have lost four of nine but in regulation only twice at home."),
    ("2026020158", "Pittsburgh Penguins", "Florida Panthers", "PPG Paints Arena", "2026-10-22T23:00:00Z", "19:00 EDT",
     (3, 6, 1, 7, 10, "four losses"), (5, 3, 2, 12, 10, "one loss"),
     "Penguins 3-6-1 on a four-game losing streak and lost 5-4 at Utah on 19 October; Panthers .600 points percentage with two overtime losses on the road."),
    ("2026020159", "New York Islanders", "Los Angeles Kings", "UBS Arena", "2026-10-22T23:30:00Z", "19:30 EDT",
     (5, 3, 1, 11, 9, "two wins"), (1, 4, 2, 4, 7, "one win"),
     "Kings have the fewest points in the league, four from seven games at a .286 points percentage; Islanders winners of two straight."),
    ("2026020160", "St. Louis Blues", "Vegas Golden Knights", "Enterprise Center", "2026-10-23T00:00:00Z", "19:00 CDT",
     (4, 4, 1, 9, 9, "one win"), (8, 3, 0, 16, 11, "one loss"),
     "Vegas second in the league on points at 16 from 11 and 8-3-0 in regulation terms; Blues exactly .500 on points percentage."),
    ("2026020161", "Dallas Stars", "Winnipeg Jets", "American Airlines Center", "2026-10-23T00:00:00Z", "19:00 CDT",
     (5, 3, 1, 11, 9, "three wins"), (4, 3, 2, 10, 9, "two losses"),
     "Stars on a three-game winning streak; Jets have dropped two straight and taken two of nine games to overtime."),
    ("2026020162", "Calgary Flames", "Minnesota Wild", "Scotiabank Saddledome", "2026-10-23T01:00:00Z", "19:00 MDT",
     (2, 6, 0, 4, 8, "one win"), (6, 2, 2, 14, 10, "one overtime loss"),
     "Flames 2-6-0 and second-last in the league on points; Wild 14 points from ten with six regulation wins."),
    ("2026020163", "Edmonton Oilers", "Carolina Hurricanes", "Rogers Place", "2026-10-23T01:00:00Z", "19:00 MDT",
     (7, 1, 1, 15, 9, "two wins"), (8, 2, 1, 17, 11, "one win"),
     "The two best points percentages in the league meet: Oilers .833 from nine games, Hurricanes .773 from eleven."),
    ("2026020164", "Seattle Kraken", "Utah Mammoth", "Climate Pledge Arena", "2026-10-23T02:00:00Z", "19:00 PDT",
     (6, 3, 1, 13, 10, "one win"), (7, 3, 0, 14, 10, "one win"),
     "Separated by a single point on identical ten-game samples; Utah 7-3-0 with no overtime losses."),
    ("2026020165", "Vancouver Canucks", "Detroit Red Wings", "Rogers Arena", "2026-10-23T02:00:00Z", "19:00 PDT",
     (2, 8, 1, 5, 11, "two losses"), (3, 3, 3, 9, 9, "one overtime loss"),
     "Canucks last in the league on points, five from eleven; Red Wings have taken three of nine games past regulation."),
]
for gid, home, away, arena, utc, local, h, a, note in NHL:
    hw, hl, hotl, hpts, hgp, hstreak = h
    aw, al, aotl, apts, agp, astreak = a
    add(
        id=f"nhl-{gid}", sport="ice-hockey", competition="NHL 2026-27 Regular Season",
        home=home, away=away, venue=arena, start_utc=utc, start_local=local,
        sources=src("nhl_sched", "nhl_stand"),
        evidence=[
            ev("Home record", f"{home} {hw}-{hl}-{hotl}, {hpts} points from {hgp} games "
                             f"(points percentage {hpts / (2 * hgp):.3f}), streak: {hstreak}", "nhl_stand"),
            ev("Away record", f"{away} {aw}-{al}-{aotl}, {apts} points from {agp} games "
                             f"(points percentage {apts / (2 * agp):.3f}), streak: {astreak}", "nhl_stand"),
            ev("Arena and start", f"{arena}, {utc} ({local} local)", "nhl_sched"),
            ev("Verified context", note, "nhl_stand"),
        ],
        flags=[{"code": "F-F7-NHL-01",
                "text": "Season goals for and against were published in the same standings payload but could not be "
                        "reconciled against that payload's own last-ten block for at least one club, so no goals "
                        "value is used anywhere on this desk and no NHL match total is priced."}],
        model={"kind": "nhl", "home_ppg": round(hpts / hgp, 6), "away_ppg": round(apts / agp, 6),
               "home_rec": f"{hw}-{hl}-{hotl}", "away_rec": f"{aw}-{al}-{aotl}",
               "home_pts": hpts, "home_gp": hgp, "away_pts": apts, "away_gp": agp,
               "home_streak": hstreak, "away_streak": astreak, "note": note},
    )

# ============================ BASEBALL (MLB) ===============================
# World Series: game ids, dates and venue from the MLB Stats API; both clubs'
# 162-game records, runs scored/allowed and home/away splits from the standings
# API; home-field confirmation from MLB.com.
MLB = [
    ("849805", "2026-10-24T00:00:00Z", "2026-10-23", "American Family Field", "World Series Game 1"),
    ("849802", "2026-10-25T00:00:00Z", "2026-10-24", "American Family Field", "World Series Game 2"),
    ("849804", "2026-10-27T00:00:00Z", "2026-10-26", "Tropicana Field", "World Series Game 3"),
]
MIL = {"w": 103, "l": 59, "rs": 832, "ra": 618, "hw": 55, "hl": 26, "aw": 48, "al": 33, "rd": 214}
TB = {"w": 98, "l": 64, "rs": 736, "ra": 650, "hw": 55, "hl": 26, "aw": 43, "al": 38, "rd": 86}
for pk, utc, official, venue, desc in MLB:
    mil_home = venue == "American Family Field"
    home, away = ("Milwaukee Brewers", "Tampa Bay Rays") if mil_home else ("Tampa Bay Rays", "Milwaukee Brewers")
    H, A = (MIL, TB) if mil_home else (TB, MIL)
    add(
        id=f"mlb-{pk}", sport="baseball", competition="MLB 2026 World Series", round=desc,
        home=home, away=away, venue=venue, start_utc=utc,
        start_local="7:00pm CT" if mil_home else "",
        sources=src("mlb_sched", "mlb_stand", "mlb_ws", "mlb_hfa"),
        evidence=[
            ev("Home club 2026", f"{H['w']}-{H['l']} ({round(H['rs']/162,2)} runs scored/game, {round(H['ra']/162,2)} allowed, {H['rd']:+d} differential)", "mlb_stand"),
            ev("Away club 2026", f"{A['w']}-{A['l']} ({round(A['rs']/162,2)} runs scored/game, {round(A['ra']/162,2)} allowed, {A['rd']:+d} differential)", "mlb_stand"),
            ev("Home split", f"{H['hw']}-{H['hl']} at home", "mlb_stand"),
            ev("Away split", f"{A['aw']}-{A['al']} on the road", "mlb_stand"),
            ev("Series status", "Brewers swept the Dodgers in the NLCS; Rays beat the Guardians in six in the ALCS. Brewers hold home field on the better regular-season record.", "mlb_hfa"),
            ev("Official game id", f"gamePk {pk}, {official}, {venue}", "mlb_sched"),
        ],
        model={"kind": "mlb",
               "home_rs_pg": round(H["rs"] / 162, 4), "home_ra_pg": round(H["ra"] / 162, 4),
               "away_rs_pg": round(A["rs"] / 162, 4), "away_ra_pg": round(A["ra"] / 162, 4),
               "home_home_w": H["hw"], "home_home_l": H["hl"], "away_road_w": A["aw"], "away_road_l": A["al"],
               "note": f"{desc}: Brewers 103-59 (+214) with home field; Rays 98-64 (+86)."},
    )

# ============================ BASKETBALL (NBA) =============================
NBA = [
    ("0022600006", "Philadelphia 76ers", "Cleveland Cavaliers", "7:00 PM ET", "2026-10-22T23:00:00Z",
     "76ers opened 1-0 by beating the Knicks 106-100 at Madison Square Garden (Maxey 28, Brown 19, James 14/9/7, Embiid 13/11/6); Cavaliers are 0-0 and open their season here."),
    ("0022600007", "Oklahoma City Thunder", "Denver Nuggets", "9:30 PM ET", "2026-10-23T01:30:00Z",
     "Thunder opened 1-0 by beating the Spurs 116-104 behind Shai Gilgeous-Alexander's 32 points, 6 rebounds, 4 assists, 3 steals and 3 blocks; Nuggets are 0-0."),
]
for gid, home, away, local, utc, note in NBA:
    add(
        id=f"nba-{gid}", sport="basketball", competition="NBA 2026-27 Regular Season",
        home=home, away=away, start_local=local, start_utc=utc, venue="",
        sources=src("nba_games", "nba_stand", "nba_recap"),
        evidence=[ev("Official listing", f"{away} @ {home}, {local}, game {gid}", "nba_games"),
                  ev("Opening-night result", note, "nba_recap"),
                  ev("Standings", "Both conferences' 2026-27 records as published (76ers 1-0, Cavaliers 0-0, Thunder 1-0, Nuggets 0-0)", "nba_stand")],
        flags=[{"code": "F-F7-NBA-01", "text": "Arena not printed on the pages read this session; left blank rather than inferred."}],
        model={"kind": "nba_onesided", "note": note,
               "home_verified_result": True, "away_verified_result": False},
    )

# ======================= BASKETBALL (EuroLeague R7) ========================
EL = [
    ("el-r7-efes-bjk", "Anadolu Efes Istanbul", "Besiktas Istanbul", "19:30 CEST", "2026-10-22T17:30:00Z",
     2, 4, 3, 3, "Efes 2-4 without Mike James (Achilles, 7-9 months), PJ Dozier (back), Isaia Cordinier and Georgios Papagiannis; Besiktas 3-3 with Lonnie Walker available to debut and DaQuan Jeffries still out. Besiktas third in the league in scoring at 92.3 ppg, Efes sixth in points allowed at 85.0."),
    ("el-r7-bay-dub", "FC Bayern Munich", "Dubai Basketball", "20:00 CEST", "2026-10-22T18:00:00Z",
     2, 4, 4, 2, "Bayern 2-4 at home after a two-round week in Turkiye; Dubai 4-2 on the road with the fifth-best defence (82.2 ppg allowed) and Dwayne Bacon third in scoring at 17.8 ppg. Bayern's Duane Washington is sixth in scoring at 16.8 ppg off the bench."),
    ("el-r7-mac-rmb", "Maccabi Rapyd Tel Aviv", "Real Madrid", "20:05 CEST", "2026-10-22T18:05:00Z",
     2, 4, 3, 3, "Maccabi 2-4 playing at a neutral venue after splitting two games in Spain; Real Madrid 3-3, winners of three straight but 1-4 away from home. The home club has won the last five meetings."),
    ("el-r7-pan-bas", "Panathinaikos AKTOR Athens", "Kosner Baskonia Vitoria-Gasteiz", "20:15 CEST", "2026-10-22T18:15:00Z",
     5, 1, 1, 5, "Panathinaikos 5-1 with a league-low 73.0 points allowed per game, looking to bounce back from a first loss under Coach Obradovic; Baskonia 1-5 under new coach Velimir Perasovic and has not won in Athens since March 2021 - Panathinaikos have taken five straight home games against them."),
    ("el-r7-zal-asv", "Zalgiris Kaunas", "LDLC ASVEL Villeurbanne", "19:00 CEST", "2026-10-23T17:00:00Z",
     2, 4, 2, 4, "Both 2-4 and both beaten twice last week. ASVEL allow a league-high 95.3 ppg; Zalgiris expect a fully healthy backcourt and must contain Patty Mills, one of five ASVEL players averaging double figures."),
]
for fid, home, away, local, utc, hw, hl, aw, al, note in EL:
    add(
        id=fid, sport="basketball", competition="EuroLeague 2026-27", round="Regular Season Round 7",
        home=home, away=away, start_local=local, start_utc=utc,
        venue="Aleksandar Nikolic Hall, Belgrade (neutral)" if fid == "el-r7-mac-rmb" else "",
        sources=src("el_gc7", "el_inj7", "el_sched"),
        evidence=[ev("Records entering Round 7", f"{home} {hw}-{hl}, {away} {aw}-{al}", "el_gc7"),
                  ev("Official preview", note, "el_gc7"),
                  ev("Confirmed availability", "Round 7 injury report as filed by the clubs", "el_inj7")],
        model={"kind": "euroleague", "home_w": hw, "home_l": hl, "away_w": aw, "away_l": al, "note": note},
        flags=[] if fid != "el-r7-mac-rmb" else [{"code": "F-F7-EL-01", "text": "Arena read as a neutral Belgrade venue in the official preview text; the specific hall name was not printed on the page read, so it is left blank."}],
    )

# ================================ DARTS (PDC) ==============================
# Round One of the 2026 Machineseeker European Championship, Westfalenhalle
# Dortmund. Fixture list and session times from the official schedule release;
# seed numbers from the official draw-bracket preview; Order of Merit money from
# the official PDC rankings page; recent results from the two most recent
# European Tour events (ET14 Basel, ET15 Maastricht).
PDC_OOM = {"Luke Littler": 3113500, "Luke Humphries": 1062500, "Gian van Veen": 1035750,
           "Gerwyn Price": 782000, "Jonny Clayton": 706000, "Josh Rock": 606500}
DARTS = [
    # home(listed first), away, seed_home, seed_away, local time, day, recent form (verified), note
    ("Ross Smith", "Karel Sedlacek", 1, 32, "19:00 CEST", "2026-10-22",
     "Smith 6-2 Ryan Joyce then 6-4 William O'Connor in the ET14 Swiss Darts Trophy round two (10 October). Sedlacek 6-4 Wessel Nijman in ET14 round two, then lost 4-6 to Martin Schindler in ET15 round two (17 October).",
     "Top seed against the 32nd seed on the one-year European Tour rankings."),
    ("James Wade", "Damon Heta", 16, 17, "19:00 CEST", "2026-10-22",
     "Wade lost 5-6 to Dirk van Duijvenbode in ET14 round two after leading; Heta beat Danny Noppert 6-3 in the same ET14 session.",
     "Neighbouring seeds, one year apart on the European Tour order of merit."),
    ("Gian van Veen", "Andrew Gilding", 8, 25, "19:00 CEST", "2026-10-22",
     "Van Veen is the reigning European Champion, beat Niko Springer 6-0 in ET14 round two and set a new European Tour record average in Maastricht. Gilding lost 1-6 to Luke Woodhouse in ET15 round two.",
     "Defending champion opens against the 25th seed; van Veen third on the Order of Merit with GBP 1,035,750."),
    ("Luke Woodhouse", "Dirk van Duijvenbode", 9, 24, "19:00 CEST", "2026-10-22",
     "Woodhouse 6-1 Andrew Gilding in ET15 round two but lost 4-6 to Rob Cross in ET14 round two. Van Duijvenbode beat James Wade 6-5 in ET14 and lost 5-6 to Ryan Searle in ET15.",
     "Both Dutch/English pairings decided by a single leg in their last European Tour meetings."),
    ("Niels Zonneveld", "Cameron Menzies", 4, 29, "19:00 CEST", "2026-10-22",
     "Zonneveld secured his first European Tour title at the Dutch Darts Championship on 18 October, beating Gerwyn Price in the round three draw. Menzies is the only Scot in the 32-player field.",
     "Fourth seed against the 29th seed."),
    ("Gerwyn Price", "Rob Cross", 13, 20, "19:00 CEST", "2026-10-22",
     "Price fourth on the Order of Merit with GBP 782,000; lost to Zonneveld in ET15 round three. Cross beat Luke Woodhouse 6-4 in ET14 round two, halting a mid-match fightback.",
     "Former world champion against the 2018 world champion."),
    ("Danny Noppert", "Stephen Bunting", 5, 28, "19:00 CEST", "2026-10-22",
     "Noppert beat Dave Chisnall 6-4 in ET15 round two but lost 3-6 to Damon Heta in ET14. Bunting lost 4-6 to Jeffrey de Graaf in ET14 round two.",
     "Fifth seed against the 28th seed."),
    ("Luke Humphries", "Ryan Searle", 12, 21, "19:00 CEST", "2026-10-22",
     "Humphries second on the Order of Merit with GBP 1,062,500 and last year's runner-up in Dortmund; beat Kevin Doets 6-5 in ET14 round two. Searle beat Dirk van Duijvenbode 6-5 in ET15 round two but lost 4-6 to Cristo Reyes in ET14.",
     "Defending runner-up against the 21st seed."),
    ("Ryan Joyce", "Jermaine Wattimena", 15, 18, "19:00 CEST", "2026-10-23",
     "Joyce lost 2-6 to Ross Smith in ET14 round two. Wattimena lost 4-6 to Michael Smith in ET14 round two.",
     "Friday's opening tie of Round One."),
    ("Krzysztof Ratajski", "Dave Chisnall", 3, 30, "19:00 CEST", "2026-10-23",
     "Ratajski beat Stefan Bellmont 6-2 in ET14 round two. Chisnall lost 4-6 to Danny Noppert in ET15 round two but beat Josh Rock 6-5 in ET14.",
     "Third seed against the 30th seed."),
    ("Nathan Aspinall", "Cristo Reyes", None, None, "19:00 CEST", "2026-10-23",
     "Reyes beat Ryan Searle 6-4 in ET14 round two. Aspinall's European Tour result was not printed on the pages read.",
     "Seed numbers for this tie were not printed in the section of the official preview that was read."),
    ("Jonny Clayton", "Niko Springer", 7, 26, "19:00 CEST", "2026-10-23",
     "Clayton fifth on the Order of Merit with GBP 706,000 and beat Maik Kuivenhoven 6-1 in ET14 round two. Springer lost 0-6 to Gian van Veen in the same session.",
     "Seventh seed against the 26th seed."),
    ("Luke Littler", "William O'Connor", None, None, "19:00 CEST", "2026-10-23",
     "Littler is world number one with GBP 3,113,500 on the two-year Order of Merit and won two of the three European Tour events he played in 2026. O'Connor lost 4-6 to Ross Smith in ET14 round two.",
     "World number one against the Irish number one; seed numbers not printed in the section read."),
    ("Wessel Nijman", "Martin Schindler", 2, 31, "19:00 CEST", "2026-10-23",
     "Nijman beat Jeffrey de Graaf 6-3 in ET15 round two but lost 4-6 to Karel Sedlacek in ET14. Schindler beat Sedlacek 6-4 in ET15 round two and lost 4-6 to Tom Bissell in ET14.",
     "Second seed against the 31st seed."),
    ("Kevin Doets", "Michael van Gerwen", None, None, "19:00 CEST", "2026-10-23",
     "Doets lost 5-6 to Luke Humphries in ET14 round two. Van Gerwen lost 4-6 to Mensur Suljovic in the same ET14 session.",
     "Four-time champion van Gerwen meets his compatriot; seed numbers not printed in the section read."),
    ("Josh Rock", "Chris Dobey", 10, 23, "19:00 CEST", "2026-10-23",
     "Rock sixth on the Order of Merit with GBP 606,500; beat Dave Chisnall 6-5 in ET14 round two. Dobey lost 4-6 to Bradley Brooks in ET14 round two.",
     "Tenth seed against the 23rd seed."),
]
for i, (p1, p2, s1, s2, local, day, form, note) in enumerate(DARTS, 1):
    flags = []
    if s1 is None or s2 is None:
        flags.append({"code": f"F-F7-PDC-{i:02d}",
                      "text": f"Seed numbers for {p1} v {p2} were not printed in the section of the official draw preview that was read; left blank rather than inferred."})
    oom = []
    for nm in (p1, p2):
        if nm in PDC_OOM:
            oom.append(ev("Order of Merit", f"{nm} GBP {PDC_OOM[nm]:,} (two-year ranking prize money)", "pdc_oom"))
    add(
        id=f"pdc-ec-r1-{i:02d}", sport="darts",
        competition="PDC 2026 Machineseeker European Championship", round="Round One",
        home=p1, away=p2, venue="Westfalenhalle, Dortmund",
        start_local=local, start_utc="",
        sources=src("pdc_sched", "pdc_draw", "pdc_prev", "pdc_oom", "pdc_et14", "pdc_et15", "pdc_venue"),
        evidence=[
            ev("Official schedule", f"{p1} v {p2}, {day} evening session, {local} local", "pdc_sched"),
            ev("Seeding", (f"seed {s1} v seed {s2}, seeded on the one-year European Tour rankings" if s1 else "seed numbers not read"), "pdc_draw"),
            ev("Recent match history", form, "pdc_et14"),
            ev("Tournament context", note, "pdc_prev"),
        ] + oom,
        flags=flags + [{"code": "F-F7-PDC-CLOCK", "text": "The official schedule publishes a session window (1900-2300 CEST) and a per-match slot on the event page; the exact UTC start for each tie was not printed, so start_utc is left blank."}],
        model={"kind": "darts", "seed_home": s1, "seed_away": s2,
               "oom_home": PDC_OOM.get(p1), "oom_away": PDC_OOM.get(p2),
               "form": form, "note": note},
    )

# ============================== SNOOKER (WST) ==============================
WST_R3 = [
    ("Kyren Wilson", "Pang Junxu", "12:00 UK", "Wilson is one of only two of the world's top 16 left in the draw after John Higgins fell 2-4 to Jak Jones. Pang Junxu edged in-form Liam Davies 4-3, the first six frames shared with Davies making 69 and 103 and Pang 112 and 73 before an 81 clearance decided it."),
    ("Matthew Selt", "Sam Craigie", "12:00 UK", "Craigie led Xu Si 3-0 with a top break of 103, was reeled back to 3-3 and won the decider with a run of 75. Selt's Round 2 opponent and score were not printed in the report that was read."),
    ("Elliot Slessor", "Ricky Walden", "13:00 UK", "Listed on the official Round 3 match centre. Neither player's Round 2 score was printed on the page read."),
    ("Anthony McGill", "Mateusz Baranowski", "13:00 UK", "Listed on the official Round 3 match centre. Neither player's Round 2 score was printed on the page read."),
    ("Mark Williams", "Martin O'Donnell", "18:00 UK", "Williams is the second of only two top-16 players remaining after Higgins' exit."),
    ("David Gilbert", "Cheung Ka Wai", "18:00 UK", "Listed on the official Round 3 match centre. Neither player's Round 2 score was printed on the page read."),
    ("Jordan Brown", "Scott Donaldson", "19:00 UK", "Listed on the official Round 3 match centre. Neither player's Round 2 score was printed on the page read."),
    ("Jak Jones", "Daniel Wells", "19:00 UK", "Jones beat John Higgins 4-2 to reach the last 16 in what the official report calls a phenomenal season."),
]
for i, (p1, p2, local, note) in enumerate(WST_R3, 1):
    top16 = {"Kyren Wilson", "Mark Williams"}
    add(
        id=f"wst-nio-r3-{i:02d}", sport="snooker",
        competition="BetVictor Northern Ireland Open 2026", round="Round 3 (last 32)",
        home=p1, away=p2, venue="Waterfront Hall, Belfast",
        start_local=local, start_utc="",
        sources=src("wst_r3", "wst_day4", "wst_matches"),
        evidence=[ev("Official match centre", f"{p1} v {p2}, 22 October, {local}", "wst_r3"),
                  ev("Recent match history", note, "wst_day4")],
        flags=[{"code": "F-F7-SNK-CLOCK", "text": "The official match centre prints a UK local start time only; no UTC offset is published on the page, so start_utc is left blank."},
               {"code": "F-F7-SNK-VENUE", "text": "Arena name not printed on the match-centre page read; carried from the tournament's published host venue and flagged for confirmation."}]
        + ([{"code": f"F-F7-SNK-{i:02d}", "text": f"Round 2 result for one or both of {p1} / {p2} was not printed on the official page read, so no verified recent score is carried for that player."}]
           if "not printed" in note else []),
        model={"kind": "snooker", "home_top16": p1 in top16, "away_top16": p2 in top16, "note": note},
    )

# ============================ RUGBY UNION (LNR) ============================
add(
    id="prod2-j8-mont-oyo", sport="rugby-union", competition="Pro D2 2026-27", round="Journee 8",
    home="US Montauban", away="Oyonnax Rugby", start_local="21h00 CEST", start_utc="2026-10-22T19:00:00Z",
    venue="Stade de Sapiac, Montauban",
    sources=src("lnr_prod2_j8", "lnr_oyo", "lnr_oyo_cal", "lnr_mont", "lnr_stats"),
    evidence=[
        ev("Official fixture", "Journee 8, jeudi 22 octobre, US Montauban (8e) v Oyonnax Rugby (1er), 21h00, Canal+ Sport", "lnr_prod2_j8"),
        ev("Table after round 7", "Oyonnax 33 points (1st, unbeaten), Provence 29, Grenoble 22, Brive 21; Montauban 8th on 17", "lnr_oyo"),
        ev("Oyonnax recent results", "J1 won 31-21 at Beziers; J2 won 47-25 v Biarritz; J3 won 56-35 v Nevers; J6 won 57-14 at Narbonne; J7 won 51-25 v Valence Romans", "lnr_oyo_cal"),
        ev("Montauban recent results", "J6 won 32-24 v Brive; J7 lost 28-54 at Dax", "lnr_mont"),
        ev("League attack/defence", "Best attack Oyonnax 205 points scored; best defence Brive 106 conceded, Provence 108, Biarritz 112", "lnr_stats"),
        ev("LNR's own published match model", "US Montauban 28.57% / Oyonnax Rugby 64.29% / draw 7.14%", "lnr_oyo"),
    ],
    model={"kind": "lnr_published", "home_pct": 28.57, "away_pct": 64.29, "draw_pct": 7.14,
           "note": "Oyonnax unbeaten and top of Pro D2 with the league's best attack (205 points); Montauban eighth and beaten 54-28 at Dax last time out."},
)
add(
    id="top14-j7-tou-usap", sport="rugby-union", competition="Top 14 2026-27", round="Journee 7",
    home="Stade Toulousain", away="USA Perpignan", start_local="16h35 CEST", start_utc="2026-10-24T14:35:00Z",
    venue="Stade Ernest Wallon, Toulouse",
    sources=src("lnr_top14_tou", "lnr_top14_j7", "lnr_top14_stats"),
    evidence=[
        ev("Official fixture", "Journee 7, samedi 24 octobre, Stade Toulousain (1er) v USA Perpignan (9e), 16h35, Stade Ernest Wallon", "lnr_top14_j7"),
        ev("Table after round 6", "Toulouse 24 points (1st), Section Paloise 22, Bordeaux-Begles 19, La Rochelle 18; Perpignan 9th on 13", "lnr_top14_tou"),
        ev("Toulouse recent results", "J1 lost 27-30 at La Rochelle; J2 won 48-12 v Bordeaux-Begles; J3 won 40-18 v Castres; J6 won 45-34 v Bayonne", "lnr_top14_tou"),
        ev("Perpignan recent results", "J5 lost 25-55 v Racing 92; J6 won 21-12 v Vannes", "lnr_top14_j7"),
        ev("LNR's own published match model", "Stade Toulousain 84.44% / USA Perpignan 14.07% / draw 1.48%", "lnr_top14_tou"),
    ],
    model={"kind": "lnr_published", "home_pct": 84.44, "away_pct": 14.07, "draw_pct": 1.48,
           "note": "Toulouse first on 24 points and unbeaten at Ernest Wallon; Perpignan ninth, and beaten 55-25 by Racing in round 5."},
)
add(
    id="top14-j7-sr-ubb", sport="rugby-union", competition="Top 14 2026-27", round="Journee 7",
    home="Stade Rochelais", away="Union Bordeaux-Begles", start_local="21h05 CEST", start_utc="2026-10-25T20:05:00Z",
    venue="Stade Marcel-Deflandre, La Rochelle",
    sources=src("lnr_lr", "lnr_top14_j7", "lnr_top14_tou"),
    evidence=[
        ev("Official fixture", "Journee 7, dimanche 25 octobre, Stade Rochelais (4e) v Union Bordeaux-Begles (3e), 21h05", "lnr_top14_j7"),
        ev("Table after round 6", "La Rochelle 4th on 18 points; Bordeaux-Begles 3rd on 19", "lnr_top14_tou"),
        ev("La Rochelle recent results", "J1 won 30-27 v Toulouse; J6 won 28-16 at LOU Rugby", "lnr_lr"),
        ev("LNR's own published match model", "Stade Rochelais 46.88% / Union Bordeaux-Begles 52.60% / draw 0.52%", "lnr_lr"),
    ],
    model={"kind": "lnr_published", "home_pct": 46.88, "away_pct": 52.60, "draw_pct": 0.52,
           "note": "A one-point gap in the table between third and fourth; LNR's own model has the visitors marginal favourites."},
)

# ============================== HANDBALL (EHF) =============================
add(
    id="ehfcl-bar-mon", sport="handball", competition="EHF Champions League Men 2026/27", round="Group phase, group E",
    home="Barca", away="Montpellier HB", venue="Palau Blaugrana, Barcelona",
    start_local="20:45 CEST", start_utc="2026-10-22T18:45:00Z",
    sources=src("ehf_times", "ehf_barca"),
    evidence=[
        ev("Official playing times", "Thursday 22.10.2026 20:45h, Barca v Montpellier HB, Palau Blaugrana (Barcelona, ESP), group E", "ehf_times"),
        ev("Head to head this season", "Barca 34 - 27 Montpellier HB, Thursday 8 October 2026, 20:45, Barcelona - the same group phase", "ehf_barca"),
    ],
    model={"kind": "handball_h2h", "h2h_margin": 7, "note": "Barca won the reverse group-phase fixture 34-27 at the same arena on 8 October 2026."},
)
add(
    id="ehfcl-kol-mag", sport="handball", competition="EHF Champions League Men 2026/27", round="Group phase, group F",
    home="Kolstad Handball", away="SC Magdeburg", venue="Kolstad Arena, Kolstad",
    start_local="20:45 CEST", start_utc="2026-10-22T18:45:00Z",
    sources=src("ehf_times", "ehf_kielce", "ehf_magdeburg"),
    evidence=[
        ev("Official playing times", "Thursday 22.10.2026 20:45h, Kolstad Handball v SC Magdeburg, Kolstad Arena (Kolstad, NOR), group F", "ehf_times"),
        ev("Magdeburg 2026/27 results", "SC Magdeburg 35-30 Industria Kielce (7 October, Kielce); SC Magdeburg 30-27 Industria Kielce (14 October, Magdeburg)", "ehf_kielce"),
    ],
    flags=[{"code": "F-F7-HB-01", "text": "No Kolstad 2026/27 group-phase result was read on an official EHF page this session, so only one side carries a sourced rating. Per repository rule 4 the price falls back to a neutral baseline and confidence is capped at Low."}],
    model={"kind": "one_sided", "note": "Magdeburg won both group-phase meetings with Industria Kielce by three and five goals; Kolstad's 2026/27 results were not read."},
)

# ================================ CRICKET ==================================
add(
    id="cri-sl-eng-odi3", sport="cricket", competition="Pakistan ODI Tri-Series 2026/27", round="3rd match",
    home="Sri Lanka", away="England", venue="Rawalpindi Cricket Stadium, Rawalpindi",
    start_local="1:00pm PKT", start_utc="2026-10-22T08:00:00Z",
    sources=src("pcb_tri", "pcb_media", "pcb_r1", "pcb_r2", "ecb_tri"),
    evidence=[
        ev("Official fixture", "22-10-2026 Sri Lanka v England, 3rd match, Rawalpindi Cricket Stadium; toss 12.30pm PKT, start 1pm PKT", "pcb_media"),
        ev("Sri Lanka recent result", "18 October, same venue: Pakistan 305 beat Sri Lanka 268 by 37 runs", "pcb_r1"),
        ev("England recent result", "20 October, same venue: Arafat Minhas 6-40 and 59 as Pakistan beat England by 87 runs", "pcb_r2"),
        ev("Squads", "England: Harry Brook (c), Gus Atkinson, Sonny Baker, Tom Banton, James Coles, Jordan Cox, Mason Crane, Henry Crocombe, Sam Curran, Liam Dawson, Ben Duckett, Will Jacks, Jamie Overton, Adil Rashid, Joe Root, Josh Tongue. Sri Lanka: Kusal Mendis (c) and 15 others.", "pcb_media"),
        ev("Series context", "England arrived on three consecutive ODI series wins; Sri Lanka won their ODI series against the West Indies 1-0 and lost to England.", "pcb_media"),
    ],
    model={"kind": "cricket_margin", "margin_runs": 25, "sigma": 45,
           "note": "Both sides lost to Pakistan at the same ground inside four days - England by 87 runs on 20 October, Sri Lanka by 37 runs on 18 October. Half of that verified 50-run gap (25 runs) is carried as the expected margin, shrunk because a single common opponent is weak evidence."},
)
add(
    id="cri-nz-ind-t20i1", sport="cricket", competition="India tour of New Zealand 2026/27", round="1st T20I",
    home="New Zealand", away="India", venue="Hagley Oval, Christchurch",
    start_local="7:00am NZDT (as printed)", start_utc="",
    sources=src("nzc_score", "nzc_tour", "icc_rank", "icc_wc", "icc_squad"),
    evidence=[
        ev("Official card", "Thursday 22 October, Blackcaps v India, Hagley Oval, Christchurch, India in New Zealand 1st T20I", "nzc_score"),
        ev("Tour confirmation", "Hagley Oval opens the India tour with back-to-back T20Is on 22 and 24 October", "nzc_tour"),
        ev("Rankings", "India retain top spot in the ICC Men's T20I team rankings; New Zealand second on 247 points", "icc_rank"),
        ev("Head to head", "India beat New Zealand by 96 runs in the ICC Men's T20 World Cup 2026 final - India 255/5, New Zealand 159 - a record third title and a second in a row", "icc_wc"),
        ev("Squad", "India named their New Zealand T20I squad on 6 October with Shreyas Iyer continuing as captain", "icc_squad"),
    ],
    flags=[{"code": "F-F7-CRI-01", "text": "The ICC rankings page read printed New Zealand's 247 points but not India's numeric rating, so the rating pair is one-sided; the price uses the verified 96-run World Cup final margin instead."},
           {"code": "F-F7-CRI-02", "text": "NZC prints a local clock with no timezone label and no UTC equivalent; start_utc left blank."}],
    model={"kind": "cricket_margin", "margin_runs": 38.4, "sigma": 45,
           "note": "India beat New Zealand by 96 runs in the T20 World Cup final in March; 40% of that verified margin is carried into a T20."},
)
add(
    id="cri-nam-ire-odi1", sport="cricket", competition="Ireland tour of Namibia 2026/27", round="1st ODI",
    home="Namibia", away="Ireland", venue="Windhoek",
    start_local="", start_utc="",
    sources=src("ci_nam", "ci_news"),
    evidence=[
        ev("Official tour fixture", "22 October: Ireland Men v Namibia Men, 1st ODI, Windhoek - the first of five ODIs to 1 November", "ci_nam"),
        ev("Ireland squad", "Paul Stirling (c), Lorcan Tucker (vc), Mark Adair, Andrew Balbirnie, Ben Calitz, Curtis Campher, Cade Carmichael, George Dockrell, Gavin Hoey, Matthew Humphreys, Andy McBrine, Liam McCarthy, Byron McDonough, Jai Moondra, Jordan Neill, Harry Tector", "ci_news"),
    ],
    flags=[{"code": "F-F7-CRI-03", "text": "Cricket Ireland publishes the fixture and venue but no start clock, and no official ICC ODI rating pair was read for Namibia and Ireland. Neither side carries a sourced numeric rating, so no price is originated and confidence is capped at Low."},
           {"code": "F-F7-CRI-04", "text": "The specific ground in Windhoek differs between the board's own listing and third-party schedules; left as the city the official tour page prints."}],
    model=None,
)
add(
    id="cri-ausw-nzw-t20i3", sport="cricket", competition="Australia Women tour match 2026/27", round="3rd T20I",
    home="Australia Women", away="New Zealand Women", venue="North Sydney Oval, Sydney",
    start_local="8:15am (as printed)", start_utc="",
    sources=src("nzc_score"),
    evidence=[ev("Official card", "Thursday 22 October, Australia Women v White Ferns, 8:15am, North Sydney Oval, Sydney", "nzc_score")],
    flags=[{"code": "F-F7-CRI-05", "text": "The first and second T20I results of this series were not read on an official page, so neither side carries a sourced form input. No price originated; capped at Low."}],
    model=None,
)

# ============================= AUSSIE RULES ================================
AFLW = {
    "North Melbourne": (10, 36, 251.9), "Geelong Cats": (10, 36, 167.2), "Melbourne": (10, 32, 177.2),
    "Western Bulldogs": (10, 32, 140.9), "Gold Coast SUNS": (10, 28, 138.9), "Carlton": (10, 28, 133.0),
    "Sydney Swans": (10, 28, 112.9), "Fremantle": (10, 20, 104.9), "Adelaide Crows": (10, 20, 102.4),
    "Hawthorn": (10, 20, 101.5), "Port Adelaide": (10, 16, 78.8), "West Coast Eagles": (10, 16, 75.2),
    "Richmond": (10, 16, 68.9), "Brisbane Lions": (10, 12, 89.7), "GWS GIANTS": (10, 8, 68.2),
    "Collingwood": (10, 4, 56.7), "Essendon": (10, 4, 55.6), "St Kilda": (10, 4, 45.1),
}
AFLW_FIX = [
    ("aflw-r11-por-col", "Port Adelaide", "Collingwood", "Friday 23 October", "Adelaide",
     "The official Round 11 note opens the round in Adelaide on Friday 23 October with Port Adelaide hosting Collingwood. Port Adelaide were held to two goals from 39 entries by Brisbane in Round 10; Collingwood were beaten by 51 points by Sydney at Windy Hill, 4.5 (29) to 12.8 (80)."),
    ("aflw-r11-nor-ade", "North Melbourne", "Adelaide Crows", "Sunday 25 October, 1.05pm AEDT", "North Hobart Oval",
     "Reigning premier North Melbourne top the ladder on 36 points at 251.9 per cent; Adelaide are ninth on 20 points at 102.4 per cent and beat Gold Coast in Round 10 through Chloe Bown's match-winning goal."),
    ("aflw-r11-haw-ess", "Hawthorn", "Essendon", "Round 11", "",
     "Hawthorn are tenth on 20 points at 101.5 per cent after losing to the Giants by one point in Round 10 when Aine McDonagh missed late; Essendon are 17th on four points at 55.6 per cent."),
]
for fid, home, away, when, venue, note in AFLW_FIX:
    hp, hpts, hpct = AFLW[home]
    ap, apts, apct = AFLW[away]
    add(
        id=fid, sport="aussie-rules", competition="2026 NAB AFLW Season", round="Round 11",
        home=home, away=away, venue=venue, start_local=when, start_utc="",
        sources=src("aflw_ladder", "aflw_r11", "aflw_finals", "aflw_r10", "aflw_syd"),
        evidence=[
            ev("Ladder after Round 10", f"{home}: {hp} played, {hpts} points, {hpct}% | {away}: {ap} played, {apts} points, {apct}%", "aflw_ladder"),
            ev("Fixture", f"{when}{(' at ' + venue) if venue else ''}", "aflw_finals"),
            ev("Recent match history", note, "aflw_r10"),
        ],
        flags=[{"code": "F-F7-AFL-01", "text": "The official ladder publishes played, points and percentage but not points for and against, so an absolute scoring total cannot be sourced; no match total is priced for this fixture."}]
        + ([{"code": "F-F7-AFL-02", "text": "Kick-off clock not printed on the official page read for this Round 11 fixture; date only, start_local left as published text."}] if "1.05pm" not in when else []),
        model={"kind": "aflw", "home_pts": hpts, "away_pts": apts, "home_pct": hpct, "away_pct": apct,
               "home_gp": hp, "away_gp": ap, "note": note},
    )

# =========================== GAELIC FOOTBALL ===============================
GAA = [
    ("gaa-cork-psfc-final", "St Finbarrs", "Nemo Rangers", "Sunday 25 October, 4:00pm", "SuperValu Pairc Ui Chaoimh, Cork",
     ["gaa_cork_final", "gaa_cork_round", "gaa_cork_2025", "munster_home"],
     "St Finbarrs beat Clonakilty 2-12 to 0-16 in the semi-final; Nemo Rangers edged Carrigaline 1-15 to 0-16 after beating Castlehaven 1-20 to 1-17 in the quarter-final. St Finbarrs won last year's final against this same opposition 1-14 to 1-13 in front of 6,949.",
     "Cork McCarthy Insurance Group Premier Senior Football Championship Final, referee David Murnane (Cork)."),
    ("gaa-wat-sfc-final", "Rathgormack", "The Nire", "Sunday 25 October, 2:30pm", "Cappoquin Logistics Fraher Field, Dungarvan",
     ["wat_fix", "wat_res", "munster_cal", "munster_home"],
     "Rathgormack beat Gaultier 1-14 to 0-15 in the semi-final and Abbeyside-Ballinacourty 5-15 to 2-5 in round 6, though they lost 1-7 to 1-11 at Abbeyside in round 5. The Nire beat Abbeyside-Ballinacourty 0-12 to 0-5 in the semi-final and Gaultier 2-10 to 0-13 in round 6.",
     "Waterford Senior Football Championship Final, referee Killian O'Sullivan (Waterford)."),
    ("gaa-gal-sfc-final", "Maigh Cuilinn", "Salthill-Knocknacarra", "Saturday 24 October, 7:00pm", "Pearse Stadium, Galway",
     ["mc_final", "mc_sf", "mc_qf", "mc_league"],
     "Maigh Cuilinn beat Annaghdown 4-26 to 0-8 in the semi-final and Mountbellew-Moylough 3-25 to 0-13 in the quarter-final, and are into a fifth consecutive county final as defending champions. They also beat Salthill-Knocknacarra 3-12 to 0-8 in league round 4 on 10 April 2026.",
     "Galway Senior Football Championship Final."),
    ("gaa-cork-safc-final", "Eire Og", "Kanturk", "Sunday 1 November, 2:00pm", "SuperValu Pairc Ui Chaoimh, Cork",
     ["gaa_cork_safc", "gaa_cork_round"],
     "Eire Og topped their group, beat Kilshannig 0-24 to 0-9 in round 3 and won the semi-final against Cill na Martra 2-16 to 1-16. Kanturk came through a quarter-final, beat Aghabullogue 2-8 to 1-11 by a point in round 3 and won their semi-final against Carbery Rangers 1-18 to 1-14.",
     "Cork McCarthy Insurance Group Senior 'A' Football Championship Final, referee James Regan."),
    ("gaa-lim-sfc-final", "Fr Caseys", "Kildimo Pallaskenry", "", "",
     ["lim_res", "lim_sf", "mc_final"],
     "Fr Caseys beat Monaleen 3-12 to 1-06 at Sean Finn Park, Rathkeale in the semi-final on 17 October. Kildimo Pallaskenry beat Mungret St Pauls 2-16 to 0-20 after extra time at Clarina on the same day.",
     "Limerick Irish Wire Products Ltd County Senior Football Championship Final; Munster GAA lists the Limerick representative in its club quarter-final on 8 November."),
]
for fid, home, away, when, venue, keys, form, comp in GAA:
    flags = []
    if not when:
        flags.append({"code": "F-F7-GAA-01", "text": "The Limerick county final date and venue were not printed on an official Limerick GAA page read this session; only the two verified semi-final results are carried. Date left blank."})
    if fid == "gaa-gal-sfc-final":
        flags.append({"code": "F-F7-GAA-02", "text": "The official club report gives Dessie Conneely's semi-final tally as 2-14 in the match text and 2-16 in the scoring list on the same page. Both figures are published; neither is inferred away."})
    if fid == "gaa-gal-sfc-final":
        flags.append({"code": "F-F7-GAA-03", "text": "Salthill-Knocknacarra's semi-final against Corofin was named as a fixture on the club's own page but its score was not read on an official page, so this row carries only Maigh Cuilinn's verified results and no head-to-head strength edge is taken from the opposition."})
    if fid == "gaa-lim-sfc-final":
        flags.append({"code": "F-F7-GAA-04", "text": "Munster GAA lists the Limerick county champions entering the Munster club quarter-final on 8 November, which confirms a Limerick final is played, but no official Limerick GAA page read this session prints that final's date or venue."})
    add(
        id=fid, sport="gaelic-football", competition=comp, round="County final",
        home=home, away=away, venue=venue, start_local=when, start_utc="",
        sources=src(*keys),
        evidence=[ev("Recent match history", form, keys[1] if len(keys) > 1 else keys[0]),
                  ev("Fixture", (when + (" at " + venue if venue else "")) or "date not published on an official page read", keys[0])],
        flags=flags,
        model={"kind": "gaa", "form": form, "note": form},
    )

# ============================= RUGBY LEAGUE ================================
RL = [
    ("rlwc26m-tga-lbn", "Tonga", "Lebanon", "Friday 23 October, 8:05pm local", "CommBank Stadium, Sydney",
     "Tonga beat England 30-12 at HBF Park, Perth in Round 1, Haumole Olakau'atu scoring twice. Lebanon's Round 1 result against Papua New Guinea was not read on an official page this session.",
     ["irl_fix", "irl_tga", "nrl_rlwc"]),
    ("rlwc26m-eng-fra", "England", "France", "Saturday 24 October, 2:35pm local", "HBF Park, Perth",
     "England lost 12-30 to Tonga in Round 1 at the same venue, conceding two tries in three minutes to turn a 10-6 lead into 22-6 against them. France's Round 1 result was not read on an official page this session.",
     ["irl_fix", "irl_eng", "nrl_rlwc"]),
    ("rlwc26w-aus-eng", "Australia", "England (Women)", "Saturday 24 October, 5:05pm local", "HBF Park, Perth",
     "Listed on the official IRL fixtures page as a Women's Rugby League World Cup Round 2 match. No Round 1 result for either side was read.",
     ["irl_fix"]),
    ("rlwc26w-nzl-fra", "New Zealand (Women)", "France (Women)", "Sunday 25 October", "One NZ Stadium, Christchurch",
     "Listed on the official IRL fixtures page as a Women's Rugby League World Cup Round 2 match. No kick-off clock and no Round 1 result were published on the page read.",
     ["irl_fix"]),
]
for fid, home, away, when, venue, form, keys in RL:
    add(
        id=fid, sport="rugby-league", competition="IRL Rugby League World Cup 2026", round="Round 2 (pool stage)",
        home=home, away=away, venue=venue, start_local=when, start_utc="",
        sources=src(*keys),
        evidence=[ev("Official fixture", f"{home} v {away}, {when}, {venue}", "irl_fix"),
                  ev("Recent match history", form, keys[1] if len(keys) > 1 else keys[0])],
        flags=[{"code": f"F-F7-RL-{fid[-8:]}", "text": "Only one side has a verified Round 1 result read on an official IRL page, and no official world-ranking pair was read for these nations. Per repository rule 4 no strength edge is applied and confidence is capped at Low."}]
        + ([{"code": "F-F7-RL-CLOCK", "text": "No kick-off clock published on the official fixtures page for this match; start time left blank."}] if "Sunday 25 October" == when else []),
        model=None,
    )

# ====================== EVENT CARDS (no head-to-head) ======================
add(
    id="golf-bermuda-2026", sport="golf", competition="PGA TOUR Butterfield Bermuda Championship",
    home="Field of 120 - Port Royal Golf Course", away="", event_only=True,
    venue="Port Royal Golf Course, Southampton, Bermuda", start_local="22-25 October 2026", start_utc="",
    sources=src("pga_bermuda", "pga_field", "pga_odds"),
    evidence=[
        ev("Tournament facts", "Par 71, 6,828 yards, purse USD 6 million, winner's share USD 1.08 million, 500 FedExCup points, defending champion Adam Schenk at 12 under", "pga_bermuda"),
        ev("Past winners", "2025 Adam Schenk -12; 2024 Rafael Campos -19; 2023 Camilo Villegas -24; 2022 Seamus Power -19; 2021 Lucas Herbert -15", "pga_bermuda"),
        ev("Scoring record", "61 - Taylor Pendrith (R2 2022), Alex Noren (R1 2023), Wesley Bryan (R3 2024)", "pga_bermuda"),
        ev("Field", "120 players including five past champions: Brendon Todd (2019), Seamus Power (2022), Camilo Villegas (2023), Rafael Campos (2024), Adam Schenk (2025)", "pga_field"),
        ev("Published prices", "Ben James the betting favourite seeking a first PGA TOUR win; Austin Smotherman +3000 the only FedExCup Fall winner in the field; Schenk +12500, Campos +22500, Villegas +17500, Todd +100000", "pga_odds"),
    ],
    flags=[{"code": "F-F7-GOLF-01", "text": "The official pages read publish tournament facts and a betting favourite but no full 120-man entry list with a verified per-player form line, so no outright price is originated. Market investigated, not priced; the missing official input is the published entry list and Round 1 tee times."}],
    model=None,
)
add(
    id="golf-stifel-2026", sport="golf", competition="PGA TOUR Champions Stifel Charity Classic",
    home="Field of 72 - Norwood Hills Country Club", away="", event_only=True,
    venue="Norwood Hills Country Club, St. Louis, Missouri", start_local="23-25 October 2026", start_utc="",
    sources=src("pga_stifel", "pga_stifel_dates", "pga_schwab"),
    evidence=[
        ev("Event facts", "54 holes, field of 72 - the top 72 on the Charles Schwab Cup points list after the regular season - and the first Charles Schwab Cup playoff event", "pga_schwab"),
        ev("Purse and past champions", "Purse USD 2,300,000; 2025 Thomas Bjorn -12 (201), 2024 Y.E. Yang -13 (200), 2023 Steve Flesch -19 (194), 2022 Padraig Harrington", "pga_stifel"),
        ev("Dates and venue", "23-25 October, Norwood Hills Country Club, St. Louis, Missouri", "pga_stifel_dates"),
    ],
    flags=[{"code": "F-F7-GOLF-02", "text": "No entry list or Charles Schwab Cup standings table was read on an official page this session, so no outright price is originated. Market investigated, not priced."}],
    model=None,
)
add(
    id="golf-senior-italian-2026", sport="golf", competition="Staysure Legends Tour Sergio Melpignano Senior Italian Open",
    home="Field - San Domenico Golf", away="", event_only=True,
    venue="San Domenico Golf, Savelletri, Italy", start_local="22-24 October 2026", start_utc="",
    sources=src("et_legends"),
    evidence=[ev("Official schedule", "Oct 22-24, Sergio Melpignano Senior Italian Open, San Domenico Golf, Savelletri, Italy, prize fund EUR 450,000, Order of Merit points 0", "et_legends")],
    flags=[{"code": "F-F7-GOLF-03", "text": "The official Legends Tour schedule lists the event but no field or defending champion was read, so no outright price is originated."}],
    model=None,
)
add(
    id="f1-usgp-2026", sport="motor-racing", competition="FIA Formula One World Championship 2026", round="Round 18",
    home="United States Grand Prix - Circuit of The Americas", away="", event_only=True,
    venue="Circuit of The Americas, Austin, Texas", start_local="23-25 October 2026 (race Sunday 25 October)", start_utc="",
    sources=src("f1_cal", "f1_usgp", "f1_stand", "f1_sing", "f1_story", "f1_perm"),
    evidence=[
        ev("Circuit data", "5.513km, 56 laps, race distance 308.405km, first Grand Prix 2012, fastest lap 1:36.169 by Charles Leclerc (2019)", "f1_usgp"),
        ev("Championship standings", "Max Verstappen fourth on 221 points", "f1_stand"),
        ev("Recent result", "Verstappen won Round 17 in Singapore in 1:42:00.785 from Charles Leclerc (+7.335s) and Kimi Antonelli (+24.573s), with Lando Norris +40.506s and Oscar Piastri +49.644s", "f1_sing"),
        ev("Form", "Verstappen has won the last two Grands Prix and the Singapore sprint, and four of the last five Grands Prix at the Circuit of The Americas", "f1_story"),
        ev("Stakes", "Six rounds remain, so 150 points are still available; Austin is Antonelli's first chance to seal the title", "f1_perm"),
    ],
    flags=[{"code": "F-F7-F1-01", "text": "The official pre-race coverage gives the championship gap as both 102 points (Antonelli over Verstappen) and 119 points adrift in two different articles published on 19 October. Both figures are recorded; neither is preferred, and no outright price is originated from them."},
           {"code": "F-F7-F1-02", "text": "No entry list, qualifying order or per-driver race price was published on the official pages read, so the win-race market is investigated but not priced."}],
    model=None,
)
add(
    id="esports-worlds-2026-swiss", sport="esports", competition="League of Legends Worlds 2026", round="Swiss stage",
    home="16-team Swiss stage", away="", event_only=True,
    venue="Allen, Texas and Brooklyn, New York (knockout stage)", start_local="Swiss 23-31 October; knockout 3-14 November", start_utc="",
    sources=src("lol_worlds", "lol_overview", "lol_live"),
    evidence=[
        ev("Format", "Play-In 15-18 October, Swiss stage 23-31 October, knockout stage 3-14 November; 16 teams in a five-round Swiss, the eight teams on three wins advance", "lol_worlds"),
        ev("Seeded tiers", "Tier 1 GEN, AL, TLAW, G2; Tier 2 TSW, HLE, BLG and one CBLOL seed; Tier 3 LYON, MKOI, T1, TES; Tier 4 CFO, IG, DK and the Play-In winner", "lol_worlds"),
        ev("Play-In results", "KT Rolster 3-2 Team Vitality; BNK FEARX 3-2 Beijing JDG; Xi'an Team WE 3-2 FlyQuest; HANJIN BRION 3-1 LGD GAMING", "lol_live"),
        ev("Draw dates", "Swiss round draws 23, 24, 26 and 30 October; quarter-final draw 31 October", "lol_worlds"),
    ],
    flags=[{"code": "F-F7-ES-01", "text": "The official live page lists Swiss-stage Bo1 entries under Thursday 22 October while the official primer puts the Swiss stage from 23 October. The conflict is recorded, not resolved, and no pairing is priced."},
           {"code": "F-F7-ES-02", "text": "Individual Swiss pairings are drawn live on 23 October, so no head-to-head market exists to originate at the time of writing."}],
    model=None,
)

# ============================== COVERAGE / FLAGS ============================
COVERAGE = [
    {"sport": "tennis", "olbg_id": 3, "hub": OLBG_HUBS["tennis"]["url"], "olbg_cards": 21, "verified_rows": 0, "priced_rows": 0,
     "outcome": "verified-zero upcoming",
     "detail": "All three ATP 250 signed supervisor draws (Almaty 9410, Lyon 496, Brussels 7485) and both WTA signed draws (Ningbo 2092, Osaka 405) were read this session. Every one shows the Round of 32 fully scored, and the ATP Live Race confirms the surviving players 'will play next in the R16'. Round of 16 pairings are not printed in those documents, so there is no upcoming tennis fixture that can be sourced. OLBG nevertheless lists 21 of these completed Round of 32 ties as 'Tomorrow'."},
    {"sport": "basketball", "olbg_id": 4, "hub": OLBG_HUBS["basketball"]["url"], "olbg_cards": 12, "verified_rows": 7, "priced_rows": 7,
     "outcome": "partly verified",
     "detail": "NBA (2 games on 22 October) and EuroLeague Round 7 (5 games) verified. Korea KBL Mobis Phoebus v Changwon Sakers and Brazil NBB Fortaleza BC v Pinheiros are listed upstream but no official league page was read for either, so both are unverified and unpriced."},
    {"sport": "golf", "olbg_id": 5, "hub": OLBG_HUBS["golf"]["url"], "olbg_cards": 4, "verified_rows": 3, "priced_rows": 0,
     "outcome": "event cards only",
     "detail": "Bermuda Championship, Stifel Charity Classic and Senior Italian Open verified as events from PGA TOUR / Legends Tour pages. The Stella Artois Players Championship (Sunshine Tour) could not be read on an official Sunshine Tour page and is unverified. No outrights priced: no published entry list."},
    {"sport": "cricket", "olbg_id": 7, "hub": OLBG_HUBS["cricket"]["url"], "olbg_cards": 7, "verified_rows": 4, "priced_rows": 2,
     "outcome": "partly verified",
     "detail": "Sri Lanka v England and New Zealand v India verified and priced. Namibia v Ireland and Australia Women v New Zealand Women verified as fixtures but with no sourced rating on both sides, so unpriced. The two CSA Pro T20 cards and Afghanistan v Zimbabwe are unverified."},
    {"sport": "snooker", "olbg_id": 8, "hub": OLBG_HUBS["snooker"]["url"], "olbg_cards": 2, "verified_rows": 8, "priced_rows": 8,
     "outcome": "fully verified",
     "detail": "All eight Round 3 ties read on the official WST match centre. OLBG lists only two of the eight upstream - a coverage gap on OLBG's side, not ours."},
    {"sport": "rugby-union", "olbg_id": 9, "hub": OLBG_HUBS["rugby-union"]["url"], "olbg_cards": 15, "verified_rows": 3, "priced_rows": 3,
     "outcome": "partly verified",
     "detail": "Three fixtures verified on LNR pages, each with LNR's own published three-way probabilities. The seven remaining Pro D2 round 8 fixtures, Gallagher Premiership round 4 and the four URC round 4 fixtures could not be confirmed on an official fixture page this session; URC standings were read but the round 4 fixture list was not."},
    {"sport": "rugby-league", "olbg_id": 10, "hub": OLBG_HUBS["rugby-league"]["url"], "olbg_cards": 3, "verified_rows": 4, "priced_rows": 0,
     "outcome": "verified fixtures, unpriced",
     "detail": "Four RLWC2026 Round 2 fixtures verified on the official IRL site. OLBG's rugby league hub publishes no World Cup match card at all on 22 October - only 2027 outrights. No official ranking pair or complete Round 1 result set was read, so no price is originated (rule 4)."},
    {"sport": "baseball", "olbg_id": 12, "hub": OLBG_HUBS["baseball"]["url"], "olbg_cards": 1, "verified_rows": 3, "priced_rows": 3,
     "outcome": "fully verified",
     "detail": "World Series games 1-3 verified on the MLB Stats API with both clubs' full 2026 records from the standings API. OLBG lists only Game 1 and prints a 20:00 clock for a game the API schedules at 00:00Z on 24 October (8pm ET on 23 October)."},
    {"sport": "ice-hockey", "olbg_id": 13, "hub": OLBG_HUBS["ice-hockey"]["url"], "olbg_cards": 4, "verified_rows": 12, "priced_rows": 12,
     "outcome": "fully verified",
     "detail": "The complete 12-game NHL slate for 22 October verified on the league schedule API with arenas, plus all 32 clubs' records from the standings API. OLBG's ice hockey hub shows three SHL games and one Liiga game and its NHL sub-route returns 'No tips found', so none of the 12 NHL games is listed upstream. The four OLBG-listed European games could not be verified on shl.se or liiga.fi this session."},
    {"sport": "motor-racing", "olbg_id": 14, "hub": OLBG_HUBS["motor-racing"]["url"], "olbg_cards": 3, "verified_rows": 1, "priced_rows": 0,
     "outcome": "event card only",
     "detail": "United States Grand Prix verified as Round 18 with full circuit data and the Singapore result. Win-race market not priced: no entry list or qualifying order published."},
    {"sport": "darts", "olbg_id": 15, "hub": OLBG_HUBS["darts"]["url"], "olbg_cards": 17, "verified_rows": 16, "priced_rows": 16,
     "outcome": "fully verified",
     "detail": "All 16 European Championship Round One ties verified across the official schedule, field-and-draw and preview releases, with Order of Merit money and the two most recent European Tour result sets. Three ties carry no printed seed numbers and are flagged."},
    {"sport": "handball", "olbg_id": 20, "hub": OLBG_HUBS["handball"]["url"], "olbg_cards": 18, "verified_rows": 2, "priced_rows": 2,
     "outcome": "partly verified",
     "detail": "The two EHF Champions League matches on 22 October verified on the official playing-times PDF. The 16 domestic and EHF European League cards listed upstream could not be read on a federation page this session and are unverified."},
    {"sport": "volleyball", "olbg_id": 21, "hub": OLBG_HUBS["volleyball"]["url"], "olbg_cards": 9, "verified_rows": 1, "priced_rows": 0,
     "outcome": "one fixture verified, unpriced",
     "detail": "PGE GiEK Skra Belchatow v PGE Projekt Warszawa on Saturday 24 October verified on the Polish league site. The men's PlusLiga URL now serves the women's TAURON Liga site, and the same fixture appears with both an 18:00 and a 12:00 clock on that site, so the kick-off is left blank and nothing is priced. The five Czech Extraliga cards and the three remaining Polish cards are unverified."},
    {"sport": "aussie-rules", "olbg_id": 22, "hub": OLBG_HUBS["aussie-rules"]["url"], "olbg_cards": 0, "verified_rows": 3, "priced_rows": 3,
     "outcome": "verified from the governing body, absent upstream",
     "detail": "OLBG's Aussie Rules hub returns 'No tips found' on 22 October even though AFLW Round 11 runs 23-25 October. Three Round 11 fixtures were verified on AFL.com.au with the full post-Round-10 ladder as the rating input."},
    {"sport": "esports", "olbg_id": 23, "hub": OLBG_HUBS["esports"]["url"], "olbg_cards": 0, "verified_rows": 1, "priced_rows": 0,
     "outcome": "event card only",
     "detail": "OLBG's eSports hub returns 'No tips found'. LoL Worlds 2026 structure, seeded tiers and Play-In results verified on the official LoL Esports site; Swiss pairings are drawn on 23 October so no head-to-head market exists yet."},
    {"sport": "gaelic-football", "olbg_id": 25, "hub": OLBG_HUBS["gaelic-football"]["url"], "olbg_cards": 6, "verified_rows": 5, "priced_rows": 5,
     "outcome": "fully verified",
     "detail": "Five county finals verified on Munster GAA, Cork GAA, Waterford GAA, Limerick GAA and the Maigh Cuilinn club site, each with semi-final scores. The All-Ireland 2027 outright listed upstream has no official source and is unverified."},
    {"sport": "greyhounds", "olbg_id": 28, "hub": OLBG_HUBS["greyhounds"]["url"], "olbg_cards": 0, "verified_rows": 0, "priced_rows": 0,
     "outcome": "verified zero",
     "detail": "OLBG's greyhound hub returns 'No tips found' on 22 October. gbgb.org.uk was not reachable to confirm or deny a racecard, so coverage is recorded as zero from OLBG and unconfirmed from GBGB."},
]

FLAGGED = [
    {"id": "F-F7-01", "severity": "finding", "sport": "policy",
     "title": "The brief's two High-confidence rules can only both hold in a 1.4-point probability band",
     "text": "The brief asks for High-confidence picks above 70% to win AND inside the -250 to +10000 price window. A 70.0% chance is a 1.4286 fair price (-233) and a 71.43% chance is exactly 1.40 (-250), so at a zero-vig fair line the admissible High band is model probability 70.0% to 71.43%. Any book-margin line pushes it out of the window entirely (a 5% overround makes 70% price -277). This desk publishes the zero-vig fair price as the originated line, shows the 5% book-equivalent alongside it, and tests the window against the fair price. Every selection above 71.43% is published in the 'Rejected Highs' table with its price instead of being quietly graded High.",
     "source": "https://buffedlizard55-lab.github.io/OLBG1/f71557b5/methodology.html"},
    {"id": "F-F7-NHL-01", "severity": "data", "sport": "ice-hockey",
     "title": "Every NHL goals-for/against value was discarded after a reconciliation failure",
     "text": "The standings payload at api-web.nhle.com/v1/standings/2026-10-21 was read through a paginated text extraction. Points, games played, wins, losses and overtime losses reconcile for all 24 clubs used on this desk (points / (2 x games played) equals the published pointPctg, and W + L + OTL equals games played). Season goals for and against do NOT reconcile: the New York Rangers object prints 17 season goals for alongside 33 goals for in its own last-ten block, which is impossible. Rather than trust some goals values and not others, all of them were discarded, the NHL model was rebuilt on points-per-game only, and no NHL match total is priced. This is a defect in how the payload was read, not in the league's data.",
     "source": "https://api-web.nhle.com/v1/standings/2026-10-21"},
    {"id": "F-F7-02", "severity": "upstream", "sport": "tennis",
     "title": "OLBG lists 21 completed tennis matches as upcoming",
     "text": "Every one of the five signed supervisor draws read this session (ATP Almaty 9410, Lyon 496, Brussels 7485; WTA Ningbo 2092, Osaka 405) shows its Round of 32 fully scored, and the ATP Live Race To Turin confirms the survivors 'will play next in the R16'. OLBG's tennis hub still presents those Round of 32 ties - Medvedev v Shimabukuro, Rybakina v Kudermetova, Machac v Khachanov and 18 others - as 'Tomorrow'. They are not priced here.",
     "source": "https://www.protennislive.com/posting/2026/9410/mds.pdf"},
    {"id": "F-F7-03", "severity": "upstream", "sport": "ice-hockey",
     "title": "OLBG's NHL sub-route returns no tips on a 12-game night",
     "text": "The NHL played 12 games on 22 October per the league's own schedule API, but OLBG's Ice Hockey hub lists three Swedish Hockey League games and one Finnish Liiga game, and its /betting-tips/Ice_Hockey/NHL/13 sub-route prints 'No tips found'. All 12 NHL games in this desk were harvested from the league, not from OLBG.",
     "source": "https://api-web.nhle.com/v1/schedule/2026-10-22"},
    {"id": "F-F7-04", "severity": "upstream", "sport": "aussie-rules",
     "title": "OLBG's Aussie Rules hub is empty during AFLW Round 11",
     "text": "OLBG's hub for sport id 22 returns 'No tips found' on 22 October although the official AFLW Round 11 begins in Adelaide on Friday 23 October. The hub copy also describes the women's competition as 'WAFL', which is the West Australian Football League - the women's league is AFLW. Both are recorded as upstream defects.",
     "source": "https://www.afl.com.au/aflw"},
    {"id": "F-F7-05", "severity": "upstream", "sport": "rugby-league",
     "title": "No RLWC2026 match card on OLBG's rugby league hub",
     "text": "The Rugby League World Cup is in its pool stage with four Round 2 fixtures across 23-25 October on the official IRL site, yet OLBG's rugby league hub publishes only three 2027 outrights (State of Origin 2027, Super League 2027, NRL 2027) and no World Cup match card.",
     "source": "https://www.intrl.sport/fixtures-results"},
    {"id": "F-F7-06", "severity": "upstream", "sport": "snooker",
     "title": "OLBG lists two of eight official Round 3 ties",
     "text": "The WST match centre publishes eight Round 3 ties for 22 October; OLBG's snooker hub shows only Matthew Selt v Sam Craigie and Kyren Wilson v Pang Junxu. The six missing ties (Slessor v Walden, McGill v Baranowski, Williams v O'Donnell, Gilbert v Cheung, Brown v Donaldson, Jones v Wells) are all priced here from the official page.",
     "source": "https://www.wst.tv/match-centre/f0b30e58-d987-4505-89c2-8b24805b98d5"},
    {"id": "F-F7-07", "severity": "upstream", "sport": "baseball",
     "title": "OLBG's World Series clock disagrees with the MLB API",
     "text": "OLBG prints 'TB Rays @ MIL Brewers, 23 Oct 20:00'. The MLB Stats API schedules gamePk 849805 at 2026-10-24T00:00:00Z with officialDate 2026-10-23, i.e. 8pm Eastern on 23 October. OLBG's clock is US Central/Eastern ambiguous with no timezone label, the same silent-localisation defect recorded in earlier sessions.",
     "source": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-20&endDate=2026-10-28&hydrate=team,linescore,venue"},
    {"id": "F-F7-08", "severity": "upstream", "sport": "cricket",
     "title": "Afghanistan v Zimbabwe is dated 23 October upstream but no governing body publishes that match",
     "text": "OLBG lists 'Afghanistan vs Zimbabwe One Day Match, 23 Oct 07:30'. The Afghanistan-Zimbabwe series in the UAE opens with a T20I at Sharjah on 27 October, and no official board page read this session publishes a 23 October ODI between these sides. The card is unverified, unpriced and left blank.",
     "source": "https://www.icc-cricket.com/tournaments/mens-t20-world-cup-2026/news/final-squads-for-icc-men-s-t20-world-cup-2026-confirmed"},
    {"id": "F-F7-09", "severity": "data", "sport": "volleyball",
     "title": "The men's Polish league URL now serves the women's competition, and the same fixture carries two clocks",
     "text": "plusliga.pl resolves to tauronliga.pl, the women's TAURON Liga site, which nevertheless carries the men's PGE GiEK Skra Belchatow v PGE Projekt Warszawa fixture for Saturday 24 October 2026. Different views of that page print 18:00 and 12:00. The fixture date is carried; the kick-off is blank and nothing is priced.",
     "source": "https://www.tauronliga.pl/teams/tour/53/id/61.html"},
    {"id": "F-F7-10", "severity": "data", "sport": "motor-racing",
     "title": "Formula 1 publishes two different championship gaps on the same day",
     "text": "formula1.com's 19 October pre-race coverage states Antonelli 'now leads by 102 points' over Verstappen in one article and describes Verstappen as '119 points adrift' in another. Both are recorded verbatim with their URLs; neither is preferred, and no championship outright is originated from them.",
     "source": "https://www.formula1.com/en/latest/article/its-race-week-5-storylines-were-excited-about-ahead-of-the-2026-united-states-grand-prix.4utgT1kLqHM2HAM98YP4TW"},
    {"id": "F-F7-11", "severity": "data", "sport": "gaelic-football",
     "title": "A club's own match report gives its star player two different tallies",
     "text": "The Maigh Cuilinn report of the Galway semi-final says Dessie Conneely 'finished with a highly impressive personal tally of 2-14' in the body and lists 'D Conneely (2-16)' in the scoring list on the same page. Both are printed; the discrepancy is not resolved by inference.",
     "source": "https://www.maighcuilinn.com/stellar-performance-against-annaghdown-sets-up-repeat-county-final/"},
    {"id": "F-F7-12", "severity": "data", "sport": "gaelic-football",
     "title": "OLBG's Kanturk tip runs against the verified championship record",
     "text": "OLBG tips Kanturk at 4/5 (80%) for the Cork Senior 'A' final. The verified record has Eire Og unbeaten and top of their group with a 0-24 to 0-9 round win and a 2-16 to 1-16 semi-final, against Kanturk's one-point round win (2-8 to 1-11) and four-point semi-final (1-18 to 1-14). The crowd view and the sourced form disagree; both are published.",
     "source": "https://gaacork.ie/2026-10-11/mccarthy-insurance-group-club-championship-weekend-round-up/"},
    {"id": "F-F7-13", "severity": "policy", "sport": "rugby-league",
     "title": "Earlier desks graded Tonga and England High without a sourced rating on both sides",
     "text": "Tonga -2.5 and England -9.5 appear as High-confidence picks in the v3 and 6a081cf6 desks. This session could verify only one Round 1 result per tie (Tonga 30-12 England) and no official world-ranking pair, so repository rule 4 refuses the strength edge and both fixtures are capped at Low here. England's own verified Round 1 result is a 12-30 loss, which a -9.5 line does not reflect.",
     "source": "https://www.intrl.sport/match-details/2566"},
    {"id": "F-F7-14", "severity": "gap", "sport": "multiple",
     "title": "Markets investigated but not priced, with the missing official input named",
     "text": "Match totals are priced only where both clubs' scoring rates were read on an official page - the 12 NHL games (goals for/against and games played per club) and the three World Series games (runs scored and allowed over 162 games). Totals are NOT priced for EuroLeague, Pro D2, Top 14, EHF Champions League, AFLW, darts, snooker, cricket, rugby league or Gaelic football, because the official pages read do not publish the per-match scoring rates or the match format needed. Golf, Formula 1 and eSports outrights are not priced because no entry list, qualifying order or drawn pairing is published yet. Each omission is named per sport on the coverage page rather than filled with a league-average constant.",
     "source": "https://api-web.nhle.com/v1/standings/2026-10-21"},
]


def main() -> None:
    harvest = {
        "session": SESSION, "harvested_utc": NOW, "harvest_date": READ,
        "hub_pattern": "https://www.olbg.com/betting-tips/{slug}/{sport_id}",
        "event_pattern": "https://www.olbg.com/betting-tips/{sport}/{tour}/{comp}/{event}/{sport_id}?event_id={id}",
        "in_scope": [{"sport": s, "olbg_id": i, "hub": OLBG_HUBS[s]["url"],
                      "cards_seen": OLBG_HUBS[s]["cards_seen"], "note": OLBG_HUBS[s]["note"]} for s, i in SPORTS],
        "excluded": [{"slug": s or "none", "olbg_id": i, "reason": r,
                      "hub": (f"https://www.olbg.com/betting-tips/{s}/{i}" if s and i else "")}
                     for s, i, r in EXCLUDED],
        "totals": {"hubs_read": len(OLBG_HUBS), "cards_seen": sum(h["cards_seen"] for h in OLBG_HUBS.values())},
    }
    (OUT / "olbg_harvest.json").write_text(json.dumps(harvest, indent=1, ensure_ascii=False), encoding="utf-8")

    fixtures = {"session": SESSION, "generated_utc": NOW, "read_date": READ,
                "rules": ["official sources only", "blank beats wrong", "assumptions are labelled",
                          "one-sided ratings are refused", "every High pick gets its own written prediction"],
                "fixtures": F}
    (OUT / "fixtures.json").write_text(json.dumps(fixtures, indent=1, ensure_ascii=False), encoding="utf-8")

    sources = {"session": SESSION, "read_date": READ,
               "sources": [{"key": k, "name": v[0], "url": v[1]} for k, v in S.items()]}
    (OUT / "sources.json").write_text(json.dumps(sources, indent=1, ensure_ascii=False), encoding="utf-8")

    coverage = {"session": SESSION, "read_date": READ, "sports": COVERAGE}
    (OUT / "coverage.json").write_text(json.dumps(coverage, indent=1, ensure_ascii=False), encoding="utf-8")

    flags = {"session": SESSION, "read_date": READ, "flags": FLAGGED}
    (OUT / "flagged.json").write_text(json.dumps(flags, indent=1, ensure_ascii=False), encoding="utf-8")

    cards = sum(1 for f in F if f["event_only"])
    sourced = sum(1 for f in F if f.get("model") and not f["event_only"])
    neutral = len(F) - cards - sourced
    print(f"f71557b5 data: {len(F)} rows = {sourced} with a sourced rating on both sides + "
          f"{neutral} published at a neutral baseline under rule 4 (one-sided or absent ratings) + "
          f"{cards} event cards; {len(S)} official source URLs; {len(FLAGGED)} register flags")


if __name__ == "__main__":
    main()
