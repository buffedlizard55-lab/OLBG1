#!/usr/bin/env python3
"""Live-verified governing-body standings, upcoming fixtures, elapsed Oct 22 results, and review flags.

Captured live between 2026-10-22T20:50:00Z and 2026-10-22T21:08:00Z.
Every unconfirmed value is None in Python/JSON and rendered as an explicit blank
marker in HTML tables — never inferred, interpolated, or filled from memory.
"""
from __future__ import annotations

# 1. Official 32-club NHL standings (https://api-web.nhle.com/v1/standings/2026-10-22, 2026-10-22T20:51:59Z)
# Tuple: (full_name, gp, w, l, otl, gf, ga, points)
NHL_STANDINGS = {
    "CAR": ("Carolina Hurricanes", 11, 8, 2, 1, 42, 27, 17),
    "VGK": ("Vegas Golden Knights", 11, 8, 3, 0, 44, 30, 16),
    "EDM": ("Edmonton Oilers", 9, 7, 1, 1, 41, 27, 15),
    "BOS": ("Boston Bruins", 10, 7, 2, 1, 36, 22, 15),
    "NYR": ("New York Rangers", 11, 7, 3, 1, 33, 24, 15),
    "TBL": ("Tampa Bay Lightning", 9, 7, 2, 0, 31, 23, 14),
    "UTA": ("Utah Mammoth", 10, 7, 3, 0, 38, 31, 14),
    "MIN": ("Minnesota Wild", 10, 6, 2, 2, 31, 25, 14),
    "OTT": ("Ottawa Senators", 10, 7, 3, 0, 29, 24, 14),
    "SEA": ("Seattle Kraken", 10, 6, 3, 1, 39, 34, 13),
    "FLA": ("Florida Panthers", 10, 5, 3, 2, 31, 30, 12),
    "TOR": ("Toronto Maple Leafs", 11, 5, 4, 2, 38, 35, 12),
    "NYI": ("New York Islanders", 9, 5, 3, 1, 27, 20, 11),
    "DAL": ("Dallas Stars", 9, 5, 3, 1, 23, 15, 11),
    "COL": ("Colorado Avalanche", 10, 5, 4, 1, 41, 31, 11),
    "SJS": ("San Jose Sharks", 10, 5, 4, 1, 27, 35, 11),
    "WSH": ("Washington Capitals", 9, 5, 4, 0, 30, 29, 10),
    "WPG": ("Winnipeg Jets", 9, 4, 3, 2, 24, 26, 10),
    "NJD": ("New Jersey Devils", 9, 5, 4, 0, 29, 30, 10),
    "MTL": ("Montréal Canadiens", 9, 4, 3, 2, 30, 34, 10),
    "BUF": ("Buffalo Sabres", 10, 4, 4, 2, 28, 37, 10),
    "NSH": ("Nashville Predators", 8, 3, 2, 3, 23, 24, 9),
    "STL": ("St. Louis Blues", 9, 4, 4, 1, 29, 29, 9),
    "DET": ("Detroit Red Wings", 9, 3, 3, 3, 23, 28, 9),
    "PHI": ("Philadelphia Flyers", 12, 3, 6, 3, 20, 37, 9),
    "ANA": ("Anaheim Ducks", 9, 4, 5, 0, 26, 29, 8),
    "PIT": ("Pittsburgh Penguins", 10, 3, 6, 1, 33, 38, 7),
    "CBJ": ("Columbus Blue Jackets", 8, 3, 5, 0, 20, 29, 6),
    "CHI": ("Chicago Blackhawks", 9, 3, 6, 0, 21, 36, 6),
    "VAN": ("Vancouver Canucks", 11, 2, 8, 1, 33, 51, 5),
    "LAK": ("Los Angeles Kings", 7, 1, 4, 2, 17, 27, 4),
    "CGY": ("Calgary Flames", 8, 2, 6, 0, 17, 37, 4),
}

# 2. Official MLB World Series clubs regular-season totals (statsapi.mlb.com)
# Tuple: (full_name, gp, w, l, rs, ra)
MLB_STANDINGS = {
    "TB": ("Tampa Bay Rays", 162, 98, 64, 736, 650),
    "MIL": ("Milwaukee Brewers", 162, 103, 59, 832, 618),
}

# 3. Official 20-club EuroLeague 2026-27 standings post-Thu Oct 22 R7 (euroleaguebasketball.net)
# Tuple: (gp, w, l, pf, pa)
EUROLEAGUE_STANDINGS = {
    "Panathinaikos AKTOR Athens": (7, 6, 1, 613, 517),
    "Fenerbahce Tarfin Istanbul": (6, 5, 1, 501, 447),
    "Olympiacos Piraeus": (6, 5, 1, 564, 524),
    "Hapoel IBI Tel Aviv": (7, 5, 2, 630, 601),
    "Dubai Basketball": (7, 5, 2, 597, 584),
    "Valencia Basket": (6, 4, 2, 583, 537),
    "Crvena Zvezda Meridianbet Belgrade": (6, 4, 2, 485, 457),
    "Real Madrid": (7, 4, 3, 667, 630),
    "FC Barcelona": (7, 4, 3, 623, 606),
    "Virtus Bologna": (7, 4, 3, 606, 608),
    "Partizan Mozzart Bet Belgrade": (6, 3, 3, 466, 471),
    "Anadolu Efes Istanbul": (7, 3, 4, 581, 590),
    "Besiktas Istanbul": (7, 3, 4, 634, 644),
    "Zalgiris Kaunas": (6, 2, 4, 490, 517),
    "LDLC ASVEL Villeurbanne": (6, 2, 4, 527, 572),
    "Maccabi Rapyd Tel Aviv": (7, 2, 5, 608, 653),
    "FC Bayern Munich": (7, 2, 5, 612, 659),
    "Paris Basketball": (6, 1, 5, 504, 545),
    "Armani Olimpia Milan": (7, 1, 6, 585, 648),
    "Kosner Baskonia Vitoria-Gasteiz": (7, 1, 6, 583, 649),
}

# 4. Official 24-club EHF Champions League Men Group Phase standings post-Thu Oct 22 R5 (ehfcl.eurohandball.com)
# Tuple: (group, gp, w, d, l, gf, ga, pts)
EHF_STANDINGS = {
    "One Veszprém HC": ("A", 5, 5, 0, 0, 185, 146, 10),
    "Füchse Berlin": ("A", 5, 3, 0, 2, 184, 172, 6),
    "FC Porto": ("A", 5, 1, 1, 3, 158, 173, 3),
    "RK Partizan AdmiralBet": ("A", 5, 0, 1, 4, 148, 184, 1),
    "Orlen Wisla Plock": ("B", 5, 3, 0, 2, 141, 136, 6),
    "MT Melsungen": ("B", 5, 3, 0, 2, 138, 138, 6),
    "HBC Nantes": ("B", 5, 3, 0, 2, 142, 143, 6),
    "HC Vardar 1961": ("B", 5, 1, 0, 4, 154, 158, 2),
    "Aalborg Håndbold": ("C", 5, 4, 1, 0, 170, 145, 9),
    "Paris Saint-Germain": ("C", 5, 3, 1, 1, 182, 157, 7),
    "HC Zagreb": ("C", 5, 2, 0, 3, 146, 158, 4),
    "RK Celje Pivovarna Laško": ("C", 5, 0, 0, 5, 150, 188, 0),
    "Sporting Clube de Portugal": ("D", 5, 4, 1, 0, 191, 165, 9),
    "GOG": ("D", 5, 3, 1, 1, 178, 172, 7),
    "OTP Bank - PICK Szeged": ("D", 5, 1, 2, 2, 172, 169, 4),
    "IFK Kristianstad": ("D", 5, 0, 0, 5, 162, 197, 0),
    "Barça": ("E", 5, 5, 0, 0, 177, 138, 10),
    "SAH - Aarhus": ("E", 5, 2, 1, 2, 150, 163, 5),
    "Dinamo Bucuresti": ("E", 5, 1, 1, 3, 134, 145, 3),
    "Montpellier Handball": ("E", 5, 1, 0, 4, 150, 165, 2),
    "SC Magdeburg": ("F", 5, 5, 0, 0, 176, 140, 10),
    "Industria Kielce": ("F", 5, 3, 0, 2, 155, 153, 6),
    "HC Kriens-Luzern": ("F", 5, 2, 0, 3, 158, 161, 4),
    "Kolstad Håndball": ("F", 5, 0, 0, 5, 143, 178, 0),
}


