#!/usr/bin/env python3
"""
Strict Automated Audit & Quality Validator for Session c17a9192-olbg1.
Exits non-zero if any single integrity, scope, provenance, math, prose, or HTML check fails.
"""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "c17a9192"
SITE_DIR = ROOT / "c17a9192"

EXPECTED_SPORTS = {
    "Tennis", "Basketball", "Golf", "Cricket", "Snooker", "Rugby Union", "Rugby League",
    "Baseball", "Ice Hockey", "Motor Racing", "Darts", "Handball", "Volleyball",
    "Aussie Rules", "eSports", "Gaelic Football", "Greyhounds",
}

FORBIDDEN_SPORT_TERMS = {
    "soccer", "american football", "nfl", "boxing", "ufc", "mma",
    "hurling", "horse racing", "cycling", "specials",
}

OFFICIAL_HOST_ALLOWLIST = {
    "statsapi.mlb.com", "www.mlb.com", "mlb.com",
    "api-web.nhle.com", "www.nhl.com", "nhl.com",
    "www.ice.hockey", "ice.hockey",
    "www.nba.com", "nba.com",
    "www.euroleaguebasketball.net", "euroleaguebasketball.net",
    "www.championsleague.basketball", "championsleague.basketball",
    "www.kbl.or.kr", "kbl.or.kr",
    "www.atptour.com", "atptour.com",
    "www.wtatennis.com", "wtatennis.com",
    "www.wst.tv", "wst.tv",
    "www.pdc.tv", "pdc.tv",
    "ehfcl.eurohandball.com", "ehfeuro.eurohandball.com", "www.eurohandball.com", "eurohandball.com",
    "www.volleyball-bundesliga.de", "volleyball-bundesliga.de",
    "www.legavolleyfemminile.it", "legavolleyfemminile.it",
    "www.tauronliga.pl", "tauronliga.pl", "www.plusliga.pl", "www.pzps.pl",
    "www.lnv.fr", "lnv.fr",
    "www.cev.eu", "cev.eu",
    "www.icc-cricket.com", "icc-cricket.com",
    "scoring.nzc.nz", "www.nzc.nz", "cricket.co.za",
    "www.cricket.com.au", "cricket.com.au",
    "www.ecb.co.uk", "ecb.co.uk",
    "top14.lnr.fr", "prod2.lnr.fr", "www.lnr.fr",
    "www.unitedrugby.com", "unitedrugby.com", "www.sixnationsrugby.com",
    "www.allblacks.com", "allblacks.com",
    "www.world.rugby", "world.rugby",
    "www.nrl.com", "nrl.com",
    "www.superleague.co.uk", "superleague.co.uk",
    "www.pgatour.com", "pgatour.com",
    "www.europeantour.com", "europeantour.com",
    "www.lpga.com", "lpga.com", "ladieseuropeantour.com",
    "sunshinetour.com", "pga.org.au", "www.jgto.org", "www.asiantour.com",
    "www.formula1.com", "formula1.com", "www.fia.com",
    "www.afl.com.au", "afl.com.au",
    "lolesports.com", "www.lolesports.com",
    "www.gaa.ie", "gaa.ie", "munster.gaa.ie", "gaacork.ie", "www.galwaygaa.ie",
    "www.gbgb.org.uk", "gbgb.org.uk",
}

FORBIDDEN_SCRAPER_HOSTS = {
    "en.wikipedia.org", "wikipedia.org", "kalshi.com", "www.kalshi.com",
    "espn.com", "www.espn.com", "flashscore.com", "www.flashscore.com",
    "sofascore.com", "www.sofascore.com", "oddschecker.com", "www.oddschecker.com",
    "localhost", "127.0.0.1",
}


class TableAndLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_tbody = False
        self.in_tr = False
        self.row_links: list[str] = []
        self.all_rows: list[list[str]] = []
        self.all_hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        ad = dict(attrs)
        if tag == "tbody":
            self.in_tbody = True
        elif tag == "tr" and self.in_tbody:
            self.in_tr = True
            self.row_links = []
        elif tag == "a":
            href = ad.get("href") or ""
            self.all_hrefs.append(href)
            if self.in_tr and href.startswith("https://"):
                self.row_links.append(href)

    def handle_endtag(self, tag: str) -> None:
        if tag == "tr" and self.in_tr:
            self.in_tr = False
            self.all_rows.append(self.row_links)
        elif tag == "tbody":
            self.in_tbody = False


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    matches = json.loads((DATA_DIR / "matches.json").read_text(encoding="utf-8"))
    lines = json.loads((DATA_DIR / "lines.json").read_text(encoding="utf-8"))
    preds = json.loads((DATA_DIR / "predictions.json").read_text(encoding="utf-8"))
    flagged = json.loads((DATA_DIR / "flagged.json").read_text(encoding="utf-8"))
    audit = json.loads((DATA_DIR / "repo_audit.json").read_text(encoding="utf-8"))

    # 1. Event count, uniqueness, sport taxonomy
    if len(matches) != 217:
        fail(f"Expected 217 reconciled events, found {len(matches)}")
    ids = [m["id"] for m in matches]
    if len(ids) != len(set(ids)):
        fail("Duplicate event IDs detected in matches.json")

    observed_sports = {m["sport"] for m in matches}
    if observed_sports != EXPECTED_SPORTS:
        fail(f"Sport set mismatch: diff = {observed_sports ^ EXPECTED_SPORTS}")

    for m in matches:
        if m["sport"].lower() in FORBIDDEN_SPORT_TERMS:
            fail(f"Excluded sport leaked: {m['sport']}")

    # 2. Official governing-body URL host allowlist check across all 217 rows
    for m in matches:
        if not m["official_sources"]:
            fail(f"Event {m['id']} has empty official_sources")
        for s in m["official_sources"]:
            host = urlparse(s["url"]).netloc.lower()
            if host in FORBIDDEN_SCRAPER_HOSTS:
                fail(f"Forbidden non-official host {host} on {m['id']}")
            if host not in OFFICIAL_HOST_ALLOWLIST:
                fail(f"Host {host} not in official governing-body allowlist on {m['id']}: {s['url']}")

    # 3. Verification honesty & high-confidence gating
    high_events = [m for m in matches if m["confidence"] == "high"]
    for m in high_events:
        if m["verification_status"] != "verified":
            fail(f"High-confidence pick {m['id']} is not full 'verified' ({m['verification_status']})")
        if not (m["venue"] and m["stat_a"] and m["stat_b"]):
            fail(f"High-confidence pick {m['id']} is missing required confirmed venue/stats")
        if not m["start_utc"] and m["sport"] != "Tennis":
            fail(f"Non-rolling high-confidence pick {m['id']} is missing start_utc")

    for m in matches:
        if m["verification_status"] == "unverified":
            if not m["flags"]:
                fail(f"Unverified event {m['id']} lacks explanatory flag reason")
            if m["stat_a"] and m["stat_b"] and m["start_utc"] and m["venue"]:
                fail(f"Unverified event {m['id']} has no blank fields")

    # 4. Originated lines completeness & booksum bounds
    if len(lines) != 217:
        fail(f"Expected 217 originated line records, found {len(lines)}")
    lines_map = {ln["event_id"]: ln for ln in lines}
    for m in matches:
        ln = lines_map.get(m["id"])
        if not ln:
            fail(f"Missing originated lines for {m['id']}")
        w_bs = ln["winner"]["booksum_pct"]
        if not (101.0 <= w_bs <= 119.5):
            fail(f"Out-of-bounds winner booksum {w_bs}% on {m['id']}")
        if m["kind"] in ("h2h_2way", "h2h_3way"):
            if not ln.get("handicap") or not ln.get("total"):
                fail(f"Missing secondary spread/total markets on {m['id']}")
        else:
            if not ln.get("field_board") or len(ln["field_board"]["runners"]) < 4:
                fail(f"Missing multi-runner board on {m['id']}")

    # 5. High-confidence predictions quality, >=30 words, uniqueness (0 shared 6-grams), exact odds sync
    if len(preds) != len(high_events):
        fail(f"High prediction count {len(preds)} != high event count {len(high_events)}")

    seen_6grams: dict[tuple[str, ...], str] = {}
    for p in preds:
        words = p["prediction_text"].split()
        if len(words) < 30:
            fail(f"Prediction {p['event_id']} too short ({len(words)} words < 30)")
        dec_str = f"{p['originated_decimal']:.2f}"
        if dec_str not in p["prediction_text"]:
            fail(f"Prediction {p['event_id']} prose missing exact originated decimal odds {dec_str}")
        if not p["verified_evidence"]:
            fail(f"Prediction {p['event_id']} missing verified_evidence[]")
        norm_tokens = [re.sub(r"[^a-z0-9]+", "", w.lower()) for w in words if re.sub(r"[^a-z0-9]+", "", w.lower())]
        local_seen = set()
        for i in range(len(norm_tokens) - 5):
            gram = tuple(norm_tokens[i : i + 6])
            if gram in local_seen:
                continue
            local_seen.add(gram)
            if gram in seen_6grams:
                fail(f"Repeated 6-word template phrase {gram} shared between {seen_6grams[gram]} and {p['event_id']}")
            seen_6grams[gram] = p["event_id"]

    # 6. HTML Pages audit: every single table body row across all 24 HTML files MUST contain >=1 official external link,
    #    and every relative link must resolve cleanly on disk!
    html_files = sorted(SITE_DIR.rglob("*.html"))
    if len(html_files) != 24:
        fail(f"Expected 24 static HTML pages (7 core + 17 sport subpages), found {len(html_files)}")

    total_checked_rows = 0
    for hf in html_files:
        raw = hf.read_text(encoding="utf-8")
        if "localhost" in raw or "127.0.0.1" in raw:
            fail(f"Forbidden localhost reference in {hf}")
        parser = TableAndLinkParser()
        parser.feed(raw)
        for idx, rlinks in enumerate(parser.all_rows):
            total_checked_rows += 1
            if not rlinks:
                fail(f"Table row #{idx+1} in {hf.relative_to(ROOT)} lacks a clickable external official link!")
        for href in parser.all_hrefs:
            if not href or href.startswith(("https://", "http://", "#", "mailto:")):
                continue
            clean = href.split("#")[0].split("?")[0]
            target = (hf.parent / clean).resolve()
            if not target.exists():
                fail(f"Broken relative link '{href}' in {hf.relative_to(ROOT)} -> {target}")

    print(
        f"PASS: 217 events across all 17 sports | 100% official allowlist | "
        f"{len(preds)} unique human high-confidence predictions (min {min(p['word_count'] for p in preds)}w, 0 shared 6-grams) | "
        f"{len(audit)} repo audit items | {len(flagged['olbg_irregularities'])} OLBG defects | "
        f"{len(html_files)} HTML pages & {total_checked_rows} table rows verified with 0 broken links!"
    )


if __name__ == "__main__":
    main()
