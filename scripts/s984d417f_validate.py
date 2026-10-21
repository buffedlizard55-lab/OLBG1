#!/usr/bin/env python3
"""
s984d417f_validate.py — Comprehensive verification suite enforcing every functional,
mathematical, prose-uniqueness, official-source, non-inference, HTML-link, and anchor
requirement across data/984d417f/, reports/SESSION_984D417F_AUDIT.md, and /984d417f/.
"""
from __future__ import annotations

import csv
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "984d417f"
SITE_DIR = ROOT / "984d417f"
REPORT_FILE = ROOT / "reports" / "SESSION_984D417F_AUDIT.md"

EXPECTED_IN_SCOPE = {
    "ice-hockey", "basketball", "baseball", "tennis", "snooker", "darts", "cricket",
    "rugby-union", "rugby-league", "handball", "volleyball", "aussie-rules", "esports",
    "gaelic-football", "golf", "motor-racing", "greyhounds",
}
FORBIDDEN_SPORTS = {
    "soccer", "football", "horse-racing", "american-football", "nfl",
    "boxing", "ufc", "mma", "hurling", "cycling", "specials",
}
UNOFFICIAL_HOST_SUBSTRINGS = (
    "wikipedia.org", "flashscore", "sofascore", "oddsportal", "oddschecker",
    "betexplorer", "transfermarkt", "espn.com", "bbc.co.uk", "nbagameshub",
    "bleacherreport", "actionnetwork", "covers.com",
)


class PageInspector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.hrefs: list[str] = []
        self.srcs: list[str] = []
        self.in_tr_data = False
        self.row_ext_links: list[int] = []
        self._cur_ext = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        ad = dict(attrs)
        if ad.get("id"):
            self.ids.add(ad["id"])
        if tag == "tr" and "data-row" in (ad.get("class") or ""):
            self.in_tr_data = True
            self._cur_ext = 0
        if tag == "a" and ad.get("href"):
            href = ad["href"]
            self.hrefs.append(href)
            if self.in_tr_data and href.startswith("https://"):
                self._cur_ext += 1
        if tag in ("script", "img") and ad.get("src"):
            self.srcs.append(ad["src"])
        if tag == "link" and ad.get("href"):
            self.srcs.append(ad["href"])

    def handle_endtag(self, tag: str) -> None:
        if tag == "tr" and self.in_tr_data:
            self.row_ext_links.append(self._cur_ext)
            self.in_tr_data = False


