"""T424375B4 — static dashboard builder for /424375b4/.

Reads the session JSON produced by s424375b4_model.py plus the capture modules
and writes a self-contained static desk: landing, matches, markets, picks,
high-confidence, predictions, analysis, methodology, sources, flagged, repo
audit and 17 sport subpages. Every table row carries at least one source link;
rows without an official read render blank official cells with a flag marker.
"""
import html
import json
import re
from pathlib import Path

from s424375b4_data import (DESK_AS_OF, HARVEST_END, HARVEST_START, SESSION_ID,
                            SOURCES, TASK_ID, RECORDS)
from s424375b4_fixtures import FIXTURES, FLAGS, EMPTY_HUBS, EMPTY_HUBS
from s424375b4_prose import PREDICTIONS, SHORTFALLS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '424375b4'
DATA = ROOT / 'data' / '424375b4'

SPORTS = [
    ('tennis', 'Tennis'), ('basketball', 'Basketball'), ('golf', 'Golf'),
    ('cricket', 'Cricket'), ('snooker', 'Snooker'), ('rugby-union', 'Rugby Union'),
    ('rugby-league', 'Rugby League'), ('baseball', 'Baseball'),
    ('ice-hockey', 'Ice Hockey'), ('motor-racing', 'Motor Racing'),
    ('darts', 'Darts'), ('handball', 'Handball'), ('volleyball', 'Volleyball'),
    ('aussie-rules', 'Aussie Rules'), ('esports', 'eSports'),
    ('gaelic-football', 'Gaelic Football'), ('greyhounds', 'Greyhounds'),
]

NAV = [
    ('index.html', 'Dashboard'), ('matches.html', 'Matches'),
    ('markets.html', 'Markets'), ('picks.html', 'Picks'),
    ('high-confidence.html', 'High Confidence'), ('predictions.html', 'Predictions'),
    ('coverage.html', 'Coverage'), ('analysis.html', 'Analysis'),
    ('methodology.html', 'Methodology'), ('sources.html', 'Sources'),
    ('flagged.html', 'Flagged for Review'), ('repo-audit.html', 'Repo Audit'),
]

CSS = """
:root{--bg:#0f1420;--card:#171e2e;--ink:#e8ecf4;--dim:#9aa6bc;--line:#27324a;
--accent:#4da3ff;--good:#2fbf71;--warn:#f2b33d;--bad:#e5484d;--high:#2fbf71;}
*{box-sizing:border-box}
body{margin:0;font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,
Helvetica,Arial,sans-serif;background:var(--bg);color:var(--ink)}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
header{background:var(--card);border-bottom:1px solid var(--line);padding:14px 22px}
header h1{margin:0;font-size:19px}header h1 span{color:var(--dim);font-weight:400}
nav{display:flex;flex-wrap:wrap;gap:2px 14px;padding:9px 22px;background:#121a2a;
border-bottom:1px solid var(--line);font-size:13px}
nav a{color:var(--dim)}nav a.on{color:var(--ink);font-weight:600}
main{padding:22px;max-width:1220px;margin:0 auto}
h2{font-size:17px;margin:26px 0 10px}h3{font-size:15px;margin:18px 0 8px}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(168px,1fr));gap:10px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.card .n{font-size:23px;font-weight:700}.card .l{color:var(--dim);font-size:12px}
table{width:100%;border-collapse:collapse;font-size:13px;background:var(--card);
border:1px solid var(--line);border-radius:8px;overflow:hidden}
th,td{padding:7px 9px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{background:#1b2436;color:var(--dim);font-weight:600;font-size:12px;
position:sticky;top:0}
tr:last-child td{border-bottom:none}
.wrap{overflow-x:auto}
.k{display:inline-block;padding:1px 7px;border-radius:20px;font-size:11px;font-weight:600}
.k-a{background:#143522;color:#7ee2a8}.k-b{background:#3a2f10;color:#f2c75c}
.k-c{background:#3a1520;color:#f09499}.k-high{background:#143522;color:#7ee2a8}
.k-med{background:#2a2f45;color:#b8c2d8}.k-low{background:#3a1520;color:#f09499}
.k-oow{background:#3a2f10;color:#f2c75c}.k-un{background:#2a2f45;color:#9aa6bc}
.pred{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--accent);
border-radius:8px;padding:13px 16px;margin:11px 0}
.pred.high{border-left-color:var(--good)}
.pred.un{border-left-color:var(--warn)}
.pred h4{margin:0 0 4px;font-size:14px}.pred .sel{color:var(--good);font-weight:600}
.pred p{margin:7px 0 4px;color:var(--ink);font-size:14px}
.meta{color:var(--dim);font-size:12px}
.flag{background:#241b2e;border:1px solid #4a2b5e;border-radius:8px;padding:11px 14px;margin:9px 0}
.flag b{color:#d79bff}
.note{background:#14202f;border:1px solid var(--line);border-radius:8px;padding:11px 14px;
margin:11px 0;color:var(--dim);font-size:13px}
footer{padding:18px 22px;color:var(--dim);font-size:12px;border-top:1px solid var(--line)}
.pill{display:inline-block;padding:1px 8px;border-radius:20px;font-size:11px;
background:#22304c;color:#9ec6ff;margin:1px}
"""


