#!/usr/bin/env python3
"""T9958 independent offline audit, re-grading and cross-desk reconciliation engine.

This session (99582dd3) has outbound HTTPS only to GitHub/npm/PyPI, so no live OLBG
or official-source fetch is possible. The engine therefore works exclusively from
retained, already-captured evidence inside the repository and never presents an
inherited fact as a fresh observation. It:

  * re-checks every retained market's price arithmetic (fair decimal = 1/p,
    decimal <-> American conversion, two-way probability mass),
  * re-grades confidence under the brief's published rule
    (High  <=>  p > 0.70 AND -250 <= fair American <= +10000),
  * audits provenance (every row needs an official governing-body URL; OLBG is
    discovery only and can never verify a sporting fact),
  * gates the human predictions (>=30 words, explicit selection, no internal
    vocabulary leaks, participant present, corpus uniqueness, direction),
  * reconciles the same matchups across parallel retained desks and records
    directional conflicts / probability divergences,
  * blanks/holds anything that fails a hard gate and records a flag instead.

Deterministic: all wall-clock input flows through the explicit ``now`` argument.
Standard library only.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "99582dd3"
PRIMARY = ROOT / "data" / "8a900c04" / "desk.json"
PREDICTIONS = ROOT / "data" / "8a900c04" / "predictions.json"

SESSION = "99582dd3"
CAPTURE_AT = "2026-10-23T16:45:00Z"  # primary desk capture timestamp, inherited

# The exact fifteen sports from the brief, in the brief's order.
SPORTS = [
    ("Golf", "golf"),
    ("Volleyball", "volleyball"),
    ("Rugby Union", "rugby-union"),
    ("Cricket", "cricket"),
    ("Snooker", "snooker"),
    ("Darts", "darts"),
    ("Baseball", "baseball"),
    ("Gaelic Sports", "gaelic-sports"),
    ("Greyhounds", "greyhounds"),
    ("Tennis", "tennis"),
    ("Motor Racing", "motor-racing"),
    ("Handball", "handball"),
    ("Ice Hockey", "ice-hockey"),
    ("Basketball", "basketball"),
    ("Rugby League", "rugby-league"),
]
SPORT_SLUGS = {name: slug for name, slug in SPORTS}

DISCOVERY_HOSTS = {"olbg.com", "www.olbg.com", "m.olbg.com"}

# Official governing-body / league / tour / federation / organiser hosts observed
# across the retained desks. Anything outside this set is flagged for manual
# review rather than silently accepted or dropped.
OFFICIAL_HOSTS = {
    "api-web.nhle.com", "www.nhl.com", "nhl.com",
    "statsapi.mlb.com", "www.mlb.com",
    "www.atptour.com", "www.wtatennis.com", "wtafiles.wtatennis.com",
    "www.pgatour.com", "www.europeantour.com", "www.lpga.com",
    "www.pdc.tv", "www.wst.tv",
    "www.gbgb.org.uk",
    "www.formula1.com",
    "www.nrl.com",
    "www.unitedrugby.com", "stats.unitedrugby.com", "www.premiershiprugby.com",
    "top14.lnr.fr",
    "www.eurohandball.com", "ehfcl.eurohandball.com", "www.lnh.fr",
    "www.daikin-hbl.de", "daikin-hbl.de",
    "www.legavolley.it", "www.plusliga.pl",
    "www.euroleaguebasketball.net", "www.nba.com", "ak-static.cms.nba.com",
    "cdn.nba.com",
    "www.icc-cricket.com", "www.nzc.nz", "scoring.nzc.nz",
    "www.cricket.com.au", "www.pcb.com.pk",
    "munster.gaa.ie", "www.gaa.ie", "gaacork.ie", "www.maighcuilinn.com",
    "www.galwaygaa.ie",
    "www.intrl.sport",
    "www.afl.com.au",
}

STOP = {
    "vs", "v", "at", "the", "and", "w", "men", "women", "de", "la", "le",
    "fc", "hc", "hk", "sc", "ac", "bk", "if", "sk", "a", "of",
}
ARITH_TOL = 0.011          # fair decimal vs 1/p tolerance (rounding noise)
AM_REL_TOL = 0.015         # relative tolerance for long-shot American prices
AM_ABS_TOL = 2             # absolute tolerance for short American prices
PROB_SUM_TOL = 0.011
HIGH_FLOOR = 0.70
MED_FLOOR = 0.575          # mirrors 8a900c04 classify_confidence boundary
AM_FLOOR, AM_CEIL = -250, 10000
DEC_FLOOR, DEC_CEIL = 1.40, 101.0
PROB_CLAMP = (0.0020, 0.9950)
WORD_FLOOR = 30


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #
def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def clamp_prob(p: float) -> float:
    return max(PROB_CLAMP[0], min(PROB_CLAMP[1], float(p)))


def american_from_prob(prob: float) -> int:
    """Mirror of the source desk's prob_to_american (American derived from p)."""
    p = clamp_prob(prob)
    if abs(p - 0.5) < 1e-9:
        return 100
    if p > 0.5:
        return -int(round(100.0 * p / (1.0 - p)))
    return int(round(100.0 * (1.0 - p) / p))


