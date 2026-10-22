"""Session 7a5b5360-olbg1 — written predictions, findings and methodology text.

Every factual claim inside a prediction is traceable to a value stored in s7a5b5360_data.py, which
in turn carries the official URL it was read from. No injury, team-news, weather, head-to-head or
scoring-rate claim is made anywhere, because none of those was read on an official page today.
"""

PREDICTIONS = {
    # ---- the four High-confidence match-winner picks -------------------------------------------
    "nhl-2026020159::New York Islanders":
        "The Islanders are 5-3-1 and have banked 11 of a possible 18 points, while Los Angeles arrive "
        "at UBS Arena with one win in seven (1-4-2) and only four points from 14. Our originated "
        "moneyline makes New York a 72.1% shot at 1.39, so the selection is the Islanders to win the "
        "match outright, not the puck line.",

    "nhl-2026020162::Minnesota Wild":
        "Minnesota carry a 6-2-2 record and 14 points from 20 into the Scotiabank Saddledome, where "
        "Calgary sit 2-6-0 with four points from 16. That is the widest points-percentage gap on "
        "tonight's board, so the model makes the Wild 70.5% to win and we back Minnesota on the "
        "moneyline at 1.42.",

    "wst-m50::Kyren Wilson":
        "Kyren Wilson is the world No. 9 on GBP 716,800 and has conceded only two frames in reaching "
        "Round 3, beating Ben Mertens 4-0 and Thepchaiya Un-Nooh 4-2. Pang Junxu, ranked 29, needed a "
        "deciding frame to see off Liam Davies. Wilson to win the match at 1.41 is our pick.",

    "wst-m54::Mark Williams":
        "Mark Williams, world No. 8 with GBP 747,400 on the published ranking list, has won both his "
        "matches by the same 4-2 scoreline, against Robbie Williams and Zhang Anda. Martin O'Donnell "
        "is outside the top 36 but has already removed Judd Trump and Luca Brecel this week. We still "
        "make Williams a 73.7% favourite at 1.36.",

    # ---- High-probability handicap picks ------------------------------------------------------
    "nhl-2026020162::Minnesota Wild +1.5":
        "The safest route into the Scotiabank Saddledome game is Minnesota on the puck line. Their 6-2-2 "
        "start is worth 14 points against Calgary's four, and the goal-difference distribution puts the "
        "Wild within one goal or better in 82.6% of simulations. That makes plus 1.5 goals a 1.21 shot.",

    "nhl-2026020158::Florida Panthers +1.5":
        "Florida are 5-2-2 and have collected 12 of 18 points; Pittsburgh are 3-6-1 with seven from 20 "
        "and sit bottom of their division on the fetched record. Giving the Panthers a 1.5-goal start "
        "at PPG Paints Arena is the pick, modelled at 79.7% and priced at 1.26.",

    "nhl-2026020165::Detroit Red Wings +1.5":
        "Vancouver's 2-8-1 start is the worst record on the twelve-game slate, five points from a "
        "possible 22. Detroit are only 3-3-3 but have avoided regulation defeats more often than the "
        "Canucks, so giving the Red Wings a 1.5-goal cushion at 1.26 - a 79.2% model chance - is the "
        "play at Rogers Arena.",

    "nhl-2026020160::Vegas Golden Knights +1.5":
        "Vegas have opened 8-3-0 for 16 points from 22 and now visit a St. Louis side sitting on nine "
        "points from 18. Our margin model gives the Golden Knights a 77.9% chance of avoiding a defeat by "
        "two or more, which is why the 1.5-goal start is priced at 1.28 for the Enterprise Center game.",

    "nhl-2026020155::New York Rangers +1.5":
        "The Rangers are 7-3-1 for 15 points from 22, Toronto 5-4-2 for 12 from 22, and the model "
        "actually prefers New York on the road. Taking the Rangers on a 1.5-goal handicap at 1.32 "
        "covers a one-goal defeat in Toronto, which our goal-difference distribution puts at 75.6%.",

    "nhl-2026020164::Utah Mammoth +1.5":
        "Utah are 7-3-0 with 14 points from 20 and Seattle 6-3-1 with 13 from 20, so the two clubs are "
        "separated by a single point at Climate Pledge Arena. In a game this tight the plus 1.5 goal "
        "start matters: the Mammoth cover in 73.4% of our simulations, priced at 1.36.",

    "nhl-2026020161::Winnipeg Jets +1.5":
        "Winnipeg arrive at 4-3-2 with ten points and Dallas at 5-3-1 with 11, a gap small enough that the "
        "model refuses to separate them by a full goal. Taking the Jets with a 1.5-goal start, a 70.6% "
        "cover chance at 1.42, is the selection at American Airlines Center.",

    # ---- Featured Medium / Low picks ----------------------------------------------------------
    "wst-m52::Elliot Slessor":
        "Slessor is the world No. 23 on GBP 329,200 and has dropped a single frame in two matches, 4-0 "
        "against He Guoqiang then 4-1 against Joe O'Connor. Ricky Walden, outside the published top "
        "36, has beaten Neil Robertson 4-1 and Joe O'Connor 4-3. Slessor to win at 1.48 is the call.",

    "nhl-2026020154::Boston Bruins":
        "Boston are 7-2-1 for 15 points from 20 and Nashville 3-2-3 for eight from 16, and the Bruins "
        "have home ice at TD Garden. The model puts Boston at 69.1% on the moneyline, which is the "
        "highest win probability of any home side on the slate after the Islanders.",

    "wst-m55::Jak Jones":
        "Jak Jones is ranked 24 with GBP 319,300 and has lost two frames in the event, 4-1 over Tom "
        "Ford and 4-2 over John Higgins. Daniel Wells, outside the top 36, has beaten Barry Hawkins "
        "4-2 and Ryan Day 4-3. Back Jones in the match-winner market at 1.52, a 65.8% model chance.",

    "nhl-2026020163::Edmonton Oilers":
        "Edmonton are 7-1-1 and have 15 points from 18, the best points percentage on the board "
        "alongside Carolina's 17 from 22. The Oilers have home ice at Rogers Place, and the model "
        "gives them 60.1% against a Hurricanes side that has played two more games. Edmonton to win "
        "at 1.66.",

    "nhl-2026020157::New Jersey Devils":
        "New Jersey are 5-4-0 while Anaheim are 4-5-0, and the Devils have home ice at the Prudential "
        "Center. The model separates them by six percentage points and prices New Jersey at 1.64 on the "
        "moneyline, a 61.0% chance, which is a Medium-confidence pick rather than a High one.",

    "mlb-849805::Milwaukee Brewers":
        "Milwaukee finished the regular season 103-59 (.636) and Tampa Bay 98-64 (.605), and the "
        "Brewers have home field at American Family Field for this World Series game. The gap is real "
        "but small, so the model makes Milwaukee only 55.6% at 1.80; the run line is the better "
        "angle than the moneyline.",

    "f1-usgp-2026::Kimi Antonelli":
        "Antonelli leads the drivers' championship on 340 points after seventeen rounds, 102 clear of "
        "Mercedes team-mate George Russell on 238, with Hamilton on 229 and Verstappen on 221. Round "
        "18 is the United States Grand Prix at the Circuit of The Americas over 56 laps. He is our "
        "race-winner selection at 4.51, but 22.2% is a Low-confidence price.",
}

