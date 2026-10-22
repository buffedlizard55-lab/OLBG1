"""Session 9dc28d1e — hand-authored prediction prose and findings.

Each prediction is written only from facts that appear in `data/9dc28d1e/desk.json` inputs and were
read from the official source named beside it. No player, streak, injury or head-to-head claim is
made unless it is present in the imported official fields.
"""

# High-tier predictions. `facts` lists the exact official values the sentence relies on so the
# validator can check every claim against the imported data rather than trusting the prose.
PREDICTIONS = [
    {
        'fixture_id': 'nhl-2026020154',
        'market': 'team-total',
        'line': 1.5,
        'selection': 'Nashville Predators over 1.5 goals',
        'title': 'Nashville Predators over 1.5 team goals at Boston',
        'source_ids': ['nhl-team-summary-20262027', 'nhl-schedule-20261022', 'nhl-club-stats-NSH'],
        'facts': [
            'Nashville 23 goals in 8 games',
            'Steven Stamkos 4 goals 6 assists in 8 games, 2 power-play goals',
            "Ryan O'Reilly 4 goals in 8 games",
            'Boston 22 goals against in 10 games',
        ],
        'text': (
            "Nashville Predators team total over 1.5 goals at Boston is the selection. The Predators "
            "carry 23 goals across their first eight games, with Steven Stamkos leading on four goals and six "
            "assists and two power-play strikes, while Ryan O'Reilly has four goals of his own. Boston "
            "have conceded 22 goals in ten games, so the visitors need only two goals for this line to "
            "settle, and the model puts that at 71.2 percent."
        ),
    },
    {
        'fixture_id': 'nhl-2026020156',
        'market': 'team-total',
        'line': 1.5,
        'selection': 'San Jose Sharks over 1.5 goals',
        'title': 'San Jose Sharks over 1.5 team goals at Ottawa',
        'source_ids': ['nhl-team-summary-20262027', 'nhl-schedule-20261022', 'nhl-club-stats-SJS'],
        'facts': [
            'San Jose 26 goals in 10 games',
            'Macklin Celebrini 5 goals 9 assists in 8 games, 37 shots',
            'Tyler Toffoli 3 goals in 10 games',
            'Will Smith 3 goals in 10 games',
            'Ottawa 24 goals against in 10 games',
        ],
        'text': (
            "San Jose Sharks over 1.5 team goals against Ottawa is the pick. San Jose have put up 26 "
            "goals across ten outings, driven by Macklin Celebrini's five goals and nine assists in eight "
            "appearances on 37 shots, with Tyler Toffoli and Will Smith adding three goals each. Ottawa "
            "have allowed 24 goals across ten games, and the model gives San Jose a 70.3 percent chance "
            "of scoring at least twice."
        ),
    },
    {
        'fixture_id': 'nhl-2026020162',
        'market': 'team-total',
        'line': 4.5,
        'selection': 'Minnesota Wild under 4.5 goals',
        'title': 'Minnesota Wild under 4.5 team goals at Calgary',
        'source_ids': ['nhl-team-summary-20262027', 'nhl-schedule-20261022', 'nhl-club-stats-MIN'],
        'facts': [
            'Minnesota 31 goals in 10 games',
            'Kirill Kaprizov 11 goals 6 assists in 10 games',
            'Matt Boldy 5 goals 4 assists in 10 games',
            'no other Minnesota skater above two goals',
            'Calgary 37 goals against in 8 games',
        ],
        'text': (
            "Minnesota Wild under 4.5 team goals at Calgary is the selection. Minnesota own 31 goals from "
            "ten games, a 3.1 per-game rate, with Kirill Kaprizov on 11 goals and 17 points and "
            "Matt Boldy on five goals and nine points; no other Wild skater has more than two goals. "
            "Calgary have conceded 37 goals in eight games, so the line is not free, yet the model puts "
            "Minnesota scoring five or more at only 29.5 percent."
        ),
    },
]

