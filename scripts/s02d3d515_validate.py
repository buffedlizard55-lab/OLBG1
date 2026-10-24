"""Gates for the 02d3d515 desk.

Checks, in order:
 1. provenance: every fixture, pick and withheld row cites a listed official source;
 2. arithmetic: fair decimal = 1/p and the American conversion matches;
 3. window and tier: no high pick outside -250..+10000, and no high pick without
    both sides read from an official page;
 4. prose: >=30 words, unique, no repeated 6-gram, no banned vocabulary;
 5. rendering: one h1, unique ids, every internal link and anchor resolves, and
    every table that declares a source column carries a link on every data row.
Exit code is non-zero if any check fails.
"""
import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
from s02d3d515_model import american_from_prob, in_band

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "02d3d515"
DATA = ROOT / "data" / "02d3d515"
BANNED = ("model", "verified")
OFFICIAL_HOSTS = {
    "api-web.nhle.com", "www.nhl.com", "statsapi.mlb.com", "www.mlb.com",
    "www.nba.com", "cdn.nba.com", "www.atptour.com", "www.formula1.com",
    "top14.lnr.fr", "www.pgatour.com", "gaacork.ie", "www.pcb.com.pk",
    "ehfcl.eurohandball.com", "www.wst.tv", "www.tauronliga.pl", "www.pdc.tv",
    "www.wtatennis.com", "www.olbg.com",
}
SOURCE_HEADER_HINTS = ("source", "link", "page read")


