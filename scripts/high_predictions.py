"""Source-bounded high-pick display labels and original prediction prose.

Each block was rewritten in the T17 re-verification pass (session b95dbd01-olbg1) so
the writing reads like a person who follows the competition rather than a template.
Every factual clause is limited to:

* the versioned fixture ``inputs`` exported from the linked governing-body page, and
* the selection itself, which is an independently originated model line and is
  labelled as such (never a bookmaker quote).

Numbers quoted in the prose are copied from those inputs. Where an input is a
prior-season or as-of-capture figure, the sentence says so.
"""
from __future__ import annotations

HIGH_PREDICTION_LINES: dict[str, str] = {
    "nhl-2026020152": "Buffalo Sabres — Match Winner @ 1.42 (also Sabres -1.5 Puck Line @ 2.05)",
    "nhl-2026020154": "Boston Bruins — Match Winner @ 1.48 (lean Bruins -1.5 @ 2.19)",
    "nhl-2026020158": "Florida Panthers — Match Winner @ 1.47 (secondary Panthers -1.5 @ 2.15)",
    "nba-sac-lac-20261021": "LA Clippers — Match Winner @ 1.30 & Clippers -8.5 Point Spread @ 1.92",
    "el-535921": "Real Madrid — Match Winner @ 1.29 & Real Madrid -9.0 Spread @ 1.94",
    "el-535923": "Panathinaikos — Match Winner @ 1.22 (also Panathinaikos -11.0 @ 1.95)",
    "mlb-849805": "Milwaukee Brewers — Game 1 Moneyline @ 1.51 (Over/Under 7.5 priced @ 1.90)",
    "mlb-849802": "Milwaukee Brewers — Game 2 Moneyline @ 1.51 (Brewers -1.5 Run Line @ 2.00)",
    "mlb-849804": "Tampa Bay Rays — Game 3 Moneyline @ 1.61 (Rays +1.5 / home-split edge)",
    "mlb-849803": "Tampa Bay Rays — Game 4 Moneyline @ 1.61 (Under 7.5 @ 1.90 as the secondary)",
    "ten-ningbo-rybakina": "Elena Rybakina — Match Winner @ 1.08 & Rybakina -4.5 Games Handicap @ 2.01",
    "ten-902093": "Belinda Bencic — Match Winner @ 1.30 & Bencic -2.5 Games Handicap @ 2.02",
    "snk-higgins-jones": "John Higgins — Match Winner @ 1.35 (secondary Higgins -1.5 Frames @ 2.06)",
    "snk-zhang-williams": "Mark Williams — Match Winner @ 1.47 (value lean Over 5.5 Frames @ 1.77)",
    "pdc-ec-03": "Niels Zonneveld — Match Winner @ 1.41 (also Zonneveld -1.5 Legs @ 2.05)",
    "pdc-ec-09": "Ryan Joyce — Match Winner @ 1.38 & Joyce -1.5 Legs Handicap @ 1.99",
    "pdc-ec-12": "Jonny Clayton — Match Winner @ 1.34 (lean Clayton -2.0 Legs @ 2.19)",
    "pdc-ec-14": "Wessel Nijman — Match Winner @ 1.36 & Nijman -1.5 Legs @ 1.93",
    "cric-nz-ind-t20-1": "India — 1st T20I Match Winner @ 1.54 (also India -7.5 @ 1.91)",
    "cric-nz-ind-t20-2": "India — 2nd T20I Match Winner @ 1.54 (paired with Over 339.5 Runs @ 1.90 lean)",
    "cric-nz-ind-t20-3": "India — 3rd T20I Match Winner @ 1.54 (India -7.5 @ 1.91 as the secondary)",
    "cric-ausw-nzw-t20-3": "Australia Women — Match Winner @ 1.32 & Australia W -14.5 @ 1.92",
    "ru-top14-609567": "Stade Toulousain — Match Winner @ 1.15 & Toulouse -13.5 Handicap @ 1.96",
    "rl-wc26-aus-fij": "Australia — Match Winner @ 1.16 & Kangaroos -14.5 Handicap @ 1.93",
    "rl-wc26-nzl-cok": "New Zealand — Match Winner @ 1.15 & Kiwis -15.0 Handicap @ 1.95",
    "rl-wc26-eng-fra": "England — Match Winner @ 1.18 & England -14.0 Handicap @ 1.96",
    "hand-ehf-12044": "Aalborg Håndbold — Match Winner @ 1.15 & Aalborg -7.0 Goals @ 1.96",
    "hand-ehf-12046": "Barça — Match Winner @ 1.22 & Barça -6.0 Goals Handicap @ 2.00",
    "aflw-r11-01": "North Melbourne — Match Winner @ 1.12 & Kangaroos -19.5 Line @ 1.94",
    "aflw-r11-04": "Carlton — Match Winner @ 1.18 & Blues -16.5 Points Line @ 1.94",
    "aflw-r11-05": "Hawthorn — Match Winner @ 1.13 & Hawks -19.0 Points Line @ 1.94",
}

