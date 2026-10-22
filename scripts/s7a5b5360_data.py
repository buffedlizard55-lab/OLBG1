"""Session 7a5b5360-olbg1 — T41 fresh matchday desk, 22-26 October 2026.

Every fixture, record and ranking in this module was read from an official page during this
session and is stored with the exact URL that was fetched. Nothing is carried over from another
session's dataset, and nothing is inferred.

Retrieval window: 2026-10-22T00:00Z .. 2026-10-22T01:30Z.
"""

RETRIEVED_UTC = "2026-10-22T01:30:00Z"
WINDOW = "22-26 October 2026"

# ---------------------------------------------------------------------------------------------
# Official sources actually fetched this session
# ---------------------------------------------------------------------------------------------
SOURCES = {
    "mlb_schedule": {
        "name": "MLB official schedule API — World Series, 21-27 Oct 2026",
        "org": "Major League Baseball (statsapi.mlb.com)",
        "url": ("https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-21&endDate=2026-10-27"
                "&fields=dates,date,games,gamePk,gameDate,teams,away,home,team,name,venue,status,"
                "detailedState,seriesDescription,gameNumber"),
        "used_for": ["fixture", "start time", "venue", "participants", "series"],
        "status": "read",
    },
    "mlb_standings": {
        "name": "MLB official standings API — 2026 regular season, National League",
        "org": "Major League Baseball (statsapi.mlb.com)",
        "url": ("https://statsapi.mlb.com/api/v1/standings?leagueId=104&season=2026&standingsTypes=regularSeason"
                "&fields=records,teamRecords,team,name,wins,losses,winningPercentage,divisionRank"),
        "used_for": ["team record input"],
        "status": "read",
    },
    "mlb_standings_al": {
        "name": "MLB official standings API — 2026 regular season, American League",
        "org": "Major League Baseball (statsapi.mlb.com)",
        "url": ("https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsTypes=regularSeason"
                "&fields=records,teamRecords,team,name,wins,losses,winningPercentage,divisionRank"),
        "used_for": ["team record input"],
        "status": "read",
    },
    "nhl_scoreboard": {
        "name": "NHL official scoreboard API — 22-23 Oct 2026 slate (includes both clubs' W-L-OTL records)",
        "org": "National Hockey League (api-web.nhle.com)",
        "url": "https://api-web.nhle.com/v1/scoreboard/2026-10-24",
        "used_for": ["fixture", "start time", "venue", "participants", "team record input"],
        "status": "read",
    },
    "urc_fixtures": {
        "name": "United Rugby Championship — 2026/27 fixtures in full (Round 4 board)",
        "org": "United Rugby Championship",
        "url": "https://www.unitedrugby.com/latest/news/2026-27-fixtures-in-full/",
        "used_for": ["fixture", "kick-off (published local)", "venue", "participants"],
        "status": "read",
    },
    "wst_matches": {
        "name": "World Snooker Tour — BetVictor Northern Ireland Open 2026 match list",
        "org": "World Snooker Tour (wst.tv)",
        "url": "https://www.wst.tv/matches",
        "used_for": ["fixture", "published clock", "round", "completed scores used as form input"],
        "status": "read",
    },
    "wst_rankings": {
        "name": "WST Johnstone's Paint World Rankings (published table, positions 1-36)",
        "org": "World Snooker Tour (wst.tv)",
        "url": "https://www.wst.tv/rankings/abfba8fe-1423-5a2a-a96b-d77e8b413ca8?showLive=false",
        "used_for": ["world ranking input"],
        "status": "read",
    },
    "f1_calendar": {
        "name": "FIA Formula One World Championship 2026 race calendar",
        "org": "Formula 1 (formula1.com)",
        "url": "https://www.formula1.com/en/racing/2026",
        "used_for": ["fixture", "round", "meeting dates"],
        "status": "read",
    },
    "f1_standings": {
        "name": "2026 FIA F1 Drivers' Standings",
        "org": "Formula 1 (formula1.com)",
        "url": "https://www.formula1.com/en/results/2026/drivers",
        "used_for": ["driver points input"],
        "status": "read",
    },
    "f1_usgp": {
        "name": "FORMULA 1 MSC CRUISES UNITED STATES GRAND PRIX 2026 — session schedule and circuit",
        "org": "Formula 1 (formula1.com)",
        "url": "https://www.formula1.com/en/racing/2026/united-states",
        "used_for": ["session times (track local)", "circuit", "lap count"],
        "status": "read",
    },
    "gaa_fixtures": {
        "name": "GAA official fixtures and results board",
        "org": "Gaelic Athletic Association",
        "url": "https://www.gaa.ie/fixtures-results",
        "used_for": ["coverage gap evidence (no gaelic football fixture in window)"],
        "status": "read_no_fixture",
    },
    # Attempted and blocked — recorded so a reader can see the refusal was not a silent gap.
    "pdc_hub": {
        "name": "PDC tournament hub (ET15 — Dutch Darts Championship)",
        "org": "Professional Darts Corporation",
        "url": "https://www.pdc.tv/tournament-hub/10824",
        "used_for": [],
        "status": "blocked_consent_wall",
    },
    "ehfcl_fixtures": {
        "name": "EHF Champions League fixtures route",
        "org": "European Handball Federation",
        "url": "https://www.ehfcl.com/en/men/fixtures-and-results",
        "used_for": [],
        "status": "http_404",
    },
    "urc_table_a": {
        "name": "URC league table route (attempt 1)",
        "org": "United Rugby Championship",
        "url": "https://www.unitedrugby.com/urc/table",
        "used_for": [],
        "status": "http_404",
    },
    "urc_table_b": {
        "name": "URC standings route (attempt 2)",
        "org": "United Rugby Championship",
        "url": "https://www.unitedrugby.com/standings",
        "used_for": [],
        "status": "http_404",
    },
    "icc_fixtures": {
        "name": "ICC fixtures and results board",
        "org": "International Cricket Council",
        "url": "https://www.icc-cricket.com/fixtures-results",
        "used_for": [],
        "status": "client_rendered_empty",
    },
    "euroleague_gc": {
        "name": "EuroLeague Game Center schedule",
        "org": "EuroLeague Basketball",
        "url": "https://www.euroleaguebasketball.net/en/euroleague/game-center/",
        "used_for": [],
        "status": "client_rendered_empty",
    },
    "aflw_fixture": {
        "name": "AFLW fixture board",
        "org": "Australian Football League",
        "url": "https://www.afl.com.au/aflw/fixture",
        "used_for": [],
        "status": "client_rendered_empty",
    },
    "nba_scoreboard": {
        "name": "NBA official live scoreboard JSON",
        "org": "National Basketball Association",
        "url": "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json",
        "used_for": [],
        "status": "http_500",
    },
    "gbgb_fixtures": {
        "name": "GBGB racing fixtures",
        "org": "Greyhound Board of Great Britain",
        "url": "https://www.gbgb.org.uk/racing/fixtures",
        "used_for": [],
        "status": "http_500",
    },
    "wst_rankings_preview": {
        "name": "WST Rankings index (top-11 preview per list)",
        "org": "World Snooker Tour (wst.tv)",
        "url": "https://www.wst.tv/rankings",
        "used_for": ["world ranking input (confirming values)"],
        "status": "read",
    },
}

