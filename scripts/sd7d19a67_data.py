"""Session d7d19a67-olbg1 (task TD7D19, claimed as T65) - transcribed official-source evidence.

Every literal in this module was read this session (2026-10-22, 12:22Z-12:55Z) from an
official publisher page listed in SOURCES. Nothing is inferred, interpolated or recalled:
where the official page did not state a value the field is None and a flag explains why.

Scope of the desk: the 17 OLBG in-scope sports (soccer/football, American football,
boxing, UFC/MMA, hurling, horse racing, cycling and specials excluded).
"""

SESSION = "d7d19a67-olbg1"
TASK = "TD7D19"
DESK_READ_UTC = "2026-10-22T12:55:00Z"
WINDOW_FROM_UTC = "2026-10-22T12:55:00Z"
WINDOW_UNTIL_UTC = "2026-10-29T12:55:00Z"

# ---------------------------------------------------------------- sources read
SOURCES = [
    {
        "id": "nhl-schedule-20261022",
        "publisher": "National Hockey League (official league API)",
        "url": "https://api-web.nhle.com/v1/schedule/2026-10-22",
        "kind": "machine-readable JSON",
        "read_at_utc": "2026-10-22T12:22:00Z",
        "role": "fixture verification (ice hockey)",
        "read": "chunk 0 of 12 read; 22 Oct 2026 slate, numberOfGames=12, four games read in full "
                "(ids 2026020154-2026020157) plus the start of id 2026020158 (venue/broadcasts only).",
        "limitation": "chunks 1-11 were not read (three retrieval attempts returned proxy signature "
                      "errors), so the remaining 22 Oct games and the away side of id 2026020158 are "
                      "unverified and published blank.",
    },
    {
        "id": "nhl-schedule-20261023",
        "publisher": "National Hockey League (official league API)",
        "url": "https://api-web.nhle.com/v1/schedule/2026-10-23",
        "kind": "machine-readable JSON",
        "read_at_utc": "2026-10-22T12:36:00Z",
        "role": "fixture verification (ice hockey)",
        "read": "chunks 0-1 of 12 read; week 23-29 Oct 2026: 23 Oct (numberOfGames=2, ids "
                "2026020166-2026020167) and 24 Oct (numberOfGames=12, ids 2026020168-2026020173 read "
                "in full, id 2026020174 read only to its broadcasts block).",
        "limitation": "chunks 2-11 not read; 25-29 Oct NHL fixtures are not published by this desk.",
    },
    {
        "id": "nhl-standings-20261021",
        "publisher": "National Hockey League (official league API)",
        "url": "https://api-web.nhle.com/v1/standings/2026-10-21",
        "kind": "machine-readable JSON",
        "read_at_utc": "2026-10-22T12:33:00Z",
        "role": "statistical input (ice hockey): all 32 clubs, gamesPlayed/wins/losses/otLosses/"
                "goalFor/goalAgainst/points/pointPctg",
        "read": "all 8 chunks read; payload timestamp standingsDateTimeUtc=2026-10-22T12:00:45Z; "
                "32 team rows transcribed to data/d7d19a67/raw/nhl_standings_2026-10-21.json "
                "(306 games played / 2 = 153 games, internally consistent).",
        "limitation": "none for the fields used.",
    },
    {
        "id": "nhl-scoreboard-20261022",
        "publisher": "National Hockey League (official league API)",
        "url": "https://api-web.nhle.com/v1/scoreboard/2026-10-22",
        "kind": "machine-readable JSON",
        "read_at_utc": "2026-10-22T12:34:00Z",
        "role": "recent match history (ice hockey): final scores for completed games",
        "read": "chunk 0 of 17 read; completed games 2026020137-2026020141 (19-20 Oct 2026) with "
                "official final scores and venues.",
        "limitation": "the 20 Oct COL@NJD row (id 2026020142) was cut before its score and is not used.",
    },
    {
        "id": "mlb-schedule-worldseries",
        "publisher": "Major League Baseball (official Stats API)",
        "url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-22&endDate=2026-10-29",
        "kind": "machine-readable JSON",
        "read_at_utc": "2026-10-22T12:24:00Z",
        "role": "fixture verification (baseball): 2026 World Series games 1-5",
        "read": "single chunk; five gamePk rows (849805, 849802, 849804, 849803, 849799) with "
                "gameType=W, seriesDescription='World Series', seriesGameNumber 1-5, gameDate, "
                "status.detailedState='Scheduled', both clubs and venue.",
        "limitation": "games 6 and 7 are not yet listed by the official feed; no pitch times beyond "
                      "gameDate are published.",
    },
    {
        "id": "mlb-standings-2026",
        "publisher": "Major League Baseball (official Stats API)",
        "url": "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsTypes=regularSeason",
        "kind": "machine-readable JSON",
        "read_at_utc": "2026-10-22T12:31:00Z",
        "role": "statistical input (baseball): 2026 regular-season wins/losses/runsScored/runsAllowed",
        "read": "chunk 0 of 4 (AL East and part of AL Central) plus the NL Central division read at "
                "https://statsapi.mlb.com/api/v1/standings?leagueId=104&season=2026&standingsTypes="
                "regularSeason&divisionId=202 - Tampa Bay Rays 98-64 (736 RS / 650 RA) and Milwaukee "
                "Brewers 103-59 (832 RS / 618 RA), the two World Series clubs.",
        "limitation": "postseason run rates are not published by the endpoint used; only regular-season "
                      "rates are used, and the model states that explicitly.",
    },
    {
        "id": "euroleague-round7",
        "publisher": "Euroleague Basketball (official competition organiser)",
        "url": "https://www.euroleaguebasketball.net/en/euroleague/news/game-center-round-7-el2627/",
        "kind": "official competition article",
        "read_at_utc": "2026-10-22T12:44:00Z",
        "role": "fixture verification + statistical input (basketball): EuroLeague Round 7",
        "read": "all 3 chunks read; nine fixtures for 22-23 Oct 2026 with published CEST start times, "
                "game-centre links (E2026/61-70) and each club's official Round-6 standing record, "
                "plus official points-for/points-allowed ranks and named player/injury context.",
        "limitation": "the 21 Oct game (Hapoel IBI Tel Aviv 90-81 Virtus Bologna) is a completed "
                      "result, not a fixture. NBA fixtures are not covered here.",
    },
    {
        "id": "wta-ningbo-op",
        "publisher": "WTA Tour (official tour document host)",
        "url": "https://wtafiles.wtatennis.com/pdf/draws/2026/2092/OP.pdf",
        "kind": "official order of play (PDF)",
        "read_at_utc": "2026-10-22T12:40:00Z",
        "role": "fixture verification (tennis): BNB Ningbo Open quarter-finals, Friday 23 October 2026",
        "read": "single chunk; tournament header (BNB Ningbo Open, Ningbo CHN, October 19-25 2026, "
                "$1,206,446, Hard/Plexipave) and five Centre Court quarter-final rows with published "
                "clock times (11:00 AM / not before 1:00 PM / followed by / not before 4:00 PM / "
                "not before 7:00 PM), seeds and the supervisor note.",
        "limitation": "the PDF prints clock times with no timezone label, so no UTC start is published; "
                      "'followed by' rows have no clock time at all.",
    },
    {
        "id": "atp-brussels-op",
        "publisher": "ATP Tour (official posting host protennislive.com)",
        "url": "https://www.protennislive.com/posting/2026/7485/op.pdf",
        "kind": "official order of play (PDF)",
        "read_at_utc": "2026-10-22T12:40:00Z",
        "role": "fixture verification (tennis): ATP event 7485 order of play, Thursday 22 October 2026",
        "read": "single chunk; three singles rows (starts at 13:30 / followed by / not before 17:00) and "
                "two doubles rows, seeding and entry codes, release stamp 10/21/2026 21:52:29, tournament "
                "director Dick Norman, ATP supervisors Rafael Schneider and Carlos Sanchez, referee "
                "Michel Willems.",
        "limitation": "the extracted PDF text carries no tournament name, city, court surface or "
                      "timezone, so those fields are published blank rather than assumed.",
    },
    {
        "id": "pcb-tri-nation-odi",
        "publisher": "Pakistan Cricket Board (official board)",
        "url": "https://www.pcb.com.pk/pakistan-england-and-sri-lanka-trination-odi-series-202627/tournament/1465.html",
        "kind": "official tournament fixture list",
        "read_at_utc": "2026-10-22T12:48:00Z",
        "role": "fixture verification (cricket): Pakistan, England and Sri Lanka Tri-nation ODI Series 2026/27",
        "read": "single chunk; all seven series rows (matches 1-6 plus the Final) with dates, teams, "
                "match names, grounds and countries; matches 1-3 carry match-centre links.",
        "limitation": "the page publishes dates only - no start times, no timezone, no results; the "
                      "31 Oct Final is listed as 'TBC vs TBC' and falls outside this desk's window.",
    },
    {
        "id": "irl-fixtures",
        "publisher": "International Rugby League (official governing body)",
        "url": "https://www.intrl.sport/fixtures-results",
        "kind": "official fixture list",
        "read_at_utc": "2026-10-22T12:50:00Z",
        "role": "fixture verification (rugby league): 23-25 Oct 2026 international fixtures",
        "read": "single chunk (no pagination needed); 13 fixtures dated 23-25 Oct 2026 with competition, "
                "round, venue, published clock time and an official match-details link each; the page "
                "also lists 30-31 Oct rows which fall outside this desk's window.",
        "limitation": "clock times carry no timezone label on the page, so UTC starts are published "
                      "blank; the IRL page does not publish team form, rankings or results for these "
                      "fixtures, so no price is originated for them.",
    },
    {
        "id": "rlwc2026-draws",
        "publisher": "Rugby League World Cup 2026 (official tournament organiser)",
        "url": "https://www.rlwc2026.com/draws-and-pools",
        "kind": "official draw and fixture page",
        "read_at_utc": "2026-10-22T12:47:00Z",
        "role": "second official corroboration (rugby league): men's Round 2 pairings and venues",
        "read": "single chunk; men's Round 2 pairings Tonga v Lebanon (CommBank Stadium, Sydney), "
                "Papua New Guinea v Samoa (Santos National Football Stadium, Port Moresby), England v "
                "France (HBF Park, Perth), New Zealand v Cook Islands (One NZ Stadium, Christchurch) and "
                "Australia v Fiji (Suncorp Stadium, Brisbane), each with an official match-centre link.",
        "limitation": "kick-off clocks on this page are rendered in the retrieval environment's own "
                      "timezone with no label, so they are not used; the IRL times are used instead.",
    },
    {
        "id": "wst-ni-open-results",
        "publisher": "World Snooker Tour (official tour site)",
        "url": "https://www.wst.tv/matches/",
        "kind": "official match list",
        "read_at_utc": "2026-10-22T12:51:00Z",
        "role": "attempted fixture verification (snooker): BetVictor Northern Ireland Open 2026",
        "read": "chunk 0 of 3 read; Round 1 rows for Sun 18 Oct and Mon 19 Oct 2026 with official "
                "frame scores (for example Mark Selby 2-4 Louis Heathcote, Neil Robertson 1-4 Ricky "
                "Walden, Shaun Murphy 2-4 Liam Davies) and match-centre links.",
        "limitation": "the rows for the still-to-be-played rounds sit beyond chunk 0 and were not read, "
                      "so this desk publishes no upcoming snooker fixture. The completed Round 1 rows are "
                      "recorded as form evidence only.",
    },
    {
        "id": "pdc-euro-champ-attempt",
        "publisher": "Professional Darts Corporation (official promoter)",
        "url": "https://www.pdc.tv/news/2026/october/19/2026-machineseeker-european-championship-schedule-confirmed/",
        "kind": "official news article (attempted)",
        "read_at_utc": "2026-10-22T12:49:00Z",
        "role": "attempted fixture verification (darts)",
        "read": "the retrieval returned only the site's cookie-consent payload (7 chunks of vendor and "
                "cookie tables); no schedule content was readable.",
        "limitation": "darts is therefore published as a coverage gap with the attempted URL.",
    },
    {
        "id": "aflw-fixture-attempt",
        "publisher": "AFL / AFLW (official competition site)",
        "url": "https://www.afl.com.au/aflw/fixture",
        "kind": "official fixture page (attempted)",
        "read_at_utc": "2026-10-22T12:54:00Z",
        "role": "attempted fixture verification (Australian rules)",
        "read": "both chunks of the page were read; they contain only site navigation, partner logos, "
                "app links and the acknowledgement of country - no fixture rows.",
        "limitation": "AFLW fixture cards are rendered client-side, so Australian rules is published as "
                      "a coverage gap with the attempted URL.",
    },
    {
        "id": "nba-scoreboard-attempt",
        "publisher": "NBA (official CDN)",
        "url": "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json",
        "kind": "machine-readable JSON (attempted)",
        "read_at_utc": "2026-10-22T12:24:00Z",
        "role": "attempted fixture verification (basketball, NBA)",
        "read": "the request returned HTTP 500 on the only attempt made inside this desk's budget.",
        "limitation": "NBA fixtures are published as a gap; a failed request is not a zero-fixture "
                      "finding. EuroLeague covers basketball for this desk.",
    },
]

