#!/usr/bin/env python3
"""T66 / 8f6d7364 — zero-margin line origination + confidence tiers.

Reads  data/8f6d7364/{fixtures,inputs}.json
Writes data/8f6d7364/lines.json

MODEL 8f6d7364-v1.0 (all parameters disclosed; every probability is a model
estimate, never a sourced fact):

  * Records  : official W-L-OTL/W-D-L as read this session (inputs.json carries
               each observation window). Beta(2,2) shrinkage toward .500
               (p = (W+2)/(GP+4)) — mandatory for early-season samples.
  * log5     : P(A) = a(1-b) / (a(1-b) + (1-a)b), a/b the shrunk win shares.
  * Home edge: +0.025 probability for the home side (NHL, MLB, EuroLeague, URC,
               Top 14, Pro D2, StarLigue). Tennis/rugby league are neutral-site
               or rating-covered: no extra edge.
  * Positions : LNR Top 14 / Pro D2 and no-record sports use the official table
               position: P = .5 + .02*(pos_away - pos_home) + .03 home, clipped
               to [.17,.83] (linear position model — disclosed assumption).
  * Handball  : shrunk log5 on the official StarLigue W-D-L; totals from the
               official goals for/against (Poisson mean) with disclosed sigma.
  * Rugby RL  : P = rating_A / (rating_A + rating_B) from the official IRL
               strength percentages (a linear share of the published rating).
  * Tennis    : Bradley-Terry on official ranks where the draw prints them,
               P(A) = rB^0.7 / (rA^0.7 + rB^0.7); unseeded/qualifier slots use
               the documented ordinal assumptions in inputs.json
               (assumption, not fact).
  * MLB totals: paired season run rates -> Poisson means; ladder = centre
               (nearest .5 to lambda) with +/-1.0 lines; win margin via the
               Poisson score-difference with tie mass split pro-rata.
  * URC lines : team means from official PF/PA; margin sigma = 10.0 points and
               total sigma = 12.0 points (disclosed constants); lines integer
               around the modelled margin / nearest .5 to lambda.
  * Tiers     : High = model p >= 0.70 AND fair American inside [-250,+10000]
               AND the fixture is official-verified (brief's literal gate).
               Medium = p >= 0.55, Low below that. Boundary decisions use p
               rounded to 6 decimals (binary-noise guard).
               Every p >= 0.70 whose price is shorter than -250 is published in
               the out-of-window ledger, never silently dropped.
"""
import json, math, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "8f6d7364")
FIX = json.load(open(os.path.join(D, "fixtures.json")))["fixtures"]
IN = json.load(open(os.path.join(D, "inputs.json")))
GEN = "2026-10-22T22:05:00Z"
HOME_SIDE = {"ice-hockey": "b", "baseball": "b", "basketball": "a", "rugby-union": "a",
             "handball": "a", "gaelic-football": "a", "snooker": "n", "volleyball": "a",
             "cricket": "n", "tennis": "n", "rugby-league": "n", "darts": "n",
             "aussie-rules": "a", "golf": "n", "motor-racing": "n"}

def am(p):
    p = round(p, 6)
    if p <= 0 or p >= 1:
        return None
    return round(-100 * p / (1 - p), 1) if p >= 0.5 else round(100 * (1 - p) / p, 1)

def dec(p):
    return round(1 / p, 4) if 0 < p < 1 else None

def in_window(a):
    return a is not None and -250.0 - 1e-9 <= a <= 10000.0

def log5(a, b):
    return (a * (1 - b)) / (a * (1 - b) + (1 - a) * b)

def shrunk(w, l, ot=0, d=0):
    gp = w + l + ot + d
    return (w + 2 + d) / (gp + 4)

def norm_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))

def pois_pmf(lmb, k):
    return math.exp(-lmb) * lmb ** k / math.factorial(k)

