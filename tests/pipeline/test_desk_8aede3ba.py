"""Contract tests for desk 8aede3ba (offline; no network access)."""

from __future__ import annotations

import json
import re
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "8aede3ba"
SITE = ROOT / "8aede3ba"

SPORTS = [
    "golf", "volleyball", "rugby-union", "cricket", "snooker", "darts", "baseball",
    "gaelic-sports", "greyhounds", "tennis", "motor-racing", "handball",
    "ice-hockey", "basketball", "rugby-league",
]
OFFICIAL_HOSTS = {
    "www.atptour.com", "wtafiles.wtatennis.com", "www.wtatennis.com", "www.nba.com",
    "api-web.nhle.com", "statsapi.mlb.com", "www.mlb.com", "www.pgatour.com",
    "www.europeantour.com", "www.lpga.com", "www.formula1.com", "www.wst.tv",
    "www.pdc.tv", "www.legavolley.it", "www.plusliga.pl", "www.tauronliga.pl",
    "www.unitedrugby.com", "stats.unitedrugby.com", "top14.lnr.fr",
    "www.icc-cricket.com", "www.pcb.com.pk", "scoring.nzc.nz", "www.nzc.nz",
    "munster.gaa.ie", "gaacork.ie", "www.galwaygaa.ie", "www.waterfordgaa.ie",
    "www.gbgb.org.uk", "ehfcl.eurohandball.com", "www.eurohandball.com",
    "www.nrl.com", "www.intrl.sport",
}
BANNED = re.compile(r"\b(model|models|verified|verification|verify)\b", re.I)


def host(url: str) -> str:
    return re.sub(r"^https://", "", url).split("/")[0]


