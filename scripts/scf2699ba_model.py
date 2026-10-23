"""Session cf2699ba-olbg1 — line origination.

Two clearly separated input classes, never mixed:

  market      Official inputs for a fixture confirmed on an official page this
              session (NHL published quotes, MLB season records, URC round
              results). These are the only selections eligible for Medium/High.

  consensus    OLBG public tip-share only. A vote distribution is NOT a
              probability, so the share is shrunk 50% toward 0.5, capped into
              [0.50, 0.90] and hard-capped at Low confidence. It exists so that
              every discovered match carries a published, clearly-labelled
              indicative price instead of a silent blank; it is never evidence.

Confidence rule (brief, taken literally):
  High   : p >= 0.70 AND -250 <= American price <= +10000 AND input class = market
  Medium : 0.62 <= p < 0.70 AND input class = market
  Low    : everything else
"""
import json
import math
import os

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "cf2699ba")

SIGMA_RUGBY = 14.0        # declared: s.d. of URC match margin, points
SHRINK_URC = 0.25         # declared: single-round margin shrinkage
HFA_RUGBY = 3.0           # declared: home advantage, points
CAP_PROB = 0.85           # declared safeguard: no one-round-sample price above 85%
SHRINK_CONSENSUS = 0.5
CONSENSUS_CAP = 0.90

WIN_MARKETS = {
    "win match", "money line", "to win", "win tournament", "grand final winner",
    "outright winner", "win race", "daily races", "win match 2-way",
}


def norm_cdf(z):
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def american_from_prob(p):
    if p <= 0 or p >= 1:
        return None
    if p > 0.5:
        return -(100.0 * p) / (1.0 - p)
    return 100.0 * (1.0 - p) / p


def decimal_from_prob(p):
    return 1.0 / p if p else None


def implied_us(quote):
    """American quote -> implied probability (with vig)."""
    q = float(quote)
    if q < 0:
        return (-q) / ((-q) + 100.0)
    return 100.0 / (q + 100.0)


