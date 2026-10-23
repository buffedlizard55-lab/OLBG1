"""Session cf2699ba-olbg1 — data layer for the 2026-10-23 desk.

Every value in this module was either
  (a) read verbatim from an official page fetched this session (see SOURCES), or
  (b) read verbatim from the OLBG public hub list, which is DISCOVERY ONLY and is
      never treated as a fact about a fixture.

Nothing is inferred. Where an official page did not supply a value the value is
None and the row is flagged in flagged.json.
"""
import json
import os

OBS = "2026-10-23T16:17Z/2026-10-23T16:40Z"   # whole-session observation window
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "cf2699ba")

SPORTS = [
    {"key": "golf", "name": "Golf", "olbg_slug": "Golf", "olbg_id": 5},
    {"key": "volleyball", "name": "Volleyball", "olbg_slug": "Volleyball", "olbg_id": 21},
    {"key": "rugby-union", "name": "Rugby Union", "olbg_slug": "Rugby_Union", "olbg_id": 9},
    {"key": "cricket", "name": "Cricket", "olbg_slug": "Cricket", "olbg_id": 7},
    {"key": "snooker", "name": "Snooker", "olbg_slug": "Snooker", "olbg_id": 8},
    {"key": "darts", "name": "Darts", "olbg_slug": "Darts", "olbg_id": 15},
    {"key": "baseball", "name": "Baseball", "olbg_slug": "Baseball", "olbg_id": 12},
    {"key": "gaelic-sports", "name": "Gaelic Sports", "olbg_slug": "Gaelic_Football", "olbg_id": 25},
    {"key": "greyhounds", "name": "Greyhounds", "olbg_slug": "Greyhounds", "olbg_id": 28},
    {"key": "tennis", "name": "Tennis", "olbg_slug": "Tennis", "olbg_id": 3},
    {"key": "motor-racing", "name": "Motor Racing", "olbg_slug": "Motor_Racing", "olbg_id": 14},
    {"key": "handball", "name": "Handball", "olbg_slug": "Handball", "olbg_id": 20},
    {"key": "ice-hockey", "name": "Ice Hockey", "olbg_slug": "Ice_Hockey", "olbg_id": 13},
    {"key": "basketball", "name": "Basketball", "olbg_slug": "Basketball", "olbg_id": 4},
    {"key": "rugby-league", "name": "Rugby League", "olbg_slug": "Rugby_League", "olbg_id": 10},
]

SOURCES = [
    {
        "id": "src-olbg-hubs",
        "org": "OLBG.com (discovery only — not a source of fact)",
        "url": "https://www.olbg.com/betting-tips/",
        "observed": "2026-10-23T16:19Z/2026-10-23T16:37Z",
        "method": "Arena page-fetch; chunk 0 (server-rendered top list) of each of the 15 in-scope hub pages",
        "role": "discovery",
        "note": "Top-list only. 'Load More Tips' pagination is XHR and was not captured. "
                "Times carry no timezone label and were proven inconsistent within the same page "
                "(see F-CF-01). Tip counts are community votes, not probabilities.",
    },
    {
        "id": "src-nhl-schedule",
        "org": "National Hockey League",
        "url": "https://api-web.nhle.com/v1/schedule/2026-10-23",
        "observed": "2026-10-23T16:24Z",
        "method": "Arena page-fetch, chunk 0 (JSON)",
        "role": "official",
        "note": "numberOfGames=2: 2026020166 MTL@CHI 2026-10-24T00:00:00Z United Center; "
                "2026020167 TBL@COL 2026-10-24T01:00:00Z Ball Arena. Both gameState=FUT, "
                "gameScheduleState=OK. Embedded per-provider odds arrays read verbatim.",
    },
    {
        "id": "src-nhl-standings",
        "org": "National Hockey League",
        "url": "https://api-web.nhle.com/v1/standings/2026-10-23",
        "observed": "2026-10-23T16:26Z",
        "method": "Arena page-fetch, chunk 0 (JSON); standingsDateTimeUtc=2026-10-23T16:17:45Z",
        "role": "official",
        "note": "Only the clubs appearing in chunk 0 were read (CAR 8-2-2 18pts, EDM 8-1-1 17pts, "
                "BOS 8-2-1 17pts, VGK 8-4-0 16pts). None of them play tonight; therefore NO "
                "club-level form is available for MTL, CHI, TBL or COL and none is asserted.",
    },
    {
        "id": "src-mlb-schedule",
        "org": "Major League Baseball",
        "url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-23&endDate=2026-10-25&hydrate=probablePitcher,team,venue,seriesStatus",
        "observed": "2026-10-23T16:27Z",
        "method": "Arena page-fetch, chunk 0 (JSON)",
        "role": "official",
        "note": "World Series Game 1 gamePk 849805, TB @ MIL, gameDate 2026-10-24T00:00:00Z, "
                "officialDate 2026-10-23, American Family Field, probable pitchers Nick Martinez (TB) "
                "and Jacob Misiorowski (MIL), ifNecessary=N, series 1 of 7. Game 2 gamePk 849802 "
                "2026-10-25T00:00:00Z, Rasmussen (TB) v Logan Henderson (MIL).",
    },
    {
        "id": "src-mlb-standings-nl",
        "org": "Major League Baseball",
        "url": "https://statsapi.mlb.com/api/v1/standings?leagueId=104&season=2026&standingsTypes=regularSeason",
        "observed": "2026-10-23T16:38Z",
        "method": "Arena page-fetch, chunk 0 (JSON). NL East clubs only in chunk 0.",
        "role": "official",
        "note": "Read but NOT usable: the Brewers (NL Central) do not appear in chunk 0, so no "
                "fresh Milwaukee record was obtained this session. Recorded for transparency.",
    },
    {
        "id": "src-mlb-standings-al",
        "org": "Major League Baseball",
        "url": "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsTypes=regularSeason",
        "observed": "2026-10-23T16:29Z",
        "method": "Arena page-fetch, chunk 0 (JSON)",
        "role": "official",
        "note": "Fresh confirmation of Tampa Bay: 98-64 (.605), home 55-26, away 43-38, "
                "RS 736 / RA 650, lastTen 5-5, streak L1, division rank 1.",
    },
    {
        "id": "src-mlb-records-capture",
        "org": "Major League Baseball (in-repo canonical capture, 2026-10-22)",
        "url": "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsTypes=regularSeason&fields=records,teamRecords,team,id,name,wins,losses,runsScored,runsAllowed,gamesPlayed,league,id,division",
        "observed": "2026-10-22T07:17:40Z/2026-10-22T07:30:30Z (captured in data/current/evidence/mlb-records-2026.json)",
        "method": "Repo canonical evidence file, read this session; original capture by the canonical pipeline",
        "role": "official-capture",
        "note": "Milwaukee: 103-59, RS 832 / RA 618, 162 games, 2026 regular season. Used because the "
                "live standings endpoint returned NL East in chunk 0 only. Observation is one day old "
                "and the season is complete, so the value cannot have changed.",
    },
    {
        "id": "src-urc-round4",
        "org": "United Rugby Championship",
        "url": "https://stats.unitedrugby.com/match-centre/2026-27/4",
        "observed": "2026-10-23T16:31Z",
        "method": "Arena page-fetch, chunk 0",
        "role": "official",
        "note": "Round 4, Friday 23 October 2026: Cardiff v Hollywoodbets Sharks 14:45 Cardiff Arms Park; "
                "Connacht v Zebre Parma 14:45 Dexcom Stadium; Edinburgh v 10bet Lions 14:45 Hive Stadium. "
                "Page states 'All times shown are Local'. Round 3 results also present and used as form.",
    },
    {
        "id": "src-f1-usgp",
        "org": "Formula 1",
        "url": "https://www.formula1.com/en/racing/2026/united-states",
        "observed": "2026-10-23T16:30Z",
        "method": "Arena page-fetch, chunk 0",
        "role": "official",
        "note": "United States Grand Prix 2026 at Circuit of The Americas: Practice 1 23 Oct 13:30-14:30, "
                "Practice 2 23 Oct 17:00-18:00 (track time), Qualifying 24 Oct 17:00, Race 25 Oct 16:00. "
                "Circuit 5.513 km, 56 laps, race distance 308.432 km.",
    },
    {
        "id": "src-wst-matches",
        "org": "World Snooker Tour",
        "url": "https://www.wst.tv/matches/",
        "observed": "2026-10-23T16:34Z",
        "method": "Arena page-fetch, chunk 0",
        "role": "official",
        "note": "BetVictor Northern Ireland Open 2026 match list. Chunk 0 covers 18-19 October only; "
                "it confirms Round 1 results (Scott Donaldson 4-0 Wu Yize, David Gilbert 4-1 Oliver Sykes) "
                "but does NOT reach the 23 October session, so today's two fixtures are NOT verified.",
    },
    {
        "id": "src-cricket-au",
        "org": "Cricket Australia",
        "url": "https://www.cricket.com.au/matches?year=2026&isCompleted=0",
        "observed": "2026-10-23T16:35Z",
        "method": "Arena page-fetch, chunk 0",
        "role": "official",
        "note": "Series and team filter lists only; no dated fixture rows in chunk 0. No cricket fixture verified.",
    },
    {
        "id": "src-euroleague-gc",
        "org": "Euroleague Basketball",
        "url": "https://www.euroleaguebasketball.net/en/euroleague/game-center/",
        "observed": "2026-10-23T16:28Z",
        "method": "Arena page-fetch, chunk 0",
        "role": "official",
        "note": "Club list only; the fixture grid is client-rendered. No EuroLeague fixture verified.",
    },
    {
        "id": "src-pdc",
        "org": "Professional Darts Corporation",
        "url": "https://www.pdc.tv/tournament/2026-cazoo-european-championship",
        "observed": "2026-10-23T16:32Z",
        "method": "Arena page-fetch, chunk 0",
        "role": "official",
        "note": "Consent wall only; no match content returned. No darts fixture verified. "
                "Same barrier recorded by session 8f6d7364 on 2026-10-22 (F-8F6D-03).",
    },
    {
        "id": "src-munster-gaa",
        "org": "Munster GAA",
        "url": "https://munster.gaa.ie/fixtures/",
        "observed": "2026-10-23T16:33Z",
        "method": "Arena page-fetch, chunk 0",
        "role": "official",
        "note": "Index page only; fixture detail sits behind club-championship sub-pages that were not "
                "fetched. No Gaelic fixture verified this session.",
    },
    {
        "id": "src-atp-scores",
        "org": "ATP Tour",
        "url": "https://www.atptour.com/en/scores/current",
        "observed": "2026-10-23T16:29Z",
        "method": "Arena page-fetch, chunk 0",
        "role": "official",
        "note": "Live/current scoreboard shows different matches (Brussels/Lyon quarter-finals) from the "
                "nine OLBG tennis rows. No tennis fixture verified; the OLBG rows carry no competition label.",
    },
    {
        "id": "src-wta-scores",
        "org": "WTA",
        "url": "https://www.wtatennis.com/scores",
        "observed": "2026-10-23T16:30Z",
        "method": "Arena page-fetch, chunk 0",
        "role": "official",
        "note": "Client-rendered; notification feed only, no match rows. No WTA fixture verified.",
    },
]


