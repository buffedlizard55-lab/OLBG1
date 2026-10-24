"""Facts captured for the 733888f2 desk (session T733888F2, 24-25 October 2026).

Every fact below was read in this session through the retrieval layer and is
listed with the exact official URL it came from. Nothing is inferred: where an
input is missing the field is None and the row says why.

Read times are the UTC timestamps of this session's reads on 2026-10-24.
"""

SESSION = '733888f2-olbg1'
TASK = 'T733888F2'
CAPTURED_UTC = '2026-10-24T23:15:00Z'

# --------------------------------------------------------------------------
# Sports in the brief, in the brief's order.
# --------------------------------------------------------------------------
SPORTS = [
    ('golf', 'Golf', 5, 'Golf'),
    ('volleyball', 'Volleyball', 21, 'Volleyball'),
    ('rugby-union', 'Rugby Union', 9, 'Rugby_Union'),
    ('cricket', 'Cricket', 7, 'Cricket'),
    ('snooker', 'Snooker', 8, 'Snooker'),
    ('darts', 'Darts', 15, 'Darts'),
    ('baseball', 'Baseball', 12, 'Baseball'),
    ('gaelic', 'Gaelic Sports', 25, 'Gaelic_Football'),
    ('greyhounds', 'Greyhounds', 28, 'Greyhounds'),
    ('tennis', 'Tennis', 3, 'Tennis'),
    ('motor-racing', 'Motor Racing', 14, 'Motor_Racing'),
    ('handball', 'Handball', 20, 'Handball'),
    ('ice-hockey', 'Ice Hockey', 13, 'Ice_Hockey'),
    ('basketball', 'Basketball', 4, 'Basketball'),
    ('rugby-league', 'Rugby League', 10, 'Rugby_League'),
]
SPORT_NAME = {s[0]: s[1] for s in SPORTS}


def olbg_url(slug):
    s = [x for x in SPORTS if x[0] == slug][0]
    return f'https://www.olbg.com/betting-tips/{s[3]}/{s[2]}'


# --------------------------------------------------------------------------
# Source register. role='fact' sources may support published numbers;
# role='discovery' sources may only say which events OLBG lists.
# --------------------------------------------------------------------------
def _src(sid, publisher, url, role, read_utc, what):
    return {'id': sid, 'publisher': publisher, 'url': url, 'role': role,
            'read_utc': read_utc, 'what': what}


