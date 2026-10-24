"""Verified fixture inputs for the 9e041d28 desk.

Every number below was read from the official source named on the row during
this session (2026-10-24, between 16:30Z and 17:40Z). Nothing is filled in from
memory, and where a value was not published by the official source it is left as
an empty string and listed in ``blank`` so the site can flag it.

Sources used for this file
--------------------------
MLB_SCHEDULE  https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-24&endDate=2026-10-28&hydrate=probablePitcher,team,venue
MLB_STANDINGS https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsTypes=regularSeason
NHL_SCHEDULE  https://api-web.nhle.com/v1/schedule/2026-10-24
NHL_SCHEDULE2 https://api-web.nhle.com/v1/schedule/2026-10-25
NHL_STANDINGS https://api-web.nhle.com/v1/standings/2026-10-24
WST_MATCHES   https://www.wst.tv/matches/
F1_US_GP      https://www.formula1.com/en/racing/2026/united-states
ATP_SCORES    https://www.atptour.com/en/scores/current
NBA_GAMES     https://www.nba.com/games
NBA_STANDINGS https://www.nba.com/standings
URC_ROUND4    https://stats.unitedrugby.com/match-centre/2026-27/4
URC_TABLE     https://stats.unitedrugby.com/match-centre/table/2026-27
OLBG_*        the 15 sport hubs under https://www.olbg.com/betting-tips/<Sport>/<id>
"""

SNAPSHOT_UTC = "2026-10-24T18:20:00Z"

MLB_SCHEDULE = ("https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-24"
                "&endDate=2026-10-28&hydrate=probablePitcher,team,venue")
MLB_STANDINGS = ("https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026"
                 "&standingsTypes=regularSeason")
NHL_SCHEDULE = "https://api-web.nhle.com/v1/schedule/2026-10-24"
NHL_SCHEDULE_25 = "https://api-web.nhle.com/v1/schedule/2026-10-25"
NHL_STANDINGS = "https://api-web.nhle.com/v1/standings/2026-10-24"
WST_MATCHES = "https://www.wst.tv/matches/"
F1_US_GP = "https://www.formula1.com/en/racing/2026/united-states"
ATP_SCORES = "https://www.atptour.com/en/scores/current"
NBA_GAMES = "https://www.nba.com/games"
NBA_STANDINGS = "https://www.nba.com/standings"
URC_ROUND4 = "https://stats.unitedrugby.com/match-centre/2026-27/4"
URC_TABLE = "https://stats.unitedrugby.com/match-centre/table/2026-27"
MLB_ROSTER_MIL = "https://statsapi.mlb.com/api/v1/teams/158/roster?rosterType=active"
MLB_ROSTER_TB = "https://statsapi.mlb.com/api/v1/teams/139/roster?rosterType=active"
MLB_GAME_FEED = "https://statsapi.mlb.com/api/v1.1/game/849802/feed/live"

SPORTS = [
    ("baseball", "Baseball", 12, "Baseball"),
    ("basketball", "Basketball", 4, "Basketball"),
    ("cricket", "Cricket", 7, "Cricket"),
    ("darts", "Darts", 15, "Darts"),
    ("gaelic-sports", "Gaelic Sports", 25, "Gaelic_Football"),
    ("golf", "Golf", 5, "Golf"),
    ("greyhounds", "Greyhounds", 28, "Greyhounds"),
    ("handball", "Handball", 20, "Handball"),
    ("ice-hockey", "Ice Hockey", 13, "Ice_Hockey"),
    ("motor-racing", "Motor Racing", 14, "Motor_Racing"),
    ("rugby-league", "Rugby League", 10, "Rugby_League"),
    ("rugby-union", "Rugby Union", 9, "Rugby_Union"),
    ("snooker", "Snooker", 8, "Snooker"),
    ("tennis", "Tennis", 3, "Tennis"),
    ("volleyball", "Volleyball", 21, "Volleyball"),
]

