#!/usr/bin/env python3
"""T5821 desk gate: independent structural + evidence checks. Exits non-zero on any failure."""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

import se58210b8_data as D

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "e58210b8"
LINES = ROOT / "data" / "e58210b8" / "lines.json"
OFFICIAL_PREFIXES = ("https://api-web.nhle.com/", "https://www.nhl.com/", "https://statsapi.mlb.com/",
                     "https://www.mlb.com/", "https://www.atptour.com/", "https://www.wst.tv/",
                     "https://www.olbg.com/")


class Rows(HTMLParser):
    """Collects <tr> rows with their cell text and hrefs."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[dict] = []
        self.cur: dict | None = None
        self.cell: list[str] | None = None
        self.hrefs: list[str] = []
        self.all_hrefs: list[str] = []
        self.headings: list[str] = []
        self._h = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "tr":
            self.cur = {"cells": [], "hrefs": []}
        elif tag == "td" and self.cur is not None:
            self.cell = []
        elif tag == "a":
            href = a.get("href", "")
            self.all_hrefs.append(href)
            if self.cur is not None:
                self.cur["hrefs"].append(href)
        elif tag in ("h1", "h2", "h3"):
            self._h = True

    def handle_endtag(self, tag):
        if tag == "tr" and self.cur is not None:
            self.rows.append(self.cur)
            self.cur = None
        elif tag == "td" and self.cell is not None:
            self.cur["cells"].append(" ".join("".join(self.cell).split()))
            self.cell = None
        elif tag in ("h1", "h2", "h3"):
            self._h = False

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)
        if self._h:
            self.headings.append(" ".join(data.split()))


def parse(path: Path) -> Rows:
    p = Rows()
    p.feed(path.read_text(encoding="utf-8"))
    return p


def check_links(path: Path, errs: list[str]) -> None:
    for href in set(parse(path).all_hrefs):
        if href.startswith(("http://", "ftp://", "//")):
            errs.append(f"{path.name}: non-HTTPS or protocol-relative link {href}")
            continue
        if href.startswith("https://"):
            continue
        if href.startswith("#"):
            continue
        if href.startswith("/"):
            errs.append(f"{path.name}: absolute link {href}")
            continue
        target = (path.parent / href.split("#")[0]).resolve()
        if target.is_dir():
            target = target / "index.html"
        if not target.is_file():
            errs.append(f"{path.name}: broken link {href}")


def check_row_links(path: Path, errs: list[str]) -> None:
    for row in parse(path).rows:
        cells = row["cells"]
        if not cells:
            continue
        if not any(h.startswith("https://") for h in row["hrefs"]):
            errs.append(f"{path.name}: row without an official HTTPS source link: {cells[:3]}")
        elif not any(any(h.startswith(p) for p in OFFICIAL_PREFIXES) for h in row["hrefs"]):
            errs.append(f"{path.name}: row link is not an official publisher: {row['hrefs']}")


def main() -> int:
    errs: list[str] = []
    pages = sorted(OUT.rglob("*.html"))
    if len(pages) != 24:
        errs.append(f"expected 24 pages, found {len(pages)}")
    for p in pages:
        check_links(p, errs)

    for slug in D.SPORT_LABEL:
        sp = OUT / "sports" / f"{slug}.html"
        if not sp.is_file():
            errs.append(f"missing sport page sports/{slug}.html")
            continue
        text = sp.read_text(encoding="utf-8")
        if D.OLBG_ROUTES[slug][0] not in text:
            errs.append(f"sports/{slug}.html missing its OLBG route")
        if "../index.html" not in text:
            errs.append(f"sports/{slug}.html has no way back to the dashboard")
    idx = (OUT / "index.html").read_text(encoding="utf-8")
    for slug in D.SPORT_LABEL:
        if f"sports/{slug}.html" not in idx:
            errs.append(f"index.html does not link sports/{slug}.html")

    for name in ("matches.html", "markets.html", "flagged.html"):
        check_row_links(OUT / name, errs)
    for slug in ("ice_hockey", "baseball"):
        check_row_links(OUT / "sports" / f"{slug}.html", errs)

    # ------------------------------------------------- modelled line integrity
    doc = json.loads(LINES.read_text(encoding="utf-8"))
    books = doc["books"]
    if len(books) != 18:
        errs.append(f"lines.json holds {len(books)} books, expected 18")
    ids = [b["id"] for b in books]
    if len(set(ids)) != len(ids):
        errs.append("duplicate fixture id in lines.json")
    for b in books:
        if b.get("unpriced"):
            if not b.get("unpriced_reason"):
                errs.append(f"{b['id']}: unpriced without a reason")
            if b.get("markets"):
                errs.append(f"{b['id']}: unpriced but carries markets")
            continue
        for m in b["markets"]:
            probs = [o["probability"] for o in m["outcomes"]]
            if abs(sum(probs) - 1.0) > 1e-9:
                errs.append(f"{b['id']} {m['market']}: probabilities sum to {sum(probs)}")
            for o in m["outcomes"]:
                want = round(1.0 / o["probability"], 3)
                if abs(want - o["fair_decimal"]) > 0.001:
                    errs.append(f"{b['id']} {m['market']} {o['selection']}: "
                                f"fair_decimal {o['fair_decimal']} != 1/p {want}")
                d = o["fair_decimal"]
                want_us = round((d - 1) * 100) if d >= 2 else -round(100 / (d - 1))
                if o["american_display"] != want_us:
                    errs.append(f"{b['id']} {m['market']} {o['selection']}: american "
                                f"{o['american_display']:+d} != {want_us:+d} from decimal {d}")
        # band flag must agree with the odds it describes
        us = b["pick_american"]
        in_window = D.WINDOW_MIN_AMERICAN <= us <= D.WINDOW_MAX_AMERICAN
        if b["pick_in_window"] != in_window:
            errs.append(f"{b['id']}: band flag {b['pick_in_window']} contradicts {us:+d}")
        if b["confidence"] == "high" and b["pick_probability"] < D.HIGH_PROBABILITY_FLOOR:
            errs.append(f"{b['id']}: labelled high at {b['pick_probability']}")
        if b["confidence"] != "high" and b["pick_probability"] >= D.HIGH_PROBABILITY_FLOOR:
            errs.append(f"{b['id']}: above the floor but labelled {b['confidence']}")

    high = [b for b in books if b["confidence"] == "high"]
    if len(high) != 4:
        errs.append(f"{len(high)} high calls, expected 4")
    outside = [b for b in high if b["pick_american"] < D.WINDOW_MIN_AMERICAN]
    if len(outside) != 4:
        errs.append(f"expected all 4 high calls shorter than -250, found {len(outside)}")
    hc = (OUT / "high-confidence.html").read_text(encoding="utf-8")
    for b in outside:
        if f"{b['pick_american']:+d}" not in hc:
            errs.append(f"high-confidence.html does not show {b['pick_american']:+d}")
    if "shorter than" not in hc:
        errs.append("high-confidence.html never discloses the out-of-window prices")

    # ------------------------------------------------------------ predictions
    preds_text = (OUT / "predictions.html").read_text(encoding="utf-8")
    blocks = re.findall(r"<div class=\"panel\"><h3>(.+?)</h3>.*?<p>(.+?)</p>", preds_text, re.S)
    if len(blocks) != 6:
        errs.append(f"predictions.html holds {len(blocks)} calls, expected 6")
    if "Anaheim Ducks to win the match" not in preds_text:
        errs.append("predictions.html omits the strongest in-window call (Anaheim at Philadelphia)")
    sixgrams: dict[tuple, str] = {}
    for title, body in blocks:
        words = re.findall(r"[A-Za-z][A-Za-z'’-]*", body)
        if len(words) < 30:
            errs.append(f"prediction '{title}' is {len(words)} words, needs 30")
        lowered = body.lower()
        for banned in ("model", "verified", "verified stats"):
            if banned in lowered:
                errs.append(f"prediction '{title}' contains the banned word '{banned}'")
        for n in range(len(words) - 5):
            gram = tuple(w.lower() for w in words[n:n + 6])
            if gram in sixgrams:
                errs.append(f"duplicate phrasing between '{sixgrams[gram]}' and '{title}'")
            sixgrams[gram] = title
        if not re.search(r"https://", body):
            pass  # source links sit in the sibling <p class="small">, checked below
    if preds_text.count("https://") < 6:
        errs.append("predictions.html does not cite its sources per call")
    if "No injury" not in preds_text and "no official availability page" not in preds_text:
        errs.append("predictions.html does not disclose the missing injury evidence")

    # --------------------------------------------------------------- freshness
    snap = datetime.strptime(D.HARVEST_UTC, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    for name in ("index.html", "matches.html", "methodology.html", "sources.html"):
        if D.HARVEST_UTC not in (OUT / name).read_text(encoding="utf-8"):
            errs.append(f"{name} does not carry the snapshot timestamp {D.HARVEST_UTC}")
    for b in books:
        start = datetime.strptime(b["start_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        if start <= snap:
            errs.append(f"{b['id']}: start {b['start_utc']} is not after the snapshot")
    if snap > datetime.now(timezone.utc):
        errs.append("snapshot timestamp is in the future")

    # ------------------------------------------------------------ flagged page
    fl = parse(OUT / "flagged.html")
    ids_found = {c for row in fl.rows for c in row["cells"] if c.startswith("F-5821-")}
    if len(ids_found) < 8:
        errs.append(f"flagged.html carries {len(ids_found)} findings, expected at least 8")
    for slug in D.COVERAGE_GAPS:
        if D.COVERAGE_GAPS[slug][:40] not in (OUT / "flagged.html").read_text(encoding="utf-8"):
            errs.append(f"flagged.html omits the {slug} gap statement")

    for e in errs:
        print("FAIL:", e)
    if errs:
        print(f"\n{len(errs)} failure(s)")
        return 1
    print(f"OK: 24 pages, {len(books)} fixture rows, {len(high)} high calls, "
          f"{len(sixgrams)} unique 6-grams, snapshot {D.HARVEST_UTC}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
