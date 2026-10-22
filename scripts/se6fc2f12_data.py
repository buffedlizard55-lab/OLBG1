"""Session e6fc2f12-olbg1 — curated official-source inputs.

Every value in this module was transcribed by hand from a payload fetched in this
session through the Arena fetch tool. Each block records the exact URL, the UTC
time the read happened, and what the read was used for. Nothing here is recalled
from memory or copied from another session's desk.

Verification rules applied to every block:
  * only values actually visible in the fetched payload are transcribed;
  * a field that was not visible stays absent, and the affected rows are left
    blank and flagged downstream (see se6fc2f12_model and the Flagged page);
  * derived values (win%, shrunk strength, expected goals) are computed in code
    and labelled as estimates, never presented as sourced facts.

Consistency checks live in se6fc2f12_validate.py:
  * NHL: wins + regulation losses + OT losses == games played, for all 32 clubs.
  * URC: W + D + L == played, for all 16 clubs.
  * MLB: wins + losses == 162 for both clubs.
"""

READ_AT = "2026-10-22T12:20:00Z"   # conservative upper bound for every read below

SOURCES = [
    {
        "id": "nhl-team-summary",
        "name": "NHL official statistics API — team summary, 2026-27 regular season",
        "url": "https://api.nhle.com/stats/rest/en/team/summary?isAggregate=false&isGame=false"
               "&sort=%5B%7B%22property%22%3A%22points%22%2C%22direction%22%3A%22DESC%22%7D%5D"
               "&start=0&limit=32&cayenneExp=seasonId%3D20262027%20and%20gameTypeId%3D2",
        "publisher": "National Hockey League",
        "official": True,
        "kind": "league API (JSON)",
        "used_for": "Games played, wins, regulation losses, overtime/shootout losses, goals for, "
                    "goals against for all 32 clubs.",
        "read_at": READ_AT,
    },
    {
        "id": "nhl-game-log",
        "name": "NHL official statistics API — game index, 2026-27",
        "url": "https://api.nhle.com/stats/rest/en/game?isAggregate=false&isGame=true"
               "&sort=%5B%7B%22property%22%3A%22gameDate%22%2C%22direction%22%3A%22ASC%22%7D%5D"
               "&start=0&limit=100&cayenneExp=season%3D20262027%20and%20gameDate%3E%3D%222026-10-22%22"
               "%20and%20gameDate%3C%3D%222026-10-29%22",
        "publisher": "National Hockey League",
        "official": True,
        "kind": "league API (JSON)",
        "used_for": "Fixture list, club pairing and Eastern start time, 22–29 October 2026.",
        "read_at": READ_AT,
    },
    {
        "id": "nhl-schedule-day",
        "name": "NHL official statistics API — game index, 22 October 2026",
        "url": "https://api.nhle.com/stats/rest/en/game?isAggregate=false&isGame=true"
               "&sort=%5B%7B%22property%22%3A%22gameDate%22%2C%22direction%22%3A%22ASC%22%7D%5D"
               "&start=0&limit=60&cayenneExp=season%3D20262027%20and%20gameDate%3E%3D%222026-10-22%22"
               "%20and%20gameDate%3C%3D%222026-10-23%22",
        "publisher": "National Hockey League",
        "official": True,
        "kind": "league API (JSON)",
        "used_for": "The twelve 22 October fixtures and their Eastern start times.",
        "read_at": READ_AT,
    },
    {
        "id": "nhl-standings-web",
        "name": "NHL standings endpoint (club names, streak and last-ten fields)",
        "url": "https://api-web.nhle.com/v1/standings/2026-10-21",
        "publisher": "National Hockey League",
        "official": True,
        "kind": "league API (JSON)",
        "used_for": "Cross-check of club identity and the last-ten / streak fields quoted in prose.",
        "read_at": READ_AT,
    },
    {
        "id": "mlb-standings",
        "name": "MLB Stats API — National League standings, 2026 regular season",
        "url": "https://statsapi.mlb.com/api/v1/standings?leagueId=104&season=2026"
               "&fields=records,teamRecords,team,id,name,wins,losses,runsScored,runsAllowed,gamesPlayed",
        "publisher": "Major League Baseball",
        "official": True,
        "kind": "league API (JSON)",
        "used_for": "Milwaukee Brewers 103-59 with 832 runs scored and 618 allowed.",
        "read_at": READ_AT,
    },
    {
        "id": "mlb-standings-al",
        "name": "MLB Stats API — American League standings, 2026 regular season",
        "url": "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026"
               "&fields=records,teamRecords,team,id,name,leagueRecord,wins,losses,pct,runsScored,"
               "runsAllowed,gamesPlayed,division,standingsType",
        "publisher": "Major League Baseball",
        "official": True,
        "kind": "league API (JSON)",
        "used_for": "Tampa Bay Rays 98-64 with 736 runs scored and 650 allowed.",
        "read_at": READ_AT,
    },
    {
        "id": "mlb-schedule",
        "name": "MLB Stats API — 2026 World Series schedule",
        "url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-22&endDate=2026-10-29"
               "&fields=dates,date,games,gamePk,gameDate,status,detailedState,teams,home,away,team,id,"
               "name,score,venue,name,dayNight",
        "publisher": "Major League Baseball",
        "official": True,
        "kind": "league API (JSON)",
        "used_for": "Game one to game five dates, exact UTC start times and venues.",
        "read_at": READ_AT,
    },
    {
        "id": "mlb-postseason-results",
        "name": "MLB Stats API — Rays and Brewers results, 1–23 October 2026",
        "url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&teamId=139,158&startDate=2026-10-01"
               "&endDate=2026-10-23&fields=dates,date,games,gamePk,gameDate,teams,home,away,team,id,name,"
               "score,isWinner,status,detailedState",
        "publisher": "Major League Baseball",
        "official": True,
        "kind": "league API (JSON)",
        "used_for": "Game-by-game scorelines used for the verified recent-form claims in predictions.",
        "read_at": READ_AT,
    },
    {
        "id": "urc-match-centre",
        "name": "United Rugby Championship official Match Centre — Round 4",
        "url": "https://www.unitedrugby.com/match-centre",
        "publisher": "United Rugby Championship",
        "official": True,
        "kind": "league website",
        "used_for": "The eight Round 4 fixtures, dates, stated local kick-off times and venues.",
        "read_at": READ_AT,
    },
    {
        "id": "urc-table",
        "name": "United Rugby Championship official league table 2026/27",
        "url": "https://stats.unitedrugby.com/match-centre/table/2026-27",
        "publisher": "United Rugby Championship",
        "official": True,
        "kind": "league website",
        "used_for": "Played, won, drawn, lost, points for and points against for all 16 clubs after "
                    "three rounds.",
        "read_at": READ_AT,
    },
    {
        "id": "nrl-draw",
        "name": "NRL official draw — Rugby League World Cup 2026, Round 2",
        "url": "https://www.nrl.com/draw/?competition=131&round=2&season=2026",
        "publisher": "National Rugby League",
        "official": True,
        "kind": "league website",
        "used_for": "The five Round 2 fixtures, dates, venues and the source's own kick-off text.",
        "read_at": READ_AT,
    },
    {
        "id": "wst-ni-open",
        "name": "World Snooker Tour — BetVictor Northern Ireland Open 2026 match schedule",
        "url": "https://www.wst.tv/matches/b4533c9e-8d2c-4ecc-8dfd-c6b284705578",
        "publisher": "World Snooker Tour",
        "official": True,
        "kind": "governing-body website",
        "used_for": "The eight scheduled Round 3 matches on 22 October 2026 and their session times.",
        "read_at": READ_AT,
    },
    {
        "id": "f1-calendar",
        "name": "Formula 1 official 2026 race calendar",
        "url": "https://www.formula1.com/en/racing/2026",
        "publisher": "Formula 1",
        "official": True,
        "kind": "championship website",
        "used_for": "Round 18, United States Grand Prix, 23–25 October 2026.",
        "read_at": READ_AT,
    },
    {
        "id": "f1-usgp",
        "name": "Formula 1 official United States Grand Prix 2026 event page",
        "url": "https://www.formula1.com/en/racing/2026/united-states",
        "publisher": "Formula 1",
        "official": True,
        "kind": "championship website",
        "used_for": "Session schedule (practice, qualifying, race) and circuit facts.",
        "read_at": READ_AT,
    },
    {
        "id": "gaa-fixtures",
        "name": "GAA official fixtures and results",
        "url": "https://www.gaa.ie/fixtures-results",
        "publisher": "Gaelic Athletic Association",
        "official": True,
        "kind": "governing-body website",
        "used_for": "Negative check: the only October fixture listed on the read date is the "
                    "Shinty-Hurling International, i.e. an excluded sport. No Gaelic football "
                    "fixture was found in scope.",
        "read_at": READ_AT,
    },
    {
        "id": "atp-scores",
        "name": "ATP Tour official current scores",
        "url": "https://www.atptour.com/en/scores/current",
        "publisher": "ATP Tour",
        "official": True,
        "kind": "tour website",
        "used_for": "Negative check: the page renders live in-play matches only. No pre-match "
                    "pairing for a later date could be verified, so no tennis row is priced.",
        "read_at": READ_AT,
    },
    {
        "id": "aflw-fixture",
        "name": "AFLW official fixture page",
        "url": "https://www.afl.com.au/aflw/fixture",
        "publisher": "Australian Football League",
        "official": True,
        "kind": "league website",
        "used_for": "Negative check: the fixture grid is client-rendered and returned no fixture "
                    "rows to the reader. No AFLW row is published.",
        "read_at": READ_AT,
    },
    {
        "id": "aflw-ladder",
        "name": "AFLW official ladder",
        "url": "https://www.afl.com.au/aflw/ladder",
        "publisher": "Australian Football League",
        "official": True,
        "kind": "league website",
        "used_for": "Negative check: the ladder body is client-rendered ('Loading…'), so no club "
                    "record could be read. Nothing inferred.",
        "read_at": READ_AT,
    },
    {
        "id": "euroleague-games",
        "name": "EuroLeague official Game Center",
        "url": "https://www.euroleaguebasketball.net/en/euroleague/game-center/",
        "publisher": "EuroLeague Basketball",
        "official": True,
        "kind": "league website",
        "used_for": "Negative check: the games grid is client-rendered; the reader received club "
                    "logos and navigation only. No basketball fixture is published.",
        "read_at": READ_AT,
    },
    {
        "id": "gbgb-home",
        "name": "Greyhound Board of Great Britain official site",
        "url": "https://www.gbgb.org.uk/",
        "publisher": "Greyhound Board of Great Britain",
        "official": True,
        "kind": "governing-body website",
        "used_for": "Negative check: the homepage exposes a results search, not an upcoming race "
                    "card. No greyhound fixture is published.",
        "read_at": READ_AT,
    },
]

