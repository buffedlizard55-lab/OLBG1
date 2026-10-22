"""Fresh, manually transcribed official observations for session 2aeea682-olbg1.

Every fixture literal below was read through Arena's page-fetch/search tools on
2026-10-22 between 20:49 and 20:55 UTC. OLBG is used only for discovery and
market-taxonomy reading, never as official confirmation of a sporting fact.
Blank fields are deliberate: no timezone, venue, participant or statistic is
inferred to make a row look complete.
"""

SESSION = "2aeea682-olbg1"
TASK = "T2AEE"
READ_AT_UTC = "2026-10-22T20:55:00Z"
WINDOW_UNTIL_UTC = "2026-10-29T20:55:00Z"

SPORTS = [
    ("tennis", "Tennis", 3, "Tennis"),
    ("basketball", "Basketball", 4, "Basketball"),
    ("golf", "Golf", 5, "Golf"),
    ("cricket", "Cricket", 7, "Cricket"),
    ("snooker", "Snooker", 8, "Snooker"),
    ("rugby-union", "Rugby union", 9, "Rugby_Union"),
    ("rugby-league", "Rugby league", 10, "Rugby_League"),
    ("baseball", "Baseball", 12, "Baseball"),
    ("ice-hockey", "Ice hockey", 13, "Ice_Hockey"),
    ("motor-racing", "Motor racing", 14, "Motor_Racing"),
    ("darts", "Darts", 15, "Darts"),
    ("handball", "Handball", 20, "Handball"),
    ("volleyball", "Volleyball", 21, "Volleyball"),
    ("aussie-rules", "Aussie rules", 22, "Aussie_Rules"),
    ("esports", "eSports", 23, "eSports"),
    ("gaelic-football", "Gaelic football", 25, "Gaelic_Football"),
    ("greyhounds", "Greyhounds", 28, "Greyhounds"),
]
SPORT_NAMES = {s: n for s, n, _, _ in SPORTS}
EXCLUDED = ["soccer/football", "American football", "boxing", "UFC/MMA", "hurling", "horse racing", "cycling", "specials"]

OFFICIAL_HOSTS = {
    "api-web.nhle.com", "www.nhl.com", "statsapi.mlb.com", "www.mlb.com",
    "www.euroleaguebasketball.net", "wtafiles.wtatennis.com", "www.intrl.sport",
    "www.pcb.com.pk", "www.wst.tv", "www.unitedrugby.com", "stats.unitedrugby.com",
    "www.eurohandball.com", "www.formula1.com", "www.pgatour.com", "www.nba.com",
    "www.afl.com.au", "www.gaa.ie", "www.gbgb.org.uk", "www.pdc.tv",
    "www.tauronliga.pl", "www.plusliga.pl", "lolesports.com",
}

def source(id, publisher, url, role, read, limitation="", official=True):
    return {"id": id, "publisher": publisher, "url": url, "role": role,
            "read_at_utc": READ_AT_UTC, "observed": read, "limitation": limitation,
            "official": official}

