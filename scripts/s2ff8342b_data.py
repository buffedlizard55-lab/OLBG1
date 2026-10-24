#!/usr/bin/env python3
"""Session 2ff8342b — verified fact base for the 24 October 2026 desk.

Everything in SOURCES was actually fetched during this session at the UTC time
recorded. FIXTURES carry the raw facts that were observed on those pages.
Nothing here is inferred: a field that was not seen is None and is listed in
`gaps`. Predictions are written by hand (no generator templates) and only use
the facts attached to their own fixture.
"""

OBSERVED_AT = "2026-10-24T17:50:00Z"
DESK_DATE = "2026-10-24"
DESK_LABEL = "Saturday 24 October 2026"

COVERED_SPORTS = [
    ("golf", "Golf", "Golf/5"),
    ("volleyball", "Volleyball", "Volleyball/21"),
    ("rugby-union", "Rugby Union", "Rugby_Union/9"),
    ("cricket", "Cricket", "Cricket/7"),
    ("snooker", "Snooker", "Snooker/8"),
    ("darts", "Darts", "Darts/15"),
    ("baseball", "Baseball", "Baseball/12"),
    ("gaelic-sports", "Gaelic Sports", "Gaelic_Football/25"),
    ("greyhounds", "Greyhounds", "Greyhounds/28"),
    ("tennis", "Tennis", "Tennis/3"),
    ("motor-racing", "Motor Racing", "Motor_Racing/14"),
    ("handball", "Handball", "Handball/20"),
    ("ice-hockey", "Ice Hockey", "Ice_Hockey/13"),
    ("basketball", "Basketball", "Basketball/4"),
    ("rugby-league", "Rugby League", "Rugby_League/10"),
]

# ---------------------------------------------------------------------------
# Sources: each entry is a page this session fetched and read.
# role: "official" = league / governing body / tour operator itself.
# role: "discovery" = OLBG listing page (fixture discovery only, never used to
# certify a fact).
# ---------------------------------------------------------------------------
SOURCES = {
    "MLB-SCHED": {
        "name": "MLB StatsAPI — 2026 World Series schedule (gamePk 849802, 849804, 849803)",
        "url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-24&endDate=2026-10-27&hydrate=probablePitcher,team,venue,linescore",
        "publisher": "Major League Baseball (statsapi.mlb.com)",
        "role": "official",
        "observed_at": "2026-10-24T17:45:00Z",
        "observed": "Three scheduled games: WS Game 2 on 2026-10-24 (TB at MIL, 2026-10-25T00:00Z), Game 3 on 2026-10-26 (MIL at TB, 2026-10-27T00:00Z), Game 4 on 2026-10-27. Probable pitchers, venues, series state and ifNecessary=N read directly from the JSON.",
    },
    "MLB-STAND-AL": {
        "name": "MLB StatsAPI — American League regular-season standings 2026",
        "url": "https://statsapi.mlb.com/api/v1/standings?leagueId=103&season=2026&standingsTypes=regularSeason",
        "publisher": "Major League Baseball (statsapi.mlb.com)",
        "role": "official",
        "observed_at": "2026-10-24T17:46:00Z",
        "observed": "Tampa Bay Rays 98-64 (.605), 55-26 home, 43-38 away, 736 runs scored, 650 allowed, last ten 5-5.",
    },
    "MLB-STAND-NL": {
        "name": "MLB StatsAPI — National League regular-season standings 2026",
        "url": "https://statsapi.mlb.com/api/v1/standings?leagueId=104&season=2026&standingsTypes=regularSeason",
        "publisher": "Major League Baseball (statsapi.mlb.com)",
        "role": "official",
        "observed_at": "2026-10-24T17:47:00Z",
        "observed": "Milwaukee Brewers 103-59 (.636), 55-26 home, 48-33 away, 832 runs scored, 618 allowed, +214 differential, W5, last ten 8-2.",
    },
    "NHL-SCHED": {
        "name": "NHL official schedule API — 24 October 2026 (12 games)",
        "url": "https://api-web.nhle.com/v1/schedule/2026-10-24",
        "publisher": "National Hockey League (api-web.nhle.com)",
        "role": "official",
        "observed_at": "2026-10-24T17:48:00Z",
        "observed": "Twelve games with start times in UTC, venues, game states and publisher-supplied odds arrays (providerId 3/6/7/8/9/10).",
    },
    "NHL-STAND": {
        "name": "NHL official standings API — 2026-10-24",
        "url": "https://api-web.nhle.com/v1/standings/2026-10-24",
        "publisher": "National Hockey League (api-web.nhle.com)",
        "role": "official",
        "observed_at": "2026-10-24T17:49:00Z",
        "observed": "Games played, points, points percentage, goals for/against, home and road splits, streaks and last-ten records for every club; standingsDateTimeUtc 2026-10-24T17:44:00Z.",
    },
    "NBA-REF": {
        "name": "NBA Official — referee assignments, 24 October 2026",
        "url": "https://official.nba.com/referee-assignments/",
        "publisher": "NBA Official (official.nba.com)",
        "role": "official",
        "observed_at": "2026-10-24T17:50:00Z",
        "observed": "Eight games listed for the date: Miami @ Charlotte, Brooklyn @ Cleveland, Milwaukee @ Philadelphia, Houston @ Atlanta, Washington @ Chicago, San Antonio @ Dallas, New Orleans @ Denver, Golden State @ Phoenix. No tip-off times or season records on the page.",
    },
    "NBA-STAND": {
        "name": "NBA.com \u2014 2026-27 regular-season standings (read 24 October 2026)",
        "url": "https://www.nba.com/standings",
        "publisher": "NBA (nba.com)",
        "role": "official",
        "observed_at": "2026-10-24T17:49:00Z",
        "observed": "Two games played per club at most. Records, home/road splits, last-ten and streak columns read directly: ATL 2-0 (2-0 road), DET 2-0, PHI 2-0 (1-0 home), TOR 2-0, LAL 2-0, OKC 2-0, HOU 2-0 (1-0 road), POR 2-0, MEM 2-0, MIN 2-0, WAS 1-1, BOS 1-1, CHI 1-1 (1-1 road), CHA 1-1 (0-1 home), IND 1-1, LAC 1-1, UTA 1-1, DAL 1-1 (1-1 road), BKN 0-1, CLE 0-1, DEN 0-1, PHX 0-1, ORL 0-2, MIA 0-2 (0-2 home), NYK 0-2, MIL 0-2, NOP 0-2, SAS 0-2 (0-2 home), GSW 0-2.",
    },
    "ATP-SCORES": {
        "name": "ATP Tour — current scores, draws and schedules",
        "url": "https://www.atptour.com/en/scores/current",
        "publisher": "ATP Tour (atptour.com)",
        "role": "official",
        "observed_at": "2026-10-24T17:51:00Z",
        "observed": "Semi-final results: Medvedev d. Bublik 6-3 ret.; Basilashvili d. Tsitsipas 6-4 6-7(5) 6-3; Griekspoor d. Cerundolo 2-6 6-3 7-6(4); Musetti d. Cobolli 4-6 6-2 7-5; Fritz d. Paul 6-3 7-5. Lyon final: Fritz v Musetti.",
    },
    "ATP-ALMATY": {
        "name": "ATP Tour — Almaty Open 2026, Medvedev v Bublik semi-final stats centre",
        "url": "https://www.atptour.com/en/scores/stats-centre/live/2026/9410/MS002",
        "publisher": "ATP Tour (atptour.com)",
        "role": "official",
        "observed_at": "2026-10-24T17:52:00Z",
        "observed": "Tournament identified as the Almaty Open (Almaty 2026); Medvedev won the semi-final 6-3 with Bublik retiring.",
    },
    "ATP-LYON": {
        "name": "ATP Tour — Lyon 2026 semi-final report (Fritz v Musetti final)",
        "url": "https://www.atptour.com/en/news/fritz-paul-cobolli-musetti-lyon-2026-sfs",
        "publisher": "ATP Tour (atptour.com)",
        "role": "official",
        "observed_at": "2026-10-24T17:53:00Z",
        "observed": "Headline and report link state Musetti saved four match points to beat Cobolli and set a Fritz final in Lyon; Fritz beat Paul 6-3 7-5.",
    },
    "WST-MATCHES": {
        "name": "World Snooker Tour — matches, BetVictor Northern Ireland Open 2026",
        "url": "https://www.wst.tv/matches/?",
        "publisher": "World Snooker Tour (wst.tv)",
        "role": "official",
        "observed_at": "2026-10-24T17:54:00Z",
        "observed": "Semi-final 62 Mark Williams v Jak Jones listed Live Now at 14:00 Sat 24 Oct; Kyren Wilson 6-5 Sam Craigie in the other semi-final; final scheduled 08:00 Sun 25 Oct, Wilson versus winner of match 62.",
    },
    "GAA-FIX": {
        "name": "GAA — fixtures and results, 24 October 2026",
        "url": "https://www.gaa.ie/fixtures-results",
        "publisher": "Gaelic Athletic Association (gaa.ie)",
        "role": "official",
        "observed_at": "2026-10-24T17:55:00Z",
        "observed": "Only fixture listed for Saturday 24 October is the Shinty-Hurling International, Ireland v Scotland, 18:00, SuperValu Páirc Uí Chaoimh. No Gaelic football fixture appears.",
    },
    "F1-MEXICO": {
        "name": "Formula 1 — Mexico City Grand Prix 2026 race hub",
        "url": "https://www.formula1.com/en/racing/2026/mexico",
        "publisher": "Formula 1 (formula1.com)",
        "role": "official",
        "observed_at": "2026-10-24T17:56:00Z",
        "observed": "Event runs 30 October – 1 November 2026 (practice 30 Oct, qualifying 31 Oct, race 1 Nov 15:00). No race on 24–25 October.",
    },
}

