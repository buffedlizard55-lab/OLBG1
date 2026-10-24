"""Contract tests for the 3d121822 desk (24 October 2026).

Run with:  python -m unittest discover -s tests/pipeline -v
"""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import s3d121822_data as D  # noqa: E402
import s3d121822_model as M  # noqa: E402

OUT = ROOT / "3d121822"
DATA = ROOT / "data" / "3d121822"


class DeskContract(unittest.TestCase):
    def test_every_fixture_has_an_olbg_discovery_link(self):
        rows = D.fixture_rows()
        self.assertGreater(len(rows), 40)
        for fx in rows:
            self.assertTrue(fx["olbg"].startswith("https://www.olbg.com/"), fx["id"])

    def test_every_sport_declares_its_gap(self):
        self.assertEqual(len(D.SPORTS), 15)
        for sp in D.SPORTS:
            self.assertTrue(sp["gap"].strip(), sp["key"])
            self.assertTrue(sp["route"].startswith("https://www.olbg.com/"), sp["key"])

    def test_prices_only_exist_with_both_records(self):
        fixtures = {f["id"]: f for f in D.fixture_rows()}
        for fid, p in M.build_prices().items():
            fx = fixtures[fid]
            table = D.NBA if fx["sport"] == "basketball" else D.NHL
            self.assertIn(fx["a"], table, fid)
            self.assertIn(fx["b"], table, fid)
            self.assertTrue(0.0 < p["p_home"] < 1.0, fid)

    def test_no_fixture_without_records_is_priced(self):
        priced_sports = {f["sport"] for f in D.fixture_rows() if f["id"] in M.build_prices()}
        self.assertEqual(priced_sports, {"basketball", "ice_hockey"})

    def test_high_labels_sit_inside_the_stated_window(self):
        for fid, p in M.build_prices().items():
            if p["conf"] == "High":
                self.assertGreaterEqual(p["p_pick"], 0.70)
                self.assertLessEqual(p["p_pick"], 1 / 3.5)

    def test_predictions_are_long_unique_and_selection_led(self):
        shingles = {}
        for fid, pred in D.PREDICTIONS.items():
            words = pred["text"].split()
            self.assertGreaterEqual(len(words), 30, fid)
            self.assertTrue(pred["selection"], fid)
            self.assertTrue(pred["evidence"], fid)
            for bad in ("model", "models", "verified", "verification"):
                self.assertNotIn(bad, pred["text"].lower(), fid)
            for i in range(len(words) - 7):
                key = tuple(w.lower().strip(",.") for w in words[i:i + 8])
                self.assertNotIn(key, shingles, f"{fid} repeats {shingles.get(key)}")
                shingles[key] = fid

    def test_every_published_pick_has_a_written_prediction(self):
        written = {fid for fid, p in M.build_prices().items() if p["written"]}
        self.assertEqual(written, set(D.PREDICTIONS))

    def test_flags_are_published_with_sources(self):
        self.assertGreaterEqual(len(D.FLAGS), 8)
        for ref, severity, _scope, title, detail, src in D.FLAGS:
            self.assertIn(severity, ("high", "medium", "low"))
            self.assertTrue(title and detail, ref)
            self.assertIn(src, D.SOURCES, ref)

    def test_built_pages_and_exports_exist(self):
        self.assertTrue((OUT / "index.html").is_file())
        self.assertTrue((OUT / "sports" / "index.html").is_file())
        self.assertEqual(len(list((OUT / "sports").glob("*.html"))), 16)
        fixtures = json.loads((DATA / "fixtures.json").read_text())
        self.assertEqual(fixtures["count"], len(D.fixture_rows()))
        self.assertEqual(fixtures["picks"], len(D.PREDICTIONS))

    def test_validator_passes(self):
        result = subprocess.run([sys.executable, str(SCRIPTS / "s3d121822_validate.py")],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_no_banned_vocabulary_in_rendered_prose(self):
        for page in (OUT / "predictions.html", OUT / "picks.html", OUT / "index.html"):
            text = page.read_text(encoding="utf-8").lower()
            self.assertNotIn(">model<", text, page.name)
            self.assertNotIn("verified by", text, page.name)


if __name__ == "__main__":
    unittest.main()
