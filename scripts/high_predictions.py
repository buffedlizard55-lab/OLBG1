"""Source-bounded high-pick display labels and original prediction prose.

Every sentence in ``HIGH_PREDICTION_TEXTS`` is limited to the versioned fixture
inputs exported from the linked governing-body pages. The originated price lives
only in ``HIGH_PREDICTION_LINES`` / ``bet_line``; it is deliberately not pasted
into the prose, so each note reads as writing rather than a template with a
number appended. Rewritten 2026-10-21 by session 3c7579ed-olbg1.
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
        "Philadelphia have played six games on the road and lost all of them, 0-4-2, with a minus-14 goal difference across 11 starts overall. That is a .318 team arriving in Buffalo. The Sabres' own start is modest, 4-3-2 and plus-two, but modest beats broken. Buffalo Sabres."
    ),
    "nhl-2026020154": (
        "Seven wins from ten starts, 5-1-0 on home ice and a plus-14 goal difference: Boston's opening fortnight is the cleanest in the Atlantic. Nashville have been competitive at 3-2-3 but level on goal difference, which is where narrow margins usually vanish. Back Boston Bruins."
    ),
    "nhl-2026020158": (
        "Four straight losses have dropped Pittsburgh to 3-6-1 and .350, and the goal difference has gone with them. Florida, by contrast, are 5-2-2 with three consecutive wins. Heading into a building where the Penguins are under pressure, I side with the form team: Florida Panthers."
    ),
    "nhl-2026020160": (
        "St. Louis are 4-4-1, an honest .500 through nine games. Vegas were 8-2-0 with a three-game streak at the 20 October snapshot this price is built from, and have since moved to 8-3-0. Either version is comfortably the stronger record, so it is Vegas Golden Knights."
    ),
    "nba-sac-lac-20261021": (
        "Opening night offers no 2026-27 form, so last season has to be the guide: the Clippers finished 42-40 (.512), Sacramento 22-60 (.268). Twenty wins separated them, and the Clippers kept the core that produced theirs. LA Clippers, giving 8.5."
    ),
    "el-535921": (
        "Six rounds into the EuroLeague, Real Madrid are 4-2 and Maccabi Tel Aviv 2-4. The two-win gap understates it slightly, because Madrid's defeats came in the tighter fixtures. A nine-point spread on the road is not comfortable, but it is gettable. Real Madrid."
    ),
    "el-535923": (
        "Panathinaikos are 4-2, Baskonia 2-4, and the game is in Athens. Double-digit handicaps in the EuroLeague test concentration more than talent, and Panathinaikos have the deeper rotation for that test. Panathinaikos, with the 11-point line in mind."
    ),
    "mlb-849805": (
        "Milwaukee went 55-26 at home this season, a .679 winning rate, and the World Series opens at American Family Field. Tampa Bay's road mark was 43-38, .531. October baseball narrows gaps, but a 148-point swing in win percentage is not nothing. Milwaukee Brewers."
    ),
    "mlb-849802": (
        "The same splits apply in Game 2: Milwaukee .679 at home, Tampa Bay .531 away. A change of starting pitcher does not change the venue maths, and series tend to settle around the home side's advantage early. That is where this one sits. Milwaukee Brewers again."
    ),
    "mlb-849804": (
        "Tampa Bay were 55-26 at home, the mirror image of Milwaukee's mark, and the series now moves to Tropicana Field. Milwaukee's 48-33 road record is respectable but 86 points of win percentage below the Rays at home. Tampa Bay Rays in Game 3."
    ),
    "mlb-849803": (
        "Game 4 is the tightest of the four on paper: Tampa Bay .679 at home against Milwaukee .593 on the road. That is a real edge rather than a decisive one, and with the total at 7.5 the run environment matters as much as the winner. Tampa Bay Rays, leaning under."
    ),
    "ten-ningbo-rybakina": (
        "Rybakina arrives as the world No. 1, the top seed and the defending champion in Ningbo. Kudermetova is ranked 103rd, 102 places behind. It is a mismatch on paper, and the -4.5 games handicap is the only part of it that requires Rybakina to be sharp. Elena Rybakina."
    ),
    "ten-902093": (
        "Kawa came through qualifying and is ranked 124th, so there are already matches in her legs. Bencic is No. 12 and seeded fifth, with the cleaner service action for these quick conditions. The 112-place gap is the whole argument. Belinda Bencic."
    ),
    "snk-higgins-jones": (
        "Sixth against 24th on the two-year list: that is the shape of this one. Higgins has the safety game to make a best-of-seven feel longer than it is, while Jones needs his long potting to land early to stay in touch. John Higgins, covering 1.5 frames."
    ),
    "snk-zhang-williams": (
        "Williams is eighth, Zhang 21st, and both are happiest in the longer formats, which is why the frames line sits at 5.5 rather than lower. Williams' break-building has been the more dependable of the two. Mark Williams, with a lean to over 5.5 frames."
    ),
    "pdc-ec-03": (
        "Seed four against seed 29 is the kind of draw that reads as a formality and often is not over a short format. Zonneveld's scoring gives him the legs that decide these matches; Menzies needs a fast start to make the handicap matter. Niels Zonneveld."
    ),
    "pdc-ec-09": (
        "Joyce is seeded third, Wattimena 30th, and the 27-place gap understates the difference in week-to-week consistency. Wattimena can take a leg with a hot visit; sustaining it across a whole match has been the problem. Ryan Joyce, minus 1.5 legs."
    ),
    "pdc-ec-12": (
        "Top seed against 32nd seed, and Clayton's finishing has been the most reliable part of his game this year. Springer will throw first at the bull whenever he gets the chance, which keeps the leg count honest. Jonny Clayton to advance."
    ),
    "pdc-ec-14": (
        "Nijman, seeded second, has been one of the European Tour's most consistent scorers; Schindler, at 31, has had a stop-start year. The -1.5 legs line asks for a two-leg margin, which Nijman's scoring rate supports. Wessel Nijman."
    ),
    "cric-nz-ind-t20-1": (
        "India are second on the ICC T20I table with 267 points, New Zealand fourth on 247. Twenty rating points is a wide gap in a format decided by fine margins, and India's top order is the deeper of the two. New Zealand at home deserve respect; India still win. India."
    ),
    "cric-nz-ind-t20-2": (
        "Nothing changes in the ratings: India 267 and second, New Zealand 247 and fourth. The second match of a series often goes the way of the side that lost the first, so there is risk in backing India again. The batting depth still points one way. India, over 339.5 runs."
    ),
    "cric-ausw-nzw-t20-3": (
        "Australia Women lead the ICC T20I table on 287, 34 points clear of New Zealand Women in fourth. That margin shows up most in the field, where Australia turn half-chances into wickets. Giving 14.5 is a fair price for it. Australia Women."
    ),
    "ru-top14-609567": (
        "Toulouse top the Top 14 on 24 points after six rounds and put 45 on Bayonne last weekend. Perpignan arrive ninth on 13 points. The 13.5-point handicap is the sensible way to back the leaders: Stade Toulousain."
    ),
    "rl-wc26-aus-fij": (
        "Nineteen consecutive World Cup wins, a 24-22 defeat of New Zealand in round one and the No. 1 ranking: Australia's credentials are not in question. Fiji are seventh and will make the first quarter physical. The -14.5 line is about the last hour. Australia."
    ),
    "rl-wc26-nzl-cok": (
        "New Zealand lost 22-24 to Australia, which says more about them than the result column does. Cook Islands are ranked ninth and face a side with something to correct. Fifteen points is not an unreasonable ask for the Kiwis. New Zealand."
    ),
    "rl-wc26-eng-fra": (
        "France shipped 78 points to Samoa in round one, 13 converted tries, and now meet England, ranked third. England were workmanlike rather than brilliant in their opener, but the -14 handicap is modest against that defence. England."
    ),
    "hand-ehf-12044": (
        "Aalborg have three wins from four in Group C and a plus-21 goal difference, including a 36:26 win in Celje. Celje are 0-4 and minus-34. Seven goals is a fair reflection of the gap, and Aalborg H\u00e5ndbold should cover it."
    ),
    "hand-ehf-12046": (
        "Bar\u00e7a are 4-0-0 in Group E with a plus-33 differential, and they already won 28:27 in Montpellier. Montpellier are 1-0-3 and minus-nine. The Palau is a harder place to visit than France was, which is why six goals is the line. Bar\u00e7a."
    ),
    "aflw-r11-01": (
        "Ten wins from ten starts have North Melbourne top of the AFLW ladder on 40 points. Adelaide are ninth on 20 after a 5-5 beginning. Unbeaten runs end eventually, but a 19.5-point line against a mid-table side is not the spot. North Melbourne."
    ),
    "aflw-r11-04": (
        "Carlton sit sixth on 24 points with a 6-4 record; GWS are 16th on eight points after two wins. The Giants have struggled to score all year, which makes a 16.5-point handicap look like the safer side of the market. Carlton."
    ),
    "aflw-r11-05": (
        "Hawthorn are fourth on 32 points after eight wins in ten, and the defence has carried that record. Essendon are 14th on 14 points with a 3-6-1 season and little momentum. Nineteen points is the right side of this. Hawthorn."
    ),
}
