#!/usr/bin/env python3
"""Session a570c470 — release gate for the /a570c470/ desk.

Checks, in order:
  1. every internal link and in-page anchor resolves;
  2. every HTML table's row cell count matches its header (colspan aware);
  3. every fixture and prediction row carries at least one official https source;
  4. every High pick is inside -250..+10000 on its published price, and its probability >= 70%;
  5. every High pick has a prediction of >= 30 words, all unique on 6-grams;
  6. every prediction states its own selection and price;
  7. scoreboard: no duplicated fixture ids, no missing sport pages.
"""
from __future__ import annotations

import json
import re
import sys
from decimal import Decimal, InvalidOperation
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "a570c470"
DATA = ROOT / "data" / "a570c470"

errors: list[str] = []
warnings: list[str] = []


class TableCheck(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.tables = []
        self.cur = None
        self.row = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "table":
            self.stack.append(self.cur)
            self.cur = {"rows": []}
        elif tag == "tr" and self.cur is not None:
            self.row = []
            self.cur["rows"].append(self.row)
        elif tag in ("td", "th") and self.row is not None:
            try:
                cs = int(a.get("colspan", 1))
            except ValueError:
                cs = 1
            self.row.append(cs)

    def handle_endtag(self, tag):
        if tag == "tr":
            self.row = None
        elif tag == "table":
            if self.cur:
                self.tables.append(self.cur)
            self.cur = self.stack.pop() if self.stack else None


def check_tables(path: Path):
    p = TableCheck()
    p.feed(path.read_text())
    for t in p.tables:
        rows = [r for r in t["rows"] if r]
        if len(rows) < 2:
            continue
        head = sum(rows[0])
        for i, r in enumerate(rows[1:], start=2):
            if sum(r) != head:
                errors.append(f"{path.relative_to(ROOT)}: table row {i} has {sum(r)} cells, header has {head}")


LINK = re.compile(r'(?:href|src)="([^"]+)"')


def check_links(path: Path):
    txt = path.read_text()
    ids = set(re.findall(r'id="([^"]+)"', txt))
    for href in LINK.findall(txt):
        if href.startswith(("http://", "https://", "mailto:", "#", "data:")):
            if href.startswith("#") and href[1:] and href[1:] not in ids:
                errors.append(f"{path.relative_to(ROOT)}: missing anchor {href}")
            continue
        target = (path.parent / href.split("#")[0]).resolve()
        if not target.exists():
            errors.append(f"{path.relative_to(ROOT)}: broken link {href}")
        elif "#" in href and href.split("#")[1]:
            tids = set(re.findall(r'id="([^"]+)"', target.read_text()))
            if href.split("#")[1] not in tids:
                errors.append(f"{path.relative_to(ROOT)}: missing anchor {href}")


def us_of(price: float) -> int:
    d = Decimal(str(price))
    if d >= 2:
        return int(round((float(d) - 1) * 100))
    return -int(round(100 / (float(d) - 1)))


def main() -> int:
    fx = json.loads((DATA / "fixtures.json").read_text())
    lines = json.loads((DATA / "lines.json").read_text())
    preds = json.loads((DATA / "predictions.json").read_text())
    srcs = json.loads((DATA / "sources.json").read_text())
    smap = {s["source_id"]: s for s in srcs["sources"]}

    # 1-2. html
    pages = sorted(SITE.rglob("*.html"))
    for p in pages:
        check_links(p)
        check_tables(p)

    # 3. sources on every fixture
    for f in fx["fixtures"]:
        if not f["sources"]:
            errors.append(f"fixture {f['id']} has no source")
        for sid in f["sources"]:
            if sid not in smap:
                errors.append(f"fixture {f['id']} cites unknown source {sid}")
            else:
                u = urlparse(smap[sid]["url"])
                if u.scheme != "https" or not u.netloc:
                    errors.append(f"source {sid} is not an https URL")

    # 4. band + probability
    highs = [b for b in lines["books"] if b["confidence"] == "High"]
    for b in highs:
        p = b["desk_pick"]
        if not p:
            errors.append(f"{b['id']}: High without a desk pick")
            continue
        if p["model_prob"] < 0.70:
            errors.append(f"{b['id']}: High at {p['model_prob']:.3f} probability")
        if not (1.40 <= p["price"] <= 101.00):
            errors.append(f"{b['id']}: High priced {p['price']} outside 1.40-101.00")
        if us_of(p["price"]) < -250 or us_of(p["price"]) > 10000:
            errors.append(f"{b['id']}: High at {us_of(p['price'])} US, outside -250..+10000")
        if not p["in_band"]:
            errors.append(f"{b['id']}: High selection not flagged in_band")

    # 5-6. predictions
    items = preds["items"]
    if len(items) != len(highs):
        errors.append(f"{len(highs)} High picks but {len(items)} predictions")
    for it in items:
        w = len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-\.]*", it["prediction"]))
        if w < 30:
            errors.append(f"{it['id']}: prediction only {w} words")
        if f"{it['price']:.2f}" not in it["prediction"]:
            errors.append(f"{it['id']}: prediction does not quote its price")
    n = 6
    grams = {}
    for it in items:
        toks = re.findall(r"[a-z0-9]+", it["prediction"].lower())
        for i in range(max(0, len(toks) - n + 1)):
            g = " ".join(toks[i:i + n])
            grams[g] = grams.get(g, 0) + 1
    dupes = {g: c for g, c in grams.items() if c > 1}
    if dupes:
        errors.append(f"{len(dupes)} repeated 6-grams across predictions")

    # 7. scoreboard
    ids = [f["id"] for f in fx["fixtures"]]
    if len(set(ids)) != len(ids):
        errors.append("duplicate fixture ids")
    for s in lines["books"]:
        if not (SITE / "sports").exists():
            errors.append("missing sports directory")
    if len(pages) < 28:
        errors.append(f"only {len(pages)} pages built, expected 28")

    print(f"pages {len(pages)} | fixtures {len(fx['fixtures'])} | priced {len(lines['books'])} | "
          f"prices {lines['price_count']:,} | High {len(highs)} | predictions {len(items)} | sources {srcs['count']}")
    for w in warnings:
        print("  WARN:", w)
    for e in errors:
        print("  ERROR:", e)
    if errors:
        print(f"FAILED — {len(errors)} errors, {len(warnings)} warnings")
        return 1
    print(f"VALIDATION PASSED — 0 errors, {len(warnings)} warnings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