# ---------------------------------------------------------------------------
# NHL — 32 clubs. Fields: abbrev, full name, GP, W, L (regulation), OTL, GF, GA
# Transcribed from nhl-team-summary (chunks 0–2). Ordered by points, as returned.
# ---------------------------------------------------------------------------
NHL_TEAMS = [
    ("CAR", "Carolina Hurricanes", 11, 8, 2, 1, 42, 27),
    ("VGK", "Vegas Golden Knights", 11, 8, 3, 0, 43, 30),
    ("EDM", "Edmonton Oilers", 9, 7, 1, 1, 41, 27),
    ("NYR", "New York Rangers", 11, 7, 3, 1, 33, 24),
    ("BOS", "Boston Bruins", 10, 7, 2, 1, 36, 22),
    ("TBL", "Tampa Bay Lightning", 9, 7, 2, 0, 31, 23),
    ("MIN", "Minnesota Wild", 10, 6, 2, 2, 31, 25),
    ("UTA", "Utah Mammoth", 10, 7, 3, 0, 38, 31),
    ("OTT", "Ottawa Senators", 10, 7, 3, 0, 27, 24),
    ("SEA", "Seattle Kraken", 10, 6, 3, 1, 37, 34),
    ("FLA", "Florida Panthers", 10, 5, 3, 2, 31, 30),
    ("TOR", "Toronto Maple Leafs", 11, 5, 4, 2, 38, 34),
    ("COL", "Colorado Avalanche", 10, 5, 4, 1, 41, 30),
    ("SJS", "San Jose Sharks", 10, 5, 4, 1, 26, 34),
    ("NYI", "New York Islanders", 9, 5, 3, 1, 27, 19),
    ("DAL", "Dallas Stars", 9, 5, 3, 1, None, None),          # goals not visible in the read
    ("MTL", "Montréal Canadiens", 9, 4, 3, 2, 28, 34),
    ("WPG", "Winnipeg Jets", 9, 4, 3, 2, 24, 26),
    ("BUF", "Buffalo Sabres", 10, 4, 4, 2, 28, 36),
    ("NJD", "New Jersey Devils", 9, 5, 4, 0, 29, 30),
    ("WSH", "Washington Capitals", 9, 5, 4, 0, 30, 29),
    ("NSH", "Nashville Predators", 8, 3, 2, 3, 23, 22),
    ("DET", "Detroit Red Wings", 9, 3, 3, 3, 22, 26),
    ("STL", "St. Louis Blues", 9, 4, 4, 1, 29, 29),
    ("PHI", "Philadelphia Flyers", 12, 3, 6, 3, 20, 36),
    ("ANA", "Anaheim Ducks", 9, 4, 5, 0, 26, 29),
    ("PIT", "Pittsburgh Penguins", 10, 3, 6, 1, 32, 37),
    ("CBJ", "Columbus Blue Jackets", 8, 3, 5, 0, 19, 29),
    ("CHI", "Chicago Blackhawks", 9, 3, 6, 0, 21, 36),
    ("VAN", "Vancouver Canucks", 11, 2, 8, 1, 33, 51),
    ("CGY", "Calgary Flames", 8, 2, 6, 0, 17, 37),
    ("LAK", "Los Angeles Kings", 7, 1, 4, 2, 17, 27),
]

