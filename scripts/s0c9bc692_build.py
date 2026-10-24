#!/usr/bin/env python3
"""Build the 0c9bc692 evidence-first OLBG research desk.

This generator deliberately uses a small, field-level fact base collected on 24 Oct 2026.
It never treats an OLBG community selection as an official sporting fact or a bookmaker quote.
All outputs stay inside this session's namespaced scope.
"""
from __future__ import annotations

import html
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "0c9bc692"
SITE = ROOT / "0c9bc692"
REPORT = ROOT / "reports" / "SESSION_0C9BC692.md"
SESSION = "0c9bc692-olbg1"
TASK = "T0C9"
OBSERVED_WINDOW = "24 Oct 2026, 17:09 UTC (single session)"

SPORTS = [
    ("golf", "Golf"), ("volleyball", "Volleyball"), ("rugby-union", "Rugby Union"),
    ("cricket", "Cricket"), ("snooker", "Snooker"), ("darts", "Darts"),
    ("baseball", "Baseball"), ("gaelic-sports", "Gaelic Sports"),
    ("greyhounds", "Greyhounds"), ("tennis", "Tennis"),
    ("motor-racing", "Motor Racing"), ("handball", "Handball"),
    ("ice-hockey", "Ice Hockey"), ("basketball", "Basketball"),
    ("rugby-league", "Rugby League"),
]
SPORT_NAME = dict(SPORTS)

# Each excerpt is a compact record of what was actually read.  The official-page link remains
# the manual review destination; short extracts make it clear which fields have been retained.
SOURCES: dict[str, dict[str, str]] = {
    "pga": {"label": "PGA TOUR schedule", "sport": "golf", "url": "https://www.pgatour.com/schedule/2026", "result": "Official 2026 schedule page was read; this desk did not retain a current 24–25 October player field from it."},
    "vworld": {"label": "Volleyball World competition URL", "sport": "volleyball", "url": "https://en.volleyballworld.com/volleyball/competitions/vnl-2026/", "result": "Official domain returned Page Not Found for the queried VNL 2026 route; no fixture was inferred."},
    "urc": {"label": "United Rugby Championship fixtures URL", "sport": "rugby-union", "url": "https://www.unitedrugby.com/fixtures", "result": "Official domain returned 404 for the queried fixtures route; no fixture was inferred."},
    "nzc": {"label": "New Zealand Cricket matches hub", "sport": "cricket", "url": "https://www.nzc.nz/matches/", "result": "The official hub links to fixtures, results and live scorecards but the observed page did not expose an exact upcoming pairing retained here."},
    "wst": {"label": "World Snooker Tour draw", "sport": "snooker", "url": "https://www.wst.tv/matches/", "result": "The official Northern Ireland Open draw showed Mark Williams v Jak Jones as scheduled at 14:00 on Saturday 24 October and the final at 08:00 Sunday 25 October."},
    "pdc": {"label": "PDC official calendar", "sport": "darts", "url": "https://www.pdc.tv/calendar/", "result": "The official site presented its consent layer rather than readable fixture content in this retrieval; an OLBG-discovered darts pairing is not confirmed by this source."},
    "mlb": {"label": "MLB Stats API schedule", "sport": "baseball", "url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-10-24", "result": "Game 849802: Tampa Bay Rays at Milwaukee Brewers; 2026-10-25T00:00:00Z; Scheduled; World Series Game 2; American Family Field; ifNecessary=N."},
    "gaa": {"label": "GAA fixtures and results", "sport": "gaelic-sports", "url": "https://www.gaa.ie/fixtures-results", "result": "Observed page showed Ireland v Scotland as Shinty-Hurling International at 18:00 Saturday 24 October, marked Final. It did not confirm either OLBG Gaelic Football club listing retained for review."},
    "gbgb": {"label": "Greyhound Board of Great Britain", "sport": "greyhounds", "url": "https://www.gbgb.org.uk/meetings/", "result": "The queried route resolved to a dated 2018 disruption article. It is not used as a contemporary fixture or runner source."},
    "atp": {"label": "ATP Tour tournaments", "sport": "tennis", "url": "https://www.atptour.com/en/tournaments", "result": "Official calendar page was read. No named 24–25 October head-to-head was retained from the observed response."},
    "f1": {"label": "Formula 1 United States Grand Prix", "sport": "motor-racing", "url": "https://www.formula1.com/en/racing/2026/united-states", "result": "Official page lists Practice 3 13:30–14:30 and qualifying 17:00–18:00 on 24 October, followed by the race at 16:00 on 25 October. The page labels these Track Time; no timezone conversion is made."},
    "ehf": {"label": "EHF Champions League matches URL", "sport": "handball", "url": "https://www.eurohandball.com/en/competitions/ehf-champions-league/men/2026-27/matches/", "result": "Official domain returned Error404 for the queried route; no fixture was inferred."},
    "nhl": {"label": "NHL official schedule API", "sport": "ice-hockey", "url": "https://api-web.nhle.com/v1/schedule/2026-10-24", "result": "Official schedule exposed ANA–PHI 17:00 UTC (PRE), LAK–NJD 19:30 UTC (FUT), and SJS–BOS 23:00 UTC (FUT), with venues and game IDs."},
    "nba": {"label": "NBA official schedule", "sport": "basketball", "url": "https://www.nba.com/schedule?date=2026-10-24", "result": "Official Saturday 24 October schedule lists eight games with ET display times and venues; this desk preserves that display timezone rather than converting it."},
    "nrl": {"label": "NRL / Rugby League World Cup draw", "sport": "rugby-league", "url": "https://www.nrl.com/draw/?competition=131&round=2&season=2026", "result": "Official Round 2 page lists New Zealand v Cook Islands, Sunday 25 October kick-off 1:05am at One NZ Stadium, and Australia v Fiji, Sunday 25 October kick-off 5:05am at Suncorp Stadium. The page does not state a timezone next to these times."},
}

OLBG_SOURCES = {
    "home": "https://www.olbg.com/betting-tips",
    "snooker": "https://www.olbg.com/betting-tips/Snooker/All_Snooker/All_Events/Mark_Williams_v_Jak_Jones/8?event_id=9952",
    "darts": "https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Krzysztof_Ratajski_vs_Kevin_Doets/15?event_id=32399",
    "gaelic": "https://www.olbg.com/betting-tips/Gaelic_Football/All_Gaelic_Football/All_Events/Moycullen_v_Salthill-Knocknacarra/25?event_id=3532",
}

