#!/usr/bin/env python3
"""Session 9dc28d1e — validator gate for the desk, its data and its published pages.

Checks, in order:
  1. desk.json counts agree with the content they describe
  2. every market's probabilities sum to one and every fair price is exactly 1/p
  3. tier labels obey the published rule, including the 70% / -250 conjunction
  4. every prediction is >=30 words, unique, names its selection and cites a High-priced row
  5. every fixture and every market carries an official https source
  6. inherited listings carry no prices
  7. every local link in every published page resolves, and pages contain no render artefacts
  8. all 17 in-scope category pages exist and the excluded categories appear nowhere as priced rows
"""

import html
import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DESK = ROOT / 'data' / '9dc28d1e' / 'desk.json'
SITE = ROOT / '9dc28d1e'
OFFICIAL_HOSTS = {
    'api-web.nhle.com', 'api.nhle.com', 'statsapi.mlb.com', 'api-live.euroleague.net',
    'www.euroleaguebasketball.net', 'www.nhl.com', 'www.mlb.com', 'www.nba.com',
    'www.atptour.com', 'www.wtatennis.com', 'www.wst.tv', 'www.pdc.tv', 'www.icc-cricket.com',
    'www.afl.com.au', 'www.intrl.sport', 'top14.lnr.fr', 'munster.gaa.ie', 'www.plusliga.pl',
    'ehfcl.eurohandball.com', 'www.formula1.com', 'www.pgatour.com', 'www.gbgb.org.uk',
    'lolesports.com', 'www.olbg.com', 'github.com', 'buffedlizard55-lab.github.io',
}
EXCLUDED = {'soccer', 'football', 'american-football', 'boxing', 'ufc', 'mma',
            'hurling', 'horse-racing', 'cycling', 'specials'}

errors = []
warnings = []


def check(cond, msg):
    if not cond:
        errors.append(msg)


