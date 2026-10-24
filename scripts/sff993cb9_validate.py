"""Validate the ff993cb9 desk: band rules, prose rules, links, page set. Exit 1 on any failure."""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "ff993cb9"
DATA = json.loads((ROOT / "data" / "ff993cb9" / "desk.json").read_text())
PICKS = DATA["picks"]
fails = []
def chk(ok, msg):
    if not ok: fails.append(msg)

# --- per-pick rules ---
ids = set()
for p in PICKS:
    chk(p["id"] not in ids, f"duplicate id {p['id']}"); ids.add(p["id"])
    chk(p["words"] >= 30, f"{p['id']} prediction only {p['words']} words")
    low = p["prediction"].lower()
    chk("model" not in low, f"{p['id']} prediction uses internal word 'model'")
    chk("verified" not in low, f"{p['id']} prediction uses internal word 'verified'")
    key = re.sub(r"[^a-zà-ÿ ]", "", p["selection"].lower()).split()
    chk(any(w in low for w in key[:2]) if key else False, f"{p['id']} prediction does not name its selection")
    am = int(p["fair_american"])
    chk(-250 <= am <= 10000, f"{p['id']} fair price {am} outside -250..+10000")
    chk(p["official"].startswith("https://"), f"{p['id']} missing official source")
    chk("olbg.com" not in p["official"], f"{p['id']} uses OLBG as fact source")
    if p["confidence"] == "High":
        chk(p["prob"] >= 0.70, f"{p['id']} High below 70%")
        chk(-250 <= am, f"{p['id']} High shorter than -250")
    if p["prob"] >= 0.70:
        chk(p["confidence"] == "High" or am < -250, f"{p['id']} 70%+ in-band but not High")

# --- uniqueness: no shared 6-gram between any two predictions ---
def grams(text, n=6):
    w = re.sub(r"[^a-zà-ÿ0-9 ]", "", text.lower()).split()
    return {" ".join(w[i:i+n]) for i in range(len(w)-n+1)}
seen = {}
for p in PICKS:
    for g in grams(p["prediction"]):
        if g in seen and seen[g] != p["id"]:
            fails.append(f"shared 6-gram between {seen[g]} and {p['id']}: '{g}'"); break
        seen[g] = p["id"]

# --- coverage honesty ---
sports = [s for s, _, _ in __import__("sys") and []]  # placeholder no-op
from collections import Counter
cnt = Counter(p["sport"] for p in PICKS)
print("Picks per sport:", dict(cnt))
chk(cnt.get("greyhounds", 0) == 0, "greyhounds must carry zero picks (flag F-FF-01)")
for slug in ["golf","volleyball","cricket","darts","gaelic-sports","tennis","motor-racing","handball","ice-hockey","basketball","rugby-league"]:
    chk(cnt.get(slug, 0) >= 5, f"{slug} below 5 picks: {cnt.get(slug,0)}")

# --- page set + internal links ---
need = ["index.html","picks.html","predictions.html","matches.html","markets.html","sports.html",
        "flagged.html","sources.html","methodology.html","olbg.html","repo-audit.html","assets/style.css"]
need += [f"sports/{s}.html" for s in ["golf","volleyball","rugby-union","cricket","snooker","darts","baseball",
         "gaelic-sports","greyhounds","tennis","motor-racing","handball","ice-hockey","basketball","rugby-league"]]
for n in need: chk((OUT / n).exists(), f"missing page {n}")
htmls = list(OUT.rglob("*.html"))
all_ids = {}
for f in htmls:
    all_ids[f.relative_to(OUT).as_posix()] = set(re.findall(r'id="([^"]+)"', f.read_text()))
for f in htmls:
    txt = f.read_text()
    chk(txt.count("<h1") == 1, f"{f.name} has {txt.count('<h1')} h1 elements")
    for href in re.findall(r'href="([^"#]+)(?:#([^"]+))?"', txt):
        target, frag = href
        if target.startswith(("http", "mailto")): continue
        tp = (f.parent / target).resolve()
        chk(tp.exists(), f"{f.relative_to(OUT)} links to missing {target}")
        if frag and tp.exists():
            rel = tp.relative_to(OUT.resolve()).as_posix()
            chk(frag in all_ids.get(rel, set()), f"{f.relative_to(OUT)} links to missing anchor #{frag} in {rel}")
for f in htmls:
    t = f.read_text().lower()
    chk("lorem" not in t and "placeholder" not in t.replace("placeholder 06:00",""), f"{f.name} contains filler text")

idx = (OUT / "index.html").read_text()
chk("High-confidence picks" in idx and "Best pick in every sport" in idx, "index missing executive summary tables")

if fails:
    print(f"VALIDATE FAIL ({len(fails)}):")
    for x in fails[:40]: print(" -", x)
    sys.exit(1)
print(f"VALIDATE PASS: {len(PICKS)} picks, {len(htmls)} pages, all band/prose/link checks green.")