SOURCES = [
    source("olbg-sitemap", "OLBG (discovery only)", "https://www.olbg.com/sitemap-betting-tips.xml", "taxonomy discovery", "Sport routes and numeric IDs; page lastmod 2026-10-22.", "Not an official sporting body; never used to verify a fixture.", False),
    source("olbg-baseball", "OLBG (discovery only)", "https://www.olbg.com/betting-tips/Baseball/12", "discovery and market taxonomy", "TB Rays @ MIL Brewers; Money Line 16/20 (80%); official explanatory text lists Money Line, Run Line and Game Totals.", "Tip share is not a market price or model probability.", False),
    source("olbg-basketball", "OLBG (discovery only)", "https://www.olbg.com/betting-tips/Basketball/4", "discovery and market taxonomy", "NBA, NBB and EuroLeague cards; Money Line and Pointspread labels; Friday EuroLeague cards match the official schedule.", "First visible screen plus Load More only; not a complete event census.", False),
    source("olbg-tennis", "OLBG (discovery only)", "https://www.olbg.com/betting-tips/Tennis/3", "discovery and market taxonomy", "Win Match, Set Betting, Games Won and Total Games labels; current WTA cards and additional ATP/WTA leads.", "Additional leads remain unverified unless an official row appears in this desk.", False),
    source("olbg-hockey", "OLBG (discovery only)", "https://www.olbg.com/betting-tips/Ice_Hockey/13", "discovery and market taxonomy", "NHL and European cards; Money Line, Game Totals and Puck Line labels.", "Displayed clocks are not used; several 22 October cards were already live/completed at read time.", False),
    source("nhl-schedule", "National Hockey League", "https://api-web.nhle.com/v1/schedule/2026-10-23", "official fixtures", "Chunks 0-4: all two games on 23 October, 12 on 24 October and five on 25 October; game IDs, FUT state, venue, UTC start and explicitly labelled home/away teams.", "26-29 October chunks were not transcribed; this is not a whole-week NHL census."),
    source("mlb-schedule", "Major League Baseball", "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-22&endDate=2026-10-29", "official fixtures and conditional-game status", "Five World Series games (849805, 849802, 849804, 849803, 849799), scheduled status, dates, venues, teams and ifNecessary flags. Game 5 is ifNecessary=Y; games 1-4 are N."),
    source("mlb-al", "Major League Baseball", "https://statsapi.mlb.com/api/v1/standings?leagueId=103&season=2026&standingsTypes=regularSeason&fields=records,teamRecords,team,id,name,wins,losses,runsScored,runsAllowed,leagueRecord", "official statistical input", "Tampa Bay: 98-64, 736 runs scored, 650 allowed; 55-26 home, 43-38 away, last-ten 5-5."),
    source("mlb-nl", "Major League Baseball", "https://statsapi.mlb.com/api/v1/standings?leagueId=104&season=2026&standingsTypes=regularSeason&fields=records,teamRecords,team,id,name,wins,losses,runsScored,runsAllowed,leagueRecord", "official statistical input", "Milwaukee: 103-59, 832 runs scored, 618 allowed; 55-26 home, 48-33 away, last-ten 8-2."),
    source("mlb-mil-form", "Major League Baseball", "https://statsapi.mlb.com/api/v1/schedule?sportId=1&teamId=158&startDate=2026-10-01&endDate=2026-10-22&fields=dates,date,games,gamePk,gameDate,officialDate,status,detailedState,teams,away,home,team,id,name,score,isWinner,seriesDescription,venue,name", "official recent results", "Eight final postseason games. NLCS: 2-1, 7-4, 6-2 and 6-4 wins over the Dodgers; preceding NLDS scores against San Diego."),
    source("mlb-tb-form", "Major League Baseball", "https://statsapi.mlb.com/api/v1/schedule?sportId=1&teamId=139&startDate=2026-10-01&endDate=2026-10-22&fields=dates,date,games,gamePk,gameDate,officialDate,status,detailedState,teams,away,home,team,id,name,score,isWinner,seriesDescription,venue,name", "official recent results", "Ten listed postseason games plus one postponed entry. Last three finals: 7-3 and 3-1 at Cleveland, then 7-3 over Cleveland at Tropicana Field on 19 October."),
    source("mlb-mil-roster", "Major League Baseball", "https://statsapi.mlb.com/api/v1/teams/158/roster?rosterType=active&season=2026&fields=roster,person,id,fullName,position,abbreviation", "official active roster", "Christian Yelich, Jackson Chourio, William Contreras, Brice Turang, Jacob Misiorowski and other active-roster entries.", "Roster presence does not confirm a starting role or availability for a particular game."),
    source("mlb-tb-roster", "Major League Baseball", "https://statsapi.mlb.com/api/v1/teams/139/roster?rosterType=active&season=2026&fields=roster,person,id,fullName,position,abbreviation", "official active roster", "Junior Caminero, Yandy Díaz, Jonathan Aranda, Drew Rasmussen, Cedric Mullins and other active-roster entries.", "Roster presence does not confirm a starting role or availability for a particular game."),
    source("euroleague-r7", "Euroleague Basketball", "https://www.euroleaguebasketball.net/en/euroleague/news/game-center-round-7-el2627/", "official fixtures, records, form and player context", "Updated article separates completed Thursday results from Friday fixtures. Friday: Zalgiris-ASVEL (both 2-4), Olympiacos-Fenerbahce (both 5-1), Paris-Valencia (1-5 v 5-1), with club/player context and CEST start times."),
    source("wta-ningbo", "WTA Tour", "https://wtafiles.wtatennis.com/pdf/draws/2026/2092/OP.pdf", "official order of play", "BNB Ningbo Open, Friday 23 October: five Centre Court quarter-finals, seeds, published clock order and hard/Plexipave surface.", "PDF has no timezone label; 'followed by' has no clock time. No ranking or form input was read."),
    source("irl", "International Rugby League", "https://www.intrl.sport/fixtures-results", "official fixtures", "Thirteen fixtures dated 23-25 October with competition, round, venue, published clock and direct match-details link.", "Clock timezone is not stated; no team form/rating input was read."),
    source("pcb", "Pakistan Cricket Board", "https://www.pcb.com.pk/pakistan-england-and-sri-lanka-trination-odi-series-202627/tournament/1465.html", "official tournament fixtures", "Seven-match tri-nation list; upcoming named matches 4-6 on 25, 27 and 29 October at Gaddafi Stadium, Lahore.", "Dates only; no start time or current team rating was read. TBC final excluded."),
    source("wst", "World Snooker Tour", "https://www.wst.tv/matches/", "official fixtures and recent results", "Northern Ireland Open scheduled quarter-finals 57-59 on 23 October: McGill-Wilson, Craigie-Slessor, Gilbert-Williams. Match 60 still says Winner of match 55 v Winner of match 56 and is not promoted to a named fixture.", "Displayed clock has no timezone label; match 60 participants remain blank/flagged in coverage findings."),
    source("urc-fixtures", "United Rugby Championship", "https://www.unitedrugby.com/latest/news/2026-27-fixtures-in-full/", "official fixtures", "Round 4: three fixtures on 23 October and five on 24 October, with venues and dual IRE & UK / ITA & SA publication clocks."),
    source("urc-adjustment", "United Rugby Championship", "https://www.unitedrugby.com/latest/news/adjustments-to-2026-27-bkt-united-rugby-championship-fixture-broadcast-for-rounds-2-4-6-15/", "official fixture correction", "Ospreys v Dragons moved from 19:45 to 19:00 UK on 24 October; St Helen's and S4C host broadcaster confirmed."),
    source("urc-match-centre", "United Rugby Championship", "https://stats.unitedrugby.com/match-centre/2026-27/4", "official match-centre cross-check", "Round 4 page and direct IDs 292608-292610 for Friday matches; page says all times are Local and also displays a viewer-local 14:45 for the Friday games.", "Viewer-local rendering is not converted to UTC. Later Saturday rows retain the official fixture-article link."),
    source("urc-team-news", "United Rugby Championship", "https://www.unitedrugby.com/latest/team-news/round-4-team-announcements/", "official player context", "Friday team announcements name full line-ups and replacements for Cardiff-Sharks, Connacht-Zebre and Edinburgh-Lions.", "No paired current rating model was built from team sheets alone."),
    source("ehf", "European Handball Federation", "https://www.eurohandball.com/en/", "official fixtures", "Official live-score calendar: three 23 October and eight 24 October fixtures transcribed with competition, displayed clock and direct EHF match URL.", "Only the first returned chunk was transcribed; venues and timezone are blank. This is not a complete EHF daily census."),
    source("f1", "Formula 1", "https://www.formula1.com/en/racing/2026/united-states", "official event schedule", "United States Grand Prix schedule: practice 23 October, qualifying 24 October, race 25 October at 16:00 track time; Circuit of the Americas, 56 laps.", "Event already has sessions before race day; no pre-event outright price is originated and track time is not converted to UTC."),
    source("nba", "NBA", "https://www.nba.com/games?date=2026-10-23", "official schedule attempt", "Calendar reports 12 games on 23 October and eight on 24 October.", "Match cards failed to render ('Sorry, something went wrong'), so no NBA pairing was promoted from OLBG into the verified match table."),
    source("pga", "PGA TOUR", "https://www.pgatour.com/tournaments/2026/butterfield-bermuda-championship/R2026528/overview", "official event status", "Butterfield Bermuda Championship at Port Royal, 22-25 October; page status R1 In Progress.", "Already in progress, so excluded from pre-match rows and prices."),
    source("aflw", "AFL", "https://www.afl.com.au/aflw/fixture", "official fixture attempt", "Official AFLW fixture navigation and page shell returned.", "No match cards were present in either extracted chunk; no AFLW fixture was invented from historical desks."),
    source("gaa", "GAA", "https://www.gaa.ie/fixtures-results", "official fixture check", "24 October listing contains Ireland v Scotland in the Shinty-Hurling International.", "That event is excluded as hurling/shinty; no eligible Gaelic football match was observed on the returned page. Not a worldwide zero-fixture claim."),
    source("gbgb", "Greyhound Board of Great Britain", "https://www.gbgb.org.uk/racing/", "official racing check", "Official racing search shell and 22 October race reports returned.", "No future race/runner card was exposed in the extracted page, so no selection was constructed."),
    source("pdc", "Professional Darts Corporation", "https://www.pdc.tv/news/2026/october/19/2026-machineseeker-european-championship-schedule-confirmed/", "official schedule attempt", "Official PDC URL returned a privacy/cookie interstitial.", "Article body and draw were not read; no darts fixture is marked verified."),
    source("volleyball", "TAURON Liga / PlusLiga", "https://www.plusliga.pl/games/tour/47.html", "official fixture attempt", "Request redirected to tauronliga.pl and returned match content, but its title says 2024/2025 while displayed matches are dated October 2026.", "Competition/season labelling is irregular; no volleyball row is published until the correct current competition page is isolated."),
    source("lol", "LoL Esports", "https://lolesports.com/en-US/schedule?leagues=worlds", "official schedule attempt", "Official schedule/league shell and Worlds tournament link returned.", "No pairing was present in the extracted schedule content; no eSports match was imported from memory."),
]
SOURCE_MAP = {s["id"]: s for s in SOURCES}