# In-band selections that meet the probability and price conditions but are deliberately capped at
# Medium because no player-level fact was available from an official source for the write-up.
EUROLEAGUE_CAPPED = [
    ('euroleague-round7-68', 'Zalgiris Kaunas +2.5 handicap', 0.7141, -249.8,
     'EuroLeague standings publish team totals only; no player-level form was read for Zalgiris or ASVEL, so the High write-up requirement cannot be met.'),
    ('euroleague-round7-68', 'Over 166.5 match total', 0.7106, -245.6,
     'Total depends on team scoring rates only; no individual availability check was possible.'),
    ('euroleague-round7-67', 'Under 178.5 match total', 0.7091, -243.8,
     'Panathinaikos and Baskonia scoring rates are verified, but player-level context is not.'),
    ('euroleague-round7-70', 'Fenerbahce Tarfin Istanbul +8.5 handicap', 0.7060, -240.1,
     'Handicap rests on team efficiency from the official standings; no roster read this session.'),
    ('euroleague-round7-65', 'FC Bayern Munich +5.5 handicap', 0.7060, -240.1,
     'Same limitation: team-level inputs only.'),
    ('euroleague-round7-70', 'Under 178.5 match total', 0.7059, -240.1,
     'Same limitation: team-level inputs only.'),
    ('euroleague-round7-64', 'Over 166.5 match total', 0.7043, -238.2,
     'Same limitation: team-level inputs only.'),
    ('euroleague-round7-62', 'Real Madrid +5.5 handicap', 0.7019, -235.4,
     'Same limitation: team-level inputs only.'),
]