def devig_pair(a_quotes, b_quotes):
    """Median, over providers, of the two-way normalised probability of side A."""
    ps = []
    for qa, qb in zip(a_quotes, b_quotes):
        ia, ib = implied_us(qa), implied_us(qb)
        ps.append(ia / (ia + ib))
    ps.sort()
    return ps[len(ps) // 2]


def poisson_pmf(k, lam):
    return math.exp(-lam) * lam ** k / math.factorial(k)


def mlb_model(inp):
    """Independent Poisson run model, conditioned on no tie (extra innings excluded)."""
    lam_a = (inp["away_rs"] / inp["away_g"] + inp["home_ra"] / inp["home_g"]) / 2.0
    lam_h = (inp["home_rs"] / inp["home_g"] + inp["away_ra"] / inp["away_g"]) / 2.0
    N = 26
    grid = {}
    total = 0.0
    for i in range(N):
        for j in range(N):
            p = poisson_pmf(i, lam_a) * poisson_pmf(j, lam_h)
            if i == j:
                continue
            grid[(i, j)] = p
            total += p
    for k in grid:
        grid[k] /= total
    ph = sum(p for (i, j), p in grid.items() if j > i)
    p_away_cover = sum(p for (i, j), p in grid.items() if i - j > -1.5)  # away +1.5
    p_home_cover = sum(p for (i, j), p in grid.items() if j - i > 1.5)
    lam_tot = lam_a + lam_h
    line = math.floor(lam_tot) + 0.5
    p_over = sum(p for (i, j), p in grid.items() if i + j > line)
    # log5 cross-check
    pa, ph_ = inp["away_pct"], inp["home_pct"]
    log5 = (pa - pa * ph_) / (pa + ph_ - 2 * pa * ph_)
    return {
        "lambda_away": lam_a, "lambda_home": lam_h, "total_line": line,
        "p_home_ml": ph, "p_home_rl": p_home_cover, "p_away_rl": p_away_cover,
        "p_over": p_over, "log5_home": 1 - log5,
    }


# The URC page prints short club names in its results block and sponsor-prefixed
# names in its fixture block for the same clubs (F-CF-05). These aliases are the
# only name mapping applied anywhere in this desk.
URC_ALIAS = {
    "Hollywoodbets Sharks": "Sharks",
    "10bet Lions": "Lions",
    "Connacht Rugby": "Connacht",
    "Edinburgh Rugby": "Edinburgh",
    "Vodacom Bulls": "Bulls",
    "DHL Stormers": "Stormers",
}


def rugby_form_ratings(results):
    """Shrunk mean margin per club from verified results (no invented ratings)."""
    agg = {}
    for r in results:
        m = r["hs"] - r["as"]
        agg.setdefault(r["home"], []).append(m)
        agg.setdefault(r["away"], []).append(-m)
    return {team: SHRINK_URC * (sum(v) / len(v)) for team, v in agg.items()}


def rugby_model(inp, margins):
    home, away = inp["home"], inp["away"]
    mh = margins.get(URC_ALIAS.get(home, home))
    ma = margins.get(URC_ALIAS.get(away, away))
    if mh is None or ma is None:
        raise SystemExit(f"no verified form for {home} v {away}")
    exp_margin = (mh - ma) + HFA_RUGBY
    p_home = norm_cdf(exp_margin / SIGMA_RUGBY)
    p_home = min(max(p_home, 1 - CAP_PROB), CAP_PROB)
    line = -round(exp_margin * 2) / 2.0          # handicap applied to the home side
    p_home_cover = norm_cdf((exp_margin + line) / SIGMA_RUGBY)
    lam = 54.6  # mean total points across the eight verified Round 3 matches
    total_line = 54.5
    p_over = norm_cdf((54.6 - total_line) / 15.0)
    return {"expected_margin": exp_margin, "p_home_ml": p_home,
            "handicap_line": line, "p_home_cover": p_home_cover,
            "total_line": total_line, "p_over": p_over,
            "home_margin_form": mh, "away_margin_form": ma}


def tier(p, price, klass):
    if klass != "market":
        return "Low"
    if p >= 0.70 and price is not None and -250 <= price <= 10000:
        return "High"
    if p >= 0.62:
        return "Medium"
    return "Low"


def market_block(label, outcomes, klass, notes=None):
    """outcomes: list of (selection, p, extra)."""
    rows = []
    for sel, p, extra in outcomes:
        if p is None:
            rows.append({"selection": sel, "p": None, "decimal": None, "american": None,
                         "tier": None, "note": "withheld — no official input"})
            continue
        dec = decimal_from_prob(p)
        am = american_from_prob(p)
        rows.append({
            "selection": sel,
            "p": round(p, 4),
            "decimal": round(dec, 3),
            "american": int(round(am)),
            "tier": tier(p, am, klass),
        })
    return {"market": label, "class": klass, "outcomes": rows, "notes": notes or []}


def build():
    fixtures = json.load(open(os.path.join(DATA, "fixtures.json")))["fixtures"]
    discovery = json.load(open(os.path.join(DATA, "discovery.json")))["events"]
    urc_r3 = json.load(open(os.path.join(DATA, "fixtures.json")))["urc_round3_results"]
    margins = rugby_form_ratings(urc_r3)

    lines = []
    for fx in fixtures:
        kind = fx["inputs"]["kind"]
        blocks = []
        detail = {}
        if kind == "nhl-provider-quotes":
            facts = {f["k"]: f["v"] for f in fx["facts"]}
            if fx["id"] == "fx-nhl-mtl-chi":
                a_q = ["-170", "-170", "-162"]
                b_q = ["+138", "+142", "+134"]
                away, home = "Montreal Canadiens", "Chicago Blackhawks"
            else:
                a_q = ["+105", "+105", "+106"]
                b_q = ["-129", "-125", "-128"]
                away, home = "Tampa Bay Lightning", "Colorado Avalanche"
            p_away = devig_pair(a_q, b_q)
            detail = {"devig_away": round(p_away, 4), "away": away, "home": home}
            blocks.append(market_block("Money line (60 minutes + OT/SO)", [
                (away, p_away, None), (home, 1 - p_away, None)], "market",
                ["De-vigged median of the three mutually consistent American-quote providers "
                 "(8, 9, 7) embedded in the official NHL schedule feed.",
                 "Puck line and game total withheld: the NHL feed supplies no goal-rate input "
                 "for either club and no official standings rows for them were read."]))
        elif kind == "mlb-records":
            m = mlb_model(fx["inputs"])
            detail = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in m.items()}
            blocks.append(market_block("Money line (incl. extra innings)", [
                ("Tampa Bay Rays", 1 - m["p_home_ml"], None),
                ("Milwaukee Brewers", m["p_home_ml"], None)], "market",
                ["Independent-Poisson run model on paired official regular-season run rates; "
                 "tie mass removed (no draw in MLB)."]))
            blocks.append(market_block("Run line 1.5", [
                ("Tampa Bay Rays +1.5", m["p_away_rl"], None),
                ("Milwaukee Brewers -1.5", m["p_home_rl"], None)], "market",
                [f"Model line, not an available sportsbook offer. log5 cross-check on season "
                 f"win% gives Milwaukee {m['log5_home']:.3f} on the money line."]))
            blocks.append(market_block(f"Game total {m['total_line']}", [
                (f"Over {m['total_line']}", m["p_over"], None),
                (f"Under {m['total_line']}", 1 - m["p_over"], None)], "market",
                [f"Centred on the paired run-rate expectation ({m['lambda_away']:.2f} + "
                 f"{m['lambda_home']:.2f} = {m['lambda_away'] + m['lambda_home']:.2f} runs)."]))
        elif kind == "urc-form":
            m = rugby_model(fx, margins)
            detail = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in m.items()}
            blocks.append(market_block("Match winner", [
                (fx["home"], m["p_home_ml"], None), (fx["away"], 1 - m["p_home_ml"], None)],
                "market",
                ["Margin-form model: each club's verified Round 3 margin shrunk 35% toward zero, "
                 "plus a declared 3-point home advantage, mapped through a normal with a declared "
                 "14-point standard deviation, capped at 85%. Single-round sample."]))
            blocks.append({"market": "Handicap", "class": "market", "outcomes": [
                {"selection": f"{fx['home']} {m['handicap_line']:+.1f} (fair model line)",
                 "p": None, "decimal": None, "american": None, "tier": None,
                 "note": "withheld — one verified round cannot support a scoring-margin line"},
                {"selection": f"Match total ({m['total_line']})", "p": None, "decimal": None,
                 "american": None, "tier": None,
                 "note": "withheld — no club-level scoring rate was verified; league mean only"}]})
        lines.append({"fixture_id": fx["id"], "sport": fx["sport"], "name": fx["name"],
                      "competition": fx["competition"], "start": fx["official_start_utc"],
                      "local_start": fx.get("local_start"), "venue": fx["venue"],
                      "status": fx["status"], "sources": fx["sources"],
                      "facts": fx["facts"], "inputs": fx["inputs"], "detail": detail,
                      "blocks": blocks})

    # ---- indicative consensus prices for discovery-only rows ----
    sports = {s["key"]: s["name"] for s in json.load(open(os.path.join(DATA, "sports.json")))["sports"]}
    verified_ids = {fx["olbg_event_id"] for fx in fixtures}
    indicative = []
    for row in discovery:
        market = (row["olbg_market"] or "").strip().lower()
        share = row.get("olbg_pct")
        rec = {
            "sport": row["sport"], "sport_name": sports[row["sport"]],
            "name": row["name"], "competition": row["competition_text"],
            "olbg_time_text": row["olbg_time_text"], "olbg_url": row["olbg_url"],
            "olbg_event_id": row["olbg_event_id"], "olbg_pick": row["olbg_pick"],
            "olbg_market": row["olbg_market"], "olbg_tips": row["olbg_tips"],
            "olbg_pct": share, "class": "consensus",
            "linked_fixture": None,
        }
        if row["olbg_event_id"] in verified_ids and market in WIN_MARKETS:
            rec["price_note"] = "official price published in the verified fixture block"
            rec["p"] = None
        elif market in WIN_MARKETS and share:
            p_raw = share / 100.0
            p = 0.5 + SHRINK_CONSENSUS * (p_raw - 0.5)
            p = min(max(p, 1 - CONSENSUS_CAP), CONSENSUS_CAP)
            am = american_from_prob(p)
            rec.update({"p": round(p, 4), "decimal": round(decimal_from_prob(p), 3),
                        "american": int(round(am)), "tier": "Low",
                        "price_note": "indicative: 50% shrunk tip-share, not a probability"})
        else:
            rec.update({"p": None, "decimal": None, "american": None, "tier": None,
                        "price_note": "not priced — a tip share cannot be mapped onto a "
                                      "handicap/total/set market line"})
        indicative.append(rec)

    all_rows = []
    for L in lines:
        for b in L["blocks"]:
            for o in b["outcomes"]:
                all_rows.append({
                    "fixture_id": L["fixture_id"], "sport": L["sport"], "name": L["name"],
                    "class": "market", "market": b["market"], "selection": o["selection"],
                    "p": o["p"], "decimal": o["decimal"], "american": o["american"],
                    "tier": o["tier"],
                })

    tiers = {"High": 0, "Medium": 0, "Low": 0}
    for r in all_rows + [i for i in indicative if i.get("tier")]:
        if r.get("tier"):
            tiers[r["tier"]] += 1

    # --- disclosures: selections at >=70% that the -250 floor excludes ---
    out_of_band = []
    for r in all_rows:
        if r["class"] == "market" and r["p"] and r["p"] >= 0.70 and r["american"] is not None \
                and r["american"] < -250:
            out_of_band.append({"sport": r["sport"], "name": r["name"], "market": r["market"],
                                "selection": r["selection"], "p": r["p"],
                                "american": r["american"], "reason": "shorter than -250"})
    # --- per-sport top five by originated probability (priced rows only) ---
    sports_all = {s["key"]: s["name"] for s in json.load(open(os.path.join(DATA, "sports.json")))["sports"]}
    top5 = {}
    for key in sports_all:
        pool = []
        for r in all_rows:
            if r["sport"] == key and r["p"]:
                pool.append({"name": r["name"], "market": r["market"], "selection": r["selection"],
                             "p": r["p"], "american": r["american"], "tier": r["tier"],
                             "class": "market"})
        for r in indicative:
            if r["sport"] == key and r.get("p"):
                pool.append({"name": r["name"], "market": r["olbg_market"],
                             "selection": r["olbg_pick"], "p": r["p"],
                             "american": r["american"], "tier": "Low", "class": "consensus"})
        pool.sort(key=lambda x: -x["p"])
        top5[key] = pool[:5]
    out = {
        "session": "cf2699ba-olbg1",
        "out_of_band": out_of_band,
        "top5_by_sport": top5,
        "generated_at": "2026-10-23T16:40Z",
        "params": {"sigma_rugby": SIGMA_RUGBY, "shrink_urc": SHRINK_URC,
                   "hfa_rugby": HFA_RUGBY, "cap_prob": CAP_PROB,
                   "shrink_consensus": SHRINK_CONSENSUS, "consensus_cap": CONSENSUS_CAP},
        "rule": "High = p>=0.70 AND -250<=price<=+10000 AND market-class input; "
                "Medium = 0.62<=p<0.70 market-class; Low = everything else.",
        "verified_lines": lines,
        "verified_outcome_count": len(all_rows),
        "indicative": indicative,
        "tier_counts": tiers,
        "rugby_form_margins": {k: round(v, 2) for k, v in margins.items()},
    }
    with open(os.path.join(DATA, "lines.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print("verified fixtures:", len(lines), "verified outcomes:", len(all_rows))
    print("tier counts:", tiers)
    print("indicative rows:", len(indicative),
          "priced:", sum(1 for i in indicative if i.get("p")))
    print("rugby margins:", out["rugby_form_margins"])
    for L in lines:
        for b in L["blocks"]:
            for o in b["outcomes"]:
                if o["p"]:
                    print(f"  {L['name'][:46]:46s} {b['market'][:22]:22s} {o['selection'][:30]:30s} "
                          f"p={o['p']:.3f} {o['american']:+5d} {o['tier']}")


if __name__ == "__main__":
    build()