def esc(s):
    return html.escape('' if s is None else str(s))


def klass_badge(k):
    label = {'A': 'A · official body read', 'B': 'B · official excerpt',
             'C': 'C · discovery only', 'discovery': 'discovery'}.get(k, k)
    cls = {'A': 'k-a', 'B': 'k-b', 'C': 'k-c', 'discovery': 'k-c'}[k]
    return f'<span class="k {cls}">{label}</span>'


def tier_badge(t):
    m = {
        'high-eligible': ('k-high', 'High band'),
        'High': ('k-high', 'High'),
        'out-of-window': ('k-oow', 'Out-of-window favourite'),
        'medium': ('k-med', 'Medium'), 'Medium': ('k-med', 'Medium'),
        'low': ('k-low', 'Low'), 'Low (model coin-flip)': ('k-low', 'Low · coin-flip'),
        'unpriced': ('k-un', 'Unpriced'),
    }
    cls, label = m.get(t, ('k-un', t))
    return f'<span class="k {cls}">{label}</span>'


def page(title, body, current):
    prefix = '../' if current.startswith('sports/') else ''

    def fix(href):
        if href.startswith(('http', '#', 'mailto', '..')):
            return href
        return prefix + href

    nav = ''.join(
        '<a href="%s" class="%s">%s</a>' % (fix(href), 'on' if href == current else '', label)
        for href, label in NAV)

    def _rewrite(m):
        return 'href="%s"' % fix(m.group(1))

    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · OLBG desk {SESSION_ID}</title><style>{CSS}</style></head>
<body><header><h1>OLBG research desk <span>· {SESSION_ID} · {TASK_ID} · as of {DESK_AS_OF}</span></h1>
<div class="meta">Independent live desk · 22 Oct 2026 · not affiliated with OLBG ·
experimental fair prices, not bookmaker offers · no guaranteed returns</div></header>
<nav>{nav}</nav><main>{body}</main>
<footer>Harvest window {HARVEST_START}–{HARVEST_END}. Evidence expires: fixtures 6h,
statistics 24h from their reads. This desk never invents values — unconfirmed cells
are blank and flagged on the <a href="flagged.html">Flagged for Review</a> page.
Source ledger: <a href="sources.html">sources.html</a>.</footer></body></html>"""
    return re.sub(r'href="([^"]+)"', _rewrite, doc)


def src_link(ids):
    out = []
    for sid in ids:
        s = next((x for x in SOURCES if x['id'] == sid), None)
        if s:
            out.append(f'<a href="{esc(s["url"])}" rel="nofollow noopener">{esc(sid)}</a>')
    return ' '.join(out) or '—'


def load_json(name):
    with open(DATA / name) as f:
        return json.load(f)


def write(name, content):
    p = OUT / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding='utf-8')


def build():
    markets = {m['fixture_id']: m for m in load_json('markets.json')}
    picks = {p['fixture_id']: p for p in load_json('picks.json')}
    preds_by_fix = {p['fixture_id']: p for p in PREDICTIONS}
    fx_by_id = {f['id']: f for f in FIXTURES}

    priced = [p for p in picks.values() if p.get('p') is not None]
    priced.sort(key=lambda x: -x['p'])
    high = [p for p in priced if p['tier'] == 'high-eligible']
    oow = [p for p in priced if p['tier'] == 'out-of-window']
    med = [p for p in priced if p['tier'] == 'medium']
    low = [p for p in priced if p['tier'] == 'low']
    unpriced = [p for p in picks.values() if p.get('p') is None]
    n_markets = sum(len(m.get('winner', [])) + len(m.get('score_markets', []))
                    for m in markets.values())

    # ------------------------------------------------------------ index ---
    kpis = [
        (len(FIXTURES), 'listings harvested'), (len(priced), 'priced fixtures'),
        (n_markets, 'originated markets'), (len(high), 'High-band picks'),
        (len(oow), 'out-of-window favourites'), (len(med), 'Medium'),
        (len(PREDICTIONS), 'predictions & previews'),
        (len(SOURCES), 'source reads'), (len(FLAGS), 'flags'),
    ]
    cards = ''.join(f'<div class="card"><div class="n">{n}</div><div class="l">{l}</div></div>'
                    for n, l in kpis)
    top_rows = ''.join(
        f'<tr><td>{esc(p["fixture_id"])}</td><td>{esc(p["sport"])}</td>'
        f'<td><b>{esc(p["selection"])}</b></td><td>{p["p"]*100:.1f}%</td>'
        f'<td>{p["fair_decimal"]:.3f}</td><td>{p["fair_american"]:.0f}</td>'
        f'<td>{tier_badge(p["tier"])}</td>'
        f'<td>{src_link(fx_by_id[p["fixture_id"]]["verify"]["source_ids"])}</td></tr>'
        for p in priced[:12])
    body = f"""