# ------------------------------------------------------- statistical inputs
# NHL: transcribed from nhl-standings-20261021 (all 32 clubs).
NHL_STANDINGS_URL = "https://api-web.nhle.com/v1/standings/2026-10-21"
NHL_STANDINGS = {
    "CAR": (11, 8, 2, 1, 42, 27, 17), "VGK": (11, 8, 3, 0, 44, 30, 16),
    "EDM": (9, 7, 1, 1, 41, 27, 15), "BOS": (10, 7, 2, 1, 36, 22, 15),
    "NYR": (11, 7, 3, 1, 33, 24, 15), "TBL": (9, 7, 2, 0, 31, 23, 14),
    "UTA": (10, 7, 3, 0, 38, 31, 14), "MIN": (10, 6, 2, 2, 31, 25, 14),
    "OTT": (10, 7, 3, 0, 29, 24, 14), "SEA": (10, 6, 3, 1, 39, 34, 13),
    "FLA": (10, 5, 3, 2, 31, 30, 12), "TOR": (11, 5, 4, 2, 38, 35, 12),
    "NYI": (9, 5, 3, 1, 27, 20, 11), "DAL": (9, 5, 3, 1, 23, 15, 11),
    "COL": (10, 5, 4, 1, 41, 31, 11), "SJS": (10, 5, 4, 1, 27, 35, 11),
    "WSH": (9, 5, 4, 0, 30, 29, 10), "WPG": (9, 4, 3, 2, 24, 26, 10),
    "NJD": (9, 5, 4, 0, 29, 30, 10), "MTL": (9, 4, 3, 2, 30, 34, 10),
    "BUF": (10, 4, 4, 2, 28, 37, 10), "NSH": (8, 3, 2, 3, 23, 24, 9),
    "STL": (9, 4, 4, 1, 29, 29, 9), "DET": (9, 3, 3, 3, 23, 28, 9),
    "PHI": (12, 3, 6, 3, 20, 37, 9), "ANA": (9, 4, 5, 0, 26, 29, 8),
    "PIT": (10, 3, 6, 1, 33, 38, 7), "CBJ": (8, 3, 5, 0, 20, 29, 6),
    "CHI": (9, 3, 6, 0, 21, 36, 6), "VAN": (11, 2, 8, 1, 33, 51, 5),
    "LAK": (7, 1, 4, 2, 17, 27, 4), "CGY": (8, 2, 6, 0, 17, 37, 4),
}
NHL_NAMES = {
    "CAR": "Carolina Hurricanes", "VGK": "Vegas Golden Knights", "EDM": "Edmonton Oilers",
    "BOS": "Boston Bruins", "NYR": "New York Rangers", "TBL": "Tampa Bay Lightning",
    "UTA": "Utah Mammoth", "MIN": "Minnesota Wild", "OTT": "Ottawa Senators",
    "SEA": "Seattle Kraken", "FLA": "Florida Panthers", "TOR": "Toronto Maple Leafs",
    "NYI": "New York Islanders", "DAL": "Dallas Stars", "COL": "Colorado Avalanche",
    "SJS": "San Jose Sharks", "WSH": "Washington Capitals", "WPG": "Winnipeg Jets",
    "NJD": "New Jersey Devils", "MTL": "Montreal Canadiens", "BUF": "Buffalo Sabres",
    "NSH": "Nashville Predators", "STL": "St. Louis Blues", "DET": "Detroit Red Wings",
    "PHI": "Philadelphia Flyers", "ANA": "Anaheim Ducks", "PIT": "Pittsburgh Penguins",
    "CBJ": "Columbus Blue Jackets", "CHI": "Chicago Blackhawks", "VAN": "Vancouver Canucks",
    "LAK": "Los Angeles Kings", "CGY": "Calgary Flames",
}
# Current streak as stamped on the same official standings payload (streakCode / streakCount).
# "OT" is the NHL's own code for a game decided in overtime/shootout against the club.
NHL_STREAK = {
    "CAR": ("W", 1), "VGK": ("L", 1), "EDM": ("W", 2), "BOS": ("OT", 1), "NYR": ("W", 1),
    "TBL": ("W", 3), "UTA": ("W", 1), "MIN": ("OT", 1), "OTT": ("W", 1), "SEA": ("W", 1),
    "FLA": ("L", 1), "TOR": ("W", 2), "NYI": ("W", 2), "DAL": ("W", 3), "COL": ("L", 2),
    "SJS": ("W", 1), "WSH": ("L", 1), "WPG": ("L", 2), "NJD": ("W", 1), "MTL": ("OT", 1),
    "BUF": ("L", 1), "NSH": ("W", 1), "STL": ("W", 1), "DET": ("OT", 1), "PHI": ("W", 3),
    "ANA": ("L", 4), "PIT": ("L", 4), "CBJ": ("L", 2), "CHI": ("L", 1), "VAN": ("L", 2),
    "LAK": ("W", 1), "CGY": ("W", 1),
}

