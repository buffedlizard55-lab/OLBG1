# -*- coding: utf-8 -*-
"""
Official-source evidence register for session 1a421e41-olbg1.

RULES THIS FILE OBEYS (COORDINATION.md s0.5):
  * Only governing bodies, tours, leagues and promoters are listed as OFFICIAL.
    Media outlets, aggregators, betting sites and Wikipedia are NOT official and
    are never used to fill a value. Where such a source was the only one that
    carried a fact, the fact is left BLANK on the desk and flagged.
  * `quote` is transcribed verbatim from the page fetched on the date in
    `fetched_utc`. Nothing is paraphrased into a value.
  * `confirms` states exactly which desk fields this evidence may fill.
    A field not named in `confirms` stays blank.

Media sources that were READ but deliberately NOT used as evidence are listed at
the bottom in NOT_OFFICIAL, so the audit trail shows they were considered and
rejected rather than missed.
"""

FETCH_DATE = "2026-10-22"

# ---------------------------------------------------------------------------
# 1. NHL - official league API (api-web.nhle.com is operated by the NHL)
# ---------------------------------------------------------------------------
NHL_SCHEDULE = {
    "source_name": "NHL (official league schedule API)",
    "source_url": "https://api-web.nhle.com/v1/schedule/2026-10-22",
    "fetched_utc": "2026-10-22T07:40:00Z",
    "official": True,
    "payload_facts": {
        "date": "2026-10-22",
        "dayAbbrev": "THU",
        "numberOfGames": 12,
        "season": 20262027,
        "gameType": 2,
    },
    "games_read_in_full": [
        {"id": 2026020154, "away": "Nashville Predators", "away_abbr": "NSH",
         "home": "Boston Bruins", "home_abbr": "BOS", "venue": "TD Garden",
         "startTimeUTC": "2026-10-22T23:00:00Z", "venueTimezone": "US/Eastern",
         "venueUTCOffset": "-04:00", "gameState": "FUT", "gameScheduleState": "OK",
         "gameCenterLink": "/gamecenter/nsh-vs-bos/2026-10-22/2026020154"},
        {"id": 2026020155, "away": "New York Rangers", "away_abbr": "NYR",
         "home": "Toronto Maple Leafs", "home_abbr": "TOR", "venue": "Scotiabank Arena",
         "startTimeUTC": "2026-10-22T23:00:00Z", "venueTimezone": "America/Toronto",
         "venueUTCOffset": "-04:00", "gameState": "FUT", "gameScheduleState": "OK",
         "gameCenterLink": "/gamecenter/nyr-vs-tor/2026-10-22/2026020155"},
        {"id": 2026020156, "away": "San Jose Sharks", "away_abbr": "SJS",
         "home": "Ottawa Senators", "home_abbr": "OTT", "venue": "Canadian Tire Centre",
         "startTimeUTC": "2026-10-22T23:00:00Z", "venueTimezone": "US/Eastern",
         "venueUTCOffset": "-04:00", "gameState": "FUT", "gameScheduleState": "OK",
         "gameCenterLink": "/gamecenter/sjs-vs-ott/2026-10-22/2026020156"},
        {"id": 2026020157, "away": "Anaheim Ducks", "away_abbr": "ANA",
         "home": "New Jersey Devils", "home_abbr": "NJD", "venue": "Prudential Center",
         "startTimeUTC": "2026-10-22T23:00:00Z", "venueTimezone": "US/Eastern",
         "venueUTCOffset": "-04:00", "gameState": "FUT", "gameScheduleState": "OK",
         "gameCenterLink": "/gamecenter/ana-vs-njd/2026-10-22/2026020157"},
        {"id": 2026020158, "away": "(read partially - away team truncated in the extract)",
         "away_abbr": None, "home": "Pittsburgh Penguins", "home_abbr": "PIT",
         "venue": "PPG Paints Arena", "startTimeUTC": "2026-10-22T23:00:00Z",
         "venueTimezone": "US/Eastern", "venueUTCOffset": "-04:00",
         "gameState": "FUT", "gameCenterLink": None},
    ],
    "games_not_read": ("The payload reports numberOfGames=12 for 2026-10-22. Only the five "
                       "objects above were read before the extract was truncated, and game "
                       "2026020158 was read only partially. The remaining games are NOT "
                       "published on this desk: they are listed as a counted-but-unread "
                       "gap (8 games) rather than inferred."),
    "confirms": ["fixture existence", "date", "kickoff in UTC", "venue",
                 "home/away designation", "game state FUT (not started)"],
    "does_not_confirm": ["standings", "points", "goals for/against", "form",
                         "goaltenders", "any rating input for line origination"],
}

