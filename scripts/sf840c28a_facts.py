"""Session f840c28a-olbg1 -- captured fact base for the 24-25 October 2026 desk.

Every value in this module was read from the URL recorded beside it during this
session. Nothing here is carried over from another desk, remembered, or
interpolated. Where a field was not read it is absent from the record and the
row is blank in the published table.

Reads were performed with the Arena retrieval layer on 2026-10-24 between
22:25Z and 22:55Z; each source carries its own ``read_utc`` stamp.
"""

from __future__ import annotations

CAPTURE_UTC = "2026-10-24T22:55:00Z"

# --------------------------------------------------------------------------
# Sources. ``tier`` is "official" (league, governing body, tour, club) or
# "discovery" (OLBG -- used only to find out which markets exist).
# --------------------------------------------------------------------------

SOURCES = [
    # --- discovery layer -------------------------------------------------
    dict(id="olbg-tennis", tier="discovery", publisher="OLBG",
         title="Tennis betting tips hub (sport 3)",
         url="https://www.olbg.com/betting-tips/Tennis/3", read_utc="2026-10-24T22:26Z"),
    dict(id="olbg-icehockey", tier="discovery", publisher="OLBG",
         title="Ice Hockey betting tips hub (sport 13)",
         url="https://www.olbg.com/betting-tips/Ice_Hockey/13", read_utc="2026-10-24T22:26Z"),
    dict(id="olbg-basketball", tier="discovery", publisher="OLBG",
         title="Basketball betting tips hub (sport 4)",
         url="https://www.olbg.com/betting-tips/Basketball/4", read_utc="2026-10-24T22:28Z"),
    dict(id="olbg-baseball", tier="discovery", publisher="OLBG",
         title="Baseball betting tips hub (sport 12)",
         url="https://www.olbg.com/betting-tips/Baseball/12", read_utc="2026-10-24T22:28Z"),
    dict(id="olbg-snooker", tier="discovery", publisher="OLBG",
         title="Snooker betting tips hub (sport 8) -- rendered 'No tips found.'",
         url="https://www.olbg.com/betting-tips/Snooker/8", read_utc="2026-10-24T22:30Z"),
    dict(id="olbg-snooker-events", tier="discovery", publisher="OLBG",
         title="Snooker All Events sub-route -- also 'No tips found.'",
         url="https://www.olbg.com/betting-tips/Snooker/All_Snooker/All_Events/8",
         read_utc="2026-10-24T22:31Z"),
    dict(id="olbg-darts", tier="discovery", publisher="OLBG",
         title="Darts betting tips hub (sport 15)",
         url="https://www.olbg.com/betting-tips/Darts/15", read_utc="2026-10-24T22:30Z"),
    dict(id="olbg-cricket", tier="discovery", publisher="OLBG",
         title="Cricket betting tips hub (sport 7)",
         url="https://www.olbg.com/betting-tips/Cricket/7", read_utc="2026-10-24T22:31Z"),
    dict(id="olbg-golf", tier="discovery", publisher="OLBG",
         title="Golf betting tips hub (sport 5) -- rendered 'No tips found.'",
         url="https://www.olbg.com/betting-tips/Golf/5", read_utc="2026-10-24T22:33Z"),
    dict(id="olbg-volleyball", tier="discovery", publisher="OLBG",
         title="Volleyball betting tips hub (sport 21)",
         url="https://www.olbg.com/betting-tips/Volleyball/21", read_utc="2026-10-24T22:33Z"),
    dict(id="olbg-rugbyunion", tier="discovery", publisher="OLBG",
         title="Rugby Union betting tips hub (sport 9)",
         url="https://www.olbg.com/betting-tips/Rugby_Union/9", read_utc="2026-10-24T22:34Z"),
    dict(id="olbg-rugbyleague", tier="discovery", publisher="OLBG",
         title="Rugby League betting tips hub (sport 10) -- outright markets only",
         url="https://www.olbg.com/betting-tips/Rugby_League/10", read_utc="2026-10-24T22:34Z"),
    dict(id="olbg-handball", tier="discovery", publisher="OLBG",
         title="Handball betting tips hub (sport 20)",
         url="https://www.olbg.com/betting-tips/Handball/20", read_utc="2026-10-24T22:36Z"),
    dict(id="olbg-motorracing", tier="discovery", publisher="OLBG",
         title="Motor Racing betting tips hub (sport 14) -- rendered 'No tips found.'",
         url="https://www.olbg.com/betting-tips/Motor_Racing/14", read_utc="2026-10-24T22:36Z"),
    dict(id="olbg-gaelic", tier="discovery", publisher="OLBG",
         title="Gaelic Football betting tips hub (sport 25)",
         url="https://www.olbg.com/betting-tips/Gaelic_Football/25", read_utc="2026-10-24T22:38Z"),
    dict(id="olbg-greyhounds", tier="discovery", publisher="OLBG",
         title="Greyhounds betting tips hub (sport 28) -- a single race listed",
         url="https://www.olbg.com/betting-tips/Greyhounds/28", read_utc="2026-10-24T22:38Z"),

    # --- official layer --------------------------------------------------
    dict(id="nhl-team-summary", tier="official", publisher="NHL",
         title="NHL team summary, season 20262027, game type 2 (all 32 clubs, games played > 0)",
         url=("https://api.nhle.com/stats/rest/en/team/summary?cayenneExp="
              "seasonId%3D20262027%20and%20gameTypeId%3D2%20and%20gamesPlayed%3E0"),
         read_utc="2026-10-24T22:41Z"),
    dict(id="nhl-schedule", tier="official", publisher="NHL",
         title="NHL schedule for 2026-10-24 (12 games, start times, venues, publisher moneyline)",
         url="https://api-web.nhle.com/v1/schedule/2026-10-24", read_utc="2026-10-24T22:59Z"),
    dict(id="nhl-standings", tier="official", publisher="NHL",
         title="NHL standings for 2026-10-24 (standingsDateTimeUtc 2026-10-24T22:25:30Z)",
         url="https://api-web.nhle.com/v1/standings/2026-10-24", read_utc="2026-10-24T22:41Z"),
    dict(id="mlb-schedule", tier="official", publisher="MLB",
         title="MLB schedule 2026-10-24 with probable pitchers (World Series Game 2)",
         url=("https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-10-24"
              "&hydrate=probablePitcher,linescore,team"),
         read_utc="2026-10-24T22:42Z"),
    dict(id="nba-injury", tier="official", publisher="NBA",
         title="NBA injury report, 10/24/26 01:00 PM ET filing",
         url="https://ak-static.cms.nba.com/referee/injury/Injury-Report_2026-10-24_01_00PM.pdf",
         read_utc="2026-10-24T22:43Z"),
    dict(id="nba-standings", tier="official", publisher="NBA",
         title="NBA 2026-27 regular season standings (conference view)",
         url="https://www.nba.com/standings?Season=2026-27&GroupBy=conf",
         read_utc="2026-10-24T22:50Z"),
    dict(id="csa-upcoming", tier="official", publisher="Cricket South Africa",
         title="CSA fixtures & schedules, upcoming",
         url="https://cricket.co.za/upcoming/", read_utc="2026-10-24T22:46Z"),
    dict(id="csa-home", tier="official", publisher="Cricket South Africa",
         title="CSA home page 'Up Next' fixture strip",
         url="https://cricket.co.za/fixtures/", read_utc="2026-10-24T22:45Z"),
]

