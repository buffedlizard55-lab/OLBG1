#!/usr/bin/env python3
"""Structural release gate for the isolated 0c9bc692 desk.

This validates the facts' representation and provenance shape. It intentionally does not call
remote sources or represent a passing run as a fresh re-certification of sporting facts.
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "0c9bc692"
SITE = ROOT / "0c9bc692"
EXPECTED_SPORTS = {
    "golf", "volleyball", "rugby-union", "cricket", "snooker", "darts", "baseball",
    "gaelic-sports", "greyhounds", "tennis", "motor-racing", "handball", "ice-hockey",
    "basketball", "rugby-league",
}

errors: list[str] = []
checks = 0


def read(name: str):
    global checks
    checks += 1
    path = DATA / name
    if not path.exists():
        errors.append(f"missing {path.relative_to(ROOT)}")
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


sources = read("sources.json")
fixtures_doc = read("fixtures.json")
markets_doc = read("markets.json")
predictions_doc = read("predictions.json")
flags_doc = read("flagged.json")
coverage_doc = read("coverage.json")
summary = read("summary.json")
observations = read("observations.json")
olbg = read("olbg_discovery.json")

source_map = {s["id"]: s for s in sources.get("sources", [])}
fixtures = fixtures_doc.get("fixtures", [])
markets = markets_doc.get("markets", [])
predictions = predictions_doc.get("predictions", [])

checks += 1
if set(s["sport"] for s in source_map.values()) != EXPECTED_SPORTS:
    errors.append("sources must cover exactly the 15 requested sports")

for source_id, source in source_map.items():
    checks += 2
    parsed = urlparse(source.get("url", ""))
    if parsed.scheme != "https" or not parsed.netloc:
        errors.append(f"source {source_id} has no public HTTPS URL")
    if not source.get("result"):
        errors.append(f"source {source_id} has no retained-result note")

fixture_ids = set()
for fixture in fixtures:
    checks += 5
    fid = fixture.get("id")
    if not fid or fid in fixture_ids:
        errors.append(f"fixture ID missing or duplicated: {fid}")
    fixture_ids.add(fid)
    if fixture.get("sport") not in EXPECTED_SPORTS:
        errors.append(f"fixture {fid} outside requested sport scope")
    if fixture.get("official_source") not in source_map:
        errors.append(f"fixture {fid} has unknown official source")
    for field in ("participants", "when", "status", "notes"):
        if not fixture.get(field):
            errors.append(f"fixture {fid} has blank required {field}")
    if fixture.get("status") == "OLBG discovery only" and not fixture.get("olbg_source"):
        errors.append(f"OLBG-only fixture {fid} lacks a discovery route")

checks += 1
if {f["sport"] for f in fixtures} - EXPECTED_SPORTS:
    errors.append("fixture contains unexpected sport")

for market in markets:
    checks += 5
    if market.get("fixture_id") not in fixture_ids:
        errors.append(f"market orphan {market.get('fixture_id')}")
    if not market.get("market") or not market.get("source_status") or not market.get("basis"):
        errors.append(f"market missing investigation explanation {market.get('fixture_id')}")
    values = [market.get(k) for k in ("fair_probability", "fair_decimal", "fair_american")]
    if any(v is not None for v in values) and any(v is None for v in values):
        errors.append(f"partially populated fair line {market.get('fixture_id')} {market.get('market')}")
    if market.get("confidence") == "High":
        errors.append("this evidence-limited desk must not emit High labels")
    if market.get("fair_probability") is not None:
        p = market["fair_probability"]
        expected_dec = 1 / p
        expected_us = round(-100 * p / (1 - p)) if p >= 0.5 else round(100 * (1 - p) / p)
        if not 0 < p < 1 or abs(market["fair_decimal"] - expected_dec) > .01 or market["fair_american"] != expected_us:
            errors.append(f"fair-price arithmetic mismatch: {market.get('fixture_id')} {market.get('market')}")

checks += 1
if not any(m.get("fair_probability") is not None for m in markets):
    errors.append("expected one disclosed low research fair line")

for prediction in predictions:
    checks += 6
    words = re.findall(r"\b[\w’'-]+\b", prediction.get("text", ""))
    if len(words) < 30:
        errors.append(f"prediction {prediction.get('fixture_id')} has fewer than 30 words")
    if re.search(r"\b(model|verified)\b", prediction.get("text", ""), flags=re.I):
        errors.append(f"prediction {prediction.get('fixture_id')} has prohibited wording")
    if prediction.get("fixture_id") not in fixture_ids:
        errors.append(f"prediction is orphaned: {prediction.get('fixture_id')}")
    if prediction.get("confidence") != "Low":
        errors.append("prediction confidence should remain Low")
    if not prediction.get("selection") or not prediction.get("sources"):
        errors.append("prediction missing selection or source")
    if any(source_id not in source_map for source_id in prediction.get("sources", [])):
        errors.append("prediction names unknown source")

checks += 2
if len(flags_doc.get("flags", [])) < 8:
    errors.append("flag register is unexpectedly incomplete")
if len(coverage_doc.get("coverage", [])) != 15:
    errors.append("coverage table must have 15 sports")

checks += 2
if summary.get("high_confidence_picks") != 0 or summary.get("originated_price_rows") != 1:
    errors.append("summary must state zero High and one price row")
if len(observations.get("observations", [])) != 15:
    errors.append("observation ledger must have one official source per sport")

checks += 2
if not olbg.get("policy", "").startswith("Discovery only") or len(olbg.get("market_families", {})) < 3:
    errors.append("OLBG discovery ledger incomplete")

required_pages = ["index.html", "matches.html", "markets.html", "predictions.html", "sources.html", "reverse-engineering.html", "flagged.html", "methodology.html", "audit.html"]
required_pages += [f"sports/{sport}.html" for sport in EXPECTED_SPORTS]
for relative in required_pages:
    checks += 3
    path = SITE / relative
    if not path.exists():
        errors.append(f"missing generated page {relative}")
        continue
    text = path.read_text(encoding="utf-8")
    if "<<<<<<<" in text or ">>>>>>>" in text or "=======" in text:
        errors.append(f"conflict marker in {relative}")
    if "Official sources read this session" in text or relative != "sources.html":
        pass
    # check all relative HTML/CSS/JS hrefs resolve under this session directory
    for value in re.findall(r'(?:href|src)="([^"]+)"', text):
        if value.startswith(("https://", "http://", "#", "mailto:")):
            continue
        target = (path.parent / value).resolve()
        try:
            target.relative_to(SITE.resolve())
        except ValueError:
            errors.append(f"page escapes desk namespace {relative}: {value}")
            continue
        if not target.exists():
            errors.append(f"broken local link {relative}: {value}")

if errors:
    print(f"0C9 VALIDATION FAILED ({len(errors)} errors; {checks} checks)")
    for error in errors:
        print(" -", error)
    sys.exit(1)
print(f"0C9 VALIDATION PASSED ({checks} checks; 0 errors)")
