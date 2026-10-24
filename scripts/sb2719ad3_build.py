#!/usr/bin/env python3
"""Calculate TB2719 fair lines and render the isolated static research desk."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import re
import shutil
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "b2719ad3"
SITE = ROOT / "b2719ad3"
OBS = json.loads((DATA / "observations.json").read_text(encoding="utf-8"))
SOURCES = OBS["source_registry"]
SPORTS = {s["slug"]: s for s in OBS["scope"]}

parser = argparse.ArgumentParser()
parser.add_argument("--as-of", help="UTC ISO timestamp; defaults to current UTC time")
args = parser.parse_args()
if args.as_of:
    AS_OF = datetime.fromisoformat(args.as_of.replace("Z", "+00:00"))
    if AS_OF.tzinfo is None:
        AS_OF = AS_OF.replace(tzinfo=timezone.utc)
else:
    AS_OF = datetime.now(timezone.utc)
AS_OF = AS_OF.astimezone(timezone.utc).replace(microsecond=0)
AS_OF_TEXT = AS_OF.isoformat().replace("+00:00", "Z")


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def american_value(p: float) -> int:
    if not 0 < p < 1:
        raise ValueError(f"Probability outside open unit interval: {p}")
    raw = -100 * p / (1 - p) if p >= 0.5 else 100 * (1 - p) / p
    return int(round(raw))


def american(p: float) -> str:
    value = american_value(p)
    return f"+{value}" if value > 0 else str(value)


def beta_rate(r: dict) -> float:
    return (r["wins"] + 2) / (r["gp"] + 4)


def log5_rate(home_rate: float, away_rate: float) -> float:
    numerator = home_rate * (1 - away_rate)
    denominator = numerator + away_rate * (1 - home_rate)
    return numerator / denominator


def log5(home: dict, away: dict) -> float:
    return log5_rate(beta_rate(home), beta_rate(away))


def poisson(mean: float) -> list[float]:
    # Ten standard deviations plus twenty captures the relevant tail even for NBA means.
    upper = max(30, int(math.ceil(mean + 10 * math.sqrt(mean) + 20)))
    values = [math.exp(-mean)]
    for k in range(1, upper + 1):
        values.append(values[-1] * mean / k)
    return values


def score_probabilities(home_mean: float, away_mean: float) -> dict[str, float]:
    hs, as_ = poisson(home_mean), poisson(away_mean)
    result = {"home": 0.0, "draw": 0.0, "away": 0.0, "home_minus_1_5": 0.0, "home_minus_4_5": 0.0, "totals": {}}
    for i, hp in enumerate(hs):
        for j, ap in enumerate(as_):
            p = hp * ap
            if i > j:
                result["home"] += p
            elif i == j:
                result["draw"] += p
            else:
                result["away"] += p
            if i - j >= 2:
                result["home_minus_1_5"] += p
            if i - j >= 5:
                result["home_minus_4_5"] += p
            total = i + j
            result["totals"][total] = result["totals"].get(total, 0.0) + p
    # Remove tiny floating tail before consumers sum the three main outcomes.
    main_mass = result["home"] + result["draw"] + result["away"]
    for key in ("home", "draw", "away"):
        result[key] /= main_mass
    return result


def scoring_means(home: dict, away: dict) -> tuple[float, float]:
    if any(r.get(key) is None for r in (home, away) for key in ("gf", "ga")):
        raise ValueError("Scoring derivatives require all GF/GA fields")
    return (
        (home["gf"] / home["gp"] + away["ga"] / away["gp"]) / 2,
        (away["gf"] / away["gp"] + home["ga"] / home["gp"]) / 2,
    )


def derivative_from_scores(home: dict, away: dict, handicap: float) -> dict:
    hm, am = scoring_means(home, away)
    matrix = score_probabilities(hm, am)
    expected = hm + am
    line = math.floor(expected * 2 + 0.5) / 2
    over = sum(p for total, p in matrix["totals"].items() if total > line)
    cover = matrix["home_minus_4_5" if handicap == 4.5 else "home_minus_1_5"]
    return {
        "expected_home_score": round(hm, 3),
        "expected_away_score": round(am, 3),
        "expected_total": round(expected, 3),
        "total_line": line,
        "over_probability": over,
        "over_fair_american": american_value(over),
        "home_handicap": -handicap,
        "home_cover_probability": cover,
        "home_cover_fair_american": american_value(cover),
    }


def volleyball_derivative(home: dict, away: dict) -> dict:
    def set_rate(r: dict) -> float:
        return (r["sets_won"] + 1) / (r["sets_won"] + r["sets_lost"] + 2)

    q = log5_rate(set_rate(home), set_rate(away))
    p3 = q**3 + (1 - q) ** 3
    p4 = 3 * (q**3 * (1 - q) + (1 - q) ** 3 * q)
    p5 = 6 * q**2 * (1 - q) ** 2
    home_cover = q**3 + 3 * q**3 * (1 - q)
    return {
        "expected_home_score": None,
        "expected_away_score": None,
        "expected_total": round(3 * p3 + 4 * p4 + 5 * p5, 3),
        "total_line": 4.5,
        "over_probability": p5,
        "over_fair_american": american_value(p5),
        "home_handicap": -1.5,
        "home_cover_probability": home_cover,
        "home_cover_fair_american": american_value(home_cover),
        "set_win_probability": q,
    }


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w’'-]+\b", text, flags=re.UNICODE))


def high_gate(e: dict, p: float, fair: int, minimum_sample: int, started: bool) -> tuple[dict, list[str]]:
    prediction = e.get("high_prediction", "")
    checks = {
        "probability_above_70": p > 0.70,
        "fair_price_in_band": -250 <= fair <= 10000,
        "minimum_six_games_each": minimum_sample >= 6,
        "prediction_30_words": word_count(prediction) >= 30,
        "prediction_language": not re.search(r"\b(model|verified)\b", prediction, re.IGNORECASE),
        "availability_context": bool(e.get("availability", "").strip()),
        "confirmed_future_start": bool(e.get("start_utc")) and not started,
    }
    reasons = [key for key, passed in checks.items() if not passed]
    return checks, reasons


def price_event(e: dict, started: bool) -> dict | None:
    if started or not e.get("pricing"):
        return None
    pricing = e["pricing"]
    home, away = pricing["home"], pricing["away"]
    minimum_sample = min(home["gp"], away["gp"])
    derivative = None
    method = ""
    if pricing["kind"] == "volleyball":
        p_home = log5(home, away)
        probabilities = {"home": p_home, "away": 1 - p_home}
        derivative = volleyball_derivative(home, away)
        method = "Beta(2,2)-shrunk log5 match records; separate set screen"
    elif pricing["kind"] == "score3":
        hm, am = scoring_means(home, away)
        matrix = score_probabilities(hm, am)
        probabilities = {key: matrix[key] for key in ("home", "draw", "away")}
        derivative = derivative_from_scores(home, away, pricing.get("handicap", 1.5))
        method = "Independent Poisson scoring approximation with draw"
    elif pricing["kind"] == "baseball":
        hr, ar = home, away
        home_overall = hr["wins"] / hr["gp"]
        away_overall = ar["wins"] / ar["gp"]
        exponent = 1.83
        home_pyth = hr["gf"] ** exponent / (hr["gf"] ** exponent + hr["ga"] ** exponent)
        away_pyth = ar["gf"] ** exponent / (ar["gf"] ** exponent + ar["ga"] ** exponent)
        home_split = hr["home_wins"] / hr["home_gp"]
        away_split = ar["away_wins"] / ar["away_gp"]
        p_home = ((home_overall - away_overall) + (home_pyth - away_pyth) + (home_split - away_split)) / 6 + 0.5
        probabilities = {"home": p_home, "away": 1 - p_home}
        derivative = derivative_from_scores(home, away, pricing.get("handicap", 1.5))
        method = "Equal blend of overall, Pythagorean and venue-split differentials"
    else:
        p_home = log5(home, away)
        probabilities = {"home": p_home, "away": 1 - p_home}
        method = "Beta(2,2)-shrunk log5 on official W-L records"
        if all(r.get(key) is not None for r in (home, away) for key in ("gf", "ga")):
            derivative = derivative_from_scores(home, away, pricing.get("handicap", 1.5))
    side = max(probabilities, key=probabilities.get)
    p = probabilities[side]
    fair = american_value(p)
    checks, reasons = high_gate(e, p, fair, minimum_sample, started)
    is_high = not reasons
    grade = "High" if is_high else ("Medium" if minimum_sample >= 5 and p >= 0.55 else "Low")
    selection = e[side]
    market = "Three-way winner" if pricing["kind"] == "score3" else "Match winner"
    if e["sport"] == "baseball":
        market = "Moneyline"
    elif e["sport"] == "ice-hockey":
        market = "Moneyline"
    return {
        "method": method,
        "probabilities": probabilities,
        "selection_side": side,
        "selection": selection,
        "market": market,
        "probability": p,
        "fair_american": fair,
        "fair_decimal": 1 / p,
        "grade": grade,
        "minimum_sample": minimum_sample,
        "high_gate": checks,
        "high_gate_failures": reasons,
        "prediction": e.get("high_prediction", "") if is_high else "",
        "prediction_words": word_count(e.get("high_prediction", "")) if is_high else 0,
        "derivative": derivative,
    }


def source_link(key: str, label: str = "Official") -> str:
    s = SOURCES[key]
    return f'<a href="{esc(s["url"])}" target="_blank" rel="noopener noreferrer">{esc(label)}<span class="external" aria-hidden="true">↗</span></a>'


def event_sources(e: dict) -> str:
    keys = []
    for key in [e["official_source"], *e.get("evidence_sources", [])]:
        if key not in keys:
            keys.append(key)
    links = "".join(f'<li>{source_link(key, SOURCES[key]["publisher"])} <span>{esc(SOURCES[key]["supports"])}</span></li>' for key in keys)
    flags = "".join(f"<li>{esc(flag)}</li>" for flag in e.get("flags", []))
    notes = "".join(f"<li>{esc(note)}</li>" for note in e.get("notes", []))
    availability = f'<p><strong>Availability:</strong> {esc(e["availability"])}</p>' if e.get("availability") else ""
    flag_block = f'<div class="flag-box"><strong>Review flags</strong><ul>{flags}</ul></div>' if flags else ""
    note_block = f'<ul class="evidence-notes">{notes}</ul>' if notes else ""
    return f'<details class="evidence"><summary>Evidence &amp; limits</summary><div class="evidence-body">{note_block}{availability}{flag_block}<ul class="source-list">{links}</ul></div></details>'


def time_cell(e: dict) -> str:
    value = e.get("start_utc")
    if not value:
        return '<td data-label="Start (UTC)" class="blank-value" title="Start unconfirmed; see Flagged for Review"><span class="flag-icon" aria-label="Start flagged">!</span></td>'
    dt = parse_time(value)
    label = dt.strftime("%d %b · %H:%M")
    if e.get("not_before"):
        label = "NB " + label
    return f'<td data-label="Start (UTC)"><time datetime="{esc(value)}">{esc(label)}</time></td>'


def fixture_row(row: dict, show_sport: bool = True) -> str:
    e, a = row, row.get("analysis")
    sport = f'<td data-label="Sport"><a href="sports/{esc(e["sport"])}.html">{esc(SPORTS[e["sport"]]["name"])}</a></td>' if show_sport else ""
    match = f'<td data-label="Match"><strong>{esc(e["away"])}</strong><span class="at">at</span><strong>{esc(e["home"])}</strong><small>{esc(e["competition"])}</small></td>'
    if a:
        selection = f'<td data-label="Selection"><strong>{esc(a["selection"])}</strong><small>{esc(a["market"])}</small></td>'
        fair = f'<td data-label="Fair odds"><span class="odds">{american(a["probability"])}</span><small>{a["probability"]:.1%}</small></td>'
        grade = f'<td data-label="Grade"><span class="grade grade-{a["grade"].lower()}">{a["grade"]}</span></td>'
    else:
        selection = '<td data-label="Selection"><span class="no-selection">No selection</span></td>'
        fair = '<td data-label="Fair odds" class="blank-value"></td>'
        grade = '<td data-label="Grade" class="blank-value"></td>'
    return f'<tr class="fixture-row" data-event-id="{esc(e["id"])}">{time_cell(e)}{sport}{match}{selection}{fair}{grade}<td data-label="Sources">{source_link(e["official_source"])}{event_sources(e)}</td></tr>'


def fixture_table(rows: list[dict], show_sport: bool = True) -> str:
    sport_head = "<th>Sport</th>" if show_sport else ""
    body = "".join(fixture_row(row, show_sport) for row in rows)
    return f'<div class="table-wrap"><table><thead><tr><th>Start (UTC)</th>{sport_head}<th>Match</th><th>Selection</th><th>Fair odds</th><th>Grade</th><th>Sources</th></tr></thead><tbody>{body}</tbody></table></div>'


def derivative_table(rows: list[dict]) -> str:
    output = []
    for row in rows:
        e, a = row, row.get("analysis")
        d = a.get("derivative") if a else None
        match = f'<strong>{esc(e["away"])} at {esc(e["home"])}</strong>'
        if d:
            values = (
                f'<td data-label="Expected total">{d["expected_total"]:.2f}</td>'
                f'<td data-label="Total line">{d["total_line"]:.1f}</td>'
                f'<td data-label="Over fair"><span class="odds">{american(d["over_probability"])}</span><small>{d["over_probability"]:.1%}</small></td>'
                f'<td data-label="Home handicap">{d["home_handicap"]:+.1f}</td>'
                f'<td data-label="Home cover fair"><span class="odds">{american(d["home_cover_probability"])}</span><small>{d["home_cover_probability"]:.1%}</small></td>'
            )
        else:
            values = '<td data-label="Expected total" class="blank-value"></td><td data-label="Total line" class="blank-value"></td><td data-label="Over fair" class="blank-value"></td><td data-label="Home handicap" class="blank-value"></td><td data-label="Home cover fair" class="blank-value"></td>'
        output.append(f'<tr data-market-event="{esc(e["id"])}"><td data-label="Match">{match}</td>{values}<td data-label="Official">{source_link(e["official_source"])}</td></tr>')
    return f'<div class="table-wrap"><table><thead><tr><th>Match</th><th>Expected total</th><th>Total line</th><th>Over fair</th><th>Home handicap</th><th>Home cover fair</th><th>Official</th></tr></thead><tbody>{"".join(output)}</tbody></table></div>'


def high_card(row: dict, nested: bool = False) -> str:
    e, a = row, row["analysis"]
    sport_prefix = "../" if nested else ""
    start = parse_time(e["start_utc"]).strftime("%d %B · %H:%M UTC") if e.get("start_utc") else "Start flagged"
    return f'''<article class="high-card" id="pick-{esc(e["id"])}">
      <div class="high-top"><a href="{sport_prefix}sports/{esc(e["sport"])}.html">{esc(SPORTS[e["sport"]]["name"])}</a><span>{esc(start)}</span></div>
      <h3>{esc(a["selection"])}</h3>
      <p class="matchup">{esc(e["away"])} at {esc(e["home"])} · {esc(a["market"])}</p>
      <div class="price-line"><span><small>Fair American</small><strong>{american(a["probability"])}</strong></span><span><small>Estimated chance</small><strong>{a["probability"]:.1%}</strong></span><span><small>Decimal</small><strong>{a["fair_decimal"]:.2f}</strong></span></div>
      <p class="prediction">{esc(a["prediction"])}</p>
      <div class="card-foot"><span>{a["prediction_words"]} words · unique analysis</span><span>{source_link(e["official_source"], "Official match evidence")}</span></div>
    </article>'''


def page(title: str, body: str, description: str, nested: bool = False, active: str = "") -> str:
    root = "../" if nested else ""
    def nav(name: str, href: str, label: str) -> str:
        cls = ' class="active"' if active == name else ""
        return f'<a{cls} href="{root}{href}">{label}</a>'
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · OLBG Research Desk</title><meta name="description" content="{esc(description)}">
<link rel="stylesheet" href="{root}styles.css"></head><body>
<a class="skip" href="#main">Skip to research</a>
<header class="site-header"><div class="header-inner"><a class="brand" href="{root}index.html"><span class="brand-mark">15</span><span><strong>OLBG</strong><small>Research Desk</small></span></a>
<nav aria-label="Main navigation">{nav("today", "index.html", "Today")}{nav("sports", "sports.html", "15 sports")}{nav("review", "flagged-for-review.html", "Flagged for Review")}{nav("method", "method.html", "Method")}</nav></div></header>
<div class="snapshot"><div><span class="live-dot"></span> Independent evidence snapshot <strong>{esc(AS_OF_TEXT)}</strong><span class="snapshot-note">Started events are removed from active picks.</span></div></div>
<main id="main">{body}</main>
<footer><div><strong>Independent research, not bookmaker prices.</strong><p>OLBG is used for discovery and market locations only. Official competition sources control the evidence. Fair odds are originated estimates, not available odds or guarantees.</p></div><a href="{root}method.html">Read the method &amp; sources</a></footer>
</body></html>'''


def section_heading(kicker: str, title: str, text: str = "") -> str:
    paragraph = f"<p>{esc(text)}</p>" if text else ""
    return f'<div class="section-heading"><div><span class="kicker">{esc(kicker)}</span><h2>{esc(title)}</h2>{paragraph}</div></div>'


# Calculate active and started rows. Blank clocks remain visible as flagged, never guessed.
rows: list[dict] = []
started_rows: list[dict] = []
for original in OBS["events"]:
    e = dict(original)
    dt = parse_time(e.get("start_utc"))
    started = bool(dt and dt <= AS_OF)
    e["started_at_snapshot"] = started
    analysis = price_event(e, started)
    row = {**e, "analysis": analysis}
    if started:
        started_rows.append(row)
    else:
        rows.append(row)

rows.sort(key=lambda r: (r.get("start_utc") is None, r.get("start_utc") or "", SPORTS[r["sport"]]["name"], r["id"]))
by_sport: dict[str, list[dict]] = defaultdict(list)
for row in rows:
    by_sport[row["sport"]].append(row)
high_rows = sorted((r for r in rows if r.get("analysis", {}) and r["analysis"]["grade"] == "High"), key=lambda r: (-r["analysis"]["probability"], r["id"]))
medium_rows = sorted((r for r in rows if r.get("analysis", {}) and r["analysis"]["grade"] == "Medium"), key=lambda r: (-r["analysis"]["probability"], r["id"]))

# Persist machine-readable prices before rendering. Started rows have no active analysis.
prices_payload = {
    "desk": "TB2719",
    "as_of": AS_OF_TEXT,
    "method_version": OBS["method_version"],
    "active_rows": rows,
    "started_rows": [{**r, "analysis": None, "exclusion": "Start passed at snapshot"} for r in started_rows],
    "high_prediction_ids": [r["id"] for r in high_rows],
    "scope": OBS["scope"],
}
(DATA / "prices.json").write_text(json.dumps(prices_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
predictions = [
    {
        "event_id": r["id"], "sport": r["sport"], "selection": r["analysis"]["selection"],
        "probability": r["analysis"]["probability"], "fair_american": r["analysis"]["fair_american"],
        "prediction": r["analysis"]["prediction"], "words": r["analysis"]["prediction_words"],
        "official_source": SOURCES[r["official_source"]]["url"],
        "sha256": hashlib.sha256(re.sub(r"\s+", " ", r["analysis"]["prediction"].strip().lower()).encode()).hexdigest(),
    }
    for r in high_rows
]
(DATA / "predictions.json").write_text(json.dumps(predictions, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

# Review register includes every event flag, started exclusion and high-gate rejection.
review: list[dict] = []
for r in rows:
    for flag in r.get("flags", []):
        review.append({"sport": r["sport"], "item": f'{r["away"]} at {r["home"]}', "reason": flag, "source": r["official_source"], "event_id": r["id"], "kind": "event"})
    a = r.get("analysis")
    if a and a["probability"] > 0.70 and a["grade"] != "High":
        review.append({"sport": r["sport"], "item": f'High withheld: {a["selection"]}', "reason": "Gate failures: " + ", ".join(a["high_gate_failures"]), "source": r["official_source"], "event_id": r["id"], "kind": "gate"})
for r in started_rows:
    review.append({"sport": r["sport"], "item": f'{r["away"]} at {r["home"]}', "reason": f'Start {r["start_utc"]} had passed at {AS_OF_TEXT}; excluded from active upcoming selections pending an official state refresh.', "source": r["official_source"], "event_id": r["id"], "kind": "started"})
for lead in OBS["review_leads"]:
    review.append({"sport": lead["sport"], "item": lead["item"], "reason": lead["reason"], "source": lead["official_source"], "event_id": "", "kind": "inventory"})
(DATA / "review.json").write_text(json.dumps(review, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

if SITE.exists():
    shutil.rmtree(SITE)
(SITE / "sports").mkdir(parents=True)
(SITE / "data").mkdir()

# Home page.
count_priced = sum(bool(r.get("analysis")) for r in rows)
count_sources = len(SOURCES)
high_html = "".join(high_card(r) for r in high_rows) if high_rows else '<div class="empty-state"><h3>No High selections survived every gate.</h3><p>The board remains empty rather than filling the daily target with unsupported picks.</p></div>'
sport_cards = []
for s in OBS["scope"]:
    sr = by_sport[s["slug"]]
    high_count = sum(bool(r.get("analysis")) and r["analysis"]["grade"] == "High" for r in sr)
    priced = sum(bool(r.get("analysis")) for r in sr)
    sport_cards.append(f'''<a class="sport-card" href="sports/{esc(s["slug"])}.html"><div><span class="sport-index">{OBS["scope"].index(s)+1:02d}</span><span class="grade grade-high">{high_count} High</span></div><h3>{esc(s["name"])}</h3><p>{len(sr)} upcoming rows · {priced} priced</p><span class="card-link">Open sport desk <span aria-hidden="true">→</span></span></a>''')
next_day = [r for r in rows if r.get("start_utc") and parse_time(r["start_utc"]).date() == AS_OF.date()]
home_body = f'''
<section class="hero"><div class="hero-copy"><span class="kicker">Saturday · 24 October 2026</span><h1>Fifteen sports.<br><em>One evidence desk.</em></h1><p>Independent fair lines, conservative grades and source-linked analysis for today and upcoming matches. No community percentages disguised as probability.</p><div class="hero-actions"><a class="button" href="#high-picks">See High selections</a><a class="button secondary" href="sports.html">Browse all sports</a></div></div><div class="hero-panel"><span class="panel-label">Executive readout</span><strong>{len(high_rows)}</strong><p>High selections across the entire board</p><div class="panel-rule"></div><dl><div><dt>Upcoming rows</dt><dd>{len(rows)}</dd></div><div><dt>Originated winner prices</dt><dd>{count_priced}</dd></div><div><dt>Registered sources</dt><dd>{count_sources}</dd></div></dl></div></section>
<section class="metric-strip" aria-label="Board summary"><div><span>Today’s confirmed starts</span><strong>{len(next_day)}</strong></div><div><span>Medium research leans</span><strong>{len(medium_rows)}</strong></div><div><span>Started / excluded</span><strong>{len(started_rows)}</strong></div><div><span>Items to review</span><strong>{len(review)}</strong></div></section>
<section id="high-picks">{section_heading("The strongest qualifying positions", "High selections", "Strictly above 70%, fair odds from -250 to +10000, at least six games per side, availability context and a unique 30+ word analysis.")}<div class="high-grid">{high_html}</div></section>
<section>{section_heading("At a glance", "Today & upcoming", "Every active fixture row has an official-source link. Blank fields are deliberate and appear on Flagged for Review.")}{fixture_table(rows)}</section>
<section>{section_heading("Navigate the board", "Fifteen sport desks", "The five-High-per-sport figure is a target, never a quota. Shortfalls remain shortfalls.")}<div class="sport-grid">{"".join(sport_cards)}</div></section>
<section class="method-callout"><div><span class="kicker">Transparent by construction</span><h2>Price first. Grade second.</h2><p>Winner probabilities use shrunk log5 records or an explicitly labeled scoring approximation. High status is never assigned by rounding up to the band.</p></div><a class="button dark" href="method.html">Inspect formulas &amp; gates</a></section>
'''
(SITE / "index.html").write_text(page("Today & upcoming", home_body, "Current independent OLBG research across exactly fifteen sports.", active="today"), encoding="utf-8")

# Sports index.
index_cards = []
for s in OBS["scope"]:
    sr = by_sport[s["slug"]]
    high_count = sum(bool(r.get("analysis")) and r["analysis"]["grade"] == "High" for r in sr)
    olbg_links = " · ".join(f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">OLBG {i+1}↗</a>' for i, url in enumerate(s["olbg_urls"]))
    index_cards.append(f'''<article class="directory-card"><div class="directory-title"><span>{OBS["scope"].index(s)+1:02d}</span><h2>{esc(s["name"])}</h2></div><p>{len(sr)} active rows · {high_count} High</p><p>{esc(s["market_location"])}</p><div class="directory-links"><a href="sports/{esc(s["slug"])}.html">Open desk →</a>{olbg_links}</div></article>''')
sports_body = f'<section class="page-hero"><span class="kicker">Complete requested scope</span><h1>Fifteen sports.<br>No silent substitutions.</h1><p>Gaelic Football and Hurling retain separate OLBG discovery routes inside the single requested Gaelic Sports desk.</p></section><section><div class="directory-grid">{"".join(index_cards)}</div></section>'
(SITE / "sports.html").write_text(page("Fifteen sports", sports_body, "Sport-by-sport current research directories.", active="sports"), encoding="utf-8")

# Sport subpages.
for s in OBS["scope"]:
    slug = s["slug"]
    sr = by_sport[slug]
    sh = [r for r in high_rows if r["sport"] == slug]
    olbg_links = "".join(f'<a class="button secondary" href="{esc(url)}" target="_blank" rel="noopener noreferrer">Open OLBG discovery ↗</a>' for url in s["olbg_urls"])
    high_section = f'<div class="high-grid">{"".join(high_card(r, nested=True) for r in sh)}</div>' if sh else '<div class="empty-state"><strong>No High selection on this desk.</strong><p>Nothing met every price, probability, sample, availability and writing gate. The target is not filled artificially.</p></div>'
    if sr:
        fixtures = fixture_table(sr, show_sport=False)
        derivatives = derivative_table(sr)
    else:
        fixtures = '<div class="empty-state"><strong>No supportable upcoming match rows.</strong><p>See the review register for the inventory limitation. No event has been invented.</p></div>'
        derivatives = '<div class="empty-state"><strong>No derivative markets to display.</strong></div>'
    body = f'''
<section class="sport-hero"><div><span class="kicker">Sport desk · {OBS["scope"].index(s)+1:02d} / 15</span><h1>{esc(s["name"])}</h1><p>{esc(s["market_location"])}</p><div class="hero-actions">{olbg_links}</div></div><div class="sport-score"><span>High / target</span><strong>{len(sh)}<small>/ 5</small></strong><p>{len(sr)} active rows · {sum(bool(r.get("analysis")) for r in sr)} priced</p></div></section>
<section>{section_heading("Full written positions", "High selections")}{high_section}</section>
<section>{section_heading("Winner screen", "Upcoming match list", "Selections are originated leans unless they appear above with full High analysis.")}{fixtures}</section>
<section>{section_heading("Handicap & total investigation", "Derivative screens", "Blank derivative cells mean the captured official evidence did not support a separate price. They are not zeroes.")}{derivatives}</section>
<section class="source-callout"><h2>Where picks live on OLBG</h2><p>{esc(s["market_location"])}</p><p>Community support shown there is not an input to these fair prices. Use the official link on every row for manual review.</p></section>
'''
    (SITE / "sports" / f"{slug}.html").write_text(page(s["name"], body, f'{s["name"]} independent match research and fair lines.', nested=True, active="sports"), encoding="utf-8")

# Review page.
review_rows = "".join(
    f'<tr data-review="{esc(i)}"><td data-label="Type"><span class="review-type">{esc(r["kind"])}</span></td><td data-label="Sport"><a href="sports/{esc(r["sport"])}.html">{esc(SPORTS[r["sport"]]["name"])}</a></td><td data-label="Item"><strong>{esc(r["item"])}</strong></td><td data-label="Reason">{esc(r["reason"])}</td><td data-label="Source">{source_link(r["source"], "Review source")}</td></tr>'
    for i, r in enumerate(review)
)
review_body = f'''
<section class="page-hero review-hero"><span class="kicker">Nothing swept aside</span><h1>Flagged for Review</h1><p>{len(review)} explicit limitations, timing exclusions and inventory gaps. Unconfirmed starts and runner fields stay blank; unsupported matches stay unpriced.</p></section>
<section><div class="review-summary"><div><strong>{len(started_rows)}</strong><span>Started exclusions</span></div><div><strong>{sum(not r.get("analysis") for r in rows)}</strong><span>Active rows without a price</span></div><div><strong>{sum(not r.get("start_utc") for r in rows)}</strong><span>Blank UTC starts</span></div></div>
<div class="table-wrap"><table class="review-table"><thead><tr><th>Type</th><th>Sport</th><th>Item</th><th>Reason</th><th>Source</th></tr></thead><tbody>{review_rows}</tbody></table></div></section>
'''
(SITE / "flagged-for-review.html").write_text(page("Flagged for Review", review_body, "All current data limitations, exclusions and unconfirmed fields.", active="review"), encoding="utf-8")

# Method and complete source registry.
source_rows = "".join(
    f'<tr data-source-id="{esc(key)}"><td data-label="Source"><strong>{esc(key)}</strong></td><td data-label="Publisher">{esc(s["publisher"])}</td><td data-label="Supports">{esc(s["supports"])}</td><td data-label="Accessed">{esc(s["accessed_at"])}</td><td data-label="Link">{source_link(key, "Open source")}</td></tr>'
    for key, s in SOURCES.items()
)
method_body = f'''
<section class="page-hero"><span class="kicker">Method · {esc(OBS["method_version"])}</span><h1>Readable inputs.<br>Auditable prices.</h1><p>All prices are fair estimates originated from the listed evidence. They are not copied odds, OLBG community support or claims of market availability.</p></section>
<section class="method-grid"><article><span class="method-number">01</span><h2>Two-way winner screen</h2><p>For official games played <code>G</code> and wins <code>W</code>, each team receives a Beta(2,2)-shrunk rate:</p><pre>r = (W + 2) / (G + 4)</pre><p>The home rate <code>rH</code> and away rate <code>rA</code> enter log5 without a hidden home adjustment:</p><pre>pH = rH(1-rA) / [rH(1-rA) + rA(1-rH)]</pre><p>NHL games played includes overtime losses, matching the league’s win-percentage basis. NHL moneyline includes overtime; its scoring derivatives use regulation-only independent Poisson scores.</p></article><article><span class="method-number">02</span><h2>Scoring &amp; derivative screens</h2><pre>home mean = (home GF/G + away GA/G) / 2
away mean = (away GF/G + home GA/G) / 2</pre><p>Independent Poisson score matrices produce three-way outcomes, home handicaps and totals. The total line is rounded to the nearest half point. This is an approximation: no unlisted home, lineup or injury adjustment is inserted.</p><p>Volleyball winners use match records. Set derivatives use separately shrunk set shares and best-of-five enumeration. Baseball averages overall, Pythagorean and venue-split differentials equally; named starters remain context rather than an undocumented adjustment.</p></article><article><span class="method-number">03</span><h2>From probability to fair odds</h2><pre>p ≥ 0.5: -100p / (1-p)
p &lt; 0.5: 100(1-p) / p</pre><p>American prices are rounded to the nearest whole number after calculation. The High gate is applied to that originated price; no probability or price is clipped to make a selection qualify.</p></article><article><span class="method-number">04</span><h2>High means every gate</h2><ul class="gate-list"><li>Probability strictly above 70%</li><li>Fair American odds from -250 through +10000</li><li>At least six comparable games per participant</li><li>Confirmed future UTC start</li><li>Official availability context</li><li>Unique natural analysis of at least 30 words</li><li>No prohibited prediction language</li></ul><p>Medium requires at least six games per side and a selected probability of at least 55% unless all High gates pass. Everything else is Low. At most five High rows per sport are allowed; there is no minimum.</p></article></section>
<section>{section_heading("Scope discipline", "What is not priced", "Started events are excluded at the snapshot. Unconfirmed clocks remain blank. Missing goals, complete runner cards, comparable records or confirmed pairings suppress the affected market. One- and two-game samples cannot be High. OLBG pagination and later Load More content are not claimed as an exhaustive global fixture census; the official rows captured here are shown line by line with their limits.")}</section>
<section>{section_heading("Manual review", "Source registry", f'{len(SOURCES)} registered discovery and official evidence locations. Access timestamps record this desk’s research snapshot; shell downloads from sporting hosts were not used.') }<div class="table-wrap"><table><thead><tr><th>Source</th><th>Publisher</th><th>Supports</th><th>Accessed</th><th>Link</th></tr></thead><tbody>{source_rows}</tbody></table></div></section>
'''
(SITE / "method.html").write_text(page("Method & sources", method_body, "Formulas, confidence gates and complete evidence source registry.", active="method"), encoding="utf-8")

# Public data copies and build manifest.
for name in ("observations.json", "sources.json", "prices.json", "predictions.json", "review.json"):
    shutil.copy2(DATA / name, SITE / "data" / name)
manifest = {
    "desk": "TB2719",
    "generated_at": AS_OF_TEXT,
    "scope_count": len(OBS["scope"]),
    "active_event_rows": len(rows),
    "started_exclusions": len(started_rows),
    "priced_rows": count_priced,
    "high_predictions": len(high_rows),
    "high_by_sport": dict(Counter(r["sport"] for r in high_rows)),
    "review_items": len(review),
    "source_count": len(SOURCES),
    "site_root": "b2719ad3/",
}
(DATA / "build-report.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
shutil.copy2(DATA / "build-report.json", SITE / "data" / "build-report.json")

CSS = r'''
:root{--ink:#17202b;--muted:#64707d;--navy:#0c1726;--navy2:#13243a;--paper:#f3f5f4;--white:#fff;--line:#dce2e3;--lime:#b8ec68;--teal:#16766e;--amber:#9a5b00;--red:#a03b3b;--shadow:0 12px 32px rgba(12,23,38,.08)}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.6 Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}a{color:var(--teal);text-decoration-thickness:1px;text-underline-offset:3px}a:hover{text-decoration-thickness:2px}h1,h2,h3,p{margin-top:0}h1,h2,h3{line-height:1.12;letter-spacing:-.035em}h1{font-size:clamp(2.6rem,6vw,5.4rem)}h2{font-size:clamp(1.6rem,3vw,2.35rem)}h3{font-size:1.35rem}code,pre{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}pre{white-space:pre-wrap;background:#edf1ef;padding:14px;border-radius:8px;font-size:.84rem}.skip{position:absolute;left:-9999px}.skip:focus{left:16px;top:16px;background:#fff;padding:10px;z-index:99}.site-header{background:var(--navy);color:#fff}.header-inner{max-width:1440px;margin:auto;padding:22px 36px;display:flex;align-items:center;justify-content:space-between;gap:28px}.brand{display:flex;align-items:center;gap:12px;color:#fff;text-decoration:none}.brand-mark{display:grid;place-items:center;width:42px;height:42px;border:1px solid #547067;border-radius:50%;color:var(--lime);font-weight:800}.brand strong,.brand small{display:block}.brand strong{font-size:1.25rem;letter-spacing:.12em}.brand small{color:#aebdc9;font-size:.72rem;letter-spacing:.1em;text-transform:uppercase}nav{display:flex;gap:28px;flex-wrap:wrap}nav a{color:#c3ced7;text-decoration:none;font-size:.88rem}nav a.active,nav a:hover{color:var(--lime)}.snapshot{background:#101f32;color:#bfccD6;border-top:1px solid #243347;font-size:.76rem}.snapshot>div{max-width:1440px;margin:auto;padding:9px 36px}.snapshot strong{color:#fff;margin-left:6px}.snapshot-note{margin-left:20px;color:#8294a5}.live-dot{display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--lime);margin-right:7px}main{max-width:1440px;margin:auto;padding:0 36px 70px}section{margin:68px 0}.hero{margin:0 -36px;padding:78px 36px 70px;background:var(--navy);color:#fff;display:grid;grid-template-columns:1.7fr .8fr;gap:70px;align-items:center}.hero h1{margin:14px 0 25px;max-width:850px}.hero h1 em{color:var(--lime);font-style:normal}.hero-copy>p{max-width:700px;color:#bdc9d3;font-size:1.08rem}.kicker{display:block;color:var(--teal);font-size:.72rem;font-weight:800;letter-spacing:.16em;text-transform:uppercase;margin-bottom:12px}.hero .kicker,.sport-hero .kicker{color:var(--lime)}.hero-actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:30px}.button{display:inline-block;background:var(--lime);color:var(--navy);font-weight:750;text-decoration:none;padding:12px 18px;border-radius:5px;font-size:.86rem}.button.secondary{background:transparent;color:inherit;border:1px solid currentColor}.button.dark{background:var(--navy);color:#fff}.hero-panel{background:var(--navy2);border:1px solid #2b3d52;padding:30px;border-radius:10px;box-shadow:var(--shadow)}.panel-label{color:#9aabba;font-size:.72rem;text-transform:uppercase;letter-spacing:.13em}.hero-panel>strong{display:block;color:var(--lime);font-size:5.5rem;line-height:1.1;letter-spacing:-.08em}.hero-panel>p{color:#c0ccd5}.panel-rule{height:1px;background:#32465b;margin:24px 0}.hero-panel dl{margin:0}.hero-panel dl div{display:flex;justify-content:space-between;padding:7px 0;gap:20px}.hero-panel dt{color:#9aabba}.hero-panel dd{margin:0;font-weight:700}.metric-strip{margin:0;background:#fff;display:grid;grid-template-columns:repeat(4,1fr);border:1px solid var(--line);border-top:0}.metric-strip div{padding:22px 28px;border-right:1px solid var(--line)}.metric-strip div:last-child{border:0}.metric-strip span{display:block;color:var(--muted);font-size:.78rem}.metric-strip strong{font-size:1.8rem}.section-heading{display:flex;justify-content:space-between;align-items:end;margin-bottom:22px}.section-heading h2{margin-bottom:8px}.section-heading p{color:var(--muted);max-width:830px;margin:0}.high-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px}.high-card{background:var(--navy);color:#fff;border-radius:10px;padding:28px;border-top:4px solid var(--lime);box-shadow:var(--shadow)}.high-top,.card-foot{display:flex;justify-content:space-between;gap:16px;font-size:.74rem;color:#a9b8c5}.high-top a{color:var(--lime);text-transform:uppercase;letter-spacing:.1em;font-weight:800}.high-card h3{font-size:2rem;margin:25px 0 7px}.matchup{color:#9fb0be}.price-line{display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid #2d3f53;border-bottom:1px solid #2d3f53;padding:17px 0;margin:22px 0}.price-line span{display:flex;flex-direction:column}.price-line small{color:#93a5b4;font-size:.68rem;text-transform:uppercase;letter-spacing:.08em}.price-line strong{font-size:1.35rem;color:var(--lime)}.prediction{font-size:1rem;line-height:1.75;color:#e1e7eb}.card-foot{border-top:1px solid #2d3f53;padding-top:16px}.card-foot a{color:#d8e3ea}.table-wrap{overflow-x:auto;background:#fff;border:1px solid var(--line);border-radius:8px;box-shadow:0 4px 16px rgba(12,23,38,.035)}table{width:100%;border-collapse:collapse;min-width:980px}th{text-align:left;padding:13px 15px;background:#eaf0ee;color:#4d5d67;text-transform:uppercase;letter-spacing:.08em;font-size:.65rem;white-space:nowrap}td{padding:16px 15px;border-top:1px solid #e6ebeb;vertical-align:top}tbody tr:hover{background:#fafcfb}td strong{display:block}td small{display:block;color:var(--muted);font-size:.7rem;margin-top:3px}.at{display:inline-block;color:var(--muted);font-size:.68rem;margin:3px 0}.odds{font-weight:800;color:var(--navy);font-variant-numeric:tabular-nums}.grade{display:inline-block;padding:3px 8px;border-radius:20px;font-size:.66rem;font-weight:800;letter-spacing:.05em;text-transform:uppercase}.grade-high{background:#e1f5c2;color:#385d0c}.grade-medium{background:#e0ece8;color:#25645b}.grade-low{background:#eceff1;color:#65717a}.no-selection{color:var(--muted);font-style:italic}.external{font-size:.7em;margin-left:3px}.evidence{margin-top:8px;min-width:150px}.evidence summary{cursor:pointer;color:var(--muted);font-size:.7rem}.evidence-body{position:relative;max-width:330px;padding-top:10px;font-size:.76rem;color:var(--muted)}.evidence-body ul{padding-left:17px}.source-list li{margin-bottom:8px}.source-list span{display:block}.flag-box{border-left:2px solid #c68a26;padding-left:10px;margin:10px 0}.blank-value{background:#fcfaf5}.flag-icon{display:inline-grid;place-items:center;width:17px;height:17px;border:1px solid #bd8327;border-radius:50%;color:#956015;font-size:.65rem;font-weight:800}.sport-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.sport-card{background:#fff;border:1px solid var(--line);border-radius:8px;padding:23px;color:var(--ink);text-decoration:none;transition:transform .15s,box-shadow .15s}.sport-card:hover{transform:translateY(-2px);box-shadow:var(--shadow)}.sport-card>div{display:flex;justify-content:space-between}.sport-index{color:#91a09f;font-size:.72rem;font-weight:700}.sport-card h3{margin:22px 0 8px}.sport-card p{color:var(--muted);font-size:.82rem}.card-link{color:var(--teal);font-size:.78rem;font-weight:750}.method-callout{background:#dfe9e3;border-radius:10px;padding:35px;display:flex;justify-content:space-between;gap:35px;align-items:center}.method-callout p{max-width:760px;margin:0}.page-hero{padding:65px 0 25px;max-width:920px}.page-hero h1{font-size:clamp(2.7rem,5vw,4.8rem);margin-bottom:22px}.page-hero p{color:var(--muted);font-size:1.05rem;max-width:780px}.directory-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}.directory-card{background:#fff;border:1px solid var(--line);padding:25px;border-radius:8px}.directory-title{display:flex;align-items:center;gap:15px}.directory-title>span{color:#91a09f;font-size:.75rem}.directory-title h2{margin:0;font-size:1.6rem}.directory-card p{color:var(--muted)}.directory-links{display:flex;gap:15px;flex-wrap:wrap;font-size:.76rem}.directory-links a:first-child{font-weight:800}.sport-hero{margin:0 -36px;padding:60px 36px;background:var(--navy);color:#fff;display:flex;justify-content:space-between;gap:40px;align-items:center}.sport-hero h1{font-size:clamp(3rem,6vw,5rem);margin-bottom:18px}.sport-hero p{color:#b7c5cf;max-width:760px}.sport-score{min-width:210px;border-left:1px solid #3a4a5b;padding-left:35px}.sport-score>span{color:#9baebf;text-transform:uppercase;font-size:.68rem;letter-spacing:.1em}.sport-score>strong{display:block;font-size:4.5rem;color:var(--lime);line-height:1.2}.sport-score>strong small{font-size:1.5rem;color:#fff}.source-callout{background:#e5ece8;border-left:4px solid var(--teal);padding:25px 30px}.source-callout p{max-width:900px}.empty-state{padding:30px;background:#fff;border:1px dashed #b9c5c3;border-radius:8px}.empty-state p{margin:7px 0 0;color:var(--muted)}.review-hero{border-bottom:1px solid var(--line)}.review-summary{display:grid;grid-template-columns:repeat(3,1fr);gap:15px;margin-bottom:22px}.review-summary div{background:#fff;border:1px solid var(--line);padding:20px}.review-summary strong,.review-summary span{display:block}.review-summary strong{font-size:2rem}.review-summary span{color:var(--muted)}.review-type{text-transform:uppercase;font-size:.64rem;letter-spacing:.08em;color:var(--amber);font-weight:800}.method-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}.method-grid article{background:#fff;border:1px solid var(--line);border-radius:8px;padding:28px}.method-grid h2{font-size:1.55rem}.method-number{color:var(--teal);font-size:.72rem;font-weight:800;letter-spacing:.1em}.gate-list li{margin:8px 0}footer{background:var(--navy);color:#aebdc9;padding:35px;display:flex;justify-content:space-between;gap:30px;align-items:center}footer strong{color:#fff}footer p{max-width:900px;margin:5px 0 0;font-size:.8rem}footer a{color:var(--lime);white-space:nowrap;font-size:.8rem}
@media(max-width:980px){.header-inner{padding:18px 22px;align-items:flex-start}.header-inner nav{gap:14px}.snapshot>div{padding:9px 22px}main{padding:0 22px 50px}.hero,.sport-hero{margin:0 -22px;padding:55px 22px;grid-template-columns:1fr}.hero{gap:35px}.hero-panel{max-width:480px}.metric-strip{grid-template-columns:repeat(2,1fr)}.metric-strip div:nth-child(2){border-right:0}.metric-strip div:nth-child(-n+2){border-bottom:1px solid var(--line)}.high-grid,.sport-grid,.method-grid{grid-template-columns:1fr}.sport-grid{grid-template-columns:repeat(2,1fr)}.directory-grid{grid-template-columns:1fr}.sport-hero{display:flex;flex-direction:column;align-items:flex-start}.sport-score{border-left:0;border-top:1px solid #3a4a5b;padding:20px 0 0}.method-callout{align-items:flex-start;flex-direction:column}}
@media(max-width:620px){.header-inner{flex-direction:column}.snapshot-note{display:block;margin:4px 0 0}.hero h1{font-size:3rem}.metric-strip{grid-template-columns:1fr}.metric-strip div{border-right:0;border-bottom:1px solid var(--line)}.sport-grid{grid-template-columns:1fr}.price-line{gap:10px}.price-line strong{font-size:1.05rem}.card-foot,.high-top{flex-direction:column}.review-summary{grid-template-columns:1fr}footer{flex-direction:column;align-items:flex-start}section{margin:48px 0}.page-hero{padding-top:40px}}
@media print{.site-header,.snapshot,footer,.hero-actions,.evidence{display:none}body{background:#fff}main{max-width:none;padding:0}.hero,.sport-hero{background:#fff;color:#000;margin:0;padding:20px 0}.hero-copy>p,.sport-hero p{color:#333}.hero h1 em,.kicker{color:#333}.high-card{box-shadow:none;background:#fff;color:#000;border:1px solid #999}.prediction,.high-top,.card-foot{color:#333}.table-wrap{box-shadow:none}section{break-inside:avoid}}
'''
(SITE / "styles.css").write_text(CSS, encoding="utf-8")

print(json.dumps(manifest, indent=2))