SOURCES = [
    _src('nhl-score-1025', 'NHL', 'https://api-web.nhle.com/v1/score/2026-10-25', 'fact',
         '2026-10-24T22:36:00Z',
         'Official score/schedule feed for 2026-10-25: five games with start times, venues, '
         'each club W-L-OT record and each club scoring/assist/goaltending leader.'),
    _src('nhl-standings', 'NHL', 'https://api-web.nhle.com/v1/standings/2026-10-24', 'fact',
         '2026-10-24T22:38:00Z',
         'Official league standings snapshot (standingsDateTimeUtc 2026-10-24T22:25:30Z); '
         'used only to confirm the two leading clubs read from the score feed.'),
    _src('mlb-schedule', 'MLB', 'https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-10-24&hydrate=probablePitcher', 'fact',
         '2026-10-24T22:52:00Z',
         'Official schedule: gamePk 849802, World Series game 2, 2026-10-25T00:00:00Z, '
         'American Family Field, probable pitchers Drew Rasmussen (TB) and Logan Henderson (MIL).'),
    _src('mlb-standings-al', 'MLB', 'https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026', 'fact',
         '2026-10-24T23:02:00Z',
         'Official final regular-season standings: Tampa Bay Rays 98-64 (AL East 1).'),
    _src('mlb-standings-nl', 'MLB', 'https://statsapi.mlb.com/api/v1/standings?leagueId=104&season=2026', 'fact',
         '2026-10-24T23:06:00Z',
         'Official final regular-season standings: Milwaukee Brewers 103-59.'),
    _src('quins-preview', 'Harlequins FC (club, official)',
         'https://www.quins.co.uk/article/accountsiq-match-preview-harlequins-v-saracens', 'fact',
         '2026-10-24T23:10:00Z',
         'Club match preview: Harlequins v Saracens, 15:00 Sunday 25 October, Twickenham Stoop, '
         'referee Hamish Smales, both named 23s, Marcus Smith 200th appearance, Fergus Burke at '
         'fly-half after Saracens\' Investec Champions Cup defeat to Connacht, and the club\'s own '
         'head-to-head note that Quins have won the last two at The Stoop and three of the last five.'),
    _src('prem-standings', 'Premiership Rugby (official)',
         'https://www.premrugby.com/competitions/gallagher-prem/standings', 'fact',
         '2026-10-24T23:12:00Z',
         'Official Gallagher PREM standings after round 3: Saracens P3 W2 D0 L1, points '
         'difference +21, 11 points, form W-L-W; Harlequins P3 W0 D0 L3, points difference -68, '
         '2 points, form L-L-L.'),
    _src('atp-basel-draw', 'ATP Tour (official)',
         'https://www.atptour.com/en/news/djokovic-basel-2026-draw-preview', 'fact',
         '2026-10-24T22:58:00Z',
         'ATP draw report for the Swiss Indoors Basel: Djokovic drawn against Ugo Humbert in round '
         'one; Stan Wawrinka meets Jiri Lehecka; Shelton is the top seed in the same half.'),
    _src('ecb-tri-series', 'England and Wales Cricket Board (official)',
         'https://www.ecb.co.uk/news/4562387/pakistan-to-host-sri-lanka-and-england-in-odi-triseries', 'fact',
         '2026-10-24T23:00:00Z',
         'Official schedule of the Pakistan ODI tri-series: 25 October Pakistan v England at '
         'Gaddafi Stadium, Lahore; 27 October Pakistan v Sri Lanka; 29 October Sri Lanka v England; '
         '31 October final.'),
    _src('pdc-ec-schedule', 'Professional Darts Corporation (official)',
         'https://www.pdc.tv/news/2026/october/19/2026-machineseeker-european-championship-schedule-confirmed/', 'fact',
         '2026-10-24T23:04:00Z',
         'Official schedule of play for the 2026 Machineseeker European Championship, Westfalenhalle '
         'Dortmund: round one 22-23 October, round two 24 October (afternoon 1300-1700 CEST), '
         'quarter-finals 25 October.'),
    _src('pdc-day-one', 'Professional Darts Corporation (official)',
         'https://www.pdc.tv/news/2026/october/22/2026-machineseeker-european-championship---day-one-latest', 'fact',
         '2026-10-24T23:04:00Z',
         'Official day-one report and round-one results, including Woodhouse 6-3 Van Duijvenbode '
         'and Huybrechts replacing Luke Humphries in the field.'),
    _src('olbg-tennis', 'OLBG (discovery only)', 'https://www.olbg.com/betting-tips/Tennis/3', 'discovery',
         '2026-10-24T22:28:00Z', 'Listed tennis events and market labels.'),
    _src('olbg-cricket', 'OLBG (discovery only)', 'https://www.olbg.com/betting-tips/Cricket/7', 'discovery',
         '2026-10-24T22:29:00Z', 'Listed cricket events and market labels.'),
    _src('olbg-darts', 'OLBG (discovery only)', 'https://www.olbg.com/betting-tips/Darts/15', 'discovery',
         '2026-10-24T22:30:00Z', 'Listed darts events, times as served and market labels.'),
    _src('olbg-snooker', 'OLBG (discovery only)', 'https://www.olbg.com/betting-tips/Snooker/8', 'discovery',
         '2026-10-24T22:31:00Z', 'Snooker hub returned "No tips found".'),
    _src('olbg-golf', 'OLBG (discovery only)', 'https://www.olbg.com/betting-tips/Golf/5', 'discovery',
         '2026-10-24T22:29:00Z', 'Golf hub returned "No tips found".'),
    _src('olbg-hockey', 'OLBG (discovery only)', 'https://www.olbg.com/betting-tips/Ice_Hockey/13', 'discovery',
         '2026-10-24T22:33:00Z', 'Listed ten NHL games for "Today" all carrying the same 19:07 time.'),
    _src('olbg-basketball', 'OLBG (discovery only)', 'https://www.olbg.com/betting-tips/Basketball/4', 'discovery',
         '2026-10-24T22:34:00Z', 'Listed seven NBA games and three KBL games.'),
    _src('olbg-baseball', 'OLBG (discovery only)', 'https://www.olbg.com/betting-tips/Baseball/12', 'discovery',
         '2026-10-24T22:35:00Z', 'Listed one MLB game: TB Rays @ MIL Brewers.'),
    _src('olbg-rugby-union', 'OLBG (discovery only)', 'https://www.olbg.com/betting-tips/Rugby_Union/9', 'discovery',
         '2026-10-24T22:37:00Z', 'Listed USA v Australia A, Harlequins v Saracens, La Rochelle v Bordeaux.'),
    _src('olbg-rugby-league', 'OLBG (discovery only)', 'https://www.olbg.com/betting-tips/Rugby_League/10', 'discovery',
         '2026-10-24T22:39:00Z', 'Only outright markets listed (State of Origin 2027, Super League 2027, NRL 2027).'),
    _src('olbg-motor', 'OLBG (discovery only)', 'https://www.olbg.com/betting-tips/Motor_Racing/14', 'discovery',
         '2026-10-24T22:40:00Z', 'Motor Racing hub returned "No tips found".'),
    _src('olbg-handball', 'OLBG (discovery only)', 'https://www.olbg.com/betting-tips/Handball/20', 'discovery',
         '2026-10-24T22:41:00Z', 'Listed ~20 handball fixtures; most popular selection shown as "Tie" for most of them.'),
    _src('olbg-volleyball', 'OLBG (discovery only)', 'https://www.olbg.com/betting-tips/Volleyball/21', 'discovery',
         '2026-10-24T22:42:00Z', 'Listed ~20 volleyball fixtures including five SuperLega matches.'),
    _src('olbg-gaelic', 'OLBG (discovery only)', 'https://www.olbg.com/betting-tips/Gaelic_Football/25', 'discovery',
         '2026-10-24T22:43:00Z', 'Listed four club football fixtures plus the 2027 All-Ireland outright.'),
    _src('olbg-greyhounds', 'OLBG (discovery only)', 'https://www.olbg.com/betting-tips/Greyhounds/28', 'discovery',
         '2026-10-24T22:44:00Z', 'Listed one race: 11:04 Doncaster with "Snowfall" as the most-tipped runner.'),
    _src('legavolley-r1', 'Lega Pallavolo Serie A (official)',
         'https://www.legavolley.it/2026/1a-giornata-and-18-10-2026-regular-season-superlega-stagione-2026-risultati-classifica/', 'fact',
         '2026-10-24T22:48:00Z',
         'Official round-one page for SuperLega 2026/27 (opened; only the site chrome was readable '
         'through the retrieval layer before the page body, so no table values are published).'),
]
SOURCE_INDEX = {s['id']: s for s in SOURCES}


