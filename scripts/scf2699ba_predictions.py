#!/usr/bin/env python3
"""T67 - prediction text and the flag register.

Every prediction is at least 30 words, names its selection explicitly, contains no banned word, and
carries fact/source pairs so a reader can walk each clause back to the page it came from.

Run: python3 scripts/scf2699ba_predictions.py
Out: data/cf2699ba/{predictions,flagged}.json
"""
import json
import pathlib
import re

DATA = pathlib.Path(__file__).resolve().parent.parent / "data" / "cf2699ba"
BANNED = ["model", "verified", "backtest", "algorithm", "AI"]

PREDICTIONS = [
    {
        "id": "p1",
        "fixture_id": "fx-urc-edi-lio",
        "sport": "rugby-union",
        "fixture": "Edinburgh v Emirates Lions",
        "market": "Money line",
        "selection": "Edinburgh win",
        "body": "Edinburgh host 10bet Lions at Hive Stadium on Friday 23 October, with the United Rugby "
                "Championship listing a 14:45 local start. Edinburgh won their Round 3 match 29-12 away "
                "at Zebre Parma on 10 October, a 17-point margin, while Lions lost 57-15 at Vodacom Bulls "
                "a day earlier. The selection is Edinburgh Rugby to win the match.",
        "facts": [
            {"k": "Venue and start", "v": "Hive Stadium, 14:45 local on Friday 23 October",
             "src": "src-urc-r4"},
            {"k": "Edinburgh Round 3", "v": "Won 29-12 away at Zebre Parma, 10 October", "src": "src-urc-r4"},
            {"k": "Lions Round 3", "v": "Lost 57-15 away at Bulls, 10 October", "src": "src-urc-r4"},
        ],
    },
    {
        "id": "p2",
        "fixture_id": "fx-urc-con-zeb",
        "sport": "rugby-union",
        "fixture": "Connacht v Zebre Parma",
        "market": "Money line",
        "selection": "Connacht win",
        "body": "Connacht welcome Zebre Parma to Dexcom Stadium for a 14:45 local start on Friday. Both "
                "clubs lost by exactly 17 points in Round 3: Connacht went down 36-19 at Glasgow Warriors "
                "on 9 October, and Zebre lost 12-29 at home to Edinburgh the next day. With the form "
                "identical, the venue is the only separator. The selection is Connacht Rugby to win.",
        "facts": [
            {"k": "Venue and start", "v": "Dexcom Stadium, 14:45 local on Friday 23 October", "src": "src-urc-r4"},
            {"k": "Connacht Round 3", "v": "Lost 36-19 away at Glasgow Warriors, 9 October", "src": "src-urc-r4"},
            {"k": "Zebre Round 3", "v": "Lost 12-29 at home to Edinburgh, 10 October", "src": "src-urc-r4"},
        ],
    },
    {
        "id": "p3",
        "fixture_id": "fx-mlb-ws-g1",
        "sport": "baseball",
        "fixture": "Tampa Bay Rays at Milwaukee Brewers",
        "market": "Money line",
        "selection": "Milwaukee Brewers win",
        "body": "Milwaukee open the World Series at American Family Field on Friday, first pitch 20:00 "
                "Eastern, which is 00:00 UTC on Saturday. They finished the regular season 103-59 with "
                "832 runs scored and 618 allowed. Tampa Bay were 98-64 overall but 43-38 on the road, and "
                "Nick Martinez starts against Jacob Misiorowski. The selection is Milwaukee Brewers on "
                "the money line.",
        "facts": [
            {"k": "Game 1 details", "v": "American Family Field, 2026-10-24T00:00Z, Martinez v Misiorowski",
             "src": "src-mlb-schedule"},
            {"k": "Milwaukee season", "v": "103-59, 832 runs scored, 618 allowed", "src": "src-mlb-records-capture"},
            {"k": "Tampa Bay season", "v": "98-64, 43-38 away", "src": "src-mlb-standings"},
        ],
    },
    {
        "id": "p4",
        "fixture_id": "fx-mlb-ws-g1",
        "sport": "baseball",
        "fixture": "Tampa Bay Rays at Milwaukee Brewers",
        "market": "Run line +1.5",
        "selection": "Tampa Bay Rays +1.5",
        "body": "Tampa Bay's run line is the calmer side of a game the money line treats as close. The "
                "Rays scored 736 runs and allowed 650 over 162 games, which points to roughly 8.75 "
                "combined runs here, so single-run finishes carry a large share of the outcomes. Tampa "
                "Bay +1.5 also covers a one-run defeat. The selection is Tampa Bay Rays +1.5.",
        "facts": [
            {"k": "Tampa Bay runs", "v": "736 scored, 650 allowed in 162 games", "src": "src-mlb-standings"},
            {"k": "Milwaukee runs", "v": "832 scored, 618 allowed in 162 games", "src": "src-mlb-records-capture"},
            {"k": "Run line", "v": "Away side covers by winning or losing by one", "src": "src-mlb-schedule"},
        ],
    },
    {
        "id": "p5",
        "fixture_id": "fx-nhl-mtl-chi",
        "sport": "ice-hockey",
        "fixture": "Montreal Canadiens at Chicago Blackhawks",
        "market": "Money line",
        "selection": "Montreal Canadiens win",
        "body": "Montreal visit the United Center for a 20:00 Eastern start on Friday, which is 00:00 UTC "
                "on Saturday. Three feeds in the league's own schedule quote Montreal between -162 and "
                "-170 and Chicago between +134 and +142, while three others make Chicago the favourite at "
                "1.59. No 2026-27 form was obtainable for either club, so the edge is thin. The selection "
                "is Montreal Canadiens on the money line.",
        "facts": [
            {"k": "Game details", "v": "United Center, 2026-10-24T00:00Z, game 2026020166", "src": "src-nhl-schedule"},
            {"k": "Quotes", "v": "Montreal -162 to -170, Chicago +134 to +142", "src": "src-nhl-schedule"},
            {"k": "Contradiction", "v": "Three other feeds make Chicago the 1.59 favourite", "src": "src-nhl-schedule"},
        ],
    },
    {
        "id": "p6",
        "fixture_id": "fx-nhl-tbl-col",
        "sport": "ice-hockey",
        "fixture": "Tampa Bay Lightning at Colorado Avalanche",
        "market": "Money line",
        "selection": "Colorado Avalanche win",
        "body": "Colorado host Tampa Bay at Ball Arena, starting 01:00 UTC on Saturday. Three feeds on "
                "the league schedule put Colorado between -125 and -129 and Tampa Bay between +105 and "
                "+106, worth roughly four points of implied probability once the margin is removed. "
                "Nothing else about either club could be read today. The selection is Colorado "
                "Avalanche on the money line.",
        "facts": [
            {"k": "Game details", "v": "Ball Arena, 2026-10-24T01:00Z, game 2026020167", "src": "src-nhl-schedule"},
            {"k": "Quotes", "v": "Colorado -125 to -129, Tampa Bay +105 to +106", "src": "src-nhl-schedule"},
            {"k": "Standings", "v": "Neither club in the portion of the table that loaded", "src": "src-nhl-standings"},
        ],
    },
    {
        "id": "p7",
        "fixture_id": "fx-mlb-ws-g1",
        "sport": "baseball",
        "fixture": "Tampa Bay Rays at Milwaukee Brewers",
        "market": "Game total",
        "selection": "Over 8.5",
        "body": "Two offences and two rotations point at roughly 8.75 combined runs at American Family "
                "Field. Tampa Bay scored 4.54 per game and allowed 4.01; Milwaukee scored 5.14 and "
                "allowed 3.82 across 162 games. Jacob Misiorowski and Nick Martinez are the announced "
                "starters. The 8.5 line therefore sits fractionally below expectation. The selection is "
                "Over 8.5 runs.",
        "facts": [
            {"k": "Tampa Bay rates", "v": "4.54 scored, 4.01 allowed per game", "src": "src-mlb-standings"},
            {"k": "Milwaukee rates", "v": "5.14 scored, 3.82 allowed per game", "src": "src-mlb-records-capture"},
            {"k": "Starters", "v": "Jacob Misiorowski (MIL), Nick Martinez (TB)", "src": "src-mlb-schedule"},
        ],
    },
]

