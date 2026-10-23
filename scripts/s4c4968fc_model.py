#!/usr/bin/env python3
"""Session 4c4968fc — zero-vig line origination and confidence grading.

Policy
------
* Every two-sided market is priced as a complementary pair, so each market sums
  to exactly 1.000 with no margin. Decimal is 1/p; American is derived from the
  decimal with no rounding drift.
* High confidence requires the conjunction in the brief: estimated strike rate
  greater than 0.70 *and* an originated fair American price inside the
  -250 .. +10000 band. Because a probability above 0.70 implies a price at or
  shorter than about -233, every High selection necessarily lands near the
  -250 end of that band; anything shorter than -250 (probability above 0.7143)
  is suppressed from High and disclosed, never promoted.
* Confidence tiers: High (0.70 < p and in band), Medium (0.50 <= p <= 0.70),
  Low (p < 0.50 or out of band).
* Lines are ours. Spread and total ladders are published at half-point or
  single-unit intervals around the desk's expected margin and total; the
  "desk line" is the rung nearest the expected value.
"""
from __future__ import annotations

import math

BAND_MIN = -250.0
BAND_MAX = 10000.0
HIGH_FLOOR = 0.70
BAND_P_MAX = 250.0 / 350.0      # 0.7142857...
BAND_P_MIN = 100.0 / 10100.0    # 0.00990099...


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def american_from_p(p: float) -> int:
    p = min(max(p, 1e-6), 1 - 1e-6)
    dec = 1.0 / p
    if dec >= 2.0:
        return int(round((dec - 1.0) * 100.0))
    return -int(round(100.0 / (dec - 1.0)))


def fmt_american(p: float) -> str:
    a = american_from_p(p)
    return f"+{a}" if a > 0 else str(a)


def in_band(p: float) -> bool:
    """Band applies to the unrounded fair American price."""
    if p >= 0.5:
        dec = 1.0 / p
        am = -100.0 / (dec - 1.0)          # negative, continuous
        return BAND_MIN <= am              # -250 <= am  (am is negative)
    dec = 1.0 / p
    am = (dec - 1.0) * 100.0
    return am <= BAND_MAX


def tier_for(p: float) -> str:
    """High needs the conjunction; chalk outside the band stays Medium."""
    if p > HIGH_FLOOR and in_band(p):
        return "High"
    if p >= 0.50:
        return "Medium"
    return "Low"


# ---------------------------------------------------------------------------
# sport parameters used when a fixture does not carry its own
# ---------------------------------------------------------------------------
DEFAULT_NORMAL = {
    "ice-hockey": dict(margin_scale=3.2, margin_sigma=2.0, total_base=5.9, total_sigma=1.55, total_slope=0.0, unit="goals"),
    "baseball": dict(margin_scale=3.4, margin_sigma=3.1, total_base=8.3, total_sigma=3.0, total_slope=0.0, unit="runs"),
    "basketball": dict(margin_scale=22.0, margin_sigma=12.5, total_base=224.0, total_sigma=18.0, total_slope=0.0, unit="points"),
    "rugby-union": dict(margin_scale=30.0, margin_sigma=14.0, total_base=48.0, total_sigma=12.0, total_slope=0.0, unit="points"),
    "rugby-league": dict(margin_scale=30.0, margin_sigma=16.0, total_base=44.0, total_sigma=13.0, total_slope=0.0, unit="points"),
    "cricket": dict(margin_scale=34.0, margin_sigma=34.0, total_base=300.0, total_sigma=40.0, total_slope=0.0, unit="runs"),
    "darts": dict(margin_scale=6.0, margin_sigma=3.2, total_base=17.0, total_sigma=3.0, total_slope=0.0, unit="legs"),
    "snooker": dict(margin_scale=3.4, margin_sigma=1.9, total_base=10.0, total_sigma=1.8, total_slope=0.0, unit="frames"),
    "handball": dict(margin_scale=8.0, margin_sigma=6.0, total_base=61.0, total_sigma=7.0, total_slope=0.0, unit="goals"),
    "gaelic-sports": dict(margin_scale=10.0, margin_sigma=6.5, total_base=30.0, total_sigma=6.0, total_slope=0.0, unit="points"),
}

