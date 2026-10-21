#!/usr/bin/env python3
"""
ccb6bde2_expand_markets.py — v2.1 recalibration + expanded-market origination.

RECALIBRATION (v2.0 -> v2.1), each change documented and reversible:
R1  Small-sample shrinkage. Record-based ratings (win% / points% / early-season
    standings) are shrunk toward the neutral 50 with an empirical-Bayes style
    factor n/(n+k), k=10 pseudo-games, where n is games played parsed from the
    sourced input string (e.g. "4-2 (.667)" -> n=6). A 4-2 vs 2-4 EuroLeague
    gap of 33.4 rating points from six games becomes 12.5. Ranking-based
    ratings (ATP/WTA/WST/PDC seed/ICC/IRL) aggregate long histories and are
    NOT shrunk. Prior-season 82-game NBA records barely move (n=82).
R2  Baseball venue double-count removed. v2.0 fed MLB home-record vs
    road-record splits into the rating gap AND added the 0.540 home logit,
    counting home advantage twice. v2.1 uses a neutral 0.500 venue term for
    fixtures whose inputs are labelled home/road splits.
R3  Tennis ratings re-verified against the official ATP list of 2026-10-19
    (fetched this session from atptour.com): Tommy Paul No.15 and B. Bonzi
    No.100 backfilled for ten-902102 (previously unrated, priced at the raw
    baseline); S. Tsitsipas No.39 verified for ten-902083 but his opponent
    Kukushkin is outside the ATP top 190 (verified by reading the full
    official 1-190 list), so per the repo's no-one-sided-ratings rule the
    match stays baseline-priced and capped low. Fixture ranking labels that
    disagree with the official 2026-10-19 list (Darderi 22->23, Rublev 24->22,
    Mannarino 67->79, Duckworth 71->73) are repriced from the official list
    and flagged. WTA ranks for ten-902039/ten-902074 could not be verified
    (the WTA rankings table is script-rendered and returned no rows), so they
    remain blank and flagged, per the brief.
Slopes are NOT changed: the audit (data/model_calibration-ccb6bde2.json) shows
the ranking curves produce plausible favourite prices, and refitting a slope
would require outcome data this repo does not hold.

Outputs:
  data/market_expansion-ccb6bde2.json  — per-match v2.1 prices + expanded books
  data/market_taxonomy-ccb6bde2.json   — market investigation register
  data/model_calibration-ccb6bde2.json — updated with v2.1 change log

Originals (data/lines.json etc.) are never modified.
"""
from __future__ import annotations

import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import model as M
import ccb6bde2_market_engine as E

SHRINK_K = 10  # pseudo-games of .500 prior (documented assumption R1)

# Ratings that are a direct win%/points% transform (rating == pct*100):
PURE_PCT_HINTS = ("Points percentage", "NBA record", "EuroLeague 2026-27",
                  "home record", "road record")
# Ratings already mapped through a compressed 0-100 ladder/standings scale by
# the harvesting session (they embed margin information, so each game carries
# roughly twice the information of a bare W/L — documented assumption):
COMPOSITE_HINTS = ("standing", "ladder", "standings")

# Official ATP rankings verified this session (atptour.com, list of 2026-10-19)
ATP_VERIFIED_2026_10_19 = {
    "Tommy Paul": 15, "Benjamin Bonzi": 100, "Stefanos Tsitsipas": 39,
    "Andrey Rublev": 22, "Luciano Darderi": 23, "James Duckworth": 73,
    "Adrian Mannarino": 79,
}
ATP_RANKINGS_URL = ("https://www.atptour.com/en/rankings/singles"
                    "?rankDate=2026-10-19&rankRange=0-100")


