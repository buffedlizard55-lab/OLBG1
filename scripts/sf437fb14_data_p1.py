"""Session f437fb14 - verified fixture data, part 1 (Baseball, Basketball, Ice Hockey).

Every value in this module was read from the source named in `official_url` during this
session (2026-10-24, UTC). Where a field could not be read, it is None and the fixture is
marked `verify="discovery"` so the build can publish it blank and flag it.

Nothing here is inferred from memory. Times marked `time_source="olbg-et"` are OLBG hub
times shown in US Eastern and converted to UTC by the build; they are NOT official.
"""

READ_AT = "2026-10-24T17:42Z"

# ---------------------------------------------------------------------------
# BASEBALL
# ---------------------------------------------------------------------------
BASEBALL = [
    {
        "id": "BB-01",
        "sport": "Baseball",
        "competition": "MLB World Series, Game 2",
        "home": "Milwaukee Brewers",
        "away": "Tampa Bay Rays",
        "start_utc": "2026-10-25T00:00:00Z",
        "time_source": "official",
        "venue": "American Family Field, Milwaukee",
        "olbg_url": "https://www.olbg.com/betting-tips/Baseball/12",
        "official_url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-10-24&hydrate=probablePitcher,linescore,team",
        "verify": "verified",
        "facts": [
            "MLB Stats API lists the game as World Series Game 2, gamePk 849802, "
            "first pitch 2026-10-25T00:00:00Z at American Family Field.",
            "Series state on the official feed: Milwaukee 1-0, Tampa Bay 0-1.",
            "`ifNecessary` is N, so this is a scheduled game rather than a conditional one.",
            "Probable pitchers: Drew Rasmussen (TB) and Logan Henderson (MIL).",
        ],
        "inputs": {
            "kind": "mlb",
            "home_rs": None, "home_ra": None, "home_w": 1, "home_l": 0,
            "away_rs": 736, "away_ra": 650, "away_w": 98, "away_l": 64,
            "away_road_w": 43, "away_road_l": 38,
            "sp_home": {"name": "Logan Henderson", "ip": 98.1, "era": 2.47, "whip": 0.84,
                        "k": 110, "bb": 19, "gs": 18, "w": 11, "l": 3, "avg": ".183"},
            "sp_away": {"name": "Drew Rasmussen", "ip": 172.0, "era": 2.67, "whip": 0.91,
                        "k": 174, "bb": 32, "gs": 30, "w": 16, "l": 5, "avg": ".199"},
        },
        "extra_sources": [
            "https://statsapi.mlb.com/api/v1/people?personIds=656876,701656&hydrate=stats(group=[pitching],type=[season],season=2026)",
            "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsTypes=regularSeason",
        ],
    }
]

# ---------------------------------------------------------------------------
# BASKETBALL  (records: nba.com/standings ; fixtures: nba.com/games)
# ---------------------------------------------------------------------------
NBA_SRC_STANDINGS = "https://www.nba.com/standings"
NBA_SRC_GAMES = "https://www.nba.com/games"

