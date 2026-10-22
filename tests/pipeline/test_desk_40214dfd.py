"""Publication gate for the 40214dfd desk.

These tests are deliberately cheap and read-only: they run the desk's own validator and
then re-assert the two invariants the brief is strictest about (a High pick must clear
70%, and every High price must sit inside the -250..+10000 band) straight from
``data/40214dfd/desk.json``, so a hand edit to the JSON cannot pass silently.
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESK = ROOT / "data" / "40214dfd" / "desk.json"
VALIDATOR = ROOT / "scripts" / "s40214dfd_validate.py"

# The brief's band: -250 is the shortest price allowed, +10000 the longest.
BAND_LOW_AMERICAN = -250
BAND_HIGH_AMERICAN = 10000
MIN_HIGH_PROBABILITY = 0.70


@unittest.skipUnless(DESK.is_file(), "desk data not present")
class Desk40214DfdTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.desk = json.loads(DESK.read_text())

    def test_validator_exits_clean(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(
            result.returncode,
            0,
            msg=f"validator failed\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )

    def test_every_high_pick_clears_seventy_percent(self) -> None:
        picks = self.desk["high_picks"]
        self.assertTrue(picks, "desk publishes no High pick")
        for pick in picks:
            with self.subTest(pick=pick["fixture_id"], selection=pick["selection"]):
                self.assertGreater(pick["probability"], MIN_HIGH_PROBABILITY)
                self.assertLessEqual(pick["probability"], 1 / 1.4 + 1e-9)

    def test_every_high_price_sits_inside_the_band(self) -> None:
        for pick in self.desk["high_picks"]:
            with self.subTest(pick=pick["fixture_id"]):
                self.assertGreaterEqual(pick["american"], BAND_LOW_AMERICAN)
                self.assertLessEqual(pick["american"], BAND_HIGH_AMERICAN)

    def test_predictions_are_long_enough_and_unique(self) -> None:
        bodies = []
        for prediction in self.desk["predictions"]:
            words = len(prediction["body"].split())
            with self.subTest(prediction=prediction["fixture_id"]):
                self.assertGreaterEqual(words, 30)
            bodies.append(prediction["body"])
        self.assertEqual(len(bodies), len(set(bodies)), "duplicate prediction text")


if __name__ == "__main__":
    unittest.main()