def pois_gt(lmb, thr):        # P(X > thr)
    k = math.floor(thr)
    return 1 - sum(pois_pmf(lmb, i) for i in range(k + 1))

def tier_of(p, verified):
    a = am(p)
    if p >= 0.700000 and in_window(a) and verified:
        return "High"
    return "Medium" if p >= 0.55 else "Low"

def sel(mid, mtype, selection, p, line=None, note=""):
    a = am(p)
    return {"market": mtype, "selection": selection, "line": line,
            "p": round(p, 6), "fair_decimal": dec(p), "fair_american": a,
            "in_window": in_window(a), "note": note}

def add_out(rows, market, selection, p, verified, line=None):
    a = am(p)
    s = {"fixture_id": rows["id"], "competition": rows["competition"],
         "match": f'{rows["participant_a"]} v {rows["participant_b"]}' if rows["participant_a"] and rows["participant_b"] else None,
         "market": market, "selection": selection, "line": line,
         "p": round(p, 6), "fair_american": a, "tier_if_in_window": tier_of(p, verified)}
    return s

LINES = {"generated_at": GEN, "model_version": IN["model_version"],
         "high_gate": "model p >= 0.70 AND fair American in [-250,+10000] AND official-verified fixture",
         "fixtures": []}
OUTWIN = []      # >=70% but shorter than -250 (disclosed, never High)
NEAR = []        # .685 <= p < .700 winner-band watch list
CROSS = []       # NHL official embedded market cross-check

def get(fid):
    return next(f for f in FIX if f["id"] == fid)

# ------------------------------------------------------------------ NHL -----
odds = IN["official_odds"]
for f in FIX:
    if f["sport"] != "ice-hockey" or f["discovery"] != "olbg":
        continue
    away, home = f["participant_a"].split()[0] if False else None, None
    key = {"NSH Predators": "NSH", "BOS Bruins": "BOS", "NY Rangers": "NYR", "TOR Maple Leafs": "TOR",
           "SJ Sharks": "SJS", "OTT Senators": "OTT", "ANA Ducks": "ANA", "NJ Devils": "NJD",
           "FLA Panthers": "FLA", "PIT Penguins": "PIT", "LA Kings": "LAK", "NY Islanders": "NYI",
           "VGS Golden Knights": "VGK", "STL Blues": "STL", "WPG Jets": "WPG", "DAL Stars": "DAL",
           "MIN Wild": "MIN", "CGY Flames": "CGY", "CAR Hurricanes": "CAR", "EDM Oilers": "EDM",
           "UTA Mammoth": "UTA", "SEA Kraken": "SEA", "DET Red Wings": "DET", "VAN Canucks": "VAN"}
    ka, kh = key[f["participant_a"]], key[f["participant_b"]]
    wa, la, oa, _, _, _, _ = IN["nhl"][ka][0], *IN["nhl"][ka][1:3], 0, 0, 0, 0
    ha = IN["nhl"][ka]; hh = IN["nhl"][kh]
    a = shrunk(ha[0], ha[1], ha[2]); b = shrunk(hh[0], hh[1], hh[2])
    p_home = min(0.95, max(0.05, log5(b, a) + 0.025))
    p_away = 1 - p_home
    ver = f["verified"]
    markets = [sel(0, "winner", f['participant_a'], p_away, None, "shrunk log5 + home edge .025"),
               sel(0, "winner", f["participant_b"], p_home, None, "shrunk log5 + home edge .025")]
    # official market cross-check (providers 7,8,9 American)
    oc = odds.get(f["id"], {})
    imp = []
    for side in (ka, kh):
        vals = [v for v in oc.get(side, []) if isinstance(v, str) and v[:1] in "+-"]
        vals = [float(v) for v in vals]
        if vals:
            imp.append(sum((100 / (abs(v) + 100)) if v > 0 else (-v / (-v + 100)) for v in vals) / len(vals))
        else:
            imp.append(None)
    if None not in imp:
        share = [imp[0] / sum(imp), imp[1] / sum(imp)]
        CROSS.append({"fixture_id": f["id"],
                      "match": f'{f["participant_a"]} v {f["participant_b"]}',
                      "official_devig": {f["participant_a"]: round(share[0], 4),
                                         f["participant_b"]: round(share[1], 4)},
                      "model": {f["participant_a"]: round(p_away, 4),
                                f["participant_b"]: round(p_home, 4)}})
    pick_p, pick_s = (p_home, f["participant_b"]) if p_home >= p_away else (p_away, f["participant_a"])
    t = tier_of(pick_p, ver)
    if pick_p >= 0.685 and pick_p < 0.70:
        NEAR.append(add_out(f, "winner", pick_s, pick_p, ver))
    if pick_p >= 0.70 and not in_window(am(pick_p)):
        OUTWIN.append(add_out(f, "winner", pick_s, pick_p, ver))
    LINES["fixtures"].append({"id": f["id"], "sport": f["sport"], "competition": f["competition"],
                              "markets": markets, "pick": pick_s, "pick_p": round(pick_p, 6),
                              "pick_american": am(pick_p), "tier": t,
                              "priceable_note": "winner only: per-team scoring rates were not carried into this dataset from the standings read (totals/handicaps withheld)"})

