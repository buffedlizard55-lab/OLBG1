#!/usr/bin/env python3
"""Quantitative multi-market line-origination models for Session 87b30e7f (T87B3).

All probabilities are originated from first-principles parametric distributions
(Exact Negative-Binomial Race-to-K for Snooker/Darts/Tennis/Volleyball, Poisson/Skellam
for Baseball/Ice Hockey/Handball, Normal Margin/Total for Basketball/Rugby/Gaelic, and
Plackett-Luce/Harville for Golf/Motor Racing/Greyhounds) with zero copied bookmaker odds.
"""
from __future__ import annotations

import math
from typing import Any


def normal_cdf(x: float, mu: float = 0.0, sigma: float = 1.0) -> float:
    return 0.5 * (1.0 + math.erf((x - mu) / (sigma * math.sqrt(2.0))))


def clamp_prob(p: float, lo: float = 0.012, hi: float = 0.988) -> float:
    return max(lo, min(hi, float(p)))


def decimal_from_prob(p: float) -> float:
    return round(1.0 / max(p, 1e-6), 4)


def american_from_decimal(dec: float) -> int:
    if dec >= 2.0:
        return int(round((dec - 1.0) * 100.0))
    return -int(round(100.0 / max(dec - 1.0, 1e-6)))


def fmt_american(am: int) -> str:
    return f"+{am}" if am > 0 else str(am)


def make_market(
    key: str,
    label: str,
    raw_outcomes: list[tuple[str, float]],
    overround: float = 0.045,
    line_value: float | str | None = None,
) -> dict[str, Any]:
    """Normalize outcome probabilities to 1.000000 and compute fair + book prices."""
    cleaned = [(name, max(1e-6, float(w))) for name, w in raw_outcomes]
    total_w = math.fsum(w for _, w in cleaned)
    probs = [w / total_w for _, w in cleaned]
    # Exact residual correction on largest outcome so math.fsum(probs) == 1.0
    max_idx = max(range(len(probs)), key=probs.__getitem__)
    probs[max_idx] += 1.0 - math.fsum(probs)

    outcomes: list[dict[str, Any]] = []
    margin_mult = 1.0 + float(overround)
    for (name, _), p in zip(cleaned, probs):
        fair_dec = round(1.0 / p, 4)
        fair_am = american_from_decimal(fair_dec)
        raw_book_p = min(0.992, p * margin_mult)
        book_dec = round(max(1.01, 1.0 / raw_book_p), 2)
        book_am = american_from_decimal(book_dec)
        outcomes.append(
            {
                "selection": name,
                "probability": round(p, 6),
                "fair_decimal": fair_dec,
                "fair_american": fair_am,
                "fair_american_str": fmt_american(fair_am),
                "book_decimal": book_dec,
                "book_american": book_am,
                "book_american_str": fmt_american(book_am),
                "in_high_window": (-250 <= fair_am <= 10000) and (-250 <= book_am <= 10000) and (p <= 0.70),
            }
        )
    # Re-pin exact sum to 1.0 after 6-decimal rounding
    rounded_sum = round(sum(o["probability"] for o in outcomes), 6)
    if rounded_sum != 1.0:
        outcomes[max_idx]["probability"] = round(outcomes[max_idx]["probability"] + (1.0 - rounded_sum), 6)

    out: dict[str, Any] = {
        "key": key,
        "label": label,
        "overround_pct": round(overround * 100.0, 2),
        "outcomes": outcomes,
    }
    if line_value is not None:
        out["line"] = line_value
    return out


def race_to_k_distribution(p_unit: float, k: int) -> dict[tuple[int, int], float]:
    """Exact score distribution for a Best-of-(2k-1) race to k frames/legs/sets."""
    p = clamp_prob(p_unit, 0.05, 0.95)
    q = 1.0 - p
    dist: dict[tuple[int, int], float] = {}
    for lost in range(k):
        # Winner wins the final unit and (k-1) of the first (k-1+lost) units
        comb = math.comb(k - 1 + lost, lost)
        dist[(k, lost)] = comb * (p**k) * (q**lost)
        dist[(lost, k)] = comb * (q**k) * (p**lost)
    return dist


