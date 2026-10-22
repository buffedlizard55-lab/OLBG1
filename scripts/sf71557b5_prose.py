#!/usr/bin/env python3
"""
sf71557b5_prose.py - hand-written previews for every High-confidence selection
originated by this desk (session f71557b5-olbg1, task T50).

Rules enforced by scripts/sf71557b5_validate.py:

* one entry per High pick, keyed by fixture id - a High pick with no entry fails the build;
* at least 30 words;
* names the team or player, states current form and recent match history, and makes the
  betting selection unmistakable;
* states the originated fair price;
* every factual clause is drawn from an official page read on 2026-10-22 and listed in
  that fixture's `evidence` block - nothing here is recalled or inferred;
* no six-word sequence may repeat inside one preview or anywhere across the corpus.
"""

PROSE = {
    "nhl-2026020157": (
        "New Jersey host Anaheim at the Prudential Center on Thursday evening with both clubs nine games "
        "into the season, and the official standings separate them clearly: the Devils stand 5-4-0 for ten "
        "points, the Ducks 4-5-0 for eight while carrying four straight defeats, the longest active slide "
        "anywhere on tonight's twelve-game slate. New Jersey on the moneyline at 1.42 is the selection."
    ),
    "el-r7-efes-bjk": (
        "Anadolu Efes and Besiktas contest the season's first Turkish derby with both backcourts rebuilt "
        "around injuries. Efes, 2-4, remain without Mike James, PJ Dozier, Isaia Cordinier and Georgios "
        "Papagiannis; Besiktas, 3-3, could hand Lonnie Walker a debut while DaQuan Jeffries recovers from "
        "wrist surgery. The visitors beat Bayern 95-87 last round and rank third in EuroLeague scoring at "
        "92.3 points nightly, against an Efes defence allowing 85.0. Besiktas plus 6.5 points at 1.41."
    ),
    "el-r7-bay-dub": (
        "Bayern Munich sit 2-4 in Round 7 and are still chasing a first EuroLeague home win after losing "
        "95-87 at Besiktas, where they wiped out a 28-point hole only to fall short anyway. Dubai Basketball "
        "arrive 4-2, victorious in Spain and Italy during the previous double round, fifth across the "
        "competition conceding 82.2 points per game, and powered by Dwayne Bacon's 17.8 average. Dubai "
        "receiving 2.5 points at 1.43 is the bet."
    ),
    "el-r7-mac-rmb": (
        "Maccabi Rapyd Tel Aviv are nominally home in Belgrade rather than Tel Aviv, which blunts the trend "
        "the official Round 7 preview leans on, namely that the home club has taken each of the last five "
        "meetings. Maccabi stand 2-4 after edging Valencia 91-88. Real Madrid are 3-3 with three consecutive "
        "victories but sit 1-4 away from Movistar Arena, that lone road success coming 98-89 at Milan. Real "
        "Madrid plus 3.5 points at 1.41."
    ),
    "el-r7-pan-bas": (
        "Panathinaikos are 5-1 and concede a competition-low 73.0 points per contest, their single blemish a "
        "first defeat under Zeljko Obradovic. Kosner Baskonia are 1-5, handed to Velimir Perasovic only last "
        "Thursday, and lost 86-78 at Virtus after flipping a 17-point deficit into a late lead. The Greens "
        "have won five successive home games against them, and Baskonia have not left Athens celebrating "
        "since March 2021. Panathinaikos minus 10.5 points at 1.41."
    ),
    "pdc-ec-r1-05": (
        "Niels Zonneveld travels to Dortmund as fourth seed and a maiden European Tour champion, having "
        "claimed the Dutch Darts Championship in Maastricht on 18 October. Cameron Menzies, seeded 29th, is "
        "the lone Scotsman among the 32 qualifiers, a field ordered strictly by one-year European Tour "
        "rankings. Our first-to-six-leg model rates Zonneveld 72.5 per cent straight up, a 1.38 fair price the "
        "window rejects, so the handicap is the compliant view: Menzies receiving 3.5 legs at 1.41."
    ),
    "pdc-ec-r1-07": (
        "Danny Noppert is seeded fifth at the Machineseeker European Championship and defeated Dave Chisnall "
        "6-4 in the Dutch Darts Championship second round on 17 October, a week after losing 3-6 to Damon "
        "Heta in Basel. Stephen Bunting, the 28th seed, exited that same Swiss event 4-6 against Jeffrey de "
        "Graaf. Noppert to win the match outright at 1.41."
    ),
    "top14-j7-tou-usap": (
        "Stade Toulousain lead the Top 14 on 24 points through six rounds, their lone setback a 30-27 "
        "opening-day loss at La Rochelle before beating Union Bordeaux-Begles 48-12, Castres 40-18 and "
        "Bayonne 45-34. USA Perpignan are ninth on 13, mauled 55-25 by Racing 92 before scraping past Vannes "
        "21-12. LNR's own published model rates Toulouse 84.44 per cent, far outside the window, so the "
        "handicap carries the bet: Toulouse minus 6.5 points at 1.43."
    ),
    "top14-j7-sr-ubb": (
        "One table point divides these two: Stade Rochelais fourth on 18, Union Bordeaux-Begles third on 19. "
        "LNR's published model favours the visitors narrowly, 52.60 per cent against 46.88. La Rochelle "
        "opened the season beating Toulouse 30-27 and recently won 28-16 at Lyon, but such a slender table "
        "gap hardly justifies conceding a big start at Marcel-Deflandre. Bordeaux-Begles plus 5.5 points "
        "at 1.42."
    ),
    "ehfcl-bar-mon": (
        "Barca host Montpellier HB at the Palau Blaugrana on Thursday, the EHF playing-times sheet confirming "
        "20:45 CEST for this group E fixture. These clubs already met inside this same group phase on "
        "8 October, in this same building, and Barca won 34-27. Seven goals separated them on that night. "
        "Barca minus 2.5 goals at 1.42 needs only three."
    ),
    "cri-sl-eng-odi3": (
        "Both teams have now used the same Rawalpindi surface within four days. Pakistan made 305 and beat "
        "Sri Lanka by 37 runs on 18 October, then Arafat Minhas claimed 6-40 plus a 59 as England were "
        "dismissed 87 runs short on 20 October. Harry Brook's England arrived holding three consecutive ODI "
        "series wins, while Kusal Mendis' Sri Lanka had already lost a series to England. Half of that "
        "50-run gap drives the model: England to win at 1.41."
    ),
    "aflw-r11-por-col": (
        "AFLW Round 11 begins in Adelaide on Friday with Port Adelaide, eleventh on 16 points at 78.8 per "
        "cent, hosting Collingwood, sixteenth on four points at 56.7. Both lost during Round 10, though by "
        "vastly different margins: Brisbane restricted Port to two goals from 39 entries, whereas Sydney "
        "thrashed Collingwood by 51 points at Windy Hill, 12.8 (80) against 4.5 (29). Back Port Adelaide to "
        "cover a 10.5-point line, priced 1.40."
    ),
    "aflw-r11-nor-ade": (
        "Reigning premiers North Melbourne head the AFLW ladder with 36 points and a percentage of 251.9, "
        "although the club's own finals preview admits they look marginally more vulnerable during 2026. "
        "Adelaide Crows sit ninth on 20 points at 102.4 per cent and required Chloe Bown's match-winning "
        "goal to survive Gold Coast in Round 10. They meet at North Hobart Oval, Sunday, 1.05pm AEDT. "
        "North Melbourne minus 35.5 points at 1.42."
    ),
    "aflw-r11-haw-ess": (
        "Hawthorn are tenth on 20 points at 101.5 per cent and still rue a one-point Round 10 loss to the "
        "Giants, sealed when Aine McDonagh missed late, having been tipped for one of the easier runs home. "
        "Essendon are seventeenth on four points at 55.6 per cent. The official finals-race preview frames "
        "this Round 11 meeting as the fixture keeping Hawthorn's September hopes breathing. Hawthorn minus "
        "21.5 points at 1.40."
    ),
    "gaa-wat-sfc-final": (
        "Rathgormack and The Nire contest the Waterford senior football final at Cappoquin Logistics Fraher "
        "Field on Sunday, 2:30pm, with Killian O'Sullivan refereeing. Rathgormack reached it via 1-14 to "
        "0-15 against Gaultier after a 5-15 to 2-5 demolition of Abbeyside-Ballinacourty, though that same "
        "Abbeyside side beat them 1-11 to 1-7 in round five. The Nire accounted for Abbeyside-Ballinacourty "
        "0-12 to 0-5 and Gaultier 2-10 to 0-13. Margins this thin are where a 3.5-point start for The Nire, "
        "at 1.43, earns its place."
    ),
}