# NHL club id -> abbreviation. Taken from the teamFullName/teamId pairs in the same payload.
NHL_IDS = {
    1: "NJD", 2: "NYI", 3: "NYR", 4: "PHI", 5: "PIT", 6: "BOS", 7: "BUF", 8: "MTL",
    9: "OTT", 10: "TOR", 12: "CAR", 13: "FLA", 14: "TBL", 15: "WSH", 16: "CHI",
    17: "DET", 18: "NSH", 19: "STL", 20: "CGY", 21: "COL", 22: "EDM", 23: "VAN",
    24: "ANA", 25: "DAL", 26: "LAK", 28: "SJS", 29: "CBJ", 30: "MIN", 52: "WPG",
    54: "VGK", 55: "SEA", 68: "UTA",
}

# NHL fixtures: (game_id, game_date, eastern_start_hhmm, home_id, away_id, venue_verified)
# Venue text is only included where the venue was visible in the read; otherwise None.
NHL_GAMES = [
    (2026020154, "2026-10-22", "19:00", 6, 18, "TD Garden"),
    (2026020155, "2026-10-22", "19:00", 10, 3, "Scotiabank Arena"),
    (2026020156, "2026-10-22", "19:00", 9, 28, "Canadian Tire Centre"),
    (2026020157, "2026-10-22", "19:00", 1, 24, "Prudential Center"),
    (2026020158, "2026-10-22", "19:00", 5, 13, "PPG Paints Arena"),
    (2026020159, "2026-10-22", "19:30", 2, 26, None),
    (2026020160, "2026-10-22", "20:00", 19, 54, None),
    (2026020161, "2026-10-22", "20:00", 25, 52, None),
    (2026020162, "2026-10-22", "21:00", 20, 30, None),
    (2026020163, "2026-10-22", "21:00", 22, 12, None),
    (2026020164, "2026-10-22", "22:00", 55, 68, None),
    (2026020165, "2026-10-22", "22:00", 23, 17, None),
    (2026020166, "2026-10-23", "20:00", 16, 8, None),
    (2026020167, "2026-10-23", "21:00", 21, 14, None),
    (2026020168, "2026-10-24", "13:00", 4, 24, None),
    (2026020169, "2026-10-24", "15:30", 1, 26, None),
    (2026020170, "2026-10-24", "19:00", 6, 28, None),
    (2026020171, "2026-10-24", "19:00", 9, 3, None),
    (2026020172, "2026-10-24", "19:00", 5, 18, None),
    (2026020173, "2026-10-24", "19:00", 15, 7, None),
    (2026020174, "2026-10-24", "19:00", 29, 54, None),
    (2026020175, "2026-10-24", "19:00", 19, 12, None),
    (2026020176, "2026-10-24", "19:00", 22, 10, None),
    (2026020177, "2026-10-24", "21:00", 68, 14, None),
    (2026020178, "2026-10-24", "22:00", 20, 17, None),
    (2026020179, "2026-10-24", "22:00", 55, 30, None),
    (2026020180, "2026-10-25", "15:00", 16, 13, None),
    (2026020181, "2026-10-25", "18:00", 25, 2, None),
    (2026020182, "2026-10-25", "19:00", 52, 8, None),
    (2026020183, "2026-10-25", "20:00", 18, 21, None),
    (2026020184, "2026-10-25", "22:00", 23, 30, None),
    (2026020185, "2026-10-26", "19:00", 3, 26, None),
    (2026020186, "2026-10-26", "20:30", 20, 10, None),
    (2026020187, "2026-10-26", "21:30", 22, 17, None),
    (2026020188, "2026-10-27", "19:00", 4, 29, None),
    (2026020189, "2026-10-27", "20:00", 12, 6, None),
    (2026020190, "2026-10-27", "20:00", 16, 26, None),
    (2026020191, "2026-10-27", "20:00", 19, 8, None),
    (2026020192, "2026-10-27", "20:00", 18, 2, None),
    (2026020193, "2026-10-27", "20:00", 25, 1, None),
    (2026020194, "2026-10-27", "20:00", 52, 13, None),
    (2026020195, "2026-10-27", "21:00", 68, 30, None),
    (2026020196, "2026-10-27", "22:00", 54, 9, None),
    (2026020197, "2026-10-27", "22:00", 24, 23, None),
    (2026020198, "2026-10-27", "22:30", 28, 7, None),
    (2026020199, "2026-10-28", "19:30", 15, 4, None),
    (2026020200, "2026-10-28", "20:30", 22, 20, None),
    (2026020201, "2026-10-28", "21:00", 21, 1, None),
    (2026020202, "2026-10-28", "22:00", 55, 10, None),
    (2026020203, "2026-10-29", "19:30", 17, 16, None),
    (2026020204, "2026-10-29", "19:00", 14, 52, None),
    (2026020205, "2026-10-29", "19:00", 5, 68, None),
    (2026020206, "2026-10-29", "19:00", 12, 29, None),
    (2026020207, "2026-10-29", "20:00", 19, 6, None),
    (2026020208, "2026-10-29", "20:00", 18, 15, None),
    (2026020209, "2026-10-29", "20:00", 25, 8, None),
    (2026020210, "2026-10-29", "20:00", 30, 2, None),
    (2026020211, "2026-10-29", "22:00", 24, 7, None),
    (2026020212, "2026-10-29", "22:00", 26, 9, None),
    (2026020213, "2026-10-29", "22:00", 28, 23, None),
]