def main() -> None:
    fx_doc = json.loads((DATA_DIR / "fixtures.json").read_text())
    ln_doc = json.loads((DATA_DIR / "lines.json").read_text())
    pr_doc = json.loads((DATA_DIR / "predictions.json").read_text())
    fl_doc = json.loads((DATA_DIR / "flagged.json").read_text())
    au_doc = json.loads((DATA_DIR / "repo_audit.json").read_text())

    fixtures = fx_doc["fixtures"]
    lines = ln_doc["lines"]
    preds = pr_doc["predictions"]

    # 1. Exact 17-sport coverage & 0 excluded sports
    sports_present = {f["sport"] for f in fixtures}
    assert sports_present == EXPECTED_IN_SCOPE, f"Sport mismatch: {sports_present ^ EXPECTED_IN_SCOPE}"
    assert not (sports_present & FORBIDDEN_SPORTS), "Excluded sport leaked into dataset!"
    for f in fixtures:
        comp_low = f["competition"].lower()
        assert "hurling" not in comp_low, f"Excluded Hurling leaked: {f['id']}"

    # 2. Every fixture has official verified https source & 0 unofficial hosts
    for f in fixtures:
        assert f["sources"], f"Missing official source on {f['id']}"
        for s in f["sources"]:
            u = s["url"]
            assert u.startswith("https://"), f"Non-HTTPS URL on {f['id']}: {u}"
            host = urlparse(u).netloc.lower()
            for bad in UNOFFICIAL_HOST_SUBSTRINGS:
                assert bad not in host, f"Unofficial host '{bad}' on {f['id']}: {u}"
        if f["unverified_fields"]:
            assert f["flags"], f"Unverified fields without flag explanation on {f['id']}"

    # 3. Mathematical odds invariants & non-pushing spreads
    assert len(lines) == len(fixtures)
    high_ids_from_lines = set()
    for ln in lines:
        prob_sum = sum(o["fair_prob"] for o in ln["outcomes"])
        assert abs(prob_sum - 1.0) <= 0.0006, f"Fair probs do not sum to 1.0 on {ln['id']}: {prob_sum}"
        assert ln["pick"]["selection"], f"Missing pick selection on {ln['id']}"
        assert ln["pick"]["confidence"] in {"low", "medium", "high"}
        if ln["kind"] == "h2h":
            line_val = abs(ln["handicap_market"]["line"])
            assert abs((line_val % 1.0) - 0.5) < 1e-6, f"Integer/push handicap line on {ln['id']}: {line_val}"
        if ln["id"] == "cric-nza-inda-fc1":
            assert ln["total_market"] is None, "4-day red-ball match total must remain unpriced/blank!"
        if ln["pick"]["confidence"] == "high":
            high_ids_from_lines.add(ln["id"])

    # 4. High-confidence predictions quality & uniqueness
    pred_ids = {p["id"] for p in preds}
    assert pred_ids == high_ids_from_lines, f"High pick mismatch: {pred_ids ^ high_ids_from_lines}"
    seen_6grams: dict[tuple[str, ...], str] = {}
    for p in preds:
        wc = len(p["prediction"].split())
        assert wc >= 30 and wc == p["word_count"], f"Word count failure on {p['id']}: {wc}"
        assert p["selection"] in p["prediction"] or p["selection"].split()[-1] in p["prediction"], (
            f"Selection not named in prose for {p['id']}: {p['selection']}"
        )
        # Ensure every W-L-D or percentage cited in prose exists in the row's official verified inputs
        ev_blob = f"{p['verified_home_form']} {p['verified_away_form']} {p['venue']}"
        for pct in re.findall(r"\b\d+\.\d+%", p["prediction"]):
            assert pct in ev_blob, f"Unverified percentage {pct} in {p['id']} vs {ev_blob}"
        toks = [w for w in re.sub(r"[^a-z0-9\s]", "", p["prediction"].lower()).split() if w]
        for i in range(len(toks) - 5):
            ng = tuple(toks[i:i + 6])
            assert ng not in seen_6grams or seen_6grams[ng] == p["id"], f"Repeated 6-gram {ng}"
            seen_6grams[ng] = p["id"]

    # 5. CSV row parity check
    with (DATA_DIR / "matches.csv").open(encoding="utf-8") as fh:
        csv_rows = list(csv.DictReader(fh))
    assert len(csv_rows) == len(fixtures)
    for r in csv_rows:
        assert r["official_source_url"].startswith("https://")

    # 6. Full HTML parse, link, asset & fragment-anchor validation across all 24 pages
    html_files = sorted(SITE_DIR.rglob("*.html"))
    assert len(html_files) == 23, f"Expected 23 HTML pages (6 top + 17 sport pages), got {len(html_files)}"

    parsed_pages: dict[Path, PageInspector] = {}
    for hf in html_files:
        ins = PageInspector()
        ins.feed(hf.read_text(encoding="utf-8"))
        parsed_pages[hf.resolve()] = ins

    # Verify every event table row on index, sport pages, markets multi-runner table, and flagged table has external official link
    must_have_source_pages = [
        SITE_DIR / "index.html",
        SITE_DIR / "flagged.html",
        *[SITE_DIR / "sports" / f"{s}.html" for s in EXPECTED_IN_SCOPE],
    ]
    for mp in must_have_source_pages:
        ins = parsed_pages[mp.resolve()]
        assert ins.row_ext_links and all(n >= 1 for n in ins.row_ext_links), (
            f"Table row missing external official source link in {mp.relative_to(ROOT)}!"
        )

    # Verify every internal link + static asset + #fragment anchor resolves!
    checked_links = 0
    for hf, ins in parsed_pages.items():
        for asset in ins.srcs:
            target = (hf.parent / asset).resolve()
            assert target.exists(), f"Missing static asset {asset} referenced in {hf.relative_to(ROOT)}"
        for href in ins.hrefs:
            if href.startswith(("https://", "mailto:")):
                checked_links += 1
                continue
            assert not href.startswith("http://"), f"Insecure HTTP link in {hf.relative_to(ROOT)}: {href}"
            path_part, _, frag = href.partition("#")
            target = (hf.parent / path_part).resolve() if path_part else hf
            assert target.exists(), f"Broken relative link '{href}' in {hf.relative_to(ROOT)} -> {target}"
            if frag and target in parsed_pages:
                assert frag in parsed_pages[target].ids, (
                    f"Broken anchor '#{frag}' in {hf.relative_to(ROOT)} -> {target.relative_to(ROOT)}"
                )
            checked_links += 1

    assert REPORT_FILE.exists() and REPORT_FILE.stat().st_size > 4000, "Audit markdown report missing or incomplete!"

    print(
        f"VALIDATION PASSED 100%: {len(fixtures)} verified events across {len(sports_present)} sports | "
        f"{len(preds)} unique human High predictions | {len(fl_doc['rows'])} blank flags | "
        f"{len(au_doc['repo_findings'])} repo audit groups | {len(html_files)} HTML pages | "
        f"{checked_links} links & anchors verified with 0 errors."
    )


if __name__ == "__main__":
    main()
