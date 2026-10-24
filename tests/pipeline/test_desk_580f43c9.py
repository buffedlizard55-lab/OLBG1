"""Tests for the 580f43c9 desk (session 580f43c9-olbg1)."""

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from s580f43c9_data import MATCHES, PICKS, SOURCES, GAPS, FLAGS  # noqa: E402
from s580f43c9_model import (american_from_prob, in_band, log5, shrink, tier,  # noqa: E402
                             hockey_derivatives, poisson_margin_prob)


class ModelTest(unittest.TestCase):
    def test_shrink_pulls_toward_half(self):
        self.assertAlmostEqual(shrink(0, 0), 0.5)
        self.assertLess(shrink(0, 2), 0.5)
        self.assertGreater(shrink(2, 0), 0.5)

    def test_log5_symmetry(self):
        self.assertAlmostEqual(log5(0.5, 0.5), 0.5)
        self.assertAlmostEqual(log5(0.7, 0.3) + log5(0.3, 0.7), 1.0)

    def test_american_round_trip(self):
        self.assertEqual(american_from_prob(0.5), -100)
        self.assertEqual(american_from_prob(0.7143), -250)
        self.assertGreater(american_from_prob(0.25), 0)

    def test_band_edges(self):
        self.assertTrue(in_band(0.71))
        self.assertFalse(in_band(0.735))   # shorter than -250
        self.assertFalse(in_band(0.002))   # longer than +10000

    def test_high_tier_needs_both_rules(self):
        self.assertEqual(tier(0.712, "basketball"), "high")
        self.assertEqual(tier(0.80, "basketball", out_of_band=True), "medium")
        self.assertEqual(tier(0.712, "tennis", inputs_complete=False), "low")
        self.assertEqual(tier(0.55, "basketball"), "low")
        self.assertEqual(tier(0.65, "basketball"), "medium")

    def test_hockey_derivatives_are_probabilities(self):
        fx = [m for m in MATCHES if m["id"] == "nhl-sjs-bos"][0]
        d = hockey_derivatives(fx)
        for key in ("over", "under", "home_puck_line", "away_puck_line"):
            self.assertGreater(d[key], 0.0)
            self.assertLess(d[key], 1.0)
        self.assertAlmostEqual(d["over"] + d["under"], 1.0, places=6)
        # a -1.5 line on both sides cannot cover every game: one-goal results lose both
        self.assertLess(d["home_puck_line"] + d["away_puck_line"], 1.0)

    def test_poisson_margin(self):
        self.assertGreater(poisson_margin_prob(3.5, 2.5, 2), 0.4)
        self.assertLess(poisson_margin_prob(2.0, 4.0, 2), 0.2)


class DataTest(unittest.TestCase):
    def test_every_match_has_official_source(self):
        official = {s["id"] for s in SOURCES if s["official"]}
        for m in MATCHES:
            self.assertIn(m["source"], official, m["id"])

    def test_every_pick_names_a_participant(self):
        by_id = {m["id"]: m for m in MATCHES}
        for p in PICKS:
            m = by_id[p["match"]]
            self.assertIn(p["side"], ("a", "b"))
            self.assertGreaterEqual(len(p["prose"].split()), 30, p["match"])

    def test_no_banned_vocabulary(self):
        for p in PICKS:
            low = p["prose"].lower()
            for bad in ("model", "verified", "verification"):
                self.assertNotIn(bad, low, p["match"])

    def test_gaps_and_flags_are_linked(self):
        for g in GAPS:
            self.assertTrue(g["source"].startswith("https://"))
        for f in FLAGS:
            self.assertTrue(f["link"].startswith("https://"))

    def test_published_json_matches_module(self):
        published = json.loads((ROOT / "data" / "580f43c9" / "picks.json").read_text())
        self.assertEqual(len(published), len(PICKS))
        self.assertEqual(sorted(c["match_id"] for c in published), sorted(p["match"] for p in PICKS))


class SiteTest(unittest.TestCase):
    def test_validator_passes(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts" / "s580f43c9_validate.py")],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_landing_page_names_every_pick(self):
        index = (ROOT / "580f43c9" / "index.html").read_text()
        cards = json.loads((ROOT / "data" / "580f43c9" / "picks.json").read_text())
        for c in cards:
            self.assertIn(c["selection"], index)


if __name__ == "__main__":
    unittest.main()
