#!/usr/bin/env python3
"""Session fa24508c-olbg1 — 23 October 2026 desk dataset.

Every fact in this module was read from the URL recorded beside it during the
observation window stamped in ``SESSION``.  Values that could not be read from an
official publisher are left as ``None`` and are flagged, never inferred.

Discovery (which events exist, tip counts, tip shares) comes from the OLBG sport
hubs.  OLBG is a discovery layer only: it cannot verify a sporting fact, so no
official field is ever sourced to it.
"""
from __future__ import annotations

SESSION = {
    "id": "fa24508c-olbg1",
    "branch": "arena/fa24508c-olbg1",
    "desk": "fa24508c",
    "date": "2026-10-23",
    "window_start_utc": "2026-10-23T16:17:00Z",
    "window_end_utc": "2026-10-23T16:52:00Z",
}

OLBG = "https://www.olbg.com"

# ---------------------------------------------------------------------------
# 1. Official sources actually read this session
# ---------------------------------------------------------------------------
SOURCES = [
    {
        "id": "S-MLB-SCHED",
        "name": "MLB Stats API — schedule, 23 Oct 2026",
        "url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-10-23",
        "publisher": "Major League Baseball",
        "read_utc": "2026-10-23T16:24:00Z",
        "used_for": "World Series Game 1: gamePk 849805, TB @ MIL, 2026-10-24T00:00Z, American Family Field, ifNecessary=N, seriesGameNumber 1 of 7",
        "status": "read",
    },
    {
        "id": "S-MLB-TB",
        "name": "MLB Stats API — Tampa Bay Rays 2026 regular-season record",
        "url": "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsTypes=regularSeason",
        "publisher": "Major League Baseball",
        "read_utc": "2026-10-23T16:31:00Z",
        "used_for": "TB 98-64 (.605), 736 runs scored / 650 allowed, away 43-38, last ten 5-5",
        "status": "read",
    },
    {
        "id": "S-MLB-MIL",
        "name": "MLB Stats API — Milwaukee Brewers 2026 regular-season record",
        "url": "https://statsapi.mlb.com/api/v1/teams/158?season=2026&hydrate=standings",
        "publisher": "Major League Baseball",
        "read_utc": "2026-10-23T16:31:00Z",
        "used_for": "MIL 103-59 (.636), 832 runs scored / 618 allowed, home 55-26, last ten 8-2, streak W5",
        "status": "read",
    },
    {
        "id": "S-NHL-SCHED",
        "name": "NHL API — schedule for 23 Oct 2026 with league odds",
        "url": "https://api-web.nhle.com/v1/schedule/2026-10-23",
        "publisher": "National Hockey League",
        "read_utc": "2026-10-23T16:27:00Z",
        "used_for": "Two games: 2026020166 MTL @ CHI (United Center, 2026-10-24T00:00Z) and 2026020167 TBL @ COL (Ball Arena, 2026-10-24T01:00Z); league-published odds quotes",
        "status": "read",
    },
    {
        "id": "S-NHL-STAND",
        "name": "NHL API — 2026-27 standings at 2026-10-23T16:17:45Z",
        "url": "https://api-web.nhle.com/v1/standings/2026-10-23",
        "publisher": "National Hockey League",
        "read_utc": "2026-10-23T16:41:00Z",
        "used_for": "MTL 4-3-2 (10 pts, 30 GF/34 GA); CHI 3-6-0 (6 pts, 21/36); TBL 7-2-0 (14 pts, 31/23); COL 5-4-1 (11 pts, 41/31)",
        "status": "read",
    },
    {
        "id": "S-NBA-GAMES",
        "name": "NBA.com — games for 23 October 2026",
        "url": "https://www.nba.com/games?date=2026-10-23",
        "publisher": "National Basketball Association",
        "read_utc": "2026-10-23T16:35:00Z",
        "used_for": "12 NBA games with tip times (ET), current 2026-27 records and official game IDs",
        "status": "read",
    },
    {
        "id": "S-URC-R4",
        "name": "United Rugby Championship — match centre, Round 4",
        "url": "https://stats.unitedrugby.com/match-centre/2026-27/4",
        "publisher": "United Rugby Championship",
        "read_utc": "2026-10-23T16:29:00Z",
        "used_for": "Round 4 fixtures and venues: Cardiff v Sharks, Connacht v Zebre Parma, Edinburgh v Lions (Fri 23 Oct, 14:45 local)",
        "status": "read",
    },
    {
        "id": "S-URC-R1",
        "name": "URC match centre — Round 1 results",
        "url": "https://stats.unitedrugby.com/match-centre/2026-27/1",
        "publisher": "United Rugby Championship",
        "read_utc": "2026-10-23T16:45:00Z",
        "used_for": "Round 1 scorelines used for form (see FORM entries)",
        "status": "read",
    },
    {
        "id": "S-URC-R2",
        "name": "URC match centre — Round 2 results",
        "url": "https://stats.unitedrugby.com/match-centre/2026-27/2",
        "publisher": "United Rugby Championship",
        "read_utc": "2026-10-23T16:45:00Z",
        "used_for": "Round 2 scorelines read: CAR 40-27 ZEB, EDI 17-13 STO (remaining Round 2 fixtures not captured in the page portion read)",
        "status": "partial",
    },
    {
        "id": "S-URC-R3",
        "name": "URC match centre — Round 3 results (page header block)",
        "url": "https://stats.unitedrugby.com/match-centre/2026-27/4",
        "publisher": "United Rugby Championship",
        "read_utc": "2026-10-23T16:29:00Z",
        "used_for": "Round 3 scorelines: GLA 36-19 CON, DRA 31-38 OSP, BUL 57-15 LIO, STO 39-22 SHA, ZEB 12-29 EDI, SCA 27-26 BEN, ULS 26-26 MUN, LEI 29-5 CAR",
        "status": "read",
    },
    {
        "id": "S-WST-MATCHES",
        "name": "World Snooker Tour — BetVictor Northern Ireland Open 2026 matches",
        "url": "https://www.wst.tv/matches/",
        "publisher": "World Snooker Tour",
        "read_utc": "2026-10-23T16:33:00Z",
        "used_for": "Quarter-finals on Fri 23 Oct 14:00: Match 60 Jak Jones v Scott Donaldson; Match 59 David Gilbert v Mark Williams. Completed QFs: McGill 1-6 Kyren Wilson, Craigie 6-2 Slessor",
        "status": "read",
    },
    {
        "id": "S-WST-RANK",
        "name": "WST — Johnstone's Paint World Rankings and One Year List",
        "url": "https://www.wst.tv/rankings/",
        "publisher": "World Snooker Tour",
        "read_utc": "2026-10-23T16:44:00Z",
        "used_for": "Mark Williams world no. 8 (£747,400); Jak Jones fourth on the one-year list (£141,000); David Gilbert eleventh on the one-year list (£73,250); Scott Donaldson and Gilbert do not appear in the top eleven of the world list",
        "status": "read",
    },
    {
        "id": "S-F1-USGP",
        "name": "Formula 1 — 2026 United States Grand Prix weekend schedule",
        "url": "https://www.formula1.com/en/racing/2026/united-states",
        "publisher": "Formula 1",
        "read_utc": "2026-10-23T16:34:00Z",
        "used_for": "COTA: FP1 Fri 23 Oct 13:30, FP2 17:00, FP3 Sat 13:30, Qualifying Sat 17:00, Race Sun 25 Oct 16:00 track time; 56 laps, 5.513 km, 308.432 km",
        "status": "read",
    },
    {
        "id": "S-MUNSTER",
        "name": "Munster GAA — fixtures and results",
        "url": "https://munster.gaa.ie/fixtures-results/",
        "publisher": "Munster GAA",
        "read_utc": "2026-10-23T16:47:00Z",
        "used_for": "Official fixture list consulted for the OLBG Gaelic club fixtures; the club senior fixtures listed by OLBG were not located in the page portion read, so they stay unverified",
        "status": "partial",
    },
    {
        "id": "S-PDC",
        "name": "PDC — Machineseeker European Championship",
        "url": "https://www.pdc.tv/tournaments/machineseeker-european-championship",
        "publisher": "Professional Darts Corporation",
        "read_utc": "2026-10-23T16:28:00Z",
        "used_for": "Attempted fixture verification — the response served a cookie-consent shell with no schedule content (flagged F-10)",
        "status": "blocked",
    },
    {
        "id": "S-ATP",
        "name": "ATP Tour — current scores",
        "url": "https://www.atptour.com/en/scores/current/view-all",
        "publisher": "ATP Tour",
        "read_utc": "2026-10-23T16:33:00Z",
        "used_for": "Attempted fixture verification — the response contained navigation and footer only, no draw or order of play (flagged F-11)",
        "status": "blocked",
    },
    {
        "id": "S-GBGB",
        "name": "GBGB — race card",
        "url": "https://www.gbgb.org.uk/race-card/",
        "publisher": "Greyhound Board of Great Britain",
        "read_utc": "2026-10-23T16:39:00Z",
        "used_for": "Attempted racecard verification — HTTP 404 (flagged F-12)",
        "status": "blocked",
    },
]

