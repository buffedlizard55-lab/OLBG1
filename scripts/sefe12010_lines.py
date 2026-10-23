#!/usr/bin/env python3
"""Session efe12010 — turns officially sourced inputs into fixtures + originated lines."""
from __future__ import annotations

import hashlib
import math
import re

import sefe12010_data as D
from sefe12010_engine import (
    BAND_MAX_AMERICAN, BAND_MIN_AMERICAN, MARGIN_OUTRIGHT, MARGIN_THREE_WAY,
    MARGIN_TWO_WAY, best_band_outcome, confidence_for, first_to, harville_top_n,
    headline_selection, log5, market, norm_cdf, poisson_over, set_prob_from_match,
    skellam_cover, tier_for, winner_favourite,
)

SHRINK_GAMES = 6.0          # NHL record shrinkage prior (games)
NHL_HOME_EDGE = 0.030       # added to the home side's win probability
MLB_HOME_EDGE = 0.035
EL_HOME_POINTS = 2.5        # EuroLeague home-court points
EL_SIGMA = 11.0             # EuroLeague margin standard deviation
EL_TOTAL_SIGMA = 16.0
TENNIS_K = 0.70             # exponent on ATP ranking points
SNOOKER_PRIOR_FRAMES = 10.0


def _fixture(**kw) -> dict:
    base = {
        "id": "", "sport": "", "competition": "", "event": "", "start_utc": "",
        "venue": "", "status": "unverified", "sources": [], "verification": {},
        "flags": [], "official_notes": [], "olbg": None, "unpriced": True,
        "markets": [], "unavailable_markets": [], "pick": None, "band_pick": None,
        "confidence": "low", "tier": "Unrated", "inputs": [],
    }
    base.update(kw)
    return base


def _src(key: str) -> dict:
    s = D.SOURCES[key]
    return {"name": s["name"], "url": s["url"], "read_utc": s["read_utc"], "key": key}


def _finalise(fx: dict) -> dict:
    """Attach the headline pick, the in-band selection and the confidence tier."""
    if not fx["markets"]:
        fx["unpriced"] = True
        fx["confidence"] = "low"
        fx["tier"] = "Unrated"
        return fx
    fx["unpriced"] = False
    wm, wo = winner_favourite(fx["markets"])
    bm, bo = headline_selection(fx["markets"])
    rated = fx["status"] == "verified"
    if wo is not None:
        fx["pick"] = {
            "market": wm["label"], "market_key": wm["key"], "selection": wo["selection"],
            "probability": wo["probability"], "fair_odds": wo["fair_odds"],
            "fair_american": wo["fair_american"], "odds": wo["odds"],
            "american": wo["american"], "in_band": wo["in_band"],
            "tier": tier_for(wo["probability"], rated),
        }
    if bo is not None:
        fx["band_pick"] = {
            "market": bm["label"], "market_key": bm["key"], "selection": bo["selection"],
            "probability": bo["probability"], "fair_odds": bo["fair_odds"],
            "fair_american": bo["fair_american"], "odds": bo["odds"],
            "american": bo["american"],
            "tier": tier_for(bo["probability"], rated),
            "confidence": confidence_for(bo["probability"], rated),
        }
        fx["confidence"] = confidence_for(bo["probability"], rated)
        fx["tier"] = tier_for(bo["probability"], rated)
    if wo is not None and not wo["in_band"]:
        fx["flags"].append(
            f"Price cap: the straight favourite ({wo['selection']}, {wo['fair_american']}) "
            f"prices shorter than {BAND_MIN_AMERICAN}, so it is held at Medium and the "
            f"published high-confidence selection moves to an in-band derivative."
        )
    return fx


