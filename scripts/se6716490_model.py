#!/usr/bin/env python3
"""Session e6716490-olbg1 — originate our own prices for every priced fixture.

The desk's pricing engine.  Small, deterministic and fully documented so every
number on the site can be reproduced.

Inputs
------
``data/e6716490/fixtures.json``.  Each fixture carries a 0-100 strength input per
side, taken from the official page cited on that row (points percentage, ladder
points, ICC rating, world ranking, tour seed, published 1X2 percentages, ...).
Where a side has no verified strength input the row is priced off a neutral
baseline, carries no strength edge, and is capped at Low confidence.

Method
------
1. Strength edge ``e = (r_home - r_away) + HFA`` in rating points; the home edge is
   only applied when the fixture is not neutral.
2. Two-way probability ``p = 1 / (1 + 10 ** (-e / denom))``.  Sports that can be
   drawn give up a draw share that is widest at a pick'em.
3. Expected margin ``m = margin_scale * e`` in the sport's scoring unit.
4. Handicap ladders are hung on **conventional half-lines** at 0.5-unit steps around
   ``m`` (the way a book hangs them), then priced from the normal CDF with the
   sport's ``sigma``.  Lines are never nudged so that a price lands inside the
   confidence band.
5. Totals are priced only when a verified scoring rate exists on both sides
   (baseball's runs per game is the only such input in this dataset).
6. Prices are zero-vig fair prices; the 5% book-equivalent is shown beside them.

Tiers
-----
* **High** — both sides measured, model probability in ``[0.70, 1/1.40]`` (i.e. a
  fair price between -250 and +10000 and better than a 70% chance) on a rung that
  the desk actually publishes.  At most one High per fixture, so the tier cannot be
  padded with correlated handicaps of the same match.
* **Medium** — both sides measured and probability >= 0.60 but outside the band.
* **Low** — one-sided inputs, neutral baseline, or probability below 0.60.

Nothing here is copied from a bookmaker; every price is the desk's own estimate.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "e6716490"

BAND_MIN_DECIMAL = 1.40        # -250
BAND_MAX_DECIMAL = 101.0       # +10000
BAND_MAX_PROB = 1 / BAND_MIN_DECIMAL   # 0.7142857
BOOK_MARGIN = 0.05
HIGH_CAP = 24                  # published High picks per release (see methodology)

PARAMS = {
    "ice-hockey":      dict(denom=9.0,  hfa=3.0, draw=0.000, margin=0.036, sigma=1.30, step=0.5, unit="goals",  label="Goals handicap"),
    "basketball":      dict(denom=7.0,  hfa=3.5, draw=0.000, margin=0.220, sigma=12.0, step=0.5, unit="points", label="Points handicap"),
    "baseball":        dict(denom=9.0,  hfa=2.0, draw=0.000, margin=0.030, sigma=4.30, step=0.5, unit="runs",   label="Runs handicap"),
    "tennis":          dict(denom=12.0, hfa=0.0, draw=0.000, margin=0.020, sigma=0.50, step=0.5, unit="sets",   label="Sets handicap"),
    "cricket":         dict(denom=10.0, hfa=2.0, draw=0.000, margin=0.350, sigma=30.0, step=5.0, unit="runs",   label="Runs handicap"),
    "snooker":         dict(denom=11.0, hfa=0.0, draw=0.000, margin=0.045, sigma=1.60, step=0.5, unit="frames", label="Frames handicap"),
    "darts":           dict(denom=10.0, hfa=0.0, draw=0.000, margin=0.055, sigma=1.80, step=0.5, unit="legs",   label="Legs handicap"),
    "rugby-union":     dict(denom=10.0, hfa=3.0, draw=0.050, margin=0.200, sigma=12.0, step=0.5, unit="points", label="Points handicap"),
    "rugby-league":    dict(denom=10.0, hfa=2.0, draw=0.035, margin=0.180, sigma=12.0, step=0.5, unit="points", label="Points handicap"),
    "handball":        dict(denom=9.0,  hfa=2.5, draw=0.045, margin=0.100, sigma=6.50, step=0.5, unit="goals",  label="Goals handicap"),
    "volleyball":      dict(denom=10.0, hfa=1.5, draw=0.000, margin=0.012, sigma=0.90, step=0.5, unit="sets",   label="Sets handicap"),
    "aussie-rules":    dict(denom=11.0, hfa=3.0, draw=0.010, margin=0.250, sigma=25.0, step=1.5, unit="points", label="Points handicap"),
    "esports":         dict(denom=12.0, hfa=0.0, draw=0.000, margin=0.020, sigma=0.70, step=0.5, unit="maps",   label="Maps handicap"),
    "gaelic-football": dict(denom=11.0, hfa=2.0, draw=0.040, margin=0.120, sigma=8.00, step=0.5, unit="points", label="Points handicap"),
}


def normal_cdf(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def american(dec: float) -> int:
    if dec >= 2.0:
        return int(round((dec - 1.0) * 100))
    return int(round(-100.0 / (dec - 1.0)))


def price(prob: float) -> dict:
    prob = min(max(prob, 0.005), 0.995)
    fair = 1.0 / prob
    book = 1.0 / min(0.995, prob * (1.0 + BOOK_MARGIN))
    return {
        "prob": round(prob, 4),
        "price": round(fair, 2),
        "us": american(fair),
        "book_price": round(book, 2),
        "book_us": american(book),
        "in_band": BAND_MIN_DECIMAL <= fair <= BAND_MAX_DECIMAL,
    }


def grade(prob: float, in_band: bool, two_sided: bool) -> str:
    if not two_sided:
        return "Low"
    if prob >= 0.70 and in_band:
        return "High"
    if prob >= 0.60:
        return "Medium"
    return "Low"


def three_way(p_home: float, draw_base: float) -> tuple[float, float, float]:
    if draw_base <= 0:
        return p_home, 0.0, 1.0 - p_home
    closeness = 1.0 - min(1.0, abs(p_home - 0.5) * 2.0)
    draw = draw_base * closeness
    return p_home * (1.0 - draw), draw, (1.0 - p_home) * (1.0 - draw)


def auto_step(sigma: float, granularity: float) -> float:
    """Half-line step wide enough to cover roughly one sigma either side in seven lines."""
    target = sigma / 3.5
    step = granularity
    while step < target - 1e-9:
        step += granularity
    return round(step, 1)


def hang_lines(margin: float, sigma: float, granularity: float) -> list[float]:
    """Home handicaps, signed: -2.5 means the home side gives 2.5.

    Seven lines are hung per fixture (the pick'em line and three either side), at
    half-line steps chosen so the board spans about one standard deviation of the
    model's margin distribution.  The lines are never nudged to move a price into
    the confidence band; whether a rung lands inside the band is decided by the
    sport's own scoring granularity.
    """
    centre = -margin                       # the line that prices the match near 50/50
    step = max(1.0, auto_step(sigma, granularity))
    base = math.floor(centre / step) * step
    lines = []
    for k in (-3, -2, -1, 0, 1, 2, 3):
        line = base + k * step
        if abs(line - round(line)) < 1e-9:   # snap whole numbers onto a half-line
            line = math.floor(line) + 0.5
        lines.append(round(line, 1))
    return sorted(set(lines))


NOW_UTC = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_fixture(row: dict) -> dict:
    sport = row["sport"]
    params = PARAMS.get(sport)
    out = {
        "id": row["id"],
        "sport": sport,
        "home": row["home"],
        "away": row["away"],
        "competition": row["competition"],
        "stage": row["stage"],
        "start_utc": row["start_utc"],
        "date_local": row["date_local"],
        "venue": row["venue"],
        "status": row["status"],
        "kind": row["kind"],
        "sources": row["sources"],
        "inputs": row["inputs"],
        "unverified_fields": row["unverified_fields"],
        "flags": [f for f in dict.fromkeys(list(row["flags"]) + list(row.get("notes") or [])) if f],
        "provenance": row["provenance"],
        "superseded": row.get("superseded", []),
        "markets": [],
        "priced": False,
        "reason": "",
        "winner_call": "",
        "winner_confidence": "",
        "two_sided": False,
        "conviction": 0.0,
    }

    if row.get("start_utc") and row["start_utc"] <= NOW_UTC:
        out["expired"] = True
        out["reason"] = (f"Started at {row['start_utc']}, before this desk's publish cut-off of {NOW_UTC}. "
                         "Kept on the record, not priced.")
        return out
    if row["kind"] == "field":
        out["reason"] = ("Outright / multi-runner card: a field cannot be priced from one official "
                         "strength input per side, so it is published unpriced and flagged.")
        return out
    if params is None:
        out["reason"] = "No pricing parameters for this sport on this desk."
        return out

    rh = row["inputs"]["home"].get("rating")
    ra = row["inputs"]["away"].get("rating")
    two_sided = rh is not None and ra is not None
    out["two_sided"] = two_sided
    if two_sided:
        edge = float(rh) - float(ra) + (0.0 if row.get("neutral") else params["hfa"])
        p_home_two = 1.0 / (1.0 + 10.0 ** (-edge / params["denom"]))
    else:
        edge = 0.0
        p_home_two = 0.5
        out["flags"].append("At least one side has no verified strength input: neutral baseline, "
                            "no strength edge applied, capped at Low confidence.")

    p_home, p_draw, p_away = three_way(p_home_two, params["draw"])
    margin = params["margin"] * edge

    # ---- match winner ------------------------------------------------------
    winner_market = {"market": "Match winner", "selections": []}
    sides = [(row["home"], p_home), (row["away"], p_away)]
    if p_draw > 0:
        sides.insert(1, ("Draw", p_draw))
    for name, prob in sides:
        priced = price(prob)
        priced.update({
            "selection": name,
            "market": "Match winner",
            "tier": grade(prob, priced["in_band"], two_sided),
            "line": None,
        })
        winner_market["selections"].append(priced)
    out["markets"].append(winner_market)

    # ---- handicap ladder ---------------------------------------------------
    # Home handicap h is signed: home covers when (home - away) + h > 0.
    for h in hang_lines(margin, params["sigma"], params["step"]):
        z = (-h - margin) / params["sigma"]
        p_home_cover = 1.0 - normal_cdf(z)
        for side, prob, handicap in (
            (row["home"], p_home_cover, h),
            (row["away"], 1.0 - p_home_cover, -h),
        ):
            priced = price(prob)
            priced.update({
                "selection": f"{side} {handicap:+.1f}",
                "market": f"{params['label']} {abs(handicap):.1f}",
                "tier": grade(prob, priced["in_band"], two_sided),
                "line": handicap,
            })
            out["markets"].append({"market": priced["market"], "selections": [priced]})

    # ---- totals ------------------------------------------------------------
    raw = row.get("model_raw") or {}
    if raw.get("kind") == "mlb" and all(
        raw.get(k) is not None for k in ("home_rs_pg", "home_ra_pg", "away_rs_pg", "away_ra_pg")
    ):
        exp_total = (raw["home_rs_pg"] + raw["home_ra_pg"] + raw["away_rs_pg"] + raw["away_ra_pg"]) / 2.0
        sigma_total = 4.30
        for line in (round(exp_total) - 1.5, round(exp_total) - 0.5, round(exp_total) + 0.5, round(exp_total) + 1.5):
            p_over = 1.0 - normal_cdf((line - exp_total) / sigma_total)
            for name, prob in ((f"Over {line}", p_over), (f"Under {line}", 1.0 - p_over)):
                priced = price(prob)
                priced.update({
                    "selection": name,
                    "market": f"Total runs {line}",
                    "tier": grade(prob, priced["in_band"], two_sided),
                    "line": line,
                })
                out["markets"].append({"market": priced["market"], "selections": [priced]})
        out["total_baseline"] = {
            "expected_runs": round(exp_total, 2),
            "rule": "mean of both sides' verified runs scored and runs allowed per game",
        }

    out["priced"] = True
    out["expected_margin"] = round(margin, 2)
    out["unit"] = params["unit"]
    out["conviction"] = round(abs(margin) / params["sigma"], 3) if params["sigma"] else 0.0
    best = max(winner_market["selections"], key=lambda s: s["prob"])
    out["winner_call"] = best["selection"]
    out["winner_confidence"] = best["tier"]
    return out


def main() -> int:
    blob = json.load((OUT / "fixtures.json").open())
    rows = [build_fixture(r) for r in blob["fixtures"]]

    # ---- High band ---------------------------------------------------------
    candidates = []
    for r in rows:
        if not r["priced"] or not r["two_sided"]:
            continue
        band = [
            s
            for m in r["markets"]
            for s in m["selections"]
            if s["tier"] == "High" and 0.70 <= s["prob"] <= BAND_MAX_PROB and s["in_band"]
        ]
        if not band:
            continue
        # Prefer the match winner when it is itself in band, then the rung priced
        # closest to the middle of the band, then the shorter price.
        band.sort(key=lambda s: (s["market"] != "Match winner", abs(s["prob"] - 0.7071), -s["prob"]))
        best = band[0]
        for s in band:
            s["tier"] = "Medium"        # any other band rung on this fixture is not High
            s["demoted"] = "one High per fixture"
        best["tier"] = "High"
        candidates.append((r, best))

    # Rank by conviction (distance of the model's view from a coin flip) and cap
    # the tier, so every published High can carry its own written prediction.
    candidates.sort(key=lambda rb: (-rb[0]["conviction"], rb[0]["start_utc"] or "9999", rb[0]["id"]))
    per_sport: dict[str, int] = {}
    per_pairing: set[tuple] = set()
    highs = []
    for r, sel in candidates:
        pairing = (r["sport"], r["home"].lower(), r["away"].lower())
        if pairing in per_pairing:
            sel["tier"] = "Medium"
            sel["demoted"] = "this pairing already carries a High pick (no duplicate Highs per match-up)"
            continue
        per_pairing.add(pairing)
        if len(highs) >= HIGH_CAP:
            sel["tier"] = "Medium"
            sel["demoted"] = f"outside the published High cap of {HIGH_CAP}"
            continue
        if per_sport.get(r["sport"], 0) >= 3:
            sel["tier"] = "Medium"
            sel["demoted"] = "sport cap (max 3 High picks per sport)"
            continue
        per_sport[r["sport"]] = per_sport.get(r["sport"], 0) + 1
        sel["high"] = True
        highs.append({
            "id": r["id"],
            "sport": r["sport"],
            "home": r["home"],
            "away": r["away"],
            "competition": r["competition"],
            "start_utc": r["start_utc"],
            "market": sel["market"],
            "selection": sel["selection"],
            "line": sel["line"],
            "prob": sel["prob"],
            "price": sel["price"],
            "us": sel["us"],
            "book_price": sel["book_price"],
            "book_us": sel["book_us"],
            "unit": r.get("unit", ""),
            "expected_margin": r.get("expected_margin"),
            "conviction": r["conviction"],
            "winner_call": r["winner_call"],
            "winner_confidence": r["winner_confidence"],
            "inputs": r["inputs"],
            "sources": r["sources"],
            "flags": r["flags"][:4],
            "provenance": r["provenance"],
        })

    counts = {
        "fixtures": len(rows),
        "priced": sum(1 for r in rows if r["priced"]),
        "unpriced": sum(1 for r in rows if not r["priced"]),
        "expired": sum(1 for r in rows if r.get("expired")),
        "markets": sum(len(r["markets"]) for r in rows),
        "selections": sum(len(m["selections"]) for r in rows for m in r["markets"]),
        "high": len(highs),
        "by_tier": {
            t: sum(1 for r in rows for m in r["markets"] for s in m["selections"] if s["tier"] == t)
            for t in ("High", "Medium", "Low")
        },
        "winner_tiers": {
            t: sum(1 for r in rows if r["priced"] and r["winner_confidence"] == t)
            for t in ("High", "Medium", "Low")
        },
        "by_sport_high": per_sport,
    }

    out = {
        "session": "e6716490-olbg1",
        "generated_utc": NOW_UTC,
        "cut_off_utc": NOW_UTC,
        "policy": {
            "fair_price": "zero-vig model probability inverted; 5% book-equivalent shown alongside",
            "band_decimal": [BAND_MIN_DECIMAL, BAND_MAX_DECIMAL],
            "band_us": [-250, 10000],
            "band_prob": [0.70, round(BAND_MAX_PROB, 6)],
            "high_rule": ("two-sided verified inputs, model probability 0.70 to 1/1.40, fair price "
                          "inside -250..+10000, one High per fixture, max 3 per sport, cap 24"),
            "high_cap": HIGH_CAP,
            "medium_rule": "two-sided verified inputs and model probability >= 0.60, outside the band",
            "low_rule": "one-sided inputs, neutral baseline, or probability below 0.60",
            "book_margin": BOOK_MARGIN,
            "params": PARAMS,
        },
        "counts": counts,
        "highs": highs,
        "rows": rows,
    }
    with (OUT / "lines.json").open("w") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print(f"priced {counts['priced']}/{counts['fixtures']} fixtures, {counts['markets']} markets, "
          f"{counts['selections']} selections, {counts['high']} High picks")
    print("tiers:", counts["by_tier"], "| winner tiers:", counts["winner_tiers"])
    for h in highs:
        print(f"  {h['sport']:15} {h['selection'][:34]:34} p={h['prob']:.3f} {h['us']:+6d} "
              f"conv={h['conviction']:.2f}  {h['home'][:22]} v {h['away'][:22]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
