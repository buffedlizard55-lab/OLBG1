#!/usr/bin/env python3
"""Validator gate for a0b04058 desk."""
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "a0b04058"
SITE_DIR = ROOT / "a0b04058"

errors=[]
warnings=[]

PUBLISHERS = {
    'api-web.nhle.com', 'www.nhl.com',
    'statsapi.mlb.com', 'www.mlb.com',
    'www.nba.com', 'cdn.nba.com',
    'www.euroleaguebasketball.net',
    'www.protennislive.com', 'www.atptour.com',
    'wtafiles.wtatennis.com', 'www.wtatennis.com',
    'www.wst.tv', 'www.pdc.tv',
    'www.eurohandball.com', 'ehfcl.eurohandball.com',
    'www.pcb.com.pk', 'www.icc-cricket.com',
    'www.nzc.nz', 'scoring.nzc.nz',
    'cricketireland.ie',
    'top14.lnr.fr', 'prod2.lnr.fr',
    'www.intrl.sport', 'www.nrl.com',
    'www.afl.com.au',
    'www.plusliga.pl', 'www.tauronliga.pl',
    'www.legavolley.it',
    'www.formula1.com', 'lolesports.com',
    'www.pgatour.com', 'www.europeantour.com',
    'www.lpga.com', 'www.gbgb.org.uk',
    'munster.gaa.ie', 'gaacork.ie',
    'www.maighcuilinn.com', 'www.unitedrugby.com', 'stats.unitedrugby.com',
    'www.stfinbarrsnhf.ie', 'www.bbc.com',
}

def is_official_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme == "https" and parsed.hostname in PUBLISHERS
    except:
        return False

def main():
    desk_path = DATA_DIR / "desk.json"
    if not desk_path.exists():
        print("VALIDATION FAILED: desk.json missing")
        sys.exit(1)
    desk = json.loads(desk_path.read_text(encoding="utf-8"))

    # Check counts
    fixtures = desk["fixtures"]
    if desk["counts"]["fixtures"] != len(fixtures):
        errors.append(f"fixtures count mismatch: {desk['counts']['fixtures']} vs {len(fixtures)}")

    # Check each fixture has official link and source
    for fp in fixtures:
        fi = fp["fixture"]
        if not fi.get("official_link", "").startswith("https://"):
            errors.append(f"{fi['key']}: official_link not HTTPS -> {fi.get('official_link')}")
        elif not is_official_url(fi["official_link"]):
            # Allow if host is in publishers, else error
            # For some, official_link may be cdn.nba.com schedule PDF which is allowed
            # Check hostname
            host = urlparse(fi["official_link"]).hostname
            if host not in PUBLISHERS:
                errors.append(f"{fi['key']}: official_link host not in allowlist -> {fi['official_link']}")
        # Check context non-empty
        if not fi.get("context"):
            errors.append(f"{fi['key']}: missing context")
        # Check olbg_hub
        if not fi.get("olbg_hub", "").startswith("https://www.olbg.com/"):
            errors.append(f"{fi['key']}: olbg_hub not OLBG -> {fi.get('olbg_hub')}")
        # Check priced
        if fp["priced"]:
            if not fp["markets"]:
                errors.append(f"{fi['key']}: priced but no markets")
            if not fp["winner_pick"]:
                errors.append(f"{fi['key']}: priced but no winner_pick")
            else:
                wp = fp["winner_pick"]
                # Check probability range
                p = wp["probability_exact"]
                if not (0 < p < 1):
                    errors.append(f"{fi['key']}: invalid prob {p}")
                # Check tier
                if wp["tier"] not in ("High","Medium","Low"):
                    errors.append(f"{fi['key']}: invalid tier {wp['tier']}")
                # Check in-window for High
                if wp["tier"] == "High":
                    # must be in-window
                    # compute american
                    if p >= 0.5:
                        amer = -round(p/(1-p)*100)
                    else:
                        amer = round((1-p)/p*100)
                    if not (-250 <= amer <= 10000):
                        errors.append(f"{fi['key']}: High pick out of window amer {amer}")
        else:
            if not fp["unpriced_reason"]:
                errors.append(f"{fi['key']}: unpriced but no reason")

    # Check predictions
    preds = desk.get("predictions", [])
    if len(preds) != desk["counts"]["predictions"]:
        errors.append(f"predictions count mismatch: {desk['counts']['predictions']} vs {len(preds)}")
    # Check each prediction >=30 words and unique
    seen_texts = set()
    for pr in preds:
        wc = len(pr["prediction_text"].split())
        if wc < 30:
            errors.append(f"{pr['id']}: too short {wc} words")
        if pr["prediction_text"] in seen_texts:
            errors.append(f"{pr['id']}: duplicate prediction text")
        seen_texts.add(pr["prediction_text"])
        # Check sources
        if not pr.get("sources"):
            errors.append(f"{pr['id']}: no sources")
        for url in pr.get("sources", []):
            if not url.startswith("https://"):
                errors.append(f"{pr['id']}: source not HTTPS {url}")
            elif not is_official_url(url):
                host = urlparse(url).hostname
                if host not in PUBLISHERS:
                    errors.append(f"{pr['id']}: source host not allowlisted {url}")

    # Check per-sport top5
    daily = desk.get("daily_top5", {})
    for sport, pids in daily.items():
        if len(pids) > 5:
            errors.append(f"{sport}: daily_top5 >5")
        # check all pids exist
        for pid in pids:
            if not any(x["id"]==pid for x in preds):
                errors.append(f"{sport}: daily_top5 pid {pid} not found in predictions")

    # Check flags
    flags = desk.get("flags", [])
    if desk["counts"]["flagged"] != len(flags):
        errors.append(f"flagged count mismatch {desk['counts']['flagged']} vs {len(flags)}")

    # Check site files exist
    required_pages = ["index.html","matches.html","markets.html","high-confidence.html","daily-top5.html","predictions.html","sources.html","flagged.html","repo-audit.html","sports.html","methodology.html","reverse-engineering.html","analysis.html"]
    for page in required_pages:
        if not (SITE_DIR / page).exists():
            errors.append(f"site page missing: {page}")

    # Check sports subpages
    for slug in desk["per_sport"].keys():
        if not (SITE_DIR / "sports" / f"{slug}.html").exists():
            errors.append(f"sport page missing: {slug}.html")

    # Check assets
    if not (SITE_DIR / "assets" / "style.css").exists():
        errors.append("assets/style.css missing")
    if not (SITE_DIR / "assets" / "app.js").exists():
        errors.append("assets/app.js missing")

    # Check CSVs
    if not (DATA_DIR / "fixtures.csv").exists():
        errors.append("fixtures.csv missing")
    if not (DATA_DIR / "markets.csv").exists():
        errors.append("markets.csv missing")

    if errors:
        print("VALIDATION FAILED")
        for e in errors:
            print(f"ERROR: {e}")
        sys.exit(1)
    else:
        print(f"VALIDATION PASSED: {len(fixtures)} fixtures, {len(preds)} predictions, {len(flags)} flags, {len(desk['sources'])} sources, 0 errors, {len(warnings)} warnings")
        for w in warnings:
            print(f"WARN: {w}")

if __name__ == "__main__":
    main()