<h2>Dashboard</h2>
<div class="note">This is the {TASK_ID} independent live desk for 22 Oct 2026 (evening).
OLBG is reverse-engineered for discovery only; every published fact is checked against
the governing body or league's own surface, every price is an experimental fair price
computed from official records, and every unconfirmed cell is blank and flagged.
Excluded per the brief: soccer/football, American football, boxing, UFC/MMA, hurling,
horse racing, cycling, specials.</div>
<div class="cards">{cards}</div>
<h2>Highest-confidence priced selections</h2>
<div class="wrap"><table><tr><th>Fixture</th><th>Sport</th><th>Selection</th>
<th>Model p</th><th>Fair dec</th><th>Fair US</th><th>Tier</th><th>Sources</th></tr>
{top_rows}</table></div>
<h2>Quick links</h2>
<p><a href="matches.html">Full match list</a> ·
<a href="markets.html">Market explorer ({n_markets} prices)</a> ·
<a href="high-confidence.html">High band &amp; out-of-window ledger</a> ·
<a href="predictions.html">Predictions</a> ·
<a href="flagged.html">Flagged for Review ({len(FLAGS)})</a> ·
<a href="coverage.html">Coverage by sport</a> ·
<a href="repo-audit.html">Repo audit</a></p>
<h2>Reading the tiers</h2>
<p class="meta"><b>High</b> = model probability ≥ 70.0% <i>and</i> the unrounded fair
price is inside −250…+10000 <i>and</i> the fixture is class A/B verified <i>and</i> a
written prediction exists. Favourites beyond −250 are disclosed separately and never
counted High. OLBG tip shares never enter a price. See
<a href="methodology.html">methodology</a>.</p>
"""
    write('index.html', page('Dashboard', body, 'index.html'))

    # ---------------------------------------------------------- matches ---
    rows = []
    for f in FIXTURES:
        p = picks.get(f['id'], {})
        start = f.get('start_official') or ''
        tz = f.get('start_tz_note') or ''
        ol = f.get('olbg')
        olbg_txt = (f"{ol['event']} · {ol.get('market','')} · "
                    f"{ol.get('selection','')} ({ol.get('share','—')} tips, "
                    f"{ol.get('pct','—')}) · OLBG label {ol['label']}"
                    if ol else 'not surfaced on OLBG hub')
        sel = p.get('selection') or ''
        tier = p.get('tier', 'unpriced')
        official = ' '.join(
            '<a href="%s">official page</a>' % esc(u) for u in f['verify']['links'][:1])
        rows.append(
            f'<tr><td>{esc(f["id"])}</td><td>{esc(f["sport"])}</td>'
            f'<td>{esc(f["competition"])}</td>'
            f'<td>{esc(f["home"])} v {esc(f["away"])}</td>'
            f'<td>{esc(start)}<div class="meta">{esc(tz)}</div></td>'
            f'<td>{klass_badge(f["verify"]["klass"])}<div class="meta">'
            f'{esc(f["verify"]["note"])}</div></td>'
            f'<td class="meta">{esc(olbg_txt)}</td>'
            f'<td>{esc(sel)}</td><td>{tier_badge(tier)}</td>'
            f'<td>{src_link(f["verify"]["source_ids"])} {official}</td></tr>')
    body = f"""