SOURCES_BY_ID = {s["id"]: s for s in SOURCES}


# --------------------------------------------------------------------------
# Sports and what OLBG actually served for each one.
# --------------------------------------------------------------------------

SPORTS = [
    dict(code="ice-hockey", name="Ice Hockey", olbg_id=13,
         olbg_url="https://www.olbg.com/betting-tips/Ice_Hockey/13",
         olbg_state="listed", olbg_events=11,
         official_name="National Hockey League", official_url="https://api-web.nhle.com/v1/standings/2026-10-24"),
    dict(code="basketball", name="Basketball", olbg_id=4,
         olbg_url="https://www.olbg.com/betting-tips/Basketball/4",
         olbg_state="listed", olbg_events=10,
         official_name="NBA", official_url="https://www.nba.com/standings?Season=2026-27&GroupBy=conf"),
    dict(code="baseball", name="Baseball", olbg_id=12,
         olbg_url="https://www.olbg.com/betting-tips/Baseball/12",
         olbg_state="listed", olbg_events=1,
         official_name="Major League Baseball", official_url="https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-10-24"),
    dict(code="cricket", name="Cricket", olbg_id=7,
         olbg_url="https://www.olbg.com/betting-tips/Cricket/7",
         olbg_state="listed", olbg_events=9,
         official_name="Cricket South Africa", official_url="https://cricket.co.za/upcoming/"),
    dict(code="volleyball", name="Volleyball", olbg_id=21,
         olbg_url="https://www.olbg.com/betting-tips/Volleyball/21",
         olbg_state="listed", olbg_events=16,
         official_name="Lega Pallavolo Serie A", official_url="https://www.legavolley.it/classifica/?IdCampionato=999"),
    dict(code="handball", name="Handball", olbg_id=20,
         olbg_url="https://www.olbg.com/betting-tips/Handball/20",
         olbg_state="listed", olbg_events=16,
         official_name="Handball-Bundesliga", official_url="https://www.daikin-hbl.de/de/hbl/tabelle"),
    dict(code="tennis", name="Tennis", olbg_id=3,
         olbg_url="https://www.olbg.com/betting-tips/Tennis/3",
         olbg_state="listed", olbg_events=15,
         official_name="ATP Tour / WTA", official_url="https://www.atptour.com/"),
    dict(code="rugby-union", name="Rugby Union", olbg_id=9,
         olbg_url="https://www.olbg.com/betting-tips/Rugby_Union/9",
         olbg_state="listed", olbg_events=3,
         official_name="Premiership Rugby / LNR", official_url="https://www.premrugby.com/fixtures-results"),
    dict(code="gaelic-sports", name="Gaelic Sports", olbg_id=25,
         olbg_url="https://www.olbg.com/betting-tips/Gaelic_Football/25",
         olbg_state="listed", olbg_events=4,
         official_name="GAA", official_url="https://www.gaa.ie/"),
    dict(code="darts", name="Darts", olbg_id=15,
         olbg_url="https://www.olbg.com/betting-tips/Darts/15",
         olbg_state="listed", olbg_events=4,
         official_name="PDC", official_url="https://www.pdc.tv/"),
    dict(code="greyhounds", name="Greyhounds", olbg_id=28,
         olbg_url="https://www.olbg.com/betting-tips/Greyhounds/28",
         olbg_state="thin", olbg_events=1,
         official_name="Greyhound Board of Great Britain", official_url="https://www.gbgb.org.uk/"),
    dict(code="snooker", name="Snooker", olbg_id=8,
         olbg_url="https://www.olbg.com/betting-tips/Snooker/8",
         olbg_state="no-tips", olbg_events=0,
         official_name="World Snooker Tour", official_url="https://www.wst.tv/"),
    dict(code="golf", name="Golf", olbg_id=5,
         olbg_url="https://www.olbg.com/betting-tips/Golf/5",
         olbg_state="no-tips", olbg_events=0,
         official_name="PGA Tour / DP World Tour", official_url="https://www.pgatour.com/"),
    dict(code="motor-racing", name="Motor Racing", olbg_id=14,
         olbg_url="https://www.olbg.com/betting-tips/Motor_Racing/14",
         olbg_state="no-tips", olbg_events=0,
         official_name="Formula 1", official_url="https://www.formula1.com/"),
    dict(code="rugby-league", name="Rugby League", olbg_id=10,
         olbg_url="https://www.olbg.com/betting-tips/Rugby_League/10",
         olbg_state="outright-only", olbg_events=0,
         official_name="NRL / Super League", official_url="https://www.nrl.com/"),
]


