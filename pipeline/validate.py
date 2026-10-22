"""Release gates: field provenance, timestamps, prices, HTML and relative links.

These validate the retained record and rendering, not unobserved real-world truth.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from datetime import timedelta,date
import argparse,math
from .common import load,parse_time,official_url,allowed_url,digest
from .config import CURRENT,ROOT,SPORT_INDEX,SPORT_MARKETS,FIXTURE_TTL_HOURS,HORIZON_DAYS
from .evidence import verify_capture,fixture_state
from .model import originate,american_from_decimal


def validate_data(directory=CURRENT):
    s=load(directory/'snapshot.json');at=parse_time(s['generated_at']);errors=[]
    caps={p.stem:load(p) for p in (directory/'evidence').glob('*.json')}
    def check(test,message):
        if not test:errors.append(message)
    for c in caps.values():
        try:
            verify_capture(c);check(parse_time(c['observed_before'])<=at,c['id']+': observation after build')
            ids=[o['id'] for o in c['observations']];check(len(ids)==len(set(ids)),c['id']+': duplicate observation ID')
            check(allowed_url(c['final_url'],True),c['id']+': invalid final publisher')
            if c['method']=='http-json-parser':
                raw=directory/'raw'/f'{c["id"]}.body'
                check(raw.is_file(),c['id']+': missing raw evidence')
                if raw.is_file():check(digest(raw.read_bytes())==c['raw_response_sha256'],c['id']+': raw hash mismatch')
        except (ValueError,KeyError,TypeError) as ex:errors.append(c['id']+': '+str(ex))
    ids=[r['id'] for r in s['fixtures']];check(len(ids)==len(set(ids)),'Duplicate fixture ID')
    for r in s['fixtures']:
        try:
            check(r['sport'] in SPORT_INDEX,r['id']+': excluded sport')
            f=r['facts'];check(bool(r['source_ids']) and len(r['source_ids'])==len(set(r['source_ids'])),r['id']+': missing/duplicate source IDs')
            check(set(r['field_evidence'])=={k for k,v in f.items() if v is not None},r['id']+': field reference mismatch')
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
        if p['markets']:check(r['state']=='upcoming' and r['in_window'],r['id']+': non-future/out-of-window price')
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
        'categories': len(SPORT_INDEX),
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
        super().__init__(convert_charrefs=True);self.links=[];self.ids=[];self.rows=[];self.row=None;self.has_td=False;self.h1=0;self.title=False;self.body={};self.records=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if 'data-record' in d:self.records.append(d)
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


def validate_site(out):
    out=Path(out).resolve();manifest=load(out/'data/current/site-manifest.json');errors=[];cache={}
    def parsed(path):
        if path not in cache:
            h=HTML();h.feed(path.read_text(encoding='utf-8'));cache[path]=h
        return cache[path]
    snapshot_path=out/'data/current/snapshot.json'
    snapshot=load(snapshot_path) if snapshot_path.is_file() else None
    books={p['fixture_id']:p for p in snapshot['prices']} if snapshot else {}
    if snapshot and 'generated_at' in snapshot:
        for key in ('generated_at','counts','input_sha256'):
            if snapshot.get(key)!=manifest.get(key):errors.append('Snapshot/manifest mismatch: '+key)
    unmanaged={p.name for p in out.glob('*.html')}-set(manifest['pages'])-{'release-review.html'}
    if unmanaged:errors.append('Unregistered root HTML (archive it or register a canonical route): '+', '.join(sorted(unmanaged)))
    for rel in manifest['pages']:
        path=out/rel
        if not path.is_file():errors.append(rel+': missing page');continue
        h=parsed(path)
        if h.body.get('data-snapshot')!=manifest['generated_at']:errors.append(rel+': canonical snapshot marker missing or mismatched')
        if h.h1!=1 or not h.title:errors.append(rel+': heading/title structure')
        if len(h.ids)!=len(set(h.ids)):errors.append(rel+': duplicate HTML IDs')
        for record in h.records:
            priced=record.get('data-priced')=='true' or 'market-book' in record.get('class','').split()
            if not priced:continue
            deadline=record.get('data-price-expires')
            try:
                end=parse_time(deadline)
                if end>parse_time(record['data-expires']) or end>parse_time(record['data-start']):raise ValueError('deadline exceeds fixture/start')
                if record.get('id') in books and deadline!=books[record['id']]['expires_at']:raise ValueError('deadline differs from price book')
            except (ValueError,TypeError,KeyError,AttributeError) as ex:errors.append(rel+': missing/invalid rendered price expiry: '+str(ex))
        for index,links in enumerate(h.rows,1):
            if not any(allowed_url(u,True) or u.startswith('https://github.com/buffedlizard55-lab/OLBG1/') for u in links):errors.append(f'{rel}: row {index} has no official/project source link')
        for href in h.links:
            u=urlsplit(href)
            if u.scheme or u.netloc:
                if u.scheme in ('javascript','data'):errors.append(rel+': unsafe link scheme')
                continue
            target=(path.parent/unquote(u.path)).resolve() if u.path else path
            try:target.relative_to(out)
            except ValueError:errors.append(rel+': link escapes project: '+href);continue
            if target.is_dir():target=target/'index.html'
            if not target.is_file():errors.append(rel+': broken link '+href);continue
            if u.fragment and target.suffix=='.html' and unquote(u.fragment) not in parsed(target).ids:errors.append(rel+': missing fragment '+href)
    return errors

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--site',type=Path,default=ROOT);a=p.parse_args()
    errors=validate_data(a.site/'data/current')+validate_site(a.site)
    for err in errors:print('ERROR:',err)
    print(f'Canonical validation: {len(errors)} errors; source truth remains limited to retained observations.')
    raise SystemExit(bool(errors))
