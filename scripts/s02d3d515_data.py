"""Data for the 02d3d515 desk.

Every value below was read from one of the official sources listed in SOURCES
during this session (2026-10-24, 17:05-17:45 UTC).  Nothing is inferred from
memory.  Values that could not be read are left as None and are published as
blank with a flag.

Line origination is our own arithmetic (see s02d3d515_model.py); the input
numbers are official and each one is named in `facts`.
"""

OBSERVED = "2026-10-24T17:45:00Z"

SOURCES = [
    dict(id="nhl-schedule", publisher="NHL", official=True,
         url="https://api-web.nhle.com/v1/schedule/2026-10-24",
         observed="2026-10-24T17:10Z",
         scope="Game IDs, venues, UTC start times and game states for the 12 NHL games on 24 Oct 2026"),
    dict(id="nhl-standings", publisher="NHL", official=True,
         url="https://api-web.nhle.com/v1/standings/2026-10-24",
         observed="2026-10-24T17:12Z",
         scope="2026-27 club records, L10, streaks, goals for/against; standings stamped 17:06:30Z"),
    dict(id="mlb-g2", publisher="MLB", official=True,
         url="https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-10-24&hydrate=team,linescore",
         observed="2026-10-24T17:15Z",
         scope="World Series Game 2, Tampa Bay Rays at Milwaukee Brewers, 2026-10-25T00:00:00Z, American Family Field"),
    dict(id="mlb-g1", publisher="MLB", official=True,
         url="https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-10-23&hydrate=linescore,decisions",
         observed="2026-10-24T17:16Z",
         scope="World Series Game 1 final: Brewers 3-2 Rays; W Misiorowski, L Martinez, SV Megill"),
    dict(id="mlb-standings", publisher="MLB", official=True,
         url="https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsTypes=regularSeason",
         observed="2026-10-24T17:18Z",
         scope="Rays 98-64, AL East champions, 736 runs scored / 650 allowed, run differential +86"),
    dict(id="nba-standings", publisher="NBA", official=True,
         url="https://www.nba.com/standings",
         observed="2026-10-24T17:20Z",
         scope="2026-27 club records and last-10 through 23 Oct 2026 for all 30 clubs"),
    dict(id="nba-games", publisher="NBA", official=True,
         url="https://www.nba.com/games",
         observed="2026-10-24T17:22Z",
         scope="Eight NBA games scheduled for 24 Oct 2026"),
    dict(id="atp-scores", publisher="ATP Tour", official=True,
         url="https://www.atptour.com/en/scores/current",
         observed="2026-10-24T17:24Z",
         scope="Semifinals: Medvedev d. Bublik 6-3 ret.; Basilashvili d. Tsitsipas 6-4 6-7(5) 6-3"),
    dict(id="f1-usgp", publisher="Formula 1", official=True,
         url="https://www.formula1.com/en/racing/2026/united-states",
         observed="2026-10-24T17:26Z",
         scope="US Grand Prix race 25 Oct 16:00 track time; FP2 order Leclerc, Antonelli, Verstappen, Hamilton, Russell"),
    dict(id="top14", publisher="Ligue Nationale de Rugby", official=True,
         url="https://top14.lnr.fr/calendrier-et-resultats",
         observed="2026-10-24T17:28Z",
         scope="Round 7 fixtures, kick-offs and live table positions (Toulon 11th v Pau 2nd; La Rochelle 4th v Bordeaux 3rd)"),
    dict(id="pga-leaderboard", publisher="PGA TOUR", official=True,
         url="https://www.pgatour.com/leaderboard",
         observed="2026-10-24T17:30Z",
         scope="Butterfield Bermuda Championship, Port Royal, 22-25 Oct; round 3 in progress and leaderboard"),
    dict(id="cork-gaa", publisher="Cork GAA", official=True,
         url="https://gaacork.ie/fixtures/",
         observed="2026-10-24T17:32Z",
         scope="25 Oct finals at SuperValu Pairc Ui Chaoimh: Premier JFC Cobh v Canovee 14:00; Premier SFC Nemo Rangers v St Finbarrs 16:00"),
    dict(id="pcb-tri-series", publisher="Pakistan Cricket Board", official=True,
         url="https://www.pcb.com.pk/news-detail/arafat-minhas-6-40-and-59-sink-england-as-pakistan-win-consecutive-games-in-odi-tri-series.html",
         observed="2026-10-24T17:34Z",
         scope="Pakistan beat England in the ODI tri-series; Arafat Minhas took 6-40 and scored 59"),
    dict(id="ehf-cl", publisher="European Handball Federation", official=True,
         url="https://ehfcl.eurohandball.com/men/2026-27/matches/",
         observed="2026-10-24T17:36Z",
         scope="EHF Champions League round fixtures on 28-29 Oct, including Vardar v Melsungen, Magdeburg v Kriens, Kielce v Kolstad"),
    dict(id="wst-matches", publisher="World Snooker Tour", official=True,
         url="https://www.wst.tv/matches/",
         observed="2026-10-24T17:07Z",
         scope="BetVictor Northern Ireland Open 2026 shown as completed (18-19 Oct); no upcoming match listed"),
    dict(id="tauron-liga", publisher="TAURON Liga", official=True,
         url="https://www.tauronliga.pl/games.html",
         observed="2026-10-24T17:38Z",
         scope="Polish women's league results through 18 Oct 2026"),
]

