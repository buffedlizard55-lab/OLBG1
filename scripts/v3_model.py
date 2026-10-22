#!/usr/bin/env python3
"""
v3_model.py - transparent, independent pricing desk.

Method (identical for every sport):
  1. Each side carries ONE rating on a 0-100 scale, derived only from the official record named
     in data/v3/fixtures.json -> home_input / away_input. No tipster odds are read.
  2. The rating gap plus home advantage forms a latent edge. P(win) = Phi(edge / 17).
     A 17-point gap is therefore a 50/50 coin-flip at a neutral venue before home advantage.
  3. The same edge sets the expected scoring margin, so handicap and total markets are priced
     from one Normal distribution rather than from separate guesses.
  4. Prices are fair (1 / probability), rounded to 2dp, with no added margin. The desk publishes
     the overround it would have to charge separately, so a reader can see the difference
     between a fair price and a bookmaker price.
  5. Best-of-N sports (darts, snooker, tennis) use a Binomial leg model instead of a margin.
"""
from __future__ import annotations

import math

PHI = lambda z: 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))
EDGE_SCALE = 17.0  # only used for the legacy edge display
PER_LEG_SCALE = 65.0  # binomial sports: rating points -> one leg of a set/frame/match


def dec(p: float) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6)
    return round(1.0 / p, 2)


def american(p: float) -> int:
    return american_from_price(dec(p))


def american_from_price(price: float) -> int:
    """US odds of the *published* decimal price.

    Deriving US odds from the probability instead of from the rounded price produced
    displays such as 1.40 / -251, which contradicts the brief's -250 floor. Every
    published moneyline is now the exact conversion of the decimal next to it.
    """
    if price >= 2.0:
        return int(round((price - 1) * 100))
    return -int(round(100 / (price - 1)))


def band(price: float) -> bool:
    """Policy band: -250 to +10000, i.e. decimal 1.40 to 101.00."""
    return 1.40 <= price <= 101.00


def _rating(side, default):
    if side is None:
        return default, True
    r = side.get("rating")
    if r is None:
        return default, True
    return float(r), False


def binomial_dist(n, p):
    """P(k wins) for k = 0..n."""
    return [math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(n + 1)]


