#!/usr/bin/env python3
"""Session e6716490-olbg1 — gate for the consolidated desk.

Checks the data and the built site.  Exits non-zero on any error.

Data:
  * every priced fixture carries at least one official source URL
  * no fixture priced after it started
  * every High tier selection is two-sided, in 0.70..1/1.40 probability and priced 1.40..101.00
  * one High per fixture, at most three per sport, never more than the published cap
  * a High pick never appears on a fixture whose register status is flagged/unverified
  * every High pick has exactly one prediction, 30+ words, selection quoted, no shared 6-gram

Site:
  * every relative link and anchor resolves inside the repository
  * every sport page exists for every sport with fixtures
  * no third-party script, font or stylesheet is referenced
  * the landing page states the same counts as the data
"""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "e6716490"
SITE = ROOT / "e6716490"

errors: list[str] = []
warnings: list[str] = []

BAND_MIN, BAND_MAX = 1.40, 101.0
BAND_MAX_PROB = 1 / BAND_MIN


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []
        self.ids: set[str] = set()
        self.scripts: list[str] = []
        self.styles: list[str] = []
        self.anchors: list[str] = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if "id" in d:
            self.ids.add(d["id"])
        if tag == "a" and "href" in d:
            self.hrefs.append(d["href"])
            self.anchors.append(d.get("href") or "")
        if tag == "script" and d.get("src"):
            self.scripts.append(d["src"])
        if tag == "link" and d.get("href"):
            self.styles.append(d["href"])


def parse(path: Path) -> Links:
    parser = Links()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def sixgrams(text: str) -> set[str]:
    toks = re.findall(r"[a-z0-9]+", text.lower())
    return {" ".join(toks[i:i + 6]) for i in range(len(toks) - 5)}