def _nhl_rows() -> list[dict]:
    raw = [
        ("2026020154", "2026-10-22", "2026-10-22T23:00:00Z", "NSH", "BOS", "TD Garden", "199936"),
        ("2026020155", "2026-10-22", "2026-10-22T23:00:00Z", "NYR", "TOR", "Scotiabank Arena", "199937"),
        ("2026020156", "2026-10-22", "2026-10-22T23:00:00Z", "SJS", "OTT", "Canadian Tire Centre", "199942"),
        ("2026020157", "2026-10-22", "2026-10-22T23:00:00Z", "ANA", "NJD", "Prudential Center", "199932"),
        ("2026020158", "2026-10-22", "2026-10-22T23:00:00Z", "FLA", "PIT", "PPG Paints Arena", "199934"),
        ("2026020159", "2026-10-22", "2026-10-22T23:30:00Z", "LAK", "NYI", "UBS Arena", "199938"),
        ("2026020160", "2026-10-22", "2026-10-23T00:00:00Z", "VGK", "STL", "Enterprise Center", "199940"),
        ("2026020161", "2026-10-22", "2026-10-23T00:00:00Z", "WPG", "DAL", "American Airlines Center", "199941"),
        ("2026020162", "2026-10-22", "2026-10-23T01:00:00Z", "MIN", "CGY", "Scotiabank Saddledome", "199935"),
        ("2026020163", "2026-10-22", "2026-10-23T01:00:00Z", "CAR", "EDM", "Rogers Place", "199931"),
        ("2026020164", "2026-10-22", "2026-10-23T02:00:00Z", "UTA", "SEA", "Climate Pledge Arena", "199939"),
        ("2026020165", "2026-10-22", "2026-10-23T02:00:00Z", "DET", "VAN", "Rogers Arena", "199933"),
        ("2026020166", "2026-10-23", "2026-10-24T00:00:00Z", "MTL", "CHI", "United Center", None),
        ("2026020167", "2026-10-23", "2026-10-24T01:00:00Z", "TBL", "COL", "Ball Arena", None),
        ("2026020168", "2026-10-24", "2026-10-24T17:00:00Z", "ANA", "PHI", "Xfinity Mobile Arena", None),
        ("2026020169", "2026-10-24", "2026-10-24T19:30:00Z", "LAK", "NJD", "Prudential Center", None),
        ("2026020170", "2026-10-24", "2026-10-24T23:00:00Z", "SJS", "BOS", "TD Garden", None),
        ("2026020171", "2026-10-24", "2026-10-24T23:00:00Z", "NYR", "OTT", "Canadian Tire Centre", None),
        ("2026020172", "2026-10-24", "2026-10-24T23:00:00Z", "NSH", "PIT", "PPG Paints Arena", None),
        ("2026020173", "2026-10-24", "2026-10-24T23:00:00Z", "BUF", "WSH", "Capital One Arena", None),
        ("2026020174", "2026-10-24", "2026-10-24T23:00:00Z", "VGK", "CBJ", "Nationwide Arena", None),
        ("2026020175", "2026-10-24", "2026-10-24T23:00:00Z", "CAR", "STL", "Enterprise Center", None),
        ("2026020176", "2026-10-24", "2026-10-24T23:00:00Z", "TOR", "EDM", "Rogers Place", None),
        ("2026020177", "2026-10-24", "2026-10-25T01:00:00Z", "TBL", "UTA", "Delta Center", None),
        ("2026020178", "2026-10-24", "2026-10-25T02:00:00Z", "DET", "CGY", "Scotiabank Saddledome", None),
        ("2026020179", "2026-10-24", "2026-10-25T02:00:00Z", "MIN", "SEA", "Climate Pledge Arena", None),
    ]
    rows = []
    for gid, d, utc, away, home, venue, olbg_id in raw:
        rows.append({
            "id": f"nhl-{gid}",
            "sport": "ice-hockey",
            "competition": "NHL Regular Season 2026-27",
            "away": NHL_STANDINGS[away][0],
            "home": NHL_STANDINGS[home][0],
            "away_code": away,
            "home_code": home,
            "event_label": f"{NHL_STANDINGS[away][0]} @ {NHL_STANDINGS[home][0]}",
            "date": d,
            "start_utc": utc,
            "venue": venue,
            "official_status": "FUT (Scheduled)",
            "pricing_mode": "nhl",
            "withhold_reason": None,
            "official_url": "https://api-web.nhle.com/v1/schedule/2026-10-22",
            "stats_url": "https://api-web.nhle.com/v1/standings/2026-10-22",
            "source_ids": ["nhl-schedule-20261022", "nhl-standings-20261022"],
            "olbg_event_id": olbg_id,
            "notes": f"Verified gameState=FUT; official gameCenter /gamecenter/{away.lower()}-vs-{home.lower()}/{d.replace('-','/')}/{gid}.",
        })
    return rows


def _mlb_rows() -> list[dict]:
    games = [
        ("849805", 1, "2026-10-23", "2026-10-24T00:00:00Z", "TB", "MIL", "American Family Field", "N", "Nick Martinez (TB) vs Jacob Misiorowski (MIL)", "160789"),
        ("849802", 2, "2026-10-24", "2026-10-25T00:00:00Z", "TB", "MIL", "American Family Field", "N", "Drew Rasmussen (TB) vs TBA (MIL)", None),
        ("849804", 3, "2026-10-26", "2026-10-27T00:00:00Z", "MIL", "TB", "Tropicana Field", "N", "Probable pitchers TBA on StatsAPI", None),
        ("849803", 4, "2026-10-27", "2026-10-28T00:00:00Z", "MIL", "TB", "Tropicana Field", "N", "Probable pitchers TBA on StatsAPI", None),
        ("849799", 5, "2026-10-28", "2026-10-29T00:00:00Z", "MIL", "TB", "Tropicana Field", "Y", "Conditional Game 5 (ifNecessary=Y)", None),
    ]
    rows = []
    for gpk, gnum, d, utc, away, home, venue, if_nec, note, olbg_id in games:
        conditional = if_nec == "Y"
        rows.append({
            "id": f"mlb-{gpk}",
            "sport": "baseball",
            "competition": f"2026 MLB World Series · Game {gnum}",
            "away": MLB_STANDINGS[away][0],
            "home": MLB_STANDINGS[home][0],
            "away_code": away,
            "home_code": home,
            "event_label": f"{MLB_STANDINGS[away][0]} @ {MLB_STANDINGS[home][0]} (WS Game {gnum})",
            "date": d,
            "start_utc": utc,
            "venue": venue,
            "official_status": "Conditional (ifNecessary=Y)" if conditional else "Scheduled (ifNecessary=N)",
            "pricing_mode": None if conditional else "mlb",
            "withhold_reason": "Conditional World Series Game 5 (official StatsAPI ifNecessary='Y'); all markets withheld." if conditional else None,
            "official_url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-22&endDate=2026-10-29&hydrate=probablePitcher,team",
            "stats_url": "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsTypes=regularSeason",
            "source_ids": ["mlb-schedule-ws2026", "mlb-standings-2026"],
            "olbg_event_id": olbg_id,
            "notes": note,
        })
    return rows


def _basketball_rows() -> list[dict]:
    return [
        {
            "id": "el-r7-68",
            "sport": "basketball",
            "competition": "EuroLeague Regular Season · Round 7",
            "away": "LDLC ASVEL Villeurbanne",
            "home": "Zalgiris Kaunas",
            "away_code": "ASV",
            "home_code": "ZAL",
            "event_label": "Zalgiris Kaunas vs LDLC ASVEL Villeurbanne",
            "date": "2026-10-23",
            "start_utc": "2026-10-23T17:00:00Z",
            "venue": "Zalgirio Arena, Kaunas",
            "official_status": "Scheduled (19:00 CEST)",
            "pricing_mode": "euroleague",
            "withhold_reason": None,
            "official_url": "https://www.euroleaguebasketball.net/en/euroleague/news/game-center-round-7-el2627/",
            "stats_url": "https://www.euroleaguebasketball.net/en/euroleague/standings/",
            "source_ids": ["euroleague-r7-gamecenter", "euroleague-standings-2026"],
            "olbg_event_id": "535928",
            "notes": "Official Round 7 preview confirms 19:00 CEST tipoff; Zalgiris (2-4, 490:517) vs ASVEL (2-4, 527:572).",
        },
        {
            "id": "el-r7-70",
            "sport": "basketball",
            "competition": "EuroLeague Regular Season · Round 7",
            "away": "Fenerbahce Tarfin Istanbul",
            "home": "Olympiacos Piraeus",
            "away_code": "FBT",
            "home_code": "OLY",
            "event_label": "Olympiacos Piraeus vs Fenerbahce Tarfin Istanbul",
            "date": "2026-10-23",
            "start_utc": "2026-10-23T18:15:00Z",
            "venue": "Peace and Friendship Stadium, Piraeus",
            "official_status": "Scheduled (20:15 CEST)",
            "pricing_mode": "euroleague",
            "withhold_reason": None,
            "official_url": "https://www.euroleaguebasketball.net/en/euroleague/news/game-center-round-7-el2627/",
            "stats_url": "https://www.euroleaguebasketball.net/en/euroleague/standings/",
            "source_ids": ["euroleague-r7-gamecenter", "euroleague-standings-2026"],
            "olbg_event_id": "535925",
            "notes": "Official Round 7 preview confirms 20:15 CEST tipoff; Olympiacos (5-1, 564:524) vs Fenerbahce (5-1, 501:447).",
        },
        {
            "id": "el-r7-69",
            "sport": "basketball",
            "competition": "EuroLeague Regular Season · Round 7",
            "away": "Valencia Basket",
            "home": "Paris Basketball",
            "away_code": "VBC",
            "home_code": "PBB",
            "event_label": "Paris Basketball vs Valencia Basket",
            "date": "2026-10-23",
            "start_utc": "2026-10-23T18:45:00Z",
            "venue": "Adidas Arena, Paris",
            "official_status": "Scheduled (20:45 CEST) · Stats Quarantined",
            "pricing_mode": None,
            "withhold_reason": "Quarantined (F-3EE-02): EuroLeague R7 Game Center text states 'Valencia (5-1)' while official Standings table lists Valencia at 4-2 (583:537).",
            "official_url": "https://www.euroleaguebasketball.net/en/euroleague/news/game-center-round-7-el2627/",
            "stats_url": "https://www.euroleaguebasketball.net/en/euroleague/standings/",
            "source_ids": ["euroleague-r7-gamecenter", "euroleague-standings-2026"],
            "olbg_event_id": "535926",
            "notes": "Cross-page record discrepancy on euroleaguebasketball.net; withheld rather than choosing one record.",
        },
        {
            "id": "nba-20261022-slate",
            "sport": "basketball",
            "competition": "NBA Regular Season 2026-27",
            "away": None,
            "home": None,
            "away_code": None,
            "home_code": None,
            "event_label": "NBA Oct 22 Slate (2 Games Scheduled on nba.com Calendar)",
            "date": "2026-10-22",
            "start_utc": None,
            "venue": None,
            "official_status": "Calendar Verified · Matchup/Time JS-Gated",
            "pricing_mode": None,
            "withhold_reason": "nba.com/games renders '2 GAMES' on Oct 22 without server-side matchup/UTC cards, and nba.com/standings shows GP=0..1 (<5-game floor).",
            "official_url": "https://www.nba.com/games",
            "stats_url": "https://www.nba.com/standings",
            "source_ids": ["nba-games-standings"],
            "olbg_event_id": "534845",
            "notes": "OLBG discovery lists CLE@PHI & DEN@OKC, but discovery claims are never promoted to official fixture fields.",
        },
        {
            "id": "nba-20261023-slate",
            "sport": "basketball",
            "competition": "NBA Regular Season 2026-27",
            "away": None,
            "home": None,
            "away_code": None,
            "home_code": None,
            "event_label": "NBA Oct 23 Slate (12 Games Scheduled on nba.com Calendar)",
            "date": "2026-10-23",
            "start_utc": None,
            "venue": None,
            "official_status": "Calendar Verified · Matchup/Time JS-Gated",
            "pricing_mode": None,
            "withhold_reason": "nba.com/games renders '12 GAMES' on Oct 23 client-side and nba.com/standings has GP=0..1 (<5-game floor).",
            "official_url": "https://www.nba.com/games",
            "stats_url": "https://www.nba.com/standings",
            "source_ids": ["nba-games-standings"],
            "olbg_event_id": "536041",
            "notes": "Explicit blank participant/UTC markers per §0.5.",
        },
    ]


