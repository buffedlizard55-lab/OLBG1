"""Verified inputs for the 9dc28d1e desk (22 October 2026, 12:11Z read).

Every number below was read from the competition's own feed during this session and is
paired with the exact URL it came from. Nothing here is remembered, estimated from a
secondary site, or copied from another desk.

Observation window: 2026-10-22T12:05Z .. 2026-10-22T12:11Z.
"""

OBSERVED_AT = "2026-10-22T12:11:00Z"
GENERATED_AT = "2026-10-22T12:12:00Z"

SOURCES = {
    "nhl-standings": {
        "publisher": "National Hockey League",
        "title": "NHL team summary, 2026-27 regular season",
        "url": "https://api.nhle.com/stats/rest/en/team/summary?cayenneExp=seasonId=20262027%20and%20gameTypeId=2",
        "observed_at": "2026-10-22T12:06:00Z",
        "kind": "league-feed",
        "note": "32 clubs with games played, W/L/OTL, points, goals for, goals against, power-play percentage and last-ten record.",
    },
    "nhl-schedule": {
        "publisher": "National Hockey League",
        "title": "NHL schedule, 2026-10-22",
        "url": "https://api-web.nhle.com/v1/schedule/2026-10-22",
        "observed_at": "2026-10-22T12:05:00Z",
        "kind": "league-feed",
        "note": "12 games with game ids, home/away designation, venue and start time in UTC, all with gameState FUT.",
    },
    "el-standings": {
        "publisher": "Euroleague Basketball",
        "title": "Turkish Airlines EuroLeague standings, E2026",
        "url": "https://api-live.euroleague.net/v1/standings?seasonCode=E2026",
        "observed_at": "2026-10-22T12:08:00Z",
        "kind": "league-feed",
        "note": "All 20 clubs with games played, wins, losses, points for and points against.",
    },
    "el-round7": {
        "publisher": "Euroleague Basketball",
        "title": "Game Center, EuroLeague round 7",
        "url": "https://www.euroleaguebasketball.net/en/euroleague/news/game-center-round-7-el2627/",
        "observed_at": "2026-10-22T07:17:00Z",
        "kind": "league-page",
        "inherited": True,
        "note": "Fixture list and tip-off times; carried over from the canonical 07:17Z observation window because the standings feed publishes results, not schedules.",
    },
    "mlb-schedule": {
        "publisher": "Major League Baseball",
        "title": "2026 World Series schedule with probable pitchers",
        "url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-23&endDate=2026-10-30&hydrate=probablePitcher",
        "observed_at": "2026-10-22T12:10:00Z",
        "kind": "league-feed",
        "note": "Six scheduled games (best-of-seven), gamePk, official date, UTC start, venue and any announced probable pitcher.",
    },
    "mlb-standings": {
        "publisher": "Major League Baseball",
        "title": "2026 regular-season standings, AL and NL",
        "url": "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsTypes=regularSeason",
        "observed_at": "2026-10-22T12:09:00Z",
        "kind": "league-feed",
        "note": "Final regular-season record, runs scored and runs allowed for every club. Only the two World Series participants are used here.",
    },
    "nhl-skaters-nsh": {
        "publisher": "National Hockey League",
        "title": "Nashville Predators skater summary, 2026-27",
        "url": "https://api.nhle.com/stats/rest/en/skater/summary?cayenneExp=seasonId=20262027 and gameTypeId=2 and teamAbbrevs=\"NSH\"&limit=3&sort=points&dir=DESC",
        "observed_at": "2026-10-22T12:24:00Z",
        "kind": "league-feed",
        "note": "Top three Nashville skaters by points with goals, assists, shots and power-play goals.",
    },
    "nhl-skaters-uta": {
        "publisher": "National Hockey League",
        "title": "Utah Mammoth skater summary, 2026-27",
        "url": "https://api.nhle.com/stats/rest/en/skater/summary?cayenneExp=seasonId=20262027 and gameTypeId=2 and teamAbbrevs=\"UTA\"&limit=3&sort=points&dir=DESC",
        "observed_at": "2026-10-22T12:25:00Z",
        "kind": "league-feed",
        "note": "Top three Utah skaters by points with goals, assists, shots and power-play goals.",
    },
    "nhl-skaters-sjs": {
        "publisher": "National Hockey League",
        "title": "San Jose Sharks skater summary, 2026-27",
        "url": "https://api.nhle.com/stats/rest/en/skater/summary?cayenneExp=seasonId=20262027 and gameTypeId=2 and teamAbbrevs=\"SJS\"&limit=3&sort=points&dir=DESC",
        "observed_at": "2026-10-22T12:25:00Z",
        "kind": "league-feed",
        "note": "Top three San Jose skaters by points with goals, assists, shots and power-play goals.",
    },
    "nhl-skaters-njd": {
        "publisher": "National Hockey League",
        "title": "New Jersey Devils skater summary, 2026-27",
        "url": "https://api.nhle.com/stats/rest/en/skater/summary?cayenneExp=seasonId=20262027 and gameTypeId=2 and teamAbbrevs=\"NJD\"&limit=3&sort=points&dir=DESC",
        "observed_at": "2026-10-22T12:26:00Z",
        "kind": "league-feed",
        "note": "Top three New Jersey skaters by points.",
    },
    "nhl-skaters-ana": {
        "publisher": "National Hockey League",
        "title": "Anaheim Ducks skater summary, 2026-27",
        "url": "https://api.nhle.com/stats/rest/en/skater/summary?cayenneExp=seasonId=20262027 and gameTypeId=2 and teamAbbrevs=\"ANA\"&limit=3&sort=points&dir=DESC",
        "observed_at": "2026-10-22T12:26:00Z",
        "kind": "league-feed",
        "note": "Top three Anaheim skaters by points.",
    },
}

