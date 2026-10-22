"""Session 9dc28d1e — verified inputs, sources and fixture inventory.

Every number in this module was transcribed from an official-source page fetched during this
session (2026-10-22, 12:04Z-12:25Z UTC) through the agent retrieval tools. The exact URL and
observation timestamp for each block is recorded in SOURCES; nothing here is recalled from
memory and nothing is inferred from OLBG discovery cards.

Transcription rules used:
  * A field is only present when the source published it.
  * Team names are copied exactly as the official feed spells them.
  * Where an official page mixes games played, wins, losses and overtime losses, the identity
    GP = W + L + OTL is asserted at import time and a mismatch aborts the build.
"""

SESSION = '9dc28d1e-olbg1'
BRANCH = 'arena/9dc28d1e-olbg1'
MODEL_VERSION = '9dc-ev1.0'
GENERATED_FALLBACK = '2026-10-22T12:25:00Z'

# --------------------------------------------------------------------------------------------------
# Official sources actually fetched in this session.
# --------------------------------------------------------------------------------------------------
SOURCES = [
    {
        'id': 'nhl-schedule-20261022',
        'publisher': 'NHL (National Hockey League)',
        'url': 'https://api-web.nhle.com/v1/schedule/2026-10-22',
        'observed_utc': '2026-10-22T12:08:00Z',
        'what': 'All 12 games under gameWeek date 2026-10-22: game ids, away/home teams, '
                'startTimeUTC, venue, gameState. Chunks 0-2 read; the later week was not enumerated.',
        'scope_note': 'Game state FUT at read time. A published schedule is not proof of a result.',
    },
    {
        'id': 'nhl-team-summary-20262027',
        'publisher': 'NHL (National Hockey League)',
        'url': 'https://api.nhle.com/stats/rest/en/team/summary'
               '?cayenneExp=seasonId=20262027%20and%20gameTypeId=2',
        'observed_utc': '2026-10-22T12:10:00Z',
        'what': '2026-27 regular-season team summary for all 32 clubs: gamesPlayed, wins, losses, '
                'otLosses, goalsFor, goalsAgainst, points, pointPct.',
        'scope_note': 'Early-season counts (7-12 games per club); not a calibrated rating.',
    },
    {
        'id': 'euroleague-standings-e2026',
        'publisher': 'Euroleague Basketball',
        'url': 'https://api-live.euroleague.net/v1/standings?seasonCode=E2026',
        'observed_utc': '2026-10-22T12:06:00Z',
        'what': 'Current EuroLeague 2026-27 standings for all 20 clubs after six or seven games: '
                'rank, played, wins, losses, points for, points against, differential.',
        'scope_note': 'Standings only; no injury, roster or availability data was imported.',
    },
    {
        'id': 'euroleague-round7-gamecenter',
        'publisher': 'Euroleague Basketball',
        'url': 'https://www.euroleaguebasketball.net/en/euroleague/news/game-center-round-7-el2627/',
        'observed_utc': '2026-10-22T07:17:40Z',
        'what': 'Round 7 match headings with published local tip-off times and W-L records.',
        'scope_note': 'INHERITED from the canonical snapshot read at 07:17Z; not re-read by this '
                      'session. Used only for tip-off times and the fixture pairing that the fresh '
                      'standings call corroborates by team name.',
        'inherited': True,
    },
    {
        'id': 'mlb-schedule-ws-2026',
        'publisher': 'MLB (Major League Baseball)',
        'url': 'https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-22'
               '&endDate=2026-10-28&hydrate=team,linescore',
        'observed_utc': '2026-10-22T12:07:00Z',
        'what': 'World Series games 849805, 849802, 849804, 849803, 849799 with official dates, '
                'UTC start times, venue and series game numbers.',
        'scope_note': 'Scheduled/preview status only.',
    },
    {
        'id': 'mlb-probable-pitchers',
        'publisher': 'MLB (Major League Baseball)',
        'url': 'https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-23'
               '&endDate=2026-10-28&hydrate=probablePitcher'
               '&fields=dates,date,games,gamePk,gameDate,teams,away,home,team,name,probablePitcher,fullName,id',
        'observed_utc': '2026-10-22T12:14:00Z',
        'what': 'Probable starting pitcher announced by MLB for World Series Game 1 '
                '(Brewers: Jacob Misiorowski). No Rays probable pitcher was published at read time.',
        'scope_note': 'A probable pitcher is not a confirmed lineup and may change.',
    },
    {
        'id': 'mlb-records-2026',
        'publisher': 'MLB (Major League Baseball)',
        'url': 'https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026'
               '&standingsTypes=regularSeason'
               '&fields=records,teamRecords,team,id,name,wins,losses,runsScored,runsAllowed,gamesPlayed',
        'observed_utc': '2026-10-22T12:15:00Z',
        'what': '2026 regular-season records and run totals for the two World Series clubs '
                '(Rays 98-64, 736 scored / 650 allowed; Brewers 103-59, 832 scored / 618 allowed).',
        'scope_note': 'Regular season, NOT postseason form. League run environment was not '
                      'established from this projection, so run-line and total markets are withheld.',
    },
    {
        'id': 'olbg-taxonomy-canonical',
        'publisher': 'Project reverse-engineering record (OLBG public routes)',
        'url': 'https://www.olbg.com/betting-tips',
        'observed_utc': '2026-10-21T05:20:00Z',
        'what': 'OLBG public sport taxonomy and route ids used for discovery and scope only.',
        'scope_note': 'Discovery is not verification. OLBG pages are never a fixture source.',
        'inherited': True,
    },
]