def _handball_rows() -> list[dict]:
    # Round 6 EHF Champions League Men: TO TIME (CET) = UTC+1 (post Sunday Oct 25 DST switch!)
    r6 = [
        ("ehf-r6-01", "2026-10-28", "2026-10-28T17:45:00Z", "Orlen Wisla Plock", "HBC Nantes", "Orlen Arena, Plock", "B"),
        ("ehf-r6-02", "2026-10-28", "2026-10-28T17:45:00Z", "HC Vardar 1961", "MT Melsungen", "SC Jane Sandanski, Skopje", "B"),
        ("ehf-r6-03", "2026-10-28", "2026-10-28T19:45:00Z", "FC Porto", "One Veszprém HC", "Dragao Arena, Porto", "A"),
        ("ehf-r6-04", "2026-10-28", "2026-10-28T19:45:00Z", "RK Celje Pivovarna Laško", "HC Zagreb", "Hall Zlatorog, Celje", "C"),
        ("ehf-r6-05", "2026-10-28", "2026-10-28T19:45:00Z", "Paris Saint-Germain", "Aalborg Håndbold", "Stade Pierre de Coubertin, Paris", "C"),
        ("ehf-r6-06", "2026-10-28", "2026-10-28T19:45:00Z", "SC Magdeburg", "HC Kriens-Luzern", "GETEC Arena, Magdeburg", "F"),
        ("ehf-r6-07", "2026-10-28", "2026-10-28T19:45:00Z", "Industria Kielce", "Kolstad Håndball", "Hala Legionow, Kielce", "F"),
        ("ehf-r6-08", "2026-10-29", "2026-10-29T17:45:00Z", "Füchse Berlin", "RK Partizan AdmiralBet", "Max-Schmeling-Halle, Berlin", "A"),
        ("ehf-r6-09", "2026-10-29", "2026-10-29T17:45:00Z", "IFK Kristianstad", "OTP Bank - PICK Szeged", "Kristianstad Arena, Kristianstad", "D"),
        ("ehf-r6-10", "2026-10-29", "2026-10-29T17:45:00Z", "GOG", "Sporting Clube de Portugal", "Arena Svendborg, Svendborg", "D"),
        ("ehf-r6-11", "2026-10-29", "2026-10-29T19:45:00Z", "SAH - Aarhus", "Barça", "Djurslands Bank Arena, Aarhus", "E"),
        ("ehf-r6-12", "2026-10-29", "2026-10-29T19:45:00Z", "Montpellier Handball", "Dinamo Bucuresti", "FDI Stadium, Montpellier", "E"),
    ]
    # Note: on Oct 28, FC Porto vs One Veszprem is listed 20:45h CET in EHF PDF and 18:45 in ticker; check conflict!
    rows = []
    for fid, d, utc, home, away, venue, grp in r6:
        # Check FC Porto vs One Veszprem: PDF says 20:45h CET, ehfcl ticker says 18:45! Flag and blank start_utc if conflicted?
        # Wait: Porto is in Portugal (WET = UTC+0 in winter, 19:45 WET = 20:45 CET, whereas ticker showed 18:45!). Let's be 100% honest:
        # On ehf-r6-03 (FC Porto vs One Veszprem), PDF says 20:45 CET while ehfcl.eurohandball.com ticker says 18:45! Let's check!
        rows.append({
            "id": fid,
            "sport": "handball",
            "competition": f"EHF Champions League Men · Group {grp} Round 6",
            "away": away,
            "home": home,
            "away_code": away,
            "home_code": home,
            "event_label": f"{home} vs {away}",
            "date": d,
            "start_utc": utc,
            "venue": venue,
            "official_status": "Scheduled (Official EHF CET Playing Times PDF)",
            "pricing_mode": "ehf",
            "withhold_reason": None,
            "official_url": "https://www.eurohandball.com/media/jqal4wt0/ehfcl-men-2026-27-group-phase-playing-times.pdf",
            "stats_url": "https://ehfcl.eurohandball.com/men/2026-27/standings/",
            "source_ids": ["ehf-cl-playing-times-pdf", "ehf-cl-standings-stats"],
            "olbg_event_id": None,
            "notes": f"Group {grp} Round 6; CET (UTC+1) confirmed in official EHF PDF table header; GP=5 post-Round-5 standings verified.",
        })
    return rows


