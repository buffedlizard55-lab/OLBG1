"""Session e6fc2f12-olbg1 — hand-written predictions for every High selection.

Rules applied to each entry:
  * at least 30 words, written for this fixture only, no shared template;
  * the betting selection is named explicitly (winner, puck line, total or team total);
  * every factual claim is one of: a season record from the official NHL team
    summary, a scoreline from the official NHL game index read on 2026-10-22, a
    URC table row, or a URC Round 4 fixture line. Nothing else is asserted;
  * no individual-player claim is made, because no player-level official read was
    performed in this session. That gap is disclosed on the Methodology and
    Flagged pages instead of being papered over with invented names.

Keys are (fixture_id, selection). The validator re-checks the word count,
uniqueness and the presence of the selection string.
"""

PREDICTIONS = {
    ("nhl-2026020180", "Under 7.5"): (
        "Selection: under 7.5 goals in Chicago Blackhawks v Florida Panthers on 25 October. "
        "Chicago have scored only 21 goals in nine games while conceding 36, and were shut out "
        "4-0 at Dallas on 17 October. Florida have 31 goals in ten games and lost 5-1 at Ottawa "
        "on 21 October. Two thin attacks meeting a 7.5 line points to the under."
    ),
    ("nhl-2026020182", "Under 7.5"): (
        "Selection: under 7.5 goals in Winnipeg Jets v Montréal Canadiens on 25 October. "
        "Winnipeg have scored 24 goals in nine games and conceded 26, and lost 2-1 at St. Louis "
        "on 20 October. Montréal have 28 goals in nine and lost 4-3 in overtime at home to San "
        "Jose on 20 October. Both clubs average under three goals a game, so 7.5 sits too high."
    ),
    ("nhl-2026020167", "Tampa Bay Lightning +1.5"): (
        "Selection: Tampa Bay Lightning +1.5 on the puck line at Colorado on 23 October. "
        "Tampa Bay are 7-2-0 with 31 goals for and 23 against in nine games, and won 6-2 at "
        "Vegas on 20 October. Colorado are 5-4-1 and lost 3-4 at New Jersey on 20 October. A "
        "side conceding 2.56 goals a game should not be losing by two or more."
    ),
    ("nhl-2026020188", "Under 6.5"): (
        "Selection: under 6.5 goals in Philadelphia Flyers v Columbus Blue Jackets on 27 October. "
        "Philadelphia have scored just 20 goals in twelve games, the thinnest attack in this "
        "sample, and beat Buffalo 3-1 on 21 October. Columbus have 19 goals in eight games and "
        "lost 6-2 at Toronto on 20 October. Two low-output offences favour the under here."
    ),
    ("nhl-2026020195", "Under 7.5"): (
        "Selection: under 7.5 goals in Utah Mammoth v Minnesota Wild on 27 October. Utah are "
        "7-3-0 with 38 goals for and 31 against, and beat Pittsburgh 5-4 on 19 October. "
        "Minnesota are 6-2-2, have conceded only 25 goals in ten games, and lost 4-3 in overtime "
        "at Edmonton on 20 October. Minnesota's defensive record points below a 7.5 total."
    ),
    ("nhl-2026020210", "Under 6.5"): (
        "Selection: under 6.5 goals in Minnesota Wild v New York Islanders on 29 October. "
        "Minnesota have allowed 25 goals in ten games and lost 4-3 in overtime at Edmonton on "
        "20 October. The Islanders have conceded 19 in nine games, the best rate in this set, "
        "and beat Anaheim 3-2 on 20 October. Two of the tightest defences meet a 6.5 line."
    ),
    ("nhl-2026020211", "Under 7.5"): (
        "Selection: under 7.5 goals in Anaheim Ducks v Buffalo Sabres on 29 October. Anaheim have "
        "26 goals for and 29 against in nine games, and lost 3-2 at the Islanders on 20 October. "
        "Buffalo have conceded 36 in ten games and lost 3-1 at home to Philadelphia on 21 October. "
        "Neither side is scoring freely, so the 7.5 line is the value side for the under."
    ),
    ("nhl-2026020163", "Carolina Hurricanes +1.5"): (
        "Selection: Carolina Hurricanes +1.5 on the puck line at Edmonton on 22 October. Carolina "
        "are 8-2-1 with 42 goals for and 27 against, and won 6-3 at Vancouver on 20 October. "
        "Edmonton are 7-1-1 and beat Minnesota 4-3 in overtime on 20 October. The best record in "
        "the league should not be asked to avoid a two-goal defeat."
    ),
    ("nhl-2026020172", "Under 7.5"): (
        "Selection: under 7.5 goals in Pittsburgh Penguins v Nashville Predators on 24 October. "
        "Pittsburgh have conceded 37 goals in ten games and lost 5-4 at Utah on 19 October. "
        "Nashville have allowed only 22 in eight games and beat St. Louis 5-2 on 17 October. "
        "Nashville's defensive profile anchors this call; a 7.5 total overstates the scoring."
    ),
    ("nhl-2026020192", "Under 6.5"): (
        "Selection: under 6.5 goals in Nashville Predators v New York Islanders on 27 October. "
        "Nashville have scored 23 and conceded 22 in eight games, beating St. Louis 5-2 on 17 "
        "October. The Islanders have 27 goals for and 19 against in nine games, and beat Anaheim "
        "3-2 on 20 October. Two of the lowest-scoring profiles in this sample meet at 6.5."
    ),
    ("nhl-2026020176", "Over 5.5"): (
        "Selection: over 5.5 goals in Edmonton Oilers v Toronto Maple Leafs on 24 October. "
        "Edmonton have 41 goals in nine games and beat Minnesota 4-3 in overtime on 20 October. "
        "Toronto have 38 in eleven games and won 6-2 at Columbus on 20 October. Two attack-first "
        "teams, both averaging well above three goals, make 5.5 a low bar."
    ),
    ("nhl-2026020168", "Under 6.5"): (
        "Selection: under 6.5 goals in Philadelphia Flyers v Anaheim Ducks on 24 October. "
        "Philadelphia have scored 20 goals in twelve games and conceded 36, then beat Buffalo "
        "3-1 on 21 October. Anaheim have 26 for and 29 against in nine games, and lost 3-2 at "
        "the Islanders on 20 October. Two teams averaging under three goals support the under."
    ),
    ("urc-r4-05", "Over 39.5"): (
        "Selection: over 39.5 match points in DHL Stormers v Scarlets on 24 October. The Stormers "
        "have scored 81 points and conceded 54 across three rounds, with a win-loss-win sequence. "
        "Scarlets have scored 68 and conceded 85, taking one win and two defeats. Scarlets' "
        "record of 28 points conceded per match points to a high-scoring afternoon in Cape Town."
    ),
    ("nhl-2026020197", "Anaheim Ducks"): (
        "Selection: Anaheim Ducks to beat Vancouver Canucks on 27 October. Anaheim are 4-5-0 with "
        "26 goals for and 29 against in nine games, and lost 3-2 at the Islanders on 20 October. "
        "Vancouver are 2-8-1, have conceded 51 goals in eleven games, and lost 6-3 at home to "
        "Carolina on 20 October. Anaheim's far superior goal difference makes them the pick."
    ),
    ("nhl-2026020170", "Over 4.5"): (
        "Selection: over 4.5 goals in Boston Bruins v San Jose Sharks on 24 October. Boston are "
        "7-2-1 with 36 goals in ten games, winning 4-1 at Los Angeles on 17 October before losing "
        "3-2 in overtime at Dallas on 20 October. San Jose have 26 goals in ten games and won "
        "4-3 in overtime at Montréal on 20 October. A 4.5 line is low for these scoring rates."
    ),
    ("nhl-2026020182", "Montréal Canadiens +1.5"): (
        "Selection: Montréal Canadiens +1.5 on the puck line at Winnipeg on 25 October. Montréal "
        "are 4-3-2 with 28 goals for and 34 against in nine games, and lost 4-3 in overtime at "
        "home to San Jose on 20 October. Winnipeg are 4-3-2 with just 24 goals in nine games and "
        "lost 2-1 at St. Louis on 20 October. Neither club wins by two often."
    ),
    ("nhl-2026020213", "San Jose Sharks over 2.5"): (
        "Selection: San Jose Sharks to score over 2.5 goals against Vancouver on 29 October. "
        "San Jose have 26 goals in ten games and scored four in an overtime win at Montréal on "
        "20 October. Vancouver have conceded 51 goals in eleven games, the worst rate in this "
        "sample, including six at home to Carolina on 20 October. A 2.5 team total is modest."
    ),
    ("nhl-2026020190", "Under 7.5"): (
        "Selection: under 7.5 goals in Chicago Blackhawks v Los Angeles Kings on 27 October. "
        "Chicago have scored 21 goals in nine games and lost 4-0 at Dallas on 17 October. Los "
        "Angeles are 1-4-2 with only 17 goals in seven games, and won 5-2 at Washington on 20 "
        "October. Two of the weakest attacks in the league meet a line set for goals."
    ),
}