# OLBG discovery pages. These are listing pages only: they tell us which events
# OLBG currently markets, not that a fixture is confirmed.
OLBG_HUBS = {
    "golf": ("https://www.olbg.com/betting-tips/Golf/5", "returned 'No tips found.' in the fetched listing"),
    "volleyball": ("https://www.olbg.com/betting-tips/Volleyball/21", "13 match listings read"),
    "rugby-union": ("https://www.olbg.com/betting-tips/Rugby_Union/9", "5 match listings read"),
    "cricket": ("https://www.olbg.com/betting-tips/Cricket/7", "8 match listings read"),
    "snooker": ("https://www.olbg.com/betting-tips/Snooker/8", "1 live match listing read"),
    "darts": ("https://www.olbg.com/betting-tips/Darts/15", "4 match listings read"),
    "baseball": ("https://www.olbg.com/betting-tips/Baseball/12", "1 match listing read"),
    "gaelic-sports": ("https://www.olbg.com/betting-tips/Gaelic_Football/25", "hub fetched; the only 24 Oct fixture listed was a hurling international, outside the brief"),
    "greyhounds": ("https://www.olbg.com/betting-tips/Greyhounds/28", "race listings read (dog names, tracks, times)"),
    "tennis": ("https://www.olbg.com/betting-tips/Tennis/3", "6 match listings read"),
    "motor-racing": ("https://www.olbg.com/betting-tips/Motor_Racing/14", "Mexico GP weekend listings read"),
    "handball": ("https://www.olbg.com/betting-tips/Handball/20", "13 match listings read"),
    "ice-hockey": ("https://www.olbg.com/betting-tips/Ice_Hockey/13", "12 NHL listings read"),
    "basketball": ("https://www.olbg.com/betting-tips/Basketball/4", "8 NBA listings read"),
    "rugby-league": ("https://www.olbg.com/betting-tips/Rugby_League/10", "no current fixtures; futures only"),
}

# ---------------------------------------------------------------------------
# Market families examined per sport on the OLBG listing (discovery only) and
# what stopped us pricing them. Status is always one of:
#   priced      — issued from official inputs elsewhere in this file
#   withheld    — market exists on OLBG, official inputs missing
#   unreadable  — page did not render the market list at all
# ---------------------------------------------------------------------------
MARKETS_EXAMINED = {
    "golf": [("Outright winner", "unreadable", "the OLBG golf hub returned 'No tips found' and no official field list was read"),
             ("Top 10 / Top 20 finish", "unreadable", "same empty hub; no field or tee times captured")],
    "volleyball": [("Match winner", "withheld", "no official league table or set-rate page was readable for these fixtures"),
                   ("Set handicap", "withheld", "same missing set data"),
                   ("Total sets / points", "withheld", "no official scoring-rate source captured")],
    "rugby-union": [("Match winner", "withheld", "the URC/Premiership fixture pages were JavaScript-only or 404"),
                    ("Handicap", "withheld", "no official score margins read"),
                    ("Total points", "withheld", "no official scoring-rate source captured")],
    "cricket": [("Match winner", "withheld", "OLBG listed the matches; no official fixture page confirmed them"),
                ("Runs handicap / total", "withheld", "no official innings data or toss/line-up feed read")],
    "snooker": [("Match winner", "withheld", "one live semi-final on the hub; wst.tv confirmed the draw but not a start time for the final opponent"),
                ("Frame handicap", "withheld", "no official frame-level results read for both semi-finalists"),
                ("Total frames", "withheld", "same missing frame data")],
    "darts": [("Match winner", "withheld", "pdc.tv served a cookie-consent shell, so no official draw or averages were read"),
              ("Legs / sets handicap", "withheld", "no official leg-level data"),
              ("Total 180s", "withheld", "no official maximums count read")],
    "baseball": [("Match winner", "priced", "season standings via statsapi.mlb.com"),
                 ("Run line ±1.5", "priced", "Poisson run rates from season runs scored/allowed"),
                 ("Match total", "priced", "same run rates; park and bullpen not modelled")],
    "gaelic-sports": [("Match result", "withheld", "the only 24 Oct GAA fixture was hurling, which the brief excludes"),
                      ("Handicap / total", "withheld", "no in-scope fixture to price")],
    "greyhounds": [("Race winner", "withheld", "GBGB trap draws and form were not readable in this window"),
                   ("Forecast / tricast", "withheld", "same missing form data")],
    "tennis": [("Match winner", "withheld", "ATP scores were read, but no official rankings or head-to-head file for the finalists"),
               ("Game handicap", "withheld", "no official service/return splits for both finalists"),
               ("Total games", "withheld", "same missing splits")],
    "motor-racing": [("Race winner", "withheld", "formula1.com confirmed the session times and circuit, not a car-performance feed"),
                     ("Podium / points finish", "withheld", "same missing performance data")],
    "handball": [("Match winner", "withheld", "EHF pages listed fixtures; no official table or goal-rate page was readable"),
                 ("Handicap", "withheld", "no official margin data"),
                 ("Total goals", "withheld", "no official scoring-rate source captured")],
    "ice-hockey": [("Match winner", "priced", "official NHL standings and schedule via api-web.nhle.com"),
                   ("Puck line ±1.5", "priced", "Skellam on season goal rates"),
                   ("Match total", "priced", "Poisson on combined goal rates; goaltenders not modelled")],
    "basketball": [("Match winner", "priced", "official nba.com standings, shrunk 20 games toward .500"),
                   ("Spread", "withheld", "no official points-per-game or pace feed was readable, so no margin can be derived"),
                   ("Match total", "withheld", "same missing scoring-rate input")],
    "rugby-league": [("Match winner", "withheld", "the OLBG hub showed no current fixture, only 2027 futures"),
                     ("Handicap / total", "withheld", "no fixture to price")],
}

