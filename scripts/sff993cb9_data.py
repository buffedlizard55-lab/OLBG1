"""TFF99 desk data — session ff993cb9. Snapshot 2026-10-24T22:32Z.
Facts were read this session from the official sources listed in SOURCES.
OLBG was used for discovery only. Prices are originated fair (no-vig) estimates:
decimal = 1/p, American derived from p. Confidence is derived in the builder.
"""
SNAPSHOT = "2026-10-24T22:32:00Z"
SNAPSHOT_LABEL = "24 Oct 2026, 22:32 UTC"

SPORTS = [
    ("golf", "Golf", "https://www.olbg.com/betting-tips/Golf/5"),
    ("volleyball", "Volleyball", "https://www.olbg.com/betting-tips/Volleyball/21"),
    ("rugby-union", "Rugby Union", "https://www.olbg.com/betting-tips/Rugby_Union/9"),
    ("cricket", "Cricket", "https://www.olbg.com/betting-tips/Cricket/7"),
    ("snooker", "Snooker", "https://www.olbg.com/betting-tips/Snooker/8"),
    ("darts", "Darts", "https://www.olbg.com/betting-tips/Darts/15"),
    ("baseball", "Baseball", "https://www.olbg.com/betting-tips/Baseball/12"),
    ("gaelic-sports", "Gaelic Sports", "https://www.olbg.com/betting-tips/Gaelic_Football/25"),
    ("greyhounds", "Greyhounds", "https://www.olbg.com/betting-tips/Greyhounds/28"),
    ("tennis", "Tennis", "https://www.olbg.com/betting-tips/Tennis/3"),
    ("motor-racing", "Motor Racing", "https://www.olbg.com/betting-tips/Motor_Racing/14"),
    ("handball", "Handball", "https://www.olbg.com/betting-tips/Handball/20"),
    ("ice-hockey", "Ice Hockey", "https://www.olbg.com/betting-tips/Ice_Hockey/13"),
    ("basketball", "Basketball", "https://www.olbg.com/betting-tips/Basketball/4"),
    ("rugby-league", "Rugby League", "https://www.olbg.com/betting-tips/Rugby_League/10"),
]
SPORT_NAME = {s: n for s, n, _ in SPORTS}
OLBG_HUB = {s: u for s, _, u in SPORTS}

