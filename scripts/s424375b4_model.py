"""T424375B4 — line origination and confidence grading.

Disclosed methodology (every output is an experimental fair price, never a
bookmaker quote):

1. Strength from official records only, with Beta(2,2) shrinkage toward .500:
     no draws:   s = (W + 2) / (W + L + 4)          (NHL: L includes OT losses)
     with draws: s = (W + D/2 + 2) / (M + 4)        (rugby: draws split half)
2. Winner probability is log5:  p_h = s_h(1-s_a) / (s_h(1-s_a) + s_a(1-s_h)).
3. Score-based markets (where official GF/GA or PF/PA rates exist) use paired
   per-game rates  e_h = (GF_h/M_h + GA_a/M_a)/2  and independent Poisson
   scores; the margin is a Skellam difference and the total a Poisson sum.
   Rugby point totals are an approximation (rugby scores are not literally
   Poisson) and every such line is labelled a research model line.
4. Basketball line/total markets are withheld: no official scoring-variance
   input was read this session (see flags).
5. Fair decimal = 1/p; American derived consistently; the −250…+10000 window
   flag uses the unrounded American price. No margin, no clipping.
6. Confidence:
     High   p >= 0.70 AND unrounded fair American within [-250, +10000]
            AND verification class A or B AND a written prediction exists.
     Medium 0.55 <= p < 0.70 (class A/B).
     Low    otherwise (including all class C rows).
   Favourites with p >= 0.70 priced beyond −250 are published separately as
   out-of-window disclosures, never as High picks.
"""
from math import exp, lgamma, log


def poisson(lam, k):
    if lam <= 0:
        return 1.0 if k == 0 else 0.0
    return exp(k * log(lam) - lam - lgamma(k + 1))

from s424375b4_data import RECORDS
from s424375b4_fixtures import FIXTURES


def shrunk(rec, drawless=True):
    if drawless:
        losses = rec['l'] + rec.get('otl', 0)
        return (rec['w'] + 2.0) / (rec['w'] + losses + 4.0)
    m = rec['gp']
    return (rec['w'] + 0.5 * rec.get('d', 0) + 2.0) / (m + 4.0)


def log5(sa, sb):
    num = sa * (1.0 - sb)
    den = num + sb * (1.0 - sa)
    return num / den if den else 0.5


def fair_decimal(p):
    return None if p is None or p <= 0 else 1.0 / p


def fair_american(p):
    if p is None or p <= 0 or p >= 1:
        return None
    if p >= 0.5:
        return -100.0 * p / (1.0 - p)
    return 100.0 * (1.0 - p) / p


def in_window(am):
    """-250..+10000 on the unrounded American price (shorter than -250 excluded)."""
    return am is not None and -250.0 <= am <= 10000.0


def skellam_pmf(lam_a, lam_b, maxk=15):
    """P(A - B = k) for independent Poissons."""
    out = {}
    for k in range(-maxk, maxk + 1):
        s = 0.0
        for ka in range(0, 80):
            kb = ka - k
            if kb < 0:
                continue
            s += poisson(lam_a, ka) * poisson(lam_b, kb)
        out[k] = s
    return out


def poisson_total_over(lam_a, lam_b, line):
    """P(A+B > line) for integer-ish lines ending .5 (no push)."""
    lam = lam_a + lam_b
    kmax = int(line) + 1
    cdf = sum(poisson(lam, k) for k in range(0, kmax))
    return 1.0 - cdf


def obs_market_band(odds_lists):
    """Observed American-quote band from the official NHL feed arrays."""
    flat = [o for lst in odds_lists if lst for o in lst]
    if not flat:
        return None
    return dict(n=len(flat), lo=min(flat), hi=max(flat), quotes=sorted(flat))


ALIAS = {
    'Zalgiris Kaunas': 'Zalgiris',
    'LDLC ASVEL Villeurbanne': 'ASVEL',
    'Fenerbahce Tarfin Istanbul': 'Fenerbahce',
    'Olympiacos Piraeus': 'Olympiacos',
    'Valencia Basket': 'Valencia',
    'Philadelphia 76ers': 'PHI 76ers',
    'Cleveland Cavaliers': 'CLE Cavaliers',
    'Oklahoma City Thunder': 'OKC Thunder',
    'Denver Nuggets': 'DEN Nuggets',
    'Boston Celtics': 'BOS Celtics',
    'New York Knicks': 'NY Knicks',
    'San Antonio Spurs': 'SAS Spurs',
    'Houston Rockets': 'HOU Rockets',
    'Chicago Bulls': 'CHI Bulls',
    'Milwaukee Bucks': 'MIL Bucks',
}


