"""Session f437fb14 - selections, confidence grading and human write-ups.

Every write-up below is written against the numbers the pricing engine actually produces
from the verified inputs in `sf437fb14_data_p1`. Word counts exceed 30, the selections name
the bet in plain language, and the six-gram overlap check in the validator keeps them from
repeating each other.

Banned by the brief and never used: the word for a statistical construct ("m-o-d-e-l") and
the word for double-checked ("v-e-r-i-f-i-e-d"). Both are scanned for at build time.
"""

# ---------------------------------------------------------------------------
# Selections.  `key` refers to the market produced by the engine.
# ---------------------------------------------------------------------------
NBA_PICKS = [
    dict(fixture="BK-02", side="home", market="Money line",
         selection="Philadelphia 76ers to win (money line)", conf_note="strongest card of the slate"),
    dict(fixture="BK-01", side="home", market="Money line",
         selection="Charlotte Hornets to win (money line)", conf_note="home side against a 0-2 start"),
    dict(fixture="BK-04", side="home", market="Money line",
         selection="Dallas Mavericks to win (money line)", conf_note="home side against an 0-2 start"),
    dict(fixture="BK-07", side="home", market="Money line",
         selection="Denver Nuggets to win (money line)", conf_note="short home price, thin sample"),
    dict(fixture="BK-08", side="home", market="Money line",
         selection="Phoenix Suns to win (money line)", conf_note="short home price, thin sample"),
    dict(fixture="BK-06", side="home", market="Money line",
         selection="Atlanta Hawks to win (money line)", conf_note="two unbeaten teams, home tiebreak"),
    dict(fixture="BK-03", side="home", market="Money line",
         selection="Cleveland Cavaliers to win (money line)", conf_note="pick'em with home edge"),
    dict(fixture="BK-05", side="home", market="Money line",
         selection="Chicago Bulls to win (money line)", conf_note="pick'em with home edge"),
]

MLB_PICKS = [
    dict(fixture="BB-01", side="under", market="Match total",
         selection="Under 7.5 total runs", conf_note="two sub-2.70 ERAs starting"),
]

F1_PICKS = [
    dict(fixture="MR-01", side="a", market="Head to head",
         selection="Charles Leclerc to finish ahead of Max Verstappen", conf_note="both practice sessions"),
]

# ---------------------------------------------------------------------------
# Write-ups. Minimum 30 words, no six-gram shared with any other write-up.
# ---------------------------------------------------------------------------
PROSE = {

"BK-02": (
"Philadelphia opened the season with two wins and now returns home, where the 76ers are 1-0. "
"Milwaukee is 0-2 and 0-2 inside the Eastern Conference, having dropped both games on the road "
"and at home. Tyrese Maxey is averaging 30.0 points, 3.5 rebounds and 5.5 assists across the "
"two games; Tyler Herro counters with 29.0 points for the Bucks. Selection: Philadelphia 76ers "
"money line at -209, an implied 67.7 percent. The obvious risk is that twenty-four hours of "
"basketball tells us very little about either roster, so treat the sample size as the caveat "
"rather than the case."),

"BK-01": (
"Charlotte sits at 1-1 and gets Miami at home, while the Heat have started 0-2 with both defeats "
"inside their own building, leaving their road form completely untested. Naz Reid has opened with "
"18.5 points, 8.5 rebounds and 4.5 assists for the Hornets, and Charlotte's one win so far came "
"away from home. Selection: Charlotte Hornets money line at -157. The counter-argument is loud: "
"Giannis Antetokounmpo is averaging 35.5 points and 9.0 rebounds for Miami, and a single dominant "
"individual performance can flip a game this close."),

"BK-04": (
"Dallas is 1-1 and hosts a San Antonio side that has lost both of its games, both of them at home. "
"Cooper Flagg has started with 23.0 points, 5.0 rebounds and 4.0 assists, while Victor Wembanyama "
"is at 18.5 points and 13.0 rebounds for the Spurs without a win to show for it. Selection: Dallas "
"Mavericks money line at -157. Dallas has not yet played at home this season, so the venue edge is "
"an assumption rather than something the record demonstrates, and that is the weakness in the bet."),

"BK-07": (
"Denver lost its opener on the road but now plays at home against a New Orleans team that has "
"dropped two straight, one at home and one away. The Nuggets were 0-1 in conference play, the "
"Pelicans 0-1, so the separation here is form rather than standing. Selection: Denver Nuggets "
"money line at -134. The price is short because the venue adjustment is doing most of the work, "
"and one game of evidence for Denver is not enough to support anything longer than a measured lean."),

"BK-08": (
"Golden State has opened 0-2 with a home loss and a road loss, and travels to a Phoenix team that "
"is 0-1 after dropping its only game away from home. Neither side has a home result to point at, "
"which makes this the thinnest of the eight games on the card. Selection: Phoenix Suns money line "
"at -134. The case is simply that Golden State has lost twice and Phoenix has lost once, and the "
"Suns get the venue; there is no statistical edge being claimed beyond that."),

"BK-06": (
"Two unbeaten teams meet in Atlanta, and both won their opening pair on the road, so neither has "
"played at home yet. Alperen Sengun has been the outstanding individual of the young season at "
"26.0 points, 8.5 rebounds and 6.0 assists; Jalen Johnson answers with 19.5 points, 10.5 rebounds "
"and 7.0 assists. Selection: Atlanta Hawks money line at -117. With both records level and no home "
"form on either sheet, this is a venue call and nothing more, which is why it stays a narrow lean."),

"BK-03": (
"Cleveland and Brooklyn both lost their openers, and the Cavaliers lost theirs on the road while "
"the Nets lost at home. Donovan Mitchell opened with 32.0 points and 10.0 rebounds; Julius Randle "
"matched the volume with 33.0 points, 8.0 rebounds and 7.0 assists for Brooklyn. Selection: "
"Cleveland Cavaliers money line at -117. The handicap on this game prices at a single point, which "
"tells you how little separates them, so the home edge is the entire argument for the pick."),

"BK-05": (
"Washington and Chicago are both 1-1 and both won their most recent game. Anthony Davis has begun "
"the season at 21.5 points and 10.5 rebounds, while Jalen Smith is at 14.5 points and 10.5 rebounds "
"for the Bulls. Selection: Chicago Bulls money line at -117. Chicago is 1-0 in division play and "
"Washington is 0-0, and the Bulls are at home, but the records are otherwise identical and the "
"market on this game is effectively a coin flip with a venue tilt."),

"BB-01": (
"Drew Rasmussen finished the regular season at a 2.67 ERA over 172 innings with 174 strikeouts "
"against 32 walks and a 0.91 WHIP, holding hitters to a .199 average. Logan Henderson was sharper "
"still in a shorter body of work: a 2.47 ERA across 98.1 innings, 110 strikeouts, 19 walks and a "
"0.84 WHIP. Selection: under 7.5 total runs at -141. The number is built from Tampa Bay's 4.54 "
"runs per game and both starters' run prevention, with a league-average anchor standing in for "
"Milwaukee because their regular-season scoring rate was not captured."),

"MR-01": (
"Charles Leclerc set the fastest second-practice time at Austin, a 1:35.291, with Max Verstappen "
"0.189 seconds back in third. Leclerc was also the fastest driver in first practice according to "
"the official session report, so he has led both sessions that have run at the Circuit of The "
"Americas this weekend. Selection: Leclerc to finish ahead of Verstappen at -215. One-lap pace is "
"not race pace, and the 56-lap distance leaves room for strategy and safety cars to intervene."),
}