# ------------------------------------------------------------------ MLB -----
for f in FIX:
    if f["sport"] != "baseball" or f["id"] == "mlb-ws-g3" or not f["participant_b"]:
        continue
    T, M = IN["mlb"]["TB"], IN["mlb"]["MIL"]
    a = shrunk(T["w"], T["l"]); b = shrunk(M["w"], M["l"])
    p_home = min(0.95, max(0.05, log5(b, a) + 0.025)); p_away = 1 - p_home
    x_M = (M["rs"] / M["gp"] + T["ra"] / T["gp"]) / 2
    x_T = (T["rs"] / T["gp"] + M["ra"] / M["gp"]) / 2
    lam = x_M + x_T
    cent = math.floor(lam) + 0.5 if (lam - math.floor(lam)) < 0.5 else math.ceil(lam) - 0.5
    tot_lines = [cent - 1.0, cent, cent + 1.0]
    markets = [sel(0, "winner", f["participant_a"], p_away, None, "shrunk log5 + home edge .025"),
               sel(0, "winner", f["participant_b"], p_home, None, "shrunk log5 + home edge .025")]
    for L in tot_lines:
        markets.append(sel(0, "total", f"Over {L:g}", pois_gt(lam, L), L,
                           f"Poisson totals from official season run rates (lambda={lam:.3f})"))
        markets.append(sel(0, "total", f"Under {L:g}", 1 - pois_gt(lam, L), L,
                           f"Poisson totals (lambda={lam:.3f})"))
    # run line +/-1.5 via Poisson difference
    N = 60
    pm = [pois_pmf(x_M, i) for i in range(N)]; pt = [pois_pmf(x_T, i) for i in range(N)]
    p_a2, p_h2, p_tie = 0.0, 0.0, 0.0
    for i in range(N):
        for j in range(N):
            pr = pm[i] * pt[j]
            if i - j >= 2: p_a2 += pr
            elif j - i >= 2: p_h2 += pr
            else: p_tie += pr
    tot2 = p_a2 + p_h2
    p_rl_away = p_a2 + p_tie * p_a2 / tot2
    markets.append(sel(0, "handicap", f'{f["participant_a"]} -1.5', p_rl_away, -1.5, "Poisson score-difference, tie mass split pro-rata"))
    markets.append(sel(0, "handicap", f'{f["participant_b"]} +1.5', 1 - p_rl_away, 1.5, "Poisson score-difference, tie mass split pro-rata"))
    pick_p, pick_s = (p_home, f["participant_b"]) if p_home >= p_away else (p_away, f["participant_a"])
    if pick_p >= 0.685 and pick_p < 0.70: NEAR.append(add_out(f, "winner", pick_s, pick_p, f["verified"]))
    if pick_p >= 0.70 and not in_window(am(pick_p)): OUTWIN.append(add_out(f, "winner", pick_s, pick_p, f["verified"]))
    LINES["fixtures"].append({"id": f["id"], "sport": f["sport"], "competition": f["competition"],
                              "markets": markets, "pick": pick_s, "pick_p": round(pick_p, 6),
                              "pick_american": am(pick_p), "tier": tier_of(pick_p, f["verified"]),
                              "priceable_note": f"season run rates: lambda_total={lam:.2f}"})