HIGH_PREDICTION_TEXTS: dict[str, str] = {
    # ---------------------------------------------------------------- ice hockey
    "nhl-2026020152": (
        "Philadelphia are 2-6-3 for a .318 points percentage and have not won on the road yet, "
        "carrying an 0-4-2 away line and a minus-14 goal differential into Buffalo. The Sabres are "
        "nothing special at 4-3-2 and plus-two, but that is the better record of the two. Back the "
        "hosts on the moneyline and treat the -1.5 puck line as the smaller add-on: {selection}"
    ),
    "nhl-2026020154": (
        "Seven wins from ten, a .750 points percentage and a plus-14 goal difference put Boston at "
        "the top of this matchup, and they are 5-1-0 on their own ice. Nashville's 3-2-3 with a level "
        "goal differential is honest but clearly second best. Home ice plus that scoring edge makes "
        "the Bruins the side to take: {selection}"
    ),
    "nhl-2026020158": (
        "Pittsburgh's 3-6-1 start has slid into a four-game losing streak and a .350 points "
        "percentage. Florida are the opposite story at 5-2-2, .667, riding three straight wins. "
        "A team in form visiting a team in freefall is usually where the value sits, so the Panthers "
        "moneyline is the pick, with -1.5 on the puck line as the secondary: {selection}"
    ),
    # ----------------------------------------------------------------- basketball
    "nba-sac-lac-20261021": (
        "The Clippers closed the previous season 42-40 (.512) and Sacramento closed at 22-60 (.268) — "
        "a twenty-win gap that has to be respected on opening night. Sacramento must also cover a "
        "spread on the road against a team that was close to .500 a year ago. That prior-season "
        "record points to a comfortable Clippers win and a cover of 8.5: {selection}"
    ),
    "el-535921": (
        "Real Madrid are 4-2 after six EuroLeague rounds; Maccabi have slipped to 2-4, and this "
        "home game is being played in Belgrade rather than Tel Aviv. The usual home-court comfort is "
        "therefore missing for Maccabi. Real's two-win cushion plus the neutral-floor setting makes "
        "the visitors the logical side, with -9.0 the aggressive version: {selection}"
    ),
    "el-535923": (
        "Panathinaikos are 4-2 and host a Baskonia team that has lost four of six. The standings gap "
        "and the Athens crowd both lean the same way, which is why the model sets an eleven-point "
        "line. Panathinaikos on the moneyline is the main position; the handicap is worth a smaller "
        "stake at 1.95: {selection}"
    ),
    # -------------------------------------------------------------------- baseball
    "mlb-849805": (
        "Milwaukee were 55-26 at American Family Field this season (.679) and Tampa Bay travelled at "
        "43-38 (.531). Home and road splits are the cleanest inputs available for a World Series "
        "opener, and they favour the Brewers by a clear margin. Take Milwaukee on the moneyline; the "
        "7.5-run total is closer to a coin flip at this stage: {selection}"
    ),
    "mlb-849802": (
        "Game 2 offers the same pairing and the same splits — Milwaukee 55-26 at home, Tampa Bay "
        "43-38 on the road. Nothing in the official season record suggests the Brewers lose their "
        "park advantage overnight, and .679 over 81 home games is a solid base rate. The Brewers "
        "moneyline is the play again: {selection}"
    ),
    "mlb-849804": (
        "The series moves to Tropicana Field, where Tampa Bay went 55-26 (.679) while Milwaukee "
        "travelled at 48-33 (.593). The Rays' home split is the better of the two, and the visitors' "
        "road mark, good as it is, gives up ground here. Tampa Bay on the moneyline is the call, with "
        "the run line only for smaller stakes: {selection}"
    ),
    "mlb-849803": (
        "Same ballpark, same argument: Tampa Bay's .679 home record against Milwaukee's .593 road "
        "record. The Rays hold the larger home-field edge of the two clubs and the Game 4 price "
        "should say so. Our pick is the Tampa Bay moneyline, with the 7.5-run under as a secondary "
        "position: {selection}"
    ),
    # ---------------------------------------------------------------------- tennis
    "ten-ningbo-rybakina": (
        "Rybakina is the world number one, the top seed in Ningbo and the defending champion there. "
        "Kudermetova is ranked 103rd. That ninety-nine-place gap in the WTA listing attached to this "
        "row is the only ranking input used, and it points to a short match. Rybakina to win is the "
        "selection, with the games handicap the aggressive option: {selection}"
    ),
    "ten-902093": (
        "Kawa came through qualifying ranked 124th and now meets Bencic, the fifth seed at number 12. "
        "A gap of more than a hundred places is the entire basis for this position, and at WTA level "
        "that is a wide one. Bencic on the moneyline is the percentage play; the -2.5 game handicap "
        "pays better: {selection}"
    ),
    # --------------------------------------------------------------------- snooker
    "snk-higgins-jones": (
        "Higgins is sixth on the WST world ranking and Jak Jones twenty-fourth, an eighteen-place "
        "gap that counts for plenty over a best-of-seven. Both men came through the first round in "
        "Belfast, so the ranking separation is the strength input this desk used. Higgins to win is "
        "the call; -1.5 frames is the value version: {selection}"
    ),
    "snk-zhang-williams": (
        "Mark Williams sits eighth in the world and Zhang Anda twenty-first, so the ranking edge "
        "belongs to the Welshman even though Zhang carries home support in Belfast. Thirteen places "
        "is a meaningful gap over a short format. Take Williams on the match market and consider "
        "-1.5 frames at the bigger price: {selection}"
    ),
    # ---------------------------------------------------------------------- darts
    "pdc-ec-03": (
        "Zonneveld is seeded fourth for Dortmund and Menzies twenty-ninth, a twenty-five-place "
        "seeding gap that shapes the first-round draw. Seeding ranks the tour, not current scoring, "
        "so the edge is measured rather than overwhelming. Zonneveld is our pick to progress, "
        "with -1.5 legs for a smaller stake: {selection}"
    ),
    "pdc-ec-09": (
        "Ryan Joyce arrives as third seed and Jermaine Wattimena as thirtieth, the widest seeding "
        "split in this part of the draw. Both can score heavily, but the tournament seed is the only "
        "comparative input verified for the tie. Our pick is Joyce on the match market, with -1.5 "
        "legs at 1.99 for the braver version: {selection}"
    ),
    "pdc-ec-12": (
        "Top seed against thirty-second seed: Clayton is number one in Dortmund and Springer is the "
        "last man into the field. On seeding alone this is the most lopsided first-round tie of the "
        "week. Clayton to win is the obvious call, and -2.0 legs at 2.19 is where the value sits: {selection}"
    ),
    "pdc-ec-14": (
        "Nijman is seeded second and Schindler thirty-first, a gap of twenty-nine places in the "
        "Dortmund field. German crowd support for Schindler is real but is not something this desk "
        "can price from an official source. On the verified seeding input Nijman wins the match, "
        "with -1.5 legs as the secondary: {selection}"
    ),
    # -------------------------------------------------------------------- cricket
    "cric-nz-ind-t20-1": (
        "India sit second on the ICC T20I table with 267 points and New Zealand fourth on 247. That "
        "twenty-point gap is the only rating input used for the opener at Hagley Oval. New Zealand "
        "have home conditions, which is why the price has not collapsed. India to win the first T20I "
        "is the pick, with India -7.5 the aggressive add: {selection}"
    ),
    "cric-nz-ind-t20-2": (
        "India remain twenty points clear of the hosts on the ICC table, 267 to 247, and the second "
        "T20I stays at Hagley Oval. Repeating the venue means the model's adjustment is unchanged from "
        "game one, so the edge does not disappear. Back India on the match price, with the over on "
        "339.5 runs as the alternative angle: {selection}"
    ),
    "cric-nz-ind-t20-3": (
        "Wellington hosts the third T20I, and the rating picture is unchanged: the visitors are on "
        "267 ICC points, the hosts on 247. A new ground is the only material difference from the "
        "first two matches, so the same side is favoured. India to win stays the consistent call, "
        "with India -7.5 the higher-variance option: {selection}"
    ),
    "cric-ausw-nzw-t20-3": (
        "Australia Women lead the ICC T20I table on 287 points; New Zealand Women are fourth on 253. "
        "Thirty-four rating points is the largest gap on this cricket card, and the match is at North "
        "Sydney Oval. Australia Women are the pick, with the -14.5 line at 1.92 as the secondary "
        "position: {selection}"
    ),
    # ---------------------------------------------------------------- rugby union
    "ru-top14-609567": (
        "Toulouse lead the Top 14 on 24 points after six rounds and beat Bayonne 45-34 last time out. "
        "Perpignan are ninth on 13. A side scoring at that rate against a mid-table visitor is the "
        "read here, and the official match sheet places the game at Ernest Wallon. Toulouse to win, "
        "with -13.5 the handicap play: {selection}"
    ),
    # ---------------------------------------------------------------- rugby league
    "rl-wc26-aus-fij": (
        "Australia are ranked first in the world and opened the tournament by beating New Zealand "
        "24-22. Fiji are seventh. The Kangaroos also carry a nineteen-match World Cup winning run "
        "into Suncorp Stadium, and that combination of ranking and tournament history points one way. "
        "Australia to win, with -14.5 as the handicap: {selection}"
    ),
    "rl-wc26-nzl-cok": (
        "New Zealand lost their opener 22-24 to Australia — a two-point margin against the top-ranked "
        "side — and remain second in the world rankings. Cook Islands are ninth. A narrow defeat to "
        "the Kangaroos is stronger form than a bare ladder line suggests, so New Zealand to win and "
        "cover -15.0 is the call: {selection}"
    ),
    "rl-wc26-eng-fra": (
        "England are ranked third and face a France side that conceded 78 points in a 4-78 opening "
        "loss to Samoa; France sit eighth. That result is the most recent verified form line for "
        "either team. England to win the match is the pick, with -14.0 the handicap option: {selection}"
    ),
    # -------------------------------------------------------------------- handball
    "hand-ehf-12044": (
        "Aalborg are second in Group C on seven points with a plus-21 goal difference, and they "
        "already won 36:26 in Celje. Celje are bottom on zero points at minus-34. The head-to-head "
        "result and the goal difference point the same way. Aalborg to win, with -7.0 goals the "
        "handicap: {selection}"
    ),
    "hand-ehf-12046": (
        "Barça lead Group E at 4-0 with a plus-33 goal difference and beat Montpellier 28:27 in the "
        "reverse fixture. Montpellier are third on two points at minus-nine. That reverse result was "
        "close, which is why the handicap is six goals rather than double figures. Barça to win, with "
        "-6.0 the secondary: {selection}"
    ),
    # ------------------------------------------------------------------ aussie rules
    "aflw-r11-01": (
        "North Melbourne top the AFLW ladder on 40 points from a 10-0 season; Adelaide are ninth on "
        "20 from 5-5. An unbeaten home side against a mid-table visitor is about as clear as this "
        "competition gets. North Melbourne to win, with -19.5 the points line: {selection}"
    ),
    "aflw-r11-04": (
        "Carlton sit sixth on 24 points after ten games (6-4) and host a GWS side that is sixteenth "
        "on eight points from 2-8. Four wins separate them on the ladder. Carlton to win is the "
        "selection, and -16.5 on the points line is the version worth a smaller stake: {selection}"
    ),
    "aflw-r11-05": (
        "Hawthorn are fourth with 32 points from 8-2 and meet an Essendon side on 14 points from "
        "3-6-1. The Hawks have twice as many wins. Take Hawthorn on the match market, with -19.0 on "
        "the points line for a secondary position: {selection}"
    ),
}
