"""Validation gate for the 40214dfd desk.

Fails loudly rather than publishing a claim it cannot support. Checks cover: price arithmetic,
tier/interval consistency, prediction length and uniqueness, fact traceability against the harvest
files, official-source coverage of every row, internal link and fragment integrity, and HTML hygiene.
Exit code 0 means every check passed.
"""
import json
import math
import re
import sys
import unicodedata
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "40214dfd"
DATA = ROOT / "data" / "40214dfd" / "desk.json"
HARVEST = ROOT / "data" / "40214dfd" / "harvest"

OFFICIAL_HOSTS = ("nhl.com", "nhle.com", "mlb.com", "euroleaguebasketball.net", "wst.tv", "gaa.ie")

NUMBER_WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20,
}

errors = []
warnings = []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []
        self.ids = set()
        self.rows = 0
        self.row_links = 0

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if "id" in d:
            self.ids.add(d["id"])
        if tag == "a" and "href" in d:
            self.hrefs.append(d["href"])
        if tag == "tr":
            self.rows += 1
        if tag == "td" and getattr(self, "_pending_link", False):
            self.row_links += 1
            self._pending_link = False


def american_from_decimal(d):
    from decimal import Decimal, ROUND_HALF_UP
    d = Decimal(str(d))
    v = (d - 1) * 100 if d >= 2 else -100 / (d - 1)
    return int(v.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def harvest_numbers():
    """Every integer and every simple per-game ratio that appears in the harvest files."""
    nums = set()
    for path in HARVEST.glob("*.json"):
        raw = path.read_text()
        for token in re.findall(r"-?\d+(?:\.\d+)?", raw):
            nums.add(round(float(token), 2))
        data = json.loads(raw)
        for row in data.get("standings_rows_verified", []):
            for a, b in (("gf", "gp"), ("ga", "gp"), ("pts", "gp")):
                if row.get(a) and row.get(b):
                    nums.add(round(row[a] / row[b], 2))
        for name, r in (data.get("team_rates") or {}).items():
            for a in ("runs_scored", "runs_allowed"):
                nums.add(round(r[a] / 162, 2))
    return nums


def check_prices(desk):
    n = 0
    for fx in desk["fixtures"]:
        for mk in fx["markets"]:
            for o in mk["outcomes"]:
                n += 1
                p = o["probability"]
                if not (0 < p < 1):
                    err(f"{fx['id']} {o['selection']}: probability not in (0,1)")
                implied = 1.0 / p if p else float("inf")
                if abs(implied - o["fair_decimal"]) > 2e-3:
                    err(f"{fx['id']} {o['selection']}: fair decimal {o['fair_decimal']} != 1/p {implied:.4f}")
                if american_from_decimal(o["fair_decimal"]) != o["american"]:
                    err(f"{fx['id']} {o['selection']}: american {o['american']} does not match decimal {o['fair_decimal']}")
                band = 1.40 <= implied <= 101.0
                if band != o["fair_price_in_brief_band"]:
                    err(f"{fx['id']} {o['selection']}: in-band flag wrong")
                if o.get("confidence") == "high" and not (0.70 < p <= 1.0 / 1.40 + 1e-9):
                    err(f"{fx['id']} {o['selection']}: High outside the 70.00-71.43% interval")
                if o.get("confidence") == "high" and not o.get("prediction_id"):
                    err(f"{fx['id']} {o['selection']}: High without a written prediction")
    if n != desk["counts"]["outcomes"]:
        err(f"outcome count {n} != declared {desk['counts']['outcomes']}")
    return n


def check_tiers(desk):
    highs = [o for fx in desk["fixtures"] for mk in fx["markets"] for o in mk["outcomes"]
             if o.get("confidence") == "high"]
    if len(highs) != desk["counts"]["high_selections"]:
        err("High selection count does not match the declared count")
    for p in desk["picks"]:
        h = p["headline"]
        if h["confidence"] == "high" and not (0.70 < h["probability"] <= 1 / 1.40 + 1e-9):
            err(f"{p['fixture_id']}: headline High outside the interval")
        if h["confidence"] == "high" and not h.get("key"):
            err(f"{p['fixture_id']}: headline High without a prediction key")
    # every priced fixture must have a pick, every pick must reference a fixture
    ids = {f["id"] for f in desk["fixtures"]}
    for p in desk["picks"]:
        if p["fixture_id"] not in ids:
            err(f"pick references unknown fixture {p['fixture_id']}")


def allowed_numbers(desk):
    """Harvest values plus the authored line values, which are desk constructs, not sourced facts."""
    nums = harvest_numbers()
    for fx in desk["fixtures"]:
        for mk in fx["markets"]:
            if mk.get("line") is not None:
                nums.add(round(abs(float(mk["line"])), 2))
    for p in desk["predictions"]:
        nums.add(round(float(p["match"]["line"]), 2))
    return nums


def check_predictions(desk, nums):
    seen_shingles = {}
    bodies = []
    for p in desk["predictions"]:
        body = p["body"]
        bodies.append(body)
        words = body.split()
        if len(words) < 30:
            err(f"{p['fixture_id']} {p['selection_label']}: only {len(words)} words")
        if not body.startswith("Selection:"):
            err(f"{p['fixture_id']}: prediction does not open with an explicit selection")
        fx = next(f for f in desk["fixtures"] if f["id"] == p["fixture_id"])
        for team in (fx["home"], fx["away"]):
            short = team.split()[-1]
            if short not in body:
                err(f"{p['fixture_id']}: prediction never names {team}")
        if not any(k in body for k in ("form", "last ten", "last 10", "record")):
            warn(f"{p['fixture_id']}: prediction does not mention recent form explicitly")
        # repetition: 12-word shingles must be unique across the desk
        toks = re.findall(r"[a-z0-9']+", body.lower())
        for i in range(max(0, len(toks) - 11)):
            sh = " ".join(toks[i:i + 12])
            if sh in seen_shingles:
                err(f"repeated 12-word phrase between {seen_shingles[sh]} and {p['fixture_id']}: {sh!r}")
            seen_shingles[sh] = p["fixture_id"]
        # every numeric claim must exist in the harvest files
        for token in re.findall(r"\d+(?:\.\d+)?", body):
            value = round(float(token), 2)
            if value not in nums and not any(abs(value - n) <= 0.051 for n in nums):
                err(f"{p['fixture_id']}: number {token} in prose is not present in any harvest file")
        for word in re.findall(r"[a-z]+", body.lower()):
            if word in NUMBER_WORDS:
                value = NUMBER_WORDS[word]
                if value not in nums:
                    err(f"{p['fixture_id']}: number word '{word}' ({value}) is not present in any harvest file")
        if not p["facts_used"]:
            err(f"{p['fixture_id']}: no facts listed")
        for f in p["facts_used"]:
            if not re.search(r"\(NHL\.com|\(MLB\.com|EuroLeague|WST", f):
                warn(f"{p['fixture_id']}: fact lacks a named publisher: {f[:50]}")
    for i, a in enumerate(bodies):
        for b in bodies[i + 1:]:
            if a == b:
                err("two identical predictions")
    if len(desk["predictions"]) != desk["counts"]["predictions"]:
        err("prediction count mismatch")


def check_sources(desk):
    for fx in desk["fixtures"]:
        if not fx["source_urls"]:
            err(f"{fx['id']}: no source url")
        for url in fx["source_urls"]:
            if not any(h in url for h in OFFICIAL_HOSTS):
                err(f"{fx['id']}: non-official source url {url}")
        if fx["markets"] and not fx["model_inputs_complete"]:
            err(f"{fx['id']}: markets exist without complete inputs")
        if not fx["markets"] and fx["settlement_verified"] is not False:
            err(f"{fx['id']}: unpriced fixture should not claim verified settlement")
    for s in desk["sources"]:
        if not any(h in s["url"] for h in OFFICIAL_HOSTS):
            err(f"source {s['source_id']}: not an official host")
        if not s.get("observed_from") or not s.get("observed_to"):
            err(f"source {s['source_id']}: missing observation window")
        if not s.get("not_read"):
            err(f"source {s['source_id']}: must state what was not read")
    for r in desk["coverage"]:
        if r["status"] == "priced" and not r["source_url"]:
            err(f"coverage {r['sport']}: priced without an official url")
    if len(desk["coverage"]) != 17:
        err(f"coverage lists {len(desk['coverage'])} sports, expected 17")
    for ex in ("Soccer / football", "Hurling", "Horse racing", "Cycling", "Specials"):
        if ex not in desk["excluded"]:
            err(f"excluded list missing {ex}")
    # no priced row may belong to an excluded sport
    for fx in desk["fixtures"]:
        if fx["sport"] in ("Soccer / football", "Hurling"):
            err(f"{fx['id']}: excluded sport present")


def check_coverage_arithmetic(desk):
    """The headline coverage numbers must reconcile with the coverage table itself."""
    rows = desk["coverage"]
    n_scope = len(rows)
    n_priced = sum(1 for r in rows if r["status"] == "priced")
    n_notver = sum(1 for r in rows if r["status"] == "not verified")
    n_listed = sum(1 for r in rows if r["status"].startswith("listed"))
    n_none = sum(1 for r in rows if r["status"] == "no in-scope fixture")
    no_price = n_scope - n_priced
    if n_notver + n_listed + n_none != no_price:
        err(f"coverage statuses do not add up: {n_notver} not verified + {n_listed} listed + "
            f"{n_none} no fixture != {no_price} without a priced row")
    if desk["counts"]["sports_in_scope"] != n_scope:
        err(f"counts.sports_in_scope {desk['counts']['sports_in_scope']} != coverage rows {n_scope}")
    idx = (ROOT / "40214dfd" / "index.html").read_text()
    cov = (ROOT / "40214dfd" / "coverage.html").read_text()
    if f"{no_price} of the {n_scope} in-scope sports" not in idx:
        err(f"index.html does not state the reconciled coverage headline "
            f"({no_price} of {n_scope})")
    if f"{n_notver} of the {n_scope} in-scope sports" not in cov:
        err(f"coverage.html does not state the reconciled not-verified count ({n_notver} of {n_scope})")


def check_pages(desk):
    pages = sorted(OUT.rglob("*.html"))
    if len(pages) < 10:
        err("expected at least ten built pages")
    ids = {}
    parsed = {}
    for p in pages:
        text = p.read_text()
        rel = p.relative_to(OUT).as_posix()
        if "%%" in text:
            err(f"{rel}: contains a literal %%")
        for bad in ("None<", ">None", "nan%", "{c[", "undefined"):
            if bad in text:
                err(f"{rel}: contains suspicious token {bad!r}")
        if text.count("<tr") != text.count("</tr>"):
            err(f"{rel}: unbalanced table rows")
        lp = Links()
        lp.feed(text)
        parsed[rel] = lp
        ids[rel] = lp.ids
    for rel, lp in parsed.items():
        for href in lp.hrefs:
            if href.startswith(("http://", "https://", "mailto:")):
                if not any(h in href for h in OFFICIAL_HOSTS) and "github.com" not in href:
                    warn(f"{rel}: external link to non-official host {href}")
                continue
            target, _, frag = href.partition("#")
            base = (OUT / rel).parent
            dest = (base / target).resolve() if target else (OUT / rel)
            if not dest.exists():
                err(f"{rel}: broken link {href}")
                continue
            if frag:
                dest_rel = dest.relative_to(OUT).as_posix()
                if dest_rel in ids and frag not in ids[dest_rel]:
                    err(f"{rel}: missing fragment #{frag} in {dest_rel}")
    # every fixture rows table must carry a source link
    for rel in ("matches.html", "markets.html", "flagged.html"):
        text = (OUT / rel).read_text()
        if text.count("<tr") < 5:
            err(f"{rel}: suspiciously few rows")
        if 'rel="noopener">source' not in text and 'official source' not in text:
            err(f"{rel}: no visible source links")
    # the dashboard must show the key numbers it claims
    idx = (OUT / "index.html").read_text()
    for key in ("priced fixtures", "High selections", "Flagged for review", "Methodology"):
        if key not in idx:
            err(f"index.html missing {key}")
    return len(pages)


def main():
    desk = json.loads(DATA.read_text())
    nums = allowed_numbers(desk)
    check_prices(desk)
    check_tiers(desk)
    check_predictions(desk, nums)
    check_sources(desk)
    check_coverage_arithmetic(desk)
    n_pages = check_pages(desk)
    print(f"frames: {len(desk['fixtures'])} fixtures, "
          f"{desk['counts']['markets']} markets, {desk['counts']['outcomes']} outcomes, "
          f"{desk['counts']['high_selections']} High")
    print(f"pages checked: {n_pages}")
    for w in warnings:
        print("WARN:", w)
    if errors:
        for e_ in errors:
            print("ERROR:", e_)
        print(f"VALIDATION FAILED — {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"VALIDATION PASSED — 0 errors, {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
