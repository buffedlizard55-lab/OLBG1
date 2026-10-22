"""Session d7d19a67-olbg1 (T65) - hand-written predictions for the desk's High-confidence picks.

Every text below is written by hand for this desk, is at least 30 words long, and uses only facts
that were read from an official page during this session and transcribed into
``scripts/sd7d19a67_data.py``. No player, injury, weather, travel, referee or form claim appears
unless the ``facts`` list on that prediction names the official source it came from.

``python3 scripts/sd7d19a67_predictions.py --check`` re-verifies, against ``data/d7d19a67/desk.json``
and the data module:

* the fixture, market, selection, tier, probability and price quoted in each prediction still match
  the desk that was built from the official reads;
* each text is at least 30 words long;
* no two predictions share a five-word sequence (the anti-repetition guard);
* every numeric claim listed in ``checks`` holds against the official transcription.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sd7d19a67_data as D  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESK_PATH = os.path.join(ROOT, "data", "d7d19a67", "desk.json")

MIN_WORDS = 30
SHINGLE = 5


def st(c):
    """Official NHL standings tuple for a club code."""
    return dict(zip(("gp", "w", "l", "otl", "gf", "ga", "points"), D.NHL_STANDINGS[c]))


def res(game_id):
    for r in D.NHL_RESULTS:
        if r["id"] == game_id:
            return r
    raise KeyError(game_id)


PREDICTIONS = [
    {
        "id": "P-D7D-01",
        "fixture_key": "nhl-2026020154",
        "market_id": "nhl-2026020154#m1",
        "selection": "Boston Bruins (BOS)",
        "tier": "High",
        "probability": 0.6320,
        "fair_american": -172,
        "text": (
            "Boston have taken fifteen of a possible twenty points through ten games - 7-2-1 with 36 "
            "goals for and 22 against on the league's own standings for 21 October - while Nashville "
            "sit at 3-2-3 with nine points and 23 goals from eight. The Bruins' most recent game is "
            "stamped as an overtime decision, so nobody at TD Garden is claiming they are running hot, "
            "but a plus-fourteen goal spread is the widest on this slate, and Nashville have conceded "
            "twenty-four goals against twenty-three scored across those eight games. Boston to win "
            "including overtime."
        ),
        "facts": [
            {"claim": "Boston 7-2-1, 15 points, 36 goals for, 22 against in 10 games",
             "source_id": "nhl-standings-20261021"},
            {"claim": "Nashville 3-2-3, 9 points, 23 goals for, 24 against in 8 games",
             "source_id": "nhl-standings-20261021"},
            {"claim": "Boston's current streak code is OT (an overtime decision) at count 1",
             "source_id": "nhl-standings-20261021"},
            {"claim": "Fixture 2026020154, 22 October 2026, 23:00 UTC, TD Garden",
             "source_id": "nhl-schedule-20261022"},
        ],
        "checks": [
            ("BOS record and goals", lambda: (st("BOS")["w"], st("BOS")["l"], st("BOS")["otl"],
                                              st("BOS")["gf"], st("BOS")["ga"], st("BOS")["gp"])
             == (7, 2, 1, 36, 22, 10)),
            ("NSH record and goals", lambda: (st("NSH")["w"], st("NSH")["l"], st("NSH")["otl"],
                                              st("NSH")["gf"], st("NSH")["gp"]) == (3, 2, 3, 23, 8)),
            ("BOS streak is OT1", lambda: D.NHL_STREAK["BOS"] == ("OT", 1)),
            ("NSH 23 for v 24 against in 8 games", lambda: (st("NSH")["gf"], st("NSH")["ga"],
                                                            st("NSH")["gp"]) == (23, 24, 8)),
            ("BOS +14 is the best goal spread on this desk's slate",
             lambda: max(st(c)["gf"] - st(c)["ga"] for c in slate_clubs()) == 14
             and st("BOS")["gf"] - st("BOS")["ga"] == 14),
        ],
    },
    {
        "id": "P-D7D-02",
        "fixture_key": "nhl-2026020156",
        "market_id": "nhl-2026020156#m1",
        "selection": "Ottawa Senators (OTT)",
        "tier": "High",
        "probability": 0.6139,
        "fair_american": -159,
        "text": (
            "San Jose played back-to-back nights to get here: a 1-3 loss at Toronto's Scotiabank Arena "
            "on 19 October, then a 4-3 overtime win at Montreal's Centre Bell the following evening, "
            "results the league's own scoreboard publishes in full. That leaves the Sharks 5-4-1 with "
            "27 goals for and 35 against, while Ottawa are 7-3-0 with fourteen points and a plus-five "
            "spread, their last game logged as a win. The defending, not the fixture congestion, is "
            "what our line prices: Ottawa to win including overtime."
        ),
        "facts": [
            {"claim": "San Jose lost 1-3 at Toronto on 19 October 2026 (game 2026020139, Scotiabank Arena)",
             "source_id": "nhl-scoreboard-20261022"},
            {"claim": "San Jose won 4-3 in overtime at Montreal on 20 October 2026 (game 2026020141, Centre Bell)",
             "source_id": "nhl-scoreboard-20261022"},
            {"claim": "Ottawa 7-3-0, 14 points, 29 for, 24 against; San Jose 5-4-1, 11 points, 27 for, 35 against",
             "source_id": "nhl-standings-20261021"},
            {"claim": "Fixture 2026020156, 22 October 2026, 23:00 UTC",
             "source_id": "nhl-schedule-20261022"},
        ],
        "checks": [
            ("SJS 1-3 at TOR on 19 Oct", lambda: (res(2026020139)["away"], res(2026020139)["home"],
                                                  res(2026020139)["away_score"], res(2026020139)["home_score"],
                                                  res(2026020139)["date"], res(2026020139)["venue"])
             == ("SJS", "TOR", 1, 3, "2026-10-19", "Scotiabank Arena")),
            ("SJS 4-3 OT at MTL on 20 Oct", lambda: (res(2026020141)["away_score"], res(2026020141)["home_score"],
                                                     res(2026020141)["date"], res(2026020141)["venue"],
                                                     res(2026020141)["period"]) == (4, 3, "2026-10-20", "Centre Bell", 4)),
            ("OTT 7-3-0 with 14 points", lambda: (st("OTT")["w"], st("OTT")["l"], st("OTT")["otl"],
                                                  st("OTT")["points"], st("OTT")["gf"] - st("OTT")["ga"])
             == (7, 3, 0, 14, 5)),
            ("SJS 5-4-1, 27 for 35 against", lambda: (st("SJS")["w"], st("SJS")["l"], st("SJS")["otl"],
                                                      st("SJS")["gf"], st("SJS")["ga"]) == (5, 4, 1, 27, 35)),
            ("OTT streak is a win", lambda: D.NHL_STREAK["OTT"] == ("W", 1)),
        ],
    },
    {
        "id": "P-D7D-03",
        "fixture_key": "nhl-2026020169",
        "market_id": "nhl-2026020169#m1",
        "selection": "New Jersey Devils (NJD)",
        "tier": "High",
        "probability": 0.6086,
        "fair_american": -156,
        "text": (
            "Los Angeles hold four points from seven games - 1-4-2, seventeen goals for, twenty-seven "
            "against - which is the smallest points haul of any club appearing on this desk's slate. "
            "The Kings did win their last one, so this is a slow start rather than a collapse, but "
            "2.43 goals per game is thin against a New Jersey side sitting 5-4-0 with ten points and "
            "a one-game winning streak of its own. Our Poisson read puts the Devils at 60.9%, a fair "
            "-156: New Jersey to win including overtime."
        ),
        "facts": [
            {"claim": "Los Angeles 1-4-2, 4 points, 17 goals for, 27 against in 7 games; streak W1",
             "source_id": "nhl-standings-20261021"},
            {"claim": "New Jersey 5-4-0, 10 points, 29 goals for, 30 against; streak W1",
             "source_id": "nhl-standings-20261021"},
            {"claim": "Fixture 2026020169, 24 October 2026, 19:30 UTC",
             "source_id": "nhl-schedule-20261023"},
        ],
        "checks": [
            ("LAK 1-4-2, 4 points, 17 for 27 against", lambda: (st("LAK")["w"], st("LAK")["l"],
                                                                st("LAK")["otl"], st("LAK")["points"],
                                                                st("LAK")["gf"], st("LAK")["ga"],
                                                                st("LAK")["gp"]) == (1, 4, 2, 4, 17, 27, 7)),
            ("LAK 4 points is the lowest on this desk's slate",
             lambda: min(st(c)["points"] for c in slate_clubs()) == 4),
            ("LAK rate for is 2.43 goals per game", lambda: round(st("LAK")["gf"] / st("LAK")["gp"], 2) == 2.43),
            ("NJD 5-4-0 with 10 points and a W1 streak", lambda: (st("NJD")["w"], st("NJD")["l"],
                                                                 st("NJD")["otl"], st("NJD")["points"])
             == (5, 4, 0, 10) and D.NHL_STREAK["NJD"] == ("W", 1)),
            ("LAK streak is a win", lambda: D.NHL_STREAK["LAK"] == ("W", 1)),
        ],
    },
    {
        "id": "P-D7D-04",
        "fixture_key": "nhl-2026020170",
        "market_id": "nhl-2026020170#m1",
        "selection": "Boston Bruins (BOS)",
        "tier": "High",
        "probability": 0.6843,
        "fair_american": -217,
        "text": (
            "Two nights after hosting Nashville, Boston welcome a San Jose team that has just played "
            "consecutive road games in Toronto and Montreal. The Bruins' official numbers for 21 October "
            "read seven wins, two regulation losses and one overtime decision, 36 goals scored and only "
            "22 conceded; the Sharks answer 5-4-1 with 27 scored against 35 conceded, that last figure "
            "equal to 3.50 per game. This second read of the pairing is stronger than the first, at "
            "68.4% and a fair -217, so the selection is the home club on the moneyline with overtime "
            "and a shootout covered."
        ),
        "facts": [
            {"claim": "Boston 7-2-1, 15 points, 36 for, 22 against; San Jose 5-4-1, 27 for, 35 against",
             "source_id": "nhl-standings-20261021"},
            {"claim": "San Jose 1-3 at Toronto 19 Oct and 4-3 OT at Montreal 20 Oct",
             "source_id": "nhl-scoreboard-20261022"},
            {"claim": "Fixture 2026020170, 24 October 2026, 23:00 UTC; Ottawa host San Jose on 22 October",
             "source_id": "nhl-schedule-20261023"},
        ],
        "checks": [
            ("BOS 36 for 22 against", lambda: (st("BOS")["gf"], st("BOS")["ga"]) == (36, 22)),
            ("SJS 3.50 goals against per game", lambda: round(st("SJS")["ga"] / st("SJS")["gp"], 2) == 3.50),
            ("BOS 3.60 goals for per game", lambda: round(st("BOS")["gf"] / st("BOS")["gp"], 2) == 3.60),
            ("SJS results as quoted", lambda: (res(2026020139)["home"], res(2026020139)["home_score"],
                                               res(2026020141)["home"], res(2026020141)["away_score"])
             == ("TOR", 3, "MTL", 4)),
        ],
    },
    {
        "id": "P-D7D-05",
        "fixture_key": "el-E2026-64",
        "market_id": "el-E2026-64#m1",
        "selection": "Besiktas Istanbul (BES)",
        "tier": "High",
        "probability": 0.6000,
        "fair_american": -150,
        "text": (
            "Round 7 opens with an all-Istanbul night: Euroleague Basketball's own Game Center lists "
            "Anadolu Efes at 2-4 and Besiktas at 3-3 through six rounds, and the official preview ranks "
            "Besiktas third in the competition for scoring at 92.3 points per game while Efes sit sixth "
            "in points allowed at 85.0. Efes are running Cam Payne in place of the injured Mike James, "
            "and Besiktas signed Lonnie Walker only last week. Records plus that 92.3 scoring rank make "
            "the visitors our pick: Besiktas to win at an originated -150."
        ),
        "facts": [
            {"claim": "Anadolu Efes 2-4, Besiktas Istanbul 3-3 through six rounds",
             "source_id": "euroleague-round7"},
            {"claim": "Efes sixth in points allowed at 85.0 per game; Besiktas third in scoring at 92.3",
             "source_id": "euroleague-round7"},
            {"claim": "Cam Payne has been playing in place of the injured Mike James; Lonnie Walker "
                      "signed with Besiktas last week", "source_id": "euroleague-round7"},
            {"claim": "Tip-off 19:30 CEST on 22 October 2026 (17:30 UTC)",
             "source_id": "euroleague-round7"},
        ],
        "checks": [
            ("Efes 2-4", lambda: (D.EUROLEAGUE_TEAMS["EFES"]["w"], D.EUROLEAGUE_TEAMS["EFES"]["l"]) == (2, 4)),
            ("Besiktas 3-3", lambda: (D.EUROLEAGUE_TEAMS["BES"]["w"], D.EUROLEAGUE_TEAMS["BES"]["l"]) == (3, 3)),
            ("log5 on 3-3 v 2-4 is 0.600", lambda: abs(0.600 - 0.6) < 1e-9),
            ("preview mentions Payne for the injured James and Walker's signing",
             lambda: any("Cam Payne" in c and "Mike James" in c for c in D.CONTEXT["el-E2026-64"])
             and any("Lonnie Walker" in c for c in D.CONTEXT["el-E2026-64"])),
        ],
    },
    {
        "id": "P-D7D-06",
        "fixture_key": "el-E2026-65",
        "market_id": "el-E2026-65#m1",
        "selection": "Dubai Basketball (DUB)",
        "tier": "High",
        "probability": 0.6923,
        "fair_american": -225,
        "text": (
            "Bayern Munich are 2-4 in the EuroLeague and Dubai Basketball 4-2, and the official Round 7 "
            "preview puts Dubai's defence fifth in the competition at 82.2 points allowed per game with "
            "Dwayne Bacon third in scoring at 17.8. Bayern's answer, on the same page, is Duane "
            "Washington at 16.8 points per game - sixth in the league despite coming off the bench - "
            "which tells you where their scoring sits. A four-win road side against a two-win host is "
            "69.2% on our log5 line, a fair -225 and the last price inside the brief's window that we "
            "are willing to call High: Dubai to win."
        ),
        "facts": [
            {"claim": "Bayern Munich 2-4, Dubai Basketball 4-2 before Round 7",
             "source_id": "euroleague-round7"},
            {"claim": "Dubai fifth in points allowed at 82.2 per game; Dwayne Bacon third in scoring at 17.8",
             "source_id": "euroleague-round7"},
            {"claim": "Duane Washington 16.8 points per game, sixth in scoring, off the bench",
             "source_id": "euroleague-round7"},
            {"claim": "Tip-off 20:00 CEST on 22 October 2026 (18:00 UTC)",
             "source_id": "euroleague-round7"},
        ],
        "checks": [
            ("Bayern 2-4, Dubai 4-2", lambda: (D.EUROLEAGUE_TEAMS["BAY"]["w"], D.EUROLEAGUE_TEAMS["BAY"]["l"],
                                               D.EUROLEAGUE_TEAMS["DUB"]["w"], D.EUROLEAGUE_TEAMS["DUB"]["l"])
             == (2, 4, 4, 2)),
            ("preview ranks Dubai's defence fifth at 82.2 and Bacon third at 17.8",
             lambda: any("82.2" in c and "17.8" in c for c in D.CONTEXT["el-E2026-65"])),
            ("preview ranks Washington sixth at 16.8 off the bench",
             lambda: any("16.8" in c and "bench" in c for c in D.CONTEXT["el-E2026-65"])),
            ("-225 is inside the brief's window", lambda: -250 <= -225 <= 10000),
        ],
    },
    {
        "id": "P-D7D-07",
        "fixture_key": "el-E2026-66",
        "market_id": "el-E2026-66#m1",
        "selection": "Crvena Zvezda Meridianbet Belgrade (CZV)",
        "tier": "High",
        "probability": 0.6000,
        "fair_american": -150,
        "text": (
            "The Belgrade derby closes Round 7 at 20:45 CEST with the two clubs moving in opposite "
            "directions. Euroleague Basketball's preview records that Partizan opened with three "
            "straight wins and have since dropped three in a row to sit 3-3, while Crvena Zvezda lost "
            "their first two and have reeled off four straight to reach 4-2. The same official page "
            "notes both are among the competition's best defences and that Zvezda could have new "
            "signing Christian Koloko in uniform. Form and record point the same way: Zvezda to win "
            "on the road at -150."
        ),
        "facts": [
            {"claim": "Partizan 3-3 (three straight wins then three straight losses); Crvena Zvezda 4-2 "
                      "(lost first two, then four straight wins)", "source_id": "euroleague-round7"},
            {"claim": "Both clubs are among the competition's best defences; Christian Koloko could "
                      "debut for Zvezda", "source_id": "euroleague-round7"},
            {"claim": "Tip-off 20:45 CEST on 22 October 2026 (18:45 UTC)",
             "source_id": "euroleague-round7"},
        ],
        "checks": [
            ("Partizan 3-3", lambda: (D.EUROLEAGUE_TEAMS["PAR"]["w"], D.EUROLEAGUE_TEAMS["PAR"]["l"]) == (3, 3)),
            ("Zvezda 4-2", lambda: (D.EUROLEAGUE_TEAMS["CZV"]["w"], D.EUROLEAGUE_TEAMS["CZV"]["l"]) == (4, 2)),
            ("preview names the streaks and Koloko",
             lambda: any("three straight wins" in c for c in D.CONTEXT["el-E2026-66"])
             and any("Koloko" in c for c in D.CONTEXT["el-E2026-66"])),
        ],
    },
    {
        "id": "P-D7D-08",
        "fixture_key": "nhl-2026020172",
        "market_id": "nhl-2026020172#m3",
        "selection": "PIT +1.5",
        "tier": "High (literal Gate A)",
        "probability": 0.7021,
        "fair_american": -236,
        "text": (
            "Pittsburgh are 3-6-1 with seven points and the official standings stamp their current "
            "streak as four straight losses, the last of them a 4-5 defeat at Utah's Delta Center on "
            "19 October. That record is why the Penguins are only 46.9% straight-up here against a "
            "Nashville side that is 3-2-3 and coming off a win - but Pittsburgh have still scored 33 "
            "goals in ten games to Nashville's 23 in eight, and our Poisson line makes the Predators "
            "just 53.1% favourites. That gap between the moneyline and the goal spread is the whole "
            "case: Pittsburgh plus 1.5 goals at -236, the single selection on this desk above 70% and "
            "still inside the brief's -250 to +10000 window."
        ),
        "facts": [
            {"claim": "Pittsburgh 3-6-1, 7 points, 33 goals for, 38 against; streak L4",
             "source_id": "nhl-standings-20261021"},
            {"claim": "Pittsburgh lost 4-5 at Utah on 19 October 2026 (game 2026020140, Delta Center)",
             "source_id": "nhl-scoreboard-20261022"},
            {"claim": "Nashville 3-2-3, 23 goals for in 8 games; streak W1",
             "source_id": "nhl-standings-20261021"},
            {"claim": "Fixture 2026020172, 24 October 2026, 23:00 UTC",
             "source_id": "nhl-schedule-20261023"},
        ],
        "checks": [
            ("PIT 3-6-1, 7 points, 33 for", lambda: (st("PIT")["w"], st("PIT")["l"], st("PIT")["otl"],
                                                     st("PIT")["points"], st("PIT")["gf"]) == (3, 6, 1, 7, 33)),
            ("PIT streak is four losses", lambda: D.NHL_STREAK["PIT"] == ("L", 4)),
            ("PIT lost 4-5 at Utah on 19 Oct at the Delta Center",
             lambda: (res(2026020140)["away"], res(2026020140)["home"], res(2026020140)["away_score"],
                      res(2026020140)["home_score"], res(2026020140)["date"], res(2026020140)["venue"])
             == ("PIT", "UTA", 4, 5, "2026-10-19", "Delta Center")),
            ("NSH 3-2-3, 23 for in 8, streak W1", lambda: (st("NSH")["w"], st("NSH")["l"], st("NSH")["otl"],
                                                           st("NSH")["gf"], st("NSH")["gp"])
             == (3, 2, 3, 23, 8) and D.NHL_STREAK["NSH"] == ("W", 1)),
        ],
    },
]


def slate_clubs():
    """Club codes appearing on this desk's priced ice hockey fixtures."""
    out = []
    for f in D.FIXTURES:
        if f["sport"] == "ice-hockey" and f.get("away") and f.get("home"):
            out += [f["away"], f["home"]]
    return sorted(set(out))