# Last-ten and streak fields transcribed from nhl-standings-web where present.
# Format: abbrev -> (l10_wins, l10_losses, l10_ot_losses, streak_code, streak_count)
NHL_L10 = {
    "CAR": (8, 2, 0, "W", 1),
    "VGK": (7, 3, 0, "L", 1),
    "EDM": (7, 1, 1, "W", 2),
    "BOS": (7, 2, 1, "OT", 1),
    "TBL": (7, 2, 0, "W", 3),
    "UTA": (7, 3, 0, "W", 1),
    "MIN": (6, 2, 2, "OT", 1),
    "OTT": (7, 3, 0, "W", 1),
    "SEA": (6, 3, 1, "W", 1),
    "FLA": (5, 3, 2, "L", 1),
    "TOR": (5, 4, 2, "W", 2),
    "NYI": (5, 3, 1, "W", 2),
    "NYR": (7, 3, 1, "W", 1),
}

# ---------------------------------------------------------------------------
# MLB — 2026 World Series, Tampa Bay Rays v Milwaukee Brewers
# ---------------------------------------------------------------------------
MLB_TEAMS = {
    "TB": {"name": "Tampa Bay Rays", "wins": 98, "losses": 64, "rs": 736, "ra": 650,
           "source": "mlb-standings-al"},
    "MIL": {"name": "Milwaukee Brewers", "wins": 103, "losses": 59, "rs": 832, "ra": 618,
            "source": "mlb-standings"},
}

