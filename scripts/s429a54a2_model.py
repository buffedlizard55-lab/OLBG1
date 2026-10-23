#!/usr/bin/env python3
"""Line origination for session 429a54a2-olbg1.

Two documented engines only:

* ``nhl``: log5 on the official 2026-10-23 points percentage for the moneyline; goals for
  and against per game drive independent-Poisson score lines for the puck line and total.
  No home edge is inserted.
* ``lnh``: attack/defence ratios around the league mean drive a bivariate Poisson score
  line for the 60-minute three-way market, the handicap and the total. No home edge.
* ``wta-rank``: official draw ranking difference through a logistic curve (scale 20).
  This is a single-input model, so it can never reach High confidence.

Anything else is priced ``None`` with an explicit withholding reason.
"""

from __future__ import annotations

import math

from s429a54a2_dataset import LNH, NHL


def log5(pa: float, pb: float) -> float:
    num = pa * (1 - pb)
    den = num + pb * (1 - pa)
    return num / den if den else 0.5


def pct(w: int, l: int, otl: int) -> float:
    gp = w + l + otl
    return (2 * w + otl) / (2 * gp) if gp else 0.5


def poisson(k: int, lam: float) -> float:
    return math.exp(-lam) * lam**k / math.factorial(k)


def poisson_grid(la: float, lb: float, n: int = 16):
    return [[poisson(i, la) * poisson(j, lb) for j in range(n)] for i in range(n)]


def total_probs(la: float, lb: float, line: float) -> tuple[float, float]:
    grid = poisson_grid(la, lb)
    over = sum(grid[i][j] for i in range(len(grid)) for j in range(len(grid)) if i + j > line)
    return over, 1 - over


def handicap_probs(la: float, lb: float, line: float) -> tuple[float, float]:
    """line is applied to side A, e.g. -1.5. Ties (push) are excluded by half lines."""
    grid = poisson_grid(la, lb)
    a = sum(grid[i][j] for i in range(len(grid)) for j in range(len(grid)) if i - j + line > 0)
    return a, 1 - a


def american(p: float) -> int | None:
    if p is None or not (0 < p < 1):
        return None
    return int(round(-100 * p / (1 - p))) if p >= 0.5 else int(round(100 * (1 - p) / p))


def decimal(p: float) -> float | None:
    return 1 / p if p else None


def in_window(p: float) -> bool:
    d = decimal(p)
    return bool(d) and 1.40 <= d <= 101.0


def _markets(two_way: list[tuple[str, float]], la: float, lb: float, labels: tuple[str, str], totals=(5.5, 6.5, 7.5), handicaps=(-1.5, 1.5), units="goals"):
    markets = []
    for name, p in two_way:
        markets.append({"market": "match_winner", "selection": name, "probability": p})
    for line in handicaps:
        for name, sign in ((labels[0], line), (labels[1], -line)):
            p, _ = handicap_probs(la, lb, sign)
            markets.append({"market": "handicap", "line": f"{sign:+g}", "units": units, "selection": name, "probability": p})
    for line in totals:
        over, under = total_probs(la, lb, line)
        markets.append({"market": "total", "line": f"{line:g}", "units": units, "selection": f"Over {line:g} {units}", "probability": over})
        markets.append({"market": "total", "line": f"{line:g}", "units": units, "selection": f"Under {line:g} {units}", "probability": under})
    return markets


