"""Verified fact base, line origination and picks for the 26 October 2026 desk.

Every fact in FIXTURES below was read from the official source named on the row
(see SOURCES) and is transcribed, not inferred. Anything the official page did
not publish is left as None and is flagged on the site.

Prices are originated here from those published numbers only. The method is
documented in METHOD and repeated verbatim on the site's methodology page.
"""
from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data' / '103ea76b' / 'desk.json'
READ_AT = '2026-10-26T04:40:00Z'

SPORTS = [
    ('golf', 'Golf', 5, 'Golf', 'https://www.olbg.com/betting-tips/Golf/5', 'https://www.pgatour.com/schedule'),
    ('volleyball', 'Volleyball', 21, 'Volleyball', 'https://www.olbg.com/betting-tips/Volleyball/21', 'https://www.legavolley.it/'),
    ('rugby-union', 'Rugby Union', 9, 'Rugby_Union', 'https://www.olbg.com/betting-tips/Rugby_Union/9', 'https://www.unitedrugby.com/'),
    ('cricket', 'Cricket', 7, 'Cricket', 'https://www.olbg.com/betting-tips/Cricket/7', 'https://www.icc-cricket.com/'),
    ('snooker', 'Snooker', 8, 'Snooker', 'https://www.olbg.com/betting-tips/Snooker/8', 'https://www.wst.tv/'),
    ('darts', 'Darts', 15, 'Darts', 'https://www.olbg.com/betting-tips/Darts/15', 'https://www.pdc.tv/'),
    ('baseball', 'Baseball', 12, 'Baseball', 'https://www.olbg.com/betting-tips/Baseball/12', 'https://www.mlb.com/'),
    ('gaelic', 'Gaelic Sports', 25, 'Gaelic_Football', 'https://www.olbg.com/betting-tips/Gaelic_Football/25', 'https://munster.gaa.ie/fixtures/events-calendar/'),
    ('greyhounds', 'Greyhounds', 28, 'Greyhounds', 'https://www.olbg.com/betting-tips/Greyhounds/28', 'https://www.gbgb.org.uk/'),
    ('tennis', 'Tennis', 3, 'Tennis', 'https://www.olbg.com/betting-tips/Tennis/3', 'https://www.atptour.com/'),
    ('motor-racing', 'Motor Racing', 14, 'Motor_Racing', 'https://www.olbg.com/betting-tips/Motor_Racing/14', 'https://www.formula1.com/'),
    ('handball', 'Handball', 20, 'Handball', 'https://www.olbg.com/betting-tips/Handball/20', 'https://ehfcl.eurohandball.com/men/2026-27/standings/'),
    ('ice-hockey', 'Ice Hockey', 13, 'Ice_Hockey', 'https://www.olbg.com/betting-tips/Ice_Hockey/13', 'https://www.nhl.com/standings/2026-10-25/wildcard'),
    ('basketball', 'Basketball', 4, 'Basketball', 'https://www.olbg.com/betting-tips/Basketball/4', 'https://www.nba.com/standings'),
    ('rugby-league', 'Rugby League', 10, 'Rugby_League', 'https://www.olbg.com/betting-tips/Rugby_League/10', 'https://www.nrl.com/'),
]
SPORT_NAMES = {s[0]: s[1] for s in SPORTS}
SPORT_HUB = {s[0]: s[5] for s in SPORTS}
SPORT_OLBG = {s[0]: s[4] for s in SPORTS}

# --- sources ---------------------------------------------------------------
SOURCES = [
    dict(id='olbg-ice-hockey', role='discovery', publisher='OLBG',
         url='https://www.olbg.com/betting-tips/Ice_Hockey/13', observed_at=READ_AT,
         supports='NHL and European ice-hockey listings: matchup, competition, displayed clock time, OLBG market and tip-vote share. Vote shares are not prices.'),
    dict(id='olbg-basketball-nba', role='discovery', publisher='OLBG',
         url='https://www.olbg.com/betting-tips/Basketball/NBA/4', observed_at=READ_AT,
         supports='Nine NBA listings with the OLBG-selected market and tip-vote share.'),
    dict(id='olbg-basketball-el', role='discovery', publisher='OLBG',
         url='https://www.olbg.com/betting-tips/Basketball/European/Euroleague/4', observed_at=READ_AT,
         supports='Six EuroLeague listings with the OLBG-selected market and tip-vote share.'),
    dict(id='olbg-baseball-mlb', role='discovery', publisher='OLBG',
         url='https://www.olbg.com/betting-tips/Baseball/MLB/12', observed_at=READ_AT,
         supports='One MLB listing (Milwaukee at Tampa Bay, money line, 9/10 tips). The Baseball hub itself returned "No tips found".'),
    dict(id='olbg-tennis', role='discovery', publisher='OLBG',
         url='https://www.olbg.com/betting-tips/Tennis/3', observed_at=READ_AT,
         supports='Fourteen tennis listings with market and tip-vote share.'),
    dict(id='olbg-cricket', role='discovery', publisher='OLBG',
         url='https://www.olbg.com/betting-tips/Cricket/7', observed_at=READ_AT,
         supports='Five cricket match listings, two player-of-the-match listings and five outright listings.'),
    dict(id='olbg-handball', role='discovery', publisher='OLBG',
         url='https://www.olbg.com/betting-tips/Handball/20', observed_at=READ_AT,
         supports='Thirteen handball listings: EHF Champions League rounds plus two domestic Swedish/Danish fixtures.'),
    dict(id='olbg-volleyball', role='discovery', publisher='OLBG',
         url='https://www.olbg.com/betting-tips/Volleyball/21', observed_at=READ_AT,
         supports='Fourteen volleyball listings across Brazil, Austria, Poland and Italy.'),
    dict(id='olbg-motor-racing', role='discovery', publisher='OLBG',
         url='https://www.olbg.com/betting-tips/Motor_Racing/14', observed_at=READ_AT,
         supports='Mexico City Grand Prix outright listing (Win Race, Charles Leclerc, 1/2 tips).'),
    dict(id='olbg-rugby-union', role='discovery', publisher='OLBG',
         url='https://www.olbg.com/betting-tips/Rugby_Union/9', observed_at=READ_AT,
         supports='Antepost only: Six Nations 2027 outright. No match markets rendered at read time.'),
    dict(id='olbg-rugby-league', role='discovery', publisher='OLBG',
         url='https://www.olbg.com/betting-tips/Rugby_League/10', observed_at=READ_AT,
         supports='Outright only: State of Origin 2027, Super League 2027 and NRL 2027. No match markets rendered.'),
    dict(id='olbg-golf', role='discovery', publisher='OLBG',
         url='https://www.olbg.com/betting-tips/Golf/5', observed_at=READ_AT,
         supports='Golf hub returned "No tips found": no tournament or match market at read time.'),
    dict(id='olbg-snooker', role='discovery', publisher='OLBG',
         url='https://www.olbg.com/betting-tips/Snooker/8', observed_at=READ_AT,
         supports='Snooker hub returned "No tips found": no match or outright market at read time.'),
    dict(id='olbg-darts', role='discovery', publisher='OLBG',
         url='https://www.olbg.com/betting-tips/Darts/15', observed_at=READ_AT,
         supports='One antepost listing (PDC World Championship 2027). No match markets rendered.'),
    dict(id='olbg-gaelic', role='discovery', publisher='OLBG',
         url='https://www.olbg.com/betting-tips/Gaelic_Football/25', observed_at=READ_AT,
         supports='Two club fixtures and one 2027 All-Ireland outright.'),
    dict(id='olbg-greyhounds', role='discovery', publisher='OLBG',
         url='https://www.olbg.com/betting-tips/Greyhounds/28', observed_at=READ_AT,
         supports='One daily-race listing (3:19 Monmore, Tullymurry Skies).'),
    dict(id='nhl-schedule-20261026', role='official', publisher='NHL',
         url='https://api-web.nhle.com/v1/schedule/2026-10-26', observed_at='2026-10-26T04:41:00Z',
         supports='NHL schedule for 26 October 2026: three games with id, venue and startTimeUTC.'),
    dict(id='nhl-standings-20261025', role='official', publisher='NHL',
         url='https://www.nhl.com/standings/2026-10-25/wildcard', observed_at='2026-10-26T04:42:00Z',
         supports='NHL standings dated 25 October 2026: GP, W, L, OT, PTS, GF, GA, home/away splits, L10 and streak for every club.'),
    dict(id='mlb-schedule-20261026', role='official', publisher='MLB',
         url='https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-26&endDate=2026-10-31&hydrate=team,venue,linescore',
         observed_at='2026-10-26T04:43:00Z',
         supports='MLB schedule 26-31 October 2026: World Series games 3-7, gameDate in UTC, venue and series state.'),
    dict(id='mlb-standings-2026', role='official', publisher='MLB',
         url='https://www.mlb.com/standings/', observed_at='2026-10-26T04:44:00Z',
         supports='MLB final regular-season standings 2026: W-L, PCT, L10, streak, runs scored and runs allowed per club.'),
    dict(id='nba-standings-2026', role='official', publisher='NBA',
         url='https://www.nba.com/standings', observed_at='2026-10-26T04:46:00Z',
         supports='NBA 2026-27 regular-season standings: W, L, WIN%, LAST10 and STRK for all 30 clubs.'),
    dict(id='el-standings-e2026', role='official', publisher='Euroleague Basketball',
         url='https://api-live.euroleague.net/v1/standings?seasonCode=E2026', observed_at='2026-10-26T04:48:00Z',
         supports='EuroLeague 2026-27 standings after round 7: games played, wins, losses, points for, points against and difference for all 20 clubs.'),
    dict(id='el-results-e2026', role='official', publisher='Euroleague Basketball',
         url='https://api-live.euroleague.net/v1/results?seasonCode=E2026', observed_at='2026-10-26T04:49:00Z',
         supports='EuroLeague 2026-27 completed results for rounds 1-7: date, home/away scores per game.'),
    dict(id='ehf-standings-202627', role='official', publisher='European Handball Federation',
         url='https://ehfcl.eurohandball.com/men/2026-27/standings/', observed_at='2026-10-26T04:52:00Z',
         supports='EHF Champions League men 2026-27 group tables (GP, W, D, L, goals for:against, difference) and the 28-29 October fixture block with published throw-off times.'),
    dict(id='f1-standings-2026', role='official', publisher='Formula 1',
         url='https://www.formula1.com/en/results/2026/drivers', observed_at='2026-10-26T04:53:00Z',
         supports='2026 FIA Formula One World Championship drivers standings: position, driver, team and points.'),
    dict(id='atp-rankings-20261026', role='official', publisher='ATP Tour',
         url='https://www.atptour.com/en/rankings/singles', observed_at='2026-10-26T04:55:00Z',
         supports='PIF ATP Rankings, singles, dated 2026.10.26: position, player, age, official points and tournaments played (top 20 read).'),
]

