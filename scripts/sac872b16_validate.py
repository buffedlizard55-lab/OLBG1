"""Validate the ac872b16 T65 desk and its rendered pages.

Run: python3 -m scripts.sac872b16_validate
Exit code 0 = PASS.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from scripts.sac872b16_prose import PREDICTIONS

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "ac872b16"
SITE = ROOT / "ac872b16"

errors: list[str] = []
warnings: list[str] = []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def main():
    fixtures = json.loads((DATA / "fixtures.json").read_text())
    markets = json.loads((DATA / "markets.json").read_text())
    picks = json.loads((DATA / "picks.json").read_text())
    meta = json.loads((DATA / "meta.json").read_text())

    ids = [f["id"] for f in fixtures]
    if len(ids) != len(set(ids)):
        err("duplicate fixture ids")
    for f in fixtures:
        if not f.get("source_urls"):
            err(f"{f['id']} has no source url")
        if f.get("pricing", {}).get("status") == "priced" and f["id"] not in markets:
            err(f"{f['id']} priced without a market block")
        if f.get("confidence") == "high" and f["verification"] != "verified":
            err(f"{f['id']} High on non-verified inputs")

    highs = [p for p in picks if p["confidence"] == "high"]
    if len(highs) != meta["counts"]["high"]:
        err("meta high count mismatch")
    if not highs:
        err("no High picks published")

    seen = set()
    for p in picks:
        pr = p.get("prediction") or ""
        words = len(re.findall(r"\S+", pr))
        if p["confidence"] in ("high", "medium"):
            if words < 30:
                err(f"{p['fixture_id']} prediction has {words} words")
            if pr in seen:
                err(f"{p['fixture_id']} prediction is not unique")
            seen.add(pr)
        if p["confidence"] == "high":
            if not (0.70 <= p["probability"] <= 0.7142857):
                err(f"{p['fixture_id']} High probability {p['probability']} outside 70-71.43%")
            if not (1.40 <= p["fair_decimal"] <= 1.4286):
                err(f"{p['fixture_id']} High fair price {p['fair_decimal']} outside 1.40-1.4286")
            if p["verification"] != "verified":
                err(f"{p['fixture_id']} High not verified")
            if p.get("american") and not (-250 <= int(p["american"]) <= 10000):
                err(f"{p['fixture_id']} High american {p['american']} outside -250..+10000")
    for p in picks:
        if p["confidence"] == "medium" and p["fixture_id"] not in PREDICTIONS:
            warn(f"{p['fixture_id']} Medium without hand-written prediction")

    for fid, blob in markets.items():
        for m in blob["markets"]:
            ps = [o["probability"] for o in m["outcomes"]]
            if any(x is None or not 0 < x < 1 for x in ps):
                if fid.startswith("carried-") is False:
                    err(f"{fid}/{m['key']} has an invalid probability")

    pages = list(SITE.rglob("*.html"))
    if len(pages) < 20:
        err(f"only {len(pages)} pages rendered")
    for page in pages:
        text = page.read_text()
        if "None" in text:
            err(f"{page} renders a literal None")
        for href in re.findall(r'href="([^"]+)"', text):
            if href.startswith(("http", "#", "mailto")):
                continue
            if not (page.parent / href).resolve().exists():
                err(f"{page} broken link {href}")
        if "<table" not in text and page.name != "methodology.html":
            warn(f"{page} has no table")

    for page in pages:
        text = page.read_text()
        if text.count("<table") and "rel=\"noopener\"" not in text:
            warn(f"{page} table without an outbound source link")

    print(f"fixtures {len(fixtures)} | markets {sum(len(m['markets']) for m in markets.values())} | "
          f"picks {len(picks)} | High {len(highs)} | pages {len(pages)}")
    for w in warnings:
        print("WARN", w)
    if errors:
        for e in errors:
            print("ERROR", e)
        print(f"FAILED {len(errors)} errors / {len(warnings)} warnings")
        raise SystemExit(1)
    print(f"PASSED 0 errors / {len(warnings)} warnings")


if __name__ == "__main__":
    main()
