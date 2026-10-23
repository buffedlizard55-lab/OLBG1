#!/usr/bin/env python3
"""T67 gate. Fails loudly rather than letting a broken desk through.

Checks
  1  row counts agree across files
  2  every discovery row has an https OLBG link and a known sport
  3  every fixture cites an official source that exists
  4  every price cites a source that exists
  5  every grade is recomputed from p and the American price, not trusted
  6  the band ledger is complete: any official row at or above 70% outside -250..+10000 is listed
  7  predictions: 30+ words, no banned word, unique text, selection matches a priced official row,
     every fact source resolves
  8  flags: unique ids, valid severity, source resolves
  9  pages: 24 exist, no script tag, no localhost, no http, every relative link resolves, stamp present
 10  no banned word appears in the rendered prediction pages

Run: python3 scripts/scf2699ba_validate.py   (exit 1 on any error)
"""
import json
import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "cf2699ba"
SITE = ROOT / "cf2699ba"

BANNED = ["model", "verified"]
BAND_LOW, BAND_HIGH = -250, 10000
errors = []
checks = []


def ok(name, cond, detail=""):
    checks.append((name, cond, detail))
    if not cond:
        errors.append(f"{name}: {detail}")


def load(name):
    return json.loads((DATA / name).read_text())


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs, self.scripts, self.text = [], [], []

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.scripts.append(dict(attrs))
        if tag == "a":
            for k, v in attrs:
                if k == "href" and v:
                    self.hrefs.append(v)
        if tag == "link":
            self.hrefs.append(dict(attrs).get("href", ""))

    def handle_data(self, data):
        self.text.append(data)


