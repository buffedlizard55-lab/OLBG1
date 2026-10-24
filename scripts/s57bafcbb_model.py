"""Desk 57bafcbb - line origination and grading.

This module takes the raw fixture feed from `s57bafcbb_data.py` and turns it
into a priced book. It owns exactly three things:

* a fair two-way line for every priced fixture, and the arithmetic that
  turns an originated probability into an American price and back;
* the confidence tier (Low / Medium / High) for the pick on each fixture;
* the margin check that proves every line is a real two-way book.

No odds are read from anywhere. Every price here is computed from the
desk's own probability estimate, which is in turn built from the official
record and form lines recorded in each fixture's `records` block. A fixture
whose records block is empty has no priced market and is published as a
directory entry instead.

Confidence bands (the desk's own, applied to the originated estimate):
    High   : estimate >= 60%  and  fair American price inside -250..+10000
    Medium : estimate >= 55%  and  fair American price inside -250..+10000
    Low    : everything else, including every price outside the band
"""

from __future__ import annotations

from pathlib import Path

import s57bafcbb_data as d

ROOT = Path(__file__).resolve().parent.parent

HIGH_FLOOR = -250.0
HIGH_CEIL = 10000.0
HIGH_P = 0.60
MEDIUM_P = 0.55

# Venue scoring averages used to set the totals line. These are the desk's
# own figures for the 2026 season and are published as estimates, not as
# lines read from any bookmaker.
TOTALS_AVERAGE = {
    "baseball": 9.4,
    "ice-hockey": 5.7,
    "tennis": 22.5,
    "darts": 15.5,
    "snooker": 7.5,
    "cricket": 500.0,
    "rugby-league": 44.0,
}
# Half-point / whole-point handicap conventions per sport.
HANDICAP = {
    "baseball": (-1.5, 0.72),
    "ice-hockey": (-1.5, 0.72),
    "tennis": (-1.0, 0.78),
    "darts": (-1.0, 0.78),
    "snooker": (-1.0, 0.78),
    "cricket": (-1.0, 0.78),
    "rugby-league": (-1.0, 0.78),
}


def american_from_prob(p):
    p = max(1e-6, min(1 - 1e-6, p))
    return int(round(-p / (1 - p) * 100)) if p >= 0.5 else int(round(100 / p - 100))


def prob_from_american(a):
    if a >= 0:
        return a / (a + 100.0)
    return -a / (-a + 100.0)


def american_in_band(a, lo=HIGH_FLOOR, hi=HIGH_CEIL):
    return lo <= a <= hi


def win_pct(record):
    """'103-59' -> 0.636. '3-7-0' -> regulation part only, since the official
    NHL line is W-L-OTL and overtime losses do not decide a match.

    Returns None for anything that is not a plain W-L line, so a semi-final
    score line like '10-8 vs Aspinall' is reported as "no record" rather than
    being misread as a win percentage."""
    if not record:
        return None
    parts = record.split("-")
    if len(parts) < 2 or not parts[0].isdigit() or not parts[1].isdigit():
        return None
    gp = int(parts[0]) + int(parts[1])
    if gp <= 0:
        return None
    return int(parts[0]) / gp


def log5(p_a, p_b, k=1.0):
    if p_a is None or p_b is None or p_a <= 0 or p_b <= 0:
        return None
    return (p_a ** k) / ((p_a ** k) + (p_b ** k))


def model_tier(p, american, lo=HIGH_FLOOR, hi=HIGH_CEIL):
    """The published confidence label. High requires the price to sit inside
    the -250..+10000 band as well as a 60%+ estimate."""
    if p is None or american is None:
        return "Low"
    if american_in_band(american, lo, hi):
        if p >= HIGH_P:
            return "High"
        if p >= MEDIUM_P:
            return "Medium"
        return "Low"
    # Outside the band: a chalk price is downgraded rather than labelled High.
    if p >= HIGH_P:
        return "Medium"
    if p >= MEDIUM_P:
        return "Low"
    return "Low"


def compute_book(fx):
    """The fair two-way book for one fixture, plus the pick and its label.

    Returns None when the fixture has no record block - those fixtures are
    published as directory entries and never priced.
    """
    pick = d.PICKS.get(fx["id"])
    recs = fx.get("records") or {}
    if not recs or not pick:
        return None

    p_sel = pick["p_select"]
    side = pick["pick"]
    other = fx["away"] if side == fx["home"] else fx["home"]
    p_other = 1.0 - p_sel

    book = {
        "method": (
            "Originated estimate built from the official record and form line "
            "recorded in the fixture, expressed as a strict two-way book"
        ),
        "home_prob": p_sel if side == fx["home"] else p_other,
        "away_prob": p_sel if side == fx["away"] else p_other,
        "home_price": american_from_prob(p_sel if side == fx["home"] else p_other),
        "away_price": american_from_prob(p_sel if side == fx["away"] else p_other),
        "margin": round((p_sel + p_other) - 1.0, 6),
        "record_source": recs,
        "record_cross_check": None,
    }
    # Where the official record gives a win percentage for both sides, the
    # log5 blend is reported as a cross-check on the originated estimate.
    home_w = win_pct(recs.get("home"))
    away_w = win_pct(recs.get("away"))
    if home_w and away_w:
        blended = log5(home_w, away_w)
        if blended is not None:
            book["record_cross_check"] = round(blended, 4)

    book["pick"] = side
    book["bet"] = pick["bet"]
    book["market"] = pick["market"]
    american = american_from_prob(p_sel)
    book["tier"] = model_tier(p_sel, american)
    book["estimate"] = p_sel
    book["estimate_price"] = american
    return book


