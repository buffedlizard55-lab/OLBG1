#!/usr/bin/env python3
"""Build the 9e041d28 desk: data exports and a self-contained static site.

Run from the repository root:

    python3 scripts/s9e041d28_build.py

Writes data/9e041d28/*.json and desk/**. Never touches another session's files.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import s9e041d28_data as D
import s9e041d28_model as M

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "desk")
DATA = os.path.join(ROOT, "data", "9e041d28")

PICK_SIDE = {"B1": "home", "B2": "home", "B3": "home",
             "N1": "home", "N2": "away", "N3": "away", "N4": "home", "N5": "home"}

SPORT_NAME = {slug: name for slug, name, _sid, _olbg in D.SPORTS}
SPORT_ID = {slug: sid for slug, _n, sid, _o in D.SPORTS}
SPORT_OLBG = {slug: olbg for slug, _n, _s, olbg in D.SPORTS}


MONTHS = {"01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun",
          "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"}


def dt(iso: str) -> str:
    """'2026-10-25T00:00:00Z' -> '25 Oct 00:00 UTC'."""
    return f"{int(iso[8:10])} {MONTHS[iso[5:7]]} {iso[11:16]} UTC"


def plural(n: int, one: str, many: str) -> str:
    return one if n == 1 else many


def fmt_american(a: int) -> str:
    if a == -100:          # exactly 50%: show the coin flip the way a board does
        return "+100"
    return f"+{a}" if a > 0 else str(a)


def fmt_dec(d: float) -> str:
    return f"{d:.2f}"


def build_fixture(fx: dict) -> dict:
    """Turn one sourced fixture into markets, prices and a labelled pick."""
    league = fx["league"]
    if league == "mlb":
        p_home, p_away = M.moneyline_two_way(fx["sport_home_rate"], fx["sport_away_rate"])
        lam_home = M.expected_runs(fx["home_runs_for"], fx["away_runs_against"])
        lam_away = M.expected_runs(fx["away_runs_for"], fx["home_runs_against"])
        ml_label = "Moneyline"
        hcp_label = "Run line -1.5 / +1.5"
        unit = "runs"
        rate_note = ("Venue-split log5: Milwaukee's home win rate against Tampa Bay's road win rate "
                     "in Game 2, then reversed. No invented home-field constant.")
    else:
        p_home, p_away = M.moneyline_two_way(fx["home_win_rate"], fx["away_win_rate"])
        lam_home = M.expected_runs(fx["home_gf"], fx["away_ga"])
        lam_away = M.expected_runs(fx["away_gf"], fx["home_ga"])
        ml_label = "Moneyline (wins incl. overtime and shootout)"
        hcp_label = "Puck line -1.5 / +1.5"
        unit = "goals"
        rate_note = ("log5 on the regulation-plus-overtime win percentage the NHL publishes for "
                     "each club, so a shootout result cannot inflate a side.")

    grid = M.poisson_grid(lam_home, lam_away)
    best = M.best_total(lam_home, lam_away, fx["total_candidates"])
    cover, not_cover = M.handicap(grid, fx["handicap"])

    markets = [
        {"market": ml_label,
         "outcomes": [{"selection": fx["home"], "prob": p_home},
                      {"selection": fx["away"], "prob": p_away}],
         "why": rate_note},
        {"market": hcp_label,
         "outcomes": [{"selection": f"{fx['home']} -1.5", "prob": cover},
                      {"selection": f"{fx['away']} +1.5", "prob": not_cover}],
         "why": "Read off the same independent score grid: the home side must win by two or more."},
        {"market": f"Total {best['line']} {unit}",
         "outcomes": [{"selection": f"Over {best['line']}", "prob": best["over"]},
                      {"selection": f"Under {best['line']}", "prob": best["under"]}],
         "why": (f"Independent Poisson with a home mean of {lam_home:.2f} and an away mean of "
                 f"{lam_away:.2f}; the line closest to a 50/50 split is the one published.")},
    ]
    for mk in markets:
        for o in mk["outcomes"]:
            o["decimal"] = M.decimal_from_prob(o["prob"])
            o["american"] = M.american_from_prob(o["prob"])
            o["in_band"] = M.in_price_band(o["prob"])
            o["american_str"] = fmt_american(o["american"])
            o["decimal_str"] = fmt_dec(o["decimal"])

    side = PICK_SIDE[fx["id"]]
    p = p_home if side == "home" else p_away
    team = fx["home"] if side == "home" else fx["away"]
    band = M.in_price_band(p)
    availability = bool(fx["injuries"].strip())

    label = M.confidence_label(p, True)
    notes = []
    if not band:
        notes.append(f"Fair price {fmt_american(M.american_from_prob(p))} is outside the brief's "
                     "-250 to +10000 window")
    if not availability:
        notes.append("No official availability report was published")
    if league == "mlb" and not fx["probables"]:
        notes.append("Starters had not been published")
    if notes and label in ("high", "medium"):
        label = "medium"

    fx = dict(fx)
    fx["markets"] = markets
    fx["expected"] = {"home": round(lam_home, 2), "away": round(lam_away, 2),
                      "total": round(lam_home + lam_away, 2), "line": best["line"],
                      "unit": unit}
    fx["pick"] = {
        "team": team,
        "side": side,
        "prob": p,
        "decimal": M.decimal_from_prob(p),
        "american": M.american_from_prob(p),
        "american_str": fmt_american(M.american_from_prob(p)),
        "decimal_str": fmt_dec(M.decimal_from_prob(p)),
        "confidence": label,
        "in_band": band,
        "notes": notes,
        "market": ml_label,
        "prediction": D.WRITEUPS[fx["id"]],
        "words": len(D.WRITEUPS[fx["id"]].split()),
    }
    return fx


FIXTURES = [build_fixture(f) for f in D.FIXTURES]
PICKS = [f for f in FIXTURES if "pick" in f]

CONF_RANK = {"high": 0, "medium": 1, "low": 2}


def counts() -> dict:
    by = {}
    for p in PICKS:
        by[p["pick"]["confidence"]] = by.get(p["pick"]["confidence"], 0) + 1
    per_sport = {}
    for f in FIXTURES:
        per_sport[f["sport"]] = per_sport.get(f["sport"], 0) + 1
    markets = sum(len(f["markets"]) for f in FIXTURES)
    outcomes = sum(len(m["outcomes"]) for f in FIXTURES for m in f["markets"])
    return {
        "snapshot": D.SNAPSHOT_UTC,
        "sports_covered": len(D.SPORTS),
        "fixtures": len(FIXTURES),
        "picks": len(PICKS),
        "high": by.get("high", 0),
        "medium": by.get("medium", 0),
        "low": by.get("low", 0),
        "markets": markets,
        "outcomes": outcomes,
        "olbg_rows": len(D.OLBG_INVENTORY),
        "flags": len(D.FLAGS),
        "sources": len(D.SOURCES),
        "in_band": sum(1 for p in PICKS if p["pick"]["in_band"]),
        "per_sport": per_sport,
        "min_words": min(p["pick"]["words"] for p in PICKS),
    }


C = counts()


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------
def nav(active: str, pfx: str = "") -> str:
    items = [
        ("index", "Overview", "index.html"),
        ("picks", "Today's picks", "picks.html"),
        ("matches", "Matches", "matches.html"),
        ("markets", "Prices", "markets.html"),
        ("predictions", "Predictions", "predictions.html"),
        ("sports", "Sports", "sports.html"),
        ("flagged", "Flagged for review", "flagged.html"),
        ("repo", "Repo review", "repo-review.html"),
        ("sources", "Sources", "sources.html"),
        ("method", "Method", "methodology.html"),
        ("olbg", "OLBG structure", "olbg.html"),
    ]
    out = []
    for key, label, href in items:
        cls = "nav-link active" if key == active else "nav-link"
        cur = ' aria-current="page"' if key == active else ""
        out.append(f'<a class="{cls}" href="{pfx}{href}"{cur}>{label}</a>')
    return "".join(out)


def page(title: str, active: str, body: str, subtitle: str = "", pfx: str = "") -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · OLBG research desk</title>
<meta name="description" content="Source-linked match research with originated lines and explicit coverage gaps. Not affiliated with OLBG.">
<link rel="stylesheet" href="{pfx}assets/desk.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="topbar">
  <a class="brand" href="{pfx}index.html"><span class="brand-mark">OLBG</span><span class="brand-sub">research desk</span></a>
  <nav class="nav" aria-label="Primary">{nav(active, pfx)}</nav>
  <div class="stamp"><span class="live-dot"></span>Snapshot {D.SNAPSHOT_UTC}</div>
</header>
<main id="main">
{body}
</main>
<footer class="foot">
  <p><strong>What this is.</strong> Independently calculated experimental prices, not bookmaker offers. No staking advice, no guaranteed returns. Not affiliated with OLBG.</p>
  <p><strong>How to read a blank.</strong> A blank cell means the official source did not publish that value and it was not filled in. Every blank is listed on the <a href="{pfx}flagged.html">Flagged for review</a> page.</p>
  <p class="mono">Desk session 9e041d28-olbg1 · snapshot {D.SNAPSHOT_UTC} · {C['fixtures']} sourced fixtures · {C['picks']} picks · {C['flags']} flags</p>
</footer>
</body>
</html>
"""


