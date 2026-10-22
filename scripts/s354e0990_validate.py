#!/usr/bin/env python3
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
desk=json.loads((ROOT/'data/354e0990/desk.json').read_text())
errs=[]
def chk(c,m):
    if not c: errs.append(m)
# counts
chk(desk['counts']['high']==0,'high must be 0 under gates')
for r in desk['priced']:
    chk(r['source_urls'] and all(u.startswith('https://') for u in r['source_urls']),f"{r['id']} official source")
    chk(abs(sum(o['probability'] for m in r['markets'] for o in []) )>=0,'noop')
    for m in r['markets']:
        chk(abs(sum(o['probability'] for o in m['outcomes'])-1)<1e-6,f"{r['id']} {m['market']} probs sum")
        for o in m['outcomes']:
            chk(abs(o['fair_decimal']-1/o['probability'])<1e-6,f"{r['id']} fair=1/p")
    # no high mislabel
    chk(r['confidence']=='low',f"{r['id']} confidence must be low")
    if r['probability']>0.70 and r['in_band']:
        errs.append(f"{r['id']} qualifies prob+band but tier not reviewed")
for r in desk['time_unverified']:
    chk(not r.get('selection'),f"{r['id']} time-unverified must have no selection")
# predictions
texts=[p['text'] for p in desk['predictions']]
for p in desk['predictions']:
    chk(p['words']>=30 and len(p['text'].split())>=30,f"{p['fixture_id']} >=30 words")
    chk(p['selection'] in p['text'],f"{p['fixture_id']} selection named in prose")
# uniqueness: no shared 6-gram
from collections import Counter
grams=Counter()
for t in texts:
    w=re.findall(r"[a-z']+",t.lower())
    for g in [' '.join(w[i:i+6]) for i in range(len(w)-5)]: grams[g]+=1
shared=[g for g,c in grams.items() if c>1]
chk(not shared,f"shared 6-grams: {shared[:3]}")
# site links
site=ROOT/'354e0990'
for htmlf in site.glob('*.html'):
    txt=htmlf.read_text()
    for href in re.findall(r'href=([^\s>]+)',txt):
        href=href.strip("'\"")
        if href.startswith('http') or href.startswith('#'): continue
        target=(htmlf.parent/href).resolve()
        # ../data links resolve relative to repo root serving
        chk(target.exists(),f"{htmlf.name} broken local link {href}")
    chk('%%' not in txt,f"{htmlf.name} render artifact")
print(f"T354E VALIDATION {'FAILED' if errs else 'PASSED'}: priced={desk['counts']['priced_upcoming']} predictions={len(texts)} errors={len(errs)}")
for e in errs: print(' -',e)
sys.exit(1 if errs else 0)
