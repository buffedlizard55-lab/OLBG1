#!/usr/bin/env python3
"""sf1c13c19_model.py - originate f1c13c19 lines from the verified fixture dataset.

Reuses the deterministic pricing mechanics of the root engine (scripts/model.py):
same sigmoid/logit strength scaling, same Gaussian handicap ladders, same 5%-margin
book rendering with the vig-free fair price published beside it.

Differences are deliberate, documented, and follow the T54/'T55 band-resolution'
consensus:

  HIGH tier requires ALL of
    1. fixture verification verdict == 'verified' (governing-body confirmation today)
    2. BOTH side ratings measured AND sourced tier == 'verified'
    3. model probability of the published selection >= 70.0%
    4. the ZERO-VIG fair price of that selection inside -250 .. +10000 US
       (fair decimal >= 1.40 for minus-priced sides; plus-money always allowed)
  Because a 70%+ pick prices shorter than -250 as soon as any margin is added, rule 4
  is tested on the vig-free line; the 5% book equivalent is printed alongside for
  comparison only.  If no rung of the market ladder lands the favourite inside
  [70.0%, 71.43%], the pick is 'above-window' -> published with tier Medium and the
  natural moneyline is shown on the Window Report page, exactly as T55 mandates.

  MEDIUM: both sides rated (any documented sourcing tier), separation >= sport med floor.
  LOW: everything else; niche-sport picks additionally price-capped (-150 niche /
       -190 general on the 5% book price), favourites beyond that cap fall to Low.

Outputs: data/f1c13c19/lines.json
"""
import json, math, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))  # scripts/
import model as M  # root deterministic engine (pure helpers + SPORTS config)

DATA = pathlib.Path("data/f1c13c19")

HIGH_P_MIN = 0.700
HIGH_P_MAX = 0.7143  # fair decimal <= 1/0.7143 = 1.40 exactly -> -250
NICHE = {"tennis", "snooker", "darts", "cricket", "handball", "volleyball",
         "gaelic-football", "greyhounds", "rugby-league", "motor-racing", "golf",
         "esports"}
EVENT_ONLY = {"golf", "motor-racing", "greyhounds"}


def fair_inside_high_window(p: float) -> bool:
    """Zero-vig band test: 70.0% <= p <= 71.43% (i.e. fair price >= 1.40 decimal)."""
    return HIGH_P_MIN <= p <= HIGH_P_MAX


def side_rating(side):
    if not side:
        return None, False, "pending"
    return side.get("rating"), ("rating" in side), side.get("tier", "pending")


def build_ladder(match, p_home_2way, cfg):
    """Gaussian margin + handicap ladder, walked outward until a rung lands in the
    zero-vig high band [70.0, 71.43]; returns (markets, best_band_rung)."""
    markets = []
    band_rung = None
    margin = cfg["sigma"] * M._norm_ppf(p_home_2way)
    fav_home = p_home_2way >= 0.5
    give = abs(margin)
    if cfg["fixed_line"] is not None and give < 2.2:
        give = cfg["fixed_line"]
    give = max(0.5, round(give * 2.0) / 2.0)
    ladder = []
    for target, role in ((0.500, "main line"), (0.600, "alternate (60%)"), (0.680, "alternate (68%)")):
        g = abs(margin) - cfg["sigma"] * M._norm_ppf(target)
        if role == "main line" and cfg["fixed_line"] is not None and abs(margin) < 2.2:
            g = cfg["fixed_line"]
        g = max(0.5, round(g * 2.0) / 2.0)
        ladder.append((g, role))
    seen = set()
    for g, role in ladder:
        if g in seen:
            continue
        seen.add(g)
        # walk outward if favourite cover probability overshoots the band top
        for _ in range(12):
            h_home = -g if fav_home else g
            p_cover = 1.0 - M._norm_cdf((-h_home - margin) / cfg["sigma"])
            p_fav_cover = p_cover if fav_home else 1.0 - p_cover
            if p_fav_cover <= HIGH_P_MAX + 1e-9:
                break
            g += 0.5
        h_home = -g if fav_home else g
        p_cover = 1.0 - M._norm_cdf((-h_home - margin) / cfg["sigma"])
        p_cover = min(max(p_cover, 0.02), 0.98)
        out = [M._outcome(f"{match['home']} {h_home:+.1f}", p_cover),
               M._outcome(f"{match['away']} {-h_home:+.1f}", 1.0 - p_cover)]
        mk = {"key": f"handicap_{len(markets)}", "name": cfg["handicap_name"],
              "line": f"{g:.1f}", "role": role, "outcomes": out,
              "basis": f"Gaussian margin projection (E[M]={margin:+.1f}, sigma={cfg['sigma']:.1f})"}
        markets.append(mk)
        p_fav = p_cover if fav_home else 1.0 - p_cover
        if HIGH_P_MIN <= p_fav <= HIGH_P_MAX:
            if band_rung is None or p_fav < band_rung[0]:
                band_rung = (p_fav, mk)
    return markets, band_rung, margin


