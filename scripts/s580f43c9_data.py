"""Evidence base for the 580f43c9 desk — 24/25 October 2026.

Every fact below was read from the official source recorded in SOURCES during this
session (2026-10-24, 17:40Z-18:25Z). Nothing here is remembered or inferred: if a
field was not readable it is None and the reason is carried in the match record.

Discovery (which fixtures exist at all) came from the OLBG betting-tips hubs; OLBG
is never used as fixture or statistical evidence.
"""

OBSERVED = "2026-10-24T18:20:00Z"

SOURCES = [
    dict(id="nba-games", publisher="NBA", official=True,
         url="https://www.nba.com/games",
         observed="2026-10-24T17:58Z",
         scope="All eight NBA games on 24 Oct 2026 (five carried here): team records, tip times in US Eastern, "
               "per-game season leaders"),
    dict(id="nba-injury", publisher="NBA", official=True,
         url="https://ak-static.cms.nba.com/referee/injury/Injury-Report_2026-10-24_01_00PM.pdf",
         observed="2026-10-24T18:40Z",
         scope="Official NBA injury report for 24 Oct 2026, 1:00 PM ET filing: per-game statuses "
               "(Out / Questionable / Probable / not yet submitted) for all eight games on the card"),
    dict(id="nhl-schedule", publisher="NHL", official=True,
         url="https://api-web.nhle.com/v1/schedule/2026-10-24",
         observed="2026-10-24T18:02Z",
         scope="12 games on 24 Oct 2026: game IDs, venues, UTC starts, game states"),
    dict(id="nhl-standings", publisher="NHL", official=True,
         url="https://api-web.nhle.com/v1/standings/2026-10-24",
         observed="2026-10-24T18:05Z",
         scope="2026-27 club records, points, L10, home/road splits, goals for/against; "
               "standings stamped 2026-10-24T17:42:15Z"),
    dict(id="mlb-schedule", publisher="MLB", official=True,
         url="https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-10-24"
             "&hydrate=team,linescore,probablePitcher",
         observed="2026-10-24T18:06Z",
         scope="World Series Game 2, Tampa Bay Rays at Milwaukee Brewers, 2026-10-25T00:00:00Z, "
               "American Family Field, probable pitchers Rasmussen/Henderson, ifNecessary=N"),
    dict(id="mlb-standings-al", publisher="MLB", official=True,
         url="https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026"
             "&standingsTypes=regularSeason",
         observed="2026-10-24T18:10Z",
         scope="2026 regular-season records; Tampa Bay Rays 98-64 (.605), home 55-26, away 43-38, "
               "L10 5-5, streak L1"),
    dict(id="mlb-standings-nl", publisher="MLB", official=True,
         url="https://statsapi.mlb.com/api/v1/standings?leagueId=104&season=2026"
             "&standingsTypes=regularSeason",
         observed="2026-10-24T18:12Z",
         scope="2026 regular-season records; Milwaukee Brewers 103-59 (.636), home 55-26, away 48-33, "
               "L10 8-2, streak W5"),
    dict(id="cork-gaa-fixtures", publisher="Cork GAA (county board, official)", official=True,
         url="https://gaacork.ie/",
         observed="2026-10-24T18:14Z",
         scope="Cork club fixtures: Sunday 25 Oct McCarthy Insurance Group Premier SFC final "
               "Nemo Rangers v St Finbarrs 16:00 SuperValu Pairc Ui Chaoimh (ref David Murnane); "
               "Premier JFC final Cobh v Canovee 14:00; Sunday 1 Nov Senior A FC final Eire Og v Kanturk"),
    dict(id="cork-gaa-psfc", publisher="Cork GAA (county board, official)", official=True,
         url="https://gaacork.ie/league/215999/",
         observed="2026-10-24T18:15Z",
         scope="Premier SFC group matrix and tables (Nemo Rangers 3 games 2-1, 57-43; St Finbarrs 3 games "
               "1-2, 63-55) and semi-finals of 10 Oct: St Finbarrs 2-12 v Clonakilty 0-16; "
               "Carrigaline 0-16 v Nemo Rangers 1-15"),
    dict(id="atp-scores", publisher="ATP Tour", official=True,
         url="https://www.atptour.com/en/scores/current",
         observed="2026-10-24T18:08Z",
         scope="Vienna semi-finals (event 9410): Medvedev (1) beat Bublik (3) 6-3 ret.; "
               "Basilashvili beat Tsitsipas (7) 6-4 6-7(5) 6-3. Basel semi-finals (event 7485) also listed"),
    dict(id="olbg-basketball", publisher="OLBG (discovery only)", official=False,
         url="https://www.olbg.com/betting-tips/Basketball/4",
         observed="2026-10-24T17:46Z", scope="Which NBA/HBL/general basketball events OLBG lists"),
    dict(id="olbg-ice-hockey", publisher="OLBG (discovery only)", official=False,
         url="https://www.olbg.com/betting-tips/Ice_Hockey/13",
         observed="2026-10-24T17:48Z", scope="Which NHL/Swiss NLA events OLBG lists"),
    dict(id="olbg-baseball", publisher="OLBG (discovery only)", official=False,
         url="https://www.olbg.com/betting-tips/Baseball/12",
         observed="2026-10-24T17:49Z", scope="MLB game list (one game: Rays @ Brewers)"),
    dict(id="olbg-gaelic", publisher="OLBG (discovery only)", official=False,
         url="https://www.olbg.com/betting-tips/Gaelic_Football/25",
         observed="2026-10-24T17:52Z", scope="Gaelic football club fixtures listed"),
    dict(id="olbg-tennis", publisher="OLBG (discovery only)", official=False,
         url="https://www.olbg.com/betting-tips/Tennis/3",
         observed="2026-10-24T17:54Z", scope="Tennis matches listed, including the Vienna final pairing"),
    dict(id="olbg-golf", publisher="OLBG (discovery only)", official=False,
         url="https://www.olbg.com/betting-tips/Golf/5",
         observed="2026-10-24T17:50Z", scope='Golf hub returned "No tips found" at read time'),
    dict(id="olbg-snooker", publisher="OLBG (discovery only)", official=False,
         url="https://www.olbg.com/betting-tips/Snooker/8",
         observed="2026-10-24T17:51Z", scope="One snooker listing, already started"),
    dict(id="olbg-darts", publisher="OLBG (discovery only)", official=False,
         url="https://www.olbg.com/betting-tips/Darts/15",
         observed="2026-10-24T17:51Z", scope="European Championship match markets listed"),
    dict(id="olbg-rugby-union", publisher="OLBG (discovery only)", official=False,
         url="https://www.olbg.com/betting-tips/Rugby_Union/9",
         observed="2026-10-24T17:53Z", scope="URC / Top 14 / Premiership fixtures listed"),
    dict(id="olbg-rugby-league", publisher="OLBG (discovery only)", official=False,
         url="https://www.olbg.com/betting-tips/Rugby_League/10",
         observed="2026-10-24T17:53Z", scope="Only 2027 outright markets; no 2026 match market"),
    dict(id="olbg-cricket", publisher="OLBG (discovery only)", official=False,
         url="https://www.olbg.com/betting-tips/Cricket/7",
         observed="2026-10-24T17:55Z", scope="International and domestic T20/ODI fixtures listed"),
    dict(id="olbg-greyhounds", publisher="OLBG (discovery only)", official=False,
         url="https://www.olbg.com/betting-tips/Greyhounds/28",
         observed="2026-10-24T17:56Z", scope="Graded races at Doncaster/Monmore/Dunstall Park etc."),
    dict(id="olbg-volleyball", publisher="OLBG (discovery only)", official=False,
         url="https://www.olbg.com/betting-tips/Volleyball/21",
         observed="2026-10-24T17:56Z", scope="SuperLega / PlusLiga / Brazil / German fixtures listed"),
    dict(id="olbg-handball", publisher="OLBG (discovery only)", official=False,
         url="https://www.olbg.com/betting-tips/Handball/20",
         observed="2026-10-24T17:57Z", scope="HBL / LNH / EHF fixtures listed"),
    dict(id="olbg-motor-racing", publisher="OLBG (discovery only)", official=False,
         url="https://www.olbg.com/betting-tips/Motor_Racing/14",
         observed="2026-10-24T17:57Z", scope="USA Grand Prix markets listed; no other race"),
    dict(id="f1-us-gp", publisher="Formula 1", official=True,
         url="https://www.formula1.com/en/racing/2026/united-states",
         observed="2026-10-24T18:18Z",
         scope="United States Grand Prix weekend at Austin; third practice in progress at read time, "
               "no qualifying classification available"),
    dict(id="urc-match-centre", publisher="United Rugby Championship", official=True,
         url="https://stats.unitedrugby.com/match-centre/2026-27/4",
         observed="2026-10-24T18:20Z",
         scope="URC Round 4 fixtures and results (Bulls 34-26 Ulster, Stormers 52-40 Scarlets, "
               "Benetton 20-24 Glasgow); remaining Round 4 fixtures were not rendered in the readable block"),
]