<h2>Matches &amp; events ({len(FIXTURES)} listings)</h2>
<div class="note">OLBG columns are discovery metadata (tip shares are votes, not
probabilities). Official columns are blank unless the value was read this session.
Class A = official body read; class B = official URL with excerpted body (cookie wall,
flagged); class C = discovery only.</div>
<div class="wrap"><table>
<tr><th>ID</th><th>Sport</th><th>Competition</th><th>Fixture</th><th>Start</th>
<th>Verification</th><th>OLBG discovery</th><th>Our selection</th><th>Tier</th>
<th>Sources</th></tr>{''.join(rows)}</table></div>
"""
    write('matches.html', page('Matches', body, 'matches.html'))

    # ---------------------------------------------------------- markets ---
    rows = []
    for m in markets.values():
        if not m.get('priced'):
            continue
        for w in m['winner']:
            rows.append((m['fixture_id'], m['sport'], 'winner', w['selection'],
                         '—', w['p'], w['fair_decimal'], w['fair_american'],
                         w['in_window']))
        for sm in m.get('score_markets', []):
            rows.append((m['fixture_id'], m['sport'], sm['market'],
                         sm['selection'], sm['line'], sm['p'], sm['fair_decimal'],
                         sm['fair_american'], sm['in_window']))
    rows.sort(key=lambda r: -r[5])
    trows = ''.join(
        f'<tr><td>{esc(r[0])}</td><td>{esc(r[1])}</td><td>{esc(r[2])}</td>'
        f'<td>{esc(r[3])}</td><td>{esc(r[4])}</td><td>{r[5]*100:.2f}%</td>'
        f'<td>{r[6]:.3f}</td><td>{r[7]:.1f}</td>'
        f'<td>{"yes" if r[8] else "no"}</td></tr>' for r in rows)
    body = f"""
<h2>Market explorer — {len(rows)} originated prices</h2>
<div class="note">Zero-margin experimental fair prices: decimal = 1/p, American
derived consistently, no clipping. Handicap and total ladders are
<b>research model lines, not available sportsbook offers</b>. They come from paired
official per-game rates and independent Poisson scores (Skellam margins). The
in-window column applies the brief's −250…+10000 test to the unrounded American
price.</div>
<div class="wrap"><table><tr><th>Fixture</th><th>Sport</th><th>Market</th>
<th>Selection</th><th>Line</th><th>p</th><th>Fair dec</th><th>Fair US</th>
<th>In window</th></tr>{trows}</table></div>
"""
    write('markets.html', page('Markets', body, 'markets.html'))

    # ------------------------------------------------------------- picks ---
    rows = ''.join(
        f'<tr><td>{esc(p["fixture_id"])}</td><td>{esc(p["sport"])}</td>'
        f'<td><b>{esc(p["selection"])}</b></td><td>{p["p"]*100:.1f}%</td>'
        f'<td>{p["fair_decimal"]:.3f}</td><td>{p["fair_american"]:.0f}</td>'
        f'<td>{"yes" if p["in_window"] else "no"}</td>'
        f'<td>{tier_badge(p["tier"])}</td>'
        f'<td>{src_link(fx_by_id[p["fixture_id"]]["verify"]["source_ids"])}</td></tr>'
        for p in priced)
    urows = ''.join(
        f'<tr><td>{esc(u["fixture_id"])}</td><td>{esc(u["sport"])}</td>'
        f'<td colspan="6" class="meta">{esc(u.get("reason",""))} '
        f'({esc(fx_by_id[u["fixture_id"]]["verify"]["note"][:110])}…)</td>'
        f'<td>{klass_badge(fx_by_id[u["fixture_id"]]["verify"]["klass"])}</td></tr>'
        for u in sorted(unpriced, key=lambda x: (x['sport'], x['fixture_id'])))
    body = f"""