# ---------------------------------------------------------------------------------------------
# Sports in scope for this desk (brief: every sport except the nine excluded ones)
# ---------------------------------------------------------------------------------------------
EXCLUDED = ["Football / Soccer", "Boxing", "UFC / MMA", "American Football", "Hurling",
            "Horse Racing", "Cycling", "Specials / Entertainment"]

IN_SCOPE = [
    "Tennis", "Basketball", "Golf", "Cricket", "Snooker", "Rugby Union", "Rugby League",
    "Baseball", "Ice Hockey", "Motor Racing", "Darts", "Handball", "Volleyball",
    "Aussie Rules", "eSports", "Gaelic Football", "Greyhounds",
]

# Coverage record for every in-scope sport: what was looked at and what came back.
COVERAGE = {
    "Baseball":      {"fixtures": 3,  "source": ["mlb_schedule", "mlb_standings", "mlb_standings_al"],
                      "state": "verified", "note": "MLB World Series games published by the MLB schedule API."},
    "Ice Hockey":    {"fixtures": 12, "source": ["nhl_scoreboard"], "state": "verified",
                      "note": "Full 12-game NHL slate for 22-23 Oct with both clubs' records in the same payload."},
    "Rugby Union":   {"fixtures": 8,  "source": ["urc_fixtures"], "state": "verified_fixture_only",
                      "note": ("Round 4 board read from the official URC release. No league table could be "
                               "read (two official routes returned 404), so these matches are priced from a "
                               "neutral baseline and confidence is capped at Low.")},
    "Snooker":       {"fixtures": 8,  "source": ["wst_matches", "wst_rankings", "wst_rankings_preview"],
                      "state": "verified", "note": ("Round 3 board plus every completed Round 1/Round 2 score "
                                                    "(used as the form input) and the published world rankings.")},
    "Motor Racing":  {"fixtures": 1,  "source": ["f1_calendar", "f1_standings", "f1_usgp"],
                      "state": "verified", "note": "Round 18, United States Grand Prix, 23-25 Oct 2026, with all 23 drivers' points."},
    "Gaelic Football": {"fixtures": 0, "source": ["gaa_fixtures"], "state": "no_fixture_in_window",
                        "note": ("The official GAA board for 22-26 Oct lists one match, the Shinty-Hurling "
                                 "International (hurling, excluded). No senior inter-county gaelic football "
                                 "fixture is published for this window.")},
    "Darts":         {"fixtures": 0, "source": ["pdc_hub"], "state": "blocked",
                      "note": "pdc.tv served a CookieYes consent interstitial instead of the tournament hub."},
    "Handball":      {"fixtures": 0, "source": ["ehfcl_fixtures"], "state": "blocked",
                      "note": "ehfcl.com/en/men/fixtures-and-results returned HTTP 404."},
    "Cricket":       {"fixtures": 0, "source": ["icc_fixtures"], "state": "client_rendered",
                      "note": "The ICC board renders entirely client-side; the fetch returned skeleton markup only."},
    "Basketball":    {"fixtures": 0, "source": ["euroleague_gc", "nba_scoreboard"], "state": "blocked",
                      "note": "EuroLeague Game Center renders client-side (team list only); the NBA CDN scoreboard returned HTTP 500."},
    "Aussie Rules":  {"fixtures": 0, "source": ["aflw_fixture"], "state": "client_rendered",
                      "note": "afl.com.au/aflw/fixture returned navigation chrome only; the fixture grid is client-rendered."},
    "Greyhounds":    {"fixtures": 0, "source": ["gbgb_fixtures"], "state": "blocked",
                      "note": "gbgb.org.uk/racing/fixtures returned HTTP 500."},
    "Tennis":        {"fixtures": 0, "source": [], "state": "not_attempted_no_dated_board",
                      "note": ("The official draw sheets (protennislive / WTA) publish pairings but no per-match "
                               "dates, and the ATP/WTA calendar pages for this week are client-rendered. A fixture "
                               "cannot be placed on a date from a draw sheet without inferring it, so no tennis "
                               "row is published.")},
    "Rugby League":  {"fixtures": 0, "source": [], "state": "not_attempted_no_static_board",
                      "note": "nrl.com draw routes are client-rendered; no static official board was read this session."},
    "Golf":          {"fixtures": 0, "source": [], "state": "not_attempted_no_static_board",
                      "note": "pgatour.com tee times and leaderboard are client-rendered; no static official board was read."},
    "Volleyball":    {"fixtures": 0, "source": [], "state": "not_attempted_no_static_board",
                      "note": "No CEV fixture board was read this session; the previous desks record the PlusLiga redirect issue."},
    "eSports":       {"fixtures": 0, "source": [], "state": "not_attempted_no_static_board",
                      "note": "lolesports.com match schedules are client-rendered."},
}

