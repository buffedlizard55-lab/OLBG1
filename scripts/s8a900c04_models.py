"""Deterministic multi-market statistical pricing models for session 8a900c04 (2026-10-23 UTC).

Every probability and line is originated exclusively from verified official team/player
performance metrics, venue effects, and injury adjustments — never from bookmaker odds or
OLBG tipster vote shares.
"""
from __future__ import annotations

import math
from typing import Dict, List, Tuple


HIGH_MIN_DECIMAL = 1.4000   # -250 American lower bound
HIGH_MAX_DECIMAL = 101.0000 # +10000 American upper bound
HIGH_MIN_PROB = 0.7000      # strict >70% probability floor for High confidence


def clamp_prob(p: float, lo: float = 0.0020, hi: float = 0.9950) -> float:
    return max(lo, min(hi, float(p)))


def prob_to_decimal(p: float) -> float:
    return round(1.0 / clamp_prob(p), 4)


def prob_to_american(p: float) -> int:
    p = clamp_prob(p)
    if abs(p - 0.5) < 1e-9:
        return 100
    if p > 0.5:
        return -int(round(100.0 * p / (1.0 - p)))
    return int(round(100.0 * (1.0 - p) / p))


def in_high_odds_window(p: float) -> bool:
    dec = prob_to_decimal(p)
    amer = prob_to_american(p)
    return (HIGH_MIN_DECIMAL <= dec <= HIGH_MAX_DECIMAL) and (-250 <= amer <= 10000)


def classify_confidence(p: float) -> Tuple[str, bool, str]:
    """Return (confidence_tier, chalk_suppressed, reason)."""
    p = clamp_prob(p)
    dec = prob_to_decimal(p)
    amer = prob_to_american(p)
    if p > HIGH_MIN_PROB and in_high_odds_window(p):
        return (
            "high",
            False,
            f"Clears >70% fair win probability ({p*100:.1f}%) inside actionable [-250, +10000] window ({amer:+d} / {dec:.2f}).",
        )
    if p > HIGH_MIN_PROB and not in_high_odds_window(p):
        return (
            "medium",
            True,
            f"Chalk-suppressed from High: {p*100:.1f}% fair probability prices at {amer:+d} ({dec:.2f}), shorter than -250 floor.",
        )
    if p >= 0.5750:
        return (
            "medium",
            False,
            f"Solid positive expectation ({p*100:.1f}%, {amer:+d} / {dec:.2f}) below >70% High threshold.",
        )
    return (
        "low",
        False,
        f"High-variance or price-sensitive spot ({p*100:.1f}%, {amer:+d} / {dec:.2f}).",
    )


def normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def poisson_pmf(lam: float, k: int) -> float:
    if lam <= 0.0:
        return 1.0 if k == 0 else 0.0
    return math.exp(-lam + k * math.log(lam) - math.lgamma(k + 1))


def best_of_n_win_prob(p_unit: float, best_of: int) -> Tuple[float, Dict[str, float]]:
    """Exact binomial/negative-binomial series probabilities for best-of-N frames/sets/legs."""
    need = best_of // 2 + 1
    p = clamp_prob(p_unit, 0.02, 0.98)
    q = 1.0 - p
    scores: Dict[str, float] = {}
    p_win_a = 0.0
    for lost in range(need):
        comb = math.comb(need - 1 + lost, lost)
        prob_a = comb * (p ** need) * (q ** lost)
        prob_b = comb * (q ** need) * (p ** lost)
        scores[f"{need}-{lost}"] = prob_a
        scores[f"{lost}-{need}"] = prob_b
        p_win_a += prob_a
    return clamp_prob(p_win_a), scores


def make_line(
    market_type: str,
    market_label: str,
    selection: str,
    prob: float,
    settlement_basis: str,
    counter_selection: str | None = None,
    counter_prob: float | None = None,
) -> Dict:
    p = clamp_prob(prob)
    dec = prob_to_decimal(p)
    amer = prob_to_american(p)
    conf, chalk_suppressed, reason = classify_confidence(p)
    out = {
        "market_type": market_type,
        "market_label": market_label,
        "selection": selection,
        "fair_prob": round(p, 4),
        "fair_pct": round(p * 100.0, 2),
        "fair_decimal": dec,
        "fair_american": amer,
        "in_window": in_high_odds_window(p),
        "confidence": conf,
        "chalk_suppressed": chalk_suppressed,
        "confidence_reason": reason,
        "settlement_basis": settlement_basis,
    }
    if counter_selection is not None and counter_prob is not None:
        cp = clamp_prob(counter_prob)
        out["counter_selection"] = counter_selection
        out["counter_prob"] = round(cp, 4)
        out["counter_decimal"] = prob_to_decimal(cp)
        out["counter_american"] = prob_to_american(cp)
    return out


