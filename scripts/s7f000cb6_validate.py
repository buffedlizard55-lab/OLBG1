#!/usr/bin/env python3
"""Strict automated verification gate for session 7f000cb6 data, lines, predictions, and HTML."""
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
sys.path.insert(0, str(ROOT))
from pipeline.config import EXCLUDED_NAMES, PUBLISHERS, SPORT_INDEX  # noqa: E402

SESSION_ID = "7f000cb6"
DATA_DIR = ROOT / "data" / SESSION_ID
SITE_DIR = ROOT / SESSION_ID


class RowAndLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self._tbody = 0
        self._tr = 0
        self._curr_row: list[str] = []
        self.tbody_rows: list[list[str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        d = dict(attrs)
        if tag == "tbody":
            self._tbody += 1
        elif tag == "tr" and self._tbody > 0:
            self._tr += 1
            self._curr_row = []

        if tag == "a" and d.get("href"):
            href = str(d["href"])
            self.links.append(href)
            if self._tr > 0:
                self._curr_row.append(href)
        elif tag in ("link", "script", "img"):
            t = d.get("href") or d.get("src")
            if t:
                self.links.append(str(t))

    def handle_endtag(self, tag: str) -> None:
        if tag == "tr" and self._tr > 0:
            self._tr -= 1
            self.tbody_rows.append(self._curr_row)
        elif tag == "tbody" and self._tbody > 0:
            self._tbody -= 1


def check_official(url: str, ctx: str, errors: list[str]) -> None:
    p = urlparse(url)
    if p.scheme != "https" or not p.hostname or p.hostname not in PUBLISHERS:
        errors.append(f"{ctx}: non-PUBLISHERS or non-https official_url '{url}'")


def main() -> int:
    errors: list[str] = []

    fixtures_doc = json.loads((DATA_DIR / "fixtures.json").read_text(encoding="utf-8"))
    lines_doc = json.loads((DATA_DIR / "lines.json").read_text(encoding="utf-8"))
    preds_doc = json.loads((DATA_DIR / "predictions.json").read_text(encoding="utf-8"))
    sources_doc = json.loads((DATA_DIR / "sources.json").read_text(encoding="utf-8"))
    audit_doc = json.loads((DATA_DIR / "repo_audit.json").read_text(encoding="utf-8"))

    fixtures = fixtures_doc["fixtures"]
    books = {b["fixture_id"]: b for b in lines_doc["books"]}
    preds = preds_doc["predictions"]

    # 1. Sport scope checks
    observed_sports = {f["sport"] for f in fixtures}
    expected_sports = set(SPORT_INDEX.keys())
    if observed_sports != expected_sports:
        errors.append(f"Sport coverage mismatch: missing={expected_sports - observed_sports}, extra={observed_sports - expected_sports}")
    for f in fixtures:
        if f["sport"] in EXCLUDED_NAMES:
            errors.append(f"Excluded sport found: {f['id']} -> {f['sport']}")
        check_official(f["official_url"], f"fixture {f['id']}", errors)

    for s in sources_doc["sources"]:
        check_official(s["official_url"], f"source {s['id']}", errors)
    for a in audit_doc["findings"]:
        check_official(a["official_url"], f"audit {a['id']}", errors)

    # 2. Pricing & High-confidence bijection checks
    high_outcomes: list[tuple[str, str]] = []
    for f in fixtures:
        b = books.get(f["id"])
        if not b:
            errors.append(f"Missing line book for {f['id']}")
            continue
        check_official(b["official_url"], f"book {f['id']}", errors)
        if b["status"] == "priced":
            if not b.get("winner_pick"):
                errors.append(f"Priced book {f['id']} missing winner_pick")
            for m in b["markets"]:
                check_official(m["official_url"], f"market {m['market_id']}", errors)
                prob_sum = sum(o["probability"] for o in m["outcomes"])
                if abs(prob_sum - 1.0) > 1e-3:
                    errors.append(f"Market {m['market_id']} probabilities sum to {prob_sum}")
                for o in m["outcomes"]:
                    if o["confidence"] == "High":
                        high_outcomes.append((f["id"], o["selection"]))
                        if not (0.7000 < o["probability"] <= 0.7142857):
                            errors.append(f"High outcome {f['id']} {o['selection']} prob {o['probability']} outside (0.70, 0.7143]")
                        if not (-250 <= o["american_odds"] <= 10000):
                            errors.append(f"High outcome {f['id']} {o['selection']} US odds {o['american_odds']} outside [-250, +10000]")
                        if f["flags"]:
                            errors.append(f"Flagged fixture {f['id']} received High grade")
        else:
            if not b.get("unpriced_reason"):
                errors.append(f"Unpriced book {f['id']} missing unpriced_reason")

    pred_pairs = [(p["match_id"], p["selection"]) for p in preds]
    if set(high_outcomes) != set(pred_pairs) or len(high_outcomes) != len(preds):
        errors.append(f"High outcomes {high_outcomes} != predictions {pred_pairs}")

    # 3. Prediction writing quality & n-gram uniqueness checks
    ng5: Counter[tuple[str, ...]] = Counter()
    ng6: Counter[tuple[str, ...]] = Counter()
    fx_map = {f["id"]: f for f in fixtures}
    for p in preds:
        check_official(p["official_url"], f"prediction {p['id']}", errors)
        words = p["text"].split()
        if len(words) < 30:
            errors.append(f"{p['id']}: fewer than 30 words ({len(words)})")
        fx = fx_map[p["match_id"]]
        for team_tok in (fx["home"].split()[0], fx["away"].split()[0]):
            if team_tok not in p["text"]:
                errors.append(f"{p['id']}: missing team reference '{team_tok}' in text")
        for pl in p["verified_players"]:
            last = pl.split()[-1]
            if last not in p["text"]:
                errors.append(f"{p['id']}: missing verified player '{pl}' in text")
        toks = [re.sub(r"^[^\w]+|[^\w]+$", "", w.lower()) for w in words]
        toks = [t for t in toks if t]
        for i in range(len(toks) - 4):
            ng5[tuple(toks[i : i + 5])] += 1
        for i in range(len(toks) - 5):
            ng6[tuple(toks[i : i + 6])] += 1

    dup5 = {k: v for k, v in ng5.items() if v > 1}
    dup6 = {k: v for k, v in ng6.items() if v > 1}
    if dup5 or dup6:
        errors.append(f"Duplicate n-grams in High predictions: 5-gram={dup5}, 6-gram={dup6}")

    # 4. CSV parity check
    for csv_p in (DATA_DIR / "matches.csv", SITE_DIR / "exports" / "matches.csv"):
        with csv_p.open(encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
        if len(rows) != len(fixtures):
            errors.append(f"{csv_p}: expected {len(fixtures)} rows, got {len(rows)}")

    # 5. HTML link resolution + official source link on EVERY tbody row across all pages
    html_files = sorted(SITE_DIR.rglob("*.html"))
    if len(html_files) != 9 + 17:
        errors.append(f"Expected 26 HTML pages under {SITE_DIR}, found {len(html_files)}")
    total_tbody_rows = 0
    for hp in html_files:
        parser = RowAndLinkParser()
        parser.feed(hp.read_text(encoding="utf-8"))
        for href in parser.links:
            if href.startswith(("#", "http://", "https://", "mailto:", "data:")):
                continue
            clean = href.split("#", 1)[0].split("?", 1)[0]
            if not clean:
                continue
            target = (hp.parent / clean).resolve()
            if not target.exists():
                errors.append(f"{hp.relative_to(ROOT)}: broken relative link '{href}' -> {target}")
        for idx, rlinks in enumerate(parser.tbody_rows, 1):
            total_tbody_rows += 1
            has_official = any(
                urlparse(u).scheme == "https" and urlparse(u).hostname in PUBLISHERS
                for u in rlinks
            )
            if not has_official:
                errors.append(f"{hp.relative_to(ROOT)} tbody row #{idx}: missing allowlisted official_url link (links={rlinks})")

    print(
        f"7f000cb6 validation: {len(fixtures)} fixtures | {lines_doc['market_count']} markets | "
        f"{len(preds)} High picks | {len(html_files)} HTML pages | {total_tbody_rows} table rows verified"
    )
    if errors:
        for err in errors[:30]:
            print("  ERROR:", err)
        return 1
    print("ALL 7f000cb6 CHECKS PASSED (0 errors)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