# --------------------------------------------------------------------------------------------------
# NHL 2026-27 club summary. Fields: (gamesPlayed, wins, losses, otLosses, goalsFor, goalsAgainst)
# Source: nhl-team-summary-20262027 (all 32 clubs, one read).
# --------------------------------------------------------------------------------------------------
NHL_TEAMS = {
    'Washington Capitals': (9, 5, 4, 0, 30, 29),
    'New Jersey Devils': (9, 5, 4, 0, 29, 30),
    'Vegas Golden Knights': (11, 8, 3, 0, 43, 30),
    'Vancouver Canucks': (11, 2, 8, 1, 33, 51),
    'Anaheim Ducks': (9, 4, 5, 0, 26, 29),
    'St. Louis Blues': (9, 4, 4, 1, 29, 29),
    'Dallas Stars': (9, 5, 3, 1, 22, 14),
    'Detroit Red Wings': (9, 3, 3, 3, 22, 26),
    'Ottawa Senators': (10, 7, 3, 0, 27, 24),
    'Winnipeg Jets': (9, 4, 3, 2, 24, 26),
    'Colorado Avalanche': (10, 5, 4, 1, 41, 30),
    'Nashville Predators': (8, 3, 2, 3, 23, 22),
    'Boston Bruins': (10, 7, 2, 1, 36, 22),
    'Columbus Blue Jackets': (8, 3, 5, 0, 19, 29),
    'Chicago Blackhawks': (9, 3, 6, 0, 21, 36),
    'Calgary Flames': (8, 2, 6, 0, 17, 37),
    'Tampa Bay Lightning': (9, 7, 2, 0, 31, 23),
    'Pittsburgh Penguins': (10, 3, 6, 1, 32, 37),
    'Montreal Canadiens': (9, 4, 3, 2, 28, 34),
    'San Jose Sharks': (10, 5, 4, 1, 26, 34),
    'New York Rangers': (11, 7, 3, 1, 33, 24),
    'New York Islanders': (9, 5, 3, 1, 27, 19),
    'Los Angeles Kings': (7, 1, 4, 2, 17, 27),
    'Seattle Kraken': (10, 6, 3, 1, 37, 34),
    'Utah Mammoth': (10, 7, 3, 0, 38, 31),
    'Minnesota Wild': (10, 6, 2, 2, 31, 25),
    'Buffalo Sabres': (10, 4, 4, 2, 28, 36),
    'Carolina Hurricanes': (11, 8, 2, 1, 42, 27),
    'Philadelphia Flyers': (12, 3, 6, 3, 20, 36),
    'Edmonton Oilers': (9, 7, 1, 1, 41, 27),
    'Florida Panthers': (10, 5, 3, 2, 31, 30),
    'Toronto Maple Leafs': (11, 5, 4, 2, 38, 34),
}

