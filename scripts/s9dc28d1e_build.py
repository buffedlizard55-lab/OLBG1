#!/usr/bin/env python3
"""Session 9dc28d1e — build the desk JSON, CSV and the static dashboard under /9dc28d1e/.

Run from the repository root:  python3 scripts/s9dc28d1e_build.py
The script is deterministic apart from the generated-at stamp, which can be pinned with --now.
"""

import argparse
import csv
import html
import json
from pathlib import Path

import s9dc28d1e_model as M
from s9dc28d1e_data import (EL_GAMES, EL_TEAMS, EXCLUDED_SPORTS, INHERITED_LISTINGS,
                            MLB_GAMES, MLB_PROBABLE, MLB_RECORDS, MODEL_VERSION, NHL_GAMES,
                            NHL_TEAMS, SESSION, SOURCES, SPORT_META)
from s9dc28d1e_prose import EUROLEAGUE_CAPPED, FINDINGS, PREDICTIONS

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / '9dc28d1e'
DATA = ROOT / 'data' / '9dc28d1e'

SOURCE_BY_ID = {s['id']: s for s in SOURCES}

NHL_PUCK_LINES = (-1.5, 1.5)
NHL_TOTALS = (5.5, 6.5)
NHL_TEAM_TOTALS = (1.5, 2.5, 3.5, 4.5)
EL_HANDICAPS = (-11.5, -8.5, -5.5, -2.5, 2.5, 5.5, 8.5, 11.5)
EL_TOTALS = (158.5, 162.5, 166.5, 170.5, 174.5, 178.5)


# ------------------------------------------------------------------ helpers
def am(p):
    return M.american_from_probability(p)


def r(x, n=4):
    return round(x, n)


def fmt_am(p):
    v = am(p)
    return f"+{v:.0f}" if v > 0 else f"{v:.0f}"


def outcome(selection, p, in_band=None, tier=None):
    return {
        'selection': selection,
        'probability': r(p, 6),
        'fair_decimal': r(1 / p, 6),
        'decimal_display': f"{1 / p:.4f}",
        'american_display': fmt_am(p),
        'fair_price_in_target_band': M.in_band(p) if in_band is None else in_band,
        'tier': tier if tier else None,
    }


def market_row(fixture_id, market, settlement, outcomes, sources, note=None):
    return {
        'id': f"{fixture_id}-{market['slug']}",
        'market': market['name'],
        'settlement': settlement,
        'status': 'experimental — zero-margin model line, not a bookmaker quote',
        'sources': sources,
        'note': note,
        'outcomes': outcomes,
    }


# ------------------------------------------------------------------ fixture + market build
def nhl_markets(fid, away, home):
    out = []
    p_home = M.nhl_moneyline(away, home)
    out.append(market_row(fid, {'name': 'Match winner (moneyline)', 'slug': 'winner'},
                          'Settles on the winner of the full game including overtime and shootout.',
                          [outcome(home, p_home), outcome(away, 1 - p_home)],
                          ['nhl-team-summary-20262027', 'nhl-schedule-20261022']))
    for line in NHL_PUCK_LINES:
        for side, team in (('home', home), ('away', away)):
            p = M.nhl_puck_line(away, home, side, line)
            if line < 0:
                label = f"{team} {line:+.1f}"
            else:
                label = f"{team} {line:+.1f}"
            out.append(market_row(fid, {'name': f'Puck line {line:+.1f}', 'slug': f'pl{str(line).replace(".", "")}{side}'},
                                  'Settles on the full game including overtime. A regulation tie becomes a one-goal overtime win for one side.',
                                  [outcome(label, p), outcome(('away' if side == 'home' else 'home'), 1 - p)],
                                  ['nhl-team-summary-20262027'],
                                  note='The opposite side is shown as a single mirrored price and is not an independent market.'))
    for line in NHL_TOTALS:
        p_over = M.nhl_total_over(away, home, line)
        out.append(market_row(fid, {'name': f'Total goals {line}', 'slug': f'tot{str(line).replace(".", "")}'},
                              'Settles on total goals in the full game including overtime.',
                              [outcome(f'Over {line} goals', p_over), outcome(f'Under {line} goals', 1 - p_over)],
                              ['nhl-team-summary-20262027']))
    for team in (home, away):
        mu = M.nhl_expected_goals(away, home)[1] if team == home else M.nhl_expected_goals(away, home)[0]
        for line in NHL_TEAM_TOTALS:
            p_over = 1 - sum(M.poisson_pmf(k, mu) for k in range(int(line) + 1))
            out.append(market_row(fid, {'name': f'{team} team total {line} goals', 'slug': f'tt{str(line).replace(".", "")}-{team[:3].lower()}'},
                                  'Settles on that club\'s goals in the full game including overtime.',
                                  [outcome(f'{team} over {line} goals', p_over),
                                   outcome(f'{team} under {line} goals', 1 - p_over)],
                                  ['nhl-team-summary-20262027'],
                                  note='The usual market line for this match is unknown; the ladder is originated at standard half-goal steps.'))
    return out


def el_markets(fid, home, away):
    out = []
    p_home = M.el_moneyline(home, away)
    out.append(market_row(fid, {'name': 'Match winner (moneyline)', 'slug': 'winner'},
                          'Settles on the winner of the full game including overtime.',
                          [outcome(home, p_home), outcome(away, 1 - p_home)],
                          ['euroleague-standings-e2026', 'euroleague-round7-gamecenter']))
    for line in EL_HANDICAPS:
        for side, team in (('home', home), ('away', away)):
            p = M.el_handicap(home, away, side, line)
            out.append(market_row(fid, {'name': f'Handicap {line:+.1f}', 'slug': f'hcp{str(line).replace(".", "").replace("-", "m")}{side}'},
                                  'Settles on the full game including overtime.',
                                  [outcome(f'{team} {line:+.1f}', p),
                                   outcome(('away' if side == 'home' else 'home'), 1 - p)],
                                  ['euroleague-standings-e2026'],
                                  note='Opposite side mirrored; the ladder is originated, not observed.'))
    for line in EL_TOTALS:
        p_over = M.el_total_over(home, away, line)
        out.append(market_row(fid, {'name': f'Match total {line}', 'slug': f'tot{str(line).replace(".", "")}'},
                              'Settles on combined points in the full game including overtime.',
                              [outcome(f'Over {line} points', p_over), outcome(f'Under {line} points', 1 - p_over)],
                              ['euroleague-standings-e2026']))
    return out