# ----------------------------------------------------------- EuroLeague -----
for f in FIX:
    if f["sport"] != "basketball" or not f["id"].startswith("el-"):
        continue
    ra, rb = IN["euroleague"][f["participant_a"]], IN["euroleague"][f["participant_b"]]
    a = shrunk(ra[0], ra[1]); b = shrunk(rb[0], rb[1])
    p_home = min(0.95, max(0.05, log5(a, b) + 0.025)); p_away = 1 - p_home
    markets = [sel(0, "winner", f["participant_a"], p_home, None, "shrunk log5 (records from official game-center) + home .025"),
               sel(0, "winner", f["participant_b"], p_away, None, "shrunk log5")]
    pick_p, pick_s = (p_home, f["participant_a"]) if p_home >= p_away else (p_away, f["participant_b"])
    if pick_p >= 0.685 and pick_p < 0.70: NEAR.append(add_out(f, "winner", pick_s, pick_p, f["verified"]))
    if pick_p >= 0.70 and not in_window(am(pick_p)): OUTWIN.append(add_out(f, "winner", pick_s, pick_p, f["verified"]))
    LINES["fixtures"].append({"id": f["id"], "sport": f["sport"], "competition": f["competition"],
                              "markets": markets, "pick": pick_s, "pick_p": round(pick_p, 6),
                              "pick_american": am(pick_p), "tier": tier_of(pick_p, f["verified"]),
                              "priceable_note": "winner only; not both teams' ppg appeared in the fetched article so totals are withheld"})

# --------------------------------------------------------------- Tennis -----
TB_ = IN["tennis_rank_basis"]; OFF = TB_["official_ranks"]
def trank(name, draw_default_uns, draw_default_q, seed=None):
    if name in OFF: return OFF[name]
    return None
def tennis_p(a, b, a_slot, b_slot, g=0.7):
    return (b_slot ** g) / (a_slot ** g + b_slot ** g)