# (game_pk, utc_start, venue)
MLB_GAMES = [
    (849805, "2026-10-24T00:00:00Z", "American Family Field"),
    (849802, "2026-10-25T00:00:00Z", "American Family Field"),
    (849804, "2026-10-27T00:00:00Z", "Tropicana Field"),
    (849803, "2026-10-28T00:00:00Z", "Tropicana Field"),
    (849799, "2026-10-29T00:00:00Z", "Tropicana Field"),
]

# Verified recent results, newest last: (date, opponent, scored, conceded, home)
MLB_FORM = {
    "TB": [
        ("2026-10-03", "New York Yankees", 1, 0, True),
        ("2026-10-05", "New York Yankees", 5, 2, True),
        ("2026-10-07", "New York Yankees", 4, 3, False),
        ("2026-10-12", "Cleveland Guardians", 3, 7, True),
        ("2026-10-13", "Cleveland Guardians", 3, 1, True),
        ("2026-10-15", "Cleveland Guardians", 2, 3, False),
        ("2026-10-17", "Cleveland Guardians", 7, 3, False),
        ("2026-10-18", "Cleveland Guardians", 3, 1, False),
        ("2026-10-19", "Cleveland Guardians", 7, 3, True),
    ],
    "MIL": [
        ("2026-10-03", "San Diego Padres", 3, 2, True),
        ("2026-10-04", "San Diego Padres", 4, 3, True),
        ("2026-10-06", "San Diego Padres", 3, 4, False),
        ("2026-10-07", "San Diego Padres", 3, 1, False),
        ("2026-10-11", "Los Angeles Dodgers", 2, 1, True),
        ("2026-10-12", "Los Angeles Dodgers", 7, 4, True),
        ("2026-10-14", "Los Angeles Dodgers", 6, 2, False),
        ("2026-10-15", "Los Angeles Dodgers", 6, 4, False),
    ],
}

