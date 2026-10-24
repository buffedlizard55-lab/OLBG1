#!/usr/bin/env python3
"""Desk 02d3d515 gate: scope, provenance, arithmetic, prose and site links.

The desk covers exactly the fifteen sports in the brief, only publishes a line
where an official page was read, and keeps every price fair (zero-vig).
"""
from __future__ import annotations

import json
import re
import sys
import unittest
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from s02d3d515_data import (FIXTURES, FLAGS, OLBG_ROUTES, PICKS, SOURCES,
                            SPORTS, WITHHELD, OBSERVED)
from s02d3d515_model import (BAND_MAX_PROB, BAND_MIN_PROB, american_from_prob,
                             decimal_from_prob, in_band, prob_from_american,
                             two_way)

DATA = ROOT / "data" / "02d3d515"
SITE = ROOT / "02d3d515"

SCOPE = {
    "Golf", "Volleyball", "Rugby Union", "Cricket", "Snooker", "Darts",
    "Baseball", "Gaelic Sports", "Greyhounds", "Tennis", "Motor Racing",
    "Handball", "Ice Hockey", "Basketball", "Rugby League",
}
BANNED = ("model", "verified")
OFFICIAL_HOSTS = {urlsplit(s["url"]).netloc for s in SOURCES if s["official"]}


class TestScope(unittest.TestCase):
    def test_fifteen_sports_in_brief_order(self):
        self.assertEqual(len(SPORTS), 15)
        self.assertEqual({name for _, name, _ in SPORTS}, SCOPE)

    def test_every_sport_has_a_page_and_a_route(self):
        for slug, name, _ in SPORTS:
            self.assertTrue((SITE / "sports" / f"{slug}.html").exists(), slug)
        routes = {sport for sport, *_ in OLBG_ROUTES}
        self.assertEqual(routes, SCOPE)

    def test_fixtures_stay_inside_scope(self):
        for fx in FIXTURES:
            self.assertIn(fx["sport"], {slug for slug, _, _ in SPORTS}, fx["id"])


class TestProvenance(unittest.TestCase):
    def test_sources_are_https_and_two_roles(self):
        for s in SOURCES:
            self.assertTrue(s["url"].startswith("https://"), s["id"])
            self.assertIn(s["official"], (True, False))
            self.assertTrue(s["observed"], s["id"])

    def test_every_fixture_cites_a_source(self):
        ids = {s["id"] for s in SOURCES}
        for fx in FIXTURES:
            self.assertIn(fx["source"], ids, fx["id"])

    def test_olbg_is_never_the_match_source(self):
        discovery = {s["id"] for s in SOURCES if not s["official"]}
        for fx in FIXTURES:
            self.assertNotIn(fx["source"], discovery, fx["id"])

    def test_priced_fixtures_read_both_sides(self):
        for p in PICKS:
            fx = next(f for f in FIXTURES if f["id"] == p["fixture"])
            facts = fx["facts"]
            self.assertTrue(facts, f"{fx['id']}: no form facts")
            self.assertNotIn("time unverified", json.dumps(facts).lower())

    def test_withheld_rows_name_what_is_missing(self):
        ids = {f["id"] for f in FIXTURES}
        for fid, missing, why in WITHHELD:
            self.assertIn(fid, ids)
            self.assertTrue(missing and why)


class TestPrices(unittest.TestCase):
    def test_fair_decimal_is_reciprocal(self):
        for p in PICKS:
            self.assertAlmostEqual(p["prob"] * decimal_from_prob(p["prob"]), 1.0, places=9)

    def test_american_conversion_round_trips(self):
        for p in PICKS:
            self.assertEqual(american_from_prob(p["prob"]), p.get("price", american_from_prob(p["prob"])))
            back = prob_from_american(american_from_prob(p["prob"]))
            self.assertAlmostEqual(back, p["prob"], places=2)

    def test_two_way_book_sums_to_one(self):
        for p in PICKS:
            if p["market"] != "Match winner":
                continue
            book = two_way(p["prob"])
            self.assertAlmostEqual(sum(o["prob"] for o in book), 1.0, places=9)

    def test_high_picks_sit_in_the_window(self):
        for p in PICKS:
            if p["confidence"] != "high":
                continue
            self.assertTrue(in_band(p["prob"]), p["selection"])
            self.assertGreaterEqual(american_from_prob(p["prob"]), -250, p["selection"])
            self.assertLessEqual(american_from_prob(p["prob"]), 10000, p["selection"])

    def test_window_bounds_are_the_requested_odds(self):
        self.assertEqual(american_from_prob(BAND_MAX_PROB), -250)
        self.assertEqual(american_from_prob(BAND_MIN_PROB), 10000)


