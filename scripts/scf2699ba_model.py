#!/usr/bin/env python3
"""T67 - originate our own prices from the observation set.

Three input classes, never mixed:

  official  the fixture is confirmed on a governing-body page and every number used comes from that
            page (or from a repository capture of it, which is labelled as such). Eligible for High.
  consensus OLBG tip-vote share only. A share is a count of published tips. It is shrunk halfway to a
            coin flip, capped at 90%, and can never be graded above Low.
  withheld  no defensible input, so no price. The market is shown and the reason is recorded.

Published convention: fair decimal = 1/p, American from p, no margin added, no bookmaker quote claimed.

Parameters are declared here once, not tuned per row:
  SIGMA_RUGBY = 14.0 points   round-to-round margin spread
  HFA_RUGBY   = 3.0 points    declared home prior (no per-venue data was available)
  SHRINK_RUGBY= 0.25          one verified round, so three quarters of every observed margin is noise
  CAP_P       = 0.85          no selection is priced above 85% on a single round of evidence
  SHRINK_CONS = 0.50          consensus half-way to a coin flip
  CAP_CONS    = 0.90

Run: python3 scripts/scf2699ba_model.py
Out: data/cf2699ba/lines.json
"""
import json
import math
import pathlib

DATA = pathlib.Path(__file__).resolve().parent.parent / "data" / "cf2699ba"

SIGMA_RUGBY = 14.0
HFA_RUGBY = 3.0
SHRINK_RUGBY = 0.25
CAP_P = 0.85
SHRINK_CONS = 0.50
CAP_CONS = 0.90
BAND_LOW, BAND_HIGH = -250, 10000
BASEBALL_TOTAL_LINE = 8.5
BASEBALL_MAX_RUNS = 20

WIN_MARKETS = {"ML", "OUT"}


def norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def implied(american):
    a = float(american)
    return (-a) / (-a + 100.0) if a < 0 else 100.0 / (a + 100.0)


def to_american(p):
    if p <= 0 or p >= 1:
        raise ValueError(p)
    return round(-100.0 * p / (1.0 - p)) if p > 0.5 else round(100.0 * (1.0 - p) / p)


def fmt_american(a):
    return f"{a:+d}"


def fair_decimal(p):
    return round(1.0 / p, 3)


def median(xs):
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0


# ------------------------------------------------------------------------------------------- prices
def devig_pair(quotes):
    """quotes: {side: [american,...]} aligned by provider. Returns median normalised p for 'away'."""
    pa = quotes["away"]["american"]
    ph = quotes["home"]["american"]
    if len(pa) != len(ph):
        raise SystemExit("provider arrays are not aligned")
    probs = []
    for a, h in zip(pa, ph):
        ia, ih = implied(a), implied(h)
        probs.append(ia / (ia + ih))
    return median(probs), [round(x, 4) for x in probs]


def poisson_pmf(lam, k):
    return math.exp(-lam) * lam ** k / math.factorial(k)


def baseball_model(m):
    away, home = m["away"], m["home"]
    g = m["games"]
    lam_a = ((away["rs"] / g) + (home["ra"] / g)) / 2.0
    lam_h = ((home["rs"] / g) + (away["ra"] / g)) / 2.0
    pa = [poisson_pmf(lam_a, i) for i in range(BASEBALL_MAX_RUNS + 1)]
    ph = [poisson_pmf(lam_h, j) for j in range(BASEBALL_MAX_RUNS + 1)]
    win_a = win_h = tie = 0.0
    home_by_two = 0.0
    over = 0.0
    for i, x in enumerate(pa):
        for j, y in enumerate(ph):
            p = x * y
            if i > j:
                win_a += p
            elif j > i:
                win_h += p
            else:
                tie += p
            if j - i >= 2:
                home_by_two += p
            if i + j > BASEBALL_TOTAL_LINE:
                over += p
    decider = win_a + win_h
    p_home = win_h / decider
    p_home_rl = home_by_two / decider
    p_over = over  # a total is not conditioned on the tie-break: the game still has runs
    wa = away["w"] / (away["w"] + away["l"])
    wh = home["w"] / (home["w"] + home["l"])
    log5 = (wh - wa * wh) / (wa + wh - 2 * wa * wh)
    return {
        "p_home": p_home, "p_away": 1 - p_home,
        "p_home_rl": p_home_rl, "p_away_rl": 1 - p_home_rl,
        "p_over": p_over, "p_under": 1 - p_over,
        "lam_away": lam_a, "lam_home": lam_h,
        "exp_total": lam_a + lam_h,
        "log5_home": log5,
        "records": {"away": f"{away['w']}-{away['l']}", "home": f"{home['w']}-{home['l']}"},
    }


