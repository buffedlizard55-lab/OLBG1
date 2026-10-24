"""Our own line arithmetic for the 02d3d515 desk.

No bookmaker price is copied.  A probability we estimate is converted straight
to a fair (zero-vig) price with decimal = 1/p, so the two-way book sums to
exactly 1.  The brief's window is -250 .. +10000, i.e. decimal 1.4 .. 101.
"""
import math

BAND_MIN_DECIMAL = 1.4      # -250
BAND_MAX_DECIMAL = 101.0    # +10000
BAND_MIN_PROB = 1 / BAND_MAX_DECIMAL     # 0.0099
BAND_MAX_PROB = 1 / BAND_MIN_DECIMAL     # 0.7143


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
    return 1.0 / p


def prob_from_american(price):
    if price >= 100:
        return 100.0 / (price + 100.0)
    return -price / (-price + 100.0)


def in_band(p):
    return BAND_MIN_PROB <= p <= BAND_MAX_PROB


def implied_from_american(price):
    return prob_from_american(price)


def poisson_under(lam, line):
    """P(total <= floor(line)) for a half line such as 6.5."""
    k = int(math.floor(line))
    return sum(math.exp(-lam) * lam ** i / math.factorial(i) for i in range(k + 1))


def two_way(p_a):
    """Fair two-way book: [probability, fair decimal, American] per side."""
    p_a = round(p_a, 6)
    p_b = round(1 - p_a, 6)
    return [
        dict(prob=p_a, decimal=round(1 / p_a, 6), american=american_from_prob(p_a)),
        dict(prob=p_b, decimal=round(1 / p_b, 6), american=american_from_prob(p_b)),
    ]


def total_book(expected_total, line):
    under = poisson_under(expected_total, line)
    under = min(max(under, 0.02), 0.98)
    return two_way(under)


def nhl_expected_total(ga_for, ga_against, gb_for, gb_against, games):
    """Blend each attack with the opposing defence; both inputs are official."""
    a_attack = ga_for / games
    b_def = gb_against / games
    b_attack = gb_for / games
    a_def = ga_against / games
    return (a_attack + b_def) / 2 + (b_attack + a_def) / 2


def tier(prob, both_sides, multi_runner=False, manual=None):
    """Confidence tier.

    high   - our own probability is at least 0.58, the fair price sits inside
             the requested window, and both sides of the match carry official
             form data.  (No high tier without a verified opponent.)
    medium - priced inside the window at 0.53-0.58, a short price above the
             -250 floor, or a multi-runner market with a clear official edge.
    low    - everything else, including partial-evidence selections.
    """
    if manual == "low":
        return "low"
    if multi_runner:
        return manual or "low"
    if both_sides and prob is not None and 0.58 <= prob <= BAND_MAX_PROB:
        return "high"
    if prob is not None and prob > BAND_MAX_PROB and both_sides:
        return "medium"          # chalk: real edge, but inside the excluded floor
    if prob is not None and prob >= 0.53:
        return "medium"
    return "low"


def clears_seventy(prob):
    return prob is not None and prob > 0.70
