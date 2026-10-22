"""Hand-authored High-confidence predictions for the 40214dfd desk.

Rules enforced by scripts/s40214dfd_validate.py:
  * every prediction is at least 30 words;
  * every prediction names the selection explicitly;
  * no two predictions share a 12-word shingle (no recycled prose);
  * every factual claim in a prediction must resolve to a field in data/40214dfd/harvest/.

Every number quoted below was read from an official page on 2026-10-22 and is stored in the
harvest file named in the row's source_id. Nothing here is recalled from memory.
"""

PREDICTIONS = [
    {
        "fixture_id": "nhl-2026020155",
        "match": {"selection": "Over 4.5", "line": 4.5},
        "selection_label": "Over 4.5 goals (Toronto Maple Leafs v New York Rangers)",
        "market": "total",
        "confidence": "high",
        "american": -236,
        "probability": 0.7026,
        "source_ids": ["nhl-scores-20261022"],
        "body": (
            "Selection: Over 4.5 goals in Toronto against the New York Rangers. Toronto has scored 38 "
            "goals and conceded 35 across 11 games, while the Rangers arrive with 33 scored and 24 "
            "allowed in the same number of outings. Auston Matthews already has eight goals and ten "
            "assists for the Leafs, and Alexis Lafreniere has seven goals for New York. Both clubs are "
            "5-3-2 or better over their last ten, and Toronto's 5-3-2 run points to open, high-event "
            "hockey rather than a shutdown night."
        ),
        "facts_used": [
            "Toronto 38 goals for and 35 against in 11 games (NHL.com scores module)",
            "New York Rangers 33 goals for and 24 against in 11 games (NHL.com scores module)",
            "Auston Matthews 8 goals and 10 assists (NHL.com team leaders)",
            "Alexis Lafreniere 7 goals (NHL.com team leaders)",
            "Toronto last ten 5-3-2, Rangers last ten 7-2-1 (NHL.com standings, 21 Oct table)",
        ],
    },
    {
        "fixture_id": "nhl-2026020160",
        "match": {"selection": "Vegas Golden Knights Under 4.5", "line": 4.5},
        "selection_label": "Vegas Golden Knights team total under 4.5 goals",
        "market": "team_total",
        "confidence": "high",
        "american": -238,
        "probability": 0.7043,
        "source_ids": ["nhl-scores-20261022"],
        "body": (
            "Selection: Vegas Golden Knights team total under 4.5 goals in St. Louis. Vegas has scored "
            "44 goals in 11 games, but the Blues have conceded only 29 in nine, and averaging those two "
            "rates pulls the visitors' expected output to about 3.6 goals. Mark Stone's eight goals and "
            "Jack Eichel's 13 assists show where the offence is generated, while St. Louis is 4-4-1 over "
            "its last ten with Joel Hofer holding three wins. This line needs five Vegas goals to lose."
        ),
        "facts_used": [
            "Vegas 44 goals for in 11 games (NHL.com scores module / standings)",
            "St. Louis 29 goals against in 9 games (NHL.com standings, 21 Oct table)",
            "Mark Stone 8 goals, Jack Eichel 13 assists (NHL.com team leaders)",
            "St. Louis last ten 4-4-1, Joel Hofer 3 wins (NHL.com standings and team leaders)",
        ],
    },
    {
        "fixture_id": "nhl-2026020161",
        "match": {"selection": "Dallas Stars Under 3.5", "line": 3.5},
        "selection_label": "Dallas Stars team total under 3.5 goals",
        "market": "team_total",
        "confidence": "high",
        "american": -244,
        "probability": 0.7092,
        "source_ids": ["nhl-scores-20261022"],
        "body": (
            "Selection: Dallas Stars team total under 3.5 goals against Winnipeg. Dallas has scored only "
            "23 goals in nine games while allowing 15, and the Jets have conceded 26 in nine, so the two "
            "rates average out to roughly 2.7 expected goals for the hosts. Mikko Rantanen has five goals "
            "and Jason Robertson six assists as the main supply lines, with Jake Oettinger on four wins. "
            "Dallas is 5-3-1 over its last ten and has won three in a row, which points to a controlled, "
            "low-event game."
        ),
        "facts_used": [
            "Dallas 23 goals for and 15 against in 9 games (NHL.com standings, 21 Oct table)",
            "Winnipeg 26 goals against in 9 games (NHL.com standings, 21 Oct table)",
            "Mikko Rantanen 5 goals, Jason Robertson 6 assists, Jake Oettinger 4 wins (NHL.com team leaders)",
            "Dallas last ten 5-3-1, current streak W3 (NHL.com standings, 21 Oct table)",
        ],
    },
    {
        "fixture_id": "nhl-2026020163",
        "match": {"selection": "Carolina Hurricanes", "line": -1.5},
        "selection_label": "Carolina Hurricanes +1.5 on the puck line",
        "market": "handicap",
        "confidence": "high",
        "american": -242,
        "probability": 0.708,
        "source_ids": ["nhl-scores-20261022"],
        "body": (
            "Selection: Carolina Hurricanes +1.5 on the puck line in Edmonton. Carolina is 8-2-1 with 42 "
            "goals for and 27 against; Edmonton is 7-1-1 with 41 and 27, so the two profiles nearly "
            "mirror each other and a one-goal finish either way is the natural shape of this game. Andrei "
            "Svechnikov has six goals and Jackson Blake ten assists for Carolina, while Connor McDavid "
            "has 20 assists for the Oilers. Carolina's 8-2-0 last ten is the better recent run, and the "
            "extra goal covers a narrow loss."
        ),
        "facts_used": [
            "Carolina 8-2-1, 42 goals for and 27 against in 11 games (NHL.com scores module and standings)",
            "Edmonton 7-1-1, 41 goals for and 27 against in 9 games (NHL.com standings, 21 Oct table)",
            "Andrei Svechnikov 6 goals, Jackson Blake 10 assists (NHL.com team leaders)",
            "Connor McDavid 20 assists (NHL.com team leaders)",
            "Carolina last ten 8-2-0, Edmonton last ten 7-1-1 (NHL.com standings, 21 Oct table)",
        ],
    },
    {
        "fixture_id": "nhl-2026020164",
        "match": {"selection": "Over 5.5", "line": 5.5},
        "selection_label": "Over 5.5 goals (Utah Mammoth v Seattle Kraken)",
        "market": "total",
        "confidence": "high",
        "american": -247,
        "probability": 0.7119,
        "source_ids": ["nhl-scores-20261022"],
        "body": (
            "Selection: Over 5.5 goals between Utah and Seattle. Utah has scored 38 and conceded 31 in ten "
            "games, and Seattle has scored 39 and conceded 34 in ten, which averages to roughly seven "
            "expected goals for this matchup and sits well clear of a line set at five and a half. Nick Schmaltz has seven "
            "goals and Clayton Keller nine assists for the Mammoth, Frederick Gaudreau has five goals for "
            "the Kraken, and both clubs have won at least six of their last ten games."
        ),
        "facts_used": [
            "Utah 38 goals for and 31 against in 10 games (NHL.com standings and scores module)",
            "Seattle 39 goals for and 34 against in 10 games (NHL.com standings, 21 Oct table)",
            "Nick Schmaltz 7 goals, Clayton Keller 9 assists (NHL.com team leaders)",
            "Frederick Gaudreau 5 goals (NHL.com team leaders)",
            "Utah last ten 7-3-0; Seattle last ten 6-3-1 (NHL.com standings, 21 Oct table)",
        ],
    },
    {
        "fixture_id": "nhl-2026020164",
        "match": {"selection": "Utah Mammoth Under 4.5", "line": 4.5},
        "selection_label": "Utah Mammoth team total under 4.5 goals",
        "market": "team_total",
        "confidence": "high",
        "american": -241,
        "probability": 0.7064,
        "source_ids": ["nhl-scores-20261022"],
        "body": (
            "Selection: Utah Mammoth team total under 4.5 goals in Seattle. Utah scores 3.8 goals per game "
            "and meets a Seattle side allowing 3.4, so the averaged expectation is about 3.6 goals and the "
            "line needs five to beat us. Karel Vejmelka has five wins in net for Utah, and the Kraken have "
            "allowed 34 goals across ten games. Utah's 7-3-0 last ten is the stronger form line in this "
            "fixture, but a five-goal night remains the minority outcome of the same model."
        ),
        "facts_used": [
            "Utah 38 goals in 10 games, Seattle 34 goals against in 10 games (NHL.com standings)",
            "Karel Vejmelka 5 wins (NHL.com team leaders)",
            "Utah last ten 7-3-0 (NHL.com standings, 21 Oct table)",
        ],
    },
    {
        "fixture_id": "nhl-2026020165",
        "match": {"selection": "Detroit Red Wings Under 4.5", "line": 4.5},
        "selection_label": "Detroit Red Wings team total under 4.5 goals",
        "market": "team_total",
        "confidence": "high",
        "american": -242,
        "probability": 0.7072,
        "source_ids": ["nhl-scores-20261022"],
        "body": (
            "Selection: Detroit Red Wings team total under 4.5 goals in Vancouver. Detroit has scored 23 "
            "goals in nine games, and although Vancouver has conceded 51 in eleven, averaging those rates "
            "still leaves Detroit near 3.6 expected goals, short of the five this line needs. Alex "
            "DeBrincat has six goals and five assists for the Wings, Elias Pettersson has eight assists "
            "for the Canucks, and Detroit's 3-3-3 record includes an overtime point from its latest game."
        ),
        "facts_used": [
            "Detroit 23 goals for in 9 games (NHL.com standings, 21 Oct table)",
            "Vancouver 51 goals against in 11 games (NHL.com standings, 21 Oct table)",
            "Alex DeBrincat 6 goals and 5 assists, Elias Pettersson 8 assists (NHL.com team leaders)",
            "Detroit 3-3-3 with current streak OT1 (NHL.com standings, 21 Oct table)",
        ],
    },
]

