"""Automated regression gate for session efe12010 (/efe12010/ & data/efe12010/).

Enforces the contract this desk published:

* every fixture row either carries an official source link or is explicitly blank and flagged;
* no sporting fact is confirmed by OLBG, which is a discovery layer only;
* every high-confidence selection sits inside the -250 / +10000 fair-price band;
* published call text is at least thirty words, unique, and free of two banned words;
* the exports, the HTML and the generator all agree, and the build is reproducible.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "efe12010"
SITE = ROOT / "efe12010"
FIXTURES = DATA / "fixtures.json"

BANNED_WORDS = ("model", "verified")

# Governing bodies, leagues, tours and organisers. OLBG is deliberately absent: it may
# put a fixture on the desk but it may never establish a fact about one.
OFFICIAL_HOSTS = {
    "api-web.nhle.com",
    "api.nhle.com",
    "statsapi.mlb.com",
    "api-live.euroleague.net",
    "www.euroleaguebasketball.net",
    "www.atptour.com",
    "www.wst.tv",
    "www.formula1.com",
    "www.cricket.com.au",
}

BAND_P_MAX = 250.0 / 350.0          # fair -250
BAND_P_MIN = 100.0 / 10100.0        # fair +10000
HIGH_FLOOR = 0.62

PAGES = [
    "index.html", "executive-summary.html", "high-confidence.html", "predictions.html",
    "matches.html", "markets.html", "sports.html", "coverage.html", "sources.html",
    "flagged.html", "analysis.html", "reverse-engineering.html", "methodology.html",
]
SPORTS = [
    "golf", "volleyball", "rugby-union", "cricket", "snooker", "darts", "baseball",
    "gaelic", "greyhounds", "tennis", "motor-racing", "handball", "ice-hockey",
    "basketball", "rugby-league",
]


@unittest.skipUnless(FIXTURES.is_file(), "efe12010 desk not yet generated")
class DeskEfe12010Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(FIXTURES.read_text(encoding="utf-8"))
        cls.fixtures = cls.payload["fixtures"]
        cls.priced = [f for f in cls.fixtures if f["markets"]]
        cls.high = [f for f in cls.priced if f["confidence"] == "high"]
        cls.preds = json.loads((DATA / "predictions.json").read_text(encoding="utf-8"))["entries"]

    # ------------------------------------------------------------------ shape
    def test_every_requested_sport_has_a_page_and_appears_in_the_data(self) -> None:
        for slug in SPORTS:
            with self.subTest(sport=slug):
                self.assertTrue((SITE / "sports" / f"{slug}.html").is_file())
        self.assertEqual(set(self.payload["sports"]), set(SPORTS))

    def test_all_desk_pages_exist_and_carry_the_shared_shell(self) -> None:
        for name in PAGES:
            page = SITE / name
            with self.subTest(page=name):
                self.assertTrue(page.is_file())
                text = page.read_text(encoding="utf-8")
                self.assertIn('<link rel="stylesheet" href="assets/style.css">', text)
                self.assertIn("Flagged for Review", text)

    def test_desk_ships_its_own_assets(self) -> None:
        css = (SITE / "assets" / "style.css").read_text(encoding="utf-8")
        self.assertTrue((SITE / "assets" / "app.js").is_file())
        self.assertNotIn("linear-gradient", css)

    # -------------------------------------------------------------- provenance
    def test_confirmed_fixtures_cite_an_official_host_and_nothing_else(self) -> None:
        for f in self.fixtures:
            if f["status"] not in ("verified", "partial"):
                continue
            with self.subTest(fixture=f["id"]):
                self.assertTrue(f["sources"], "a confirmed fixture must carry a source")
                for s in f["sources"]:
                    host = urlparse(s["url"]).netloc
                    self.assertIn(host, OFFICIAL_HOSTS)
                    self.assertTrue(s["url"].startswith("https://"))

    def test_olbg_never_confirms_a_fixture(self) -> None:
        for f in self.fixtures:
            for s in f["sources"]:
                self.assertNotIn("olbg.com", s["url"], f"{f['id']} cites OLBG as evidence")

    def test_fixture_states_are_one_of_three_and_behave_accordingly(self) -> None:
        for f in self.fixtures:
            with self.subTest(fixture=f["id"]):
                self.assertIn(f["status"], ("verified", "partial", "unverified"))
                if f["status"] == "verified":
                    self.assertTrue(f["markets"], "a confirmed fixture should be priced")
                elif f["status"] == "partial":
                    # confirmed to exist, but an input needed for pricing was missing
                    self.assertEqual(f["markets"], [])
                    self.assertTrue(f["sources"])
                    self.assertTrue(f["flags"] or f["unavailable_markets"])
                else:
                    self.assertEqual(f["markets"], [])
                    self.assertEqual(f["sources"], [])
                    self.assertEqual(f["start_utc"], "")
                    self.assertEqual(f["venue"], "")
                    self.assertTrue(f["flags"], "an unconfirmed fixture must be flagged")

    def test_fixture_ids_are_unique_and_deterministic(self) -> None:
        ids = [f["id"] for f in self.fixtures]
        self.assertEqual(len(ids), len(set(ids)))

    def test_no_priced_fixture_is_missing_its_inputs(self) -> None:
        for f in self.priced:
            with self.subTest(fixture=f["id"]):
                self.assertTrue(f["inputs"], "a priced fixture must list its official inputs")

    # ------------------------------------------------------------------ prices
    def test_every_exclusive_market_is_a_coherent_book(self) -> None:
        for f in self.priced:
            for m in f["markets"]:
                with self.subTest(fixture=f["id"], market=m["key"]):
                    total = sum(o["probability"] for o in m["outcomes"])
                    if m["exclusive"]:
                        self.assertAlmostEqual(total, 1.0, places=5)
                    else:
                        self.assertGreater(total, 1.0)
                    for o in m["outcomes"]:
                        self.assertGreater(o["fair_odds"], 1.0)
                        self.assertLess(o["odds"], o["fair_odds"])

    def test_band_membership_matches_the_published_rule(self) -> None:
        for f in self.priced:
            for m in f["markets"]:
                for o in m["outcomes"]:
                    expected = BAND_P_MIN <= o["probability"] <= BAND_P_MAX + 1e-12
                    self.assertEqual(o["in_band"], expected, f"{f['id']}/{o['selection']}")

    def test_high_confidence_picks_clear_the_floor_and_the_band(self) -> None:
        self.assertGreaterEqual(len(self.high), 10)
        for f in self.high:
            bp = f["band_pick"]
            with self.subTest(fixture=f["id"], selection=bp["selection"]):
                self.assertGreaterEqual(bp["probability"], HIGH_FLOOR)
                self.assertLessEqual(bp["probability"], BAND_P_MAX + 1e-12)
                american = int(bp["fair_american"].replace("+", ""))
                self.assertGreaterEqual(american, -250)
                self.assertLessEqual(american, 10000)
                self.assertEqual(f["status"], "verified")

    def test_a_price_capped_favourite_is_never_published_as_high(self) -> None:
        for f in self.priced:
            pick = f["pick"]
            if pick and not pick["in_band"]:
                with self.subTest(fixture=f["id"]):
                    self.assertNotEqual(f["band_pick"]["selection"], pick["selection"])
                    self.assertTrue(any("Price cap" in x for x in f["flags"]))

    # -------------------------------------------------------------- call copy
    def test_every_priced_fixture_has_a_written_call(self) -> None:
        self.assertEqual(len(self.preds), len(self.priced))

    def test_calls_are_long_enough_unique_and_name_their_selection(self) -> None:
        seen = set()
        for p in self.preds:
            with self.subTest(fixture=p["fixture_id"]):
                self.assertGreaterEqual(len(p["text"].split()), 30)
                self.assertNotIn(p["text"], seen)
                seen.add(p["text"])
                self.assertTrue(p["availability"].strip())
                self.assertTrue(p["sources"])

    def test_banned_words_never_reach_published_call_text(self) -> None:
        for p in self.preds:
            lowered = (p["text"] + " " + p["availability"]).lower()
            for word in BANNED_WORDS:
                with self.subTest(fixture=p["fixture_id"], word=word):
                    self.assertNotIn(word, lowered)

    def test_banned_words_never_reach_the_rendered_call_blocks(self) -> None:
        pattern = re.compile(r'<article class="(?:call|bigcall)".*?</article>', re.S)
        for name in ("high-confidence.html", "predictions.html", "executive-summary.html"):
            text = (SITE / name).read_text(encoding="utf-8")
            for block in pattern.findall(text):
                body = re.sub(r"<[^>]+>", " ", block).lower()
                for word in BANNED_WORDS:
                    with self.subTest(page=name, word=word):
                        self.assertNotIn(word, body)

    # ----------------------------------------------------------------- exports
    def test_csv_exports_line_up_with_the_json(self) -> None:
        import csv

        with (DATA / "matches.csv").open(encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        self.assertEqual(len(rows), len(self.fixtures))
        self.assertEqual({r["fixture_id"] for r in rows}, {f["id"] for f in self.fixtures})

        with (DATA / "markets.csv").open(encoding="utf-8") as fh:
            market_rows = list(csv.DictReader(fh))
        self.assertEqual(
            len(market_rows),
            sum(len(m["outcomes"]) for f in self.fixtures for m in f["markets"]),
        )

    def test_flag_register_covers_every_flagged_fixture(self) -> None:
        flags = json.loads((DATA / "flags.json").read_text(encoding="utf-8"))
        registered = {x["fixture_id"] for x in flags["fixture_flags"]}
        expected = {f["id"] for f in self.fixtures if f["flags"] or f["unavailable_markets"]}
        self.assertEqual(registered, expected)
        self.assertTrue(flags["blocked_sources"])

    def test_every_blocked_source_names_what_was_tried_and_what_failed(self) -> None:
        sources = json.loads((DATA / "sources.json").read_text(encoding="utf-8"))
        for b in sources["blocked"]:
            with self.subTest(source=b["name"]):
                self.assertTrue(b["attempted"].strip())
                self.assertTrue(b["failure"].strip())
                self.assertTrue(b["url"].startswith("https://"))

    # ------------------------------------------------------------ reproducible
    def test_build_is_reproducible(self) -> None:
        before = FIXTURES.read_bytes()
        res = subprocess.run(
            [sys.executable, "scripts/sefe12010_build.py"],
            cwd=ROOT, capture_output=True, text=True, timeout=300,
        )
        self.assertEqual(res.returncode, 0, msg=f"{res.stdout}\n{res.stderr}")
        self.assertEqual(FIXTURES.read_bytes(), before, "rebuild changed the exports")


if __name__ == "__main__":
    unittest.main()