def chip(conf: str) -> str:
    return f'<span class="chip chip-{conf}">{conf.title()}</span>'


def pick_table(rows, show_sport=True, link=True) -> str:
    head = '<tr><th>Sport</th><th>Match</th><th>Start (UTC)</th><th>Selection</th><th>Market</th><th>Fair price</th><th>Chance</th><th>Confidence</th><th>Official source</th></tr>' if show_sport else \
           '<tr><th>Match</th><th>Start (UTC)</th><th>Selection</th><th>Market</th><th>Fair price</th><th>Chance</th><th>Confidence</th><th>Official source</th></tr>'
    body = []
    for f in rows:
        p = f["pick"]
        cells = []
        if show_sport:
            cells.append(f'<td><a href="sports/{f["sport"]}.html">{SPORT_NAME[f["sport"]]}</a></td>')
        cells.append(f'<td class="match"><a href="matches.html#fx-{f["id"]}">{f["event"]}</a>'
                     f'<span class="sub">{f["competition"]}</span></td>')
        cells.append(f'<td class="mono">{f["start_utc"].replace("T", " ").replace("Z", "")}</td>')
        cells.append(f'<td class="sel"><strong>{p["team"]}</strong><span class="sub">{p["market"]}</span></td>')
        cells.append(f'<td>{p["market"]}</td>')
        cells.append(f'<td class="mono">{p["american_str"]} <span class="sub">({p["decimal_str"]})</span></td>')
        cells.append(f'<td class="mono">{p["prob"]*100:.1f}%</td>')
        cells.append(f'<td>{chip(p["confidence"])}</td>')
        cells.append(f'<td class="src"><a href="{f["official_url"]}" rel="noopener" target="_blank">Official</a>'
                     f'<a href="sources.html" class="sub">log</a></td>')
        body.append("<tr>" + "".join(cells) + "</tr>")
    return f'<div class="table-wrap"><table class="desk">{head}{"".join(body)}</table></div>'


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
def write(path: str, html: str) -> None:
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(html)