# ---------------------------------------------------------------------------
# Matches.  a = away/first-named side, b = home/second-named side.
# `facts` holds only numbers read from the source in `source`.
# ---------------------------------------------------------------------------

MATCHES = [
    dict(id="nba-mia-cha", sport="basketball", comp="NBA", round="Regular season",
         a="Miami Heat", b="Charlotte Hornets", start_utc="2026-10-24T22:00:00Z",
         start_label="24 Oct · 22:00 UTC (6:00 PM ET on the NBA games page)",
         venue=None, source="nba-games",
         facts=dict(a_record="0-2", b_record="1-1"),
         injuries=dict(a="Pelle Larsson probable (left finger sprain)",
                       b="Christian Anderson probable (left ankle sprain); Kylan Boswell out (right knee "
                         "surgery); Kon Knueppel out (left hamstring strain); Coby White out (left calf "
                         "strain); Grant Williams out (right hamstring strain)"),
         injury_note="NBA official injury report, 24 Oct 2026 1:00 PM ET filing."),
    dict(id="nba-bkn-cle", sport="basketball", comp="NBA", round="Regular season",
         a="Brooklyn Nets", b="Cleveland Cavaliers", start_utc="2026-10-24T23:30:00Z",
         start_label="24 Oct · 23:30 UTC (7:30 PM ET)",
         venue=None, source="nba-games",
         facts=dict(a_record="0-1", b_record="0-1"),
         injuries=dict(a="Tyler Bilodeau out (right shoulder sprain)",
                       b="Khalifa Diop out (left knee injury management); Nae'Qwan Tomlin out (low back "
                         "stress reaction); Ernest Udeh Jr out (G League two-way)"),
         injury_note="NBA official injury report, 24 Oct 2026 1:00 PM ET filing."),
    dict(id="nba-mil-phi", sport="basketball", comp="NBA", round="Regular season",
         a="Milwaukee Bucks", b="Philadelphia 76ers", start_utc="2026-10-24T23:30:00Z",
         start_label="24 Oct · 23:30 UTC (7:30 PM ET)",
         venue=None, source="nba-games",
         facts=dict(a_record="0-2", b_record="2-0"),
         injuries=dict(a="Team had not yet submitted a report at the 1:00 PM ET filing",
                       b="Dominick Barlow out (low back stress reaction); Tacko Fall out (left quadriceps "
                         "strain); Ariel Hukporti out (right Achilles tendon rupture); LeBron James out "
                         "(low back/sciatica); Dean Wade questionable (left ankle sprain)"),
         injury_note="NBA official injury report, 24 Oct 2026 1:00 PM ET filing; Milwaukee's sheet was "
                     "still marked not yet submitted, so their availability is unknown rather than clear."),
    dict(id="nba-sas-dal", sport="basketball", comp="NBA", round="Regular season",
         a="San Antonio Spurs", b="Dallas Mavericks", start_utc="2026-10-25T00:00:00Z",
         start_label="25 Oct · 00:00 UTC (8:00 PM ET on 24 Oct)",
         venue=None, source="nba-games",
         facts=dict(a_record="0-2", b_record="1-1"),
         injuries=None,
         injury_note="NBA official injury report, 24 Oct 2026 1:00 PM ET filing: both San Antonio and "
                     "Dallas were listed as not yet submitted, so the field stays blank rather than clear."),
    dict(id="nba-hou-atl", sport="basketball", comp="NBA", round="Regular season",
         a="Houston Rockets", b="Atlanta Hawks", start_utc="2026-10-25T00:30:00Z",
         start_label="25 Oct · 00:30 UTC (8:30 PM ET on 24 Oct)",
         venue=None, source="nba-games",
         facts=dict(a_record="2-0", b_record="2-0"),
         injuries=dict(a="Steven Adams out (left ankle injury management); Fred VanVleet out (right knee "
                         "injury management); Reed Sheppard questionable (left knee contusion/bone bruise)",
                       b="Mouhamed Gueye out (left foot fracture); Henri Veesaar out (right ACL tear); "
                         "RayJ Dennis, Keshon Gilbert and Jalen Wilson questionable (G League two-way)"),
         injury_note="NBA official injury report, 24 Oct 2026 1:00 PM ET filing."),

    dict(id="nhl-sjs-bos", sport="ice-hockey", comp="NHL", round="Regular season",
         a="San Jose Sharks", b="Boston Bruins", start_utc="2026-10-24T23:00:00Z",
         start_label="24 Oct · 23:00 UTC", venue="TD Garden, Boston", source="nhl-schedule",
         facts=dict(a_points=13, a_gp=11, a_gf=33, a_ga=37, a_l10="5-4-1", a_road="4-2-1",
                    a_reg_wins=1, a_streak="W2",
                    b_points=17, b_gp=11, b_gf=42, b_ga=22, b_l10="7-2-1", b_home="4-1-0",
                    b_reg_wins=7, b_streak="W1"),
         injuries=None, injury_note="No official NHL injury report read; blank."),
    dict(id="nhl-nyr-ott", sport="ice-hockey", comp="NHL", round="Regular season",
         a="New York Rangers", b="Ottawa Senators", start_utc="2026-10-24T23:00:00Z",
         start_label="24 Oct · 23:00 UTC", venue="Canadian Tire Centre, Ottawa", source="nhl-schedule",
         facts=dict(a_points=15, a_gp=12, a_gf=37, a_ga=29, a_l10="6-3-1", a_road="1-4-1",
                    a_road_gf=8, a_road_ga=19, a_streak="L1",
                    b_points=14, b_gp=11, b_gf=31, b_ga=30, b_l10="6-4-0", b_home="4-2-0",
                    b_streak="L1"),
         injuries=None, injury_note="No official NHL injury report read; blank."),
    dict(id="nhl-tor-edm", sport="ice-hockey", comp="NHL", round="Regular season",
         a="Toronto Maple Leafs", b="Edmonton Oilers", start_utc="2026-10-24T23:00:00Z",
         start_label="24 Oct · 23:00 UTC", venue="Rogers Place, Edmonton", source="nhl-schedule",
         facts=dict(a_points=14, a_gp=12, a_gf=43, a_ga=39, a_l10="5-3-2", a_streak="W3",
                    b_points=17, b_gp=10, b_gf=47, b_ga=32, b_l10="8-1-1", b_home="3-1-1",
                    b_streak="W3"),
         injuries=None, injury_note="No official NHL injury report read; blank."),
    dict(id="nhl-tb-uta", sport="ice-hockey", comp="NHL", round="Regular season",
         a="Tampa Bay Lightning", b="Utah Mammoth", start_utc="2026-10-25T01:00:00Z",
         start_label="25 Oct · 01:00 UTC", venue="Delta Center, Salt Lake City", source="nhl-schedule",
         facts=dict(a_points=14, a_gp=10, a_gf=34, a_ga=29, a_road="2-3-0", a_road_gf=16,
                    a_road_ga=20, a_l10="7-3-0", a_streak="L1",
                    b_points=14, b_gp=11, b_gf=41, b_ga=36, b_home="3-1-0", b_l10="6-4-0",
                    b_streak="L1"),
         injuries=None, injury_note="No official NHL injury report read; blank."),
    dict(id="nhl-min-sea", sport="ice-hockey", comp="NHL", round="Regular season",
         a="Minnesota Wild", b="Seattle Kraken", start_utc=None,
         start_label="Start time not read from the official schedule block (flagged F-05)",
         venue="Climate Pledge Arena, Seattle", source="nhl-schedule",
         facts=dict(a_points=14, a_gp=11, a_gf=32, a_ga=27, a_road="2-3-2", a_road_gf=17,
                    a_road_ga=19, a_l10="5-3-2", a_streak="L1",
                    b_points=15, b_gp=11, b_gf=38, b_ga=36, b_home="3-2-0", b_l10="6-3-1",
                    b_streak="W2"),
         injuries=None, injury_note="No official NHL injury report read; blank."),

    dict(id="mlb-tb-mil", sport="baseball", comp="MLB", round="World Series, Game 2",
         a="Tampa Bay Rays", b="Milwaukee Brewers", start_utc="2026-10-25T00:00:00Z",
         start_label="25 Oct · 00:00 UTC", venue="American Family Field, Milwaukee",
         source="mlb-schedule",
         facts=dict(a_record="98-64", a_pct=".605", a_home="55-26", a_away="43-38", a_l10="5-5",
                    a_streak="L1", a_sp="Drew Rasmussen",
                    b_record="103-59", b_pct=".636", b_home="55-26", b_away="48-33", b_l10="8-2",
                    b_streak="W5", b_sp="Logan Henderson",
                    series="Milwaukee lead 1-0", if_necessary="N", game_pk=849802),
         injuries=None,
         injury_note="No official MLB injury report was read; field left blank. Probable pitchers are "
                     "the ones published on the official schedule."),

    dict(id="gaa-nemo-finbarrs", sport="gaelic-football", comp="Cork Premier SFC", round="Final",
         a="Nemo Rangers", b="St Finbarrs", start_utc=None,
         start_label="Sunday 25 October, 16:00 local (Irish time); UTC conversion not published",
         venue="SuperValu Pairc Ui Chaoimh, Cork", source="cork-gaa-fixtures",
         facts=dict(a_group="3 games: 2 wins, 1 loss; 57 points for, 43 against",
                    b_group="3 games: 1 win, 2 losses; 63 points for, 55 against",
                    a_sf="beat Carrigaline 1-15 to 0-16 (10 Oct, semi-final)",
                    b_sf="beat Clonakilty 2-12 to 0-16 (10 Oct, semi-final)",
                    referee="David Murnane"),
         injuries=None, injury_note="No official club injury bulletin is published; field left blank."),

    dict(id="atp-vienna-final", sport="tennis", comp="ATP Vienna (event 9410)", round="Final",
         a="Nikoloz Basilashvili", b="Daniil Medvedev", start_utc=None,
         start_label="Sunday 25 October; time not published on the official scores page (flagged F-06)",
         venue="Wiener Stadthalle, Vienna", source="atp-scores",
         facts=dict(b_seed="1", a_seed="unseeded",
                    a_sf="beat Stefanos Tsitsipas (7) 6-4 6-7(5) 6-3",
                    b_sf="beat Alexander Bublik (3) 6-3 ret.",
                    ranking_note="No ATP ranking numbers were read this session"),
         injuries=None, injury_note="No official ATP withdrawal/injury notice read; field left blank."),
]