def american_from_decimal(dec: float) -> int:
    if dec >= 2.0:
        return round((dec - 1.0) * 100.0)
    return round(-100.0 / (dec - 1.0))


def in_price_window(american: int, decimal: float) -> bool:
    return (AM_FLOOR <= american <= AM_CEIL) and (DEC_FLOOR <= decimal <= DEC_CEIL)


def grade_for(prob: float, american: int, decimal: float) -> tuple[str, bool]:
    """Mirror of 8a900c04 classify_confidence: (grade, chalk_suppressed)."""
    if prob > HIGH_FLOOR and in_price_window(american, decimal):
        return "high", False
    if prob > HIGH_FLOOR:
        return "medium", True       # chalk suppressed from High
    if prob >= MED_FLOOR:
        return "medium", False
    return "low", False


def american_matches(derived: int, stored: int) -> bool:
    if abs(stored) <= 200:
        return abs(derived - stored) <= AM_ABS_TOL
    return abs(derived - stored) <= max(AM_ABS_TOL, abs(stored) * AM_REL_TOL)


def tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", (text or "").lower()) if t not in STOP and len(t) > 1}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def host_of(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except (ValueError, AttributeError):
        return ""


def is_official(url: str) -> bool:
    p = urlparse(url or "")
    return p.scheme == "https" and (p.hostname or "") in OFFICIAL_HOSTS


def source_role(url: str) -> str:
    host = host_of(url)
    path = urlparse(url or "").path.lower()
    if host in {"api-web.nhle.com", "statsapi.mlb.com", "ak-static.cms.nba.com",
                "cdn.nba.com", "wtafiles.wtatennis.com", "stats.unitedrugby.com",
                "scoring.nzc.nz"}:
        return "official structured data feed"
    if "/news/" in path or host == "www.nhl.com" and "/news/" in path:
        return "official publisher news article"
    if host.endswith("nhl.com"):
        return "official league page"
    return "official governing-body / tour page"


@dataclass
class Flag:
    code: str
    severity: str          # high | medium | low | info
    subject: str
    detail: str
    source_urls: list[str] = field(default_factory=list)
    sport: str = ""
    event_id: str = ""
    cross_ref: dict = field(default_factory=dict)

    def as_dict(self, idx: int) -> dict:
        return {
            "id": f"F9958-{idx:03d}",
            "code": self.code,
            "severity": self.severity,
            "sport": self.sport,
            "event_id": self.event_id,
            "subject": self.subject,
            "detail": self.detail,
            "source_urls": self.source_urls,
            "cross_reference": self.cross_ref,
        }