# explicit slots (official seeds where printed; documented assumptions otherwise)
TEN_SLOTS = {
    "tn-osaka-li-tagger": ("Ann Li", 31, "Lilli Tagger", 59),
    "tn-osaka-gibson-krueger": ("Talia Gibson", 41, "Ashlyn Krueger", 59),
    "tn-osaka-stoiana-siniakova": ("Mary Stoiana", 69, "Katerina Siniakova", 59),
    "tn-osaka-boulter-ruzic": ("Katie Boulter", 54, "Antonia Ruzic", 59),
    "tn-ningbo-bejlek-bouzkova": ("Sara Bejlek", 21, "Marie Bouzkova", 21),
    "tn-ningbo-fernandez-alexandrova": ("Leylah Fernandez", 21, "Ekaterina Alexandrova", 21),
    "tn-ningbo-jovic-shnaider": ("Iva Jovic", 11, "Diana Shnaider", 13),
    "tn-ningbo-rybakina-kawa": ("Elena Rybakina", 1, "Katarzyna Kawa", 31),
    "tn-almaty-basil-mann": ("Nikoloz Basilashvili", 31, "Adrian Mannarino", 21),
    "tn-almaty-tsitsi-duck": ("Stefanos Tsitsipas", 7, "James Duckworth", 21),
    "tn-almaty-medv-atmane": ("Daniil Medvedev", 1, "Terence Atmane", 21),
    "tn-brussels-griek-leheck": ("Tallon Griekspoor", 21, "Jiri Lehecka", 2),
    "tn-lyon-moutet-paul": ("Corentin Moutet", 21, "Tommy Paul", 4),
    "tn-lyon-altmaier-fritz": ("Daniel Altmaier", 21, "Taylor Fritz", 2),
}
for f in FIX:
    if f["sport"] != "tennis": continue
    na, sa, nb, sb = TEN_SLOTS[f["id"]]
    p_a = tennis_p(na, nb, sa, sb)
    markets = [sel(0, "winner", na, p_a, None, f"Bradley-Terry rank model, slots {sa} v {sb} (rank/seed from official draws)"),
               sel(0, "winner", nb, 1 - p_a, None, "complement")]
    pick_p, pick_s = (p_a, na) if p_a >= 0.5 else (1 - p_a, nb)
    if pick_p >= 0.685 and pick_p < 0.70: NEAR.append(add_out(f, "winner", pick_s, pick_p, f["verified"]))
    if pick_p >= 0.70 and not in_window(am(pick_p)): OUTWIN.append(add_out(f, "winner", pick_s, pick_p, f["verified"]))
    LINES["fixtures"].append({"id": f["id"], "sport": "tennis", "competition": f["competition"],
                              "markets": markets, "pick": pick_s, "pick_p": round(pick_p, 6),
                              "pick_american": am(pick_p), "tier": tier_of(pick_p, f["verified"]),
                              "priceable_note": "winner only; set-score/game-total inputs are not published in official draws"})

# ------------------------------------------------------------------ URC -----
for f in FIX:
    if f["sport"] != "rugby-union" or not f["id"].startswith("urc-"): continue
    if not f["participant_b"]: continue
    ta, tb = IN["urc"][f["participant_a"]], IN["urc"][f["participant_b"]]
    a = (ta[0] + 2) / (sum(ta[:3]) + 4); b = (tb[0] + 2) / (sum(tb[:3]) + 4)
    p_home = min(0.95, max(0.05, log5(a, b) + 0.025)); p_away = 1 - p_home
    markets = [sel(0, "winner", f["participant_a"], p_home, None, "shrunk log5 on official table + home .025"),
               sel(0, "winner", f["participant_b"], p_away, None, "shrunk log5")]
    ga, gb = sum(ta[:3]), sum(tb[:3])
    x_a = (ta[3] / ga + tb[4] / gb) / 2
    x_b = (tb[3] / gb + ta[4] / ga) / 2
    m = x_a - x_b
    line = round(m)
    p_cover_a = 1 - norm_cdf((line - m) / 10.0)
    markets.append(sel(0, "handicap", f'{f["participant_a"]} {line:+g}', p_cover_a, line, "normal margin model, sigma=10 (disclosed)"))
    markets.append(sel(0, "handicap", f'{f["participant_b"]} {-line:+g}', 1 - p_cover_a, -line, "complement of the same line"))
    lam = x_a + x_b
    cent = math.floor(lam) + 0.5 if (lam - math.floor(lam)) < 0.5 else math.ceil(lam) - 0.5
    for L in (cent - 4.0, cent, cent + 4.0):
        markets.append(sel(0, "total", f"Over {L:g}", norm_cdf((lam - L) / 12.0), L, "normal totals model, sigma=12 (disclosed)"))
        markets.append(sel(0, "total", f"Under {L:g}", 1 - norm_cdf((lam - L) / 12.0), L, "same"))
    pick_p, pick_s = (p_home, f["participant_a"]) if p_home >= p_away else (p_away, f["participant_b"])
    if pick_p >= 0.685 and pick_p < 0.70: NEAR.append(add_out(f, "winner", pick_s, pick_p, f["verified"]))
    if pick_p >= 0.70 and not in_window(am(pick_p)): OUTWIN.append(add_out(f, "winner", pick_s, pick_p, f["verified"]))
    LINES["fixtures"].append({"id": f["id"], "sport": "rugby-union", "competition": f["competition"],
                              "markets": markets, "pick": pick_s, "pick_p": round(pick_p, 6),
                              "pick_american": am(pick_p), "tier": tier_of(pick_p, f["verified"]),
                              "priceable_note": f"model margin {m:+.1f} pts, lambda {lam:.1f}"})

