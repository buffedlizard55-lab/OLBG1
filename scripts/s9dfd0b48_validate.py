#!/usr/bin/env python3
"""Desk gate for session 9dfd0b48-olbg1: sources, prices, prose, links, coverage. No network."""
from __future__ import annotations
import json, os, re, sys
from html.parser import HTMLParser
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "9dfd0b48"); SITE = os.path.join(ROOT, "9dfd0b48")
OFFICIAL = {"www.atptour.com", "www.wst.tv", "www.euroleaguebasketball.net", "statsapi.mlb.com", "api-web.nhle.com"}
errs = []

def load(n): return json.load(open(os.path.join(DATA, n)))["items"]

class Rows(HTMLParser):
    def __init__(s): super().__init__(); s.rows=[]; s.cur=None; s.links=[]; s.inbody=False
    def handle_starttag(s, t, a):
        a=dict(a)
        if t=="tbody": s.inbody=True
        if t=="tr" and s.inbody: s.cur=[]
        if t=="a" and a.get("href") is not None:
            s.links.append(a["href"])
            if s.cur is not None: s.cur.append(a["href"])
    def handle_endtag(s, t):
        if t=="tr" and s.cur is not None: s.rows.append(s.cur); s.cur=None
        if t=="tbody": s.inbody=False

fx, mk, pk, pr, fl, cov = (load(n) for n in ("fixtures.json","markets.json","picks.json","predictions.json","flags.json","coverage.json"))
ids = {f["id"] for f in fx}
for f in fx:
    hosts = {re.sub(r"^https://([^/]+).*$", r"\1", s["url"]) for s in f["sources"]}
    if not hosts & OFFICIAL: errs.append(f"{f['id']}: no official host in sources {hosts}")
    if not re.match(r"20\d\d-\d\d-\d\dT\d\d:\d\dZ$", f["start"]): errs.append(f"{f['id']}: bad start {f['start']}")
    if f["priced"] and not any(m["fixture"]==f["id"] for m in mk): errs.append(f"{f['id']}: priced but no markets")
    if not f["priced"] and not any(g.get("ref")==f["id"] and g["code"]=="UNPRICED" for g in fl): errs.append(f"{f['id']}: unpriced without UNPRICED flag")
for m in mk:
    if m["fixture"] not in ids: errs.append(f"market orphan {m}")
    if abs(m["p_a"]+m["p_b"]-1)>1e-3: errs.append(f"{m['fixture']} {m['market']}: probs do not sum to 1")
    if not (-10000<=m["price_a"]<=10000 and -10000<=m["price_b"]<=10000): errs.append(f"{m['fixture']}: price range")
    if not m["source"].startswith("https://"): errs.append(f"{m['fixture']}: market source not https")
hi = [p for p in pk if p["confidence"]=="High"]
for p in hi:
    if not (-250 <= p["featured"]["price"] <= 10000): errs.append(f"{p['fixture']}: High featured price {p['featured']['price']} outside window")
    if not any(q["fixture"]==p["fixture"] for q in pr): errs.append(f"{p['fixture']}: High pick without prediction")
for p in pk:
    if p["confidence"] not in ("High","Medium","Low"): errs.append(f"{p['fixture']}: bad tier")
    if (p["p"]>=0.70) != (p["confidence"]=="High"): errs.append(f"{p['fixture']}: tier/prob mismatch")
seen6 = {}
for q in pr:
    w = q["text"].split()
    if len(w) < 30: errs.append(f"{q['fixture']}: prediction {len(w)} words")
    if not any(w in q["text"] for w in q["selection"].split() if len(w) >= 4): errs.append(f"{q['fixture']}: selection not named")
    for i in range(len(w)-5):
        k=" ".join(x.lower().strip(".,;:") for x in w[i:i+6])
        if k in seen6 and seen6[k]!=q["fixture"]: errs.append(f"{q['fixture']}: shares phrase '{k}' with {seen6[k]}")
        seen6[k]=q["fixture"]
if len({c["sport"] for c in cov}) != 17: errs.append("coverage must list 17 sports")
for g in fl:
    if not g["url"].startswith("https://"): errs.append(f"flag without https url: {g['label'][:40]}")
# site
pages = []
for d,_,fs in os.walk(SITE):
    pages += [os.path.join(d,f) for f in fs if f.endswith(".html")]
for pg in pages:
    r = Rows(); r.feed(open(pg).read())
    for i,row in enumerate(r.rows,1):
        if not any(h.startswith("https://") for h in row): errs.append(f"{os.path.relpath(pg,ROOT)}: table row {i} has no https source link")
    for h in r.links:
        if h.startswith("http://"): errs.append(f"{pg}: http link {h}")
        if not h.startswith(("https://","#","mailto:")):
            dest = os.path.normpath(os.path.join(os.path.dirname(pg), h.split("#")[0]))
            if not os.path.isfile(dest): errs.append(f"{os.path.relpath(pg,ROOT)}: broken link {h}")
    if "linear-gradient" in open(pg).read(): errs.append(f"{pg}: gradient")
print(f"fixtures={len(fx)} markets={len(mk)} picks={len(pk)} high={len(hi)} predictions={len(pr)} flags={len(fl)} pages={len(pages)}")
if errs:
    print("\n".join("ERROR "+e for e in errs)); sys.exit(1)
print("OK: desk 9dfd0b48 passes")