# Completed NHL results read from nhl-scoreboard-20261022 (chunk 0), used as recent history.
NHL_RESULTS = [
    {"id": 2026020137, "date": "2026-10-19", "away": "ANA", "home": "NYR", "away_score": 2,
     "home_score": 5, "venue": "Madison Square Garden", "state": "OFF", "period": 3},
    {"id": 2026020138, "date": "2026-10-19", "away": "COL", "home": "PHI", "away_score": 2,
     "home_score": 3, "venue": "Xfinity Mobile Arena", "state": "OFF", "period": 3},
    {"id": 2026020139, "date": "2026-10-19", "away": "SJS", "home": "TOR", "away_score": 1,
     "home_score": 3, "venue": "Scotiabank Arena", "state": "OFF", "period": 3},
    {"id": 2026020140, "date": "2026-10-19", "away": "PIT", "home": "UTA", "away_score": 4,
     "home_score": 5, "venue": "Delta Center", "state": "OFF", "period": 3},
    {"id": 2026020141, "date": "2026-10-20", "away": "SJS", "home": "MTL", "away_score": 4,
     "home_score": 3, "venue": "Centre Bell", "state": "OFF", "period": 4,
     "note": "periodDescriptor periodType=OT on the official payload"},
]

# MLB: 2026 regular season, read from mlb-standings-2026.
MLB_TEAMS = {
    "TB": {"name": "Tampa Bay Rays", "w": 98, "l": 64, "rs": 736, "ra": 650,
           "division_rank": "1", "division": "AL East"},
    "MIL": {"name": "Milwaukee Brewers", "w": 103, "l": 59, "rs": 832, "ra": 618,
            "division_rank": "1", "division": "NL Central"},
}

# EuroLeague Round 7: records and official context read from euroleague-round7.
EUROLEAGUE_TEAMS = {
    "EFES": {"name": "Anadolu Efes Istanbul", "w": 2, "l": 4},
    "BES": {"name": "Besiktas Istanbul", "w": 3, "l": 3},
    "BAY": {"name": "FC Bayern Munich", "w": 2, "l": 4},
    "DUB": {"name": "Dubai Basketball", "w": 4, "l": 2},
    "MAC": {"name": "Maccabi Rapyd Tel Aviv", "w": 2, "l": 4},
    "MAD": {"name": "Real Madrid", "w": 3, "l": 3},
    "PAO": {"name": "Panathinaikos AKTOR Athens", "w": 5, "l": 1},
    "BAS": {"name": "Kosner Baskonia Vitoria-Gasteiz", "w": 1, "l": 5},
    "MIL": {"name": "Armani Olimpia Milan", "w": 1, "l": 5},
    "BAR": {"name": "FC Barcelona", "w": 3, "l": 3},
    "PAR": {"name": "Partizan Mozzart Bet Belgrade", "w": 3, "l": 3},
    "CZV": {"name": "Crvena Zvezda Meridianbet Belgrade", "w": 4, "l": 2},
    "ZAL": {"name": "Zalgiris Kaunas", "w": 2, "l": 4},
    "ASV": {"name": "LDLC ASVEL Villeurbanne", "w": 2, "l": 4},
    "OLY": {"name": "Olympiacos Piraeus", "w": 5, "l": 1},
    "FEN": {"name": "Fenerbahce Tarfin Istanbul", "w": 5, "l": 1},
    "PARIS": {"name": "Paris Basketball", "w": 1, "l": 5},
    "VAL": {"name": "Valencia Basket", "w": 5, "l": 1},
}