def games_played(value: str, label: str = "") -> int | None:
    """Parse games played from a sourced record string, avoiding match scores.

    Accepts W-L(-D) records only in record-like positions: at string start
    ('55-26 at home'), before a parenthetical ('4-2 (.667)'), or inside
    parentheses ('(4-3-2, +2 GD)', '(10-0)'). Bare scorelines embedded in
    prose ('beat Bayonne 45-34') are deliberately not matched. Falls back to
    a '(J6)'-style matchday tag in the label (Top 14 after round 6).
    """
    v = value or ""
    patterns = [
        r"^(\d+)-(\d+)(?:-(\d+))?\b",
        r"\b(\d+)-(\d+)(?:-(\d+))?\s*\(",
        r"\((\d+)-(\d+)(?:-(\d+))?[,\)]",
    ]
    for pat in patterns:
        m = re.search(pat, v)
        if m:
            n = sum(int(x) for x in m.groups() if x)
            if 0 < n <= 95:
                return n
    m = re.search(r"\(J(\d+)\)", label or "")
    return int(m.group(1)) if m else None


def shrink(rating: float, n: int | None) -> float:
    if n is None:
        return rating
    return round(50.0 + (rating - 50.0) * n / (n + SHRINK_K), 2)


def calibrated_inputs(fixture: dict) -> tuple[dict, list[dict]]:
    """Return (possibly adjusted fixture copy, list of change records)."""
    import copy
    fx = copy.deepcopy(fixture)
    changes: list[dict] = []
    inputs = fx.get("inputs") or {}
    sport = fx["sport"]

    for side in ("home", "away"):
        inp = inputs.get(side) or {}
        label = inp.get("label", "")
        rating = inp.get("rating")
        name = fx[side]

        # R3 — official ATP re-verification / backfill
        if sport == "tennis" and name in ATP_VERIFIED_2026_10_19:
            rank = ATP_VERIFIED_2026_10_19[name]
            new_rating = M.tennis_rank_rating(rank)
            if rating is None:
                inputs[side] = {
                    "label": "ATP world ranking",
                    "value": f"No. {rank} (official PIF ATP Rankings, 2026-10-19)",
                    "rating": new_rating,
                    "backfilled_by": "ccb6bde2 (verified atptour.com)",
                }
                changes.append({"side": side, "change": "rating_backfilled",
                                "detail": f"{name}: unrated in v2.0 -> official "
                                          f"rank No.{rank}, rating {new_rating}",
                                "source": ATP_RANKINGS_URL})
            elif abs(rating - new_rating) > 0.6:
                changes.append({"side": side, "change": "rating_corrected",
                                "detail": f"{name}: fixture label '{inp.get('value')}' "
                                          f"(rating {rating}) -> official 2026-10-19 "
                                          f"rank No.{rank} (rating {new_rating})",
                                "source": ATP_RANKINGS_URL})
                inp["rating"] = new_rating
            continue

        # R1 — shrinkage of small-sample record ratings
        if rating is not None:
            n = games_played(inp.get("value", ""), label)
            n_eff, kind = None, None
            if any(h in label for h in PURE_PCT_HINTS):
                n_eff, kind = n, "pure win%/points% rating"
            elif any(h in label for h in COMPOSITE_HINTS):
                n_eff = (2 * n) if n is not None else None
                kind = "composite standings-mapped rating (games counted double)"
            if n_eff is not None and n is not None and n <= 40:
                new = shrink(rating, n_eff)
                if abs(new - rating) >= 0.5:
                    changes.append({"side": side, "change": "rating_shrunk",
                                    "detail": f"{name}: '{inp.get('value')}' from "
                                              f"{n} games ({kind}); rating {rating} -> {new} "
                                              f"(shrinkage {n_eff}/({n_eff}+{SHRINK_K}) toward 50)"})
                    inp["rating"] = new
    fx["inputs"] = inputs
    return fx, changes


def price_calibrated(fixture: dict) -> tuple[dict, list[dict]]:
    """Reprice with model.py logic on calibrated inputs (+ R2 baseball fix)."""
    fx, changes = calibrated_inputs(fixture)

    home_in = (fx.get("inputs") or {}).get("home") or {}
    away_in = (fx.get("inputs") or {}).get("away") or {}
    is_split = (fx["sport"] == "baseball"
                and "home record" in home_in.get("label", "")
                and "road record" in away_in.get("label", ""))
    if is_split:
        fx["neutral"] = True  # removes the extra venue logit (R2)
        changes.append({"side": "match", "change": "venue_double_count_removed",
                        "detail": "Inputs are home/road split records, which "
                                  "already embed venue; v2.0 also added the "
                                  "0.540 home logit. v2.1 prices splits at a "
                                  "neutral 0.500 venue term."})

    priced = M.price_match(fx)
    return priced, changes


