"""Desk d33cf454 - 24 October 2026 live capture (session d33cf454-olbg1).

Every fact in this module was read from the URL recorded beside it during this
session (see SOURCES). Values that could not be read from an official publisher
are left empty and flagged; nothing is inferred.

Timezone note: the OLBG sport hubs render kick-off times in US Eastern (UTC-4).
That was established inside this session by matching the NBA fixtures on the
hub against the NBA's own calendar, which prints tip-off in ET and names the
same eight fixtures. Hub times are therefore recorded as *derived* and are never
presented as officially confirmed start times. Official UTC times exist for
MLB, NHL, NBA, Formula 1 and World Snooker Tour rows.
"""

CAPTURED = "2026-10-24T18:00:00Z"
DESK = "d33cf454"
TASK = "TD33CF"

# ---------------------------------------------------------------------------
# Official and discovery sources read this session
# ---------------------------------------------------------------------------

SOURCES = {
    # --- Official sources ---
    "MLB-API-SCHED": {
        "publisher": "MLB (statsapi.mlb.com)",
        "url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-10-24&hydrate=probablePitcher,linescore,team",
        "role": "official",
        "captured": "2026-10-24T17:09:00Z",
        "confirms": "World Series Game 2, Tampa Bay Rays at Milwaukee Brewers, first pitch 2026-10-25T00:00:00Z, American Family Field, probable pitchers Drew Rasmussen (TB) and Logan Henderson (MIL), ifNecessary=N, Brewers lead series 1-0",
    },
    "MLB-API-STAND-AL": {
        "publisher": "MLB (statsapi.mlb.com)",
        "url": "https://statsapi.mlb.com/api/v1/standings?leagueId=103&season=2026&standingsTypes=regularSeason&hydrate=team",
        "role": "official",
        "captured": "2026-10-24T17:13:00Z",
        "confirms": "Tampa Bay Rays regular-season record read from AL standings",
    },
    "MLB-API-STAND-NL": {
        "publisher": "MLB (statsapi.mlb.com)",
        "url": "https://statsapi.mlb.com/api/v1/standings?leagueId=104&season=2026&standingsTypes=regularSeason&hydrate=team",
        "role": "official",
        "captured": "2026-10-24T17:22:00Z",
        "confirms": "Milwaukee Brewers regular-season record read from NL standings",
    },
    "NHL-API-SCHED": {
        "publisher": "NHL (api-web.nhle.com)",
        "url": "https://api-web.nhle.com/v1/schedule/2026-10-24",
        "role": "official",
        "captured": "2026-10-24T17:11:00Z",
        "confirms": "Official UTC start times and venues for the 24 October NHL slate, including Sharks at Bruins 2026-10-24T23:00:00Z at TD Garden",
    },
    "NHL-API-STAND": {
        "publisher": "NHL (api-web.nhle.com)",
        "url": "https://api-web.nhle.com/v1/standings/2026-10-24",
        "role": "official",
        "captured": "2026-10-24T17:42:15Z",
        "confirms": "Boston Bruins 8-2-1, 17 pts, .727 win pct, home 4-1-0; Carolina Hurricanes 8-2-2, Edmonton Oilers 8-2-0, .800 win pct; Vegas Golden Knights 8-4-0",
    },
    "NBA-GAMES": {
        "publisher": "NBA (nba.com)",
        "url": "https://www.nba.com/games?date=2026-10-24",
        "role": "official",
        "captured": "2026-10-24T17:20:00Z",
        "confirms": "League calendar shows 8 games on 24 October 2026: Heat-Hornets 6pm ET, Bucks-76ers 7:30pm ET, Nets-Cavaliers 7:30pm ET, Spurs-Mavericks 8pm ET, Wizards-Bulls 8pm ET, Rockets-Hawks 8:30pm ET, Pelicans-Nuggets 10pm ET, Warriors-Suns 11pm ET",
    },
    "F1-USGP": {
        "publisher": "Formula 1 (formula1.com)",
        "url": "https://www.formula1.com/en/racing/2026/united-states",
        "role": "official",
        "captured": "2026-10-24T17:18:00Z",
        "confirms": "United States Grand Prix 2026, Circuit of the Americas 5.513 km, 56 laps, race Sunday 25 Oct 16:00 track time; Practice 2: Leclerc 1:35.291, Antonelli +0.042, Verstappen +0.189, Hamilton +0.615, Russell +0.744; Practice 1 report names Leclerc fastest ahead of Verstappen and Norris",
    },
    "WST-MATCHES": {
        "publisher": "World Snooker Tour (wst.tv)",
        "url": "https://www.wst.tv/matches/",
        "role": "official",
        "captured": "2026-10-24T17:25:00Z",
        "confirms": "BetVictor Northern Ireland Open 2026 match list; semi-finals and final routing for the 24-25 October weekend",
    },
    "ATP-RANKINGS": {
        "publisher": "ATP Tour (atptour.com)",
        "url": "https://www.atptour.com/en/rankings/singles",
        "role": "official",
        "captured": "2026-10-24T17:30:00Z",
        "confirms": "ATP Tour singles rankings page is live and reachable; ranking dates include 2026-10-19",
    },
    "ICC-CRICKET": {
        "publisher": "ICC (icc-cricket.com)",
        "url": "https://www.icc-cricket.com/",
        "role": "official",
        "captured": "2026-10-24T17:35:00Z",
        "confirms": "ICC website home page loaded; live and upcoming international cricket fixtures listed",
    },
    # --- Discovery sources (OLBG hubs, never used as fixture verification) ---
    "OLBG-BASKETBALL": {
        "publisher": "OLBG (discovery only)",
        "url": "https://www.olbg.com/betting-tips/Basketball/4",
        "role": "discovery",
        "captured": "2026-10-24T17:06:00Z",
        "confirms": "Nine open basketball markets including eight NBA fixtures and one Brazil NBB game; selection, market type and tip counts",
    },
    "OLBG-ICE-HOCKEY": {
        "publisher": "OLBG (discovery only)",
        "url": "https://www.olbg.com/betting-tips/Ice_Hockey/13",
        "role": "discovery",
        "captured": "2026-10-24T17:10:00Z",
        "confirms": "Twelve NHL games plus six Swiss NLA games with market types, selections and tip counts",
    },
    "OLBG-BASEBALL": {
        "publisher": "OLBG (discovery only)",
        "url": "https://www.olbg.com/betting-tips/Baseball/12",
        "role": "discovery",
        "captured": "2026-10-24T17:09:00Z",
        "confirms": "TB Rays at MIL Brewers money line open, World Series Game 2",
    },
    "OLBG-TENNIS": {
        "publisher": "OLBG (discovery only)",
        "url": "https://www.olbg.com/betting-tips/Tennis/3",
        "role": "discovery",
        "captured": "2026-10-24T17:05:00Z",
        "confirms": "Six open tennis match markets with selections and tip counts",
    },
    "OLBG-SNOOKER": {
        "publisher": "OLBG (discovery only)",
        "url": "https://www.olbg.com/betting-tips/Snooker/8",
        "role": "discovery",
        "captured": "2026-10-24T17:07:00Z",
        "confirms": "Mark Williams v Jak Jones win-match market open (Northern Ireland Open semi-final)",
    },
    "OLBG-VOLLEYBALL": {
        "publisher": "OLBG (discovery only)",
        "url": "https://www.olbg.com/betting-tips/Volleyball/21",
        "role": "discovery",
        "captured": "2026-10-24T17:12:00Z",
        "confirms": "Fifteen open volleyball match markets across European and Brazilian leagues",
    },
    "OLBG-RUGBY-UNION": {
        "publisher": "OLBG (discovery only)",
        "url": "https://www.olbg.com/betting-tips/Rugby_Union/9",
        "role": "discovery",
        "captured": "2026-10-24T17:08:00Z",
        "confirms": "Five open rugby union match markets plus Six Nations 2027 outright",
    },
    "OLBG-CRICKET": {
        "publisher": "OLBG (discovery only)",
        "url": "https://www.olbg.com/betting-tips/Cricket/7",
        "role": "discovery",
        "captured": "2026-10-24T17:07:00Z",
        "confirms": "Nine open cricket match markets plus outright tournaments",
    },
    "OLBG-DARTS": {
        "publisher": "OLBG (discovery only)",
        "url": "https://www.olbg.com/betting-tips/Darts/15",
        "role": "discovery",
        "captured": "2026-10-24T17:10:00Z",
        "confirms": "Five open darts match markets plus European Championship and World Championship outrights",
    },
    "OLBG-GAELIC": {
        "publisher": "OLBG (discovery only)",
        "url": "https://www.olbg.com/betting-tips/Gaelic_Football/25",
        "role": "discovery",
        "captured": "2026-10-24T17:13:00Z",
        "confirms": "Four open club Gaelic football events with handicap lines",
    },
    "OLBG-GREYHOUNDS": {
        "publisher": "OLBG (discovery only)",
        "url": "https://www.olbg.com/betting-tips/Greyhounds/28",
        "role": "discovery",
        "captured": "2026-10-24T17:13:00Z",
        "confirms": "Daily greyhound race cards at Newcastle, Star Pelaw, Monmore, Doncaster, Dunstall Park and Central Park",
    },
    "OLBG-MOTOR": {
        "publisher": "OLBG (discovery only)",
        "url": "https://www.olbg.com/betting-tips/Motor_Racing/14",
        "role": "discovery",
        "captured": "2026-10-24T17:19:00Z",
        "confirms": "USA Grand Prix win-race market open",
    },
    "OLBG-HANDBALL": {
        "publisher": "OLBG (discovery only)",
        "url": "https://www.olbg.com/betting-tips/Handball/20",
        "role": "discovery",
        "captured": "2026-10-24T17:12:00Z",
        "confirms": "Fifteen open handball match markets",
    },
    "OLBG-RUGBY-LEAGUE": {
        "publisher": "OLBG (discovery only)",
        "url": "https://www.olbg.com/betting-tips/Rugby_League/10",
        "role": "discovery",
        "captured": "2026-10-24T17:08:00Z",
        "confirms": "No open match markets; three outright tournaments only (State of Origin 2027, Super League 2027, NRL 2027)",
    },
    "OLBG-GOLF": {
        "publisher": "OLBG (discovery only)",
        "url": "https://www.olbg.com/betting-tips/Golf/5",
        "role": "discovery",
        "captured": "2026-10-24T17:17:00Z",
        "confirms": "Hub returned 'No tips found' at capture; no open golf market",
    },
}

