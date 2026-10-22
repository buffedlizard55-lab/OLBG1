"""Originate transparent experimental fair lines for the fresh 2aeea682 desk.

No bookmaker quote, availability, edge or calibrated forecast is claimed. The only
priced fixtures are those with paired official inputs read in this session:
MLB games 1-4 (regular-season run rates) and three EuroLeague games (records).
"""
from __future__ import annotations
import csv
import json
import math
from collections import Counter
from pathlib import Path
import s2aeea682_data as D

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "2aeea682"
HIGH_FLOOR = 0.70
SHORT = -250.0
LONG = 10000.0


def american_exact(p: float) -> float:
    return -100.0 * p / (1.0 - p) if p >= 0.5 else 100.0 * (1.0 - p) / p


def in_window(p: float) -> bool:
    return SHORT <= american_exact(p) <= LONG


def outcome(selection: str, p: float, **extra):
    dec = 1.0 / p
    row = {"selection": selection, "probability_exact": p, "probability": round(p, 6),
           "fair_decimal": round(dec, 4), "fair_american": round(american_exact(p)),
           "fair_american_exact": american_exact(p), "in_brief_window": in_window(p)}
    row.update(extra)
    return row


def market(fixture, family, name, model, inputs, outcomes, **extra):
    assert abs(sum(o["probability_exact"] for o in outcomes) - 1.0) < 1e-8, (fixture["id"], name)
    number = 1 + len(fixture["markets"])
    row = {"id": f"{fixture['id']}#m{number}", "family": family, "market": name,
           "model": model, "inputs": inputs, "outcomes": outcomes,
           "source_id": fixture["source_id"], "official_link": fixture["official_link"]}
    row.update(extra)
    fixture["markets"].append(row)
    return row


def poisson_pmf(lam, n):
    return math.exp(-lam) * lam ** n / math.factorial(n)


def grid(la, lb, cap=40):
    a = [poisson_pmf(la, n) for n in range(cap + 1)]
    b = [poisson_pmf(lb, n) for n in range(cap + 1)]
    z = sum(a) * sum(b)
    return [[a[i] * b[j] / z for j in range(cap + 1)] for i in range(cap + 1)]


def total_over(lam, half_line):
    probs = [poisson_pmf(lam, n) for n in range(61)]
    z = sum(probs)
    return sum(p for n, p in enumerate(probs) if n > half_line) / z


def mlb_lines(f):
    away, home = D.MLB_TEAMS[f["away_code"]], D.MLB_TEAMS[f["home_code"]]
    ga, gh = away["w"] + away["l"], home["w"] + home["l"]
    la = ((away["rs"] / ga) + (home["ra"] / gh)) / 2.0
    lb = ((home["rs"] / gh) + (away["ra"] / ga)) / 2.0
    g = grid(la, lb)
    cap = len(g) - 1
    pa9 = sum(g[i][j] for i in range(cap + 1) for j in range(cap + 1) if i > j)
    pb9 = sum(g[i][j] for i in range(cap + 1) for j in range(cap + 1) if j > i)
    tie = 1.0 - pa9 - pb9
    pa = pa9 + tie * la / (la + lb)
    pb = 1.0 - pa
    inputs = (f"MLB official 2026 regular-season totals: {away['name']} {away['rs']} RS/{away['ra']} RA in {ga} games; "
              f"{home['name']} {home['rs']} RS/{home['ra']} RA in {gh} games. Rates are averaged; no pitcher, park, lineup or postseason adjustment.")
    model = "mlb-independent-poisson-v1"
    market(f,"winner","Match winner (including extra innings)",model,inputs,
           [outcome(away["name"],pa),outcome(home["name"],pb)])
    market(f,"regulation","Result after nine innings (3-way)",model,inputs,
           [outcome(away["name"]+" nine-inning win",pa9),outcome("Tie after nine innings",tie),outcome(home["name"]+" nine-inning win",pb9)])
    for line in (1.5,2.5):
        pa_cover = sum(g[i][j] for i in range(cap+1) for j in range(cap+1) if i-j > line)
        pb_cover = sum(g[i][j] for i in range(cap+1) for j in range(cap+1) if j-i > line)
        market(f,"run-line",f"Run line {away['name']} -{line} / {home['name']} +{line}",model,inputs,
               [outcome(f"{away['name']} -{line}",pa_cover),outcome(f"{home['name']} +{line}",1-pa_cover)])
        market(f,"run-line",f"Run line {away['name']} +{line} / {home['name']} -{line}",model,inputs,
               [outcome(f"{away['name']} +{line}",1-pb_cover),outcome(f"{home['name']} -{line}",pb_cover)])
    for line in (6.5,7.5,8.5,9.5,10.5,11.5):
        p_over = sum(g[i][j] for i in range(cap+1) for j in range(cap+1) if i+j > line)
        market(f,"total",f"Match total {line} runs",model,inputs,
               [outcome(f"Over {line}",p_over),outcome(f"Under {line}",1-p_over)])
    for line in (9,10,11):
        under = sum(g[i][j] for i in range(cap+1) for j in range(cap+1) if i+j < line)
        push = sum(g[i][j] for i in range(cap+1) for j in range(cap+1) if i+j == line)
        over = 1.0-under-push
        denom = under+over
        market(f,"asian-total",f"Match total {line} runs (exactly {line} refunded)",model,inputs,
               [outcome(f"Under {line} runs (push refunded at {line})",under/denom),
                outcome(f"Over {line} runs (push refunded at {line})",over/denom)],
               push_probability=push,price_basis="probabilities conditional on the total not landing exactly on the integer")
    for code,team,lam in ((f["away_code"],away,la),(f["home_code"],home,lb)):
        for line in (3.5,4.5,5.5):
            p_over = total_over(lam,line)
            market(f,"team-total",f"{team['name']} team total {line} runs",model,inputs,
                   [outcome(f"{team['name']} over {line}",p_over),outcome(f"{team['name']} under {line}",1-p_over)])
    f["model_detail"] = {"lambda_away":la,"lambda_home":lb,"expected_total":la+lb,
                         "away_code":f["away_code"],"home_code":f["home_code"]}
    f["winner_pick"] = pick_from_winner(f)
    return f