def rugby_margins(results):
    agg = {}
    for hname, hs, aname, as_, _d in results:
        agg.setdefault(hname, []).append(hs - as_)
        agg.setdefault(aname, []).append(as_ - hs)
    return agg


def rugby_model(m, margins):
    for side in ("home", "away"):
        if m[side] not in margins:
            raise SystemExit(f"no verified form for {m[side]} - refusing to price {m['name']}")
    mh = SHRINK_RUGBY * (sum(margins[m["home"]]) / len(margins[m["home"]]))
    ma = SHRINK_RUGBY * (sum(margins[m["away"]]) / len(margins[m["away"]]))
    exp_margin = mh - ma + HFA_RUGBY
    raw = norm_cdf(exp_margin / SIGMA_RUGBY)
    p_home = min(max(raw, 1 - CAP_P), CAP_P)
    return {"p_home": p_home, "p_away": 1 - p_home, "exp_margin": exp_margin,
            "raw_home": raw, "form_home": mh, "form_away": ma,
            "n_home": len(margins[m["home"]]), "n_away": len(margins[m["away"]])}


# -------------------------------------------------------------------------------------------- tiers
def grade(p, american, cls):
    if cls != "official":
        return "Low"
    if p >= 0.70 and BAND_LOW <= american <= BAND_HIGH:
        return "High"
    if p >= 0.62:
        return "Medium"
    return "Low"


def outcome(mid, sport, fixture, market, selection, p, source_id, cls, note="", extra=None):
    american = to_american(p)
    return {
        "fixture_id": mid, "sport": sport, "fixture": fixture,
        "market": market, "selection": selection,
        "p": round(p, 4), "decimal": fair_decimal(p), "american": american,
        "american_text": fmt_american(american),
        "in_band": BAND_LOW <= american <= BAND_HIGH,
        "class": cls, "tier": grade(p, american, cls),
        "source": source_id, "note": note, "extra": extra or {},
    }


