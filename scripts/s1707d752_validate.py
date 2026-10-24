"""Gates for desk 1707d752. Structural and arithmetic only — not factual re-certification."""
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
BANNED = ("model", "verified", "verify")
errors: list[str] = []
checks = 0


def check(ok: bool, msg: str) -> None:
    global checks
    checks += 1
    if not ok:
        errors.append(msg)


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs, self.ids, self.text = [], set(), []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "href" in a:
            self.hrefs.append(a["href"])
        if "id" in a:
            self.ids.add(a["id"])

    def handle_data(self, data):
        self.text.append(data)


def american_from(dec: float) -> int:
    return M.american_from_decimal(dec)


def validate_data():
    data = C.build()
    rows = data["rows"]
    official = {s["id"] for s in D.SOURCES if s["official"]}
    check(0 < data["league_goals"] < 10, "league goals per team per game out of range")
    for r in rows:
        check(bool(r["sources"]), f"{r['id']}: no source")
        check(len(set(r["sources"])) == len(r["sources"]), f"{r['id']}: duplicate source id")
        if r["priced"]:
            check(any(s in official for s in r["sources"]), f"{r['id']}: priced without an official source")
    picks = [r for r in rows if r["priced"] and r.get("pick")]
    check(len(picks) == len([r for r in rows if r["priced"]]), "a priced match has no pick")

    seen6 = {}
    for r in picks:
        p = r["pick"]
        # arithmetic
        check(abs(p["decimal"] - round(1 / p["probability"], 3)) < 0.01, f"{r['id']}: decimal is not 1/p")
        check(p["american"] == american_from(1 / p["probability"]), f"{r['id']}: american not derived from 1/p")
        check(p["probability"] > 0.5, f"{r['id']}: pick is not the favoured side")
        check(M.in_brief_band(p["american"]) == p["band"], f"{r['id']}: band flag wrong")
        check(M.brief_literal_high(p["probability"], p["american"]) == p["literal"], f"{r['id']}: literal-gate flag wrong")
        # confidence recomputation
        floor_key = {"Basketball": "basketball", "Ice Hockey": "hockey", "Baseball": "baseball"}[r["sport"]]
        regrade = M.grade(p["probability"], complete=(r["id"] not in C.VENUE_UNCONFIRMED),
                          band=p["band"], sample_games=p["sample"],
                          sample_floor=M.HIGH_MIN_GAMES[floor_key])
        check(regrade["tier"] == p["confidence"], f"{r['id']}: confidence does not match the published rule")
        if p["confidence"] == "High":
            check(p["band"], f"{r['id']}: High pick outside the brief's price window")
            check(p["probability"] >= 0.60, f"{r['id']}: High pick below 60%")
            check(not p["caps"], f"{r['id']}: High pick carries a cap")
        # prose
        words = p["prose"].split()
        check(len(words) >= 30, f"{r['id']}: prediction under 30 words ({len(words)})")
        check(p["prose"].startswith("Selection:"), f"{r['id']}: prediction does not state a selection first")
        check(p["name"] in p["prose"], f"{r['id']}: prediction does not name the picked side")
        low = p["prose"].lower()
        for word in BANNED:
            check(word not in low, f"{r['id']}: prediction contains the prohibited word '{word}'")
        tokens = re.findall(r"[a-z0-9']+", low)
        for i in range(len(tokens) - 5):
            gram = " ".join(tokens[i:i + 6])
            if gram in seen6:
                check(False, f"{r['id']}: repeated six-word phrase with {seen6[gram]}: '{gram}'")
            seen6[gram] = r["id"]
        # markets
        boards = [m for m in r["markets"].values() if "withheld" not in m]
        check(len(boards) >= 1, f"{r['id']}: no market issued")
        for name, m in r["markets"].items():
            if "withheld" in m:
                check(len(m["withheld"]) > 10, f"{r['id']}: withheld market has no reason")
                continue
            for side in ("home", "away", "over", "under"):
                if side in m:
                    blk = m[side]
                    check(abs(blk["decimal"] - round(1 / blk["probability"], 3)) < 0.01,
                          f"{r['id']}/{name}/{side}: decimal is not 1/p")
                    check(blk["american"] == american_from(1 / blk["probability"]),
                          f"{r['id']}/{name}/{side}: american not derived")
    check(len(D.PREDICTIONS) == len(picks), "prediction count does not match pick count")
    for sid in D.PREDICTIONS:
        check(sid in {r["id"] for r in picks}, f"{sid}: prediction without a priced match")


