"""Quality gate for the 26 October 2026 desk (aa2881ac). Prints `errors: 0` on success.

The canonical pipeline.validate does not walk desk subfolders, so this script
checks every page and every pick of this desk itself.
"""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))

import saa2881ac_data as D  # noqa: E402
import saa2881ac_model as M  # noqa: E402

ROOT = D.ROOT
DESK = ROOT / 'aa2881ac'
DATA = ROOT / 'data' / 'aa2881ac' / 'desk.json'
PAGES = ['index.html', 'discovery.html', 'picks.html', 'predictions.html', 'matches.html', 'flagged.html',
         'sources.html', 'audit.html', 'methodology.html', 'sports.html'] + \
        [f'sports/{s}.html' for s in D.SPORT_INDEX]
OFFICIAL_HOSTS = {
    'api-web.nhle.com', 'www.nhl.com', 'statsapi.mlb.com', 'www.mlb.com', 'www.atptour.com',
    'ehfcl.eurohandball.com', 'www.legavolleyfemminile.it', 'www.formula1.com', 'www.icc-cricket.com',
    'www.penny-del.org', 'www.nba.com', 'www.pgatour.com', 'www.tauronliga.pl', 'www.gaa.ie',
    'www.gbgb.org.uk', 'www.wst.tv', 'www.pdc.tv', 'www.sixnationsrugby.com', 'www.nrl.com'}
OLBG_HOSTS = {'www.olbg.com'}
GITHUB_HOSTS = {'github.com'}
NO_OLBG_PAGES = {'index.html', 'picks.html', 'matches.html', 'predictions.html'}
BANNED = re.compile(r'\b(model|models|verified|verification|verify|algorithm|machine learning|ai-driven|'
                    r'backtested|guaranteed? win|lock)\b', re.I)
PLACEHOLDER = re.compile(r'\{[a-z_]+\}|TODO|TBD|lorem', re.I)
INJURY_WORDS = re.compile(r'\b(injur\w*|ruled out|sidelined|doubtful|questionable)\b', re.I)


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.h1 = 0
        self.title = ''
        self._in_title = False
        self.css = False
        self.ids, self.links, self.rows = [], [], []
        self._row = None
        self._in_tbody = False

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if 'id' in d:
            self.ids.append(d['id'])
        if tag == 'h1':
            self.h1 += 1
        if tag == 'title':
            self._in_title = True
        if tag == 'link' and d.get('rel') == 'stylesheet' and d.get('href', '').endswith('styles.css'):
            self.css = True
        if tag == 'tbody':
            self._in_tbody = True
        if tag == 'tr' and self._in_tbody:
            self._row = []
        if tag == 'a' and d.get('href'):
            self.links.append(d['href'])
            if self._row is not None:
                self._row.append(d['href'])

    def handle_endtag(self, tag):
        if tag == 'title':
            self._in_title = False
        if tag == 'tbody':
            self._in_tbody = False
        if tag == 'tr' and self._row is not None:
            self.rows.append(self._row)
            self._row = None

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def host(url):
    return urlsplit(url).netloc.lower()