NHL_NAMES = {
    "ANA":"Anaheim Ducks", "BOS":"Boston Bruins", "BUF":"Buffalo Sabres", "CAR":"Carolina Hurricanes",
    "CBJ":"Columbus Blue Jackets", "CGY":"Calgary Flames", "CHI":"Chicago Blackhawks", "COL":"Colorado Avalanche",
    "DAL":"Dallas Stars", "DET":"Detroit Red Wings", "EDM":"Edmonton Oilers", "FLA":"Florida Panthers",
    "LAK":"Los Angeles Kings", "MIN":"Minnesota Wild", "MTL":"Montréal Canadiens", "NJD":"New Jersey Devils",
    "NSH":"Nashville Predators", "NYI":"New York Islanders", "NYR":"New York Rangers", "OTT":"Ottawa Senators",
    "PHI":"Philadelphia Flyers", "PIT":"Pittsburgh Penguins", "SEA":"Seattle Kraken", "SJS":"San Jose Sharks",
    "STL":"St. Louis Blues", "TBL":"Tampa Bay Lightning", "TOR":"Toronto Maple Leafs", "UTA":"Utah Mammoth",
    "VAN":"Vancouver Canucks", "VGK":"Vegas Golden Knights", "WSH":"Washington Capitals", "WPG":"Winnipeg Jets",
}