# Short, clearly-labelled notes for selections that miss the brief's window. These are findings,
# not High picks, and the site renders them on the Flagged for Review page.
NEAR_MISS_NOTES = [
    {
        "fixture_id": "nhl-2026020154",
        "label": "Boston Bruins to win (-252 fair)",
        "detail": (
            "Boston's record model probability is 71.6%, which values the Bruins at -252 on a fair basis: "
            "one American point shorter than the brief's -250 floor. The selection clears 70% but cannot "
            "be published as High without breaking the price rule, so it is listed here instead."
        ),
    },
    {
        "fixture_id": "nhl-2026020159",
        "label": "New York Islanders to win (-311 fair)",
        "detail": (
            "The Islanders' 5-3-1 record against Los Angeles' 1-4-2 gives a 75.7% modelled chance, but Los "
            "Angeles goals-for and goals-against were not present in the retrieved standings chunk, so no "
            "goal-based market could be originated and the moneyline itself prices beyond the window."
        ),
    },
    {
        "fixture_id": "el-r7-67",
        "label": "Panathinaikos AKTOR Athens to win (-544 fair)",
        "detail": (
            "A 5-1 record against Baskonia's 1-5 produces an 84.5% modelled chance. That is a genuine "
            "strong view, but its fair price is far outside -250..+10000 and the official preview gives "
            "scoring averages for only one side, so no alternate line was originated to bring it into the "
            "window."
        ),
    },
]
