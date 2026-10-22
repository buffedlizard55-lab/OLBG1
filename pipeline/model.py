"""Independent, deliberately experimental prices. No tip-share or market odds input.

No calibration sample has been collected for this implementation. Accordingly ALL
live model outputs are Low confidence; High is withheld, not fabricated by tuning
an alternate handicap to a desired percentage. Unsupported markets remain null.
"""
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP
import math
from .common import parse_time, iso
from .config import STATS_TTL_HOURS, SPORT_MARKETS, MARKET_REQUIREMENTS
from .evidence import fixture_state

MODEL_VERSION = 'evidence-v1.0'
ASSUMPTIONS = {
    'record_model': 'Beta(2,2) shrinkage of season W/L, followed by log5. No home advantage, player adjustment or market input.',
    'nhl_settlement': 'Match winner including overtime and shootout; binary losses = regulation losses + OT/SO losses.',
    'mlb_score_model': 'Independent Poisson final-score approximation, conditioned on unequal scores. Rates average own runs/game and opponent runs-allowed/game. No pitcher, park or postseason adjustment. NOT calibrated.',
    'mlb_handicaps': 'Fixed research lines A -1.5 and A +1.5, never selected to manufacture confidence.',
    'mlb_totals': 'Three half-run research totals centered on floor(sum of expected scores) + 0.5. These are originated lines, NOT observed bookmaker offerings.',
    'confidence': 'Low until temporal out-of-sample calibration, current market quote, and fully sourced form/player/history context are available. A high modeled chance alone does not confer high confidence.',
}