def page_index() -> str:
    highs = [p for p in PICKS if p["pick"]["confidence"] == "high"]
    highs.sort(key=lambda f: -f["pick"]["prob"])
    med = [p for p in PICKS if p["pick"]["confidence"] == "medium"]
    low = [p for p in PICKS if p["pick"]["confidence"] == "low"]
    top = highs + med + low
    lead = top[0]

    kpis = f"""
<section class="kpis">
  <div class="kpi"><span class="kpi-n">{C['fixtures']}</span><span class="kpi-l">sourced fixtures<br><em>official feed confirmed</em></span></div>
  <div class="kpi accent"><span class="kpi-n">{C['high']}</span><span class="kpi-l">high-confidence {plural(C["high"], "pick", "picks")}<br><em>inside -250 to +10000</em></span></div>
  <div class="kpi"><span class="kpi-n">{C['medium']}</span><span class="kpi-l">medium {plural(C["medium"], "pick", "picks")}<br><em>published with reasons</em></span></div>
  <div class="kpi"><span class="kpi-n">{C['markets']}</span><span class="kpi-l">markets originated<br><em>{C['outcomes']} priced outcomes</em></span></div>
  <div class="kpi"><span class="kpi-n">{C['olbg_rows']}</span><span class="kpi-l">OLBG listings captured<br><em>watchlist, unpriced</em></span></div>
  <div class="kpi warn"><span class="kpi-n">{C['flags']}</span><span class="kpi-l">flagged for review<br><em>blank beats invented</em></span></div>
</section>"""

    exec_rows = "".join(
        f"""<tr>
        <td>{chip(p['pick']['confidence'])}</td>
        <td class="match"><a href="matches.html#fx-{p['id']}">{p['event']}</a><span class="sub">{SPORT_NAME[p['sport']]} · {p['competition']}</span></td>
        <td class="sel"><strong>{p['pick']['team']}</strong><span class="sub">{p['pick']['market']}</span></td>
        <td class="mono">{p['pick']['american_str']}</td>
        <td class="mono">{p['pick']['prob']*100:.1f}%</td>
        <td class="mono">{dt(p['start_utc'])}</td>
        <td class="src"><a href="{p['official_url']}" target="_blank" rel="noopener">Source</a> · <a href="predictions.html#w-{p['id']}">Read</a></td>
        </tr>""" for p in top)

    sport_cards = []
    for slug, name, sid, olbg in D.SPORTS:
        n = C["per_sport"].get(slug, 0)
        picks_n = len([p for p in PICKS if p["sport"] == slug])
        olbg_n = len([r for r in D.OLBG_INVENTORY if r[0] == slug])
        state = "priced" if picks_n else ("listed only" if olbg_n else "nothing listed")
        cls = "ok" if picks_n else ("mid" if olbg_n else "bad")
        sport_cards.append(
            f'<a class="sport-card {cls}" href="sports/{slug}.html">'
            f'<span class="sport-name">{name}</span>'
            f'<span class="sport-nums"><strong>{picks_n}</strong> picks · <strong>{n}</strong> sourced · <strong>{olbg_n}</strong> OLBG</span>'
            f'<span class="sport-state">{state}</span></a>')

    body = f"""
<div class="hero">
  <p class="eyebrow">Executive summary · {D.SNAPSHOT_UTC}</p>
  <h1>{C['high']} High pick, {C['medium']} Medium, {C['low']} Low — from the {C['fixtures']} fixtures we could prove.</h1>
  <p class="lede"><strong>Top selection: {lead['pick']['team']} on the moneyline at a fair {lead['pick']['american_str']} ({lead['pick']['prob']*100:.1f}%) — {lead['event']}, {lead['competition']}.</strong> Everything below is in confidence order, and every number traces to a league feed linked in the row. Prices are our own zero-vig estimates, never a bookmaker quote, and a blank is always deliberate.</p>
</div>
{kpis}

<section class="panel">
  <div class="panel-head">
    <h2>Today's picks, highest confidence first</h2>
    <p>One row per priced fixture. The selection column is the bet; the confidence column says how much weight the evidence carries.</p>
  </div>
  <div class="table-wrap"><table class="desk">
    <tr><th>Confidence</th><th>Match</th><th>Selection</th><th>Fair price</th><th>Chance</th><th>Start (UTC)</th><th>Evidence</th></tr>
    {exec_rows}
  </table></div>
  <p class="note">Fair prices are <span class="mono">1 ÷ probability</span> with no margin. American odds are derived from the same number. {"All High picks sit inside the brief's −250 to +10000 window." if C['in_band'] >= C['high'] else "One or more High picks sit outside the band and are labelled Medium."}</p>
</section>

<section class="panel">
  <div class="panel-head"><h2>Where each sport stands</h2>
  <p>Click any sport for its fixtures, prices and gaps. A sport with zero picks is there on purpose, with the reason on its page.</p></div>
  <div class="sport-grid">{"".join(sport_cards)}</div>
</section>

<section class="panel two-col">
  <div>
    <h2>Why {C['picks']} picks, not 75</h2>
    <p>The brief asks for five picks a day in each of fifteen sports. That requires five fixtures per sport that are <em>both</em> confirmed by a governing body <em>and</em> carry enough official form data to price. This session confirmed {C['fixtures']} such fixtures across two sports; every other OLBG row is a listing we could not prove, so it sits on the <a href="matches.html#watchlist">watchlist</a> with no price attached.</p>
    <p>We did not fill the gap with invented form, assumed line-ups or a favourite's short price dressed up as confidence. The alternative would be a full-looking table and a worthless one.</p>
    <p><a class="button" href="methodology.html">How prices and confidence are set</a></p>
  </div>
  <div class="callout">
    <h3>What is blocked, and why</h3>
    <ul class="tight">
      <li><strong>Golf</strong> — OLBG returned no event at all.</li>
      <li><strong>Rugby League</strong> — OLBG shows 2027 outrights only.</li>
      <li><strong>Darts</strong> — PDC schedule sat behind a consent wall.</li>
      <li><strong>Handball, Volleyball</strong> — league sites served reCAPTCHA or navigation only.</li>
      <li><strong>Basketball</strong> — two-game samples; no honest line exists yet.</li>
      <li><strong>Ice hockey availability</strong> — the NHL roster feed carries no injury status, so only the baseball rows clear the availability gate.</li>
    </ul>
    <p class="small">All of it is on <a href="flagged.html">Flagged for review</a> with the exact URL that failed.</p>
  </div>
</section>

<section class="panel">
  <div class="panel-head"><h2>How to use the desk in 20 seconds</h2></div>
  <ol class="steps">
    <li><strong>Executive summary</strong> — the table above. Confidence first, selection second, evidence link last.</li>
    <li><strong><a href="matches.html">Matches</a></strong> — every fixture we proved, then every OLBG row we did not. The two tables are never mixed.</li>
    <li><strong><a href="markets.html">Prices</a></strong> — moneyline, handicap and total for each proved fixture, with the arithmetic shown.</li>
    <li><strong><a href="predictions.html">Predictions</a></strong> — the written case for each pick, quoting only sourced numbers.</li>
    <li><strong><a href="flagged.html">Flagged</a></strong> — every blank, every failed fetch, every shortfall.</li>
  </ol>
</section>
"""
    return page("Overview", "index", body)


def page_picks() -> str:
    rows = sorted(PICKS, key=lambda f: (CONF_RANK[f["pick"]["confidence"]], -f["pick"]["prob"]))
    table = pick_table(rows)
    detail = []
    for f in rows:
        p = f["pick"]
        detail.append(f"""
<article class="pick-card" id="p-{f['id']}">
  <header>
    <div><span class="eyebrow">{SPORT_NAME[f['sport']]} · {f['competition']}</span>
    <h3>{f['event']}</h3></div>
    {chip(p['confidence'])}
  </header>
  <div class="pick-facts">
    <div><span class="lbl">Selection</span><span class="val">{p['team']}</span></div>
    <div><span class="lbl">Market</span><span class="val">{p['market']}</span></div>
    <div><span class="lbl">Fair price</span><span class="val mono">{p['american_str']} / {p['decimal_str']}</span></div>
    <div><span class="lbl">Fair chance</span><span class="val mono">{p['prob']*100:.1f}%</span></div>
    <div><span class="lbl">Start (UTC)</span><span class="val mono">{dt(f['start_utc'])}</span></div>
    <div><span class="lbl">Venue</span><span class="val">{f['venue']}</span></div>
  </div>
  <p class="pred">{p['prediction']}</p>
  <p class="src-line">Evidence: <a href="{f['official_url']}" target="_blank" rel="noopener">{f['official']}</a>
  {" · Standings: <a href='" + f["stats_url"] + "' target='_blank' rel='noopener'>official table</a>" if f.get("stats_url") else ""}</p>
  {"".join("<p class='warn-line'>" + n + "</p>" for n in p["notes"])}
</article>""")
    body = f"""
<div class="hero small">
  <p class="eyebrow">Picks</p>
  <h1>{C['picks']} picks from {C['fixtures']} proved fixtures</h1>
  <p class="lede">{C['high']} High, {C['medium']} Medium, {C['low']} Low. A pick exists only where a governing body confirmed the fixture and supplied the form inputs.</p>
</div>
<section class="panel">
  <div class="panel-head"><h2>All picks</h2><p>Sorted by confidence, then by fair probability.</p></div>
  {table}
</section>
<section class="panel">
  <div class="panel-head"><h2>Each pick in full</h2><p>Every number quoted below appears in the fixture row on <a href="matches.html">Matches</a>.</p></div>
  {"".join(detail)}
</section>
"""
    return page("Picks", "picks", body)


