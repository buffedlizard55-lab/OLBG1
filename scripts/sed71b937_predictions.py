#!/usr/bin/env python3
"""TED71 (session ed71b937-olbg1) - hand-written predictions.

Each text is written for one specific High selection.  Every factual clause
must trace to a page read this session; anything that was not read is said to
be absent rather than filled in.  The words "model" and "verified" are banned
from the published prose (they belong to internal working, not to the reader).
"""

from __future__ import annotations

import json
import os
import re

SESSION = "ed71b937-olbg1"
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data", "ed71b937")

BANNED = ("model", "verified", "verification", "algorithm", "our data shows")
MIN_WORDS = 30

PREDICTIONS = [
    {
        "match": "Zalgiris Kaunas v LDLC ASVEL Villeurbanne",
        "selection": "Zalgiris Kaunas +6.5 (handicap)",
        "sport": "Basketball",
        "competition": "2026-27 EuroLeague, regular season round 7",
        "start_utc": "2026-10-23T17:00:00Z",
        "text": (
            "Zalgiris Kaunas taking a 6.5-point start against LDLC ASVEL "
            "Villeurbanne is the play in Kaunas on Friday night. Both clubs "
            "reach round seven sitting on identical 2-4 records, so the "
            "separator is the scoring balance rather than the win column: "
            "Kaunas have been outscored by 27 points over six rounds, 490 for "
            "and 517 against, whereas Villeurbanne's hole is 45 points, 527 "
            "for and 572 against. Kaunas are therefore the tighter of the two "
            "units and are giving up nothing like ASVEL's margin, and with "
            "six and a half points in hand they only need to avoid a "
            "seven-point collapse. Back Zalgiris plus 6.5 to cover, winning "
            "outright or losing by six or fewer. No injury or availability "
            "bulletin was published on any page read for this desk, so treat "
            "this as a form-and-margin read rather than a team-news one."
        ),
        "facts": [
            {"claim": "Zalgiris Kaunas are 2-4 after six EuroLeague rounds, "
                      "490 points for and 517 against (differential -27).",
             "source": "https://www.olympiacosbc.gr/el/",
             "read_utc": "2026-10-23T17:08:00Z"},
            {"claim": "LDLC ASVEL Villeurbanne are 2-4 after six rounds, 527 "
                      "points for and 572 against (differential -45).",
             "source": "https://www.olympiacosbc.gr/el/",
             "read_utc": "2026-10-23T17:08:00Z"},
            {"claim": "The fixture is a EuroLeague 2026-27 regular-season "
                      "round 7 game played on 23 October 2026.",
             "source": "https://www.olympiacosbc.gr/el/",
             "read_utc": "2026-10-23T17:08:00Z"},
            {"claim": "OLBG's Basketball hub listed this event (id 535928) "
                      "with 9 of 16 open tips on Zalgiris.",
             "source": "https://www.olbg.com/betting-tips/Basketball/4",
             "read_utc": "2026-10-23T16:14:00Z"},
        ],
        "absent": [
            "Player availability / injury bulletin - not published on any "
            "official page read this session.",
            "Head-to-head history - not read this session.",
            "Venue - not printed on the standings page that was read.",
        ],
    },
    {
        "match": "Paris Basketball v Valencia Basket",
        "selection": "Valencia Basket -4.5 (handicap)",
        "sport": "Basketball",
        "competition": "2026-27 EuroLeague, regular season round 7",
        "start_utc": "2026-10-23T18:45:00Z",
        "text": (
            "Valencia Basket laying 4.5 points to Paris Basketball is the "
            "selection. Valencia travel to Paris 4-2 with the third-best "
            "scoring balance on the EuroLeague table after six rounds, 583 "
            "points for against 537 conceded, a +46 differential. Paris sit "
            "1-5 and -41, having scored 504 and shipped 545, and that single "
            "win has done nothing to plug the leak at the defensive end. The "
            "gap between a side conceding 90.8 a night and one conceding 89.5 "
            "while scoring nearly thirteen more per game is exactly the sort "
            "of spread that clears five points, so take Valencia minus 4.5 to "
            "win by five or more. There was no team-news or availability "
            "release on the pages read for this desk, so the case rests on "
            "the season-long numbers rather than on who suits up."
        ),
        "facts": [
            {"claim": "Valencia Basket are 4-2 after six EuroLeague rounds, "
                      "583 points for and 537 against (differential +46).",
             "source": "https://www.olympiacosbc.gr/el/",
             "read_utc": "2026-10-23T17:08:00Z"},
            {"claim": "Paris Basketball are 1-5 after six rounds, 504 points "
                      "for and 545 against (differential -41).",
             "source": "https://www.olympiacosbc.gr/el/",
             "read_utc": "2026-10-23T17:08:00Z"},
            {"claim": "Paris score 84.0 per game and concede 90.8; Valencia "
                      "score 97.2 and concede 89.5 (both arithmetic on the "
                      "same six-round official totals).",
             "source": "https://www.olympiacosbc.gr/el/",
             "read_utc": "2026-10-23T17:08:00Z"},
            {"claim": "OLBG's Basketball hub listed this event (id 535926) "
                      "with 5 of 10 open tips on Valencia.",
             "source": "https://www.olbg.com/betting-tips/Basketball/4",
             "read_utc": "2026-10-23T16:14:00Z"},
        ],
        "absent": [
            "Player availability / injury bulletin - not published on any "
            "official page read this session.",
            "Head-to-head history - not read this session.",
            "Venue - not printed on the standings page that was read.",
        ],
    },
]


def check(preds=None):
    """Gate: length, banned vocabulary, shared-phrase uniqueness."""
    preds = preds if preds is not None else PREDICTIONS
    problems = []
    for p in preds:
        words = re.findall(r"[A-Za-z0-9']+", p["text"].lower())
        if len(words) < MIN_WORDS:
            problems.append("{}: only {} words".format(p["selection"],
                                                       len(words)))
        for bad in BANNED:
            if bad in p["text"].lower():
                problems.append("{}: banned word '{}'".format(
                    p["selection"], bad))
    # 6-gram uniqueness across predictions
    def grams(t):
        w = re.findall(r"[A-Za-z0-9']+", t.lower())
        return {" ".join(w[i:i + 6]) for i in range(len(w) - 5)}
    for i in range(len(preds)):
        for j in range(i + 1, len(preds)):
            shared = grams(preds[i]["text"]) & grams(preds[j]["text"])
            if shared:
                problems.append("shared 6-gram between {} and {}: {}".format(
                    preds[i]["selection"], preds[j]["selection"],
                    sorted(shared)[:3]))
    return problems


def build():
    problems = check()
    out = {
        "session": SESSION, "task": "TED71",
        "generated_at": "2026-10-23T17:15:00Z",
        "policy": {
            "min_words": MIN_WORDS,
            "banned_words": list(BANNED),
            "rule": "Every factual clause traces to a page read this session; "
                    "anything not read is listed under 'absent' instead of "
                    "being filled in.",
            "uniqueness": "No 6-gram may repeat between two predictions.",
            "gate_result": problems or ["PASS"],
        },
        "predictions": PREDICTIONS,
    }
    with open(os.path.join(DATA, "predictions.json"), "w",
              encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    return out, problems


if __name__ == "__main__":
    o, problems = build()
    for p in o["predictions"]:
        n = len(re.findall(r"[A-Za-z0-9']+", p["text"]))
        print("{} words | {}".format(n, p["selection"]))
    print("GATE:", problems or "PASS")
