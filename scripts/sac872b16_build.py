"""Build the T65 / ac872b16 desk: data, market origination and confidence tiers.

Run:  python3 -m scripts.sac872b16_build
Outputs data/ac872b16/*.json and ac872b16/*.html
"""
from __future__ import annotations

import json
import math
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from scripts.sac872b16_data import (
    AFLW, CARRIED_PRICED, EUROLEAGUE, EUROLEAGUE_FIXTURES, EURO_ALIASES,
    NHL, NHL_CITY_TO_ABBREV, NHL_FIXTURES, SOURCES,
)
from scripts.sac872b16_prose import PREDICTIONS, SPORT_NOTES

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "ac872b16"
SITE = ROOT / "ac872b16"
AS_OF = datetime(2026, 10, 22, 12, 30, tzinfo=timezone.utc)
NOW_ISO = AS_OF.strftime("%Y-%m-%dT%H:%M:%SZ")

SPORTS = [
    ("tennis", "Tennis", 3), ("basketball", "Basketball", 4), ("golf", "Golf", 5),
    ("cricket", "Cricket", 7), ("snooker", "Snooker", 8), ("rugby-union", "Rugby Union", 9),
    ("rugby-league", "Rugby League", 10), ("baseball", "Baseball", 12), ("ice-hockey", "Ice Hockey", 13),
    ("motor-racing", "Motor Racing", 14), ("darts", "Darts", 15), ("handball", "Handball", 20),
    ("volleyball", "Volleyball", 21), ("aussie-rules", "Aussie Rules", 22), ("esports", "eSports", 23),
    ("gaelic-football", "Gaelic Football", 25), ("greyhounds", "Greyhounds", 28),
]
SPORT_NAME = {s: n for s, n, _ in SPORTS}
CARRIED_PICK_SPORTS = {"baseball"}