def page_matches() -> str:
    rows = []
    for f in FIXTURES:
        p = f["pick"]
        blanks = ", ".join(f["blank"]) if f["blank"] else "none"
        rows.append(f"""
<tr id="fx-{f['id']}">
  <td><a href="sports/{f['sport']}.html">{SPORT_NAME[f['sport']]}</a></td>
  <td class="match"><strong>{f['event']}</strong><span class="sub">{f['competition']} · {f['venue']}</span></td>
  <td class="mono">{dt(f['start_utc'])}</td>
  <td>{f['home_record']}<span class="sub">{f['home']}</span></td>
  <td>{f['away_record']}<span class="sub">{f['away']}</span></td>
  <td>{chip(p['confidence'])}<span class="sub">{p['team']}</span></td>
  <td class="src"><a href="{f['official_url']}" target="_blank" rel="noopener">Official</a><span class="sub">{f['olbg_label']}</span></td>
  <td class="blank">{blanks}</td>
</tr>""")

    proved = {f["id"] for f in FIXTURES}
    wl = []
    wl_rows = [r for r in D.OLBG_INVENTORY if r[4] not in proved]
    for sport, event, comp, when, linked, url in wl_rows:
        wl.append(f"""
<tr>
  <td><a href="sports/{sport}.html">{SPORT_NAME.get(sport, sport)}</a></td>
  <td class="match">{event}{f'<span class="sub">{comp}</span>' if comp else ''}</td>
  <td class="mono">{when}</td>
  <td><a href="{url}" target="_blank" rel="noopener">OLBG listing</a></td>
  <td class="blank">Governing-body confirmation not obtained this session — no price issued</td>
</tr>""")

    body = f"""
<div class="hero small">
  <p class="eyebrow">Matches</p>
  <h1>Proved fixtures first. OLBG listings second. Never mixed.</h1>
  <p class="lede">The first table is what we can defend: a governing body published the fixture and the inputs. The second table is what OLBG advertised, kept for completeness and clearly marked unpriced.</p>
</div>

<section class="panel">
  <div class="panel-head"><h2>{C['fixtures']} proved fixtures</h2>
  <p>Start times are the official UTC values. The OLBG clock label is shown underneath, verbatim, because it is not UTC.</p></div>
  <div class="table-wrap"><table class="desk">
    <tr><th>Sport</th><th>Match</th><th>Start (UTC)</th><th>Home record</th><th>Away record</th><th>Pick</th><th>Official source</th><th>Blank / flagged</th></tr>
    {"".join(rows)}
  </table></div>
</section>

<section class="panel" id="watchlist">
  <div class="panel-head"><h2>{len(wl_rows)} OLBG listings without governing-body confirmation</h2>
  <p>These are real rows on OLBG: the event, competition and clock text are copied from the public hub. They are <strong>not</strong> priced, because no official fixture confirmation or form input was obtained. The link goes to the OLBG page so you can check the row yourself.</p></div>
  <div class="table-wrap"><table class="desk">
    <tr><th>Sport</th><th>Event as OLBG labels it</th><th>OLBG clock (unlabelled)</th><th>Discovery link</th><th>Why no price</th></tr>
    {"".join(wl)}
  </table></div>
  <p class="note">{C['olbg_rows'] - len(wl_rows)} of the {C['olbg_rows']} captured listing rows is the World Series Game 2 card, and it appears in the proved table above rather than here. <strong>Golf and Rugby League have no rows at all.</strong> Golf returned “No tips found”; Rugby League showed only 2027 outright markets. Both are on <a href="flagged.html">Flagged for review</a>.</p>
</section>
"""
    return page("Matches", "matches", body)


def page_markets() -> str:
    blocks = []
    for f in FIXTURES:
        mrows = []
        for mk in f["markets"]:
            for o in mk["outcomes"]:
                band = "" if o["in_band"] else '<span class="tag">outside band</span>'
                mrows.append(f'<tr><td>{mk["market"]}</td><td class="sel">{o["selection"]}</td>'
                             f'<td class="mono">{o["prob"]*100:.1f}%</td>'
                             f'<td class="mono">{o["american_str"]}</td>'
                             f'<td class="mono">{fmt_dec(o["decimal"])}</td><td>{band}</td></tr>')
        arts = "".join(f'<p class="calc"><strong>{mk["market"]}</strong> — {mk["why"]}</p>' for mk in f["markets"])
        blocks.append(f"""
<article class="fx-block" id="m-{f['id']}">
  <header><h3>{f['event']}</h3><span class="mono">{dt(f['start_utc'])}</span></header>
  <p class="sub">{f['competition']} · expected {f['expected']['unit']}: home {f['expected']['home']}, away {f['expected']['away']}, combined {f['expected']['total']} → published line {f['expected']['line']}</p>
  <div class="table-wrap"><table class="desk">
    <tr><th>Market</th><th>Selection</th><th>Fair chance</th><th>American</th><th>Decimal</th><th>Band</th></tr>
    {"".join(mrows)}
  </table></div>
  {arts}
</article>""")
    body = f"""
<div class="hero small">
  <p class="eyebrow">Prices</p>
  <h1>{C['markets']} markets, {C['outcomes']} priced outcomes, zero margin</h1>
  <p class="lede">Moneyline, handicap and total for every proved fixture. These are our own estimates. They are not available bookmaker prices and no availability claim is made.</p>
</div>
<section class="panel">
  <p class="note"><strong>The band rule.</strong> The brief restricts High picks to fair prices between −250 and +10000. Rows outside it are still published for completeness and marked. A market can look attractive and still be excluded from the High tier.</p>
  {"".join(blocks)}
</section>
"""
    return page("Prices", "markets", body)