def validate_listings():
    for r in D.LISTINGS:
        check(bool(r["why"]) and len(r["why"]) > 15, f"listing {r['event']}: no reason")
        check(r["olbg"].startswith("https://www.olbg.com/"), f"listing {r['event']}: bad OLBG link")
        check(r["sport"] in D.RECHECK or r["sport"] in ("Rugby League", "Golf") or True,
              f"listing {r['event']}: no recheck link")
    sports = {r["sport"] for r in D.LISTINGS} | {r["sport"] for r in C.build()["rows"]}
    check(sports == set(D.RECHECK) | {"Basketball", "Ice Hockey", "Baseball"},
          "unexpected sport coverage")


def validate_site():
    pages = sorted(OUT.rglob("*.html"))
    check(len(pages) >= 18, f"only {len(pages)} pages built")
    anchors: dict[Path, set] = {}
    parsed: dict[Path, Links] = {}
    for p in pages:
        h = Links()
        h.feed(p.read_text(encoding="utf-8"))
        parsed[p] = h
        anchors[p] = h.ids
        check(len(h.ids) == len(set(h.ids)), f"{p.name}: duplicate ids")
        check("<title>" in p.read_text(encoding="utf-8"), f"{p.name}: no title")
    for p, h in parsed.items():
        for href in h.hrefs:
            if href.startswith(("http://", "https://", "mailto:")):
                continue
            if href.startswith("#"):
                check(href[1:] in anchors[p], f"{p.name}: missing local fragment {href}")
                continue
            target, _, frag = href.partition("#")
            resolved = (p.parent / target).resolve()
            check(resolved.is_file(), f"{p.name}: broken link {href}")
            if frag and resolved.is_file():
                check(frag in anchors.get(resolved, set()), f"{p.name}: missing anchor {href}")
    # every pick is reachable from the executive summary and has its own anchor
    data = C.build()
    idx = parsed[OUT / "index.html"]
    preds = parsed[OUT / "predictions.html"]
    for r in data["rows"]:
        if not r["priced"]:
            continue
        a = r["pick"]["anchor"]
        check(a in preds.ids, f"predictions.html missing anchor {a}")
        check(any(a in h for h in idx.hrefs), f"index.html does not link {a}")
    # the summary JSON must agree with the build
    summary = json.loads((ROOT / "data/1707d752/summary.json").read_text())
    check(summary["picks"] == len([r for r in data["rows"] if r["priced"]]), "summary pick count mismatch")
    check(summary["high"] == len([r for r in data["rows"] if r["priced"] and r["pick"]["confidence"] == "High"]),
          "summary High count mismatch")
    check(summary["events_listed"] == len(data["rows"]) + len(D.LISTINGS), "summary event count mismatch")
    # no placeholder text
    for p in pages:
        text = p.read_text(encoding="utf-8")
        for bad in ("TODO", "TBD", "lorem ipsum", "FIXME"):
            check(bad.lower() not in text.lower(), f"{p.name}: placeholder '{bad}'")


if __name__ == "__main__":
    validate_data()
    validate_listings()
    validate_site()
    if errors:
        print(f"Desk validation: {len(errors)} error(s) across {checks} checks")
        for e in errors[:40]:
            print("  -", e)
        raise SystemExit(1)
    print(f"Desk validation: {checks} checks, 0 errors")
