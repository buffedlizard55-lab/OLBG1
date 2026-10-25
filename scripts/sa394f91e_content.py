"""Fixtures, originated markets, graded picks and written analysis.

Only fields an official publisher printed this session appear here. Fields that
were not published are None and are rendered as a blank with a reason.
"""
from __future__ import annotations

import sa394f91e_model as M

# --------------------------------------------------------------------------
# Official fixtures. Every row names the official source id it was read from.
# --------------------------------------------------------------------------
NHL = [
    dict(key='nhl-2026020180', sport='ice-hockey', competition='NHL',
         away='FLA', home='CHI', away_name='Florida Panthers', home_name='Chicago Blackhawks',
         venue='United Center', start_utc='2026-10-25T19:00:00Z', neutral=False,
         source='nhl-schedule-1025', source_url='https://api-web.nhle.com/v1/schedule/2026-10-25',
         game_link='https://www.nhl.com/gamecenter/fla-vs-chi/2026/10/25/2026020180'),
    dict(key='nhl-2026020181', sport='ice-hockey', competition='NHL',
         away='NYI', home='DAL', away_name='New York Islanders', home_name='Dallas Stars',
         venue='American Airlines Center', start_utc='2026-10-25T22:00:00Z', neutral=False,
         source='nhl-schedule-1025', source_url='https://api-web.nhle.com/v1/schedule/2026-10-25',
         game_link='https://www.nhl.com/gamecenter/nyi-vs-dal/2026/10/25/2026020181'),
    dict(key='nhl-2026020182', sport='ice-hockey', competition='NHL',
         away='MTL', home='WPG', away_name='Montréal Canadiens', home_name='Winnipeg Jets',
         venue='Princess Auto Stadium', start_utc='2026-10-25T23:00:00Z', neutral=True,
         designation='2026 Tim Hortons NHL Heritage Classic',
         source='nhl-schedule-1025', source_url='https://api-web.nhle.com/v1/schedule/2026-10-25',
         game_link='https://www.nhl.com/gamecenter/mtl-vs-wpg/2026/10/25/2026020182'),
    dict(key='nhl-2026020183', sport='ice-hockey', competition='NHL',
         away='COL', home='NSH', away_name='Colorado Avalanche', home_name='Nashville Predators',
         venue='Bridgestone Arena', start_utc='2026-10-26T00:00:00Z', neutral=False,
         source='nhl-schedule-1025', source_url='https://api-web.nhle.com/v1/schedule/2026-10-25',
         game_link='https://www.nhl.com/gamecenter/col-vs-nsh/2026/10/25/2026020183'),
]

NHL_PARTIAL = dict(
    key='nhl-2026020184', sport='ice-hockey', competition='NHL',
    venue='Rogers Arena', note='Fifth game of the 25 October slate.',
    source='nhl-schedule-1025', source_url='https://api-web.nhle.com/v1/schedule/2026-10-25',
    missing='The response was truncated mid-record during capture, so neither club nor the '
            'start time was read on an official page. OLBG discovery separately lists '
            '"MIN Wild @ VAN Canucks" against a Vancouver home venue, but a discovery listing '
            'is not an official fixture, so the clubs are left blank and no price is issued.')

NBA = [
    dict(key='nba-0022600112', sport='basketball', competition='NBA',
         away='LAL', home='UTA', away_name='Los Angeles Lakers', home_name='Utah Jazz',
         venue='Delta Center', city='Salt Lake City, UT', tip_published='5:00 PM ET',
         start_utc='2026-10-25T21:00:00Z', start_utc_derived=True,
         source='nba-schedule-1025', source_url='https://www.nba.com/schedule?date=10/25/2026',
         game_link='https://www.nba.com/game/lal-vs-uta-0022600112'),
    dict(key='nba-0022600113', sport='basketball', competition='NBA',
         away='IND', home='BKN', away_name='Indiana Pacers', home_name='Brooklyn Nets',
         venue='Barclays Center', city='Brooklyn, NY', tip_published='6:00 PM ET',
         start_utc='2026-10-25T22:00:00Z', start_utc_derived=True,
         source='nba-schedule-1025', source_url='https://www.nba.com/schedule?date=10/25/2026',
         game_link='https://www.nba.com/game/ind-vs-bkn-0022600113'),
    dict(key='nba-0022600114', sport='basketball', competition='NBA',
         away='ORL', home='NYK', away_name='Orlando Magic', home_name='New York Knicks',
         venue='Madison Square Garden', city='New York, NY', tip_published='7:00 PM ET',
         start_utc='2026-10-25T23:00:00Z', start_utc_derived=True,
         source='nba-schedule-1025', source_url='https://www.nba.com/schedule?date=10/25/2026',
         game_link='https://www.nba.com/game/orl-vs-nyk-0022600114'),
    dict(key='nba-0022600115', sport='basketball', competition='NBA',
         away='TOR', home='MIN', away_name='Toronto Raptors', home_name='Minnesota Timberwolves',
         venue='Target Center', city='Minneapolis, MN', tip_published='7:00 PM ET',
         start_utc='2026-10-25T23:00:00Z', start_utc_derived=True,
         source='nba-schedule-1025', source_url='https://www.nba.com/schedule?date=10/25/2026',
         game_link='https://www.nba.com/game/tor-vs-min-0022600115'),
    dict(key='nba-0022600116', sport='basketball', competition='NBA',
         away='LAC', home='OKC', away_name='LA Clippers', home_name='Oklahoma City Thunder',
         venue='Paycom Center', city='Oklahoma City, OK', tip_published='7:00 PM ET',
         start_utc='2026-10-25T23:00:00Z', start_utc_derived=True,
         source='nba-schedule-1025', source_url='https://www.nba.com/schedule?date=10/25/2026',
         game_link='https://www.nba.com/game/lac-vs-okc-0022600116'),
]