def mlb_markets(fid, away, home):
    p_home = M.mlb_moneyline(away, home)
    return [market_row(fid, {'name': 'Match winner (moneyline)', 'slug': 'winner'},
                       'Settles on the winner of the game. No run line or total is originated for this sport.',
                       [outcome(home, p_home), outcome(away, 1 - p_home)],
                       ['mlb-records-2026', 'mlb-schedule-ws-2026'],
                       note='Run line and totals withheld: the 2026 league run environment was not verified (F-9DC-05).')]


def build():
    priced = []
    fixtures = []

    for fid, away, home, start, venue in NHL_GAMES:
        fixtures.append({
            'id': fid, 'sport': 'ice-hockey', 'competition': 'NHL 2026-27 regular season',
            'home': home, 'away': away, 'start_utc': start, 'venue': venue,
            'status': 'scheduled (gameState FUT at read time)', 'priced': True,
            'source_ids': ['nhl-schedule-20261022', 'nhl-team-summary-20262027'],
            'verified_this_session': True,
        })
        mk = nhl_markets(fid, away, home)
        priced.append({
            'fixture_id': fid, 'sport': 'ice-hockey', 'home': home, 'away': away,
            'start_utc': start, 'venue': venue, 'markets': mk,
            'inputs': {
                'home_record': dict(zip(('gp', 'w', 'l', 'otl', 'gf', 'ga'), NHL_TEAMS[home])),
                'away_record': dict(zip(('gp', 'w', 'l', 'otl', 'gf', 'ga'), NHL_TEAMS[away])),
                'expected_goals': {'home': r(M.nhl_expected_goals(away, home)[1], 2),
                                   'away': r(M.nhl_expected_goals(away, home)[0], 2)},
            },
        })

    for fid, home, away, start, tsrc in EL_GAMES:
        fixtures.append({
            'id': fid, 'sport': 'basketball', 'competition': 'EuroLeague 2026-27, Round 7',
            'home': home, 'away': away, 'start_utc': start, 'venue': None,
            'status': 'scheduled', 'priced': True,
            'source_ids': ['euroleague-standings-e2026', tsrc],
            'verified_this_session': True,
            'time_inherited': True,
        })
        priced.append({
            'fixture_id': fid, 'sport': 'basketball', 'home': home, 'away': away,
            'start_utc': start, 'venue': None, 'markets': el_markets(fid, home, away),
            'inputs': {
                'home_record': dict(zip(('gp', 'w', 'l', 'pf', 'pa'), EL_TEAMS[home])),
                'away_record': dict(zip(('gp', 'w', 'l', 'pf', 'pa'), EL_TEAMS[away])),
                'expected_points': {'home': r(M.el_expected_points(home, away)[0], 2),
                                    'away': r(M.el_expected_points(home, away)[1], 2)},
            },
        })

    for fid, away, home, start, venue, label in MLB_GAMES:
        fixtures.append({
            'id': fid, 'sport': 'baseball', 'competition': label,
            'home': home, 'away': away, 'start_utc': start, 'venue': venue,
            'status': 'scheduled', 'priced': True,
            'source_ids': ['mlb-schedule-ws-2026', 'mlb-records-2026'],
            'verified_this_session': True,
            'probable_pitcher': MLB_PROBABLE.get(fid, {}),
        })
        priced.append({
            'fixture_id': fid, 'sport': 'baseball', 'home': home, 'away': away,
            'start_utc': start, 'venue': venue, 'markets': mlb_markets(fid, away, home),
            'inputs': {'home_record': MLB_RECORDS[home], 'away_record': MLB_RECORDS[away]},
        })

    fixture_sources = {f['id']: f['source_ids'] for f in fixtures}
    fixture_competition = {f['id']: f['competition'] for f in fixtures}
    for row in priced:
        row['source_ids'] = fixture_sources[row['fixture_id']]
        row['competition'] = fixture_competition[row['fixture_id']]

    # ---- tiers
    prediction_keys = {(p['fixture_id'], p['selection']) for p in PREDICTIONS}
    capped = {(fid, sel): reason for fid, sel, _, _, reason in EUROLEAGUE_CAPPED}
    out_of_window = []
    for row in priced:
        for mk in row['markets']:
            for oc in mk['outcomes']:
                p = oc['probability']
                if p > 0.70 and M.in_band(p) and (row['fixture_id'], oc['selection']) in prediction_keys:
                    oc['tier'] = 'high'
                elif p > 0.70 and M.in_band(p):
                    oc['tier'] = 'medium'
                    oc['tier_reason'] = capped.get((row['fixture_id'], oc['selection']),
                                                   'In band but no prediction was written for this line.')
                elif p > 0.70:
                    oc['tier'] = 'outside_window'
                    out_of_window.append({
                        'fixture_id': row['fixture_id'], 'market': mk['market'],
                        'selection': oc['selection'], 'probability': p,
                        'american': oc['american_display'],
                    })
                elif p >= 0.60:
                    oc['tier'] = 'medium'
                else:
                    oc['tier'] = 'low'
            mk['tiers'] = sorted({o['tier'] for o in mk['outcomes']})

    # ---- sensitivity for High rows
    def nhl_team_total_prob(away, home, team, line, shrink, edge):
        old_s, old_e = M.NHL_SHRINK, M.NHL_HOME_EDGE
        M.NHL_SHRINK, M.NHL_HOME_EDGE = shrink, edge
        try:
            mu_a, mu_h = M.nhl_expected_goals(away, home)
        finally:
            M.NHL_SHRINK, M.NHL_HOME_EDGE = old_s, old_e
        mu = mu_h if team == home else mu_a
        over = 1 - sum(M.poisson_pmf(k, mu) for k in range(int(line) + 1))
        return over

    sensitivity = []
    for pred in PREDICTIONS:
        row = next(x for x in priced if x['fixture_id'] == pred['fixture_id'])
        is_over = 'over' in pred['selection'].lower()
        team = row['home'] if pred['selection'].startswith(row['home']) else row['away']
        vals = []
        for shrink in (8.0, 12.0, 16.0):
            for edge in (0.05, 0.10, 0.15):
                over = nhl_team_total_prob(row['away'], row['home'], team, pred['line'], shrink, edge)
                vals.append(over if is_over else 1 - over)
        sensitivity.append({
            'fixture_id': pred['fixture_id'], 'selection': pred['selection'],
            'probability': next(o['probability'] for mk in row['markets'] for o in mk['outcomes']
                                if o['selection'] == pred['selection']),
            'low': r(min(vals)), 'high': r(max(vals)),
            'fragile': min(vals) <= 0.70 or max(vals) > 0.7142857,
        })

    # ---- desk document
    all_outcomes = [o for row in priced for mk in row['markets'] for o in mk['outcomes']]
    counts = {
        'priced_matches': len(priced),
        'inherited_listings': len(INHERITED_LISTINGS),
        'fixtures_total': len(fixtures) + len(INHERITED_LISTINGS),
        'markets': sum(len(row['markets']) for row in priced),
        'outcomes': len(all_outcomes),
        'high': sum(1 for o in all_outcomes if o['tier'] == 'high'),
        'medium': sum(1 for o in all_outcomes if o['tier'] == 'medium'),
        'low': sum(1 for o in all_outcomes if o['tier'] == 'low'),
        'outside_window': sum(1 for o in all_outcomes if o['tier'] == 'outside_window'),
        'predictions': len(PREDICTIONS),
        'findings': len(FINDINGS),
        'sports_in_scope': len(SPORT_META),
        'sports_priced': len({row['sport'] for row in priced}),
        'sports_with_participants': len({row['sport'] for row in priced} |
                                        {s for s, *_ in INHERITED_LISTINGS if s in SPORT_META}),
    }

    desk = {
        'desk': '9dc28d1e',
        'session': SESSION,
        'generated_at': NOW,
        'model_version': MODEL_VERSION,
        'scope': {
            'in_scope_sports': [{'slug': k, 'name': v[0], 'olbg_id': v[1], 'official_url': v[2]}
                                for k, v in SPORT_META.items()],
            'excluded_sports': [{'name': n, 'olbg_id': i, 'note': note} for n, i, note in EXCLUDED_SPORTS],
        },
        'gate': {
            'rule': 'High = model probability > 0.70 AND selected line fair American in [-250, +10000] '
                    'AND a unique >=30-word prediction supported by verified player-level facts.',
            'band_low_american': -250,
            'band_high_american': 10000,
            'implied_probability_at_70pct_american': -233.33,
            'effective_probability_window': [0.70, 0.7142857],
            'note': 'American prices shorter than -250 are excluded even when the probability is far above 70%.',
        },
        'sources': [{k: v for k, v in s.items()} for s in SOURCES] + [
            {'id': 'nhl-club-stats-NSH', 'publisher': 'NHL', 'url': 'https://api-web.nhle.com/v1/club-stats/NSH/20262027/2',
             'observed_utc': '2026-10-22T12:22:00Z', 'what': 'Nashville skater and goalie season totals.', 'scope_note': 'Player-level form used only in the High write-up.'},
            {'id': 'nhl-club-stats-SJS', 'publisher': 'NHL', 'url': 'https://api-web.nhle.com/v1/club-stats/SJS/20262027/2',
             'observed_utc': '2026-10-22T12:23:00Z', 'what': 'San Jose skater and goalie season totals.', 'scope_note': 'Player-level form used only in the High write-up.'},
            {'id': 'nhl-club-stats-MIN', 'publisher': 'NHL', 'url': 'https://api-web.nhle.com/v1/club-stats/MIN/20262027/2',
             'observed_utc': '2026-10-22T12:24:00Z', 'what': 'Minnesota skater and goalie season totals.', 'scope_note': 'Player-level form used only in the High write-up.'},
        ],
        'fixtures': fixtures,
        'inherited': [{
            'sport': s, 'id': fid, 'participant_a': a, 'participant_b': b,
            'date': d, 'start_utc': st, 'note': note,
            'source_ids': ['canonical-snapshot-20261022T0727Z'],
            'verified_this_session': False, 'priced': False,
        } for s, fid, a, b, d, st, note in INHERITED_LISTINGS],
        'priced': priced,
        'predictions': PREDICTIONS,
        'sensitivity': sensitivity,
        'capped_in_band': [
            {'fixture_id': row['fixture_id'], 'selection': o['selection'], 'probability': o['probability'],
             'american': o['american_display'], 'reason': o.get('tier_reason', '')}
            for row in priced for mk in row['markets'] for o in mk['outcomes']
            if o['tier'] == 'medium' and o['probability'] > 0.70
        ],
        'out_of_window': sorted(out_of_window, key=lambda x: -x['probability']),
        'findings': FINDINGS,
        'counts': counts,
    }
    return desk