# Exact schedule entries are only retained when the official page named the participants/event.
FIXTURES: list[dict[str, Any]] = [
    {"id": "NBA-001", "sport": "basketball", "participants": "Miami Heat at Charlotte Hornets", "when": "24 Oct · 6:00 PM ET", "venue": "Spectrum Center, Charlotte, NC", "status": "scheduled", "official_source": "nba", "notes": "NBA official schedule listing."},
    {"id": "NBA-002", "sport": "basketball", "participants": "Brooklyn Nets at Cleveland Cavaliers", "when": "24 Oct · 7:30 PM ET", "venue": "Rocket Arena, Cleveland, OH", "status": "scheduled", "official_source": "nba", "notes": "NBA official schedule listing."},
    {"id": "NBA-003", "sport": "basketball", "participants": "Milwaukee Bucks at Philadelphia 76ers", "when": "24 Oct · 7:30 PM ET", "venue": "Xfinity Mobile Arena, Philadelphia, PA", "status": "scheduled", "official_source": "nba", "notes": "NBA official schedule listing."},
    {"id": "NBA-004", "sport": "basketball", "participants": "Washington Wizards at Chicago Bulls", "when": "24 Oct · 8:00 PM ET", "venue": "United Center, Chicago, IL", "status": "scheduled", "official_source": "nba", "notes": "NBA official schedule listing."},
    {"id": "NBA-005", "sport": "basketball", "participants": "San Antonio Spurs at Dallas Mavericks", "when": "24 Oct · 8:00 PM ET", "venue": "American Airlines Center, Dallas, TX", "status": "scheduled", "official_source": "nba", "notes": "NBA official schedule listing."},
    {"id": "NBA-006", "sport": "basketball", "participants": "Houston Rockets at Atlanta Hawks", "when": "24 Oct · 8:30 PM ET", "venue": "State Farm Arena, Atlanta, GA", "status": "scheduled", "official_source": "nba", "notes": "NBA official schedule listing."},
    {"id": "NBA-007", "sport": "basketball", "participants": "New Orleans Pelicans at Denver Nuggets", "when": "24 Oct · 9:00 PM ET", "venue": "Ball Arena, Denver, CO", "status": "scheduled", "official_source": "nba", "notes": "NBA official schedule listing."},
    {"id": "NBA-008", "sport": "basketball", "participants": "Golden State Warriors at Phoenix Suns", "when": "24 Oct · 10:00 PM ET", "venue": "Mortgage Matchup Center, Phoenix, AZ", "status": "scheduled", "official_source": "nba", "notes": "NBA official schedule listing."},
    {"id": "NHL-001", "sport": "ice-hockey", "participants": "Anaheim Ducks at Philadelphia Flyers", "when": "24 Oct · 17:00 UTC", "venue": "Xfinity Mobile Arena", "status": "pre-game (PRE)", "official_source": "nhl", "notes": "NHL game 2026020168."},
    {"id": "NHL-002", "sport": "ice-hockey", "participants": "Los Angeles Kings at New Jersey Devils", "when": "24 Oct · 19:30 UTC", "venue": "Prudential Center", "status": "future (FUT)", "official_source": "nhl", "notes": "NHL game 2026020169."},
    {"id": "NHL-003", "sport": "ice-hockey", "participants": "San Jose Sharks at Boston Bruins", "when": "24 Oct · 23:00 UTC", "venue": "TD Garden", "status": "future (FUT)", "official_source": "nhl", "notes": "NHL game 2026020170."},
    {"id": "MLB-001", "sport": "baseball", "participants": "Tampa Bay Rays at Milwaukee Brewers", "when": "25 Oct · 00:00 UTC", "venue": "American Family Field", "status": "scheduled", "official_source": "mlb", "notes": "World Series Game 2; game 849802; normal game (ifNecessary=N)."},
    {"id": "SNO-001", "sport": "snooker", "participants": "Mark Williams v Jak Jones", "when": "24 Oct · 14:00 (timezone not published in retained source)", "venue": "", "status": "scheduled", "official_source": "wst", "olbg_source": "snooker", "notes": "Northern Ireland Open semi-final, Match 62."},
    {"id": "F1-001", "sport": "motor-racing", "participants": "Formula 1 United States Grand Prix — qualifying", "when": "24 Oct · 17:00–18:00 Track Time", "venue": "Circuit of the Americas (Austin)", "status": "scheduled", "official_source": "f1", "notes": "Field session; official page labels the display as Track Time."},
    {"id": "F1-002", "sport": "motor-racing", "participants": "Formula 1 United States Grand Prix — race", "when": "25 Oct · 16:00 Track Time", "venue": "Circuit of the Americas (Austin)", "status": "scheduled", "official_source": "f1", "notes": "Field event; official page labels the display as Track Time."},
    {"id": "RL-001", "sport": "rugby-league", "participants": "New Zealand v Cook Islands", "when": "25 Oct · 1:05am (timezone not published in retained source)", "venue": "One NZ Stadium, Christchurch", "status": "upcoming", "official_source": "nrl", "notes": "Rugby League World Cup Round 2."},
    {"id": "RL-002", "sport": "rugby-league", "participants": "Australia v Fiji", "when": "25 Oct · 5:05am (timezone not published in retained source)", "venue": "Suncorp Stadium, Brisbane", "status": "upcoming", "official_source": "nrl", "notes": "Rugby League World Cup Round 2."},
    # These three entries are intentionally visible but unavailable for price/pick output.
    {"id": "OLBG-DAR-001", "sport": "darts", "participants": "Krzysztof Ratajski v Kevin Doets", "when": "OLBG showed Today · 13:15; timezone not stated", "venue": "", "status": "OLBG discovery only", "official_source": "pdc", "olbg_source": "darts", "notes": "Official PDC calendar retrieval was blocked by consent content; keep unconfirmed."},
    {"id": "OLBG-GAA-001", "sport": "gaelic-sports", "participants": "Moycullen v Salthill-Knocknacarra", "when": "OLBG showed Tomorrow · 12:00; timezone not stated", "venue": "", "status": "OLBG discovery only", "official_source": "gaa", "olbg_source": "gaelic", "notes": "Unconfirmed: exact club pairing was not present on the official GAA page read in this session."},
]