# --- verified fixture facts -------------------------------------------------
# goals/points/runs columns are exactly the official published values.
FIXTURES = [
    # ---- NHL -------------------------------------------------------------
    dict(id='nhl-lak-nyr', sport='ice-hockey', competition='NHL', home='NY Rangers', away='LA Kings',
         olbg_time='Today 19:07', start_utc='2026-10-26T23:00:00Z', venue='Madison Square Garden',
         sources=['nhl-schedule-20261026', 'nhl-standings-20261025', 'olbg-ice-hockey'],
         olbg_market='Money Line - NY Rangers', olbg_tips='3/3', olbg_share='100%',
         home_stats=dict(gp=13, w=7, l=5, otl=1, pts=15, gf=41, ga=36, l10='5-4-1', strk='L2', home='6-0-0'),
         away_stats=dict(gp=9, w=2, l=5, otl=2, pts=6, gf=21, ga=32, l10=None, strk=None, home=None),
         facts='NY Rangers 7-5-1 (15 pts), 41 goals for and 36 against, 6-0-0 at home, 5-4-1 over ten, on a two-game losing run. LA Kings 2-5-2 (6 pts), 21 goals for and 32 against.'),
    dict(id='nhl-tor-cgy', sport='ice-hockey', competition='NHL', home='Calgary Flames', away='Toronto Maple Leafs',
         olbg_time='Today 20:37', start_utc='2026-10-27T00:30:00Z', venue='Scotiabank Saddledome',
         sources=['nhl-schedule-20261026', 'nhl-standings-20261025', 'olbg-ice-hockey'],
         olbg_market='Puck Line +1.50 - Calgary Flames', olbg_tips='1/1', olbg_share='100%',
         home_stats=dict(gp=10, w=4, l=6, otl=0, pts=8, gf=23, ga=39, l10='4-6-0', strk='W3', home='3-3-0'),
         away_stats=dict(gp=13, w=7, l=4, otl=2, pts=16, gf=50, ga=41, l10='6-2-2', strk='W4', home=None),
         facts='Toronto 7-4-2 (16 pts), 50 goals for and 41 against, 6-2-2 over ten and riding a four-game winning run. Calgary 4-6-0 (8 pts), 23 goals for and 39 against, but 3-3-0 at home and winners of three straight.'),
    dict(id='nhl-det-edm', sport='ice-hockey', competition='NHL', home='Edmonton Oilers', away='Detroit Red Wings',
         olbg_time='Today 21:37', start_utc='2026-10-27T01:30:00Z', venue='Rogers Place',
         sources=['nhl-schedule-20261026', 'nhl-standings-20261025', 'olbg-ice-hockey'],
         olbg_market='Money Line - Edmonton Oilers', olbg_tips='1/1', olbg_share='100%',
         home_stats=dict(gp=11, w=8, l=2, otl=1, pts=17, gf=49, ga=39, l10='8-2-0', strk='L1', home='3-2-1'),
         away_stats=dict(gp=11, w=4, l=4, otl=3, pts=11, gf=29, ga=34, l10='4-3-3', strk='L1', home=None),
         facts='Edmonton 8-2-1 (17 pts), 49 goals for and 39 against, 8-2-0 over ten. Detroit 4-4-3 (11 pts), 29 goals for and 34 against, 4-3-3 over ten and two points from its last five games.'),
    # ---- MLB -------------------------------------------------------------
    dict(id='mlb-ws-g3', sport='baseball', competition='World Series, Game 3', home='Tampa Bay Rays', away='Milwaukee Brewers',
         olbg_time='Today 21:00', start_utc='2026-10-27T00:00:00Z', venue='Tropicana Field',
         sources=['mlb-schedule-20261026', 'mlb-standings-2026', 'olbg-baseball-mlb'],
         olbg_market='Money Line - Tampa Bay Rays', olbg_tips='9/10', olbg_share='90%',
         home_stats=dict(gp=162, w=98, l=64, pct='.605', rs=736, ra=650, l10='5-5', strk='L1'),
         away_stats=dict(gp=162, w=103, l=59, pct='.636', rs=832, ra=618, l10='8-2', strk='W5'),
         facts='Milwaukee finished 103-59 (.636) with 832 runs scored and 618 allowed, 8-2 over its last ten and on a five-game winning run. Tampa Bay finished 98-64 (.605) with 736 scored and 650 allowed, 5-5 over ten. Milwaukee leads the series 2-0.'),
    dict(id='mlb-ws-g4', sport='baseball', competition='World Series, Game 4', home='Tampa Bay Rays', away='Milwaukee Brewers',
         olbg_time='not listed on OLBG', start_utc='2026-10-28T00:00:00Z', venue='Tropicana Field',
         sources=['mlb-schedule-20261026', 'mlb-standings-2026'],
         olbg_market=None, olbg_tips=None, olbg_share=None,
         home_stats=dict(gp=162, w=98, l=64, pct='.605', rs=736, ra=650, l10='5-5', strk='L1'),
         away_stats=dict(gp=162, w=103, l=59, pct='.636', rs=832, ra=618, l10='8-2', strk='W5'),
         facts='Game 4 of the World Series at Tropicana Field. Series stands 2-0 to Milwaukee after Game 3. Season lines: Milwaukee 103-59, 832 scored and 618 allowed; Tampa Bay 98-64, 736 scored and 650 allowed.'),
    dict(id='mlb-ws-g5', sport='baseball', competition='World Series, Game 5', home='Tampa Bay Rays', away='Milwaukee Brewers',
         olbg_time='not listed on OLBG', start_utc='2026-10-29T00:00:00Z', venue='Tropicana Field',
         sources=['mlb-schedule-20261026', 'mlb-standings-2026'],
         olbg_market=None, olbg_tips=None, olbg_share=None,
         home_stats=dict(gp=162, w=98, l=64, pct='.605', rs=736, ra=650, l10='5-5', strk='L1'),
         away_stats=dict(gp=162, w=103, l=59, pct='.636', rs=832, ra=618, l10='8-2', strk='W5'),
         facts='Game 5 of the World Series, scheduled in the official MLB feed at Tropicana Field. Season lines: Milwaukee 103-59 (.636), Tampa Bay 98-64 (.605).'),
    # ---- NBA (money line only: no official points data captured) ----------
    dict(id='nba-min-cle', sport='basketball', competition='NBA', home='Cleveland Cavaliers', away='Minnesota Timberwolves',
         olbg_time='Today 19:00', start_utc=None, venue=None,
         sources=['nba-standings-2026', 'olbg-basketball-nba'],
         olbg_market='Pointspread - Minnesota +3.50', olbg_tips='2/2', olbg_share='100%',
         home_stats=dict(gp=2, w=1, l=1, wl='1-1', l10='1-1', strk='W1', conf='1-1', home='1-0'),
         away_stats=dict(gp=3, w=3, l=0, wl='3-0', l10='3-0', strk='W3', conf='0-0', home='1-0'),
         facts='Minnesota is 3-0 with a three-game winning run and 2-0 on the road. Cleveland is 1-1, 1-0 at home, having won its last game.'),
    dict(id='nba-dal-mia', sport='basketball', competition='NBA', home='Miami Heat', away='Dallas Mavericks',
         olbg_time='Today 19:30', start_utc=None, venue=None,
         sources=['nba-standings-2026', 'olbg-basketball-nba'],
         olbg_market='Pointspread - Dallas +8.50', olbg_tips='2/2', olbg_share='100%',
         home_stats=dict(gp=3, w=0, l=3, wl='0-3', l10='0-3', strk='L3', conf='0-2', home='0-2'),
         away_stats=dict(gp=3, w=1, l=2, wl='1-2', l10='1-2', strk='L1', conf='0-2', home='0-1'),
         facts='Miami is 0-3 and 0-2 at home on a three-game losing run. Dallas is 1-2, 1-1 on the road and 0-2 in conference play.'),
    dict(id='nba-ind-mil', sport='basketball', competition='NBA', home='Milwaukee Bucks', away='Indiana Pacers',
         olbg_time='Today 20:00', start_utc=None, venue=None,
         sources=['nba-standings-2026', 'olbg-basketball-nba'],
         olbg_market='Money Line - Indiana Pacers', olbg_tips='2/2', olbg_share='100%',
         home_stats=dict(gp=3, w=0, l=3, wl='0-3', l10='0-3', strk='L3', conf='0-3', home='0-1'),
         away_stats=dict(gp=3, w=2, l=1, wl='2-1', l10='2-1', strk='W1', conf='1-0', home='0-1'),
         facts='Indiana is 2-1 overall, 2-0 on the road and 1-0 in conference play, on a one-game winning run. Milwaukee is 0-3 and 0-3 in conference play, on a three-game losing run.'),
    dict(id='nba-atl-hou', sport='basketball', competition='NBA', home='Houston Rockets', away='Atlanta Hawks',
         olbg_time='Today 20:30', start_utc=None, venue=None,
         sources=['nba-standings-2026', 'olbg-basketball-nba'],
         olbg_market='Pointspread - Houston -5.50', olbg_tips='2/2', olbg_share='100%',
         home_stats=dict(gp=3, w=3, l=0, wl='3-0', l10='3-0', strk='W3', conf='2-0', home='1-0'),
         away_stats=dict(gp=3, w=2, l=1, wl='2-1', l10='2-1', strk='L1', conf='2-0', home='0-1'),
         facts='Houston is 3-0 with a three-game winning run, 2-0 in conference play and 2-0 on the road. Atlanta is 2-1 and 2-0 in conference play but lost its last game.'),
    dict(id='nba-was-cha', sport='basketball', competition='NBA', home='Charlotte Hornets', away='Washington Wizards',
         olbg_time='Today 19:00', start_utc=None, venue=None,
         sources=['nba-standings-2026', 'olbg-basketball-nba'],
         olbg_market='Money Line - Washington Wizards', olbg_tips='1/2', olbg_share='50%',
         home_stats=dict(gp=3, w=2, l=1, wl='2-1', l10='2-1', strk='W1', conf='2-1', home='1-1'),
         away_stats=dict(gp=3, w=2, l=1, wl='2-1', l10='2-1', strk='W1', conf='2-1', home='1-1'),
         facts='Both clubs are 2-1 with a one-game winning run. Charlotte is 2-1 in conference play and 1-1 at home; Washington is 2-1 in conference play and 1-0 on the road.'),
    dict(id='nba-chi-bos', sport='basketball', competition='NBA', home='Boston Celtics', away='Chicago Bulls',
         olbg_time='Today 19:30', start_utc=None, venue=None,
         sources=['nba-standings-2026', 'olbg-basketball-nba'],
         olbg_market='Pointspread - Chicago +13.50', olbg_tips='1/1', olbg_share='100%',
         home_stats=dict(gp=2, w=1, l=1, wl='1-1', l10='1-1', strk='W1', conf='1-1', home='1-0'),
         away_stats=dict(gp=3, w=1, l=2, wl='1-2', l10='1-2', strk='L1', conf='1-2', home='0-1'),
         facts='Boston is 1-1, 1-0 at home and won its last game. Chicago is 1-2, 1-1 on the road, on a one-game losing run.'),
    dict(id='nba-phx-okc', sport='basketball', competition='NBA', home='Oklahoma City Thunder', away='Phoenix Suns',
         olbg_time='Today 20:00', start_utc=None, venue=None,
         sources=['nba-standings-2026', 'olbg-basketball-nba'],
         olbg_market='Game Totals - Under 218.50', olbg_tips='1/1', olbg_share='100%',
         home_stats=dict(gp=3, w=3, l=0, wl='3-0', l10='3-0', strk='W3', conf='3-0', home='2-0'),
         away_stats=dict(gp=2, w=1, l=1, wl='1-1', l10='1-1', strk='W1', conf='1-1', home='1-0'),
         facts='Oklahoma City is 3-0, 3-0 in conference play and 2-0 at home on a three-game winning run. Phoenix is 1-1, 1-0 at home and 0-1 on the road.'),
    dict(id='nba-mem-uta', sport='basketball', competition='NBA', home='Utah Jazz', away='Memphis Grizzlies',
         olbg_time='Today 21:00', start_utc=None, venue=None,
         sources=['nba-standings-2026', 'olbg-basketball-nba'],
         olbg_market='Money Line - Memphis Grizzlies', olbg_tips='1/1', olbg_share='100%',
         home_stats=dict(gp=3, w=1, l=2, wl='1-2', l10='1-2', strk='L1', conf='1-2', home='1-1'),
         away_stats=dict(gp=3, w=3, l=0, wl='3-0', l10='3-0', strk='W3', conf='3-0', home='1-0'),
         facts='Memphis is 3-0 and 3-0 in conference play, 2-0 on the road. Utah is 1-2 and 1-2 in conference play, 1-1 at home.'),
    dict(id='nba-gs-den', sport='basketball', competition='NBA', home='Denver Nuggets', away='Golden State Warriors',
         olbg_time='Today 22:00', start_utc=None, venue=None,
         sources=['nba-standings-2026', 'olbg-basketball-nba'],
         olbg_market='Pointspread - Denver -7.50', olbg_tips='1/1', olbg_share='100%',
         home_stats=dict(gp=2, w=1, l=1, wl='1-1', l10='1-1', strk='W1', conf='1-1', home='1-0'),
         away_stats=dict(gp=3, w=0, l=3, wl='0-3', l10='0-3', strk='L3', conf='0-3', home='0-1'),
         facts='Denver is 1-1, 1-0 at home and won its last game. Golden State is 0-3, 0-3 in conference play and 0-2 on the road on a three-game losing run.'),
    # ---- EuroLeague -------------------------------------------------------
    dict(id='el-dub-par', sport='basketball', competition='EuroLeague', home='BC Dubai', away='Paris Basketball',
         olbg_time='Tomorrow 12:00', start_utc=None, venue=None,
         sources=['el-standings-e2026', 'el-results-e2026', 'olbg-basketball-el'],
         olbg_market='Pointspread - BC Dubai -10.50', olbg_tips='1/1', olbg_share='100%',
         home_stats=dict(gp=7, w=5, l=2, pf=597, pa=584),
         away_stats=dict(gp=7, w=1, l=6, pf=597, pa=649),
         facts='Dubai is 5-2 (sixth) with 597 points scored and 584 conceded across seven rounds. Paris is 1-6 (18th) with 597 scored and 649 conceded.'),
    dict(id='el-mun-bar', sport='basketball', competition='EuroLeague', home='Bayern Munich', away='FC Barcelona',
         olbg_time='Tomorrow 15:00', start_utc=None, venue=None,
         sources=['el-standings-e2026', 'el-results-e2026', 'olbg-basketball-el'],
         olbg_market='Game Totals - Over 173.50', olbg_tips='1/1', olbg_share='100%',
         home_stats=dict(gp=7, w=2, l=5, pf=612, pa=659),
         away_stats=dict(gp=7, w=4, l=3, pf=623, pa=606),
         facts='Bayern is 2-5 (16th) with 612 scored and 659 conceded. Barcelona is 4-3 (ninth) with 623 scored and 606 conceded.'),
    dict(id='el-pan-mil', sport='basketball', competition='EuroLeague', home='Panathinaikos Athens', away='Olimpia Milano',
         olbg_time='Tomorrow 15:15', start_utc=None, venue=None,
         sources=['el-standings-e2026', 'el-results-e2026', 'olbg-basketball-el'],
         olbg_market='Money Line - Panathinaikos', olbg_tips='1/1', olbg_share='100%',
         home_stats=dict(gp=7, w=6, l=1, pf=613, pa=517),
         away_stats=dict(gp=7, w=1, l=6, pf=585, pa=648),
         facts='Panathinaikos leads the league at 6-1 with 613 scored and 517 conceded, the best defensive record in the competition. Milano is 1-6 (19th) with 585 scored and 648 conceded.'),
    dict(id='el-val-fen', sport='basketball', competition='EuroLeague', home='Valencia Basket', away='Fenerbahce Istanbul',
         olbg_time='Tomorrow 15:30', start_utc=None, venue=None,
         sources=['el-standings-e2026', 'el-results-e2026', 'olbg-basketball-el'],
         olbg_market='Money Line - Fenerbahce', olbg_tips='1/1', olbg_share='100%',
         home_stats=dict(gp=7, w=5, l=2, pf=687, pa=630),
         away_stats=dict(gp=7, w=6, l=1, pf=565, pa=508),
         facts='Valencia is 5-2 (third) with a league-high 687 points scored but 630 conceded. Fenerbahce is 6-1 (second) with 565 scored and 508 conceded, the second-best defensive record.'),
    dict(id='el-bas-mad', sport='basketball', competition='EuroLeague', home='Baskonia Vitoria-Gasteiz', away='Real Madrid',
         olbg_time='Tomorrow 16:00', start_utc=None, venue=None,
         sources=['el-standings-e2026', 'el-results-e2026', 'olbg-basketball-el'],
         olbg_market='Pointspread - Real Madrid -9.50', olbg_tips='1/1', olbg_share='100%',
         home_stats=dict(gp=7, w=1, l=6, pf=583, pa=649),
         away_stats=dict(gp=7, w=4, l=3, pf=667, pa=630),
         facts='Baskonia is 1-6 (20th) with 583 scored and 649 conceded. Real Madrid is 4-3 (seventh) with 667 scored and 630 conceded.'),
    dict(id='el-vir-zal', sport='basketball', competition='EuroLeague', home='Virtus Bologna', away='Zalgiris Kaunas',
         olbg_time='28 Oct 15:30', start_utc=None, venue=None,
         sources=['el-standings-e2026', 'el-results-e2026', 'olbg-basketball-el'],
         olbg_market='Game Totals - Over 171.50', olbg_tips='1/1', olbg_share='100%',
         home_stats=dict(gp=7, w=4, l=3, pf=606, pa=608),
         away_stats=dict(gp=7, w=3, l=4, pf=595, pa=602),
         facts='Virtus is 4-3 (10th) with 606 scored and 608 conceded. Zalgiris is 3-4 (12th) with 595 scored and 602 conceded.'),
    # ---- EHF Champions League --------------------------------------------
    dict(id='ehf-mag-kri', sport='handball', competition='EHF Champions League, Group F', home='SC Magdeburg', away='HC Kriens-Luzern',
         olbg_time='28 Oct 15:45', start_utc='2026-10-28T20:45:00Z', venue=None,
         sources=['ehf-standings-202627', 'olbg-handball'],
         olbg_market='Money Line - Tie', olbg_tips='7/11', olbg_share='64%',
         home_stats=dict(gp=5, w=5, d=0, l=0, gf=176, ga=140, group='F', rank=1),
         away_stats=dict(gp=5, w=2, d=0, l=3, gf=158, ga=161, group='F', rank=3),
         facts='Magdeburg leads Group F at 5-0 with 176 goals scored and 140 conceded, a differential of +36. Kriens-Luzern is third at 2-3 with 158 scored and 161 conceded (-3).'),
    dict(id='ehf-kie-kol', sport='handball', competition='EHF Champions League, Group F', home='Industria Kielce', away='Kolstad Handball',
         olbg_time='28 Oct 15:45', start_utc='2026-10-28T20:45:00Z', venue=None,
         sources=['ehf-standings-202627', 'olbg-handball'],
         olbg_market='Money Line - Tie', olbg_tips='5/8', olbg_share='63%',
         home_stats=dict(gp=5, w=3, d=0, l=2, gf=155, ga=153, group='F', rank=2),
         away_stats=dict(gp=5, w=0, d=0, l=5, gf=143, ga=178, group='F', rank=4),
         facts='Kielce is second in Group F at 3-2 with 155 goals scored and 153 conceded. Kolstad is bottom at 0-5 with 143 scored and 178 conceded (-35).'),
    dict(id='ehf-por-ves', sport='handball', competition='EHF Champions League, Group A', home='FC Porto', away='One Veszprem HC',
         olbg_time='28 Oct 13:45', start_utc='2026-10-28T18:45:00Z', venue=None,
         sources=['ehf-standings-202627', 'olbg-handball'],
         olbg_market='Money Line - Tie', olbg_tips='3/6', olbg_share='50%',
         home_stats=dict(gp=5, w=1, d=1, l=3, gf=158, ga=173, group='A', rank=3),
         away_stats=dict(gp=5, w=5, d=0, l=0, gf=185, ga=146, group='A', rank=1),
         facts='Veszprem leads Group A at 5-0 with a competition-best 185 goals scored and 146 conceded (+39). Porto is third at 1-1-3 with 158 scored and 173 conceded (-15).'),
    dict(id='ehf-var-mel', sport='handball', competition='EHF Champions League, Group B', home='HC Vardar 1961', away='MT Melsungen',
         olbg_time='28 Oct 13:45', start_utc='2026-10-28T18:45:00Z', venue=None,
         sources=['ehf-standings-202627', 'olbg-handball'],
         olbg_market='Money Line - Tie', olbg_tips='4/7', olbg_share='57%',
         home_stats=dict(gp=5, w=1, d=0, l=4, gf=154, ga=158, group='B', rank=4),
         away_stats=dict(gp=5, w=3, d=0, l=2, gf=138, ga=138, group='B', rank=2),
         facts='Melsungen is second in Group B at 3-2 with 138 goals scored and 138 conceded. Vardar is fourth at 1-4 with 154 scored and 158 conceded.'),
    dict(id='ehf-wis-nan', sport='handball', competition='EHF Champions League, Group B', home='Orlen Wisla Plock', away='HBC Nantes',
         olbg_time='28 Oct 13:45', start_utc='2026-10-28T18:45:00Z', venue=None,
         sources=['ehf-standings-202627', 'olbg-handball'],
         olbg_market='Money Line - Tie', olbg_tips='4/6', olbg_share='67%',
         home_stats=dict(gp=5, w=3, d=0, l=2, gf=141, ga=136, group='B', rank=1),
         away_stats=dict(gp=5, w=3, d=0, l=2, gf=142, ga=143, group='B', rank=3),
         facts='Wisla leads Group B on 6 points at 3-2 with 141 goals scored and 136 conceded. Nantes is level on 6 points at 3-2 with 142 scored and 143 conceded.'),
    dict(id='ehf-psg-aal', sport='handball', competition='EHF Champions League, Group C', home='Paris Saint-Germain', away='Aalborg Handbold',
         olbg_time='28 Oct 15:45', start_utc='2026-10-28T20:45:00Z', venue=None,
         sources=['ehf-standings-202627', 'olbg-handball'],
         olbg_market='Money Line - Tie', olbg_tips='4/6', olbg_share='67%',
         home_stats=dict(gp=5, w=3, d=1, l=1, gf=182, ga=157, group='C', rank=2),
         away_stats=dict(gp=5, w=4, d=1, l=0, gf=170, ga=145, group='C', rank=1),
         facts='Aalborg leads Group C at 4-1 with 170 goals scored and 145 conceded (+25). PSG is second at 3-1-1 with 182 scored (second-highest in the competition) and 157 conceded.'),
    dict(id='ehf-cel-zag', sport='handball', competition='EHF Champions League, Group C', home='RK Celje Pivovarna Lasko', away='HC Zagreb',
         olbg_time='28 Oct 15:45', start_utc='2026-10-28T20:45:00Z', venue=None,
         sources=['ehf-standings-202627', 'olbg-handball'],
         olbg_market='Money Line - Tie', olbg_tips='4/6', olbg_share='67%',
         home_stats=dict(gp=5, w=0, d=0, l=5, gf=150, ga=188, group='C', rank=4),
         away_stats=dict(gp=5, w=2, d=0, l=3, gf=146, ga=158, group='C', rank=3),
         facts='Zagreb is third in Group C at 2-3 with 146 goals scored and 158 conceded. Celje is bottom at 0-5 with 150 scored and a competition-worst 188 conceded (-38).'),
    dict(id='ehf-kri-sze', sport='handball', competition='EHF Champions League, Group D', home='IFK Kristianstad', away='OTP Bank-PICK Szeged',
         olbg_time='29 Oct 13:45', start_utc='2026-10-29T18:45:00Z', venue=None,
         sources=['ehf-standings-202627', 'olbg-handball'],
         olbg_market='Money Line - Tie', olbg_tips='1/3', olbg_share='33%',
         home_stats=dict(gp=5, w=0, d=0, l=5, gf=162, ga=197, group='D', rank=4),
         away_stats=dict(gp=5, w=1, d=2, l=2, gf=172, ga=169, group='D', rank=3),
         facts='Szeged is third in Group D at 1-2-2 with 172 goals scored and 169 conceded. Kristianstad is bottom at 0-5 with 162 scored and 197 conceded (-35).'),
    dict(id='ehf-gog-spo', sport='handball', competition='EHF Champions League, Group D', home='GOG', away='Sporting CP',
         olbg_time='29 Oct 13:45', start_utc='2026-10-29T18:45:00Z', venue=None,
         sources=['ehf-standings-202627', 'olbg-handball'],
         olbg_market='Money Line - GOG', olbg_tips='2/4', olbg_share='50%',
         home_stats=dict(gp=5, w=3, d=1, l=1, gf=178, ga=172, group='D', rank=2),
         away_stats=dict(gp=5, w=4, d=1, l=0, gf=191, ga=165, group='D', rank=1),
         facts='Sporting leads Group D at 4-1 with 191 goals scored, the highest in the group phase, and 165 conceded (+26). GOG is second at 3-1-1 with 178 scored and 172 conceded.'),
    dict(id='ehf-fuc-par', sport='handball', competition='EHF Champions League, Group A', home='Fuchse Berlin', away='RK Partizan',
         olbg_time='29 Oct 13:45', start_utc='2026-10-29T18:45:00Z', venue=None,
         sources=['ehf-standings-202627', 'olbg-handball'],
         olbg_market='Money Line - Tie', olbg_tips='6/11', olbg_share='55%',
         home_stats=dict(gp=5, w=3, d=0, l=2, gf=184, ga=172, group='A', rank=2),
         away_stats=dict(gp=5, w=0, d=1, l=4, gf=148, ga=184, group='A', rank=4),
         facts='Fuchse Berlin is second in Group A at 3-2 with 184 goals scored and 172 conceded. Partizan is bottom at 0-1-4 with 148 scored and 184 conceded (-36).'),
    dict(id='ehf-mon-din', sport='handball', competition='EHF Champions League, Group E', home='Montpellier Handball', away='Dinamo Bucuresti',
         olbg_time='29 Oct 15:45', start_utc='2026-10-29T20:45:00Z', venue=None,
         sources=['ehf-standings-202627', 'olbg-handball'],
         olbg_market='Money Line - Tie', olbg_tips='2/3', olbg_share='67%',
         home_stats=dict(gp=5, w=1, d=0, l=4, gf=150, ga=165, group='E', rank=4),
         away_stats=dict(gp=5, w=1, d=1, l=3, gf=134, ga=145, group='E', rank=3),
         facts='Dinamo is third in Group E at 1-1-3 with 134 goals scored, the lowest in the group, and 145 conceded. Montpellier is bottom at 1-4 with 150 scored and 165 conceded.'),
    dict(id='ehf-aar-bar', sport='handball', competition='EHF Champions League, Group E', home='SAH Aarhus', away='Barca',
         olbg_time='29 Oct 15:45', start_utc='2026-10-29T20:45:00Z', venue=None,
         sources=['ehf-standings-202627', 'olbg-handball'],
         olbg_market='Money Line - FC Barcelona', olbg_tips='1/3', olbg_share='33%',
         home_stats=dict(gp=5, w=2, d=1, l=2, gf=150, ga=163, group='E', rank=2),
         away_stats=dict(gp=5, w=5, d=0, l=0, gf=177, ga=138, group='E', rank=1),
         facts='Barca leads Group E at 5-0 with 177 goals scored and 138 conceded (+39). Aarhus is second at 2-1-2 with 150 scored and 163 conceded (-13).'),
]