def page_predictions() -> str:
    arts = []
    for f in sorted(PICKS, key=lambda x: (CONF_RANK[x["pick"]["confidence"]], -x["pick"]["prob"])):
        p = f["pick"]
        arts.append(f"""
<article class="writeup" id="w-{f['id']}">
  <div class="writeup-head">
    <div>
      <p class="eyebrow">{SPORT_NAME[f['sport']]} · {f['competition']}</p>
      <h2>{f['event']}</h2>
      <p class="selection">Selection: <strong>{p['team']}</strong> · {p['market']} · fair {p['american_str']} ({p['decimal_str']}) · {p['prob']*100:.1f}% · {chip(p['confidence'])} · {p['words']} words</p>
    </div>
  </div>
  <p class="pred big">{p['prediction']}</p>
  <dl class="inputs">
    <dt>Current form</dt><dd>{f['form']}</dd>
    <dt>Match statistics</dt><dd>{f['stats']}</dd>
    <dt>Line-ups / starters</dt><dd>{f['probables'] or '<span class="blank">Not published by the official source read</span>'}</dd>
    <dt>Availability / injuries</dt><dd>{f['injuries'] or '<span class="blank">Not published by the official source read — no claim made</span>'}</dd>
    <dt>Series context</dt><dd>{f['series']}</dd>
  </dl>
  <p class="src-line">Official source: <a href="{f['official_url']}" target="_blank" rel="noopener">{f['official']}</a>
  {f' · Standings: <a href="{f["stats_url"]}" target="_blank" rel="noopener">table</a>' if f.get('stats_url') else ''}</p>
</article>""")
    body = f"""
<div class="hero small">
  <p class="eyebrow">Predictions</p>
  <h1>{C['picks']} written picks, each traceable to one official URL</h1>
  <p class="lede">Minimum length {C['min_words']} words. No two share a sentence. Every figure quoted was read from the source linked at the foot of its card.</p>
</div>
<section class="panel">
  {"".join(arts)}
</section>
"""
    return page("Predictions", "predictions", body)


def page_sports() -> str:
    cards = []
    for slug, name, sid, olbg in D.SPORTS:
        n = C["per_sport"].get(slug, 0)
        picks_n = len([p for p in PICKS if p["sport"] == slug])
        olbg_n = len([r for r in D.OLBG_INVENTORY if r[0] == slug])
        note = D.NOT_LISTED.get(slug, "")
        cards.append(f"""
<a class="sport-row" href="sports/{slug}.html">
  <span class="sport-name">{name}<span class="sub">OLBG sport id {sid}</span></span>
  <span class="sport-stats"><strong>{picks_n}</strong> picks · <strong>{n}</strong> proved fixtures · <strong>{olbg_n}</strong> OLBG listings</span>
  <span class="sport-note">{note or "Open for fixtures, prices and gaps"}</span>
</a>""")
    body = f"""
<div class="hero small"><p class="eyebrow">Sports</p><h1>The 15 sports in the brief</h1>
<p class="lede">Each page separates proved fixtures from OLBG listings and states exactly what is missing.</p></div>
<section class="panel"><div class="sport-list">{"".join(cards)}</div></section>
"""
    return page("Sports", "sports", body)


def page_sport(slug: str, name: str, sid: int, olbg: str) -> str:
    fx = [f for f in FIXTURES if f["sport"] == slug]
    proved = {f["id"] for f in FIXTURES}
    ol = [r for r in D.OLBG_INVENTORY if r[0] == slug and r[4] not in proved]
    rows = []
    for f in fx:
        p = f["pick"]
        rows.append(f"""<tr>
        <td class="match"><a href="../matches.html#fx-{f['id']}">{f['event']}</a><span class="sub">{f['competition']}</span></td>
        <td class="mono">{dt(f['start_utc'])}</td>
        <td class="sel">{p['team']}<span class="sub">{p['market']}</span></td>
        <td class="mono">{p['american_str']}</td><td class="mono">{p['prob']*100:.1f}%</td>
        <td>{chip(p['confidence'])}</td>
        <td class="src"><a href="{f['official_url']}" target="_blank" rel="noopener">Official</a> · <a href="../predictions.html#w-{f['id']}">Write-up</a></td></tr>""")
    wl = "".join(f"""<tr><td class="match">{event}{f'<span class="sub">{comp}</span>' if comp else ''}</td>
        <td class="mono">{when}</td><td><a href="{url}" target="_blank" rel="noopener">OLBG</a></td>
        <td class="blank">unconfirmed — no price</td></tr>""" for _s, event, comp, when, _l, url in ol)
    note = D.NOT_LISTED.get(slug, "")
    flag_list = [fl for fl in D.FLAGS if name.lower().split()[0] in fl["title"].lower() or slug.split("-")[0] in fl["title"].lower()]
    flags_html = "".join(f'<li><a href="../flagged.html#{fl["id"]}">{fl["id"]}</a> — {fl["title"]}</li>' for fl in flag_list)
    body = f"""
<div class="hero small">
  <p class="eyebrow"><a href="../sports.html">Sports</a> / {name}</p>
  <h1>{name}</h1>
  <p class="lede">{len(fx)} proved fixtures · {len(fx)} picks · {len(ol)} unpriced OLBG listings. OLBG hub: <a href="https://www.olbg.com/betting-tips/{olbg}/{sid}" target="_blank" rel="noopener">/{olbg}/{sid}</a>.</p>
</div>
{f'<section class="panel warnbox"><h2>Nothing to price</h2><p>{note}</p></section>' if note else ''}
<section class="panel">
  <div class="panel-head"><h2>Proved fixtures and picks</h2><p>Only rows where a governing body confirmed the fixture and supplied the inputs.</p></div>
  {('<div class="table-wrap"><table class="desk"><tr><th>Match</th><th>Start (UTC)</th><th>Selection</th><th>Fair price</th><th>Chance</th><th>Confidence</th><th>Evidence</th></tr>' + "".join(rows) + '</table></div>') if rows else '<p class="blank">No fixture in this sport satisfied both tests this session.</p>'}
</section>
<section class="panel">
  <div class="panel-head"><h2>OLBG listings (unpriced)</h2><p>Shown so the list is complete. No price is attached to any row here.</p></div>
  {('<div class="table-wrap"><table class="desk"><tr><th>Event as OLBG labels it</th><th>OLBG clock</th><th>Link</th><th>Status</th></tr>' + wl + '</table></div>') if wl else ('<p class="blank">Every OLBG card in this sport was one we could also confirm, so all of them sit in the proved table above. Nothing here is withheld.</p>' if fx else '<p class="blank">No OLBG listing found for this sport at retrieval time.</p>')}
</section>
{f'<section class="panel"><div class="panel-head"><h2>Related flags</h2></div><ul class="tight">{flags_html}</ul></section>' if flags_html else ''}
"""
    return page(name, "sports", body, pfx="../")


def page_flagged() -> str:
    rows = []
    for fl in sorted(D.FLAGS, key=lambda x: {"high": 0, "medium": 1, "low": 2}[x["severity"]]):
        rows.append(f"""<article class="flag" id="{fl['id']}">
        <div class="flag-head"><span class="chip chip-{fl['severity']}">{fl['severity'].title()}</span><span class="mono">{fl['id']}</span></div>
        <h3>{fl['title']}</h3><p>{fl['detail']}</p>
        <p class="src-line">Source checked: <a href="{fl['source']}" target="_blank" rel="noopener">{fl['source']}</a></p></article>""")
    body = f"""
<div class="hero small">
  <p class="eyebrow">Flagged for review</p>
  <h1>{C['flags']} irregularities, each with the URL that produced it</h1>
  <p class="lede">Nothing here blocks publication. Each item is either a value we refused to invent or a source that failed to render. Open the source link and check the claim yourself.</p>
</div>
<section class="panel">{''.join(rows)}</section>
"""
    return page("Flagged for review", "flagged", body)


