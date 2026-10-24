"""Gate for desk 8cfb80b2: tier arithmetic, prose rules, provenance and links."""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.s8cfb80b2_data import SOURCES, EVENTS, PICKS, SPORTS, FLAGS, COVERAGE


class DeskData(unittest.TestCase):
    def test_every_row_has_a_known_source(self):
        for ev in EVENTS:
            self.assertTrue(ev["src"], ev["id"])
            for sid in ev["src"]:
                self.assertIn(sid, SOURCES, ev["id"])

    def test_only_the_fifteen_sports(self):
        allowed = {s for s, _, _ in SPORTS}
        self.assertEqual(len(allowed), 15)
        for ev in EVENTS:
            self.assertIn(ev["sport"], allowed)

    def test_official_basis_requires_a_start(self):
        for ev in EVENTS:
            if ev["basis"] == "official":
                self.assertRegex(ev["start"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

    def test_tiers_match_their_own_numbers(self):
        for p in PICKS:
            in_band = -250 <= p["american"] <= 10000
            if p["tier"] == "High":
                self.assertGreater(p["prob"], 0.70, p["id"])
                self.assertTrue(in_band, p["id"])
            else:
                self.assertFalse(p["prob"] > 0.70 and in_band,
                                 f"{p['id']} qualifies for High but is labelled {p['tier']}")

    def test_picks_have_an_official_source_and_two_markets(self):
        by_id = {e["id"]: e for e in EVENTS}
        for p in PICKS:
            ev = by_id[p["event"]]
            self.assertTrue(any(SOURCES[s]["role"] == "official" for s in ev["src"]), p["id"])
            self.assertGreaterEqual(len(p["markets"]), 2, p["id"])

    def test_predictions_are_long_unique_and_clean(self):
        grams = []
        for p in PICKS:
            words = re.findall(r"[A-Za-z0-9'’/?.-]+", p["prediction"])
            self.assertGreaterEqual(len(words), 30, p["id"])
            low = p["prediction"].lower()
            for banned in ("model", "verified", "verify"):
                self.assertNotIn(banned, low, p["id"])
            tokens = re.findall(r"[a-z0-9']+", low)
            g = {" ".join(tokens[i:i + 6]) for i in range(max(0, len(tokens) - 5))}
            for other in grams:
                self.assertLessEqual(len(g & other), 1, p["id"])
            grams.append(g)

    def test_no_event_is_priced_twice_on_the_same_selection(self):
        seen = set()
        for p in PICKS:
            key = (p["event"], p["selection"])
            self.assertNotIn(key, seen)
            seen.add(key)

    def test_flags_and_coverage(self):
        self.assertGreaterEqual(len(FLAGS), 5)
        for f in FLAGS:
            self.assertRegex(f[0], r"^F-8C-\d\d$")
            self.assertTrue(f[4].startswith("https://"))
        self.assertEqual({s for s, _, _ in SPORTS}, set(COVERAGE))

    def test_json_is_regenerated_from_the_module(self):
        data = ROOT / "data" / "8cfb80b2"
        self.assertEqual(json.loads((data / "picks.json").read_text()), json.loads(json.dumps(PICKS)))
        self.assertEqual(json.loads((data / "events.json").read_text()), json.loads(json.dumps(EVENTS)))


class DeskBuild(unittest.TestCase):
    def test_build_and_validate(self):
        for cmd in (["python3", "scripts/s8cfb80b2_build.py"],
                    ["python3", "scripts/s8cfb80b2_validate.py"]):
            out = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(out.returncode, 0, out.stdout + out.stderr)

    def test_all_fifteen_sport_pages_exist(self):
        for slug, _, _ in SPORTS:
            self.assertTrue((ROOT / "8cfb80b2" / "sports" / f"{slug}.html").exists(), slug)


if __name__ == "__main__":
    unittest.main()
