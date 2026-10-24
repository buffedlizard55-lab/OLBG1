#!/usr/bin/env python3
"""Release gates for the 29dd717c evidence and static dashboard."""
from __future__ import annotations

import json
import math
import re
import sys
import unittest
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import s29dd717c_data as D  # noqa: E402
import s29dd717c_build as B  # noqa: E402

DATA = ROOT / "data" / "29dd717c"
SITE = ROOT / "29dd717c"
EXPECTED = {"Golf", "Volleyball", "Rugby Union", "Cricket", "Snooker", "Darts",
            "Baseball", "Gaelic Sports", "Greyhounds", "Tennis", "Motor Racing",
            "Handball", "Ice Hockey", "Basketball", "Rugby League"}


def dt(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "href" in a:
            self.hrefs.append(a["href"])
        if "id" in a:
            self.ids.add(a["id"])


class ScopeAndSources(unittest.TestCase):
    def test_exact_fifteen_sports_and_pages(self):
        self.assertEqual(len(D.SPORTS), 15)
        self.assertEqual({name for _slug, name, _url in D.SPORTS}, EXPECTED)
        for slug, _name, _url in D.SPORTS:
            self.assertTrue((SITE / "sports" / f"{slug}.html").is_file(), slug)

    def test_unique_ids_and_complete_coverage(self):
        ids = [f["id"] for f in D.FIXTURES]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(D.OLBG_OBSERVATIONS), 15)
        self.assertEqual(len(B.COVERAGE), 15)
        self.assertEqual({c["sport"] for c in B.COVERAGE}, {s[0] for s in D.SPORTS})

    def test_sources_are_official_https_timestamped_and_limited(self):
        for s in D.SOURCES:
            self.assertTrue(s["official"], s["id"])
            self.assertTrue(s["url"].startswith("https://"), s["id"])
            self.assertNotIn("olbg.com", s["url"], s["id"])
            dt(s["observed_at"])
            self.assertTrue(s["supports"].strip(), s["id"])
            self.assertTrue(s["limitation"].strip(), s["id"])

    def test_every_fixture_and_flag_has_official_links(self):
        sources = {s["id"]: s for s in D.SOURCES}
        for row in list(D.FIXTURES) + list(D.FLAGS):
            self.assertTrue(row["source_ids"], row["id"])
            for sid in row["source_ids"]:
                self.assertIn(sid, sources, (row["id"], sid))
                self.assertTrue(sources[sid]["official"])
        for f in D.FIXTURES:
            self.assertIsInstance(f["olbg_event_id"], int, f["id"])
            self.assertTrue(f["official_id"], f["id"])

    def test_olbg_is_discovery_only(self):
        for obs in D.OLBG_OBSERVATIONS:
            self.assertIn("Discovery only", obs["role"])
            self.assertIn("olbg.com", obs["url"])
            dt(obs["observed_at"])


class PublicationGate(unittest.TestCase):
    def test_retained_starts_are_upcoming_or_explicitly_blank(self):
        cutoff = dt(D.CUTOFF)
        for f in B.FIXTURES:
            if f["start_utc"]:
                self.assertGreater(dt(f["start_utc"]), cutoff, f["id"])
            else:
                self.assertIn("start", f["review_reasons"].lower(), f["id"])

    def test_every_blank_start_or_venue_is_flagged(self):
        flagged = (SITE / "flagged.html").read_text(encoding="utf-8")
        for f in B.FIXTURES:
            if not f["start_utc"] or not f["venue"] or f["flags"] or f["markets_withheld"]:
                self.assertTrue(f["review_reasons"], f["id"])
                self.assertIn("F29-ROW-" + f["id"].upper().replace("_", "-"), flagged)

    def test_started_nhl_and_nba_discoveries_are_not_picks(self):
        excluded = {"200007", "200008", "200006", "200003", "200001", "200002", "200010", "536111", "536112"}
        retained = {str(f["olbg_event_id"]) for f in D.FIXTURES}
        self.assertFalse(excluded & retained)
        self.assertIn("F29-001", (SITE / "flagged.html").read_text())
        self.assertIn("F29-002", (SITE / "flagged.html").read_text())

    def test_unconfirmed_kanturk_and_darts_have_no_pick(self):
        ids = {f["id"] for f in D.FIXTURES}
        self.assertNotIn("gaa-3531", ids)
        self.assertFalse([f for f in D.FIXTURES if f["sport"] == "darts"])
        text = (SITE / "flagged.html").read_text()
        self.assertIn("3531", text)
        self.assertIn("F29-003", text)


