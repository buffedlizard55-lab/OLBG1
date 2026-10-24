#!/usr/bin/env python3
"""Desk 37003e61 gate: scope, provenance, arithmetic, pick rules and site links."""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from s37003e61_data import CAPTURED, FIXTURES, OLBG_ROUTES, SOURCES, SPORTS
from s37003e61_engine import (BAND_CEILING, BAND_HIGH, BAND_LOW, HIGH_FLOOR,
                              american, in_band, price_book)
from s37003e61_predictions import NOT_PICKED, PREDICTIONS

SITE = ROOT / "37003e61"
DATA = ROOT / "data" / "37003e61"
SPORT_SLUGS = [s[0] for s in SPORTS]
BOOKS = {f["id"]: price_book(f) for f in FIXTURES}
HIGH = [(f, BOOKS[f["id"]]["high"]) for f in FIXTURES if BOOKS[f["id"]].get("high")]
BANNED = re.compile(r"\bmodel\b|\bverified\b", re.I)


def words(text):
    return re.findall(r"[A-Za-z0-9'’\-]+", text)


def grams(text, n=7):
    w = [x.lower() for x in words(text)]
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}


class TestScope(unittest.TestCase):
    def test_fifteen_sports_requested(self):
        self.assertEqual(len(SPORTS), 15)
        self.assertEqual(len({s[0] for s in SPORTS}), 15)

    def test_every_requested_sport_has_a_page(self):
        for slug in SPORT_SLUGS:
            self.assertTrue((SITE / "sports" / f"{slug}.html").exists(), slug)

    def test_every_requested_sport_has_an_olbg_route(self):
        self.assertEqual(len(OLBG_ROUTES), 15)
        for sport, sid, url, _ in OLBG_ROUTES:
            self.assertTrue(url.startswith("https://www.olbg.com/betting-tips/"))
            self.assertIsInstance(sid, int)

    def test_sport_ids_match_the_known_map(self):
        expected = {"Tennis": 3, "Basketball": 4, "Golf": 5, "Cricket": 7, "Snooker": 8,
                    "Rugby Union": 9, "Rugby League": 10, "Baseball": 12, "Ice Hockey": 13,
                    "Motor Racing": 14, "Darts": 15, "Handball": 20, "Volleyball": 21,
                    "Gaelic Football": 25, "Greyhounds": 28}
        got = {sport: sid for sport, sid, _, _ in OLBG_ROUTES}
        self.assertEqual(got, expected)


