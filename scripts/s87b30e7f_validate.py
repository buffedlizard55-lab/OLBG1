#!/usr/bin/env python3
"""Strict zero-dependency verification suite for Session 87b30e7f (T87B3)."""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "87b30e7f"
SITE_DIR = ROOT / "87b30e7f"
REPORT_HTML = ROOT / "reports" / "SESSION_87B30E7F.html"
REPORT_MD = ROOT / "reports" / "SESSION_87B30E7F.md"

EXPECTED_15_SPORTS = {
    "golf",
    "volleyball",
    "rugby-union",
    "cricket",
    "snooker",
    "darts",
    "baseball",
    "gaelic-sports",
    "greyhounds",
    "tennis",
    "motor-racing",
    "handball",
    "ice-hockey",
    "basketball",
    "rugby-league",
}

OFFICIAL_HOSTS = {
    "ak-static.cms.nba.com",
    "www.nba.com",
    "statsapi.mlb.com",
    "api-web.nhle.com",
    "wtafiles.wtatennis.com",
    "www.protennislive.com",
    "www.atptour.com",
    "www.lpga.com",
    "www.europeantour.com",
    "www.pgatour.com",
    "www.motogp.com",
    "www.formula1.com",
    "www.nascar.com",
    "www.nrl.com",
    "www.unitedrugby.com",
    "stats.unitedrugby.com",
    "www.cricket.com.au",
    "www.icc-cricket.com",
    "www.bcci.tv",
    "www.wst.tv",
    "play.wst.tv",
    "www.pdc.tv",
    "www.legavolley.it",
    "www.lnh.fr",
    "www.h-bw.de",
    "www.rhein-neckar-loewen.de",
    "www.gaa.ie",
    "munster.gaa.ie",
    "www.galwaygaa.ie",
    "www.gbgb.org.uk",
    "www.dunstallpark-greyhounds.co.uk",
    "www.euroleaguebasketball.net",
}


class TableAndLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.ids: list[str] = []
        self._tbody = 0
        self._in_tr = False
        self._cur_row: list[str] = []
        self.tbody_rows: list[list[str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        d = dict(attrs)
        if d.get("id"):
            self.ids.append(str(d["id"]))
        if tag == "tbody":
            self._tbody += 1
        elif tag == "tr" and self._tbody > 0:
            self._in_tr = True
            self._cur_row = []
        for k in ("href", "src"):
            if d.get(k) is not None:
                val = str(d[k])
                self.links.append(val)
                if tag == "a" and k == "href" and self._in_tr:
                    self._cur_row.append(val)

    def handle_endtag(self, tag: str) -> None:
        if tag == "tr" and self._in_tr:
            self._in_tr = False
            self.tbody_rows.append(self._cur_row)
        elif tag == "tbody" and self._tbody > 0:
            self._tbody -= 1


def validate_desk() -> list[str]:
    errors: list[str] = []

    for fn in (
        "olbg_taxonomy.json",
        "sources.json",
        "fixtures.json",
        "lines.json",
        "predictions.json",
        "flagged.json",
        "repo_audit.json",
        "summary.json",
        "matches.csv",
    ):
        if not (DATA_DIR / fn).is_file():
            errors.append(f"Missing data artifact: data/87b30e7f/{fn}")
    if errors:
        return errors

    tax = json.loads((DATA_DIR / "olbg_taxonomy.json").read_text(encoding="utf-8"))
    fx_doc = json.loads((DATA_DIR / "fixtures.json").read_text(encoding="utf-8"))
    ln_doc = json.loads((DATA_DIR / "lines.json").read_text(encoding="utf-8"))
    pr_doc = json.loads((DATA_DIR / "predictions.json").read_text(encoding="utf-8"))
    fl_doc = json.loads((DATA_DIR / "flagged.json").read_text(encoding="utf-8"))
    au_doc = json.loads((DATA_DIR / "repo_audit.json").read_text(encoding="utf-8"))

    covered_slugs = {s["slug"] for s in tax["covered_sports"]}
    if covered_slugs != EXPECTED_15_SPORTS or tax["covered_count"] != 15:
        errors.append(f"Taxonomy mismatch: {covered_slugs}")

    fixtures = fx_doc["fixtures"]
    lines = {l["id"]: l for l in ln_doc["lines"]}
    preds = {p["id"]: p for p in pr_doc["predictions"]}

    if len(fixtures) != 75 or len(lines) != 75 or len(preds) != 75:
        errors.append(f"Expected 75 fixtures/lines/predictions, got {len(fixtures)}/{len(lines)}/{len(preds)}")

    by_sport = Counter(f["sport"] for f in fixtures)
    for sp in EXPECTED_15_SPORTS:
        if by_sport[sp] != 5:
            errors.append(f"Sport {sp} has {by_sport[sp]} fixtures instead of 5")
    for sp in by_sport:
        if sp not in EXPECTED_15_SPORTS:
            errors.append(f"Out-of-scope sport leaked: {sp}")

    ngrams: Counter[tuple[str, ...]] = Counter()
    high_count = 0

    for f in fixtures:
        fid = f["id"]
        if f["start_utc"] < "2026-10-24T00:00:00Z":
            errors.append(f"{fid}: start_utc {f['start_utc']} is not strictly >= 2026-10-24T00:00:00Z")
        for url_key in ("official_source_url", "secondary_source_url"):
            u = f[url_key]
            parsed = urlparse(u)
            if parsed.scheme != "https" or parsed.hostname not in OFFICIAL_HOSTS:
                errors.append(f"{fid}: {url_key} not in official HTTPS allowlist -> {u}")
        if not f["olbg_url"].startswith("https://www.olbg.com/betting-tips/"):
            errors.append(f"{fid}: invalid olbg_url {f['olbg_url']}")
        for k, v in f.get("blank_values", {}).items():
            if v != "":
                errors.append(f"{fid}: unconfirmed field {k} must be blank (''), got {v!r}")

        ln = lines.get(fid)
        pr = preds.get(fid)
        if not ln or not pr:
            errors.append(f"{fid}: missing line or prediction")
            continue

        if len(ln["markets"]) != 4:
            errors.append(f"{fid}: expected 4 markets, got {len(ln['markets'])}")
        for m in ln["markets"]:
            prob_sum = sum(o["probability"] for o in m["outcomes"])
            if abs(prob_sum - 1.0) > 1e-5:
                errors.append(f"{fid}/{m['key']}: probability sum {prob_sum} != 1.0")
            for o in m["outcomes"]:
                if not (0.005 < o["probability"] < 0.995):
                    errors.append(f"{fid}/{m['key']}: implausible probability {o['probability']}")
                if o["fair_decimal"] < 1.01 or o["book_decimal"] < 1.01:
                    errors.append(f"{fid}/{m['key']}: invalid decimal odds")

        if ln["confidence"] == "high":
            high_count += 1
            if not (-250 <= ln["pick_fair_american"] <= 10000):
                errors.append(f"{fid}: high pick fair_american {ln['pick_fair_american']} outside [-250, +10000]")
            if not (-250 <= ln["pick_book_american"] <= 10000):
                errors.append(f"{fid}: high pick book_american {ln['pick_book_american']} outside [-250, +10000]")
            if ln["pick_probability"] > 0.70:
                errors.append(f"{fid}: high pick zero-vig probability {ln['pick_probability']} > 0.70 chalk cap")

        txt = pr["prediction"]
        words = txt.split()
        if len(words) < 30:
            errors.append(f"{fid}: prediction word count {len(words)} < 30")
        if re.search(r"model|verif", txt, re.IGNORECASE):
            errors.append(f"{fid}: prediction contains forbidden substring model/verified")
        if pr["recommended_selection"].lower() not in txt.lower():
            errors.append(f"{fid}: recommended_selection {pr['recommended_selection']!r} not stated in prediction prose")

        toks = [re.sub(r"^[^\w]+|[^\w]+$", "", w.lower()) for w in words]
        toks = [t for t in toks if t]
        for idx in range(len(toks) - 5):
            ngrams[tuple(toks[idx : idx + 6])] += 1

    dup_ngrams = {k: c for k, c in ngrams.items() if c > 1}
    if dup_ngrams:
        errors.append(f"Duplicate 6-word n-grams in predictions: {dup_ngrams}")

    if not (25 <= high_count <= 50):
        errors.append(f"Unexpected high-confidence count {high_count}")

    for item in fl_doc["blank_unconfirmed_items"]:
        if item["blank_value"] != "":
            errors.append(f"Flagged item {item['flag_id']} blank_value is not ''")
        if not item["official_source_url"].startswith("https://"):
            errors.append(f"Flagged item {item['flag_id']} lacks HTTPS official source")

    if len(au_doc["findings"]) < 8:
        errors.append("Repo audit has fewer than 8 adjudicated findings")

    with (DATA_DIR / "matches.csv").open(encoding="utf-8", newline="") as fh:
        csv_rows = list(csv.DictReader(fh))
    if len(csv_rows) != 75:
        errors.append(f"CSV export has {len(csv_rows)} rows instead of 75")

    # Validate all 22 HTML pages (6 top-level + 15 sport pages + 1 report HTML)
    html_pages = [
        SITE_DIR / "index.html",
        SITE_DIR / "picks.html",
        SITE_DIR / "predictions.html",
        SITE_DIR / "flagged.html",
        SITE_DIR / "audit.html",
        SITE_DIR / "methodology.html",
        *[SITE_DIR / "sports" / f"{sp}.html" for sp in sorted(EXPECTED_15_SPORTS)],
        REPORT_HTML,
    ]
    if not REPORT_MD.is_file():
        errors.append("Missing reports/SESSION_87B30E7F.md")

    parsed_cache: dict[Path, TableAndLinkParser] = {}
    for page in html_pages:
        if not page.is_file():
            errors.append(f"Missing HTML page: {page.relative_to(ROOT)}")
            continue
        p = TableAndLinkParser()
        p.feed(page.read_text(encoding="utf-8"))
        parsed_cache[page.resolve()] = p
        if len(p.ids) != len(set(p.ids)):
            errors.append(f"{page.relative_to(ROOT)}: duplicate HTML element IDs")
        for r_idx, row_hrefs in enumerate(p.tbody_rows, 1):
            if not any(h.startswith("https://") for h in row_hrefs):
                errors.append(f"{page.relative_to(ROOT)}: tbody row #{r_idx} lacks HTTPS source link")

    for page, p in parsed_cache.items():
        rel = page.relative_to(ROOT).as_posix()
        for href in p.links:
            if not href:
                errors.append(f"{rel}: empty href/src")
                continue
            if href.startswith("http://"):
                errors.append(f"{rel}: non-HTTPS external link -> {href}")
                continue
            if href.startswith(("https://", "mailto:", "tel:", "#")):
                if href.startswith("#") and href[1:] and href[1:] not in p.ids:
                    errors.append(f"{rel}: broken same-page fragment {href}")
                continue
            clean, _, frag = href.partition("#")
            clean = clean.split("?", 1)[0]
            dest = (page.parent / clean).resolve()
            if dest.is_dir():
                dest = dest / "index.html"
            try:
                dest.relative_to(ROOT.resolve())
            except ValueError:
                errors.append(f"{rel}: relative link escapes repo root -> {href}")
                continue
            if not dest.is_file():
                errors.append(f"{rel}: broken relative link -> {href}")
                continue
            if frag and dest in parsed_cache and frag not in parsed_cache[dest].ids:
                errors.append(f"{rel}: broken cross-page fragment -> {href}")

    return errors


def main() -> int:
    errs = validate_desk()
    if errs:
        for err in errs:
            print("FAIL:", err)
        return 1
    print("PASS: Session 87b30e7f desk validated (15 sports, 75 upcoming fixtures, 300 markets, 75 unique predictions, 22 HTML pages).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
