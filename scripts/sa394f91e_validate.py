"""Gate for the 25 October 2026 desk. Exits non-zero on any failure."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

import sa394f91e_content as C  # noqa: E402
import sa394f91e_data as E     # noqa: E402
import sa394f91e_model as M    # noqa: E402

SITE = ROOT / 'a394f91e'
OFFICIAL_HOSTS = {'www.nhl.com', 'api-web.nhle.com', 'statsapi.mlb.com', 'www.nba.com',
                  'www.mlb.com', 'www.formula1.com', 'www.pdc.tv', 'www.premrugby.com',
                  'www.icc-cricket.com', 'www.wst.tv', 'www.gaa.ie', 'www.gbgb.org.uk',
                  'www.atptour.com', 'www.cev.eu', 'www.eurohandball.com', 'www.nrl.com',
                  'www.pgatour.com'}
errors, checks = [], 0


def ck(cond, msg):
    global checks
    checks += 1
    if not cond:
        errors.append(msg)


def pages():
    return sorted(SITE.rglob('*.html'))


def read(p):
    return p.read_text(encoding='utf-8')


def main():
    ck((ROOT / 'data' / 'a394f91e' / 'desk.json').exists(), 'desk.json missing')
    desk = json.loads((ROOT / 'data' / 'a394f91e' / 'desk.json').read_text())

    # --- every page ------------------------------------------------------
    ck(len(pages()) == 25, f'expected 25 pages, found {len(pages())}')
    for p in pages():
        t = read(p)
        rel = p.relative_to(SITE)
        ck(t.count('<h1') == 1, f'{rel}: h1 count is {t.count("<h1")}')
        ck('styles.css' in t, f'{rel}: no stylesheet link')
        for bad in (r'\bTODO\b', r'\bFIXME\b', r'\blorem\b', r'\bPLACEHOLDER\b',
                    r'\{unfilled\}', r'>None<', r'\bnan\b', r'\bNaN\b', r'\bundefined\b'):
            ck(not re.search(bad, t), f'{rel}: placeholder token {bad!r}')
        for h in re.findall(r'href="(?!#|https?:|mailto)([^"]+)"', t):
            target = (p.parent / h.split('#')[0]).resolve()
            ck(target.exists(), f'{rel}: broken local link {h}')

    # --- provenance: every fixture row carries an official link ----------
    official_urls = {s['url'] for s in E.SOURCES if s['role'] in ('official', 'official_attempt')}
    o_hosts = {u.split('/')[2] for u in official_urls}
    for name in ('matches.html', 'picks.html', 'index.html'):
        t = read(SITE / name)
        ck('olbg.com/betting-tips' not in t,
           f'{name}: OLBG link rendered on a provenance page')

    for f in C.NHL + C.NBA + C.MLB:
        host = f['source_url'].split('/')[2]
        ck(host in OFFICIAL_HOSTS, f'{f["key"]}: source host {host} is not an official publisher')

    # --- the band and the grade rule -------------------------------------
    for p in desk['picks']:
        price = p['price']
        ck(M.BAND_LOW <= price <= M.BAND_HIGH,
           f'{p["fixture"]}: price {price} outside the -250..+10000 band')
        ck(M.grade(p['probability']) == p['grade'],
           f'{p["fixture"]}: grade {p["grade"]} does not follow the rule')
        ck(p['grade'] in ('High', 'Medium'), f'{p["fixture"]}: a pick was graded {p["grade"]}')
        ck(0.55 <= p['probability'] < 0.72, f'{p["fixture"]}: probability {p["probability"]} off-band')
    ck(len([p for p in desk['picks'] if p['grade'] == 'High']) == 2, 'expected 2 High picks')
    ck(len(desk['picks']) == len(C.PREDICTIONS), 'a graded pick has no written analysis')

    # --- prose ------------------------------------------------------------
    words = {}
    for key, text in C.PREDICTIONS.items():
        words[key] = text.split()
        ck(len(words[key]) >= 30, f'{key}: prediction is {len(words[key])} words')
        low = text.lower()
        for banned in ('model', 'verified', 'verify', 'hallucinat'):
            ck(banned not in low, f'{key}: internal vocabulary {banned!r} in the prediction')
        ck(len(set(w.lower() for w in words[key])) / len(words[key]) > 0.5,
           f'{key}: prediction repeats itself too heavily')

    def grams(ws, n=6):
        return {tuple(w.lower() for w in ws[i:i + n]) for i in range(len(ws) - n + 1)}

    keys = list(C.PREDICTIONS)
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            shared = grams(words[keys[i]]) & grams(words[keys[j]])
            ck(not shared, f'{keys[i]} and {keys[j]} share a six-word run: {list(shared)[:2]}')

    # --- discovery ledger is internally consistent ------------------------
    ck(len(E.DISCOVERY) == desk['discovery'].__len__(), 'discovery ledger count drifted')
    for d in E.DISCOVERY:
        ck(d[7].startswith('https://www.olbg.com/betting-tips/'), f'{d[1]}: discovery link not OLBG')
        ck(d[0] in E.SPORT_INDEX, f'{d[1]}: unknown sport slug {d[0]}')
    for d in E.OUTRIGHTS:
        ck(d[0] in E.SPORT_INDEX, f'{d[1]}: unknown sport slug {d[0]}')

    # --- sources ----------------------------------------------------------
    ids = [s['id'] for s in E.SOURCES]
    ck(len(ids) == len(set(ids)), 'duplicate source id')
    for s in E.SOURCES:
        ck(re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', s['read_at']),
           f'{s["id"]}: read_at is not an exact UTC timestamp')
        ck(s['url'].startswith('https://'), f'{s["id"]}: source is not https')

    # --- every published fixture names a source that exists ---------------
    for f in desk['fixtures']:
        ck(any(s['url'] == f['source_url'] for s in E.SOURCES),
           f'{f["key"]}: fixture source is not in the source list')

    # --- no claim of an injury or a player anywhere ----------------------
    prose = read(SITE / 'predictions.html').lower()
    for bad in ('doubtful', 'ruled out', 'injury report', 'hamstring', 'concussion',
                'returns from injury', 'fitness test'):
        ck(bad not in prose, f'predictions.html: unverified availability language {bad!r}')

    # --- determinism ------------------------------------------------------
    before = {p: read(p) for p in pages()}
    import sa394f91e_build as B
    B.write()
    for p, t in before.items():
        ck(read(p) == t, f'{p.name}: rebuild is not byte-identical')

    print(f'checks: {checks}   errors: {len(errors)}')
    for e in errors:
        print('  FAIL', e)
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
