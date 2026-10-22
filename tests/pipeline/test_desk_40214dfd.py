import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESK = ROOT / "data" / "40214dfd" / "desk.json"


class Desk40214dfdTest(unittest.TestCase):
    """The desk gate must pass, and its central claim must be arithmetically true."""

    def test_desk_validator_passes(self):
        if not DESK.exists():
            self.skipTest("desk data not present")
        result = subprocess.run([sys.executable, str(ROOT / "scripts" / "s40214dfd_validate.py")],
                                capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("VALIDATION PASSED", result.stdout)

    def test_high_selections_respect_the_brief_window(self):
        desk = json.loads(DESK.read_text())
        highs = [o for fx in desk["fixtures"] for mk in fx["markets"] for o in mk["outcomes"]
                 if o.get("confidence") == "high"]
        self.assertTrue(highs, "expected at least one High selection")
        for o in highs:
            self.assertGreater(o["probability"], 0.70)
            self.assertLessEqual(o["probability"], 1 / 1.40 + 1e-9)
            self.assertGreaterEqual(o["fair_decimal"], 1.40)
            self.assertTrue(o.get("prediction_id"))

    def test_no_bookmaker_quote_is_claimed(self):
        desk = json.loads(DESK.read_text())
        for fx in desk["fixtures"]:
            for mk in fx["markets"]:
                self.assertIn("no bookmaker quote captured", mk["status"])

    def test_every_market_cites_an_official_host(self):
        hosts = ("nhl.com", "nhle.com", "mlb.com", "euroleaguebasketball.net", "wst.tv", "gaa.ie")
        desk = json.loads(DESK.read_text())
        for fx in desk["fixtures"]:
            self.assertTrue(any(any(h in u for h in hosts) for u in fx["source_urls"]), fx["id"])


if __name__ == "__main__":
    unittest.main()
