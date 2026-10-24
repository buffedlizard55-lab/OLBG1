"""Gate for desk 3d121822.  python3 scripts/s3d121822_validate.py"""
from __future__ import annotations

import json
import re
import sys
from html import unescape
from pathlib import Path
from urllib.parse import unquote, urlsplit

import s3d121822_data as D
import s3d121822_model as M

OUT = M.OUT
DATA = M.DATA
BANNED = ("model", "models", "verified", "verification")
errors: list[str] = []


def check(ok, msg):
    if not ok:
        errors.append(msg)


def pages():
    return sorted(OUT.rglob("*.html"))


def strip(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def main():
    fixtures = {f["id"]: f for f in D.fixture_rows()}
    prices = M.build_prices()

    # --- data integrity
    check(len(fixtures) == len(set(fixtures)), "duplicate fixture ids")
    for fx in fixtures.values():
        check(fx["olbg"].startswith("https://www.olbg.com/"),
              f"{fx['id']}: OLBG discovery link missing or not OLBG")
        check(fx["a"] and fx["b"], f"{fx['id']}: participant missing")
    for sp in D.SPORTS:
        check(bool(sp["gap"]), f"{sp['key']}: no gap statement")
        check(sp["route"].startswith("https://www.olbg.com/"), f"{sp['key']}: no OLBG route")

    # --- price / confidence algebra
    for fid, p in prices.items():
        check(len(M.market_rows(fixtures[fid], p)) == 4, f"{fid}: expected 4 market rows")
        if p["conf"] == "High":
            check(M.HIGH_FLOOR <= p["p_pick"] <= M.BAND_FLOOR,
                  f"{fid}: High outside the 70%/-250 window ({p['p_pick']:.4f})")
        if p["written"]:
            check(p["side"] is not None, f"{fid}: prediction without a selection")
            check(fid in D.PREDICTIONS, f"{fid}: pick without a written analysis")

    # --- predictions
    shingles: dict[tuple, str] = {}
    for fid, pred in D.PREDICTIONS.items():
        check(fid in fixtures, f"{fid}: prediction for unknown fixture")
        words = pred["text"].split()
        check(len(words) >= 30, f"{fid}: prediction is {len(words)} words, needs 30")
        low = pred["text"].lower()
        for bad in BANNED:
            check(bad not in low, f"{fid}: banned word '{bad}' in published prose")
        tokens = {t.lower().strip("().,") for t in (fixtures[fid]["a"] + " " + fixtures[fid]["b"]).split()[1:]}
        check(any(t and t in pred["selection"].lower() for t in tokens),
              f"{fid}: selection does not name a participant")
        check(pred["evidence"], f"{fid}: no evidence links")
        for sid in pred["evidence"]:
            check(sid in D.SOURCES, f"{fid}: unknown evidence id {sid}")
        for i in range(len(words) - 7):
            key = tuple(w.lower().strip(",.") for w in words[i:i + 8])
            if key in shingles and shingles[key] != fid:
                check(False, f"{fid}: repeats an 8-word phrase from {shingles[key]}")
                break
            shingles[key] = fid
    check(len(D.PREDICTIONS) == len([p for p in prices.values() if p["written"]]),
          "prediction count does not match published picks")

    # --- pages: structure, links, rows
    for path in pages():
        html = path.read_text(encoding="utf-8")
        check(html.count("<h1") == 1, f"{path.relative_to(OUT)}: expected exactly one h1")
        check("<title>" in html, f"{path.relative_to(OUT)}: no title")
        check(">None<" not in html and "None</td>" not in html and "None</b>" not in html,
              f"{path.relative_to(OUT)}: literal None rendered")
        for href in re.findall(r'href="([^"]+)"', html):
            href = unescape(href)
            parts = urlsplit(href)
            if parts.scheme or parts.netloc:
                check(parts.scheme in ("https", "http"), f"{path.name}: unsafe scheme {href}")
                if parts.netloc and not parts.scheme == "https":
                    check(False, f"{path.name}: non-https external link {href}")
                continue
            target = (path.parent / unquote(parts.path)).resolve() if parts.path else path
            try:
                target.relative_to(OUT.resolve())
            except ValueError:
                errors.append(f"{path.name}: link escapes desk {href}")
                continue
            if target.is_dir():
                target = target / "index.html"
            check(target.is_file(), f"{path.relative_to(OUT)}: broken link {href}")
            if parts.fragment and target.suffix == ".html" and target.is_file():
                check(f'id="{unquote(parts.fragment)}"' in target.read_text(encoding="utf-8"),
                      f"{path.relative_to(OUT)}: missing fragment {href}")
        for row in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S):
            if "<th" in row:
                continue
            check("href=" in row, f"{path.relative_to(OUT)}: table row without a source link: "
                                  f"{strip(row)[:80]}")

    # --- data exports
    fx = json.loads((DATA / "fixtures.json").read_text())
    check(fx["count"] == len(fixtures), "fixtures.json count drift")
    check(fx["priced"] == len(prices), "fixtures.json priced drift")
    check(fx["picks"] == len(D.PREDICTIONS), "fixtures.json picks drift")
    preds = json.loads((DATA / "predictions.json").read_text())
    check(preds["count"] == len(D.PREDICTIONS), "predictions.json count drift")
    flags = json.loads((DATA / "flags.json").read_text())
    check(flags["count"] == len(D.FLAGS), "flags.json count drift")

    # --- every sport has a page and every fixture appears on it
    for sp in D.SPORTS:
        page = OUT / "sports" / f"{sp['key']}.html"
        check(page.is_file(), f"{sp['key']}: sport page missing")
        if page.is_file():
            html = page.read_text(encoding="utf-8")
            for row in sp["fixtures"]:
                check(row[0] in html or row[2] in html,
                      f"{sp['key']}: fixture {row[0]} not rendered")

    for e in errors:
        print("ERROR:", e)
    print(f"3d121822 validation: {len(errors)} errors · {len(pages())} pages · "
          f"{len(fixtures)} fixtures · {len(prices)} priced · {len(D.PREDICTIONS)} predictions")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