# ------------------------------------------------------------------ fixtures
# time_utc: only where the official source published an exact UTC instant.
# time_local: only where the official source printed a clock time; timezone label
# recorded separately (None means the official page carried no label).
FIXTURES = [
    # --- ice hockey (NHL) ------------------------------------------------
    {"key": "nhl-2026020154", "sport": "ice-hockey", "competition": "NHL 2026-27 regular season",
     "away": "NSH", "home": "BOS", "date": "2026-10-22", "time_utc": "2026-10-22T23:00:00Z",
     "venue": "TD Garden", "status": "FUT", "event_id": "2026020154",
     "sources": ["nhl-schedule-20261022"], "official_link":
         "https://www.nhl.com/gamecenter/nsh-vs-bos/2026-10-22/2026020154"},
    {"key": "nhl-2026020155", "sport": "ice-hockey", "competition": "NHL 2026-27 regular season",
     "away": "NYR", "home": "TOR", "date": "2026-10-22", "time_utc": "2026-10-22T23:00:00Z",
     "venue": "Scotiabank Arena", "status": "FUT", "event_id": "2026020155",
     "sources": ["nhl-schedule-20261022"], "official_link":
         "https://www.nhl.com/gamecenter/nyr-vs-tor/2026-10-22/2026020155"},
    {"key": "nhl-2026020156", "sport": "ice-hockey", "competition": "NHL 2026-27 regular season",
     "away": "SJS", "home": "OTT", "date": "2026-10-22", "time_utc": "2026-10-22T23:00:00Z",
     "venue": "Canadian Tire Centre", "status": "FUT", "event_id": "2026020156",
     "sources": ["nhl-schedule-20261022"], "official_link":
         "https://www.nhl.com/gamecenter/sjs-vs-ott/2026-10-22/2026020156"},
    {"key": "nhl-2026020157", "sport": "ice-hockey", "competition": "NHL 2026-27 regular season",
     "away": "ANA", "home": "NJD", "date": "2026-10-22", "time_utc": "2026-10-22T23:00:00Z",
     "venue": "Prudential Center", "status": "FUT", "event_id": "2026020157",
     "sources": ["nhl-schedule-20261022"], "official_link":
         "https://www.nhl.com/gamecenter/ana-vs-njd/2026-10-22/2026020157"},
    {"key": "nhl-2026020158", "sport": "ice-hockey", "competition": "NHL 2026-27 regular season",
     "away": None, "home": "PIT", "date": "2026-10-22", "time_utc": "2026-10-22T23:00:00Z",
     "venue": "PPG Paints Arena", "status": "FUT", "event_id": "2026020158",
     "sources": ["nhl-schedule-20261022"], "official_link":
         "https://api-web.nhle.com/v1/schedule/2026-10-22",
     "blank_fields": ["away"],
     "flag": "F-D7D-01"},
    {"key": "nhl-2026020166", "sport": "ice-hockey", "competition": "NHL 2026-27 regular season",
     "away": "MTL", "home": "CHI", "date": "2026-10-23", "time_utc": "2026-10-24T00:00:00Z",
     "venue": "United Center", "status": "FUT", "event_id": "2026020166",
     "sources": ["nhl-schedule-20261023"], "official_link":
         "https://www.nhl.com/gamecenter/mtl-vs-chi/2026-10-23/2026020166"},
    {"key": "nhl-2026020167", "sport": "ice-hockey", "competition": "NHL 2026-27 regular season",
     "away": "TBL", "home": "COL", "date": "2026-10-23", "time_utc": "2026-10-24T01:00:00Z",
     "venue": "Ball Arena", "status": "FUT", "event_id": "2026020167",
     "sources": ["nhl-schedule-20261023"], "official_link":
         "https://www.nhl.com/gamecenter/tbl-vs-col/2026-10-23/2026020167"},
    {"key": "nhl-2026020168", "sport": "ice-hockey", "competition": "NHL 2026-27 regular season",
     "away": "ANA", "home": "PHI", "date": "2026-10-24", "time_utc": "2026-10-24T17:00:00Z",
     "venue": "Xfinity Mobile Arena", "status": "FUT", "event_id": "2026020168",
     "sources": ["nhl-schedule-20261023"], "official_link":
         "https://www.nhl.com/gamecenter/ana-vs-phi/2026-10-24/2026020168"},
    {"key": "nhl-2026020169", "sport": "ice-hockey", "competition": "NHL 2026-27 regular season",
     "away": "LAK", "home": "NJD", "date": "2026-10-24", "time_utc": "2026-10-24T19:30:00Z",
     "venue": "Prudential Center", "status": "FUT", "event_id": "2026020169",
     "sources": ["nhl-schedule-20261023"], "official_link":
         "https://www.nhl.com/gamecenter/lak-vs-njd/2026-10-24/2026020169"},
    {"key": "nhl-2026020170", "sport": "ice-hockey", "competition": "NHL 2026-27 regular season",
     "away": "SJS", "home": "BOS", "date": "2026-10-24", "time_utc": "2026-10-24T23:00:00Z",
     "venue": "TD Garden", "status": "FUT", "event_id": "2026020170",
     "sources": ["nhl-schedule-20261023"], "official_link":
         "https://www.nhl.com/gamecenter/sjs-vs-bos/2026-10-24/2026020170"},
    {"key": "nhl-2026020171", "sport": "ice-hockey", "competition": "NHL 2026-27 regular season",
     "away": "NYR", "home": "OTT", "date": "2026-10-24", "time_utc": "2026-10-24T23:00:00Z",
     "venue": "Canadian Tire Centre", "status": "FUT", "event_id": "2026020171",
     "sources": ["nhl-schedule-20261023"], "official_link":
         "https://www.nhl.com/gamecenter/nyr-vs-ott/2026-10-24/2026020171"},
    {"key": "nhl-2026020172", "sport": "ice-hockey", "competition": "NHL 2026-27 regular season",
     "away": "NSH", "home": "PIT", "date": "2026-10-24", "time_utc": "2026-10-24T23:00:00Z",
     "venue": "PPG Paints Arena", "status": "FUT", "event_id": "2026020172",
     "sources": ["nhl-schedule-20261023"], "official_link":
         "https://www.nhl.com/gamecenter/nsh-vs-pit/2026-10-24/2026020172"},
    {"key": "nhl-2026020173", "sport": "ice-hockey", "competition": "NHL 2026-27 regular season",
     "away": "BUF", "home": "WSH", "date": "2026-10-24", "time_utc": "2026-10-24T23:00:00Z",
     "venue": "Capital One Arena", "status": "FUT", "event_id": "2026020173",
     "sources": ["nhl-schedule-20261023"], "official_link":
         "https://www.nhl.com/gamecenter/buf-vs-wsh/2026-10-24/2026020173"},
    {"key": "nhl-2026020174", "sport": "ice-hockey", "competition": "NHL 2026-27 regular season",
     "away": None, "home": "CBJ", "date": "2026-10-24", "time_utc": "2026-10-24T23:00:00Z",
     "venue": "Nationwide Arena", "status": "FUT", "event_id": "2026020174",
     "sources": ["nhl-schedule-20261023"], "official_link":
         "https://api-web.nhle.com/v1/schedule/2026-10-23",
     "blank_fields": ["away"], "flag": "F-D7D-01"},

    # --- baseball (MLB World Series) -------------------------------------
    {"key": "mlb-849805", "sport": "baseball", "competition": "MLB 2026 World Series (game 1)",
     "away": "TB", "home": "MIL", "date": "2026-10-23", "time_utc": "2026-10-24T00:00:00Z",
     "venue": "American Family Field", "status": "Scheduled", "event_id": "849805",
     "sources": ["mlb-schedule-worldseries"], "official_link":
         "https://www.mlb.com/gameday/849805"},
    {"key": "mlb-849802", "sport": "baseball", "competition": "MLB 2026 World Series (game 2)",
     "away": "TB", "home": "MIL", "date": "2026-10-24", "time_utc": "2026-10-25T00:00:00Z",
     "venue": "American Family Field", "status": "Scheduled", "event_id": "849802",
     "sources": ["mlb-schedule-worldseries"], "official_link":
         "https://www.mlb.com/gameday/849802"},
    {"key": "mlb-849804", "sport": "baseball", "competition": "MLB 2026 World Series (game 3)",
     "away": "MIL", "home": "TB", "date": "2026-10-26", "time_utc": "2026-10-27T00:00:00Z",
     "venue": "Tropicana Field", "status": "Scheduled", "event_id": "849804",
     "sources": ["mlb-schedule-worldseries"], "official_link":
         "https://www.mlb.com/gameday/849804"},
    {"key": "mlb-849803", "sport": "baseball", "competition": "MLB 2026 World Series (game 4)",
     "away": "MIL", "home": "TB", "date": "2026-10-27", "time_utc": "2026-10-28T00:00:00Z",
     "venue": "Tropicana Field", "status": "Scheduled", "event_id": "849803",
     "sources": ["mlb-schedule-worldseries"], "official_link":
         "https://www.mlb.com/gameday/849803"},
    {"key": "mlb-849799", "sport": "baseball", "competition": "MLB 2026 World Series (game 5)",
     "away": "MIL", "home": "TB", "date": "2026-10-28", "time_utc": "2026-10-29T00:00:00Z",
     "venue": "Tropicana Field", "status": "Scheduled", "event_id": "849799",
     "sources": ["mlb-schedule-worldseries"], "official_link":
         "https://www.mlb.com/gameday/849799"},

    # --- basketball (EuroLeague Round 7) ---------------------------------
    {"key": "el-E2026-64", "sport": "basketball", "competition": "EuroLeague 2026-27 Round 7",
     "away": "BES", "home": "EFES", "date": "2026-10-22", "time_utc": "2026-10-22T17:30:00Z",
     "time_local": "19:30 CEST", "venue": None, "status": "scheduled", "event_id": "E2026/64",
     "sources": ["euroleague-round7"], "official_link":
         "https://www.euroleaguebasketball.net/euroleague/game-center/2026-27/anadolu-efes-istanbul-besiktas-istanbul/E2026/64/",
     "blank_fields": ["venue"], "flag": "F-D7D-02"},
    {"key": "el-E2026-65", "sport": "basketball", "competition": "EuroLeague 2026-27 Round 7",
     "away": "DUB", "home": "BAY", "date": "2026-10-22", "time_utc": "2026-10-22T18:00:00Z",
     "time_local": "20:00 CEST", "venue": None, "status": "scheduled", "event_id": "E2026/65",
     "sources": ["euroleague-round7"], "official_link":
         "https://www.euroleaguebasketball.net/euroleague/game-center/2026-27/fc-bayern-munich-dubai-basketball/E2026/65/",
     "blank_fields": ["venue"], "flag": "F-D7D-02"},
    {"key": "el-E2026-62", "sport": "basketball", "competition": "EuroLeague 2026-27 Round 7",
     "away": "MAD", "home": "MAC", "date": "2026-10-22", "time_utc": "2026-10-22T18:05:00Z",
     "time_local": "20:05 CEST", "venue": None, "status": "scheduled", "event_id": "E2026/62",
     "sources": ["euroleague-round7"], "official_link":
         "https://www.euroleaguebasketball.net/euroleague/game-center/2026-27/maccabi-rapyd-tel-aviv-real-madrid/E2026/62/",
     "blank_fields": ["venue"], "flag": "F-D7D-02"},
    {"key": "el-E2026-67", "sport": "basketball", "competition": "EuroLeague 2026-27 Round 7",
     "away": "BAS", "home": "PAO", "date": "2026-10-22", "time_utc": "2026-10-22T18:15:00Z",
     "time_local": "20:15 CEST", "venue": None, "status": "scheduled", "event_id": "E2026/67",
     "sources": ["euroleague-round7"], "official_link":
         "https://www.euroleaguebasketball.net/euroleague/game-center/2026-27/panathinaikos-aktor-athens-kosner-baskonia-vitoria-gasteiz/E2026/67/",
     "blank_fields": ["venue"], "flag": "F-D7D-02"},
    {"key": "el-E2026-63", "sport": "basketball", "competition": "EuroLeague 2026-27 Round 7",
     "away": "BAR", "home": "MIL", "date": "2026-10-22", "time_utc": "2026-10-22T18:30:00Z",
     "time_local": "20:30 CEST", "venue": None, "status": "scheduled", "event_id": "E2026/63",
     "sources": ["euroleague-round7"], "official_link":
         "https://www.euroleaguebasketball.net/euroleague/game-center/2026-27/armani-olimpia-milan-fc-barcelona/E2026/63/",
     "blank_fields": ["venue"], "flag": "F-D7D-02"},
    {"key": "el-E2026-66", "sport": "basketball", "competition": "EuroLeague 2026-27 Round 7",
     "away": "CZV", "home": "PAR", "date": "2026-10-22", "time_utc": "2026-10-22T18:45:00Z",
     "time_local": "20:45 CEST", "venue": None, "status": "scheduled", "event_id": "E2026/66",
     "sources": ["euroleague-round7"], "official_link":
         "https://www.euroleaguebasketball.net/euroleague/game-center/2026-27/partizan-mozzart-bet-belgrade-crvena-zvezda-meridianbet-belgrade/E2026/66/",
     "blank_fields": ["venue"], "flag": "F-D7D-02"},
    {"key": "el-E2026-68", "sport": "basketball", "competition": "EuroLeague 2026-27 Round 7",
     "away": "ASV", "home": "ZAL", "date": "2026-10-23", "time_utc": "2026-10-23T17:00:00Z",
     "time_local": "19:00 CEST", "venue": None, "status": "scheduled", "event_id": "E2026/68",
     "sources": ["euroleague-round7"], "official_link":
         "https://www.euroleaguebasketball.net/euroleague/game-center/2026-27/zalgiris-kaunas-ldlc-asvel-villeurbanne/E2026/68/",
     "blank_fields": ["venue"], "flag": "F-D7D-02"},
    {"key": "el-E2026-70", "sport": "basketball", "competition": "EuroLeague 2026-27 Round 7",
     "away": "FEN", "home": "OLY", "date": "2026-10-23", "time_utc": "2026-10-23T18:15:00Z",
     "time_local": "20:15 CEST", "venue": None, "status": "scheduled", "event_id": "E2026/70",
     "sources": ["euroleague-round7"], "official_link":
         "https://www.euroleaguebasketball.net/euroleague/game-center/2026-27/olympiacos-piraeus-fenerbahce-tarfin-istanbul/E2026/70/",
     "blank_fields": ["venue"], "flag": "F-D7D-02"},
    {"key": "el-E2026-69", "sport": "basketball", "competition": "EuroLeague 2026-27 Round 7",
     "away": "VAL", "home": "PARIS", "date": "2026-10-23", "time_utc": "2026-10-23T18:45:00Z",
     "time_local": "20:45 CEST", "venue": None, "status": "scheduled", "event_id": "E2026/69",
     "sources": ["euroleague-round7"], "official_link":
         "https://www.euroleaguebasketball.net/euroleague/game-center/2026-27/paris-basketball-valencia-basket/E2026/69/",
     "blank_fields": ["venue"], "flag": "F-D7D-02"},

    # --- tennis (WTA Ningbo Open, Friday 23 October 2026) ----------------
    {"key": "wta-ningbo-qf1", "sport": "tennis",
     "competition": "BNB Ningbo Open 2026 (WTA, Ningbo CHN, 19-25 Oct, $1,206,446, hard/Plexipave) - quarter-final, doubles",
     "away": "Erin Routliffe (NZL) / Aldila Sutjiadi (INA)",
     "home": "Ulrikke Eikeri (NOR) / Quinn Gleason (USA)",
     "date": "2026-10-23", "time_utc": None, "time_local": "Starting at 11:00 AM",
     "venue": "Center Court", "status": "scheduled", "event_id": "ningbo-qf-d1",
     "sources": ["wta-ningbo-op"],
     "official_link": "https://wtafiles.wtatennis.com/pdf/draws/2026/2092/OP.pdf",
     "blank_fields": ["time_utc"], "flag": "F-D7D-03", "side_label": ("listed first", "listed second")},
    {"key": "wta-ningbo-qf2", "sport": "tennis",
     "competition": "BNB Ningbo Open 2026 (WTA) - quarter-final, singles",
     "away": "Sara Bejlek (CZE)", "home": "Marie Bouzkova (CZE)",
     "date": "2026-10-23", "time_utc": None, "time_local": "Not before 1:00 PM",
     "venue": "Center Court", "status": "scheduled", "event_id": "ningbo-qf-s1",
     "sources": ["wta-ningbo-op"],
     "official_link": "https://wtafiles.wtatennis.com/pdf/draws/2026/2092/OP.pdf",
     "blank_fields": ["time_utc"], "flag": "F-D7D-03", "side_label": ("listed first", "listed second")},
    {"key": "wta-ningbo-qf3", "sport": "tennis",
     "competition": "BNB Ningbo Open 2026 (WTA) - quarter-final, singles",
     "away": "Leylah Fernandez (CAN)", "home": "Ekaterina Alexandrova",
     "date": "2026-10-23", "time_utc": None, "time_local": "Followed by (no clock time printed)",
     "venue": "Center Court", "status": "scheduled", "event_id": "ningbo-qf-s2",
     "sources": ["wta-ningbo-op"],
     "official_link": "https://wtafiles.wtatennis.com/pdf/draws/2026/2092/OP.pdf",
     "blank_fields": ["time_utc"], "flag": "F-D7D-04",
     "side_label": ("listed first", "listed second"),
     "note": "the official PDF prints no country code after Ekaterina Alexandrova, so none is published"},
    {"key": "wta-ningbo-qf4", "sport": "tennis",
     "competition": "BNB Ningbo Open 2026 (WTA) - quarter-final, singles",
     "away": "[4] Iva Jovic (USA)", "home": "[6] Diana Shnaider",
     "date": "2026-10-23", "time_utc": None, "time_local": "Not before 4:00 PM",
     "venue": "Center Court", "status": "scheduled", "event_id": "ningbo-qf-s3",
     "sources": ["wta-ningbo-op"],
     "official_link": "https://wtafiles.wtatennis.com/pdf/draws/2026/2092/OP.pdf",
     "blank_fields": ["time_utc"], "flag": "F-D7D-04",
     "side_label": ("listed first", "listed second"),
     "note": "the official PDF prints no country code after Diana Shnaider, so none is published"},
    {"key": "wta-ningbo-qf5", "sport": "tennis",
     "competition": "BNB Ningbo Open 2026 (WTA) - quarter-final, singles",
     "away": "[1] Elena Rybakina (KAZ)", "home": "[Q] Katarzyna Kawa (POL)",
     "date": "2026-10-23", "time_utc": None, "time_local": "Not before 7:00 PM",
     "venue": "Center Court", "status": "scheduled", "event_id": "ningbo-qf-s4",
     "sources": ["wta-ningbo-op"],
     "official_link": "https://wtafiles.wtatennis.com/pdf/draws/2026/2092/OP.pdf",
     "blank_fields": ["time_utc"], "flag": "F-D7D-05",
     "side_label": ("listed first", "listed second"),
     "note": "the official PDF text layer concatenates the second player's surname and country code as "
             "'KAWAPOL'; it is split here as printed-name 'Katarzyna Kawa' and code 'POL' and the "
             "artefact is flagged"},

    # --- tennis (ATP event 7485 order of play, Thursday 22 October 2026) --
    {"key": "atp-7485-s1", "sport": "tennis",
     "competition": "ATP Tour 2026 event 7485 order of play - singles (tournament name not printed on the official PDF)",
     "away": "Raphael Collignon (BEL)", "home": "[2] Jiri Lehecka (CZE)",
     "date": "2026-10-22", "time_utc": None, "time_local": "Starts At 13:30",
     "venue": "Centre Court", "status": "scheduled", "event_id": "7485-centre-1",
     "sources": ["atp-brussels-op"],
     "official_link": "https://www.protennislive.com/posting/2026/7485/op.pdf",
     "blank_fields": ["time_utc", "competition_name", "city"], "flag": "F-D7D-06",
     "side_label": ("listed first", "listed second")},
    {"key": "atp-7485-s2", "sport": "tennis",
     "competition": "ATP Tour 2026 event 7485 order of play - singles",
     "away": "[WC] David Goffin (BEL)", "home": "[5] Alex Michelsen (USA)",
     "date": "2026-10-22", "time_utc": None, "time_local": "Followed By",
     "venue": "Centre Court", "status": "scheduled", "event_id": "7485-centre-2",
     "sources": ["atp-brussels-op"],
     "official_link": "https://www.protennislive.com/posting/2026/7485/op.pdf",
     "blank_fields": ["time_utc", "competition_name", "city"], "flag": "F-D7D-06",
     "side_label": ("listed first", "listed second")},
    {"key": "atp-7485-s3", "sport": "tennis",
     "competition": "ATP Tour 2026 event 7485 order of play - singles",
     "away": "Damir Dzumhur (BIH)", "home": "[6] Zizou Bergs (BEL)",
     "date": "2026-10-22", "time_utc": None, "time_local": "Not Before 17:00",
     "venue": "Centre Court", "status": "scheduled", "event_id": "7485-centre-3",
     "sources": ["atp-brussels-op"],
     "official_link": "https://www.protennislive.com/posting/2026/7485/op.pdf",
     "blank_fields": ["time_utc", "competition_name", "city"], "flag": "F-D7D-06",
     "side_label": ("listed first", "listed second")},
    {"key": "atp-7485-d1", "sport": "tennis",
     "competition": "ATP Tour 2026 event 7485 order of play - doubles",
     "away": "[1] Guido Andreozzi (ARG) / Manuel Guinard (FRA)",
     "home": "Nicolas Barrientos (COL) / David Pel (NED)",
     "date": "2026-10-22", "time_utc": None, "time_local": "Starts At 15:00",
     "venue": "Centre Court", "status": "scheduled", "event_id": "7485-centre-d1",
     "sources": ["atp-brussels-op"],
     "official_link": "https://www.protennislive.com/posting/2026/7485/op.pdf",
     "blank_fields": ["time_utc", "competition_name", "city"], "flag": "F-D7D-06",
     "side_label": ("listed first", "listed second")},
    {"key": "atp-7485-d2", "sport": "tennis",
     "competition": "ATP Tour 2026 event 7485 order of play - doubles",
     "away": "Constantin Frantzen (GER) / Robert Galloway (USA)",
     "home": "[WC] Raphael Collignon (BEL) / David Goffin (BEL)",
     "date": "2026-10-22", "time_utc": None, "time_local": "Followed By",
     "venue": "Centre Court", "status": "scheduled", "event_id": "7485-centre-d2",
     "sources": ["atp-brussels-op"],
     "official_link": "https://www.protennislive.com/posting/2026/7485/op.pdf",
     "blank_fields": ["time_utc", "competition_name", "city"], "flag": "F-D7D-06",
     "side_label": ("listed first", "listed second")},

    # --- cricket (PCB tri-nation ODI series 2026/27) ---------------------
    {"key": "pcb-36933", "sport": "cricket",
     "competition": "Pakistan, England and Sri Lanka Tri-nation ODI Series 2026/27 (3rd match)",
     "away": "Sri Lanka", "home": "England", "date": "2026-10-22", "time_utc": None,
     "time_local": None, "venue": "Rawalpindi Cricket Stadium, Rawalpindi", "status": None,
     "event_id": "36933", "sources": ["pcb-tri-nation-odi"], "official_link":
         "https://www.pcb.com.pk/pakistan-england-and-sri-lanka-trination-odi-series-202627/match/36933.html",
     "blank_fields": ["time_utc", "time_local", "status"], "flag": "F-D7D-07"},
    {"key": "pcb-match4", "sport": "cricket",
     "competition": "Pakistan, England and Sri Lanka Tri-nation ODI Series 2026/27 (4th match)",
     "away": "Pakistan", "home": "England", "date": "2026-10-25", "time_utc": None,
     "time_local": None, "venue": "Gaddafi Stadium, Lahore", "status": None,
     "event_id": None, "sources": ["pcb-tri-nation-odi"], "official_link":
         "https://www.pcb.com.pk/pakistan-england-and-sri-lanka-trination-odi-series-202627/tournament/1465.html",
     "blank_fields": ["time_utc", "time_local", "status", "event_id"], "flag": "F-D7D-08"},
    {"key": "pcb-match5", "sport": "cricket",
     "competition": "Pakistan, England and Sri Lanka Tri-nation ODI Series 2026/27 (5th match)",
     "away": "Pakistan", "home": "Sri Lanka", "date": "2026-10-27", "time_utc": None,
     "time_local": None, "venue": "Gaddafi Stadium, Lahore", "status": None,
     "event_id": None, "sources": ["pcb-tri-nation-odi"], "official_link":
         "https://www.pcb.com.pk/pakistan-england-and-sri-lanka-trination-odi-series-202627/tournament/1465.html",
     "blank_fields": ["time_utc", "time_local", "status", "event_id"], "flag": "F-D7D-08"},
    {"key": "pcb-match6", "sport": "cricket",
     "competition": "Pakistan, England and Sri Lanka Tri-nation ODI Series 2026/27 (6th match)",
     "away": "Sri Lanka", "home": "England", "date": "2026-10-29", "time_utc": None,
     "time_local": None, "venue": "Gaddafi Stadium, Lahore", "status": None,
     "event_id": None, "sources": ["pcb-tri-nation-odi"], "official_link":
         "https://www.pcb.com.pk/pakistan-england-and-sri-lanka-trination-odi-series-202627/tournament/1465.html",
     "blank_fields": ["time_utc", "time_local", "status", "event_id"], "flag": "F-D7D-08"},

    # --- rugby league (IRL, 23-25 Oct 2026) ------------------------------
    {"key": "irl-2586", "sport": "rugby-league",
     "competition": "IRL Women's Rugby League World Cup 2026, Round 2",
     "away": "Samoa", "home": "Wales", "date": "2026-10-23", "time_utc": None,
     "time_local": "17:50", "venue": "CommBank Stadium, Sydney", "status": None,
     "event_id": "2586", "sources": ["irl-fixtures"],
     "official_link": "https://www.intrl.sport/match-details/2586",
     "blank_fields": ["time_utc", "status"], "flag": "F-D7D-09"},
    {"key": "irl-2569", "sport": "rugby-league",
     "competition": "IRL Men's Rugby League World Cup 2026, Round 2, pool B",
     "away": "Tonga", "home": "Lebanon", "date": "2026-10-23", "time_utc": None,
     "time_local": "20:05", "venue": "CommBank Stadium, Sydney", "status": None,
     "event_id": "2569", "sources": ["irl-fixtures", "rlwc2026-draws"],
     "official_link": "https://www.intrl.sport/match-details/2569",
     "corroborating_link": "https://www.rlwc2026.com/draw/mens/2026/round-2/tonga-v-lebanon",
     "blank_fields": ["time_utc", "status"], "flag": "F-D7D-09"},
    {"key": "irl-2587", "sport": "rugby-league",
     "competition": "IRL Women's Rugby League World Cup 2026, Round 2",
     "away": "Fiji", "home": "Papua New Guinea", "date": "2026-10-24", "time_utc": None,
     "time_local": "12:15", "venue": "Santos National Football Stadium, Port Moresby",
     "status": None, "event_id": "2587", "sources": ["irl-fixtures"],
     "official_link": "https://www.intrl.sport/match-details/2587",
     "blank_fields": ["time_utc", "status"], "flag": "F-D7D-09"},
    {"key": "irl-2661", "sport": "rugby-league",
     "competition": "Senior International Match (Men)",
     "away": "Scotland", "home": "Wales", "date": "2026-10-24", "time_utc": None,
     "time_local": "14:00", "venue": "Biggar RFC", "status": None, "event_id": "2661",
     "sources": ["irl-fixtures"], "official_link": "https://www.intrl.sport/match-details/2661",
     "blank_fields": ["time_utc", "status"], "flag": "F-D7D-09"},
    {"key": "irl-2664", "sport": "rugby-league",
     "competition": "European Championship B (Men)",
     "away": "Netherlands", "home": "Serbia", "date": "2026-10-24", "time_utc": None,
     "time_local": "14:00", "venue": "FK Zemun Stadium", "status": None, "event_id": "2664",
     "sources": ["irl-fixtures"], "official_link": "https://www.intrl.sport/match-details/2664",
     "blank_fields": ["time_utc", "status"], "flag": "F-D7D-09"},
    {"key": "irl-2570", "sport": "rugby-league",
     "competition": "IRL Men's Rugby League World Cup 2026, Round 2, pool B",
     "away": "Papua New Guinea", "home": "Samoa", "date": "2026-10-24", "time_utc": None,
     "time_local": "14:25", "venue": "Santos National Football Stadium, Port Moresby",
     "status": None, "event_id": "2570", "sources": ["irl-fixtures", "rlwc2026-draws"],
     "official_link": "https://www.intrl.sport/match-details/2570",
     "corroborating_link": "https://www.rlwc2026.com/draw/mens/2026/round-2/papua-new-guinea-v-samoa",
     "blank_fields": ["time_utc", "status"], "flag": "F-D7D-09"},
    {"key": "irl-2571", "sport": "rugby-league",
     "competition": "IRL Men's Rugby League World Cup 2026, Round 2, pool B",
     "away": "England", "home": "France", "date": "2026-10-24", "time_utc": None,
     "time_local": "14:35", "venue": "HBF Park, Perth", "status": None, "event_id": "2571",
     "sources": ["irl-fixtures", "rlwc2026-draws"],
     "official_link": "https://www.intrl.sport/match-details/2571",
     "corroborating_link": "https://www.rlwc2026.com/draw/mens/2026/round-2/england-v-france",
     "blank_fields": ["time_utc", "status"], "flag": "F-D7D-09"},
    {"key": "irl-2646", "sport": "rugby-league",
     "competition": "European Championship D (Men)",
     "away": "Italy", "home": "Czechia", "date": "2026-10-24", "time_utc": None,
     "time_local": "15:00", "venue": "Stadio Giovanni Invernizzi, Abbiategrasso",
     "status": None, "event_id": "2646", "sources": ["irl-fixtures"],
     "official_link": "https://www.intrl.sport/match-details/2646",
     "blank_fields": ["time_utc", "status"], "flag": "F-D7D-09"},
    {"key": "irl-2588", "sport": "rugby-league",
     "competition": "IRL Women's Rugby League World Cup 2026, Round 2",
     "away": "Australia", "home": "England", "date": "2026-10-24", "time_utc": None,
     "time_local": "17:05", "venue": "HBF Park, Perth", "status": None, "event_id": "2588",
     "sources": ["irl-fixtures"], "official_link": "https://www.intrl.sport/match-details/2588",
     "blank_fields": ["time_utc", "status"], "flag": "F-D7D-09"},
    {"key": "irl-2665", "sport": "rugby-league",
     "competition": "Senior International Match (Women)",
     "away": "Malta", "home": "Philippines", "date": "2026-10-25", "time_utc": None,
     "time_local": "15:00", "venue": "Croom Oval", "status": None, "event_id": "2665",
     "sources": ["irl-fixtures"], "official_link": "https://www.intrl.sport/match-details/2665",
     "blank_fields": ["time_utc", "status"], "flag": "F-D7D-09"},
    {"key": "irl-2589", "sport": "rugby-league",
     "competition": "IRL Women's Rugby League World Cup 2026, Round 2",
     "away": "New Zealand", "home": "France", "date": "2026-10-25", "time_utc": None,
     "time_local": "15:50", "venue": "One NZ Stadium, Christchurch", "status": None,
     "event_id": "2589", "sources": ["irl-fixtures"],
     "official_link": "https://www.intrl.sport/match-details/2589",
     "blank_fields": ["time_utc", "status"], "flag": "F-D7D-09"},
    {"key": "irl-2572", "sport": "rugby-league",
     "competition": "IRL Men's Rugby League World Cup 2026, Round 2, pool A",
     "away": "New Zealand", "home": "Cook Islands", "date": "2026-10-25", "time_utc": None,
     "time_local": "18:05", "venue": "One NZ Stadium, Christchurch", "status": None,
     "event_id": "2572", "sources": ["irl-fixtures", "rlwc2026-draws"],
     "official_link": "https://www.intrl.sport/match-details/2572",
     "corroborating_link": "https://www.rlwc2026.com/draw/mens/2026/round-2/new-zealand-v-cook-islands",
     "blank_fields": ["time_utc", "status"], "flag": "F-D7D-09"},
    {"key": "irl-2573", "sport": "rugby-league",
     "competition": "IRL Men's Rugby League World Cup 2026, Round 2, pool A",
     "away": "Australia", "home": "Fiji", "date": "2026-10-25", "time_utc": None,
     "time_local": "19:05", "venue": "Suncorp Stadium, Brisbane", "status": None,
     "event_id": "2573", "sources": ["irl-fixtures", "rlwc2026-draws"],
     "official_link": "https://www.intrl.sport/match-details/2573",
     "corroborating_link": "https://www.rlwc2026.com/draw/mens/2026/round-2/australia-v-fiji",
     "blank_fields": ["time_utc", "status"], "flag": "F-D7D-09"},
]

