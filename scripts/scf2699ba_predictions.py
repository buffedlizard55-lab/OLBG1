"""Session cf2699ba-olbg1 — written selections and the review register.

Prediction bodies are hand-written prose. Every factual clause is attached to the
official source it came from, and the validator re-checks that each attached
source id exists and was observed this session. The words "model" and "verified"
are banned from the published prose by the validator; the evidence trail lives in
the linked source block instead.
"""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "cf2699ba")

PREDICTIONS = [
    {
        "id": "p1",
        "fixture_id": "fx-urc-edinburgh-lions",
        "sport": "rugby-union",
        "match": "Edinburgh Rugby v 10bet Lions",
        "competition": "United Rugby Championship Round 4",
        "selection": "Edinburgh Rugby to win",
        "market": "Match winner",
        "tier": "Medium",
        "p": 0.85,
        "decimal": 1.176,
        "american": -567,
        "band_note": "Above the 70% threshold but priced shorter than -250, so it sits outside the "
                     "price window the brief asks us to concentrate on. Published, not counted as High.",
        "body": "Edinburgh welcome 10bet Lions to Hive Stadium for a Round 4 tie that kicks off at 14:45 "
                "local time on Friday 23 October. Edinburgh won their last match 29-12 away at Zebre "
                "Parma on 10 October, a 17-point margin, while Lions conceded 57 points at Vodacom Bulls "
                "in a 42-point defeat. On the only evidence available this week the gap is wide, and home "
                "advantage adds to it. The selection is Edinburgh Rugby to win the match.",
        "facts": [
            {"text": "Kick-off Friday 23 October 2026, 14:45 local, Hive Stadium", "src": "src-urc-round4"},
            {"text": "Zebre Parma 12-29 Edinburgh on 10 October 2026", "src": "src-urc-round4"},
            {"text": "Vodacom Bulls 57-15 10bet Lions on 10 October 2026", "src": "src-urc-round4"},
        ],
        "open_gaps": ["No team news, travel or availability list was published on the page consulted.",
                      "One verified round of results is the entire form sample."],
    },
    {
        "id": "p2",
        "fixture_id": "fx-urc-connacht-zebre",
        "sport": "rugby-union",
        "match": "Connacht Rugby v Zebre Parma",
        "competition": "United Rugby Championship Round 4",
        "selection": "Connacht Rugby to win",
        "market": "Match winner",
        "tier": "Low",
        "p": 0.585,
        "decimal": 1.709,
        "american": -141,
        "band_note": "Inside the -250 to +10000 window but below 70%, so it cannot be High.",
        "body": "Connacht host Zebre Parma at Dexcom Stadium on Friday 23 October. Both clubs lost by "
                "exactly 17 points in Round 3: Connacht went down 36-19 at Glasgow Warriors on 9 October "
                "and Zebre were beaten 12-29 at home by Edinburgh the following day. With the form sample "
                "level, venue is the whole of the edge, and Connacht have it. The selection is Connacht "
                "Rugby to win the match.",
        "facts": [
            {"text": "Kick-off Friday 23 October 2026, 14:45 local, Dexcom Stadium", "src": "src-urc-round4"},
            {"text": "Glasgow Warriors 36-19 Connacht on 9 October 2026", "src": "src-urc-round4"},
            {"text": "Zebre Parma 12-29 Edinburgh on 10 October 2026", "src": "src-urc-round4"},
        ],
        "open_gaps": ["No availability or team announcements were obtainable.",
                      "A single round cannot distinguish two clubs with identical margins."],
    },
    {
        "id": "p3",
        "fixture_id": "fx-mlb-ws-g1",
        "sport": "baseball",
        "match": "Tampa Bay Rays at Milwaukee Brewers — World Series Game 1",
        "competition": "MLB World Series",
        "selection": "Milwaukee Brewers money line",
        "market": "Money line",
        "tier": "Low",
        "p": 0.561,
        "decimal": 1.783,
        "american": -128,
        "band_note": "Inside the price window, below 70%.",
        "body": "Milwaukee open the World Series at American Family Field on Friday, with first pitch at "
                "20:00 Eastern, 00:00 UTC on Saturday. They finished the regular season 103-59, scoring "
                "832 runs and allowing 618, while Tampa Bay went 98-64 and were 43-38 on the road. Jacob "
                "Misiorowski is the announced Milwaukee starter against Nick Martinez. The season-long "
                "run profile favours the home side. The selection is Milwaukee Brewers on the money line.",
        "facts": [
            {"text": "Game 1, American Family Field, 2026-10-24T00:00:00Z, ifNecessary=N", "src": "src-mlb-schedule"},
            {"text": "Probable pitchers: Nick Martinez (TB), Jacob Misiorowski (MIL)", "src": "src-mlb-schedule"},
            {"text": "Tampa Bay 98-64, away 43-38, RS 736 RA 650", "src": "src-mlb-standings-al"},
            {"text": "Milwaukee 103-59, RS 832 RA 618", "src": "src-mlb-records-capture"},
        ],
        "open_gaps": ["Postseason form is not what the records measure; the regular season is complete.",
                      "No injury report or lineup card was published on the pages consulted."],
    },
    {
        "id": "p4",
        "fixture_id": "fx-mlb-ws-g1",
        "sport": "baseball",
        "match": "Tampa Bay Rays at Milwaukee Brewers — World Series Game 1",
        "competition": "MLB World Series",
        "selection": "Tampa Bay Rays +1.5 on the run line",
        "market": "Run line 1.5",
        "tier": "Low",
        "p": 0.594,
        "decimal": 1.683,
        "american": -146,
        "band_note": "Inside the price window, below 70%.",
        "body": "The run line is the way to take Tampa Bay without backing them to win outright. Across 162 "
                "games the Rays scored 736 and allowed 650, roughly 4.5 for and 4.0 against, and the pairing "
                "with Milwaukee's 832 and 618 puts the game near 8.75 combined runs, which keeps the final "
                "margin small more often than not. A one-run defeat still pays. The selection is Tampa Bay "
                "Rays +1.5.",
        "facts": [
            {"text": "Tampa Bay RS 736 / RA 650 over 162 games", "src": "src-mlb-standings-al"},
            {"text": "Milwaukee RS 832 / RA 618 over 162 games", "src": "src-mlb-records-capture"},
            {"text": "Game 1 confirmed, start 2026-10-24T00:00:00Z", "src": "src-mlb-schedule"},
        ],
        "open_gaps": ["Bullpen usage and late-inning availability were not published on the pages consulted."],
    },
    {
        "id": "p5",
        "fixture_id": "fx-nhl-mtl-chi",
        "sport": "ice-hockey",
        "match": "Montreal Canadiens at Chicago Blackhawks",
        "competition": "NHL",
        "selection": "Montreal Canadiens money line",
        "market": "Money line",
        "tier": "Low",
        "p": 0.6,
        "decimal": 1.667,
        "american": -150,
        "band_note": "Inside the price window, below 70%.",
        "body": "Montreal are at the United Center for a 20:00 Eastern start on Friday, 00:00 UTC on Saturday. "
                "Three feeds in the NHL's own schedule carry Montreal between -162 and -170 and Chicago "
                "between +134 and +142, while three other feeds quote Chicago as the 1.59 favourite, so the "
                "picture is genuinely mixed. There is a real but small edge to Montreal on the majority "
                "reading. The selection is Montreal Canadiens on the money line.",
        "facts": [
            {"text": "Game 2026020166, United Center, 2026-10-24T00:00:00Z, state FUT", "src": "src-nhl-schedule"},
            {"text": "Montreal quotes -170 / -170 / -162; Chicago +138 / +142 / +134", "src": "src-nhl-schedule"},
            {"text": "Contradicting feed quotes Chicago 1.59 against Montreal 2.35", "src": "src-nhl-schedule"},
        ],
        "open_gaps": ["No 2026-27 record or recent result for either club was read, so no form claim is made.",
                      "No lineup, goaltender or injury confirmation was available."],
    },
    {
        "id": "p6",
        "fixture_id": "fx-nhl-tbl-col",
        "sport": "ice-hockey",
        "match": "Tampa Bay Lightning at Colorado Avalanche",
        "competition": "NHL",
        "selection": "Colorado Avalanche money line",
        "market": "Money line",
        "tier": "Low",
        "p": 0.536,
        "decimal": 1.866,
        "american": -115,
        "band_note": "Inside the price window, below 70%.",
        "body": "Colorado host Tampa Bay at Ball Arena with a 01:00 UTC start on Saturday. Three feeds in the "
                "NHL schedule put Colorado between -125 and -129 and Tampa Bay between +105 and +106, which "
                "is a modest edge once the margin is removed. It is not a match anyone should describe as "
                "one-sided, and nothing about either club's start to the season was obtainable. The selection "
                "is Colorado Avalanche on the money line.",
        "facts": [
            {"text": "Game 2026020167, Ball Arena, 2026-10-24T01:00:00Z, state FUT", "src": "src-nhl-schedule"},
            {"text": "Colorado quotes -129 / -125 / -128; Tampa Bay +105 / +105 / +106", "src": "src-nhl-schedule"},
        ],
        "open_gaps": ["No club-level form, goaltender or availability information was available.",
                      "This fixture was not present on the OLBG top list captured, so it is official-only."],
    },
    {
        "id": "p7",
        "fixture_id": "fx-mlb-ws-g1",
        "sport": "baseball",
        "match": "Tampa Bay Rays at Milwaukee Brewers — World Series Game 1",
        "competition": "MLB World Series",
        "selection": "Over 8.5 runs",
        "market": "Game total 8.5",
        "tier": "Low",
        "p": 0.533,
        "decimal": 1.876,
        "american": -114,
        "band_note": "Inside the price window, below 70%.",
        "body": "Tampa Bay scored 4.54 runs a game and allowed 4.01 across 162 games; Milwaukee scored 5.14 "
                "and allowed 3.82. Pairing each side's scoring with the other's concession puts the combined "
                "expectation at roughly 8.75 runs, which sits just above an 8.5 line. Two announced starters, "
                "Nick Martinez and Jacob Misiorowski, are the only pitching information available. The "
                "selection is Over 8.5 runs.",
        "facts": [
            {"text": "Tampa Bay 736 RS / 650 RA in 162 games (4.54 / 4.01 per game)", "src": "src-mlb-standings-al"},
            {"text": "Milwaukee 832 RS / 618 RA in 162 games (5.14 / 3.82 per game)", "src": "src-mlb-records-capture"},
            {"text": "Announced starters Martinez and Misiorowski; game 1 of the World Series", "src": "src-mlb-schedule"},
        ],
        "open_gaps": ["Park factors, weather and bullpen state were not published on the pages consulted."],
    },
]