def price_event(e):
    sport = e["sport"]
    cfg = M.SPORTS[sport]
    home_in = e["inputs"]["home"]; away_in = e["inputs"]["away"]
    r_home, has_home, tier_home = side_rating(home_in)
    r_away, has_away, tier_away = side_rating(away_in)
    both_rated = has_home and has_away
    both_verified = both_rated and tier_home == "verified" and tier_away == "verified"
    rating_tier = "verified" if both_verified else (
        "cross-checked" if (both_rated) else "pending")

    p_venue = 0.500 if e.get("neutral") else cfg["p_base"]
    logit = M._logit(p_venue)
    if both_rated:
        logit += (r_home - r_away) / cfg["scale"]
    p_home_2way = min(max(M._sigmoid(logit), 0.025), 0.975)

    markets = []
    if cfg["draws"]:
        d_raw = cfg["draw_p"] * math.exp(-(((p_home_2way - 0.5) / 0.34) ** 2))
        d = max(0.018, round(d_raw, 6))
        probs3 = M._normalize_probs([p_home_2way*(1-d), d, (1-p_home_2way)*(1-d)])
        winner_outcomes = [M._outcome(e["home"], probs3[0]), M._outcome("Draw", probs3[1]),
                           M._outcome(e["away"], probs3[2])]
        p_home, p_draw, p_away = probs3
        dnb = M._normalize_probs([p_home_2way, 1.0 - p_home_2way])
        markets.append({"key": "dnb", "name": "Draw No Bet (2-Way)", "line": "PK",
                        "outcomes": [M._outcome(f"{e['home']} (DNB)", dnb[0]),
                                     M._outcome(f"{e['away']} (DNB)", dnb[1])],
                        "basis": "Two-way conditional probabilities excluding regulation draw"})
    else:
        probs2 = M._normalize_probs([p_home_2way, 1.0 - p_home_2way])
        winner_outcomes = [M._outcome(e["home"], probs2[0]), M._outcome(e["away"], probs2[1])]
        p_home, p_away, p_draw = probs2[0], probs2[1], 0.0

    markets.insert(0, {"key": "winner", "name": "Match Winner (3-Way)" if cfg["draws"] else "Match Winner",
                       "line": "", "outcomes": winner_outcomes,
                       "basis": ("Official ratings + venue adjustment" if both_rated
                                 else "Neutral venue baseline (unrated side)")})

    fav_home = p_home_2way >= 0.5
    p_best = max(p_home, p_away)
    band_rung = None; margin = 0.0
    if sport not in EVENT_ONLY:
        hcaps, band_rung, margin = build_ladder(e, p_home_2way, cfg)
        markets.extend(hcaps)

    comp_override = M.COMPETITION_TOTALS.get(e.get("competition", ""), None)
    tot_base = comp_override[0] if comp_override else cfg["total"]
    tot_sigma = comp_override[1] if comp_override else cfg["tsigma"]
    if tot_base is not None and sport not in EVENT_ONLY:
        if sport in ("tennis", "snooker", "darts", "volleyball"):
            closeness = 1.0 - 2.0 * abs(p_home_2way - 0.5)
            p_over_raw = 0.44 + 0.14 * closeness
        else:
            p_over_raw = 0.500
        step = max(1.5, round((tot_sigma / 4.0) * 2.0) / 2.0)
        z_base = M._norm_ppf(1.0 - p_over_raw)
        for offset, role in ((0.0, "baseline total"), (-step, "alternate low"), (step, "alternate high")):
            line_total = round(tot_base + offset, 1)
            p_over = 1.0 - M._norm_cdf(z_base + (line_total - tot_base) / tot_sigma)
            p_over = min(max(p_over, 0.02), 0.98)
            markets.append({"key": f"total_{role[-3:]}", "name": f"Match Total ({cfg['total_name']})",
                            "line": f"{line_total:.1f}", "role": role,
                            "outcomes": [M._outcome(f"Over {line_total:.1f}", p_over),
                                         M._outcome(f"Under {line_total:.1f}", 1.0 - p_over)],
                            "basis": f"Competition baseline {tot_base:.1f} (sigma={tot_sigma:.1f})"})

    # -------- selection logic --------------------------------------------------
    verdict = e["verification"]["verdict"]
    winner_pick = "Draw" if (cfg["draws"] and p_draw >= max(p_home, p_away)) else (
        e["home"] if p_home >= p_away else e["away"])
    winner_out = next(o for o in winner_outcomes if o["selection"] == winner_pick)

    in_band_ml = HIGH_P_MIN <= winner_out["probability"] <= HIGH_P_MAX
    band_rung_p = band_rung[0] if band_rung else None

    if band_rung and band_rung_p >= winner_out["probability"] - 1e-9 and not in_band_ml:
        sel_p, sel_mk = band_rung
        sel_out = max(sel_mk["outcomes"], key=lambda o: o["probability"])
        pick = {"selection": sel_out["selection"], "market": sel_mk["name"],
                "line": sel_mk["line"], "probability": sel_out["probability"],
                "fair_odds": sel_out["fair_odds"], "fair_american": sel_out["fair_american"],
                "odds": sel_out["odds"], "american": sel_out["american"],
                "basis": "in-band handicap rung"}
    else:
        pick = {"selection": winner_pick, "market": "Match Winner", "line": "",
                "probability": winner_out["probability"], "fair_odds": winner_out["fair_odds"],
                "fair_american": winner_out["fair_american"], "odds": winner_out["odds"],
                "american": winner_out["american"], "basis": "moneyline"}

    above_window = verdict == "verified" and both_verified and p_best >= 0.70 and not (
        in_band_ml or (band_rung is not None))

    # -------- confidence -------------------------------------------------------
    reasons = []
    if verdict == "pending":
        conf = "low"; reasons.append(f"fixture verdict 'pending' caps Low")
    elif not both_rated:
        conf = "low"; reasons.append("one/both sides lack a measured rating")
    elif verdict == "verified" and both_verified and in_band_ml:
        conf = "high"; reasons.append("moneyline sits in the zero-vig high band at >=70%")
        pick["band"] = "zero-vig"
    elif verdict == "verified" and both_verified and band_rung and pick.get("band") != "zero-vig":
        conf = "high"; reasons.append("in-band handicap rung at >=70% (both ratings official)")
    elif p_best >= cfg["med"]:
        conf = "medium"
        if above_window:
            reasons.append("above-window: strongest view prices shorter than the -250 floor on the vig-free line")
        else:
            reasons.append("separation clears the medium floor")
    else:
        conf = "low"; reasons.append("model separation below medium floor")

    # niche/global favourite price cap on our own book price (rule 7 of project)
    # (an above-window row is a Window Report publication, not a window pick - T55)
    if conf != "high" and not above_window:
        cap = -150 if sport in NICHE else -190
        val = M.american_value(pick["odds"])
        if val < cap:
            conf = "low"; reasons.append(f"pick price {val} breaches the {'niche -150' if sport in NICHE else 'global -190'} cap")

    if rating_tier == "cross-checked" and conf == "high":
        conf = "medium"; reasons.append("High requires governing-body-verified ratings on both sides")

    return {
        "id": e["id"], "sport": sport, "favourite": winner_pick if winner_out["selection"] != "Draw" else
            (e["home"] if p_home >= p_away else e["away"]),
        "home_probability": round(p_home, 4), "draw_probability": round(p_draw, 4),
        "away_probability": round(p_away, 4),
        "expected_margin": round(margin, 2),
        "rating_home": r_home, "rating_away": r_away, "rating_tier": rating_tier,
        "both_verified": both_verified,
        "pick": pick, "confidence": conf, "above_window": above_window,
        "reasons": reasons, "markets": markets,
    }


def main():
    fx = json.loads((DATA / "fixtures.json").read_text())
    priced, listings = [], []
    for e in fx["events"]:
        if e["sport"] in EVENT_ONLY or e["id"].startswith(("f1-", "golf-")):
            listings.append({"id": e["id"], "sport": e["sport"], "competition": e["competition"],
                             "home": e["home"], "away": e["away"], "note": "event/outright listing - not priced (no per-runner ratings matrix read this session)"})
            continue
        priced.append(price_event(e))
    out = {
        "desk": "f1c13c19", "model_version": "t56-zero-vig-band-v1",
        "high_rule": ">=70.0% AND zero-vig fair price inside -250..+10000, both ratings official-verified",
        "stats": {
            "events_priced": len(priced),
            "high": sum(1 for p in priced if p["confidence"] == "high"),
            "medium": sum(1 for p in priced if p["confidence"] == "medium"),
            "low": sum(1 for p in priced if p["confidence"] == "low"),
            "above_window": sum(1 for p in priced if p["above_window"]),
            "event_listings": len(listings),
        },
        "lines": priced, "event_listings": listings,
    }
    (DATA / "lines.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(json.dumps(out["stats"], indent=1))


if __name__ == "__main__":
    main()