# ---------------------------------------------------------------------------
# Selections.  side: "a" or "b".  Probability is produced by s580f43c9_model.py
# from the facts above; `prose` is the human write-up (>= 30 words, unique).
# ---------------------------------------------------------------------------

PICKS = [
    dict(match="nba-mia-cha", side="b", market="Match winner (money line)",
         prose="Charlotte host Miami having split their opening two games while the Heat arrive 0-2. The "
               "Hornets carry a real availability problem though: Boswell, Knueppel, White and Williams are "
               "all out, with only Anderson probable on that filing, while Miami are "
               "close to whole. Record and home floor still make Charlotte the selection, but the missing "
               "rotation is why this is graded low rather than medium."),
    dict(match="nba-bkn-cle", side="b", market="Match winner (money line)",
         prose="Brooklyn and Cleveland both opened 0-1, so the bare records say coin flip and only home "
               "court separates them in our numbers. Cleveland's absences are bench-level (Diop, Tomlin, "
               "Udeh) against Brooklyn losing Bilodeau, so availability does not shift the argument either "
               "way. One game apiece means the Cavaliers are a low-conviction home selection, not a strong "
               "one; the price of -135 reflects exactly that."),
    dict(match="nba-mil-phi", side="b", market="Match winner (money line)",
         prose="Philadelphia are 2-0 and host a Milwaukee team that has lost both openers, and the official "
               "1:00 PM ET report lists LeBron James out with low back/sciatica plus Barlow, Fall and "
               "Hukporti unavailable, with Wade questionable. Milwaukee had not submitted a sheet at that "
               "filing, so their availability is unknown. That combination makes the 76ers the strongest "
               "basketball pick here at about 79%, capped at medium because -375 is shorter than the -250 "
               "floor."),
    dict(match="nba-sas-dal", side="b", market="Match winner (money line)",
         prose="San Antonio are 0-2 and visit a Dallas side that split its first two games, and the standard "
               "home adjustment lifts the Mavericks to roughly 69% in our pricing. The availability picture "
               "cannot sharpen that: both clubs were still marked not yet submitted at the afternoon filing, "
               "yet submitted, so no injury edge is claimed in either direction. Thin samples and a blank "
               "training room keep this at medium."),
    dict(match="nba-hou-atl", side="b", market="Match winner (money line)",
         prose="Houston and Atlanta both arrive 2-0, so this is unbeaten record against unbeaten record and "
               "home court is the only separator our numbers find. Availability tilts it: the official "
               "report rules out Adams and VanVleet for Houston with Sheppard questionable, while Atlanta "
               "lose only Gueye and Veesaar plus two-way questionables. That is worth a couple of points, "
               "making the Hawks a thin lean at -135 rather than a strong side."),

    dict(match="nhl-sjs-bos", side="b", market="Match winner (money line)",
         prose="Boston are 8-2-1 with 42 goals for and 22 against, and have won four of five at TD Garden, so "
               "the Bruins are the selection against a San Jose side whose 13 points include just one "
               "regulation win. The Sharks are a respectable 4-2-1 on the road, which is why our estimate "
               "sits just under 70% at a fair price of -225 and the Bruins stay in the medium tier rather than "
               "clearing the high bar."),
    dict(match="nhl-nyr-ott", side="b", market="Match winner (money line)",
         prose="The Rangers' road split is the decisive number: 1-4-1 away with eight goals scored and 19 "
               "conceded. Ottawa are 7-4-0 overall and 4-2-0 at home and are our money-line pick, though a "
               "55% estimate keeps this a low-confidence lean. The overall records are almost identical, so "
               "the venue split carries the whole argument."),
    dict(match="nhl-tor-edm", side="b", market="Match winner (money line)",
         prose="Edmonton are 8-1-1 with 47 goals scored and a three-game winning run, and they host a Toronto "
               "team on 14 points from 12 games. The Oilers rate near 75% on the money line, our strongest "
               "hockey number of the night, but a fair -306 is shorter than the brief's -250 floor. That "
               "price ceiling, not the probability, is what caps this row at medium."),
    dict(match="nhl-tb-uta", side="a", market="Match winner (money line)",
         prose="Utah are 7-4-0 and Tampa Bay 7-3-0, so the records are level. The Lightning's road form is "
               "the soft spot (2-3-0 away, 16 scored, 20 conceded) against a Utah home record of 3-1-0, yet "
               "our line still makes Tampa Bay the narrowest of money-line favourites at a fair -102. That is "
               "a coin-flip lean, not a conviction play, and it is graded low."),
    dict(match="nhl-min-sea", side="b", market="Match winner (money line)",
         prose="Seattle are 7-3-1 on a two-game winning run and 3-2-0 at home, while Minnesota have taken two "
               "of seven on the road (2-3-2, 17 goals for, 19 against). The Kraken are the money-line pick at "
               "around 58% and a fair -140. The start time was not readable in the official schedule block we "
               "loaded, so "
               "confirm the puck drop before staking anything."),

    dict(match="mlb-tb-mil", side="b", market="Match winner (money line)",
         prose="Milwaukee lead the World Series 1-0 and send Logan Henderson against Drew Rasmussen in Game 2 "
               "at American Family Field. The Brewers went 103-59 with a 55-26 home record and an 8-2 last "
               "ten, while Tampa Bay were 43-38 on the road and arrive off a Game 1 defeat. Back Milwaukee "
               "near 56%; the Rays' 98 wins keep this low confidence."),

    dict(match="gaa-nemo-finbarrs", side="a", market="Match winner",
         prose="Nemo Rangers meet St Finbarrs in the Cork Premier SFC final at SuperValu Pairc Ui Chaoimh. "
               "Nemo beat Carrigaline 1-15 to 0-16 in their semi-final and took two of three group games with "
               "a 57-43 return; St Finbarrs beat Clonakilty 2-12 to 0-16 but won only one of three group "
               "games, scoring 63 and conceding 55. Nemo are the pick at about 64%."),

    dict(match="atp-vienna-final", side="b", market="Match winner",
         prose="Daniil Medvedev, the top seed, meets Nikoloz Basilashvili in the Vienna final after advancing "
               "when Alexander Bublik retired at 6-3, while Basilashvili came through 6-4 6-7(5) 6-3 against "
               "Stefanos Tsitsipas. Medvedev had the shorter semi-final and is the selection at roughly 64%. "
               "No ranking or head-to-head feed was read, so this is a low-confidence call."),
]

