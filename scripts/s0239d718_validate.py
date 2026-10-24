#!/usr/bin/env python3
"""Release gates for the namespaced 0239d718 OLBG clarity desk."""
from __future__ import annotations

import json
import math
import re
import sys
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "0239d718"
SITE = ROOT / "0239d718"
DISCOVERY_HOSTS = {"www.olbg.com", "olbg.com"}
BANNED_IN_PROSE = ("model", "models", "verified", "verification", "algorithm",
                   "machine learning", "ai-driven", "backtested")


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def american(p):
    if p <= 0 or p >= 1:
        raise ValueError(p)
    return -round(100 * p / (1 - p)) if p >= 0.5 else round(100 * (1 - p) / p)


def words(text):
    return re.findall(r"\b[\w'-]+\b", text.lower())


def ngrams(text, n=25):
    toks = words(text)
    return {" ".join(toks[i:i+n]) for i in range(len(toks)-n+1)}


def host(url):
    return urlsplit(url).hostname or ""


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.ids = []
        self.rows = []
        self.row = None
        self.has_td = False
        self.h1 = 0
        self.title = False
        self.body = {}

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "body":
            self.body = d
        if tag == "h1":
            self.h1 += 1
        if tag == "title":
            self.title = True
        if d.get("id"):
            self.ids.append(d["id"])
        for key in ("href", "src"):
            if d.get(key):
                self.links.append(d[key])
        if tag == "tr":
            self.row = []
            self.has_td = False
        if tag == "td":
            self.has_td = True
        if tag == "a" and self.row is not None and d.get("href"):
            self.row.append(d["href"])

    def handle_endtag(self, tag):
        if tag == "tr" and self.row is not None:
            if self.has_td:
                self.rows.append(self.row)
            self.row = None