# ---------------------------------------------------------------------------
# 2. Discovery layer — every event the OLBG sport hubs listed in the window
#    (sport, competition, label, olbg_start_text, selection, market, tip_share,
#     url, event_id)
# ---------------------------------------------------------------------------
D = []


def disc(sport, comp, label, when, sel, market, share, url, eid):
    D.append({
        "sport": sport, "competition": comp, "label": label, "olbg_start": when,
        "selection": sel, "market": market, "tip_share": share,
        "url": url, "event_id": eid,
    })


T = OLBG + "/betting-tips/Tennis/All_Tennis/All_Events/"
disc("Tennis", "ATP/WTA", "Arthur Fils vs Alex Michelsen", "Today 12:30", "Arthur Fils", "Win Match", 50, T + "Arthur_Fils_vs_Alex_Michelsen/3?event_id=902150", 902150)
disc("Tennis", "ATP/WTA", "Flavio Cobolli vs Brandon Nakashima", "Today 13:00", "Flavio Cobolli", "Win Match", 63, T + "Flavio_Cobolli_vs_Brandon_Nakashima/3?event_id=902155", 902155)
disc("Tennis", "ATP/WTA", "Jan Lennard Struff vs Zizou Bergs", "Today 14:00", "Jan Lennard Struff", "Win Match", 63, T + "Jan_Lennard_Struff_vs_Zizou_Bergs/3?event_id=902153", 902153)
disc("Tennis", "ATP/WTA", "Luca Van Assche vs Lorenzo Musetti", "Today 14:30", "Luca Van Assche", "Win Match", 60, T + "Luca_Van_Assche_vs_Lorenzo_Musetti/3?event_id=902147", 902147)
disc("Tennis", "ATP/WTA", "Ann Li vs Ashlyn Krueger", "Today 23:00", "Over 22.50", "Total Games", 67, T + "Ann_Li_vs_Ashlyn_Krueger/3?event_id=902157", 902157)
disc("Tennis", "ATP/WTA", "Katie Boulter vs Katerina Siniakova", "Tomorrow 00:30", "Katie Boulter", "Win Match", 100, T + "Katie_Boulter_vs_Katerina_Siniakova/3?event_id=902162", 902162)
disc("Tennis", "ATP/WTA", "Leylah Fernandez vs Marie Bouzkova", "Tomorrow 03:00", "Leylah Fernandez", "Win Match", 100, T + "Leylah_Fernandez_vs_Marie_Bouzkova/3?event_id=902160", 902160)
disc("Tennis", "ATP/WTA", "Elena Rybakina vs Diana Shnaider", "Tomorrow 05:30", "Diana Shnaider", "Win Match", 100, T + "Elena_Rybakina_vs_Diana_Shnaider/3?event_id=902163", 902163)
disc("Tennis", "ATP/WTA", "Nikoloz Basilashvili vs Stefanos Tsitsipas", "Tomorrow 06:00", "Tsitsipas 2-1", "Set Betting", 100, T + "Nikoloz_Basilashvili_vs_Stefanos_Tsitsipas/3?event_id=902159", 902159)

DA = OLBG + "/betting-tips/Darts/All_Darts/All_Events/"
disc("Darts", "PDC European Championship", "Jonny Clayton vs Niko Springer", "Today 14:45", "Jonny Clayton", "Win Match 2-way", 84, DA + "Jonny_Clayton_vs_Niko_Springer/15?event_id=32335", 32335)
disc("Darts", "PDC European Championship", "Wessel Nijman vs Martin Schindler", "Today 15:45", "Wessel Nijman", "Win Match 2-way", 78, DA + "Wessel_Nijman_vs_Martin_Schindler/15?event_id=32326", 32326)
disc("Darts", "PDC European Championship", "Ryan Joyce vs Jermaine Wattimena", "Today 13:15", "Ryan Joyce", "Win Match 2-way", 64, DA + "Ryan_Joyce_vs_Jermaine_Wattimena/15?event_id=32332", 32332)
disc("Darts", "PDC European Championship", "Krzysztof Ratajski vs Dave Chisnall", "Today 13:45", "Krzysztof Ratajski", "Win Match 2-way", 58, DA + "Krzysztof_Ratajski_vs_Dave_Chisnall/15?event_id=32333", 32333)
disc("Darts", "PDC European Championship", "Nathan Aspinall vs Cristo Reyes", "Today 14:15", "Nathan Aspinall", "Win Match 2-way", 64, DA + "Nathan_Aspinall_vs_Cristo_Reyes/15?event_id=32327", 32327)
disc("Darts", "PDC European Championship", "Luke Littler vs William OConnor", "Today 15:15", "Luke Littler", "Win Match 2-way", 70, DA + "Luke_Littler_vs_William_OConnor/15?event_id=32328", 32328)
disc("Darts", "PDC European Championship", "Kevin Doets vs Michael van Gerwen", "Today 16:15", "Michael van Gerwen", "Win Match 2-way", 59, DA + "Kevin_Doets_vs_Michael_van_Gerwen/15?event_id=32331", 32331)
disc("Darts", "PDC European Championship", "Josh Rock vs Chris Dobey", "Today 16:45", "Josh Rock", "Win Match 2-way", 53, DA + "Josh_Rock_vs_Chris_Dobey/15?event_id=32336", 32336)
disc("Darts", "PDC European Championship", "Stephen Bunting vs Kim Huybrechts", "Tomorrow 13:15", "Kim Huybrechts", "Win Match 2-way", 67, DA + "Stephen_Bunting_vs_Kim_Huybrechts/15?event_id=32384", 32384)
disc("Darts", "PDC European Championship", "Gian van Veen vs Luke Woodhouse", "Tomorrow 13:15", "Luke Woodhouse", "Win Match 2-way", 67, DA + "Gian_van_Veen_vs_Luke_Woodhouse/15?event_id=32385", 32385)
disc("Darts", "PDC European Championship", "Ross Smith vs Damon Heta", "Tomorrow 13:15", "Damon Heta", "Win Match 2-way", 67, DA + "Ross_Smith_vs_Damon_Heta/15?event_id=32386", 32386)
disc("Darts", "PDC European Championship", "Cameron Menzies vs Gerwyn Price", "Tomorrow 13:15", "Gerwyn Price", "Win Match 2-way", 50, DA + "Cameron_Menzies_vs_Gerwyn_Price/15?event_id=32383", 32383)

DS = OLBG + "/betting-tips/Snooker/All_Snooker/All_Events/"
disc("Snooker", "Northern Ireland Open 2026 (QF)", "Jak Jones vs Scott Donaldson", "Today 14:05", "Jak Jones", "Win Match", 73, DS + "Jak_Jones_vs_Scott_Donaldson/8?event_id=9951", 9951)
disc("Snooker", "Northern Ireland Open 2026 (QF)", "David Gilbert vs Mark Williams", "Today 14:05", "Mark Williams", "Win Match", 73, DS + "David_Gilbert_vs_Mark_Williams/8?event_id=9950", 9950)

DB = OLBG + "/betting-tips/Basketball/"
disc("Basketball", "EuroLeague", "Zalgiris vs Asvel Lyon Villeurbanne", "Today 13:00", "Zalgiris", "Money Line", 56, DB + "European/Euroleague/Zalgiris_vs_Asvel_Lyon_Villeurbanne/4?event_id=535928", 535928)
disc("Basketball", "EuroLeague", "Olympiacos vs Fenerbahce", "Today 14:15", "Olympiacos", "Money Line", 60, DB + "European/Euroleague/Olympiacos_vs_Fenerbahce/4?event_id=535925", 535925)
disc("Basketball", "EuroLeague", "Paris vs Valencia", "Today 14:45", "Valencia", "Money Line", 50, DB + "European/Euroleague/Paris_vs_Valencia/4?event_id=535926", 535926)
disc("Basketball", "NBA", "CHI Bulls @ MIL Bucks", "Today 16:10", "MIL Bucks", "Money Line", 100, DB + "NBA/NBA/CHI_Bulls_@_MIL_Bucks/4?event_id=536041", 536041)
disc("Basketball", "NBA", "MIN Timberwolves @ ORL Magic", "Today 19:10", "MIN Timberwolves", "Money Line", 100, DB + "NBA/NBA/MIN_Timberwolves_@_ORL_Magic/4?event_id=536036", 536036)
disc("Basketball", "NBA", "HOU Rockets @ SA Spurs", "Today 21:40", "SA Spurs", "Money Line", 67, DB + "NBA/NBA/HOU_Rockets_@_SA_Spurs/4?event_id=534841", 534841)
disc("Basketball", "NBA", "NY Knicks @ BOS Celtics", "Today 19:10", "BOS Celtics -2.50", "Pointspread", 100, DB + "NBA/NBA/NY_Knicks_@_BOS_Celtics/4?event_id=534842", 534842)
disc("Basketball", "NBA", "TOR Raptors @ WAS Wizards", "Today 19:10", "TOR Raptors", "Money Line", 75, DB + "NBA/NBA/TOR_Raptors_@_WAS_Wizards/4?event_id=536034", 536034)
disc("Basketball", "NBA", "DAL Mavericks @ IND Pacers", "Today 19:10", "IND Pacers", "Money Line", 100, DB + "NBA/NBA/DAL_Mavericks_@_IND_Pacers/4?event_id=536037", 536037)
disc("Basketball", "NBA", "DET Pistons @ MIA Heat", "Today 20:10", "DET Pistons", "Money Line", 100, DB + "NBA/NBA/DET_Pistons_@_MIA_Heat/4?event_id=536038", 536038)
disc("Basketball", "NBA", "POR Trail Blazers @ SAC Kings", "Today 22:10", "POR -10.50", "Pointspread", 100, DB + "NBA/NBA/POR_Trail_Blazers_@_SAC_Kings/4?event_id=536043", 536043)
disc("Basketball", "NBA", "ATL Hawks @ CHA Hornets", "Today 19:10", "ATL Hawks -2.50", "Pointspread", 100, DB + "NBA/NBA/ATL_Hawks_@_CHA_Hornets/4?event_id=536035", 536035)
disc("Basketball", "NBA", "NO Pelicans @ UTA Jazz", "Today 21:40", "UTA Jazz", "Money Line", 100, DB + "NBA/NBA/NO_Pelicans_@_UTA_Jazz/4?event_id=536040", 536040)
disc("Basketball", "NBA", "LA Clippers @ LA Lakers", "Today 22:10", "LA Clippers +9.50", "Pointspread", None, DB + "NBA/NBA/LA_Clippers_@_LA_Lakers/4?event_id=536042", 536042)
disc("Basketball", "Poland PLK", "Gtk Gliwice vs Torun", "Today 14:15", "Torun", "Money Line", 67, DB + "European/Poland_PLK/Gtk_Gliwice_vs_Torun/4?event_id=536031", 536031)

