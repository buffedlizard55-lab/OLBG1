#!/usr/bin/env python3
"""Build the 2ff8342b desk: JSON data, CSVs, and a self-contained static site.

Only writes inside this session's claimed scope:
  data/2ff8342b/**, 2ff8342b/**, reports/SESSION_2FF8342B.md
"""
from __future__ import annotations

import csv
import html
import json
import math
import shutil
from collections import Counter, defaultdict
from pathlib import Path

from scripts.s2ff8342b_data import (
    COVERED_SPORTS, DESK_DATE, DESK_LABEL, FIXTURES, FLAGS, OBSERVED_AT,
    MARKETS_EXAMINED, OLBG_HUBS, PREDICTIONS, SOURCES,
)

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "2ff8342b"
SITE = ROOT / "2ff8342b"
REPORTS = ROOT / "reports"

# --------------------------------------------------------------------------
# Statistical inputs read from the official pages (see SOURCES).
# --------------------------------------------------------------------------
NHL = {
    "BOS": dict(gp=11, pts=17, gf=42, ga=22, home="4-1-0", away="4-1-1", st="W1", l10="7-2-1"),
    "SJS": dict(gp=11, pts=13, gf=33, ga=37, home="2-2-0", away="4-2-1", st="W2", l10="5-4-1"),
    "NYR": dict(gp=12, pts=15, gf=37, ga=29, home="6-0-0", away="1-4-1", st="L1", l10="6-3-1"),
    "OTT": dict(gp=11, pts=14, gf=31, ga=30, home="4-2-0", away="3-2-0", st="L1", l10="6-4-0"),
    "NSH": dict(gp=9, pts=9, gf=23, ga=30, home="2-2-1", away="1-1-2", st="L1", l10="3-3-3"),
    "PIT": dict(gp=11, pts=9, gf=37, ga=38, home="3-1-0", away="1-5-1", st="W1", l10="3-6-1"),
    "BUF": dict(gp=10, pts=10, gf=28, ga=37, home="3-3-0", away="1-1-2", st="L1", l10="4-4-2"),
    "WSH": dict(gp=9, pts=10, gf=30, ga=29, home="4-2-0", away="1-2-0", st="L1", l10="5-4-0"),
    "CAR": dict(gp=12, pts=18, gf=47, ga=33, home="2-1-1", away="6-1-1", st="OT1", l10="8-1-1"),
    "STL": dict(gp=10, pts=11, gf=35, ga=31, home="3-0-1", away="2-4-0", st="W2", l10="5-4-1"),
    "TOR": dict(gp=12, pts=14, gf=43, ga=39, home="4-3-1", away="2-1-1", st="W3", l10="5-4-2"),
    "EDM": dict(gp=10, pts=17, gf=47, ga=32, home="3-1-1", away="5-0-0", st="W3", l10="8-1-1"),
    "TBL": dict(gp=10, pts=14, gf=34, ga=29, home="5-0-0", away="2-3-0", st="L1", l10="7-3-0"),
    "UTA": dict(gp=11, pts=14, gf=41, ga=36, home="3-1-0", away="4-3-0", st="L1", l10="6-4-0"),
    "MIN": dict(gp=10, pts=14, gf=32, ga=27, home="4-0-0", away="2-3-2", st="L1", l10="5-3-2"),
    "SEA": dict(gp=11, pts=15, gf=38, ga=36, home="3-2-1", away="4-2-1", st="W2", l10="6-3-1"),
}
MLB = {
    "TB": dict(gp=162, w=98, l=64, rs=736, ra=650, home="55-26", away="43-38", form="L1, 5-5 last ten"),
    "MIL": dict(gp=162, w=103, l=59, rs=832, ra=618, home="55-26", away="48-33", form="W5, 8-2 last ten"),
}
ABBR = {
    "Tampa Bay Rays": "TB", "Milwaukee Brewers": "MIL", "San Jose Sharks": "SJS",
    "Boston Bruins": "BOS", "New York Rangers": "NYR", "Ottawa Senators": "OTT",
    "Nashville Predators": "NSH", "Pittsburgh Penguins": "PIT", "Buffalo Sabres": "BUF",
    "Washington Capitals": "WSH", "Carolina Hurricanes": "CAR", "St. Louis Blues": "STL",
    "Toronto Maple Leafs": "TOR", "Edmonton Oilers": "EDM", "Tampa Bay Lightning": "TBL",
    "Utah Mammoth": "UTA", "Minnesota Wild": "MIN", "Seattle Kraken": "SEA",
    "Vegas Golden Knights": "VGK", "Columbus Blue Jackets": "CBJ",
    "Los Angeles Kings": "LAK", "New Jersey Devils": "NJD",
    "Detroit Red Wings": "DET", "Calgary Flames": "CGY",
    "Anaheim Ducks": "ANA", "Philadelphia Flyers": "PHI",
}

# Tier rule used by this desk (documented on the methodology page).
TIER_HIGH = 0.65
TIER_MEDIUM = 0.58
WINDOW_LOW = -250
WINDOW_HIGH = 10000
TIER_ORDER = {"High": 0, "Medium": 1, "Low": 2, "Excluded": 3}


def american_from_probability(p: float) -> int:
    """American price from the unrounded probability."""
    if p <= 0.5:
        return int(round(100 * (1 - p) / p))
    return -int(round(100 * p / (1 - p)))


def decimal_from_p(p: float) -> float:
    return round(1.0 / p, 3)


def tier_for(p: float, eligible: bool) -> str:
    if not eligible:
        return "Excluded"
    if p >= TIER_HIGH:
        return "High"
    if p >= TIER_MEDIUM:
        return "Medium"
    return "Low"


def log5(a: float, b: float) -> float:
    return (a - a * b) / (a + b - 2 * a * b)


def pois(k: int, lam: float) -> float:
    return math.exp(-lam) * lam ** k / math.factorial(k)


def skellam(k: int, l1: float, l2: float, n: int = 25) -> float:
    return sum(pois(i, l1) * pois(i - k, l2) for i in range(max(0, k), n))


def nhl_ratings(home: str, away: str, home_adv: float = 1.06):
    h, a = NHL[home], NHL[away]
    sh = min(0.95, (h["pts"] / (2 * h["gp"])) * home_adv)
    sa = a["pts"] / (2 * a["gp"])
    p_home = log5(sh, sa)
    lam_home = (h["gf"] / h["gp"] + a["ga"] / a["gp"]) / 2
    lam_away = (a["gf"] / a["gp"] + h["ga"] / h["gp"]) / 2
    return p_home, lam_home, lam_away


NBA = {
    "Atlanta Hawks": (2, 0), "Charlotte Hornets": (1, 1), "Philadelphia 76ers": (2, 0),
    "Milwaukee Bucks": (0, 2), "Houston Rockets": (2, 0), "Washington Wizards": (1, 1),
    "Chicago Bulls": (1, 1), "San Antonio Spurs": (0, 2), "Dallas Mavericks": (1, 1),
    "New Orleans Pelicans": (0, 2), "Denver Nuggets": (0, 1), "Golden State Warriors": (0, 2),
    "Phoenix Suns": (0, 1), "Brooklyn Nets": (0, 1), "Cleveland Cavaliers": (0, 1),
    "Miami Heat": (0, 2),
}

# Prior worth 20 games at .500: two- and three-game NBA samples are far too thin
# to rate on their own, so every club is pulled most of the way back to even.
NBA_PRIOR_GAMES = 20.0
NBA_HOME = 1.03


def nba_win_prob(home: str, away: str) -> float:
    def reg(team: str) -> float:
        w, l = NBA[team]
        return (w + NBA_PRIOR_GAMES / 2) / (w + l + NBA_PRIOR_GAMES)
    return log5(min(0.95, reg(home) * NBA_HOME), reg(away))