# ------------------------------------------------------------------ site rendering
CSS = """
:root{--bg:#0b1220;--card:#131d2f;--line:#243349;--txt:#e6edf7;--muted:#93a4bd;--accent:#4cc2ff;
--good:#4ade80;--warn:#fbbf24;--bad:#f87171;--hi:#22d3ee}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--txt);font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
header{background:linear-gradient(180deg,#101a2b,#0b1220);border-bottom:1px solid var(--line);padding:18px 0}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}
h1{font-size:24px;margin:0 0 6px}h2{font-size:19px;margin:30px 0 10px}h3{font-size:16px;margin:20px 0 8px}
.sub{color:var(--muted);font-size:13px}
nav{display:flex;flex-wrap:wrap;gap:6px;margin-top:14px}
nav a{background:#16233a;border:1px solid var(--line);padding:6px 11px;border-radius:7px;font-size:13px;color:var(--txt)}
nav a.on{background:#1d3a55;border-color:#2f5f86;color:#fff}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:20px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px}
.card .n{font-size:26px;font-weight:700}.card .l{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.04em}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden;font-size:13px;margin:10px 0 24px}
th,td{padding:8px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{background:#16233a;color:#cfe0f5;font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.03em;position:sticky;top:0}
tr:last-child td{border-bottom:none}tbody tr:hover{background:#16233a}
.num{font-variant-numeric:tabular-nums;white-space:nowrap}
.tag{display:inline-block;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:600;letter-spacing:.02em}
.high{background:rgba(76,194,255,.16);color:#8fdcff;border:1px solid #2c6f96}
.medium{background:rgba(251,191,36,.14);color:#fcd34d;border:1px solid #7a5c12}
.low{background:rgba(148,163,184,.14);color:#c3cfe0;border:1px solid #3a4a63}
.outside_window{background:rgba(248,113,113,.12);color:#fca5a5;border:1px solid #7f2f2f}
.none{background:#1a2436;color:#8496ad;border:1px solid #2c3a50}
.note{background:#101b2c;border-left:3px solid var(--accent);padding:10px 14px;border-radius:0 8px 8px 0;color:#c9d8ea;font-size:13px;margin:14px 0}
.warnbox{border-left-color:var(--warn)}
.pred{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin:14px 0}
.pred .meta{color:var(--muted);font-size:12px;margin-bottom:6px}
.pred p{margin:8px 0 0}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px}
footer{border-top:1px solid var(--line);margin-top:40px;padding:22px 0;color:var(--muted);font-size:12px}
code{background:#0e1726;padding:2px 5px;border-radius:4px;font-size:12px}
.small{font-size:12px;color:var(--muted)}
"""