# --------------------------------------------------------------------------
# NHL club records, read from the NHL team-summary endpoint (nhl-team-summary).
# Keyed by the abbreviation the NHL publishes.
# --------------------------------------------------------------------------

NHL_TEAMS = {
    #        GP  W  L  OTL PTS  GF/G    GA/G    PP%     PK%
    "CAR": dict(gp=12, w=8, l=2, otl=2, pts=18, gf=3.91666, ga=2.41666, pp=0.239130, pk=0.833334),
    "EDM": dict(gp=10, w=8, l=1, otl=1, pts=17, gf=4.60000, ga=3.20000, pp=0.352941, pk=0.724138),
    "BOS": dict(gp=11, w=8, l=2, otl=1, pts=17, gf=3.81818, ga=2.00000, pp=0.225806, pk=0.805556),
    "VGK": dict(gp=12, w=8, l=4, otl=0, pts=16, gf=3.75000, ga=3.00000, pp=0.250000, pk=0.678572),
    "SEA": dict(gp=11, w=7, l=3, otl=1, pts=15, gf=3.81818, ga=3.36363, pp=0.250000, pk=0.687500),
    "NYR": dict(gp=12, w=7, l=4, otl=1, pts=15, gf=3.08333, ga=2.41666, pp=0.200000, pk=0.916667),
    "TOR": dict(gp=12, w=6, l=4, otl=2, pts=14, gf=3.58333, ga=3.16666, pp=0.285714, pk=0.974359),
    "OTT": dict(gp=11, w=7, l=4, otl=0, pts=14, gf=2.63636, ga=2.72727, pp=0.122448, pk=0.780488),
    "TBL": dict(gp=10, w=7, l=3, otl=0, pts=14, gf=3.40000, ga=2.90000, pp=0.135135, pk=0.777778),
    "UTA": dict(gp=11, w=7, l=4, otl=0, pts=14, gf=3.72727, ga=3.27272, pp=0.384615, pk=0.666667),
    "MIN": dict(gp=11, w=6, l=3, otl=2, pts=14, gf=2.90909, ga=2.45454, pp=0.257142, pk=0.783784),
    "COL": dict(gp=11, w=6, l=4, otl=1, pts=13, gf=4.27272, ga=3.00000, pp=0.200000, pk=0.827587),
    "DAL": dict(gp=10, w=6, l=3, otl=1, pts=13, gf=2.50000, ga=1.60000, pp=0.160000, pk=0.916667),
    "SJS": dict(gp=11, w=6, l=4, otl=1, pts=13, gf=2.90909, ga=3.27272, pp=0.257142, pk=0.805556),
    "NJD": dict(gp=10, w=6, l=4, otl=0, pts=12, gf=3.30000, ga=3.10000, pp=0.218750, pk=0.720000),
    "NYI": dict(gp=10, w=5, l=3, otl=2, pts=12, gf=2.90000, ga=2.20000, pp=0.200000, pk=0.882353),
    "MTL": dict(gp=10, w=5, l=3, otl=2, pts=12, gf=3.20000, ga=3.50000, pp=0.125000, pk=0.809524),
    "FLA": dict(gp=11, w=5, l=4, otl=2, pts=12, gf=2.81818, ga=3.09090, pp=0.192307, pk=0.826087),
    "STL": dict(gp=10, w=5, l=4, otl=1, pts=11, gf=3.50000, ga=3.10000, pp=0.250000, pk=0.857143),
    "WPG": dict(gp=10, w=4, l=3, otl=3, pts=11, gf=2.60000, ga=2.90000, pp=0.222222, pk=0.807693),
    "ANA": dict(gp=11, w=5, l=6, otl=0, pts=10, gf=2.90909, ga=3.36363, pp=0.222222, pk=0.761905),
    "BUF": dict(gp=10, w=4, l=4, otl=2, pts=10, gf=2.80000, ga=3.60000, pp=0.111111, pk=0.666667),
    "WSH": dict(gp=9, w=5, l=4, otl=0, pts=10, gf=3.33333, ga=3.22222, pp=0.200000, pk=0.800000),
    "PHI": dict(gp=13, w=3, l=7, otl=3, pts=9, gf=1.84615, ga=3.15384, pp=0.162790, pk=0.826087),
    "PIT": dict(gp=11, w=4, l=6, otl=1, pts=9, gf=3.27272, ga=3.36363, pp=0.212121, pk=0.833334),
    "NSH": dict(gp=9, w=3, l=3, otl=3, pts=9, gf=2.55555, ga=3.11111, pp=0.285714, pk=0.833334),
    "CBJ": dict(gp=8, w=3, l=5, otl=0, pts=6, gf=2.37500, ga=3.62500, pp=0.086956, pk=0.700000),
    "CHI": dict(gp=10, w=3, l=7, otl=0, pts=6, gf=2.20000, ga=4.00000, pp=0.103448, pk=0.766667),
    "CGY": dict(gp=9, w=3, l=6, otl=0, pts=6, gf=2.11111, ga=4.22222, pp=0.260869, pk=0.838710),
    "LAK": dict(gp=8, w=2, l=4, otl=2, pts=6, gf=2.50000, ga=3.62500, pp=0.160000, pk=0.629630),
    "VAN": dict(gp=12, w=2, l=9, otl=1, pts=5, gf=2.91666, ga=4.66666, pp=0.222222, pk=0.650000),
    # Detroit: goals for/against were not visible in the returned page slice, so
    # they are deliberately absent rather than estimated.
    "DET": dict(gp=11, w=4, l=4, otl=3, pts=11, gf=None, ga=None, pp=0.222222, pk=0.694445),
}