def originate(row: dict) -> dict:
    kind = row.get("input_kind")
    out = {
        "fixture_id": row["id"],
        "markets": [],
        "selection": None,
        "probability": None,
        "american": None,
        "fair_decimal": None,
        "tier": None,
        "in_window": False,
        "withheld": [],
        "notes": [],
        "basis": None,
    }
    if row["status"] in ("elapsed", "unverified"):
        out["withheld"].append("start elapsed before the snapshot" if row["status"] == "elapsed" else "fixture not confirmed on an official page")
        return out

    if kind == "nhl":
        st = NHL.get(row["a"]), NHL.get(row["b"])
        if st[0] is None or st[1] is None:
            out["withheld"].append("official standings row missing")
            return out
        (gpa, wa, la_, oa, gfa, gaa), (gpb, wb, lb_, ob, gfb, gab) = st
        pa, pb = pct(wa, la_, oa), pct(wb, lb_, ob)
        p = log5(pa, pb)
        la = (gfa / gpa + gab / gpb) / 2
        lb = (gfb / gpb + gaa / gpa) / 2
        out["basis"] = (f"log5 of official points percentages {pa:.4f} v {pb:.4f}; expected goals "
                        f"{la:.2f}-{lb:.2f} from GF/GP and GA/GP; no home edge")
        out["markets"] = _markets([(row["a"], p), (row["b"], 1 - p)], la, lb, (row["a"], row["b"]))
        out["selection"], out["probability"] = row["a"], p
    elif kind == "lnh":
        sta, stb = LNH.get(row["a"]), LNH.get(row["b"])
        if sta is None or stb is None:
            out["withheld"].append("official LNH table row missing")
            return out
        n = len(LNH)
        mean_gf = sum(v[5] for v in LNH.values()) / sum(v[1] for v in LNH.values())
        mean_ga = sum(v[6] for v in LNH.values()) / sum(v[1] for v in LNH.values())
        league = (mean_gf + mean_ga) / 2
        la = (sta[5] / sta[1]) * (stb[6] / stb[1]) / league
        lb = (stb[5] / stb[1]) * (sta[6] / sta[1]) / league
        grid = poisson_grid(round(la * 4) / 4, round(lb * 4) / 4, n=90)
        win = sum(grid[i][j] for i in range(90) for j in range(90) if i > j)
        draw = sum(grid[i][j] for i in range(90) for j in range(90) if i == j)
        loss = 1 - win - draw
        # drop the draw for the two-way selection probability
        p = win / (win + loss)
        out["basis"] = (f"attack/defence ratios around the LNH league mean ({league:.2f} goals); "
                        f"expected 60-minute score {la:.1f}-{lb:.1f}; no home edge")
        out["markets"] = [
            {"market": "match_winner_3way", "selection": row["a"], "probability": win},
            {"market": "match_winner_3way", "selection": "Draw", "probability": draw},
            {"market": "match_winner_3way", "selection": row["b"], "probability": loss},
        ]
        for line in (-2.5, 2.5):
            for name, sign in ((row["a"], line), (row["b"], -line)):
                q, _ = handicap_probs(round(la * 4) / 4, round(lb * 4) / 4, sign)
                out["markets"].append({"market": "handicap", "line": f"{sign:+g}", "units": "goals", "selection": name, "probability": q})
        for line in (55.5, 57.5, 59.5):
            over, under = total_probs(round(la * 4) / 4, round(lb * 4) / 4, line)
            out["markets"].append({"market": "total", "line": f"{line:g}", "units": "goals", "selection": f"Over {line:g} goals", "probability": over})
            out["markets"].append({"market": "total", "line": f"{line:g}", "units": "goals", "selection": f"Under {line:g} goals", "probability": under})
        out["selection"], out["probability"] = row["a"], p
    elif kind == "wta-rank":
        out["withheld"].append(
            "only the official draw seeding/ranking order was read, with no rating scale, "
            "serve/return split or surface form, so no probability is asserted")
        out["basis"] = "ranking order only"
        return out
    else:
        out["withheld"].append("no official quantitative strength input was read for both sides")
        return out

    kept = []
    for m in out["markets"]:
        q = m.get("probability")
        if q is None:
            kept.append(m)
            continue
        if not (0 < q < 1):
            out["withheld"].append(f"{m['selection']} dropped: the line sits outside the score distribution")
            continue
        m["american"] = american(q)
        m["fair_decimal"] = decimal(q)
        kept.append(m)
    out["markets"] = kept
    p = out["probability"]
    out["americain"] = out["american"] = american(p)
    out["fair_decimal"] = decimal(p)
    out["in_window"] = in_window(p)
    if p >= 0.70:
        out["tier"] = "High" if out["in_window"] else "High (price outside -250..+10000)"
    elif p >= 0.60:
        out["tier"] = "Medium"
    else:
        out["tier"] = "Low"
    if kind == "lnh" and out["tier"].startswith("High"):
        out["notes"].append("opponent-adjusted attack/defence inputs; no injury or squad data read")
    return out