# --------------------------------------------------------------------- ice hockey
def build_ice_hockey() -> list[dict]:
    out = []
    for g in D.NHL_GAMES:
        h, a = D.NHL_TEAMS[g["home"]], D.NHL_TEAMS[g["away"]]
        hw = (h["w"] + SHRINK_GAMES / 2) / (h["gp"] + SHRINK_GAMES)
        aw = (a["w"] + SHRINK_GAMES / 2) / (a["gp"] + SHRINK_GAMES)
        p_home = min(max(log5(hw, aw) + NHL_HOME_EDGE, 0.02), 0.98)
        markets = [market(
            "winner", "Match Winner (incl. OT/SO)",
            [(h["name"], p_home), (a["name"], 1 - p_home)], MARGIN_TWO_WAY,
            "Shrunk regulation-plus-overtime win rates (prior of 6 games at .500) combined "
            "with the Bill James log5 identity, then a flat +3.0pp home-ice adjustment.",
        )]
        unavailable = []
        if h["gf"] is None or h["ga"] is None or a["gf"] is None or a["ga"] is None:
            missing = h["name"] if h["gf"] is None else a["name"]
            unavailable.append({
                "key": "total", "label": "Game Total Goals", "status": "unverified",
                "reason": (f"Goals for / goals against for {missing} were not returned in the "
                           f"chunk of the official team-summary report that was read, so no "
                           f"scoring rate can be stated without inventing one."),
            })
            unavailable.append({
                "key": "puckline", "label": "Puck Line -1.5 / +1.5", "status": "unverified",
                "reason": f"Depends on the same missing {missing} scoring rates.",
            })
            flags = [f"Blank total and puck line: {missing} goals for/against unavailable from the official read."]
        else:
            mu_h = (h["gf"] / h["gp"] + a["ga"] / a["gp"]) / 2.0
            mu_a = (a["gf"] / a["gp"] + h["ga"] / h["gp"]) / 2.0
            lam = mu_h + mu_a
            line = math.floor(lam) + 0.5
            p_over = poisson_over(line, lam)
            markets.append(market(
                "total", f"Game Total {line:.1f} Goals",
                [(f"Over {line:.1f} goals", p_over), (f"Under {line:.1f} goals", 1 - p_over)],
                MARGIN_TWO_WAY,
                f"Independent Poisson goal counts, lambda_home={mu_h:.2f} and "
                f"lambda_away={mu_a:.2f} from the two sides' official goals for and against.",
            ))
            p_h15 = skellam_cover(mu_h, mu_a, 1.5)
            markets.append(market(
                "puckline", "Puck Line -1.5 / +1.5",
                [(f"{h['name']} -1.5", p_h15), (f"{a['name']} +1.5", 1 - p_h15)],
                MARGIN_TWO_WAY,
                "Skellam difference of the same two Poisson counts.",
            ))
            p_h25 = poisson_over(2.5, mu_h)
            markets.append(market(
                "team_total_home", f"{h['name']} Team Total 2.5",
                [(f"{h['name']} Over 2.5", p_h25), (f"{h['name']} Under 2.5", 1 - p_h25)],
                MARGIN_TWO_WAY, "Home-side Poisson count only.",
            ))
            p_a25 = poisson_over(2.5, mu_a)
            markets.append(market(
                "team_total_away", f"{a['name']} Team Total 2.5",
                [(f"{a['name']} Over 2.5", p_a25), (f"{a['name']} Under 2.5", 1 - p_a25)],
                MARGIN_TWO_WAY, "Away-side Poisson count only.",
            ))
            alt = line + 1.0
            p_alt = poisson_over(alt, lam)
            markets.append(market(
                "total_alt", f"Alternate Game Total {alt:.1f} Goals",
                [(f"Over {alt:.1f} goals", p_alt), (f"Under {alt:.1f} goals", 1 - p_alt)],
                MARGIN_TWO_WAY, "Same Poisson total, one goal higher on the ladder."))
            p_btts = poisson_over(1.5, mu_h) * poisson_over(1.5, mu_a)
            markets.append(market(
                "btts2", "Both Teams To Score 2+ Goals",
                [("Both teams 2+ goals — Yes", p_btts),
                 ("Both teams 2+ goals — No", 1 - p_btts)], MARGIN_TWO_WAY,
                "Product of the two independent Poisson counts clearing 1.5 goals."))
            flags = []
        olbg = next((r for r in D.OLBG_HARVEST
                     if r["sport"] == "ice-hockey" and a["name"].split()[-1] in r["event"]
                     and h["name"].split()[-1] in r["event"]), None)
        fx = _fixture(
            id=f"EFE-NHL-{g['id']}", sport="ice-hockey", competition="NHL Regular Season 2026-27",
            event=f"{a['name']} @ {h['name']}", start_utc=g["utc"], venue=g["venue"],
            status="verified",
            sources=[_src("nhl_sched_24" if g["utc"] > "2026-10-24T12" else "nhl_sched_23"), _src("nhl_team")],
            verification={
                "verdict": "confirmed", "checked_utc": D.SOURCES["nhl_team"]["read_utc"],
                "evidence": D.SOURCES["nhl_team"]["url"],
                "fields": ["start_utc", "venue", "home record", "away record", "goals for", "goals against"],
            },
            flags=flags, markets=markets, unavailable_markets=unavailable,
            olbg=olbg,
            inputs=[
                f"{h['name']}: {h['w']}-{h['l']}-{h['otl']}, {h['pts']} pts in {h['gp']} GP, "
                f"GF {h['gf'] if h['gf'] is not None else '—'} / GA {h['ga'] if h['ga'] is not None else '—'}, "
                f"PP {h['pp']*100:.1f}%, PK {h['pk']*100:.1f}%" if h["pk"] else
                f"{h['name']}: {h['w']}-{h['l']}-{h['otl']}, {h['pts']} pts in {h['gp']} GP, PP {h['pp']*100:.1f}%",
                f"{a['name']}: {a['w']}-{a['l']}-{a['otl']}, {a['pts']} pts in {a['gp']} GP, "
                f"GF {a['gf'] if a['gf'] is not None else '—'} / GA {a['ga'] if a['ga'] is not None else '—'}, "
                f"PP {a['pp']*100:.1f}%, PK {a['pk']*100:.1f}%" if a["pk"] else
                f"{a['name']}: {a['w']}-{a['l']}-{a['otl']}, {a['pts']} pts in {a['gp']} GP, PP {a['pp']*100:.1f}%",
            ],
        )
        out.append(_finalise(fx))
    return out