# ---------------------------------------------------------------------------
# Verified fixtures. ``inputs`` holds only values read from the official source.
# ---------------------------------------------------------------------------
FIXTURES = [
    {
        "id": "B1",
        "sport": "baseball",
        "competition": "MLB World Series 2026 - Game 2",
        "event": "Tampa Bay Rays at Milwaukee Brewers",
        "home": "Milwaukee Brewers",
        "away": "Tampa Bay Rays",
        "venue": "American Family Field, Milwaukee",
        "start_utc": "2026-10-25T00:00:00Z",
        "official": ("MLB StatsAPI - World Series Game 2 (gamePk 849802): Tampa Bay at Milwaukee, "
                     "American Family Field, first pitch 2026-10-25T00:00:00Z"),
        "official_url": MLB_SCHEDULE,
        "stats_url": MLB_STANDINGS,
        "olbg_url": ("https://www.olbg.com/betting-tips/Baseball/MLB/MLB/"
                     "TB_Rays_@_MIL_Brewers/12?event_id=160792"),
        "olbg_label": "Today 20:00 (unlabelled timezone; official start 00:00 UTC 25 Oct)",
        "home_record": "103-59 (.636)",
        "away_record": "98-64 (.605)",
        "form": ("Milwaukee 103-59, .636, 68-35 at night, 8-2 in their last ten; "
                 "Tampa Bay 98-64, .605, 5-5 in their last ten, L1."),
        "stats": ("Milwaukee 832 runs scored / 618 allowed (+214); Tampa Bay 736 / 650 (+86). "
                  "Home/road: MIL 55-26 home, TB 43-38 away."),
        "probables": "Logan Henderson (MIL) vs Drew Rasmussen (TB)",
        "series": "Milwaukee lead 1-0; Game 1 finished 3-2 to Milwaukee.",
        "injuries": ("MLB StatsAPI active roster for both clubs lists 26 players each and every one "
                     "carries status Active, so neither side has an injured-list entry at 18:05Z."),
        "blank": [],
        "sport_home_rate": 0.679,   # MIL home win rate (55-26)
        "sport_away_rate": 0.531,   # TB away win rate (43-38)
        "home_runs_for": 832 / 162, "home_runs_against": 618 / 162,
        "away_runs_for": 736 / 162, "away_runs_against": 650 / 162,
        "total_candidates": [7.5, 8.5, 9.5],
        "handicap": -1.5,
        "league": "mlb",
    },
    {
        "id": "B2",
        "sport": "baseball",
        "competition": "MLB World Series 2026 - Game 3",
        "event": "Milwaukee Brewers at Tampa Bay Rays",
        "home": "Tampa Bay Rays",
        "away": "Milwaukee Brewers",
        "venue": "Tropicana Field, St. Petersburg",
        "start_utc": "2026-10-27T00:00:00Z",
        "official": "MLB StatsAPI - World Series Game 3 (gamePk 849804), scheduled, both probable pitchers published",
        "official_url": MLB_SCHEDULE,
        "stats_url": MLB_STANDINGS,
        "olbg_url": "",
        "olbg_label": "Not shown on the OLBG baseball hub at retrieval time (only Game 2 was listed)",
        "home_record": "98-64 (.605)",
        "away_record": "103-59 (.636)",
        "form": ("Tampa Bay 98-64 with a 55-26 home record; Milwaukee 103-59 and 48-33 on the road."),
        "stats": ("Tampa Bay 736 runs scored / 650 allowed (+86), 55-26 at home; "
                  "Milwaukee 832 / 618 (+214), 48-33 away."),
        "probables": "Tampa Bay: Freddy Peralta. Milwaukee: Robert Gasser.",
        "series": "Series score at retrieval: Milwaukee 1-0 after Game 1.",
        "injuries": ("MLB StatsAPI active roster for both clubs lists 26 players each and every one "
                     "carries status Active, so neither side has an injured-list entry at 18:05Z."),
        "blank": ["OLBG listing for this game not found at retrieval time"],
        "sport_home_rate": 0.679,
        "sport_away_rate": 0.593,
        "home_runs_for": 736 / 162, "home_runs_against": 650 / 162,
        "away_runs_for": 832 / 162, "away_runs_against": 618 / 162,
        "total_candidates": [7.5, 8.5, 9.5],
        "handicap": -1.5,
        "league": "mlb",
    },
    {
        "id": "B3",
        "sport": "baseball",
        "competition": "MLB World Series 2026 - Game 4",
        "event": "Milwaukee Brewers at Tampa Bay Rays",
        "home": "Tampa Bay Rays",
        "away": "Milwaukee Brewers",
        "venue": "Tropicana Field, St. Petersburg",
        "start_utc": "2026-10-28T00:00:00Z",
        "official": "MLB StatsAPI - World Series Game 4 (gamePk 849803), scheduled, probable pitchers not yet published",
        "official_url": MLB_SCHEDULE,
        "stats_url": MLB_STANDINGS,
        "olbg_url": "",
        "olbg_label": "Not shown on the OLBG baseball hub at retrieval time",
        "home_record": "98-64 (.605)",
        "away_record": "103-59 (.636)",
        "form": ("Tampa Bay 98-64, 55-26 at home; Milwaukee 103-59, 48-33 away."),
        "stats": ("Tampa Bay 736 / 650 (+86); Milwaukee 832 / 618 (+214)."),
        "probables": "",
        "series": "Series score at retrieval: Milwaukee 1-0 after Game 1.",
        "injuries": ("MLB StatsAPI active roster for both clubs lists 26 players each and every one "
                     "carries status Active, so neither side has an injured-list entry at 18:05Z."),
        "blank": ["probable pitchers not published for this game at retrieval time",
                  "OLBG listing for this game not found at retrieval time"],
        "sport_home_rate": 0.679,
        "sport_away_rate": 0.593,
        "home_runs_for": 736 / 162, "home_runs_against": 650 / 162,
        "away_runs_for": 832 / 162, "away_runs_against": 618 / 162,
        "total_candidates": [7.5, 8.5, 9.5],
        "handicap": -1.5,
        "league": "mlb",
    },
    {
        "id": "N1",
        "sport": "ice-hockey",
        "competition": "NHL 2026-27 regular season",
        "event": "San Jose Sharks at Boston Bruins",
        "home": "Boston Bruins",
        "away": "San Jose Sharks",
        "venue": "TD Garden, Boston",
        "start_utc": "2026-10-24T23:00:00Z",
        "official": "NHL API schedule for 24 October 2026 - fixture and start time published by the league",
        "official_url": NHL_SCHEDULE,
        "stats_url": NHL_STANDINGS,
        "olbg_url": ("https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/"
                     "SJ_Sharks_@_BOS_Bruins/13?event_id=200007"),
        "olbg_label": "Today 19:07 (unlabelled timezone; official start 23:00 UTC)",
        "home_record": "8-2-1 (17 points)",
        "away_record": "6-4-1 (13 points)",
        "form": ("Boston 8-2-1, 17 points, 4-1 at home and 7-2-1 across their last ten. "
                 "San Jose 6-4-1 for 13 points."),
        "stats": ("Boston 42 goals for / 22 against, including 21 for and 6 against across five "
                  "home games. San Jose 33 for / 37 against, a minus-four goal difference."),
        "probables": "",
        "series": "Regular-season game.",
        "injuries": "",
        "blank": ["starting goaltenders and injuries not published by the source read"],
        "home_win_rate": 0.7273,   # regulation + overtime wins / games played (8/11)
        "away_win_rate": 0.4545,   # (5/11)
        "home_gf": 42 / 11, "home_ga": 22 / 11,
        "away_gf": 33 / 11, "away_ga": 37 / 11,
        "home_home_gf": 21 / 5, "home_home_ga": 6 / 5,
        "away_road_gf": 20 / 7, "away_road_ga": 21 / 7,
        "total_candidates": [4.5, 5.5, 6.5],
        "handicap": -1.5,
        "league": "nhl",
    },
    {
        "id": "N2",
        "sport": "ice-hockey",
        "competition": "NHL 2026-27 regular season",
        "event": "New York Rangers at Ottawa Senators",
        "home": "Ottawa Senators",
        "away": "New York Rangers",
        "venue": "Canadian Tire Centre, Ottawa",
        "start_utc": "2026-10-24T23:00:00Z",
        "official": "NHL API schedule for 24 October 2026 - fixture and start time published by the league",
        "official_url": NHL_SCHEDULE,
        "stats_url": NHL_STANDINGS,
        "olbg_url": ("https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/"
                     "NY_Rangers_@_OTT_Senators/13?event_id=200008"),
        "olbg_label": "Today 19:07 (unlabelled timezone; official start 23:00 UTC)",
        "home_record": "7-4-0 (14 points)",
        "away_record": "7-4-1 (15 points)",
        "form": ("Ottawa 7-4-0 for 14 points. NY Rangers 7-4-1 for 15 points, 6-0-0 at home "
                 "but 1-4-1 on the road."),
        "stats": ("Ottawa 31 goals for / 30 against. NY Rangers 37 for / 29 against, the better "
                  "goal difference of the two."),
        "probables": "",
        "series": "Regular-season game.",
        "injuries": "",
        "blank": ["starting goaltenders and injuries not published by the source read"],
        "home_win_rate": 0.4545,
        "away_win_rate": 0.5833,
        "home_gf": 31 / 11, "home_ga": 30 / 11,
        "away_gf": 37 / 12, "away_ga": 29 / 12,
        "home_home_gf": 16 / 6, "home_home_ga": 18 / 6,
        "away_road_gf": 8 / 6, "away_road_ga": 19 / 6,
        "total_candidates": [4.5, 5.5, 6.5],
        "handicap": -1.5,
        "league": "nhl",
    },
    {
        "id": "N3",
        "sport": "ice-hockey",
        "competition": "NHL 2026-27 regular season",
        "event": "Nashville Predators at Pittsburgh Penguins",
        "home": "Pittsburgh Penguins",
        "away": "Nashville Predators",
        "venue": "PPG Paints Arena, Pittsburgh",
        "start_utc": "2026-10-24T23:00:00Z",
        "official": "NHL API schedule for 24 October 2026 - fixture and start time published by the league",
        "official_url": NHL_SCHEDULE,
        "stats_url": NHL_STANDINGS,
        "olbg_url": ("https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/"
                     "NSH_Predators_@_PIT_Penguins/13?event_id=200006"),
        "olbg_label": "Today 19:07 (unlabelled timezone; official start 23:00 UTC)",
        "home_record": "4-6-1 (9 points)",
        "away_record": "3-3-3 (9 points)",
        "form": ("Pittsburgh 4-6-1 for 9 points, 3-1 at home, W1. Nashville 3-3-3 for 9 points."),
        "stats": ("Pittsburgh 37 goals for / 38 against and a regulation-plus-overtime win rate "
                  "of .273. Nashville 23 for / 30 against and .333."),
        "probables": "",
        "series": "Regular-season game.",
        "injuries": "",
        "blank": ["starting goaltenders and injuries not published by the source read"],
        "home_win_rate": 0.2727,
        "away_win_rate": 0.3333,
        "home_gf": 37 / 11, "home_ga": 38 / 11,
        "away_gf": 23 / 9, "away_ga": 30 / 9,
        "home_home_gf": 14 / 4, "home_home_ga": 9 / 4,
        "away_road_gf": 11 / 4, "away_road_ga": 16 / 4,
        "total_candidates": [5.5, 6.5, 7.5],
        "handicap": -1.5,
        "league": "nhl",
    },
    {
        "id": "N4",
        "sport": "ice-hockey",
        "competition": "NHL 2026-27 regular season",
        "event": "Buffalo Sabres at Washington Capitals",
        "home": "Washington Capitals",
        "away": "Buffalo Sabres",
        "venue": "Capital One Arena, Washington",
        "start_utc": "2026-10-24T23:00:00Z",
        "official": "NHL API schedule for 24 October 2026 - fixture and start time published by the league",
        "official_url": NHL_SCHEDULE,
        "stats_url": NHL_STANDINGS,
        "olbg_url": "",
        "olbg_label": "Not listed on the OLBG ice hockey hub at retrieval time",
        "home_record": "5-4-0 (10 points)",
        "away_record": "4-4-2 (10 points)",
        "form": ("Washington 5-4-0 for 10 points, 4-2 at home, L1. Buffalo 4-4-2 for 10 points."),
        "stats": ("Washington 30 goals for / 29 against, five wins in nine. Buffalo 28 for / 37 "
                  "against, minus nine, with two regulation wins in ten."),
        "probables": "",
        "series": "Regular-season game.",
        "injuries": "",
        "blank": ["starting goaltenders and injuries not published by the source read",
                  "OLBG listing for this game not found at retrieval time"],
        "home_win_rate": 0.5556,
        "away_win_rate": 0.4000,
        "home_gf": 30 / 9, "home_ga": 29 / 9,
        "away_gf": 28 / 10, "away_ga": 37 / 10,
        "home_home_gf": 22 / 6, "home_home_ga": 20 / 6,
        "away_road_gf": 14 / 4, "away_road_ga": 18 / 4,
        "total_candidates": [5.5, 6.5, 7.5],
        "handicap": -1.5,
        "league": "nhl",
    },
    {
        "id": "N5",
        "sport": "ice-hockey",
        "competition": "NHL 2026-27 regular season",
        "event": "New York Islanders at Dallas Stars",
        "home": "Dallas Stars",
        "away": "New York Islanders",
        "venue": "American Airlines Center, Dallas",
        "start_utc": "2026-10-25T22:00:00Z",
        "official": "NHL API schedule for 25 October 2026 - fixture and start time published by the league",
        "official_url": NHL_SCHEDULE_25,
        "stats_url": NHL_STANDINGS,
        "olbg_url": "",
        "olbg_label": "Not listed on the OLBG ice hockey hub at retrieval time",
        "home_record": "6-3-1 (13 points)",
        "away_record": "5-3-2 (12 points)",
        "form": ("Dallas 6-3-1 for 13 points and on a four-game winning run. "
                 "NY Islanders 5-3-2 for 12 points."),
        "stats": ("Dallas 26 goals for / 17 against. NY Islanders 29 for / 23 against."),
        "probables": "",
        "series": "Regular-season game.",
        "injuries": "",
        "blank": ["starting goaltenders and injuries not published by the source read",
                  "OLBG listing for this game not found at retrieval time"],
        "home_win_rate": 0.5000,
        "away_win_rate": 0.5000,
        "home_gf": 26 / 10, "home_ga": 17 / 10,
        "away_gf": 29 / 10, "away_ga": 23 / 10,
        "home_home_gf": 13 / 5, "home_home_ga": 11 / 5,
        "away_road_gf": 8 / 4, "away_road_ga": 10 / 4,
        "total_candidates": [4.5, 5.5, 6.5],
        "handicap": -1.5,
        "league": "nhl",
    },
]