NHL_TEAM_NAMES = {
    "ANA": "Anaheim Ducks", "BOS": "Boston Bruins", "BUF": "Buffalo Sabres",
    "CAR": "Carolina Hurricanes", "CBJ": "Columbus Blue Jackets", "CGY": "Calgary Flames",
    "CHI": "Chicago Blackhawks", "COL": "Colorado Avalanche", "DAL": "Dallas Stars",
    "DET": "Detroit Red Wings", "EDM": "Edmonton Oilers", "FLA": "Florida Panthers",
    "LAK": "Los Angeles Kings", "MIN": "Minnesota Wild", "MTL": "Montreal Canadiens",
    "NJD": "New Jersey Devils", "NSH": "Nashville Predators", "NYI": "New York Islanders",
    "NYR": "New York Rangers", "OTT": "Ottawa Senators", "PHI": "Philadelphia Flyers",
    "PIT": "Pittsburgh Penguins", "SEA": "Seattle Kraken", "SJS": "San Jose Sharks",
    "STL": "St. Louis Blues", "TBL": "Tampa Bay Lightning", "TOR": "Toronto Maple Leafs",
    "UTA": "Utah Mammoth", "VAN": "Vancouver Canucks", "VGK": "Vegas Golden Knights",
    "WPG": "Winnipeg Jets", "WSH": "Washington Capitals",
}

# --------------------------------------------------------------------------
# NHL fixtures. Times are the clock OLBG printed (US Eastern) converted to UTC
# by adding four hours; OLBG prints no timezone, which is recorded as a flag.
# --------------------------------------------------------------------------