FLAGS = [
    {"id": "F-7A-01", "severity": "high", "status": "brief-level, not a data error",
     "title": "The brief's -250 floor and its 70% threshold cannot both be satisfied once a bookmaker margin exists",
     "detail": ("A selection with a 70% chance prices at 1.4286 fair, i.e. about -233. Add any margin and it "
                "quotes at roughly 1.37, about -270. So a pick that is genuinely 70%+ almost always prices "
                "shorter than the -250 floor the brief asks us to stay above. This desk publishes the "
                "probability, the fair decimal price and an in-band yes/no for every selection rather than "
                "silently dropping either rule. Of the 26 selections at 70% or better on this board, 16 price "
                "shorter than -250."),
     "evidence": ["data/7a5b5360/high_probability.json"], "sources": []},
    {"id": "F-7A-02", "severity": "low", "status": "upstream quirk",
     "title": "MLB returns World Series games out of chronological order",
     "detail": ("The schedule API lists gamePk 849805 (23 Oct), 849802 (24 Oct), 849804 (26 Oct) and 849803 "
                "(27 Oct). The gamePk sequence is therefore not chronological and the payload reports "
                "gameNumber 1 for all four games. No game number is asserted anywhere on this site; the "
                "dates and venues are quoted exactly as returned."),
     "evidence": ["data/7a5b5360/fixtures.json"], "sources": ["mlb_schedule"]},
    {"id": "F-7A-03", "severity": "medium", "status": "unverified value left blank",
     "title": "Leinster v Munster has no confirmed venue",
     "detail": ("The official URC Round 4 release prints the venue as \"TBC, Dublin\". Rather than naming the "
                "Aviva Stadium or the RDS, the row keeps the published text and the venue is flagged."),
     "evidence": ["data/7a5b5360/fixtures.json"], "sources": ["urc_fixtures"]},
    {"id": "F-7A-04", "severity": "medium", "status": "coverage gap",
     "title": "No URC league table could be read, so eight rugby matches are priced from a neutral baseline",
     "detail": ("unitedrugby.com/urc/table and unitedrugby.com/standings both returned HTTP 404. Without a "
                "table there is no sourced strength input for either side, so the model switches its "
                "strength term off, applies only a home term, and caps confidence at Low. No handicap or "
                "total is originated for these matches because a line would have to be invented."),
     "evidence": ["data/7a5b5360/coverage.json"], "sources": ["urc_table_a", "urc_table_b"]},
    {"id": "F-7A-05", "severity": "medium", "status": "left blank on purpose",
     "title": "Eight snooker rows have no start_utc",
     "detail": ("wst.tv prints \"08:00\", \"09:00\", \"14:00\" and \"15:00\" against \"Thu 22 Oct\" with no zone. "
                "A conversion would be arithmetic on a rendering, so start_utc is empty for all eight rows "
                "and the published clock is stored verbatim in start_published."),
     "evidence": ["data/7a5b5360/fixtures.json"], "sources": ["wst_matches"]},
    {"id": "F-7A-06", "severity": "low", "status": "partial source",
     "title": "The WST ranking table served only positions 1-36",
     "detail": ("Ten of the sixteen players in Round 3 fall outside the 36 rows the site served, so their "
                "world ranking and prize-money values are blank. They are described only as \"outside the "
                "published top 36\", which is what the page supports, and their strength input is built from "
                "frames won in this event instead."),
     "evidence": ["data/7a5b5360/fixtures.json"], "sources": ["wst_rankings"]},
    {"id": "F-7A-07", "severity": "high", "status": "blocked",
     "title": "Darts could not be harvested: pdc.tv serves a consent wall",
     "detail": ("https://www.pdc.tv/tournament-hub/10824 returned the CookieYes consent interstitial and "
                "eight further chunks of cookie policy, with no fixture content. No darts row is published."),
     "evidence": ["data/7a5b5360/coverage.json"], "sources": ["pdc_hub"]},
    {"id": "F-7A-08", "severity": "high", "status": "blocked",
     "title": "Handball, greyhounds and NBA endpoints failed outright",
     "detail": ("ehfcl.com/en/men/fixtures-and-results returned HTTP 404; gbgb.org.uk/racing/fixtures "
                "returned HTTP 500; cdn.nba.com's live scoreboard returned HTTP 500. None of the three "
                "sports has a published row on this desk."),
     "evidence": ["data/7a5b5360/coverage.json"],
     "sources": ["ehfcl_fixtures", "gbgb_fixtures", "nba_scoreboard"]},
    {"id": "F-7A-09", "severity": "high", "status": "client-rendered",
     "title": "Cricket, basketball and Aussie Rules boards render entirely in the browser",
     "detail": ("icc-cricket.com/fixtures-results returned nine repeated \"loading\" blocks and no fixture; "
                "euroleaguebasketball.net/en/euroleague/game-center returned a team list with an empty "
                "schedule; afl.com.au/aflw/fixture returned navigation chrome only. These sports are "
                "reported as unverified rather than guessed."),
     "evidence": ["data/7a5b5360/coverage.json"],
     "sources": ["icc_fixtures", "euroleague_gc", "aflw_fixture"]},
    {"id": "F-7A-10", "severity": "medium", "status": "coverage gap",
     "title": "Tennis cannot be placed on a date from an official draw sheet",
     "detail": ("The official ATP draw PDFs publish pairings, seeds and rankings but no per-match dates, and "
                "the tour calendar pages for this week are client-rendered. Assigning a date would be an "
                "inference, so no tennis fixture is published even though draws exist."),
     "evidence": ["data/7a5b5360/coverage.json"], "sources": []},
    {"id": "F-7A-11", "severity": "low", "status": "verified absence",
     "title": "The official GAA board publishes no senior gaelic football fixture for 22-26 October",
     "detail": ("gaa.ie/fixtures-results for October 2026 lists one match in the window, the Shinty-Hurling "
                "International between Ireland and Scotland at SuperValu Pairc Ui Chaoimh on 24 October, "
                "which is hurling and therefore out of scope. No gaelic football row is published."),
     "evidence": ["data/7a5b5360/coverage.json"], "sources": ["gaa_fixtures"]},
    {"id": "F-7A-12", "severity": "low", "status": "derived value disclosed",
     "title": "The United States Grand Prix start time is derived, not published in UTC",
     "detail": ("formula1.com prints session times in track-local time only. The 21:00Z race start comes from "
                "the two clocks the page displays side by side (my time UTC-4, track time UTC-5). The race "
                "is Sunday 25 October at 16:00 track time; qualifying is Saturday at 17:00."),
     "evidence": ["data/7a5b5360/fixtures.json"], "sources": ["f1_usgp"]},
    {"id": "F-7A-13", "severity": "medium", "status": "not priced",
     "title": "No starting pitcher is published for the World Series games in the fetched payload",
     "detail": ("The MLB schedule payload with the field filter used here carries no probablePitcher, so the "
                "pitching matchup is not modelled and the game-level prices rest on season records and home "
                "field alone. A reader should treat the baseball prices as the softest on the board."),
     "evidence": ["data/7a5b5360/fixtures.json"], "sources": ["mlb_schedule"]},
    {"id": "F-7A-14", "severity": "high", "status": "coverage gap",
     "title": "Twelve of the seventeen in-scope sports have no verified fixture on this desk",
     "detail": ("Five sports are covered (baseball, ice hockey, rugby union, snooker, motor racing) with 32 "
                "fixtures. The other twelve are listed on the coverage page with the exact URL that was "
                "tried and what came back. This desk is a fresh 22-26 October snapshot, not a replacement "
                "for the older desks already published in this repository."),
     "evidence": ["data/7a5b5360/coverage.json"], "sources": []},
]

