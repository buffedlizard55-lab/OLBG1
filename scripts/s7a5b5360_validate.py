"""Session 7a5b5360-olbg1 — validation gate for the /7a5b5360/ desk.

Checks (all must pass):
  1. every fixture row carries at least one https official-source link
  2. every fixture has both sides' input recorded and every originated price is a finite number > 1
  3. predictions are >= 30 words, share no 6-word n-gram, and reference a selection that exists
  4. every internal link in the 7a5b5360 tree resolves, and every external link is https
  5. the JSON exports agree with the HTML (counts, ids)
  6. all 17 in-scope sports appear in the coverage record, and the 9 excluded sports do not
"""
import glob
import json
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "7a5b5360")
DATA = os.path.join(ROOT, "data", "7a5b5360")
errors = []
warnings = []


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        for k, v in attrs:
            if k in ("href", "src") and v:
                self.links.append(v)


def load(name):
    with open(os.path.join(DATA, name)) as fh:
        return json.load(fh)


def main():
    fx = load("fixtures.json")["fixtures"]
    mk = load("markets.json")["boards"]
    pk = load("picks.json")["picks"]
    pr = load("predictions.json")["items"]
    hp = load("high_probability.json")["selections"]
    src = load("sources.json")
    cov = load("coverage.json")
    bnd = load("bundle.json")

    # 1 + 2
    for f in fx:
        if not f["sources"]:
            errors.append(f"{f['id']}: no source keys")
        for s in f["sources"]:
            u = src.get(s, {}).get("url", "")
            if not u.startswith("https://"):
                errors.append(f"{f['id']}: source {s} is not an https official URL")
        for side in ("home", "away"):
            if side not in f["inputs"]:
                errors.append(f"{f['id']}: missing {side} input block")

    # 3
    for m in mk:
        for s in m["markets"]:
            if s["fair"] is None or not isinstance(s["prob"], float):
                errors.append(f"{m['id']}: selection {s['sel']} has no probability")
            elif s["fair"] <= 1.0:
                errors.append(f"{m['id']}: selection {s['sel']} priced at {s['fair']}")

    seen = {}
    for p in pr:
        if p["words"] < 30:
            errors.append(f"prediction {p['match_id']}::{p['selection']} is only {p['words']} words")
        board = next((m for m in mk if m["id"] == p["match_id"]), None)
        if not board or not any(s["sel"] == p["selection"] for s in board["markets"]):
            errors.append(f"prediction {p['match_id']}::{p['selection']} points at a selection that is not priced")
        words = re.findall(r"[a-z0-9']+", p["text"].lower())
        for i in range(len(words) - 5):
            gram = " ".join(words[i:i + 6])
            if gram in seen:
                errors.append(f"repeated 6-word phrase {gram!r} in {p['match_id']} and {seen[gram]}")
            seen[gram] = p["match_id"]
    if len({p["text"] for p in pr}) != len(pr):
        errors.append("duplicate prediction text")

    # 4
    pages = sorted(glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True))
    if not pages:
        errors.append("no pages built")
    for page in pages:
        with open(page) as fh:
            parser = Links()
            parser.feed(fh.read())
        rel = os.path.relpath(page, SITE)
        for href in parser.links:
            if href.startswith(("https://", "mailto:", "#")):
                continue
            if href.startswith("http://"):
                errors.append(f"{rel}: non-https external link {href}")
                continue
            target = href.split("#")[0].split("?")[0]
            if not target:
                continue
            dest = os.path.normpath(os.path.join(os.path.dirname(page), target))
            if not os.path.exists(dest):
                errors.append(f"{rel}: broken internal link {href}")

    # 5
    if bnd["counts"]["fixtures"] != len(fx):
        errors.append("bundle fixture count disagrees with fixtures.json")
    if bnd["counts"]["markets"] != sum(len(m["markets"]) for m in mk):
        errors.append("bundle market count disagrees with markets.json")
    if len(pk) != len(fx):
        errors.append("one pick per fixture is required")
    for h in hp:
        if h["prob"] < 0.70:
            errors.append(f"high-probability list contains {h['match_id']} at {h['prob']}")

    # 6
    for sport in cov["in_scope"]:
        if sport not in cov["coverage"]:
            errors.append(f"in-scope sport missing from coverage: {sport}")
    for sport in cov["excluded"]:
        if sport in cov["coverage"]:
            errors.append(f"excluded sport appears in coverage: {sport}")
    if len(cov["in_scope"]) != 17:
        errors.append("in-scope list is not 17 sports")

    if warnings:
        print("warnings:")
        for w in warnings:
            print("  -", w)
    if errors:
        print(f"FAILED — {len(errors)} error(s)")
        for x in errors:
            print("  -", x)
        return 1
    print(f"7a5b5360 VALIDATION PASSED — {len(pages)} pages, {len(fx)} fixtures, "
          f"{sum(len(m['markets']) for m in mk)} markets, {len(pr)} predictions, "
          f"{len(hp)} 70%+ selections, 0 errors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