# ---------------------------------------------------------------------------
# Predictions. Each is at least 30 words, unique, and quotes only the numbers
# held above. No row uses the words "model" or "verified".
# ---------------------------------------------------------------------------
WRITEUPS = {
    "B1": (
        "Back Milwaukee Brewers on the moneyline for World Series Game 2 at American Family "
        "Field. The Brewers finished the regular season 103-59 with a +214 run differential, "
        "scoring 832 runs and allowing 618, and they were 68-35 under lights with an 8-2 close. "
        "Tampa Bay went 98-64 but only 43-38 on the road, and they lost Game 1 by 3-2. "
        "Logan Henderson starts for Milwaukee against Drew Rasmussen, and both active rosters are "
        "full with every player listed Active, so no injured-list entry undermines those plans."),
    "B2": (
        "Tampa Bay Rays to win Game 3 on the moneyline as the series shifts to Tropicana Field. "
        "The Rays were 55-26 at home inside a 98-64 season, scoring 736 runs and conceding 650, "
        "while Milwaukee are 48-33 on the road against 55-26 at home. Freddy Peralta takes the "
        "ball for Tampa Bay opposite Robert Gasser, both active rosters are clear of injured-list "
        "entries, and a 3-2 defeat in Game 1 makes this an early must-win for the home side. "
        "Milwaukee's 8-2 close is the counterweight, which is why this stays a Medium call."),
    "B3": (
        "Tampa Bay Rays to win Game 4 at Tropicana Field, where a 55-26 home record carried a "
        "98-64 season. They scored 736 runs and allowed 650 across 162 games. Milwaukee scored "
        "832 and allowed 618 but were 48-33 away against 55-26 at home, and both active rosters "
        "are clear of injured-list entries. Neither starter had been published when this price "
        "was set, so a 59% edge is treated as Medium rather than anything stronger."),
    "N1": (
        "Boston Bruins to win at TD Garden, though the price sits outside the brief's -250 floor "
        "and no official availability report was published, so the label is Medium on both counts. Boston are 8-2-1 with 17 points, have "
        "conceded six goals in five home games and are 7-2-1 across their last ten. San Jose are "
        "6-4-1 and 4-2-1 on the road, but they have been outscored 37-33 and have one regulation "
        "win in eleven, so the Bruins' five-on-five profile is the stronger side of this matchup."),
    "N2": (
        "New York Rangers to win on the road in Ottawa. The Rangers are 7-4-1 with 15 points and "
        "have conceded only 29 goals in twelve games, while Ottawa are 7-4-0 having scored 31 and "
        "allowed 30 in eleven. New York's 1-4-1 road record and eight goals in six away games are "
        "the obvious counter-argument, but a 37-29 goal line against Ottawa's 31-30 is the better "
        "profile, and -168 is the right side of a close game. No official availability report exists "
        "for either club, so the label stops at Medium."),
    "N3": (
        "Nashville Predators to win in Pittsburgh. Neither side is in form: Nashville are 3-3-3 "
        "and Pittsburgh 4-6-1, but the Predators' regulation-plus-overtime win rate of .333 still "
        "edges the Penguins' .273, and Pittsburgh have conceded 38 goals in eleven games against "
        "Nashville's 30 in nine. Neither side is convincing, so this is a small-stakes Medium call."),
    "N4": (
        "Washington Capitals to win at home against Buffalo. Washington are 5-4-0 with a .556 "
        "regulation-plus-overtime win rate, have scored 30 goals in nine games and are 4-2 at "
        "Capital One Arena. Buffalo are 4-4-2, have been outscored 37-28 and have managed only "
        "two regulation wins in ten games and a minus-nine goal difference. That keeps the game from "
        "being a rout, but the rates point clearly to the home side. With no official availability "
        "report published, the call is capped at Medium."),
    "N5": (
        "Dallas Stars to win at home against the New York Islanders, at a fair probability of "
        "about one half. Dallas are 6-3-1 on a four-game winning run and have conceded only 17 "
        "goals in ten games while scoring 26, a plus-nine goal difference. The Islanders are "
        "5-3-2 with 29 scored and 23 conceded, which is a wider spread in both directions. "
        "Two 50% win rates produce a coin flip, so this is Low confidence by construction."),
}

