"""T2988 desk data: only values actually read from official sources on 2026-10-22.

Every number below is transcribed from a URL listed in SOURCES. Nothing is inferred,
interpolated or copied from another session's files. Where a value was not read it is
absent, and the fixture is published unpriced.
"""
import math

SESSION = "2988bd19-olbg1"
TASK = "T2988"
BUILT = "2026-10-22T21:00:00Z"
READ_WINDOW = "2026-10-22T20:48Z to 2026-10-22T20:59Z"
READ_NOTE = ("The fetch tool does not expose per-request HTTP metadata. These reads all happened inside "
             "one 12-minute window; the order below is the order in which they were issued, not an "
             "invented per-request timestamp.")

# ---------------------------------------------------------------- sources (read this session)
SOURCES = [
    dict(id="nhl-schedule", label="NHL schedule feed, 22 Oct 2026", publisher="NHL",
         url="https://api-web.nhle.com/v1/schedule/2026-10-22",
         what="12 games on 2026-10-22 with game ids, venues and startTimeUTC"),
    dict(id="nhl-team-summary", label="NHL club summary statistics, 2026-27", publisher="NHL",
         url="https://api.nhle.com/stats/rest/en/team/summary?isAggregate=false&isGame=false&sort=teamFullName&dir=ASC&limit=32&cayenneExp=seasonId=20262027%20and%20gameTypeId=2",
         what="games played, W-L-OTL, points, goals for/against, goals per game, power-play % for 30 clubs"),
    dict(id="nhl-team-nsh", label="NHL club summary — Nashville Predators", publisher="NHL",
         url="https://api.nhle.com/stats/rest/en/team/summary?isAggregate=false&isGame=false&cayenneExp=seasonId=20262027%20and%20gameTypeId=2%20and%20teamId=18", what="single-club totals re-read to fix a truncated row"),
    dict(id="nhl-team-wpg", label="NHL club summary — Winnipeg Jets", publisher="NHL",
         url="https://api.nhle.com/stats/rest/en/team/summary?isAggregate=false&isGame=false&cayenneExp=seasonId=20262027%20and%20gameTypeId=2%20and%20teamId=52", what="single-club totals (Winnipeg fell outside the read chunks)"),
    dict(id="nhl-skaters-tor", label="NHL skater summary — Toronto", publisher="NHL",
         url="https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=false&isGame=false&sort=points&dir=DESC&limit=3&cayenneExp=seasonId=20262027%20and%20gameTypeId=2%20and%20teamId=10", what="top three Toronto skaters by points"),
    dict(id="nhl-skaters-nyr", label="NHL skater summary — New York Rangers", publisher="NHL",
         url="https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=false&isGame=false&sort=points&dir=DESC&limit=3&cayenneExp=seasonId=20262027%20and%20gameTypeId=2%20and%20teamId=3", what="top three Rangers skaters by points"),
    dict(id="nhl-skaters-sjs", label="NHL skater summary — San Jose", publisher="NHL",
         url="https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=false&isGame=false&sort=points&dir=DESC&limit=3&cayenneExp=seasonId=20262027%20and%20gameTypeId=2%20and%20teamId=28", what="top three Sharks skaters by points"),
    dict(id="nhl-skaters-bos", label="NHL skater summary — Boston", publisher="NHL",
         url="https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=false&isGame=false&sort=points&dir=DESC&limit=3&cayenneExp=seasonId=20262027%20and%20gameTypeId=2%20and%20teamId=6", what="top three Bruins skaters by points"),
    dict(id="nhl-scoreboard", label="NHL scoreboard feed, 19-20 Oct 2026 results", publisher="NHL",
         url="https://api-web.nhle.com/v1/scoreboard/2026-10-22",
         what="final scores for 19 Oct (ANA 2-5 NYR, COL 2-3 PHI, SJS 1-3 TOR, PIT 4-5 UTA) and 20 Oct (SJS 4-3 MTL, OT)"),
    dict(id="nhl-standings", label="NHL standings, 22 Oct 2026", publisher="NHL",
         url="https://api-web.nhle.com/v1/standings/2026-10-22",
         what="standings snapshot stamped 2026-10-22T20:49:30Z by the feed"),
    dict(id="mlb-schedule", label="MLB schedule, 18-30 Oct 2026", publisher="MLB",
         url="https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-18&endDate=2026-10-30&fields=dates,date,games,gamePk,gameDate,status,detailedState,teams,team,name,score,venue,gameNumber",
         what="World Series fixtures with gamePk, UTC start, venue and status; no game scheduled on 22 Oct"),
    dict(id="mlb-standings", label="MLB standings, 2026 regular season", publisher="MLB",
         url="https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&fields=records,teamRecords,team,name,wins,losses,winningPercentage,runsScored,runsAllowed,gamesPlayed", what="Tampa Bay 98-64, 736 runs scored, 650 allowed in 162 games"),
    dict(id="mlb-mil-hitting", label="MLB Milwaukee hitting, 2026", publisher="MLB",
         url="https://statsapi.mlb.com/api/v1/teams/158/stats?stats=season&group=hitting&season=2026&fields=stats,splits,stat,runs,gamesPlayed,homeRuns,ops", what="Milwaukee 832 runs, 154 home runs, .744 OPS in 162 games"),
    dict(id="mlb-mil-pitching", label="MLB Milwaukee pitching, 2026", publisher="MLB",
         url="https://statsapi.mlb.com/api/v1/teams/158/stats?stats=season&group=pitching&season=2026&fields=stats,splits,stat,runs,gamesPlayed,era", what="Milwaukee 618 runs allowed, 3.51 ERA in 162 games"),
    dict(id="nba-schedule", label="NBA schedule, 22-23 Oct 2026", publisher="NBA",
         url="https://www.nba.com/schedule?date=10%2F22%2F2026",
         what="two games on 22 Oct (CLE at PHI 7:00 PM ET, DEN at OKC 9:30 PM ET) with venues and game ids"),
    dict(id="nba-standings", label="NBA 2026-27 standings", publisher="NBA",
         url="https://www.nba.com/standings",
         what="one-game sample: PHI 1-0, CLE 0-0, OKC 1-0"),
    dict(id="el-standings", label="EuroLeague standings 2026-27", publisher="EuroLeague Basketball",
         url="https://www.euroleaguebasketball.net/en/euroleague/standings/",
         what="all 20 clubs: games played, W-L, points for/against"),
    dict(id="el-game-center", label="EuroLeague game centre", publisher="EuroLeague Basketball",
         url="https://www.euroleaguebasketball.net/en/euroleague/game-center/",
         what="page returned club names and filters only; no fixture rows were rendered, so no EuroLeague fixture is verified"),
    dict(id="olbg-home", label="OLBG home page", publisher="OLBG",
         url="https://www.olbg.com/",
         what="discovery only: featured tips across sports"),
    dict(id="olbg-nhl", label="OLBG ice hockey hub", publisher="OLBG",
         url="https://www.olbg.com/betting-tips/Ice_Hockey/13",
         what="discovery only: 12 NHL events for 22 Oct with community tip shares"),
    dict(id="olbg-mlb", label="OLBG baseball hub", publisher="OLBG",
         url="https://www.olbg.com/betting-tips/Baseball/12",
         what="discovery only: Tampa Bay at Milwaukee, 23 Oct"),
    dict(id="olbg-basketball", label="OLBG basketball hub", publisher="OLBG",
         url="https://www.olbg.com/betting-tips/Basketball/4",
         what="discovery only: NBA and EuroLeague events"),
    dict(id="olbg-tennis", label="OLBG tennis hub", publisher="OLBG",
         url="https://www.olbg.com/betting-tips/Tennis/3",
         what="discovery only: 14 tennis matches listed for 22-23 Oct"),
    dict(id="olbg-cricket", label="OLBG cricket hub", publisher="OLBG",
         url="https://www.olbg.com/betting-tips/Cricket/7",
         what="discovery only: three upcoming cricket matches"),
    dict(id="olbg-snooker", label="OLBG snooker hub", publisher="OLBG",
         url="https://www.olbg.com/betting-tips/Snooker/8",
         what="hub returned 'No tips found'"),
    dict(id="pdc", label="PDC (darts) site", publisher="PDC",
         url="https://www.pdc.tv/",
         what="returned a cookie-consent wall with no fixture content"),
    dict(id="atp-current", label="ATP Tour scores, current", publisher="ATP",
         url="https://www.atptour.com/en/scores/current",
         what="completed round-of-16 matches only; no upcoming fixture list"),
    dict(id="urc", label="United Rugby Championship fixtures URL", publisher="URC",
         url="https://www.unitedrugby.com/fixtures",
         what="returned the site's 404 page"),
]