HANDICAP_CAP = {"ice-hockey": 3.5, "baseball": 4.0, "basketball": 24.0, "rugby-union": 22.0,
                "rugby-league": 24.0, "cricket": 40.0, "darts": 4.5, "snooker": 3.0,
                "handball": 9.5, "gaelic-sports": 8.5}

# Rung spacing. Quarter lines (0.25) are the standard Asian-handicap grid and are
# used where a wider grid would leave gaps inside the eligible price band.
STEP = {"ice-hockey": 0.25, "baseball": 1.0, "basketball": 0.5, "rugby-union": 0.25,
        "rugby-league": 0.25, "cricket": 1.0, "darts": 0.25, "snooker": 0.25,
        "handball": 0.25, "gaelic-sports": 0.25}


def _fmt_total(x: float) -> str:
    return f"{int(round(x))}" if abs(x - round(x)) < 1e-9 else f"{x:.2f}".rstrip("0").rstrip(".")


def _fmt_line(x: float) -> str:
    if abs(x - round(x)) < 1e-9:
        v = int(round(x))
        return f"{v:+d}" if v > 0 else f"{v}"
    return f"{x:+.2f}".rstrip("0").rstrip(".")


def _normal_markets(fx):
    s = fx["sport"]
    p = fx["params"]
    base = DEFAULT_NORMAL[s]
    ms = p.get("margin_scale", base["margin_scale"])
    mσ = p.get("margin_sigma", base["margin_sigma"])
    tb = p.get("total_base", base["total_base"])
    tσ = p.get("total_sigma", base["total_sigma"])
    tslope = p.get("total_slope", base["total_slope"])
    unit = p.get("unit", base["unit"])
    step = STEP.get(s, 0.5)

    pa = fx["p_first"]
    pb = 1.0 - pa
    mu_m = ms * (pa - pb)
    mu_t = tb + tslope * (pa - pb)

    out = []

    def add(market, line, sel, prob, note=""):
        out.append(dict(fixture=fx["id"], sport=s, market=market, line=line,
                        selection=sel, p=round(prob, 6),
                        decimal=round(1.0 / prob, 4) if prob > 0 else None,
                        american=american_from_p(prob), american_str=fmt_american(prob),
                        tier=tier_for(prob), note=note))

    # --- match winner (two-way, complementary)
    add("Match winner", "", fx["a"], pa, "zero-vig complementary pair")
    add("Match winner", "", fx["b"], pb, "zero-vig complementary pair")

    # --- handicap / spread ladder
    span = min(ms * 1.6 + 2 * step, HANDICAP_CAP.get(s, 20.0))
    h = -round(span / step) * step
    while h <= round(span / step) * step + 1e-9:
        pl = 1.0 - norm_cdf((0.0 - (mu_m + h)) / mσ)     # a covers h
        if 0.02 < pl < 0.98:
            add("Handicap", f"{fx['a']} {_fmt_line(h)}", fx["a"], pl,
                "desk handicap ladder")
            add("Handicap", f"{fx['b']} {_fmt_line(-h)}", fx["b"], 1.0 - pl,
                "desk handicap ladder")
        h = round(h + step, 4)

    # --- match total ladder
    span_t = tσ * 1.8 + 2 * step
    span_t = min(span_t, max(6 * step, tσ * 1.8))
    lo = mu_t - span_t
    hi = mu_t + span_t
    L = round(lo / step) * step
    while L <= hi + 1e-9:
        ov = 1.0 - norm_cdf((L - mu_t) / tσ)
        if 0.02 < ov < 0.98:
            add("Match total", f"Over {_fmt_total(L)} {unit}", "Over", ov, "desk total ladder")
            add("Match total", f"Under {_fmt_total(L)} {unit}", "Under", 1.0 - ov, "desk total ladder")
        L = round(L + step, 4)

    # --- team totals (each side's own score line)
    for team, mu_team in ((fx["a"], (mu_t + mu_m) / 2.0), (fx["b"], (mu_t - mu_m) / 2.0)):
        sigma_team = tσ / math.sqrt(2.0)
        for off in (-1.75, -1.5, -1.25, -1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75):
            L = round((mu_team + off) / step) * step
            if L <= 0:
                continue
            ov = 1.0 - norm_cdf((L - mu_team) / sigma_team)
            if 0.05 < ov < 0.95:
                add("Team total", f"{team} over {_fmt_total(L)} {unit}", f"{team} over", ov,
                    "desk team-total rung")
                add("Team total", f"{team} under {_fmt_total(L)} {unit}", f"{team} under", 1.0 - ov,
                    "desk team-total rung")
    return out