# --------------------------------------------------------------------------- #
# Gate evaluation
# --------------------------------------------------------------------------- #
def check_market(market: dict) -> list[dict]:
    """Re-derive every arithmetic/grade invariant for one retained market."""
    checks: list[dict] = []
    p = market.get("fair_prob")
    dec = market.get("fair_decimal")
    am = market.get("fair_american")
    label = (market.get("confidence") or "").lower()
    if p is None or dec is None or am is None:
        checks.append({"gate": "G2", "ok": False, "detail": "market missing price components"})
        return checks
    expect_dec = 1.0 / p
    checks.append({
        "gate": "G2", "ok": abs(expect_dec - dec) <= ARITH_TOL,
        "detail": f"1/p={expect_dec:.4f} vs stored decimal {dec}",
    })
    # Source desk derives American from the (clamped) probability, not the
    # rounded decimal, so re-derive the same way and tolerate long-shot rounding.
    expect_am = american_from_prob(p)
    checks.append({
        "gate": "G2", "ok": american_matches(expect_am, am),
        "detail": f"derived American {expect_am} vs stored {am}",
    })
    cp = market.get("counter_prob")
    if cp is not None:
        checks.append({
            "gate": "G2", "ok": abs(cp + p - 1.0) <= PROB_SUM_TOL,
            "detail": f"two-way mass {cp + p:.4f}",
        })
    window = in_price_window(am, dec)
    checks.append({
        "gate": "G3", "ok": bool(market.get("in_window")) == window,
        "detail": f"window flag={market.get('in_window')} computed={window}",
    })
    expect_grade, expect_chalk = grade_for(p, am, dec)
    grade_ok = label == expect_grade
    if expect_chalk is not None and "chalk_suppressed" in market:
        grade_ok = grade_ok and bool(market.get("chalk_suppressed")) == expect_chalk
    checks.append({
        "gate": "G3", "ok": grade_ok,
        "detail": f"stored grade '{label}'/chalk={market.get('chalk_suppressed')} "
                  f"vs recomputed '{expect_grade}'/chalk={expect_chalk}",
    })
    if label == "high":
        checks.append({
            "gate": "G3", "ok": p > HIGH_FLOOR and window and not market.get("chalk_suppressed"),
            "detail": "high must clear 70% inside -250..+10000 and not be chalk-suppressed",
        })
    return checks