FIXTURES = []
def fx(id, sport, competition, a, b, date, source_id, link, **kw):
    row = {"id": id, "sport": sport, "competition": competition, "side_a": a, "side_b": b,
           "date": date, "source_id": source_id, "official_link": link, "kind": "match",
           "away": None, "home": None, "start_utc": None, "display_time": None,
           "timezone": None, "venue": None, "status": "scheduled", "blank_fields": [],
           "notes": []}
    row.update(kw)
    FIXTURES.append(row)
    return row

def nhl(id, away, home, date, start, venue):
    slug = f"{away.lower()}-vs-{home.lower()}"
    # NHL's gameCenterLink uses the officialDate (local schedule date) as YYYY/MM/DD.
    link = f"https://www.nhl.com/gamecenter/{slug}/{date.replace('-', '/')}/{id}"
    return fx(f"nhl-{id}", "ice-hockey", "NHL 2026-27 regular season", NHL_NAMES[away], NHL_NAMES[home],
              date, "nhl-schedule", link, away=NHL_NAMES[away], home=NHL_NAMES[home], start_utc=start,
              display_time=start[11:16] + " UTC", timezone="UTC", venue=venue, status="FUT",
              notes=["NHL game ID and FUT state observed in official schedule response."])

nhl(2026020166,"MTL","CHI","2026-10-23","2026-10-24T00:00:00Z","United Center")
nhl(2026020167,"TBL","COL","2026-10-23","2026-10-24T01:00:00Z","Ball Arena")
nhl(2026020168,"ANA","PHI","2026-10-24","2026-10-24T17:00:00Z","Xfinity Mobile Arena")
nhl(2026020169,"LAK","NJD","2026-10-24","2026-10-24T19:30:00Z","Prudential Center")
nhl(2026020170,"SJS","BOS","2026-10-24","2026-10-24T23:00:00Z","TD Garden")
nhl(2026020171,"NYR","OTT","2026-10-24","2026-10-24T23:00:00Z","Canadian Tire Centre")
nhl(2026020172,"NSH","PIT","2026-10-24","2026-10-24T23:00:00Z","PPG Paints Arena")
nhl(2026020173,"BUF","WSH","2026-10-24","2026-10-24T23:00:00Z","Capital One Arena")
nhl(2026020174,"VGK","CBJ","2026-10-24","2026-10-24T23:00:00Z","Nationwide Arena")
nhl(2026020175,"CAR","STL","2026-10-24","2026-10-24T23:00:00Z","Enterprise Center")
nhl(2026020176,"TOR","EDM","2026-10-24","2026-10-24T23:00:00Z","Rogers Place")
nhl(2026020177,"TBL","UTA","2026-10-24","2026-10-25T01:00:00Z","Delta Center")
nhl(2026020178,"DET","CGY","2026-10-24","2026-10-25T02:00:00Z","Scotiabank Saddledome")
nhl(2026020179,"MIN","SEA","2026-10-24","2026-10-25T02:00:00Z","Climate Pledge Arena")
nhl(2026020180,"FLA","CHI","2026-10-25","2026-10-25T19:00:00Z","United Center")
nhl(2026020181,"NYI","DAL","2026-10-25","2026-10-25T22:00:00Z","American Airlines Center")
nhl(2026020182,"MTL","WPG","2026-10-25","2026-10-25T23:00:00Z","Princess Auto Stadium")
nhl(2026020183,"COL","NSH","2026-10-25","2026-10-26T00:00:00Z","Bridgestone Arena")
nhl(2026020184,"MIN","VAN","2026-10-25","2026-10-26T02:00:00Z","Rogers Arena")

