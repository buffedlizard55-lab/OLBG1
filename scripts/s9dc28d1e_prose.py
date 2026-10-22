"""Written predictions and findings for the 9dc28d1e desk.

Predictions are keyed by (fixture_id, selection) so the builder can resolve the priced
outcome rather than trusting a hand-written id. Each body is unique prose of at least
thirty words and every fact in its table carries a source key.
"""

PREDICTIONS = [
    {
        "fixture_id": "nhl-2026020154",
        "selection": "Nashville Predators over 1.5 goals",
        "headline": "Nashville to score twice at Boston, even against the Bruins' stingy defence",
        "body": (
            "Nashville are 3-2-3 through eight games and have scored 23 goals in that span, but the "
            "reason this line is attractive is shot volume rather than finishing: Filip Forsberg has "
            "put 24 shots on goal in eight "
            "games for a single goal, and Steven Stamkos has 14 shots and 10 points from the same "
            "span. Boston have conceded only 22 goals in ten games, one of the best rates in the "
            "league, which is exactly why the team total sits at 1.5 rather than 2.5. Two goals is "
            "the realistic floor for a club generating this much rubber, and the model puts it at "
            "71.1%, one of only four selections on the slate that clears the brief's rule."
        ),
        "facts": [
            ("Nashville record", "3-2-3, 9 points from 8 games", "nhl-standings"),
            ("Nashville scoring", "23 goals in 8 games (2.88 per game)", "nhl-standings"),
            ("Nashville conceding", "22 goals against in 8 games (2.75 per game)", "nhl-standings"),
            ("Boston record", "7-2-1, 36 goals for, 22 against in 10 games", "nhl-standings"),
            ("Steven Stamkos", "4 goals, 6 assists, 10 points, 14 shots, 2 power-play goals", "nhl-skaters-nsh"),
            ("Filip Forsberg", "1 goal, 7 assists, 8 points, 24 shots", "nhl-skaters-nsh"),
            ("Roman Josi", "1 goal, 8 assists, 9 points, 19 shots", "nhl-skaters-nsh"),
        ],
    },
    {
        "fixture_id": "nhl-2026020164",
        "selection": "Utah Mammoth +1.5",
        "headline": "Utah to stay within one goal in Seattle",
        "body": (
            "Utah have won seven of ten and scored 38 goals, and the offence runs through two "
            "players who are both above a point a game: Nick Schmaltz has seven goals and six "
            "assists with five of those goals on the power play, and Clayton Keller has four and "
            "nine. Seattle have scored almost as much, 37 goals in ten, but have conceded 34 and "
            "have already lost three times, so a one-goal Seattle win still cashes this line. The "
            "model gives Utah a 70.5% chance of not losing by two or more, which makes it the "
            "thinnest of the three Highs and the one most exposed if Utah's 36.1% power play turns "
            "out to be a five-game artefact."
        ),
        "facts": [
            ("Utah record", "7-3-0, 38 goals for, 31 against in 10 games", "nhl-standings"),
            ("Utah power play", "36.1% (13 of 36)", "nhl-standings"),
            ("Nick Schmaltz", "7 goals, 6 assists, 13 points, 5 power-play goals, 31 shots", "nhl-skaters-uta"),
            ("Clayton Keller", "4 goals, 9 assists, 13 points, 8 power-play points", "nhl-skaters-uta"),
            ("Mikhail Sergachev", "3 goals, 8 assists, 11 points", "nhl-skaters-uta"),
            ("Seattle record", "6-3-1, 37 goals for, 34 against in 10 games", "nhl-standings"),
        ],
    },
    {
        "fixture_id": "nhl-2026020156",
        "selection": "San Jose Sharks over 1.5 goals",
        "headline": "San Jose to score twice in Ottawa",
        "body": (
            "San Jose are 5-4-1 with 26 goals in ten games, and the scoring is unusually "
            "concentrated: Macklin Celebrini has 14 points in eight games from 37 shots, including "
            "an overtime winner, while Will Smith and Ivar Stenberg have seven points each. Ottawa "
            "are 7-3-0 and have conceded 24 goals in ten, so the Senators are the tougher half of "
            "this matchup and the total sits low for that reason. The model still gives the Sharks "
            "a 70.4% chance of two goals or more, because a team putting up Celebrini's shot volume "
            "usually gets there, and the same shape of bet as the Nashville line is the one this "
            "desk is most comfortable repeating."
        ),
        "facts": [
            ("San Jose record", "5-4-1, 26 goals for, 34 against in 10 games", "nhl-standings"),
            ("Macklin Celebrini", "5 goals, 9 assists, 14 points, 37 shots in 8 games", "nhl-skaters-sjs"),
            ("Will Smith", "3 goals, 4 assists, 7 points", "nhl-skaters-sjs"),
            ("Ivar Stenberg", "2 goals, 5 assists, 7 points", "nhl-skaters-sjs"),
            ("Ottawa record", "7-3-0, 27 goals for, 24 against in 10 games", "nhl-standings"),
            ("Ottawa special teams", "13.0% power play, 79.5% penalty kill", "nhl-standings"),
        ],
    },
    {
        "fixture_id": "nhl-2026020157",
        "selection": "Under 7.5 goals",
        "headline": "Under 7.5 goals between two clubs that are not converting their chances",
        "body": (
            "New Jersey's nine games have produced 59 goals and Anaheim's 55, and neither side is "
            "finishing at a rate that suggests a burst: Jack Hughes has nine points but only two goals "
            "from 35 shots, and Leo Carlsson's eleven points have come from just eleven shots, a "
            "conversion rate no player sustains. Both clubs are conceding around three goals a game — "
            "30 in nine for the Devils, 29 in nine for the Ducks — so the model's expected total lands "
            "close to six. Under 7.5 clears the 70% test at 70.0% and a fair price of −234, which is "
            "the fourth and last selection inside the brief's window."
        ),
        "facts": [
            ("New Jersey record", "5-4-0, 29 goals for, 30 against in 9 games", "nhl-standings"),
            ("Anaheim record", "4-5-0, 26 goals for, 29 against in 9 games", "nhl-standings"),
            ("Jack Hughes", "2 goals, 7 assists, 9 points, 35 shots, 2 overtime goals", "nhl-skaters-njd"),
            ("Jesper Bratt", "2 goals, 5 assists, 7 points, 24 shots", "nhl-skaters-njd"),
            ("Nico Hischier", "4 goals, 2 assists, 6 points, 3 power-play goals", "nhl-skaters-njd"),
            ("Leo Carlsson", "2 goals, 9 assists, 11 points from 11 shots", "nhl-skaters-ana"),
            ("Beckett Sennecke", "5 goals, 3 assists, 8 points, 25 shots", "nhl-skaters-ana"),
            ("Mikael Granlund", "2 goals, 6 assists, 8 points", "nhl-skaters-ana"),
        ],
    },
]

