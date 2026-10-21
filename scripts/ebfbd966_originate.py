#!/usr/bin/env python3
"""Line origination engine — OUR OWN lines, built only from documented inputs.

Inputs (all recorded per match in data/matches.json):
  1. OLBG crowd signal: share of OLBG win tips on the most-tipped selection + sample size.
  2. Official ranking/seed gap, ONLY where encoded from a verified official source
     (PDC draw seeds, snooker world rankings alongside the WST draw, ICC ODI ratings).
  3. Structural home edge per league, from OLBG's own published league statistics where
     available (rugby union home-win rates), else a small fixed allowance.
  4. League scoring baselines for totals/handicaps from OLBG's published averages
     (rugby union, handball) or OLBG market standards (NHL puck line 1.5, MLB run line 1.5,
     darts total legs 9.5 in best-of-11). Where no published average was fetched, the
     baseline is tagged MODEL-BASELINE and flagged — it is our estimate, not a sourced fact.

No bookmaker odds are used anywhere: OLBG's odds columns were not present in the fetched
pages, and this project's brief is to originate independent lines. Fair odds = 1/p (no margin).

Formulas (identical wording on the site's Methodology page):
  Smoothed crowd share for the named side:  s = (tips_for + 2) / (tips_total + 4)
  Winner markets:        p_named starts at s.
  Directional markets (Set Betting / 1st Set / Set Score naming the eventual winner):
                         p_named = 0.5 + 0.5*(s - 0.5)   (half-strength)
  Handicap markets:      the backed 'plus' side is the underdog; favourite = other side.
                         p_fav from the backed line via the sport margin map, nudged by (s-0.5)*0.1.
                         A backed 'minus' side is the favourite, same map.
  Totals markets:        no winner signal (p starts 0.50); the crowd Over/Under becomes our total pick.
  Tie/Draw most-tipped:  no usable winner split -> p_home = 0.52 fallback, forced LOW (flagged in data).
  Ranking adjustment:    better-ranked side += min(12, 0.5 * |rank gap|) percentage points.
                         ICC ODI rating gap (Afghanistan v Bangladesh only): += 0.5pp per rating point, cap 6pp.
  Home adjustment:       league table below (percentage points to the true home side).
  Final p is capped to [0.52, 0.88] for the favourite. Pick = higher-p side.
  3-way sports: draw allowance d (Rugby Union 2.3% OLBG-published; Handball 9.0% from OLBG EHF CL
  tie rate 9.8%; Gaelic Football 8% MODEL) -> p_home3 = p_home*(1-d) etc.

Confidence (deterministic):
  HIGH  Path A: p>=0.70 AND tips_total>=6 AND winner market AND corroborating official gap agrees
                AND no conflict/contested flags.
        Path B: p>=0.80 AND official seed/rank gap >=11 (darts) / >=40 (snooker) AND directional
                agreement AND event VERIFIED AND no conflict/contested.
  MEDIUM: p>=0.60 with tips_total>=4, or p>=0.70 with tips_total>=2; no conflict/contested.
  LOW:    everything else. Forced LOW: signal conflicts, CONTESTED fixtures, Tie-most-tipped,
          unknown tip counts. NBA opening week can never exceed MEDIUM (no form base).
"""
import json, pathlib
from fractions import Fraction

ROOT = pathlib.Path(__file__).resolve().parent.parent
data = json.loads((ROOT/"data"/"ebfbd966_matches.json").read_text())

WINNER_MARKETS = {"Win Match","Money Line","To Win","Win Match 2-way"}
DIRECTIONAL = {"Set Betting","1st Set Winner","Set Score"}
US_AWAY_FIRST = {"NBA","NHL"}  # OLBG 'A @ B': B is home. MLB id BBA-01 handled explicitly.

HOME_PP = {  # percentage points to true home side
 ("Basketball","NBA"):2, ("Basketball","EuroLeague"):3, ("Basketball","EuroCup"):3,
 ("Basketball","Basketball Champions League"):3, ("Basketball","Korea KBL"):2,
 ("Ice Hockey","NHL"):2, ("Rugby Union","*"):4, ("Handball","*"):3, ("Volleyball","*"):2,
 ("Baseball","*"):2, ("Ice Hockey","*"):2,
}
DRAW_RATE = {"Rugby Union":0.023, "Handball":0.09, "Gaelic Football":0.08}