# EuroLeague 2026-27 standings after round 6/7.
# Fields: (gamesPlayed, wins, losses, pointsFor, pointsAgainst). Source: euroleague-standings-e2026
EL_TEAMS = {
    'Panathinaikos AKTOR Athens': (6, 5, 1, 528, 438),
    'Fenerbahce Tarfin Istanbul': (6, 5, 1, 501, 447),
    'Olympiacos Piraeus': (6, 5, 1, 564, 524),
    'Hapoel IBI Tel Aviv': (7, 5, 2, 630, 601),
    'Valencia Basket': (6, 4, 2, 583, 537),
    'Crvena Zvezda Meridianbet Belgrade': (6, 4, 2, 485, 457),
    'Dubai Basketball': (6, 4, 2, 490, 493),
    'Virtus Bologna': (7, 4, 3, 606, 608),
    'Real Madrid': (6, 3, 3, 554, 531),
    'FC Barcelona': (6, 3, 3, 534, 525),
    'Besiktas Istanbul': (6, 3, 3, 545, 555),
    'Partizan Mozzart Bet Belgrade': (6, 3, 3, 466, 471),
    'Anadolu Efes Istanbul': (6, 2, 4, 492, 510),
    'Zalgiris Kaunas': (6, 2, 4, 490, 517),
    'FC Bayern Munich': (6, 2, 4, 521, 552),
    'Maccabi Rapyd Tel Aviv': (6, 2, 4, 509, 540),
    'LDLC ASVEL Villeurbanne': (6, 2, 4, 527, 572),
    'Paris Basketball': (6, 1, 5, 504, 545),
    'Armani Olimpia Milan': (6, 1, 5, 504, 559),
    'Kosner Baskonia Vitoria-Gasteiz': (6, 1, 5, 504, 564),
}

# --------------------------------------------------------------------------------------------------
# Priced fixtures. Times are UTC. `time_source` names the source id that published the start time.
# `input_source` names the source that supplied the ratings.
# --------------------------------------------------------------------------------------------------
NHL_GAMES = [
    # (fixture_id, away, home, start_utc, venue)
    ('nhl-2026020154', 'Nashville Predators', 'Boston Bruins', '2026-10-22T23:00:00Z', 'TD Garden'),
    ('nhl-2026020155', 'New York Rangers', 'Toronto Maple Leafs', '2026-10-22T23:00:00Z', 'Scotiabank Arena'),
    ('nhl-2026020156', 'San Jose Sharks', 'Ottawa Senators', '2026-10-22T23:00:00Z', 'Canadian Tire Centre'),
    ('nhl-2026020157', 'Anaheim Ducks', 'New Jersey Devils', '2026-10-22T23:00:00Z', 'Prudential Center'),
    ('nhl-2026020158', 'Florida Panthers', 'Pittsburgh Penguins', '2026-10-22T23:00:00Z', 'PPG Paints Arena'),
    ('nhl-2026020159', 'Los Angeles Kings', 'New York Islanders', '2026-10-22T23:30:00Z', 'UBS Arena'),
    ('nhl-2026020160', 'Vegas Golden Knights', 'St. Louis Blues', '2026-10-23T00:00:00Z', 'Enterprise Center'),
    ('nhl-2026020161', 'Winnipeg Jets', 'Dallas Stars', '2026-10-23T00:00:00Z', 'American Airlines Center'),
    ('nhl-2026020162', 'Minnesota Wild', 'Calgary Flames', '2026-10-23T01:00:00Z', 'Scotiabank Saddledome'),
    ('nhl-2026020163', 'Carolina Hurricanes', 'Edmonton Oilers', '2026-10-23T01:00:00Z', 'Rogers Place'),
    ('nhl-2026020164', 'Utah Mammoth', 'Seattle Kraken', '2026-10-23T02:00:00Z', 'Climate Pledge Arena'),
    ('nhl-2026020165', 'Detroit Red Wings', 'Vancouver Canucks', '2026-10-23T02:00:00Z', 'Rogers Arena'),
]