def ev(sport, eid, name, comp, when, pick, market, tips, pct, url):
    return {
        "sport": sport, "olbg_event_id": eid, "name": name, "competition_text": comp,
        "olbg_time_text": when, "olbg_pick": pick, "olbg_market": market,
        "olbg_tips": tips, "olbg_pct": pct, "olbg_url": url,
    }


B = "https://www.olbg.com/betting-tips/"

DISCOVERY = [
    # ---------------- ICE HOCKEY (13) ----------------
    ev("ice-hockey", 199946, "Esbjerg Energy vs Herning Blue Fox", "Danish Metal Ligaen", "Today 13:00", "Herning Blue Fox", "Money Line", "3/3", 100, B + "Ice_Hockey/Other/Danish_Metal_Ligaen/Esbjerg_Energy_vs_Herning_Blue_Fox/13?event_id=199946"),
    ev("ice-hockey", 199984, "MTL Canadiens @ CHI Blackhawks", "NHL", "Today 20:07", "MTL Canadiens", "Money Line", "3/3", 100, B + "Ice_Hockey/NHL/NHL/MTL_Canadiens_@_CHI_Blackhawks/13?event_id=199984"),
    ev("ice-hockey", 199927, "Grizzlys Wolfsburg vs ERC Ingolstadt", "Germany Eishockey Liga", "Today 13:30", "ERC Ingolstadt", "Money Line", "2/2", 100, B + "Ice_Hockey/Other/Germany_Eishockey_Liga/Grizzlys_Wolfsburg_vs_ERC_Ingolstadt/13?event_id=199927"),
    ev("ice-hockey", 199947, "Rodovre Mighty Bulls vs Herlev Eagles", "Danish Metal Ligaen", "Today 13:30", "Herlev Eagles", "Money Line", "2/2", 100, B + "Ice_Hockey/Other/Danish_Metal_Ligaen/Rodovre_Mighty_Bulls_vs_Herlev_Eagles/13?event_id=199947"),
    ev("ice-hockey", 199955, "K Espoo vs HIFK", "Finland SM Liiga", "Today 12:30", "Over 5.50", "Game Totals", "1/1", 100, B + "Ice_Hockey/Other/Finland_SM_Liiga/K_Espoo_vs_HIFK/13?event_id=199955"),
    ev("ice-hockey", 199965, "Graz 99ers vs EHC Black Wings Linz", "Austria EHL", "Today 12:30", "EHC Black Wings Linz +1.50", "Puck Line", "1/2", 50, B + "Ice_Hockey/Other/Austria_EHL/Graz_99ers_vs_EHC_Black_Wings_Linz/13?event_id=199965"),
    ev("ice-hockey", 199969, "HK Olimpija Ljubljana vs Fehervar AV19", "Austria EHL", "Today 13:15", "HK Olimpija Ljubljana -1.50", "Puck Line", "1/1", 100, B + "Ice_Hockey/Other/Austria_EHL/HK_Olimpija_Ljubljana_vs_Fehervar_AV19/13?event_id=199969"),
    ev("ice-hockey", 199926, "Eisbaren Berlin vs Augsburger Panther", "Germany Eishockey Liga", "Today 13:30", "Eisbaren Berlin -1.50", "Puck Line", "1/1", 100, B + "Ice_Hockey/Other/Germany_Eishockey_Liga/Eisbaren_Berlin_vs_Augsburger_Panther/13?event_id=199926"),
    ev("ice-hockey", 199925, "Adler Mannheim vs Lowen Frankfurt", "Germany Eishockey Liga", "Today 13:30", "Adler Mannheim", "Money Line", "1/1", 100, B + "Ice_Hockey/Other/Germany_Eishockey_Liga/Adler_Mannheim_vs_Lowen_Frankfurt/13?event_id=199925"),
    ev("ice-hockey", 199928, "Nurnberg Ice Tigers vs Krefeld Pinguine", "Germany Eishockey Liga", "Today 13:30", "Under 5.50", "Game Totals", "1/1", 100, B + "Ice_Hockey/Other/Germany_Eishockey_Liga/Nurnberg_Ice_Tigers_vs_Krefeld_Pinguine/13?event_id=199928"),
    ev("ice-hockey", 199924, "EHC Munchen vs Iserlohn Roosters", "Germany Eishockey Liga", "Today 13:30", "EHC Munchen", "Money Line", "1/1", 100, B + "Ice_Hockey/Other/Germany_Eishockey_Liga/EHC_Munchen_vs_Iserlohn_Roosters/13?event_id=199924"),
    ev("ice-hockey", 199930, "Straubing Tigers vs Kolner Haie", "Germany Eishockey Liga", "Today 13:30", "Under 5.50", "Game Totals", "1/1", 100, B + "Ice_Hockey/Other/Germany_Eishockey_Liga/Straubing_Tigers_vs_Kolner_Haie/13?event_id=199930"),
    ev("ice-hockey", 199968, "Pioneers Vorarlberg vs HCB Sudtirol Alperia", "Austria EHL", "Today 13:30", "HCB Sudtirol Alperia", "Money Line", "1/1", 100, B + "Ice_Hockey/Other/Austria_EHL/Pioneers_Vorarlberg_vs_HCB_Sudtirol_Alperia/13?event_id=199968"),
    ev("ice-hockey", 199908, "Fribourg Gotteron vs EHC Biel", "Switzerland NLA", "Today 13:45", "Fribourg Gotteron", "Money Line", None, None, B + "Ice_Hockey/Other/Switzerland_NLA/Fribourg_Gotteron_vs_EHC_Biel/13?event_id=199908"),

    # ---------------- BASKETBALL (4) ----------------
    ev("basketball", 535928, "Zalgiris vs Asvel Lyon Villeurbanne", "Euroleague", "Today 13:00", "Zalgiris", "Money Line", "9/16", 56, B + "Basketball/European/Euroleague/Zalgiris_vs_Asvel_Lyon_Villeurbanne/4?event_id=535928"),
    ev("basketball", 535925, "Olympiacos vs Fenerbahce", "Euroleague", "Today 14:15", "Olympiacos", "Money Line", "6/10", 60, B + "Basketball/European/Euroleague/Olympiacos_vs_Fenerbahce/4?event_id=535925"),
    ev("basketball", 535926, "Paris vs Valencia", "Euroleague", "Today 14:45", "Valencia", "Money Line", "5/10", 50, B + "Basketball/European/Euroleague/Paris_vs_Valencia/4?event_id=535926"),
    ev("basketball", 536041, "CHI Bulls @ MIL Bucks", "NBA", "Today 16:10", "MIL Bucks", "Money Line", "5/5", 100, B + "Basketball/NBA/NBA/CHI_Bulls_@_MIL_Bucks/4?event_id=536041"),
    ev("basketball", 536036, "MIN Timberwolves @ ORL Magic", "NBA", "Today 19:10", "MIN Timberwolves", "Money Line", "5/5", 100, B + "Basketball/NBA/NBA/MIN_Timberwolves_@_ORL_Magic/4?event_id=536036"),
    ev("basketball", 534841, "HOU Rockets @ SA Spurs", "NBA", "Today 21:40", "SA Spurs", "Money Line", "4/6", 67, B + "Basketball/NBA/NBA/HOU_Rockets_@_SA_Spurs/4?event_id=534841"),
    ev("basketball", 534842, "NY Knicks @ BOS Celtics", "NBA", "Today 19:10", "BOS Celtics -2.50", "Pointspread", "3/3", 100, B + "Basketball/NBA/NBA/NY_Knicks_@_BOS_Celtics/4?event_id=534842"),
    ev("basketball", 536034, "TOR Raptors @ WAS Wizards", "NBA", "Today 19:10", "TOR Raptors", "Money Line", "3/4", 75, B + "Basketball/NBA/NBA/TOR_Raptors_@_WAS_Wizards/4?event_id=536034"),
    ev("basketball", 536037, "DAL Mavericks @ IND Pacers", "NBA", "Today 19:10", "IND Pacers", "Money Line", "3/3", 100, B + "Basketball/NBA/NBA/DAL_Mavericks_@_IND_Pacers/4?event_id=536037"),
    ev("basketball", 536038, "DET Pistons @ MIA Heat", "NBA", "Today 20:10", "DET Pistons", "Money Line", "3/3", 100, B + "Basketball/NBA/NBA/DET_Pistons_@_MIA_Heat/4?event_id=536038"),
    ev("basketball", 536043, "POR Trail Blazers @ SAC Kings", "NBA", "Today 22:10", "POR Trail Blazers -10.50", "Pointspread", "3/3", 100, B + "Basketball/NBA/NBA/POR_Trail_Blazers_@_SAC_Kings/4?event_id=536043"),
    ev("basketball", 536031, "Gtk Gliwice vs Torun", "Poland PLK", "Today 14:15", "Torun", "Money Line", "2/3", 67, B + "Basketball/European/Poland_PLK/Gtk_Gliwice_vs_Torun/4?event_id=536031"),
    ev("basketball", 536035, "ATL Hawks @ CHA Hornets", "NBA", "Today 19:10", "ATL Hawks -2.50", "Pointspread", "2/2", 100, B + "Basketball/NBA/NBA/ATL_Hawks_@_CHA_Hornets/4?event_id=536035"),
    ev("basketball", 536040, "NO Pelicans @ UTA Jazz", "NBA", "Today 21:40", "UTA Jazz", "Money Line", "2/2", 100, B + "Basketball/NBA/NBA/NO_Pelicans_@_UTA_Jazz/4?event_id=536040"),

    # ---------------- TENNIS (3) ----------------
    ev("tennis", 902150, "Arthur Fils vs Alex Michelsen", None, "Today 12:30", "Arthur Fils", "Win Match", "5/10", 50, B + "Tennis/All_Tennis/All_Events/Arthur_Fils_vs_Alex_Michelsen/3?event_id=902150"),
    ev("tennis", 902155, "Flavio Cobolli vs Brandon Nakashima", None, "Today 13:00", "Flavio Cobolli", "Win Match", "5/8", 63, B + "Tennis/All_Tennis/All_Events/Flavio_Cobolli_vs_Brandon_Nakashima/3?event_id=902155"),
    ev("tennis", 902153, "Jan Lennard Struff vs Zizou Bergs", None, "Today 14:00", "Jan Lennard Struff", "Win Match", "5/8", 63, B + "Tennis/All_Tennis/All_Events/Jan_Lennard_Struff_vs_Zizou_Bergs/3?event_id=902153"),
    ev("tennis", 902147, "Luca Van Assche vs Lorenzo Musetti", None, "Today 14:30", "Luca Van Assche", "Win Match", "3/5", 60, B + "Tennis/All_Tennis/All_Events/Luca_Van_Assche_vs_Lorenzo_Musetti/3?event_id=902147"),
    ev("tennis", 902157, "Ann Li vs Ashlyn Krueger", None, "Today 23:00", "Over 22.50", "Total Games", "2/3", 67, B + "Tennis/All_Tennis/All_Events/Ann_Li_vs_Ashlyn_Krueger/3?event_id=902157"),
    ev("tennis", 902162, "Katie Boulter vs Katerina Siniakova", None, "Tomorrow 00:30", "Katie Boulter", "Win Match", "1/1", 100, B + "Tennis/All_Tennis/All_Events/Katie_Boulter_vs_Katerina_Siniakova/3?event_id=902162"),
    ev("tennis", 902160, "Leylah Fernandez vs Marie Bouzkova", None, "Tomorrow 03:00", "Leylah Fernandez", "Win Match", "1/1", 100, B + "Tennis/All_Tennis/All_Events/Leylah_Fernandez_vs_Marie_Bouzkova/3?event_id=902160"),
    ev("tennis", 902163, "Elena Rybakina vs Diana Shnaider", None, "Tomorrow 05:30", "Diana Shnaider", "Win Match", "1/1", 100, B + "Tennis/All_Tennis/All_Events/Elena_Rybakina_vs_Diana_Shnaider/3?event_id=902163"),
    ev("tennis", 902159, "Nikoloz Basilashvili vs Stefanos Tsitsipas", None, "Tomorrow 06:00", "Stefanos Tsitsipas to win 2-1", "Set Betting", "1/1", 100, B + "Tennis/All_Tennis/All_Events/Nikoloz_Basilashvili_vs_Stefanos_Tsitsipas/3?event_id=902159"),

    # ---------------- CRICKET (7) ----------------
    ev("cricket", 188839, "Tasmania vs Victoria One Day Match", "Australia domestic", "Today 19:30", "Tasmania", "Win Match", "5/7", 71, B + "Cricket/All_Cricket/All_Events/Tasmania_vs_Victoria_One_Day_Match/7?event_id=188839"),
    ev("cricket", 188832, "New Zealand vs India 2nd T20 Match", None, "Tomorrow 03:00", "India", "Win Match", "4/5", 80, B + "Cricket/All_Cricket/All_Events/New_Zealand_vs_India_2nd_T20_Match/7?event_id=188832"),
    ev("cricket", 188840, "Western Australia vs New South Wales One Day Match", "Australia domestic", "Tomorrow 02:00", "Western Australia", "Win Match", "3/4", 75, B + "Cricket/All_Cricket/All_Events/Western_Australia_vs_New_South_Wales_One_Day_Match/7?event_id=188840"),
    ev("cricket", 188841, "Lions vs Limpopo Impalas T20", "South Africa domestic", "Tomorrow 07:00", "Lions", "Win Match", "3/3", 100, B + "Cricket/All_Cricket/All_Events/Lions_vs_Limpopo_Impalas_T20/7?event_id=188841"),
    ev("cricket", 188842, "Eastern Cape Iinyathi vs Warriors T20", "South Africa domestic", "Tomorrow 07:00", "Warriors", "Win Match", "2/2", 100, B + "Cricket/All_Cricket/All_Events/Eastern_Cape_Iinyathi_vs_Warriors_T20/7?event_id=188842"),
    ev("cricket", 188843, "Knights vs Mpumalanga Rhinos T20", "South Africa domestic", "Tomorrow 12:00", "Mpumalanga Rhinos", "Win Match", "1/1", 100, B + "Cricket/All_Cricket/All_Events/Knights_vs_Mpumalanga_Rhinos_T20/7?event_id=188843"),
    ev("cricket", 188838, "Pakistan vs England One Day Match", None, "25 Oct 04:00", "Pakistan", "Win Match", "1/1", 100, B + "Cricket/All_Cricket/All_Events/Pakistan_vs_England_One_Day_Match/7?event_id=188838"),
    ev("cricket", 182606, "World Cup 2027 (outright)", "ICC", "21 Nov 2027 05:00", "India", "Outright Winner", "6/12", 50, B + "Cricket/All_Cricket/All_Events/World_Cup_2027/7?event_id=182606"),
    ev("cricket", 187184, "Big Bash Women 2026 (outright)", "Australia", "05 Dec 03:10", "Sydney Sixers W", "Outright Winner", "2/3", 67, B + "Cricket/All_Cricket/All_Events/Big_Bash_Women_2026/7?event_id=187184"),
    ev("cricket", 187503, "T20 Big Bash 2026-27 (outright)", "Australia", "12 Dec 03:15", "Adelaide Strikers", "Outright Winner", "1/2", 50, B + "Cricket/All_Cricket/All_Events/T20_Big_Bash_2026-27/7?event_id=187503"),
    ev("cricket", 187504, "SA20 2026-27 (outright)", "South Africa", "24 Jan 2027 11:30", "Pretoria Capitals", "Outright Winner", "1/1", 100, B + "Cricket/All_Cricket/All_Events/SA20_2026-27/7?event_id=187504"),
    ev("cricket", 188350, "T20 Blast 2027 (outright)", "England", "18 Jul 2027 11:00", "Sussex", "Outright Winner", None, None, B + "Cricket/All_Cricket/All_Events/T20_Blast_2027/7?event_id=188350"),

    # ---------------- SNOOKER (8) ----------------
    ev("snooker", 9951, "Jak Jones v Scott Donaldson", "BetVictor Northern Ireland Open", "Today 14:05", "Jak Jones", "Win Match", "11/15", 73, B + "Snooker/All_Snooker/All_Events/Jak_Jones_v_Scott_Donaldson/8?event_id=9951"),
    ev("snooker", 9950, "David Gilbert v Mark Williams", "BetVictor Northern Ireland Open", "Today 14:05", "Mark Williams", "Win Match", "11/15", 73, B + "Snooker/All_Snooker/All_Events/David_Gilbert_v_Mark_Williams/8?event_id=9950"),

    # ---------------- DARTS (15) ----------------
    ev("darts", 32335, "Jonny Clayton vs Niko Springer", "European Championship", "Today 14:45", "Jonny Clayton", "Win Match 2-way", "26/31", 84, B + "Darts/All_Darts/All_Events/Jonny_Clayton_vs_Niko_Springer/15?event_id=32335"),
    ev("darts", 32326, "Wessel Nijman vs Martin Schindler", "European Championship", "Today 15:45", "Wessel Nijman", "Win Match 2-way", "18/23", 78, B + "Darts/All_Darts/All_Events/Wessel_Nijman_vs_Martin_Schindler/15?event_id=32326"),
    ev("darts", 32332, "Ryan Joyce vs Jermaine Wattimena", "European Championship", "Today 13:15", "Ryan Joyce", "Win Match 2-way", "16/25", 64, B + "Darts/All_Darts/All_Events/Ryan_Joyce_vs_Jermaine_Wattimena/15?event_id=32332"),
    ev("darts", 32333, "Krzysztof Ratajski vs Dave Chisnall", "European Championship", "Today 13:45", "Krzysztof Ratajski", "Win Match 2-way", "15/26", 58, B + "Darts/All_Darts/All_Events/Krzysztof_Ratajski_vs_Dave_Chisnall/15?event_id=32333"),
    ev("darts", 32327, "Nathan Aspinall vs Cristo Reyes", "European Championship", "Today 14:15", "Nathan Aspinall", "Win Match 2-way", "14/22", 64, B + "Darts/All_Darts/All_Events/Nathan_Aspinall_vs_Cristo_Reyes/15?event_id=32327"),
    ev("darts", 32328, "Luke Littler vs William OConnor", "European Championship", "Today 15:15", "Luke Littler", "Win Match 2-way", "14/20", 70, B + "Darts/All_Darts/All_Events/Luke_Littler_vs_William_OConnor/15?event_id=32328"),
    ev("darts", 32331, "Kevin Doets vs Michael van Gerwen", "European Championship", "Today 16:15", "Michael van Gerwen", "Win Match 2-way", "10/17", 59, B + "Darts/All_Darts/All_Events/Kevin_Doets_vs_Michael_van_Gerwen/15?event_id=32331"),
    ev("darts", 32336, "Josh Rock vs Chris Dobey", "European Championship", "Today 16:45", "Josh Rock", "Win Match 2-way", "10/19", 53, B + "Darts/All_Darts/All_Events/Josh_Rock_vs_Chris_Dobey/15?event_id=32336"),
    ev("darts", 32384, "Stephen Bunting vs Kim Huybrechts", "European Championship", "Tomorrow 13:15", "Kim Huybrechts", "Win Match 2-way", "2/3", 67, B + "Darts/All_Darts/All_Events/Stephen_Bunting_vs_Kim_Huybrechts/15?event_id=32384"),
    ev("darts", 32385, "Gian van Veen vs Luke Woodhouse", "European Championship", "Tomorrow 13:15", "Luke Woodhouse", "Win Match 2-way", "2/3", 67, B + "Darts/All_Darts/All_Events/Gian_van_Veen_vs_Luke_Woodhouse/15?event_id=32385"),
    ev("darts", 32386, "Ross Smith vs Damon Heta", "European Championship", "Tomorrow 13:15", "Damon Heta", "Win Match 2-way", "2/3", 67, B + "Darts/All_Darts/All_Events/Ross_Smith_vs_Damon_Heta/15?event_id=32386"),
    ev("darts", 32383, "Cameron Menzies vs Gerwyn Price", "European Championship", "Tomorrow 13:15", "Gerwyn Price", "Win Match 2-way", "1/2", 50, B + "Darts/All_Darts/All_Events/Cameron_Menzies_vs_Gerwyn_Price/15?event_id=32383"),
    ev("darts", 32338, "European Championship (outright)", "PDC", "25 Oct 14:00", "Gian van Veen", "Win Tournament", "4/18", 22, B + "Darts/All_Darts/All_Events/European_Championship/15?event_id=32338"),
    ev("darts", 26023, "PDC World Championship 2027 (outright)", "PDC", "03 Jan 2027 12:00", "Luke Littler", "Win Tournament", "23/37", 62, B + "Darts/All_Darts/All_Events/PDC_World_Championship_2027/15?event_id=26023"),

    # ---------------- BASEBALL (12) ----------------
    ev("baseball", 160789, "TB Rays @ MIL Brewers", "MLB World Series", "Today 20:00", "MIL Brewers", "Money Line", "25/31", 81, B + "Baseball/MLB/MLB/TB_Rays_@_MIL_Brewers/12?event_id=160789"),

    # ---------------- RUGBY UNION (9) ----------------
    ev("rugby-union", 609560, "Aurillac v Nevers", "ProD2", "Today 13:30", "Aurillac", "To Win", "14/19", 74, B + "Rugby_Union/All_Rugby_Union/All_Events/Aurillac_v_Nevers/9?event_id=609560"),
    ev("rugby-union", 609558, "Agen v Nissa", "ProD2", "Today 13:30", "Agen", "To Win", "12/18", 67, B + "Rugby_Union/All_Rugby_Union/All_Events/Agen_v_Nissa/9?event_id=609558"),
    ev("rugby-union", 609557, "Narbonne v Brive", "ProD2", "Today 13:00", "Brive", "To Win", "11/17", 65, B + "Rugby_Union/All_Rugby_Union/All_Events/Narbonne_v_Brive/9?event_id=609557"),
    ev("rugby-union", 609577, "Connacht v Zebre Parma", "United Rugby Championship", "Today 14:45", "Connacht", "To Win", "11/15", 73, B + "Rugby_Union/All_Rugby_Union/All_Events/Connacht_v_Zebre_Parma/9?event_id=609577"),
    ev("rugby-union", 609579, "Edinburgh v Lions", "United Rugby Championship", "Today 14:45", "Edinburgh", "To Win", "8/9", 89, B + "Rugby_Union/All_Rugby_Union/All_Events/Edinburgh_v_Lions/9?event_id=609579"),
    ev("rugby-union", 609563, "Soyaux Angouleme v Dax", "ProD2", "Today 13:30", "Dax", "To Win", "7/14", 50, B + "Rugby_Union/All_Rugby_Union/All_Events/Soyaux_Angouleme_v_Dax/9?event_id=609563"),
    ev("rugby-union", 609570, "Gloucester v Bath", "Premiership", "Today 14:45", "Gloucester", "To Win", "7/7", 100, B + "Rugby_Union/All_Rugby_Union/All_Events/Gloucester_v_Bath/9?event_id=609570"),
    ev("rugby-union", 609559, "Valence Romans v Colomiers", "ProD2", "Today 13:30", "Valence Romans", "To Win", "6/11", 55, B + "Rugby_Union/All_Rugby_Union/All_Events/Valence_Romans_v_Colomiers/9?event_id=609559"),
    ev("rugby-union", 609562, "Provence v Beziers", "ProD2", "Today 15:00", "Provence", "To Win", "6/10", 60, B + "Rugby_Union/All_Rugby_Union/All_Events/Provence_v_Beziers/9?event_id=609562"),
    ev("rugby-union", 609561, "Grenoble v Biarritz", "ProD2", "Today 15:00", "Grenoble", "To Win", "6/10", 60, B + "Rugby_Union/All_Rugby_Union/All_Events/Grenoble_v_Biarritz/9?event_id=609561"),
    ev("rugby-union", 609575, "Cardiff v Sharks", "United Rugby Championship", "Today 14:45", "Sharks", "To Win", "4/7", 57, B + "Rugby_Union/All_Rugby_Union/All_Events/Cardiff_v_Sharks/9?event_id=609575"),
    ev("rugby-union", 609573, "Newcastle Red Bulls v Sale Sharks", "Premiership", "Today 14:45", "Sale Sharks", "To Win", "3/5", 60, B + "Rugby_Union/All_Rugby_Union/All_Events/Newcastle_Red_Bulls_v_Sale_Sharks/9?event_id=609573"),
    ev("rugby-union", 609576, "Bulls v Ulster", "United Rugby Championship", "Tomorrow 07:45", "Ulster", "To Win", "3/4", 75, B + "Rugby_Union/All_Rugby_Union/All_Events/Bulls_v_Ulster/9?event_id=609576"),
    ev("rugby-union", 609582, "Japan v Fiji", None, "Tomorrow 01:50", "Fiji", "To Win", "2/3", 67, B + "Rugby_Union/All_Rugby_Union/All_Events/Japan_v_Fiji/9?event_id=609582"),
    ev("rugby-union", 609580, "Stormers v Scarlets", "United Rugby Championship", "Tomorrow 10:00", "Scarlets", "To Win", None, None, B + "Rugby_Union/All_Rugby_Union/All_Events/Stormers_v_Scarlets/9?event_id=609580"),

    # ---------------- VOLLEYBALL (21) ----------------
    ev("volleyball", 37009, "VOLLEY GOATS Mitteldeutschland vs Netzhoppers KW", "Germany Bundesliga", "Today 13:30", "Netzhoppers KW", "Win Match", "6/7", 86, B + "Volleyball/All_Volleyball/All_Events/VOLLEY_GOATS_Mitteldeutschland_vs_Netzhoppers_KW/21?event_id=37009"),
    ev("volleyball", 37001, "Brasilia W vs Sesc RJ Flamengo W", "Brazil", "Today 17:30", "Brasilia W", "Win Match", "5/9", 56, B + "Volleyball/All_Volleyball/All_Events/Brasilia_W_vs_Sesc_RJ_Flamengo_W/21?event_id=37001"),
    ev("volleyball", 37015, "ATSC Klagenfurt Women vs Linz Steg W", "Austria", "Today 14:00", "Linz Steg W", "Win Match", "4/7", 57, B + "Volleyball/All_Volleyball/All_Events/ATSC_Klagenfurt_Women_vs_Linz_Steg_W/21?event_id=37015"),
    ev("volleyball", 37022, "Minas W vs Paulistano-Barueri W", "Brazil", "Today 17:30", "Minas W", "Win Match", "4/6", 67, B + "Volleyball/All_Volleyball/All_Events/Minas_W_vs_Paulistano-Barueri_W/21?event_id=37022"),
    ev("volleyball", 37025, "Lokomotiv Avia vs Montana", "Bulgaria", "Today 12:30", "Lokomotiv Avia", "Win Match", "3/4", 75, B + "Volleyball/All_Volleyball/All_Events/Lokomotiv_Avia_vs_Montana/21?event_id=37025"),
    ev("volleyball", 36964, "PGE Skra Belchatow vs Projekt Warszawa", "Poland PlusLiga", "Tomorrow 12:00", "Projekt Warszawa", "Win Match", "2/3", 67, B + "Volleyball/All_Volleyball/All_Events/PGE_Skra_Belchatow_vs_Projekt_Warszawa/21?event_id=36964"),
    ev("volleyball", 37002, "Mackenzie W vs Osasco W", "Brazil", "Tomorrow 15:00", "Mackenzie W", "Win Match", "2/3", 67, B + "Volleyball/All_Volleyball/All_Events/Mackenzie_W_vs_Osasco_W/21?event_id=37002"),
    ev("volleyball", 37003, "Abel-Moda Brusque W vs Praia Clube W", "Brazil", "Tomorrow 20:00", "Abel/Moda Brusque W", "Win Match", "2/2", 100, B + "Volleyball/All_Volleyball/All_Events/Abel-Moda_Brusque_W_vs_Praia_Clube_W/21?event_id=37003"),
    ev("volleyball", 36994, "Trentino vs Cisterna", "Italy SuperLega", "25 Oct 12:00", "Cisterna", "Win Match", "2/2", 100, B + "Volleyball/All_Volleyball/All_Events/Trentino_vs_Cisterna/21?event_id=36994"),
    ev("volleyball", 36997, "Perugia vs Pordenone", "Italy SuperLega", "25 Oct 13:00", "Pordenone", "Win Match", "2/2", 100, B + "Volleyball/All_Volleyball/All_Events/Perugia_vs_Pordenone/21?event_id=36997"),
    ev("volleyball", 36965, "CHKS Chelm vs Resovia Rzeszow", "Poland PlusLiga", "25 Oct 13:00", "Resovia Rzeszow", "Win Match", "2/3", 67, B + "Volleyball/All_Volleyball/All_Events/CHKS_Chelm_vs_Resovia_Rzeszow/21?event_id=36965"),
    ev("volleyball", 37017, "SG Sokol-Post W vs TSV Hartberg W", "Austria", "Tomorrow 10:30", "SG Sokol/Post W to win 3-1", "Set Score", "1/1", 100, B + "Volleyball/All_Volleyball/All_Events/SG_Sokol-Post_W_vs_TSV_Hartberg_W/21?event_id=37017"),
    ev("volleyball", 37031, "UVC Ried vs VBK Klagenfurt", "Austria", "Tomorrow 12:00", "UVC Ried", "Win Match", "1/1", 100, B + "Volleyball/All_Volleyball/All_Events/UVC_Ried_vs_VBK_Klagenfurt/21?event_id=37031"),
    ev("volleyball", 37026, "Sternberk W vs VK Lvice Praha W", "Czechia", "Tomorrow 12:00", "Sternberk W to win 3-1", "Set Score", "1/1", 100, B + "Volleyball/All_Volleyball/All_Events/Sternberk_W_vs_VK_Lvice_Praha_W/21?event_id=37026"),

    # ---------------- HANDBALL (20) ----------------
    ev("handball", 12083, "Pays dAix UC vs Toulouse", "France Starligue", "Today 14:00", "Toulouse", "Money Line", "7/16", 44, B + "Handball/All_Handball/All_Events/Pays_dAix_UC_vs_Toulouse/20?event_id=12083"),
    ev("handball", 12088, "Frisch Auf Goppingen vs ThSV Eisenach", "Germany HBL", "Today 13:00", "Tie", "Money Line", "6/15", 40, B + "Handball/All_Handball/All_Events/Frisch_Auf_Goppingen_vs_ThSV_Eisenach/20?event_id=12088"),
    ev("handball", 12101, "Bidasoa Irun vs Caserio Ciudad Real", "Spain Liga Asobal", "Today 13:00", "Bidasoa Irun", "Money Line", "6/12", 50, B + "Handball/All_Handball/All_Events/Bidasoa_Irun_vs_Caserio_Ciudad_Real/20?event_id=12101"),
    ev("handball", 12080, "Limoges 87 vs Dunkerque", "France Starligue", "Today 14:00", "Limoges 87", "Money Line", "6/15", 40, B + "Handball/All_Handball/All_Events/Limoges_87_vs_Dunkerque/20?event_id=12080"),
    ev("handball", 12093, "TSV Hannover Burgdorf vs TBV Lemgo Lippe", "Germany HBL", "Today 14:00", "Tie", "Money Line", "6/13", 46, B + "Handball/All_Handball/All_Events/TSV_Hannover_Burgdorf_vs_TBV_Lemgo_Lippe/20?event_id=12093"),
    ev("handball", 12120, "GRK Ohrid vs Spor Toto SK", "EHF European Cup", "Today 12:30", "Spor Toto SK +11.50", "Match Handicap", "5/5", 100, B + "Handball/All_Handball/All_Events/GRK_Ohrid_vs_Spor_Toto_SK/20?event_id=12120"),
    ev("handball", 12079, "Chartres vs USAM Nimes", "France Starligue", "Today 14:00", "Tie", "Money Line", "5/10", 50, B + "Handball/All_Handball/All_Events/Chartres_vs_USAM_Nimes/20?event_id=12079"),
    ev("handball", 12110, "Estonia W vs Kosovo W", "Women's international", "Today 14:00", "Kosovo (W)", "Money Line", "5/11", 45, B + "Handball/All_Handball/All_Events/Estonia_W_vs_Kosovo_W/20?event_id=12110"),
    ev("handball", 12121, "FC Barcelona vs Ciudad Encantada", "Spain Liga Asobal", "Today 13:00", "Ciudad Encantada +13.50", "Match Handicap", "4/5", 80, B + "Handball/All_Handball/All_Events/FC_Barcelona_vs_Ciudad_Encantada/20?event_id=12121"),
    ev("handball", 12085, "Selestat Alsace vs Caen", "France Starligue", "Today 14:30", "Caen", "Money Line", "4/8", 50, B + "Handball/All_Handball/All_Events/Selestat_Alsace_vs_Caen/20?event_id=12085"),
    ev("handball", 12086, "Tremblay vs Cesson Rennes", "France Starligue", "Today 14:30", "Cesson Rennes", "Money Line", "4/9", 44, B + "Handball/All_Handball/All_Events/Tremblay_vs_Cesson_Rennes/20?event_id=12086"),
    ev("handball", 12076, "Skive FH vs Aalborg Handbold", "Denmark", "Tomorrow 09:00", "Aalborg Handbold", "Money Line", "3/6", 50, B + "Handball/All_Handball/All_Events/Skive_FH_vs_Aalborg_Handbold/20?event_id=12076"),
    ev("handball", 12077, "Skjern Handbold vs Ribe Esbjerg HH", "Denmark", "Tomorrow 10:00", "Ribe Esbjerg HH", "Money Line", "2/3", 67, B + "Handball/All_Handball/All_Events/Skjern_Handbold_vs_Ribe_Esbjerg_HH/20?event_id=12077"),
    ev("handball", 12107, "Villa De Aranda vs Puerto Sagunto", "Spain Liga Asobal", "Tomorrow 13:00", "Puerto Sagunto", "Money Line", "2/2", 100, B + "Handball/All_Handball/All_Events/Villa_De_Aranda_vs_Puerto_Sagunto/20?event_id=12107"),

    # ---------------- MOTOR RACING (14) ----------------
    ev("motor-racing", 913, "USA Grand Prix", "Formula 1", "25 Oct 16:00", "Max Verstappen", "Win Race", "13/38", 34, B + "Motor_Racing/All_Motor_Racing/All_Events/USA_Grand_Prix/14?event_id=913"),
    ev("motor-racing", 828, "Formula 1 Drivers Championship 2026 (outright)", "Formula 1", "06 Dec 08:00", "Max Verstappen", "Win Tournament", "9/33", 27, B + "Motor_Racing/All_Motor_Racing/All_Events/Formula_1_Drivers_Championship_2026/14?event_id=828"),
    ev("motor-racing", 912, "F1 Drivers Championship 2026 Without Kimi Antonelli (outright)", "Formula 1", "06 Dec 08:00", "Max Verstappen", "Win Tournament", "4/7", 57, B + "Motor_Racing/All_Motor_Racing/All_Events/Formula_1_Drivers_Championship_2026_Without_Kimi_Antonelli/14?event_id=912"),

    # ---------------- GAELIC SPORTS (25) ----------------
    ev("gaelic-sports", 3530, "St Finbarrs v Nemo Rangers", "Cork SFC", "25 Oct 12:00", "Nemo Rangers +1.50", None, "14/18", 78, B + "Gaelic_Football/All_Gaelic_Football/All_Events/St_Finbarrs_v_Nemo_Rangers/25?event_id=3530"),
    ev("gaelic-sports", 3532, "Moycullen v Salthill-Knocknacarra", "Galway SFC", "25 Oct 12:00", "Moycullen -3.50", None, "12/24", 50, B + "Gaelic_Football/All_Gaelic_Football/All_Events/Moycullen_v_Salthill-Knocknacarra/25?event_id=3532"),
    ev("gaelic-sports", 3531, "Kanturk v Eire Og Cor", "Cork club", "01 Nov 09:00", "Kanturk", None, "4/7", 57, B + "Gaelic_Football/All_Gaelic_Football/All_Events/Kanturk_v_Eire_Og_Cor/25?event_id=3531"),
    ev("gaelic-sports", 3537, "Fr Caseys v Kildimo Pallaskenry", "Limerick SFC", "01 Nov 10:30", "Fr Caseys", None, "3/3", 100, B + "Gaelic_Football/All_Gaelic_Football/All_Events/Fr_Caseys_v_Kildimo_Pallaskenry/25?event_id=3537"),
    ev("gaelic-sports", 3327, "All Ireland Football Championship 2027 (outright)", "GAA", "25 Jul 2027 10:30", "Kerry", None, "5/7", 71, B + "Gaelic_Football/All_Gaelic_Football/All_Events/All_Ireland_Football_Championship_2027/25?event_id=3327"),

    # ---------------- GREYHOUNDS (28) ----------------
    ev("greyhounds", 689803, "5:12 Towcester", "GBGB daily card", "Today 12:12", "Choices Jean", "Daily Races", "2/4", 50, B + "Greyhounds/All_Greyhounds/All_Events/5:12_Towcester/28?event_id=689803"),
    ev("greyhounds", 689800, "5:18 Kinsley", "GBGB daily card", "Today 12:18", "Grumpy Sandstorm", "Daily Races", "2/2", 100, B + "Greyhounds/All_Greyhounds/All_Events/5:18_Kinsley/28?event_id=689800"),
    ev("greyhounds", 689802, "5:31 Towcester", "GBGB daily card", "Today 12:31", "Mums Image", "Daily Races", "2/2", 100, B + "Greyhounds/All_Greyhounds/All_Events/5:31_Towcester/28?event_id=689802"),
    ev("greyhounds", 689805, "5:49 Towcester", "GBGB daily card", "Today 12:49", "Trapstyle Sneezy", "Daily Races", "2/2", 100, B + "Greyhounds/All_Greyhounds/All_Events/5:49_Towcester/28?event_id=689805"),
    ev("greyhounds", 689846, "8:33 Romford", "GBGB daily card", "Today 15:33", "Ontherun Jamie", "Daily Races", "2/2", 100, B + "Greyhounds/All_Greyhounds/All_Events/8:33_Romford/28?event_id=689846"),
    ev("greyhounds", 689717, "9:13 Romford", "GBGB daily card", "Today 16:13", "Grouchos Gregor", "Daily Races", "2/2", 100, B + "Greyhounds/All_Greyhounds/All_Events/9:13_Romford/28?event_id=689717"),
    ev("greyhounds", 689806, "5:24 Newcastle", "GBGB daily card", "Today 12:24", "Alnwick Tina", "Daily Races", "1/1", 100, B + "Greyhounds/All_Greyhounds/All_Events/5:24_Newcastle/28?event_id=689806"),
    ev("greyhounds", 689804, "5:37 Kinsley", "GBGB daily card", "Today 12:37", "Grumpy Jacko", "Daily Races", "1/1", 100, B + "Greyhounds/All_Greyhounds/All_Events/5:37_Kinsley/28?event_id=689804"),
    ev("greyhounds", 689798, "5:43 Newcastle", "GBGB daily card", "Today 12:43", "Dryland Velvet", "Daily Races", "1/2", 50, B + "Greyhounds/All_Greyhounds/All_Events/5:43_Newcastle/28?event_id=689798"),
    ev("greyhounds", 689801, "5:51 Harlow", "GBGB daily card", "Today 12:51", "Doreens Poppy", "Daily Races", "1/1", 100, B + "Greyhounds/All_Greyhounds/All_Events/5:51_Harlow/28?event_id=689801"),
    ev("greyhounds", 689807, "5:56 Kinsley", "GBGB daily card", "Today 12:56", "Kellyseyenoone", "Daily Races", "1/1", 100, B + "Greyhounds/All_Greyhounds/All_Events/5:56_Kinsley/28?event_id=689807"),
    ev("greyhounds", 689808, "6:02 Newcastle", "GBGB daily card", "Today 13:02", "Mollys Aoibhe", "Daily Races", "1/1", 100, B + "Greyhounds/All_Greyhounds/All_Events/6:02_Newcastle/28?event_id=689808"),
    ev("greyhounds", 689810, "6:08 Nottingham", "GBGB daily card", "Today 13:08", "Honeygar Flow", "Daily Races", "1/1", 100, B + "Greyhounds/All_Greyhounds/All_Events/6:08_Nottingham/28?event_id=689810"),
    ev("greyhounds", 689811, "6:11 Harlow", "GBGB daily card", "Today 13:11", "Club Dream", "Daily Races", "1/1", 100, B + "Greyhounds/All_Greyhounds/All_Events/6:11_Harlow/28?event_id=689811"),
    ev("greyhounds", 689816, "6:18 Sheffield", "GBGB daily card", "Today 13:18", "Jaykay Seven", "Daily Races", "1/1", 100, B + "Greyhounds/All_Greyhounds/All_Events/6:18_Sheffield/28?event_id=689816"),

    # ---------------- RUGBY LEAGUE (10) ----------------
    ev("rugby-league", 2695857, "State of Origin 2027 (outright)", "NRL", "27 May 2027 06:00", "New South Wales", "Win Tournament", "9/12", 75, B + "Rugby_League/All_Rugby_League/All_Events/State_of_Origin_2027/10?event_id=2695857"),
    ev("rugby-league", 2801554, "Super League 2027 (outright)", "RFL", "02 Oct 2027 13:00", "Leeds Rhinos", "Grand Final Winner", "1/3", 33, B + "Rugby_League/All_Rugby_League/All_Events/Super_League_2027/10?event_id=2801554"),
    ev("rugby-league", 2801600, "NRL 2027 (outright)", "NRL", "03 Oct 2027 04:00", "Penrith Panthers", "Grand Final Winner", "1/2", 50, B + "Rugby_League/All_Rugby_League/All_Events/NRL_2027/10?event_id=2801600"),
]

