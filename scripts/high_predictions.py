"""Original prediction prose for every high-confidence pick (T41, session 2ca35f17-olbg1).

Rules this module is written to, and that ``scripts/validate.py`` enforces:

* one note per high-confidence pick, no more and no fewer (bijection with the priced set);
* at least 30 words, written as prose rather than a filled-in template;
* no six-word sequence is shared by two notes anywhere in the corpus;
* every factual clause is traceable to that fixture's stored, source-linked inputs
  (``data/fixtures.json`` -> ``inputs``/``competition``/``stage``/``venue``) - no outside
  knowledge, no inferred form, no player statistics we did not record from an official feed;
* the selection is stated in the text itself ("Selection: <team> -7.0") so the bet is
  unambiguous even when the price is stripped out of the sentence;
* the price lives only in ``bet_line`` (built by ``scripts/origin_lines.py`` from the
  model output), never inside the prose, so a re-price cannot leave a stale number in a
  sentence.

The previous pass priced every high pick on the moneyline.  Under the T41 price-window
rule a moneyline shorter than -250 cannot be published as a high-confidence pick, so for
those fixtures the note now explains the handicap rung that carries the same view at a
price inside the window.
"""
from __future__ import annotations

HIGH_PREDICTION_TEXTS: dict[str, str] = {
    # ---------------- Ice hockey (NHL) ----------------
    "nhl-2026020152": (
        "Buffalo bring a 4-3-2 record and a .556 points percentage into a home game against a "
        "Philadelphia side sitting at 2-6-3 with a minus-19 goal difference. The Flyers' road "
        "line reads 0-4-1, which means they have still not won away from home this season. A "
        "fourteen-goal swing in goal differential, plus home ice, is the case. "
        "Selection: Buffalo Sabres to win."
    ),
    "nhl-2026020154": (
        "Boston have opened 7-2-1 - a .750 points percentage and a plus-14 differential - and they "
        "are 3-1-0 inside TD Garden. Nashville arrive at .563 with a minus-one goal difference, a "
        "respectable but ordinary profile for a ten-game sample. Seven wins in ten for the Bruins "
        "against three in eight for the Predators settles it. Selection: Boston Bruins to win."
    ),
    "nhl-2026020158": (
        "Pittsburgh are 3-6-1 after four consecutive defeats, the longest current slide in this "
        "dataset. Florida are 5-2-2 with three straight wins and a .667 points percentage. Pittsburgh "
        "have home ice, which is the only argument in their favour, and it does not outweigh a .317 "
        "gap in points percentage. Selection: Florida "
        "Panthers to win."
    ),
    "nhl-2026020160": (
        "St. Louis sit at 4-4-1 and .500, with nothing in the record that separates them from the "
        "pack. Vegas were 8-2-0 and .800 on a three-game streak when this fixture was priced, and "
        "the official table has since moved to 8-3-0 after a defeat, a drift the row discloses. The "
        "Blues' building narrows the edge without erasing it. Selection: Vegas Golden Knights to win."
    ),
    # ---------------- Basketball ----------------
    "nba-sac-lac-20261021": (
        "Opening night leaves last season's finishing record as the only measured form, and it is "
        "lopsided: the Clippers closed 42-40 while Sacramento finished 22-60. Twenty wins of "
        "separation explains the short moneyline, and it is also why we step onto the spread "
        "instead of taking the win price. At Intuit Dome the Clippers need only be two points "
        "better. Selection: LA Clippers -2.0 on the point spread."
    ),
    "el-535921": (
        "Real Madrid are 4-2 through six EuroLeague rounds; Maccabi Tel Aviv are 2-4. The fixture "
        "is staged at Aleksandar Nikolic Hall in Belgrade rather than in Israel, so Maccabi get no "
        "home floor, and that neutral venue is already inside our rating adjustment. Two wins of "
        "separation is thin evidence for a large number, so four points is not in play. Selection: "
        "Real Madrid -2.5."
    ),
    "el-535923": (
        "Panathinaikos have started this EuroLeague season 4-2 and return to the OAKA in Athens. "
        "Baskonia are 2-4 across the same six rounds, having dropped four of their opening six. "
        "The standings gap is real but modest, which is why the handicap sits at four and a half "
        "rather than anything wider. Selection: Panathinaikos -4.5."
    ),
    # ---------------- Baseball ----------------
    "mlb-849805": (
        "Milwaukee closed the regular season 55-26 at American Family Field, a .679 home record, "
        "and the World Series opens in that ballpark. Tampa Bay were 43-38 on the road, .531, "
        "which is competent without being intimidating. A .148 difference in winning rate between "
        "the two venues is the entire argument for the home side in Game 1. Selection: Milwaukee "
        "Brewers to win."
    ),
    "mlb-849802": (
        "Game 2 stays in Milwaukee and so does the same structural edge: the Brewers were 55-26 at "
        "home (.679) across 2026, while the Rays were 43-38 away (.531). Two games in one park give "
        "the home dugout the last at-bat and the crowd. Nothing in the verified file points the "
        "other way, and the price is still inside our window. Selection: Milwaukee Brewers to win "
        "Game 2."
    ),
    # ---------------- Tennis ----------------
    "ten-ningbo-rybakina": (
        "Rybakina arrives in Ningbo as the world No. 1 and the top seed, and she is the defending "
        "champion at this event; Kudermetova is ranked No. 103. That ranking gap makes the "
        "moneyline unusable, so the games handicap has to carry the view. Laying three games asks "
        "for a controlled win rather than a flawless one. Selection: Elena Rybakina -3.0 games."
    ),
    "ten-902093": (
        "Belinda Bencic is the fifth seed and world No. 12; Katarzyna Kawa came through qualifying "
        "and sits at No. 124. Kawa came through qualifying to reach the round of 16, which is why "
        "we are not reaching for a wide games line. One game of cover still demands a "
        "straightforward Bencic win. Selection: Belinda Bencic -1.0 game."
    ),
    # ---------------- Snooker ----------------
    "snk-higgins-jones": (
        "John Higgins is the world No. 6 and Jak Jones is No. 24 going into this best-of-seven "
        "second round at the Waterfront Hall in Belfast. The ranking gap is the strongest verified "
        "input we hold on both men, and half a frame is the smallest handicap on the board: Higgins "
        "needs only to take the match. Selection: John Higgins -0.5 frames."
    ),
    "snk-zhang-williams": (
        "Mark Williams is ranked eighth in the world, Zhang Anda 21st, and the two meet over seven "
        "frames in Belfast. Our model reads world ranking on both sides, which makes Williams a "
        "clear favourite; that favouritism is priced short enough that the frame handicap adds "
        "little. We take the match winner. Selection: Mark Williams to win."
    ),
    # ---------------- Darts ----------------
    "pdc-ec-03": (
        "Niels Zonneveld is seeded fourth for the European Championship in Dortmund and Cameron "
        "Menzies is seeded 29th of the 32-player field. Over a best-of-eleven first round the seed "
        "gap is the cleanest evidence the draw gives us, and it points one way. Selection: Niels "
        "Zonneveld to win."
    ),
    "pdc-ec-09": (
        "Ryan Joyce is the third seed in Dortmund; Jermaine Wattimena is seeded 30th. Twenty-seven "
        "places separate them inside the same 32-player field, and eleven legs is short enough "
        "that seeding usually tells. Half a leg keeps the ask to a straightforward win. Selection: "
        "Ryan Joyce -0.5 legs."
    ),
    "pdc-ec-12": (
        "Jonny Clayton is seeded first for the European Championship and Niko Springer is 32nd, the "
        "widest seed gap in the draw. Our pricing treats top seed against last seed accordingly, "
        "and the moneyline is too short to sit inside our window, so the half-leg handicap is the "
        "only usable vehicle. Selection: Jonny Clayton -0.5 legs."
    ),
    "pdc-ec-14": (
        "Wessel Nijman is seeded second in Dortmund and Martin Schindler is 31st, a gap of 29 "
        "places in the same field. Nijman holds the second seed in the 32-player field, and the "
        "first round is best of eleven legs. Half a leg does not ask for a whitewash. Selection: "
        "Wessel Nijman -0.5 legs."
    ),
    # ---------------- Cricket ----------------
    "cric-nz-ind-t20-1": (
        "India sit second in the ICC Men's T20I ratings on 267 points; New Zealand are fourth on "
        "247. The series opener is at Hagley Oval in Christchurch, where home conditions help the "
        "Black Caps, and that is already in the model. Twenty rating points is the sort of gap "
        "that survives a venue adjustment. Selection: India to win the first T20I."
    ),
    "cric-nz-ind-t20-2": (
        "The second T20I stays at Hagley Oval and the ratings have not moved: India second on 267, "
        "New Zealand fourth on 247. India are the reigning T20 World Cup winners, a status already "
        "baked into that rating rather than an extra claim. The venue edge for the hosts is priced "
        "in and is not enough. Selection: India to win the second T20I."
    ),
    "cric-ausw-nzw-t20-3": (
        "Australia Women lead the ICC Women's T20I ratings on 287 points and New Zealand Women are "
        "fourth on 253. The third T20I is at North Sydney Oval, and a 34-point rating gap is one of "
        "the widest in this dataset. With the match-winner price outside our window, three runs is "
        "how we express the same view. Selection: Australia Women -3.0."
    ),
    # ---------------- Rugby union ----------------
    "ru-top14-609567": (
        "Toulouse lead the Top 14 after six rounds on 24 points and come into round seven off a "
        "45-34 win over Bayonne; Perpignan are ninth on 13 points. Eleven points and eight places "
        "separate the two sides in the official table. The match-winner price is far outside our "
        "window, so seven points carries the view instead. Selection: Stade Toulousain -7.0."
    ),
    # ---------------- Rugby league ----------------
    "rl-wc26-aus-fij": (
        "Australia are ranked first by the IRL and opened their World Cup with a 24-22 win over New "
        "Zealand, their nineteenth consecutive World Cup victory. Fiji are ranked seventh. Suncorp "
        "Stadium in Brisbane supplies a home crowd, and the six-place ranking gap is wide enough to "
        "lay more than a converted try. Selection: Australia -7.5."
    ),
    "rl-wc26-nzl-cok": (
        "New Zealand are ranked second in the world and lost their opener 22-24 to Australia, the "
        "narrowest possible margin. Cook Islands are ranked ninth, and the fixture is at One New "
        "Zealand Stadium in Christchurch. Seven ranking places separate them, and eight points is a "
        "fair way to price that difference. Selection: New Zealand -8.0."
    ),
    "rl-wc26-eng-fra": (
        "England are ranked third by the IRL; France are eighth and arrive after a 4-78 defeat by "
        "Samoa in round one. That scoreline is the most recent verified form available for either "
        "side, and it is a heavy one. HBF Park in Perth is neutral ground, which the model already "
        "accounts for. Selection: England -7.0."
    ),
    # ---------------- Handball ----------------
    "hand-ehf-12044": (
        "Aalborg are second in Group C at 3-1-0 with a plus-21 goal difference, and they won 36:26 "
        "in Celje earlier in this group phase. Celje are fourth at 0-0-4 with minus-34. Ten goals "
        "separated the sides in the reverse fixture, so a four-goal handicap in Aalborg is a "
        "conservative ask. Selection: Aalborg Håndbold -4.0."
    ),
    "hand-ehf-12046": (
        "Barça top Group E at 4-0-0 with a plus-33 differential and won 28:27 in Montpellier in the "
        "away fixture. Montpellier are third at 1-0-3. That one-goal reverse result is the reason "
        "the handicap is only three at the Palau Blaugrana, where the model adds home advantage. "
        "Selection: Barça -3.0."
    ),
    # ---------------- Aussie rules (AFLW) — re-priced 2026-10-22 from the official ladder (T35/T63) ----------------
    "aflw-r11-01": (
        "North Melbourne sit top of the AFLW ladder on 36 points, their only blemish in ten rounds "
        "a single loss, with a commanding 251.9 per cent. Adelaide are ninth at 20 points from a "
        "5-5-0 record and 102.4 per cent, and the match is staged at North Hobart Oval. Sixteen "
        "ladder points and four wins separate the clubs on the official table. "
        "Selection: North Melbourne -8.0."
    ),
    "aflw-r11-02": (
        "Geelong are second on the official ladder with 36 points from ten matches, nine wins and "
        "a 167.2 percentage. Fremantle hold eighth place on 20 points, a 5-5-0 record and 104.9 "
        "per cent. At GMHBA Stadium a four-win, sixteen-point table gap separates the clubs, which "
        "the model reads as a comfortable home win rather than a close one. "
        "Selection: Geelong Cats -7.0."
    ),
    "aflw-r11-04": (
        "Carlton are sixth on 28 points after ten rounds, seven wins and a 133.0 percentage; GWS "
        "are fifteenth on eight points from a 2-8-0 record at 68.2 per cent. The clubs meet at "
        "IKON Park with twenty ladder points and five wins between them, a gulf the official "
        "table makes plain going into round eleven. Selection: Carlton -10.0."
    ),
    "aflw-r11-05": (
        "Hawthorn sit tenth on 20 points with a 5-5-0 record and 101.5 per cent; Essendon are "
        "seventeenth on four points, one win from ten and 55.6 per cent. At the Kennedy Community "
        "Centre in Dingley, four wins and sixteen ladder points separate the two, so the home side "
        "is backed to cover a moderate margin. Selection: Hawthorn -7.0."
    ),
}
