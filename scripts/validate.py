#!/usr/bin/env python3
"""
validate.py - gate every build. Fails loudly rather than shipping a broken site.

Checks
  1. every internal link / asset / data reference in docs/ resolves on disk
  2. every external link is absolute https
  3. every fixture carries at least one official source link
  4. every fixture has a verification status
  5. every priced match originates a match-winner market with a pick that exists in it
  6. confidence values are from the allowed set
  7. every prediction targets a real high-confidence match, states its selection,
     and runs to at least 30 words
  8. every in-scope sport has a page, and no page is orphaned
"""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT  # Pages serves main:/ so the site root is the repo root

errors: list[str] = []
warnings: list[str] = []


class LinkCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self.ids: set[str] = set()
        self.anchors: list[tuple[str, str]] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "a" and "href" in a:
            self.links.append((a["href"], a.get("target", "")))
        if tag in ("link", "script", "img") and ("href" in a or "src" in a):
            self.links.append((a.get("href") or a.get("src"), ""))


def check_links():
    pages = sorted(list(DOCS.glob("*.html")) + list((DOCS / "sports").glob("*.html")))
    known = {p.relative_to(DOCS).as_posix() for p in pages}
    for sub in ("assets", "data"):
        for f in (DOCS / sub).rglob("*"):
            if f.is_file():
                known.add(f.relative_to(DOCS).as_posix())
    # additive (session 2360a617): session-desk namespaces (aa4e9dbf/, ebfbd966/, 2360a617/, docs/, …)
    # also resolve on disk — check every repo file so cross-board nav links validate
    for f in DOCS.rglob("*"):
        if f.is_file() and ".git" not in f.parts:
            known.add(f.relative_to(DOCS).as_posix())

    inbound: dict[str, int] = {}
    for page in pages:
        rel = page.relative_to(DOCS).as_posix()
        parser = LinkCollector()
        parser.feed(page.read_text(encoding="utf-8"))
        for href, target in parser.links:
            if href is None:
                errors.append(f"{rel}: empty href/src")
                continue
            if href.startswith(("http://", "https://")):
                if href.startswith("http://"):
                    warnings.append(f"{rel}: insecure external link {href}")
                if " " in href:
                    errors.append(f"{rel}: external link contains a space: {href}")
                continue
            if href.startswith(("mailto:", "tel:", "javascript:", "#")):
                continue
            if href.startswith("/OLBG1/"):
                href = href[len("/OLBG1/"):]
                if not href:
                    href = "index.html"
            path = href.split("#")[0]
            if not path:
                continue
            resolved = (page.parent / path).resolve()
            try:
                rel_resolved = resolved.relative_to(DOCS.resolve()).as_posix()
            except ValueError:
                errors.append(f"{rel}: link escapes site root -> {href}")
                continue
            if rel_resolved.startswith("docs/") and (DOCS / rel_resolved).is_file():
                continue  # companion board is a separate static tree
            if rel_resolved not in known:
                errors.append(f"{rel}: broken internal link -> {href}")
            else:
                inbound[rel_resolved] = inbound.get(rel_resolved, 0) + 1

    # orphan check keeps its original scope: root + sports/ pages (session 2360a617 note:
    # `known` now also contains session-desk namespaces, which are linked from their own desk index)
    for page in [p.relative_to(DOCS).as_posix() for p in pages]:
        if page.endswith(".html") and page not in ("404.html", "index.html"):
            if inbound.get(page, 0) == 0:
                errors.append(f"orphan page (nothing links to it): {page}")
    return known