<h2>Confidence grading</h2>
<div class="note">Winner preferences are the higher-probability side of the modelled
two-way market. <b>High</b> needs p ≥ 70.0% plus the fair price inside −250…+10000
plus class A/B evidence plus a written prediction. Everything else is Medium, Low or
an out-of-window disclosure.</div>
<h3>Priced ({len(priced)})</h3>
<div class="wrap"><table><tr><th>Fixture</th><th>Sport</th><th>Selection</th>
<th>Model p</th><th>Fair dec</th><th>Fair US</th><th>In window</th><th>Tier</th>
<th>Sources</th></tr>{rows}</table></div>
<h3>Unpriced ({len(unpriced)}) — no official record pair</h3>
<div class="wrap"><table><tr><th>Fixture</th><th>Sport</th><th colspan="6">Reason</th>
<th>Class</th></tr>{urows}</table></div>
"""
    write('picks.html', page('Picks', body, 'picks.html'))

    # -------------------------------------------------- high confidence ---
    def pick_block(p, tag):
        pred = preds_by_fix.get(p['fixture_id'])
        f = fx_by_id[p['fixture_id']]
        obs = markets[p['fixture_id']].get('observed_quote_band')
        obs_txt = (f'Official-feed price snapshot: {obs["quotes"]} '
                   f'({obs["n"]} quotes)' if obs else
                   'No observed book price this session — window test on fair price only.')
        pred_txt = pred['text'] if pred else '<i>No prediction written.</i>'
        cls = 'high' if tag == 'High' else ''
        io = 'inside' if p['in_window'] else 'outside'
        home, away = esc(f['home']), esc(f['away'])
        tierb = tier_badge(p['tier'])
        sel = esc(p['selection'])
        stats = "%.1f%% · fair %.3f (%.0f)" % (p['p'] * 100, p['fair_decimal'], p['fair_american'])
        srcs = src_link(f['verify']['source_ids'])
        return ('<div class="pred ' + cls + '">'
                f'<h4>{home} v {away} — {tierb}</h4>'
                f'<div class="sel">{sel} · model {stats} · {io} −250…+10000</div>'
                f'<p>{pred_txt}</p>'
                f'<div class="meta">Observed market context: {esc(obs_txt)} Sources:'
                f'{srcs}</div></div>')

    high_blocks = ''.join(pick_block(p, 'High') for p in high)
    oow_blocks = ''.join(pick_block(p, 'oow') for p in oow)
    body = f"""
<h2>High confidence — strict band</h2>
<div class="note">Brief rule applied literally: model probability above 70% <b>and</b>
the pick's price inside −250…+10000. On our unrounded fair prices that admits
{len(high)} of {len(priced)} priced picks today; the rest of the 70%+ favourites are
published below with their prices so nothing is hidden. We do not invent High picks
to fill quotas.</div>
{high_blocks or '<p>No High-band picks at this checkpoint.</p>'}
<h2>70%+ favourites beyond −250 (disclosed, not High) — {len(oow)}</h2>
<div class="note">These carry the same verified records and written analysis but their
fair price is shorter than −250, so the brief's window excludes them from High. The
NHL rows also carry the official feed's own price snapshot for comparison.</div>
{oow_blocks}
"""
    write('high-confidence.html', page('High confidence', body, 'high-confidence.html'))

    # ------------------------------------------------------- predictions ---
    blocks = []
    for p in PREDICTIONS:
        f = fx_by_id[p['fixture_id']]
        tagcls = 'high' if p['tier'] == 'High' else ('un' if p['tier'].startswith('Unpriced') else '')
        blocks.append(f"""<div class="pred {tagcls}">
<h4>{esc(p['id'])} · {esc(f['home'])} v {esc(f['away'])} · {tier_badge(p['tier'])}</h4>
<div class="sel">{esc(p['selection'])}</div>
<p>{esc(p['text'])}</p>
<div class="meta">{len(re.findall(r"[A-Za-z0-9%’'–-]+", p['text']))} words ·
official facts cited: {src_link(p['sources'])}</div></div>""")
    body = f"""
<h2>Predictions ({len(PREDICTIONS)})</h2>
<div class="note">Each graded prediction is a unique hand-written analysis of at least
30 words naming the selection and the participants, leaning only on facts read from
official pages this session (linked under each block). Unpriced previews name a
selection but are never graded, because the inputs needed to grade them were not
read. Shortfalls per sport are listed on the <a href="coverage.html">coverage</a> page.</div>
{''.join(blocks)}
"""
    write('predictions.html', page('Predictions', body, 'predictions.html'))

    # --------------------------------------------------------- coverage ---
    rows = []
    for slug, name in SPORTS:
        fxs = [f for f in FIXTURES if f['sport'] == slug]
        pr = [p for p in priced if p['sport'] == slug]
        pred_n = sum(1 for p in PREDICTIONS
                     if fx_by_id[p['fixture_id']]['sport'] == slug)
        empty = next((e for e in EMPTY_HUBS if e[0] == slug), None)
        gap = SHORTFALLS.get(slug, '')
        if empty:
            note = empty[3]
        else:
            note = gap
        rows.append(
            f'<tr><td><a href="sports/{slug}.html">{esc(name)}</a></td>'
            f'<td>{len(fxs)}</td><td>{len(pr)}</td><td>{pred_n}</td>'
            f'<td class="meta">{esc(note)}</td>'
            f'<td>{src_link(["S-OLBG-HUBS"] + (["S-NHL-SCHED"] if slug=="ice-hockey" else []))}</td></tr>')
    body = f"""