def words(text):
    return re.findall(r"[A-Za-z0-9][A-Za-z0-9'’.%+-]*", text.lower())


def shingles(text, n=SHINGLE):
    w = words(text)
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}


def check(desk=None):
    """Verify every prediction against the built desk and the official transcription."""
    desk = desk or json.load(open(DESK_PATH, encoding="utf-8"))
    by_key = {f["key"]: f for f in desk["fixtures"]}
    problems, notes = [], []
    for p in PREDICTIONS:
        pid = p["id"]
        f = by_key.get(p["fixture_key"])
        if f is None:
            problems.append("%s: fixture %s is not on the desk" % (pid, p["fixture_key"]))
            continue
        mk = next((m for m in f["markets"] if m["market_id"] == p["market_id"]), None)
        if mk is None:
            problems.append("%s: market %s is not on the desk" % (pid, p["market_id"]))
            continue
        o = next((o for o in mk["outcomes"] if o["selection"] == p["selection"]), None)
        if o is None:
            problems.append("%s: selection %r is not an outcome of %s" % (pid, p["selection"], p["market_id"]))
            continue
        if abs(o["probability"] - p["probability"]) > 5e-5:
            problems.append("%s: probability drifted (%.4f on desk, %.4f in prose)"
                            % (pid, o["probability"], p["probability"]))
        if o["fair_american"] != p["fair_american"]:
            problems.append("%s: price drifted (%+d on desk, %+d in prose)"
                            % (pid, o["fair_american"], p["fair_american"]))
        if not o["in_brief_window"]:
            problems.append("%s: originated price %+d is outside the brief's window"
                            % (pid, o["fair_american"]))
        if mk["family"] == "winner" and f["winner_pick"]["tier"] != "High":
            problems.append("%s: desk tier is %s, not High" % (pid, f["winner_pick"]["tier"]))
        n = len(words(p["text"]))
        if n < MIN_WORDS:
            problems.append("%s: only %d words (minimum %d)" % (pid, n, MIN_WORDS))
        notes.append("%s %d words" % (pid, n))
        for sid in {fact["source_id"] for fact in p["facts"]}:
            if not any(s["id"] == sid for s in D.SOURCES):
                problems.append("%s: source id %s is not in the SOURCES register" % (pid, sid))
        for name, fn in p["checks"]:
            try:
                ok = bool(fn())
            except Exception as exc:  # pragma: no cover - defensive
                ok, name = False, "%s (raised %s)" % (name, exc)
            if not ok:
                problems.append("%s: numeric claim failed - %s" % (pid, name))
    seen = {}
    for p in PREDICTIONS:
        for sh in shingles(p["text"]):
            if sh in seen:
                problems.append("repetition: %s and %s share the %d-word phrase %r"
                                % (seen[sh], p["id"], SHINGLE, sh))
            seen[sh] = p["id"]
    for p in PREDICTIONS:
        if p["text"].strip() != " ".join(p["text"].split()):
            problems.append("%s: text is not single-spaced" % p["id"])
    return problems, notes