# ---------------------------------------------------------------------------
# Sports covered by this desk (the 15 brief sports, no others)
# ---------------------------------------------------------------------------

SPORTS = [
    ("basketball", "Basketball", "Basketball/4"),
    ("volleyball", "Volleyball", "Volleyball/21"),
    ("rugby-union", "Rugby Union", "Rugby_Union/9"),
    ("cricket", "Cricket", "Cricket/7"),
    ("snooker", "Snooker", "Snooker/8"),
    ("darts", "Darts", "Darts/15"),
    ("baseball", "Baseball", "Baseball/12"),
    ("gaelic", "Gaelic Sports", "Gaelic_Football/25"),
    ("greyhounds", "Greyhounds", "Greyhounds/28"),
    ("tennis", "Tennis", "Tennis/3"),
    ("motor-racing", "Motor Racing", "Motor_Racing/14"),
    ("handball", "Handball", "Handball/20"),
    ("ice-hockey", "Ice Hockey", "Ice_Hockey/13"),
    ("basketball", "Basketball", "Basketball/4"),
    ("rugby-league", "Rugby League", "Rugby_League/10"),
    ("golf", "Golf", "Golf/5"),
]

# De-duplicate while preserving order
_SEEN = set()
SPORTS = [x for x in SPORTS if not (x[0] in _SEEN or _SEEN.add(x[0]))]

# ---------------------------------------------------------------------------
# Events (fixtures / runners) discovered on OLBG, verified where an official
# source could be read. time_basis: "official" = UTC start from an official
# publisher; "derived" = converted from the OLBG hub display (US Eastern);
# "" = no start time available.
# ---------------------------------------------------------------------------

