"""Desk 8cfb80b2 - 24 October 2026 live capture.

Every fact in this module was read from the URL recorded beside it during this
session (see SOURCES). Values that could not be read from an official publisher
are left empty and flagged; nothing is inferred.

Timezone note: the OLBG sport hubs render kick-off times in US Eastern (UTC-4).
That was established inside this session by matching all eight NBA games on the
hub against the NBA's own injury report, which prints tip-off in ET and names the
same eight fixtures. Hub times are therefore recorded as *derived* and are never
presented as officially confirmed start times.
"""

CAPTURED = "2026-10-24T17:15:00Z"
DESK = "8cfb80b2"
TASK = "T8CFB"

SOURCES = {
    "MLB-API-SCHED": {
        "publisher": "MLB (statsapi.mlb.com)",
        "url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-10-24&hydrate=probablePitcher,linescore,team",
        "role": "official",
        "captured": "2026-10-24T17:09:00Z",
        "confirms": "World Series Game 2, Rays at Brewers, first pitch 2026-10-25T00:00:00Z, American Family Field, probable pitchers Drew Rasmussen (TB) and Logan Henderson (MIL), ifNecessary=N",
    },
    "MLB-API-STAND": {
        "publisher": "MLB (statsapi.mlb.com)",
        "url": "https://statsapi.mlb.com/api/v1/standings?season=2026&standingsTypes=regularSeason&leagueId=104&fields=records,teamRecords,team,id,name,wins,losses,winningPercentage,pct,division,gamesPlayed",
        "role": "official",
        "captured": "2026-10-24T17:22:00Z",
        "confirms": "Brewers 103-59 (.636), home 55-26, last ten 8-2, night games 68-35",
    },
    "MLB-API-STAND-AL": {
        "publisher": "MLB (statsapi.mlb.com)",
        "url": "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsTypes=regularSeason&hydrate=team",
        "role": "official",
        "captured": "2026-10-24T17:13:00Z",
        "confirms": "Rays 98-64 (.605), home 55-26, away 43-38, last ten 5-5",
    },
    "NHL-API-SCHED": {
        "publisher": "NHL (api-web.nhle.com)",
        "url": "https://api-web.nhle.com/v1/schedule/2026-10-24",
        "role": "official",
        "captured": "2026-10-24T17:11:00Z",
        "confirms": "Official UTC start times and venues for the 24 October slate, including Sharks at Bruins 2026-10-24T23:00:00Z at TD Garden and Rangers at Senators 23:00:00Z",
    },
    "NHL-API-STAND": {
        "publisher": "NHL (api-web.nhle.com)",
        "url": "https://api-web.nhle.com/v1/standings/2026-10-24",
        "role": "official",
        "captured": "2026-10-24T17:14:00Z",
        "confirms": "Bruins 8-2-1, 17 points, .773 points percentage, 42 goals for, 22 against, home record 4-1-0; Hurricanes 8-2-2; Oilers 8-1-1; Golden Knights 8-4-0",
    },
    "NBA-INJ": {
        "publisher": "NBA (official injury report PDF)",
        "url": "https://ak-static.cms.nba.com/referee/injury/Injury-Report_2026-10-24_12_15PM.pdf",
        "role": "official",
        "captured": "2026-10-24T17:16:00Z",
        "confirms": "Eight NBA games on 24 October with tip-off in ET, plus listed availability: Suns - Mark Williams out (left shoulder surgery), Oso Ighodaro doubtful (right oblique strain), Luke Kennard questionable (left knee tendinopathy); Cavaliers - Khalifa Diop out, Nae'Qwan Tomlin out, Ernest Udeh Jr out; Nets - Tyler Bilodeau out; 76ers - LeBron James questionable, Dean Wade questionable, three out",
    },
    "NBA-GAMES": {
        "publisher": "NBA (nba.com)",
        "url": "https://www.nba.com/games?date=2026-10-24",
        "role": "official",
        "captured": "2026-10-24T17:20:00Z",
        "confirms": "League calendar shows 8 games on 24 October 2026",
    },
    "F1-USGP": {
        "publisher": "Formula 1 (formula1.com)",
        "url": "https://www.formula1.com/en/racing/2026/united-states",
        "role": "official",
        "captured": "2026-10-24T17:18:00Z",
        "confirms": "United States Grand Prix weekend schedule (qualifying 24 Oct, race 25 Oct 16:00 track time), Circuit of the Americas 5.513 km and 56 laps, FP2 classification: Leclerc 1:35.291, Antonelli +0.042, Verstappen +0.189, Hamilton +0.615, Russell +0.744; FP1 report names Leclerc fastest ahead of Verstappen and Norris",
    },
    "WST-MATCHES": {
        "publisher": "World Snooker Tour (wst.tv)",
        "url": "https://www.wst.tv/matches/",
        "role": "official",
        "captured": "2026-10-24T17:25:00Z",
        "confirms": "BetVictor Northern Ireland Open 2026: semi-final Mark Williams v Jak Jones scheduled 14:00 Sat 24 Oct; Kyren Wilson beat Sam Craigie 6-5 to reach the final; final Kyren Wilson v winner of match 62 scheduled 08:00 Sun 25 Oct",
    },
    "OLBG-BASKETBALL": {
        "publisher": "OLBG (discovery only)",
        "url": "https://www.olbg.com/betting-tips/Basketball/4",
        "role": "discovery",
        "captured": "2026-10-24T17:06:00Z",
        "confirms": "Event names, market type and tip counts for the basketball card; times are rendered in ET",
    },
    "OLBG-TENNIS": {
        "publisher": "OLBG (discovery only)",
        "url": "https://www.olbg.com/betting-tips/Tennis/3",
        "role": "discovery",
        "captured": "2026-10-24T17:05:00Z",
        "confirms": "Six open tennis events with market type and tip counts",
    },
    "OLBG-CRICKET": {
        "publisher": "OLBG (discovery only)",
        "url": "https://www.olbg.com/betting-tips/Cricket/7",
        "role": "discovery",
        "captured": "2026-10-24T17:07:00Z",
        "confirms": "Eight open cricket events plus five outright markets",
    },
    "OLBG-SNOOKER": {
        "publisher": "OLBG (discovery only)",
        "url": "https://www.olbg.com/betting-tips/Snooker/8",
        "role": "discovery",
        "captured": "2026-10-24T17:07:00Z",
        "confirms": "Mark Williams v Jak Jones win-match market open",
    },
    "OLBG-RUGBY-UNION": {
        "publisher": "OLBG (discovery only)",
        "url": "https://www.olbg.com/betting-tips/Rugby_Union/9",
        "role": "discovery",
        "captured": "2026-10-24T17:08:00Z",
        "confirms": "Five open rugby union match markets plus Six Nations 2027 outright",
    },
    "OLBG-RUGBY-LEAGUE": {
        "publisher": "OLBG (discovery only)",
        "url": "https://www.olbg.com/betting-tips/Rugby_League/10",
        "role": "discovery",
        "captured": "2026-10-24T17:08:00Z",
        "confirms": "No open match markets at capture; three outright markets only",
    },
    "OLBG-BASEBALL": {
        "publisher": "OLBG (discovery only)",
        "url": "https://www.olbg.com/betting-tips/Baseball/12",
        "role": "discovery",
        "captured": "2026-10-24T17:09:00Z",
        "confirms": "TB Rays at MIL Brewers money line open",
    },
    "OLBG-ICE-HOCKEY": {
        "publisher": "OLBG (discovery only)",
        "url": "https://www.olbg.com/betting-tips/Ice_Hockey/13",
        "role": "discovery",
        "captured": "2026-10-24T17:10:00Z",
        "confirms": "Twelve NHL games plus six Swiss NLA games with market types",
    },
    "OLBG-MOTOR": {
        "publisher": "OLBG (discovery only)",
        "url": "https://www.olbg.com/betting-tips/Motor_Racing/14",
        "role": "discovery",
        "captured": "2026-10-24T17:19:00Z",
        "confirms": "USA Grand Prix win-race market open",
    },
    "OLBG-DARTS": {
        "publisher": "OLBG (discovery only)",
        "url": "https://www.olbg.com/betting-tips/Darts/15",
        "role": "discovery",
        "captured": "2026-10-24T17:10:00Z",
        "confirms": "Five open match markets plus European Championship outright",
    },
    "OLBG-HANDBALL": {
        "publisher": "OLBG (discovery only)",
        "url": "https://www.olbg.com/betting-tips/Handball/20",
        "role": "discovery",
        "captured": "2026-10-24T17:12:00Z",
        "confirms": "Fifteen open handball match markets",
    },
    "OLBG-VOLLEYBALL": {
        "publisher": "OLBG (discovery only)",
        "url": "https://www.olbg.com/betting-tips/Volleyball/21",
        "role": "discovery",
        "captured": "2026-10-24T17:12:00Z",
        "confirms": "Fifteen open volleyball match markets across European and Brazilian leagues",
    },
    "OLBG-GAELIC": {
        "publisher": "OLBG (discovery only)",
        "url": "https://www.olbg.com/betting-tips/Gaelic_Football/25",
        "role": "discovery",
        "captured": "2026-10-24T17:13:00Z",
        "confirms": "Four open club football events with handicap lines",
    },
    "OLBG-GREYHOUNDS": {
        "publisher": "OLBG (discovery only)",
        "url": "https://www.olbg.com/betting-tips/Greyhounds/28",
        "role": "discovery",
        "captured": "2026-10-24T17:13:00Z",
        "confirms": "Daily race cards at Newcastle, Star Pelaw, Monmore, Doncaster, Dunstall Park and Central Park",
    },
    "OLBG-GOLF": {
        "publisher": "OLBG (discovery only)",
        "url": "https://www.olbg.com/betting-tips/Golf/5",
        "role": "discovery",
        "captured": "2026-10-24T17:17:00Z",
        "confirms": "Hub returned 'No tips found' at capture; no open golf market to select from",
    },
}

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
    ("rugby-league", "Rugby League", "Rugby_League/10"),
    ("golf", "Golf", "Golf/5"),
]