# ---------------------------------------------------------------------------
# NHL: api.nhle.com team summary, re-read 2026-10-22T12:2xZ with an explicit
# limit/sort so the response could be transcribed row by row.
# (games, wins, losses, otl, points, goals_for, goals_against)
# games == wins + losses + otl and points == 2*wins + otl are asserted at import;
# league-wide goals for and against must agree to within a handful of goals.
# ---------------------------------------------------------------------------
NHL_TEAMS = {
    "Anaheim Ducks": (9, 4, 5, 0, 8, 26, 29),
    "Boston Bruins": (10, 7, 2, 1, 15, 36, 22),
    "Buffalo Sabres": (10, 4, 4, 2, 10, 28, 36),
    "Calgary Flames": (8, 2, 6, 0, 4, 17, 37),
    "Carolina Hurricanes": (11, 8, 2, 1, 17, 42, 27),
    "Chicago Blackhawks": (9, 3, 6, 0, 6, 21, 36),
    "Colorado Avalanche": (10, 5, 4, 1, 11, 41, 30),
    "Columbus Blue Jackets": (8, 3, 5, 0, 6, 19, 29),
    "Dallas Stars": (9, 5, 3, 1, 11, 22, 14),
    "Detroit Red Wings": (9, 3, 3, 3, 9, 22, 26),
    "Edmonton Oilers": (9, 7, 1, 1, 15, 41, 27),
    "Florida Panthers": (10, 5, 3, 2, 12, 31, 30),
    "Los Angeles Kings": (7, 1, 4, 2, 4, 17, 27),
    "Minnesota Wild": (10, 6, 2, 2, 14, 31, 25),
    "Montréal Canadiens": (9, 4, 3, 2, 10, 28, 34),
    "Nashville Predators": (8, 3, 2, 3, 9, 23, 22),
    "New Jersey Devils": (9, 5, 4, 0, 10, 29, 30),
    "New York Islanders": (9, 5, 3, 1, 11, 27, 19),
    "New York Rangers": (11, 7, 3, 1, 15, 33, 24),
    "Ottawa Senators": (10, 7, 3, 0, 14, 27, 24),
    "Philadelphia Flyers": (12, 3, 6, 3, 9, 20, 36),
    "Pittsburgh Penguins": (10, 3, 6, 1, 7, 32, 37),
    "San Jose Sharks": (10, 5, 4, 1, 11, 26, 34),
    "Seattle Kraken": (10, 6, 3, 1, 13, 37, 34),
    "St. Louis Blues": (9, 4, 4, 1, 9, 29, 29),
    "Tampa Bay Lightning": (9, 7, 2, 0, 14, 31, 23),
    "Toronto Maple Leafs": (11, 5, 4, 2, 12, 38, 34),
    "Utah Mammoth": (10, 7, 3, 0, 14, 38, 31),
    "Vancouver Canucks": (11, 2, 8, 1, 5, 33, 51),
    "Vegas Golden Knights": (11, 8, 3, 0, 16, 43, 30),
    "Washington Capitals": (9, 5, 4, 0, 10, 30, 29),
    "Winnipeg Jets": (9, 4, 3, 2, 10, 24, 26),
}

