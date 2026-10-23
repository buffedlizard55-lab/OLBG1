import datetime as dt
import json
import unittest
from pathlib import Path

from scripts.s99659729_audit import audit


class FreshnessAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.as_of = dt.datetime.fromisoformat("2026-10-23T21:26:46+00:00")
        cls.result = audit(cls.as_of)

    def test_exact_15_sport_scope_is_present(self):
        self.assertEqual(self.result["counts"]["sports_present"], 15)
        self.assertEqual(set(self.result["scope"]), set(self.result["counts"]["sports"]))

    def test_audit_discloses_it_did_not_refresh_live_sources(self):
        self.assertFalse(self.result["live_official_refresh_performed"])
        self.assertGreater(self.result["snapshot_age_minutes"], 50)

    def test_strict_high_gate_applied_to_inherited_high_labels(self):
        counts = self.result["counts"]
        self.assertEqual(counts["high_labeled_rows"], 51)
        self.assertEqual(counts["strict_high_gate_rows"], 3)
        self.assertEqual(counts["high_labeled_rows_failing_strict_gate"], 48)
        for row in self.result["findings"]["strict_high_gate_rows"]:
            self.assertGreater(row["probability"], 0.70)
            self.assertGreaterEqual(row["fair_american"], -250)
            self.assertLessEqual(row["fair_american"], 10000)
            self.assertTrue(row["source"].startswith("https://"))

    def test_elapsed_and_near_start_events_are_flagged_not_regraded_as_results(self):
        findings = self.result["findings"]
        self.assertEqual([x["id"] for x in findings["elapsed_start_rows"]], ["GH01"])
        self.assertEqual(len(findings["starts_within_two_hours"]), 6)
        self.assertEqual(len(findings["missing_exact_start_rows"]), 9)

    def test_fixture_and_market_rows_retain_sources(self):
        counts = self.result["counts"]
        self.assertEqual(counts["fixture_source_missing"], 0)
        self.assertEqual(counts["market_rows_without_https_source"], 0)
        self.assertEqual(counts["market_rows_with_unknown_fixture"], 0)

    def test_market_semantics_are_not_misrepresented_as_sum_to_one(self):
        counts = self.result["counts"]
        self.assertEqual(counts["incomplete_best_of_five_score_books"], 5)
        self.assertEqual(counts["nonexclusive_driver_markets_flagged_for_joint_consistency"], 2)
        for group in self.result["findings"]["nonexclusive_driver_markets"]:
            self.assertIn("probability_sum_not_a_one-sum_test", group)

    def test_prediction_prose_structural_gates(self):
        findings = self.result["findings"]
        self.assertEqual(findings["prediction_prose_violations"], [])
        self.assertEqual(findings["duplicate_prediction_text_count"], 0)
        self.assertEqual(findings["prediction_source_missing_ids"], [])

    def test_published_dashboard_pages_have_disclosures_and_links(self):
        root = Path(__file__).resolve().parents[2] / "99659729"
        for filename in ("index.html", "matches.html", "flagged.html"):
            self.assertTrue((root / filename).is_file())
            content = (root / filename).read_text(encoding="utf-8")
            self.assertIn("no live sports-source refresh", content.lower())
            self.assertIn("https://", content)
        page = (root / "index.html").read_text(encoding="utf-8")
        self.assertIn("https://api-web.nhle.com/v1/schedule/2026-10-23", page)
        self.assertNotIn("%7C", page)


if __name__ == "__main__":
    unittest.main()