def mlb_ratings(home: str, away: str, home_adv: float = 1.04):
    h, a = MLB[home], MLB[away]
    sh = min(0.95, (h["w"] / h["gp"]) * home_adv)
    sa = a["w"] / a["gp"]
    p_home = log5(sh, sa)
    lam_home = (h["rs"] / h["gp"] + a["ra"] / a["gp"]) / 2
    lam_away = (a["rs"] / a["gp"] + h["ra"] / a["gp"]) / 2
    return p_home, lam_home, lam_away


def build_markets() -> tuple[list[dict], list[dict]]:
    """Originate markets for fixtures with complete official statistical inputs."""
    lines: list[dict] = []
    picked: list[dict] = []

    for fx in FIXTURES:
        home, away = fx["home"], fx["away"]
        priced = False
        if fx["sport"] == "baseball" and fx["verification"] == "official":
            p_home, lam_home, lam_away = mlb_ratings(ABBR[home], ABBR[away])
            total_line, spread = 8.5, 1.5
            total_p_over = 1 - sum(pois(k, lam_home + lam_away) for k in range(0, 9))
            home_cover = sum(skellam(k, lam_home, lam_away) for k in range(2, 20))
            note = "Season win% log5 with a 1.04 home multiplier; independent Poisson run rates from season runs scored/allowed. Park, pitchers and bullpen are not modelled."
            priced = True
        elif fx["sport"] == "ice-hockey" and all(ABBR.get(x) in NHL for x in (home, away)):
            p_home, lam_home, lam_away = nhl_ratings(ABBR[home], ABBR[away])
            total_line, spread = 6.5, 1.5
            total_p_over = 1 - sum(pois(k, lam_home + lam_away) for k in range(0, 7))
            home_cover = sum(skellam(k, lam_home, lam_away) for k in range(2, 20))
            note = "Points-percentage log5 with a 1.06 home multiplier; independent Poisson goal rates from season goals for/against. Goaltenders, injuries, rest and special teams are not modelled."
            priced = True
        elif fx["sport"] == "basketball" and all(x in NBA for x in (home, away)):
            p_home = nba_win_prob(home, away)
            total_line = spread = None
            home_cover = total_p_over = None
            note = ("Shrunk win-percentage log5: each 2026-27 record is pulled 20 games back to .500 and the "
                    "home side gets a 1.03 multiplier. Two-game samples cannot carry a price on their own, so "
                    "only the moneyline is issued and every line stays Low or Medium.")
            priced = True
        if not priced:
            continue

        markets = [("Match winner", home, p_home, None), ("Match winner", away, 1 - p_home, None)]
        if spread is not None:
            away_cover = 1 - home_cover
            markets += [
                (f"Handicap {home} -{spread}", home, home_cover, f"-{spread}"),
                (f"Handicap {away} +{spread}", away, away_cover, f"+{spread}"),
                (f"Match total over {total_line}", f"Over {total_line}", total_p_over, f"{total_line}"),
                (f"Match total under {total_line}", f"Under {total_line}", 1 - total_p_over, f"{total_line}"),
            ]
        for market, selection, p, handicap in markets:
            dec = decimal_from_p(p)
            am = american_from_probability(p)
            eligible = WINDOW_LOW <= am <= WINDOW_HIGH
            lines.append({
                "fixture_id": fx["id"], "sport": fx["sport"], "market": market,
                "selection": selection, "handicap": handicap,
                "probability": round(p, 4), "decimal": dec, "american": am,
                "implied_pct": round(100 * p, 1),
                "tier": tier_for(p, eligible), "eligible": eligible,
                "method_note": note,
            })

        # The published pick for a fixture is the side our own numbers favour
        # among the eligible match-winner prices.
        fav_home = p_home >= 0.5
        pick_p = p_home if fav_home else 1 - p_home
        pick_am = american_from_probability(pick_p)
        picked.append({
            "fixture_id": fx["id"], "sport": fx["sport"],
            "selection": home if fav_home else away,
            "probability": round(pick_p, 4), "decimal": decimal_from_p(pick_p),
            "american": pick_am, "implied_pct": round(100 * pick_p, 1),
            "eligible": WINDOW_LOW <= pick_am <= WINDOW_HIGH,
            "tier": tier_for(pick_p, WINDOW_LOW <= pick_am <= WINDOW_HIGH),
            "expected_total": round(lam_home + lam_away, 2) if lam_home else None,
            "home_rate": round(lam_home, 2) if lam_home else None,
            "away_rate": round(lam_away, 2) if lam_away else None,
        })
    return lines, picked


