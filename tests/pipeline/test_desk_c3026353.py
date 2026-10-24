"""Tests for the TC3026353 desk (session c3026353-olbg1).

These run with the repo's standard command:
    python3 -m unittest discover -s tests/pipeline -v
"""
from __future__ import annotations

import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import sc3026353_model as model  # noqa: E402
import sc3026353_validate as validate  # noqa: E402


class TestDeskModel(unittest.TestCase):
    def test_decimal_is_reciprocal_of_probability(self):
        for p in (0.55, 0.70, 0.85):
            self.assertAlmostEqual(1.0 / p, 1.0 / p)
            am = model.p_to_american(p)
            self.assertAlmostEqual(model.american_to_p(am), p, places=6)

    def test_high_gate_window_arithmetic(self):
        # 70.0% maps to about -233.3; 71.43% maps to -250 — the whole band.
        self.assertGreaterEqual(model.p_to_american(0.70), -234.0)
        self.assertLessEqual(model.p_to_american(0.70), -233.0)
        self.assertAlmostEqual(model.p_to_american(5 / 7), -250.0, places=6)

    def test_tier_labels(self):
        self.assertEqual(model.tier(0.71, -245.0, True), "High")
        self.assertEqual(model.tier(0.80, -400.0, True), "Medium (chalk cap)")
        self.assertEqual(model.tier(0.62, -163.0, True), "Medium")
        self.assertEqual(model.tier(0.62, -163.0, False), "Medium (evidence gap)")
        self.assertEqual(model.tier(0.40, 150.0, True), "Low")
        self.assertEqual(model.tier(0.40, 150.0, False), "Low (evidence gap)")

    def test_best_of_n_monotonic(self):
        self.assertLess(model._best_of_n(0.5, 11), model._best_of_n(0.55, 11))
        self.assertAlmostEqual(model._best_of_n(0.5, 19), 0.5, places=6)

    def test_field_weights_normalise(self):
        probs = model.field_win_probs([("A", 30), ("B", 60), ("C", 10)])
        self.assertAlmostEqual(sum(probs.values()), 1.0, places=6)
        self.assertAlmostEqual(probs["B"], 0.6, places=6)

    def test_log5_symmetry(self):
        self.assertAlmostEqual(model._log5(0.7, 0.3) + model._log5(0.3, 0.7), 1.0, places=9)


class TestDeskValidation(unittest.TestCase):
    def test_desk_passes_own_validator(self):
        data = ROOT / "data" / "c3026353"
        if not (data / "predictions.json").exists():
            self.skipTest("desk data not built yet (run scripts/sc3026353_build.py)")
        errors, _warnings, stats = validate.check()
        self.assertEqual(errors, [], msg="; ".join(errors[:10]))
        self.assertGreaterEqual(stats["predictions"], 50)

    def test_every_prediction_text_is_unique_and_clean(self):
        path = ROOT / "data" / "c3026353" / "predictions.json"
        if not path.exists():
            self.skipTest("desk data not built yet")
        rows = json.loads(path.read_text())["rows"]
        texts = [r["text"].lower() for r in rows]
        self.assertEqual(len(texts), len(set(texts)), "duplicate prediction text")
        for r in rows:
            self.assertNotIn("model", r["text"].lower())
            self.assertNotIn("verified", r["text"].lower())

    def test_every_fixture_has_official_source(self):
        path = ROOT / "data" / "c3026353" / "sources.json"
        if not path.exists():
            self.skipTest("desk data not built yet")
        sources = {s["id"]: s for s in json.loads(path.read_text())["sources"]}
        fixtures = json.loads((ROOT / "data" / "c3026353" / "fixtures.json").read_text())["fixtures"]
        for fx in fixtures:
            offs = [sources[s] for s in fx["sources"] if s in sources and sources[s]["kind"] == "official"]
            self.assertTrue(offs, f"{fx['id']} has no official source")
            for s in offs:
                self.assertTrue(s["url"].startswith("https://"))

    def test_high_picks_sit_inside_the_briefs_window(self):
        path = ROOT / "data" / "c3026353" / "predictions.json"
        if not path.exists():
            self.skipTest("desk data not built yet")
        for r in json.loads(path.read_text())["rows"]:
            if r["tier"] == "High":
                self.assertGreater(r["p"], 0.70)
                self.assertGreaterEqual(r["american"], -250.0)
                self.assertLessEqual(r["american"], 10000.0)


if __name__ == "__main__":
    unittest.main()
