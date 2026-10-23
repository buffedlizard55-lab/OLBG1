#!/usr/bin/env python3
"""T5821 (session e58210b8-olbg1) verified observation set.

Every value in this module was read from an official publisher on 2026-10-23 by the
session's retrieval tool.  Nothing here is inferred from memory: where a value was
not read it is simply absent, and the desk publishes it blank with a flag.
"""
from __future__ import annotations

SESSION = "e58210b8-olbg1"
TASK = "T5821"
HARVEST_UTC = "2026-10-23T19:35:00Z"
WINDOW_MIN_AMERICAN = -250
WINDOW_MAX_AMERICAN = 10000
HIGH_PROBABILITY_FLOOR = 250 / 350  # -250 fair price == 0.714285... implied probability

OLBG_ROUTES = {
    "tennis": ("Tennis", 3),
    "basketball": ("Basketball", 4),
    "golf": ("Golf", 5),
    "cricket": ("Cricket", 7),
    "snooker": ("Snooker", 8),
    "rugby_union": ("Rugby_Union", 9),
    "rugby_league": ("Rugby_League", 10),
    "baseball": ("Baseball", 12),
    "ice_hockey": ("Ice_Hockey", 13),
    "motor_racing": ("Motor_Racing", 14),
    "darts": ("Darts", 15),
    "handball": ("Handball", 20),
    "volleyball": ("Volleyball", 21),
    "gaelic_sports": ("Gaelic_Football", 25),
    "greyhounds": ("Greyhounds", 28),
}

SPORT_LABEL = {
    "ice_hockey": "Ice Hockey", "baseball": "Baseball", "tennis": "Tennis",
    "snooker": "Snooker", "golf": "Golf", "cricket": "Cricket",
    "rugby_union": "Rugby Union", "rugby_league": "Rugby League",
    "motor_racing": "Motor Racing", "darts": "Darts", "handball": "Handball",
    "volleyball": "Volleyball", "gaelic_sports": "Gaelic Sports",
    "greyhounds": "Greyhounds", "basketball": "Basketball",
}

SOURCES = [
    {"id": "nhl-schedule-1023", "name": "NHL official schedule feed, 2026-10-23",
     "url": "https://api-web.nhle.com/v1/schedule/2026-10-23", "role": "official",
     "read_utc": "2026-10-23T19:35:00Z",
     "note": "Two games listed for 2026-10-23 with gameState FUT, venue and startTimeUTC."},
    {"id": "nhl-schedule-1024", "name": "NHL official schedule feed, 2026-10-24",
     "url": "https://api-web.nhle.com/v1/schedule/2026-10-24", "role": "official",
     "read_utc": "2026-10-23T19:35:00Z",
     "note": "numberOfGames 12 for 2026-10-24 and 5 for 2026-10-25; all 12 Saturday games read "
             "individually plus the first Sunday game (Florida at Chicago)."},
    {"id": "nhl-standings", "name": "NHL official standings, 2026-10-23",
     "url": "https://api-web.nhle.com/v1/standings/2026-10-23", "role": "official",
     "read_utc": "2026-10-23T19:35:00Z",
     "note": "standingsDateTimeUtc 2026-10-23T19:29:30Z. All 32 clubs read: games played, wins, "
             "losses, overtime losses, points, goals for/against, last-10 record, home/road splits "
             "and streak code."},
    {"id": "mlb-schedule", "name": "MLB Stats API schedule, 2026-10-23 to 2026-10-28",
     "url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-23&endDate=2026-10-28",
     "role": "official", "read_utc": "2026-10-23T19:33:00Z",
     "note": "totalGames 5 in the window, all 2026 World Series games between the Tampa Bay Rays and "
             "the Milwaukee Brewers; each carries ifNecessary N and detailedState Scheduled."},
    {"id": "mlb-nl-standings", "name": "MLB Stats API National League standings, 2026",
     "url": "https://statsapi.mlb.com/api/v1/standings?leagueId=104&season=2026",
     "role": "official", "read_utc": "2026-10-23T19:36:00Z",
     "note": "Milwaukee Brewers 103-59, .636, 832 runs scored, 618 runs allowed, first in the "
             "National League Central."},
    {"id": "olbg-sitemap", "name": "OLBG public betting-tips sitemap",
     "url": "https://www.olbg.com/sitemap-betting-tips.xml", "role": "discovery",
     "read_utc": "2026-10-23T19:31:00Z",
     "note": "lastmod 2026-10-23 on every route. Confirms the sport-hub grammar "
             "/betting-tips/{Sport_Slug}/{sport_id} for all 15 sports in the brief."},
    {"id": "olbg-robots", "name": "OLBG robots policy", "url": "https://www.olbg.com/robots.txt",
     "role": "discovery", "read_utc": "2026-10-23T19:30:00Z",
     "note": "/api/ and /storage/app/json_data/ are disallowed; the desk did not request them."},
    {"id": "olbg-hub-tennis", "name": "OLBG tennis hub", "url": "https://www.olbg.com/betting-tips/Tennis/3",
     "role": "discovery", "read_utc": "2026-10-23T19:29:00Z",
     "note": "Server-rendered page returned the literal empty state 'No tips found.' with no "
             "event rows in the delivered HTML."},
    {"id": "olbg-hub-ice-hockey", "name": "OLBG ice hockey hub",
     "url": "https://www.olbg.com/betting-tips/Ice_Hockey/13", "role": "discovery",
     "read_utc": "2026-10-23T19:29:00Z",
     "note": "Same empty state 'No tips found.'; the NHL competition sub-route "
             "/betting-tips/Ice_Hockey/NHL/13 behaved identically."},
    {"id": "atp-scores", "name": "ATP Tour official scores page",
     "url": "https://www.atptour.com/en/scores/current", "role": "official",
     "read_utc": "2026-10-23T19:34:00Z",
     "note": "Quarter-final results for three ATP Tour tournaments on 2026-10-23."},
    {"id": "wst-tournaments", "name": "World Snooker Tour tournament list",
     "url": "https://www.wst.tv/tournaments/", "role": "official",
     "read_utc": "2026-10-23T19:36:00Z",
     "note": "BetVictor Northern Ireland Open 2026, Sun 18 Oct - Sun 25 Oct 2026, Belfast."},
    {"id": "wst-ni-open-matches", "name": "World Snooker Tour Northern Ireland Open matches",
     "url": "https://www.wst.tv/matches/b4533c9e-8d2c-4ecc-8dfd-c6b284705578", "role": "official",
     "read_utc": "2026-10-23T19:37:00Z",
     "note": "Round 1 results with frame scores; publisher prints clock times without a timezone label."},
]