def check_data():
    fixtures = json.loads((ROOT / "data/fixtures.json").read_text())
    lines = json.loads((ROOT / "data/lines.json").read_text())
    preds = json.loads((ROOT / "data/predictions.json").read_text())
    taxonomy = json.loads((ROOT / "data/olbg_taxonomy.json").read_text())

    ids = set()
    for m in fixtures["matches"]:
        mid = m.get("id")
        if not mid:
            errors.append("fixture without an id")
            continue
        ids.add(mid)
        if not m.get("sources"):
            errors.append(f"{mid}: no sources")
        for s in m["sources"]:
            if not str(s.get("url", "")).startswith("https://"):
                errors.append(f"{mid}: source is not https -> {s.get('url')}")
        if m.get("status") not in ("verified", "cross-checked", "unverified"):
            errors.append(f"{mid}: bad status {m.get('status')}")
        if not m.get("competition"):
            errors.append(f"{mid}: missing competition")

    priced = {p["id"]: p for p in lines["lines"]}
    for mid, p in priced.items():
        if mid not in ids:
            errors.append(f"priced match {mid} has no fixture")
        if p["confidence"] not in ("high", "medium", "low"):
            errors.append(f"{mid}: bad confidence {p['confidence']}")
        win = next((m for m in p["markets"] if m["key"] == "winner"), None)
        if not win:
            errors.append(f"{mid}: no match-winner market")
            continue
        sels = [o["selection"] for o in win["outcomes"]]
        if p["pick"] not in sels:
            errors.append(f"{mid}: pick '{p['pick']}' is not an outcome of its own winner market")
        probs = sum(o["probability"] for o in win["outcomes"])
        if abs(probs - 1.0) > 1e-6:
            errors.append(f"{mid}: winner probabilities sum to {probs:.6f}, not 1")
        for mk in p["markets"]:
            for o in mk["outcomes"]:
                if not (1.0 < o["odds"] < 100.0):
                    errors.append(f"{mid}: implausible odds {o['odds']}")

    seen = set()
    for it in preds["items"]:
        mid = it["match_id"]
        if mid in seen:
            errors.append(f"duplicate prediction for {mid}")
        seen.add(mid)
        if mid not in priced:
            errors.append(f"prediction for unpriced match {mid}")
        elif priced[mid]["confidence"] != "high":
            errors.append(f"prediction for non-high-confidence match {mid}")
        elif priced[mid]["pick"] != it["selection"]:
            errors.append(f"{mid}: prediction selection '{it['selection']}' != model pick '{priced[mid]['pick']}'")
        words = len(it["text"].split())
        if words < 30:
            errors.append(f"{mid}: prediction is {words} words, minimum is 30")
        stage = next((x.get("stage", "") for x in json.loads((ROOT / "data/fixtures.json").read_text())["matches"]
                      if x["id"] == mid), "")
        game_no = re.search(r"Game (\d+)", stage)
        if game_no and "Game" in it["text"]:
            if f"Game {game_no.group(1)}" not in it["text"]:
                errors.append(f"{mid}: prediction mentions a Game number that does not match the fixture stage '{stage}'")
        if it["selection"].lower() not in it["text"].lower():
            warnings.append(f"{mid}: selection name not spelled out verbatim in the text")
        if not it.get("sources"):
            errors.append(f"{mid}: prediction has no sources")

    high = [p for p in priced.values() if p["confidence"] == "high"]
    if len(high) != len(preds["items"]):
        errors.append(f"{len(high)} high-confidence picks but {len(preds['items'])} predictions")

    in_scope = [s for s in taxonomy["sports"] if s["in_scope"]]
    if len(in_scope) != 17:
        errors.append(f"expected 17 in-scope sports, found {len(in_scope)}")
    return in_scope


def check_pages(in_scope):
    for s in in_scope:
        slug = s["name"].lower().replace(" ", "-")
        alias = {"Ice Hockey": "ice-hockey", "Rugby Union": "rugby-union", "Rugby League": "rugby-league",
                 "Motor Racing": "motor-racing", "Aussie Rules": "aussie-rules",
                 "Gaelic Football": "gaelic-football", "eSports": "esports"}.get(s["name"], slug)
        if not (DOCS / "sports" / f"{alias}.html").exists():
            errors.append(f"missing sport page for {s['name']} ({alias})")


def main() -> int:
    check_links()
    in_scope = check_data()
    check_pages(in_scope)

    n = len(list(DOCS.glob("*.html"))) + len(list((DOCS / "sports").glob("*.html")))
    print(f"pages: {n}")
    print(f"errors: {len(errors)}   warnings: {len(warnings)}")
    for w in warnings[:20]:
        print("  WARN ", w)
    for err in errors[:40]:
        print("  ERROR", err)
    if errors:
        print("\nVALIDATION FAILED")
        return 1
    print("\nVALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