# ---------------------------------------------------------------------------
# Market investigation.  Every family is listed for every priced match; families
# we could not originate carry the missing input that blocked them.
# ---------------------------------------------------------------------------

MARKET_FAMILIES = [
    ("Match winner", "Priced", "Two-way market from the originated win probability."),
    ("Handicap / line", "Withheld", "No official handicap line is published on the sources we can read; a "
                                    "self-made spread would be a guess dressed as a market."),
    ("Match total", "Withheld", "Requires per-team scoring rates at the venue; only win/loss splits were "
                                "readable for this sport."),
]

NHL_MARKET_FAMILIES = [
    ("Match winner", "Priced", "Two-way money line from the originated win probability."),
    ("Puck line -1.5 / +1.5", "Priced", "Derived from an independent-Poisson goal model whose rates come "
                                        "from each club's official goals for/against per game."),
    ("Match total", "Priced", "Poisson total; the line is ours, not a bookmaker's, and is published as a "
                              "half-goal line."),
    ("Correct score / first goalscorer / props", "Withheld",
     "No official scorer or line-combination feed was read; pricing them would be invention."),
]

TENNIS_MARKET_FAMILIES = [
    ("Match winner", "Priced", "Two-way market from the originated win probability."),
    ("Total games / set betting", "Withheld", "Requires serve and return statistics for both players; the "
                                              "official scores page carries no season serve data."),
    ("Handicap games", "Withheld", "Same missing input as total games."),
]