# Official context sentences read this session, used only in prediction prose.
# Each entry quotes or closely paraphrases the official page named in "source".
CONTEXT = {
    "el-E2026-65": [
        "Euroleague Basketball's Round 7 Game Center records Bayern Munich as 2-4 and Dubai Basketball "
        "as 4-2 before this fixture.",
        "The same official preview rates Dubai's defence fifth in the competition at 82.2 points allowed "
        "per game and Dwayne Bacon's 17.8 points per game as third-best in the league.",
        "It also records Bayern's Duane Washington at 16.8 points per game, sixth in scoring despite "
        "coming off the bench.",
    ],
    "el-E2026-64": [
        "Euroleague Basketball lists Anadolu Efes at 2-4 and Besiktas at 3-3 through six rounds.",
        "The official preview states Efes are sixth in the league in points allowed at 85.0 per game and "
        "that Cam Payne has been playing in place of the injured Mike James.",
        "It records Besiktas as third in the competition in scoring at 92.3 points per game and notes "
        "Lonnie Walker signed with the club last week.",
    ],
    "el-E2026-66": [
        "Euroleague Basketball's Round 7 Game Center gives Partizan a 3-3 record and Crvena Zvezda 4-2.",
        "The official preview states Partizan opened with three straight wins and have since dropped "
        "three in a row, while Zvezda lost their first two before reeling off four straight wins.",
        "It also records that both clubs are among the competition's best defences and that Zvezda could "
        "have new signing Christian Koloko in uniform.",
    ],
    "el-E2026-63": [
        "Euroleague Basketball lists Armani Olimpia Milan at 1-5, having lost four in a row, and FC "
        "Barcelona at 3-3 after splitting a pair of tight home games.",
        "The official preview states it should be a close game and that the clubs split home wins last "
        "season with both games decided by a single possession.",
    ],
    "el-E2026-62": [
        "Euroleague Basketball lists Maccabi Rapyd Tel Aviv at 2-4 and Real Madrid at 3-3.",
        "The official preview states Madrid have won three in a row but are 1-4 away from home, and that "
        "the home team has won each of the last five meetings between these clubs.",
    ],
    "el-E2026-67": [
        "Euroleague Basketball lists Panathinaikos AKTOR Athens at 5-1 and Kosner Baskonia at 1-5.",
        "The official preview records Panathinaikos' defence as a league-low 73.0 points allowed per game "
        "and five straight home wins over Baskonia, who last won in Athens in March 2021.",
    ],
    "el-E2026-69": [
        "Euroleague Basketball lists Paris Basketball at 1-5 on a three-game losing streak and Valencia "
        "Basket at 5-1 coming off their first loss.",
        "The official preview records Valencia as the competition's top offence at 98.3 points per game "
        "and Paris' Nadir Hifi as the league's top scorer at 20.2 points per game.",
    ],
    "el-E2026-70": [
        "Euroleague Basketball lists Olympiacos Piraeus and Fenerbahce Tarfin Istanbul both at 5-1, tied "
        "with Panathinaikos for the competition's best record.",
        "The official preview rates Olympiacos second in scoring at 98.2 points per game and Fenerbahce "
        "second in defence at 74.5 points allowed per game, and records three straight Olympiacos wins "
        "over Fenerbahce including the 2026 Final Four semi-final.",
    ],
    "el-E2026-68": [
        "Euroleague Basketball lists Zalgiris Kaunas and LDLC ASVEL Villeurbanne both at 2-4.",
        "The official preview records ASVEL as allowing a league-high 95.3 points per game through six "
        "rounds.",
    ],
    "nhl-2026020170": [
        "The NHL's official standings for 2026-10-21 (published 2026-10-22T12:00:45Z) give Boston 7-2-1 "
        "with 15 points from 10 games, 36 goals for and 22 against.",
        "The same official standings give San Jose 5-4-1 with 11 points from 10 games, 27 goals for and "
        "35 against, the league's 16th-ranked club.",
        "The NHL's official scoreboard records San Jose losing 1-3 at Toronto on 19 October 2026 and "
        "winning 4-3 in overtime at Montreal on 20 October 2026.",
    ],
    "nhl-2026020154": [
        "The NHL's official standings for 2026-10-21 give Boston 7-2-1 (15 points, 36 goals for, 22 "
        "against) and Nashville 3-2-3 (9 points, 23 goals for, 24 against from eight games).",
    ],
    "nhl-2026020156": [
        "The NHL's official standings for 2026-10-21 give Ottawa 7-3-0 (14 points, 29 goals for, 24 "
        "against) and San Jose 5-4-1 (11 points, 27 goals for, 35 against).",
        "The NHL's official scoreboard records San Jose losing 1-3 at Toronto on 19 October and winning "
        "4-3 in overtime at Montreal on 20 October 2026.",
    ],
    "mlb-849805": [
        "MLB's official Stats API standings give the Tampa Bay Rays a 98-64 2026 regular season with 736 "
        "runs scored and 650 allowed, first in the AL East.",
        "The same official standings give the Milwaukee Brewers 103-59 with 832 runs scored and 618 "
        "allowed, first in the NL Central.",
        "MLB's official schedule lists the World Series as Rays at Brewers for games 1 and 2 at American "
        "Family Field, then Brewers at Rays for games 3 to 5 at Tropicana Field.",
    ],
}