# --------------------------------------------------------------------------
# Matches. status: 'priced' | 'listed'
# inputs: the exact official numbers the price is built from.
# --------------------------------------------------------------------------
def m(**kw):
    kw.setdefault('status', 'priced')
    kw.setdefault('facts', [])
    kw.setdefault('inputs', {})
    kw.setdefault('market_notes', [])
    return kw


MATCHES = [
    # ---------------- Ice Hockey -------------------------------------------------
    m(id='NHL-1', sport='ice-hockey', comp='NHL', start='2026-10-25T19:00:00Z',
      start_label='Sun 25 Oct, 19:00 UTC', venue='United Center, Chicago',
      home='Chicago Blackhawks', away='Florida Panthers',
      official='https://www.nhl.com/gamecenter/fla-vs-chi/2026/10/25/2026020180',
      inputs={'away': {'record': '5-4-2', 'points': 12, 'gp': 11},
              'home': {'record': '3-7-0', 'points': 6, 'gp': 10}},
      facts=['Florida are 5-4-2 and Chicago are 3-7-0 on the NHL score feed.',
             'Brady Tkachuk leads Florida with 7 goals; Matthew Tkachuk has 12 assists; '
             'Jacob Markstrom has 3 wins.',
             'Chicago counters with 3 goals from Roman Kantserov, 5 assists from Patrick Kane '
             'and 3 wins from Spencer Knight.']),
    m(id='NHL-2', sport='ice-hockey', comp='NHL', start='2026-10-25T22:00:00Z',
      start_label='Sun 25 Oct, 22:00 UTC', venue='American Airlines Center, Dallas',
      home='Dallas Stars', away='New York Islanders',
      official='https://www.nhl.com/gamecenter/nyi-vs-dal/2026/10/25/2026020181',
      inputs={'away': {'record': '5-3-2', 'points': 12, 'gp': 10},
              'home': {'record': '6-3-1', 'points': 13, 'gp': 10}},
      facts=['Dallas are 6-3-1 and the Islanders 5-3-2 after ten games each.',
             'Mikko Rantanen has 5 goals and Jason Robertson 8 assists for Dallas; '
             'Jake Oettinger has 5 wins.',
             'Bo Horvat has 5 goals, Matthew Schaefer 8 assists and Ilya Sorokin 5 wins for New York.']),
    m(id='NHL-3', sport='ice-hockey', comp='NHL (2026 Tim Hortons Heritage Classic)', start='2026-10-25T23:00:00Z',
      start_label='Sun 25 Oct, 23:00 UTC', venue='Princess Auto Stadium, Winnipeg (neutral site)',
      home='Winnipeg Jets', away='Montreal Canadiens', neutral=True,
      official='https://www.nhl.com/gamecenter/mtl-vs-wpg/2026/10/25/2026020182',
      inputs={'away': {'record': '5-3-2', 'points': 12, 'gp': 10},
              'home': {'record': '4-3-3', 'points': 11, 'gp': 10}},
      facts=['The NHL feed marks this as a neutral-site game at Princess Auto Stadium for the '
             '2026 Tim Hortons NHL Heritage Classic.',
             'Montreal are 5-3-2 with Cole Caufield on 6 goals and Nick Suzuki on 7 assists.',
             'Winnipeg are 4-3-3 with Kyle Connor on 9 goals and Neal Pionk on 6 assists.']),
    m(id='NHL-4', sport='ice-hockey', comp='NHL', start='2026-10-26T00:00:00Z',
      start_label='Mon 26 Oct, 00:00 UTC', venue='Bridgestone Arena, Nashville',
      home='Nashville Predators', away='Colorado Avalanche',
      official='https://www.nhl.com/gamecenter/col-vs-nsh/2026/10/25/2026020183',
      inputs={'away': {'record': '6-4-1', 'points': 13, 'gp': 11},
              'home': {'record': '3-3-3', 'points': 9, 'gp': 9}},
      facts=['Colorado are 6-4-1; Nashville are 3-3-3 and have played two fewer games.',
             'Artturi Lehkonen has 9 goals and Nathan MacKinnon 13 assists for Colorado, '
             'with Mackenzie Blackwood on 5 wins.',
             'Ryan O\'Reilly has 4 goals, Roman Josi 8 assists and Juuse Saros 3 wins for Nashville.']),
    m(id='NHL-5', sport='ice-hockey', comp='NHL', start='2026-10-26T02:00:00Z',
      start_label='Mon 26 Oct, 02:00 UTC', venue='Rogers Arena, Vancouver',
      home='Vancouver Canucks', away='Minnesota Wild',
      official='https://www.nhl.com/gamecenter/min-vs-van/2026/10/25/2026020184',
      inputs={'away': {'record': '6-3-2', 'points': 14, 'gp': 11},
              'home': {'record': '2-9-1', 'points': 5, 'gp': 12}},
      facts=['Minnesota are 6-3-2 and Vancouver are 2-9-1, the widest record gap on the slate.',
             'Kirill Kaprizov has 11 goals and Quinn Hughes 11 assists for Minnesota; '
             'Jesper Wallstedt has 6 wins.',
             'Vancouver\'s leading scorer has 4 goals and Leevi Merilainen has 1 win.']),

    # ---------------- Baseball ---------------------------------------------------
    m(id='MLB-1', sport='baseball', comp='MLB World Series, game 2', start='2026-10-25T00:00:00Z',
      start_label='Sun 25 Oct, 00:00 UTC (8pm ET Sat)', venue='American Family Field, Milwaukee',
      home='Milwaukee Brewers', away='Tampa Bay Rays',
      official='https://www.mlb.com/gameday/849802',
      inputs={'away': {'record': '98-64', 'pct': .605},
              'home': {'record': '103-59', 'pct': .636},
              'series': 'Milwaukee lead the best-of-seven 1-0'},
      facts=['MLB lists the game as World Series game 2 of 7 at American Family Field.',
             'The probable pitchers are Drew Rasmussen for Tampa Bay and Logan Henderson for Milwaukee.',
             'Milwaukee finished the regular season 103-59, Tampa Bay 98-64.']),

    # ---------------- Rugby Union -------------------------------------------------
    m(id='RU-1', sport='rugby-union', comp='Gallagher PREM, round 4', start='2026-10-25T15:00:00Z',
      start_label='Sun 25 Oct, 15:00 UTC', venue='Twickenham Stoop, London',
      home='Harlequins', away='Saracens',
      official='https://www.quins.co.uk/article/accountsiq-match-preview-harlequins-v-saracens',
      inputs={'away': {'table': 'P3 W2 D0 L1', 'points': 11, 'pd': 21, 'form': 'W-L-W'},
              'home': {'table': 'P3 W0 D0 L3', 'points': 2, 'pd': -68, 'form': 'L-L-L'}},
      facts=['Harlequins have lost all three league games, with a points difference of -68 and '
             '2 points; Saracens are 2-1 with +21 and 11 points.',
             'Harlequins name Marcus Smith at fly-half for his 200th appearance; Saracens start '
             'Fergus Burke at 10 with Maro Itoje captaining.',
             'Referee Hamish Smales; the club notes Quins have won the last two meetings at The Stoop.']),
]

