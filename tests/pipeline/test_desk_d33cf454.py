"""Desk-level contract tests for d33cf454 (session d33cf454-olbg1)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from sd33cf454_data import EVENTS, PICKS, SOURCES, SPORTS, FLAGS, COVERAGE  # noqa: E402


def test_all_fifteen_sports_present():
    slugs = {s for s, _, _ in SPORTS}
    expected = {
        "golf", "volleyball", "rugby-union", "cricket", "snooker", "darts",
        "baseball", "gaelic", "greyhounds", "tennis", "motor-racing",
        "handball", "ice-hockey", "basketball", "rugby-league",
    }
    assert expected <= slugs, f"missing sports: {expected - slugs}"


def test_every_event_has_a_source():
    for ev in EVENTS:
        assert ev["src"], f"{ev['id']}: no source"
        assert ev["sport"] in {s for s, _, _ in SPORTS}, f"{ev['id']}: unknown sport"


def test_every_source_is_https():
    for sid, s in SOURCES.items():
        assert s["url"].startswith("https://"), f"{sid}: not https"
        assert s["role"] in ("official", "discovery"), f"{sid}: bad role"


def test_high_picks_respect_price_window():
    for p in PICKS:
        prob = p["prob"]
        american = int(round(-100 * prob / (1 - prob))) if prob >= 0.5 else int(round(100 * (1 - prob) / prob))
        assert -250 <= american <= 10000, f"{p['id']}: price outside window"
        if p["tier"] == "High":
            assert prob > 0.70, f"{p['id']}: High but prob <= 0.70"
            assert -250 <= p["american"] <= 10000, f"{p['id']}: High but american outside band"


def test_predictions_at_least_30_words_and_unique():
    import re

    def wc(t):
        return len(re.findall(r"[A-Za-z0-9'’/?.-]+", t))

    seen = []
    for p in PICKS:
        assert wc(p["prediction"]) >= 30, f"{p['id']}: under 30 words"
        for w in ("model", "verified", "verify"):
            assert w not in p["prediction"].lower(), f"{p['id']}: banned word {w}"
        grams = {
            " ".join(re.findall(r"[a-z0-9']+", p["prediction"].lower())[i : i + 6])
            for i in range(max(0, len(re.findall(r"[a-z0-9']+", p["prediction"].lower())) - 5))
        }
        for _, other in seen:
            assert len(grams & other) <= 1, f"{p['id']}: repeated 6-gram"
        seen.append((p["id"], grams))


def test_flagged_have_links():
    for fid, title, scope, detail, link in FLAGS:
        assert link.startswith("https://"), f"{fid}: no https link"


def test_coverage_covers_all_sports():
    for slug, _, _ in SPORTS:
        assert slug in COVERAGE, f"{slug}: missing coverage note"