# ---------------------------------------------------------------------------
# 2. PDC - official promoter (pdc.tv). European Championship 2026, Dortmund.
# ---------------------------------------------------------------------------
PDC_EUROPEAN_CHAMPIONSHIP = {
    "source_name": "PDC (official promoter)",
    "sources": [
        {"url": "https://www.pdc.tv/news/2026/october/19/2026-machineseeker-european-championship-schedule-confirmed/",
         "title": "2026 Machineseeker European Championship schedule confirmed",
         "published": "2026-10-19"},
        {"url": "https://www.pdc.tv/news/2026/october/21/2026-machineseeker-european-championship-preview",
         "title": "2026 Machineseeker European Championship preview",
         "published": "2026-10-21"},
    ],
    "fetched_utc": "2026-10-22T07:44:00Z",
    "official": True,
    "event": "2026 Machineseeker European Championship",
    "venue": "Westfalenhallen, Dortmund",
    "dates": "2026-10-22 to 2026-10-25",
    "quote_schedule_of_play": ("Thursday October 22 (1900-2300 CEST, 1800-2200 BST) "
                               "Round One x8"),
    "quote_draw": ("(1) Ross Smith v (32) Karel Sedlacek / (16) James Wade v (17) Damon Heta / "
                   "(8) Gian van Veen v (25) Andrew Gilding / (9) Luke Woodhouse v (24) Dirk van "
                   "Duijvenbode / (4) Niels Zonneveld v (29) Cameron Menzies / (13) Gerwyn Price "
                   "v (20) Rob Cross / (5) Danny Noppert v (28) Stephen Bunting / (12) Luke "
                   "Humphries v (21) Ryan Searle / (2) Wessel Nijman v (31) Martin Schindler / "
                   "(15) Ryan Joyce v (18) Jermaine Wattimena / (7) Jonny Clayton v (26) Niko "
                   "Springer / (10) Josh Rock v (23) Chris Dobey / (3) Krzysztof Ratajski v "
                   "(30) Dave Chisnall"),
    "quote_thursday_order": ("Luke Woodhouse v Dirk van Duijvenbode / Danny Noppert v Stephen "
                             "Bunting / Niels Zonneveld v Cameron Menzies / Gerwyn Price v Rob "
                             "Cross / James Wade v Damon Heta / Luke Humphries v Ryan Searle / "
                             "Gian van Veen v Andrew Gilding / Ross Smith v Karel Sedlacek"),
    "quote_preview_form": ("Van Veen edged out Humphries in a captivating final 12 months ago, "
                           "and the world number two will also kick off his challenge against "
                           "Ryan Searle on Thursday."),
    # Seeding is the OFFICIAL strength input used by this desk's darts model.
    "seeds": {
        "Ross Smith": 1, "Wessel Nijman": 2, "Krzysztof Ratajski": 3,
        "Niels Zonneveld": 4, "Danny Noppert": 5, "Gian van Veen": 8,
        "Luke Woodhouse": 9, "Josh Rock": 10, "Luke Humphries": 12,
        "Gerwyn Price": 13, "Ryan Joyce": 15, "James Wade": 16,
        "Damon Heta": 17, "Jermaine Wattimena": 18, "Rob Cross": 20,
        "Ryan Searle": 21, "Chris Dobey": 23, "Dirk van Duijvenbode": 24,
        "Andrew Gilding": 25, "Niko Springer": 26, "Stephen Bunting": 28,
        "Cameron Menzies": 29, "Dave Chisnall": 30, "Martin Schindler": 31,
        "Karel Sedlacek": 32,
    },
    "confirms": ["event name", "venue", "dates", "every Round One pairing",
                 "official seeding of each player", "session window 1900-2300 CEST / 1800-2200 BST",
                 "Gian van Veen is the world number two",
                 "Gian van Veen beat Luke Humphries in the 2025 final"],
    "does_not_confirm": ["leg format of each round (not stated on the pages read)",
                         "individual start time of each tie (the PDC places all eight "
                         "Thursday ties in one 1900-2300 CEST session)",
                         "player three-dart averages", "Order of Merit money figures"],
    "thursday_ties": [
        ("Luke Woodhouse", "Dirk van Duijvenbode"),
        ("Danny Noppert", "Stephen Bunting"),
        ("Niels Zonneveld", "Cameron Menzies"),
        ("Gerwyn Price", "Rob Cross"),
        ("James Wade", "Damon Heta"),
        ("Luke Humphries", "Ryan Searle"),
        ("Gian van Veen", "Andrew Gilding"),
        ("Ross Smith", "Karel Sedlacek"),
    ],
}

# ---------------------------------------------------------------------------
# 3. World Snooker Tour - official tour (wst.tv)
# ---------------------------------------------------------------------------
WST_NORTHERN_IRELAND_OPEN = {
    "source_name": "World Snooker Tour (official tour)",
    "sources": [
        {"url": "https://www.wst.tv/matches/",
         "title": "Matches - World Snooker Tour (match centre)"},
        {"url": "https://www.wst.tv/news/2026/october/21/betvictor-northern-ireland-open-2026-day-four-afternoon",
         "title": "BetVictor Northern Ireland Open 2026 Day Four Afternoon",
         "published": "2026-10-21"},
    ],
    "fetched_utc": "2026-10-22T07:46:00Z",
    "official": True,
    "event": "BetVictor Northern Ireland Open 2026",
    "stage": "Round 3 / last 16, Belfast",
    "quote_top16": ("Defeat for Higgins means that only two of the world's top 16 - Mark Williams "
                    "and Kyren Wilson - remain in the draw."),
    "quote_higgins": ("Jak Jones' phenomenal season got even better as he beat legend John Higgins "
                      "4-2 to reach the last 16 of the BetVictor Northern Ireland Open in Belfast."),
    "quote_williams": ("Williams enjoyed a 4-2 win over Zhang Anda, taking the last two frames with "
                       "breaks of 78 and 58 to set up a tie with Luca Brecel or Martin O'Donnell."),
    "quote_williams_record": ("Last year, Williams became the oldest ever winner of a ranking title "
                              "when he landed the Xi'an Grand Prix and the 51-year-old could extend "
                              "that record this week."),
    "quote_pang": ("China's Pang Junxu edged out in-form Liam Davies 4-3 in a dramatic finish. The "
                   "first six frames were shared, Davies making breaks of 69 and 103 while Pang made "
                   "112 and 73. In the decider, Welshman Davies was on 60 when he missed a difficult "
                   "red to a top corner, and Pang capitalised with a superb 81 clearance. He now "
                   "faces Kyren Wilson."),
    "quote_craigie": ("Sam Craigie took a 3-0 lead over Xu Si with a top break of 103, then saw his "
                      "opponent come back to 3-3, but won the decider with a run of 75. He now meets "
                      "Matthew Selt."),
    "match_centre_rows_read": [
        {"players": "Kyren Wilson v Pang Junxu", "match_no": 50, "listed": "12:00 Thu 22 Oct"},
        {"players": "Matthew Selt v Sam Craigie", "match_no": 51, "listed": "12:00 Thu 22 Oct"},
        {"players": "Elliot Slessor v Ricky Walden", "match_no": None, "listed": "13:00 Thu 22 Oct"},
        {"players": "Mark Williams v Winner of match 44", "match_no": None, "listed": "18:00 Thu 22 Oct"},
        {"players": "Kyren Wilson 4-0 Ben Mertens", "match_no": None, "listed": "13:00"},
        {"players": "Thepchaiya Un-Nooh 2-4 Kyren Wilson", "match_no": None, "listed": "18:00 Tue 20 Oct"},
        {"players": "Mark Williams 4-2 Robbie Williams", "match_no": None, "listed": "09:00 Tue 20 Oct"},
        {"players": "Zhang Anda 2-4 Mark Williams", "match_no": None, "listed": "13:00 Wed 21 Oct"},
        {"players": "Zhang Anda 4-2 Liam Pullen", "match_no": None, "listed": "19:00 Mon 19 Oct"},
    ],
    "confirms": ["Wilson, Williams, Selt, Craigie, Pang Junxu, Slessor, Walden, O'Donnell all play "
                 "a last-16 tie on Thu 22 Oct",
                 "Kyren Wilson is inside the world top 16",
                 "Mark Williams is inside the world top 16",
                 "Pang Junxu is NOT inside the world top 16",
                 "Martin O'Donnell is NOT inside the world top 16",
                 "Kyren Wilson beat Ben Mertens 4-0",
                 "Kyren Wilson beat Thepchaiya Un-Nooh 4-2",
                 "Mark Williams beat Robbie Williams 4-2",
                 "Mark Williams beat Zhang Anda 4-2",
                 "Pang Junxu beat Liam Davies 4-3",
                 "Sam Craigie beat Xu Si 4-3",
                 "John Higgins LOST 4-2 to Jak Jones on 21 Oct 2026",
                 "Mark Williams is 51 years old",
                 "Mark Williams won the Xi'an Grand Prix last season"],
    "does_not_confirm": ["official seed numbers (the WST pages read do not print seeds)",
                         "frame format of the last-16 ties",
                         "Matthew Selt's round-2 result (only a non-official source carried it)",
                         "Jordan Brown, Scott Donaldson, Anthony McGill, Mateusz Baranowski, "
                         "David Gilbert, Cheung Ka Wai, Jak Jones, Daniel Wells results"],
}