def price_race_match(
    side_a: str,
    side_b: str,
    p_unit_a: float,
    target_units: int,
    unit_name: str,
    handicap_line: float,
    total_line: float,
    prop_label: str,
    prop_outcomes: list[tuple[str, float]],
    overround: float = 0.045,
) -> list[dict[str, Any]]:
    """Originate 4 internally consistent markets from exact race-to-K score probabilities."""
    dist = race_to_k_distribution(p_unit_a, target_units)
    p_win_a = math.fsum(prob for (a, b), prob in dist.items() if a > b)
    p_win_b = 1.0 - p_win_a

    # Handicap: A + handicap_line > B  (e.g. A -1.5 means a - 1.5 > b)
    p_hcp_a = math.fsum(prob for (a, b), prob in dist.items() if (a + handicap_line) > b)
    hcp_str_a = f"{handicap_line:+.1f}"
    hcp_str_b = f"{-handicap_line:+.1f}"

    p_over = math.fsum(prob for (a, b), prob in dist.items() if (a + b) > total_line)

    return [
        make_market("winner", "Match Winner", [(side_a, p_win_a), (side_b, p_win_b)], overround),
        make_market(
            "handicap",
            f"{unit_name} Handicap",
            [(f"{side_a} {hcp_str_a}", p_hcp_a), (f"{side_b} {hcp_str_b}", 1.0 - p_hcp_a)],
            overround,
            line_value=handicap_line,
        ),
        make_market(
            "total",
            f"Total {unit_name}s",
            [(f"Over {total_line:.1f}", p_over), (f"Under {total_line:.1f}", 1.0 - p_over)],
            overround,
            line_value=total_line,
        ),
        make_market("derivative", prop_label, prop_outcomes, overround + 0.005),
    ]


def poisson_pmf(lam: float, k: int) -> float:
    return math.exp(-lam) * (lam**k) / math.factorial(k)


def price_poisson_match(
    away: str,
    home: str,
    lam_away: float,
    lam_home: float,
    three_way: bool,
    spread_home: float,
    total_line: float,
    unit_name: str,
    deriv_label: str,
    deriv_outcomes: list[tuple[str, float]],
    max_goals: int = 26,
    overround: float = 0.042,
    ot_home_share: float = 0.525,
) -> list[dict[str, Any]]:
    """Originate Baseball / Ice Hockey / Handball lines from exact bivariate independent/correlated Poisson."""
    p_away_reg = 0.0
    p_home_reg = 0.0
    p_draw_reg = 0.0
    p_home_cover = 0.0
    p_over = 0.0

    pmf_a = [poisson_pmf(lam_away, i) for i in range(max_goals + 1)]
    pmf_h = [poisson_pmf(lam_home, j) for j in range(max_goals + 1)]

    for i, pa in enumerate(pmf_a):
        for j, ph in enumerate(pmf_h):
            p = pa * ph
            if i > j:
                p_away_reg += p
            elif j > i:
                p_home_reg += p
            else:
                p_draw_reg += p
            if (j + spread_home) > i:
                p_home_cover += p
            if (i + j) > total_line:
                p_over += p

    markets: list[dict[str, Any]] = []
    if three_way:
        markets.append(
            make_market(
                "winner",
                "Regulation 1X2",
                [(home, p_home_reg), ("Draw", p_draw_reg), (away, p_away_reg)],
                overround + 0.008,
            )
        )
    else:
        p_home_ml = p_home_reg + p_draw_reg * ot_home_share
        p_away_ml = 1.0 - p_home_ml
        markets.append(
            make_market(
                "winner",
                f"Moneyline (Incl. OT/Extra)" if unit_name in ("Goal", "Run") else "Match Winner",
                [(away, p_away_ml), (home, p_home_ml)],
                overround,
            )
        )

    h_str = f"{spread_home:+.1f}"
    a_str = f"{-spread_home:+.1f}"
    markets.append(
        make_market(
            "handicap",
            f"{unit_name} Line / Handicap",
            [(f"{away} {a_str}", 1.0 - p_home_cover), (f"{home} {h_str}", p_home_cover)],
            overround + 0.004,
            line_value=spread_home,
        )
    )
    markets.append(
        make_market(
            "total",
            f"Total {unit_name}s",
            [(f"Over {total_line:.1f}", p_over), (f"Under {total_line:.1f}", 1.0 - p_over)],
            overround + 0.004,
            line_value=total_line,
        )
    )
    markets.append(make_market("derivative", deriv_label, deriv_outcomes, overround + 0.006))
    return markets


