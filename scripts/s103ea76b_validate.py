"""Release gate for the 26 October 2026 fifteen-sport desk (session 103ea76b).

This mirrors pipeline.validate.validate_desk on arithmetic, provenance, prose and
links, and adds the two rules this desk needs:

* a fixture may leave ``start_utc`` blank, but only when it says so in
  ``start_time_status`` and the gap is named on the Flagged for Review page;
* a priced fixture needs both clubs' published records, not a league-wide table.

Run: python scripts/s103ea76b_validate.py [--site 103ea76b]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipeline.config import PUBLISHERS  # noqa: E402
from pipeline.desk import BAND_HIGH, BAND_LOW, HIGH_MIN, PICK_MIN, SPORT_INDEX, american_from_prob  # noqa: E402

OFFICIAL_HOSTS = set(PUBLISHERS) | {'www.nhl.com', 'www.mlb.com', 'nhl.com', 'mlb.com'}
DISCOVERY_HOSTS = {'www.olbg.com', 'olbg.com'}
BANNED = ('model', 'models', 'verified', 'verification', 'algorithm', 'machine learning',
          'ai-driven', 'backtested')
COUNT_KEYS = {'sports_requested', 'sports_with_fixtures', 'fixtures', 'priced_fixtures',
              'unpriced_fixtures', 'markets', 'outcomes', 'withheld_markets', 'picks', 'high',
              'medium', 'predictions', 'sources', 'flags'}


class HTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.body = {}
        self.h1 = 0
        self.title = ''
        self.ids = []
        self.links = []
        self.rows = []
        self._in_title = False
        self._tbody = 0
        self._row = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'body':
            self.body = a
        elif tag == 'h1':
            self.h1 += 1
        elif tag == 'title':
            self._in_title = True
        elif tag == 'tbody':
            self._tbody += 1
        elif tag == 'tr' and self._tbody:
            self._row = []
        if 'id' in a:
            self.ids.append(a['id'])
        if tag == 'a' and a.get('href') is not None:
            self.links.append(a['href'])
            if self._row is not None:
                self._row.append(a['href'])
        elif tag in ('link', 'script', 'img'):
            target = a.get('href') or a.get('src')
            if target:
                self.links.append(target)

    def handle_endtag(self, tag):
        if tag == 'title':
            self._in_title = False
        elif tag == 'tr' and self._row is not None:
            self.rows.append(self._row)
            self._row = None
        elif tag == 'tbody' and self._tbody:
            self._tbody -= 1

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def words(text):
    return [w for w in re.split(r'\s+', (text or '').strip()) if re.search(r'[A-Za-z0-9]', w)]


def grams(tokens, n=6):
    return {' '.join(tokens[i:i + n]).lower() for i in range(len(tokens) - n + 1)}


def host(url):
    return (urlsplit(url).hostname or '').lower()


def validate(site, directory):
    site = Path(site).resolve()
    directory = Path(directory).resolve()
    errors = []
    warns = []

    def check(test, message):
        if not test:
            errors.append(message)

    manifest_path = directory / 'manifest.json'
    desk_path = directory / 'desk.json'
    if not manifest_path.is_file():
        return [f'{manifest_path}: missing'], warns
    if not desk_path.is_file():
        return [f'{desk_path}: missing'], warns
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    desk = json.loads(desk_path.read_text(encoding='utf-8'))

    # --- sources ---------------------------------------------------------
    sources = {s['id']: s for s in desk['sources']}
    check(len(sources) == len(desk['sources']), 'duplicate source id')
    for sid, s in sources.items():
        check(s['url'].startswith('https://'), f'{sid}: source is not https')
        if s['role'] == 'official':
            check(host(s['url']) in OFFICIAL_HOSTS, f'{sid}: official host not allowlisted ({host(s["url"])})')
        else:
            check(host(s['url']) in DISCOVERY_HOSTS, f'{sid}: discovery host not allowlisted')
        check(bool(s.get('observed_at')), f'{sid}: no read timestamp')
        check(bool(s.get('supports')), f'{sid}: no stated use')

    # --- fixtures --------------------------------------------------------
    ids = [f['id'] for f in desk['fixtures']]
    check(len(ids) == len(set(ids)), 'duplicate fixture id')
    for f in desk['fixtures']:
        check(bool(f.get('sources')), f'{f["id"]}: no source')
        for sid in f['sources']:
            check(sid in sources, f'{f["id"]}: unknown source {sid}')
        if f.get('start_utc'):
            check(re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', f['start_utc']),
                  f'{f["id"]}: start time not in ISO UTC form')
            check('published by the official feed' in f.get('start_time_status', ''),
                  f'{f["id"]}: start time present but status not stated')
        else:
            check('not published' in f.get('start_time_status', ''),
                  f'{f["id"]}: blank start time without a status line')
            check(bool(f.get('start_time_note')), f'{f["id"]}: blank start time without an explanation')
        if f['priced']:
            for side in ('home_stats', 'away_stats'):
                check(bool(f.get(side)), f'{f["id"]}: priced without the {side.replace("_stats", "")} record')
            for market in f['markets']:
                out = market['outcomes']
                check(len(out) == 2, f'{f["id"]}/{market["key"]}: not a two-way book')
                check(abs(sum(o['p'] for o in out) - 1) < 1e-9,
                      f'{f["id"]}/{market["key"]}: probabilities do not sum to one')
                for o in out:
                    check(0 < o['p'] < 1, f'{f["id"]}: invalid probability')
                    check(abs(o['fair_decimal'] * o['p'] - 1) < 5e-4,
                          f'{f["id"]}: fair decimal is not the reciprocal')
                    check(o['american'] == american_from_prob(o['p']), f'{f["id"]}: American price mismatch')
                    check(o['in_band'] == (BAND_LOW <= o['american'] <= BAND_HIGH),
                          f'{f["id"]}: band flag does not follow the price')
        else:
            check(bool(f.get('unpriced_reason')), f'{f["id"]}: unpriced without a reason')
            check(not f['markets'], f'{f["id"]}: unpriced but carries markets')
        check(bool(f.get('withheld')), f'{f["id"]}: no withheld-market note')
        if not f['pick']:
            check(bool(f.get('no_pick_reason')), f'{f["id"]}: no pick and no reason')

    # --- picks and prose -------------------------------------------------
    picks = [f for f in desk['fixtures'] if f['pick']]
    for f in picks:
        p = f['pick']
        check(f['priced'], f'{f["id"]}: pick on an unpriced fixture')
        check(p['probability'] >= PICK_MIN, f'{f["id"]}: pick below the 55% floor')
        check(BAND_LOW <= p['american'] <= BAND_HIGH, f'{f["id"]}: pick outside the band')
        check(p['confidence'] == ('high' if p['probability'] >= HIGH_MIN else 'medium'),
              f'{f["id"]}: confidence tier does not follow the threshold')
        check(p.get('selection') and p.get('market_label'), f'{f["id"]}: pick without a labelled selection')
        text = (p.get('prediction') or '').strip()
        check(text, f'{f["id"]}: pick has no written prediction')
        if text:
            check(len(words(text)) >= 30, f'{f["id"]}: prediction shorter than 30 words')
            low = text.lower()
            for banned in BANNED:
                check(banned not in low, f'{f["id"]}: prediction contains "{banned}"')
            check(p['selection'].lower() in low or p['selection'].split(' -')[0].lower() in low,
                  f'{f["id"]}: prediction does not name the selection')
            check('  ' not in text, f'{f["id"]}: double space in prose')
        check(bool(p.get('gaps')), f'{f["id"]}: pick does not state what is missing')
    seen = {}
    for f in picks:
        for g in grams(words(f['pick'].get('prediction'))):
            seen.setdefault(g, set()).add(f['id'])
    repeated = sorted(k for k, v in seen.items() if len(v) > 1)
    check(not repeated, 'predictions share six-word phrases: ' + '; '.join(repeated[:3]))

    # --- counts ----------------------------------------------------------
    counts = {
        'sports_requested': len(SPORT_INDEX),
        'sports_with_fixtures': len({f['sport'] for f in desk['fixtures']}),
        'fixtures': len(desk['fixtures']),
        'priced_fixtures': sum(1 for f in desk['fixtures'] if f['priced']),
        'unpriced_fixtures': sum(1 for f in desk['fixtures'] if not f['priced']),
        'markets': sum(len(f['markets']) for f in desk['fixtures']),
        'outcomes': sum(len(m['outcomes']) for f in desk['fixtures'] for m in f['markets']),
        'withheld_markets': sum(len(f.get('withheld', [])) for f in desk['fixtures']),
        'picks': len(picks),
        'high': sum(1 for f in picks if f['pick']['confidence'] == 'high'),
        'medium': sum(1 for f in picks if f['pick']['confidence'] == 'medium'),
        'predictions': len(picks),
        'sources': len(sources),
        'flags': len(desk['flags']),
    }
    check(set(desk['counts']) == COUNT_KEYS, 'desk counts carry keys outside the canonical set: '
          + ', '.join(sorted(set(desk['counts']) ^ COUNT_KEYS)))
    check(desk['counts'] == counts, 'desk counts do not reconcile with the rows')
    check(manifest['counts'] == counts, 'manifest counts do not reconcile with the rows')

    # --- sport coverage --------------------------------------------------
    wanted = [s['slug'] for s in SPORT_INDEX.values()]
    check(set(desk['sport_order']) == set(wanted),
          'sport list is not exactly the fifteen requested sports')
    check(len(desk['sport_order']) == 15, 'sport list is not fifteen entries long')
    check([s['code'] for s in desk['sports']] == desk['sport_order'], 'sport metadata order mismatch')
    for s in desk['sports']:
        check(s['olbg_url'].startswith('https://www.olbg.com/betting-tips/'), f'{s["code"]}: bad OLBG hub')
        check(host(s['official_hub']) in OFFICIAL_HOSTS, f'{s["code"]}: official hub not allowlisted')
    check({x['sport'] for x in desk['listings_only']} == set(wanted),
          'listing-only inventory does not cover the fifteen sports')

    # --- flags and audit -------------------------------------------------
    for x in desk['flags']:
        check(bool(x.get('source_ids')), f'{x["id"]}: flag without a page')
        for sid in x['source_ids']:
            check(sid in sources, f'{x["id"]}: unknown source {sid}')
        check(bool(x.get('recheck')), f'{x["id"]}: flag without a closing step')
    for x in desk['audit']:
        target = ROOT / x['review'].split('#')[0]
        check(target.is_file(), f'{x["id"]}: audit target {x["review"]} does not exist')
        check(bool(x.get('evidence')), f'{x["id"]}: audit finding without evidence')

    # --- pages -----------------------------------------------------------
    cache = {}

    def parsed(path):
        if path not in cache:
            p = HTML()
            p.feed(path.read_text(encoding='utf-8'))
            cache[path] = p
        return cache[path]

    check('index.html' in manifest['pages'], 'manifest does not list the landing page')
    for rel in manifest['pages']:
        path = site / rel
        if not path.is_file():
            errors.append(f'{rel}: missing page')
            continue
        p = parsed(path)
        check(p.body.get('data-snapshot') == manifest['generated_at'],
              f'{rel}: snapshot marker missing or mismatched')
        check(p.h1 == 1, f'{rel}: page must have exactly one h1')
        check(bool(p.title), f'{rel}: page has no title')
        check(len(p.ids) == len(set(p.ids)), f'{rel}: duplicate HTML ids')
        project_only = rel == 'sources.html'
        for index, links in enumerate(p.rows, 1):
            ok = any(host(u) in OFFICIAL_HOSTS or (project_only and host(u) in DISCOVERY_HOSTS)
                     for u in links if u.startswith('https://'))
            if not ok:
                errors.append(f'{rel}: table row {index} has no official source link')
        for href in p.links:
            parts = urlsplit(href)
            if parts.scheme or parts.netloc:
                if parts.scheme in ('javascript', 'data') or (parts.scheme == 'http'):
                    errors.append(f'{rel}: unsafe link {href}')
                continue
            target = (path.parent / unquote(parts.path)).resolve() if parts.path else path
            try:
                target.relative_to(site)
            except ValueError:
                errors.append(f'{rel}: link escapes the site: {href}')
                continue
            if target.is_dir():
                target = target / 'index.html'
            if not target.is_file():
                errors.append(f'{rel}: broken link {href}')
                continue
            if parts.fragment and target.suffix == '.html':
                if unquote(parts.fragment) not in parsed(target).ids:
                    errors.append(f'{rel}: missing fragment {href}')
    published = {p.name for p in site.glob('*.html')}
    check(not (published - set(manifest['pages'])),
          'unregistered root HTML: ' + ', '.join(sorted(published - set(manifest['pages']))))
    missing = set(manifest['pages']) - {p.relative_to(site).as_posix() for p in site.rglob('*.html')}
    check(not missing, 'manifest lists pages that do not exist: ' + ', '.join(sorted(missing)))
    return errors, warns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--site', type=Path, default=ROOT / '103ea76b')
    ap.add_argument('--data', type=Path, default=None)
    args = ap.parse_args()
    data = args.data or args.site / 'data' / 'desk'
    errors, warns = validate(args.site, data)
    for w in warns:
        print('WARN:', w)
    for e in errors:
        print('ERROR:', e)
    print(f'103ea76b gate: {len(errors)} errors, {len(warns)} warnings across '
          f'{len(json.loads((Path(data) / "manifest.json").read_text())["pages"])} pages.')
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