# ----------------------------------------------------------------------- baseball
def build_baseball() -> list[dict]:
    def pyth(rs: int, ra: int) -> float:
        return rs ** 1.83 / (rs ** 1.83 + ra ** 1.83)

    out = []
    for g in D.MLB_GAMES:
        h, a = D.MLB_TEAMS[g["home"]], D.MLB_TEAMS[g["away"]]
        hr = 0.5 * h["pct"] + 0.5 * pyth(h["rs"], h["ra"])
        ar = 0.5 * a["pct"] + 0.5 * pyth(a["rs"], a["ra"])
        p_home = min(max(log5(hr, ar) + MLB_HOME_EDGE, 0.02), 0.98)
        mu_h = (h["rs"] / 162.0 + a["ra"] / 162.0) / 2.0
        mu_a = (a["rs"] / 162.0 + h["ra"] / 162.0) / 2.0
        lam = mu_h + mu_a
        line = math.floor(lam) + 0.5
        markets = [
            market("winner", "Money Line",
                   [(h["name"], p_home), (a["name"], 1 - p_home)], MARGIN_TWO_WAY,
                   "50/50 blend of actual win percentage and Pythagorean expectation "
                   "(exponent 1.83) from the official final 2026 standings, combined through "
                   "log5 with a +3.5pp home adjustment."),
            market("runline", "Run Line -1.5 / +1.5",
                   [(f"{h['name']} -1.5", skellam_cover(mu_h, mu_a, 1.5)),
                    (f"{a['name']} +1.5", 1 - skellam_cover(mu_h, mu_a, 1.5))],
                   MARGIN_TWO_WAY, "Skellam difference of two Poisson run counts."),
            market("total", f"Game Total {line:.1f} Runs",
                   [(f"Over {line:.1f} runs", poisson_over(line, lam)),
                    (f"Under {line:.1f} runs", 1 - poisson_over(line, lam))],
                   MARGIN_TWO_WAY,
                   f"Poisson total with lambda={lam:.2f} from season runs scored and allowed."),
        ]
        fx = _fixture(
            id=f"EFE-MLB-{g['id']}", sport="baseball", competition="MLB World Series 2026",
            event=f"{a['name']} @ {h['name']} — {g['label']}", start_utc=g["utc"],
            venue=g["venue"], status="verified",
            sources=[_src("mlb_sched"), _src("mlb_standings")],
            verification={
                "verdict": "confirmed", "checked_utc": D.SOURCES["mlb_standings"]["read_utc"],
                "evidence": D.SOURCES["mlb_standings"]["url"],
                "fields": ["gamePk", "start_utc", "venue", "home record", "away record",
                           "runs scored", "runs allowed"],
            },
            flags=[
                "Scoring inputs are full-season team rates. Neither probable starting pitcher "
                "nor any postseason bullpen usage was published in the endpoints read, so the "
                "run line and total are capped at Medium and carry wider uncertainty than the "
                "money line."
            ],
            markets=markets,
            unavailable_markets=[{
                "key": "first_five", "label": "First Five Innings", "status": "unverified",
                "reason": "Requires probable starters, which the schedule endpoint did not return.",
            }],
            olbg=next((r for r in D.OLBG_HARVEST if r["sport"] == "baseball"), None),
            inputs=[
                f"{h['name']}: {h['w']}-{h['l']} ({h['pct']:.3f}), RS {h['rs']} / RA {h['ra']}, "
                f"home {h['home']}, last ten {h['l10']}, Pythagorean {h['pyth']}",
                f"{a['name']}: {a['w']}-{a['l']} ({a['pct']:.3f}), RS {a['rs']} / RA {a['ra']}, "
                f"away {a['away']}, last ten {a['l10']}, Pythagorean {a['pyth']}",
            ],
        )
        out.append(_finalise(fx))
    return out