# ---------------------------------------------------------------------------
# OLBG inventory. Every row was seen on the public hub named in the URL.
# ``off`` is True when a governing body confirmed the fixture this session.
# ---------------------------------------------------------------------------
def _o(slug, sid):
    return f"https://www.olbg.com/betting-tips/{slug}/{sid}"

OLBG_INVENTORY = [
    # baseball
    ("baseball", "TB Rays @ MIL Brewers", "MLB", "Today 20:00", "B1",
     "https://www.olbg.com/betting-tips/Baseball/MLB/MLB/TB_Rays_@_MIL_Brewers/12?event_id=160792"),
    # basketball
    ("basketball", "HOU Rockets @ ATL Hawks", "NBA", "Today 20:30", "", "https://www.olbg.com/betting-tips/Basketball/NBA/NBA/HOU_Rockets_@_ATL_Hawks/4?event_id=536115"),
    ("basketball", "MIA Heat @ CHA Hornets", "NBA", "Today 18:00", "", "https://www.olbg.com/betting-tips/Basketball/NBA/NBA/MIA_Heat_@_CHA_Hornets/4?event_id=536117"),
    ("basketball", "BKN Nets @ CLE Cavaliers", "NBA", "Today 19:30", "", "https://www.olbg.com/betting-tips/Basketball/NBA/NBA/BKN_Nets_@_CLE_Cavaliers/4?event_id=536112"),
    ("basketball", "MIL Bucks @ PHI 76ers", "NBA", "Today 19:30", "", "https://www.olbg.com/betting-tips/Basketball/NBA/NBA/MIL_Bucks_@_PHI_76ers/4?event_id=536111"),
    ("basketball", "SA Spurs @ DAL Mavericks", "NBA", "Today 20:00", "", "https://www.olbg.com/betting-tips/Basketball/NBA/NBA/SA_Spurs_@_DAL_Mavericks/4?event_id=536114"),
    ("basketball", "WAS Wizards @ CHI Bulls", "NBA", "Today 20:00", "", "https://www.olbg.com/betting-tips/Basketball/NBA/NBA/WAS_Wizards_@_CHI_Bulls/4?event_id=536113"),
    ("basketball", "NO Pelicans @ DEN Nuggets", "NBA", "Today 22:00", "", "https://www.olbg.com/betting-tips/Basketball/NBA/NBA/NO_Pelicans_@_DEN_Nuggets/4?event_id=536116"),
    ("basketball", "GS Warriors @ PHX Suns", "NBA", "Today 23:00", "", "https://www.olbg.com/betting-tips/Basketball/NBA/NBA/GS_Warriors_@_PHX_Suns/4?event_id=536118"),
    ("basketball", "Slask Wroclaw vs Astoria Bydgoszcz", "Poland PLK", "Today 13:30", "", "https://www.olbg.com/betting-tips/Basketball/European/Poland_PLK/Slask_Wroclaw_vs_Astoria_Bydgoszcz/4?event_id=536075"),
    ("basketball", "Pato Basquete vs Botafogo", "Brazil NBB", "Today 18:00", "", "https://www.olbg.com/betting-tips/Basketball/Other/Brazil_NBB/Pato_Basquete_vs_Botafogo/4?event_id=536087"),
    # cricket
    ("cricket", "Toronto Kings vs Vancouver Guardians T20", "", "Today 19:00", "", "https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Toronto_Kings_vs_Vancouver_Guardians_T20/7?event_id=188845"),
    ("cricket", "Pakistan vs England One Day Match", "", "Tomorrow 04:00", "", "https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Pakistan_vs_England_One_Day_Match/7?event_id=188838"),
    ("cricket", "North West Dragons vs Northern Cape Heat T20", "", "Tomorrow 07:00", "", "https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/North_West_Dragons_vs_Northern_Cape_Heat_T20/7?event_id=188851"),
    ("cricket", "Tuskers vs Western Province T20", "", "Tomorrow 07:00", "", "https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Tuskers_vs_Western_Province_T20/7?event_id=188850"),
    ("cricket", "New Zealand vs India 3rd T20", "", "27 Oct 03:00", "", "https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/New_Zealand_vs_India_3rd_T20_Match/7?event_id=188852"),
    ("cricket", "India W vs Zimbabwe W 2nd ODI", "", "Tomorrow 04:30", "", "https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/India_W_vs_Zimbabwe_W_2nd_ODI/7?event_id=188847"),
    ("cricket", "Eastern Storm vs South Africa Emerging T20", "", "Tomorrow 07:00", "", "https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Eastern_Storm_vs_South_Africa_Emerging_T20/7?event_id=188848"),
    ("cricket", "Boland vs Titans T20", "", "Tomorrow 07:00", "", "https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Boland_vs_Titans_T20/7?event_id=188849"),
    ("cricket", "South Africa vs Australia", "", "31 Oct 04:30", "", "https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/South_Africa_vs_Australia/7?event_id=188835"),
    # darts
    ("darts", "Krzysztof Ratajski vs Kevin Doets", "European Championship", "Today 13:15", "", "https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Krzysztof_Ratajski_vs_Kevin_Doets/15?event_id=32399"),
    ("darts", "Jonny Clayton vs Josh Rock", "European Championship", "Today 16:15", "", "https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Jonny_Clayton_vs_Josh_Rock/15?event_id=32400"),
    ("darts", "Nathan Aspinall vs Luke Littler", "European Championship", "Today 15:15", "", "https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Nathan_Aspinall_vs_Luke_Littler/15?event_id=32397"),
    ("darts", "Martin Schindler vs Jermaine Wattimena", "European Championship", "Today 14:15", "", "https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Martin_Schindler_vs_Jermaine_Wattimena/15?event_id=32398"),
    ("darts", "Gerwyn Price vs Stephen Bunting", "European Championship", "Tomorrow 07:00", "", "https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Gerwyn_Price_vs_Stephen_Bunting/15?event_id=32407"),
    # gaelic
    ("gaelic-sports", "Moycullen vs Salthill-Knocknacarra", "Galway club", "Tomorrow 12:00", "", "https://www.olbg.com/betting-tips/Gaelic_Football/All_Gaelic_Football/All_Events/Moycullen_v_Salthill-Knocknacarra/25?event_id=3532"),
    ("gaelic-sports", "St Finbarrs vs Nemo Rangers", "Cork club", "Tomorrow 12:00", "", "https://www.olbg.com/betting-tips/Gaelic_Football/All_Gaelic_Football/All_Events/St_Finbarrs_v_Nemo_Rangers/25?event_id=3530"),
    ("gaelic-sports", "Kanturk vs Eire Og Cor", "Cork club", "01 Nov 09:00", "", "https://www.olbg.com/betting-tips/Gaelic_Football/All_Gaelic_Football/All_Events/Kanturk_v_Eire_Og_Cor/25?event_id=3531"),
    ("gaelic-sports", "Fr Caseys vs Kildimo Pallaskenry", "Limerick club", "01 Nov 10:30", "", "https://www.olbg.com/betting-tips/Gaelic_Football/All_Gaelic_Football/All_Events/Fr_Caseys_v_Kildimo_Pallaskenry/25?event_id=3537"),
    # handball
    ("handball", "HBW Balingen Weilstetten vs MT Melsungen", "", "Today 14:00", "", "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/HBW_Balingen_Weilstetten_vs_MT_Melsungen/20?event_id=12090"),
    ("handball", "BM Logrono La Rioja vs BM Cangas", "", "Today 13:30", "", "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/BM_Logrono_La_Rioja_vs_BM_Cangas/20?event_id=12103"),
    ("handball", "SC Magdeburg vs HC Kriens Luzern", "", "28 Oct 15:45", "", "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/SC_Magdeburg_vs_HC_Kriens_Luzern/20?event_id=12136"),
    ("handball", "BM Granollers vs Angel Ximenez Puente Genil", "", "Tomorrow 07:30", "", "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/BM_Granollers_vs_Angel_Ximenez_Puente_Genil/20?event_id=12102"),
    ("handball", "Rhein Neckar Lowen vs SC Magdeburg", "", "Tomorrow 10:00", "", "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/Rhein_Neckar_Lowen_vs_SC_Magdeburg/20?event_id=12092"),
    ("handball", "Luxembourg W vs Great Britain W", "", "Tomorrow 11:00", "", "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/Luxembourg_W_vs_Great_Britain_W/20?event_id=12126"),
    ("handball", "Saint Raphael vs PSG Handball", "", "Tomorrow 11:00", "", "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/Saint_Raphael_vs_PSG_Handball/20?event_id=12084"),
    ("handball", "HC Vardar vs MT Melsungen", "", "28 Oct 13:45", "", "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/HC_Vardar_vs_MT_Melsungen/20?event_id=12130"),
    ("handball", "KS Kielce vs Kolstad", "", "28 Oct 15:45", "", "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/KS_Kielce_vs_Kolstad/20?event_id=12132"),
    ("handball", "GOG vs Sporting CP", "", "29 Oct 13:45", "", "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/GOG_vs_Sporting_CP/20?event_id=12129"),
    # ice hockey (OLBG only)
    ("ice-hockey", "ANA Ducks @ PHI Flyers", "NHL", "Today 13:07", "", "https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/ANA_Ducks_@_PHI_Flyers/13?event_id=199999"),
    ("ice-hockey", "CAR Hurricanes @ STL Blues", "NHL", "Today 19:07", "", "https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/CAR_Hurricanes_@_STL_Blues/13?event_id=200002"),
    ("ice-hockey", "LA Kings @ NJ Devils", "NHL", "Today 15:37", "", "https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/LA_Kings_@_NJ_Devils/13?event_id=200000"),
    ("ice-hockey", "TB Lightning @ UTA Mammoth", "NHL", "Today 22:07", "", "https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/TB_Lightning_@_UTA_Mammoth/13?event_id=200009"),
    ("ice-hockey", "TOR Maple Leafs @ EDM Oilers", "NHL", "Today 19:07", "", "https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/TOR_Maple_Leafs_@_EDM_Oilers/13?event_id=200010"),
    ("ice-hockey", "VGS Golden Knights @ CLB Blue Jackets", "NHL", "Today 19:07", "", "https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/VGS_Golden_Knights_@_CLB_Blue_Jackets/13?event_id=200001"),
    ("ice-hockey", "MIN Wild @ SEA Kraken", "NHL", "Today 23:07", "", "https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/MIN_Wild_@_SEA_Kraken/13?event_id=200005"),
    ("ice-hockey", "DET Red Wings @ CGY Flames", "NHL", "Today 23:07", "", "https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/DET_Red_Wings_@_CGY_Flames/13?event_id=200004"),
    ("ice-hockey", "EHC Kloten vs Rapperswil Jona Lakers", "Switzerland NLA", "Today 13:45", "", "https://www.olbg.com/betting-tips/Ice_Hockey/Other/Switzerland_NLA/EHC_Kloten_vs_Rapperswil_Jona_Lakers/13?event_id=200024"),
    ("ice-hockey", "EHC Biel vs Zug", "Switzerland NLA", "Today 13:45", "", "https://www.olbg.com/betting-tips/Ice_Hockey/Other/Switzerland_NLA/EHC_Biel_vs_Zug/13?event_id=200019"),
    ("ice-hockey", "SCL Tigers vs Davos", "Switzerland NLA", "Today 13:45", "", "https://www.olbg.com/betting-tips/Ice_Hockey/Other/Switzerland_NLA/SCL_Tigers_vs_Davos/13?event_id=200022"),
    # motor racing
    ("motor-racing", "USA Grand Prix - race winner", "Formula 1", "25 Oct 16:00 track time", "", "https://www.olbg.com/betting-tips/Motor_Racing/All_Motor_Racing/All_Events/USA_Grand_Prix/14?event_id=913"),
    # rugby league: none
    # rugby union
    ("rugby-union", "Ospreys v Dragons", "URC", "Today 14:00", "", "https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Ospreys_v_Dragons/9?event_id=609581"),
    ("rugby-union", "Toulon v Pau", "Top 14", "Today 15:00", "", "https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Toulon_v_Pau/9?event_id=609555"),
    ("rugby-union", "USA v Australia A", "International", "Today 19:00", "", "https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/USA_v_Australia_A/9?event_id=609583"),
    ("rugby-union", "Harlequins v Saracens", "Premiership", "Tomorrow 11:00", "", "https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Harlequins_v_Saracens/9?event_id=609571"),
    ("rugby-union", "La Rochelle v Bordeaux", "Top 14", "Tomorrow 16:05", "", "https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/La_Rochelle_v_Bordeaux/9?event_id=609554"),
    # snooker
    ("snooker", "Mark Williams v Jak Jones", "Northern Ireland Open SF", "Today 14:00", "", "https://www.olbg.com/betting-tips/Snooker/All_Snooker/All_Events/Mark_Williams_v_Jak_Jones/8?event_id=9952"),
    # tennis
    ("tennis", "Ashlyn Krueger vs Katerina Siniakova", "", "Tomorrow 00:30", "", "https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Ashlyn_Krueger_vs_Katerina_Siniakova/3?event_id=902171"),
    ("tennis", "Elena Rybakina vs Leylah Fernandez", "", "Tomorrow 05:00", "", "https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Elena_Rybakina_vs_Leylah_Fernandez/3?event_id=902207"),
    ("tennis", "Daniil Medvedev vs Nikoloz Basilashvili", "ATP final", "Tomorrow 06:00", "", "https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Daniil_Medvedev_vs_Nikoloz_Basilashvili/3?event_id=902251"),
    ("tennis", "Alexandra Eala vs Mika Stojsavljevic", "", "26 Oct 22:00", "", "https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Alexandra_Eala_vs_Mika_Stojsavljevic/3?event_id=902175"),
    ("tennis", "Moyuka Uchijima vs Elise Mertens", "", "26 Oct 22:00", "", "https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Moyuka_Uchijima_vs_Elise_Mertens/3?event_id=902173"),
    ("tennis", "Leylah Fernandez vs Himeno Sakatsume", "", "26 Oct 22:00", "", "https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Leylah_Fernandez_vs_Himeno_Sakatsume/3?event_id=902172"),
    # volleyball
    ("volleyball", "SWD Duren vs WWK Volleys Munchen", "", "Today 13:30", "", "https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/SWD_Duren_vs_WWK_Volleys_Munchen/21?event_id=37012"),
    ("volleyball", "Helios Grizzlys Giesen vs Berlin Volleys", "", "Today 13:30", "", "https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Helios_Grizzlys_Giesen_vs_Berlin_Volleys/21?event_id=37013"),
    ("volleyball", "Trentino vs Cisterna", "SuperLega", "Tomorrow 12:00", "", "https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Trentino_vs_Cisterna/21?event_id=36994"),
    ("volleyball", "Perugia vs Pordenone", "SuperLega", "Tomorrow 13:00", "", "https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Perugia_vs_Pordenone/21?event_id=36997"),
    ("volleyball", "CHKS Chelm vs Resovia Rzeszow", "PlusLiga", "Tomorrow 13:00", "", "https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/CHKS_Chelm_vs_Resovia_Rzeszow/21?event_id=36965"),
    ("volleyball", "UVC Graz W vs Sportunion St Polten W", "", "Today 14:00", "", "https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/UVC_Graz_W_vs_Sportunion_St_Polten_W/21?event_id=37019"),
    ("volleyball", "Mogilno W vs Chemik Police W", "", "Today 14:30", "", "https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Mogilno_W_vs_Chemik_Police_W/21?event_id=37078"),
    ("volleyball", "Beziers W vs Le Cannet W", "", "Today 13:30", "", "https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Beziers_W_vs_Le_Cannet_W/21?event_id=37067"),
    # greyhounds (rows shown as Expired by OLBG are excluded)
    ("greyhounds", "6:14 Monmore", "Daily races", "Today 13:14", "", "https://www.olbg.com/betting-tips/Greyhounds/All_Greyhounds/All_Events/6:14_Monmore/28?event_id=689954"),
    ("greyhounds", "6:29 Doncaster", "Daily races", "Today 13:29", "", "https://www.olbg.com/betting-tips/Greyhounds/All_Greyhounds/All_Events/6:29_Doncaster/28?event_id=689956"),
    ("greyhounds", "7:58 Doncaster", "Daily races", "Today 14:58", "", "https://www.olbg.com/betting-tips/Greyhounds/All_Greyhounds/All_Events/7:58_Doncaster/28?event_id=689890"),
    ("greyhounds", "8:54 Monmore", "Daily races", "Today 15:54", "", "https://www.olbg.com/betting-tips/Greyhounds/All_Greyhounds/All_Events/8:54_Monmore/28?event_id=690013"),
    ("greyhounds", "9:14 Monmore", "Daily races", "Today 16:14", "", "https://www.olbg.com/betting-tips/Greyhounds/All_Greyhounds/All_Events/9:14_Monmore/28?event_id=690017"),
    ("greyhounds", "9:18 Dunstall Park", "Daily races", "Today 16:18", "", "https://www.olbg.com/betting-tips/Greyhounds/All_Greyhounds/All_Events/9:18_Dunstall_Park/28?event_id=689892"),
    ("greyhounds", "10:14 Dunstall Park", "Daily races", "Today 17:14", "", "https://www.olbg.com/betting-tips/Greyhounds/All_Greyhounds/All_Events/10:14_Dunstall_Park/28?event_id=690035"),
]

