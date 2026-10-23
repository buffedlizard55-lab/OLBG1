"""Comprehensive contract & statistical invariant tests for Session 8a900c04."""
from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path

from pipeline.audit import build_audit
from pipeline.common import official_url, parse_time

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "8a900c04"
SITE_DIR = ROOT / "8a900c04"

EXPECTED_15_SPORTS = {
    "Golf",
    "Volleyball",
    "Rugby Union",
    "Cricket",
    "Snooker",
    "Darts",
    "Baseball",
    "Gaelic Sports",
    "Greyhounds",
    "Tennis",
    "Motor Racing",
    "Handball",
    "Ice Hockey",
    "Basketball",
    "Rugby League",
}


class TestDesk8a900c04(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.desk = json.loads((DATA_DIR / "desk.json").read_text(encoding="utf-8"))
        cls.predictions = json.loads((DATA_DIR / "predictions.json").read_text(encoding="utf-8"))
        cls.repo_audit = json.loads((DATA_DIR / "repo_audit.json").read_text(encoding="utf-8"))

    def test_exact_15_sport_scope_and_depth(self) -> None:
        events = self.desk["events"]
        sports_present = {e["sport"] for e in events}
        self.assertEqual(sports_present, EXPECTED_15_SPORTS)
        self.assertEqual(len(events), 75)
        for sp in EXPECTED_15_SPORTS:
            sp_events = [e for e in events if e["sport"] == sp]
            self.assertEqual(len(sp_events), 5, f"Expected 5 events for {sp}")

    def test_high_confidence_strictly_inside_minus250_to_plus10000_window(self) -> None:
        for ev in self.desk["events"]:
            for m in ev["markets"]:
                if m["confidence"] == "high":
                    self.assertGreater(m["fair_prob"], 0.70, f"{ev['id']} High pick below 70%: {m}")
                    self.assertGreaterEqual(m["fair_decimal"], 1.40, f"{ev['id']} High pick <1.40 dec: {m}")
                    self.assertLessEqual(m["fair_decimal"], 101.0, f"{ev['id']} High pick >101.0 dec: {m}")
                    self.assertGreaterEqual(m["fair_american"], -250, f"{ev['id']} High pick <-250 US: {m}")
                    self.assertLessEqual(m["fair_american"], 10000, f"{ev['id']} High pick >+10000 US: {m}")
                    self.assertFalse(m["chalk_suppressed"])
                if m["fair_american"] < -250:
                    self.assertNotEqual(
                        m["confidence"],
                        "high",
                        f"Chalk shorter than -250 must NEVER be rated High: {ev['id']} {m}",
                    )
                    self.assertTrue(m["chalk_suppressed"])

    def test_human_predictions_zero_forbidden_words_and_rich_length(self) -> None:
        self.assertEqual(len(self.predictions), 75)
        for p in self.predictions:
            txt = p["prediction"]
            low = txt.lower()
            self.assertNotIn("model", low, f"Forbidden substring 'model' in {p['id']}")
            self.assertNotIn("verif", low, f"Forbidden substring 'verif' in {p['id']}")
            self.assertGreaterEqual(len(txt.split()), 48, f"Prediction too short in {p['id']}")
            self.assertTrue(txt.startswith("Selection:"), f"Obvious selection missing in {p['id']}")

    def test_official_publisher_provenance_zero_audit_warnings(self) -> None:
        audit = build_audit(parse_time("2026-10-23T16:29:00Z"), write=False)
        self.assertEqual(audit["counts"]["parse_errors"], 0)
        our_rows = [r for r in audit["rows"] if r["file"].startswith("data/8a900c04/")]
        for r in our_rows:
            self.assertTrue(r["official_urls"], f"Row missing allowlisted official_urls: {r}")
            self.assertNotEqual(r["stored_start_elapsed"], True, f"Elapsed start on {r}")
        for ev in self.desk["events"]:
            has_allowed = any(
                official_url(u)
                for u in (ev["official_url"], ev["secondary_official_url"], ev["publisher_crossref_url"])
            )
            self.assertTrue(has_allowed, f"{ev['id']} lacks allowlisted publisher URL")

    def test_flagged_rows_strictly_null_unconfirmed_fields(self) -> None:
        flagged = self.desk["flagged"]
        self.assertEqual(len(flagged), 7)
        for row in flagged:
            self.assertFalse(row["verified"])
            for field in ("start_utc", "venue", "selection", "fair_prob", "fair_decimal", "fair_american", "confidence"):
                self.assertIsNone(row[field], f"Unconfirmed field {field} must be null on {row['id']}")

    def test_multi_page_html_and_csv_exports_exist_and_clean(self) -> None:
        expected_pages = [
            SITE_DIR / "index.html",
            SITE_DIR / "todays-picks.html",
            SITE_DIR / "upcoming-picks.html",
            SITE_DIR / "markets.html",
            SITE_DIR / "methodology.html",
            SITE_DIR / "sources.html",
            SITE_DIR / "repo-audit.html",
            SITE_DIR / "flagged.html",
            ROOT / "reports" / "SESSION_8A900C04.html",
            ROOT / "reports" / "SESSION_8A900C04.md",
        ]
        for p in expected_pages:
            self.assertTrue(p.is_file(), f"Missing generated page: {p}")
        sport_pages = list((SITE_DIR / "sports").glob("*.html"))
        self.assertEqual(len(sport_pages), 15)

        with (DATA_DIR / "fixtures.csv").open(encoding="utf-8") as fh:
            f_rows = list(csv.DictReader(fh))
        self.assertEqual(len(f_rows), 82)  # 75 verified + 7 flagged

        with (DATA_DIR / "markets.csv").open(encoding="utf-8") as fh:
            m_rows = list(csv.DictReader(fh))
        self.assertGreaterEqual(len(m_rows), 450)


if __name__ == "__main__":
    unittest.main()