# --------------------------------------------------------------------- basketball
def build_basketball() -> list[dict]:
    out = []
    for g in D.EL_GAMES:
        h, a = D.EL_TEAMS[g["home"]], D.EL_TEAMS[g["away"]]
        hr = (h["pf"] - h["pa"]) / h["gp"]
        ar = (a["pf"] - a["pa"]) / a["gp"]
        margin = hr - ar + EL_HOME_POINTS
        p_home = min(max(norm_cdf(margin / EL_SIGMA), 0.02), 0.98)
        spread = round(margin * 2) / 2.0
        if abs(spread - margin) < 1e-9:
            spread += 0.5
        p_cover = norm_cdf((margin - spread) / EL_SIGMA)
        hp = (h["pf"] / h["gp"] + a["pa"] / a["gp"]) / 2.0
        ap = (a["pf"] / a["gp"] + h["pa"] / h["gp"]) / 2.0
        tot = hp + ap
        tline = round(tot * 2) / 2.0
        if abs(tline - tot) < 1e-9:
            tline += 0.5
        p_over = 1 - norm_cdf((tline - tot) / EL_TOTAL_SIGMA)
        sign = f"-{spread:.1f}" if spread > 0 else f"+{abs(spread):.1f}"
        osign = f"+{spread:.1f}" if spread > 0 else f"-{abs(spread):.1f}"
        markets = [
            market("winner", "Match Winner",
                   [(h["name"], p_home), (a["name"], 1 - p_home)], MARGIN_TWO_WAY,
                   f"Season point differential per game ({hr:+.2f} v {ar:+.2f}) plus "
                   f"{EL_HOME_POINTS:.1f} points of home court, normal margin with "
                   f"sigma {EL_SIGMA:.1f}."),
            market("handicap", f"Handicap {h['name']} {sign}",
                   [(f"{h['name']} {sign}", p_cover), (f"{a['name']} {osign}", 1 - p_cover)],
                   MARGIN_TWO_WAY, f"Expected margin {margin:+.2f} points against a {spread:.1f} line."),
            market("total", f"Match Total {tline:.1f} Points",
                   [(f"Over {tline:.1f} points", p_over), (f"Under {tline:.1f} points", 1 - p_over)],
                   MARGIN_TWO_WAY,
                   f"Expected total {tot:.1f} from both sides' official points for and against, "
                   f"normal with sigma {EL_TOTAL_SIGMA:.1f}."),
        ]
        fx = _fixture(
            id=f"EFE-EL-{g['id']}", sport="basketball",
            competition="Turkish Airlines EuroLeague 2026-27 — Round 7",
            event=f"{h['name']} v {a['name']}", start_utc=g["utc"], venue=g["venue"],
            status="verified", sources=[_src("el_sched"), _src("el_standings")],
            verification={
                "verdict": "confirmed", "checked_utc": D.SOURCES["el_standings"]["read_utc"],
                "evidence": D.SOURCES["el_standings"]["url"],
                "fields": ["start_utc", "venue", "won", "lost", "points for", "points against"],
            },
            flags=[],
            markets=markets,
            unavailable_markets=[{
                "key": "player_props", "label": "Player markets", "status": "unverified",
                "reason": "No player availability or rotation list was published on the feeds read.",
            }],
            olbg=next((r for r in D.OLBG_HARVEST if r["sport"] == "basketball"
                       and h["name"].split()[0] in r["event"]), None),
            inputs=[
                f"{h['name']}: {h['w']}-{h['l']} after {h['gp']} games, {h['pf']} points for / "
                f"{h['pa']} against ({hr:+.2f} per game), standings position {h['pos']}",
                f"{a['name']}: {a['w']}-{a['l']} after {a['gp']} games, {a['pf']} points for / "
                f"{a['pa']} against ({ar:+.2f} per game), standings position {a['pos']}",
            ],
        )
        out.append(_finalise(fx))

    # NBA — discovered on OLBG, never confirmed on an official feed.
    for row in D.OLBG_HARVEST:
        if row["sport"] != "basketball" or row["comp"] not in ("NBA", "PLK (Poland)"):
            continue
        fx = _fixture(
            id=_stable_id("EFE-NBA", row["comp"], row["event"]),
            sport="basketball", competition=row["comp"], event=row["event"],
            start_utc="", venue="", status="unverified",
            sources=[], verification={"verdict": "blocked",
                                      "checked_utc": "2026-10-23T16:40:00Z",
                                      "evidence": "https://www.nba.com/schedule",
                                      "fields": []},
            flags=["No official NBA source could be read (three endpoints returned HTTP 500 or "
                   "a retired-endpoint error). Start time, venue and both team records are left "
                   "blank and this fixture is not priced."],
            markets=[], unavailable_markets=[], olbg=row,
            inputs=[],
        )
        out.append(_finalise(fx))
    return out


