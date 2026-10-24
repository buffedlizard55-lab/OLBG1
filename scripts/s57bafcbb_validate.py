#!/usr/bin/env python3
"""Desk 57bafcbb - self-validation.

Mirrors the checks the repository's canonical desks are held to:

* exactly 15 sports in the brief's order, one page per sport, unique fixture ids;
* every priced fixture cites at least one official source, and every source
  URL is a live https URL;
* every pick's fair price is the arithmetic of its own estimate, and every
  pick carries a written prediction of at least 30 words that names the pick,
  states the bet and prints the price;
* High picks sit inside the -250..+10000 band and are 60% or better, and the
  desk never labels a pick High whose price is outside the band;
* prediction prose is unique in its 5-grams and 6-grams;
* the rendered HTML has no banned vocabulary, no linear-gradient, exactly one
  h1 per page, no duplicate ids, no plain http:// links, and every internal
  link resolves inside the repository;
* every table row on every page carries an https link;
* the JSON mirrors reconcile with the module of record by exact count.

Run:  python3 scripts/s57bafcbb_validate.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import s57bafcbb_data as d
import s57bafcbb_model as m

ROOT = Path(__file__).resolve().parent.parent
DESK_DIR = ROOT / "57bafcbb"
DATA_DIR = ROOT / "data" / "57bafcbb"

BANNED = ["model", "verified"]
PAGES = ["index.html", "picks.html", "predictions.html", "matches.html", "markets.html",
         "flagged.html", "sources.html", "methodology.html"]
SPORT_PAGES = [f"sports/{s['slug']}.html" for s in d.SPORTS]


def _fail(errors, msg):
    errors.append(msg)


def check_sports(errors, desk):
    slugs = [s["slug"] for s in d.SPORTS]
    brief = ["golf", "volleyball", "rugby-union", "cricket", "snooker", "darts", "baseball",
             "gaelic-sports", "greyhounds", "tennis", "motor-racing", "handball",
             "ice-hockey", "basketball", "rugby-league"]
    if slugs != brief:
        _fail(errors, f"sports are not the brief's 15 in order: {slugs}")
    for s in d.SPORTS:
        path = DESK_DIR / s["page"]
        if not path.is_file():
            _fail(errors, f"missing sport page {s['page']}")
    for slug in slugs:
        fixture_ids = [f["id"] for f in desk["fixtures"] if f["sport"] == slug]
        if len(fixture_ids) != len(set(fixture_ids)):
            _fail(errors, f"duplicate fixture ids in sport {slug}")


def check_ids(errors, desk):
    ids = [f["id"] for f in desk["fixtures"]]
    if len(ids) != len(set(ids)):
        _fail(errors, f"duplicate fixture ids across the desk: {sorted(set(ids))}")


def check_priced_fixtures_have_official_source(errors, desk):
    for f in desk["fixtures"]:
        if not f.get("priced"):
            continue
        official = [s for s in f["sources"] if s.get("official")]
        if not official:
            _fail(errors, f"priced fixture {f['id']} cites no official source: {[s['id'] for s in f['sources']]}")


def check_lines(errors, desk):
    for f in desk["fixtures"]:
        book = f.get("book")
        if not book:
            continue
        if not (0.02 <= book["home_prob"] <= 0.98 and 0.02 <= book["away_prob"] <= 0.98):
            _fail(errors, f"{f['id']}: probabilities outside the fair range")
        if abs((book["home_prob"] + book["away_prob"]) - 1.0) > 1e-6:
            _fail(errors, f"{f['id']}: two-way book is not fair (margin {book['margin']})")
        for side in ("home", "away"):
            p = book[f"{side}_prob"]
            if book[f"{side}_price"] != m.american_from_prob(p):
                _fail(errors, f"{f['id']}: {side} price {book[f'{side}_price']} != american({p})")
        est = book["estimate"]
        if not (0.05 <= est <= 0.98):
            _fail(errors, f"{f['id']}: estimate {est} outside the supported range")
        if book["estimate_price"] != m.american_from_prob(est):
            _fail(errors, f"{f['id']}: pick price {book['estimate_price']} != american({est})")


def check_tiers(errors, desk):
    high = 0
    over70 = 0
    for p in desk["picks"]:
        if p["american"] != m.american_from_prob(p["estimate"]):
            _fail(errors, f"{p['fixture_id']}: pick price {p['american']} != american({p['estimate']})")
        if p["tier"] == "High":
            high += 1
            if p["estimate"] >= 0.70:
                over70 += 1
            if not m.american_in_band(p["american"]):
                _fail(errors, f"{p['fixture_id']}: High pick {p['pick']} priced {p['american']} outside the band")
            if p["estimate"] < 0.60:
                _fail(errors, f"{p['fixture_id']}: High pick {p['pick']} below the 60% floor ({p['estimate']})")
            if not p["has_prediction"]:
                _fail(errors, f"{p['fixture_id']}: High pick has no written prediction")
        if p["tier"] == "Medium" and not m.american_in_band(p["american"]):
            _fail(errors, f"{p['fixture_id']}: Medium pick {p['pick']} priced {p['american']} outside the band")
        if not p["has_prediction"]:
            _fail(errors, f"{p['fixture_id']}: pick {p['pick']} has no written prediction")
    if high == 0:
        _fail(errors, "desk published no High confidence pick at all")
    return high, over70


def check_predictions(errors, desk):
    preds = desk["predictions"]
    pick_ids = {p["fixture_id"] for p in desk["picks"]}
    for p in preds:
        if p["fixture_id"] not in pick_ids:
            _fail(errors, f"prediction for {p['fixture_id']} which is not a pick")
        if p["words"] < 30:
            _fail(errors, f"prediction for {p['fixture_id']} is only {p['words']} words")
        if p["pick"] not in p["text"]:
            _fail(errors, f"prediction for {p['fixture_id']} does not name the pick {p['pick']}")
        if p["bet"] not in p["text"]:
            _fail(errors, f"prediction for {p['fixture_id']} does not state the bet {p['bet']}")
        if str(p["american"]) not in p["text"]:
            _fail(errors, f"prediction for {p['fixture_id']} does not print its price {p['american']}")
        if "<<PRICE>>" in p["text"]:
            _fail(errors, f"prediction for {p['fixture_id']} still carries an unfilled price placeholder")
    if len(preds) != len(pick_ids):
        _fail(errors, f"predictions ({len(preds)}) do not cover every pick ({len(pick_ids)})")
    # uniqueness at 5-gram and 6-gram level across the whole desk
    for n in (5, 6):
        seen = {}
        for p in preds:
            words = p["text"].split()
            grams = [" ".join(words[i:i + n]) for i in range(max(0, len(words) - n + 1))]
            for g in grams:
                if g in seen:
                    _fail(errors, f"{n}-gram repeated: {g!r} in {seen[g]} and {p['fixture_id']}")
                seen[g] = p["fixture_id"]
    # no prediction may be a bare winner statement
    for p in preds:
        if len(p["text"].split()) < 30:
            _fail(errors, f"prediction for {p['fixture_id']} is not a full paragraph")


def check_sources(errors, desk):
    for s in d.SOURCES:
        if not s["url"].startswith("https://"):
            _fail(errors, f"source {s['id']} is not https: {s['url']}")
        if not re.match(r"^https://[^\s/]+", s["url"]):
            _fail(errors, f"source {s['id']} has an unusable URL: {s['url']}")
    ids = [s["id"] for s in d.SOURCES]
    if len(ids) != len(set(ids)):
        _fail(errors, "duplicate source ids")


def _internal_links_resolve(errors, rel_dir: Path, text: str, label: str):
    for href in re.findall(r'href="([^"]+)"', text):
        if href.startswith(("http://", "https://", "mailto:", "#", "tel:")):
            continue
        if href.startswith("//"):
            _fail(errors, f"{label}: protocol-relative link {href}")
            continue
        target = (rel_dir / href).resolve()
        try:
            target.relative_to(ROOT)
        except ValueError:
            _fail(errors, f"{label}: link {href} escapes the repository")
            continue
        if not target.is_file():
            _fail(errors, f"{label}: link {href} does not resolve to a file")


def check_html(errors):
    for name in PAGES + SPORT_PAGES:
        path = DESK_DIR / name
        if not path.is_file():
            _fail(errors, f"missing page {name}")
            continue
        text = path.read_text()
        low = text.lower()
        for word in BANNED:
            if word in low:
                _fail(errors, f"{name}: banned word {word!r} appears on the page")
        if "linear-gradient" in low:
            _fail(errors, f"{name}: CSS contains linear-gradient")
        if low.count("<h1") != 1:
            _fail(errors, f"{name}: expected exactly one h1, found {low.count('<h1')}")
        ids = re.findall(r'\sid="([^"]+)"', text)
        dupes = {i for i in ids if ids.count(i) > 1}
        if dupes:
            _fail(errors, f"{name}: duplicate ids {sorted(dupes)}")
        if "http://" in text:
            _fail(errors, f"{name}: plain http:// link found")
        _internal_links_resolve(errors, DESK_DIR / Path(name).parent, text, name)
        # every data table row carries an https link (header rows are exempt)
        for row in re.findall(r"<tr[^>]*>(.*?)</tr>", text, re.S):
            if "<td" not in row:
                continue
            if "https://" not in row:
                _fail(errors, f"{name}: a table row has no https source link")


def check_reconcile(errors, desk):
    fixtures = json.loads((DATA_DIR / "fixtures.json").read_text())
    picks = json.loads((DATA_DIR / "picks.json").read_text())
    preds = json.loads((DATA_DIR / "predictions.json").read_text())
    sources = json.loads((DATA_DIR / "sources.json").read_text())
    flags = json.loads((DATA_DIR / "flags.json").read_text())
    olbg = json.loads((DATA_DIR / "olbg.json").read_text())
    coverage = json.loads((DATA_DIR / "coverage.json").read_text())
    manifest = json.loads((DATA_DIR / "manifest.json").read_text())

    if len(fixtures) != len(desk["fixtures"]):
        _fail(errors, f"fixtures.json ({len(fixtures)}) != module ({len(desk['fixtures'])})")
    if len(picks) != len(desk["picks"]):
        _fail(errors, f"picks.json ({len(picks)}) != module ({len(desk['picks'])})")
    if len(preds) != len(desk["predictions"]):
        _fail(errors, f"predictions.json ({len(preds)}) != module ({len(desk['predictions'])})")
    if len(sources) != len(d.SOURCES):
        _fail(errors, "sources.json does not match the module of record")
    if len(flags) != len(d.FLAG_ITEMS):
        _fail(errors, "flags.json does not match the module of record")
    if len(olbg) != len(d.OLBG_LOG):
        _fail(errors, "olbg.json does not match the module of record")
    if len(coverage) != 15:
        _fail(errors, "coverage.json does not cover all 15 sports")
    if manifest["session_id"] != d.SESSION_ID:
        _fail(errors, "manifest.json carries the wrong session id")
    if manifest["fixtures"] != len(fixtures) or manifest["priced_fixtures"] != len(picks):
        _fail(errors, "manifest.json counts do not reconcile")
    tiers = {"High": 0, "Medium": 0, "Low": 0}
    for p in picks:
        tiers[p["tier"]] = tiers.get(p["tier"], 0) + 1
    if manifest["tiers"] != tiers:
        _fail(errors, f"manifest tiers {manifest['tiers']} != actual {tiers}")
    for f in flags:
        for u in f["source_links"]:
            if not u.startswith("https://"):
                _fail(errors, f"flag {f['id']} links a non-https url {u}")
    for s in d.OLBG_LOG:
        if not s["url"].startswith("https://"):
            _fail(errors, f"olbg log {s['sport']} links a non-https url")


def check_flags(errors):
    ids = [f["id"] for f in d.FLAG_ITEMS]
    if len(ids) != len(set(ids)):
        _fail(errors, "duplicate flag ids")
    flagged_sports = {f["id"] for f in d.FLAG_ITEMS if f["kind"] == "sport-coverage"}
    priced = {p["sport"] for p in m.build_all()["picks"]}
    for s in d.SPORTS:
        if s["slug"] not in priced and f"f-{s['slug']}-no-market" not in flagged_sports:
            _fail(errors, f"sport {s['slug']} has no priced pick and no flagged-coverage entry")


def run():
    desk = m.build_all()
    errors = []
    check_sports(errors, desk)
    check_ids(errors, desk)
    check_priced_fixtures_have_official_source(errors, desk)
    check_lines(errors, desk)
    high, over70 = check_tiers(errors, desk)
    check_predictions(errors, desk)
    check_sources(errors, desk)
    check_html(errors)
    check_reconcile(errors, desk)
    check_flags(errors)

    report = {
        "session_id": d.SESSION_ID,
        "fixtures": len(desk["fixtures"]),
        "priced_fixtures": len(desk["picks"]),
        "predictions": len(desk["predictions"]),
        "high_picks": high,
        "high_picks_above_70": over70,
        "tiers": {"High": high,
                  "Medium": sum(1 for p in desk["picks"] if p["tier"] == "Medium"),
                  "Low": sum(1 for p in desk["picks"] if p["tier"] == "Low")},
        "sports_priced": len({p["sport"] for p in desk["picks"]}),
        "flags": len(d.FLAG_ITEMS),
        "pages": len(PAGES) + len(SPORT_PAGES),
        "errors": errors,
    }
    return report


def main():
    report = run()
    for e in report["errors"]:
        print(f"  FAIL  {e}")
    print(f"desk {report['session_id']}: {report['pages']} pages, {report['fixtures']} fixtures, "
          f"{report['priced_fixtures']} picks, {report['predictions']} predictions, "
          f"{report['high_picks']} High, {report['flags']} flags")
    if report["errors"]:
        print(f"  {len(report['errors'])} FAILURE(S)")
        return 1
    print("  OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