def price_gaussian_match(
    home: str,
    away: str,
    exp_home: float,
    exp_away: float,
    sd_margin: float,
    sd_total: float,
    unit_name: str,
    period_label: str,
    prop_label: str,
    prop_selection: str,
    prop_prob: float,
    draw_band: float = 0.0,
) -> Tuple[List[Dict], Dict]:
    """Originate 6 market types from opponent- & injury-adjusted scoring expectations."""
    mu_diff = exp_home - exp_away
    mu_tot = exp_home + exp_away

    if draw_band > 0.0:
        p_home = 1.0 - normal_cdf((draw_band - mu_diff) / sd_margin)
        p_away = normal_cdf((-draw_band - mu_diff) / sd_margin)
        p_draw = max(0.005, 1.0 - p_home - p_away)
        # Also compute 2-way DNB / OT-inclusive win prob
        p_win_home = 1.0 - normal_cdf((0.0 - mu_diff) / sd_margin)
    else:
        p_home = 1.0 - normal_cdf((0.0 - mu_diff) / sd_margin)
        p_away = 1.0 - p_home
        p_draw = 0.0
        p_win_home = p_home

    fav_is_home = p_win_home >= 0.5
    fav_team = home if fav_is_home else away
    dog_team = away if fav_is_home else home
    fav_p = p_win_home if fav_is_home else (1.0 - p_win_home)

    markets: List[Dict] = []
    markets.append(
        make_line(
            "winner",
            "Match Winner (2-Way)" if draw_band == 0.0 else "Match Result / Winner",
            f"{fav_team} to Win",
            fav_p,
            f"Official full-game result ({unit_name})",
            f"{dog_team} to Win",
            1.0 - fav_p,
        )
    )

    # Search half-point handicap lines so we inspect both balanced spread AND Golden Window alt spread
    fav_mu = mu_diff if fav_is_home else -mu_diff
    balanced_line = round(fav_mu - 0.5) + 0.5
    if balanced_line < 0.5:
        balanced_line = 0.5
    p_bal = 1.0 - normal_cdf((balanced_line - fav_mu) / sd_margin)
    markets.append(
        make_line(
            "handicap",
            f"Primary Handicap ({unit_name})",
            f"{fav_team} -{balanced_line:.1f}" if p_bal >= 0.5 else f"{dog_team} +{balanced_line:.1f}",
            p_bal if p_bal >= 0.5 else 1.0 - p_bal,
            f"Half-{unit_name} handicap (zero push)",
            f"{dog_team} +{balanced_line:.1f}" if p_bal >= 0.5 else f"{fav_team} -{balanced_line:.1f}",
            (1.0 - p_bal) if p_bal >= 0.5 else p_bal,
        )
    )

    # Search half-point alt handicap/spread across [-28.5, +18.5] for calibrated Golden Window line
    best_alt = None
    for step in range(-60, 61):
        line_val = step + 0.5  # e.g., -3.5 means fav gives 3.5 -> threshold = +3.5
        p_cov = 1.0 - normal_cdf((line_val - fav_mu) / sd_margin)
        if 0.7015 <= p_cov <= 0.7135:
            cand_sel = f"{fav_team} {-line_val:+.1f}"
            opp_sel = f"{dog_team} {line_val:+.1f}"
            best_alt = (abs(p_cov - 0.7080), cand_sel, p_cov, opp_sel)
            break
    if best_alt is not None:
        _, c_sel, c_p, o_sel = best_alt
        markets.append(
            make_line(
                "alt-handicap",
                f"Actionable Spread / Handicap ({unit_name})",
                c_sel,
                c_p,
                f" Calibrated {unit_name} handicap within [-250, +10000]",
                o_sel,
                1.0 - c_p,
            )
        )

    # Game total Over / Under
    tot_line = math.floor(mu_tot) + 0.5
    # Offset total slightly toward strongest data edge or check alt total
    p_over = 1.0 - normal_cdf((tot_line - mu_tot) / sd_total)
    over_fav = p_over >= 0.5
    markets.append(
        make_line(
            "total",
            f"Match Total ({unit_name})",
            f"Over {tot_line:.1f} {unit_name}" if over_fav else f"Under {tot_line:.1f} {unit_name}",
            p_over if over_fav else (1.0 - p_over),
            f"Combined full-game {unit_name}",
            f"Under {tot_line:.1f} {unit_name}" if over_fav else f"Over {tot_line:.1f} {unit_name}",
            (1.0 - p_over) if over_fav else p_over,
        )
    )

    # Team Total market (higher-rated offense Over or lower-rated offense Under)
    sd_team = sd_total * 0.64
    tt_line = math.floor(exp_home - 0.35 * sd_team) + 0.5 if fav_is_home else math.floor(exp_away - 0.35 * sd_team) + 0.5
    tt_mu = exp_home if fav_is_home else exp_away
    p_tt = 1.0 - normal_cdf((tt_line - tt_mu) / sd_team)
    markets.append(
        make_line(
            "team-total",
            f"{fav_team} Team Total ({unit_name})",
            f"{fav_team} Over {tt_line:.1f}",
            p_tt,
            f"Official {fav_team} team score ({unit_name})",
            f"{fav_team} Under {tt_line:.1f}",
            1.0 - p_tt,
        )
    )

    # First-half / period derivative
    p_fh = 1.0 - normal_cdf((0.0 - 0.52 * fav_mu) / (sd_margin * 0.72))
    markets.append(
        make_line(
            "period",
            period_label,
            f"{fav_team} {period_label} Winner (DNB)",
            p_fh,
            f"Official {period_label.lower()} scoring",
            f"{dog_team} {period_label} Winner (DNB)",
            1.0 - p_fh,
        )
    )

    # Player prop / derivative
    markets.append(
        make_line(
            "player-prop",
            prop_label,
            prop_selection,
            prop_prob,
            "Official governing-body boxscore / match sheet",
        )
    )

    meta = {
        "exp_home": round(exp_home, 2),
        "exp_away": round(exp_away, 2),
        "exp_margin": round(mu_diff, 2),
        "exp_total": round(mu_tot, 2),
        "p_home_win": round(p_win_home, 4),
        "p_draw": round(p_draw, 4),
    }
    return markets, meta


