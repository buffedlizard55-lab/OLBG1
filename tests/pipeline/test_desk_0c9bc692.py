"""Regression checks for the namespaced 0c9bc692 evidence desk."""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "0c9bc692"
SITE = ROOT / "0c9bc692"


class Desk0C9Tests(unittest.TestCase):
    def read(self, name: str):
        return json.loads((DATA / name).read_text(encoding="utf-8"))

    def test_summary_is_honest_about_high_picks(self):
        summary = self.read("summary.json")
        self.assertEqual(summary["sports"], 15)
        self.assertEqual(summary["high_confidence_picks"], 0)
        self.assertEqual(summary["originated_price_rows"], 1)

    def test_every_fixture_has_a_source_and_no_official_claim_for_olbg_only_row(self):
        source_ids = {x["id"] for x in self.read("sources.json")["sources"]}
        for fixture in self.read("fixtures.json")["fixtures"]:
            self.assertIn(fixture["official_source"], source_ids)
            if fixture["status"] == "OLBG discovery only":
                self.assertIn("unconfirmed", fixture["notes"].lower())

    def test_written_note_is_full_length_and_without_banned_prediction_words(self):
        predictions = self.read("predictions.json")["predictions"]
        self.assertEqual(len(predictions), 1)
        text = predictions[0]["text"]
        self.assertGreaterEqual(len(re.findall(r"\b[\w’'-]+\b", text)), 30)
        self.assertIsNone(re.search(r"\b(model|verified)\b", text, re.I))

    def test_every_named_sport_has_a_category_page(self):
        coverage = self.read("coverage.json")["coverage"]
        self.assertEqual(len(coverage), 15)
        for sport in coverage:
            page = SITE / "sports" / f"{sport['sport_key']}.html"
            self.assertTrue(page.exists(), str(page))


if __name__ == "__main__":
    unittest.main()