def shrunk_log5(a,b):
    pa = (a["w"]+2.0)/(a["w"]+a["l"]+4.0)
    pb = (b["w"]+2.0)/(b["w"]+b["l"]+4.0)
    p = (pa-pa*pb)/(pa+pb-2*pa*pb)
    return p,pa,pb


def euro_lines(f):
    away,home = D.EUROLEAGUE[f["away_code"]],D.EUROLEAGUE[f["home_code"]]
    pa,sa,sb = shrunk_log5(away,home)
    inputs = (f"Official EuroLeague Round 7 records: {away['name']} {away['w']}-{away['l']}; "
              f"{home['name']} {home['w']}-{home['l']}. Beta(2,2) shrinkage then log5; no home advantage.")
    market(f,"winner","Match winner","euroleague-log5-v1",inputs,
           [outcome(away["name"],pa),outcome(home["name"],1-pa)])
    f["model_detail"] = {"shrunk_away_rate":sa,"shrunk_home_rate":sb}
    f["winner_pick"] = pick_from_winner(f)
    return f


def pick_from_winner(f):
    m = f["markets"][0]
    best = max(m["outcomes"],key=lambda o:o["probability_exact"])
    p = best["probability_exact"]
    tied = abs(m["outcomes"][0]["probability_exact"] - m["outcomes"][1]["probability_exact"]) < 1e-12
    if p > HIGH_FLOOR and best["in_brief_window"]:
        tier = "High"
        reason = "winner passes >70% and the fair-price window"
    elif p >= 0.55 or (p > 250/350 and not best["in_brief_window"]):
        tier = "Medium"
        reason = ("winner has a model lean but its fair price is outside -250…+10000" if not best["in_brief_window"]
                  else "winner has a model lean but does not exceed 70%")
    else:
        tier = "Low"
        reason = "winner probability is below 55%; no strong evidence-backed lean"
    if tied:
        tier = "Low"
        reason = "identical shrunk records produce 50.00% on both sides; no team is selected"
    return {"market_id":m["id"],"selection":"No winner preference" if tied else best["selection"],"tier":tier,"reason":reason,**{k:best[k] for k in ("probability","probability_exact","fair_decimal","fair_american","fair_american_exact","in_brief_window")}}