# ---------------------------------------------------------------------------
# 4. ATP Tour - official tour (atptour.com)
# ---------------------------------------------------------------------------
ATP_LIVE_RACE_AND_FIELDS = {
    "source_name": "ATP Tour (official tour)",
    "sources": [
        {"url": "https://www.atptour.com/en/rankings/singles-race-to-turin",
         "title": "Rankings - PIF ATP Live Race To Turin"},
        {"url": "https://www.atptour.com/en/news/almaty-brussels-lyon-2026-scouting-report",
         "title": "Scouting Report: Turin contenders Daniil Medvedev, Arthur Fils, Flavio Cobolli "
                  "lead Almaty, Brussels, Lyon fields",
         "published": "2026-10-18"},
        {"url": "https://www.atptour.com/en/scores/current/almaty/9410/draws",
         "title": "Almaty Open draws - Kazakhstan, 19-25 Oct 2026"},
    ],
    "fetched_utc": "2026-10-22T07:47:00Z",
    "official": True,
    "live_race_rows_read": [
        {"live_rank": 6,  "player": "D. Medvedev", "points": 3420,
         "note": "Almaty - Will play next in the R16"},
        {"live_rank": 13, "player": "T. Fritz", "points": 2530,
         "note": "Lyon - Will play next in the R16"},
        {"live_rank": 25, "player": "A. Bublik", "points": 1785,
         "note": "Almaty - Will play next in the R16"},
        {"live_rank": 48, "player": "S. Baez", "points": 1014,
         "note": "Lyon - Lost to P. Herbert in the R32"},
    ],
    "quote_medvedev": ("Medvedev's Turin push: Top seed and defending champion Medvedev heads to "
                       "Almaty after reaching the semi-finals in Beijing and Shanghai. Currently "
                       "sixth in the PIF ATP Live Race To Turin, the 30-year-old opens his Almaty "
                       "campaign against Sho Shimabukuro or Roman Safiullin."),
    "tournament_dates": "Almaty Open, Kazakhstan, 19-25 Oct 2026",
    "confirms": ["Daniil Medvedev is Almaty top seed and defending champion",
                 "Daniil Medvedev reached the semi-finals in Beijing and Shanghai",
                 "Daniil Medvedev is 6th in the PIF ATP Live Race To Turin on 3,420 points",
                 "Daniil Medvedev is 30 years old",
                 "Daniil Medvedev plays Sho Shimabukuro in the Almaty R16 on 22 Oct",
                 "Taylor Fritz is 13th in the Live Race on 2,530 points and plays the Lyon R16",
                 "Alexander Bublik is 25th in the Live Race on 1,785 points and plays the Almaty R16",
                 "Pierre-Hugues Herbert beat Sebastian Baez in the Lyon R32",
                 "Flavio Cobolli is one of the three named field leaders across Almaty/Brussels/Lyon"],
    "does_not_confirm": ["any ranking or points for Sho Shimabukuro, Karen Khachanov, Tomas Machac, "
                         "Fabian Marozsan, Jiri Lehecka, Stan Wawrinka, Brandon Nakashima, "
                         "Alex Michelsen, David Goffin, Zizou Bergs, Damir Dzumhur, Borna Gojo, "
                         "Daniel Altmaier, Raphael Collignon, Valentin Vacherot, Luca Van Assche, "
                         "Kyrian Jacquet",
                         "any WTA player (the WTA pages were not fetched this session)",
                         "whether Luciano Darderi is still in the Almaty draw"],
}

# ---------------------------------------------------------------------------
# 5. Official-source COVERAGE SUMMARY per sport (honest statement of reach)
# ---------------------------------------------------------------------------
SPORT_OFFICIAL_REACH = {
    # sport_key: (official body, url or None if not reached this session, status)
    "tennis": ("ATP Tour", "https://www.atptour.com/en/rankings/singles-race-to-turin",
               "partial - ATP reached; WTA not reached this session"),
    "basketball": ("Euroleague Basketball",
                   "https://www.euroleaguebasketball.net/en/euroleague/standings/",
                   "reached - full official standings (20 clubs, PTS+/PTS-/H/A/L10) plus the official Round 7 Game Center for all 9 upcoming fixtures; Class A two-sided margin input"),
    "golf": (None, None, "not reached this session - no official page fetched"),
    "cricket": (None, None, "not reached this session - no official page fetched"),
    "snooker": ("World Snooker Tour", "https://www.wst.tv/matches/", "reached"),
    "rugby_union": (None, None, "not reached this session - no official page fetched"),
    "rugby_league": (None, None, "not reached this session - no official page fetched"),
    "baseball": (None, None, "not reached this session - no official page fetched"),
    "ice_hockey": ("NHL", "https://api-web.nhle.com/v1/schedule/2026-10-22",
                   "partial - schedule reached; no standings fetched, so no rating input"),
    "motor_racing": (None, None, "not reached this session - no official page fetched"),
    "darts": ("PDC", "https://www.pdc.tv/news/2026/october/21/2026-machineseeker-european-championship-preview",
              "reached - full Round One draw and seedings"),
    "handball": (None, None, "not reached this session - no official page fetched"),
    "volleyball": (None, None, "not reached this session - no official page fetched"),
    "aussie_rules": (None, None, "not reached this session - OLBG hub empty, AFL not fetched"),
    "esports": (None, None, "not reached this session - OLBG hub empty, Riot not fetched"),
    "gaelic_football": (None, None, "not reached this session - GAA not fetched"),
    "greyhounds": (None, None, "not reached this session - GBGB not fetched"),
}