# ---------------------------------------------------------------------------
# United Rugby Championship — Round 4 and the table after three rounds
# (abbrev, name, P, W, D, L, PF, PA, form)
# ---------------------------------------------------------------------------
URC_TABLE = [
    ("EDI", "Edinburgh", 3, 3, 0, 0, 80, 54, "WWW"),
    ("GLA", "Glasgow Warriors", 3, 2, 1, 0, 95, 72, "WDW"),
    ("BUL", "Vodacom Bulls", 3, 2, 0, 1, 126, 54, "WLW"),
    ("STO", "DHL Stormers", 3, 2, 0, 1, 81, 54, "WLW"),
    ("SHA", "Hollywoodbets Sharks", 3, 2, 0, 1, 89, 83, "WWL"),
    ("CAR", "Cardiff Rugby", 3, 2, 0, 1, 66, 71, "WWL"),
    ("LIO", "10bet Lions", 3, 2, 0, 1, 77, 102, "WWL"),
    ("DRA", "Dragons RFC", 3, 1, 1, 1, 88, 83, "DWL"),
    ("MUN", "Munster", 3, 1, 1, 1, 72, 74, "LWD"),
    ("LEI", "Leinster", 3, 1, 0, 2, 75, 58, "LLW"),
    ("ULS", "Ulster", 3, 0, 2, 1, 88, 93, "LDD"),
    ("SCA", "Scarlets", 3, 1, 0, 2, 68, 85, "LLW"),
    ("OSP", "Ospreys", 3, 1, 0, 2, 81, 107, "LLW"),
    ("CON", "Connacht", 3, 1, 0, 2, 56, 84, "LWL"),
    ("BEN", "Benetton", 3, 0, 1, 2, 64, 68, "DLL"),
    ("ZEB", "Zebre Parma", 3, 0, 0, 3, 52, 116, "LLL"),
]

