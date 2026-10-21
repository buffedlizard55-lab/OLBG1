#!/usr/bin/env python3
"""Read data/fixtures.json, originate lines for every match, write data/lines.json."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from model import price_match, SPORTS  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    fixtures = json.loads((ROOT / "data/fixtures.json").read_text())
    matches = fixtures["matches"]

    priced, skipped = [], []
    for m in matches:
        if not m.get("away"):
            skipped.append({"id": m["id"], "reason": "championship round with no two-sided fixture - verified but not priced"})
            continue
        if m["sport"] not in SPORTS:
            skipped.append({"id": m["id"], "reason": f"no model config for sport '{m['sport']}'"})
            continue
        priced.append(price_match(m))

    out = {
        "generated": fixtures["retrieved"],
        "window": fixtures["window"],
        "model_version": "1.0.0",
        "counts": {
            "matches": len(priced),
            "high": sum(1 for p in priced if p["confidence"] == "high"),
            "medium": sum(1 for p in priced if p["confidence"] == "medium"),
            "low": sum(1 for p in priced if p["confidence"] == "low"),
        },
        "lines": priced,
        "skipped": skipped,
    }
    (ROOT / "data/lines.json").write_text(json.dumps(out, indent=2) + "\n")

    print(f"priced {len(priced)} matches")
    for tier in ("high", "medium", "low"):
        n = out["counts"][tier]
        print(f"  {tier:<7} {n}")
    print("\nHIGH CONFIDENCE PICKS")
    for p in priced:
        if p["confidence"] == "high":
            print(f"  {p['sport']:<12} {p['pick']:<26} p={max(p['home_probability'], p['away_probability']):.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