# -------------------------------------------------------------------------- tennis
def build_tennis() -> list[dict]:
    out = []
    for m in D.ATP_MATCHES:
        pa, pb = D.ATP_POINTS.get(m["a"]), D.ATP_POINTS.get(m["b"])
        rated = pa is not None and pb is not None
        markets, unavailable, flags = [], [], []
        if rated:
            wa = pa ** TENNIS_K / (pa ** TENNIS_K + pb ** TENNIS_K)
            markets.append(market(
                "winner", "Win Match", [(m["a"], wa), (m["b"], 1 - wa)], MARGIN_TWO_WAY,
                f"PIF ATP ranking points raised to the power {TENNIS_K:.2f} and normalised "
                f"({pa:,} v {pb:,} points).",
            ))
            s = set_prob_from_match(wa)
            sets = [
                (f"{m['a']} 2-0", s * s),
                (f"{m['a']} 2-1", 2 * s * s * (1 - s)),
                (f"{m['b']} 2-1", 2 * (1 - s) * (1 - s) * s),
                (f"{m['b']} 2-0", (1 - s) * (1 - s)),
            ]
            markets.append(market("set_betting", "Set Betting (best of three)", sets,
                                  MARGIN_THREE_WAY,
                                  f"Per-set probability {s:.3f} inverted from the match price."))
            p_a_sh = s * s + 2 * s * s * (1 - s) + 2 * (1 - s) * (1 - s) * s
            markets.append(market(
                "handicap", f"Set Handicap {m['a']} -1.5 / {m['b']} +1.5",
                [(f"{m['a']} -1.5 sets", s * s), (f"{m['b']} +1.5 sets", 1 - s * s)],
                MARGIN_TWO_WAY, "Straight-sets win for the favourite against the field."))
            markets.append(market(
                "total", "Match Total Sets 2.5",
                [("Over 2.5 sets", 2 * s * (1 - s)), ("Under 2.5 sets", 1 - 2 * s * (1 - s))],
                MARGIN_TWO_WAY, "Probability the match reaches a deciding set."))
        else:
            missing = [n for n in (m["a"], m["b"]) if n not in D.ATP_POINTS]
            unavailable.append({
                "key": "winner", "label": "Win Match", "status": "unverified",
                "reason": (f"No PIF ATP ranking points were captured for {', '.join(missing)} in "
                           f"the pages read, so no price can be stated."),
            })
            flags.append(f"Blank price: ranking points for {', '.join(missing)} not captured. "
                         f"Fixture published for completeness only.")
        if m["utc"] is None:
            flags.append("Blank start time: the official order of play lists this match as "
                         "'Followed By' / not yet scheduled, so no UTC instant is published.")
        fx = _fixture(
            id="EFE-" + m["id"], sport="tennis", competition=m["tour"],
            event=f"{m['a']} v {m['b']} — {m['round']}", start_utc=m["utc"] or "",
            venue=m["court"], status="verified" if rated else "partial",
            sources=[_src(m["src"])] + ([_src("atp_rankings")] if rated else []),
            verification={
                "verdict": "confirmed" if rated else "partially confirmed",
                "checked_utc": D.SOURCES[m["src"]]["read_utc"],
                "evidence": D.SOURCES[m["src"]]["url"],
                "fields": ["round", "court", "scheduled order"] + (["ranking points"] if rated else []),
            },
            flags=flags, markets=markets, unavailable_markets=unavailable,
            olbg=next((r for r in D.OLBG_HARVEST if r["sport"] == "tennis"
                       and m["a"].split()[-1] in r["event"]), None),
            inputs=([f"{m['a']}: ATP No. {D.ATP_RANKS[m['a']]}, {pa:,} ranking points",
                     f"{m['b']}: ATP No. {D.ATP_RANKS[m['b']]}, {pb:,} ranking points"] if rated else [])
                   + [m["form"]],
        )
        out.append(_finalise(fx))
    return out