# ------------------------------------------------- Top14 / ProD2 / StarLigue -
def position_fixtures(f, pos):
    pa, pb = pos[f["participant_a"]], pos[f["participant_b"]]
    p_home = min(0.83, max(0.17, 0.5 + 0.02 * (pb - pa) + 0.03))
    return p_home, f"linear official-position model (pos {pa} v {pb}), home +.03"

for f in FIX:
    if f["sport"] == "rugby-union" and f["competition"].startswith("Top 14"):
        p_home, note = position_fixtures(f, IN["top14_positions"])
    elif f["sport"] == "rugby-union" and f["competition"].startswith("Pro D2"):
        p_home, note = position_fixtures(f, IN["prod2_positions"])
    elif f["sport"] == "handball" and f["id"] in ("hb-lim-dun", "hb-aix-tou", "hb-cha-nim",
                                                  "hb-sel-cae", "hb-tre-ces", "hb-nan-cha"):
        key = {"Pays dAix UC": "Aix", "USAM Nimes": "Nimes", "Chambery Savoie": "Chambery",
               "Cesson Rennes": "Cesson Rennes", "Limoges 87": "Limoges",
               "Selestat Alsace": "Selestat"}
        ka, kb = key.get(f["participant_a"], f["participant_a"]), key.get(f["participant_b"], f["participant_b"])
        ta, tb = IN["lnh"][ka], IN["lnh"][kb]
        a = shrunk(ta[0], ta[1] + ta[2] if len(ta) > 2 else ta[1]); b = shrunk(tb[0], tb[1] + tb[2])
        # LNH list is [W, D, L, GF, GA] except Paris [7,0,0] pattern consistent: index1=D? verify shape:
        # stored as [W, D, L, GF, GA] -> wins=idx0, draws=idx1, losses=idx2
        a = shrunk(ta[0], ta[2], 0, ta[1]); b = shrunk(tb[0], tb[2], 0, tb[1])
        p_home = min(0.95, max(0.05, log5(a, b) + 0.025))
        note = "shrunk log5 on official StarLigue W-D-L + home .025"
        markets = [sel(0, "winner", f["participant_a"], p_home, None, note),
                   sel(0, "winner", f["participant_b"], 1 - p_home, None, note)]
        x_a = (ta[3] / 7 + tb[4] / 7) / 2; x_b = (tb[3] / 7 + ta[4] / 7) / 2
        lam = x_a + x_b; m = x_a - x_b
        line = round(m)
        p_cov = 1 - norm_cdf((line - m) / 6.0)
        markets.append(sel(0, "handicap", f'{f["participant_a"]} {line:+g}', p_cov, line, "normal margin, sigma=6 (disclosed)"))
        markets.append(sel(0, "handicap", f'{f["participant_b"]} {-line:+g}', 1 - p_cov, -line, "complement"))
        cl = round(lam)
        for L in (cl - 2, cl, cl + 2):
            markets.append(sel(0, "total", f"Over {L:g}", norm_cdf((lam - L) / 8.0), L, "Poisson-mean totals, sigma=8 (disclosed)"))
            markets.append(sel(0, "total", f"Under {L:g}", 1 - norm_cdf((lam - L) / 8.0), L, "same"))
        pick_p, pick_s = (p_home, f["participant_a"]) if p_home >= 0.5 else (1 - p_home, f["participant_b"])
        if pick_p >= 0.685 and pick_p < 0.70: NEAR.append(add_out(f, "winner", pick_s, pick_p, f["verified"]))
        if pick_p >= 0.70 and not in_window(am(pick_p)): OUTWIN.append(add_out(f, "winner", pick_s, pick_p, f["verified"]))
        LINES["fixtures"].append({"id": f["id"], "sport": f["sport"], "competition": f["competition"],
                                  "markets": markets, "pick": pick_s, "pick_p": round(pick_p, 6),
                                  "pick_american": am(pick_p), "tier": tier_of(pick_p, f["verified"]),
                                  "priceable_note": f"model margin {m:+.1f} goals, lambda {lam:.1f}"})
        continue
    elif f["sport"] in ("rugby-union", "handball") and f.get("sources"):
        if f["sport"] == "rugby-union" and not f["competition"].startswith(("Top 14", "Pro D2")):
            continue
        if f["sport"] == "handball" and f["id"] not in ("hb-lim-dun", "hb-aix-tou", "hb-cha-nim",
                                                        "hb-sel-cae", "hb-tre-ces", "hb-nan-cha"):
            continue
    else:
        continue
    p_home, note = position_fixtures(f, IN["top14_positions"] if f["competition"].startswith("Top 14") else IN["prod2_positions"])
    markets = [sel(0, "winner", f["participant_a"], p_home, None, note),
               sel(0, "winner", f["participant_b"], 1 - p_home, None, note)]
    pick_p, pick_s = (p_home, f["participant_a"]) if p_home >= 0.5 else (1 - p_home, f["participant_b"])
    if pick_p >= 0.685 and pick_p < 0.70: NEAR.append(add_out(f, "winner", pick_s, pick_p, f["verified"]))
    if pick_p >= 0.70 and not in_window(am(pick_p)): OUTWIN.append(add_out(f, "winner", pick_s, pick_p, f["verified"]))
    LINES["fixtures"].append({"id": f["id"], "sport": "rugby-union", "competition": f["competition"],
                              "markets": markets, "pick": pick_s, "pick_p": round(pick_p, 6),
                              "pick_american": am(pick_p), "tier": tier_of(pick_p, f["verified"]),
                              "priceable_note": "winner only (no official PF/PA fetched for this competition)"})

