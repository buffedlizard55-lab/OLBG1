"""
s8fc47dcb_data.py — T60 fresh 22-Oct future-only desk: dataset builder.

WHAT THIS DOES
--------------
1. Loads the primary desk (`data/fixtures.json`, read-only — never edited here).
2. Applies an explicit cutoff (2026-10-22T07:30:00Z): started rows are expired,
   undated rows are listed separately, only dated future rows are priced.
3. Applies the in-session verification overlay below. Every overlay entry is a
   value actually read on an official governing-body page on 2026-10-22 via the
   page-fetch tool (NHL official API, EuroLeague, EHF, LNR Top 14, IRL, NRL,
   ICC, NZC). Rows that could not be re-read carry the named blocker and are
   capped below High. Nothing is inferred; unverified values stay as stored
   and are labelled `not-rechecked`.
4. Originates OUR OWN fair-price (0% overround) lines reusing the root model's
   published sport constants (`scripts/model.py`), with an extended handicap
   ladder (50/60/70/80% favourite-cover rungs, half-point lines) and a 5-run
   total ladder. Fair pricing is used because at any positive margin a >=70%
   selection cannot be quoted at -250 or longer (at 5% vig the ceiling is
   68.05%); the 5%-vig price is still printed next to every fair quote.
5. Confidence: High (strict) requires ALL of: fixture status `verified`,
   measured official ratings on both sides, two-way win probability >= 0.60
   (so a coin flip cannot manufacture a High via a plus-handicap), an exact
   selected-line probability >= 0.70 with fair odds inside 1.40..101.00
   (i.e. -250..+10000), and an in-session official-source re-read of the row
   (`confirmed` or `corrected`). Cricket Highs are restricted to the match
   winner (T20 margins are runs-or-wickets bimodal; a runs handicap is not a
   sound expression of the edge). Medium = both-measured, verified, clears
   the sport's root medium floor. Low = everything else.

Outputs: data/8fc47dcb/*.json  (this session's namespace only)
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import model as M  # root model: published constants + math helpers (read-only)

OUT = ROOT / "data" / "8fc47dcb"
CUTOFF = "2026-10-22T07:30:00Z"
CHECKED_AT = "2026-10-22T07:26-08:00Z (page-fetch reads, this session)"

# ---------------------------------------------------------------------------
# In-session verification overlay — ONLY values read on official pages today.
# rating changes are applied only where the rating is a direct function of
# the official number (win% / points% / IRL ranking %). Where the root rating
# is a hand mapping with no published formula (handball groups, Top 14), the
# FACTS are confirmed/corrected in the label and the rating is retained,
# which is stated on the row.
# ---------------------------------------------------------------------------
OVERLAY = {
    # --- NHL: schedule + standings/2026-10-20 both read this session ---
    "nhl-2026020154": dict(
        status="confirmed",
        evidence="NHL schedule API lists game 2026020154 as Nashville Predators @ Boston Bruins, TD Garden, 2026-10-22T23:00:00Z, gameState FUT. NHL standings 2026-10-20: Boston Bruins 7-2-1, pointPctg .750, GD +14, home 3-1-0; Nashville Predators 3-2-3, pointPctg .5625, GD -1. Both stored inputs match exactly.",
        sources=[("NHL official schedule API (2026-10-22)", "https://api-web.nhle.com/v1/schedule/2026-10-22"),
                 ("NHL official standings API (2026-10-20)", "https://api-web.nhle.com/v1/standings/2026-10-20")]),
    "nhl-2026020155": dict(
        status="confirmed",
        evidence="NHL schedule API lists game 2026020155 as New York Rangers @ Toronto Maple Leafs, Scotiabank Arena, 2026-10-22T23:00:00Z, FUT. Standings 2026-10-20: Toronto Maple Leafs 5-4-2, .545; New York Rangers 7-3-1, .682. Stored points percentages match (the Rangers goal-difference sub-value was not in the read chunk and is not used).",
        sources=[("NHL official schedule API (2026-10-22)", "https://api-web.nhle.com/v1/schedule/2026-10-22"),
                 ("NHL official standings API (2026-10-20)", "https://api-web.nhle.com/v1/standings/2026-10-20")]),
    "nhl-2026020158": dict(
        status="confirmed",
        evidence="NHL schedule API lists game 2026020158 as Florida Panthers @ Pittsburgh Penguins, PPG Paints Arena, 2026-10-22T23:00:00Z, FUT. Standings 2026-10-20: Pittsburgh Penguins 3-6-1, .350, streak L4; Florida Panthers 5-2-2, .667, streak W3, GD +5. Stored inputs match.",
        sources=[("NHL official schedule API (2026-10-22)", "https://api-web.nhle.com/v1/schedule/2026-10-22"),
                 ("NHL official standings API (2026-10-20)", "https://api-web.nhle.com/v1/standings/2026-10-20")]),
    "nhl-2026020160": dict(
        status="corrected",
        evidence="NHL schedule API lists game 2026020160 as Vegas Golden Knights @ St. Louis Blues, Enterprise Center, 2026-10-23T00:00:00Z, FUT. Standings 2026-10-20 (standingsDateTimeUtc 2026-10-22T07:32:20Z on re-read): St. Louis Blues 4-4-1, .500 (stored correct); Vegas Golden Knights 8-3-0, .727, GD +14, streak L1 — the stored 8-2-0 / .800 / W3 snapshot is superseded (root desk already disclosed this drift). Away rating corrected 80.0 -> 72.7 and the match re-priced.",
        inputs=dict(away=dict(label="Points percentage", value="0.727 (8-3-0, +14 GD, L1 streak) — corrected 2026-10-22", rating=72.7)),
        sources=[("NHL official schedule API (2026-10-22)", "https://api-web.nhle.com/v1/schedule/2026-10-22"),
                 ("NHL official standings API (2026-10-20)", "https://api-web.nhle.com/v1/standings/2026-10-20")]),
    # --- EuroLeague: official standings read this session ---
    "el-535921": dict(
        status="corrected",
        evidence="EuroLeague official standings (2026-27, read 2026-10-22): Maccabi Rapyd Tel Aviv 2-4 (.333, -31) — stored correct; Real Madrid 3-3 (.500, +23, away 1-3) — stored 4-2 (.667) is wrong/stale. Away rating corrected 66.7 -> 50.0 and re-priced. OLBG's basketball hub independently lists this fixture today as event 535921 (Real Madrid, Money Line, 4/6 win tips).",
        inputs=dict(away=dict(label="EuroLeague 2026-27", value="3-3 (.500) — corrected 2026-10-22", rating=50.0)),
        sources=[("EuroLeague official standings 2026-27", "https://www.euroleaguebasketball.net/en/euroleague/standings/")]),
    "el-535923": dict(
        status="corrected",
        evidence="EuroLeague official standings: Panathinaikos AKTOR Athens 1st, 5-1 (.833, 528-438, +90, home 4-1) — stored 4-2 corrected; Kosner Baskonia Vitoria-Gasteiz 20th, 1-5 (.167, 504-564, -60, away 0-2) — stored 2-4 corrected. Ratings corrected 66.7 -> 83.3 and 33.3 -> 16.7 (rating = official win%). OLBG hub lists the game today as event 535923 (Panathinaikos, Money Line, 4/6).",
        inputs=dict(home=dict(label="EuroLeague 2026-27", value="5-1 (.833) — corrected 2026-10-22", rating=83.3),
                    away=dict(label="EuroLeague 2026-27", value="1-5 (.167) — corrected 2026-10-22", rating=16.7)),
        sources=[("EuroLeague official standings 2026-27", "https://www.euroleaguebasketball.net/en/euroleague/standings/")]),
    "el-535918": dict(
        status="corrected",
        evidence="Root desk stored no ratings for this row (unrated). EuroLeague official standings read this session: Anadolu Efes Istanbul 2-4 (.333, -18); Besiktas Istanbul 3-3 (.500, -1). Ratings added as official win% (33.3 / 50.0), the same definition the other EuroLeague rows use, so the match is now priced on measured inputs.",
        inputs=dict(home=dict(label="EuroLeague 2026-27", value="2-4 (.333) — added 2026-10-22", rating=33.3),
                    away=dict(label="EuroLeague 2026-27", value="3-3 (.500) — added 2026-10-22", rating=50.0)),
        sources=[("EuroLeague official standings 2026-27", "https://www.euroleaguebasketball.net/en/euroleague/standings/")]),
    # --- EHF Champions League: official standings read this session ---
    "hand-ehf-12048": dict(
        status="confirmed",
        evidence="EHF official standings: SC Magdeburg group 1st, 4-0-0, 141:108 (+33), 8 pts; Kolstad Håndball 4th, 0-0-4, 111:143 (-32), 0 pts. Stored records/points match. EHF lists Kolstad Håndball v SC Magdeburg on 22 Oct at 20:45 local (= 18:45Z as stored).",
        sources=[("EHF Champions League Men 2026/27 standings", "https://ehfcl.eurohandball.com/men/2026-27/standings/")]),
    "hand-ehf-12046": dict(
        status="corrected",
        evidence="EHF Group E: Barça 1st, 4-0-0, 137:104 (+33), 8 pts — stored correct. Montpellier Handball are 4th (not 3rd as stored; Dinamo Bucuresti are 3rd on 3 pts from 5 games), 1-0-3, 116:125 (-9), 2 pts — record/points/GD stored correctly, position corrected. The stored 28:27 head-to-head score was not on the page read and is not used. No hand-rating formula is published by the root desk, so ratings are retained and the corrected position is disclosed here.",
        sources=[("EHF Champions League Men 2026/27 standings", "https://ehfcl.eurohandball.com/men/2026-27/standings/")]),
    "hand-ehf-12049": dict(
        status="corrected",
        evidence="EHF Group B: Orlen Wisla Plock 1st, 3-0-1, 6 pts — stored correct; MT Melsungen 3rd but 2-0-2 with 4 pts (110:112), not the stored 1-0-3 (2 pts). Record corrected in the label; hand rating retained (no published mapping) and disclosed.",
        sources=[("EHF Champions League Men 2026/27 standings", "https://ehfcl.eurohandball.com/men/2026-27/standings/")]),
    "hand-ehf-12051": dict(
        status="confirmed",
        evidence="EHF Group D: GOG 2nd, 3-0-1, 6 pts (145:139); OTP Bank - PICK Szeged 3rd, 1-1-2, 3 pts (139:136). Stored records/points match.",
        sources=[("EHF Champions League Men 2026/27 standings", "https://ehfcl.eurohandball.com/men/2026-27/standings/")]),
    "hand-ehf-12054": dict(
        status="not-rechecked",
        evidence="EHF Group D table was read (Sporting Clube de Portugal 1st, 3-1-0, 7 pts, 149:125; IFK Kristianstad 4th, 0-0-4, 0 pts, 122:155) but the root row carries no ratings and publishes no record-to-rating mapping for handball, so no rating was invented. Row stays unrated / Low; the official table is linked for manual review.",
        sources=[("EHF Champions League Men 2026/27 standings", "https://ehfcl.eurohandball.com/men/2026-27/standings/")]),
    # --- Top 14: LNR official classement (J6) read this session ---
    "ru-top14-609567": dict(
        status="confirmed",
        evidence="LNR official Top 14 classement after J6: Stade Toulousain 1st, 24 pts (5-0-1, 197-124, +73; five straight wins J2-J6 on the form strip); USA Perpignan 9th, 13 pts (3-0-3, 166-199, -33). Next match listed as Toulouse v USA Perpignan (USAP), 24 October, Toulouse at home. Stored positions/points match (the 45-34 Bayonne score in the stored label was not on the page read and is not used).",
        sources=[("LNR Top 14 official classement (J6)", "https://top14.lnr.fr/classement")]),
    "ru-top14-609564": dict(
        status="confirmed",
        evidence="LNR classement J6: Aviron Bayonnais 5th, 17 pts (4-0-2, 190-214); LOU Rugby 8th, 14 pts (3-0-3, 193-202; form strip shows defeats in J4, J5 and J6). Next match listed as Bayonne v LOU, 24 October, Bayonne at home. Stored positions/points match (stored 16-28 score not re-read, not used).",
        sources=[("LNR Top 14 official classement (J6)", "https://top14.lnr.fr/classement")]),
    "ru-top14-609554": dict(
        status="confirmed",
        evidence="LNR classement J6: Union Bordeaux-Bègles 3rd, 19 pts (4-0-2, +64); Stade Rochelais 4th, 18 pts (4-0-2, +9). Next match listed as La Rochelle v Bordeaux, 25 October. Stored positions/points match (stored Lyon score not re-read, not used).",
        sources=[("LNR Top 14 official classement (J6)", "https://top14.lnr.fr/classement")]),
    # --- Cricket: ICC rankings + NZC fixtures read this session ---
    "cric-nz-ind-t20-2": dict(
        status="confirmed",
        evidence="ICC official men's T20I team rankings: India No. 2 (267), New Zealand No. 4 (247) — stored ratings points match exactly (the stored 'T20WC winners' note was not on the page read and is not used). NZC official fixtures list BLACKCAPS v India, 2nd T20I, Sat 24 Oct, Hagley Oval, Christchurch.",
        sources=[("ICC official rankings", "https://www.icc-cricket.com/rankings"),
                 ("NZC official fixtures (scoring.nzc.nz)", "https://scoring.nzc.nz/fixtures")]),
    "cric-ausw-nzw-t20-3": dict(
        status="corrected",
        evidence="NZC official fixtures list Australia Women v WHITE FERNS, 3rd T20I, Thu 22 Oct, North Sydney Oval, Sydney — fixture and venue confirmed. ICC women's T20I team rankings now read Australia No. 1 (292) and New Zealand No. 4 (248); stored points (287 / 253) corrected in the labels. The root 0-100 model ratings are retained because no points-to-rating formula is published; disclosed here.",
        inputs=dict(home=dict(label="ICC Women's T20I rating", value="No. 1 (292 rating) — points corrected 2026-10-22", rating=88.0),
                    away=dict(label="ICC Women's T20I rating", value="No. 4 (248 rating) — points corrected 2026-10-22", rating=69.0)),
        sources=[("ICC official rankings", "https://www.icc-cricket.com/rankings"),
                 ("NZC official fixtures (scoring.nzc.nz)", "https://scoring.nzc.nz/fixtures")]),
}

# IRL world rankings read live this session (https://www.intrl.sport/world-rankings).
# For re-verified rugby-league rows the model rating IS the official IRL ranking
# percentage — a published numeric input, replacing the root hand mapping.
IRL_MEN = {"Australia": (1, 100), "New Zealand": (2, 82), "England": (3, 70), "Samoa": (4, 56),
           "Tonga": (5, 54), "Papua New Guinea": (6, 47), "Fiji": (7, 34), "Cook Islands": (8, 24),
           "France": (11, 21), "Lebanon": (23, 7)}
IRL_WOMEN = {"Australia Jillaroos": (1, 100), "Australia": (1, 100), "New Zealand": (2, 64),
             "England Women": (3, 40), "England": (3, 40), "France": (4, 25), "Samoa Women": (5, 22),
             "Samoa": (5, 22), "Papua New Guinea": (6, 19), "Wales Women": (9, 17), "Wales": (9, 17), "Fiji": (12, 13)}
NRL_MEN_URL = "https://www.nrl.com/draw/rugby-league-world-cup/2026/round-2/"
NRL_WOMEN_URL = "https://www.nrl.com/draw/womens-rugby-league-world-cup/2026/round-2/"
IRL_URL = "https://www.intrl.sport/world-rankings"
RL_FIXTURE_EVIDENCE = {
    "rl-wc26-tga-lbn": "NRL official RLWC26 Round 2 draw lists Tonga vs Lebanon, Friday 23 October, CommBank Stadium, Sydney.",
    "rl-wc26-png-sam": "NRL draw lists Papua New Guinea vs Samoa, Saturday 24 October, Santos National Football Stadium, Port Moresby.",
    "rl-wc26-eng-fra": "NRL draw lists England vs France, Saturday 24 October, HBF Park, Perth.",
    "rl-wc26-nzl-cok": "NRL draw lists New Zealand vs Cook Islands, Sunday 25 October, One NZ Stadium, Christchurch.",
    "rl-wc26-aus-fij": "NRL draw lists Australia vs Fiji, Sunday 25 October, Suncorp Stadium, Brisbane.",
    "rl-wc26w-sam-wal": "NRL women's RLWC26 Round 2 draw lists Samoa vs Wales, Friday 23 October, CommBank Stadium, Sydney.",
    "rl-wc26w-aus-eng": "NRL women's draw lists Australia vs England, Saturday 24 October, HBF Park, Perth.",
}

BLOCKERS = {
    "darts": "PDC official draw page returned only its cookie-consent wall in every fetched chunk (7/7) on 2026-10-22; seeds and pairings could not be re-read. Rows retain their recorded PDC source link, are marked not-rechecked, and are capped below High.",
    "aussie-rules": "The official AFLW ladder (afl.com.au/aflw/ladder) is client-rendered: both fetched chunks returned the page shell with no ladder rows on 2026-10-22, so neither positions nor points could be re-read (pre-existing root finding F-T34-01 also questions the stored ladder). Rows are not-rechecked and capped below High.",
}
DEFAULT_BLOCKER = "Not re-fetched in this session: the row's recorded governing-body source from the primary desk is retained and linked, the stored values are published unchanged as a dated snapshot, and the row is capped below High. This session re-read official pages only for the rows listed as confirmed/corrected in verification.json."


def rating_of(side):
    if not side:
        return None, False
    return side.get("rating"), (side.get("rating") is not None and not side.get("bounded", False))


def outcome(selection, p):
    fair = M.to_fair_odds(p)
    book = M.to_odds(p)
    return dict(selection=selection, probability=round(p, 6), fair_odds=fair,
                fair_american=M.to_american(fair), book5_odds=book,
                book5_american=M.to_american(book), implied_pct=M.implied(p))


def in_window_fair(fair_odds):
    return 1.40 <= fair_odds <= 101.0


def price(m):
    cfg = M.SPORTS[m["sport"]]
    r_home, meas_home = rating_of(m.get("inputs", {}).get("home"))
    r_away, meas_away = rating_of(m.get("inputs", {}).get("away"))
    both_rated = r_home is not None and r_away is not None
    both_meas = bool(meas_home and meas_away)
    p_venue = 0.500 if m.get("neutral", False) else cfg["p_base"]
    logit = M._logit(p_venue) + ((r_home - r_away) / cfg["scale"] if both_rated else 0.0)
    p2_home = min(max(M._sigmoid(logit), 0.025), 0.975)
    if cfg["draws"]:
        d = max(0.018, round(cfg["draw_p"] * math.exp(-(((p2_home - 0.5) / 0.34) ** 2)), 6))
        probs = M._normalize_probs([p2_home * (1 - d), d, (1 - p2_home) * (1 - d)])
        p_home, p_draw, p_away = probs
    else:
        p_home, p_away = M._normalize_probs([p2_home, 1 - p2_home])
        p_draw = 0.0
    margin = cfg["sigma"] * M._norm_ppf(p2_home)
    fav_home = p2_home >= 0.5
    favourite = m["home"] if fav_home else m["away"]
    p_best2 = max(p2_home, 1 - p2_home)

    markets = []
    win_out = [outcome(m["home"], p_home)] + ([outcome("Draw", p_draw)] if cfg["draws"] else []) + [outcome(m["away"], p_away)]
    markets.append(dict(key="winner", name="Match Winner (3-Way)" if cfg["draws"] else "Match Winner",
                        line="", outcomes=win_out,
                        basis="Official governing-body ratings + venue adjustment" if both_rated else "Neutral venue baseline (no measured rating pair)"))
    if cfg["draws"]:
        dnb = M._normalize_probs([p2_home, 1 - p2_home])
        markets.append(dict(key="dnb", name="Draw No Bet (2-Way)", line="PK",
                            outcomes=[outcome(f"{m['home']} (DNB)", dnb[0]), outcome(f"{m['away']} (DNB)", dnb[1])],
                            basis="Two-way conditional probabilities excluding the draw"))

    handicap = []
    if m["sport"] not in ("motor-racing", "golf", "greyhounds"):
        seen = set()
        for key, target, role in (("handicap_50", 0.50, "main line (50% cover)"),
                                  ("handicap_60", 0.60, "alternate (60% cover)"),
                                  ("handicap_70", 0.70, "alternate (70% cover)"),
                                  ("handicap_80", 0.80, "alternate (80% cover)")):
            # favourite line (points added to favourite's margin) for exact target cover, snapped to x.5
            fav_line_exact = -(abs(margin) - cfg["sigma"] * M._norm_ppf(target))
            fav_line = math.ceil(fav_line_exact - 0.5) + 0.5  # smallest x.5 line at/above exact (half lines only, no pushes)
            if fav_line in seen:
                continue
            seen.add(fav_line)
            h_home = fav_line if fav_home else -fav_line
            p_home_cover = min(max(1 - M._norm_cdf((-h_home - margin) / cfg["sigma"]), 0.02), 0.98)
            handicap.append(dict(key=key, name=cfg["handicap_name"], line=f"{abs(h_home):.1f}", role=role,
                                 outcomes=[outcome(f"{m['home']} {h_home:+.1f}", p_home_cover),
                                           outcome(f"{m['away']} {-h_home:+.1f}", 1 - p_home_cover)],
                                 basis=f"Gaussian margin projection (E[M]={margin:+.1f}, sigma={cfg['sigma']:.1f}); rung targets {target:.0%} favourite cover, half-point line, exact probability recomputed"))
        markets.extend(handicap)

    comp_override = M.COMPETITION_TOTALS.get(m.get("competition", ""))
    tot_base = comp_override[0] if comp_override is not None else cfg["total"]
    tot_sigma = comp_override[1] if comp_override is not None else cfg["tsigma"]
    unavailable = []
    if tot_base is not None and tot_sigma is not None:
        if m["sport"] in ("tennis", "snooker", "darts", "volleyball"):
            p_over_raw = 0.44 + 0.14 * (1.0 - 2.0 * abs(p2_home - 0.5))
        else:
            p_over_raw = 0.500
        step = max(1.5, round((tot_sigma / 4.0) * 2.0) / 2.0)
        z_base = M._norm_ppf(1.0 - p_over_raw)
        seen = set()
        for key, off in (("total_m2", -2 * step), ("total_m1", -step), ("total", 0.0), ("total_p1", step), ("total_p2", 2 * step)):
            line_total = round(tot_base + off, 1)
            if line_total in seen or line_total <= 0:
                continue
            seen.add(line_total)
            p_over = min(max(1 - M._norm_cdf(z_base + (line_total - tot_base) / tot_sigma), 0.02), 0.98)
            markets.append(dict(key=key, name=f"Match Total ({cfg['total_name']})", line=f"{line_total:.1f}",
                                role="baseline total" if off == 0 else f"alternate total ({off:+.1f})",
                                outcomes=[outcome(f"Over {line_total:.1f}", p_over), outcome(f"Under {line_total:.1f}", 1 - p_over)],
                                basis=f"Assumed competition baseline total {tot_base:.1f} (sigma={tot_sigma:.1f}) from the published root-model constants — a modelling assumption, not a sourced team statistic; totals are therefore never High selections on this desk"))
    else:
        unavailable.append(dict(key="total", name="Match Total", status="unverified",
                                reason="No official, competition-specific total baseline is recorded for this format; left blank rather than inferred."))
    # Investigated, not priced (no official input recorded) — named, not silently omitted.
    unavailable += [
        dict(key="correct_score", name="Correct Score / Exact Margin", status="investigated-not-priced",
             reason="Would require a sourced score-distribution input per team; only an aggregate margin sigma (modelling assumption) is recorded."),
        dict(key="player_props", name="Player Props", status="investigated-not-priced",
             reason="No official player-level form/lineup input is recorded for this fixture on the primary desk."),
        dict(key="period_markets", name="Period / Half / Set / Leg Sub-markets", status="investigated-not-priced",
             reason="No official segment-level scoring input is recorded; the full-match margin model does not identify segment prices."),
    ]

    return dict(p_home=p_home, p_draw=p_draw, p_away=p_away, p_best2=p_best2, margin=margin,
                favourite=favourite, fav_home=fav_home, both_rated=both_rated, both_meas=both_meas,
                rating_home=r_home, rating_away=r_away, markets=markets, unavailable=unavailable)


def strict_selection(m, priced):
    """Tightest favourite-side winner/handicap selection with p>=0.70 at fair odds in window."""
    best = None
    for mk in priced["markets"]:
        if mk["key"] == "winner":
            pool = [o for o in mk["outcomes"] if o["selection"] == priced["favourite"]]
        elif mk["key"].startswith("handicap"):
            if m["sport"] == "cricket":
                continue  # winner-only High rule for cricket (see module docstring)
            pool = [o for o in mk["outcomes"] if o["selection"].startswith(priced["favourite"] + " ")]
        else:
            continue
        for o in pool:
            # Exact-probability ceiling as well as rounded odds: p <= 1/1.40, so a
            # 71.5% line cannot sneak into the -250 window via 2dp rounding.
            if 0.70 <= o["probability"] <= (1.0 / 1.40 + 1e-9) and in_window_fair(o["fair_odds"]):
                if best is None or o["fair_odds"] > best[1]["fair_odds"]:
                    best = (mk, o)
    return best


def main():
    fixtures = json.loads((ROOT / "data" / "fixtures.json").read_text())["matches"]
    try:
        from s8fc47dcb_prose import PROSE
    except Exception:
        PROSE = {}

    future, expired, undated = [], [], []
    for m in fixtures:
        s = m.get("start_utc") or ""
        (expired if s and s < CUTOFF else undated if not s else future).append(m)

    verification, dataset, predictions = [], [], []
    for orig in sorted(future, key=lambda x: x["start_utc"]):
        m = json.loads(json.dumps(orig))  # deep copy; primary file never edited
        ov = OVERLAY.get(m["id"])
        v_status, v_evidence = "not-rechecked", BLOCKERS.get(m["sport"], DEFAULT_BLOCKER)
        v_sources = []
        if m["sport"] == "rugby-league" and m["id"] in RL_FIXTURE_EVIDENCE:
            women = "Women" in m["competition"]
            table = IRL_WOMEN if women else IRL_MEN
            corr = []
            for side in ("home", "away"):
                team = m[side]
                rank, pct = table[team]
                old = m["inputs"][side]
                corr.append(f"{team}: stored '{old['value']}' (hand rating {old['rating']}) -> IRL live No. {rank} ({pct}%), rating := {pct}")
                m["inputs"][side] = dict(label="IRL World Ranking (live 2026-10-22)",
                                         value=f"No. {rank} ({pct}% ranking points)", rating=float(pct))
            v_status = "corrected"
            v_evidence = (RL_FIXTURE_EVIDENCE[m["id"]] + " IRL official world rankings read live this session; "
                          "stored ranks/ratings superseded: " + "; ".join(corr) +
                          ". Stored R1 scorelines in the old labels were not on the pages read and are not used.")
            v_sources = [("IRL official world rankings", IRL_URL),
                         ("NRL official RLWC26 draw (Round 2)", NRL_WOMEN_URL if women else NRL_MEN_URL)]
        elif ov:
            v_status, v_evidence = ov["status"], ov["evidence"]
            v_sources = list(ov.get("sources", []))
            for side, new_inputs in ov.get("inputs", {}).items():
                m.setdefault("inputs", {})[side] = new_inputs
        verification.append(dict(match_id=m["id"], sport=m["sport"], match=f"{m['home']} v {m['away']}",
                                 start_utc=m["start_utc"], status=v_status, evidence=v_evidence,
                                 recheck_sources=[dict(name=n, url=u) for n, u in v_sources],
                                 recorded_sources=m["sources"], checked_at=CHECKED_AT))

        if not m.get("away"):
            dataset.append(dict(fixture=m, priced=False, note="Event/field card — no two-sided market originated."))
            continue
        priced = price(m)
        cfg = M.SPORTS[m["sport"]]
        sel = strict_selection(m, priced)
        gates = dict(status_verified=m["status"] == "verified", both_measured=priced["both_meas"],
                     separation=priced["p_best2"] >= 0.60, strict_line=sel is not None,
                     reverified=v_status in ("confirmed", "corrected"))
        if all(gates.values()):
            confidence = "high"
        elif priced["both_meas"] and m["status"] == "verified" and priced["p_best2"] >= cfg["med"]:
            confidence = "medium"
        else:
            confidence = "low"
        reasons = []
        if confidence != "high":
            if not gates["status_verified"]:
                reasons.append(f"fixture status is '{m['status']}', not 'verified'")
            if not gates["both_measured"]:
                reasons.append("no measured official rating pair (neutral baseline; capped at Low)")
            if not gates["separation"]:
                reasons.append(f"two-way win probability {priced['p_best2']:.1%} below the 60% separation gate")
            if not gates["strict_line"]:
                reasons.append("no favourite winner/handicap line lands at >=70% with fair odds inside 1.40-101.00")
            if not gates["reverified"]:
                reasons.append("not re-read against an official page this session (blocker in verification register)")
        winner_call = priced["favourite"]
        row = dict(fixture=m, priced=True, confidence=confidence, verification_status=v_status,
                   winner_call=winner_call,
                   home_probability=round(priced["p_home"], 4), draw_probability=round(priced["p_draw"], 4),
                   away_probability=round(priced["p_away"], 4), expected_margin=round(priced["margin"], 2),
                   rating_home=priced["rating_home"], rating_away=priced["rating_away"],
                   both_measured=priced["both_meas"], both_rated=priced["both_rated"],
                   gates=gates, tier_reasons=reasons, markets=priced["markets"],
                   unavailable_markets=priced["unavailable"],
                   strict_selection=(dict(market=sel[0]["name"], key=sel[0]["key"], line=sel[0].get("line", ""),
                                          selection=sel[1]["selection"], probability=sel[1]["probability"],
                                          fair_odds=sel[1]["fair_odds"], fair_american=sel[1]["fair_american"],
                                          book5_odds=sel[1]["book5_odds"], book5_american=sel[1]["book5_american"])
                                     if sel else None))
        dataset.append(row)
        if confidence == "high":
            text = PROSE.get(m["id"], "")
            predictions.append(dict(match_id=m["id"], sport=m["sport"], competition=m["competition"],
                                    start_utc=m["start_utc"], match=f"{m['home']} v {m['away']}",
                                    selection=sel[1]["selection"], market=sel[0]["name"], line=sel[0].get("line", ""),
                                    probability=sel[1]["probability"], fair_odds=sel[1]["fair_odds"],
                                    fair_american=sel[1]["fair_american"], winner_call=winner_call,
                                    text=text, words=len(text.split()), sources=m["sources"],
                                    recheck_sources=[dict(name=n, url=u) for n, u in v_sources]))

    flagged = []
    for v in verification:
        if v["status"] == "corrected":
            flagged.append(dict(kind="corrected-on-recheck", match_id=v["match_id"], match=v["match"],
                                detail=v["evidence"], sources=v["recheck_sources"]))
        elif v["status"] == "not-rechecked":
            flagged.append(dict(kind="not-rechecked", match_id=v["match_id"], match=v["match"],
                                detail=v["evidence"], sources=v["recorded_sources"]))
    for m in expired:
        flagged.append(dict(kind="expired-at-cutoff", match_id=m["id"],
                            match=f"{m['home']} v {m['away']}",
                            detail=f"Stored start {m.get('start_utc') or 'blank'} is before the explicit cutoff {CUTOFF}; excluded from the future desk by timestamp arithmetic only — no result is asserted.",
                            sources=m["sources"]))
    for m in undated:
        flagged.append(dict(kind="undated", match_id=m["id"], match=f"{m['home']} v {m['away']}",
                            detail="No start time is recorded on the primary desk (left blank there because no official page stated one); a fixture without a confirmed start cannot be listed as upcoming, so it is excluded from pricing and published here instead.",
                            sources=m["sources"]))
    flagged.insert(0, dict(kind="systemic", match_id="olbg-clock-display",
                           match="OLBG hub clock vs official UTC",
                           detail="OLBG's basketball hub read on 2026-10-22 shows Maccabi Tel Aviv vs Real Madrid at 'Today 14:05' and Panathinaikos vs Baskonia at 'Today 14:15' with no timezone label; the stored official tip-offs are 18:05Z and 18:15Z (EDT display, UTC-4). Readers should not treat OLBG card times as UTC.",
                           sources=[dict(name="OLBG basketball hub (live, read 2026-10-22)", url="https://www.olbg.com/betting-tips/Basketball/4"),
                                    dict(name="EuroLeague official game center", url="https://www.euroleaguebasketball.net/euroleague/game-center/")]))
    flagged.insert(1, dict(kind="systemic", match_id="root-high-prose-arithmetic",
                           match="Root-desk expired High prose: Buffalo Sabres v Philadelphia Flyers (21 Oct, expired here)",
                           detail="The root prediction text says 'A fourteen-goal swing in goal differential' while its own stored inputs are Buffalo -7 and Philadelphia -19, a 12-goal swing (also noted by sessions T56/PR #76). The fixture is expired at this desk's cutoff so no live pick is affected; the root text itself is not edited from this namespace — flagged for the root desk owner.",
                           sources=[dict(name="NHL official standings API (2026-10-20)", url="https://api-web.nhle.com/v1/standings/2026-10-20"),
                                    dict(name="NHL.com Gamecenter #2026020152", url="https://www.nhl.com/gamecenter/2026020152")]))

    taxonomy = json.loads((ROOT / "data" / "olbg_taxonomy.json").read_text())
    olbg = dict(
        taxonomy_source="https://www.olbg.com/sitemap-betting-tips.xml",
        reread="2026-10-22 (this session): sitemap entries dated 2026-10-22 still list the 17 in-scope hubs with the same sport IDs as the committed taxonomy (Tennis/3, Basketball/4, Golf/5, Cricket/7, Snooker/8, Rugby Union/9, Rugby League/10, Baseball/12, Ice Hockey/13, Motor Racing/14, Darts/15, Handball/20, Volleyball/21, Aussie Rules/22, eSports/23, Gaelic Football/25, Greyhounds/28); excluded hubs remain Football/1, Horse Racing/2, American Football/11, Boxing/16, Cycling/17 plus unlisted Specials/18 and Hurling/26 recorded previously.",
        live_hub_evidence=[
            dict(hub="Basketball (sport 4)", url="https://www.olbg.com/betting-tips/Basketball/4", read="2026-10-22",
                 observation="Live cards read this session include Maccabi Tel Aviv vs Real Madrid (event_id=535921, selection Real Madrid, market 'Money Line', 4/6 win tips 67%, shown 'Today 14:05') and Panathinaikos vs Baskonia (event_id=535923, Panathinaikos, Money Line, 4/6 67%, 'Today 14:15'); sub-routes linked from the hub include NBA, WNBA and European/Euroleague. Hub times carry no timezone label (EDT vs the 18:05Z/18:15Z official tip-offs)."),
        ],
        excluded_note="Excluded per brief: soccer/football, boxing, UFC/MMA, american football, hurling, horse racing, cycling, specials.",
        sports=taxonomy["sports"])

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "dataset.json").write_text(json.dumps(dict(
        desk="8fc47dcb", generated="2026-10-22", cutoff_utc=CUTOFF,
        model="s8fc47dcb fair-price extension of root olbg-independent-logit-normal-v2.0 constants",
        pricing="Fair (0% overround) headline odds; 5%-vig bookmaker price printed alongside. High window judged on the fair price (see Methodology arithmetic).",
        counts=dict(future=len(future), priced=sum(1 for r in dataset if r["priced"]),
                    expired=len(expired), undated=len(undated),
                    high=sum(1 for r in dataset if r.get("confidence") == "high"),
                    medium=sum(1 for r in dataset if r.get("confidence") == "medium"),
                    low=sum(1 for r in dataset if r.get("confidence") == "low")),
        rows=dataset), indent=1))
    (OUT / "predictions.json").write_text(json.dumps(dict(
        rule="Unique >=30-word human prediction per strict High pick, built only from facts read on official pages this session; selection stated verbatim.",
        count=len(predictions), items=predictions), indent=1))
    (OUT / "verification.json").write_text(json.dumps(dict(
        method="Each future row was compared with official governing-body pages fetched and read on 2026-10-22 in this session; statuses mean confirmed (all priced facts match), corrected (official page supersedes stored value; price rebuilt), not-rechecked (blocker named; stored snapshot retained, capped below High).",
        checked_at=CHECKED_AT, rows=verification), indent=1))
    (OUT / "flagged.json").write_text(json.dumps(dict(cutoff_utc=CUTOFF, items=flagged), indent=1))
    (OUT / "olbg.json").write_text(json.dumps(olbg, indent=1))

    his = [r for r in dataset if r.get("confidence") == "high"]
    print(f"future={len(future)} priced={sum(1 for r in dataset if r['priced'])} "
          f"high={len(his)} medium={sum(1 for r in dataset if r.get('confidence')=='medium')} "
          f"low={sum(1 for r in dataset if r.get('confidence')=='low')} expired={len(expired)} undated={len(undated)}")
    for r in his:
        s = r["strict_selection"]
        print(f"  HIGH {r['fixture']['start_utc']} {r['fixture']['id']:22s} {s['selection']} [{s['market']} {s['line']}] "
              f"p={s['probability']:.3f} fair={s['fair_odds']} ({s['fair_american']}) book5={s['book5_odds']} win={r['winner_call']} prose={'YES' if PROSE.get(r['fixture']['id']) else 'MISSING'}")
    print("near-miss strict lines blocked only by verification/gates:")
    for r in dataset:
        if r["priced"] and r.get("strict_selection") and r["confidence"] != "high":
            print(f"  {r['fixture']['id']:22s} {r['strict_selection']['selection']} p={r['strict_selection']['probability']:.3f} -> {r['confidence']}: {'; '.join(r['tier_reasons'])}")


if __name__ == "__main__":
    main()