MLB_TEAMS = {
    "TB": {"name":"Tampa Bay Rays", "id":139, "w":98, "l":64, "rs":736, "ra":650,
           "home":"55-26", "away":"43-38", "last_ten":"5-5", "source_id":"mlb-al", "roster_source":"mlb-tb-roster"},
    "MIL": {"name":"Milwaukee Brewers", "id":158, "w":103, "l":59, "rs":832, "ra":618,
            "home":"55-26", "away":"48-33", "last_ten":"8-2", "source_id":"mlb-nl", "roster_source":"mlb-mil-roster"},
}
def mlb(game, away, home, date, start, venue, number, necessary):
    a, h = MLB_TEAMS[away], MLB_TEAMS[home]
    notes = [f"World Series Game {number}; ifNecessary={necessary} in MLB schedule."]
    blanks = [] if necessary == "N" else ["winner_pick", "all_prices"]
    return fx(f"mlb-{game}", "baseball", "2026 World Series", a["name"], h["name"], date,
              "mlb-schedule", f"https://www.mlb.com/gameday/{game}", away=a["name"], home=h["name"],
              start_utc=start, display_time=start[11:16]+" UTC", timezone="UTC", venue=venue,
              status="Scheduled", away_code=away, home_code=home, series_game=number,
              if_necessary=necessary, blank_fields=blanks, notes=notes)
mlb(849805,"TB","MIL","2026-10-23","2026-10-24T00:00:00Z","American Family Field",1,"N")
mlb(849802,"TB","MIL","2026-10-24","2026-10-25T00:00:00Z","American Family Field",2,"N")
mlb(849804,"MIL","TB","2026-10-26","2026-10-27T00:00:00Z","Tropicana Field",3,"N")
mlb(849803,"MIL","TB","2026-10-27","2026-10-28T00:00:00Z","Tropicana Field",4,"N")
mlb(849799,"MIL","TB","2026-10-28","2026-10-29T00:00:00Z","Tropicana Field",5,"Y")

EUROLEAGUE = {
    "ZAL": {"name":"Zalgiris Kaunas", "w":2, "l":4}, "ASV": {"name":"LDLC ASVEL Villeurbanne", "w":2, "l":4},
    "OLY": {"name":"Olympiacos Piraeus", "w":5, "l":1}, "FEN": {"name":"Fenerbahce Tarfin Istanbul", "w":5, "l":1},
    "PARIS": {"name":"Paris Basketball", "w":1, "l":5}, "VAL": {"name":"Valencia Basket", "w":5, "l":1},
}
EURO_CONTEXT = {
    "el-E2026-68": ["Both clubs lost twice last week; ASVEL allowed a league-high 95.3 points per game through six rounds.", "Zalgiris may have its entire backcourt healthy; ASVEL's Patty Mills is one of five double-figure scorers."],
    "el-E2026-70": ["Olympiacos have back-to-back overtime road wins and three straight wins against Fenerbahce, per the official preview.", "Olympiacos average 98.2 points; Fenerbahce allow 74.5, second in defence. Fenerbahce seek their first road win."],
    "el-E2026-69": ["Paris have lost three straight; Valencia are coming off their first loss.", "Valencia lead the league at 98.3 points per game; Paris's Nadir Hifi leads scorers at 20.2. TJ Shorts returns to face Paris."],
}
def euro(game, away, home, date, cest, slug):
    a, h = EUROLEAGUE[away], EUROLEAGUE[home]
    return fx(f"el-E2026-{game}", "basketball", "EuroLeague 2026-27 Round 7", a["name"], h["name"], date,
              "euroleague-r7", f"https://www.euroleaguebasketball.net/euroleague/game-center/2026-27/{slug}/E2026/{game}/",
              away=a["name"], home=h["name"], display_time=cest+" CEST", timezone="CEST",
              away_code=away, home_code=home, blank_fields=["start_utc", "venue"],
              notes=EURO_CONTEXT[f"el-E2026-{game}"])
euro(68,"ASV","ZAL","2026-10-23","19:00","zalgiris-kaunas-ldlc-asvel-villeurbanne")
euro(70,"FEN","OLY","2026-10-23","20:15","olympiacos-piraeus-fenerbahce-tarfin-istanbul")
euro(69,"VAL","PARIS","2026-10-23","20:45","paris-basketball-valencia-basket")