# ---------------------------------------------------------------- NHL club totals (verified)
# abbrev: (games_played, wins, losses, ot_losses, points, goals_for, goals_against, pp_pct)
NHL_TEAMS = {
    "ANA": ("Anaheim Ducks", 9, 4, 5, 0, 8, 26, 29, 22.6),
    "BOS": ("Boston Bruins", 10, 7, 2, 1, 15, 36, 22, 21.4),
    "CGY": ("Calgary Flames", 8, 2, 6, 0, 4, 17, 37, 21.1),
    "CAR": ("Carolina Hurricanes", 11, 8, 2, 1, 17, 42, 27, 22.7),
    "DAL": ("Dallas Stars", 9, 5, 3, 1, 11, 22, 14, 17.4),
    "DET": ("Detroit Red Wings", 9, 3, 3, 3, 9, 22, 26, 21.9),
    "EDM": ("Edmonton Oilers", 9, 7, 1, 1, 15, 41, 27, 31.0),
    "FLA": ("Florida Panthers", 10, 5, 3, 2, 12, 31, 30, 20.8),
    "LAK": ("Los Angeles Kings", 7, 1, 4, 2, 4, 17, 27, 17.4),
    "MIN": ("Minnesota Wild", 10, 6, 2, 2, 14, 31, 25, 29.0),
    "NSH": ("Nashville Predators", 8, 3, 2, 3, 9, 23, 22, 29.6),
    "NJD": ("New Jersey Devils", 9, 5, 4, 0, 10, 29, 30, 20.0),
    "NYI": ("New York Islanders", 9, 5, 3, 1, 11, 27, 19, 17.9),
    "NYR": ("New York Rangers", 11, 7, 3, 1, 15, 33, 24, 20.6),
    "OTT": ("Ottawa Senators", 10, 7, 3, 0, 14, 27, 24, 13.0),
    "PHI": ("Philadelphia Flyers", 12, 3, 6, 3, 9, 20, 36, 13.9),
    "PIT": ("Pittsburgh Penguins", 10, 3, 6, 1, 7, 32, 37, 23.3),
    "SJS": ("San Jose Sharks", 10, 5, 4, 1, 11, 26, 34, 24.2),
    "SEA": ("Seattle Kraken", 10, 6, 3, 1, 13, 37, 34, 21.9),
    "STL": ("St. Louis Blues", 9, 4, 4, 1, 9, 29, 29, 19.2),
    "TOR": ("Toronto Maple Leafs", 11, 5, 4, 2, 12, 38, 34, 27.5),
    "UTA": ("Utah Mammoth", 10, 7, 3, 0, 14, 38, 31, 36.1),
    "VAN": ("Vancouver Canucks", 11, 2, 8, 1, 5, 33, 51, 21.9),
    "VGK": ("Vegas Golden Knights", 11, 8, 3, 0, 16, 43, 30, 25.0),
    "WSH": ("Washington Capitals", 9, 5, 4, 0, 10, 30, 29, 20.0),
    "WPG": ("Winnipeg Jets", 9, 4, 3, 2, 10, 24, 26, 26.1),
}

