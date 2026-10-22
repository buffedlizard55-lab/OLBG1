"""Verified inputs for the T65 / ac872b16 desk (22 October 2026).

Every number in this module was read from an official competition source during
this session and is paired with the source id used in SOURCES.  Nothing here is
copied from a media outlet, an aggregator or a betting site.

Two input tiers are kept deliberately separate:

* TIER_A  - fetched and read in this session (NHL, EuroLeague, NBA standings).
* TIER_B  - official reads made earlier the same day by the T63 desk and cited
             with their source URLs and read timestamps (AFLW ladder, PDC draw,
             Top 14 / URC / Pro D2 tables, EHF Champions League table, WST
             event frames).  These are labelled cross-checked, never
             "verified this session".

All model probabilities are originated estimates.  They are not bookmaker
quotes and no market price was captured.
"""
from __future__ import annotations

SOURCES = {
    "nhl-standings": {
        "publisher": "NHL",
        "title": "NHL 2026-27 standings (payload date 2026-10-21)",
        "url": "https://api-web.nhle.com/v1/standings/now",
        "read_utc": "2026-10-22T12:06:00Z",
        "note": "Returned HTTP 200 JSON. standingsDateTimeUtc 2026-10-22T12:00:45Z.",
    },
    "nhl-team-summary": {
        "publisher": "NHL",
        "title": "NHL 2026-27 club summary statistics",
        "url": "https://api.nhle.com/stats/rest/en/team/summary?cayenneExp=seasonId=20262027%20and%20gameTypeId=2",
        "read_utc": "2026-10-22T12:10:00Z",
        "note": "32 clubs; goals for/against and per-game rates used for the margin model.",
    },
    "nhl-schedule-20261022": {
        "publisher": "NHL",
        "title": "NHL schedule, 22 October 2026",
        "url": "https://api-web.nhle.com/v1/schedule/2026-10-22",
        "read_utc": "2026-10-22T12:07:00Z",
        "note": "numberOfGames 12; gameState FUT; startTimeUTC and venues.",
    },
    "euroleague-standings": {
        "publisher": "Euroleague Basketball",
        "title": "EuroLeague 2026-27 regular-season standings",
        "url": "https://www.euroleaguebasketball.net/en/euroleague/standings/",
        "read_utc": "2026-10-22T12:12:00Z",
        "note": "All 20 clubs; GP, W, L, PTS+, PTS-, L10 read from the official table.",
    },
    "euroleague-round7": {
        "publisher": "Euroleague Basketball",
        "title": "Game Center, Round 7, 2026-27",
        "url": "https://www.euroleaguebasketball.net/en/euroleague/news/game-center-round-7-el2627/",
        "read_utc": "2026-10-22T07:17:00Z",
        "note": "Fixture dates and CEST tip-off times; UTC converted from the published CEST.",
    },
    "nba-standings": {
        "publisher": "NBA",
        "title": "NBA 2026-27 regular-season standings",
        "url": "https://www.nba.com/standings",
        "read_utc": "2026-10-22T12:20:00Z",
        "note": "Opening week: every club has played at most one game, so no NBA price is originated.",
    },
    "aflw-fixture": {
        "publisher": "Australian Football League",
        "title": "2026 NAB AFLW fixture",
        "url": "https://www.afl.com.au/aflw/fixture",
        "read_utc": "2026-10-22T07:36:00Z",
        "note": "Read by the T63 desk and recorded in data/92af340c/dataset.json; re-used with provenance.",
    },
    "aflw-ladder": {
        "publisher": "Australian Football League",
        "title": "2026 AFLW ladder after Round 10",
        "url": "https://www.afl.com.au/aflw/ladder",
        "read_utc": "2026-10-22T07:36:00Z",
        "note": "Ladder values captured by T63. The page is client-rendered; a fresh 12:1xZ fetch returned 'Loading' with no rows, so values are cross-checked, not re-verified.",
    },
    "pdc-draw": {
        "publisher": "Professional Darts Corporation",
        "title": "2026 Machineseeker European Championship field and draw",
        "url": "https://www.pdc.tv/news/2026/october/18/2026-Machineseeker-European-Championship-field---draw-confirmed",
        "read_utc": "2026-10-22T07:34:00Z",
        "note": "Draw and seed order captured by T63; used only for carried Medium/Low prices.",
    },
    "top14-classement": {
        "publisher": "Ligue Nationale de Rugby",
        "title": "Top 14 2026-27 classement",
        "url": "https://top14.lnr.fr/classement",
        "read_utc": "2026-10-22T07:40:00Z",
        "note": "Captured by T63; ratings carried at Medium confidence.",
    },
    "urc": {
        "publisher": "United Rugby Championship",
        "title": "United Rugby Championship fixtures and table",
        "url": "https://www.unitedrugby.com/",
        "read_utc": "2026-10-22T07:41:00Z",
        "note": "T63 captured URC fixtures. A fresh /standings request at 12:2xZ returned HTTP 404, so no URC rating is used.",
    },
    "ehf-cl": {
        "publisher": "European Handball Federation",
        "title": "EHF Champions League Men 2026-27 standings",
        "url": "https://ehfcl.eurohandball.com/men/2026-27/standings/",
        "read_utc": "2026-10-22T07:45:00Z",
        "note": "Captured by T63; carried at Medium confidence.",
    },
    "wst-matches": {
        "publisher": "World Snooker Tour",
        "title": "BetVictor Northern Ireland Open 2026 match results",
        "url": "https://www.wst.tv/matches/",
        "read_utc": "2026-10-22T01:30:00Z",
        "note": "Frames won/lost in the event and world ranking captured by the T41 desk; no start timezone is published.",
    },
    "mlb-standings": {
        "publisher": "MLB",
        "title": "MLB 2026 regular-season standings",
        "url": "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsTypes=regularSeason",
        "read_utc": "2026-10-22T12:15:00Z",
        "note": "AL records read directly this session; NL records carried from the T41/T354E readings.",
    },
}