# (id, date, stated local kick-off, home, away, venue)
URC_GAMES = [
    ("urc-r4-01", "2026-10-23", "14:45", "CAR", "SHA", "Cardiff Arms Park"),
    ("urc-r4-02", "2026-10-23", "14:45", "CON", "ZEB", "Dexcom Stadium"),
    ("urc-r4-03", "2026-10-23", "14:45", "EDI", "LIO", "Hive Stadium"),
    ("urc-r4-04", "2026-10-24", "07:45", "BUL", "ULS", "Loftus Versfeld"),
    ("urc-r4-05", "2026-10-24", "10:00", "STO", "SCA", "DHL Stadium"),
    ("urc-r4-06", "2026-10-24", "10:00", "BEN", "GLA", "Stadio Monigo"),
    ("urc-r4-07", "2026-10-24", "13:00", "LEI", "MUN", "Aviva Stadium"),
    ("urc-r4-08", "2026-10-24", "14:00", "OSP", "DRA", "St Helen's"),
]

# ---------------------------------------------------------------------------
# Rugby League World Cup 2026 — Round 2 (fixtures only; no club-style table was
# captured, so these rows are published unpriced and flagged).
# ---------------------------------------------------------------------------
RLWC_GAMES = [
    ("rlwc-r2-01", "2026-10-23", "05:05", "Tonga", "Lebanon",
     "CommBank Stadium, Sydney", "https://www.nrl.com/draw/?competition=131&round=2&season=2026"),
    ("rlwc-r2-02", "2026-10-24", "00:25", "Papua New Guinea", "Samoa",
     "Santos National Football Stadium, Port Moresby",
     "https://www.nrl.com/draw/?competition=131&round=2&season=2026"),
    ("rlwc-r2-03", "2026-10-24", "02:35", "England", "France",
     "HBF Park, Perth", "https://www.nrl.com/draw/?competition=131&round=2&season=2026"),
    ("rlwc-r2-04", "2026-10-25", "01:05", "New Zealand", "Cook Islands",
     "One NZ Stadium, Christchurch", "https://www.nrl.com/draw/?competition=131&round=2&season=2026"),
    ("rlwc-r2-05", "2026-10-25", "05:05", "Australia", "Fiji",
     "Suncorp Stadium, Brisbane", "https://www.nrl.com/draw/?competition=131&round=2&season=2026"),
]

# ---------------------------------------------------------------------------
# Snooker — Northern Ireland Open, scheduled Round 3 matches (22 Oct 2026)
# ---------------------------------------------------------------------------
SNOOKER_GAMES = [
    ("snooker-nio-r3-51", "2026-10-22", "08:00", "Matthew Selt", "Sam Craigie"),
    ("snooker-nio-r3-50", "2026-10-22", "08:00", "Kyren Wilson", "Pang Junxu"),
    ("snooker-nio-r3-49", "2026-10-22", "09:00", "Anthony McGill", "Mateusz Baranowski"),
    ("snooker-nio-r3-52", "2026-10-22", "09:00", "Elliot Slessor", "Ricky Walden"),
    ("snooker-nio-r3-54", "2026-10-22", "14:00", "Mark Williams", "Martin O'Donnell"),
    ("snooker-nio-r3-53", "2026-10-22", "14:00", "David Gilbert", "Ka Wai Cheung"),
    ("snooker-nio-r3-56", "2026-10-22", "15:00", "Jordan Brown", "Scott Donaldson"),
    ("snooker-nio-r3-55", "2026-10-22", "15:00", "Jak Jones", "Daniel Wells"),
]