MLB_MARKET_FAMILIES = [
    ("Match winner (money line)", "Priced", "Two-way market from the originated win probability."),
    ("Run line -1.5 / +1.5", "Withheld", "Needs both clubs' run rates; only the Rays' runs scored/allowed "
                                         "block was read and the Brewers' block was truncated."),
    ("Game total", "Withheld", "Same missing run-rate input."),
]

GAA_MARKET_FAMILIES = [
    ("Match winner", "Priced", "Two-way market from the originated win probability."),
    ("Handicap / total points", "Withheld", "Cork GAA publishes scorelines but no per-game scoring-rate "
                                            "table or line; any handicap would be invented."),
]

# ---------------------------------------------------------------------------
# Sports the desk could not price.  Reason + the source that blocked (or lacks)
# the market, so the gap is auditable rather than hidden.
# ---------------------------------------------------------------------------

GAPS = [
    dict(sport="Golf", olbg="https://www.olbg.com/betting-tips/Golf/5", blocked="OLBG golf hub returned "
         '"No tips found" at 17:50Z, so there is no golf market on the site to originate against.',
         source="https://www.olbg.com/betting-tips/Golf/5"),
    dict(sport="Volleyball", olbg="https://www.olbg.com/betting-tips/Volleyball/21",
         blocked="Fixtures are listed, but neither legavolley.it (SuperLega) nor plusliga.pl served a readable "
                 "fixture or standings block; tauronliga.pl returned the Polish women's site instead.",
         source="https://ww2.legavolley.it/lvc/"),
    dict(sport="Rugby Union", olbg="https://www.olbg.com/betting-tips/Rugby_Union/9",
         blocked="URC Round 4 was readable for completed matches only; the remaining fixtures did not render, "
                 "lnr.fr returned 404 and premrugby.com served a JavaScript shell with no fixture rows.",
         source="https://stats.unitedrugby.com/match-centre/2026-27/4"),
    dict(sport="Cricket", olbg="https://www.olbg.com/betting-tips/Cricket/7",
         blocked="OLBG lists Pakistan v England and several CSA T20 games, but pcb.com.pk's fixtures routes "
                 "returned its 404 page and no other official board schedule was read.",
         source="https://www.pcb.com.pk/404page.html"),
    dict(sport="Snooker", olbg="https://www.olbg.com/betting-tips/Snooker/8",
         blocked="The only snooker listing (Mark Williams v Jak Jones, 14:05) had already started at read "
                 "time, so no future match exists to price.",
         source="https://www.olbg.com/betting-tips/Snooker/8"),
    dict(sport="Darts", olbg="https://www.olbg.com/betting-tips/Darts/15",
         blocked="pdc.tv served a consent wall with no readable tournament, draw or order of play.",
         source="https://www.pdc.tv/tournaments"),
    dict(sport="Greyhounds", olbg="https://www.olbg.com/betting-tips/Greyhounds/28",
         blocked="Only graded races with single tips are listed; no official runner, trap or result feed "
                 "was readable, so no runner-level line can be originated.",
         source="https://www.olbg.com/betting-tips/Greyhounds/28"),
    dict(sport="Motor Racing", olbg="https://www.olbg.com/betting-tips/Motor_Racing/14",
         blocked="The United States Grand Prix weekend was mid-practice at read time; formula1.com carried no "
                 "qualifying classification, so no grid-based line could be originated.",
         source="https://www.formula1.com/en/racing/2026/united-states"),
    dict(sport="Handball", olbg="https://www.olbg.com/betting-tips/Handball/20",
         blocked="ehfcl.eurohandball.com/en/matches/ and eurohandball.com/en/matches/ both returned 404; no "
                 "HBL or LNH fixture/standings block was readable.",
         source="https://ehfcl.eurohandball.com/en/matches/"),
    dict(sport="Rugby League", olbg="https://www.olbg.com/betting-tips/Rugby_League/10",
         blocked="OLBG lists only 2027 outright markets (State of Origin, Super League and NRL Grand Final); "
                 "no 2026 match market is open, so nothing can be priced.",
         source="https://www.olbg.com/betting-tips/Rugby_League/10"),
]