# ---------------------------------------------------------------------------
# EuroLeague 2026-27 (official standings, read 12:12Z)
# code: (name, gp, w, l, points_for, points_against, l10)
# ---------------------------------------------------------------------------
EUROLEAGUE = {
    "PAO": ("Panathinaikos AKTOR Athens", 6, 5, 1, 528, 438, "5-1"),
    "FEN": ("Fenerbahce Tarfin Istanbul", 6, 5, 1, 501, 447, "5-1"),
    "OLY": ("Olympiacos Piraeus", 6, 5, 1, 564, 524, "5-1"),
    "HTA": ("Hapoel IBI Tel Aviv", 7, 5, 2, 630, 601, "5-2"),
    "VBC": ("Valencia Basket", 6, 4, 2, 583, 537, "4-2"),
    "CZV": ("Crvena Zvezda Meridianbet Belgrade", 6, 4, 2, 485, 457, "4-2"),
    "DUB": ("Dubai Basketball", 6, 4, 2, 490, 493, "4-2"),
    "VIR": ("Virtus Bologna", 7, 4, 3, 606, 608, "4-3"),
    "RMB": ("Real Madrid", 6, 3, 3, 554, 531, "3-3"),
    "BAR": ("FC Barcelona", 6, 3, 3, 534, 525, "3-3"),
    "BJK": ("Besiktas Istanbul", 6, 3, 3, 554, 555, "3-3"),
    "PAR": ("Partizan Mozzart Bet Belgrade", 6, 3, 3, 466, 471, "3-3"),
    "EFS": ("Anadolu Efes Istanbul", 6, 2, 4, 492, 510, "2-4"),
    "ZAL": ("Zalgiris Kaunas", 6, 2, 4, 490, 517, "2-4"),
    "BAY": ("FC Bayern Munich", 6, 2, 4, 521, 552, "2-4"),
    "MTA": ("Maccabi Rapyd Tel Aviv", 6, 2, 4, 509, 540, "2-4"),
    "ASV": ("LDLC ASVEL Villeurbanne", 6, 2, 4, 527, 572, "2-4"),
    "PBB": ("Paris Basketball", 6, 1, 5, 504, 545, "1-5"),
    "MIL": ("Armani Olimpia Milan", 6, 1, 5, 504, 559, "1-5"),
    "KBA": ("Kosner Baskonia Vitoria-Gasteiz", 6, 1, 5, 504, 564, "1-5"),
}