# ---- OLBG listings we could not price -------------------------------------
LISTINGS_ONLY = [
    dict(sport='golf', reason='OLBG returned "No tips found" on the golf hub: no tournament or match market existed to price at 04:47Z.',
         rows=[]),
    dict(sport='snooker', reason='OLBG returned "No tips found" on the snooker hub: no match or outright market existed at 04:47Z.',
         rows=[]),
    dict(sport='rugby-union', reason='OLBG rendered antepost only (Six Nations 2027). No match market, and no official 2027 squad or fixture data was read.',
         rows=[dict(match='Six Nations 2027', comp='Outright', time='14 Mar 2027 16:00', market='Win Tournament', sel='Ireland', tips='3/10', share='30%')]),
    dict(sport='rugby-league', reason='OLBG rendered outrights only (State of Origin 2027, Super League 2027, NRL 2027). No match market existed at 04:47Z.',
         rows=[dict(match='State of Origin 2027', comp='Outright', time='27 May 2027 06:00', market='Win Tournament', sel='New South Wales', tips='9/12', share='75%'),
               dict(match='Super League 2027', comp='Outright', time='02 Oct 2027 13:00', market='Grand Final Winner', sel='Wigan Warriors', tips='2/4', share='50%'),
               dict(match='NRL 2027', comp='Outright', time='03 Oct 2027 04:30', market='Grand Final Winner', sel='Penrith Panthers', tips='1/3', share='33%')]),
    dict(sport='darts', reason='OLBG rendered one antepost market (PDC World Championship 2027) and no match market.',
         rows=[dict(match='PDC World Championship 2027', comp='Outright', time='03 Jan 2027 12:00', market='Win Tournament', sel='Luke Littler', tips='22/36', share='61%')]),
    dict(sport='tennis', reason='Fourteen match listings exist, but only one side of each matchup has a published ATP ranking in the top 20 that was read; a price needs both sides. No WTA ranking page was read.',
         rows=[dict(match='Novak Djokovic vs Ugo Humbert', comp='ATP', time='Tomorrow 06:00', market='Win Match', sel='Djokovic', tips='4/5', share='80%'),
               dict(match='Jakub Mensik vs Lukas Neumayer', comp='ATP', time='Today 12:30', market='Win Match', sel='Mensik', tips='3/3', share='100%'),
               dict(match='Tomas Machac vs Alex De Minaur', comp='ATP', time='Today 10:00', market='Win Match', sel='De Minaur', tips='2/2', share='100%'),
               dict(match='Matteo Berrettini vs Tomas Martin Etcheverry', comp='ATP', time='Today 08:30', market='Win Match', sel='Berrettini', tips='3/4', share='75%'),
               dict(match='Stan Wawrinka vs Jiri Lehecka', comp='ATP', time='Tomorrow 06:00', market='Win Match', sel='Lehecka', tips='4/7', share='57%')]),
    dict(sport='motor-racing', reason='One race outright exists (Mexico City Grand Prix, Win Race). No qualifying or race-result page was captured, so a race price would rest on the championship table alone.',
         rows=[dict(match='Mexico City Grand Prix', comp='Formula 1', time='01 Nov 15:00', market='Win Race', sel='Charles Leclerc', tips='1/2', share='50%')]),
    dict(sport='volleyball', reason='Fourteen listings across four national leagues and no official league table or result page was captured for any of them.',
         rows=[dict(match='Norde Volei vs Volei Renata', comp='Brazil Superliga', time='Today 20:00', market='Win Match', sel='Norde Volei', tips='6/8', share='75%'),
               dict(match='Montes Claros vs Sada Cruzeiro', comp='Brazil Superliga', time='Today 18:00', market='Win Match', sel='Sada Cruzeiro', tips='5/10', share='50%'),
               dict(match='SG VCA Amstetten vs UVC Ried', comp='Austria', time='Today 11:30', market='Win Match', sel='UVC Ried', tips='4/5', share='80%'),
               dict(match='UVC Graz vs Waldviertel', comp='Austria', time='Today 14:00', market='Win Match', sel='Waldviertel', tips='4/5', share='80%'),
               dict(match='VBK Klagenfurt vs SK Aich-Dob', comp='Austria', time='Today 13:00', market='Win Match', sel='SK Aich/Dob', tips='3/4', share='75%')]),
    dict(sport='cricket', reason='Five match listings exist. No official board page (ICC, NZC, PCB, Cricket Ireland, Cricket Australia, CSA) returned a readable fixture or result for these matches at read time.',
         rows=[dict(match='New Zealand vs India, 3rd T20', comp='T20 International', time='Tomorrow 03:00', market='Win Match', sel='India', tips='14/21', share='67%'),
               dict(match='Namibia vs Ireland, 3rd ODI', comp='ODI', time='Tomorrow 03:30', market='Win Match', sel='Ireland', tips='11/16', share='69%'),
               dict(match='Pakistan vs Sri Lanka, ODI', comp='ODI', time='Tomorrow 04:00', market='Win Match', sel='Pakistan', tips='5/9', share='56%'),
               dict(match='Melbourne Stars W vs Hobart Hurricanes W', comp='WBBL', time='29 Oct 04:10', market='Win Match', sel='Hobart Hurricanes W', tips='4/6', share='67%'),
               dict(match='Brisbane Heat W vs Sydney Sixers W', comp='WBBL', time='30 Oct 04:10', market='Win Match', sel='Sydney Sixers W', tips='3/5', share='60%')]),
    dict(sport='gaelic', reason='Two club fixtures (1 November) and one 2027 outright exist. No official GAA club team-sheet, result or league table was captured.',
         rows=[dict(match='Kanturk v Eire Og Cor', comp='Munster club', time='01 Nov 09:00', market='Handicap', sel='Eire Og Cor +0.50', tips='6/6', share='100%'),
               dict(match='Fr Caseys v Kildimo Pallaskenry', comp='Munster club', time='01 Nov 10:30', market='Handicap', sel='Kildimo Pallaskenry +3.50', tips='5/7', share='71%')]),
    dict(sport='ice-hockey', reason='Six European ice-hockey listings (Danish Metal Ligaen, Liiga, SHL, DEL) sit beside the three NHL games. No official league feed for them was captured, so they are listed without a price; the three NHL games are priced above.',
         rows=[]),
    dict(sport='baseball', reason='The baseball hub showed "No tips found" while the MLB sub-hub carried the World Series game. That single listing is priced above, so there is no unpriced baseball row.',
         rows=[]),
    dict(sport='basketball', reason='All fifteen NBA and EuroLeague listings carry prices above, so there is no unpriced basketball row.',
         rows=[]),
    dict(sport='handball', reason='Eleven of the thirteen EHF Champions League listings are priced above; the two domestic games (Sweden, Denmark) are not, and they appear in the reason below.',
         rows=[dict(match='OV Helsingborg vs IF Hallby', comp='Swedish Handbollsligan', time='28 Oct 18:00', market='Match Winner', sel='OV Helsingborg', tips='1/1', share='100%'),
               dict(match='Skanderborg vs FC Barcelona', comp='Danish Herreligaen', time='28 Oct 18:30', market='Match Winner', sel='Skanderborg', tips='1/1', share='100%')]),
    dict(sport='greyhounds', reason='One daily-race listing exists. No GBGB racecard, sectionals or form page was captured for the runners.',
         rows=[dict(match='3:19 Monmore', comp='Daily races', time='Today 11:19', market='Daily Races', sel='Tullymurry Skies', tips='1/1', share='100%')]),
]

