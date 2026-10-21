#!/usr/bin/env python3
"""
ccb6bde2_validate.py — validation gate for the /ccb6bde2/ desk. Fails (exit 1) on:
  * any priced market whose probabilities do not sum to 1 (1e-6 tolerance)
  * book odds inconsistent with the 5%-overround convention
  * a match row without an official source URL
  * a high-confidence pick without a prediction, or whose prediction quotes a
    winner price different from the v2.1 book
  * a prediction under 30 words, or a repeated 6-word n-gram across predictions
  * a broken internal link anywhere in ccb6bde2/*.html
  * expanded correct-score books inconsistent with the winner price
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "ccb6bde2"
errors: list[str] = []


def check(cond: bool, msg: str) -> None:
    if not cond:
        errors.append(msg)


def main() -> None:
    exp = json.loads((ROOT / "data" / "market_expansion-ccb6bde2.json").read_text())
    fresh = {p["match_id"]: p for p in
             json.loads((ROOT / "data" / "predictions-ccb6bde2.json").read_text())["items"]}
    matches = [r for r in exp["matches"] if not r.get("field_event")]
    n_markets = 0

    for r in matches:
        src = r.get("official_source") or {}
        check(bool(src.get("url", "").startswith("https://")),
              f"{r['id']}: missing official source URL")
        all_markets = r["v21"]["core_markets"] + r["expanded_markets"]
        for m in all_markets:
            n_markets += 1
            micro = sum(round(o["probability"] * 1_000_000) for o in m["outcomes"])
            check(micro == 1_000_000, f"{r['id']} {m['key']}: probs sum {micro/1e6:.6f}")
            for o in m["outcomes"]:
                p = o["probability"]
                expect = round(min(max(1.0 / (min(max(p, 0.012), 0.960) * 1.05), 1.02), 85.0), 2)
                check(abs(o["odds"] - expect) < 0.015,
                      f"{r['id']} {m['key']} '{o['selection']}': odds {o['odds']} != {expect}")
                check(1.0 < o["odds"] <= 85.0, f"{r['id']} {m['key']}: odds out of range")

        # correct-score book must reproduce the two-way winner probability
        cs = next((m for m in r["expanded_markets"] if m["key"] == "correct_score"), None)
        if cs:
            hp, ap = r["v21"]["home_probability"], r["v21"]["away_probability"]
            p2 = hp / (hp + ap)
            home_mass = sum(o["probability"] for o in cs["outcomes"]
                            if o["selection"].startswith(r["home"]))
            check(abs(home_mass - p2) < 0.002,
                  f"{r['id']}: correct-score home mass {home_mass:.4f} != winner p {p2:.4f}")

    # ---- predictions ------------------------------------------------------
    texts: list[tuple[str, str]] = []
    highs = [r for r in matches if r["v21"]["confidence"] == "high"]
    for r in highs:
        p = fresh.get(r["id"]) or r.get("prediction_v20")
        check(p is not None, f"{r['id']}: high pick without prediction")
        if not p:
            continue
        check(p["selection"] == r["v21"]["pick"],
              f"{r['id']}: prediction selection '{p['selection']}' != pick '{r['v21']['pick']}'")
        w = len(p["text"].split())
        check(w >= 30, f"{r['id']}: prediction only {w} words")
        texts.append((r["id"], p["text"]))
        win = {o["selection"]: o["odds"] for o in r["v21"]["core_markets"][0]["outcomes"]}
        pick_odds = win.get(r["v21"]["pick"])
        nums = re.findall(r"\b\d\.\d\d\b", p["text"])
        if nums and pick_odds:
            check(abs(float(nums[0]) - pick_odds) < 0.005,
                  f"{r['id']}: prediction quotes {nums[0]} but v2.1 winner price is {pick_odds}")

    def ngrams(t: str, n: int = 6):
        w = re.findall(r"[a-z]+(?:'[a-z]+)?|\d+(?:\.\d+)?", t.lower())
        return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            dup = ngrams(texts[i][1]) & ngrams(texts[j][1])
            check(not dup, f"predictions {texts[i][0]} & {texts[j][0]} share 6-gram: {sorted(dup)[:1]}")

    # ---- internal links ----------------------------------------------------
    hrefs = re.compile(r'href="([^"#]+)(#[^"]*)?"')
    n_links = 0
    for page in sorted(OUT.rglob("*.html")):
        for m in hrefs.finditer(page.read_text()):
            href = m.group(1)
            if href.startswith(("http://", "https://", "mailto:")):
                continue
            n_links += 1
            target = (page.parent / href).resolve()
            ok = target.is_file() or (target / "index.html").is_file()
            check(ok, f"{page.relative_to(ROOT)}: broken internal link '{href}'")

    print(f"validated {len(matches)} matches, {n_markets} markets, "
          f"{len(highs)} high-confidence predictions, {n_links} internal links")
    if errors:
        print(f"VALIDATION FAILED — {len(errors)} errors:")
        for e in errors[:40]:
            print(" -", e)
        sys.exit(1)
    print("VALIDATION PASSED")


if __name__ == "__main__":
    main()