class TestFixtures(unittest.TestCase):
    def test_ids_unique(self):
        ids = [f["id"] for f in FIXTURES]
        self.assertEqual(len(ids), len(set(ids)))

    def test_sports_are_in_scope(self):
        for fx in FIXTURES:
            self.assertIn(fx["sport"], SPORT_SLUGS, fx["id"])

    def test_sources_resolve(self):
        for fx in FIXTURES:
            self.assertTrue(fx["sources"], f"{fx['id']}: no sources")
            for sid in fx["sources"]:
                self.assertIn(sid, SOURCES, f"{fx['id']}: {sid}")

    def test_source_urls_https(self):
        for sid, s in SOURCES.items():
            self.assertTrue(s["url"].startswith("https://"), sid)
            self.assertEqual(urlsplit(s["url"]).scheme, "https")
            self.assertIn(s["status"], {"read", "failed"})

    def test_status_values(self):
        for fx in FIXTURES:
            self.assertIn(fx["status"], {"official", "olbg_only"}, fx["id"])

    def test_olbg_only_rows_carry_no_price(self):
        for fx in FIXTURES:
            if fx["status"] == "olbg_only":
                self.assertEqual(BOOKS[fx["id"]]["markets"], [], fx["id"])
                self.assertTrue(fx["flags"], fx["id"])

    def test_unpriced_official_rows_explain_themselves(self):
        for fx in FIXTURES:
            if fx["status"] == "official" and not BOOKS[fx["id"]]["rated"]:
                self.assertTrue(fx["flags"] or fx["id"] in NOT_PICKED, fx["id"])

    def test_capture_stamp_is_iso(self):
        self.assertRegex(CAPTURED, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


class TestArithmetic(unittest.TestCase):
    def test_two_way_mass(self):
        for fx in FIXTURES:
            for m in BOOKS[fx["id"]]["markets"]:
                total = sum(o["probability"] for o in m["outcomes"])
                self.assertAlmostEqual(total, 1.0, places=6, msg=f"{fx['id']}/{m['key']}")

    def test_decimal_times_probability(self):
        for fx in FIXTURES:
            for m in BOOKS[fx["id"]]["markets"]:
                for o in m["outcomes"]:
                    self.assertAlmostEqual(o["fair_decimal"] * o["probability"], 1.0, places=3)

    def test_probabilities_strictly_inside_unit_interval(self):
        for fx in FIXTURES:
            for m in BOOKS[fx["id"]]["markets"]:
                for o in m["outcomes"]:
                    self.assertTrue(0.0 < o["probability"] < 1.0)

    def test_band_flag_agrees_with_american(self):
        for fx in FIXTURES:
            for m in BOOKS[fx["id"]]["markets"]:
                for o in m["outcomes"]:
                    self.assertEqual(o["in_band"], BAND_LOW <= o["fair_american"] <= BAND_HIGH)

    def test_american_round_trips(self):
        self.assertEqual(american(1.4), -250)
        self.assertEqual(american(2.0), 100)
        self.assertEqual(american(11.0), 1000)

    def test_window_is_narrow_by_construction(self):
        self.assertAlmostEqual(BAND_CEILING * 100, 71.42857, places=4)
        self.assertTrue(in_band(BAND_CEILING - 1e-6))
        self.assertFalse(in_band(0.75))


class TestHighPicks(unittest.TestCase):
    def test_high_picks_exist(self):
        self.assertGreaterEqual(len(HIGH), 5)

    def test_every_high_pick_passes_both_gates(self):
        for fx, h in HIGH:
            self.assertGreater(h["probability"], HIGH_FLOOR, fx["id"])
            self.assertLessEqual(h["probability"], BAND_CEILING + 1e-9, fx["id"])
            self.assertGreaterEqual(h["fair_american"], BAND_LOW, fx["id"])
            self.assertLessEqual(h["fair_american"], BAND_HIGH, fx["id"])

    def test_every_high_pick_has_a_write_up(self):
        for fx, _ in HIGH:
            self.assertIn(fx["id"], PREDICTIONS)

    def test_no_write_up_without_a_high_pick(self):
        high_ids = {fx["id"] for fx, _ in HIGH}
        for fid in PREDICTIONS:
            self.assertIn(fid, high_ids)

    def test_high_picks_span_more_than_one_sport(self):
        self.assertGreaterEqual(len({fx["sport"] for fx, _ in HIGH}), 3)


class TestPredictions(unittest.TestCase):
    def test_minimum_length(self):
        for fid, p in PREDICTIONS.items():
            self.assertGreaterEqual(len(words(p["text"])), 30, fid)

    def test_no_internal_terms(self):
        for fid, p in PREDICTIONS.items():
            self.assertIsNone(BANNED.search(p["text"]), fid)

    def test_no_repeated_seven_word_phrase(self):
        seen = {}
        for fid, p in PREDICTIONS.items():
            for g in grams(p["text"]):
                self.assertFalse(g in seen and seen[g] != fid, f"{fid}: repeated phrase {g!r}")
                seen[g] = fid

    def test_each_write_up_carries_sources(self):
        for fid, p in PREDICTIONS.items():
            self.assertTrue(p["basis"], fid)
            for label, fact in p["basis"]:
                self.assertTrue(label and fact)

    def test_write_ups_are_not_padded_with_boilerplate(self):
        starts = [p["text"][:40] for p in PREDICTIONS.values()]
        self.assertEqual(len(starts), len(set(starts)))


class TestExports(unittest.TestCase):
    def test_json_exports_load(self):
        for name in ("fixtures", "markets", "picks", "predictions", "sources", "flagged", "summary"):
            path = DATA / f"{name}.json"
            self.assertTrue(path.exists(), name)
            json.loads(path.read_text())

    def test_summary_matches_the_data(self):
        summary = json.loads((DATA / "summary.json").read_text())
        self.assertEqual(summary["fixtures"], len(FIXTURES))
        self.assertEqual(summary["high"], len(HIGH))
        self.assertEqual(summary["sport_count"], 15)

    def test_matches_csv_header(self):
        lines = (DATA / "matches.csv").read_text().strip().splitlines()
        self.assertEqual(lines[0].split(",")[:5], ["id", "sport", "competition", "home", "away"])
        self.assertEqual(len(lines) - 1, len(FIXTURES))


class TestSite(unittest.TestCase):
    def test_pages_exist(self):
        for name in ("index", "picks", "predictions", "matches", "markets", "sports",
                     "sources", "flagged", "methodology", "reverse-engineering", "repo-audit"):
            self.assertTrue((SITE / f"{name}.html").exists(), name)

    def test_every_page_has_navigation_and_title(self):
        pages = list(SITE.glob("*.html")) + list((SITE / "sports").glob("*.html"))
        for page in pages:
            text = page.read_text(encoding="utf-8")
            self.assertIn("<title>", text, page.name)
            self.assertIn('class="main"', text, page.name)
            self.assertGreater(len(text), 1500, page.name)

    def test_no_broken_local_links(self):
        pages = list(SITE.glob("*.html")) + list((SITE / "sports").glob("*.html"))
        for page in pages:
            text = page.read_text(encoding="utf-8")
            for href in set(re.findall(r'href="([^"#?]+)', text)):
                if href.startswith(("http://", "https://", "mailto:", "data:")):
                    continue
                self.assertTrue((page.parent / href).exists(), f"{page.name}: {href}")

    def test_no_conflict_markers(self):
        for page in list(SITE.glob("*.html")) + list((SITE / "sports").glob("*.html")):
            self.assertNotRegex(page.read_text(encoding="utf-8"),
                                r"^(<<<<<<<|>>>>>>>|=======)$", page.name)

    def test_index_shows_the_picks_above_the_fold(self):
        text = (SITE / "index.html").read_text(encoding="utf-8")
        self.assertIn("High-confidence picks", text)
        self.assertIn("Executive summary", text)

    def test_index_links_every_high_pick(self):
        text = (SITE / "index.html").read_text(encoding="utf-8")
        for fx, _ in HIGH:
            self.assertIn(f'href="predictions.html#{fx["id"]}"', text, fx["id"])

    def test_site_does_not_claim_guaranteed_returns(self):
        for page in SITE.glob("*.html"):
            text = page.read_text(encoding="utf-8").lower()
            self.assertNotIn("guaranteed profit", text, page.name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
