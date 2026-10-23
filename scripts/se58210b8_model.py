#!/usr/bin/env python3
"""T5821 line origination: zero-margin prices from official records only.

Two disclosed estimators are averaged before a log5 comparison:

1. binary record win share (overtime and shootout losses count as defeats);
2. Pythagorean expectation on official goals for/against with exponent 2.

No home-ice edge, no missing-rating default and no bookmaker quote is inserted.
Fair decimal is 1/p with no margin, so the American display follows arithmetically.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import se58210b8_data as D

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / D.SESSION.split("-")[0]


def log5(pa: float, pb: float) -> float:
    return (pa - pa * pb) / (pa + pb - 2 * pa * pb)


def american(decimal: float) -> int:
    if decimal >= 2.0:
        return int(round((decimal - 1.0) * 100))
    return -int(round(100.0 / (decimal - 1.0)))


def team_rating(abbr: str) -> float:
    gp, w, l, otl, _pts, gf, ga, _l10, _streak, _home, _road, _conf, _div = D.NHL_TEAMS[abbr]
    record = w / gp
    pyth = (gf ** 2) / (gf ** 2 + ga ** 2)
    return (record + pyth) / 2


def goal_rates(home: str, away: str) -> tuple[float, float]:
    """Expected regulation goals per side from official per-game scoring, no venue edge."""
    _, _, _, _, _, gf_h, ga_h, *_ = D.NHL_TEAMS[home]
    gp_h = D.NHL_TEAMS[home][0]
    gp_a = D.NHL_TEAMS[away][0]
    gf_a, ga_a = D.NHL_TEAMS[away][5], D.NHL_TEAMS[away][6]
    lam_home = ((gf_h / gp_h) + (ga_a / gp_a)) / 2
    lam_away = ((gf_a / gp_a) + (ga_h / gp_h)) / 2
    return lam_home, lam_away


def poisson(lam: float, k: int) -> float:
    return math.exp(-lam) * lam ** k / math.factorial(k)


def goal_matrix(lam_home: float, lam_away: float, cap: int = 13) -> list[list[float]]:
    return [[poisson(lam_home, i) * poisson(lam_away, j) for j in range(cap)] for i in range(cap)]


def price_game(fixture) -> dict:
    fid, date, start, away, home, venue, game_id = fixture
    p_home = log5(team_rating(home), team_rating(away))
    p_away = 1.0 - p_home
    lam_home, lam_away = goal_rates(home, away)
    matrix = goal_matrix(lam_home, lam_away)
    cover_home = sum(matrix[i][j] for i in range(13) for j in range(13) if i - j >= 2)
    over = sum(matrix[i][j] for i in range(13) for j in range(13) if i + j >= 6)

    def side(p: float, label: str) -> dict:
        # Publish a rounded probability and derive every displayed price from that rounded
        # number, so the decimal, the American price and 1/p always reconcile on the page.
        p_pub = round(p, 4)
        dec = round(1.0 / p_pub, 3)
        us = american(dec)
        return {"selection": label, "probability": p_pub, "fair_decimal": dec,
                "american_display": us,
                "fair_price_in_target_band": D.WINDOW_MIN_AMERICAN <= us <= D.WINDOW_MAX_AMERICAN}

    markets = [
        {"market": "Money Line", "key": "winner",
         "note": "Two-way, overtime and shootout included. Rating-based, zero margin.",
         "outcomes": [side(p_home, D.NHL_TEAM_NAME[home]), side(p_away, D.NHL_TEAM_NAME[away])]},
        {"market": "Puck Line -1.5", "key": "handicap",
         "note": "Model line, not a quoted offer. Regulation goal model; a one-goal game that goes "
                 "to overtime cannot cover -1.5.",
         "outcomes": [side(cover_home, D.NHL_TEAM_NAME[home] + " -1.5"),
                      side(1 - cover_home, D.NHL_TEAM_NAME[away] + " +1.5")]},
        {"market": "Match Total 5.5", "key": "total",
         "note": "Model line, not a quoted offer. Regulation goals only: overtime and shootout "
                 "goals are excluded, which biases the under side.",
         "outcomes": [side(over, "Over 5.5 goals"), side(1 - over, "Under 5.5 goals")]},
    ]
    pick_home = p_home >= p_away
    pick_p = p_home if pick_home else p_away
    pick_label = D.NHL_TEAM_NAME[home] if pick_home else D.NHL_TEAM_NAME[away]
    pick_p = round(pick_p, 4)
    dec = round(1.0 / pick_p, 3)
    us = american(dec)
    in_band = D.WINDOW_MIN_AMERICAN <= us <= D.WINDOW_MAX_AMERICAN
    # Confidence comes from the originated probability alone; the price window is reported
    # separately so a strongly evidenced favourite that prices shorter than -250 is disclosed
    # rather than silently dropped or silently promoted into the requested band.
    if pick_p >= 0.70:
        confidence = "high"
    elif pick_p >= 0.60:
        confidence = "medium"
    else:
        confidence = "low"
    band = "in-window (-250 to +10000)" if in_band else "shorter than -250 (outside the window)"
    return {
        "id": fid, "sport": "ice_hockey", "date": date, "start_utc": start,
        "away": D.NHL_TEAM_NAME[away], "home": D.NHL_TEAM_NAME[home], "venue": venue,
        "official_game_id": game_id,
        "source_ids": ["nhl-schedule-1023" if date == "2026-10-23" else "nhl-schedule-1024",
                       "nhl-standings"],
        "inputs": {
            "away": {"abbr": away, "record": f"{D.NHL_TEAMS[away][1]}-{D.NHL_TEAMS[away][2]}-{D.NHL_TEAMS[away][3]}",
                     "goals_for": D.NHL_TEAMS[away][5], "goals_against": D.NHL_TEAMS[away][6],
                     "rating": round(team_rating(away), 4)},
            "home": {"abbr": home, "record": f"{D.NHL_TEAMS[home][1]}-{D.NHL_TEAMS[home][2]}-{D.NHL_TEAMS[home][3]}",
                     "goals_for": D.NHL_TEAMS[home][5], "goals_against": D.NHL_TEAMS[home][6],
                     "rating": round(team_rating(home), 4)},
            "expected_goals": [round(lam_home, 2), round(lam_away, 2)],
        },
        "markets": markets,
        "pick": pick_label, "pick_probability": round(pick_p, 4), "pick_decimal": round(dec, 3),
        "pick_american": us, "pick_in_window": in_band, "band": band,
        "high_and_in_window": confidence == "high" and in_band, "confidence": confidence,
        "withheld": [
            {"market": "Player points / shots props", "status": "unverified",
             "reason": "No official player-availability or usage input was read in this pass."},
            {"market": "Correct score", "status": "unverified",
             "reason": "Published only as a model distribution; no official price input."},
            {"market": "Period betting", "status": "unverified",
             "reason": "No official period-level input was read in this pass."},
        ],
    }


def build() -> dict:
    books = [price_game(f) for f in D.NHL_FIXTURES]
    for fid, date, start, away, home, venue, pk, label in D.MLB_FIXTURES:
        books.append({
            "id": fid, "sport": "baseball", "date": date, "start_utc": start,
            "away": away, "home": home, "venue": venue, "official_game_id": pk, "label": label,
            "source_ids": ["mlb-schedule"] + (["mlb-nl-standings"] if home in D.MLB_RECORDS or away in D.MLB_RECORDS else []),
            "inputs": {"home_record": D.MLB_RECORDS.get(home), "away_record": D.MLB_RECORDS.get(away)},
            "markets": [], "pick": None, "confidence": None, "unpriced": True,
            "unpriced_reason": "Only one side's official regular-season record was read this pass; "
                               "the Tampa Bay Rays' record was not read, and the pricing rule "
                               "requires both measured records.",
            "withheld": [
                {"market": "Money Line", "status": "unverified",
                 "reason": "Both clubs' official season run production was not read."},
                {"market": "Run Line -1.5", "status": "unverified",
                 "reason": "Derived from the same missing input as the money line."},
                {"market": "Match Total", "status": "unverified",
                 "reason": "Derived from the same missing input as the money line."},
            ],
        })
    return {"session": D.SESSION, "task": D.TASK, "harvest_utc": D.HARVEST_UTC,
            "books": books}


if __name__ == "__main__":
    doc = build()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "lines.json").write_text(json.dumps(doc, indent=1), encoding="utf-8")
    high = [b for b in doc["books"] if b.get("confidence") == "high"]
    print("high and in window:", sum(1 for b in high if b.get("high_and_in_window")))
    med = [b for b in doc["books"] if b.get("confidence") == "medium"]
    low = [b for b in doc["books"] if b.get("confidence") == "low"]
    print(f"books={len(doc['books'])} high={len(high)} medium={len(med)} low={len(low)} "
          f"unpriced={sum(1 for b in doc['books'] if b.get('unpriced'))}")
    for b in sorted(high, key=lambda x: -x["pick_probability"]):
        print(f"  HIGH {b['away']} @ {b['home']} {b['date']} pick={b['pick']} "
              f"p={b['pick_probability']} {b['pick_american']:+d}")
    for b in sorted(med, key=lambda x: -x["pick_probability"]):
        print(f"  MED  {b['away']} @ {b['home']} pick={b['pick']} p={b['pick_probability']} {b['pick_american']:+d}")