DI = OLBG + "/betting-tips/Ice_Hockey/"
disc("Ice Hockey", "Danish Metal Ligaen", "Esbjerg Energy vs Herning Blue Fox", "Today 13:00", "Herning Blue Fox", "Money Line", 100, DI + "Other/Danish_Metal_Ligaen/Esbjerg_Energy_vs_Herning_Blue_Fox/13?event_id=199946", 199946)
disc("Ice Hockey", "NHL", "MTL Canadiens @ CHI Blackhawks", "Today 20:07", "MTL Canadiens", "Money Line", 100, DI + "NHL/NHL/MTL_Canadiens_@_CHI_Blackhawks/13?event_id=199984", 199984)
disc("Ice Hockey", "Germany Eishockey Liga", "Grizzlys Wolfsburg vs ERC Ingolstadt", "Today 13:30", "ERC Ingolstadt", "Money Line", 100, DI + "Other/Germany_Eishockey_Liga/Grizzlys_Wolfsburg_vs_ERC_Ingolstadt/13?event_id=199927", 199927)
disc("Ice Hockey", "Danish Metal Ligaen", "Rodovre Mighty Bulls vs Herlev Eagles", "Today 13:30", "Herlev Eagles", "Money Line", 100, DI + "Other/Danish_Metal_Ligaen/Rodovre_Mighty_Bulls_vs_Herlev_Eagles/13?event_id=199947", 199947)
disc("Ice Hockey", "Finland SM Liiga", "K Espoo vs HIFK", "Today 12:30", "Over 5.50", "Game Totals", 100, DI + "Other/Finland_SM_Liiga/K_Espoo_vs_HIFK/13?event_id=199955", 199955)
disc("Ice Hockey", "Austria EHL", "Graz 99ers vs EHC Black Wings Linz", "Today 12:30", "Linz +1.50", "Puck Line", 50, DI + "Other/Austria_EHL/Graz_99ers_vs_EHC_Black_Wings_Linz/13?event_id=199965", 199965)
disc("Ice Hockey", "Austria EHL", "HK Olimpija Ljubljana vs Fehervar AV19", "Today 13:15", "Olimpija -1.50", "Puck Line", 100, DI + "Other/Austria_EHL/HK_Olimpija_Ljubljana_vs_Fehervar_AV19/13?event_id=199969", 199969)
disc("Ice Hockey", "Germany Eishockey Liga", "Eisbaren Berlin vs Augsburger Panther", "Today 13:30", "Eisbaren Berlin -1.50", "Puck Line", 100, DI + "Other/Germany_Eishockey_Liga/Eisbaren_Berlin_vs_Augsburger_Panther/13?event_id=199926", 199926)
disc("Ice Hockey", "Germany Eishockey Liga", "Adler Mannheim vs Lowen Frankfurt", "Today 13:30", "Adler Mannheim", "Money Line", 100, DI + "Other/Germany_Eishockey_Liga/Adler_Mannheim_vs_Lowen_Frankfurt/13?event_id=199925", 199925)
disc("Ice Hockey", "Germany Eishockey Liga", "Nurnberg Ice Tigers vs Krefeld Pinguine", "Today 13:30", "Under 5.50", "Game Totals", 100, DI + "Other/Germany_Eishockey_Liga/Nurnberg_Ice_Tigers_vs_Krefeld_Pinguine/13?event_id=199928", 199928)
disc("Ice Hockey", "Germany Eishockey Liga", "EHC Munchen vs Iserlohn Roosters", "Today 13:30", "EHC Munchen", "Money Line", 100, DI + "Other/Germany_Eishockey_Liga/EHC_Munchen_vs_Iserlohn_Roosters/13?event_id=199924", 199924)
disc("Ice Hockey", "Germany Eishockey Liga", "Straubing Tigers vs Kolner Haie", "Today 13:30", "Under 5.50", "Game Totals", 100, DI + "Other/Germany_Eishockey_Liga/Straubing_Tigers_vs_Kolner_Haie/13?event_id=199930", 199930)
disc("Ice Hockey", "Austria EHL", "Pioneers Vorarlberg vs HCB Sudtirol Alperia", "Today 13:30", "HCB Sudtirol", "Money Line", 100, DI + "Other/Austria_EHL/Pioneers_Vorarlberg_vs_HCB_Sudtirol_Alperia/13?event_id=199968", 199968)
disc("Ice Hockey", "Switzerland NLA", "Fribourg Gotteron vs EHC Biel", "Today 13:45", "Fribourg Gotteron", "Money Line", 100, DI + "Other/Switzerland_NLA/Fribourg_Gotteron_vs_EHC_Biel/13?event_id=199908", 199908)

DBB = OLBG + "/betting-tips/Baseball/MLB/MLB/"
disc("Baseball", "MLB World Series G1", "TB Rays @ MIL Brewers", "Today 20:00", "MIL Brewers", "Money Line", 81, DBB + "TB_Rays_@_MIL_Brewers/12?event_id=160789", 160789)

DR = OLBG + "/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/"
disc("Rugby Union", "Pro D2", "Aurillac v Nevers", "Today 13:30", "Aurillac", "To Win", 74, DR + "Aurillac_v_Nevers/9?event_id=609560", 609560)
disc("Rugby Union", "Pro D2", "Agen v Nissa", "Today 13:30", "Agen", "To Win", 67, DR + "Agen_v_Nissa/9?event_id=609558", 609558)
disc("Rugby Union", "Pro D2", "Narbonne v Brive", "Today 13:00", "Brive", "To Win", 65, DR + "Narbonne_v_Brive/9?event_id=609557", 609557)
disc("Rugby Union", "URC", "Connacht v Zebre Parma", "Today 14:45", "Connacht", "To Win", 73, DR + "Connacht_v_Zebre_Parma/9?event_id=609577", 609577)
disc("Rugby Union", "URC", "Edinburgh v Lions", "Today 14:45", "Edinburgh", "To Win", 89, DR + "Edinburgh_v_Lions/9?event_id=609579", 609579)
disc("Rugby Union", "Pro D2", "Soyaux Angouleme v Dax", "Today 13:30", "Dax", "To Win", 50, DR + "Soyaux_Angouleme_v_Dax/9?event_id=609563", 609563)
disc("Rugby Union", "Premiership", "Gloucester v Bath", "Today 14:45", "Gloucester", "To Win", 100, DR + "Gloucester_v_Bath/9?event_id=609570", 609570)
disc("Rugby Union", "Pro D2", "Valence Romans v Colomiers", "Today 13:30", "Valence Romans", "To Win", 55, DR + "Valence_Romans_v_Colomiers/9?event_id=609559", 609559)
disc("Rugby Union", "Pro D2", "Provence v Beziers", "Today 15:00", "Provence", "To Win", 60, DR + "Provence_v_Beziers/9?event_id=609562", 609562)
disc("Rugby Union", "Pro D2", "Grenoble v Biarritz", "Today 15:00", "Grenoble", "To Win", 60, DR + "Grenoble_v_Biarritz/9?event_id=609561", 609561)
disc("Rugby Union", "URC", "Cardiff v Sharks", "Today 14:45", "Sharks", "To Win", 57, DR + "Cardiff_v_Sharks/9?event_id=609575", 609575)
disc("Rugby Union", "Premiership", "Newcastle Red Bulls v Sale Sharks", "Today 14:45", "Sale Sharks", "To Win", 60, DR + "Newcastle_Red_Bulls_v_Sale_Sharks/9?event_id=609573", 609573)
disc("Rugby Union", "URC", "Bulls v Ulster", "Tomorrow 07:45", "Ulster", "To Win", 75, DR + "Bulls_v_Ulster/9?event_id=609576", 609576)
disc("Rugby Union", "International", "Japan v Fiji", "Tomorrow 01:50", "Fiji", "To Win", 67, DR + "Japan_v_Fiji/9?event_id=609582", 609582)
disc("Rugby Union", "URC", "Stormers v Scarlets", "Tomorrow 10:00", "Scarlets", "To Win", None, DR + "Stormers_v_Scarlets/9?event_id=609580", 609580)