FINDINGS = [
    {
        "id": "F-9DC-01",
        "title": "The High gate can only ever return a 1.43-point band of probabilities",
        "detail": (
            "More than 70% implies a fair American price shorter than −233.33. Requiring that price to "
            "be no shorter than −250 leaves 70.00% < p ≤ 71.43%. The +10000 end of the stated range "
            "corresponds to 0.99% and is unreachable in a two-way market. The rule therefore selects on "
            "price proximity, not on confidence."
        ),
        "impact": "Every High on this desk. Needs a decision from whoever wrote the brief.",
    },
    {
        "id": "F-9DC-02",
        "title": "One in-band EuroLeague selection is capped at Medium for lack of player evidence",
        "detail": (
            "Anadolu Efes v Besiktas over 166.5 points prices at 71.2% (−247) and passes both tests in "
            "the brief's rule. No official EuroLeague player-level source was available to this session, "
            "so the required write-up could not be produced. The price is published; the tier is Medium. "
            "It is now the only in-band selection on the desk that is not published as High."
        ),
        "impact": "One selection. Visible on the markets page with its price intact.",
    },
    {
        "id": "F-9DC-03",
        "title": "The strongest line on the slate is excluded by the price floor",
        "detail": (
            "Panathinaikos at home to Baskonia prices at 81.8% with a fair price of −451. It clears the "
            "probability test by twelve points and fails the −250 test by two hundred. The same is true "
            "of 167 other selections above 70%."
        ),
        "impact": "The desk's best information is published as Medium, not High.",
    },
    {
        "id": "F-9DC-04",
        "title": "EuroLeague tip-off times are inherited, not re-read",
        "detail": (
            "The standings feed used for ratings publishes results only. Tip-off times come from the "
            "07:17Z canonical observation of the round 7 game centre, five hours before this desk was "
            "built, and are marked as inherited on every EuroLeague fixture."
        ),
        "impact": "Nine fixtures. A schedule change after 07:17Z would not be reflected.",
    },
    {
        "id": "F-9DC-05",
        "title": "No game-level recent results were read",
        "detail": (
            "The club schedule feeds return the full season and were too large to read within this "
            "session's budget. Form is therefore expressed as season-to-date record, goals for, goals "
            "against and per-player scoring totals, not as a list of recent scorelines."
        ),
        "impact": "All three predictions. The brief asked for recent match history; this is a partial answer.",
    },
    {
        "id": "F-9DC-06",
        "title": "Fourteen of seventeen in-scope categories have no verified input",
        "detail": (
            "Only ice hockey, basketball and baseball produced fixtures that could be re-read from an "
            "official feed in this window. The other fourteen categories are kept as empty pages rather "
            "than filled with remembered fixtures from earlier windows."
        ),
        "impact": "Coverage. The gap is structural, not an oversight.",
    },
    {
        "id": "F-9DC-07",
        "title": "NHL venues were visible for only five of twelve games",
        "detail": (
            "The schedule feed returns venue inside each game object; the read covered games 154 to 158. "
            "The remaining seven venues are blank rather than reconstructed from general knowledge."
        ),
        "impact": "Seven fixture rows on the matches page.",
    },
    {
        "id": "F-9DC-08",
        "title": "MLB pricing rests on two clubs' rates, not a league run environment",
        "detail": (
            "Run expectations are the mean of each batting side's runs scored and each bowling side's "
            "runs allowed per game, with a fixed home adjustment. No league-average run environment was "
            "read, so totals and run lines are labelled as model output and the desk does not claim they "
            "match a market."
        ),
        "impact": "Two priced World Series games. Game 2 also has no announced starter.",
    },
    {
        "id": "F-9DC-09",
        "title": "The models are uncalibrated and the sensitivity ranges are wider than the gate",
        "detail": (
            "None of the priced fixtures had started when the desk was built, so no outcome backtest "
            "exists. Re-running each High across the shrinkage and home-advantage grid moves it by three "
            "to five percentage points, which is two to three times the width of the 70.00–71.43% window."
        ),
        "impact": "Every probability on the desk. Treat tiers as labels, not guarantees.",
    },
    {
        "id": "F-9DC-10",
        "title": "The EuroLeague model was recalibrated by judgement, and that is disclosed",
        "detail": (
            "A multiplicative attack/defence model priced Panathinaikos at 97.5% for this fixture, which "
            "no basketball market would sustain. The published version shrinks each club's points "
            "differential toward zero and applies half of the remaining gap, which moves that match to "
            "81.8%. The 0.50 weight is a judgement call, chosen so the largest favourite on the slate "
            "lands near 82%."
        ),
        "impact": "All nine EuroLeague fixtures.",
    },
]