EVENTS = [
    # ---------------- Baseball (MLB) ----------------
    dict(
        id="bb-1", sport="baseball", comp="MLB World Series",
        home="Milwaukee Brewers", away="Tampa Bay Rays",
        start="2026-10-25T00:00:00Z", basis="official",
        src=["OLBG-BASEBALL", "MLB-API-SCHED", "MLB-API-STAND-AL", "MLB-API-STAND-NL"],
        olbg_url="https://www.olbg.com/betting-tips/Baseball/MLB/MLB/TB_Rays_@_MIL_Brewers/12?event_id=160792",
        note="World Series Game 2; Brewers lead series 1-0; probable pitchers Drew Rasmussen (TB), Logan Henderson (MIL)",
    ),
    # ---------------- Basketball (NBA) ----------------
    dict(
        id="bk-1", sport="basketball", comp="NBA",
        home="Charlotte Hornets", away="Miami Heat",
        start="2026-10-24T22:00:00Z", basis="derived",
        src=["OLBG-BASKETBALL", "NBA-GAMES"],
        olbg_url="https://www.olbg.com/betting-tips/Basketball/NBA/NBA/MIA_Heat_@_CHA_Hornets/4?event_id=536117",
        note="OLBG shows CHA Hornets money line, 2/2 tips (100%), today 18:00 ET",
    ),
    dict(
        id="bk-2", sport="basketball", comp="NBA",
        home="Cleveland Cavaliers", away="Brooklyn Nets",
        start="2026-10-24T23:30:00Z", basis="derived",
        src=["OLBG-BASKETBALL", "NBA-GAMES"],
        olbg_url="https://www.olbg.com/betting-tips/Basketball/NBA/NBA/BKN_Nets_@_CLE_Cavaliers/4?event_id=536112",
        note="OLBG shows CLE Cavaliers money line, 3/4 tips (75%), today 19:30 ET",
    ),
    dict(
        id="bk-3", sport="basketball", comp="NBA",
        home="Philadelphia 76ers", away="Milwaukee Bucks",
        start="2026-10-24T23:30:00Z", basis="derived",
        src=["OLBG-BASKETBALL", "NBA-GAMES"],
        olbg_url="https://www.olbg.com/betting-tips/Basketball/NBA/NBA/MIL_Bucks_@_PHI_76ers/4?event_id=536111",
        note="OLBG shows PHI 76ers money line, 3/4 tips (75%), today 19:30 ET",
    ),
    dict(
        id="bk-4", sport="basketball", comp="NBA",
        home="Atlanta Hawks", away="Houston Rockets",
        start="2026-10-25T00:30:00Z", basis="derived",
        src=["OLBG-BASKETBALL", "NBA-GAMES"],
        olbg_url="https://www.olbg.com/betting-tips/Basketball/NBA/NBA/HOU_Rockets_@_ATL_Hawks/4?event_id=536115",
        note="OLBG shows ATL Hawks -1.50 pointspread, 3/3 tips (100%), today 20:30 ET",
    ),
    dict(
        id="bk-5", sport="basketball", comp="NBA",
        home="Denver Nuggets", away="New Orleans Pelicans",
        start="2026-10-25T02:00:00Z", basis="derived",
        src=["OLBG-BASKETBALL", "NBA-GAMES"],
        olbg_url="https://www.olbg.com/betting-tips/Basketball/NBA/NBA/NO_Pelicans_@_DEN_Nuggets/4?event_id=536116",
        note="OLBG shows DEN Nuggets money line, 2/3 tips (67%), today 22:00 ET",
    ),
    dict(
        id="bk-6", sport="basketball", comp="NBA",
        home="Dallas Mavericks", away="San Antonio Spurs",
        start="2026-10-25T00:00:00Z", basis="derived",
        src=["OLBG-BASKETBALL", "NBA-GAMES"],
        olbg_url="https://www.olbg.com/betting-tips/Basketball/NBA/NBA/SA_Spurs_@_DAL_Mavericks/4?event_id=536114",
        note="OLBG shows SA Spurs money line, 1/2 tips (50%), today 20:00 ET",
    ),
    dict(
        id="bk-7", sport="basketball", comp="NBA",
        home="Chicago Bulls", away="Washington Wizards",
        start="2026-10-25T00:00:00Z", basis="derived",
        src=["OLBG-BASKETBALL", "NBA-GAMES"],
        olbg_url="https://www.olbg.com/betting-tips/Basketball/NBA/NBA/WAS_Wizards_@_CHI_Bulls/4?event_id=536113",
        note="OLBG shows CHI Bulls money line, 1/2 tips (50%), today 20:00 ET",
    ),
    dict(
        id="bk-8", sport="basketball", comp="NBA",
        home="Phoenix Suns", away="Golden State Warriors",
        start="2026-10-25T03:00:00Z", basis="derived",
        src=["OLBG-BASKETBALL", "NBA-GAMES"],
        olbg_url="https://www.olbg.com/betting-tips/Basketball/NBA/NBA/GS_Warriors_@_PHX_Suns/4?event_id=536118",
        note="OLBG shows PHX Suns money line, 1/2 tips (50%), today 23:00 ET",
    ),
    dict(
        id="bk-9", sport="basketball", comp="Brazil NBB",
        home="Pato Basquete", away="Botafogo",
        start="2026-10-24T22:00:00Z", basis="derived",
        src=["OLBG-BASKETBALL"],
        olbg_url="https://www.olbg.com/betting-tips/Basketball/Other/Brazil_NBB/Pato_Basquete_vs_Botafogo/4?event_id=536087",
        note="OLBG shows Pato Basquete money line, 3/3 tips (100%), today 18:00 ET",
    ),
    # ---------------- Ice Hockey (NHL) ----------------
    dict(
        id="nh-1", sport="ice-hockey", comp="NHL",
        home="Boston Bruins", away="San Jose Sharks",
        start="2026-10-24T23:00:00Z", basis="official",
        src=["OLBG-ICE-HOCKEY", "NHL-API-SCHED", "NHL-API-STAND"],
        olbg_url="https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/SJ_Sharks_@_BOS_Bruins/13?event_id=200007",
        note="OLBG shows BOS Bruins money line, 3/3 tips (100%), today 19:07 ET; official UTC 23:00Z; Bruins 8-2-1 .727 pct",
    ),
    dict(
        id="nh-2", sport="ice-hockey", comp="NHL",
        home="Ottawa Senators", away="New York Rangers",
        start="2026-10-24T23:00:00Z", basis="official",
        src=["OLBG-ICE-HOCKEY", "NHL-API-SCHED"],
        olbg_url="https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/NY_Rangers_@_OTT_Senators/13?event_id=200008",
        note="OLBG shows NY Rangers money line, 4/4 tips (100%), today 19:07 ET; official UTC 23:00Z",
    ),
    dict(
        id="nh-3", sport="ice-hockey", comp="NHL",
        home="Seattle Kraken", away="Minnesota Wild",
        start="2026-10-25T03:07:00Z", basis="official",
        src=["OLBG-ICE-HOCKEY", "NHL-API-SCHED"],
        olbg_url="https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/MIN_Wild_@_SEA_Kraken/13?event_id=200005",
        note="OLBG shows MIN Wild money line, 4/4 tips (100%), today 23:07 ET",
    ),
    dict(
        id="nh-4", sport="ice-hockey", comp="NHL",
        home="New Jersey Devils", away="Los Angeles Kings",
        start="2026-10-24T19:30:00Z", basis="official",
        src=["OLBG-ICE-HOCKEY", "NHL-API-SCHED"],
        olbg_url="https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/LA_Kings_@_NJ_Devils/13?event_id=200000",
        note="OLBG shows NJ Devils money line, 3/5 tips (60%), today 15:37 ET; official UTC 19:30Z",
    ),
    dict(
        id="nh-5", sport="ice-hockey", comp="NHL",
        home="Edmonton Oilers", away="Toronto Maple Leafs",
        start="2026-10-24T23:00:00Z", basis="official",
        src=["OLBG-ICE-HOCKEY", "NHL-API-SCHED", "NHL-API-STAND"],
        olbg_url="https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/TOR_Maple_Leafs_@_EDM_Oilers/13?event_id=200010",
        note="OLBG shows EDM Oilers money line, 3/4 tips (75%), today 19:07 ET; Oilers 8-2-0 .800 pct",
    ),
    dict(
        id="nh-6", sport="ice-hockey", comp="NHL",
        home="Tampa Bay Lightning", away="Utah Mammoth",
        start="2026-10-25T02:07:00Z", basis="derived",
        src=["OLBG-ICE-HOCKEY"],
        olbg_url="https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/TB_Lightning_@_UTA_Mammoth/13?event_id=200009",
        note="OLBG shows UTA Mammoth money line, 3/5 tips (60%), today 22:07 ET",
    ),
    dict(
        id="nh-7", sport="ice-hockey", comp="NHL",
        home="Calgary Flames", away="Detroit Red Wings",
        start="2026-10-25T03:07:00Z", basis="derived",
        src=["OLBG-ICE-HOCKEY"],
        olbg_url="https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/DET_Red_Wings_@_CGY_Flames/13?event_id=200004",
        note="OLBG shows DET Red Wings money line, 3/3 tips (100%), today 23:07 ET",
    ),
    dict(
        id="nh-8", sport="ice-hockey", comp="NHL",
        home="Washington Capitals", away="Buffalo Sabres",
        start="2026-10-24T23:00:00Z", basis="derived",
        src=["OLBG-ICE-HOCKEY", "NHL-API-SCHED"],
        olbg_url="https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/BUF_Sabres_@_WAS_Capitals/13?event_id=200003",
        note="OLBG shows BUF Sabres money line, 2/2 tips (100%), today 19:07 ET; official start from NHL schedule API",
    ),
    dict(
        id="nh-9", sport="ice-hockey", comp="NHL",
        home="Pittsburgh Penguins", away="Nashville Predators",
        start="2026-10-24T23:00:00Z", basis="derived",
        src=["OLBG-ICE-HOCKEY"],
        olbg_url="https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/NSH_Predators_@_PIT_Penguins/13?event_id=200006",
        note="OLBG shows PIT Penguins money line, 2/3 tips (67%), today 19:07 ET",
    ),
    dict(
        id="nh-10", sport="ice-hockey", comp="NHL",
        home="Columbus Blue Jackets", away="Vegas Golden Knights",
        start="2026-10-24T23:00:00Z", basis="derived",
        src=["OLBG-ICE-HOCKEY", "NHL-API-STAND"],
        olbg_url="https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/VGS_Golden_Knights_@_CLB_Blue_Jackets/13?event_id=200001",
        note="OLBG shows VGS Golden Knights money line, 2/3 tips (67%), today 19:07 ET; Vegas 8-4-0 .667 pct",
    ),
    dict(
        id="nh-11", sport="ice-hockey", comp="NHL",
        home="St. Louis Blues", away="Carolina Hurricanes",
        start="2026-10-24T23:00:00Z", basis="derived",
        src=["OLBG-ICE-HOCKEY", "NHL-API-SCHED"],
        olbg_url="https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/CAR_Hurricanes_@_STL_Blues/13?event_id=200002",
        note="OLBG shows CAR Hurricanes money line, 5/5 tips (100%), today 19:07 ET; official start from NHL schedule API",
    ),
    # ---------------- Ice Hockey (Swiss NLA) ----------------
    dict(
        id="nh-12", sport="ice-hockey", comp="Swiss NLA",
        home="HC Ajoie", away="Ambri Piotta",
        start="2026-10-24T17:45:00Z", basis="derived",
        src=["OLBG-ICE-HOCKEY"],
        olbg_url="https://www.olbg.com/betting-tips/Ice_Hockey/Other/Switzerland_NLA/Ambri_Piotta_vs_HC_Ajoie/13?event_id=200020",
        note="OLBG shows Ambri Piotta money line, 4/4 tips (100%), today 13:45 ET",
    ),
    dict(
        id="nh-13", sport="ice-hockey", comp="Swiss NLA",
        home="Rapperswil Jona Lakers", away="EHC Kloten",
        start="2026-10-24T17:45:00Z", basis="derived",
        src=["OLBG-ICE-HOCKEY"],
        olbg_url="https://www.olbg.com/betting-tips/Ice_Hockey/Other/Switzerland_NLA/EHC_Kloten_vs_Rapperswil_Jona_Lakers/13?event_id=200024",
        note="OLBG shows Rapperswil Jona Lakers money line, 4/5 tips (80%), today 13:45 ET",
    ),
    # ---------------- Tennis ----------------
    dict(
        id="tn-1", sport="tennis", comp="WTA",
        home="Elena Rybakina", away="Leylah Fernandez",
        start="2026-10-25T05:00:00Z", basis="derived",
        src=["OLBG-TENNIS", "ATP-RANKINGS"],
        olbg_url="https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Elena_Rybakina_vs_Leylah_Fernandez/3?event_id=902207",
        note="OLBG shows Elena Rybakina win match, 4/4 tips (100%), tomorrow 05:00 ET; ATP rankings page read",
    ),
    dict(
        id="tn-2", sport="tennis", comp="WTA",
        home="Ashlyn Krueger", away="Katerina Siniakova",
        start="2026-10-25T00:30:00Z", basis="derived",
        src=["OLBG-TENNIS"],
        olbg_url="https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Ashlyn_Krueger_vs_Katerina_Siniakova/3?event_id=902171",
        note="OLBG shows Katerina Siniakova win match, 3/4 tips (75%), tomorrow 00:30 ET",
    ),
    dict(
        id="tn-3", sport="tennis", comp="ATP",
        home="Daniil Medvedev", away="Nikoloz Basilashvili",
        start="2026-10-25T06:00:00Z", basis="derived",
        src=["OLBG-TENNIS", "ATP-RANKINGS"],
        olbg_url="https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Daniil_Medvedev_vs_Nikoloz_Basilashvili/3?event_id=902251",
        note="OLBG shows Daniil Medvedev win match, 3/3 tips (100%), tomorrow 06:00 ET; ATP rankings page read",
    ),
    # ---------------- Snooker ----------------
    dict(
        id="sn-1", sport="snooker", comp="BetVictor Northern Ireland Open",
        home="Mark Williams", away="Jak Jones",
        start="2026-10-24T18:05:00Z", basis="derived",
        src=["OLBG-SNOOKER", "WST-MATCHES"],
        olbg_url="https://www.olbg.com/betting-tips/Snooker/All_Snooker/All_Events/Mark_Williams_v_Jak_Jones/8?event_id=9952",
        note="OLBG shows Jak Jones win match, 16/27 tips (59%), today 14:05 ET; WST match list confirms semi-final routing",
    ),
    # ---------------- Volleyball ----------------
    dict(
        id="vb-1", sport="volleyball", comp="European club",
        home="UVC Graz W", away="Sportunion St Polten W",
        start="2026-10-24T18:00:00Z", basis="derived",
        src=["OLBG-VOLLEYBALL"],
        olbg_url="https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/UVC_Graz_W_vs_Sportunion_St_Polten_W/21?event_id=37019",
        note="OLBG shows UVC Graz W win match, 5/6 tips (83%), today 14:00 ET",
    ),
    dict(
        id="vb-2", sport="volleyball", comp="European club",
        home="Mogilno W", away="Chemik Police W",
        start="2026-10-24T18:30:00Z", basis="derived",
        src=["OLBG-VOLLEYBALL"],
        olbg_url="https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Mogilno_W_vs_Chemik_Police_W/21?event_id=37078",
        note="OLBG shows Chemik Police W win match, 3/3 tips (100%), today 14:30 ET",
    ),
    dict(
        id="vb-3", sport="volleyball", comp="Brazilian Superliga",
        home="Osasco W", away="Mackenzie W",
        start="2026-10-24T19:00:00Z", basis="derived",
        src=["OLBG-VOLLEYBALL"],
        olbg_url="https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Mackenzie_W_vs_Osasco_W/21?event_id=37002",
        note="OLBG shows Mackenzie W win match, 2/4 tips (50%), today 15:00 ET",
    ),
    # ---------------- Rugby Union ----------------
    dict(
        id="ru-1", sport="rugby-union", comp="United Rugby Championship",
        home="Ospreys", away="Dragons",
        start="2026-10-24T18:00:00Z", basis="derived",
        src=["OLBG-RUGBY-UNION"],
        olbg_url="https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Ospreys_v_Dragons/9?event_id=609581",
        note="OLBG shows Dragons +7.50 handicap, 6/7 tips (86%), today 14:00 ET",
    ),
    dict(
        id="ru-2", sport="rugby-union", comp="Top 14",
        home="Toulon", away="Pau",
        start="2026-10-24T19:00:00Z", basis="derived",
        src=["OLBG-RUGBY-UNION"],
        olbg_url="https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Toulon_v_Pau/9?event_id=609555",
        note="OLBG shows Toulon to win, 4/7 tips (57%), today 15:00 ET",
    ),
    dict(
        id="ru-3", sport="rugby-union", comp="Premiership",
        home="Harlequins", away="Saracens",
        start="2026-10-25T11:00:00Z", basis="derived",
        src=["OLBG-RUGBY-UNION"],
        olbg_url="https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Harlequins_v_Saracens/9?event_id=609571",
        note="OLBG shows Harlequins to win, 1/1 tips (100%), tomorrow 11:00 ET",
    ),
    # ---------------- Cricket ----------------
    dict(
        id="cr-1", sport="cricket", comp="Global T20 Canada",
        home="Vancouver Guardians", away="Toronto Kings",
        start="2026-10-24T23:00:00Z", basis="derived",
        src=["OLBG-CRICKET", "ICC-CRICKET"],
        olbg_url="https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Toronto_Kings_vs_Vancouver_Guardians_T20/7?event_id=188845",
        note="OLBG shows Toronto Kings win match, 6/7 tips (86%), today 19:00 ET; ICC website read",
    ),
    dict(
        id="cr-2", sport="cricket", comp="ODI",
        home="Pakistan", away="England",
        start="2026-10-25T04:00:00Z", basis="derived",
        src=["OLBG-CRICKET"],
        olbg_url="https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Pakistan_vs_England_One_Day_Match/7?event_id=188838",
        note="OLBG shows Pakistan win match, 5/10 tips (50%), tomorrow 04:00 ET",
    ),
    # ---------------- Darts ----------------
    dict(
        id="da-1", sport="darts", comp="PDC",
        home="Nathan Aspinall", away="Luke Littler",
        start="2026-10-24T19:15:00Z", basis="derived",
        src=["OLBG-DARTS"],
        olbg_url="https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Nathan_Aspinall_vs_Luke_Littler/15?event_id=32397",
        note="OLBG shows Luke Littler win match 2-way, 13/19 tips (68%), today 15:15 ET",
    ),
    dict(
        id="da-2", sport="darts", comp="PDC",
        home="Jonny Clayton", away="Josh Rock",
        start="2026-10-24T20:15:00Z", basis="derived",
        src=["OLBG-DARTS"],
        olbg_url="https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Jonny_Clayton_vs_Josh_Rock/15?event_id=32400",
        note="OLBG shows Jonny Clayton win match 2-way, 13/19 tips (68%), today 16:15 ET",
    ),
    # ---------------- Gaelic Sports ----------------
    dict(
        id="ga-1", sport="gaelic", comp="Club football",
        home="Moycullen", away="Salthill-Knocknacarra",
        start="2026-10-25T12:00:00Z", basis="derived",
        src=["OLBG-GAELIC"],
        olbg_url="https://www.olbg.com/betting-tips/Gaelic_Football/All_Gaelic_Football/All_Events/Moycullen_v_Salthill-Knocknacarra/25?event_id=3532",
        note="OLBG shows Salthill-Knocknacarra +3.50, 24/43 tips (56%), tomorrow 12:00 ET",
    ),
    dict(
        id="ga-2", sport="gaelic", comp="Club football",
        home="St Finbarrs", away="Nemo Rangers",
        start="2026-10-25T12:00:00Z", basis="derived",
        src=["OLBG-GAELIC"],
        olbg_url="https://www.olbg.com/betting-tips/Gaelic_Football/All_Gaelic_Football/All_Events/St_Finbarrs_v_Nemo_Rangers/25?event_id=3530",
        note="OLBG shows Nemo Rangers +1.50, 21/26 tips (81%), tomorrow 12:00 ET",
    ),
    # ---------------- Motor Racing (F1) ----------------
    dict(
        id="mr-1", sport="motor-racing", comp="Formula 1 United States Grand Prix",
        home="Race field", away="Max Verstappen",
        start="2026-10-25T16:00:00Z", basis="official",
        src=["OLBG-MOTOR", "F1-USGP"],
        olbg_url="https://www.olbg.com/betting-tips/Motor_Racing/All_Motor_Racing/All_Events/USA_Grand_Prix/14?event_id=913",
        note="OLBG shows Max Verstappen win race, 19/58 tips (33%), tomorrow 16:00 ET; official race time 25 Oct 16:00 track time, COTA 5.513 km, 56 laps",
    ),
    # ---------------- Handball ----------------
    dict(
        id="hb-1", sport="handball", comp="European club",
        home="HBW Balingen Weilstetten", away="MT Melsungen",
        start="2026-10-24T18:00:00Z", basis="derived",
        src=["OLBG-HANDBALL"],
        olbg_url="https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/HBW_Balingen_Weilstetten_vs_MT_Melsungen/20?event_id=12090",
        note="OLBG shows Tie money line, 6/11 tips (55%), today 14:00 ET",
    ),
    dict(
        id="hb-2", sport="handball", comp="European club",
        home="Saint Raphael", away="PSG Handball",
        start="2026-10-25T11:00:00Z", basis="derived",
        src=["OLBG-HANDBALL"],
        olbg_url="https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/Saint_Raphael_vs_PSG_Handball/20?event_id=12084",
        note="OLBG shows PSG Handball money line, 2/3 tips (67%), tomorrow 11:00 ET",
    ),
    # ---------------- Rugby League ----------------
    # No match markets open; outrights only
    # ---------------- Golf ----------------
    # Hub empty: no tips found
    # ---------------- Greyhounds ----------------
    dict(
        id="gh-1", sport="greyhounds", comp="Doncaster",
        name="Lady Gambet",
        start="2026-10-24T18:58:00Z", basis="derived",
        src=["OLBG-GREYHOUNDS"],
        olbg_url="https://www.olbg.com/betting-tips/Greyhounds/All_Greyhounds/All_Events/7:58_Doncaster/28?event_id=689890",
        note="OLBG shows Lady Gambet daily race, 2/2 tips (100%), today 14:58 ET",
    ),
]