# abbr: (games played, wins, losses, ot losses, points, goals for, goals against,
#        last-10 W-L-OTL, streak, home record, road record, conference, division)
NHL_TEAMS = {
    "CAR": (12, 8, 2, 2, 18, 47, 33, "8-1-1", "OT1", "4-1-1", "6-1-1", "Eastern", "Metropolitan"),
    "EDM": (10, 8, 1, 1, 17, 47, 32, "8-1-1", "W3", "3-1-1", "5-0-0", "Western", "Pacific"),
    "BOS": (11, 8, 2, 1, 17, 42, 22, "7-2-1", "W1", "4-1-0", "4-1-1", "Eastern", "Atlantic"),
    "VGK": (12, 8, 4, 0, 16, 46, 36, "7-3-0", "L2", "5-2-0", "3-2-0", "Western", "Pacific"),
    "SEA": (11, 7, 3, 1, 15, 44, 37, "6-3-1", "W2", "3-2-1", "4-2-1", "Western", "Pacific"),
    "NYR": (12, 7, 4, 1, 15, 37, 29, "6-3-1", "L1", "6-0-0", "1-4-1", "Eastern", "Metropolitan"),
    "TBL": (9, 7, 2, 0, 14, 31, 23, "7-2-0", "W3", "5-0-0", "2-2-0", "Eastern", "Atlantic"),
    "UTA": (11, 7, 4, 0, 14, 41, 36, "6-4-0", "L1", "3-1-1", "4-3-0", "Western", "Central"),
    "MIN": (11, 6, 3, 2, 14, 32, 27, "5-3-2", "L1", "4-0-0", "2-3-2", "Western", "Central"),
    "OTT": (11, 7, 4, 0, 14, 31, 30, "6-4-0", "L1", "4-2-0", "3-2-0", "Eastern", "Atlantic"),
    "TOR": (12, 6, 4, 2, 14, 43, 39, "5-3-2", "W3", "4-1-1", "2-1-1", "Eastern", "Atlantic"),
    "DAL": (10, 6, 3, 1, 13, 26, 17, "6-3-1", "W4", "3-2-1", "3-1-0", "Western", "Central"),
    "SJS": (11, 6, 4, 1, 13, 33, 37, "5-4-1", "W2", "2-2-1", "4-2-1", "Western", "Pacific"),
    "NYI": (10, 5, 3, 2, 12, 29, 23, "5-3-2", "OT1", "4-1-1", "1-2-1", "Eastern", "Metropolitan"),
    "NJD": (10, 6, 4, 0, 12, 33, 31, "6-4-0", "W2", "5-2-0", "1-2-0", "Eastern", "Metropolitan"),
    "FLA": (11, 5, 4, 2, 12, 31, 34, "4-4-2", "L2", "2-1-0", "3-3-2", "Eastern", "Atlantic"),
    "COL": (10, 5, 4, 1, 11, 41, 31, "5-4-1", "L2", "3-1-1", "2-3-0", "Western", "Central"),
    "STL": (10, 5, 4, 1, 11, 35, 31, "5-4-1", "W2", "3-0-1", "2-4-0", "Western", "Central"),
    "WPG": (10, 4, 3, 3, 11, 26, 29, "4-3-3", "OT1", "2-2-1", "2-1-2", "Western", "Central"),
    "DET": (10, 4, 3, 3, 11, 28, 30, "4-3-3", "W1", "3-3-1", "1-0-2", "Eastern", "Atlantic"),
    "WSH": (9, 5, 4, 0, 10, 30, 29, "5-4-0", "L1", "4-2-0", "1-2-0", "Eastern", "Metropolitan"),
    "MTL": (9, 4, 3, 2, 10, 30, 34, "4-3-2", "OT1", "3-2-1", "1-1-1", "Eastern", "Atlantic"),
    "BUF": (10, 4, 4, 2, 10, 28, 37, "4-4-2", "L1", "3-3-0", "1-1-2", "Eastern", "Atlantic"),
    "NSH": (9, 3, 3, 3, 9, 23, 30, "3-3-3", "L1", "2-2-1", "1-1-2", "Western", "Central"),
    "PIT": (11, 4, 6, 1, 9, 37, 38, "3-6-1", "W1", "3-1-0", "1-5-1", "Eastern", "Metropolitan"),
    "PHI": (12, 3, 6, 3, 9, 20, 37, "3-5-2", "W3", "2-2-2", "1-4-1", "Eastern", "Metropolitan"),
    "ANA": (10, 4, 6, 0, 8, 27, 33, "4-6-0", "L5", "1-3-0", "3-3-0", "Western", "Pacific"),
    "CBJ": (8, 3, 5, 0, 6, 20, 29, "3-5-0", "L2", "3-3-0", "0-2-0", "Eastern", "Metropolitan"),
    "LAK": (8, 2, 4, 2, 6, 20, 29, "2-4-2", "W2", "0-3-0", "2-1-2", "Western", "Pacific"),
    "CGY": (9, 3, 6, 0, 6, 19, 38, "3-6-0", "W2", "2-3-0", "1-3-0", "Western", "Pacific"),
    "CHI": (9, 3, 6, 0, 6, 21, 36, "3-6-0", "L1", "3-2-0", "0-4-0", "Western", "Central"),
    "VAN": (12, 2, 9, 1, 5, 35, 56, "1-8-1", "L3", "1-4-0", "1-5-1", "Western", "Pacific"),
}