DC = OLBG + "/betting-tips/Cricket/All_Cricket/All_Events/"
disc("Cricket", "Australia domestic one-day", "Tasmania vs Victoria One Day Match", "Today 19:30", "Tasmania", "Win Match", 71, DC + "Tasmania_vs_Victoria_One_Day_Match/7?event_id=188839", 188839)
disc("Cricket", "New Zealand v India T20I", "New Zealand vs India 2nd T20 Match", "Tomorrow 03:00", "India", "Win Match", 80, DC + "New_Zealand_vs_India_2nd_T20_Match/7?event_id=188832", 188832)
disc("Cricket", "Australia domestic one-day", "Western Australia vs New South Wales One Day Match", "Tomorrow 02:00", "Western Australia", "Win Match", 75, DC + "Western_Australia_vs_New_South_Wales_One_Day_Match/7?event_id=188840", 188840)
disc("Cricket", "CSA T20 Challenge", "Lions vs Limpopo Impalas T20", "Tomorrow 07:00", "Lions", "Win Match", 100, DC + "Lions_vs_Limpopo_Impalas_T20/7?event_id=188841", 188841)
disc("Cricket", "CSA T20 Challenge", "Eastern Cape Iinyathi vs Warriors T20", "Tomorrow 07:00", "Warriors", "Win Match", 100, DC + "Eastern_Cape_Iinyathi_vs_Warriors_T20/7?event_id=188842", 188842)
disc("Cricket", "CSA T20 Challenge", "Knights vs Mpumalanga Rhinos T20", "Tomorrow 12:00", "Mpumalanga Rhinos", "Win Match", 100, DC + "Knights_vs_Mpumalanga_Rhinos_T20/7?event_id=188843", 188843)
disc("Cricket", "Pakistan v England ODI", "Pakistan vs England One Day Match", "25 Oct 04:00", "Pakistan", "Win Match", 100, DC + "Pakistan_vs_England_One_Day_Match/7?event_id=188838", 188838)

DV = OLBG + "/betting-tips/Volleyball/All_Volleyball/All_Events/"
disc("Volleyball", "Volleyball Bundesliga", "VOLLEY GOATS Mitteldeutschland vs Netzhoppers KW", "Today 13:30", "Netzhoppers KW", "Win Match", 86, DV + "VOLLEY_GOATS_Mitteldeutschland_vs_Netzhoppers_KW/21?event_id=37009", 37009)
disc("Volleyball", "Brazil Superliga W", "Brasilia W vs Sesc RJ Flamengo W", "Today 17:30", "Brasilia W", "Win Match", 56, DV + "Brasilia_W_vs_Sesc_RJ_Flamengo_W/21?event_id=37001", 37001)
disc("Volleyball", "Austria W", "ATSC Klagenfurt Women vs Linz Steg W", "Today 14:00", "Linz Steg W", "Win Match", 57, DV + "ATSC_Klagenfurt_Women_vs_Linz_Steg_W/21?event_id=37015", 37015)
disc("Volleyball", "Brazil Superliga W", "Minas W vs Paulistano-Barueri W", "Today 17:30", "Minas W", "Win Match", 67, DV + "Minas_W_vs_Paulistano-Barueri_W/21?event_id=37022", 37022)
disc("Volleyball", "Bulgaria", "Lokomotiv Avia vs Montana", "Today 12:30", "Lokomotiv Avia", "Win Match", 75, DV + "Lokomotiv_Avia_vs_Montana/21?event_id=37025", 37025)
disc("Volleyball", "PlusLiga", "PGE Skra Belchatow vs Projekt Warszawa", "Tomorrow 12:00", "Projekt Warszawa", "Win Match", 67, DV + "PGE_Skra_Belchatow_vs_Projekt_Warszawa/21?event_id=36964", 36964)
disc("Volleyball", "Brazil Superliga W", "Mackenzie W vs Osasco W", "Tomorrow 15:00", "Mackenzie W", "Win Match", 67, DV + "Mackenzie_W_vs_Osasco_W/21?event_id=37002", 37002)
disc("Volleyball", "Brazil Superliga W", "Abel-Moda Brusque W vs Praia Clube W", "Tomorrow 20:00", "Abel/Moda Brusque W", "Win Match", 100, DV + "Abel-Moda_Brusque_W_vs_Praia_Clube_W/21?event_id=37003", 37003)
disc("Volleyball", "SuperLega", "Trentino vs Cisterna", "25 Oct 12:00", "Cisterna", "Win Match", 100, DV + "Trentino_vs_Cisterna/21?event_id=36994", 36994)
disc("Volleyball", "SuperLega", "Perugia vs Pordenone", "25 Oct 13:00", "Pordenone", "Win Match", 100, DV + "Perugia_vs_Pordenone/21?event_id=36997", 36997)
disc("Volleyball", "PlusLiga", "CHKS Chelm vs Resovia Rzeszow", "25 Oct 13:00", "Resovia Rzeszow", "Win Match", 67, DV + "CHKS_Chelm_vs_Resovia_Rzeszow/21?event_id=36965", 36965)
disc("Volleyball", "Austria W", "SG Sokol-Post W vs TSV Hartberg W", "Tomorrow 10:30", "Sokol/Post W 3-1", "Set Score", 100, DV + "SG_Sokol-Post_W_vs_TSV_Hartberg_W/21?event_id=37017", 37017)
disc("Volleyball", "Austria", "UVC Ried vs VBK Klagenfurt", "Tomorrow 12:00", "UVC Ried", "Win Match", 100, DV + "UVC_Ried_vs_VBK_Klagenfurt/21?event_id=37031", 37031)
disc("Volleyball", "Czech W", "Sternberk W vs VK Lvice Praha W", "Tomorrow 12:00", "Sternberk W 3-1", "Set Score", 100, DV + "Sternberk_W_vs_VK_Lvice_Praha_W/21?event_id=37026", 37026)

DH = OLBG + "/betting-tips/Handball/All_Handball/All_Events/"
disc("Handball", "LNH Starligue", "Pays dAix UC vs Toulouse", "Today 14:00", "Toulouse", "Money Line", 44, DH + "Pays_dAix_UC_vs_Toulouse/20?event_id=12083", 12083)
disc("Handball", "HBL", "Frisch Auf Goppingen vs ThSV Eisenach", "Today 13:00", "Tie", "Money Line", 40, DH + "Frisch_Auf_Goppingen_vs_ThSV_Eisenach/20?event_id=12088", 12088)
disc("Handball", "Liga ASOBAL", "Bidasoa Irun vs Caserio Ciudad Real", "Today 13:00", "Bidasoa Irun", "Money Line", 50, DH + "Bidasoa_Irun_vs_Caserio_Ciudad_Real/20?event_id=12101", 12101)
disc("Handball", "LNH Starligue", "Limoges 87 vs Dunkerque", "Today 14:00", "Limoges 87", "Money Line", 40, DH + "Limoges_87_vs_Dunkerque/20?event_id=12080", 12080)
disc("Handball", "HBL", "TSV Hannover Burgdorf vs TBV Lemgo Lippe", "Today 14:00", "Tie", "Money Line", 46, DH + "TSV_Hannover_Burgdorf_vs_TBV_Lemgo_Lippe/20?event_id=12093", 12093)
disc("Handball", "SEHA/EHF", "GRK Ohrid vs Spor Toto SK", "Today 12:30", "Spor Toto +11.50", "Match Handicap", 100, DH + "GRK_Ohrid_vs_Spor_Toto_SK/20?event_id=12120", 12120)
disc("Handball", "LNH Starligue", "Chartres vs USAM Nimes", "Today 14:00", "Tie", "Money Line", 50, DH + "Chartres_vs_USAM_Nimes/20?event_id=12079", 12079)
disc("Handball", "Women international", "Estonia W vs Kosovo W", "Today 14:00", "Kosovo (W)", "Money Line", 45, DH + "Estonia_W_vs_Kosovo_W/20?event_id=12110", 12110)
disc("Handball", "Liga ASOBAL", "FC Barcelona vs Ciudad Encantada", "Today 13:00", "Ciudad Encantada +13.50", "Match Handicap", 80, DH + "FC_Barcelona_vs_Ciudad_Encantada/20?event_id=12121", 12121)
disc("Handball", "LNH Starligue", "Selestat Alsace vs Caen", "Today 14:30", "Caen", "Money Line", 50, DH + "Selestat_Alsace_vs_Caen/20?event_id=12085", 12085)
disc("Handball", "LNH Starligue", "Tremblay vs Cesson Rennes", "Today 14:30", "Cesson Rennes", "Money Line", 44, DH + "Tremblay_vs_Cesson_Rennes/20?event_id=12086", 12086)
disc("Handball", "Denmark Handboldligaen", "Skive FH vs Aalborg Handbold", "Tomorrow 09:00", "Aalborg Handbold", "Money Line", 50, DH + "Skive_FH_vs_Aalborg_Handbold/20?event_id=12076", 12076)
disc("Handball", "Denmark Handboldligaen", "Skjern Handbold vs Ribe Esbjerg HH", "Tomorrow 10:00", "Ribe Esbjerg HH", "Money Line", 67, DH + "Skjern_Handbold_vs_Ribe_Esbjerg_HH/20?event_id=12077", 12077)
disc("Handball", "Liga ASOBAL", "Villa De Aranda vs Puerto Sagunto", "Tomorrow 13:00", "Puerto Sagunto", "Money Line", 100, DH + "Villa_De_Aranda_vs_Puerto_Sagunto/20?event_id=12107", 12107)
disc("Handball", "HBL", "HC Erlangen vs THW Kiel", "Tomorrow 12:00", "HC Erlangen", "Money Line", None, DH + "HC_Erlangen_vs_THW_Kiel/20?event_id=12091", 12091)