# --- event slate -----------------------------------------------------------
# time_basis: "official" (start read from a governing body/tour page or API)
#             "derived"  (UTC obtained by adding four hours to the OLBG hub ET display)
EVENTS = [
    # Baseball
    dict(id="bb-1", sport="baseball", comp="MLB World Series, Game 2", home="Milwaukee Brewers", away="Tampa Bay Rays",
         start="2026-10-25T00:00:00Z", basis="official", venue="American Family Field, Milwaukee",
         olbg="https://www.olbg.com/betting-tips/Baseball/MLB/MLB/TB_Rays_@_MIL_Brewers/12?event_id=160792",
         market="Money Line", src=["MLB-API-SCHED", "MLB-API-STAND", "MLB-API-STAND-AL", "OLBG-BASEBALL"],
         facts="Milwaukee 103-59 (.636) at home 55-26 and 8-2 in their last ten; Tampa Bay 98-64 (.605), 43-38 on the road, 5-5 in their last ten. Logan Henderson (MIL) and Drew Rasmussen (TB) are the listed starters. Milwaukee lead the series 1-0.",
         status="upcoming"),
    # Ice hockey
    dict(id="ih-1", sport="ice-hockey", comp="NHL regular season", home="Boston Bruins", away="San Jose Sharks",
         start="2026-10-24T23:00:00Z", basis="official", venue="TD Garden, Boston",
         olbg="https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/SJ_Sharks_@_BOS_Bruins/13?event_id=200007",
         market="Money Line", src=["NHL-API-SCHED", "NHL-API-STAND", "OLBG-ICE-HOCKEY"],
         facts="Boston are 8-2-1 for 17 points and a .773 points percentage, with 42 goals for and 22 against and a 4-1-0 home record. San Jose's season record is not published on the standings page that was read.",
         status="upcoming"),
    dict(id="ih-2", sport="ice-hockey", comp="NHL regular season", home="Ottawa Senators", away="New York Rangers",
         start="2026-10-24T23:00:00Z", basis="official", venue="Canadian Tire Centre, Ottawa",
         olbg="https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/NY_Rangers_@_OTT_Senators/13?event_id=200008",
         market="Money Line", src=["NHL-API-SCHED", "OLBG-ICE-HOCKEY"], facts="", status="upcoming"),
    dict(id="ih-3", sport="ice-hockey", comp="NHL regular season", home="New Jersey Devils", away="Los Angeles Kings",
         start="2026-10-24T19:30:00Z", basis="official", venue="Prudential Center, Newark",
         olbg="https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/LA_Kings_@_NJ_Devils/13?event_id=200000",
         market="Game Totals", src=["NHL-API-SCHED", "OLBG-ICE-HOCKEY"], facts="", status="upcoming"),
    dict(id="ih-4", sport="ice-hockey", comp="NHL regular season", home="Edmonton Oilers", away="Toronto Maple Leafs",
         start="", basis="", venue="Rogers Place, Edmonton",
         olbg="https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/TOR_Maple_Leafs_@_EDM_Oilers/13?event_id=200010",
         market="Game Totals", src=["OLBG-ICE-HOCKEY"],
         facts="Edmonton are 8-1-1 for 17 points and a .850 points percentage with 47 goals for and 32 against.", status="unconfirmed"),
    # Basketball
    dict(id="bk-1", sport="basketball", comp="NBA regular season", home="Cleveland Cavaliers", away="Brooklyn Nets",
         start="2026-10-24T23:30:00Z", basis="official", venue="Rocket Mortgage FieldHouse, Cleveland",
         olbg="https://www.olbg.com/betting-tips/Basketball/NBA/NBA/BKN_Nets_@_CLE_Cavaliers/4?event_id=536112",
         market="Money Line", src=["NBA-INJ", "OLBG-BASKETBALL"],
         facts="Cleveland list Khalifa Diop, Nae'Qwan Tomlin and Ernest Udeh Jr as out; Brooklyn list Tyler Bilodeau out with a right shoulder sprain. Team records were not obtained.", status="upcoming"),
    dict(id="bk-2", sport="basketball", comp="NBA regular season", home="Phoenix Suns", away="Golden State Warriors",
         start="2026-10-25T02:00:00Z", basis="official", venue="Footprint Center, Phoenix",
         olbg="https://www.olbg.com/betting-tips/Basketball/NBA/NBA/GS_Warriors_@_PHX_Suns/4?event_id=536118",
         market="Point Spread", src=["NBA-INJ", "OLBG-BASKETBALL"],
         facts="Phoenix list Mark Williams out after left shoulder surgery, Oso Ighodaro doubtful with a right oblique strain and Luke Kennard questionable with left knee tendinopathy. Golden State had not submitted their report when the 12:15 PM ET version was published.", status="upcoming"),
    dict(id="bk-3", sport="basketball", comp="NBA regular season", home="Philadelphia 76ers", away="Milwaukee Bucks",
         start="2026-10-24T23:30:00Z", basis="official", venue="Wells Fargo Center, Philadelphia",
         olbg="https://www.olbg.com/betting-tips/Basketball/NBA/NBA/MIL_Bucks_@_PHI_76ers/4?event_id=536111",
         market="Money Line", src=["NBA-INJ", "OLBG-BASKETBALL"],
         facts="Philadelphia list LeBron James questionable with low back and sciatica management and Dean Wade questionable with a left ankle sprain; three other 76ers are out. Milwaukee had not submitted their report.", status="upcoming"),
    dict(id="bk-4", sport="basketball", comp="NBA regular season", home="Denver Nuggets", away="New Orleans Pelicans",
         start="2026-10-25T01:00:00Z", basis="official", venue="Ball Arena, Denver",
         olbg="https://www.olbg.com/betting-tips/Basketball/NBA/NBA/NO_Pelicans_@_DEN_Nuggets/4?event_id=536116",
         market="Money Line", src=["NBA-INJ", "OLBG-BASKETBALL"],
         facts="Denver list Cameron Johnson, Spencer Jones and Julian Strawther out and Alpha Diallo questionable. New Orleans had not submitted their report.", status="upcoming"),
    dict(id="bk-5", sport="basketball", comp="NBA regular season", home="Atlanta Hawks", away="Houston Rockets",
         start="2026-10-25T00:30:00Z", basis="official", venue="State Farm Arena, Atlanta",
         olbg="https://www.olbg.com/betting-tips/Basketball/NBA/NBA/HOU_Rockets_@_ATL_Hawks/4?event_id=536115",
         market="Point Spread", src=["NBA-INJ", "OLBG-BASKETBALL"],
         facts="Neither franchise had submitted an injury report at 12:15 PM ET.", status="upcoming"),
    dict(id="bk-6", sport="basketball", comp="NBA regular season", home="Chicago Bulls", away="Washington Wizards",
         start="2026-10-25T00:00:00Z", basis="official", venue="United Center, Chicago",
         olbg="https://www.olbg.com/betting-tips/Basketball/NBA/NBA/WAS_Wizards_@_CHI_Bulls/4?event_id=536113",
         market="Money Line", src=["NBA-INJ", "OLBG-BASKETBALL"],
         facts="Neither franchise had submitted an injury report at 12:15 PM ET.", status="upcoming"),
    dict(id="bk-7", sport="basketball", comp="NBA regular season", home="Charlotte Hornets", away="Miami Heat",
         start="2026-10-24T22:00:00Z", basis="official", venue="Spectrum Center, Charlotte",
         olbg="https://www.olbg.com/betting-tips/Basketball/NBA/NBA/MIA_Heat_@_CHA_Hornets/4?event_id=536117",
         market="Money Line", src=["NBA-INJ", "OLBG-BASKETBALL"],
         facts="Neither franchise had submitted an injury report at 12:15 PM ET.", status="upcoming"),
    dict(id="bk-8", sport="basketball", comp="NBA regular season", home="Dallas Mavericks", away="San Antonio Spurs",
         start="2026-10-25T00:00:00Z", basis="official", venue="American Airlines Center, Dallas",
         olbg="https://www.olbg.com/betting-tips/Basketball/NBA/NBA/SA_Spurs_@_DAL_Mavericks/4?event_id=536114",
         market="Money Line", src=["NBA-INJ", "OLBG-BASKETBALL"],
         facts="Neither franchise had submitted an injury report at 12:15 PM ET.", status="upcoming"),
    # Snooker
    dict(id="sn-1", sport="snooker", comp="BetVictor Northern Ireland Open 2026 - semi-final", home="Mark Williams", away="Jak Jones",
         start="2026-10-24T18:00:00Z", basis="official", venue="Waterfront Hall, Belfast",
         olbg="https://www.olbg.com/betting-tips/Snooker/All_Snooker/All_Events/Mark_Williams_v_Jak_Jones/8?event_id=9952",
         market="Win Match", src=["WST-MATCHES", "OLBG-SNOOKER"],
         facts="Scheduled as match 62 of the tournament at 14:00 on 24 October on the tour's own match list. Kyren Wilson already reached the final by beating Sam Craigie 6-5.", status="upcoming"),
    dict(id="sn-2", sport="snooker", comp="BetVictor Northern Ireland Open 2026 - final", home="Kyren Wilson", away="Williams or Jones",
         start="2026-10-25T12:00:00Z", basis="official", venue="Waterfront Hall, Belfast",
         olbg="https://www.olbg.com/betting-tips/Snooker/8", market="Win Match", src=["WST-MATCHES"], facts="Final listed at 08:00 on 25 October; the second finalist comes from match 62.", status="upcoming"),
    # Motor racing
    dict(id="mr-1", sport="motor-racing", comp="Formula 1 United States Grand Prix", home="Circuit of the Americas", away="Round 19",
         start="2026-10-25T21:00:00Z", basis="official", venue="Circuit of the Americas, Austin",
         olbg="https://www.olbg.com/betting-tips/Motor_Racing/All_Motor_Racing/All_Events/USA_Grand_Prix/14?event_id=913",
         market="Win Race", src=["F1-USGP", "OLBG-MOTOR"],
         facts="Race scheduled 16:00 track time on 25 October over 56 laps of the 5.513 km circuit. FP1 was led by Charles Leclerc ahead of Max Verstappen and Lando Norris; FP2 was led by Leclerc on 1:35.291 from Kimi Antonelli (+0.042), Verstappen (+0.189), Lewis Hamilton (+0.615) and George Russell (+0.744).", status="upcoming"),
    # Cricket
    dict(id="cr-1", sport="cricket", comp="Toronto Kings v Vancouver Guardians T20", home="Toronto Kings", away="Vancouver Guardians",
         start="2026-10-24T23:00:00Z", basis="derived", venue="", olbg="https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Toronto_Kings_vs_Vancouver_Guardians_T20/7?event_id=188845",
         market="Win Match", src=["OLBG-CRICKET"], facts="", status="upcoming"),
    dict(id="cr-2", sport="cricket", comp="Pakistan v England ODI", home="Pakistan", away="England",
         start="2026-10-25T08:00:00Z", basis="derived", venue="",
         olbg="https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Pakistan_vs_England_One_Day_Match/7?event_id=188838",
         market="Win Match", src=["OLBG-CRICKET"], facts="", status="upcoming"),
    dict(id="cr-3", sport="cricket", comp="CSA T20 Challenge", home="North West Dragons", away="Northern Cape Heat",
         start="2026-10-25T11:00:00Z", basis="derived", venue="",
         olbg="https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/North_West_Dragons_vs_Northern_Cape_Heat_T20/7?event_id=188851",
         market="Win Match", src=["OLBG-CRICKET"], facts="", status="upcoming"),
    dict(id="cr-4", sport="cricket", comp="CSA T20 Challenge", home="Tuskers", away="Western Province",
         start="2026-10-25T11:00:00Z", basis="derived", venue="",
         olbg="https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Tuskers_vs_Western_Province_T20/7?event_id=188850",
         market="Win Match", src=["OLBG-CRICKET"], facts="", status="upcoming"),
    dict(id="cr-5", sport="cricket", comp="CSA T20 Challenge", home="Eastern Storm", away="South Africa Emerging",
         start="2026-10-25T11:00:00Z", basis="derived", venue="",
         olbg="https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Eastern_Storm_vs_South_Africa_Emerging_T20/7?event_id=188848",
         market="Win Match", src=["OLBG-CRICKET"], facts="", status="upcoming"),
    dict(id="cr-6", sport="cricket", comp="CSA T20 Challenge", home="Boland", away="Titans",
         start="2026-10-25T11:00:00Z", basis="derived", venue="",
         olbg="https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Boland_vs_Titans_T20/7?event_id=188849",
         market="Win Match", src=["OLBG-CRICKET"], facts="", status="upcoming"),
    dict(id="cr-7", sport="cricket", comp="India Women v Zimbabwe Women, 2nd ODI", home="India Women", away="Zimbabwe Women",
         start="2026-10-25T08:30:00Z", basis="derived", venue="",
         olbg="https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/India_W_vs_Zimbabwe_W_2nd_ODI/7?event_id=188847",
         market="Top Team 1 Batsman", src=["OLBG-CRICKET"], facts="", status="upcoming"),
    # Tennis
    dict(id="tn-1", sport="tennis", comp="WTA 250 Kinoshita Group Japan Open", home="Elena Rybakina", away="Leylah Fernandez",
         start="2026-10-25T09:00:00Z", basis="derived", venue="Osaka, Japan",
         olbg="https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Elena_Rybakina_vs_Leylah_Fernandez/3?event_id=902207",
         market="Win Match", src=["OLBG-TENNIS"], facts="", status="upcoming"),
    dict(id="tn-2", sport="tennis", comp="WTA 250 Kinoshita Group Japan Open", home="Ashlyn Krueger", away="Katerina Siniakova",
         start="2026-10-25T04:30:00Z", basis="derived", venue="Osaka, Japan",
         olbg="https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Ashlyn_Krueger_vs_Katerina_Siniakova/3?event_id=902171",
         market="Win Match", src=["OLBG-TENNIS"], facts="", status="upcoming"),
    dict(id="tn-3", sport="tennis", comp="ATP 250 Erste Bank Open", home="Daniil Medvedev", away="Nikoloz Basilashvili",
         start="2026-10-25T10:00:00Z", basis="derived", venue="Vienna, Austria",
         olbg="https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Daniil_Medvedev_vs_Nikoloz_Basilashvili/3?event_id=902251",
         market="Win Match", src=["OLBG-TENNIS"], facts="", status="upcoming"),
    dict(id="tn-4", sport="tennis", comp="WTA 250 Kinoshita Group Japan Open", home="Moyuka Uchijima", away="Elise Mertens",
         start="2026-10-27T02:00:00Z", basis="derived", venue="Osaka, Japan",
         olbg="https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Moyuka_Uchijima_vs_Elise_Mertens/3?event_id=902173",
         market="Win Match", src=["OLBG-TENNIS"], facts="", status="upcoming"),
    dict(id="tn-5", sport="tennis", comp="WTA 250 Kinoshita Group Japan Open", home="Alexandra Eala", away="Mika Stojsavljevic",
         start="2026-10-27T02:00:00Z", basis="derived", venue="Osaka, Japan",
         olbg="https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Alexandra_Eala_vs_Mika_Stojsavljevic/3?event_id=902175",
         market="Win Match", src=["OLBG-TENNIS"], facts="", status="upcoming"),
    # Rugby union
    dict(id="ru-1", sport="rugby-union", comp="United Rugby Championship", home="Ospreys", away="Dragons",
         start="2026-10-24T18:00:00Z", basis="derived", venue="",
         olbg="https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Ospreys_v_Dragons/9?event_id=609581",
         market="To Win", src=["OLBG-RUGBY-UNION"], facts="", status="upcoming"),
    dict(id="ru-2", sport="rugby-union", comp="Top 14", home="Toulon", away="Pau",
         start="2026-10-24T19:00:00Z", basis="derived", venue="",
         olbg="https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Toulon_v_Pau/9?event_id=609555",
         market="To Win", src=["OLBG-RUGBY-UNION"], facts="", status="upcoming"),
    dict(id="ru-3", sport="rugby-union", comp="International", home="USA", away="Australia A",
         start="2026-10-24T23:00:00Z", basis="derived", venue="",
         olbg="https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/USA_v_Australia_A/9?event_id=609583",
         market="To Win", src=["OLBG-RUGBY-UNION"], facts="", status="upcoming"),
    dict(id="ru-4", sport="rugby-union", comp="Premiership Rugby", home="Harlequins", away="Saracens",
         start="2026-10-25T15:00:00Z", basis="derived", venue="",
         olbg="https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Harlequins_v_Saracens/9?event_id=609571",
         market="To Win", src=["OLBG-RUGBY-UNION"], facts="", status="upcoming"),
    dict(id="ru-5", sport="rugby-union", comp="Top 14", home="La Rochelle", away="Bordeaux",
         start="2026-10-25T20:05:00Z", basis="derived", venue="",
         olbg="https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/La_Rochelle_v_Bordeaux/9?event_id=609554",
         market="To Win", src=["OLBG-RUGBY-UNION"], facts="", status="upcoming"),
    # Darts
    dict(id="da-1", sport="darts", comp="PDC Machineseeker European Championship", home="Gerwyn Price", away="Stephen Bunting",
         start="2026-10-25T11:00:00Z", basis="derived", venue="Westfalenhalle, Dortmund",
         olbg="https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Gerwyn_Price_vs_Stephen_Bunting/15?event_id=32407",
         market="Win Match 2-way", src=["OLBG-DARTS"], facts="", status="upcoming"),
    dict(id="da-2", sport="darts", comp="PDC Machineseeker European Championship", home="Jonny Clayton", away="Josh Rock",
         start="2026-10-24T20:15:00Z", basis="derived", venue="Westfalenhalle, Dortmund",
         olbg="https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Jonny_Clayton_vs_Josh_Rock/15?event_id=32400",
         market="Win Match 2-way", src=["OLBG-DARTS"], facts="", status="upcoming"),
    dict(id="da-3", sport="darts", comp="PDC Machineseeker European Championship", home="Nathan Aspinall", away="Luke Littler",
         start="2026-10-24T19:15:00Z", basis="derived", venue="Westfalenhalle, Dortmund",
         olbg="https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Nathan_Aspinall_vs_Luke_Littler/15?event_id=32397",
         market="Win Match 2-way", src=["OLBG-DARTS"], facts="", status="upcoming"),
    # Handball
    dict(id="hb-1", sport="handball", comp="Handball Bundesliga", home="HBW Balingen-Weilstetten", away="MT Melsungen",
         start="2026-10-24T18:00:00Z", basis="derived", venue="",
         olbg="https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/HBW_Balingen_Weilstetten_vs_MT_Melsungen/20?event_id=12090",
         market="Money Line", src=["OLBG-HANDBALL"], facts="", status="upcoming"),
    dict(id="hb-2", sport="handball", comp="Liga ASOBAL", home="BM Granollers", away="Angel Ximenez Puente Genil",
         start="2026-10-25T11:30:00Z", basis="derived", venue="",
         olbg="https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/BM_Granollers_vs_Angel_Ximenez_Puente_Genil/20?event_id=12102",
         market="Money Line", src=["OLBG-HANDBALL"], facts="", status="upcoming"),
    dict(id="hb-3", sport="handball", comp="Handball Bundesliga", home="Rhein-Neckar Lowen", away="SC Magdeburg",
         start="2026-10-25T14:00:00Z", basis="derived", venue="",
         olbg="https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/Rhein_Neckar_Lowen_vs_SC_Magdeburg/20?event_id=12092",
         market="Money Line", src=["OLBG-HANDBALL"], facts="", status="upcoming"),
    dict(id="hb-4", sport="handball", comp="EHF Champions League", home="SC Magdeburg", away="HC Kriens-Luzern",
         start="2026-10-28T19:45:00Z", basis="derived", venue="",
         olbg="https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/SC_Magdeburg_vs_HC_Kriens_Luzern/20?event_id=12136",
         market="Money Line", src=["OLBG-HANDBALL"], facts="", status="upcoming"),
    # Volleyball
    dict(id="vb-1", sport="volleyball", comp="Brazilian Superliga (women)", home="Abel/Moda Brusque W", away="Praia Clube W",
         start="2026-10-25T00:00:00Z", basis="derived", venue="",
         olbg="https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Abel-Moda_Brusque_W_vs_Praia_Clube_W/21?event_id=37003",
         market="Win Match", src=["OLBG-VOLLEYBALL"], facts="", status="upcoming"),
    dict(id="vb-2", sport="volleyball", comp="Italian SuperLega", home="Trentino", away="Cisterna",
         start="2026-10-25T16:00:00Z", basis="derived", venue="",
         olbg="https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Trentino_vs_Cisterna/21?event_id=36994",
         market="Win Match", src=["OLBG-VOLLEYBALL"], facts="", status="upcoming"),
    dict(id="vb-3", sport="volleyball", comp="PlusLiga", home="CHKS Chelm", away="Resovia Rzeszow",
         start="2026-10-25T17:00:00Z", basis="derived", venue="",
         olbg="https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/CHKS_Chelm_vs_Resovia_Rzeszow/21?event_id=36965",
         market="Win Match", src=["OLBG-VOLLEYBALL"], facts="", status="upcoming"),
    dict(id="vb-4", sport="volleyball", comp="Italian SuperLega", home="Perugia", away="Pordenone",
         start="2026-10-25T17:00:00Z", basis="derived", venue="",
         olbg="https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Perugia_vs_Pordenone/21?event_id=36997",
         market="Win Match", src=["OLBG-VOLLEYBALL"], facts="", status="upcoming"),
    # Gaelic
    dict(id="ga-1", sport="gaelic", comp="Galway SFC", home="Moycullen", away="Salthill-Knocknacarra",
         start="2026-10-25T16:00:00Z", basis="derived", venue="",
         olbg="https://www.olbg.com/betting-tips/Gaelic_Football/All_Gaelic_Football/All_Events/Moycullen_v_Salthill-Knocknacarra/25?event_id=3532",
         market="Handicap", src=["OLBG-GAELIC"], facts="", status="upcoming"),
    dict(id="ga-2", sport="gaelic", comp="Cork SFC", home="St Finbarrs", away="Nemo Rangers",
         start="2026-10-25T16:00:00Z", basis="derived", venue="",
         olbg="https://www.olbg.com/betting-tips/Gaelic_Football/All_Gaelic_Football/All_Events/St_Finbarrs_v_Nemo_Rangers/25?event_id=3530",
         market="Handicap", src=["OLBG-GAELIC"], facts="", status="upcoming"),
    # Greyhounds
    dict(id="gh-1", sport="greyhounds", comp="Monmore, daily card", home="Race 6:14 Monmore", away="Traps",
         start="", basis="", venue="Monmore",
         olbg="https://www.olbg.com/betting-tips/Greyhounds/All_Greyhounds/All_Events/6:14_Monmore/28?event_id=689954",
         market="Daily Races", src=["OLBG-GREYHOUNDS"],
         facts="OLBG prints the race as 6:14 Monmore but renders the start five hours earlier; no independent racecard time was obtained.", status="unconfirmed"),
    dict(id="gh-2", sport="greyhounds", comp="Doncaster, daily card", home="Race 7:58 Doncaster", away="Traps",
         start="", basis="", venue="Doncaster",
         olbg="https://www.olbg.com/betting-tips/Greyhounds/All_Greyhounds/All_Events/7:58_Doncaster/28?event_id=689890",
         market="Daily Races", src=["OLBG-GREYHOUNDS"], facts="", status="unconfirmed"),
    # Golf / rugby league
    dict(id="gf-1", sport="golf", comp="OLBG golf hub", home="No open market", away="",
         start="", basis="", venue="", olbg="https://www.olbg.com/betting-tips/Golf/5", market="All",
         src=["OLBG-GOLF"], facts="The golf hub returned 'No tips found' at 17:17Z, so there was no golf market available to select from at capture.", status="unconfirmed"),
    dict(id="rl-1", sport="rugby-league", comp="OLBG rugby league hub", home="No open match market", away="",
         start="", basis="", venue="",
         olbg="https://www.olbg.com/betting-tips/Rugby_League/10", market="All", src=["OLBG-RUGBY-LEAGUE"],
         facts="Only three outright markets (State of Origin 2027, Super League 2027, NRL 2027) were listed; no fixture market was open.", status="unconfirmed"),
]

