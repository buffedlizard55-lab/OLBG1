"""T424375B4 — session 424375b4-olbg1 data capture.

Every value below was transcribed from a source read during this session's live
fetch window (2026-10-22T20:55Z–21:10Z). Nothing is filled from memory or
inference: where a value was not read from a source, it is absent (None) and the
row carries an explicit flag. OLBG observations are discovery only (tip shares
are votes, not probabilities). Model outputs are computed in s424375b4_model.py
and are labelled estimates everywhere.

Verification classes:
  A — official publisher body fetched and read directly this session
  B — official publisher URL confirmed; body text taken from a search-engine
      excerpt of that exact official URL because the publisher serves a
      cookie-consent shell to the fetcher (flagged for reviewer)
  C — discovery only (OLBG hub); no official read completed — values blank
"""

SESSION_ID = '424375b4-olbg1'
TASK_ID = 'T424375B4'
HARVEST_START = '2026-10-22T20:55:00Z'
HARVEST_END = '2026-10-22T21:10:00Z'
DESK_AS_OF = '2026-10-22T21:06:00Z'

# ---------------------------------------------------------------- sources ---
SOURCES = [
    dict(id='S-NHL-SCHED', sport='ice-hockey', publisher='NHL (api-web.nhle.com)',
         url='https://api-web.nhle.com/v1/schedule/2026-10-22',
         read_at='2026-10-22T20:58Z', klass='A',
         what='Official 2026-22-27 NHL game-week feed: 12 scheduled games on '
              '2026-10-22 (gameState FUT, gameScheduleState OK), exact startTimeUTC '
              'per game, venues, embedded provider odds arrays for both sides.'),
    dict(id='S-NHL-STAND', sport='ice-hockey', publisher='NHL (api-web.nhle.com)',
         url='https://api-web.nhle.com/v1/standings/2026-10-22',
         read_at='2026-10-22T20:58Z', klass='A',
         what='Official standings stamped standingsDateTimeUtc 2026-10-22T20:57:30Z: '
              'all 32 clubs with W-L-OTL, points, goals for/against, home/road '
              'splits, L10 records and streak codes.'),
    dict(id='S-MLB-SCHED', sport='baseball', publisher='MLB (statsapi.mlb.com)',
         url='https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=10/23/2026&hydrate=probablePitcher',
         read_at='2026-10-22T20:58Z', klass='A',
         what='Official MLB schedule: World Series Game 1, Tampa Bay Rays at '
              'Milwaukee Brewers, gamePk 849805, gameDate 2026-10-24T00:00:00Z, '
              'status Scheduled, ifNecessary "N" (Normal Game), probable pitchers '
              'Nick Martinez (TB) and Jacob Misiorowski (MIL), American Family Field.'),
    dict(id='S-MLB-AL-EAST', sport='baseball', publisher='MLB (statsapi.mlb.com)',
         url='https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026',
         read_at='2026-10-22T20:59Z', klass='A',
         what='Official 2026 regular-season standings: Tampa Bay Rays 98-64 '
              '(.605, AL East champions), runs scored 736, runs allowed 650.'),
    dict(id='S-MLB-NL-EAST', sport='baseball', publisher='MLB (statsapi.mlb.com)',
         url='https://statsapi.mlb.com/api/v1/standings?leagueId=104&season=2026&division=204',
         read_at='2026-10-22T21:04Z', klass='A',
         what='Official NL standings read (division filter ignored by the endpoint; '
              'response carried the NL East). Milwaukee Brewers record NOT present '
              'in any chunk read this session — Brewers row left blank and flagged.'),
    dict(id='S-URC-TABLE', sport='rugby-union', publisher='United Rugby Championship',
         url='https://stats.unitedrugby.com/match-centre/table/2026-27',
         read_at='2026-10-22T21:01Z', klass='A',
         what='Official URC table after three rounds: all 16 clubs with points, '
              'played, W-D-L, bonus points, points for/against and FORM strings.'),
    dict(id='S-URC-R4', sport='rugby-union', publisher='United Rugby Championship',
         url='https://stats.unitedrugby.com/match-centre/2026-27/4',
         read_at='2026-10-22T21:01Z', klass='A',
         what='Official Round 4 fixtures (page states "All times shown are Local"): '
              'Friday 23 October — Cardiff v Sharks, Connacht v Zebre, Edinburgh v '
              'Lions at 14:45; Saturday 24 October — Bulls v Ulster 07:45, Stormers '
              'v Scarlets 10:00, Benetton v Glasgow 10:00, Leinster v Munster 13:00, '
              'Ospreys v Dragons 14:00.'),
    dict(id='S-PROD2-J8', sport='rugby-union', publisher='LNR (prod2.lnr.fr)',
         url='https://prod2.lnr.fr/calendrier-et-resultats',
         read_at='2026-10-22T21:03Z', klass='A',
         what='Official Pro D2 Journée 8 calendar: eight fixtures Thursday 22 and '
              'Friday 23 October with published club league positions and French '
              'local kick-off times.'),
    dict(id='S-PROD2-TABLE', sport='rugby-union', publisher='LNR (prod2.lnr.fr)',
         url='https://prod2.lnr.fr/classement',
         read_at='2026-10-22T21:04Z', klass='A',
         what='Official Pro D2 standings (J7, plus Montauban/Oyonnax already on 8 '
              'matches): all 16 clubs with points, played, G-N-P, bonus, points '
              'for/against and recent-form result links.'),
    dict(id='S-TOP14-J7', sport='rugby-union', publisher='LNR (top14.lnr.fr)',
         url='https://top14.lnr.fr/calendrier-et-resultats',
         read_at='2026-10-22T21:03Z', klass='A',
         what='Official Top 14 Journée 7 calendar: seven fixtures Saturday 24 and '
              'Sunday 25 October with published club league positions and French '
              'local kick-off times.'),
    dict(id='S-TOP14-TABLE', sport='rugby-union', publisher='LNR (top14.lnr.fr)',
         url='https://top14.lnr.fr/classement',
         read_at='2026-10-22T21:04Z', klass='A',
         what='Official Top 14 standings (J6): all 14 clubs with points, played, '
              'G-N-P, bonus, points for/against and recent-form result links.'),
    dict(id='S-EL-STAND', sport='basketball', publisher='Euroleague Basketball',
         url='https://www.euroleaguebasketball.net/en/euroleague/standings/',
         read_at='2026-10-22T21:04Z', klass='A',
         what='Official EuroLeague 2026-27 regular-season standings: all 20 clubs '
              'with GP, W-L, win%, points for/against, home/away splits and L10.'),
    dict(id='S-NBA-CLEPHI', sport='basketball', publisher='NBA (nba.com)',
         url='https://www.nba.com/cavaliers/game/0022600006-cavaliers-vs-sixers-philadelphia-pa-10-22-2026/event-details',
         read_at='2026-10-22T21:05Z', klass='B',
         what='Official event-details JSON-LD excerpt: Cleveland Cavaliers at '
              'Philadelphia 76ers, startDate 2026-10-22T23:00:00Z, Xfinity Mobile '
              'Arena, Philadelphia PA. (Body obtained via search excerpt of this '
              'exact official URL.)'),
    dict(id='S-NBA-NEWS', sport='basketball', publisher='NBA (nba.com)',
         url='https://www.nba.com/news/starting-5-october-22-2026',
         read_at='2026-10-22T21:05Z', klass='B',
         what='Official NBA.com Starting 5 (22 Oct 2026): "LeBron James and Jaylen '
              'Brown make their home debuts for Philly when the Sixers host the Cavs '
              '(7 ET). Then, Nikola Jokić and the Nuggets open their season against '
              'Shai Gilgeous-Alexander and the Thunder (9:30 ET)."'),
    dict(id='S-NBA-SCHED-NEWS', sport='basketball', publisher='NBA (nba.com)',
         url='https://www.nba.com/news/2026-27-nba-regular-season-schedule',
         read_at='2026-10-22T21:05Z', klass='B',
         what='Official 2026-27 schedule release: Oct 22 LeBron James home debut '
              'for Philadelphia vs Donovan Mitchell and the Cavaliers (7 p.m. ET); '
              'Shai Gilgeous-Alexander Thunder vs Nikola Jokić Nuggets at Paycom '
              'Center (9:30 p.m. ET); Oct 23 Knicks at Celtics (7 p.m. ET) and '
              'Spurs host the Rockets (9:30 p.m. ET) at Moody Center, Austin.'),
    dict(id='S-NBA-NYKBOS', sport='basketball', publisher='NBA (nba.com)',
         url='https://www.nba.com/game/0022600008',
         read_at='2026-10-22T21:05Z', klass='B',
         what='Official NBA game page excerpt: New York Knicks at Boston Celtics, '
              'Friday October 23rd 2026, 7:00 PM ET.'),
    dict(id='S-NBA-KNICKS', sport='basketball', publisher='NBA (nba.com)',
         url='https://www.nba.com/team/1610612752/knicks',
         read_at='2026-10-22T21:05Z', klass='B',
         what='Official Knicks team page excerpt: New York 0-1 (lost 106-100 at '
              'home to Philadelphia on Oct 20), Boston 0-1 entering Oct 23.'),
    dict(id='S-PDC-SCHED', sport='darts', publisher='Professional Darts Corporation',
         url='https://www.pdc.tv/news/2026/october/19/2026-machineseeker-european-championship-schedule-confirmed/',
         read_at='2026-10-22T21:03Z', klass='B',
         what='Official PDC schedule article excerpt: "Friday October 23 (1900-2300 '
              'CEST, 1800-2200 BST) Round One x8 — Ryan Joyce v Jermaine Wattimena; '
              'Krzysztof Ratajski v Dave Chisnall; Nathan Aspinall v Cristo Reyes; '
              'Jonny Clayton v Niko Springer; Luke Littler v William O\'Connor; '
              'Wessel Nijman v Martin Schindler; Kevin Doets v Michael van Gerwen; '
              'Josh Rock v Chris Dobey." (pdc.tv serves a cookie-consent shell to '
              'the fetcher; text is the search-engine excerpt of this exact URL.)'),
    dict(id='S-PDC-PREVIEW', sport='darts', publisher='Professional Darts Corporation',
         url='https://www.pdc.tv/news/2026/october/21/2026-machineseeker-european-championship-preview/',
         read_at='2026-10-22T21:03Z', klass='B',
         what='Official PDC preview excerpt: Luke Littler (world number one) faces '
              'Ireland\'s William O\'Connor; four-time champion Michael van Gerwen '
              'faces compatriot Kevin Doets; Josh Rock and Chris Dobey also meet.'),
    dict(id='S-ATP-SCORES', sport='tennis', publisher='ATP Tour',
         url='https://www.atptour.com/en/scores/current',
         read_at='2026-10-22T21:00Z', klass='A',
         what='Official ATP live scores page: Round-of-16 results read this session '
              '— Medvedev d. Shimabukuro 6-2 6-1 and Bublik w/o Marozsan (event '
              '9410); Lehecka d. Collignon 6-4 6-2 and Michelsen d. Goffin 6-3 6-4 '
              '(event 7485); Cobolli d. Wawrinka 6-2 6-4 and Fritz d. Herbert 6-2 '
              '7-5 (Lyon, event 496). ATP news confirms "Fritz shakes off scary '
              'fall, Cobolli fires past Wawrinka in Lyon".'),
    dict(id='S-WTA-TOUR', sport='tennis', publisher='WTA',
         url='https://www.wtatennis.com/scores',
         read_at='2026-10-22T21:00Z', klass='A',
         what='Official WTA scores hub: this-week tournaments are Prudential Hong '
              'Kong Tennis Open (1074), BNB Ningbo Open (2092) and Kinoshita Group '
              'Japan Open (Osaka, 405). Draw pages render client-side only; the '
              'individual OLBG-listed WTA match-ups could NOT be confirmed from an '
              'official body this session and are flagged unverified.'),
    dict(id='S-F1-USA', sport='motor-racing', publisher='Formula 1',
         url='https://www.formula1.com/en/racing/2026/united-states',
         read_at='2026-10-22T21:03Z', klass='A',
         what='Official United States Grand Prix page: FORMULA 1 MSC CRUISES UNITED '
              'STATES GRAND PRIX 2026 at Circuit of The Americas — 23 Oct Practice 1 '
              '13:30-14:30 and Practice 2 17:00-18:00, 24 Oct Practice 3 13:30-14:30 '
              'and Qualifying 17:00-18:00, 25 Oct Race 16:00 (track time). Circuit '
              'length 5.513km, 56 laps, race distance 308.432km; first GP 2012.'),
    dict(id='S-OLBG-HUBS', sport='all', publisher='OLBG (discovery only)',
         url='https://www.olbg.com/betting-tips',
         read_at='2026-10-22T20:56Z', klass='discovery',
         what='All 17 in-scope OLBG sport hubs read at 20:56-20:57Z: /betting-tips/'
              'Tennis/3, Basketball/4, Golf/5, Cricket/7, Snooker/8, Rugby_Union/9, '
              'Rugby_League/10, Baseball/12, Ice_Hockey/13, Motor_Racing/14, '
              'Darts/15, Handball/20, Volleyball/21, Aussie_Rules/22, eSports/23, '
              'Gaelic_Football/25, Greyhounds/28. Snooker, Aussie Rules, eSports and '
              'Greyhounds hubs returned "No tips found." Listings below are discovery '
              'leads; tip shares are votes, never used as probabilities.'),
]

