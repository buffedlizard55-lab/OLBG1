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
    # AFLW previews rewritten 2026-10-22 (T35/T63, session 92af340c-olbg1) against the official
    # afl.com.au ladder after Round 10. The former aflw-r11-03 and aflw-r11-09 previews were
    # retired with the re-price: those matches no longer grade High on the corrected ratings
    # (Bulldogs v Lions-... level on points; Brisbane 14th, not 2nd). Previous texts are in git
    # history at scripts/v3_prose.py before this commit.
    'aflw-r11-06': (
        'Gold Coast are fifth on the official AFLW ladder with 28 points from a 7-3 record and 138.9 per cent, while Richmond sit thirteenth with sixteen points, four wins from ten and 68.9 per cent. Three wins and twelve ladder points separate the clubs after ten rounds, with the match at the Suns\' own People First Stadium. Selection: Gold Coast SUNS -4.5 at 1.41.'
    ),
    'aflw-r11-07': (
        'Port Adelaide are eleventh with 16 points from a 4-6 record and 78.8 per cent; Collingwood are sixteenth on four points, having won once in ten at 56.7 per cent. A twelve-point ladder gap and three extra wins back the home side at Alberton Oval, though neither club arrives in strong form. Selection: Port Adelaide -3.5 at 1.40.'
    ),
    'aflw-r11-08': (
        'Sydney are seventh on the ladder with 28 points from 7-3 and 112.9 per cent, while West Coast hold twelfth place on sixteen points, a 4-6 record and 75.2 per cent. A gap of three wins and twelve points across ten rounds favours the Swans, who host at Henson Park. Selection: Sydney Swans -2.5 at 1.40.'
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
