"""Gates for the 733888f2 desk. Exit code 1 on any error."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

import s733888f2_data as D          # noqa: E402
import s733888f2_model as M         # noqa: E402
import s733888f2_build as B         # noqa: E402

OUT = ROOT / '733888f2'
BANNED = ('model', 'verified', 'verify', 'algorithm')
OFFICIAL_HOSTS = ('nhl.com', 'statsapi.mlb.com', 'mlb.com', 'quins.co.uk', 'premrugby.com',
                  'atptour.com', 'ecb.co.uk', 'pdc.tv', 'legavolley.it',
                  'trentinovolley.it')
EXPECTED = ['index.html', 'picks.html', 'predictions.html', 'matches.html', 'markets.html',
            'sports.html', 'flagged.html', 'sources.html', 'methodology.html',
            'repo-audit.html', 'reverse-engineering.html', 'archive.html']


def words(text):
    return re.findall(r"[A-Za-z0-9'’\-]+", text)


def grams(text, n=6):
    w = [x.lower() for x in words(text)]
    return {' '.join(w[i:i + n]) for i in range(max(0, len(w) - n + 1))}


def check_structure(errors):
    for name in EXPECTED:
        if not (OUT / name).is_file():
            errors.append(f'missing page {name}')
    for slug_, _, _, _ in D.SPORTS:
        if not (OUT / 'sports' / f'{slug_}.html').is_file():
            errors.append(f'missing sport page {slug_}')


def check_matches(errors):
    ids = [m['id'] for m in D.MATCHES]
    if len(ids) != len(set(ids)):
        errors.append('duplicate match id')
    for m in D.MATCHES:
        if not m['official'].startswith('https://'):
            errors.append(f'{m["id"]}: official link is not https')
        host = m['official'].split('/')[2]
        if not any(host == h or host.endswith('.' + h) for h in OFFICIAL_HOSTS):
            errors.append(f'{m["id"]}: {host} is not an allow-listed official publisher')
        if not m['facts']:
            errors.append(f'{m["id"]}: no facts')
        for side in ('home', 'away'):
            if side not in m['inputs']:
                errors.append(f'{m["id"]}: missing {side} input')
        if m['start'] < '2026-10-24T22:25:00Z':
            errors.append(f'{m["id"]}: start time is not in the future at capture')


def check_prices(errors):
    for m in D.MATCHES:
        card = M.price_match(m)
        if card is None:
            errors.append(f'{m["id"]}: not priceable')
            continue
        w = card['market_winner']
        total = w['home']['p'] + w['away']['p']
        if abs(total - 1.0) > 1e-9:
            errors.append(f'{m["id"]}: two-way book does not sum to 1 ({total})')
        p = card['pick']
        if p['selection'] not in (m['home'], m['away']):
            errors.append(f'{m["id"]}: pick is not one of the two participants')
        expected = M.tier(p['p'], p['american'])
        if p['tier'] != expected:
            errors.append(f'{m["id"]}: tier {p["tier"]} != {expected}')
        if p['tier'] == 'High' and not (p['p'] > 0.70 and M.in_band(p['american'])):
            errors.append(f'{m["id"]}: High pick fails the conjunction')
        if p['tier'] != 'High' and p['p'] > 0.70 and M.in_band(p['american']):
            errors.append(f'{m["id"]}: band-qualifying pick not labelled High')


def check_predictions(errors):
    seen = {}
    for m in D.MATCHES:
        text = B.PREDICTIONS.get(m['id'], '')
        if not text:
            errors.append(f'{m["id"]}: no written prediction')
            continue
        if len(words(text)) < 30:
            errors.append(f'{m["id"]}: prediction is {len(words(text))} words, under 30')
        low = text.lower()
        for bad in BANNED:
            if bad in low:
                errors.append(f'{m["id"]}: prediction contains internal vocabulary "{bad}"')
        pick = M.price_match(m)['pick']
        if pick['selection'].split()[0].lower() not in low:
            errors.append(f'{m["id"]}: prediction does not name the selection')
        g = grams(text)
        for other_id, other in seen.items():
            if g & other:
                errors.append(f'{m["id"]} shares a six-word run with {other_id}')
        seen[m['id']] = g
    for mid in B.PREDICTIONS:
        if mid not in {m['id'] for m in D.MATCHES}:
            errors.append(f'prediction for unknown match {mid}')


def check_unpriced(errors):
    for u in D.UNPRICED:
        if len(u['reason']) < 20:
            errors.append(f'{u["event"]}: reason too short')
        if not u['olbg'].startswith('https://'):
            errors.append(f'{u["event"]}: discovery link is not https')
        if u['sport'] not in D.SPORT_NAME:
            errors.append(f'{u["event"]}: unknown sport {u["sport"]}')


def check_pages(errors):
    for path in sorted(OUT.rglob('*.html')):
        text = path.read_text()
        if text.count('<h1') != 1:
            errors.append(f'{path.relative_to(OUT)}: {text.count("<h1")} h1 elements')
        rel = str(path.relative_to(OUT))
        must_cite = (rel in ('index.html', 'picks.html', 'predictions.html', 'matches.html',
                             'markets.html', 'sources.html', 'repo-audit.html',
                             'reverse-engineering.html', 'flagged.html')
                     or rel.startswith('sports/'))
        if must_cite and 'href="http' not in text:
            errors.append(f'{rel}: no external source links')
        for href in re.findall(r'href="([^"]+)"', text):
            if href.startswith(('http://', 'https://', '#', 'mailto:')):
                continue
            target = (path.parent / href.split('#')[0]).resolve()
            if not target.exists():
                errors.append(f'{path.relative_to(OUT)}: broken link {href}')


def check_coverage(errors):
    covered = {m['sport'] for m in D.MATCHES}
    for slug_, name, _, _ in D.SPORTS:
        if slug_ not in covered:
            if not [u for u in D.UNPRICED if u['sport'] == slug_]:
                # must at least be a documented empty hub
                flag_text = ' '.join(f[4] for f in B.FLAGS)
                if name.split()[0] not in flag_text:
                    errors.append(f'{name}: neither priced, listed nor flagged')


def run():
    errors = []
    check_structure(errors)
    check_matches(errors)
    check_prices(errors)
    check_predictions(errors)
    check_unpriced(errors)
    check_pages(errors)
    check_coverage(errors)
    return errors


if __name__ == '__main__':
    bad = run()
    for b in bad:
        print('ERROR', b)
    print(f'{len(bad)} error(s)')
    sys.exit(1 if bad else 0)