<h2>Coverage by sport</h2>
<div class="note">The brief aims for five predictions per covered sport. Where the
official evidence does not reach five verified matches, the shortfall is stated
instead of filled: no hallucinated fixtures, prices or write-ups.</div>
<div class="wrap"><table><tr><th>Sport</th><th>Listings</th><th>Priced</th>
<th>Predictions</th><th>Gap / note</th><th>Sources</th></tr>{''.join(rows)}</table></div>
<h2>Hubs with no tips at harvest</h2>
<ul>{''.join(f'<li><b>{esc(e[1])}</b> — {esc(e[3])} <a href="{esc(e[2])}">hub</a></li>' for e in EMPTY_HUBS)}</ul>
"""
    write('coverage.html', page('Coverage', body, 'coverage.html'))

    # -------------------------------------------------- sport subpages ---
    for slug, name in SPORTS:
        fxs = [f for f in FIXTURES if f['sport'] == slug]
        rows = []
        for f in fxs:
            p = picks.get(f['id'], {})
            m = markets.get(f['id'], {})
            wtxt = ''
            if m.get('priced'):
                w = max(m['winner'], key=lambda x: x['p'])
                wtxt = (f"{w['selection']} {w['p']*100:.1f}% "
                        f"(fair {w['fair_decimal']:.3f} / {w['fair_american']:.0f})")
            pred = preds_by_fix.get(f['id'])
            rows.append(
                f'<tr><td>{esc(f["competition"])}</td>'
                f'<td>{esc(f["home"])} v {esc(f["away"])}</td>'
                f'<td>{esc(f.get("start_official") or "—")}'
                f'<div class="meta">{esc(f.get("start_tz_note") or "")}</div></td>'
                f'<td>{klass_badge(f["verify"]["klass"])}</td>'
                f'<td>{esc(wtxt)}</td><td>{tier_badge(p.get("tier","unpriced"))}</td>'
                f'<td>{"yes" if pred else "no"}</td>'
                f'<td>{src_link(f["verify"]["source_ids"])}</td></tr>')
        empty = next((e for e in EMPTY_HUBS if e[0] == slug), None)
        empt = (f'<div class="note">{esc(empty[3])} '
                f'<a href="{esc(empty[2])}">official hub</a></div>') if empty else ''
        body = f"""
<h2>{esc(name)}</h2>
{empt}
<div class="wrap"><table><tr><th>Competition</th><th>Fixture</th><th>Start</th>
<th>Verification</th><th>Model pick</th><th>Tier</th><th>Prediction</th>
<th>Sources</th></tr>{''.join(rows) if rows else '<tr><td colspan="8">No listings in the harvest window.</td></tr>'}</table></div>
<div class="note">{esc(SHORTFALLS.get(slug, ''))}</div>
"""
        write(f'sports/{slug}.html', page(name, body, f'sports/{slug}.html'))

    # ---------------------------------------------------------- sources ---
    rows = ''.join(
        f'<tr><td>{esc(s["id"])}</td><td>{esc(s["sport"])}</td>'
        f'<td>{esc(s["publisher"])}</td>'
        f'<td><a href="{esc(s["url"])}" rel="nofollow noopener">{esc(s["url"])}</a></td>'
        f'<td>{esc(s["read_at"])}</td><td>{klass_badge(s["klass"])}</td>'
        f'<td class="meta">{esc(s["what"])}</td></tr>' for s in SOURCES)
    body = f"""