# ---------------------------------------------------------------------------------------------
# Fixtures. `inputs` holds only values read on an official page in this session.
# rating is a derived 0-100 transform of the sourced value; the transform is printed on the
# methodology page. A None rating means "no sourced value" and forces a neutral baseline.
# ---------------------------------------------------------------------------------------------
FIXTURES = [
    # ---------------- MLB World Series ----------------
    dict(id="mlb-849805", sport="Baseball", competition="MLB", stage="World Series, game at Milwaukee",
         start_utc="2026-10-24T00:00:00Z", start_published="2026-10-24T00:00:00Z (gameDate in the MLB schedule API)",
         home="Milwaukee Brewers", away="Tampa Bay Rays", venue="American Family Field, Milwaukee",
         neutral=False,
         inputs={"home": {"label": "2026 regular-season record", "value": "103-59 (.636)", "rating": 63.6},
                 "away": {"label": "2026 regular-season record", "value": "98-64 (.605)", "rating": 60.5}},
         sources=["mlb_schedule", "mlb_standings", "mlb_standings_al"],
         flags=["MLB returns the games in the order 849805, 849802, 849804, 849803 for 23, 24, 26 and 27 October — the gamePk sequence is not chronological and no game number is asserted here."]),
    dict(id="mlb-849802", sport="Baseball", competition="MLB", stage="World Series, game at Milwaukee",
         start_utc="2026-10-25T00:00:00Z", start_published="2026-10-25T00:00:00Z (gameDate in the MLB schedule API)",
         home="Milwaukee Brewers", away="Tampa Bay Rays", venue="American Family Field, Milwaukee",
         neutral=False,
         inputs={"home": {"label": "2026 regular-season record", "value": "103-59 (.636)", "rating": 63.6},
                 "away": {"label": "2026 regular-season record", "value": "98-64 (.605)", "rating": 60.5}},
         sources=["mlb_schedule", "mlb_standings", "mlb_standings_al"],
         flags=["No starting pitcher is published for this game on the fetched payload, so the pitching matchup is deliberately not priced."]),
    dict(id="mlb-849804", sport="Baseball", competition="MLB", stage="World Series, game at Tampa Bay",
         start_utc="2026-10-27T00:00:00Z", start_published="2026-10-27T00:00:00Z (gameDate in the MLB schedule API)",
         home="Tampa Bay Rays", away="Milwaukee Brewers", venue="Tropicana Field, St. Petersburg",
         neutral=False,
         inputs={"home": {"label": "2026 regular-season record", "value": "98-64 (.605)", "rating": 60.5},
                 "away": {"label": "2026 regular-season record", "value": "103-59 (.636)", "rating": 63.6}},
         sources=["mlb_schedule", "mlb_standings", "mlb_standings_al"],
         flags=["Scheduled for 27 October 00:00Z, i.e. the evening of 26 October in Tampa Bay — inside the window only on local time."]),
]