FLAGS = [
    ("F-CF-01", "high", "all sports", "every row with a printed time",
     "OLBG prints no timezone and mixes conventions inside a single capture. A greyhound race whose card "
     "reads 17:12 is shown as Today 12:12, which is US Eastern; United Rugby Championship matches are "
     "shown at 14:45, the same figure the URC prints as local; the World Series is shown at 20:00, which "
     "is Eastern; the Formula 1 race is shown at 16:00, which matches the circuit's local start.",
     "Displayed strings reproduce the page; no conversion is published anywhere in this desk.",
     "src-olbg-hubs"),
    ("F-CF-02", "high", "ice-hockey", "Montreal at Chicago",
     "OLBG shows the game as Today 20:07. The league schedules it for 20:00 Eastern. Every on-the-hour "
     "NHL row on the hub carries the same :07 minute field.",
     "Both strings published side by side. League time used for any ordering.",
     "src-nhl-schedule"),
    ("F-CF-03", "high", "ice-hockey", "both NHL games",
     "The league's own schedule response carries mutually contradictory quotes. Montreal is 2.35 decimal "
     "on three feeds and -170 on three others; Chicago is 1.59 on one set and +138 on the other, so the "
     "two sets disagree about which side is favourite.",
     "Only the three consistent American-quote feeds were used; the contradictory set is excluded and "
     "named on the row.",
     "src-nhl-schedule"),
    ("F-CF-04", "medium", "rugby-union", "three URC fixtures",
     "The URC page names the same clubs two ways: the fixture block reads Hollywoodbets Sharks and "
     "Emirates Lions, the results block reads Sharks and Lions. There is also an OLBG row for Newcastle "
     "Red Bulls that does not match the club name in use elsewhere.",
     "A small alias table maps fixture names to result names; nothing was guessed beyond sponsor prefixes.",
     "src-urc-r4"),
    ("F-CF-05", "high", "ice-hockey", "NHL hub",
     "The hub carries several NHL fixtures under today's heading. The league schedules exactly two games "
     "for 23 October, and only one of them appears among the hub's NHL rows.",
     "Hub rows kept as discovery; only the two league-confirmed games carry a price.",
     "src-nhl-schedule"),
    ("F-CF-06", "medium", "golf", "whole sport",
     "The golf hub returns No tips found, so no fixture, market or selection exists to check. This desk "
     "cannot pretend to cover golf beyond recording the empty hub.",
     "Sport page published with the empty state and the hub link.",
     "src-olbg-hubs"),
    ("F-CF-07", "medium", "rugby-league", "whole sport",
     "The rugby league hub carries 2027 outrights only (State of Origin, Super League, NRL). No match-"
     "level row exists, so there is nothing to originate a match line against.",
     "Outrights listed and priced as indicative; no match rows claimed.",
     "src-olbg-hubs"),
    ("F-CF-08", "high", "darts", "eight European Championship rows",
     "The PDC tournament page returns a consent wall rather than content, so the draw, the session order "
     "and the match distances could not be read. Today's eight first-round ties are unconfirmed.",
     "Listed as discovery, unconfirmed, never priced as anything better than indicative.",
     "src-olbg-hubs"),
    ("F-CF-09", "high", "snooker", "two last-64 ties",
     "The World Snooker Tour match list loaded only as far as the 18-19 October sessions, so today's "
     "Jak Jones and David Gilbert ties are not on the tournament page. Their Round 1 results are: "
     "Donaldson 4-0 Wu Yize, Gilbert 4-1 Sykes.",
     "No snooker fixture is treated as confirmed; the two rows stay discovery-only.",
     "src-wst-nio"),
    ("F-CF-10", "high", "basketball", "fourteen rows",
     "The EuroLeague game centre renders its schedule client-side and returned only a club list. The NBA "
     "scoreboard endpoint returned HTTP 500. Neither league's fixtures for today could be read.",
     "Fourteen rows listed as discovery; none confirmed, none graded above indicative.",
     "src-olbg-hubs"),
    ("F-CF-11", "medium", "tennis", "nine rows",
     "The ATP scores page listed Brussels and Lyon quarter-finals and the WTA scores page a live event; "
     "none of those matches appears in OLBG's nine rows. The rows cannot be matched to an official "
     "order of play.",
     "No tennis fixture confirmed; no tennis price.",
     "src-olbg-hubs"),
    ("F-CF-12", "medium", "cricket", "seven match rows",
     "The Cricket Australia match page returned filter metadata rather than a fixture list. New Zealand "
     "against India, the South African domestic T20s and Pakistan against England are all unconfirmed.",
     "Seven rows listed as discovery; no cricket fixture confirmed.",
     "src-olbg-hubs"),
    ("F-CF-13", "medium", "gaelic-sports", "four match rows",
     "The Munster GAA fixtures page returned navigation only. The two Cork and Galway county finals "
     "carried by OLBG could not be matched to a published fixture list.",
     "Four rows listed as discovery; no Gaelic fixture confirmed.",
     "src-olbg-hubs"),
    ("F-CF-14", "medium", "baseball", "Milwaukee's season record",
     "Today's standings call returned the American League block only, so Milwaukee's 103-59 record and "
     "832/618 run totals come from the repository's own canonical capture of the same endpoint on "
     "22 October, one day earlier.",
     "The row names the capture and its date; the league figure for Tampa Bay was read fresh today.",
     "src-mlb-records-capture"),
    ("F-CF-15", "medium", "ice-hockey", "four clubs",
     "The league standings response loaded the top of the table only (Carolina 18 points, Edmonton and "
     "Boston 16, Vegas 15). None of Montreal, Chicago, Tampa Bay or Colorado appears in the loaded part.",
     "No club record is quoted for any of tonight's four teams.",
     "src-nhl-standings"),
    ("F-CF-16", "high", "all sports", "every prediction",
     "No injury, suspension, availability or team-news feed could be read for any sport this session. "
     "Nothing about player availability appears in any prediction, because nothing was obtainable.",
     "Recorded here so the absence is visible rather than silently patched with a guess.",
     "src-olbg-hubs"),
    ("F-CF-17", "medium", "greyhounds", "fifteen race rows",
     "The greyhound hub prints a race name of 17:12 beside a time of Today 12:12, and no GBGB card was "
     "read, so no runner, trap or grade could be confirmed. Dog names are reproduced as printed.",
     "Rows stay discovery-only. No greyhound price is graded above indicative.",
     "src-olbg-hubs"),
    ("F-CF-18", "high", "all sports", "117 indicative prices",
     "An OLBG tip-vote share is a count of published tips, not a price and not a probability. This desk "
     "converts the share to a probability only after halving it toward a coin flip and capping it, and "
     "labels every such row indicative and Low.",
     "Never graded Medium or High, and never counted in the confirmed-outcome totals.",
     "src-olbg-hubs"),
    ("F-CF-19", "medium", "rugby-union", "Cardiff v Sharks",
     "OLBG prices Cardiff at 14:45 with the Sharks as 4/7 favourites, while the URC fixture list places "
     "the same match at the same time. The match is confirmed; the price direction on the hub is not "
     "something this desk can check against a league source, which publishes no prices.",
     "Fixture confirmed from the URC; the hub's selection direction is quoted, not endorsed.",
     "src-urc-r4"),
    ("F-CF-20", "medium", "handball", "GRK Ohrid v Spor Toto",
     "OLBG lists this as an EHF European Cup tie at 12:30 with a +11.50 handicap on the away side. No "
     "EHF page was read, so neither the competition nor the line could be confirmed.",
     "Row stays discovery-only.",
     "src-olbg-hubs"),
    ("F-CF-21", "high", "all sports", "zero High picks",
     "The brief's High rule needs a win chance above 70% and a price no shorter than -250. Those two "
     "conditions together admit only 70.0% to 71.4%. The strongest confirmed selection today, Edinburgh "
     "at about 85%, prices at -567; the next, Connacht at about 59%, is nowhere near the floor.",
     "Zero High picks published, with the arithmetic shown rather than a quota filled.",
     "src-urc-r4"),
]