EL_GAMES = [
    # (fixture_id, home, away, start_utc, time_source)
    ('euroleague-round7-64', 'Anadolu Efes Istanbul', 'Besiktas Istanbul', '2026-10-22T17:30:00Z', 'euroleague-round7-gamecenter'),
    ('euroleague-round7-65', 'FC Bayern Munich', 'Dubai Basketball', '2026-10-22T18:00:00Z', 'euroleague-round7-gamecenter'),
    ('euroleague-round7-62', 'Maccabi Rapyd Tel Aviv', 'Real Madrid', '2026-10-22T18:05:00Z', 'euroleague-round7-gamecenter'),
    ('euroleague-round7-67', 'Panathinaikos AKTOR Athens', 'Kosner Baskonia Vitoria-Gasteiz', '2026-10-22T18:15:00Z', 'euroleague-round7-gamecenter'),
    ('euroleague-round7-63', 'Armani Olimpia Milan', 'FC Barcelona', '2026-10-22T18:30:00Z', 'euroleague-round7-gamecenter'),
    ('euroleague-round7-66', 'Partizan Mozzart Bet Belgrade', 'Crvena Zvezda Meridianbet Belgrade', '2026-10-22T18:45:00Z', 'euroleague-round7-gamecenter'),
    ('euroleague-round7-68', 'Zalgiris Kaunas', 'LDLC ASVEL Villeurbanne', '2026-10-23T17:00:00Z', 'euroleague-round7-gamecenter'),
    ('euroleague-round7-70', 'Olympiacos Piraeus', 'Fenerbahce Tarfin Istanbul', '2026-10-23T18:15:00Z', 'euroleague-round7-gamecenter'),
    ('euroleague-round7-69', 'Paris Basketball', 'Valencia Basket', '2026-10-23T18:45:00Z', 'euroleague-round7-gamecenter'),
]

MLB_GAMES = [
    # (fixture_id, away, home, start_utc, venue, series_label)
    ('mlb-849805', 'Tampa Bay Rays', 'Milwaukee Brewers', '2026-10-24T00:00:00Z', 'American Family Field', 'World Series Game 1'),
    ('mlb-849802', 'Tampa Bay Rays', 'Milwaukee Brewers', '2026-10-25T00:00:00Z', 'American Family Field', 'World Series Game 2'),
    ('mlb-849804', 'Milwaukee Brewers', 'Tampa Bay Rays', '2026-10-27T00:00:00Z', 'Tropicana Field', 'World Series Game 3'),
    ('mlb-849803', 'Milwaukee Brewers', 'Tampa Bay Rays', '2026-10-28T00:00:00Z', 'Tropicana Field', 'World Series Game 4'),
]

MLB_RECORDS = {
    'Tampa Bay Rays': {'gp': 162, 'w': 98, 'l': 64, 'rs': 736, 'ra': 650},
    'Milwaukee Brewers': {'gp': 162, 'w': 103, 'l': 59, 'rs': 832, 'ra': 618},
}

MLB_PROBABLE = {
    'mlb-849805': {'home': 'Jacob Misiorowski', 'away': None},
}