# ---------------- NHL, 22-23 October slate ----------------
_NHL = [
    ("2026020154", "2026-10-22T23:00:00Z", "Boston Bruins", "7-2-1", 15, 20, "Nashville Predators", "3-2-3", 8, 16, "TD Garden, Boston"),
    ("2026020155", "2026-10-22T23:00:00Z", "Toronto Maple Leafs", "5-4-2", 12, 22, "New York Rangers", "7-3-1", 15, 22, "Scotiabank Arena, Toronto"),
    ("2026020156", "2026-10-22T23:00:00Z", "Ottawa Senators", "6-3-0", 12, 18, "San Jose Sharks", "5-4-1", 11, 20, "Canadian Tire Centre, Ottawa"),
    ("2026020157", "2026-10-22T23:00:00Z", "New Jersey Devils", "5-4-0", 10, 18, "Anaheim Ducks", "4-5-0", 8, 18, "Prudential Center, Newark"),
    ("2026020158", "2026-10-22T23:00:00Z", "Pittsburgh Penguins", "3-6-1", 7, 20, "Florida Panthers", "5-2-2", 12, 18, "PPG Paints Arena, Pittsburgh"),
    ("2026020159", "2026-10-22T23:30:00Z", "New York Islanders", "5-3-1", 11, 18, "Los Angeles Kings", "1-4-2", 4, 14, "UBS Arena, Elmont"),
    ("2026020160", "2026-10-23T00:00:00Z", "St. Louis Blues", "4-4-1", 9, 18, "Vegas Golden Knights", "8-3-0", 16, 22, "Enterprise Center, St. Louis"),
    ("2026020161", "2026-10-23T00:00:00Z", "Dallas Stars", "5-3-1", 11, 18, "Winnipeg Jets", "4-3-2", 10, 18, "American Airlines Center, Dallas"),
    ("2026020162", "2026-10-23T01:00:00Z", "Calgary Flames", "2-6-0", 4, 16, "Minnesota Wild", "6-2-2", 14, 20, "Scotiabank Saddledome, Calgary"),
    ("2026020163", "2026-10-23T01:00:00Z", "Edmonton Oilers", "7-1-1", 15, 18, "Carolina Hurricanes", "8-2-1", 17, 22, "Rogers Place, Edmonton"),
    ("2026020164", "2026-10-23T02:00:00Z", "Seattle Kraken", "6-3-1", 13, 20, "Utah Mammoth", "7-3-0", 14, 20, "Climate Pledge Arena, Seattle"),
    ("2026020165", "2026-10-23T02:00:00Z", "Vancouver Canucks", "2-8-1", 5, 22, "Detroit Red Wings", "3-3-3", 9, 18, "Rogers Arena, Vancouver"),
]
for gid, start, home, hrec, hpts, hgp, away, arec, apts, agp, venue in _NHL:
    FIXTURES.append(dict(
        id="nhl-" + gid, sport="Ice Hockey", competition="NHL", stage="Regular season",
        start_utc=start, start_published=start + " (startTimeUTC in the NHL scoreboard payload)",
        home=home, away=away, venue=venue, neutral=False,
        inputs={"home": {"label": "2026-27 record and points percentage", "value": f"{hrec} · {hpts}/{hgp} pts = {hpts/hgp:.3f}",
                         "rating": round(100 * hpts / hgp, 1)},
                "away": {"label": "2026-27 record and points percentage", "value": f"{arec} · {apts}/{agp} pts = {apts/agp:.3f}",
                         "rating": round(100 * apts / agp, 1)}},
        sources=["nhl_scoreboard"], flags=[]))