def _tennis_markets(fx):
    """Best-of-three sets. p_first is the match probability."""
    out = []
    s = fx["sport"]
    pa = fx["p_first"]

    # find per-set probability p such that P(win best of 3) = pa
    def match_prob(ps):
        return ps * ps * (3 - 2 * ps)

    lo, hi = 0.01, 0.99
    for _ in range(80):
        mid = (lo + hi) / 2
        if match_prob(mid) < pa:
            lo = mid
        else:
            hi = mid
    ps = (lo + hi) / 2

    def add(market, line, sel, prob, note=""):
        out.append(dict(fixture=fx["id"], sport=s, market=market, line=line,
                        selection=sel, p=round(prob, 6), decimal=round(1 / prob, 4),
                        american=american_from_p(prob), american_str=fmt_american(prob),
                        tier=tier_for(prob), note=note))

    add("Match winner", "", fx["a"], pa, "best-of-three conversion")
    add("Match winner", "", fx["b"], 1 - pa, "best-of-three conversion")
    # set handicap: a -1.5 sets = wins 2-0
    p20 = ps * ps
    p21 = 2 * ps * ps * (1 - ps) * 1.0
    add("Set handicap", f"{fx['a']} -1.5 sets", fx["a"], p20, "straight-sets win")
    add("Set handicap", f"{fx['b']} +1.5 sets", fx["b"], 1 - p20, "complement")
    add("Set handicap", f"{fx['b']} -1.5 sets", fx["b"], (1 - ps) ** 2, "straight-sets win")
    add("Set handicap", f"{fx['a']} +1.5 sets", fx["a"], 1 - (1 - ps) ** 2, "complement")
    # total sets
    p_2 = ps * ps + (1 - ps) ** 2
    add("Total sets", "Over 2.5 sets", "Over", 1 - p_2, "three-set match")
    add("Total sets", "Under 2.5 sets", "Under", p_2, "two-set match")

    # total games ladder: two tight sets is a short match, three sets a long one
    g_base, g_sigma = 22.5, 4.0
    g_mu = g_base + 2.2 * (1 - p_2)
    L = round((g_mu - 9.0) * 4) / 4
    while L <= g_mu + 9.0 + 1e-9:
        ov = 1.0 - norm_cdf((L - g_mu) / g_sigma)
        if 0.04 < ov < 0.96:
            add("Total games", f"Over {_fmt_total(L)} games", "Over", ov, "desk games ladder")
            add("Total games", f"Under {_fmt_total(L)} games", "Under", 1 - ov, "desk games ladder")
        L = round(L + 0.25, 4)
    return out


def _volleyball_markets(fx):
    """Best-of-five sets."""
    out = []
    s = fx["sport"]
    pa = fx["p_first"]

    def match_prob(ps):
        # P(win race to 3)
        return sum(math.comb(2 + k, k) * ps ** 3 * (1 - ps) ** k for k in range(0, 3))

    lo, hi = 0.01, 0.99
    for _ in range(80):
        mid = (lo + hi) / 2
        if match_prob(mid) < pa:
            lo = mid
        else:
            hi = mid
    ps = (lo + hi) / 2

    def add(market, line, sel, prob, note=""):
        out.append(dict(fixture=fx["id"], sport=s, market=market, line=line,
                        selection=sel, p=round(prob, 6), decimal=round(1 / prob, 4),
                        american=american_from_p(prob), american_str=fmt_american(prob),
                        tier=tier_for(prob), note=note))

    add("Match winner", "", fx["a"], pa, "best-of-five conversion")
    add("Match winner", "", fx["b"], 1 - pa, "best-of-five conversion")
    p30 = ps ** 3
    p31 = 3 * ps ** 3 * (1 - ps)
    add("Set handicap", f"{fx['a']} -2.5 sets", fx["a"], p30, "3-0 win")
    add("Set handicap", f"{fx['b']} +2.5 sets", fx["b"], 1 - p30, "complement")
    add("Set handicap", f"{fx['b']} -2.5 sets", fx["b"], (1 - ps) ** 3, "0-3 win")
    add("Set handicap", f"{fx['a']} +2.5 sets", fx["a"], 1 - (1 - ps) ** 3, "complement")
    p_four = 1 - p30 - p31 - (1 - ps) ** 3 - 3 * ps * (1 - ps) ** 3
    add("Total sets", "Over 3.5 sets", "Over", p_four, "four or five sets")
    add("Total sets", "Under 3.5 sets", "Under", 1 - p_four, "three sets")

    # total points ladder
    pt_base, pt_sigma = 168.0, 13.0
    pt_mu = pt_base + 10.0 * (p_four - 0.55)
    L = round((pt_mu - 30.0) * 4) / 4
    while L <= pt_mu + 30.0 + 1e-9:
        ov = 1.0 - norm_cdf((L - pt_mu) / pt_sigma)
        if 0.04 < ov < 0.96:
            add("Total points", f"Over {_fmt_total(L)} points", "Over", ov, "desk points ladder")
            add("Total points", f"Under {_fmt_total(L)} points", "Under", 1 - ov, "desk points ladder")
        L = round(L + 0.25, 4)
    return out


