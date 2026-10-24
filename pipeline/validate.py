"""Release gates: field provenance, timestamps, prices, HTML and relative links.

These validate the retained record and rendering, not unobserved real-world truth.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from datetime import timedelta,date
import argparse,math,re
from .common import load,parse_time,official_url,allowed_url,digest
from .config import CURRENT,ROOT,PUBLISHERS,SPORT_MARKETS,FIXTURE_TTL_HOURS,HORIZON_DAYS
from .evidence import verify_capture,fixture_state
from .model import originate,american_from_decimal
from .config import SPORT_INDEX as EVIDENCE_SPORTS
from .desk import (BAND_HIGH, BAND_LOW, HIGH_MIN, PICK_MIN, SPORT_INDEX, MLB_TEAMS, TEAMS,
                   american_from_prob)


def validate_data(directory=CURRENT):
    s=load(directory/'snapshot.json');at=parse_time(s['generated_at']);errors=[]
    caps={p.stem:load(p) for p in (directory/'evidence').glob('*.json')}
    def check(test,message):
        if not test:errors.append(message)
    for c in caps.values():
        try:
            verify_capture(c);check(parse_time(c['observed_before'])<=at,c['id']+': observation after build')
            ids=[o['id'] for o in c['observations']];check(len(ids)==len(set(ids)),c['id']+': duplicate observation ID')
            check(official_url(c['final_url']) if c['role']=='official' else allowed_url(c['final_url'],True),
                  c['id']+': invalid final publisher')
            if c['method']=='http-json-parser':
                raw=directory/'raw'/f'{c["id"]}.body'
                check(raw.is_file(),c['id']+': missing raw evidence')
                if raw.is_file():check(digest(raw.read_bytes())==c['raw_response_sha256'],c['id']+': raw hash mismatch')
        except (ValueError,KeyError,TypeError) as ex:errors.append(c['id']+': '+str(ex))
    network=load(directory/'network.json') if (directory/'network.json').exists() else {}
    for prefix in network.get('successful_feeds', []):
        c=caps.get('http-'+prefix+'-schedule')
        check(c is not None and c.get('complete') is True,
              prefix+': full-slate replacement without complete official capture')
    for prefix,dates in network.get('replace_fixture_dates', {}).items():
        c=caps.get('http-'+prefix+'-schedule')
        check(prefix=='nhl' and c is not None and c.get('complete') is False and
              c.get('covered_dates')==dates and len(dates)==len(set(dates)),
              prefix+': partial date replacement not backed by matching official capture')
    ids=[r['id'] for r in s['fixtures']];check(len(ids)==len(set(ids)),'Duplicate fixture ID')
    for r in s['fixtures']:
        try:
            check(r['sport'] in EVIDENCE_SPORTS,r['id']+': excluded sport')
            f=r['facts'];check(bool(r['source_ids']) and len(r['source_ids'])==len(set(r['source_ids'])),r['id']+': missing/duplicate source IDs')
            check(set(r['field_evidence'])=={k for k,v in f.items() if v is not None},r['id']+': field reference mismatch')
            if r['sport']=='baseball':
                check(f.get('if_necessary') in (None,'Y','N'),r['id']+': invalid MLB conditional flag')
            else:
                check(f.get('if_necessary') is None,r['id']+': MLB conditional flag on other sport')
            for key,value in f.items():
                if value is None:continue
                refs=r['field_evidence'].get(key,[]);check(bool(refs),r['id']+': no evidence for '+key)
                supported=False
                for ref in refs:
                    sid,oid=ref.split('#',1);c=caps[sid]
                    check(sid in r['source_ids'],r['id']+': field source absent from expiry scope')
                    check(c['role']=='official' and official_url(c['url']),r['id']+': discovery used as verification')
                    obs=next(o for o in c['observations'] if o['id']==oid)
                    supported |= obs['values'].get(key)==value
                check(supported,r['id']+': unsupported value '+key)
            earliest=min(parse_time(caps[sid]['observed_after']) for sid in r['source_ids'])
            latest=max(parse_time(caps[sid]['observed_before']) for sid in r['source_ids'])
            check(parse_time(r['verified_after'])==earliest,r['id']+': restamped observation')
            check(parse_time(r['verified_before'])==latest,r['id']+': wrong end bound')
            check(parse_time(r['expires_at'])==earliest+timedelta(hours=FIXTURE_TTL_HOURS),r['id']+': expiry extended')
            check(r['state']==fixture_state(r,at),r['id']+': stale state')
            if f['start_utc']:
                start=parse_time(f['start_utc']);expected_window=at<=start<at+timedelta(days=HORIZON_DAYS)
            else:
                expected_window=f['date'] is None or at.date()<=date.fromisoformat(f['date'])<=at.date()+timedelta(days=HORIZON_DAYS-1)
            check(r['in_window']==expected_window,r['id']+': incorrect rolling-window membership')
            if f['date']:date.fromisoformat(f['date'])
        except (KeyError,ValueError,StopIteration,TypeError) as ex:errors.append(r['id']+': '+str(ex))
    stat_ids=[r['id'] for r in s['statistics']];check(len(stat_ids)==len(set(stat_ids)),'Duplicate statistic ID')
    for r in s['statistics']:
        try:
            c=caps[r['source_id']];o=next(x for x in c['observations'] if x['id']==r['observation_id'])
            check(c['role']=='official','Stat from discovery source')
            for k,v in r.items():
                if k in ('id','source_id','observation_id'):continue
                if k in ('observed_after','observed_before'):check(v==c[k],r['id']+': restamped stat')
                else:check(o['values'].get(k)==v,r['id']+': unsupported stat '+k)
            check(r['games_played']==r['wins']+r['losses']+r.get('ot_losses',0),r['id']+': invalid record arithmetic')
        except (KeyError,ValueError,StopIteration,TypeError) as ex:errors.append(r['id']+': '+str(ex))
    prices={p['fixture_id']:p for p in s['prices']};check(len(prices)==len(s['prices']),'Duplicate price-book row');check(set(prices)==set(ids),'Missing/extra price-book rows')
    for r in s['fixtures']:
        p=prices.get(r['id'])
        if not p:continue
        check(p==originate(r,s['statistics'],at),r['id']+': nonreproducible price / confidence')
        check(p['market_quote'] is None,r['id']+': fabricated bookmaker quote')
        check(p['confidence'] in (None,'low'),r['id']+': unsupported confidence upgrade')
        if p['markets']:
            check(r['state']=='upcoming' and r['in_window'],r['id']+': non-future/out-of-window price')
            if r['sport']=='baseball':
                check(r['facts'].get('if_necessary')=='N',r['id']+': conditional/unknown MLB game priced')
        covered={m['market'] for m in p['markets']}|{m['market'] for m in p['withheld']}
        check(covered==set(SPORT_MARKETS[r['sport']]),r['id']+': uninvestigated market family')
        for m in p['markets']:
            outcomes=m['outcomes'];check(len(outcomes)==2,m['id']+': not a two-way book')
            check(abs(math.fsum(o['probability'] for o in outcomes)-1)<1e-10,m['id']+': mass not 1')
            for o in outcomes:
                pr=o['probability'];check(0<pr<1 and math.isfinite(pr),m['id']+': invalid probability')
                check(abs(o['fair_decimal']*pr-1)<1e-10,m['id']+': price not fair 1/p')
                check(o['american_display']==american_from_decimal(o['decimal_display']),m['id']+': US/decimal mismatch')
                check(o['fair_price_in_target_band']==(1.4<=o['fair_decimal']<=101),m['id']+': false band claim')
    # Displayed KPIs must agree with the actual books and rows, not a hand-edited total.
    counts = {
        'captured_listings': len(s['fixtures']),
        'current_listings': sum(r['in_window'] and r['state'] not in ('stale','closed','date elapsed','start elapsed','observation not yet available','status not pre-match') for r in s['fixtures']),
        'upcoming_exact': sum(r['in_window'] and r['state']=='upcoming' for r in s['fixtures']),
        'categories': len(EVIDENCE_SPORTS),
        'categories_with_listings': sum(c['listing_count']>0 for c in s['coverage']),
        'fully_covered_categories': 0,
        'sources': sum(c['role']=='official' for c in caps.values()),
        'priced_matches': sum(bool(p['markets']) for p in s['prices']),
        'originated_markets': sum(len(p['markets']) for p in s['prices']),
        'originated_outcomes': sum(len(m['outcomes']) for p in s['prices'] for m in p['markets']),
        'unpriced': sum(not p['markets'] for p in s['prices']),
        **{tier: sum(p['confidence']==tier for p in s['prices']) for tier in ('low','medium','high')},
    }
    check(s['counts']==counts,'Snapshot counts do not reconcile with retained rows')
    for c in s['coverage']:
        rows=[r for r in s['fixtures'] if r['sport']==c['slug'] and r['in_window']]
        fresh=[r for r in rows if r['state'] not in ('stale','closed','date elapsed','start elapsed','observation not yet available','status not pre-match')]
        check(c['captured_count']==len(rows) and c['listing_count']==len(fresh),c['slug']+': coverage counts do not reconcile')
        check(c['priced_count']==sum(bool(prices[r['id']]['markets']) for r in fresh if r['id'] in prices),c['slug']+': coverage price count does not reconcile')
    check(s['predictions']==[],'Unsupported High prose release')
    check(s['complete'] is False,'False completeness claim')
    check(len(s['coverage'])==17 and all(not c['scope_complete'] for c in s['coverage']),'False sport completeness')
    return errors

class HTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links=[];self.ids=[];self.rows=[];self.row=None;self.has_td=False
        self.h1=0;self.title=False;self.body={}

    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=='body':self.body=d
        if tag=='h1':self.h1+=1
        if tag=='title':self.title=True
        if d.get('id'):self.ids.append(d['id'])
        for key in ('href','src'):
            if d.get(key):self.links.append(d[key])
        if tag=='tr':self.row=[];self.has_td=False
        if tag=='td':self.has_td=True
        if tag=='a' and self.row is not None and d.get('href'):self.row.append(d['href'])

    def handle_endtag(self,tag):
        if tag=='tr' and self.row is not None:
            if self.has_td:self.rows.append(self.row)
            self.row=None


OFFICIAL_HOSTS = set(PUBLISHERS) | {'www.nhl.com', 'www.mlb.com', 'nhl.com', 'mlb.com'}
DISCOVERY_HOSTS = {'www.olbg.com', 'olbg.com'}
BANNED_IN_PROSE = ('model', 'models', 'verified', 'verification', 'algorithm', 'machine learning',
                   'AI-driven', 'backtested')


def _host(url):
    return urlsplit(url).hostname or ''


def _words(text):
    return [w for w in re.split(r"\s+", text.strip()) if re.search(r"[A-Za-z0-9]", w)]


def _grams(words, n):
    return {tuple(words[i:i + n]) for i in range(len(words) - n + 1)}


def validate_desk(site, directory=None):
    """Gates for the published desk: provenance, arithmetic, band, prose, links."""
    site = Path(site).resolve()
    directory = Path(directory) if directory else site / 'data' / 'desk'
    errors = []

    def check(test, message):
        if not test:
            errors.append(message)

    manifest_path = directory / 'manifest.json'
    desk_path = directory / 'desk.json'
    if not manifest_path.is_file():
        return ['data/desk/manifest.json: missing']
    if not desk_path.is_file():
        return ['data/desk/desk.json: missing']
    manifest = load(manifest_path)
    desk = load(desk_path)

    sources = {s['id']: s for s in desk['sources']}
    check(len(sources) == len(desk['sources']), 'duplicate source id')
    for sid, source in sources.items():
        check(source['url'].startswith('https://'), sid + ': source is not https')
        host = _host(source['url'])
        if source['role'] == 'official':
            check(host in OFFICIAL_HOSTS, sid + ': official source host not on the allowlist')
        else:
            check(host in DISCOVERY_HOSTS, sid + ': discovery source host not on the allowlist')
        check(bool(source.get('observed_at')), sid + ': no read timestamp')
        check(bool(source.get('supports')), sid + ': no stated use')

    ids = [f['id'] for f in desk['fixtures']]
    check(len(ids) == len(set(ids)), 'duplicate fixture id')
    for f in desk['fixtures']:
        check(bool(f['sources']), f['id'] + ': no source')
        for sid in f['sources']:
            check(sid in sources, f['id'] + ': unknown source ' + str(sid))
        check(bool(f['start_utc']), f['id'] + ': no start time')
        if f['priced']:
            check(TEAMS_OK(f), f['id'] + ': priced without both clubs\' records in the dataset')
            for market in f['markets']:
                outcomes = market['outcomes']
                check(len(outcomes) == 2, f['id'] + '/' + market['key'] + ': not a two-way book')
                check(abs(sum(o['p'] for o in outcomes) - 1) < 1e-9,
                      f['id'] + '/' + market['key'] + ': probabilities do not sum to one')
                for o in outcomes:
                    check(0 < o['p'] < 1, f['id'] + '/' + market['key'] + ': invalid probability')
                    check(abs(o['fair_decimal'] * o['p'] - 1) < 5e-4,
                          f['id'] + ': fair decimal is not the reciprocal of the probability')
                    check(o['american'] == american_from_prob(o['p']),
                          f['id'] + ': American price does not follow from the probability')
                    check(o['in_band'] == (BAND_LOW <= o['american'] <= BAND_HIGH),
                          f['id'] + ': band flag does not match the price')
        else:
            check(bool(f.get('unpriced_reason')), f['id'] + ': unpriced with no stated reason')
            check(not f['markets'], f['id'] + ': unpriced but carries markets')

    picks = [f for f in desk['fixtures'] if f['pick']]
    for f in picks:
        p = f['pick']
        check(f['priced'], f['id'] + ': pick on an unpriced fixture')
        check(p['probability'] >= PICK_MIN, f['id'] + ': pick below the 55% floor')
        check(BAND_LOW <= p['american'] <= BAND_HIGH,
              f['id'] + ': pick outside the -250..+10000 band')
        check(p['confidence'] == ('high' if p['probability'] >= HIGH_MIN else 'medium'),
              f['id'] + ': confidence tier does not follow the published threshold')
        text = (p.get('prediction') or '').strip()
        check(text, f['id'] + ': pick has no written prediction')
        if text:
            words = _words(text)
            check(len(words) >= 30, f['id'] + ': prediction is shorter than 30 words')
            low = text.lower()
            for banned in BANNED_IN_PROSE:
                check(banned.lower() not in low, f['id'] + ': prediction contains "' + banned + '"')
            check(p['selection'].split(' -')[0].lower() in low or p['selection'].lower() in low,
                  f['id'] + ': prediction does not name the selection')
    seen = {}
    for f in picks:
        words = _words(f['pick'].get('prediction') or '')
        for gram in _grams(words, 6):
            key = ' '.join(gram).lower()
            seen.setdefault(key, set()).add(f['id'])
    repeated = sorted(k for k, v in seen.items() if len(v) > 1)
    check(not repeated, 'predictions share six-word phrases: ' + '; '.join(repeated[:3]))

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
    check(desk['counts'] == counts, 'desk counts do not reconcile with the rows')
    check(manifest['counts'] == counts, 'manifest counts do not reconcile with the rows')

    # --- pages -----------------------------------------------------------
    parsed_cache = {}

    def parsed(path):
        if path not in parsed_cache:
            parser = HTML()
            parser.feed(path.read_text(encoding='utf-8'))
            parsed_cache[path] = parser
        return parsed_cache[path]

    for rel in manifest['pages']:
        path = site / rel
        if not path.is_file():
            errors.append(rel + ': missing page')
            continue
        parser = parsed(path)
        check(parser.body.get('data-snapshot') == manifest['generated_at'],
              rel + ': snapshot marker missing or mismatched')
        check(parser.h1 == 1, rel + ': page must have exactly one h1')
        check(bool(parser.title), rel + ': page has no title')
        check(len(parser.ids) == len(set(parser.ids)), rel + ': duplicate HTML ids')
        project_only = rel == 'sources.html'
        for index, links in enumerate(parser.rows, 1):
            ok = any((_host(u) in OFFICIAL_HOSTS) or (project_only and _host(u) in DISCOVERY_HOSTS)
                     for u in links if u.startswith('https://'))
            if not ok:
                errors.append(f'{rel}: table row {index} has no official source link')
        for href in parser.links:
            parts = urlsplit(href)
            if parts.scheme or parts.netloc:
                if parts.scheme in ('javascript', 'data'):
                    errors.append(rel + ': unsafe link scheme')
                continue
            target = (path.parent / unquote(parts.path)).resolve() if parts.path else path
            try:
                target.relative_to(site)
            except ValueError:
                errors.append(rel + ': link escapes the published site: ' + href)
                continue
            if target.is_dir():
                target = target / 'index.html'
            if not target.is_file():
                errors.append(rel + ': broken link ' + href)
                continue
            if parts.fragment and target.suffix == '.html':
                if unquote(parts.fragment) not in parsed(target).ids:
                    errors.append(rel + ': missing fragment ' + href)
    if site != ROOT:
        # The published artifact must contain only registered pages. The repository
        # root keeps many earlier desks and legacy pages in place so that their own
        # relative links still resolve; they are not part of the artifact.
        published = {p.name for p in site.glob('*.html')}
        unregistered = published - set(manifest['pages'])
        check(not unregistered, 'unregistered root HTML: ' + ', '.join(sorted(unregistered)))
    return errors


def TEAMS_OK(fixture):
    from .desk import MLB_TEAMS, TEAMS
    table = TEAMS if fixture['sport'] == 'ice-hockey' else MLB_TEAMS
    for code in (fixture['a'], fixture['home']):
        team = table.get(code)
        if not team:
            return False
        if fixture['sport'] == 'ice-hockey' and not team.get('gp'):
            return False
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--site', type=Path, default=ROOT)
    args = parser.parse_args()
    errors = validate_data(ROOT / 'data' / 'current') + validate_desk(args.site)
    for err in errors:
        print('ERROR:', err)
    print(f'Canonical validation: {len(errors)} errors. Source truth is limited to the observations '
          f'retained in data/desk and data/current.')
    raise SystemExit(bool(errors))