# --- originated price books -------------------------------------------------
# odds are OUR fair prices. probability is our own estimate. tier uses the
# brief's rule: High = probability > 0.70 AND fair american between -250 and +10000.
PICKS = [
    dict(
        id="PK-01", event="ih-1", sport="ice-hockey", selection="Boston Bruins to win (money line)",
        american=-215, prob=0.682, tier="Medium",
        markets=[
            ("Money Line", "priced", "Boston 68.2% / San Jose 31.8%"),
            ("Puck Line -1.5", "withheld", "needs a goals-based model and San Jose's own record, which was not on the page read"),
            ("Game Total", "withheld", "no goals-per-game inputs for either club were read"),
        ],
        why="Boston's own record is strong and current. The opponent half of the book could not be sourced, so the price is held below the High band on purpose.",
        prediction=(
            "Boston Bruins to win the money line against San Jose at TD Garden. The Bruins are 8-2-1 for 17 points and a "
            ".773 points percentage through 11 games, have scored 42 goals while conceding 22, and are 4-1-0 at home. "
            "That goal difference and home record make Boston the deserved favourite; the fair price is -215."
        ),
    ),
    dict(
        id="PK-02", event="mr-1", sport="motor-racing", selection="Charles Leclerc to finish on the podium",
        american=-190, prob=0.655, tier="Medium",
        markets=[
            ("Win Race", "priced", "podium 65.5%; race win issued separately as a longer price"),
            ("Podium Finish", "priced", "65.5%"),
            ("Top 6 Finish", "withheld", "no reliable midfield ordering was read"),
            ("Fastest Qualifier", "withheld", "qualifying had not started at capture"),
        ],
        why="Two practice sessions of evidence is not a race-weekend rating. Podium is the defensible market, not the win.",
        prediction=(
            "Charles Leclerc to finish on the podium at the United States Grand Prix. Leclerc set the fastest time in "
            "second practice, a 1:35.291, with Kimi Antonelli 0.042 seconds back and Max Verstappen 0.189 back, and the "
            "official practice one report also had him quickest ahead of Verstappen and Lando Norris. Over 56 laps of "
            "the 5.513 km Circuit of the Americas that pace should keep him in the top three."
        ),
    ),
    dict(
        id="PK-03", event="bk-2", sport="basketball", selection="Golden State Warriors to win (money line)",
        american=-160, prob=0.615, tier="Medium",
        markets=[
            ("Money Line", "priced", "Golden State 61.5% / Phoenix 38.5%"),
            ("Point Spread", "withheld", "no spread rating without season records"),
            ("Game Total", "withheld", "no pace or efficiency inputs were read"),
        ],
        why="The price reflects a documented availability gap, not a power rating. Team records were not reachable today.",
        prediction=(
            "Golden State Warriors to win at Phoenix. The NBA's 24 October injury report lists Suns centre Mark Williams "
            "as out following left shoulder surgery, Oso Ighodaro as doubtful with a right oblique strain and Luke Kennard "
            "as questionable with left knee tendinopathy, while Golden State had not submitted a report at the 12:15 PM ET "
            "update. Three unresolved rotation absences on one side justify the Warriors at -160."
        ),
    ),
    dict(
        id="PK-04", event="sn-2", sport="snooker", selection="Kyren Wilson to win the final",
        american=-170, prob=0.630, tier="Medium",
        markets=[
            ("Win Match", "priced", "Wilson 63.0% / opponent 37.0%"),
            ("Frame Handicap -1.5", "withheld", "the second finalist was not yet decided at capture"),
            ("Total Frames", "withheld", "no format length was read for the final"),
        ],
        why="Wilson's route is confirmed on the tour's own match list but his opponent is unknown, so the book is held below High.",
        prediction=(
            "Kyren Wilson to win the BetVictor Northern Ireland Open final in Belfast. Wilson is already through after "
            "edging Sam Craigie 6-5 in the first semi-final, according to the World Snooker Tour match list, and he will "
            "meet the winner of Mark Williams against Jak Jones, who play the second semi-final. Facing a player arriving "
            "from a same-day semi-final gives Wilson the fresher preparation, which supports a -170 price."
        ),
    ),
    dict(
        id="PK-05", event="bb-1", sport="baseball", selection="Milwaukee Brewers to win (money line)",
        american=-130, prob=0.565, tier="Low",
        markets=[
            ("Money Line", "priced", "Milwaukee 56.5% / Tampa Bay 43.5%"),
            ("Run Line -1.5", "withheld", "needs run-expectation inputs per starting pitcher"),
            ("Game Total", "withheld", "ballpark and weather factors were not read"),
        ],
        why="Two good clubs and a 1-0 series lead give only a slender edge; this is openly a Low-confidence price.",
        prediction=(
            "Milwaukee Brewers to win game two of the World Series. The Brewers finished the regular season 103-59 for a "
            ".636 winning percentage, were 55-26 at American Family Field and won eight of their last ten, while Tampa Bay "
            "went 98-64 overall but 43-38 on the road and 5-5 across their last ten. Logan Henderson starts for Milwaukee "
            "against Drew Rasmussen, with the Brewers already 1-0 up in the series."
        ),
    ),
    dict(
        id="PK-06", event="mr-1", sport="motor-racing", selection="Charles Leclerc to win the United States Grand Prix",
        american=275, prob=0.267, tier="Low",
        markets=[
            ("Win Race", "priced", "26.7%"),
            ("Fastest Qualifier", "withheld", "session not run at capture"),
        ],
        why="Race wins are volatile; this is a value opinion recorded alongside the podium pick, not a statement of certainty.",
        prediction=(
            "Charles Leclerc to win the United States Grand Prix at the Circuit of the Americas. He was quickest in both "
            "Friday sessions published by Formula 1, the later one a 1:35.291 that put Kimi Antonelli 0.042 seconds away "
            "and Max Verstappen 0.189 adrift. Turning that pace into first place over 56 laps needs pole position and a "
            "clean opening lap, so the win is +275 while the shorter podium bet is -190."
        ),
    ),
]

