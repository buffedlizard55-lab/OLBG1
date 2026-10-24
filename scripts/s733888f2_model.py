"""Fair-line origination for the 733888f2 desk.

Everything here is an estimate produced by this desk. It is never presented as a
fact and never copied from a bookmaker or from OLBG tip shares.

Formulas (identical for every row, published on methodology.html):

  hockey    strength = (points + 1.0) / (games + 2.0)          [shrinkage to 0.5 pts/game]
            logit(p_home) = 1.5 * (s_home - s_away) + 0.12    [0.12 = home ice, 0 for a neutral site]
  baseball  strength = ln(pct / (1 - pct))                     [Bradley-Terry on season win %]
            logit(p_home) = 1.0 * (s_home - s_away) + 0.20
  rugby     strength = (league points + 1.0) / (games + 2.0)
            logit(p_home) = 0.9 * (s_home - s_away) + 0.10

Prices are margin-free: decimal = 1 / p. No vig is added, so two-way books sum
to 100.0%. A handicap "spread at even money" is derived from the same win
probability with a published per-sport margin sigma:
  hockey 1.9 goals, baseball 3.4 runs, rugby 12 points.
That derivation is an assumption, not a measured distribution, and every row
that uses it says so.

Tiers:
  High    p > 0.70  AND  fair American inside [-250, +10000]
  Strong  p >= 0.70 but outside that band (the band ceiling is -250 = 71.43%)
  Medium  0.55 <= p < 0.70
  Low     p < 0.55
"""
import math

SIGMA = {'ice-hockey': 1.9, 'baseball': 3.4, 'rugby-union': 12.0}
BAND_LO, BAND_HI = -250.0, 10000.0


def logistic(x):
    return 1.0 / (1.0 + math.exp(-x))


def american(p):
    """Fair American price for probability p (no margin)."""
    if p is None or p <= 0 or p >= 1:
        return None
    if p >= 0.5:
        return round(-100.0 * p / (1.0 - p), 0)
    return round(100.0 * (1.0 - p) / p, 0)


def decimal(p):
    return round(1.0 / p, 3)


def implied(p):
    return round(100.0 * p, 1)


def tier(p, am):
    if p > 0.70 and am is not None and BAND_LO <= am <= BAND_HI:
        return 'High'
    if p >= 0.70:
        return 'Strong'
    if p >= 0.55:
        return 'Medium'
    return 'Low'


def in_band(am):
    return am is not None and BAND_LO <= am <= BAND_HI


def _norm_cdf(z):
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def handicap_line(p_home, sigma):
    """Even-money spread for the home side, and the cover probability.

    We invert the normal margin distribution for the line that is closest to a
    coin flip, then state the probability that the home side covers it.
    """
    # margin (home - away) with mean chosen so that P(margin > 0) = p_home
    mu = sigma * _norm_cdf_inv(p_home)
    line = round(-mu * 2.0) / 2.0          # nearest half-point line
    p_cover = 1.0 - _norm_cdf((line - mu) / sigma)
    return line, p_cover


def _norm_cdf_inv(p):
    lo, hi = -6.0, 6.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if _norm_cdf(mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def model_hockey(inp):
    a, h = inp['away'], inp['home']
    sa = (a['points'] + 1.0) / (a['gp'] + 2.0)
    sh = (h['points'] + 1.0) / (h['gp'] + 2.0)
    home_edge = 0.0 if inp.get('neutral') else 0.12
    ph = logistic(1.5 * (sh - sa) + home_edge)
    return ph


def model_baseball(inp):
    a, h = inp['away'], inp['home']
    sa = math.log(a['pct'] / (1 - a['pct']))
    sh = math.log(h['pct'] / (1 - h['pct']))
    return logistic(1.0 * (sh - sa) + 0.20)


def model_rugby(inp):
    def s(row):
        pts = row['points']
        gp = int(row['table'].split()[0].lstrip('P'))
        return (pts + 1.0) / (gp + 2.0)
    return logistic(0.9 * (s(inp['home']) - s(inp['away'])) + 0.10)


MODELS = {'ice-hockey': model_hockey, 'baseball': model_baseball,
          'rugby-union': model_rugby}


def price_match(match):
    """Return the priced card for one match, or None when inputs are missing."""
    sport = match['sport']
    if sport not in MODELS or not match.get('inputs'):
        return None
    inp = dict(match['inputs'])
    inp['neutral'] = bool(match.get('neutral', False))
    ph = MODELS[sport](inp)
    pa = 1.0 - ph
    out = {'sport': sport, 'home': match['home'], 'away': match['away'],
           'p_home': ph, 'p_away': pa,
           'market_winner': {'home': {'p': ph, 'american': american(ph), 'decimal': decimal(ph)},
                             'away': {'p': pa, 'american': american(pa), 'decimal': decimal(pa)}}}
    line, p_cover = handicap_line(ph, SIGMA[sport])
    out['market_handicap'] = {'line': line, 'p_home_covers': p_cover,
                              'home_american': american(p_cover),
                              'away_american': american(1 - p_cover),
                              'sigma': SIGMA[sport],
                              'basis': 'structural estimate from the win probability'}
    # Pick = the stronger side.
    side = 'home' if ph >= pa else 'away'
    p = ph if side == 'home' else pa
    am = american(p)
    out['pick'] = {'side': side,
                   'selection': match[side],
                   'opponent': match['away' if side == 'home' else 'home'],
                   'market': 'Moneyline (match winner)',
                   'p': p, 'american': am, 'decimal': decimal(p),
                   'implied_pct': implied(p),
                   'tier': tier(p, am), 'in_band': in_band(am)}
    return out