# OLBG is used for discovery only.  It is never used to verify a fact.
OLBG_ROUTES = [
    ("Golf", "https://www.olbg.com/betting-tips/Golf/5", "2026-10-24T17:05Z", "rendered 'No tips found.'"),
    ("Volleyball", "https://www.olbg.com/betting-tips/Volleyball/21", "2026-10-24T17:05Z", "today/tomorrow club fixtures listed"),
    ("Rugby Union", "https://www.olbg.com/betting-tips/Rugby_Union/9", "2026-10-24T17:05Z", "Premiership, Top 14 and URC fixtures listed"),
    ("Cricket", "https://www.olbg.com/betting-tips/Cricket/7", "2026-10-24T17:06Z", "international and domestic fixtures listed"),
    ("Snooker", "https://www.olbg.com/betting-tips/Snooker/8", "2026-10-24T17:06Z", "one fixture listed, already started"),
    ("Darts", "https://www.olbg.com/betting-tips/Darts/15", "2026-10-24T17:06Z", "European Championship matches listed"),
    ("Baseball", "https://www.olbg.com/betting-tips/Baseball/12", "2026-10-24T17:06Z", "one MLB game listed"),
    ("Gaelic Sports", "https://www.olbg.com/betting-tips/Gaelic_Football/25", "2026-10-24T17:07Z", "Cork and Galway club finals listed"),
    ("Greyhounds", "https://www.olbg.com/betting-tips/Greyhounds/28", "2026-10-24T17:07Z", "today's graded cards, several already expired"),
    ("Tennis", "https://www.olbg.com/betting-tips/Tennis/3", "2026-10-24T17:07Z", "ATP and WTA matches listed"),
    ("Motor Racing", "https://www.olbg.com/betting-tips/Motor_Racing/14", "2026-10-24T17:08Z", "USA Grand Prix listed"),
    ("Handball", "https://www.olbg.com/betting-tips/Handball/20", "2026-10-24T17:08Z", "domestic and EHF fixtures listed"),
    ("Ice Hockey", "https://www.olbg.com/betting-tips/Ice_Hockey/13", "2026-10-24T17:08Z", "NHL and Swiss NLA games listed"),
    ("Basketball", "https://www.olbg.com/betting-tips/Basketball/4", "2026-10-24T17:09Z", "eight NBA games plus European leagues"),
    ("Rugby League", "https://www.olbg.com/betting-tips/Rugby_League/10", "2026-10-24T17:09Z", "no upcoming match: 2027 outrights only"),
]