# ------------------------------------------------------------------------- snooker
def build_snooker() -> list[dict]:
    out = []
    for m in D.SNOOKER_MATCHES:
        A, B = D.SNOOKER_PLAYERS[m["a"]], D.SNOOKER_PLAYERS[m["b"]]
        qa = (A["fw"] + SNOOKER_PRIOR_FRAMES / 2) / (A["fw"] + A["fl"] + SNOOKER_PRIOR_FRAMES)
        qb = (B["fw"] + SNOOKER_PRIOR_FRAMES / 2) / (B["fw"] + B["fl"] + SNOOKER_PRIOR_FRAMES)
        q = log5(qa, qb)
        pa = first_to(6, q)
        markets = [
            market("winner", "Win Match", [(m["a"], pa), (m["b"], 1 - pa)], MARGIN_TWO_WAY,
                   f"Single-frame edge {q:.3f} from event frames won and lost (shrunk to a "
                   f"10-frame even prior), raced to six frames."),
            market("handicap", f"Frame Handicap {m['a']} -2.5 / {m['b']} +2.5",
                   [(f"{m['a']} -2.5 frames", first_to(6, q) * (1 - first_to(4, 1 - q)) if False else _frame_hcap(q, 2.5)),
                    (f"{m['b']} +2.5 frames", 1 - _frame_hcap(q, 2.5))],
                   MARGIN_TWO_WAY, "Race-to-six frame simulation with a 2.5-frame start."),
            market("total", "Match Total 9.5 Frames",
                   [("Over 9.5 frames", _frames_over(q, 9.5)),
                    ("Under 9.5 frames", 1 - _frames_over(q, 9.5))],
                   MARGIN_TWO_WAY, "Distribution of frames played in a race to six."),
        ]
        flags = []
        if "not captured" in A["window"] or "not captured" in B["window"]:
            flags.append("Uneven evidence window: one player's earlier-round frame line was not "
                         "captured in the page read, so the frame prior carries more weight on "
                         "that side. Disclosed rather than back-filled.")
        fx = _fixture(
            id="EFE-" + m["id"], sport="snooker",
            competition="BetVictor Northern Ireland Open 2026 (Belfast)",
            event=f"{m['a']} v {m['b']} — {m['label']}", start_utc=m["utc"],
            venue="Waterfront Hall, Belfast", status="verified",
            sources=[_src("wst_draw")],
            verification={"verdict": "confirmed", "checked_utc": D.SOURCES["wst_draw"]["read_utc"],
                          "evidence": D.SOURCES["wst_draw"]["url"],
                          "fields": ["round", "start time", "both names", "earlier-round frame scores"]},
            flags=flags, markets=markets, unavailable_markets=[],
            olbg=next((r for r in D.OLBG_HARVEST if r["sport"] == "snooker"
                       and m["a"].split()[-1] in r["event"]), None),
            inputs=[f"{m['a']}: {A['fw']}-{A['fl']} frames in this event ({A['window']})",
                    f"{m['b']}: {B['fw']}-{B['fl']} frames in this event ({B['window']})"],
        )
        out.append(_finalise(fx))
    return out


def _frame_hcap(q: float, start: float) -> float:
    """P(favourite wins by more than `start` frames) in a race to six."""
    total = 0.0
    for lost in range(0, 6):
        p = math.comb(5 + lost, lost) * (q ** 6) * ((1 - q) ** lost)
        if 6 - lost > start:
            total += p
    return max(min(total, 1 - 1e-6), 1e-6)


