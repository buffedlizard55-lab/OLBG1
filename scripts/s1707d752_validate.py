"""Site and data checks for desk 1707d752.

Run after scripts/s1707d752_build.py. Everything asserted here is a property the
desk claims on its own pages, so a failure means a page is lying.
"""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

import s1707d752_compute as C
import s1707d752_data as D
import s1707d752_model as M

OUT = ROOT / "1707d752"
SPORTS = ["Basketball", "Ice Hockey", "Baseball", "Tennis", "Cricket", "Rugby Union", "Rugby League",
          "Darts", "Snooker", "Golf", "Volleyball", "Handball", "Gaelic Sports", "Greyhounds",
          "Motor Racing"]
SLUG = {s: s.lower().replace(" ", "-") for s in SPORTS}
BANNED = ("model", "verified", "verify", "lock", "banker")
failures: list[str] = []
checked = 0


def ok(cond: bool, msg: str) -> None:
    global checked
    checked += 1
    if not cond:
        failures.append(msg)


class Doc(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.ids: set[str] = set()
        self.title = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "href" in a:
            self.links.append(a["href"])
        if "id" in a:
            self.ids.add(a["id"])

    def handle_data(self, data):
        if data.strip() and not self.title:
            self.title = data.strip()


def parse(p: Path) -> Doc:
    d = Doc()
    d.feed(p.read_text(encoding="utf-8"))
    return d


def check_data() -> dict:
    data = C.build()
    rows = data["rows"]
    official = {s["id"] for s in D.SOURCES if s["official"]}
    ok(2.0 < data["league_goals"] < 5.0, "league goals per team per game outside a sane band")

    for r in rows:
        ok(bool(r["sources"]), f"{r['id']}: no source recorded")
        ok(r["sport"] in SPORTS, f"{r['id']}: unknown sport {r['sport']}")
        ok("olbg" in r and r["olbg"].startswith("https://www.olbg.com/"), f"{r['id']}: no OLBG listing link")
        if r["utc"]:
            ok(re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", r["utc"]) is not None,
               f"{r['id']}: start time is not ISO UTC")
        if r["priced"]:
            ok(bool(set(r["sources"]) & official), f"{r['id']}: priced without an official source")
        else:
            ok(len(r.get("why", "")) > 20, f"{r['id']}: unpriced without a stated reason")

    picks = [r for r in rows if r["priced"]]
    seen: dict[str, str] = {}
    for r in picks:
        p = r["pick"]
        ok(abs(p["decimal"] - 1 / p["probability"]) < 0.002, f"{r['id']}: decimal is not 1/p")
        ok(p["american"] == M.american_from_decimal(1 / p["probability"]), f"{r['id']}: American price misderived")
        ok(M.in_brief_band(p["american"]) == p["band"], f"{r['id']}: band claim wrong")
        ok(M.brief_literal_high(p["probability"], p["american"]) == p["literal"], f"{r['id']}: literal test wrong")
        sport_key = {"Basketball": "basketball", "Ice Hockey": "hockey", "Baseball": "baseball"}[r["sport"]]
        grade = M.grade(p["probability"], complete=r["complete"], band=p["band"],
                        sample_games=r["summary"]["sample"],
                        sample_floor=M.HIGH_MIN_GAMES[sport_key])
        ok(grade["tier"] == p["confidence"], f"{r['id']}: tier does not follow the published rule")
        if p["confidence"] == "High":
            ok(p["probability"] >= 0.60 and p["band"] and r["complete"], f"{r['id']}: High pick fails a gate")
        if p["caps"]:
            ok(p["confidence"] == "Medium" and p["probability"] >= 0.60,
               f"{r['id']}: a cap is recorded but the tier or probability does not match")
        if p["confidence"] == "High":
            ok(not p["caps"], f"{r['id']}: High pick carries a cap")
        for cap in p["caps"]:
            ok(len(cap) > 15, f"{r['id']}: cap reason too short")

        prose = p["prose"]
        ok(len(prose.split()) >= 30, f"{r['id']}: prediction under 30 words ({len(prose.split())})")
        ok(prose.startswith("Selection:"), f"{r['id']}: prediction does not lead with the selection")
        ok(p["name"] in prose, f"{r['id']}: prediction does not name the picked side")
        low = prose.lower()
        for word in BANNED:
            ok(word not in low, f"{r['id']}: prediction uses '{word}'")
        tokens = re.findall(r"[a-z0-9']+", low)
        for i in range(len(tokens) - 5):
            gram = " ".join(tokens[i:i + 5])
            if gram in seen and len(gram) > 25:
                ok(False, f"{r['id']}: repeats a five-word phrase from {seen[gram]}")
            seen[gram] = r["id"]

        ok(len(r["markets"]) >= 2, f"{r['id']}: fewer than two markets investigated")
        for name, m in r["markets"].items():
            if "withheld" in m:
                ok(len(m["withheld"]) > 30, f"{r['id']}/{name}: withheld without a real reason")
                continue
            for side, blk in m.items():
                if side in ("home", "away", "over", "under"):
                    ok(abs(blk["decimal"] - 1 / blk["probability"]) < 0.002,
                       f"{r['id']}/{name}/{side}: decimal is not 1/p")
                    ok(blk["american"] == M.american_from_decimal(1 / blk["probability"]),
                       f"{r['id']}/{name}/{side}: American price misderived")

    ok(set(D.PREDICTIONS) == {r["id"] for r in picks}, "prediction set does not match the priced set")
    return data


def check_copy(data: dict) -> None:
    for row in D.LISTINGS:
        ok(len(row["why"]) > 20, f"listing {row['event']}: reason too short")
        ok(row["olbg"].startswith("https://www.olbg.com/"), f"listing {row['event']}: bad OLBG link")
        ok(row["sport"] in SPORTS, f"listing {row['event']}: unknown sport")
    ok(len({r["sport"] for r in D.LISTINGS} | {r["sport"] for r in data["rows"]}) == 15,
       "not all fifteen sports are represented")
    for flag in D.FLAGS:
        ok(len(flag["detail"]) > 80, f"{flag['id']}: flag detail too short")
        ok(flag["source"].startswith(("http", "method.html")), f"{flag['id']}: flag source unlinked")


def check_site(data: dict) -> None:
    pages = sorted(OUT.rglob("*.html"))
    ok(len(pages) >= 26, f"only {len(pages)} pages built")
    docs = {p: parse(p) for p in pages}

    for s in SPORTS:
        ok((OUT / "sports" / f"{SLUG[s]}.html").is_file(), f"missing sport page for {s}")

    for p, d in docs.items():
        text = p.read_text(encoding="utf-8")
        ok("<title>" in text, f"{p}: no title")
        for bad in ("TODO", "TBD", "FIXME", "{e(", "None</td>", "&lt;built-in"):
            ok(bad not in text, f"{p}: contains '{bad}'")
        for href in d.links:
            if href.startswith(("http://", "https://", "mailto:")):
                continue
            target, _, frag = href.partition("#")
            if not target:
                ok(frag in d.ids, f"{p}: missing in-page anchor #{frag}")
                continue
            resolved = (p.parent / target).resolve()
            ok(resolved.is_file(), f"{p}: broken link {href}")
            if frag and resolved.is_file():
                ok(frag in docs[resolved].ids, f"{p}: {href} points at a missing anchor")

    index = docs[OUT / "index.html"]
    preds = docs[OUT / "predictions.html"]
    flagged = docs[OUT / "flagged.html"]
    for r in data["rows"]:
        if not r["priced"]:
            continue
        anchor = r["pick"]["anchor"]
        ok(anchor in preds.ids, f"predictions.html lacks {anchor}")
        ok(any(anchor in h for h in index.links), f"index.html never links {anchor}")
        ok(f"predictions.html#{anchor}" in index.links, f"index.html does not name the full location of {anchor}")
    for flag in D.FLAGS:
        ok(flag["id"] in flagged.ids, f"flagged.html lacks {flag['id']}")

    summary = json.loads((ROOT / "data/1707d752/summary.json").read_text())
    picks = [r for r in data["rows"] if r["priced"]]
    ok(summary["picks"] == len(picks), "summary pick count is stale")
    ok(summary["high"] == sum(1 for r in picks if r["pick"]["confidence"] == "High"),
       "summary High count is stale")
    ok(summary["events_listed"] == len(data["rows"]) + len(D.LISTINGS), "summary event count is stale")
    picks_json = json.loads((ROOT / "data/1707d752/picks.json").read_text())
    ok(len(picks_json) == len(picks), "picks.json is stale")
    for entry in picks_json:
        ok(len(entry["prediction"].split()) >= 30, f"picks.json {entry['id']}: prediction too short")


if __name__ == "__main__":
    data = check_data()
    check_copy(data)
    check_site(data)
    if failures:
        print(f"desk 1707d752: {len(failures)} failure(s) in {checked} checks")
        for f in failures[:30]:
            print("  -", f)
        raise SystemExit(1)
    print(f"desk 1707d752: {checked} checks, 0 failures")
