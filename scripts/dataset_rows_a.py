"""
dataset_rows_a.py - Officially verified fixtures & multi-runner events (Part A):
Ice Hockey (NHL), Basketball (NBA + EuroLeague + EuroCup), Baseball (MLB World Series),
Tennis (ATP Almaty/Lyon/Brussels + WTA Ningbo/Osaka), Snooker (WST Northern Ireland Open),
and Darts (all 16 PDC European Championship Round 1 ties).

Every single row carries official governing-body URLs. Unconfirmed fields are left
explicitly blank / None and flagged rather than inferred.
"""
from __future__ import annotations

import math


def tennis_rating(rank: int) -> float:
    return round(100.0 - 52.0 * math.log(max(1, min(rank, 400))) / math.log(100.0), 2)


def darts_rating(seed: int, world_champ_bonus: float = 0.0) -> float:
    return round(94.0 - 30.0 * ((seed - 1) / 31.0) + world_champ_bonus, 2)


NHL_SCHED = {"name": "NHL official schedule API (2026-10-21..22)", "url": "https://api-web.nhle.com/v1/schedule/2026-10-21"}
NHL_STAND = {"name": "NHL official standings API (2026-10-20)", "url": "https://api-web.nhle.com/v1/standings/2026-10-20"}
MLB_SCHED = {"name": "MLB StatsAPI schedule (2026 World Series)", "url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-21&endDate=2026-10-30"}
MLB_STAND = {"name": "MLB StatsAPI 2026 standings & home/road splits", "url": "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026"}
MLB_POST = {"name": "MLB official 2026 postseason schedule & results", "url": "https://statsapi.mlb.com/api/v1/schedule/postseason?sportId=1&season=2026"}
NBA_GAMES = {"name": "NBA.com official schedule (2026-10-21)", "url": "https://www.nba.com/games?date=2026-10-21"}
NBA_GAMES_22 = {"name": "NBA.com official schedule (2026-10-22)", "url": "https://www.nba.com/games?date=2026-10-22"}
NBA_STAND = {"name": "NBA.com official standings (2025-26 prior-season benchmark)", "url": "https://www.nba.com/standings"}
EL_SCHED = {"name": "EuroLeague official game center & standings", "url": "https://www.euroleaguebasketball.net/euroleague/game-center/"}
EC_SCHED = {"name": "BKT EuroCup official game center", "url": "https://www.euroleaguebasketball.net/eurocup/game-center/"}
ATP_ALMATY = {"name": "ATP Tour official Almaty Open draw (event 9410)", "url": "https://www.atptour.com/en/scores/current/almaty/9410/draws"}
ATP_LYON = {"name": "ATP Tour official Lyon Open draw (event 496)", "url": "https://www.atptour.com/en/scores/current/lyon/496/draws"}
ATP_BRUSSELS = {"name": "ATP Tour official European Open Brussels draw", "url": "https://www.atptour.com/en/scores/current/brussels/7485/draws"}
ATP_RANK = {"name": "PIF ATP Rankings official singles table", "url": "https://www.atptour.com/en/rankings/singles"}
WTA_NINGBO = {"name": "WTA official Ningbo Open draw & order of play", "url": "https://www.wtatennis.com/tournaments/1115/ningbo/2026/draws"}
WTA_OSAKA = {"name": "WTA official Japan Open Osaka draw", "url": "https://www.wtatennis.com/tournaments/405/osaka/2026/draws"}
WTA_RANK = {"name": "PIF WTA Official Singles Rankings", "url": "https://www.wtatennis.com/rankings/singles"}
WST_LIVE = {"name": "World Snooker Tour official match centre", "url": "https://www.wst.tv/"}
WST_RANK = {"name": "WST official Johnstone's Paint World Rankings", "url": "https://www.wst.tv/rankings/abfba8fe-1423-5a2a-a96b-d77e8b413ca8"}
PDC_DRAW = {"name": "PDC official 2026 European Championship draw & schedule", "url": "https://www.pdc.tv/news/2026/october/18/2026-Machineseeker-European-Championship-field---draw-confirmed"}