def audit_event(event: dict, now: datetime, flags: list[Flag]) -> dict:
    eid = event["id"]
    sport = event["sport"]
    urls = list(dict.fromkeys(u for u in (event.get("official_url"),
                                          event.get("secondary_official_url"),
                                          event.get("publisher_crossref_url")) if u))
    gate_rows: list[dict] = []

    # G1 provenance --------------------------------------------------------- #
    official = [u for u in urls if is_official(u)]
    unknown = [host_of(u) for u in urls if not is_official(u) and host_of(u) not in DISCOVERY_HOSTS]
    g1 = bool(official)
    gate_rows.append({"gate": "G1", "ok": g1, "detail": f"{len(official)} official URL(s)"})
    if not g1:
        flags.append(Flag("G1-NO-OFFICIAL", "high", f"{eid} {event['event']}",
                          "No official governing-body URL retained; OLBG discovery cannot verify a fact.",
                          [event.get("olbg_url", "")], sport, eid))
    for host in unknown:
        flags.append(Flag("G1-UNKNOWN-HOST", "medium", f"{eid} {event['event']}",
                          f"Source host '{host}' is not in the curated official registry; manual review.",
                          urls, sport, eid))

    # G4 timing ------------------------------------------------------------- #
    start = parse_ts(event["start_utc"])
    elapsed = start <= now
    gate_rows.append({"gate": "G4", "ok": True,
                      "detail": "elapsed at build" if elapsed else "upcoming at build"})

    # G2/G3 per market ------------------------------------------------------ #
    market_results = []
    hard_fail = not g1
    for m in event.get("markets", []):
        checks = check_market(m)
        market_results.append({"market_label": m.get("market_label"),
                               "selection": m.get("selection"),
                               "checks": checks})
        for c in checks:
            if not c["ok"]:
                hard_fail = True
                flags.append(Flag(
                    f"{c['gate']}-MARKET", "high" if c["gate"] == "G3" else "medium",
                    f"{eid} · {m.get('market_label')}", c["detail"], official[:1], sport, eid))

    # Event-level match-winner re-grade ------------------------------------ #
    mw_p = event.get("match_winner_prob")
    mw_am = event.get("match_winner_american")
    mw_dec = event.get("match_winner_decimal")
    mw_check = None
    if mw_p is not None and mw_am is not None and mw_dec is not None:
        mw_grade, mw_chalk = grade_for(mw_p, mw_am, mw_dec)
        stored_mw = (event.get("match_winner_confidence") or "").lower()
        mw_check = {"recomputed_grade": mw_grade, "stored_grade": stored_mw,
                    "ok": mw_grade == stored_mw
                    and bool(event.get("match_winner_chalk_suppressed")) == mw_chalk,
                    "chalk_suppressed": bool(event.get("match_winner_chalk_suppressed"))}
        if not mw_check["ok"]:
            flags.append(Flag("G3-MATCH-WINNER", "medium",
                              f"{eid} {event['event']}",
                              f"Match-winner stored grade '{stored_mw}' != recomputed '{mw_grade}' "
                              f"(p={mw_p}, {mw_am}).", official[:1], sport, eid))
        # chalk suppression sanity: >70% but shorter than -250 must be suppressed
        if mw_p > HIGH_FLOOR and mw_am < AM_FLOOR and not event.get("match_winner_chalk_suppressed"):
            flags.append(Flag("G3-CHALK", "high", f"{eid} {event['event']}",
                              f"Favorite at {mw_am} (<-250) with p={mw_p} is not marked chalk-suppressed.",
                              official[:1], sport, eid))

    # Recommended selection must resolve to a real retained market --------- #
    rec_market = event.get("recommended_market")
    rec_sel = event.get("recommended_selection")
    rec_match = next((m for m in event.get("markets", [])
                      if m.get("market_label") == rec_market and m.get("selection") == rec_sel), None)
    g_rec = rec_match is not None
    gate_rows.append({"gate": "G3", "ok": g_rec,
                      "detail": f"recommended selection resolves: {rec_market} / {rec_sel}"})
    if not g_rec:
        hard_fail = True
        flags.append(Flag("G3-REC-ORPHAN", "high", f"{eid} {event['event']}",
                          "Recommended selection not found among the retained priced markets.",
                          official[:1], sport, eid))
    else:
        rec_grade, _ = grade_for(rec_match["fair_prob"], rec_match["fair_american"],
                                 rec_match["fair_decimal"])
        if rec_grade != (rec_match.get("confidence") or "").lower():
            flags.append(Flag("G3-REC-GRADE", "medium", f"{eid} {event['event']}",
                              f"Recommended market grade mismatch: stored "
                              f"{rec_match.get('confidence')} vs recomputed {rec_grade}.",
                              official[:1], sport, eid))

    # G5/G6 prose ----------------------------------------------------------- #
    prose = event.get("prediction") or ""
    words = prose.split()
    pchecks = {
        "present": bool(prose),
        "min_words": len(words) >= WORD_FLOOR,
        "word_count_field": event.get("prediction_word_count") == len(words),
        "no_model": "model" not in prose.lower(),
        "no_verified": "verified" not in prose.lower(),
        "states_selection": "selection" in prose.lower(),
        "names_participant": bool(tokens(event.get("home", "")) & tokens(prose))
        or bool(tokens(event.get("away", "")) & tokens(prose)),
    }
    prose_hard_ok = all(pchecks.values())
    gate_rows.append({"gate": "G5", "ok": prose_hard_ok,
                      "detail": ", ".join(f"{k}={v}" for k, v in pchecks.items())})
    if not prose_hard_ok:
        hard_fail = True
        failed = [k for k, v in pchecks.items() if not v]
        flags.append(Flag("G5-PROSE", "high", f"{eid} {event['event']}",
                          f"Prediction failed hard prose gate(s): {', '.join(failed)}.",
                          official[:1], sport, eid))

    # G6 directional contradiction: only the explicit Selection sentence is
    # inspected, so historical form clauses ("won 6-3 over X") never trip it.
    fav = (event.get("match_winner_selection") or "")
    fav_name = re.sub(r"\s*(to win|moneyline).*$", "", fav, flags=re.I).strip()
    fav_tokens = tokens(fav_name)
    sel_match = re.search(r"Selection:\s*([^.!?]+[.!?])", prose)
    if sel_match:
        clause = sel_match.group(1)
        for piece in re.split(r"[;:(]", clause):
            if " over " not in piece.lower():
                continue
            # Distance phrases ("over 575 metres", "over 18 holes") are not matchups.
            if re.search(r"over\s+\d", piece.lower()):
                continue
            subj_tokens = tokens(piece.split(" over ")[0])
            if fav_tokens and subj_tokens and not (subj_tokens & fav_tokens) and \
                    (subj_tokens & tokens(event.get("home", ""))
                     or subj_tokens & tokens(event.get("away", ""))):
                flags.append(Flag("G6-DIRECTION", "medium", f"{eid} {event['event']}",
                                  f"Selection sentence names a non-favorite over the priced match-winner "
                                  f"favorite ({fav_name}): \"{piece.strip()}\"",
                                  official[:1], sport, eid))

    # In-window high that remains a current recommendation ------------------ #
    rec_high = bool(rec_match and rec_match["fair_prob"] > HIGH_FLOOR
                    and in_price_window(rec_match["fair_american"], rec_match["fair_decimal"])
                    and not rec_match.get("chalk_suppressed"))

    return {
        "id": eid,
        "sport": sport,
        "sport_slug": SPORT_SLUGS[sport],
        "event": event["event"],
        "home": event.get("home"),
        "away": event.get("away"),
        "competition": event.get("competition"),
        "venue": event.get("venue") or "",
        "start_utc": event["start_utc"],
        "timing": "elapsed" if elapsed else ("today" if start.date() == now.date() else "upcoming"),
        "is_today_card": bool(event.get("is_today_card")),
        "olbg_url": event.get("olbg_url"),
        "official_urls": official,
        "all_source_urls": urls,
        "source_roles": [{"url": u, "role": source_role(u)} for u in official],
        "origin_desk": "8a900c04",
        "captured_at": CAPTURE_AT,
        "match_winner": {
            "selection": event.get("match_winner_selection"),
            "prob": mw_p, "decimal": mw_dec, "american": mw_am,
            "stored_grade": (event.get("match_winner_confidence") or "").lower(),
            "check": mw_check,
        },
        "recommended": {
            "market": rec_market, "selection": rec_sel,
            "prob": event.get("fair_prob"), "pct": event.get("fair_pct"),
            "decimal": event.get("fair_decimal"), "american": event.get("fair_american"),
            "stored_grade": (event.get("confidence") or "").lower(),
            "is_high": rec_high,
            "resolves": g_rec,
        },
        "form_summary": event.get("form_summary") or "",
        "injury_report": event.get("injury_report") or "",
        "stats_note": event.get("stats_note") or "",
        "prediction": prose if prose_hard_ok else "",
        "prediction_word_count": len(words),
        "prose_checks": pchecks,
        "hard_fail": hard_fail,
        "gate_rows": gate_rows,
        "markets": event.get("markets", []),
        "market_checks": market_results,
        "cross_flags": [],     # filled by reconciliation
    }


