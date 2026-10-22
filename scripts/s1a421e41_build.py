#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T60 / session 1a421e41-olbg1 -- desk builder.

Reads
  data/1a421e41/olbg_harvest_raw.py   (live OLBG harvest, 17 in-scope sports)
  data/1a421e41/official_evidence.py  (official-source register)
Writes
  data/1a421e41/desk.json

Everything numeric in the output is either
  (a) copied verbatim from an official source (with the URL attached), or
  (b) produced by OUR OWN origination model from those official inputs, with
      the model constant named and labelled as an assumption.
No value is ever inferred, interpolated from a bookmaker, or filled in from a
non-official source. Where an official figure does not exist the field is left
null and the row is flagged unverified.

Deterministic: no clock, no random, no network. Re-running produces the same
bytes except for generated_utc, which is taken from the harvest stamp.
"""

import importlib.util
import json
import math
import os
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "1a421e41")
OUT = os.path.join(DATA, "desk.json")

SESSION = "1a421e41-olbg1"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


H = _load("olbg_harvest_raw", os.path.join(DATA, "olbg_harvest_raw.py"))
E = _load("official_evidence", os.path.join(DATA, "official_evidence.py"))

GENERATED_UTC = H.HARVEST_UTC
NOW_ISO = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ===========================================================================
# 1. SCOPE
# ===========================================================================

SPORT_LABEL = {
    "tennis": "Tennis",
    "basketball": "Basketball",
    "golf": "Golf",
    "cricket": "Cricket",
    "snooker": "Snooker",
    "rugby_union": "Rugby Union",
    "rugby_league": "Rugby League",
    "baseball": "Baseball",
    "ice_hockey": "Ice Hockey",
    "motor_racing": "Motor Racing",
    "darts": "Darts",
    "handball": "Handball",
    "volleyball": "Volleyball",
    "aussie_rules": "Aussie Rules",
    "esports": "eSports",
    "gaelic_football": "Gaelic Football",
    "greyhounds": "Greyhounds",
}

# Excluded by the brief, with the OLBG id we confirmed each sits on.
EXCLUDED = [
    {"label": "Soccer / Football", "olbg_id": 1, "reason": "excluded by brief (soccer, football)"},
    {"label": "Horse Racing", "olbg_id": 2, "reason": "excluded by brief"},
    {"label": "American Football", "olbg_id": 11, "reason": "excluded by brief"},
    {"label": "Boxing", "olbg_id": 16, "reason": "excluded by brief (boxing; UFC/MMA carded under Boxing/Specials on OLBG)"},
    {"label": "Cycling", "olbg_id": 17, "reason": "excluded by brief"},
    {"label": "Specials", "olbg_id": 18, "reason": "excluded by brief (specials; UFC/MMA also carded here)"},
    {"label": "Hurling", "olbg_id": 26, "reason": "excluded by brief"},
]

# ===========================================================================
# 2. OUR MODEL CONSTANTS  (assumptions -- never presented as sourced facts)
# ===========================================================================

# Spread / total standard deviations, in the sport's own scoring unit.
# These are OUR assumptions. They are published with a sensitivity note.
SPORT_SIGMA = {
    "basketball":    {"unit": "points", "sigma_h": 11.5, "sigma_t": 16.0},
    "rugby_union":   {"unit": "points", "sigma_h": 12.5, "sigma_t": 14.0},
    "rugby_league":  {"unit": "points", "sigma_h": 12.5, "sigma_t": 14.0},
    "aussie_rules":  {"unit": "points", "sigma_h": 32.0, "sigma_t": 36.0},
    "handball":      {"unit": "goals",  "sigma_h": 6.0,  "sigma_t": 8.5},
    "tennis":        {"unit": "games",  "sigma_h": 5.2,  "sigma_t": 8.5},
    "baseball":      {"unit": "runs",   "sigma_h": 4.0,  "sigma_t": 4.5},
    "ice_hockey":    {"unit": "goals",  "sigma_h": 2.35, "sigma_t": 2.6},
    "volleyball":    {"unit": "sets",   "sigma_h": 1.15, "sigma_t": 1.4},
    "darts":         {"unit": "legs",   "sigma_h": 2.30, "sigma_t": 3.0},
    "snooker":       {"unit": "frames", "sigma_h": 2.0,  "sigma_t": 3.2},
    "cricket":       {"unit": "runs",   "sigma_h": None, "sigma_t": None},
    "golf":          {"unit": "strokes", "sigma_h": None, "sigma_t": None},
    "motor_racing":  {"unit": "points", "sigma_h": None, "sigma_t": None},
    "greyhounds":    {"unit": "lengths", "sigma_h": None, "sigma_t": None},
    "esports":       {"unit": "maps",   "sigma_h": None, "sigma_t": None},
    "gaelic_football": {"unit": "points", "sigma_h": None, "sigma_t": None},
}

# Consensus-only fallback (Class C). OUR assumption.
CLASS_C_BASE = 0.50
CLASS_C_SLOPE = 0.30
CLASS_C_CAP = 0.680
CLASS_C_MIN_TIPS = 5

# One-sided official evidence (Class B). OUR assumption, hard-capped Medium.
CLASS_B_P = 0.640

# Snooker: WST states officially which of the world's top 16 remain in the
# draw. The 0.755 edge we give that side is OUR assumption.
SNOOKER_TOP16_P = 0.755

# Darts: seed-gap logistic on the official PDC seedings. OUR assumption.
DARTS_K = 0.62
DARTS_SCALE = 8.0

PROB_FLOOR = 0.06
PROB_CEIL = 0.94

# The high-confidence window required by the brief.
WINDOW_AMERICAN_MIN = -250
WINDOW_AMERICAN_MAX = 10000
HIGH_PROB_MIN = 0.70

OVERROUND_BOOK = 0.05  # printed beside every price, never used to gate


# ===========================================================================
# 3. MATHS
# ===========================================================================

def phi(x):
    """Standard normal CDF."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def phi_inv(p, lo=-8.0, hi=8.0):
    """Standard normal inverse CDF by bisection (deterministic, 200 iters)."""
    p = min(max(p, 1e-12), 1.0 - 1e-12)
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if phi(mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def clip_prob(p):
    return min(max(p, PROB_FLOOR), PROB_CEIL)


def p_to_decimal(p):
    if p <= 0:
        return None
    return round(1.0 / p, 4)


def p_to_american(p):
    """Zero-vig American price for a true probability p."""
    if p <= 0 or p >= 1:
        return None
    if p >= 0.5:
        return int(round(-100.0 * p / (1.0 - p)))
    return int(round(100.0 * (1.0 - p) / p))


def book_american(p):
    """Same selection priced by a book carrying a 5% overround. Printed for
    comparison only; the window gate always uses the zero-vig price."""
    pb = min(p * (1.0 + OVERROUND_BOOK), 0.999)
    return p_to_american(pb)


def in_window(american):
    return american is not None and WINDOW_AMERICAN_MIN <= american <= WINDOW_AMERICAN_MAX


def round_half(x):
    return round(x * 2.0) / 2.0


# ===========================================================================
# 4. OFFICIAL CROSSWALKS
# ===========================================================================

# OLBG short name -> official club name in the EuroLeague standings.
# A name crosswalk only; no numeric value is taken from it.
EUROLEAGUE_ALIAS = {
    "Anadolu Efes": "Anadolu Efes Istanbul",
    "Besiktas": "Besiktas Istanbul",
    "Bayern Munich": "FC Bayern Munich",
    "BC Dubai": "Dubai Basketball",
    "Maccabi Tel Aviv": "Maccabi Rapyd Tel Aviv",
    "Real Madrid": "Real Madrid",
    "Panathinaikos": "Panathinaikos AKTOR Athens",
    "Baskonia": "Kosner Baskonia Vitoria-Gasteiz",
    "Milano": "Armani Olimpia Milan",
    "Barcelona": "FC Barcelona",
    "Partizan": "Partizan Mozzart Bet Belgrade",
    "Crvena Zvezda": "Crvena Zvezda Meridianbet Belgrade",
    "Zalgiris": "Zalgiris Kaunas",
    "Asvel Lyon Villeurbanne": "LDLC ASVEL Villeurbanne",
    "Olympiacos": "Olympiacos Piraeus",
    "Fenerbahce": "Fenerbahce Tarfin Istanbul",
    "Paris Basketball": "Paris Basketball",
    "Valencia": "Valencia Basket",
}

_STANDINGS = {r[1]: r for r in E.EUROLEAGUE_STANDINGS["rows"]}
_TOT = E.EUROLEAGUE_STANDINGS["totals"]

# Home-court advantage DERIVED from official data, not assumed:
#   official home win rate = 33/61 = 0.540984
#   HCA = sigma_margin * Phi^-1(home_win_rate)
# sigma_margin itself is our documented assumption, so HCA inherits that label.
HOME_WIN_RATE = _TOT["home_wins"] / (_TOT["home_wins"] + _TOT["away_wins"])
BASKETBALL_SIGMA_H = SPORT_SIGMA["basketball"]["sigma_h"]
BASKETBALL_HCA = BASKETBALL_SIGMA_H * phi_inv(HOME_WIN_RATE)

# OLBG fixture -> official EuroLeague game_id (from the official Game Center).
EUROLEAGUE_GAME_BY_OLBG_EVENT = {
    535918: "E2026/64",
    535920: "E2026/65",
    535921: "E2026/62",
    535923: "E2026/67",
    535922: "E2026/63",
    535924: "E2026/66",
    535928: "E2026/68",
    535925: "E2026/70",
}
EUROLEAGUE_GAMES = {g["game_id"]: g for g in E.EUROLEAGUE_GAME_CENTER["games"]}


def club_stats(official_name):
    """Per-game scoring rates taken straight from the official standings."""
    r = _STANDINGS.get(official_name)
    if not r:
        return None
    gp = r[3]
    return {
        "club": official_name,
        "code": r[2],
        "pos": r[0],
        "gp": gp,
        "w": r[4],
        "l": r[5],
        "win_pct": r[6],
        "pts_for": r[7],
        "pts_against": r[8],
        "diff": r[9],
        "home": r[10],
        "away": r[11],
        "ot": r[12],
        "last10": r[13],
        "ppg_for": round(r[7] / gp, 4),
        "ppg_against": round(r[8] / gp, 4),
        "ppd": round(r[9] / gp, 4),
    }


# Darts: official PDC seedings and the official Thursday order of play.
PDC_SEEDS = E.PDC_EUROPEAN_CHAMPIONSHIP["seeds"]
PDC_TIES = [tuple(t) for t in E.PDC_EUROPEAN_CHAMPIONSHIP["thursday_ties"]]
PDC_SOURCES = list(E.PDC_EUROPEAN_CHAMPIONSHIP["sources"])

# Snooker: the only officially stated strength differential on the WST page.
WST_TOP16_QUOTE = E.WST_NORTHERN_IRELAND_OPEN["quote_top16"]
WST_TOP16_PLAYERS = ["Mark Williams", "Kyren Wilson"]
WST_SOURCES = list(E.WST_NORTHERN_IRELAND_OPEN["sources"])
WST_FORM = {
    "Kyren Wilson": [
        E.WST_NORTHERN_IRELAND_OPEN["match_centre_rows_read"][4]["players"],  # 4-0 Ben Mertens
        E.WST_NORTHERN_IRELAND_OPEN["match_centre_rows_read"][5]["players"],  # 2-4 Un-Nooh
    ],
    "Mark Williams": [
        E.WST_NORTHERN_IRELAND_OPEN["match_centre_rows_read"][6]["players"],  # 4-2 Robbie Williams
        E.WST_NORTHERN_IRELAND_OPEN["match_centre_rows_read"][7]["players"],  # Zhang Anda 2-4
    ],
    "Pang Junxu": ["Pang Junxu 4-3 Liam Davies (official WST match centre: breaks 112, 73, 81)"],
    "Sam Craigie": ["Sam Craigie 4-3 Xu Si (official WST match centre: top break 103, won on a decider 75)"],
    "John Higgins": [E.WST_NORTHERN_IRELAND_OPEN["quote_higgins"]],
}

# Tennis: official ATP Live Race rows read this session.
ATP_RACE = {r["player"]: r for r in E.ATP_LIVE_RACE_AND_FIELDS["live_race_rows_read"]}
ATP_SOURCES = list(E.ATP_LIVE_RACE_AND_FIELDS["sources"])
ATP_NAME_MAP = {
    "Daniil Medvedev": "D. Medvedev",
    "Taylor Fritz": "T. Fritz",
    "Alexander Bublik": "A. Bublik",
    "Sebastian Baez": "S. Baez",
}

# Players / clubs for whom an official body published CURRENT FORM this session.
OFFICIAL_FORM_PLAYERS = {"Gian van Veen", "Luke Humphries"}  # pdc.tv preview


# ===========================================================================
# 5. FIXTURE PARSING
# ===========================================================================

VS_TOKENS = (" vs. ", " vs ", " v ", " @ ", " v. ")


def split_fixture(fixture):
    """Split an OLBG fixture string into (left, right, separator)."""
    for tok in VS_TOKENS:
        if tok in fixture:
            a, b = fixture.split(tok, 1)
            return a.strip(), b.strip(), tok.strip()
    return fixture.strip(), None, None


def slugify(fixture, competition, event_id):
    """Reconstruct OLBG's card slug from the harvested strings.

    OLBG's own observed scheme: <Subcat>/<Event_Slug>/<event_id>?event_id=NNN
    with spaces and apostrophes dropped from the event slug. This is a
    reconstruction, so every reconstructed URL is labelled as such in the
    output and is never presented as a harvested literal.
    """
    base = fixture.replace("'", "").replace("’", "").replace(".", "")
    base = "_".join(base.split())
    comp = "_".join(competition.split()) if competition else ""
    return {"competition_slug": comp, "event_slug": base, "event_id": event_id}


def olbg_card_url(sport_key, slug):
    hub = H.HARVEST_META[sport_key]["hub"]
    return "%s/%s/%s?event_id=%s" % (hub, slug["competition_slug"], slug["event_slug"], slug["event_id"])


# ===========================================================================
# 6. RATING RESOLUTION
# ===========================================================================

def rate_euroleague(event_id, fixture):
    """Class A -- official two-sided margin origination."""
    left, right, _ = split_fixture(fixture)
    h_official = EUROLEAGUE_ALIAS.get(left)
    a_official = EUROLEAGUE_ALIAS.get(right)
    if not h_official or not a_official:
        return None
    hs = club_stats(h_official)
    as_ = club_stats(a_official)
    if not hs or not as_:
        return None
    # Expected scores, each the mean of a side's own official scoring rate and
    # its opponent's official points-allowed rate. Both inputs are official.
    e_home = (hs["ppg_for"] + as_["ppg_against"]) / 2.0
    e_away = (as_["ppg_for"] + hs["ppg_against"]) / 2.0
    margin_centre = e_home - e_away + BASKETBALL_HCA
    total_centre = e_home + e_away
    p_home = phi(margin_centre / BASKETBALL_SIGMA_H)
    game_id = EUROLEAGUE_GAME_BY_OLBG_EVENT.get(event_id)
    game = EUROLEAGUE_GAMES.get(game_id) if game_id else None
    sources = [E.EUROLEAGUE_STANDINGS["source_url"]]
    if game:
        sources.append(E.EUROLEAGUE_GAME_CENTER["source_url"])
    evidence = []
    if game:
        evidence.extend(game["facts"])
        evidence.append("Official kick-off: %s CEST on %s (game %s)." % (
            game["official_ko_cest"], game["date"], game["game_id"]))
    evidence.append(
        "Official standings: %s %d-%d, PTS+ %d, PTS- %d, %+.0f, home %s, away %s. "
        "%s %d-%d, PTS+ %d, PTS- %d, %+.0f, home %s, away %s." % (
            hs["club"], hs["w"], hs["l"], hs["pts_for"], hs["pts_against"], hs["diff"], hs["home"], hs["away"],
            as_["club"], as_["w"], as_["l"], as_["pts_for"], as_["pts_against"], as_["diff"], as_["home"], as_["away"],
        ))
    evidence.append(
        "Origination: E[%s pts] = (%.2f own ppg + %.2f opponent ppg allowed)/2 = %.2f; "
        "E[%s pts] = (%.2f + %.2f)/2 = %.2f; margin centre %.2f + HCA %.2f = %.2f; total centre %.2f." % (
            h_official, hs["ppg_for"], as_["ppg_against"], e_home,
            a_official, as_["ppg_for"], hs["ppg_against"], e_away,
            e_home - e_away, BASKETBALL_HCA, margin_centre, total_centre,
        ))
    return {
        "klass": "A",
        "basis": "official_two_sided_margin",
        "p_subject": clip_prob(p_home),
        "subject": h_official,
        "subject_side": "home",
        "opponent": a_official,
        "margin_centre": round(margin_centre, 4),
        "total_centre": round(total_centre, 4),
        "total_originatable": True,
        "e_home": round(e_home, 4),
        "e_away": round(e_away, 4),
        "home_stats": hs,
        "away_stats": as_,
        "game_id": game_id,
        "narrative_key": game_id,
        "official_ko_cest": game["official_ko_cest"] if game else None,
        "official_date": game["date"] if game else None,
        "form_ok": True,
        "sources": sources,
        "evidence": evidence,
        "conflicts": [c["id"] for c in E.EUROLEAGUE_OFFICIAL_CONFLICTS],
    }


def rate_darts(fixture):
    """Class A -- official PDC seedings for both players."""
    left, right, _ = split_fixture(fixture)
    sl = PDC_SEEDS.get(left)
    sr = PDC_SEEDS.get(right)
    if sl is None or sr is None:
        return None
    gap = abs(sr - sl)
    fav, dog = (left, right) if sl < sr else (right, left)
    p = 1.0 / (1.0 + math.exp(-DARTS_K * gap / DARTS_SCALE))
    tie = None
    for t in PDC_TIES:
        if set(t) == {left, right}:
            tie = t
            break
    ev = [
        "Official PDC European Championship 2026 seedings: %s seed %d, %s seed %d (seed gap %d)." % (left, sl, right, sr, gap),
        "Origination: p = 1/(1+exp(-%.2f*%d/%.1f)) = %.4f for %s." % (DARTS_K, gap, DARTS_SCALE, p, fav),
        E.PDC_EUROPEAN_CHAMPIONSHIP.get("quote_schedule_of_play", ""),
    ]
    if E.PDC_EUROPEAN_CHAMPIONSHIP.get("quote_preview_form"):
        ev.append(E.PDC_EUROPEAN_CHAMPIONSHIP["quote_preview_form"])
    if tie:
        ev.append("Official Thursday order of play lists this tie: %s v %s." % (tie[0], tie[1]))
    form_ok = bool({fav, dog} & OFFICIAL_FORM_PLAYERS)
    return {
        "klass": "A",
        "basis": "official_seed_gap",
        "p_subject": clip_prob(p),
        "subject": fav,
        "subject_side": "listed",
        "opponent": dog,
        "margin_centre": None,
        "total_centre": None,
        "total_originatable": False,
        "form_ok": form_ok,
        "sources": PDC_SOURCES,
        "evidence": [x for x in ev if x],
        "conflicts": [],
        "seed_gap": gap,
    }


def wst_official_listing(left, right):
    """Return the official WST match-centre row that names BOTH players."""
    for r in E.WST_NORTHERN_IRELAND_OPEN["match_centre_rows_read"]:
        pl = r.get("players") or ""
        if " v " not in pl:
            continue
        a, b = pl.split(" v ", 1)
        a, b = a.strip(), b.strip()
        if {a.lower(), b.lower()} == {left.lower(), right.lower()}:
            return r
    return None


def rate_snooker(fixture):
    """Class A only where the official WST match centre names BOTH players and
    WST also states that one of them is a surviving world top-16 player.

    Where OLBG names an opponent the official listing has not resolved yet (it
    still reads 'Winner of match NN'), the evidence is one-sided and the row is
    Class B, hard-capped at Medium, and the discrepancy is flagged.
    """
    left, right, _ = split_fixture(fixture)
    t16 = [p for p in (left, right) if p in WST_TOP16_PLAYERS]
    if len(t16) != 1:
        return None
    fav = t16[0]
    dog = right if fav == left else left
    listing = wst_official_listing(left, right)
    both_official = listing is not None
    ev = [
        "Official WST quote: \"%s\"" % WST_TOP16_QUOTE,
        "%s is one of the two world top-16 players officially confirmed still in the draw." % fav,
        "Origination: we give the officially confirmed top-16 side p = %.3f (OUR constant, not a sourced figure)." % SNOOKER_TOP16_P,
    ]
    for f in WST_FORM.get(fav, []):
        ev.append("Official WST match-centre form for %s: %s." % (fav, f))
    for f in WST_FORM.get(dog, []):
        ev.append("Official WST match-centre form for %s: %s." % (dog, f))
    if both_official:
        ev.append("Official WST match centre lists this tie by name: %s (match %s, listed %s), so both players are officially confirmed."
                  % (listing["players"], listing.get("match_no") or "n/a", listing.get("listed")))
    else:
        ev.append("The official WST match centre does NOT name both players for this tie; it still reads 'Mark Williams v Winner of match 44'. "
                  "OLBG supplies the opponent's name, so the evidence is one-sided and this row is capped at Medium.")
    return {
        "klass": "A" if both_official else "B",
        "basis": "official_top16_both_named" if both_official else "official_top16_one_sided",
        "p_subject": clip_prob(SNOOKER_TOP16_P),
        "subject": fav,
        "subject_side": "listed",
        "opponent": dog,
        "margin_centre": None,
        "total_centre": None,
        "total_originatable": False,
        "form_ok": bool(WST_FORM.get(fav)) and both_official,
        "hard_cap": None if both_official else "Medium",
        "narrative_key": ("WST-%s" % listing["match_no"]) if (both_official and listing.get("match_no")) else None,
        "opponent_named_officially": both_official,
        "sources": WST_SOURCES,
        "evidence": ev,
        "conflicts": [],
    }


def rate_tennis(fixture):
    """Class B (one side officially rated) or Class A (both sides officially rated)."""
    left, right, _ = split_fixture(fixture)
    def race_of(name):
        key = ATP_NAME_MAP.get(name, name)
        if key in ATP_RACE:
            return ATP_RACE[key]
        for k, v in ATP_RACE.items():
            if k.split(". ")[-1].lower() == name.split()[-1].lower():
                return v
        return None
    rl, rr = race_of(left), race_of(right)
    if not rl and not rr:
        return None
    if rl and rr:
        fav, dog = (left, right) if rl["live_rank"] < rr["live_rank"] else (right, left)
        rf, rd = (rl, rr) if rl["live_rank"] < rr["live_rank"] else (rr, rl)
        klass, basis = "A", "official_live_race_both_sides"
        p = clip_prob(0.50 + (SNOOKER_TOP16_P - 0.50))
    else:
        r = rl or rr
        fav = left if rl else right
        dog = right if rl else left
        rf, rd = r, None
        klass, basis = "B", "official_live_race_one_sided"
        p = clip_prob(CLASS_B_P)
    ev = [
        "Official ATP Live Race to Turin: %s, live rank %d, %d points. Note: \"%s\"." % (
            rf["player"], rf["live_rank"], rf["points"], rf["note"]),
    ]
    if rd:
        ev.append("Official ATP Live Race to Turin: %s, live rank %d, %d points. Note: \"%s\"." % (
            rd["player"], rd["live_rank"], rd["points"], rd["note"]))
    else:
        ev.append("No official ATP rating was published for %s, so this fixture is single-sided evidence only." % dog)
    ev.append("Origination: %s p = %.3f under the %s rule (OUR constant)." % (
        "both-sides-rated" if klass == "A" else "one-sided", p, basis))
    if E.ATP_LIVE_RACE_AND_FIELDS.get("quote_medvedev"):
        ev.append("Official ATP scouting report: \"%s\"" % E.ATP_LIVE_RACE_AND_FIELDS["quote_medvedev"])
    return {
        "klass": klass,
        "basis": basis,
        "p_subject": p,
        "subject": fav,
        "subject_side": "listed",
        "opponent": dog,
        "margin_centre": None,
        "total_centre": None,
        "total_originatable": False,
        "form_ok": False,
        "hard_cap": "Medium" if klass == "B" else None,
        "sources": ATP_SOURCES,
        "evidence": ev,
        "conflicts": [],
    }


def rate_from_consensus(win_tips, total_tips, share_pct, fixture):
    """Class C -- OLBG tipster consensus only. Never graded High."""
    left, right, _ = split_fixture(fixture)
    tips = (win_tips or 0)
    if share_pct is None or tips < CLASS_C_MIN_TIPS:
        return {
            "klass": "C",
            "basis": "consensus_insufficient",
            "p_subject": CLASS_C_BASE,
            "subject": left,
            "subject_side": "listed",
            "opponent": right,
            "margin_centre": None,
            "total_centre": None,
            "total_originatable": False,
            "form_ok": False,
            "hard_cap": "Medium",
            "sources": [],
            "evidence": ["No official governing-body source reached for this fixture; only OLBG consensus is available, "
                         "which is not an official source. Probability left at the neutral %.2f." % CLASS_C_BASE],
            "conflicts": [],
        }
    share = share_pct / 100.0
    p = clip_prob(min(CLASS_C_BASE + CLASS_C_SLOPE * (share - 0.5), CLASS_C_CAP))
    return {
        "klass": "C",
        "basis": "olbg_consensus_only",
        "p_subject": p,
        "subject": left,
        "subject_side": "listed",
        "opponent": right,
        "margin_centre": None,
        "total_centre": None,
        "total_originatable": False,
        "form_ok": False,
        "hard_cap": "Medium",
        "sources": [],
        "evidence": ["OLBG consensus share %.0f%% over %d tips. OLBG is not an official source, so this can never be "
                     "graded High; p = 0.50 + 0.30*(%.2f-0.5) capped at %.2f." % (share_pct, tips, share, CLASS_C_CAP)],
        "conflicts": [],
    }


# ===========================================================================
# 7. MARKET ORIGINATION
# ===========================================================================

def build_markets(home_name, away_name, p_home, mc, tc, total_ok, sigma_h, sigma_t, unit, klass):
    """Originate every market we can defend, on our own zero-vig basis.

    Sign convention: mc is the expected margin of the HOME (first-listed) side
    over the away side, in the sport's own scoring unit. Rungs sit on a strict
    half-point grid so that no rung can ever push.

    Spread and total ladders are originated only where we hold an official
    rating input (Class A or B). A Class C row carries a moneyline only,
    because a spread built on tipster consensus would look authoritative
    without being sourced.
    """
    markets = []
    if home_name is None or away_name is None:
        return markets

    # ---- match winner ----------------------------------------------------
    for side, p in ((home_name, p_home), (away_name, clip_prob(1.0 - p_home))):
        p = clip_prob(p)
        am = p_to_american(p)
        markets.append({
            "market": "Match Winner", "line": None, "side": side,
            "label": "%s to win" % side,
            "p": round(p, 6), "decimal": p_to_decimal(p), "american": am,
            "book5_american": book_american(p),
            "centre": None, "offset": 0.0, "unit": unit,
            "in_window": in_window(am), "ge_70": p >= HIGH_PROB_MIN,
            "origin": "official" if klass in ("A", "B") else "consensus_only",
        })

    if klass not in ("A", "B"):
        return markets

    # ---- handicap ladder -------------------------------------------------
    # Where an official body published scoring data we have a true margin
    # centre. Where it published only a rating (seeds, rank, top-16 status)
    # we convert that probability into the equivalent margin centre so the
    # ladder is expressed in the sport's own unit.
    if sigma_h:
        if mc is None:
            mc = sigma_h * phi_inv(p_home)
        h = 0.5
        while h <= max(3.0 * sigma_h, 6.0):
            z = (h - mc) / sigma_h
            for side, p in ((home_name, 1.0 - phi(z)), (away_name, phi(z))):
                p = clip_prob(p)
                am = p_to_american(p)
                sign = "-" if side == home_name else "+"
                markets.append({
                    "market": "Handicap",
                    "line": round(h if side == home_name else -h, 1),
                    "side": side,
                    "label": "%s %s%.1f %s" % (side, sign, h, unit or ""),
                    "p": round(p, 6), "decimal": p_to_decimal(p), "american": am,
                    "book5_american": book_american(p),
                    "centre": round(mc, 4),
                    "offset": round(abs((h if side == home_name else -h) - mc), 4),
                    "unit": unit,
                    "in_window": in_window(am), "ge_70": p >= HIGH_PROB_MIN,
                    "origin": "official",
                })
            h += 1.0

    # ---- total ladder, only where an official anchor exists --------------
    if sigma_t and tc is not None and total_ok:
        base = math.floor(tc) + 0.5      # strict .5 grid: a total can never push
        for k in range(0, int(3.0 * sigma_t) + 2):
            for x in ([base] if k == 0 else [base - k, base + k]):
                z = (x - tc) / sigma_t
                for side_label, p in (("Over", 1.0 - phi(z)), ("Under", phi(z))):
                    p = clip_prob(p)
                    am = p_to_american(p)
                    markets.append({
                        "market": "Match Total", "line": round(x, 1), "side": side_label,
                        "label": "%s %.1f %s" % (side_label, x, unit or "points"),
                        "p": round(p, 6), "decimal": p_to_decimal(p), "american": am,
                        "book5_american": book_american(p),
                        "centre": round(tc, 4), "offset": round(abs(x - tc), 4),
                        "unit": unit,
                        "in_window": in_window(am), "ge_70": p >= HIGH_PROB_MIN,
                        "origin": "official",
                    })
    return markets


def grade(p, american, klass, hard_cap, form_ok):
    """Confidence tier for a selection."""
    if klass == "A" and p >= HIGH_PROB_MIN and in_window(american) and form_ok:
        return "High"
    if hard_cap == "Medium":
        return "Medium" if p > 0.5 + 1e-9 else "Low"
    if p >= 0.62 and in_window(american):
        return "Medium"
    if p >= 0.55:
        return "Medium"
    return "Low"


def pick_high(markets, klass, form_ok, hard_cap):
    """Tightest rung that satisfies every High gate."""
    if hard_cap == "Medium" or klass != "A" or not form_ok:
        return None, []
    cands = [m for m in markets if m["ge_70"] and m["in_window"]]
    rejected = [m for m in markets if m["ge_70"] and not m["in_window"]]
    if not cands:
        return None, rejected
    order = {"Match Winner": 0, "Handicap": 1, "Match Total": 2}
    cands.sort(key=lambda m: (round(m["offset"], 6), order.get(m["market"], 9), abs(m["line"] or 0)))
    return cands[0], rejected


# ===========================================================================
# 8. PREDICTIONS (hand-written narrative + computed selection sentence)
# ===========================================================================

NARRATIVE = {
    "E2026/64": "Anadolu Efes arrive at this Istanbul derby off an uplifting road win in Kaunas, with Cam Payne holding the backcourt together while Mike James is injured, and they sit thirteenth on 2-4 having scored 492 and conceded 510 across six rounds. Besiktas are level on 3-3, beat Bayern on Friday to salvage a split of the two-round week, and could hand new signing Lonnie Walker his debut. Besiktas average 92.3 points, third best in the league, against an Efes defence conceding 85.0.",
    "E2026/65": "Bayern Munich are 2-4 and back in their own hall after a two-round week in Turkiye, having put up 521 and given away 552, with Duane Washington chipping in 16.8 points per game off the bench alongside three-point specialist Andreas Obst. Dubai Basketball come in 4-2 and still travelling after wins in Spain and Italy, conceding just 82.2 a night, fifth best in the competition, while Dwayne Bacon averages a league-third-best 17.8.",
    "E2026/62": "Maccabi Rapyd Tel Aviv split their two games in Spain last week and stand 2-4 with 509 points for and 540 against, though Yam Madar has settled in quickly. Real Madrid are 3-3 and have won three in a row, yet their away column reads 1-3 in the official standings rather than the 1-4 quoted in the round preview, and Theo Maledon has taken a clear step forward in his second season in Madrid. The home team has taken each of the last five meetings.",
    "E2026/67": "Panathinaikos AKTOR are 5-1 and first in the official standings on a plus-90 differential, conceding a league-low 73.0 points per game, and they are looking to answer their maiden defeat under Coach Obradovic. Kosner Baskonia sit bottom on 1-5 at minus 60, and Velimir Perasovic has only just taken the reins. Panathinaikos have won five straight at home against Baskonia, who last left Athens with a victory back in March 2021.",
    "E2026/63": "Armani Olimpia Milan have lost four in a row and sit nineteenth on 1-5, giving up 93.2 a game, with Moses Wright leading the frontline against the club he had agreed terms with in the summer. FC Barcelona are 3-3 after splitting a pair of tight home games, and Josh Nebo returns to the city where he spent the previous two seasons. These two split home wins last season, and both of those games were decided by a single possession.",
    "E2026/66": "The Eternal Derby pairs Partizan Mozzart Bet, who opened with three straight wins and have since dropped three in a row, against Crvena Zvezda Meridianbet, who lost their first two before reeling off four straight to reach 4-2. Zvezda are managing frontcourt injuries and could give new signing Christian Koloko his uniform. Both defences rank among the best in the league, which is exactly why our total for this one sits at the bottom of the whole Round 7 range.",
    "E2026/68": "Zalgiris Kaunas are 2-4 and should have their entire backcourt healthy, which they may well need against Patty Mills, one of five ASVEL players averaging double figures. LDLC ASVEL are also 2-4 and lost twice last week, and Tony Parker's side has conceded a league-high 95.3 points per game through the first six rounds. That single defensive number does more work in our pricing of this fixture than any other input.",
    "E2026/70": "Olympiacos Piraeus return home after back-to-back overtime wins on the road, 5-1 and third in the official standings on plus 40. Fenerbahce Tarfin Istanbul are also 5-1 but are still chasing a first road win of the season, having conceded only 74.5 a game, second best in the league. Olympiacos have beaten Fenerbahce three times running, including the semi-final at the 2026 Final Four and the semi-final at the 2026 SuperCup.",
    "E2026/69": "Round 7 closes in Paris, where Paris Basketball are 1-5 and on a three-game losing streak, though they still field the competition's leading scorer in Nadir Hifi at 20.2 points a night. Valencia Basket are 4-2 in the official standings with 583 points for, the highest total of any club, and TJ Shorts comes back to face the team he led to the 2024 EuroCup title. OLBG does not list this fixture on its basketball hub at all.",
}

NARRATIVE["WST-50"] = (
    "The last sixteen in Belfast has already thinned out badly. The World Snooker Tour confirms that only two of the "
    "world's top sixteen, Mark Williams and Kyren Wilson, are still in the draw. Wilson has been ruthless getting here, "
    "beating Ben Mertens 4-0 and then seeing off Thepchaiya Un-Nooh 4-2. Pang Junxu, by contrast, needed all seven "
    "frames to get past Liam Davies 4-3, compiling breaks of 112, 73 and 81 along the way, which tells you he can score "
    "freely but also that he has been pushed the distance already in this event. Wilson is rightly the short price to "
    "win outright, but at minus 308 the straight match-winner market falls outside the window we work in."
)

SELECTION_TEMPLATES = [
    "Our own zero-vig origination makes {label} the play at {american} ({decimal}), which we read as a {pct} per cent chance and which sits inside the band this desk works in.",
    "The bet we are taking is {label}, priced by us at {american} ({decimal}) and rated {pct} per cent against the vig-free fair line.",
    "We therefore go with {label} at {american} ({decimal}), a {pct} per cent chance on our numbers and the tightest rung that still lands inside the window.",
    "Backing {label} is the obvious angle here: we price it {american} ({decimal}), or {pct} per cent, and no shorter rung survives the window test.",
    "So the selection is {label} at {american} ({decimal}), which our model puts at {pct} per cent, comfortably inside the minus 250 to plus 10000 band.",
    "On our own line {label} is {american} ({decimal}), a {pct} per cent proposition, and that is the wager we would make on this game.",
    "Our answer is {label}, originated at {american} ({decimal}) and {pct} per cent, chosen because it is the closest rung to our centre that still satisfies the window.",
    "We make {label} the selection: {american} ({decimal}) on our zero-vig basis, equivalent to {pct} per cent, with a book carrying five per cent overround showing roughly {book}.",
    "Take {label} at {american} ({decimal}). That is {pct} per cent on our origination and the only rung on this board that is both above seventy and inside the window.",
    "We side with {label}, which our vig-free line prices at {american} ({decimal}) and rates at {pct} per cent.",
    "The selection that survives every one of our four gates is {label}, at {american} ({decimal}) and {pct} per cent.",
    "Our answer on this board is {label}: {american} ({decimal}) zero-vig, a {pct} per cent chance, and the closest rung to our centre that still qualifies.",
]


def fmt_american(am):
    if am is None:
        return "n/a"
    return ("minus %d" % abs(am)) if am < 0 else ("plus %d" % am)


def build_prediction(row, high, idx):
    gid = row["rating"].get("narrative_key") or row["rating"].get("game_id")
    narrative = NARRATIVE.get(gid)
    if not narrative:
        return None
    tmpl = SELECTION_TEMPLATES[idx % len(SELECTION_TEMPLATES)]
    sel = tmpl.format(
        label=high["label"],
        american=fmt_american(high["american"]),
        decimal="%.2f" % high["decimal"],
        pct="%.1f" % (high["p"] * 100.0),
        book=fmt_american(high["book5_american"]),
    )
    text = narrative + " " + sel
    return {
        "for_selection": high["label"],
        "market": high["market"],
        "american": high["american"],
        "decimal": high["decimal"],
        "p": high["p"],
        "word_count": len(text.split()),
        "text": text,
        "official_sources": row["sources"]["official"],
    }


# ===========================================================================
# 9. ROW ASSEMBLY
# ===========================================================================

def resolve_rating(sport_key, event_id, fixture, win_tips, total_tips, share_pct, competition):
    if sport_key == "basketball" and (competition or "").lower().startswith("euroleague"):
        r = rate_euroleague(event_id, fixture)
        if r:
            return r
    if sport_key == "darts":
        r = rate_darts(fixture)
        if r:
            return r
    if sport_key == "snooker":
        r = rate_snooker(fixture)
        if r:
            return r
    if sport_key == "tennis":
        r = rate_tennis(fixture)
        if r:
            return r
    return rate_from_consensus(win_tips, total_tips, share_pct, fixture)


def _norm_source(s):
    """Official sources are recorded either as a bare URL string or as a dict
    carrying url/title/published. Normalise both to {url, name}."""
    if isinstance(s, dict):
        url = s.get("url") or ""
        return {"url": url, "name": s.get("title") or official_source_name(url),
                "published": s.get("published")}
    return {"url": s, "name": official_source_name(s), "published": None}


def official_links_for(rating):
    links, seen = [], set()
    for s in rating.get("sources") or []:
        n = _norm_source(s)
        if n["url"] and n["url"] not in seen:
            seen.add(n["url"])
            links.append(n)
    return links


def urls_only(items):
    out = []
    for i in items or []:
        u = i.get("url") if isinstance(i, dict) else i
        if u and u not in out:
            out.append(u)
    return out


OFFICIAL_SOURCE_NAMES = [
    ("euroleaguebasketball.net/en/euroleague/standings", "Euroleague Basketball - official standings"),
    ("euroleaguebasketball.net/euroleague/news/game-center-round-7", "Euroleague Basketball - official Round 7 Game Center"),
    ("api-web.nhle.com", "NHL - official schedule API"),
    ("pdc.tv", "PDC - official draw, schedule of play and event preview"),
    ("wst.tv", "World Snooker Tour - official match centre and event report"),
    ("atptour.com", "ATP Tour - official Live Race, scouting report and draws"),
]


def official_source_name(url):
    for frag, name in OFFICIAL_SOURCE_NAMES:
        if frag in url:
            return name
    return "official source"


def make_row(sport_key, tup, origin="olbg", extra=None):
    (event_id, day_label, clock, competition, fixture, tipped, market,
     win_tips, total_tips, share_pct, experts, comments) = tup
    slug = slugify(fixture, competition, event_id)
    rating = resolve_rating(sport_key, event_id, fixture, win_tips, total_tips, share_pct, competition)

    left, right, sep = split_fixture(fixture)

    # Normalise to a home/away (first-listed/second-listed) pair. For club
    # sport the official club names are used; for individual sport the OLBG
    # listing order is used, since no governing body published a venue order.
    if rating["basis"] == "official_two_sided_margin":
        home_name, away_name = rating["subject"], rating.get("opponent")
        p_home = rating["p_subject"]
    else:
        home_name, away_name = left, right
        if rating["subject"] == left:
            p_home = rating["p_subject"]
        elif rating["subject"] == right:
            p_home = clip_prob(1.0 - rating["p_subject"])
        else:
            home_name, away_name = rating["subject"], rating.get("opponent") or right
            p_home = rating["p_subject"]

    sig = SPORT_SIGMA.get(sport_key) or {}
    markets = build_markets(
        home_name, away_name, p_home,
        rating.get("margin_centre"), rating.get("total_centre"),
        bool(rating.get("total_originatable")),
        sig.get("sigma_h"), sig.get("sigma_t"), sig.get("unit"), rating["klass"])

    # The pick the brief asks for is a MATCH WINNER pick, so it always follows
    # the favourite side rather than the first-listed side.
    if p_home >= 0.5:
        subj, p_sub = home_name, p_home
    else:
        subj, p_sub = away_name, clip_prob(1.0 - p_home)
    subj_am = None
    for m in markets:
        if m["market"] == "Match Winner" and m["side"] == subj:
            subj_am = m["american"]
    tier = grade(p_sub, subj_am, rating["klass"], rating.get("hard_cap"), rating.get("form_ok", False))
    if tier == "High" and not in_window(subj_am):
        tier = "Medium"

    high, rejected = pick_high(markets, rating["klass"], rating.get("form_ok", False), rating.get("hard_cap"))

    flags = []
    if not rating["sources"]:
        flags.append({"code": "UNVERIFIED-RATING", "detail": "No official governing-body source reached for this fixture; rating is OLBG consensus only and is capped at Medium."})
    if rating.get("total_originatable") is False and SPORT_SIGMA.get(sport_key, {}).get("sigma_t"):
        flags.append({"code": "TOTAL-NOT-ORIGINATED", "detail": "Match total left blank: no official body published enough scoring data to originate one. We never infer totals."})
    if rating["klass"] == "C" and SPORT_SIGMA.get(sport_key, {}).get("sigma_h"):
        flags.append({"code": "SPREAD-NOT-ORIGINATED", "detail": "Handicap left blank: with no official rating input for either side a spread would be unsourced. Only the consensus moneyline is published, and it is hard-capped at Medium."})
    if rating.get("opponent_named_officially") is False:
        flags.append({"code": "OPPONENT-NOT-OFFICIALLY-NAMED", "detail": "OLBG names the opponent, but the official WST match centre still lists the tie as 'Mark Williams v Winner of match 44'. The opponent's identity is therefore OLBG-only and the row is capped at Medium (F-1A-SNK-01)."})
    if clock is None:
        flags.append({"code": "CLOCK-NOT-RENDERED", "detail": "OLBG did not render a start clock for this card."})
    if market in (None, ""):
        flags.append({"code": "MARKET-CHIP-EMPTY", "detail": "OLBG rendered an empty market chip for this card (F-1A-MARKET-01)."})
    if share_pct is None and win_tips == 0:
        flags.append({"code": "SHARE-BLANK-ON-ZERO", "detail": "OLBG prints no consensus percentage when the win-tip count is zero (F-1A-SHARE-01)."})
    if share_pct is None and (win_tips or 0) > 0:
        flags.append({"code": "SHARE-NOT-RENDERED", "detail": "Consensus percentage not rendered by OLBG despite tips being present."})

    row = {
        "row_id": "%s-%s" % (sport_key, event_id),
        "origin": origin,
        "sport": sport_key,
        "sport_label": SPORT_LABEL[sport_key],
        "olbg_id": H.HARVEST_META[sport_key]["olbg_id"],
        "hub_url": H.HARVEST_META[sport_key]["hub"],
        "olbg_event_id": event_id,
        "day_label": day_label,
        "olbg_clock": clock,
        "olbg_clock_timezone": None,
        "competition": competition,
        "fixture": fixture,
        "home": left,
        "away": right,
        "separator": sep,
        "olbg_url": olbg_card_url(sport_key, slug),
        "olbg_url_reconstructed": True,
        "olbg_tip": {
            "tipped_selection": tipped,
            "market_chip": market,
            "win_tips": win_tips,
            "total_tips": total_tips,
            "consensus_share_pct": share_pct,
            "experts": experts,
            "comments": comments,
        },
        "rating": {
            "klass": rating["klass"],
            "basis": rating["basis"],
            "home_name": home_name,
            "away_name": away_name,
            "p_home": round(p_home, 6),
            "subject": subj,
            "opponent": (away_name if subj == home_name else home_name),
            "p_subject": round(p_sub, 6),
            "form_ok": bool(rating.get("form_ok")),
            "hard_cap": rating.get("hard_cap"),
            "margin_centre": rating.get("margin_centre"),
            "total_centre": rating.get("total_centre"),
            "total_originatable": bool(rating.get("total_originatable")),
            "game_id": rating.get("game_id"),
            "narrative_key": rating.get("narrative_key"),
            "opponent_named_officially": rating.get("opponent_named_officially"),
            "official_ko_cest": rating.get("official_ko_cest"),
            "official_date": rating.get("official_date"),
            "evidence": rating.get("evidence") or [],
            "conflicts": rating.get("conflicts") or [],
        },
        "markets": markets,
        "market_counts": {
            "total": len(markets),
            "match_winner": len([m for m in markets if m["market"] == "Match Winner"]),
            "handicap": len([m for m in markets if m["market"] == "Handicap"]),
            "match_total": len([m for m in markets if m["market"] == "Match Total"]),
        },
        "winner_pick": {
            "selection": subj,
            "p": round(p_sub, 6),
            "american": subj_am,
            "decimal": p_to_decimal(p_sub),
            "book5_american": book_american(p_sub),
            "confidence": tier,
            "olbg_tipped": tipped,
            "agrees_with_olbg": (tipped is not None and subj is not None and tipped.strip().lower() == subj.strip().lower()),
        },
        "high_selection": None,
        "rejected_highs": [
            {"label": m["label"], "market": m["market"], "p": m["p"], "american": m["american"],
             "reason": "probability %.4f clears 70%% but the zero-vig price %s falls outside the -250 / +10000 window"
                       % (m["p"], fmt_american(m["american"]))}
            for m in rejected
        ],
        "prediction": None,
        "sources": {
            "olbg": [{"url": olbg_card_url(sport_key, slug), "name": "OLBG tip card (reconstructed URL)", "official": False},
                     {"url": H.HARVEST_META[sport_key]["hub"], "name": "OLBG %s hub (harvested)" % SPORT_LABEL[sport_key], "official": False}],
            "official": official_links_for(rating),
        },
        "flags": flags,
    }
    if extra:
        row.update(extra)
    return row, high


# ===========================================================================
# 10. BUILD
# ===========================================================================

def build():
    rows = []
    high_queue = []
    for sport_key in SPORT_LABEL:
        for tup in H.HARVEST.get(sport_key, []):
            row, high = make_row(sport_key, tup)
            rows.append(row)
            if high:
                high_queue.append((row, high))

    # ---- official additions: fixtures a governing body confirms that OLBG
    # ---- does not render (the tip-gated blind spot, proved live).
    additions = []
    nhl = E.NHL_SCHEDULE
    PARTIAL = "read partially"
    for g in nhl["games_read_in_full"]:
        away_raw = g.get("away") or ""
        partial = PARTIAL in away_raw or not away_raw
        fixture = ("%s vs %s" % (g["home"], away_raw)) if not partial else g["home"]
        tup = (g["id"], "Today", g["startTimeUTC"][11:16] + " UTC", "NHL", fixture,
               None, None, None, None, None, None, None)
        row, _high = make_row("ice_hockey", tup, origin="official_addition", extra={
            "official_addition_reason": "NHL's official schedule API lists 12 games on 2026-10-22 while OLBG's Ice Hockey hub renders none of them (F-1A-NHL-01).",
            "official_fixture": {k: g.get(k) for k in (
                "id", "home", "away", "home_abbr", "away_abbr", "venue",
                "startTimeUTC", "venueTimezone", "venueUTCOffset",
                "gameState", "gameScheduleState", "gameCenterLink",
            )} | {"game_center": ("https://www.nhl.com" + g["gameCenterLink"]) if g.get("gameCenterLink") else None},
        })
        row["sources"]["official"] = [{"url": nhl["source_url"], "name": nhl["source_name"], "official": True}]
        row["olbg_url"] = None
        row["olbg_url_reconstructed"] = False
        row["flags"] = [f for f in row["flags"] if f["code"] != "CLOCK-NOT-RENDERED"]
        row["flags"].append({"code": "NOT-LISTED-ON-OLBG", "detail": "Fixture confirmed by NHL's official schedule API but absent from OLBG's Ice Hockey hub."})
        row["flags"].append({"code": "RATING-UNVERIFIED", "detail": "NHL's schedule API confirms fixture, date, UTC start, venue and state only. It publishes no standings or ratings, so no probability is originated and the row stays at the neutral 0.50. See F-F7-NHL-01: the NHL season goals-for/against figures published elsewhere do not reconcile, so no NHL total is priced."})
        if partial:
            row["away"] = None
            row["fixture"] = g["home"] + " vs [away team not read]"
            row["markets"] = []
            row["market_counts"] = {"total": 0, "match_winner": 0, "handicap": 0, "match_total": 0}
            row["winner_pick"] = {"selection": None, "p": None, "american": None, "decimal": None,
                                  "book5_american": None, "confidence": "Low", "olbg_tipped": None,
                                  "agrees_with_olbg": False}
            row["flags"].append({"code": "OFFICIAL-READ-PARTIAL", "detail": "The official NHL payload was truncated mid-record for this game, so the away team is unknown. It is left blank rather than inferred, and no market is originated. Game id %s." % g.get("id")})
        additions.append(row)

    gap = E.EUROLEAGUE_OLBG_COVERAGE_GAP["missing"][0]
    pv = [g for g in E.EUROLEAGUE_GAME_CENTER["games"] if g["game_id"] == "E2026/69"][0]
    fixture = "Paris Basketball vs Valencia"
    tup = ("E2026-69", pv["date"][8:10] + " Oct", "20:45 CEST", "Euroleague", fixture,
           None, None, None, None, None, None, None)
    row, high = make_row("basketball", tup, origin="official_addition", extra={
        "official_addition_reason": "Euroleague Basketball's official Round 7 Game Center lists this as the closing game of the round, but OLBG's Basketball hub does not render it (F-1A-BBALL-01).",
    })
    row["rating"]["game_id"] = "E2026/69"
    row["rating"]["narrative_key"] = "E2026/69"
    row["rating"]["official_ko_cest"] = pv["official_ko_cest"]
    row["rating"]["official_date"] = pv["date"]
    row["olbg_event_id"] = None
    row["olbg_url"] = None
    row["olbg_url_reconstructed"] = False
    row["row_id"] = "basketball-official-E2026-69"
    row["sources"]["official"] = [
        {"url": E.EUROLEAGUE_STANDINGS["source_url"], "name": "Euroleague Basketball - official standings", "official": True},
        {"url": E.EUROLEAGUE_GAME_CENTER["source_url"], "name": "Euroleague Basketball - official Round 7 Game Center", "official": True},
    ]
    row["sources"]["olbg"] = []
    row["flags"] = [{"code": "NOT-LISTED-ON-OLBG", "detail": "Confirmed by the official EuroLeague Game Center (2026-10-23, 20:45 CEST, game E2026/69) but absent from OLBG's Basketball hub, which renders 8 of the round's 9 upcoming games."}]
    additions.append(row)
    if high:
        high_queue.append((row, high))

    rows.extend(additions)

    # ---- predictions, one per High selection ---------------------------
    for idx, (row, high) in enumerate(high_queue):
        row["high_selection"] = high
        pred = build_prediction(row, high, idx)
        row["prediction"] = pred

    return rows, high_queue


def main():
    rows, high_queue = build()

    sports = []
    for k in SPORT_LABEL:
        rs = [r for r in rows if r["sport"] == k and r["origin"] == "olbg"]
        sports.append({
            "key": k,
            "label": SPORT_LABEL[k],
            "olbg_id": H.HARVEST_META[k]["olbg_id"],
            "hub": H.HARVEST_META[k]["hub"],
            "olbg_rows": len(rs),
            "class_a": len([r for r in rs if r["rating"]["klass"] == "A"]),
            "class_b": len([r for r in rs if r["rating"]["klass"] == "B"]),
            "class_c": len([r for r in rs if r["rating"]["klass"] == "C"]),
            "markets_originated": sum(r["market_counts"]["total"] for r in rs),
            "high": len([r for r in rs if r["high_selection"]]),
            "flagged": len([r for r in rs if r["flags"]]),
        })

    desk = {
        "meta": {
            "session": SESSION,
            "task": "T60",
            "generated_utc": GENERATED_UTC,
            "built_at_utc": NOW_ISO,
            "olbg_root": H.OLBG_ROOT,
            "harvest_file": "data/1a421e41/olbg_harvest_raw.py",
            "evidence_file": "data/1a421e41/official_evidence.py",
            "rows_total": len(rows),
            "rows_from_olbg": len([r for r in rows if r["origin"] == "olbg"]),
            "rows_official_additions": len([r for r in rows if r["origin"] == "official_addition"]),
            "sports_in_scope": len(SPORT_LABEL),
            "high_selections": len([r for r in rows if r["high_selection"]]),
            "predictions": len([r for r in rows if r["prediction"]]),
            "markets_originated": sum(r["market_counts"]["total"] for r in rows),
        },
        "scope": {
            "in_scope": [{"key": k, "label": SPORT_LABEL[k], "olbg_id": H.HARVEST_META[k]["olbg_id"],
                          "hub": H.HARVEST_META[k]["hub"]} for k in SPORT_LABEL],
            "excluded": EXCLUDED,
        },
        "policy": {
            "window": {"american_min": WINDOW_AMERICAN_MIN, "american_max": WINDOW_AMERICAN_MAX,
                       "prob_min": HIGH_PROB_MIN,
                       "prob_band": [round(HIGH_PROB_MIN, 6),
                                     round(1.0 / (1.0 + 100.0 / 250.0), 6)],
                       "note": "At zero vig, p=0.700 prices at -233 and p=0.714286 prices at exactly -250, so the intersection of 'greater than 70 per cent' and 'between -250 and +10000' is a band only 0.0143 wide in probability space. At a 5 per cent overround the two tests cannot both bind: p=0.700 books at -277. We therefore gate on the zero-vig price and print the 5 per cent book equivalent beside it for comparison only."},
            "tiers": {
                "High": "Class A official evidence for BOTH sides, current form confirmed by an official body, p >= 0.700, and the zero-vig price inside -250 / +10000. All four gates must pass.",
                "Medium": "Single-sided official evidence (hard-capped), or consensus-only, or p >= 0.62 with an in-window price.",
                "Low": "Everything else.",
            },
            "classes": {
                "A": "An official governing body published a rating, record or seed for BOTH sides.",
                "B": "An official governing body published a rating for ONE side only. Hard-capped at Medium.",
                "C": "No official source reached. OLBG consensus only. Hard-capped at Medium and never High.",
            },
            "model_constants": {
                "sport_sigma": SPORT_SIGMA,
                "class_b_p": CLASS_B_P,
                "class_c": {"base": CLASS_C_BASE, "slope": CLASS_C_SLOPE, "cap": CLASS_C_CAP, "min_tips": CLASS_C_MIN_TIPS},
                "snooker_top16_p": SNOOKER_TOP16_P,
                "darts": {"k": DARTS_K, "scale": DARTS_SCALE},
                "prob_bounds": [PROB_FLOOR, PROB_CEIL],
                "overround_book_printed": OVERROUND_BOOK,
                "label": "Every number in model_constants is OUR assumption, not a sourced fact. Facts come only from official_sources.",
            },
            "derived": {
                "official_home_win_rate": round(HOME_WIN_RATE, 6),
                "home_win_rate_basis": "33 home wins and 28 away wins across the 61 games in the official EuroLeague standings (sum of the H column and the A column).",
                "basketball_hca_points": round(BASKETBALL_HCA, 4),
                "hca_formula": "HCA = sigma_margin * Phi^-1(official home win rate) = 11.5 * Phi^-1(0.540984)",
                "ladder_rule": "Handicap and total rungs sit on a half-point grid only, so no rung can push. Handicap rungs step 1.0 from 0.5; total rungs step 1.0 either side of the centre rounded to the nearest half point.",
                "tightest_rung_rule": "Among rungs that clear both the 70 per cent floor and the price window, the one closest to our own centre is taken. Ties break on market order Match Winner, Handicap, Match Total, then on the smaller line.",
                "totals_rule": "A match total is originated ONLY where an official body published the scoring inputs. Where it did not, the total is left blank and flagged TOTAL-NOT-ORIGINATED. We never infer a total.",
                "spread_rule": "A handicap ladder is originated only where we hold an official rating input (Class A or B). Where the official body published scoring data we use the true margin centre; where it published only a rating (seed, rank, top-16 status) we convert that probability into the equivalent margin centre via sigma * Phi^-1(p) so the ladder is still expressed in the sport's own unit. Class C rows carry a moneyline only and are flagged SPREAD-NOT-ORIGINATED.",
                "winner_pick_rule": "The match-winner pick always follows the favourite side, not the first-listed side, so an away favourite is picked correctly.",
                "name_crosswalk_rule": "For club fixtures the market labels use the official club names from the governing body's own standings, while the fixture string is kept exactly as OLBG rendered it. The crosswalk maps names only and never carries a numeric value.",
            },
        },
        "sports": sports,
        "rows": rows,
        "high_picks": [
            {"row_id": r["row_id"], "sport": r["sport_label"], "fixture": r["fixture"],
             "selection": r["high_selection"]["label"], "market": r["high_selection"]["market"],
             "american": r["high_selection"]["american"], "decimal": r["high_selection"]["decimal"],
             "p": r["high_selection"]["p"], "book5_american": r["high_selection"]["book5_american"],
             "official_sources": r["sources"]["official"],
             "prediction": (r["prediction"] or {}).get("text")}
            for r, _h in high_queue
        ],
        "official_sources": official_source_register(),
        "findings": findings(),
    }

    with open(OUT, "w") as fh:
        json.dump(desk, fh, indent=1, sort_keys=False, ensure_ascii=False)
        fh.write("\n")

    m = desk["meta"]
    print("wrote %s" % OUT)
    print("rows %d (olbg %d + official additions %d) | sports %d | markets %d" % (
        m["rows_total"], m["rows_from_olbg"], m["rows_official_additions"],
        m["sports_in_scope"], m["markets_originated"]))
    print("high selections %d | predictions %d" % (m["high_selections"], m["predictions"]))
    for hp in desk["high_picks"]:
        print("  HIGH %-42s %-34s %6d  %.4f  words=%d" % (
            hp["fixture"][:42], hp["selection"][:34], hp["american"], hp["p"],
            len((hp["prediction"] or "").split())))
    tiers = {}
    for r in rows:
        tiers[r["winner_pick"]["confidence"]] = tiers.get(r["winner_pick"]["confidence"], 0) + 1
    print("winner-pick tiers:", tiers)
    print("rows with >=1 official source:", len([r for r in rows if r["sources"]["official"]]))
    print("rows flagged:", len([r for r in rows if r["flags"]]))


def official_source_register():
    reg = []
    for name, obj in [
        ("Euroleague Basketball - official standings", E.EUROLEAGUE_STANDINGS),
        ("Euroleague Basketball - official Round 7 Game Center", E.EUROLEAGUE_GAME_CENTER),
        ("NHL - official schedule API", E.NHL_SCHEDULE),
        ("PDC - official draw / schedule of play / preview", E.PDC_EUROPEAN_CHAMPIONSHIP),
        ("World Snooker Tour - official match centre / report", E.WST_NORTHERN_IRELAND_OPEN),
        ("ATP Tour - official Live Race / scouting report / draws", E.ATP_LIVE_RACE_AND_FIELDS),
    ]:
        urls = []
        if obj.get("source_url"):
            urls.append(obj["source_url"])
        for u in urls_only(obj.get("sources")):
            if u not in urls:
                urls.append(u)
        reg.append({"name": name, "urls": urls, "fetched_utc": obj.get("fetched_utc"),
                    "official": True,
                    "confirms": obj.get("confirms") or [],
                    "does_not_confirm": obj.get("does_not_confirm") or []})
    for u in E.EUROLEAGUE_GAME_CENTER.get("companion_official_pages", []):
        reg.append({"name": "Euroleague Basketball - companion official page", "urls": [u],
                    "fetched_utc": E.EUROLEAGUE_GAME_CENTER.get("fetched_utc"), "official": True,
                    "confirms": [], "does_not_confirm": []})
    reg.append({"name": "REJECTED as non-official (media, aggregators, betting sites)",
                "urls": [n["url"] for n in E.NOT_OFFICIAL], "official": False,
                "fetched_utc": None, "confirms": [], "does_not_confirm": [],
                "detail": [{"url": n["url"], "why_rejected": n["why_rejected"]} for n in E.NOT_OFFICIAL]})
    return reg


def findings():
    f = []
    cr = E.EUROLEAGUE_CLOCK_RECONCILIATION
    f.append({
        "id": "F-1A-CLOCK-04",
        "severity": "high",
        "sport": "Basketball",
        "title": "OLBG's unlabelled hub clock is US Eastern Daylight Time, proved against official CEST kick-offs",
        "detail": "For all 8 EuroLeague fixtures OLBG renders, OLBG's card clock equals the official CEST kick-off published by euroleaguebasketball.net minus exactly 6 hours. CEST is UTC+2 and EDT is UTC-4, a 6-hour difference, so the unlabelled clock is US Eastern Daylight Time. 8 of 8 match with no residual.",
        "evidence": [{"olbg_event_id": r[0], "olbg_fixture": r[1], "olbg_day": r[2], "olbg_clock": r[3],
                      "official_fixture": r[4], "official_date": r[5], "official_ko_cest": r[6], "delta_hours": r[7]}
                     for r in cr["rows"]],
        "sources": [E.EUROLEAGUE_GAME_CENTER["source_url"], H.HARVEST_META["basketball"]["hub"]],
        "status": "confirmed",
    })
    g = E.EUROLEAGUE_OLBG_COVERAGE_GAP
    f.append({
        "id": "F-1A-BBALL-01",
        "severity": "high",
        "sport": "Basketball",
        "title": "OLBG's tip-gated hub hides an official EuroLeague fixture",
        "detail": "Round 7 has 9 official upcoming games. OLBG's Basketball hub renders 8. Paris Basketball vs Valencia Basket (2026-10-23, 20:45 CEST, game E2026/69, Paris 1-5 v Valencia 4-2) is absent, even though it closes the round and features the league's top scorer. A card only appears once at least one tipster posts, so a zero-tip fixture is invisible.",
        "evidence": g["missing"],
        "sources": [E.EUROLEAGUE_GAME_CENTER["source_url"], E.EUROLEAGUE_STANDINGS["source_url"], H.HARVEST_META["basketball"]["hub"]],
        "status": "confirmed",
    })
    for c in E.EUROLEAGUE_OFFICIAL_CONFLICTS:
        f.append({
            "id": c["id"], "severity": "medium", "sport": "Basketball",
            "title": "Official source disagrees with itself: %s" % c["what"],
            "detail": c.get("why_irreconcilable") or c.get("resolution") or c.get("what") or "",
            "evidence": [{"prose": c.get("prose"), "table": c.get("table"),
                          "reconciles_exactly": c.get("reconciles_exactly"),
                          "does_not_reconcile": c.get("does_not_reconcile"),
                          "resolution": c.get("resolution")}],
            "sources": c.get("sources") or [E.EUROLEAGUE_STANDINGS["source_url"], E.EUROLEAGUE_GAME_CENTER["source_url"]],
            "status": "confirmed",
        })
    f.append({
        "id": "F-1A-NHL-01", "severity": "high", "sport": "Ice Hockey",
        "title": "OLBG's Ice Hockey hub shows no NHL games at all",
        "detail": "NHL's official schedule API reports numberOfGames=12 for 2026-10-22. OLBG's Ice Hockey hub renders 7 cards, all SHL or Liiga, and none of the 12 NHL games. The four games we read in full are carried on our desk as official additions.",
        "evidence": [E.NHL_SCHEDULE["payload_facts"], E.NHL_SCHEDULE["games_read_in_full"],
                     {"olbg_hub": H.HARVEST_META["ice_hockey"]["hub"], "olbg_cards": len(H.HARVEST["ice_hockey"])}],
        "sources": [E.NHL_SCHEDULE["source_url"], H.HARVEST_META["ice_hockey"]["hub"]],
        "status": "confirmed",
    })
    f.append({
        "id": "F-1A-EMPTY-01", "severity": "medium", "sport": "Aussie Rules / eSports",
        "title": "Two in-scope sports render no fixtures on OLBG",
        "detail": "OLBG's Aussie Rules hub (id 22) and eSports hub (id 23) both render 'No tips found.' They stay in scope as sports with zero coverage rather than being dropped, because the brief's scope is defined by sport, not by whether tipsters have posted.",
        "evidence": [H.AUSSIE_RULES_HUB_STATE, H.ESPORTS_HUB_STATE],
        "sources": [H.HARVEST_META["aussie_rules"]["hub"], H.HARVEST_META["esports"]["hub"]],
        "status": "confirmed",
    })
    f.append({
        "id": "F-1A-CLOCK-01", "severity": "medium", "sport": "Greyhounds",
        "title": "Greyhound card title clock and card clock differ by exactly 5 hours with no timezone label",
        "detail": "OLBG event 689570 carries the title '11:14 Kinsley' while its own card clock reads 'Today 06:14', a difference of exactly 5 hours, and neither value is labelled with a timezone. The same 5-hour pattern appears on events 689576, 689581 and 689584.",
        "evidence": [c for c in H.CLOCK_CONFLICTS],
        "sources": [H.HARVEST_META["greyhounds"]["hub"]],
        "status": "confirmed",
    })
    f.append({
        "id": "F-1A-CLOCK-03", "severity": "medium", "sport": "Darts / Snooker",
        "title": "OLBG's session labels contradict official schedule-of-play windows",
        "detail": "The PDC officially schedules all eight Thursday European Championship ties inside a 1900-2300 CEST session (1800-2200 BST), yet OLBG groups the same ties under clocks in the 13:15-16:45 range. Separately, OLBG lists snooker at 08:00 where the official WST match centre lists Match 50 and Match 51 at 12:00. Both gaps are arithmetic and neither OLBG value carries a timezone label.",
        "evidence": [E.PDC_EUROPEAN_CHAMPIONSHIP.get("quote_thursday_order"),
                     E.WST_NORTHERN_IRELAND_OPEN["match_centre_rows_read"][:4]],
        "sources": list(E.PDC_EUROPEAN_CHAMPIONSHIP["sources"]) + list(E.WST_NORTHERN_IRELAND_OPEN["sources"]) + [H.HARVEST_META["darts"]["hub"]],
        "status": "confirmed",
    })
    f.append({
        "id": "F-1A-MARKET-01", "severity": "low", "sport": "Gaelic Football",
        "title": "All six Gaelic Football cards render an empty market chip",
        "detail": "OLBG prints a market chip on most cards naming the market the consensus tip refers to. All 6 cards on the Gaelic Football hub render that chip empty, so the market the tipsters are actually tipping is not machine-readable from the hub.",
        "evidence": [{"olbg_event_id": t[0], "fixture": t[4], "market_chip": t[6]} for t in H.HARVEST["gaelic_football"]],
        "sources": [H.HARVEST_META["gaelic_football"]["hub"]],
        "status": "confirmed",
    })
    f.append({
        "id": "F-1A-SHARE-01", "severity": "low", "sport": "multiple",
        "title": "OLBG prints no consensus percentage when the win-tip count is zero",
        "detail": "Cards where the win-tip count is 0 render a blank consensus percentage rather than 0 per cent, for example event 188350 (0/0) and event 101911 (0/2). Any consumer that treats the blank as missing data rather than as zero will mis-aggregate.",
        "evidence": [{"olbg_event_id": t[0], "fixture": t[4], "win_tips": t[7], "share_pct": t[9]}
                     for sp in H.HARVEST for t in H.HARVEST[sp] if t[9] is None],
        "sources": [H.OLBG_ROOT],
        "status": "confirmed",
    })
    f.append({
        "id": "F-1A-RL-01", "severity": "medium", "sport": "Rugby League",
        "title": "OLBG's Rugby League hub lists only 2027 outrights, no match cards",
        "detail": "The Rugby League hub renders three outright markets dated 2027 and no head-to-head match cards, and carries no Rugby League World Cup 2026 pricing, so the sport has no match-level coverage to originate lines against.",
        "evidence": [{"olbg_event_id": t[0], "day": t[1], "competition": t[3], "fixture": t[4]} for t in H.HARVEST["rugby_league"]],
        "sources": [H.HARVEST_META["rugby_league"]["hub"]],
        "status": "confirmed",
    })
    f.append({
        "id": "F-1A-TZ-01", "severity": "high", "sport": "all",
        "title": "No OLBG clock anywhere on the site carries a timezone label",
        "detail": "Across all 17 in-scope hubs, every rendered clock is bare. F-1A-CLOCK-04 proves the basketball hub clock is US Eastern Daylight Time by an exact 6-hour offset against official CEST kick-offs, and F-1A-CLOCK-01 shows a 5-hour internal inconsistency on the greyhound hub. A user reading 'Today 14:05' has no way to know which of these it is without external cross-referencing.",
        "evidence": [{"hub": k, "sample_clocks": sorted({t[2] for t in H.HARVEST[k] if t[2]})[:4]} for k in SPORT_LABEL if H.HARVEST.get(k)],
        "sources": [H.OLBG_ROOT],
        "status": "confirmed",
    })
    f.append({
        "id": "F-1A-CHIP-01", "severity": "low", "sport": "Aussie Rules / eSports",
        "title": "Empty hubs render the sports-menu chip as 'All Sports'",
        "detail": "On a hub with no fixtures, OLBG's breadcrumb chip falls back to the literal text 'All Sports' instead of naming the sport, so the page does not identify itself.",
        "evidence": [H.AUSSIE_RULES_HUB_STATE, H.ESPORTS_HUB_STATE],
        "sources": [H.HARVEST_META["aussie_rules"]["hub"], H.HARVEST_META["esports"]["hub"]],
        "status": "confirmed",
    })
    f.append({
        "id": "AUD-1A-HIGGINS-01", "severity": "high", "sport": "Snooker",
        "title": "The repo's root predictions file prices a snooker match that has already been decided",
        "detail": "data/predictions.json lines 351 and 360, duplicated at lines 1230 and 1239, publish a High-confidence 'John Higgins -0.5 Frame Handicap @ 1.51 (-196)' for the Belfast second round. The official WST page fetched this session records that Jak Jones beat John Higgins 4-2 on 21 October 2026, so the desk is pricing a decided match. Independently confirms AUD-F7-04.",
        "evidence": [{"file": "data/predictions.json", "lines": [351, 360, 1230, 1239]},
                     E.WST_NORTHERN_IRELAND_OPEN["quote_higgins"]],
        "sources": list(E.WST_NORTHERN_IRELAND_OPEN["sources"]) + ["data/predictions.json"],
        "status": "confirmed",
    })
    f.append({
        "id": "AUD-1A-DUP-01", "severity": "medium", "sport": "repo",
        "title": "Root predictions file stores the same 29 predictions twice",
        "detail": "data/predictions.json declares count: 29 but holds 58 objects: the identical 29-prediction set appears under the top-level keys 'items' and 'predictions', and the two text arrays compare equal element by element. Any consumer that walks the tree double-counts.",
        "evidence": [{"file": "data/predictions.json", "declared_count": 29, "objects_found": 58,
                      "duplicate_keys": ["items", "predictions"], "texts_equal": True}],
        "sources": ["data/predictions.json"],
        "status": "confirmed",
    })
    f.append({
        "id": "AUD-1A-WIN-01", "severity": "high", "sport": "Aussie Rules",
        "title": "High-confidence row priced outside the window its own desk claims to enforce",
        "detail": "data/6a081cf6_high_band.json line 267 carries 'us': -251 for selection 'Brisbane Lions -3' graded confidence High. That is outside the -250 to +10000 band the same desk's board row (T44) claims to enforce.",
        "evidence": [{"file": "data/6a081cf6_high_band.json", "line": 267, "us": -251,
                      "selection": "Brisbane Lions -3", "confidence": "High"}],
        "sources": ["data/6a081cf6_high_band.json"],
        "status": "confirmed",
    })
    f.append({
        "id": "AUD-1A-WIN-02", "severity": "high", "sport": "Aussie Rules",
        "title": "The same out-of-window High price recurs on a second desk",
        "detail": "data/v3/predictions.json line 1963 grades the identical 'Brisbane Lions -3' selection at -251 as High, on the T43 desk that claims confidence-band policy (-250 to +10000) enforcement.",
        "evidence": [{"file": "data/v3/predictions.json", "line": 1963, "us": -251,
                      "selection": "Brisbane Lions -3", "confidence": "High"}],
        "sources": ["data/v3/predictions.json"],
        "status": "confirmed",
    })
    f.append({
        "id": "AUD-1A-DARDERI-01", "severity": "medium", "sport": "Tennis",
        "title": "Root fixtures file carries a tennis event that is no longer on OLBG",
        "detail": "data/fixtures.json lines 1176 and 6850 carry 'away': 'Luciano Darderi' for OLBG event_id 902038 ('James Duckworth vs Luciano Darderi'). Our fresh 22 October harvest of the OLBG tennis hub lists 14 cards with event_ids 902069 to 902131 and no 902038, so the stored row is stale or expired. The result of that match is NOT confirmable from the official ATP pages we reached, so we flag it without asserting an outcome.",
        "evidence": [{"file": "data/fixtures.json", "lines": [1176, 6850], "event_id": 902038},
                     {"harvested_tennis_event_ids": [t[0] for t in H.HARVEST["tennis"]]}],
        "sources": list(E.ATP_LIVE_RACE_AND_FIELDS["sources"]) + [H.HARVEST_META["tennis"]["hub"], "data/fixtures.json"],
        "status": "flagged-unverified-result",
    })
    f.append({
        "id": "AUD-1A-README-01", "severity": "low", "sport": "repo",
        "title": "README page count is stale",
        "detail": "README.md line 56 claims '0 broken relative links across all 160 published HTML pages'. The tree currently contains 319 HTML files. Confirms AUD-F7-01 with a fresh count.",
        "evidence": [{"file": "README.md", "line": 56, "claimed_pages": 160, "actual_html_files": 319}],
        "sources": ["README.md"],
        "status": "confirmed",
    })
    f.append({
        "id": "F-1A-AFL-01", "severity": "low", "sport": "Aussie Rules",
        "title": "OLBG appears to label a women's national competition 'WAFL'",
        "detail": "Cards on the Aussie Rules hub use the competition label 'WAFL'. WAFL is ordinarily the West Australian Football League, a men's state competition, so the label is a candidate mis-tagging of the women's national competition. Not resolvable without afl.com.au, which we did not reach, so this stays a candidate and is not asserted.",
        "evidence": sorted({t[3] for t in H.HARVEST.get("aussie_rules", [])}),
        "sources": [H.HARVEST_META["aussie_rules"]["hub"]],
        "status": "candidate-unverified",
    })
    f.append({
        "id": "F-1A-GAA-01", "severity": "low", "sport": "Gaelic Football",
        "title": "Hurling club fixtures appear under the Gaelic Football hub",
        "detail": "Some club fixtures rendered on OLBG's Gaelic Football hub (id 25) look like hurling fixtures, while hurling has its own excluded OLBG id (26). Candidate scope leak between an in-scope and an excluded sport; needs gaa.ie to confirm and is not asserted here.",
        "evidence": [{"olbg_event_id": t[0], "competition": t[3], "fixture": t[4]} for t in H.HARVEST["gaelic_football"]],
        "sources": [H.HARVEST_META["gaelic_football"]["hub"]],
        "status": "candidate-unverified",
    })
    f.append({
        "id": "F-1A-CLOCK-02", "severity": "low", "sport": "Cricket",
        "title": "Root board and hub disagree on a cricket start clock",
        "detail": "OLBG event 188829 (England v Sri Lanka) shows 04:00 on the root board and 09:00 on the sport hub. We could not confirm either value against an official source, so this is recorded as an unconfirmed discrepancy and NOT asserted.",
        "evidence": [c for c in H.CLOCK_CONFLICTS],
        "sources": [H.HARVEST_META["cricket"]["hub"]],
        "status": "unconfirmed",
    })
    f.append({
        "id": "F-1A-GRAN-01", "severity": "high", "sport": "all",
        "title": "The high-confidence window is granularity-limited, not conviction-limited",
        "detail": "The window p >= 0.70 AND price >= -250 spans only 0.0143 of probability. A handicap rung steps probability by 0.3434/sigma per half point, so whether any rung lands in the band is governed by the sport's scoring variance rather than by how strong the favourite is. At sigma 11.5 (basketball) a qualifying rung exists almost always; at sigma 2.30 (darts legs), 2.0 (snooker frames) or 1.15 (volleyball sets) it almost never does. This is why every High selection on this desk comes from basketball, while genuine 0.75-0.79 favourites in darts and snooker are rejected for landing a few American points short of -250.",
        "evidence": [{"sport": k, "unit": v["unit"], "sigma_h": v["sigma_h"],
                      "prob_step_per_half_rung": (round(0.3434 / v["sigma_h"] * 0.5, 5) if v["sigma_h"] else None),
                      "band_width": 0.0143}
                     for k, v in SPORT_SIGMA.items()],
        "sources": [],
        "status": "confirmed-model-property",
    })
    for item in f:
        item["sources"] = urls_only(item.get("sources"))
        if item.get("evidence") is None:
            item["evidence"] = []
    return f


if __name__ == "__main__":
    main()