DG = OLBG + "/betting-tips/Gaelic_Football/All_Gaelic_Football/All_Events/"
disc("Gaelic Sports", "Munster club football", "St Finbarrs v Nemo Rangers", "25 Oct 12:00", "Nemo Rangers +1.50", "Handicap", 78, DG + "St_Finbarrs_v_Nemo_Rangers/25?event_id=3530", 3530)
disc("Gaelic Sports", "Galway club football", "Moycullen v Salthill-Knocknacarra", "25 Oct 12:00", "Moycullen -3.50", "Handicap", 50, DG + "Moycullen_v_Salthill-Knocknacarra/25?event_id=3532", 3532)
disc("Gaelic Sports", "Cork club football", "Kanturk v Eire Og Cor", "01 Nov 09:00", "Kanturk", "Win Match", 57, DG + "Kanturk_v_Eire_Og_Cor/25?event_id=3531", 3531)
disc("Gaelic Sports", "Limerick club football", "Fr Caseys v Kildimo Pallaskenry", "01 Nov 10:30", "Fr Caseys", "Win Match", 100, DG + "Fr_Caseys_v_Kildimo_Pallaskenry/25?event_id=3537", 3537)

DHH = OLBG + "/betting-tips/Greyhounds/All_Greyhounds/All_Events/"
for _label, _when, _sel, _eid in [
    ("5:12 Towcester", "Today 12:12", "Choices Jean", 689803),
    ("5:18 Kinsley", "Today 12:18", "Grumpy Sandstorm", 689800),
    ("5:31 Towcester", "Today 12:31", "Mums Image", 689802),
    ("5:49 Towcester", "Today 12:49", "Trapstyle Sneezy", 689805),
    ("8:33 Romford", "Today 15:33", "Ontherun Jamie", 689846),
    ("9:13 Romford", "Today 16:13", "Grouchos Gregor", 689717),
    ("5:24 Newcastle", "Today 12:24", "Alnwick Tina", 689806),
    ("5:37 Kinsley", "Today 12:37", "Grumpy Jacko", 689804),
    ("5:43 Newcastle", "Today 12:43", "Dryland Velvet", 689798),
    ("5:51 Harlow", "Today 12:51", "Doreens Poppy", 689801),
    ("5:56 Kinsley", "Today 12:56", "Kellyseyenoone", 689807),
    ("6:02 Newcastle", "Today 13:02", "Mollys Aoibhe", 689808),
    ("6:08 Nottingham", "Today 13:08", "Honeygar Flow", 689810),
    ("6:11 Harlow", "Today 13:11", "Club Dream", 689811),
    ("6:18 Sheffield", "Today 13:18", "Jaykay Seven", 689816),
]:
    _slug = _label.replace(":", "").replace(" ", "_")
    disc("Greyhounds", "UK daily card", _label, _when, _sel, "Daily Races", 100,
         DHH + f"{_slug}/28?event_id={_eid}", _eid)

DM = OLBG + "/betting-tips/Motor_Racing/All_Motor_Racing/All_Events/"
disc("Motor Racing", "Formula 1", "USA Grand Prix", "25 Oct 16:00", "Max Verstappen", "Win Race", 34, DM + "USA_Grand_Prix/14?event_id=913", 913)
disc("Motor Racing", "Formula 1", "Formula 1 Drivers Championship 2026", "06 Dec 08:00", "Max Verstappen", "Win Tournament", 27, DM + "Formula_1_Drivers_Championship_2026/14?event_id=828", 828)

DRL = OLBG + "/betting-tips/Rugby_League/All_Rugby_League/All_Events/"
disc("Rugby League", "State of Origin", "State of Origin 2027", "27 May 2027 06:00", "New South Wales", "Win Tournament", 75, DRL + "State_of_Origin_2027/10?event_id=2695857", 2695857)
disc("Rugby League", "Super League", "Super League 2027", "02 Oct 2027 13:00", "Leeds Rhinos", "Grand Final Winner", 33, DRL + "Super_League_2027/10?event_id=2801554", 2801554)
disc("Rugby League", "NRL", "NRL 2027", "03 Oct 2027 04:30", "Penrith Panthers", "Grand Final Winner", 50, DRL + "NRL_2027/10?event_id=2801600", 2801600)

# ---------------------------------------------------------------------------
# 3. Verified fixtures and the inputs read for them
# ---------------------------------------------------------------------------
URC_RESULTS = {
    # round: [(home, away, hs, as)]
    1: [("Benetton", "Dragons", 19, 19), ("Connacht", "Stormers", 15, 29),
        ("Ulster", "Edinburgh", 29, 34), ("Lions", "Leinster", 27, 26),
        ("Sharks", "Ospreys", 41, 24), ("Munster", "Glasgow", 20, 26),
        ("Zebre", "Bulls", 13, 47), ("Scarlets", "Cardiff", 15, 21)],
    2: [("Cardiff", "Zebre", 40, 27), ("Edinburgh", "Stormers", 17, 13)],
    3: [("Glasgow", "Connacht", 36, 19), ("Dragons", "Ospreys", 31, 38),
        ("Bulls", "Lions", 57, 15), ("Stormers", "Sharks", 39, 22),
        ("Zebre", "Edinburgh", 12, 29), ("Scarlets", "Benetton", 27, 26),
        ("Ulster", "Munster", 26, 26), ("Leinster", "Cardiff", 29, 5)],
}

