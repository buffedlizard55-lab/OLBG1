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
        "Buffalo’s recorded NHL mark is 4-3-2, a .556 points percentage with a plus-two goal differential. "
        "Philadelphia’s source-linked record is 2-6-3, .318, including 0-4-2 away and minus-14 overall. "
        "That documented early-season contrast leads to Buffalo Sabres Match Winner: {selection}."
    ),
    "nhl-2026020154": (
        "Boston’s official snapshot shows 7-2-1, a .750 points percentage, 5-1-0 at home and plus-14 goal difference. "
        "Nashville are listed at 3-2-3 with a .563 percentage and level goal difference. "
        "The recorded Bruins advantage supports this Boston Bruins selection: {selection}."
    ),
    "nhl-2026020158": (
        "Pittsburgh arrive with a 3-6-1 record, .350 points percentage and an L4 losing streak in the official table. "
        "Florida’s corresponding entry is 5-2-2, .667, with a W3 winning streak. "
        "For this fixture, the stored current form comparison backs Florida Panthers Match Winner: {selection}."
    ),
    "nhl-2026020160": (
        "St. Louis are recorded at 4-4-1 and a .500 points percentage, while Vegas carry an 8-2-0 record, .800, plus a W3 streak. "
        "Those are the full source-linked form inputs retained for the matchup. "
        "The independent model therefore selects Vegas Golden Knights: {selection}."
    ),
    "nba-sac-lac-20261021": (
        "The prior-season NBA records stored for this opening-week comparison are 42-40 (.512) for the LA Clippers and 22-60 (.268) for Sacramento. "
        "No additional lineup or tactical claim is used in this note. "
        "The resulting LA Clippers Match Winner model line is {selection}."
    ),
    "el-535921": (
        "Maccabi Tel Aviv’s official EuroLeague entry is 2-4 (.333), whereas Real Madrid’s is 4-2 (.667). "
        "This six-game record split is the only current form evidence cited for the Round 7 matchup. "
        "The selection is Real Madrid Match Winner: {selection}."
    ),
    "el-535923": (
        "Panathinaikos are listed 4-2 (.667) in the EuroLeague snapshot; Baskonia are listed 2-4 (.333). "
        "The write-up relies on that published league comparison and does not add an unsupported playing-style judgment. "
        "Panathinaikos Match Winner is the model choice: {selection}."
    ),
    "mlb-849805": (
        "For World Series Game 1, Milwaukee’s stored 2026 home record is 55-26 (.679), while Tampa Bay’s stored road record is 43-38 (.531). "
        "These home-road figures are the documented form split used by the model. "
        "Milwaukee Brewers Game 1 Moneyline is the selection: {selection}."
    ),
    "mlb-849802": (
        "Game 2 retains Milwaukee’s recorded 55-26 home mark (.679) against Tampa Bay’s recorded 43-38 road mark (.531). "
        "The source-linked split is presented without a starter, bullpen or matchup assertion. "
        "The Milwaukee Brewers model preference for this second game is {selection}."
    ),
    "mlb-849804": (
        "Tampa Bay’s Game 3 entry carries a 55-26 home record (.679); Milwaukee’s paired road entry is 48-33 (.593). "
        "Those published splits are the only historical record comparison stated here. "
        "For the third contest, the originated Tampa Bay Rays selection is {selection}."
    ),
    "mlb-849803": (
        "The Game 4 source snapshot again places Tampa Bay at 55-26 at home (.679) and Milwaukee at 48-33 away (.593). "
        "No pitching, injury or tactical information has been added beyond those records. "
        "The desk’s fourth-game Tampa Bay Rays choice is {selection}."
    ),
    "ten-ningbo-rybakina": (
        "Elena Rybakina is recorded No. 1, seed 1 and defending champion, while Polina Kudermetova is recorded No. 103. "
        "Those WTA ranking descriptors are the full source-backed player form context in this preview. "
        "The Match Winner selection is Elena Rybakina: {selection}."
    ),
    "ten-902093": (
        "Katarzyna Kawa is listed as No. 124 and a qualifier; Belinda Bencic is listed No. 12 and seed 5. "
        "The note uses that official rankings contrast without making a surface or injury claim. "
        "Belinda Bencic is the proposed Match Winner selection: {selection}."
    ),
    "snk-higgins-jones": (
        "The WST rankings recorded for this Round 2 match are John Higgins at No. 6 and Jak Jones at No. 24. "
        "That is the complete player-comparison evidence used for the best-of-seven fixture. "
        "The independent line identifies John Higgins Match Winner as {selection}."
    ),
    "snk-zhang-williams": (
        "Zhang Anda’s stored WST rank is 21, while Mark Williams’ stored WST rank is 8. "
        "No potting, safety or tactical statistic is claimed outside the published ranking pair. "
        "The model’s match-winner call is Mark Williams: {selection}."
    ),
    "pdc-ec-03": (
        "Niels Zonneveld enters with the recorded European Tour seed of No. 4; Cameron Menzies is recorded as seed No. 29. "
        "Those official seed positions provide the limited comparison for this best-of-11 opener. "
        "Niels Zonneveld Match Winner is the originated selection: {selection}."
    ),
    "pdc-ec-09": (
        "Ryan Joyce is listed as European Tour seed No. 3, and Jermaine Wattimena as seed No. 30. "
        "The preview keeps to those published seed values rather than asserting checkout or scoring statistics. "
        "The model points to Ryan Joyce Match Winner: {selection}."
    ),
    "pdc-ec-12": (
        "The PDC source inputs show Jonny Clayton at seed No. 1 and Niko Springer at seed No. 32. "
        "That seeding spread is the sole documented current tournament context retained here. "
        "For the opening round, Jonny Clayton is selected: {selection}."
    ),
    "pdc-ec-14": (
        "Wessel Nijman’s official European Tour seed is No. 2, compared with Martin Schindler’s No. 31. "
        "This text does not infer crowd, scoring or finishing performance beyond that seed gap. "
        "The resulting Wessel Nijman Match Winner line is {selection}."
    ),
    "cric-nz-ind-t20-1": (
        "New Zealand are recorded No. 4 on 247 in the men’s T20I rating, while India are No. 2 on 267 and labelled T20 World Cup winners. "
        "Those published team markers are the current-series context used for the first T20I. "
        "India Match Winner is the source-bounded selection: {selection}."
    ),
    "cric-nz-ind-t20-2": (
        "For the second T20I, the stored ICC values remain New Zealand No. 4 (247) and India No. 2 (267), with India labelled T20 World Cup winners. "
        "No player availability or tactical statement is added to that ratings comparison. "
        "The model again selects India Match Winner: {selection}."
    ),
    "cric-ausw-nzw-t20-3": (
        "Australia Women are listed No. 1 on 287 in the women’s T20I ratings, and New Zealand Women No. 4 on 253. "
        "The 34-point ranking separation is the recorded form context kept for this third T20I. "
        "Australia Women Match Winner is the independent selection: {selection}."
    ),
    "ru-top14-609567": (
        "Stade Toulousain are first after six Top 14 rounds with 24 points and a recorded 45-34 win over Bayonne; USA Perpignan are ninth on 13 points. "
        "Those official table details are the complete recent-result comparison used in this preview. "
        "The model selects Stade Toulousain Match Winner: {selection}."
    ),
    "rl-wc26-aus-fij": (
        "Australia are recorded No. 1, having beaten New Zealand 24-22 in Round 1 and carrying 19 straight World Cup wins; Fiji are No. 7. "
        "That published ranking and tournament-history information is the basis used here. "
        "Australia Match Winner is the model selection: {selection}."
    ),
    "rl-wc26-nzl-cok": (
        "New Zealand are recorded No. 2 after a 22-24 opening loss to Australia, while Cook Islands are No. 9. "
        "The official Round 1 result and ranking difference form the stated recent-match comparison. "
        "The selection for this fixture is New Zealand Match Winner: {selection}."
    ),
    "rl-wc26-eng-fra": (
        "England’s listed IRL ranking is No. 3; France are No. 8 and their stored Round 1 result is a 4-78 loss to Samoa. "
        "These are the only tournament-history facts carried into the model note. "
        "England Match Winner receives the desk’s selection: {selection}."
    ),
    "hand-ehf-12044": (
        "Aalborg are second in Group C at 3-1-0, seven points and plus-21, with a recorded 36-26 win at Celje. "
        "Celje are fourth at 0-0-4, zero points and minus-34. "
        "That table and prior-result evidence supports Aalborg Håndbold Match Winner: {selection}."
    ),
    "hand-ehf-12046": (
        "Barça lead Group E at 4-0-0, eight points and plus-33, including a recorded 28-27 win over Montpellier. "
        "Montpellier are third at 1-0-3, two points and minus-nine. "
        "The source-linked group comparison leads to Barça Match Winner: {selection}."
    ),
    "aflw-r11-01": (
        "North Melbourne top the recorded AFLW Round 10 ladder on 40 points at 10-0; Adelaide Crows are ninth on 20 points at 5-5. "
        "Those ladder records are the complete current-season form comparison used. "
        "The North Melbourne model preference is Match Winner: {selection}."
    ),
    "aflw-r11-04": (
        "Carlton sit sixth in the stored Round 10 AFLW ladder with 24 points from 6-4, whereas GWS GIANTS are sixteenth on eight points from 2-8. "
        "No extra roster or playing-style conclusion is attached to that table gap. "
        "The independent call is Carlton Match Winner: {selection}."
    ),
    "aflw-r11-05": (
        "Hawthorn are fourth on the official Round 10 ladder with 32 points at 8-2; Essendon are fourteenth on 14 points at 3-6-1. "
        "This recorded ladder split is the current form detail behind the model. "
        "Hawthorn Match Winner is the nominated selection: {selection}."
    ),
}