# --------------------------------------------------------------------------
# Listed-but-not-priced rows: discovered on OLBG, no official input read.
# --------------------------------------------------------------------------
def u(sport, comp, event, when, reason, olbg=None):
    return {'sport': sport, 'comp': comp, 'event': event, 'when': when,
            'reason': reason, 'olbg': olbg or olbg_url(sport)}


UNPRICED = [
    u('rugby-union', 'International', 'USA v Australia A', 'OLBG: "Today 19:00" (time as served)',
      'Fixture not confirmed on a governing-body page this session; USA Rugby and Rugby Australia '
      'pages were not reachable through the retrieval layer.', 'https://www.olbg.com/betting-tips/Rugby_Union/9'),
    u('rugby-union', 'Top 14', 'La Rochelle v Bordeaux', 'OLBG: "Tomorrow 16:05" (time as served)',
      'LNR Top 14 match page not read this session, so neither side\'s current table line is available.'),
    u('cricket', 'Pakistan ODI tri-series', 'Pakistan v England, 4th match', '25 Oct, Gaddafi Stadium Lahore',
      'Fixture and venue confirmed by the ECB schedule, but no official toss, squad or series '
      'scorecard was read, so no price is published.', 'https://www.ecb.co.uk/news/4562387/pakistan-to-host-sri-lanka-and-england-in-odi-triseries'),
    u('cricket', 'Pakistan ODI tri-series', 'Pakistan v Sri Lanka', '27 Oct, Gaddafi Stadium Lahore',
      'Fixture confirmed by the ECB schedule; no official form or squad input read.'),
    u('cricket', 'Pakistan ODI tri-series', 'Sri Lanka v England', '29 Oct, Gaddafi Stadium Lahore',
      'Fixture confirmed by the ECB schedule; no official form or squad input read.'),
    u('cricket', 'CSA T20 Challenge', 'North West Dragons v Northern Cape Heat', 'OLBG: "Tomorrow 07:00"',
      'No Cricket South Africa page read this session.'),
    u('cricket', 'CSA T20 Challenge', 'Tuskers v Western Province', 'OLBG: "Tomorrow 07:00"',
      'No Cricket South Africa page read this session.'),
    u('cricket', 'CSA T20 Challenge', 'Boland v Titans', 'OLBG: "Tomorrow 07:00"',
      'No Cricket South Africa page read this session.'),
    u('cricket', 'CSA T20 Challenge', 'Eastern Storm v South Africa Emerging', 'OLBG: "Tomorrow 07:00"',
      'No Cricket South Africa page read this session.'),
    u('cricket', 'Global T20 Canada', 'Toronto Kings v Vancouver Guardians', 'OLBG: "Today 19:00"',
      'No official league page read this session.'),
    u('cricket', 'International (women)', 'India W v Zimbabwe W, 2nd ODI', 'OLBG: "Tomorrow 04:30"',
      'No BCCI or Zimbabwe Cricket page read this session.'),
    u('cricket', 'International', 'New Zealand v India, 3rd T20', '27 Oct',
      'No New Zealand Cricket or BCCI page read this session.'),
    u('cricket', 'International', 'Namibia v Ireland, 3rd ODI', '27 Oct',
      'No Cricket Ireland or Cricket Namibia page read this session.'),
    u('tennis', 'ATP 500 Basel', 'Novak Djokovic v Ugo Humbert', 'Basel, round one',
      'Draw confirmed by the ATP, but no ATP ranking, ranking-points or 2026 match record was read, '
      'so the price is withheld.', 'https://www.atptour.com/en/news/djokovic-basel-2026-draw-preview'),
    u('tennis', 'ATP 500 Basel', 'Stan Wawrinka v Jiri Lehecka', 'Basel, round one',
      'Draw confirmed by the ATP; no ranking or form input read.', 'https://www.atptour.com/en/news/djokovic-basel-2026-draw-preview'),
    u('tennis', 'ATP 500 Basel', 'Ben Shelton v Casper Ruud', 'OLBG listing only',
      'The ATP draw report read this session does not settle this pairing\'s round or court, so the '
      'row is discovery-only.'),
    u('tennis', 'ATP 500 Basel', 'Taylor Fritz v Stefanos Tsitsipas', 'OLBG listing only',
      'Draw slot not confirmed on the ATP report read this session.'),
    u('tennis', 'ATP 500 Basel', 'Holger Rune v Quentin Halys', 'OLBG listing only',
      'Draw slot not confirmed on the ATP report read this session.'),
    u('tennis', 'ATP 500 Basel', 'Lorenzo Musetti v Taylor Fritz', 'OLBG listing only',
      'Draw slot not confirmed on the ATP report read this session.'),
    u('tennis', 'WTA', 'Elena Rybakina v Leylah Fernandez', 'OLBG: "Tomorrow 05:00"',
      'No WTA draw or ranking page read this session.'),
    u('tennis', 'WTA', 'Ashlyn Krueger v Katerina Siniakova', 'OLBG: "Tomorrow 00:30"',
      'No WTA draw or ranking page read this session.'),
    u('basketball', 'NBA', 'Milwaukee Bucks @ Philadelphia 76ers', 'OLBG: "Today 19:30"',
      'nba.com served only its calendar shell (8 games listed for 24 Oct, no matchup data); the '
      'CDN scoreboard endpoint returned HTTP 500 and stats.nba.com was unreachable, so no official '
      'record was read.'),
    u('basketball', 'NBA', 'New Orleans Pelicans @ Denver Nuggets', 'OLBG: "Today 22:00"',
      'No official NBA record or availability input read.'),
    u('basketball', 'NBA', 'Brooklyn Nets @ Cleveland Cavaliers', 'OLBG: "Today 19:30"',
      'No official NBA record or availability input read.'),
    u('basketball', 'NBA', 'San Antonio Spurs @ Dallas Mavericks', 'OLBG: "Today 20:00"',
      'No official NBA record or availability input read.'),
    u('basketball', 'NBA', 'Houston Rockets @ Atlanta Hawks', 'OLBG: "Today 20:30"',
      'No official NBA record or availability input read.'),
    u('basketball', 'NBA', 'Washington Wizards @ Chicago Bulls', 'OLBG: "Today 20:00"',
      'No official NBA record or availability input read.'),
    u('basketball', 'NBA', 'Golden State Warriors @ Phoenix Suns', 'OLBG: "Today 23:00"',
      'No official NBA record or availability input read.'),
    u('volleyball', 'SuperLega', 'Itas Trentino v Cisterna', 'OLBG: "Tomorrow 12:00"',
      'The official SuperLega round-one page was opened but only site chrome was retrievable, so no '
      'table line is published for either side.', 'https://www.legavolley.it/2026/1a-giornata-and-18-10-2026-regular-season-superlega-stagione-2026-risultati-classifica/'),
    u('volleyball', 'SuperLega', 'Cucine Lube Civitanova v Pallavolo Padova', 'OLBG: "Tomorrow 13:00"',
      'No official table line read.'),
    u('volleyball', 'SuperLega', 'Sir Susa Scai Perugia v Tinet Prata di Pordenone', 'OLBG: "Tomorrow 13:00"',
      'No official table line read.'),
    u('volleyball', 'SuperLega', 'Vero Volley Monza v Rana Verona', 'OLBG: "Tomorrow 13:00"',
      'No official table line read.'),
    u('volleyball', 'SuperLega', 'CHKS Chelm v Resovia Rzeszow', 'OLBG: "Tomorrow 13:00"',
      'Polish PlusLiga page not read this session.'),
    u('volleyball', 'Bundesliga', 'Barock Volleys Ludwigsburg v TV Rottenburg', 'OLBG: "Tomorrow 12:00"',
      'German league page not read this session.'),
    u('volleyball', 'Sultanlar Ligi', 'Vakifbank W v Galatasaray W', 'OLBG: "Tomorrow 07:00"',
      'Turkish league page not read this session.'),
    u('volleyball', 'Sultanlar Ligi', 'Besiktas W v Goztepe W', 'OLBG: "Tomorrow 06:00"',
      'Turkish league page not read this session.'),
    u('volleyball', 'Brazilian Superliga', 'Abel-Moda Brusque W v Praia Clube W', 'OLBG: "Today 20:00"',
      'Brazilian league page not read this session.'),
    u('volleyball', 'Serie A1 (women)', 'Conegliano W v Vallefoglia W', 'OLBG: "28 Oct 15:00"',
      'Italian women\'s league page not read this session.'),
    u('handball', 'Handbollsligan', 'Ystads IF HF v Hammarby IF HF', 'OLBG: "Tomorrow 09:00"',
      'No Swedish league page read this session, and OLBG shows the market favourite as "Tie", which '
      'is not a usable probability.'),
    u('handball', 'Liga ASOBAL', 'CBM Sporting Alicante v Ademar Leon', 'OLBG: "Tomorrow 07:00"',
      'No Liga ASOBAL page read this session.'),
    u('handball', 'Liqui Moly StarLigue', 'Saint Raphael v PSG Handball', 'OLBG: "Tomorrow 11:00"',
      'No LNH page read this session.'),
    u('handball', 'Handball-Bundesliga', 'Rhein Neckar Lowen v SC Magdeburg', 'OLBG: "Tomorrow 10:00"',
      'No HBL page read this session.'),
    u('handball', 'EHF Champions League', 'SC Magdeburg v HC Kriens Luzern', '28 Oct',
      'EHF fixture page not read this session.'),
    u('handball', 'EHF Champions League', 'KS Kielce v Kolstad', '28 Oct',
      'EHF fixture page not read this session.'),
    u('handball', 'EHF Champions League', 'Fuchse Berlin v RK Partizan', '29 Oct',
      'EHF fixture page not read this session.'),
    u('gaelic', 'Galway SFC', 'Moycullen v Salthill-Knocknacarra', 'OLBG: "Tomorrow 12:00"',
      'No Galway GAA fixture or result page read this session.'),
    u('gaelic', 'Cork SFC', 'St Finbarrs v Nemo Rangers', 'OLBG: "Tomorrow 12:00"',
      'No Cork GAA fixture or result page read this session.'),
    u('gaelic', 'Cork SFC', 'Kanturk v Eire Og', '1 Nov',
      'No Cork GAA page read this session.'),
    u('gaelic', 'Limerick SFC', 'Fr Caseys v Kildimo Pallaskenry', '1 Nov',
      'No Limerick GAA page read this session.'),
    u('greyhounds', 'GBGB graded', '11:04 Doncaster (most-tipped: Snowfall)', 'OLBG: "Tomorrow 07:04"',
      'GBGB does not publish a machine-readable card for this meeting through the retrieval layer, '
      'so no trap draw, sectional or form line is available for any runner.'),
    u('darts', 'PDC European Championship', 'Ross Smith v Luke Woodhouse', 'OLBG: "Tomorrow 08:15"',
      'PDC results show this as a completed Saturday second-round tie (Smith beat Damon Heta 10-7 '
      'and Woodhouse beat Gian van Veen 10-6), so OLBG is listing a played match as upcoming.'),
    u('darts', 'PDC European Championship', 'Gerwyn Price v Stephen Bunting', 'OLBG: "Tomorrow 09:15"',
      'PDC results show both players already through Saturday\'s second round (Price 10-4 Menzies, '
      'Bunting 10-3 Huybrechts); the pair meet in the Sunday quarter-final, which OLBG has not listed.'),
]
