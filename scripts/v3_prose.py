#!/usr/bin/env python3
"""
v3_prose.py - hand-written match previews.

Policy: every High-confidence selection carries a bespoke preview of at least 30 words that names
the participants, quotes the official form input, and states the selection in plain English. The
text is written per fixture, not generated from a template, so no two previews share a frame.
"""

HIGH_PROSE = {
    'nhl-2026020158': (
        'Florida arrive in Pittsburgh on a three-game winning run with 12 points from nine games and a plus-five goal difference. The Penguins have lost four straight and hold seven points from ten at 0.350. At PPG Paints Arena the desk takes the road side on the moneyline: Florida Panthers to win at 1.41.'
    ),
    'el-pao-bas-1022': (
        'Panathinaikos are top of the EuroLeague after six rounds at 5-1 with a plus-90 points differential; Baskonia are twentieth at 1-5 and minus-60, a 150-point swing between them. Round 7 is at the Telekom Center in Athens, and the desk prices that gap through the handicap: Panathinaikos -1 at 1.40.'
    ),
    'pdc-ec-16': (
        'Josh Rock is seeded tenth of 32 for the Machineseeker European Championship and Chris Dobey twenty-third, a thirteen-place gap in the draw. Their Round 1 tie is best of 11 legs at the Westfalenhalle in Dortmund on Friday, and the desk takes the higher seed: Josh Rock to win at 1.42.'
    ),
    'aflw-r11-07': (
        'Port Adelaide are eleventh on the AFLW ladder with 20 points from a 5-5 season, two wins and eight points clear of Collingwood, who are fifteenth at 3-7. Round 11 is at Alberton Oval, and the desk backs the home side outright: Port Adelaide to win at 1.41.'
    ),
    'aflw-r11-09': (
        'Brisbane are second on the AFLW ladder with 32 points from 8-2 and travel to RSEA Park to face St Kilda, who are tenth on 20 points at 5-5. Three wins and twelve ladder points separate the sides, so the desk lays three points: Brisbane Lions -3 at 1.40.'
    ),
    'aflw-r11-03': (
        'Melbourne are third with 32 points from an 8-2 start and visit Mission Whitten Oval, where the Western Bulldogs are twelfth on 16 points at 4-6. Four wins and sixteen ladder points divide the teams, and the desk lays 6.5 points: Melbourne -6.5 at 1.41.'
    ),
    'rl-wc26w-sam-wal': (
        "Samoa Women sit fifth in the IRL women's rankings and Wales seventh, but Wales arrive at CommBank Stadium after conceding 70 points in a 6-70 Round 1 defeat by England Women. That recent result is why the desk lays more than a point: Samoa Women -1.5 at 1.40."
    ),
    'rl-wc26-tga-lbn': (
        'Tonga hold fifth place on the IRL list and Lebanon eleventh, a six-place gap before Round 2 at CommBank Stadium in Sydney. The desk prices that ranking edge into the handicap rather than the moneyline: Tonga -2.5 at 1.40.'
    ),
    'rl-wc26-eng-fra': (
        'England are third in the IRL world rankings and France eighth, and France conceded 78 points in a 4-78 Round 1 defeat by Samoa. Round 2 is at HBF Park in Perth, where the desk is willing to lay more than a converted try: England -9.5 at 1.42.'
    ),
    'hand-ehf-12048': (
        'Magdeburg lead their EHF Champions League group on eight points from a 4-0-0 start, while Kolstad are fourth with nothing from four rounds at 0-0-4. The Round 5 tie is at the Trondheim Spektrum, and the desk lays a single goal: SC Magdeburg -1 at 1.41.'
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
