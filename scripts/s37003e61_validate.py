#!/usr/bin/env python3
"""Desk 37003e61 self-checks.  Exits non-zero on any failure."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from s37003e61_data import FIXTURES, SOURCES, SPORTS
from s37003e61_engine import (BAND_CEILING, BAND_HIGH, BAND_LOW, HIGH_FLOOR,
                              american, price_book)
from s37003e61_predictions import NOT_PICKED, PREDICTIONS

DESK = ROOT / "37003e61"
BANNED = re.compile(r"\bmodel\b|\bverified\b", re.I)


def _words(t: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9'’\-]+", t)


def _grams(t: str, n: int = 7) -> set[str]:
    w = [x.lower() for x in _words(t)]
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}


def check() -> list[str]:
    bad: list[str] = []
    ids = [f["id"] for f in FIXTURES]
    if len(ids) != len(set(ids)):
        bad.append("duplicate fixture ids")
    if {f["sport"] for f in FIXTURES} - {s[0] for s in SPORTS}:
        bad.append("fixture with unknown sport")
    books = {f["id"]: price_book(f) for f in FIXTURES}

    for f in FIXTURES:
        for s in f["sources"]:
            if s not in SOURCES:
                bad.append(f"{f['id']}: unknown source {s}")
        for s in f["sources"]:
            if s in SOURCES and not SOURCES[s]["url"].startswith("https://"):
                bad.append(f"{f['id']}: non-https source {s}")
        b = books[f["id"]]
        if (f["status"] == "official" and f["profile"] in ("nhl", "nba", "ru", "rl")
                and not b["rated"] and not any("no price" in x.lower() for x in f.get("flags", []))):
            bad.append(f"{f['id']}: official row with unread inputs but no explanation")
        for m in b["markets"]:
            tot = sum(o["probability"] for o in m["outcomes"])
            if abs(tot - 1.0) > 1e-6:
                bad.append(f"{f['id']}/{m['key']}: two-way mass {tot:.9f}")
            for o in m["outcomes"]:
                if not 0.0 < o["probability"] < 1.0:
                    bad.append(f"{f['id']}/{m['key']}: probability out of range")
                if abs(o["fair_decimal"] * o["probability"] - 1.0) > 1e-3:
                    bad.append(f"{f['id']}/{m['key']}: decimal x probability != 1")
                if o["in_band"] != (BAND_LOW <= o["fair_american"] <= BAND_HIGH):
                    bad.append(f"{f['id']}/{m['key']}: in_band disagrees with american()")
        if f["profile"] == "none" and b["markets"]:
            bad.append(f"{f['id']}: priced without a profile")
        if f["status"] == "olbg_only" and b["markets"]:
            bad.append(f"{f['id']}: discovery-only row carried a price")

    high = [(f, books[f["id"]]["high"]) for f in FIXTURES if books[f["id"]].get("high")]
    for f, h in high:
        if h["probability"] <= HIGH_FLOOR:
            bad.append(f"{f['id']}: High pick at {h['probability']:.4f} <= 70%")
        if not (BAND_LOW <= h["fair_american"] <= BAND_HIGH):
            bad.append(f"{f['id']}: High price {h['fair_american']} outside band")
        if h["probability"] > BAND_CEILING + 1e-9:
            bad.append(f"{f['id']}: High pick above the band ceiling")
        if f["id"] not in PREDICTIONS:
            bad.append(f"{f['id']}: High pick without a write-up")
    if len(high) != len(PREDICTIONS):
        bad.append(f"write-up count {len(PREDICTIONS)} != High count {len(high)}")

    for fid, p in PREDICTIONS.items():
        text = p["text"]
        if len(_words(text)) < 30:
            bad.append(f"{fid}: write-up is {len(_words(text))} words")
        if BANNED.search(text):
            bad.append(f"{fid}: write-up contains an internal term")
        if not p.get("basis"):
            bad.append(f"{fid}: write-up has no sourced basis")
    grams: dict[str, str] = {}
    for fid, p in PREDICTIONS.items():
        for g in _grams(p["text"]):
            if g in grams and grams[g] != fid:
                bad.append(f"{fid}: seven-word phrase repeats {grams[g]!r}: {g!r}")
                break
            grams[g] = fid
    for fid in NOT_PICKED:
        if fid not in {f["id"] for f in FIXTURES}:
            bad.append(f"NOT_PICKED references unknown fixture {fid}")

    pages = list(DESK.glob("*.html")) + list((DESK / "sports").glob("*.html"))
    if len(pages) < 25:
        bad.append(f"only {len(pages)} pages built")
    for page in pages:
        text = page.read_text(encoding="utf-8")
        if re.search(r"^(<<<<<<<|>>>>>>>|=======)$", text, re.M):
            bad.append(f"{page.name}: conflict marker")
        for href in set(re.findall(r'href="([^"#?]+)', text)):
            if href.startswith(("http://", "https://", "mailto:", "data:")):
                continue
            if not (page.parent / href.split("#")[0]).exists():
                bad.append(f"{page.relative_to(DESK)}: broken link {href}")
        if "<title>" not in text or len(text) < 800:
            bad.append(f"{page.name}: suspiciously small page")
    for page in (ROOT / "index.html", ROOT / "picks.html"):
        text = page.read_text(encoding="utf-8")
        if 'href="37003e61/' in text:
            bad.append("root page already links the desk (peer scope)")

    for name in ("fixtures", "markets", "picks", "predictions", "sources", "flagged", "summary"):
        p = ROOT / "data" / "37003e61" / f"{name}.json"
        if not p.exists():
            bad.append(f"missing export {p.name}")
        else:
            json.loads(p.read_text())
    return bad


if __name__ == "__main__":
    problems = check()
    if problems:
        print(f"FAIL: {len(problems)} problem(s)")
        for p in problems[:40]:
            print("  -", p)
        raise SystemExit(1)
    print("OK: every desk check passed")