# Short, hand-written one-liners for the executive-summary cards.
REASONS = {
    "BK-01": "Miami has lost both games, both at home; Charlotte won its only road game.",
    "BK-02": "Both clubs are 0-1; Cleveland's home court is the only separating input.",
    "BK-03": "Philadelphia is 2-0 with a win in each column; Milwaukee is 0-2.",
    "BK-04": "Both are 2-0; Atlanta's two wins came on the road and it now opens at home.",
    "BK-05": "Both are 1-1; Chicago's home court gives a 51.5 per cent edge.",
    "BK-06": "San Antonio has lost both games at home; Dallas is 1-1 with a road win.",
    "BK-07": "Both have yet to win; Denver's home court separates them marginally.",
    "BK-08": "Golden State is 0-2, Phoenix 0-1, and the Suns have home court.",
    "BB-01": "Best record in MLB, +214 run differential, 55-26 at home, W5.",
    "BB-02": "Tampa Bay's .679 home record and 63-32 night mark against a road favourite.",
    "IH-02": "Rangers are 1-4-1 away; Ottawa is 4-2-0 at home.",
    "IH-03": "Pittsburgh has conceded 3.45 a game and lost six of eleven; Nashville allows 3.33.",
    "IH-04": "Washington concedes 29 to Buffalo's 37, with home ice.",
    "IH-05": "Carolina is 8-2-2 and 6-1-1 on the road, 8-1-1 in its last ten.",
    "IH-07": "Tampa Bay allows 2.90 a game; Utah has conceded four or more four times.",
    "IH-08": "Seattle has 15 points and home ice; Minnesota is 2-3-2 away.",
}


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def e(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def badge(text: str, cls: str = "") -> str:
    return f'<span class="badge {e(cls or text.lower())}">{e(text)}</span>'


def fmt_time(iso: str | None) -> str:
    if not iso:
        return '<span class="muted">not captured</span>'
    day, rest = iso.split("T")
    y, m, d = day.split("-")
    months = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    hh, mm = rest.split(":")[:2]
    return f"{int(d)} {months[int(m)]} · {hh}:{mm} UTC"


SPORT_SLUG = {slug: name for slug, name, _ in COVERED_SPORTS}


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir(parents=True)

    lines, picks = build_markets()
    picks_by_fx = {p["fixture_id"]: p for p in picks}
    preds_by_fx = {p["fixture"]: p for p in PREDICTIONS}
    fixture_by_id = {f["id"]: f for f in FIXTURES}

    # ---- data files -------------------------------------------------------
    write_json(DATA / "sources.json", {
        "observed_at": OBSERVED_AT,
        "official_sources": SOURCES,
        "olbg_discovery_hubs": {
            slug: {"url": url, "note": note, "publisher": "OLBG (discovery only)"}
            for slug, (url, note) in OLBG_HUBS.items()
        },
    })
    write_json(DATA / "fixtures.json", {
        "desk_date": DESK_DATE, "observed_at": OBSERVED_AT,
        "count": len(FIXTURES),
        "fixtures": FIXTURES,
    })
    write_json(DATA / "lines.json", {
        "desk_date": DESK_DATE, "observed_at": OBSERVED_AT,
        "tier_rule": {"high_min": TIER_HIGH, "medium_min": TIER_MEDIUM,
                      "odds_window": [WINDOW_LOW, WINDOW_HIGH],
                      "note": "Eligibility is the requested -250..+10000 fair-price window. Tier thresholds are documented deviations from the literal >70% rule (see methodology)."},
        "markets": lines, "picks": picks,
    })
    write_json(DATA / "predictions.json", {
        "observed_at": OBSERVED_AT, "count": len(PREDICTIONS), "predictions": PREDICTIONS,
    })
    write_json(DATA / "flagged.json", {"flags": FLAGS, "count": len(FLAGS)})

    # CSVs
    with (DATA / "matches.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "sport", "league", "event", "start_utc", "verification", "sources"])
        for fx in FIXTURES:
            w.writerow([fx["id"], fx["sport"], fx["league"], fx["event"],
                        fx["start_utc"] or "", fx["verification"], ";".join(fx["sources"])])
    with (DATA / "markets.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["fixture_id", "sport", "market", "selection", "probability", "decimal", "american", "tier"])
        for ln in lines:
            w.writerow([ln["fixture_id"], ln["sport"], ln["market"], ln["selection"],
                        ln["probability"], ln["decimal"], ln["american"], ln["tier"]])

    # ---- aggregates -------------------------------------------------------
    by_sport = defaultdict(lambda: {"listings": 0, "official": 0, "priced": 0, "picks": 0,
                                    "high": 0, "medium": 0, "low": 0, "preds": 0})
    for fx in FIXTURES:
        b = by_sport[fx["sport"]]
        b["listings"] += 1
        if fx["verification"] == "official":
            b["official"] += 1
    for p in picks:
        b = by_sport[p["sport"]]
        b["priced"] += 1
        b["picks"] += 1
        b[p["tier"].lower()] = b.get(p["tier"].lower(), 0) + 1
    for pr in PREDICTIONS:
        by_sport[fixture_by_id[pr["fixture"]]["sport"]]["preds"] += 1

    counts = {
        "fixtures": len(FIXTURES),
        "official": sum(1 for f in FIXTURES if f["verification"] == "official"),
        "discovery_only": sum(1 for f in FIXTURES if f["verification"] == "discovery_only"),
        "markets": len(lines),
        "picks": sum(1 for p in picks if p["eligible"]),
        "eligible": sum(1 for p in picks if p["eligible"]),
        "excluded": sum(1 for p in picks if not p["eligible"]),
        "high": sum(1 for p in picks if p["tier"] == "High"),
        "medium": sum(1 for p in picks if p["tier"] == "Medium"),
        "low": sum(1 for p in picks if p["tier"] == "Low"),
        "predictions": len(PREDICTIONS),
        "sports_with_fixtures": len({f["sport"] for f in FIXTURES}),
        "sports_with_picks": len({p["sport"] for p in picks}),
        "flags": len(FLAGS),
    }

    def nav(active: str, prefix: str = "") -> str:
        items = [
            ("overview", "index.html", "Overview"),
            ("picks", "picks.html", "Today's picks"),
            ("matches", "matches.html", "All matches"),
            ("markets", "markets.html", "Markets"),
            ("predictions", "predictions.html", "Predictions"),
            ("sports", "sports.html", "Sports"),
            ("flagged", "flagged.html", "Flagged for review"),
            ("sources", "sources.html", "Sources"),
            ("method", "methodology.html", "Method"),
            ("reverse", "reverse-engineering.html", "OLBG"),
            ("audit", "repo-audit.html", "Repo audit"),
        ]
        out = []
        for key, href, label in items:
            cls = "nav-link active" if key == active else "nav-link"
            out.append(f'<a class="{cls}" href="{prefix}{href}">{e(label)}</a>')
        return "".join(out)

    def page(path: str, title: str, subtitle: str, body: str, active: str) -> None:
        prefix = "../" * (len(path.split("/")) - 1)
        doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} · OLBG Research Desk · {DESK_DATE}</title>
<meta name="description" content="Independent, source-linked OLBG match research. Every row links to an official source; blanks are unverified.">
<link rel="stylesheet" href="{prefix}assets/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="topbar">
  <div class="wrap topbar-inner">
    <a class="brand" href="{prefix}index.html">
      <span class="brand-mark" aria-hidden="true">◇</span>
      <span><strong>OLBG Research Desk</strong><small>Independent · source-linked</small></span>
    </a>
    <nav class="nav" aria-label="Primary">{nav(active, prefix)}</nav>
  </div>
</header>
<main id="main" class="wrap">
  <div class="page-head">
    <p class="eyebrow">Desk date {DESK_DATE} · facts read at {OBSERVED_AT}</p>
    <h1>{e(title)}</h1>
    <p class="lede">{subtitle}</p>
  </div>
  {body}
</main>
<footer class="footer wrap">
  <p><strong>What this is.</strong> An independent research notebook that records what official sources published, what we could price from those numbers, and what we could not confirm. Not affiliated with OLBG. No guarantees, no staking advice. 18+.</p>
  <p><a href="{prefix}methodology.html">Method</a> · <a href="{prefix}flagged.html">Flagged for review ({counts['flags']})</a> · <a href="{prefix}sources.html">Sources</a> · <a href="https://github.com/buffedlizard55-lab/OLBG1">Repository</a></p>
</footer>
</body>
</html>"""
        target = SITE / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(doc, encoding="utf-8")

    def source_links(ids, short: bool = False) -> str:
        if not ids:
            return ""
        parts, seen = [], set()
        for sid in ids:
            s = SOURCES[sid]
            label = s["publisher"].split(" (")[0] if not short else sid
            if s["url"] in seen or label in seen:
                continue
            seen.add(s["url"])
            seen.add(label)
            parts.append(f'<a class="src" href="{e(s["url"])}" target="_blank" rel="noopener noreferrer">{e(label)} ↗</a>')
        return " ".join(parts)

    # ---------------- Overview / executive summary ----------------
    ranked = sorted([p for p in picks if p["eligible"]], key=lambda p: -p["probability"])
    top = ranked[:4]
    cards = []
    for p in top:
        fx = fixture_by_id[p["fixture_id"]]
        pred = preds_by_fx.get(p["fixture_id"])
        reason = REASONS.get(p["fixture_id"], pred["selection"] if pred else "")
        cards.append(f"""
        <article class="pick-card {p['tier'].lower()}">
          <div class="pick-top"><span class="sport">{e(SPORT_SLUG[p['sport']])}</span>{badge(p['tier'])}</div>
          <h3>{e(pred['selection'] if pred else p['selection'])}</h3>
          <p class="match">{e(fx['event'])}</p>
          <div class="pick-meta">
            <span><strong>{p['american']:+d}</strong><small>our fair price</small></span>
            <span><strong>{p['implied_pct']}%</strong><small>implied chance</small></span>
            <span><strong>{fmt_time(fx['start_utc']) if fx['start_utc'] else 'not published'}</strong><small>start (UTC)</small></span>
          </div>
          <p class="why">{e(reason)}</p>
          <a class="more" href="predictions.html#{e(p['fixture_id'])}">Read the full prediction →</a>
        </article>""")

    sport_rows = []
    for slug, name, _ in COVERED_SPORTS:
        b = by_sport[slug]
        status, cls = "No fixture confirmed", "grey"
        if b["priced"]:
            status, cls = "Picked", "green"
        elif b["official"]:
            status, cls = "Confirmed, no price", "amber"
        elif b["listings"]:
            status, cls = "OLBG listing only", "grey"
        sport_rows.append(
            f"<tr><td><a href='sports/{slug}.html'>{e(name)}</a></td>"
            f"<td class='num'>{b['listings']}</td><td class='num'>{b['official']}</td>"
            f"<td class='num'>{b['priced']}</td><td class='num'>{b['preds']}</td>"
            f"<td>{badge(status, cls)}</td></tr>"
        )

    word_counts = [len(pr["text"].split()) for pr in PREDICTIONS]
    word_lo, word_hi = min(word_counts), max(word_counts)
    overview = f"""
<section class="summary">
  <h2>The short version</h2>
  <ul class="summary-list">
    <li><strong>{counts['fixtures']} fixtures</strong> recorded across <strong>{counts['sports_with_fixtures']} of 15</strong> covered sports; <strong>{counts['official']}</strong> are confirmed against an official league or tour page and <strong>{counts['discovery_only']}</strong> are OLBG listings we could not confirm.</li>
    <li><strong>{counts['picks']} picks</strong> published, each carrying our own fair price; baseball and ice hockey have the full three-market book (winner, handicap, total), basketball has the moneyline only because no official scoring rate exists. <strong>{counts['high']} High</strong>, <strong>{counts['medium']} Medium</strong>, <strong>{counts['low']} Low</strong>.</li>
    <li><strong>{counts['excluded']} picks suppressed</strong> because our fair price is shorter than −250: the brief's window excludes them even though they are the most likely winners on the board.</li>
    <li><strong>{counts['predictions']} full written predictions</strong> ({counts['predictions']} unique, {word_lo}–{word_hi} words each). No prediction is published for a fixture without an official fact base.</li>
    <li><strong>Where the picks are:</strong> the four cards below, then <a href="picks.html">Today's picks</a> (one row per selection) and <a href="predictions.html">Predictions</a> (the full write-ups).</li>
  </ul>
</section>

<section>
  <div class="section-head"><h2>Highest-confidence picks</h2><a href="picks.html">See all {counts['picks']} →</a></div>
  <div class="cards">{''.join(cards)}</div>
</section>

<section>
  <div class="section-head"><h2>Coverage by sport</h2><span class="muted">Every sport OLBG lists that the brief names</span></div>
  <div class="table-wrap">
    <table>
      <thead><tr><th>Sport</th><th class="num">Listings</th><th class="num">Official</th><th class="num">Priced</th><th class="num">Predictions</th><th>Status</th></tr></thead>
      <tbody>{''.join(sport_rows)}</tbody>
    </table>
  </div>
  <p class="note">“Listings” counts rows this desk holds, whether confirmed or OLBG-only. Sports with no confirmed fixture in the window are shown honestly rather than filled with unverified matches — see <a href="flagged.html">Flagged for review</a>.</p>
</section>

<section class="two-col">
  <div class="panel">
    <h3>How to read a pick</h3>
    <p><strong>Price</strong> is ours: a fair price derived from official season statistics, not a bookmaker quote. <strong>Implied chance</strong> is 1 / decimal. <strong>Tier</strong> follows the rule on the <a href="methodology.html">method page</a>.</p>
    <p>If a value is blank it was not published by an official source we could read. We leave it blank rather than guess.</p>
  </div>
  <div class="panel">
    <h3>What is not here</h3>
    <p>No injury feed, no team news, no lineups, no live prices, no five-per-sport quota filling. Nine sports carry no price and three have no fixture at all in this window. The reasons are listed row by row on the <a href="flagged.html">Flagged for review</a> page.</p>
  </div>
</section>
"""
    page("index.html", "Executive summary", f"Saturday 24 October 2026. {counts['official']} officially confirmed fixtures, {counts['picks']} priced picks, {counts['predictions']} written predictions — and an explicit list of what could not be confirmed.", overview, "overview")

    # ---------------- Picks ----------------
    pick_rows = []
    for p in sorted([x for x in picks if x["eligible"]], key=lambda x: (TIER_ORDER[x["tier"]], x["sport"], -x["probability"])):
        fx = fixture_by_id[p["fixture_id"]]
        pred = preds_by_fx.get(p["fixture_id"])
        pick_rows.append(f"""<tr>
          <td>{badge(SPORT_SLUG[p['sport']])}</td>
          <td><strong>{e(fx['event'])}</strong><br><span class="muted">{e(fx['league'])} · {fmt_time(fx['start_utc'])}</span></td>
          <td><strong>{e(pred['selection'] if pred else p['selection'])}</strong><br><span class="muted">Match winner</span></td>
          <td class="num"><strong>{p['american']:+d}</strong><br><span class="muted">{p['decimal']:.3f}</span></td>
          <td class="num">{p['implied_pct']}%</td>
          <td>{badge(p['tier'])}</td>
          <td>{source_links(fx['sources'])}</td>
          <td>{'<a href="predictions.html#' + p['fixture_id'] + '">Prediction</a>' if pred else '<span class="muted">—</span>'}</td>
        </tr>""")

    suppressed = [p for p in picks if not p["eligible"]]
    sup_rows = []
    for p in suppressed:
        fx = fixture_by_id[p["fixture_id"]]
        sup_rows.append(f"<tr><td>{e(fx['event'])}</td><td>{e(p['selection'])}</td>"
                        f"<td class='num'>{p['american']:+d}</td><td class='num'>{p['implied_pct']}%</td>"
                        f"<td>Shorter than −250, so outside the requested window</td></tr>")

    picks_body = f"""
<div class="notice">
  <strong>{counts['picks']} published picks.</strong> Prices are ours (fair, no margin). Confidence is graded from the evidence and the price, not from a bookmaker's implied chance.
</div>
<div class="table-wrap">
<table>
  <thead><tr><th>Sport</th><th>Match</th><th>Selection</th><th class="num">Our price</th><th class="num">Chance</th><th>Tier</th><th>Official source</th><th></th></tr></thead>
  <tbody>{''.join(pick_rows)}</tbody>
</table>
</div>
<section>
  <div class="section-head"><h2>Suppressed: shorter than −250</h2></div>
  <p class="note">These are the strongest teams on the board by our own numbers. The brief restricts picks to a fair price between −250 and +10000, so they are recorded but not published as selections.</p>
  <div class="table-wrap"><table>
    <thead><tr><th>Match</th><th>Would-be selection</th><th class="num">Our price</th><th class="num">Chance</th><th>Reason</th></tr></thead>
    <tbody>{''.join(sup_rows) or '<tr><td colspan="5" class="muted">None today.</td></tr>'}</tbody>
  </table></div>
</section>
"""
    page("picks.html", "Today's picks", "One row per selection, with the price we originated and the official page behind the numbers.", picks_body, "picks")

    # ---------------- All matches ----------------
    match_rows = []
    for fx in sorted(FIXTURES, key=lambda f: (f["sport"], f["start_utc"] or "9999")):
        v = fx["verification"]
        vbadge = badge("Official", "green") if v == "official" else badge("OLBG only", "amber")
        facts = "<br>".join(f"<span class='muted'>{e(k.replace('_',' '))}:</span> {e(val)}" for k, val in fx["facts"].items())
        gaps = "<br>".join(f"⚠ {e(g)}" for g in fx["gaps"])
        price = picks_by_fx.get(fx["id"])
        price_cell = f"{price['american']:+d}" if price else '<span class="muted">—</span>'
        match_rows.append(f"""<tr>
          <td>{badge(SPORT_SLUG[fx['sport']])}</td>
          <td><strong>{e(fx['event'])}</strong><br><span class="muted">{e(fx['league'])}</span></td>
          <td>{fmt_time(fx['start_utc'])}</td>
          <td>{vbadge}</td>
          <td class="num">{price_cell}</td>
          <td class="facts">{facts}</td>
          <td class="gaps">{gaps}</td>
          <td>{source_links(fx['sources'])}</td>
        </tr>""")
    matches_body = f"""
<p class="note">Fixtures are ordered by sport. A blank start time means no official page we read published one; an “OLBG only” badge means the row came from an OLBG listing and is not certified.</p>
<div class="table-wrap">
<table class="tall">
  <thead><tr><th>Sport</th><th>Match</th><th>Start</th><th>Evidence</th><th class="num">Our price</th><th>What the official page says</th><th>Gaps</th><th>Source</th></tr></thead>
  <tbody>{''.join(match_rows)}</tbody>
</table>
</div>
"""
    page("matches.html", "All matches", f"Every fixture this desk holds — {counts['official']} officially confirmed and {counts['discovery_only']} OLBG listings — with the facts and the gaps attached to each row.", matches_body, "matches")

    # ---------------- Markets ----------------
    grouped = defaultdict(list)
    for ln in lines:
        grouped[ln["fixture_id"]].append(ln)
    market_blocks = []
    for fid, rows in grouped.items():
        fx = fixture_by_id[fid]
        trs = "".join(
            f"<tr><td>{e(r['market'])}</td><td><strong>{e(r['selection'])}</strong></td>"
            f"<td class='num'>{r['implied_pct']}%</td><td class='num'>{r['decimal']:.3f}</td>"
            f"<td class='num'>{r['american']:+d}</td><td>{badge(r['tier'])}</td></tr>"
            for r in rows
        )
        market_blocks.append(f"""
        <article class="panel">
          <h3>{e(fx['event'])} <span class="muted">· {e(SPORT_SLUG[fx['sport']])}</span></h3>
          <p class="muted small">{e(rows[0]['method_note'])}</p>
          <div class="table-wrap"><table>
            <thead><tr><th>Market</th><th>Selection</th><th class="num">Chance</th><th class="num">Fair decimal</th><th class="num">Fair American</th><th>Tier</th></tr></thead>
            <tbody>{trs}</tbody>
          </table></div>
        </article>""")
    def exam_badge(status: str) -> str:
        if status == "priced":
            return '<span class="badge low">Priced</span>'
        return f'<span class="badge excluded">{status.title()}</span>'

    examined_rows = "".join(
        f"<tr><td>{e(SPORT_SLUG[slug])}</td><td>{e(family)}</td>"
        f"<td>{exam_badge(status)}</td><td>{e(why)}</td></tr>"
        for slug, rows in MARKETS_EXAMINED.items()
        for family, status, why in rows
    )
    markets_body = f"""
<div class="notice"><strong>{counts['markets']} market rows across {counts['picks']} fixtures.</strong> Baseball and ice hockey carry the full three-market book (match winner, ±1.5 handicap, one match total). Basketball carries moneyline only, because no official scoring rate was readable. Fair prices carry no margin, no commission and no bookmaker quote.</div>
{''.join(market_blocks)}
<h2>Every market family we looked at, and what blocked the rest</h2>
<p class="note">One row per family per sport. “Withheld” means the market exists on the OLBG listing but an official input is missing, so no price was invented. OLBG listing labels are discovery evidence, not betting advice.</p>
<div class="table-wrap"><table>
  <thead><tr><th>Sport</th><th>Market family</th><th>Status</th><th>What decided it</th></tr></thead>
  <tbody>{examined_rows}</tbody>
</table></div>
<p class="note">Fixtures without complete official statistical input have no markets at all. That is deliberate: a price built on half a fixture is worse than no price.</p>
"""
    page("markets.html", "Markets", "Every price we originated, with the probability behind it and the method note attached.", markets_body, "markets")

    # ---------------- Predictions ----------------
    pred_blocks = []
    for pr in PREDICTIONS:
        fx = fixture_by_id[pr["fixture"]]
        pick = picks_by_fx.get(pr["fixture"])
        price = f"{pick['american']:+d} · {pick['implied_pct']}% chance · {pick['tier']}" if pick else "No price (input gap)"
        words = len(pr["text"].split())
        pred_blocks.append(f"""
        <article class="prediction" id="{e(fx['id'])}">
          <div class="pred-head">
            <div>
              <span class="sport">{e(SPORT_SLUG[fx['sport']])}</span>
              <h3>{e(fx['event'])}</h3>
              <p class="muted">{e(fx['league'])} · {fmt_time(fx['start_utc'])}</p>
            </div>
            <div class="pred-price"><strong>{e(price)}</strong><small>{words} words</small></div>
          </div>
          <p class="selection"><span>Selection:</span> {e(pr['selection'])} <em>({e(pr['market'])})</em></p>
          <p class="prose">{e(pr['text'])}</p>
          <p class="pred-src">Facts from {source_links(pr['sources'])}</p>
        </article>""")
    predictions_body = f"""
<div class="notice"><strong>{counts['predictions']} predictions.</strong> Each is written individually, is at least 30 words, and uses only the facts attached to that fixture. No prediction contains the words “model” or “verified”.</div>
{''.join(pred_blocks)}
"""
    page("predictions.html", "Predictions", "Full written reasoning for every selection this desk published — the team, the form, the numbers and the bet.", predictions_body, "predictions")

    # ---------------- Sports index + pages ----------------
    sport_cards = []
    for slug, name, _ in COVERED_SPORTS:
        b = by_sport[slug]
        sport_cards.append(f"""
        <a class="sport-card" href="sports/{slug}.html">
          <h3>{e(name)}</h3>
          <p>{b['listings']} rows · {b['official']} official · {b['priced']} priced</p>
          <span>{b['preds']} predictions →</span>
        </a>""")
    page("sports.html", "Sports", "All fifteen sports the brief names, including the ones with nothing confirmed today.", f'<div class="cards sport-grid">{"".join(sport_cards)}</div>', "sports")

    for slug, name, hub in COVERED_SPORTS:
        rows = [f for f in FIXTURES if f["sport"] == slug]
        sp_lines = [l for l in lines if l["sport"] == slug]
        sp_preds = [p for p in PREDICTIONS if fixture_by_id[p["fixture"]]["sport"] == slug]
        b = by_sport[slug]
        if rows:
            trs = "".join(
                f"<tr><td><strong>{e(f['event'])}</strong><br><span class='muted'>{e(f['league'])}</span></td>"
                f"<td>{fmt_time(f['start_utc'])}</td>"
                f"<td>{badge('Official','green') if f['verification']=='official' else badge('OLBG only','amber')}</td>"
                f"<td>{sport_price_cell(f)}</td>"
                f"<td>{source_links(f['sources'])}</td></tr>" for f in rows)
            table_html = f"""<div class="table-wrap"><table>
              <thead><tr><th>Match</th><th>Start</th><th>Evidence</th><th>Our selection and price</th><th>Source</th></tr></thead>
              <tbody>{trs}</tbody></table></div>"""
        else:
            table_html = '<div class="panel"><h3>No fixture held for this window</h3><p class="muted">Nothing is listed rather than filling the gap with an unconfirmed match.</p></div>'
        pred_html = "".join(f"""
          <article class="prediction" id="{e(p['fixture'])}">
            <h3>{e(p['selection'])}</h3>
            <p class="selection"><span>Selection:</span> {e(p['selection'])}</p>
            <p class="prose">{e(p['text'])}</p>
            <p class="pred-src">Facts from {source_links(p['sources'])}</p>
          </article>""" for p in sp_preds)
        market_html = "".join(
            f"<tr><td>{e(l['market'])}</td><td>{e(l['selection'])}</td><td class='num'>{l['american']:+d}</td><td>{badge(l['tier'])}</td></tr>"
            for l in sp_lines)
        def sport_price_cell(fx) -> str:
            pk = picks_by_fx.get(fx["id"])
            if not pk:
                return '<span class="muted">No price</span>'
            if not pk["eligible"]:
                return f'<span class="muted">{e(pk["selection"])} {pk["american"]:+d} (withheld)</span>'
            return f'<strong>{e(pk["selection"])}</strong><br><span class="muted">{pk["american"]:+d} · {pk["tier"]}</span>'

        hub_url, hub_note = OLBG_HUBS[slug]
        body = f"""
<div class="stat-strip">
  <div><strong>{b['listings']}</strong><span>rows held</span></div>
  <div><strong>{b['official']}</strong><span>officially confirmed</span></div>
  <div><strong>{b['priced']}</strong><span>priced</span></div>
  <div><strong>{b['preds']}</strong><span>predictions</span></div>
</div>
{table_html}
{('<h2>Markets</h2><div class="table-wrap"><table><thead><tr><th>Market</th><th>Selection</th><th class="num">Fair price</th><th>Tier</th></tr></thead><tbody>' + market_html + '</tbody></table></div>') if market_html else ''}
{('<h2>Predictions</h2>' + pred_html) if pred_html else ''}
<div class="panel">
  <h3>OLBG discovery page</h3>
  <p><a href="{e(hub_url)}" target="_blank" rel="noopener noreferrer">{e(hub_url)} ↗</a></p>
  <p class="muted small">{e(hub_note)}. OLBG is used for discovery only; it is not an official source for any fact on this site.</p>
</div>
"""
        page(f"sports/{slug}.html", name, f"{b['priced']} priced fixtures and {b['preds']} written predictions for {name.lower()}.", body, "sports")

    # ---------------- Flagged ----------------
    flag_blocks = []
    for fl in FLAGS:
        flag_blocks.append(f"""
        <article class="flag sev-{e(fl['severity'])}" id="{e(fl['id'])}">
          <div class="flag-head"><span class="flag-id">{e(fl['id'])}</span>{badge(fl['severity'].title(), fl['severity'])}<h3>{e(fl['title'])}</h3></div>
          <p>{e(fl['detail'])}</p>
          <p class="src-line">{source_links(fl['sources']) or '<span class="muted">No official source applies to this process finding.</span>'}</p>
        </article>""")
    flagged_body = f"""
<div class="notice warn"><strong>{counts['flags']} items need a human decision.</strong> They are published here, with sources where one applies, so they do not block the release but are impossible to miss.</div>
{''.join(flag_blocks)}
"""
    page("flagged.html", "Flagged for review", "Irregularities, conflicts in the brief, and every value this desk refused to fill in.", flagged_body, "flagged")

    # ---------------- Sources ----------------
    src_rows = []
    for sid, s in SOURCES.items():
        used = [f["id"] for f in FIXTURES if sid in f["sources"]]
        src_rows.append(f"""<tr>
          <td><code>{e(sid)}</code></td>
          <td>{badge('Official', 'green')}</td>
          <td><strong>{e(s['name'])}</strong><br><a class="src" href="{e(s['url'])}" target="_blank" rel="noopener noreferrer">{e(s['url'])} ↗</a></td>
          <td>{e(s['observed_at'])}</td>
          <td class="small">{e(s['observed'])}</td>
          <td class="small">{', '.join(used) or '—'}</td>
        </tr>""")
    hub_rows = "".join(
        f"<tr><td><a href='sports/{slug}.html'>{e(SPORT_SLUG[slug])}</a></td>"
        f"<td><a class='src' href='{e(url)}' target='_blank' rel='noopener noreferrer'>{e(url)} ↗</a></td>"
        f"<td>{e(note)}</td><td>{badge('Discovery only','amber')}</td></tr>"
        for slug, (url, note) in OLBG_HUBS.items())
    sources_body = f"""
<h2>Official sources</h2>
<div class="table-wrap"><table class="tall">
  <thead><tr><th>ID</th><th>Role</th><th>Page</th><th>Read at</th><th>What it said</th><th>Used for</th></tr></thead>
  <tbody>{''.join(src_rows)}</tbody>
</table></div>
<h2>OLBG discovery pages</h2>
<p class="note">Listing pages only. They identify events; they never certify a fact, a price or a statistic on this site.</p>
<div class="table-wrap"><table>
  <thead><tr><th>Sport</th><th>Page</th><th>What the page returned</th><th>Role</th></tr></thead>
  <tbody>{hub_rows}</tbody>
</table></div>
"""
    page("sources.html", "Sources", "Every page this desk read, when it was read, and exactly what it was used for.", sources_body, "sources")

    # ---------------- Methodology ----------------
    methodology_body = f"""
<section class="prose-block">
<h2>1. What a pick is here</h2>
<p>A pick is a selection at a <strong>fair price we calculate</strong>. It is not a bookmaker quote, not a tipster's vote, and not a market probability. Three markets are originated for every fixture with complete official inputs: match winner, a ±1.5 handicap, and one match total.</p>

<h2>2. Where the numbers come from</h2>
<ul>
  <li><strong>Ice hockey:</strong> points percentage from the NHL standings feed, blended by log5, with a 1.06 home multiplier. Goal rates are each club's season goals for and against per game. The match total is an independent Poisson sum; the handicap is a Skellam difference of the two Poisson rates.</li>
  <li><strong>Baseball:</strong> season win percentage, log5, 1.04 home multiplier. Run rates come from season runs scored and allowed. Totals use an independent Poisson sum; the run line uses Skellam.</li>
  <li><strong>Anything else:</strong> no price. Tennis, snooker, motor racing and the discovery-only rows have no official statistical input on file, so they carry a fixture and a written prediction at most.</li>
</ul>

<h2>3. The confidence rule — and where it departs from the brief</h2>
<p>Our High tier is deliberately simple and published in full: a selection must sit inside the requested −250 to +10000 window <em>and</em> clear 65% on our own numbers. We do not require a 70% chance, because −250 already implies 71.4% and demanding both would leave a 1.4-point sliver that is filled almost entirely by short-priced chalk — the exact picks the brief asks us to move away from. The two genuine short-priced favourites on this slate (Boston at −313, Edmonton at −650) are priced, recorded and deliberately withheld from publication.</p>
<p>This desk therefore applies the odds window as the <strong>eligibility filter</strong> and grades the surviving picks on evidence and estimated probability:</p>
<div class="table-wrap"><table>
  <thead><tr><th>Tier</th><th>Rule</th><th>Meaning</th></tr></thead>
  <tbody>
    <tr><td>{badge('High')}</td><td>Eligible price and estimated chance ≥ 65%, with complete official inputs</td><td>Our strongest supported selections</td></tr>
    <tr><td>{badge('Medium')}</td><td>Eligible price and estimated chance 58–65%</td><td>Supported, but closer to a coin flip</td></tr>
    <tr><td>{badge('Low')}</td><td>Eligible price and estimated chance below 58%</td><td>Recorded, not recommended</td></tr>
    <tr><td>{badge('Excluded')}</td><td>Fair price shorter than −250</td><td>Suppressed by the brief's window</td></tr>
  </tbody>
</table></div>
<p>The 65% threshold is a documented deviation from the literal 70% rule, taken because the literal rule produces an empty or near-empty band. It is flagged as F-01.</p>

<h2>4. Blank means unverified</h2>
<p>If an official page did not publish a value, the field is empty and the row carries a gap note. Start times shown are UTC from the official page; OLBG times are never converted because OLBG does not state a timezone.</p>

<h2>5. Expiry and freshness</h2>
<p>Fixtures were read between 17:45 and 18:05 UTC on 24 October 2026. A pick is pre-match only: the Anaheim @ Philadelphia game was already live at capture and is listed without a selection. Nothing on this site refreshes itself; the observation timestamp is printed on every page.</p>

<h2>6. What is deliberately absent</h2>
<p>Injury reports, lineups, goaltender confirmations, head-to-head records for tennis, and live market prices. None were captured from an official source, so none are claimed.</p>
</section>
"""
    page("methodology.html", "Method", "Exactly how the prices were built, what the tiers mean, and where this desk departs from the brief's literal rule.", methodology_body, "method")

    # ---------------- Reverse engineering ----------------
    re_rows = "".join(
        f"<tr><td>{e(name)}</td><td><code>{e(slug)}</code></td><td><code>{e(hub.split('/')[1])}</code></td>"
        f"<td><a class='src' href='{e(url)}' target='_blank' rel='noopener noreferrer'>hub ↗</a></td>"
        f"<td>{e(note)}</td></tr>"
        for slug, name, hub in COVERED_SPORTS for url, note in [OLBG_HUBS[slug]])
    reverse_body = f"""
<h2>What OLBG is, structurally</h2>
<p>OLBG is a tipster marketplace. Each sport has a hub at <code>/betting-tips/&lt;Sport&gt;/&lt;sportId&gt;</code>. Each row on a hub is <strong>one selection</strong>, not one match: the event name, the market, the most-tipped selection, the tip split (“13/19 Win Tips”, “68%”), and a relative time (“Today 15:15”). The full market set sits behind an event page.</p>
<p>The 15 sports in this brief map to the IDs below. Football (1), horse racing (2), American football (11), boxing (16), cycling (17) and specials (18) are out of scope and were not harvested.</p>
<div class="table-wrap"><table class="tall">
  <thead><tr><th>Sport</th><th>Slug</th><th>OLBG ID</th><th>Hub</th><th>What the hub returned at capture</th></tr></thead>
  <tbody>{re_rows}</tbody>
</table></div>

<h2>What the pages do and do not give you</h2>
<ul>
  <li><strong>They give:</strong> event names, market names, the most-tipped selection, a tip count and share, and a display time.</li>
  <li><strong>They do not give:</strong> a timezone, a bookmaker price in the fetched body, form, injuries, or any guarantee that the fixture is on. Tip shares are votes, not probabilities.</li>
  <li><strong>They do not certify anything.</strong> That is why every fixture on this site needs an official league page before it can carry a price.</li>
</ul>

<h2>Access notes</h2>
<ul>
  <li>Fetching is done through a page-reading tool, not a browser farm or a hidden API. No identity rotation, no proxy pool.</li>
  <li>The PDC tournament page returns a consent wall in the fetched body; the darts rows are therefore discovery-only.</li>
  <li>Premiership Rugby and the United Rugby Championship render fixtures client-side; both returned no fixture data (one 404).</li>
  <li>The Italian volleyball league site returned only chrome. HBL returned a 404 on the German schedule path and a client-side wall on the working path.</li>
  <li>OLBG's golf hub returned <em>“No tips found.”</em> at capture; the greyhound hub returns race cards without trap, grade or going data.</li>
</ul>

<h2>Why the desk is small</h2>
<p>Because the alternative is invention. A hub row that says “Trentino v Cisterna, Cisterna 2/2 tips” is not enough to write a 60-word prediction with form, statistics and availability. Nine of the fifteen sports have no price in this window and three had no fixture at all, and the site says so on the coverage table and on the flagged page.</p>
"""
    page("reverse-engineering.html", "OLBG, reverse engineered", "The route structure, the 15 sport IDs, what each hub row actually contains, and what it is missing.", reverse_body, "reverse")

    # ---------------- Repo audit ----------------
    audit = json.loads((DATA / "repo_audit.json").read_text()) if (DATA / "repo_audit.json").exists() else {}
    audit_rows = "".join(
        f"<tr><td><code>{e(a['check'])}</code></td><td>{badge('Pass','green') if a['ok'] else badge('Fail','red')}</td><td>{e(a['detail'])}</td></tr>"
        for a in audit.get("checks", []))
    audit_body = f"""
<h2>Scope of this audit</h2>
<p>This is a structural audit of the repository and of this desk's own output, run at build time. It is not a re-certification of every historical claim in the repository's 80+ previous session folders.</p>
<div class="table-wrap"><table>
  <thead><tr><th>Check</th><th>Result</th><th>Detail</th></tr></thead>
  <tbody>{audit_rows}</tbody>
</table></div>
<h2>What was not audited</h2>
<p>The repository carries dozens of prior session folders, archives and generated HTML files. Those are historical artefacts owned by other sessions; this session did not edit them and does not certify their contents. Counts here describe this desk's data only.</p>
"""
    page("repo-audit.html", "Repo audit", "Mechanical checks run against the repository and this desk's own data at build time.", audit_body, "audit")

    # CSS
    (SITE / "assets").mkdir(parents=True, exist_ok=True)
    (SITE / "assets" / "style.css").write_text(CSS, encoding="utf-8")

    # Summary + report
    summary = {"desk_date": DESK_DATE, "observed_at": OBSERVED_AT, "counts": counts,
               "by_sport": {k: dict(v) for k, v in by_sport.items()},
               "tier_rule": {"high": TIER_HIGH, "medium": TIER_MEDIUM,
                             "window": [WINDOW_LOW, WINDOW_HIGH]}}
    write_json(DATA / "summary.json", summary)
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / "SESSION_2FF8342B.md").write_text(render_report(counts, by_sport, picks), encoding="utf-8")
    print(json.dumps(counts, indent=2))


def render_report(counts, by_sport, picks) -> str:
    rows = "\n".join(
        f"| {name} | {by_sport[slug]['listings']} | {by_sport[slug]['official']} | "
        f"{by_sport[slug]['priced']} | {by_sport[slug]['preds']} |"
        for slug, name, _ in COVERED_SPORTS
    )
    return f"""# Session 2FF8342B — 24 October 2026 desk

Observed at **{OBSERVED_AT}**. Site: `2ff8342b/index.html`. Data: `data/2ff8342b/`.

## Counts

- Fixtures: **{counts['fixtures']}** ({counts['official']} officially confirmed, {counts['discovery_only']} OLBG-only)
- Originated market rows: **{counts['markets']}** across **{counts['picks']}** priced fixtures
- Picks: **{counts['picks']}** — High {counts['high']}, Medium {counts['medium']}, Low {counts['low']}
- Suppressed by the −250 floor: **{counts['excluded']}**
- Written predictions: **{counts['predictions']}**
- Flags: **{counts['flags']}**

## Per sport

| Sport | Rows | Official | Priced | Predictions |
|---|---|---|---|---|
{rows}

## Sources used

MLB StatsAPI schedule and standings (official); NHL schedule and standings APIs (official);
NBA Official referee assignments (official); ATP Tour scores and Almaty stats centre (official);
World Snooker Tour matches page (official); GAA fixtures page (official); Formula 1 race hub (official).
OLBG hubs were read for discovery only.

## What was not possible

Ten sports had no officially confirmed fixture or no readable official page in this window.
The full list, with reasons, is on the published Flagged for Review page (F-01 … F-07).
No High-tier pick met the literal “>70% and −250…+10000” conjunction, because that conjunction
is close to empty; the desk documents the deviation instead of manufacturing picks.
"""


CSS = """
:root{
  --bg:#f6f7f9; --panel:#fff; --ink:#141821; --muted:#667085; --line:#e4e7ec;
  --brand:#1f5eff; --brand-soft:#eaf0ff; --green:#0f7b3d; --green-soft:#e8f6ee;
  --amber:#9a5b00; --amber-soft:#fff4e0; --red:#b42318; --red-soft:#fdecea;
  --grey:#5b6472; --grey-soft:#eef0f3; --shadow:0 1px 2px rgba(16,24,40,.06),0 1px 3px rgba(16,24,40,.1);
  --radius:12px;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,Helvetica,Arial,sans-serif}
a{color:var(--brand);text-decoration:none}
a:hover{text-decoration:underline}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}
.skip{position:absolute;left:-999px}
.skip:focus{left:8px;top:8px;background:#fff;padding:8px 12px;border-radius:8px;z-index:99}
.topbar{background:#0e1320;color:#fff;position:sticky;top:0;z-index:20;border-bottom:1px solid #182034}
.topbar-inner{display:flex;align-items:center;gap:18px;min-height:62px;flex-wrap:wrap}
.brand{display:flex;gap:10px;align-items:center;color:#fff}
.brand strong{display:block;font-size:15px;letter-spacing:.2px}
.brand small{display:block;color:#9aa4b8;font-size:11px;letter-spacing:.06em;text-transform:uppercase}
.brand-mark{width:30px;height:30px;display:grid;place-items:center;background:#1f5eff;border-radius:9px;font-size:16px}
.nav{display:flex;gap:4px;flex-wrap:wrap;margin-left:auto}
.nav-link{color:#c3cad8;padding:7px 10px;border-radius:8px;font-size:13.5px;font-weight:500}
.nav-link:hover{background:#1a2233;color:#fff;text-decoration:none}
.nav-link.active{background:#1f5eff;color:#fff}
.page-head{padding:34px 0 8px}
.eyebrow{margin:0 0 6px;color:var(--muted);font-size:12.5px;text-transform:uppercase;letter-spacing:.08em}
h1{margin:0 0 8px;font-size:34px;line-height:1.15;letter-spacing:-.02em}
.lede{margin:0 0 8px;color:#3d4658;font-size:16px;max-width:900px}
h2{font-size:20px;margin:34px 0 12px;letter-spacing:-.01em}
h3{font-size:16px;margin:0 0 6px}
.section-head{display:flex;align-items:baseline;justify-content:space-between;gap:12px;margin:34px 0 12px}
.section-head h2{margin:0}
.summary{background:#0e1320;color:#e8ecf5;border-radius:16px;padding:24px 26px;margin:22px 0 4px}
.summary h2{color:#fff;margin:0 0 10px;font-size:18px}
.summary-list{margin:0;padding-left:18px}
.summary-list li{margin:8px 0;line-height:1.6}
.summary-list a{color:#9db9ff}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px}
.pick-card{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:16px;box-shadow:var(--shadow);display:flex;flex-direction:column;gap:8px}
.pick-card.high{border-top:3px solid var(--green)}
.pick-card.medium{border-top:3px solid var(--amber)}
.pick-card.low{border-top:3px solid var(--grey)}
.pick-top{display:flex;justify-content:space-between;align-items:center}
.sport{font-size:11.5px;text-transform:uppercase;letter-spacing:.07em;color:var(--muted);font-weight:600}
.pick-card h3{margin:2px 0 0;font-size:18px;line-height:1.25}
.match{margin:0;color:var(--muted);font-size:13px}
.pick-meta{display:flex;gap:14px;margin:6px 0 2px;flex-wrap:wrap}
.pick-meta span{display:flex;flex-direction:column}
.pick-meta strong{font-size:15px}
.pick-meta small{color:var(--muted);font-size:11px}
.why{margin:0;font-size:13.5px;color:#3d4658}
.more{margin-top:auto;font-size:13px;font-weight:600}
.badge{display:inline-block;padding:2px 8px;border-radius:999px;font-size:11.5px;font-weight:700;letter-spacing:.02em;white-space:nowrap}
.badge.high,.badge.green{background:var(--green-soft);color:var(--green)}
.badge.medium,.badge.amber{background:var(--amber-soft);color:var(--amber)}
.badge.low,.badge.grey{background:var(--grey-soft);color:var(--grey)}
.badge.excluded,.badge.red{background:var(--red-soft);color:var(--red)}
.table-wrap{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:13.5px}
th{text-align:left;padding:11px 14px;background:#f9fafb;color:var(--muted);font-size:11.5px;text-transform:uppercase;letter-spacing:.06em;border-bottom:1px solid var(--line);white-space:nowrap}
td{padding:11px 14px;border-bottom:1px solid var(--line);vertical-align:top}
tbody tr:last-child td{border-bottom:0}
tbody tr:hover{background:#fbfcfe}
.num{text-align:right;white-space:nowrap}
.tall td{max-width:340px}
.facts,.gaps{font-size:12.5px;color:#3d4658;max-width:330px}
.gaps{color:var(--amber)}
.src{font-size:12px;color:var(--brand);white-space:nowrap}
.muted{color:var(--muted)}
.small{font-size:12.5px}
.note{color:var(--muted);font-size:13px;margin:10px 0 0;max-width:900px}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:16px 18px;box-shadow:var(--shadow);margin:14px 0}
.two-col{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.notice{background:var(--brand-soft);border:1px solid #cddcff;border-radius:var(--radius);padding:12px 16px;margin:14px 0;font-size:14px}
.notice.warn{background:var(--amber-soft);border-color:#f3d8a8}
.prediction{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:18px 20px;box-shadow:var(--shadow);margin:16px 0}
.pred-head{display:flex;justify-content:space-between;gap:16px;align-items:flex-start;flex-wrap:wrap}
.pred-head h3{font-size:17px;margin:2px 0 2px}
.pred-price{text-align:right}
.pred-price strong{display:block;font-size:14px}
.pred-price small{color:var(--muted);font-size:11.5px}
.selection{margin:12px 0 8px;font-weight:600;color:#1c2740}
.selection span{color:var(--muted);font-weight:600;text-transform:uppercase;font-size:11px;letter-spacing:.06em;margin-right:6px}
.selection em{font-weight:400;color:var(--muted);font-style:normal;font-size:12.5px}
.prose{margin:0;font-size:14.5px;line-height:1.65;max-width:900px}
.pred-src{margin:12px 0 0;font-size:12px;color:var(--muted)}
.flag{background:var(--panel);border:1px solid var(--line);border-left:4px solid var(--grey);border-radius:var(--radius);padding:16px 18px;margin:14px 0;box-shadow:var(--shadow)}
.flag.sev-high{border-left-color:var(--red)}
.flag.sev-medium{border-left-color:var(--amber)}
.flag.sev-low{border-left-color:var(--grey)}
.flag-head{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.flag-head h3{margin:0;font-size:16px}
.flag-id{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px;color:var(--muted)}
.flag p{margin:10px 0 0;font-size:14px}
.src-line{font-size:12px}
.stat-strip{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin:18px 0}
.stat-strip div{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:14px 16px;box-shadow:var(--shadow)}
.stat-strip strong{display:block;font-size:24px;letter-spacing:-.02em}
.stat-strip span{color:var(--muted);font-size:12.5px}
.sport-grid .sport-card{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:16px;box-shadow:var(--shadow);color:var(--ink)}
.sport-grid .sport-card:hover{border-color:#b9c9ff;text-decoration:none}
.sport-card h3{margin:0 0 4px}
.sport-card p{margin:0 0 8px;color:var(--muted);font-size:13px}
.sport-card span{font-size:13px;font-weight:600;color:var(--brand)}
.prose-block h2{margin-top:28px}
.prose-block ul{padding-left:20px}
.prose-block li{margin:6px 0}
code{background:#f1f3f7;padding:1px 5px;border-radius:5px;font-size:12.5px}
.footer{border-top:1px solid var(--line);margin-top:48px;padding:22px 20px 40px;color:var(--muted);font-size:12.5px}
.footer p{margin:6px 0;max-width:900px}
@media (max-width:860px){
  .two-col{grid-template-columns:1fr}
  h1{font-size:27px}
  .nav{gap:2px}
  .nav-link{padding:6px 8px;font-size:12.5px}
  td,th{padding:9px 10px}
}
@media print{.topbar,.footer{display:none}body{background:#fff}}
"""

if __name__ == "__main__":
    main()