# ---------------------------------------------------------------------------
# Fixtures confirmed on an official page fetched THIS session.
# 'verified': every populated field below is traceable to the cited source id.
# ---------------------------------------------------------------------------
FIXTURES = [
    {
        "id": "fx-nhl-mtl-chi",
        "sport": "ice-hockey",
        "name": "Montreal Canadiens at Chicago Blackhawks",
        "home": "Chicago Blackhawks", "away": "Montreal Canadiens",
        "competition": "NHL",
        "official_start_utc": "2026-10-24T00:00:00Z",
        "venue": "United Center",
        "status": "FUT (scheduled, not started)",
        "olbg_event_id": 199984,
        "olbg_time_text": "Today 20:07",
        "sources": ["src-nhl-schedule"],
        "game_id": "2026020166",
        "facts": [
            {"k": "Official start", "v": "2026-10-24T00:00:00Z", "src": "src-nhl-schedule"},
            {"k": "Venue", "v": "United Center, Chicago", "src": "src-nhl-schedule"},
            {"k": "Game state", "v": "FUT; gameScheduleState OK", "src": "src-nhl-schedule"},
            {"k": "Quoted prices (provider 8/9/7)", "v": "MTL -170 / -170 / -162; CHI +138 / +142 / +134", "src": "src-nhl-schedule"},
            {"k": "Contradicting quotes (provider 6/3/10)", "v": "MTL 2.35 / 1.60 / 2.03; CHI 1.59 / 2.37 / 3.15", "src": "src-nhl-schedule"},
        ],
        "inputs": {"kind": "nhl-provider-quotes", "providers_used": [8, 9, 7]},
    },
    {
        "id": "fx-nhl-tbl-col",
        "sport": "ice-hockey",
        "name": "Tampa Bay Lightning at Colorado Avalanche",
        "home": "Colorado Avalanche", "away": "Tampa Bay Lightning",
        "competition": "NHL",
        "official_start_utc": "2026-10-24T01:00:00Z",
        "venue": "Ball Arena",
        "status": "FUT (scheduled, not started)",
        "olbg_event_id": 199984,
        "olbg_time_text": "not listed on the OLBG ice hockey top list captured at 16:21Z",
        "sources": ["src-nhl-schedule"],
        "game_id": "2026020167",
        "facts": [
            {"k": "Official start", "v": "2026-10-24T01:00:00Z", "src": "src-nhl-schedule"},
            {"k": "Venue", "v": "Ball Arena, Denver", "src": "src-nhl-schedule"},
            {"k": "Game state", "v": "FUT; gameScheduleState OK", "src": "src-nhl-schedule"},
            {"k": "Quoted prices (provider 8/9/7)", "v": "TBL +105 / +105 / +106; COL -129 / -125 / -128", "src": "src-nhl-schedule"},
        ],
        "inputs": {"kind": "nhl-provider-quotes", "providers_used": [8, 9, 7]},
    },
    {
        "id": "fx-mlb-ws-g1",
        "sport": "baseball",
        "name": "Tampa Bay Rays at Milwaukee Brewers — World Series Game 1",
        "home": "Milwaukee Brewers", "away": "Tampa Bay Rays",
        "competition": "MLB World Series",
        "official_start_utc": "2026-10-24T00:00:00Z",
        "venue": "American Family Field",
        "status": "Scheduled (statusCode S, startTimeTBD false)",
        "olbg_event_id": 160789,
        "olbg_time_text": "Today 20:00",
        "sources": ["src-mlb-schedule", "src-mlb-standings-al", "src-mlb-records-capture"],
        "game_id": "849805",
        "facts": [
            {"k": "Official date / start", "v": "officialDate 2026-10-23; gameDate 2026-10-24T00:00:00Z", "src": "src-mlb-schedule"},
            {"k": "Series", "v": "World Series Game 1 of 7; isTied true", "src": "src-mlb-schedule"},
            {"k": "ifNecessary", "v": "N (Normal Game)", "src": "src-mlb-schedule"},
            {"k": "Probable pitchers", "v": "TB Nick Martinez; MIL Jacob Misiorowski", "src": "src-mlb-schedule"},
            {"k": "Tampa Bay regular season", "v": "98-64 (.605); home 55-26; away 43-38; RS 736 RA 650; lastTen 5-5", "src": "src-mlb-standings-al"},
            {"k": "Milwaukee regular season", "v": "103-59; RS 832 RA 618 (capture 2026-10-22)", "src": "src-mlb-records-capture"},
        ],
        "inputs": {"kind": "mlb-records", "away_rs": 736, "away_ra": 650, "away_g": 162,
                   "home_rs": 832, "home_ra": 618, "home_g": 162,
                   "away_pct": 0.605, "home_pct": 0.639},
    },
    {
        "id": "fx-urc-cardiff-sharks",
        "sport": "rugby-union",
        "name": "Cardiff Rugby v Hollywoodbets Sharks",
        "home": "Cardiff Rugby", "away": "Hollywoodbets Sharks",
        "competition": "United Rugby Championship Round 4",
        "official_start_utc": None,
        "local_start": "14:45 local (23 Oct 2026) — URC publishes local time only",
        "venue": "Cardiff Arms Park",
        "status": "Scheduled",
        "olbg_event_id": 609575,
        "olbg_time_text": "Today 14:45",
        "sources": ["src-urc-round4"],
        "facts": [
            {"k": "Fixture and local kick-off", "v": "Fri 23 Oct 2026, 14:45, Cardiff Arms Park", "src": "src-urc-round4"},
            {"k": "Round 3 form — Cardiff", "v": "Leinster 29-5 Cardiff (away, 10 Oct)", "src": "src-urc-round4"},
            {"k": "Round 3 form — Sharks", "v": "DHL Stormers 39-22 Hollywoodbets Sharks (away, 10 Oct)", "src": "src-urc-round4"},
        ],
        "inputs": {"kind": "urc-form", "hf": 3.0, "sigma": 13.0},
    },
    {
        "id": "fx-urc-connacht-zebre",
        "sport": "rugby-union",
        "name": "Connacht Rugby v Zebre Parma",
        "home": "Connacht Rugby", "away": "Zebre Parma",
        "competition": "United Rugby Championship Round 4",
        "official_start_utc": None,
        "local_start": "14:45 local (23 Oct 2026) — URC publishes local time only",
        "venue": "Dexcom Stadium",
        "status": "Scheduled",
        "olbg_event_id": 609577,
        "olbg_time_text": "Today 14:45",
        "sources": ["src-urc-round4"],
        "facts": [
            {"k": "Fixture and local kick-off", "v": "Fri 23 Oct 2026, 14:45, Dexcom Stadium", "src": "src-urc-round4"},
            {"k": "Round 3 form — Connacht", "v": "Glasgow Warriors 36-19 Connacht (away, 9 Oct)", "src": "src-urc-round4"},
            {"k": "Round 3 form — Zebre", "v": "Zebre Parma 12-29 Edinburgh (home, 10 Oct)", "src": "src-urc-round4"},
        ],
        "inputs": {"kind": "urc-form", "hf": 3.0, "sigma": 13.0},
    },
    {
        "id": "fx-urc-edinburgh-lions",
        "sport": "rugby-union",
        "name": "Edinburgh Rugby v 10bet Lions",
        "home": "Edinburgh Rugby", "away": "10bet Lions",
        "competition": "United Rugby Championship Round 4",
        "official_start_utc": None,
        "local_start": "14:45 local (23 Oct 2026) — URC publishes local time only",
        "venue": "Hive Stadium",
        "status": "Scheduled",
        "olbg_event_id": 609579,
        "olbg_time_text": "Today 14:45",
        "sources": ["src-urc-round4"],
        "facts": [
            {"k": "Fixture and local kick-off", "v": "Fri 23 Oct 2026, 14:45, Hive Stadium", "src": "src-urc-round4"},
            {"k": "Round 3 form — Edinburgh", "v": "Zebre Parma 12-29 Edinburgh (away, 10 Oct)", "src": "src-urc-round4"},
            {"k": "Round 3 form — Lions", "v": "Vodacom Bulls 57-15 10bet Lions (away, 10 Oct)", "src": "src-urc-round4"},
        ],
        "inputs": {"kind": "urc-form", "hf": 3.0, "sigma": 13.0},
    },
]