VERIFIED = [
    {
        "id": "BB-001", "sport": "Baseball", "competition": "MLB World Series, Game 1",
        "home": "Milwaukee Brewers", "away": "Tampa Bay Rays",
        "start_utc": "2026-10-24T00:00:00Z", "start_local": "Fri 23 Oct 20:00 ET",
        "venue": "American Family Field, Milwaukee", "olbg_id": 160789,
        "official_url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-10-23",
        "extra_urls": ["https://statsapi.mlb.com/api/v1/teams/158?season=2026&hydrate=standings",
                       "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsTypes=regularSeason"],
        "facts": [
            "gamePk 849805, gameType W, seriesDescription 'World Series', seriesGameNumber 1 of 7, ifNecessary N",
            "Milwaukee 103-59 (.636), 832 runs scored, 618 allowed, 55-26 at home, last ten 8-2, current streak W5",
            "Tampa Bay 98-64 (.605), 736 runs scored, 650 allowed, 43-38 away, last ten 5-5",
        ],
        "starters": None,
        "note": "Starting pitchers are not published in the schedule response, so the total is not pitcher-adjusted (F-7).",
    },
    {
        "id": "IH-001", "sport": "Ice Hockey", "competition": "NHL regular season",
        "home": "Chicago Blackhawks", "away": "Montréal Canadiens",
        "start_utc": "2026-10-24T00:00:00Z", "start_local": "Fri 23 Oct 20:00 ET",
        "venue": "United Center, Chicago", "olbg_id": 199984,
        "official_url": "https://api-web.nhle.com/v1/schedule/2026-10-23",
        "extra_urls": ["https://api-web.nhle.com/v1/standings/2026-10-23"],
        "facts": [
            "Game id 2026020166, startTimeUTC 2026-10-24T00:00:00Z, venue United Center, gameState FUT",
            "Montréal 9 GP, 4-3-2, 10 points, 30 goals for, 34 against, 1-1-1 on the road",
            "Chicago 9 GP, 3-6-0, 6 points, 21 goals for, 36 against, 3-2-0 at home",
            "League-published quotes: Montréal −170 (two providers), Chicago +138 / +142",
        ],
        "starters": None,
        "note": None,
    },
    {
        "id": "IH-002", "sport": "Ice Hockey", "competition": "NHL regular season",
        "home": "Colorado Avalanche", "away": "Tampa Bay Lightning",
        "start_utc": "2026-10-24T01:00:00Z", "start_local": "Fri 23 Oct 21:00 ET",
        "venue": "Ball Arena, Denver", "olbg_id": None,
        "official_url": "https://api-web.nhle.com/v1/schedule/2026-10-23",
        "extra_urls": ["https://api-web.nhle.com/v1/standings/2026-10-23"],
        "facts": [
            "Game id 2026020167, startTimeUTC 2026-10-24T01:00:00Z, venue Ball Arena, gameState FUT",
            "Tampa Bay 9 GP, 7-2-0, 14 points, 31 goals for, 23 against, 2-2-0 on the road, streak W3",
            "Colorado 10 GP, 5-4-1, 11 points, 41 goals for, 31 against, 3-1-0 at home, streak L2",
            "League-published quotes: Colorado −129 / −125, Tampa Bay +105",
        ],
        "starters": None,
        "note": "Our record-based estimate and the league's published quotes disagree by about 23 points on Tampa Bay (F-5).",
    },
    {
        "id": "BK-001", "sport": "Basketball", "competition": "NBA regular season",
        "home": "Milwaukee Bucks", "away": "Chicago Bulls",
        "start_utc": "2026-10-23T20:00:00Z", "start_local": "Fri 23 Oct 16:00 ET",
        "venue": None, "olbg_id": 536041,
        "official_url": "https://www.nba.com/games?date=2026-10-23",
        "extra_urls": [],
        "facts": ["Game 0022600099, 4:00 PM ET; Chicago 0-1, Milwaukee 0-1 on the season"],
        "starters": None,
        "note": "One game played; no team-specific verified strength input (F-6).",
    },
    {
        "id": "BK-002", "sport": "Basketball", "competition": "NBA regular season",
        "home": "Boston Celtics", "away": "New York Knicks",
        "start_utc": "2026-10-23T23:00:00Z", "start_local": "Fri 23 Oct 19:00 ET",
        "venue": None, "olbg_id": 534842,
        "official_url": "https://www.nba.com/games?date=2026-10-23",
        "extra_urls": [],
        "facts": ["Game 0022600008, 7:00 PM ET; New York 0-1, Boston 0-1"],
        "starters": None, "note": "One game played; prior-driven line (F-6).",
    },
    {
        "id": "BK-003", "sport": "Basketball", "competition": "NBA regular season",
        "home": "Washington Wizards", "away": "Toronto Raptors",
        "start_utc": "2026-10-23T23:00:00Z", "start_local": "Fri 23 Oct 19:00 ET",
        "venue": None, "olbg_id": 536034,
        "official_url": "https://www.nba.com/games?date=2026-10-23",
        "extra_urls": [],
        "facts": ["Game 0022600097, 7:00 PM ET; Toronto 1-0, Washington 1-0"],
        "starters": None, "note": "One game played; prior-driven line (F-6).",
    },
    {
        "id": "BK-004", "sport": "Basketball", "competition": "NBA regular season",
        "home": "Charlotte Hornets", "away": "Atlanta Hawks",
        "start_utc": "2026-10-23T23:00:00Z", "start_local": "Fri 23 Oct 19:00 ET",
        "venue": None, "olbg_id": 536035,
        "official_url": "https://www.nba.com/games?date=2026-10-23",
        "extra_urls": [],
        "facts": ["Game 0022600094, 7:00 PM ET; Atlanta 1-0, Charlotte 1-0"],
        "starters": None, "note": "One game played; prior-driven line (F-6).",
    },
    {
        "id": "BK-005", "sport": "Basketball", "competition": "NBA regular season",
        "home": "Orlando Magic", "away": "Minnesota Timberwolves",
        "start_utc": "2026-10-23T23:00:00Z", "start_local": "Fri 23 Oct 19:00 ET",
        "venue": None, "olbg_id": 536036,
        "official_url": "https://www.nba.com/games?date=2026-10-23",
        "extra_urls": [],
        "facts": ["Game 0022600096, 7:00 PM ET; Minnesota 1-0, Orlando 0-1"],
        "starters": None, "note": "One game played; prior-driven line (F-6).",
    },
    {
        "id": "BK-006", "sport": "Basketball", "competition": "NBA regular season",
        "home": "Indiana Pacers", "away": "Dallas Mavericks",
        "start_utc": "2026-10-23T23:00:00Z", "start_local": "Fri 23 Oct 19:00 ET",
        "venue": None, "olbg_id": 536037,
        "official_url": "https://www.nba.com/games?date=2026-10-23",
        "extra_urls": [],
        "facts": ["Game 0022600095, 7:00 PM ET; Dallas 0-1, Indiana 1-0"],
        "starters": None, "note": "One game played; prior-driven line (F-6).",
    },
    {
        "id": "BK-007", "sport": "Basketball", "competition": "NBA regular season",
        "home": "Miami Heat", "away": "Detroit Pistons",
        "start_utc": "2026-10-24T00:00:00Z", "start_local": "Fri 23 Oct 20:00 ET",
        "venue": None, "olbg_id": 536038,
        "official_url": "https://www.nba.com/games?date=2026-10-23",
        "extra_urls": [],
        "facts": ["Game 0022600098, 8:00 PM ET; Detroit 1-0, Miami 0-1"],
        "starters": None, "note": "One game played; prior-driven line (F-6).",
    },
    {
        "id": "BK-008", "sport": "Basketball", "competition": "NBA regular season",
        "home": "San Antonio Spurs", "away": "Houston Rockets",
        "start_utc": "2026-10-24T01:30:00Z", "start_local": "Fri 23 Oct 21:30 ET",
        "venue": None, "olbg_id": 534841,
        "official_url": "https://www.nba.com/games?date=2026-10-23",
        "extra_urls": [],
        "facts": ["Game 0022600009, 9:30 PM ET; Houston 1-0, San Antonio 0-1"],
        "starters": None, "note": "One game played; prior-driven line (F-6).",
    },
    {
        "id": "BK-009", "sport": "Basketball", "competition": "NBA regular season",
        "home": "Utah Jazz", "away": "New Orleans Pelicans",
        "start_utc": "2026-10-24T01:30:00Z", "start_local": "Fri 23 Oct 21:30 ET",
        "venue": None, "olbg_id": 536040,
        "official_url": "https://www.nba.com/games?date=2026-10-23",
        "extra_urls": [],
        "facts": ["Game 0022600100, 9:30 PM ET; New Orleans 0-1, Utah 0-1"],
        "starters": None, "note": "One game played; prior-driven line (F-6).",
    },
    {
        "id": "BK-010", "sport": "Basketball", "competition": "NBA regular season",
        "home": "Golden State Warriors", "away": "Memphis Grizzlies",
        "start_utc": "2026-10-24T02:00:00Z", "start_local": "Fri 23 Oct 22:00 ET",
        "venue": None, "olbg_id": None,
        "official_url": "https://www.nba.com/games?date=2026-10-23",
        "extra_urls": [],
        "facts": ["Game 0022600101, 10:00 PM ET; Memphis 1-0, Golden State 0-1"],
        "starters": None, "note": "One game played; prior-driven line (F-6).",
    },
    {
        "id": "BK-011", "sport": "Basketball", "competition": "NBA regular season",
        "home": "Los Angeles Lakers", "away": "Los Angeles Clippers",
        "start_utc": "2026-10-24T02:00:00Z", "start_local": "Fri 23 Oct 22:00 ET",
        "venue": None, "olbg_id": 536042,
        "official_url": "https://www.nba.com/games?date=2026-10-23",
        "extra_urls": [],
        "facts": ["Game 0022600102, 10:00 PM ET; Clippers 1-0, Lakers 1-0"],
        "starters": None, "note": "One game played; prior-driven line (F-6).",
    },
    {
        "id": "BK-012", "sport": "Basketball", "competition": "NBA regular season",
        "home": "Sacramento Kings", "away": "Portland Trail Blazers",
        "start_utc": "2026-10-24T02:00:00Z", "start_local": "Fri 23 Oct 22:00 ET",
        "venue": None, "olbg_id": 536043,
        "official_url": "https://www.nba.com/games?date=2026-10-23",
        "extra_urls": [],
        "facts": ["Game 0022600103, 10:00 PM ET; Portland 1-0, Sacramento 0-1"],
        "starters": None, "note": "One game played; prior-driven line (F-6).",
    },
    {
        "id": "RU-001", "sport": "Rugby Union", "competition": "United Rugby Championship, Round 4",
        "home": "Cardiff Rugby", "away": "Hollywoodbets Sharks",
        "start_utc": None, "start_local": "Fri 23 Oct 14:45 (URC local)",
        "venue": "Cardiff Arms Park", "olbg_id": 609575,
        "official_url": "https://stats.unitedrugby.com/match-centre/2026-27/4",
        "extra_urls": ["https://stats.unitedrugby.com/match-centre/2026-27/1",
                       "https://stats.unitedrugby.com/match-centre/2026-27/2"],
        "facts": ["Round 4 fixture listed by URC: Cardiff v Hollywoodbets Sharks, Cardiff Arms Park",
                  "Cardiff R3: lost 5-29 at Leinster; R2: beat Zebre 40-27; R1: won 21-15 at Scarlets",
                  "Sharks R3: lost 22-39 at Stormers; R1: beat Ospreys 41-24"],
        "starters": None, "note": "URC publishes local kick-off time only; no UTC offset was printed (F-16).",
    },
    {
        "id": "RU-002", "sport": "Rugby Union", "competition": "United Rugby Championship, Round 4",
        "home": "Connacht", "away": "Zebre Parma",
        "start_utc": None, "start_local": "Fri 23 Oct 14:45 (URC local)",
        "venue": "Dexcom Stadium", "olbg_id": 609577,
        "official_url": "https://stats.unitedrugby.com/match-centre/2026-27/4",
        "extra_urls": ["https://stats.unitedrugby.com/match-centre/2026-27/1"],
        "facts": ["Round 4 fixture listed by URC: Connacht v Zebre Parma, Dexcom Stadium",
                  "Connacht R3: lost 19-36 at Glasgow; R1: lost 15-29 at home to Stormers",
                  "Zebre R3: lost 12-29 at home to Edinburgh; R2: lost 27-40 at Cardiff; R1: lost 13-47 at home to Bulls"],
        "starters": None, "note": None,
    },
    {
        "id": "RU-003", "sport": "Rugby Union", "competition": "United Rugby Championship, Round 4",
        "home": "Edinburgh Rugby", "away": "10bet Lions",
        "start_utc": None, "start_local": "Fri 23 Oct 14:45 (URC local)",
        "venue": "Hive Stadium", "olbg_id": 609579,
        "official_url": "https://stats.unitedrugby.com/match-centre/2026-27/4",
        "extra_urls": ["https://stats.unitedrugby.com/match-centre/2026-27/1",
                       "https://stats.unitedrugby.com/match-centre/2026-27/2",
                       "https://stats.unitedrugby.com/match-centre/2026-27/4"],
        "facts": ["Round 4 fixture listed by URC: Edinburgh v 10bet Lions, Hive Stadium",
                  "Edinburgh R1: won 34-29 at Ulster; R2: beat Stormers 17-13; R3: won 29-12 at Zebre (three wins from three)",
                  "Lions R3: lost 15-57 at Bulls; R1: beat Leinster 27-26"],
        "starters": None, "note": None,
    },
    {
        "id": "RU-004", "sport": "Rugby Union", "competition": "United Rugby Championship, Round 4",
        "home": "Vodacom Bulls", "away": "Ulster",
        "start_utc": None, "start_local": "Sat 24 Oct 07:45 (OLBG render)",
        "venue": "Loftus Versfeld", "olbg_id": 609576,
        "official_url": "https://stats.unitedrugby.com/match-centre/2026-27/4",
        "extra_urls": ["https://stats.unitedrugby.com/match-centre/2026-27/1"],
        "facts": ["Bulls R1: won 47-13 at Zebre; R3: beat Lions 57-15 at Loftus Versfeld",
                  "Ulster R1: lost 29-34 at home to Edinburgh; R3: drew 26-26 at home with Munster"],
        "starters": None, "note": "Fixture time taken from the OLBG render; URC Round 4 listing read for Round 4 did not expose Saturday kick-off text in the captured portion.",
    },
    {
        "id": "RU-005", "sport": "Rugby Union", "competition": "United Rugby Championship, Round 4",
        "home": "DHL Stormers", "away": "Scarlets",
        "start_utc": None, "start_local": "Sat 24 Oct 10:00 (OLBG render)",
        "venue": "DHL Stadium", "olbg_id": 609580,
        "official_url": "https://stats.unitedrugby.com/match-centre/2026-27/4",
        "extra_urls": ["https://stats.unitedrugby.com/match-centre/2026-27/1",
                       "https://stats.unitedrugby.com/match-centre/2026-27/2"],
        "facts": ["Stormers R1: won 29-15 at Connacht; R2: lost 13-17 at Edinburgh; R3: beat Sharks 39-22 at DHL Stadium",
                  "Scarlets R1: lost 15-21 at home to Cardiff; R3: beat Benetton 27-26 at Parc y Scarlets"],
        "starters": None, "note": None,
    },
    {
        "id": "SN-001", "sport": "Snooker", "competition": "BetVictor Northern Ireland Open 2026, quarter-final",
        "home": "Jak Jones", "away": "Scott Donaldson",
        "start_utc": None, "start_local": "Fri 23 Oct 14:00 (WST render)",
        "venue": None, "olbg_id": 9951,
        "official_url": "https://www.wst.tv/matches/",
        "extra_urls": ["https://www.wst.tv/rankings/"],
        "facts": ["Match 60, quarter-final, Fri 23 Oct 14:00, scheduled",
                  "Jones beat Daniel Wells 4-2 in the round of 16",
                  "Donaldson beat Jordan Brown 4-2 in the round of 16 and Noppon Saengkham 4-1 in the round of 32",
                  "Jones is fourth on the WST one-year list (£141,000)"],
        "starters": None, "note": "No head-to-head strength input is published, so no price was originated (F-8).",
    },
    {
        "id": "SN-002", "sport": "Snooker", "competition": "BetVictor Northern Ireland Open 2026, quarter-final",
        "home": "David Gilbert", "away": "Mark Williams",
        "start_utc": None, "start_local": "Fri 23 Oct 14:00 (WST render)",
        "venue": None, "olbg_id": 9950,
        "official_url": "https://www.wst.tv/matches/",
        "extra_urls": ["https://www.wst.tv/rankings/"],
        "facts": ["Match 59, quarter-final, Fri 23 Oct 14:00, scheduled",
                  "Gilbert beat Ka Wai Cheung 4-2 in the round of 16 and Gao Yang 4-3 in the round of 32",
                  "Williams beat Martin O'Donnell 4-0 in the round of 16 and Zhang Anda 4-2 in the round of 32",
                  "Williams is world no. 8 (£747,400); Gilbert is eleventh on the one-year list (£73,250)"],
        "starters": None, "note": "No head-to-head strength input is published, so no price was originated (F-8).",
    },
    {
        "id": "MR-001", "sport": "Motor Racing", "competition": "Formula 1, United States Grand Prix",
        "home": "United States Grand Prix", "away": "56-lap race, Circuit of the Americas",
        "start_utc": "2026-10-25T21:00:00Z", "start_local": "Sun 25 Oct 16:00 track time",
        "venue": "Circuit of the Americas, Austin", "olbg_id": 913,
        "official_url": "https://www.formula1.com/en/racing/2026/united-states",
        "extra_urls": [],
        "facts": ["Race Sunday 25 October, 16:00 track time; 56 laps; 5.513 km lap; 308.432 km race distance",
                  "Practice 1 Friday 13:30-14:30 and Practice 2 17:00-18:00 track time",
                  "Qualifying Saturday 17:00-18:00 track time"],
        "starters": None,
        "note": "OLBG offers an outright race-winner market only; no head-to-head or handicap market was listed, so no price was originated (F-14). Track time converted to 21:00Z because COTA is UTC-5 during the race weekend.",
    },
]

