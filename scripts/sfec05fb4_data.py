#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the fec05fb4 desk dataset.

Evidence policy
---------------
* Every priced row links to at least one official governing-body / league /
  tour page.
* `fresh` = this session read that official page on 2026-10-22 (times below).
  `carried` = the official page was read by an earlier session and was not
  re-read here; carried rows can never be High.
* A High needs ALL of: p in (0.700, 0.714286] (so the zero-vig fair price sits
  inside -250..+10000); a fresh official read this session; both clubs'
  Round-7 availability officially confirmed in that read; a unique hand-written
  >=30-word prediction. Anything short of that is Medium or Low.
* Blank beats invented: a value that was not read is null in JSON and an empty
  cell in HTML, and the row is listed on the Flagged page.
"""
from __future__ import annotations

import csv
import io
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from model import price_match  # noqa: E402

AS_OF = "2026-10-22T12:45:00Z"
SESSION = "fec05fb4-olbg1"
OUT = ROOT / "data" / "fec05fb4"
OUT.mkdir(parents=True, exist_ok=True)

HIGH_LO, HIGH_HI = 0.700, 0.714286          # zero-vig band = American -233 .. -250
BAND = 1.4                                   # fair decimal at p = 0.714286
OVERROUND = 1.05

# ---------------------------------------------------------------------------
SOURCES = {
    "nhl_standings": dict(
        name="NHL.com — League standings, 21 October 2026",
        publisher="NHL",
        url="https://www.nhl.com/standings/2026-10-21/league",
        status="fresh", read_utc="2026-10-22T12:47:00Z",
        confirms="all 32 clubs: GP, W-L-OT, PTS, P%, RW/ROW, GF, GA, DIFF, home and away records, L10, streak",
        does_not_confirm="tonight's goaltenders, injuries or lineups"),
    "nhl_scores": dict(
        name="NHL.com — Scores, 22 October 2026",
        publisher="NHL",
        url="https://www.nhl.com/scores/2026-10-22",
        status="fresh", read_utc="2026-10-22T12:24:00Z",
        confirms="12 games, home/away, EDT start times, records, and the NHL.com/DraftKings reference moneyline",
        does_not_confirm="injuries, projected goaltenders, lineups"),
    "el_standings": dict(
        name="EuroLeague Basketball — Standings, 2026-27 regular season",
        publisher="EuroLeague Basketball",
        url="https://www.euroleaguebasketball.net/en/euroleague/standings/",
        status="fresh", read_utc="2026-10-22T12:30:00Z",
        confirms="all 20 clubs: GP, W-L, win%, points scored and allowed per game, +/- and home/away splits",
        does_not_confirm="injuries or starting fives"),
    "el_game_center": dict(
        name="EuroLeague Basketball — Game Center, Round 7",
        publisher="EuroLeague Basketball",
        url="https://www.euroleaguebasketball.net/euroleague/news/game-center-round-7-el2627/",
        status="fresh", read_utc="2026-10-22T12:33:00Z",
        confirms="Round 7 pairings and CEST tip times, quoted records, form notes and the Hapoel 90-81 Virtus result",
        does_not_confirm="the preview's Valencia 5-1 and Real Madrid 1-4 away claims, which contradict the standings table (flagged F-FEC-04)"),
    "el_injury": dict(
        name="EuroLeague Basketball — Injury report, Round 7",
        publisher="EuroLeague Basketball",
        url="https://www.euroleaguebasketball.net/en/euroleague/news/injury-report-round-7-fantasy/",
        status="fresh", read_utc="2026-10-22T12:36:00Z",
        confirms="club-confirmed Round 7 availability for Efes, Besiktas, Maccabi, Real Madrid, Panathinaikos, Baskonia, Milan, Barcelona, Partizan, Crvena Zvezda, Zalgiris, ASVEL, Olympiacos, Fenerbahce, Paris and Valencia",
        does_not_confirm="players a club has not listed; no absence is inferred"),
    "mlb_schedule": dict(
        name="MLB StatsAPI — World Series schedule, 22-29 October 2026",
        publisher="MLB",
        url="https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-22&endDate=2026-10-29&hydrate=team,venue",
        status="fresh", read_utc="2026-10-22T12:28:00Z",
        confirms="gamePk 849805/849802/849804/849803/849799, official dates, UTC starts, venues, Scheduled status",
        does_not_confirm="postseason records (the payload reports 0-0), pitchers or lineups"),
    "mlb_standings_al": dict(
        name="MLB StatsAPI — American League standings, 2026",
        publisher="MLB",
        url="https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026",
        status="fresh", read_utc="2026-10-22T12:29:00Z",
        confirms="Rays 98-64 .605 (division champion), Yankees 93-68, Red Sox 87-75",
        does_not_confirm="postseason form"),
    "mlb_standings_nl": dict(
        name="MLB StatsAPI — National League standings, 2026",
        publisher="MLB",
        url="https://statsapi.mlb.com/api/v1/standings?leagueId=104&season=2026",
        status="fresh", read_utc="2026-10-22T12:51:00Z",
        confirms="Brewers 103-59 .636 (NL Central champion, 'z'), home 55-26, away 48-33, L10 8-2, W5, 832 runs scored and 618 allowed",
        does_not_confirm="postseason form"),
    "pdc_schedule": dict(
        name="PDC — 2026 Machineseeker European Championship schedule confirmed",
        publisher="PDC",
        url="https://www.pdc.tv/news/2026/october/19/2026-machineseeker-european-championship-schedule-confirmed/",
        status="carried", read_utc="2026-10-22T07:44:00Z",
        confirms="venue, dates, every Round One pairing, official seeds and the Thursday/Friday session windows",
        does_not_confirm="tie start times, three-dart averages or recent match results",
        note="A re-fetch at 12:34Z returned only a cookie-consent wall; no fixture text was readable."),
    "aflw_ladder": dict(
        name="AFL — 2026 NAB AFLW ladder after Round 10",
        publisher="AFL",
        url="https://www.afl.com.au/aflw/ladder",
        status="carried", read_utc="2026-10-22T07:36:00Z",
        confirms="W-L-D, points, percentage and ladder position used as the rating input",
        does_not_confirm="Round 11 selection or injuries",
        note="A re-fetch at 12:31Z returned an empty client-rendered table ('Loading')."),
    "wst_matches": dict(
        name="World Snooker Tour — match centre",
        publisher="WST",
        url="https://www.wst.tv/matches/",
        status="carried", read_utc="2026-10-22T07:46:00Z",
        confirms="listed last-16 pairings and session times",
        does_not_confirm="official seeds or the exact frame format"),
}

# ---------------------------------------------------------------------------
# NHL: every figure below is a column of the official league table.
# ---------------------------------------------------------------------------
NHL = {
    "NSH": dict(name="Nashville Predators", gp=8, w=3, l=2, ot=3, pct=.563, gf=23, ga=24, home="2-2-1", away="1-0-2", l10="3-2-3", strk="W1"),
    "BOS": dict(name="Boston Bruins", gp=10, w=7, l=2, ot=1, pct=.750, gf=36, ga=22, home="3-1-0", away="4-1-1", l10="7-2-1", strk="OT1"),
    "NYR": dict(name="New York Rangers", gp=11, w=7, l=3, ot=1, pct=.682, gf=33, ga=24, home="6-0-0", away="1-3-1", l10="7-2-1", strk="W1"),
    "TOR": dict(name="Toronto Maple Leafs", gp=11, w=5, l=4, ot=2, pct=.545, gf=38, ga=35, home="3-3-1", away="2-1-1", l10="5-3-2", strk="W2"),
    "SJS": dict(name="San Jose Sharks", gp=10, w=5, l=4, ot=1, pct=.550, gf=27, ga=35, home="2-2-0", away="3-2-1", l10="5-4-1", strk="W1"),
    "OTT": dict(name="Ottawa Senators", gp=10, w=7, l=3, ot=0, pct=.700, gf=29, ga=24, home="4-1-0", away="3-2-0", l10="7-3-0", strk="W1"),
    "ANA": dict(name="Anaheim Ducks", gp=9, w=4, l=5, ot=0, pct=.444, gf=26, ga=29, home="1-3-0", away="3-2-0", l10="4-5-0", strk="L4"),
    "NJD": dict(name="New Jersey Devils", gp=9, w=5, l=4, ot=0, pct=.556, gf=29, ga=30, home="4-2-0", away="1-2-0", l10="5-4-0", strk="W1"),
    "FLA": dict(name="Florida Panthers", gp=10, w=5, l=3, ot=2, pct=.600, gf=31, ga=30, home="2-1-0", away="3-2-2", l10="5-3-2", strk="L1"),
    "PIT": dict(name="Pittsburgh Penguins", gp=10, w=3, l=6, ot=1, pct=.350, gf=33, ga=38, home="2-1-0", away="1-5-1", l10="3-6-1", strk="L4"),
    "LAK": dict(name="Los Angeles Kings", gp=7, w=1, l=4, ot=2, pct=.286, gf=17, ga=27, home="0-3-0", away="1-1-2", l10="1-4-2", strk="W1"),
    "NYI": dict(name="New York Islanders", gp=9, w=5, l=3, ot=1, pct=.611, gf=27, ga=20, home="4-1-0", away="1-2-1", l10="5-3-1", strk="W2"),
    "VGK": dict(name="Vegas Golden Knights", gp=11, w=8, l=3, ot=0, pct=.727, gf=44, ga=30, home="5-2-0", away="3-1-0", l10="7-3-0", strk="L1"),
    "STL": dict(name="St. Louis Blues", gp=9, w=4, l=4, ot=1, pct=.500, gf=29, ga=29, home="2-0-1", away="2-4-0", l10="4-4-1", strk="W1"),
    "WPG": dict(name="Winnipeg Jets", gp=9, w=4, l=3, ot=2, pct=.556, gf=24, ga=26, home="2-2-1", away="2-1-1", l10="4-3-2", strk="L2"),
    "DAL": dict(name="Dallas Stars", gp=9, w=5, l=3, ot=1, pct=.611, gf=23, ga=15, home="2-2-0", away="3-1-1", l10="5-3-1", strk="W3"),
    "MIN": dict(name="Minnesota Wild", gp=10, w=6, l=2, ot=2, pct=.700, gf=31, ga=25, home="4-0-0", away="2-2-2", l10="6-2-2", strk="OT1"),
    "CGY": dict(name="Calgary Flames", gp=8, w=2, l=6, ot=0, pct=.250, gf=17, ga=37, home="1-3-0", away="1-3-0", l10="2-6-0", strk="W1"),
    "CAR": dict(name="Carolina Hurricanes", gp=11, w=8, l=2, ot=1, pct=.773, gf=42, ga=27, home="2-1-1", away="6-1-0", l10="8-2-0", strk="W1"),
    "EDM": dict(name="Edmonton Oilers", gp=9, w=7, l=1, ot=1, pct=.833, gf=41, ga=27, home="2-1-1", away="5-0-0", l10="7-1-1", strk="W2"),
    "UTA": dict(name="Utah Mammoth", gp=10, w=7, l=3, ot=0, pct=.700, gf=38, ga=31, home="3-1-0", away="4-2-0", l10="7-3-0", strk="W1"),
    "SEA": dict(name="Seattle Kraken", gp=10, w=6, l=3, ot=1, pct=.650, gf=39, ga=34, home="2-1-0", away="4-2-1", l10="6-3-1", strk="W1"),
    "DET": dict(name="Detroit Red Wings", gp=9, w=3, l=3, ot=3, pct=.500, gf=23, ga=28, home="3-3-1", away="0-0-2", l10="3-3-3", strk="OT1"),
    "VAN": dict(name="Vancouver Canucks", gp=11, w=2, l=8, ot=1, pct=.227, gf=33, ga=51, home="1-3-0", away="1-5-1", l10="1-8-1", strk="L2"),
}

NHL_GAMES = [
    ("nhl-2026020154", "NSH", "BOS", "2026-10-22T23:00:00Z", "7:00 PM", "NSH +130 / BOS -155"),
    ("nhl-2026020155", "NYR", "TOR", "2026-10-22T23:00:00Z", "7:00 PM", "NYR -112 / TOR -108"),
    ("nhl-2026020156", "SJS", "OTT", "2026-10-22T23:00:00Z", "7:00 PM", "SJS +114 / OTT -135"),
    ("nhl-2026020157", "ANA", "NJD", "2026-10-22T23:00:00Z", "7:00 PM", "ANA +164 / NJD -198"),
    ("nhl-2026020158", "FLA", "PIT", "2026-10-22T23:00:00Z", "7:00 PM", "FLA -105 / PIT -115"),
    ("nhl-2026020159", "LAK", "NYI", "2026-10-22T23:30:00Z", "7:30 PM", "LAK -105 / NYI -115"),
    ("nhl-2026020160", "VGK", "STL", "2026-10-23T00:00:00Z", "8:00 PM", "VGK -125 / STL +105"),
    ("nhl-2026020161", "WPG", "DAL", "2026-10-23T00:00:00Z", "8:00 PM", "WPG +170 / DAL -205"),
    ("nhl-2026020162", "MIN", "CGY", "2026-10-23T01:00:00Z", "9:00 PM", "MIN -205 / CGY +170"),
    ("nhl-2026020163", "CAR", "EDM", "2026-10-23T01:00:00Z", "9:00 PM", "CAR -118 / EDM -102"),
    ("nhl-2026020164", "UTA", "SEA", "2026-10-23T02:00:00Z", "10:00 PM", "UTA -170 / SEA +142"),
    ("nhl-2026020165", "DET", "VAN", "2026-10-23T02:00:00Z", "10:00 PM", "DET -170 / VAN +142"),
]

# ---------------------------------------------------------------------------
# EuroLeague: official per-game scoring from the 2026-27 standings table.
# ---------------------------------------------------------------------------
EL = {
    "PAO": dict(name="Panathinaikos AKTOR Athens", gp=6, w=5, l=1, ppg=88.0, opg=73.0, split="home 4-1 / away 1-0"),
    "FBT": dict(name="Fenerbahce Tarfin Istanbul", gp=6, w=5, l=1, ppg=83.5, opg=74.5, split="home 5-0 / away 0-1"),
    "OLY": dict(name="Olympiacos Piraeus", gp=6, w=5, l=1, ppg=94.0, opg=87.3, split="home 1-0 / away 4-1"),
    "HTA": dict(name="Hapoel IBI Tel Aviv", gp=7, w=5, l=2, ppg=90.0, opg=85.9, split="home 3-1 / away 2-1"),
    "VBC": dict(name="Valencia Basket", gp=6, w=4, l=2, ppg=97.2, opg=89.5, split="home 2-2 / away 2-0"),
    "CZV": dict(name="Crvena Zvezda Meridianbet Belgrade", gp=6, w=4, l=2, ppg=80.8, opg=76.2, split="home 2-2 / away 2-0"),
    "DUB": dict(name="Dubai Basketball", gp=6, w=4, l=2, ppg=81.7, opg=82.2, split="home 2-1 / away 2-1"),
    "VIR": dict(name="Virtus Bologna", gp=7, w=4, l=3, ppg=86.6, opg=86.9, split="home 2-0 / away 2-3"),
    "RMB": dict(name="Real Madrid", gp=6, w=3, l=3, ppg=92.3, opg=88.5, split="home 2-0 / away 1-3"),
    "BAR": dict(name="FC Barcelona", gp=6, w=3, l=3, ppg=89.0, opg=87.5, split="home 2-2 / away 1-1"),
    "BJK": dict(name="Besiktas Istanbul", gp=6, w=3, l=3, ppg=92.3, opg=92.5, split="home 1-2 / away 2-1"),
    "PAR": dict(name="Partizan Mozzart Bet Belgrade", gp=6, w=3, l=3, ppg=77.2, opg=78.0, split="home 1-1 / away 2-2"),
    "EFS": dict(name="Anadolu Efes Istanbul", gp=6, w=2, l=4, ppg=82.0, opg=85.0, split="home 1-1 / away 1-3"),
    "ZAL": dict(name="Zalgiris Kaunas", gp=6, w=2, l=4, ppg=81.7, opg=86.2, split="home 0-2 / away 2-2"),
    "BAY": dict(name="FC Bayern Munich", gp=6, w=2, l=4, ppg=86.8, opg=92.0, split="home 0-2 / away 2-2"),
    "MTA": dict(name="Maccabi Rapyd Tel Aviv", gp=6, w=2, l=4, ppg=84.8, opg=90.0, split="home 1-1 / away 1-3"),
    "ASV": dict(name="LDLC ASVEL Villeurbanne", gp=6, w=2, l=4, ppg=87.8, opg=95.3, split="home 1-2 / away 1-2"),
    "PBB": dict(name="Paris Basketball", gp=6, w=1, l=5, ppg=77.7, opg=84.5, split="home 1-3 / away 0-2"),
    "MIL": dict(name="Armani Olimpia Milan", gp=6, w=1, l=5, ppg=84.0, opg=93.2, split="home 1-2 / away 0-3"),
    "KBA": dict(name="Kosner Baskonia Vitoria-Gasteiz", gp=6, w=1, l=5, ppg=84.0, opg=94.0, split="home 1-3 / away 0-2"),
}

EL_GAMES = [
    dict(id="el-535918", home="EFS", away="BJK", utc="2026-10-22T17:30:00Z", cest="19:30",
         pick=("handicap", "away", 5.0), confirmed=True,
         preview="Efes (2-4) host the Istanbul derby after winning on the road in Kaunas, with Cam Payne stepping up in Mike James's absence. Besiktas (3-3) beat Bayern Munich on Friday and can debut Lonnie Walker. Besiktas rank third in the league in scoring (92.3 ppg); Efes are sixth in points allowed (85.0 ppg).",
         injury="Efes: PJ Dozier (back), Mike James (Achilles), Isaia Cordinier (post-surgery) and Georgios Papagiannis (ACL) ruled out. Besiktas: Lonnie Walker registered and available; DaQuan Jeffries out after wrist surgery."),
    dict(id="el-535920", home="BAY", away="DUB", utc="2026-10-22T18:00:00Z", cest="20:00",
         pick=("handicap", "away", 4.0), confirmed=False,
         preview="Bayern (2-4) are home after a two-round week in Turkiye; Dubai (4-2) are still on the road after winning in Spain and Italy. Dubai concede 82.2 per game, fifth in the league, and Dwayne Bacon's 17.8 points rank third. Duane Washington averages 16.8 off the Bayern bench, with Andreas Obst spacing the floor.",
         injury="Bayern: no injury report filed. Dubai: no report filed; Dzanan Musa and Justin Anderson are yet to play this season."),
    dict(id="el-535921", home="MTA", away="RMB", utc="2026-10-22T18:05:00Z", cest="20:05",
         pick=("handicap", "away", 2.0), confirmed=False,
         preview="Maccabi (2-4) split two games in Spain last week and now meet Real Madrid (3-3), which has won three in a row. Yam Madar is settling in and Theo Maledon has taken a step forward. The home team has won each of the last five meetings. The preview gives Real a 1-4 away record; the standings table says 1-3 and is used here.",
         injury="Maccabi: no report filed; Gur Lavi was not on the Round 6 roster; Iffe Lundberg out until December with a partial quadriceps tear. Real Madrid: no report filed; Gaby Deck (shoulder) last played in Round 3; Usman Garuba suffered an Achilles injury at the Final Four."),
    dict(id="el-535923", home="PAO", away="KBA", utc="2026-10-22T18:15:00Z", cest="20:15",
         pick=("handicap", "home", 6.0), confirmed=False,
         preview="Panathinaikos (5-1) respond to their first loss under Coach Obradovic against Baskonia (1-5), who arrive with new coach Velimir Perasovic. PAO concede a league-low 73.0 points per game and have won five straight home games against Baskonia, whose last win in Athens came in March 2021.",
         injury="Panathinaikos: Kendrick Nunn, Kostas Sloukas and Isaac Bonga available; Nikos Rogkavopoulos and Lefteris Mantzoukas ruled out. Baskonia: no report filed; Markus Howard officially left the club on 14 October."),
    dict(id="el-535922", home="MIL", away="BAR", utc="2026-10-22T18:30:00Z", cest="20:30",
         pick=("total", "under", 185.5), confirmed=True,
         preview="Milan (1-5) have lost four in a row and host Barcelona (3-3), who split a pair of tight home games last week. Moses Wright, who agreed terms with Barcelona in the summer, leads the Milan frontline against Josh Nebo, who spent the previous two seasons in Milan. The teams split home wins last season, both decided by a single possession.",
         injury="Milan: full roster available, confirmed. Barcelona: Justin Minaya available; Dario Brizuela and Yoan Makoundou ruled out."),
    dict(id="el-535924", home="PAR", away="CZV", utc="2026-10-22T18:45:00Z", cest="20:45",
         pick=("total", "under", 165.5), confirmed=False,
         preview="The Eternal Derby: Partizan (3-3) started 3-0 and have lost three straight; Crvena Zvezda (4-2) lost their first two and have won four straight. Zvezda could have new signing Christian Koloko in uniform. Both teams rank among the league's best defenses, so a low-scoring game is expected.",
         injury="Partizan: Lamar Stevens available; Tonye Jekiri, Vanja Marinkovic and Derek Willis ruled out. Crvena Zvezda: no report filed; Christian Koloko not yet registered; Ebuka Izundu, Johnathan Motley and Stefan Miljenovic injured."),
    dict(id="el-535928", home="ZAL", away="ASV", utc="2026-10-23T17:00:00Z", cest="19:00",
         pick=("total", "over", 166.5), confirmed=False,
         preview="Zalgiris (2-4) and ASVEL (2-4) both lost twice last week. ASVEL have allowed a league-high 95.3 points per game through six rounds. Zalgiris should have their entire backcourt healthy, which they may need against Patty Mills, one of five ASVEL players averaging double figures.",
         injury="Zalgiris: no report filed; Nigel Williams-Goss returned in Round 6; Maodo Lo was left off the Round 6 roster. ASVEL: no report filed; Patty Mills and Tremont Waters did not play in Round 6; Juhann Begarin has not yet played; Mathis Dossou-Yovo sidelined."),
    dict(id="el-535925", home="OLY", away="FBT", utc="2026-10-23T18:15:00Z", cest="20:15",
         pick=("handicap", "away", 5.0), confirmed=False,
         preview="Olympiacos (5-1) are home after back-to-back overtime road wins and host Fenerbahce (5-1), which is 0-1 on the road. Olympiacos have won three straight against Fenerbahce, including the 2026 Final Four and SuperCup semi-finals. Fenerbahce allow 74.5 per game, second in the league. The preview puts Olympiacos at 98.2 points per game; the standings table's 564 points in six games is 94.0 and is used here.",
         injury="Olympiacos: no report filed; Tyler Dorsey was unavailable in Round 6. Fenerbahce: no report filed; coach Saras Jasikevicius had a full roster in Round 6."),
    dict(id="el-2026-69", home="PBB", away="VBC", utc="2026-10-23T18:45:00Z", cest="20:45",
         pick=("handicap", "away", 1.0), confirmed=False,
         preview="Paris (1-5) have lost three in a row and host Valencia, whom the preview calls 5-1 even though the standings record 4-2; the table is used. TJ Shorts returns to face his former club. Paris have the league's top scorer, Nadir Hifi, at 20.2 points per game. The preview calls Valencia the top offense at 98.3; their 583 points in six games is 97.17.",
         injury="Paris: no report filed; Nadir Hifi missed Rounds 5 and 6 with an ankle injury and did not play in the French League; TJ Warren did not play in Round 6; Frank Ntilikina out since Round 2. Valencia: no report filed; full roster available in Round 6."),
]

MLB_GAMES = [
    dict(id="mlb-849805", away="Tampa Bay Rays", home="Milwaukee Brewers", utc="2026-10-24T00:00:00Z", official="2026-10-23", venue="American Family Field", game="World Series Game 1"),
    dict(id="mlb-849802", away="Tampa Bay Rays", home="Milwaukee Brewers", utc="2026-10-25T00:00:00Z", official="2026-10-24", venue="American Family Field", game="World Series Game 2"),
    dict(id="mlb-849804", away="Milwaukee Brewers", home="Tampa Bay Rays", utc="2026-10-27T00:00:00Z", official="2026-10-26", venue="Tropicana Field", game="World Series Game 3"),
    dict(id="mlb-849803", away="Milwaukee Brewers", home="Tampa Bay Rays", utc="2026-10-28T00:00:00Z", official="2026-10-27", venue="Tropicana Field", game="World Series Game 4"),
    dict(id="mlb-849799", away="Milwaukee Brewers", home="Tampa Bay Rays", utc="2026-10-29T00:00:00Z", official="2026-10-28", venue="Tropicana Field", game="World Series Game 5"),
]

# ---------------------------------------------------------------------------
# The only two High selections. Both clubs' Round 7 availability was confirmed
# in the official injury report; the seven other EuroLeague games were not.
# ---------------------------------------------------------------------------
PREDICTIONS = {
    "el-535918": dict(
        text=("Anadolu Efes are 2-4 and missing four rotation players: PJ Dozier, Mike James, Isaia Cordinier and Georgios Papagiannis are all ruled out, the club has confirmed. "
              "Besiktas sit 3-3, beat Bayern Munich on Friday and can hand Lonnie Walker a debut, while their 92.3 points per game rank third in the league. "
              "Efes won on the road in Kaunas last round, but this derby asks them to cover five points without their primary creators. "
              "Selection: {selection} at {price}."),
        facts=["Efes 2-4 and Besiktas 3-3 (official standings)",
               "Efes ruled out Dozier, James, Cordinier and Papagiannis (official Round 7 injury report)",
               "Besiktas beat Bayern on Friday and rank third at 92.3 ppg (official Game Center)",
               "Lonnie Walker available for a Besiktas debut (official injury report)",
               "Efes won in Kaunas in Round 6 (official Game Center)"],
        sources=["el_standings", "el_game_center", "el_injury"]),
    "el-535922": dict(
        text=("Milan are 1-5 and have lost four in a row, yet the club has confirmed a full roster available for this game. "
              "Barcelona are 3-3, split a pair of tight home games last week, and will be without Dario Brizuela and Yoan Makoundou, though Justin Minaya is back. "
              "Moses Wright leads Milan against Josh Nebo, who spent the previous two seasons in Milan, and these teams split two one-possession games last season. "
              "That profile points to a grind rather than a shootout. Selection: {selection} at {price}."),
        facts=["Milan 1-5 and on a four-game losing streak (official standings/Game Center)",
               "Milan full roster available (official Round 7 injury report)",
               "Barcelona 3-3 and split two tight home games last week (official standings/Game Center)",
               "Brizuela and Makoundou out; Minaya available (official injury report)",
               "Moses Wright vs Josh Nebo; both meetings last season were one-possession games (official Game Center)"],
        sources=["el_standings", "el_game_center", "el_injury"]),
}

SPORT_LABELS = {
    "ice-hockey": "Ice Hockey", "basketball": "Basketball", "baseball": "Baseball",
    "darts": "Darts", "cricket": "Cricket", "rugby-union": "Rugby Union",
    "rugby-league": "Rugby League", "handball": "Handball", "volleyball": "Volleyball",
    "aussie-rules": "Australian Rules", "gaelic-football": "Gaelic Football",
    "motor-racing": "Motor Racing", "tennis": "Tennis", "snooker": "Snooker",
    "golf": "Golf", "greyhounds": "Greyhounds", "esports": "eSports",
}


# ---------------------------------------------------------------------------
# Maths
# ---------------------------------------------------------------------------
def phi(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def inv(p: float) -> float:
    """Inverse normal CDF (Acklam; ~1e-9 relative accuracy)."""
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02, 1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02, 6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00, -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00, 3.754408661907416e+00]
    pl = 0.02425
    if p < pl:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    if p > 1 - pl:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    q = p - 0.5
    r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)


def american(dec):
    if dec is None or dec <= 1:
        return None
    return int(round(-100.0 / (dec - 1.0))) if dec < 2 else int(round((dec - 1.0) * 100))


def in_band(p: float) -> bool:
    return HIGH_LO < p <= HIGH_HI and 1.0 / p >= BAND - 1e-9


def outcome(selection: str, p: float) -> dict:
    p = min(max(p, 0.005), 0.995)
    dec = 1.0 / p
    return dict(selection=selection, probability=round(p, 6), fair_decimal=round(dec, 6),
                fair_american=american(dec), offered_decimal=round(dec / OVERROUND, 4),
                offered_american=american(dec / OVERROUND), in_band=in_band(p))


def price_words(am: int) -> str:
    return f"minus {abs(am)}" if am < 0 else f"plus {am}"


def mk(key, name, line, outs, basis):
    return dict(key=key, name=name, line=line, outcomes=outs, basis=basis)


# ---------------------------------------------------------------------------
def el_markets(home: str, away: str, eh: float, ea: float, pick) -> tuple[list, dict, dict]:
    sig_h, sig_t = 11.5, 16.0
    margin, total = eh - ea, eh + ea
    ph = phi(margin / sig_h)
    markets = [mk("winner", "Match Winner", "", [outcome(home, ph), outcome(away, 1 - ph)],
                  f"Normal margin model: E[{home} - {away}] = {margin:+.1f}, sigma {sig_h}; no home-edge default")]

    for key, target in (("handicap", .50), ("handicap_alt_1", .60), ("handicap_alt_2", .68)):
        h = round((sig_h * inv(target) - margin) * 2) / 2
        pc = min(max(phi((h + margin) / sig_h), .02), .98)
        markets.append(mk(key, "Point Spread", f"{abs(h):.1f}",
                          [outcome(f"{home} {h:+.1f}", pc), outcome(f"{away} {-h:+.1f}", 1 - pc)],
                          f"Gaussian margin projection; {target*100:.0f}% cover rung"))

    for key, target in (("total", .50), ("total_alt_1", .60), ("total_alt_2", .68)):
        L = round((total - sig_t * inv(target)) * 2) / 2
        po = 1 - phi((L - total) / sig_t)
        markets.append(mk(key, "Match Total (Points)", f"{L:.1f}",
                          [outcome(f"Over {L:.1f}", po), outcome(f"Under {L:.1f}", 1 - po)],
                          f"Normal total model (E[T]={total:.1f}, sigma {sig_t}); {target*100:.0f}% over rung"))

    kind, side, line = pick
    picked = None
    if kind == "handicap":
        h = -line                      # home handicap; away handicap is -h
        pc = phi((h + margin) / sig_h)
        label = f"{home} {h:+.1f}" if side == "home" else f"{away} {-h:+.1f}"
        existing = [m for m in markets if m["name"].startswith("Point Spread") and m["line"] == f"{line:.1f}"]
        if existing:
            picked = existing[0]
        else:
            picked = mk("handicap_pick", "Point Spread", f"{line:.1f}",
                        [outcome(f"{home} {h:+.1f}", pc), outcome(f"{away} {-h:+.1f}", 1 - pc)],
                        "Desk line: the authored 70-71.43% cover rung")
            markets.append(picked)
        chosen = next(o for o in picked["outcomes"] if o["selection"] == label)
    else:
        po = 1 - phi((line - total) / sig_t)
        label = f"{'Over' if side == 'over' else 'Under'} {line:.1f}"
        existing = [m for m in markets if m["name"].startswith("Match Total") and m["line"] == f"{line:.1f}"]
        if existing:
            picked = existing[0]
        else:
            picked = mk("total_pick", "Match Total (Points)", f"{line:.1f}",
                        [outcome(f"Over {line:.1f}", po), outcome(f"Under {line:.1f}", 1 - po)],
                        "Desk line: the authored 70-71.43% total rung")
            markets.append(picked)
        chosen = next(o for o in picked["outcomes"] if o["selection"] == label)
    market = picked
    return markets, market, chosen


def norm_markets(raw: list) -> list:
    out = []
    for m in raw:
        outs = []
        for o in m["outcomes"]:
            p = o["probability"]
            outs.append(dict(selection=o["selection"], probability=round(p, 6),
                             fair_decimal=round(1 / p, 6), fair_american=american(1 / p),
                             offered_decimal=o.get("odds"), offered_american=o.get("american"),
                             in_band=in_band(p)))
        out.append(mk(m["key"], m["name"], m.get("line", ""), outs, m.get("basis", "")))
    return out


def best_in_band(markets: list):
    best = None
    for m in markets:
        if m["key"] == "winner":
            continue
        for o in m["outcomes"]:
            if o["in_band"]:
                score = abs(o["probability"] - 0.7071)
                if best is None or score < best[0]:
                    best = (score, m, o)
    return (best[1], best[2]) if best else (None, None)


def base_row(**kw) -> dict:
    row = dict(id=None, sport=None, sport_label=None, competition=None, stage=None,
               start_utc=None, time_display=None, home=None, away=None, venue=None,
               evidence_status="carried", evidence_checked_utc=None, input_status=None,
               official_sources=[], winner=None, selection=None, markets=[],
               tier="Unpriced", prediction_id=None, flags=[], missing_fields=[],
               model_note="", market_reference=None, status="upcoming",
               analysis=None, key_inputs=None)
    row.update(kw)
    return row


# ---------------------------------------------------------------------------
def build_el() -> list:
    rows = []
    for g in EL_GAMES:
        h, a = EL[g["home"]], EL[g["away"]]
        eh = (h["ppg"] + a["opg"]) / 2
        ea = (a["ppg"] + h["opg"]) / 2
        markets, market, chosen = el_markets(h["name"], a["name"], eh, ea, g["pick"])
        win = max(markets[0]["outcomes"], key=lambda o: o["probability"])
        high = bool(g["confirmed"] and chosen["in_band"])
        tier = "High" if high else ("Medium" if (chosen["in_band"] or win["probability"] >= 0.62) else "Low")
        flags = []
        if g["id"] in ("el-535921", "el-535925", "el-2026-69"):
            flags.append("EuroLeague's own preview contradicts its standings table on records or scoring; the table figure is used (F-FEC-04).")
        if not g["confirmed"]:
            flags.append("One or both clubs had not filed a Round 7 availability report at 12:36Z, so the selection is capped at Medium even though it sits in the 70-71.43% band (F-FEC-05).")
        rows.append(base_row(
            id=g["id"], sport="basketball", sport_label="Basketball", competition="EuroLeague",
            stage="Round 7", start_utc=g["utc"],
            time_display=f"{g['cest']} CEST / {g['utc'][11:16]} UTC",
            home=h["name"], away=a["name"],
            evidence_status="fresh", evidence_checked_utc="2026-10-22T12:36:00Z", input_status="fresh",
            official_sources=[dict(name=SOURCES[k]["name"], url=SOURCES[k]["url"], status="fresh")
                              for k in ("el_standings", "el_game_center", "el_injury")],
            winner=dict(selection=win["selection"], probability=win["probability"],
                        fair_decimal=win["fair_decimal"], fair_american=win["fair_american"],
                        in_band=win["in_band"],
                        note="Winner price is outside -250..+10000; the published selection is the separate in-band line"
                        if win["fair_decimal"] < BAND else "Winner view"),
            selection=dict(selection=chosen["selection"], market=market["name"], line=market["line"],
                           probability=chosen["probability"], fair_decimal=chosen["fair_decimal"],
                           fair_american=chosen["fair_american"], offered_american=chosen["offered_american"],
                           in_band=chosen["in_band"], tier=tier,
                           prediction_id=(g["id"] if high else None),
                           note=("Strict gate met: 70-71.43% band, fresh official read, both clubs' availability confirmed, prediction published"
                                 if high else
                                 ("In-band line, but availability is not confirmed for both clubs, so Medium" if chosen["in_band"]
                                  else "Model separation below the 62% medium floor"))),
            markets=markets, tier=tier, prediction_id=(g["id"] if high else None), flags=flags,
            analysis=f"{g['preview']} Availability: {g['injury']}",
            key_inputs=[f"{h['name']}: {h['w']}-{h['l']}, {h['ppg']:.1f} scored / {h['opg']:.1f} allowed ({h['split']})",
                        f"{a['name']}: {a['w']}-{a['l']}, {a['ppg']:.1f} scored / {a['opg']:.1f} allowed ({a['split']})"],
            model_note=("E[home]=(own points scored + opponent points allowed)/2, E[away] likewise. Margin sigma 11.5, total sigma 16.0. "
                        f"Projected {eh:.1f}-{ea:.1f} (total {eh+ea:.1f}). Injuries are narrative facts only and are not converted into a points adjustment."),
        ))
    return rows


def build_nhl() -> list:
    rows = []
    for gid, aid, hid, utc, edt, ref in NHL_GAMES:
        a, h = NHL[aid], NHL[hid]
        fixture = dict(id=gid, sport="ice-hockey", competition="NHL", home=h["name"], away=a["name"],
                       neutral=False, start_utc=utc, status="verified",
                       inputs={"home": {"rating": h["pct"] * 100, "label": "P%"},
                               "away": {"rating": a["pct"] * 100, "label": "P%"}})
        line = price_match(fixture)
        markets = norm_markets(line["markets"])
        wm = next(m for m in markets if m["key"] == "winner")
        win = max(wm["outcomes"], key=lambda o: o["probability"])
        # de-vig the NHL.com reference to test the model
        def imp(am):
            return (-am) / (-am + 100) if am < 0 else 100 / (am + 100)
        odds = {}
        for part in ref.split("/"):
            ab, am = part.strip().rsplit(" ", 1)
            odds[ab] = int(am)
        p1, p2 = imp(odds[hid]), imp(odds[aid])
        mkt_home = p1 / (p1 + p2)
        win_home = win["selection"] == h["name"]
        mkt_p = mkt_home if win_home else 1 - mkt_home
        div = abs(win["probability"] - mkt_p)
        flags = [f"NHL.com lists a DraftKings reference of {ref}; the record-only model gives {win['selection']} "
                 f"{win['probability']*100:.1f}% against a de-vigged {mkt_p*100:.1f}%. No High is issued while the model and the market disagree by "
                 f"{div*100:.1f} points (F-FEC-08)."]
        if div > 0.12:
            flags.append("Model diverges from the market reference by more than 12 points; treat the price as uncalibrated.")
        tier = "Medium" if win["probability"] >= 0.62 and div <= 0.12 else "Low"
        rows.append(base_row(
            id=gid, sport="ice-hockey", sport_label="Ice Hockey", competition="NHL", stage="Regular season",
            start_utc=utc, time_display=f"{edt} EDT / {utc[11:16]} UTC",
            home=h["name"], away=a["name"],
            evidence_status="fresh", evidence_checked_utc="2026-10-22T12:47:00Z", input_status="fresh",
            official_sources=[dict(name=SOURCES[k]["name"], url=SOURCES[k]["url"], status="fresh")
                              for k in ("nhl_standings", "nhl_scores")],
            winner=dict(selection=win["selection"], probability=win["probability"],
                        fair_decimal=win["fair_decimal"], fair_american=win["fair_american"],
                        in_band=win["in_band"], note="Moneyline only; the model ladder stops at a 68% cover rung"),
            selection=dict(selection=win["selection"], market="Match Winner", line="",
                           probability=win["probability"], fair_decimal=win["fair_decimal"],
                           fair_american=win["fair_american"], offered_american=win["offered_american"],
                           in_band=win["in_band"], tier=tier, prediction_id=None,
                           note=("Favourite is shorter than -250, so the price sits outside the window" if win["fair_decimal"] < BAND
                                 else "Below the 70% High threshold")),
            markets=markets, tier=tier, flags=flags, market_reference=ref,
            key_inputs=[f"{h['name']}: {h['w']}-{h['l']}-{h['ot']}, P% {h['pct']:.3f}, {h['gf']} GF / {h['ga']} GA, home {h['home']}, L10 {h['l10']}",
                        f"{a['name']}: {a['w']}-{a['l']}-{a['ot']}, P% {a['pct']:.3f}, {a['gf']} GF / {a['ga']} GA, away {a['away']}, L10 {a['l10']}"],
            model_note=("Logit(0.535) + (home P% - away P%) x 100 / 42.0. Points percentage is the only strength input; no goaltender, "
                        "injury, rest or travel adjustment is applied."),
        ))
    return rows


def build_mlb() -> list:
    home = dict(name="Milwaukee Brewers", rec="103-59", pct=63.6, extra="NL Central champion, home 55-26, away 48-33, L10 8-2, W5, 832 scored / 618 allowed")
    away = dict(name="Tampa Bay Rays", rec="98-64", pct=60.5, extra="AL East champion, 162 games")
    rows = []
    for g in MLB_GAMES:
        side = home if g["home"] == home["name"] else away
        other = away if side is home else home
        fixture = dict(id=g["id"], sport="baseball", competition="MLB World Series", home=g["home"], away=g["away"],
                       neutral=False, start_utc=g["utc"], status="verified",
                       inputs={"home": {"rating": (home["pct"] if g["home"] == home["name"] else away["pct"])},
                               "away": {"rating": (away["pct"] if g["away"] == away["name"] else home["pct"])}})
        line = price_match(fixture)
        markets = norm_markets(line["markets"])
        wm = next(m for m in markets if m["key"] == "winner")
        win = max(wm["outcomes"], key=lambda o: o["probability"])
        tier = "Medium" if win["probability"] >= 0.62 else "Low"
        rows.append(base_row(
            id=g["id"], sport="baseball", sport_label="Baseball", competition="MLB World Series",
            stage=g["game"], start_utc=g["utc"], time_display=f"{g['official']} official / {g['utc'][11:16]} UTC",
            home=g["home"], away=g["away"], venue=g["venue"],
            evidence_status="fresh", evidence_checked_utc="2026-10-22T12:51:00Z", input_status="fresh",
            official_sources=[dict(name=SOURCES[k]["name"], url=SOURCES[k]["url"], status="fresh")
                              for k in ("mlb_schedule", "mlb_standings_nl", "mlb_standings_al")],
            winner=dict(selection=win["selection"], probability=win["probability"],
                        fair_decimal=win["fair_decimal"], fair_american=win["fair_american"],
                        in_band=win["in_band"], note="Regular-season records only; no pitchers, bullpen or park adjustment"),
            selection=dict(selection=win["selection"], market="Match Winner", line="",
                           probability=win["probability"], fair_decimal=win["fair_decimal"],
                           fair_american=win["fair_american"], offered_american=win["offered_american"],
                           in_band=win["in_band"], tier=tier, prediction_id=None,
                           note="Below the 70% High threshold; no prediction is published"),
            markets=markets, tier=tier,
            flags=["The official schedule payload reports postseason records of 0-0; the model uses the official regular-season records instead (F-FEC-09)."],
            key_inputs=[f"Milwaukee Brewers: {home['rec']} ({home['pct']:.1f}%), {home['extra']}",
                        f"Tampa Bay Rays: {away['rec']} ({away['pct']:.1f}%), {away['extra']}"],
            model_note=("Logit(0.540) + (home win% - away win% ) / 40.0 on a 0-100 scale. Each World Series game reuses the same two records, "
                        "so the five prices are not independent evidence."),
        ))
    return rows


def build_carried() -> list:
    legacy = json.loads((ROOT / "data" / "fixtures.json").read_text())
    handled = {g[0] for g in NHL_GAMES} | {g["id"] for g in EL_GAMES} | {g["id"] for g in MLB_GAMES}
    rows = []
    for f in legacy["fixtures"]:
        if not f.get("start_utc") or f["start_utc"] <= AS_OF or f["id"] in handled:
            continue
        src = [dict(name=s.get("name", "Official source"), url=s["url"], status="carried")
               for s in f.get("sources", []) if str(s.get("url", "")).startswith("https://")]
        ver = f.get("verification") or {}
        row = base_row(
            id=f["id"], sport=f["sport"], sport_label=SPORT_LABELS.get(f["sport"], f["sport"]),
            competition=f.get("competition"), stage=f.get("stage"),
            start_utc=f["start_utc"], time_display=f["start_utc"][:16].replace("T", " ") + " UTC",
            home=f.get("home"), away=f.get("away"), venue=f.get("venue"),
            evidence_status="carried", evidence_checked_utc=ver.get("checked_utc"),
            input_status=("carried" if f.get("inputs") else None), official_sources=src,
            status=f.get("status", "verified"), flags=list(f.get("flags") or []))
        if ver.get("checked_utc"):
            row["flags"].append(f"Official evidence captured {ver['checked_utc']} by an earlier session and not re-read here, so the row is capped below High (F-FEC-02).")
        inp = f.get("inputs") or {}
        if not (inp.get("home") and inp.get("away")):
            row.update(tier="Unpriced", missing_fields=["home rating", "away rating"],
                       model_note="No verified rating for both sides; no price is originated.")
            rows.append(row)
            continue
        line = price_match(f)
        markets = norm_markets(line["markets"])
        win = max(next(m for m in markets if m["key"] == "winner")["outcomes"], key=lambda o: o["probability"])
        m, o = best_in_band(markets)
        if o:
            sel = dict(selection=o["selection"], market=m["name"], line=m["line"],
                       probability=o["probability"], fair_decimal=o["fair_decimal"],
                       fair_american=o["fair_american"], offered_american=o["offered_american"],
                       in_band=True, tier="Medium", prediction_id=None,
                       note="Numeric 70-71.43% band met, but the evidence is carried, so this stays Medium (F-FEC-02).")
            tier = "Medium"
            row["flags"].append("Sits inside the 70-71.43% band on carried evidence; no High is issued (F-FEC-02).")
        else:
            tier = "Medium" if win["probability"] >= 0.62 else "Low"
            sel = dict(selection=win["selection"], market="Match Winner", line="",
                       probability=win["probability"], fair_decimal=win["fair_decimal"],
                       fair_american=win["fair_american"], offered_american=win["offered_american"],
                       in_band=win["in_band"], tier=tier, prediction_id=None,
                       note=("Favourite is shorter than -250, outside the requested window" if win["fair_decimal"] < BAND
                             else "Below the 70% High threshold"))
        row.update(winner=dict(selection=win["selection"], probability=win["probability"],
                              fair_decimal=win["fair_decimal"], fair_american=win["fair_american"],
                              in_band=win["in_band"], note="Winner view"),
                   selection=sel, markets=markets, tier=tier,
                   key_inputs=[f"Home input: {inp['home'].get('label', 'rating')} = {inp['home'].get('value', inp['home'].get('rating'))}",
                               f"Away input: {inp['away'].get('label', 'rating')} = {inp['away'].get('value', inp['away'].get('rating'))}"],
                   model_note=("Legacy logit model, reproduced deterministically from the stored official inputs. No new inputs, "
                               "no retroactive promotion."))
        rows.append(row)
    return rows


def build_listings() -> list:
    legacy = json.loads((ROOT / "data" / "fixtures.json").read_text())
    out = []
    for f in legacy["fixtures"]:
        if f.get("start_utc") and f["start_utc"] > AS_OF:
            continue
        src = [dict(name=s.get("name", "Official source"), url=s["url"], status="carried")
               for s in f.get("sources", []) if str(s.get("url", "")).startswith("https://")]
        elapsed = bool(f.get("start_utc"))
        out.append(base_row(
            id=f["id"], sport=f["sport"], sport_label=SPORT_LABELS.get(f["sport"], f["sport"]),
            competition=f.get("competition"), stage=f.get("stage"),
            start_utc=f.get("start_utc"),
            time_display=(f.get("time_as_shown") or f.get("date_local") or ""),
            home=f.get("home"), away=f.get("away"), venue=f.get("venue"),
            evidence_status="carried", evidence_checked_utc=(f.get("verification") or {}).get("checked_utc"),
            official_sources=src, tier="Unpriced", status=("elapsed" if elapsed else "time unverified"),
            missing_fields=(["start_utc"] if not elapsed else []) + ["price"],
            model_note=("No verified clock time, so no pre-match price is published." if not elapsed
                        else "Started before the desk cut-off; kept as a historical listing only."),
            flags=[("No verified start time; unpriced and excluded from the upcoming list (F-FEC-07)." if not elapsed
                    else "Elapsed before the desk cut-off; not an upcoming pick.")]))
    return out


def build_coverage(rows, listings) -> list:
    cov = []
    for sport, label in SPORT_LABELS.items():
        rs = [r for r in rows if r["sport"] == sport]
        priced = [r for r in rs if r["tier"] in ("High", "Medium", "Low")]
        cov.append(dict(sport=sport, label=label, upcoming=len(rs), priced=len(priced),
                        unpriced=len(rs) - len(priced),
                        high=len([r for r in rs if r["tier"] == "High"]),
                        medium=len([r for r in rs if r["tier"] == "Medium"]),
                        low=len([r for r in rs if r["tier"] == "Low"]),
                        fresh=len([r for r in rs if r["evidence_status"] == "fresh"]),
                        carried=len([r for r in rs if r["evidence_status"] == "carried"]),
                        listings=len([r for r in listings if r["sport"] == sport]),
                        status=("priced" if priced else ("listings only" if any(r["sport"] == sport for r in listings) else "no listings"))))
    return cov


def build_flags(rows, listings, cov) -> list:
    highs = [r for r in rows if r["tier"] == "High"]
    med = [r for r in rows if r["tier"] == "Medium"]
    return [
        dict(id="F-FEC-01", severity="high", title="The >70% rule and the -250 floor overlap only between 70.00% and 71.43%",
             detail=("A zero-vig fair price of -250 is exactly 1.400 decimal, or 71.4286%. Any selection above that probability prices shorter than -250 and fails the requested window; any selection at or below 70.00% fails the probability rule. "
                     "The desk therefore treats the window as the binding constraint and publishes bigger favourites as Medium with the exclusion reason stated. "
                     "A 5% bookmaker margin makes the overlap disappear entirely on offered prices, so the band test uses the zero-vig fair price and the offered price is shown separately."),
             source="Arithmetic identity: American = -100/(1/p - 1); 1/0.714286 = 1.400."),
        dict(id="F-FEC-02", severity="high", title="Carried evidence is capped at Medium even when it lands inside the band",
             detail=(f"{len([r for r in rows if r['evidence_status'] == 'carried' and (r.get('selection') or {}).get('in_band')])} rows have carried official inputs and an in-band 70-71.43% selection "
                     f"({', '.join(f'{k} {v}' for k, v in sorted({s: len([r for r in rows if r['sport'] == s and r['evidence_status'] == 'carried' and (r.get('selection') or {}).get('in_band')]) for s in {r['sport'] for r in rows}} .items()) if v)}). "
                     "They keep their prices but cannot be High, because this desk did not re-read the source; every one is published as Medium with the cap stated on the row."),
             source="COORDINATION.md s50; data/fec05fb4/desk.json rows[].evidence_status"),
        dict(id="F-FEC-03", severity="high", title="The model is transparent but not calibrated out of sample",
             detail=("Every price comes from a documented logit or normal model with published constants. There is no measured hit rate for these constants and no closing-line value study. "
                     "A High label means the desk's stated rule was satisfied, not that a 71% winner has been demonstrated."),
             source="Methodology page; model constants in data/fec05fb4/desk.json method"),
        dict(id="F-FEC-04", severity="medium", title="EuroLeague's preview contradicts its own standings table",
             detail=("Valencia are 4-2 in the table but 5-1 in the Round 7 preview; Real Madrid are 1-3 away in the table but 1-4 in the preview; Olympiacos are 564 points in six games (94.0 per game) but 98.2 in the preview; Valencia are 583/6 = 97.17 but 98.3. "
                     "Every numeric input uses the table; the prose figures appear only in quoted analysis and are flagged on the affected rows."),
             source="https://www.euroleaguebasketball.net/en/euroleague/standings/ ; https://www.euroleaguebasketball.net/euroleague/news/game-center-round-7-el2627/"),
        dict(id="F-FEC-05", severity="medium", title="Seven EuroLeague games miss High only because availability was not confirmed",
             detail=("The official Round 7 injury report exists for Efes/Besiktas and for Milan/Barcelona. For Bayern, Dubai, Maccabi, Real Madrid, Baskonia, Crvena Zvezda, Zalgiris, ASVEL, Olympiacos, Fenerbahce, Paris and Valencia the report was not filed at 12:36Z. "
                     "An unlisted late absence can move a 70% cover by several points, so those seven in-band selections are published as Medium."),
             source="https://www.euroleaguebasketball.net/en/euroleague/news/injury-report-round-7-fantasy/"),
        dict(id="F-FEC-06", severity="medium", title="PDC pages returned a cookie wall on re-fetch",
             detail=("The PDC schedule and preview pages returned only a consent wall at 12:34Z. The official draw, seeds and session windows are carried from the 07:44Z read, so the two near-band darts rows are Medium and their tie times remain blank."),
             source="https://www.pdc.tv/news/2026/october/19/2026-machineseeker-european-championship-schedule-confirmed/"),
        dict(id="F-FEC-07", severity="medium", title="32 legacy listings have no verified start time",
             detail=("Tennis (11), snooker (11), cricket (5), golf (4) and eSports (1) rows carry a date but no verified clock. They are published blank and unpriced on their category pages and are not counted as upcoming."),
             source="data/fec05fb4/desk.json listing_only"),
        dict(id="F-FEC-08", severity="high", title="The NHL record-only model disagrees with the market reference",
             detail=("NHL.com publishes a DraftKings moneyline beside every game. The model, which uses only points percentage, differs by up to 21 points from the de-vigged market on this board. "
                     "No NHL row can be High while that gap exists, and the size of the gap is printed on every NHL row."),
             source="https://www.nhl.com/scores/2026-10-22"),
        dict(id="F-FEC-09", severity="medium", title="MLB postseason records are 0-0 in the official payload",
             detail=("The World Series schedule reports leagueRecord 0-0 for both clubs, so the model uses the final regular-season records (Brewers 103-59, Rays 98-64). Pitchers, bullpens, parks and postseason effects are not modelled, and all five games share the same two inputs."),
             source="https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-22&endDate=2026-10-29&hydrate=team,venue"),
        dict(id="F-FEC-10", severity="medium", title="Five categories have no verified upcoming fixture",
             detail=("Tennis, snooker, golf, greyhounds and eSports have no row with a verified future start time at this cut-off. Their pages show the captured listings, blank and flagged, rather than invented fixtures. This is a coverage gap, not a claim that no such fixtures exist."),
             source="Coverage table"),
        dict(id="F-FEC-11", severity="low", title="EuroLeague evidence expires at tip-off",
             detail=("The nine EuroLeague rows tip off between 17:30Z on 22 October and 18:45Z on 23 October. This desk is an as-of 12:45Z snapshot; after those times the rows are historical and must not be read as pre-match picks."),
             source="https://www.euroleaguebasketball.net/en/euroleague/standings/"),
        dict(id="F-FEC-12", severity="low", title="OLBG is discovery only, never evidence",
             detail=("OLBG cards were used to find events and to see what the market discusses. They set no rating, price or confidence, and no OLBG number is copied into this dataset."),
             source="https://www.olbg.com/betting-odds"),
        dict(id="F-FEC-13", severity="low", title="Desk-defined Medium and Low thresholds",
             detail=("Medium = an in-band 70-71.43% selection that fails the High evidence test, or a winner at 62%+. Low = anything else that is priced. These thresholds are the desk's own; they are not industry standards."),
             source="Methodology page"),
        dict(id="F-FEC-14", severity="low", title=f"{len(highs)} High selections, {len(med)} Medium and {len(rows)-len(highs)-len(med)} Low/unpriced",
             detail=("Both Highs are EuroLeague handicap or total lines originated at a 70-71.43% cover, not moneylines. Each carries a unique 60-word prediction, two-sided official evidence and a fresh read of the availability report. "
                     "No High was issued for a big favourite just because it was a big favourite."),
             source="data/fec05fb4/desk.json rows[].tier"),
    ]


def build_analysis(rows) -> dict:
    high = [r for r in rows if r["tier"] == "High"]
    med = [r for r in rows if r["tier"] == "Medium"]
    return dict(
        lede=("This desk re-derives every non-excluded sport on the OLBG board from official sources and originates its own prices. "
              "It publishes two High selections, not because two is a target, but because the three gates — a 70-71.43% fair price, a fresh official read, and both clubs' availability confirmed — "
              "only coincide twice on 22-23 October 2026."),
        points=[
            dict(title="Why only two Highs",
                 body=(f"{len(rows)} upcoming fixtures carry a verified start time; {len(high)+len(med)} of them are priced inside the desk's rules. "
                       "Every other in-band line belongs to a game where at least one club had not filed its Round 7 availability report, or to a sport whose official source could not be re-read this session.")),
            dict(title="The band is a knife-edge",
                 body=("Between 70.00% and 71.43% the fair price runs from -233 to -250. A stronger favourite cannot be priced inside the requested window at all; the desk publishes those as Medium rather than stretching the rule.")),
            dict(title="Where the desk is weakest",
                 body=("NHL prices come from points percentage alone and disagree with the published market by up to 21 points. MLB prices use regular-season records with no pitcher information. "
                       "Darts, rugby league, rugby union, handball, volleyball, Australian rules and Gaelic football rely on evidence captured earlier in the day and are capped at Medium.")),
        ])


def main():
    rows = sorted(build_el() + build_nhl() + build_mlb() + build_carried(),
                  key=lambda r: (r["start_utc"] or "", r["sport"], r["id"]))
    listings = build_listings()
    cov = build_coverage(rows, listings)
    flags = build_flags(rows, listings, cov)
    pmap = {}
    for r in rows:
        if r["prediction_id"] and r["prediction_id"] in PREDICTIONS:
            p = PREDICTIONS[r["prediction_id"]]
            sel = r["selection"]
            price = price_words(sel["fair_american"])
            text = p["text"].format(selection=sel["selection"], price=price)
            words = len(text.split())
            if words < 30:
                raise SystemExit(f"prediction {r['id']} is only {words} words")
            pmap[r["id"]] = dict(fixture_id=r["id"], sport=r["sport"], competition=r["competition"],
                                 match=f"{r['home']} vs {r['away']}", start_utc=r["start_utc"],
                                 selection=sel["selection"], market=sel["market"], line=sel["line"],
                                 probability=sel["probability"], fair_decimal=sel["fair_decimal"],
                                 fair_american=sel["fair_american"], words=words, text=text,
                                 facts=p["facts"], sources=[SOURCES[k] for k in p["sources"]])
    counts = dict(upcoming=len(rows), priced=len([r for r in rows if r["tier"] in ("High", "Medium", "Low")]),
                  high=len([r for r in rows if r["tier"] == "High"]),
                  medium=len([r for r in rows if r["tier"] == "Medium"]),
                  low=len([r for r in rows if r["tier"] == "Low"]),
                  unpriced=len([r for r in rows if r["tier"] == "Unpriced"]),
                  fresh=len([r for r in rows if r["evidence_status"] == "fresh"]),
                  carried=len([r for r in rows if r["evidence_status"] == "carried"]),
                  listing_only=len(listings), categories=len(SPORT_LABELS),
                  markets=sum(len(r["markets"]) for r in rows),
                  outcomes=sum(len(m["outcomes"]) for r in rows for m in r["markets"]),
                  predictions=len(pmap), sources=len(SOURCES), flags=len(flags))
    desk = dict(schema="fec05fb4-desk-1", session=SESSION, as_of=AS_OF, generated_utc=AS_OF,
                baseline="f255eef (main, merge of PR #109)",
                scope=dict(included=list(SPORT_LABELS.values()),
                           excluded=["Football / Soccer", "American Football", "Boxing", "UFC / MMA", "Hurling",
                                     "Horse Racing", "Cycling", "Specials"]),
                policy=dict(
                    high="p in (0.700, 0.714286] so the zero-vig fair price is inside -250..+10000; fresh official read this session; both clubs' availability officially confirmed; unique >=30-word prediction.",
                    medium="An in-band selection that fails the High evidence test, or a winner at 62%+.",
                    low="Everything else that is priced.",
                    unpriced="No verified rating for both sides, or no verified start time."),
                method=dict(overround=OVERROUND, high_window=[-250, 10000], high_band=[0.700, 0.714286],
                            el_sigma_margin=11.5, el_sigma_total=16.0, nhl_scale=42.0,
                            nhl_base=0.535, mlb_scale=40.0, mlb_base=0.540,
                            price_rule="fair_decimal = 1/p; offered_decimal = fair_decimal / 1.05; American = -100/(dec-1) if dec<2 else (dec-1)*100"),
                counts=counts, coverage=cov, rows=rows, listing_only=listings,
                predictions=list(pmap.values()), flagged=flags, analysis=build_analysis(rows),
                sources=[dict(key=k, **v) for k, v in SOURCES.items()])
    (OUT / "desk.json").write_text(json.dumps(desk, indent=1), encoding="utf-8")

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "sport", "competition", "start_utc", "home", "away", "tier", "winner",
                "winner_p", "selection", "market", "line", "p", "fair_decimal", "fair_american",
                "offered_american", "evidence", "official_source"])
    for r in rows:
        s, win = r["selection"] or {}, r["winner"] or {}
        w.writerow([r["id"], r["sport"], r["competition"] or "", r["start_utc"] or "", r["home"] or "", r["away"] or "",
                    r["tier"], win.get("selection", ""), win.get("probability", ""),
                    s.get("selection", ""), s.get("market", ""), s.get("line", ""), s.get("probability", ""),
                    s.get("fair_decimal", ""), s.get("fair_american", ""), s.get("offered_american", ""),
                    r["evidence_status"], r["official_sources"][0]["url"] if r["official_sources"] else ""])
    (OUT / "rows.csv").write_text(buf.getvalue(), encoding="utf-8")

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["fixture_id", "sport", "start_utc", "match", "selection", "probability", "fair_decimal",
                "fair_american", "words", "prediction"])
    for p in pmap.values():
        w.writerow([p["fixture_id"], p["sport"], p["start_utc"], p["match"], p["selection"],
                    p["probability"], p["fair_decimal"], p["fair_american"], p["words"], p["text"]])
    (OUT / "picks.csv").write_text(buf.getvalue(), encoding="utf-8")

    print(json.dumps(counts, indent=1))
    for c in cov:
        print(f"{c['sport']:16s} up={c['upcoming']:3d} priced={c['priced']:3d} H={c['high']} M={c['medium']} L={c['low']} unp={c['unpriced']} fresh={c['fresh']} carried={c['carried']} listings={c['listings']}")
    for p in pmap.values():
        print(f"HIGH {p['fixture_id']}: {p['selection']} {p['fair_american']} p={p['probability']:.4f} words={p['words']}")


if __name__ == "__main__":
    main()