# ---------------------------------------------------------------------------
# Fixtures.  `a` is away / first named, `b` is home / second named.
# facts are verbatim numbers read from the official source named in `source`.
# ---------------------------------------------------------------------------
FIXTURES = [
    dict(
        id="nhl-sjs-bos", sport="ice-hockey", comp="NHL", round="Regular season",
        a="San Jose Sharks", b="Boston Bruins", a_abbr="SJS", b_abbr="BOS",
        start_utc="2026-10-24T23:00:00Z", venue="TD Garden, Boston",
        source="nhl-schedule", standings="nhl-standings",
        facts=dict(
            a_record="6-4-1", a_points="13", a_l10="5-4-1", a_goals_for="33", a_goals_against="37",
            a_road="4-2-1", a_regulation_wins="1", a_streak="W2",
            b_record="8-2-1", b_points="17", b_l10="7-2-1", b_goals_for="42", b_goals_against="22",
            b_home="4-1-0", b_regulation_wins="7", b_streak="W1",
        ),
        injuries=None,
        injury_note="No official NHL injury report was read for this fixture; the field is left blank.",
        game_id="2026020170",
    ),
    dict(
        id="nhl-lak-njd", sport="ice-hockey", comp="NHL", round="Regular season",
        a="Los Angeles Kings", b="New Jersey Devils", a_abbr="LAK", b_abbr="NJD",
        start_utc="2026-10-24T19:30:00Z", venue="Prudential Center, Newark",
        source="nhl-schedule", standings="nhl-standings",
        facts=dict(
            b_record="6-4-0", b_points="12", b_l10="6-4-0", b_goals_for="33", b_goals_against="31",
            b_home="5-2-0", b_regulation_wins="4", b_streak="W2",
        ),
        injuries=None,
        injury_note="Los Angeles season record and both injury lists were not captured; values left blank.",
        game_id="2026020169",
    ),
    dict(
        id="nhl-nyr-ott", sport="ice-hockey", comp="NHL", round="Regular season",
        a="New York Rangers", b="Ottawa Senators", a_abbr="NYR", b_abbr="OTT",
        start_utc="2026-10-24T23:00:00Z", venue="Canadian Tire Centre, Ottawa",
        source="nhl-schedule", standings="nhl-standings",
        facts=dict(
            b_record="7-4-0", b_points="14", b_l10="4-4-2", b_goals_for="31", b_goals_against="30",
            b_home="4-2-0", b_regulation_wins="5", b_streak="L1",
        ),
        injuries=None,
        injury_note="New York Rangers season record and both injury lists were not captured; values left blank.",
        game_id="2026020171",
    ),
    dict(
        id="nhl-vgk-cbj", sport="ice-hockey", comp="NHL", round="Regular season",
        a="Vegas Golden Knights", b="Columbus Blue Jackets", a_abbr="VGK", b_abbr="CBJ",
        start_utc="2026-10-24T23:00:00Z", venue="Nationwide Arena, Columbus",
        source="nhl-schedule", standings="nhl-standings",
        facts=dict(
            a_record="8-4-0", a_points="16", a_l10="7-3-0", a_goals_for="46", a_goals_against="36",
            a_road="3-2-0", a_regulation_wins="6", a_streak="L2",
        ),
        injuries=None,
        injury_note="Columbus season record and both injury lists were not captured; values left blank.",
        game_id="2026020174",
    ),
    dict(
        id="nhl-nsh-pit", sport="ice-hockey", comp="NHL", round="Regular season",
        a="Nashville Predators", b="Pittsburgh Penguins", a_abbr="NSH", b_abbr="PIT",
        start_utc="2026-10-24T23:00:00Z", venue="PPG Paints Arena, Pittsburgh",
        source="nhl-schedule", standings="nhl-standings",
        facts=dict(),
        injuries=None,
        injury_note="Neither club's season record was captured; no line is published for this fixture.",
        game_id="2026020172",
    ),
    dict(
        id="nba-mia-cha", sport="basketball", comp="NBA", round="Regular season",
        a="Miami Heat", b="Charlotte Hornets", a_abbr="MIA", b_abbr="CHA",
        start_utc="2026-10-24T22:00:00Z", venue="Spectrum Center, Charlotte",
        source="nba-games", standings="nba-standings",
        facts=dict(a_record="0-2", a_l10="0-2", a_streak="L2", b_record="1-1", b_l10="1-1", b_streak="L1"),
        injuries=None,
        injury_note="NBA injury reports are published by each club; none was read for this game, so the field is blank.",
    ),
    dict(
        id="nba-bkn-cle", sport="basketball", comp="NBA", round="Regular season",
        a="Brooklyn Nets", b="Cleveland Cavaliers", a_abbr="BKN", b_abbr="CLE",
        start_utc="2026-10-24T23:30:00Z", venue="Rocket Arena, Cleveland",
        source="nba-games", standings="nba-standings",
        facts=dict(a_record="0-1", a_l10="0-1", a_streak="L1", b_record="0-1", b_l10="0-1", b_streak="L1"),
        injuries=None,
        injury_note="No club injury report was read; the field is blank.",
    ),
    dict(
        id="nba-mil-phi", sport="basketball", comp="NBA", round="Regular season",
        a="Milwaukee Bucks", b="Philadelphia 76ers", a_abbr="MIL", b_abbr="PHI",
        start_utc="2026-10-24T23:30:00Z", venue="Xfinity Mobile Arena, Philadelphia",
        source="nba-games", standings="nba-standings",
        facts=dict(a_record="0-2", a_l10="0-2", a_streak="L2", b_record="2-0", b_l10="2-0", b_streak="W2"),
        injuries=None,
        injury_note="No club injury report was read; the field is blank.",
    ),
    dict(
        id="nba-sas-dal", sport="basketball", comp="NBA", round="Regular season",
        a="San Antonio Spurs", b="Dallas Mavericks", a_abbr="SAS", b_abbr="DAL",
        start_utc="2026-10-25T00:00:00Z", venue="American Airlines Center, Dallas",
        source="nba-games", standings="nba-standings",
        facts=dict(a_record="0-2", a_l10="0-2", a_streak="L2", b_record="1-1", b_l10="1-1", b_streak="W1"),
        injuries=None,
        injury_note="No club injury report was read; the field is blank.",
    ),
    dict(
        id="nba-was-chi", sport="basketball", comp="NBA", round="Regular season",
        a="Washington Wizards", b="Chicago Bulls", a_abbr="WAS", b_abbr="CHI",
        start_utc="2026-10-25T00:00:00Z", venue="United Center, Chicago",
        source="nba-games", standings="nba-standings",
        facts=dict(a_record="1-1", a_l10="1-1", a_streak="L1", b_record="1-1", b_l10="1-1", b_streak="W1"),
        injuries=None,
        injury_note="No club injury report was read; the field is blank.",
    ),
    dict(
        id="nba-hou-atl", sport="basketball", comp="NBA", round="Regular season",
        a="Houston Rockets", b="Atlanta Hawks", a_abbr="HOU", b_abbr="ATL",
        start_utc="2026-10-25T00:30:00Z", venue="State Farm Arena, Atlanta",
        source="nba-games", standings="nba-standings",
        facts=dict(a_record="2-0", a_l10="2-0", a_streak="W2", b_record="2-0", b_l10="2-0", b_streak="W2"),
        injuries=None,
        injury_note="No club injury report was read; the field is blank.",
    ),
    dict(
        id="nba-nop-den", sport="basketball", comp="NBA", round="Regular season",
        a="New Orleans Pelicans", b="Denver Nuggets", a_abbr="NOP", b_abbr="DEN",
        start_utc="2026-10-25T02:00:00Z", venue="Ball Arena, Denver",
        source="nba-games", standings="nba-standings",
        facts=dict(a_record="0-2", a_l10="0-2", a_streak="L2", b_record="0-1", b_l10="0-1", b_streak="L1"),
        injuries=None,
        injury_note="No club injury report was read; the field is blank.",
    ),
    dict(
        id="nba-gsw-phx", sport="basketball", comp="NBA", round="Regular season",
        a="Golden State Warriors", b="Phoenix Suns", a_abbr="GSW", b_abbr="PHX",
        start_utc="2026-10-25T03:00:00Z", venue="Footprint Center, Phoenix",
        source="nba-games", standings="nba-standings",
        facts=dict(a_record="0-2", a_l10="0-2", a_streak="L2", b_record="0-1", b_l10="0-1", b_streak="L1"),
        injuries=None,
        injury_note="No club injury report was read; the field is blank.",
    ),
    dict(
        id="mlb-tb-mil", sport="baseball", comp="MLB World Series", round="Game 2 of 7",
        a="Tampa Bay Rays", b="Milwaukee Brewers", a_abbr="TB", b_abbr="MIL",
        start_utc="2026-10-25T00:00:00Z", venue="American Family Field, Milwaukee",
        source="mlb-g2", standings="mlb-standings",
        facts=dict(
            a_record="98-64", a_run_diff="+86", a_runs_scored="736", a_runs_allowed="650",
            a_road="43-38", a_series="Lost Game 1 2-3",
            b_home="Game 1 winner", b_series="Won Game 1 3-2",
        ),
        injuries=None,
        injury_note="No official MLB injury report was read for Game 2; the field is blank.",
    ),
    dict(
        id="atp-final", sport="tennis", comp="ATP Tour", round="Final",
        a="Nikoloz Basilashvili", b="Daniil Medvedev", a_abbr="BAS", b_abbr="MED",
        start_utc="2026-10-25T04:00:00Z", venue="Center Court (venue not captured)",
        source="atp-scores", standings=None,
        facts=dict(
            a_semi="Beat Stefanos Tsitsipas 6-4 6-7(5) 6-3",
            b_semi="Beat Alexander Bublik 6-3 0-0 (Bublik retired)",
        ),
        injuries=None,
        injury_note="Bublik retired in the other semi-final; no ATP withdrawal note for the final was read, so the final's availability field is blank.",
    ),
    dict(
        id="f1-usgp", sport="motor-racing", comp="Formula 1", round="United States Grand Prix",
        a="United States Grand Prix", b="", a_abbr="", b_abbr="",
        start_utc="2026-10-25T21:00:00Z", venue="Circuit of the Americas, Austin",
        source="f1-usgp", standings=None,
        facts=dict(
            race="25 Oct 16:00 track time (US CDT), 56 laps, 308.432 km",
            fp2="Leclerc 1:35.291; Antonelli +0.042; Verstappen +0.189; Hamilton +0.615; Russell +0.744",
        ),
        injuries=None,
        injury_note="No official driver-availability statement was read; the field is blank.",
    ),
    dict(
        id="pga-bermuda", sport="golf", comp="PGA TOUR", round="Butterfield Bermuda Championship",
        a="Butterfield Bermuda Championship", b="", a_abbr="", b_abbr="",
        start_utc=None, start_label="25 Oct · final round (tee times not captured)", venue="Port Royal Golf Course, Southampton",
        source="pga-leaderboard", standings=None,
        facts=dict(
            event="22-25 Oct 2026, round 3 in progress at the time of reading",
            leader="Austin Smotherman -16 through 10 holes of round 3",
            chasing="Chandler Blanchet -15; Chris Kirk, Ben Silverman and Seamus Power -14",
        ),
        injuries=None,
        injury_note="No official withdrawal list was read; the field is blank.",
    ),
    dict(
        id="ru-toulon-pau", sport="rugby-union", comp="Top 14", round="Round 7",
        a="RC Toulon", b="Section Paloise", a_abbr="Toulon", b_abbr="Pau",
        start_utc="2026-10-24T19:00:00Z", venue="Stade Mayol, Toulon",
        source="top14", standings="top14",
        facts=dict(a_table="11th", b_table="2nd",
                   context="Round 7; Toulouse top the table after beating Perpignan 38-33; kick-off 21:00 French time"),
        injuries=None,
        injury_note="No official Top 14 injury list was read; the field is blank.",
    ),
    dict(
        id="ru-larochelle-bordeaux", sport="rugby-union", comp="Top 14", round="Round 7",
        a="Stade Rochelais", b="Union Bordeaux-Begles", a_abbr="La Rochelle", b_abbr="Bordeaux",
        start_utc="2026-10-25T19:05:00Z", venue="Stade Marcel-Deflandre, La Rochelle",
        source="top14", standings="top14",
        facts=dict(a_table="4th", b_table="3rd",
                   context="Round 7; both clubs in the top four before kick-off; kick-off 21:05 French time"),
        injuries=None,
        injury_note="No official Top 14 injury list was read; the field is blank.",
    ),
    dict(
        id="cricket-pak-eng", sport="cricket", comp="ODI tri-series", round="ODI",
        a="Pakistan", b="England", a_abbr="PAK", b_abbr="ENG",
        start_utc="2026-10-25T03:00:00Z", venue="Venue not captured",
        source="pcb-tri-series", standings=None,
        facts=dict(
            context="Pakistan won consecutive tri-series games, including the match reported on 20 Oct",
            performance="Arafat Minhas took 6-40 and scored 59 in that win",
            margin="Pakistan's biggest ODI win over England by runs since 2005 (PCB)",
        ),
        injuries=None,
        injury_note="No official squad or injury statement was read for this fixture; the field is blank.",
    ),
    dict(
        id="gaa-nemo-barrs", sport="gaelic-football", comp="Cork Premier SFC", round="Final",
        a="Nemo Rangers", b="St Finbarrs", a_abbr="Nemo", b_abbr="Barrs",
        start_utc="2026-10-25T15:00:00Z", venue="SuperValu Pairc Ui Chaoimh",
        source="cork-gaa", standings=None,
        facts=dict(round="Final", venue="SuperValu Pairc Ui Chaoimh", referee="David Murnane"),
        injuries=None,
        injury_note="No official team-sheet or injury list was read; the field is blank.",
    ),
    dict(
        id="gaa-cobh-canovee", sport="gaelic-football", comp="Cork Premier JFC", round="Final",
        a="Cobh", b="Canovee", a_abbr="Cobh", b_abbr="Canovee",
        start_utc="2026-10-25T13:00:00Z", venue="SuperValu Pairc Ui Chaoimh",
        source="cork-gaa", standings=None,
        facts=dict(round="Final", venue="SuperValu Pairc Ui Chaoimh", referee="Niall Hayes"),
        injuries=None,
        injury_note="No official team-sheet or injury list was read; the field is blank.",
    ),
    dict(
        id="ehf-vardar-melsungen", sport="handball", comp="EHF Champions League", round="Group phase",
        a="HC Vardar 1961", b="MT Melsungen", a_abbr="Vardar", b_abbr="Melsungen",
        start_utc="2026-10-28T17:45:00Z", venue="Venue not captured",
        source="ehf-cl", standings=None, facts=dict(), injuries=None,
        injury_note="No group standings or injury list were captured; no line is published.",
    ),
    dict(
        id="ehf-magdeburg-kriens", sport="handball", comp="EHF Champions League", round="Group phase",
        a="SC Magdeburg", b="HC Kriens-Luzern", a_abbr="Magdeburg", b_abbr="Kriens",
        start_utc="2026-10-28T19:45:00Z", venue="Venue not captured",
        source="ehf-cl", standings=None, facts=dict(), injuries=None,
        injury_note="No group standings or injury list were captured; no line is published.",
    ),
    dict(
        id="ehf-kielce-kolstad", sport="handball", comp="EHF Champions League", round="Group phase",
        a="Industria Kielce", b="Kolstad Handball", a_abbr="Kielce", b_abbr="Kolstad",
        start_utc="2026-10-28T19:45:00Z", venue="Venue not captured",
        source="ehf-cl", standings=None, facts=dict(), injuries=None,
        injury_note="No group standings or injury list were captured; no line is published.",
    ),
    dict(
        id="ehf-gog-sporting", sport="handball", comp="EHF Champions League", round="Group phase",
        a="GOG", b="Sporting CP", a_abbr="GOG", b_abbr="Sporting",
        start_utc="2026-10-29T17:45:00Z", venue="Venue not captured",
        source="ehf-cl", standings=None, facts=dict(), injuries=None,
        injury_note="No group standings or injury list were captured; no line is published.",
    ),
    dict(
        id="ehf-fuchse-partizan", sport="handball", comp="EHF Champions League", round="Group phase",
        a="Fuchse Berlin", b="RK Partizan", a_abbr="Fuchse", b_abbr="Partizan",
        start_utc="2026-10-29T17:45:00Z", venue="Venue not captured",
        source="ehf-cl", standings=None, facts=dict(), injuries=None,
        injury_note="No group standings or injury list were captured; no line is published.",
    ),
]