NHL_GAMES = [
    dict(away="TOR", home="EDM", olbg_time="Today 19:07", start_utc="2026-10-24T23:07Z"),
    dict(away="SJS", home="BOS", olbg_time="Today 19:07", start_utc="2026-10-24T23:07Z"),
    dict(away="CAR", home="STL", olbg_time="Today 19:07", start_utc="2026-10-24T23:07Z"),
    dict(away="VGK", home="CBJ", olbg_time="Today 19:07", start_utc="2026-10-24T23:07Z"),
    dict(away="NYR", home="OTT", olbg_time="Today 19:07", start_utc="2026-10-24T23:07Z"),
    dict(away="BUF", home="WSH", olbg_time="Today 19:07", start_utc="2026-10-24T23:07Z"),
    dict(away="NSH", home="PIT", olbg_time="Today 19:07", start_utc="2026-10-24T23:07Z"),
    dict(away="TBL", home="UTA", olbg_time="Today 22:07", start_utc="2026-10-25T02:07Z"),
    dict(away="MIN", home="SEA", olbg_time="Today 23:07", start_utc="2026-10-25T03:07Z"),
    dict(away="DET", home="CGY", olbg_time="Today 23:07", start_utc="2026-10-25T03:07Z"),
    dict(away="MTL", home="WPG", olbg_time="Tomorrow 19:07", start_utc="2026-10-25T23:07Z"),
]

# --------------------------------------------------------------------------
# NBA. Records from the official standings; availability from the official
# injury report (13:00 ET filing on 24 October 2026).
# --------------------------------------------------------------------------

NBA_RECORDS = {
    "ATL": (2, 0), "DET": (2, 0), "PHI": (2, 0), "TOR": (2, 0),
    "WAS": (1, 1), "BOS": (1, 1), "CHI": (1, 1), "CHA": (1, 1), "IND": (1, 1),
    "BKN": (0, 1), "CLE": (0, 1),
    "ORL": (0, 2), "MIA": (0, 2), "NYK": (0, 2), "MIL": (0, 2),
    "LAL": (2, 0), "OKC": (2, 0), "HOU": (2, 0), "POR": (2, 0), "MEM": (2, 0), "MIN": (2, 0),
    "LAC": (1, 1), "UTA": (1, 1), "DAL": (1, 1),
    "DEN": (0, 1), "PHX": (0, 1),
    "NOP": (0, 2), "SAS": (0, 2), "GSW": (0, 2),
}

NBA_TEAM_NAMES = {
    "ATL": "Atlanta Hawks", "BKN": "Brooklyn Nets", "BOS": "Boston Celtics",
    "CHA": "Charlotte Hornets", "CHI": "Chicago Bulls", "CLE": "Cleveland Cavaliers",
    "DAL": "Dallas Mavericks", "DEN": "Denver Nuggets", "DET": "Detroit Pistons",
    "GSW": "Golden State Warriors", "HOU": "Houston Rockets", "IND": "Indiana Pacers",
    "LAC": "LA Clippers", "LAL": "Los Angeles Lakers", "MEM": "Memphis Grizzlies",
    "MIA": "Miami Heat", "MIL": "Milwaukee Bucks", "MIN": "Minnesota Timberwolves",
    "NOP": "New Orleans Pelicans", "NYK": "New York Knicks", "OKC": "Oklahoma City Thunder",
    "ORL": "Orlando Magic", "PHI": "Philadelphia 76ers", "PHX": "Phoenix Suns",
    "POR": "Portland Trail Blazers", "SAC": "Sacramento Kings", "SAS": "San Antonio Spurs",
    "TOR": "Toronto Raptors", "UTA": "Utah Jazz", "WAS": "Washington Wizards",
}

NBA_GAMES = [
    dict(away="MIA", home="CHA", et="06:00 PM ET", start_utc="2026-10-24T22:00Z",
         on_olbg_hub=False),
    dict(away="BKN", home="CLE", et="07:30 PM ET", start_utc="2026-10-24T23:30Z", on_olbg_hub=True),
    dict(away="MIL", home="PHI", et="07:30 PM ET", start_utc="2026-10-24T23:30Z", on_olbg_hub=True),
    dict(away="SAS", home="DAL", et="08:00 PM ET", start_utc="2026-10-25T00:00Z", on_olbg_hub=True),
    dict(away="WAS", home="CHI", et="08:00 PM ET", start_utc="2026-10-25T00:00Z", on_olbg_hub=True),
    dict(away="HOU", home="ATL", et="08:30 PM ET", start_utc="2026-10-25T00:30Z", on_olbg_hub=True),
    dict(away="NOP", home="DEN", et="09:00 PM ET", start_utc="2026-10-25T01:00Z", on_olbg_hub=True),
    dict(away="MEM", home="SAC", et="09:00 PM ET", start_utc="2026-10-25T01:00Z", on_olbg_hub=False),
    dict(away="GSW", home="PHX", et="10:00 PM ET", start_utc="2026-10-25T02:00Z", on_olbg_hub=True),
]