# (publisher, title, url, read_utc, used_for)
SOURCES = [
 ("OLBG (discovery only)", "Tennis hub — event list, Win Match market, tip counts", "https://www.olbg.com/betting-tips/Tennis/3", "2026-10-24T22:28Z", "Discovery: which matches/markets OLBG lists. Never used as a fact source."),
 ("NHL (official API)", "Schedule 25 Oct 2026", "https://api-web.nhle.com/v1/schedule/2026-10-25", "2026-10-24T22:26Z", "Ice hockey fixtures, venues, start times (game IDs 2026020180-184)."),
 ("NHL (official API)", "Schedule 26 Oct 2026", "https://api-web.nhle.com/v1/schedule/2026-10-26", "2026-10-24T22:29Z", "Ice hockey fixtures Mon 26 Oct (LAK@NYR, TOR@CGY, DET@EDM)."),
 ("NHL.com", "Standings at 24 Oct 2026", "https://www.nhl.com/standings", "2026-10-24T22:28Z", "Records, GF/GA, home/away splits, last-10, streaks quoted in hockey write-ups."),
 ("MLB Stats API (official)", "Schedule 24-31 Oct incl. World Series Games 2-5", "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-24&endDate=2026-10-31", "2026-10-24T22:26Z", "TB @ MIL Game 2 (25 Oct 00:00Z), MIL @ TB Game 3 (27 Oct 00:00Z) at Tropicana Field; series record 0-1 / 1-0; listed Game 2 pitchers Rasmussen / Henderson."),
 ("NPB (official)", "Nippon Series dates", "https://npb.jp/eng/", "2026-10-24T22:29Z", "Japan Series Games 1-7 dates 24 Oct - 1 Nov."),
 ("NBA.com", "Standings 2026-27", "https://www.nba.com/standings", "2026-10-24T22:29Z", "Early-season records and home/road splits for the 25 Oct NBA slate."),
 ("NBA.com", "Games / team schedules 25 Oct 2026", "https://www.nba.com/games", "2026-10-24T22:27Z", "Sunday slate: LAL@UTA, IND@BKN, ORL@NYK, TOR@MIN, LAC@OKC, DET@PHI, MEM@SAC."),
 ("ATP Tour", "Basel (328) singles draw", "https://www.atptour.com/en/scores/current/basel/328/draws", "2026-10-24T22:28Z", "Basel R32 pairings, 26 Oct - 1 Nov, indoor hard."),
 ("ATP Tour", "Basel top seeds with rankings", "https://www.atptour.com/en/scores/current/basel/328/top-seeds", "2026-10-24T22:31Z", "Seeds/ranks: Shelton 1 (rank 4), Fils 2 (10), Jodar 3 (11), Djokovic 4 (12), Davidovich Fokina 5 (13), Fritz 6 (14), Lehecka 8 (20), Ruud 9 (24). No seed 7 listed."),
 ("ATP Tour", "Struff shocks Fils in Brussels semi-final (24 Oct)", "https://www.atptour.com/en/news/struff-fils-brussels-2026-saturday-sf", "2026-10-24T22:31Z", "Fils lost the Brussels semi-final on 24 Oct before travelling to Basel (headline read on atptour.com)."),
 ("Volleyball World (FIVB)", "SuperLega 2026/27 standings after round 1", "https://en.volleyballworld.com/volleyball/competitions/superlega/standings/", "2026-10-24T22:29Z", "Set/point records for all 12 SuperLega clubs after one match."),
 ("Volleyball World (FIVB)", "SuperLega schedule 25 Oct 2026 (matches #7-#12)", "https://en.volleyballworld.com/volleyball/competitions/superlega/schedule/", "2026-10-24T22:28Z", "Six Sunday fixtures: Perugia-Prata, Trentino-Cisterna, Piacenza-Modena, Lube-Padova, Milano-Cuneo, Monza-Verona."),
 ("Prem Rugby (official)", "Gallagher PREM standings", "https://www.premrugby.com/competitions/gallagher-prem/standings", "2026-10-24T22:30Z", "Saracens 2-1, 11 pts, +21; Harlequins 0-3, 2 pts, -68 before the 25 Oct derby."),
 ("LNR Top 14 (official)", "Top 14 standings / J7 calendar", "https://top14.lnr.fr/classement", "2026-10-24T22:30Z", "Bordeaux-Begles 3rd, 19 pts (215-151); La Rochelle 4th, 18 pts (144-135); J7 Sunday fixture at Marcel-Deflandre."),
 ("ICC", "Fixtures and results hub", "https://www.icc-cricket.com/fixtures-results", "2026-10-24T22:27Z", "Official fixture confirmation for the 25-27 Oct internationals priced here."),
 ("ESPNcricinfo (scorecards - not a governing body)", "Series scorecards and points tables", "https://www.cricinfo.com/", "2026-10-24T22:27Z-22:31Z", "Ball-by-ball scorecard facts quoted in cricket write-ups (tri-series table, NZ v IND chases, SA v AUS Test scores, League 2 table, IND-W 1st ODI). Fixture existence is tied to the ICC hub above; see flag F-FF-07."),
 ("WST (official)", "Wilson Beats Craigie In Belfast Drama", "https://www.wst.tv/news/2026/october/24/Wilson-Beats-Craigie-In-Belfast-Drama", "2026-10-24T22:30Z", "Kyren Wilson beat Sam Craigie 6-5 to reach the Northern Ireland Open final."),
 ("WST (official)", "Northern Ireland Open match centre", "https://www.wst.tv/matches/", "2026-10-24T22:30Z", "Final scheduled 25 Oct, Waterfront Hall; second semi-final Williams v Jones on 24 Oct evening."),
 ("PDC (official)", "2026 Machineseeker European Championship schedule", "https://www.pdc.tv/news/2026/october/19/2026-machineseeker-european-championship-schedule-confirmed/", "2026-10-24T22:28Z", "Quarter-finals Sun 25 Oct afternoon session, Dortmund; semi-finals and final Sunday evening."),
 ("PDC (official)", "Littler kickstarts European Championship title bid", "https://www.pdc.tv/news/2026/october/23/Littler-kickstarts-European-Championship-title-bid-in-style/", "2026-10-24T22:28Z", "Littler beat O'Connor 6-3 with a 105.05 average; Doets beat Van Gerwen in round one."),
 ("Munster GAA (official)", "Events calendar - county finals 25 Oct", "https://munster.gaa.ie/fixtures/events-calendar/", "2026-10-24T22:28Z", "Kerry SFC final Dr Crokes v Kenmare 14:00; Limerick SHC final Na Piarsaigh v Kilmallock 15:45; Cork PSFC final St Finbarr's v Nemo 16:00."),
 ("Kerry GAA (official)", "Fixtures and results", "https://www.kerrygaa.ie/fixtures-results/", "2026-10-24T22:31Z", "Kerry final fixture, Fitzgerald Stadium, referee Sean Joy."),
 ("Galway GAA (official)", "Weekend fixture changes 25 Oct", "https://www.galwaygaa.ie/changes-weekend-football-fixture-schedule/", "2026-10-24T22:28Z", "Galway SFC final Maigh Cuilinn v Salthill-Knocknacarra moved to Sunday 16:00, Pearse Stadium."),
 ("Greyhound Racing Ireland (official)", "Upcoming race cards", "https://www.grireland.ie/racing/upcoming-race-cards/", "2026-10-24T22:28Z", "Cards listed: 25-Oct-26 Clonmel and Lifford (plus 24 Oct cards)."),
 ("GBGB (official)", "Open races / 2026 Category One schedule", "https://www.gbgb.org.uk/racing/open-races/", "2026-10-24T22:28Z", "Principal races schedule; no Sunday graded racecards with form were read this session - see flag F-FF-01."),
 ("Formula 1 (official)", "United States GP 2026 - qualifying results and schedule", "https://www.formula1.com/en/racing/2026/united-states", "2026-10-24T22:29Z", "Qualifying top 5 times; race Sun 25 Oct 16:00 local, 56 laps, Circuit of the Americas."),
 ("MotoGP (official)", "Calendar 2026", "https://www.motogp.com/en/calendar/2026", "2026-10-24T22:29Z", "Australian GP weekend at Phillip Island 23-25 Oct; Malaysian GP 30 Oct - 1 Nov."),
 ("Australian GP / motogp.com.au (event official)", "Marquez takes extraordinary pole at Phillip Island", "https://www.motogp.com.au/fan-zone/news/marquez-takes-extraordinary-pole-despite-early-crash-at-phillip-island", "2026-10-24T22:30Z", "Marc Marquez pole 1:34.203, 1.494s clear of Alex Marquez, set after an early qualifying crash."),
 ("EHF (official)", "EHF Champions League Men 2026/27 standings", "https://ehfcl.eurohandball.com/men/2026-27/standings/", "2026-10-24T22:30Z", "Group A and C tables read in full (Veszprem 5-0; Aalborg 4-1-0; PSG 3-1-1; Zagreb 2-3; Porto 1-1-3; Celje 0-5)."),
 ("EHF (official)", "TV guide / October events", "https://www.eurohandball.com/en/tv-guide/", "2026-10-24T22:28Z", "25 Oct European Cup ties and women's World Championship qualifiers listed (tracked, not priced)."),
 ("NRL.com (official - RLWC rights holder coverage)", "World Cup team lists: men's round 2", "https://www.nrl.com/news/2026/10/20/world-cup-team-lists-mens-round-2/", "2026-10-24T22:29Z", "Named line-ups for New Zealand v Cook Islands (Hughes/Nikorima halves; Cook Islands captain KL Iro)."),
 ("NRL.com (official)", "World Cup team lists: men's round 1", "https://www.nrl.com/news/2026/10/13/world-cup-team-lists-mens-round-1/", "2026-10-24T22:29Z", "Australia and Fiji line-ups and squad notes."),
 ("PGA TOUR (official)", "Butterfield Bermuda Championship leaderboard after R3", "https://www.pgatour.com/leaderboard", "2026-10-24T22:30Z", "Smotherman and Power -16 (197); Moore, Conners, Silverman -14; Port Royal, par 71."),
 ("DP World Tour (official)", "Genesis Championship leaderboard after R3", "https://www.europeantour.com/dpworld-tour/genesis-championship-2026/leaderboard", "2026-10-24T22:30Z", "Katsuragawa -13 (69-68-63), Jarvis -11, Kim/Rozner/Shin -10; Woo Jeong Hills."),
 ("LPGA (official)", "Tournaments - BMW Ladies Championship 22-25 Oct", "https://www.lpga.com/tournaments", "2026-10-24T22:28Z", "Event dates/venue read; the 54-hole leaderboard was not read from lpga.com this session - see flag F-FF-08."),
]

