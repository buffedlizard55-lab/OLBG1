"""Captured evidence for the 26 October 2026 desk (session aa2881ac-olbg1).

Every constant here was read during this session from the URL recorded in
SOURCES. The raw captures sit beside the desk in data/aa2881ac/*_raw.txt. If an
official page did not publish a figure, it is absent here rather than guessed,
and the gap is listed in FLAGS by saa2881ac_content.py.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'aa2881ac'
READ_WINDOW = '2026-10-26T04:45Z to 05:25Z'
GENERATED_FOR = '2026-10-26'


def _olbg(slug, sid, when, what):
    return dict(id=f'olbg-{slug.lower().replace("_", "-")}', publisher='OLBG',
                url=f'https://www.olbg.com/betting-tips/{slug}/{sid}',
                read_at=when, role='discovery', supports=what)


SOURCES = [
    _olbg('Golf', 5, '2026-10-26T04:46Z', 'Hub returned "No tips found." No golf market listed.'),
    _olbg('Volleyball', 21, '2026-10-26T04:46Z',
          'Fourteen volleyball events (Brazil, Poland, Austria and Italy) with the most-tipped selection and tip share.'),
    _olbg('Rugby_Union', 9, '2026-10-26T04:47Z', 'Only the Six Nations 2027 outright was listed. No match market.'),
    _olbg('Cricket', 7, '2026-10-26T04:47Z', 'Five match markets plus a man-of-the-match market for South Africa v Australia.'),
    _olbg('Snooker', 8, '2026-10-26T04:47Z', 'Hub returned "No tips found."'),
    _olbg('Darts', 15, '2026-10-26T04:48Z', 'Only the PDC World Championship 2027 outright was listed.'),
    _olbg('Baseball', 12, '2026-10-26T04:48Z', 'Hub returned "No tips found." The World Series was not listed.'),
    _olbg('Gaelic_Football', 25, '2026-10-26T04:48Z', 'Two Munster club football fixtures plus the All-Ireland 2027 outright.'),
    _olbg('Greyhounds', 28, '2026-10-26T04:49Z', 'A single race listed: 3:19 Monmore, one tip on Tullymurry Skies.'),
    _olbg('Tennis', 3, '2026-10-26T04:50Z',
          'Twenty match markets read from the first two of five pages (ATP Basel and Vienna, plus WTA and lower-tier matches).'),
    _olbg('Motor_Racing', 14, '2026-10-26T04:51Z', 'One market: Mexico City Grand Prix winner, Charles Leclerc on 1 of 2 tips.'),
    _olbg('Handball', 20, '2026-10-26T04:52Z',
          'Twelve EHF Champions League round-six fixtures plus one Swedish league match. "Tie" was the most-tipped outcome in nine of them.'),
    _olbg('Ice_Hockey', 13, '2026-10-26T04:45Z', 'Three NHL games, two Danish games, and four Liiga, SHL and DEL games.'),
    _olbg('Basketball', 4, '2026-10-26T04:53Z', 'Hub returned "No tips found." No NBA or European market.'),
    _olbg('Rugby_League', 10, '2026-10-26T04:54Z', 'Outrights only: State of Origin 2027, Super League and NRL 2027 Grand Finals.'),
    # ---- official publishers ------------------------------------------------
    dict(id='nhl-schedule', publisher='NHL', url='https://api-web.nhle.com/v1/schedule/2026-10-26',
         read_at='2026-10-26T04:58Z', role='official',
         supports='The 26 October games (LAK@NYR, TOR@CGY, DET@EDM), ten of the eleven 27 October games, venues and UTC start times.'),
    dict(id='nhl-standings', publisher='NHL', url='https://api-web.nhle.com/v1/standings/2026-10-25',
         read_at='2026-10-26T04:55Z', role='official',
         supports='All 32 clubs: GP, W, L, OTL, goals for and against, home and road splits, last ten and streak (standingsDateTimeUtc 2026-10-26T04:41:45Z).'),
    dict(id='nhl-standings-page', publisher='NHL', url='https://www.nhl.com/standings/2026-10-25/league',
         read_at='2026-10-26T04:55Z', role='official',
         supports='Human-readable view of the same standings table (the JSON above is what was read).'),
    dict(id='del-table', publisher='PENNY DEL', url='https://www.penny-del.org/tabelle',
         read_at='2026-10-26T05:18Z', role='official',
         supports='Koelner Haie v Adler Mannheim on 27 Oct at 19:00 CET, plus the table rows for thirteen of the fourteen clubs (Iserlohn row cut off in the read).'),
    dict(id='mlb-ws', publisher='MLB', url='https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-20&endDate=2026-11-05&gameType=W&hydrate=probablePitcher,linescore',
         read_at='2026-10-26T05:00Z', role='official',
         supports='World Series G1 MIL 3 TB 2 and G2 MIL 5 TB 4 (both finals). G3 at Tropicana Field 27 Oct 00:00Z with Gasser v Peralta probable. G4 has no probables published.'),
    dict(id='mlb-team-hitting', publisher='MLB', url='https://statsapi.mlb.com/api/v1/teams/stats?season=2026&group=hitting,pitching&stats=season&sportIds=1&gameType=R',
         read_at='2026-10-26T05:03Z', role='official',
         supports='Regular-season runs scored: MIL 832, TB 736, plus nine other clubs on the first page read.'),
    dict(id='mlb-mil-pitching', publisher='MLB', url='https://statsapi.mlb.com/api/v1/teams/158/stats?stats=season&group=pitching&season=2026&gameType=R',
         read_at='2026-10-26T05:04Z', role='official', supports='MIL runs allowed 618, ERA 3.51, 103-59.'),
    dict(id='mlb-tb-pitching', publisher='MLB', url='https://statsapi.mlb.com/api/v1/teams/139/stats?stats=season&group=pitching&season=2026&gameType=R',
         read_at='2026-10-26T05:04Z', role='official', supports='TB runs allowed 650, ERA 3.70, 98-64.'),
    dict(id='mlb-starters', publisher='MLB', url='https://statsapi.mlb.com/api/v1/people?personIds=688107,642547&hydrate=stats(group=[pitching],type=[season],season=2026)',
         read_at='2026-10-26T05:04Z', role='official', supports='Robert Gasser 2026: 20 starts, 3.87 ERA, 1.19 WHIP, 4.03 runs per nine.'),
    dict(id='mlb-peralta', publisher='MLB', url='https://statsapi.mlb.com/api/v1/people/642547/stats?stats=season&group=pitching&season=2026&gameType=R',
         read_at='2026-10-26T05:05Z', role='official',
         supports='Freddy Peralta 2026: 32 starts, 4.42 ERA overall (4.99 in 22 starts for the Mets, 3.25 in 10 for Tampa Bay), 4.85 runs per nine.'),
    dict(id='atp-rankings', publisher='ATP Tour', url='https://www.atptour.com/en/rankings/singles',
         read_at='2026-10-26T05:10Z', role='official',
         supports='Singles ranking and points dated 26 Oct 2026 (top 150, read from the page JSON feed at /en/-/www/rank/sglroll/150).'),
    dict(id='atp-basel-op', publisher='ATP Tour', url='https://www.atptour.com/en/scores/current/basel/328/daily-schedule',
         read_at='2026-10-26T05:07Z', role='official', supports='Basel order of play for Monday 26 October (Day 3).'),
    dict(id='atp-basel-draw', publisher='ATP Tour', url='https://www.atptour.com/en/scores/current/basel/328/draws',
         read_at='2026-10-26T05:12Z', role='official',
         supports='Basel R32 pairings, including Djokovic (4, WC) v Humbert and Tabilo v Jodar (3).'),
    dict(id='atp-vienna-op', publisher='ATP Tour', url='https://www.atptour.com/en/scores/current/vienna/337/daily-schedule',
         read_at='2026-10-26T05:07Z', role='official', supports='Vienna order of play for Monday 26 October (Day 3).'),
    dict(id='atp-scores', publisher='ATP Tour', url='https://www.atptour.com/en/scores/current',
         read_at='2026-10-26T05:06Z', role='official',
         supports='Qualifying results: Neumayer d. Droguet, Machac d. Marozsan (walkover), J.M. Cerundolo d. Altmaier.'),
    dict(id='ehf-cl', publisher='EHF', url='https://ehfcl.eurohandball.com/men/2026-27/standings/',
         read_at='2026-10-26T05:15Z', role='official',
         supports='EHF Champions League group tables after five rounds and the round-six fixture list for 28 and 29 October.'),
    dict(id='f1-races', publisher='Formula 1', url='https://www.formula1.com/en/results/2026/races',
         read_at='2026-10-26T05:15Z', role='official', supports='Winner of each of the eighteen 2026 races held so far, the latest being the United States GP on 25 Oct.'),
    dict(id='f1-drivers', publisher='Formula 1', url='https://www.formula1.com/en/results/2026/drivers',
         read_at='2026-10-26T05:14Z', role='official_attempt',
         supports='Lists driver names only. The text that came back had no points column.'),
    dict(id='lvf-table', publisher='Lega Volley Femminile', url='https://www.legavolleyfemminile.it/classifica/',
         read_at='2026-10-26T05:20Z', role='official',
         supports='Serie A1 women table after round five: matches, wins, sets and rally points for every club.'),
    dict(id='icc-fixtures', publisher='ICC', url='https://www.icc-cricket.com/rankings/team-rankings/mens/t20i',
         read_at='2026-10-26T05:22Z', role='official_attempt',
         supports='The fixture strip lists NZ v IND T20 (271648), NAM v IRE ODI (275412), PAK v SL ODI (274146) and SA v AUS Test (269792). The rankings table came back as empty cells.'),
    dict(id='nba-standings', publisher='NBA', url='https://www.nba.com/standings?GroupedBy=Conference',
         read_at='2026-10-26T05:00Z', role='official_attempt',
         supports='2026-27 standings read, two to four games in. The game list for 26 Oct could not be read from nba.com/games (client-rendered) or the cdn.nba.com feeds (HTTP 500).'),
    dict(id='nba-games', publisher='NBA', url='https://www.nba.com/games?date=2026-10-26',
         read_at='2026-10-26T04:59Z', role='official_attempt',
         supports='Calendar shows 9 games on 26 Oct and 4 on 27 Oct, but the matchups were not rendered ("Sorry, something went wrong").'),
    dict(id='pga-schedule', publisher='PGA TOUR', url='https://www.pgatour.com/schedule',
         read_at='2026-10-26T05:20Z', role='official_attempt',
         supports='2026 schedule page was read, but no tournament field or player-form figures were captured, so no golf price is originated.'),
    dict(id='tauron-liga', publisher='TAURON Liga', url='https://www.tauronliga.pl/table.html',
         read_at='2026-10-26T05:22Z', role='official_attempt',
         supports='Page returned fifteen chunks of men\'s PlusLiga match tiles under the TAURON Liga (women) banner. No women\'s table was extracted.'),
]
SOURCE = {s['id']: s for s in SOURCES}

# --------------------------------------------------------------------------
# The fifteen brief sports: slug, display name, OLBG id, OLBG path, the
# official hub used, and what OLBG showed at read time.
# --------------------------------------------------------------------------
SPORTS = [
    ('ice-hockey', 'Ice Hockey', 13, 'Ice_Hockey', 'https://api-web.nhle.com/v1/schedule/2026-10-26', 'matches'),
    ('tennis', 'Tennis', 3, 'Tennis', 'https://www.atptour.com/en/scores/current', 'matches'),
    ('handball', 'Handball', 20, 'Handball', 'https://ehfcl.eurohandball.com/men/2026-27/standings/', 'matches'),
    ('baseball', 'Baseball', 12, 'Baseball', 'https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-20&endDate=2026-11-05&gameType=W&hydrate=probablePitcher,linescore', 'empty'),
    ('volleyball', 'Volleyball', 21, 'Volleyball', 'https://www.legavolleyfemminile.it/classifica/', 'matches'),
    ('motor-racing', 'Motor Racing', 14, 'Motor_Racing', 'https://www.formula1.com/en/results/2026/races', 'matches'),
    ('cricket', 'Cricket', 7, 'Cricket', 'https://www.icc-cricket.com/rankings/team-rankings/mens/t20i', 'matches'),
    ('gaelic', 'Gaelic Sports', 25, 'Gaelic_Football', 'https://www.gaa.ie/fixtures-results/', 'matches'),
    ('greyhounds', 'Greyhounds', 28, 'Greyhounds', 'https://www.gbgb.org.uk/', 'matches'),
    ('basketball', 'Basketball', 4, 'Basketball', 'https://www.nba.com/standings?GroupedBy=Conference', 'empty'),
    ('golf', 'Golf', 5, 'Golf', 'https://www.pgatour.com/schedule', 'empty'),
    ('snooker', 'Snooker', 8, 'Snooker', 'https://www.wst.tv/', 'empty'),
    ('darts', 'Darts', 15, 'Darts', 'https://www.pdc.tv/', 'outright'),
    ('rugby-union', 'Rugby Union', 9, 'Rugby_Union', 'https://www.sixnationsrugby.com/', 'outright'),
    ('rugby-league', 'Rugby League', 10, 'Rugby_League', 'https://www.nrl.com/', 'outright'),
]
SPORT_INDEX = {s[0]: dict(slug=s[0], name=s[1], olbg_id=s[2],
                          olbg_url=f'https://www.olbg.com/betting-tips/{s[3]}/{s[2]}',
                          official_url=s[4], olbg_state=s[5]) for s in SPORTS}

# --------------------------------------------------------------------------
# OLBG discovery rows: (sport, event, competition, OLBG time label, most-tipped
# selection, market, tip share, OLBG event id). OLBG time labels are US Eastern.
# --------------------------------------------------------------------------
DISCOVERY = [
    ('ice-hockey', 'Sonderjyske v Aalborg', 'Denmark Metal Ligaen', 'Today 14:30', 'Sonderjyske', 'Money Line', '4/4', 200050),
    ('ice-hockey', 'Los Angeles Kings v New York Rangers', 'NHL', 'Today 19:07', 'New York Rangers', 'Money Line', '3/3', 200101),
    ('ice-hockey', 'Frederikshavn v Odense', 'Denmark Metal Ligaen', 'Today 14:00', 'Frederikshavn -1.5', 'Puck Line', '2/2', 200058),
    ('ice-hockey', 'Toronto Maple Leafs v Calgary Flames', 'NHL', 'Today 20:37', 'Calgary +1.5', 'Puck Line', '1/1', 200103),
    ('ice-hockey', 'Detroit Red Wings v Edmonton Oilers', 'NHL', 'Today 21:37', 'Edmonton Oilers', 'Money Line', '1/1', 200102),
    ('ice-hockey', 'Kalpa v Sport', 'Finland Liiga', 'Tomorrow 12:30', 'Kalpa', 'Money Line', '2/2', 200081),
    ('ice-hockey', 'Malmo v Linkoping', 'Sweden SHL', 'Tomorrow 14:00', 'Malmo', 'Money Line', '2/2', 200082),
    ('ice-hockey', 'Frolunda v Rogle', 'Sweden SHL', 'Tomorrow 14:00', 'Frolunda', 'Money Line', '2/2', 200083),
    ('ice-hockey', 'Koln v Mannheim', 'Germany DEL', 'Tomorrow 14:00', 'Mannheim', 'Money Line', '1/1', 200100),
    ('volleyball', 'Norde v Renata', 'Brazil Superliga', 'Today 20:00', 'Norde', 'Win Match', '6/8', 37102),
    ('volleyball', 'Montes Claros v Sada Cruzeiro', 'Brazil Superliga', 'Today 18:00', 'Sada Cruzeiro', 'Win Match', '5/10', 37101),
    ('volleyball', 'Amstetten v Ried', 'Austria AVL', 'Today', 'Ried', 'Win Match', '4/5', 37116),
    ('volleyball', 'BKS Bielsko W v LKS Lodz W', 'Poland TAURON Liga', 'Today', 'LKS Lodz W', 'Win Match', '4/7', 37080),
    ('volleyball', 'UVC Graz v Waldviertel', 'Austria AVL', 'Today', 'Waldviertel', 'Win Match', '4/5', 37119),
    ('volleyball', 'Klagenfurt v Aich/Dob', 'Austria AVL', 'Today', 'Aich/Dob', 'Win Match', '3/4', 37118),
    ('volleyball', 'Sancor W v SESI Bauru W', 'Brazil Superliga W', 'Today', 'SESI Bauru W', 'Win Match', '3/5', 37004),
    ('volleyball', 'Hollabrunn v Hartberg', 'Austria AVL', 'Today', 'Hartberg 3-2', 'Set Score', '3/x', 37117),
    ('volleyball', 'Marignano W v Bergamo W', 'Italy Serie A1 W', 'Tomorrow', 'Bergamo W', 'Win Match', '2/3', 37075),
    ('volleyball', 'Opole W v Palac W', 'Poland TAURON Liga', 'Tomorrow', 'Palac W', 'Win Match', '2/4', 37081),
    ('volleyball', 'Suzano v Goias', 'Brazil Superliga', 'Tomorrow', 'Suzano', 'Win Match', '2/3', 37103),
    ('volleyball', 'Praia v Sao Jose', 'Brazil Superliga', 'Tomorrow', 'Praia', 'Win Match', '2/3', 37104),
    ('volleyball', 'Conegliano W v Vallefoglia W', 'Italy Serie A1 W', '28 Oct', 'Vallefoglia W', 'Win Match', '5/7', 37076),
    ('volleyball', 'Budowlani W v Radomka W', 'Poland TAURON Liga', '28 Oct', 'Radomka 3-0', 'Set Score', '3/x', 37082),
    ('cricket', 'New Zealand v India (3rd T20I)', 'International T20', 'Tomorrow 03:00', 'India', 'Match Winner', '14/21', 188852),
    ('cricket', 'Namibia v Ireland (3rd ODI)', 'International ODI', 'Tomorrow 03:30', 'Ireland', 'Match Winner', '11/16', 188854),
    ('cricket', 'Pakistan v Sri Lanka (ODI)', 'International ODI', 'Tomorrow 04:00', 'Pakistan', 'Match Winner', '5/9', 188868),
    ('cricket', 'Melbourne Stars W v Hobart Hurricanes W', 'WBBL', '29 Oct', 'Hobart Hurricanes W', 'Match Winner', '4/6', 188864),
    ('cricket', 'Brisbane Heat W v Sydney Sixers W', 'WBBL', '30 Oct', 'Sydney Sixers W', 'Match Winner', '3/5', 188865),
    ('cricket', 'South Africa v Australia (Test)', 'World Test Championship', '31 Oct', 'AK Markram', 'Man of the Match', '3/5', 188835),
    ('tennis', 'Badosa v Carol Young Suh Lee', 'WTA', 'Today 03:30', 'Badosa', 'Win Match', '6/7', 902300),
    ('tennis', 'Eala v Stojsavljevic', 'WTA', 'Today 04:00', 'Eala', 'Win Match', '6/9', 902175),
    ('tennis', 'Sasnovich v Bartunkova', 'WTA/ITF', 'Today', 'Bartunkova', 'Win Match', '3/6', 902306),
    ('tennis', 'Han Shi v Ibragimova', 'WTA/ITF', 'Today', 'Han Shi', 'Win Match', '3/5', 902299),
    ('tennis', 'Berrettini v Etcheverry', 'ATP Vienna', 'Today 08:30', 'Berrettini', 'Win Match', '3/4', 902208),
    ('tennis', 'Mensik v Neumayer', 'ATP Vienna', 'Today 12:30', 'Mensik', 'Win Match', '3/3', 902321),
    ('tennis', 'Fernandez v Sakatsume', 'WTA', 'Today 22:00', 'Fernandez', 'Win Match', '3/5', 902172),
    ('tennis', 'Dart v Prozorova', 'WTA/ITF', 'Today', 'Over 22.5 games', 'Total Games', '2/2', 902303),
    ('tennis', 'Kotliar v Senica', 'Challenger/ITF', 'Today', 'Kotliar', 'Win Match', '2/3', 902315),
    ('tennis', 'Machac v De Minaur', 'ATP Vienna', 'Today', 'De Minaur', 'Win Match', '2/2', 902318),
    ('tennis', 'Vergara Rivera v Gomes', 'Challenger/ITF', 'Today', 'Vergara Rivera', 'Win Match', '2/2', 902334),
    ('tennis', 'Fullana v Ayala', 'Challenger/ITF', 'Today', 'Fullana', 'Win Match', '2/2', 902339),
    ('tennis', 'Vacherot v Navone', 'ATP Basel', 'Today', 'Navone', 'Win Match', '1/2', 902237),
    ('tennis', 'Rune v Halys', 'ATP Basel', 'Today', 'Halys', 'Win Match', '1/2', 902236),
    ('tennis', 'Labrana v Ce', 'Challenger/ITF', 'Today', 'Ce', 'Win Match', '1/1', 902340),
    ('tennis', 'Fery v Fearnley', 'ATP Vienna', 'Today', 'Fearnley', 'Win Match', '1/1', 902319),
    ('tennis', 'Djokovic v Humbert', 'ATP Basel', 'Tomorrow 06:00', 'Djokovic', 'Win Match', '4/5', 902233),
    ('tennis', 'Wawrinka v Lehecka', 'ATP Basel', 'Tomorrow', 'Lehecka', 'Win Match', '4/7', 902232),
    ('tennis', 'Tagger v Venus Williams', 'WTA', 'Tomorrow', 'Venus Williams 2-0', 'Set Betting', '2/2', 902189),
    ('tennis', 'Tabilo v Jodar', 'ATP Basel', 'Tomorrow', 'Tabilo', 'Win Match', '2/4', 902238),
    ('handball', 'Magdeburg v Kriens', 'EHF Champions League', '28 Oct', 'Tie', 'Money Line', '7/11', 12136),
    ('handball', 'Kielce v Kolstad', 'EHF Champions League', '28 Oct', 'Tie', 'Money Line', '5/8', 12132),
    ('handball', 'Vardar v Melsungen', 'EHF Champions League', '28 Oct', 'Tie', 'Money Line', '4/7', 12130),
    ('handball', 'Wisla Plock v Nantes', 'EHF Champions League', '28 Oct', 'Tie', 'Money Line', '4/6', 12138),
    ('handball', 'PSG v Aalborg', 'EHF Champions League', '28 Oct', 'Tie', 'Money Line', '4/6', 12134),
    ('handball', 'Celje v Zagreb', 'EHF Champions League', '28 Oct', 'Tie', 'Money Line', '4/6', 12135),
    ('handball', 'Porto v Veszprem', 'EHF Champions League', '28 Oct', 'Tie', 'Money Line', '3/6', 12127),
    ('handball', 'Fuchse Berlin v Partizan', 'EHF Champions League', '29 Oct', 'Tie', 'Money Line', '6/11', 12128),
    ('handball', 'GOG v Sporting', 'EHF Champions League', '29 Oct', 'GOG', 'Money Line', '2/4', 12129),
    ('handball', 'Montpellier v Dinamo Bucuresti', 'EHF Champions League', '29 Oct', 'Tie', 'Money Line', '2/3', 12133),
    ('handball', 'Kristianstad v Szeged', 'EHF Champions League', '29 Oct', 'Tie', 'Money Line', '1/3', 12131),
    ('handball', 'Skanderborg v Barcelona', 'EHF Champions League', '29 Oct', 'Barcelona', 'Money Line', '1/3', 12137),
    ('handball', 'Helsingborg v Hallby', 'Sweden Handbollsligan', 'Today', 'Helsingborg', 'Money Line', '5/10', 12150),
    ('gaelic', 'Kanturk v Eire Og', 'Cork club football', '01 Nov', 'Eire Og +0.5', 'Handicap', '6/6', 3531),
    ('gaelic', 'Fr Caseys v Kildimo Pallaskenry', 'Limerick club football', '01 Nov', 'Kildimo Pallaskenry +3.5', 'Handicap', '5/7', 3537),
    ('greyhounds', '3:19 Monmore', 'GBGB', 'Today 11:19', 'Tullymurry Skies', 'Win', '1/1', 690193),
    ('motor-racing', 'Mexico City Grand Prix', 'Formula 1', '01 Nov 15:00', 'Charles Leclerc', 'Race Winner', '1/2', 914),
]

OUTRIGHTS = [
    ('rugby-union', 'Six Nations 2027', 'Ireland', '3/10', 609013),
    ('darts', 'PDC World Championship 2027 (from 3 Jan 2027)', 'Luke Littler', '22/36 (61%)', 26023),
    ('rugby-league', 'State of Origin 2027', 'New South Wales', '9/12', 2695857),
    ('rugby-league', 'Super League 2027 Grand Final', 'Wigan', '2/4', 2801554),
    ('rugby-league', 'NRL 2027 Grand Final', 'Penrith', '1/3', 2801600),
    ('gaelic', 'All-Ireland Football 2027', 'Kerry', '6/8', 3327),
]

# --------------------------------------------------------------------------
# NHL: parsed from the raw capture of api-web.nhle.com/v1/standings.
# --------------------------------------------------------------------------
NHL_NAMES = {
    'ANA': 'Anaheim Ducks', 'BOS': 'Boston Bruins', 'BUF': 'Buffalo Sabres', 'CAR': 'Carolina Hurricanes',
    'CBJ': 'Columbus Blue Jackets', 'CGY': 'Calgary Flames', 'CHI': 'Chicago Blackhawks', 'COL': 'Colorado Avalanche',
    'DAL': 'Dallas Stars', 'DET': 'Detroit Red Wings', 'EDM': 'Edmonton Oilers', 'FLA': 'Florida Panthers',
    'LAK': 'Los Angeles Kings', 'MIN': 'Minnesota Wild', 'MTL': 'Montreal Canadiens', 'NJD': 'New Jersey Devils',
    'NSH': 'Nashville Predators', 'NYI': 'New York Islanders', 'NYR': 'New York Rangers', 'OTT': 'Ottawa Senators',
    'PHI': 'Philadelphia Flyers', 'PIT': 'Pittsburgh Penguins', 'SEA': 'Seattle Kraken', 'SJS': 'San Jose Sharks',
    'STL': 'St. Louis Blues', 'TBL': 'Tampa Bay Lightning', 'TOR': 'Toronto Maple Leafs', 'UTA': 'Utah Mammoth',
    'VAN': 'Vancouver Canucks', 'VGK': 'Vegas Golden Knights', 'WPG': 'Winnipeg Jets', 'WSH': 'Washington Capitals'}


def _parse_nhl():
    table = {}
    for line in (RAW / 'nhl_standings_raw.txt').read_text().splitlines():
        if not line.strip() or line.startswith('#'):
            continue
        parts = [p.strip() for p in line.split('|')]
        head = parts[0].split()
        code = head[0]
        gp, w, l, otl, gf, ga = map(int, head[1:7])
        hrec, hgoals = parts[1].split()
        rrec, rgoals = parts[2].split()
        l10rec, l10goals = parts[3].split()
        table[code] = dict(code=code, name=NHL_NAMES[code], gp=gp, w=w, l=l, otl=otl, gf=gf, ga=ga,
                           home=hrec, home_goals=hgoals, road=rrec, road_goals=rgoals,
                           l10=l10rec, l10_goals=l10goals, streak=parts[4])
    return table


NHL = _parse_nhl()

# (game id, ET date, away, home, venue, start UTC)
NHL_GAMES = [
    (2026020185, '2026-10-26', 'LAK', 'NYR', 'Madison Square Garden', '2026-10-26T23:00Z'),
    (2026020186, '2026-10-26', 'TOR', 'CGY', 'Scotiabank Saddledome', '2026-10-27T00:30Z'),
    (2026020187, '2026-10-26', 'DET', 'EDM', 'Rogers Place', '2026-10-27T01:30Z'),
    (2026020188, '2026-10-27', 'CBJ', 'PHI', 'Xfinity Mobile Arena', '2026-10-27T23:00Z'),
    (2026020189, '2026-10-27', 'BOS', 'CAR', 'Lenovo Center', '2026-10-28T00:00Z'),
    (2026020190, '2026-10-27', 'LAK', 'CHI', 'United Center', '2026-10-28T00:00Z'),
    (2026020191, '2026-10-27', 'MTL', 'STL', 'Enterprise Center', '2026-10-28T00:00Z'),
    (2026020192, '2026-10-27', 'NYI', 'NSH', 'Bridgestone Arena', '2026-10-28T00:00Z'),
    (2026020193, '2026-10-27', 'NJD', 'DAL', 'American Airlines Center', '2026-10-28T00:00Z'),
    (2026020194, '2026-10-27', 'FLA', 'WPG', 'Canada Life Centre', '2026-10-28T00:00Z'),
    (2026020195, '2026-10-27', 'MIN', 'UTA', 'Delta Center', '2026-10-28T01:00Z'),
    (2026020196, '2026-10-27', 'OTT', 'VGK', 'T-Mobile Arena', '2026-10-28T02:00Z'),
    (2026020197, '2026-10-27', 'VAN', 'ANA', 'Honda Center', '2026-10-28T02:00Z'),
]
NHL_ON_OLBG = {2026020185: 200101, 2026020186: 200103, 2026020187: 200102}

# --------------------------------------------------------------------------
# PENNY DEL table rows read (13 of 14 clubs; Iserlohn's row was cut off).
# club: (GP, PTS, W, OTW, SOW, L, OTL, SOL, GF, GA)
# --------------------------------------------------------------------------
DEL = {
    'Eisbaeren Berlin': (12, 29, 9, 0, 1, 2, 0, 0, 44, 18),
    'Nuernberg Ice Tigers': (13, 25, 8, 0, 0, 4, 0, 1, 47, 31),
    'EHC Red Bull Muenchen': (12, 24, 7, 0, 1, 3, 1, 0, 38, 37),
    'Straubing Tigers': (12, 23, 7, 0, 1, 4, 0, 0, 46, 34),
    'Adler Mannheim': (12, 23, 7, 0, 0, 3, 1, 1, 40, 29),
    'ERC Ingolstadt': (13, 20, 5, 2, 0, 5, 0, 1, 40, 43),
    'Koelner Haie': (12, 19, 5, 1, 0, 4, 1, 1, 45, 45),
    'Grizzlys Wolfsburg': (13, 17, 3, 1, 2, 5, 2, 0, 35, 39),
    'Pinguins Bremerhaven': (12, 15, 5, 0, 0, 7, 0, 0, 24, 31),
    'Augsburger Panther': (12, 14, 4, 0, 1, 7, 0, 0, 36, 40),
    'Schwenninger Wild Wings': (13, 14, 3, 2, 0, 7, 1, 0, 31, 47),
    'Loewen Frankfurt': (12, 13, 3, 0, 1, 6, 1, 1, 25, 28),
    'Krefeld Pinguine': (12, 13, 4, 0, 0, 7, 0, 1, 29, 37),
}
DEL_POS = {'Adler Mannheim': 5, 'Koelner Haie': 7}

# --------------------------------------------------------------------------
# MLB World Series (statsapi.mlb.com)
# --------------------------------------------------------------------------
MLB = dict(
    MIL=dict(name='Milwaukee Brewers', rs=832, ra=618, w=103, l=59, era='3.51', ops='.744'),
    TB=dict(name='Tampa Bay Rays', rs=736, ra=650, w=98, l=64, era='3.70', ops='.728'),
    games=162,
    # runs scored by the eleven clubs on the first page of the team-hitting read
    partial_league_runs=[832, 736, 801, 752, 767, 850, 715, 690, 648, 742, 739],
    gasser=dict(gs=20, era='3.87', whip='1.19', ip='109.1', ra9=4.03, rec='5-5'),
    peralta=dict(gs=32, era='4.42', whip='1.33', ip='169.0', ra9=4.85, rec='10-11',
                 nym_gs=22, nym_era='4.99', tb_gs=10, tb_era='3.25', tb_rec='5-2'),
    g1='MIL 3, TB 2 (23 Oct, American Family Field)',
    g2='MIL 5, TB 4 (24 Oct, American Family Field)',
)

# --------------------------------------------------------------------------
# ATP rankings (26 Oct 2026 list). None = outside the top 150 that was read.
# --------------------------------------------------------------------------
ATP = {
    'Alex de Minaur': (10, 3280), 'Rafael Jodar': (11, 3234), 'Novak Djokovic': (12, 3090),
    'Jakub Mensik': (16, 2495), 'Learner Tien': (18, 2345), 'Jiri Lehecka': (21, 2275),
    'Luciano Darderi': (23, 2160), 'Casper Ruud': (25, 1995), 'Tomas Martin Etcheverry': (29, 1565),
    'Alejandro Tabilo': (30, 1565), 'Valentin Vacherot': (31, 1480), 'Arthur Fery': (35, 1406),
    'Matteo Arnaldi': (36, 1311), 'Ugo Humbert': (38, 1270), 'Mariano Navone': (43, 1164),
    'Quentin Halys': (45, 1127), 'Luca Van Assche': (46, 1105), 'Matteo Berrettini': (48, 1083),
    'Nuno Borges': (53, 1000), 'Juan Manuel Cerundolo': (54, 1000), 'Daniel Altmaier': (60, 874),
    'Tomas Machac': (71, 804), 'Jacob Fearnley': (86, 686),
    'Holger Rune': None, 'Lukas Neumayer': None, 'Stan Wawrinka': None, 'Dominic Stricker': None,
    'Mika Brunold': None,
}
ATP_CUTOFF_POINTS = 378   # rank 150 on the list read

# (key, event, round, court/time note, player A, player B, seeds/status note, source id, OLBG event id or None)
TENNIS = [
    ('vie-ber-etc', 'ATP 500 Vienna', 'R32', 'Mon 26 Oct, Centre Court, first match 13:30 CET',
     'Matteo Berrettini', 'Tomas Martin Etcheverry', '', 'atp-vienna-op', 902208),
    ('vie-mac-dem', 'ATP 500 Vienna', 'R32', 'Mon 26 Oct, Centre Court, second match',
     'Tomas Machac', 'Alex de Minaur', 'Machac (Q); de Minaur seeded 5', 'atp-vienna-op', 902318),
    ('vie-men-neu', 'ATP 500 Vienna', 'R32', 'Mon 26 Oct, Centre Court, not before 17:30 CET',
     'Jakub Mensik', 'Lukas Neumayer', 'Mensik seeded 8; Neumayer (Q)', 'atp-vienna-op', 902321),
    ('vie-van-tie', 'ATP 500 Vienna', 'R32', 'Mon 26 Oct, Centre Court, not before 20:00 CET',
     'Luca Van Assche', 'Learner Tien', '', 'atp-vienna-op', None),
    ('vie-fer-fea', 'ATP 500 Vienna', 'R32', 'Mon 26 Oct, Glaubandich Court, 17:30 CET',
     'Arthur Fery', 'Jacob Fearnley', 'Fearnley (Q)', 'atp-vienna-op', 902319),
    ('vie-dar-arn', 'ATP 500 Vienna', 'R32', 'Mon 26 Oct, Glaubandich Court, second match',
     'Luciano Darderi', 'Matteo Arnaldi', '', 'atp-vienna-op', None),
    ('bas-vac-nav', 'ATP 500 Basel', 'R32', 'Mon 26 Oct, Center Court, first match 13:30 CET',
     'Valentin Vacherot', 'Mariano Navone', '', 'atp-basel-op', 902237),
    ('bas-run-hal', 'ATP 500 Basel', 'R32', 'Mon 26 Oct, Center Court, second match',
     'Holger Rune', 'Quentin Halys', '', 'atp-basel-op', 902236),
    ('bas-str-ruu', 'ATP 500 Basel', 'R32', 'Mon 26 Oct, Center Court, not before 20:00 CET',
     'Dominic Stricker', 'Casper Ruud', 'Stricker (WC); Ruud seeded 9', 'atp-basel-op', None),
    ('bas-bru-bor', 'ATP 500 Basel', 'R32', 'Mon 26 Oct, IWB Court 1, not before 13:30 CET',
     'Mika Brunold', 'Nuno Borges', 'Brunold (LL)', 'atp-basel-op', None),
    ('bas-alt-cer', 'ATP 500 Basel', 'R32', 'Mon 26 Oct, IWB Court 1, second match',
     'Daniel Altmaier', 'Juan Manuel Cerundolo', 'Altmaier (LL); Cerundolo (Q)', 'atp-basel-op', None),
    ('bas-djo-hum', 'ATP 500 Basel', 'R32', 'Order of play not yet published at read time',
     'Novak Djokovic', 'Ugo Humbert', 'Djokovic seeded 4 (WC)', 'atp-basel-draw', 902233),
    ('bas-tab-jod', 'ATP 500 Basel', 'R32', 'Order of play not yet published at read time',
     'Alejandro Tabilo', 'Rafael Jodar', 'Jodar seeded 3', 'atp-basel-draw', 902238),
]

# --------------------------------------------------------------------------
# EHF Champions League group tables after five rounds:
# club: (group, GP, W, D, L, GF, GA, PTS)
# --------------------------------------------------------------------------
EHF = {
    'One Veszprem HC': ('A', 5, 5, 0, 0, 185, 146, 10), 'Fuchse Berlin': ('A', 5, 3, 0, 2, 184, 172, 6),
    'FC Porto': ('A', 5, 1, 1, 3, 158, 173, 3), 'RK Partizan': ('A', 5, 0, 1, 4, 148, 184, 1),
    'Orlen Wisla Plock': ('B', 5, 3, 0, 2, 141, 136, 6), 'MT Melsungen': ('B', 5, 3, 0, 2, 138, 138, 6),
    'HBC Nantes': ('B', 5, 3, 0, 2, 142, 143, 6), 'HC Vardar 1961': ('B', 5, 1, 0, 4, 154, 158, 2),
    'Aalborg Handbold': ('C', 5, 4, 1, 0, 170, 145, 9), 'Paris Saint-Germain': ('C', 5, 3, 1, 1, 182, 157, 7),
    'HC Zagreb': ('C', 5, 2, 0, 3, 146, 158, 4), 'RK Celje': ('C', 5, 0, 0, 5, 150, 188, 0),
    'Sporting CP': ('D', 5, 4, 1, 0, 191, 165, 9), 'GOG': ('D', 5, 3, 1, 1, 178, 172, 7),
    'OTP Bank-PICK Szeged': ('D', 5, 1, 2, 2, 172, 169, 4), 'IFK Kristianstad': ('D', 5, 0, 0, 5, 162, 197, 0),
    'Barca': ('E', 5, 5, 0, 0, 177, 138, 10), 'SAH-Aarhus': ('E', 5, 2, 1, 2, 150, 163, 5),
    'Dinamo Bucuresti': ('E', 5, 1, 1, 3, 134, 145, 3), 'Montpellier Handball': ('E', 5, 1, 0, 4, 150, 165, 2),
    'SC Magdeburg': ('F', 5, 5, 0, 0, 176, 140, 10), 'Industria Kielce': ('F', 5, 3, 0, 2, 155, 153, 6),
    'HC Kriens-Luzern': ('F', 5, 2, 0, 3, 158, 161, 4), 'Kolstad Handball': ('F', 5, 0, 0, 5, 143, 178, 0),
}
# (EHF match id, date, CET time, home, away, OLBG event id)
EHF_GAMES = [
    ('202711020101016', '2026-10-28', '18:45', 'Orlen Wisla Plock', 'HBC Nantes', 12138),
    ('202711020101004', '2026-10-28', '18:45', 'FC Porto', 'One Veszprem HC', 12127),
    ('202711020101022', '2026-10-28', '18:45', 'HC Vardar 1961', 'MT Melsungen', 12130),
    ('202711020101067', '2026-10-28', '20:45', 'Industria Kielce', 'Kolstad Handball', 12132),
    ('202711020101036', '2026-10-28', '20:45', 'RK Celje', 'HC Zagreb', 12135),
    ('202711020101065', '2026-10-28', '20:45', 'SC Magdeburg', 'HC Kriens-Luzern', 12136),
    ('202711020101026', '2026-10-28', '20:45', 'Paris Saint-Germain', 'Aalborg Handbold', 12134),
    ('202711020101046', '2026-10-29', '18:45', 'IFK Kristianstad', 'OTP Bank-PICK Szeged', 12131),
    ('202711020101040', '2026-10-29', '18:45', 'GOG', 'Sporting CP', 12129),
    ('202711020101009', '2026-10-29', '18:45', 'Fuchse Berlin', 'RK Partizan', 12128),
    ('202711020101055', '2026-10-29', '20:45', 'Montpellier Handball', 'Dinamo Bucuresti', 12133),
    ('202711020101054', '2026-10-29', '20:45', 'SAH-Aarhus', 'Barca', 12137),
]
EHF_SLUGS = {
    '202711020101016': 'OrlenWislaPlock-HBCNantes', '202711020101004': 'FCPorto-OneVeszpr%C3%A9mHC',
    '202711020101022': 'HCVardar1961-MTMelsungen', '202711020101067': 'IndustriaKielce-KolstadH%C3%A5ndball',
    '202711020101036': 'RKCeljePivovarnaLa%C5%A1ko-HCZagreb', '202711020101065': 'SCMagdeburg-HCKriensLuzern',
    '202711020101026': 'ParisSaintGermain-AalborgH%C3%A5ndbold', '202711020101046': 'IFKKristianstad-OTPBankPICKSzeged',
    '202711020101040': 'GOG-SportingClubedePortugal', '202711020101009': 'F%C3%BCchseBerlin-RKPartizanAdmiralBet',
    '202711020101055': 'MontpellierHandball-DinamoBucuresti', '202711020101054': 'SAHAarhus-Bar%C3%A7a',
}

# --------------------------------------------------------------------------
# Lega Volley Femminile Serie A1 table (after round five):
# club: (pos, PT, played, W, L, sets won, sets lost, rally points for, against)
# --------------------------------------------------------------------------
LVF = {
    'Numia Vero Volley Milano': (1, 15, 5, 5, 0, 15, 1, 400, 289),
    'Imoco Conegliano': (2, 12, 4, 4, 0, 12, 0, 304, 219),
    'Savio Vallefoglia': (3, 11, 4, 4, 0, 12, 4, 377, 351),
    "Fenera Chieri '76": (4, 11, 5, 4, 1, 12, 5, 389, 343),
    'Volley Bergamo': (5, 8, 4, 3, 1, 9, 6, 325, 320),
    'Savino Del Bene Scandicci': (6, 8, 4, 2, 2, 10, 7, 385, 352),
    'Igor Gorgonzola Novara': (7, 6, 4, 2, 2, 8, 8, 334, 339),
    'Volley Talmassons FVG': (8, 6, 5, 2, 3, 7, 10, 381, 390),
    'Il Bisonte Firenze': (9, 4, 5, 1, 4, 6, 12, 380, 412),
    'Uyba Busto Arsizio': (10, 4, 5, 1, 4, 5, 13, 370, 424),
    'Omag Consolini Volley 1907': (11, 3, 4, 1, 3, 4, 9, 289, 291),
    'CBF Balducci Macerata': (12, 3, 5, 1, 4, 6, 13, 377, 446),
    'Granda Volley Cuneo': (13, 3, 5, 1, 4, 4, 13, 343, 416),
    'Millenium Brescia': (14, 2, 5, 1, 4, 5, 14, 380, 442),
}
# (key, home, away, OLBG label, OLBG event id)
LVF_GAMES = [
    ('lvf-oma-ber', 'Omag Consolini Volley 1907', 'Volley Bergamo', 'Tomorrow (27 Oct)', 37075),
    ('lvf-con-val', 'Imoco Conegliano', 'Savio Vallefoglia', '28 Oct', 37076),
]

# --------------------------------------------------------------------------
# F1 2026 race winners (formula1.com/en/results/2026/races)
# --------------------------------------------------------------------------
F1_WINNERS = [
    ('Australia', '08 Mar', 'George Russell', 'Mercedes'), ('China', '15 Mar', 'Kimi Antonelli', 'Mercedes'),
    ('Japan', '29 Mar', 'Kimi Antonelli', 'Mercedes'), ('Miami', '03 May', 'Kimi Antonelli', 'Mercedes'),
    ('Canada', '24 May', 'Kimi Antonelli', 'Mercedes'), ('Monaco', '07 Jun', 'Kimi Antonelli', 'Mercedes'),
    ('Barcelona-Catalunya', '14 Jun', 'Lewis Hamilton', 'Ferrari'), ('Austria', '28 Jun', 'George Russell', 'Mercedes'),
    ('Great Britain', '05 Jul', 'Charles Leclerc', 'Ferrari'), ('Belgium', '19 Jul', 'Kimi Antonelli', 'Mercedes'),
    ('Hungary', '26 Jul', 'Lando Norris', 'McLaren'), ('Netherlands', '23 Aug', 'Lando Norris', 'McLaren'),
    ('Italy', '06 Sep', 'Kimi Antonelli', 'Mercedes'), ('Spain', '13 Sep', 'Kimi Antonelli', 'Mercedes'),
    ('Azerbaijan', '26 Sep', 'George Russell', 'Mercedes'), ('Bahrain', '04 Oct', 'Max Verstappen', 'Red Bull Racing'),
    ('Singapore', '11 Oct', 'Max Verstappen', 'Red Bull Racing'), ('United States', '25 Oct', 'Kimi Antonelli', 'Mercedes'),
]

# Cricket fixtures confirmed on the ICC fixture strip: (OLBG event, ICC match id, ICC path)
ICC_MATCHES = {
    188852: ('271648', 'https://www.icc-cricket.com/matches/271648/new-zealand-vs-india'),
    188854: ('275412', 'https://www.icc-cricket.com/matches/275412/namibia-vs-ireland'),
    188868: ('274146', 'https://www.icc-cricket.com/matches/274146/pakistan-vs-sri-lanka'),
    188835: ('269792', 'https://www.icc-cricket.com/tournaments/world-test-championship/matches/269792/south-africa-vs-australia'),
}