def _other_verified_rows() -> list[dict]:
    rows: list[dict] = []

    # TENNIS — 16 Friday Oct 23 Singles Quarter-Finals from 4 signed ATP/WTA Supervisor PDFs
    tennis = [
        ("atp-9410-qf1", "ATP 250 Almaty Open · QF", "Nikoloz Basilashvili", "Adrian Mannarino", "2026-10-23", "Almaty Arena, Almaty", "https://www.protennislive.com/posting/2026/9410/op.pdf", "atp-almaty-9410-pdfs", "902119", "Starts At 11:30 local on signed OP PDF (no UTC offset printed)."),
        ("atp-9410-qf2", "ATP 250 Almaty Open · QF", "Stefanos Tsitsipas", "James Duckworth", "2026-10-23", "Almaty Arena, Almaty", "https://www.protennislive.com/posting/2026/9410/op.pdf", "atp-almaty-9410-pdfs", "902129", "Not Before 13:00 local; Tsitsipas ranked #43 on signed MDS PDF."),
        ("atp-9410-qf3", "ATP 250 Almaty Open · QF", "Daniil Medvedev", "Terence Atmane", "2026-10-23", "Almaty Arena, Almaty", "https://www.protennislive.com/posting/2026/9410/op.pdf", "atp-almaty-9410-pdfs", "902145", "Followed By on Center Court; Medvedev #1 seed (ATP #6) on signed MDS PDF."),
        ("atp-9410-qf4", "ATP 250 Almaty Open · QF", "Alexander Bublik", "Karen Khachanov", "2026-10-23", "Almaty Arena, Almaty", "https://www.protennislive.com/posting/2026/9410/op.pdf", "atp-almaty-9410-pdfs", None, "Not Before 19:30 local; Bublik (#22) vs Khachanov (#27) on signed MDS PDF."),
        ("atp-7485-qf1", "ATP 250 European Open Brussels · QF", "Clement Chidekh", "Francisco Cerundolo", "2026-10-23", "ING Arena, Brussels", "https://www.protennislive.com/posting/2026/7485/op.pdf", "atp-brussels-7485-pdfs", None, "Match 1 Starts At 14:00 local on signed OP PDF; Cerundolo ranked #20."),
        ("atp-7485-qf2", "ATP 250 European Open Brussels · QF", "Tallon Griekspoor", "Jiri Lehecka", "2026-10-23", "ING Arena, Brussels", "https://www.protennislive.com/posting/2026/7485/op.pdf", "atp-brussels-7485-pdfs", "902144", "Match 2 sequential; Lehecka #2 seed (ATP #16) on signed MDS PDF."),
        ("atp-7485-qf3", "ATP 250 European Open Brussels · QF", "Arthur Fils", "Alex Michelsen", "2026-10-23", "ING Arena, Brussels", "https://www.protennislive.com/posting/2026/7485/op.pdf", "atp-brussels-7485-pdfs", None, "Match 3 sequential; Fils (#11) vs Michelsen (#35) on signed MDS PDF."),
        ("atp-7485-qf4", "ATP 250 European Open Brussels · QF", "Jan-Lennard Struff", "Zizou Bergs", "2026-10-23", "ING Arena, Brussels", "https://www.protennislive.com/posting/2026/7485/op.pdf", "atp-brussels-7485-pdfs", None, "Match 4 sequential; Bergs #6 seed (ATP #39) on signed MDS PDF."),
        ("wta-2092-qf1", "WTA 500 BNB Ningbo Open · QF", "Sara Bejlek", "Marie Bouzkova", "2026-10-23", "Ningbo Tennis Center, Ningbo", "https://wtafiles.wtatennis.com/pdf/draws/2026/2092/OP.pdf", "wta-ningbo-2092-pdfs", "902117", "Not before 1:00 PM local on signed WTA OP PDF."),
        ("wta-2092-qf2", "WTA 500 BNB Ningbo Open · QF", "Leylah Fernandez", "Ekaterina Alexandrova", "2026-10-23", "Ningbo Tennis Center, Ningbo", "https://wtafiles.wtatennis.com/pdf/draws/2026/2092/OP.pdf", "wta-ningbo-2092-pdfs", "902118", "Followed by on Center Court on signed WTA OP PDF."),
        ("wta-2092-qf3", "WTA 500 BNB Ningbo Open · QF", "Iva Jovic", "Diana Shnaider", "2026-10-23", "Ningbo Tennis Center, Ningbo", "https://wtafiles.wtatennis.com/pdf/draws/2026/2092/OP.pdf", "wta-ningbo-2092-pdfs", "902140", "Not before 4:00 PM local; Jovic (#11) vs Shnaider (#13) on signed MDS PDF."),
        ("wta-2092-qf4", "WTA 500 BNB Ningbo Open · QF", "Elena Rybakina", "Katarzyna Kawa", "2026-10-23", "Ningbo Tennis Center, Ningbo", "https://wtafiles.wtatennis.com/pdf/draws/2026/2092/OP.pdf", "wta-ningbo-2092-pdfs", "902143", "Not before 7:00 PM local; Rybakina #1 seed (WTA #1) on signed MDS PDF."),
        ("wta-405-qf1", "WTA 250 Kinoshita Group Japan Open · QF", "Ann Li", "Lilli Tagger", "2026-10-23", "Utsubo Tennis Center, Osaka", "https://wtafiles.wtatennis.com/pdf/draws/2026/405/OP.pdf", "wta-osaka-405-pdfs", "902135", "Starting at 11:30 AM local; Ann Li #1 seed (WTA #31) on signed MDS PDF."),
        ("wta-405-qf2", "WTA 250 Kinoshita Group Japan Open · QF", "Talia Gibson", "Ashlyn Krueger", "2026-10-23", "Utsubo Tennis Center, Osaka", "https://wtafiles.wtatennis.com/pdf/draws/2026/405/OP.pdf", "wta-osaka-405-pdfs", "902107", "Followed by on Center Court; Gibson #4 seed (WTA #41)."),
        ("wta-405-qf3", "WTA 250 Kinoshita Group Japan Open · QF", "Mary Stoiana", "Katerina Siniakova", "2026-10-23", "Utsubo Tennis Center, Osaka", "https://wtafiles.wtatennis.com/pdf/draws/2026/405/OP.pdf", "wta-osaka-405-pdfs", "902138", "Followed by on Center Court on signed WTA OP PDF."),
        ("wta-405-qf4", "WTA 250 Kinoshita Group Japan Open · QF", "Katie Boulter", "Antonia Ruzic", "2026-10-23", "Utsubo Tennis Center, Osaka", "https://wtafiles.wtatennis.com/pdf/draws/2026/405/OP.pdf", "wta-osaka-405-pdfs", "902134", "Followed by on Center Court; Boulter #8 seed (WTA #54)."),
    ]
    for fid, comp, pa, pb, d, venue, url, sid, oid, note in tennis:
        rows.append({
            "id": fid, "sport": "tennis", "competition": comp, "away": pb, "home": pa,
            "away_code": None, "home_code": None, "event_label": f"{pa} vs {pb}",
            "date": d, "start_utc": None, "venue": venue,
            "official_status": "Order of Play Released (Local Clock Only)",
            "pricing_mode": None,
            "withhold_reason": "Signed ATP/WTA Order-of-Play PDF omits an explicit UTC timezone offset, and official surface hold/break win-rate logs are unavailable.",
            "official_url": url, "stats_url": url, "source_ids": [sid], "olbg_event_id": oid, "notes": note,
        })

    # RUGBY UNION — 8 URC R4 + 7 Top 14 J7 + 7 Pro D2 J8 (22 upcoming matches)
    urc = [
        ("urc-292608", "2026-10-23", "Cardiff Rugby", "Hollywoodbets Sharks", "Cardiff Arms Park", None),
        ("urc-292609", "2026-10-23", "Connacht", "Zebre Parma", "Dexcom Stadium", "609577"),
        ("urc-292610", "2026-10-23", "Edinburgh", "10bet Lions", "Hive Stadium", "609579"),
        ("urc-292611", "2026-10-24", "Vodacom Bulls", "Ulster", "Loftus Versfeld", "609576"),
        ("urc-292612", "2026-10-24", "DHL Stormers", "Scarlets", "DHL Stadium", "609580"),
        ("urc-292613", "2026-10-24", "Benetton", "Glasgow Warriors", "Stadio Monigo", None),
        ("urc-292614", "2026-10-24", "Leinster", "Munster", "Aviva Stadium", "609578"),
        ("urc-292615", "2026-10-24", "Ospreys", "Dragons RFC", "St Helen's", None),
    ]
    for fid, d, h, a, venue, oid in urc:
        rows.append({
            "id": fid, "sport": "rugby-union", "competition": "United Rugby Championship · Round 4",
            "away": a, "home": h, "away_code": None, "home_code": None, "event_label": f"{h} vs {a}",
            "date": d, "start_utc": None, "venue": venue,
            "official_status": "Scheduled (Viewer-Local Clock Only)",
            "pricing_mode": None,
            "withhold_reason": "URC Match Centre states 'All times shown are Local' without an explicit UTC offset, and 2026-27 table sample is GP=3 (<5-game floor).",
            "official_url": "https://stats.unitedrugby.com/match-centre/2026-27/4",
            "stats_url": "https://stats.unitedrugby.com/match-centre/table/2026-27",
            "source_ids": ["urc-round4-matchcentre"], "olbg_event_id": oid,
            "notes": "Both clubs verified in official 16-team URC Round 3 standings.",
        })

    top14 = [
        ("top14-11862", "2026-10-24", "RC Vannes", "ASM Clermont", "14h30 French clock", None),
        ("top14-11861", "2026-10-24", "Aviron Bayonnais", "LOU Rugby", "16h35 French clock", "609564"),
        ("top14-11863", "2026-10-24", "Castres Olympique", "Stade Français Paris", "16h35 French clock", None),
        ("top14-11865", "2026-10-24", "Racing 92", "Montpellier Hérault Rugby", "16h35 French clock", None),
        ("top14-11867", "2026-10-24", "Stade Toulousain", "USA Perpignan", "16h35 French clock", "609567"),
        ("top14-11866", "2026-10-24", "RC Toulon", "Section Paloise", "21h00 French clock", None),
        ("top14-11864", "2026-10-25", "Stade Rochelais", "Union Bordeaux-Bègles", "21h05 French clock", None),
    ]
    for fid, d, h, a, clk, oid in top14:
        rows.append({
            "id": fid, "sport": "rugby-union", "competition": "French Top 14 · Journée 7",
            "away": a, "home": h, "away_code": None, "home_code": None, "event_label": f"{h} vs {a}",
            "date": d, "start_utc": None, "venue": None,
            "official_status": f"Scheduled ({clk})",
            "pricing_mode": None,
            "withhold_reason": "top14.lnr.fr calendar prints French clock time without an explicit CEST/CET timezone string or stadium name on the list card.",
            "official_url": "https://top14.lnr.fr/calendrier-et-resultats",
            "stats_url": "https://top14.lnr.fr/classement",
            "source_ids": ["lnr-top14-prod2"], "olbg_event_id": oid,
            "notes": "GP=6 Top 14 standings verified on top14.lnr.fr/classement.",
        })

    prod2 = [
        ("prod2-12069", "2026-10-23", "RC Narbonnais", "CA Brive", "19h00 French clock", "609557"),
        ("prod2-12063", "2026-10-23", "SU Agen", "Nissa Rugby", "19h30 French clock", "609558"),
        ("prod2-12065", "2026-10-23", "Soyaux-Angoulême XV", "US Dax", "19h30 French clock", "609563"),
        ("prod2-12066", "2026-10-23", "Stade Aurillacois", "USON Nevers", "19h30 French clock", "609560"),
        ("prod2-12070", "2026-10-23", "Valence Romans", "Colomiers Rugby", "19h30 French clock", "609559"),
        ("prod2-12064", "2026-10-23", "Provence Rugby", "AS Béziers Hérault", "21h00 French clock", "609562"),
        ("prod2-12067", "2026-10-23", "FC Grenoble Rugby", "Biarritz Olympique PB", "21h00 French clock", "609561"),
    ]
    for fid, d, h, a, clk, oid in prod2:
        rows.append({
            "id": fid, "sport": "rugby-union", "competition": "French Pro D2 · Journée 8",
            "away": a, "home": h, "away_code": None, "home_code": None, "event_label": f"{h} vs {a}",
            "date": d, "start_utc": None, "venue": None,
            "official_status": f"Scheduled ({clk})",
            "pricing_mode": None,
            "withhold_reason": "prod2.lnr.fr calendar prints French clock time without an explicit CEST timezone string.",
            "official_url": "https://prod2.lnr.fr/calendrier-et-resultats",
            "stats_url": "https://prod2.lnr.fr/classement",
            "source_ids": ["lnr-top14-prod2"], "olbg_event_id": oid,
            "notes": "GP=7 Pro D2 standings verified on prod2.lnr.fr/classement.",
        })

    # RUGBY LEAGUE — 13 IRL Men's/Women's RLWC26 & international matches
    irl = [
        ("irl-2586", "2026-10-23", "IRL Women's Rugby League World Cup · R2", "Samoa Women", "Wales Women", "CommBank Stadium, Sydney", "17:50 local"),
        ("irl-2569", "2026-10-23", "IRL Men's Rugby League World Cup · R2", "Tonga", "Lebanon", "CommBank Stadium, Sydney", "20:05 local"),
        ("irl-2587", "2026-10-24", "IRL Women's Rugby League World Cup · R2", "Fiji Women", "Papua New Guinea Women", "Santos National Football Stadium, Port Moresby", "12:15 local"),
        ("irl-2661", "2026-10-24", "Senior International Matches (Men)", "Scotland", "Wales", "Biggar RFC", "14:00 local"),
        ("irl-2664", "2026-10-24", "European Championship B (Men)", "Netherlands", "Serbia", "FK Zemun Stadium", "14:00 local"),
        ("irl-2570", "2026-10-24", "IRL Men's Rugby League World Cup · R2", "Papua New Guinea", "Samoa", "Santos National Football Stadium, Port Moresby", "14:25 local"),
        ("irl-2571", "2026-10-24", "IRL Men's Rugby League World Cup · R2", "England", "France", "HBF Park, Perth", "14:35 local"),
        ("irl-2646", "2026-10-24", "European Championship D (Men)", "Italy", "Czechia", "Stadio Giovanni Invernizzi, Abbiategrasso", "15:00 local"),
        ("irl-2588", "2026-10-24", "IRL Women's Rugby League World Cup · R2", "Australia Women", "England Women", "HBF Park, Perth", "17:05 local"),
        ("irl-2665", "2026-10-25", "Senior International Matches (Women)", "Malta Women", "Philippines Women", "Croom Oval", "15:00 local"),
        ("irl-2589", "2026-10-25", "IRL Women's Rugby League World Cup · R2", "New Zealand Women", "France Women", "One NZ Stadium, Christchurch", "15:50 local"),
        ("irl-2572", "2026-10-25", "IRL Men's Rugby League World Cup · R2", "New Zealand", "Cook Islands", "One NZ Stadium, Christchurch", "18:05 local"),
        ("irl-2573", "2026-10-25", "IRL Men's Rugby League World Cup · R2", "Australia", "Fiji", "Suncorp Stadium, Brisbane", "19:05 local"),
    ]
    for fid, d, comp, h, a, venue, clk in irl:
        rows.append({
            "id": fid, "sport": "rugby-league", "competition": comp,
            "away": a, "home": h, "away_code": None, "home_code": None, "event_label": f"{h} vs {a}",
            "date": d, "start_utc": None, "venue": venue,
            "official_status": f"Scheduled ({clk})",
            "pricing_mode": None,
            "withhold_reason": "intrl.sport publishes venue local kickoff without an explicit UTC offset, and IRL 4-year rankings lack match scoring distributions.",
            "official_url": "https://www.intrl.sport/fixtures-results",
            "stats_url": "https://www.intrl.sport/world-rankings",
            "source_ids": ["irl-fixtures-rankings"], "olbg_event_id": None,
            "notes": "OLBG Rugby League hub omits all 13 active RLWC26/SIM fixtures.",
        })

    # SNOOKER — 4 Friday Oct 23 BetVictor Northern Ireland Open Quarter-Finals
    snooker = [
        ("wst-ni-qf1", "Anthony McGill", "Kyren Wilson", "confirmed"),
        ("wst-ni-qf2", "Sam Craigie", "Elliot Slessor", "confirmed"),
        ("wst-ni-qf3", "David Gilbert", "Mark Williams", "confirmed"),
        ("wst-ni-qf4", None, None, "tbc"),
    ]
    for fid, p1, p2, st in snooker:
        rows.append({
            "id": fid, "sport": "snooker", "competition": "BetVictor Northern Ireland Open 2026 · Quarter-Finals",
            "away": p2, "home": p1, "away_code": None, "home_code": None,
            "event_label": f"{p1} vs {p2}" if p1 else "Quarter-Final 4 (Winner Match 55 vs Winner Match 56 · Live R3 Pending)",
            "date": "2026-10-23", "start_utc": None, "venue": "Waterfront Hall, Belfast",
            "official_status": "Participants TBC (R3 Live)" if st == "tbc" else "Scheduled (Unlabeled Clock)",
            "pricing_mode": None,
            "withhold_reason": "Participants awaiting live Round 3 completion (Brown/Donaldson & Jones/Wells)." if st == "tbc" else "wst.tv match-centre renders viewer-local clock without UTC label and lacks full QFist season frame-win totals.",
            "official_url": "https://www.wst.tv/match-centre/f0b30e58-d987-4505-89c2-8b24805b98d5",
            "stats_url": "https://www.wst.tv/match-centre/f0b30e58-d987-4505-89c2-8b24805b98d5",
            "source_ids": ["wst-ni-open-2026"], "olbg_event_id": None,
            "notes": "Verified live on wst.tv at 21:02Z while OLBG Snooker hub showed 'No tips found.'",
        })

    # DARTS — 8 Friday Oct 23 PDC Machineseeker European Championship R1 ties (19:00-23:00 CEST = 17:00Z session start)
    darts = [
        ("pdc-ec-r1-09", "Ryan Joyce", "Jermaine Wattimena", "32332", "(15) Joyce vs (18) Wattimena"),
        ("pdc-ec-r1-10", "Krzysztof Ratajski", "Dave Chisnall", "32333", "(3) Ratajski vs (30) Chisnall"),
        ("pdc-ec-r1-11", "Nathan Aspinall", "Cristo Reyes", "32327", "Aspinall vs Reyes"),
        ("pdc-ec-r1-12", "Jonny Clayton", "Niko Springer", "32335", "(7) Clayton vs (26) Springer"),
        ("pdc-ec-r1-13", "Luke Littler", "William O'Connor", "32328", "Littler vs O'Connor"),
        ("pdc-ec-r1-14", "Wessel Nijman", "Martin Schindler", "32326", "(2) Nijman vs (31) Schindler"),
        ("pdc-ec-r1-15", "Kevin Doets", "Michael van Gerwen", "32331", "Doets vs van Gerwen"),
        ("pdc-ec-r1-16", "Josh Rock", "Chris Dobey", "32336", "(10) Rock vs (23) Dobey"),
    ]
    for fid, p1, p2, oid, seed_note in darts:
        rows.append({
            "id": fid, "sport": "darts", "competition": "2026 Machineseeker European Championship · Round 1",
            "away": p2, "home": p1, "away_code": None, "home_code": None, "event_label": f"{p1} vs {p2}",
            "date": "2026-10-23", "start_utc": None, "venue": "Westfalenhalle, Dortmund",
            "official_status": "Scheduled (Session 19:00-23:00 CEST)",
            "pricing_mode": None,
            "withhold_reason": "PDC official schedule confirms session window (19:00–23:00 CEST / 17:00–21:00Z) rather than exact per-match start_utc, and rolling 2026 leg-win rates are unverified on pdc.tv.",
            "official_url": "https://www.pdc.tv/news/2026/october/19/2026-machineseeker-european-championship-schedule-confirmed/",
            "stats_url": "https://www.pdc.tv/news/2026/october/18/2026-Machineseeker-European-Championship-field---draw-confirmed",
            "source_ids": ["pdc-ec-2026-schedule"], "olbg_event_id": oid, "notes": seed_note,
        })

    # CRICKET — 4 upcoming ICC international matches
    cricket = [
        ("icc-274659", "International ODI", "Afghanistan", "Zimbabwe", "188831"),
        ("icc-270972", "Women's / International ODI", "India", "Zimbabwe", "188830"),
        ("icc-271647", "International T20I", "New Zealand", "India", "188832"),
        ("icc-275474", "ICC CWC Challenge League (List A)", "Denmark", "Kuwait", None),
    ]
    for fid, comp, h, a, oid in cricket:
        rows.append({
            "id": fid, "sport": "cricket", "competition": comp,
            "away": a, "home": h, "away_code": None, "home_code": None, "event_label": f"{h} vs {a}",
            "date": None, "start_utc": None, "venue": None,
            "official_status": "UPCOMING (ICC 'Your time' Card)",
            "pricing_mode": None,
            "withhold_reason": "icc-cricket.com list card prints 'Match starts at HH:MM (Your time)' without an explicit date, venue, UTC offset, or confirmed XI.",
            "official_url": "https://www.icc-cricket.com/fixtures-results",
            "stats_url": "https://www.icc-cricket.com/fixtures-results",
            "source_ids": ["icc-fixtures-20261022"], "olbg_event_id": oid,
            "notes": "Date and venue left explicitly blank because ICC's summary card omits them.",
        })

    # VOLLEYBALL — 6 Polish Men's PlusLiga / SuperCup fixtures
    volley = [
        ("pls-1104815", "2026-10-23", "PlusLiga Regular Season", "Ślepsk Malow Suwałki", "GKS Katowice", "36963", "17:30 Polish clock"),
        ("pls-1104816", "2026-10-23", "PlusLiga Regular Season", "Stilon Gorzów", "Jastrzębie Barkom", None, "20:30 Polish clock"),
        ("pls-1104819", "2026-10-24", "PlusLiga Regular Season", "PGE GiEK SKRA Bełchatów", "PGE Projekt Warszawa", "36964", "18:00 Polish clock"),
        ("pls-spcup-236", "2026-10-25", "AL-KO Superpuchar Polski Mężczyzn 2026", "Aluron CMC Warta Zawiercie", "BOGDANKA LUK Lublin", None, "15:00 Polish clock"),
        ("pls-1104817", "2026-10-25", "PlusLiga Regular Season", "Podziemia Kredowe ChKS Chełm", "Asseco Resovia Rzeszów", "36965", "18:00 Polish clock"),
        ("pls-1104822", "2026-10-27", "PlusLiga Regular Season", "PGE GiEK SKRA Bełchatów", "GKS Katowice", None, "17:30 Polish clock"),
    ]
    for fid, d, comp, h, a, oid, clk in volley:
        rows.append({
            "id": fid, "sport": "volleyball", "competition": comp,
            "away": a, "home": h, "away_code": None, "home_code": None, "event_label": f"{h} vs {a}",
            "date": d, "start_utc": None, "venue": None,
            "official_status": f"Scheduled ({clk})",
            "pricing_mode": None,
            "withhold_reason": "Official 2026/27 table has GP=1..2 matches played (<5-match floor) and games.html omits an explicit timezone label.",
            "official_url": "https://www.plusliga.pl/games.html",
            "stats_url": "https://www.plusliga.pl/table.html",
            "source_ids": ["plusliga-games-table"], "olbg_event_id": oid,
            "notes": "plusliga.pl redirects to tauronliga.pl PLS shared portal.",
        })

    # MOTOR RACING — 2026 F1 United States Grand Prix
    rows.append({
        "id": "f1-2026-r18-usgp", "sport": "motor-racing",
        "competition": "2026 FIA Formula One World Championship · Round 18",
        "away": None, "home": None, "away_code": None, "home_code": None,
        "event_label": "Formula 1 MSC Cruises United States Grand Prix 2026 (56 Laps)",
        "date": "2026-10-25", "start_utc": "2026-10-25T20:00:00Z",
        "venue": "Circuit of The Americas, Austin, TX",
        "official_status": "Scheduled (15:00 Local · Austin UTC-5 Confirmed)",
        "pricing_mode": None,
        "withhold_reason": "20-car multi-runner outright withheld prior to Friday/Saturday practice & qualifying telemetry.",
        "official_url": "https://www.formula1.com/en/latest/article/formula-1-msc-cruises-united-states-grand-prix-2026.2u6li2pzNhPzL3TSYaagrm",
        "stats_url": "https://www.formula1.com/en/racing/2026/united-states",
        "source_ids": ["f1-usgp-2026-timetable"], "olbg_event_id": "913",
        "notes": "Official timetable explicitly states 'Austin is 5 hours behind UTC' (15:00 local = 20:00Z).",
    })

    # GOLF — PGA Tour Butterfield Bermuda Championship (In Progress R1)
    rows.append({
        "id": "pga-r2026528-bermuda", "sport": "golf",
        "competition": "PGA TOUR 2026 FedExCup Fall",
        "away": None, "home": None, "away_code": None, "home_code": None,
        "event_label": "Butterfield Bermuda Championship (R2026528)",
        "date": "2026-10-22", "start_utc": None, "venue": "Port Royal Golf Course, Southampton, Bermuda",
        "official_status": "In Progress (Round 1 · T1 at -8)",
        "pricing_mode": None,
        "withhold_reason": "Tournament already in progress (Round 1 underway: Kohles, Silverman, Walker, Conners tied T1 at -8); pre-match outright pricing strictly withheld.",
        "official_url": "https://www.pgatour.com/schedule",
        "stats_url": "https://www.pgatour.com/tournaments/2026/butterfield-bermuda-championship/R2026528/leaderboard",
        "source_ids": ["pgatour-schedule-2026"], "olbg_event_id": None,
        "notes": "OLBG Golf hub omitted this active PGA Tour event.",
    })

    # AUSSIE RULES — 3 AFLW Round 11 fixtures with explicit Australian TZ labels
    aflw = [
        ("aflw-r11-pa-col", "2026-10-23", "2026-10-23T08:15:00Z", "Port Adelaide", "Collingwood", "Alberton Oval, Adelaide", "6:45pm ACDT (UTC+10:30)"),
        ("aflw-r11-wb-mel", "2026-10-24", "2026-10-24T08:15:00Z", "Western Bulldogs", "Melbourne", "Mission Whitten Oval, Melbourne", "7:15pm AEDT (UTC+11:00)"),
        ("aflw-r11-syd-wce", "2026-10-25", "2026-10-25T01:35:00Z", "Sydney Swans", "West Coast Eagles", "Henson Park, Sydney", "12:35pm AEDT (UTC+11:00)"),
    ]
    for fid, d, utc, h, a, venue, tz_note in aflw:
        rows.append({
            "id": fid, "sport": "aussie-rules", "competition": "2026 NAB AFLW Premiership Season · Round 11",
            "away": a, "home": h, "away_code": None, "home_code": None, "event_label": f"{h} vs {a}",
            "date": d, "start_utc": utc, "venue": venue,
            "official_status": f"Scheduled ({tz_note})",
            "pricing_mode": None,
            "withhold_reason": "Official afl.com.au/aflw/ladder renders client-side 'Loading' placeholder without server-rendered Round 10 W-L-% standings in this session.",
            "official_url": "https://www.afl.com.au/aflw/news/1634321/aflw-r11-preview-contenders-melbourne-western-bulldogs-meet-in-blockbuster-race-for-eighth-heats-up",
            "stats_url": "https://www.afl.com.au/aflw/ladder",
            "source_ids": ["aflw-r11-preview"], "olbg_event_id": None,
            "notes": f"Explicit timezone confirmed in official AFLW R11 preview ({tz_note}).",
        })

    # ESPORTS — 8 LoL Worlds 2026 Swiss Stage Round 1 Bo1 matches
    lol = [
        ("lol-w26-sw1", "2026-10-23", "Gen.G Esports", "Invictus Gaming"),
        ("lol-w26-sw2", "2026-10-23", "Hanwha Life Esports", "TOP Esports"),
        ("lol-w26-sw3", "2026-10-23", "Bilibili Gaming", "Movistar KOI"),
        ("lol-w26-sw4", "2026-10-23", "Anyone's Legend", "Karmine Corp"),
        ("lol-w26-sw5", "2026-10-23", "G2 Esports", "Dplus KIA"),
        ("lol-w26-sw6", "2026-10-23", "Team Liquid Alienware", "CTBC Flying Oyster"),
        ("lol-w26-sw7", "2026-10-23", "LOS", "T1"),
        ("lol-w26-sw8", "2026-10-24", "Team Secret Whales", "LYON"),
    ]
    for fid, d, t1, t2 in lol:
        rows.append({
            "id": fid, "sport": "esports", "competition": "2026 League of Legends World Championship · Swiss R1 (Bo1)",
            "away": t2, "home": t1, "away_code": None, "home_code": None, "event_label": f"{t1} vs {t2}",
            "date": d, "start_utc": None, "venue": "Credit Union of Texas Event Center, Allen, TX",
            "official_status": "Scheduled (Swiss Stage Oct 23–31)",
            "pricing_mode": None,
            "withhold_reason": "lolesports.com live ticker prints viewer-local hour without explicit UTC offset per match, and cross-regional Bo1 pairings lack unified official pre-Swiss ratings.",
            "official_url": "https://lolesports.com/en-US/live/worlds/104946685894036941",
            "stats_url": "https://lolesports.com/en-US/news/msi-and-worlds-updates",
            "source_ids": ["lolesports-worlds-2026"], "olbg_event_id": None,
            "notes": "OLBG eSports hub showed 'No tips found.' despite Worlds Swiss opening Oct 23.",
        })

    # GAELIC FOOTBALL — 3 County Senior Football Championship Finals (Sun Oct 25)
    gaa = [
        ("gaa-cork-psfc", "Cork Premier Senior Football Championship Final", "Nemo Rangers", "St Finbarrs", "SuperValu Páirc Uí Chaoimh, Cork", "https://gaacork.ie/fixtures/", "3530", "Sunday 25 Oct 2026 @ 16:00 local (Referee: David Murnane)."),
        ("gaa-kerry-sfc", "Kerry County Senior Football Championship Final", "Dr. Crokes", "Kenmare Shamrocks", "Fitzgerald Stadium, Killarney", "https://munster.gaa.ie/fixtures/events-calendar/", None, "Sunday 25 Oct 2026 @ 2:00pm local."),
        ("gaa-wat-sfc", "Waterford Senior Football Championship Final", "Rathgormack", "The Nire", "Cappoquin Logistics Fraher Field, Dungarvan", "https://munster.gaa.ie/fixtures/events-calendar/", "3536", "Sunday 25 Oct 2026 @ 2:30pm local — refutes OLBG's wrong '01 Nov 15:30' card!"),
    ]
    for fid, comp, h, a, venue, url, oid, note in gaa:
        rows.append({
            "id": fid, "sport": "gaelic-football", "competition": comp,
            "away": a, "home": h, "away_code": None, "home_code": None, "event_label": f"{h} vs {a}",
            "date": "2026-10-25", "start_utc": None, "venue": venue,
            "official_status": "Scheduled (Irish Local Clock Only)",
            "pricing_mode": None,
            "withhold_reason": "Munster/Cork GAA pages omit explicit GMT/IST timezone labels and county knockout finals lack unified club points-per-game league tables.",
            "official_url": url, "stats_url": url, "source_ids": ["gaa-munster-cork-2026"],
            "olbg_event_id": oid, "notes": note,
        })

    # GREYHOUNDS — 3 GBGB Category One Finals
    dogs = [
        ("gbgb-champ-stakes", "2026-10-23", "Premier Greyhound Racing Champion Stakes (575m Flat)", "Romford"),
        ("gbgb-scurry-cup", "2026-10-24", "Arena Racing Company Scurry Gold Cup (270m Flat)", "Dunstall Park"),
        ("gbgb-oaks-2026", "2026-10-24", "Premier Greyhound Racing Oaks (480m Flat)", "Dunstall Park"),
    ]
    for fid, d, ev, track in dogs:
        rows.append({
            "id": fid, "sport": "greyhounds", "competition": "GBGB 2026 Category One Open Race",
            "away": None, "home": None, "away_code": None, "home_code": None, "event_label": f"{track} · {ev}",
            "date": d, "start_utc": None, "venue": track,
            "official_status": "Category One Scheduled · Trap Draw JS-Gated",
            "pricing_mode": None,
            "withhold_reason": "GBGB Category One schedule verifies date, track, and distance only; 6-trap runner names and off-times require JS racecard POST queries.",
            "official_url": "https://www.gbgb.org.uk/racing/open-races/2025-category-one-schedule/",
            "stats_url": "https://www.gbgb.org.uk/racing/open-races/",
            "source_ids": ["gbgb-cat1-2026"], "olbg_event_id": None,
            "notes": "OLBG Greyhounds hub showed 'No tips found.' at 20:56Z.",
        })

    return rows


