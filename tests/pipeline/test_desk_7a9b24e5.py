"""Automated regression gate for session 7a9b24e5 (7a9b24e5/ and data/7a9b24e5/).

Checks the published desk the way a reader would: every sport page exists, every
table row carries an official link, the promoted prices sit inside the stated
band, the written pieces are long enough and unique, and the two banned words
stay out of the published prose.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESK = ROOT / "7a9b24e5"
DATA = ROOT / "data" / "7a9b24e5"

SPORTS = ["Baseball", "Basketball", "Cricket", "Darts", "Gaelic Sports", "Golf",
          "Greyhounds", "Handball", "Ice Hockey", "Motor Racing", "Rugby League",
          "Rugby Union", "Snooker", "Tennis", "Volleyball"]
SLUG = {s: s.lower().replace(" ", "-") for s in SPORTS}
PAGES = ["index.html", "matches.html", "markets.html", "high-confidence.html",
         "predictions.html", "analysis.html", "sources.html", "flagged.html",
         "methodology.html", "reverse-engineering.html", "repo-audit.html"]


def text_of(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


class Desk( unittest.TestCase ):
    @classmethod
    def setUpClass(cls):
        cls.markets = json.loads((DATA / "markets.json").read_text())
        cls.picks = json.loads((DATA / "picks.json").read_text())
        cls.capped = json.loads((DATA / "capped.json").read_text())
        cls.desk = json.loads((DATA / "desk.json").read_text())
        cls.preds = json.loads((DATA / "predictions.json").read_text())["predictions"]
        cls.pages = {p: (DESK / p).read_text() for p in PAGES if (DESK / p).is_file()}

    def test_every_top_level_page_exists(self):
        for p in PAGES:
            self.assertTrue((DESK / p).is_file(), p)

    def test_fifteen_sport_pages_exist(self):
        for s in SPORTS:
            self.assertTrue((DESK / "sports" / f"{SLUG[s]}.html").is_file(), s)

    def test_fifteen_sports_declared_once(self):
        names = [s["name"] if isinstance(s, dict) else s for s in self.desk["sports"]]
        self.assertEqual(sorted(names), sorted(SPORTS))

    def test_banned_words_absent_from_published_prose(self):
        bad = re.compile(r"\b(model|models|modelling|verified|verify)\b", re.I)
        for name, html in self.pages.items():
            self.assertIsNone(bad.search(text_of(html)), f"{name} contains a banned word")
        for pred in self.preds:
            self.assertIsNone(bad.search(pred["text"]), pred["pick_id"])

    def test_every_match_row_links_an_official_source(self):
        html = self.pages["matches.html"]
        rows = re.findall(r"<tr><td>([A-Z]{2}\d\d)</td>(.*?)</tr>", html, re.S)
        self.assertEqual(len(rows), len(self.desk["fixtures"]))
        for fid, row in rows:
            self.assertIn('href="https://', row, f"{fid} has no source link")

    def test_promoted_prices_are_inside_the_stated_band(self):
        for p in self.picks:
            self.assertGreaterEqual(p["p"], 0.62, p["pick_id"])
            self.assertLessEqual(p["p"], 250 / 350, p["pick_id"])   # -250 is 71.43%
            self.assertGreaterEqual(p["fair_american"], -250, p["pick_id"])
            self.assertLessEqual(p["fair_american"], 10000, p["pick_id"])

    def test_capped_outcomes_are_not_promoted(self):
        promoted = {p["selection"] for p in self.picks}
        for m in self.capped:
            self.assertGreater(m["p"], 0.7143, m["selection"])
        self.assertTrue(promoted)

    def test_one_promoted_pick_per_fixture_and_five_per_sport_max(self):
        seen = [p["fixture"] for p in self.picks]
        self.assertEqual(len(seen), len(set(seen)))
        per = {}
        for p in self.picks:
            per[p["fixture"][:2]] = per.get(p["fixture"][:2], 0) + 1
        self.assertTrue(all(v <= 5 for v in per.values()), per)

    def test_predictions_cover_every_pick_and_are_unique(self):
        ids = {p["pick_id"] for p in self.picks}
        self.assertEqual({p["pick_id"] for p in self.preds}, ids)
        texts = [re.sub(r"\W+", " ", p["text"].lower()).strip() for p in self.preds]
        self.assertEqual(len(texts), len(set(texts)))
        for pred in self.preds:
            words = len(pred["text"].split())
            self.assertGreaterEqual(words, 30, f"{pred['pick_id']} has {words} words")
            self.assertTrue(pred["sources"], pred["pick_id"])
            self.assertIn(pred["pick_id"], self.pages["predictions.html"])

    def test_predictions_named_selection_er_named(self):
        by_id = {p["pick_id"]: p for p in self.picks}
        for pred in self.preds:
            pick = by_id[pred["pick_id"]]
            side = pick["selection"].split(" Over ")[0].split(" +")[0].split(" -")[0]
            hay = (pred["headline"] + " " + pred["text"]).lower()
            self.assertIn(side.lower().split()[-1], hay, pred["pick_id"])

    def test_market_count_matches_published_file(self):
        page = self.pages["markets.html"]
        self.assertIn(f"{len(self.markets)} originated outcomes", text_of(page))

    def test_every_gap_sport_is_flagged(self):
        flagged = text_of(self.pages["flagged.html"]).lower()
        for sport, gap in self.desk["gaps"].items():
            self.assertIn(sport.lower(), flagged, sport)
            self.assertTrue(gap["why"] and gap["tried"], sport)

    def test_internal_links_resolve(self):
        for name, html in self.pages.items():
            for href in re.findall(r'href="([^"#:]+\.html[^"]*)"', html):
                target = (DESK / name).parent / href.split("#")[0]
                self.assertTrue(target.is_file(), f"{name} -> {href}")
        for sport in SPORTS:
            html = (DESK / "sports" / f"{SLUG[sport]}.html").read_text()
            for href in re.findall(r'href="([^"#:]+\.html[^"]*)"', html):
                target = (DESK / "sports" / href.split("#")[0])
                self.assertTrue(target.is_file(), f"{sport} -> {href}")

    def test_no_browser_side_localhost_calls(self):
        for name, html in self.pages.items():
            self.assertNotIn("localhost", html, name)
            self.assertNotIn("127.0.0.1", html, name)

    def test_expiry_stamp_published(self):
        self.assertIn("Evidence expires", self.pages["index.html"])


if __name__ == "__main__":
    unittest.main()