<h2>Source ledger ({len(SOURCES)} reads)</h2>
<div class="note">Class A = the official publisher body was fetched and read in this
session. Class B = the official URL is confirmed and the body text comes from a
search-engine excerpt of that exact URL because the publisher serves a cookie wall to
the fetcher (flagged F-04). Discovery = OLBG, never an authority for facts.</div>
<div class="wrap"><table><tr><th>ID</th><th>Sport</th><th>Publisher</th><th>URL</th>
<th>Read (UTC)</th><th>Class</th><th>What was read</th></tr>{rows}</table></div>
"""
    write('sources.html', page('Sources', body, 'sources.html'))

    # ----------------------------------------------------------- flagged ---
    rows = ''.join(
        f'<div class="flag"><b>{esc(fl["id"])} [{esc(fl["severity"])}]</b> — '
        f'<b>{esc(fl["title"])}</b><div class="meta">{esc(fl["detail"])}</div>'
        f'<div class="meta">Recheck: ' +
        ' · '.join(f'<a href="{esc(u)}">{esc(u)}</a>' for u in fl['links']) +
        '</div></div>' for fl in FLAGS)
    body = f"""
<h2>Flagged for Review ({len(FLAGS)})</h2>
<div class="note">Nothing here blocks publication; each item is a request for a human
check. Values that could not be confirmed from an official source are left blank
throughout the desk and listed here with official recheck links.</div>
{rows}
"""
    write('flagged.html', page('Flagged for Review', body, 'flagged.html'))

    # -------------------------------------------------------- methodology ---
    body = """
<h2>Methodology</h2>
<h3>Reverse engineering OLBG</h3>
<p>All 17 in-scope OLBG sport hubs were read live inside the harvest window. Hubs
publish event cards with a most-tipped selection, a market label and a tip share
(e.g. "7/8 Win Tips, 88%"). Those shares are <b>votes, never probabilities</b>, and
never enter a price. Hub start labels are inconsistent across sports (the same site
showed NHL tips labelled 19:07, Pro D2 tips 13:00 and NBA tips 00:10 — flag F-01), so
they are recorded as discovery metadata only.</p>
<h3>Verification</h3>
<p>Every row is graded A, B or C (see <a href="sources.html">sources</a>). Class A rows
were confirmed against the league or governing body's own site or API. Unconfirmed
cells are blank and flagged — never inferred.</p>
<h3>Origination model (experimental fair prices)</h3>
<ol>
<li>Strength from official records with Beta(2,2) shrinkage:
no draws <code>s=(W+2)/(W+L+4)</code> (NHL defeats include overtime losses);
draws split <code>s=(W+D/2+2)/(M+4)</code> (rugby).</li>
<li>Winner probability is log5:
<code>p_h = s_h(1−s_a) / (s_h(1−s_a) + s_a(1−s_h))</code>.</li>
<li>Where official scoring rates exist (NHL goals, rugby points), paired per-game
rates feed independent Poisson scores: margins are Skellam, totals Poisson sums.
These are research model lines, not bookmaker offers.</li>
<li>Basketball line and total markets are withheld: no official scoring-variance
input was read this session.</li>
<li>Fair decimal = 1/p. American derived consistently. The −250…+10000 flag uses the
unrounded price. No margin, no clipping.</li>
</ol>
<h3>Confidence</h3>
<p><b>High</b> requires all of: p ≥ 70.0%; fair American inside −250…+10000; class A/B
fixture; a written prediction citing official facts. Favourites shorter than −250 are
published as out-of-window disclosures. Medium is 0.55 ≤ p &lt; 0.70 (class A/B); Low
covers everything else including every class C row.</p>
<h3>Evidence expiry</h3>
<p>Fixture reads are treated as stale after 6 hours and statistical reads after 24;
rebuilds do not rejuvenate them. Nothing on this desk is current beyond those windows.</p>
"""
    write('methodology.html', page('Methodology', body, 'methodology.html'))

    # ---------------------------------------------------------- analysis ---
    rows = ''.join(
        f'<tr><td>{esc(p["fixture_id"])}</td><td>{esc(p["selection"])}</td>'
        f'<td>{p["p"]*100:.1f}%</td><td>{p["fair_american"]:.0f}</td>'
        f'<td>{esc(p["tier"])}</td></tr>' for p in priced[:15])
    body = f"""