# Injury/availability rows exactly as the league filed them. "NOT YET
# SUBMITTED" is the league's own text and is kept verbatim.
NBA_INJURIES = {
    ("MIA", "CHA"): {
        "MIA": [("Larsson, Pelle", "Probable", "Left Finger Sprain")],
        "CHA": [("Anderson, Christian", "Probable", "Left Ankle Sprain"),
                ("Boswell, Kylan", "Out", "Right Knee Surgery"),
                ("Knueppel, Kon", "Out", "Left Hamstring Strain"),
                ("White, Coby", "Out", "Left Calf Strain"),
                ("Williams, Grant", "Out", "Right Hamstring Strain")],
    },
    ("BKN", "CLE"): {
        "BKN": [("Bilodeau, Tyler", "Out", "Right Shoulder Sprain")],
        "CLE": [("Diop, Khalifa", "Out", "Left Knee Injury Management"),
                ("Tomlin, Nae'Qwan", "Out", "Low Back Stress Reaction"),
                ("Udeh, Jr., Ernest", "Out", "G League - Two-Way")],
    },
    ("MIL", "PHI"): {
        "MIL": "NOT YET SUBMITTED",
        "PHI": [("Barlow, Dominick", "Out", "Low Back Stress Reaction"),
                ("Fall, Tacko", "Out", "Left Quadriceps Strain"),
                ("Hukporti, Ariel", "Out", "Right Achilles Tendon Rupture / Tear"),
                ("James, LeBron", "Out", "Low back/ Sciatica"),
                ("Wade, Dean", "Questionable", "Left Ankle Sprain")],
    },
    ("SAS", "DAL"): {"SAS": "NOT YET SUBMITTED", "DAL": "NOT YET SUBMITTED"},
    ("WAS", "CHI"): {
        "WAS": "NOT YET SUBMITTED",
        "CHI": [("Claxton, Nic", "Out", "Left Hamstring Strain"),
                ("Essengue, Noa", "Probable", "Right Head Contusion")],
    },
    ("HOU", "ATL"): {
        "HOU": [("Adams, Steven", "Out", "Left Ankle Injury Management"),
                ("Sheppard, Reed", "Questionable", "Left Knee Contusion / Bone Bruise"),
                ("VanVleet, Fred", "Out", "Right Knee Injury Management")],
        "ATL": [("Dennis, RayJ", "Questionable", "G League - Two-Way"),
                ("Gilbert, Keshon", "Questionable", "G League - Two-Way"),
                ("Gueye, Mouhamed", "Out", "Left Foot Fracture"),
                ("Veesaar, Henri", "Out", "Right ACL Tear"),
                ("Wilson, Jalen", "Questionable", "G League - Two-Way")],
    },
    ("NOP", "DEN"): {
        "NOP": "NOT YET SUBMITTED",
        "DEN": [("Diallo, Alpha", "Questionable", "Right Wrist Sprain"),
                ("Johnson, Cameron", "Out", "Right Ankle Sprain"),
                ("Jones, Spencer", "Out", "Bilateral Hamstring Injury Management"),
                ("Strawther, Julian", "Out", "Left Knee Sprain")],
    },
    ("MEM", "SAC"): {"MEM": "NOT YET SUBMITTED", "SAC": "NOT YET SUBMITTED"},
    ("GSW", "PHX"): {
        "GSW": "NOT YET SUBMITTED",
        "PHX": [("Ighodaro, Oso", "Doubtful", "Right Oblique Strain"),
                ("Kennard, Luke", "Questionable", "Left Knee Tendinopathy"),
                ("Williams, Mark", "Out", "Left Shoulder Surgery")],
    },
}

# --------------------------------------------------------------------------
# MLB -- one game. Everything below came from the MLB schedule API.
# --------------------------------------------------------------------------

MLB_GAMES = [
    dict(away="Tampa Bay Rays", home="Milwaukee Brewers", competition="World Series, Game 2",
         start_utc="2026-10-25T00:00Z", venue="American Family Field",
         away_pitcher="Drew Rasmussen", home_pitcher="Logan Henderson",
         away_series="0-1", home_series="1-0", series_game="2 of 7"),
]

# --------------------------------------------------------------------------
# Cricket -- CSA fixtures read from the governing body (25 October 2026).
# --------------------------------------------------------------------------