NAV = [
    ('index.html', 'Dashboard'),
    ('matches.html', 'Matches'),
    ('markets.html', 'Markets & prices'),
    ('predictions.html', 'High-confidence picks'),
    ('analysis.html', 'Gate analysis'),
    ('flagged.html', 'Flagged for review'),
    ('sources.html', 'Sources'),
    ('methodology.html', 'Methodology'),
]


def page(title, rel, body, active=None, subtitle=''):
    def nav_link(href, label):
        cls = ' class="on"' if href == active else ''
        return f'<a href="{rel}{href}"{cls}>{html.escape(label)}</a>'
    nav = ''.join(nav_link(href, label) for href, label in NAV)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} · OLBG research desk 9dc28d1e</title>
<style>{CSS}</style></head>
<body>
<header><div class="wrap">
<h1>{html.escape(title)}</h1>
<div class="sub">{subtitle or 'Session 9dc28d1e · evidence-first desk · generated ' + NOW}</div>
<nav>{nav}</nav>
</div></header>
<main class="wrap">
{body}
</main>
<footer><div class="wrap">
<p><strong>Estimate, not advice.</strong> Every price on this desk is a zero-margin model line originated
from official team-season inputs. No bookmaker quote, availability or edge is claimed. Blank means
unverified. This desk is independent of OLBG and of the canonical dashboard build.</p>
<p>Generated {NOW} · model {MODEL_VERSION} · <a href="{rel}sources.html">source register</a> ·
<a href="{rel}methodology.html">methodology and limits</a></p>
</div></footer>
</body></html>"""


def tag(t):
    label = {'high': 'HIGH', 'medium': 'MEDIUM', 'low': 'LOW', 'outside_window': 'OUTSIDE WINDOW'}.get(t, '—')
    return f'<span class="tag {t}">{label}</span>'


def src_links(ids):
    out = []
    for sid in ids:
        s = SOURCE_BY_ID.get(sid) or next((x for x in EXTRA_SOURCES if x['id'] == sid), None)
        if not s:
            out.append(html.escape(sid))
            continue
        host = s['url'].split('/')[2]
        out.append(f'<a href="{html.escape(s["url"])}" title="{html.escape(s["publisher"])}">{html.escape(host)}</a>')
    return ' '.join(out) if out else '—'


EXTRA_SOURCES = [
    {'id': 'nhl-club-stats-NSH', 'publisher': 'NHL', 'url': 'https://api-web.nhle.com/v1/club-stats/NSH/20262027/2',
     'observed_utc': '2026-10-22T12:22:00Z', 'what': 'Nashville skater and goalie season totals.', 'scope_note': 'Player-level form used only in the High write-up.'},
    {'id': 'nhl-club-stats-SJS', 'publisher': 'NHL', 'url': 'https://api-web.nhle.com/v1/club-stats/SJS/20262027/2',
     'observed_utc': '2026-10-22T12:23:00Z', 'what': 'San Jose skater and goalie season totals.', 'scope_note': 'Player-level form used only in the High write-up.'},
    {'id': 'nhl-club-stats-MIN', 'publisher': 'NHL', 'url': 'https://api-web.nhle.com/v1/club-stats/MIN/20262027/2',
     'observed_utc': '2026-10-22T12:24:00Z', 'what': 'Minnesota skater and goalie season totals.', 'scope_note': 'Player-level form used only in the High write-up.'},
    {'id': 'canonical-snapshot-20261022T0727Z', 'publisher': 'Project canonical snapshot',
     'url': 'https://github.com/buffedlizard55-lab/OLBG1/blob/main/data/current/snapshot.json',
     'observed_utc': '2026-10-22T07:17:40Z', 'what': 'Inherited listings and their original official source links.',
     'scope_note': 'Not re-read by this session; prices withheld.'},
]


def sport_card(slug, meta, desk):
    priced = [x for x in desk['priced'] if x['sport'] == slug]
    inherited = [x for x in desk['inherited'] if x['sport'] == slug]
    highs = sum(1 for x in priced for mk in x['markets'] for o in mk['outcomes'] if o['tier'] == 'high')
    if priced:
        status = f'<span class="tag high">{highs} HIGH</span>' if highs else '<span class="tag medium">PRICED</span>'
        note = f'{len(priced)} matches priced this session'
    elif inherited:
        status = '<span class="tag none">LISTED</span>'
        note = f'{len(inherited)} listings, prices withheld'
    else:
        status = '<span class="tag none">NO INPUT</span>'
        note = 'no official input obtained today'
    return (f'<div class="card"><h3 style="margin:0 0 6px"><a href="sports/{slug}.html">'
            f'{html.escape(meta[0])}</a></h3><div class="small">OLBG route id {meta[1]}</div>'
            f'<div style="margin-top:8px">{status}&nbsp; <span class="small">{note}</span></div></div>')


def render(desk):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'assets').mkdir(exist_ok=True)
    (OUT / 'assets' / 'style.css').write_text(CSS)
    c = desk['counts']
    preds = desk['predictions']

    # ---------------- index
    hi_rows = []
    for p in preds:
        row = next(x for x in desk['priced'] if x['fixture_id'] == p['fixture_id'])
        prob = next(o['probability'] for mk in row['markets'] for o in mk['outcomes'] if o['selection'] == p['selection'])
        sens = next(s for s in desk['sensitivity'] if s['fixture_id'] == p['fixture_id'])
        hi_rows.append(f"""<tr><td><a href="sports/{row['sport']}.html">{html.escape(row['sport'])}</a></td>
