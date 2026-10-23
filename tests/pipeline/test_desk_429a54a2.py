"""Regression gates for the 429a54a2 desk (structural, no network)."""

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "429a54a2"


class Desk429a54a2Test(unittest.TestCase):
    def setUp(self):
        self.fixtures = json.loads((DATA / "fixtures.json").read_text())
        self.preds = json.loads((DATA / "predictions.json").read_text())

    def test_every_row_has_an_official_link_and_window(self):
        for f in self.fixtures:
            self.assertTrue(f["official_url"].startswith("https://"), f["id"])
            host = f["official_url"].split("/")[2]
            if f["status"] != "unverified":
                self.assertNotIn("olbg", host, f"{f['id']}: discovery source used as verification")
            self.assertTrue(f["observed"], f["id"])

    def test_unverified_and_elapsed_rows_are_never_priced(self):
        for f in self.fixtures:
            if f["status"] != "verified":
                self.assertEqual(f["price"]["markets"], [], f["id"])
                self.assertIsNone(f["price"]["selection"], f["id"])

    def test_high_picks_clear_both_gates(self):
        for f in self.fixtures:
            p = f["price"]
            if p["tier"] == "High":
                self.assertGreaterEqual(p["probability"], 0.70, f["id"])
                self.assertGreaterEqual(p["fair_decimal"], 1.40, f["id"])
                self.assertLessEqual(p["fair_decimal"], 101.0, f["id"])
            if p["tier"] and p["tier"].startswith("High ("):
                self.assertGreaterEqual(p["probability"], 0.70, f["id"])
                self.assertLess(p["fair_decimal"], 1.40, f["id"])

    def test_prices_are_fair_and_mass_sums_to_one(self):
        for f in self.fixtures:
            for m in f["price"]["markets"]:
                self.assertAlmostEqual(m["fair_decimal"] * m["probability"], 1.0, places=9)
            two = [m for m in f["price"]["markets"] if m["market"] == "match_winner"]
            if two:
                self.assertAlmostEqual(sum(m["probability"] for m in two), 1.0, places=6)

    def test_predictions_are_long_unique_and_free_of_internal_words(self):
        seen = []
        for p in self.preds:
            words = p["text"].split()
            self.assertGreaterEqual(len(words), 30, p["id"])
            for bad in ("model", "verified"):
                self.assertIsNone(re.search(rf"\b{bad}\b", p["text"], re.I), f"{p['id']} contains {bad}")
            tokens = re.findall(r"[a-z0-9']+", p["text"].lower())
            grams = {" ".join(tokens[i:i + 6]) for i in range(len(tokens) - 5)}
            for other in seen:
                self.assertFalse(grams & other, f"{p['id']} repeats a six-word phrase")
            seen.append(grams)

    def test_desk_validator_exits_clean(self):
        result = subprocess.run([sys.executable, "scripts/s429a54a2_validate.py"], cwd=ROOT,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
