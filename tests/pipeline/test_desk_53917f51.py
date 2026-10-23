#!/usr/bin/env python3
"""Read-only audit gate for T496E; protects the 53917f51 review artifacts."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from s53917f51_audit import build_audit  # noqa: E402

DATA = ROOT / "data" / "53917f51"
SITE = ROOT / "53917f51"


class TestIndependentAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = build_audit()
        cls.findings = {item["id"]: item for item in cls.audit["findings"]}
        cls.evidence = json.loads((DATA / "evidence.json").read_text(encoding="utf-8"))

    def test_full_snapshot_is_parsed_and_high_thresholds_are_recomputed(self):
        counts = self.audit["counts"]
        self.assertEqual(counts["fixtures"], 81)
        self.assertEqual(counts["market_outcomes"], 460)
        self.assertEqual(counts["predictions"], 51)
        self.assertEqual(counts["high_labeled"], 51)
        self.assertEqual(counts["high_strictly_over_70_percent"], 3)
        self.assertEqual(counts["high_exactly_70_percent"], 2)
        self.assertEqual(counts["high_below_70_percent"], 46)
        self.assertEqual(counts["high_labeled_in_fair_american_band"], 51)

    def test_prediction_text_constraints_are_measured(self):
        counts = self.audit["counts"]
        self.assertGreaterEqual(counts["predictions_min_words"], 30)
        self.assertEqual(counts["predictions_unique_texts"], 51)
        self.assertEqual(counts["prediction_forbidden_word_occurrences"], 0)
        self.assertEqual(counts["predictions_with_injury_or_availability_term"], 7)

    def test_critical_fixture_findings_are_source_backed(self):
        tennis = self.findings["F-53917-01"]
        self.assertEqual(tennis["severity"], "Critical")
        self.assertEqual(len(tennis["official_sources"]), 3)
        self.assertTrue(any("wtatennis.com" in row["url"] for row in tennis["official_sources"]))

        euroleague = self.findings["F-53917-14"]
        self.assertEqual(euroleague["severity"], "Critical")
        self.assertEqual(euroleague["data"]["affected_fixture_ids"], ["BK07", "BK08", "BK09", "BK10"])
        self.assertEqual(euroleague["data"]["affected_high_picks"], 4)
        self.assertTrue(any("de89146d-ddb7-4931-9deb-f72672b4d63b.pdf" in row["url"]
                            for row in euroleague["official_sources"]))

    def test_timestamp_source_authority_and_stale_input_checks_remain_flagged(self):
        counts = self.audit["counts"]
        self.assertEqual(counts["upcoming_with_start_at_or_before_capture"], 1)
        self.assertEqual(counts["flagged_unverified_start_but_start_value_populated"], 1)
        self.assertEqual(counts["fixture_rows_using_known_media_sources"], 2)
        self.assertEqual(counts["fixture_source_refs_from_known_media"], 3)
        self.assertEqual(counts["high_with_stale_or_not_refetched_inputs"], 2)
        self.assertEqual(counts["source_registry_entries_with_fetch_metadata"], 0)

    def test_fresh_evidence_is_explicit_and_official_links_are_manual_reviewable(self):
        self.assertEqual(self.evidence["audit_id"], "53917f51")
        self.assertIn("2026-10-23", self.evidence["read_window_utc"])
        self.assertGreaterEqual(len(self.evidence["sources"]), 20)
        for record in self.evidence["sources"]:
            self.assertTrue(record["publisher"])
            self.assertTrue(record["title"])
            self.assertTrue(record["excerpt"])
            self.assertTrue(record["supports"])
            self.assertIn("2026-10-23", record["read_window_utc"])
            parsed = urlsplit(record["url"])
            self.assertIn(parsed.scheme, {"http", "https"})
            self.assertTrue(parsed.netloc)

    def test_generated_review_pages_exist_and_keep_subject_desk_read_only(self):
        for name in ("index.html", "flagged.html", "sources.html", "assets/style.css"):
            self.assertTrue((SITE / name).is_file(), name)
        report_html = ROOT / "reports" / "SESSION_53917F51.html"
        self.assertTrue(report_html.is_file())
        self.assertNotIn("<code>data/496eaf02/<strong></code>", report_html.read_text(encoding="utf-8"))
        html = (SITE / "flagged.html").read_text(encoding="utf-8")
        self.assertIn("F-53917-14", html)
        self.assertIn("BK07", html)
        self.assertIn("WTA", html)

    def test_generated_page_local_links_resolve(self):
        from html.parser import HTMLParser
        from urllib.parse import unquote, urlsplit

        class LinksAndIds(HTMLParser):
            def __init__(self):
                super().__init__()
                self.links = []
                self.ids = set()

            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                if tag == "a" and attrs.get("href"):
                    self.links.append(attrs["href"])
                if attrs.get("id"):
                    self.ids.add(attrs["id"])

        pages = list(SITE.rglob("*.html")) + [ROOT / "reports" / "SESSION_53917F51.html"]
        for page in pages:
            parser = LinksAndIds()
            parser.feed(page.read_text(encoding="utf-8"))
            for href in parser.links:
                parsed = urlsplit(href)
                if parsed.scheme or parsed.netloc:
                    continue
                target = (page.parent / unquote(parsed.path)).resolve() if parsed.path else page
                self.assertTrue(target.is_file(), f"{page.relative_to(ROOT)} -> {href}")
                if parsed.fragment and target.suffix == ".html":
                    target_parser = LinksAndIds()
                    target_parser.feed(target.read_text(encoding="utf-8"))
                    self.assertIn(parsed.fragment, target_parser.ids,
                                  f"{page.relative_to(ROOT)} -> {href}")


if __name__ == "__main__":
    unittest.main()