FLAGS = [
    {"id": "F-CF-01", "sev": "high", "sport": "all",
     "title": "OLBG start times carry no zone label and mix conventions inside the same capture",
     "detail": "The same hub list rendered 12:12 for a 17:12 Towcester race (a US-Eastern rendering), "
               "14:45 for URC fixtures the URC itself publishes as 14:45 local UK/Irish time, and 16:00 for "
               "a Formula 1 race whose track time at Austin is 16:00. No page states a timezone. Times were "
               "therefore published verbatim and never converted to UTC.",
     "rows": ["all discovery rows"], "src": ["src-olbg-hubs", "src-urc-round4", "src-f1-usgp"]},
    {"id": "F-CF-02", "sev": "medium", "sport": "ice-hockey",
     "title": "OLBG minute field is corrupted for on-the-hour NHL starts",
     "detail": "OLBG shows 'Today 20:07' for Montreal at Chicago. The NHL's own feed gives "
               "2026-10-24T00:00:00Z, which is 20:00 Eastern. Every on-the-hour NHL row on the hub carries "
               ":07 minutes, so the minute field cannot be trusted.",
     "rows": ["199984"], "src": ["src-olbg-hubs", "src-nhl-schedule"]},
    {"id": "F-CF-03", "sev": "high", "sport": "ice-hockey",
     "title": "The NHL feed embeds mutually contradictory prices for the same outcome",
     "detail": "For game 2026020166 the feed gives Montreal 2.35 (decimal), 1.60 and 2.03 on three providers "
               "but -170, -170 and -162 on three others; Chicago is simultaneously 1.59 and +138. One set "
               "makes Chicago the favourite, the other makes Montreal the favourite. Only the three "
               "American-quote providers were used, and the contradiction is disclosed on every affected row.",
     "rows": ["fx-nhl-mtl-chi", "fx-nhl-tbl-col"], "src": ["src-nhl-schedule"]},
    {"id": "F-CF-04", "sev": "medium", "sport": "ice-hockey",
     "title": "OLBG lists far more NHL games than the league has scheduled today",
     "detail": "The hub listed at least fifteen NHL fixtures under 'Today', but the NHL schedule for "
               "2026-10-23 contains exactly two games (numberOfGames=2). Expired rows are left in the list "
               "and no expired badge was shown, so an OLBG row is not evidence that a game is still to come.",
     "rows": ["ice-hockey hub"], "src": ["src-olbg-hubs", "src-nhl-schedule"]},
    {"id": "F-CF-05", "sev": "medium", "sport": "rugby-union",
     "title": "URC page names the same clubs two different ways on one page",
     "detail": "The Round 4 fixture block prints 'Hollywoodbets Sharks', '10bet Lions', 'Connacht Rugby' and "
               "'Edinburgh Rugby'; the Round 3 results block on the same page prints 'Sharks', 'Lions', "
               "'Connacht' and 'Edinburgh'. A six-entry alias table is the only name mapping used in this "
               "desk and it is published with the code.",
     "rows": ["fx-urc-cardiff-sharks", "fx-urc-connacht-zebre", "fx-urc-edinburgh-lions"],
     "src": ["src-urc-round4"]},
    {"id": "F-CF-06", "sev": "high", "sport": "golf",
     "title": "Golf returned zero events — the covered sport has no discoverable match list today",
     "detail": "The OLBG golf hub rendered 'No tips found.' at 16:20Z. No tournament, no field and no price "
               "can be offered. Nothing was substituted from another source.",
     "rows": ["golf"], "src": ["src-olbg-hubs"]},
    {"id": "F-CF-07", "sev": "high", "sport": "rugby-league",
     "title": "Rugby League has no fixtures at all on OLBG, only 2027 outrights",
     "detail": "The hub carried State of Origin 2027, Super League 2027 and NRL 2027 only. The 2026 Rugby "
               "League World Cup knockout stage falls in this window but is not listed, so the brief's "
               "five-match target cannot be attempted from OLBG discovery.",
     "rows": ["2695857", "2801554", "2801600"], "src": ["src-olbg-hubs"]},
    {"id": "F-CF-08", "sev": "high", "sport": "darts",
     "title": "pdc.tv returns a consent wall instead of match content",
     "detail": "The European Championship tournament page returned a CookieYes consent dialog and no "
               "schedule. Twelve darts fixtures are therefore discovery-only. The same barrier was "
               "recorded by session 8f6d7364 on 2026-10-22 as F-8F6D-03.",
     "rows": ["32335", "32326", "32328"], "src": ["src-pdc"]},
    {"id": "F-CF-09", "sev": "medium", "sport": "snooker",
     "title": "WST match list is reachable but does not reach today's session in one capture",
     "detail": "wst.tv/matches returned the Northern Ireland Open list, but the first chunk covers 18-19 "
               "October. It confirms Round 1 results for Scott Donaldson (4-0 over Wu Yize) and David "
               "Gilbert (4-1 over Oliver Sykes) yet says nothing about the 23 October matches, which are "
               "not verified and therefore unpriced.",
     "rows": ["9951", "9950"], "src": ["src-wst-matches"]},
    {"id": "F-CF-10", "sev": "medium", "sport": "basketball",
     "title": "Both basketball routes failed to expose fixtures",
     "detail": "The EuroLeague game centre is client-rendered and returns a club list with no dates; "
               "cdn.nba.com returned HTTP 500. Fifteen basketball rows are discovery-only.",
     "rows": ["basketball hub"], "src": ["src-euroleague-gc"]},
    {"id": "F-CF-11", "sev": "high", "sport": "tennis",
     "title": "The nine OLBG tennis rows carry no competition, and the tours list different matches",
     "detail": "OLBG routes every tennis row through /All_Tennis/All_Events/ with no tournament name. The ATP "
               "current-scoreboard page at the same moment lists Brussels and Lyon quarter-finals, none of "
               "which match the OLBG pairings. The WTA scores page is client-rendered. No tennis fixture "
               "could be tied to an official draw.",
     "rows": ["902150", "902155", "902163"], "src": ["src-olbg-hubs", "src-atp-scores", "src-wta-scores"]},
    {"id": "F-CF-12", "sev": "medium", "sport": "cricket",
     "title": "Cricket Australia page returned filters, not fixtures",
     "detail": "cricket.com.au/matches rendered series and team filter lists only in the first capture. The "
               "seven domestic and international cricket rows remain discovery-only; no cricket total, "
               "handicap or winner price is published.",
     "rows": ["188839", "188832", "188840"], "src": ["src-cricket-au"]},
    {"id": "F-CF-13", "sev": "medium", "sport": "gaelic-sports",
     "title": "Munster GAA fixture detail sits behind sub-pages that were not reached",
     "detail": "The fixtures index returned navigation only. The four club fixtures (Cork, Galway, Limerick) "
               "are therefore unverified, including the St Finbarrs v Nemo Rangers game scheduled for "
               "25 October.",
     "rows": ["3530", "3532", "3531", "3537"], "src": ["src-munster-gaa"]},
    {"id": "F-CF-14", "sev": "medium", "sport": "baseball",
     "title": "Live MLB standings returned one division in the first capture",
     "detail": "The fresh standings call put NL East clubs in the first chunk, so Milwaukee's record was "
               "taken from the repository's canonical 2026-10-22 capture of the same endpoint. The value "
               "cannot have changed because the 162-game season is complete, but the observation is one "
               "day old and is labelled as such.",
     "rows": ["fx-mlb-ws-g1"], "src": ["src-mlb-standings-nl", "src-mlb-records-capture"]},
    {"id": "F-CF-15", "sev": "low", "sport": "all",
     "title": "OLBG club and player spellings differ from official names",
     "detail": "'Nissa' for Nice, 'Newcastle Red Bulls' for the Newcastle Premiership club, 'William OConnor' "
               "for William O'Connor, 'Pays dAix UC' and 'EHC Munchen'. Names are reproduced as published on "
               "OLBG rows and never silently corrected.",
     "rows": ["609558", "609573", "32328", "12083"], "src": ["src-olbg-hubs"]},
    {"id": "F-CF-16", "sev": "high", "sport": "all",
     "title": "No injury, suspension or availability information was obtained for any fixture",
     "detail": "None of the official pages reached this session published a team news, injury or suspension "
               "list. No prediction asserts one. This is the single largest gap against the brief.",
     "rows": ["all fixtures"], "src": ["src-nhl-schedule", "src-mlb-schedule", "src-urc-round4"]},
    {"id": "F-CF-17", "sev": "high", "sport": "all",
     "title": "Zero High-confidence selections today, and the reason is structural",
     "detail": "The rule as written needs a probability of at least 70% AND an American price no shorter "
               "than -250, which bounds the eligible band to 70.0-71.4%. Only six fixtures could be "
               "confirmed on an official page, and the strongest of them (Edinburgh, 85%) prices at -567, "
               "outside the window. Nothing was reclassified to manufacture a High.",
     "rows": ["all"], "src": ["src-nhl-schedule", "src-mlb-schedule", "src-urc-round4"]},
    {"id": "F-CF-18", "sev": "medium", "sport": "greyhounds",
     "title": "Greyhound runners are unverified and cannot be checked against GBGB data",
     "detail": "Fifteen race rows with dog names were discovered. GBGB publishes meeting and open-race "
               "calendars, not per-race runner lists, and no GBGB page was fetched this session. No "
               "greyhound selection is priced.",
     "rows": ["689803", "689846", "689717"], "src": ["src-olbg-hubs"]},
    {"id": "F-CF-19", "sev": "medium", "sport": "all",
     "title": "107 indicative prices exist and none of them is evidence",
     "detail": "Where no official input was available, an indicative price was still published so that "
               "every discovered match has a number rather than a silent blank. It is a 50% shrunk OLBG tip "
               "share, capped at 0.90, permanently graded Low, and marked 'indicative' on every row. It must "
               "not be read as a probability or as a tip.",
     "rows": ["107 rows"], "src": ["src-olbg-hubs"]},
]

WORDS = {"model", "models", "verified", "verify", "verification", "algorithm", "ai"}


def main():
    os.makedirs(OUT, exist_ok=True)
    for p in PREDICTIONS:
        p["words"] = len(p["body"].split())
    payloads = {
        "predictions.json": {"session": "cf2699ba-olbg1", "count": len(PREDICTIONS),
                             "note": "Every clause is source-linked. Word counts are computed, minimum 30.",
                             "predictions": PREDICTIONS},
        "flagged.json": {"session": "cf2699ba-olbg1", "count": len(FLAGS), "flags": FLAGS},
    }
    for name, obj in payloads.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
            json.dump(obj, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
    bad = [p["id"] for p in PREDICTIONS if p["words"] < 30]
    hits = [(p["id"], w) for p in PREDICTIONS for w in p["body"].lower().replace(",", " ").replace(".", " ").split() if w in WORDS]
    print(f"predictions={len(PREDICTIONS)} flags={len(FLAGS)} short={bad} banned={hits}")
    print("word counts:", [p["words"] for p in PREDICTIONS])


if __name__ == "__main__":
    main()
