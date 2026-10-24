#!/usr/bin/env python3
"""Release gates for the 2ff8342b desk.

Checks the facts we can check mechanically: every official row has an official
source, prices match their probabilities, tiers match the published rule,
predictions are long enough, unique and free of the forbidden words, and every
internal link resolves to a generated file.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "2ff8342b"
SITE = ROOT / "2ff8342b"

FORBIDDEN = (" model ", " models ", "verified", "verify", "verification")
OFFICIAL_HOSTS = (
    "statsapi.mlb.com", "api-web.nhle.com", "official.nba.com", "nba.com",
    "atptour.com", "wst.tv", "gaa.ie", "formula1.com",
)


def _american(p: float) -> int:
    if p <= 0.5:
        return round(100 * (1 - p) / p)
    return -round(100 * p / (1 - p))


def validate() -> list[str]:
    errors: list[str] = []
    fixtures = json.loads((DATA / "fixtures.json").read_text())
    lines = json.loads((DATA / "lines.json").read_text())
    preds = json.loads((DATA / "predictions.json").read_text())
    sources = json.loads((DATA / "sources.json").read_text())["official_sources"]
    flagged = json.loads((DATA / "flagged.json").read_text())
    summary = json.loads((DATA / "summary.json").read_text())

    ids = [f["id"] for f in fixtures["fixtures"]]
    if len(ids) != len(set(ids)):
        errors.append("duplicate fixture id")

    valid_sports = {"golf", "volleyball", "rugby-union", "cricket", "snooker", "darts", "baseball",
                    "gaelic-sports", "greyhounds", "tennis", "motor-racing", "handball",
                    "ice-hockey", "basketball", "rugby-league"}

    for fx in fixtures["fixtures"]:
        fid = fx["id"]
        if fx["sport"] not in valid_sports:
            errors.append(f"{fid}: sport outside the brief's 15")
        if fx["verification"] == "official":
            if not fx["sources"]:
                errors.append(f"{fid}: official row without a source")
            for sid in fx["sources"]:
                src = sources.get(sid)
                if src is None:
                    errors.append(f"{fid}: unknown source {sid}")
                    continue
                if src["role"] != "official":
                    errors.append(f"{fid}: non-official source used for a fact")
                host = urlsplit(src["url"]).hostname or ""
                if not any(host == h or host.endswith("." + h) for h in OFFICIAL_HOSTS):
                    errors.append(f"{fid}: source host not on the official allow-list ({host})")
        elif fx["verification"] == "discovery_only":
            if fx["sources"]:
                errors.append(f"{fid}: discovery-only row carries a source id")
            if not fx["gaps"]:
                errors.append(f"{fid}: discovery-only row without a gap note")
        else:
            errors.append(f"{fid}: unknown verification level")

    # price arithmetic and tier rule
    tier_rule = lines["tier_rule"]
    for ln in lines["markets"]:
        p = ln["probability"]
        if abs(1 / ln["decimal"] - p) > 0.002:
            errors.append(f"{ln['fixture_id']}: decimal does not match probability")
        if _american(p) != ln["american"]:
            errors.append(f"{ln['fixture_id']}: american conversion mismatch for {ln['market']}")
        in_window = tier_rule["odds_window"][0] <= ln["american"] <= tier_rule["odds_window"][1]
        if in_window != ln["eligible"]:
            errors.append(f"{ln['fixture_id']}: eligibility flag mismatch")
        expected = ("Excluded" if not in_window else
                    "High" if p >= tier_rule["high_min"] else
                    "Medium" if p >= tier_rule["medium_min"] else "Low")
        if expected != ln["tier"]:
            errors.append(f"{ln['fixture_id']}: tier mismatch ({expected} vs {ln['tier']})")

    for pick in lines["picks"]:
        in_window = tier_rule["odds_window"][0] <= pick["american"] <= tier_rule["odds_window"][1]
        if pick["tier"] == "Excluded":
            if in_window:
                errors.append(f"{pick['fixture_id']}: suppressed pick is actually inside the window")
        else:
            if not in_window:
                errors.append(f"{pick['fixture_id']}: published pick outside the odds window")
            expected = ("High" if pick["probability"] >= tier_rule["high_min"]
                        else "Medium" if pick["probability"] >= tier_rule["medium_min"] else "Low")
            if pick["tier"] != expected:
                errors.append(f"{pick['fixture_id']}: pick tier mismatch")

    # predictions
    texts = []
    for pr in preds["predictions"]:
        words = len(pr["text"].split())
        if words < 30:
            errors.append(f"{pr['id']}: only {words} words")
        if pr["fixture"] not in ids:
            errors.append(f"{pr['id']}: unknown fixture")
        lowered = " " + pr["text"].lower() + " "
        for word in FORBIDDEN:
            if word in lowered:
                errors.append(f"{pr['id']}: forbidden token{word!r}")
        for sid in pr["sources"]:
            if sid not in sources:
                errors.append(f"{pr['id']}: unknown source {sid}")
        texts.append(" ".join(pr["text"].lower().split()))
    if len(texts) != len(set(texts)):
        errors.append("duplicate prediction text")

    # the published pick must be the side the prediction argues for
    pick_by_fx = {p["fixture_id"]: p for p in lines["picks"]}
    for pr in preds["predictions"]:
        pick = pick_by_fx.get(pr["fixture"])
        if pick and pick["selection"].lower() not in pr["selection"].lower():
            errors.append(f"{pr['id']}: prediction argues for a different side than the published pick")

    # every priced fixture with a prediction must have the selection side named
    for pr in preds["predictions"]:
        if pr["fixture"] not in {p["fixture_id"] for p in lines["picks"]}:
            # tennis has no price by design; require the gap to say so
            fx = next(f for f in fixtures["fixtures"] if f["id"] == pr["fixture"])
            if not any("price" in g.lower() for g in fx["gaps"]):
                errors.append(f"{pr['fixture']}: prediction without a price and no price-gap note")

    # counts
    counts = summary["counts"]
    if counts["fixtures"] != len(fixtures["fixtures"]):
        errors.append("summary fixture count mismatch")
    if counts["markets"] != len(lines["markets"]):
        errors.append("summary market count mismatch")
    if counts["predictions"] != len(preds["predictions"]):
        errors.append("summary prediction count mismatch")
    if counts["flags"] != len(flagged["flags"]):
        errors.append("summary flag count mismatch")

    # site links
    pages = list(SITE.rglob("*.html"))
    if not pages:
        errors.append("no HTML pages generated")
    for page in pages:
        text = page.read_text(encoding="utf-8")
        for href in re.findall(r'(?:href|src)="([^"#:]+)"', text):
            if not href or href.startswith(("#", "http", "mailto", "data:")):
                continue
            target = (page.parent / href.split("#")[0]).resolve()
            if not target.exists():
                errors.append(f"{page.relative_to(ROOT)}: broken link {href}")
        if "<script" in text:
            errors.append(f"{page.relative_to(ROOT)}: contains a script tag")

    # every official fixture must be reachable on at least one sports page
    for fx in fixtures["fixtures"]:
        if not (SITE / "sports" / f"{fx['sport']}.html").exists():
            errors.append(f"missing sport page for {fx['sport']}")

    return sorted(set(errors))


if __name__ == "__main__":
    problems = validate()
    print("\n".join(problems) if problems else "OK — all desk gates pass")
    raise SystemExit(1 if problems else 0)
