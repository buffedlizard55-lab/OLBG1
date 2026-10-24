"""Session f437fb14 - structural and arithmetic gate for the /f437fb14/ desk.

Fails the build on: a broken relative link or fragment, a price that does not equal 1/p,
a pick outside the brief's -250..+10000 window, a tier that breaks its own published rule,
a write-up under 30 words, two write-ups sharing a six-gram, a banned word, or JSON that has
drifted from the generator.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sf437fb14_model as M
import sf437fb14_picks as PK

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "f437fb14")
DATA = os.path.join(ROOT, "data", "f437fb14")

BANNED = ["model", "verified"]
errors = []
checks = [0]


def ok(cond, msg):
    checks[0] += 1
    if not cond:
        errors.append(msg)


def main():
    pages = []
    for dirpath, _, files in os.walk(SITE):
        for f in files:
            if f.endswith(".html"):
                pages.append(os.path.join(dirpath, f))
    ok(len(pages) == 26, f"expected 26 pages, found {len(pages)}")

    # ---- link and fragment integrity
    ids_by_file = {}
    for p in pages:
        body = open(p, encoding="utf-8").read()
        ids_by_file[os.path.normpath(p)] = set(re.findall(r'id="([^"]+)"', body))

    for p in pages:
        body = open(p, encoding="utf-8").read()
        for href in re.findall(r'href="([^"]+)"', body):
            if href.startswith(("http://", "https://", "mailto:")):
                ok(True, "")
                continue
            checks[0] += 1
            target, _, frag = href.partition("#")
            if target:
                tpath = os.path.normpath(os.path.join(os.path.dirname(p), target))
                if not os.path.exists(tpath):
                    errors.append(f"{os.path.relpath(p, SITE)}: broken link {href}")
                    continue
            else:
                tpath = os.path.normpath(p)
            if frag:
                ids = ids_by_file.get(tpath, set())
                if frag not in ids:
                    errors.append(f"{os.path.relpath(p, SITE)}: missing fragment #{frag} in {href}")

    # ---- every local asset referenced exists
    ok(os.path.exists(os.path.join(SITE, "assets", "style.css")), "stylesheet missing")

    # ---- JSON integrity + arithmetic
    picks = json.load(open(os.path.join(DATA, "picks.json"), encoding="utf-8"))
    markets = json.load(open(os.path.join(DATA, "markets.json"), encoding="utf-8"))
    fixtures = json.load(open(os.path.join(DATA, "fixtures.json"), encoding="utf-8"))
    summary = json.load(open(os.path.join(DATA, "summary.json"), encoding="utf-8"))

    ok(summary["fixtures"] == len(fixtures), "summary fixture count drifted")
    ok(summary["markets"] == len(markets), "summary market count drifted")
    ok(summary["picks"] == len(picks), "summary pick count drifted")

    for m in markets:
        ok(m["american"] == M.american(m["p"]), f"{m['fixture']} {m['label']}: price != american(p)")
        ok(m["in_band"] == M.in_band(m["american"]), f"{m['fixture']}: band flag wrong")

    for p in picks:
        ok(M.in_band(p["american"]), f"pick {p['fixture']} outside -250..+10000")
        want = M.confidence(p["p"], p["grade"], p["american"])
        ok(p["confidence"] == want, f"pick {p['fixture']}: tier {p['confidence']} != rule {want}")
        ok(p["confidence"] in ("High", "Medium", "Low"), f"pick {p['fixture']}: bad tier")

    # ---- fixtures carry provenance
    for f in fixtures:
        ok(bool(f.get("olbg_url")), f"{f['id']}: no OLBG discovery link")
        if f.get("verify") == "verified":
            ok(bool(f.get("official_url")), f"{f['id']}: verified without an official link")

    # ---- write-ups
    words_by = {}
    for p in picks:
        text = PK.PROSE.get(p["fixture"], "")
        ok(len(text.split()) >= 30, f"{p['fixture']}: write-up under 30 words")
        low = " " + text.lower() + " "
        for w in BANNED:
            ok(f" {w} " not in low, f"{p['fixture']}: banned word '{w}'")
        ok(p["selection"].split()[0].lower() in low or "selection:" in low,
           f"{p['fixture']}: write-up does not name the selection")
        words_by[p["fixture"]] = re.findall(r"[a-z0-9']+", text.lower())

    grams = {}
    for fid, ws in words_by.items():
        for i in range(len(ws) - 5):
            g = " ".join(ws[i:i + 6])
            grams.setdefault(g, []).append(fid)
    dupes = {g: v for g, v in grams.items() if len(set(v)) > 1}
    ok(not dupes, f"repeated six-grams across write-ups: {list(dupes)[:3]}")

    # ---- selection labels must be readable, not bare over/under
    body = open(os.path.join(SITE, "picks.html"), encoding="utf-8").read()
    ok(">over<" not in body.lower() and ">under<" not in body.lower(),
       "a bare over/under leaked into picks.html")

    print(f"pages={len(pages)} checks={checks[0]} errors={len(errors)}")
    for err in errors[:40]:
        print("  ERROR:", err)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
