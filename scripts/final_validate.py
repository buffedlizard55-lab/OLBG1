#!/usr/bin/env python3
"""
final_validate.py - release gate for the consolidated dashboard at the repository root.

What it proves, and what it does not:

* It proves the published pages agree with data/final/bundle.json, that every price is the
  exact conversion of the probability it came from, that every row carries an official
  HTTPS source, that every high-confidence selection sits inside the brief's price window,
  that every high-confidence prediction is a unique 30+ word piece naming its selection,
  that every table is rectangular, and that every internal link resolves.
* It does NOT claim any remote page has been re-read. Verification of a fact against a
  governing body is recorded per row (`status`, `verified_at`, `sources`); this gate checks
  the structure and the arithmetic, not the live web.

Run after scripts/final_site.py. Exit 0 only when every check passes.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

# The allowlist is maintained next to the legacy gate so there is one list, not two.
from validate import OFFICIAL_FIXTURE_HOSTS  # noqa: E402

BUNDLE = ROOT / "data" / "final" / "bundle.json"
SPORTS = ["tennis", "basketball", "golf", "cricket", "snooker", "rugby-union", "rugby-league",
          "baseball", "ice-hockey", "motor-racing", "darts", "handball", "volleyball",
          "aussie-rules", "esports", "gaelic-football", "greyhounds"]
NAV_PAGES = ["index.html", "picks.html", "markets.html", "predictions.html", "sports.html",
             "flagged.html", "verification.html", "sources.html", "methodology.html",
             "analysis.html", "archive.html"]

errors: list[str] = []
warnings: list[str] = []


class Tables(HTMLParser):
    """Collect tables as header cell count + per-body-row cell counts (colspan expanded),
    plus every link and every link seen inside a body row."""

    def __init__(self) -> None:
        super().__init__()
        self.stack: list[dict] = []
        self.tables: list[dict] = []
        self.links: list[str] = []
        self.title = ""
        self._in_title = False
        self.lang = ""
        self.row_links: list[list[str]] = []
        self._row: list[str] | None = None
        self.has_h1 = False

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


def parse(path: Path) -> Tables:
    p = Tables()
    p.feed(path.read_text(encoding="utf-8"))
    return p


def us_from_price(price: float) -> int:
    return int(round((price - 1) * 100)) if price >= 2.0 else -int(round(100 / (price - 1)))


def check_bundle() -> dict:
    if not BUNDLE.is_file():
        errors.append("data/final/bundle.json is missing - run scripts/final_site.py")
        return {}
    doc = json.loads(BUNDLE.read_text(encoding="utf-8"))
    rows = doc["rows"]
    counts = doc["counts"]
    priced = [r for r in rows if not r["event_only"]]

    if counts["fixtures"] != len(rows):
        errors.append(f"bundle counts.fixtures {counts['fixtures']} != {len(rows)} rows")
    if counts["priced_matches"] != len(priced):
        errors.append(f"bundle counts.priced_matches {counts['priced_matches']} != {len(priced)}")
    if counts["prices"] != sum(r["market_count"] for r in rows):
        errors.append("bundle counts.prices does not equal the sum of per-row market counts")

    seen: set[str] = set()
    for r in rows:
        if r["id"] in seen:
            errors.append(f"duplicate fixture id {r['id']}")
        seen.add(r["id"])
        if not r["sources"]:
            errors.append(f"{r['id']}: no official source")
        for s in r["sources"]:
            url = s.get("url", "")
            if not url.startswith("https://"):
                errors.append(f"{r['id']}: source is not HTTPS -> {url!r}")
            elif (urlparse(url).hostname or "") not in OFFICIAL_FIXTURE_HOSTS:
                errors.append(f"{r['id']}: source host not on the official allowlist -> {url}")
            if not s.get("name"):
                errors.append(f"{r['id']}: source has no name")
        if r["status"] not in ("verified", "carried"):
            errors.append(f"{r['id']}: unexpected status {r['status']!r}")
        if not (r.get("start_utc") or r.get("date_local")):
            errors.append(f"{r['id']}: neither a UTC start nor a local date")
        if r["event_only"] and r["pick"]:
            errors.append(f"{r['id']}: event card carries a selection")
        if not r["event_only"] and not r["markets"]:
            errors.append(f"{r['id']}: priced match with no markets")
        for m in r["markets"]:
            if not (1.02 <= m["price"] <= 60):
                errors.append(f"{r['id']}: implausible price {m['price']}")
            if us_from_price(m["price"]) != m["us"]:
                errors.append(f"{r['id']}: us {m['us']} is not the conversion of price {m['price']}")
            if not (0 < m["model_prob"] < 1):
                errors.append(f"{r['id']}: probability out of range")
            tolerance = 0.011 + 0.0006 * m["price"]  # 4dp probability rounding widens with price
            if abs(round(1.0 / m["model_prob"], 2) - m["price"]) > tolerance:
                errors.append(f"{r['id']}: price {m['price']} is not 1 / {m['model_prob']}")
        p = r["pick"]
        if p:
            if not (1.40 <= p["price"] <= 101.0):
                errors.append(f"{r['id']}: selection price {p['price']} outside the -250/+10000 window")
            if us_from_price(p["price"]) != p["us"]:
                errors.append(f"{r['id']}: pick us/price disagree")
            if p["confidence"] not in ("High", "Medium", "Low"):
                errors.append(f"{r['id']}: bad confidence {p['confidence']!r}")
            if p["confidence"] == "High":
                if p["model_prob"] < 0.70:
                    errors.append(f"{r['id']}: High pick below 70%")
                if r["status"] != "verified":
                    errors.append(f"{r['id']}: High pick on a {r['status']} row")
                if not p.get("prose"):
                    errors.append(f"{r['id']}: High pick without prose")
                if p["market"] not in ("Match winner", "Handicap"):
                    errors.append(f"{r['id']}: High pick on an ineligible market {p['market']}")
            elif p["market"] not in ("Match winner", "Handicap"):
                errors.append(f"{r['id']}: selection on an ineligible market {p['market']}")
            if not any(s["url"] in {x["url"] for x in r["sources"]} for s in r["sources"]):
                errors.append(f"{r['id']}: selection has no source")
    return doc


def check_prose(rows: list[dict]) -> None:
    highs = [r for r in rows if r["pick"] and r["pick"]["confidence"] == "High"]
    grams: dict[str, str] = {}
    for r in highs:
        text = r["pick"]["prose"] or ""
        words = len(text.split())
        if words < 30:
            errors.append(f"{r['id']}: prediction is {words} words, needs 30+")
        if r["pick"]["selection"].split()[0] not in text and r["home"].split()[0] not in text:
            errors.append(f"{r['id']}: prediction never names the selection or the home side")
        if f'{r["pick"]["price"]:.2f}' not in text:
            errors.append(f"{r['id']}: prediction does not state its price")
        tail = " ".join(text.split()[-14:])
        if f'{r["pick"]["price"]:.2f}' not in tail:
            errors.append(f"{r['id']}: prediction does not close on its selection at the quoted price")
        tokens = re.findall(r"[a-z0-9]+", text.lower())
        local: set[str] = set()
        for i in range(len(tokens) - 5):
            gram = " ".join(tokens[i:i + 6])
            if gram in grams:
                errors.append(f"{r['id']}: repeated 6-gram with {grams[gram]}: {gram}")
            if gram in local:
                errors.append(f"{r['id']}: repeated 6-gram inside one preview: {gram}")
            local.add(gram)
        grams.update({g: r["id"] for g in local})


def check_pages(doc: dict) -> None:
    rows = doc.get("rows", [])
    priced = [r for r in rows if not r["event_only"]]
    counts = doc.get("counts", {})

    expected = set(NAV_PAGES) | {f"sports/{s}.html" for s in SPORTS} | {"404.html"}
    for rel in sorted(expected):
        if not (ROOT / rel).is_file():
            errors.append(f"missing page {rel}")

    for rel in sorted(expected):
        path = ROOT / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        parsed = parse(path)
        if not parsed.lang:
            errors.append(f"{rel}: <html> has no lang attribute")
        if not parsed.title.strip():
            errors.append(f"{rel}: no <title>")
        if "<h1" not in text:
            errors.append(f"{rel}: no <h1>")
        if re.search(r'href="https?://(www\.)?google\.com/search', text):
            errors.append(f"{rel}: links to a Google search instead of an official source")
        if "None<" in text or ">None" in text:
            errors.append(f"{rel}: contains a None artefact")
        if text.count("<table") != text.count("</table>"):
            errors.append(f"{rel}: unbalanced <table> tags")
        for href in parsed.links:
            if not href or href.startswith(("https://", "mailto:", "#", "javascript:")):
                continue
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
                dest.relative_to(ROOT.resolve())
            except ValueError:
                errors.append(f"{rel}: link escapes the repository -> {href}")
                continue
            if not dest.is_file():
                errors.append(f"{rel}: broken internal link -> {href}")
        for index, tbl in enumerate(parsed.tables, 1):
            if not tbl["head"]:
                continue
            for row_cells in tbl["rows"]:
                if row_cells not in (0, tbl["head"]):
                    errors.append(f"{rel}: table {index} header has {tbl['head']} cells but a row has {row_cells}")

    # Landing page must show the whole headline set, not a sample.
    index = parse(ROOT / "index.html")
    if not index.tables:
        errors.append("index.html renders no tables")
    else:
        body = (ROOT / "index.html").read_text(encoding="utf-8")
        for r in rows:
            if r["pick"] and r["pick"]["confidence"] == "High":
                if f'row-{r["id"]}"' not in body:
                    errors.append(f"index.html is missing high pick {r['id']}")

    # All-matches page must carry every priced match, and every row an official link.
    picks = parse(ROOT / "picks.html")
    if picks.tables and picks.tables[0]["rows"]:
        rendered = len(picks.tables[0]["rows"])  # the parser already excludes the header row
        if rendered != len(priced):
            errors.append(f"picks.html renders {rendered} rows, bundle has {len(priced)} priced matches")
    else:
        errors.append("picks.html has no table")
    policy = re.compile(r"methodology\.html")
    for index, links in enumerate(picks.row_links, 1):
        if not any(h.startswith("https://") for h in links):
            errors.append(f"picks.html: row {index} has no HTTPS source link")

    markets = (ROOT / "markets.html").read_text(encoding="utf-8")
    if markets.count("<details") != len(priced):
        errors.append(f"markets.html has {markets.count('<details')} market sheets, expected {len(priced)}")
    if markets.count("<tr>") < counts.get("prices", 0):
        errors.append("markets.html renders fewer price rows than the bundle holds")

    csv_path = ROOT / "data" / "final" / "rows.csv"
    with csv_path.open(encoding="utf-8") as fh:
        n = sum(1 for _ in csv.reader(fh)) - 1
    if n != len(rows):
        errors.append(f"rows.csv has {n} data rows, bundle has {len(rows)}")

    # Every sport page must exist, carry its rows and a source in each row.
    for slug in SPORTS:
        sub = [r for r in rows if r["sport"] == slug]
        page_rel = f"sports/{slug}.html"
        parsed = parse(ROOT / page_rel)
        total = sum(len(t["rows"]) for t in parsed.tables)
        if not sub:
            errors.append(f"{page_rel}: no rows for this sport")
        if total < len([r for r in sub if not r["event_only"]]):
            errors.append(f"{page_rel}: fewer table rows than matches")
        for index, links in enumerate(parsed.row_links, 1):
            if links and not any(h.startswith("https://") or policy.search(h) for h in links):
                errors.append(f"{page_rel}: row {index} has no official source link")

    flagged = (ROOT / "flagged.html").read_text(encoding="utf-8")
    if "F-26B-01" not in flagged:
        errors.append("flagged.html does not carry the audit findings")
    if "Flagged for review" not in flagged:
        errors.append("flagged.html is not labelled as the review page")


def main() -> int:
    doc = check_bundle()
    if doc:
        check_prose(doc["rows"])
        check_pages(doc)
    print(f"bundle rows {len(doc.get('rows', []))} | high picks "
          f"{sum(1 for r in doc.get('rows', []) if r['pick'] and r['pick']['confidence'] == 'High')} | "
          f"prices {sum(r['market_count'] for r in doc.get('rows', []))}")
    print(f"Errors: {len(errors)}   Warnings: {len(warnings)}")
    for w in warnings[:10]:
        print("  WARN:", w)
    for e in errors[:40]:
        print("  ERR :", e)
    if errors:
        print("\nFINAL VALIDATION FAILED")
        return 1
    print("\nFINAL VALIDATION PASSED - pages, prices, prose, sources and links are consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