# ---------------------------------------------------------------------------
# Our selections.  `prob` is our own estimated win probability for that
# selection (zero-vig); `price` is the fair American price derived from it.
# confidence is ours; `why` is a one-line reason shown in tables.
# `prediction` is the written analysis, >=30 words, unique per row.
# ---------------------------------------------------------------------------
PICKS = [
    dict(
        fixture="nhl-sjs-bos", market="Match total", selection="Under 6.5 goals",
        prob=0.612, confidence="high",
        why="Both clubs' goals for and against produce a 6.09-goal expectation, below the 6.5 line.",
        prediction=(
            "Boston have scored 42 and conceded 22 in 11 games, while San Jose have scored 33 and "
            "conceded 37 in the same number, and the two attacks have not been converting at a rate "
            "that supports a seven-goal night. The Bruins have allowed only six goals across five "
            "home games, and the Sharks have managed just one regulation win all season. Take Under "
            "6.5 goals at TD Garden."
        ),
    ),
    dict(
        fixture="nhl-sjs-bos", market="Match winner", selection="Boston Bruins",
        prob=0.708, confidence="medium",
        why="Boston are 8-2-1 with a 7-2-1 run and a 42-22 goal split; San Jose have one regulation win.",
        prediction=(
            "Boston bring an 8-2-1 record and a 42-22 goal difference into a home game they have "
            "controlled all month, winning four of five at TD Garden. San Jose are 6-4-1 but have "
            "won only one game in regulation and have been outscored 37-33, so their record leans on "
            "overtime and the shootout. Back the Bruins to win in regulation or better."
        ),
    ),
    dict(
        fixture="nba-mia-cha", market="Match winner", selection="Charlotte Hornets",
        prob=0.596, confidence="medium",
        why="Charlotte are 1-1 against Miami's 0-2 start, and the model gives the home side the edge.",
        prediction=(
            "Miami arrive 0-2 after dropping both opening games, while Charlotte split their first "
            "two and come in off a one-point defeat. The Hornets hold home court and a marginally "
            "better early record, and the Heat have yet to show scoring consistency in the young "
            "season. Take Charlotte on the money line, with the small sample size noted."
        ),
    ),
    dict(
        fixture="nba-bkn-cle", market="Match winner", selection="Cleveland Cavaliers",
        prob=0.555, confidence="low",
        why="Both clubs are 0-1; home advantage separates two identical records.",
        prediction=(
            "Both teams are 0-1, so this is a home-court call rather than a form call. Cleveland "
            "lost their opener on the road and return to Rocket Arena, where the crowd and travel "
            "edge sit with them. Brooklyn also lost their first game and are on the road again. "
            "Backing Cleveland in a near-even matchup is the percentage play."
        ),
    ),
    dict(
        fixture="nba-mil-phi", market="Match winner", selection="Philadelphia 76ers",
        prob=0.798, confidence="medium",
        why="Philadelphia are 2-0 at home against a 0-2 Milwaukee side; the fair price is shorter than -250.",
        prediction=(
            "Philadelphia have opened 2-0 and are at home, while Milwaukee are 0-2 and have lost "
            "both games by a combined margin that leaves them chasing this one from tip-off. The "
            "76ers' early record is built on defence, and the Bucks have yet to find a settled "
            "rotation. The call is Philadelphia, though the fair price sits outside the "
            "requested window."
        ),
    ),
    dict(
        fixture="nba-sas-dal", market="Match winner", selection="Dallas Mavericks",
        prob=0.596, confidence="medium",
        why="Dallas are 1-1 at home against a San Antonio side that has started 0-2.",
        prediction=(
            "San Antonio have lost both games and travel to a Dallas team that split its opening "
            "pair and won its most recent outing. The Mavericks have home court and the better "
            "early record, and the Spurs have yet to get a win on the board. Dallas are the "
            "selection, with the caveat that two-game samples are thin."
        ),
    ),
    dict(
        fixture="nba-was-chi", market="Match winner", selection="Chicago Bulls",
        prob=0.552, confidence="low",
        why="Both clubs are 1-1; Chicago's home floor is the only separator in the data.",
        prediction=(
            "Washington and Chicago are both 1-1 and both won their most recent game, so this "
            "comes down to venue. Chicago are at the United Center, where they have already "
            "played once this season, and Washington are on the road. With nothing between the "
            "records, back the Bulls on the money line at home."
        ),
    ),
    dict(
        fixture="nba-hou-atl", market="Match winner", selection="Atlanta Hawks",
        prob=0.552, confidence="low",
        why="Two 2-0 teams meet; home advantage is the only differentiator we can support.",
        prediction=(
            "Both Houston and Atlanta are 2-0, so there is no form edge to price. Atlanta are at "
            "home and have won both games by double digits, while Houston's perfect start came "
            "without a road test of this kind. The Hawks on the money line is a home-court call "
            "in a matchup the records cannot separate."
        ),
    ),
    dict(
        fixture="nba-nop-den", market="Match winner", selection="Denver Nuggets",
        prob=0.596, confidence="medium",
        why="Denver are 0-1 at altitude; New Orleans have started 0-2 and are on the road.",
        prediction=(
            "New Orleans are 0-2 and now travel to Denver, where the altitude and the Nuggets' "
            "frontcourt make life difficult for a team still searching for its first win. Denver "
            "lost their opener but were competitive, and Ball Arena is a genuine home edge. Take "
            "the Nuggets on the money line."
        ),
    ),
    dict(
        fixture="nba-gsw-phx", market="Match winner", selection="Phoenix Suns",
        prob=0.596, confidence="medium",
        why="Phoenix are 0-1 at home against a Golden State side that has opened 0-2.",
        prediction=(
            "Golden State have lost both games and are on the road for the third time in a week, "
            "while Phoenix dropped their opener and return home with a point to prove. The Suns "
            "have the better early defensive numbers of the two and the home floor. Take Phoenix, "
            "priced as a marginal favourite rather than a lock."
        ),
    ),
    dict(
        fixture="mlb-tb-mil", market="Match winner", selection="Milwaukee Brewers",
        prob=0.575, confidence="medium",
        why="Milwaukee won Game 1 3-2 at home and hold home field again, though the season record was not captured.",
        prediction=(
            "Milwaukee took Game 1 of the World Series 3-2 at American Family Field, with Jacob "
            "Misiorowski earning the win and Trevor Megill closing it out. Tampa Bay had a 98-64 "
            "regular season and a +86 run differential, but they are 0-1 in the series and their "
            "road record was 43-38. Home field and the Game 1 result point to Milwaukee, though the "
            "Brewers' own season record was not captured."
        ),
    ),
    dict(
        fixture="mlb-tb-mil", market="Match total", selection="Under 8.5 runs",
        prob=0.545, confidence="low",
        why="Game 1 produced five runs and both bullpens closed cleanly; the line is set above that.",
        prediction=(
            "Game 1 finished 3-2, with Milwaukee scoring twice in the first inning and once in the "
            "seventh, and neither side reached five runs. Tampa Bay allowed 650 runs across the "
            "regular season, one of the better staff totals in the league, and the Brewers' bullpen "
            "closed the opener without conceding. Under 8.5 runs is the lean, offered as a low-tier "
            "call because Milwaukee's season run data was not captured."
        ),
    ),
    dict(
        fixture="atp-final", market="Match winner", selection="Daniil Medvedev",
        prob=0.640, confidence="medium",
        why="Medvedev reached the final in straight sets; Basilashvili needed three sets and over two hours.",
        prediction=(
            "Medvedev advanced when Alexander Bublik retired after losing the first set 6-3, leaving "
            "him with far less court time than Basilashvili, who needed 6-4 6-7(5) 6-3 and more than "
            "two hours to beat Stefanos Tsitsipas. Freshness and the shorter route through the draw "
            "favour the Russian. Back Medvedev to win the final, with the caveat that no head-to-head "
            "record was captured."
        ),
    ),
    dict(
        fixture="f1-usgp", market="Race winner", selection="Charles Leclerc",
        prob=0.260, confidence="medium",
        why="Leclerc set the fastest FP2 time, 0.042s clear of Antonelli and 0.189s clear of Verstappen.",
        prediction=(
            "Leclerc topped second practice at Circuit of the Americas with a 1:35.291, ahead of "
            "Antonelli by 0.042s and Verstappen by 0.189s, and he also led first practice. The "
            "Ferrari has looked comfortable through the high-speed section, and track position "
            "matters at a circuit where the run to Turn 1 decides a lot. Leclerc to win the United "
            "States Grand Prix is the selection."
        ),
    ),
    dict(
        fixture="f1-usgp", market="Podium finish", selection="Max Verstappen",
        prob=0.620, confidence="medium",
        why="Verstappen was third in FP2, within two tenths of the pace, and has won at COTA before.",
        prediction=(
            "Verstappen ended second practice third, 0.189s off Leclerc and ahead of both Hamilton "
            "and Russell, which puts him firmly in the leading group at a circuit he knows well. "
            "Red Bull's long-run pace has been competitive across the weekend, and overtaking is "
            "possible at COTA with the long back straight. Verstappen for a podium finish is the "
            "call."
        ),
    ),
    dict(
        fixture="f1-usgp", market="Top 6 finish", selection="Kimi Antonelli",
        prob=0.640, confidence="low",
        why="Antonelli was second in FP2, 0.042s off the pace, in only his first full season.",
        prediction=(
            "Antonelli put the Mercedes second on the FP2 sheet, just 0.042s behind Leclerc and "
            "ahead of Verstappen, Hamilton and Russell. A single lap in practice is not a race "
            "guarantee, but the pace is real and a top-six finish is a modest ask for a car that "
            "has been in the top four all weekend. Antonelli for a top-six finish, low tier."
        ),
    ),
    dict(
        fixture="pga-bermuda", market="Outright winner", selection="Austin Smotherman",
        prob=0.300, confidence="medium",
        why="Smotherman leads by one at -16 through 10 holes of round 3, with the final round on Sunday.",
        prediction=(
            "Smotherman leads the Butterfield Bermuda Championship at 16 under through ten holes of "
            "the third round, one clear of Chandler Blanchet at 15 under and two ahead of Chris Kirk, "
            "Ben Silverman and Seamus Power. Port Royal is a short, exposed coastal course where wind "
            "can compress a leaderboard quickly, so the margin is not comfortable. Smotherman to "
            "win is the call, with the caveat that the third round was still in progress."
        ),
    ),
    dict(
        fixture="pga-bermuda", market="Top 10 finish", selection="Seamus Power",
        prob=0.560, confidence="low",
        why="Power is tied third at -14 through eight holes of round 3 and has been inside the top five all week.",
        prediction=(
            "Power sits at 14 under through eight holes of the third round, tied third and two "
            "shots off the lead, after rounds of 66 and 64. The Irishman has been one of the most "
            "consistent ball-strikers in the field and has already banked two low rounds on a course "
            "that rewards accuracy off the tee. Power for a top-ten finish is the selection at a "
            "modest price."
        ),
    ),
    dict(
        fixture="ru-toulon-pau", market="Match winner", selection="Section Paloise",
        prob=0.548, confidence="medium",
        why="Pau sit second in the Top 14 table; Toulon are 11th after six rounds.",
        prediction=(
            "Pau arrive second in the Top 14 table while Toulon sit 11th, a gap of nine places after "
            "six rounds. Toulon have home advantage at Stade Mayol, which is worth a lot in this "
            "league, but their league position reflects an inconsistent start and Pau have been the "
            "more reliable side. Pau to win is the call, priced as a marginal underdog rather than a "
            "confident one."
        ),
    ),
    dict(
        fixture="ru-larochelle-bordeaux", market="Match winner", selection="Union Bordeaux-Begles",
        prob=0.520, confidence="low",
        why="Bordeaux are third, one place above La Rochelle, but travel to Stade Marcel-Deflandre.",
        prediction=(
            "Bordeaux sit third and La Rochelle fourth, so the table gives Bordeaux the narrowest of "
            "edges, but the match is at Stade Marcel-Deflandre, one of the hardest away trips in "
            "France. La Rochelle's home record is the reason the price is close. Bordeaux to win is "
            "a low-tier call because the venue arguably outweighs a one-place table gap."
        ),
    ),
    dict(
        fixture="cricket-pak-eng", market="Match winner", selection="Pakistan",
        prob=0.580, confidence="medium",
        why="Pakistan have won consecutive tri-series games, including a record-margin win over England.",
        prediction=(
            "Pakistan have won back-to-back matches in the ODI tri-series, and the most recent "
            "meeting with England was their biggest win over them by runs since 2005. Arafat Minhas "
            "took 6-40 and made 59 in that game, giving Pakistan both a frontline wicket-taker and "
            "lower-order runs. Pakistan to win is the selection, with the venue and toss not captured."
        ),
    ),
]

