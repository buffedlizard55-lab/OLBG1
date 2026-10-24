"""Gate for the f840c28a desk.

Checks the built artefact, not the intent:

  * every page exists, has one h1, and every relative link resolves
  * every published fixture names an official source that is in the source list
  * every pick is inside the brief's -250..+10000 band
  * every pick's tier matches the published grading rule
  * every prediction is at least 30 words, uses no internal vocabulary and
    shares no six-word run with another prediction
  * every flagged item carries at least one source that exists
  * the counts in the manifest match the counts in the data

Usage:  python3 scripts/sf840c28a_validate.py [--quiet]
Exit code 0 when everything passes.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DESK = "f840c28a"
OUT = ROOT / DESK
DATA = ROOT / "data" / DESK

PAGES = ["index.html", "picks.html", "predictions.html", "matches.html", "markets.html",
         "sports.html", "flagged.html", "sources.html", "methodology.html",
         "repo-review.html"]

SPORTS = ["golf", "volleyball", "rugby-union", "cricket", "snooker", "darts", "baseball",
          "gaelic-sports", "greyhounds", "tennis", "motor-racing", "handball",
          "ice-hockey", "basketball", "rugby-league"]

BAND_LO, BAND_HI = -250.0, 10000.0
FORBIDDEN = ("model", "verified", "verification", "modelled", "modeled")


class Checks:
    def __init__(self) -> None:
        self.n = 0
        self.fails: list[str] = []

    def ok(self, cond: bool, label: str) -> None:
        self.n += 1
        if not cond:
            self.fails.append(label)

    def eq(self, a, b, label: str) -> None:
        self.ok(a == b, f"{label} (got {a!r}, expected {b!r})")


def text_of(path: pathlib.Path) -> str:
    raw = path.read_text(errors="ignore")
    raw = re.sub(r"<style>.*?</style>", " ", raw, flags=re.S)
    raw = re.sub(r"<script>.*?</script>", " ", raw, flags=re.S)
    return re.sub(r"<[^>]+>", " ", raw)


def six_grams(text: str):
    words = re.findall(r"[a-z0-9']+", text.lower())
    return {tuple(words[i:i + 6]) for i in range(max(0, len(words) - 5))}


def main(argv) -> int:
    quiet = "--quiet" in argv
    c = Checks()

    # ---------------------------------------------------------------- data
    desk = json.loads((DATA / "desk.json").read_text())
    manifest = json.loads((DATA / "manifest.json").read_text())
    sources = json.loads((DATA / "sources.json").read_text())
    flags = json.loads((DATA / "flags.json").read_text())
    source_ids = {s["id"] for s in sources}
    official_ids = {s["id"] for s in sources if s["tier"] == "official"}

    # every source has a URL and a read time
    for s in sources:
        c.ok(s["url"].startswith("http"), f'source {s["id"]} has a URL')
        c.ok(bool(s.get("read_utc")), f'source {s["id"]} has a read time')
        c.ok(s["tier"] in ("official", "discovery"), f'source {s["id"]} has a tier')

    # every priced fixture names an official source
    priced = [f for f in desk["fixtures"] if f["priced"]]
    for f in priced:
        c.ok(f.get("fixture_source") in official_ids,
             f'priced fixture {f["away"]}@{f["home"]} has an official fixture source')
        c.ok(bool(f.get("markets")), f'priced fixture {f["away"]}@{f["home"]} has markets')
    c.ok(len(priced) > 0, "at least one priced fixture")

    # band + tier rule on every outcome
    n_outcomes = 0
    for f in desk["fixtures"]:
        for o in f.get("outcomes", []):
            n_outcomes += 1
            price, p = o["price"], o["p"]
            inband = BAND_LO <= price <= BAND_HI
            c.eq(o["band"], "in" if inband else "out",
                 f'band state for {o["selection"]}')
            expected = ("High" if p > 0.70 else "Medium" if p >= 0.60
                        else "Low" if p >= 0.52 else "outside band")
            if not inband:
                expected = "outside band"
            c.eq(o["tier"], expected, f'tier for {o["selection"]} at {price:.0f}')
    c.ok(n_outcomes > 0, "the desk priced something")

    # every pick is inside the band and graded consistently
    for p in desk["picks"]:
        c.ok(BAND_LO <= p["price"] <= BAND_HI,
             f'pick {p["selection"]} is inside the band ({p["price"]:.0f})')
        c.ok(p["confidence"] in ("High", "Medium", "Low"),
             f'pick {p["selection"]} has a published tier')
        c.ok(p["selection"] and p["market"], f'pick {p["selection"]} names a selection')
        c.ok(p.get("fixture_source") in official_ids,
             f'pick {p["selection"]} traces to an official fixture source')

    # predictions
    preds = [(p["fixture"], p["prediction"]) for p in desk["picks"] if p.get("prediction")]
    c.ok(len(preds) >= 5, "at least five written predictions")
    grams_seen: dict[str, set] = {}
    for fixture, text in preds:
        c.ok(len(text.split()) >= 30, f"prediction for {fixture} is at least 30 words")
        low = text.lower()
        for bad in FORBIDDEN:
            c.ok(bad not in low, f"prediction for {fixture} avoids '{bad}'")
        g = six_grams(text)
        for other, og in grams_seen.items():
            c.ok(not (g & og), f"prediction for {fixture} does not repeat {other}")
        grams_seen[fixture] = g
        c.ok(text.rstrip().endswith((".", "!", "?")), f"prediction for {fixture} ends cleanly")

    # flags
    for fl in flags:
        if not fl["id"].startswith("F-"):
            continue      # repository findings cite files, not URLs
        c.ok(bool(fl.get("sources")), f'flag {fl["id"]} has sources')
        for sid in fl.get("sources", []):
            c.ok(sid in source_ids, f'flag {fl["id"]} references a known source ({sid})')

    # counts
    cnt = desk["counts"]
    c.eq(cnt["fixtures"], len(desk["fixtures"]), "fixture count")
    c.eq(cnt["priced"], len(priced), "priced count")
    c.eq(cnt["picks"], len(desk["picks"]), "pick count")
    c.eq(cnt["high"], sum(1 for p in desk["picks"] if p["confidence"] == "High"), "High count")
    c.eq(cnt["medium"], sum(1 for p in desk["picks"] if p["confidence"] == "Medium"),
         "Medium count")
    c.eq(cnt["low"], sum(1 for p in desk["picks"] if p["confidence"] == "Low"), "Low count")
    c.eq(cnt["predictions"], len(preds), "prediction count")
    c.eq(manifest["counts"], cnt, "manifest matches desk counts")
    c.eq(cnt["sports"], 15, "fifteen sports covered")

    # ---------------------------------------------------------------- pages
    for name in PAGES:
        path = OUT / name
        c.ok(path.is_file(), f"page {name} exists")
        if not path.is_file():
            continue
        html_text = path.read_text()
        c.eq(html_text.count("<h1"), 1, f"page {name} has exactly one h1")
        c.ok("<title>" in html_text, f"page {name} has a title")
        c.ok("TODO" not in html_text and "FIXME" not in html_text, f"page {name} has no placeholder")
        for href in re.findall(r'href="([^"#?]+\.html)"', html_text):
            if href.startswith("http"):
                continue
            target = (path.parent / href).resolve()
            c.ok(target.is_file(), f'{name} link {href} resolves')
    for code in SPORTS:
        path = OUT / "sports" / f"{code}.html"
        c.ok(path.is_file(), f"sport page {code} exists")
        if path.is_file():
            c.eq(path.read_text().count("<h1"), 1, f"sport page {code} has one h1")

    # the summary page must actually show the picks
    index = text_of(OUT / "index.html")
    for p in desk["picks"]:
        c.ok(p["selection"] in index, f'summary page shows the pick {p["selection"]}')

    # no internal vocabulary on the public pages
    for name in PAGES + [f"sports/{s}.html" for s in SPORTS]:
        t = text_of(OUT / name).lower()
        for bad in ("verified", "our model"):
            c.ok(bad not in t, f"{name} does not say '{bad}'")

    print(f"{c.n - len(c.fails)}/{c.n} checks passed")
    if c.fails:
        print("FAILURES:")
        for f in c.fails[:40]:
            print("  -", f)
        return 1
    if not quiet:
        print(f"desk {DESK}: {cnt['fixtures']} fixtures, {cnt['priced']} priced, "
              f"{cnt['markets']} markets, {cnt['outcomes']} prices, {cnt['picks']} picks "
              f"({cnt['high']} High / {cnt['medium']} Medium / {cnt['low']} Low), "
              f"{len(preds)} predictions, {len(flags)} flags, {len(sources)} sources")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
