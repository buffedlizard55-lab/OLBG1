"""Focused standard-library tests for the 23728b2b research desk."""
from __future__ import annotations

import re
import unittest
from datetime import datetime
from pathlib import Path

from scripts.s23728b2b_data import FIXTURES, OBSERVED, PICKS, SOURCES, SPORTS
from scripts.s23728b2b_lib import assemble, confidence, display_american, fair_american, fair_decimal


class TestFairPriceArithmetic(unittest.TestCase):
    def test_decimal_is_reciprocal(self):
        self.assertAlmostEqual(fair_decimal(.68), 1.4705882352941176)

    def test_favorite_american_price(self):
        self.assertAlmostEqual(fair_american(.68), -212.5)

    def test_underdog_american_price(self):
        self.assertAlmostEqual(fair_american(.34), 194.11764705882354)

    def test_american_round_trip(self):
        for probability in [.05, .34, .5, .68, .71, .86]:
            with self.subTest(probability=probability):
                american = fair_american(probability)
                decimal = 1 + american / 100 if american > 0 else 1 + 100 / -american
                self.assertAlmostEqual(1 / decimal, probability)

    def test_display_price_has_explicit_sign(self):
        self.assertEqual(display_american(.68), "-213")
        self.assertEqual(display_american(.34), "+194")


class TestConfidenceGate(unittest.TestCase):
    def test_high_requires_strict_probability(self):
        self.assertEqual(confidence(.70), "Medium")
        self.assertEqual(confidence(.71), "High")

    def test_short_price_cannot_be_high(self):
        self.assertEqual(confidence(.86), "Medium")
        self.assertLess(fair_american(.86), -250)

    def test_probability_above_band_edge_cannot_be_high(self):
        self.assertEqual(confidence(.715), "Medium")
        self.assertLess(fair_american(.715), -250)

    def test_negative_250_boundary_is_allowed(self):
        probability = 5 / 7
        self.assertAlmostEqual(fair_american(probability), -250)
        self.assertEqual(confidence(probability), "High")

    def test_low_and_medium_boundaries(self):
        self.assertEqual(confidence(.54), "Low")
        self.assertEqual(confidence(.55), "Medium")


class TestDeskRecords(unittest.TestCase):
    def test_exact_requested_sports(self):
        self.assertEqual(len(SPORTS), 15)
        self.assertEqual(dict(SPORTS)["gaelic-sports"], "Gaelic Sports")
        self.assertEqual(dict(SPORTS)["motor-racing"], "Motor Racing")

    def test_expected_card_shape(self):
        desk = assemble()
        self.assertEqual(len(FIXTURES), 55)
        self.assertEqual(len(PICKS), 53)
        self.assertEqual(desk["summary"]["alternative_lines"], 85)
        self.assertEqual(desk["summary"]["total_lines"], 138)
        self.assertEqual(desk["summary"]["sports_with_prices"], 12)

    def test_all_fixture_sources_are_official(self):
        sources = {source["id"]: source for source in SOURCES}
        for fixture in FIXTURES:
            self.assertTrue(sources[fixture["source"]]["official"])
            self.assertTrue(all(sources[sid]["official"] for sid in fixture["extra_sources"]))

    def test_seven_high_picks_have_long_unique_prose(self):
        desk = assemble()
        high = [line for line in desk["lines"] if line["role"] == "primary" and line["confidence"] == "High"]
        self.assertEqual(len(high), 7)
        predictions = {prediction["fixture"]: prediction["text"] for prediction in desk["predictions"]}
        self.assertEqual(len(set(predictions.values())), 53)
        for line in high:
            self.assertGreaterEqual(len(re.findall(r"\b[\w’'-]+\b", predictions[line["fixture"]])), 30)
            fixture = desk["fixture_by_id"][line["fixture"]]
            self.assertTrue(fixture["side_evidence"]["a"] and fixture["side_evidence"]["b"])

    def test_prediction_vocabulary_excludes_internal_terms(self):
        for pick in PICKS:
            self.assertIsNone(re.search(r"\b(?:model|verified)\b", pick["prediction"], re.I))

    def test_all_rows_upcoming_at_snapshot_or_time_blank(self):
        cut = datetime.fromisoformat(OBSERVED.replace("Z", "+00:00"))
        for fixture in FIXTURES:
            if fixture["start_utc"]:
                self.assertGreater(datetime.fromisoformat(fixture["start_utc"].replace("Z", "+00:00")), cut)
            else:
                self.assertIn("start_utc", fixture["missing_fields"])
                self.assertTrue(fixture["flag_ids"])

    def test_withheld_and_context_rows_have_no_primary_line(self):
        priced = {pick["fixture"] for pick in PICKS}
        self.assertNotIn("da-pri-bun", priced)
        self.assertNotIn("rl-aus-fij", priced)

    def test_rendered_site_and_data_exist(self):
        root = Path(__file__).resolve().parents[2]
        self.assertTrue((root / "23728b2b" / "index.html").is_file())
        self.assertEqual(len(list((root / "23728b2b" / "sports").glob("*.html"))), 15)
        self.assertTrue((root / "data" / "23728b2b" / "desk.json").is_file())


if __name__ == "__main__":
    unittest.main()