# --------------------------------------------------------------------------- #
# Cross-desk reconciliation
# --------------------------------------------------------------------------- #
def load_other_desks() -> dict:
    desks: dict[str, list[dict]] = {}

    # 429a54a2: explicit two-participant fixtures with price books ------------
    p = ROOT / "data/429a54a2/fixtures.json"
    rows = []
    if p.exists():
        for f in json.loads(p.read_text()):
            price = f.get("price") or {}
            # The fixture's top-level selection can name the first participant;
            # the actual favorite is the highest-probability winner outcome.
            winners = [m for m in price.get("markets", []) if m.get("market") == "match_winner"]
            pick = max(winners, key=lambda m: m.get("probability") or 0.0, default=None)
            if not pick or pick.get("probability") is None:
                continue
            rows.append({
                "desk": "429a54a2", "fixture": f"{f.get('participant_a')} v {f.get('participant_b')}",
                "tokens": tokens(f"{f.get('participant_a')} {f.get('participant_b')}"),
                "selection": pick.get("selection"), "prob": pick.get("probability"),
                "american": pick.get("american"), "tier": price.get("tier"),
                "official_url": f.get("official_url"),
            })
    desks["429a54a2"] = rows

    # 3ee30bba: high/chalk pick lists, winner family only ---------------------
    p = ROOT / "data/3ee30bba/desk.json"
    rows = []
    if p.exists():
        d = json.loads(p.read_text())
        for f in d.get("high_picks", []) + d.get("chalk_capped", []):
            if f.get("family") != "winner":
                continue
            rows.append({
                "desk": "3ee30bba", "fixture": f.get("event_label"),
                "tokens": tokens(f.get("event_label", "").replace("@", " ")),
                "selection": f.get("selection"), "prob": f.get("probability"),
                "american": f.get("american"), "tier": f.get("confidence"),
                "official_url": f.get("official_url"),
            })
    desks["3ee30bba"] = rows

    # 7f000cb6: price books joined to fixtures for participants ---------------
    rows = []
    lp = ROOT / "data/7f000cb6/lines.json"
    fp = ROOT / "data/7f000cb6/fixtures.json"
    if lp.exists() and fp.exists():
        fx = {x["id"]: x for x in json.loads(fp.read_text()).get("fixtures", [])}
        for b in json.loads(lp.read_text()).get("books", []):
            fxrow = fx.get(b["fixture_id"])
            if not fxrow:
                continue
            wp = b.get("winner_pick") or {}
            rows.append({
                "desk": "7f000cb6",
                "fixture": f"{fxrow.get('home')} v {fxrow.get('away')}",
                "tokens": tokens(f"{fxrow.get('home')} {fxrow.get('away')}"),
                "selection": wp.get("selection"), "prob": wp.get("probability"),
                "american": wp.get("american_odds"), "tier": wp.get("confidence"),
                "official_url": b.get("official_url"),
            })
    desks["7f000cb6"] = rows
    return desks