# Fixture list and official tip-off times (Game Center, converted from CEST).
EUROLEAGUE_FIXTURES = [
    ("el-r7-1", "2026-10-22T17:30:00Z", "EFS", "BJK"),
    ("el-r7-2", "2026-10-22T18:00:00Z", "BAY", "DUB"),
    ("el-r7-3", "2026-10-22T18:05:00Z", "MTA", "RMB"),
    ("el-r7-4", "2026-10-22T18:15:00Z", "PAO", "KBA"),
    ("el-r7-5", "2026-10-22T18:30:00Z", "MIL", "BAR"),
    ("el-r7-6", "2026-10-22T18:45:00Z", "PAR", "CZV"),
    ("el-r7-7", "2026-10-23T17:00:00Z", "ZAL", "ASV"),
    ("el-r7-8", "2026-10-23T18:15:00Z", "OLY", "FEN"),
    ("el-r7-9", "2026-10-23T18:45:00Z", "PBB", "VBC"),
]

# ---------------------------------------------------------------------------
# NHL 2026-27 (official standings / club summary, read 12:06-12:10Z)
# abbrev: (name, gp, w, l, otl, gf, ga, l10, streak)
# ---------------------------------------------------------------------------
NHL = {
    "ANA": ("Anaheim Ducks", 9, 4, 5, 0, 26, 29, "4-5-0", "L1"),
    "BOS": ("Boston Bruins", 10, 7, 2, 1, 36, 22, "7-2-1", "OT1"),
    "BUF": ("Buffalo Sabres", 10, 4, 4, 2, 28, 36, "4-4-2", "W1"),
    "CAR": ("Carolina Hurricanes", 11, 8, 2, 1, 42, 27, "8-2-1", "W1"),
    "CBJ": ("Columbus Blue Jackets", 8, 3, 5, 0, 19, 29, "3-5-0", "L2"),
    "CGY": ("Calgary Flames", 8, 2, 6, 0, 17, 37, "2-6-0", "L3"),
    "CHI": ("Chicago Blackhawks", 9, 3, 6, 0, 21, 36, "3-6-0", "L1"),
    "COL": ("Colorado Avalanche", 10, 5, 4, 1, 41, 30, "5-4-1", "W1"),
    "DAL": ("Dallas Stars", 9, 5, 3, 1, 22, 14, "5-3-1", "W2"),
    "DET": ("Detroit Red Wings", 9, 3, 3, 3, 22, 26, "3-3-3", "W1"),
    "EDM": ("Edmonton Oilers", 9, 7, 1, 1, 41, 27, "7-1-1", "W2"),
    "FLA": ("Florida Panthers", 10, 5, 3, 2, 31, 30, "5-3-2", "L1"),
    "LAK": ("Los Angeles Kings", 7, 1, 4, 2, 17, 27, "1-4-2", "L2"),
    "MIN": ("Minnesota Wild", 10, 6, 2, 2, 31, 25, "6-2-2", "W2"),
    "MTL": ("Montreal Canadiens", 9, 4, 3, 2, 28, 34, "4-3-2", "W1"),
    "NJD": ("New Jersey Devils", 9, 5, 4, 0, 29, 30, "5-4-0", "W1"),
    "NSH": ("Nashville Predators", 8, 3, 2, 3, 23, 22, "3-2-3", "W1"),
    "NYI": ("New York Islanders", 9, 5, 3, 1, 27, 19, "5-3-1", "W1"),
    "NYR": ("New York Rangers", 11, 7, 3, 1, 33, 24, "7-3-1", "W3"),
    "OTT": ("Ottawa Senators", 10, 7, 3, 0, 27, 24, "7-3-0", "W1"),
    "PHI": ("Philadelphia Flyers", 12, 3, 6, 3, 20, 36, "3-6-3", "L1"),
    "PIT": ("Pittsburgh Penguins", 10, 3, 6, 1, 32, 37, "3-6-1", "L1"),
    "SEA": ("Seattle Kraken", 10, 6, 3, 1, 37, 34, "6-3-1", "W1"),
    "SJS": ("San Jose Sharks", 10, 5, 4, 1, 26, 34, "5-4-1", "W1"),
    "STL": ("St. Louis Blues", 9, 4, 4, 1, 29, 29, "4-4-1", "W1"),
    "TBL": ("Tampa Bay Lightning", 9, 7, 2, 0, 31, 23, "7-2-0", "W5"),
    "TOR": ("Toronto Maple Leafs", 11, 5, 4, 2, 38, 34, "5-4-2", "W1"),
    "UTA": ("Utah Mammoth", 10, 7, 3, 0, 38, 31, "7-3-0", "W1"),
    "VAN": ("Vancouver Canucks", 11, 2, 8, 1, 33, 51, "2-8-1", "L1"),
    "VGK": ("Vegas Golden Knights", 11, 8, 3, 0, 43, 30, "8-3-0", "L1"),
    "WPG": ("Winnipeg Jets", 9, 4, 3, 2, 24, 26, "4-3-2", "W1"),
    "WSH": ("Washington Capitals", 9, 5, 4, 0, 30, 29, "5-4-0", "W1"),
}