def _frames_over(q: float, line: float) -> float:
    total = 0.0
    for lost in range(0, 6):
        played = 6 + lost
        p = math.comb(5 + lost, lost) * ((q ** 6) * ((1 - q) ** lost) +
                                         ((1 - q) ** 6) * (q ** lost))
        if played > line:
            total += p
    return max(min(total, 1 - 1e-6), 1e-6)


# -------------------------------------------------------------------- motor racing
def build_motor_racing() -> list[dict]:
    pts = D.F1_POINTS
    field = sum(pts.values())
    last5 = [w for _, _, w in D.F1_RECENT_WINNERS]
    win = {}
    for name, p in pts.items():
        share = p / field
        form = last5.count(name) / len(last5)
        win[name] = 0.5 * share + 0.5 * form
    s = sum(win.values())
    win = {k: v / s for k, v in win.items()}
    podium = harville_top_n(win, 3)
    points_finish = harville_top_n(win, 8)

    markets = [
        market("winner", "Win Race — United States Grand Prix",
               sorted(((f"{k} — win the race", v) for k, v in win.items()), key=lambda kv: -kv[1]),
               MARGIN_OUTRIGHT,
               "Half the weight on each driver's share of the 2026 championship points among "
               "the top eight, half on their share of the last five grand prix wins."),
        market("podium", "Podium Finish (top three)",
               sorted(((f"{k} — podium finish", min(v, 0.97)) for k, v in podium.items()),
                      key=lambda kv: -kv[1]),
               MARGIN_OUTRIGHT, "Harville order-statistic expansion of the win prices. "
               "Three selections can win at once, so this column does not sum to 100%.",
               normalise=False),
        market("points", "Points Finish (top eight)",
               sorted(((f"{k} — points finish", min(v, 0.985)) for k, v in points_finish.items()),
                      key=lambda kv: -kv[1]),
               MARGIN_OUTRIGHT, "Harville expansion over the same eight-driver field. "
               "Eight selections can win at once, so this column does not sum to 100%.",
               normalise=False),
    ]
    fx = _fixture(
        id="EFE-F1-USA-2026", sport="motor-racing",
        competition="FIA Formula One World Championship 2026 — Round 21",
        event="FORMULA 1 MSC CRUISES UNITED STATES GRAND PRIX 2026",
        start_utc="2026-10-25T20:00:00Z",
        venue="Circuit of The Americas, Austin — 5.513 km, 56 laps, 308.432 km",
        status="verified",
        sources=[_src("f1_event"), _src("f1_drivers"), _src("f1_races")],
        verification={"verdict": "confirmed", "checked_utc": D.SOURCES["f1_races"]["read_utc"],
                      "evidence": D.SOURCES["f1_races"]["url"],
                      "fields": ["session schedule", "circuit length", "lap count",
                                 "drivers' standings", "last five race winners"]},
        flags=["Only an eight-driver field is priced — the official standings page was read down "
               "to eighth place. Drivers outside the top eight are not given a price rather than "
               "being assigned a guessed one.",
               "No qualifying result exists yet (qualifying is 2026-10-24T21:00:00Z), so grid "
               "position is absent from every price here."],
        markets=markets, unavailable_markets=[
            {"key": "fastest_qualifier", "label": "Fastest Qualifier", "status": "unverified",
             "reason": "Qualifying has not run and no official session timing exists yet."},
            {"key": "fastest_lap", "label": "Fastest Lap", "status": "unverified",
             "reason": "No official 2026 fastest-lap-by-race table was read."},
        ],
        olbg=next((r for r in D.OLBG_HARVEST if r["sport"] == "motor-racing"), None),
        inputs=[f"{k}: {v} championship points ({D.F1_TEAM[k]})" for k, v in pts.items()] +
               [f"Last five grands prix: " + ", ".join(f"{g} {d} — {w}" for g, d, w in D.F1_RECENT_WINNERS)],
    )
    return [_finalise(fx)]