def rec_get(table, name):
    return table.get(name) or table.get(ALIAS.get(name, ''))


def fixture_records(fx):
    """Return (rec_home, rec_away, league_key) using the right record table."""
    comp = (fx.get('competition') or '').lower()
    sp = fx['sport']
    if sp == 'ice-hockey' and comp.startswith('nhl'):
        return (RECORDS['NHL'][abbrev(fx['home'])],
                RECORDS['NHL'][abbrev(fx['away'])], 'NHL', True)
    if sp == 'rugby-union':
        if 'urc' in comp:
            k = 'URC'
        elif 'pro d2' in comp:
            k = 'PROD2'
        elif 'top 14' in comp:
            k = 'TOP14'
        else:
            return (None, None, None, None)
        return (rec_get(RECORDS[k], fx['home']), rec_get(RECORDS[k], fx['away']), k, False)
    if 'euroleague' in comp:
        return (rec_get(RECORDS['EL'], fx['home']), rec_get(RECORDS['EL'], fx['away']), 'EL', True)
    if sp == 'basketball' and 'nba' in comp:
        rh = rec_get(RECORDS['NBA'], fx['home'])
        ra = rec_get(RECORDS['NBA'], fx['away'])
        return (rh, ra, 'NBA', True)
    if sp == 'baseball':
        rh = rec_get(RECORDS['MLB'], fx['home'])
        ra = rec_get(RECORDS['MLB'], fx['away'])
        return (rh, ra, 'MLB', True)
    return (None, None, None, None)


NHL_ABBR = {
    'Nashville Predators': 'NSH', 'Boston Bruins': 'BOS',
    'New York Rangers': 'NYR', 'Toronto Maple Leafs': 'TOR',
    'San Jose Sharks': 'SJS', 'Ottawa Senators': 'OTT',
    'Anaheim Ducks': 'ANA', 'New Jersey Devils': 'NJD',
    'Florida Panthers': 'FLA', 'Pittsburgh Penguins': 'PIT',
    'Los Angeles Kings': 'LAK', 'New York Islanders': 'NYI',
    'Vegas Golden Knights': 'VGK', 'St. Louis Blues': 'STL',
    'Winnipeg Jets': 'WPG', 'Dallas Stars': 'DAL',
    'Minnesota Wild': 'MIN', 'Calgary Flames': 'CGY',
    'Carolina Hurricanes': 'CAR', 'Edmonton Oilers': 'EDM',
    'Utah Mammoth': 'UTA', 'Seattle Kraken': 'SEA',
    'Detroit Red Wings': 'DET', 'Vancouver Canucks': 'VAN',
}


def abbrev(name):
    return NHL_ABBR[name]


def score_rates(rec, key):
    if rec is None or rec.get('gp') in (None, 0):
        return None, None
    if rec.get('pf') is None or rec.get('pa') is None:
        return None, None
    return rec['pf'] / rec['gp'], rec['pa'] / rec['gp']