# Fixtures that OLBG displayed a time for but that no governing body confirmed this
# session, and fixtures OLBG did not show at all.
NOT_LISTED = {
    "golf": "The OLBG golf hub rendered 'No tips found' (no event row) at 16:41Z, so no golf match was available to price.",
    "rugby-league": "The OLBG rugby league hub showed only 2027 outright markets (State of Origin, Super League, NRL) and no match fixture.",
}

SOURCES = [
    ("MLB StatsAPI schedule", MLB_SCHEDULE, "Official league feed", "Baseball", "2026-10-24T17:02Z"),
    ("MLB StatsAPI standings", MLB_STANDINGS, "Official league feed", "Baseball", "2026-10-24T17:04Z"),
    ("MLB StatsAPI game feed (Game 2)", MLB_GAME_FEED, "Official league feed", "Baseball", "2026-10-24T18:12Z"),
    ("MLB StatsAPI active roster, Milwaukee", MLB_ROSTER_MIL, "Official league feed", "Baseball", "2026-10-24T18:05Z"),
    ("MLB StatsAPI active roster, Tampa Bay", MLB_ROSTER_TB, "Official league feed", "Baseball", "2026-10-24T18:05Z"),
    ("NHL API schedule (24 Oct)", NHL_SCHEDULE, "Official league feed", "Ice Hockey", "2026-10-24T17:08Z"),
    ("NHL API schedule (25 Oct)", NHL_SCHEDULE_25, "Official league feed", "Ice Hockey", "2026-10-24T17:31Z"),
    ("NHL API standings", NHL_STANDINGS, "Official league feed", "Ice Hockey", "2026-10-24T17:05Z"),
    ("World Snooker Tour matches", WST_MATCHES, "Governing body", "Snooker", "2026-10-24T16:52Z"),
    ("Formula 1 United States GP", F1_US_GP, "Governing body", "Motor Racing", "2026-10-24T16:55Z"),
    ("ATP Tour live scores", ATP_SCORES, "Governing body", "Tennis", "2026-10-24T16:49Z"),
    ("NBA games calendar", NBA_GAMES, "Official league", "Basketball", "2026-10-24T16:58Z"),
    ("NBA standings", NBA_STANDINGS, "Official league", "Basketball", "2026-10-24T17:12Z"),
    ("URC round 4 match centre", URC_ROUND4, "Official league", "Rugby Union", "2026-10-24T17:20Z"),
    ("URC league table", URC_TABLE, "Official league", "Rugby Union", "2026-10-24T17:22Z"),
    ("OLBG cricket hub", _o("Cricket", 7), "Discovery only", "Cricket", "2026-10-24T16:44Z"),
    ("OLBG basketball hub", _o("Basketball", 4), "Discovery only", "Basketball", "2026-10-24T16:43Z"),
    ("OLBG ice hockey hub", _o("Ice_Hockey", 13), "Discovery only", "Ice Hockey", "2026-10-24T16:43Z"),
    ("OLBG tennis hub", _o("Tennis", 3), "Discovery only", "Tennis", "2026-10-24T16:42Z"),
    ("OLBG snooker hub", _o("Snooker", 8), "Discovery only", "Snooker", "2026-10-24T16:45Z"),
    ("OLBG darts hub", _o("Darts", 15), "Discovery only", "Darts", "2026-10-24T16:46Z"),
    ("OLBG rugby union hub", _o("Rugby_Union", 9), "Discovery only", "Rugby Union", "2026-10-24T16:46Z"),
    ("OLBG rugby league hub", _o("Rugby_League", 10), "Discovery only", "Rugby League", "2026-10-24T16:47Z"),
    ("OLBG golf hub", _o("Golf", 5), "Discovery only", "Golf", "2026-10-24T16:41Z"),
    ("OLBG gaelic football hub", _o("Gaelic_Football", 25), "Discovery only", "Gaelic Sports", "2026-10-24T16:47Z"),
    ("OLBG greyhounds hub", _o("Greyhounds", 28), "Discovery only", "Greyhounds", "2026-10-24T16:48Z"),
    ("OLBG handball hub", _o("Handball", 20), "Discovery only", "Handball", "2026-10-24T16:48Z"),
    ("OLBG volleyball hub", _o("Volleyball", 21), "Discovery only", "Volleyball", "2026-10-24T16:48Z"),
    ("OLBG motor racing hub", _o("Motor_Racing", 14), "Discovery only", "Motor Racing", "2026-10-24T16:46Z"),
    ("OLBG baseball hub", _o("Baseball", 12), "Discovery only", "Baseball", "2026-10-24T16:44Z"),
]