def words(text):
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-]*", text))


def main():
    lines = json.loads((DATA / "lines.json").read_text())
    price = {}
    for r in lines["rows"]:
        if r["class"] == "official":
            price[(r["fixture_id"], r["selection"])] = r

    out = []
    for p in PREDICTIONS:
        key = (p["fixture_id"], p["selection"])
        if key not in price:
            raise SystemExit(f"prediction {p['id']} has no originated price: {key}")
        pr = price[key]
        body = " ".join(p["body"].split())
        low = body.lower()
        hits = [w for w in BANNED if re.search(rf"\b{re.escape(w.lower())}\b", low)]
        if hits:
            raise SystemExit(f"prediction {p['id']} contains banned words: {hits}")
        n = words(body)
        if n < 30:
            raise SystemExit(f"prediction {p['id']} is only {n} words")
        out.append({**p, "body": body, "words": n,
                    "p": pr["p"], "decimal": pr["decimal"], "american": pr["american"],
                    "american_text": pr["american_text"], "tier": pr["tier"], "in_band": pr["in_band"]})

    (DATA / "predictions.json").write_text(json.dumps(out, indent=1))

    flags = [{"id": i, "severity": s, "sport": sp, "row": rw, "issue": iss, "action": act, "source": src}
             for i, s, sp, rw, iss, act, src in FLAGS]
    (DATA / "flagged.json").write_text(json.dumps(flags, indent=1))

    print(f"predictions={len(out)} flags={len(flags)} "
          f"words={[x['words'] for x in out]}")
    print("tiers:", {x["id"]: x["tier"] for x in out})


if __name__ == "__main__":
    main()