# w, l, home_w, home_l, road_w, road_l, conf, div, last10, streak  -- all read from
# the 2026-27 regular-season standings table.
NBA_RECORDS = {
    "Atlanta Hawks":      dict(w=2, l=0, hw=0, hl=0, rw=2, rl=0, conf="2-0", div="2-0", l10="2-0", streak="W 2"),
    "Detroit Pistons":    dict(w=2, l=0, hw=1, hl=0, rw=1, rl=0, conf="2-0", div="0-0", l10="2-0", streak="W 2"),
    "Philadelphia 76ers": dict(w=2, l=0, hw=1, hl=0, rw=1, rl=0, conf="2-0", div="1-0", l10="2-0", streak="W 2"),
    "Toronto Raptors":    dict(w=2, l=0, hw=1, hl=0, rw=1, rl=0, conf="2-0", div="0-0", l10="2-0", streak="W 2"),
    "Washington Wizards": dict(w=1, l=1, hw=1, hl=1, rw=0, rl=0, conf="1-1", div="0-0", l10="1-1", streak="L 1"),
    "Boston Celtics":     dict(w=1, l=1, hw=1, hl=0, rw=0, rl=1, conf="1-1", div="1-0", l10="1-1", streak="W 1"),
    "Chicago Bulls":      dict(w=1, l=1, hw=0, hl=0, rw=1, rl=1, conf="1-1", div="1-0", l10="1-1", streak="W 1"),
    "Charlotte Hornets":  dict(w=1, l=1, hw=0, hl=1, rw=1, rl=0, conf="1-1", div="0-1", l10="1-1", streak="L 1"),
    "Indiana Pacers":     dict(w=1, l=1, hw=0, hl=1, rw=1, rl=0, conf="0-0", div="0-0", l10="1-1", streak="L 1"),
    "Brooklyn Nets":      dict(w=0, l=1, hw=0, hl=1, rw=0, rl=0, conf="0-1", div="0-0", l10="0-1", streak="L 1"),
    "Cleveland Cavaliers": dict(w=0, l=1, hw=0, hl=0, rw=0, rl=1, conf="0-1", div="0-0", l10="0-1", streak="L 1"),
    "Orlando Magic":      dict(w=0, l=2, hw=0, hl=2, rw=0, rl=0, conf="0-1", div="0-1", l10="0-2", streak="L 2"),
    "Miami Heat":         dict(w=0, l=2, hw=0, hl=2, rw=0, rl=0, conf="0-1", div="0-0", l10="0-2", streak="L 2"),
    "New York Knicks":    dict(w=0, l=2, hw=0, hl=1, rw=0, rl=1, conf="0-2", div="0-2", l10="0-2", streak="L 2"),
    "Milwaukee Bucks":    dict(w=0, l=2, hw=0, hl=1, rw=0, rl=1, conf="0-2", div="0-1", l10="0-2", streak="L 2"),
    "Los Angeles Lakers": dict(w=2, l=0, hw=2, hl=0, rw=0, rl=0, conf="2-0", div="2-0", l10="2-0", streak="W 2"),
    "Oklahoma City Thunder": dict(w=2, l=0, hw=1, hl=0, rw=1, rl=0, conf="2-0", div="1-0", l10="2-0", streak="W 2"),
    "Houston Rockets":    dict(w=2, l=0, hw=1, hl=0, rw=1, rl=0, conf="2-0", div="2-0", l10="2-0", streak="W 2"),
    "Portland Trail Blazers": dict(w=2, l=0, hw=1, hl=0, rw=1, rl=0, conf="2-0", div="0-0", l10="2-0", streak="W 2"),
    "Memphis Grizzlies":  dict(w=2, l=0, hw=1, hl=0, rw=1, rl=0, conf="2-0", div="0-0", l10="2-0", streak="W 2"),
    "Minnesota Timberwolves": dict(w=2, l=0, hw=0, hl=0, rw=2, rl=0, conf="0-0", div="0-0", l10="2-0", streak="W 2"),
    "LA Clippers":        dict(w=1, l=1, hw=1, hl=0, rw=0, rl=1, conf="1-1", div="1-1", l10="1-1", streak="L 1"),
    "Utah Jazz":          dict(w=1, l=1, hw=1, hl=0, rw=0, rl=1, conf="1-1", div="0-0", l10="1-1", streak="W 1"),
    "Dallas Mavericks":   dict(w=1, l=1, hw=0, hl=0, rw=1, rl=1, conf="0-1", div="0-1", l10="1-1", streak="W 1"),
    "Denver Nuggets":     dict(w=0, l=1, hw=0, hl=0, rw=0, rl=1, conf="0-1", div="0-1", l10="0-1", streak="L 1"),
    "Phoenix Suns":       dict(w=0, l=1, hw=0, hl=0, rw=0, rl=1, conf="0-1", div="0-0", l10="0-1", streak="L 1"),
    "New Orleans Pelicans": dict(w=0, l=2, hw=0, hl=1, rw=0, rl=1, conf="0-1", div="0-0", l10="0-2", streak="L 2"),
    "San Antonio Spurs":  dict(w=0, l=2, hw=0, hl=2, rw=0, rl=0, conf="0-2", div="0-1", l10="0-2", streak="L 2"),
    "Golden State Warriors": dict(w=0, l=2, hw=0, hl=1, rw=0, rl=1, conf="0-2", div="0-1", l10="0-2", streak="L 2"),
}