for id, a, b, t in [
    ("wta-ningbo-qf1","Erin Routliffe / Aldila Sutjiadi","Ulrikke Eikeri / Quinn Gleason","11:00 AM"),
    ("wta-ningbo-qf2","Sara Bejlek","Marie Bouzkova","Not before 1:00 PM"),
    ("wta-ningbo-qf3","Leylah Fernandez","Ekaterina Alexandrova","Followed by"),
    ("wta-ningbo-qf4","[4] Iva Jovic","[6] Diana Shnaider","Not before 4:00 PM"),
    ("wta-ningbo-qf5","[1] Elena Rybakina","[Q] Katarzyna Kawa","Not before 7:00 PM"),
]:
    fx(id,"tennis","BNB Ningbo Open quarter-finals",a,b,"2026-10-23","wta-ningbo",
       "https://wtafiles.wtatennis.com/pdf/draws/2026/2092/OP.pdf",display_time=t,
       venue=None,blank_fields=["start_utc","timezone","venue"],notes=["Hard/Plexipave; official order may be moved at the supervisor's discretion."])

IRL_ROWS = [
    (2586,"Women's Rugby League World Cup Round 2","Samoa","Wales","2026-10-23","17:50","CommBank Stadium, Sydney"),
    (2569,"Men's Rugby League World Cup Round 2","Tonga","Lebanon","2026-10-23","20:05","CommBank Stadium, Sydney"),
    (2587,"Women's Rugby League World Cup Round 2","Fiji","Papua New Guinea","2026-10-24","12:15","Santos National Football Stadium, Port Moresby"),
    (2661,"Senior International Matches (Men)","Scotland","Wales","2026-10-24","14:00","Biggar RFC"),
    (2664,"European Championship B (Men)","Netherlands","Serbia","2026-10-24","14:00","FK Zemun Stadium"),
    (2570,"Men's Rugby League World Cup Round 2","Papua New Guinea","Samoa","2026-10-24","14:25","Santos National Football Stadium, Port Moresby"),
    (2571,"Men's Rugby League World Cup Round 2","England","France","2026-10-24","14:35","HBF Park, Perth"),
    (2646,"European Championship D (Men)","Italy","Czechia","2026-10-24","15:00","Stadio Giovanni Invernizzi, Abbiategrasso"),
    (2588,"Women's Rugby League World Cup Round 2","Australia","England","2026-10-24","17:05","HBF Park, Perth"),
    (2665,"Senior International Matches (Women)","Malta","Philippines","2026-10-25","15:00","Croom Oval"),
    (2589,"Women's Rugby League World Cup Round 2","New Zealand","France","2026-10-25","15:50","One NZ Stadium, Christchurch"),
    (2572,"Men's Rugby League World Cup Round 2","New Zealand","Cook Islands","2026-10-25","18:05","One NZ Stadium, Christchurch"),
    (2573,"Men's Rugby League World Cup Round 2","Australia","Fiji","2026-10-25","19:05","Suncorp Stadium, Brisbane"),
]
for id, comp, a, b, date, t, venue in IRL_ROWS:
    fx(f"irl-{id}","rugby-league",comp,a,b,date,"irl",f"https://www.intrl.sport/match-details/{id}",
       display_time=t,venue=venue,blank_fields=["start_utc","timezone"])

for id, num, a, b, date in [("pcb-match4",4,"Pakistan","England","2026-10-25"),("pcb-match5",5,"Pakistan","Sri Lanka","2026-10-27"),("pcb-match6",6,"Sri Lanka","England","2026-10-29")]:
    fx(id,"cricket",f"Pakistan/England/Sri Lanka Tri-nation ODI — match {num}",a,b,date,"pcb",
       "https://www.pcb.com.pk/pakistan-england-and-sri-lanka-trination-odi-series-202627/tournament/1465.html",
       venue="Gaddafi Stadium, Lahore",blank_fields=["start_utc","display_time","timezone"])

for num, a, b, t, uuid in [
    (57,"Anthony McGill","Kyren Wilson","08:00","71b7dbc4-9b19-4b26-b482-add32562040a"),
    (58,"Sam Craigie","Elliot Slessor","08:00","c8486960-4aa5-40f6-812a-5dcd38dae85b"),
    (59,"David Gilbert","Mark Williams","14:00","19048b0d-aaf4-4691-ad10-15b1b707f622"),
]:
    fx(f"wst-{num}","snooker","BetVictor Northern Ireland Open quarter-finals",a,b,"2026-10-23","wst",
       f"https://www.wst.tv/match-centre/{uuid}",display_time=t,blank_fields=["start_utc","timezone","venue"])