# ---------------------------------------------------------------------------
# Formula 1 — United States Grand Prix weekend sessions (track time, as published)
# ---------------------------------------------------------------------------
F1_SESSIONS = [
    ("f1-usgp-p1", "Practice 1", "2026-10-23", "13:30–14:30"),
    ("f1-usgp-p2", "Practice 2", "2026-10-23", "17:00–18:00"),
    ("f1-usgp-p3", "Practice 3", "2026-10-24", "13:30–14:30"),
    ("f1-usgp-q", "Qualifying", "2026-10-24", "17:00–18:00"),
    ("f1-usgp-race", "Race", "2026-10-25", "16:00"),
]

# ---------------------------------------------------------------------------
# Sports that are in scope for the brief but for which this session could not
# verify a fixture from an official source. Each entry records the official URL
# that was read and the specific reason no row is published.
# ---------------------------------------------------------------------------
UNVERIFIED_SPORTS = [
    ("basketball", "Basketball",
     "https://www.euroleaguebasketball.net/en/euroleague/game-center/",
     "EuroLeague Game Center is client-rendered; the read returned club logos and navigation, "
     "not a fixture list. NBA's public scoreboard endpoint returned HTTP 500 on the same attempt. "
     "No fixture is published because none could be read from an official page."),
    ("tennis", "Tennis",
     "https://www.atptour.com/en/scores/current",
     "The ATP current-scores page exposes in-play matches only. A later-round pairing could not be "
     "verified, and pricing a match already in progress is not a pre-match selection. No row."),
    ("darts", "Darts",
     "https://www.pdc.tv/tournaments",
     "The PDC tournaments route returned a cookie-consent interstitial as its entire readable body. "
     "No fixture, round or start time could be read, so no darts row is published."),
    ("golf", "Golf",
     "https://www.pgatour.com/schedule",
     "The PGA Tour schedule grid is client-rendered; no tournament field or tee time could be read "
     "as a fixture. No row."),
    ("cricket", "Cricket",
     "https://www.cricket.com.au/matches",
     "The Cricket Australia matches page returned series and team filters but the fixture cards sit "
     "outside the readable body. A series name is not a dated fixture, so no row is published."),
    ("handball", "Handball",
     "https://ehfcl.eurohandball.com/men/2026-27/",
     "The EHF Champions League route is client-rendered; no round, pairing or throw-off time could "
     "be read. No row."),
    ("volleyball", "Volleyball",
     "https://www.tauronliga.pl/games.html",
     "The Polish league games page returned an older round's tie-break detail with no upcoming date "
     "in the readable body. No future fixture could be verified. No row."),
    ("esports", "eSports",
     "https://lolesports.com/schedule",
     "The official LoL Esports schedule is client-rendered. The public schedule endpoint requires a "
     "request header this reader cannot set. No row."),
    ("greyhounds", "Greyhounds",
     "https://www.gbgb.org.uk/",
     "GBGB publishes a results search and open-race notices, not an upcoming race card with runners. "
     "No runner-level fixture could be read. No row."),
    ("aussie-rules", "Australian Rules",
     "https://www.afl.com.au/aflw/fixture",
     "The AFLW fixture grid and ladder both returned client-rendered placeholders ('Loading…'). The "
     "former /aflw/fixtures route is a 404. No AFLW fixture or record could be verified. No row."),
    ("gaelic-football", "Gaelic Football",
     "https://www.gaa.ie/fixtures-results",
     "The only October fixture listed on the read date is the Shinty-Hurling International, which is "
     "an excluded sport under the brief. No Gaelic football fixture was in scope. No row."),
]