def american_from_decimal(decimal):
    d = Decimal(str(decimal))
    if not d.is_finite() or d <= 1:
        raise ValueError('Decimal odds must be finite and > 1')
    price = (d - 1) * 100 if d >= 2 else -100 / (d - 1)
    return int(price.quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def price(p):
    if isinstance(p, bool) or not math.isfinite(p) or not 0 < p < 1:
        raise ValueError('Non-degenerate probability required')
    raw = 1.0 / p
    displayed = Decimal(str(raw)).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
    # Very small odds cannot be represented at this display precision. Never clamp.
    if displayed <= 1:
        raise ValueError('Price below display resolution')
    return {'probability': p, 'fair_decimal': raw, 'decimal_display': str(displayed),
            'american_display': american_from_decimal(displayed),
            'fair_price_in_target_band': 1.4 <= raw <= 101.0}


def record_ok(r, at):
    if not r:
        return False
    keys = ('wins', 'losses', 'games_played')
    if any(type(r.get(k)) is not int or r[k] < 0 for k in keys):
        return False
    ot = r.get('ot_losses', 0)
    if type(ot) is not int or ot < 0:
        return False
    if r['games_played'] != r['wins'] + r['losses'] + ot or r['games_played'] < 5:
        return False
    if 'points' in r and r['points'] != 2 * r['wins'] + ot:
        return False
    try:
        start = parse_time(r['observed_after'])
        end = parse_time(r['observed_before'])
        from datetime import date
        if date.fromisoformat(r['as_of']) > at.date():
            return False
    except (KeyError, ValueError, TypeError, AttributeError):
        return False
    if start > end or end > at or at - start >= timedelta(hours=STATS_TTL_HOURS):
        return False
    return True


def log5(a, b):
    """Odds-ratio comparison of two beta-posterior means; no one-sided fallback."""
    pa = (a['wins'] + 2) / (a['games_played'] + 4)
    pb = (b['wins'] + 2) / (b['games_played'] + 4)
    return (pa * (1-pb)) / (pa*(1-pb) + pb*(1-pa))


def poisson_vector(rate, max_score=60):
    if not 0 < rate < 20:
        raise ValueError('Rate outside tested baseball model domain')
    values = [math.exp(-rate)]
    for n in range(1, max_score+1):
        values.append(values[-1]*rate/n)
    if 1-sum(values) > 1e-10:
        raise ValueError('Unaccounted score tail')
    return values


def baseball_grid(a, b):
    for r in (a, b):
        if any(type(r.get(k)) is not int or r[k] <= 0 for k in ('runs_scored', 'runs_allowed')):
            raise ValueError('Both verified run aggregates required')
        if r['games_played'] < 30:
            raise ValueError('Thirty games per team required for score approximation')
    la = (a['runs_scored']/a['games_played'] + b['runs_allowed']/b['games_played']) / 2
    lb = (b['runs_scored']/b['games_played'] + a['runs_allowed']/a['games_played']) / 2
    va, vb = poisson_vector(la), poisson_vector(lb)
    pairs = [(i, j, x*y) for i, x in enumerate(va) for j, y in enumerate(vb) if i != j]
    mass = math.fsum(z for _, _, z in pairs)
    return [(i, j, z/mass) for i, j, z in pairs], (la, lb), mass


def two_way(mid, label, selections, probability, source_ids, settlement, **extra):
    return {'id': mid, 'market': label, 'settlement': settlement, 'status': 'experimental',
            'confidence': 'low', 'model_version': MODEL_VERSION,
            'sources': list(dict.fromkeys(source_ids)), 'market_quote': None,
            'quote_status': 'unverified — no bookmaker price captured',
            'outcomes': [{'selection': selections[0], **price(probability)},
                         {'selection': selections[1], **price(1-probability)}], **extra}


def confidence_gate(probability, fair_decimal, calibration=None, quote=None, context=None):
    """Explain the High withholding policy. No unsigned 'calibrated: true' shortcut.

    This version has no validated, temporally held-out calibration artifact and
    cannot issue Medium/High. Updating that is a model-version change with tests,
    not a freeform flag or imported legacy label.
    """
    reasons = ['No validated out-of-sample calibration for '+MODEL_VERSION]
    if not 1.4 <= fair_decimal <= 101.0:
        reasons.append('Originated fair price outside −250…+10000')
    if not quote:
        reasons.append('Available bookmaker price and settlement unverified')
    if not context:
        reasons.append('Current player availability, form and recent match history not all verified')
    return 'low', reasons


def prematch_status_verified(row):
    """Only explicit supported pre-match states qualify; missing is not Scheduled.

    Adapter states are retained in official observations. Do not guess that a new
    provider status code, an unknown value or a blank means a playable fixture.
    """
    states = {
        'NHL': {'FUT', 'PRE'},
        'MLB': {'Scheduled', 'Pre-Game', 'Warmup'},
        'NBA': {'Scheduled'},
        'EuroLeague': {'Scheduled'},
    }
    facts = row['facts']
    return facts.get('official_status') in states.get(facts.get('competition'), set())


def originate(row, statistics, at):
    f = row['facts']
    reason = None
    result = {'fixture_id': row['id'], 'model_version': MODEL_VERSION, 'selection': None,
              'confidence': None, 'probability': None, 'fair_decimal': None, 'american_display': None,
              'market_quote': None, 'markets': [], 'input_ids': [], 'expires_at': None, 'notes': [], 'withheld': []}
    if row.get('in_window') is False:
        reason = 'Outside declared rolling source-date window'
    elif fixture_state(row, at) != 'upcoming':
        reason = 'Exact future start and fresh fixture evidence required; current state: '+fixture_state(row, at)
    elif not prematch_status_verified(row):
        reason = 'Official pre-match status unverified or not supported; a future published start alone is insufficient'
    elif not f['participant_a'] or not f['participant_b']:
        reason = 'No verified head-to-head; full field and a field model required'
    elif row['sport'] not in ('baseball', 'ice-hockey', 'basketball'):
        reason = 'No validated sport-specific model or compatible two-sided input series implemented'
    else:
        inputs = []
        for side in ('participant_a', 'participant_b'):
            identity = f[side+'_id']
            # Only exact official IDs or explicitly captured exact names; never fuzzy-join.
            options = [r for r in statistics if identity is not None and f['competition'] is not None and f['season'] is not None
                       and r.get('competition') == f['competition'] and r.get('season') == f['season']
                       and r.get('team_id') == identity and record_ok(r, at)]
            options.sort(key=lambda r: (r['observed_after'], r['id']), reverse=True)
            inputs.append(options[0] if options else None)
        a, b = inputs
        if not a or not b:
            reason = 'Missing, inconsistent, stale, or fewer-than-five-game record on at least one side; no neutral-price fallback'
        else:
            if a['as_of'] != b['as_of']:
                reason = 'Inputs have different as-of periods; no cross-snapshot matchup price'
            else:
                result['input_ids'] = [a['id'], b['id']]
                result['expires_at'] = iso(min(
                    parse_time(row['expires_at']), parse_time(f['start_utc']),
                    *(parse_time(r['observed_after']) + timedelta(hours=STATS_TTL_HOURS) for r in inputs)))
                src = row['source_ids'] + [a['source_id'], b['source_id']]
                pa, pb = f['participant_a'], f['participant_b']
                p = log5(a, b)
                settle = 'Full match, including overtime'+(' and shootout' if row['sport']=='ice-hockey' else '')
                result['notes'] = [ASSUMPTIONS['record_model']]
                if row['sport'] == 'baseball':
                    try:
                        grid, rates, mass = baseball_grid(a, b)
                        p = math.fsum(z for i,j,z in grid if i>j)
                        result['notes'] = [ASSUMPTIONS['mlb_score_model'], f'Model rates A={rates[0]:.6f}, B={rates[1]:.6f}; non-tie mass before conditioning={mass:.8f}.']
                        settle = 'Full-game research approximation, conditional on unequal final scores; no claim of sportsbook availability'
                        for line in (-1.5, 1.5):
                            pc = math.fsum(z for i,j,z in grid if i+line>j)
                            result['markets'].append(two_way(f'{row["id"]}-spread-{line}', 'handicap',
                                [f'{pa} {line:+g} runs',f'{pb} {-line:+g} runs'], pc, src, settle, line=line, units='runs'))
                        center = math.floor(sum(rates))+.5
                        for line in (center-1, center, center+1):
                            over = math.fsum(z for i,j,z in grid if i+j>line)
                            result['markets'].append(two_way(f'{row["id"]}-total-{line}', 'total',
                                [f'Over {line:g} runs',f'Under {line:g} runs'], over, src, settle, line=line, units='runs'))
                    except ValueError as error:
                        result['notes'].append('Score markets withheld: '+str(error))
                win = two_way(row['id']+'-winner', 'winner', [pa,pb], p, src, settle)
                result['markets'].insert(0,win)
                if abs(p-.5) > 1e-12:
                    best = win['outcomes'][0 if p>.5 else 1]
                    conf, caps = confidence_gate(best['probability'], best['fair_decimal'])
                    result.update(selection=best['selection'], confidence=conf, probability=best['probability'],
                                  fair_decimal=best['fair_decimal'], decimal_display=best['decimal_display'],
                                  american_display=best['american_display'], fair_price_in_target_band=best['fair_price_in_target_band'])
                    result['notes'] += caps
                else:
                    result['notes'].append('Equal probabilities: no arbitrary winner selection')
    priced = {m['market'] for m in result['markets']}
    for market in SPORT_MARKETS[row['sport']]:
        if market not in priced:
            result['withheld'].append({'market': market, 'status': 'unverified / not priced',
                                      'reason': reason or MARKET_REQUIREMENTS[market],
                                      'selection': None, 'probability': None, 'line': None, 'source_ids': row['source_ids']})
    if reason:
        result['notes'].append(reason)
    return result