def price_poisson_match(
    home: str,
    away: str,
    lam_home: float,
    lam_away: float,
    unit_name: str,
    ot_home_share: float,
    period_label: str,
    prop_label: str,
    prop_selection: str,
    prop_prob: float,
    max_k: int = 24,
) -> Tuple[List[Dict], Dict]:
    """Exact bivariate independent Poisson + OT resolution for MLB / NHL."""
    pmf_h = [poisson_pmf(lam_home, k) for k in range(max_k + 1)]
    pmf_a = [poisson_pmf(lam_away, k) for k in range(max_k + 1)]

    p_reg_h = 0.0
    p_reg_a = 0.0
    p_tie = 0.0
    diff_probs: Dict[int, float] = {}
    tot_probs: Dict[int, float] = {}
    for i in range(max_k + 1):
        for j in range(max_k + 1):
            pr = pmf_h[i] * pmf_a[j]
            d = i - j
            t = i + j
            diff_probs[d] = diff_probs.get(d, 0.0) + pr
            tot_probs[t] = tot_probs.get(t, 0.0) + pr
            if i > j:
                p_reg_h += pr
            elif j > i:
                p_reg_a += pr
            else:
                p_tie += pr

    p_win_h = p_reg_h + p_tie * ot_home_share
    p_win_a = 1.0 - p_win_h
    fav_is_home = p_win_h >= 0.5
    fav = home if fav_is_home else away
    dog = away if fav_is_home else home
    fav_p = p_win_h if fav_is_home else p_win_a

    # Standard +/- 1.5 run/puck line (including OT 1-goal win for +1.5 dog cover)
    # Favorite -1.5 requires regulation win by >=2 goals/runs (plus walk-off HR edge in MLB ~18% of extras)
    extra_two = 0.16 * p_tie * (ot_home_share if fav_is_home else (1.0 - ot_home_share))
    p_fav_minus_15 = sum(pr for d, pr in diff_probs.items() if (d >= 2 if fav_is_home else d <= -2)) + extra_two
    p_dog_plus_15 = 1.0 - p_fav_minus_15

    # Standard + alternate totals
    mu_tot = lam_home + lam_away
    std_tot = round(mu_tot * 2.0) / 2.0
    if std_tot == int(std_tot):
        std_tot += 0.5
    p_over_std = sum(pr for t, pr in tot_probs.items() if t > std_tot) + (0.55 * p_tie if std_tot - mu_tot < 0.8 else 0.35 * p_tie) * 0.25
    p_over_std = clamp_prob(sum(pr for t, pr in tot_probs.items() if t > std_tot))

    markets: List[Dict] = [
        make_line(
            "winner",
            "Moneyline (Incl. OT/Extra Innings)",
            f"{fav} Moneyline",
            fav_p,
            f"Official final winner including overtime/extra {unit_name.lower()}",
            f"{dog} Moneyline",
            1.0 - fav_p,
        ),
        make_line(
            "handicap",
            f"{'Run' if unit_name == 'Runs' else 'Puck'} Line (+/-1.5)",
            f"{dog} +1.5" if p_dog_plus_15 >= p_fav_minus_15 else f"{fav} -1.5",
            max(p_dog_plus_15, p_fav_minus_15),
            f"Official +/-1.5 {unit_name.lower()} handicap",
            f"{fav} -1.5" if p_dog_plus_15 >= p_fav_minus_15 else f"{dog} +1.5",
            min(p_dog_plus_15, p_fav_minus_15),
        ),
        make_line(
            "total",
            f"Game Total ({unit_name})",
            f"Over {std_tot:.1f} {unit_name}" if p_over_std >= 0.5 else f"Under {std_tot:.1f} {unit_name}",
            p_over_std if p_over_std >= 0.5 else 1.0 - p_over_std,
            f"Regulation + overtime combined {unit_name.lower()}",
            f"Under {std_tot:.1f} {unit_name}" if p_over_std >= 0.5 else f"Over {std_tot:.1f} {unit_name}",
            (1.0 - p_over_std) if p_over_std >= 0.5 else p_over_std,
        ),
    ]

    # Check exact Poisson alt total or +2.5/-1.5 line landing closest to Golden Window [0.701, 0.714]
    candidates = []
    for k_line in range(2, 13):
        half = k_line + 0.5
        po = clamp_prob(sum(pr for t, pr in tot_probs.items() if t > half))
        pu = 1.0 - po
        candidates.append((abs(po - 0.708), f"Over {half:.1f} {unit_name}", po, f"Under {half:.1f} {unit_name}"))
        candidates.append((abs(pu - 0.708), f"Under {half:.1f} {unit_name}", pu, f"Over {half:.1f} {unit_name}"))
    p_dog_25 = 1.0 - sum(pr for d, pr in diff_probs.items() if (d >= 3 if fav_is_home else d <= -3))
    candidates.append((abs(p_dog_25 - 0.708), f"{dog} +2.5", p_dog_25, f"{fav} -2.5"))
    candidates.sort(key=lambda x: x[0])
    _, alt_sel, alt_p, alt_opp = candidates[0]
    markets.append(
        make_line(
            "alt-total",
            f"Alternate Line / Total ({unit_name})",
            alt_sel,
            alt_p,
            f"Exact Poisson {unit_name.lower()} distribution line",
            alt_opp,
            1.0 - alt_p,
        )
    )

    # Team total
    fav_lam = lam_home if fav_is_home else lam_away
    tt_half = max(1.5, math.floor(fav_lam) - 0.5)
    p_tt = clamp_prob(1.0 - sum(poisson_pmf(fav_lam, k) for k in range(int(tt_half) + 1)))
    markets.append(
        make_line(
            "team-total",
            f"{fav} Team Total ({unit_name})",
            f"{fav} Over {tt_half:.1f} {unit_name}",
            p_tt,
            f"Official {fav} team {unit_name.lower()}",
            f"{fav} Under {tt_half:.1f} {unit_name}",
            1.0 - p_tt,
        )
    )

    # Period / First-5-innings / 1st Period DNB
    f_share = 0.55 if unit_name == "Runs" else 0.31
    pmf_fh = [poisson_pmf(lam_home * f_share, k) for k in range(14)]
    pmf_fa = [poisson_pmf(lam_away * f_share, k) for k in range(14)]
    fh_h = sum(pmf_fh[i] * pmf_fa[j] for i in range(14) for j in range(14) if i > j)
    fh_a = sum(pmf_fh[i] * pmf_fa[j] for i in range(14) for j in range(14) if j > i)
    fh_dnb = fh_h / max(1e-6, fh_h + fh_a)
    markets.append(
        make_line(
            "period",
            period_label,
            f"{fav} {period_label} (Draw No Bet)",
            fh_dnb if fav_is_home else 1.0 - fh_dnb,
            f"Official {period_label.lower()} score (push if tied)",
            f"{dog} {period_label} (Draw No Bet)",
            (1.0 - fh_dnb) if fav_is_home else fh_dnb,
        )
    )

    markets.append(
        make_line(
            "player-prop",
            prop_label,
            prop_selection,
            prop_prob,
            "Official league boxscore / play-by-play",
        )
    )

    meta = {
        "exp_home": round(lam_home, 2),
        "exp_away": round(lam_away, 2),
        "exp_margin": round(lam_home - lam_away, 2),
        "exp_total": round(mu_tot, 2),
        "p_home_win": round(p_win_h, 4),
        "p_reg_tie": round(p_tie, 4),
    }
    return markets, meta


