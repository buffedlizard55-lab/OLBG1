"""Release gate for desk d33cf454.

Checks, in order:
  1. every event and pick resolves to a known source id;
  2. no pick claims a tier its own numbers do not support;
  3. every prediction is >= 30 words, unique, and free of the banned words;
  4. every generated page exists and every relative link/fragment resolves;
  5. the JSON under data/d33cf454 is exactly what the data module produces.
Exit code 1 on any failure. Prints a line per rule.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.sd33cf454_data import SOURCES, EVENTS, PICKS, SPORTS, FLAGS, COVERAGE

DESK = "d33cf454"
OUT = ROOT / DESK
DATA = ROOT / "data" / DESK
BANNED = ("model", "verified", "verify")
errors, checks = [], 0


def check(ok, msg):
    global checks
    checks += 1
    if not ok:
        errors.append(msg)


def wc(t):
    return len(re.findall(r"[A-Za-z0-9'’/?.-]+", t))


# 1. provenance
for ev in EVENTS:
    check(bool(ev["src"]), f"{ev['id']}: no source")
    for sid in ev["src"]:
        check(sid in SOURCES, f"{ev['id']}: unknown source {sid}")
    check(ev["sport"] in {s for s, _, _ in SPORTS}, f"{ev['id']}: sport outside the fifteen")
    check(ev["basis"] in ("", "official", "derived"), f"{ev['id']}: bad time basis")
    if ev["basis"] == "official":
        check(bool(ev["start"]), f"{ev['id']}: official basis without a start")
    if ev["start"]:
        check(
            bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", ev["start"])),
            f"{ev['id']}: bad start format",
        )
for sid, s in SOURCES.items():
    check(s["url"].startswith("https://"), f"{sid}: non-https source")
    check(s["role"] in ("official", "discovery"), f"{sid}: bad role")
for slug, name, path in SPORTS:
    check(slug in COVERAGE, f"{slug}: missing coverage note")

# 2. tier arithmetic
ev_by_id = {x["id"]: x for x in EVENTS}
for p in PICKS:
    check(p["event"] in ev_by_id, f"{p['id']}: unknown event")
    check(0 < p["prob"] < 1, f"{p['id']}: probability out of range")
    fair = int(round(-100 * p["prob"] / (1 - p["prob"]))) if p["prob"] >= 0.5 else int(round(100 * (1 - p["prob"]) / p["prob"]))
    check(abs(fair - p["american"]) <= 2, f"{p['id']}: american price does not match probability")
    in_band = -250 <= p["american"] <= 10000
    if p["tier"] == "High":
        check(p["prob"] > 0.70 and in_band, f"{p['id']}: High claimed outside the >70% band")
    else:
        check(not (p["prob"] > 0.70 and in_band), f"{p['id']}: qualifies for High but is labelled {p['tier']}")
    ev = ev_by_id[p["event"]]
    check(any(SOURCES[s]["role"] == "official" for s in ev["src"]), f"{p['id']}: priced without an official source")
    check(len(p["markets"]) >= 2, f"{p['id']}: fewer than two markets examined")

# 3. prose
seen = []
for p in PICKS:
    t = p["prediction"]
    check(wc(t) >= 30, f"{p['id']}: prediction under 30 words ({wc(t)})")
    for w in BANNED:
        check(w not in t.lower(), f"{p['id']}: banned word '{w}' in public prediction")
    grams = {
        " ".join(re.findall(r"[a-z0-9']+", t.lower())[i : i + 6])
        for i in range(max(0, len(re.findall(r"[a-z0-9']+", t.lower())) - 5))
    }
    for other_id, other in seen:
        dup = grams & other
        check(len(dup) <= 1, f"{p['id']} repeats a six-word phrase from {other_id}: {sorted(dup)[:2]}")
    seen.append((p["id"], grams))

# 4. pages and links
pages = sorted(OUT.rglob("*.html"))
check(len(pages) >= 20, f"only {len(pages)} pages built")
link_re = re.compile(r'(?:href|src)=["\']([^\'"]+)["\']')
ids = {}
for page in pages:
    txt = page.read_text(encoding="utf-8")
    ids[page] = set(re.findall(r'id=(["\'])([^\'"]+)\1', txt))
    ids[page] = {m[1] for m in ids[page]}
for page in pages:
    txt = page.read_text(encoding="utf-8")
    for target in link_re.findall(txt):
        if target.startswith(("http://", "https://", "mailto:", "#", "data:")):
            if target.startswith("#") and target[1:] and target[1:] not in ids[page]:
                errors.append(f"{page.name}: missing fragment {target}")
            continue
        path, _, frag = target.partition("#")
        dest = (page.parent / path).resolve() if path else page
        check(dest.exists(), f"{page.relative_to(ROOT)}: broken link {target}")
        if frag and dest.exists() and dest.suffix == ".html":
            check(frag in ids.get(dest, set()), f"{page.relative_to(ROOT)}: missing fragment {target}")

# 5. data files match the module
expect = {
    "events": EVENTS,
    "picks": PICKS,
    "sources": SOURCES,
    "coverage": COVERAGE,
    "flags": [dict(id=a, finding=b, scope=c, detail=d, link=f) for a, b, c, d, f in FLAGS],
}
for name, obj in expect.items():
    f = DATA / f"{name}.json"
    check(f.exists(), f"missing {f}")
    if f.exists():
        check(
            json.loads(f.read_text(encoding="utf-8")) == json.loads(json.dumps(obj)),
            f"{f.name}: out of date",
        )

# report
print(f"desk {DESK}: {checks} checks, {len(errors)} failures")
for line in errors[:40]:
    print("  FAIL", line)
print(
    f"  pages={len(pages)} events={len(EVENTS)} picks={len(PICKS)} "
    f"official_sources={sum(1 for s in SOURCES.values() if s['role']=='official')}"
)
sys.exit(1 if errors else 0)