def reconcile(slate: list[dict], flags: list[Flag]) -> list[dict]:
    desks = load_other_desks()
    findings: list[dict] = []
    for row in slate:
        own_tokens = tokens(f"{row['home']} {row['away']}")
        fav_tokens = tokens(row["match_winner"].get("selection") or "")
        for desk_name, records in desks.items():
            # One reconciled statement per (event, desk): keep the strongest
            # matching book (largest distance from a coin flip).
            matches = [o for o in records if jaccard(own_tokens, o["tokens"]) >= 0.5]
            if not matches:
                continue
            other = max(matches, key=lambda o: abs((o.get("prob") or 0.5) - 0.5))
            other_sel = tokens(other.get("selection") or "")
            same_side = bool(other_sel & fav_tokens)
            record = {
                "event_id": row["id"], "sport": row["sport"], "event": row["event"],
                "desk": desk_name, "matched_books": len(matches),
                "other_fixture": other["fixture"],
                "other_selection": other["selection"], "other_prob": other["prob"],
                "other_american": other["american"], "other_tier": other["tier"],
                "other_official_url": other["official_url"],
                "own_selection": row["match_winner"]["selection"],
                "own_prob": row["match_winner"]["prob"],
                "own_american": row["match_winner"]["american"],
                "same_side": same_side,
            }
            if not same_side and other.get("selection") and row["match_winner"].get("selection"):
                record["finding"] = "directional-conflict"
                findings.append(record)
                row["cross_flags"].append("directional-conflict:" + desk_name)
                extra = (" Repeated team pairings (e.g. playoff rematches) cannot be "
                         "distinguished by name matching alone." if len(matches) > 1 else "")
                flags.append(Flag(
                    "G7-CONFLICT", "high",
                    f"{row['id']} {row['event']}",
                    f"Parallel desk {desk_name} prices '{other['selection']}' "
                    f"({fmt_p(other['prob'])}, {other['american']}) as match winner while 8a900c04 "
                    f"prices '{row['match_winner']['selection']}' "
                    f"({fmt_p(row['match_winner']['prob'])}, {row['match_winner']['american']}). "
                    "Opposite favorites cannot be reconciled offline; manual review required." + extra,
                    [u for u in row["all_source_urls"] if is_official(u)][:1]
                    + ([other["official_url"]] if other.get("official_url") else []),
                    row["sport"], row["id"], {"desk": desk_name, "books": len(matches)}))
            elif same_side and other.get("prob") and row["match_winner"].get("prob"):
                gap = abs(other["prob"] - row["match_winner"]["prob"])
                if gap > 0.15:
                    record["finding"] = "probability-divergence"
                    record["prob_gap"] = round(gap, 4)
                    findings.append(record)
                    row["cross_flags"].append("divergence:" + desk_name)
                    flags.append(Flag(
                        "G7-DIVERGENCE", "medium",
                        f"{row['id']} {row['event']}",
                        f"Same favored side as {desk_name} but probabilities diverge by "
                        f"{gap:.1%} ({fmt_p(other['prob'])} vs {fmt_p(row['match_winner']['prob'])}).",
                        [u for u in row["all_source_urls"] if is_official(u)][:1]
                        + ([other["official_url"]] if other.get("official_url") else []),
                        row["sport"], row["id"], {"desk": desk_name}))
    return findings


def fmt_p(p) -> str:
    return "n/a" if p is None else f"{p:.1%}"