RACE_FORMATS = {  # sport -> (units_needed, unit_name) from fixture stage strings
    "darts": (6, "legs"),        # "Round 1 (Best of 11 legs)"
    "snooker": (4, "frames"),    # "Round 2 (Best of 7)"
    "volleyball": (3, "sets"),   # best-of-5 standard (PlusLiga / SuperLega)
}


def p_home_2way(priced: dict) -> float:
    hp, ap = priced["home_probability"], priced["away_probability"]
    return hp / (hp + ap)


def expand(fixture: dict, priced: dict) -> list[dict]:
    sport = fixture["sport"]
    cfg = M.SPORTS[sport]
    home, away = fixture["home"], fixture.get("away", "")
    p2 = p_home_2way(priced)
    mu_m = priced["expected_margin"]  # recomputed by price_match on calibrated p
    sig_m = cfg["sigma"]
    comp_override = M.COMPETITION_TOTALS.get(fixture.get("competition", ""))
    mu_t = comp_override[0] if comp_override is not None else cfg["total"]
    sig_t = comp_override[1] if comp_override is not None else cfg["tsigma"]
    if sport in ("tennis", "snooker", "darts", "volleyball"):
        closeness = 1.0 - 2.0 * abs(p2 - 0.5)  # keep v2 totals anchoring
        if mu_t is not None:
            pass  # mu_t stays the documented baseline

    books: list[dict] = []

    if sport in RACE_FORMATS:
        need, unit = RACE_FORMATS[sport]
        books += E.race_markets(home, away, p2, need, unit, sport)

    if sport == "tennis":
        books += E.tennis_markets(home, away, p2, mu_t, sig_t)
        # games handicap ladder from the normal games-margin (sigma in model)
        books += [m for m in E.margin_markets(home, away, mu_m, sig_m, None, None,
                                              sport, cfg, False)
                  if m["group"] == "Handicaps"]
    elif sport == "volleyball":
        books += E.volleyball_points(home, away, p2, sig_t)
    elif sport in ("darts", "snooker"):
        pass  # race book covers score/totals/handicap exactly
    elif sport == "esports":
        books += E.margin_markets(home, away, mu_m, sig_m, mu_t, sig_t,
                                  sport, cfg, False)
    else:  # normal margin/total sports
        books += E.margin_markets(home, away, mu_m, sig_m, mu_t, sig_t,
                                  sport, cfg, cfg["draws"])

    if sport == "ice-hockey":
        books += E.hockey_regulation(home, away, mu_m, sig_m, p2)
    if sport == "baseball":
        books += E.baseball_f5(home, away, mu_m, sig_m, mu_t, sig_t)
    if sport == "cricket" and mu_t is not None:
        books += E.cricket_innings(home, away, mu_t, sig_t)
    return books