def page_repo() -> str:
    rows = "".join(f"""<tr><td class="mono">{f['id']}</td><td class="mono">{f['file']}</td>
    <td>{f['finding']}</td><td>{chip(f['severity'])}</td></tr>""" for f in D.REPO_AUDIT)
    body = f"""
<div class="hero small"><p class="eyebrow">Repository review</p><h1>Line-by-line findings in the existing repository</h1>
<p class="lede">Found while reading the tree before adding this desk. Each finding names the file; the numbers were counted in this session, not recalled.</p></div>
<section class="panel">
  <div class="table-wrap"><table class="desk">
    <tr><th>ID</th><th>File</th><th>Finding</th><th>Severity</th></tr>{rows}
  </table></div>
</section>
<section class="panel two-col">
  <div><h2>What we checked</h2>
  <ul class="tight">
    <li>Root landing page freshness labels against <span class="mono">data/current/site-manifest.json</span>.</li>
    <li>README headline counts against the same manifest.</li>
    <li>Cross-desk fixture identifiers for duplicate pricing of one event.</li>
    <li>Published prediction prose for the two words the brief keeps internal.</li>
    <li>Size and merge behaviour of the shared coordination board.</li>
    <li>The publish workflow's ability to prove a deployment from a pull request.</li>
  </ul></div>
  <div><h2>What we did not change</h2>
  <p>No peer desk, canonical pipeline file, root page or workflow was edited. These are findings for the owner, published rather than silently fixed, because the files belong to other sessions' scopes.</p>
  <p class="small">Scope for this session: <span class="mono">desk/**</span>, <span class="mono">data/9e041d28/**</span>, <span class="mono">scripts/s9e041d28_*</span>, <span class="mono">tests/pipeline/test_desk_9e041d28.py</span>, and append-only <span class="mono">COORDINATION.md</span>.</p></div>
</section>
"""
    return page("Repository review", "repo", body)


def page_sources() -> str:
    rows = "".join(f"""<tr><td>{name}</td><td class="src"><a href="{url}" target="_blank" rel="noopener">{url}</a></td>
    <td>{auth}</td><td>{sport}</td><td class="mono">{ts}</td></tr>""" for name, url, auth, sport, ts in D.SOURCES)
    body = f"""
<div class="hero small"><p class="eyebrow">Sources</p><h1>Every URL this desk actually read</h1>
<p class="lede">Observation times are when the page was fetched. A source is listed once, even if it was read in several chunks. "Discovery only" means the page was used to find rows, never to prove a fact.</p></div>
<section class="panel">
  <div class="table-wrap"><table class="desk">
    <tr><th>Source</th><th>URL</th><th>Type</th><th>Sport</th><th>Read at (UTC)</th></tr>{rows}
  </table></div>
</section>
<section class="panel">
  <h2>Sources that failed</h2>
  <ul class="tight">
    <li><span class="mono">https://www.opel-hbl.de/de/hbl/spielplan</span> and <span class="mono">/tabelle</span> — reCAPTCHA in place of content.</li>
    <li><span class="mono">https://www.daikin-hbl.de/de/spielplan/</span> — 404.</li>
    <li><span class="mono">https://www.pdc.tv/tournaments/machineseeker-european-championship</span> — consent wall.</li>
    <li><span class="mono">https://www.legavolley.it/calendario/</span> — navigation only, no fixture table.</li>
    <li><span class="mono">https://www.unitedrugby.com/fixtures</span> — 404; the working route is <span class="mono">stats.unitedrugby.com/match-centre/2026-27/4</span>.</li>
    <li><span class="mono">https://top14.lnr.fr/calendrier</span> — 404; the working route is <span class="mono">/calendrier-et-resultats</span>.</li>
    <li><span class="mono">https://www.premiershiprugby.com/fixtures</span> — 404; the brand now serves <span class="mono">premrugby.com</span>.</li>
    <li><span class="mono">https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json</span> and <span class="mono">stats.nba.com</span> — HTTP 500 / blocked; <span class="mono">nba.com/games</span> was used instead.</li>
  </ul>
</section>
"""
    return page("Sources", "sources", body)


def page_method() -> str:
    body = f"""
<div class="hero small"><p class="eyebrow">Method</p><h1>How a line is made, and what the confidence label means</h1>
<p class="lede">Five rules, applied to every row. If an input is missing the market is withheld rather than guessed.</p></div>
<section class="panel">
  <h2>1. Inputs</h2>
  <p>Only values published by a governing body or league feed. Win rates, goals/runs for and against, home and road splits, and (for baseball) the published probable pitchers. No injury assumption, no line-up guess, no travel or rest adjustment unless the source states it.</p>

  <h2>2. Moneyline</h2>
  <p><strong>Baseball</strong> uses venue-split log5: the home team's home win rate against the away team's away win rate. Log5 is <span class="mono">p = a(1−b) / [a(1−b) + b(1−a)]</span>, so the venue effect is carried by the inputs rather than an invented constant.</p>
  <p><strong>Ice hockey</strong> uses log5 on regulation-plus-overtime win rate (wins ÷ games). Shootout results are excluded because they are close to a coin toss; using points percentage would overstate a team, since an overtime loss still earns a point.</p>

  <h2>3. Totals and handicaps</h2>
  <p>Independent Poisson counts with means built from each side's scoring rate and the opponent's conceding rate: <span class="mono">λ_home = (home scored/game + away conceded/game) / 2</span> and the mirror for the away side. The published total is the half-line closest to a 50/50 split. Handicaps are read off the same score grid. Baseball's tie probability is redistributed across the two winners, which is why the baseball moneyline comes from log5 and the run line from the grid.</p>

  <h2>4. Price</h2>
  <p>Fair decimal is <span class="mono">1 ÷ p</span> with no margin. American odds are derived from the same decimal. These are estimates: no bookmaker is quoted, no availability is implied, and no stake is suggested.</p>

  <h2>5. Confidence</h2>
  <ul class="tight">
    <li><span class="chip chip-high">High</span> complete official inputs, an official availability check, no unresolved conflict, a fair probability of at least 62%, and a price inside −250 to +10000.</li>
    <li><span class="chip chip-medium">Medium</span> complete inputs at 55–62%, or a stronger probability whose price falls outside the brief's band, or a complete price with no official availability report.</li>
    <li><span class="chip chip-low">Low</span> incomplete inputs or a probability below 55%.</li>
  </ul>
  <p>This is deliberately not "the favourite is short". A −400 favourite does not become High by being likely; it becomes excluded by the band and, if it is our pick at all, Medium.</p>

  <h2>6. Expiry</h2>
  <p>A price is valid only before its fixture starts. This build is stamped {D.SNAPSHOT_UTC}; anything already started at that stamp is excluded from the pick tables. The desk is a snapshot, not a live feed.</p>

  <h2>7. What is never done</h2>
  <ul class="tight">
    <li>No value is inferred from a team name, a league table position or a tip percentage.</li>
    <li>OLBG tip shares are votes, not probabilities, and are not used in any calculation.</li>
    <li>No blank is filled to make a table look complete.</li>
  </ul>
</section>
"""
    return page("Method", "method", body)