NHL_TEAM_NAME = {
    "ANA": "Anaheim Ducks", "BOS": "Boston Bruins", "BUF": "Buffalo Sabres", "CGY": "Calgary Flames",
    "CAR": "Carolina Hurricanes", "CHI": "Chicago Blackhawks", "COL": "Colorado Avalanche",
    "CBJ": "Columbus Blue Jackets", "DAL": "Dallas Stars", "DET": "Detroit Red Wings",
    "EDM": "Edmonton Oilers", "FLA": "Florida Panthers", "LAK": "Los Angeles Kings",
    "MIN": "Minnesota Wild", "MTL": "Montreal Canadiens", "NSH": "Nashville Predators",
    "NJD": "New Jersey Devils", "NYI": "New York Islanders", "NYR": "New York Rangers",
    "OTT": "Ottawa Senators", "PHI": "Philadelphia Flyers", "PIT": "Pittsburgh Penguins",
    "SJS": "San Jose Sharks", "SEA": "Seattle Kraken", "STL": "St. Louis Blues",
    "TBL": "Tampa Bay Lightning", "TOR": "Toronto Maple Leafs", "UTA": "Utah Mammoth",
    "VAN": "Vancouver Canucks", "VGK": "Vegas Golden Knights", "WSH": "Washington Capitals",
    "WPG": "Winnipeg Jets",
}