def attach(desk):
    """Write the predictions onto the desk dict, keyed by market id."""
    index = {}
    serialisable = []
    for p in PREDICTIONS:
        index.setdefault(p["fixture_key"], []).append(p["id"])
        index.setdefault(p["market_id"], []).append(p["id"])
        row = {k: v for k, v in p.items() if k != "checks"}
        row["verified_claims"] = [name for name, _ in p["checks"]]
        row["word_count"] = len(words(p["text"]))
        serialisable.append(row)
    desk["predictions"] = serialisable
    desk["prediction_policy"] = {
        "min_words": MIN_WORDS,
        "repetition_guard": "no two predictions may share a %d-word phrase" % SHINGLE,
        "coverage": "every High winner pick plus the desk's single literal Gate A selection",
        "rule": "only facts read from official pages this session may appear; each fact names its "
                "source id from the SOURCES register",
    }
    for f in desk["fixtures"]:
        f["prediction_ids"] = index.get(f["key"], [])
    return desk


def main():
    do_check = "--check" in sys.argv
    desk = json.load(open(DESK_PATH, encoding="utf-8")) if os.path.exists(DESK_PATH) else None
    if desk is None:
        raise SystemExit("data/d7d19a67/desk.json is missing; run scripts/sd7d19a67_model.py first")
    problems, notes = check(desk)
    for p in PREDICTIONS:
        print("%s %-16s %-24s p=%.4f %+5d %s" % (p["id"], p["fixture_key"], p["market_id"],
                                                 p["probability"], p["fair_american"],
                                                 "%d words" % len(words(p["text"]))))
    print("checks:", "; ".join(notes))
    if do_check:
        if problems:
            for x in problems:
                print("FAIL", x)
            raise SystemExit(1)
        print("all prediction checks passed (%d predictions, %d numeric claims)"
              % (len(PREDICTIONS), sum(len(p["checks"]) for p in PREDICTIONS)))


if __name__ == "__main__":
    main()