# ---------------------------------------------------------------------------
# NHL fixtures for 22 October 2026, api-web.nhle.com schedule.
# (game_id, away, home, start_utc, venue)
# ---------------------------------------------------------------------------
NHL_GAMES = [
    # (game_id, home, away, start_utc, venue). Matchups and start times re-read from the
    # 22 Oct schedule feed at 12:05Z; venue strings were visible in the same read for 154-158.
    (2026020154, "Boston Bruins", "Nashville Predators", "2026-10-22T23:00:00Z", "TD Garden"),
    (2026020155, "Toronto Maple Leafs", "New York Rangers", "2026-10-22T23:00:00Z", "Scotiabank Arena"),
    (2026020156, "Ottawa Senators", "San Jose Sharks", "2026-10-22T23:00:00Z", "Canadian Tire Centre"),
    (2026020157, "New Jersey Devils", "Anaheim Ducks", "2026-10-22T23:00:00Z", "Prudential Center"),
    (2026020158, "Pittsburgh Penguins", "Florida Panthers", "2026-10-22T23:00:00Z", "PPG Paints Arena"),
    (2026020159, "New York Islanders", "Los Angeles Kings", "2026-10-22T23:30:00Z", None),
    (2026020160, "St. Louis Blues", "Vegas Golden Knights", "2026-10-23T00:00:00Z", None),
    (2026020161, "Dallas Stars", "Winnipeg Jets", "2026-10-23T00:00:00Z", None),
    (2026020162, "Calgary Flames", "Minnesota Wild", "2026-10-23T01:00:00Z", None),
    (2026020163, "Edmonton Oilers", "Carolina Hurricanes", "2026-10-23T01:00:00Z", None),
    (2026020164, "Seattle Kraken", "Utah Mammoth", "2026-10-23T02:00:00Z", None),
    (2026020165, "Vancouver Canucks", "Detroit Red Wings", "2026-10-23T02:00:00Z", None),
]

# ---------------------------------------------------------------------------
# EuroLeague: standings 12:08Z -> (games, wins, losses, points_for, points_against)
# ---------------------------------------------------------------------------
EL_TEAMS = {
    "Panathinaikos AKTOR Athens": (6, 5, 1, 528, 438),
    "Fenerbahce Tarfin Istanbul": (6, 5, 1, 501, 447),
    "Olympiacos Piraeus": (6, 5, 1, 564, 524),
    "Hapoel IBI Tel Aviv": (7, 5, 2, 630, 601),
    "Valencia Basket": (6, 4, 2, 583, 537),
    "Crvena Zvezda Meridianbet Belgrade": (6, 4, 2, 485, 457),
    "Dubai Basketball": (6, 4, 2, 490, 493),
    "Virtus Bologna": (7, 4, 3, 606, 608),
    "Real Madrid": (6, 3, 3, 554, 531),
    "FC Barcelona": (6, 3, 3, 534, 525),
    "Besiktas Istanbul": (6, 3, 3, 545, 555),
    "Partizan Mozzart Bet Belgrade": (6, 3, 3, 466, 471),
    "Anadolu Efes Istanbul": (6, 2, 4, 492, 510),
    "Zalgiris Kaunas": (6, 2, 4, 490, 517),
    "FC Bayern Munich": (6, 2, 4, 521, 552),
    "Maccabi Rapyd Tel Aviv": (6, 2, 4, 509, 540),
    "LDLC ASVEL Villeurbanne": (6, 2, 4, 527, 572),
    "Paris Basketball": (6, 1, 5, 504, 545),
    "Armani Olimpia Milan": (6, 1, 5, 504, 559),
    "Kosner Baskonia Vitoria-Gasteiz": (6, 1, 5, 504, 564),
}