CRICKET_GAMES = [
    dict(competition="Hollywoodbets Pro 20", home="Fidelity Titans Women", away="YesPlay Cobras",
         date="2026-10-25", local_time="10:00", venue=None,
         url="https://cricket.co.za/fixtures/"),
    dict(competition="Hollywoodbets Pro 20", home="Garden Route Badgers Women", away="Warriors",
         date="2026-10-25", local_time="10:00", venue=None,
         url="https://cricket.co.za/fixtures/"),
    dict(competition="Pro20 Cup 2026/27", home="World Sports Betting Eastern Storm",
         away="CSA High Performance", date="2026-10-25", local_time="13:00", venue=None,
         url="https://cricket.co.za/fixtures/"),
    dict(competition="Colts: 1-Day Match", home="Boland", away="Border",
         date="2026-10-25", local_time="10:00", venue=None,
         url="https://cricket.co.za/fixtures/"),
    dict(competition="CSA Women's Provincial 2026/27", home="Northern Cape Women",
         away="Free State Women", date="2026-10-25", local_time="10:00", venue=None,
         url="https://cricket.co.za/fixtures/"),
    dict(competition="CSA Women's Provincial 2026/27", home="Limpopo Women",
         away="North West Dragons Women", date="2026-10-25", local_time="10:00", venue=None,
         url="https://cricket.co.za/fixtures/"),
]

# --------------------------------------------------------------------------
# Everything OLBG served that we did NOT independently confirm. Published as
# discovery-only listings so the user can see the full board.
# --------------------------------------------------------------------------