class Page(HTMLParser):
    """Collects headings, ids, links and table structure."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.ids, self.h1, self.has_title = [], [], 0, False
        self.tables, self.sourced_rows = [], []
        self._table = None
        self._row = None
        self._cell = None
        self._in_thead = False
        self._in_cell_tag = None
        self._buf = []

    # -- element handling -------------------------------------------------
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if d.get("id"):
            self.ids.append(d["id"])
        if tag == "title":
            self.has_title = True
        if tag == "h1":
            self.h1 += 1
        for key in ("href", "src"):
            if d.get(key):
                self.links.append(d[key])
        if tag == "table":
            self._table = {"headers": [], "rows": []}
            self.tables.append(self._table)
        elif tag == "thead":
            self._in_thead = True
        elif tag == "tbody":
            self._in_thead = False
        elif tag == "tr" and self._table is not None:
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = {"text": "", "links": []}
            self._in_cell_tag = tag
            self._buf = []
        elif tag == "a" and d.get("href") and self._cell is not None:
            self._cell["links"].append(d["href"])
        elif tag == "br" and self._cell is not None:
            self._buf.append(" ")

    def handle_data(self, data):
        if self._cell is not None:
            self._buf.append(data)

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._cell is not None:
            self._cell["text"] = " ".join("".join(self._buf).split())
            self._row.append(self._cell)
            self._cell, self._in_cell_tag, self._buf = None, None, []
        elif tag == "tr" and self._row is not None and self._table is not None:
            if self._in_thead:
                self._table["headers"] = [c["text"].lower() for c in self._row]
            else:
                self._table["rows"].append(self._row)
            self._row = None
        elif tag == "table" and self._table is not None:
            heads = self._table["headers"]
            idx = next((i for i, h in enumerate(heads)
                        if any(hint in h for hint in SOURCE_HEADER_HINTS)), None)
            if idx is not None:
                label = heads[idx]
                for row in self._table["rows"]:
                    if len(row) > idx:
                        self.sourced_rows.append((label, row[idx]["links"]))
            self._table = None


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def check_data():
    errors, warnings = [], []
    desk = load_json(DATA / "desk.json")
    sources = {s["id"]: s for s in desk["sources"]}
    fixtures = {f["id"]: f for f in desk["fixtures"]}
    picks = desk["picks"]
    published = [p for p in picks if p.get("confidence")]

    for sid, s in sources.items():
        if not s["url"].startswith("https://"):
            errors.append(f"source {sid}: not https")
        host = urlsplit(s["url"]).netloc
        if host not in OFFICIAL_HOSTS:
            errors.append(f"source {sid}: host {host} is not on the official list")
        if not s["observed"]:
            errors.append(f"source {sid}: no observation time")

    for f in fixtures.values():
        if f["source"] not in sources:
            errors.append(f"fixture {f['id']}: unknown source")
        if f.get("standings") and f["standings"] not in sources:
            errors.append(f"fixture {f['id']}: unknown standings source")
        if not f["start_utc"] and not f.get("start_label"):
            errors.append(f"fixture {f['id']}: no start time and no label")

    seen = set()
    for p in published:
        if p["fixture"] not in fixtures:
            errors.append(f"pick {p['selection']}: unknown fixture {p['fixture']}")
            continue
        expected = american_from_prob(p["prob"])
        if expected != p["price"]:
            errors.append(f"pick {p['selection']}: price {p['price']} != 1/p {expected}")
        if abs(p["decimal"] - round(1 / p["prob"], 3)) > 1e-9:
            errors.append(f"pick {p['selection']}: decimal is not fair")
        if not in_band(p["prob"]):
            warnings.append(f"pick {p['selection']}: {p['prob']:.1%} is outside the window "
                            f"and is published as {p['confidence']}")
            if p["confidence"] == "high":
                errors.append(f"pick {p['selection']}: high tier outside the odds window")
        words = len(p["prediction"].split())
        if words < 30:
            errors.append(f"pick {p['selection']}: prediction is only {words} words")
        low = p["prediction"].lower()
        for bad in BANNED:
            if re.search(rf"\b{bad}\w*", low):
                errors.append(f"pick {p['selection']}: banned vocabulary '{bad}'")
        if p["prediction"] in seen:
            errors.append(f"pick {p['selection']}: duplicate prediction")
        seen.add(p["prediction"])

    grams = Counter()
    for p in published:
        words = re.findall(r"[a-z0-9']+", p["prediction"].lower())
        for i in range(len(words) - 5):
            grams[" ".join(words[i:i + 6])] += 1
    repeated = [g for g, n in grams.items() if n > 1]
    if repeated:
        errors.append(f"repeated 6-grams across predictions: {repeated[:3]}")

    side_keys = {
        "ice-hockey": ("a_record", "b_record"),
        "basketball": ("a_record", "b_record"),
        "baseball": ("a_record", "b_record"),
        "tennis": ("a_semi", "b_semi"),
        "rugby-union": ("a_table", "b_table"),
        "cricket": ("a_record", "b_record"),
    }
    for p in published:
        fx = fixtures[p["fixture"]]
        keys = side_keys.get(fx["sport"])
        both = bool(keys) and all(fx["facts"].get(k) for k in keys)
        if p["confidence"] == "high" and not (both and 0.58 <= p["prob"] <= 0.7143):
            errors.append(f"pick {p['selection']}: high tier without both sides read")

    for fid, missing, why in desk["withheld"]:
        if fid not in fixtures:
            errors.append(f"withheld row {fid}: unknown fixture")
        if not missing or not why:
            errors.append(f"withheld row {fid}: missing reason")

    if not any(p["confidence"] == "high" for p in published):
        errors.append("no high-confidence pick published")
    return errors, warnings


def check_pages():
    errors = []
    pages = sorted(OUT.rglob("*.html"))
    parsed = {}
    for path in pages:
        h = Page()
        h.feed(path.read_text(encoding="utf-8"))
        parsed[path] = h
        rel = path.relative_to(OUT)
        if h.h1 != 1:
            errors.append(f"{rel}: {h.h1} h1 elements")
        if not h.has_title:
            errors.append(f"{rel}: no title")
        if len(h.ids) != len(set(h.ids)):
            errors.append(f"{rel}: duplicate ids")

    ids = {p: set(h.ids) for p, h in parsed.items()}
    for path, h in parsed.items():
        rel = path.relative_to(OUT)
        for href in h.links:
            u = urlsplit(href)
            if u.scheme in ("http", "https"):
                if u.scheme != "https":
                    errors.append(f"{rel}: insecure external link {href}")
                continue
            if u.scheme:
                errors.append(f"{rel}: bad scheme {href}")
                continue
            target = (path.parent / unquote(u.path)).resolve() if u.path else path
            try:
                target.relative_to(OUT.resolve())
            except ValueError:
                errors.append(f"{rel}: link escapes the desk {href}")
                continue
            if u.path and not target.exists():
                errors.append(f"{rel}: broken link {href}")
                continue
            if u.fragment and target.suffix == ".html" and u.fragment not in ids.get(target, set()):
                errors.append(f"{rel}: broken anchor {href}")

    required = {"index.html", "picks.html", "matches.html", "markets.html",
                "sources.html", "flagged.html", "sports.html", "predictions.html"}
    for path, h in parsed.items():
        rel = path.relative_to(OUT)
        if rel.name in required and not any(t["rows"] for t in h.tables):
            errors.append(f"{rel}: no table rows")
        for label, links in h.sourced_rows:
            if not links:
                errors.append(f"{rel}: a row in the '{label}' table carries no source link")
    if len(parsed) < 26:
        errors.append(f"only {len(parsed)} pages built")
    return errors


def main():
    data_errors, warnings = check_data()
    page_errors = check_pages()
    for w in warnings:
        print("WARN", w)
    for err in data_errors + page_errors:
        print("ERROR", err)
    pages = len(list(OUT.rglob("*.html")))
    if data_errors or page_errors:
        print(f"FAILED · {len(data_errors)} data error(s) · {len(page_errors)} page error(s)")
        return 1
    print(f"PASS · {pages} pages · data, prices and links clean · {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