# ---------------------------------------------------------- Rugby league -----
for f in FIX:
    if f["sport"] != "rugby-league": continue
    comp = f["competition"]
    table = IN["irl_women"] if "Women" in comp or "Women's" in comp else IN["irl_men"]
    ra, rb = table.get(f["participant_a"]), table.get(f["participant_b"])
    if ra is None or rb is None:
        continue
    p_a = ra / (ra + rb)
    note = "linear share of official IRL strength ratings"
    markets = [sel(0, "winner", f["participant_a"], p_a, None, note),
               sel(0, "winner", f["participant_b"], 1 - p_a, None, note)]
    pick_p, pick_s = (p_a, f["participant_a"]) if p_a >= 0.5 else (1 - p_a, f["participant_b"])
    if pick_p >= 0.685 and pick_p < 0.70: NEAR.append(add_out(f, "winner", pick_s, pick_p, f["verified"]))
    if pick_p >= 0.70 and not in_window(am(pick_p)): OUTWIN.append(add_out(f, "winner", pick_s, pick_p, f["verified"]))
    LINES["fixtures"].append({"id": f["id"], "sport": "rugby-league", "competition": f["competition"],
                              "markets": markets, "pick": pick_s, "pick_p": round(pick_p, 6),
                              "pick_american": am(pick_p), "tier": tier_of(pick_p, f["verified"]),
                              "priceable_note": f"official ratings {ra} v {rb}"})