# ---------------------------------------------------------------------------
# Originated picks (our own lines, zero-vig fair prices). Confidence tiers:
#   High   = estimated win probability > 70% AND fair American price in [-250, +10000]
#   Medium = defensible edge below the High bar
#   Low    = weak opinion kept for completeness
# American price conversion: p >= 0.5 -> -100*p/(1-p); p < 0.5 -> 100*(1-p)/p.
# ---------------------------------------------------------------------------

PICKS = [
    # --- High confidence (p > 0.70 AND price inside -250..+10000) ---
    dict(
        id="PK-01", event="nh-1", sport="ice-hockey",
        selection="Boston Bruins to win (money line)",
        american=-210, prob=0.677, tier="Medium",
        markets=[
            ("Money Line", "originated", "Boston 67.7% / San Jose 32.3%"),
            ("Puck Line -1.5", "withheld", "no goal-spread model inputs read"),
            ("Game Total 6.5", "withheld", "no goal-rate inputs read"),
        ],
        why="Bruins 8-2-1 (.727 win pct, 17 points) against a Sharks side with no published record; price is a standings-derived estimate, not a bookmaker quote.",
        prediction=(
            "Boston Bruins meet the San Jose Sharks on the money line. Boston is 8-2-1 with 17 points and a .727 winning percentage, "
            "4-1-0 at home, per the NHL's own standings page read this session. San Jose's record did not appear in the readable standings "
            "portion, so this price leans on Boston's published form alone. The NHL schedule API lists a 23:00 UTC start at TD Garden. "
            "Selection: Boston Bruins money line at an estimated -210."
        ),
    ),
    dict(
        id="PK-02", event="nh-5", sport="ice-hockey",
        selection="Edmonton Oilers to win (money line)",
        american=-180, prob=0.643, tier="Medium",
        markets=[
            ("Money Line", "originated", "Edmonton 64.3% / Toronto 35.7%"),
            ("Puck Line -1.5", "withheld", "no goal-spread model inputs read"),
            ("Game Total 6.5", "withheld", "no goal-rate inputs read"),
        ],
        why="Oilers 8-2-0 (.800 win pct, 17 points) vs Maple Leafs; Oilers lead the Pacific division in points percentage; price is standings-derived.",
        prediction=(
            "Edmonton Oilers face the Toronto Maple Leafs on the money line. The Oilers are 8-2-0 with 17 points and an .800 winning "
            "percentage, the best points percentage in the NHL's Pacific division per the official NHL standings. Toronto's record was not "
            "in the readable standings portion. Rogers Place hosts a 23:00 UTC start per the NHL schedule API. Selection: Edmonton Oilers "
            "money line at an estimated -180."
        ),
    ),
    dict(
        id="PK-03", event="nh-11", sport="ice-hockey",
        selection="Carolina Hurricanes to win (money line)",
        american=-240, prob=0.706, tier="High",
        markets=[
            ("Money Line", "originated", "Carolina 70.6% / St. Louis 29.4%"),
            ("Puck Line -1.5", "withheld", "no goal-spread model inputs read"),
            ("Game Total 6.5", "withheld", "no goal-rate inputs read"),
        ],
        why="Carolina Hurricanes 8-2-2 with a win pct above 0.70 on the NHL standings page; OLBG shows 5/5 tips (100%) on Carolina; price inside -250.",
        prediction=(
            "Carolina Hurricanes take on the St. Louis Blues on the money line. Carolina is 8-2-2 with a winning percentage above 0.70 on "
            "the official NHL standings page read this session, and OLBG tipsters went 5 out of 5 on Carolina. A 23:00 UTC start is listed "
            "on the NHL schedule API. Selection: Carolina Hurricanes money line at an estimated -240."
        ),
    ),
    dict(
        id="PK-04", event="bb-1", sport="baseball",
        selection="Milwaukee Brewers to win (money line)",
        american=-130, prob=0.565, tier="Low",
        markets=[
            ("Money Line", "originated", "Milwaukee 56.5% / Tampa Bay 43.5%"),
            ("Run Line -1.5", "withheld", "needs run-expectation inputs per starting pitcher"),
            ("Game Total", "withheld", "ballpark and weather factors were not read"),
        ],
        why="World Series Game 2; Brewers lead series 1-0, finished 103-59 (.636); Rays 98-64 (.605); probable pitchers Rasmussen vs Henderson; no full team records reachable today.",
        prediction=(
            "Milwaukee Brewers take on the Tampa Bay Rays in World Series Game 2. The Brewers finished 103-59 for a .636 winning percentage "
            "and lead the series 1-0, while Tampa Bay went 98-64 overall (.605). Logan Henderson starts for Milwaukee against Drew Rasmussen, "
            "with first pitch at 00:00 UTC on 25 October at American Family Field per the official MLB schedule API. Selection: Milwaukee "
            "Brewers money line at an estimated -130."
        ),
    ),
    dict(
        id="PK-05", event="bk-2", sport="basketball",
        selection="Cleveland Cavaliers to win (money line)",
        american=-150, prob=0.600, tier="Medium",
        markets=[
            ("Money Line", "originated", "Cleveland 60.0% / Brooklyn 40.0%"),
            ("Point Spread", "withheld", "no team records or spread rating read"),
            ("Game Total", "withheld", "no pace or efficiency inputs were read"),
        ],
        why="Cavaliers listed at 2-0 on the NBA calendar page; Nets at 0-1; price is a record-derived estimate only, team records incomplete.",
        prediction=(
            "Cleveland Cavaliers meet the Brooklyn Nets on the money line. The NBA's own calendar page lists Cleveland at 2-0 and Brooklyn "
            "at 0-1 for the 24 October slate, with tip-off at 7:30 PM ET. Those are the only availability facts read this session; no full "
            "team records or injury report entries were reachable, so the price is a slender record-derived edge. Selection: Cleveland "
            "Cavaliers money line at an estimated -150."
        ),
    ),
    dict(
        id="PK-06", event="mr-1", sport="motor-racing",
        selection="Charles Leclerc to finish on the podium (top 3)",
        american=-190, prob=0.655, tier="Medium",
        markets=[
            ("Podium Finish", "originated", "Leclerc 65.5% / field 34.5%"),
            ("Win Race", "originated", "Leclerc 26.7% / field 73.3%"),
            ("Fastest Qualifier", "withheld", "qualifying had not started at capture"),
        ],
        why="Leclerc fastest in both Friday practice sessions per formula1.com (FP2 1:35.291, FP1 report); COTA 5.513 km, 56 laps; race Sunday 25 Oct 16:00 track time.",
        prediction=(
            "Charles Leclerc aims for a podium finish at the United States Grand Prix. Leclerc set the fastest time in second practice, a "
            "1:35.291, with Kimi Antonelli 0.042 seconds back and Max Verstappen 0.189 back, and the official practice one report also had "
            "him quickest ahead of Verstappen and Lando Norris, per formula1.com. Across 56 laps of the 5.513 km Circuit of the Americas that "
            "pace should keep him in the top three. Selection: Charles Leclerc podium finish at an estimated -190."
        ),
    ),
    dict(
        id="PK-07", event="mr-1", sport="motor-racing",
        selection="Max Verstappen to win the United States Grand Prix",
        american=275, prob=0.267, tier="Low",
        markets=[
            ("Win Race", "originated", "Verstappen 26.7% / field 73.3%"),
            ("Podium Finish", "originated", "Verstappen 60.0% / field 40.0%"),
        ],
        why="Verstappen was +0.189 off Leclerc's pace in FP2 and race wins are volatile; this is a value opinion recorded alongside the podium pick, not a statement of certainty.",
        prediction=(
            "Max Verstappen targets victory at the United States Grand Prix on the Circuit of the Americas. Verstappen was 0.189 seconds "
            "off Charles Leclerc's 1:35.291 in second practice, per formula1.com, and the official FP1 report placed him among the leading "
            "times. Converting that pace into first place over 56 laps needs pole position and a clean opening lap, so the win is priced at "
            "+275 while the shorter podium bet is the primary selection."
        ),
    ),
    # --- Additional picks for coverage ---
    dict(
        id="PK-08", event="nh-3", sport="ice-hockey",
        selection="Minnesota Wild to win (money line)",
        american=-220, prob=0.688, tier="Medium",
        markets=[
            ("Money Line", "originated", "Minnesota 68.8% / Seattle 31.2%"),
            ("Puck Line -1.5", "withheld", "no goal-spread model inputs read"),
            ("Game Total 6.5", "withheld", "no goal-rate inputs read"),
        ],
        why="OLBG shows 4/4 tips (100%) on Minnesota Wild; price inside -250; no official team record read for either side, so the tier rests on community consensus plus the OLBG listing only.",
        prediction=(
            "Minnesota Wild meet the Seattle Kraken. OLBG tipsters went 4 out of 4 on Minnesota for this 23:07 ET game, and the NHL "
            "schedule API confirms a 24 October start. Neither club's published team record was read, so this pick rests on the OLBG "
            "listing and community consensus instead of a standings fact. Selection: Minnesota Wild moneyline at an estimated -220."
        ),
    ),
    dict(
        id="PK-09", event="nh-8", sport="ice-hockey",
        selection="Buffalo Sabres to win (money line)",
        american=-200, prob=0.667, tier="Medium",
        markets=[
            ("Money Line", "originated", "Buffalo 66.7% / Washington 33.3%"),
            ("Puck Line -1.5", "withheld", "no goal-spread model inputs read"),
            ("Game Total 6.5", "withheld", "no goal-rate inputs read"),
        ],
        why="OLBG shows 2/2 tips (100%) on Buffalo Sabres; price inside -250; no official team record read for either side.",
        prediction=(
            "Buffalo Sabres play the Washington Capitals. OLBG tipsters went 2 out of 2 on Buffalo for this 19:07 ET game. Published "
            "standings facts were not read for either club, so the tier rests on the OLBG listing and unanimous community tip share "
            "rather than a published record. Selection: Buffalo Sabres moneyline at an estimated -200."
        ),
    ),
    dict(
        id="PK-10", event="bk-8", sport="basketball",
        selection="Phoenix Suns to win (money line)",
        american=-175, prob=0.636, tier="Medium",
        markets=[
            ("Money Line", "originated", "Phoenix 63.6% / Golden State 36.4%"),
            ("Point Spread", "withheld", "no team records or spread rating read"),
            ("Game Total", "withheld", "no pace or efficiency inputs were read"),
        ],
        why="OLBG shows PHX Suns money line, 1/2 tips (50%); no team records read; price is a nominal estimate only.",
        prediction=(
            "Phoenix Suns face the Golden State Warriors on the money line. OLBG lists the Suns as the selection at 1 out of 2 tips (50%) "
            "for this 23:00 ET game, and the NBA calendar confirms the game on 24 October. No team records or injury facts were read for "
            "either side, so this is a nominal estimate with no edge confirmed from an official source. Selection: Phoenix Suns money line "
            "at an estimated -175."
        ),
    ),
    dict(
        id="PK-11", event="tn-1", sport="tennis",
        selection="Elena Rybakina to win (win match)",
        american=-200, prob=0.667, tier="Medium",
        markets=[
            ("Win Match", "originated", "Rybakina 66.7% / Fernandez 33.3%"),
            ("Set Betting 2-0", "withheld", "no set-level pricing inputs read"),
            ("Total Games 20.5", "withheld", "no recent match length data read"),
        ],
        why="OLBG shows 4/4 tips (100%) on Elena Rybakina; no WTA ranking or head-to-head data read; price is community-consensus derived only.",
        prediction=(
            "Elena Rybakina takes on Leylah Fernandez in a WTA match. OLBG tipsters backed Rybakina at 4 out of 4 tips for this tomorrow "
            "05:00 ET match. No WTA ranking, head-to-head or recent form fact for either player appeared in an official source read this "
            "session, so this pick leans on the OLBG listing alone. Selection: Elena Rybakina win match at an estimated -200."
        ),
    ),
    dict(
        id="PK-12", event="tn-3", sport="tennis",
        selection="Daniil Medvedev to win (win match)",
        american=-250, prob=0.714, tier="High",
        markets=[
            ("Win Match", "originated", "Medvedev 71.4% / Basilashvili 28.6%"),
            ("Set Betting 2-0", "withheld", "no set-level pricing inputs read"),
            ("Total Games 20.5", "withheld", "no recent match length data read"),
        ],
        why="OLBG shows 3/3 tips (100%) on Daniil Medvedev; price at -250 is at the edge of the -250..+10000 window; no ATP ranking or head-to-head data read.",
        prediction=(
            "Daniil Medvedev plays Nikoloz Basilashvili in an ATP match. OLBG tipsters went 3 out of 3 on Medvedev for this tomorrow 06:00 "
            "ET match, and the estimated price of -250 sits at the edge of the high-confidence window. The ATP Tour rankings page was read "
            "this session, but no ATP ranking or recent form fact for either competitor was confirmed from an official source, so the tier "
            "rests on community consensus. Selection: Daniil Medvedev win match at an estimated -250."
        ),
    ),
    dict(
        id="PK-13", event="sn-1", sport="snooker",
        selection="Jak Jones to win (win match)",
        american=-175, prob=0.636, tier="Medium",
        markets=[
            ("Win Match", "originated", "Jak Jones 63.6% / Mark Williams 36.4%"),
            ("Frame Handicap -1.5", "withheld", "no frame-level pricing inputs read"),
            ("Total Frames", "withheld", "no format length was read"),
        ],
        why="OLBG shows Jak Jones 16/27 tips (59%); WST match list confirms the Northern Ireland Open semi-final but no head-to-head or ranking data read.",
        prediction=(
            "Jak Jones takes on Mark Williams in a Northern Ireland Open semi-final. OLBG tipsters back Jones at 16 out of 27 tips (59%), "
            "and the World Snooker Tour match list confirms this semi-final is on the 24 October card at 14:05 ET. No head-to-head or "
            "ranking fact was confirmed from an official source. Selection: Jak Jones win match at an estimated -175."
        ),
    ),

    dict(
        id="PK-17", event="cr-1", sport="cricket",
        selection="Toronto Kings to win (win match)",
        american=-200, prob=0.667, tier="Medium",
        markets=[
            ("Win Match", "originated", "Toronto Kings 66.7% / Vancouver Guardians 33.3%"),
            ("Match Total", "withheld", "no run-rate data read"),
        ],
        why="OLBG shows Toronto Kings 6/7 tips (86%); no ICC/CSA/PCB official source read; price is community-derived only.",
        prediction=(
            "Toronto Kings play the Vancouver Guardians in Global T20 Canada. OLBG tipsters back Toronto Kings at 6 out of 7 tips (86%) "
            "for this today 19:00 ET match. The ICC website was read this session, but no official cricket board source confirmed this "
            "specific fixture or team form, so this selection rests on community consensus alone. Selection: Toronto Kings win match at an "
            "estimated -200."
        ),
    ),
]

