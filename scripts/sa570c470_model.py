#!/usr/bin/env python3
"""Session a570c470 — independent pricing model.

Method (documented on the Methodology page and identical for every sport):

1.  Each side carries one strength figure on a 0-100 scale derived only from the official
    figure recorded in ``data/a570c470/fixtures.json -> inputs``.  No betting market input
    is used anywhere.
2.  The rating gap plus home advantage forms an edge.  ``P(win) = Phi(edge / SCALE)`` where
    SCALE is published per sport.  The same edge sets the expected margin, so handicap and
    total markets come from one distribution rather than three separate guesses.
3.  Prices are FAIR (1 / probability, two decimals, no margin).  The 5% margin a bookmaker
    would need is published alongside so a reader can see the difference.
4.  Best-of-N sports solve for the per-leg probability that reproduces the match probability
    under the binomial model, then price every frame/leg/set market off that score matrix.

Band policy: **High** requires model probability at least 70% AND the published (fair) price
inside -250..+10000, i.e. decimal 1.40..101.00.  Because the desk originates the line it
quotes the handicap rung whose probability lands near 71%, which is inside that window; when
the moneyline itself already sits inside the window the moneyline is used instead.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "a570c470"

PHI = lambda z: 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def PHI_INV(p: float) -> float:
    lo, hi = -8.0, 8.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if PHI(mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


BAND_LO, BAND_HI = 1.40, 101.00
MARGIN = 0.05
HIGH_P, MEDIUM_P = 0.70, 0.55
TARGET_RUNG_P = 0.706
ASSUMED_RANK = {"tennis": 100, "snooker": 64, "darts": 33, "esports": 5}

SCALE = {
    "tennis": 60.0, "snooker": 55.0, "darts": 55.0, "esports": 40.0,
    "basketball": 75.0, "ice-hockey": 80.0, "baseball": 90.0, "handball": 75.0,
    "volleyball": 60.0, "rugby-union": 55.0, "rugby-league": 60.0,
    "aussie-rules": 65.0, "cricket": 80.0, "gaelic": 40.0,
}
HFA = {
    "tennis": 0.0, "snooker": 0.0, "darts": 0.0, "esports": 0.0,
    "basketball": 3.5, "ice-hockey": 6.0, "baseball": 2.0, "handball": 3.0,
    "volleyball": 4.0, "rugby-union": 5.0, "rugby-league": 3.0,
    "aussie-rules": 6.0, "cricket": 3.0, "gaelic": 2.0,
}
STEP = {k: 0.5 for k in ("basketball", "ice-hockey", "baseball", "handball", "rugby-union",
                         "rugby-league", "aussie-rules", "cricket", "gaelic", "tennis")}
RANK_SPORTS = {"tennis", "snooker", "darts", "esports"}
THREE_WAY = {"rugby-union", "rugby-league", "handball", "gaelic"}

SPORT_CAP = {"eSports": ("Medium", "Riot draw tier is a seeding position, not a measured strength rating."),
             "Volleyball": ("Medium", "One round of PlusLiga has been played, so the sample is one match."),
             "Cricket": ("Low", "One- or two-match sample with no published ranking line read."),
             "Gaelic Football": ("Low", "No official club rating exists; a single semi-final margin is the only input.")}


def american(p: float) -> int:
    d = 1.0 / p if p > 0 else 999.0
    if d >= 2.0:
        return int(round((d - 1) * 100))
    return -int(round(100 / (d - 1))) if d > 1.0 else -10000


def dec(p: float) -> float:
    return round(1.0 / min(max(p, 1e-6), 1 - 1e-6), 2)


def in_band(price: float) -> bool:
    return BAND_LO <= price <= BAND_HI


# ------------------------------------------------------------------ strengths
def pct_from(side: dict, kind: str):
    """Win rate on a 0-1 scale from whatever official figure the row carries."""
    if kind == "aussie-rules" and side.get("points") is not None:
        return side["points"] / 40.0                      # maximum ladder points in 10 games
    if kind == "rugby-union" and side.get("points") is not None:
        return side["points"] / (3.0 * side["games"])     # 3 league points for a win
    if kind == "ice-hockey" and side.get("points") is not None:
        return side["points"] / (2.0 * side["games"])
    if side.get("margin") is not None:
        return max(0.05, min(0.95, 0.5 + side["margin"] / 80.0))
    rec = str(side.get("record") or "")
    m = re.match(r"^(\d+)-(\d+)", rec)
    if m:
        w, l = int(m.group(1)), int(m.group(2))
        if w + l == 0:
            return 0.5
        return (w + 1.0) / (w + l + 2.0)                   # two pseudo-games of shrinkage
    return None


def diff_term(side: dict, kind: str) -> float:
    d, g = side.get("diff"), side.get("games")
    if d is None or not g:
        return 0.0
    k = {"basketball": 1.2, "handball": 1.5, "ice-hockey": 3.0, "baseball": 6.0,
         "rugby-union": 1.0, "aussie-rules": 0.6, "cricket": 0.25}.get(kind, 0.0)
    return (d / g) * k


def strength(fx: dict) -> dict:
    kind = fx["market_kind"] or ""
    hi = fx["inputs"].get("home") or {}
    ai = fx["inputs"].get("away") or {}
    out = {"mode": "", "home": 50.0, "away": 50.0, "one_sided": True, "assumed": False,
           "basis_home": hi.get("basis", ""), "basis_away": ai.get("basis", ""),
           "note": ""}

    if kind in RANK_SPORTS:
        hr, ar = hi.get("rank"), ai.get("rank")
        assumed = False
        if hr is None and ar is not None:
            hr, assumed = ASSUMED_RANK[kind], True
            out["note"] = f"home ranking not published; model assumes rank {hr}"
        if ar is None and hr is not None:
            ar, assumed = ASSUMED_RANK[kind], True
            out["note"] = f"away ranking not published; model assumes rank {ar}"
        mult = 18.0 if kind != "esports" else 18.0
        hs = 100 - mult * math.log(hr) if hr else 50.0
        as_ = 100 - mult * math.log(ar) if ar else 50.0
        out.update(mode="ranking", home=hs, away=as_, assumed=assumed,
                   one_sided=(hi.get("rank") is None or ai.get("rank") is None))
        return out

    hp, ap = pct_from(hi, kind), pct_from(ai, kind)
    if hp is None or ap is None:
        out.update(mode="none", one_sided=True)
        return out
    out.update(mode="record",
               home=max(5.0, min(95.0, 100 * hp + diff_term(hi, kind))),
               away=max(5.0, min(95.0, 100 * ap + diff_term(ai, kind))),
               one_sided=False)
    return out


# ------------------------------------------------------------------ markets
def score_matrix(p_leg, need):
    sc = {}
    for x in range(0, need):
        sc[(need, x)] = math.comb(need - 1 + x, x) * p_leg ** need * (1 - p_leg) ** x
        sc[(x, need)] = math.comb(need - 1 + x, x) * (1 - p_leg) ** need * p_leg ** x
    tot = sum(sc.values()) or 1
    return {k: v / tot for k, v in sc.items()}


def normal_markets(fx, mu, sigma, three_way):
    mk = []
    p_home = 1 - PHI((0.5 - mu) / sigma) if three_way else PHI(mu / sigma)
    p_away = PHI((-0.5 - mu) / sigma) if three_way else 1 - p_home
    mk.append(("Match winner", fx["home"], p_home, True))
    if three_way:
        mk.append(("Match winner", "Draw", 1 - p_home - p_away, False))
    mk.append(("Match winner", fx["away"], p_away, True))
    if three_way:
        ph = p_home / (p_home + p_away)
        mk.append(("Draw no bet", f"{fx['home']} (DNB)", ph, False))
        mk.append(("Draw no bet", f"{fx['away']} (DNB)", 1 - ph, False))

    step = STEP.get(fx["market_kind"], 0.5)
    fav_home = p_home >= p_away
    fav = fx["home"] if fav_home else fx["away"]
    dog = fx["away"] if fav_home else fx["home"]
    base = mu if fav_home else -mu
    used = set()
    for target in (0.50, 0.60, TARGET_RUNG_P):
        line = base - sigma * PHI_INV(target)
        line = round(line / step) * step
        for _ in range(8):
            p = PHI((base - line) / sigma)
            if abs(p - target) < 0.012:
                break
            line += step if p < target else -step
        if line == 0 or line in used:
            continue
        used.add(line)
        p_fav = PHI((base - line) / sigma)
        if line > 0:
            fav_label, dog_label = f"{fav} -{line:g}", f"{dog} +{line:g}"
        else:
            fav_label, dog_label = f"{fav} +{-line:g}", f"{dog} -{-line:g}"
        mk.append(("Handicap", fav_label, p_fav, line > 0))
        mk.append(("Handicap", dog_label, 1 - p_fav, False))

    tl = fx.get("total_line")
    if tl:
        tsig = sigma * 1.6 if fx["market_kind"] in ("ice-hockey", "baseball") else sigma * 1.15
        step_t = max(0.5, round(tsig * 0.5, 1))
        for off in (0.0, step_t, -step_t):
            ln = round((tl + off) / 0.5) * 0.5
            mk.append(("Total", f"Over {ln:g}", 1 - PHI((ln - tl) / tsig), False))
            mk.append(("Total", f"Under {ln:g}", PHI((ln - tl) / tsig), False))
    return mk


def series_markets(fx, p_match):
    cfg = fx["series"]
    legs, need, unit = cfg["legs"], cfg["need"], cfg["unit"]
    lo, hi = 0.001, 0.999
    for _ in range(200):
        mid = (lo + hi) / 2
        sc = score_matrix(mid, need)
        if sum(v for (a, b), v in sc.items() if a > b) < p_match:
            lo = mid
        else:
            hi = mid
    p_leg = (lo + hi) / 2
    sc = score_matrix(p_leg, need)
    p_home = sum(v for (a, b), v in sc.items() if a > b)
    mk = [("Match winner", fx["home"], p_home, True), ("Match winner", fx["away"], 1 - p_home, True)]
    if legs > 1:
        for (a, b), v in sorted(sc.items(), key=lambda kv: -kv[1])[:6]:
            who = fx["home"] if a > b else fx["away"]
            mk.append((f"Correct score ({unit})", f"{a}-{b} {who}", v, False))
    for line in (0.5, 1.5, 2.5, 3.5):
        if line > need - 0.5:
            continue
        ph = sum(v for (a, b), v in sc.items() if (a - b) > line)
        pa = sum(v for (a, b), v in sc.items() if (b - a) > line)
        if ph > 0.02:
            mk.append(("Handicap", f"{fx['home']} -{line:g} {unit}", ph, p_home >= 0.5))
        if pa > 0.02:
            mk.append(("Handicap", f"{fx['away']} -{line:g} {unit}", pa, p_home < 0.5))
    for tl in (legs + 0.5, legs + 1.5, legs + 2.5):
        over = sum(v for (a, b), v in sc.items() if a + b > tl)
        mk.append(("Total", f"Over {tl:g} {unit}", over, False))
        mk.append(("Total", f"Under {tl:g} {unit}", 1 - over, False))
    return mk


def cap_for(fx):
    if fx["sport"] == "Basketball" and fx["competition"] == "NBA":
        return "Medium", "NBA rows carry a one-game sample, so the desk caps them at Medium."
    if fx["sport"] in SPORT_CAP:
        return SPORT_CAP[fx["sport"]]
    return None, None


def price(fx):
    st = strength(fx)
    kind = fx["market_kind"]
    scale = SCALE[kind]
    hfa = fx.get("hfa", HFA.get(kind, 0.0))
    edge = st["home"] - st["away"] + hfa
    p_match_home = PHI(edge / scale)

    if fx.get("series"):
        raw = series_markets(fx, p_match_home)
    else:
        sigma = fx.get("sigma") or 12.0
        raw = normal_markets(fx, (edge / scale) * sigma, sigma, kind in THREE_WAY)

    markets, seen = [], set()
    for market, selection, p, opinion in raw:
        if p < 0.02 or p > 0.98:
            continue
        if (market, selection) in seen:
            continue
        seen.add((market, selection))
        d = dec(p)
        markets.append({
            "market": market, "selection": selection,
            "model_prob": round(p, 4), "prob_pct": round(p * 100, 1),
            "price": d, "us": american(p),
            "book_price_margin5": round(d / (1 + MARGIN), 2),
            "in_band": in_band(d), "opinion": opinion,
        })

    h2h = [m for m in markets if m["market"] == "Match winner" and m["selection"] != "Draw"]
    if not h2h:
        return None
    mw = max(h2h, key=lambda m: m["model_prob"])
    mw_conf = "High" if mw["model_prob"] >= HIGH_P and mw["in_band"] else (
        "Medium" if mw["model_prob"] >= MEDIUM_P else "Low")

    eligible = [m for m in markets
                if m["market"] in ("Match winner", "Handicap") and m["in_band"]
                and m.get("opinion") and m["selection"] != "Draw"]
    best = max(eligible, key=lambda m: m["model_prob"]) if eligible else None
    conf, cap = "Low", None
    if best:
        p = best["model_prob"]
        conf = "High" if p >= HIGH_P else ("Medium" if p >= MEDIUM_P else "Low")
    if conf == "High" and (st["one_sided"] or st["assumed"]):
        conf, cap = "Medium", "one side's strength is missing or is a documented assumption"
    if conf == "High":
        lvl, txt = cap_for(fx)
        if lvl:
            conf, cap = lvl, txt
    if conf == "High" and fx["status"] != "verified":
        conf, cap = "Medium", "row not newly verified this session"

    return {
        "id": fx["id"], "sport": fx["sport"], "competition": fx["competition"],
        "home": fx["home"], "away": fx["away"], "start_utc": fx["start_utc"],
        "venue": fx["venue"], "stage": fx["stage"], "status": fx["status"],
        "sources": fx["sources"], "flags": fx["flags"],
        "strength": {k: (round(v, 1) if isinstance(v, float) else v) for k, v in st.items()},
        "edge": round(edge, 2), "scale": scale, "hfa": hfa,
        "markets": markets,
        "match_winner_call": {
            "selection": mw["selection"], "price": mw["price"], "us": mw["us"],
            "prob_pct": mw["prob_pct"], "confidence": mw_conf,
        },
        "desk_pick": best, "confidence": conf, "cap_reason": cap,
    }


def main() -> None:
    fx = json.loads((DATA / "fixtures.json").read_text())
    books, cards = [], []
    for row in fx["fixtures"]:
        book = None if (row["event_only"] or not row.get("market_kind")) else price(row)
        if book is None:
            cards.append({k: row[k] for k in ("id", "sport", "competition", "home", "start_utc",
                                              "venue", "stage", "sources", "flags")})
        else:
            books.append(book)

    prices = sum(len(b["markets"]) for b in books)
    conf = {"High": 0, "Medium": 0, "Low": 0}
    for b in books:
        conf[b["confidence"]] += 1
    doc = {
        "model": {
            "version": "a570c470-v1",
            "strength_scale": SCALE, "home_advantage": HFA, "margin_for_transparency": MARGIN,
            "band": {"low_decimal": BAND_LO, "high_decimal": BAND_HI, "low_us": -250, "high_us": 10000},
            "high_probability_floor": HIGH_P, "medium_probability_floor": MEDIUM_P,
            "assumed_rank_when_missing": ASSUMED_RANK,
        },
        "book_count": len(books), "event_card_count": len(cards),
        "price_count": prices, "confidence_counts": conf, "high_count": conf["High"],
        "books": books, "event_cards": cards,
    }
    (DATA / "lines.json").write_text(json.dumps(doc, indent=1) + "\n")
    print(f"{len(books)} priced books | {len(cards)} event cards | {prices} prices | "
          f"{conf['High']} High / {conf['Medium']} Medium / {conf['Low']} Low")
    for b in books:
        if b["confidence"] == "High":
            d = b["desk_pick"]
            print(f"  HIGH {b['sport']:<13} {b['home'][:22]:<22} v {b['away'][:22]:<22} "
                  f"{d['market']:<11} {d['selection'][:32]:<32} {d['price']:>5} {d['prob_pct']:>5}%")


if __name__ == "__main__":
    main()