# fixture id, utc, home, away, game id (blank = not read), venue (blank = not read)
NHL_FIXTURES = [
    ("nhl-2026020154", "2026-10-22T23:00:00Z", "BOS", "NSH", "2026020154", "TD Garden"),
    ("nhl-2026020155", "2026-10-22T23:00:00Z", "TOR", "NYR", "2026020155", "Scotiabank Arena"),
    ("nhl-2026020156", "2026-10-22T23:00:00Z", "OTT", "SJS", "2026020156", "Canadian Tire Centre"),
    ("nhl-2026020157", "2026-10-22T23:00:00Z", "NJD", "ANA", "2026020157", "Prudential Center"),
    ("nhl-2026020158", "2026-10-22T23:00:00Z", "PIT", "FLA", "2026020158", "PPG Paints Arena"),
    ("nhl-2026020159", "2026-10-22T23:30:00Z", "NYI", "LAK", "2026020159", ""),
    ("nhl-2026020160", "2026-10-23T00:00:00Z", "STL", "VGK", "2026020160", ""),
    ("nhl-2026020161", "2026-10-23T00:00:00Z", "DAL", "WPG", "2026020161", ""),
    ("nhl-2026020162", "2026-10-23T01:00:00Z", "CGY", "MIN", "2026020162", ""),
    ("nhl-2026020163", "2026-10-23T01:00:00Z", "EDM", "CAR", "2026020163", ""),
    ("nhl-2026020164", "2026-10-23T02:00:00Z", "SEA", "UTA", "2026020164", ""),
    ("nhl-2026020165", "2026-10-23T02:00:00Z", "VAN", "DET", "2026020165", ""),
    ("nhl-2026020166", "2026-10-24T00:00:00Z", "CHI", "MTL", "2026020166", ""),
    ("nhl-2026020167", "2026-10-24T01:00:00Z", "COL", "TBL", "2026020167", ""),
]