def select_high_candidates(fixtures):
    """Publish every qualifying outcome as a candidate; feature the strongest per fixture.

    The featured High set is therefore deterministic, not chosen to fill a quota.
    Other qualifying outcomes stay visible on the markets page as alternates.
    """
    featured = []
    for f in fixtures:
        candidates = []
        for m in f["markets"]:
            for o in m["outcomes"]:
                if o["probability_exact"] > HIGH_FLOOR and o["in_brief_window"]:
                    candidate = {"fixture_id":f["id"],"market_id":m["id"],"sport":f["sport"],
                                 "market":m["market"],"selection":o["selection"],
                                 "probability":o["probability"],"probability_exact":o["probability_exact"],
                                 "fair_decimal":o["fair_decimal"],"fair_american":o["fair_american"],
                                 "fair_american_exact":o["fair_american_exact"],"official_link":f["official_link"],
                                 "source_id":m["source_id"]}
                    candidates.append(candidate)
                    f["high_candidates"].append(candidate)
        if candidates:
            best = max(candidates,key=lambda c:c["probability_exact"])
            best = dict(best)
            best["tier"] = "High"
            best["prediction_required"] = True
            f["featured_high"] = best
            featured.append(best)
        else:
            f["featured_high"] = None
    return featured


def unpriced_reason(f):
    if f["sport"] == "baseball" and f.get("if_necessary") == "Y":
        return "MLB marks this game ifNecessary=Y; all prices and winner preference are withheld."
    reasons = {
        "ice-hockey":"Current paired NHL team-stat rows were not transcribed for every club in this fresh pass; no inherited ratings are reused.",
        "tennis":"Official order of play supplies participants only; no paired official ranking/form input was read.",
        "rugby-league":"Official fixture list supplies no paired form or rating input; clock timezone is also unstated.",
        "cricket":"Official tournament page supplies date and ground but no start time or paired current rating.",
        "snooker":"Official scheduled matches are confirmed, but no fresh paired ranking/form input was transcribed.",
        "rugby-union":"Official fixtures and some team sheets are confirmed, but team sheets alone are not a calibrated rating input.",
        "handball":"Official pairings are confirmed, but no paired EHF rating/form input was transcribed.",
        "motor-racing":"Event-only card; no full-field driver rating or pre-event market is originated after sessions have begun.",
    }
    return reasons.get(f["sport"],"No compatible official statistical input was read.")


def build():
    fixtures = []
    for original in D.FIXTURES:
        f = dict(original)
        f["sport_name"] = D.SPORT_NAMES[f["sport"]]
        f["markets"] = []
        f["winner_pick"] = None
        f["high_candidates"] = []
        f["featured_high"] = None
        f["verification"] = "official-fields-verified"
        f["priced"] = False
        f["unpriced_reason"] = None
        if f["sport"] == "baseball" and f.get("if_necessary") == "N":
            mlb_lines(f)
            f["priced"] = True
        elif f["sport"] == "basketball":
            euro_lines(f)
            f["priced"] = True
        else:
            f["unpriced_reason"] = unpriced_reason(f)
        fixtures.append(f)
    featured = select_high_candidates(fixtures)
    return fixtures,featured


def counts(fixtures,featured,predictions):
    c = Counter()
    per = {}
    for f in fixtures:
        p = per.setdefault(f["sport"],{"name":f["sport_name"],"fixtures":0,"priced":0,"markets":0,"high":0,"medium":0,"low":0,"unpriced":0})
        p["fixtures"] += 1
        c["fixtures"] += 1
        if f["priced"]:
            p["priced"] += 1
            c["priced"] += 1
        else:
            p["unpriced"] += 1
            c["unpriced"] += 1
        p["markets"] += len(f["markets"])
        c["markets"] += len(f["markets"])
        c["outcomes"] += sum(len(m["outcomes"]) for m in f["markets"])
        c["high_candidates"] += len(f["high_candidates"])
        if f["winner_pick"]:
            tier = f["winner_pick"]["tier"].lower()
            p[tier] += 1
            c["winner_"+tier] += 1
    c["featured_high"] = len(featured)
    c["predictions"] = len(predictions)
    c["sports_with_fixtures"] = len(per)
    c["sports_covered_by_pages"] = len(D.SPORTS)
    return dict(c),per