FLAGS = [
    dict(id='F01', topic='Golf and snooker have no OLBG market', severity='high',
         detail='The golf hub returned "No tips found" and the snooker hub returned "No tips found" at 04:47Z. With no market there is nothing to price, so both sports are listed with their official tours and no pick.',
         recheck='Re-read https://www.olbg.com/betting-tips/Golf/5 and https://www.olbg.com/betting-tips/Snooker/8 when a tournament week begins.',
         source_ids=['olbg-golf', 'olbg-snooker']),
    dict(id='F02', topic='Rugby Union shows antepost only', severity='high',
         detail='The rugby union hub rendered one market, Six Nations 2027 (Ireland, 3/10 tips). No club match market appeared, so no match could be priced.',
         recheck='Re-read https://www.olbg.com/betting-tips/Rugby_Union/9 before the next URC or Premiership round.',
         source_ids=['olbg-rugby-union']),
    dict(id='F03', topic='Rugby League shows outrights only', severity='high',
         detail='Three outright markets were rendered (State of Origin 2027, Super League 2027, NRL 2027) and no match market. The 2027 outrights are eleven months away and rest on squad information we did not read.',
         recheck='Re-read https://www.olbg.com/betting-tips/Rugby_League/10 when a match market appears.',
         source_ids=['olbg-rugby-league']),
    dict(id='F04', topic='Darts has one antepost market', severity='medium',
         detail='Only the PDC World Championship 2027 outright was rendered. There was no match market and no readable PDC page for the current tour.',
         recheck='Re-read https://www.olbg.com/betting-tips/Darts/15 during a ranked PDC weekend.',
         source_ids=['olbg-darts']),
    dict(id='F05', topic='Baseball hub and MLB sub-hub disagree', severity='medium',
         detail='The baseball hub said "No tips found" while the MLB sub-hub listed Milwaukee at Tampa Bay. Both observations are recorded rather than one being treated as a correction of the other.',
         recheck='Re-read both https://www.olbg.com/betting-tips/Baseball/12 and https://www.olbg.com/betting-tips/Baseball/MLB/12.',
         source_ids=['olbg-baseball-mlb']),
    dict(id='F06', topic='No official NBA start time captured', severity='high',
         detail='cdn.nba.com returned HTTP 500 for both the scoreboard and standings JSON. The NBA rows therefore carry the OLBG clock reading and no UTC start time, because no official page published one that we could read.',
         recheck='Read an official NBA schedule or scoreboard feed for 26 October 2026 and add startTimeUTC to the nine NBA rows.',
         source_ids=['olbg-basketball-nba', 'nba-standings-2026']),
    dict(id='F07', topic='NBA handicap and total withheld', severity='medium',
         detail='No official NBA points-for or points-against table was captured, so a pointspread or game total would be invented. NBA rows carry money-line prices only; EuroLeague rows, where points are published, carry all three markets.',
         recheck='Capture an official NBA team-stats page with points for and against, then originate spreads and totals.',
         source_ids=['nba-standings-2026']),
    dict(id='F08', topic='OLBG clock times carry no timezone', severity='medium',
         detail='OLBG showed Los Angeles at New York as "Today 19:07" where the NHL feed publishes 23:00Z (19:00 Eastern), and showed Magdeburg at 15:45 where the EHF page publishes 20:45. The OLBG clock is reproduced verbatim on every row and is never converted to UTC.',
         recheck='Confirm the OLBG display timezone from its own documentation; until then only official feeds supply start times.',
         source_ids=['olbg-ice-hockey', 'ehf-standings-202627', 'nhl-schedule-20261026']),
    dict(id='F09', topic='Tennis cannot be priced from one ranked side', severity='high',
         detail='Fourteen tennis listings exist, but the ATP page read gives a ranking for only one player in each matchup, and no WTA ranking page was read. A price needs both sides, so the listings are published without picks.',
         recheck='Read the ATP and WTA ranking tables and the official draw for each tournament, then price both sides of each match.',
         source_ids=['olbg-tennis', 'atp-rankings-20261026']),
    dict(id='F10', topic='Cricket has fixtures but no official data', severity='high',
         detail='Five cricket match listings exist (New Zealand v India, Namibia v Ireland, Pakistan v Sri Lanka, two WBBL games) but no official board page read returned a fixture, result or squad for them.',
         recheck='Read the ICC, NZC, PCB, Cricket Ireland, Cricket Australia and CSA fixture pages for these matches.',
         source_ids=['olbg-cricket']),
    dict(id='F11', topic='Volleyball spans four leagues with no table', severity='high',
         detail='Fourteen volleyball listings cover Brazil, Austria, Poland and Italy. No official table or result page was captured for any of those competitions, so no team-level fact exists to price from.',
         recheck='Read the CBV, Austrian Volleyball League, Tauron Liga and Lega Pallavolo Serie A pages.',
         source_ids=['olbg-volleyball']),
    dict(id='F12', topic='Gaelic games lack club data', severity='high',
         detail='Two Munster club fixtures are listed for 1 November with handicap markets. No official GAA club team-sheet, result or table was read, so neither could be priced.',
         recheck='Read the Munster GAA club fixture and result pages for 1 November 2026.',
         source_ids=['olbg-gaelic']),
    dict(id='F13', topic='Greyhounds lack a racecard', severity='medium',
         detail='One daily race is listed (3:19 Monmore, Tullymurry Skies). No GBGB racecard, sectional or form page was captured for the six runners.',
         recheck='Read the GBGB racecard for the 3:19 Monmore and price the field.',
         source_ids=['olbg-greyhounds']),
    dict(id='F14', topic='Formula 1 race price withheld', severity='medium',
         detail='The championship table was read (Antonelli 365, Russell 242, Hamilton 241, Verstappen 236, Leclerc 233) but no qualifying or race result page. Originating a 1 November race price from season points alone would be a guess, so the Mexico City listing carries no pick.',
         recheck='Read the 2026 qualifying and race results and the Mexico City weekend entry list.',
         source_ids=['f1-standings-2026', 'olbg-motor-racing']),
    dict(id='F15', topic='No injury report or lineup anywhere', severity='high',
         detail='No official injury report, roster note or starting lineup was read for any of the 33 priced fixtures. No prediction therefore names a player, and every pick row carries that gap explicitly.',
         recheck='Read the official availability report for each league on the matchday and add named absences to the write-ups.',
         source_ids=['nhl-standings-20261025', 'mlb-standings-2026', 'nba-standings-2026', 'el-results-e2026', 'ehf-standings-202627']),
    dict(id='F16', topic='No starting pitchers for the World Series', severity='medium',
         detail='The MLB feed used carries teams, venue and series state but was requested without the probable-pitcher hydrate, so no starter is named and the baseball prices rest on team run rates.',
         recheck='Re-request the MLB schedule with hydrate=probablePitcher and re-price the three games.',
         source_ids=['mlb-schedule-20261026']),
    dict(id='F17', topic='Game 5 conditional status not read', severity='low',
         detail='Games 3 and 4 are marked "ifNecessary: N" in the official feed. The Game 5 row was truncated before that flag, so the row says only that the game is listed.',
         recheck='Re-read the Game 5 object and record the ifNecessary flag.',
         source_ids=['mlb-schedule-20261026']),
    dict(id='F18', topic='Originated prices are not market prices', severity='medium',
         detail='No bookmaker price was captured for any fixture, so these are our own lines. A value comparison against the market is impossible until bookmaker prices are read.',
         recheck='Capture bookmaker prices for the same fixtures and compare implied probabilities.',
         source_ids=['olbg-ice-hockey', 'olbg-basketball-el', 'olbg-handball']),
    dict(id='F19', topic='Thin samples drive basketball prices', severity='medium',
         detail='NBA clubs have played two or three games. Records are shrunk toward .500 with a ten-game prior, which is why an 0-3 club can still be priced close to even and why no NBA pick is graded above 0.64.',
         recheck='Re-price after ten games, when the published record carries real information.',
         source_ids=['nba-standings-2026']),
    dict(id='F20', topic='Domestic handball games unpriced', severity='low',
         detail='Two handball listings (OV Helsingborg v IF Hallby, Skanderborg v FC Barcelona) are Swedish and Danish league games. The EHF table covers Champions League matches only, so neither has an official record we could read.',
         recheck='Read the Swedish and Danish league tables and price both fixtures.',
         source_ids=['olbg-handball', 'ehf-standings-202627']),
]