# Rows we could not price.  Published as blanks on the site with a reason.
WITHHELD = [
    ("nhl-lak-njd", "Los Angeles season record not captured", "Only New Jersey's record was read; a two-sided line needs both."),
    ("nhl-nyr-ott", "New York Rangers record not captured", "Only Ottawa's record was read; no opponent side to price against."),
    ("nhl-vgk-cbj", "Columbus record not captured", "Only Vegas's record was read."),
    ("nhl-nsh-pit", "Neither record captured", "No official 2026-27 record read for either club."),
    ("ehf-vardar-melsungen", "No group standings captured", "EHF fixture confirmed, but no form data was read."),
    ("ehf-magdeburg-kriens", "No group standings captured", "EHF fixture confirmed, but no form data was read."),
    ("ehf-kielce-kolstad", "No group standings captured", "EHF fixture confirmed, but no form data was read."),
    ("ehf-gog-sporting", "No group standings captured", "EHF fixture confirmed, but no form data was read."),
    ("ehf-fuchse-partizan", "No group standings captured", "EHF fixture confirmed, but no form data was read."),
    ("gaa-nemo-barrs", "No official form captured", "Cork GAA confirms the final but publishes no league table for the knockout."),
    ("gaa-cobh-canovee", "No official form captured", "Cork GAA confirms the final but publishes no league table for the knockout."),
]