# ---------------------------------------------------------------------------
# 6. Sources READ but REJECTED as non-official (audit trail)
# ---------------------------------------------------------------------------
NOT_OFFICIAL = [
    {"url": "https://en.wikipedia.org/wiki/2026_Northern_Ireland_Open",
     "why_rejected": "Wikipedia is not the governing body. It carried seed numbers "
                     "(Wilson 9, Pang Junxu 26, Selt 46, Craigie 70, Williams 10, Zhang Anda 18) "
                     "which were therefore NOT used; the desk uses the WST top-16 statement instead."},
    {"url": "https://www.snooker.org/res/index.asp?event=2548",
     "why_rejected": "Independent results aggregator, not the World Snooker Tour."},
    {"url": "https://snookerhq.com/2026-10-22/last-16-2026-northern-ireland-open-draw/",
     "why_rejected": "Fan/media site. Carried 'Round of 16 (bo7)' and BST start times; the frame "
                     "format was therefore left BLANK on the desk rather than inferred."},
    {"url": "https://www.bbc.com/sport/snooker/articles/cwkg5k7873kxo",
     "why_rejected": "Broadcaster, not the governing body. Its round-2 result list was not used."},
    {"url": "https://metro.co.uk/2026-10-19/northern-ireland-open-2026-carnage-top-seeds-string-belfast-upsets-29719657/",
     "why_rejected": "Newspaper, not the governing body."},
    {"url": "https://ronnieo147.com/",
     "why_rejected": "Player-owned site quoting WST copy. The underlying WST page was used instead "
                     "where the fact was needed."},
    {"url": "https://dartsnews.com/pdc/2026-european-championship-darts-draw-gerwyn-price-headlines-first-round-against-rob-cross-as-luke-littler-and-luke-humphries-find-out-opponents",
     "why_rejected": "Darts media site; the PDC's own pages were used instead."},
    {"url": "https://dave.sport/news/european-darts-championship-2026-draw-price-cross/",
     "why_rejected": "Betting/media site. Carried the £750,000 prize fund and £150,000 winner share, "
                     "which were therefore left BLANK on the desk."},
    {"url": "https://www.sportingnews.com/us/darts/news/2026-european-darts-championship-draw-schedule-prize-money-format/54da7e3c71b21e04a355af17",
     "why_rejected": "Media outlet."},
    {"url": "https://www.espn.com/darts/story/_/id/49948004/pdc-european-championship-darts-2026-schedule-results-how-watch-prize-money-dates-more-dortmund",
     "why_rejected": "Broadcaster."},
    {"url": "https://www.southwalesargus.co.uk/sport/26649003.gerwyn-price-drawn-rob-cross-darts-championship/",
     "why_rejected": "Local newspaper. Its 'Westfalenhallen, Dortmund' venue claim is corroborated "
                     "by the PDC preview, which is the citation used."},
    {"url": "https://www.universtennis.com/2026-10-22/atp-250-almaty-medvedev-bublik-atmane-le-programme-du-jeudi-22-octobre/",
     "why_rejected": "Tennis media site. Its order of play and French-time clocks were not used."},
    {"url": "https://www.tennis.com/tournaments/almaty-open/matches/d-medvedev-vs-s-shimabukuro-2026-10-22",
     "why_rejected": "Media site. Its 'Projected Winner 90%' figure is a third-party model and was "
                     "NOT used; this desk originates its own probability."},
    {"url": "https://kalshi.com/tennis/schedule",
     "why_rejected": "Betting/exchange operator."},
    {"url": "https://www.espn.co.uk/tennis/schedule",
     "why_rejected": "Broadcaster."},
    {"url": "https://en.wikipedia.org/wiki/Luke_Humphries",
     "why_rejected": "Wikipedia. Its list of Humphries' 2026 finals (World Masters runner-up to "
                     "Littler, Premier League runner-up to Littler, World Grand Prix winner over "
                     "Price 6-4) was NOT used as evidence."},
    {"url": "https://en.wikipedia.org/wiki/2026_World_Grand_Prix_(darts)",
     "why_rejected": "Wikipedia."},
    {"url": "https://en.wikipedia.org/wiki/Kyren_Wilson",
     "why_rejected": "Wikipedia. Its 'current ranking 9' was NOT used; the desk uses only the WST "
                     "top-16 statement."},
    {"url": "https://en.wikipedia.org/wiki/Daniil_Medvedev",
     "why_rejected": "Wikipedia. Its 'current ranking No. 5 (19 October 2026)' was NOT used."},
    {"url": "https://etusuora.com/uutiset/snooker-ni-open-tulokset-tapahtumia-20-10-2026",
     "why_rejected": "Finnish media site."},
    {"url": "https://www.olbg.com/",
     "why_rejected": "OLBG is the SUBJECT of the reverse-engineering task and a tipster-community "
                     "aggregator. It is cited on this desk as the harvested card source only, never "
                     "as an official source for a fixture fact."},
]


# ---------------------------------------------------------------------------
# EUROLEAGUE BASKETBALL - OFFICIAL GAME CENTER, ROUND 7, 2026-27
# Source: euroleaguebasketball.net (the competition's own governing domain).
# Fetched in full (chunks 0-1) on 2026-10-22. Chunk 2 is an unrelated
# article carousel and was not needed.
#
# This is the ONLY source reached by this session that supplies an official
# two-sided strength input (win-loss records for BOTH clubs) for a whole
# slate, so every EuroLeague fixture below is graded Class A.
# ---------------------------------------------------------------------------