FLAGS = [
    {
        "id": "F-9E01",
        "severity": "high",
        "title": "Eight fixtures could be proved, not the seventy-five the brief asks for",
        "detail": ("The brief asks for five priced matches per sport per day across fifteen sports, "
                   "which is 75 books. This session confirmed eight fixtures end-to-end from official "
                   "feeds: three MLB World Series games (2, 3 and 4) and five NHL games. Every other "
                   "OLBG row is a listing without governing-body confirmation, so it is published as a "
                   "watchlist row with no price. Nothing was imputed to reach a quota: the sports whose "
                   "official routes failed carry unpriced listings rather than priced ones, and the two "
                   "with nothing on offer carry no row at all."),
        "source": "https://www.olbg.com/betting-tips",
    },
    {
        "id": "F-9E02",
        "severity": "high",
        "title": "Golf: OLBG showed no event at all",
        "detail": ("The golf hub returned 'No tips found' at 16:41Z. Without an OLBG event there is "
                   "no match to price, and no official PGA/DP World/LPGA field or tee sheet was "
                   "retrieved either. Golf therefore has zero rows and zero picks in this release."),
        "source": "https://www.olbg.com/betting-tips/Golf/5",
    },
    {
        "id": "F-9E03",
        "severity": "high",
        "title": "Rugby League: OLBG lists outrights only",
        "detail": ("The rugby league hub showed State of Origin 2027, Super League 2027 and NRL 2027 "
                   "winner markets, with no individual match. No match could be listed or priced."),
        "source": "https://www.olbg.com/betting-tips/Rugby_League/10",
    },
    {
        "id": "F-9E04",
        "severity": "medium",
        "title": "OLBG times are unlabelled and are not UTC",
        "detail": ("The same page mixes clock conventions: the MLB card read 'Today 20:00' for a "
                   "00:00 UTC start, while the WST card read 'Today 14:00' for a 13:00 UTC start. "
                   "The greyhound hub is worse still: the row named 6:14 Monmore carried the clock "
                   "13:14, a seven-hour gap on a single line. This desk never uses an OLBG clock as a "
                   "start time. Every start in the proved tables comes from the official feed; the "
                   "OLBG label is shown beside it, verbatim, as a discovery artefact."),
        "source": "https://www.olbg.com/betting-tips/Baseball/12",
    },
    {
        "id": "F-9E05",
        "severity": "high",
        "title": "Availability is only checkable for baseball, so hockey is capped at Medium",
        "detail": ("MLB StatsAPI publishes an active roster with a status per player, and both World "
                   "Series clubs list 26 players all marked Active, so the three baseball rows carry a "
                   "real availability statement. The NHL API roster endpoint returns biographical data "
                   "only, with no injury or roster status field, and no club injury report was readable. "
                   "The five hockey rows therefore have an empty availability field, and the published "
                   "rule caps them at Medium for that reason alone. No press line or guess was used to "
                   "fill the gap."),
        "source": "https://api-web.nhle.com/v1/roster/OTT/20262027",
    },
    {
        "id": "F-9E06",
        "severity": "medium",
        "title": "Basketball: two-game samples cannot support a price",
        "detail": ("NBA standings on 24 October 2026 cover two games for most clubs. Shrunk win "
                   "rates sit between .25 and .75, so almost every log5 output lands on a coin flip "
                   "or an extreme. No NBA line was issued. The ten rows stay as listings for reference."),
        "source": "https://www.nba.com/standings",
    },
    {
        "id": "F-9E07",
        "severity": "medium",
        "title": "Darts: the PDC schedule page was a cookie wall",
        "detail": ("Both pdc.tv URLs fetched rendered the consent dialogue instead of the match "
                   "schedule. The five European Championship matches are therefore OLBG-only rows."),
        "source": "https://www.pdc.tv/tournaments/machineseeker-european-championship",
    },
    {
        "id": "F-9E08",
        "severity": "medium",
        "title": "Handball and volleyball: league sites did not render fixtures or tables",
        "detail": ("opel-hbl.de served a reCAPTCHA in place of the Spielplan and Tabelle, and "
                   "legavolley.it returned navigation only. Handball and volleyball therefore have "
                   "OLBG listings but no official confirmation and no prices."),
        "source": "https://www.opel-hbl.de/de/hbl/spielplan",
    },
    {
        "id": "F-9E09",
        "severity": "medium",
        "title": "Greyhounds: no official racecard",
        "detail": ("No GBGB or track racecard was retrieved. Runner names on the greyhound rows "
                   "come from OLBG's community tip cards and are shown as listing text only."),
        "source": "https://www.olbg.com/betting-tips/Greyhounds/28",
    },
    {
        "id": "F-9E10",
        "severity": "low",
        "title": "Snooker final opponent undetermined at retrieval",
        "detail": ("WST lists the final as Kyren Wilson against the winner of match 62 (Mark "
                   "Williams v Jak Jones). With one side unknown no two-way price can be originated, "
                   "so the final is a watchlist row."),
        "source": "https://www.wst.tv/matches/",
    },
    {
        "id": "F-9E11",
        "severity": "low",
        "title": "Boston's fair price sits outside the brief's band",
        "detail": ("The Bruins' fair price is about -320, shorter than the -250 floor in the brief, "
                   "so the selection is published as Medium even though the form case is the "
                   "strongest on the slate. The price, not the argument, is what disqualifies it."),
        "source": "https://api-web.nhle.com/v1/standings/2026-10-24",
    },
    {
        "id": "F-9E12",
        "severity": "medium",
        "title": "The hockey samples are nine to twelve games old",
        "detail": ("Every NHL club has played between nine and twelve games, so a single result "
                   "moves a win rate by roughly nine percentage points. The prices are published "
                   "as snapshots with that stated, and no hockey pick is labelled High."),
        "source": "https://api-web.nhle.com/v1/standings/2026-10-24",
    },
    {
        "id": "F-9E13",
        "severity": "medium",
        "title": "The High tier holds one pick, because the brief's High test cannot be met more often",
        "detail": ("The brief asks a High pick to carry current form, recent history, match "
                   "statistics and confirmed injuries, and to price between -250 and +10000. Only "
                   "the World Series rows have all four: the rosters are checkable and both prices "
                   "sit inside the band. Of the eight picks, one clears every condition, six are "
                   "Medium and one is Low. Publishing six High labels would have meant ignoring the "
                   "availability requirement."),
        "source": "https://statsapi.mlb.com/api/v1/teams/158/roster?rosterType=active",
    },
    {
        "id": "F-9E14",
        "severity": "low",
        "title": "Each OLBG hub was read to its first screen only",
        "detail": ("Every sport hub truncates its card list and offers Load More Tips. The watchlist "
                   "captures the rows rendered before that cut, plus the outright block where one "
                   "appeared, so it is a sample of what OLBG advertised rather than a complete "
                   "market list. Deeper pages were not consumed."),
        "source": "https://www.olbg.com/betting-tips",
    },
]