SPORTS = [
    ("ice-hockey", "Ice Hockey", "NHL.com · api-web.nhle.com"),
    ("basketball", "Basketball", "NBA.com"),
    ("baseball", "Baseball", "MLB.com · statsapi.mlb.com"),
    ("cricket", "Cricket", "Pakistan Cricket Board"),
    ("darts", "Darts", "PDC"),
    ("gaelic-football", "Gaelic Sports", "Cork GAA"),
    ("golf", "Golf", "PGA TOUR"),
    ("greyhounds", "Greyhounds", "GBGB"),
    ("handball", "Handball", "EHF Champions League"),
    ("motor-racing", "Motor Racing", "Formula 1"),
    ("rugby-league", "Rugby League", "RFL / NRL"),
    ("rugby-union", "Rugby Union", "LNR Top 14"),
    ("snooker", "Snooker", "World Snooker Tour"),
    ("tennis", "Tennis", "ATP Tour"),
    ("volleyball", "Volleyball", "TAURON Liga"),
]

# Items where the official source could not settle the question.  These are
# published, with links, on the Flagged for Review page.
FLAGS = [
    dict(id="F-01", severity="high", sport="Rugby League", title="No upcoming Rugby League match exists on OLBG",
         detail="OLBG's Rugby League hub lists only 2027 outright markets (State of Origin, Super League Grand Final, NRL Grand Final). No 2026 match market is open, so no line or pick can be originated. The sport is published as a gap rather than filled.",
         link="https://www.olbg.com/betting-tips/Rugby_League/10", link_label="OLBG Rugby League hub (discovery)"),
    dict(id="F-02", severity="high", sport="Snooker", title="OLBG's only Snooker listing had already started",
         detail="The single Snooker row (Mark Williams v Jak Jones, 14:05) was listed for a start earlier than the read time, and WST's official match page shows the Northern Ireland Open as completed on 18-19 October. No future Snooker match could be confirmed, so none is published.",
         link="https://www.wst.tv/matches/", link_label="World Snooker Tour matches"),
    dict(id="F-03", severity="high", sport="Greyhounds", title="Greyhound entries on the hub were expired or unverifiable",
         detail="The greyhound hub lists today's graded races, several already marked Expired, and no official GBGB card was read for any of them. Publishing a pick without an official card would be invention, so the sport is carried as a gap.",
         link="https://www.olbg.com/betting-tips/Greyhounds/28", link_label="OLBG Greyhounds hub (discovery)"),
    dict(id="F-04", severity="medium", sport="Golf", title="OLBG renders 'No tips found' on the Golf hub",
         detail="At 17:05Z the Golf hub returned an empty tips table although the PGA TOUR event is live. Golf picks here are built from the official PGA TOUR leaderboard, not from OLBG, and the OLBG gap is recorded.",
         link="https://www.olbg.com/betting-tips/Golf/5", link_label="OLBG Golf hub (discovery)"),
    dict(id="F-05", severity="medium", sport="Darts", title="PDC pages are cookie-walled to this reader",
         detail="pdc.tv returns a consent wall instead of match content, so the European Championship order of play could not be read from the governing body. Darts is carried as a gap rather than priced from the OLBG listing alone.",
         link="https://www.pdc.tv/tournaments", link_label="PDC tournaments"),
    dict(id="F-06", severity="medium", sport="Tennis", title="WTA pages did not render match data",
         detail="wtatennis.com returned navigation and notification text with no draw or order of play, so the WTA matches listed by OLBG could not be confirmed. Only the ATP final, whose two semi-finals were read on atptour.com, is priced.",
         link="https://www.wtatennis.com/scores", link_label="WTA scores"),
    dict(id="F-07", severity="medium", sport="Volleyball", title="No official volleyball fixture matching an OLBG match was read",
         detail="The Italian league site renders results through a script this reader cannot execute, and the Polish league page returned women's TAURON Liga results that do not match the OLBG fixtures. Volleyball is carried as a gap.",
         link="https://www.tauronliga.pl/games.html", link_label="TAURON Liga fixtures"),
    dict(id="F-08", severity="low", sport="All", title="Start times for US sports come from the OLBG display",
         detail="NHL start times are taken from api-web.nhle.com and MLB's from statsapi.mlb.com. NBA start times are converted from the US Eastern times displayed on OLBG (UTC+4 in October); NBA.com confirms eight games on 24 October but its fixture list did not render, so the individual times are flagged as OLBG-sourced.",
         link="https://www.nba.com/games", link_label="NBA games (8 scheduled 24 Oct)"),
    dict(id="F-09", severity="low", sport="All", title="Several season records could not be captured",
         detail="NHL standings were read as paginated JSON; clubs beyond the pages read (Los Angeles, New York Rangers, Columbus, Nashville, Pittsburgh) have blank records rather than estimates, and their fixtures carry no line.",
         link="https://api-web.nhle.com/v1/standings/2026-10-24", link_label="NHL standings"),
    dict(id="F-10", severity="low", sport="All", title="Injury and availability fields are blank, not guessed",
         detail="No official injury report was read for any published fixture. Every injury cell on the site is blank and says why, rather than naming a player who may or may not be available.",
         link="https://www.nhl.com/info/injury-report", link_label="NHL injury report page (not read)"),
    dict(id="F-11", severity="high", sport="All", title="Coverage is short of the five-per-sport target",
         detail="The brief asks for five written predictions per sport per day. This desk publishes 21 priced selections across 8 sports. Sports without a confirmed fixture and confirmed form are carried as gaps rather than filled with invented analysis. The shortfall is listed per sport in the coverage table.",
         link="https://www.olbg.com/betting-tips", link_label="OLBG all-sports hub (discovery)"),
    dict(id="F-12", severity="low", sport="All", title="Some kick-off conversions rely on a published local time",
         detail="Top 14 kick-offs are published in French local time and Cork finals in Irish local time; both are converted to UTC here (CEST = UTC+2, IST = UTC+1). The ATP final time, and the venue for the Pakistan ODI, come from the OLBG listing because the official pages did not publish them; both are marked in the sources table.",
         link="https://top14.lnr.fr/calendrier-et-resultats", link_label="Top 14 calendar"),
]