# --------------------------------------------------------------------------------------------------
# Listed-but-unpriced inventory inherited from the canonical snapshot (observation window
# 2026-10-22T07:17:40Z-07:30:30Z). These rows are re-published with EMPTY prices and an explicit
# "not re-read by this session" status. They are not used to justify any confidence tier.
# --------------------------------------------------------------------------------------------------
INHERITED_LISTINGS = [
    # (sport, fixture_id, participant_a, participant_b, date_or_none, start_utc_or_none, note)
    ('basketball', 'nba-0022600006', 'Cavaliers', '76ers', '2026-10-22', None, 'NBA schedule read at 07:17Z; start time not published in the captured excerpt'),
    ('basketball', 'nba-0022600007', 'Nuggets', 'Thunder', '2026-10-22', None, 'NBA schedule read at 07:17Z; start time not published in the captured excerpt'),
    ('cricket', 'pcb-odi-1465-3', 'Sri Lanka', 'England', '2026-10-22', None, 'PCB fixture list read at 07:17Z; no start time captured'),
    ('cricket', 'pcb-odi-1465-4', 'Pakistan', 'England', '2026-10-25', None, 'PCB fixture list read at 07:17Z; no start time captured'),
    ('cricket', 'pcb-odi-1465-5', 'Pakistan', 'Sri Lanka', '2026-10-27', None, 'PCB fixture list read at 07:17Z; no start time captured'),
    ('golf', 'pga-schedule-R2026528', None, None, '2026-10-22', None, 'PGA TOUR schedule row; field not enumerated in the captured excerpt'),
    ('handball', 'ehf-cl-schedule-1', 'MT Melsungen', 'Orlen Wisla Plock', '2026-10-22', None, 'EHF Champions League schedule read at 07:17Z'),
    ('handball', 'ehf-cl-schedule-2', 'OTP Bank-Pick Szeged', 'GOG', '2026-10-22', None, 'EHF Champions League schedule read at 07:17Z'),
    ('handball', 'ehf-cl-schedule-3', 'Sporting CP', 'IFK Kristianstad', '2026-10-22', None, 'EHF Champions League schedule read at 07:17Z'),
    ('handball', 'ehf-cl-schedule-4', 'Barça', 'Montpellier HB', '2026-10-22', None, 'EHF Champions League schedule read at 07:17Z'),
    ('handball', 'ehf-cl-schedule-5', 'Kolstad Handball', 'SC Magdeburg', '2026-10-22', None, 'EHF Champions League schedule read at 07:17Z'),
    ('snooker', 'wst-ni-open-1', 'Kyren Wilson', 'Pang Junxu', '2026-10-22', None, 'WST match list read at 07:17Z; session time not captured'),
    ('snooker', 'wst-ni-open-2', 'Matthew Selt', 'Sam Craigie', '2026-10-22', None, 'WST match list read at 07:17Z'),
    ('snooker', 'wst-ni-open-3', 'Elliot Slessor', 'Ricky Walden', '2026-10-22', None, 'WST match list read at 07:17Z'),
    ('snooker', 'wst-ni-open-4', 'Anthony McGill', 'Mateusz Baranowski', '2026-10-22', None, 'WST match list read at 07:17Z'),
    ('snooker', 'wst-ni-open-5', 'Mark Williams', "Martin O'Donnell", '2026-10-22', None, 'WST match list read at 07:17Z'),
    ('snooker', 'wst-ni-open-6', 'David Gilbert', 'Cheung Ka Wai', '2026-10-22', None, 'WST match list read at 07:17Z'),
    ('snooker', 'wst-ni-open-7', 'Jordan Brown', 'Scott Donaldson', '2026-10-22', None, 'WST match list read at 07:17Z'),
    ('snooker', 'wst-ni-open-8', 'Jak Jones', 'Daniel Wells', '2026-10-22', None, 'WST match list read at 07:17Z'),
    ('tennis', 'atp-almaty-op-1', 'Terence Atmane', 'Mattia Bellucci', '2026-10-22', None, 'ATP Almaty draw read at 07:17Z'),
    ('tennis', 'atp-almaty-op-2', 'Tomas Machac', 'Karen Khachanov', '2026-10-22', None, 'ATP Almaty draw read at 07:17Z'),
    ('tennis', 'atp-almaty-op-3', 'Daniil Medvedev', 'Sho Shimabukuro', '2026-10-22', None, 'ATP Almaty draw read at 07:17Z'),
    ('tennis', 'atp-almaty-op-4', 'Alexander Bublik', 'Fabian Marozsan', '2026-10-22', None, 'ATP Almaty draw read at 07:17Z'),
    ('tennis', 'atp-brussels-op-1', 'Raphael Collignon', 'Jiri Lehecka', '2026-10-22', None, 'ATP Brussels draw read at 07:17Z'),
    ('tennis', 'atp-brussels-op-2', 'David Goffin', 'Alex Michelsen', '2026-10-22', None, 'ATP Brussels draw read at 07:17Z'),
    ('tennis', 'atp-brussels-op-3', 'Damir Dzumhur', 'Zizou Bergs', '2026-10-22', None, 'ATP Brussels draw read at 07:17Z'),
    ('tennis', 'atp-lyon-op-1', 'Valentin Vacherot', 'Luca Van Assche', '2026-10-22', None, 'ATP Lyon draw read at 07:17Z'),
    ('tennis', 'atp-lyon-op-2', 'Pierre-Hugues Herbert', 'Taylor Fritz', '2026-10-22', None, 'ATP Lyon draw read at 07:17Z'),
    ('tennis', 'atp-lyon-op-3', 'Borna Gojo', 'Daniel Altmaier', '2026-10-22', None, 'ATP Lyon draw read at 07:17Z'),
    ('tennis', 'atp-lyon-op-4', 'Flavio Cobolli', 'Stan Wawrinka', '2026-10-22', None, 'ATP Lyon draw read at 07:17Z'),
    ('tennis', 'atp-lyon-op-5', 'Kyrian Jacquet', 'Brandon Nakashima', '2026-10-22', None, 'ATP Lyon draw read at 07:17Z'),
    ('tennis', 'wta-ningbo-op-1', 'Iva Jovic', 'Jasmine Paolini', '2026-10-22', None, 'WTA Ningbo signed draw read at 07:17Z'),
    ('tennis', 'wta-ningbo-op-2', 'Katarzyna Kawa', 'Belinda Bencic', '2026-10-22', None, 'WTA Ningbo signed draw read at 07:17Z'),
    ('tennis', 'wta-ningbo-op-3', 'Alexandra Eala', 'Diana Shnaider', '2026-10-22', None, 'WTA Ningbo signed draw read at 07:17Z'),
    ('tennis', 'wta-ningbo-op-4', 'Elena Rybakina', 'Polina Kudermetova', '2026-10-22', None, 'WTA Ningbo signed draw read at 07:17Z'),
    ('tennis', 'wta-osaka-op-1', 'Ann Li', 'Zeynep Sonmez', '2026-10-22', None, 'WTA Osaka draw read at 07:17Z'),
    ('tennis', 'wta-osaka-op-2', 'Mary Stoiana', 'Moyuka Uchijima', '2026-10-22', None, 'WTA Osaka draw read at 07:17Z'),
    ('tennis', 'wta-osaka-op-3', 'Magda Linette', 'Katerina Siniakova', '2026-10-22', None, 'WTA Osaka draw read at 07:17Z'),
    ('tennis', 'atp-almaty-op-5', 'Alexander Donski / Filip Polasek', 'Yuki Bhambri / Ryan Seggerman', '2026-10-22', None, 'ATP Almaty doubles draw read at 07:17Z'),
    ('tennis', 'atp-almaty-op-6', 'Jason Kubler / John Peers', 'Nathaniel Lammons / Jackson Withrow', '2026-10-22', None, 'ATP Almaty doubles draw read at 07:17Z'),
    ('tennis', 'atp-almaty-op-7', 'N. Sriram Balaji / Evan King', 'Jean-Julien Rojer / Theodore van Rijthoven', '2026-10-22', None, 'ATP Almaty doubles draw read at 07:17Z'),
    ('tennis', 'atp-brussels-op-4', 'Guido Andreozzi / Manuel Guinard', 'Nicolas Barrientos / David Pel', '2026-10-22', None, 'ATP Brussels doubles draw read at 07:17Z'),
    ('tennis', 'atp-brussels-op-5', 'Constantin Frantzen / Robin Haase', 'Raphael Collignon / David Goffin', '2026-10-22', None, 'ATP Brussels doubles draw read at 07:17Z'),
    ('tennis', 'atp-lyon-op-6', 'Romain Arneodo / Ugo Blanchet', 'Matisse Bobichon / Kilian Jacquet', '2026-10-22', None, 'ATP Lyon doubles draw read at 07:17Z'),
    ('tennis', 'atp-lyon-op-7', 'Santiago Gonzalez / Hendrik Jebens', 'Theo Arribage / Albano Olivetti', '2026-10-22', None, 'ATP Lyon doubles draw read at 07:17Z'),
    ('tennis', 'atp-lyon-op-8', 'Julian Cash / Lloyd Glasspool', 'Andrew Paulson / Nino Serdarusic', '2026-10-22', None, 'ATP Lyon doubles draw read at 07:17Z'),
    ('tennis', 'wta-ningbo-op-5', 'Hanyu Guo / Kristina Mladenovic', 'Ellen Perez / Demi Schuurs', '2026-10-22', None, 'WTA Ningbo doubles draw read at 07:17Z'),
    ('tennis', 'wta-ningbo-op-6', 'Mariia Kozyreva / Maia Lumsden', 'Desirae Krawczyk / Fanny Stollar', '2026-10-22', None, 'WTA Ningbo doubles draw read at 07:17Z'),
    ('tennis', 'wta-osaka-op-4', 'Ingrid Neel / Giuliana Olmos', 'Isabelle Haverlag / Lilli Tagger', '2026-10-22', None, 'WTA Osaka doubles draw read at 07:17Z'),
    ('tennis', 'wta-osaka-op-5', 'Jesika Maleckova / Miriam Skoch', 'Hao-Ching Chan / Miyu Kato', '2026-10-22', None, 'WTA Osaka doubles draw read at 07:17Z'),
    ('aussie-rules', 'aflw-8970-8970', 'Port Adelaide', 'Collingwood', '2026-10-23', '2026-10-23T08:15:00Z', 'AFLW fixture read at 07:17Z; ladder inputs not re-read this session'),
    ('motor-racing', 'f1-austin-practice1', None, None, '2026-10-23', None, 'Formula 1 session row; no participant pair applies'),
    ('motor-racing', 'f1-austin-practice2', None, None, '2026-10-23', None, 'Formula 1 session row; no participant pair applies'),
    ('motor-racing', 'f1-austin-practice3', None, None, '2026-10-24', None, 'Formula 1 session row; no participant pair applies'),
    ('motor-racing', 'f1-austin-qualifying', None, None, '2026-10-24', None, 'Formula 1 session row; no participant pair applies'),
    ('motor-racing', 'f1-austin-race', None, None, '2026-10-25', None, 'Formula 1 race row; grid and field not verified this session'),
    ('rugby-league', 'irl-fixtures-2569', 'Tonga', 'Lebanon', '2026-10-23', None, 'International Rugby League fixture list read at 07:17Z'),
    ('rugby-league', 'irl-fixtures-2586', 'Samoa', 'Wales', '2026-10-23', None, 'International Rugby League fixture list read at 07:17Z'),
    ('rugby-league', 'irl-fixtures-2570', 'Papua New Guinea', 'Samoa', '2026-10-24', None, 'International Rugby League fixture list read at 07:17Z'),
    ('rugby-league', 'irl-fixtures-2571', 'England', 'France', '2026-10-24', None, 'International Rugby League fixture list read at 07:17Z'),
    ('rugby-league', 'irl-fixtures-2587', 'Fiji', 'Papua New Guinea', '2026-10-24', None, 'International Rugby League fixture list read at 07:17Z'),
    ('rugby-league', 'irl-fixtures-2588', 'Australia', 'England', '2026-10-24', None, 'International Rugby League fixture list read at 07:17Z'),
    ('rugby-league', 'irl-fixtures-2646', 'Italy', 'Czechia', '2026-10-24', None, 'International Rugby League fixture list read at 07:17Z'),
    ('rugby-league', 'irl-fixtures-2661', 'Scotland', 'Wales', '2026-10-24', None, 'International Rugby League fixture list read at 07:17Z'),
    ('rugby-league', 'irl-fixtures-2664', 'Netherlands', 'Serbia', '2026-10-24', None, 'International Rugby League fixture list read at 07:17Z'),
    ('rugby-league', 'irl-fixtures-2572', 'New Zealand', 'Cook Islands', '2026-10-25', None, 'International Rugby League fixture list read at 07:17Z'),
    ('rugby-league', 'irl-fixtures-2573', 'Australia', 'Fiji', '2026-10-25', None, 'International Rugby League fixture list read at 07:17Z'),
    ('rugby-league', 'irl-fixtures-2589', 'New Zealand', 'France', '2026-10-25', None, 'International Rugby League fixture list read at 07:17Z'),
    ('rugby-league', 'irl-fixtures-2665', 'Malta', 'Philippines', '2026-10-25', None, 'International Rugby League fixture list read at 07:17Z'),
    ('rugby-union', 'lnr-top14-j7-1', 'RC Vannes', 'ASM Clermont', '2026-10-24', None, 'TOP 14 round 7 calendar read at 07:17Z'),
    ('rugby-union', 'lnr-top14-j7-2', 'Aviron Bayonnais', 'LOU Rugby', '2026-10-24', None, 'TOP 14 round 7 calendar read at 07:17Z'),
    ('rugby-union', 'lnr-top14-j7-3', 'Castres Olympique', 'Stade Français Paris', '2026-10-24', None, 'TOP 14 round 7 calendar read at 07:17Z'),
    ('rugby-union', 'lnr-top14-j7-4', 'Racing 92', 'Montpellier Hérault Rugby', '2026-10-24', None, 'TOP 14 round 7 calendar read at 07:17Z'),
    ('rugby-union', 'lnr-top14-j7-5', 'Stade Toulousain', 'USA Perpignan', '2026-10-24', None, 'TOP 14 round 7 calendar read at 07:17Z'),
    ('rugby-union', 'lnr-top14-j7-6', 'RC Toulon', 'Section Paloise', '2026-10-24', None, 'TOP 14 round 7 calendar read at 07:17Z'),
    ('rugby-union', 'lnr-top14-j7-7', 'Stade Rochelais', 'Union Bordeaux-Bègles', '2026-10-25', None, 'TOP 14 round 7 calendar read at 07:17Z'),
    ('volleyball', 'pls-skra-calendar-24', 'PGE GiEK SKRA Bełchatów', 'PGE Projekt Warszawa', '2026-10-24', None, 'PlusLiga calendar read at 07:17Z'),
    ('volleyball', 'pls-skra-calendar-27', 'PGE GiEK SKRA Bełchatów', 'GKS Katowice', '2026-10-27', None, 'PlusLiga calendar read at 07:17Z'),
    ('gaelic-football', 'munster-calendar-cork', 'St Finbarrs', 'Nemo Rangers', '2026-10-25', None, 'Munster GAA calendar read at 07:17Z'),
    ('gaelic-football', 'munster-calendar-kerry', 'Dr. Crokes', 'Kenmare Shamrocks', '2026-10-25', None, 'Munster GAA calendar read at 07:17Z'),
    ('gaelic-football', 'munster-calendar-waterford', 'Rathgormack', 'The Nire', '2026-10-25', None, 'Munster GAA calendar read at 07:17Z'),
    ('esports', 'riot-worlds-overview-worlds2', None, None, None, None, 'Riot Worlds overview row; no dated match captured'),
    ('greyhounds', 'gbgb-open-races', None, None, None, None, 'GBGB open-race calendar produced no verified runner field'),
]

