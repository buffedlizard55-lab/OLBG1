#!/usr/bin/env python3
"""Invariant checks for the 9e041d28 desk.

Run directly (``python3 scripts/s9e041d28_validate.py``) or through
``tests/pipeline/test_desk_9e041d28.py``. Returns a list of human-readable
errors; an empty list means every published claim is internally consistent.

The checks are deliberately about *transfer* between the sourced data, the
pricing module and the HTML, not about re-asserting the numbers themselves.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import s9e041d28_data as D  # noqa: E402
import s9e041d28_model as M  # noqa: E402

DESK = ROOT / "desk"
DATA = ROOT / "data" / "9e041d28"
BANNED = ("model", "verified")
OFFICIAL_HOSTS = ("statsapi.mlb.com", "api-web.nhle.com")
DISCOVERY_HOSTS = ("www.olbg.com",)

PAGES = [
    "index.html", "picks.html", "matches.html", "markets.html", "predictions.html",
    "sports.html", "flagged.html", "repo-review.html", "sources.html",
    "methodology.html", "olbg.html",
]


def _load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def check_data(errors: list[str]) -> dict:
    desk = _load("desk.json")
    for name in ("fixtures.json", "picks.json", "flags.json"):
        if not (DATA / name).is_file():
            errors.append(f"missing export data/9e041d28/{name}")

    if desk["snapshot"] != D.SNAPSHOT_UTC:
        errors.append("snapshot stamp in desk.json differs from the data module")

    fixtures, picks = desk["fixtures"], desk["picks"]
    if len(fixtures) != len(D.FIXTURES):
        errors.append(f"{len(fixtures)} exported fixtures for {len(D.FIXTURES)} sourced rows")
    if len(picks) != len(fixtures):
        errors.append("every proved fixture must carry exactly one pick")

    for f in fixtures:
        if not f["official_url"].startswith("https://"):
            errors.append(f"{f['id']}: official source is not an https URL")
        host = re.sub(r"^https://([^/]+).*$", r"\1", f["official_url"])
        if not any(host.endswith(h) for h in OFFICIAL_HOSTS):
            errors.append(f"{f['id']}: official source host {host} is not a league feed")
        if any(host.endswith(h) for h in DISCOVERY_HOSTS):
            errors.append(f"{f['id']}: OLBG used as an official source")
        if f["olbg_url"] and "olbg.com" not in f["olbg_url"]:
            errors.append(f"{f['id']}: discovery link is not an OLBG URL")
        if f["sport"] not in {s[0] for s in D.SPORTS}:
            errors.append(f"{f['id']}: sport outside the brief's fifteen")

    seen = set()
    for p in picks:
        if p["confidence"] not in ("high", "medium", "low"):
            errors.append(f"{p['fixture_id']}: bad confidence label {p['confidence']!r}")
        fx = next(f for f in fixtures if f["id"] == p["fixture_id"])
        if fx["start_utc"] < desk["snapshot"]:
            errors.append(f"{p['fixture_id']}: priced fixture had already started at the snapshot")
        expected = M.american_from_prob(p["prob"])
        if abs(expected - p["american"]) > 1:
            errors.append(f"{p['fixture_id']}: american odds disagree with probability")
        if p["in_band"] != M.in_price_band(p["prob"]):
            errors.append(f"{p['fixture_id']}: band flag disagrees with the price")
        if p["confidence"] == "high":
            if not p["in_band"]:
                errors.append(f"{p['fixture_id']}: High pick outside -250..+10000")
            if not fx["injuries"].strip():
                errors.append(f"{p['fixture_id']}: High pick without an availability check")
            if p["prob"] < 0.62:
                errors.append(f"{p['fixture_id']}: High pick below the 62% floor")
        text = p["prediction"]
        words = len(text.split())
        if words < 30:
            errors.append(f"{p['fixture_id']}: prediction is {words} words, floor is 30")
        if p["words"] != words:
            errors.append(f"{p['fixture_id']}: word count not recomputed from the text")
        low = text.lower()
        for token in BANNED:
            if token in low:
                errors.append(f"{p['fixture_id']}: prediction contains the internal word {token!r}")
        if text in seen:
            errors.append(f"{p['fixture_id']}: prediction duplicates another pick")
        seen.add(text)
        if p["team"] not in text:
            errors.append(f"{p['fixture_id']}: selection is not named in its own write-up")
    return desk


def check_markets(desk: dict, errors: list[str]) -> None:
    for block in desk["markets"]:
        for mk in block["markets"]:
            total = sum(o["prob"] for o in mk["outcomes"])
            if abs(total - 1.0) > 1e-6:
                errors.append(f"{block['fixture_id']}/{mk['market']}: outcomes sum to {total:.6f}")
            for o in mk["outcomes"]:
                if not 0 < o["prob"] < 1:
                    errors.append(f"{block['fixture_id']}/{mk['market']}: probability out of range")
                if abs(o["decimal"] - 1 / o["prob"]) > 1e-6:
                    errors.append(f"{block['fixture_id']}/{mk['market']}: decimal is not 1/p")


def check_sources(desk: dict, errors: list[str]) -> None:
    urls = [s["url"] for s in desk["sources"]]
    if len(urls) != len(set(urls)):
        errors.append("duplicate source URLs in the log")
    if len(desk["sources"]) < 10:
        errors.append("source log is implausibly short")
    for s in desk["sources"]:
        if not s["url"].startswith("https://"):
            errors.append(f"source {s['name']}: not https")
        if s["read_at"] > desk["snapshot"]:
            errors.append(f"source {s['name']}: read after the snapshot stamp")
    for fl in desk["flags"]:
        if not fl["source"].startswith("https://"):
            errors.append(f"{fl['id']}: flag has no source link")
        if fl["severity"] not in ("high", "medium", "low"):
            errors.append(f"{fl['id']}: bad severity")
    for f in desk["fixtures"]:
        if not f["official_url"].startswith("https://"):
            errors.append(f"{f['id']}: fixture lacks a source link")


def check_html(desk: dict, errors: list[str]) -> None:
    for page in PAGES:
        path = DESK / page
        if not path.is_file():
            errors.append(f"missing page desk/{page}")
            continue
        text = path.read_text(encoding="utf-8")
        if 'lang="en"' not in text:
            errors.append(f"{page}: no language declaration")
        if "<title>" not in text or 'name="viewport"' not in text:
            errors.append(f"{page}: missing title or viewport")
        if "None" in re.sub(r"<[^>]+>", " ", text):
            errors.append(f"{page}: rendered a literal 'None'")
        if text.lower().count("guarantee") and "no guaranteed returns" not in text.lower():
            errors.append(f"{page}: implies a guarantee")
        for m in re.finditer(r'(?:href|src)="([^"#:]+\.(?:html|css|json|csv))"', text):
            target = (path.parent / m.group(1)).resolve()
            if not target.is_file():
                errors.append(f"{page}: broken local link {m.group(1)}")

    for slug, _name, _sid, _olbg in D.SPORTS:
        if not (DESK / "sports" / f"{slug}.html").is_file():
            errors.append(f"missing sport page sports/{slug}.html")

    index = (DESK / "index.html").read_text(encoding="utf-8")
    if "Executive summary" not in index:
        errors.append("landing page does not open with the executive summary")
    if index.index("Executive summary") > index.index("</main>"):
        errors.append("executive summary is not near the top of the landing page")
    for p in desk["picks"]:
        if p["fixture_id"] not in index:
            errors.append(f"landing page omits pick {p['fixture_id']}")

    flagged = (DESK / "flagged.html").read_text(encoding="utf-8")
    for fl in desk["flags"]:
        if fl["id"] not in flagged:
            errors.append(f"flagged page omits {fl['id']}")

    # no page may present an OLBG listing as priced
    matches = (DESK / "matches.html").read_text(encoding="utf-8")
    if "OLBG listings without governing-body confirmation" not in matches:
        errors.append("matches page does not separate confirmed fixtures from listings")


def check_coverage(errors: list[str]) -> None:
    priced = {f["sport"] for f in D.FIXTURES}
    listed = {r[0] for r in D.OLBG_INVENTORY}
    for slug, name, _sid, _olbg in D.SPORTS:
        if slug not in priced and slug not in listed and slug not in D.NOT_LISTED:
            errors.append(f"{name}: neither priced, listed nor explained as absent")
    if len(D.SPORTS) != 15:
        errors.append("sport registry is not the brief's fifteen")


def validate_desk() -> list[str]:
    errors: list[str] = []
    for path in (DESK, DATA):
        if not path.is_dir():
            return [f"missing build output {path.relative_to(ROOT)}"]
    desk = check_data(errors)
    check_markets(desk, errors)
    check_sources(desk, errors)
    check_html(desk, errors)
    check_coverage(errors)
    return errors


if __name__ == "__main__":
    problems = validate_desk()
    for p in problems:
        print("ERR :", p)
    print(f"{len(problems)} problem(s)")
    sys.exit(1 if problems else 0)
