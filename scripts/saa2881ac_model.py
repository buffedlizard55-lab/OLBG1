"""Independent price origination for the 26 October 2026 desk.

Every input is a figure read this session from an official publisher (see
saa2881ac_data.SOURCES). The modelling constants below (priors, home edges,
spreads) are this desk's own documented assumptions; they are not facts read
from any page and are listed as such on the methodology page.

Grades: a selection is High when its originated probability is at least 0.60
and its fair American price sits inside -250..+10000; Medium at 0.55 to 0.60
inside the band; Low at 0.40 to 0.55 inside the band. Anything else is not
graded and cannot become a pick.
"""
from __future__ import annotations

import math
from functools import lru_cache

import saa2881ac_data as D

BAND_LOW, BAND_HIGH = -250, 10000
HIGH_MIN, MEDIUM_MIN, LOW_MIN = 0.60, 0.55, 0.40


def phi(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def american(p: float) -> int:
    p = min(max(p, 1e-6), 1 - 1e-6)
    if p >= 0.5:
        return int(round(-100.0 * p / (1.0 - p)))
    return int(round(100.0 * (1.0 - p) / p))


def fmt(price: int) -> str:
    return f'+{price}' if price > 0 else str(price)


def in_band(price: int) -> bool:
    return BAND_LOW <= price <= BAND_HIGH


def grade(p: float) -> str:
    if not in_band(american(p)):
        return 'none'
    if p >= HIGH_MIN:
        return 'High'
    if p >= MEDIUM_MIN:
        return 'Medium'
    if p >= LOW_MIN:
        return 'Low'
    return 'none'


def outcome(name, p):
    return dict(name=name, prob=round(p, 4), price=american(p))


# --------------------------------------------------------------------------
# Ice hockey (NHL and DEL): shrunk attack/defence, normal margin and total.
# --------------------------------------------------------------------------
HOCKEY_PRIOR_GAMES = 10.0
HOCKEY_HOME_ADV = 0.18
HOCKEY_SIGMA_MARGIN = 1.85
HOCKEY_SIGMA_TOTAL = 2.40

NHL_LEAGUE_GPG = sum(t['gf'] for t in D.NHL.values()) / sum(t['gp'] for t in D.NHL.values())
DEL_LEAGUE_GPG = sum(r[8] for r in D.DEL.values()) / sum(r[0] for r in D.DEL.values())


def _hockey(gp, gf, ga, mean):
    att = (gf + mean * HOCKEY_PRIOR_GAMES) / (gp + HOCKEY_PRIOR_GAMES)
    dfn = (ga + mean * HOCKEY_PRIOR_GAMES) / (gp + HOCKEY_PRIOR_GAMES)
    return att, dfn


def hockey_markets(away_name, home_name, away_row, home_row, mean):
    """away_row/home_row = (gp, gf, ga)."""
    aatt, adfn = _hockey(*away_row, mean)
    hatt, hdfn = _hockey(*home_row, mean)
    eg_away = aatt * hdfn / mean - HOCKEY_HOME_ADV / 2.0
    eg_home = hatt * adfn / mean + HOCKEY_HOME_ADV / 2.0
    margin, total = eg_home - eg_away, eg_home + eg_away
    p_home = phi(margin / HOCKEY_SIGMA_MARGIN)
    fav_home = margin >= 0
    # puck line: favourite -1.5 / underdog +1.5
    if fav_home:
        cover = 1 - phi((1.5 - margin) / HOCKEY_SIGMA_MARGIN)
        pl = [outcome(f'{home_name} -1.5', cover), outcome(f'{away_name} +1.5', 1 - cover)]
    else:
        cover = phi((-1.5 - margin) / HOCKEY_SIGMA_MARGIN)
        pl = [outcome(f'{away_name} -1.5', cover), outcome(f'{home_name} +1.5', 1 - cover)]
    line = 6.5 if total >= 6.0 else 5.5   # half-goal lines only, so no push
    p_over = 1 - phi((line - total) / HOCKEY_SIGMA_TOTAL)
    return dict(
        exp=dict(away=round(eg_away, 2), home=round(eg_home, 2), total=round(total, 2), margin=round(margin, 2)),
        markets=[
            dict(key='ml', name='Money Line (incl. OT/SO)', outcomes=[
                outcome(f'{away_name} win', 1 - p_home), outcome(f'{home_name} win', p_home)]),
            dict(key='pl', name='Puck Line', outcomes=pl),
            dict(key='tot', name=f'Total Goals {line}', outcomes=[
                outcome(f'Over {line}', p_over), outcome(f'Under {line}', 1 - p_over)]),
        ])


def nhl_markets(away, home):
    a, h = D.NHL[away], D.NHL[home]
    return hockey_markets(a['name'], h['name'], (a['gp'], a['gf'], a['ga']),
                          (h['gp'], h['gf'], h['ga']), NHL_LEAGUE_GPG)


def del_markets(away, home):
    a, h = D.DEL[away], D.DEL[home]
    return hockey_markets(away, home, (a[0], a[8], a[9]), (h[0], h[8], h[9]), DEL_LEAGUE_GPG)


# --------------------------------------------------------------------------
# Baseball: season run rates, blended with the probable starter, normal margin.
# --------------------------------------------------------------------------
MLB_STARTER_SHARE = 5.0 / 9.0
MLB_HOME_RUNS = 0.10
MLB_SIGMA_MARGIN = 4.3
MLB_SIGMA_TOTAL = 4.5
MLB_LEAGUE_RPG = sum(D.MLB['partial_league_runs']) / len(D.MLB['partial_league_runs']) / D.MLB['games']


def mlb_g3():
    g = D.MLB['games']
    mil, tb = D.MLB['MIL'], D.MLB['TB']
    mil_allow = MLB_STARTER_SHARE * D.MLB['gasser']['ra9'] + (1 - MLB_STARTER_SHARE) * mil['ra'] / g
    tb_allow = MLB_STARTER_SHARE * D.MLB['peralta']['ra9'] + (1 - MLB_STARTER_SHARE) * tb['ra'] / g
    exp_mil = mil['rs'] / g * tb_allow / MLB_LEAGUE_RPG - MLB_HOME_RUNS
    exp_tb = tb['rs'] / g * mil_allow / MLB_LEAGUE_RPG + MLB_HOME_RUNS
    margin, total = exp_mil - exp_tb, exp_mil + exp_tb
    p_mil = phi(margin / MLB_SIGMA_MARGIN)
    cover = 1 - phi((1.5 - margin) / MLB_SIGMA_MARGIN)
    line = 8.5
    p_over = 1 - phi((line - total) / MLB_SIGMA_TOTAL)
    return dict(
        exp=dict(away=round(exp_mil, 2), home=round(exp_tb, 2), total=round(total, 2), margin=round(margin, 2)),
        markets=[
            dict(key='ml', name='Money Line', outcomes=[
                outcome('Milwaukee Brewers win', p_mil), outcome('Tampa Bay Rays win', 1 - p_mil)]),
            dict(key='rl', name='Run Line', outcomes=[
                outcome('Milwaukee Brewers -1.5', cover), outcome('Tampa Bay Rays +1.5', 1 - cover)]),
            dict(key='tot', name=f'Total Runs {line}', outcomes=[
                outcome(f'Over {line}', p_over), outcome(f'Under {line}', 1 - p_over)]),
        ])


# --------------------------------------------------------------------------
# Tennis: ranking-points ratio, best of three sets.
# --------------------------------------------------------------------------
def tennis_markets(a, b):
    ra, rb = D.ATP[a], D.ATP[b]
    if ra is None or rb is None:
        return None
    pa = ra[1] / (ra[1] + rb[1])
    # per-set probability s solving p = s^2 (3 - 2s)
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if mid * mid * (3 - 2 * mid) < pa:
            lo = mid
        else:
            hi = mid
    s = (lo + hi) / 2
    fav, dog, sf = (a, b, s) if pa >= 0.5 else (b, a, 1 - s)
    straight = sf * sf
    return dict(
        exp=dict(points_a=ra[1], points_b=rb[1], set_prob_a=round(s, 3)),
        markets=[
            dict(key='ml', name='Match Winner', outcomes=[outcome(f'{a} win', pa), outcome(f'{b} win', 1 - pa)]),
            dict(key='sets', name='Set Handicap 1.5', outcomes=[
                outcome(f'{fav} -1.5 sets (2-0)', straight), outcome(f'{dog} +1.5 sets', 1 - straight)]),
        ])


# --------------------------------------------------------------------------
# Handball: shrunk goal rates, normal margin with an explicit draw band.
# --------------------------------------------------------------------------
HB_PRIOR_GAMES = 3.0
HB_HOME_ADV = 1.5
HB_SIGMA_MARGIN = 5.5
HB_SIGMA_TOTAL = 6.0
EHF_LEAGUE_GPG = sum(r[5] for r in D.EHF.values()) / sum(r[1] for r in D.EHF.values())


def handball_markets(home, away):
    def rate(club):
        r = D.EHF[club]
        att = (r[5] + EHF_LEAGUE_GPG * HB_PRIOR_GAMES) / (r[1] + HB_PRIOR_GAMES)
        dfn = (r[6] + EHF_LEAGUE_GPG * HB_PRIOR_GAMES) / (r[1] + HB_PRIOR_GAMES)
        return att, dfn

    hatt, hdfn = rate(home)
    aatt, adfn = rate(away)
    eg_home = hatt * adfn / EHF_LEAGUE_GPG + HB_HOME_ADV / 2
    eg_away = aatt * hdfn / EHF_LEAGUE_GPG - HB_HOME_ADV / 2
    m, total = eg_home - eg_away, eg_home + eg_away
    p_home = 1 - phi((0.5 - m) / HB_SIGMA_MARGIN)
    p_away = phi((-0.5 - m) / HB_SIGMA_MARGIN)
    p_draw = 1 - p_home - p_away
    hcap = round(abs(m) * 2) / 2
    hcap = max(hcap, 1.5) if hcap % 1 else hcap + 0.5   # always a half-goal line
    fav, dog = (home, away) if m >= 0 else (away, home)
    cover = 1 - phi((hcap - abs(m)) / HB_SIGMA_MARGIN)
    line = math.floor(total) + 0.5
    p_over = 1 - phi((line - total) / HB_SIGMA_TOTAL)
    return dict(
        exp=dict(home=round(eg_home, 1), away=round(eg_away, 1), total=round(total, 1), margin=round(m, 1)),
        markets=[
            dict(key='1x2', name='Match Result (1X2)', outcomes=[
                outcome(f'{home} win', p_home), outcome('Draw', p_draw), outcome(f'{away} win', p_away)]),
            dict(key='hcap', name=f'Handicap {hcap}', outcomes=[
                outcome(f'{fav} -{hcap}', cover), outcome(f'{dog} +{hcap}', 1 - cover)]),
            dict(key='tot', name=f'Total Goals {line}', outcomes=[
                outcome(f'Over {line}', p_over), outcome(f'Under {line}', 1 - p_over)]),
        ])


# --------------------------------------------------------------------------
# Volleyball: rally-point share, shrunk by half, exact set and match maths.
# --------------------------------------------------------------------------
VB_SHRINK = 0.5
VB_HOME_RALLY = 0.005


def _set_prob(q, target):
    """Probability of winning a set to `target` (win by two) on rally prob q."""
    @lru_cache(maxsize=None)
    def f(a, b):
        if a >= target and a - b >= 2:
            return 1.0
        if b >= target and b - a >= 2:
            return 0.0
        if a >= target - 1 and b >= target - 1 and a == b:
            # deuce: win two in a row before losing two in a row
            return q * q / (q * q + (1 - q) * (1 - q))
        return q * f(a + 1, b) + (1 - q) * f(a, b + 1)
    return f(0, 0)


def volleyball_markets(home, away):
    h, a = D.LVF[home], D.LVF[away]
    sh = h[7] / (h[7] + h[8])
    sa = a[7] / (a[7] + a[8])
    q = 0.5 + VB_SHRINK * (sh - sa) + VB_HOME_RALLY
    s, s5 = _set_prob(q, 25), _set_prob(q, 15)
    p30 = s ** 3
    p31 = 3 * s ** 3 * (1 - s)
    p32 = 6 * s ** 2 * (1 - s) ** 2 * s5
    p_home = p30 + p31 + p32
    l30 = (1 - s) ** 3
    l31 = 3 * (1 - s) ** 3 * s
    fav, dog = (home, away) if p_home >= 0.5 else (away, home)
    fav_hcap = p30 + p31 if p_home >= 0.5 else l30 + l31
    return dict(
        exp=dict(rally_q=round(q, 4), set_prob=round(s, 3), share_home=round(sh, 3), share_away=round(sa, 3)),
        markets=[
            dict(key='ml', name='Match Winner', outcomes=[outcome(f'{home} win', p_home), outcome(f'{away} win', 1 - p_home)]),
            dict(key='sets', name='Set Handicap 1.5', outcomes=[
                outcome(f'{fav} -1.5 sets (3-0 or 3-1)', fav_hcap), outcome(f'{dog} +1.5 sets', 1 - fav_hcap)]),
        ])


# --------------------------------------------------------------------------
# Formula 1: smoothed share of 2026 race wins.
# --------------------------------------------------------------------------
F1_ALPHA = 0.5
F1_FIELD_PSEUDO = 2.0


def f1_markets():
    wins = {}
    teams = {}
    for _gp, _date, driver, team in D.F1_WINNERS:
        wins[driver] = wins.get(driver, 0) + 1
        teams[driver] = team
    denom = len(D.F1_WINNERS) + F1_ALPHA * len(wins) + F1_FIELD_PSEUDO
    probs = {d: (w + F1_ALPHA) / denom for d, w in wins.items()}
    field = F1_FIELD_PSEUDO / denom
    merc = sum(p for d, p in probs.items() if teams[d] == 'Mercedes')
    outs = [outcome(f'{d} to win', p) for d, p in sorted(probs.items(), key=lambda x: -x[1])]
    outs.append(outcome('Any other driver to win', field))
    return dict(
        exp=dict(wins=wins, denom=denom),
        markets=[
            dict(key='win', name='Race Winner', outcomes=outs),
            dict(key='team', name='Winning Constructor: Mercedes', outcomes=[
                outcome('A Mercedes driver wins', merc), outcome('Any other team wins', 1 - merc)]),
        ])