def home_pp(m):
    return HOME_PP.get((m["sport"], m["league"]), HOME_PP.get((m["sport"],"*"), 0))

def true_home_is_first(m):
    if m["id"]=="BBA-01": return False          # Rays @ Brewers
    if m["league"] in US_AWAY_FIRST: return False
    return True                                   # 'A vs B' / 'A v B': first-named at home

def frac(dec):
    f = Fraction(dec-1).limit_denominator(20)  # bookmaker-style small denominators (decimal is primary)
    return f"{f.numerator}/{f.denominator}"

def r5(x):  # round to nearest 0.5, min 0.5
    return max(0.5, round(x*2)/2)

def margin_to_p(sport, line):
    # inverse of handicap maps below; conservative
    k = {"Rugby Union":45,"Handball":16,"Gaelic Football":30,"Darts":11,"Ice Hockey":5}
    return 0.5 + line / k.get(sport, 20)

# expected-margin multipliers: margin = k*(p-0.5)
K_MARGIN = {"NBA":28,"EuroBasket":24,"Rugby Union":45,"Handball":16,"Tennis":12,"Gaelic Football":30}

def handicap_line(m, p_fav):
    s, lg = m["sport"], m["league"]
    if s=="Cricket": return (None, "n/a — no standard match handicap market (see note)")
    if s=="Ice Hockey": return (1.5, "OLBG market standard: puck line usually 1.5")
    if s=="Baseball": return (1.5, "OLBG market standard: run line usually 1.5")
    if s=="Darts": return (1.5 if p_fav<0.60 else 2.5 if p_fav<0.74 else 3.5 if p_fav<0.84 else 4.5, "Legs handicap steps for best-of-11 (OLBG guide: ±1.5 legs is the standard line)")
    if s=="Snooker": return (1.5 if p_fav<0.72 else 2.5, "Frame handicap for best-of-7 (OLBG: −1.5 = win by 2+ frames)")
    if s=="Volleyball": return (1.5 if p_fav<0.80 else 2.5, "Set handicap, best of 5")
    k = K_MARGIN["NBA"] if lg=="NBA" else K_MARGIN.get(s, K_MARGIN.get("EuroBasket") if s=="Basketball" else 20)
    if s=="Basketball" and lg!="NBA": k = 24
    unit = {"Basketball":"points","Rugby Union":"points","Handball":"goals","Tennis":"games","Gaelic Football":"points"}[s]
    return (r5(k*(p_fav-0.5)), f"Expected-margin map: {k} {unit} per unit of win probability (see Methodology)")

def total_line(m, p_fav):
    s, lg = m["sport"], m["league"]
    if s=="Cricket": return (None, None, "n/a — no standard match total market on OLBG")
    if s=="Rugby Union":
        base = 48.5 if "United Rugby" in lg else 49.5
        return (base, "Over" if 0.55<=p_fav<=0.75 else "Under", "OLBG-PUBLISHED-AVG (URC 48.9 / Top 14 49.7 avg total points, last 5 seasons)")
    if s=="Handball":
        womens = " W" in (m["home"]+m["away"]) or "(W)" in (m["home"]+m["away"])
        base = 55.5 if womens else 60.5
        src = "MODEL-BASELINE (women's/intl)" if womens else "OLBG-PUBLISHED-AVG (EHF CL men: 60.82 goals/game, last 5 editions)"
        return (base, "Over" if 0.55<=p_fav<=0.78 else "Under", src)
    if s=="Basketball":
        base = {"NBA":224.5,"EuroLeague":164.5,"EuroCup":160.5,"Basketball Champions League":160.5,"Korea KBL":158.5}[lg]
        return (base, "Over" if p_fav<0.68 else "Under", "MODEL-BASELINE — league-typical line; no official pace average fetched (flagged)")
    if s=="Ice Hockey":
        return (5.5, "Over" if p_fav<0.70 else "Under", "OLBG market context (5.5 is the line in OLBG's most-tipped NHL totals)" if lg=="NHL" else "MODEL-BASELINE")
    if s=="Baseball":
        return (7.5, "Under", "MODEL-BASELINE — World Series Game 1; starters unconfirmed (flagged)")
    if s=="Tennis":
        base = 22.5 if p_fav<0.62 else 20.5
        return (base, "Over" if p_fav<0.62 else "Under", "MODEL-BASELINE — total games, best of 3 (OLBG example line: 20.5)")
    if s=="Darts":
        return (9.5, "Over" if p_fav<0.68 else "Under", "OLBG-MARKET-STANDARD — best-of-11 legs, line 9.5 (OLBG darts guide)")
    if s=="Snooker":
        return (5.5, "Over" if p_fav<0.68 else "Under", "MODEL-BASELINE — total frames, best of 7")
    if s=="Volleyball":
        return (3.5, "Over" if p_fav<0.70 else "Under", "MODEL-BASELINE — total sets, best of 5 (OLBG lists no totals market)")
    if s=="Gaelic Football":
        return (40.5, "Over" if p_fav<0.68 else "Under", "MODEL-BASELINE — total points; no published average fetched (flagged)")
    return (None, None, "n/a")