# ---------------------------------------------------------------- NHL skaters (verified, top 3)
NHL_SKATERS = {
    "TOR": [
        dict(name="Auston Matthews", pos="C", gp=11, g=8, a=10, pts=18, pm=5, shots=33, ppg=3, src="nhl-skaters-tor"),
        dict(name="William Nylander", pos="R", gp=11, g=6, a=9, pts=15, pm=-2, shots=33, ppg=2, src="nhl-skaters-tor"),
        dict(name="Kirill Marchenko", pos="R", gp=11, g=5, a=6, pts=11, pm=-3, shots=29, ppg=3, src="nhl-skaters-tor"),
    ],
    "NYR": [
        dict(name="Alexis Lafreniere", pos="L", gp=11, g=7, a=6, pts=13, pm=3, shots=22, ppg=2, src="nhl-skaters-nyr"),
        dict(name="Adam Fox", pos="D", gp=11, g=0, a=10, pts=10, pm=0, shots=13, ppg=0, src="nhl-skaters-nyr"),
        dict(name="Mika Zibanejad", pos="C", gp=11, g=2, a=7, pts=9, pm=1, shots=19, ppg=1, src="nhl-skaters-nyr"),
    ],
    "SJS": [
        dict(name="Macklin Celebrini", pos="C", gp=8, g=5, a=9, pts=14, pm=0, shots=37, ppg=2, src="nhl-skaters-sjs"),
        dict(name="Will Smith", pos="C", gp=10, g=3, a=4, pts=7, pm=-5, shots=25, ppg=1, src="nhl-skaters-sjs"),
        dict(name="Tyler Toffoli", pos="C", gp=10, g=3, a=4, pts=7, pm=0, shots=23, ppg=2, src="nhl-skaters-sjs"),
    ],
    "BOS": [
        dict(name="David Pastrnak", pos="R", gp=10, g=4, a=8, pts=12, pm=2, shots=34, ppg=3, src="nhl-skaters-bos"),
        dict(name="Morgan Geekie", pos="C", gp=10, g=1, a=7, pts=8, pm=3, shots=10, ppg=1, src="nhl-skaters-bos"),
        dict(name="Fraser Minten", pos="C", gp=10, g=4, a=4, pts=8, pm=7, shots=26, ppg=0, src="nhl-skaters-bos"),
    ],
}

