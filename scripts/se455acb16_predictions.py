#!/usr/bin/env python3
"""No approved High predictions in this evidence window.

These independently written, sourced Low research notes are not claimed to meet
the richer High context contract. Unknown player/lineup information stays unknown.
No copied first-draft prose or invented game histories are retained.
"""
PREDICTIONS = []

RESEARCH_NOTES = [
    {
        "fixture_id":"nhl-2026020166",
        "text":"The tentative winner preference is Montréal Canadiens, but the injury news is an important caution. Montréal’s 4-3-2 start compares with Chicago’s 3-6-0, while the NHL reports that Nick Suzuki is expected to miss two to four weeks with an upper-body injury. This record-only price does not quantify his absence, and it should not be mistaken for a high-confidence selection.",
        "source_ids":["nhl-schedule","nhl-standings","nhl-suzuki"],
    },
    {
        "fixture_id":"nhl-2026020176",
        "text":"Edmonton Oilers are the record-based winner preference against Toronto. The Oilers have eight wins from ten games and a three-game winning streak, with 47 goals scored against 32 conceded. Toronto’s 6-4-2 record and 43 goals underline that this is not a walkover. Starting-goaltender confirmation and a complete availability check are missing, so confidence remains Low despite Edmonton’s stronger headline record.",
        "source_ids":["nhl-schedule","nhl-standings"],
    },
    {
        "fixture_id":"nhl-2026020174",
        "text":"Vegas Golden Knights to win is the provisional research lean, rather than a claim about an available wager. Vegas are 8-4-0 with 46 goals for and 36 against; Columbus stand at 3-5-0 with 20 scored and 29 conceded. Both teams show two successive losses in the official table. That shared downturn deserves attention before treating the season-record gap as a dependable edge.",
        "source_ids":["nhl-schedule","nhl-standings"],
    },
    {
        "fixture_id":"nhl-2026020170",
        "text":"Boston Bruins are preferred on the experimental match-winner line. Their 8-2-1 record and 42-22 goal balance are stronger than San Jose’s 6-4-1 and 33-37, but the Sharks arrive on a two-game winning streak. The NHL scoreboard lists David Pastrnak with six goals and ten assists. That context supports further research, not an automatic upgrade: complete lineups and current betting availability have not been established.",
        "source_ids":["nhl-schedule","nhl-standings","nhl-scoreboard"],
    },
    {
        "fixture_id":"nhl-2026020169",
        "text":"New Jersey Devils are the tentative winner choice against Los Angeles Kings. The official records are 6-4-0 for New Jersey and 2-4-2 for Los Angeles, although each side has won its last two. The Kings’ overtime defeats count as defeats here rather than half-wins. The resulting favourite price can fall outside the requested odds window; it is disclosed without changing the price or promoting the confidence tier.",
        "source_ids":["nhl-schedule","nhl-standings"],
    },
    {
        "fixture_id":"mlb-849805",
        "text":"Milwaukee Brewers to win Game 1 is a Low-confidence research preference, drawn from regular-season run rates rather than current pitching matchups. Milwaukee finished with 832 runs scored and 618 allowed; Tampa Bay recorded 736 and 650 over the same 162-game period. Those aggregates favour the Brewers in this simplified comparison, but they do not establish postseason form, a confirmed starting lineup or a profitable available betting price.",
        "source_ids":["mlb-schedule","mlb-standings"],
    },
]
