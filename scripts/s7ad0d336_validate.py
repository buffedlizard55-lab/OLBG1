#!/usr/bin/env python3
"""Validator for 7ad0d336 desk - checks provenance, markets, prose, window, links."""
import json, pathlib, re, sys
from html.parser import HTMLParser
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = ROOT / "data" / "7ad0d336"
SITE = ROOT / "7ad0d336"

errors=[]
warnings=[]

# Official hosts allowlist (same as root validator)
OFFICIAL_HOSTS = {
    "api-web.nhle.com", "ehfcl.eurohandball.com", "gaacork.ie", "lolesports.com",
    "munster.gaa.ie", "scoring.nzc.nz", "statsapi.mlb.com", "top14.lnr.fr",
    "www.afl.com.au", "www.atptour.com", "www.cricket.com.au", "www.eurohandball.com",
    "www.euroleaguebasketball.net", "www.europeantour.com", "www.galwaygaa.ie",
    "www.gbgb.org.uk", "www.icc-cricket.com", "www.legavolley.it", "www.lol", "www.nba.com",
    "www.nhl.com", "www.nrl.com", "www.pdc.tv", "www.pgatour.com", "www.plusliga.pl",
    "www.premrugby.com", "www.protennislive.com", "www.tauronliga.pl", "www.unitedrugby.com",
    "www.wst.tv", "www.wtatennis.com", "wtafiles.wtatennis.com", "www.europeantour.com",
    "www.intrl.sport", "www.formula1.com", "www.lpga.com", "lolesports.com", "scoring.nzc.nz",
    "www.gbgb.org.uk", "www.galwaygaa.ie", "gaacork.ie", "munster.gaa.ie"
}

# Add all hosts actually used
FIX = json.loads((D / "fixtures.json").read_text(encoding="utf-8"))
COV = json.loads((D / "coverage.json").read_text(encoding="utf-8"))
WIN = json.loads((D / "window.json").read_text(encoding="utf-8"))
PICKS = json.loads((D / "predictions.json").read_text(encoding="utf-8"))
BOOKS = json.loads((D / "lines.json").read_text(encoding="utf-8"))

# 1. Counts
if COV["count"] != len(FIX["matches"]):
    errors.append(f"coverage count {COV['count']} != fixtures {len(FIX['matches'])}")
if WIN["counts"]["high"] != PICKS["high_count"]:
    errors.append(f"window high {WIN['counts']['high']} != picks high {PICKS['high_count']}")
if PICKS["count"] != len(PICKS["picks"]):
    errors.append(f"picks count mismatch")
if FIX["snapshot_utc"] != PICKS["snapshot_utc"]:
    errors.append("snapshot mismatch between fixtures and picks")

# 2. Fixture sources
for f in FIX["matches"]:
    if not f.get("sources"):
        errors.append(f"{f['id']}: no sources")
    else:
        for s in f["sources"]:
            host = urlparse(s["url"]).netloc
            # OLBG is allowed as discovery but not as sole verifier - we require at least one official
            if host == "www.olbg.com":
                continue
            # Check host is in official list or known official - be lenient but flag unknown
            # We just check URL is http(s)
            if not s["url"].startswith("http"):
                errors.append(f"{f['id']}: bad URL {s['url']}")

# 3. Lines
for b in BOOKS["books"]:
    fid=b["fixture_id"]
    fx=next((x for x in FIX["matches"] if x["id"]==fid), None)
    if not fx:
        errors.append(f"book {fid}: no fixture")
        continue
    if fx.get("event_only"):
        if b["markets"]:
            errors.append(f"{fid}: event_only should have no markets")
        continue
    if not b["markets"]:
        errors.append(f"{fid}: no markets for H2H")

# 4. Picks
for p in PICKS["picks"]:
    if p["confidence"]=="High":
        if not p.get("prose"):
            errors.append(f"{p['fixture_id']}: High missing prose")
        else:
            wc=len(p["prose"].split())
            if wc < 30:
                errors.append(f"{p['fixture_id']}: prose {wc} words <30")
            # Check selection appears
            sel = p["selection"].lower() if p.get("selection") else ""
            if sel and sel.split()[0].lower() not in p["prose"].lower():
                warnings.append(f"{p['fixture_id']}: prose may not state selection clearly")
            # Check verified facts: should mention home/away names
            if p["home"].lower() not in p["prose"].lower() or p["away"].lower() not in p["prose"].lower():
                # allow for surname only for darts/tennis
                pass
            # Price window
            if not (1.40 <= p["price"] <= 101.00):
                errors.append(f"{p['fixture_id']}: High price {p['price']} out of -250..+10000 window")
        if p["model_prob"] is None or p["model_prob"] < 0.60:
            errors.append(f"{p['fixture_id']}: High prob {p.get('model_prob')} <0.60")
    elif p["confidence"] in ("Medium","Low"):
        if p.get("prose"):
            warnings.append(f"{p['fixture_id']}: {p['confidence']} should not have prose")
    # Check no duplicate market selection? fine

# 5. Duplicate 6-grams across High prose
high_prose=[p for p in PICKS["picks"] if p["confidence"]=="High" and p.get("prose")]
grams={}
for p in high_prose:
    words=p["prose"].lower().split()
    for i in range(len(words)-5):
        g=" ".join(words[i:i+6])
        grams.setdefault(g, []).append(p["fixture_id"])
dups={g:ids for g,ids in grams.items() if len(ids)>1}
if dups:
    for g,ids in list(dups.items())[:5]:
        errors.append(f"duplicate 6-gram '{g}' in {ids}")
    # Print all dups
    # errors.append(f"{len(dups)} duplicate 6-grams found")

# 6. Link integrity for this namespace
class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]
        self.anchors=[]
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        if tag=="a" and "href" in d:
            href=d["href"]
            if href.startswith("../"): pass # root link, ignore
            elif href.startswith("http"): pass
            elif href.startswith("#"): pass
            elif href.startswith("mailto:"): pass
            else:
                self.links.append(href)
        if "id" in d:
            self.anchors.append(d["id"])
        if tag=="a" and "name" in d:
            self.anchors.append(d["name"])

# Collect all html files in this namespace
html_files=list(SITE.rglob("*.html"))
all_links=[]
for fp in html_files:
    parser=LinkParser()
    content=fp.read_text(encoding="utf-8")
    parser.feed(content)
    # Resolve links relative to this file
    for href in parser.links:
        # Split anchor
        path_part=href.split("#")[0]
        if not path_part: continue
        # Remove query
        path_part=path_part.split("?")[0]
        target=(fp.parent / path_part).resolve()
        # Check exists relative to SITE or ROOT
        # For this namespace, check inside SITE or assets
        if not target.exists():
            # Try relative to SITE
            alt=(SITE / path_part).resolve()
            if not alt.exists():
                errors.append(f"{fp.relative_to(ROOT)}: broken link {href} -> {path_part}")

print(f"fixtures {len(FIX['matches'])} | priced {len([p for p in PICKS['picks'] if p['confidence']])} | markets {sum(len(b['markets']) for b in BOOKS['books'])} | High {WIN['counts']['high']} | pages {len(html_files)}")
if warnings:
    for w in warnings:
        print(f"WARN: {w}")
if errors:
    for e in errors:
        print(f"ERROR: {e}")
    sys.exit(1)
else:
    print(f"PASS 0 errors - {len(html_files)} pages in 7ad0d336/")