def _matchup_markets(fx):
    """Two-way head-to-head (golf 72-hole matchup, F1 head-to-head)."""
    out = []
    s = fx["sport"]
    pa = fx["p_first"]
    if s == "golf":
        unit = "strokes"
        step = 0.5
    else:
        unit = "position"
        step = 0.5

    def add(market, line, sel, prob, note=""):
        out.append(dict(fixture=fx["id"], sport=s, market=market, line=line,
                        selection=sel, p=round(prob, 6), decimal=round(1 / prob, 4),
                        american=american_from_p(prob), american_str=fmt_american(prob),
                        tier=tier_for(prob), note=note))

    add("Head-to-head", "level", fx["a"], pa, "outright matchup")
    add("Head-to-head", "level", fx["b"], 1 - pa, "outright matchup")
    # handicap ladder
    sigma = 3.0 if s == "golf" else 2.0
    mu = (pa - 0.5) * 2 * (2.0 if s == "golf" else 1.2)
    h = -6.0
    while h <= 6.0 + 1e-9:
        pl = 1.0 - norm_cdf((0.0 - (mu + h)) / sigma)
        if 0.02 < pl < 0.98:
            add("Matchup handicap", f"{fx['a']} {_fmt_line(h)} {unit}", fx["a"], pl, "desk matchup handicap")
            add("Matchup handicap", f"{fx['b']} {_fmt_line(-h)} {unit}", fx["b"], 1 - pl, "desk matchup handicap")
        h = round(h + step, 4)
    return out


def build_markets(fixtures):
    rows = []
    for fx in fixtures:
        p = fx["params"]
        if p.get("sets") and fx["sport"] == "tennis":
            rows.extend(_tennis_markets(fx))
        elif p.get("sets") and fx["sport"] == "volleyball":
            rows.extend(_volleyball_markets(fx))
        elif p.get("set_model"):
            rows.extend(_tennis_markets(fx))
        elif p.get("matchup"):
            rows.extend(_matchup_markets(fx))
        else:
            rows.extend(_normal_markets(fx))
    return rows


def select_picks(rows, fixtures, limit=5):
    """Highest-probability High selections, up to `limit` per sport."""
    fx_by_id = {f["id"]: f for f in fixtures}
    highs = [r for r in rows if r["tier"] == "High"]
    by_sport = {}
    for r in highs:
        by_sport.setdefault(r["sport"], []).append(r)
    picks = []
    for sport, rs in by_sport.items():
        # prefer the rung closest to the top of the band, then diversify markets
        rs = sorted(rs, key=lambda r: (-r["p"], r["fixture"], r["market"]))
        chosen, seen = [], set()
        for r in rs:
            key = (r["fixture"], r["market"])
            if key in seen:
                continue
            seen.add(key)
            chosen.append(r)
            if len(chosen) >= limit:
                break
        picks.extend(chosen)
    for r in picks:
        fx = fx_by_id[r["fixture"]]
        r["event"] = f"{fx['a']} v {fx['b']}"
        r["competition"] = fx["comp"]
        r["start"] = fx["start"]
    return picks