# ---------------------------------------------------------------------------
# Fixtures.
# verification:
#   "official"       — participants/date read on an official page (source ids
#                      in `sources`); statistics attached where quoted.
#   "discovery_only" — seen only on OLBG; no official page fetched for it.
# start_utc None   — time not obtained from an official page. Never guessed.
# ---------------------------------------------------------------------------
FIXTURES = [
    # ---------------- Baseball (MLB) ----------------
    {
        "id": "BB-01", "sport": "baseball", "league": "MLB World Series — Game 2",
        "event": "Tampa Bay Rays at Milwaukee Brewers",
        "away": "Tampa Bay Rays", "home": "Milwaukee Brewers",
        "start_utc": "2026-10-25T00:00:00Z",
        "venue": "American Family Field, Milwaukee",
        "status": "Scheduled", "verification": "official",
        "sources": ["MLB-SCHED", "MLB-STAND-AL", "MLB-STAND-NL"],
        "facts": {
            "series": "Milwaukee leads 1-0",
            "away_pitcher": "Drew Rasmussen (TB)",
            "home_pitcher": "Logan Henderson (MIL)",
            "away_record": "98-64 (.605), 43-38 away",
            "home_record": "103-59 (.636), 55-26 home",
            "away_runs": "736 scored / 650 allowed (162 games)",
            "home_runs": "832 scored / 618 allowed (+214, MLB best)",
            "home_form": "W5 entering the series; 8-2 in the last ten",
            "away_form": "L1; 5-5 in the last ten",
        },
        "gaps": ["Injury reports not captured for either roster.",
                 "Bullpen availability for Game 2 not published on the pages fetched."],
    },
    {
        "id": "BB-02", "sport": "baseball", "league": "MLB World Series — Game 3",
        "event": "Milwaukee Brewers at Tampa Bay Rays",
        "away": "Milwaukee Brewers", "home": "Tampa Bay Rays",
        "start_utc": "2026-10-27T00:00:00Z",
        "venue": "Tropicana Field, St. Petersburg",
        "status": "Scheduled", "verification": "official",
        "sources": ["MLB-SCHED", "MLB-STAND-AL", "MLB-STAND-NL"],
        "facts": {
            "series": "Game 3 of the best-of-seven",
            "away_pitcher": "Robert Gasser (MIL)",
            "home_pitcher": "Freddy Peralta (TB)",
            "away_record": "103-59 (.636), 48-33 away",
            "home_record": "98-64 (.605), 55-26 home",
            "away_runs": "832 scored / 618 allowed",
            "home_runs": "736 scored / 650 allowed",
            "home_form": "Tampa Bay finished 63-32 at night",
            "away_form": "Milwaukee finished 68-35 at night",
        },
        "gaps": ["Pitcher workloads after Games 1–2 not published on the pages fetched.",
                 "No injury report captured."],
    },
    # ---------------- Ice Hockey (NHL) ----------------
    {
        "id": "IH-01", "sport": "ice-hockey", "league": "NHL regular season",
        "event": "San Jose Sharks at Boston Bruins",
        "away": "San Jose Sharks", "home": "Boston Bruins",
        "start_utc": "2026-10-24T23:00:00Z", "venue": "TD Garden, Boston",
        "status": "Scheduled", "verification": "official", "sources": ["NHL-SCHED", "NHL-STAND"],
        "facts": {"away_record": "6-4-1 (13 pts), 33 GF / 37 GA, 4-2-1 away",
                  "home_record": "8-2-1 (17 pts), 42 GF / 22 GA, 4-1-0 home",
                  "away_form": "W2", "home_form": "W1",
                  "market_ref": "Sharks +152 / Bruins -184 (official NHL API odds array)"},
        "gaps": ["Goaltender starters not published on the schedule page.",
                 "Injury and roster status not captured."],
    },
    {
        "id": "IH-02", "sport": "ice-hockey", "league": "NHL regular season",
        "event": "New York Rangers at Ottawa Senators",
        "away": "New York Rangers", "home": "Ottawa Senators",
        "start_utc": "2026-10-24T23:00:00Z", "venue": "Canadian Tire Centre, Ottawa",
        "status": "Scheduled", "verification": "official", "sources": ["NHL-SCHED", "NHL-STAND"],
        "facts": {"away_record": "7-4-1 (15 pts), 37 GF / 29 GA, 1-4-1 away",
                  "home_record": "7-3-0 (14 pts), 31 GF / 30 GA, 4-2-0 home",
                  "away_form": "L1; 6-0-0 at home but 1-4-1 on the road",
                  "home_form": "L1", "market_ref": "Rangers +105 / Senators -128"},
        "gaps": ["Goaltender starters not published on the schedule page.",
                 "Injury and roster status not captured."],
    },
    {
        "id": "IH-03", "sport": "ice-hockey", "league": "NHL regular season",
        "event": "Nashville Predators at Pittsburgh Penguins",
        "away": "Nashville Predators", "home": "Pittsburgh Penguins",
        "start_utc": "2026-10-24T23:00:00Z", "venue": "PPG Paints Arena, Pittsburgh",
        "status": "Scheduled", "verification": "official", "sources": ["NHL-SCHED", "NHL-STAND"],
        "facts": {"away_record": "3-3-3 (9 pts), 23 GF / 30 GA, 1-1-2 away",
                  "home_record": "4-6-1 (9 pts), 37 GF / 38 GA, 3-1-0 home",
                  "away_form": "L1", "home_form": "W1",
                  "market_ref": "Predators +106 / Penguins -128"},
        "gaps": ["Goaltender starters not published on the schedule page.",
                 "Injury and roster status not captured."],
    },
    {
        "id": "IH-04", "sport": "ice-hockey", "league": "NHL regular season",
        "event": "Buffalo Sabres at Washington Capitals",
        "away": "Buffalo Sabres", "home": "Washington Capitals",
        "start_utc": "2026-10-24T23:00:00Z", "venue": "Capital One Arena, Washington",
        "status": "Scheduled", "verification": "official", "sources": ["NHL-SCHED", "NHL-STAND"],
        "facts": {"away_record": "4-4-2 (10 pts), 28 GF / 37 GA, 1-1-2 away",
                  "home_record": "5-4-0 (10 pts), 30 GF / 29 GA, 4-2-0 home",
                  "away_form": "L1", "home_form": "L1",
                  "market_ref": "Sabres +100 / Capitals -120"},
        "gaps": ["Goaltender starters not published on the schedule page.",
                 "Injury and roster status not captured."],
    },
    {
        "id": "IH-05", "sport": "ice-hockey", "league": "NHL regular season",
        "event": "Carolina Hurricanes at St. Louis Blues",
        "away": "Carolina Hurricanes", "home": "St. Louis Blues",
        "start_utc": "2026-10-24T23:00:00Z", "venue": "Enterprise Center, St. Louis",
        "status": "Scheduled", "verification": "official", "sources": ["NHL-SCHED", "NHL-STAND"],
        "facts": {"away_record": "8-2-2 (18 pts), 47 GF / 33 GA, 6-1-1 away",
                  "home_record": "5-4-1 (11 pts), 35 GF / 31 GA, 3-0-1 home",
                  "away_form": "8-1-1 in the last ten", "home_form": "W2",
                  "market_ref": "Hurricanes -154 / Blues +128"},
        "gaps": ["Goaltender starters not published on the schedule page.",
                 "Injury and roster status not captured."],
    },
    {
        "id": "IH-06", "sport": "ice-hockey", "league": "NHL regular season",
        "event": "Toronto Maple Leafs at Edmonton Oilers",
        "away": "Toronto Maple Leafs", "home": "Edmonton Oilers",
        "start_utc": "2026-10-24T23:00:00Z", "venue": "Rogers Place, Edmonton",
        "status": "Scheduled", "verification": "official", "sources": ["NHL-SCHED", "NHL-STAND"],
        "facts": {"away_record": "6-4-2 (14 pts), 43 GF / 39 GA, 2-1-1 away",
                  "home_record": "8-1-1 (17 pts), 47 GF / 32 GA, 5-0-0 away record",
                  "away_form": "W3", "home_form": "W3; 8-1-1 in the last ten",
                  "market_ref": "Maple Leafs +150 / Oilers -182"},
        "gaps": ["Goaltender starters not published on the schedule page.",
                 "Injury and roster status not captured."],
    },
    {
        "id": "IH-07", "sport": "ice-hockey", "league": "NHL regular season",
        "event": "Tampa Bay Lightning at Utah Mammoth",
        "away": "Tampa Bay Lightning", "home": "Utah Mammoth",
        "start_utc": "2026-10-25T01:00:00Z", "venue": "Delta Center, Salt Lake City",
        "status": "Scheduled", "verification": "official", "sources": ["NHL-SCHED", "NHL-STAND"],
        "facts": {"away_record": "7-3-0 (14 pts), 34 GF / 29 GA, 2-3-0 away",
                  "home_record": "7-4-0 (14 pts), 41 GF / 36 GA, 3-1-0 home",
                  "away_form": "L1 but 5-0-0 at home", "home_form": "L1",
                  "market_ref": "Lightning +120 / Mammoth -144"},
        "gaps": ["Goaltender starters not published on the schedule page.",
                 "Injury and roster status not captured."],
    },
    {
        "id": "IH-08", "sport": "ice-hockey", "league": "NHL regular season",
        "event": "Minnesota Wild at Seattle Kraken",
        "away": "Minnesota Wild", "home": "Seattle Kraken",
        "start_utc": None, "venue": "Climate Pledge Arena, Seattle",
        "status": "Scheduled", "verification": "official", "sources": ["NHL-SCHED", "NHL-STAND"],
        "facts": {"away_record": "6-3-1 (14 pts), 32 GF / 27 GA, 2-3-2 away",
                  "home_record": "7-3-1 (15 pts), 38 GF / 36 GA, 3-2-1 home",
                  "away_form": "L1", "home_form": "W2",
                  "market_ref": "not captured — the fetched schedule excerpt did not include this game's odds"},
        "gaps": ["Official start time not captured: the game fell outside the fetched excerpt. Left blank.",
                 "Goaltender starters and injuries not captured."],
    },
    {
        "id": "IH-09", "sport": "ice-hockey", "league": "NHL regular season",
        "event": "Vegas Golden Knights at Columbus Blue Jackets",
        "away": "Vegas Golden Knights", "home": "Columbus Blue Jackets",
        "start_utc": "2026-10-24T23:00:00Z", "venue": "Nationwide Arena, Columbus",
        "status": "Scheduled", "verification": "official", "sources": ["NHL-SCHED"],
        "facts": {"away_record": "8-4-0 (16 pts), 46 GF / 36 GA",
                  "away_form": "L2", "market_ref": "Golden Knights -138 / Blue Jackets +116"},
        "gaps": ["Columbus season record not captured (club absent from the standings excerpts read).",
                 "Goaltender starters and injuries not captured."],
    },
    {
        "id": "IH-10", "sport": "ice-hockey", "league": "NHL regular season",
        "event": "Los Angeles Kings at New Jersey Devils",
        "away": "Los Angeles Kings", "home": "New Jersey Devils",
        "start_utc": "2026-10-24T19:30:00Z", "venue": "Prudential Center, Newark",
        "status": "Scheduled", "verification": "official", "sources": ["NHL-SCHED", "NHL-STAND"],
        "facts": {"home_record": "6-4-0 (12 pts), 33 GF / 31 GA, 5-2-0 home",
                  "home_form": "W2", "market_ref": "Kings +162 / Devils -194"},
        "gaps": ["Los Angeles season record not captured.", "Goaltenders and injuries not captured."],
    },
    {
        "id": "IH-11", "sport": "ice-hockey", "league": "NHL regular season",
        "event": "Detroit Red Wings at Calgary Flames",
        "away": "Detroit Red Wings", "home": "Calgary Flames",
        "start_utc": "2026-10-25T02:00:00Z", "venue": "Scotiabank Saddledome, Calgary",
        "status": "Scheduled", "verification": "official", "sources": ["NHL-SCHED", "NHL-STAND"],
        "facts": {"away_record": "4-3-3 (11 pts), 28 GF / 30 GA, 1-0-2 away",
                  "away_form": "W1", "market_ref": "Red Wings -130 / Flames +108"},
        "gaps": ["Calgary season record not captured.", "Goaltenders and injuries not captured."],
    },
    {
        "id": "IH-12", "sport": "ice-hockey", "league": "NHL regular season",
        "event": "Anaheim Ducks at Philadelphia Flyers",
        "away": "Anaheim Ducks", "home": "Philadelphia Flyers",
        "start_utc": "2026-10-24T17:00:00Z", "venue": "Xfinity Mobile Arena, Philadelphia",
        "status": "In progress at capture", "verification": "official", "sources": ["NHL-SCHED", "NHL-STAND"],
        "facts": {"home_record": "3-6-1 (9 pts), 20 GF / 37 GA, 2-2-2 home",
                  "home_form": "W3", "market_ref": "no pre-match price captured"},
        "gaps": ["Game was already live at 17:42Z, so it is not a pre-match selection.",
                 "Anaheim record not captured."],
    },
    # ---------------- Basketball (NBA) — fixtures only ----------------
    {
        "id": "BK-01", "sport": "basketball", "league": "NBA regular season",
        "event": "Miami Heat at Charlotte Hornets", "away": "Miami Heat", "home": "Charlotte Hornets",
        "start_utc": None, "venue": None, "status": "Scheduled", "verification": "official",
        "sources": ["NBA-REF", "NBA-STAND"],
        "facts": {"away_record": "Miami Heat 0-2 (0-2 home, 0-0 road, L2)", "home_record": "Charlotte Hornets 1-1 (0-1 home, 1-0 road, L1)", "referee_crew": "James Williams, Natalie Sago, Simone Jelks"},
        "gaps": ["Tip-off time not published on the official page fetched; left blank.",
                 "No injury report, tip-off time or market price was captured for this desk."],
    },
    {
        "id": "BK-02", "sport": "basketball", "league": "NBA regular season",
        "event": "Brooklyn Nets at Cleveland Cavaliers", "away": "Brooklyn Nets", "home": "Cleveland Cavaliers",
        "start_utc": None, "venue": None, "status": "Scheduled", "verification": "official",
        "sources": ["NBA-REF", "NBA-STAND"],
        "facts": {"away_record": "Brooklyn Nets 0-1 (0-0 home, 0-1 road, L1)", "home_record": "Cleveland Cavaliers 0-1 (0-0 home, 0-1 road, L1)", "referee_crew": "Courtney Kirkland, Eric Dalen, Suyash Mehta"},
        "gaps": ["Tip-off time not published on the official page fetched.", "No injury report, tip-off time or market price captured."],
    },
    {
        "id": "BK-03", "sport": "basketball", "league": "NBA regular season",
        "event": "Milwaukee Bucks at Philadelphia 76ers", "away": "Milwaukee Bucks", "home": "Philadelphia 76ers",
        "start_utc": None, "venue": None, "status": "Scheduled", "verification": "official",
        "sources": ["NBA-REF", "NBA-STAND"],
        "facts": {"away_record": "Milwaukee Bucks 0-2 (0-1 home, 0-1 road, L2)", "home_record": "Philadelphia 76ers 2-0 (1-0 home, 1-0 road, W2)", "referee_crew": "Tyler Ford, Dedric Taylor, Robert Hussey"},
        "gaps": ["Tip-off time not published on the official page fetched.", "No injury report, tip-off time or market price captured."],
    },
    {
        "id": "BK-04", "sport": "basketball", "league": "NBA regular season",
        "event": "Houston Rockets at Atlanta Hawks", "away": "Houston Rockets", "home": "Atlanta Hawks",
        "start_utc": None, "venue": None, "status": "Scheduled", "verification": "official",
        "sources": ["NBA-REF", "NBA-STAND"],
        "facts": {"away_record": "Houston Rockets 2-0 (1-0 home, 1-0 road, W2)", "home_record": "Atlanta Hawks 2-0 (0-0 home, 2-0 road, W2)", "referee_crew": "Nick Buchert, Andy Nagy, CJ Washington"},
        "gaps": ["Tip-off time not published on the official page fetched.", "No injury report, tip-off time or market price captured."],
    },
    {
        "id": "BK-05", "sport": "basketball", "league": "NBA regular season",
        "event": "Washington Wizards at Chicago Bulls", "away": "Washington Wizards", "home": "Chicago Bulls",
        "start_utc": None, "venue": None, "status": "Scheduled", "verification": "official",
        "sources": ["NBA-REF", "NBA-STAND"],
        "facts": {"away_record": "Washington Wizards 1-1 (1-1 home, 0-0 road, L1)", "home_record": "Chicago Bulls 1-1 (0-0 home, 1-1 road, W1)", "referee_crew": "Justin Van Duyne, Gediminas Petraitis, Matt Kallio"},
        "gaps": ["Tip-off time not published on the official page fetched.", "No injury report, tip-off time or market price captured."],
    },
    {
        "id": "BK-06", "sport": "basketball", "league": "NBA regular season",
        "event": "San Antonio Spurs at Dallas Mavericks", "away": "San Antonio Spurs", "home": "Dallas Mavericks",
        "start_utc": None, "venue": None, "status": "Scheduled", "verification": "official",
        "sources": ["NBA-REF", "NBA-STAND"],
        "facts": {"away_record": "San Antonio Spurs 0-2 (0-2 home, 0-0 road, L2)", "home_record": "Dallas Mavericks 1-1 (0-0 home, 1-1 road, W1)", "referee_crew": "Karl Lane, Tre Maddox, Phenizee Ransom"},
        "gaps": ["Tip-off time not published on the official page fetched.", "No injury report, tip-off time or market price captured."],
    },
    {
        "id": "BK-07", "sport": "basketball", "league": "NBA regular season",
        "event": "New Orleans Pelicans at Denver Nuggets", "away": "New Orleans Pelicans", "home": "Denver Nuggets",
        "start_utc": None, "venue": None, "status": "Scheduled", "verification": "official",
        "sources": ["NBA-REF", "NBA-STAND"],
        "facts": {"away_record": "New Orleans Pelicans 0-2 (0-1 home, 0-1 road, L2)", "home_record": "Denver Nuggets 0-1 (0-0 home, 0-1 road, L1)", "referee_crew": "Scott Foster, John Butler, Nate Cearley"},
        "gaps": ["Tip-off time not published on the official page fetched.", "No injury report, tip-off time or market price captured."],
    },
    {
        "id": "BK-08", "sport": "basketball", "league": "NBA regular season",
        "event": "Golden State Warriors at Phoenix Suns", "away": "Golden State Warriors", "home": "Phoenix Suns",
        "start_utc": None, "venue": None, "status": "Scheduled", "verification": "official",
        "sources": ["NBA-REF", "NBA-STAND"],
        "facts": {"away_record": "Golden State Warriors 0-2 (0-1 home, 0-1 road, L2)", "home_record": "Phoenix Suns 0-1 (0-0 home, 0-1 road, L1)", "referee_crew": "Ray Acosta, Sean Corbin, Derrick Collins"},
        "gaps": ["Tip-off time not published on the official page fetched.", "No injury report, tip-off time or market price captured."],
    },
    # ---------------- Tennis (ATP finals) ----------------
    {
        "id": "TN-01", "sport": "tennis", "league": "ATP Tour — Almaty Open final",
        "event": "Daniil Medvedev v Nikoloz Basilashvili", "away": "Nikoloz Basilashvili", "home": "Daniil Medvedev",
        "start_utc": None, "venue": "Almaty, Kazakhstan", "status": "Final — scheduled",
        "verification": "official", "sources": ["ATP-SCORES", "ATP-ALMATY"],
        "facts": {"home_path": "Beat Alexander Bublik 6-3 in the semi-final (Bublik retired).",
                  "away_path": "Beat Stefanos Tsitsipas 6-4 6-7(5) 6-3 in the semi-final.",
                  "other_semi": "Bublik was seeded third; Tsitsipas was seeded seventh.",
                  "ranking_note": "Neither player's current ranking was captured from an official page."},
        "gaps": ["Official start time not shown on the pages fetched; OLBG displayed 'Tomorrow 05:00' with no timezone, so it is not converted here.",
                 "No head-to-head record or serving statistics captured.",
                 "No price originated: ranking input missing."],
    },
    {
        "id": "TN-02", "sport": "tennis", "league": "ATP Tour — Lyon final",
        "event": "Taylor Fritz v Lorenzo Musetti", "away": "Lorenzo Musetti", "home": "Taylor Fritz",
        "start_utc": None, "venue": "Lyon, France", "status": "Final — scheduled",
        "verification": "official", "sources": ["ATP-SCORES", "ATP-LYON"],
        "facts": {"home_path": "Beat Tommy Paul 6-3 7-5 in the semi-final.",
                  "away_path": "Saved four match points to beat Flavio Cobolli 4-6 6-2 7-5.",
                  "seeding": "Fritz seeded second and Paul fourth in the top half; Musetti seeded sixth, Cobolli first.",
                  "ranking_note": "Current rankings were not captured from an official page."},
        "gaps": ["Official start time not captured.", "No head-to-head or serve statistics captured.",
                 "No price originated: ranking input missing."],
    },
    # ---------------- Snooker ----------------
    {
        "id": "SN-01", "sport": "snooker", "league": "BetVictor Northern Ireland Open — final",
        "event": "Kyren Wilson v Mark Williams or Jak Jones", "away": "Mark Williams / Jak Jones", "home": "Kyren Wilson",
        "start_utc": "2026-10-25T08:00:00Z", "venue": "Belfast (venue not stated on the matches page)",
        "status": "Final — opponent not yet decided", "verification": "official", "sources": ["WST-MATCHES"],
        "facts": {"semi_final": "Kyren Wilson beat Sam Craigie 6-5.",
                  "other_semi": "Mark Williams v Jak Jones was in progress at 17:54Z (0-0).",
                  "schedule": "Final listed 08:00 Sunday 25 October."},
        "gaps": ["Opponent unresolved at capture, so no selection can be priced.",
                 "The times shown on wst.tv are not timezone-labelled; the 08:00 start is recorded exactly as displayed and treated as unconfirmed."],
    },
    # ---------------- Discovery-only rows (OLBG listings) ----------------
    {
        "id": "DT-01", "sport": "darts", "league": "PDC European Championship (per OLBG listing)",
        "event": "Nathan Aspinall v Luke Littler", "away": "Nathan Aspinall", "home": "Luke Littler",
        "start_utc": None, "venue": None, "status": "Listed on OLBG", "verification": "discovery_only",
        "sources": [], "facts": {"olbg_listing": "Today 15:15; Luke Littler backed by 13 of 19 tips (68%)"},
        "gaps": ["No official PDC page could be read (the tournament page returned a cookie wall). Fixture and time are OLBG-only and are not certified.",
                 "No statistics, injuries or prices captured."],
    },
    {
        "id": "DT-02", "sport": "darts", "league": "PDC European Championship (per OLBG listing)",
        "event": "Jonny Clayton v Josh Rock", "away": "Jonny Clayton", "home": "Josh Rock",
        "start_utc": None, "venue": None, "status": "Listed on OLBG", "verification": "discovery_only",
        "sources": [], "facts": {"olbg_listing": "Today 16:15; Jonny Clayton backed by 13 of 19 tips (68%)"},
        "gaps": ["Official PDC confirmation not obtained.", "No statistics or prices captured."],
    },
    {
        "id": "DT-03", "sport": "darts", "league": "PDC European Championship (per OLBG listing)",
        "event": "Martin Schindler v Jermaine Wattimena", "away": "Martin Schindler", "home": "Jermaine Wattimena",
        "start_utc": None, "venue": None, "status": "Listed on OLBG", "verification": "discovery_only",
        "sources": [], "facts": {"olbg_listing": "Today 14:15; Jermaine Wattimena backed by 10 of 19 tips (53%)"},
        "gaps": ["Official PDC confirmation not obtained.", "No statistics or prices captured."],
    },
    {
        "id": "DT-04", "sport": "darts", "league": "PDC European Championship (per OLBG listing)",
        "event": "Gerwyn Price v Stephen Bunting", "away": "Gerwyn Price", "home": "Stephen Bunting",
        "start_utc": None, "venue": None, "status": "Listed on OLBG", "verification": "discovery_only",
        "sources": [], "facts": {"olbg_listing": "Tomorrow 07:00; Gerwyn Price backed by 2 of 2 tips"},
        "gaps": ["Official PDC confirmation not obtained.", "No statistics or prices captured."],
    },
    {
        "id": "CK-01", "sport": "cricket", "league": "T20 (per OLBG listing)",
        "event": "Toronto Kings v Vancouver Guardians", "away": "Vancouver Guardians", "home": "Toronto Kings",
        "start_utc": None, "venue": None, "status": "Listed on OLBG", "verification": "discovery_only",
        "sources": [], "facts": {"olbg_listing": "Today 19:00; Toronto Kings backed by 6 of 7 tips (86%)"},
        "gaps": ["No official competition page fetched; fixture is OLBG-only.", "No team form or squad data captured."],
    },
    {
        "id": "CK-02", "sport": "cricket", "league": "ODI (per OLBG listing)",
        "event": "Pakistan v England", "away": "England", "home": "Pakistan",
        "start_utc": None, "venue": None, "status": "Listed on OLBG", "verification": "discovery_only",
        "sources": [], "facts": {"olbg_listing": "Tomorrow 04:00; Pakistan backed by 5 of 10 tips (50%)"},
        "gaps": ["No official board (PCB/ECB) page fetched.", "No series state, form or availability captured."],
    },
    {
        "id": "CK-03", "sport": "cricket", "league": "South African domestic T20 (per OLBG listing)",
        "event": "North West Dragons v Northern Cape Heat", "away": "Northern Cape Heat", "home": "North West Dragons",
        "start_utc": None, "venue": None, "status": "Listed on OLBG", "verification": "discovery_only",
        "sources": [], "facts": {"olbg_listing": "Tomorrow 07:00; North West Dragons backed by 5 of 6 tips (83%)"},
        "gaps": ["No official CSA page fetched.", "No form or availability captured."],
    },
    {
        "id": "CK-04", "sport": "cricket", "league": "South African domestic T20 (per OLBG listing)",
        "event": "Tuskers v Western Province", "away": "Western Province", "home": "Tuskers",
        "start_utc": None, "venue": None, "status": "Listed on OLBG", "verification": "discovery_only",
        "sources": [], "facts": {"olbg_listing": "Tomorrow 07:00; Western Province backed by 5 of 5 tips (100%)"},
        "gaps": ["No official CSA page fetched.", "No form or availability captured."],
    },
    {
        "id": "HB-01", "sport": "handball", "league": "German HBL (per OLBG listing)",
        "event": "HBW Balingen-Weilstetten v MT Melsungen", "away": "MT Melsungen", "home": "HBW Balingen-Weilstetten",
        "start_utc": None, "venue": None, "status": "Listed on OLBG", "verification": "discovery_only",
        "sources": [], "facts": {"olbg_listing": "Today 14:00; market led by 'Tie' with 6 of 11 tips (55%)"},
        "gaps": ["Official HBL fixture list is rendered client-side and could not be read; OLBG listing only.",
                 "No table position, form or squad data captured."],
    },
    {
        "id": "HB-02", "sport": "handball", "league": "German HBL (per OLBG listing)",
        "event": "Rhein-Neckar Löwen v SC Magdeburg", "away": "SC Magdeburg", "home": "Rhein-Neckar Löwen",
        "start_utc": None, "venue": None, "status": "Listed on OLBG", "verification": "discovery_only",
        "sources": [], "facts": {"olbg_listing": "Tomorrow 10:00; Rhein-Neckar Löwen backed by 2 of 3 tips"},
        "gaps": ["Official HBL confirmation not obtained.", "No form data captured."],
    },
    {
        "id": "HB-03", "sport": "handball", "league": "EHF Champions League (per OLBG listing)",
        "event": "SC Magdeburg v HC Kriens-Luzern", "away": "HC Kriens-Luzern", "home": "SC Magdeburg",
        "start_utc": None, "venue": None, "status": "Listed on OLBG", "verification": "discovery_only",
        "sources": [], "facts": {"olbg_listing": "28 Oct 15:45; market led by 'Tie' with 3 of 4 tips"},
        "gaps": ["No EHF page fetched.", "No form data captured."],
    },
    {
        "id": "HB-04", "sport": "handball", "league": "Liqui Moly Handball-Bundesliga (per OLBG listing)",
        "event": "Saint-Raphaël v Paris Saint-Germain", "away": "Paris Saint-Germain", "home": "Saint-Raphaël",
        "start_utc": None, "venue": None, "status": "Listed on OLBG", "verification": "discovery_only",
        "sources": [], "facts": {"olbg_listing": "Tomorrow 11:00; PSG backed by 2 of 3 tips"},
        "gaps": ["No official LNH page fetched.", "No form data captured."],
    },
    {
        "id": "HB-05", "sport": "handball", "league": "Women's international (per OLBG listing)",
        "event": "Luxembourg W v Great Britain W", "away": "Great Britain W", "home": "Luxembourg W",
        "start_utc": None, "venue": None, "status": "Listed on OLBG", "verification": "discovery_only",
        "sources": [], "facts": {"olbg_listing": "Tomorrow 11:00; Great Britain W backed by 2 of 2 tips"},
        "gaps": ["No official federation page fetched.", "No form data captured."],
    },
    {
        "id": "VB-01", "sport": "volleyball", "league": "Italian SuperLega (per OLBG listing)",
        "event": "Trentino v Cisterna", "away": "Cisterna", "home": "Trentino",
        "start_utc": None, "venue": None, "status": "Listed on OLBG", "verification": "discovery_only",
        "sources": [], "facts": {"olbg_listing": "Tomorrow 12:00; Cisterna backed by 2 of 2 tips"},
        "gaps": ["Italian league site returned no readable fixture list; OLBG listing only.", "No form data captured."],
    },
    {
        "id": "VB-02", "sport": "volleyball", "league": "Italian SuperLega (per OLBG listing)",
        "event": "Perugia v Pordenone", "away": "Pordenone", "home": "Perugia",
        "start_utc": None, "venue": None, "status": "Listed on OLBG", "verification": "discovery_only",
        "sources": [], "facts": {"olbg_listing": "Tomorrow 13:00; Pordenone backed by 2 of 2 tips"},
        "gaps": ["Official confirmation not obtained.", "No form data captured."],
    },
    {
        "id": "VB-03", "sport": "volleyball", "league": "Polish PlusLiga (per OLBG listing)",
        "event": "CHKS Chełm v Resovia Rzeszów", "away": "Resovia Rzeszów", "home": "CHKS Chełm",
        "start_utc": None, "venue": None, "status": "Listed on OLBG", "verification": "discovery_only",
        "sources": [], "facts": {"olbg_listing": "Tomorrow 13:00; Resovia backed by 2 of 3 tips"},
        "gaps": ["Official PlusLiga confirmation not obtained.", "No form data captured."],
    },
    {
        "id": "VB-04", "sport": "volleyball", "league": "Austrian league (per OLBG listing)",
        "event": "UVC Graz W v Sportunion St Pölten W", "away": "Sportunion St Pölten W", "home": "UVC Graz W",
        "start_utc": None, "venue": None, "status": "Listed on OLBG", "verification": "discovery_only",
        "sources": [], "facts": {"olbg_listing": "Today 14:00; UVC Graz W backed by 5 of 6 tips (83%)"},
        "gaps": ["Official Austrian federation confirmation not obtained.", "No form data captured."],
    },
    {
        "id": "VB-05", "sport": "volleyball", "league": "Brazilian Superliga (per OLBG listing)",
        "event": "Abel-Moda Brusque W v Praia Clube W", "away": "Praia Clube W", "home": "Abel-Moda Brusque W",
        "start_utc": None, "venue": None, "status": "Listed on OLBG", "verification": "discovery_only",
        "sources": [], "facts": {"olbg_listing": "Today 20:00; Abel/Moda Brusque backed by 2 of 3 tips"},
        "gaps": ["Official Brazilian federation confirmation not obtained.", "No form data captured."],
    },
    {
        "id": "RU-01", "sport": "rugby-union", "league": "United Rugby Championship (per OLBG listing)",
        "event": "Ospreys v Dragons", "away": "Dragons", "home": "Ospreys",
        "start_utc": None, "venue": None, "status": "Listed on OLBG", "verification": "discovery_only",
        "sources": [], "facts": {"olbg_listing": "Today 14:00; Dragons +7.5 backed by 6 of 7 tips (86%)"},
        "gaps": ["URC fixture pages returned 404; OLBG listing only.", "No table position, form or team news captured."],
    },
    {
        "id": "RU-02", "sport": "rugby-union", "league": "Top 14 (per OLBG listing)",
        "event": "Toulon v Pau", "away": "Pau", "home": "Toulon",
        "start_utc": None, "venue": None, "status": "Listed on OLBG", "verification": "discovery_only",
        "sources": [], "facts": {"olbg_listing": "Today 15:00; Toulon backed by 4 of 7 tips (57%)"},
        "gaps": ["No LNR page fetched.", "No form or team news captured."],
    },
    {
        "id": "RU-03", "sport": "rugby-union", "league": "International (per OLBG listing)",
        "event": "USA v Australia A", "away": "Australia A", "home": "USA",
        "start_utc": None, "venue": None, "status": "Listed on OLBG", "verification": "discovery_only",
        "sources": [], "facts": {"olbg_listing": "Today 19:00; Australia A backed by 1 of 2 tips"},
        "gaps": ["No World Rugby or union page fetched.", "No form or team news captured."],
    },
    {
        "id": "RU-04", "sport": "rugby-union", "league": "Gallagher Premiership (per OLBG listing)",
        "event": "Harlequins v Saracens", "away": "Saracens", "home": "Harlequins",
        "start_utc": None, "venue": None, "status": "Listed on OLBG", "verification": "discovery_only",
        "sources": [], "facts": {"olbg_listing": "Tomorrow 11:00; Harlequins backed by 1 of 1 tip"},
        "gaps": ["Premiership Rugby's fixtures page renders client-side and returned no fixture data; OLBG listing only."],
    },
    {
        "id": "RU-05", "sport": "rugby-union", "league": "Top 14 (per OLBG listing)",
        "event": "La Rochelle v Bordeaux", "away": "Bordeaux", "home": "La Rochelle",
        "start_utc": None, "venue": None, "status": "Listed on OLBG", "verification": "discovery_only",
        "sources": [], "facts": {"olbg_listing": "Tomorrow 16:05; Bordeaux backed by 1 of 2 tips"},
        "gaps": ["No LNR page fetched.", "No form or team news captured."],
    },
    {
        "id": "GH-01", "sport": "greyhounds", "league": "UK graded racing (per OLBG listing)",
        "event": "7:58 Doncaster", "away": None, "home": "Lady Gambet",
        "start_utc": None, "venue": "Doncaster", "status": "Listed on OLBG", "verification": "discovery_only",
        "sources": [], "facts": {"olbg_listing": "Dog: Lady Gambet; 2 of 2 tips"},
        "gaps": ["No GBGB racecard fetched; trap numbers, grade, distance and going unknown.",
                 "Times are OLBG display values with no timezone."],
    },
    {
        "id": "GH-02", "sport": "greyhounds", "league": "UK graded racing (per OLBG listing)",
        "event": "8:54 Monmore", "away": None, "home": "Crossfield Jess",
        "start_utc": None, "venue": "Monmore", "status": "Listed on OLBG", "verification": "discovery_only",
        "sources": [], "facts": {"olbg_listing": "Dog: Crossfield Jess; 2 of 3 tips"},
        "gaps": ["No GBGB racecard fetched; trap numbers, grade, distance and going unknown."],
    },
    {
        "id": "GH-03", "sport": "greyhounds", "league": "UK graded racing (per OLBG listing)",
        "event": "9:14 Monmore", "away": None, "home": "Skylars Vision",
        "start_utc": None, "venue": "Monmore", "status": "Listed on OLBG", "verification": "discovery_only",
        "sources": [], "facts": {"olbg_listing": "Dog: Skylars Vision; 2 of 2 tips"},
        "gaps": ["No GBGB racecard fetched; trap numbers, grade, distance and going unknown."],
    },
    {
        "id": "GH-04", "sport": "greyhounds", "league": "UK graded racing (per OLBG listing)",
        "event": "9:18 Dunstall Park", "away": None, "home": "Avarua Lake",
        "start_utc": None, "venue": "Dunstall Park", "status": "Listed on OLBG", "verification": "discovery_only",
        "sources": [], "facts": {"olbg_listing": "Dog: Avarua Lake; 2 of 4 tips"},
        "gaps": ["No GBGB racecard fetched; trap numbers, grade, distance and going unknown."],
    },
    {
        "id": "GH-05", "sport": "greyhounds", "league": "UK graded racing (per OLBG listing)",
        "event": "10:14 Dunstall Park", "away": None, "home": "Greenwell Gypsy",
        "start_utc": None, "venue": "Dunstall Park", "status": "Listed on OLBG", "verification": "discovery_only",
        "sources": [], "facts": {"olbg_listing": "Dog: Greenwell Gypsy; 2 of 3 tips"},
        "gaps": ["No GBGB racecard fetched; trap numbers, grade, distance and going unknown."],
    },
    # ---------------- Motor racing ----------------
    {
        "id": "MR-01", "sport": "motor-racing", "league": "Formula 1 — Mexico City Grand Prix",
        "event": "Mexico City Grand Prix", "away": None, "home": None,
        "start_utc": "2026-11-01T15:00:00Z", "venue": "Autódromo Hermanos Rodríguez",
        "status": "Scheduled (future weekend)", "verification": "official", "sources": ["F1-MEXICO"],
        "facts": {"race": "Sunday 1 November 15:00 track time; qualifying 31 October 17:00",
                  "circuit": "4.304 km, 71 laps, race distance 305.354 km",
                  "note": "No Formula 1 or other motor race takes place on 24–25 October per this calendar."},
        "gaps": ["Entry list, grid and championship standings not captured.",
                 "No outright price originated: driver form and championship data missing."],
    },
]