<td>{html.escape(row['away'])} at {html.escape(row['home'])}<div class="small">{html.escape(row['start_utc'])} · {html.escape(row['venue'] or '')}</div></td>
<td>{html.escape(p['selection'])}</td>
<td class="num">{prob*100:.1f}%</td><td class="num">{fmt_am(prob)}</td>
<td class="num">{sens['low']*100:.1f}–{sens['high']*100:.1f}%</td><td>{tag('high')}</td></tr>""")

    body = f"""
<p class="sub" style="max-width:860px">A fresh 22 October 2026 desk: official sources re-read between 12:04Z and 12:25Z,
own zero-margin lines across winner, handicap, match-total and team-total markets, and the brief's
High-confidence rule applied literally and conjunctively.</p>

<div class="cards">
  <div class="card"><div class="n">{c['priced_matches']}</div><div class="l">Priced matches</div></div>
  <div class="card"><div class="n">{c['markets']}</div><div class="l">Originated markets</div></div>
  <div class="card"><div class="n">{c['outcomes']}</div><div class="l">Priced outcomes</div></div>
  <div class="card"><div class="n">{c['high']}</div><div class="l">High confidence</div></div>
  <div class="card"><div class="n">{c['medium']}</div><div class="l">Medium</div></div>
  <div class="card"><div class="n">{c['low']}</div><div class="l">Low</div></div>
  <div class="card"><div class="n">{c['outside_window']}</div><div class="l">Over 70%, price outside window</div></div>
  <div class="card"><div class="n">{c['predictions']}</div><div class="l">Written predictions</div></div>
</div>

<h2>High-confidence picks</h2>
<table><thead><tr><th>Sport</th><th>Fixture</th><th>Selection</th><th>Model probability</th>
<th>Fair price</th><th>Sensitivity range</th><th>Tier</th></tr></thead><tbody>
{''.join(hi_rows)}
</tbody></table>
<p class="small">Sensitivity range re-computes the same selection under shrinkage of 8, 12 and 16 games and a
home edge of 0.05, 0.10 and 0.15 goals. A High whose range leaves the 70.00–71.43% window is fragile;
the analysis page shows each row. <a href="predictions.html">Read the full write-ups →</a></p>

<div class="note warnbox">
<strong>The gate is narrower than it looks.</strong> "More than 70%" already implies an American price shorter
than −233.33. Requiring the price to be no shorter than −250 leaves a window only <strong>1.43 percentage
points wide</strong>. That is why 108 listings produce {c['high']} High picks rather than dozens, and why
{c['outside_window']} selections that clear 70% are published as <em>outside window</em> instead of being
relabelled. <a href="analysis.html">See the arithmetic and every near-miss →</a>
</div>

<h2>Categories</h2>
<div class="grid2">
{''.join(sport_card(slug, meta, desk) for slug, meta in SPORT_META.items())}
</div>

<h2>What is and is not complete</h2>
<table><tbody>
<tr><td style="width:240px"><strong>Verified this session</strong></td><td>25 matches: 12 NHL games, 9 EuroLeague games, 4 MLB World Series games. Participants, UTC starts, venues where published, and every rating input were read from the league's own feed.</td></tr>
<tr><td><strong>Inherited, unpriced</strong></td><td>{c['inherited_listings']} listings carry the 07:17Z canonical observation window, blank prices and an explicit "not re-read" status.</td></tr>
<tr><td><strong>Withheld on purpose</strong></td><td>MLB run lines and totals (no verified league run environment); EuroLeague High tiers (no player-level source); five categories with no official draw.</td></tr>
<tr><td><strong>Never claimed</strong></td><td>Bookmaker availability, edge, stake, injury news, or a calibrated probability.</td></tr>
</tbody></table>
<p><a href="flagged.html">All {c['findings']} flagged items →</a></p>
"""
    (OUT / 'index.html').write_text(page('OLBG research desk', '', body, 'index.html',
                                         f'Session 9dc28d1e · {c["priced_matches"]} priced matches · generated {NOW}'))

    # ---------------- matches
    rows = []
    for f in desk['fixtures']:
        rows.append(f"""<tr><td>{html.escape(f['sport'])}</td><td>{html.escape(f['competition'])}</td>
