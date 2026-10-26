"""Independent release-audit artifact checks for session e25879f7."""
from __future__ import annotations

import json
import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import se25879f7_audit as A  # noqa: E402


class Rows(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inside_table = False
        self.inside_row = False
        self.row_links: list[str] = []
        self.rows: list[list[str]] = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "table":
            self.inside_table = True
        elif tag == "tr" and self.inside_table:
            self.inside_row = True
            self.row_links = []
        elif tag == "a" and self.inside_row and attrs.get("href"):
            self.row_links.append(attrs["href"])

    def handle_endtag(self, tag):
        if tag == "tr" and self.inside_row:
            self.rows.append(self.row_links)
            self.inside_row = False
        elif tag == "table":
            self.inside_table = False


class PublishedDeskAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        A.main()
        cls.audit = json.loads((ROOT / "data/e25879f7/audit.json").read_text(encoding="utf-8"))
        cls.page = (ROOT / "e25879f7/index.html").read_text(encoding="utf-8")

    def test_fifteen_sports_are_explicit_and_each_row_links_sources(self):
        rows = self.audit["sport_rows"]
        self.assertEqual(len(rows), 15)
        self.assertEqual({r["slug"] for r in rows}, {s[0] for s in A.D.SPORTS})
        for row in rows:
            self.assertTrue(row["official_source"].startswith("https://"), row["sport"])
            self.assertTrue(row["olbg_discovery"].startswith("https://www.olbg.com/"), row["sport"])

    def test_high_selections_all_have_written_predictions_and_official_links(self):
        self.assertEqual(len(self.audit["high_picks"]), self.audit["counts"]["high"])
        for pick in self.audit["high_picks"]:
            self.assertTrue(pick["has_prediction"], pick["id"])
            self.assertGreaterEqual(pick["prediction_words"], 30, pick["id"])
            self.assertTrue(pick["official_source"].startswith("https://"), pick["id"])
            self.assertIn(pick["prediction_url"], self.page)

    def test_reported_counts_are_from_retained_snapshot(self):
        c = self.audit["counts"]
        self.assertEqual((c["sports"], c["fixtures"], c["priced"], c["picks"], c["high"], c["predictions"]),
                         (15, 48, 39, 34, 11, 20))
        self.assertEqual(sum(r["official_fixture_rows"] > 0 for r in self.audit["sport_rows"]), 7)
        self.assertEqual(sum(r["picks"] > 0 for r in self.audit["sport_rows"]), 6)
        self.assertEqual(sum(r["picks"] for r in self.audit["sport_rows"]), c["picks"])
        self.assertEqual(sum(r["high_picks"] for r in self.audit["sport_rows"]), c["high"])
        self.assertEqual(sum(r["written_predictions"] for r in self.audit["sport_rows"]), c["predictions"])

    def test_every_html_table_row_has_an_https_source_link(self):
        parser = Rows()
        parser.feed(self.page)
        data_rows = [links for links in parser.rows if links]
        self.assertEqual(len(data_rows), 26)  # 15 sport rows + 11 High-pick rows
        for i, links in enumerate(data_rows, 1):
            self.assertTrue(any(urlsplit(link).scheme == "https" for link in links), f"row {i}")

    def test_limits_are_prominent_and_no_new_sport_claims_are_added(self):
        for phrase in ("not a live", "no injury", "not proof", "originated estimates", "24 October"):
            self.assertIn(phrase.lower(), self.page.lower())
        self.assertEqual(self.audit["prediction_vocab_hits"], [])
        self.assertEqual(len(self.audit["findings"]), 4)

    def test_publication_request_stays_within_session_scope(self):
        # This audit site is deliberately separate from the shared canonical build.
        self.assertTrue((ROOT / "aa2881ac/index.html").is_file())
        self.assertTrue((ROOT / "index.html").is_file())
        self.assertIn("../aa2881ac/index.html", self.page)


if __name__ == "__main__":
    unittest.main()