def main():
    desk = json.loads(DESK.read_text())
    priced = desk['priced']
    inherited = desk['inherited']
    preds = desk['predictions']
    counts = desk['counts']

    # 1 counts
    outcomes = [o for row in priced for mk in row['markets'] for o in mk['outcomes']]
    check(counts['priced_matches'] == len(priced), 'priced_matches count mismatch')
    check(counts['markets'] == sum(len(r['markets']) for r in priced), 'market count mismatch')
    check(counts['outcomes'] == len(outcomes), 'outcome count mismatch')
    check(counts['fixtures_total'] == len(priced) + len(inherited), 'fixture total mismatch')
    check(counts['predictions'] == len(preds), 'prediction count mismatch')
    check(counts['findings'] == len(desk['findings']), 'finding count mismatch')
    for t in ('high', 'medium', 'low', 'outside_window'):
        check(counts[t] == sum(1 for o in outcomes if o['tier'] == t), f'{t} count mismatch')

    # 2 arithmetic
    for row in priced:
        for mk in row['markets']:
            total = sum(o['probability'] for o in mk['outcomes'])
            check(abs(total - 1) < 1e-5, f"{mk['id']} probabilities sum to {total}")
            for o in mk['outcomes']:
                p = o['probability']
                check(abs(o['fair_decimal'] * p - 1) < 2e-3, f"{mk['id']} fair decimal != 1/p")
                am = -100 * p / (1 - p) if p >= 0.5 else 100 * (1 - p) / p
                shown = float(o['american_display'].replace('+', ''))
                check(abs(shown - am) < 1.01, f"{mk['id']} american display off by more than 1")
                check(0 < p < 1, f"{mk['id']} probability outside (0,1)")

    # 3 tiers
    pred_keys = {(p['fixture_id'], p['selection']) for p in preds}
    for row in priced:
        for mk in row['markets']:
            for o in mk['outcomes']:
                p = o['probability']
                am = -100 * p / (1 - p) if p >= 0.5 else 100 * (1 - p) / p
                band = -250 <= am <= 10000
                if o['tier'] == 'high':
                    check(p > 0.70, f"{mk['id']} High at p={p}")
                    check(band, f"{mk['id']} High outside price window at {am:.1f}")
                    check((row['fixture_id'], o['selection']) in pred_keys,
                          f"{mk['id']} High without a prediction")
                elif o['tier'] == 'outside_window':
                    check(p > 0.70 and not band, f"{mk['id']} outside_window label inconsistent")
                elif o['tier'] == 'medium' and p > 0.70:
                    check(band, f"{mk['id']} capped Medium but price outside window")
                    check(bool(o.get('tier_reason')), f"{mk['id']} capped Medium without a reason")
                elif o['tier'] == 'medium':
                    check(0.60 <= p <= 0.70, f"{mk['id']} Medium at p={p}")
                elif o['tier'] == 'low':
                    check(p < 0.60, f"{mk['id']} Low at p={p}")

    # 4 predictions
    texts = [p['text'] for p in preds]
    for p in preds:
        words = len(p['text'].split())
        check(words >= 30, f"{p['fixture_id']} prediction only {words} words")
        check(p['selection'].lower() in p['text'].lower() or
              p['selection'].split()[0].lower() in p['text'].lower(),
              f"{p['fixture_id']} prediction does not name the selection")
        row = next((r for r in priced if r['fixture_id'] == p['fixture_id']), None)
        check(row is not None, f"{p['fixture_id']} prediction references unknown fixture")
        if row:
            match = [o for mk in row['markets'] for o in mk['outcomes'] if o['selection'] == p['selection']]
            check(len(match) == 1, f"{p['fixture_id']} selection not uniquely priced")
            if match:
                check(match[0]['tier'] == 'high', f"{p['fixture_id']} prediction row is not High")
        check(bool(p['source_ids']), f"{p['fixture_id']} prediction has no source")
        for sent in re.split(r'(?<=[.!?])\s+', p['text']):
            check(len(sent.split()) >= 3, f"{p['fixture_id']} degenerate sentence")
    grams = Counter()
    for t in texts:
        w = re.findall(r"[a-z']+", t.lower())
        for g in (' '.join(w[i:i + 6]) for i in range(len(w) - 5)):
            grams[g] += 1
    shared = [g for g, c in grams.items() if c > 1]
    check(not shared, f'predictions share 6-grams: {shared[:3]}')
    check(len({p['text'] for p in preds}) == len(preds), 'duplicate prediction text')

    # 5 sources
    for row in priced:
        check(bool(row['source_ids']), f"{row['fixture_id']} has no source id")
    for mk in (mk for row in priced for mk in row['markets']):
        check(bool(mk['sources']), f"{mk['id']} has no source")
    for s in desk['sources']:
        host = urlparse(s['url']).hostname
        check(host in OFFICIAL_HOSTS, f"source {s['id']} host {host} not on the official allow-list")
        check(s['url'].startswith('https://'), f"source {s['id']} is not https")
        check(bool(s.get('observed_utc')), f"source {s['id']} has no observation time")

    # 6 inherited
    for i in inherited:
        check(i['priced'] is False, f"inherited {i['id']} marked priced")
        check('probability' not in i, f"inherited {i['id']} carries a probability")
        check(bool(i['source_ids']), f"inherited {i['id']} has no source")
        check(not any(i['priced'] for i in inherited), 'inherited row priced')

    # sport scope
    sports = {r['sport'] for r in priced} | {i['sport'] for i in inherited}
    check(not (sports & EXCLUDED), f'excluded sport present: {sports & EXCLUDED}')

    # 7 pages
    pages = sorted(SITE.rglob('*.html'))
    check(len(pages) >= 25, f'only {len(pages)} pages rendered')
    for page in pages:
        text = page.read_text()
        check('%%' not in text, f'{page.name} contains a render artefact')
        check('localhost' not in text and '127.0.0.1' not in text, f'{page.name} references localhost')
        check('<nav>' in text, f'{page.name} has no navigation')
        for href in re.findall(r'href="([^"]+)"', text):
            if href.startswith(('http://', 'https://', '#', 'mailto:')):
                continue
            target = (page.parent / href.split('#')[0]).resolve()
            check(target.exists(), f'{page.relative_to(ROOT)} broken local link {href}')
        for src in re.findall(r'src="([^"]+)"', text):
            if src.startswith(('http://', 'https://', 'data:')):
                continue
            check((page.parent / src).exists(), f'{page.name} broken asset {src}')

    # 8 coverage
    for slug in desk['scope']['in_scope_sports']:
        check((SITE / 'sports' / f"{slug['slug']}.html").exists(),
              f"missing category page {slug['slug']}")
    check(len(desk['scope']['excluded_sports']) == 8, 'excluded scope list changed')
    for ex in desk['scope']['excluded_sports']:
        check(ex['name'].lower() not in {s.lower() for s in sports},
              f"excluded sport {ex['name']} appears in the fixture set")

    print(f"9DC28D1E VALIDATION {'FAILED' if errors else 'PASSED'}: "
          f"priced={len(priced)} outcomes={len(outcomes)} high={counts['high']} "
          f"predictions={len(preds)} pages={len(pages)} errors={len(errors)} warnings={len(warnings)}")
    for w in warnings:
        print(' warn:', w)
    for e in errors:
        print(' -', e)
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
