#!/usr/bin/env python3
"""CI bridge for the isolated TB2719 evidence desk."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "b2719ad3"
SITE = ROOT / "b2719ad3"


class TestDeskB2719AD3(unittest.TestCase):
    def test_full_desk_validator(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "sb2719ad3_check.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads((DATA / "checks.json").read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["broken_local_links"], [])

    def test_exact_scope_and_site_pages(self):
        obs = json.loads((DATA / "observations.json").read_text(encoding="utf-8"))
        self.assertEqual(len(obs["scope"]), 15)
        self.assertEqual(len({s["slug"] for s in obs["scope"]}), 15)
        for sport in obs["scope"]:
            self.assertTrue((SITE / "sports" / f'{sport["slug"]}.html').is_file())

    def test_predictions_obey_high_contract(self):
        predictions = json.loads((DATA / "predictions.json").read_text(encoding="utf-8"))
        normalized = []
        for row in predictions:
            self.assertGreater(row["probability"], 0.70)
            self.assertGreaterEqual(row["fair_american"], -250)
            self.assertLessEqual(row["fair_american"], 10000)
            self.assertGreaterEqual(row["words"], 30)
            self.assertNotRegex(row["prediction"], r"(?i)\b(model|verified)\b")
            self.assertTrue(row["official_source"].startswith("https://"))
            normalized.append(re.sub(r"\s+", " ", row["prediction"].strip().lower()))
        self.assertEqual(len(normalized), len(set(normalized)))

    def test_started_and_unpriced_rows_never_gain_active_picks(self):
        prices = json.loads((DATA / "prices.json").read_text(encoding="utf-8"))
        self.assertTrue(all(row["analysis"] is None for row in prices["started_rows"]))
        for row in prices["active_rows"]:
            if row["analysis"] is None:
                self.assertTrue(row["flags"], row["id"])

    def test_public_report_matches_data(self):
        report = json.loads((DATA / "build-report.json").read_text(encoding="utf-8"))
        prices = json.loads((DATA / "prices.json").read_text(encoding="utf-8"))
        predictions = json.loads((DATA / "predictions.json").read_text(encoding="utf-8"))
        self.assertEqual(report["scope_count"], 15)
        self.assertEqual(report["active_event_rows"], len(prices["active_rows"]))
        self.assertEqual(report["started_exclusions"], len(prices["started_rows"]))
        self.assertEqual(report["high_predictions"], len(predictions))

    def test_canonical_front_door_preserves_peer_links(self):
        builder = (ROOT / "pipeline" / "build.py").read_text(encoding="utf-8")
        root = (ROOT / "index.html").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("link='b2719ad3/index.html'", builder)
        for peer in ("37003e61/index.html", "8cfb80b2/index.html", "02d3d515/index.html", "3d121822/index.html"):
            self.assertIn(peer, builder)
            self.assertIn(peer, root)
        self.assertIn('href="b2719ad3/index.html"', root)
        self.assertIn("/OLBG1/b2719ad3/index.html", readme)


if __name__ == "__main__":
    unittest.main()
