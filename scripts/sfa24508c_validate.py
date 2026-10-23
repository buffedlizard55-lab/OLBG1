#!/usr/bin/env python3
"""Session fa24508c-olbg1 — line-by-line gate for the 23 Oct 2026 desk.

Checks, with no network access:
  * every originated price belongs to an officially verified fixture;
  * every price is exactly 1/probability and the American conversion is correct;
  * every verified fixture cites an allowlisted official host;
  * every written prediction is >= 30 words, unique in shape, and free of the
    two banned words;
  * every flag carries an external source;
  * every covered sport has a page and every internal link resolves.
Exit code 0 only when there are no errors.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DESK = ROOT / "fa24508c"
errors: list[str] = []

OFFICIAL_HOSTS = {
    "statsapi.mlb.com", "api-web.nhle.com", "www.nba.com", "stats.unitedrugby.com",
    "www.wst.tv", "www.formula1.com", "munster.gaa.ie", "www.pdc.tv",
    "www.atptour.com", "www.gbgb.org.uk", "www.olbg.com",
}

BANNED = ("model", "verified")


def american(decimal: float) -> int:
    if decimal >= 2.0:
        return int(round((decimal - 1.0) * 100))
    return int(round(-100.0 / (decimal - 1.0)))


def main() -> int:
    data = json.loads((ROOT / "data" / "fa24508c" / "desk.json").read_text())
    fixtures = {f["id"]: f for f in data["fixtures"]}
    markets = data["markets"]

    # 1-2. price arithmetic and provenance
    for m in markets:
        f = fixtures.get(m["fixture_id"])
        if f is None:
            errors.append(f"price {m['fixture_id']} {m['selection']} has no fixture")
            continue
        if not f.get("official_url"):
            errors.append(f"price on unverified fixture {m['fixture_id']}")
        expected = 1.0 / m["p"]
        if abs(expected - m["decimal"]) > 5e-4:
            errors.append(f"decimal mismatch {m['fixture_id']} {m['selection']}: "
                          f"{m['decimal']} vs 1/p={expected:.4f}")
        if american(m["decimal"]) != m["american"]:
            errors.append(f"american mismatch {m['fixture_id']} {m['selection']}")
        if not (0.0 < m["p"] < 1.0):
            errors.append(f"probability out of range {m['fixture_id']}")
        tier = "High" if m["p"] >= 0.70 else ("Medium" if m["p"] >= 0.60 else "Low")
        if m["confidence"] != tier:
            errors.append(f"tier mismatch {m['fixture_id']} {m['selection']}: "
                          f"{m['confidence']} vs {tier}")

    # 3. official hosts
    for f in fixtures.values():
        if not f.get("facts"):
            errors.append(f"verified fixture {f['id']} carries no read facts")
        host = urlparse(f["official_url"]).netloc
        if host not in OFFICIAL_HOSTS:
            errors.append(f"{f['id']} cites non-allowlisted host {host}")

    # 4. predictions
    seen = Counter()
    for p in data["predictions"]:
        words = p["body"].split()
        if len(words) < 30:
            errors.append(f"prediction {p['fixture_id']} is {len(words)} words (<30)")
        low = p["body"].lower()
        for banned in BANNED:
            if re.search(rf"\b{banned}\b", low):
                errors.append(f"prediction {p['fixture_id']} contains banned word '{banned}'")
        sig = " ".join(words[:8]).lower()
        seen[sig] += 1
        if seen[sig] > 1:
            errors.append(f"predictions share an opening: {sig}")
        if p["fixture_id"] not in fixtures:
            errors.append(f"prediction references unknown fixture {p['fixture_id']}")
        sel = p["selection"].lower()
        if not any(tok in low for tok in ("to win", "selection", "back ")):
            errors.append(f"prediction {p['fixture_id']} does not state a selection clearly")

    # 5. flags
    for fl in data["flags"]:
        if not fl.get("source", "").startswith("http"):
            errors.append(f"flag {fl['id']} has no external source")

    # 6. pages and links
    slugs = {s["slug"] for s in data["sports"]}
    for slug in slugs:
        if not (DESK / "sports" / f"{slug}.html").exists():
            errors.append(f"missing sport page {slug}.html")
    pages = list(DESK.rglob("*.html"))
    if len(pages) < 24:
        errors.append(f"only {len(pages)} pages built")
    for page in pages:
        text = page.read_text()
        if "<title>" not in text or "</html>" not in text:
            errors.append(f"{page} is not a complete document")
        for href in re.findall(r'href="([^"]+)"', text):
            if href.startswith(("http", "#", "mailto", "/")):
                continue
            target = (page.parent / href.split("#")[0]).resolve()
            if href.split("#")[0] and not target.exists():
                errors.append(f"{page.relative_to(ROOT)} broken link -> {href}")

    print(f"checked {len(pages)} pages, {len(markets)} prices, "
          f"{len(fixtures)} fixtures, {len(data['predictions'])} predictions, "
          f"{len(data['flags'])} flags")
    if errors:
        for e in errors:
            print("  ERR:", e)
        print(f"VALIDATION FAILED ({len(errors)} errors)")
        return 1
    print("VALIDATION PASSED (0 errors)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