# ---------------- United Rugby Championship, Round 4 ----------------
_URC = [
    ("Cardiff", "Hollywoodbets Sharks", "Cardiff Arms Park, Cardiff", "2026-10-23T18:45:00Z", "Fri 23 Oct, KO 19:45 IRE & UK / 20:45 ITA & SA"),
    ("Connacht", "Zebre Parma", "Dexcom Stadium, Galway", "2026-10-23T18:45:00Z", "Fri 23 Oct, KO 19:45 IRE & UK / 20:45 ITA & SA"),
    ("Edinburgh", "Lions", "Hive Stadium, Edinburgh", "2026-10-23T18:45:00Z", "Fri 23 Oct, KO 19:45 IRE & UK / 20:45 ITA & SA"),
    ("Vodacom Bulls", "Ulster", "Loftus Versfeld, Pretoria", "2026-10-24T11:45:00Z", "Sat 24 Oct, KO 12:45 IRE & UK / 13:45 ITA & SA"),
    ("DHL Stormers", "Scarlets", "DHL Stadium, Cape Town", "2026-10-24T14:00:00Z", "Sat 24 Oct, KO 15:00 IRE & UK / 16:00 ITA & SA"),
    ("Benetton", "Glasgow Warriors", "Stadio Monigo, Treviso", "2026-10-24T14:00:00Z", "Sat 24 Oct, KO 15:00 IRE & UK / 16:00 ITA & SA"),
    ("Leinster", "Munster", "Dublin (venue TBC in the official release)", "2026-10-24T17:00:00Z", "Sat 24 Oct, KO 18:00 IRE & UK / 19:00 ITA & SA"),
    ("Ospreys", "Dragons", "St. Helen's, Swansea", "2026-10-24T18:45:00Z", "Sat 24 Oct, KO 19:45 IRE & UK / 20:45 ITA & SA"),
]
for home, away, venue, start, pub in _URC:
    FIXTURES.append(dict(
        id="urc-" + home.lower().replace(" ", "-") + "-" + away.lower().replace(" ", "-")[:12],
        sport="Rugby Union", competition="United Rugby Championship", stage="Round 4",
        start_utc=start, start_published=pub, home=home, away=away, venue=venue, neutral=False,
        inputs={"home": {"label": "League position", "value": "", "rating": None},
                "away": {"label": "League position", "value": "", "rating": None}},
        sources=["urc_fixtures"],
        flags=["No 2026-27 URC table could be read from the official site (two routes returned 404), so this match is priced from a neutral baseline and confidence is capped at Low.",
               "start_utc is a conversion of the published IRE & UK clock (UTC+1 in October); the source publishes local time only."]))