# --------------------------------------------------------------- records ---
# (win, loss, ot_loss or draw, played, extra scoring info). All values class A
# reads unless noted. r_detail carries anything else the source published.

RECORDS = {
    # NHL (W, L, OTL, GP, GF, GA, L10 text, streak text)
    'NHL': {
        'NSH': dict(w=3, l=2, otl=3, gp=8, gf=23, ga=24, l10='3-2-3', streak='W1'),
        'BOS': dict(w=7, l=2, otl=1, gp=10, gf=36, ga=22, l10='7-2-1', streak='OT1'),
        'NYR': dict(w=7, l=3, otl=1, gp=11, gf=33, ga=24, l10='7-2-1', streak='W1'),
        'TOR': dict(w=5, l=4, otl=2, gp=11, gf=38, ga=35, l10='5-3-2', streak='W2'),
        'SJS': dict(w=5, l=4, otl=1, gp=10, gf=27, ga=35, l10='5-4-1', streak='W1'),
        'OTT': dict(w=7, l=3, otl=0, gp=10, gf=29, ga=24, l10='7-3-0', streak='W1'),
        'ANA': dict(w=4, l=5, otl=0, gp=9, gf=26, ga=29, l10='4-5-0', streak='L4'),
        'NJD': dict(w=5, l=4, otl=0, gp=9, gf=29, ga=30, l10='5-4-0', streak='W1'),
        'FLA': dict(w=5, l=3, otl=2, gp=10, gf=31, ga=30, l10='5-3-2', streak='L1'),
        'PIT': dict(w=3, l=6, otl=1, gp=10, gf=33, ga=38, l10='3-6-1', streak='L4'),
        'LAK': dict(w=1, l=4, otl=2, gp=7, gf=17, ga=27, l10='1-4-2', streak='W1'),
        'NYI': dict(w=5, l=3, otl=1, gp=9, gf=27, ga=20, l10='5-3-1', streak='W2'),
        'VGK': dict(w=8, l=3, otl=0, gp=11, gf=44, ga=30, l10='7-3-0', streak='L1'),
        'STL': dict(w=4, l=4, otl=1, gp=9, gf=29, ga=29, l10='4-4-1', streak='W1'),
        'WPG': dict(w=4, l=3, otl=2, gp=9, gf=24, ga=26, l10=None, streak=None),
        'DAL': dict(w=5, l=3, otl=1, gp=9, gf=23, ga=15, l10='5-3-1', streak='W3'),
        'MIN': dict(w=6, l=2, otl=2, gp=10, gf=31, ga=25, l10='6-2-2', streak='OT1'),
        'CGY': dict(w=2, l=6, otl=0, gp=8, gf=17, ga=37, l10='2-6-0', streak='W1'),
        'CAR': dict(w=8, l=2, otl=1, gp=11, gf=42, ga=27, l10='8-2-0', streak='W1'),
        'EDM': dict(w=7, l=1, otl=1, gp=9, gf=41, ga=27, l10='7-1-1', streak='W2'),
        'UTA': dict(w=7, l=3, otl=0, gp=10, gf=38, ga=31, l10='7-3-0', streak='W1'),
        'SEA': dict(w=6, l=3, otl=1, gp=10, gf=39, ga=34, l10='6-3-1', streak='W1'),
        'DET': dict(w=3, l=3, otl=3, gp=9, gf=23, ga=28, l10='3-3-3', streak='OT1'),
        'VAN': dict(w=2, l=8, otl=1, gp=11, gf=33, ga=51, l10='2-8-0', streak='L2'),
    },
    # URC: (W, D, L, PL, PF, PA, points, form)
    'URC': {
        'Edinburgh': dict(w=3, d=0, l=0, gp=3, pf=80, pa=54, pts=14, form='W W W'),
        'Glasgow Warriors': dict(w=2, d=1, l=0, gp=3, pf=95, pa=72, pts=13, form='W D W'),
        'Vodacom Bulls': dict(w=2, d=0, l=1, gp=3, pf=126, pa=54, pts=11, form='W L W'),
        'DHL Stormers': dict(w=2, d=0, l=1, gp=3, pf=81, pa=54, pts=11, form='W L W'),
        'Hollywoodbets Sharks': dict(w=2, d=0, l=1, gp=3, pf=89, pa=83, pts=10, form='W W L'),
        'Cardiff Rugby': dict(w=2, d=0, l=1, gp=3, pf=66, pa=71, pts=9, form='W W L'),
        '10bet Lions': dict(w=2, d=0, l=1, gp=3, pf=77, pa=102, pts=9, form='W W L'),
        'Dragons RFC': dict(w=1, d=1, l=1, gp=3, pf=88, pa=83, pts=9, form='D W L'),
        'Munster': dict(w=1, d=1, l=1, gp=3, pf=72, pa=74, pts=9, form='L W D'),
        'Leinster': dict(w=1, d=0, l=2, gp=3, pf=75, pa=58, pts=8, form='L L W'),
        'Ulster': dict(w=0, d=2, l=1, gp=3, pf=88, pa=93, pts=8, form='L D D'),
        'Scarlets': dict(w=1, d=0, l=2, gp=3, pf=68, pa=85, pts=7, form='L L W'),
        'Ospreys': dict(w=1, d=0, l=2, gp=3, pf=81, pa=107, pts=6, form='L L W'),
        'Connacht': dict(w=1, d=0, l=2, gp=3, pf=56, pa=84, pts=5, form='L W L'),
        'Benetton': dict(w=0, d=1, l=2, gp=3, pf=64, pa=68, pts=5, form='D L L'),
        'Zebre Parma': dict(w=0, d=0, l=3, gp=3, pf=52, pa=116, pts=1, form='L L L'),
    },
    # Pro D2: (G, N, P, M, PF, PA, points)
    'PROD2': {
        'Oyonnax': dict(w=7, d=0, l=1, gp=8, pf=336, pa=178, pts=34),
        'Provence': dict(w=7, d=0, l=0, gp=7, pf=222, pa=158, pts=29),
        'Grenoble': dict(w=5, d=0, l=2, gp=7, pf=213, pa=176, pts=22),
        'Montauban': dict(w=5, d=0, l=3, gp=8, pf=206, pa=237, pts=21),
        'Brive': dict(w=5, d=0, l=2, gp=7, pf=206, pa=164, pts=21),
        'Biarritz': dict(w=4, d=1, l=2, gp=7, pf=213, pa=191, pts=20),
        'Dax': dict(w=4, d=0, l=3, gp=7, pf=269, pa=264, pts=19),
        'Soyaux-Angouleme': dict(w=3, d=1, l=3, gp=7, pf=220, pa=180, pts=17),
        'Aurillac': dict(w=3, d=0, l=4, gp=7, pf=240, pa=254, pts=16),
        'Agen': dict(w=3, d=0, l=4, gp=7, pf=189, pa=206, pts=15),
        'Valence Romans': dict(w=2, d=0, l=5, gp=7, pf=192, pa=190, pts=13),
        'Colomiers': dict(w=2, d=0, l=5, gp=7, pf=220, pa=207, pts=12),
        'Nissa': dict(w=2, d=0, l=5, gp=7, pf=171, pa=213, pts=11),
        'Beziers': dict(w=2, d=0, l=5, gp=7, pf=147, pa=240, pts=9),
        'Narbonne': dict(w=2, d=0, l=5, gp=7, pf=186, pa=296, pts=9),
        'Nevers': dict(w=0, d=0, l=7, gp=7, pf=146, pa=222, pts=4),
    },
    # Top 14
    'TOP14': {
        'Toulouse': dict(w=5, d=0, l=1, gp=6, pf=197, pa=124, pts=24),
        'Pau': dict(w=5, d=0, l=1, gp=6, pf=239, pa=181, pts=22),
        'Bordeaux-Begles': dict(w=4, d=0, l=2, gp=6, pf=215, pa=151, pts=19),
        'La Rochelle': dict(w=4, d=0, l=2, gp=6, pf=144, pa=135, pts=18),
        'Bayonne': dict(w=4, d=0, l=2, gp=6, pf=190, pa=214, pts=17),
        'Stade Francais': dict(w=3, d=0, l=3, gp=6, pf=147, pa=158, pts=14),
        'Montpellier': dict(w=3, d=0, l=3, gp=6, pf=163, pa=122, pts=14),
        'Lyon': dict(w=3, d=0, l=3, gp=6, pf=193, pa=202, pts=14),
        'Perpignan': dict(w=3, d=0, l=3, gp=6, pf=166, pa=199, pts=13),
        'Toulon': dict(w=2, d=0, l=4, gp=6, pf=130, pa=130, pts=12),
        'Clermont': dict(w=2, d=0, l=4, gp=6, pf=140, pa=169, pts=11),
        'Racing 92': dict(w=2, d=0, l=4, gp=6, pf=143, pa=196, pts=10),
        'Castres': dict(w=2, d=0, l=4, gp=6, pf=126, pa=153, pts=9),
        'Vannes': dict(w=0, d=0, l=6, gp=6, pf=117, pa=176, pts=1),
    },
    # EuroLeague: (W, L, GP, PTS+, PTS-)
    'EL': {
        'Panathinaikos': dict(w=6, l=1, gp=7, pf=613, pa=517),
        'Fenerbahce': dict(w=5, l=1, gp=6, pf=501, pa=447),
        'Olympiacos': dict(w=5, l=1, gp=6, pf=564, pa=524),
        'Hapoel Tel Aviv': dict(w=5, l=2, gp=7, pf=630, pa=601),
        'Dubai': dict(w=5, l=2, gp=7, pf=597, pa=584),
        'Valencia': dict(w=4, l=2, gp=6, pf=583, pa=537),
        'Crvena Zvezda': dict(w=4, l=2, gp=6, pf=485, pa=457),
        'Real Madrid': dict(w=4, l=3, gp=7, pf=667, pa=630),
        'Barcelona': dict(w=4, l=3, gp=7, pf=623, pa=606),
        'Virtus Bologna': dict(w=4, l=3, gp=7, pf=606, pa=608),
        'Partizan': dict(w=3, l=3, gp=6, pf=466, pa=471),
        'Anadolu Efes': dict(w=3, l=4, gp=7, pf=581, pa=590),
        'Besiktas': dict(w=3, l=4, gp=7, pf=634, pa=644),
        'Zalgiris': dict(w=2, l=4, gp=6, pf=490, pa=517),
        'ASVEL': dict(w=2, l=4, gp=6, pf=527, pa=572),
        'Maccabi Tel Aviv': dict(w=2, l=5, gp=7, pf=608, pa=653),
        'FC Bayern Munich': dict(w=2, l=5, gp=7, pf=612, pa=659),
        'Paris Basketball': dict(w=1, l=5, gp=6, pf=504, pa=545),
        'Olimpia Milan': dict(w=1, l=6, gp=7, pf=585, pa=648),
        'Baskonia': dict(w=1, l=6, gp=7, pf=583, pa=649),
    },
    # NBA (tiny samples — season opened 21 Oct 2026)
    'NBA': {
        'PHI 76ers': dict(w=1, l=0, gp=1, pf=None, pa=None),
        'CLE Cavaliers': dict(w=0, l=0, gp=0, pf=None, pa=None),
        'BOS Celtics': dict(w=0, l=1, gp=1, pf=None, pa=None),
        'NY Knicks': dict(w=0, l=1, gp=1, pf=None, pa=None),
        # DEN / OKC / HOU / SAS / CHI / MIL: records not read from an official
        # body this session -> absent (blank + flagged in the tables).
    },
    # MLB regular season 2026
    'MLB': {
        'Tampa Bay Rays': dict(w=98, l=64, gp=162, pf=736, pa=650),
        # Milwaukee Brewers: NOT read this session.
    },
}