# ------------------------------------------------------- coverage gaps
GAPS = [
    {"sport": "aussie-rules", "name": "Australian rules", "olbg_hub":
        "https://www.olbg.com/betting-tips/Aussie_Rules/22",
     "attempted": "https://www.afl.com.au/aflw/fixture", "attempts": 2,
     "reason": "Both chunks of the official AFLW fixture page contained only navigation, partner and "
               "footer markup; the fixture cards are rendered client-side, so no AFLW row could be read.",
     "status": "attempted, page not machine-readable"},
    {"sport": "darts", "name": "Darts", "olbg_hub": "https://www.olbg.com/betting-tips/Darts/15",
     "attempted": "https://www.pdc.tv/news/2026/october/19/2026-machineseeker-european-championship-schedule-confirmed/",
     "attempts": 2,
     "reason": "The official PDC article returned only its cookie-consent payload (vendor and cookie "
               "tables across 7 chunks); no schedule content was readable.",
     "status": "attempted, content behind consent overlay"},
    {"sport": "snooker", "name": "Snooker", "olbg_hub": "https://www.olbg.com/betting-tips/Snooker/8",
     "attempted": "https://www.wst.tv/matches/", "attempts": 1,
     "reason": "Chunk 0 of 3 on the official World Snooker Tour match list returned the completed Round 1 "
               "rows of the BetVictor Northern Ireland Open 2026 (18-19 Oct). The rows for the rounds "
               "still to be played sit in chunks 1-2, which this desk did not read inside its budget, so "
               "no upcoming snooker fixture is published.",
     "status": "partially read, upcoming rows not published"},
    {"sport": "rugby-union", "name": "Rugby union", "olbg_hub":
        "https://www.olbg.com/betting-tips/Rugby_Union/9", "attempted": None, "attempts": 0,
     "reason": "No rugby union fixture page was fetched this session; the desk's retrieval budget was "
               "spent on ice hockey, baseball, basketball, tennis, cricket and rugby league. Absence of "
               "rows is not a finding that no fixtures exist.",
     "status": "not attempted this session"},
    {"sport": "golf", "name": "Golf", "olbg_hub": "https://www.olbg.com/betting-tips/Golf/5",
     "attempted": None, "attempts": 0,
     "reason": "Not attempted this session (budget). No tournament, field or price is published.",
     "status": "not attempted this session"},
    {"sport": "motor-racing", "name": "Motor racing", "olbg_hub":
        "https://www.olbg.com/betting-tips/Motor_Racing/14", "attempted": None, "attempts": 0,
     "reason": "Not attempted this session (budget). No session, grid or price is published.",
     "status": "not attempted this session"},
    {"sport": "handball", "name": "Handball", "olbg_hub":
        "https://www.olbg.com/betting-tips/Handball/20", "attempted": None, "attempts": 0,
     "reason": "Not attempted this session (budget).", "status": "not attempted this session"},
    {"sport": "volleyball", "name": "Volleyball", "olbg_hub":
        "https://www.olbg.com/betting-tips/Volleyball/21", "attempted": None, "attempts": 0,
     "reason": "Not attempted this session (budget).", "status": "not attempted this session"},
    {"sport": "esports", "name": "eSports", "olbg_hub": "https://www.olbg.com/betting-tips/eSports/23",
     "attempted": None, "attempts": 0,
     "reason": "Not attempted this session (budget).", "status": "not attempted this session"},
    {"sport": "gaelic-football", "name": "Gaelic football", "olbg_hub":
        "https://www.olbg.com/betting-tips/Gaelic_Football/25", "attempted": None, "attempts": 0,
     "reason": "Not attempted this session (budget).", "status": "not attempted this session"},
    {"sport": "greyhounds", "name": "Greyhounds", "olbg_hub":
        "https://www.olbg.com/betting-tips/Greyhounds/28", "attempted": None, "attempts": 0,
     "reason": "Not attempted this session (budget).", "status": "not attempted this session"},
    {"sport": "basketball-nba", "name": "Basketball - NBA subset", "olbg_hub":
        "https://www.olbg.com/betting-tips/Basketball/4",
     "attempted": "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json",
     "attempts": 1,
     "reason": "The official NBA CDN scoreboard returned HTTP 500. A failed request is not a "
               "zero-fixture finding; basketball is covered for this desk by EuroLeague Round 7 only.",
     "status": "attempted, HTTP 500"},
]