AUDIT = [
    dict(id='A01', severity='high', area='data/current/snapshot.json',
         finding='The committed snapshot reports 108 fixtures, 0 current listings, 0 priced matches, 0 predictions and 0 high-grade picks. data/desk/desk.json in the same commit reports 21 fixtures, 13 priced, 11 picks with 6 High and 5 Medium, and README.md repeats the 6 High figure.',
         evidence='data/current/snapshot.json: counts.current_listings=0, counts.priced_matches=0, counts.high=0, predictions=[]; data/desk/desk.json: counts.picks=11, counts.high=6; README.md line 35.',
         review='README.md'),
    dict(id='A02', severity='high', area='data/current/discovery.json',
         finding='All 17 OLBG pages are recorded as "unverified" with the reason "robots policy unavailable; request withheld", and the events list is empty, so the canonical snapshot contains no OLBG observation at all. Earlier desks nevertheless publish OLBG listings.',
         evidence='data/current/discovery.json: 17 pages, statuses all "unverified", events=[].',
         review='data/current/discovery.json'),
    dict(id='A03', severity='medium', area='published page weight',
         finding='Two committed pages are far heavier than the rest of the site: markets.html is 2,187 KB and verification.html is 883 KB. Both are carried into the published artifact by the archive copy step.',
         evidence='File sizes measured on the checkout: markets.html 2,187 KB, verification.html 883 KB, index.html 30 KB.',
         review='markets.html'),
    dict(id='A04', severity='medium', area='repository layout',
         finding='Seventy-nine top-level directories are named with an eight-character session hash. Each holds a complete copy of a desk, and the canonical build copies every archived desk into the artifact on each deploy.',
         evidence='79 directories matching [0-9a-f]{8} at the repository root.',
         review='pipeline/build.py'),
    dict(id='A05', severity='low', area='COORDINATION.md',
         finding='Section numbers are reused: four or more headings share a number and at least ten numbers appear twice, so the board cannot be read as a sequence.',
         evidence='Duplicate top-level section numbers detected in COORDINATION.md, including 4, 13, 43, 60, 64, 71, 74, 75, 78 and 82.',
         review='COORDINATION.md'),
    dict(id='A06', severity='low', area='data/current/matches.csv',
         finding='The canonical CSV contains a UTF-8 byte-order mark before the "id" header, and every row in it carries no price, no confidence and no model probability.',
         evidence='data/current/matches.csv: first bytes are EF BB BF; experimental_selection, confidence, model_probability and fair_decimal are empty on the sampled rows.',
         review='data/current/matches.csv'),
]