<td><strong>{html.escape(f['home'])}</strong> v {html.escape(f['away'])}<div class="small">venue: {html.escape(f['venue'] or '—')}</div></td>
<td class="num">{html.escape(f['start_utc'])}</td><td>{html.escape(f['status'])}</td>
<td>{src_links(f['source_ids'])}</td><td>{'yes' if f.get('time_inherited') else 're-read 12:0x–12:2xZ'}</td></tr>""")
    for i in desk['inherited']:
        rows.append(f"""<tr><td>{html.escape(i['sport'])}</td><td>inherited listing</td>
<td>{html.escape(i['participant_a'] or '—')} v {html.escape(i['participant_b'] or '—')}</td>
<td class="num">{html.escape(i['start_utc'] or i['date'] or '—')}</td>
<td><span class="tag none">NOT RE-READ</span><div class="small">{html.escape(i['note'])}</div></td>
<td>{src_links(i['source_ids'])}</td><td>no</td></tr>""")
    body = f"""
<p class="sub">Every row is home v away. Priced rows were re-read this session. Inherited rows keep their
original official link but are explicitly marked as not re-read, and carry no prices.</p>
<table><thead><tr><th>Sport</th><th>Competition</th><th>Fixture</th><th>Start (UTC)</th>
<th>Status</th><th>Official source</th><th>Verified now</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
"""
    (OUT / 'matches.html').write_text(page('Matches', '', body, 'matches.html'))

    # ---------------- markets
    rows = []
    for row in desk['priced']:
        for mk in row['markets']:
            for oc in mk['outcomes']:
                reason = oc.get('tier_reason')
                rows.append(f"""<tr><td>{html.escape(row['sport'])}</td>
<td>{html.escape(row['home'])} v {html.escape(row['away'])}<div class="small">{html.escape(row['start_utc'])}</div></td>
<td>{html.escape(mk['market'])}</td><td>{html.escape(oc['selection'])}</td>
<td class="num">{oc['probability']*100:.2f}%</td><td class="num">{oc['decimal_display']}</td>
<td class="num">{oc['american_display']}</td><td>{tag(oc['tier'])}</td>
<td class="small">{html.escape(reason) if reason else ''}</td></tr>""")
    body = f"""
<p class="sub">{c['markets']} markets · {c['outcomes']} priced outcomes. Decimal and American prices are
derived from the model probability with no margin. "Outside window" means the selection clears 70% but its
fair price is shorter than −250, which the brief excludes.</p>
<table><thead><tr><th>Sport</th><th>Fixture</th><th>Market</th><th>Selection</th><th>Probability</th>
<th>Fair decimal</th><th>Fair American</th><th>Tier</th><th>Note</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
"""
    (OUT / 'markets.html').write_text(page('Markets and prices', '', body, 'markets.html'))

    # ---------------- predictions
    blocks = []
    for p in preds:
        row = next(x for x in desk['priced'] if x['fixture_id'] == p['fixture_id'])
        prob = next(o['probability'] for mk in row['markets'] for o in mk['outcomes'] if o['selection'] == p['selection'])
        sens = next(s for s in desk['sensitivity'] if s['fixture_id'] == p['fixture_id'])
        blocks.append(f"""<div class="pred">
<div class="meta">{html.escape(row['sport'].upper())} · {html.escape(row['competition'])} ·
{html.escape(row['away'])} at {html.escape(row['home'])} · {html.escape(row['start_utc'])} ·
{html.escape(row['venue'] or '')}</div>
<h3 style="margin:0">{html.escape(p['title'])}</h3>
<p><strong>Selection:</strong> {html.escape(p['selection'])} · <strong>fair price</strong> {fmt_am(prob)}
({1/prob:.4f}) · <strong>model probability</strong> {prob*100:.1f}% · {tag('high')}</p>
<p>{html.escape(p['text'])}</p>
<p class="small">Words: {len(p['text'].split())}. Sensitivity under parameter perturbations:
{sens['low']*100:.1f}–{sens['high']*100:.1f}% {'— <strong>fragile</strong>' if sens['fragile'] else ''}.
Sources: {src_links(p['source_ids'])}.</p>
</div>""")
    body = f"""
<p class="sub">Written only for selections that clear the model threshold, the price window and the
player-level evidence requirement. Each names the participants, the verified form and the selection.</p>
{''.join(blocks)}
<div class="note">No prediction is generated for the {len(desk['capped_in_band'])} EuroLeague selections that
clear the first two conditions but have no verified player-level input — they sit in
<a href="flagged.html">Flagged for review</a> at Medium.</div>
"""
    (OUT / 'predictions.html').write_text(page('High-confidence picks', '', body, 'predictions.html'))

    # ---------------- analysis
    def sens_badge(fragile):
        return '<span class="tag outside_window">FRAGILE</span>' if fragile else '<span class="tag high">STABLE</span>'
    sens_rows = ''.join(
        "<tr><td>{}</td><td class='num'>{:.2f}%</td><td class='num'>{:.1f}%</td>"
        "<td class='num'>{:.1f}%</td><td>{}</td></tr>".format(
            html.escape(s['selection']), s['probability'] * 100, s['low'] * 100,
            s['high'] * 100, sens_badge(s['fragile']))
        for s in desk['sensitivity'])
    capped_rows = ''.join(
        f"<tr><td>{html.escape(x['fixture_id'])}</td><td>{html.escape(x['selection'])}</td>"
        f"<td class='num'>{x['probability']*100:.2f}%</td><td class='num'>{x['american']}</td>"
        f"<td class='small'>{html.escape(x['reason'])}</td></tr>" for x in desk['capped_in_band'])
    ow_rows = ''.join(
        f"<tr><td>{html.escape(x['fixture_id'])}</td><td>{html.escape(x['market'])}</td>"
        f"<td>{html.escape(x['selection'])}</td><td class='num'>{x['probability']*100:.1f}%</td>"
        f"<td class='num'>{x['american']}</td></tr>" for x in desk['out_of_window'][:25])
    body = f"""