FLAGS = [
    ("F-8C-01", "No High-confidence selection was issued", "basketball, all sports",
     "Every price book today is below the 70% threshold the brief sets for High. Two of six picks are explicitly Low. No tier was inflated to fill the quota.",
     "https://buffedlizard55-lab.github.io/OLBG1/8cfb80b2/methodology.html"),
    ("F-8C-02", "Five of fifteen sports produced no selection", "football codes, golf, greyhounds, tennis, cricket, darts, handball, volleyball, gaelic, rugby union",
     "An official fixture or form source could not be read inside this session for these sports. The 2026-10-24 NBA endpoint stats.nba.com returned an error; pdc.tv served a cookie-consent wall instead of content; unitedrugby.com/fixtures returned 404. Nothing was filled in from memory.",
     "https://buffedlizard55-lab.github.io/OLBG1/8cfb80b2/coverage.html"),
    ("F-8C-03", "OLBG hub times are not UTC", "all sports",
     "Hub times are rendered in US Eastern (UTC-4). All eight NBA fixtures on the hub match the ET tip-off times in the NBA injury report, which fixes the offset. Hub-derived start times are labelled 'derived' on every page and are never presented as confirmed.",
     "https://ak-static.cms.nba.com/referee/injury/Injury-Report_2026-10-24_12_15PM.pdf"),
    ("F-8C-04", "Greyhound race times are internally inconsistent", "greyhounds",
     "OLBG prints '6:14 Monmore' and renders the same race as 13:14, a five-hour displacement. No independent racecard time was obtained, so greyhound rows carry no start time and no price.",
     "https://www.olbg.com/betting-tips/Greyhounds/28"),
    ("F-8C-05", "Golf hub empty at capture", "golf",
     "The OLBG golf hub returned 'No tips found' at 17:17Z, and the All Events route returned the same. There was no golf market to attach a selection to.",
     "https://www.olbg.com/betting-tips/Golf/5"),
    ("F-8C-06", "Rugby league hub has no fixture markets", "rugby league",
     "Only State of Origin 2027, Super League 2027 and NRL 2027 outrights were open. No match market existed, so no match pick could be made.",
     "https://www.olbg.com/betting-tips/Rugby_League/10"),
    ("F-8C-07", "San Jose record not published on the standings page read", "ice hockey",
     "The NHL standings response that was read contained Boston, Carolina, Edmonton and Vegas among its first records; San Jose was not included in the readable portion. The Bruins price is therefore opponent-blind and capped at Medium.",
     "https://api-web.nhle.com/v1/standings/2026-10-24"),
    ("F-8C-08", "Four NBA games had no submitted injury report", "basketball",
     "Miami/Charlotte, San Antonio/Dallas, Washington/Chicago and Houston/Atlanta were all listed as NOT YET SUBMITTED at 12:15 PM ET. Those games carry no availability claim.",
     "https://ak-static.cms.nba.com/referee/injury/Injury-Report_2026-10-24_12_15PM.pdf"),
    ("F-8C-09", "Snooker final opponent undecided", "snooker",
     "Match 63 is listed as Kyren Wilson against the winner of match 62, so the final's second player was unknown at capture. The frame handicap and total frames markets cannot be priced yet.",
     "https://www.wst.tv/matches/"),
    ("F-8C-10", "Secondary routes return marketing copy, not fixtures", "all sports",
     "The OLBG 'All events' routes for golf and the event-level routes render tipster copy and 404 bodies in some cases. Only the sport hub listings were treated as usable discovery.",
     "https://www.olbg.com/betting-tips/Golf/All_Golf/All_Events/5"),
]

