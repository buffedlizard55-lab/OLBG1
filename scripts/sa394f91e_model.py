"""Independent price origination for the 25 October 2026 desk.

Two documented methods, both driven only by figures read from an official
publisher this session:

NHL  - a shrunk attack/defence rating. Each club's goals for and goals against
       per game are pulled toward the league mean with a ten-game prior, then
       combined attack-vs-defence to give expected goals for each side. 0.18
       goals of home advantage is split evenly. Win, puck-line and total
       probabilities come from a normal approximation (sigma 1.85 on the
       margin, 2.40 on the total).

NBA  - the only officially published input is the win-loss record, two to three
       games old. The record is pulled toward .500 with a twenty-game prior and
       run through a log-5 combination, then shifted by a home-court term.
"""
from __future__ import annotations

import math

# --------------------------------------------------------------------------
# NHL. League average goals per team per game, derived from the 32-club goals-for
# column of https://www.nhl.com/standings/2026-10-24/wildcard (352 team-games).
# --------------------------------------------------------------------------
NHL_GF = {'BOS': 48, 'OTT': 38, 'TOR': 50, 'CAR': 51, 'NYR': 41, 'NJD': 36, 'TBL': 34,
          'WSH': 34, 'NYI': 29, 'MTL': 34, 'FLA': 31, 'DET': 28, 'BUF': 31, 'PIT': 40,
          'PHI': 24, 'CBJ': 22, 'UTA': 41, 'MIN': 32, 'DAL': 26, 'EDM': 49, 'VGK': 47,
          'SEA': 44, 'COL': 47, 'SJS': 37, 'WPG': 26, 'STL': 35, 'NSH': 25, 'ANA': 32,
          'CGY': 19, 'LAK': 21, 'CHI': 22, 'VAN': 35}
NHL_GA = {'BOS': 26, 'OTT': 34, 'TOR': 41, 'CAR': 33, 'NYR': 36, 'NJD': 32, 'TBL': 29,
          'WSH': 32, 'NYI': 23, 'MTL': 35, 'FLA': 34, 'DET': 30, 'BUF': 41, 'PIT': 40,
          'PHI': 42, 'CBJ': 30, 'UTA': 36, 'MIN': 27, 'DAL': 17, 'EDM': 39, 'VGK': 38,
          'SEA': 37, 'COL': 34, 'SJS': 43, 'WPG': 29, 'STL': 35, 'NSH': 33, 'ANA': 37,
          'CGY': 38, 'LAK': 32, 'CHI': 40, 'VAN': 56}
# games played, from the GP column of the same table
NHL_GP = {'BOS': 12, 'OTT': 12, 'TOR': 13, 'CAR': 13, 'NYR': 13, 'NJD': 11, 'TBL': 10,
          'WSH': 10, 'NYI': 10, 'MTL': 10, 'FLA': 11, 'DET': 10, 'BUF': 11, 'PIT': 12,
          'PHI': 13, 'CBJ': 9, 'UTA': 11, 'MIN': 11, 'DAL': 10, 'EDM': 11, 'VGK': 13,
          'SEA': 11, 'COL': 11, 'SJS': 12, 'WPG': 10, 'STL': 11, 'NSH': 10, 'ANA': 11,
          'CGY': 9, 'LAK': 9, 'CHI': 10, 'VAN': 12}

NHL_LEAGUE_GPG = sum(NHL_GF.values()) / sum(NHL_GP.values())   # 3.1506
NHL_PRIOR_GAMES = 10.0
NHL_HOME_ADV = 0.18
NHL_SIGMA_MARGIN = 1.85
NHL_SIGMA_TOTAL = 2.40

NBA_PRIOR_GAMES = 20.0
NBA_HOME_LOGIT = 0.22

# The brief's band, applied as a hard rule.
BAND_LOW, BAND_HIGH = -250, 10000
HIGH_MIN, MEDIUM_MIN = 0.60, 0.55