# recent results actually read in the scoreboard feed
RECENT_RESULTS = [
    dict(date="2026-10-19", text="Anaheim Ducks 2 at New York Rangers 5", src="nhl-scoreboard"),
    dict(date="2026-10-19", text="Colorado Avalanche 2 at Philadelphia Flyers 3", src="nhl-scoreboard"),
    dict(date="2026-10-19", text="San Jose Sharks 1 at Toronto Maple Leafs 3", src="nhl-scoreboard"),
    dict(date="2026-10-19", text="Pittsburgh Penguins 4 at Utah Mammoth 5", src="nhl-scoreboard"),
    dict(date="2026-10-20", text="San Jose Sharks 4 at Montreal Canadiens 3 (overtime)", src="nhl-scoreboard"),
]

# ---------------------------------------------------------------- MLB (verified)
MLB_TEAMS = {
    "TB": ("Tampa Bay Rays", 162, 98, 64, 736, 650),
    "MIL": ("Milwaukee Brewers", 162, None, None, 832, 618),
}

# ---------------------------------------------------------------- EuroLeague (verified records)
EUROLEAGUE = [
    ("Panathinaikos AKTOR Athens", 7, 6, 1, 613, 517),
    ("Fenerbahce Tarfin Istanbul", 6, 5, 1, 501, 447),
    ("Olympiacos Piraeus", 6, 5, 1, 564, 524),
    ("Hapoel IBI Tel Aviv", 7, 5, 2, 630, 601),
    ("Dubai Basketball", 7, 5, 2, 597, 584),
    ("Valencia Basket", 6, 4, 2, 583, 537),
    ("Crvena Zvezda Meridianbet Belgrade", 6, 4, 2, 485, 457),
    ("Real Madrid", 7, 4, 3, 667, 630),
    ("FC Barcelona", 7, 4, 3, 623, 606),
    ("Virtus Bologna", 7, 4, 3, 606, 608),
    ("Partizan Mozzart Bet Belgrade", 6, 3, 3, 466, 471),
    ("Anadolu Efes Istanbul", 7, 3, 4, 581, 590),
    ("Besiktas Istanbul", 7, 3, 4, 634, 644),
    ("Zalgiris Kaunas", 6, 2, 4, 490, 517),
    ("LDLC ASVEL Villeurbanne", 6, 2, 4, 527, 572),
    ("Maccabi Rapyd Tel Aviv", 7, 2, 5, 608, 653),
    ("FC Bayern Munich", 7, 2, 5, 612, 659),
    ("Paris Basketball", 6, 1, 5, 504, 545),
    ("Armani Olimpia Milan", 7, 1, 6, 585, 648),
    ("Kosner Baskonia Vitoria-Gasteiz", 7, 1, 6, 583, 649),
]