# ------------------------------------------------------------------------- cricket
def build_cricket() -> list[dict]:
    out = []
    for f in D.CRICKET_FIXTURES:
        fx = _fixture(
            id="EFE-CR-" + f["id"].replace(":", ""), sport="cricket", competition=f["comp"],
            event=f["event"], start_utc=f["utc"], venue=f["venue"], status="partial",
            sources=[_src("ca_matches")],
            verification={"verdict": "confirmed", "checked_utc": D.SOURCES["ca_matches"]["read_utc"],
                          "evidence": D.SOURCES["ca_matches"]["url"],
                          "fields": ["match id", "competition", "both teams", "start_utc", "venue"]},
            flags=["Fixture confirmed, pricing withheld: the Cricket Australia matches index "
                   "publishes the schedule but no squad, form or ladder figures, and no separate "
                   "official standings page was read inside the session budget. Leaving every "
                   "market blank is the correct outcome rather than estimating one."],
            markets=[], unavailable_markets=[
                {"key": "winner", "label": "Win Match", "status": "unverified",
                 "reason": "No official team form, ladder or squad data was obtained."},
                {"key": "total", "label": "Match Total Runs", "status": "unverified",
                 "reason": "No official scoring rates for either side were obtained."},
            ],
            olbg=next((r for r in D.OLBG_HARVEST if r["sport"] == "cricket"
                       and f["event"].split(" v ")[0].split()[0] in r["event"]), None),
            inputs=[],
        )
        out.append(_finalise(fx))
    return out


# --------------------------------------------- discovery-only sports (blank+flagged)
DISCOVERY_ONLY = {
    "darts": ("PDC — pdc.tv serves only a CookieYes consent document on every readable chunk of "
              "the 2026 European Championship page, so neither the draw nor the session times "
              "could be confirmed."),
    "rugby-union": ("United Rugby Championship, LNR Pro D2 and Premiership Rugby fixture pages "
                    "either 404 or were not reachable inside the session budget."),
    "rugby-league": ("OLBG published no rugby-league match cards today — only three ante-post "
                     "outrights — so there was no fixture to confirm."),
    "handball": ("The LNH competition was renamed Daikin StarLigue and the old calendar path "
                 "404s; no handball governing-body page was read."),
    "volleyball": ("plusliga.pl redirects to tauronliga.pl and paginates past the session budget; "
                   "no volleyball federation page was read."),
    "golf": ("OLBG returned 'No tips found.' on every golf hub, and the PGA Tour 2026 tournament "
             "index path 404s. Nothing to price and nothing to confirm."),
    "gaelic": ("No county-board fixture page was read; the Cork and Galway championship ties "
               "discovered on OLBG are two days out."),
    "greyhounds": ("gbgb.org.uk/race-card/ returns the GBGB 404 template, so no runner, trap or "
                   "grade data could be obtained for any of the eight cards."),
}


def _stable_id(prefix: str, *parts: str) -> str:
    """Deterministic id. Python's str hash is salted per process, so it must not be used."""
    digest = hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:8]
    slug = re.sub(r"[^a-z0-9]+", "-", parts[-1].lower()).strip("-")[:40]
    return f"{prefix}-{slug}-{digest}" if slug else f"{prefix}-{digest}"


def build_discovery_only() -> list[dict]:
    out = []
    for sport, reason in DISCOVERY_ONLY.items():
        for row in D.OLBG_HARVEST:
            if row["sport"] != sport:
                continue
            fx = _fixture(
                id=_stable_id("EFE-DSC-" + sport, row["comp"], row["event"]),
                sport=sport, competition=row["comp"], event=row["event"],
                start_utc="", venue="", status="unverified", sources=[],
                verification={"verdict": "blocked", "checked_utc": "2026-10-23T16:26:00Z",
                              "evidence": _blocked_url(sport), "fields": []},
                flags=[f"Unverified — official source unavailable. {reason}"],
                markets=[], unavailable_markets=[], olbg=row, inputs=[],
            )
            out.append(_finalise(fx))
    return out


def _blocked_url(sport: str) -> str:
    for b in D.BLOCKED_SOURCES:
        if b["sport"] == sport:
            return b["url"]
    return "https://www.olbg.com/betting-tips"


def build_all() -> list[dict]:
    fixtures = []
    fixtures += build_ice_hockey()
    fixtures += build_baseball()
    fixtures += build_basketball()
    fixtures += build_tennis()
    fixtures += build_snooker()
    fixtures += build_motor_racing()
    fixtures += build_cricket()
    fixtures += build_discovery_only()
    return fixtures


if __name__ == "__main__":
    for fx in build_all():
        bp = fx["band_pick"]
        if bp and bp["confidence"] == "high":
            print(f"{fx['sport']:14s} {bp['tier']:22s} {bp['probability']:.4f} "
                  f"{bp['fair_american']:>7s}  {fx['event'][:46]:46s} | {bp['selection']}")