def build_markets():
    markets = []
    picks = []
    for fx in FIXTURES:
        rh, ra, key, drawless = fixture_records(fx)
        ver = fx['verify']
        cls = ver['klass']
        entry = dict(fixture_id=fx['id'], sport=fx['sport'],
                     competition=fx['competition'], home=fx['home'],
                     away=fx['away'], verify=cls)
        if rh is None or ra is None:
            entry['priced'] = False
            entry['unpriced_reason'] = ('one or both official records not read '
                                        'this session')
            picks.append(dict(fixture_id=fx['id'], sport=fx['sport'], p=None,
                              tier='unpriced', selection=None,
                              reason=entry['unpriced_reason']))
            markets.append(entry)
            continue
        sh = shrunk(rh, drawless)
        sa = shrunk(ra, drawless)
        p_home = log5(sh, sa)
        p_away = 1.0 - p_home
        entry['priced'] = True
        entry['strength'] = dict(home=round(sh, 6), away=round(sa, 6))
        entry['winner'] = []
        for side, p, name in (('home', p_home, fx['home']),
                              ('away', p_away, fx['away'])):
            am = fair_american(p)
            entry['winner'].append(dict(
                side=side, selection=name, p=round(p, 6),
                fair_decimal=round(fair_decimal(p), 4),
                fair_american=round(am, 1),
                in_window=in_window(am)))
        # observed market band (NHL only)
        band = obs_market_band([fx.get('odds_home_us'), fx.get('odds_away_us')])
        if band:
            entry['observed_quote_band'] = band

        # score-based markets
        gh, ga = score_rates(rh, key)
        ah, aa = score_rates(ra, key)
        entry['score_markets'] = []
        if gh is not None and ah is not None:
            exp_home = (gh + aa) / 2.0
            exp_away = (ah + ga) / 2.0
            entry['score_model'] = dict(
                paired_rates=f'home {gh:.3f} for/{ga:.3f} against per game; '
                             f'away {ah:.3f}/{aa:.3f}; expected home {exp_home:.2f} '
                             f'— away {exp_away:.2f}',
                exp_home=round(exp_home, 3), exp_away=round(exp_away, 3))
            sk = skellam_pmf(exp_home, exp_away, maxk=12)
            for line in (-2.5, -1.5, -0.5, 0.5, 1.5, 2.5):
                p_cov = sum(v for k, v in sk.items() if k > line)
                am = fair_american(p_cov)
                entry['score_markets'].append(dict(
                    market='handicap' if key != 'NHL' else 'puck-line',
                    line=line, side='home' if line < 0 else 'home',
                    selection=f"{fx['home']} {line:+}", p=round(p_cov, 6),
                    fair_decimal=round(fair_decimal(p_cov), 4),
                    fair_american=round(am, 1), in_window=in_window(am),
                    label='research model line — not a bookmaker offer'))
            tot_line = round(exp_home + exp_away)
            for line in (tot_line - 1.5, tot_line + 0.5, tot_line + 2.5):
                p_over = poisson_total_over(exp_home, exp_away, line)
                p_under = 1.0 - p_over
                for side, p, sel in (('over', p_over, f'Over {line}'),
                                     ('under', p_under, f'Under {line}')):
                    am = fair_american(p)
                    entry['score_markets'].append(dict(
                        market='total', line=line, side=side, selection=sel,
                        p=round(p, 6), fair_decimal=round(fair_decimal(p), 4),
                        fair_american=round(am, 1), in_window=in_window(am),
                        label='research model line — not a bookmaker offer'))

        # pick: the higher-probability winner side
        best = max(entry['winner'], key=lambda w: w['p'])
        am = best['fair_american']
        p = best['p']
        eligible = (p >= 0.70 and in_window(am) and cls in ('A', 'B'))
        if eligible:
            tier = 'high-eligible'
        elif p >= 0.70:
            tier = 'out-of-window'
        elif p >= 0.55 and cls in ('A', 'B'):
            tier = 'medium'
        else:
            tier = 'low'
        picks.append(dict(
            fixture_id=fx['id'], sport=fx['sport'], selection=best['selection'],
            side=best['side'], p=p, fair_decimal=best['fair_decimal'],
            fair_american=best['fair_american'], in_window=best['in_window'],
            tier=tier, verify=cls,
            market_price_window=(band is not None and
                                 in_window(median_american(band, best['side'],
                                                           fx)))))
        markets.append(entry)
    return markets, picks


def median_american(band, side, fx):
    lst = fx.get('odds_home_us') if side == 'home' else fx.get('odds_away_us')
    if not lst:
        return None
    s = sorted(lst)
    return s[len(s) // 2]


def top_picks_per_sport(picks, n=5):
    out = {}
    priced = [p for p in picks if p.get('p') is not None]
    for p in priced:
        out.setdefault(p['sport'], []).append(p)
    for sp in out:
        out[sp] = sorted(out[sp], key=lambda x: -x['p'])[:n]
    return out


if __name__ == '__main__':
    import json
    markets, picks = build_markets()
    with open('data/424375b4/markets.json', 'w') as f:
        json.dump(markets, f, indent=1)
    with open('data/424375b4/picks.json', 'w') as f:
        json.dump(picks, f, indent=1)
    top = top_picks_per_sport(picks)
    with open('data/424375b4/top5.json', 'w') as f:
        json.dump(top, f, indent=1)
    print('priced fixtures:', sum(1 for m in markets if m.get('priced')))
    print('unpriced:', sum(1 for m in markets if not m.get('priced')))
    for sp, rows in sorted(top.items()):
        print(sp, [(r['selection'], r['p'], r['tier']) for r in rows])