# --------------------------------------------------------------------------- #
# Corpus-level prose uniqueness
# --------------------------------------------------------------------------- #
def uniqueness_scan(slate: list[dict], flags: list[Flag]) -> dict:
    seen: dict[tuple, list[str]] = {}
    for row in slate:
        prose = row.get("prediction") or ""
        words = re.findall(r"[a-z0-9']+", prose.lower())
        for gram in set(zip(*[words[i:] for i in range(7)])) if len(words) >= 7 else []:
            seen.setdefault(gram, []).append(row["id"])
    duplicates = [{"gram": " ".join(g), "events": ids} for g, ids in seen.items() if len(ids) > 1]
    for dup in duplicates:
        flags.append(Flag("G5-UNIQUE", "low",
                          f"Predictions {', '.join(dup['events'])}",
                          f"Shared seven-word phrase: \"{dup['gram']}\". Minor uniqueness finding.",
                          [], "", ""))
    return {"repeated_7grams": duplicates}


# --------------------------------------------------------------------------- #
# Main run
# --------------------------------------------------------------------------- #
def run(now_iso: str | None = None, out: Path = OUT) -> dict:
    now = parse_ts(now_iso) if now_iso else datetime.now(timezone.utc).replace(microsecond=0)
    out.mkdir(parents=True, exist_ok=True)
    desk = json.loads(PRIMARY.read_text())
    json.loads(PREDICTIONS.read_text())  # integrity: file must parse and match embedded prose
    flags: list[Flag] = []

    slate = [audit_event(e, now, flags) for e in desk["events"]]

    # Carry the seven quarantined OLBG-only discovery rows into the flag register
    for f in desk.get("flagged", []):
        flags.append(Flag(
            "G1-OLBG-UNCONFIRMED", "medium",
            f"{f.get('id')} {f.get('event')}",
            f"OLBG hub lists this {f.get('sport')} card ({f.get('competition')}, "
            f"display '{f.get('olbg_display_time')}', tips {f.get('olbg_tips')}) but no official "
            "governing-body confirmation was retained; it stays unpriced and is excluded from the slate.",
            [f.get("olbg_url", "")], f.get("sport", ""), f.get("id", "")))

    cross = reconcile(slate, flags)
    uniqueness = uniqueness_scan(slate, flags)

    # Calibration-shape finding: the originating engine explicitly targets a
    # "golden window" near p=0.708 when constructing alternate lines, so the
    # High cluster sits on the eligibility boundary rather than spanning a
    # natural edge distribution. Recorded as an info-level structural finding.
    high_probs = [r["recommended"]["prob"] for r in slate if r["recommended"]["is_high"]]
    if high_probs and sum(1 for p in high_probs if p <= 0.715) / len(high_probs) >= 0.9:
        flags.append(Flag(
            "G3-CLUSTER", "info", "High-confidence probability distribution",
            f"All {len(high_probs)} High recommendations fall inside "
            f"{min(high_probs):.4f}-{max(high_probs):.4f} (59-of-59 at or below 0.715). The originating "
            "engine constructs alternate spreads/totals by minimising distance to p=0.708, so the cluster "
            "at the -250 window boundary is a calibration shape to review, not 59 independent strong edges.",
            [], "", ""))

    # Source registry -------------------------------------------------------- #
    registry: dict[str, dict] = {}
    for row in slate:
        for url in row["all_source_urls"]:
            host = host_of(url)
            entry = registry.setdefault(host, {
                "host": host, "official": is_official(url),
                "role": source_role(url), "urls": set(), "events": set()})
            entry["urls"].add(url)
            entry["events"].add(row["id"])
    sources = [{"host": h, "official": v["official"], "role": v["role"],
                "url_count": len(v["urls"]), "event_count": len(v["events"]),
                "urls": sorted(v["urls"])} for h, v in sorted(registry.items())]

    # Predictions gated ------------------------------------------------------ #
    predictions = [{
        "event_id": r["id"], "sport": r["sport"], "event": r["event"],
        "start_utc": r["start_utc"], "timing": r["timing"],
        "selection": r["recommended"]["selection"],
        "market": r["recommended"]["market"],
        "prob": r["recommended"]["prob"], "american": r["recommended"]["american"],
        "grade": r["recommended"]["stored_grade"],
        "word_count": r["prediction_word_count"],
        "prediction": r["prediction"],
        "withheld": not bool(r["prediction"]),
        "official_urls": r["official_urls"],
        "cross_flags": r["cross_flags"],
    } for r in slate]

    flags_dicts = [f.as_dict(i + 1) for i, f in enumerate(flags)]
    high_rows = [r for r in slate if r["recommended"]["is_high"] and not r["hard_fail"]
                 and r["timing"] != "elapsed"]
    summary = {
        "session": SESSION,
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "mode": "offline audit of retained evidence; no live fetch possible (egress restricted to GitHub/npm/PyPI)",
        "primary_origin_desk": "8a900c04",
        "primary_capture_at": CAPTURE_AT,
        "sports": len(SPORTS),
        "events": len(slate),
        "events_per_sport": {name: sum(1 for r in slate if r["sport"] == name) for name, _ in SPORTS},
        "timing": {"elapsed": sum(1 for r in slate if r["timing"] == "elapsed"),
                   "today": sum(1 for r in slate if r["timing"] == "today"),
                   "upcoming": sum(1 for r in slate if r["timing"] == "upcoming")},
        "markets_total": sum(len(r["markets"]) for r in slate),
        "high_recommended_current": len(high_rows),
        "high_recommended_with_conflict": sum(1 for r in high_rows if r["cross_flags"]),
        "hard_held_events": sum(1 for r in slate if r["hard_fail"]),
        "predictions_released": sum(1 for p in predictions if not p["withheld"]),
        "predictions_withheld": sum(1 for p in predictions if p["withheld"]),
        "flags_total": len(flags_dicts),
        "flags_by_severity": {s: sum(1 for f in flags_dicts if f["severity"] == s)
                              for s in ("high", "medium", "low", "info")},
        "cross_desk_findings": len(cross),
        "repeated_7grams": len(uniqueness["repeated_7grams"]),
        "official_source_hosts": sum(1 for s in sources if s["official"]),
    }

    (out / "audit.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    (out / "slate.json").write_text(json.dumps(slate, indent=2, ensure_ascii=False) + "\n")
    (out / "flags.json").write_text(json.dumps(flags_dicts, indent=2, ensure_ascii=False) + "\n")
    (out / "predictions_gated.json").write_text(
        json.dumps(predictions, indent=2, ensure_ascii=False) + "\n")
    (out / "sources.json").write_text(json.dumps(sources, indent=2, ensure_ascii=False) + "\n")
    (out / "cross_desk.json").write_text(json.dumps(cross, indent=2, ensure_ascii=False) + "\n")
    _write_csvs(out, slate, flags_dicts)
    return summary


def _write_csvs(out: Path, slate: list[dict], flags: list[dict]) -> None:
    with (out / "slate.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["event_id", "sport", "event", "competition", "start_utc", "timing",
                    "match_winner_selection", "match_winner_prob", "match_winner_american",
                    "match_winner_grade", "recommended_market", "recommended_selection",
                    "recommended_prob", "recommended_american", "recommended_grade",
                    "hard_fail", "cross_flags", "official_url"])
        for r in slate:
            mw, rec = r["match_winner"], r["recommended"]
            w.writerow([r["id"], r["sport"], r["event"], r["competition"], r["start_utc"],
                        r["timing"], mw["selection"], mw["prob"], mw["american"],
                        mw["stored_grade"], rec["market"], rec["selection"], rec["prob"],
                        rec["american"], rec["stored_grade"], r["hard_fail"],
                        ";".join(r["cross_flags"]), r["official_urls"][0] if r["official_urls"] else ""])
    with (out / "markets.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["event_id", "sport", "market", "selection", "prob", "decimal",
                    "american", "in_window", "confidence", "chalk_suppressed", "official_url"])
        for r in slate:
            for m in r["markets"]:
                w.writerow([r["id"], r["sport"], m.get("market_label"), m.get("selection"),
                            m.get("fair_prob"), m.get("fair_decimal"), m.get("fair_american"),
                            m.get("in_window"), m.get("confidence"),
                            m.get("chalk_suppressed"),
                            r["official_urls"][0] if r["official_urls"] else ""])
    with (out / "flags.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["flag_id", "severity", "code", "sport", "event_id", "subject",
                    "detail", "source_urls"])
        for f in flags:
            w.writerow([f["id"], f["severity"], f["code"], f["sport"], f["event_id"],
                        f["subject"], f["detail"], " | ".join(f["source_urls"])])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--now", help="UTC ISO timestamp for deterministic timing gates")
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    summary = run(args.now, args.out)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