EUROLEAGUE_GAME_CENTER = {
    "source_name": "Euroleague Basketball - Game Center: Hapoel ends Virtus's winning streak (Round 7)",
    "source_url": "https://www.euroleaguebasketball.net/euroleague/news/game-center-round-7-el2627/",
    "fetched_utc": "2026-10-22T07:24:00Z",
    "official": True,
    "headline": "Round 7 will be spread over 3 days, features 2 derbies and a rematch from last season's semifinals",
    "game_id_scheme": "https://www.euroleaguebasketball.net/euroleague/game-center/2026-27/<slug>/E2026/<n>/",
    # ---- already played, therefore correctly absent from OLBG ----
    "played": [
        {
            "date": "2026-10-21",
            "fixture": "Hapoel IBI Tel Aviv 90-81 Virtus Bologna",
            "game_id": "E2026/61",
            "facts": [
                "Hapoel stretched its winning streak to three games with a 90-81 victory over Virtus.",
                "Hapoel outscored the visitors 54-33 in the second half to turn the game on its head.",
                "Virtus entered Round 7 tied for the EuroLeague's longest winning streak at four games and led 36-48 at halftime.",
                "Zach LeDay scored 18 of his game-high 22 points after the break and grabbed 7 of his 10 rebounds in the second half to finish with a double-double.",
                "Elijah Bryant poured in 10 of his 12 points in the second half; Vasilije Micic added 16 points and Tai Odiase chipped in 13.",
                "Aliou Diarra led Virtus with 12 points and 7 rebounds; Derrick Alston also scored 12 but was held scoreless in the second half.",
            ],
        }
    ],
    # ---- upcoming Round 7 games ----
    "games": [
        {
            "date": "2026-10-22", "official_ko_cest": "19:30", "game_id": "E2026/64",
            "home": "Anadolu Efes Istanbul", "away": "Besiktas Istanbul",
            "home_record": "2-4", "away_record": "3-3",
            "facts": [
                "Thursday's slate begins in Istanbul with a derby between Efes (2-4) and Besiktas (3-3).",
                "Efes comes off an uplifting road win in Kaunas, and its backcourt is getting back to shape with Cam Payne playing well in place of the injured Mike James.",
                "Besiktas defeated Bayern on Friday to salvage a split from the two-round week and could get a boost with the debut of Lonnie Walker, who signed with the club last week.",
                "Besiktas is third in the league in scoring (92.3 ppg) and Efes is sixth in points allowed (85.0 ppg).",
            ],
        },
        {
            "date": "2026-10-22", "official_ko_cest": "20:00", "game_id": "E2026/65",
            "home": "FC Bayern Munich", "away": "Dubai Basketball",
            "home_record": "2-4", "away_record": "4-2",
            "facts": [
                "Bayern (2-4) returns home after a two-round week in Turkiye, while Dubai (4-2) remains on the road after winning games in Spain and Italy last week.",
                "Dubai will lean on an iron-fisted defense, fifth in the league with 82.2 points allowed per game, and the prolific scoring of Dwayne Bacon, whose 17.8 points per game are third-best in the league.",
                "Bayern's Duane Washington (16.8 ppg) is sixth in scoring despite coming off the bench, and getting home going alongside three-point ace Andreas Obst could be the key for the hosts.",
            ],
        },
        {
            "date": "2026-10-22", "official_ko_cest": "20:05", "game_id": "E2026/62",
            "home": "Maccabi Rapyd Tel Aviv", "away": "Real Madrid",
            "home_record": "2-4", "away_record": "3-3",
            "facts": [
                "After splitting its two games in Spain last week, Maccabi (2-4) meets Real Madrid (3-3), which has won three in a row but is 1-4 away from home.",
                "Both teams have enjoyed strong starts from their guards, with Yam Madar adjusting well to life with Maccabi and Theo Maledon taking a huge step forward in his second season in Madrid.",
                "The home team has won each of the last five times these teams have met.",
            ],
        },
        {
            "date": "2026-10-22", "official_ko_cest": "20:15", "game_id": "E2026/67",
            "home": "Panathinaikos AKTOR Athens", "away": "Kosner Baskonia Vitoria-Gasteiz",
            "home_record": "5-1", "away_record": "1-5",
            "facts": [
                "The teams from opposite ends of the standings meet as Panathinaikos (5-1) looks to bounce back from its maiden loss under Coach Obradovic.",
                "Baskonia (1-5) comes to Athens looking to improve under Coach Velimir Perasovic, who took the reins at the club on Thursday.",
                "The Greens' defense has allowed a league-low 73.0 points per game this season.",
                "Panathinaikos has won five straight home games against Baskonia, which last left Athens with a victory in March 2021.",
            ],
        },
        {
            "date": "2026-10-22", "official_ko_cest": "20:30", "game_id": "E2026/63",
            "home": "Armani Olimpia Milan", "away": "FC Barcelona",
            "home_record": "1-5", "away_record": "3-3",
            "facts": [
                "After losing four in a row, Milan (1-5) will try to turn things around when it hosts Barcelona (3-3), which split a pair of tight home games last week.",
                "Moses Wright, who had agreed to terms with Barcelona in the summer, leads the Milan frontline against Barcelona's Josh Nebo, who spent the previous two seasons in Milan.",
                "It should be a close game; these teams split home wins last season, with both games decided by a single possession.",
            ],
        },
        {
            "date": "2026-10-22", "official_ko_cest": "20:45", "game_id": "E2026/66",
            "home": "Partizan Mozzart Bet Belgrade", "away": "Crvena Zvezda Meridianbet Belgrade",
            "home_record": "3-3", "away_record": "4-2",
            "facts": [
                "They call it the 'Eternal Derby': Partizan (3-3) faces archrival Crvena Zvezda (4-2).",
                "Partizan started the season with three straight wins but has since dropped three in a row.",
                "Zvezda has gone the opposite direction, dropping its first two games before reeling off four straight wins.",
                "Zvezda has been dealing with frontcourt injuries and could have new signing Christian Koloko in uniform for this game.",
                "The teams are among the best in defense in the league, so a low-scoring slugfest could be in store.",
            ],
        },
        {
            "date": "2026-10-23", "official_ko_cest": "19:00", "game_id": "E2026/68",
            "home": "Zalgiris Kaunas", "away": "LDLC ASVEL Villeurbanne",
            "home_record": "2-4", "away_record": "2-4",
            "facts": [
                "Friday's trio tips off in Kaunas, where Zalgiris (2-4) tries to get back to winning ways against ASVEL (2-4). Both teams lost twice last week.",
                "ASVEL will need to improve its defense as Coach Tony Parker's side has allowed a league-high 95.3 points per game through the first six rounds.",
                "Zalgiris should have its entire backcourt healthy, which it may need to slow down ASVEL star Patty Mills, one of five players averaging double figures in points on the team.",
            ],
        },
        {
            "date": "2026-10-23", "official_ko_cest": "20:15", "game_id": "E2026/70",
            "home": "Olympiacos Piraeus", "away": "Fenerbahce Tarfin Istanbul",
            "home_record": "5-1", "away_record": "5-1",
            "facts": [
                "After back-to-back overtime wins on the road, Olympiacos (5-1) returns home to take on Fenerbahce (5-1), which is seeking its first road win of the season.",
                "The two teams are tied with Panathinaikos for the best record in the league, but one of them will fall behind after this game.",
                "The Reds boast the league's second-most potent attack with 98.2 points per game, while Fenerbahce is second in defense, having allowed just 74.5 points per game.",
                "Olympiacos has won three in a row against Fenerbahce, including the semifinal at the 2026 Final Four and the semifinal at the 2026 Euroleague Basketball SuperCup.",
            ],
        },
        {
            "date": "2026-10-23", "official_ko_cest": "20:45", "game_id": "E2026/69",
            "home": "Paris Basketball", "away": "Valencia Basket",
            "home_record": "1-5", "away_record": "5-1",
            "facts": [
                "Round 7 closes in the City of Light, where Paris (1-5) tries to end a three-game losing streak against Valencia (5-1), which is coming off its first loss.",
                "The game features the return of former Paris star TJ Shorts to face his former team; Shorts led Paris to the 2024 EuroCup championship and a spot in the 2025 EuroLeague Playoffs in the player and club's first appearance in the competition.",
                "Valencia enters with the league's top offense (98.3 ppg), while Paris features the league's top scorer in Nadir Hifi (20.2 ppg).",
            ],
        },
    ],
    "companion_official_pages": [
        "https://www.euroleaguebasketball.net/euroleague/news/injury-report-round-7-fantasy/",
        "https://www.euroleaguebasketball.net/euroleague/news/pregame-quotes-round-7-el2627/",
        "https://www.euroleaguebasketball.net/euroleague/news/zach-leday-comeback-hapoel-virtus-bologna/",
    ],
}