MLB = [
    dict(key='mlb-849804', sport='baseball', competition='MLB World Series, Game 3',
         away='MIL', home='TB', away_name='Milwaukee Brewers', home_name='Tampa Bay Rays',
         venue='Tropicana Field', start_utc='2026-10-27T00:00:00Z',
         official_date='2026-10-26',
         source='mlb-schedule-window',
         source_url='https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-25&endDate=2026-11-08',
         series_note='Series standing after game 1, as published: Brewers 1-0, Rays 0-1. '
                     'These are series figures from the official schedule feed, not season records.'),
]

# Official league records, read from the sources above.
NHL_RECORDS = {
    'FLA': dict(gp=11, w=5, l=4, ot=2, pts=12, gf=31, ga=34, home='2-1-0', road='3-3-2', l10='4-4-2', strk='L2'),
    'CHI': dict(gp=10, w=3, l=7, ot=0, pts=6, gf=22, ga=40, home='3-3-0', road='0-4-0', l10='3-7-0', strk='L2'),
    'NYI': dict(gp=10, w=5, l=3, ot=2, pts=12, gf=29, ga=23, home='4-1-1', road='1-2-1', l10='5-3-2', strk='OT1'),
    'DAL': dict(gp=10, w=6, l=3, ot=1, pts=13, gf=26, ga=17, home='3-2-0', road='3-1-1', l10='6-3-1', strk='W4'),
    'MTL': dict(gp=10, w=5, l=3, ot=2, pts=12, gf=34, ga=35, home='3-2-1', road='2-1-1', l10='5-3-2', strk='W1'),
    'WPG': dict(gp=10, w=4, l=3, ot=3, pts=11, gf=26, ga=29, home='2-2-1', road='2-1-2', l10='4-3-3', strk='OT1'),
    'COL': dict(gp=11, w=6, l=4, ot=1, pts=13, gf=47, ga=34, home='4-1-1', road='2-3-0', l10='5-4-1', strk='W1'),
    'NSH': dict(gp=10, w=3, l=3, ot=4, pts=10, gf=25, ga=33, home='2-2-1', road='1-1-3', l10='3-3-4', strk='OT1'),
}
NBA_RECORDS = {
    'LAL': dict(w=2, l=0, home='2-0', road='0-0', l10='2-0', strk='W2'),
    'UTA': dict(w=1, l=1, home='1-0', road='0-1', l10='1-1', strk='W1'),
    'IND': dict(w=1, l=1, home='0-1', road='1-0', l10='1-1', strk='L1'),
    'BKN': dict(w=0, l=2, home='0-1', road='0-1', l10='0-2', strk='L2'),
    'ORL': dict(w=0, l=2, home='0-2', road='0-0', l10='0-2', strk='L2'),
    'NYK': dict(w=0, l=2, home='0-1', road='0-1', l10='0-2', strk='L2'),
    'TOR': dict(w=2, l=0, home='1-0', road='1-0', l10='2-0', strk='W2'),
    'MIN': dict(w=2, l=0, home='0-0', road='2-0', l10='2-0', strk='W2'),
    'LAC': dict(w=1, l=1, home='1-0', road='0-1', l10='1-1', strk='L1'),
    'OKC': dict(w=2, l=0, home='1-0', road='1-0', l10='2-0', strk='W2'),
}

# --------------------------------------------------------------------------
# Picks. A pick is issued only on the money line, only when the originated
# probability clears 0.55 and its fair price sits inside -250..+10000.
# --------------------------------------------------------------------------
PICKS = [
    dict(fixture='nhl-2026020180', selection='Florida Panthers to win (money line)',
         team='FLA', p=0.6167),
    dict(fixture='nhl-2026020183', selection='Colorado Avalanche to win (money line)',
         team='COL', p=0.6770),
    dict(fixture='nhl-2026020181', selection='Dallas Stars to win (money line)',
         team='DAL', p=0.5730),
]

PREDICTIONS = {
'nhl-2026020180': (
 "Back the Florida Panthers on the money line when they visit the Chicago Blackhawks at the "
 "United Center. Florida are 5-4-2 for 12 points, with 31 goals scored and 34 conceded in 11 "
 "games, and they are 3-3-2 on the road with a last-ten line of 4-4-2. Chicago are 3-7-0 on six "
 "points, have scored only 22 goals in ten games and have conceded 40, a total bettered only by "
 "Vancouver and San Jose in the published table. The Blackhawks are 0-4-0 away and have lost "
 "their last two, so the road side is the selection."),
'nhl-2026020183': (
 "The selection is the Colorado Avalanche to win at the Nashville Predators. Colorado are 6-4-1 "
 "for 13 points and have scored 47 goals in 11 games, an average of 4.27 per game that is "
 "matched by Vegas and bettered only by Edmonton's 49 in the Western Conference, while conceding 34. Nashville are 3-3-4 "
 "on 10 points with 25 scored and 33 conceded, and four of their ten games have finished as "
 "overtime or shootout defeats. The Predators are 2-2-1 at home and carry a last-ten line of "
 "3-3-4 into the game."),
'nhl-2026020181': (
 "Dallas Stars to beat the New York Islanders at the American Airlines Center. Dallas are 6-3-1 "
 "for 13 points and have conceded only 17 goals in ten games, the lowest goals-against figure "
 "anywhere in the published league table, while scoring 26. They have won four straight and are "
 "3-2-0 at home. The Islanders arrive at 5-3-2 on 12 points with 29 scored and 23 conceded, a "
 "1-2-1 road record and an overtime defeat in their most recent game."),
}
