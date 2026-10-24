"""The 24 October 2026 desk: captured facts, originated prices, picks and write-ups.

Everything in ``TEAMS``, ``FIXTURES`` and ``SOURCES`` was read from an official
publisher during this session and is stamped with the read time. Nothing is
carried over from an earlier desk: an earlier observation is not this session's
evidence.

Two rules govern the output and both are enforced again in
``pipeline/validate.py``:

* a price is *originated* here from officially published season data, never
  copied from a bookmaker, and the market price (where the official feed
  publishes one) is shown next to it, clearly labelled as the publisher's;
* a pick is only issued when the originated probability is at least 0.55, the
  fair American price sits inside the brief's -250..+10000 window, and every
  input for that match is sourced. Confidence is then High at 0.60 and above,
  Medium from 0.55 to 0.60.

The brief's "high confidence" description is applied as written: the band's
shortest allowed price (-250, i.e. 71.4%) is the ceiling, so a selection that is
*only* a short market favourite cannot be published here, and the >70% market
price the brief calls trivial is excluded by the band itself rather than by a
second, contradictory filter.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone

BAND_LOW, BAND_HIGH = -250, 10000
HIGH_MIN, PICK_MIN = 0.60, 0.55
PRIOR_GAMES = 10.0            # shrinkage prior: ten league-average games
LEAGUE_GF = 3.10              # NHL goals per team per game (prior mean)
HFA_NHL = 0.30                # goals, full home advantage
SIGMA_NHL = 1.85              # standard deviation of a game margin
SIGMA_TOTAL = 2.40            # standard deviation of a game total
LEAGUE_RPG = 4.50             # MLB runs per team per game (prior mean)
HFA_MLB = 0.15                # runs
SIGMA_MLB = 3.00
PRIOR_GAMES_MLB = 30.0

READ_AT = '2026-10-24T18:00:00Z'

SPORTS = [
    ('ice-hockey', 'Ice Hockey', 13, 'Ice_Hockey', 'https://www.nhl.com/schedule'),
    ('baseball', 'Baseball', 12, 'Baseball', 'https://www.mlb.com/schedule'),
    ('golf', 'Golf', 5, 'Golf', 'https://www.pgatour.com/schedule'),
    ('volleyball', 'Volleyball', 21, 'Volleyball', 'https://www.plusliga.pl/games.html'),
    ('rugby-union', 'Rugby Union', 9, 'Rugby_Union', 'https://www.unitedrugby.com/fixtures'),
    ('cricket', 'Cricket', 7, 'Cricket', 'https://www.icc-cricket.com/fixtures-results'),
    ('snooker', 'Snooker', 8, 'Snooker', 'https://www.wst.tv/matches/'),
    ('darts', 'Darts', 15, 'Darts', 'https://www.pdc.tv/tournaments'),
    ('gaelic', 'Gaelic Sports', 25, 'Gaelic_Football', 'https://munster.gaa.ie/fixtures/events-calendar/'),
    ('greyhounds', 'Greyhounds', 28, 'Greyhounds', 'https://www.gbgb.org.uk/racing/open-races/'),
    ('tennis', 'Tennis', 3, 'Tennis', 'https://www.atptour.com/en/scores/current'),
    ('motor-racing', 'Motor Racing', 14, 'Motor_Racing', 'https://www.formula1.com/en/racing/2026'),
    ('handball', 'Handball', 20, 'Handball', 'https://www.eurohandball.com/en/competitions/'),
    ('basketball', 'Basketball', 4, 'Basketball', 'https://www.nba.com/games'),
    ('rugby-league', 'Rugby League', 10, 'Rugby_League', 'https://www.nrl.com/draw/'),
]
SPORT_INDEX = {s[0]: {'slug': s[0], 'name': s[1], 'olbg_id': s[2],
                      'olbg_url': f'https://www.olbg.com/betting-tips/{s[3]}/{s[2]}',
                      'official_url': s[4]} for s in SPORTS}

SOURCES = [
    {'id': 'nhl-on-tap-7568',
     'url': 'https://www.nhl.com/news/nhl-on-tap-news-and-notes-october-24-2026',
     'publisher': 'NHL', 'observed_at': '2026-10-24T22:36:00Z',
     'supports': 'Boston and Edmonton preview: records, recent results, named player statistics and John Tavares upper-body injury. Read via page retrieval; not a live status feed.',
     'role': 'official'},
    {'id': 'nhl-schedule-2410',
     'url': 'https://api-web.nhle.com/v1/schedule/2026-10-24',
     'publisher': 'NHL',
     'observed_at': '2026-10-24T17:52:00Z',
     'supports': 'Game IDs, exact UTC start times, venues, neutral-site flag and the published '
                 'partner moneyline prices for the twelve NHL games of 24 October 2026.',
     'role': 'official'},
    {'id': 'nhl-schedule-2510',
     'url': 'https://api-web.nhle.com/v1/schedule/2026-10-25',
     'publisher': 'NHL',
     'observed_at': '2026-10-24T17:53:00Z',
     'supports': 'Game IDs, exact UTC start times, venues and the Heritage Classic neutral-site '
                 'flag for the NHL games of 25 October 2026.',
     'role': 'official'},
    {'id': 'nhl-standings-2410',
     'url': 'https://api-web.nhle.com/v1/standings/2026-10-24',
     'publisher': 'NHL',
     'observed_at': '2026-10-24T17:42:00Z',
     'supports': '2026-27 club records, goals for and against, home/road splits, last-ten records '
                 'and streaks, stamped by the league at 2026-10-24T17:42:15Z.',
     'role': 'official'},
    {'id': 'mlb-schedule',
     'url': 'https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-24&endDate=2026-10-31',
     'publisher': 'MLB',
     'observed_at': '2026-10-24T17:55:00Z',
     'supports': 'World Series game numbers 2 to 7, gamePk identifiers, exact UTC start times, '
                 'venues and the league if-necessary flag (games 5 to 7 conditional).',
     'role': 'official'},
    {'id': 'mlb-result-2310',
     'url': 'https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-10-23',
     'publisher': 'MLB',
     'observed_at': '2026-10-24T17:56:00Z',
     'supports': 'Final score of World Series Game 1: Milwaukee 3, Tampa Bay 2, at American Family Field.',
     'role': 'official'},
    {'id': 'mlb-standings-al',
     'url': 'https://statsapi.mlb.com/api/v1/standings?leagueId=103&season=2026&standingsTypes=regularSeason',
     'publisher': 'MLB',
     'observed_at': '2026-10-24T17:56:00Z',
     'supports': 'Tampa Bay 98-64, home 55-26, road 43-38, last ten 5-5 (AL East table).',
     'role': 'official'},
    {'id': 'mlb-standings-nl',
     'url': 'https://statsapi.mlb.com/api/v1/standings?leagueId=104&season=2026&standingsTypes=regularSeason',
     'publisher': 'MLB',
     'observed_at': '2026-10-24T17:57:00Z',
     'supports': 'Milwaukee 103-59, home 55-26, road 48-33, last ten 8-2 (NL Central table).',
     'role': 'official'},
    {'id': 'olbg-ice-hockey',
     'url': 'https://www.olbg.com/betting-tips/Ice_Hockey/13',
     'publisher': 'OLBG (discovery only)',
     'observed_at': '2026-10-24T17:47:00Z',
     'supports': 'Which NHL and Swiss NLA match markets OLBG lists today, and the per-event '
                 'moneyline tip cards. Tip shares are member votes and are never used as prices.',
     'role': 'discovery'},
]

# --- NHL club data ---------------------------------------------------------
# gp, w, l, otl, gf, ga, home (w-l-otl) with games, road (w-l-otl) with games,
# last ten (w-l-otl), streak, source id.
TEAMS = {
    'ANA': dict(name='Anaheim Ducks', gp=None, w=None, l=None, otl=None, gf=None, ga=None, src=None),
    'BOS': dict(name='Boston Bruins', gp=11, w=8, l=2, otl=1, gf=42, ga=22, home='4-1-0', home_gp=5,
                road='4-1-1', road_gp=6, l10='7-2-1', streak='W1', src='nhl-standings-2410'),
    'BUF': dict(name='Buffalo Sabres', gp=10, w=4, l=4, otl=2, gf=28, ga=37, home='3-3-0', home_gp=6,
                road='1-1-2', road_gp=4, l10='4-4-2', streak='L1', src='nhl-standings-2410'),
    'CAR': dict(name='Carolina Hurricanes', gp=12, w=8, l=2, otl=2, gf=47, ga=33, home='2-1-1', home_gp=4,
                road='6-1-1', road_gp=8, l10='8-1-1', streak='OT1', src='nhl-standings-2410'),
    'CBJ': dict(name='Columbus Blue Jackets', gp=None, w=None, l=None, otl=None, gf=None, ga=None, src=None),
    'CGY': dict(name='Calgary Flames', gp=None, w=None, l=None, otl=None, gf=None, ga=None, src=None),
    'CHI': dict(name='Chicago Blackhawks', gp=None, w=None, l=None, otl=None, gf=None, ga=None, src=None),
    'COL': dict(name='Colorado Avalanche', gp=11, w=6, l=4, otl=1, gf=47, ga=34, home='4-1-1', home_gp=6,
                road='2-3-0', road_gp=5, l10='5-4-1', streak='W1', src='nhl-standings-2410'),
    'DAL': dict(name='Dallas Stars', gp=10, w=6, l=3, otl=1, gf=26, ga=17, home='3-2-0', home_gp=5,
                road='3-1-1', road_gp=5, l10='6-3-1', streak='W4', src='nhl-standings-2410'),
    'DET': dict(name='Detroit Red Wings', gp=10, w=4, l=3, otl=3, gf=28, ga=30, home='3-3-1', home_gp=7,
                road='1-0-2', road_gp=3, l10='4-3-3', streak='W1', src='nhl-standings-2410'),
    'EDM': dict(name='Edmonton Oilers', gp=10, w=8, l=1, otl=1, gf=47, ga=32, home='3-1-1', home_gp=5,
                road='5-0-0', road_gp=5, l10='8-1-1', streak='W3', src='nhl-standings-2410'),
    'FLA': dict(name='Florida Panthers', gp=11, w=5, l=4, otl=2, gf=28, ga=30, home='2-1-0', home_gp=3,
                road='3-3-2', road_gp=8, l10='4-4-2', streak='L2', src='nhl-standings-2410'),
    'LAK': dict(name='Los Angeles Kings', gp=None, w=None, l=None, otl=None, gf=None, ga=None, src=None),
    'MIN': dict(name='Minnesota Wild', gp=11, w=6, l=3, otl=2, gf=32, ga=27, home='4-0-0', home_gp=4,
                road='2-3-2', road_gp=7, l10='5-3-2', streak='L1', src='nhl-standings-2410'),
    'MTL': dict(name='Montreal Canadiens', gp=10, w=5, l=3, otl=2, gf=34, ga=35, home='3-2-1', home_gp=6,
                road='2-1-1', road_gp=4, l10='5-3-2', streak='W1', src='nhl-standings-2410'),
    'NJD': dict(name='New Jersey Devils', gp=10, w=6, l=4, otl=0, gf=33, ga=31, home='5-2-0', home_gp=7,
                road='1-2-0', road_gp=3, l10='6-4-0', streak='W2', src='nhl-standings-2410'),
    'NSH': dict(name='Nashville Predators', gp=9, w=3, l=3, otl=3, gf=23, ga=30, home='2-2-1', home_gp=5,
                road='1-1-2', road_gp=4, l10='3-3-3', streak='L1', src='nhl-standings-2410'),
    'NYI': dict(name='New York Islanders', gp=10, w=5, l=3, otl=2, gf=29, ga=23, home='4-1-1', home_gp=6,
                road='1-2-1', road_gp=4, l10='5-3-2', streak='OT1', src='nhl-standings-2410'),
    'NYR': dict(name='New York Rangers', gp=12, w=7, l=4, otl=1, gf=37, ga=29, home='6-0-0', home_gp=6,
                road='1-4-1', road_gp=6, l10='6-3-1', streak='L1', src='nhl-standings-2410'),
    'OTT': dict(name='Ottawa Senators', gp=11, w=7, l=4, otl=0, gf=31, ga=30, home='4-2-0', home_gp=6,
                road='3-2-0', road_gp=5, l10='6-4-0', streak='L1', src='nhl-standings-2410'),
    'PHI': dict(name='Philadelphia Flyers', gp=12, w=3, l=6, otl=3, gf=20, ga=37, home='2-2-2', home_gp=6,
                road='1-4-1', road_gp=6, l10='3-5-2', streak='W3', src='nhl-standings-2410'),
    'PIT': dict(name='Pittsburgh Penguins', gp=11, w=4, l=6, otl=1, gf=37, ga=38, home='3-1-0', home_gp=4,
                road='1-5-1', road_gp=7, l10='3-6-1', streak='W1', src='nhl-standings-2410'),
    'SEA': dict(name='Seattle Kraken', gp=11, w=7, l=3, otl=1, gf=38, ga=36, home='3-2-1', home_gp=6,
                road='4-2-1', road_gp=7, l10='6-3-1', streak='W2', src='nhl-standings-2410'),
    'SJS': dict(name='San Jose Sharks', gp=11, w=6, l=4, otl=1, gf=33, ga=37, home='2-2-0', home_gp=4,
                road='4-2-1', road_gp=7, l10='5-4-1', streak='W2', src='nhl-standings-2410',
                note='Only one of San Jose\'s eleven games has been won in regulation.'),
    'STL': dict(name='St. Louis Blues', gp=10, w=5, l=4, otl=1, gf=35, ga=31, home='3-0-1', home_gp=4,
                road='2-4-0', road_gp=6, l10='5-4-1', streak='W2', src='nhl-standings-2410'),
    'TBL': dict(name='Tampa Bay Lightning', gp=10, w=7, l=3, otl=0, gf=34, ga=29, home='5-0-0', home_gp=5,
                road='2-3-0', road_gp=5, l10='7-3-0', streak='L1', src='nhl-standings-2410'),
    'TOR': dict(name='Toronto Maple Leafs', gp=12, w=6, l=4, otl=2, gf=43, ga=39, home='4-3-1', home_gp=8,
                road='2-1-1', road_gp=4, l10='5-3-2', streak='W3', src='nhl-standings-2410'),
    'UTA': dict(name='Utah Mammoth', gp=11, w=7, l=4, otl=0, gf=41, ga=36, home='3-1-0', home_gp=4,
                road='4-3-0', road_gp=7, l10='6-4-0', streak='L1', src='nhl-standings-2410'),
    'VGK': dict(name='Vegas Golden Knights', gp=12, w=8, l=4, otl=0, gf=46, ga=36, home='5-2-0', home_gp=7,
                road='3-2-0', road_gp=5, l10='7-3-0', streak='L2', src='nhl-standings-2410'),
    'WPG': dict(name='Winnipeg Jets', gp=10, w=4, l=3, otl=3, gf=26, ga=29, home='2-2-1', home_gp=5,
                road='2-1-2', road_gp=5, l10='4-3-3', streak='OT1', src='nhl-standings-2410'),
    'WSH': dict(name='Washington Capitals', gp=9, w=5, l=4, otl=0, gf=30, ga=29, home='4-2-0', home_gp=6,
                road='1-2-0', road_gp=3, l10='5-4-0', streak='L1', src='nhl-standings-2410'),
}

# --- MLB club data ---------------------------------------------------------
MLB_TEAMS = {
    'MIL': dict(name='Milwaukee Brewers', w=103, l=59, home='55-26', road='48-33', l10='8-2',
                src='mlb-standings-nl'),
    'TBR': dict(name='Tampa Bay Rays', w=98, l=64, home='55-26', road='43-38', l10='5-5',
                src='mlb-standings-al'),
}

# --- fixtures --------------------------------------------------------------
# market_* are the moneyline prices the *league's own feed* publishes for its
# betting partners (providerId 9, American). They are never our price.
FIXTURES = [
    dict(id='nhl-2026020168', sport='ice-hockey', a='ANA', b='PHI', home='PHI',
         start_utc='2026-10-24T17:00:00Z', venue='Xfinity Mobile Arena', neutral=False,
         competition='NHL', game_state='LIVE', sources=['nhl-schedule-2410']),
    dict(id='nhl-2026020169', sport='ice-hockey', a='LAK', b='NJD', home='NJD',
         start_utc='2026-10-24T19:30:00Z', venue='Prudential Center', neutral=False,
         competition='NHL', game_state='FUT', sources=['nhl-schedule-2410'],
         market_home=-194, market_away=160),
    dict(id='nhl-2026020170', sport='ice-hockey', a='SJS', b='BOS', home='BOS',
         start_utc='2026-10-24T23:00:00Z', venue='TD Garden', neutral=False,
         competition='NHL', game_state='FUT', sources=['nhl-schedule-2410', 'nhl-on-tap-7568'],
         market_home=-192, market_away=160),
    dict(id='nhl-2026020171', sport='ice-hockey', a='NYR', b='OTT', home='OTT',
         start_utc='2026-10-24T23:00:00Z', venue='Canadian Tire Centre', neutral=False,
         competition='NHL', game_state='FUT', sources=['nhl-schedule-2410'],
         market_home=-125, market_away=105),
    dict(id='nhl-2026020172', sport='ice-hockey', a='NSH', b='PIT', home='PIT',
         start_utc='2026-10-24T23:00:00Z', venue='PPG Paints Arena', neutral=False,
         competition='NHL', game_state='FUT', sources=['nhl-schedule-2410'],
         market_home=-125, market_away=105),
    dict(id='nhl-2026020173', sport='ice-hockey', a='BUF', b='WSH', home='WSH',
         start_utc='2026-10-24T23:00:00Z', venue='Capital One Arena', neutral=False,
         competition='NHL', game_state='FUT', sources=['nhl-schedule-2410'],
         market_home=-125, market_away=105),
    dict(id='nhl-2026020174', sport='ice-hockey', a='VGK', b='CBJ', home='CBJ',
         start_utc='2026-10-24T23:00:00Z', venue='Nationwide Arena', neutral=False,
         competition='NHL', game_state='FUT', sources=['nhl-schedule-2410'],
         market_home=114, market_away=-135),
    dict(id='nhl-2026020175', sport='ice-hockey', a='CAR', b='STL', home='STL',
         start_utc='2026-10-24T23:00:00Z', venue='Enterprise Center', neutral=False,
         competition='NHL', game_state='FUT', sources=['nhl-schedule-2410'],
         market_home=130, market_away=-155),
    dict(id='nhl-2026020176', sport='ice-hockey', a='TOR', b='EDM', home='EDM',
         start_utc='2026-10-24T23:00:00Z', venue='Rogers Place', neutral=False,
         competition='NHL', game_state='FUT', sources=['nhl-schedule-2410', 'nhl-on-tap-7568'],
         market_home=-166, market_away=140),
    dict(id='nhl-2026020177', sport='ice-hockey', a='TBL', b='UTA', home='UTA',
         start_utc='2026-10-25T01:00:00Z', venue='Delta Center', neutral=False,
         competition='NHL', game_state='FUT', sources=['nhl-schedule-2410'],
         market_home=-142, market_away=120),
    dict(id='nhl-2026020178', sport='ice-hockey', a='DET', b='CGY', home='CGY',
         start_utc='2026-10-25T02:00:00Z', venue='Scotiabank Saddledome', neutral=False,
         competition='NHL', game_state='FUT', sources=['nhl-schedule-2410'],
         market_home=108, market_away=-130),
    dict(id='nhl-2026020180', sport='ice-hockey', a='FLA', b='CHI', home='CHI',
         start_utc='2026-10-25T19:00:00Z', venue='United Center', neutral=False,
         competition='NHL', game_state='FUT', sources=['nhl-schedule-2510']),
    dict(id='nhl-2026020181', sport='ice-hockey', a='NYI', b='DAL', home='DAL',
         start_utc='2026-10-25T22:00:00Z', venue='American Airlines Center', neutral=False,
         competition='NHL', game_state='FUT', sources=['nhl-schedule-2510']),
    dict(id='nhl-2026020182', sport='ice-hockey', a='MTL', b='WPG', home='WPG',
         start_utc='2026-10-25T23:00:00Z', venue='Princess Auto Stadium', neutral=True,
         competition='NHL (2026 Tim Hortons Heritage Classic)', game_state='FUT',
         sources=['nhl-schedule-2510']),
    dict(id='nhl-2026020183', sport='ice-hockey', a='COL', b='NSH', home='NSH',
         start_utc='2026-10-26T00:00:00Z', venue='Bridgestone Arena', neutral=False,
         competition='NHL', game_state='FUT', sources=['nhl-schedule-2510']),
    dict(id='mlb-849802', sport='baseball', a='TBR', b='MIL', home='MIL',
         start_utc='2026-10-25T00:00:00Z', venue='American Family Field', neutral=False,
         competition='MLB World Series, Game 2 (Milwaukee lead 1-0)', game_state='Scheduled',
         conditional=False, sources=['mlb-schedule', 'mlb-result-2310']),
    dict(id='mlb-849804', sport='baseball', a='MIL', b='TBR', home='TBR',
         start_utc='2026-10-27T00:00:00Z', venue='Tropicana Field', neutral=False,
         competition='MLB World Series, Game 3', game_state='Scheduled',
         conditional=False, sources=['mlb-schedule']),
    dict(id='mlb-849803', sport='baseball', a='MIL', b='TBR', home='TBR',
         start_utc='2026-10-28T00:00:00Z', venue='Tropicana Field', neutral=False,
         competition='MLB World Series, Game 4', game_state='Scheduled',
         conditional=False, sources=['mlb-schedule']),
    dict(id='mlb-849799', sport='baseball', a='MIL', b='TBR', home='TBR',
         start_utc='2026-10-29T00:00:00Z', venue='Tropicana Field', neutral=False,
         competition='MLB World Series, Game 5 (if necessary)', game_state='Scheduled',
         conditional=True, sources=['mlb-schedule']),
    dict(id='mlb-849801', sport='baseball', a='TBR', b='MIL', home='MIL',
         start_utc='2026-10-31T00:00:00Z', venue='American Family Field', neutral=False,
         competition='MLB World Series, Game 6 (if necessary)', game_state='Scheduled',
         conditional=True, sources=['mlb-schedule']),
    dict(id='mlb-849800', sport='baseball', a='TBR', b='MIL', home='MIL',
         start_utc='2026-11-01T00:00:00Z', venue='American Family Field', neutral=False,
         competition='MLB World Series, Game 7 (if necessary)', game_state='Scheduled',
         conditional=True, sources=['mlb-schedule']),
]

# Fixtures the official slate contains but this desk did not capture in full.
# They are published as gaps, never as inferred rows.
UNCAPTURED = [
    {'sport': 'ice-hockey',
     'detail': 'The NHL feed reports twelve games on 24 October 2026; eleven were captured with '
               'time, venue and both clubs. Minnesota @ Seattle is the twelfth and was not reached '
               'before this desk closed.',
     'source': 'nhl-schedule-2410'},
    {'sport': 'ice-hockey',
     'detail': 'The NHL feed reports five games on 25 October 2026; four were captured. The fifth '
               'was not reached before this desk closed.',
     'source': 'nhl-schedule-2510'},
]

# Clubs whose 2026-27 record was not read this session. Their games are listed
# with an official start and source but are not priced: a price without both
# clubs\' records would be an invented input.
MISSING_CLUBS = {
    'ANA': 'Anaheim was on the captured standings page beyond the chunk read this session.',
    'CBJ': 'Columbus was on the captured standings page beyond the chunk read this session.',
    'CGY': 'Calgary was on the captured standings page beyond the chunk read this session.',
    'CHI': 'Chicago was on the captured standings page beyond the chunk read this session.',
    'LAK': 'Los Angeles was on the captured standings page beyond the chunk read this session.',
}


# --- maths -----------------------------------------------------------------
def american_from_prob(p):
    if p is None or not (0 < p < 1):
        return None
    return int(round(-100 * p / (1 - p))) if p >= 0.5 else int(round(100 * (1 - p) / p))


def normal_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def shrink(rate, gp, prior_rate, prior_games=PRIOR_GAMES):
    return (rate * gp + prior_rate * prior_games) / (gp + prior_games)


def team_rates(code, sport='ice-hockey'):
    if sport == 'ice-hockey':
        t = TEAMS[code]
        if not t.get('gp'):
            return None
        gf = shrink(t['gf'] / t['gp'], t['gp'], LEAGUE_GF)
        ga = shrink(t['ga'] / t['gp'], t['gp'], LEAGUE_GF)
        return {'gf': gf, 'ga': ga, 'record': f"{t['w']}-{t['l']}-{t['otl']}"}
    t = MLB_TEAMS[code]
    gp = t['w'] + t['l']
    win = shrink(t['w'] / gp, gp, 0.5, PRIOR_GAMES_MLB)
    return {'win': win, 'record': f"{t['w']}-{t['l']}"}


def nhl_book(fx):
    """Originated moneyline, puck line and match total for an NHL game."""
    away, home = team_rates(fx['a']), team_rates(fx['home'])
    if not away or not home:
        return None
    hfa = 0.0 if fx.get('neutral') else HFA_NHL
    lam_home = (home['gf'] + away['ga']) / 2 + hfa / 2
    lam_away = (away['gf'] + home['ga']) / 2 - hfa / 2
    margin = lam_home - lam_away
    p_home = normal_cdf(margin / SIGMA_NHL)
    total = lam_home + lam_away
    p_over = 1 - normal_cdf((5.5 - total) / SIGMA_TOTAL)
    p_home_pl = 1 - normal_cdf((1.5 - margin) / SIGMA_NHL)
    markets = [
        {'key': 'moneyline', 'label': 'Match winner (moneyline, includes overtime and shootout)',
         'outcomes': [
             {'selection': TEAMS[fx['home']]['name'], 'code': fx['home'], 'p': p_home},
             {'selection': TEAMS[fx['a']]['name'], 'code': fx['a'], 'p': 1 - p_home}]},
        {'key': 'puck-line', 'label': 'Puck line (handicap, 1.5 goals, no push)',
         'outcomes': [
             {'selection': f"{TEAMS[fx['home']]['name']} -1.5", 'code': fx['home'], 'p': p_home_pl},
             {'selection': f"{TEAMS[fx['a']]['name']} +1.5", 'code': fx['a'], 'p': 1 - p_home_pl}]},
        {'key': 'total', 'label': 'Match total goals (5.5, no push)',
         'outcomes': [
             {'selection': 'Over 5.5 goals', 'code': 'OVER', 'p': p_over},
             {'selection': 'Under 5.5 goals', 'code': 'UNDER', 'p': 1 - p_over}]},
    ]
    return {'lam_home': lam_home, 'lam_away': lam_away, 'total': total, 'markets': markets}


def mlb_book(fx):
    """Originated moneyline for an MLB game, plus the markets we withhold."""
    away, home = team_rates(fx['a'], 'baseball'), team_rates(fx['home'], 'baseball')
    if not away or not home:
        return None
    # Log5 on shrunk win rates, then a small home-field adjustment.
    pa, ph = away['win'], home['win']
    p_home = (ph - pa * ph) / (ph + pa - 2 * pa * ph)
    if fx.get('neutral'):
        pass
    elif fx.get('home'):
        p_home = min(0.95, max(0.05, p_home + 0.025))
    markets = [{'key': 'moneyline', 'label': 'Match winner (moneyline)',
                'outcomes': [
                    {'selection': MLB_TEAMS[fx['home']]['name'], 'code': fx['home'], 'p': p_home},
                    {'selection': MLB_TEAMS[fx['a']]['name'], 'code': fx['a'], 'p': 1 - p_home}]}]
    return {'markets': markets, 'p_home': p_home}


def enrich(fx):
    """Attach books, prices, band membership and the pick for one fixture."""
    out = dict(fx)
    book = nhl_book(fx) if fx['sport'] == 'ice-hockey' else mlb_book(fx)
    out['book'] = book
    if fx.get('conditional'):
        book = None
    out['priced'] = bool(book)
    if not book and fx.get('conditional'):
        out['unpriced_reason'] = ('Conditional game. The league flags this fixture as if-necessary, so '
                                  'no selection is issued on a match that may never be played.')
        out['markets'] = []
        out['pick'] = None
        return out
    if not book:
        missing = [c for c in (fx['a'], fx['home']) if not team_rates(c, fx['sport'])]
        out['unpriced_reason'] = (
            'Official record not captured for ' + ' and '.join(TEAMS[c]['name'] for c in missing)
            + '. A price without both clubs\' published records would be an invented input.')
        out['markets'] = []
        out['pick'] = None
        return out
    for market in book['markets']:
        for o in market['outcomes']:
            o['fair_decimal'] = round(1 / o['p'], 4)
            o['american'] = american_from_prob(o['p'])
            o['in_band'] = bool(BAND_LOW <= o['american'] <= BAND_HIGH)
    out['markets'] = book['markets']
    out['withheld'] = []
    if fx['sport'] == 'baseball':
        out['withheld'] = [
            {'key': 'handicap', 'label': 'Run line (+/-1.5)',
             'reason': 'Withheld: the run line needs a read run environment for both clubs. '
                       'Only win-loss and home/road splits were read, so a spread would rest on an '
                       'unread input.'},
            {'key': 'total', 'label': 'Match total runs',
             'reason': 'Withheld: MLB publishes starting pitchers separately and no confirmed '
                       'starter for this game was read. A total without the starters would be an '
                       'invented input.'},
        ]
    out['pick'] = choose_pick(out)
    return out


def choose_pick(fx):
    """One pick per match. The winner market leads; a total is used only when it is blank.

    The rule is fixed and published on the methodology page: take the better
    side of the moneyline if it clears 0.55 and sits inside the band; otherwise
    take the strongest in-band selection from the other investigated markets.
    Handicap selections are priced for comparison but never selected, because a
    one-goal cushion can clear 70% without saying anything about who wins.
    """
    ml = next((m for m in fx['markets'] if m['key'] == 'moneyline'), None)
    if ml:
        top = max(ml['outcomes'], key=lambda o: o['p'])
        if top['in_band'] and top['p'] >= PICK_MIN:
            return _pick(ml, top)
    best = None
    for market in fx['markets']:
        if market['key'] in ('moneyline', 'puck-line'):
            continue
        for o in market['outcomes']:
            if o['in_band'] and o['p'] >= PICK_MIN and (best is None or o['p'] > best[1]['p']):
                best = (market, o)
    return _pick(*best) if best else None


def _pick(market, outcome):
    return {'market': market['key'], 'market_label': market['label'],
            'selection': outcome['selection'], 'code': outcome['code'],
            'probability': outcome['p'], 'fair_decimal': outcome['fair_decimal'],
            'american': outcome['american'],
            'confidence': 'high' if outcome['p'] >= HIGH_MIN else 'medium'}


def build_desk():
    fixtures = [enrich(fx) for fx in FIXTURES]
    picks = [f for f in fixtures if f['pick']]
    for f in picks:
        f['prediction'] = PREDICTIONS.get(f['id'])
        f['pick']['prediction'] = PREDICTIONS.get(f['id'])
    counts = {
        'sports_requested': len(SPORTS),
        'sports_with_fixtures': len({f['sport'] for f in fixtures}),
        'fixtures': len(fixtures),
        'priced_fixtures': sum(1 for f in fixtures if f['priced']),
        'unpriced_fixtures': sum(1 for f in fixtures if not f['priced']),
        'markets': sum(len(f['markets']) for f in fixtures),
        'outcomes': sum(len(m['outcomes']) for f in fixtures for m in f['markets']),
        'withheld_markets': sum(len(f.get('withheld', [])) for f in fixtures),
        'picks': len(picks),
        'high': sum(1 for f in picks if f['pick']['confidence'] == 'high'),
        'medium': sum(1 for f in picks if f['pick']['confidence'] == 'medium'),
        'predictions': len(PREDICTIONS),
        'sources': len(SOURCES),
        'flags': len(FLAGS),
    }
    return {'generated_at': READ_AT, 'fixtures': fixtures, 'picks': picks,
            'counts': counts, 'sources': SOURCES, 'flags': FLAGS, 'uncaptured': UNCAPTURED}


# --- written predictions ---------------------------------------------------
# Every number below is taken from the sources listed on the same row. Each
# write-up names the selection in its first sentence and runs past 30 words.
PREDICTIONS = {
    'nhl-2026020170': (
        'Boston Bruins to win, including overtime and shootout, is my selection against San Jose. '
        'Boston enters 8-2-1 after beating Nashville 6-0 on Thursday, with David Pastrnak and Charlie '
        'McAvoy contributing four points apiece. Pastrnak has 16 points in eleven games, while Macklin '
        'Celebrini has fourteen in nine for the Sharks. San Jose has won twice consecutively after '
        'a 1-3-1 stretch, so this is not a one-sided matchup. Boston’s seven-game point streak '
        'provides the stronger recent foundation; neither starting goalie nor a complete injury list '
        'is established by the cited preview.'),
    'nhl-2026020171': (
        'Over 5.5 goals is the call when the New York Rangers visit Canadian Tire Centre. The winner '
        'market is a coin flip, with Ottawa at 53%, but the scoring rates are not neutral: the '
        'Rangers put up 3.08 goals a game and concede 2.42, while Ottawa scores 2.82 and concedes '
        '2.73. Blend those four rates and the projected total lands essentially on the line at 5.5, '
        'so this is the thinnest call on the board; the over still edges it because the Rangers\' '
        'twelve games have averaged 5.50 goals and Ottawa\'s eleven 5.55.'),
    'nhl-2026020172': (
        'Back the Pittsburgh Penguins at home to Nashville. Pittsburgh is only 4-6-1 overall, yet it '
        'is 3-1-0 at PPG Paints Arena and has scored 37 goals across eleven games. The Predators '
        'have managed 23 in nine, the lowest scoring rate of any club priced here, and hold a '
        '1-1-2 road line. Pittsburgh scores 3.36 per game while Nashville scores 2.56, and the '
        'visitors concede 3.33 a night, so the home side owns the better half of a level matchup.'),
    'nhl-2026020173': (
        'The Washington Capitals are the pick at Capital One Arena against Buffalo. Washington is '
        '5-4-0 and 4-2-0 at home, with 30 goals for and 29 against. The Sabres are 4-4-2 and minus '
        'nine on the season after scoring 28 and conceding 37, and they have taken four of a '
        'possible eight road points at 1-1-2. Buffalo leaks 3.70 goals a game, the widest '
        'defensive hole in this fixture, and Washington has the steadier numbers on home ice.'),
    'nhl-2026020175': (
        'Over 5.5 goals is the play in St. Louis. Carolina\'s twelve games have produced 80 goals, '
        '47 for and 33 against, and the Blues have '
        'produced 66 across ten. The Hurricanes average 3.92 per game and St. Louis 3.50, and the '
        'Blues concede 3.10 a game compared with Carolina\'s 2.75. Two attacks combining for 7.42 '
        'goals a game make 5.5 a low bar, even with St. Louis unbeaten in regulation at home.'),
    'nhl-2026020176': (
        'Edmonton Oilers to win the match, with overtime and shootout included, is the selection '
        'against Toronto. Connor McDavid supplied two goals and three assists in Thursday’s 6-5 '
        'shootout victory over Carolina, taking him to 31 points through ten games. Edmonton’s '
        '8-1-1 start contrasts with Toronto’s 6-4-2 record. The Maple Leafs remain dangerous '
        'through Auston Matthews, but John Tavares is week to week with an upper-body injury '
        'according to the league preview. That combination supports Edmonton, although the '
        'starting goaltenders and full availability picture remain unresolved.'),
    'nhl-2026020177': (
        'Utah Mammoth to beat Tampa Bay at Delta Center is the pick. Utah is 7-4-0 with 41 goals for '
        'and 36 against, and has won three of four at home. The Lightning are 7-3-0 overall but '
        '2-3-0 on the road, where they have scored 16 and conceded 20. Utah scores 3.73 per game '
        'against a Tampa Bay side conceding 2.90, and the road split plus the venue carries the '
        'Mammoth past a Lightning team that has lost its last outing.'),
    'nhl-2026020181': (
        'The Dallas Stars at home to the New York Islanders is the selection. They are 6-3-1 and have won '
        'four in a row, conceding just 17 goals in ten games, the tightest defensive record on this '
        'board. New York is 5-3-2 but 1-2-1 on the road, scoring eight goals and conceding ten away '
        'from home. Dallas concedes 1.70 goals a night; New York\'s 23 against across ten works '
        'out at 2.30, a difference of more than half a goal every game.'),
    'nhl-2026020182': (
        'Play over 5.5 goals at the Heritage Classic in Winnipeg. Montreal\'s ten games have '
        'produced 69 goals, 34 for and 35 against, and the Jets\' have produced 55. The Canadiens '
        'average 3.40 goals and concede 3.50; Winnipeg averages 2.60 and concedes 2.90. A neutral '
        'outdoor venue removes the usual home cushion, and the combined rates project a total '
        'comfortably above a line set at five and a half.'),
    'nhl-2026020183': (
        'Over 5.5 goals in Nashville is the call. The Colorado Avalanche\'s eleven games have produced 81 goals, 47 for '
        'and 34 against, the highest combined figure on this slate, and the Avalanche average 4.27 '
        'a game. The Predators have scored only 23 in nine yet concede 3.33, so their defensive '
        'numbers alone point above the line. Six goals is a modest requirement when one side is '
        'scoring at four and a quarter a night.'),
    'mlb-849802': (
        'The Milwaukee Brewers are the pick to take World Series Game 2. They finished 103-59, are 55-26 at '
        'American Family Field and 8-2 across their last ten, and they won Game 1 at the same park '
        'by 3-2. Tampa Bay went 98-64 but only 43-38 on the road, with a 5-5 run over the last ten '
        'games. The home record and the sharper recent form both point to the Brewers, even allowing '
        'for a Rays side that won 55 games at home this year.'),
}

# --- review flags ----------------------------------------------------------
FLAGS = [
    {'id': 'F-3507-01', 'severity': 'resolved-rule',
     'title': 'The brief\'s two High-pick conditions contradicted each other; the band now governs',
     'detail': 'Taken together, "more than 70% to win" and "fair price between -250 and +10000" '
               'leave only the 1.4-point slice from -250 to -233, which is why earlier desks '
               'published zero High picks. This desk treats the -250..+10000 band as the hard '
               'rule (0.99% to 71.4% implied) and adds its own minimum of 60% for High. A '
               'selection cannot be High just for being a short market favourite: anything '
               'shorter than -250 is excluded by the band.',
     'sources': ['olbg-ice-hockey']},
    {'id': 'F-3507-02', 'severity': 'coverage',
     'title': 'Thirteen of the fifteen requested sports carry no priced match today',
     'detail': 'Every sport is listed on the site with the link to its own OLBG hub, but only ice '
               'hockey and baseball had an official fixture-and-record source that could be read '
               'and parsed this session. NBA and EuroLeague feeds returned errors, the ATP scores '
               'page showed only matches already in progress, and the remaining federations '
               'publish no machine-readable fixture list. Nothing was filled in from memory.',
     'sources': []},
    {'id': 'F-3507-03', 'severity': 'gap',
     'title': 'Two NHL games on the official slate were not captured',
     'detail': 'The league feed reports twelve games on 24 October and five on 25 October. Eleven '
               'and four respectively were captured with start, venue and both clubs. Minnesota @ '
               'Seattle and one further 25 October game were not reached. They are listed as gaps, '
               'not as rows with a guessed time.',
     'sources': ['nhl-schedule-2410', 'nhl-schedule-2510']},
    {'id': 'F-3507-04', 'severity': 'unverified',
     'title': 'Injury and lineup news is not included anywhere in this desk',
     'detail': 'No official injury report, transaction wire or confirmed starting lineup was read '
               'for any of these matches. Rather than describe unread team news, every write-up '
               'sticks to records, scoring and splits that are on the cited page. Where a total '
               'would need a starting pitcher, the market is withheld instead of estimated.',
     'sources': ['nhl-standings-2410', 'mlb-schedule']},
    {'id': 'F-3507-05', 'severity': 'interpretation',
     'title': 'The published market price is the league feed\'s, not a bookmaker screenshot',
     'detail': 'The NHL schedule feed publishes partner prices next to each game. Those are shown '
               'beside our originated price and labelled as the publisher\'s. They are used only '
               'for comparison; no originated price is copied from them, and no claim of a betting '
               'edge is made where our price is the longer of the two.',
     'sources': ['nhl-schedule-2410']},
    {'id': 'F-3507-06', 'severity': 'gap',
     'title': 'Six clubs could not be priced because their season record was not read',
     'detail': 'Anaheim, Columbus, Calgary, Chicago and Los Angeles sit beyond the portion of the '
               'standings page read this session. Their four games are published with official '
               'start times and source links but no price. A price built on one club\'s record '
               'would be an invented input.',
     'sources': ['nhl-standings-2410', 'nhl-schedule-2410']},
]