def P(id, sport, comp, match, start, market, selection, prob, official, label, prediction, evidence):
    return dict(id=id, sport=sport, competition=comp, match=match, start=start,
                market=market, selection=selection, prob=prob, official=official,
                official_label=label, prediction=prediction, evidence=evidence,
                olbg=OLBG_HUB[sport])

NHL_S = "https://www.nhl.com/standings"
NHL_SCH25 = "https://api-web.nhle.com/v1/schedule/2026-10-25"
NHL_SCH26 = "https://api-web.nhle.com/v1/schedule/2026-10-26"
NBA_S = "https://www.nba.com/standings"
MLB_API = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-24&endDate=2026-10-31"
ATP_DRAW = "https://www.atptour.com/en/scores/current/basel/328/draws"
ATP_SEEDS = "https://www.atptour.com/en/scores/current/basel/328/top-seeds"
VW_S = "https://en.volleyballworld.com/volleyball/competitions/superlega/standings/"

PICKS = [
 # ---------------- ICE HOCKEY ----------------
 P("IH-01","ice-hockey","NHL regular season","New York Islanders at Dallas Stars","25 Oct 2026, 22:00 UTC","Match winner (incl. OT)","Dallas Stars to win",0.60,NHL_S,"NHL.com standings",
   "Dallas Stars to win against the Islanders at American Airlines Center. Dallas arrive 6-3-1 on a four-game winning run and have conceded only 17 goals in ten games, the stingiest mark among the teams in Sunday action, while New York are 5-3-2 but just 1-2-1 on the road. That defensive gap, 26 goals for against a side leaking chances away from Long Island, points to the home team.",
   "DAL 6-3-1, GF26 GA17, W4 · NYI 5-3-2, GF29 GA23, away 1-2-1 (NHL.com 24 Oct)"),
 P("IH-02","ice-hockey","NHL regular season","New York Islanders at Dallas Stars","25 Oct 2026, 22:00 UTC","Match total goals","Under 6.5 goals",0.62,NHL_S,"NHL.com standings",
   "Under 6.5 goals in Dallas on Sunday night. The Stars have allowed 17 goals across ten outings and scored 26, an average total of 4.3 per game, and the Islanders sit at 29 scored and 23 conceded through ten for a 5.2 average. Two low-event teams, neither trading in shootouts early this season, make seven goals a high bar to clear.",
   "DAL games average 4.3 total goals · NYI games 5.2 (GF/GA, NHL.com 24 Oct)"),
 P("IH-03","ice-hockey","NHL Heritage Classic (outdoor, Winnipeg)","Montreal Canadiens at Winnipeg Jets","25 Oct 2026, 23:00 UTC","Puck line (handicap)","Montreal Canadiens +1.5 goals",0.705,NHL_S,"NHL.com standings",
   "Montreal Canadiens +1.5 goals outdoors at Princess Auto Stadium. The Canadiens are 5-3-2 and have already been taken beyond regulation four times in ten games, winning both of their shootouts, which is the profile of a team living in one-goal contests. Winnipeg, 4-3-3 with 26 goals scored in ten, rarely blow anyone away, so Montreal keeping this within a goal, or winning it outright, is the play.",
   "MTL 5-3-2, SO 2-0 · WPG 4-3-3, GF26 in 10 (NHL.com 24 Oct); neutral-site Heritage Classic (NHL schedule)"),
 P("IH-04","ice-hockey","NHL regular season","Colorado Avalanche at Nashville Predators","26 Oct 2026, 00:00 UTC","Match total goals","Over 5.5 goals",0.63,NHL_S,"NHL.com standings",
   "Over 5.5 goals at Bridgestone Arena. Colorado have produced the league's wildest early-season games, 47 scored and 34 conceded in eleven, an average above seven goals a night, and even a quieter Nashville side at 23 for and 30 against in nine should contribute against that pace. The Avalanche attack travels, with 47 goals the joint-most in the standings, so six goals is well within reach.",
   "COL 6-4-1 GF47 GA34 · NSH 3-3-3 GF23 GA30 (NHL.com 24 Oct)"),
 P("IH-05","ice-hockey","NHL regular season","Los Angeles Kings at New York Rangers","26 Oct 2026, 23:00 UTC","Match winner (incl. OT)","New York Rangers to win",0.68,NHL_S,"NHL.com standings",
   "New York Rangers to win at Madison Square Garden on Monday. The Rangers are a perfect 6-0-0 at home in a 7-4-1 start, scoring 37 and conceding 29, whereas Los Angeles limp east at 2-5-2 with a minus-11 goal difference and only 21 goals from nine games. The Kings' 2-2-2 road record flatters them against a side yet to drop a point on home ice.",
   "NYR 7-4-1, home 6-0-0 · LAK 2-5-2, GF21 GA32 (NHL.com 24 Oct)"),
 P("IH-06","ice-hockey","NHL regular season","Toronto Maple Leafs at Calgary Flames","27 Oct 2026, 00:30 UTC","Match winner (incl. OT)","Toronto Maple Leafs to win",0.66,NHL_S,"NHL.com standings",
   "Toronto Maple Leafs to win in Calgary. Toronto ride a three-game winning streak at 6-4-2 with 43 goals scored, and they meet a Flames team rooted near the foot of the West at 3-6-0, minus-19 in goal difference and conceding 38 in nine games. Calgary have already shipped four or more far too often, and the Leafs' 2-1-1 road mark says their scoring travels well enough.",
   "TOR 6-4-2, GF43, W3 · CGY 3-6-0, GF19 GA38, -19 (NHL.com 24 Oct)"),
 P("IH-07","ice-hockey","NHL regular season","Detroit Red Wings at Edmonton Oilers","27 Oct 2026, 01:30 UTC","Match total goals","Over 6.5 goals",0.57,NHL_S,"NHL.com standings",
   "Over 6.5 goals at Rogers Place, where Edmonton have turned every night into a track meet: 47 goals scored and 32 conceded in ten games for the 8-1-1 Oilers, winners of three straight. Detroit arrive 4-3-3 at 28 for and 30 against, perfectly capable of adding two or three of their own, and in this building that combination regularly lands north of the total.",
   "EDM 8-1-1 GF47 GA32, .850 pts% · DET 4-3-3 GF28 GA30 (NHL.com 24 Oct)"),

 # ---------------- BASKETBALL ----------------
 P("BK-01","basketball","NBA regular season","Los Angeles Lakers at Utah Jazz","25 Oct 2026, 21:00 UTC","Match winner","Los Angeles Lakers to win",0.58,NBA_S,"NBA.com standings",
   "Los Angeles Lakers to win in Salt Lake City, with an honest health warning: this is game three of the season for both. The Lakers opened 2-0 at home, and NBA.com's schedule page shows they closed their home stand by beating the Clippers in a game that finished 125-117 to the hosts. Utah are 1-1, won their only home game, so the road team gets the vote but nothing stronger.",
   "LAL 2-0 (home 2-0) · UTA 1-1 (home 1-0) · LAL beat LAC 125-117 (NBA.com team schedule)"),
 P("BK-02","basketball","NBA regular season","Indiana Pacers at Brooklyn Nets","25 Oct 2026, 22:00 UTC","Match winner","Indiana Pacers to win",0.60,NBA_S,"NBA.com standings",
   "Indiana Pacers to win at Barclays Center. Brooklyn have played once and lost it at home, while the Pacers split their first two and already won their only road assignment, exactly the kind of small early-season split worth siding with before any rotation patterns settle. Two games is thin evidence, nobody should pretend otherwise, but of the pair Indiana have shown more.",
   "IND 1-1, road 1-0 · BKN 0-1, home 0-1 (NBA.com 24 Oct)"),
 P("BK-03","basketball","NBA regular season","Orlando Magic at New York Knicks","25 Oct 2026, 23:00 UTC","Match winner","New York Knicks to win",0.54,NBA_S,"NBA.com standings",
   "New York Knicks to win a meeting of two 0-2 teams at Madison Square Garden, and this one is priced like the coin-flip it is. Orlando lost both of their opening games at home and now travel for the first time, while New York also start over after defeats home and away. With nothing in the form lines, home court is the only usable edge, hence the low rating.",
   "ORL 0-2 (home 0-2) · NYK 0-2 (NBA.com 24 Oct)"),
 P("BK-04","basketball","NBA regular season","Toronto Raptors at Minnesota Timberwolves","25 Oct 2026, 23:00 UTC","Match winner","Minnesota Timberwolves to win",0.57,NBA_S,"NBA.com standings",
   "Minnesota Timberwolves to win their home opener against Toronto. Both clubs are 2-0, yet the shapes differ: Minnesota banked both wins on the road, the harder trick, while the Raptors split one home and one away. Bringing an unbeaten road record back to Target Center earns Minnesota the call in a fixture where the standings page otherwise separates the teams by nothing at all.",
   "MIN 2-0, road 2-0 · TOR 2-0, home 1-0 / road 1-0 (NBA.com 24 Oct)"),
 P("BK-05","basketball","NBA regular season","LA Clippers at Oklahoma City Thunder","25 Oct 2026, 23:00 UTC","Match winner","Oklahoma City Thunder to win",0.64,NBA_S,"NBA.com standings",
   "Oklahoma City Thunder to win at Paycom Center. Oklahoma City started 2-0 with one win on each floor, the cleanest opening on Sunday's card, and the Clippers come in 1-1 having just lost the Hallway game 125-117 to the Lakers on the road. Early-season basketball rewards the team that has shown it twice, and on this week's evidence that is the Thunder.",
   "OKC 2-0 · LAC 1-1, road 0-1 (lost 117-125 at LAL) (NBA.com 24 Oct)"),
 P("BK-06","basketball","NBA regular season","Detroit Pistons at Philadelphia 76ers","25 Oct 2026, 23:30 UTC","Match winner","Philadelphia 76ers to win",0.56,NBA_S,"NBA.com standings",
   "Philadelphia 76ers to win a clash of 2-0 starts. Philadelphia's pair of wins includes a divisional victory and one success in front of their own crowd, and Detroit, for all their matching record, now walk into the tougher building for their second road test of the week. Records identical, schedules weeks young, so the home team gets a narrow, honestly labelled nod.",
   "PHI 2-0 (div 1-0) · DET 2-0 (NBA.com 24 Oct)"),

 # ---------------- BASEBALL ----------------
 P("BB-01","baseball","MLB World Series, Game 2","Tampa Bay Rays at Milwaukee Brewers","25 Oct 2026, 00:00 UTC","Match winner","Milwaukee Brewers to win (Game 2)",0.57,MLB_API,"MLB Stats API (official schedule)",
   "Milwaukee Brewers to win Game 2 and double their World Series lead. Milwaukee took Friday's opener 3-2 behind five one-run innings from Jacob Misiorowski, with Christian Yelich tripling in the first run and William Contreras adding an RBI single and throwing out two Rays runners. Tampa Bay's listed starter Drew Rasmussen faces a lineup already seeing the ball well at American Family Field.",
   "Game 1: MIL 3-2 TB (23 Oct) · Game 2 listed pitchers Rasmussen (TB) / Henderson (MIL) in MLB feed"),
 P("BB-02","baseball","MLB World Series, Game 2","Tampa Bay Rays at Milwaukee Brewers","25 Oct 2026, 00:00 UTC","Match total runs","Under 8.5 runs (Game 2)",0.58,MLB_API,"MLB Stats API (official schedule)",
   "Under 8.5 runs in Game 2. The opener produced five runs total on fifteen combined hits, and it took a scratch run in the seventh and a ninth-inning groundout to reach even that, with Trevor Megill escaping a bases-loaded jam to end it. World Series games tighten further with every leverage arm available, and nothing about Friday's tempo suggests a nine-run evening follows.",
   "Game 1 total 5 runs, 15 hits, 3:09 (23 Oct box score)"),
 P("BB-03","baseball","MLB World Series, Game 3","Milwaukee Brewers at Tampa Bay Rays","27 Oct 2026, 00:00 UTC","Match total runs","Under 8.5 runs (Game 3)",0.56,MLB_API,"MLB Stats API (official schedule)",
   "Under 8.5 runs again as the series moves indoors to Tropicana Field for Game 3 on Monday night. The only completed evidence in this matchup is a 3-2 opener where both bullpens held leads late, Tampa Bay managed two runs from seven hits, and no inning produced more than the two Milwaukee scored in the first. Until one lineup breaks out, the under keeps the vote.",
   "Series moves to Tropicana Field (MLB schedule) · Game 1 finished 3-2"),
 P("BB-04","baseball","MLB World Series, Game 3","Milwaukee Brewers at Tampa Bay Rays","27 Oct 2026, 00:00 UTC","Match winner","Tampa Bay Rays to win (Game 3)",0.53,MLB_API,"MLB Stats API (official schedule)",
   "Tampa Bay Rays to win Game 3 at home, priced as the marginal call it is. The Rays lost the opener by one run on the road, pushed the tying run to third base in the ninth, and out-hit expectations against elite velocity without cashing in. A venue switch and last at-bats are real edges in a one-run series, so the home side gets a tentative vote at a plus price.",
   "TB lost Game 1 by one run (2-3), tying run at third in the 9th"),
 P("BB-05","baseball","NPB Japan Series, Game 2","Fukuoka SoftBank Hawks at Yokohama DeNA BayStars","25 Oct 2026, 09:00 UTC","Match winner","Fukuoka SoftBank Hawks to win (Game 2)",0.60,"https://npb.jp/eng/","NPB (official)",
   "Fukuoka SoftBank Hawks to win Game 2 in Yokohama. SoftBank were the Pacific League's runaway side at 91-49-3, a .650 pace, while DeNA came through the Central League at 71-69-3 and needed the Climax Series route to get here. DeNA's pitching was superb in shutting out Hanshin three times in the final stage, yet the season-long gap of twenty wins still has to count for something.",
   "SoftBank 91-49-3 (.650) · DeNA 71-69-3 (.507); DeNA beat Hanshin 4-1 in Climax final stage"),
 P("BB-06","baseball","NPB Japan Series, Game 3","Yokohama DeNA BayStars at Fukuoka SoftBank Hawks","27 Oct 2026 (18:00 JST)","Match winner","Fukuoka SoftBank Hawks to win (Game 3)",0.64,"https://npb.jp/eng/","NPB (official)",
   "Back SoftBank again for Game 3, this time at home as the Japan Series switches to the Mizuho PayPay Dome. SoftBank finished eleven and a half games clear in their league, the profile of a team that has been winning home series all year, and DeNA's 71-win season included long stretches spent chasing .500. Add the designated-hitter comforts of the Pacific League park and the hosts rate clear favourites.",
   "SoftBank won PL by 11.5 games · Games 3-5 in Fukuoka (NPB schedule)"),

 # ---------------- TENNIS ----------------
 P("TN-01","tennis","ATP 500 Swiss Indoors Basel, R32","Stan Wawrinka vs Jiri Lehecka","26 Oct 2026 (Basel, indoor hard)","Match winner","Jiri Lehecka to win",0.68,ATP_SEEDS,"ATP Tour - Basel top seeds",
   "Jiri Lehecka to beat Stan Wawrinka in Basel. Lehecka is the eighth seed and world number 20 on the ATP's own Basel seeds page, while Wawrinka needed a wild card into his home event at the St. Jakobshalle. The Swiss crowd and a famous backhand keep this from being any stronger a call, but against a seeded top-20 opponent indoors, sentiment only stretches so far.",
   "Lehecka seed 8, rank 20 · Wawrinka wild card (ATP Basel draw/seeds)"),
 P("TN-02","tennis","ATP 500 Swiss Indoors Basel, R32","Novak Djokovic vs Ugo Humbert","26 Oct 2026 (Basel, indoor hard)","Match winner","Novak Djokovic to win",0.66,ATP_SEEDS,"ATP Tour - Basel top seeds",
   "Novak Djokovic to beat Ugo Humbert in his Basel opener. Djokovic is seeded fourth from a world ranking of 12 on the ATP seeds list, and even in the late stretch of his career a first-round draw against an unseeded opponent indoors is a match he is expected to manage. Humbert's left-handed serve can hurry anyone on this surface, which caps confidence at this level rather than higher.",
   "Djokovic seed 4, rank 12 (wild card entry) · Humbert unseeded (ATP Basel)"),
 P("TN-03","tennis","ATP 500 Swiss Indoors Basel, R32","Hubert Hurkacz vs Arthur Fils","26 Oct 2026 (Basel, indoor hard)","Match total games","Over 22.5 games",0.58,ATP_SEEDS,"ATP Tour - Basel top seeds",
   "Over 22.5 games when Arthur Fils meets Hubert Hurkacz. Fils is the second seed and world number 10, but he spent Saturday losing a Brussels semi-final to Jan-Lennard Struff, the ATP reported, and now turns around quickly against one of the biggest servers in the draw. Hurkacz holding serve deep into sets while Fils works off the travel is a recipe for tiebreaks and a long evening.",
   "Fils seed 2, rank 10 · Fils lost Brussels SF to Struff on 24 Oct (ATP news headline)"),
 P("TN-04","tennis","ATP 500 Swiss Indoors Basel, R32","Taylor Fritz vs Stefanos Tsitsipas","26 Oct 2026 (Basel, indoor hard)","Match winner","Taylor Fritz to win",0.57,ATP_SEEDS,"ATP Tour - Basel top seeds",
   "Taylor Fritz to edge Stefanos Tsitsipas in the standout first-round tie in Basel. Fritz holds the seeding edge, sixth from a ranking of 14 on the official ATP list, and his flatter ball-striking is built for indoor hard courts where the bounce stays true. Tsitsipas unseeded in this field tells its own story about their respective seasons, though his ceiling keeps this at medium confidence only.",
   "Fritz seed 6, rank 14 · Tsitsipas unseeded (ATP Basel)"),
 P("TN-05","tennis","ATP 500 Swiss Indoors Basel, R32","Dominic Stricker vs Casper Ruud","26 Oct 2026 (Basel, indoor hard)","Match winner","Casper Ruud to win",0.62,ATP_SEEDS,"ATP Tour - Basel top seeds",
   "Casper Ruud to beat home wild card Dominic Stricker. Ruud is seeded ninth at world number 24 and brings the steadier baseline game to a matchup the Basel crowd will try to turn into something else entirely. Stricker's left-handed power plays well indoors and justifies keeping this short of a strong rating, but over three sets the seeded player's return depth usually wins these nights.",
   "Ruud seed 9, rank 24 · Stricker wild card (ATP Basel draw)"),
 P("TN-06","tennis","ATP 500 Swiss Indoors Basel, R32","Alejandro Davidovich Fokina vs Zizou Bergs","26 Oct 2026 (Basel, indoor hard)","Match winner","Alejandro Davidovich Fokina to win",0.60,ATP_SEEDS,"ATP Tour - Basel top seeds",
   "Alejandro Davidovich Fokina to beat Zizou Bergs in round one. The Spaniard is the fifth seed from a career-best neighbourhood of world number 13 on the ATP seeds page, a ranking built on return games that travel to indoor courts perfectly well. Bergs hits a heavy ball and can rush opponents, yet the gap between a top-five seed and the unseeded pack is there for a reason.",
   "Davidovich Fokina seed 5, rank 13 · Bergs unseeded (ATP Basel)"),
 P("TN-07","tennis","ATP 500 Swiss Indoors Basel, R32","Alejandro Tabilo vs Rafael Jodar","26 Oct 2026 (Basel, indoor hard)","Set handicap","Rafael Jodar to win 2-0 (straight sets)",0.52,ATP_SEEDS,"ATP Tour - Basel top seeds",
   "Rafael Jodar to win in straight sets against Alejandro Tabilo, a lower-rated dart at a worthwhile price. Jodar is the third seed and world number 11, a startling rise that the ATP's own Basel page confirms, and seeded players of that standing are supposed to close first-round doors quickly. Tabilo's left-handed angles can steal a set from anyone, which is exactly why this stays in the low band.",
   "Jodar seed 3, rank 11 · Tabilo unseeded (ATP Basel)"),

 # ---------------- VOLLEYBALL ----------------
 P("VB-01","volleyball","Italian SuperLega 2026/27, Round 2","Itas Trentino vs Cisterna Volley","25 Oct 2026, 17:00 local (Trento)","Match winner","Itas Trentino to win",0.58,VW_S,"Volleyball World - SuperLega standings",
   "Itas Trentino to win at home in round two's meeting of perfect starts. Both clubs opened with 3-0 sweeps, Cisterna actually posting the better point ratio at 79-56 against Trentino's 75-61, so this is no coronation. The PalaTrento crowd and Trentino's status as the established power shade it, with the honest caveat that one match each is all the form anyone has.",
   "TRE 1-0 (3-0, 75-61) · CIS 1-0 (3-0, 79-56), ranked 3rd/1st (Volleyball World)"),
 P("VB-02","volleyball","Italian SuperLega 2026/27, Round 2","Sir Susa Scai Perugia vs Tinet Prata di Pordenone","25 Oct 2026, 18:00 local (Perugia)","Match winner","Sir Susa Scai Perugia to win",0.66,VW_S,"Volleyball World - SuperLega standings",
   "Sir Susa Scai Perugia to beat Tinet Prata di Pordenone at the PalaEvangelisti. Perugia needed five sets on opening day, beating Cuneo 3-2 across a 114-95 point spread, while Prata also won, 3-1, so the visitors are no pushover. Still, Perugia at home against a club playing only its second-ever match at this level this season is the side the percentages have to follow.",
   "Perugia 1-0 (3-2, 114-95) · Prata 1-0 (3-1, 94-90) (Volleyball World)"),
 P("VB-03","volleyball","Italian SuperLega 2026/27, Round 2","Gas Sales Bluenergy Piacenza vs Valsa Group Modena","25 Oct 2026, 18:00 local (Piacenza)","Match winner","Gas Sales Bluenergy Piacenza to win",0.665,VW_S,"Volleyball World - SuperLega standings",
   "Gas Sales Bluenergy Piacenza to beat Valsa Group Modena at the PalaBanca. Piacenza opened with a clean 3-0 sweep and a 75-56 point count, whereas Modena were on the wrong end of the same scoreline, managing only 61 points in three sets against Trentino. One team arrives having dominated its first night, the other having been dominated, and home court widens that gap.",
   "PIA 1-0 (3-0, 75-56) · MOD 0-1 (0-3, 61-75) (Volleyball World)"),
 P("VB-04","volleyball","Italian SuperLega 2026/27, Round 2","Cucine Lube Civitanova vs Pallavolo Padova","25 Oct 2026, 18:00 local (Civitanova)","Set handicap","Cucine Lube Civitanova -1.5 sets",0.703,VW_S,"Volleyball World - SuperLega standings",
   "Cucine Lube Civitanova -1.5 sets against Pallavolo Padova, meaning Lube to win by at least two clear sets. Lube swept Verona 3-0 with a 78-65 point margin on opening night, while Padova were swept themselves and scored only 56 points, the joint-fewest of the first round. Every measured line from round one points the same way, and the Eurosuole Forum rarely forgives slow starts.",
   "CVA 1-0 (3-0, 78-65) · PAD 0-1 (0-3, 56-75), point ratio 0.746 (Volleyball World)"),
 P("VB-05","volleyball","Italian SuperLega 2026/27, Round 2","Allianz Milano vs Acqua Sant'Anna Cuneo","25 Oct 2026, 19:00 local (Milano)","Total sets","Over 3.5 sets",0.62,VW_S,"Volleyball World - SuperLega standings",
   "Over 3.5 sets at the Allianz Cloud, so at least four sets between Milano and Cuneo. Milano were swept on day one and posted the league's worst point ratio at 0.708, but Cuneo are the interesting half of this bet: they dragged mighty Perugia through five sets, scoring 95 points in defeat. A visitor that stubborn against a wobbling host rarely produces a straight-sets finish either way.",
   "Cuneo lost 2-3 to Perugia (95-114) · Milano 0-3 (56-79) (Volleyball World)"),
 P("VB-06","volleyball","Italian SuperLega 2026/27, Round 2","Vero Volley Monza vs Rana Verona","25 Oct 2026, 18:00 local (Monza)","Match winner","Vero Volley Monza to win",0.59,VW_S,"Volleyball World - SuperLega standings",
   "Vero Volley Monza to register their first win of the season against Rana Verona. Monza at least took a set and 90 points from their opening loss, finishing within four points overall, while Verona were swept by Lube and managed 65 points across three sets. Neither side has a win yet, but Monza's first-night numbers are closer to respectability, and they have the home floor.",
   "MZA 0-1 (1-3, 90-94) · VER 0-1 (0-3, 65-78) (Volleyball World)"),
 P("VB-07","volleyball","Italian SuperLega 2026/27, Round 2","Sir Susa Scai Perugia vs Tinet Prata di Pordenone","25 Oct 2026, 18:00 local (Perugia)","Set handicap (outsider)","Tinet Prata di Pordenone +2.5 sets",0.60,VW_S,"Volleyball World - SuperLega standings",
   "Tinet Prata di Pordenone +2.5 sets in Perugia, which only asks the newcomers to win a single set. Prata won their opener 3-1 and scored 94 points doing it, and Perugia have already shown they can be dragged long, needing a fifth set and 114 points to shake off Cuneo. Backing the underdog to nick one set is a different, softer question than backing them to win.",
   "Prata won opener 3-1 (94-90) · Perugia needed 5 sets in round 1 (Volleyball World)"),
]