# ---------------- Snooker: Northern Ireland Open, Round 3 (Thu 22 Oct) ----------------
_WST_RANK = {"Mark Williams": (8, 747400), "Kyren Wilson": (9, 716800), "Elliot Slessor": (23, 329200),
             "Jak Jones": (24, 319300), "Pang Junxu": (29, 272750), "David Gilbert": (34, 221200)}
# frames won / lost across completed Rounds 1-2, read from wst.tv/matches
_WST_FORM = {
    "Matthew Selt": (8, 5), "Sam Craigie": (8, 6), "Kyren Wilson": (8, 2), "Pang Junxu": (8, 5),
    "Anthony McGill": (8, 2), "Mateusz Baranowski": (8, 6), "Elliot Slessor": (8, 1), "Ricky Walden": (8, 4),
    "Mark Williams": (8, 4), "Martin O'Donnell": (8, 5), "David Gilbert": (8, 4), "Ka Wai Cheung": (8, 3),
    "Jordan Brown": (8, 5), "Scott Donaldson": (8, 1), "Jak Jones": (8, 2), "Daniel Wells": (8, 5),
}
_WST_FLAGS = {
    "Elliot Slessor": "Beat He Guoqiang 4-0 (Round 1) and Joe O'Connor 4-1 (Round 2) per wst.tv/matches.",
    "Scott Donaldson": "Beat Wu Yize 4-0 (Round 1) and Noppon Saengkham 4-1 (Round 2) per wst.tv/matches.",
    "Kyren Wilson": "Beat Ben Mertens 4-0 (Round 1) and Thepchaiya Un-Nooh 4-2 (Round 2) per wst.tv/matches.",
    "Anthony McGill": "Beat Stephen Maguire 4-1 (Round 1) and Jack Lisowski 4-1 (Round 2) per wst.tv/matches.",
    "Mark Williams": "Beat Robbie Williams 4-2 (Round 1) and Zhang Anda 4-2 (Round 2) per wst.tv/matches.",
    "Ka Wai Cheung": "Beat Ronnie O'Sullivan 4-3 (Round 1) and Stuart Bingham 4-0 (Round 2) per wst.tv/matches.",
}
_WST_R3 = [
    ("M50", "Kyren Wilson", "Pang Junxu", "08:00"),
    ("M51", "Matthew Selt", "Sam Craigie", "08:00"),
    ("M49", "Anthony McGill", "Mateusz Baranowski", "09:00"),
    ("M52", "Elliot Slessor", "Ricky Walden", "09:00"),
    ("M54", "Mark Williams", "Martin O'Donnell", "14:00"),
    ("M53", "David Gilbert", "Ka Wai Cheung", "14:00"),
    ("M55", "Jak Jones", "Daniel Wells", "15:00"),
    ("M56", "Jordan Brown", "Scott Donaldson", "15:00"),
]
for mid, home, away, clock in _WST_R3:
    def _inp(name):
        w, l = _WST_FORM[name]
        rk = _WST_RANK.get(name)
        return {"label": "Frames won/lost in this event (Rounds 1-2)",
                "value": f"{w}-{l} ({100.0*w/(w+l):.1f}% of frames won)" +
                         (f"; world no. {rk[0]} ({chr(163)}{rk[1]:,})" if rk else "; outside the published top 36"),
                "rating": round(100.0 * w / (w + l), 1),
                "rank": rk[0] if rk else None}
    fl = ["WST publishes a timezone-less clock; start_utc is deliberately left blank rather than converted.",
          "World ranking is blank for players outside the 36 positions served on the WST table this session."]
    for n in (home, away):
        if n in _WST_FLAGS:
            fl.append(_WST_FLAGS[n])
    FIXTURES.append(dict(
        id="wst-" + mid.lower(), sport="Snooker", competition="BetVictor Northern Ireland Open 2026",
        stage="Round 3 (best of 7)", start_utc="", start_published=f"Thu 22 Oct, {clock} (WST clock, no zone published)",
        home=home, away=away, venue="", neutral=False,
        inputs={"home": _inp(home), "away": _inp(away)},
        sources=["wst_matches", "wst_rankings", "wst_rankings_preview"], flags=fl))