<h2>1. The gate, arithmetically</h2>
<p>American odds map to probability as <code>p = 100/(100+|A|)</code> for negative A. Three anchor points:</p>
<table><thead><tr><th>American</th><th>Implied probability</th><th>Verdict under the brief</th></tr></thead><tbody>
<tr><td class="num">−233.33</td><td class="num">70.00%</td><td>the exact "greater than 70%" boundary</td></tr>
<tr><td class="num">−250.00</td><td class="num">71.43%</td><td>the brief's price floor</td></tr>
<tr><td class="num">+10000</td><td class="num">0.99%</td><td>the brief's price ceiling — never reachable at 70%</td></tr>
</tbody></table>
<p>Both conditions can only hold for probabilities in <strong>(70.00%, 71.43%]</strong>. Any selection more
likely than 71.43% is too short to be inside the window; any selection between 0.99% and 70% fails the
probability test. This desk applies the conjunction literally. It does not quietly widen the window,
and it does not call a −400 favourite "high confidence in the −250 to +10000 band".</p>

<h2>2. What that produced</h2>
<div class="cards">
<div class="card"><div class="n">{c['high']}</div><div class="l">High (all three conditions)</div></div>
<div class="card"><div class="n">{len(desk['capped_in_band'])}</div><div class="l">In band, capped at Medium</div></div>
<div class="card"><div class="n">{c['outside_window']}</div><div class="l">Over 70%, price outside</div></div>
<div class="card"><div class="n">{c['low']}</div><div class="l">Low</div></div>
</div>

<h2>3. Tier fragility</h2>
<p>A probability that sits inside a 1.43-point window is sensitive to the model's own assumptions.
Each High is re-computed at shrinkage of 8, 12 and 16 games and a home edge of 0.05, 0.10 and 0.15 goals.</p>
<table><thead><tr><th>Selection</th><th>Base</th><th>Low</th><th>High</th><th>Status</th></tr></thead>
<tbody>{sens_rows}</tbody></table>
<p class="small">"Fragile" does not mean the pick is wrong; it means the label depends on the prior. The
price that goes with it moves the same way.</p>

<h2>4. In-band selections capped at Medium</h2>
<p>These clear probability and price. They are not High because the required player-level evidence was not
available from an official source for the write-up.</p>
<table><thead><tr><th>Fixture</th><th>Selection</th><th>Probability</th><th>Fair American</th><th>Why capped</th></tr></thead>
<tbody>{capped_rows}</tbody></table>

<h2>5. The strongest selections the brief excludes</h2>
<p>Every row below clears 70% but prices shorter than −250, so the brief's window removes it. Shown for
transparency, not counted as High.</p>
<table><thead><tr><th>Fixture</th><th>Market</th><th>Selection</th><th>Probability</th><th>Fair American</th></tr></thead>
<tbody>{ow_rows}</tbody></table>
<p class="small">Top 25 by probability of {c['outside_window']} such selections.</p>

<h2>6. Coverage</h2>
<p>Seventeen in-scope categories. {c['sports_priced']} were priced this session, all from league-run feeds.
The remaining categories are listed but unpriced: their official pages either published no draw this
session or their inputs were not re-read. Nothing was filled in from memory.</p>
"""
    (OUT / 'analysis.html').write_text(page('Gate analysis', '', body, 'analysis.html'))

    # ---------------- flagged
    find_rows = ''.join(f"""<div class="pred"><h3 style="margin-top:0">{html.escape(f['id'])} ·
<span class="tag {'outside_window' if f['severity']=='high' else 'medium' if f['severity']=='medium' else 'low'}">{f['severity'].upper()}</span></h3>
<strong>{html.escape(f['title'])}</strong>
<p>{html.escape(f['detail'])}</p>
<p class="small">Sources: {html.escape(', '.join(f['sources']))} · Status: {html.escape(f['status'])}</p></div>"""
                         for f in desk['findings'])
    body = f"""
<p class="sub">Documented irregularities, withheld fields and assumptions. None of these block publication;
all are listed so a reviewer can check them against the links.</p>
{find_rows}
"""
    (OUT / 'flagged.html').write_text(page('Flagged for review', '', body, 'flagged.html'))

    # ---------------- sources
    all_sources = desk['sources']
    rows = ''.join(f"""<tr><td><code>{html.escape(s['id'])}</code></td><td>{html.escape(s['publisher'])}</td>
<td><a href="{html.escape(s['url'])}">{html.escape(s['url'])}</a></td>
<td class="num">{html.escape(s['observed_utc'])}</td>
<td>{html.escape(s['what'])}<div class="small">{html.escape(s['scope_note'])}</div></td>
<td>{'inherited' if s.get('inherited') else 're-read this session'}</td></tr>""" for s in all_sources)
    body = f"""
<p class="sub">Only official publishers: the league, tour, governing body or its own data service.
Aggregators, media outlets and betting sites are never used as verification.</p>
<table><thead><tr><th>ID</th><th>Publisher</th><th>URL</th><th>Observed (UTC)</th><th>What was read</th><th>Channel</th></tr></thead>
<tbody>{rows}</tbody></table>
<div class="note">Sandbox egress outside the package registries and GitHub is closed, so every page above was
retrieved through the agent's web-fetch tool. The recorded time is the observation window, not an
invented HTTP timestamp.</div>
"""
    (OUT / 'sources.html').write_text(page('Sources', '', body, 'sources.html'))

    # ---------------- methodology
    body = f"""
<h2>Inputs</h2>
<p>Team-season totals only: games played, wins, losses, overtime losses, goals or points for and against.
All from the league's own feed, all read in a single observation window on 22 October 2026.</p>

