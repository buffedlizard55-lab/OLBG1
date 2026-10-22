"""Explicit scope, publisher identity, retention, and market investigation policy."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / 'data' / 'current'
SCHEMA_VERSION = 1
FIXTURE_TTL_HOURS = 6
STATS_TTL_HOURS = 24
HORIZON_DAYS = 7

# This is a project scope, not a claim to have enumerated all OLBG competitions.
SPORTS = [
    ('tennis', 'Tennis', 3, 'Tennis', 'https://www.atptour.com/en/scores/current'),
    ('basketball', 'Basketball', 4, 'Basketball', 'https://www.nba.com/games'),
    ('golf', 'Golf', 5, 'Golf', 'https://www.pgatour.com/schedule'),
    ('cricket', 'Cricket', 7, 'Cricket', 'https://www.icc-cricket.com/fixtures-results'),
    ('snooker', 'Snooker', 8, 'Snooker', 'https://www.wst.tv/matches/'),
    ('rugby-union', 'Rugby Union', 9, 'Rugby_Union', 'https://top14.lnr.fr/calendrier-et-resultats'),
    ('rugby-league', 'Rugby League', 10, 'Rugby_League', 'https://www.intrl.sport/fixtures-results'),
    ('baseball', 'Baseball', 12, 'Baseball', 'https://www.mlb.com/schedule'),
    ('ice-hockey', 'Ice Hockey', 13, 'Ice_Hockey', 'https://www.nhl.com/schedule'),
    ('motor-racing', 'Motor Racing', 14, 'Motor_Racing', 'https://www.formula1.com/en/racing/2026'),
    ('darts', 'Darts', 15, 'Darts', 'https://www.pdc.tv/tournaments'),
    ('handball', 'Handball', 20, 'Handball', 'https://ehfcl.eurohandball.com/men/'),
    ('volleyball', 'Volleyball', 21, 'Volleyball', 'https://www.plusliga.pl/games.html'),
    ('aussie-rules', 'Aussie Rules', 22, 'Aussie_Rules', 'https://www.afl.com.au/aflw/fixture'),
    ('esports', 'eSports', 23, 'eSports', 'https://lolesports.com/en-US/schedule'),
    ('gaelic-football', 'Gaelic Football', 25, 'Gaelic_Football', 'https://munster.gaa.ie/fixtures/events-calendar/'),
    ('greyhounds', 'Greyhounds', 28, 'Greyhounds', 'https://www.gbgb.org.uk/racing/open-races/'),
]
SPORT_INDEX = {x[0]: {'slug': x[0], 'name': x[1], 'olbg_id': x[2],
                         'olbg_url': f'https://www.olbg.com/betting-tips/{x[3]}/{x[2]}',
                         'official_url': x[4]} for x in SPORTS}
EXCLUDED_IDS = {1, 2, 11, 16, 17, 18, 26}
EXCLUDED_NAMES = {'soccer', 'football', 'association-football', 'american-football',
                  'boxing', 'ufc', 'mma', 'mixed-martial-arts', 'hurling',
                  'horse-racing', 'cycling', 'specials', 'entertainment'}

# Exact host comparison, not string matching or arbitrary subdomains.
PUBLISHERS = {
    'api-web.nhle.com': 'NHL', 'www.nhl.com': 'NHL',
    'statsapi.mlb.com': 'MLB', 'www.mlb.com': 'MLB',
    'www.nba.com': 'NBA', 'cdn.nba.com': 'NBA',
    'www.euroleaguebasketball.net': 'Euroleague Basketball',
    'api-live.euroleague.net': 'Euroleague Basketball',
    'www.protennislive.com': 'ATP draw service', 'www.atptour.com': 'ATP',
    'wtafiles.wtatennis.com': 'WTA', 'www.wtatennis.com': 'WTA',
    'www.wst.tv': 'World Snooker Tour', 'www.pdc.tv': 'Professional Darts Corporation',
    'www.eurohandball.com': 'European Handball Federation', 'ehfcl.eurohandball.com': 'EHF',
    'www.pcb.com.pk': 'Pakistan Cricket Board', 'www.icc-cricket.com': 'ICC',
    'www.nzc.nz': 'New Zealand Cricket', 'scoring.nzc.nz': 'New Zealand Cricket',
    'cricketireland.ie': 'Cricket Ireland', 'www.ecb.co.uk': 'ECB',
    'top14.lnr.fr': 'Ligue Nationale de Rugby', 'prod2.lnr.fr': 'LNR',
    'www.intrl.sport': 'International Rugby League', 'www.nrl.com': 'NRL',
    'www.afl.com.au': 'Australian Football League',
    'www.plusliga.pl': 'Polish professional volleyball league',
    'www.tauronliga.pl': 'Polish professional volleyball league',
    'www.legavolley.it': 'Lega Pallavolo Serie A',
    'www.formula1.com': 'Formula 1', 'lolesports.com': 'Riot Games / LoL Esports',
    'www.pgatour.com': 'PGA TOUR', 'www.europeantour.com': 'European Tour',
    'www.lpga.com': 'LPGA', 'www.gbgb.org.uk': 'Greyhound Board of Great Britain',
    'munster.gaa.ie': 'Munster GAA', 'gaacork.ie': 'Cork GAA',
    'www.waterfordgaa.ie': 'Waterford GAA', 'www.maighcuilinn.com': 'Maigh Cuilinn GAA',
    'www.unitedrugby.com': 'United Rugby Championship', 'stats.unitedrugby.com': 'URC',
}
DISCOVERY_HOSTS = {'www.olbg.com', 'olbg.com'}

# Investigation inventory, NOT an assertion that bookmakers offer these markets.
MARKET_REQUIREMENTS = {
    'winner': 'Both participants, exact future start, compatible current records, explicit settlement scope.',
    'handicap': 'Verified score distributions, units and format, handicap value, push and overtime rules.',
    'total': 'Verified scoring data for both sides, format and period, total line, overtime and push rules.',
    'team-total': 'Team-level scoring histories and opposition-adjusted distribution; settlement rules.',
    'period': 'Period-by-period official results, format and period-specific model.',
    'correct-score': 'A normalized joint score distribution with a finite format or an explicit tail.',
    'player-prop': 'Confirmed player identity/availability, official player game logs and prop definition.',
    'outright': 'Complete confirmed field, withdrawals, calibrated multi-runner model, dead-heat rules.',
    'placement': 'Complete field, places paid, dead-heat/each-way settlement and finishing model.',
}
SPORT_MARKETS = {
    'tennis': ['winner', 'handicap', 'total', 'period', 'correct-score', 'player-prop'],
    'basketball': ['winner', 'handicap', 'total', 'team-total', 'period', 'player-prop'],
    'golf': ['winner', 'handicap', 'total', 'outright', 'placement'],
    'cricket': ['winner', 'handicap', 'total', 'team-total', 'period', 'player-prop'],
    'snooker': ['winner', 'handicap', 'total', 'correct-score', 'period', 'player-prop'],
    'rugby-union': ['winner', 'handicap', 'total', 'team-total', 'period', 'player-prop'],
    'rugby-league': ['winner', 'handicap', 'total', 'team-total', 'period', 'player-prop'],
    'baseball': ['winner', 'handicap', 'total', 'team-total', 'period', 'player-prop'],
    'ice-hockey': ['winner', 'handicap', 'total', 'team-total', 'period', 'player-prop'],
    'motor-racing': ['winner', 'outright', 'placement', 'handicap', 'player-prop'],
    'darts': ['winner', 'handicap', 'total', 'correct-score', 'period', 'player-prop'],
    'handball': ['winner', 'handicap', 'total', 'team-total', 'period', 'player-prop'],
    'volleyball': ['winner', 'handicap', 'total', 'team-total', 'period', 'correct-score'],
    'aussie-rules': ['winner', 'handicap', 'total', 'team-total', 'period', 'player-prop'],
    'esports': ['winner', 'handicap', 'total', 'period', 'correct-score', 'player-prop'],
    'gaelic-football': ['winner', 'handicap', 'total', 'team-total', 'period', 'player-prop'],
    'greyhounds': ['winner', 'outright', 'placement', 'correct-score', 'handicap'],
}
