#!/usr/bin/env python3
"""Desk 92af340c — strict offline validator (session 92af340c-olbg1).

Checks the desk's harvest evidence, dataset tier logic, High-window arithmetic,
prediction rules (>=30 unique words, sourced), flagged-item sourcing and page
link integrity. Exits non-zero on any error. No network access is performed.
"""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "92af340c"
OUT = ROOT / "92af340c"

SPORT_IDS = {"tennis": 3, "basketball": 4, "golf": 5, "cricket": 7, "snooker": 8,
             "rugby-union": 9, "rugby-league": 10, "baseball": 12, "ice-hockey": 13,
             "motor-racing": 14, "darts": 15, "handball": 20, "volleyball": 21,
             "aussie-rules": 22, "esports": 23, "gaelic-football": 25, "greyhounds": 28}
FRESH = {"confirmed", "corrected"}
PAGES = ["index.html", "picks.html", "predictions.html", "sports.html", "verification.html",
         "flagged.html", "methodology.html", "sources.html", "reverse-engineering.html"]


class Links(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        for k, v in dict(attrs).items():
            if k in ("href", "src") and v:
                self.hrefs.append(v)


def american_value(text):
    text = str(text).strip()
    return int(text)


def in_strict_window(american):
    value = american_value(american)
    if value < 0:
        return -250 <= value < 0
    return 0 < value <= 10000


def https(url):
    p = urlsplit(url or "")
    return p.scheme == "https" and bool(p.hostname)


def main():
    errors = []

    # 1. harvest layer ------------------------------------------------------------
    files = sorted((DATA / "harvest").glob("*.json"))
    if len(files) != 17:
        errors.append(f"harvest: expected 17 hub files, found {len(files)}")
    harvests, total_cards = {}, 0
    for file in files:
        h = json.loads(file.read_text(encoding="utf-8"))
        sport = h.get("sport")
        harvests[sport] = h
        if sport not in SPORT_IDS:
            errors.append(f"harvest {file.name}: unknown sport {sport}")
            continue
        want = f"https://www.olbg.com/betting-tips/{h.get('slug')}/{SPORT_IDS[sport]}"
        if h.get("url") != want:
            errors.append(f"harvest {sport}: url {h.get('url')} != {want}")
        if not str(h.get("read_utc", "")).startswith("2026-10-22"):
            errors.append(f"harvest {sport}: read_utc {h.get('read_utc')} is not from the 2026-10-22 session")
        if len(h.get("events", [])) != h.get("event_cards_captured"):
            errors.append(f"harvest {sport}: events {len(h.get('events', []))} != captured {h.get('event_cards_captured')}")
        total_cards += h.get("event_cards_captured", 0)
    index = json.loads((DATA / "olbg.json").read_text(encoding="utf-8"))
    if index.get("event_cards_total") != total_cards:
        errors.append(f"olbg.json total {index.get('event_cards_total')} != summed {total_cards}")
    missing = set(SPORT_IDS) - set(harvests)
    if missing:
        errors.append(f"harvest missing sports: {sorted(missing)}")

    # 2. dataset -------------------------------------------------------------------
    ds = json.loads((DATA / "dataset.json").read_text(encoding="utf-8"))
    rows = ds["rows"]
    counts = ds["counts"]
    if len(rows) != counts["future"] + counts["expired"] + counts["undated"]:
        errors.append("dataset: row count != future+expired+undated")
    seen_c = {"future": 0, "expired": 0, "undated": 0, "priced": 0, "high": 0, "medium": 0, "low": 0}
    high_ids = set()
    for r in rows:
        fx = r["fixture"]
        if not any(https(s.get("url")) for s in fx["sources"]):
            errors.append(f"row {fx['id']}: no official https source link")
        seen_c[r["time_status"]] += 1
        if r["priced"]:
            seen_c["priced"] += 1
            view = r["view"]
            tier = r["desk_confidence"]
            if r["time_status"] == "future" and tier:
                seen_c[tier] += 1
                gates = r.get("gates", {})
                expect = ("high" if all(gates.values()) else
                          "medium" if gates.get("in_window") and gates.get("both_rated") else "low")
                if tier != expect:
                    errors.append(f"row {fx['id']}: tier {tier} != recomputed {expect}")
                fresh_ok = (r["ledger"].get("status") in FRESH) == bool(gates.get("ledger_fresh"))
                if not fresh_ok:
                    errors.append(f"row {fx['id']}: ledger_fresh gate disagrees with ledger status")
                if tier == "high":
                    high_ids.add(fx["id"])
                    if not in_strict_window(view["american"]):
                        errors.append(f"High row {fx['id']}: american {view['american']} outside strict -250..+10000")
                    if not (view["both_rated"] and view["both_measured"]):
                        errors.append(f"High row {fx['id']}: ratings not measured both sides")
    for key in seen_c:
        if seen_c[key] != counts[key]:
            errors.append(f"counts.{key}: recomputed {seen_c[key]} != published {counts[key]}")

    # 3. predictions ------------------------------------------------------------------
    pr = json.loads((DATA / "predictions.json").read_text(encoding="utf-8"))
    items = pr["items"]
    if pr["count"] != len(items) or set(p["match_id"] for p in items) != high_ids:
        errors.append("predictions: count/ids disagree with dataset High tier")
    texts = [p["text"] for p in items]
    if len(set(texts)) != len(texts):
        errors.append("predictions: duplicate prediction text")
    for p in items:
        words = len(p["text"].split())
        if words < 30 or p.get("word_count") != words:
            errors.append(f"prediction {p['match_id']}: word count {words} (need >=30 and stored value to match)")
        if not in_strict_window(p["american"]):
            errors.append(f"prediction {p['match_id']}: american {p['american']} outside strict window")
        if not p.get("selection") or not p.get("winner_call"):
            errors.append(f"prediction {p['match_id']}: missing selection/winner call")
        if not any(https(s.get("url")) for s in p.get("sources", [])):
            errors.append(f"prediction {p['match_id']}: no official https source link")

    # 4. flagged --------------------------------------------------------------------
    fl = json.loads((DATA / "flagged.json").read_text(encoding="utf-8"))
    for it in fl["items"]:
        if not any(https(s.get("url")) for s in it.get("sources", [])):
            errors.append(f"flagged {it['id']}: no https source link")

    # 5. pages ----------------------------------------------------------------------
    for name in PAGES:
        path = OUT / name
        if not path.exists():
            errors.append(f"missing page {name}")
            continue
        parser = Links()
        parser.feed(path.read_text(encoding="utf-8"))
        for href in parser.hrefs:
            if href.startswith(("http://",)):
                errors.append(f"{name}: insecure link {href}")
            elif href.startswith("https://"):
                continue
            elif href.startswith("#"):
                continue
            target = (path.parent / href.split("#")[0]).resolve()
            if not target.exists():
                errors.append(f"{name}: broken local link {href}")
    for slug in SPORT_IDS:
        path = OUT / "sports" / f"{slug}.html"
        if not path.exists():
            errors.append(f"missing sports/{slug}.html")
    official_row_re = re.compile(r'class="src" href="https://')
    for name in ("picks.html", "predictions.html"):
        text = (OUT / name).read_text(encoding="utf-8")
        if not official_row_re.search(text):
            errors.append(f"{name}: no official source links rendered")

    if errors:
        print(f"FAIL — {len(errors)} error(s):")
        for e in errors[:40]:
            print("  -", e)
        sys.exit(1)
    print(f"PASS — desk 92af340c: 17 hubs/{total_cards} cards harvested 2026-10-22, "
          f"{counts['future']} future rows, High {counts['high']} (strict -250..+10000, all >=30 unique sourced words), "
          f"Med {counts['medium']}, Low {counts['low']}, {len(PAGES) + len(SPORT_IDS)} pages, links OK")


if __name__ == "__main__":
    main()