DISCOVERY_ONLY = {
    "tennis": [
        ("Elena Rybakina vs Leylah Fernandez", "Tomorrow 05:00", "88%"),
        ("Daniil Medvedev vs Nikoloz Basilashvili", "Tomorrow 06:00", "88%"),
        ("Ashlyn Krueger vs Katerina Siniakova", "Tomorrow 00:30", "56%"),
        ("Stan Wawrinka vs Jiri Lehecka", "26 Oct 06:00", "67%"),
        ("Alexandra Eala vs Mika Stojsavljevic", "26 Oct 22:00", "67%"),
        ("Lorenzo Musetti vs Taylor Fritz", "Tomorrow 09:30", "50%"),
        ("Novak Djokovic vs Ugo Humbert", "26 Oct 06:00", "100%"),
        ("Ben Shelton vs Casper Ruud", "26 Oct 06:00", "100%"),
        ("Holger Rune vs Quentin Halys", "26 Oct 06:00", "100%"),
        ("Taylor Fritz vs Stefanos Tsitsipas", "26 Oct 06:00", "100%"),
    ],
    "volleyball": [
        ("Trentino vs Cisterna (SuperLega)", "Tomorrow 12:00", "86%"),
        ("Civitanova vs Padova (SuperLega)", "Tomorrow 13:00", "100%"),
        ("Perugia vs Pordenone (SuperLega)", "Tomorrow 13:00", "83%"),
        ("Monza vs Verona (SuperLega)", "Tomorrow 13:00", "100%"),
        ("CHKS Chelm vs Resovia Rzeszow (PlusLiga)", "Tomorrow 13:00", "60%"),
        ("Vakifbank W vs Galatasaray W (Turkey)", "Tomorrow 07:00", "57%"),
        ("Besiktas W vs Goztepe W (Turkey)", "Tomorrow 06:00", "67%"),
        ("Barock Volleys Ludwigsburg vs TV Rottenburg (Germany)", "Tomorrow 12:00", "83%"),
        ("Abel-Moda Brusque W vs Praia Clube W (Brazil)", "Today 20:00", "75%"),
    ],
    "handball": [
        ("Ystads IF HF vs Hammarby IF HF (Sweden)", "Tomorrow 09:00", "draw 100%"),
        ("CBM Sporting Alicante vs Ademar Leon (Spain)", "Tomorrow 07:00", "draw 71%"),
        ("Saint Raphael vs PSG Handball (France)", "Tomorrow 11:00", "draw 71%"),
        ("SC Magdeburg vs HC Kriens Luzern (Europe)", "28 Oct 15:45", "draw 71%"),
        ("Rhein-Neckar Lowen vs SC Magdeburg (Germany)", "Tomorrow 10:00", "home 67%"),
        ("Fuchse Berlin vs HSG Wetzlar (Germany)", "Tomorrow 11:30", "draw 50%"),
        ("KS Kielce vs Kolstad (Europe)", "28 Oct 15:45", "draw 75%"),
        ("Bergischer HC vs HC Hamburg (Germany)", "Tomorrow 11:30", "draw 100%"),
    ],
    "rugby-union": [
        ("USA v Australia A", "Today 19:00", "Australia A 67%"),
        ("Harlequins v Saracens (Premiership)", "Tomorrow 11:00", "Harlequins 80%"),
        ("La Rochelle v Bordeaux (Top 14)", "Tomorrow 16:05", "Bordeaux 60%"),
    ],
    "gaelic-sports": [
        ("Moycullen v Salthill-Knocknacarra", "Tomorrow 12:00", "Salthill +3.5, 60%"),
        ("St Finbarrs v Nemo Rangers", "Tomorrow 12:00", "Nemo Rangers +1.5, 87%"),
        ("Kanturk v Eire Og Cor", "01 Nov 09:00", "Eire Og +0.5, 100%"),
        ("Fr Caseys v Kildimo Pallaskenry", "01 Nov 10:30", "Fr Caseys 57%"),
    ],
    "darts": [
        ("Ross Smith vs Luke Woodhouse", "Tomorrow 08:15", "Ross Smith 100%"),
        ("Gerwyn Price vs Stephen Bunting", "Tomorrow 09:15", "Over 10.5 180s"),
        ("European Championship (outright)", "Tomorrow 14:00", "Luke Littler 62%"),
        ("PDC World Championship 2027 (outright)", "03 Jan 2027", "Luke Littler 61%"),
    ],
    "greyhounds": [
        ("11:04 Doncaster", "Tomorrow 07:04", "Snowfall 100%"),
    ],
    "cricket": [
        ("Toronto Kings vs Vancouver Guardians T20", "Today 19:00", "Toronto 90%"),
        ("Pakistan vs England One Day Match", "Tomorrow 04:00", "Pakistan 60%"),
        ("North West Dragons vs Northern Cape Heat T20", "Tomorrow 07:00", "North West 89%"),
        ("Tuskers vs Western Province T20", "Tomorrow 07:00", "Western Province 100%"),
        ("Eastern Storm vs South Africa Emerging T20", "Tomorrow 07:00", "Eastern Storm 83%"),
        ("Boland vs Titans T20", "Tomorrow 07:00", "Titans 83%"),
        ("India W vs Zimbabwe W 2nd ODI", "Tomorrow 04:30", "S Mandhana top bat 60%"),
        ("New Zealand vs India 3rd T20", "27 Oct 03:00", "India 75%"),
        ("Namibia vs Ireland 3rd ODI", "27 Oct 03:30", "Ireland 100%"),
    ],
    "basketball": [
        ("MIL Bucks @ PHI 76ers", "Today 19:30", "PHI 57%"),
        ("NO Pelicans @ DEN Nuggets", "Today 22:00", "DEN 80%"),
        ("BKN Nets @ CLE Cavaliers", "Today 19:30", "CLE 64%"),
        ("SA Spurs @ DAL Mavericks", "Today 20:00", "SAS 70%"),
        ("HOU Rockets @ ATL Hawks", "Today 20:30", "ATL 83%"),
        ("WAS Wizards @ CHI Bulls", "Today 20:00", "WAS 100%"),
        ("GS Warriors @ PHX Suns", "Today 23:00", "GSW 60%"),
    ],
    "baseball": [
        ("TB Rays @ MIL Brewers", "Today 20:00", "TB Rays 59%"),
    ],
    "ice-hockey": [
        ("TOR Maple Leafs @ EDM Oilers", "Today 19:07", "EDM 79%"),
        ("SJ Sharks @ BOS Bruins", "Today 19:07", "BOS 83%"),
        ("CAR Hurricanes @ STL Blues", "Today 19:07", "CAR 91%"),
        ("VGS Golden Knights @ CLB Blue Jackets", "Today 19:07", "VGK 67%"),
        ("MIN Wild @ SEA Kraken", "Today 23:07", "SEA 58%"),
        ("NY Rangers @ OTT Senators", "Today 19:07", "NYR 86%"),
        ("BUF Sabres @ WAS Capitals", "Today 19:07", "WAS 71%"),
        ("TB Lightning @ UTA Mammoth", "Today 22:07", "UTA 56%"),
        ("NSH Predators @ PIT Penguins", "Today 19:07", "PIT 80%"),
        ("DET Red Wings @ CGY Flames", "Today 23:07", "CGY 67%"),
        ("MTL Canadiens @ WPG Jets", "Tomorrow 19:07", "Over 5.5"),
    ],
    "rugby-league": [
        ("State of Origin 2027 (outright)", "27 May 2027", "New South Wales 75%"),
        ("Super League 2027 Grand Final (outright)", "02 Oct 2027", "Leeds Rhinos 33%"),
        ("NRL 2027 Grand Final (outright)", "03 Oct 2027", "Penrith Panthers 50%"),
    ],
}

OLBG_NAME_DIFFERENCES = [
    dict(olbg="Eastern Storm vs South Africa Emerging T20",
         official="World Sports Betting Eastern Storm vs CSA High Performance",
         note="OLBG bills the CSA High Performance XI as 'South Africa Emerging'. "
              "The governing body's own fixture list uses 'CSA High Performance'.",
         sources=["olbg-cricket", "csa-home"]),
    dict(olbg="VGS Golden Knights",
         official="Vegas Golden Knights",
         note="OLBG's abbreviation for the club differs from the NHL's own 'VGK'.",
         sources=["olbg-icehockey", "nhl-team-summary"]),
]