# A market is never called available merely because the general sport supports it.  These are
# outcomes of the research step: one supported own line, source-observed market names, or a blank.
MARKETS: list[dict[str, Any]] = []
for fixture in FIXTURES:
    if fixture["id"] == "SNO-001":
        MARKETS.extend([
            {"fixture_id": fixture["id"], "market": "Win Match", "source_status": "observed on OLBG; participants confirmed by WST", "selection": "Mark Williams", "fair_probability": 0.60, "fair_decimal": 1.67, "fair_american": -150, "confidence": "Low", "basis": "Three WST wins retained for Williams (4–2, 4–0, 6–4) and two retained Jones wins (4–2, 6–5); a small-sample, uncalibrated 60/40 estimate. Not an available quote.", "olbg_market": True},
            {"fixture_id": fixture["id"], "market": "Handicap Betting", "source_status": "observed on OLBG", "selection": "", "fair_probability": None, "fair_decimal": None, "fair_american": None, "confidence": "Withheld", "basis": "No source-backed frame-distribution input was retained for an originated handicap line.", "olbg_market": True},
            {"fixture_id": fixture["id"], "market": "Frame Betting", "source_status": "observed on OLBG", "selection": "", "fair_probability": None, "fair_decimal": None, "fair_american": None, "confidence": "Withheld", "basis": "No source-backed frame-distribution input was retained for a total or correct-score line.", "olbg_market": True},
        ])
    elif fixture["id"] == "OLBG-DAR-001":
        for market in ["Win Match 2-way", "Total 180s", "Most 180s", "Handicap 2-way", "Total Legs"]:
            MARKETS.append({"fixture_id": fixture["id"], "market": market, "source_status": "observed on OLBG; event unconfirmed by official source", "selection": "", "fair_probability": None, "fair_decimal": None, "fair_american": None, "confidence": "Withheld", "basis": "No official fixture confirmation; no price or pick produced.", "olbg_market": True})
    elif fixture["id"] == "OLBG-GAA-001":
        for market in ["FT Result", "Handicap"]:
            MARKETS.append({"fixture_id": fixture["id"], "market": market, "source_status": "observed on OLBG; event unconfirmed by official source", "selection": "", "fair_probability": None, "fair_decimal": None, "fair_american": None, "confidence": "Withheld", "basis": "No official fixture confirmation; no price or pick produced.", "olbg_market": True})
    else:
        market_names = ["Match winner", "Handicap / spread", "Match total"]
        if fixture["sport"] == "motor-racing":
            market_names = ["Outright / podium", "Grid / qualifying", "Race total / classification"]
        for market in market_names:
            MARKETS.append({"fixture_id": fixture["id"], "market": market, "source_status": "investigated; no OLBG event page retained for this official listing", "selection": "", "fair_probability": None, "fair_decimal": None, "fair_american": None, "confidence": "Withheld", "basis": "A schedule alone does not establish an available OLBG market or enough current performance inputs for a responsible originated line.", "olbg_market": False})

PREDICTIONS = [{
    "fixture_id": "SNO-001",
    "sport": "snooker",
    "confidence": "Low",
    "selection": "Mark Williams to win",
    "fair_american": -150,
    "word_count": 83,
    "text": "Selection: Mark Williams to win, rated Low at an originated fair −150. World Snooker Tour lists Williams’ 4–2 result over Zhang Anda on 21 October, 4–0 result over Martin O’Donnell on 22 October, and 6–4 quarter-final win over David Gilbert on 23 October. Jak Jones reached this semi-final by beating Daniel Wells 4–2 and Scott Donaldson 6–5 in the same official draw. No player-availability item was read, and the limited retained sample keeps this below the executive list.",
    "sources": ["wst"],
}]

FLAGS = [
    {"id": "F-0C9-01", "severity": "High", "topic": "No approved High picks", "detail": "No selection clears the desk's evidence, calibration, context and current-market requirements. The executive summary intentionally contains zero High picks rather than quota-filling.", "source": ""},
    {"id": "F-0C9-02", "severity": "High", "topic": "Daily five-per-sport target", "detail": "All 15 sports are represented, but the evidence base does not support five separate source-backed High predictions in any category. Shortfall: 75 requested High predictions.", "source": ""},
    {"id": "F-0C9-03", "severity": "Medium", "topic": "OLBG is discovery, not fixture proof", "detail": "OLBG exposes tip counts and market labels, not an official sporting record or a bookmaker quote. Every OLBG-only event is blank and withheld until an official competition source confirms it.", "source": OLBG_SOURCES["home"]},
    {"id": "F-0C9-04", "severity": "Medium", "topic": "Darts confirmation blocked", "detail": "The queried PDC page exposed consent content rather than its calendar. Krzysztof Ratajski v Kevin Doets remains unconfirmed and unpriced.", "source": SOURCES["pdc"]["url"]},
    {"id": "F-0C9-05", "severity": "Medium", "topic": "Gaelic club matches not confirmed", "detail": "The GAA page read did not name the two OLBG Gaelic Football club pairings. No outcome, handicap or probability is supplied for them.", "source": SOURCES["gaa"]["url"]},
    {"id": "F-0C9-06", "severity": "Medium", "topic": "Timezone omission", "detail": "WST semi-final time, NRL kickoff times, OLBG Today/Tomorrow labels, and F1 Track Time are displayed exactly as read. They are not converted to UTC where the source did not publish a timezone.", "source": ""},
    {"id": "F-0C9-07", "severity": "Medium", "topic": "Unavailable official fixture routes", "detail": "The queried Volleyball World, URC and EHF competition routes returned a not-found response. No substitute fixture list was guessed.", "source": SOURCES["vworld"]["url"]},
    {"id": "F-0C9-08", "severity": "Medium", "topic": "Greyhound source stale", "detail": "The GBGB query resolved to an old 2018 weather story, so this desk retains no current meeting, runner or race market.", "source": SOURCES["gbgb"]["url"]},
    {"id": "F-0C9-09", "severity": "Low", "topic": "Snooker estimate is not a quote", "detail": "The −150 Snooker fair display is an own small-sample research estimate. It is neither an OLBG price nor a bookmaker offer and carries a Low label.", "source": SOURCES["wst"]["url"]},
]


def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def slug_name(sport: str) -> str:
    return SPORT_NAME[sport]


def rel(page: str, current: str) -> str:
    if current.startswith("sports/"):
        return "../" + page
    return page


def source_link(source_id: str, current: str = "") -> str:
    source = SOURCES[source_id]
    return f'<a class="source" href="{esc(source["url"])}" target="_blank" rel="noopener noreferrer">{esc(source["label"])} ↗</a>'


def olbg_link(key: str) -> str:
    return f'<a class="source discovery" href="{esc(OLBG_SOURCES[key])}" target="_blank" rel="noopener noreferrer">OLBG discovery ↗</a>'