URC_ROWS = [
    ("urc-292608","Cardiff Rugby","Hollywoodbets Sharks","2026-10-23","19:45 IRE & UK / 20:45 ITA & SA","Cardiff Arms Park, Cardiff"),
    ("urc-292609","Connacht Rugby","Zebre Parma","2026-10-23","19:45 IRE & UK / 20:45 ITA & SA","Dexcom Stadium, Galway"),
    ("urc-292610","Edinburgh Rugby","10bet Lions","2026-10-23","19:45 IRE & UK / 20:45 ITA & SA","Hive Stadium, Edinburgh"),
    ("urc-bul-uls","Vodacom Bulls","Ulster","2026-10-24","12:45 IRE & UK / 13:45 ITA & SA","Loftus Versfeld, Pretoria"),
    ("urc-sto-sca","DHL Stormers","Scarlets","2026-10-24","15:00 IRE & UK / 16:00 ITA & SA","DHL Stadium, Cape Town"),
    ("urc-ben-gla","Benetton","Glasgow Warriors","2026-10-24","15:00 IRE & UK / 16:00 ITA & SA","Stadio Monigo, Treviso"),
    ("urc-lei-mun","Leinster","Munster","2026-10-24","18:00 IRE & UK / 19:00 ITA & SA",None),
    ("urc-osp-dra","Ospreys","Dragons","2026-10-24","19:00 UK", "St Helen’s, Swansea"),
]
for id,a,b,date,t,venue in URC_ROWS:
    src = "urc-adjustment" if id == "urc-osp-dra" else "urc-fixtures"
    blanks = ["start_utc"] + (["venue"] if venue is None else [])
    notes = ["Leinster venue is TBC on the official fixture list; left blank."] if venue is None else []
    link = "https://www.unitedrugby.com/latest/news/2026-27-fixtures-in-full/"
    if id.startswith("urc-292"):
        slug = {"urc-292608":"cardiff-rugby-vs-hollywoodbets-sharks", "urc-292609":"connacht-rugby-vs-zebre-parma", "urc-292610":"edinburgh-rugby-vs-10bet-lions"}[id]
        link = f"https://stats.unitedrugby.com/match-centre/202601/united-rugby-championship/{slug}-2026-10-23/{id.split('-')[1]}"
    elif id == "urc-osp-dra":
        link = "https://www.unitedrugby.com/latest/news/adjustments-to-2026-27-bkt-united-rugby-championship-fixture-broadcast-for-rounds-2-4-6-15/"
    fx(id,"rugby-union","BKT United Rugby Championship Round 4",a,b,date,src,link,
       display_time=t,timezone="published local zones; not converted",venue=venue,blank_fields=blanks,notes=notes)

EHF_ROWS = [
    ("202711020702049","Kur","MRK Sloga Doboj","2026-10-23","15:00","EHF European Cup Men","Kur-MRKSlogaDoboj"),
    ("202711020702003","GRK Ohrid","Spor Toto SK","2026-10-23","18:30","EHF European Cup Men","GRKOhrid-SporTotoSK"),
    ("202712030103001","Estonia","Kosovo","2026-10-23","20:00","World Championship 2027 Women","Estonia-Kosovo"),
    ("202711020702022","Istanbul GSK","Rebud KPR Ostrovia Ostrów Wielkopolski","2026-10-24","13:00","EHF European Cup Men","IstanbulGSK-RebudKPROstroviaOstr%C3%B3wWielkopolski"),
    ("202711020702020","Tallinna Mistra","BK-46","2026-10-24","13:00","EHF European Cup Men","TallinnaMistra-BK46"),
    ("202711020702029","Dragunas Klaipeda","HC Robe Zubri","2026-10-24","14:30","EHF European Cup Men","DragunasKlaipeda-HCRobeZubri"),
    ("202711020702050","MRK Sloga Doboj","Kur","2026-10-24","15:00","EHF European Cup Men","MRKSlogaDoboj-Kur"),
    ("202711020702041","Ionikos A.C. N.F.","AS SGS Ramhat Hashron","2026-10-24","15:00","EHF European Cup Men","IonikosACNF-ASSGSRamhatHashron"),
    ("202711020702013","PLER-Budapest","Islington HC","2026-10-24","16:00","EHF European Cup Men","PLERBudapest-IslingtonHC"),
    ("202712030103002","Kosovo","Estonia","2026-10-24","17:00","World Championship 2027 Women","Kosovo-Estonia"),
    ("202711020702005","AHC Potaissa Turda","Derdaele Sporting Pelt","2026-10-24","17:00","EHF European Cup Men","AHCPotaissaTurda-DerdaeleSportingPelt"),
]
for id,a,b,date,t,comp,slug in EHF_ROWS:
    fx(f"ehf-{id}","handball",comp,a,b,date,"ehf",f"https://www.eurohandball.com/en/matches/{id}/{slug}/",
       display_time=t,blank_fields=["start_utc","timezone","venue"])

