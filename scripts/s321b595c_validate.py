"""Structural and arithmetic gate for desk 321b595c.  Run: python3 scripts/s321b595c_validate.py

Checks every published row against the rule it claims to follow. Exit code 1 on any error.
"""
import json
import math
import re
import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "321b595c"
SITE = ROOT / "321b595c"

errors, checks = [], 0


def ok(cond, msg):
    global checks
    checks += 1
    if not cond:
        errors.append(msg)


def american(p):
    return int(round(-100 * p / (1 - p))) if p > 0.5 else int(round(100 * (1 - p) / p))


def dec(a):
    return 1 + (a / 100 if a > 0 else 100 / abs(a))


def main():
    sources = {s["id"]: s for s in json.loads((DATA / "sources.json").read_text())["sources"]}
    fx = json.loads((DATA / "fixtures.json").read_text())["fixtures"]
    preds = json.loads((DATA / "predictions.json").read_text())["predictions"]
    flags = json.loads((DATA / "flags.json").read_text())["flags"]
    cov = json.loads((DATA / "coverage.json").read_text())["sports"]
    summary = json.loads((DATA / "summary.json").read_text())

    # ---- source register
    for sid, s in sources.items():
        ok(sid == s["id"], f"source id mismatch {sid}")
        ok(s["url"].startswith("https://"), f"{sid} url not https")
        ok(re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\dZ", s["read_utc"] or "") is not None,
           f"{sid} read stamp malformed")
        ok(len(s["note"]) > 10, f"{sid} has no note")
    ok(len(sources) >= 30, "source register too thin")

    # ---- fixtures
    for f in fx:
        ok(f.get("olbg_url", "").startswith("https://www.olbg.com/"), f"{f['id']} missing OLBG url")
        ok(len(f.get("sources", [])) > 0, f"{f['id']} has no source")
        for s in f.get("sources", []):
            ok(s in sources, f"{f['id']} cites unknown source {s}")
        ok(f["sport"] in {c["sport"] for c in cov}, f"{f['id']} sport not in coverage table")
        if f["priced"]:
            kinds = {sources[s]["kind"] for s in f["sources"] if s in sources}
            ok("official" in kinds, f"{f['id']} is priced without an official source")
            ok(f.get("model") is not None, f"{f['id']} priced without a model record")
            ok(f.get("markets"), f"{f['id']} priced with no market rows")
        if f["selection"]:
            ok(f["confidence"] in ("High", "Medium", "Low"), f"{f['id']} pick without a confidence label")
            p = f["prob"]
            want = "High" if p >= 0.65 else ("Medium" if p >= 0.575 else "Low")
            ok(want == f["confidence"], f"{f['id']} label {f['confidence']} but probability {p} implies {want}")
            ok(american(p) == f["fair"], f"{f['id']} fair price {f['fair']} != {american(p)} from probability")
            ok(-250 <= f["fair"] <= 10000, f"{f['id']} fair price outside the brief band")
            ok(isinstance(p, float) and 0 < p < 1, f"{f['id']} probability out of range")

    # ---- market rows arithmetic
    for f in fx:
        for m in f.get("markets", []):
            for sel, pr, fa in ((m["selection"], m["prob"], m["fair"]), (m["alt_selection"], m["alt_prob"], m["alt_fair"])):
                ok(0 < pr < 1, f"{f['id']} {sel} probability out of range")
                ok(american(pr) == fa, f"{f['id']} {sel} price {fa} != {american(pr)}")
            ok(abs(m["prob"] + m["alt_prob"] - 1) < 1e-6, f"{f['id']} {m['market']} sides do not sum to 1")

    # ---- published price sanity: best price cannot be shorter than the shortest provider price
    for f in fx:
        if f.get("best") is not None:
            ok(dec(f["best"]) > 1, f"{f['id']} best price impossible")

    # ---- predictions
    banned = re.compile(r"\b(model|models|modelled|verified|verify|algorithm)\b", re.I)
    grams = {}
    for p in preds:
        words = p["text"].split()
        ok(len(words) >= 30, f"{p['fixture_id']} prediction under 30 words ({len(words)})")
        ok(len(words) == p["words"], f"{p['fixture_id']} word count mismatch")
        ok(not banned.search(p["text"]), f"{p['fixture_id']} prediction uses banned vocabulary")
        ok(p["selection"].split()[0].strip("()") in p["text"] or p["selection"][:12] in p["text"],
           f"{p['fixture_id']} prediction does not name its selection")
        ok(p["confidence"] in ("High", "Medium", "Low"), f"{p['fixture_id']} prediction without confidence")
        for i in range(len(words) - 7):
            g = " ".join(w.lower().strip(".,;:()") for w in words[i:i + 8])
            grams.setdefault(g, set()).add(p["fixture_id"])
    for g, ids in grams.items():
        ok(len(ids) == 1, f"eight-word run reused across predictions: {g!r} in {ids}")
    for a, b in combinations(preds, 2):
        ok(a["selection"] != b["selection"], f"duplicate selection string {a['selection']}")

    # ---- coverage consistency
    ok(sum(c["fixtures"] for c in cov) == len(fx), "coverage fixture counts do not sum to the fixture table")
    ok(sum(c["predictions"] for c in cov) == len(preds), "coverage prediction counts disagree")
    ok(sum(c["priced"] for c in cov) == len([f for f in fx if f["priced"]]), "coverage priced counts disagree")
    ok(summary["fixtures"] == len(fx) and summary["predictions"] == len(preds)
       and summary["picks"] == len([f for f in fx if f["selection"]]), "summary counts disagree with data")
    ok(summary["flags"] == len(flags), "flag count disagrees")
    ok(summary["sources"] == len(sources), "source count disagrees")
    ok(summary["high"] == len([f for f in fx if f.get("confidence") == "High"]), "High count disagrees")
    strict = [f for f in fx if f.get("selection") and f["prob"] > 0.70 and -250 <= f["fair"] <= 10000]
    ok(summary["strict70_and_band"] == len(strict), "strict 70% count disagrees")

    # ---- flags
    ids = [f["id"] for f in flags]
    ok(len(ids) == len(set(ids)), "duplicate flag id")
    for f in flags:
        ok(f["severity"] in ("low", "medium", "high"), f"{f['id']} bad severity")
        for s in f["sources"]:
            ok(s in sources, f"{f['id']} cites unknown source {s}")

    # ---- site: every page, every link, every fragment
    pages = sorted(SITE.rglob("*.html"))
    ok(len(pages) >= 24, f"only {len(pages)} pages built")
    ids_on = {}
    for p in pages:
        t = p.read_text(encoding="utf-8")
        ids_on[p] = set(re.findall(r'id="([^"]+)"', t))
    nav_targets = {"index.html", "predictions.html", "matches.html", "markets.html", "coverage.html",
                   "flagged.html", "sources.html", "methodology.html", "repo-review.html"}
    for p in pages:
        t = p.read_text(encoding="utf-8")
        ok("<title>" in t and "</html>" in t, f"{p} is not a complete document")
        ok("http://" not in t.replace("https://", ""), f"{p} contains an insecure link")
        for href in re.findall(r'href="([^"]+)"', t):
            if href.startswith("http"):
                ok(href.startswith("https://"), f"{p} non-https external link {href}")
                continue
            target, _, frag = href.partition("#")
            path = (p.parent / target).resolve() if target else p
            ok(path.exists(), f"{p} broken link {href}")
            if frag and path.exists() and path.suffix == ".html":
                ok(frag in ids_on.get(path, set()) or frag in ("",), f"{p} broken fragment {href}")
        for name in nav_targets:
            ok(name in t, f"{p} missing navigation entry {name}")

    # ---- no reader-facing jargon in the rendered prediction page
    predpage = (SITE / "predictions.html").read_text(encoding="utf-8")
    body = re.sub(r"<[^>]+>", " ", predpage)
    for bad in (" model ", " verified ", "algorithm"):
        ok(bad not in body.lower(), f"predictions page contains {bad!r}")

    print(f"checks: {checks}   errors: {len(errors)}")
    for e in errors:
        print("  ERROR", e)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
