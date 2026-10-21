"""Source-bounded high-pick display labels and original prediction prose.

Every sentence in ``HIGH_PREDICTION_TEXTS`` is limited to the versioned fixture
inputs exported from the linked governing-body pages.  The ``{selection}``
placeholder is an independently originated model line, not a bookmaker price.
"""
from __future__ import annotations

HIGH_PREDICTION_LINES: dict[str, str] = {
    "nhl-2026020152": "Buffalo Sabres — Match Winner @ 1.42 (also Sabres -1.5 Puck Line @ 2.05)",
    "nhl-2026020154": "Boston Bruins — Match Winner @ 1.48 (lean Bruins -1.5 @ 2.19)",
    "nhl-2026020158": "Florida Panthers — Match Winner @ 1.47 (secondary Panthers -1.5 @ 2.15)",
    "nhl-2026020160": "Vegas Golden Knights — Match Winner @ 1.49 (puck line -1.5 @ 2.20)",
    "nba-sac-lac-20261021": "LA Clippers — Match Winner @ 1.30 & Clippers -8.5 Point Spread @ 1.92",
    "el-535921": "Real Madrid — Match Winner @ 1.29 & Real Madrid -9.0 Spread @ 1.94",
    "el-535923": "Panathinaikos — Match Winner @ 1.22 (also Panathinaikos -11.0 @ 1.95)",
    "mlb-849805": "Milwaukee Brewers — Game 1 Moneyline @ 1.51 (Under/Over 7.5 priced @ 1.90)",
    "mlb-849802": "Milwaukee Brewers — Game 2 Moneyline @ 1.51 (Brewers -1.5 Run Line @ 2.00)",
    "mlb-849804": "Tampa Bay Rays — Game 3 Moneyline @ 1.61 (Rays +1.5 / ML home split edge)",
    "mlb-849803": "Tampa Bay Rays — Game 4 Moneyline @ 1.61 (paired with Under 7.5 @ 1.90 lean)",
    "ten-ningbo-rybakina": "Elena Rybakina — Match Winner @ 1.08 & Rybakina -4.5 Games Handicap @ 2.01",
    "ten-902093": "Belinda Bencic — Match Winner @ 1.30 & Bencic -2.5 Games Handicap @ 2.02",
    "snk-higgins-jones": "John Higgins — Match Winner @ 1.35 (secondary Higgins -1.5 Frames @ 2.06)",
    "snk-zhang-williams": "Mark Williams — Match Winner @ 1.47 (value lean Over 5.5 Frames @ 1.77)",
    "pdc-ec-03": "Niels Zonneveld — Match Winner @ 1.41 (also Zonneveld -1.5 Legs @ 2.05)",
    "pdc-ec-09": "Ryan Joyce — Match Winner @ 1.38 & Joyce -1.5 Legs Handicap @ 1.99",
    "pdc-ec-12": "Jonny Clayton — Match Winner @ 1.34 (lean Clayton -2.0 Legs @ 2.19)",
    "pdc-ec-14": "Wessel Nijman — Match Winner @ 1.36 & Nijman -1.5 Legs @ 1.93",
    "cric-nz-ind-t20-1": "India — 1st T20I Match Winner @ 1.54 (also India -7.5 Runs/Eq @ 1.91)",
    "cric-nz-ind-t20-2": "India — 2nd T20I Match Winner @ 1.54 (paired with Over 339.5 Runs @ 1.90 lean)",
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
    "nhl-2026020152": (
        "Buffalo have played to a 4-3-2 record, a .556 points percentage and a plus-two goal difference. Philadelphia are 2-6-3 and minus-14, and their road line reads 0-4-2, which is the detail that decides this for us. Early-season samples are small, but a six-game winless run away from home is the kind of form we will not ignore. Back Buffalo Sabres on the moneyline: {selection}"
    ),
    "nhl-2026020154": (
        "Boston are 7-2-1 for .750 and plus-14, and they have defended TD Garden at 3-1-0 so far. Nashville carry a .563 points percentage with a goal difference of exactly zero, so the Predators have been neither better nor worse than break-even. Home ice plus a much healthier differential is the whole case, and it is a strong one. We are with Boston Bruins: {selection}"
    ),
    "nhl-2026020158": (
        "Pittsburgh’s 3-6-1 start has turned into four straight defeats, the longest current slide in this dataset. Florida are 5-2-2 and winners of three in a row, though they arrive on the back end of a back-to-back after facing Ottawa. Even allowing for tired legs, a .667 side against a .350 side is a mismatch worth taking. Florida Panthers: {selection}"
    ),
    "nhl-2026020160": (
        "St. Louis are an even 4-4-1 and .500, with nothing in the record to suggest they separate from the pack. At our pricing snapshot Vegas were the better team by a distance: 8-2-0, .800, riding a three-game win streak. The Blues’ building narrows that edge without erasing it. We side with Vegas Golden Knights: {selection}"
    ),
    "nba-sac-lac-20261021": (
        "Opening night gives no current-season form, so the only measured input is the final 2025-26 record: the Clippers at 42-40 (.512) against Sacramento’s 22-60 (.268). Twenty wins is a wide gap inside the same conference, and the game is at Intuit Dome. Nothing else in the verified file contradicts it. We take LA Clippers on the moneyline: {selection}"
    ),
    "el-535921": (
        "Real Madrid have opened this EuroLeague season at 4-2; Maccabi Tel Aviv are 2-4 through the same six rounds. The fixture is staged at Aleksandar Nikolic Hall in Belgrade rather than in Israel, so Maccabi do not get their own floor. Two extra wins in a short sample is not decisive, yet it is the only form we can verify. Real Madrid: {selection}"
    ),
    "el-535923": (
        "Panathinaikos sit 4-2 after six EuroLeague rounds and return to OAKA, a setting our model weights as one of the strongest home venues in the competition. Baskonia are 2-4 across the same period. Here the better record and the better building belong to the same team, which is rarer than it sounds. Panathinaikos are the play: {selection}"
    ),
    "mlb-849805": (
        "Game 1 of the World Series sends Tampa Bay to American Family Field, where Milwaukee went 55-26 (.679) in the regular season. The Rays were 43-38 away from Tropicana Field (.531). Both clubs won their league pennants to get here, but the home and road splits are the clearest verified separator in the file, and they belong to the Brewers. Milwaukee Brewers take the opener: {selection}"
    ),
    "mlb-849802": (
        "Game 2 repeats the matchup and the arithmetic: Milwaukee’s home record reads 55-26 (.679) while Tampa Bay’s road record sits at 43-38 (.531). A single game does not rewrite a 162-game sample, so the case for the home side is unchanged from the opener. We stay on Milwaukee Brewers: {selection}"
    ),
    "mlb-849804": (
        "The series moves to Tropicana Field for Game 3 and the splits move with it. Tampa Bay finished 55-26 (.679) at home; Milwaukee were a respectable but lesser 48-33 (.593) on the road. That gap in winning percentage is why the same model that liked the Brewers in Games 1 and 2 now flips. Tampa Bay Rays are the pick: {selection}"
    ),
    "mlb-849803": (
        "Game 4 keeps the World Series at Tropicana Field, where Tampa Bay posted that 55-26 (.679) home mark across 2026. Milwaukee’s road record of 48-33 (.593) is good without matching it. Venue advantage now belongs to the Rays, and the stored regular-season splits are the only inputs we need to say so. Tampa Bay Rays to win: {selection}"
    ),
    "ten-ningbo-rybakina": (
        "Rybakina arrives as world No. 1, the top seed and the defending champion in Ningbo, which is about as complete a profile as a WTA 500 draw can offer. Kudermetova is ranked No. 103. Rankings do not settle three-set matches on their own, but 102 places plus title history at the venue is a margin we are happy to price. Elena Rybakina: {selection}"
    ),
    "ten-902093": (
        "Bencic is the world No. 12 and seeded fifth in Ningbo; Kawa is ranked No. 124 and came through qualifying. Qualifiers can carry momentum into a main draw, yet 112 ranking places is exactly the sort of edge our model leans on in a best-of-three format. Belinda Bencic is our selection: {selection}"
    ),
    "snk-higgins-jones": (
        "John Higgins is the world No. 6 and Jak Jones is No. 24, an 18-place gap on the WST two-year list. Both men can run deep in Belfast, but that table rewards the week-in, week-out consistency which tends to settle best-of-seven frames. Our model makes Higgins clear favourite and the ranking supports it. John Higgins to win: {selection}"
    ),
    "snk-zhang-williams": (
        "Mark Williams sits eighth on the WST world list; Zhang Anda is 21st. That 13-place separation is the only verified form input for this second-round tie, and in a short best-of-seven it counts for more than it looks, because the higher-ranked player usually controls the safety exchanges. We take Mark Williams: {selection}"
    ),
    "pdc-ec-03": (
        "Zonneveld arrives in Dortmund as the fourth seed for the European Championship; Menzies is seeded 29th. Seeding here reflects a season of European Tour results rather than one hot weekend, which is the sample we want for a first-round tie. A gap of 25 places is substantial. Niels Zonneveld is our call: {selection}"
    ),
    "pdc-ec-09": (
        "Ryan Joyce is seeded third for this event, Jermaine Wattimena 30th. A 27-place gap in the European Tour standings points to a clear favourite in a short-format first round, where one break of throw so often settles matters. We are backing the higher seed to justify it. Ryan Joyce to advance: {selection}"
    ),
    "pdc-ec-12": (
        "Jonny Clayton tops the European Tour seeding for Dortmund at No. 1; Niko Springer is No. 32, the last man into the field. On season-long order-of-merit evidence that is the widest gap in the first round. Clayton holds the top seed because his results earned it. Jonny Clayton: {selection}"
    ),
    "pdc-ec-14": (
        "Wessel Nijman is seeded second and Martin Schindler 31st, a 29-place split. German crowds will be behind Schindler and stage support is real, but seeding is built from results and Nijman’s have been far stronger across the tour. On verified inputs the edge is unambiguous. Wessel Nijman to win: {selection}"
    ),
    "cric-nz-ind-t20-1": (
        "India are the ICC’s No. 2 Men’s T20I side on 267 rating points and the reigning T20 World Cup winners. New Zealand sit fourth on 247. Twenty rating points is a meaningful gap in a format this short, and it is the only measured comparison we hold for the series opener at Hagley Oval. India are our pick: {selection}"
    ),
    "cric-nz-ind-t20-2": (
        "The second T20I stays at Hagley Oval with the same ratings attached: India No. 2 on 267, New Zealand No. 4 on 247. Squads do not change 48 hours apart, so neither does our read of the series. We are with India again for the second instalment: {selection}"
    ),
    "cric-ausw-nzw-t20-3": (
        "Australia Women lead the ICC Women’s T20I table on 287 rating points; New Zealand Women are fourth on 253. A 34-point cushion is the largest rating gap anywhere in this dataset, and the match is at North Sydney Oval in Australia. That combination is why our model makes the hosts strong favourites. Australia Women: {selection}"
    ),
    "ru-top14-609567": (
        "Toulouse top the Top 14 after six rounds on 24 points and arrive off a 45-34 win over Bayonne. Perpignan are ninth on 13, eleven points adrift. Stade Ernest-Wallon is a hard place to travel to at the best of times, and the standings say this is not the best of times for the visitors. Stade Toulousain to win: {selection}"
    ),
    "rl-wc26-aus-fij": (
        "Australia are ranked No. 1 by the IRL, opened their World Cup with a 24-22 win over New Zealand and have won 19 straight World Cup matches. Fiji are ranked seventh. That streak is the most striking verified statistic in this dataset, and nothing in Fiji’s ranking suggests it ends at Suncorp Stadium. Australia: {selection}"
    ),
    "rl-wc26-nzl-cok": (
        "New Zealand are the IRL’s No. 2 side and lost their opener to Australia by two points, 22-24, a far better performance than a defeat usually implies. Cook Islands are ranked ninth. The Kiwis’ response to a narrow loss is the angle here, and the ranking gap backs it up. We take New Zealand: {selection}"
    ),
    "rl-wc26-eng-fra": (
        "England are ranked third in the world by the IRL. France are eighth and come into this off a 4-78 defeat by Samoa in Round 1, a 74-point margin that is hard to read any other way. HBF Park in Perth hosts the tie, and the verified evidence points one direction. England are the clear selection: {selection}"
    ),
    "hand-ehf-12044": (
        "Aalborg are second in Group C at 3-1-0 with seven points, a plus-21 goal difference and a 36:26 win in Celje already on the record. Celje are bottom at 0-0-4, minus-34. Head-to-head evidence this one-sided is rare in the Champions League, and the reverse fixture was not close. Aalborg Håndbold: {selection}"
    ),
    "hand-ehf-12046": (
        "Barça lead Group E at 4-0-0 with eight points and a plus-33 goal difference, and they have already beaten Montpellier 28:27 away. The French side are third at 1-0-3, minus-9. A one-goal road win warns against expecting a blowout, but the standings still point firmly to the hosts at Palau Blaugrana. Barça: {selection}"
    ),
    "aflw-r11-01": (
        "North Melbourne are unbeaten in the AFLW: ten wins from ten, 40 points, top of the ladder after Round 10. Adelaide are ninth on 20 points at 5-5. A perfect record against a .500 side is about as one-sided as this competition gets, and the game is at Arden Street. North Melbourne are our pick: {selection}"
    ),
    "aflw-r11-04": (
        "Carlton sit sixth on 24 points with a 6-4 record, while GWS are 16th on eight points at 2-8. The ladder gap is ten places and the win gap is four, which in a ten-round season is the difference between chasing finals and rebuilding. IKON Park hosts it. Carlton to win: {selection}"
    ),
    "aflw-r11-05": (
        "Hawthorn are fourth on 32 points at 8-2; Essendon are 14th on 14 points with a 3-6-1 record. The Hawks have won five more games than the Bombers and lost four fewer, and the fixture is at Kinetic Stadium. Our model makes Hawthorn clear favourites and the ladder supports it. Hawthorn: {selection}"
    ),
}