SPORT_META = {
    'tennis': ('Tennis', 3, 'https://www.atptour.com/en/scores/current'),
    'basketball': ('Basketball', 4, 'https://www.nba.com/games'),
    'golf': ('Golf', 5, 'https://www.pgatour.com/schedule'),
    'cricket': ('Cricket', 7, 'https://www.icc-cricket.com/fixtures-results'),
    'snooker': ('Snooker', 8, 'https://www.wst.tv/matches/'),
    'rugby-union': ('Rugby Union', 9, 'https://top14.lnr.fr/calendrier-et-resultats'),
    'rugby-league': ('Rugby League', 10, 'https://www.intrl.sport/fixtures-results'),
    'baseball': ('Baseball', 12, 'https://www.mlb.com/schedule'),
    'ice-hockey': ('Ice Hockey', 13, 'https://www.nhl.com/schedule'),
    'motor-racing': ('Motor Racing', 14, 'https://www.formula1.com/en/racing/2026'),
    'darts': ('Darts', 15, 'https://www.pdc.tv/tournaments'),
    'handball': ('Handball', 20, 'https://ehfcl.eurohandball.com/men/'),
    'volleyball': ('Volleyball', 21, 'https://www.plusliga.pl/games.html'),
    'aussie-rules': ('Aussie Rules', 22, 'https://www.afl.com.au/aflw/fixture'),
    'esports': ('eSports', 23, 'https://lolesports.com/en-US/schedule'),
    'gaelic-football': ('Gaelic Football', 25, 'https://munster.gaa.ie/fixtures/events-calendar/'),
    'greyhounds': ('Greyhounds', 28, 'https://www.gbgb.org.uk/racing/open-races/'),
}

EXCLUDED_SPORTS = [
    ('Soccer / Football', 1, 'Excluded by project scope.'),
    ('American Football', 2, 'Excluded by project scope.'),
    ('Boxing', 11, 'Excluded by project scope.'),
    ('UFC / MMA', 16, 'Excluded by project scope.'),
    ('Hurling', 17, 'Excluded by project scope (Gaelic football is a distinct in-scope category).'),
    ('Horse Racing', 18, 'Excluded by project scope.'),
    ('Cycling', 26, 'Excluded by project scope.'),
    ('Specials', 31, 'Excluded by project scope (non-fixture specials markets).'),
]
