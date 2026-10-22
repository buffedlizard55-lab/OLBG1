#!/usr/bin/env python3
"""T66 / 8f6d7364 — high-confidence predictions (hand-written, one per High).

Emits data/8f6d7364/predictions.json. Every factual clause maps to a fact entry
whose `source` is the official page fetched this session; word counts and
uniqueness (no shared 6-gram with another prediction) are re-checked here.
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "8f6d7364")
LINES = json.load(open(os.path.join(D, "lines.json")))
FIX = {f["id"]: f for f in json.load(open(os.path.join(D, "fixtures.json")))["fixtures"]}
GEN = "2026-10-22T22:15:00Z"

NHL_STD = "https://api-web.nhle.com/v1/standings/now"
NHL_SCH = "https://api-web.nhle.com/v1/schedule/2026-10-22"
IRL_FIX = "https://www.intrl.sport/fixtures-results"
IRL_RANK = "https://www.intrl.sport/world-rankings"

P1 = (
    "Back the Minnesota Wild to win this one in Calgary. Minnesota reach the Saddledome with six wins "
    "from their last ten outings (6-2-2, fourteen points in ten games overall), and even their most recent "
    "blemish was only an overtime loss — their current streak reads OT1. The Flames, by contrast, have taken "
    "just four points from eight games (2-6-0) and only two wins in their last eight; their 25% points share "
    "is half of Minnesota's 70%. Calgary did win last time out (streak W1), but one result does not close a "
    "ten-point form gap. Our line makes the Wild 70.23% favourites at a fair -236, which sits inside the "
    "-250 to +10000 window, so the high-confidence selection is MINNESOTA WILD TO WIN THE MATCH (moneyline)."
)
P2 = (
    "Take Australia Women to beat England at HBF Park. Australia top the official IRL women's world rankings "
    "on a maximum 100% rating while England sit third on 40%, and those ratings are recalculated from results "
    "across the current season and the three before it, weighting winning margins, the strength of opposition "
    "and how recently the games were played — so the gap is built from sustained recent match history, not "
    "reputation. It is Round 2 of the Women's Rugby League World Cup in Perth, and our model converts that "
    "official rating gap into 71.43% for Australia, a fair price of exactly -250 at the edge of the brief's "
    "window. The high-confidence call is AUSTRALIA WOMEN TO WIN (match winner)."
)

def wc(t):
    return len(re.findall(r"[A-Za-z0-9'%-]+", t))

def grams(t, n=6):
    w = re.findall(r"[a-z0-9'%-]+", t.lower())
    return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}

assert wc(P1) >= 30 and wc(P2) >= 30
assert not (grams(P1) & grams(P2)), "shared 6-gram between predictions"

PREDS = [
    {
        "id": "P-8F6D-01",
        "fixture_id": "nhl-min-cgy",
        "sport": "ice-hockey",
        "match": "MIN Wild @ CGY Flames",
        "competition": "NHL",
        "kickoff_utc": "2026-10-23T01:00:00Z",
        "selection": "MIN Wild to win the match (moneyline)",
        "tier": "High",
        "model_p": 0.702273,
        "fair_american": -235.9,
        "prose": P1,
        "word_count": wc(P1),
        "facts": [
            {"fact": "Minnesota last-ten record 6-2-2; 10 GP, 14 points; streak OT1", "source": NHL_STD,
             "observed": "2026-10-22T20:56Z/2026-10-22T21:04Z"},
            {"fact": "Calgary record 2-6-0, 8 GP, 4 points (25% point share); last-ten 2-6-0; streak W1", "source": NHL_STD,
             "observed": "2026-10-22T20:56Z/2026-10-22T21:04Z"},
            {"fact": "Fixture: MIN Wild at CGY Flames, start 2026-10-23T01:00:00Z, gameState FUT", "source": NHL_SCH,
             "observed": "2026-10-22T20:53Z/2026-10-22T21:00Z"},
            {"fact": "Official market cross-check (NHL-embedded odds, devig of American providers): CGY ~0.648 vs model 0.702 — divergence disclosed on the Analysis page", "source": NHL_SCH,
             "observed": "2026-10-22T20:53Z/2026-10-22T21:00Z"}
        ],
        "official_links": [NHL_STD, NHL_SCH, "https://www.olbg.com/betting-tips/Ice_Hockey/13"],
        "written_at": GEN
    },
    {
        "id": "P-8F6D-02",
        "fixture_id": "rugby-league-rl-women-3",
        "sport": "rugby-league",
        "match": "Australia W v England W",
        "competition": "IRL Women's Rugby League World Cup, Round 2",
        "kickoff": "2026-10-24 17:05 (venue local; official page states no timezone — flagged F-8F6D-08)",
        "venue": "HBF Park, Perth",
        "selection": "Australia W to win the match (match winner)",
        "tier": "High",
        "model_p": 0.714286,
        "fair_american": -250.0,
        "prose": P2,
        "word_count": wc(P2),
        "facts": [
            {"fact": "Official IRL women's rankings: Australia 1st at 100%, England 3rd at 40%", "source": IRL_RANK,
             "observed": "2026-10-22T21:34Z/2026-10-22T21:35Z and re-read 22:1xZ"},
            {"fact": "Rankings methodology (official): current season plus three preceding seasons with margin, opposition-strength and recency weighting", "source": IRL_RANK,
             "observed": "2026-10-22T21:34Z/2026-10-22T21:35Z"},
            {"fact": "Fixture: Women's RLWC Round 2, Australia v England, Sat 24 Oct 2026, 17:05, HBF Park Perth", "source": IRL_FIX,
             "observed": "2026-10-22T21:09Z/2026-10-22T21:10Z"}
        ],
        "official_links": [IRL_RANK, IRL_FIX, "https://www.olbg.com/betting-tips/Rugby_League/10"],
        "written_at": GEN
    },
]

# cross-check against the model ledger
high = {h["fixture_id"]: h for h in LINES["ledgers"]["high_selections"]}
assert set(high) == {p["fixture_id"] for p in PREDS}, "every High selection needs exactly one prediction"
for p in PREDS:
    h = high[p["fixture_id"]]
    assert abs(h["p"] - p["model_p"]) < 1e-6 and abs(h["fair_american"] - p["fair_american"]) < 0.05

json.dump({"generated_at": GEN, "count": len(PREDS), "predictions": PREDS},
          open(os.path.join(D, "predictions.json"), "w"), indent=1, ensure_ascii=False)
print("predictions:", [(p["id"], p["fixture_id"], p["word_count"]) for p in PREDS])