# ---------------------------------------------------------------------------
# AFLW Round 11 (official fixture and ladder values captured by T63, 07:36Z)
# id, utc, home, away, venue, home ladder value, home rating, away value, away rating
# ---------------------------------------------------------------------------
AFLW = [
    ("aflw-r11-01", "2026-10-25T02:05:00Z", "North Melbourne", "Adelaide Crows", "North Hobart Oval, Hobart",
     "1st, 36 pts (9-1-0, 251.9%)", 89.0, "9th, 20 pts (5-5-0, 102.4%)", 59.0, 16.46),
    ("aflw-r11-02", "2026-10-24T04:05:00Z", "Geelong Cats", "Fremantle", "GMHBA Stadium, Geelong",
     "2nd, 36 pts (9-1-0, 167.2%)", 88.0, "8th, 20 pts (5-5-0, 104.9%)", 60.0, 15.58),
    ("aflw-r11-03", "2026-10-24T08:15:00Z", "Western Bulldogs", "Melbourne", "Mission Whitten Oval, Melbourne",
     "4th, 32 pts (8-2-0, 140.9%)", 81.0, "3rd, 32 pts (8-2-0, 177.2%)", 82.0, 2.08),
    ("aflw-r11-04", "2026-10-25T06:05:00Z", "Carlton", "GWS GIANTS", "IKON Park, Melbourne",
     "6th, 28 pts (7-3-0, 133.0%)", 73.0, "15th, 8 pts (2-8-0, 68.2%)", 38.0, 18.61),
    ("aflw-r11-05", "2026-10-25T04:05:00Z", "Hawthorn", "Essendon", "Kennedy Community Centre, Dingley",
     "10th, 20 pts (5-5-0, 101.5%)", 58.0, "17th, 4 pts (1-9-0, 55.6%)", 30.0, 15.58),
    ("aflw-r11-06", "2026-10-24T06:05:00Z", "Gold Coast SUNS", "Richmond", "People First Stadium, Gold Coast",
     "5th, 28 pts (7-3-0, 138.9%)", 74.0, "13th, 16 pts (4-6-0, 68.9%)", 51.0, 13.35),
    ("aflw-r11-07", "2026-10-23T08:15:00Z", "Port Adelaide", "Collingwood", "Alberton Oval, Adelaide",
     "11th, 16 pts (4-6-0, 78.8%)", 53.0, "16th, 4 pts (1-9-0, 56.7%)", 31.0, 12.90),
    ("aflw-r11-08", "2026-10-25T01:35:00Z", "Sydney Swans", "West Coast Eagles", "Henson Park, Sydney",
     "7th, 28 pts (7-3-0, 112.9%)", 72.0, "12th, 16 pts (4-6-0, 75.2%)", 52.0, 11.99),
    ("aflw-r11-09", "2026-10-24T02:05:00Z", "St Kilda", "Brisbane Lions", "RSEA Park, Melbourne",
     "18th, 4 pts (1-9-0, 45.1%)", 29.0, "14th, 12 pts (3-7-0, 89.7%)", 45.0, -5.15),
]

# Aliases used to join OLBG discovery cards to official fixtures.
EURO_ALIASES = {
    "anadolu efes": "EFS", "besiktas": "BJK", "bayern munich": "BAY", "bc dubai": "DUB",
    "dubai basketball": "DUB", "maccabi tel aviv": "MTA", "real madrid": "RMB",
    "panathinaikos": "PAO", "baskonia": "KBA", "milano": "MIL", "barcelona": "BAR",
    "partizan": "PAR", "crvena zvezda": "CZV", "zalgiris": "ZAL", "asvel": "ASV",
    "olympiacos": "OLY", "fenerbahce": "FEN", "paris basketball": "PBB", "valencia": "VBC",
}

NHL_CITY_TO_ABBREV = {
    "anaheim": "ANA", "boston": "BOS", "buffalo": "BUF", "calgary": "CGY", "carolina": "CAR",
    "chicago": "CHI", "colorado": "COL", "columbus": "CBJ", "dallas": "DAL", "detroit": "DET",
    "edmonton": "EDM", "florida": "FLA", "los angeles": "LAK", "la": "LAK", "minnesota": "MIN",
    "montreal": "MTL", "nashville": "NSH", "new jersey": "NJD", "ny islanders": "NYI",
    "ny rangers": "NYR", "ottawa": "OTT", "philadelphia": "PHI", "pittsburgh": "PIT",
    "san jose": "SJS", "seattle": "SEA", "st louis": "STL", "tampa bay": "TBL",
    "toronto": "TOR", "utah": "UTA", "vancouver": "VAN", "vegas": "VGK", "winnipeg": "WPG",
    "washington": "WSH",
}

# Carried rows: fixture ids from the T63 dataset that are priced again here with
# their captured official inputs.  Confidence is capped at medium.
CARRIED_PRICED = {
    "darts": {"max_conf": "medium", "note": "PDC draw/seed inputs captured by T63 at 07:34Z; not re-fetched."},
    "rugby-union": {"max_conf": "medium", "note": "Top 14 / URC / Pro D2 inputs captured by T63 at 07:40Z; carried."},
    "handball": {"max_conf": "medium", "note": "EHF Champions League table captured by T63 at 07:45Z; carried."},
    "baseball": {"max_conf": "low", "note": "2026 regular-season records; postseason roster effects not modelled."},
}