# ---------------------------------------------------------------------------
# Flagged irregularities.  severity: high / medium / low
# ---------------------------------------------------------------------------

FLAGS = [
    dict(id="F-01", severity="high", sport="All",
         title="The High tier is empty because the brief's two rules intersect in a 1.4-point window",
         detail="The brief defines a high-confidence pick as better than 70% and also requires the fair price "
                "to be no shorter than -250. A -250 price is 71.43%, so only selections between 70.00% and "
                "71.43% can satisfy both rules. No selection originated on this card lands in that window, "
                "so zero High picks are published rather than one being manufactured to fill the tier.",
         link="https://www.olbg.com/betting-tips", link_label="OLBG betting-tips index (discovery)"),
    dict(id="F-02", severity="medium", sport="Basketball / Ice Hockey",
         title="Three selections clear 70% but are excluded by the -250 floor",
         detail="Philadelphia (78.9%, fair -375) and Edmonton (75.4%, fair -306) both exceed 70% on our "
                "numbers, but their fair prices are shorter than -250, which the brief excludes, so they are "
                "published at medium tier. No selection landed between 70.00% and 71.43%, the only span that "
                "could satisfy both of the brief's rules.",
         link="https://www.nba.com/games", link_label="NBA games (records used)"),
    dict(id="F-03", severity="high", sport="All",
         title="Availability is sourced for basketball only; the other eight priced rows are blank",
         detail="The five NBA rows now carry the official 1:00 PM ET injury report, including the two games "
                "where a club had not yet submitted a sheet (Milwaukee, and both San Antonio and Dallas) — "
                "those stay blank because unknown is not clear. No official NHL, MLB, Cork GAA or ATP "
                "availability document was read, so those rows remain blank by design and must not be read "
                "as 'no injuries'.",
         link="https://ak-static.cms.nba.com/referee/injury/Injury-Report_2026-10-24_01_00PM.pdf",
         link_label="NBA official injury report, 24 Oct 2026 1:00 PM ET"),
    dict(id="F-04", severity="high", sport="15 covered sports",
         title="Ten of the fifteen requested sports carry no priced selection",
         detail="Golf, Volleyball, Rugby Union, Cricket, Snooker, Darts, Greyhounds, Motor Racing, Handball "
                "and Rugby League are published as gaps with the exact blocking source on the sports pages "
                "and on the Flagged page. The five sports with prices are Basketball, Ice Hockey, Baseball, "
                "Gaelic Sports and Tennis.",
         link="https://www.olbg.com/betting-tips", link_label="OLBG betting-tips index"),
    dict(id="F-05", severity="low", sport="Ice Hockey",
         title="Minnesota Wild at Seattle Kraken start time not read",
         detail="The official schedule's timing block for game 2026020179 was not reached before the read "
                "stopped, so the row carries a blank start rather than a guessed one.",
         link="https://api-web.nhle.com/v1/schedule/2026-10-24", link_label="NHL schedule API"),
    dict(id="F-06", severity="low", sport="Tennis",
         title="Vienna final pairing and start are partly derived",
         detail="Both semi-finals are confirmed on the official ATP scores page, so the final pairing follows "
                "from them; the start time is not published there. The only time available was OLBG's listing "
                "(06:00), which is discovery and is not used as a fixture fact.",
         link="https://www.atptour.com/en/scores/current", link_label="ATP Tour scores"),
    dict(id="F-07", severity="medium", sport="Darts / Handball / Volleyball / Rugby Union",
         title="Four governing-body sites were unreadable from this environment",
         detail="pdc.tv (consent wall), ehfcl.eurohandball.com and eurohandball.com (404), legavolley.it "
                "(landing page only) and lnr.fr (404) could not supply fixtures, so those sports carry no "
                "lines. The dead ends are listed on the sources page rather than skipped silently.",
         link="https://www.pdc.tv/tournaments", link_label="PDC tournaments (consent wall)"),
    dict(id="F-08", severity="medium", sport="Basketball",
         title="NBA season-leader block on the official games page is not citable",
         detail="The games page labels a Milwaukee player under Miami and a Charlotte player under Charlotte "
                "with mismatched club codes. Because the labels are internally inconsistent, no player-level "
                "statistic from that block is used in any write-up.",
         link="https://www.nba.com/games", link_label="NBA games"),
    dict(id="F-09", severity="medium", sport="All",
         title="Five-per-sport quota not met",
         detail="The desk publishes 13 selections across five sports (Basketball 5, Ice Hockey 5, Baseball 1, "
                "Gaelic Sports 1, Tennis 1). Ten sports produced none because no official fixture-and-form "
                "source was readable. Nothing was written to reach a quota.",
         link="https://www.olbg.com/betting-tips", link_label="OLBG betting-tips index"),
    dict(id="F-10", severity="low", sport="Repository",
         title="COORDINATION.md contains two sections numbered 78",
         detail="Sections by sessions 7a9b24e5-olbg1 and 37003e61-olbg1 are both headed '## 78.', and the "
                "second appears after sections 79 and 80. Numbering is not sequential; content is not "
                "affected, but cross-references by section number are ambiguous.",
         link="https://github.com/buffedlizard55-lab/OLBG1/blob/main/COORDINATION.md",
         link_label="COORDINATION.md"),
    dict(id="F-11", severity="low", sport="Repository",
         title="Six desk directories have no namespaced data directory",
         detail="2360a617, 6a081cf6, aa4e9dbf, ccb6bde2, ebfbd966 and f7fa77fc publish pages without a "
                "matching data/<id>/ folder. Some store JSON as flat suffixed files or under datasets/, so "
                "this is a layout inconsistency, not proven data loss.",
         link="https://github.com/buffedlizard55-lab/OLBG1", link_label="Repository root"),
]