# ---------------------------------------------------------------- fixtures
NHL_GAMES = [
    # game id, away, home, start UTC, venue
    (2026020154, "NSH", "BOS", "2026-10-22T23:00:00Z", "TD Garden, Boston"),
    (2026020155, "NYR", "TOR", "2026-10-22T23:00:00Z", "Scotiabank Arena, Toronto"),
    (2026020156, "SJS", "OTT", "2026-10-22T23:00:00Z", "Canadian Tire Centre, Ottawa"),
    (2026020157, "ANA", "NJD", "2026-10-22T23:00:00Z", "Prudential Center, Newark"),
    (2026020158, "FLA", "PIT", "2026-10-22T23:00:00Z", "PPG Paints Arena, Pittsburgh"),
    (2026020159, "LAK", "NYI", "2026-10-22T23:30:00Z", "UBS Arena, Elmont"),
    (2026020160, "VGK", "STL", "2026-10-23T00:00:00Z", "Enterprise Center, St. Louis"),
    (2026020161, "WPG", "DAL", "2026-10-23T00:00:00Z", "American Airlines Center, Dallas"),
    (2026020162, "MIN", "CGY", "2026-10-23T01:00:00Z", "Scotiabank Saddledome, Calgary"),
    (2026020163, "CAR", "EDM", "2026-10-23T01:00:00Z", "Rogers Place, Edmonton"),
    (2026020164, "UTA", "SEA", "2026-10-23T02:00:00Z", "Climate Pledge Arena, Seattle"),
    (2026020165, "DET", "VAN", "2026-10-23T02:00:00Z", "Rogers Arena, Vancouver"),
]

MLB_GAMES = [
    # gamePk, away, home, start UTC, venue, scheduled date in source
    (849805, "TB", "MIL", "2026-10-24T00:00:00Z", "American Family Field, Milwaukee", "2026-10-23"),
    (849802, "TB", "MIL", "2026-10-25T00:00:00Z", "American Family Field, Milwaukee", "2026-10-24"),
    (849804, "MIL", "TB", "2026-10-27T00:00:00Z", "Tropicana Field, St. Petersburg", "2026-10-26"),
    (849803, "MIL", "TB", "2026-10-28T00:00:00Z", "Tropicana Field, St. Petersburg", "2026-10-27"),
    (849799, "MIL", "TB", "2026-10-29T00:00:00Z", "Tropicana Field, St. Petersburg", "2026-10-28"),
    (849801, "TB", "MIL", "2026-10-31T00:00:00Z", "American Family Field, Milwaukee", "2026-10-30"),
]

# OLBG-discovered events (discovery only, no official confirmation this session)
# NBA: fixture officially confirmed on nba.com but intentionally unpriced (see F-2988-02)
NBA_GAMES = [
    ("0022600006", "Cleveland Cavaliers", "Philadelphia 76ers", "2026-10-22T23:00:00Z",
     "Xfinity Mobile Arena, Philadelphia", "7:00 PM ET, 22 Oct"),
    ("0022600007", "Denver Nuggets", "Oklahoma City Thunder", "2026-10-23T01:30:00Z",
     "Paycom Center, Oklahoma City", "9:30 PM ET, 22 Oct"),
]