<h2>Ratings</h2>
<p>Attack and defence are shrunk toward the league mean with weight <code>k = GP/(GP+K)</code>:
K = 12 games for NHL goals, K = 8 for EuroLeague points. Every club has played 6–12 games, so an
unshrunk nine-game goal rate would be mostly noise. Expected scoring for a side is its adjusted attack
plus the opponent's adjusted defence minus the league mean, plus a home edge (0.10 goals NHL,
1.5 points EuroLeague).</p>

<h2>Distributions</h2>
<ul>
<li><strong>NHL</strong>: independent Poisson goals per side. Moneyline = regulation win plus half the tie mass.
Puck line uses the regulation margin and converts a tie into a one-goal overtime win. Totals use a Poisson
total; team totals use each side's own Poisson mean.</li>
<li><strong>EuroLeague</strong>: margin and total modelled as Normal around the expected values, with
dispersions of 12.0 and 15.5 points. Those are documented assumptions, not fitted parameters.</li>
<li><strong>MLB</strong>: log5 on the two official winning percentages. No run line, no total.</li>
</ul>

<h2>Pricing</h2>
<p><code>fair_decimal = 1/p</code>; the American price is derived from the same probability. No margin, no
clipping, no rounding inside the calculation. A zero-margin price is a statement of the model's
probability, not a quote anyone is obliged to honour.</p>

<h2>Confidence rule</h2>
<p>High requires all three of: probability strictly above 70%; fair American inside [−250, +10000]; and a
unique ≥30-word prediction supported by verified player-level facts. Medium is 60–70%, or an in-band
selection without the third condition. Low is everything else. “Outside window” is a separate flag, not a
confidence tier.</p>

<h2>What this desk does not know</h2>
<ul>
<li>No bookmaker price, availability or margin was read. No edge is claimed.</li>
<li>No injury, suspension, lineup, travel or rest information was imported.</li>
<li>No backtest against settled results was run; the probabilities are not calibrated frequencies.</li>
<li>Postseason MLB form is not modelled; the records are regular season.</li>
<li>Early-season NHL and EuroLeague samples are small and the shrinkage is a judgement, which is why the
sensitivity table exists.</li>
</ul>
"""
    (OUT / 'methodology.html').write_text(page('Methodology and limits', '', body, 'methodology.html'))

    # ---------------- sport pages
    for slug, meta in SPORT_META.items():
        priced = [x for x in desk['priced'] if x['sport'] == slug]
        inherited = [x for x in desk['inherited'] if x['sport'] == slug]
        parts = [f'<p class="sub">Official hub: <a href="{html.escape(meta[2])}">{html.escape(meta[2])}</a> · '
                 f'OLBG route id {meta[1]} · discovery only, never verification.</p>']
        if priced:
            parts.append(f'<h2>Priced matches ({len(priced)})</h2>')
            for row in priced:
                rows = ''.join(f"<tr><td>{html.escape(mk['market'])}</td><td>{html.escape(o['selection'])}</td>"
                               f"<td class='num'>{o['probability']*100:.2f}%</td><td class='num'>{o['american_display']}</td>"
                               f"<td>{tag(o['tier'])}</td></tr>"
                               for mk in row['markets'] for o in mk['outcomes'])
                parts.append(f"""<h3>{html.escape(row['home'])} v {html.escape(row['away'])}
<span class="small">{html.escape(row['start_utc'])} · {html.escape(row['venue'] or '')}</span></h3>
<table><thead><tr><th>Market</th><th>Selection</th><th>Probability</th><th>Fair American</th><th>Tier</th></tr></thead>
<tbody>{rows}</tbody></table>""")
        if inherited:
            rows = ''.join(f"<tr><td>{html.escape(i['participant_a'] or '—')} v {html.escape(i['participant_b'] or '—')}</td>"
                           f"<td class='num'>{html.escape(i['start_utc'] or i['date'] or '—')}</td>"
                           f"<td><span class='tag none'>NOT RE-READ</span> <span class='small'>{html.escape(i['note'])}</span></td></tr>"
                           for i in inherited)
            parts.append(f"<h2>Listed, unpriced ({len(inherited)})</h2>"
                         "<table><thead><tr><th>Fixture</th><th>Date / start</th><th>Status</th></tr></thead>"
                         f"<tbody>{rows}</tbody></table>")
        if not priced and not inherited:
            parts.append('<div class="note warnbox">No participant-level official input was obtained for this '
                         'category in this session. Nothing is filled in. See <a href="../flagged.html">'
                         'Flagged for review</a>.</div>')
        body = ''.join(parts)
        (OUT / 'sports').mkdir(exist_ok=True)
        (OUT / 'sports' / f'{slug}.html').write_text(
            page(meta[0], '../', body, None, f'Category page · {meta[0]} · session 9dc28d1e'))


def write_data(desk):
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / 'desk.json').write_text(json.dumps(desk, indent=1, ensure_ascii=False) + '\n')
    with (DATA / 'priced.csv').open('w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['fixture_id', 'sport', 'home', 'away', 'start_utc', 'market', 'selection',
                    'probability', 'fair_decimal', 'american', 'tier', 'source_ids'])
        for row in desk['priced']:
            for mk in row['markets']:
                for o in mk['outcomes']:
                    w.writerow([row['fixture_id'], row['sport'], row['home'], row['away'], row['start_utc'],
                                mk['market'], o['selection'], f"{o['probability']:.6f}",
                                f"{o['fair_decimal']:.6f}", o['american_display'], o['tier'],
                                ';'.join(row['source_ids'])])
    with (DATA / 'predictions.csv').open('w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['fixture_id', 'selection', 'words', 'text'])
        for p in desk['predictions']:
            w.writerow([p['fixture_id'], p['selection'], len(p['text'].split()), p['text']])


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--now', default=None)
    args = ap.parse_args()
    from datetime import datetime, timezone
    NOW = args.now or datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    desk = build()
    write_data(desk)
    render(desk)
    print('built', desk['counts'])