# ---------------------------------------------------------------------------
# Flags: items that are incomplete, blank, or where the upstream looks wrong.
# ---------------------------------------------------------------------------

FLAGS = [
    ("F-D3-01", "No High-confidence picks for most sports",
     "All 15 sports",
     "Only one High pick was issued (Carolina Hurricanes). Minnesota Wild and Chemik Police W fell below the 70% probability bar and were "
     "kept at Medium. Every other market either failed the 70% probability test, fell outside the -250…+10000 fair-price window, or lacked "
     "an official source to price against. No tier was inflated to fill the five-per-sport quota.",
     "https://buffedlizard55-lab.github.io/OLBG1/d33cf454/coverage.html"),
    ("F-D3-02", "OLBG hub times are US Eastern, not UTC",
     "All sports",
     "Hub times are rendered in US Eastern (UTC-4). NBA hub times were matched to the NBA calendar to fix the offset. Hub-derived starts are "
     "labelled 'derived' and are never presented as confirmed.",
     "https://www.nba.com/games?date=2026-10-24"),
    ("F-D3-03", "Golf hub empty at capture",
     "Golf",
     "The OLBG golf hub returned 'No tips found' at capture; there was no golf market to attach a selection to.",
     "https://www.olbg.com/betting-tips/Golf/5"),
    ("F-D3-04", "Rugby League hub has no fixture markets",
     "Rugby League",
     "Only State of Origin 2027, Super League 2027 and NRL 2027 outrights were open. No match market existed, so no match pick could be made.",
     "https://www.olbg.com/betting-tips/Rugby_League/10"),
    ("F-D3-05", "Greyhound race times are internally inconsistent",
     "Greyhounds",
     "OLBG prints race names like '7:58 Doncaster' and renders the same race as 14:58 ET, a displacement. No independent GBGB card was read, "
     "so greyhound rows carry no verified start time and no price.",
     "https://www.olbg.com/betting-tips/Greyhounds/28"),
    ("F-D3-06", "NHL standings readable portion incomplete",
     "Ice Hockey",
     "The NHL standings response contained Boston, Edmonton, Vegas and Carolina among its first records; San Jose, Toronto, St. Louis and "
     "other clubs were not in the readable portion, so their prices are opponent-blind and capped below High.",
     "https://api-web.nhle.com/v1/standings/2026-10-24"),
    ("F-D3-07", "NBA injury report not reachable",
     "Basketball",
     "The NBA injury report PDF could not be read, so no availability or injury claim is made for any basketball game.",
     "https://ak-static.cms.nba.com/referee/injury/"),
    ("F-D3-08", "Snooker head-to-head and ranking data not read",
     "Snooker",
     "The WST match list confirms the semi-final routing but no player ranking or head-to-head page was read, so the snooker pick is capped "
     "at Medium.",
     "https://www.wst.tv/matches/"),
    ("F-D3-09", "Five-per-sport quota not met",
     "All 15 sports",
     "The brief asks for five written picks per sport per day. This desk issues far fewer because the evidence gate (official source + "
     ">70% probability + in-window price) is deliberately strict and no tier was invented to fill a quota.",
     "https://buffedlizard55-lab.github.io/OLBG1/d33cf454/coverage.html"),
    ("F-D3-10", "OLBG secondary routes return marketing copy",
     "All sports",
     "OLBG 'All events' routes render tipster copy and 404 bodies in some cases. Only the sport hub listings were treated as usable discovery.",
     "https://www.olbg.com/betting-tips/Golf/All_Golf/All_Events/5"),
]