class PricingAndProse(unittest.TestCase):
    def test_market_probabilities_and_prices(self):
        for f in B.FIXTURES:
            self.assertTrue(f["markets"], f["id"])
            for m in f["markets"]:
                self.assertAlmostEqual(sum(o["probability"] for o in m["outcomes"]), 1.0, places=5,
                                       msg=f"{f['id']} {m['market']}")
                self.assertAlmostEqual(m["overround"], 1.0, places=5)
                for o in m["outcomes"]:
                    self.assertGreater(o["probability"], 0)
                    self.assertLess(o["probability"], 1)
                    self.assertAlmostEqual(o["decimal"], round(1 / o["probability"], 3), places=3)
                    self.assertEqual(o["american"], B.american(o["probability"]))
                    self.assertTrue(math.isfinite(o["decimal"]))

    def test_one_winner_and_winner_confidence_per_match(self):
        for f in B.FIXTURES:
            p = f["pick"]
            outcomes = f["markets"][0]["outcomes"]
            best = max(outcomes, key=lambda o: o["probability"])
            self.assertEqual(p["match_winner_lean"], best["label"])
            self.assertEqual(p["match_winner_probability"], best["probability"])
            self.assertIn(p["match_winner_confidence"], {"Low", "Medium", "High"})
            if p["match_winner_confidence"] == "High":
                self.assertGreaterEqual(best["probability"], 0.70)
                self.assertGreaterEqual(best["american"], -250)
                self.assertLessEqual(best["american"], 10000)

    def test_strict_high_gate_and_caps(self):
        order = {"Low": 0, "Medium": 1, "High": 2}
        for f in B.FIXTURES:
            p = f["pick"]
            if p["confidence"] == "High":
                self.assertGreaterEqual(p["probability"], 0.70, f["id"])
                self.assertGreaterEqual(p["american"], -250, f["id"])
                self.assertLessEqual(p["american"], 10000, f["id"])
                self.assertGreaterEqual(p["analysis_words"], 30, f["id"])
            if p["probability"] >= 0.70 and p["american"] < -250:
                self.assertNotEqual(p["confidence"], "High", f["id"])
            if f.get("max_confidence"):
                self.assertLessEqual(order[p["confidence"]], order[f["max_confidence"]])

    def test_unique_natural_analysis_and_prohibited_terms(self):
        seen = set()
        for f in D.FIXTURES:
            text = f["analysis"].strip()
            self.assertTrue(text.startswith("Selection:"), f["id"])
            words = re.findall(r"\b[\w’'-]+\b", text)
            self.assertGreaterEqual(len(words), 30, f["id"])
            self.assertIsNone(re.search(r"\b(model|verified)\b", text, re.I), f["id"])
            normal = re.sub(r"\W+", " ", text.lower()).strip()
            self.assertNotIn(normal, seen, f["id"])
            seen.add(normal)
            self.assertTrue(f["availability"].strip(), f["id"])

    def test_high_analysis_has_evidence_and_availability_context(self):
        for f in B.FIXTURES:
            if f["pick"]["confidence"] != "High":
                continue
            self.assertGreaterEqual(len(f["facts"]), 2, f["id"])
            self.assertTrue(f["source_ids"], f["id"])
            self.assertRegex(f["analysis"].lower(), r"injur|availab|team-sheet|retire|workload|medical")

    def test_counts_and_written_predictions(self):
        manifest = json.loads((DATA / "manifest.json").read_text())
        self.assertEqual(manifest["counts"]["fixtures"], len(B.FIXTURES))
        self.assertEqual(manifest["counts"]["picks"], len(B.PICKS))
        self.assertEqual(manifest["counts"]["predictions"], len(B.PICKS))
        self.assertEqual(manifest["counts"]["lines"], len(B.LINES))
        predictions = json.loads((DATA / "predictions.json").read_text())["predictions"]
        self.assertEqual(len(predictions), len(B.FIXTURES))
        self.assertEqual(len({p["analysis"] for p in predictions}), len(predictions))


class StaticSite(unittest.TestCase):
    def test_expected_pages_and_no_empty_active_sport(self):
        expected = {"index.html", "picks.html", "predictions.html", "matches.html", "sports.html",
                    "flagged.html", "sources.html", "methodology.html", "reverse-engineering.html",
                    "repository-audit.html"}
        for rel in expected:
            self.assertTrue((SITE / rel).is_file(), rel)
        for c in B.COVERAGE:
            text = (SITE / "sports" / f"{c['sport']}.html").read_text()
            if c["picks"]:
                self.assertIn("Selection:", text, c["sport"])
                self.assertIn("https://", text, c["sport"])
            else:
                self.assertIn("No supported selection published", text, c["sport"])

    def test_all_local_links_and_fragments_resolve(self):
        pages = list(SITE.rglob("*.html"))
        parsed = {}
        for path in pages:
            parser = Links()
            parser.feed(path.read_text(encoding="utf-8"))
            parsed[path] = parser
        for path, parser in parsed.items():
            for href in parser.hrefs:
                if not href or href.startswith(("https://", "http://", "mailto:", "tel:", "javascript:")):
                    continue
                parts = urlsplit(href)
                rel = unquote(parts.path)
                target = path if not rel else (path.parent / rel).resolve()
                self.assertTrue(target.exists(), f"{path.relative_to(SITE)} -> {href}")
                if parts.fragment and target.suffix == ".html":
                    self.assertIn(parts.fragment, parsed[target].ids,
                                  f"{path.relative_to(SITE)} -> {href}")

    def test_archive_registration_is_single_and_nojekyll_exists(self):
        build = (ROOT / "pipeline" / "build.py").read_text()
        self.assertEqual(build.count("29dd717c/index.html"), 1)
        self.assertTrue((ROOT / ".nojekyll").exists())

    def test_no_unrendered_python_or_placeholder_markup(self):
        for path in SITE.rglob("*.html"):
            text = path.read_text()
            self.assertNotIn("{esc(", text, path)
            self.assertNotIn("{p[", text, path)
            self.assertNotIn("None", text, path)
            self.assertNotIn("linear-gradient", text, path)


if __name__ == "__main__":
    unittest.main()