def side_of_selection(m):
    """Return ('H'|'A'|None, kind) for the most-tipped selection."""
    sel = m["olbg_selection"]
    if sel in ("Tie","Draw"): return (None, "tie")
    if m["olbg_market"] in ("Total Legs","Game Totals"): return (None, "total")
    # strip scoreline/handicap suffixes for matching
    base = sel
    for suf in (" to win 2-1"," to win 2-0"," to win 3-0"," +1.50"," -1.50"," +3.50"," +18.50"," +11.50"," +28.50"," +10.50"," +23.50"," -3.50"," -2.50"):
        base = base.replace(suf,"")
    base = base.replace("(W)","W").strip()
    h = m["home"].replace("(W)","W"); a = m["away"].replace("(W)","W")
    if base==h: return ("H","side")
    if base==a: return ("A","side")
    return (None,"unknown")

def originate(m):
    flags_extra = []
    tf, tt = m.get("tips_for"), m.get("tips_total")
    side, kind = side_of_selection(m)
    pH = 0.50
    crowd_note = "no usable crowd signal"
    if tf is not None and tt:
        s = (tf+2)/(tt+4)
        if kind=="side" and m["olbg_market"] in WINNER_MARKETS:
            pH = s if side=="H" else 1-s
            crowd_note = f"winner market: smoothed crowd share s={s:.3f} for {'home/first' if side=='H' else 'away/second'}"
        elif kind=="side" and m["olbg_market"] in DIRECTIONAL:
            p_named = 0.5 + 0.5*(s-0.5)
            pH = p_named if side=="H" else 1-p_named
            crowd_note = f"directional market ({m['olbg_market']}): half-strength s={s:.3f}"
        elif kind=="side" and "Handicap" in m["olbg_market"] or (kind=="side" and m["olbg_market"]=="Puck Line"):
            import re
            mm = re.search(r"([+-])(\d+\.\d+)", m["olbg_selection"])
            line = float(mm.group(2)) if mm else 1.5
            sign = mm.group(1) if mm else "+"
            p_fav = margin_to_p(m["sport"], line) + (s-0.5)*0.1
            fav_is_named = (sign=="-")
            named_p = p_fav if fav_is_named else 1-p_fav
            pH = named_p if side=="H" else 1-named_p
            crowd_note = f"handicap market: backed {m['olbg_selection']} -> implied favourite p={p_fav:.3f}"
        elif kind=="tie":
            pH = 0.52
            crowd_note = "Tie most-tipped: 0.52 home fallback (flagged)"
        elif kind=="total":
            crowd_note = f"totals market only ({m['olbg_selection']}): winner starts 0.50"
    # ranking adjustment
    rank_note, gap = "", None
    sh, sa = m.get("seed_home"), m.get("seed_away")
    if sh and sa:
        gap = abs(sh-sa)
        adj = min(0.12, 0.005*gap)
        if sh<sa: pH += adj; rank_note=f"ranking adj +{adj*100:.1f}pp to {m['home']} (#{sh} v #{sa})"
        else: pH -= adj; rank_note=f"ranking adj +{adj*100:.1f}pp to {m['away']} (#{sa} v #{sh})"
    if m["id"]=="CRI-01":  # ICC ODI ratings AFG 92 vs BAN 82
        pH += 0.05; gap = 10; rank_note="ICC ODI rating adj +5.0pp to Afghanistan (92 v 82)"
    # home adjustment
    pp = home_pp(m)
    if pp:
        pH += (pp/100) if true_home_is_first(m) else -(pp/100)
    pH = max(0.12, min(0.88, pH))
    if pH==0.50: pH = 0.52  # documented first-named lean on exact coin flips
    fav_is_home = pH >= 0.5
    p_fav = max(pH, 1-pH); p_fav = max(0.52, min(0.88, p_fav))
    pick = m["home"] if fav_is_home else m["away"]
    dog = m["away"] if fav_is_home else m["home"]
    # conflict detection: crowd side vs ranking side
    conflict = any("IRREGULARITY" in f for f in m.get("flags",[]))
    rank_agrees = None
    if sh and sa:
        rank_pick_home = sh<sa
        rank_agrees = (rank_pick_home==fav_is_home)
        if side in ("H","A") and m["olbg_market"] in WINNER_MARKETS:
            crowd_home = (side=="H")
            if crowd_home != rank_pick_home and gap>=5:
                conflict = True
                flags_extra.append("Model note: OLBG crowd majority and the official seeding/ranking gap point to different winners — forced LOW.")
    corroborated = bool((sh and sa and rank_agrees) or m["id"]=="CRI-01")
    # confidence
    forced_low = conflict or m.get("verification")=="CONTESTED" or kind=="tie" or tf is None
    pathB = (p_fav>=0.80 and gap is not None and ((m["sport"]=="Darts" and gap>=11) or (m["sport"]=="Snooker" and gap>=40))
             and m.get("verification")=="VERIFIED" and rank_agrees)
    if not forced_low and ((p_fav>=0.70 and (tt or 0)>=6 and m["olbg_market"] in WINNER_MARKETS and corroborated) or pathB):
        conf = "HIGH"
    elif not forced_low and ((p_fav>=0.60 and (tt or 0)>=4) or (p_fav>=0.70 and (tt or 0)>=2)):
        conf = "MEDIUM"
    else:
        conf = "LOW"
    if m["league"]=="NBA" and conf=="HIGH": conf="MEDIUM"  # opening-week cap (documented)
    # markets
    hline, hnote = handicap_line(m, p_fav)
    hpick = None
    if hline is not None:
        hpick = f"{pick} -{hline}" if p_fav>=0.62 else f"{dog} +{hline}"
    tline, tpick_dir, tsrc = total_line(m, p_fav)
    # crowd total override
    if kind=="total" and m["olbg_selection"].startswith(("Over","Under")):
        tpick_dir = m["olbg_selection"].split()[0]
        import re
        mm = re.search(r"(\d+\.\d+)", m["olbg_selection"])
        if mm: tline = float(mm.group(1))
        tsrc += " | Direction follows OLBG crowd total selection."
    tpick = f"{tpick_dir} {tline}" if tline is not None else None
    d = DRAW_RATE.get(m["sport"])
    probs = {"pick": round(p_fav,3), "other": round(1-p_fav,3)}
    if d:
        probs = {"home": round(pH*(1-d),3), "draw": d, "away": round((1-pH)*(1-d),3),
                 "pick": round(p_fav*(1-d),3), "other": round((1-p_fav)*(1-d),3)}
    fp = probs["pick"]; fo = probs["other"]
    return {
      "id": m["id"], "pick": pick, "pick_prob": fp, "other_prob": fo,
      "draw_prob": (d if d else None),
      "fair_decimal_pick": round(1/fp,2), "fair_decimal_other": round(1/fo,2),
      "fair_fractional_pick": frac(1/fp), "fair_fractional_other": frac(1/fo),
      "handicap_line": hline, "handicap_pick": hpick, "handicap_basis": hnote,
      "total_line": tline, "total_pick": tpick, "total_basis": tsrc,
      "confidence": conf,
      "derivation": " | ".join(x for x in [crowd_note, rank_note, (f"home adj {pp:+d}pp" if pp else ""), f"p(favourite)={p_fav:.3f}"] if x),
      "extra_flags": flags_extra,
    }

lines = {m["id"]: originate(m) for m in data["matches"]}
(ROOT/"data"/"ebfbd966_lines.json").write_text(json.dumps({"meta":{"generated_from":"data/ebfbd966_matches.json + scripts/ebfbd966_originate.py","harvest_date":data["meta"]["harvest_date"]},"lines":lines}, indent=1, ensure_ascii=False))
from collections import Counter
print(Counter(v["confidence"] for v in lines.values()))
print("HIGH:", [k for k,v in lines.items() if v["confidence"]=="HIGH"])
for k,v in lines.items():
    if v["confidence"]=="HIGH": print(k, v["pick"], v["pick_prob"], v["derivation"])