# Season leaders printed beside each game on nba.com/games (verified, 2026-27 season to date)
NBA_LEADERS = {
    "Miami Heat": [("Giannis Antetokounmpo", "35.5 PPG", "9.0 RPG", "3.0 APG")],
    "Charlotte Hornets": [("Naz Reid", "18.5 PPG", "8.5 RPG", "4.5 APG")],
    "Milwaukee Bucks": [("Tyler Herro", "29.0 PPG", "3.5 RPG", "6.5 APG")],
    "Philadelphia 76ers": [("Tyrese Maxey", "30.0 PPG", "3.5 RPG", "5.5 APG")],
    "Brooklyn Nets": [("Julius Randle", "33.0 PPG", "8.0 RPG", "7.0 APG")],
    "Cleveland Cavaliers": [("Donovan Mitchell", "32.0 PPG", "10.0 RPG", "3.0 APG")],
    "San Antonio Spurs": [("Victor Wembanyama", "18.5 PPG", "13.0 RPG", "2.5 APG")],
    "Dallas Mavericks": [("Cooper Flagg", "23.0 PPG", "5.0 RPG", "4.0 APG")],
    "Washington Wizards": [("Anthony Davis", "21.5 PPG", "10.5 RPG", "2.0 APG")],
    "Chicago Bulls": [("Jalen Smith", "14.5 PPG", "10.5 RPG", "1.0 APG")],
    "Houston Rockets": [("Alperen Sengun", "26.0 PPG", "8.5 RPG", "6.0 APG")],
    "Atlanta Hawks": [("Jalen Johnson", "19.5 PPG", "10.5 RPG", "7.0 APG")],
}

# ET -> UTC conversion for 24 October 2026 (EDT, UTC-4).
BASKETBALL = [
    dict(id="BK-01", sport="Basketball", competition="NBA", away="Miami Heat", home="Charlotte Hornets",
         start_utc="2026-10-24T22:00:00Z", time_source="official", et="6:00 PM ET",
         game_id="0022600104", official_url=NBA_SRC_GAMES, secondary_url=NBA_SRC_STANDINGS,
         olbg_url="https://www.olbg.com/betting-tips/Basketball/4", verify="verified"),
    dict(id="BK-02", sport="Basketball", competition="NBA", away="Milwaukee Bucks", home="Philadelphia 76ers",
         start_utc="2026-10-24T23:30:00Z", time_source="official", et="7:30 PM ET",
         game_id="0022600106", official_url=NBA_SRC_GAMES, secondary_url=NBA_SRC_STANDINGS,
         olbg_url="https://www.olbg.com/betting-tips/Basketball/4", verify="verified"),
    dict(id="BK-03", sport="Basketball", competition="NBA", away="Brooklyn Nets", home="Cleveland Cavaliers",
         start_utc="2026-10-24T23:30:00Z", time_source="official", et="7:30 PM ET",
         game_id="0022600105", official_url=NBA_SRC_GAMES, secondary_url=NBA_SRC_STANDINGS,
         olbg_url="https://www.olbg.com/betting-tips/Basketball/4", verify="verified"),
    dict(id="BK-04", sport="Basketball", competition="NBA", away="San Antonio Spurs", home="Dallas Mavericks",
         start_utc="2026-10-25T00:00:00Z", time_source="official", et="8:00 PM ET",
         game_id="0022600109", official_url=NBA_SRC_GAMES, secondary_url=NBA_SRC_STANDINGS,
         olbg_url="https://www.olbg.com/betting-tips/Basketball/4", verify="verified"),
    dict(id="BK-05", sport="Basketball", competition="NBA", away="Washington Wizards", home="Chicago Bulls",
         start_utc="2026-10-25T00:00:00Z", time_source="official", et="8:00 PM ET",
         game_id="0022600108", official_url=NBA_SRC_GAMES, secondary_url=NBA_SRC_STANDINGS,
         olbg_url="https://www.olbg.com/betting-tips/Basketball/4", verify="verified"),
    dict(id="BK-06", sport="Basketball", competition="NBA", away="Houston Rockets", home="Atlanta Hawks",
         start_utc="2026-10-25T00:30:00Z", time_source="official", et="8:30 PM ET",
         game_id="0022600107", official_url=NBA_SRC_GAMES, secondary_url=NBA_SRC_STANDINGS,
         olbg_url="https://www.olbg.com/betting-tips/Basketball/4", verify="verified"),
    dict(id="BK-07", sport="Basketball", competition="NBA", away="New Orleans Pelicans", home="Denver Nuggets",
         start_utc="2026-10-25T02:00:00Z", time_source="olbg-et", et="10:00 PM ET",
         game_id=None, official_url=NBA_SRC_GAMES, secondary_url=NBA_SRC_STANDINGS,
         olbg_url="https://www.olbg.com/betting-tips/Basketball/4", verify="partial"),
    dict(id="BK-08", sport="Basketball", competition="NBA", away="Golden State Warriors", home="Phoenix Suns",
         start_utc="2026-10-25T03:00:00Z", time_source="olbg-et", et="11:00 PM ET",
         game_id=None, official_url=NBA_SRC_GAMES, secondary_url=NBA_SRC_STANDINGS,
         olbg_url="https://www.olbg.com/betting-tips/Basketball/4", verify="partial"),
]