class TestProse(unittest.TestCase):
    def test_predictions_are_long_enough_and_unique(self):
        texts = [p["prediction"] for p in PICKS]
        self.assertEqual(len(texts), len(set(texts)))
        for p in PICKS:
            self.assertGreaterEqual(len(p["prediction"].split()), 30, p["selection"])

    def test_banned_words_absent(self):
        blob = " ".join(p["prediction"] for p in PICKS).lower()
        for bad in BANNED:
            self.assertIsNone(re.search(rf"\b{bad}\w*", blob), bad)

    def test_no_repeated_six_word_run(self):
        grams = Counter()
        for p in PICKS:
            words = re.findall(r"[a-z0-9']+", p["prediction"].lower())
            for i in range(len(words) - 5):
                grams[" ".join(words[i:i + 6])] += 1
        self.assertEqual([g for g, n in grams.items() if n > 1], [])

    def test_each_prediction_names_a_team_or_player(self):
        for p in PICKS:
            fx = next(f for f in FIXTURES if f["id"] == p["fixture"])
            names = [t for t in re.split(r"[^A-Za-z]+", " ".join([p["selection"], fx["a"], fx["b"]]))
                     if len(t) > 3]
            self.assertTrue(any(n.lower() in p["prediction"].lower() for n in names),
                            f"{p['selection']}: prose does not name the side")

    def test_selection_is_stated_plainly(self):
        for p in PICKS:
            low = p["prediction"].lower()
            markers = ("take ", "back ", "backing", "selection", "pick", "fancy",
                       "side with", "call", "point to", "lean", "edge", "favour",
                       "favor", "should", "price", "value", "for a", "for the")
            self.assertTrue(any(m in low for m in markers),
                            p["selection"])


class TestFlags(unittest.TestCase):
    def test_flag_ids_unique_and_linked(self):
        ids = [f["id"] for f in FLAGS]
        self.assertEqual(len(ids), len(set(ids)))
        for f in FLAGS:
            self.assertTrue(f["link"].startswith("https://"), f["id"])

    def test_coverage_shortfall_is_flagged(self):
        self.assertTrue(any(f["id"] == "F-11" for f in FLAGS))

    def test_observation_time_present(self):
        self.assertRegex(OBSERVED, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


class TestSite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = {p.relative_to(SITE).as_posix(): p.read_text(encoding="utf-8")
                     for p in SITE.rglob("*.html")}

    def test_page_count_and_titles(self):
        self.assertEqual(len(self.pages), 26)
        for name, html in self.pages.items():
            self.assertEqual(html.count("<h1"), 1, name)
            self.assertIn("<title>", html, name)

    def test_navigation_reaches_every_category(self):
        index = self.pages["index.html"]
        for href in ("picks.html", "matches.html", "markets.html", "predictions.html",
                     "sports.html", "sources.html", "methodology.html", "flagged.html"):
            self.assertIn(f'href="{href}"', index, href)

    def test_every_sport_page_is_linked(self):
        sports = self.pages["sports.html"]
        for slug, _, _ in SPORTS:
            self.assertIn(f'href="sports/{slug}.html"', sports, slug)

    def test_local_links_resolve(self):
        for name, html in self.pages.items():
            base = (SITE / name).parent
            for href in re.findall(r'href="([^"]+)"', html):
                u = urlsplit(href)
                if u.scheme or href.startswith("#"):
                    continue
                target = (base / u.path).resolve() if u.path else (SITE / name)
                self.assertTrue(target.exists(), f"{name}: broken link {href}")

    def test_json_export_matches_module(self):
        desk = json.loads((DATA / "desk.json").read_text(encoding="utf-8"))
        self.assertEqual(len(desk["picks"]), len(PICKS))
        self.assertEqual(len(desk["fixtures"]), len(FIXTURES))
        self.assertEqual(desk["observed"], OBSERVED)

    def test_banned_words_absent_from_html(self):
        # allowed only in the methodology paragraph that explains why they are avoided
        for name, html in self.pages.items():
            body = re.sub(r"<[^>]+>", " ", html).lower()
            for bad in BANNED:
                hits = re.findall(rf"\b{bad}\w*", body)
                self.assertEqual(hits, [], f"{name}: {bad}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