SPORT_NAMES = {
    "ice-hockey": "Ice hockey", "baseball": "Baseball", "basketball": "Basketball",
    "tennis": "Tennis", "cricket": "Cricket", "rugby-league": "Rugby league",
    "rugby-union": "Rugby union", "golf": "Golf", "snooker": "Snooker", "darts": "Darts",
    "handball": "Handball", "volleyball": "Volleyball", "aussie-rules": "Australian rules",
    "esports": "eSports", "gaelic-football": "Gaelic football", "greyhounds": "Greyhounds",
    "motor-racing": "Motor racing",
}
SPORT_OLBG = {
    "ice-hockey": "https://www.olbg.com/betting-tips/Ice_Hockey/13",
    "baseball": "https://www.olbg.com/betting-tips/Baseball/12",
    "basketball": "https://www.olbg.com/betting-tips/Basketball/4",
    "tennis": "https://www.olbg.com/betting-tips/Tennis/3",
    "cricket": "https://www.olbg.com/betting-tips/Cricket/7",
    "rugby-league": "https://www.olbg.com/betting-tips/Rugby_League/10",
    "rugby-union": "https://www.olbg.com/betting-tips/Rugby_Union/9",
    "golf": "https://www.olbg.com/betting-tips/Golf/5",
    "snooker": "https://www.olbg.com/betting-tips/Snooker/8",
    "darts": "https://www.olbg.com/betting-tips/Darts/15",
    "handball": "https://www.olbg.com/betting-tips/Handball/20",
    "volleyball": "https://www.olbg.com/betting-tips/Volleyball/21",
    "aussie-rules": "https://www.olbg.com/betting-tips/Aussie_Rules/22",
    "esports": "https://www.olbg.com/betting-tips/eSports/23",
    "gaelic-football": "https://www.olbg.com/betting-tips/Gaelic_Football/25",
    "greyhounds": "https://www.olbg.com/betting-tips/Greyhounds/28",
    "motor-racing": "https://www.olbg.com/betting-tips/Motor_Racing/14",
}