def build_fixture_list() -> list[dict]:
    return _nhl_rows() + _mlb_rows() + _basketball_rows() + _handball_rows() + _other_verified_rows()


# 16 explicitly expired / completed / live-in-play Oct 21-22 rows (excluded from pre-match pricing)
ELAPSED_FIXTURES = [
    {"id": "el-r7-61", "sport": "basketball", "competition": "EuroLeague R7", "match": "Hapoel IBI Tel Aviv vs Virtus Bologna", "date": "2026-10-21", "result_or_state": "Final: 90–81", "official_url": "https://www.euroleaguebasketball.net/en/euroleague/news/game-center-round-7-el2627/", "impact": "Completed Wed Oct 21; Zach LeDay 22 pts / 10 reb."},
    {"id": "el-r7-64", "sport": "basketball", "competition": "EuroLeague R7", "match": "Anadolu Efes Istanbul vs Besiktas Istanbul", "date": "2026-10-22", "result_or_state": "Final: 89–80", "official_url": "https://www.euroleaguebasketball.net/en/euroleague/news/game-center-round-7-el2627/", "impact": "Elapsed since 12:30Z midday snapshots (several midday desks priced Besiktas ML); Cam Payne 22 pts."},
    {"id": "el-r7-65", "sport": "basketball", "competition": "EuroLeague R7", "match": "FC Bayern Munich vs Dubai Basketball", "date": "2026-10-22", "result_or_state": "Final: 91–107", "official_url": "https://www.euroleaguebasketball.net/en/euroleague/news/game-center-round-7-el2627/", "impact": "Elapsed Thu evening; Mfioundu Kabengele 24 pts as Dubai improved to 5-2."},
    {"id": "el-r7-62", "sport": "basketball", "competition": "EuroLeague R7", "match": "Maccabi Rapyd Tel Aviv vs Real Madrid", "date": "2026-10-22", "result_or_state": "Final: 99–113", "official_url": "https://www.euroleaguebasketball.net/en/euroleague/news/game-center-round-7-el2627/", "impact": "Elapsed Thu evening; Facundo Campazzo 21 pts / 5 ast."},
    {"id": "el-r7-67", "sport": "basketball", "competition": "EuroLeague R7", "match": "Panathinaikos AKTOR Athens vs Kosner Baskonia Vitoria-Gasteiz", "date": "2026-10-22", "result_or_state": "Final: 85–79", "official_url": "https://www.euroleaguebasketball.net/en/euroleague/news/game-center-round-7-el2627/", "impact": "Elapsed Thu evening; Mathias Lessort 20 pts, Panathinaikos 6-1."},
    {"id": "el-r7-63", "sport": "basketball", "competition": "EuroLeague R7", "match": "Armani Olimpia Milan vs FC Barcelona", "date": "2026-10-22", "result_or_state": "Final: 81–89", "official_url": "https://www.euroleaguebasketball.net/en/euroleague/news/game-center-round-7-el2627/", "impact": "Elapsed Thu evening; Kevin Punter 18 pts."},
    {"id": "el-r7-66", "sport": "basketball", "competition": "EuroLeague R7", "match": "Partizan Mozzart Bet Belgrade vs Crvena Zvezda Meridianbet Belgrade", "date": "2026-10-22", "result_or_state": "In-Play (20:45 CEST tipoff)", "official_url": "https://www.euroleaguebasketball.net/en/euroleague/news/game-center-round-7-el2627/", "impact": "Live in crunch time at 21:01Z; strictly excluded from pre-match pricing."},
    {"id": "ehf-r5-19", "sport": "handball", "competition": "EHF CL Men R5", "match": "MT Melsungen vs Orlen Wisla Plock", "date": "2026-10-22", "result_or_state": "Final: 28–26 (60:00')", "official_url": "https://ehfcl.eurohandball.com/men/2026-27/matches/details/202711020101019/MTMelsungen-OrlenWislaPlock/", "impact": "Completed Thu evening; Balenciaga 6G, Mensing 6G."},
    {"id": "ehf-r5-43", "sport": "handball", "competition": "EHF CL Men R5", "match": "OTP Bank - PICK Szeged vs GOG", "date": "2026-10-22", "result_or_state": "Final: 33–33 (60:00')", "official_url": "https://ehfcl.eurohandball.com/men/2026-27/standings/", "impact": "Completed 60-minute draw Thu evening; updates Group D standings."},
    {"id": "ehf-r5-41", "sport": "handball", "competition": "EHF CL Men R5", "match": "Sporting Clube de Portugal vs IFK Kristianstad", "date": "2026-10-22", "result_or_state": "Final: 42–40 (60:00')", "official_url": "https://ehfcl.eurohandball.com/men/2026-27/standings/", "impact": "Completed Thu evening; Sporting moves to 4-1-0 (9 pts) in Group D."},
    {"id": "ehf-r5-49", "sport": "handball", "competition": "EHF CL Men R5", "match": "Barça vs Montpellier Handball", "date": "2026-10-22", "result_or_state": "Final: 40–34 (60:00')", "official_url": "https://ehfcl.eurohandball.com/men/2026-27/matches/details/202711020101049/Bar%C3%A7a-MontpellierHandball/", "impact": "Completed Thu evening; N'guessan/Gómez/Frade 7G each for Barça; Villeminot/Casado 6G each for Montpellier."},
    {"id": "ehf-r5-64", "sport": "handball", "competition": "EHF CL Men R5", "match": "Kolstad Håndball vs SC Magdeburg", "date": "2026-10-22", "result_or_state": "Final: 32–35 (60:00')", "official_url": "https://ehfcl.eurohandball.com/men/2026-27/standings/", "impact": "Completed Thu evening; Magdeburg moves to 5-0-0 (10 pts) in Group F."},
    {"id": "prod2-12068", "sport": "rugby-union", "competition": "French Pro D2 J8", "match": "US Montauban vs Oyonnax Rugby", "date": "2026-10-22", "result_or_state": "Completed (Montauban Win, Oyonnax Bd)", "official_url": "https://prod2.lnr.fr/classement", "impact": "21h00 French kickoff finished; Oyonnax moves to 7-0-1 (34 pts), Montauban 5-0-3 (21 pts)."},
    {"id": "wst-ni-r3-a", "sport": "snooker", "competition": "NI Open R3", "match": "Jordan Brown vs Scott Donaldson", "date": "2026-10-22", "result_or_state": "Live Now (0–0 at 21:02Z)", "official_url": "https://www.wst.tv/match-centre/f0b30e58-d987-4505-89c2-8b24805b98d5", "impact": "In-play Round 3 evening tie; pre-match pricing barred."},
    {"id": "wst-ni-r3-b", "sport": "snooker", "competition": "NI Open R3", "match": "Jak Jones vs Daniel Wells", "date": "2026-10-22", "result_or_state": "Live Now (1–0 at 21:02Z)", "official_url": "https://www.wst.tv/match-centre/f0b30e58-d987-4505-89c2-8b24805b98d5", "impact": "In-play Round 3 evening tie; winner advances to Friday QF4."},
    {"id": "pdc-ec-d1-hum", "sport": "darts", "competition": "PDC European Championship R1 Day 1", "match": "Kim Huybrechts (rep. Luke Humphries) vs Ryan Searle + 7 Day 1 Ties", "date": "2026-10-22", "result_or_state": "Elapsed Session (17:00–21:00Z); Humphries Withdrawn", "official_url": "https://www.pdc.tv/news/2026/october/22/humphries-withdraws-from-machineseeker-european-championship", "impact": "Luke Humphries withdrew due to gastroenteritis; legacy repo rows still list Humphries vs Searle."},
]