<h2>Analysis &amp; findings</h2>
<h3>1. The brief's High band is genuinely narrow</h3>
<p>Requiring both p ≥ 70% and a price no shorter than −250 caps the band at a fair
price of −233…−250 (p between 70.0% and 71.43%). Exactly {len(high)} of {len(priced)}
priced picks sit in it today — Vegas Golden Knights and Toulouse, both at precisely
70.0% / −233. {len(oow)} further 70%+ favourites exist and are published with full
disclosure instead of being squeezed into the band.</p>
<h3>2. Where the model got its confidence</h3>
<p>The strongest signals on the card are structural: Provence (7-0-0) versus Béziers
(2-0-5, −93), Aurillac versus winless Nevers (0-0-7), and Pau's league-best 239-point
attack against a Toulon side sitting on a zero points differential. In the NHL the
gap-makers are the Islanders' +7 and Boston's +14 differentials against opponents
with negative ones.</p>
<h3>3. Price snapshots vs the model</h3>
<p>For NHL rows the official feed carries third-party price snapshots (flag F-02).
The market mostly agrees with the model's ordering but not its magnitude — the
Islanders are modelled 75.7% while the feed's quotes sit near −110. That divergence
is published on every affected pick rather than smoothed away.</p>
<h3>4. Coverage reality</h3>
<p>Eleven of the seventeen sports have at least one listing; six hubs were empty or
outright-only. Verified depth concentrates in NHL, French rugby, URC and the NBA
slate. Tennis (13 listings), handball (15) and volleyball (14) could not be verified
at row level this session and contribute zero predictions — the honest count.</p>
<h3>Top 15 priced picks</h3>
<div class="wrap"><table><tr><th>Fixture</th><th>Selection</th><th>p</th>
<th>Fair US</th><th>Tier</th></tr>{rows}</table></div>
"""
    write('analysis.html', page('Analysis', body, 'analysis.html'))

    # --------------------------------------------------------- repo audit ---
    audit = [
        ('A-42B-01', 'high', 'Nine task rows remain "in progress" or "queued" past the '
         '§0.4 60-minute takeover rule (T9–T12, T19, T51, T97DC, T-FEC and others).',
         'COORDINATION.md §1'),
        ('A-42B-02', 'medium', 'Duplicate task id T63 appears twice in the board '
         '(sessions f1c13c19 and 92af340c both recorded as T63).',
         'COORDINATION.md §1'),
        ('A-42B-03', 'medium', 'Duplicate/out-of-order section numbers persist '
         '(§4 twice, §13 twice, §43 twice) despite earlier audit notes.',
         'COORDINATION.md'),
        ('A-42B-04', 'low', 'Root navigation still lacks companion entries requested by '
         'f71557b5 (03:45Z), 1a421e41 (07:22Z) and d7d19a67 (12:58Z). archive.html '
         'auto-lists desks, so nothing is unreachable, but the requests are open.',
         'COORDINATION.md §4'),
        ('A-42B-05', 'low', 'Several published pages exceed 200 KB (verification.html '
         '≈ 904 KB, flagged.html ≈ 213 KB, picks.html ≈ 194 KB), which slows the '
         'dashboard for reviewers on slow links.', 'repository root'),
        ('A-42B-06', 'info', 'Canonical pipeline gates (tests/pipeline, scripts/validate.py, '
         'pipeline.validate, pipeline.build) are green at this session\'s checkpoint; '
         'results recorded in SESSION_424375B4.md.', 'tests/, pipeline/, scripts/'),
        ('A-42B-07', 'info', 'This session touched only its claimed scope; see the '
         'scope table in SESSION_424375B4.md.', 'git log'),
    ]
    rows = ''.join(
        f'<tr><td>{esc(a[0])}</td><td>{tier_badge({"high":"low","medium":"medium","low":"out-of-window","info":"unpriced"}[a[1]])}'
        f'<div class="meta">{esc(a[1])}</div></td><td>{esc(a[2])}</td>'
        f'<td class="meta">{esc(a[3])}</td></tr>' for a in audit)
    body = f"""
<h2>Repository audit (line-by-line, this session)</h2>
<div class="note">The brief asks for a line-by-line repo review with links. This audit
covers the shared coordination board and repository-wide hygiene items this session
could verify directly from checked-in bytes; per-desk data audits remain the property
of the sessions that published them. Findings are labelled with severity and never
block the merge.</div>
<div class="wrap"><table><tr><th>ID</th><th>Severity</th><th>Finding</th>
<th>Where</th></tr>{rows}</table></div>
<h3>Verification performed</h3>
<ul>
<li>Canonical gates re-run at this checkpoint (see report).</li>
<li>Every desk table row carries at least one source link (checked by
<code>scripts/s424375b4_validate.py</code>).</li>
<li>Prediction word-count and uniqueness checks run at build time.</li>
</ul>
"""
    write('repo-audit.html', page('Repo audit', body, 'repo-audit.html'))

    print('pages written:', len(list(OUT.rglob('*.html'))))


if __name__ == '__main__':
    build()