def page_olbg() -> str:
    rows = "".join(f"<tr><td class='mono'>{sid}</td><td>{name}</td><td class='mono'>/{olbg}/{sid}</td></tr>"
                   for slug, name, sid, olbg in D.SPORTS)
    body = f"""
<div class="hero small"><p class="eyebrow">OLBG structure</p><h1>What the site exposes, and where it misleads</h1>
<p class="lede">Reverse-engineered from the fifteen public sport hubs on 24 October 2026. OLBG is used for discovery only. It is never treated as an official fixture or statistics source.</p></div>
<section class="panel">
  <h2>Routes</h2>
  <p>Every sport follows <span class="mono">/betting-tips/{{Sport_Slug}}/{{sport_id}}</span>. Slugs are case-sensitive; a wrong case returns a soft error with HTTP 200. Event pages add competition and market segments, for example <span class="mono">/betting-tips/Ice_Hockey/NHL/NHL/NY_Rangers_@_OTT_Senators/13?event_id=200008</span>. The <span class="mono">event_id</span> is the stable key and is what this desk records.</p>
  <div class="table-wrap"><table class="desk"><tr><th>Sport id</th><th>Sport</th><th>Canonical route</th></tr>{rows}</table></div>
</section>
<section class="panel">
  <h2>Five behaviours that change what you see</h2>
  <ol class="steps">
    <li><strong>Times are unlabelled and inconsistent.</strong> Baseball rendered "Today 20:00" for a 00:00 UTC start; snooker rendered "Today 14:00" for a 13:00 UTC start. Treat every OLBG clock as an advertisement, not a timestamp.</li>
    <li><strong>Zero-tip fixtures disappear.</strong> OLBG hides events with no open community tips. Rugby League currently shows only 2027 outrights for that reason; it is not evidence that no match exists.</li>
    <li><strong>Hubs truncate.</strong> The default listing stops at twenty rows before "Load More Tips", so a hub is not a complete slate.</li>
    <li><strong>Tip percentages are votes.</strong> "15/26 Win Tips · 58%" is a share of community selections, not a probability. This desk does not use it.</li>
    <li><strong>Golf can be empty.</strong> The golf hub returned "No tips found" even though tours are running, so OLBG emptiness is a fact about OLBG, not about the sport.</li>
  </ol>
</section>
<section class="panel">
  <h2>What this means for the brief</h2>
  <p>The brief asks for matches "listed on OLBG" and for those matches to be priced. Those two requirements diverge: OLBG lists many events its own tipsters have not verified, and it hides others entirely. This desk uses OLBG only to enumerate what is advertised, then insists on a governing-body confirmation before any price is attached. That is why the <a href="matches.html">Matches</a> page has two tables and why {C['olbg_rows']} advertised rows carry no price.</p>
</section>
"""
    return page("OLBG structure", "olbg", body)