def price_series_match(
    player_a: str,
    player_b: str,
    p_unit_a: float,
    best_of: int,
    unit_singular: str,
    unit_plural: str,
    prop_label: str,
    prop_selection: str,
    prop_prob: float,
) -> Tuple[List[Dict], Dict]:
    """Exact Markov series model for Darts (legs), Snooker (frames), Tennis (sets), Volleyball (sets)."""
    p_match_a, exact_scores = best_of_n_win_prob(p_unit_a, best_of)
    need = best_of // 2 + 1
    fav_is_a = p_match_a >= 0.5
    fav = player_a if fav_is_a else player_b
    dog = player_b if fav_is_a else player_a
    fav_p = p_match_a if fav_is_a else (1.0 - p_match_a)

    # Margin & total distributions directly from exact score probabilities!
    margins_fav: Dict[int, float] = {}
    totals: Dict[int, float] = {}
    for sc, pr in exact_scores.items():
        sa, sb = [int(x) for x in sc.split("-")]
        m = (sa - sb) if fav_is_a else (sb - sa)
        t = sa + sb
        margins_fav[m] = margins_fav.get(m, 0.0) + pr
        totals[t] = totals.get(t, 0.0) + pr

    markets: List[Dict] = [
        make_line(
            "winner",
            f"Match Winner (Best of {best_of} {unit_plural})",
            f"{fav} to Win",
            fav_p,
            f"First to {need} {unit_plural.lower()}",
            f"{dog} to Win",
            1.0 - fav_p,
        )
    ]

    # Handicap search across all valid half-unit handicaps 1.5 .. need-0.5
    h_cands = []
    for k in range(1, need):
        h = k + 0.5
        p_fav_cov = clamp_prob(sum(pr for m, pr in margins_fav.items() if m > h))
        p_dog_cov = 1.0 - p_fav_cov
        h_cands.append((abs(p_fav_cov - 0.708), f"{fav} -{h:.1f} {unit_plural}", p_fav_cov, f"{dog} +{h:.1f} {unit_plural}"))
        h_cands.append((abs(p_dog_cov - 0.708), f"{dog} +{h:.1f} {unit_plural}", p_dog_cov, f"{fav} -{h:.1f} {unit_plural}"))

    # Standard -1.5 / +1.5 line first
    p_std_fav = clamp_prob(sum(pr for m, pr in margins_fav.items() if m > 1.5))
    markets.append(
        make_line(
            "handicap",
            f"{unit_singular} Handicap (-1.5 / +1.5)",
            f"{fav} -1.5 {unit_plural}" if p_std_fav >= 0.5 else f"{dog} +1.5 {unit_plural}",
            max(p_std_fav, 1.0 - p_std_fav),
            f"Official {unit_singular.lower()} margin",
            f"{dog} +1.5 {unit_plural}" if p_std_fav >= 0.5 else f"{fav} -1.5 {unit_plural}",
            min(p_std_fav, 1.0 - p_std_fav),
        )
    )

    # Best total line (Over/Under) across all valid totals need .. best_of-1
    t_cands = []
    for k in range(need, best_of):
        line_t = k + 0.5
        po = clamp_prob(sum(pr for t, pr in totals.items() if t > line_t))
        pu = 1.0 - po
        t_cands.append((abs(po - 0.708), f"Over {line_t:.1f} {unit_plural}", po, f"Under {line_t:.1f} {unit_plural}"))
        t_cands.append((abs(pu - 0.708), f"Under {line_t:.1f} {unit_plural}", pu, f"Over {line_t:.1f} {unit_plural}"))
    all_cands = sorted(h_cands + t_cands, key=lambda x: x[0])
    t_cands.sort(key=lambda x: x[0])
    _, t_sel, t_p, t_opp = t_cands[0]
    markets.append(
        make_line(
            "total",
            f"Total {unit_plural} Over / Under",
            t_sel,
            t_p,
            f"Total {unit_plural.lower()} contested in match",
            t_opp,
            1.0 - t_p,
        )
    )

    # Add best calibrated line if different from standard -1.5/total
    _, best_sel, best_p, best_opp = all_cands[0]
    if best_sel not in {markets[1]["selection"], markets[2]["selection"]}:
        markets.append(
            make_line(
                "alt-handicap",
                f"Alternate {unit_singular} Handicap",
                best_sel,
                best_p,
                f"Exact {unit_singular.lower()} distribution handicap",
                best_opp,
                1.0 - best_p,
            )
        )

    # Opening unit winner (1st Set / 1st Frame / Opening 2 Legs)
    p_first = p_unit_a if fav_is_a else (1.0 - p_unit_a)
    markets.append(
        make_line(
            "period",
            f"1st {unit_singular} Winner",
            f"{fav} to Win 1st {unit_singular}",
            p_first,
            f"Official 1st {unit_singular.lower()} winner",
            f"{dog} to Win 1st {unit_singular}",
            1.0 - p_first,
        )
    )

    # Most likely exact score
    top_sc, top_sc_p = max(exact_scores.items(), key=lambda kv: kv[1])
    sa, sb = [int(x) for x in top_sc.split("-")]
    sc_label = f"{player_a} {sa}-{sb}" if sa > sb else f"{player_b} {sb}-{sa}"
    markets.append(
        make_line(
            "correct-score",
            f"Exact {unit_singular} Score",
            sc_label,
            top_sc_p,
            f"Official final {unit_singular.lower()} score",
        )
    )

    markets.append(
        make_line(
            "player-prop",
            prop_label,
            prop_selection,
            prop_prob,
            "Official governing-body match statistics",
        )
    )

    exp_tot = sum(t * pr for t, pr in totals.items())
    exp_m = sum(m * pr for m, pr in margins_fav.items()) * (1.0 if fav_is_a else -1.0)
    meta = {
        "unit_prob_a": round(p_unit_a, 4),
        "best_of": best_of,
        "exp_total": round(exp_tot, 2),
        "exp_margin": round(exp_m, 2),
        "p_home_win": round(p_match_a, 4),
    }
    return markets, meta


def select_recommended_pick(markets: List[Dict]) -> Dict:
    """Choose the sharpest primary betting selection across all originated markets:
    1) Any High-confidence selection strictly inside [-250, +10000] (highest fair_prob first).
    2) Otherwise highest-probability non-chalk-suppressed selection inside [-250, +10000].
    3) Fallback to primary Match Winner line.
    """
    highs = [m for m in markets if m["confidence"] == "high" and m["in_window"] and not m["chalk_suppressed"]]
    if highs:
        return sorted(highs, key=lambda m: m["fair_prob"], reverse=True)[0]
    in_win = [m for m in markets if m["in_window"] and not m["chalk_suppressed"]]
    if in_win:
        return sorted(in_win, key=lambda m: m["fair_prob"], reverse=True)[0]
    return markets[0]