# id, official date, start UTC, away abbr, home abbr, venue, official game id
NHL_FIXTURES = [
    ("nhl-2026020166", "2026-10-23", "2026-10-24T00:00:00Z", "MTL", "CHI", "United Center", 2026020166),
    ("nhl-2026020167", "2026-10-23", "2026-10-24T01:00:00Z", "TBL", "COL", "Ball Arena", 2026020167),
    ("nhl-2026020168", "2026-10-24", "2026-10-24T17:00:00Z", "ANA", "PHI", "Xfinity Mobile Arena", 2026020168),
    ("nhl-2026020169", "2026-10-24", "2026-10-24T19:30:00Z", "LAK", "NJD", "Prudential Center", 2026020169),
    ("nhl-2026020170", "2026-10-24", "2026-10-24T23:00:00Z", "SJS", "BOS", "TD Garden", 2026020170),
    ("nhl-2026020171", "2026-10-24", "2026-10-24T23:00:00Z", "NYR", "OTT", "Canadian Tire Centre", 2026020171),
    ("nhl-2026020172", "2026-10-24", "2026-10-24T23:00:00Z", "NSH", "PIT", "PPG Paints Arena", 2026020172),
    ("nhl-2026020173", "2026-10-24", "2026-10-24T23:00:00Z", "BUF", "WSH", "Capital One Arena", 2026020173),
    ("nhl-2026020174", "2026-10-24", "2026-10-24T23:00:00Z", "VGK", "CBJ", "Nationwide Arena", 2026020174),
    ("nhl-2026020175", "2026-10-24", "2026-10-24T23:00:00Z", "CAR", "STL", "Enterprise Center", 2026020175),
    ("nhl-2026020176", "2026-10-24", "2026-10-24T23:00:00Z", "TOR", "EDM", "Rogers Place", 2026020176),
    ("nhl-2026020177", "2026-10-24", "2026-10-25T01:00:00Z", "TBL", "UTA", "Delta Center", 2026020177),
    ("nhl-2026020178", "2026-10-24", "2026-10-25T02:00:00Z", "DET", "CGY", "Scotiabank Saddledome", 2026020178),
    ("nhl-2026020179", "2026-10-24", "2026-10-25T02:00:00Z", "MIN", "SEA", "Climate Pledge Arena", 2026020179),
    ("nhl-2026020180", "2026-10-25", "2026-10-25T19:00:00Z", "FLA", "CHI", "United Center", 2026020180),
]

MLB_FIXTURES = [
    ("mlb-849805", "2026-10-23", "2026-10-24T00:00:00Z", "Tampa Bay Rays", "Milwaukee Brewers",
     "American Family Field", 849805, "World Series Game 1"),
    ("mlb-849802", "2026-10-24", "2026-10-25T00:00:00Z", "Tampa Bay Rays", "Milwaukee Brewers",
     "American Family Field", 849802, "World Series Game 2"),
    ("mlb-849804", "2026-10-26", "2026-10-27T00:00:00Z", "Milwaukee Brewers", "Tampa Bay Rays",
     "Tropicana Field", 849804, "World Series Game 3"),
]

# Official records that were actually read. The Rays' record was NOT read this pass.
MLB_RECORDS = {
    "Milwaukee Brewers": {"wins": 103, "losses": 59, "runs_scored": 832, "runs_allowed": 618,
                          "division_rank": 1, "source_id": "mlb-nl-standings"},
}

# Sports where the official fixture list was not read in this pass. Each entry keeps the
# OLBG discovery route and the reason the row set is empty instead of invented.
COVERAGE_GAPS = {
    "tennis": "Official ATP scores page read on 2026-10-23 and returned three quarter-final-day "
              "tournaments, but the 2026-10-24 semi-final order of play was not read, so no "
              "upcoming fixture row is published.",
    "snooker": "BetVictor Northern Ireland Open 2026 (18-25 Oct, Belfast) confirmed on wst.tv and "
               "its round 1 results read, but the quarter-final/semi-final schedule for 24-25 Oct "
               "was not read, so no upcoming fixture row is published.",
    "golf": "No official tour schedule page was read in this pass; golf listings are tournament "
            "outrights rather than head-to-head matches, and none are published from memory.",
    "cricket": "No official fixture page was read in this pass.",
    "rugby_union": "No official fixture page was read in this pass.",
    "rugby_league": "No official fixture page was read in this pass.",
    "motor_racing": "No official fixture page was read in this pass.",
    "darts": "No official fixture page was read in this pass.",
    "handball": "No official fixture page was read in this pass.",
    "volleyball": "No official fixture page was read in this pass.",
    "gaelic_sports": "No official fixture page was read in this pass.",
    "greyhounds": "No official racecard was read in this pass.",
    "basketball": "NBA and EuroLeague fixture feeds were not read in this pass; the NBA public "
                  "scoreboard routes recorded as failing for peer sessions were not retried.",
}