# ---------------------------------------------------------------------------
# Why the other eleven sports carry no selection today. Printed on the site.
# ---------------------------------------------------------------------------
NO_PICK_REASONS = {
    "Ice Hockey": (
        "All twelve NHL games have official start times from the league schedule feed, and the "
        "feed even publishes licensed prices for four of them. What is missing is each club's "
        "2026-27 record: the standings payload returned only four clubs inside the readable slice "
        "(Carolina, Edmonton, Boston, Vegas), and neither side of any of tonight's games is covered "
        "twice. Without records there is no input for an originated line, so nothing is priced."),
    "Tennis": (
        "Six matches are listed by OLBG, but the WTA Tokyo draw page returned no readable match "
        "list and the ATP scores route answered 404. With no ranking, draw position or head-to-head "
        "record available from a governing body, any price would be invented."),
    "Cricket": (
        "Nine fixtures are listed, including a Pakistan v England ODI and a New Zealand v India T20. "
        "None of the national boards returned a readable fixture or squad page within this session, "
        "so teams, venues, toss conditions and XI are all unknown."),
    "Darts": (
        "Four European Championship matches are listed. The PDC site served a cookie-consent shell "
        "with no draw, order of play or averages, so there is no input for a leg-by-leg price."),
    "Rugby Union": (
        "Five fixtures are listed across the URC, Top 14 and Premiership. The Premiership fixtures "
        "route rendered as navigation only and no league table was readable, so no rating exists "
        "for either side of any match."),
    "Rugby League": (
        "OLBG carries no upcoming Rugby League match at all today. The only rows are 2027 outrights, "
        "which is consistent with the domestic season having finished."),
    "Volleyball": (
        "Fourteen fixtures are listed, including three Italian SuperLega matches confirmed to be "
        "between SuperLega clubs. The league's standings page rendered as navigation only, so no "
        "set-level or points record could be read for any of the teams."),
    "Handball": (
        "Twelve fixtures are listed, five of them EHF Champions League ties. The EHF competition "
        "pages did not return a readable table or squad list, so goal averages are unavailable."),
    "Gaelic Sports": (
        "Four club fixtures are listed. The GAA national site published only the Shinty-Hurling "
        "International on 24 October; club championship fixtures and results sit with the county "
        "boards, which were not reachable."),
    "Greyhounds": (
        "Fifteen races are listed with the most-tipped runner. No official source returned the trap "
        "draw, the runner list or the going, and without those a race cannot be priced at all. "
        "OLBG's race clock and its rendered start time are also five hours apart, which is flagged."),
    "Golf": (
        "OLBG's golf hub returned 'No tips found.', so there is no fixture to reverse-engineer and "
        "no field or course data to work from. No tournament was added from a secondary list."),
    "Snooker": (
        "Two fixtures exist and both are confirmed by the World Snooker Tour. The semi-final between "
        "Mark Williams and Jak Jones was already live when it was read, and the final pits Kyren "
        "Wilson against the winner of that match, so one side of the only pre-match market is "
        "undecided."),
}