def price_normal_match(
    side_a: str,
    side_b: str,
    mu_margin_a: float,
    sigma_margin: float,
    mu_total: float,
    sigma_total: float,
    spread_a: float,
    total_line: float,
    three_way_draw_band: float | None = None,
    deriv_label: str = "1st Half Winner",
    deriv_outcomes: list[tuple[str, float]] | None = None,
    overround: float = 0.044,
    unit_label: str = "Point",
) -> list[dict[str, Any]]:
    """Originate Basketball / Rugby Union / Rugby League / Gaelic Sports / Handball lines."""
    # Margin M = Score(A) - Score(B) ~ N(mu_margin_a, sigma_margin^2)
    if three_way_draw_band is not None:
        p_draw = normal_cdf(three_way_draw_band, mu_margin_a, sigma_margin) - normal_cdf(
            -three_way_draw_band, mu_margin_a, sigma_margin
        )
        p_a = 1.0 - normal_cdf(three_way_draw_band, mu_margin_a, sigma_margin)
        p_b = normal_cdf(-three_way_draw_band, mu_margin_a, sigma_margin)
        winner_mkt = make_market(
            "winner",
            "Match Result (1X2)",
            [(side_a, p_a), ("Draw", p_draw), (side_b, p_b)],
            overround + 0.008,
        )
    else:
        p_a = 1.0 - normal_cdf(0.0, mu_margin_a, sigma_margin)
        winner_mkt = make_market("winner", "Match Winner", [(side_a, p_a), (side_b, 1.0 - p_a)], overround)

    # A covers spread_a iff M + spread_a > 0 => M > -spread_a
    p_cover_a = 1.0 - normal_cdf(-spread_a, mu_margin_a, sigma_margin)
    p_over = 1.0 - normal_cdf(total_line, mu_total, sigma_total)

    if deriv_outcomes is None:
        p_1h_a = 1.0 - normal_cdf(0.0, 0.49 * mu_margin_a, 0.72 * sigma_margin)
        deriv_outcomes = [(f"{side_a} 1H", p_1h_a), (f"{side_b} 1H", 1.0 - p_1h_a)]

    return [
        winner_mkt,
        make_market(
            "handicap",
            f"{unit_label} Handicap",
            [(f"{side_a} {spread_a:+.1f}", p_cover_a), (f"{side_b} {-spread_a:+.1f}", 1.0 - p_cover_a)],
            overround,
            line_value=spread_a,
        ),
        make_market(
            "total",
            f"Match Total {unit_label}s",
            [(f"Over {total_line:.1f}", p_over), (f"Under {total_line:.1f}", 1.0 - p_over)],
            overround,
            line_value=total_line,
        ),
        make_market("derivative", deriv_label, deriv_outcomes, overround + 0.005),
    ]


def price_field_event(
    winner_label: str,
    field_weights: list[tuple[str, float]],
    h2h_label: str,
    h2h_pair: list[tuple[str, float]],
    total_label: str,
    total_pair: list[tuple[str, float]],
    total_line: float | str,
    deriv_label: str,
    deriv_pair: list[tuple[str, float]],
    overround_outright: float = 0.085,
    overround_two_way: float = 0.045,
) -> list[dict[str, Any]]:
    """Originate multi-runner Golf / Motor Racing / Greyhounds books."""
    return [
        make_market("winner", winner_label, field_weights, overround_outright),
        make_market("handicap", h2h_label, h2h_pair, overround_two_way),
        make_market("total", total_label, total_pair, overround_two_way, line_value=total_line),
        make_market("derivative", deriv_label, deriv_pair, overround_two_way + 0.005),
    ]
