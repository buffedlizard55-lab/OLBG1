#!/usr/bin/env python3
"""T6B47 gate: validate the desk data and the built site.

Checks
  D1  every pick satisfies the brief's stated conjunction or is labelled out-of-window
  D2  every pick carries at least one official source link
  D3  every pick has a write-up, and every write-up maps to a pick
  D4  predictions: >=30 words, no internal vocabulary, no shared six-gram
  D5  no duplicate bet key across picks, one pick per fixture
  D6  every flag has a source
  D7  every fixture either has an official source or is registered as unverified
  D8  every relative link in every page resolves
  D9  page counts match the JSON counts
"""
from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "6b47ea39"
SITE = ROOT / "6b47ea39"
BANNED = ("model", "verified", "verification", "algorithm")


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for name, value in attrs:
                if name == "href" and value:
                    self.hrefs.append(value)


def words(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def ngrams(text: str, size: int = 6):
    tokens = re.findall(r"[a-z0-9']+", text.lower())
    return {" ".join(tokens[i : i + size]) for i in range(max(0, len(tokens) - size + 1))}


def main() -> int:
    errors: list[str] = []
    slate = json.loads((DATA / "slate.json").read_text(encoding="utf-8"))
    picks_doc = json.loads((DATA / "picks.json").read_text(encoding="utf-8"))
    preds = json.loads((DATA / "predictions.json").read_text(encoding="utf-8"))
    flags = json.loads((DATA / "flags.json").read_text(encoding="utf-8"))
    events = {e["id"]: e for e in slate["events"]}
    picks = picks_doc["picks"]

    # D1 / D2 / D5
    seen_bets: dict[str, str] = {}
    seen_events: set[str] = set()
    for pick in picks:
        if pick["probability"] > 0.70 and pick["tier"] == "high-in-window":
            if not (-250.0 - 1e-6 <= pick["american"] <= 10000.0 + 1e-6):
                errors.append(f"D1 {pick['pick_id']}: labelled in-window but priced {pick['american']}")
        elif pick["tier"] == "high-in-window":
            errors.append(f"D1 {pick['pick_id']}: in-window label with {pick['probability']:.3f} probability")
        elif pick["tier"] == "out-of-window" and pick["probability"] <= 0.70:
            errors.append(f"D1 {pick['pick_id']}: out-of-window label with sub-70% probability")
        if not pick["official_sources"]:
            errors.append(f"D2 {pick['pick_id']}: no official source")
        if pick["event_id"] in seen_events:
            errors.append(f"D5 {pick['pick_id']}: second pick on fixture {pick['event_id']}")
        seen_events.add(pick["event_id"])
        if pick["bet_key"] in seen_bets:
            errors.append(f"D5 {pick['pick_id']}: duplicate bet key {pick['bet_key']}")
        seen_bets[pick["bet_key"]] = pick["pick_id"]
        if pick["event_id"] not in events:
            errors.append(f"D5 {pick['pick_id']}: unknown fixture")
        elif events[pick["event_id"]]["state"] != "upcoming":
            errors.append(f"D5 {pick['pick_id']}: pick on non-upcoming fixture")

    # D3 / D4
    pick_ids = {p["pick_id"] for p in picks}
    pred_ids = {p["pick_id"] for p in preds["predictions"]}
    if pick_ids - pred_ids:
        errors.append(f"D3 picks without write-up: {sorted(pick_ids - pred_ids)}")
    if pred_ids - pick_ids:
        errors.append(f"D3 write-ups without a pick: {sorted(pred_ids - pick_ids)}")
    seen: dict[str, str] = {}
    for row in preds["predictions"]:
        count = words(row["text"])
        if count < 30:
            errors.append(f"D4 {row['pick_id']}: {count} words")
        if count != row["words"]:
            errors.append(f"D4 {row['pick_id']}: stored word count {row['words']} != {count}")
        low = row["text"].lower()
        for word in BANNED:
            if re.search(rf"\b{word}\b", low):
                errors.append(f"D4 {row['pick_id']}: contains '{word}'")
        for gram in ngrams(row["text"]):
            if gram in seen:
                errors.append(f"D4 {row['pick_id']}: shares six-gram with {seen[gram]}: '{gram}'")
                break
            seen[gram] = row["pick_id"]
        if not row["official_sources"]:
            errors.append(f"D2 {row['pick_id']}: write-up without an official source")
        # the write-up must name the selection it is attached to
        display = str(row.get("display_selection") or row["selection"])
        low_text = row["text"].lower()
        total = re.search(r"(over|under)\s+([0-9]+(?:\.[0-9])?)", display.lower())
        if total:
            if total.group(1) not in low_text or total.group(2) not in low_text:
                errors.append(f"D4 {row['pick_id']}: text does not state '{total.group(1)} {total.group(2)}'")
        else:
            keys = [w for w in re.findall(r"[A-Za-z][A-Za-z'-]{3,}", display) if w.lower() not in {
                "over", "under", "goals", "frames", "points", "sets", "winner", "finish", "match", "best", "handicap",
                "top", "stakes", "beat", "round", "line", "run", "cup", "open"}]
            if keys and not any(k.lower() in low_text for k in keys):
                errors.append(f"D4 {row['pick_id']}: text does not name the selection '{display}'")
    if preds["problems"]:
        errors.append(f"D4 builder reported: {preds['problems']}")

    # D6
    for flag in flags["flags"]:
        if not flag["source"]:
            errors.append(f"D6 {flag['id']}: no source")

    # D7
    unlinked = [e for e in slate["events"] if not e["official_sources"]]
    if unlinked and not any("no official source" in json.dumps(f).lower() for f in flags["flags"]):
        errors.append(f"D7 {len(unlinked)} fixtures without a source and no register entry")

    # D8 / D9
    pages = sorted(SITE.rglob("*.html"))
    for page in pages:
        parser = Links()
        parser.feed(page.read_text(encoding="utf-8"))
        for href in parser.hrefs:
            parts = urlsplit(href)
            if parts.scheme in ("http", "https", "mailto"):
                continue
            if not parts.path:
                continue
            target = (page.parent / parts.path).resolve()
            if not target.exists():
                errors.append(f"D8 {page.relative_to(ROOT)}: broken link {href}")
    index = (SITE / "index.html").read_text(encoding="utf-8")
    for needle, label in (("High · in window", "in-window badge"), ("Flagged for review", "flagged nav")):
        if needle not in index:
            errors.append(f"D9 index missing {label}")
    picks_page = (SITE / "picks.html").read_text(encoding="utf-8")
    if picks_page.count('<tr>') < len(picks):
        errors.append("D9 picks page has fewer rows than picks")
    pred_page = (SITE / "predictions.html").read_text(encoding="utf-8")
    if pred_page.count('class="pred"') < len(preds["predictions"]):
        errors.append("D9 predictions page missing write-ups")

    print(f"pages: {len(pages)} · picks: {len(picks)} · predictions: {len(preds['predictions'])} · flags: {len(flags['flags'])}")
    if errors:
        print(f"FAILED — {len(errors)} error(s)")
        for error in errors[:40]:
            print("  " + error)
        return 1
    print("PASSED — data, writing rules and site links are consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
