#!/usr/bin/env python3
"""Offline, fail-closed release audit. Never recertifies remote sporting facts.

Usage: python scripts/release_audit.py --as-of 2026-10-22T07:30:00Z
Stored inputs are retained for traceability; approved values stay null until an
independent official-source check can be implemented. No invented fallback data.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {'soccer','football','american-football','boxing','ufc','mma','ufc-mma',
            'hurling','horse-racing','cycling','specials','entertainment'}

def instant(value):
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise ValueError('Timezone required')
    return dt

def in_window(value):
    try:
        n = float(value)
        return -250 <= n <= -100 or 100 <= n <= 10000
    except (ValueError, TypeError):
        return False

def audit(fixtures, lines, predictions, as_of):
    now = instant(as_of)
    line_map = {r['id']: r for r in lines}
    pred_map = {r['match_id']: r for r in predictions}
    rows = []
    for f in fixtures:
        line, pred = line_map.get(f['id'], {}), pred_map.get(f['id'])
        flags = ['Official evidence not re-fetched in this session; current facts unverified.']
        past = False
        if f.get('start_utc'):
            try:
                past = instant(f['start_utc']) <= now
                if past:
                    flags.append('Stored start has passed; result and current event status are unknown.')
            except ValueError:
                flags.append('Stored start timestamp is invalid or lacks timezone.')
        else:
            flags.append('Exact start time missing; upcoming status cannot be confirmed.')
        if f.get('sport') in EXCLUDED:
            flags.append('Excluded sport; must not enter approved coverage.')
        if not f.get('sources'):
            flags.append('Official source link missing.')
        if line.get('confidence') == 'high':
            p = line.get('pick_probability')
            if not isinstance(p, (int, float)) or not 0.70 < p <= 1:
                flags.append('Legacy High probability does not exceed 70%; not eligible under strict research screen.')
            if not in_window(line.get('pick_american')):
                flags.append('Legacy High price outside valid -250 to +10000 American odds window.')
            if not pred or len(pred.get('text', '').split()) < 30:
                flags.append('High prediction absent or fewer than 30 whitespace-delimited words.')
        if line:
            flags.append('Model calibration and current inputs not validated; no approved betting selection.')
        if f['id'] == 'nhl-2026020152':
            flags.append('Stored prose says fourteen-goal swing, but stored -7 versus -19 implies 12; neither record freshly confirmed.')
        rows.append({
            'id': f['id'], 'sport': f.get('sport'),
            'archived_label': f.get('home','') + (' vs ' + f['away'] if f.get('away') else ''),
            'archived_start_utc': f.get('start_utc'), 'stored_start_passed': past,
            'prior_status': f.get('status'), 'legacy_confidence': line.get('confidence'),
            'legacy_probability': line.get('pick_probability'),
            'legacy_american': line.get('pick_american'),
            'current_verification': 'unverified', 'verified_start_utc': None,
            'verified_home': None, 'verified_away': None, 'verified_form': None,
            'approved_selection': None, 'approved_probability': None,
            'approved_confidence': None, 'approved_prediction': None,
            'sources': f.get('sources', []), 'flags': flags,
        })
    return {'as_of': as_of, 'scope': 'Primary dataset only; companion desks not recertified.',
            'method': 'Offline structural and arithmetic audit, not official-source verification.',
            'network_limit': 'OLBG and official sports hosts outside sandbox outbound allowlist. Direct OLBG and NHL HTTPS probes failed (curl exit 35).',
            'approved_picks': 0, 'rows': rows,
            'counts': {'rows': len(rows), 'stored_start_passed': sum(r['stored_start_passed'] for r in rows),
                       'legacy_high': sum(r['legacy_confidence'] == 'high' for r in rows),
                       'unverified': len(rows)}}

def render(report):
    e = lambda v: escape(str(v if v is not None else ''))
    sports = Counter(r['sport'] for r in report['rows'])
    nav = ''.join(f'<a href="#sport-{e(s)}">{e(s)} ({n})</a> ' for s,n in sorted(sports.items()))
    sections = []
    for sport in sorted(sports):
        body = []
        for r in report['rows']:
            if r['sport'] != sport:
                continue
            links = ' · '.join(f'<a href="{e(s["url"])}">{e(s.get("name", "Official source"))}</a>' for s in r['sources'] if s.get('url','').startswith('https://'))
            flags = '<ul>' + ''.join(f'<li>{e(f)}</li>' for f in r['flags']) + '</ul>'
            body.append(f'<tr><td>{e(r["id"])}<br>{e(r["archived_label"])}</td><td>{e(r["archived_start_utc"])}</td><td>Unverified</td><td></td><td></td><td>{flags}</td><td>{links}</td></tr>')
        sections.append(f'<section id="sport-{e(sport)}"><h2>{e(sport)}</h2><div class="scroll"><table><thead><tr><th>Archived record (not recertified)</th><th>Stored start UTC</th><th>Current verification</th><th>Verified start UTC</th><th>Approved pick</th><th>Flagged for Review</th><th>Official source links (not re-fetched)</th></tr></thead><tbody>{"".join(body)}</tbody></table></div></section>')
    c = report['counts']
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Flagged for Review · Release evidence audit</title>
<style>body{{font:16px/1.6 system-ui,sans-serif;background:#0c1422;color:#e8eef7;margin:0}}main{{max-width:1400px;margin:auto;padding:32px}}a{{color:#86d8ff}}nav{{display:flex;gap:16px;flex-wrap:wrap}}h1{{font-size:2.4rem}}.notice{{background:#342d1b;border-left:4px solid #ffcb67;padding:20px}}.stats{{display:flex;gap:20px;flex-wrap:wrap;margin:24px 0}}.stats div{{background:#18283c;padding:20px;border-radius:10px}}strong{{font-size:1.3em}}.scroll{{overflow:auto}}table{{border-collapse:collapse;width:100%;font-size:14px}}td,th{{padding:14px;text-align:left;vertical-align:top;border-bottom:1px solid #33445b;min-width:100px}}th{{background:#18283c}}td:first-child{{min-width:210px}}td:nth-child(6){{min-width:320px}}li{{margin-bottom:8px}}section{{margin-top:36px}}select,input{{font:inherit;padding:8px}}[hidden]{{display:none!important}}</style></head><body><main>
<nav><a href="index.html">Archived dashboard</a><a href="flagged.html">Prior findings</a><a href="methodology.html">Legacy methodology</a><a href="reports/RELEASE_AUDIT.json">Download row-level JSON</a></nav>
<h1>Flagged for Review</h1><p>Release evidence audit · {e(report['as_of'])}</p>
<div class="notice"><b>No fresh sporting facts or picks certified.</b> {e(report['network_limit'])} Source links are provided for review, not proof of this session’s verification. Blank approved fields mean unverified. Archived identifiers, participants, times and status labels are prior repository claims only.</div>
<div class="stats"><div><strong>{c['rows']}</strong><br>Archived primary records</div><div><strong>{c['unverified']}</strong><br>Not freshly verified</div><div><strong>{c['stored_start_passed']}</strong><br>Stored starts passed</div><div><strong>0</strong><br>Approved current picks</div></div>
<h2>Findings and limits</h2><ul><li>The existing primary model permits a 60% conviction floor for High. This audit flags High probabilities not exceeding 70% as a strict research screen, not an empirically calibrated confidence rule.</li><li>Market-implied probability is not an independent forecast. -250 implies 71.43%; +10000 implies 0.99%. An independent probability above 70% at a longer price would require justified evidence of an edge, not selecting an artificial handicap to meet a label.</li><li>Model estimates cannot be verified as facts by an official fixture link. Calibration, settlement rules, injuries, recent form and market completeness are not established by this offline audit.</li><li>A passed stored start is not evidence that a match finished. No result is inferred.</li><li>Stored Buffalo prose says fourteen-goal swing although the stored differentials imply 12. The report flags rather than rewrites unsupported prose.</li><li>No full live OLBG coverage claim, new official verification, or new human prediction is made. Companion desks remain historical independent workspaces and are outside this audit.</li></ul>
<label for="query">Filter archived records and findings</label> <input id="query" type="search" placeholder="Team, sport or finding"><p id="result" aria-live="polite"></p><nav aria-label="Sport categories">{nav}</nav>
{''.join(sections)}<p>Reproduce: <code>python scripts/release_audit.py --as-of {e(report['as_of'])}</code>. Checks are local and do not certify external URLs or facts.</p></main>
<script>document.getElementById('query').addEventListener('input',function(){{let n=0;const q=this.value.toLowerCase();document.querySelectorAll('tbody tr').forEach(r=>{{r.hidden=!r.textContent.toLowerCase().includes(q);if(!r.hidden)n++}});document.querySelectorAll('section').forEach(s=>s.hidden=![...s.querySelectorAll('tbody tr')].some(r=>!r.hidden));document.getElementById('result').textContent=n+' records shown';}});</script></body></html>'''

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--as-of', default=datetime.now(timezone.utc).isoformat())
    args = parser.parse_args()
    paths = ['data/fixtures.json','data/lines.json','data/predictions.json']
    fixtures, lines, preds = [json.loads((ROOT / p).read_text()) for p in paths]
    report = audit(fixtures['matches'], lines['lines'], preds['predictions'], args.as_of)
    report['input_sha256'] = {p: sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
    (ROOT/'reports/RELEASE_AUDIT.json').write_text(json.dumps(report, indent=2)+'\n')
    (ROOT/'release-review.html').write_text(render(report))
    print(json.dumps(report['counts']), 'approved picks:', report['approved_picks'])

if __name__ == '__main__':
    main()