def main():
    sports = load("sports.json")
    sources = load("sources.json")
    discovery = load("discovery.json")
    fixtures = load("fixtures.json")
    lines = load("lines.json")
    preds = load("predictions.json")
    flags = load("flagged.json")

    keys = {s["key"] for s in sports}
    src_ids = {s["id"] for s in sources}
    rows = lines["rows"]
    official = [r for r in rows if r["class"] == "official"]
    consensus = [r for r in rows if r["class"] == "consensus"]

    # 1 counts
    ok("sports = 15", len(sports) == 15, str(len(sports)))
    ok("discovery = 134", len(discovery) == 134, str(len(discovery)))
    ok("fixtures = 6", len(fixtures) == 6, str(len(fixtures)))
    ok("official prices = 16", len(official) == 16, str(len(official)))
    ok("indicative prices = 117", len(consensus) == 117, str(len(consensus)))
    ok("predictions = 7", len(preds) == 7, str(len(preds)))
    ok("flags = 21", len(flags) == 21, str(len(flags)))
    ok("sources = 9", len(sources) == 9, str(len(sources)))

    # 2 discovery integrity
    for r in discovery:
        ok(f"discovery sport {r['olbg_event_id']}", r["sport"] in keys, r["sport"])
        ok(f"discovery url {r['olbg_event_id']}", r["url"].startswith("https://www.olbg.com/"), r["url"])
        ok(f"discovery share {r['olbg_event_id']}", 0 < r["share"] <= 1, str(r["share"]))
    ids = [r["olbg_event_id"] for r in discovery]
    ok("discovery ids unique", len(ids) == len(set(ids)), "duplicates present")

    # 3 fixtures cite an official source
    for f in fixtures:
        ok(f"fixture source {f['id']}", f["evidence"] in src_ids, f["evidence"])
        src = next(s for s in sources if s["id"] == f["evidence"])
        ok(f"fixture source official {f['id']}", src["official"] is True, f["evidence"])
        ok(f"fixture sport {f['id']}", f["sport"] in keys, f["sport"])

    # 4-5 prices
    for r in rows:
        for sid in r["source"].split("+"):
            ok(f"price source {r['selection']}", sid in src_ids, sid)
        p, am = r["p"], r["american"]
        recomputed = round(-100.0 * p / (1 - p)) if p > 0.5 else round(100.0 * (1 - p) / p)
        ok(f"american recomputes {r['selection']} {r['market']}", abs(recomputed - am) <= 1,
           f"{am} != {recomputed}")
        ok(f"decimal recomputes {r['selection']} {r['market']}", abs(r["decimal"] - 1 / p) < 5e-3,
           str(r["decimal"]))
        if r["class"] == "official":
            want = "High" if (p >= 0.70 and BAND_LOW <= am <= BAND_HIGH) else ("Medium" if p >= 0.62 else "Low")
        else:
            want = "Low"
        ok(f"grade {r['selection']} {r['market']}", r["tier"] == want, f"{r['tier']} != {want}")
        ok(f"band flag {r['selection']} {r['market']}",
           r["in_band"] == (BAND_LOW <= am <= BAND_HIGH), str(r["in_band"]))

    # 6 band ledger
    ledger = {(x["selection"], x["market"]) for x in lines["out_of_band"]}
    expect = {(r["selection"], r["market"]) for r in official if r["p"] >= 0.70 and not r["in_band"]}
    ok("out-of-band ledger complete", ledger == expect, f"{ledger} != {expect}")
    tiers = lines["tier_counts"]
    ok("tier counts add up", sum(tiers.values()) == len(rows), str(tiers))
    ok("no High published without a qualifying row",
       tiers.get("High", 0) == sum(1 for r in rows if r["tier"] == "High"), str(tiers))

    # 7 predictions
    bodies = {}
    priced = {(r["fixture_id"], r["selection"]): r for r in official}
    for p in preds:
        words = len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-]*", p["body"]))
        ok(f"prediction {p['id']} length", words >= 30, str(words))
        ok(f"prediction {p['id']} word count field", p["words"] == words, f"{p['words']} != {words}")
        low = p["body"].lower()
        ok(f"prediction {p['id']} banned word", not any(re.search(rf"\b{w}\b", low) for w in BANNED), low[:60])
        ok(f"prediction {p['id']} unique", p["body"] not in bodies, "duplicate body")
        bodies[p["body"]] = p["id"]
        ok(f"prediction {p['id']} price exists", (p["fixture_id"], p["selection"]) in priced,
           p["selection"])
        pr = priced.get((p["fixture_id"], p["selection"]))
        if pr:
            ok(f"prediction {p['id']} price matches model", pr["american"] == p["american"],
               f"{pr['american']} != {p['american']}")
        ok(f"prediction {p['id']} states a selection", p["selection"].split()[0].lower() in low,
           p["selection"])
        for f in p["facts"]:
            ok(f"prediction {p['id']} fact source", f["src"] in src_ids, f["src"])
            ok(f"prediction {p['id']} fact filled", bool(f["k"]) and bool(f["v"]), str(f))

    # 8 flags
    fids = [f["id"] for f in flags]
    ok("flag ids unique", len(fids) == len(set(fids)), "duplicates")
    for f in flags:
        ok(f"flag severity {f['id']}", f["severity"] in {"high", "medium", "low"}, f["severity"])
        ok(f"flag source {f['id']}", f["source"] in src_ids, f["source"])
        for field in ("row", "issue", "action"):
            ok(f"flag text {f['id']} {field}", bool(f[field].strip()), "empty")

    # 9 pages
    pages = sorted(SITE.rglob("*.html"))
    ok("24 pages", len(pages) == 24, str(len(pages)))
    ok("15 sport pages", len(list((SITE / "sports").glob("*.html"))) == 15,
       str(len(list((SITE / "sports").glob("*.html")))))
    sport_pages = {p.stem for p in (SITE / "sports").glob("*.html")}
    ok("sport page per sport", sport_pages == keys, str(sport_pages ^ keys))

    for page_path in pages:
        raw = page_path.read_text()
        rel = page_path.relative_to(SITE)
        lp = Links()
        lp.feed(raw)
        ok(f"{rel} no script", not lp.scripts and "<script" not in raw.lower(), "script tag present")
        ok(f"{rel} snapshot stamp", "Snapshot taken 2026-10-23" in raw, "footer stamp missing")
        ok(f"{rel} no localhost", "localhost" not in raw and "127.0.0.1" not in raw, "localhost reference")
        for href in lp.hrefs:
            if href.startswith(("http://",)):
                ok(f"{rel} insecure link", False, href)
                continue
            if href.startswith(("https://", "mailto:", "#")):
                continue
            target = (page_path.parent / href.split("#")[0]).resolve()
            ok(f"{rel} link {href}", target.is_file(), "unresolved")

    # 10 rendered prose
    for name in sorted(x.relative_to(SITE).as_posix() for x in pages):
        raw = (SITE / name).read_text()
        lp = Links()
        lp.feed(raw)
        text = " ".join(lp.text).lower()
        hits = [w for w in BANNED if re.search(rf"\b{w}\b", text)]
        ok(f"{name} free of banned words", not hits, str(hits))

    passed = sum(1 for _n, c, _d in checks if c)
    print(f"gates run: {len(checks)}  passed: {passed}  failed: {len(errors)}")
    if errors:
        print("\nERRORS")
        for x in errors[:60]:
            print("  -", x)
        print(f"\nVALIDATION FAILED ({len(errors)} errors)")
        return 1
    print("\nVALIDATION PASSED (0 errors)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
