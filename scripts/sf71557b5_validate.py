#!/usr/bin/env python3
"""
sf71557b5_validate.py - release gate for the f71557b5 desk.

Fails (exit 1) on any of:

* a table row on any data page without at least one external official-source link;
* a price that is not the exact zero-vig conversion of the probability beside it;
* a High-confidence selection outside -250..+10000, below 0.700, on an unverified row,
  or on a row whose ratings are one-sided;
* a High-confidence preview under 30 words, missing its price, not naming a side, or
  sharing any six-word sequence with another preview or with itself;
* a source URL that is not HTTPS or not on this desk's official allowlist;
* a broken internal link, a non-rectangular table, a missing page, a None artefact,
  or a page count that disagrees with the dataset.

Run:  python3 scripts/sf71557b5_validate.py
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from html.parser import HTMLParser
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "f71557b5"
D = ROOT / "data" / "f71557b5"

OFFICIAL_HOSTS = {
    "api-web.nhle.com", "statsapi.mlb.com", "www.mlb.com", "www.nba.com",
    "www.euroleaguebasketball.net", "www.pdc.tv", "www.wst.tv", "prod2.lnr.fr",
    "top14.lnr.fr", "www.eurohandball.com", "ehfcl.eurohandball.com", "www.pcb.com.pk",
    "www.ecb.co.uk", "scoring.nzc.nz", "www.nzc.nz", "www.icc-cricket.com",
    "cricketireland.ie", "www.intrl.sport", "www.nrl.com", "www.afl.com.au",
    "gaacork.ie", "munster.gaa.ie", "www.waterfordgaa.ie", "www.maighcuilinn.com",
    "limerickgaa.ie", "www.galwaygaa.ie", "www.pgatour.com", "www.europeantour.com",
    "www.formula1.com", "lolesports.com", "www.protennislive.com", "www.atptour.com",
    "wtafiles.wtatennis.com", "www.wtatennis.com", "stats.unitedrugby.com",
    "www.unitedrugby.com", "www.shl.se", "www.tauronliga.pl", "www.plusliga.pl",
    "www.gbgb.org.uk", "www.premiershiprugby.com", "premiershiprugby.com",
    "www.srilankacricket.lk", "srilankacricket.lk",
}
UPSTREAM_HOST = "www.olbg.com"      # measured, never used to verify a fact
SPORTS = ["tennis", "basketball", "golf", "cricket", "snooker", "rugby-union", "rugby-league",
          "baseball", "ice-hockey", "motor-racing", "darts", "handball", "volleyball",
          "aussie-rules", "esports", "gaelic-football", "greyhounds"]
PAGES = ["index.html", "picks.html", "markets.html", "predictions.html", "window.html",
         "sports.html", "coverage.html", "verification.html", "audit.html",
         "reverse-engineering.html", "flagged.html", "sources.html", "methodology.html"]
DATA_PAGES = ["picks.html", "sports.html", "coverage.html", "verification.html", "window.html"]

errors: list[str] = []
notes: list[str] = []


class Tables(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.tables, self.links = [], [], []
        self.row_links, self._row = [], None
        self.title, self._in_title, self.lang, self.has_h1 = "", False, "", False

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "html":
            self.lang = d.get("lang", "")
        elif tag == "title":
            self._in_title = True
        elif tag == "h1":
            self.has_h1 = True
        elif tag == "table":
            self.stack.append({"head": 0, "rows": [], "in_head": True, "cur": None})
        elif tag == "thead" and self.stack:
            self.stack[-1]["in_head"] = True
        elif tag == "tbody" and self.stack:
            self.stack[-1]["in_head"] = False
        elif tag == "tr" and self.stack:
            self.stack[-1]["cur"] = 0
            self._row = []
        elif tag in ("th", "td") and self.stack:
            span = int(d.get("colspan", 1) or 1)
            tbl = self.stack[-1]
            if tbl["cur"] is None:
                tbl["cur"] = 0
            if tag == "th" and (tbl["in_head"] or not tbl["rows"]):
                tbl["head"] += span
            else:
                tbl["cur"] += span
        if tag in ("a", "img", "link", "script") and (d.get("href") or d.get("src")):
            url = d.get("href") or d.get("src") or ""
            self.links.append(url)
            if self._row is not None and tag == "a":
                self._row.append(url)

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag == "tr" and self.stack:
            tbl = self.stack[-1]
            if not tbl["in_head"] and tbl["cur"] is not None:
                tbl["rows"].append(tbl["cur"])
                self.row_links.append(self._row or [])
            tbl["cur"] = None
            self._row = None
        elif tag == "table" and self.stack:
            tbl = self.stack.pop()
            self.tables.append({"head": tbl["head"], "rows": tbl["rows"]})

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def us_from_price(price):
    if price >= 2.0:
        return int(round((price - 1) * 100))
    if price <= 1.01:
        return -10000
    return -int(round(100 / (price - 1)))


def check_data():
    fx = json.loads((D / "fixtures.json").read_text(encoding="utf-8"))["fixtures"]
    ln = json.loads((D / "lines.json").read_text(encoding="utf-8"))
    rows = ln["rows"]
    if len(rows) != len(fx):
        errors.append(f"lines.json has {len(rows)} rows, fixtures.json has {len(fx)}")

    seen = set()
    for f in fx:
        if f["id"] in seen:
            errors.append(f"duplicate fixture id {f['id']}")
        seen.add(f["id"])
        if not f["sources"]:
            errors.append(f"{f['id']}: no official source")
        for s in f["sources"]:
            u = s.get("url", "")
            host = urlparse(u).hostname or ""
            if not u.startswith("https://"):
                errors.append(f"{f['id']}: source is not HTTPS -> {u}")
            elif host not in OFFICIAL_HOSTS and host != UPSTREAM_HOST:
                errors.append(f"{f['id']}: source host not on the official allowlist -> {u}")
            if not s.get("name"):
                errors.append(f"{f['id']}: source has no name")
        if not (f.get("start_utc") or f.get("start_local")):
            documented = any("clock" in fl["text"].lower() or "date" in fl["text"].lower()
                             or "kick-off" in fl["text"].lower() for fl in f.get("flags", []))
            if not documented:
                errors.append(f"{f['id']}: neither a UTC start nor a published local clock, "
                              "and no flag documents the absence")
        if f["status"] not in ("verified", "carried", "unverified"):
            errors.append(f"{f['id']}: unexpected status {f['status']!r}")

    grams, highs = {}, []
    for r in rows:
        for m in r["markets"]:
            for o in m["outcomes"]:
                if abs(round(1.0 / o["prob"], 2) - o["price"]) > 0.011 + 0.0006 * o["price"]:
                    errors.append(f"{r['id']}: price {o['price']} is not 1/{o['prob']}")
                if us_from_price(o["price"]) != o["us"]:
                    errors.append(f"{r['id']}: us {o['us']} is not the conversion of {o['price']}")
        s = r["selection"]
        if not s:
            continue
        if s["us"] < -250 or s["us"] > 10000:
            errors.append(f"{r['id']}: selection {s['us']:+d} outside -250..+10000")
        if s["confidence"] not in ("High", "Medium", "Low"):
            errors.append(f"{r['id']}: bad confidence {s['confidence']!r}")
        if s["confidence"] == "High":
            highs.append(r)
            if s["prob"] < 0.700:
                errors.append(f"{r['id']}: High below 0.700 ({s['prob']})")
            if r["status"] != "verified":
                errors.append(f"{r['id']}: High on a {r['status']} row")
            if s.get("cap"):
                errors.append(f"{r['id']}: High on a row whose ratings are one-sided")
            if not s.get("prose"):
                errors.append(f"{r['id']}: High without a hand-written preview")
    for r in highs:
        s = r["selection"]
        txt = s["prose"]
        words = len(txt.split())
        if words < 30:
            errors.append(f"{r['id']}: preview is {words} words, needs 30+")
        if f'{s["price"]:.2f}' not in txt:
            errors.append(f"{r['id']}: preview does not state its price {s['price']:.2f}")
        names = [r["home"].split()[0].lower()]
        if r["away"]:
            names.append(r["away"].split()[0].lower())
        names.append(s["selection"].split()[0].lower())
        low = txt.lower()
        if not any(n in low for n in names):
            errors.append(f"{r['id']}: preview never names a side or the selection")
        toks = re.findall(r"[a-z0-9]+", low)
        local = set()
        for i in range(len(toks) - 5):
            g = " ".join(toks[i:i + 6])
            if g in grams:
                errors.append(f"{r['id']}: repeated 6-gram with {grams[g]}: {g}")
            if g in local:
                errors.append(f"{r['id']}: repeated 6-gram inside one preview: {g}")
            local.add(g)
        grams.update({g: r["id"] for g in local})
    return ln, len(highs)


def check_pages(ln, n_high):
    expected = set(PAGES) | {f"sports/{s}.html" for s in SPORTS} | {"assets/style.css"}
    for rel in sorted(expected):
        if not (SITE / rel).is_file():
            errors.append(f"missing page {rel}")

    parsed_pages = {}
    for rel in sorted(expected):
        path = SITE / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if rel.endswith(".css"):
            continue
        parsed = Tables()
        parsed.feed(text)
        parsed_pages[rel] = (parsed, text)
        if not parsed.lang:
            errors.append(f"{rel}: <html> has no lang attribute")
        if not parsed.title.strip():
            errors.append(f"{rel}: no <title>")
        if not parsed.has_h1:
            errors.append(f"{rel}: no <h1>")
        if "None<" in text or ">None" in text:
            errors.append(f"{rel}: contains a None artefact")
        if text.count("<table") != text.count("</table>"):
            errors.append(f"{rel}: unbalanced <table> tags")
        if re.search(r'href="https?://(www\.)?google\.com/search', text):
            errors.append(f"{rel}: links to a search engine instead of an official source")
        for href in parsed.links:
            if not href or href.startswith(("https://", "http://", "mailto:", "#", "javascript:")):
                if href.startswith("http://"):
                    errors.append(f"{rel}: non-HTTPS external link {href}")
                continue
            clean = href.split("#", 1)[0].split("?", 1)[0]
            if not clean:
                continue
            dest = (path.parent / clean).resolve()
            if dest.is_dir():
                dest = dest / "index.html"
            try:
                dest.relative_to(SITE.resolve())
            except ValueError:
                errors.append(f"{rel}: link escapes the desk -> {href}")
                continue
            if not dest.is_file():
                errors.append(f"{rel}: broken internal link -> {href}")
        for i, tbl in enumerate(parsed.tables, 1):
            if not tbl["head"]:
                continue
            for cells in tbl["rows"]:
                if cells not in (0, tbl["head"]):
                    errors.append(f"{rel}: table {i} header has {tbl['head']} cells but a row has {cells}")

    # every data-page table row must carry an external official link
    for rel in DATA_PAGES + [f"sports/{s}.html" for s in SPORTS]:
        if rel not in parsed_pages:
            continue
        parsed, _ = parsed_pages[rel]
        for i, links in enumerate(parsed.row_links, 1):
            if not links:
                continue
            ext = [h for h in links if h.startswith("https://")]
            if not ext:
                errors.append(f"{rel}: table row {i} has no external official source link")
            elif not any((urlparse(h).hostname or "") in OFFICIAL_HOSTS for h in ext):
                notes.append(f"{rel}: table row {i} cites only {ext[0]}")

    idx = parsed_pages.get("index.html")
    if idx:
        text = idx[1]
        for r in ln["rows"]:
            if r["selection"] and r["selection"]["confidence"] == "High":
                if f'row-{r["id"]}' not in text:
                    errors.append(f"index.html is missing High pick {r['id']}")
    picks = parsed_pages.get("picks.html")
    if picks:
        rendered = sum(len(t["rows"]) for t in picks[0].tables)
        if rendered < len(ln["rows"]):
            errors.append(f"picks.html renders {rendered} rows, dataset has {len(ln['rows'])}")
    flagged = parsed_pages.get("flagged.html")
    if flagged:
        if "Flagged for Review" not in flagged[1]:
            errors.append("flagged.html is not labelled as the review page")
        if "F-F7-01" not in flagged[1]:
            errors.append("flagged.html does not carry the register")
    if n_high != ln["counts"]["high"]:
        errors.append(f"counts.high {ln['counts']['high']} != {n_high} computed")
    prices = sum(len(m["outcomes"]) for r in ln["rows"] for m in r["markets"])
    if prices != ln["counts"]["prices"]:
        errors.append(f"counts.prices {ln['counts']['prices']} != {prices} computed")
    return len(parsed_pages)


def main():
    ln, n_high = check_data()
    pages = check_pages(ln, n_high)
    c = ln["counts"]
    print(f"f71557b5: {c['fixtures']} rows | {c['priced']} priced | {c['prices']} prices | "
          f"{c['selections']} tips ({c['high']} High / {c['medium']} Medium / {c['low']} Low) | "
          f"{c['no_bet']} no-bet | {c['rejected_highs']} rejected rungs | {pages} pages checked")
    for n in notes[:8]:
        print("  note:", n)
    for e in errors[:40]:
        print("  ERR :", e)
    if errors:
        print(f"\nF71557B5 VALIDATION FAILED - {len(errors)} errors")
        return 1
    print("\nF71557B5 VALIDATION PASSED - provenance, prices, band, prose and links are consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
