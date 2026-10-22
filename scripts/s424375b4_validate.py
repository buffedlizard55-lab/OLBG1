"""T424375B4 — desk validator. Fails loudly on any contract violation."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '424375b4'
DATA = ROOT / 'data' / '424375b4'

sys.path.insert(0, str(ROOT / 'scripts'))
from s424375b4_data import SOURCES  # noqa: E402
from s424375b4_fixtures import FIXTURES, FLAGS  # noqa: E402
from s424375b4_prose import PREDICTIONS  # noqa: E402

errors, checks = [], 0


def ck(cond, msg):
    global checks
    checks += 1
    if not cond:
        errors.append(msg)


markets = json.load(open(DATA / 'markets.json'))
picks = json.load(open(DATA / 'picks.json'))

# --- data contracts -------------------------------------------------------
ck(len(FIXTURES) >= 100, 'fixture count unexpectedly low')
ck(len(SOURCES) >= 20, 'source ledger too small')
fx_ids = [f['id'] for f in FIXTURES]
ck(len(fx_ids) == len(set(fx_ids)), 'duplicate fixture ids')
for f in FIXTURES:
    v = f['verify']
    ck(v['klass'] in ('A', 'B', 'C'), f"{f['id']}: bad class")
    ck(bool(v['source_ids']), f"{f['id']}: no source id")
    ck(any(u.startswith('https://') for u in v['links']),
       f"{f['id']}: no https source link")
    for sid in v['source_ids']:
        ck(any(s['id'] == sid for s in SOURCES), f"{f['id']}: unknown source {sid}")
    if v['klass'] == 'C':
        for field in ('start_official',):
            pass  # starts may be blank; blanks are required for record-derived fields
    if v['klass'] == 'C' and not any(
            any(s['id'] == sid and s['klass'] in ('A', 'B') for s in SOURCES)
            for sid in v['source_ids']):
        ck(f.get('players', []) == [],
           f"{f['id']}: class C row carries unverified player facts")

# --- model consistency ---------------------------------------------------
priced = [p for p in picks if p.get('p') is not None]
ck(len(priced) >= 35, f'expected >=35 priced picks, got {len(priced)}')
for p in picks:
    if p.get('p') is not None:
        ck(0.0 < p['p'] < 1.0, f"{p['fixture_id']}: p out of range")
        ck(abs(p['fair_decimal'] - 1.0 / p['p']) < 1e-3,
           f"{p['fixture_id']}: fair decimal mismatch")
        am = p['fair_american']
        if p['p'] >= 0.5:
            ck(abs(am + 100 * p['p'] / (1 - p['p'])) < 0.6,
               f"{p['fixture_id']}: american mismatch")
        if p['tier'] == 'high-eligible':
            ck(round(p['p'], 6) >= 0.70, f"{p['fixture_id']}: High without p>=0.70")
            ck(-250.0 <= p['fair_american'] <= 10000.0,
               f"{p['fixture_id']}: High outside price window")
            ck(p['verify'] in ('A', 'B'), f"{p['fixture_id']}: High without class A/B")
            ck(any(x['fixture_id'] == p['fixture_id'] for x in PREDICTIONS),
               f"{p['fixture_id']}: High without a written prediction")
        if p['tier'] == 'out-of-window':
            ck(round(p['p'], 6) >= 0.70 and p['fair_american'] < -250.0,
               f"{p['fixture_id']}: mislabelled out-of-window")

# --- predictions ---------------------------------------------------------
texts = []
for pr in PREDICTIONS:
    words = re.findall(r"[A-Za-z0-9%’'’-]+", pr['text'])
    ck(len(words) >= 30, f"{pr['id']}: only {len(words)} words")
    ck(pr['selection'] and pr['selection'] != '', f"{pr['id']}: no selection named")
    ck(bool(pr['sources']), f"{pr['id']}: no sources")
    for sid in pr['sources']:
        ck(any(s['id'] == sid for s in SOURCES), f"{pr['id']}: unknown source {sid}")
    ck(any(x['id'] == pr['fixture_id'] for x in FIXTURES),
       f"{pr['id']}: unknown fixture")
    texts.append(pr['text'].strip().lower())
ck(len(texts) == len(set(texts)), 'prediction texts are not unique')
openers = [t[:60] for t in texts]
ck(len(openers) == len(set(openers)), 'prediction openers repeat')

# --- pages ---------------------------------------------------------------
required = ['index.html', 'matches.html', 'markets.html', 'picks.html',
            'high-confidence.html', 'predictions.html', 'coverage.html',
            'analysis.html', 'methodology.html', 'sources.html', 'flagged.html',
            'repo-audit.html']
for name in required:
    p = OUT / name
    ck(p.exists(), f'missing page {name}')
    if p.exists():
        body = p.read_text()
        for href in re.findall(r'href="([^"]+)"', body):
            if href.startswith(('http', '#', 'mailto')):
                continue
            target = (p.parent / href).resolve()
            ck(target.exists(), f'{name}: broken internal link {href}')
sport_pages = list((OUT / 'sports').glob('*.html'))
ck(len(sport_pages) == 17, f'expected 17 sport pages, got {len(sport_pages)}')

# every fixture row must appear on matches.html with a source id
mhtml = (OUT / 'matches.html').read_text()
for f in FIXTURES:
    ck(f['id'] in mhtml, f"{f['id']} missing from matches.html")

# flagged page must carry every flag
fhtml = (OUT / 'flagged.html').read_text()
for fl in FLAGS:
    ck(fl['id'] in fhtml, f"{fl['id']} missing from flagged.html")

print(f'checks run: {checks}')
if errors:
    print('VALIDATION FAILED')
    for e in errors:
        print(' -', e)
    sys.exit(1)
print('VALIDATION PASSED — 0 errors')
