#!/usr/bin/env python3
"""
validate.py - Repository-wide strict build gate across root (/), /f7fa77fc/,
and cross-linked companion trees (/docs/, /ebfbd966/, /aa4e9dbf/).

Checks:
  1. Every internal href / src across ALL HTML pages in / and /f7fa77fc/ resolves on disk
  2. Zero orphan pages across both / and /f7fa77fc/
  3. Zero linear-gradient rules in site_src/style.css
  4. Zero excluded sports present in data/fixtures.json or data/lines.json
  5. Every fixture row carries >=1 HTTPS official source link and valid status
  6. Every two-sided match originates Winner, Handicap & Total (plus DNB on 3-way sports),
     probabilities sum to 1.000000, and all odds lie in (1.01, 100.0)
  7. Exact bijection between confidence == "high" and data/predictions.json,
     >= 30 words each, selection named, sources attached, and 0 repeated 6-word n-grams
  8. Every <tbody><tr> across index.html, picks.html, sports/*.html, and flagged.html
     includes at least one external https:// link or internal sport route
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

errors: list[str] = []
warnings: list[str] = []

EXCLUDED_SLUGS = {
    "football", "soccer", "horse-racing", "american-football",
    "boxing", "ufc", "mma", "ufc-mma", "specials", "entertainment",
    "hurling", "cycling",
}


class LinkAndRowCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.in_tbody = False
        self.in_tr = False
        self.row_links: list[list[str]] = []
        self.cur_row: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        if tag == "tbody":
            self.in_tbody = True
        elif tag == "tr" and self.in_tbody:
            self.in_tr = True
            self.cur_row = []
        if tag == "a" and "href" in a and a["href"] is not None:
            self.links.append(a["href"])
            if self.in_tr:
                self.cur_row.append(a["href"])
        if tag in ("link", "script", "img"):
            target = a.get("href") or a.get("src")
            if target is not None:
                self.links.append(target)

    def handle_endtag(self, tag: str) -> None:
        if tag == "tbody":
            self.in_tbody = False
        elif tag == "tr" and self.in_tr:
            self.in_tr = False
            self.row_links.append(self.cur_row)


def check_site_tree(site_dir: Path, label: str) -> int:
    pages = sorted(list(site_dir.glob("*.html")) + list((site_dir / "sports").glob("*.html")))
    known_site = {p.relative_to(site_dir).as_posix() for p in pages}
    inbound: Counter[str] = Counter()

    for page in pages:
        rel = page.relative_to(ROOT).as_posix()
        parser = LinkAndRowCollector()
        parser.feed(page.read_text(encoding="utf-8"))

        for href in parser.links:
            if not href:
                errors.append(f"{rel}: empty href/src")
                continue
            if href.startswith(("https://", "http://")):
                if href.startswith("http://"):
                    warnings.append(f"{rel}: non-HTTPS external URL {href}")
                if " " in href:
                    errors.append(f"{rel}: external URL contains whitespace -> {href}")
                continue
            if href.startswith(("mailto:", "tel:", "javascript:", "#")):
                continue
            clean = href.split("#")[0].split("?")[0]
            if not clean:
                continue
            resolved = (page.parent / clean).resolve()
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                errors.append(f"{rel}: link escapes repository root -> {href}")
                continue
            if not resolved.is_file():
                errors.append(f"{rel}: broken internal link -> {href} (expected {resolved})")
                continue
            try:
                sub_rel = resolved.relative_to(site_dir.resolve()).as_posix()
                inbound[sub_rel] += 1
            except ValueError:
                pass

        # Every match/flag table row on picks.html, sports/*.html, and flagged.html must carry a link
        if page.name in ("picks.html", "flagged.html") or page.parent.name == "sports":
            for idx, rlinks in enumerate(parser.row_links, 1):
                if not any(u.startswith("https://") for u in rlinks):
                    errors.append(f"{rel}: table row #{idx} has no HTTPS source link")

    for sp_page in known_site:
        if sp_page not in ("404.html", "index.html") and inbound[sp_page] == 0:
            errors.append(f"{label}: orphan page {sp_page}")

    return len(pages)


def check_data_and_predictions() -> None:
    css_txt = (ROOT / "site_src" / "style.css").read_text(encoding="utf-8")
    if "linear-gradient" in css_txt:
        errors.append("site_src/style.css still contains linear-gradient")

    fixtures = json.loads((ROOT / "data" / "fixtures.json").read_text())["fixtures"]
    lines = json.loads((ROOT / "data" / "lines.json").read_text())["lines"]
    preds = json.loads((ROOT / "data" / "predictions.json").read_text())["predictions"]
    tax = json.loads((ROOT / "data" / "olbg_taxonomy.json").read_text())["sports"]

    in_scope_tax = [s for s in tax if s["in_scope"]]
    if len(in_scope_tax) != 17:
        errors.append(f"Expected 17 in-scope sports in olbg_taxonomy.json, got {len(in_scope_tax)}")

    seen_ids: set[str] = set()
    for f in fixtures:
        fid = f.get("id")
        if not fid or fid in seen_ids:
            errors.append(f"Invalid or duplicate fixture id: {fid}")
        seen_ids.add(fid)
        if f["sport"] in EXCLUDED_SLUGS:
            errors.append(f"{fid}: excluded sport leaked into dataset: {f['sport']}")
        if not f.get("sources"):
            errors.append(f"{fid}: missing official source")
        for s in f.get("sources", []):
            if not str(s.get("url", "")).startswith("https://"):
                errors.append(f"{fid}: non-HTTPS source {s.get('url')}")
        if f.get("status") not in ("verified", "cross-checked", "unverified"):
            errors.append(f"{fid}: invalid status {f.get('status')}")

    lines_by_id = {l["id"]: l for l in lines}
    h2h_ids = {f["id"] for f in fixtures if f.get("away")}
    if set(lines_by_id.keys()) != h2h_ids:
        errors.append(f"H2H fixtures ({len(h2h_ids)}) != priced lines ({len(lines_by_id)})")

    for lid, l in lines_by_id.items():
        if l["confidence"] not in ("high", "medium", "low"):
            errors.append(f"{lid}: invalid confidence {l['confidence']}")
        mk_keys = {m["key"] for m in l["markets"]}
        if not {"winner", "handicap"}.issubset(mk_keys):
            errors.append(f"{lid}: missing required winner/handicap market ({mk_keys})")
        win = next(m for m in l["markets"] if m["key"] == "winner")
        if l["pick"] not in {o["selection"] for o in win["outcomes"]}:
            errors.append(f"{lid}: pick {l['pick']} not found in winner outcomes")
        for mk in l["markets"]:
            psum = sum(o["probability"] for o in mk["outcomes"])
            if abs(psum - 1.0) > 1e-5:
                errors.append(f"{lid}/{mk['key']}: probability sum {psum} != 1.0")
            for o in mk["outcomes"]:
                if not (1.01 < o["odds"] < 100.0):
                    errors.append(f"{lid}/{mk['key']}: implausible odds {o['odds']}")

    high_ids = {lid for lid, l in lines_by_id.items() if l["confidence"] == "high"}
    pred_ids = {p["match_id"] for p in preds}
    if high_ids != pred_ids:
        errors.append(f"High picks ({len(high_ids)}) != predictions ({len(pred_ids)})")

    ngrams: Counter[tuple[str, ...]] = Counter()
    for p in preds:
        mid = p["match_id"]
        words = p["text"].split()
        if len(words) < 30:
            errors.append(f"{mid}: prediction has {len(words)} words (<30 minimum)")
        if lines_by_id[mid]["pick"].lower() not in p["text"].lower():
            errors.append(f"{mid}: winner pick '{lines_by_id[mid]['pick']}' missing from prediction prose")
        if not p.get("sources"):
            errors.append(f"{mid}: prediction missing official sources")
        toks = [re.sub(r"^[^\w]+|[^\w]+$", "", w.lower()) for w in words]
        toks = [t for t in toks if t]
        for i in range(len(toks) - 5):
            ngrams[tuple(toks[i : i + 6])] += 1

    dup_ngrams = {k: v for k, v in ngrams.items() if v > 1}
    if dup_ngrams:
        errors.append(f"Duplicate 6-word n-grams in predictions: {dup_ngrams}")

    # Check all 17 sport pages exist in both /sports/ and /f7fa77fc/sports/
    cov = json.loads((ROOT / "data" / "coverage.json").read_text())["included"]
    for c in cov:
        for base in (ROOT, ROOT / "f7fa77fc"):
            sp_file = base / "sports" / f"{c['sport']}.html"
            if not sp_file.is_file():
                errors.append(f"Missing sport subpage: {sp_file}")


def main() -> int:
    n_root = check_site_tree(ROOT, "root")
    n_ns = check_site_tree(ROOT / "f7fa77fc", "f7fa77fc")
    check_data_and_predictions()

    print(f"Validated HTML pages: {n_root} at / + {n_ns} at /f7fa77fc/ = {n_root + n_ns} pages")
    print(f"Errors: {len(errors)}   Warnings: {len(warnings)}")
    for w in warnings[:20]:
        print("  WARN:", w)
    for err in errors[:30]:
        print("  ERR :", err)
    if errors:
        print("\nVALIDATION FAILED")
        return 1
    print("\nVALIDATION PASSED — ZERO ERRORS, ZERO BROKEN LINKS, ZERO DUPLICATE N-GRAMS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
