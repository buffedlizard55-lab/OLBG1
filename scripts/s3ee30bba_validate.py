#!/usr/bin/env python3
"""Strict automated validator for session 3ee30bba-olbg1 (/3ee30bba/ & data/3ee30bba/)."""
from __future__ import annotations

import csv
import json
import math
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from pipeline.config import EXCLUDED_NAMES, PUBLISHERS
from scripts.s3ee30bba_model import (
    BAND_MAX_AMERICAN,
    BAND_MIN_AMERICAN,
    HIGH_PROB_FLOOR,
    american_from_fair_decimal,
    verify_standings_conservation,
)

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "3ee30bba"
SITE_DIR = ROOT / "3ee30bba"


class DeskHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = False
        self.h1 = 0
        self.ids: list[str] = []
        self.links: list[str] = []
        self._in_tbody = 0
        self._in_tr = False
        self._in_td = False
        self._td_buf: list[str] = []
        self._row_links: list[str] = []
        self._row_tds: list[str] = []
        self.tbody_rows: list[tuple[list[str], list[str]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        d = dict(attrs)
        if tag == "title":
            self.title = True
        elif tag == "h1":
            self.h1 += 1
        if d.get("id"):
            self.ids.append(str(d["id"]))
        for k in ("href", "src"):
            if d.get(k):
                self.links.append(str(d[k]))
        if tag == "tbody":
            self._in_tbody += 1
        elif tag == "tr" and self._in_tbody > 0:
            self._in_tr = True
            self._row_links = []
            self._row_tds = []
        elif tag == "td" and self._in_tr:
            self._in_td = True
            self._td_buf = []
        if tag == "a" and self._in_tr and d.get("href"):
            self._row_links.append(str(d["href"]))

    def handle_data(self, data: str) -> None:
        if self._in_td:
            self._td_buf.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "td" and self._in_td:
            self._in_td = False
            self._row_tds.append("".join(self._td_buf).strip())
        elif tag == "tr" and self._in_tr:
            self._in_tr = False
            self.tbody_rows.append((self._row_tds, self._row_links))
        elif tag == "tbody" and self._in_tbody > 0:
            self._in_tbody -= 1


def is_official_sport_url(url: str) -> bool:
    u = urlsplit(url)
    return u.scheme == "https" and (u.hostname or "") in PUBLISHERS


def main() -> int:
    errors: list[str] = []

    def check(cond: bool, msg: str) -> None:
        if not cond:
            errors.append(msg)

    # 1. Closed-system standings conservation
    try:
        verify_standings_conservation()
    except Exception as exc:
        errors.append(f"Conservation check failed: {exc}")

    # 2. Load desk.json
    desk_path = DATA_DIR / "desk.json"
    if not desk_path.is_file():
        print("ERROR: missing data/3ee30bba/desk.json")
        return 1
    desk = json.loads(desk_path.read_text(encoding="utf-8"))
    as_of = desk["as_of_utc"]
    fixtures = desk["fixtures"]
    books = desk["books"]
    high_picks = desk["high_picks"]
    preds = desk["predictions"]

    check(len(desk["covered_sports"]) == 17, "Expected 17 covered sports")
    for s in desk["covered_sports"]:
        check(s["slug"] not in EXCLUDED_NAMES, f"Excluded sport in covered_sports: {s['slug']}")

    # 3. Fixture & pricing checks
    seen_fids = set()
    recounted_highs = []
    for f in fixtures:
        fid = f["id"]
        check(fid not in seen_fids, f"Duplicate fixture id {fid}")
        seen_fids.add(fid)
        check(f["sport"] not in EXCLUDED_NAMES, f"{fid}: excluded sport {f['sport']}")
        check(is_official_sport_url(f["official_url"]), f"{fid}: official_url not in allowlist -> {f['official_url']}")
        b = books.get(fid)
        check(b is not None, f"{fid}: missing book")
        if not b:
            continue
        if b["markets"]:
            check(bool(f["start_utc"]) and f["start_utc"] > as_of, f"{fid}: priced fixture lacks future start_utc")
            check(fid != "mlb-849799", "Conditional MLB Game 5 must not be priced")
            check(fid != "el-r7-69", "Quarantined Valencia fixture must not be priced")
            wp = b["winner_pick"]
            check(wp is not None, f"{fid}: priced book missing winner_pick")
            top_m0 = max(b["markets"][0]["outcomes"], key=lambda o: o["probability"])
            check(wp == top_m0, f"{fid}: winner_pick drifted from market[0] top outcome")
        else:
            check(b["winner_pick"] is None, f"{fid}: unpriced book has winner_pick")
            check(bool(f["withhold_reason"]), f"{fid}: unpriced fixture lacks withhold_reason")

        for m in b["markets"]:
            mass = math.fsum(o["probability"] for o in m["outcomes"])
            check(abs(mass - 1.0) < 1e-9, f"{m['id']}: probability mass {mass} != 1.0")
            for o in m["outcomes"]:
                pr = o["probability"]
                check(0.0 < pr < 1.0, f"{m['id']}: invalid probability {pr}")
                check(abs(o["fair_decimal"] * pr - 1.0) < 1e-9, f"{m['id']}: fair_decimal != 1/p")
                check(o["american"] == american_from_fair_decimal(o["fair_decimal"]), f"{m['id']}: american rounding mismatch")
                if o["confidence"] == "high":
                    recounted_highs.append((fid, m["id"], o["selection"]))
                    check(pr > HIGH_PROB_FLOOR, f"{m['id']}: High pick <= 70% ({pr})")
                    check(1.4 <= o["fair_decimal"] <= 101.0, f"{m['id']}: High pick outside decimal band ({o['fair_decimal']})")
                    check(BAND_MIN_AMERICAN <= o["american"] <= BAND_MAX_AMERICAN, f"{m['id']}: High pick outside US band ({o['american']})")
                if pr > 1.0 / 1.4:
                    check(o["confidence"] == "medium", f"{m['id']}: heavy chalk < -250 not capped at Medium")

    check(len(recounted_highs) == len(high_picks) == len(preds) == 13, f"Expected 13 High picks & predictions, got {len(recounted_highs)}/{len(high_picks)}/{len(preds)}")

    # 4. Prediction quality & 5-gram uniqueness
    hp_keys = {(h["fixture_id"], h["market_id"], h["selection"]): h for h in high_picks}
    pr_keys = {(p["fixture_id"], p["market_id"], p["selection"]) for p in preds}
    check(set(hp_keys) == pr_keys, "High picks and predictions do not form a 1-to-1 bijection")

    ngrams5: Counter[tuple[str, ...]] = Counter()
    for p in preds:
        hp = hp_keys.get((p["fixture_id"], p["market_id"], p["selection"]))
        if not hp:
            continue
        words = p["body"].split()
        check(len(words) >= 30, f"{p['id']}: only {len(words)} words (<30)")
        check(p["selection"] in p["body"], f"{p['id']}: selection '{p['selection']}' missing from body")
        check(hp["american_display"] in p["body"], f"{p['id']}: price {hp['american_display']} missing from body")
        check(f"{hp['probability']*100:.2f}%" in p["body"], f"{p['id']}: probability missing from body")
        check(len(p.get("players_cited", [])) >= 2, f"{p['id']}: fewer than 2 verified players cited")
        for pl in p.get("players_cited", []):
            last = pl.split()[-1]
            check(last in p["body"], f"{p['id']}: cited player '{pl}' missing from prose")
        check(bool(p.get("official_urls")) and all(is_official_sport_url(u) for u in p["official_urls"]), f"{p['id']}: invalid official_urls")
        toks = [re.sub(r"^[^\w]+|[^\w]+$", "", w.lower()) for w in words]
        toks = [t for t in toks if t]
        for idx in range(len(toks) - 4):
            ngrams5[tuple(toks[idx : idx + 5])] += 1

    dup5 = {k: v for k, v in ngrams5.items() if v > 1}
    check(not dup5, f"Duplicate 5-word phrases across predictions: {dup5}")

    # 5. CSV export checks
    with (DATA_DIR / "fixtures.csv").open(encoding="utf-8", newline="") as fh:
        fix_csv = list(csv.DictReader(fh))
    check(len(fix_csv) == len(fixtures), f"fixtures.csv row count {len(fix_csv)} != {len(fixtures)}")
    with (DATA_DIR / "markets.csv").open(encoding="utf-8", newline="") as fh:
        mkt_csv = list(csv.DictReader(fh))
    check(len(mkt_csv) == desk["counts"]["originated_outcomes"], f"markets.csv row count {len(mkt_csv)} != {desk['counts']['originated_outcomes']}")

    # 6. HTML structure, table rows, official links & relative routing
    html_pages = sorted(SITE_DIR.rglob("*.html"))
    check(len(html_pages) == 28, f"Expected 28 HTML pages under 3ee30bba/, found {len(html_pages)}")
    parsed_cache: dict[Path, DeskHTMLParser] = {}
    for page in html_pages:
        p = DeskHTMLParser()
        p.feed(page.read_text(encoding="utf-8"))
        parsed_cache[page] = p

    total_tbody_rows = 0
    for page, p in parsed_cache.items():
        rel = page.relative_to(ROOT).as_posix()
        check(p.title and p.h1 == 1, f"{rel}: invalid <title> or <h1> count ({p.h1})")
        check(len(p.ids) == len(set(p.ids)), f"{rel}: duplicate HTML element IDs")
        for r_idx, (tds, r_links) in enumerate(p.tbody_rows, 1):
            total_tbody_rows += 1
            check(all(bool(cell) for cell in tds), f"{rel} row #{r_idx}: empty <td> cell found")
            check(any(is_official_sport_url(u) for u in r_links), f"{rel} row #{r_idx}: missing allowlisted official https:// source link")
        for href in p.links:
            u = urlsplit(href)
            if u.scheme or u.netloc:
                check(u.scheme not in ("javascript", "data"), f"{rel}: unsafe scheme in {href}")
                continue
            check(not u.path.startswith("/"), f"{rel}: root-escaping link {href}")
            target = (page.parent / unquote(u.path)).resolve() if u.path else page
            try:
                target.relative_to(ROOT)
            except ValueError:
                errors.append(f"{rel}: link escapes repository -> {href}")
                continue
            if target.is_dir():
                target = target / "index.html"
            check(target.is_file(), f"{rel}: broken relative link -> {href}")
            if u.fragment and target.suffix == ".html" and target in parsed_cache:
                check(unquote(u.fragment) in parsed_cache[target].ids, f"{rel}: missing fragment #{u.fragment} in {href}")

    if errors:
        for e in errors:
            print("ERROR:", e)
        print(f"VALIDATION FAILED ({len(errors)} error(s))")
        return 1

    print(
        f"VALIDATION PASSED — {len(html_pages)} HTML pages, {total_tbody_rows} source-linked table rows, "
        f"{len(fixtures)} fixtures ({desk['counts']['priced_fixtures']} priced), "
        f"{desk['counts']['originated_markets']} markets, {len(high_picks)} in-window High picks, 0 errors."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