def main() -> None:
    fixtures = json.loads((ROOT / "data" / "fixtures.json").read_text())["fixtures"]
    old_lines = {l["id"]: l for l in
                 json.loads((ROOT / "data" / "lines.json").read_text())["lines"]}
    preds = {p["match_id"]: p for p in
             json.loads((ROOT / "data" / "predictions.json").read_text())["items"]}

    rows, changes_all = [], []
    conf_counter_old, conf_counter_new = Counter(), Counter()
    tier_changes, pick_changes = [], []

    for fx in fixtures:
        if not fx.get("away"):
            rows.append({"id": fx["id"], "sport": fx["sport"],
                         "field_event": True,
                         "official_source": fx["sources"][0] if fx.get("sources") else None})
            continue
        priced, changes = price_calibrated(fx)
        old = old_lines[fx["id"]]
        books = expand(fx, priced)
        conf_counter_old[old["confidence"]] += 1
        conf_counter_new[priced["confidence"]] += 1
        if priced["confidence"] != old["confidence"]:
            tier_changes.append({"id": fx["id"], "sport": fx["sport"],
                                 "from": old["confidence"], "to": priced["confidence"],
                                 "p_pick_old": max(old["home_probability"], old["away_probability"]),
                                 "p_pick_new": max(priced["home_probability"], priced["away_probability"])})
        if priced["pick"] != old["pick"]:
            pick_changes.append({"id": fx["id"], "sport": fx["sport"],
                                 "old_pick": old["pick"], "new_pick": priced["pick"]})
        for c in changes:
            changes_all.append({"match_id": fx["id"], **c})
        rows.append({
            "id": fx["id"], "sport": fx["sport"], "sport_name": priced["sport_name"],
            "competition": fx["competition"], "stage": fx.get("stage", ""),
            "start_utc": fx.get("start_utc"), "date_local": fx.get("date_local"),
            "home": fx["home"], "away": fx["away"], "venue": fx.get("venue", ""),
            "status": fx["status"],
            "inputs_v21": fx.get("inputs"),
            "official_source": fx["sources"][0] if fx.get("sources") else None,
            "all_sources": fx.get("sources", []),
            "olbg": fx.get("olbg"),
            "v20": {"pick": old["pick"], "confidence": old["confidence"],
                    "home_probability": old["home_probability"],
                    "draw_probability": old["draw_probability"],
                    "away_probability": old["away_probability"],
                    "winner_odds": [o["odds"] for o in old["markets"][0]["outcomes"]]},
            "v21": {
                "pick": priced["pick"], "confidence": priced["confidence"],
                "home_probability": priced["home_probability"],
                "draw_probability": priced["draw_probability"],
                "away_probability": priced["away_probability"],
                "expected_margin": priced["expected_margin"],
                "rating_home": priced["rating_home"],
                "rating_away": priced["rating_away"],
                "both_measured": priced["both_measured"],
                "core_markets": priced["markets"],
            },
            "calibration_changes": changes,
            "expanded_markets": books,
            "expanded_market_count": len(books),
            "prediction_v20": preds.get(fx["id"]),
            "flags": fx.get("flags", []),
        })

    doc = {
        "generated": "2026-10-21",
        "session": "ccb6bde2-olbg1",
        "model": "olbg-independent-logit-normal-v2.1 (recalibrated) + expanded-market engine v1",
        "recalibration": {
            "R1_small_sample_shrinkage": f"rating' = 50 + (rating-50) * n/(n+{SHRINK_K}) "
                                         "for record-based ratings with n<=40 games",
            "R2_baseball_venue": "home/road split inputs priced at neutral 0.500 venue term",
            "R3_atp_reverification": "official PIF ATP Rankings 2026-10-19 (atptour.com)",
            "slopes": "unchanged — audit found ranking curves plausible; see calibration file",
        },
        "confidence_counts_v20": dict(conf_counter_old),
        "confidence_counts_v21": dict(conf_counter_new),
        "tier_changes": tier_changes,
        "pick_changes": pick_changes,
        "calibration_change_log": changes_all,
        "matches": rows,
    }
    out = ROOT / "data" / "market_expansion-ccb6bde2.json"
    out.write_text(json.dumps(doc, indent=2) + "\n")

    total_markets = sum(r.get("expanded_market_count", 0) for r in rows)
    print(f"v2.1 repriced {len([r for r in rows if not r.get('field_event')])} H2H matches")
    print(f"confidence v2.0={dict(conf_counter_old)} -> v2.1={dict(conf_counter_new)}")
    print(f"tier changes: {len(tier_changes)}  pick changes: {len(pick_changes)}")
    for tc in tier_changes:
        print("  TIER", tc)
    for pc in pick_changes:
        print("  PICK", pc)
    print(f"calibration changes logged: {len(changes_all)}")
    print(f"expanded markets originated: {total_markets} "
          f"(avg {total_markets / max(1,len([r for r in rows if not r.get('field_event')])):.1f}/match)")
    print("wrote", out)


if __name__ == "__main__":
    main()