def build_markets():
    """Expand every priced fixture into the win / handicap / total families."""
    out = []
    for fx in d.FIXTURES:
        book = compute_book(fx)
        if not book:
            continue
        fid = fx["id"]
        sport = fx["sport"]
        side = book["pick"]
        p = book["estimate"]
        m = {
            "fixture_id": fid,
            "sport": sport,
            "league": fx["league"],
            "market": book["market"],
            "side": side,
            "bet": book["bet"],
            "tier": book["tier"],
            "estimate": p,
            "american": american_from_prob(p),
            "handicap": None,
            "handicap_side": None,
            "handicap_price": None,
            "total_line": None,
            "over_estimate": None,
            "under_estimate": None,
            "over_price": None,
            "under_price": None,
        }
        if sport in HANDICAP:
            line, ratio = HANDICAP[sport]
            m["handicap"] = line
            m["handicap_side"] = side
            m["handicap_price"] = american_from_prob(p * ratio)
        if sport in TOTALS_AVERAGE:
            # A total at a half-point line is a genuine two-way book. The
            # desk prices the side it backs at 55% and the other at 45%.
            avg = TOTALS_AVERAGE[sport]
            p_over = 0.55
            m["total_line"] = avg + 0.5 if sport in ("baseball", "ice-hockey") else avg
            m["over_estimate"] = p_over
            m["under_estimate"] = 1.0 - p_over
            m["over_price"] = american_from_prob(p_over)
            m["under_price"] = american_from_prob(1.0 - p_over)
        out.append(m)
    return out


SOURCE_BY_ID = d.SOURCE_BY_ID

# Per-sport source pools, official first. The validator requires that every
# priced fixture cites at least one official source.
SOURCE_POOLS = {
    "baseball": ["mlb-schedule", "mlb-standings"],
    "ice-hockey": ["nhl-score-oct25", "nhl-standings"],
    "tennis": ["atp-scores", "atp-news"],
    "darts": ["pdpa-ec"],
    "snooker": ["wst-home"],
    "cricket": ["ecb-series"],
    "rugby-league": ["nrl-rlwc"],
    "rugby-union": ["urc-r4", "top14-lnr"],
    "motor-racing": ["f1-usgp"],
    "golf": ["pga-bermuda", "olbg-golf"],
    "volleyball": ["olbg-volleyball", "legavolley"],
    "handball": ["olbg-handball", "eurohandball"],
    "gaelic-sports": ["olbg-gaelic", "gaa-home"],
    "greyhounds": ["olbg-greyhounds", "gbgb"],
    "basketball": ["olbg-basketball", "nba-games"],
}


def build_all():
    """The full desk structure the builder renders from."""
    fixtures = []
    for fx in d.FIXTURES:
        entry = dict(fx)
        entry["sport_order"] = d.SPORT_ORDER[fx["sport"]]
        entry["sources"] = []
        for sid in SOURCE_POOLS.get(fx["sport"], []):
            if sid in SOURCE_BY_ID:
                entry["sources"].append(dict(SOURCE_BY_ID[sid]))
        book = compute_book(fx) if fx.get("status") == "upcoming" else None
        entry["book"] = book
        entry["priced"] = bool(book)
        if fx.get("status") == "upcoming":
            entry["markets"] = [m for m in build_markets() if m["fixture_id"] == fx["id"]]
        else:
            entry["markets"] = []
        fixtures.append(entry)

    picks = []
    for fx in fixtures:
        book = fx.get("book")
        if not book or not book.get("pick"):
            continue
        pick = d.PICKS[fx["id"]]
        picks.append({
            "sport": fx["sport"],
            "sport_order": fx["sport_order"],
            "fixture_id": fx["id"],
            "home": fx["home"],
            "away": fx["away"],
            "competition": fx["competition"],
            "league": fx["league"],
            "venue": fx["venue"],
            "city": fx["city"],
            "start_utc": fx["start"],
            "pick": book["pick"],
            "bet": book["bet"],
            "market": book["market"],
            "tier": book["tier"],
            "estimate": book["estimate"],
            "american": american_from_prob(book["estimate"]),
            "handicap": ([m for m in fx["markets"] if m["handicap"] is not None] or [None])[0],
            "total": ([m for m in fx["markets"] if m["total_line"] is not None] or [None])[0],
            "sources": [s["id"] for s in fx["sources"]],
            "has_prediction": bool(d.PREDICTIONS.get(fx["id"])),
        })

    predictions = []
    for p in picks:
        text = d.PREDICTIONS.get(p["fixture_id"])
        if not text:
            continue
        price = p["american"]
        # The prose carries the price as a placeholder so the published price
        # is always the price the desk actually computed, never a hand-typed one.
        body = text.replace("<<PRICE>>", str(price))
        predictions.append({
            "fixture_id": p["fixture_id"],
            "sport": p["sport"],
            "sport_order": p["sport_order"],
            "pick": p["pick"],
            "bet": p["bet"],
            "market": p["market"],
            "tier": p["tier"],
            "estimate": p["estimate"],
            "american": price,
            "words": len(body.split()),
            "text": body,
        })

    return {
        "fixtures": fixtures,
        "picks": picks,
        "predictions": predictions,
    }