# ---------------- Motor racing: F1 United States Grand Prix ----------------
F1_DRIVERS = [
    ("Kimi Antonelli", "Mercedes", 340), ("George Russell", "Mercedes", 238), ("Lewis Hamilton", "Ferrari", 229),
    ("Max Verstappen", "Red Bull Racing", 221), ("Charles Leclerc", "Ferrari", 215), ("Lando Norris", "McLaren", 201),
    ("Oscar Piastri", "McLaren", 138), ("Isack Hadjar", "Red Bull Racing", 97), ("Liam Lawson", "Racing Bulls", 75),
    ("Pierre Gasly", "Alpine", 41), ("Arvid Lindblad", "Racing Bulls", 38), ("Franco Colapinto", "Alpine", 27),
    ("Oliver Bearman", "Haas", 23), ("Nico Hulkenberg", "Audi", 13), ("Gabriel Bortoleto", "Audi", 10),
    ("Esteban Ocon", "Haas", 7), ("Fernando Alonso", "Aston Martin", 7), ("Carlos Sainz", "Williams", 7),
    ("Alexander Albon", "Williams", 5), ("Yuki Tsunoda", "Racing Bulls", 1), ("Lance Stroll", "Aston Martin", 0),
    ("Valtteri Bottas", "Cadillac", 0), ("Sergio Perez", "Cadillac", 0),
]

F1_EVENT = dict(
    id="f1-usgp-2026", sport="Motor Racing", competition="FIA Formula One World Championship",
    stage="Round 18 — United States Grand Prix", start_utc="2026-10-25T21:00:00Z",
    start_published="Sun 25 Oct, race 16:00 track time (F1 publishes session times in track-local time only)",
    home="United States Grand Prix", away="23-driver field", venue="Circuit of The Americas, Austin (56 laps, 5.513 km)",
    neutral=True, kind="field",
    inputs={"home": {"label": "Championship leader", "value": "Kimi Antonelli, 340 points after 17 rounds",
                     "rating": None},
            "away": {"label": "Field", "value": "23 classified drivers and teams on the published standings",
                     "rating": None}}, sources=["f1_calendar", "f1_standings", "f1_usgp"],
    flags=["Race start 21:00Z is derived from the two clocks the official page prints side by side (my time UTC-4, track time UTC-5) — F1 publishes track-local times only.",
           "Points totals are the standings after Round 17 (Singapore); the United States round is Round 18 and has not been run."])

FIELD = [{"name": n, "team": t, "points": p} for n, t, p in F1_DRIVERS]

FIXTURES.append(F1_EVENT)
