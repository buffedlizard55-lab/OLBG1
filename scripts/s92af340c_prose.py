#!/usr/bin/env python3
"""Desk 92af340c — hand-authored High-tier predictions (session 92af340c-olbg1, 2026-10-22).

Every text is written for this desk only (not copied from the root desk, v3 or 6a081cf6
prose) and is built strictly from facts stored on the fixture row: the official-source
input values in data/fixtures.json, the verification-ledger evidence in
data/verification.json, and the desk's own fresh OLBG hub read where a row cross-
references one. Each entry names the selection, current form, recent results and the
obvious betting call, and is at least thirty words long. The validator enforces length,
uniqueness and the strict -250..+10000 High window.
"""

PROSE = {
    "nhl-2026020154": (
        "Boston have dropped just one game in regulation at TD Garden all season, going "
        "3-1-0 at home inside a 7-2-1 start worth a .750 points percentage and a plus-14 "
        "goal difference, all re-read from the official NHL standings feed in the early "
        "hours of 22 October. Nashville arrive at .563 with three overtime losses already "
        "banked and a minus-one goal difference, so the Bruins on the moneyline at -208 "
        "is the obvious selection."
    ),
    "mlb-849805": (
        "The World Series opens at American Family Field with a stark split: the Brewers "
        "won 55 of their 81 home games this year (.679) while the Rays managed 43 wins in "
        "81 away from Tampa (.531), both splits verified against the official MLB feed for "
        "gamePk 849805 on 24 October. Milwaukee at -196 is the straightforward pick, with "
        "home-field run production doing the heavy lifting."
    ),
    "mlb-849802": (
        "The same split carries into Game 2 in Milwaukee: Brewers .679 at home against "
        "Rays .531 on the road, each figure re-read from statsapi.mlb.com rather than "
        "inferred from series noise. Back-to-back nights in a loud home building usually "
        "widen that gap, and Milwaukee's -196 moneyline again rates as the sensible side, "
        "the fair mark of -169 keeping the pick comfortably inside the desk's High window."
    ),
    "cric-nz-ind-t20-2": (
        "India land in Christchurch as the ICC's No. 2 ranked T20I side on 267 rating "
        "points and reigning T20 World Cup champions, while New Zealand sit fourth on 247; "
        "the official NZC fixture list confirms the second T20I at Hagley Oval on 24 "
        "October. Recent form says the visitors are the class of this series, and India at "
        "-185 is the obvious selection."
    ),
    "ru-top14-609567": (
        "Toulouse sit top of the Top 14 after six journees on 24 points, their latest "
        "outing a 45-34 statement win over Bayonne, while Perpignan linger ninth on 13; "
        "the LNR's official match sheet 11867 confirms Saturday 24 October, 16h35 at Stade "
        "Ernest-Wallon. Toulouse -7.0 at -250 against a side eleven points below them in "
        "the table is the pick, and the desk model projects a 13-point margin."
    ),
    "rl-wc26-aus-fij": (
        "Australia opened their World Cup defence with a hard-fought 24-22 win over New "
        "Zealand and carry a 19-match World Cup winning streak into Suncorp Stadium, where "
        "the IRL ranks them No. 1 against Fiji's No. 7; official IRL match record 2573 "
        "confirms Sunday 25 October, 19:05 local. Australia -7.5 at -250 is the selection, "
        "with the desk's 14.2-point margin projection clearing the line."
    ),
    "rl-wc26-nzl-cok": (
        "The Kiwis' narrow 22-24 loss to Australia showed they can be pressed, but the "
        "IRL's No. 2 side still hosts Cook Islands, ranked No. 9, at One New Zealand "
        "Stadium in Christchurch on Sunday 25 October per official IRL match record 2572. "
        "Against opposition two tiers down the world rankings, New Zealand -8.0 at -244 is "
        "the obvious angle, and the projected 14.6-point margin gives the pick room."
    ),
    "rl-wc26-eng-fra": (
        "France were beaten 4-78 by Samoa in their World Cup opener, and that collapse is "
        "reflected in the IRL rankings gap - England No. 3, France No. 8 - as the "
        "tournament reaches HBF Park, Perth, on Saturday 24 October (official IRL record "
        "2571, 14:35 local). England -7.0 at -244 is the selection; the desk projects a "
        "13.5-point margin, suggesting the line is shorter than the expected gap."
    ),
    "hand-ehf-12046": (
        "Barca are four wins from four in EHF Champions League Group E with a plus-33 goal "
        "difference, including a 28-27 victory in the reverse fixture, while Montpellier "
        "sit third on two points at minus-nine; the official EHF round sheet confirms "
        "Thursday 22 October, 20:45 CEST at Palau Blaugrana. Barca -3.0 at -222 is the "
        "pick, and OLBG's own tipsters have swung behind the home side, 8 of 14 tips at "
        "this desk's fresh hub read."
    ),
    "aflw-r11-01": (
        "North Melbourne top the AFLW ladder after ten rounds on 36 points with a 251.9 "
        "percentage - the competition's most dominant scoring profile - while Adelaide sit "
        "ninth on 20 points at 102.4, every figure read from the official afl.com.au "
        "ladder on 22 October. The Kangaroos' -8.0 line at -244 for Sunday's North Hobart "
        "Oval outing is the clear selection, with the desk margin at 16.5 points."
    ),
    "aflw-r11-02": (
        "Geelong share the ladder-topping 36-point tally with North Melbourne, nine wins "
        "from ten at 167.2 percentage, and host Fremantle - eighth on 20 points at 104.9 "
        "percentage - at GMHBA Stadium on Saturday 24 October per the official AFLW "
        "fixture list. The Cats -7.0 at -250 is the pick: the desk's official-ladder "
        "ratings project a 15.6-point margin, more than double the handicap."
    ),
    "aflw-r11-04": (
        "Carlton arrive at IKON Park sixth on 28 points with a 133.0 percentage after ten "
        "rounds, against a GWS side fifteenth on eight points and a 68.2 percentage - the "
        "second-worst in the competition - per the official afl.com.au ladder read on 22 "
        "October. Carlton -10.0 at -250 for Sunday 25 October is the selection; the "
        "projected 18.6-point margin makes the double-digit line look short, not long."
    ),
    "aflw-r11-05": (
        "Hawthorn's five-and-five start keeps them tenth on 20 points at 101.5 percentage, "
        "but Sunday's visitor is far weaker: Essendon sit seventeenth on four points, one "
        "win from ten and a 55.6 percentage, the ladder's second-lowest, all per the "
        "official afl.com.au read of 22 October. At the Kennedy Community Centre, "
        "Hawthorn -7.0 at -250 is the obvious call - the projected 15.6-point margin is "
        "more than twice the handicap."
    ),
}

SELECTION_LABEL = {
    "nhl-2026020154": "Boston Bruins",
    "mlb-849805": "Milwaukee Brewers",
    "mlb-849802": "Milwaukee Brewers",
    "cric-nz-ind-t20-2": "India",
    "ru-top14-609567": "Stade Toulousain -7.0",
    "rl-wc26-aus-fij": "Australia -7.5",
    "rl-wc26-nzl-cok": "New Zealand -8.0",
    "rl-wc26-eng-fra": "England -7.0",
    "hand-ehf-12046": "Barça -3.0",
    "aflw-r11-01": "North Melbourne -8.0",
    "aflw-r11-02": "Geelong Cats -7.0",
    "aflw-r11-04": "Carlton -10.0",
    "aflw-r11-05": "Hawthorn -7.0",
}
