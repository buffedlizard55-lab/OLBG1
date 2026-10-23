#!/usr/bin/env python3
"""Desk 8aede3ba gate: provenance, price arithmetic, prediction rules, site links.

Exit code 0 only when every check passes. Run from repository root:
    python3 scripts/s8aede3ba_validate.py
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "8aede3ba"
DATA = ROOT / "data" / "8aede3ba"

# Exact host match against governing bodies, leagues, tours, boards and clubs that
# actually appear in this desk. OLBG is deliberately absent.
OFFICIAL_HOSTS = {
    "www.atptour.com",
    "wtafiles.wtatennis.com",
    "www.wtatennis.com",
    "www.nba.com",
    "api-web.nhle.com",
    "statsapi.mlb.com",
    "www.mlb.com",
    "www.pgatour.com",
    "www.europeantour.com",
    "www.lpga.com",
    "www.formula1.com",
    "www.wst.tv",
    "www.pdc.tv",
    "www.legavolley.it",
    "www.plusliga.pl",
    "www.tauronliga.pl",
    "www.unitedrugby.com",
    "stats.unitedrugby.com",
    "top14.lnr.fr",
    "www.icc-cricket.com",
    "www.pcb.com.pk",
    "scratch.nzc.nz",
    "scoring.nzc.nz",
    "www.nzc.nz",
    "munster.gaa.ie",
    "gaacork.ie",
    "www.galwaygaa.ie",
    "www.waterfordgaa.ie",
    "www.limerickgaa.ie",
    "www.gbgb.org.uk",
    "ehfcl.eurohandball.com",
    "www.eurohandball.com",
    "www.nrl.com",
    "www.intrl.sport",
}
BANNED = re.compile(r"\b(model|models|verified|verification|verify)\b", re.I)
SPORTS = [
    "golf", "volleyball", "rugby-union", "cricket", "snooker", "darts", "baseball",
    "gaelic-sports", "greyhounds", "tennis", "motor-racing", "handball",
    "ice-hockey", "basketball", "rugby-league",
]
errors: list[str] = []
warnings: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


class Doc(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []
        self.ids: list[str] = []
        self.title = False
        self.h1 = 0
        self.rows: list[list[str]] = []
        self._row: list[str] | None = None
        self._td = False

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "title":
            self.title = True
        if tag == "h1":
            self.h1 += 1
        if d.get("id"):
            self.ids.append(d["id"])
        if d.get("href"):
            self.links.append(d["href"])
        if tag == "tr":
            self._row, self._td = [], False
        if tag == "td":
            self._td = True
        if tag == "a" and self._row is not None and d.get("href"):
            self._row.append(d["href"])

    def handle_endtag(self, tag):
        if tag == "tr" and self._row is not None:
            if self._td:
                self.rows.append(self._row)
            self._row = None


def check_data() -> tuple[int, int, int]:
    fx = json.loads((DATA / "fixtures.json").read_text())
    preds_doc = json.loads((DATA / "predictions.json").read_text())
    flags = json.loads((DATA / "flagged.json").read_text())
    summary = json.loads((DATA / "summary.json").read_text())
    rows = fx["fixtures"]
    preds = preds_doc["predictions"]

    if fx["sports_covered"] != 15:
        fail(f"expected 15 covered sports, got {fx['sports_covered']}")

    ids = [r["id"] for r in rows]
    if len(ids) != len(set(ids)):
        fail("duplicate fixture ids")

    seen_sports = {r["sport"] for r in rows}
    missing = set(SPORTS) - seen_sports
    if missing:
        fail(f"sports with no fixtures: {sorted(missing)}")

    by_id = {r["id"]: r for r in rows}
    high_rows = [r for r in rows if r["confidence"] == "High"]
    high_ids = [r["id"] for r in high_rows]

    for r in rows:
        if not r["official_url"].startswith("https://"):
            fail(f"{r['id']}: official url not https")
        host = urlsplit(r["official_url"]).hostname or ""
        if host not in OFFICIAL_HOSTS:
            fail(f"{r['id']}: official host not allowlisted ({host})")
        if r["secondary_official_url"]:
            h2 = urlsplit(r["secondary_official_url"]).hostname or ""
            if h2 and h2 not in OFFICIAL_HOSTS:
                warnings.append(f"{r['id']}: secondary host not allowlisted ({h2})")
        if not r["markets"]:
            fail(f"{r['id']}: no originated markets")
        for m in r["markets"]:
            outs = m["outcomes"]
            if len(outs) < 2:
                fail(f"{r['id']}/{m['market_name']}: fewer than two outcomes")
            mass = sum(o["p_fair"] for o in outs)
            if abs(mass - 1.0) > 5e-4:
                fail(f"{r['id']}/{m['market_name']}: fair mass {mass} != 1")
            for o in outs:
                p = o["p_fair"]
                if not (0 < p < 1):
                    fail(f"{r['id']}/{m['market_name']}: invalid probability {p}")
                dec = o["decimal_odds"]
                if abs(dec * p - 1.0) > 2e-3:
                    fail(f"{r['id']}/{m['market_name']}: {dec} is not 1/p for p={p}")
                am = o["american_odds"]
                expect = int(round((dec - 1) * 100)) if dec >= 2 else int(round(-100 / (dec - 1)))
                if am != expect:
                    fail(f"{r['id']}/{m['market_name']}: american {am} != decimal-derived {expect}")
        # the published selection must exist among the published quotes
        labels = [o["label"] for m in r["markets"] for o in m["outcomes"]]
        if r["selection"] not in labels:
            fail(f"{r['id']}: selection '{r['selection']}' is not among quoted outcomes")

    for r in high_rows:
        if r["selection_prob"] < 0.70:
            fail(f"{r['id']}: High pick fair probability {r['selection_prob']:.4f} < 0.70")
        if not (-250 <= r["selection_american"] <= 10000):
            fail(f"{r['id']}: High pick price {r['selection_american']} outside -250..+10000")
        text = r["prediction"]
        if len(text.split()) < 30:
            fail(f"{r['id']}: prediction shorter than 30 words")
        if BANNED.search(text):
            fail(f"{r['id']}: prediction contains a banned internal word")
        low = text.lower()
        if r["selection"].lower() in low:
            pass
        else:
            line_tok = re.search(r"[-+]?\d+(?:\.\d+)?", r["selection"])
            team_ok = any(tok and tok.lower() in low for tok in (r["home"].split()[0], r["away"].split()[0]))
            line_ok = bool(line_tok) and line_tok.group(0).lstrip("+") in low
            if not (team_ok and line_ok):
                fail(f"{r['id']}: prediction does not name the selection ({r['selection']})")
        if r["home"].split()[0].lower() not in text.lower() and r["away"].split()[0].lower() not in text.lower():
            fail(f"{r['id']}: prediction does not name either participant")

    # every prose row is a High row, and every High row has prose
    prose_ids = {p["fixture_id"] for p in preds}
    if prose_ids != set(high_ids):
        fail(f"prose/high mismatch: prose-only {sorted(prose_ids - set(high_ids))}, high-only {sorted(set(high_ids) - prose_ids)}")

    # uniqueness of long n-grams across all 66 write-ups
    grams: Counter = Counter()
    for p in preds:
        toks = [re.sub(r"[^\w']", "", w).lower() for w in p["text"].split()]
        toks = [t for t in toks if t]
        for i in range(len(toks) - 6):
            grams[tuple(toks[i:i + 7])] += 1
    dupes = {g: c for g, c in grams.items() if c > 1}
    if dupes:
        fail(f"repeated 7-grams across predictions: {list(dupes)[:3]}")

    # flags must all carry a resolvable-looking source
    for f in flags["flags"]:
        if not f["source_url"].startswith("https://"):
            fail(f"{f['id']}: flag source not https")
        if f["repository_url"] and not f["repository_url"].startswith("https://github.com/"):
            fail(f"{f['id']}: repository url malformed")

    counts = fx["counts"]
    if counts["fixtures"] != len(rows):
        fail("fixture count mismatch")
    if counts["high"] != len(high_rows):
        fail("high count mismatch")
    if summary["high"] != len(high_rows) or summary["fixtures"] != len(rows):
        fail("summary counts disagree with fixtures")
    if summary["markets"] != sum(len(r["markets"]) for r in rows):
        fail("summary market count disagrees")
    if summary["predictions"] != len(preds):
        fail("summary prediction count disagrees")
    if summary["flags"] != len(flags["flags"]):
        fail("summary flag count disagrees")
    if len(preds) != len(high_rows):
        fail("prediction count does not equal high count")

    # quota reporting must be honest: no sport may claim 5+ High without having them
    for slug in SPORTS:
        have = sum(1 for r in high_rows if r["sport"] == slug)
        claimed = summary["high_per_sport"].get(slug, 0)
        if have != claimed:
            fail(f"{slug}: high_per_sport {claimed} != actual {have}")
        if have > 5:
            warnings.append(f"{slug}: {have} High picks (target is 5)")
    return len(rows), len(high_rows), len(preds)


def check_site() -> int:
    manifest = json.loads((DATA / "site-manifest.json").read_text())
    pages = manifest["pages"]
    parsed: dict[Path, Doc] = {}
    for rel in pages:
        p = SITE / rel
        if not p.is_file():
            fail(f"missing page {rel}")
            continue
        d = Doc()
        d.feed(p.read_text(encoding="utf-8"))
        parsed[p.resolve()] = d
        if not d.title:
            fail(f"{rel}: no <title>")
        if d.h1 != 1:
            fail(f"{rel}: expected exactly one h1, found {d.h1}")
        if len(d.ids) != len(set(d.ids)):
            fail(f"{rel}: duplicate ids")
        if not d.rows and rel not in ("sports.html", "methodology.html", "predictions.html"):
            fail(f"{rel}: no table rows")
        # Fixture/market tables must cite a governing body. Audit registers
        # (flagged / repo-audit / sources) may also cite the project repository or
        # the published site they are describing, which is still a real traceable link.
        register = rel in ("flagged.html", "repo-audit.html", "sources.html")
        for i, links in enumerate(d.rows, 1):
            if register:
                ok = any(u.startswith("https://") for u in links)
                label = "traceable https source"
            else:
                ok = any((urlsplit(u).hostname or "") in OFFICIAL_HOSTS for u in links)
                label = "official governing-body link"
            if not ok:
                fail(f"{rel}: row {i} has no {label}")

    # internal link + fragment integrity across the whole desk
    broken = 0
    for path, d in parsed.items():
        for href in d.links:
            u = urlsplit(href)
            if u.scheme or u.netloc:
                if u.scheme in ("javascript", "data"):
                    fail(f"{path.name}: unsafe scheme {u.scheme}")
                continue
            target = (path.parent / unquote(u.path)).resolve() if u.path else path
            try:
                target.relative_to(SITE.resolve())
            except ValueError:
                fail(f"{path.name}: link escapes desk ({href})")
                broken += 1
                continue
            if target.is_dir():
                target = target / "index.html"
            if not target.is_file():
                fail(f"{path.name}: broken link {href}")
                broken += 1
                continue
            if u.fragment:
                td = parsed.get(target) or Doc()
                if target not in parsed:
                    td.feed(target.read_text(encoding="utf-8"))
                    parsed[target] = td
                if unquote(u.fragment) not in td.ids:
                    fail(f"{path.name}: missing fragment {href}")
                    broken += 1
    return len(parsed) - broken


def main() -> int:
    if not (DATA / "fixtures.json").is_file():
        print("run scripts/s8aede3ba_build.py first")
        return 1
    n_fx, n_high, n_pred = check_data()
    n_pages = check_site()
    print(f"Desk 8aede3ba: {n_fx} fixtures | {n_high} High picks | {n_pred} predictions | {n_pages} pages")
    for w in warnings[:10]:
        print("  WARN:", w)
    for e in errors[:40]:
        print("  ERR :", e)
    if errors:
        print(f"\nVALIDATION FAILED — {len(errors)} error(s)")
        return 1
    print("\nVALIDATION PASSED — provenance, price arithmetic, writing rules and site links are consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