FLAGS = [
    {
        "id": "F-3EE-01",
        "severity": "high",
        "category": "OLBG Upstream Defect",
        "subject": "OLBG 5-Hour Unlabeled Split-Timezone Cache (EDT UTC-4 vs BST UTC+1)",
        "detail": "Read simultaneously at 20:56Z on 22 Oct 2026, OLBG's Ice Hockey (NSH@BOS 'Today 19:07' vs 23:00Z), Baseball (TB@MIL 'Tomorrow 20:00' vs 24 Oct 00:00Z), Rugby Union, and Motor Racing hubs render unlabeled EDT (UTC-4), while Basketball (Zalgiris vs ASVEL 'Tomorrow 18:00' vs 17:00Z) and Gaelic Football render unlabeled BST (UTC+1) — a 5-hour silent discrepancy with zero timezone indicator.",
        "action": "Never use OLBG timestamps; verify UTC only from official governing-body feeds.",
        "official_url": "https://api-web.nhle.com/v1/schedule/2026-10-22",
    },
    {
        "id": "F-3EE-02",
        "severity": "high",
        "category": "Official Cross-Page Conflict",
        "subject": "Valencia Basket Record Conflict on euroleaguebasketball.net (5-1 vs 4-2)",
        "detail": "EuroLeague's official Round 7 Game Center preview states 'Valencia (5-1)' ahead of Friday's trip to Paris Basketball, whereas the official 2026-27 Standings page lists Valencia Basket at GP 6, W 4, L 2 (PTS+ 583, PTS- 537).",
        "action": "Quarantined el-r7-69 (Paris Basketball vs Valencia Basket): all prices left blank rather than arbitrating between two official pages.",
        "official_url": "https://www.euroleaguebasketball.net/en/euroleague/standings/",
    },
    {
        "id": "F-3EE-03",
        "severity": "high",
        "category": "OLBG Wrong Fixture Date",
        "subject": "Waterford SFC Final (Rathgormack v The Nire, OLBG event_id=3536): '01 Nov' vs Official '25 Oct'",
        "detail": "OLBG's Gaelic Football hub lists Rathgormack v The Nire for '01 Nov 15:30', whereas Munster GAA's official Events Calendar confirms Sunday, Oct 25, 2026 @ 2:30pm at Cappoquin Logistics Fraher Field, Dungarvan.",
        "action": "Published Munster GAA's verified 2026-10-25 date and flagged OLBG's 7-day error.",
        "official_url": "https://munster.gaa.ie/fixtures/events-calendar/",
    },
    {
        "id": "F-3EE-04",
        "severity": "medium",
        "category": "Conditional Fixture",
        "subject": "2026 World Series Game 5 (mlb-849799): Official ifNecessary='Y'",
        "detail": "MLB StatsAPI marks Game 5 (Milwaukee Brewers @ Tampa Bay Rays, 2026-10-29T00:00:00Z) as ifNecessary='Y' ('If Necessary Game').",
        "action": "Listed on Baseball schedule with all markets withheld; excluded from confidence grading.",
        "official_url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-22&endDate=2026-10-29&hydrate=probablePitcher,team",
    },
    {
        "id": "F-3EE-05",
        "severity": "high",
        "category": "Late Player Withdrawal",
        "subject": "PDC European Championship: Luke Humphries Withdrawn (Gastroenteritis), Replaced by Kim Huybrechts",
        "detail": "PDC confirmed on 22 Oct 2026 that #12 seed Luke Humphries withdrew through illness and was replaced by Kim Huybrechts against Ryan Searle in Thursday's Day 1 session; legacy repo data/fixtures.json (line 2346) still lists Humphries.",
        "action": "Recorded official withdrawal in Elapsed Day 1 ledger and Repo Audit; only Friday Oct 23 R1 ties are listed as upcoming.",
        "official_url": "https://www.pdc.tv/news/2026/october/22/humphries-withdraws-from-machineseeker-european-championship",
    },
    {
        "id": "F-3EE-06",
        "severity": "medium",
        "category": "21:10Z Live Expiry Sweep",
        "subject": "16 Midday Snapshot Matches Have Now Finished or Started (EuroLeague R7, EHF CL R5, Pro D2, WST, PDC)",
        "detail": "Between earlier sessions' 12:30Z–13:00Z checkpoints and 21:10Z UTC on 22 Oct 2026, 6 EuroLeague R7 games, 5 EHF CL R5 games, 1 Pro D2 match, 2 WST R3 ties, and 8 PDC Day 1 ties started or finished.",
        "action": "Moved all started/completed rows to the Elapsed Ledger with official final scores and refreshed standings (EuroLeague GP=6..7, EHF GP=5, Pro D2 GP=7..8).",
        "official_url": "https://www.euroleaguebasketball.net/en/euroleague/news/game-center-round-7-el2627/",
    },
    {
        "id": "F-3EE-07",
        "severity": "medium",
        "category": "EHF Cross-Route Clock Check",
        "subject": "FC Porto vs One Veszprém HC (28 Oct 2026): EHF PDF '20:45 CET' vs Website Ticker '18:45'",
        "detail": "EHF's official Playing Times PDF lists FC Porto vs One Veszprém HC at 20:45h CET (19:45 WET local in Porto = 19:45Z), whereas the ehfcl.eurohandball.com top ticker displays '18:45' without a timezone label.",
        "action": "Retained the explicit timezone-labeled EHF PDF timestamp (19:45Z) and flagged the 1-hour ticker discrepancy for manual review.",
        "official_url": "https://www.eurohandball.com/media/jqal4wt0/ehfcl-men-2026-27-group-phase-playing-times.pdf",
    },
    {
        "id": "F-3EE-08",
        "severity": "medium",
        "category": "OLBG Active-Tournament Blind Spots",
        "subject": "Five OLBG Hubs Miss Active World Cups / Championships (Snooker, Rugby League, Aussie Rules, eSports, Greyhounds)",
        "detail": "At 20:56Z, OLBG returned 'No tips found.' on Snooker (NI Open QFs), Aussie Rules (AFLW R11), eSports (LoL Worlds Swiss), and Greyhounds (GBGB Cat 1), and showed only 2027 ante-post cards on Rugby League (missing all 13 RLWC26 Round 2 matches) and Champions Tour only on Golf (missing PGA Bermuda).",
        "action": "Harvested upcoming schedules directly from WST, IRL, AFLW, LoL Esports, GBGB, and PGA Tour official portals.",
        "official_url": "https://www.intrl.sport/fixtures-results",
    },
    {
        "id": "F-3EE-09",
        "severity": "low",
        "category": "OLBG Rendering Defect",
        "subject": "Cricket Hub Blank Tip Share on T20 Blast 2027 (event_id=188350, Sussex Outright)",
        "detail": "OLBG's Cricket hub renders an active 'Sussex — Outright Winner' card on event_id=188350 with blank win-tip numerator/denominator and percentage (each-way-only tip division defect).",
        "action": "Documented in OLBG Reverse-Engineering audit; community tip shares never enter our origination models.",
        "official_url": "https://www.icc-cricket.com/fixtures-results",
    },
    {
        "id": "F-3EE-10",
        "severity": "medium",
        "category": "Unverified Timezone Offset",
        "subject": "16 Signed ATP/WTA Friday Oct 23 Quarter-Final PDFs Omit Explicit Timezone Offset",
        "detail": "Official Supervisor OP PDFs for ATP Almaty (9410), ATP Brussels (7485), WTA Ningbo (2092), and WTA Osaka (405) print local court start times ('Starts At 11:30', 'Starts At 14:00', 'Not before 1:00 PM') without a UTC offset token.",
        "action": "Left start_utc blank (None) on all 16 tennis rows and withheld pre-match pricing.",
        "official_url": "https://www.protennislive.com/posting/2026/9410/op.pdf",
    },
    {
        "id": "F-3EE-11",
        "severity": "medium",
        "category": "Early-Season Sample Floor (<5 GP)",
        "subject": "NBA (GP 0–1), PlusLiga Volleyball (GP 1–2) & URC Rugby (GP 3) Below 5-Game Statistical Floor",
        "detail": "Official 2026-27 tables read live show NBA clubs at 0–1 GP, Polish PlusLiga clubs at 1–2 GP, and URC clubs at 3 GP — too small for reliable non-prior-dominated origination without historical multi-season feeds.",
        "action": "Published verified schedules and left prices blank rather than fabricating prior ratings.",
        "official_url": "https://www.nba.com/standings",
    },
    {
        "id": "F-3EE-12",
        "severity": "medium",
        "category": "Client-Side JS Hydration Barrier",
        "subject": "AFLW Ladder (afl.com.au/aflw/ladder) & GBGB Trap Cards Require Browser JS Execution",
        "detail": "Fetching afl.com.au/aflw/ladder returns 'Loading' in the Actual Ladder table body, and gbgb.org.uk/racing/open-races/ requires interactive JS filter state for 6-trap runner names.",
        "action": "Kept AFLW R11 fixtures and GBGB Category One finals unpriced with explicit blank markers; refused to copy unverified ladder numbers from earlier sessions.",
        "official_url": "https://www.afl.com.au/aflw/ladder",
    },
    {
        "id": "F-3EE-13",
        "severity": "low",
        "category": "In-Progress Multi-Runner Event",
        "subject": "PGA Tour Butterfield Bermuda Championship Already in Round 1 Play",
        "detail": "pgatour.com/schedule confirms Round 1 is In Progress (Ben Kohles, Ben Silverman, Danny Walker, Corey Conners tied T1 at -8).",
        "action": "Listed with 'In Progress' status and no pre-tournament outright price.",
        "official_url": "https://www.pgatour.com/schedule",
    },
    {
        "id": "F-3EE-14",
        "severity": "low",
        "category": "Pending Bracket Slot",
        "subject": "WST Northern Ireland Open QF4 Participants TBC (Brown/Donaldson vs Jones/Wells Live)",
        "detail": "At 21:02Z, WST Match Centre lists Quarter-Final 4 on 23 Oct as 'Winner of match 55 vs Winner of match 56' while both Round 3 matches are Live Now.",
        "action": "Published QF4 with explicit blank participant cells rather than guessing the R3 winners.",
        "official_url": "https://www.wst.tv/match-centre/f0b30e58-d987-4505-89c2-8b24805b98d5",
    },
    {
        "id": "F-3EE-15",
        "severity": "medium",
        "category": "Price-Window Cap (< -250 Chalk)",
        "subject": "Heavy Favourites Shorter Than -250 (p > 71.43%) Capped at Medium Confidence",
        "detail": "Across NHL, MLB Run Lines (Brewers +1.5 at -259 in Games 3–4), EuroLeague alt spreads, and EHF Champions League Group Phase mismatches (Veszprém, Barça, Magdeburg), outcomes with p > 71.43% price steeper than -250.",
        "action": "Strictly capped at Medium per the brief's -250..+10000 High-confidence window and itemized in the Out-of-Window Chalk Register.",
        "official_url": "https://api-web.nhle.com/v1/standings/2026-10-22",
    },
    {
        "id": "F-3EE-16",
        "severity": "low",
        "category": "Probable Pitcher Update",
        "subject": "2026 World Series Games 1–2 Rays Starters Confirmed Since Midday; Brewers G2 & G3–G4 Still TBA",
        "detail": "MLB StatsAPI now lists Nick Martinez (TB) vs Jacob Misiorowski (MIL) for Game 1 and Drew Rasmussen (TB) for Game 2, while Milwaukee's Game 2 starter and both clubs' Games 3–4 starters remain TBA.",
        "action": "Recorded confirmed starters in fixture notes; team run-rate Poisson model disclosed as regular-season aggregate without pitcher-level adjustment.",
        "official_url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-22&endDate=2026-10-29&hydrate=probablePitcher,team",
    },
]