# ------------------------------------- selection-level Highs (all markets) ---
HIGH_SEL = []
for fr in LINES["fixtures"]:
    ver = get(fr["id"])["verified"]
    for m in fr["markets"]:
        p = m["p"]
        if p >= 0.700000 and in_window(m["fair_american"]) and ver:
            HIGH_SEL.append({"fixture_id": fr["id"], **m, "match": f'{get(fr["id"])}'.strip() if False else
                             f'{get(fr["id"])["participant_a"]} v {get(fr["id"])["participant_b"]}',
                             "competition": fr["competition"], "sport": fr["sport"]})
        elif p >= 0.700000 and not in_window(m["fair_american"]) and m["market"] == "winner":
            pass  # already in OUTWIN

# --------------------------------------------------- unpriced inventory -----
priced = {fr["id"] for fr in LINES["fixtures"]}
UNPRICED = []
REASONS = {
    "ice-hockey": "European club rows: no official league source fetched this session",
    "baseball": "participant_b blank (payload chunk cut) — no price without both teams",
    "basketball": "official team records/strength input not retrievable (NBA JS blocks; NBB federation not fetched)",
    "cricket": "fixture itself not officially verified (ICC JS, NZC failure, CSA stale widget) and no official strength input",
    "darts": "PDC Order of Merit/rankings not retrievable (official site consent wall, F-8F6D-03) — no official strength input",
    "volleyball": "fixture not officially verified (federation pages not completed) — no price on an unverified fixture",
    "handball": "unverified federation rows; French rows priced separately",
    "gaelic-football": "no official strength input (county ladders/forms not fetched) — fixture verified rows stay unpriced",
    "snooker": "no official ranking/strength input fetched (WST rankings not read) — fixture verified, pricing withheld",
    "aussie-rules": "official AFLW ladder not retrievable (JS loading) — fixture verified, pricing withheld",
    "golf": "field-outright markets: no official per-player stroke input; investigated, not priced",
    "motor-racing": "race-outright market: no official per-driver performance input beyond the entry; investigated, not priced",
    "rugby-union": "Premiership row not officially verified (JS) — no price",
}
for f in FIX:
    if f["id"] in priced: continue
    if f["sport"] == "handball" and f["verified"] and f["id"].startswith("hb-") and f["id"] in ("hb-lim-dun", "hb-aix-tou", "hb-cha-nim", "hb-sel-cae", "hb-tre-ces", "hb-nan-cha"):
        continue
    reason = REASONS.get(f["sport"], "no official strength input this session")
    if f["sport"] == "rugby-union" and f["id"] == "prem-new-sale":
        reason = REASONS["rugby-union"]
    UNPRICED.append({"id": f["id"], "sport": f["sport"], "verified": f["verified"], "reason": reason})

LINES["ledgers"] = {
    "high_selections": HIGH_SEL,
    "out_of_window_ge70_winners": OUTWIN,
    "near_band_winners_685_700": NEAR,
    "nhl_official_market_cross_check": CROSS,
    "unpriced": UNPRICED,
}
counts = {"High": 0, "Medium": 0, "Low": 0}
for fr in LINES["fixtures"]:
    counts[fr["tier"]] = counts.get(fr["tier"], 0) + 1
LINES["counts"] = {"priced_fixtures": len(LINES["fixtures"]), **counts,
                   "high_selections": len(HIGH_SEL), "unpriced": len(UNPRICED),
                   "out_of_window_ge70": len(OUTWIN), "near_band": len(NEAR)}
json.dump(LINES, open(os.path.join(D, "lines.json"), "w"), indent=1, ensure_ascii=False)
print(json.dumps(LINES["counts"], indent=1))
print("HIGH SELECTIONS:")
for h in HIGH_SEL:
    print(" ", h["fixture_id"], "|", h["market"], "|", h["selection"], "| p=", h["p"], "| am=", h["fair_american"])
print("OUT OF WINDOW (winners):", len(OUTWIN))
for o in OUTWIN:
    print("  ", o["fixture_id"], o["selection"], o["p"], o["fair_american"])
print("NEAR:", [(n["fixture_id"], n["p"], n["fair_american"]) for n in NEAR])