MONTHS = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def phi(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def american(fair: float) -> str:
    if fair >= 2:
        return f"+{round((fair - 1) * 100)}"
    return f"{round(-100 / (fair - 1))}"


def price_outcome(selection: str, p: float) -> dict:
    fair = 1.0 / p
    return {
        "selection": selection,
        "probability": round(p, 6),
        "fair_decimal": round(fair, 4),
        "american": american(fair),
        "in_band": 0.70 <= p <= 0.7142857 and 1.40 <= fair <= 1.4286,
    }


def parse_olbg_time(label: str, today: date = date(2026, 10, 22)):
    """OLBG renders US Eastern time without a zone.  The NHL card 'Today 19:07'
    against an official 23:00Z start fixes the offset at UTC-4 (EDT)."""
    s = (label or "").strip()
    m = re.match(r"Today\s+(\d{1,2}):(\d{2})", s)
    if m:
        d = today
    else:
        m = re.match(r"Tomorrow\s+(\d{1,2}):(\d{2})", s)
        if m:
            d = today + timedelta(days=1)
        else:
            m = re.match(r"(\d{1,2})\s+([A-Za-z]{3})\s+(\d{1,2}):(\d{2})", s)
            if not m:
                return None
            mon = MONTHS.get(m.group(2).title())
            if not mon:
                return None
            d = date(today.year, mon, int(m.group(1)))
            if d < today - timedelta(days=60):
                d = date(today.year + 1, mon, int(m.group(1)))
    hh, mm = int(m.group(m.lastindex - 1)), int(m.group(m.lastindex))
    return datetime(d.year, d.month, d.day, hh, mm, tzinfo=timezone.utc) + timedelta(hours=4)


def fmt_line(value: float) -> str:
    if abs(value - round(value)) < 1e-9:
        return f"{value:+.1f}"
    return f"{value:+.1f}"


# ---------------------------------------------------------------------------
# load discovery
# ---------------------------------------------------------------------------
def load_olbg():
    events = []
    for path in sorted((ROOT / "data" / "92af340c" / "harvest").glob("*.json")):
        blob = json.loads(path.read_text())
        for ev in blob.get("events", []):
            start = parse_olbg_time(ev.get("time_label", ""))
            events.append({
                "sport": blob["sport"],
                "event_id": ev.get("event_id"),
                "league": ev.get("league"),
                "match": ev.get("match"),
                "time_label": ev.get("time_label"),
                "start_utc": start.strftime("%Y-%m-%dT%H:%M:%SZ") if start else None,
                "olbg_selection": ev.get("selection"),
                "olbg_market": ev.get("market"),
                "olbg_tips": ev.get("tips"),
                "olbg_pct": ev.get("pct"),
            })
    return events


def load_carried():
    """Future priced rows captured by T63 at 08:31Z."""
    path = ROOT / "data" / "92af340c" / "dataset.json"
    if not path.exists():
        return []
    blob = json.loads(path.read_text())
    rows = []
    for r in blob.get("rows", []):
        if r.get("time_status") != "future" or not r.get("priced") or not r.get("view"):
            continue
        sport = r["fixture"]["sport"]
        if sport not in CARRIED_PRICED:
            continue
        rows.append(r)
    return rows


# ---------------------------------------------------------------------------
# assemble fixtures
# ---------------------------------------------------------------------------
def official_fixtures():
    fixtures, markets = [], {}

    # ---- EuroLeague ----
    for fid, utc, hc, ac in EUROLEAGUE_FIXTURES:
        hn, hg, hw, hl, hpf, hpa, hl10 = EUROLEAGUE[hc]
        an, ag, aw, al, apf, apa, al10 = EUROLEAGUE[ac]
        # average-of-own-offence-and-opponent-defence (canonical method)
        hscore = (hpf / hg + apa / ag) / 2.0
        ascore = (apf / ag + hpa / hg) / 2.0
        m, total = hscore - ascore, hscore + ascore
        markets[fid] = build_team_markets(fid, "basketball", hn, an, m, total, 12.0, 18.0,
                                          "Match winner (includes overtime); handicap and total are full-game research lines.")
        fixtures.append({
            "id": fid, "sport": "basketball", "competition": "EuroLeague", "stage": "Round 7",
            "start_utc": utc, "home": hn, "away": an, "venue": "", "neutral": False,
            "kind": "match", "discovery": "official", "verification": "verified",
            "source_ids": ["euroleague-round7", "euroleague-standings"],
            "source_urls": [SOURCES["euroleague-round7"]["url"], SOURCES["euroleague-standings"]["url"]],
            "inputs": {
                "home": {"label": "2026-27 EuroLeague record", "value": f"{hw}-{hl} in {hg} GP; {hpf} PF / {hpa} PA; L10 {hl10}", "rating": round(hw / hg, 3)},
                "away": {"label": "2026-27 EuroLeague record", "value": f"{aw}-{al} in {ag} GP; {apf} PF / {apa} PA; L10 {al10}", "rating": round(aw / ag, 3)},
            },
            "pricing": {"status": "priced", "model": "score-average normal margin", "mean_margin": round(m, 3),
                        "sigma": 12.0, "mean_total": round(total, 3), "sigma_total": 18.0, "provenance": "fresh"},
            "notes": ["UTC is a deterministic conversion of the officially published CEST tip-off.",
                      "No home-court term is applied."],
            "flags": [],
        })

    # ---- NHL ----
    for fid, utc, h, a, gid, venue in NHL_FIXTURES:
        hn, hg, hw, hl, ho, hgf, hga, hl10, hstr = NHL[h]
        an, ag, aw, al, ao, agf, aga, al10, astr = NHL[a]
        hscore = (hgf / hg + aga / ag) / 2.0
        ascore = (agf / ag + hga / hg) / 2.0
        m, total = hscore - ascore, hscore + ascore
        markets[fid] = build_team_markets(fid, "ice-hockey", hn, an, m, total, 2.0, 2.4,
                                          "Match winner includes overtime and shootout; handicap is a full-game puck line (no ties).")
        fixtures.append({
            "id": fid, "sport": "ice-hockey", "competition": "NHL", "stage": "Regular season",
            "start_utc": utc, "home": hn, "away": an, "venue": venue, "neutral": False,
            "kind": "match", "discovery": "official", "verification": "verified",
            "source_ids": ["nhl-schedule-20261022", "nhl-standings", "nhl-team-summary"],
            "source_urls": [SOURCES["nhl-schedule-20261022"]["url"], SOURCES["nhl-standings"]["url"], SOURCES["nhl-team-summary"]["url"]],
            "inputs": {
                "home": {"label": "2026-27 NHL record and goals", "value": f"{hw}-{hl}-{ho} in {hg} GP; {hgf} GF / {hga} GA; L10 {hl10}; streak {hstr}", "rating": round((2 * hw + ho) / (2 * hg), 3)},
                "away": {"label": "2026-27 NHL record and goals", "value": f"{aw}-{al}-{ao} in {ag} GP; {agf} GF / {aga} GA; L10 {al10}; streak {astr}", "rating": round((2 * aw + ao) / (2 * ag), 3)},
            },
            "pricing": {"status": "priced", "model": "goals-for/against average, normal margin", "mean_margin": round(m, 3),
                        "sigma": 2.0, "mean_total": round(total, 3), "sigma_total": 2.4, "provenance": "fresh"},
            "notes": ["No home-ice term is applied.", "Game id " + gid + " from the official schedule."],
            "flags": [] if venue else ["Venue was not captured on the fetched schedule chunk; left blank."],
        })

    # ---- AFLW ----
    for fid, utc, h, a, venue, hv, hr, av, ar, mm in AFLW:
        markets[fid] = build_team_markets(fid, "aussie-rules", h, a, mm, 74.5, 18.5, 20.0,
                                          "Match winner; points line and total are full-match research lines.")
        fixtures.append({
            "id": fid, "sport": "aussie-rules", "competition": "NAB AFLW Premiership Season", "stage": "Round 11",
            "start_utc": utc, "home": h, "away": a, "venue": venue, "neutral": False,
            "kind": "match", "discovery": "official", "verification": "verified",
            "source_ids": ["aflw-fixture", "aflw-ladder"],
            "source_urls": [SOURCES["aflw-fixture"]["url"], SOURCES["aflw-ladder"]["url"]],
            "inputs": {"home": {"label": "AFLW ladder after Round 10", "value": hv, "rating": hr},
                       "away": {"label": "AFLW ladder after Round 10", "value": av, "rating": ar}},
            "pricing": {"status": "priced", "model": "ladder-derived margin, normal", "mean_margin": mm,
                        "sigma": 18.5, "mean_total": 74.5, "sigma_total": 20.0, "provenance": "official-same-day"},
            "notes": ["Expected margin is the ladder-derived value recorded in data/92af340c/dataset.json.",
                      "The ladder page is client-rendered; a fresh fetch at 12:2xZ returned 'Loading' with no rows."],
            "flags": ["AFLW ladder values are a same-day official read by T63, not re-rendered in this session."],
        })
    return fixtures, markets


def build_team_markets(fid, sport, home, away, m, total, sigma, sigma_total, settlement):
    """Winner, main handicap/total plus the best in-band half-point rung.

    Selection order: favourite lays points, underdog takes points, total.
    Whole-number lines and NHL +/-0.5 lines are never used for a pick.
    """
    def hsel(line):
        return f"{home} {fmt_line(-line)}"

    def asel(line):
        return f"{away} {fmt_line(line)}"

    out = []
    p_home = phi(m / sigma)
    out.append({"key": "winner", "name": "Match Winner", "line": None, "settlement": settlement,
                "outcomes": [price_outcome(home, p_home), price_outcome(away, 1 - p_home)]})

    if sport == "ice-hockey":
        main = 1.5 if m >= 0 else -1.5
    else:
        main = round(m * 2) / 2
    out.append({"key": "handicap", "name": "Handicap", "line": main, "settlement": settlement,
                "outcomes": [price_outcome(hsel(main), 1 - phi((main - m) / sigma)),
                             price_outcome(asel(main), phi((main - m) / sigma))]})
    mt = round(total * 2) / 2
    out.append({"key": "total", "name": "Total", "line": mt, "settlement": settlement,
                "outcomes": [price_outcome(f"Over {mt:g}", 1 - phi((mt - total) / sigma_total)),
                             price_outcome(f"Under {mt:g}", phi((mt - total) / sigma_total))]})

    z = 0.545
    fav_home = m >= 0
    mf = abs(m)
    cap = {"basketball": 12.0, "aussie-rules": 20.0, "ice-hockey": 2.5}[sport]
    cands = []

    def half_points_near(v):
        base = round(v * 2) / 2
        return [base + d for d in (-1.0, -0.5, 0.0, 0.5, 1.0)]

    # 1. favourite lays points
    for L in half_points_near(mf - sigma * z):
        if L < 0.5 or abs(L) > cap or abs(L - round(L)) < 1e-9:
            continue
        if sport == "ice-hockey" and L < 1.5:
            continue
        p = 1 - phi((L - mf) / sigma)
        if 0.70 <= p <= 0.7142857:
            cands.append((0, abs(p - 0.70714), "favourite", L, p))
    # 2. underdog takes points
    for X in half_points_near(mf + sigma * z):
        if X < 0.5 or abs(X) > cap or abs(X - round(X)) < 1e-9:
            continue
        if sport == "ice-hockey" and X < 1.5:
            continue
        p = phi((X - mf) / sigma)
        if 0.70 <= p <= 0.7142857:
            cands.append((1, abs(p - 0.70714), "cushion", X, p))
    # 3. totals
    for sign, side in ((1, "under"), (-1, "over")):
        for T in half_points_near(total + sign * sigma_total * z):
            if T < 0.5 or abs(T - round(T)) < 1e-9:
                continue
            p = phi((T - total) / sigma_total) if side == "under" else 1 - phi((T - total) / sigma_total)
            if 0.70 <= p <= 0.7142857:
                cands.append((2, abs(p - 0.70714), side, T, p))

    cands.sort()
    if cands:
        _, _, cls, mag, p = cands[0]
        if cls in ("favourite", "cushion"):
            side_home = fav_home if cls == "favourite" else not fav_home
            line_home = mag if fav_home else -mag
            sel = hsel(line_home) if side_home else asel(line_home)
            out.append({"key": "handicap_alt", "name": "Handicap (selected rung)", "line": line_home,
                        "settlement": settlement,
                        "outcomes": [price_outcome(hsel(line_home), 1 - phi((line_home - m) / sigma)),
                                     price_outcome(asel(line_home), phi((line_home - m) / sigma))]})
            pick_line = line_home
        else:
            sel = f"{'Under' if cls == 'under' else 'Over'} {mag:g}"
            out.append({"key": "total_alt", "name": "Total (selected rung)", "line": mag,
                        "settlement": settlement,
                        "outcomes": [price_outcome(f"Over {mag:g}", 1 - phi((mag - total) / sigma_total)),
                                     price_outcome(f"Under {mag:g}", phi((mag - total) / sigma_total))]})
            pick_line = mag
        out.append({"key": "_selected", "name": "Handicap" if cls in ("favourite", "cushion") else "Total",
                    "line": pick_line, "settlement": settlement, "selection": sel,
                    "probability": p, "class": cls})
    return {"fixture_id": fid, "markets": [x for x in out if x["key"] != "_selected"],
            "selected": next((x for x in out if x["key"] == "_selected"), None)}


def carried_fixtures():
    fixtures, markets = [], []
    for r in load_carried():
        fx = r["fixture"]
        sport = fx["sport"]
        view = r["view"]
        mk = []
        for m in view.get("markets", []):
            outs = []
            for o in m.get("outcomes", []):
                p = o.get("probability")
                if p is None or not 0 < p < 1:
                    continue
                outs.append(price_outcome(o["selection"], p))
            if outs:
                mk.append({"key": m.get("key"), "name": m.get("name"), "line": m.get("line"),
                           "settlement": "As captured by the T63 desk; not re-verified this session.",
                           "outcomes": outs})
        if not mk:
            continue
        fid = "carried-" + str(fx["id"])
        markets.append({"fixture_id": fid, "markets": mk, "selected": None})
        fixtures.append({
            "id": fid, "sport": sport, "competition": fx.get("competition", ""), "stage": fx.get("stage", ""),
            "start_utc": fx.get("start_utc"), "home": fx.get("home"), "away": fx.get("away"),
            "venue": fx.get("venue", ""), "neutral": bool(fx.get("neutral")),
            "kind": "match", "discovery": "carried", "verification": "cross-checked",
            "source_ids": [], "source_urls": [s.get("url") for s in fx.get("sources", []) if s.get("url")],
            "inputs": fx.get("inputs") or {}, "pricing": {"status": "priced" if sport in CARRIED_PICK_SPORTS else "carried-line",
                                                         "model": "T63 carried model",
                                                         "provenance": "carried-2026-10-22T08:31Z"},
            "model": {"margin": view.get("expected_margin"), "total": None,
                      "home_rating": view.get("rating_home"), "away_rating": view.get("rating_away")},
            "notes": [CARRIED_PRICED[sport]["note"]],
            "flags": ([] if sport in CARRIED_PICK_SPORTS else
                      ["Line only: no same-session official input for both sides, so no pick or confidence is issued."]),
        })
    return fixtures, markets


def olbg_fixtures(official):
    """Turn OLBG discovery cards into listing rows, joining any official match."""
    rows = []
    by_sport = {}
    for f in official:
        by_sport.setdefault(f["sport"], []).append(f)
    for r in load_carried():
        fx = r["fixture"]
        by_sport.setdefault(fx["sport"], []).append(fx)
    for ev in load_olbg():
        sport = ev["sport"]
        kind = "match"
        if ev.get("olbg_market") and any(w in ev["olbg_market"].lower() for w in ("outright", "tournament", "grand final", "win race")):
            kind = "outright"
        if sport == "greyhounds":
            kind = "race"
        if sport in ("golf", "motor-racing"):
            kind = "event"
        start = ev["start_utc"]
        if start and start < NOW_ISO:
            continue  # expired before the desk snapshot
        fid = f"olbg-{sport}-{ev['event_id']}"
        matched = None
        if kind == "match":
            matched = join_official(ev, by_sport.get(sport, []))
        if matched:
            # attach the discovery card to the official fixture, keep official pricing
            matched.setdefault("olbg", []).append({k: ev[k] for k in ("event_id", "match", "time_label", "olbg_selection", "olbg_market", "olbg_tips", "olbg_pct")})
            continue
        rows.append({
            "id": fid, "sport": sport, "competition": ev.get("league") or "", "stage": "",
            "start_utc": start, "home": ev.get("match"), "away": "", "venue": "", "neutral": False,
            "kind": kind, "discovery": "olbg", "verification": "unverified",
            "source_ids": ["olbg-import"], "source_urls": ["https://www.olbg.com/betting-tips/"],
            "inputs": {}, "pricing": {"status": "unpriced", "model": None, "provenance": "none"},
            "olbg": [{k: ev[k] for k in ("event_id", "match", "time_label", "olbg_selection", "olbg_market", "olbg_tips", "olbg_pct")}],
            "notes": ["OLBG discovery card only; no official fixture or current-form input was captured for this row."],
            "flags": ["Unverified listing: no official source read."],
        })
    return rows


def join_official(ev, candidates):
    text = (ev.get("match") or "").lower()
    if ev["sport"] in ("darts", "baseball", "rugby-union", "handball"):
        toks = set(re.findall(r"[a-z]{4,}", text))
        for f in candidates:
            names = [str(f.get("home") or "").lower(), str(f.get("away") or "").lower()]
            hits = 0
            for n in names:
                nt = set(re.findall(r"[a-z]{4,}", n))
                if nt and (len(nt & toks) >= 2 or any(t in text for t in nt)):
                    hits += 1
            if hits == 2 and len(toks) >= 3:
                return f
    if ev["sport"] == "basketball" and "euroleague" in text or ev["sport"] == "basketball":
        for f in candidates:
            hn = f["home"].lower()
            an = f["away"].lower()
            if any(a in text for a in [hn, an]) and sum(1 for a in [hn, an] if a in text) >= 1:
                # require both sides to appear through aliases
                hit = 0
                for side in (f["home"], f["away"]):
                    key = side.lower()
                    aliases = [k for k, v in EURO_ALIASES.items() if EUROLEAGUE.get(v, ("",))[0] == side]
                    if key in text or any(a in text for a in aliases):
                        hit += 1
                if hit == 2:
                    return f
    if ev["sport"] == "ice-hockey":
        teams = [t.strip() for t in re.split(r"\s+@\s+|\s+vs\s+", ev.get("match") or "", flags=re.I)]
        if len(teams) == 2:
            abbrs = []
            for t in teams:
                low = t.lower()
                ab = None
                for city, code in NHL_CITY_TO_ABBREV.items():
                    if city in low:
                        ab = code
                        break
                # also accept the official abbreviation in the string
                if not ab:
                    for code in NHL:
                        if re.search(r"\b" + code + r"\b", t, flags=re.I):
                            ab = code
                            break
                abbrs.append(ab)
            if all(abbrs):
                for f in candidates:
                    if {f["home"], f["away"]} == set(abbrs) or (f["home"] == abbrs[0] and f["away"] == abbrs[1]):
                        return f
                for f in candidates:
                    if set(abbrs) <= {f["home"], f["away"]}:
                        return f
    return None


# ---------------------------------------------------------------------------
# picks and tiers
# ---------------------------------------------------------------------------
def choose_pick(fixture, market_blob):
    if not market_blob or market_blob.get("markets") is None:
        return None
    sel = market_blob.get("selected")
    winner = market_blob["markets"][0]["outcomes"]
    fav = winner[0] if winner[0]["probability"] >= winner[1]["probability"] else winner[1]
    if sel:
        p = sel["probability"]
        cand = price_outcome(sel["selection"], p)
        cand.update({"market": sel["name"].replace(" (selected rung)", ""), "line": sel["line"], "class": sel["class"]})
        return cand
    # no in-band rung: publish the model favourite as the match-winner pick
    return {"selection": fav["selection"], "probability": fav["probability"], "fair_decimal": fav["fair_decimal"],
            "american": fav["american"], "in_band": fav["in_band"], "market": "Match Winner",
            "line": None, "class": "winner"}


def assign_tiers(fixtures, markets):
    for f in fixtures:
        blob = markets.get(f["id"])
        if f["pricing"]["status"] == "carried-line" or f["pricing"]["status"] != "priced" or not blob:
            f["pick"] = None
            f["confidence"] = "line-only" if f["pricing"]["status"] == "carried-line" else "unpriced"
            f["tier_reasons"] = (["Markets are published, but no pick is issued: both sides lack a current verified input."]
                                 if f["pricing"]["status"] == "carried-line" else
                                 ["No verified current-form input for both sides; price left blank."])
            if blob and blob["markets"]:
                w = blob["markets"][0]["outcomes"]
                fav = max(w, key=lambda o: o["probability"])
                f["match_winner"] = fav["selection"]
                f["winner_probability"] = fav["probability"]
            continue
            f["pick"] = None
            f["confidence"] = "unpriced"
            f["tier_reasons"] = ["No verified current-form input for both sides; price left blank."]
            continue
        pick = choose_pick(f, blob)
        f["pick"] = pick
        w = blob["markets"][0]["outcomes"]
        fav = max(w, key=lambda o: o["probability"])
        f["match_winner"] = fav["selection"]
        f["winner_probability"] = fav["probability"]
        reasons = []
        if not pick:
            f["confidence"] = "low"
            f["tier_reasons"] = ["No priceable market."]
            continue
        if f["verification"] == "verified":
            reasons.append("Official fixture and both inputs read in this session or earlier today.")
        else:
            reasons.append("Carried official inputs from an earlier same-day read; not re-fetched.")
        if pick["probability"] > 0.70:
            reasons.append(f"Model probability {pick['probability']*100:.2f}% is above 70%.")
        else:
            reasons.append(f"Model probability {pick['probability']*100:.2f}% is not above 70%.")
        if 1.40 <= pick["fair_decimal"] <= 1.4286:
            reasons.append(f"Originated fair price {pick['fair_decimal']:.4f} is inside 1.40-1.4286 (-250 to -233).")
        else:
            reasons.append(f"Originated fair price {pick['fair_decimal']:.4f} is outside the -250..+10000 window.")
        pred = PREDICTIONS.get(f["id"])
        if pred:
            reasons.append("A unique hand-authored prediction is attached.")
        if f["verification"] != "verified":
            conf = "medium" if f["pricing"]["provenance"] != "none" else "low"
            reasons.append("Capped below High because the inputs were not re-fetched in this session.")
        elif pick["probability"] > 0.70 and 1.40 <= pick["fair_decimal"] <= 1.4286 and pred:
            conf = "high"
            reasons.append("All High gates pass.")
        elif pick["probability"] > 0.70 and 1.40 <= pick["fair_decimal"] <= 1.4286 and not pred:
            conf = "medium"
            reasons.append("Band and probability pass, but no prediction is attached; High withheld.")
        elif f["pricing"]["provenance"] == "fresh":
            conf = "medium"
        else:
            conf = "low"
        f["confidence"] = conf
        f["tier_reasons"] = reasons


# ---------------------------------------------------------------------------
# write JSON
# ---------------------------------------------------------------------------
def build():
    official, official_markets = official_fixtures()
    carried, carried_markets = carried_fixtures()
    listings = olbg_fixtures(official)
    fixtures = official + carried + listings
    markets = dict(official_markets)
    for b in carried_markets:
        markets[b["fixture_id"]] = b
    assign_tiers(fixtures, markets)
    fixtures.sort(key=lambda f: (f.get("start_utc") or "9999", f["sport"], f["id"]))
    picks = [dict(f["pick"], fixture_id=f["id"], sport=f["sport"], home=f["home"], away=f["away"],
                  start_utc=f["start_utc"], competition=f["competition"], confidence=f["confidence"],
                  match_winner=f.get("match_winner"), winner_probability=f.get("winner_probability"),
                  prediction=PREDICTIONS.get(f["id"]), tier_reasons=f["tier_reasons"], verification=f["verification"])
             for f in fixtures if f.get("pick") and f["confidence"] != "unpriced"]
    counts = {
        "fixtures": len(fixtures),
        "matches": sum(1 for f in fixtures if f["kind"] == "match"),
        "priced": sum(1 for f in fixtures if f["pricing"]["status"] == "priced"),
        "markets": sum(len(m["markets"]) for m in markets.values()),
        "outcomes": sum(len(mk["outcomes"]) for m in markets.values() for mk in m["markets"]),
        "high": sum(1 for f in fixtures if f["confidence"] == "high"),
        "medium": sum(1 for f in fixtures if f["confidence"] == "medium"),
        "low": sum(1 for f in fixtures if f["confidence"] == "low"),
        "unpriced": sum(1 for f in fixtures if f["confidence"] == "unpriced"),
        "line_only": sum(1 for f in fixtures if f["confidence"] == "line-only"),
        "sports": len({f["sport"] for f in fixtures}),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "fixtures.json").write_text(json.dumps(fixtures, indent=1))
    (OUT / "markets.json").write_text(json.dumps(markets, indent=1))
    (OUT / "picks.json").write_text(json.dumps(picks, indent=1))
    (OUT / "sources.json").write_text(json.dumps(SOURCES, indent=1))
    (OUT / "meta.json").write_text(json.dumps({
        "schema": "ac872b16-desk-1", "session": "ac872b16-olbg1", "task": "T65",
        "as_of": NOW_ISO, "counts": counts,
        "confidence_rule": "High = model probability > 70% AND originated fair price in 1.40-1.4286 (-250 to -233) AND both inputs official AND unique >=30-word prediction. Medium = priced but one gate missing. Low = priced with weaker/carried inputs. Unpriced = blank, flagged.",
        "model": {
            "basketball": "Expected score = mean(own points scored/GP, opponent points allowed/GP); normal margin sigma 12; total sigma 18; no home-court term.",
            "ice-hockey": "Expected goals = mean(own goals for/GP, opponent goals against/GP); normal margin sigma 2.0; total sigma 2.4; no home-ice term.",
            "aussie-rules": "Ladder-derived expected margin recorded by T63; normal sigma 18.5; total mean 74.5, sigma 20.",
            "carried": "Darts/rugby union/handball/baseball prices carried from data/92af340c/dataset.json (08:31Z).",
        },
        "price_policy": "Fair decimal = 1/p, no margin, no clipping. American is derived from the rounded decimal. These are originated research lines, not bookmaker quotes.",
    }, indent=1))
    return fixtures, markets, picks, counts


if __name__ == "__main__":
    fx, mk, pk, counts = build()
    print(json.dumps(counts, indent=1))
    for f in fx:
        if f["confidence"] == "high":
            p = f["pick"]
            print("HIGH", f["sport"], f["home"], "v", f["away"], "|", p["market"], p["selection"],
                  round(p["probability"], 4), p["fair_decimal"])