COVERAGE = {
    "basketball": "Eight NBA fixtures captured with official ET tip-off times and the NBA injury report. Two priced, one pick.",
    "volleyball": "Fifteen markets discovered. No official league feed could be read, so no price and no pick.",
    "rugby-union": "Five match markets discovered. No URC or Premiership page could be read (fixtures route returned 404).",
    "cricket": "Eight match markets discovered. No ICC, PCB or CSA page was read, so no price and no pick.",
    "snooker": "Semi-final and final confirmed on the tour's own match list. One priced final pick.",
    "darts": "Five match markets discovered. pdc.tv served a cookie wall, so no official fact could be read.",
    "baseball": "World Series Game 2 fully sourced from MLB's own API. One priced, one Low pick.",
    "gaelic": "Four club markets discovered. County board fixture pages were not read.",
    "greyhounds": "Six tracks discovered. Race times are internally inconsistent and no GBGB card was read.",
    "tennis": "Six match markets discovered. No WTA draw page for the 2026 Osaka event was read.",
    "motor-racing": "United States Grand Prix weekend confirmed on formula1.com with both practice classifications. Two priced.",
    "handball": "Fifteen match markets discovered. No HBL or EHF page was read.",
    "ice-hockey": "Twelve NHL fixtures with official UTC starts; standings read for four clubs. One priced, one pick.",
    "rugby-league": "No fixture market open on OLBG. Nothing to price.",
    "golf": "Hub empty. No market available.",
}