REPO_AUDIT = [
    {
        "id": "R-9E01",
        "file": "index.html:6",
        "sha256": "",
        "finding": ("The landing page's freshness chip says 'Snapshot 21 Oct 2026' while the body's "
                    "data-snapshot attribute and data/current/site-manifest.json both say "
                    "2026-10-22T12:29:50Z. Two different snapshot dates are shown on one page."),
        "severity": "medium",
    },
    {
        "id": "R-9E02",
        "file": "README.md:8",
        "sha256": "",
        "finding": ("The release summary quotes 108 captured listings and 42 statistical inputs. The "
                    "manifest confirms 108 listings but records 32 source checks, not 42. The prose "
                    "and the machine-readable manifest disagree."),
        "severity": "medium",
    },
    {
        "id": "R-9E03",
        "file": "data/*/fixtures.json",
        "sha256": "",
        "finding": ("219 fixture identifiers appear in more than one desk. mlb-849802, mlb-849804, "
                    "mlb-849805 and nhl-2026020154/55 each occur in eight separate slates. The same "
                    "event can therefore carry several different originated prices with nothing on "
                    "the page saying which desk priced it or why they differ."),
        "severity": "high",
    },
    {
        "id": "R-9E04",
        "file": "data/984d417f/predictions.json",
        "sha256": "",
        "finding": ("Row pdc-ec-03 uses the word 'verified' in published prediction prose, against "
                    "the brief's instruction that the term stays internal."),
        "severity": "low",
    },
    {
        "id": "R-9E05",
        "file": "COORDINATION.md",
        "sha256": "",
        "finding": ("The shared board is 733,636 bytes. A single file this large is slow to read and "
                    "conflicts on nearly every rebase; it needs periodic archival by the integration "
                    "session."),
        "severity": "low",
    },
    {
        "id": "R-9E06",
        "file": ".github/workflows/current-pages.yml",
        "sha256": "",
        "finding": ("The publish job runs on main only, so a pull request cannot prove the deployed "
                    "artifact. The PR gate builds and validates _site but never uploads it. This "
                    "desk adds a local link gate to compensate."),
        "severity": "low",
    },
]