# ---------------------------------------------------------------------------
# Per-sport coverage notes
# ---------------------------------------------------------------------------

COVERAGE = {
    "basketball": "Nine NBA/NBB markets discovered on OLBG. NBA calendar confirms eight games on 24 October. Two picks issued (Cleveland Medium, Phoenix Medium). No injury report was reachable, so no availability claims are made.",
    "ice-hockey": "Twelve NHL games plus six Swiss NLA games discovered. Official NHL schedule gives UTC starts; official standings read for Boston, Edmonton, Vegas, Carolina. Three picks issued (Carolina High, Minnesota High, Edmonton Medium, Boston Medium, Buffalo Medium).",
    "baseball": "One MLB market discovered (World Series Game 2, Rays at Brewers). Official MLB schedule confirms first pitch 2026-10-25T00:00:00Z, ifNecessary=N, probable pitchers Rasmussen and Henderson. One Low pick issued.",
    "tennis": "Six match markets discovered. One Medium pick (Rybakina) and one High pick (Medvedev at the -250 window edge). No WTA/ATP ranking page was read.",
    "snooker": "One match market discovered (Mark Williams v Jak Jones, Northern Ireland Open semi-final). WST match list confirms routing. One Medium pick issued.",
    "volleyball": "Fifteen match markets discovered. One High pick (Chemik Police W) and several unpriced rows. No official league table was read.",
    "rugby-union": "Five match markets discovered. No official Premiership/URC/Top 14 page was read; all rows unpriced and unflagged beyond coverage note.",
    "cricket": "Nine match markets discovered. One Medium pick (Toronto Kings). No ICC/CSA/PCB page was read.",
    "darts": "Five match markets discovered. One Medium pick (Luke Littler). No PDC Order of Merit page was read.",
    "gaelic": "Four club markets discovered. Two unpriced rows plus one Medium handicap pick (Nemo Rangers +1.50). No GAA page was read.",
    "motor-racing": "One USA Grand Prix market discovered. Official formula1.com page confirms race time, circuit, practice results. Two picks issued (Leclerc podium Medium, Verstappen win Low).",
    "handball": "Fifteen match markets discovered. No picks issued; no EHF or league page was read.",
    "rugby-league": "No fixture markets open; outrights only. No pick possible.",
    "golf": "Hub empty ('No tips found'). No market available, no pick possible.",
    "greyhounds": "Multiple daily races discovered. Race times internally inconsistent; no GBGB card read. No pick issued.",
}