def main():
    sports = json.loads((DATA / "sports.json").read_text())
    discovery = json.loads((DATA / "discovery.json").read_text())
    fixtures = json.loads((DATA / "fixtures.json").read_text())
    inputs = json.loads((DATA / "inputs.json").read_text())

    rows, withheld, derivations = [], [], {}

    # ---- NHL: money line from the three mutually consistent provider quotes ---------------------
    for fid, q in inputs["nhl_quotes"].items():
        fx = next(f for f in fixtures if f["id"] == fid)
        p_away, per_provider = devig_pair(q)
        rows.append(outcome(fid, fx["sport"], fx["name"], "Money line", f"{fx['away']} win",
                            p_away, q["source"], "official",
                            "De-vigged median of the three consistent provider quotes in the league feed.",
                            {"providers": q["away"]["american"], "per_provider_p": per_provider}))
        rows.append(outcome(fid, fx["sport"], fx["name"], "Money line", f"{fx['home']} win",
                            1 - p_away, q["source"], "official",
                            "Opposite side of the same de-vigged pair.",
                            {"providers": q["home"]["american"], "per_provider_p": per_provider}))
        derivations[fid] = {
            "method": "two-way de-vig of three provider quotes, median of the normalised pairs",
            "excluded": q["excluded"],
            "provider_p_away": per_provider,
        }
        for mkt, why in (("Puck line", "The feed publishes no per-club goal rates, so no puck line or "
                                       "total can be derived without inventing an input."),
                         ("Game total", "As above: no confirmed goals-for or goals-against input for "
                                        "these four clubs this session.")):
            withheld.append({"fixture_id": fid, "sport": fx["sport"], "fixture": fx["name"],
                             "market": mkt, "reason": why, "source": q["source"]})

    # ---- MLB: Poisson from official season runs ------------------------------------------------
    for fid, m in inputs["mlb"].items():
        fx = next(f for f in fixtures if f["id"] == fid)
        r = baseball_model(m)
        src = f"{m['away']['source']}+{m['home']['source']}"
        note = (f"Poisson with {r['lam_away']:.2f} expected runs for {m['away']['name']} and "
                f"{r['lam_home']:.2f} for {m['home']['name']}; ties removed.")
        rows += [
            outcome(fid, fx["sport"], fx["name"], "Money line", f"{fx['home']} win", r["p_home"], src,
                    "official", note + f" Cross-check: log5 on season records gives {r['log5_home']:.3f}.",
                    {"log5": round(r["log5_home"], 4)}),
            outcome(fid, fx["sport"], fx["name"], "Money line", f"{fx['away']} win", r["p_away"], src,
                    "official", "Opposite side of the same distribution."),
            outcome(fid, fx["sport"], fx["name"], "Run line -1.5", f"{fx['home']} -1.5", r["p_home_rl"], src,
                    "official", "Home side must win by two or more."),
            outcome(fid, fx["sport"], fx["name"], "Run line +1.5", f"{fx['away']} +1.5", r["p_away_rl"], src,
                    "official", "Away side covers by winning, or losing by one."),
            outcome(fid, fx["sport"], fx["name"], "Game total", f"Over {BASEBALL_TOTAL_LINE}", r["p_over"], src,
                    "official", f"Expected total {r['exp_total']:.2f} runs against a {BASEBALL_TOTAL_LINE} line."),
            outcome(fid, fx["sport"], fx["name"], "Game total", f"Under {BASEBALL_TOTAL_LINE}", r["p_under"], src,
                    "official", "Complement of the over."),
        ]
        derivations[fid] = {
            "method": "independent Poisson on season runs scored and allowed per game, ties removed",
            "lambda_away": round(r["lam_away"], 3), "lambda_home": round(r["lam_home"], 3),
            "exp_total": round(r["exp_total"], 3), "log5_home": round(r["log5_home"], 4),
            "records": r["records"],
        }
        withheld.append({"fixture_id": fid, "sport": fx["sport"], "fixture": fx["name"],
                         "market": "Starting pitchers' form",
                         "reason": "Probable pitchers are named officially, but no season line for either "
                                   "was read this session, so no pitcher adjustment is applied.",
                         "source": "src-mlb-schedule"})

    # ---- URC: money line only ----------------------------------------------------------------
    margins = rugby_margins(inputs["urc"]["results"])
    league_totals = [hs + as_ for _h, hs, _a, as_, _d in inputs["urc"]["results"]]
    for fx in [f for f in fixtures if f["sport"] == "rugby-union"]:
        r = rugby_model(fx, margins)
        rows.append(outcome(fx["id"], fx["sport"], fx["name"], "Money line", f"{fx['home']} win",
                            r["p_home"], inputs["urc"]["source"], "official",
                            f"Form-only estimate: one confirmed Round 3 match per club, shrunk to "
                            f"{SHRINK_RUGBY:.2f}, plus a declared {HFA_RUGBY:.0f}-point home prior.",
                            {"exp_margin": round(r["exp_margin"], 2), "raw": round(r["raw_home"], 4),
                             "form_home": round(r["form_home"], 2), "form_away": round(r["form_away"], 2)}))
        rows.append(outcome(fx["id"], fx["sport"], fx["name"], "Money line", f"{fx['away']} win",
                            1 - r["p_home"], inputs["urc"]["source"], "official",
                            "Opposite side of the same estimate."))
        derivations[fx["id"]] = {
            "method": "shrunk single-round margin average plus declared home prior, normal CDF, capped",
            "exp_margin": round(r["exp_margin"], 2), "raw_home": round(r["raw_home"], 4),
            "cap_applied": abs(r["raw_home"] - r["p_home"]) > 1e-9,
            "league_mean_total": round(sum(league_totals) / len(league_totals), 2),
        }
        for mkt, why in (
            ("Handicap", "One confirmed match per club cannot support a fair points line; a line derived "
                         "from a single 42-point defeat would be an artefact of the sample, not evidence."),
            ("Match total", "The same single-round sample cannot separate a team total from the league "
                            "mean, so no over/under line is published."),
        ):
            withheld.append({"fixture_id": fx["id"], "sport": fx["sport"], "fixture": fx["name"],
                             "market": mkt, "reason": why, "source": inputs["urc"]["source"]})

    # ---- consensus rows: indicative only ------------------------------------------------------
    verified_ids = {f["olbg_event_id"]: f for f in fixtures if f.get("olbg_event_id")}
    for r in discovery:
        sel = r["olbg_pick"]
        base = {
            "fixture_id": f"ob-{r['sport']}-{r['olbg_event_id']}",
            "sport": r["sport"],
            "fixture": r["name"],
            "market": r["market"],
            "selection": sel,
            "source": "src-olbg-hubs",
            "class": "consensus",
            "olbg_event_id": r["olbg_event_id"],
            "url": r["url"],
            "olbg_time_text": r["olbg_time_text"],
            "olbg_tips": r["olbg_tips"],
        }
        if r["market"] in WIN_MARKETS:
            p = min(max(0.5 + SHRINK_CONS * (r["share"] - 0.5), 0.5), CAP_CONS)
            am = to_american(p)
            base.update({"p": round(p, 4), "decimal": fair_decimal(p), "american": am,
                         "american_text": fmt_american(am),
                         "in_band": BAND_LOW <= am <= BAND_HIGH, "tier": "Low",
                         "note": f"Indicative only: {r['tips'] if 'tips' in r else r['olbg_tips']} tips, "
                                 f"{r['share']*100:.0f}% of the vote on this selection, halved toward a "
                                 f"coin flip and capped at {CAP_CONS*100:.0f}%."})
            rows.append(base)
        else:
            withheld.append({
                "fixture_id": base["fixture_id"], "sport": r["sport"], "fixture": r["name"],
                "market": r["market"], "selection": sel,
                "reason": "A tip-vote share describes a selection inside a line the tipsters were given; "
                          "it cannot be turned into a fair handicap, total or set line without the "
                          "underlying scoring distribution, which no official page supplied.",
                "source": "src-olbg-hubs",
            })

    tiers = {}
    for x in rows:
        tiers[x["tier"]] = tiers.get(x["tier"], 0) + 1

    out_of_band = [x for x in rows if x["class"] == "official" and x["p"] >= 0.70 and not x["in_band"]]

    by_sport = {}
    for x in rows:
        by_sport.setdefault(x["sport"], []).append(x)
    top5 = {}
    for sport, xs in by_sport.items():
        xs = sorted(xs, key=lambda z: (-z["p"], z["fixture"]))
        top5[sport] = [{"fixture": z["fixture"], "selection": z["selection"], "p": z["p"],
                        "american_text": z["american_text"], "tier": z["tier"], "class": z["class"],
                        "source": z["source"], "market": z["market"]} for z in xs[:5]]

    payload = {
        "generated": "2026-10-23",
        "parameters": {"SIGMA_RUGBY": SIGMA_RUGBY, "HFA_RUGBY": HFA_RUGBY,
                       "SHRINK_RUGBY": SHRINK_RUGBY, "CAP_P": CAP_P, "SHRINK_CONS": SHRINK_CONS,
                       "CAP_CONS": CAP_CONS, "BAND": [BAND_LOW, BAND_HIGH],
                       "BASEBALL_TOTAL_LINE": BASEBALL_TOTAL_LINE},
        "rows": rows,
        "withheld": withheld,
        "derivations": derivations,
        "tier_counts": tiers,
        "class_counts": {c: sum(1 for x in rows if x["class"] == c) for c in ("official", "consensus")},
        "out_of_band": out_of_band,
        "top5": top5,
    }
    (DATA / "lines.json").write_text(json.dumps(payload, indent=1))
    print(f"priced={len(rows)} official={payload['class_counts']['official']} "
          f"consensus={payload['class_counts']['consensus']} withheld={len(withheld)} tiers={tiers}")
    for x in rows:
        if x["class"] == "official":
            print(f"  {x['sport']:11s} {x['market']:14s} {x['selection']:38s} p={x['p']:.3f} "
                  f"{x['american_text']:>6s} {x['tier']}")
    print("out_of_band:", [(x["selection"], x["american_text"]) for x in out_of_band])


if __name__ == "__main__":
    main()