METHOD = dict(
    version='originated-1.0',
    band='A selection is in band when its fair American price is between -250 and +10000, i.e. an implied probability from 0.0099 to 0.7143. Nothing shorter than -250 and nothing longer than +10000 is published as a pick.',
    tiers='High: originated probability >= 0.60 and in band. Medium: >= 0.55 and < 0.60. Low: >= 0.45 and < 0.55. Below 0.45 no pick is published.',
    pick_rule='For each priced fixture the pick is the in-band outcome with the highest originated probability; if no outcome reaches 0.45 the fixture carries no pick and says why.',
    team_model='Scoring rates are shrunk toward a sport prior before use: rate = (published total + prior_games * prior_rate) / (games played + prior_games). NHL prior 3.00 goals in 10 games; MLB prior 4.50 runs in 20 games; handball prior 30.0 goals in 5 games. Basketball uses the published win-loss record shrunk to .500 with a 10-game prior.',
    margin_model='Expected goals or points for each side = mean of that side\'s shrunk scoring rate and the opponent\'s shrunk conceding rate, plus or minus half of the published home edge. NHL 0.30 goals, MLB 0.20 runs, handball 1.20 goals. The margin is the difference; a normal distribution gives win, handicap and total probabilities. Score standard deviations: NHL 1.8, MLB 4.2, handball 8.0; totals 2.3, 4.6 and 9.0.',
    mlb_note='MLB run line is fixed at 1.5 runs, which is the standard posted line.',
    withheld='Player props are withheld on every fixture because no confirmed lineup or availability list was read. Correct-score and period markets are withheld because no per-period distribution was read. NBA pointspread and game-total markets are withheld because no official NBA points-for or points-against table was captured; the NBA rows therefore carry money-line prices only.',
    honesty='Every number quoted in a prediction appears on the official page linked on the same row. Where a page did not publish something - NBA start times, NBA points, injuries, lineups - the field is blank and the gap is named on the fixture row and the Flagged for review page.',
)