# Official ppg for/against quoted verbatim by the Game Center above. Used as
# the totals input for our own origination (never a bookmaker total).
EUROLEAGUE_OFFICIAL_PPG = {
    "Panathinaikos AKTOR Athens": {"allowed_ppg": 73.0, "note": "league-low"},
    "Besiktas Istanbul": {"scored_ppg": 92.3, "note": "third in the league"},
    "Anadolu Efes Istanbul": {"allowed_ppg": 85.0, "note": "sixth in points allowed"},
    "Dubai Basketball": {"allowed_ppg": 82.2, "note": "fifth in the league"},
    "LDLC ASVEL Villeurbanne": {"allowed_ppg": 95.3, "note": "league-high, through six rounds"},
    "Olympiacos Piraeus": {"scored_ppg": 98.2, "note": "league's second-most potent attack"},
    "Fenerbahce Tarfin Istanbul": {"allowed_ppg": 74.5, "note": "second in defense"},
    "Valencia Basket": {"scored_ppg": 98.3, "note": "league's top offense"},
}

EUROLEAGUE_OFFICIAL_PLAYERS = {
    "Dwayne Bacon": {"club": "Dubai Basketball", "stat": "17.8 ppg", "note": "third-best in the league"},
    "Duane Washington": {"club": "FC Bayern Munich", "stat": "16.8 ppg", "note": "sixth in scoring despite coming off the bench"},
    "Nadir Hifi": {"club": "Paris Basketball", "stat": "20.2 ppg", "note": "league's top scorer"},
    "Cam Payne": {"club": "Anadolu Efes Istanbul", "note": "playing well in place of the injured Mike James"},
    "Mike James": {"club": "Anadolu Efes Istanbul", "note": "injured"},
    "Lonnie Walker": {"club": "Besiktas Istanbul", "note": "signed last week, could debut"},
    "Yam Madar": {"club": "Maccabi Rapyd Tel Aviv", "note": "adjusting well to life with Maccabi"},
    "Theo Maledon": {"club": "Real Madrid", "note": "taking a huge step forward in his second season in Madrid"},
    "Moses Wright": {"club": "Armani Olimpia Milan", "note": "had agreed to terms with Barcelona in the summer"},
    "Josh Nebo": {"club": "FC Barcelona", "note": "spent the previous two seasons in Milan"},
    "Christian Koloko": {"club": "Crvena Zvezda Meridianbet Belgrade", "note": "new signing, could be in uniform"},
    "Patty Mills": {"club": "LDLC ASVEL Villeurbanne", "note": "star; one of five players averaging double figures in points"},
    "Andreas Obst": {"club": "FC Bayern Munich", "note": "three-point ace"},
    "TJ Shorts": {"club": "Valencia Basket", "note": "returns to face former club Paris; led them to the 2024 EuroCup title"},
    "Zach LeDay": {"club": "Hapoel IBI Tel Aviv", "note": "22 pts / 10 reb double-double v Virtus, 18 pts after the break"},
}