# Round 3 URC results used as form inputs (verbatim from src-urc-round4).
URC_R3 = [
    {"home": "Glasgow Warriors", "away": "Connacht", "hs": 36, "as": 19},
    {"home": "Dragons RFC", "away": "Ospreys", "hs": 31, "as": 38},
    {"home": "Vodacom Bulls", "away": "Lions", "hs": 57, "as": 15},
    {"home": "DHL Stormers", "away": "Sharks", "hs": 39, "as": 22},
    {"home": "Zebre Parma", "away": "Edinburgh", "hs": 12, "as": 29},
    {"home": "Scarlets", "away": "Benetton", "hs": 27, "as": 26},
    {"home": "Ulster", "away": "Munster", "hs": 26, "as": 26},
    {"home": "Leinster", "away": "Cardiff Rugby", "hs": 29, "as": 5},
]


def main():
    os.makedirs(OUT, exist_ok=True)
    payloads = {
        "sports.json": {"session": "cf2699ba-olbg1", "observed": OBS, "sports": SPORTS},
        "sources.json": {"session": "cf2699ba-olbg1", "observed": OBS, "count": len(SOURCES), "sources": SOURCES},
        "discovery.json": {
            "session": "cf2699ba-olbg1",
            "observed": "2026-10-23T16:19Z/2026-10-23T16:37Z",
            "method": "Arena page-fetch, chunk 0 of each OLBG hub",
            "note": "OLBG is discovery only. Counts are community tip votes, never probabilities. "
                    "Times carry no zone label; see F-CF-01.",
            "count": len(DISCOVERY),
            "events": DISCOVERY,
        },
        "fixtures.json": {
            "session": "cf2699ba-olbg1", "observed": OBS,
            "count": len(FIXTURES), "fixtures": FIXTURES, "urc_round3_results": URC_R3,
        },
    }
    for name, obj in payloads.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
            json.dump(obj, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
    print(f"wrote {len(payloads)} files: {len(SPORTS)} sports, {len(SOURCES)} sources, "
          f"{len(DISCOVERY)} discovery rows, {len(FIXTURES)} verified fixtures")


if __name__ == "__main__":
    main()