def _phi(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def american(p: float) -> int:
    p = min(max(p, 1e-6), 1 - 1e-6)
    if p >= 0.5:
        return int(round(-100.0 * p / (1.0 - p)))
    return int(round(100.0 * (1.0 - p) / p))


def in_band(price: int) -> bool:
    return BAND_LOW <= price <= BAND_HIGH


def grade(p: float) -> str:
    price = american(p)
    if not in_band(price):
        return 'none'
    if p >= HIGH_MIN:
        return 'High'
    if p >= MEDIUM_MIN:
        return 'Medium'
    return 'none'


def nhl_ratings(club: str) -> tuple[float, float]:
    gp = NHL_GP[club]
    att = (NHL_GF[club] + NHL_LEAGUE_GPG * NHL_PRIOR_GAMES) / (gp + NHL_PRIOR_GAMES)
    dfn = (NHL_GA[club] + NHL_LEAGUE_GPG * NHL_PRIOR_GAMES) / (gp + NHL_PRIOR_GAMES)
    return att, dfn


def nhl_markets(away: str, home: str) -> dict:
    aatt, adfn = nhl_ratings(away)
    hatt, hdfn = nhl_ratings(home)
    eg_away = aatt * hdfn / NHL_LEAGUE_GPG - NHL_HOME_ADV / 2.0
    eg_home = hatt * adfn / NHL_LEAGUE_GPG + NHL_HOME_ADV / 2.0
    margin = eg_home - eg_away
    total = eg_home + eg_away
    p_home, p_away = _phi(margin / NHL_SIGMA_MARGIN), 1 - _phi(margin / NHL_SIGMA_MARGIN)
    cover_home = 1 - _phi((1.5 - margin) / NHL_SIGMA_MARGIN)
    total_line = 6.0 if total >= 6.0 else 5.5
    p_over = 1 - _phi((total_line - total) / NHL_SIGMA_TOTAL)
    return dict(
        eg_away=round(eg_away, 2), eg_home=round(eg_home, 2),
        exp_total=round(total, 2), margin=round(margin, 2),
        markets=[
            dict(key='moneyline', name='Money Line',
                 line='', outcomes=[
                     dict(name=f'{away} win', prob=round(p_away, 4), price=american(p_away)),
                     dict(name=f'{home} win', prob=round(p_home, 4), price=american(p_home))]),
            dict(key='puckline', name='Puck Line (-1.5 / +1.5)',
                 line='1.5', outcomes=[
                     dict(name=f'{home} -1.5', prob=round(cover_home, 4), price=american(cover_home)),
                     dict(name=f'{away} +1.5', prob=round(1 - cover_home, 4),
                          price=american(1 - cover_home))]),
            dict(key='total', name='Game Total', line=str(total_line), outcomes=[
                dict(name=f'Over {total_line}', prob=round(p_over, 4), price=american(p_over)),
                dict(name=f'Under {total_line}', prob=round(1 - p_over, 4), price=american(1 - p_over))]),
        ])


def nba_markets(away: str, home: str, rec_a: tuple[int, int], rec_h: tuple[int, int]) -> dict:
    def pct(w, l):
        return (w + NBA_PRIOR_GAMES / 2.0) / (w + l + NBA_PRIOR_GAMES)

    pa, ph = pct(*rec_a), pct(*rec_h)
    base = (pa * (1 - ph)) / (pa * (1 - ph) + ph * (1 - pa))
    z = math.log(base / (1 - base)) + NBA_HOME_LOGIT
    p_home = 1.0 / (1.0 + math.exp(-z))
    p_away = 1 - p_home
    return dict(
        markets=[dict(key='moneyline', name='Money Line', line='', outcomes=[
            dict(name=f'{away} win', prob=round(p_away, 4), price=american(p_away)),
            dict(name=f'{home} win', prob=round(p_home, 4), price=american(p_home))])],
        notes='Money line only. No point spread and no game total is published: '
              'no official per-game scoring, pace or rating figure was captured this session, '
              'so a spread or a total would be an invented number.')