def nav(current: str = "") -> str:
    links = [("index.html", "Executive summary"), ("matches.html", "Matches"), ("markets.html", "Markets"), ("predictions.html", "Written analysis"), ("sources.html", "Sources"), ("reverse-engineering.html", "OLBG map"), ("flagged.html", "Flagged")]
    items = []
    for href, label in links:
        active = " active" if current == href else ""
        items.append(f'<a class="{active.strip()}" href="{rel(href, current)}">{label}</a>')
    return f'''<header><div class="nav"><a class="brand" href="{rel('index.html', current)}">OLBG research desk <span>24 OCT 2026</span></a><nav>{''.join(items)}</nav></div></header>'''


def shell(title: str, content: str, current: str = "", description: str = "") -> str:
    desc = description or "Evidence-first OLBG research desk."
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)} · OLBG research desk</title><meta name="description" content="{esc(desc)}"><link rel="stylesheet" href="{rel('assets/style.css', current)}"></head><body>
{nav(current)}
<main>{content}</main>
<footer><div><strong>Session {SESSION}</strong> · {TASK} · source window: {OBSERVED_WINDOW}</div><div>Not affiliated with OLBG. Research only; no execution or guarantee.</div></footer>
<script src="{rel('assets/app.js', current)}"></script></body></html>'''


def hero(kicker: str, heading: str, text: str, actions: str = "") -> str:
    return f'''<section class="hero"><div><p class="kicker">{esc(kicker)}</p><h1>{esc(heading)}</h1><p>{text}</p></div>{actions}</section>'''


def fixture_table(rows: list[dict[str, Any]], current: str = "") -> str:
    if not rows:
        return '<div class="empty">No exact fixture row retained for this category. See the Flagged page for the source-specific reason.</div>'
    tr = []
    for row in rows:
        olbg = olbg_link(row["olbg_source"]) if row.get("olbg_source") else ""
        venue = esc(row["venue"]) if row["venue"] else '<span class="blank">Not published in retained source</span>'
        tr.append(f'''<tr data-sport="{esc(row['sport'])}"><td><span class="id">{esc(row['id'])}</span><br><span class="pill sport">{esc(slug_name(row['sport']))}</span></td><td><strong>{esc(row['participants'])}</strong><br><span class="sub">{esc(row['notes'])}</span></td><td>{esc(row['when'])}</td><td>{venue}</td><td><span class="pill {('warn' if 'discovery only' in row['status'] else 'ok')}">{esc(row['status'])}</span></td><td>{source_link(row['official_source'], current)} {olbg}</td></tr>''')
    return '''<div class="table-wrap"><table><thead><tr><th>ID / Sport</th><th>Match or event</th><th>Start shown by source</th><th>Venue</th><th>Status retained</th><th>Manual review</th></tr></thead><tbody>''' + ''.join(tr) + '</tbody></table></div>'


def market_table(rows: list[dict[str, Any]], current: str = "") -> str:
    lookup = {f["id"]: f for f in FIXTURES}
    tr = []
    for row in rows:
        fixture = lookup[row["fixture_id"]]
        probability = f"{row['fair_probability']:.0%}" if row["fair_probability"] is not None else ""
        price = f"{row['fair_decimal']:.2f} / {row['fair_american']:+d}" if row["fair_decimal"] is not None else ""
        selection = esc(row["selection"]) if row["selection"] else '<span class="blank">Blank — withheld</span>'
        conf = row["confidence"].lower()
        olbg = olbg_link(fixture["olbg_source"]) if row["olbg_market"] and fixture.get("olbg_source") else ""
        tr.append(f'''<tr><td><span class="id">{esc(row['fixture_id'])}</span><br><span class="sub">{esc(fixture['participants'])}</span></td><td>{esc(row['market'])}</td><td>{selection}</td><td class="num">{probability or '—'}</td><td class="num">{price or '—'}</td><td><span class="pill {conf}">{esc(row['confidence'])}</span></td><td>{esc(row['basis'])}<br>{source_link(fixture['official_source'], current)} {olbg}</td></tr>''')
    return '''<div class="table-wrap"><table><thead><tr><th>Fixture</th><th>Market investigated</th><th>Selection</th><th>Fair chance</th><th>Own fair display</th><th>Tier</th><th>Reason / source</th></tr></thead><tbody>''' + ''.join(tr) + '</tbody></table></div>'


def coverage_cards(current: str = "") -> str:
    cards = []
    for key, name in SPORTS:
        rows = [f for f in FIXTURES if f["sport"] == key]
        exact = len([f for f in rows if f["status"] != "OLBG discovery only"])
        if exact:
            status = f"{exact} exact official schedule row{'s' if exact != 1 else ''}"
            tone = "ok"
        elif rows:
            status = f"{len(rows)} OLBG discovery row — held"
            tone = "warn"
        else:
            status = "Source reviewed; no exact row retained"
            tone = "warn"
        cards.append(f'''<a class="sport-card" href="{rel('sports/' + key + '.html', current)}"><span>{esc(name)}</span><strong class="pill {tone}">{esc(status)}</strong><small>Open category ledger →</small></a>''')
    return '<div class="sport-grid">' + ''.join(cards) + '</div>'


def index_page() -> str:
    exact = len([f for f in FIXTURES if f["status"] != "OLBG discovery only"])
    withheld = len(MARKETS) - 1
    body = hero("Executive summary", "What is actionable today — and what is not", "<strong>There are no approved High-confidence selections in this release.</strong> The desk did not convert source access, tip counts, or a simple favourite into an executive recommendation. One clearly labelled <em>Low</em> Snooker research line is shown below; every other investigated market remains blank rather than pretending a line, quote, injury report, or availability signal was read.", '<div class="actions"><a class="button primary" href="predictions.html">Read analysis</a><a class="button" href="flagged.html">Review gaps</a></div>')
    body += f'''<section class="metrics"><article><b>0</b><span>Approved High picks</span><small>Not a quota failure hidden by labels</small></article><article><b>{exact}</b><span>Exact official schedule rows</span><small>From NBA, NHL, MLB, WST, F1 and NRL</small></article><article><b>15</b><span>Sports represented</span><small>Each has a source/recheck trail</small></article><article><b>{withheld}</b><span>Market rows withheld</span><small>No unsupported price or pick is shown</small></article></section>'''
    body += '<section class="section"><div class="section-head"><h2>Where the picks are</h2><p>Only the written-analysis page contains narrative selections. This release has one Low research line and zero executive picks.</p></div>'
    body += '''<div class="callout"><strong>Current executive list: empty.</strong> A High label requires source-backed fixture status, substantive current context, a defensible line construction, and a price in the requested −250 to +10000 range. None met the full test. The low Snooker note is separated so it cannot be mistaken for an approved pick.</div></section>'''
    body += '<section class="section"><div class="section-head"><h2>Today and upcoming schedule ledger</h2><p>Exact times retain the publisher’s display timezone or explicitly say it was not published.</p><a href="matches.html">Open all matches →</a></div>'
    body += fixture_table(FIXTURES, "index.html") + '</section>'
    body += '<section class="section"><div class="section-head"><h2>15-sport coverage map</h2><p>Click a sport to see its source, exact rows and what remains blank.</p></div>' + coverage_cards('index.html') + '</section>'
    body += '<section class="section"><div class="section-head"><h2>Reverse-engineering result</h2><p>OLBG has been treated strictly as a discovery surface, never an official sport-record source.</p></div><div class="two"><article class="panel"><h3>Observed OLBG behavior</h3><p>The landing page exposes individual event routes, a community tip count, a selection label and market names. The event pages inspected exposed Snooker, Darts and Gaelic Football market families. No bookmaker quote was retained from OLBG.</p><a class="source discovery" href="' + OLBG_SOURCES["home"] + '" target="_blank" rel="noopener noreferrer">OLBG landing page ↗</a> <a href="reverse-engineering.html">Route map →</a></article><article class="panel"><h3>Publication rule</h3><p>An OLBG-discovered fixture stays visibly unconfirmed until a governing body, league, tour, promoter or team page names the same event. It then still needs enough current inputs before an originated line can be written.</p><a href="methodology.html">Read methodology →</a></article></div></section>'
    return shell("Executive summary", body, "index.html", "Clear executive summary and source-linked fixture ledger.")


def matches_page() -> str:
    body = hero("Complete retained list", "Matches and events", "Every row has an official manual-review link. OLBG-only rows are deliberately included in the same table with an obvious <strong>discovery only</strong> status; their values are not completed by inference.")
    body += '<div class="controls"><label>Filter sport <select data-filter><option value="">All 15 sports</option>' + ''.join(f'<option value="{k}">{esc(v)}</option>' for k, v in SPORTS) + '</select></label><label>Search <input type="search" data-search placeholder="Team, player, event or ID"></label><span data-count></span></div>'
    body += fixture_table(FIXTURES, "matches.html")
    return shell("All matches", body, "matches.html")


def markets_page() -> str:
    body = hero("Market research", "What was investigated — separate from what is priced", "The table distinguishes a market label observed on an OLBG event page from an actual price. Blank fields are deliberate: no available quote is asserted, and no number is generated without a source-bounded basis.")
    body += '<div class="callout"><strong>One own fair display only:</strong> Mark Williams 60% / 1.67 / −150. It is a Low research estimate using a tiny, stated WST sample, not a bookmaker offer. All other market rows are withheld.</div>'
    body += market_table(MARKETS, "markets.html")
    return shell("Markets", body, "markets.html")


def predictions_page() -> str:
    prediction = PREDICTIONS[0]
    body = hero("Written analysis only", "Predictions", "There are <strong>zero High-confidence predictions</strong>. The single Low research note is included because it is a fully written, source-bounded selection rather than an unexplained winner name. It is not part of the executive list.")
    body += '''<div class="callout"><strong>High-confidence requirement:</strong> the requested 70%+ and −250…+10000 display band is necessary but not sufficient. This desk also requires a sufficient current evidence trail and an available-market check. None qualify.</div>'''
    body += f'''<article class="prediction"><div class="prediction-top"><div><p class="kicker">{esc(prediction['sport'])} · research note</p><h2>{esc(prediction['selection'])}</h2></div><span class="pill low">Low</span></div><div class="selection"><strong>Selection</strong><span>{esc(prediction['selection'])}</span><strong>Own fair display</strong><span class="num">{prediction['fair_american']:+d}</span><strong>Confidence</strong><span>Low — not executive</span></div><p>{esc(prediction['text'])}</p><div class="prediction-meta"><span>{prediction['word_count']} words</span>{''.join(source_link(s, 'predictions.html') for s in prediction['sources'])}</div></article>'''
    return shell("Written analysis", body, "predictions.html")


def sources_page() -> str:
    rows = []
    for key, source in SOURCES.items():
        rows.append(f'''<tr><td><span class="pill sport">{esc(slug_name(source['sport']))}</span></td><td><strong>{esc(source['label'])}</strong></td><td>{source_link(key, 'sources.html')}</td><td>{esc(source['result'])}</td></tr>''')
    body = hero("Manual review links", "Official sources read this session", "These are the authoritative review destinations for the fields retained in this desk. A link does not silently certify a field not described in the observed-result column.")
    body += '<div class="table-wrap"><table><thead><tr><th>Sport</th><th>Source</th><th>Link</th><th>What this desk retained</th></tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>'
    body += '<section class="section"><div class="section-head"><h2>OLBG discovery links</h2><p>These are displayed apart from official sources. Tip counts are community activity, not fixture confirmation or price data.</p></div><div class="two">' + ''.join(f'<article class="panel"><h3>{esc(key.title())}</h3><a class="source discovery" href="{esc(url)}" target="_blank" rel="noopener noreferrer">OLBG page ↗</a></article>' for key, url in OLBG_SOURCES.items()) + '</div></section>'
    return shell("Sources", body, "sources.html")


def reverse_engineering_page() -> str:
    body = hero("OLBG discovery audit", "What the public OLBG pages exposed", "This is a bounded observation of public HTML, not a private API reconstruction. It describes only routes and fields actually read in the 24 October session, then separates them from the official sporting sources required elsewhere in the desk.")
    body += '''<section class="two"><article class="panel"><h2>Observed route pattern</h2><p>The landing page linked individual sport/event pages beneath <span class="id">/betting-tips/…</span>. The three event pages below use a readable sport path and an <span class="id">event_id</span> query parameter. This is recorded to make manual review easy; it is not used to manufacture hidden schedule data.</p><a class="source discovery" href="https://www.olbg.com/betting-tips" target="_blank" rel="noopener noreferrer">OLBG public landing ↗</a></article><article class="panel"><h2>Observed fields</h2><p>The pages exposed match title, a Today/Tomorrow display label, community tip numerator/denominator, selection labels and market names. They did not provide a retained bookmaker quote. Community percentage is never substituted for an originated probability.</p><a href="methodology.html">Publication rules →</a></article></section>'''
    observations = [
        ("Snooker", "Mark Williams v Jak Jones", "Win Match; Handicap Betting; Frame Betting", "Official WST draw confirms the semi-final pairing."),
        ("Darts", "Krzysztof Ratajski v Kevin Doets", "Win Match 2-way; Total 180s; Most 180s; Handicap 2-way; Total Legs", "PDC page was consent-blocked; fixture is held blank."),
        ("Gaelic Football", "Moycullen v Salthill-Knocknacarra", "FT Result; Handicap", "The GAA page read did not name the club fixture; held blank."),
    ]
    table = []
    for sport, event, markets, disposition in observations:
        key = "snooker" if sport == "Snooker" else "darts" if sport == "Darts" else "gaelic"
        table.append(f'<tr><td><span class="pill sport">{esc(sport)}</span></td><td><strong>{esc(event)}</strong></td><td>{esc(markets)}</td><td>{esc(disposition)}</td><td>{olbg_link(key)}</td></tr>')
    body += '<section class="section"><div class="section-head"><h2>Event-route ledger</h2><p>Only one row became eligible for an own Low research line after an official fixture source was also read.</p></div><div class="table-wrap"><table><thead><tr><th>Sport</th><th>OLBG title</th><th>Market labels observed</th><th>Official-source disposition</th><th>Manual review</th></tr></thead><tbody>' + ''.join(table) + '</tbody></table></div></section>'
    return shell("OLBG map", body, "reverse-engineering.html")


def flagged_page() -> str:
    rows = []
    for f in FLAGS:
        source = f'<a class="source" href="{esc(f["source"])}" target="_blank" rel="noopener noreferrer">Open cited page ↗</a>' if f["source"] else '<span class="blank">No single external page; see desk methodology</span>'
        rows.append(f'<tr><td><span class="id">{esc(f["id"])}</span></td><td><span class="pill warn">{esc(f["severity"])}</span></td><td><strong>{esc(f["topic"])}</strong></td><td>{esc(f["detail"])}</td><td>{source}</td></tr>')
    body = hero("Flagged for review", "Known gaps and irregularities", "These items are not hidden behind a confidence badge. They explain why the executive list is empty and where a future refresh must gather stronger official evidence.")
    body += '<div class="table-wrap"><table><thead><tr><th>ID</th><th>Severity</th><th>Issue</th><th>Why it matters</th><th>Manual review</th></tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>'
    return shell("Flagged for review", body, "flagged.html")


def methodology_page() -> str:
    body = hero("Methodology", "How this desk avoids invented certainty", "The desk is deliberately narrower than a global fixture feed. It records what the official pages actually named during one window, makes source limits visible, and does not convert tip-share popularity into a price or probability.")
    body += '''<section class="two"><article class="panel"><h2>Inclusion</h2><ol><li>An exact fixture/event is retained only when an official page named it.</li><li>The source page and observed-result note accompany each row.</li><li>Publisher time labels stay unchanged when no timezone was stated.</li><li>OLBG-discovered rows have a separate discovery label and can never become official through repetition.</li></ol></article><article class="panel"><h2>Price and confidence</h2><ol><li>Markets are investigated individually: winner, handicap/spread, total and any sport-specific family seen on the event page.</li><li>A blank market means no price/pick was produced; it does not mean the market is unavailable.</li><li>The single Snooker fair display is an explicit 60/40 research construction from stated WST results, with no vig and no bookmaker claim.</li><li>High requires more than a 70% number and an in-band American display: it also needs current context, credible inputs and market eligibility.</li></ol></article></section>'''
    body += '''<section class="section"><div class="section-head"><h2>Scope and expiry</h2></div><div class="panel"><p><strong>Source observation window:</strong> ''' + OBSERVED_WINDOW + '''. This is not a promise that a schedule, player availability, market, tip count or result remains current after that window. The desk contains no injury assertion unless an official source item was read; no such item was used in the published Low note. It provides no staking instruction, quote comparison, execution path or personalized advice.</p></div></section>'''
    return shell("Methodology", body, "methodology.html")


def audit_page() -> str:
    official = [f for f in FIXTURES if f["status"] != "OLBG discovery only"]
    body = hero("Repository review", "Line-by-line desk audit", "This page records checks over this session's own generated data and pages. It is a structural audit, not a substitute for reading the linked official pages.")
    checks = [
        ("Fixture source link", f"{len(FIXTURES)}/{len(FIXTURES)} rows have an official source ID and public manual-review URL."),
        ("Official exact match/event", f"{len(official)}/{len(FIXTURES)} rows are direct official-schedule entries; 2 are OLBG discovery-only and visibly held."),
        ("Market trace", f"{len(MARKETS)}/{len(MARKETS)} market rows carry a fixture ID, source-status explanation and withheld/low label."),
        ("Prediction prose", "1/1 narrative is 30+ words, names the selection, carries an official WST source link, and contains no prohibited prediction wording."),
        ("High confidence", "0 High labels; therefore no quota-driven high prose or out-of-band price claim exists."),
        ("Internal pages", "All dashboard routes and 15 category pages are generated by this script and checked by the session validator."),
    ]
    body += '<div class="table-wrap"><table><thead><tr><th>Check</th><th>Result</th></tr></thead><tbody>' + ''.join(f'<tr><td><strong>{esc(a)}</strong></td><td>{esc(b)}</td></tr>' for a, b in checks) + '</tbody></table></div>'
    return shell("Desk audit", body, "audit.html")


def sport_page(key: str) -> str:
    name = slug_name(key)
    rows = [f for f in FIXTURES if f["sport"] == key]
    source = next((s for s in SOURCES.values() if s["sport"] == key), None)
    status = "Exact schedule rows retained" if any(f["status"] != "OLBG discovery only" for f in rows) else "No exact official fixture retained"
    text = f"<strong>{esc(status)}.</strong> " + (esc(source["result"]) if source else "No source record.")
    body = hero("Category ledger", name, text, f'<div class="actions"><a class="button" href="../sources.html">All sources</a><a class="button" href="../flagged.html">Flagged items</a></div>')
    body += '<section class="section"><div class="section-head"><h2>Fixture/event rows</h2><p>Blank is intentional when the source did not publish a field.</p></div>' + fixture_table(rows, "sports/" + key + ".html") + '</section>'
    sports_markets = [m for m in MARKETS if next(f for f in FIXTURES if f["id"] == m["fixture_id"])["sport"] == key]
    body += '<section class="section"><div class="section-head"><h2>Markets investigated</h2><p>No label implies a line or quote unless the row says so.</p></div>' + market_table(sports_markets, "sports/" + key + ".html") + '</section>'
    if source:
        body += f'<section class="panel"><h2>Source record</h2><p>{esc(source["result"])}</p>{source_link(next(k for k,v in SOURCES.items() if v is source), "sports/" + key + ".html")}</section>'
    return shell(name, body, "sports/" + key + ".html")


CSS = r''':root{--ink:#17221d;--muted:#596760;--bg:#f5f7f5;--card:#fff;--line:#d8e1da;--green:#135b3d;--greenlite:#e8f3ed;--amber:#825a09;--amberlite:#fff3dc;--red:#8c2d25;--redlite:#fcedeb;--mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}a{color:var(--green);text-decoration:none}a:hover{text-decoration:underline}header{background:#10281d;color:#fff;position:sticky;top:0;z-index:4;border-bottom:1px solid #274839}.nav{max-width:1440px;margin:auto;padding:10px 24px;display:flex;align-items:center;justify-content:space-between;gap:18px;flex-wrap:wrap}.brand{color:#fff;font-weight:750;letter-spacing:-.01em}.brand span{font-size:10px;color:#aed0bd;letter-spacing:.08em;margin-left:7px}.nav nav{display:flex;gap:3px;flex-wrap:wrap}.nav nav a{color:#d6e8de;border-radius:6px;padding:5px 9px;font-size:13px;font-weight:600}.nav nav a.active,.nav nav a:hover{background:#28513d;color:#fff;text-decoration:none}main{max-width:1440px;margin:auto;padding:28px 24px 44px}.hero{background:var(--card);border:1px solid var(--line);border-radius:11px;padding:22px 24px;display:flex;align-items:flex-start;justify-content:space-between;gap:20px;flex-wrap:wrap}.hero>div:first-child{max-width:930px}.hero h1{font-size:27px;line-height:1.18;letter-spacing:-.025em;margin:0 0 8px}.hero p{color:var(--muted);margin:0}.kicker{color:var(--green)!important;font-size:11px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;margin:0 0 6px!important}.actions{display:flex;gap:8px;flex-wrap:wrap}.button{display:inline-block;border:1px solid var(--line);border-radius:6px;padding:8px 11px;font-size:13px;font-weight:700;background:#fff;color:var(--ink)}.button.primary{background:var(--green);border-color:var(--green);color:#fff}.button:hover{text-decoration:none;opacity:.94}.metrics{display:grid;grid-template-columns:repeat(4,minmax(155px,1fr));gap:12px;margin:18px 0}.metrics article,.panel{background:var(--card);border:1px solid var(--line);border-radius:9px;padding:15px 17px}.metrics b{display:block;font-size:28px;line-height:1.1;letter-spacing:-.03em}.metrics span{font-weight:700;display:block;margin:4px 0}.metrics small,.sub{font-size:12px;color:var(--muted)}.section{margin-top:25px}.section-head{display:flex;justify-content:space-between;gap:16px;align-items:baseline;flex-wrap:wrap;margin:0 0 10px}.section-head h2{font-size:19px;margin:0;letter-spacing:-.015em}.section-head p{font-size:13px;color:var(--muted);margin:0}.callout{background:#fff9e8;border:1px solid #ecd89d;border-radius:8px;padding:12px 15px;margin:15px 0;color:#604609}.table-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:9px;background:var(--card)}table{width:100%;border-collapse:collapse;font-size:13px}th,td{padding:10px 12px;vertical-align:top;text-align:left;border-bottom:1px solid #e7ede8}th{background:#eff4f0;font-size:10.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);white-space:nowrap}tbody tr:last-child td{border-bottom:0}tbody tr:hover{background:#fbfdfb}.id,.num{font-family:var(--mono);font-size:12px}.pill{display:inline-block;border-radius:999px;padding:2px 7px;font-size:11px;font-weight:750;white-space:nowrap}.pill.ok,.pill.low{background:#e9f3ed;color:#17603f}.pill.warn,.pill.withheld{background:var(--amberlite);color:var(--amber)}.pill.sport{background:#e8f0ec;color:#305845}.blank{font-style:italic;color:var(--red);font-size:12px}.source{display:inline-block;border:1px solid var(--line);background:#f3f6f3;border-radius:5px;padding:2px 7px;font-size:11.5px;font-weight:700;margin:1px 2px 1px 0}.source.discovery{background:#edf4f0;color:#245d40}.sport-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:10px}.sport-card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:13px 14px;display:grid;gap:5px;color:var(--ink)}.sport-card:hover{border-color:var(--green);text-decoration:none}.sport-card>span{font-weight:750}.sport-card small{font-size:12px;color:var(--muted)}.two{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.panel h2,.panel h3{margin:0 0 8px;font-size:17px}.panel p{margin:0 0 10px;color:var(--muted)}.prediction{margin-top:18px;border:1px solid var(--line);background:var(--card);border-radius:10px;padding:18px}.prediction-top{display:flex;justify-content:space-between;gap:12px}.prediction h2{margin:0;font-size:20px}.selection{margin:12px 0;padding:9px 12px;background:#edf4f0;border-left:3px solid var(--green);display:flex;gap:9px 16px;flex-wrap:wrap;font-size:13px}.prediction-meta{border-top:1px dashed var(--line);padding-top:10px;display:flex;gap:10px;align-items:center;flex-wrap:wrap;color:var(--muted);font-size:12px}.controls{display:flex;gap:10px;align-items:center;flex-wrap:wrap;background:#fff;border:1px solid var(--line);border-radius:8px;padding:10px 12px;margin:15px 0}.controls label{font-size:12px;font-weight:700;color:var(--muted);display:flex;gap:6px;align-items:center}.controls input,.controls select{font:13px inherit;padding:6px 8px;border:1px solid var(--line);border-radius:5px}.controls [data-count]{margin-left:auto;color:var(--muted);font-size:12px}ol{padding-left:20px;margin:0}li{margin-bottom:7px}footer{max-width:1440px;margin:auto;padding:18px 24px 35px;border-top:1px solid var(--line);color:var(--muted);font-size:12px;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}.empty{padding:18px;background:#fff;border:1px dashed var(--line);border-radius:8px;color:var(--muted)}@media(max-width:800px){main{padding:18px 14px 35px}.nav{padding:10px 14px}.metrics{grid-template-columns:repeat(2,1fr)}.two{grid-template-columns:1fr}.hero h1{font-size:23px}}@media(max-width:470px){.metrics{grid-template-columns:1fr}.nav{gap:8px}}'''

JS = r'''(()=>{const f=document.querySelector('[data-filter]'),q=document.querySelector('[data-search]'),c=document.querySelector('[data-count]');if(!f&&!q)return;const rows=[...document.querySelectorAll('tbody tr[data-sport]')];const run=()=>{let n=0;rows.forEach(r=>{const hit=(!f||!f.value||r.dataset.sport===f.value)&&(!q||!q.value||r.textContent.toLowerCase().includes(q.value.toLowerCase()));r.hidden=!hit;if(hit)n++});if(c)c.textContent=`${n} row${n===1?'':'s'} shown`};f?.addEventListener('change',run);q?.addEventListener('input',run);run()})();'''


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def dump(path: Path, payload: Any) -> None:
    write(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def build() -> None:
    # Machine-readable artifacts
    coverage = []
    for sport, label in SPORTS:
        rows = [f for f in FIXTURES if f["sport"] == sport]
        source_id = next((k for k, v in SOURCES.items() if v["sport"] == sport), None)
        coverage.append({"sport": label, "sport_key": sport, "exact_official_rows": sum(r["status"] != "OLBG discovery only" for r in rows), "olbg_discovery_only_rows": sum(r["status"] == "OLBG discovery only" for r in rows), "source_id": source_id, "source_status": SOURCES[source_id]["result"] if source_id else ""})
    dump(DATA / "sources.json", {"session": SESSION, "observed_window": OBSERVED_WINDOW, "sources": [{"id": k, **v} for k, v in SOURCES.items()]})
    dump(DATA / "fixtures.json", {"session": SESSION, "observed_window": OBSERVED_WINDOW, "fixtures": FIXTURES})
    dump(DATA / "markets.json", {"session": SESSION, "markets": MARKETS})
    dump(DATA / "predictions.json", {"session": SESSION, "predictions": PREDICTIONS})
    dump(DATA / "flagged.json", {"session": SESSION, "flags": FLAGS})
    dump(DATA / "coverage.json", {"session": SESSION, "coverage": coverage})
    dump(DATA / "olbg_discovery.json", {"session": SESSION, "observed_window": OBSERVED_WINDOW, "policy": "Discovery only; no quote or official factual claim is created from OLBG.", "observed_routes": OLBG_SOURCES, "market_families": {"Mark Williams v Jak Jones": ["Win Match", "Handicap Betting", "Frame Betting"], "Krzysztof Ratajski v Kevin Doets": ["Win Match 2-way", "Total 180s", "Most 180s", "Handicap 2-way", "Total Legs"], "Moycullen v Salthill-Knocknacarra": ["FT Result", "Handicap"]}})
    summary = {"session": SESSION, "task": TASK, "observed_window": OBSERVED_WINDOW, "sports": 15, "fixture_rows": len(FIXTURES), "exact_official_schedule_rows": sum(f["status"] != "OLBG discovery only" for f in FIXTURES), "olbg_discovery_only_rows": sum(f["status"] == "OLBG discovery only" for f in FIXTURES), "market_rows": len(MARKETS), "originated_price_rows": 1, "high_confidence_picks": 0, "low_research_notes": len(PREDICTIONS), "flags": len(FLAGS)}
    dump(DATA / "summary.json", summary)
    dump(DATA / "observations.json", {"session": SESSION, "window": OBSERVED_WINDOW, "method": "Public pages were read through the session retrieval tool. Only concise field-level notes are stored; no full response body or fabricated request metadata is retained.", "observations": [{"source_id": k, "url": v["url"], "retained_excerpt": v["result"]} for k, v in SOURCES.items()]})

    # Pages and assets
    write(SITE / "assets" / "style.css", CSS)
    write(SITE / "assets" / "app.js", JS)
    write(SITE / "index.html", index_page())
    write(SITE / "matches.html", matches_page())
    write(SITE / "markets.html", markets_page())
    write(SITE / "predictions.html", predictions_page())
    write(SITE / "sources.html", sources_page())
    write(SITE / "reverse-engineering.html", reverse_engineering_page())
    write(SITE / "flagged.html", flagged_page())
    write(SITE / "methodology.html", methodology_page())
    write(SITE / "audit.html", audit_page())
    for key, _ in SPORTS:
        write(SITE / "sports" / f"{key}.html", sport_page(key))

    # A concise reproducibility record, no claim that a structural check freshly recertifies sources.
    report = f'''# Session {SESSION} — {TASK}\n\n## 24 October evidence-first desk\n\n- **Observation window:** {OBSERVED_WINDOW}\n- **Scope:** the exact 15 requested sports only.\n- **Retained fixture/event rows:** {summary['fixture_rows']} ({summary['exact_official_schedule_rows']} direct official schedule rows; {summary['olbg_discovery_only_rows']} OLBG discovery-only rows, held blank).\n- **Market investigation rows:** {summary['market_rows']}; one explicitly Low own fair display; all remaining lines withheld.\n- **Executive High picks:** 0. The requested five-per-sport High target is short by 75 and is published on the Flagged page rather than filled with weak claims.\n\n## Source boundary\n\nThe Sources page and `data/0c9bc692/sources.json` list every official page read and a short note of the fields retained. Official links are manual-review links for every table row. OLBG links are clearly labelled discovery only: community tip counts and labels were not treated as official facts or bookmaker prices.\n\n## Clear outcome\n\nThe dashboard makes the executive outcome explicit: there are no High-confidence picks. The only selection is a **Low** Mark Williams research line, accompanied by an 83-word source-bounded explanation. It is not an executive recommendation. Darts and Gaelic OLBG discoveries remain unconfirmed; several sports have a source-status record but no exact fixture in the retained response.\n\n## Reproducibility\n\n```sh\npython3 scripts/s0c9bc692_build.py\npython3 scripts/s0c9bc692_validate.py\n```\n\nThe validator checks local source IDs/URLs, row linking, market linkage, prediction length and prohibited prediction wording, the one disclosed fair-price arithmetic, generated routes, and no conflict markers. It cannot substitute for re-reading dynamic official pages.\n'''
    write(REPORT, report)


if __name__ == "__main__":
    build()
    print(f"built {SITE.relative_to(ROOT)}/ and {DATA.relative_to(ROOT)}/")