# ---------------------------------------------------------------------------
# 4. Line origination inputs — only values read above
# ---------------------------------------------------------------------------
MLB = {"TB": {"w": 98, "l": 64, "rs": 736, "ra": 650},
       "MIL": {"w": 103, "l": 59, "rs": 832, "ra": 618}}
NHL = {
    "MTL": {"gp": 9, "w": 4, "l": 5, "gf": 30, "ga": 34},
    "CHI": {"gp": 9, "w": 3, "l": 6, "gf": 21, "ga": 36},
    "TBL": {"gp": 9, "w": 7, "l": 2, "gf": 31, "ga": 23},
    "COL": {"gp": 10, "w": 5, "l": 5, "gf": 41, "ga": 31},
}
NBA_GAMES = [
    ("BK-001", "Milwaukee Bucks", "Chicago Bulls", "0022600099"),
    ("BK-002", "Boston Celtics", "New York Knicks", "0022600008"),
    ("BK-003", "Washington Wizards", "Toronto Raptors", "0022600097"),
    ("BK-004", "Charlotte Hornets", "Atlanta Hawks", "0022600094"),
    ("BK-005", "Orlando Magic", "Minnesota Timberwolves", "0022600096"),
    ("BK-006", "Indiana Pacers", "Dallas Mavericks", "0022600095"),
    ("BK-007", "Miami Heat", "Detroit Pistons", "0022600098"),
    ("BK-008", "San Antonio Spurs", "Houston Rockets", "0022600009"),
    ("BK-009", "Utah Jazz", "New Orleans Pelicans", "0022600100"),
    ("BK-010", "Golden State Warriors", "Memphis Grizzlies", "0022600101"),
    ("BK-011", "Los Angeles Lakers", "LA Clippers", "0022600102"),
    ("BK-012", "Sacramento Kings", "Portland Trail Blazers", "0022600103"),
]