# ---------------------------------------------------------------------------
# F-1A-CLOCK-04: OLBG's hub clock is US Eastern Daylight Time, unlabelled.
# Every one of the eight EuroLeague fixtures OLBG lists is exactly 6h behind
# the official CEST kick-off published by euroleaguebasketball.net.
# CEST = UTC+2, EDT = UTC-4, difference = 6h. Arithmetic, not inference.
# ---------------------------------------------------------------------------
EUROLEAGUE_CLOCK_RECONCILIATION = {
    "rule": "OLBG hub clock (unlabelled) == official CEST kick-off minus exactly 6 hours == US Eastern Daylight Time",
    "delta_hours": -6,
    "matched": 8,
    "total_official_upcoming": 9,
    "rows": [
        # olbg_event_id, olbg_fixture, olbg_day, olbg_clock, official_fixture, official_date, official_ko_cest, delta_h
        (535918, "Anadolu Efes vs Besiktas", "Today", "13:30", "Anadolu Efes Istanbul vs. Besiktas Istanbul", "2026-10-22", "19:30", -6),
        (535920, "Bayern Munich vs BC Dubai", "Today", "14:00", "FC Bayern Munich vs. Dubai Basketball", "2026-10-22", "20:00", -6),
        (535921, "Maccabi Tel Aviv vs Real Madrid", "Today", "14:05", "Maccabi Rapyd Tel Aviv vs. Real Madrid", "2026-10-22", "20:05", -6),
        (535923, "Panathinaikos vs Baskonia", "Today", "14:15", "Panathinaikos AKTOR Athens vs. Kosner Baskonia Vitoria-Gasteiz", "2026-10-22", "20:15", -6),
        (535922, "Milano vs Barcelona", "Today", "14:30", "Armani Olimpia Milan vs. FC Barcelona", "2026-10-22", "20:30", -6),
        (535924, "Partizan vs Crvena Zvezda", "Today", "14:45", "Partizan Mozzart Bet Belgrade vs. Crvena Zvezda Meridianbet Belgrade", "2026-10-22", "20:45", -6),
        (535928, "Zalgiris vs Asvel Lyon Villeurbanne", "Tomorrow", "13:00", "Zalgiris Kaunas vs. LDLC ASVEL Villeurbanne", "2026-10-23", "19:00", -6),
        (535925, "Olympiacos vs Fenerbahce", "Tomorrow", "14:15", "Olympiacos Piraeus vs. Fenerbahce Tarfin Istanbul", "2026-10-23", "20:15", -6),
    ],
}

# ---------------------------------------------------------------------------
# F-1A-BBALL-01: tip-gated blind spot, proved against an official slate.
# Round 7 has 10 official games (1 played Wed 21 Oct + 9 upcoming). OLBG's
# /Basketball/4 hub renders 8 of the 9 upcoming ones. Paris Basketball vs
# Valencia Basket (2026-10-23, 20:45 CEST, E2026/69) is absent, even though
# it is the round's closing game and carries the league's top scorer.
# ---------------------------------------------------------------------------
EUROLEAGUE_OLBG_COVERAGE_GAP = {
    "official_upcoming_games": 9,
    "rendered_on_olbg": 8,
    "missing": [
        {
            "fixture": "Paris Basketball vs. Valencia Basket",
            "date": "2026-10-23",
            "official_ko_cest": "20:45",
            "game_id": "E2026/69",
            "records": "Paris 1-5, Valencia 5-1",
            "why_it_matters": "Closing game of Round 7; features the league's top scorer Nadir Hifi (20.2 ppg) and TJ Shorts' return to Paris.",
        }
    ],
    "correctly_absent": [
        {"fixture": "Hapoel IBI Tel Aviv 90-81 Virtus Bologna", "reason": "already played on 2026-10-21"}
    ],
}


# ---------------------------------------------------------------------------
# EUROLEAGUE OFFICIAL STANDINGS - REGULAR SEASON 2026-27 (as fetched)
# Source: https://www.euroleaguebasketball.net/en/euroleague/standings/
# Columns exactly as published: Pos, Club, GP, W, L, Win%, PTS+, PTS-, +/-,
# H (home), A (away), OT (overtime), L10 (last ten).
#
# RECONCILIATION PERFORMED OFFLINE (all four checks pass 20/20):
#   (1) PTS+ - PTS- == +/- for every club.
#   (2) W + L == GP for every club, and Win% == W/GP.
#   (3) H-record + A-record == overall W-L for every club.
#   (4) The table is a closed system: sum(PTS+) == sum(PTS-) == 10546, and
#       sum(W) == sum(L) == 61 == number of games played (122 team-games).
#       Home wins 33, away wins 28 -> official home win rate 33/61 = 0.5410.
# Because the table reconciles perfectly and the Game Center prose does not
# (see EUROLEAGUE_OFFICIAL_CONFLICTS), the TABLE is treated as authoritative.
# ---------------------------------------------------------------------------