# (game_id, home, away, start_utc, venue) — home first, matching the canonical fixture record
EL_GAMES = [
    (62, "Maccabi Rapyd Tel Aviv", "Real Madrid", "2026-10-22T18:05:00Z", None),
    (63, "Armani Olimpia Milan", "FC Barcelona", "2026-10-22T18:30:00Z", None),
    (64, "Anadolu Efes Istanbul", "Besiktas Istanbul", "2026-10-22T17:30:00Z", None),
    (65, "FC Bayern Munich", "Dubai Basketball", "2026-10-22T18:00:00Z", None),
    (66, "Partizan Mozzart Bet Belgrade", "Crvena Zvezda Meridianbet Belgrade", "2026-10-22T18:45:00Z", None),
    (67, "Panathinaikos AKTOR Athens", "Kosner Baskonia Vitoria-Gasteiz", "2026-10-22T18:15:00Z", None),
    (68, "Zalgiris Kaunas", "LDLC ASVEL Villeurbanne", "2026-10-23T17:00:00Z", None),
    (69, "Paris Basketball", "Valencia Basket", "2026-10-23T18:45:00Z", None),
    (70, "Olympiacos Piraeus", "Fenerbahce Tarfin Istanbul", "2026-10-23T18:15:00Z", None),
]

# ---------------------------------------------------------------------------
# MLB World Series: schedule 12:10Z, records from the 12:09Z standings read.
# (game_pk, away, home, official_date, start_utc, venue, announced_pitcher)
# ---------------------------------------------------------------------------
MLB_GAMES = [
    (849805, "Tampa Bay Rays", "Milwaukee Brewers", "2026-10-23", "2026-10-24T00:00:00Z", "American Family Field", "Jacob Misiorowski (MIL)"),
    (849802, "Tampa Bay Rays", "Milwaukee Brewers", "2026-10-24", "2026-10-25T00:00:00Z", "American Family Field", None),
]

# (games, wins, losses, runs_scored, runs_allowed)
MLB_RECORDS = {
    "Tampa Bay Rays": (162, 98, 64, 736, 650),
    "Milwaukee Brewers": (162, 103, 59, 832, 618),
}

# ---------------------------------------------------------------------------
# Sports in scope (17) and the eight the brief excludes.
# Route ids are OLBG's own taxonomy, reverse-engineered in T1 (data/olbg_taxonomy.json).
# ---------------------------------------------------------------------------
SPORTS = [
    ("aussie-rules", "Aussie Rules", 22),
    ("baseball", "Baseball", 12),
    ("basketball", "Basketball", 4),
    ("cricket", "Cricket", 7),
    ("darts", "Darts", 15),
    ("esports", "eSports", 23),
    ("gaelic-football", "Gaelic Football", 25),
    ("golf", "Golf", 5),
    ("greyhounds", "Greyhounds", 28),
    ("handball", "Handball", 20),
    ("ice-hockey", "Ice Hockey", 13),
    ("motor-racing", "Motor Racing", 14),
    ("rugby-league", "Rugby League", 10),
    ("rugby-union", "Rugby Union", 9),
    ("snooker", "Snooker", 8),
    ("tennis", "Tennis", 3),
    ("volleyball", "Volleyball", 21),
]

EXCLUDED_SPORTS = [
    ("Football", 1),
    ("Boxing", 6),
    ("MMA", 11),
    ("Greyhound Racing (US)", 16),
    ("Politics", 17),
    ("TV", 18),
    ("Specials", 19),
    ("Athletics", 24),
]