# ---------------------------------------------------------------------------
# ICE HOCKEY
# ---------------------------------------------------------------------------
NHL_SCHED = "https://api-web.nhle.com/v1/schedule/2026-10-24"
NHL_STAND = "https://api-web.nhle.com/v1/standings/2026-10-24"

# Club lines actually read out of the official standings payload this session.
# Only four clubs fell inside the returned slice; the rest are left blank, not guessed.
NHL_READ = {
    "CAR": dict(name="Carolina Hurricanes", gp=12, w=8, l=2, otl=2, pts=18, gf=47, ga=33, gd=14, l10="8-1-1", streak="OT 1"),
    "EDM": dict(name="Edmonton Oilers", gp=10, w=8, l=1, otl=1, pts=17, gf=47, ga=32, gd=15, l10="8-1-1", streak="W 3"),
    "BOS": dict(name="Boston Bruins", gp=11, w=8, l=2, otl=1, pts=17, gf=42, ga=22, gd=20, l10="7-2-1", streak="W 1"),
    "VGK": dict(name="Vegas Golden Knights", gp=12, w=8, l=4, otl=0, pts=16, gf=46, ga=36, gd=10, l10="7-3-0", streak="L 2"),
}

# Licensed market prices published inside the official NHL schedule feed (decimal +
# American, providers 3/6/7/8/9/10). These are the league's own published quotes and are
# reproduced as a market reference only - they are NOT our originated line.
HOCKEY = [
    dict(id="IH-01", sport="Ice Hockey", competition="NHL", away="Anaheim Ducks", home="Philadelphia Flyers",
         start_utc="2026-10-24T17:00:00Z", venue="Xfinity Mobile Arena", state="LIVE (in progress at read time)",
         official_url=NHL_SCHED, olbg_url="https://www.olbg.com/betting-tips/Ice_Hockey/13", verify="verified",
         market=None, time_source="official"),
    dict(id="IH-02", sport="Ice Hockey", competition="NHL", away="Los Angeles Kings", home="New Jersey Devils",
         start_utc="2026-10-24T19:30:00Z", venue="Prudential Center", state="FUT",
         official_url=NHL_SCHED, olbg_url="https://www.olbg.com/betting-tips/Ice_Hockey/13", verify="verified",
         market=dict(away=["2.55", "2.54", "+162", "+159", "+160", "3.50"],
                     home=["1.52", "1.52", "-194", "-198", "-192", "1.90"]),
         time_source="official"),
    dict(id="IH-03", sport="Ice Hockey", competition="NHL", away="San Jose Sharks", home="Boston Bruins",
         start_utc="2026-10-24T23:00:00Z", venue="TD Garden", state="FUT",
         official_url=NHL_SCHED, olbg_url="https://www.olbg.com/betting-tips/Ice_Hockey/13", verify="verified",
         market=dict(away=["2.54", "2.44", "+160", "+152", "+156", "3.40"],
                     home=["1.53", "1.55", "-192", "-184", "-193", "1.90"]),
         time_source="official"),
    dict(id="IH-04", sport="Ice Hockey", competition="NHL", away="New York Rangers", home="Ottawa Senators",
         start_utc="2026-10-24T23:00:00Z", venue="Canadian Tire Centre", state="FUT",
         official_url=NHL_SCHED, olbg_url="https://www.olbg.com/betting-tips/Ice_Hockey/13", verify="verified",
         market=dict(away=["2.05", "1.87", "+105", "+106", "+105", "2.70"],
                     home=["1.90", "1.90", "-110", "-112", "-110", "1.90"]),
         time_source="official"),
    dict(id="IH-05", sport="Ice Hockey", competition="NHL", away="Carolina Hurricanes", home="St. Louis Blues",
         start_utc="2026-10-24T23:07:00Z", venue=None, state=None,
         official_url=NHL_SCHED, olbg_url="https://www.olbg.com/betting-tips/Ice_Hockey/13", verify="partial",
         market=None, time_source="olbg-et"),
    dict(id="IH-06", sport="Ice Hockey", competition="NHL", away="Minnesota Wild", home="Seattle Kraken",
         start_utc="2026-10-25T03:07:00Z", venue=None, state=None,
         official_url=NHL_SCHED, olbg_url="https://www.olbg.com/betting-tips/Ice_Hockey/13", verify="partial",
         market=None, time_source="olbg-et"),
    dict(id="IH-07", sport="Ice Hockey", competition="NHL", away="Toronto Maple Leafs", home="Edmonton Oilers",
         start_utc="2026-10-24T23:07:00Z", venue=None, state=None,
         official_url=NHL_SCHED, olbg_url="https://www.olbg.com/betting-tips/Ice_Hockey/13", verify="partial",
         market=None, time_source="olbg-et"),
    dict(id="IH-08", sport="Ice Hockey", competition="NHL", away="Tampa Bay Lightning", home="Utah Mammoth",
         start_utc="2026-10-25T02:07:00Z", venue=None, state=None,
         official_url=NHL_SCHED, olbg_url="https://www.olbg.com/betting-tips/Ice_Hockey/13", verify="partial",
         market=None, time_source="olbg-et"),
    dict(id="IH-09", sport="Ice Hockey", competition="NHL", away="Detroit Red Wings", home="Calgary Flames",
         start_utc="2026-10-25T03:07:00Z", venue=None, state=None,
         official_url=NHL_SCHED, olbg_url="https://www.olbg.com/betting-tips/Ice_Hockey/13", verify="partial",
         market=None, time_source="olbg-et"),
    dict(id="IH-10", sport="Ice Hockey", competition="NHL", away="Buffalo Sabres", home="Washington Capitals",
         start_utc="2026-10-24T23:07:00Z", venue=None, state=None,
         official_url=NHL_SCHED, olbg_url="https://www.olbg.com/betting-tips/Ice_Hockey/13", verify="partial",
         market=None, time_source="olbg-et"),
    dict(id="IH-11", sport="Ice Hockey", competition="NHL", away="Nashville Predators", home="Pittsburgh Penguins",
         start_utc="2026-10-24T23:07:00Z", venue=None, state=None,
         official_url=NHL_SCHED, olbg_url="https://www.olbg.com/betting-tips/Ice_Hockey/13", verify="partial",
         market=None, time_source="olbg-et"),
    dict(id="IH-12", sport="Ice Hockey", competition="NHL", away="Vegas Golden Knights", home="Columbus Blue Jackets",
         start_utc="2026-10-24T23:07:00Z", venue=None, state=None,
         official_url=NHL_SCHED, olbg_url="https://www.olbg.com/betting-tips/Ice_Hockey/13", verify="partial",
         market=None, time_source="olbg-et"),
]