REPO_REVIEW = [
    {"id": "R-01", "where": "README.md:56", "status": "inconsistent",
     "finding": ("The README states \"0 broken relative links across all 160 published HTML pages\", but "
                 "scripts/validate.py run on this branch counts 208 published HTML pages. The link claim is "
                 "true (0 errors, 0 warnings) but the page count is stale, most likely because later desks "
                 "added pages without regenerating that sentence."),
     "evidence": "python3 scripts/validate.py -> 'Validated relative links across 208 published HTML pages / Errors: 0 Warnings: 0'"},
    {"id": "R-02", "where": "README.md:51-53", "status": "verified",
     "finding": ("The headline counts (134 source-linked events, 126 two-sided H2H books, 31 High picks) "
                 "match what the validator prints for the root desk today: \"Primary data: 134 fixtures | 126 "
                 "H2H line books | 31 high-confidence predictions\"."),
     "evidence": "python3 scripts/validate.py -> 'Primary data: 134 fixtures | 126 H2H line books | 31 high-confidence predictions'"},
    {"id": "R-03", "where": "COORDINATION.md:7", "status": "inconsistent",
     "finding": ("The board header still reads \"Last updated: 2026-10-21T08:01:32Z\" even though sections "
                 "run to §30 and the task table runs to T40, i.e. later work was appended without the header "
                 "being touched. This session appended §31 and added T41 but did not rewrite the header, "
                 "because the file is shared and append-only by convention."),
     "evidence": "sed -n '7p' COORDINATION.md"},
    {"id": "R-04", "where": "data/, datasets/", "status": "structural",
     "finding": ("Eighteen tracked files describe matches, fixtures, lines or picks across five parallel "
                 "namespaces (root, c17a9192, 984d417f, ebfbd966, aa4e9dbf) with different counts: 134 root "
                 "rows, 217 in c17a9192, 145 in 984d417f. There is no single canonical dataset, so a reader "
                 "must know which desk a number came from. This desk adds a sixth namespace under "
                 "data/7a5b5360 and does not touch any of the others."),
     "evidence": "git ls-files | grep -E '^(data|datasets)/.*(matches|fixtures|lines|picks)' -> 18 files"},
    {"id": "R-05", "where": "COORDINATION.md (T35, T19, T10)", "status": "open",
     "finding": ("Three task rows are still open or in progress from earlier sessions (T35 AFLW re-price, "
                 "T19 live refresh, T10 multi-market origination). None of them is in this session's scope "
                 "and all three remain untouched, but the board is not in a fully done state."),
     "evidence": "COORDINATION.md section 1"},
    {"id": "R-06", "where": "whole tree", "status": "verified",
     "finding": ("Every tracked JSON file parses (0 invalid), no .pyc files are tracked, and .gitignore "
                 "covers __pycache__/ and *.pyc. The root dashboard validates clean before this session's "
                 "changes, which is the baseline this desk was added to."),
     "evidence": "json.load over data/**/*.json and datasets/*.json -> invalid json: [] ; git ls-files | grep -c '\\.pyc$' -> 0"},
]

