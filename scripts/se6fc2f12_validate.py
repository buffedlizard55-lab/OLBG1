"""Session e6fc2f12-olbg1 — release gate for the namespaced desk.

Fails on any of:
  * a fixture without an official source, or a source without an https URL;
  * a market pointing at a fixture that does not exist, or a duplicate market key;
  * a probability outside (0,1) or an American price inconsistent with it;
  * a High row outside the brief's rule (p > 0.70 and -250 <= price <= +10000);
  * a High row without a prediction, a prediction under 30 words, or a duplicate;
  * a prediction that does not name its own selection;
  * any internal link, asset or anchor that does not resolve;
  * render artefacts ("None", "nan", "NaN", a stray "%%");
  * a page that nothing links to;
  * counts in model.json that disagree with the data.
"""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "e6fc2f12"
SITE = ROOT / "e6fc2f12"

errors: list[str] = []
warnings: list[str] = []


def load(name: str):
    return json.loads((DATA / name).read_text())


fixtures = load("fixtures.json")
markets = load("markets.json")
sources = load("sources.json")
coverage = load("coverage.json")
model = load("model.json")
predictions = load("predictions.json")

src_ids = {s["id"] for s in sources}

# ---------------------------------------------------------------- sources
for s in sources:
    if not s["url"].startswith("https://"):
        errors.append(f"source {s['id']}: URL is not https")
    if not s.get("official"):
        errors.append(f"source {s['id']}: not marked official")
    if not s.get("read_at"):
        errors.append(f"source {s['id']}: no read timestamp")

# ---------------------------------------------------------------- fixtures
seen = set()
for f in fixtures:
    if f["id"] in seen:
        errors.append(f"duplicate fixture id {f['id']}")
    seen.add(f["id"])
    if not f["source_ids"]:
        errors.append(f"fixture {f['id']}: no source")
    for sid in f["source_ids"]:
        if sid not in src_ids:
            errors.append(f"fixture {f['id']}: unknown source {sid}")
    if f["priced"] and not f["markets_priced"]:
        errors.append(f"fixture {f['id']}: marked priced but has no markets")
    if not f["priced"] and f.get("markets_priced"):
        errors.append(f"fixture {f['id']}: unpriced but carries markets")
    if not f["priced"] and not f.get("reason"):
        errors.append(f"fixture {f['id']}: unpriced without a stated reason")
    if not (f.get("starts_at_utc") or f.get("starts_local")):
        errors.append(f"fixture {f['id']}: no start information at all")

# ---------------------------------------------------------------- markets
fx = {f["id"] for f in fixtures}
keys = set()
for m in markets:
    if m["fixture_id"] not in fx:
        errors.append(f"market on unknown fixture {m['fixture_id']}")
    key = (m["fixture_id"], m["market"], m["selection"], m["line"])
    if key in keys:
        errors.append(f"duplicate market key {key}")
    keys.add(key)
    p = m["model_probability"]
    if not (0 < p < 1):
        errors.append(f"{key}: probability {p} out of range")
        continue
    if abs(m["fair_decimal"] - 1 / p) > 1e-3:
        errors.append(f"{key}: decimal price is not 1/p")
    a = -100 * p / (1 - p) if p >= 0.5 else 100 * (1 - p) / p
    if abs(m["american"] - a) > 1.5:
        errors.append(f"{key}: American price inconsistent with probability")

    # tier rules
    if m["tier"] == "High":
        if p <= 0.70:
            errors.append(f"{key}: High but probability {p:.4f} <= 0.70")
        if not (-250 <= m["american"] <= 10000):
            errors.append(f"{key}: High but price {m['american']} outside -250..+10000")
        if not m["high_eligible"]:
            errors.append(f"{key}: High on a market marked not High-eligible")
    elif m["tier"] == "Medium":
        if p < 0.65:
            errors.append(f"{key}: Medium but probability {p:.4f} < 0.65")
        if m["high_eligible"] and p > 0.70 and -250 <= m["american"] <= 10000:
            errors.append(f"{key}: should be High ({p:.4f}) but is Medium")
    else:
        if m["high_eligible"] and p > 0.70 and -250 <= m["american"] <= 10000:
            errors.append(f"{key}: qualifies as High but is graded {m['tier']}")

# ---------------------------------------------------------------- predictions
high = [m for m in markets if m["tier"] == "High"]
if len(high) != len(predictions):
    errors.append(f"{len(high)} High rows but {len(predictions)} published predictions")
seen_text = {}
for row in predictions:
    key = (row["fixture_id"], row["selection"])
    text = row.get("prediction") or ""
    words = [w for w in re.split(r"\s+", text.strip()) if w]
    if len(words) < 30:
        errors.append(f"{key}: prediction has {len(words)} words")
    haystack = re.sub(r"[^a-z0-9. ]", " ", text.lower())
    tokens = [w for w in re.sub(r"[^a-z0-9. ]", " ", row["selection"].lower()).split()
              if len(w) > 2 and w not in {"over", "under"}]
    missing = [w for w in tokens if w not in haystack.split()]
    if missing:
        errors.append(f"{key}: prediction omits selection tokens {missing}")
    if text in seen_text:
        errors.append(f"{key}: prediction duplicates {seen_text[text]}")
    seen_text[text] = key
    if not re.match(r"^Selection:", text):
        warnings.append(f"{key}: prediction does not open with 'Selection:'")
    if row["tier"] != "High":
        errors.append(f"{key}: prediction on a non-High row")