# ---------------------------------------------------------------------------
# Hand-written predictions. Each uses only the facts of its own fixture.
# confidence is assigned in the builder from the originated probability and
# the desk's published tier rule; it is stored here as the intended label so
# the validator can cross-check the two.
# ---------------------------------------------------------------------------
PREDICTIONS = [
    {
        "id": "P-BB-01", "fixture": "BB-01", "market": "Match winner (moneyline)",
        "selection": "Milwaukee Brewers to win",
        "text": (
            "Milwaukee returns home for Game 2 of the World Series holding a 103-59 regular-season record, "
            "the best run differential in the majors at plus 214, and a 55-26 home mark. The Brewers have won "
            "five straight and eight of their last ten, while Tampa Bay went 43-38 on the road and 5-5 over the "
            "same ten-game span. Logan Henderson takes the ball against Drew Rasmussen, and Milwaukee's 832 runs "
            "scored are 96 more than Tampa Bay managed across 162 games. The selection is the Brewers moneyline."
        ),
        "sources": ["MLB-SCHED", "MLB-STAND-AL", "MLB-STAND-NL"],
    },
    {
        "id": "P-BB-02", "fixture": "BB-02", "market": "Match winner (moneyline)",
        "selection": "Milwaukee Brewers to win",
        "text": (
            "Milwaukee's offence is the reason to take the road side in Game 3. The Brewers scored 832 runs across "
            "162 games, 96 more than Tampa Bay, and finished 48-33 away with a plus-214 run differential that was "
            "the best in the majors. Robert Gasser is scheduled against Freddy Peralta, and Tampa Bay's 55-26 home "
            "record is the counter-argument, but the Rays managed a 5-5 close to the season. At close to even money, "
            "the stronger lineup and the deeper season-long margin make Milwaukee the selection on the moneyline."
        ),
        "sources": ["MLB-SCHED", "MLB-STAND-AL", "MLB-STAND-NL"],
    },
    {
        "id": "P-IH-01", "fixture": "IH-02", "market": "Match winner (moneyline)",
        "selection": "Ottawa Senators to win",
        "text": (
            "Ottawa has banked 14 points from eleven games and is 4-2-0 at the Canadian Tire Centre, while the "
            "Rangers have collected just one win in six road games despite a perfect 6-0-0 record at home. New York "
            "has scored 37 goals and conceded 29, but eight of those goals for came in a single home stand and the "
            "road split is 1-4-1. Ottawa's 31 goals for and 30 against suggest a tight game, and home ice plus the "
            "sharp travel split points to the Senators. The selection is Ottawa on the moneyline."
        ),
        "sources": ["NHL-SCHED", "NHL-STAND"],
    },
    {
        "id": "P-IH-02", "fixture": "IH-03", "market": "Match winner (moneyline)",
        "selection": "Nashville Predators to win",
        "text": (
            "Nashville is not the side the standings suggest at first glance: it has conceded 30 goals in nine games, "
            "3.33 per game, while Pittsburgh has shipped 38 in eleven, 3.45 per game, and has lost six of those "
            "eleven. The Penguins' 37 goals for flatter a 4-6-1 record, and only three of their wins have come at "
            "PPG Paints Arena in six home starts. The Predators are 1-1-2 on the road, so this is a narrow call rather than a "
            "confident one, and our fair price of -131 reflects a game that could go either way. The selection is "
            "Nashville on the moneyline."
        ),
        "sources": ["NHL-SCHED", "NHL-STAND"],
    },
    {
        "id": "P-IH-03", "fixture": "IH-04", "market": "Match winner (moneyline)",
        "selection": "Washington Capitals to win",
        "text": (
            "Washington is 4-2-0 at Capital One Arena with a plus-one goal differential, and Buffalo arrives at "
            "1-1-2 on the road having been outscored 37-28 across ten games. The Sabres have lost their last outing "
            "and have allowed four or more goals in four of their ten starts. Both clubs have ten points, but the "
            "Capitals have done it with a steadier defensive record, conceding 29 goals to Buffalo's 37. Home ice "
            "and the shot-suppression edge make Washington the selection on the moneyline."
        ),
        "sources": ["NHL-SCHED", "NHL-STAND"],
    },
    {
        "id": "P-IH-04", "fixture": "IH-05", "market": "Match winner (moneyline)",
        "selection": "Carolina Hurricanes to win",
        "text": (
            "Carolina is the form team of the early season at 8-2-2 with 18 points, a 6-1-1 road record and an "
            "8-1-1 mark over its last ten. The Hurricanes have scored 47 goals and conceded 33, while St. Louis is "
            "5-4-1 and has been outscored on the road despite a 3-0-1 home record. The Blues have won two straight, "
            "but those wins came against sides outside the current top ten, and their 35 goals for is twelve fewer "
            "than Carolina's. The selection is Carolina on the moneyline."
        ),
        "sources": ["NHL-SCHED", "NHL-STAND"],
    },
    {
        "id": "P-IH-05", "fixture": "IH-07", "market": "Match winner (moneyline)",
        "selection": "Tampa Bay Lightning to win",
        "text": (
            "Tampa Bay has allowed 29 goals in ten games, 2.90 per game, against Utah's 36 in eleven, and that "
            "defensive gap is the basis for backing the road side. The Lightning are 7-3-0 overall but "
            "only 2-3-0 away, while Utah is 3-1-0 at the Delta Center and has scored 41 goals, so the risk is real. "
            "The counterweight is that Utah has conceded four or more in four of its eleven starts and lost its last "
            "game. At a fair price of -113 the Lightning's superior goals-against rate is worth the travel risk. "
            "Selection: Tampa Bay moneyline."
        ),
        "sources": ["NHL-SCHED", "NHL-STAND"],
    },
    {
        "id": "P-IH-06", "fixture": "IH-08", "market": "Match winner (moneyline)",
        "selection": "Seattle Kraken to win",
        "text": (
            "Seattle has 15 points from eleven games and has won two straight, scoring 38 goals against 36. "
            "Minnesota is 2-3-2 on the road and has dropped its last game, with 32 goals for and 27 against. The "
            "Wild's defensive numbers are the better of the two, so this is closer than the raw points suggest, "
            "but home ice and Seattle's 3-2-1 record at Climate Pledge Arena edge it. With no official start time "
            "captured for this fixture, treat the price as provisional. The selection is Seattle on the moneyline."
        ),
        "sources": ["NHL-SCHED", "NHL-STAND"],
    },
    {
        "id": "P-TN-01", "fixture": "TN-01", "market": "Match winner (outright, no price)",
        "selection": "Daniil Medvedev to win the Almaty Open final",
        "text": (
            "Medvedev reached the Almaty final by beating third seed Alexander Bublik 6-3, with Bublik retiring, "
            "while Basilashvili needed three sets to see off seventh seed Stefanos Tsitsipas 6-4 6-7(5) 6-3. The "
            "Georgian has therefore spent considerably more time on court across the semi-finals. No official "
            "ranking, head-to-head or serving data was captured for this desk, so no price is offered and the "
            "confidence stays low. The selection is Medvedev to win the title."
        ),
        "sources": ["ATP-SCORES", "ATP-ALMATY"],
    },
    {
        "id": "P-TN-02", "fixture": "TN-02", "market": "Match winner (outright, no price)",
        "selection": "Taylor Fritz to win the Lyon final",
        "text": (
            "Fritz came through his semi-final against Tommy Paul 6-3 7-5 without dropping a set, while Musetti "
            "had to save four match points before beating top seed Flavio Cobolli 4-6 6-2 7-5. That is a heavy "
            "physical and emotional cost to carry into a final 24 hours later. Fritz also holds the higher seeding "
            "of the two, at second against sixth. No official ranking or head-to-head page was captured, so no "
            "price is published. The selection is Fritz to win the Lyon title."
        ),
        "sources": ["ATP-SCORES", "ATP-LYON"],
    },
    {
        "id": "P-BK-01", "fixture": "BK-01", "market": "Match winner (moneyline)",
        "selection": "Charlotte Hornets to win",
        "text": (
            "Charlotte is 1-1 and Miami is 0-2, and the split matters more than the raw records: the Heat have "
            "played both games at home and lost both, while the Hornets won their only road game and lost at home. "
            "Our numbers make Charlotte a 56 per cent favourite, a thin edge rather than a strong one, so this is a "
            "low-confidence call. No official injury report was readable for either roster, which keeps availability "
            "an open risk. Selection: Charlotte Hornets to win."
        ),
        "sources": ["NBA-REF", "NBA-STAND"],
    },
    {
        "id": "P-BK-03", "fixture": "BK-03", "market": "Match winner (moneyline)",
        "selection": "Philadelphia 76ers to win",
        "text": (
            "Philadelphia is 2-0 with one home win and one road win, while Milwaukee has opened 0-2 with a defeat "
            "in each column. That start is the reason our numbers make the 76ers a 60.5 per cent favourite, the "
            "clearest edge on tonight's basketball board. Two games is a small sample, so the edge is treated as "
            "medium rather than high confidence. Official injury status could not be read for this fixture. "
            "Selection: Philadelphia 76ers to win."
        ),
        "sources": ["NBA-REF", "NBA-STAND"],
    },
    {
        "id": "P-BK-04", "fixture": "BK-04", "market": "Match winner (moneyline)",
        "selection": "Atlanta Hawks to win",
        "text": (
            "Both teams are 2-0, but the routes differ: Houston won once at home and once away, while Atlanta won "
            "both of its games on the road and now plays its home opener. Our numbers give the Hawks a 51.7 per cent "
            "edge once home court is applied, which is close to a coin flip and is why this stays low confidence. "
            "Two-game samples are thin, and no official injury report was readable. Selection: Atlanta Hawks to win."
        ),
        "sources": ["NBA-REF", "NBA-STAND"],
    },
    {
        "id": "P-BK-06", "fixture": "BK-06", "market": "Match winner (moneyline)",
        "selection": "Dallas Mavericks to win",
        "text": (
            "Dallas is 1-1 and San Antonio is 0-2, and the Spurs have lost both of their games at home, which is the "
            "wrong pattern to carry into a road trip. The Mavericks' win came away from home, and our numbers make "
            "them a 56 per cent favourite with home court. That is a modest edge rather than a commanding one, and "
            "the official injury report was not readable for this desk. Selection: Dallas Mavericks to win."
        ),
        "sources": ["NBA-REF", "NBA-STAND"],
    },
    {
        "id": "P-BK-08", "fixture": "BK-08", "market": "Match winner (moneyline)",
        "selection": "Phoenix Suns to win",
        "text": (
            "Golden State is 0-2 with one home defeat and one road defeat, while Phoenix is 0-1 after losing its only "
            "game away from home. Both teams are chasing a first win, but the Suns get home court and our numbers "
            "make them a 56 per cent favourite, thin enough to keep the call at low confidence. No official injury "
            "report was available for either roster. Selection: Phoenix Suns to win."
        ),
        "sources": ["NBA-REF", "NBA-STAND"],
    },
]