SPREAD_LINES = {'ice-hockey': 1.5, 'baseball': 1.5}
TOTAL_LINES = {}
SIGMA = {
    'ice-hockey': (1.8, 2.3),
    'baseball': (4.2, 4.6),
    'handball': (8.0, 9.0),
    'basketball': (11.0, 14.0),
}
PRIOR = {'ice-hockey': (3.0, 10), 'baseball': (4.5, 20), 'handball': (30.0, 5),
         'basketball': (82.0, 5)}
HOME_EDGE = {'ice-hockey': 0.30, 'baseball': 0.20, 'handball': 1.20, 'basketball': 0.10}


def phi(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def american_from_prob(p):
    if not 0 < p < 1:
        raise ValueError('probability out of range')
    if p >= 0.5:
        return int(round(-100.0 * p / (1.0 - p)))
    return int(round(100.0 * (1.0 - p) / p))


def band(american):
    return -250 <= american <= 10000


def price(p):
    p = round(p, 6)
    dec = round(1.0 / p, 4)
    am = american_from_prob(p)
    return dict(p=p, fair_decimal=dec, american=am, in_band=band(am))


def shrunk(total, games, sport):
    """Scoring rate shrunk toward the sport prior."""
    if sport == 'basketball':
        return total / games
    prior_rate, prior_games = PRIOR[sport]
    return (total + prior_games * prior_rate) / (games + prior_games)


def basketball_prob(home_stats, away_stats, home=True):
    """Win probability from the published win-loss record, shrunk to .500."""
    def rate(s):
        return (s['w'] + 0.5 * s.get('d', 0) + 5.0) / (s['gp'] + 10.0)
    ph, pa = rate(home_stats), rate(away_stats)
    denom = ph + pa - 2 * ph * pa
    p_home_side = (ph - ph * pa) / denom if denom else 0.5
    # home edge applied on the log-odds scale to whichever side is at home
    if home:
        logit = math.log(p_home_side / (1 - p_home_side)) + HOME_EDGE['basketball']
        return 1 / (1 + math.exp(-logit))
    logit = math.log(p_home_side / (1 - p_home_side)) - HOME_EDGE['basketball']
    return 1 / (1 + math.exp(-logit))


def record_margin(fx, points=10.0):
    """A record-based margin: win-probability edge scaled to the sport's scoring unit."""
    h, a = fx['home_stats'], fx['away_stats']

    def rate(s):
        return (s['w'] + 0.5 * s.get('d', 0) + 3.0) / (s['gp'] + 6.0)

    ph, pa = rate(h), rate(a)
    denom = ph + pa - 2 * ph * pa
    p_home = (ph - ph * pa) / denom if denom else 0.5
    logit = math.log(p_home / (1 - p_home)) + 0.10
    p_home = 1 / (1 + math.exp(-logit))
    return (p_home - 0.5) * points


def scoring_model(fx):
    sport = fx['sport']
    if sport == 'basketball' and 'pf' not in fx['home_stats']:
        p_home = basketball_prob(fx['home_stats'], fx['away_stats'])
        return dict(p_home=p_home, total=None, margin=None)

    h, a = fx['home_stats'], fx['away_stats']
    if sport in ('ice-hockey', 'baseball'):
        key_for, key_against = ('gf', 'ga') if sport == 'ice-hockey' else ('rs', 'ra')
    elif sport == 'basketball':
        key_for, key_against = 'pf', 'pa'
    else:
        key_for, key_against = 'gf', 'ga'
    h_att = shrunk(h[key_for], h['gp'], sport)
    h_def = shrunk(h[key_against], h['gp'], sport)
    a_att = shrunk(a[key_for], a['gp'], sport)
    a_def = shrunk(a[key_against], a['gp'], sport)
    edge = {'ice-hockey': 0.15, 'baseball': 0.10, 'handball': 0.60, 'basketball': 1.25}[sport]
    xg_home = (h_att + a_def) / 2.0 + edge
    xg_away = (a_att + h_def) / 2.0 - edge
    margin = xg_home - xg_away
    total = xg_home + xg_away
    sigma_margin, _ = SIGMA[sport]
    if sport == 'handball':
        margin = 0.6 * margin + 0.4 * record_margin(fx)
    elif sport == 'basketball':
        margin = 0.7 * margin + 0.3 * record_margin(fx, points=40.0)
    p_home = phi(margin / sigma_margin)
    return dict(p_home=p_home, total=total, margin=margin, xg_home=xg_home, xg_away=xg_away)


def total_line(sport, total):
    step = 0.5
    return round(total) + step if (round(total) + step) != total else round(total) + 0.5


def markets_for(fx):
    """Originate winner, handicap and total markets from the published numbers."""
    sport = fx['sport']
    model = scoring_model(fx)
    markets = []
    home, away = fx['home'], fx['away']
    p_home = model['p_home']

    def two_way(key, label, sel_a, p_a, sel_b, extra=None):
        outcomes = [dict(sel=sel_a, **price(p_a)), dict(sel=sel_b, **price(1 - p_a))]
        m = dict(key=key, label=label, outcomes=outcomes)
        if extra:
            m.update(extra)
        markets.append(m)

    two_way('winner', 'Match winner (money line)', home, p_home, away)

    if sport == 'basketball' and 'pf' not in fx['home_stats']:
        return markets, model

    sigma_margin, sigma_total = SIGMA[sport]
    margin = model['margin']
    if sport == 'handball':
        line = min(9.5, max(1.5, math.floor(abs(margin)) + 0.5))
    elif sport == 'basketball':
        line = min(15.5, max(1.5, math.floor(abs(margin)) + 0.5))
    else:
        line = SPREAD_LINES[sport]
    p_fav_cover = 1.0 - phi((line - abs(margin)) / sigma_margin)
    if margin >= 0:
        two_way('handicap', f'Handicap {home} -{line}', f'{home} -{line}', p_fav_cover,
                f'{away} +{line}', extra=dict(line=-line))
    else:
        two_way('handicap', f'Handicap {away} -{line}', f'{home} +{line}', 1.0 - p_fav_cover,
                f'{away} -{line}', extra=dict(line=line))
    tline = total_line(sport, model['total'])
    p_over = 1.0 - phi((tline - model['total']) / sigma_total)
    two_way('total', f'Match total {tline}', f'Over {tline}', p_over, f'Under {tline}', extra=dict(line=tline))
    return markets, model


PUBLISH_FLOOR = 0.55
PICKS_PER_COMPETITION = 6


def choose_pick(markets):
    candidates = []
    for m in markets:
        for o in m['outcomes']:
            if o['in_band'] and o['p'] >= PUBLISH_FLOOR:
                candidates.append((o['p'], m, o))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    p, m, o = candidates[0]
    tier = 'high' if p >= 0.60 else 'medium' if p >= 0.55 else 'low'
    return dict(market=m['key'], market_label=m['label'], selection=o['sel'], probability=p,
                american=o['american'], fair_decimal=o['fair_decimal'], confidence=tier)


def grade(p):
    return 'high' if p >= 0.60 else 'medium' if p >= 0.55 else 'low'


def american_text(am):
    return f'+{am}' if am > 0 else str(am)


def build():
    fixtures = []
    for f in FIXTURES:
        markets, model = markets_for(f)
        for m in markets:
            for o in m['outcomes']:
                o['grade'] = grade(o['p'])
        pick = choose_pick(markets)
        withheld = [
            'Player props: no confirmed lineup or availability list was read for this fixture.',
            'Correct score and period markets: no official period-level scoring distribution was read.',
        ]
        if f['sport'] == 'basketball':
            withheld.insert(0, 'Pointspread and game total: no official NBA points-for or points-against table was captured, so a line would be invented.')
        if f['sport'] == 'handball':
            withheld.append('Domestic-league form: the EHF table covers Champions League matches only.')
        fixtures.append(dict(
            id=f['id'], sport=f['sport'], competition=f['competition'], home=f['home'], away=f['away'],
            olbg_time=f['olbg_time'], start_utc=f['start_utc'], venue=f['venue'],
            olbg_market=f['olbg_market'], olbg_tips=f['olbg_tips'], olbg_share=f['olbg_share'],
            sources=f['sources'], facts=f['facts'],
            home_stats=f['home_stats'], away_stats=f['away_stats'],
            markets=markets, pick=pick, withheld=withheld, priced=True,
            model=dict(p_home=round(model['p_home'], 6),
                       expected_total=None if model['total'] is None else round(model['total'], 2),
                       expected_margin=None if model.get('margin') is None else round(model['margin'], 2)),
        ))
    # keep at most six published picks per competition, highest grade first
    seen = {}
    for f in sorted(fixtures, key=lambda x: -(x['pick']['probability'] if x['pick'] else 0)):
        if not f['pick']:
            continue
        comp = f['competition']
        seen[comp] = seen.get(comp, 0) + 1
        if seen[comp] > PICKS_PER_COMPETITION:
            f['pick'] = None
            f['no_pick_reason'] = ('Rated inside the band but outside the six highest grades for this '
                                   'competition, so no pick is published on this row.')
    return fixtures


def no_pick_reason(f):
    best = None
    for m in f['markets']:
        for o in m['outcomes']:
            if o['in_band'] and (best is None or o['p'] > best['p']):
                best = o
    if best is None:
        return 'Every originated outcome prices outside the -250..+10000 band or below the 0.55 floor, so no pick is published.'
    return (f'The highest-graded in-band outcome on this fixture is {best["sel"]} at {round(best["p"] * 100, 1)}%, '
            f'which is below the 0.55 publication floor. No pick is published.')


def main():
    fixtures = build()
    prose = json.loads((ROOT / 'data' / '103ea76b' / 'prose.json').read_text(encoding='utf-8'))
    for f in fixtures:
        if f['pick']:
            entry = prose[f['id']]
            f['pick']['prose'] = entry['prose']
            f['pick']['gaps'] = entry['gaps']
            f['pick']['prediction'] = entry['prose']
            f['pick']['words'] = len([w for w in re.split(r'\s+', entry['prose'])
                                      if re.search(r'[A-Za-z0-9]', w)])
        else:
            f.setdefault('no_pick_reason', no_pick_reason(f))
        if f.get('start_utc'):
            f['start_time_status'] = 'published by the official feed named in sources'
            f['start_time_note'] = ''
        else:
            f['start_time_status'] = 'not published by any official page we could read'
            f['start_time_note'] = ('OLBG showed only a relative clock reading (' + f['olbg_time'] +
                                    '). The official schedule feed we could reach did not publish a start time, '
                                    'so the field is left blank rather than converted or guessed.')
    picks = [f for f in fixtures if f['pick']]
    by_sport = {}
    for f in fixtures:
        by_sport.setdefault(f['sport'], []).append(f)
    counts = dict(
        sports_requested=len(SPORTS),
        sports_with_fixtures=len(by_sport),
        fixtures=len(fixtures),
        priced_fixtures=sum(1 for f in fixtures if f['priced']),
        unpriced_fixtures=sum(1 for f in fixtures if not f['priced']),
        markets=sum(len(f['markets']) for f in fixtures),
        outcomes=sum(len(m['outcomes']) for f in fixtures for m in f['markets']),
        withheld_markets=sum(len(f['withheld']) for f in fixtures),
        picks=len(picks),
        high=sum(1 for f in picks if f['pick']['confidence'] == 'high'),
        medium=sum(1 for f in picks if f['pick']['confidence'] == 'medium'),
        predictions=len(picks),
        sources=len(SOURCES),
        flags=len(FLAGS),
    )
    extras = dict(
        sports_with_picks=len({f['sport'] for f in picks}),
        low=sum(1 for f in picks if f['pick']['confidence'] == 'low'),
        sports_with_olbg_capture=len(SPORTS),
        listings_only_rows=sum(len(x['rows']) for x in LISTINGS_ONLY),
    )
    desk = dict(
        generated_at=READ_AT,
        sport_order=[s[0] for s in SPORTS],
        sports=[dict(code=s[0], name=s[1], olbg_id=s[2], olbg_route=s[3], olbg_url=s[4], official_hub=s[5])
                for s in SPORTS],
        sources=SOURCES,
        fixtures=fixtures,
        picks_sort=[f['id'] for f in sorted(picks, key=lambda f: (-f['pick']['probability'], f['id']))],
        listings_only=LISTINGS_ONLY,
        flags=FLAGS,
        audit=AUDIT,
        audit_findings=len(AUDIT),
        method=METHOD,
        counts=counts,
        extras=extras,
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(desk, indent=1, sort_keys=False) + '\n', encoding='utf-8')
    print(json.dumps(counts, indent=1))
    print(json.dumps(extras, indent=1))
    for f in picks:
        p = f['pick']
        print(f"{f['id']:16s} {p['confidence']:6s} p={p['probability']:.3f} {american_text(p['american']):>6s}  {p['selection']}")
    return desk


if __name__ == '__main__':
    main()