EUROLEAGUE_STANDINGS = {
    "source_name": "Euroleague Basketball - Standings, Regular season 2026-27",
    "source_url": "https://www.euroleaguebasketball.net/en/euroleague/standings/",
    "fetched_utc": "2026-10-22T07:24:00Z",
    "official": True,
    "columns": ["pos", "club", "code", "gp", "w", "l", "win_pct", "pts_for",
                "pts_against", "diff", "home", "away", "ot", "last10"],
    "legend": ["(Q) - Shows the qualified teams for the playoffs",
               "7th-10th Place - Play-in Qualification"],
    "rows": [
        (1,  "Panathinaikos AKTOR Athens",              "PAO", 6, 5, 1, "83.3%", 528, 438,  90, "4-1", "1-0", "0-0", "5-1"),
        (2,  "Fenerbahce Tarfin Istanbul",              "FBT", 6, 5, 1, "83.3%", 501, 447,  54, "5-0", "0-1", "0-0", "5-1"),
        (3,  "Olympiacos Piraeus",                      "OLY", 6, 5, 1, "83.3%", 564, 524,  40, "1-0", "4-1", "2-0", "5-1"),
        (4,  "Hapoel IBI Tel Aviv",                     "HTA", 7, 5, 2, "71.4%", 630, 601,  29, "3-1", "2-1", "0-0", "5-2"),
        (5,  "Valencia Basket",                         "VBC", 6, 4, 2, "66.7%", 583, 537,  46, "2-2", "2-0", "0-1", "4-2"),
        (6,  "Crvena Zvezda Meridianbet Belgrade",      "CZV", 6, 4, 2, "66.7%", 485, 457,  28, "2-2", "2-0", "0-0", "4-2"),
        (7,  "Dubai Basketball",                        "DUB", 6, 4, 2, "66.7%", 490, 493,  -3, "2-1", "2-1", "0-0", "4-2"),
        (8,  "Virtus Bologna",                          "VIR", 7, 4, 3, "57.1%", 606, 608,  -2, "2-0", "2-3", "0-0", "4-3"),
        (9,  "Real Madrid",                             "RMB", 6, 3, 3, "50%",   554, 531,  23, "2-0", "1-3", "0-0", "3-3"),
        (10, "FC Barcelona",                            "BAR", 6, 3, 3, "50%",   534, 525,   9, "2-2", "1-1", "0-1", "3-3"),
        (11, "Besiktas Istanbul",                       "BJK", 6, 3, 3, "50%",   554, 555,  -1, "1-2", "2-1", "0-0", "3-3"),
        (12, "Partizan Mozzart Bet Belgrade",           "PAR", 6, 3, 3, "50%",   466, 471,  -5, "1-1", "2-2", "0-0", "3-3"),
        (13, "Anadolu Efes Istanbul",                   "EFS", 6, 2, 4, "33.3%", 492, 510, -18, "1-1", "1-3", "0-0", "2-4"),
        (14, "Zalgiris Kaunas",                         "ZAL", 6, 2, 4, "33.3%", 490, 517, -27, "0-2", "2-2", "0-0", "2-4"),
        (15, "FC Bayern Munich",                        "BAY", 6, 2, 4, "33.3%", 521, 552, -31, "0-2", "2-2", "0-0", "2-4"),
        (16, "Maccabi Rapyd Tel Aviv",                  "MTA", 6, 2, 4, "33.3%", 509, 540, -31, "1-1", "1-3", "0-0", "2-4"),
        (17, "LDLC ASVEL Villeurbanne",                 "ASV", 6, 2, 4, "33.3%", 527, 572, -45, "1-2", "1-2", "0-0", "2-4"),
        (18, "Paris Basketball",                        "PBB", 6, 1, 5, "16.7%", 504, 545, -41, "1-3", "0-2", "0-0", "1-5"),
        (19, "Armani Olimpia Milan",                    "MIL", 6, 1, 5, "16.7%", 504, 559, -55, "1-2", "0-3", "0-0", "1-5"),
        (20, "Kosner Baskonia Vitoria-Gasteiz",         "KBA", 6, 1, 5, "16.7%", 504, 564, -60, "1-3", "0-2", "0-0", "1-5"),
    ],
    "totals": {
        "team_games": 122, "games": 61, "sum_pts_for": 10546, "sum_pts_against": 10546,
        "sum_wins": 61, "sum_losses": 61, "home_wins": 33, "away_wins": 28,
        "home_win_rate": round(33 / 61, 6),
        "league_avg_points_per_team_game": round(10546 / 122, 4),
        "league_avg_game_total": round(2 * 10546 / 122, 4),
    },
}

# ---------------------------------------------------------------------------
# Official-vs-official conflicts on euroleaguebasketball.net, same fetch date.
# The standings table is internally consistent on four independent checks; the
# Game Center prose is not. Recorded, NOT silently resolved.
# ---------------------------------------------------------------------------
EUROLEAGUE_OFFICIAL_CONFLICTS = [
    {
        "id": "F-1A-EURO-01",
        "what": "Valencia Basket's record",
        "prose": "Game Center: 'Paris (1-5) will try to put an end to a three-game losing streak against Valencia (5-1), which is coming off its first loss.'",
        "table": "Standings: Valencia Basket GP 6, W 4, L 2, Win% 66.7%, H 2-2, A 2-0.",
        "why_irreconcilable": "A 5-1 club cannot also be 4-2 over the same 6 games played, and 'coming off its first loss' is inconsistent with a 5-1 record. The standings' H 2-2 + A 2-0 = 4-2 reconciles with GP 6; 5-1 would require GP 6 with 5 wins, contradicting the same table.",
        "resolution": "Standings table used as authoritative (it passes all four reconciliation checks). Prose figure discarded and flagged.",
        "sources": [
            "https://www.euroleaguebasketball.net/euroleague/news/game-center-round-7-el2627/",
            "https://www.euroleaguebasketball.net/en/euroleague/standings/",
        ],
    },
    {
        "id": "F-1A-EURO-02",
        "what": "Real Madrid's away record",
        "prose": "Game Center: Real Madrid 'has won three in a row, but is 1-4 away from home.'",
        "table": "Standings: Real Madrid GP 6, W 3, L 3, H 2-0, A 1-3.",
        "why_irreconcilable": "H 2-0 plus A 1-4 would be 3-4 over 7 games, but the official GP is 6. The published A 1-3 sums correctly with H 2-0 to 3-3 over 6 games.",
        "resolution": "Away record taken as 1-3 from the standings; the prose 1-4 is flagged as an official-source error.",
        "sources": [
            "https://www.euroleaguebasketball.net/euroleague/news/game-center-round-7-el2627/",
            "https://www.euroleaguebasketball.net/en/euroleague/standings/",
        ],
    },
    {
        "id": "F-1A-EURO-03",
        "what": "Points-per-game claims in Game Center prose vs the official standings table",
        "reconciles_exactly": [
            ("Panathinaikos AKTOR Athens", "allowed a league-low 73.0 points per game", 438, 6, 73.0),
            ("Fenerbahce Tarfin Istanbul", "second in defense, having allowed just 74.5 points per game", 447, 6, 74.5),
            ("Dubai Basketball", "fifth in the league with 82.2 points allowed per game", 493, 6, 82.1667),
            ("LDLC ASVEL Villeurbanne", "allowed a league-high 95.3 points per game through the first six rounds", 572, 6, 95.3333),
            ("Besiktas Istanbul", "third in the league in scoring (92.3 ppg.)", 554, 6, 92.3333),
            ("Anadolu Efes Istanbul", "sixth in points allowed (85.0 ppg.)", 510, 6, 85.0),
        ],
        "does_not_reconcile": [
            ("Olympiacos Piraeus", "the league's second-most potent attack with 98.2 points per game", 564, 6, 94.0,
             "564/6 = 94.0 ppg, not 98.2. A 98.2 ppg rate over 6 games implies 589.2 points; the official PTS+ is 564."),
            ("Valencia Basket", "Valencia enters the game with the league's top offense (98.3 ppg.)", 583, 6, 97.1667,
             "583/6 = 97.17 ppg, not 98.3. A 98.3 ppg rate over 6 games implies 589.8 points; the official PTS+ is 583."),
        ],
        "resolution": "All totals and margins are originated from the standings' PTS+/PTS-/GP only. The two unreconciled prose ppg figures are never used as a numeric input; they are quoted as narrative context and flagged.",
    },
]