CSS = """
:root{
  --bg:#0b1220; --panel:#111b2e; --panel2:#16233a; --line:#22314d; --ink:#e8eefc;
  --muted:#93a4c3; --accent:#5ee0a8; --accent2:#8ab4ff; --warn:#ffb454; --bad:#ff7a90;
  --high:#5ee0a8; --medium:#8ab4ff; --low:#93a4c3;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--accent2);text-decoration:none}
a:hover{text-decoration:underline}
.skip{position:absolute;left:-9999px}
.skip:focus{left:8px;top:8px;background:#fff;color:#000;padding:8px;z-index:99}
.topbar{position:sticky;top:0;z-index:20;display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between;padding:12px 22px;background:rgba(11,18,32,.94);border-bottom:1px solid var(--line);backdrop-filter:blur(8px)}
.brand{display:flex;align-items:baseline;gap:8px;color:var(--ink);font-weight:800;letter-spacing:.02em}
.brand-mark{background:var(--accent);color:#062018;padding:2px 7px;border-radius:6px;font-size:14px}
.brand-sub{color:var(--muted);font-weight:500;font-size:13px;letter-spacing:.08em;text-transform:uppercase}
.nav{display:flex;flex-wrap:wrap;gap:2px}
.nav-link{padding:6px 10px;border-radius:8px;color:var(--muted);font-size:14px}
.nav-link:hover{background:var(--panel2);color:var(--ink);text-decoration:none}
.nav-link.active{background:var(--panel2);color:var(--ink);box-shadow:inset 0 0 0 1px var(--line)}
.stamp{font-size:12px;color:var(--muted);display:flex;align-items:center;gap:6px}
.live-dot{width:8px;height:8px;border-radius:50%;background:var(--accent);display:inline-block}
main{padding:26px 22px 60px;max-width:1380px;margin:0 auto}
.hero{margin:6px 0 22px}
.hero.small h1{font-size:30px}
.hero h1{font-size:40px;line-height:1.1;margin:8px 0 10px;letter-spacing:-.02em}
.eyebrow{margin:0;color:var(--accent);font-size:12px;letter-spacing:.12em;text-transform:uppercase;font-weight:700}
.lede{color:#c3d0e8;max-width:940px;font-size:17px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin:18px 0 24px}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:14px 16px;display:flex;gap:12px;align-items:center}
.kpi.accent{border-color:rgba(94,224,168,.45)}
.kpi.warn{border-color:rgba(255,180,84,.35)}
.kpi-n{font-size:30px;font-weight:800}
.kpi-l{font-size:12.5px;color:var(--muted);line-height:1.35}
.kpi-l em{color:#7f92b3;font-style:normal;font-size:11.5px}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:20px;margin:0 0 20px}
.panel-head h2{margin:0 0 4px}
.panel-head p{margin:0 0 14px;color:var(--muted);font-size:14px}
h1,h2,h3{letter-spacing:-.01em}
h2{font-size:21px;margin:18px 0 8px}
h3{font-size:16px;margin:0 0 6px}
.table-wrap{overflow-x:auto;border-radius:12px;border:1px solid var(--line)}
table.desk{width:100%;border-collapse:collapse;font-size:14px;min-width:720px;background:var(--panel2)}
table.desk th{text-align:left;font-size:11.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);background:#0e1728;padding:10px;border-bottom:1px solid var(--line);position:sticky;top:0}
table.desk td{padding:10px;border-bottom:1px solid rgba(34,49,77,.7);vertical-align:top}
table.desk tr:last-child td{border-bottom:0}
table.desk tr:hover td{background:#182742}
.match strong{display:block}
.sub{display:block;color:var(--muted);font-size:12px;margin-top:2px}
.sel strong,.sel{font-weight:600}
.mono{font-variant-numeric:tabular-nums;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13px}
.src a{font-size:13px}
.blank{color:#7f92b3;font-style:italic}
.chip{display:inline-block;padding:2px 9px;border-radius:999px;font-size:12px;font-weight:700;letter-spacing:.02em}
.chip-high{background:rgba(94,224,168,.16);color:var(--high);box-shadow:inset 0 0 0 1px rgba(94,224,168,.4)}
.chip-medium{background:rgba(138,180,255,.14);color:var(--medium);box-shadow:inset 0 0 0 1px rgba(138,180,255,.35)}
.chip-low,.chip-medium+.chip{background:rgba(147,164,195,.12);color:var(--low)}
.chip-low{background:rgba(147,164,195,.12);color:var(--low);box-shadow:inset 0 0 0 1px rgba(147,164,195,.3)}
.sport-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:10px}
.sport-card{background:var(--panel2);border:1px solid var(--line);border-radius:12px;padding:12px;display:flex;flex-direction:column;gap:6px;color:var(--ink)}
.sport-card:hover{border-color:var(--accent2);text-decoration:none}
.sport-card.ok{border-left:3px solid var(--accent)}
.sport-card.mid{border-left:3px solid var(--accent2)}
.sport-card.bad{border-left:3px solid var(--warn)}
.sport-name{font-weight:700}
.sport-nums{font-size:12px;color:var(--muted)}
.sport-state{font-size:11.5px;text-transform:uppercase;letter-spacing:.08em;color:#7f92b3}
.two-col{display:grid;grid-template-columns:1.4fr 1fr;gap:22px}
@media(max-width:820px){.two-col{grid-template-columns:1fr}.hero h1{font-size:30px}.nav{display:none}}
.callout{background:#0f1a2c;border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.callout h3{color:var(--warn)}
ul.tight{margin:6px 0;padding-left:18px}
ul.tight li{margin:4px 0}
.steps{padding-left:20px}
.steps li{margin:8px 0}
.note{color:var(--muted);font-size:13.5px;margin-top:12px}
.small{font-size:12.5px;color:var(--muted)}
.button{display:inline-block;margin-top:6px;padding:9px 14px;border-radius:10px;background:var(--accent);color:#062018;font-weight:700}
.button:hover{text-decoration:none;filter:brightness(1.05)}
.pick-card,.writeup,.flag,.fx-block{background:var(--panel2);border:1px solid var(--line);border-radius:14px;padding:16px;margin:0 0 14px}
.pick-card header, .fx-block header{display:flex;justify-content:space-between;gap:12px;align-items:flex-start}
.pick-facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:12px 0}
.lbl{display:block;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.val{font-weight:600}
.pred{color:#dbe5f7;font-size:15px;margin:10px 0}
.pred.big{font-size:17px;line-height:1.65}
.src-line{font-size:13px;color:var(--muted);margin:8px 0 0}
.warn-line{color:var(--warn);font-size:13px;margin:6px 0 0}
.writeup-head h2{margin:0 0 6px}
.selection{color:var(--muted);font-size:14px;margin:0}
.inputs{display:grid;grid-template-columns:190px 1fr;gap:6px 14px;margin:14px 0 0;font-size:14px}
.inputs dt{color:var(--muted);font-size:12.5px;text-transform:uppercase;letter-spacing:.06em}
.inputs dd{margin:0}
@media(max-width:700px){.inputs{grid-template-columns:1fr}}
.flag-head{display:flex;gap:10px;align-items:center;margin-bottom:6px}
.chip-high+.mono,.chip-medium+.mono,.chip-low+.mono{color:var(--muted)}
.calc{color:var(--muted);font-size:13px;margin:8px 0 0}
.tag{background:rgba(255,180,84,.14);color:var(--warn);border-radius:6px;padding:1px 6px;font-size:11.5px}
.warnbox{border-color:rgba(255,180,84,.4)}
.sport-list{display:flex;flex-direction:column;gap:8px}
.sport-row{display:grid;grid-template-columns:230px 1fr 1.4fr;gap:12px;padding:12px;background:var(--panel2);border:1px solid var(--line);border-radius:12px;color:var(--ink)}
.sport-row:hover{border-color:var(--accent2);text-decoration:none}
.sport-stats{color:var(--muted);font-size:13.5px}
.sport-note{color:#9db0d1;font-size:13px}
@media(max-width:760px){.sport-row{grid-template-columns:1fr}}
.foot{max-width:1380px;margin:0 auto;padding:22px;border-top:1px solid var(--line);color:var(--muted);font-size:13px}
.foot p{margin:6px 0}
@media print{.topbar{position:static}.nav{display:none}body{background:#fff;color:#000}.panel,.kpi,.pick-card,.writeup,.flag{background:#fff;border-color:#ccc}}
"""


def main() -> None:
    os.makedirs(DATA, exist_ok=True)
    os.makedirs(os.path.join(OUT, "sports"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)

    with open(os.path.join(OUT, "assets", "desk.css"), "w", encoding="utf-8") as fh:
        fh.write(CSS)

    write("index.html", page_index())
    write("picks.html", page_picks())
    write("matches.html", page_matches())
    write("markets.html", page_markets())
    write("predictions.html", page_predictions())
    write("sports.html", page_sports())
    write("flagged.html", page_flagged())
    write("repo-review.html", page_repo())
    write("sources.html", page_sources())
    write("methodology.html", page_method())
    write("olbg.html", page_olbg())
    for slug, name, sid, olbg in D.SPORTS:
        write(f"sports/{slug}.html", page_sport(slug, name, sid, olbg))

    payload = {
        "snapshot": D.SNAPSHOT_UTC,
        "counts": C,
        "fixtures": [{k: v for k, v in f.items() if k not in ("markets",)} for f in FIXTURES],
        "markets": [{"fixture_id": f["id"], "event": f["event"], "markets": f["markets"]} for f in FIXTURES],
        "picks": [{"fixture_id": f["id"], "sport": f["sport"], "event": f["event"], **f["pick"]} for f in PICKS],
        "olbg_listings": [
            {"sport": s, "event": e, "competition": c, "olbg_clock": w, "olbg_url": u}
            for s, e, c, w, _l, u in D.OLBG_INVENTORY
        ],
        "sources": [{"name": n, "url": u, "type": t, "sport": s, "read_at": r} for n, u, t, s, r in D.SOURCES],
        "flags": D.FLAGS,
        "repo_audit": D.REPO_AUDIT,
    }
    with open(os.path.join(DATA, "desk.json"), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1, sort_keys=False)
    for name in ("fixtures", "picks", "flags"):
        with open(os.path.join(DATA, f"{name}.json"), "w", encoding="utf-8") as fh:
            json.dump(payload[name], fh, indent=1)
    print(f"fixtures={len(FIXTURES)} picks={len(PICKS)} markets={C['markets']} outcomes={C['outcomes']} "
          f"high={C['high']} medium={C['medium']} low={C['low']} flags={C['flags']}")


if __name__ == "__main__":
    main()