FINDINGS = [
    {
        'id': 'F-9DC-01',
        'severity': 'high',
        'title': "The brief's own High gate is a 1.43-percentage-point window",
        'detail': (
            "A probability above 70% can never price longer than -233.33 American, because -233.33 is "
            "exactly the 70% point. Requiring both 'more than 70%' and 'between -250 and +10000' "
            "therefore leaves only probabilities in (70.00%, 71.43%]. Every selection outside that "
            "sliver is either too likely to be inside the price floor or too unlikely to clear 70%. "
            "This desk applies the conjunction literally and publishes the excluded near-misses."
        ),
        'sources': ['arithmetic: american = -100p/(1-p); 70% -> -233.33; 71.4286% -> -250'],
        'status': 'open — needs a product decision, not more data',
    },
    {
        'id': 'F-9DC-02',
        'severity': 'high',
        'title': 'Eight EuroLeague selections clear both High conditions but are capped at Medium',
        'detail': (
            "The eight selections listed in this finding satisfy probability > 70% and a fair price "
            "inside [-250, +10000]. They are published as Medium because the brief also requires a "
            "prediction naming a player, and the official EuroLeague machine-readable source used here "
            "publishes standings only - no roster, minutes or availability. Fabricating a player would "
            "be worse than capping the tier, so the rule applied is: High = probability + price + a "
            "prediction supported by verified player-level facts."
        ),
        'sources': ['euroleague-standings-e2026'],
        'status': 'needs review — accept the cap or supply a player-level source',
    },
    {
        'id': 'F-9DC-03',
        'severity': 'medium',
        'title': 'Seventy-three listings are inherited, not re-read, and carry no prices',
        'detail': (
            "The canonical snapshot verified these listings at 2026-10-22T07:17:40Z-07:30:30Z. This "
            "session did not re-fetch those pages, so every inherited row is published with blank "
            "prices, an explicit 'not re-read by this session' status and the canonical observation "
            "window. No inherited row contributes to any confidence tier."
        ),
        'sources': ['canonical snapshot data/current/snapshot.json'],
        'status': 'open — by design; prices withheld',
    },
    {
        'id': 'F-9DC-04',
        'severity': 'medium',
        'title': 'EuroLeague tip-off times are inherited; the standings were re-read',
        'detail': (
            "The EuroLeague game-center article returns its tip-off times only in prose, and the "
            "attempted machine-read of a round-level endpoint returned 'Resource not found'. The nine "
            "Round 7 pairings and times therefore carry the 07:17Z observation window, while the "
            "standings that drive every EuroLeague price were re-read at 12:06Z. Fixture time and "
            "rating input are verified on different clocks."
        ),
        'sources': ['euroleague-round7-gamecenter', 'euroleague-standings-e2026'],
        'status': 'open — retire when a machine-readable schedule endpoint is confirmed',
    },
    {
        'id': 'F-9DC-05',
        'severity': 'medium',
        'title': 'MLB run line and totals withheld rather than guessed',
        'detail': (
            "The official standings projection used here returns the two World Series clubs' wins, "
            "losses, runs scored and runs allowed, but not a league run environment. Pricing a run line "
            "or total needs that environment, so only the moneyline is originated. The result is that "
            "the four World Series games carry one two-way market each."
        ),
        'sources': ['mlb-records-2026', 'mlb-schedule-ws-2026'],
        'status': 'open — needs a verified 2026 league run rate',
    },
    {
        'id': 'F-9DC-06',
        'severity': 'high',
        'title': 'Model calibration is unverified; tier fragility is published with every High',
        'detail': (
            "No backtest against settled results was possible in this session, so probabilities are "
            "model estimates, not measured frequencies. Every High tier is therefore re-computed under "
            "shrinkage and home-edge perturbations and the resulting probability range is shown in the "
            "table. A pick whose range crosses the 70% threshold or the -250 floor is marked fragile."
        ),
        'sources': ['model: 9dc-ev1.0, see Methodology'],
        'status': 'open — needs a settled-results backtest',
    },
    {
        'id': 'F-9DC-07',
        'severity': 'low',
        'title': 'Overtime is split 50/50 by assumption',
        'detail': (
            "NHL moneylines settle after overtime and the shootout. Regulation goals are modelled as "
            "Poisson and a regulation tie is allocated half to each side. That is an assumption, not a "
            "measurement; it moves the moneyline by at most half of the tie mass, roughly two points of "
            "probability in these games."
        ),
        'sources': ['nhl-team-summary-20262027'],
        'status': 'documented assumption',
    },
    {
        'id': 'F-9DC-08',
        'severity': 'medium',
        'title': 'Five in-scope categories produced no verified participant-level input today',
        'detail': (
            "Darts, greyhounds, golf, eSports and motor racing are in scope but no official page read "
            "in this session returned a usable draw, runner field or entry list. The PDC tournaments "
            "page returned consent-banner furniture instead of a draw, and the GBGB open-race calendar "
            "returned no runner field. These categories are listed with blank participants and prices."
        ),
        'sources': ['https://www.pdc.tv/tournaments', 'https://www.gbgb.org.uk/racing/open-races/'],
        'status': 'open — needs a machine-readable official draw',
    },
    {
        'id': 'F-9DC-09',
        'severity': 'low',
        'title': 'Canonical rows list the home side first without labelling it',
        'detail': (
            "The canonical fixture rows put the home club in the first participant column (for example "
            "'Boston Bruins v Nashville Predators' is Boston at home to Nashville). That convention is "
            "the reverse of the usual 'away at home' reading and is easy to misread. This desk labels "
            "every fixture 'Home v Away' explicitly and states the venue."
        ),
        'sources': ['nhl-schedule-20261022'],
        'status': 'presentation — corrected on this desk, inherited rows left untouched',
    },
    {
        'id': 'F-9DC-10',
        'severity': 'low',
        'title': 'MLB UTC start crosses the calendar date',
        'detail': (
            "World Series Game 1 is officially dated 2026-10-23 in US Eastern but starts at "
            "2026-10-24T00:00:00Z. The canonical row and the MLB feed agree; the date looks wrong only "
            "if the timezone is dropped. Published here with both the UTC start and the official date."
        ),
        'sources': ['mlb-schedule-ws-2026'],
        'status': 'verified — no correction required',
    },
]