DISCOVERED = [
    ("basketball", "EuroLeague", "Zalgiris Kaunas", "LDLC ASVEL Villeurbanne", "2026-10-23", "18:00 local (OLBG)", "fixture not confirmed on euroleaguebasketball.net"),
    ("basketball", "EuroLeague", "Olympiacos Piraeus", "Fenerbahce Tarfin Istanbul", "2026-10-23", "19:15 local (OLBG)", "fixture not confirmed on euroleaguebasketball.net"),
    ("basketball", "EuroLeague", "Paris Basketball", "Valencia Basket", "2026-10-23", "19:45 local (OLBG)", "fixture not confirmed on euroleaguebasketball.net"),
    ("cricket", "ODI", "Afghanistan", "Zimbabwe", "2026-10-23", "07:30 local (OLBG)", "no official cricket board page read this session"),
    ("cricket", "T20", "Dolphins", "Garden Route Badgers", "2026-10-23", "12:00 local (OLBG)", "no official cricket board page read this session"),
    ("cricket", "T20I", "New Zealand", "India", "2026-10-24", "03:00 local (OLBG)", "no official cricket board page read this session"),
    ("darts", "PDC", "Ross Smith", "Karel Sedlacek", "2026-10-22", "starting soon (OLBG)", "PDC site returned a consent wall; no official confirmation"),
    ("darts", "PDC", "Ryan Joyce", "Jermaine Wattimena", "2026-10-23", "20 hours (OLBG)", "PDC site returned a consent wall; no official confirmation"),
    ("darts", "PDC", "Jonny Clayton", "Niko Springer", "2026-10-23", "21 hours (OLBG)", "PDC site returned a consent wall; no official confirmation"),
    ("tennis", "ATP/WTA", "Ann Li", "Lilli Tagger", "2026-10-22", "22:30 local (OLBG)", "no official fixture page read"),
    ("tennis", "ATP/WTA", "Talia Gibson", "Ashlyn Krueger", "2026-10-23", "00:00 local (OLBG)", "no official fixture page read"),
    ("tennis", "ATP/WTA", "Leylah Fernandez", "Ekaterina Alexandrova", "2026-10-23", "02:30 local (OLBG)", "no official fixture page read"),
    ("tennis", "ATP/WTA", "Stefanos Tsitsipas", "James Duckworth", "2026-10-23", "04:00 local (OLBG)", "no official fixture page read"),
    ("tennis", "ATP/WTA", "Sara Bejlek", "Marie Bouzkova", "2026-10-23", "01:00 local (OLBG)", "no official fixture page read"),
    ("tennis", "ATP/WTA", "Iva Jovic", "Diana Shnaider", "2026-10-23", "04:00 local (OLBG)", "no official fixture page read"),
    ("tennis", "ATP/WTA", "Daniil Medvedev", "Terence Atmane", "2026-10-23", "05:30 local (OLBG)", "no official fixture page read"),
    ("tennis", "ATP/WTA", "Mary Stoiana", "Katerina Siniakova", "2026-10-23", "01:30 local (OLBG)", "no official fixture page read"),
    ("tennis", "ATP/WTA", "Nikoloz Basilashvili", "Adrian Mannarino", "2026-10-23", "02:30 local (OLBG)", "no official fixture page read"),
    ("tennis", "ATP/WTA", "Katie Boulter", "Antonia Ruzic", "2026-10-23", "03:00 local (OLBG)", "no official fixture page read"),
    ("tennis", "ATP/WTA", "Elena Rybakina", "Katarzyna Kawa", "2026-10-23", "07:00 local (OLBG)", "no official fixture page read"),
    ("tennis", "ATP/WTA", "Corentin Moutet", "Tommy Paul", "2026-10-23", "08:00 local (OLBG)", "no official fixture page read"),
    ("tennis", "ATP/WTA", "Daniel Altmaier", "Taylor Fritz", "2026-10-23", "09:30 local (OLBG)", "no official fixture page read"),
    ("tennis", "ATP/WTA", "Tallon Griekspoor", "Jiri Lehecka", "2026-10-23", "10:00 local (OLBG)", "no official fixture page read"),
]