# ---------------------------------------------------------------- counts
computed = {
    "fixtures": len(fixtures),
    "fixtures_priced": sum(1 for f in fixtures if f["priced"]),
    "fixtures_unpriced": sum(1 for f in fixtures if not f["priced"]),
    "markets": len(markets),
}
for k, v in computed.items():
    if model["counts"].get(k) != v:
        errors.append(f"model.json counts.{k}={model['counts'].get(k)} but computed {v}")
tiers = {t: sum(1 for m in markets if m["tier"] == t) for t in ("High", "Medium", "Low")}
if model["counts"].get("outcomes_by_tier") != tiers:
    errors.append("model.json tier counts disagree with the data")

# ---------------------------------------------------------------- arithmetic
ratings = load("ratings.json")
for abbr, t in ratings["nhl"].items():
    if t["w"] + t["l"] + t["otl"] != t["gp"]:
        errors.append(f"nhl {abbr}: W+L+OTL != GP")
    if not (0 < t["win_pct"] < 1):
        errors.append(f"nhl {abbr}: win_pct out of range")
for abbr, t in ratings["urc"].items():
    if t["w"] + t["d"] + t["l"] != t["p"]:
        errors.append(f"urc {abbr}: W+D+L != P")
for abbr, t in ratings["mlb"].items():
    if t["w"] + t["l"] != t["gp"]:
        errors.append(f"mlb {abbr}: W+L != GP")

# ---------------------------------------------------------------- html
class Checker(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.links: list[str] = []
        self.ids: set[str] = set()
        self.bad: list[str] = []
        self.void = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
                     "meta", "param", "source", "track", "wbr"}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        for name in ("href", "src"):
            if name in a and a[name] is not None:
                self.links.append(a[name])
        if tag not in self.void:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in self.void:
            return
        if not self.stack:
            self.bad.append(f"stray </{tag}>")
            return
        if self.stack[-1] != tag:
            if tag in self.stack:
                while self.stack and self.stack[-1] != tag:
                    self.bad.append(f"unclosed <{self.stack.pop()}> before </{tag}>")
                if self.stack:
                    self.stack.pop()
            else:
                self.bad.append(f"stray </{tag}>")
        else:
            self.stack.pop()


pages = sorted(SITE.rglob("*.html"))
all_ids: dict[str, set[str]] = {}
parsed: dict[str, Checker] = {}
for p in pages:
    raw = p.read_text(encoding="utf-8")
    for artefact in ("nan", "NaN", "%%"):
        if artefact in raw:
            errors.append(f"{p.name}: render artefact {artefact!r}")
    if re.search(r">\s*None\s*<", raw):
        errors.append(f"{p.name}: literal None rendered in the page")
    c = Checker()
    c.feed(raw)
    parsed[p] = c
    all_ids[p] = c.ids
    for b in c.bad:
        errors.append(f"{p.name}: {b}")
    if c.stack:
        errors.append(f"{p.name}: unclosed tags at EOF {c.stack}")

for p, c in parsed.items():
    for link in c.links:
        if link.startswith(("http://", "https://", "mailto:", "data:")):
            continue
        if link.startswith("#"):
            if link[1:] and link[1:] not in all_ids[p]:
                errors.append(f"{p.name}: dangling anchor {link}")
            continue
        target, _, frag = link.partition("#")
        resolved = (p.parent / target).resolve()
        if not resolved.exists():
            errors.append(f"{p.name}: broken link {link}")
            continue
        if frag:
            tgt = resolved if resolved.suffix == ".html" else resolved
            ids = all_ids.get(tgt, set())
            if ids and frag not in ids:
                errors.append(f"{p.name}: anchor {link} not found")

# reachability from index
linked: set[Path] = set()
stack = [SITE / "index.html"]
while stack:
    cur = stack.pop()
    if cur in linked or cur not in parsed:
        continue
    linked.add(cur)
    for link in parsed[cur].links:
        if link.startswith(("http", "mailto", "data:", "#")):
            continue
        t = (cur.parent / link.partition("#")[0]).resolve()
        if t.suffix == ".html" and t.exists() and t not in linked:
            stack.append(t)
for p in pages:
    if p not in linked:
        errors.append(f"{p.relative_to(SITE).as_posix()}: not reachable from index.html")

# ---------------------------------------------------------------- coverage
sports_in_scope = 17
covered = {f["sport"] for f in fixtures}
listed = {u[0] for u in coverage["unverified_sports"]}
if len(covered | listed) != sports_in_scope:
    warnings.append(f"coverage lists {len(covered | listed)} categories, expected {sports_in_scope}")

# ---------------------------------------------------------------- report
print(f"pages: {len(pages)}")
print(f"fixtures: {len(fixtures)} ({computed['fixtures_priced']} priced)")
print(f"markets: {len(markets)} · High {tiers['High']} / Medium {tiers['Medium']} / Low {tiers['Low']}")
print(f"predictions: {len(predictions)}")
print(f"sources: {len(sources)}")
for w in warnings:
    print("WARN:", w)
for e in errors:
    print("ERROR:", e)
if errors:
    print(f"\nVALIDATION FAILED — {len(errors)} error(s), {len(warnings)} warning(s)")
    sys.exit(1)
print(f"\nVALIDATION PASSED — 0 errors, {len(warnings)} warning(s)")