def validate():
    errors = []

    def check(test, message):
        if not test:
            errors.append(message)

    desk = load(DATA / "desk.json")
    sources_doc = load(DATA / "sources.json")
    discovery_doc = load(DATA / "olbg_discovery.json")
    flags_doc = load(DATA / "flags.json")
    audit_doc = load(DATA / "audit.json")
    lines_doc = load(DATA / "lines.json")

    sources = {s["id"]: s for s in sources_doc["sources"]}
    check(len(sources) == len(sources_doc["sources"]), "duplicate source id")
    official_hosts = set()
    discovery_hosts = set(DISCOVERY_HOSTS)
    for sid, src in sources.items():
        check(src["url"].startswith("https://"), sid + ": source URL is not https")
        h = host(src["url"])
        if src["role"] == "official":
            official_hosts.add(h)
            check(h not in DISCOVERY_HOSTS, sid + ": discovery host marked official")
            check(bool(src.get("observed_at")), sid + ": no observation timestamp")
            check(bool(src.get("supports")), sid + ": no stated use")
        else:
            discovery_hosts.add(h)
            check(h in DISCOVERY_HOSTS, sid + ": unexpected discovery host")

    # Counts and coverage.
    sports = desk["sports"]
    picks = desk["picks"]
    matches = desk["matches"]
    lines = desk["lines"]
    flags = desk["flags"]
    check(len(sports) == 15, "desk must cover exactly 15 sports")
    check(len({s["slug"] for s in sports}) == 15, "duplicate sport slug")
    by_sport = {}
    for p in picks:
        by_sport.setdefault(p["sport"], []).append(p)
    for s in sports:
        check(len(by_sport.get(s["slug"], [])) == 5,
              s["slug"] + ": expected five picks, found " + str(len(by_sport.get(s["slug"], []))))
    check(len(matches) == 57, "unexpected match count")
    check(len(lines) == 4 * len(matches), "each match must carry four originated lines")
    check(len(picks) == 75, "unexpected pick count")
    counts = {
        "sports": len(sports), "matches": len(matches), "picks": len(picks),
        "high": sum(p["confidence"] == "high" for p in picks),
        "medium": sum(p["confidence"] == "medium" for p in picks),
        "low": sum(p["confidence"] == "low" for p in picks),
        "lines": len(lines),
        "sources": sum(s["role"] == "official" for s in sources.values()),
        "discovery_sources": sum(s["role"] == "discovery" for s in sources.values()),
        "flags": len(flags), "audit_findings": len(audit_doc["findings"]),
        "predictions": len(picks),
    }
    check(desk["counts"] == counts, "desk counts do not reconcile: " + json.dumps(counts))
    check(desk["strict_high_gate"] == {"min_probability": 0.70, "min_american": -250, "max_american": 10000},
          "strict high gate changed")

    # Source references and event times.
    match_ids = {m["id"] for m in matches}
    check(len(match_ids) == len(matches), "duplicate match id")
    gate = desk["strict_high_gate"]
    snapshot = datetime.fromisoformat(desk["generated_at"].replace("Z", "+00:00"))
    for m in matches:
        check(bool(m["source_ids"]), m["id"] + ": no source ids")
        check(any(sources[s]["role"] == "official" for s in m["source_ids"]),
              m["id"] + ": no official source")
        for sid in m["source_ids"]:
            check(sid in sources, m["id"] + ": unknown source " + sid)
        check(host(m["discovery_url"]) in discovery_hosts,
              m["id"] + ": discovery URL is not OLBG")
        if m["start_utc"]:
            start = datetime.fromisoformat(m["start_utc"].replace("Z", "+00:00"))
            check(start >= snapshot, m["id"] + ": exact start is before the snapshot")
        check(bool(m["source_ids"]), m["id"] + ": missing source links")

    # Originated line arithmetic.
    line_ids = [ln["id"] for ln in lines]
    check(len(line_ids) == len(set(line_ids)), "duplicate line id")
    per_match = {}
    for ln in lines:
        per_match.setdefault(ln["match_id"], 0)
        per_match[ln["match_id"]] += 1
        check(ln["match_id"] in match_ids, ln["id"] + ": unknown match")
        check(any(sources[s]["role"] == "official" for s in ln["source_ids"]),
              ln["id"] + ": no official source")
        p = ln["probability"]
        check(0 < p < 1, ln["id"] + ": invalid probability")
        check(ln["fair_american"] == american(p), ln["id"] + ": price does not follow probability")
        check(ln["in_band"] == (-250 <= ln["fair_american"] <= 10000),
              ln["id"] + ": price-band flag mismatch")
    for mid in match_ids:
        check(per_match.get(mid) == 4, mid + ": must have four originated lines")

    # Picks, predictions and the strict gate.
    seen_text = set()
    seen_grams = {}
    pick_ids = [p["id"] for p in picks]
    check(len(pick_ids) == len(set(pick_ids)), "duplicate pick id")
    for p in picks:
        check(p["match_id"] in match_ids, p["id"] + ": unknown match")
        check(any(sources[s]["role"] == "official" for s in p["source_ids"]),
              p["id"] + ": no official source")
        check(host(p["discovery_url"]) in discovery_hosts,
              p["id"] + ": discovery URL is not OLBG")
        pr = p["probability"]
        price = p["fair_american"]
        check(0 < pr < 1, p["id"] + ": invalid probability")
        check(price == american(pr), p["id"] + ": price does not follow probability")
        expected = "high" if pr > 0.70 and -250 <= price <= 10000 else ("medium" if pr >= 0.62 else "low")
        check(p["confidence"] == expected, p["id"] + ": confidence tier mismatch")
        if p["confidence"] == "high":
            check(pr > gate["min_probability"], p["id"] + ": high pick not above 70%")
            check(gate["min_american"] <= price <= gate["max_american"],
                  p["id"] + ": high pick outside price band")
        text = p["prediction"].strip()
        check(text, p["id"] + ": empty prediction")
        check(text not in seen_text, p["id"] + ": duplicate prediction text")
        seen_text.add(text)
        w = words(text)
        check(len(w) >= 30, p["id"] + ": prediction shorter than 30 words")
        low = text.lower()
        check(p["selection"].lower() in low,
              p["id"] + ": prediction does not name the exact selection")
        for banned in BANNED_IN_PROSE:
            check(banned not in low, p["id"] + ": banned internal word '" + banned + "'")
        for gram in ngrams(text, 25):
            seen_grams.setdefault(gram, set()).add(p["id"])
    repeated = [g for g, ids in seen_grams.items() if len(ids) > 1]
    check(not repeated, "predictions share a 25-word passage: " + "; ".join(repeated[:3]))

    # Review queue and audit rows all need official recheck links.
    check(flags_doc["flags"] == flags, "flags data mismatch")
    for f in flags:
        check(any(sources[s]["role"] == "official" for s in f["official_source_ids"]),
              f["id"] + ": flagged row has no official recheck")
        check(f["official_url"] if "official_url" in f else True, f["id"] + ": bad official URL field")
    for i, f in enumerate(audit_doc["findings"], 1):
        check(any(sources[s]["role"] == "official" for s in f["official_source_ids"]),
              "audit finding " + str(i) + ": no official recheck")
        check(bool(f["repo_url"]), "audit finding " + str(i) + ": no repo line link")
    check(audit_doc["files_scanned"] > 0 and audit_doc["lines_scanned"] > 0,
          "repo audit did not scan any files")

    # Discovery ledger.
    check(len(discovery_doc["sports"]) == 15, "discovery ledger must list 15 sports")
    check(len(discovery_doc["quirks"]) >= 8, "discovery ledger missing platform quirks")
    for q in discovery_doc["quirks"]:
        check(len(q) == 5, "each discovery quirk needs discovery and official source ids")
        check(sources[q[3]]["role"] == "discovery", "quirk discovery source is not discovery")
        check(sources[q[4]]["role"] == "official", "quirk recheck source is not official")

    # Static site: one h1, snapshot marker, unique ids, source links on rows,
    # and all internal links/fragments resolve.
    pages = {}
    for path in sorted(SITE.rglob("*.html")):
        parser = Page()
        parser.feed(path.read_text(encoding="utf-8"))
        rel = path.relative_to(SITE).as_posix()
        pages[rel] = parser
        check(parser.h1 == 1, rel + ": must have exactly one h1")
        check(parser.title, rel + ": missing title")
        check(parser.body.get("data-snapshot") == desk["generated_at"],
              rel + ": snapshot marker mismatch")
        check(len(parser.ids) == len(set(parser.ids)), rel + ": duplicate HTML ids")
        for index, links in enumerate(parser.rows, 1):
            ok = any(host(u) in official_hosts for u in links if u.startswith("https://"))
            check(ok, f"{rel}: table row {index} has no official source link")
    check(len(pages) >= 25, "expected the full namespaced site to be generated")

    for rel, parser in pages.items():
        path = SITE / rel
        for link in parser.links:
            parts = urlsplit(link)
            if parts.scheme or parts.netloc:
                check(parts.scheme not in ("javascript", "data", "mailto"),
                      rel + ": unsafe external link " + link)
                continue
            target = (path.parent / unquote(parts.path)).resolve() if parts.path else path.resolve()
            try:
                target.relative_to(SITE.resolve())
            except ValueError:
                errors.append(rel + ": link escapes the namespaced site: " + link)
                continue
            if target.is_dir():
                target = target / "index.html"
            check(target.is_file(), rel + ": broken internal link " + link)
            if parts.fragment and target.suffix == ".html" and target.is_file():
                target_rel = target.relative_to(SITE).as_posix()
                target_parser = pages.get(target_rel)
                if target_parser is None:
                    target_parser = Page()
                    target_parser.feed(target.read_text(encoding="utf-8"))
                    pages[target_rel] = target_parser
                check(unquote(parts.fragment) in target_parser.ids,
                      rel + ": missing fragment " + link)

    return errors


def main():
    errors = validate()
    for err in errors:
        print("ERROR:", err)
    print(f"0239d718 desk validation: {len(errors)} errors.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