def validate():
    errors = []

    def check(ok, msg):
        if not ok:
            errors.append(msg)

    parsed = {}
    for rel in PAGES:
        path = DESK / rel
        if not path.is_file():
            errors.append(f'{rel}: missing')
            continue
        text = path.read_text(encoding='utf-8')
        p = Page()
        p.feed(text)
        parsed[rel] = p
        check(p.h1 == 1, f'{rel}: expected one h1, found {p.h1}')
        check(p.css, f'{rel}: stylesheet link missing')
        check(bool(p.title.strip()), f'{rel}: empty title')
        check(len(p.ids) == len(set(p.ids)), f'{rel}: duplicate ids')
        check(not PLACEHOLDER.search(text), f'{rel}: placeholder text present')
        if rel in NO_OLBG_PAGES:
            check(not any(host(u) in OLBG_HOSTS for u in p.links), f'{rel}: OLBG link on a pick/match page')
        allowed = set(OFFICIAL_HOSTS)
        if rel in ('discovery.html', 'sources.html') or rel.startswith('sports/'):
            allowed |= OLBG_HOSTS
        if rel == 'audit.html':
            allowed = GITHUB_HOSTS
        if rel == 'sources.html' or rel == 'flagged.html':
            allowed |= OLBG_HOSTS
        for i, links in enumerate(p.rows, 1):
            check(any(u.startswith('https://') and host(u) in allowed for u in links),
                  f'{rel}: table row {i} has no source link from an allowed host')
    # internal links and fragments
    for rel, p in parsed.items():
        base = (DESK / rel).parent
        for href in p.links:
            parts = urlsplit(href)
            if parts.scheme or parts.netloc:
                check(parts.scheme == 'https', f'{rel}: non-https external link {href}')
                continue
            target = (base / unquote(parts.path)).resolve() if parts.path else (DESK / rel).resolve()
            try:
                trel = target.relative_to(DESK.resolve()).as_posix()
            except ValueError:
                errors.append(f'{rel}: link leaves the desk {href}')
                continue
            if not target.is_file():
                errors.append(f'{rel}: broken link {href}')
                continue
            if parts.fragment and trel in parsed:
                check(parts.fragment in parsed[trel].ids, f'{rel}: missing fragment {href}')

    # data checks
    desk = json.loads(DATA.read_text(encoding='utf-8'))
    picks, preds, fixtures = desk['picks'], desk['predictions'], desk['fixtures']
    fx = {f['key']: f for f in fixtures}
    for p in picks:
        g = M.grade(p['prob'])
        if p['capped']:
            check(p['grade'] == 'Low' and not fx[p['fixture']]['confirmed'], f'{p["id"]}: bad cap')
        else:
            check(g == p['grade'], f'{p["id"]}: grade {p["grade"]} does not match probability ({g})')
        check(M.in_band(p['price']), f'{p["id"]}: price {p["price"]} outside -250..+10000')
        check(abs(p['price'] - M.american(p['prob'])) <= 2, f'{p["id"]}: price does not match probability')
        check(host(p['source']) in OFFICIAL_HOSTS, f'{p["id"]}: pick source is not official')
        f = fx[p['fixture']]
        names = [o['name'] for m in f['priced']['markets'] for o in m['outcomes']]
        check(p['selection'] in names, f'{p["id"]}: selection not among originated outcomes')
    for slug in D.SPORT_INDEX:
        check(sum(p['sport'] == slug for p in picks) <= 10, f'{slug}: more than 10 picks')
        check(sum(p['sport'] == slug for p in preds) <= 5, f'{slug}: more than 5 predictions')
    texts = [p['text'] for p in preds]
    check(len(texts) == len(set(texts)), 'duplicate prediction text')
    starts = [' '.join(t.split()[:6]) for t in texts]
    check(len(starts) == len(set(starts)), 'two predictions open with the same six words')
    for p in preds:
        t = p['text']
        check(len(t.split()) >= 30, f'{p["pick"]}: prediction under 30 words')
        check(not BANNED.search(t), f'{p["pick"]}: banned word in prediction')
        check(not INJURY_WORDS.search(t), f'{p["pick"]}: injury claim in prediction')
        check(p['price_text'] in t, f'{p["pick"]}: prediction does not state its price')
        sel = p['selection'].split(' win')[0].split(' -')[0].split(' to win')[0]
        first = sel.split()[0] if not sel.startswith('A Mercedes') else 'Mercedes'
        check(first in t, f'{p["pick"]}: selection {sel!r} not obvious in the text')
    for f in fixtures:
        for s in f['sources']:
            check(host(s['url']) in OFFICIAL_HOSTS, f'{f["key"]}: fixture source host {host(s["url"])} not official')
        if not f.get('priced'):
            check(bool(f.get('unpriced')), f'{f["key"]}: unpriced fixture has no stated reason')
    for fl in desk['flags']:
        check(fl['url'].startswith('https://'), f'{fl["id"]}: flag without a source link')
    for r in desk['audit']:
        check(r['url'].startswith('https://github.com/buffedlizard55-lab/OLBG1/'), f'{r["id"]}: audit link')
    counts = desk['counts']
    check(counts['picks'] == len(picks) and counts['predictions'] == len(preds), 'counts do not reconcile')
    check(counts['high'] == sum(p['grade'] == 'High' for p in picks), 'High count does not reconcile')
    check(set(D.SPORT_INDEX) == {s for s in D.SPORT_INDEX if (DESK / 'sports' / f'{s}.html').is_file()},
          'a sport page is missing')
    return errors


if __name__ == '__main__':
    errs = validate()
    for x in errs:
        print('ERROR', x)
    print(f'errors: {len(errs)}')
    sys.exit(1 if errs else 0)
