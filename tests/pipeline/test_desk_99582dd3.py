"""Contract tests for the 99582dd3 independent offline verification desk (T9958).

Offline only: every test works from retained evidence and never opens a socket.
The audit and builders are deterministic at a fixed build timestamp.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import s99582dd3_audit as audit  # noqa: E402
import s99582dd3_build as build  # noqa: E402

FIXED_NOW = "2026-10-23T19:45:00Z"
EXPECTED_15 = {name for name, _ in audit.SPORTS}


class LinkCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links: list[str] = []
        self.h1 = 0
        self.title = 0

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "h1":
            self.h1 += 1
        if tag == "title":
            self.title += 1
        if tag == "a" and d.get("href") is not None:
            self.links.append(d["href"])
        if tag in ("link", "script", "img"):
            t = d.get("href") or d.get("src")
            if t is not None:
                self.links.append(t)


class TestDesk99582dd3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.data_dir = Path(cls.tmp.name) / "data"
        cls.site_dir = Path(cls.tmp.name) / "site"
        cls.summary = audit.run(FIXED_NOW, cls.data_dir)
        cls.slate = json.loads((cls.data_dir / "slate.json").read_text())
        cls.flags = json.loads((cls.data_dir / "flags.json").read_text())
        build.build(FIXED_NOW, cls.site_dir)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_exact_15_sports_five_events_each(self):
        self.assertEqual({r["sport"] for r in self.slate}, EXPECTED_15)
        self.assertEqual(len(self.slate), 75)
        for name in EXPECTED_15:
            self.assertEqual(sum(1 for r in self.slate if r["sport"] == name), 5, name)

    def test_every_row_has_official_https_source(self):
        for r in self.slate:
            self.assertTrue(r["official_urls"], r["id"])
            for u in r["all_source_urls"]:
                p = urlparse(u)
                self.assertEqual(p.scheme, "https")
                self.assertIn(p.hostname, audit.OFFICIAL_HOSTS | audit.DISCOVERY_HOSTS)

    def test_high_grade_rule_and_window(self):
        for r in self.slate:
            rec = r["recommended"]
            if rec["is_high"]:
                self.assertGreater(rec["prob"], 0.70)
                self.assertGreaterEqual(rec["american"], -250)
                self.assertLessEqual(rec["american"], 10000)
            for m in r["markets"]:
                if (m.get("confidence") or "").lower() == "high":
                    self.assertGreater(m["fair_prob"], 0.70)
                    self.assertGreaterEqual(m["fair_american"], -250)
                    self.assertLessEqual(m["fair_american"], 10000)
                    self.assertFalse(m.get("chalk_suppressed"))

    def test_price_arithmetic_reproduces(self):
        for r in self.slate:
            for m in r["markets"]:
                p, dec = m["fair_prob"], m["fair_decimal"]
                self.assertLess(abs(1.0 / p - dec), 0.011, r["id"])
                derived = audit.american_from_prob(p)
                self.assertTrue(
                    audit.american_matches(derived, m["fair_american"]),
                    f"{r['id']} {m['market_label']} {derived} vs {m['fair_american']}")
                if m.get("counter_prob") is not None:
                    self.assertLess(abs(m["counter_prob"] + p - 1.0), 0.011)

    def test_prose_gates(self):
        for r in self.slate:
            prose = r["prediction"]
            self.assertTrue(prose, r["id"])
            self.assertGreaterEqual(len(prose.split()), 30)
            self.assertNotIn("model", prose.lower())
            self.assertNotIn("verified", prose.lower())
            self.assertIn("selection", prose.lower())

    def test_known_cross_desk_conflicts_and_direction_flag(self):
        codes = {f["code"] for f in self.flags}
        self.assertIn("G7-CONFLICT", codes)
        self.assertIn("G6-DIRECTION", codes)
        conflict_events = {f["event_id"] for f in self.flags if f["code"] == "G7-CONFLICT"}
        self.assertIn("IH01", conflict_events)   # Montreal/Chicago opposite favorites
        direction = next(f for f in self.flags if f["code"] == "G6-DIRECTION")
        self.assertEqual(direction["event_id"], "GF01")
        # every conflicted event keeps its badge, which the builder uses to
        # keep it out of the clean executive-summary set
        badged = {r["id"] for r in self.slate if r["cross_flags"]}
        self.assertIn("IH01", badged)
        for r in self.slate:
            if r["id"] in badged:
                self.assertTrue(r["cross_flags"])

    def test_no_hard_holds_and_quarantined_olbg_cards(self):
        self.assertEqual(sum(1 for r in self.slate if r["hard_fail"]), 0)
        olbg = [f for f in self.flags if f["code"] == "G1-OLBG-UNCONFIRMED"]
        self.assertEqual(len(olbg), 7)

    def test_deterministic_outputs(self):
        with tempfile.TemporaryDirectory() as td:
            again = Path(td)
            audit.run(FIXED_NOW, again)
            for name in ("slate.json", "flags.json", "predictions_gated.json", "sources.json"):
                self.assertEqual((again / name).read_text(),
                                 (self.data_dir / name).read_text(), name)

    def test_site_pages_structure_and_links(self):
        pages = ["index.html", "todays-picks.html", "upcoming-picks.html", "markets.html",
                 "predictions.html", "flagged.html", "sources.html", "repo-audit.html",
                 "methodology.html"] + [f"sports/{slug}.html" for _, slug in audit.SPORTS]
        for rel in pages:
            path = self.site_dir / rel
            self.assertTrue(path.is_file(), rel)
            c = LinkCollector()
            c.feed(path.read_text())
            self.assertEqual(c.h1, 1, rel)
            self.assertEqual(c.title, 1, rel)
            for href in c.links:
                if href.startswith(("https://", "mailto:", "#")):
                    continue
                clean = href.split("#", 1)[0].split("?", 1)[0]
                target = (path.parent / unquote(clean)).resolve()
                self.assertTrue(str(target).startswith(str(self.site_dir.resolve())), rel)
                self.assertTrue(target.is_file(), f"{rel}: broken {href}")

    def test_flag_count_matches_summary(self):
        self.assertEqual(self.summary["flags_total"], len(self.flags))
        self.assertEqual(self.summary["sports"], 15)
        self.assertEqual(self.summary["events"], 75)
        self.assertEqual(self.summary["markets_total"], 472)


if __name__ == "__main__":
    unittest.main()
