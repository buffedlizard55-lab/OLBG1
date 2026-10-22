"""Automated CI regression gate for session 3ee30bba-olbg1 (/3ee30bba/ & data/3ee30bba/)."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESK = ROOT / "data" / "3ee30bba" / "desk.json"
VALIDATOR = ROOT / "scripts" / "s3ee30bba_validate.py"


@unittest.skipUnless(DESK.is_file(), "3ee30bba desk not yet generated")
class Desk3ee30bbaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.desk = json.loads(DESK.read_text(encoding="utf-8"))

    def test_validator_passes_cleanly(self) -> None:
        res = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(res.returncode, 0, msg=f"stdout:\n{res.stdout}\nstderr:\n{res.stderr}")

    def test_all_high_picks_clear_70_percent_and_price_band(self) -> None:
        picks = self.desk["high_picks"]
        self.assertEqual(len(picks), 13)
        for p in picks:
            with self.subTest(pick=p["market_id"], selection=p["selection"]):
                self.assertGreater(p["probability"], 0.70)
                self.assertLessEqual(p["probability"], 1.0 / 1.4 + 1e-9)
                self.assertGreaterEqual(p["american"], -250)
                self.assertLessEqual(p["american"], 10000)

    def test_predictions_bijection_word_count_and_uniqueness(self) -> None:
        preds = self.desk["predictions"]
        self.assertEqual(len(preds), len(self.desk["high_picks"]))
        bodies = []
        for pred in preds:
            words = pred["body"].split()
            self.assertGreaterEqual(len(words), 30, pred["id"])
            self.assertIn(pred["selection"], pred["body"], pred["id"])
            bodies.append(pred["body"])
        self.assertEqual(len(bodies), len(set(bodies)))


if __name__ == "__main__":
    unittest.main()