def write_csv(desk):
    with (OUT/"fixtures.csv").open("w",newline="",encoding="utf-8") as fh:
        fields = ["fixture_id","sport","competition","side_a","side_b","date","start_utc","display_time","timezone","venue","status","priced","winner_selection","winner_probability","winner_fair_american","winner_tier","featured_high_selection","featured_high_probability","featured_high_american","unpriced_reason","official_source","blank_fields"]
        w = csv.DictWriter(fh,fieldnames=fields); w.writeheader()
        for f in desk["fixtures"]:
            wp = f["winner_pick"] or {}
            hp = f["featured_high"] or {}
            w.writerow({"fixture_id":f["id"],"sport":f["sport"],"competition":f["competition"],"side_a":f["side_a"] or "","side_b":f["side_b"] or "","date":f["date"],"start_utc":f["start_utc"] or "","display_time":f["display_time"] or "","timezone":f["timezone"] or "","venue":f["venue"] or "","status":f["status"],"priced":"yes" if f["priced"] else "no","winner_selection":wp.get("selection",""),"winner_probability":wp.get("probability",""),"winner_fair_american":wp.get("fair_american",""),"winner_tier":wp.get("tier",""),"featured_high_selection":hp.get("selection",""),"featured_high_probability":hp.get("probability",""),"featured_high_american":hp.get("fair_american",""),"unpriced_reason":f["unpriced_reason"] or "","official_source":f["official_link"],"blank_fields":";".join(f["blank_fields"])})
    with (OUT/"markets.csv").open("w",newline="",encoding="utf-8") as fh:
        fields = ["fixture_id","sport","market_id","market","family","model","selection","probability","fair_decimal","fair_american","in_brief_window","featured_high","official_source"]
        w = csv.DictWriter(fh,fieldnames=fields); w.writeheader()
        for f in desk["fixtures"]:
            for m in f["markets"]:
                for o in m["outcomes"]:
                    featured = bool(f["featured_high"] and f["featured_high"]["market_id"] == m["id"] and f["featured_high"]["selection"] == o["selection"])
                    w.writerow({"fixture_id":f["id"],"sport":f["sport"],"market_id":m["id"],"market":m["market"],"family":m["family"],"model":m["model"],"selection":o["selection"],"probability":o["probability"],"fair_decimal":o["fair_decimal"],"fair_american":o["fair_american"],"in_brief_window":"yes" if o["in_brief_window"] else "no","featured_high":"yes" if featured else "no","official_source":f["official_link"]})


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    fixtures,featured = build()
    import s2aeea682_predictions as P
    predictions = P.attach(fixtures,featured)
    c,per = counts(fixtures,featured,predictions)
    coverage = []
    for slug,name,olbg_id,route in D.SPORTS:
        coverage.append({"sport":slug,"name":name,"olbg_id":olbg_id,
                         "olbg_hub":f"https://www.olbg.com/betting-tips/{route}/{olbg_id}",
                         "note":D.COVERAGE_NOTES[slug],**per.get(slug,{"fixtures":0,"priced":0,"markets":0,"high":0,"medium":0,"low":0,"unpriced":0})})
    desk = {"schema_version":1,"session":D.SESSION,"task":D.TASK,"read_at_utc":D.READ_AT_UTC,
            "window":{"from_utc":D.READ_AT_UTC,"until_utc":D.WINDOW_UNTIL_UTC,"note":"Source-specific coverage limits are published; not a worldwide complete fixture census."},
            "excluded_sports":D.EXCLUDED,"confidence_policy":{"high":"p > 0.70 AND unrounded fair American price within -250…+10000; strongest qualifying outcome per priced fixture is featured; every featured High requires unique >=30-word evidence-bounded prose.","winner_tiers":"Winner preference is separately labelled Low/Medium/High. Medium includes strong favourites whose prices are outside the brief window.","prices":"Experimental zero-margin fair estimates only; not bookmaker quotes or availability.","high_candidates":"All qualifying outcomes remain visible; only the strongest per fixture receives featured prose to avoid repetitive bulk writing."},
            "counts":c,"fixtures":fixtures,"featured_high":featured,"predictions":predictions,
            "sources":D.SOURCES,"coverage":coverage,"market_investigation":D.MARKET_INVESTIGATION,
            "mlb_teams":D.MLB_TEAMS,"euroleague_teams":D.EUROLEAGUE,"euroleague_context":D.EURO_CONTEXT}
    with (OUT/"desk.json").open("w",encoding="utf-8") as fh:
        json.dump(desk,fh,ensure_ascii=False,indent=1); fh.write("\n")
    write_csv(desk)
    problems = P.check(desk)
    if problems:
        raise SystemExit("Prediction checks failed:\n - "+"\n - ".join(problems))
    print(json.dumps(c,indent=2,sort_keys=True))
    for h in featured:
        print("HIGH",h["fixture_id"],h["selection"],f"{h['probability']:.6f}",h["fair_american"])

if __name__ == "__main__":
    main()