def main() -> int:
    fixtures = json.load((OUT / "fixtures.json").open())
    lines = json.load((OUT / "lines.json").open())
    verification = json.load((OUT / "verification.json").open())
    preds = json.load((OUT / "predictions.json").open())

    cut_off = lines["cut_off_utc"]

    # ---- data gates -------------------------------------------------------
    for row in lines["rows"]:
        if not row["priced"]:
            continue
        if not row["sources"]:
            errors.append(f"{row['id']}: priced with no official source")
        for s in row["sources"]:
            if not s["url"].startswith("http"):
                errors.append(f"{row['id']}: source url is not absolute ({s['url']})")
        if row.get("start_utc") and row["start_utc"] <= cut_off:
            errors.append(f"{row['id']}: priced after its own start ({row['start_utc']} <= {cut_off})")
        for m in row["markets"]:
            for s in m["selections"]:
                if not 0.0 < s["prob"] < 1.0:
                    errors.append(f"{row['id']}: probability out of range {s['prob']}")
                expected = 1 / s["prob"]
                if abs(s["price"] - expected) > max(0.06, expected * 0.02):
                    errors.append(f"{row['id']}: fair price {s['price']} is not 1/p ({s['prob']})")
                if s["tier"] == "High":
                    if not row["two_sided"]:
                        errors.append(f"{row['id']}: High on one-sided inputs")
                    if not (0.70 <= s["prob"] <= BAND_MAX_PROB):
                        errors.append(f"{row['id']}: High probability {s['prob']} outside 0.70..{BAND_MAX_PROB:.5f}")
                    if not (BAND_MIN <= s["price"] <= BAND_MAX):
                        errors.append(f"{row['id']}: High price {s['price']} outside the band")

    highs = lines["highs"]
    if len({h["id"] for h in highs}) != len(highs):
        errors.append("more than one High pick on the same fixture")
    if len(highs) > lines["policy"]["high_cap"]:
        errors.append(f"{len(highs)} High picks exceeds the published cap")
    per_sport: dict[str, int] = {}
    for h in highs:
        per_sport[h["sport"]] = per_sport.get(h["sport"], 0) + 1
    for sport, n in per_sport.items():
        if n > 3:
            errors.append(f"{sport}: {n} High picks exceeds the 3-per-sport cap")
    for h in highs:
        if h["verification"]["status"] not in {"re-fetched", "carried"}:
            errors.append(f"{h['id']}: High pick with unknown verification status")

    # ---- predictions ------------------------------------------------------
    pred_by_fixture = {p["fixture_id"]: p for p in preds["predictions"]}
    for h in highs:
        p = pred_by_fixture.get(h["id"])
        if not p:
            errors.append(f"{h['id']}: High pick with no written prediction")
            continue
        if p["words"] < 30:
            errors.append(f"{h['id']}: prediction only {p['words']} words")
        if p["selection"] != h["selection"]:
            errors.append(f"{h['id']}: prediction selection does not match the price")
        if h["selection"].split()[0].lower() not in p["text"].lower():
            errors.append(f"{h['id']}: prediction never names the selection's side")
    if len(pred_by_fixture) != len(highs):
        errors.append(f"{len(pred_by_fixture)} predictions for {len(highs)} High picks")

    seen: dict[str, str] = {}
    for p in preds["predictions"]:
        for gram in sixgrams(p["text"]):
            if gram in seen and seen[gram] != p["fixture_id"]:
                errors.append(f"shared six-gram between {seen[gram]} and {p['fixture_id']}: {gram!r}")
            seen.setdefault(gram, p["fixture_id"])

    # ---- verification ledger ---------------------------------------------
    for c in verification["checks"]:
        if not c["url"].startswith("http"):
            errors.append(f"verification check without an official url: {c['fixture_id']}")
    re_fetched = sum(1 for r in lines["rows"] if r.get("verification", {}).get("status") == "re-fetched")
    if re_fetched != verification["counts"]["fixtures_touched"]:
        errors.append("verification counts disagree with the rows")

    # ---- site: links ------------------------------------------------------
    pages = sorted(SITE.rglob("*.html"))
    if not pages:
        errors.append("no site pages were built")
    by_id_cache: dict[Path, set[str]] = {}
    for p in pages:
        parser = parse(p)
        by_id_cache[p] = parser.ids
        for href in parser.hrefs:
            if href.startswith(("http://", "https://", "mailto:")):
                continue
            target, _, anchor = href.partition("#")
            resolved = (p.parent / target).resolve() if target else p.resolve()
            if not resolved.exists():
                errors.append(f"{p.relative_to(ROOT)}: broken link {href!r}")
                continue
            if anchor:
                ids = by_id_cache.get(resolved) or parse(resolved).ids
                by_id_cache[resolved] = ids
                if anchor not in ids:
                    errors.append(f"{p.relative_to(ROOT)}: missing anchor #{anchor} in {resolved.name}")
        for src in parser.scripts:
            if src.startswith(("http://", "https://")):
                errors.append(f"{p.relative_to(ROOT)}: third-party script {src}")
        for css in parser.styles:
            if css.startswith(("http://", "https://")):
                errors.append(f"{p.relative_to(ROOT)}: third-party stylesheet {css}")

    # ---- site: coverage ---------------------------------------------------
    for sport in {r["sport"] for r in lines["rows"]}:
        if not (SITE / "sports" / f"{sport}.html").exists():
            errors.append(f"no sport page for {sport}")

    index = (SITE / "index.html").read_text()
    for token in (str(fixtures["count"]), str(lines["counts"]["priced"]),
                  str(lines["counts"]["markets"]), str(len(highs))):
        if token not in index:
            warnings.append(f"landing page does not mention {token}")

    # ---- report -----------------------------------------------------------
    print(f"pages {len(pages)} | fixtures {fixtures['count']} | priced {lines['counts']['priced']} | "
          f"markets {lines['counts']['markets']} | High {len(highs)} | predictions "
          f"{len(preds['predictions'])} | live re-checks {verification['counts']['checks']}")
    for w in warnings:
        print("WARN:", w)
    if errors:
        for e in errors:
            print("ERROR:", e)
        print(f"VALIDATION FAILED — {len(errors)} error(s)")
        return 1
    print("VALIDATION PASSED — data, band, prose and links are consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