class Desk8aede3baTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = json.loads((DATA / "fixtures.json").read_text())
        cls.rows = cls.doc["fixtures"]
        cls.preds = json.loads((DATA / "predictions.json").read_text())["predictions"]
        cls.flags = json.loads((DATA / "flagged.json").read_text())["flags"]
        cls.summary = json.loads((DATA / "summary.json").read_text())
        cls.manifest = json.loads((DATA / "site-manifest.json").read_text())

    # --- scope -------------------------------------------------------------
    def test_all_fifteen_brief_sports_present(self) -> None:
        self.assertEqual({r["sport"] for r in self.rows}, set(SPORTS))
        self.assertEqual(self.summary["sports_covered"], 15)

    def test_fixture_ids_unique(self) -> None:
        ids = [r["id"] for r in self.rows]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_row_cites_an_allowlisted_governing_body(self) -> None:
        for r in self.rows:
            self.assertTrue(r["official_url"].startswith("https://"), r["id"])
            self.assertIn(host(r["official_url"]), OFFICIAL_HOSTS, r["id"])

    def test_olbg_never_used_as_verification(self) -> None:
        for r in self.rows:
            self.assertIn("olbg.com", r["olbg_url"])
            self.assertNotIn("olbg.com", r["official_url"])
            self.assertNotIn("olbg.com", r["secondary_official_url"])

    # --- pricing -----------------------------------------------------------
    def test_every_fixture_has_four_market_families(self) -> None:
        for r in self.rows:
            keys = [m["market_key"] for m in r["markets"]]
            self.assertEqual(len(keys), 4, r["id"])
            self.assertEqual(len(set(keys)), 4, r["id"])

    def test_fair_mass_and_one_over_probability(self) -> None:
        for r in self.rows:
            for m in r["markets"]:
                self.assertAlmostEqual(sum(o["p_fair"] for o in m["outcomes"]), 1.0, places=4)
                for o in m["outcomes"]:
                    self.assertGreater(o["p_fair"], 0)
                    self.assertLess(o["p_fair"], 1)
                    self.assertAlmostEqual(o["decimal_odds"] * o["p_fair"], 1.0, delta=2e-3)

    def test_american_matches_decimal(self) -> None:
        for r in self.rows:
            for m in r["markets"]:
                for o in m["outcomes"]:
                    dec, am = o["decimal_odds"], o["american_odds"]
                    expect = int(round((dec - 1) * 100)) if dec >= 2 else int(round(-100 / (dec - 1)))
                    self.assertEqual(am, expect, f'{r["id"]}/{o["label"]}')

    def test_published_selection_is_quoted(self) -> None:
        for r in self.rows:
            labels = [o["label"] for m in r["markets"] for o in m["outcomes"]]
            self.assertIn(r["selection"], labels, r["id"])

    # --- confidence gate ---------------------------------------------------
    def test_high_picks_clear_both_gates(self) -> None:
        high = [r for r in self.rows if r["confidence"] == "High"]
        self.assertGreater(len(high), 40)
        for r in high:
            self.assertGreaterEqual(r["selection_prob"], 0.70, r["id"])
            self.assertGreaterEqual(r["selection_american"], -250, r["id"])
            self.assertLessEqual(r["selection_american"], 10000, r["id"])

    def test_no_chalk_above_seventy_is_published_high(self) -> None:
        for r in self.rows:
            if r["confidence"] == "High":
                continue
            self.assertFalse(
                r["selection_prob"] >= 0.70 and r["selection_american"] >= -250,
                f'{r["id"]} clears both gates but is not marked High',
            )

    def test_each_sport_has_at_least_three_high_picks_or_a_flag(self) -> None:
        per = Counter(r["sport"] for r in self.rows if r["confidence"] == "High")
        short = {s: per.get(s, 0) for s in SPORTS if per.get(s, 0) < 3}
        self.assertEqual(short, {"greyhounds": 0})
        gap_ids = {f["id"] for f in self.flags}
        self.assertIn("F-8A-10", gap_ids)
        self.assertIn("F-8A-11", gap_ids)

    # --- prose -------------------------------------------------------------
    def test_predictions_bijection_word_count_and_vocabulary(self) -> None:
        high_ids = {r["id"] for r in self.rows if r["confidence"] == "High"}
        self.assertEqual({p["fixture_id"] for p in self.preds}, high_ids)
        for p in self.preds:
            words = p["text"].split()
            self.assertGreaterEqual(len(words), 30, p["fixture_id"])
            self.assertGreaterEqual(p["word_count"], 30)
            self.assertIsNone(BANNED.search(p["text"]), p["fixture_id"])

    def test_predictions_are_unique_and_name_their_selection(self) -> None:
        grams: Counter = Counter()
        for p in self.preds:
            toks = [re.sub(r"[^\w']", "", w).lower() for w in p["text"].split()]
            toks = [t for t in toks if t]
            for i in range(len(toks) - 6):
                grams[tuple(toks[i:i + 7])] += 1
        self.assertEqual([g for g, c in grams.items() if c > 1], [])
        for p in self.preds:
            row = next(r for r in self.rows if r["id"] == p["fixture_id"])
            low = p["text"].lower()
            if row["selection"].lower() not in low:
                line = re.search(r"[-+]?\d+(?:\.\d+)?", row["selection"])
                self.assertTrue(any(t.lower() in low for t in (row["home"].split()[0], row["away"].split()[0])), p["fixture_id"])
                self.assertIsNotNone(line)
                self.assertIn(line.group(0).lstrip("+"), low, p["fixture_id"])

    # --- registers ---------------------------------------------------------
    def test_flags_are_source_linked(self) -> None:
        self.assertGreaterEqual(len(self.flags), 10)
        for f in self.flags:
            self.assertTrue(f["source_url"].startswith("https://"), f["id"])
            self.assertIn(f["severity"], ("high", "medium", "low", "info"))

    def test_counts_reconcile(self) -> None:
        c = self.doc["counts"]
        self.assertEqual(c["fixtures"], len(self.rows))
        self.assertEqual(c["high"], sum(1 for r in self.rows if r["confidence"] == "High"))
        self.assertEqual(c["markets"], sum(len(r["markets"]) for r in self.rows))
        self.assertEqual(self.summary["predictions"], len(self.preds))
        self.assertEqual(self.summary["flags"], len(self.flags))

    # --- site --------------------------------------------------------------
    def test_pages_and_assets_exist(self) -> None:
        for rel in self.manifest["pages"]:
            self.assertTrue((SITE / rel).is_file(), rel)
        self.assertTrue((SITE / "assets" / "desk.css").is_file())
        for slug in SPORTS:
            self.assertTrue((SITE / "sports" / f"{slug}.html").is_file(), slug)

    def test_no_localhost_or_remote_assets_in_pages(self) -> None:
        for rel in self.manifest["pages"]:
            text = (SITE / rel).read_text()
            self.assertNotIn("localhost", text, rel)
            self.assertNotIn("127.0.0.1", text, rel)
            self.assertNotIn("<script", text.lower(), rel)

    def test_validator_exits_clean(self) -> None:
        import subprocess
        import sys
        proc = subprocess.run(
            [sys.executable, "scripts/s8aede3ba_validate.py"],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