METHOD_TEXT = [
    ("What this desk is",
     "A fresh snapshot of the 22-26 October 2026 fixture window, harvested from official sources on "
     "2026-10-22 between 00:00Z and 01:30Z. Thirty-two fixtures across five sports carry a sourced "
     "record, an originated board and a labelled pick. Twelve further in-scope sports are reported as "
     "unverified on the coverage page with the exact URL that was tried."),
    ("How a fixture gets in",
     "A row only exists if the participants, the start time and the venue were read on an official page "
     "during this session, and that page's URL is attached to the row. Where the official page does not "
     "publish a value - a confirmed venue, a UTC kick-off, a world ranking - the value is left empty and "
     "listed on the Flagged for Review page. Nothing is filled in from memory or from another site."),
    ("How a price is originated",
     "Each side is given a sourced strength input: season record for MLB, points percentage for the NHL, "
     "a blend of frames won in this event and world ranking for the snooker, championship points for the "
     "Formula One field. A logistic model turns the difference into a probability; the shrinkage "
     "coefficients, the home-field terms, the total baselines and the F1 exponent are printed in full in "
     "the assumption table on the Markets page and are modelling choices, never statistics."),
    ("What 'fair' and 'book' mean here",
     "The fair column is 1/probability - our own line with no margin. The book column is what a margin of "
     "4.5% (two-way), 6.0% (three-way) or 7.5% (F1 field) would make that price. Neither column is a quote "
     "from a bookmaker; both are produced by this model."),
    ("How confidence is graded",
     "High means the model gives the selection at least a 70% chance, Medium 55-69.9%, Low below 55%. The "
     "grade describes the model's probability, not the size of the price and not the size of the stake. "
     "Rugby union is capped at Low for the reason in F-7A-04."),
    ("What is deliberately not modelled",
     "Injuries, team news, weather, rest days, travel, head-to-head history and starting pitchers are all "
     "absent because none of them was read on an official page today. The prices on the baseball games "
     "are the softest on this desk for exactly that reason (F-7A-13)."),
]
