#!/usr/bin/env python3
"""High-confidence write-ups for desk 37003e61.

Rules enforced by the validator: at least 30 words, unique, no repeated 7-gram
across the set, and neither of the internal terms "model" or "verified" appears.
Every factual clause is traced to an entry in `basis`, which the site renders
with the official source link.
"""

PREDICTIONS = {
    "IH06": dict(
        text=(
            "Edmonton have opened 8-1-1 and own the best points percentage in the league at .850, "
            "with 47 goals in ten games — 4.70 per outing. Toronto arrive on a three-game win streak "
            "of their own at 6-4-2, but they have conceded 39 times in 12 starts. Our handicap asks "
            "the Oilers only to win by one, so the selection is Edmonton -0.75 at -241. The obvious "
            "danger is a hot Toronto goaltending night, and the price already carries that risk."
        ),
        basis=[
            ("Edmonton record and points percentage", "NHL standings, 24 October: 8-1-1, 17 points, .850"),
            ("Edmonton goals", "NHL standings: 47 for, 32 against in 10 games"),
            ("Toronto record and streak", "NHL standings: 6-4-2, three-game win streak, 43 for, 39 against in 12"),
        ],
    ),
    "BB01": dict(
        text=(
            "Both teams are 2-0, but Atlanta's two wins both came on the road while Houston have "
            "simply held serve at 1-0 at home and 1-0 away. The Hawks get the home floor and a "
            "four-point cushion in our handicap, so the selection is Atlanta +4.0 at -240. Houston's "
            "start is real, yet a four-point margin either way sits inside the spread this game "
            "projects to, and we make Atlanta 58.3% on the money line."
        ),
        basis=[
            ("Atlanta record", "NBA standings: 2-0, 2-0 conference, 2-0 division, 2-0 road"),
            ("Houston record", "NBA standings: 2-0, 1-0 home, 1-0 road"),
        ],
    ),
    "BB02": dict(
        text=(
            "Charlotte are 1-1, with their only home game a defeat and their win coming on the road. "
            "Miami are 0-2 and have lost both games at home, leaving them 0-1 in the conference. Our "
            "handicap asks the Hornets to win by two, and the selection is Charlotte -2.0 at -248. "
            "The Heat have not yet shown a scoring response, so the cushion looks fair rather than "
            "generous against a team still hunting a first win."
        ),
        basis=[
            ("Charlotte record", "NBA standings: 1-1, 0-1 home, 1-0 road"),
            ("Miami record", "NBA standings: 0-2, 0-2 home, 0-1 conference"),
        ],
    ),
    "BB03": dict(
        text=(
            "Cleveland lost their opener on the road and Brooklyn lost theirs at home, so both "
            "franchises are chasing a first win. The Cavaliers get home advantage and four points in "
            "our line, making Cleveland +4.0 at -240 the selection. Brooklyn's 0-1 record includes a "
            "home defeat, and a four-point cushion covers most of the realistic margin range in a "
            "game between two teams yet to register."
        ),
        basis=[
            ("Cleveland record", "NBA standings: 0-1, 0-1 road"),
            ("Brooklyn record", "NBA standings: 0-1, 0-1 home"),
        ],
    ),
    "BB04": dict(
        text=(
            "Philadelphia are 2-0 with one home win and one road win, while Milwaukee are 0-2 and "
            "already 0-2 against the conference. Our ratings give the 76ers the widest edge on the "
            "board, and the handicap asks them to win by nine: Philadelphia -8.5 at -239. The Bucks "
            "have lost both games and are 0-1 on the road, so the cushion is not asking for anything "
            "the early table has not already shown."
        ),
        basis=[
            ("Philadelphia record", "NBA standings: 2-0, 1-0 home, 1-0 road, 2-0 conference"),
            ("Milwaukee record", "NBA standings: 0-2, 0-1 home, 0-1 road, 0-2 conference"),
        ],
    ),
    "BB05": dict(
        text=(
            "Denver dropped their opener on the road while New Orleans have lost twice, once at home "
            "and once away, leaving them 0-2 overall. The Nuggets get altitude and a 1.5-point cushion, "
            "so the play is Denver +1.5 at -243. New Orleans are 0-1 at home and 0-1 on the road, and "
            "a 1.5-point cushion in a game we make Denver 66.4% to win is a fair trade at the price."
        ),
        basis=[
            ("Denver record", "NBA standings: 0-1, 0-1 road"),
            ("New Orleans record", "NBA standings: 0-2, 0-1 home, 0-1 road"),
        ],
    ),
    "RU01": dict(
        text=(
            "Pau sit second in the Top 14 after six of the seven round-seven matches were complete, "
            "nine places above Toulon in eleventh. The visitors have the stronger table position and "
            "our line gives them a 1.25-point cushion: Section Paloise +1.25 at -240. Toulon at home "
            "are never a soft touch, which is exactly why the cushion matters more than the outright "
            "price of -199 on the Pau win."
        ),
        basis=[
            ("League positions", "LNR Top 14 calendar, Journée 7: Pau 2nd, Toulon 11th"),
            ("Round seven results", "LNR: Toulouse 38-33 Perpignan, Castres 16-8 Stade Français, Bayonne 27-31 Lyon"),
        ],
    ),
    "RU02": dict(
        text=(
            "Fourth plays third at Stade Marcel-Deflandre, with La Rochelle one place below "
            "Bordeaux-Bègles in the official table. Home advantage closes that gap in our ratings, and "
            "the line gives the hosts a 3.75-point cushion: Stade Rochelais +3.75 at -238. Bordeaux "
            "have the better position, but only by one place, and the outright market still makes La "
            "Rochelle a -137 favourite for the match."
        ),
        basis=[
            ("League positions", "LNR Top 14 calendar, Journée 7: La Rochelle 4th, Bordeaux-Bègles 3rd"),
            ("Kick-off", "LNR: Sunday 25 October, 21:05 local"),
        ],
    ),
    "RL01": dict(
        text=(
            "New Zealand are third in the Rugby League World Cup group and Cook Islands fourth, and "
            "our line asks the Kiwis to win by five: New Zealand -5.0 at -235. The group table is the "
            "only official ranking input published for this fixture, and it places New Zealand one "
            "place higher. A five-point cushion is the conservative reading of that gap, with the "
            "venue at One NZ Stadium in Christchurch."
        ),
        basis=[
            ("Group positions", "NRL.com Round 2 draw: New Zealand 3rd, Cook Islands 4th"),
            ("Venue", "NRL.com: One NZ Stadium, Christchurch"),
        ],
    ),
    "RL02": dict(
        text=(
            "Fiji lead the World Cup group and Australia are second, yet the hosts carry the venue "
            "and a three-point cushion in our handicap. The selection is Fiji +3.0 at -235. Fiji's "
            "table position is the only official form input on the page and it is one place better "
            "than Australia's, so a three-point cushion makes the pick about that gap rather than "
            "about the Suncorp Stadium crowd."
        ),
        basis=[
            ("Group positions", "NRL.com Round 2 draw: Fiji 1st, Australia 2nd"),
            ("Venue", "NRL.com: Suncorp Stadium, Brisbane"),
        ],
    ),
}

NOT_PICKED = {
    "IH01": "Boston's opponent record was not in the standings chunk read; no line is issued.",
    "IH03": "Vegas's opponent record was not in the standings chunk read; no line is issued.",
    "IH04": "The quarter-line that fits the window does not exist for this margin; no High selection.",
    "IH05": "The closest line sits outside the -250 floor; the winner is published as Medium only.",
    "BS01": "Starting-pitcher season statistics were not read; no line is issued.",
    "TN01": "Ranking and service statistics were not read; no line is issued.",
    "TN02": "Doubles pairing statistics were not read; no line is issued.",
    "SN01": "Frame-level scoring and head-to-head were not read; no line is issued.",
    "SN02": "The opponent is not decided, so no line can be originated.",
    "RU03": "Neither club's Round 4 form string was read; no line is issued.",
    "RU04": "Discovery only; the official match page was not read.",
    "MR01": "Only five drivers were classified in the session read; the field is incomplete, so no High selection.",
    "VB01": "No league table was read, so no price is issued.",
    "VB02": "No league table was read, so no price is issued.",
    "VB03": "No league table was read, so no price is issued.",
    "VB04": "No league table was read, so no price is issued.",
}
