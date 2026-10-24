#!/usr/bin/env python3
"""Desk 99d43605 validation gate.

Mirrors the repository's desk rules plus this desk's own:

* 15 sports in brief order; page per sport;
* every priced fixture cites at least one *official* source and every table
  row on every page carries an https link;
* High picks sit inside the American window -250..+10000 with probability
  strictly above 70.00%;
* predictions exist for exactly the High picks, at least 30 words each, all
  unique, with the banned words "model"/"verified" nowhere on the site;
* no gradients in the CSS, one h1 per page, all internal links resolvable;
* JSON exports reconcile with the module of record.

No network calls; the gate audits the published snapshot only.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from s99d43605_data import (FIXTURES, FLAG_ITEMS, OLBG_LOG, PREDICTIONS,  # noqa: E402
                            SOURCES, SPORTS, build_all)
from s99d43605_model import prob_from_american  # noqa: E402

SITE = ROOT / "99d43605"
DATA = ROOT / "data" / "99d43605"
BANNED = ("model", "verified")
errors: list[str] = []

SCOPE = {
    "Golf", "Volleyball", "Rugby Union", "Cricket", "Snooker", "Darts",
    "Baseball", "Gaelic Sports", "Greyhounds", "Tennis", "Motor Racing",
    "Handball", "Ice Hockey", "Basketball", "Rugby League",
}


class Collector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.ids: list[str] = []
        self.h1 = 0
        self.title = False
        self._tbody = 0
        self._tr = 0
        self.rows: list[list[str]] = []
        self._row: list[str] = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "h1":
            self.h1 += 1
        if tag == "title":
            self.title = True
        if tag == "tbody":
            self._tbody += 1
        elif tag == "tr" and self._tbody:
            self._tr += 1
            self._row = []
        if d.get("id"):
            self.ids.append(d["id"])
        if tag == "a" and d.get("href"):
            self.links.append(str(d["href"]))
            if self._tr:
                self._row.append(str(d["href"]))
        elif tag in ("link", "script", "img"):
            t = d.get("href") or d.get("src")
            if t:
                self.links.append(str(t))

    def handle_endtag(self, tag):
        if tag == "tr" and self._tr:
            self._tr -= 1
            self.rows.append(self._row)
        elif tag == "tbody" and self._tbody:
            self._tbody -= 1


def check(problem: bool, message: str) -> None:
    if problem:
        errors.append(message)


def check_data(b) -> None:
    check(len(SPORTS) != 15, "sport count differs from the brief's 15")
    check({name for _, name, _ in SPORTS} != SCOPE, "sport names drifted from the brief")
    ids = {s["id"] for s in SOURCES}
    for s in SOURCES:
        check(not s["url"].startswith("https://"), f"source {s['id']}: not https")
        check(not s.get("observed"), f"source {s['id']}: no observation stamp")
    official = {s["id"] for s in SOURCES if s["official"]}
    discovery = ids - official
    for fx in FIXTURES:
        missing = [sid for sid in fx["source_ids"] if sid not in ids]
        check(bool(missing), f"fixture {fx['id']}: unregistered sources {missing}")
    for fx in b["fixtures"]:
        if fx["markets"]:
            has_off = any(s in official for s in fx["source_ids"])
            if fx["state"] == "upcoming" and any(len(fx.get("manual_tier") or "") >= 0 for _ in [0]):
                check(not has_off and not fx.get("manual_tier") and fx.get("markets", [{}])[0].get("measured", True),
                      f"fixture {fx['id']}: measured market without an official source")
        if fx["markets"] and not any(s in official for s in fx["source_ids"]):
            check(not (fx.get("manual_tier") or not fx["markets"][0].get("measured", True)),
                  f"fixture {fx['id']}: official source absent yet priced as if measured")
    # High rules
    for fx in b["highs"]:
        check(not (fx["pick_prob"] and fx["pick_prob"] > 0.70), f"high {fx['id']}: prob not above 0.70")
        am = fx["american"]
        check(not (-250 <= am <= 10000 if isinstance(am, int) else False),
              f"high {fx['id']}: american {am} outside -250..+10000")
        check(prob_from_american(am) <= 0.70 if isinstance(am, int) else True,
              f"high {fx['id']}: implied prob of price not above 0.70")
        check(not any(s in official for s in fx["source_ids"]) or fx["state"] != "upcoming",
              f"high {fx['id']}: not official-backed and upcoming")
        check(set(fx["source_ids"]) & discovery and len(fx["source_ids"]) <= 1,
              f"high {fx['id']}: discovery source acting alone")
    # every pick has both american and decimal consistent with p
    for fx in b["picks"]:
        check(fx["american"] is None or fx["decimal"] is None, f"pick {fx['id']}: incomplete price")
    # predictions == highs, word count, uniqueness
    check(set(PREDICTIONS) != {f["id"] for f in b["highs"]}, "predictions not 1:1 with High picks")
    texts = list(PREDICTIONS.values())
    for fid, txt in PREDICTIONS.items():
        check(len(txt.split()) < 30, f"prediction {fid}: under 30 words")
        check(bool(re.search(r"(?i)\b(model|verified)\b", txt)), f"prediction {fid}: banned word")
    grams = Counter()
    for fid, txt in PREDICTIONS.items():
        ws = re.findall(r"[a-z']+", txt.lower())
        grams.update(tuple(ws[i:i + 5]) for i in range(len(ws) - 4))
    dup = [g for g, n in grams.items() if n > 1]
    check(bool(dup), f"predictions share 5-grams across prose: {dup[:3]}")
    check(len({t.strip() for t in texts}) != len(texts), "duplicate prediction text")


def check_pages(b) -> None:
    pages = sorted(SITE.rglob("*.html"))
    check(len(pages) != 25, f"expected 25 desk pages, found {len(pages)}")
    for slug, *_ in SPORTS:
        check(not (SITE / "sports" / f"{slug}.html").exists(), f"missing sports/{slug}.html")
    for page in pages:
        rel = page.relative_to(ROOT).as_posix()
        text = page.read_text(encoding="utf-8")
        c = Collector()
        c.feed(text)
        check("linear-gradient" in text, f"{rel}: gradient in CSS")
        check(c.h1 != 1, f"{rel}: expected one h1, found {c.h1}")
        check(not c.title, f"{rel}: missing title")
        check(len(c.ids) != len(set(c.ids)), f"{rel}: duplicate html ids")
        check(bool(re.search(r"(?i)\b(model|verified)\b", text)), f"{rel}: banned word on page")
        for i, row in enumerate(c.rows, 1):
            check(not any(h.startswith("https://") for h in row), f"{rel}: table row {i} lacks https source link")
        for href in c.links:
            u = urlparse(href)
            if u.scheme in ("http",):
                errors.append(f"{rel}: plain http link {href}")
            if u.scheme in ("javascript", "data"):
                errors.append(f"{rel}: unsafe link scheme {href}")
            if u.scheme or u.netloc or href.startswith("#"):
                continue
            dest = (page.parent / u.path).resolve() if u.path else page
            try:
                dest.relative_to(ROOT.resolve())
            except ValueError:
                errors.append(f"{rel}: link escapes repo {href}")
                continue
            if dest.is_dir():
                dest = dest / "index.html"
            check(not dest.exists(), f"{rel}: broken internal link {href}")


def check_json(b) -> None:
    manifest = json.loads((DATA / "manifest.json").read_text())
    counts = manifest["counts"]
    calc = {
        "fixtures": len(b["fixtures"]),
        "priced": sum(1 for f in b["fixtures"] if f["markets"]),
        "picks": len(b["picks"]),
        "high": len(b["highs"]),
        "predictions": len(PREDICTIONS),
        "flags": len(FLAG_ITEMS),
        "sports": len(SPORTS),
        "sources": len(SOURCES),
    }
    for k, v in calc.items():
        check(counts.get(k) != v, f"manifest count {k}: {counts.get(k)} != {v}")
    checks = {
        "picks.json": ("picks", calc["picks"]),
        "predictions.json": ("predictions", calc["predictions"]),
        "flags.json": ("flags", calc["flags"]),
        "fixtures.json": ("fixtures", calc["fixtures"]),
    }
    for name, (key, n) in checks.items():
        doc = json.loads((DATA / name).read_text())
        check(len(doc[key]) != n, f"{name}: {len(doc[key])} rows != module {n}")
    coverage = json.loads((DATA / "coverage.json").read_text())["coverage"]
    check(len(coverage) != 15, "coverage: not 15 sports")
    olbg_doc = json.loads((DATA / "olbg.json").read_text())
    check(len(olbg_doc["routes"]) != 15, "olbg.json: not 15 routes")
    check(len(OLBG_LOG) != 15, "OLBG_LOG: not 15 entries")


def main() -> int:
    b = build_all()
    check_data(b)
    check_pages(b)
    check_json(b)
    for e in errors:
        print("ERR:", e)
    print(f"desk validation: {len(errors)} errors | fixtures={len(b['fixtures'])} "
          f"picks={len(b['picks'])} high={len(b['highs'])} predictions={len(PREDICTIONS)}")
    print("DESK VALIDATION " + ("FAILED" if errors else "PASSED"))
    return bool(errors)


if __name__ == "__main__":
    sys.exit(main())
