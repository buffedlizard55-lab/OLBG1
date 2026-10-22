#!/usr/bin/env python3
"""
v3_prose.py - hand-written match previews.

Policy: every High-confidence selection carries a bespoke preview of at least 30 words that names
the participants, quotes the official form input, and states the selection in plain English. The
text is written per fixture, not generated from a template, so no two previews share a frame.
"""

HIGH_PROSE = {
    'nhl-2026020158': (
        'Pittsburgh have lost four in a row and own seven points from ten games with a minus-five goal differential, while Florida have won three straight and carry twelve points from nine with a plus-five mark. The Panthers have taken five more points from one fewer game. Selection: Florida Panthers to win at 1.41.'
    ),
    'el-pao-bas-1022': (
        'Panathinaikos lead the EuroLeague at 5-1 with a plus-90 point differential, while Baskonia are last at 1-5 and minus-60, a 150-point gap across six rounds. The Greek side also has the deeper rotation and the home floor at the Telekom Center. Selection: Panathinaikos -1 at 1.40.'
    ),
    'pdc-ec-16': (
        'Josh Rock enters as the tenth seed of 32 while Chris Dobey is seeded twenty-third, a thirteen-place gap on the European Tour order of merit. Over a best-of-eleven first round the model turns that seeding edge into a clear match price. Selection: Josh Rock to win at 1.42.'
    ),
    'aflw-r11-07': (
        'Port Adelaide sit eleventh on the AFLW ladder with 20 points from a 5-5 record, while Collingwood are fifteenth on 12 points at 3-7. The Power have won two more matches and eight more ladder points across ten rounds, and this one is at Alberton. Selection: Port Adelaide to win at 1.41.'
    ),
    'aflw-r11-09': (
        'Brisbane are second on 32 points after an 8-2 start and travel to RSEA Park to meet St Kilda, tenth on 20 points at 5-5. Three wins and twelve ladder points separate them, and the model makes the Lions a three-point road favourite. Selection: Brisbane Lions -3 at 1.40.'
    ),
    'aflw-r11-03': (
        'Melbourne are third with 32 points from 8-2 and visit Mission Whitten Oval, where the Western Bulldogs are twelfth on 16 points at 4-6. Four wins and sixteen ladder points divide the sides after ten rounds of the official ladder. Selection: Melbourne -6.5 at 1.41.'
    ),
    'rl-wc26w-sam-wal': (
        "Samoa Women are ranked fifth in the IRL women's rankings; Wales are seventh and arrive after a 6-70 loss to England Women in Round 1. The two-place ranking gap understates the form difference, which is why the line sits at a converted try and a half. Selection: Samoa Women -1.5 at 1.40."
    ),
    'rl-wc26-tga-lbn': (
        "Tonga occupy fifth place on the IRL world list and Lebanon eleventh, a six-place gap. Round 2 at CommBank Stadium follows Lebanon's physical opener, and the model still expects Tonga to control the middle third through their forward rotation. Selection: Tonga -2.5 at 1.40."
    ),
    'rl-wc26-eng-fra': (
        "England are ranked third in the world and France eighth, and France conceded 78 points in a 4-78 Round 1 defeat by Samoa. England's pack and edge defence are the reason the desk is prepared to lay more than a converted try at HBF Park. Selection: England -9.5 at 1.42."
    ),
    'hand-ehf-12048': (
        "Magdeburg top their EHF Champions League group at 4-0-0 for eight points, while Kolstad are fourth at 0-0-4 having taken nothing from four rounds. The German side's perfect record and superior goal difference underpin a one-goal handicap in Trondheim. Selection: SC Magdeburg -1 at 1.41."
    ),
}

# Short, factual one-line summaries used on the sport pages for every priced fixture.
def auto_summary(fx: dict) -> str:
    hi = fx.get("home_input") or {}
    ai = fx.get("away_input") or {}
    bits = []
    if hi.get("value"):
        bits.append(f"{fx['home']}: {hi['value']}")
    if ai.get("value"):
        bits.append(f"{fx['away']}: {ai['value']}")
    return " | ".join(bits)
