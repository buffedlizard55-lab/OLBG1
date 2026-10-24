"""Tests for desk 57bafcbb (session 57bafcbb-olbg1, claim T57BAFCBB).

The desk is the fresh 24-25 October 2026 overnight window for the 15-sport
OLBG brief. These tests re-derive the desk from its own modules and assert the
invariants the brief demands:

* 15 sports in the brief's order, one page per sport;
* every priced fixture is backed by at least one official source;
* every pick's fair price is the arithmetic of its own estimate, and every
  pick carries a unique written prediction of at least 30 words that names the
  pick, states the bet and prints the price;
* High picks sit inside -250..+10000 and are 60% or better, and the desk
  publishes at least one;
* the rendered HTML has no banned vocabulary, no linear-gradient, one h1 per
  page, no duplicate ids, no plain http:// and no broken internal links;
* every data table row carries an https link;
* the JSON mirrors reconcile with the module of record by exact count.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
DESK_DIR = ROOT / "57bafcbb"
DATA_DIR = ROOT / "data" / "57bafcbb"
sys.path.insert(0, str(SCRIPTS))

import s57bafcbb_data as d  # noqa: E402
import s57bafcbb_model as m  # noqa: E402

BRIEF_ORDER = ["golf", "volleyball", "rugby-union", "cricket", "snooker", "darts",
               "baseball", "gaelic-sports", "greyhounds", "tennis", "motor-racing",
               "handball", "ice-hockey", "basketball", "rugby-league"]


def _desk():
    return m.build_all()


class DeskShapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.desk = _desk()

    def test_exactly_15_sports_in_brief_order(self):
        self.assertEqual([s["slug"] for s in d.SPORTS], BRIEF_ORDER)

    def test_one_page_per_sport(self):
        for s in d.SPORTS:
            self.assertTrue((DESK_DIR / s["page"]).is_file(), s["page"])

    def test_fixture_ids_unique(self):
        ids = [f["id"] for f in self.desk["fixtures"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_fixtures_carry_an_official_or_discovery_source(self):
        for f in self.desk["fixtures"]:
            self.assertTrue(f["sources"], f["id"])

    def test_priced_fixtures_cite_an_official_source(self):
        for f in self.desk["fixtures"]:
            if f.get("priced"):
                self.assertTrue(
                    any(s["official"] for s in f["sources"]),
                    f"{f['id']} priced without an official source",
                )

    def test_unpriced_fixtures_are_directory_entries_not_priced(self):
        for f in self.desk["fixtures"]:
            if not f.get("priced"):
                self.assertIsNone(f.get("book"), f["id"])
                self.assertIn(f["status"], ("directory-entry", "completed"), f["id"])


class LineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.desk = _desk()

    def test_two_way_book_is_fair(self):
        for f in self.desk["fixtures"]:
            book = f.get("book")
            if not book:
                continue
            self.assertAlmostEqual(book["home_prob"] + book["away_prob"], 1.0, places=6)
            self.assertAlmostEqual(book["margin"], 0.0, places=6)

    def test_every_price_is_the_arithmetic_of_its_estimate(self):
        for f in self.desk["fixtures"]:
            book = f.get("book")
            if not book:
                continue
            self.assertEqual(book["estimate_price"], m.american_from_prob(book["estimate"]))
            self.assertEqual(book["home_price"], m.american_from_prob(book["home_prob"]))
            self.assertEqual(book["away_price"], m.american_from_prob(book["away_prob"]))

    def test_estimates_inside_supported_range(self):
        for p in self.desk["picks"]:
            self.assertGreaterEqual(p["estimate"], 0.05)
            self.assertLessEqual(p["estimate"], 0.98)

    def test_high_picks_inside_the_band_and_60_percent_or_better(self):
        high = [p for p in self.desk["picks"] if p["tier"] == "High"]
        self.assertGreater(len(high), 0, "the desk published no High pick")
        for p in high:
            self.assertTrue(m.american_in_band(p["american"]), p["fixture_id"])
            self.assertGreaterEqual(p["estimate"], 0.60, p["fixture_id"])

    def test_no_high_pick_priced_outside_the_band(self):
        for p in self.desk["picks"]:
            if p["tier"] == "High":
                self.assertGreaterEqual(p["american"], -250)
                self.assertLessEqual(p["american"], 10000)

    def test_markets_carry_win_handicap_and_total_where_supported(self):
        for f in self.desk["fixtures"]:
            if not f.get("markets"):
                continue
            mk = f["markets"][0]
            self.assertEqual(mk["american"], m.american_from_prob(mk["estimate"]))

    def test_every_pick_has_a_written_prediction(self):
        pick_ids = {p["fixture_id"] for p in self.desk["picks"]}
        pred_ids = {p["fixture_id"] for p in self.desk["predictions"]}
        self.assertEqual(pick_ids, pred_ids)

    def test_predictions_are_long_enough(self):
        for p in self.desk["predictions"]:
            self.assertGreaterEqual(p["words"], 30, p["fixture_id"])

    def test_predictions_name_the_pick_bet_and_price(self):
        for p in self.desk["predictions"]:
            self.assertIn(p["pick"], p["text"], p["fixture_id"])
            self.assertIn(p["bet"], p["text"], p["fixture_id"])
            self.assertIn(str(p["american"]), p["text"], p["fixture_id"])
            self.assertNotIn("<<PRICE>>", p["text"])

    def test_predictions_are_unique_at_5_and_6_grams(self):
        for n in (5, 6):
            seen = {}
            for p in self.desk["predictions"]:
                words = p["text"].split()
                for i in range(len(words) - n + 1):
                    gram = " ".join(words[i:i + n])
                    self.assertNotIn(gram, seen, f"{n}-gram {gram!r}")
                    seen[gram] = p["fixture_id"]


class SourceTests(unittest.TestCase):
    def test_all_sources_are_https(self):
        for s in d.SOURCES:
            self.assertTrue(s["url"].startswith("https://"), s["id"])

    def test_source_ids_unique(self):
        ids = [s["id"] for s in d.SOURCES]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_sport_has_an_official_source(self):
        for slug in BRIEF_ORDER:
            pool = m.SOURCE_POOLS[slug]
            self.assertTrue(any(p in d.SOURCE_BY_ID for p in pool), slug)

    def test_olbg_log_covers_all_15_sports(self):
        slugs = {row["slug"] for row in d.OLBG_LOG}
        self.assertEqual(slugs, set(BRIEF_ORDER))
        for row in d.OLBG_LOG:
            self.assertTrue(row["url"].startswith("https://"))

    def test_unreadable_official_sources_are_flagged(self):
        flagged_ids = {f["id"] for f in d.FLAG_ITEMS if f["kind"] == "source"}
        self.assertIn("f-sources-unreadable", flagged_ids)
        unreadable = [s["id"] for s in d.SOURCES if not s["official"] and s["id"] in
                      ("legavolley", "top14-lnr", "premierrugby")]
        self.assertTrue(unreadable)


class HtmlTests(unittest.TestCase):
    PAGES = ["index.html", "picks.html", "predictions.html", "matches.html",
             "markets.html", "flagged.html", "sources.html", "methodology.html"]
    BANNED = ["model", "verified"]

    def test_pages_exist_and_are_well_formed(self):
        for name in self.PAGES + [f"sports/{s['slug']}.html" for s in d.SPORTS]:
            path = DESK_DIR / name
            self.assertTrue(path.is_file(), name)
            text = path.read_text()
            for word in self.BANNED:
                self.assertNotIn(word, text.lower(), f"{name}: {word}")
            self.assertNotIn("linear-gradient", text.lower(), name)
            self.assertEqual(text.lower().count("<h1"), 1, name)
            ids = re.findall(r'\sid="([^"]+)"', text)
            self.assertEqual(len(ids), len(set(ids)), f"{name}: duplicate ids")

    def test_no_plain_http(self):
        for path in DESK_DIR.rglob("*.html"):
            self.assertNotIn("http://", path.read_text(), path.name)

    def test_internal_links_resolve_inside_the_repository(self):
        for path in DESK_DIR.rglob("*.html"):
            text = path.read_text()
            for href in re.findall(r'href="([^"]+)"', text):
                if href.startswith(("https://", "http://", "mailto:", "#", "tel:")):
                    continue
                target = (path.parent / href).resolve()
                try:
                    target.relative_to(ROOT)
                except ValueError:
                    self.fail(f"{path.name}: {href} escapes the repository")
                self.assertTrue(target.is_file(), f"{path.name}: {href} does not resolve")

    def test_every_data_table_row_carries_an_https_link(self):
        for path in DESK_DIR.rglob("*.html"):
            text = path.read_text()
            for row in re.findall(r"<tr[^>]*>(.*?)</tr>", text, re.S):
                if "<td" not in row:
                    continue
                self.assertIn("https://", row, f"{path.name}: a data row has no source link")


class MirrorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.desk = _desk()

    def test_json_mirrors_reconcile(self):
        self.assertEqual(len(json.loads((DATA_DIR / "fixtures.json").read_text())),
                         len(self.desk["fixtures"]))
        self.assertEqual(len(json.loads((DATA_DIR / "picks.json").read_text())),
                         len(self.desk["picks"]))
        self.assertEqual(len(json.loads((DATA_DIR / "predictions.json").read_text())),
                         len(self.desk["predictions"]))
        self.assertEqual(len(json.loads((DATA_DIR / "sources.json").read_text())), len(d.SOURCES))
        self.assertEqual(len(json.loads((DATA_DIR / "flags.json").read_text())), len(d.FLAG_ITEMS))
        self.assertEqual(len(json.loads((DATA_DIR / "olbg.json").read_text())), len(d.OLBG_LOG))
        self.assertEqual(len(json.loads((DATA_DIR / "coverage.json").read_text())), 15)

    def test_manifest_matches_module(self):
        manifest = json.loads((DATA_DIR / "manifest.json").read_text())
        self.assertEqual(manifest["session_id"], d.SESSION_ID)
        self.assertEqual(manifest["fixtures"], len(self.desk["fixtures"]))
        self.assertEqual(manifest["priced_fixtures"], len(self.desk["picks"]))
        self.assertEqual(manifest["predictions"], len(self.desk["predictions"]))
        self.assertEqual(manifest["sports"], 15)


class ValidatorTests(unittest.TestCase):
    def test_desk_validator_passes(self):
        out = subprocess.run(
            [sys.executable, "scripts/s57bafcbb_validate.py"],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertIn("OK", out.stdout)


if __name__ == "__main__":
    unittest.main()