# ---------------------------------------------------------------------------
# Repository audit, line by line, of things that can be checked mechanically.
# ---------------------------------------------------------------------------

AUDIT = [
    dict(id="A-01", area="Root navigation", check="Every local href in the root index.html resolves on disk",
         result="75 local links, 0 missing", verdict="pass",
         note="Checked with a filesystem resolution pass; anchors stripped before testing."),
    dict(id="A-02", area="Canonical data", check="count fields equal the length of the list they describe",
         result="data/lines.json count 126 with 126 rows; data/fixtures.json count 134 with 134 rows; "
                "data/predictions.json count 30 with 30 rows", verdict="pass", note="Internal consistency only."),
    dict(id="A-03", area="Canonical data", check="Behaviour of the canonical High tier in data/lines.json",
         result="confidence_counts reports 30 high / 30 medium / 66 low", verdict="flag",
         note="The canonical file's 30 high rows are not re-verified here. Desk 02d3d515 recorded that some "
              "of its high rows sit below 70%; this desk did not re-read every row and makes no claim either way."),
    dict(id="A-04", area="Scope", check="/sports contains one page per covered sport",
         result="17 pages for a 15-sport brief", verdict="flag",
         note="The extra two are Australian rules and eSports, which the brief does not list."),
    dict(id="A-05", area="Coordination", check="Section numbering in COORDINATION.md is unique",
         result="two '## 78.' headings", verdict="flag", note="See F-10."),
    dict(id="A-06", area="Desk layout", check="Every desk directory has a namespaced data folder",
         result="6 of 60 desk directories have none", verdict="flag", note="See F-11."),
    dict(id="A-07", area="Ignored artefacts", check=".gitignore excludes build output and raw responses",
         result="ignores _site/, node_modules/, .output/, .cache/, data/current/raw/, data/release/raw/, "
                "*.pyc", verdict="pass", note="Read directly from .gitignore."),
]
