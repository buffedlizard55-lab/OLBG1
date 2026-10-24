"""Line-origination arithmetic for the 99d43605 desk (T99D4).

Every input is a number read from an official league/federation page during this
session (2026-10-24).  No bookmaker price is used as an input; partner prices
printed on official league pages are quoted only as context, never as inputs.

Pricing rule (matches the canonical desk convention):
  * season records are shrunk with a Beta(2,2) prior, then paired with a log5
    comparison;
  * no home-ice/court adjustment, no market adjustment, no memory input;
  * a probability p is published as a *fair* (zero-margin) price: decimal = 1/p,
    so a two-way book always sums to exactly 1.

High-confidence gate (the brief's intersection, which is deliberately narrow):
  * our own estimate must be strictly above 0.70, AND
  * the fair American price must land inside -250 .. +10000  (decimal 1.40..101),
  * both sides of the match must carry officially measured inputs, AND
  * the fixture must be upcoming at build time.

Because a fair price of exactly -250 corresponds to p ~= 0.71429, the only
eligible High window is 0.70 < p <= 0.71429 (fair prices roughly -234 to -250).
Estimates above that ceiling are published as Medium with an explicit
"price would be shorter than -250" flag.  Nothing is stretched into High.
"""

import math

BAND_MIN_DECIMAL = 1.4      # fair -250
BAND_MAX_DECIMAL = 101.0    # fair +10000
BAND_MAX_PROB = 1 / BAND_MIN_DECIMAL   # 0.714285...
HIGH_FLOOR = 0.70           # brief: clear favorite, strictly above 70%
MEDIUM_FLOOR = 0.55         # published working cut, documented on methodology page


def american_from_prob(p):
    if p is None:
        return None
    if not 0 < p < 1:
        raise ValueError("probability must be strictly between 0 and 1")
    dec = 1.0 / p
    if dec >= 2.0:
        return int(round((dec - 1.0) * 100))
    return int(round(-100.0 / (dec - 1.0)))


def decimal_from_prob(p):
    return round(1.0 / p, 6)


def prob_from_american(price):
    if price >= 100:
        return 100.0 / (price + 100.0)
    return -price / (-price + 100.0)


def american_in_band(p):
    """True when the fair American price sits inside the requested window."""
    return BAND_MIN_DECIMAL <= 1.0 / p <= BAND_MAX_DECIMAL


def shrink(wins, games):
    """Beta(2,2) shrinkage of a win share toward 0.5 (canonical convention)."""
    if games is None or games <= 0 or wins is None:
        return None
    return (wins + 2.0) / (games + 4.0)


def log5(pa, pb):
    """Bradley-Terry / Bill James pairing of two shrunken win shares."""
    if pa is None or pb is None:
        return None
    denom = pa * (1 - pb) + pb * (1 - pa)
    if denom <= 0:
        return None
    return pa * (1 - pb) / denom


def two_way(p_a):
    """Fair two-way book: probability, fair decimal and American per side."""
    p_a = round(p_a, 6)
    p_b = round(1 - p_a, 6)
    return [
        dict(prob=p_a, decimal=round(1 / p_a, 6), american=american_from_prob(p_a)),
        dict(prob=p_b, decimal=round(1 / p_b, 6), american=american_from_prob(p_b)),
    ]


def poisson_cdf(lam, k):
    """P(X <= k) for X ~ Poisson(lam)."""
    return sum(math.exp(-lam) * lam ** i / math.factorial(i) for i in range(k + 1))


def total_market(lam_total, line):
    """Under/Over a half-line (e.g. 5.5) from a blended expected total."""
    under = poisson_cdf(lam_total, int(math.floor(line)))
    under = min(max(under, 0.02), 0.98)
    return two_way(under)


def blended_rate(attack_g, attack_gp, defense_ga, defense_gp, clamp=(0.5, 9.0)):
    """Blend one attack's goals/game with the opponent's goals-allowed/game."""
    if min(attack_gp or 0, defense_gp or 0) <= 0:
        return None
    rate = (attack_g / attack_gp + defense_ga / defense_gp) / 2.0
    return min(max(rate, clamp[0]), clamp[1])


def poisson_margin_under(lam_a, lam_b, line):
    """P((A goals) - (B goals) < line) for independent Poisson scores.

    Used to price hockey/basketball-style handicaps: e.g. line=+1.5 on side A
    means P(margin > -1.5) = 1 - P(margin <= -2).
    """
    if lam_a is None or lam_b is None:
        return None
    limit = 25
    pmf_a = [math.exp(-lam_a) * lam_a ** i / math.factorial(i) for i in range(limit + 1)]
    pmf_b = [math.exp(-lam_b) * lam_b ** i / math.factorial(i) for i in range(limit + 1)]
    dist = {}
    for i, pa in enumerate(pmf_a):
        for j, pb in enumerate(pmf_b):
            dist[i - j] = dist.get(i - j, 0.0) + pa * pb
    tail = sum(p for m, p in dist.items() if m < line)
    return min(max(tail, 0.02), 0.98)


def seed_strength(seed):
    """Darts origination: official bracket seed to a rate (documented heuristic)."""
    return 1.0 / float(seed)


def seed_pair(seed_a, seed_b):
    """Win probability from two official tournament seeds."""
    sa, sb = seed_strength(seed_a), seed_strength(seed_b)
    return sa / (sa + sb)


def rugby_points_share(points, games):
    """Top 14 table points on a 0..1 scale (max 5 table points per game),
    then Beta(2,2)-shrunk like any other season win share."""
    if points is None or not games:
        return None
    per_game_01 = (points / 5.0) / games   # 0..1
    return shrink(per_game_01, games)      # shrunk toward 0.5


def tier(prob, *, measured_sides=2, fixture_state="upcoming", market_kind="match",
         partner_conflict=False, short_price=False, manual=None):
    """Confidence tier with explicit downgrade reasons.

    high   : 0.70 < prob <= 0.71429 (fair price -234 to -250), both sides
             measured officially, upcoming fixture.
    medium : 0.55 <= prob <= 0.70 with a priced fair line, OR a prob that is
             too strong for the price window (> 0.71429), OR a priced
             multi-runner/one-sided market (capped), OR a partner-conflict
             downgrade is not applied at prob >= 0.55.
    low    : everything priced below 0.55, partial evidence, or conflicts.
    """
    if manual == "low":
        return "low"
    if prob is None:
        return "low"
    if manual == "medium":
        return "medium"
    if fixture_state != "upcoming":
        return "low"
    if partner_conflict:
        return "low"
    if prob > BAND_MAX_PROB:
        return "medium"   # price would be shorter than -250; demoted + flagged
    if prob > HIGH_FLOOR and measured_sides == 2 and market_kind == "match":
        return "high"
    if prob >= MEDIUM_FLOOR or short_price:
        return "medium" if measured_sides == 2 else "low"
    return "low"