# ---------------------------------------------------------------------------
# 5. Predictions (High and the strongest Medium selections)
# ---------------------------------------------------------------------------
PREDICTIONS = [
    {
        "fixture_id": "RU-003", "confidence": "High",
        "selection": "Edinburgh Rugby to win the match",
        "price": "−376 (1.266)", "probability": 0.7915,
        "words_target": 30,
        "body": (
            "Edinburgh have won all three opening rounds of the United Rugby Championship, "
            "beating Ulster 34-29 away, DHL Stormers 17-13 at Hive Stadium and Zebre Parma 29-12 in Parma. "
            "The Lions arrive after shipping 57 points at Loftus Versfeld in a 57-15 defeat to Vodacom Bulls, "
            "conceding 57 points in that match. Back Edinburgh to win the match at home on Friday."
        ),
    },
    {
        "fixture_id": "RU-004", "confidence": "High",
        "selection": "Vodacom Bulls to win the match",
        "price": "−567 (1.176)", "probability": 0.8503,
        "words_target": 30,
        "body": (
            "Vodacom Bulls have scored 104 points across two completed rounds, beating Zebre Parma 47-13 in Parma "
            "and thrashing the Lions 57-15 at Loftus Versfeld. Ulster drew 26-26 at home with Munster in round three "
            "but lost 34-29 at home to Edinburgh in round one, and now face a Bulls pack that has conceded only 28 points. "
            "The selection is Vodacom Bulls to win the match."
        ),
    },
    {
        "fixture_id": "RU-002", "confidence": "Medium",
        "selection": "Connacht to win the match",
        "price": "−163 (1.613)", "probability": 0.6200,
        "words_target": 30,
        "body": (
            "Zebre Parma have lost all three completed United Rugby Championship rounds, conceding 47 points at home "
            "to Vodacom Bulls, 40 at Cardiff and 29 at home to Edinburgh. Connacht have started badly too, losing 15-29 "
            "at home to DHL Stormers and 19-36 at Glasgow, but they return to Dexcom Stadium against a side that has conceded "
            "116 points across those three rounds. The pick is Connacht to win the match."
        ),
    },
    {
        "fixture_id": "RU-005", "confidence": "Medium",
        "selection": "DHL Stormers to win the match",
        "price": "−177 (1.565)", "probability": 0.6391,
        "words_target": 30,
        "body": (
            "DHL Stormers opened with a 29-15 win at Connacht and beat Hollywoodbets Sharks 39-22 at DHL Stadium in round three, "
            "their only defeat a 17-13 loss at Edinburgh. Scarlets have one win from their completed matches, edging Benetton 27-26 "
            "in Llanelli after losing 21-15 at home to Cardiff. DHL Stormers to win the match is the selection."
        ),
    },
    {
        "fixture_id": "IH-002", "confidence": "Medium",
        "selection": "Tampa Bay Lightning to win the match",
        "price": "−225 (1.444)", "probability": 0.6923,
        "words_target": 30,
        "body": (
            "Tampa Bay Lightning are 7-2-0 through nine games with 31 goals scored and 23 conceded, and carry a three-game "
            "winning streak into Colorado. Colorado Avalanche are 5-4-1 with 41 goals for and 31 against, and have lost their "
            "last two. The league's own published quotes make Colorado a −129 favourite, so this is a deliberately contrarian "
            "call against the market. Selection: Tampa Bay Lightning to win the match."
        ),
    },
]

# ---------------------------------------------------------------------------
# 6. Irregularities / flagged items
# ---------------------------------------------------------------------------
FLAGS = [
    {"id": "F-1", "severity": "high", "area": "Golf",
     "detail": "The OLBG golf hub returned 'No tips found' at 16:25Z, so zero golf fixtures were discovered for today. "
               "That is an OLBG suppression behaviour (no open community tips), not evidence that no golf is being played.",
     "source": "https://www.olbg.com/betting-tips/Golf/5"},
    {"id": "F-2", "severity": "high", "area": "Rugby League",
     "detail": "The rugby league hub listed only 2027 outright markets (State of Origin, Super League, NRL). No match "
               "fixture was available, so the sport has no analysable events in this window.",
     "source": "https://www.olbg.com/betting-tips/Rugby_League/10"},
    {"id": "F-3", "severity": "high", "area": "OLBG clock",
     "detail": "Greyhound card times are rendered five hours behind the UK race times printed in the same row "
               "(e.g. '5:12 Towcester' shown as 'Today 12:12'), while URC and snooker rows show local European times. "
               "The hub prints no timezone, so no UTC start was derived for those rows.",
     "source": "https://www.olbg.com/betting-tips/Greyhounds/28"},
    {"id": "F-4", "severity": "high", "area": "Coverage",
     "detail": "Fixtures were confirmed against an official publisher for five sports only (baseball, ice hockey, "
               "basketball, rugby union, snooker) plus the motor-racing schedule. Tennis, cricket, darts, handball, "
               "volleyball, greyhounds, golf, Gaelic games and rugby league rows are discovery-only and every official "
               "field is blank.",
     "source": "https://www.olbg.com/betting-tips"},
    {"id": "F-5", "severity": "high", "area": "Ice hockey",
     "detail": "On Tampa Bay @ Colorado our record-based estimate gives Tampa Bay 69.2% while the league's published, "
               "de-vigged quotes imply 46.4% — a 22.8-point disagreement. Both readings are published; neither is "
               "treated as the truth.",
     "source": "https://api-web.nhle.com/v1/schedule/2026-10-23"},
    {"id": "F-6", "severity": "high", "area": "Basketball",
     "detail": "Every NBA team has played one game. No team-specific strength input exists yet, so NBA prices use a "
               "single disclosed league-average home prior (0.55) and are labelled Low. They are placeholders, not "
               "team reads.",
     "source": "https://www.nba.com/games?date=2026-10-23"},
    {"id": "F-7", "severity": "medium", "area": "Baseball",
     "detail": "Starting pitchers are not published in the MLB schedule response, so the World Series total is not "
               "pitcher-adjusted and should not be compared with a bookmaker total.",
     "source": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-10-23"},
    {"id": "F-8", "severity": "medium", "area": "Snooker",
     "detail": "Both Northern Ireland Open quarter-finals have verified fixture details and verified results, but no "
               "published head-to-head strength input, so no price was originated. WST prize-money rankings were read "
               "and are shown as context only.",
     "source": "https://www.wst.tv/rankings/"},
    {"id": "F-9", "severity": "medium", "area": "Gaelic Sports",
     "detail": "The Munster GAA fixture list was read, but the OLBG club fixtures (St Finbarrs v Nemo Rangers, "
               "Moycullen v Salthill-Knocknacarra, both 25 Oct) were not located in the page portion read. They stay "
               "unverified and no price was originated.",
     "source": "https://munster.gaa.ie/fixtures-results/"},
    {"id": "F-10", "severity": "medium", "area": "Darts",
     "detail": "pdc.tv served a cookie-consent shell with no schedule content, so all 12 darts fixtures on the OLBG hub "
               "remain unverified against the governing body. No price was originated.",
     "source": "https://www.pdc.tv/tournaments/machineseeker-european-championship"},
    {"id": "F-11", "severity": "medium", "area": "Tennis",
     "detail": "atptour.com returned navigation and footer only (client-rendered scores), so the nine OLBG tennis "
               "fixtures remain unverified. No price was originated.",
     "source": "https://www.atptour.com/en/scores/current/view-all"},
    {"id": "F-12", "severity": "medium", "area": "Greyhounds",
     "detail": "gbgb.org.uk/race-card/ returned HTTP 404, so no runner, trap or going data could be confirmed for the "
               "15 discovered races.",
     "source": "https://www.gbgb.org.uk/race-card/"},
    {"id": "F-13", "severity": "high", "area": "Confidence band",
     "detail": "The brief's two rules do not overlap much: a price inside −250…+10000 implies a probability of at most "
               "71.4%, while High requires at least 70%. That leaves a 1.4-point window. This desk enforces both rules "
               "literally, so 0 selections qualify in-band and 2 High selections are published out-of-band in a "
               "disclosed ledger.",
     "source": "https://www.olbg.com/betting-tips"},
    {"id": "F-14", "severity": "medium", "area": "Motor Racing",
     "detail": "OLBG lists only an outright race-winner market for the United States Grand Prix. With a 20-driver field "
               "no single runner reaches 70%, and there is no head-to-head or handicap market to price.",
     "source": "https://www.olbg.com/betting-tips/Motor_Racing/14"},
    {"id": "F-15", "severity": "low", "area": "Baseball",
     "detail": "OLBG renders the World Series opener as 'Today 20:00'. MLB's own feed gives 2026-10-24T00:00:00Z, which "
               "is 20:00 ET on 23 October. Both are consistent; the UTC date differs from the US local date.",
     "source": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-10-23"},
    {"id": "F-16", "severity": "medium", "area": "Rugby Union",
     "detail": "The URC match centre states 'All times shown are Local' without publishing an offset, so no UTC start "
               "was derived for the five URC fixtures. OLBG's rendered times are recorded separately.",
     "source": "https://stats.unitedrugby.com/match-centre/2026-27/4"},
    {"id": "F-17", "severity": "low", "area": "Rugby Union",
     "detail": "Only two Round 2 scorelines were captured before the page response was truncated, so form margins for "
               "Cardiff, Sharks, Connacht, Zebre, Edinburgh, Lions, Bulls, Ulster, Stormers and Scarlets are computed "
               "from the matches actually read, with the sample size printed beside each price.",
     "source": "https://stats.unitedrugby.com/match-centre/2026-27/2"},
]