# ---------------------------------------------------------------------------
# Flagged irregularities — published on the Flagged for Review page.
# ---------------------------------------------------------------------------
FLAGS = [
    {
        "id": "F-01", "severity": "high",
        "title": "The −250 floor and the >70% rule almost never overlap",
        "detail": (
            "A fair price of −250 implies a 71.4% chance. Requiring both 'more than 70%' and a price no shorter "
            "than −250 leaves an effective band of roughly 70.0%–71.4%. Every genuine short-priced favourite on "
            "this slate (Boston at −313, Edmonton at −650 on our numbers) falls outside the requested odds window, "
            "so it cannot be published as a High pick under the brief. This desk therefore treats the odds window "
            "as the eligibility filter and grades confidence from the evidence, and it publishes the conflict "
            "rather than manufacturing in-band High picks."
        ),
        "sources": ["NHL-SCHED"],
    },
    {
        "id": "F-02", "severity": "high",
        "title": "Nine of the fifteen sports carry no price, and three have no fixture at all",
        "detail": (
            "Twelve sports have at least one row. Only ice hockey, basketball and baseball have the official "
            "statistical inputs needed to originate a line, so nine sports are unpriced. Golf's OLBG hub returned "
            "'No tips found.'; the only GAA fixture on 24 October is the shinty-hurling international, which the "
            "brief excludes; Rugby League is between seasons and lists futures only. Darts, cricket, handball, "
            "volleyball, rugby union and greyhounds are listed on OLBG but their official pages were a consent "
            "wall, client-rendered or 404, so those rows are discovery-only. Snooker, tennis and motor racing have "
            "officially confirmed fixtures but no readable form or ranking input, so they are priced nowhere and "
            "get no prediction."
        ),
        "sources": ["GAA-FIX", "WST-MATCHES", "ATP-SCORES", "F1-MEXICO"],
    },
    {
        "id": "F-03", "severity": "medium",
        "title": "OLBG displays times without a timezone",
        "detail": (
            "OLBG event times appear as 'Today 15:15', 'Tomorrow 05:00' and so on, with minute offsets that do not "
            "map cleanly onto any single zone. No OLBG time is converted or presented as UTC on this desk; official "
            "start times are used wherever they exist and are left blank otherwise."
        ),
        "sources": ["NHL-SCHED"],
    },
    {
        "id": "F-04", "severity": "medium",
        "title": "PDC tournament page is behind a consent wall",
        "detail": (
            "https://www.pdc.tv/tournaments/machineseeker-european-championship returned only cookie-consent text "
            "in the fetched body, so the four darts matches listed by OLBG could not be checked against the PDC. "
            "They are published as discovery-only."
        ),
        "sources": [],
    },
    {
        "id": "F-05", "severity": "medium",
        "title": "Two NHL games cannot be priced",
        "detail": (
            "Columbus, Los Angeles, Calgary and Anaheim were absent from the standings excerpts captured, so "
            "Vegas @ Columbus, Los Angeles @ New Jersey and Detroit @ Calgary have only one side's statistical "
            "input and no price is originated. Minnesota @ Seattle has both inputs but no official start time in "
            "the captured excerpt; its price is marked provisional."
        ),
        "sources": ["NHL-STAND"],
    },
    {
        "id": "F-06", "severity": "low",
        "title": "No injury or availability feed captured",
        "detail": (
            "None of the official pages read for this desk published a usable injury report for the fixtures "
            "priced. Predictions therefore make no availability claims at all; where a lineup fact was not captured "
            "it is absent rather than assumed."
        ),
        "sources": ["NHL-SCHED", "MLB-SCHED"],
    },
    {
        "id": "F-07", "severity": "low",
        "title": "MLB series record is a series record, not a season record",
        "detail": (
            "The MLB StatsAPI leagueRecord inside the World Series schedule shows each club's record in the series "
            "(Milwaukee 1-0, Tampa Bay 0-1). Season records used in the write-ups come from the separate regular-"
            "season standings feed and are labelled as such."
        ),
        "sources": ["MLB-SCHED", "MLB-STAND-NL"],
    },
]