def price_fixture(f: dict) -> dict:
    rh, dh = _rating(f.get("home_input"), 58.0)
    ra, da = _rating(f.get("away_input"), 58.0)
    defaulted = dh or da
    # A missing rating must never be turned into a strength edge. Subtracting a league-average
    # prior from a measured rating manufactures a gap no source ever measured (97.5 - 58 = 39.5
    # points, which priced an unrated opponent at 5.51). When either side is unrated the edge is
    # zero and the price is the venue baseline only.
    edge = 0.0 if defaulted else (rh - ra)
    edge += float(f.get("hfa") or 0.0)

    out = {
        "id": f["id"],
        "edge_measured": not defaulted,
        "sport": f["sport"],
        "competition": f.get("competition", ""),
        "home": f.get("home", ""),
        "away": f.get("away", ""),
        "start_utc": f.get("start_utc"),
        "date_local": f.get("date_local"),
        "status": f.get("status"),
        "verified_at": f.get("verified_at"),
        "venue": f.get("venue", ""),
        "stage": f.get("stage", ""),
        "time_note": f.get("time_note", ""),
        "flags": list(f.get("flags", [])),
        "sources": f.get("sources", []),
        "home_input": f.get("home_input"),
        "away_input": f.get("away_input"),
        "event_only": bool(f.get("event_only")),
        "assumptions": {
            "model": f.get("model") or "normal",
            "sigma": float(f.get("sigma") or 14.0),
            "slope": float(f.get("slope") or 0.05),
            "hfa": float(f.get("hfa") or 0.0),
            "hc_max": float(f.get("hc_max") or 6.5),
            "total_line": float(f.get("total_line") or 45.0),
            "total_sigma": float(f.get("total_sigma") or f.get("sigma") or 14.0),
            "series": f.get("series"),
            "per_leg_scale": PER_LEG_SCALE if (f.get("model") == "binomial" and f.get("series")) else None,
        },
        "defaulted": defaulted,
        "edge": round(edge, 2),
        "markets": [],
        "pick": None,
        "confidence": None,
        "cap": None,
    }
    if out["event_only"]:
        out["note"] = "Event card only - no head-to-head market is priced."
        out["best_market"] = None
        out["high_candidates"] = []
        return out

    mkts = []

    def add(market, selection, p, extra=None):
        p = min(max(p, 0.03), 0.97)
        # a 2% shot at 50/1 is not a market this desk quotes
        if market != "Match winner" and (p < 0.02 or p > 0.98):
            return
        price = dec(p)
        row = {
            "market": market,
            "selection": selection,
            "model_prob": round(p, 4),
            "price": price,
            "us": american_from_price(price),
            "prob_pct": round(p * 100, 1),
            "in_band": band(price),
        }
        if extra:
            row.update(extra)
        mkts.append(row)

    if f.get("model") == "binomial" and f.get("series"):
        legs = int(f["series"]["legs"])
        need = legs // 2 + 1
        p_leg_home = min(max(PHI(edge / PER_LEG_SCALE), 0.05), 0.95)
        scores = {}
        for x in range(0, need):
            scores[(need, x)] = math.comb(need - 1 + x, x) * (p_leg_home ** need) * ((1 - p_leg_home) ** x)
            scores[(x, need)] = math.comb(need - 1 + x, x) * ((1 - p_leg_home) ** need) * (p_leg_home ** x)
        total = sum(scores.values())
        scores = {k: v / total for k, v in scores.items()}
        p_home = sum(v for (h, a_), v in scores.items() if h > a_)
        p_away = 1 - p_home
        add("Match winner", f.get("home", ""), p_home)
        add("Match winner", f.get("away", ""), p_away)
        for (h, a_), v in sorted(scores.items(), key=lambda kv: -kv[1])[:12]:
            side = f.get("home", "") if h > a_ else f.get("away", "")
            add("Correct score", f"{h}-{a_} {side}", v)
        for line in (1.5, 2.5, 3.5):
            ph = sum(v for (h, a_), v in scores.items() if (h - a_) > line)
            pa = sum(v for (h, a_), v in scores.items() if (a_ - h) > line)
            unit = f["series"].get("unit", "legs")
            add("Handicap", f"{f.get('home','')} -{line} {unit}", ph)
            add("Handicap", f"{f.get('away','')} -{line} {unit}", pa)
        out["p_home"] = p_home
        out["p_away"] = p_away
        out["draw_p"] = 0.0
    else:
        sigma = float(f.get("sigma") or 14.0)
        slope = float(f.get("slope") or 0.05)
        mu = edge * slope
        p_home = PHI(mu / sigma)
        p_away = 1 - p_home
        add("Match winner", f.get("home", ""), p_home)
        add("Match winner", f.get("away", ""), p_away)

        hc_max = float(f.get("hc_max") or 6.5)
        for line in (1, 1.5, 2, 2.5, 3, 3.5, 4.5, 6.5, 9.5, 12.5, 16.5, 20.5, 24.5, 30.5, 40.5):
            if line > hc_max:
                continue
            add("Handicap", f"{f.get('home','')} -{line:g}", PHI((mu - line) / sigma))
            add("Handicap", f"{f.get('away','')} -{line:g}", PHI((-mu - line) / sigma))

        tl = float(f.get("total_line") or 45.0)
        tsig = float(f.get("total_sigma") or sigma)
        for off in (0.0, round(tsig * 0.55, 1), -round(tsig * 0.55, 1), round(tsig * 1.1, 1), -round(tsig * 1.1, 1)):
            line = round((tl + off) * 2) / 2
            add("Total", f"Over {line:g}", 1 - PHI((line - tl) / tsig))
            add("Total", f"Under {line:g}", PHI((line - tl) / tsig))

        out["p_home"] = p_home
        out["p_away"] = p_away
        out["draw_p"] = 0.0
        out["mu"] = round(mu, 2)
        out["sigma"] = sigma

    # headline pick: the stronger side in the match-winner market
    h2h = [m for m in mkts if m["market"] == "Match winner"]
    headline = max(h2h, key=lambda m: m["model_prob"])
    price = headline["price"]
    p = headline["model_prob"]
    conf = "High" if (p >= 0.70 and band(price)) else ("Medium" if p >= 0.55 else "Low")
    cap = None
    if conf == "High" and defaulted:
        conf, cap = "Medium", "one side unrated"
    if conf == "High" and out["status"] == "carried":
        conf, cap = "Medium", "row not re-verified on 22 Oct"
    headline = dict(headline)
    headline["confidence"] = conf
    headline["cap_reason"] = cap
    if p >= 0.70 and not band(price):
        headline["below_band"] = True
    out["pick"] = headline
    out["confidence"] = conf

    # Desk selection: one policy-compliant pick per match. Totals are published for reference
    # only and are not eligible, because a total ladder can always manufacture a 70% quote on
    # both sides at different lines.
    eligible = [m for m in mkts
                if m["market"] in ("Match winner", "Handicap")
                and m["in_band"]]
    best = max(eligible, key=lambda m: m["model_prob"]) if eligible else None
    if best is not None and defaulted:
        # No measured input on either side: the only thing moving this price is the home-field
        # constant. A tip here would be a guess dressed as an edge, so the card is a no-bet and
        # the reason is published. (The match-winner call is still shown, graded Low.)
        out["no_tip_reason"] = ("No official rating was captured for either side, so this price reflects only the "
                                "home-field adjustment. The desk will not tip a home-advantage-only number.")
        best = None
    if best is not None and best["model_prob"] < 0.52:
        # the only in-band line is a coin-flip or worse: publish no tip rather than a bad one
        best = None
    if best is not None:
        best = dict(best)
        p = best["model_prob"]
        conf = "High" if p >= 0.70 else ("Medium" if p >= 0.55 else "Low")
        cap = None
        if conf == "High" and defaulted:
            conf, cap = "Medium", "one side unrated"
        if conf == "High" and out["status"] == "carried":
            conf, cap = "Medium", "row not re-verified on 22 Oct"
        best["confidence"] = conf
        best["cap_reason"] = cap
    if best is None and "no_tip_reason" not in out:
        out["no_tip_reason"] = "No selection at or above 52% clears the -250 floor on this card."
    out["best_market"] = best
    out["high_candidates"] = [best] if (best and best["confidence"] == "High") else []
    # Alternate rungs priced below 5% (or above 95%) are not useful to a reader and the
    # binomial floor can make both sides of a rung quote 3.0%, so drop those rungs.
    kept = [m for m in mkts if m["market"] == "Match winner" or 0.05 <= m["model_prob"] <= 0.95]
    out["markets"] = sorted(kept, key=lambda m: -m["model_prob"])
    return out


def summarise(priced: list[dict]) -> dict:
    played = [p for p in priced if not p["event_only"]]
    highs = [p for p in played if p.get("high_candidates")]
    return {
        "fixtures": len(priced),
        "priced_matches": len(played),
        "event_cards": len(priced) - len(played),
        "markets": sum(len(p["markets"]) for p in played),
        "high_picks": sum(len(p["high_candidates"]) for p in played),
        "matches_with_high": len(highs),
        "medium_picks": sum(1 for p in played if p["confidence"] == "Medium"),
        "low_picks": sum(1 for p in played if p["confidence"] == "Low"),
        "high_picks_headline": sum(1 for p in played if p["confidence"] == "High"),
    }