SPORTS = [
    ("ice-hockey", "Ice hockey"),
    ("baseball", "Baseball"),
    ("basketball", "Basketball"),
    ("tennis", "Tennis"),
    ("cricket", "Cricket"),
    ("darts", "Darts"),
    ("snooker", "Snooker"),
    ("rugby-union", "Rugby union"),
    ("rugby-league", "Rugby league"),
    ("golf", "Golf"),
    ("handball", "Handball"),
    ("volleyball", "Volleyball"),
    ("aussie-rules", "Australian rules"),
    ("esports", "eSports"),
    ("gaelic-football", "Gaelic football"),
    ("greyhounds", "Greyhounds"),
    ("motor-racing", "Motor racing"),
]
SPORT_NAME = dict(SPORTS)

# ---------------------------------------------------------------- model
TIE_HALF = 0.5


def poisson_pmf(total, n=26):
    return [math.exp(-total) * total ** k / math.factorial(k) for k in range(n)]


def nhl_lambdas(away, home):
    ah = NHL_TEAMS[home]
    aa = NHL_TEAMS[away]
    # tuple layout: (name, gp, w, l, otl, pts, gf, ga, pp_pct)
    home_gf, home_ga = ah[6] / ah[1], ah[7] / ah[1]
    away_gf, away_ga = aa[6] / aa[1], aa[7] / aa[1]
    return (home_gf + away_ga) / 2.0, (away_gf + home_ga) / 2.0


def mlb_lambdas(away, home):
    h = MLB_TEAMS[home]
    a = MLB_TEAMS[away]
    return (h[4] / h[1] + a[5] / a[1]) / 2.0, (a[4] / a[1] + h[5] / h[1]) / 2.0


def american(p):
    if p >= 0.5:
        return -100.0 * p / (1.0 - p)
    return 100.0 * (1.0 - p) / p


def two_way(lh, la, n=26):
    dh, da = poisson_pmf(lh, n), poisson_pmf(la, n)
    home_win = sum(dh[i] * da[j] for i in range(n) for j in range(n) if i > j) + TIE_HALF * sum(
        dh[i] * da[i] for i in range(n))
    home_minus_1 = sum(dh[i] * da[j] for i in range(n) for j in range(n) if i - j >= 2)
    home_minus_2 = sum(dh[i] * da[j] for i in range(n) for j in range(n) if i - j >= 3)
    away_minus_1 = sum(dh[i] * da[j] for i in range(n) for j in range(n) if j - i >= 2)
    away_minus_2 = sum(dh[i] * da[j] for i in range(n) for j in range(n) if j - i >= 3)
    out = {
        "home_ml": home_win, "away_ml": 1 - home_win,
        "home_-1.5": home_minus_1, "away_+1.5": 1 - home_minus_1,
        "home_+1.5": 1 - away_minus_1, "away_-1.5": away_minus_1,
        "home_-2.5": home_minus_2, "away_+2.5": 1 - home_minus_2,
        "home_+2.5": 1 - away_minus_2, "away_-2.5": away_minus_2,
    }
    for line in (4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.5):
        over = 1 - sum(dh[i] * da[j] for i in range(n) for j in range(n) if i + j <= int(line))
        out["over_%s" % line] = over
        out["under_%s" % line] = 1 - over
    for line in (1.5, 2.5, 3.5, 4.5):
        ho = 1 - sum(dh[:int(line) + 1])
        ao = 1 - sum(da[:int(line) + 1])
        out["home_over_%s" % line], out["home_under_%s" % line] = ho, 1 - ho
        out["away_over_%s" % line], out["away_under_%s" % line] = ao, 1 - ao
    dh3 = [math.exp(-lh / 3) * (lh / 3) ** k / math.factorial(k) for k in range(9)]
    da3 = [math.exp(-la / 3) * (la / 3) ** k / math.factorial(k) for k in range(9)]
    for line in (1.5, 2.5):
        over = 1 - sum(dh3[i] * da3[j] for i in range(9) for j in range(9) if i + j <= int(line))
        out["p1_over_%s" % line], out["p1_under_%s" % line] = over, 1 - over
    return out


def fair_decimal(p):
    return round(1.0 / p, 4)


def band_note(p):
    if 0.70 < p <= 0.7142857:
        return "inside the strict band (>70% and fair price no shorter than -250)"
    if p > 0.7142857:
        return "above the band: fair price is shorter than -250"
    return "below the band: probability is not above 70%"