fx("f1-usgp-2026","motor-racing","Formula 1 United States Grand Prix","United States Grand Prix",None,
   "2026-10-25","f1","https://www.formula1.com/en/racing/2026/united-states",kind="event",
   display_time="16:00 track time",timezone="track-local (not converted)",venue="Circuit of the Americas",
   blank_fields=["start_utc","side_b","winner_pick","all_prices"],notes=["Event-only card; practice and qualifying precede the race. No driver field/rating input was used."])

COVERAGE_NOTES = {
    "tennis":"Five official WTA quarter-finals. Other current OLBG tennis leads are not included until their own ATP/WTA pages are read; no price without rankings/form inputs.",
    "basketball":"Three official Friday EuroLeague fixtures priced by winner only. NBA's official calendar counts games but failed to render pairings; no NBA match was imported from OLBG alone.",
    "golf":"Official PGA page says Bermuda R1 is In Progress, so no pre-event row or price. A historical R2026028 URL was also checked and actually identifies the BMW Championship, not Bermuda; correct Bermuda ID is R2026528.",
    "cricket":"Three future PCB fixtures verified with dates and grounds. Start times and prices are blank; TBC final excluded.",
    "snooker":"Three named WST quarter-finals verified. Match 60 remains Winner 55 v Winner 56 and is not named or priced.",
    "rugby-union":"All eight official URC Round 4 fixtures listed; Ospreys time corrected to the later official adjustment. Leinster venue blank because official says TBC.",
    "rugby-league":"All 13 IRL fixtures displayed for 23-25 October. Published clock times have no timezone, and no lines are invented without ratings.",
    "baseball":"Five official World Series rows. Games 1-4 priced; conditional Game 5 is unpriced. Identical team inputs produce identical model numbers across games 1-4; no park/pitcher adjustment is claimed.",
    "ice-hockey":"All 19 official NHL games on 23-25 October included. Prices withheld because this session did not transcribe every required current team-stat row; 26-29 October remain a stated coverage gap.",
    "motor-racing":"One official F1 event-only row, no driver selection. Race is 25 October; earlier sessions mean this is not treated as an untouched pre-event outright.",
    "darts":"PDC official article returned only a privacy interstitial. No fixture or price is marked verified.",
    "handball":"Eleven official EHF fixtures transcribed from the first calendar chunk. Later chunks, venues, timezone and prices remain open; not a complete daily census.",
    "volleyball":"Official PlusLiga URL redirected to TAURON Liga and showed a 2024/2025 title beside October 2026 match content. Rows withheld pending competition/season reconciliation.",
    "aussie-rules":"AFLW official page returned navigation but no match cards. No rows carried over from expired desks.",
    "esports":"LoL Esports official schedule shell returned without pairings in the extracted content. No eSports rows inferred.",
    "gaelic-football":"GAA official page showed only an excluded Shinty-Hurling International. This is not a claim that no Gaelic football exists elsewhere.",
    "greyhounds":"GBGB official racing page exposed a search shell and reports, not a future runner card. No greyhound selection was generated.",
}

MARKET_INVESTIGATION = {
    "baseball":[
        ("Money line / match winner","priced","Independent Poisson score grid; tie after regulation split by expected-run share."),
        ("Nine-inning 1X2","priced","Model market, not a claim about operator availability."),
        ("Run line ±1.5 and ±2.5","priced","Full-game model lines."),
        ("Match totals half-run and integer push-refund","priced","6.5-11.5 plus Asian 9, 10 and 11. Integer prices condition on no push."),
        ("Team totals","priced","3.5, 4.5 and 5.5 for each club from its own Poisson rate."),
        ("First five innings","withheld","No official inning-split input was read."),
        ("Starting-pitcher and player props","withheld","Roster presence is not a starter/performance projection; no verified prop inputs."),
        ("Correct score","withheld","A score grid exists internally, but no verified market offering/settlement rules were found; not published as a betting selection."),
        ("World Series outright","withheld","Conditional game state and series path require separate modelling; not silently derived from single-game lines."),
    ],
    "basketball":[
        ("Match winner","priced","Beta(2,2)-shrunk records and log5; no home advantage inserted."),
        ("Point spread","withheld","Official preview lacks a paired margin distribution for all three games."),
        ("Match and team totals","withheld","Official scoring/defence figures are not available for both sides of every fixture."),
        ("Quarter/half and player props","withheld","No compatible official period/player projection inputs."),
    ],
}
DEFAULT_MARKETS = [
    ("Match winner / tournament winner","withheld","No compatible official statistical input was read for both sides or the full field."),
    ("Handicap / spread / sets / frames / legs","withheld","A fixture list alone does not supply a margin distribution."),
    ("Match and team totals","withheld","No paired scoring-rate input was verified."),
    ("Period, correct-score and player props","withheld","No official period/player inputs and settlement rules were verified."),
]
for slug, _, _, _ in SPORTS:
    MARKET_INVESTIGATION.setdefault(slug, DEFAULT_MARKETS)