FLAGS = {
    "F-D7D-01": "NHL game rows 2026020158 (22 Oct, PPG Paints Arena) and 2026020174 (24 Oct, Nationwide "
                "Arena) were read only as far as their venue and broadcast blocks; the official away club "
                "was not inside the chunks this desk read, so the away side is published blank and the "
                "row is unpriced. Recheck: https://api-web.nhle.com/v1/schedule/2026-10-22 and "
                "https://api-web.nhle.com/v1/schedule/2026-10-23",
    "F-D7D-02": "The official EuroLeague Round 7 Game Center preview publishes club records, start times "
                "and game-centre links but no arena name, so venue is blank on all nine basketball rows. "
                "Recheck each game-centre link on the row.",
    "F-D7D-03": "The official WTA order of play prints clock times with no timezone label, so no UTC "
                "start is published for the BNB Ningbo Open rows and they are unpriced.",
    "F-D7D-04": "Two official WTA order-of-play rows carry no country code for one player (Ekaterina "
                "Alexandrova, Diana Shnaider); the code is left blank rather than assumed.",
    "F-D7D-05": "The official WTA order-of-play PDF text layer concatenates surname and country code as "
                "'KAWAPOL'; the split published here is a transcription of the printed token and is "
                "flagged for manual review against the PDF.",
    "F-D7D-06": "The official ATP order-of-play PDF for event 7485 prints no tournament name, host city, "
                "surface or timezone, so those fields are blank and the five rows are unpriced. The event "
                "number is the only official identifier available.",
    "F-D7D-07": "The official PCB tournament page publishes dates, teams and grounds but no start time, "
                "timezone or match status for the tri-nation ODI series, so those fields are blank.",
    "F-D7D-08": "PCB matches 4, 5 and 6 (25, 27 and 29 Oct) have no match-centre link on the official "
                "tournament page - only the first three matches are hyperlinked - so no official match id "
                "is published for them.",
    "F-D7D-09": "IRL publishes kick-off clocks with no timezone label. Independent official corroboration "
                "(rlwc2026.com) renders the same fixtures in the retrieval environment's own timezone, so "
                "no UTC start is published for any rugby league row and none is priced.",
    "F-D7D-10": "Brief-rule tension: a model probability above 70% is arithmetically a price shorter than "
                "-233, while the brief's window starts at -250, so the literal intersection is only "
                "-250 to -233 (70.0%-71.4%). Both readings are published: gate A (literal) and gate B "
                "(in-window evidence-earned High).",
    "F-D7D-11": "Eleven of the seventeen in-scope sports have no rows in this desk. Each gap on the "
                "Flagged page carries the attempted official URL and the specific failure, or is labelled "
                "'not attempted this session'. A gap is not a finding that the sport has no fixtures.",
    "F-D7D-12": "No bookmaker price, availability or edge is claimed anywhere in this desk. Every number "
                "in the price columns is an originated fair price computed from the official inputs named "
                "on the row. Nothing here is a quote from OLBG.com or from any operator; OLBG was used for "
                "sport and hub discovery only.",
    "F-D7D-13": "The five World Series fixtures originate byte-identical lines (Milwaukee 55.54% / -125 "
                "in every game) because the only official team input read this session is the 2026 "
                "regular-season run differential for both clubs: no starting pitcher, bullpen, park or "
                "rest-day figure was read, and none was invented. The series is priced once, not five "
                "times, and every row says so. Recheck: https://statsapi.mlb.com/api/v1/standings and "
                "each game's official schedule row.",
    "F-D7D-14": "Ice hockey predictions cite club-level official facts only (standings, goal totals, "
                "streak codes and the five completed results on the official scoreboard). No official "
                "NHL injury report or roster page was read this session, so no goaltender, lineup or "
                "player-availability claim is made for any hockey pick.",
    "F-D7D-15": "Confidence labels attach to the winner market of each fixture, per the brief's "
                "'pick a match winner and label each with a confidence level'. Derivative markets "
                "(3-way regulation, handicap, match total) are published with probability, fair decimal "
                "and fair American prices but no match confidence label, and prose predictions are "
                "written for the seven High winner picks plus the single literal Gate A derivative "
                "selection (Pittsburgh +1.5 goals). The other derivative rows that clear p>=0.60 are "
                "listed on the High-confidence page with their prices and inputs instead of prose.",
    "F-D7D-16": "nhl-poisson-v1 and mlb-poisson-v1 are independent-Poisson models with no "
                "out-of-sample calibration, no home-ice or home-field adjustment and no correlation "
                "between the two sides' scoring. Totals and handicap lines inherited from them "
                "(expected totals 5.43-6.72 goals in hockey, 8.75 runs in baseball) are therefore "
                "model artefacts as much as reads, and no edge is claimed against any operator price.",
}