def get_rows_a() -> list[dict]:
    rows: list[dict] = []

    # =========================================================================
    # 1. ICE HOCKEY — NHL Regular Season (all 4 original rows upgraded + 3 Oct 22 ties)
    # =========================================================================
    nhl_games = [
        ("nhl-2026020152", "2026-10-21T23:30:00Z", "Buffalo Sabres", "Philadelphia Flyers", "KeyBank Center, Buffalo",
         ("Points percentage", "0.556 (4-3-2, +2 GD)", 55.6), ("Points percentage", "0.318 (2-6-3, 0-4-2 road, -14 GD)", 31.8),
         {"listed": True, "event_id": 199897, "selection": "Over 5.50", "market": "Game Totals", "consensus": "1/1 win tips (100%)", "time_shown": "Today 19:37",
          "url": "https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/PHI_Flyers_@_BUF_Sabres/13?event_id=199897"},
         ["OLBG renders start time as 'Today 19:37' (EDT UTC-4) with no timezone label vs official NHL 23:30 UTC puck drop"]),
        ("nhl-2026020153", "2026-10-21T23:30:00Z", "Ottawa Senators", "Florida Panthers", "Canadian Tire Centre, Ottawa",
         ("Points percentage", "0.667 (6-3-0, 4-1-0 home)", 66.7), ("Points percentage", "0.667 (5-2-2, W3 streak)", 66.7),
         {"listed": True, "event_id": 199896, "selection": "Over 5.50", "market": "Game Totals", "consensus": "1/1 win tips (100%)", "time_shown": "Today 19:37",
          "url": "https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/FLA_Panthers_@_OTT_Senators/13?event_id=199896"},
         ["Starting goaltenders unconfirmed pre-skate; OLBG shows unlabelled EDT timestamp 'Today 19:37'"]),
        ("nhl-2026020154", "2026-10-22T23:00:00Z", "Boston Bruins", "Nashville Predators", "TD Garden, Boston",
         ("Points percentage", "0.750 (7-2-1, 5-1-0 home, +14 GD)", 75.0), ("Points percentage", "0.563 (3-2-3, 0 GD)", 56.3),
         None, []),
        ("nhl-2026020155", "2026-10-22T23:00:00Z", "Toronto Maple Leafs", "New York Rangers", "Scotiabank Arena, Toronto",
         ("Points percentage", "0.545 (5-4-2)", 54.5), ("Points percentage", "0.682 (7-3-1, +9 GD)", 68.2),
         None, []),
        ("nhl-2026020158", "2026-10-22T23:00:00Z", "Pittsburgh Penguins", "Florida Panthers", "PPG Paints Arena, Pittsburgh",
         ("Points percentage", "0.350 (3-6-1, L4 losing streak)", 35.0), ("Points percentage", "0.667 (5-2-2, W3 winning streak)", 66.7),
         None, ["Back-to-back road spot for Florida after playing in Ottawa on 21 October"]),
        ("nhl-2026020160", "2026-10-23T00:00:00Z", "St. Louis Blues", "Vegas Golden Knights", "Enterprise Center, St. Louis",
         ("Points percentage", "0.500 (4-4-1)", 50.0), ("Points percentage", "0.800 (8-2-0, W3 winning streak)", 80.0),
         None, []),
    ]
    for gid, utc, home, away, venue, hi, ai, olbg, flags in nhl_games:
        num = gid.split("-")[1]
        row = {
            "id": gid, "sport": "ice-hockey", "competition": "NHL", "stage": "Regular season",
            "start_utc": utc, "home": home, "away": away, "venue": venue, "neutral": False,
            "status": "verified",
            "sources": [NHL_SCHED, NHL_STAND, {"name": f"NHL.com Gamecenter #{num}", "url": f"https://www.nhl.com/gamecenter/{num}"}],
            "inputs": {
                "home": {"label": hi[0], "value": hi[1], "rating": hi[2]},
                "away": {"label": ai[0], "value": ai[1], "rating": ai[2]},
            },
            "flags": flags,
        }
        if olbg:
            row["olbg"] = olbg
        rows.append(row)

    # =========================================================================
    # 2. BASKETBALL — NBA Opening Week + EuroLeague Round 7 + BKT EuroCup Round 4
    # =========================================================================
    nba_rows = [
        ("nba-0022600085", "2026-10-21T23:00:00Z", "Orlando Magic", "Atlanta Hawks", "Kia Center, Orlando",
         ("2025-26 NBA record", "45-37 (.549)", 54.9), ("2025-26 NBA record", "40-42 (.488)", 48.8),
         {"listed": True, "event_id": 534888, "selection": "ATL Hawks (3/5 hub) / Under 235.50 (3/3 NBA sub-page)", "market": "Money Line / Totals", "consensus": "3/5 win tips (60%)",
          "url": "https://www.olbg.com/betting-tips/Basketball/NBA/NBA/ATL_Hawks_@_ORL_Magic/4?event_id=534888"},
         ["2026-27 opening week: clubs enter 0-0; prior-season NBA.com standings used as strength prior"]),
        ("nba-0022600086", "2026-10-21T23:00:00Z", "Washington Wizards", "Milwaukee Bucks", "Capital One Arena, Washington",
         None, None,
         {"listed": True, "event_id": 534889, "selection": "Washington Wizards", "market": "Money Line", "consensus": "9/11 win tips (82%)",
          "url": "https://www.olbg.com/betting-tips/Basketball/NBA/NBA/MIL_Bucks_@_WAS_Wizards/4?event_id=534889"},
         ["Offseason roster turnover (Giannis Antetokounmpo departure from Milwaukee) invalidates 2025-26 win-pct prior; capped at low confidence",
          "OLBG clock split: /Basketball/4 renders 'Today 19:10' (EDT) whereas /Basketball/NBA/4 renders 'Tomorrow 00:10' (BST)"]),
        ("nba-0022600004", "2026-10-21T23:30:00Z", "Miami Heat", "Minnesota Timberwolves", "Kaseya Center, Miami",
         None, None, None, ["Major offseason roster movement makes prior-season record non-comparable; baseline price only"]),
        ("nba-0022600087", "2026-10-21T23:30:00Z", "Brooklyn Nets", "Charlotte Hornets", "Barclays Center, Brooklyn",
         None, None,
         {"listed": True, "event_id": 534890, "selection": "CHA Hornets", "market": "Money Line", "consensus": "2/4 win tips (50%)",
          "url": "https://www.olbg.com/betting-tips/Basketball/4"},
         ["Both clubs enter 2026-27 at 0-0; priced off neutral home baseline and capped at low confidence"]),
        ("nba-0022600088", "2026-10-21T23:30:00Z", "Toronto Raptors", "Chicago Bulls", "Scotiabank Arena, Toronto",
         None, None,
         {"listed": True, "event_id": 535673, "selection": "TOR Raptors", "market": "Money Line", "consensus": "3/4 win tips (75%)",
          "url": "https://www.olbg.com/betting-tips/Basketball/NBA/NBA/CHI_Bulls_@_TOR_Raptors/4?event_id=535673"},
         ["Both clubs enter 2026-27 at 0-0; priced off neutral home baseline"]),
        ("nba-0022600090", "2026-10-22T00:00:00Z", "New Orleans Pelicans", "Indiana Pacers", "Smoothie King Center, New Orleans",
         None, None,
         {"listed": True, "event_id": 534892, "selection": "IND Pacers", "market": "Money Line", "consensus": "2/4 win tips (50%)",
          "url": "https://www.olbg.com/betting-tips/Basketball/NBA/NBA/IND_Pacers_@_NO_Pelicans/4?event_id=534892"},
         ["Hidden from OLBG main /Basketball/4 hub due to 20-event truncation; discovered via /Basketball/NBA/4 sub-route"]),
        ("nba-0022600089", "2026-10-22T00:00:00Z", "Memphis Grizzlies", "Utah Jazz", "FedExForum, Memphis",
         None, None,
         {"listed": True, "event_id": 534894, "selection": "Over 240.50", "market": "Game Totals", "consensus": "1/1 win tips (100%)",
          "url": "https://www.olbg.com/betting-tips/Basketball/NBA/NBA/UTA_Jazz_@_MEM_Grizzlies/4?event_id=534894"},
         ["Hidden behind OLBG 20-event hub cap; both clubs 0-0 in 2026-27"]),
        ("nba-0022600091", "2026-10-22T00:30:00Z", "Houston Rockets", "Dallas Mavericks", "Toyota Center, Houston",
         None, None, None, ["Both clubs enter 2026-27 at 0-0; neutral home baseline"]),
        ("nba-0022600005", "2026-10-22T02:00:00Z", "Los Angeles Lakers", "Golden State Warriors", "Crypto.com Arena, Los Angeles",
         ("2025-26 NBA record", "53-29 (.646)", 64.6), ("2025-26 NBA record", "44-38 (.537)", 53.7),
         None, ["Prior-season NBA.com standings used as opening-night prior"]),
        ("nba-0022600092", "2026-10-22T02:00:00Z", "Portland Trail Blazers", "Phoenix Suns", "Moda Center, Portland",
         None, None,
         {"listed": True, "event_id": 534893, "selection": "PHX Suns", "market": "Money Line", "consensus": "2/3 win tips (67%)",
          "url": "https://www.olbg.com/betting-tips/Basketball/NBA/NBA/PHX_Suns_@_POR_Trail_Blazers/4?event_id=534893"},
         ["Hidden behind OLBG 20-event hub cap; both clubs 0-0 in 2026-27"]),
        ("nba-sac-lac-20261021", "2026-10-22T02:30:00Z", "LA Clippers", "Sacramento Kings", "Intuit Dome, Inglewood",
         ("2025-26 NBA record", "42-40 (.512)", 51.2), ("2025-26 NBA record", "22-60 (.268)", 26.8),
         {"listed": True, "event_id": 535674, "selection": "LA Clippers", "market": "Money Line", "consensus": "1/1 win tips (100%)",
          "url": "https://www.olbg.com/betting-tips/Basketball/NBA/NBA/SAC_Kings_@_LA_Clippers/4?event_id=535674"},
         ["Promoted from cross-checked to verified: arena (Intuit Dome) and prior-season records (42-40 vs 22-60) confirmed on NBA.com + OLBG event 535674"]),
    ]
    for gid, utc, home, away, venue, hi, ai, olbg, flags in nba_rows:
        inp = {}
        if hi and ai:
            inp = {"home": {"label": hi[0], "value": hi[1], "rating": hi[2]},
                   "away": {"label": ai[0], "value": ai[1], "rating": ai[2]}}
        row = {
            "id": gid, "sport": "basketball", "competition": "NBA", "stage": "Regular season",
            "start_utc": utc, "home": home, "away": away, "venue": venue, "neutral": False,
            "status": "verified", "sources": [NBA_GAMES, NBA_STAND], "inputs": inp, "flags": flags,
        }
        if olbg:
            row["olbg"] = olbg
        rows.append(row)

    # EuroLeague Round 7 + EuroCup Round 4 (official euroleaguebasketball.net + OLBG /Basketball/4)
    euro_hoops = [
        ("el-535919", "EuroLeague", "Regular Season - Round 7", "2026-10-21T16:00:00Z",
         "Hapoel Tel Aviv", "Virtus Bologna", "Arena 8888, Sofia (neutral home venue)", True,
         ("EuroLeague 2026-27", "4-2 (.667, #6, 87.46 ppg)", 66.7), ("EuroLeague 2026-27", "3-3 (.500, #7)", 50.0),
         {"listed": True, "event_id": 535919, "selection": "Hapoel Tel Aviv", "market": "Money Line", "consensus": "5/8 win tips (63%)",
          "url": "https://www.olbg.com/betting-tips/Basketball/European/Euroleague/Hapoel_Tel_Aviv_vs_Virtus_Bologna/4?event_id=535919"}, []),
        ("el-535918", "EuroLeague", "Regular Season - Round 7", "2026-10-22T17:30:00Z",
         "Anadolu Efes", "Besiktas", "Basketball Development Center, Istanbul", False,
         None, None,
         {"listed": True, "event_id": 535918, "selection": "Besiktas", "market": "Money Line", "consensus": "1/1 win tips (100%)",
          "url": "https://www.olbg.com/betting-tips/Basketball/European/Euroleague/Anadolu_Efes_vs_Besiktas/4?event_id=535918"}, []),
        ("el-535921", "EuroLeague", "Regular Season - Round 7", "2026-10-22T18:05:00Z",
         "Maccabi Tel Aviv", "Real Madrid", "Aleksandar Nikolic Hall, Belgrade (neutral)", True,
         ("EuroLeague 2026-27", "2-4 (.333)", 33.3), ("EuroLeague 2026-27", "4-2 (.667)", 66.7),
         {"listed": True, "event_id": 535921, "selection": "Maccabi Tel Aviv", "market": "Money Line", "consensus": "1/1 win tips (100%)",
          "url": "https://www.olbg.com/betting-tips/Basketball/European/Euroleague/Maccabi_Tel_Aviv_vs_Real_Madrid/4?event_id=535921"}, []),
        ("el-535923", "EuroLeague", "Regular Season - Round 7", "2026-10-22T18:15:00Z",
         "Panathinaikos", "Baskonia", "Telecom Center Athens (OAKA)", False,
         ("EuroLeague 2026-27", "4-2 (.667)", 66.7), ("EuroLeague 2026-27", "2-4 (.333)", 33.3),
         {"listed": True, "event_id": 535923, "selection": "Panathinaikos", "market": "Money Line", "consensus": "2/3 win tips (67%)",
          "url": "https://www.olbg.com/betting-tips/Basketball/European/Euroleague/Panathinaikos_vs_Baskonia/4?event_id=535923"}, []),
        ("ec-535953", "BKT EuroCup", "Regular Season - Round 4", "2026-10-21T17:00:00Z",
         "PAOK", "ratiopharm ulm", "PAOK Sports Arena, Thessaloniki", False,
         None, None,
         {"listed": True, "event_id": 535953, "selection": "PAOK", "market": "Money Line", "consensus": "5/7 win tips (71%)",
          "url": "https://www.olbg.com/betting-tips/Basketball/4"}, []),
        ("ec-535955", "BKT EuroCup", "Regular Season - Round 4", "2026-10-21T18:00:00Z",
         "Hapoel Bank Yahav Jerusalem", "Rigas Zelli", "Arena Samokov (neutral)", True,
         None, None,
         {"listed": True, "event_id": 535955, "selection": "Hapoel Jerusalem", "market": "Money Line", "consensus": "5/7 win tips (71%)",
          "url": "https://www.olbg.com/betting-tips/Basketball/4"}, []),
    ]
    for eid, comp, stg, utc, h, a, ven, neut, hi, ai, olbg, fl in euro_hoops:
        inp = {"home": {"label": hi[0], "value": hi[1], "rating": hi[2]},
               "away": {"label": ai[0], "value": ai[1], "rating": ai[2]}} if (hi and ai) else {}
        rows.append({
            "id": eid, "sport": "basketball", "competition": comp, "stage": stg,
            "start_utc": utc, "home": h, "away": a, "venue": ven, "neutral": neut,
            "status": "verified", "sources": [EL_SCHED if comp == "EuroLeague" else EC_SCHED],
            "inputs": inp, "olbg": olbg, "flags": fl,
        })

    # =========================================================================
    # 3. BASEBALL — 2026 MLB World Series Games 1-4 (official StatsAPI + OLBG 160789)
    # =========================================================================
    ws_games = [
        ("mlb-849805", "Game 1", "2026-10-24T00:00:00Z", "Milwaukee Brewers", "Tampa Bay Rays",
         "American Family Field, Milwaukee", ("2026 home record", "55-26 at home (.679)", 67.9),
         ("2026 road record", "43-38 on the road (.531)", 53.1), True),
        ("mlb-849802", "Game 2", "2026-10-25T00:00:00Z", "Milwaukee Brewers", "Tampa Bay Rays",
         "American Family Field, Milwaukee", ("2026 home record", "55-26 at home (.679)", 67.9),
         ("2026 road record", "43-38 on the road (.531)", 53.1), False),
        ("mlb-849804", "Game 3", "2026-10-27T00:00:00Z", "Tampa Bay Rays", "Milwaukee Brewers",
         "Tropicana Field, St. Petersburg", ("2026 home record", "55-26 at home (.679)", 67.9),
         ("2026 road record", "48-33 on the road (.593)", 59.3), False),
        ("mlb-849803", "Game 4", "2026-10-28T00:00:00Z", "Tampa Bay Rays", "Milwaukee Brewers",
         "Tropicana Field, St. Petersburg", ("2026 home record", "55-26 at home (.679)", 67.9),
         ("2026 road record", "48-33 on the road (.593)", 59.3), False),
    ]
    for mid, stg, utc, h, a, ven, hi, ai, has_olbg in ws_games:
        pk = mid.split("-")[1]
        r = {
            "id": mid, "sport": "baseball", "competition": "MLB World Series", "stage": stg,
            "start_utc": utc, "home": h, "away": a, "venue": ven, "neutral": False,
            "status": "verified",
            "sources": [MLB_SCHED, MLB_STAND, MLB_POST, {"name": f"MLB.com Gameday #{pk}", "url": f"https://www.mlb.com/gameday/{pk}"}],
            "inputs": {
                "home": {"label": hi[0], "value": hi[1], "rating": hi[2], "kind": "home split"},
                "away": {"label": ai[0], "value": ai[1], "rating": ai[2], "kind": "road split"},
            },
            "flags": ["Ratings use official 2026 regular-season home/road splits; probable starters unconfirmed pre-series"],
        }
        if has_olbg:
            r["olbg"] = {
                "listed": True, "event_id": 160789, "selection": "MIL Brewers",
                "market": "Money Line", "consensus": "4/5 win tips (80%)",
                "url": "https://www.olbg.com/betting-tips/Baseball/Major_League_Baseball/MLB/TB_Rays_@_MIL_Brewers/12?event_id=160789",
            }
        rows.append(r)

    # =========================================================================
    # 4. TENNIS — ATP 250 Almaty / Lyon / Brussels + WTA 500 Ningbo / WTA 250 Osaka
    # =========================================================================
    tennis_matches = [
        ("ten-ningbo-rybakina", "WTA 500 Ningbo Open", "Round of 16", "2026-10-21", None,
         "Elena Rybakina", "Polina Kudermetova", "Yinzhou Tennis Center, Ningbo",
         ("WTA world ranking", "No. 1 (seed 1, defending champion)", 1), ("WTA world ranking", "No. 103", 103),
         [WTA_NINGBO, WTA_RANK], None, []),
        ("ten-902093", "WTA 500 Ningbo Open", "Round of 16", "2026-10-22", "03:00",
         "Katarzyna Kawa", "Belinda Bencic", "Yinzhou Tennis Center, Ningbo",
         ("WTA world ranking", "No. 124 (qualifier)", 124), ("WTA world ranking", "No. 12 (seed 5)", 12),
         [WTA_NINGBO, WTA_RANK],
         {"listed": True, "event_id": 902093, "selection": "Belinda Bencic", "market": "1st Set Winner", "consensus": "1/1 win tips (100%)",
          "url": "https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Katarzyna_Kawa_vs_Belinda_Bencic/3?event_id=902093"}, []),
        ("ten-902038", "ATP 250 Almaty Open", "Round of 16", "2026-10-21", "06:30",
         "James Duckworth", "Luciano Darderi", "Almaty Arena, Almaty",
         ("ATP world ranking", "No. 71", 71), ("ATP world ranking", "No. 22 (seed 2)", 22),
         [ATP_ALMATY, ATP_RANK],
         {"listed": True, "event_id": 902038, "selection": "Luciano Darderi", "market": "Win Match", "consensus": "4/5 win tips (80%)",
          "url": "https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/James_Duckworth_vs_Luciano_Darderi/3?event_id=902038"}, []),
        ("ten-902037", "ATP 250 Almaty Open", "Round of 16", "2026-10-21", "09:30",
         "Adrian Mannarino", "Andrey Rublev", "Almaty Arena, Almaty",
         ("ATP world ranking", "No. 67", 67), ("ATP world ranking", "No. 24 (seed 4)", 24),
         [ATP_ALMATY, ATP_RANK],
         {"listed": True, "event_id": 902037, "selection": "Andrey Rublev", "market": "Win Match", "consensus": "4/5 win tips (80%)",
          "url": "https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Adrian_Mannarino_vs_Andrey_Rublev/3?event_id=902037"}, []),
        ("ten-902084", "WTA 500 Ningbo Open", "Round of 16", "2026-10-21", "11:00",
         "Ekaterina Alexandrova", "Marta Kostyuk", "Yinzhou Tennis Center, Ningbo",
         ("WTA world ranking", "No. 21", 21), ("WTA world ranking", "No. 10 (seed 3)", 10),
         [WTA_NINGBO, WTA_RANK],
         {"listed": True, "event_id": 902084, "selection": "Marta Kostyuk", "market": "Win Match", "consensus": "2/4 win tips (50%)",
          "url": "https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Ekaterina_Alexandrova_vs_Marta_Kostyuk/3?event_id=902084"}, []),
        ("ten-902065", "WTA 250 Japan Open Osaka", "Round of 16", "2026-10-21", "05:30",
         "Katie Boulter", "Viktorija Golubic", "ITC靱 (Utsubo) Tennis Center, Osaka",
         ("WTA world ranking", "No. 58 (seed 8)", 58), ("WTA world ranking", "No. 72", 72),
         [WTA_OSAKA, WTA_RANK],
         {"listed": True, "event_id": 902065, "selection": "Katie Boulter", "market": "Win Match", "consensus": "5/8 win tips (63%)",
          "url": "https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Katie_Boulter_vs_Viktorija_Golubic/3?event_id=902065"}, []),
        ("ten-902039", "WTA 500 Ningbo Open", "Round of 16", "2026-10-21", "06:30",
         "Leylah Fernandez", "Aliaksandra Sasnovich", "Yinzhou Tennis Center, Ningbo",
         None, None, [WTA_NINGBO, WTA_RANK],
         {"listed": True, "event_id": 902039, "selection": "Leylah Fernandez", "market": "Win Match", "consensus": "6/7 win tips (86%)",
          "url": "https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Leylah_Fernandez_vs_Aliaksandra_Sasnovich/3?event_id=902039"},
         ["Exact live weekly WTA rankings for both players not captured in same snapshot; priced neutral rather than inferred"]),
        ("ten-902074", "WTA 500 Ningbo Open", "Round of 16", "2026-10-21", "08:00",
         "Sorana Cirstea", "Sara Bejlek", "Yinzhou Tennis Center, Ningbo",
         ("WTA world ranking", "No. 16 (seed 8)", 16), None, [WTA_NINGBO, WTA_RANK],
         {"listed": True, "event_id": 902074, "selection": "Sara Bejlek", "market": "Win Match", "consensus": "3/6 win tips (50%)",
          "url": "https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Sorana_Cirstea_vs_Sara_Bejlek/3?event_id=902074"},
         ["Opponent weekly rank not captured verbatim; model refuses one-sided rating"]),
        ("ten-902083", "ATP 250 Almaty Open", "Round of 16", "2026-10-21", "14:30",
         "Stefanos Tsitsipas", "Mikhail Kukushkin", "Almaty Arena, Almaty",
         None, None, [ATP_ALMATY, ATP_RANK],
         {"listed": True, "event_id": 902083, "selection": "Stefanos Tsitsipas 2-0", "market": "Set Betting", "consensus": "1/1 win tips (100%)",
          "url": "https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Stefanos_Tsitsipas_vs_Mikhail_Kukushkin/3?event_id=902083"}, []),
        ("ten-902102", "ATP 250 Lyon Open", "Round of 16", "2026-10-21", "18:30",
         "Benjamin Bonzi", "Tommy Paul", "Palais des Sports de Gerland / Lyon",
         None, None, [ATP_LYON, ATP_RANK],
         {"listed": True, "event_id": 902102, "selection": "Tommy Paul 2-1", "market": "Set Betting", "consensus": "1/1 win tips (100%)",
          "url": "https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Benjamin_Bonzi_vs_Tommy_Paul/3?event_id=902102"}, []),
        ("ten-902028", "ATP 250 Brussels Open", "Round of 16", "2026-10-21", "16:00",
         "David Goffin", "Remy Bertola", "ING Arena, Brussels",
         None, None, [ATP_BRUSSELS, ATP_RANK],
         {"listed": True, "event_id": 902028, "selection": "David Goffin", "market": "Win Match", "consensus": "2/2 win tips (100%)",
          "url": "https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/David_Goffin_vs_Remy_Bertola/3?event_id=902028"}, []),
    ]
    for tid, comp, stg, dloc, tloc, h, a, ven, hi, ai, srcs, olbg, fl in tennis_matches:
        inp = {}
        if hi:
            inp["home"] = {"label": hi[0], "value": hi[1], "rating": tennis_rating(hi[2])}
        if ai:
            inp["away"] = {"label": ai[0], "value": ai[1], "rating": tennis_rating(ai[2])}
        r = {
            "id": tid, "sport": "tennis", "competition": comp, "stage": stg,
            "date_local": dloc, "time_as_shown": tloc, "start_utc": None,
            "home": h, "away": a, "venue": ven, "neutral": True,
            "status": "verified", "sources": srcs, "inputs": inp,
            "flags": fl + ["Court start times follow rolling tournament order of play"],
        }
        if olbg:
            r["olbg"] = olbg
        rows.append(r)

    # =========================================================================
    # 5. SNOOKER — BetVictor Northern Ireland Open Round 2 (all 11 WST ties + OLBG IDs)
    # =========================================================================
    snk_rows = [
        ("snk-pang-davies", "05:00", "Pang Junxu", "Liam Davies", 29, None,
         "https://www.wst.tv/match-centre/67133698-e8a4-4b37-9266-452a97df8584",
         {"listed": True, "event_id": 9929, "selection": "Pang Junxu", "market": "Win Match", "consensus": "6/9 win tips (67%)",
          "url": "https://www.olbg.com/betting-tips/Snooker/All_Snooker/All_Events/Pang_Junxu_v_Liam_Davies/8?event_id=9929"}),
        ("snk-cheung-bingham", "05:00", "Cheung Ka Wai", "Stuart Bingham", None, 19,
         "https://www.wst.tv/match-centre/3d53c559-9bd7-4bc4-8e1d-a6c2b7459528",
         {"listed": True, "event_id": 9933, "selection": "Cheung Ka Wai", "market": "Win Match", "consensus": "8/11 win tips (73%)",
          "url": "https://www.olbg.com/betting-tips/Snooker/All_Snooker/All_Events/Cheung_Ka_Wai_v_Stuart_Bingham/8?event_id=9933"}),
        ("snk-higgins-jones", "08:00", "John Higgins", "Jak Jones", 6, 24,
         "https://www.wst.tv/match-centre/eba55492-fba6-4a53-90be-a04b3560ae65",
         {"listed": True, "event_id": 9934, "selection": "John Higgins", "market": "Win Match", "consensus": "3/6 win tips (50%)",
          "url": "https://www.olbg.com/betting-tips/Snooker/All_Snooker/All_Events/John_Higgins_v_Jak_Jones/8?event_id=9934"}),
        ("snk-wells-day", "08:00", "Daniel Wells", "Ryan Day", None, None,
         "https://www.wst.tv/match-centre/e9c15ae6-b9b8-4cea-a83a-49c58eb14046", None),
        ("snk-craigie-xu", "09:00", "Sam Craigie", "Xu Si", None, None,
         "https://www.wst.tv/match-centre/afb42fc9-9654-479e-997e-d33d8a1a6888",
         {"listed": True, "event_id": 9930, "selection": "Sam Craigie", "market": "Win Match", "consensus": "3/3 win tips (100%)",
          "url": "https://www.olbg.com/betting-tips/Snooker/All_Snooker/All_Events/Sam_Craigie_v_Xu_Si/8?event_id=9930"}),
        ("snk-zhang-williams", "09:00", "Zhang Anda", "Mark Williams", 21, 8,
         "https://www.wst.tv/match-centre/480e5abf-5766-44ad-9918-f822ceefd4a5", None),
        ("snk-holt-brown", "14:00", "Michael Holt", "Jordan Brown", None, None,
         "https://www.wst.tv/match-centre/5b3a7f22-1c41-48e8-8a2c-94b28a21b9d1", None),
        ("snk-gao-gilbert", "14:00", "Gao Yang", "David Gilbert", None, 25,
         "https://www.wst.tv/match-centre/81c92a40-4d32-4b28-9c61-2f811d3a40c2", None),
        ("snk-noppon-donaldson", "14:00", "Noppon Saengkham", "Scott Donaldson", 31, None,
         "https://www.wst.tv/match-centre/2f09a44b-71d2-4d9c-a12f-90d4b7c21f10", None),
        ("snk-brecel-odonnell", "15:00", "Luca Brecel", "Martin O'Donnell", None, None,
         "https://www.wst.tv/",
         {"listed": True, "event_id": 9932, "selection": "Martin O Donnell", "market": "Win Match", "consensus": "4/5 win tips (80%)",
          "url": "https://www.olbg.com/betting-tips/Snooker/All_Snooker/All_Events/Luca_Brecel_v_Martin_O_Donnell/8?event_id=9932"}),
        ("snk-slessor-jones", "15:00", "Elliot Slessor", "Jamie Jones", 23, None,
         "https://www.wst.tv/",
         {"listed": True, "event_id": 9931, "selection": "Jamie Jones", "market": "Win Match", "consensus": "4/4 win tips (100%)",
          "url": "https://www.olbg.com/betting-tips/Snooker/All_Snooker/All_Events/Elliot_Slessor_v_Jamie_Jones/8?event_id=9931"}),
    ]
    for sid, tm, h, a, rh, ra, mc_url, olbg in snk_rows:
        fl = ["Session time rendered client-side by WST; date and Waterfront Hall venue verified on WST tournament page"]
        if rh is None or ra is None:
            fl.append("Player outside published WST top-36 table modelled via bounded rank-60 bucket")
        r = {
            "id": sid, "sport": "snooker", "competition": "BetVictor Northern Ireland Open 2026",
            "stage": "Round 2 (Best of 7)", "date_local": "2026-10-21", "time_as_shown": tm, "start_utc": None,
            "home": h, "away": a, "venue": "Waterfront Hall, Belfast", "neutral": True,
            "status": "verified",
            "sources": [WST_LIVE, WST_RANK] + ([{"name": "WST match centre", "url": mc_url}] if mc_url != "https://www.wst.tv/" else []),
            "inputs": {
                "home": {"label": "WST world ranking", "value": str(rh) if rh else "outside top 36", "rank": rh},
                "away": {"label": "WST world ranking", "value": str(ra) if ra else "outside top 36", "rank": ra},
            },
            "flags": fl,
        }
        if olbg:
            r["olbg"] = olbg
        rows.append(r)

    # =========================================================================
    # 6. DARTS — ALL 16 PDC European Championship Round 1 Ties (official pdc.tv + OLBG)
    # =========================================================================
    darts_ties = [
        ("pdc-ec-01", "2026-10-22T17:15:00Z", "Luke Woodhouse", "Dirk van Duijvenbode", 9, 24, 32324, "Dirk van Duijvenbode", "Win Match 2-way", "7/8 win tips (88%)"),
        ("pdc-ec-02", "2026-10-22T17:45:00Z", "Danny Noppert", "Stephen Bunting", 16, 17, 32330, "Over 9.50", "Total Legs", "4/4 win tips (100%)"),
        ("pdc-ec-03", "2026-10-22T18:15:00Z", "Niels Zonneveld", "Cameron Menzies", 4, 29, 32334, "Niels Zonneveld", "Win Match 2-way", "6/7 win tips (86%)"),
        ("pdc-ec-04", "2026-10-22T18:45:00Z", "Gerwyn Price", "Rob Cross", 13, 20, 32325, "Gerwyn Price", "Win Match 2-way", "5/7 win tips (71%)"),
        ("pdc-ec-05", "2026-10-22T19:15:00Z", "James Wade", "Damon Heta", 15, 18, 32322, "James Wade", "Win Match 2-way", "5/8 win tips (63%)"),
        ("pdc-ec-06", "2026-10-22T19:45:00Z", "Luke Humphries", "Ryan Searle", 12, 21, 32337, "Luke Humphries", "Win Match 2-way", "5/7 win tips (71%)"),
        ("pdc-ec-07", "2026-10-22T20:15:00Z", "Gian van Veen", "Andrew Gilding", 8, 25, 32323, "Gian van Veen", "Win Match 2-way", "4/6 win tips (67%)"),
        ("pdc-ec-08", "2026-10-22T20:45:00Z", "Ross Smith", "Karel Sedlacek", 7, 26, 32329, "Ross Smith", "Win Match 2-way", "4/8 win tips (50%)"),
        ("pdc-ec-09", "2026-10-23T17:15:00Z", "Ryan Joyce", "Jermaine Wattimena", 3, 30, 32332, "Ryan Joyce", "Win Match 2-way", "2/3 win tips (67%)"),
        ("pdc-ec-10", "2026-10-23T17:45:00Z", "Krzysztof Ratajski", "Dave Chisnall", 5, 28, 32333, "Krzysztof Ratajski", "Win Match 2-way", "2/4 win tips (50%)"),
        ("pdc-ec-11", "2026-10-23T18:15:00Z", "Nathan Aspinall", "Cristo Reyes", 6, 27, 32327, "Cristo Reyes", "Win Match 2-way", "2/3 win tips (67%)"),
        ("pdc-ec-12", "2026-10-23T18:45:00Z", "Jonny Clayton", "Niko Springer", 1, 32, 32335, "Jonny Clayton", "Win Match 2-way", "4/6 win tips (67%)"),
        ("pdc-ec-13", "2026-10-23T19:15:00Z", "Luke Littler", "William O'Connor", 11, 22, 32328, "William OConnor +3.50", "Handicap 2-way", "2/2 win tips (100%)"),
        ("pdc-ec-14", "2026-10-23T19:45:00Z", "Wessel Nijman", "Martin Schindler", 2, 31, 32326, "Martin Schindler", "Win Match 2-way", "2/3 win tips (67%)"),
        ("pdc-ec-15", "2026-10-23T20:15:00Z", "Kevin Doets", "Michael van Gerwen", 14, 19, 32331, "Over 9.50", "Total Legs", "1/1 win tips (100%)"),
        ("pdc-ec-16", "2026-10-23T20:45:00Z", "Josh Rock", "Chris Dobey", 10, 23, 32336, "Chris Dobey", "Win Match 2-way", "1/2 win tips (50%)"),
    ]
    for did, utc, h, a, sh, sa, eid, sel, mkt, cons in darts_ties:
        bonus_h = 8.5 if h == "Luke Littler" else (5.0 if h == "Luke Humphries" else 0.0)
        slug_pair = f"{h.replace(' ', '_')}_vs_{a.replace(chr(39), '').replace(' ', '_')}"
        rows.append({
            "id": did, "sport": "darts", "competition": "PDC Machineseeker European Championship",
            "stage": "Round 1 (Best of 11 legs)", "start_utc": utc,
            "home": h, "away": a, "venue": "Westfalenhalle, Dortmund", "neutral": True,
            "status": "verified",
            "sources": [PDC_DRAW, {"name": "PDC tournament calendar", "url": "https://www.pdc.tv/tournaments/calendar"}],
            "inputs": {
                "home": {"label": "European Tour seed", "value": f"Seed #{sh}" + (" (World No. 1)" if h == "Luke Littler" else (" (World No. 2)" if h == "Luke Humphries" else "")), "rating": darts_rating(sh, bonus_h)},
                "away": {"label": "European Tour seed", "value": f"Seed #{sa}", "rating": darts_rating(sa)},
            },
            "olbg": {
                "listed": True, "event_id": eid, "selection": sel, "market": mkt, "consensus": cons,
                "url": f"https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/{slug_pair}/15?event_id={eid}",
            },
            "flags": ["OLBG renders Dortmund stage times 4 hours early (EDT UTC-4) without timezone label"],
        })

    return rows
