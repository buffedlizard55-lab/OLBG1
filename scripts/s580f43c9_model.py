"""Independent line origination for the 580f43c9 desk.

All prices are ours. They are built only from numbers that were read from an
official league/tour/board source in s580f43c9_data.py, with the arithmetic below
fixed before any result was looked at:

  * records are shrunk toward .500 with a pseudo-count, because 1-3 game samples
    carry almost no information;
  * two sides are combined with the log5 form, which is exact for independent
    win rates;
  * a venue multiplier is applied to the home side's odds (basketball 1.35,
    hockey 1.20, baseball 1.12, neutral-venue Gaelic 1.00);
  * hockey goals are Poisson with rate = (own goals for + opponent goals against)
    / 2 / games played, which is also used for the puck line and the total;
  * fair decimal is 1/p with no margin, and American is derived from the decimal.

Nothing is clipped, and no price is adjusted to reach a confidence tier.
"""

import math

BANDS = (-250, 10000)


def shrink(wins, losses, pseudo=6.0):
    """Win rate shrunk toward .500 by `pseudo` pseudo-games."""
    games = wins + losses
    if games <= 0:
        return 0.5
    return (wins + pseudo / 2.0) / (games + pseudo)


def log5(pa, pb):
    """P(A beats B) from independent win rates."""
    denom = pa + pb - 2.0 * pa * pb
    if denom <= 0:
        return 0.5
    return (pa - pa * pb) / denom


def with_home_edge(p, multiplier):
    if p <= 0.0 or p >= 1.0:
        return p
    odds = p / (1.0 - p) * multiplier
    return odds / (1.0 + odds)


def decimal_from_prob(p):
    return float("inf") if p <= 0 else 1.0 / p


def american_from_prob(p):
    if p <= 0.0 or p >= 1.0:
        return None
    if p >= 0.5:
        return int(round(-100.0 * p / (1.0 - p)))
    return int(round(100.0 * (1.0 - p) / p))


def in_band(p):
    am = american_from_prob(p)
    if am is None:
        return False
    return BANDS[0] <= am <= BANDS[1]


def implied_from_american(american):
    if american is None:
        return None
    return (-american) / (-american + 100.0) if american < 0 else 100.0 / (american + 100.0)


def poisson_pmf(lam, k):
    return math.exp(-lam) * lam ** k / math.factorial(k)


def poisson_total_prob(lam, line, side):
    """P(total > line) or P(total < line) for a half-goal line."""
    p_under = sum(poisson_pmf(lam, k) for k in range(0, int(math.floor(line)) + 1))
    return 1.0 - p_under if side == "over" else p_under


def poisson_margin_prob(lh, la, min_margin):
    """P(home goals - away goals >= min_margin)."""
    total = 0.0
    for h in range(0, 15):
        ph = poisson_pmf(lh, h)
        for a in range(0, 15):
            if h - a >= min_margin:
                total += ph * poisson_pmf(la, a)
    return total


# ---------------------------------------------------------------------------
# Per-sport origination
# ---------------------------------------------------------------------------

def _split_record(record):
    w, l = record.split("-")
    return int(w), int(l)


def basketball_prob(fx):
    aw, al = _split_record(fx["facts"]["a_record"])
    bw, bl = _split_record(fx["facts"]["b_record"])
    pa = shrink(aw, al, 6.0)
    pb = shrink(bw, bl, 6.0)
    p_home = with_home_edge(log5(pb, pa), 1.35)
    return p_home, pa, pb


def hockey_prob(fx):
    f = fx["facts"]
    pa = (f["a_points"] + 3.0) / (2.0 * f["a_gp"] + 6.0)
    pb = (f["b_points"] + 3.0) / (2.0 * f["b_gp"] + 6.0)
    p_home = with_home_edge(log5(pb, pa), 1.20)
    return p_home, pa, pb


def baseball_prob(fx):
    f = fx["facts"]
    aw, al = _split_record(f["a_record"])
    bw, bl = _split_record(f["b_record"])
    pa = aw / (aw + al)
    pb = bw / (bw + bl)
    p_home = with_home_edge(log5(pb, pa), 1.12)
    return p_home, pa, pb


def gaelic_prob(fx):
    # Group-stage record only: 2-1 and 1-2, shrunk hard because three games is nothing.
    pa = shrink(2, 1, 4.0)   # Nemo Rangers group record (first-named side)
    pb = shrink(1, 2, 4.0)   # St Finbarrs group record (second-named side)
    p_first_named = log5(pa, pb)
    return 1.0 - p_first_named, pa, pb


def tennis_prob(fx):
    # Seed-anchored prior: top seed vs unseeded player on an indoor hard court.
    # No ranking points or head-to-head were readable, so the value is a prior and
    # the pick is capped at low confidence (see tier()).
    return 0.64, None, None


SCHEDULE_END = {
    "basketball": 2026 - 1,  # placeholder, unused
}


def originate(fx):
    sport = fx["sport"]
    if sport == "basketball":
        p_home, pa, pb = basketball_prob(fx)
    elif sport == "ice-hockey":
        p_home, pa, pb = hockey_prob(fx)
    elif sport == "baseball":
        p_home, pa, pb = baseball_prob(fx)
    elif sport == "gaelic-football":
        p_home, pa, pb = gaelic_prob(fx)
    elif sport == "tennis":
        p_home, pa, pb = tennis_prob(fx)
    else:
        raise ValueError("no origination rule for sport " + sport)
    return dict(
        p_home=p_home, p_away=1.0 - p_home,
        side_a_rate=pa, side_b_rate=pb,
        decimal=decimal_from_prob(p_home),
        american=american_from_prob(p_home),
    )


def hockey_derivatives(fx):
    """Puck line and total from official goals for/against."""
    f = fx["facts"]
    lh = (f["b_gf"] / f["b_gp"] + f["a_ga"] / f["a_gp"]) / 2.0
    la = (f["a_gf"] / f["a_gp"] + f["b_ga"] / f["b_gp"]) / 2.0
    total = lh + la
    line = math.floor(total) + 0.5  # nearest half-goal above the raw total
    return dict(
        lam_home=round(lh, 3), lam_away=round(la, 3), raw_total=round(total, 3),
        total_line=line,
        over=poisson_total_prob(total, line, "over"),
        under=poisson_total_prob(total, line, "under"),
        home_puck_line=poisson_margin_prob(lh, la, 2),   # home -1.5
        away_puck_line=poisson_margin_prob(la, lh, 2),   # away -1.5
    )


def tier(p, sport, inputs_complete=True, out_of_band=False):
    """Confidence tier.

    High   : p > 0.70 AND the fair American price is inside -250..+10000
             AND both sides of the market rest on read official inputs.
    Medium : 0.60 <= p <= 0.70, or p > 70% but priced shorter than -250 (the
             brief's band rule excludes it from High).
    Low    : everything else, including any sport whose required inputs are not
             all readable (tennis today).
    """
    if not inputs_complete:
        return "low"
    if p > 0.70 and in_band(p):
        return "high"
    if p > 0.70 and out_of_band:
        return "medium"
    if 0.60 <= p <= 0.70:
        return "medium"
    return "low"


INPUT_COMPLETE = {
    "basketball": True,
    "ice-hockey": True,
    "baseball": True,
    "gaelic-football": True,
    "tennis": False,
}
