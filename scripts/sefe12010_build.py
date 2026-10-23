#!/usr/bin/env python3
"""Session efe12010 — build the desk website and its data exports.

Writes:
    data/efe12010/*.json   machine-readable exports
    data/efe12010/*.csv    spreadsheet exports
    efe12010/*.html        the published desk (landing page + twelve sections)
    efe12010/sports/*.html one page per covered sport (15)
    efe12010/assets/*      this desk's own stylesheet and script

Run from anywhere:  python3 scripts/sefe12010_build.py
"""
from __future__ import annotations

import csv
import html
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import sefe12010_data as D                      # noqa: E402
import sefe12010_lines as L                     # noqa: E402
from sefe12010_predictions import PREDICTIONS   # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "efe12010"
DATA = ROOT / "data" / "efe12010"
DESK = "efe12010"
BUILT = os.environ.get("EFE_BUILD_STAMP", "2026-10-23T17:05:00Z")
NOW = "2026-10-23T16:26:40Z"   # sandbox clock at harvest time, used for elapsed checks

SPORT_NAME = dict(D.SPORTS)
SPORT_ORDER = [s for s, _ in D.SPORTS]

e = html.escape


# ============================================================== page furniture
NAV = [
    ("Desk", [
        ("index.html", "Overview", "M3 3h7v7H3zM14 3h7v7h-7zM3 14h7v7H3zM14 14h7v7h-7z"),
        ("executive-summary.html", "Executive summary", "M4 4h16v16H4zM8 9h8M8 13h8M8 17h5"),
        ("high-confidence.html", "High-confidence picks", "M12 3l2.6 6.4L21 12l-6.4 2.6L12 21l-2.6-6.4L3 12l6.4-2.6z"),
        ("predictions.html", "All written calls", "M4 19V5m4 14V9m4 10V3m4 16v-7m4 7V7"),
    ]),
    ("Data", [
        ("matches.html", "Match ledger", "M4 6h16M4 12h16M4 18h16"),
        ("markets.html", "Market explorer", "M4 20V10m7 10V4m7 16v-7M2 22h20"),
        ("sports.html", "Sports index", "M12 3a9 9 0 100 18 9 9 0 000-18zM3 12h18M12 3c-5 5-5 13 0 18M12 3c5 5 5 13 0 18"),
        ("coverage.html", "Coverage report", "M12 3v18M3 12h18"),
    ]),
    ("Evidence", [
        ("sources.html", "Sources & evidence", "M10 13a5 5 0 007 0l3-3a5 5 0 00-7-7l-2 2M14 11a5 5 0 00-7 0l-3 3a5 5 0 007 7l2-2"),
        ("flagged.html", "Flagged for Review", "M5 21V4c5-4 9 4 14 0v10c-5 4-9-4-14 0"),
        ("analysis.html", "Analysis & findings", "M4 20V10m7 10V4m7 16v-7M2 22h20"),
        ("reverse-engineering.html", "OLBG reverse-engineering", "M8 5L2 12l6 7M16 5l6 7-6 7M14 3l-4 18"),
        ("methodology.html", "Methodology", "M12 5v16M3 4c3-1 6-1 9 1 3-2 6-2 9-1v15c-3-1-6-1-9 1-3-2-6-2-9-1z"),
    ]),
]

CSP = ("default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
       "img-src 'self' data:; object-src 'none'; base-uri 'none'; form-action 'none'; "
       "connect-src 'none'")


def icon(path: str, size: int = 17) -> str:
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true"><path d="{path}"/></svg>')


def nav_html(active: str, depth: int) -> str:
    up = "../" * depth
    out = []
    for label, items in NAV:
        out.append(f'<div class="nav-label">{label}</div>')
        for href, text, d in items:
            cls = "nav-link active" if href == active else "nav-link"
            cur = ' aria-current="page"' if href == active else ""
            out.append(f'<a class="{cls}" href="{up}{href}"{cur}>{icon(d)}<span>{e(text)}</span></a>')
    return "".join(out)


def page(active: str, title: str, heading: str, lede: str, body: str, depth: int = 0,
         counts: dict | None = None) -> str:
    up = "../" * depth
    counts = counts or {}
    chips = "".join(
        f'<span class="chip"><b>{e(str(v))}</b> {e(k)}</span>' for k, v in counts.items())
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<meta name="description" content="{e(lede)[:180]}">
<title>{e(title)} · Desk {DESK}</title>
<link rel="stylesheet" href="{up}assets/style.css">
<script defer src="{up}assets/app.js"></script>
</head><body>
<a class="skip" href="#main">Skip to content</a>
<div class="shade" id="shade" hidden></div>
<aside class="sidebar" id="sidebar" aria-label="Desk navigation">
  <a class="brand" href="{up}index.html"><span class="mark">{icon("M4 20V10m7 10V4m7 16v-7M2 22h20", 22)}</span>
  <span><strong>OLBG REVERSE DESK</strong><small>session {DESK}</small></span></a>
  <nav>{nav_html(active, depth)}</nav>
  <div class="side-foot">
    <div class="card-note"><strong>Evidence first</strong>
    <p>Blank means no official source could confirm it. Nothing on this desk is inferred or filled in.</p></div>
    <a class="back" href="{up}../index.html">&#8592; Project home</a>
    <a class="back" href="{up}../archive.html">All research desks</a>
    <p>Independent research · not affiliated with OLBG</p>
  </div>
</aside>
<div class="layout">
<header class="topbar">
  <button class="menu" id="menu" aria-label="Open navigation" aria-expanded="false" aria-controls="sidebar">{icon("M3 6h18M3 12h18M3 18h18", 20)}</button>
  <div class="crumb"><span>Desk {DESK} <span aria-hidden="true">/</span></span><strong>{e(heading)}</strong></div>
  <div class="top-right"><span class="dot"></span><span>Snapshot {BUILT[:10]}</span>
  <a href="https://github.com/buffedlizard55-lab/OLBG1" rel="noopener noreferrer" target="_blank">GitHub</a></div>
</header>
<main class="main" id="main">
<header class="head">
  <div><p class="eyebrow">15-sport reverse-engineering desk</p><h1>{e(heading)}</h1><p class="lede">{e(lede)}</p></div>
  <div class="chips">{chips}</div>
</header>
{body}
<footer class="footer">
  <span>Independent research, not betting advice. 18+ · never stake what you cannot afford to lose.</span>
  <span>Built {BUILT} · <a href="{up}methodology.html">how this desk works</a> · <a href="{up}flagged.html">flagged items</a></span>
</footer>
</main></div></body></html>"""


def panel(title: str, inner: str, sub: str = "", extra: str = "") -> str:
    s = f'<p class="sub">{sub}</p>' if sub else ""
    return (f'<section class="panel"><div class="panel-head"><div><h2>{e(title)}</h2>{s}</div>'
            f'{extra}</div>{inner}</section>')


def table(headers: list[str], rows: list[list[str]], cls: str = "", note: str = "") -> str:
    if not rows:
        return f'<p class="empty">{e(note or "No rows.")}</p>'
    th = "".join(f"<th>{e(h)}</th>" for h in headers)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return (f'<div class="t-wrap"><table class="{cls}"><thead><tr>{th}</tr></thead>'
            f'<tbody>{tr}</tbody></table></div>')


def src_link(url: str, label: str = "Official source") -> str:
    return (f'<a class="src" href="{e(url)}" target="_blank" rel="noopener noreferrer">'
            f'{e(label)} {icon("M14 3h7v7M21 3L10 14M10 3H4v17h17v-6", 11)}</a>')


def price_cell(bp: dict, big: bool = False) -> str:
    """Render a selection's price. The desk leads with the fair price, because that is
    the number the -250/+10000 band is measured against; the margin-loaded quote is
    shown underneath it."""
    if not bp:
        return blank("Not priced")
    cls = "odds big" if big else "odds"
    return (f'<span class="{cls}">{e(bp["fair_american"])}</span><br>'
            f'<span class="muted">{pct(bp["probability"])} · quoted {e(bp["american"])}</span>')


STATE_PILL = {
    "verified": '<span class="pill ok">confirmed</span>',
    "partial": '<span class="pill info">confirmed · not priced</span>',
    "unverified": '<span class="pill warn">unconfirmed</span>',
}


def state_pill(status: str) -> str:
    return STATE_PILL.get(status, STATE_PILL["unverified"])


def badge(tier: str) -> str:
    t = tier.lower()
    if t.startswith("high"):
        k = "hi"
    elif t.startswith("medium"):
        k = "md"
    elif t == "unrated":
        k = "un"
    else:
        k = "lo"
    return f'<span class="badge {k}">{e(tier)}</span>'


def blank(reason: str = "") -> str:
    t = f' title="{e(reason)}"' if reason else ""
    return f'<span class="blank"{t}>—</span>'


def when(utc: str) -> str:
    if not utc:
        return blank("No official start time published")
    return f'<time datetime="{e(utc)}">{e(utc.replace("T", " ").replace(":00Z", "Z"))}</time>'


MONTHS = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
          "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}


def olbg_utc(t: str) -> str:
    """Convert an OLBG clock string to UTC. OLBG renders in the viewer zone, which
    resolved to Eastern Daylight Time (UTC-4) for this session, so add four hours."""
    t = (t or "").strip()
    if not t or t == "ante-post":
        return ""
    parts = t.split()
    hhmm = next((p for p in parts if ":" in p), None)
    if hhmm is None:
        return ""
    hh, mm = (int(x) for x in hhmm.split(":"))
    if parts[0] == "Today":
        day, month = 23, 10
    elif parts[0] == "Tomorrow":
        day, month = 24, 10
    elif parts[0].isdigit() and len(parts) > 1 and parts[1] in MONTHS:
        day, month = int(parts[0]), MONTHS[parts[1]]
    else:
        return ""
    base = datetime(2026, month, day, hh, mm, tzinfo=timezone.utc)
    return (base + timedelta(hours=4)).strftime("%Y-%m-%dT%H:%MZ")


def pct(p: float) -> str:
    return f"{p * 100:.1f}%"


def slug_href(sport: str, depth: int) -> str:
    up = "../" * depth
    return f'{up}sports/{sport}.html'


# ====================================================================== build
def main() -> None:
    fixtures = L.build_all()
    for fx in fixtures:
        fx["prediction"] = PREDICTIONS.get(fx["id"])

    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "sports").mkdir(exist_ok=True)
    (SITE / "assets").mkdir(exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)

    priced = [f for f in fixtures if f["markets"]]
    unpriced = [f for f in fixtures if not f["markets"]]
    highs = [f for f in priced if f["confidence"] == "high"]
    highs.sort(key=lambda f: -f["band_pick"]["probability"])
    mediums = [f for f in priced if f["confidence"] == "medium"]
    flagged = [f for f in fixtures if f["flags"] or f["status"] != "verified"]
    n_markets = sum(len(f["markets"]) for f in fixtures)
    n_outcomes = sum(len(m["outcomes"]) for f in fixtures for m in f["markets"])
    covered = sorted({f["sport"] for f in priced})

    write_exports(fixtures, priced, highs)
    write_assets()

    build_index(fixtures, priced, unpriced, highs, mediums, covered, n_markets, n_outcomes)
    build_exec(highs, mediums, covered)
    build_high(highs)
    build_predictions(priced)
    build_matches(fixtures)
    build_markets(fixtures, n_markets, n_outcomes)
    build_sports_index(fixtures, priced, highs)
    build_coverage(fixtures, priced, highs)
    build_sources()
    build_flagged(fixtures, flagged)
    build_analysis(fixtures, priced, highs)
    build_reverse()
    build_methodology()
    for sport, name in D.SPORTS:
        build_sport_page(sport, name, fixtures)

    print(f"desk {DESK}: {len(fixtures)} fixtures, {len(priced)} priced, {len(highs)} high, "
          f"{n_markets} markets, {n_outcomes} outcomes, "
          f"{len(list(SITE.rglob('*.html')))} pages")


# ------------------------------------------------------------------- exports
def write_exports(fixtures, priced, highs) -> None:
    (DATA / "fixtures.json").write_text(json.dumps({
        "desk": DESK, "built_utc": BUILT, "harvest_utc": NOW,
        "sports": dict(D.SPORTS), "count": len(fixtures), "fixtures": fixtures,
    }, indent=1), encoding="utf-8")

    (DATA / "olbg_harvest.json").write_text(json.dumps({
        "desk": DESK, "captured_utc": NOW,
        "note": ("Discovery layer only. OLBG is where these events were found; it is never "
                 "used to confirm a sporting fact. Clock values are as rendered by OLBG, "
                 "which serves Eastern Daylight Time to this session (UTC-4)."),
        "hubs": D.OLBG_HUBS, "timezone_evidence": D.TZ_EVIDENCE,
        "rows": D.OLBG_HARVEST,
    }, indent=1), encoding="utf-8")

    (DATA / "sources.json").write_text(json.dumps({
        "desk": DESK, "official": D.SOURCES, "blocked": D.BLOCKED_SOURCES,
    }, indent=1), encoding="utf-8")

    (DATA / "predictions.json").write_text(json.dumps({
        "desk": DESK, "built_utc": BUILT,
        "entries": [{
            "fixture_id": f["id"], "sport": f["sport"], "competition": f["competition"],
            "event": f["event"], "start_utc": f["start_utc"],
            "tier": f["tier"], "confidence": f["confidence"],
            "market": f["band_pick"]["market"], "selection": f["band_pick"]["selection"],
            "probability": f["band_pick"]["probability"],
            "fair_american": f["band_pick"]["fair_american"],
            "quoted_american": f["band_pick"]["american"],
            "text": f["prediction"]["text"], "availability": f["prediction"]["availability"],
            "sources": [s["url"] for s in f["sources"]],
        } for f in priced if f.get("prediction")],
    }, indent=1), encoding="utf-8")

    (DATA / "flags.json").write_text(json.dumps({
        "desk": DESK, "built_utc": BUILT,
        "fixture_flags": [{"fixture_id": f["id"], "sport": f["sport"], "event": f["event"],
                           "status": f["status"], "flags": f["flags"],
                           "unavailable_markets": f["unavailable_markets"]}
                          for f in fixtures if f["flags"] or f["unavailable_markets"]],
        "blocked_sources": D.BLOCKED_SOURCES,
        "elapsed_at_harvest": [{"sport": s, "detail": d, "source": D.SOURCES[k]["url"]}
                               for s, d, k in D.ELAPSED],
    }, indent=1), encoding="utf-8")

    with (DATA / "matches.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["fixture_id", "sport", "competition", "event", "start_utc", "venue",
                    "status", "selection", "market", "probability", "fair_american",
                    "quoted_american", "tier", "source_url"])
        for f in fixtures:
            bp = f["band_pick"] or {}
            w.writerow([f["id"], f["sport"], f["competition"], f["event"], f["start_utc"],
                        f["venue"], f["status"], bp.get("selection", ""), bp.get("market", ""),
                        bp.get("probability", ""), bp.get("fair_american", ""),
                        bp.get("american", ""), f["tier"],
                        f["sources"][0]["url"] if f["sources"] else ""])

    with (DATA / "markets.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["fixture_id", "sport", "event", "market", "selection", "probability",
                    "fair_decimal", "fair_american", "quoted_decimal", "quoted_american",
                    "in_price_band"])
        for f in fixtures:
            for m in f["markets"]:
                for o in m["outcomes"]:
                    w.writerow([f["id"], f["sport"], f["event"], m["label"], o["selection"],
                                o["probability"], o["fair_odds"], o["fair_american"],
                                o["odds"], o["american"], "yes" if o["in_band"] else "no"])


# -------------------------------------------------------------------- assets
def write_assets() -> None:
    (SITE / "assets" / "style.css").write_text(CSS, encoding="utf-8")
    (SITE / "assets" / "app.js").write_text(JS, encoding="utf-8")


# --------------------------------------------------------------------- pages
def build_index(fixtures, priced, unpriced, highs, mediums, covered, n_markets, n_outcomes):
    kpi = [
        ("Fixtures discovered", len(fixtures), "Every event pulled off the fifteen OLBG hubs."),
        ("Confirmed on an official source", len([f for f in fixtures if f["status"] in ("verified", "partial")]),
         "Start time and both competitors matched against a governing body, league or tour feed."),
        ("Priced by this desk", len(priced), "Fixtures with enough official input to originate a line."),
        ("Markets originated", n_markets, f"{n_outcomes} individual priced outcomes."),
        ("High-confidence selections", len(highs), "Inside the −250 to +10000 band."),
        ("Published blank and flagged", len(unpriced), "No official source, so no number was invented."),
    ]
    cards = "".join(
        f'<article class="kpi"><p class="k-label">{e(t)}</p><p class="k-val">{v}</p>'
        f'<p class="k-sub">{e(s)}</p></article>' for t, v, s in kpi)

    top = table(
        ["Sport", "Fixture", "Start (UTC)", "Selection", "Our price (fair)", "Confidence"],
        [[f'<a href="{slug_href(f["sport"],0)}">{e(SPORT_NAME[f["sport"]])}</a>',
          f'<strong>{e(f["event"])}</strong><br><span class="muted">{e(f["competition"])}</span>',
          when(f["start_utc"]),
          f'<strong>{e(f["band_pick"]["selection"])}</strong><br>'
          f'<span class="muted">{e(f["band_pick"]["market"])}</span>',
          price_cell(f["band_pick"]),
          badge(f["tier"])] for f in highs[:8]], "lined")

    sport_rows = []
    for sport in SPORT_ORDER:
        sf = [f for f in fixtures if f["sport"] == sport]
        sp = [f for f in sf if f["markets"]]
        sh = [f for f in sp if f["confidence"] == "high"]
        state = ("<span class='pill ok'>priced</span>" if sp else
                 "<span class='pill warn'>blank &amp; flagged</span>" if sf else
                 "<span class='pill none'>nothing listed</span>")
        sport_rows.append([
            f'<a href="{slug_href(sport,0)}"><strong>{e(SPORT_NAME[sport])}</strong></a>',
            str(len(sf)), str(len(sp)), str(len(sh)), state,
            src_link(D.OLBG_HUBS.get(sport, "https://www.olbg.com/betting-tips"), "OLBG hub")])

    body = f"""
<div class="notice">{icon("M12 3L2 21h20zM12 9v5m0 3v.01")}
<p><strong>This is a research snapshot, not a live feed.</strong> Every row below was taken on
{e(NOW)}. Prices are originated here from official inputs — none of them is copied from a
bookmaker or from OLBG. Events that had already started at harvest time are listed on the
<a href="flagged.html">Flagged for Review</a> page and are not published as picks.</p></div>

<div class="kpis">{cards}</div>

{panel("Today's strongest calls", top,
       "The eight highest-probability selections inside the published price band. "
       "The full ladder is on the executive summary.",
       '<a class="btn" href="executive-summary.html">Executive summary</a>')}

{panel("Coverage by sport", table(
    ["Sport", "Discovered", "Priced", "High-confidence", "State", "Discovery hub"],
    sport_rows, "lined"),
    "All fifteen requested sports are listed. Where an official source could not be reached the "
    "row count is published with blank prices rather than estimated ones.")}

<div class="grid2">
{panel("What this desk did", '''<div class="prose">
<ol>
<li><strong>Harvested</strong> all fifteen OLBG sport hubs and recorded every card, its clock, its
tip counts and its consensus percentage.</li>
<li><strong>Worked out the clock.</strong> OLBG renders times in the viewer's zone; for this session
that is Eastern Daylight Time, so every OLBG clock here is converted at +4 hours to UTC. The proof
is on the reverse-engineering page.</li>
<li><strong>Re-sourced every fixture</strong> against the governing body, league or tour that owns
it — NHL, MLB, EuroLeague, ATP, World Snooker Tour, Formula 1 and Cricket Australia.</li>
<li><strong>Originated our own prices</strong> from those official inputs, across win, handicap,
total, team total, run line, puck line, set betting, frame handicap, podium and points markets.</li>
<li><strong>Published the gaps.</strong> Nine sports could not be confirmed on an official source;
their rows ship blank with the exact URL and failure recorded.</li>
</ol></div>''')}
{panel("Reading the prices", f'''<div class="prose">
<p>Headline prices on this desk are <em>fair</em> prices — the straight translation of our own
probability, with no margin at all. That is the number the confidence band is measured against. A
<em>quoted</em> price is shown beside it, carrying a flat loading so a two-way book totals
{100 * (1 + 0.045):.1f}%.</p>
<p>A selection is only eligible for the High label if its fair price sits between
<strong>−250 and +10000</strong>. Anything shorter than −250 is held at Medium with a visible
price-cap note, and the desk publishes an in-band derivative instead. That is why several
high-confidence calls below are totals or handicaps rather than straight winners.</p>
<p><a href="methodology.html">Full method, formulas and confidence bands →</a></p>
</div>''')}
</div>

{panel("Downloads", f'''<div class="prose"><ul>
<li><a href="../data/{DESK}/matches.csv">matches.csv</a> — one row per fixture with the headline selection</li>
<li><a href="../data/{DESK}/markets.csv">markets.csv</a> — every priced outcome, {n_outcomes} rows</li>
<li><a href="../data/{DESK}/fixtures.json">fixtures.json</a> — full records including the evidence ledger</li>
<li><a href="../data/{DESK}/predictions.json">predictions.json</a> — the written calls</li>
<li><a href="../data/{DESK}/olbg_harvest.json">olbg_harvest.json</a> — the raw discovery layer</li>
<li><a href="../data/{DESK}/sources.json">sources.json</a> — official sources read, and the ones that failed</li>
<li><a href="../data/{DESK}/flags.json">flags.json</a> — every flag raised</li>
</ul></div>''')}
"""
    (SITE / "index.html").write_text(page(
        "index.html", "Overview", "Fifteen-sport desk overview",
        "Reverse-engineered from OLBG's public tip hubs, re-sourced against official feeds and "
        "priced independently.", body,
        counts={"sports": 15, "fixtures": len(fixtures), "high picks": len(highs)}),
        encoding="utf-8")


def build_exec(highs, mediums, covered):
    rows = []
    for i, f in enumerate(highs, 1):
        p = f["prediction"]
        rows.append([
            f'<span class="rank">{i}</span>',
            f'<a href="{slug_href(f["sport"],0)}">{e(SPORT_NAME[f["sport"]])}</a>',
            f'<strong>{e(f["event"])}</strong><br><span class="muted">{e(f["competition"])}</span>',
            when(f["start_utc"]),
            f'<strong>{e(f["band_pick"]["selection"])}</strong><br>'
            f'<span class="muted">{e(f["band_pick"]["market"])}</span>',
            f'<span class="odds">{e(f["band_pick"]["fair_american"])}</span><br>'
            f'<span class="muted">quoted {e(f["band_pick"]["american"])}</span>',
            pct(f["band_pick"]["probability"]),
            badge(f["tier"]),
            src_link(f["sources"][0]["url"]) if f["sources"] else blank(),
        ])

    med_rows = [[
        f'<a href="{slug_href(f["sport"],0)}">{e(SPORT_NAME[f["sport"]])}</a>',
        f'{e(f["event"])}', when(f["start_utc"]),
        f'<strong>{e(f["band_pick"]["selection"])}</strong>',
        f'<span class="odds">{e(f["band_pick"]["fair_american"])}</span><br>'
        f'<span class="muted">quoted {e(f["band_pick"]["american"])}</span>',
        pct(f["band_pick"]["probability"]), badge(f["tier"]),
        src_link(f["sources"][0]["url"]) if f["sources"] else blank(),
    ] for f in sorted(mediums, key=lambda f: -f["band_pick"]["probability"])]

    by_sport = {}
    for f in highs:
        by_sport.setdefault(f["sport"], []).append(f)
    short = []
    for sport in SPORT_ORDER:
        n = len(by_sport.get(sport, []))
        if n >= 5:
            state = "<span class='pill ok'>target met</span>"
        elif n:
            state = f"<span class='pill warn'>{5 - n} short</span>"
        else:
            state = "<span class='pill none'>none available</span>"
        short.append([e(SPORT_NAME[sport]), str(n), "5", state])

    body = f"""
<div class="notice">{icon("M12 3L2 21h20zM12 9v5m0 3v.01")}
<p><strong>{len(highs)} high-confidence selections</strong> cleared the band for today and the next
four days, across {len({f["sport"] for f in highs})} sports. Every one of them is written up in full
on the <a href="high-confidence.html">high-confidence page</a>. Selections are ordered by our own
probability, strongest first.</p></div>

{panel("Highest-confidence picks — today and upcoming", table(
    ["#", "Sport", "Fixture", "Start (UTC)", "Selection", "Our price (fair)", "Chance", "Tier", "Evidence"],
    rows, "lined sortable"),
    "All inside the −250 to +10000 band. Prices carry this desk's own margin; the fair price is "
    "shown on each fixture's market table.")}

{panel("The same calls, in one paragraph each", "".join(
    f'''<article class="call"><header><span class="tag">{e(SPORT_NAME[f["sport"]])}</span>
    <h3>{e(f["event"])}</h3>
    <p class="meta">{when(f["start_utc"])} · {e(f["venue"]) if f["venue"] else "venue not published"}</p></header>
    <p class="sel"><span class="sel-label">Selection</span>
    <strong>{e(f["band_pick"]["selection"])}</strong>
    <span class="odds">{e(f["band_pick"]["fair_american"])}</span>
    <span class="muted">quoted {e(f["band_pick"]["american"])}</span> {badge(f["tier"])}</p>
    <p>{e(f["prediction"]["text"])}</p>
    <p class="avail"><strong>Team news:</strong> {e(f["prediction"]["availability"])}</p>
    <p class="links">{" ".join(src_link(s["url"], s["name"]) for s in f["sources"])}</p>
    </article>''' for f in highs))}

{panel("Next rung down — Medium confidence", table(
    ["Sport", "Fixture", "Start (UTC)", "Selection", "Our price (fair)", "Chance", "Tier", "Evidence"],
    med_rows, "lined"),
    "Priced and written up, but short of the High floor. Published so the ladder is complete "
    "rather than cherry-picked.")}

{panel("Against the five-a-day target", table(
    ["Sport", "High-confidence calls", "Daily target", "State"], short, "lined"),
    "The brief asks for five high-confidence predictions per sport per day. Where the target is "
    "not met it is because the official evidence did not support a fifth call, not because the "
    "work stopped. The shortfall is itemised on the coverage report.")}
"""
    (SITE / "executive-summary.html").write_text(page(
        "executive-summary.html", "Executive summary", "Executive summary",
        "The strongest selections this desk can stand behind for today's and the next few days' "
        "fixtures, with the evidence behind each one.", body,
        counts={"high": len(highs), "medium": len(mediums), "sports with a high call": len(by_sport)}),
        encoding="utf-8")


def build_high(highs):
    cards = []
    for f in highs:
        p = f["prediction"]
        alt = [o for m in f["markets"] for o in m["outcomes"]
               if o["in_band"] and o["selection"] != f["band_pick"]["selection"]]
        alt.sort(key=lambda o: -o["probability"])
        alt_rows = [[e(o["selection"]), pct(o["probability"]), e(o["fair_american"]),
                     e(o["american"])] for o in alt[:5]]
        cards.append(f"""<article class="bigcall" id="{e(f["id"])}">
<header class="bc-head">
  <div><span class="tag">{e(SPORT_NAME[f["sport"]])}</span>{badge(f["tier"])}
  <h3>{e(f["event"])}</h3>
  <p class="meta">{e(f["competition"])} · {when(f["start_utc"])} · {e(f["venue"]) if f["venue"] else "venue not published"}</p></div>
  <div class="bc-price"><span class="bc-sel">{e(f["band_pick"]["selection"])}</span>
  <span class="bc-odds">{e(f["band_pick"]["fair_american"])}</span>
  <span class="bc-sub">{pct(f["band_pick"]["probability"])} chance · quoted {e(f["band_pick"]["american"])} with margin</span>
  <span class="bc-sub">{e(f["band_pick"]["market"])}</span></div>
</header>
<div class="bc-body">
  <div><h4>The call</h4><p>{e(p["text"])}</p>
  <h4>Availability</h4><p class="avail">{e(p["availability"])}</p></div>
  <div><h4>Official inputs used</h4><ul class="inputs">
  {"".join(f"<li>{e(i)}</li>" for i in f["inputs"]) or "<li>—</li>"}</ul>
  <h4>Evidence</h4><p class="links">{" ".join(src_link(s["url"], s["name"]) for s in f["sources"])}</p>
  {"<h4>Flags</h4><ul class='flags'>" + "".join(f"<li>{e(x)}</li>" for x in f["flags"]) + "</ul>" if f["flags"] else ""}
  </div>
</div>
<details><summary>Other in-band outcomes on this fixture</summary>
{table(["Outcome", "Chance", "Fair", "Quoted"], alt_rows, "mini")}</details>
</article>""")

    body = f"""
<div class="notice">{icon("M12 3l2.6 6.4L21 12l-6.4 2.6L12 21l-2.6-6.4L3 12l6.4-2.6z")}
<p>A selection reaches this page only when its fair price lands between <strong>−250 and
+10000</strong> and our probability clears 62%. Everything shorter than −250 is held back and
replaced by an in-band derivative on the same fixture, which is why some calls below are totals,
handicaps or podium markets rather than straight winners.</p></div>
{"".join(cards)}
"""
    (SITE / "high-confidence.html").write_text(page(
        "high-confidence.html", "High-confidence picks", "High-confidence picks",
        "Every selection that cleared the price band and the probability floor, written up in full.",
        body, counts={"calls": len(highs)}), encoding="utf-8")


def build_predictions(priced):
    order = sorted(priced, key=lambda f: (SPORT_ORDER.index(f["sport"]),
                                          -f["band_pick"]["probability"]))
    blocks = []
    cur = None
    for f in order:
        if f["sport"] != cur:
            cur = f["sport"]
            blocks.append(f'<h2 class="sport-rule" id="{e(cur)}">{e(SPORT_NAME[cur])}</h2>')
        p = f["prediction"]
        blocks.append(f"""<article class="call">
<header><span class="tag">{e(f["competition"])}</span>{badge(f["tier"])}
<h3>{e(f["event"])}</h3>
<p class="meta">{when(f["start_utc"])} · {e(f["venue"]) if f["venue"] else "venue not published"}</p></header>
<p class="sel"><span class="sel-label">Selection</span><strong>{e(p["selection"])}</strong>
<span class="odds">{e(f["band_pick"]["fair_american"])}</span>
<span class="muted">{pct(f["band_pick"]["probability"])} · quoted {e(f["band_pick"]["american"])} · {e(f["band_pick"]["market"])}</span></p>
<p>{e(p["text"])}</p>
<p class="avail"><strong>Team news:</strong> {e(p["availability"])}</p>
<p class="links">{" ".join(src_link(s["url"], s["name"]) for s in f["sources"])}</p>
</article>""")

    counts = {}
    for f in order:
        counts[SPORT_NAME[f["sport"]]] = counts.get(SPORT_NAME[f["sport"]], 0) + 1
    body = f"""
<div class="notice">{icon("M4 19V5m4 14V9m4 10V3m4 16v-7m4 7V7")}
<p>One written call for every fixture this desk was able to price — {len(order)} in total, each at
least thirty words and each written by hand against the official inputs listed with it. Fixtures
without an official source carry no call at all; they are on the
<a href="flagged.html">Flagged for Review</a> page.</p></div>
{"".join(blocks)}
"""
    (SITE / "predictions.html").write_text(page(
        "predictions.html", "All written calls", "All written calls",
        "Every priced fixture, with the selection and the reasoning behind it.", body,
        counts=counts), encoding="utf-8")


def build_matches(fixtures):
    rows = []
    for f in sorted(fixtures, key=lambda f: (SPORT_ORDER.index(f["sport"]),
                                             f["start_utc"] or "9", f["event"])):
        bp = f["band_pick"]
        status = state_pill(f["status"])
        rows.append([
            f'<a href="{slug_href(f["sport"],0)}">{e(SPORT_NAME[f["sport"]])}</a>',
            e(f["competition"]),
            f'<strong>{e(f["event"])}</strong>',
            when(f["start_utc"]),
            e(f["venue"]) if f["venue"] else blank("No official venue published"),
            status,
            (f'<strong>{e(bp["selection"])}</strong><br><span class="muted">{e(bp["market"])}</span>'
             if bp else blank("Not priced — no official input")),
            price_cell(bp),
            badge(f["tier"]),
            (src_link(f["sources"][0]["url"], f["sources"][0]["name"]) if f["sources"]
             else f'<a class="src warnlink" href="flagged.html">why this is blank</a>'),
        ])
    body = f"""
<div class="notice">{icon("M4 6h16M4 12h16M4 18h16")}
<p>Every fixture the desk found across the fifteen hubs, confirmed or not. A dash means the official
source did not publish that value and the desk refused to guess it. Use the filter to narrow by sport
or by state.</p></div>
<div class="toolbar">
  <label class="field"><span>Filter</span><input id="q" type="search" placeholder="team, competition, venue…" autocomplete="off"></label>
  <div class="segmented" id="seg">
    <button class="on" data-f="all">All</button><button data-f="confirmed">Confirmed</button>
    <button data-f="unconfirmed">Unconfirmed</button><button data-f="priced">Priced</button>
  </div>
  <a class="btn" href="../data/{DESK}/matches.csv" download>Download CSV</a>
</div>
{panel("Match ledger", table(
    ["Sport", "Competition", "Fixture", "Start (UTC)", "Venue", "State", "Selection",
     "Our price (fair)", "Tier", "Evidence"], rows, "lined sortable filterable"))}
"""
    (SITE / "matches.html").write_text(page(
        "matches.html", "Match ledger", "Match ledger",
        "The complete list of fixtures reverse-engineered from OLBG, with the official source "
        "behind each confirmed row.", body,
        counts={"rows": len(rows),
                "confirmed": len([f for f in fixtures
                                  if f["status"] in ("verified", "partial")])}),
        encoding="utf-8")


def build_markets(fixtures, n_markets, n_outcomes):
    blocks = []
    cur = None
    for f in sorted(fixtures, key=lambda f: (SPORT_ORDER.index(f["sport"]), f["event"])):
        if not f["markets"] and not f["unavailable_markets"]:
            continue
        if f["sport"] != cur:
            cur = f["sport"]
            blocks.append(f'<h2 class="sport-rule" id="{e(cur)}">{e(SPORT_NAME[cur])}</h2>')
        mt = []
        for m in f["markets"]:
            rows = [[
                e(o["selection"]),
                f'<span class="bar"><span style="width:{min(o["probability"]*100,100):.1f}%"></span></span> {pct(o["probability"])}',
                f'{o["fair_odds"]:.2f}', e(o["fair_american"]),
                f'<span class="odds">{e(o["american"])}</span>',
                '<span class="pill ok">in band</span>' if o["in_band"]
                else '<span class="pill warn">outside −250 / +10000</span>',
            ] for o in m["outcomes"]]
            mt.append(
                f'<div class="market"><div class="m-head"><h4>{e(m["label"])}</h4>'
                f'<span class="muted">book {m["book_pct"]:.1f}%'
                f'{"" if m["exclusive"] else " · multiple winners, column does not total 100%"}</span></div>'
                f'<p class="note">{e(m["note"])}</p>'
                + table(["Outcome", "Our chance", "Fair decimal", "Fair American", "Quoted",
                         "Price band"], rows, "mini") + "</div>")
        for u in f["unavailable_markets"]:
            mt.append(f'<div class="market blankm"><div class="m-head"><h4>{e(u["label"])}</h4>'
                      f'<span class="pill warn">not priced</span></div>'
                      f'<p class="note">{e(u["reason"])}</p></div>')
        blocks.append(f"""<section class="fx">
<header class="fx-head"><div><h3>{e(f["event"])}</h3>
<p class="meta">{e(f["competition"])} · {when(f["start_utc"])}</p></div>
<p class="links">{" ".join(src_link(s["url"], s["name"]) for s in f["sources"]) or blank("No official source")}</p>
</header>{"".join(mt)}</section>""")

    body = f"""
<div class="notice">{icon("M4 20V10m7 10V4m7 16v-7M2 22h20")}
<p>{n_markets} markets and {n_outcomes} individual outcomes, all originated here. The fair column is
the straight translation of our probability; the quoted column adds this desk's margin. Where a
market could not be priced from official data it is shown explicitly rather than omitted.</p></div>
{"".join(blocks)}
"""
    (SITE / "markets.html").write_text(page(
        "markets.html", "Market explorer", "Market explorer",
        "Every market this desk investigated, priced from official inputs, including the ones it "
        "could not price.", body,
        counts={"markets": n_markets, "outcomes": n_outcomes}), encoding="utf-8")


def build_sports_index(fixtures, priced, highs):
    cards = []
    for sport in SPORT_ORDER:
        sf = [f for f in fixtures if f["sport"] == sport]
        sp = [f for f in sf if f["markets"]]
        sh = [f for f in sp if f["confidence"] == "high"]
        state = ("ok" if sp else "warn")
        cards.append(f"""<a class="sportcard {state}" href="sports/{sport}.html">
<h3>{e(SPORT_NAME[sport])}</h3>
<p class="sc-nums"><span><b>{len(sf)}</b> fixtures</span><span><b>{len(sp)}</b> priced</span>
<span><b>{len(sh)}</b> high</span></p>
<p class="sc-state">{"Priced from official data" if sp else "Published blank — official source unavailable"}</p>
</a>""")
    body = f"""
<div class="notice">{icon("M12 3a9 9 0 100 18 9 9 0 000-18zM3 12h18")}
<p>All fifteen requested sports have a page, including the six where no official source could be
reached. Those pages carry the discovery rows and the exact reason the data is blank.</p></div>
<div class="sportgrid">{"".join(cards)}</div>
"""
    (SITE / "sports.html").write_text(page(
        "sports.html", "Sports index", "Sports index",
        "One page per sport in scope.", body, counts={"sports": 15}), encoding="utf-8")


def build_sport_page(sport, name, fixtures):
    sf = [f for f in fixtures if f["sport"] == sport]
    sp = [f for f in sf if f["markets"]]
    sh = sorted([f for f in sp if f["confidence"] == "high"],
                key=lambda f: -f["band_pick"]["probability"])
    harvest = [r for r in D.OLBG_HARVEST if r["sport"] == sport]
    blocked = [b for b in D.BLOCKED_SOURCES if b["sport"] == sport]
    elapsed = [(s, d, k) for s, d, k in D.ELAPSED if s == sport]

    led = table(
        ["Fixture", "Start (UTC)", "Venue", "State", "Selection", "Our price (fair)", "Tier", "Evidence"],
        [[f'<strong>{e(f["event"])}</strong><br><span class="muted">{e(f["competition"])}</span>',
          when(f["start_utc"]),
          e(f["venue"]) if f["venue"] else blank("Not published officially"),
          state_pill(f["status"]),
          (f'<strong>{e(f["band_pick"]["selection"])}</strong><br>'
           f'<span class="muted">{e(f["band_pick"]["market"])}</span>') if f["band_pick"]
          else blank("Not priced"),
          price_cell(f["band_pick"]),
          badge(f["tier"]),
          (src_link(f["sources"][0]["url"], f["sources"][0]["name"]) if f["sources"]
           else '<a class="src warnlink" href="../flagged.html">reason</a>')]
         for f in sorted(sf, key=lambda f: f["start_utc"] or "9")],
        "lined", "Nothing discovered on the OLBG hub for this sport.")

    calls = "".join(f"""<article class="call">
<header><span class="tag">{e(f["competition"])}</span>{badge(f["tier"])}
<h3>{e(f["event"])}</h3><p class="meta">{when(f["start_utc"])}</p></header>
<p class="sel"><span class="sel-label">Selection</span><strong>{e(f["band_pick"]["selection"])}</strong>
<span class="odds">{e(f["band_pick"]["fair_american"])}</span>
<span class="muted">{pct(f["band_pick"]["probability"])} · quoted {e(f["band_pick"]["american"])}</span></p>
<p>{e(f["prediction"]["text"])}</p>
<p class="avail"><strong>Team news:</strong> {e(f["prediction"]["availability"])}</p>
<p class="links">{" ".join(src_link(s["url"], s["name"]) for s in f["sources"])}</p>
</article>""" for f in sh if f.get("prediction"))

    mk = []
    for f in sp:
        rows = []
        for m in f["markets"]:
            for o in m["outcomes"]:
                rows.append([e(m["label"]), e(o["selection"]), pct(o["probability"]),
                             f'{o["fair_odds"]:.2f}', e(o["fair_american"]),
                             f'<span class="odds">{e(o["american"])}</span>',
                             '<span class="pill ok">in band</span>' if o["in_band"]
                             else '<span class="pill warn">out of band</span>'])
        mk.append(f'<h4 class="mk-title">{e(f["event"])}</h4>' + table(
            ["Market", "Outcome", "Chance", "Fair decimal", "Fair American", "Quoted", "Band"],
            rows, "mini"))

    hv = table(["Competition", "Event", "OLBG clock (EDT)", "UTC equivalent", "Tips", "Market",
                "Crowd consensus"],
               [[e(r["comp"]), e(r["event"]), e(r.get("t") or "—"),
                 e(olbg_utc(r.get("t", "")) or "—"), e(str(r.get("tips") or "—")),
                 e(r.get("market") or "—"), e(r.get("consensus") or "—")] for r in harvest],
               "mini", "No cards were listed on this hub at harvest time.")

    bl = ("".join(
        f'<div class="blockcard"><h4>{e(b["name"])}</h4>'
        f'<p><strong>Tried:</strong> <code>{e(b["attempted"])}</code></p>'
        f'<p><strong>Result:</strong> {e(b["failure"])}</p>'
        f'<p>{src_link(b["url"], "Publisher home")}</p></div>' for b in blocked)
        or "<p class='empty'>No blocked source for this sport.</p>")

    el = ("".join(f'<li>{e(d)} <span class="muted">({e(D.SOURCES[k]["url"])})</span></li>'
                  for _, d, k in elapsed) or "<li>None recorded.</li>")

    body = f"""
{panel("Fixture ledger", led,
       f"Every {name.lower()} event discovered, with its official confirmation where one exists.")}
{panel("High-confidence calls", calls or '<p class="empty">No selection in this sport cleared the '
       'price band and the probability floor from the official data available.</p>')}
{panel("Originated markets", "".join(mk) or '<p class="empty">No market could be priced for this '
       'sport, because no official input was obtainable. Nothing has been estimated.</p>')}
{panel("OLBG discovery layer", hv,
       "What OLBG itself published, before any official check. Used to find events, never to "
       "confirm them. OLBG serves this session Eastern Daylight Time, so add four hours for UTC.")}
<div class="grid2">
{panel("Official sources that could not be read", bl)}
{panel("Already started at harvest time", f"<ul class='flags'>{el}</ul>",
       "Events in this list are deliberately not published as picks.")}
</div>
"""
    (SITE / "sports" / f"{sport}.html").write_text(page(
        "sports.html", name, name,
        f"{name} fixtures reverse-engineered from OLBG and checked against official sources.",
        body, depth=1,
        counts={"fixtures": len(sf), "priced": len(sp), "high": len(sh)}), encoding="utf-8")


def build_coverage(fixtures, priced, highs):
    rows = []
    for sport in SPORT_ORDER:
        sf = [f for f in fixtures if f["sport"] == sport]
        sp = [f for f in sf if f["markets"]]
        sh = [f for f in sp if f["confidence"] == "high"]
        blocked = [b for b in D.BLOCKED_SOURCES if b["sport"] == sport]
        if sp:
            reason = "Official source read and used."
        elif blocked:
            reason = blocked[0]["failure"]
        elif not sf:
            reason = "OLBG listed nothing for this sport at harvest time."
        else:
            reason = "No official source could be reached inside this session."
        rows.append([
            f'<a href="sports/{sport}.html"><strong>{e(SPORT_NAME[sport])}</strong></a>',
            str(len(sf)), str(len(sp)), str(len(sh)),
            f'{len(sh)}/5',
            e(reason),
            src_link(blocked[0]["url"], "Publisher") if blocked else
            (src_link(sp[0]["sources"][0]["url"], "Official feed") if sp and sp[0]["sources"]
             else src_link(D.OLBG_HUBS.get(sport, "https://www.olbg.com/betting-tips"), "OLBG hub")),
        ])

    gap_rows = [[e(b["sport"].replace("-", " ").title()), e(b["name"]),
                 f'<code>{e(b["attempted"])}</code>', e(b["failure"]),
                 src_link(b["url"], "Publisher home")] for b in D.BLOCKED_SOURCES]

    body = f"""
<div class="notice">{icon("M12 3v18M3 12h18")}
<p>The brief asks for five high-confidence predictions per sport per day. This page states exactly
where that was achieved and where it was not, and why. No shortfall has been papered over with an
estimated number.</p></div>

{panel("Coverage and the five-a-day target", table(
    ["Sport", "Discovered", "Priced", "High-confidence", "Against target", "Why", "Link"],
    rows, "lined"))}

{panel("Official sources attempted and refused", table(
    ["Sport", "Source", "URL attempted", "Result", "Publisher"], gap_rows, "lined"),
    "Each of these was tried during this session. The failure text is recorded verbatim so the "
    "attempt can be repeated and checked.")}

{panel("What would close the gaps", '''<div class="prose"><ul>
<li><strong>Basketball (NBA).</strong> Three public endpoints returned HTTP 500 or an Akamai
rejection. The untried routes are the static league schedule JSON and the per-team schedule pages.</li>
<li><strong>Darts.</strong> pdc.tv serves a consent document in place of page content; the draw is
likely reachable from a tournament sub-path that skips the consent template.</li>
<li><strong>Rugby union.</strong> The United Rugby Championship fixtures path has moved; the
competition's own navigation points at a different slug.</li>
<li><strong>Handball.</strong> The French league renamed its competition to Daikin StarLigue, so the
old calendar path is dead; the live path is the renamed one.</li>
<li><strong>Golf.</strong> OLBG itself returned "No tips found." on every golf hub, so there was
nothing to reverse-engineer, and the PGA Tour season index path 404s.</li>
<li><strong>Greyhounds.</strong> The GBGB race-card path returns the organisation's 404 template;
the racing section index is the working entry point.</li>
</ul></div>''')}
"""
    (SITE / "coverage.html").write_text(page(
        "coverage.html", "Coverage report", "Coverage report",
        "Exactly how much of the fifteen-sport brief this desk could support with official "
        "evidence, and what blocked the rest.", body,
        counts={"sports in scope": 15, "sports priced": len({f["sport"] for f in priced}),
                "blocked sources": len(D.BLOCKED_SOURCES)}), encoding="utf-8")


def build_sources():
    rows = [[e(s["name"]), f'<code>{e(s["host"])}</code>', src_link(s["url"], s["url"][:68]),
             e(s["read_utc"]),
             e(s.get("note") or "Read successfully and used for the rows that cite it.")]
            for s in D.SOURCES.values()]
    blocked = [[e(b["sport"].replace("-", " ").title()), e(b["name"]),
                f'<code>{e(b["attempted"])}</code>', e(b["failure"]),
                src_link(b["url"], "Publisher")] for b in D.BLOCKED_SOURCES]
    tz = [[e(t["check"]), e(t["detail"]), src_link(t["url"], "Evidence")] for t in D.TZ_EVIDENCE]
    hubs = [[e(SPORT_NAME[k]), src_link(v, v)] for k, v in D.OLBG_HUBS.items()]

    body = f"""
<div class="notice">{icon("M10 13a5 5 0 007 0l3-3a5 5 0 00-7-7l-2 2M14 11a5 5 0 00-7 0l-3 3a5 5 0 007 7l2-2")}
<p>Two layers, kept strictly apart. <strong>Discovery</strong> is OLBG: it tells the desk an event
exists. <strong>Confirmation</strong> is the governing body, league or tour: it is the only thing
allowed to establish a fact. No row on this desk is confirmed by OLBG.</p></div>

{panel("Official sources read", table(
    ["Source", "Host", "URL", "Read (UTC)", "What it established"], rows, "lined"))}

{panel("Timezone evidence", table(["Check", "Reasoning", "Link"], tz, "lined"),
    "OLBG renders event clocks in the viewer's own zone. These three independent cross-checks all "
    "resolve to UTC−4 for this session, which is the conversion applied everywhere on the desk. "
    "World Snooker Tour and Cricket Australia were found to geo-render the same way.")}

{panel("Discovery hubs", table(["Sport", "OLBG hub"], hubs, "lined"),
    "The fifteen entry points harvested. Listed for traceability only — none of them confirms "
    "anything.")}

{panel("Attempted and refused", table(
    ["Sport", "Source", "URL attempted", "Result", "Publisher"], blocked, "lined"),
    "Recorded so a reviewer can repeat the attempt rather than take this desk's word for it.")}
"""
    (SITE / "sources.html").write_text(page(
        "sources.html", "Sources & evidence", "Sources & evidence",
        "Every official feed read, every one refused, and the timezone proof behind the clocks.",
        body, counts={"official sources": len(D.SOURCES),
                      "refused": len(D.BLOCKED_SOURCES), "hubs": len(D.OLBG_HUBS)}),
        encoding="utf-8")


def build_flagged(fixtures, flagged):
    rows = []
    for f in fixtures:
        for fl in f["flags"]:
            rows.append([
                f'<a href="{slug_href(f["sport"],0)}">{e(SPORT_NAME[f["sport"]])}</a>',
                f'<strong>{e(f["event"])}</strong>', e(fl),
                state_pill(f["status"]),
                (src_link(f["sources"][0]["url"], f["sources"][0]["name"]) if f["sources"]
                 else src_link(f["verification"].get("evidence", "https://www.olbg.com/betting-tips"),
                               "Publisher")),
            ])
    blank_rows = []
    for f in fixtures:
        for u in f["unavailable_markets"]:
            blank_rows.append([
                e(SPORT_NAME[f["sport"]]), f'<strong>{e(f["event"])}</strong>',
                e(u["label"]), '<span class="pill warn">blank</span>', e(u["reason"])])
    el_rows = [[e(SPORT_NAME.get(s, s)), e(d), src_link(D.SOURCES[k]["url"], "Official page")]
               for s, d, k in D.ELAPSED]
    blocked = [[e(b["sport"].replace("-", " ").title()), e(b["name"]),
                f'<code>{e(b["attempted"])}</code>', e(b["failure"]),
                src_link(b["url"], "Publisher")] for b in D.BLOCKED_SOURCES]

    body = f"""
<div class="notice warn">{icon("M5 21V4c5-4 9 4 14 0v10c-5 4-9-4-14 0")}
<p><strong>Everything on this page needs a human eye.</strong> None of it stops the desk publishing:
the rule here is that an unconfirmable value stays blank and gets listed, rather than being filled
in from memory or from a secondary report.</p></div>

{panel("Fixture-level flags", table(
    ["Sport", "Fixture", "Flag", "State", "Evidence"], rows, "lined"),
    f"{len(rows)} flags raised across {len({r[1] for r in rows})} fixtures.")}

{panel("Markets left deliberately blank", table(
    ["Sport", "Fixture", "Market", "State", "Why it is blank"], blank_rows, "lined"),
    "A blank market is a decision, not an omission.")}

{panel("Already started or finished at harvest time", table(
    ["Sport", "Observation", "Official page"], el_rows, "lined"),
    "These were live or complete when the hubs were read at 2026-10-23T16:26Z. The desk does not "
    "publish a pick on an event that has started, so they appear here instead of on the picks "
    "pages.")}

{panel("Official sources that could not be read", table(
    ["Sport", "Source", "URL attempted", "Result", "Publisher"], blocked, "lined"),
    "Nine sports are published blank because of these. Each attempt and its exact failure is "
    "recorded so the check can be repeated.")}

{panel("Known structural irregularities on OLBG itself", '''<div class="prose"><ul>
<li><strong>Each-way blank-percentage bug.</strong> The T20 Blast 2027 outright card (event 188350)
renders its consensus column as <code>0/0</code> with an empty percentage while still showing tip
counts. The same pattern appears on other ante-post each-way markets.</li>
<li><strong>Silent empty hubs.</strong> The golf hub answers with "No tips found." rather than an
error or an empty-state code, so an automated harvest that only checks HTTP status will record a
successful read of an empty sport.</li>
<li><strong>Outright-only sports.</strong> Rugby league published three ante-post outrights and no
match cards at all, which is indistinguishable from a coverage failure unless the page body is
parsed.</li>
<li><strong>Viewer-zone clocks.</strong> Every clock is rendered in the reader's own timezone with
no zone label anywhere in the markup, so a harvest without an independent cross-check will silently
shift every start time.</li>
<li><strong>Expired cards stay listed.</strong> Elapsed events remain on the hub marked "Expired",
mixed in with live ones, which is how several of this morning's tennis and snooker cards were still
present at harvest time.</li>
</ul></div>''')}
"""
    (SITE / "flagged.html").write_text(page(
        "flagged.html", "Flagged for Review", "Flagged for Review",
        "Unconfirmed values, blank markets, refused sources and OLBG's own irregularities.",
        body, counts={"fixture flags": len(rows), "blank markets": len(blank_rows),
                      "refused sources": len(blocked)}), encoding="utf-8")


def build_analysis(fixtures, priced, highs):
    # OLBG consensus versus our own line, where both exist
    rows = []
    for f in priced:
        if not f["olbg"] or not f["olbg"].get("consensus"):
            continue
        rows.append([
            e(SPORT_NAME[f["sport"]]), f'<strong>{e(f["event"])}</strong>',
            e(f["olbg"].get("market") or "—"),
            f'{e(f["olbg"]["consensus"])} <span class="muted">({e(str(f["olbg"].get("tips") or "—"))} tips)</span>',
            f'<strong>{e(f["pick"]["selection"])}</strong> {pct(f["pick"]["probability"])}',
            badge(f["tier"]),
        ])

    body = f"""
<div class="notice">{icon("M4 20V10m7 10V4m7 16v-7M2 22h20")}
<p>What the reverse-engineering actually produced, where this desk disagrees with the OLBG crowd,
and what the evidence will not support.</p></div>

{panel("Finding 1 — the crowd and this desk disagree on the United States Grand Prix", f'''
<div class="prose">
<p>OLBG's motor racing hub shows Max Verstappen as the most-tipped driver for Austin, with 13 of 38
tips. Our own line makes <strong>Kimi Antonelli</strong> the narrow favourite at 30.1% against
Verstappen's 26.6%, because Antonelli leads the championship on 340 points to Verstappen's 221 while
Verstappen leads on recent wins, two of the last five against Antonelli's two.</p>
<p>The two inputs pull in opposite directions and the split weighting lands them almost level. That
is a genuine disagreement with the crowd rather than an error on either side, and it is the reason
this desk's published motor racing call is a <em>Verstappen podium</em> at −246 rather than a race
winner: the podium market is where an in-band price exists without having to resolve the
disagreement.</p>
<p>{src_link("https://www.formula1.com/en/results/2026/drivers", "Official 2026 drivers' standings")}
{src_link("https://www.formula1.com/en/results/2026/races", "Official 2026 race results")}</p>
</div>''')}

{panel("Finding 2 — a timezone trap that silently corrupts every scraped start time", f'''
<div class="prose">
<p>OLBG prints event clocks with no timezone marker anywhere in the page. The clock is rendered in
the reader's own zone, which for this session resolved to Eastern Daylight Time. Three independent
cross-checks settled it: a Towcester greyhound race shown as "Today 12:12" and already expired
(17:12 BST = 16:12 UTC), World Series Game 1 shown as "Today 20:00" against the MLB Stats API's
2026-10-24T00:00:00Z, and Fils v Michelsen shown as "Today 12:30" against the ATP's "Not Before
18:30" Brussels time.</p>
<p>All three resolve to UTC−4. Two official sites were then found to geo-render the same way:
<strong>wst.tv</strong> prints the Belfast evening session as "14:00" and
<strong>cricket.com.au</strong> prints Australian fixtures in Eastern time too. That resolved an
apparent conflict between the OLBG snooker clock and the World Snooker Tour draw — both are
Eastern, both mean 18:00 UTC, and the match is in fact the 19:00 BST evening session.</p>
<p>{src_link("https://www.olbg.com/betting-tips/Greyhounds/28", "Greyhound hub")}
{src_link("https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-23&endDate=2026-10-26", "MLB Stats API")}
{src_link("https://www.atptour.com/en/scores/current/brussels/7485/daily-schedule", "ATP Brussels order of play")}</p>
</div>''')}

{panel("Finding 3 — where the edges actually are this week", '''<div class="prose">
<p>Nine of the thirteen high-confidence calls are totals, handicaps or derivative markets rather
than straight winners, and that is not a stylistic choice. In the NHL the records are bunched: only
Boston (8-2-1) and Tampa Bay (7-2-0) separate themselves far enough for a money line to clear the
floor. Everywhere else the separation is in the scoring rates, not the win rates — Philadelphia have
scored 1.67 goals a game, Los Angeles 2.50, and both numbers push their totals below the market's
usual six and a half.</p>
<p>The same thing happens in the World Series. Milwaukee finished 103-59 against Tampa Bay's 98-64,
but the Pythagorean lines (103-59 against 90-72) and the road records (48-33 against 43-38) put the
sides much closer than the raw gap suggests, so the run line pays better than the money line.</p>
</div>''')}

{panel("Finding 4 — the price cap changes which selection gets published", f'''<div class="prose">
<p>Three fixtures produced a straight favourite shorter than −250 and were therefore held at Medium
with the published selection moved to an in-band derivative: New Jersey against Los Angeles,
Valencia at Paris, and Mark Williams against David Gilbert. In each case the desk prices the
favourite as the clear winner, but the brief's band stops at −250, so publishing the money line
would put a selection outside the stated window at the top of the page.</p>
<p>This is worth stating plainly because it changes the shape of the output: a desk that ignored the
band would show more "winner" picks and fewer totals, and would look more confident than the
evidence warrants.</p>
</div>''')}

{panel("OLBG crowd consensus against this desk's line", table(
    ["Sport", "Fixture", "OLBG market", "OLBG consensus", "Our winner-market favourite", "Tier"],
    rows, "lined"),
    "Only fixtures where OLBG published a consensus and this desk was able to originate a price. "
    "OLBG is the discovery layer here, not a source of truth.")}

{panel("What the evidence would not support", '''<div class="prose">
<p>Cricket is the clearest example. Five fixtures were confirmed in full — match id, both teams,
UTC start and venue — from Cricket Australia's own matches index, but that index publishes no
ladder, no squad and no form figures, and no second official source was read inside this session.
Every cricket market is therefore blank. The fixtures are published because they are confirmed; the
prices are not, because they would have had to be invented.</p>
<p>The same logic applies to two tennis matches where the players sit outside the portion of the
official rankings that was read, to Colorado's goals for and against, and to Jak Jones's
second-round frame line. In each case the surrounding row is published and the missing cell is left
empty and listed on the flagged page.</p>
</div>''')}
"""
    (SITE / "analysis.html").write_text(page(
        "analysis.html", "Analysis & findings", "Analysis & findings",
        "Four findings from reverse-engineering OLBG, and an honest account of what the evidence "
        "would not support.", body, counts={"findings": 4}), encoding="utf-8")


def build_reverse():
    hub_rows = [[e(SPORT_NAME[k]), f'<code>/betting-tips/{k.title()}/…</code>', src_link(v, v)]
                for k, v in D.OLBG_HUBS.items()]
    harvest_rows = [[e(SPORT_NAME.get(r["sport"], r["sport"])), e(r["comp"]), e(r["event"]),
                     e(r.get("t") or "—"), e(olbg_utc(r.get("t", "")) or "—"),
                     e(str(r.get("tips") or "—")), e(r.get("market") or "—"),
                     e(r.get("consensus") or "—")] for r in D.OLBG_HARVEST]
    tz_rows = [[e(t["check"]), e(t["detail"]), src_link(t["url"], "Check")] for t in D.TZ_EVIDENCE]

    body = f"""
<div class="notice">{icon("M8 5L2 12l6 7M16 5l6 7-6 7M14 3l-4 18")}
<p>How OLBG's public tip hubs are put together, what they expose, and the four behaviours that will
break a naive harvest. This page is the discovery layer in full; nothing here is treated as a
confirmed sporting fact.</p></div>

{panel("URL architecture", f'''<div class="prose">
<p>Every sport hub follows the same shape: <code>olbg.com/betting-tips/&lt;Sport&gt;/&lt;id&gt;</code>,
where the id is a stable small integer. The sport name in the path is cosmetic — the integer is what
routes. Individual cards hang off <code>/betting-tips/&lt;Sport&gt;/&lt;id&gt;/&lt;event-id&gt;</code>
with a six-digit event id, and the same event id reappears across markets on that event.</p>
<p>Each card exposes four machine-readable quantities: the number of tips, the number of tipsters on
the leading selection, that selection's share as a percentage, and the market the consensus applies
to. There is no odds field and no timezone field.</p>
</div>''' + table(["Sport", "Path shape", "Hub"], hub_rows, "lined"))}

{panel("The four behaviours that break a naive harvest", '''<div class="prose"><ol>
<li><strong>Clocks are rendered in the viewer's zone with no label.</strong> A scraper that records
"Today 20:00" and stamps it UTC will be four hours wrong for every row in this session's region.
The fix is an independent cross-check against an official feed, which is what the timezone table
below does.</li>
<li><strong>Empty hubs return a success page.</strong> Golf answers with the literal string
"No tips found." under a normal 200 response, so status-code-only monitoring records a healthy
scrape of a sport that produced nothing.</li>
<li><strong>Outright-only sports look identical to failures.</strong> Rugby league returned three
ante-post outrights and zero match cards. Without parsing the card type, that is indistinguishable
from a broken selector.</li>
<li><strong>Each-way markets can render a null consensus.</strong> The T20 Blast 2027 outright,
event 188350, shows <code>0/0</code> tipsters and an empty percentage while still reporting a
non-zero tip count — an internal inconsistency that will produce a divide-by-zero in any consensus
calculation.</li>
</ol></div>''')}

{panel("Timezone proof", table(["Check", "Reasoning", "Link"], tz_rows, "lined"),
    "Three independent cross-checks, all landing on UTC−4. The conversion is applied to every OLBG "
    "clock on this desk.")}

{panel("Full harvest", table(
    ["Sport", "Competition", "Event", "OLBG clock (EDT)", "UTC equivalent", "Tips", "Market",
     "Consensus"], harvest_rows, "lined sortable filterable"),
    f"{len(harvest_rows)} cards captured across the fifteen hubs at {NOW}.")}
"""
    (SITE / "reverse-engineering.html").write_text(page(
        "reverse-engineering.html", "OLBG reverse-engineering", "OLBG reverse-engineering",
        "The structure of OLBG's tip hubs, the timezone trap, and the full discovery harvest.",
        body, counts={"hubs": 15, "cards captured": len(D.OLBG_HARVEST)}), encoding="utf-8")


def build_methodology():
    band = [
        ["High-A", "p ≥ 70.0% and fair price inside the band", "−250 to −233", "Published in full"],
        ["High-B", "62.0% ≤ p &lt; 70.0%", "−233 to −163", "Published in full"],
        ["Medium", "50.0% ≤ p &lt; 62.0%", "−163 to +100", "Published, written up, not headlined"],
        ["Medium (price-capped)", "p &gt; 71.43%, i.e. shorter than −250",
         "shorter than −250", "Held back; an in-band derivative is published instead"],
        ["Low", "p &lt; 50.0%", "longer than +100", "Published only as the other side of a market"],
        ["Unrated", "No two officially sourced inputs", "—", "Blank and flagged"],
    ]
    formulas = [
        ["Ice hockey — winner",
         "Shrunk win rate w = (W + 3) / (GP + 6), combined through log5, plus 3.0 points of home ice",
         "Official NHL team summary report"],
        ["Ice hockey — totals, puck line, team totals",
         "Independent Poisson counts, λ_team = (own GF/g + opponent GA/g) / 2; difference via Skellam",
         "Official NHL team summary report"],
        ["Baseball — money line",
         "50/50 blend of actual win percentage and Pythagorean expectation (exponent 1.83), log5, "
         "plus 3.5 points of home advantage", "Official MLB standings"],
        ["Baseball — run line and total",
         "Poisson run counts from season runs scored and allowed per game",
         "Official MLB standings"],
        ["Basketball — winner and handicap",
         "Season point differential per game, plus 2.5 points of home court, normal margin with "
         "σ = 11.0", "Official EuroLeague standings"],
        ["Basketball — total",
         "Symmetric blend of both sides' points for and against, normal with σ = 16.0",
         "Official EuroLeague standings"],
        ["Tennis — winner",
         "p = RP_a^0.70 / (RP_a^0.70 + RP_b^0.70) on PIF ATP ranking points",
         "Official ATP singles rankings"],
        ["Tennis — set betting and totals",
         "Per-set probability inverted from the match price, then the best-of-three tree",
         "Official ATP singles rankings"],
        ["Snooker — winner, frame handicap, frame total",
         "Frame rate shrunk as (frames won + 5) / (frames played + 10), log5 for the single-frame "
         "edge, then a negative binomial race to six", "Official WST tournament draw"],
        ["Motor racing — win, podium, points",
         "p = 0.5 × share of championship points among the top eight + 0.5 × share of the last five "
         "race wins; podium and points by Harville expansion",
         "Official F1 drivers' standings and race results"],
    ]
    body = f"""
<div class="notice">{icon("M12 5v16M3 4c3-1 6-1 9 1 3-2 6-2 9-1v15c-3-1-6-1-9 1-3-2-6-2-9-1z")}
<p>Every number on this desk is reproducible from the official inputs listed beside it. No price is
copied from a bookmaker, from OLBG, or from any aggregator. Where an input is missing, the market is
left blank — there is no default rating anywhere in this pipeline.</p></div>

{panel("The evidence rule", '''<div class="prose">
<p>A fixture is marked <strong>confirmed</strong> only when its start time and both competitors were
read from the governing body, league or tour that owns the competition. OLBG can put a fixture on
the desk; it can never confirm one.</p>
<p>A value that an official source did not publish is rendered as a dash, listed on the flagged
page, and excluded from every calculation that depends on it. Colorado's goals for and against are
the clearest case: the fixture is confirmed and the money line is priced from the points column, but
the total and the puck line are blank because the scoring rates were not in the portion of the
official report that was read.</p>
</div>''')}

{panel("Confidence bands", table(
    ["Tier", "Condition", "Fair price range", "How it is published"], band, "lined"),
    "The brief fixes the eligible window at −250 to +10000, which caps probability at 71.43%. "
    "Anything shorter is a better bet and a worse price, and the desk says so rather than quietly "
    "publishing it as a High.")}

{panel("Pricing formulas", table(
    ["Market", "How it is computed", "Official input"], formulas, "lined"),
    "All ten are implemented in scripts/sefe12010_engine.py and scripts/sefe12010_lines.py and are "
    "re-run from scratch on every build.")}

{panel("Margin", f'''<div class="prose">
<p>Each market shows two prices. The <strong>fair</strong> price is 1 / p with no margin at all, and
it is the one the confidence band is measured against. The <strong>quoted</strong> price adds a flat
loading — 4.5% on two-way markets, 6.0% on three-way, 8.0% on outrights — so a two-way book here
totals 104.5%.</p>
<p>Markets where more than one selection can win at once, such as podium and points finishes, are
marked as non-exclusive and their columns deliberately do not total 100%.</p>
</div>''')}

{panel("Writing rules for published calls", '''<div class="prose">
<p>Every written call is at least thirty words, is written by hand rather than from a template, and
names the selection in plain language so there is no ambiguity about what is being backed. Each one
cites current form, the recent record and at least one fixture-specific statistic taken from the
official source listed beside it.</p>
<p>Injuries are reported only where an official source published them. None of the feeds read for
this desk carries an injury or availability list, and every call says so explicitly rather than
reaching for a secondary report or an untraceable recollection.</p>
<p>Two words are banned from published call text and a test in the repository enforces their
absence on every build.</p>
</div>''')}

{panel("Reproducing this desk", f'''<div class="prose">
<pre><code>python3 scripts/sefe12010_build.py
python3 -m unittest tests.pipeline.test_desk_{DESK} -v
python3 scripts/validate.py</code></pre>
<p>The build is deterministic and dependency-free. The data module holds the harvest and every
official input as literals with their read timestamps, so a reviewer can diff the inputs
independently of the arithmetic.</p>
</div>''')}
"""
    (SITE / "methodology.html").write_text(page(
        "methodology.html", "Methodology", "Methodology",
        "How every price, band and written call on this desk is produced, and the rule that keeps "
        "unconfirmed values blank.", body,
        counts={"priced markets": 10, "bands": 6}), encoding="utf-8")


# ======================================================================= CSS/JS
CSS = """:root{
--bg:#f6f7f9;--panel:#fff;--ink:#14181f;--muted:#5d6672;--line:#e3e7ec;--line2:#eef1f5;
--accent:#1b4ed8;--accent-soft:#eaf0ff;--ok:#0d7a4a;--ok-soft:#e6f5ee;
--warn:#8a5a00;--warn-soft:#fdf2dd;--none:#6b7280;--none-soft:#f0f1f3;
--hi:#0d7a4a;--hi-soft:#e6f5ee;--md:#8a5a00;--md-soft:#fdf2dd;--lo:#6b7280;--lo-soft:#f0f1f3;
--sidebar:#101520;--sidebar-ink:#c9d1dd;--radius:10px;
--mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
--sans:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.6 var(--sans)}
a{color:var(--accent)}
.skip{position:absolute;left:-9999px}
.skip:focus{left:12px;top:12px;background:#fff;padding:8px 12px;border-radius:6px;z-index:99}
.sidebar{position:fixed;inset:0 auto 0 0;width:252px;background:var(--sidebar);color:var(--sidebar-ink);
display:flex;flex-direction:column;padding:18px 14px;overflow-y:auto;z-index:40}
.brand{display:flex;gap:10px;align-items:center;color:#fff;text-decoration:none;padding:4px 6px 16px}
.brand .mark{width:34px;height:34px;border-radius:9px;background:#1f2937;display:grid;place-items:center;color:#8fb4ff;flex:0 0 auto}
.brand strong{display:block;font-size:12.5px;letter-spacing:.09em}
.brand small{display:block;font-size:11px;color:#8b95a5;font-family:var(--mono)}
.nav-label{font-size:10.5px;letter-spacing:.13em;color:#6f7a8a;margin:14px 8px 6px}
.nav-link{display:flex;gap:9px;align-items:center;padding:7px 9px;border-radius:7px;color:var(--sidebar-ink);
text-decoration:none;font-size:13.5px}
.nav-link:hover{background:#1a2130;color:#fff}
.nav-link.active{background:#1f2a3d;color:#fff;font-weight:600}
.side-foot{margin-top:auto;padding:14px 8px 4px;font-size:11.5px;color:#7a8595}
.back{display:block;color:#9fb6e8;text-decoration:none;font-size:12px;padding:3px 0}
.back:hover{color:#fff;text-decoration:underline}
.card-note{background:#171e2b;border:1px solid #232d3e;border-radius:9px;padding:10px 11px;margin-bottom:10px}
.card-note strong{color:#9fe0bb;font-size:12px;display:block;margin-bottom:4px}
.card-note p{margin:0;color:#97a2b2;font-size:11.5px;line-height:1.5}
.layout{margin-left:252px;min-height:100vh;display:flex;flex-direction:column}
.topbar{position:sticky;top:0;z-index:30;background:rgba(255,255,255,.94);border-bottom:1px solid var(--line);
display:flex;align-items:center;gap:12px;padding:10px 24px;backdrop-filter:blur(6px)}
.menu{display:none;background:none;border:1px solid var(--line);border-radius:7px;padding:5px;cursor:pointer;color:var(--ink)}
.crumb{font-size:13px;color:var(--muted);display:flex;gap:6px}
.crumb strong{color:var(--ink)}
.top-right{margin-left:auto;display:flex;gap:14px;align-items:center;font-size:12.5px;color:var(--muted)}
.dot{width:7px;height:7px;border-radius:50%;background:var(--ok);display:inline-block;margin-right:5px}
.main{padding:24px;max-width:1280px;width:100%}
.head{display:flex;gap:18px;flex-wrap:wrap;align-items:flex-end;justify-content:space-between;margin-bottom:20px}
.eyebrow{margin:0;font-size:11px;letter-spacing:.12em;color:var(--accent);font-weight:600}
h1{margin:4px 0 6px;font-size:28px;letter-spacing:-.02em}
.lede{margin:0;color:var(--muted);max-width:66ch}
.chips{display:flex;gap:8px;flex-wrap:wrap}
.chip{background:var(--panel);border:1px solid var(--line);border-radius:999px;padding:5px 12px;font-size:12px;color:var(--muted)}
.chip b{color:var(--ink)}
.notice{display:flex;gap:11px;background:var(--accent-soft);border:1px solid #cfdcff;border-radius:var(--radius);
padding:13px 15px;margin-bottom:20px;color:#1d2b4d}
.notice.warn{background:var(--warn-soft);border-color:#f0ddb4;color:#5d4100}
.notice svg{flex:0 0 auto;margin-top:3px}
.notice p{margin:0;font-size:13.5px;line-height:1.55}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(192px,1fr));gap:12px;margin-bottom:20px}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:14px 15px}
.k-label{margin:0;font-size:11.5px;color:var(--muted);letter-spacing:.03em}
.k-val{margin:5px 0 3px;font-size:30px;font-weight:650;letter-spacing:-.03em;font-variant-numeric:tabular-nums}
.k-sub{margin:0;font-size:11.5px;color:var(--muted);line-height:1.45}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);margin-bottom:20px;overflow:hidden}
.panel-head{display:flex;gap:14px;align-items:flex-start;justify-content:space-between;padding:15px 17px;border-bottom:1px solid var(--line2)}
.panel-head h2{margin:0;font-size:16px;letter-spacing:-.01em}
.panel-head .sub{margin:5px 0 0;font-size:12.5px;color:var(--muted);max-width:80ch}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.grid2>.panel{margin-bottom:0}
.t-wrap{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:13px}
thead th{text-align:left;font-size:11px;letter-spacing:.07em;text-transform:uppercase;color:var(--muted);
padding:10px 14px;border-bottom:1px solid var(--line);white-space:nowrap;background:#fafbfc}
tbody td{padding:11px 14px;border-bottom:1px solid var(--line2);vertical-align:top}
tbody tr:last-child td{border-bottom:0}
tbody tr:hover{background:#fbfcfd}
table.mini{font-size:12.5px}
table.mini thead th,table.mini tbody td{padding:7px 12px}
.sortable thead th{cursor:pointer}
.sortable thead th:hover{color:var(--ink)}
.muted{color:var(--muted);font-size:12px}
.odds{font-family:var(--mono);font-weight:600;font-size:13px}
.odds.big{font-size:15px}
.blank{color:#9aa3af;font-weight:600}
.rank{display:inline-grid;place-items:center;width:22px;height:22px;border-radius:50%;background:var(--accent-soft);
color:var(--accent);font-size:11.5px;font-weight:700}
.badge{display:inline-block;padding:2.5px 8px;border-radius:999px;font-size:11px;font-weight:650;white-space:nowrap}
.badge.hi{background:var(--hi-soft);color:var(--hi)}
.badge.md{background:var(--md-soft);color:var(--md)}
.badge.lo{background:var(--lo-soft);color:var(--lo)}
.badge.un{background:#f3eaff;color:#5b2d91}
.pill{display:inline-block;padding:2px 8px;border-radius:5px;font-size:11px;font-weight:600;white-space:nowrap}
.pill.ok{background:var(--ok-soft);color:var(--ok)}
.pill.warn{background:var(--warn-soft);color:var(--warn)}
.pill.none{background:var(--none-soft);color:var(--none)}
.pill.info{background:var(--accent-soft);color:var(--accent)}
.src{display:inline-flex;gap:4px;align-items:center;font-size:12px;text-decoration:none;color:var(--accent);white-space:nowrap}
.src:hover{text-decoration:underline}
.warnlink{color:var(--warn)}
.btn{display:inline-flex;gap:6px;align-items:center;background:var(--accent);color:#fff;border-radius:7px;
padding:7px 13px;font-size:12.5px;font-weight:600;text-decoration:none;white-space:nowrap}
.btn:hover{background:#1640b5}
.toolbar{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin-bottom:16px}
.field{display:flex;flex-direction:column;gap:3px;font-size:11px;color:var(--muted)}
.field input{border:1px solid var(--line);border-radius:7px;padding:7px 11px;font:14px var(--sans);min-width:260px;background:#fff}
.segmented{display:flex;border:1px solid var(--line);border-radius:7px;overflow:hidden;background:#fff}
.segmented button{border:0;background:none;padding:8px 13px;font:13px var(--sans);cursor:pointer;color:var(--muted);border-right:1px solid var(--line)}
.segmented button:last-child{border-right:0}
.segmented button.on{background:var(--accent);color:#fff;font-weight:600}
.prose{padding:15px 17px;font-size:13.5px;line-height:1.65}
.prose p:first-child{margin-top:0}
.prose p:last-child{margin-bottom:0}
.prose ul,.prose ol{padding-left:19px;margin:0 0 12px}
.prose li{margin-bottom:7px}
.prose code{font-family:var(--mono);font-size:12px;background:#f1f3f6;padding:1px 5px;border-radius:4px}
.prose pre{background:#101520;color:#d7e0ec;padding:13px 15px;border-radius:8px;overflow-x:auto}
.prose pre code{background:none;color:inherit;font-size:12.5px}
.empty{padding:15px 17px;margin:0;color:var(--muted);font-size:13px}
.sport-rule{font-size:13px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);
border-bottom:1px solid var(--line);padding-bottom:7px;margin:26px 0 14px}
.call{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:15px 17px;margin-bottom:12px}
.call header{display:flex;gap:9px;align-items:center;flex-wrap:wrap;margin-bottom:9px}
.call h3{margin:0;font-size:15.5px;flex:1 1 320px}
.call .meta{margin:0;flex:1 1 100%;font-size:12px;color:var(--muted)}
.call p{margin:0 0 9px;font-size:13.5px;line-height:1.62}
.call .avail{font-size:12.5px;color:var(--muted);background:#fafbfc;border-left:2px solid var(--line);padding:7px 11px;border-radius:0 6px 6px 0}
.tag{background:var(--accent-soft);color:var(--accent);font-size:11px;font-weight:650;padding:2.5px 8px;border-radius:5px}
.sel{display:flex;gap:9px;align-items:center;flex-wrap:wrap;background:#fafbfc;border:1px solid var(--line2);border-radius:7px;padding:8px 11px}
.sel-label{font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.links{display:flex;gap:11px;flex-wrap:wrap}
.bigcall{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);margin-bottom:16px;overflow:hidden}
.bc-head{display:flex;gap:16px;justify-content:space-between;flex-wrap:wrap;padding:15px 17px;border-bottom:1px solid var(--line2)}
.bc-head h3{margin:7px 0 3px;font-size:17px}
.bc-head .meta{margin:0;font-size:12px;color:var(--muted)}
.bc-price{text-align:right;min-width:190px}
.bc-sel{display:block;font-weight:650;font-size:14px}
.bc-odds{display:block;font-family:var(--mono);font-size:26px;font-weight:700;color:var(--accent);letter-spacing:-.02em}
.bc-sub{display:block;font-size:11.5px;color:var(--muted)}
.bc-body{display:grid;grid-template-columns:1.25fr 1fr;gap:20px;padding:15px 17px}
.bc-body h4{margin:0 0 6px;font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.bc-body p{margin:0 0 13px;font-size:13.5px;line-height:1.62}
.bc-body .avail{font-size:12.5px;color:var(--muted)}
.inputs,.flags{margin:0 0 13px;padding-left:17px;font-size:12.5px;color:var(--muted)}
.inputs li,.flags li{margin-bottom:5px}
.bigcall details{border-top:1px solid var(--line2);padding:0}
.bigcall summary{padding:11px 17px;cursor:pointer;font-size:12.5px;color:var(--muted);font-weight:600}
.fx{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);margin-bottom:16px;overflow:hidden}
.fx-head{display:flex;gap:14px;justify-content:space-between;flex-wrap:wrap;padding:14px 17px;border-bottom:1px solid var(--line2);background:#fafbfc}
.fx-head h3{margin:0;font-size:15.5px}
.fx-head .meta{margin:3px 0 0;font-size:12px;color:var(--muted)}
.market{border-bottom:1px solid var(--line2);padding:12px 0 4px}
.market:last-child{border-bottom:0}
.m-head{display:flex;gap:10px;align-items:baseline;justify-content:space-between;padding:0 17px}
.m-head h4{margin:0;font-size:13.5px}
.market .note{margin:4px 17px 8px;font-size:12px;color:var(--muted);max-width:92ch}
.blankm{background:#fffdf7}
.bar{display:inline-block;width:54px;height:6px;border-radius:3px;background:var(--line);vertical-align:middle;margin-right:6px;overflow:hidden}
.bar>span{display:block;height:100%;background:var(--accent);border-radius:3px}
.sportgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(228px,1fr));gap:12px}
.sportcard{display:block;background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--ok);
border-radius:var(--radius);padding:14px 15px;text-decoration:none;color:inherit}
.sportcard.warn{border-left-color:var(--warn)}
.sportcard:hover{border-color:var(--accent);box-shadow:0 1px 3px rgba(20,24,31,.07)}
.sportcard h3{margin:0 0 8px;font-size:15px}
.sc-nums{display:flex;gap:12px;margin:0 0 7px;font-size:12px;color:var(--muted)}
.sc-nums b{color:var(--ink);font-size:14px}
.sc-state{margin:0;font-size:11.5px;color:var(--muted)}
.mk-title{margin:18px 17px 7px;font-size:13px;color:var(--muted)}
.blockcard{border-bottom:1px solid var(--line2);padding:12px 17px}
.blockcard:last-child{border-bottom:0}
.blockcard h4{margin:0 0 6px;font-size:13.5px}
.blockcard p{margin:0 0 5px;font-size:12.5px;color:var(--muted)}
.blockcard code{font-family:var(--mono);font-size:11.5px;background:#f1f3f6;padding:1px 5px;border-radius:4px;word-break:break-all}
.footer{margin-top:auto;padding:22px 0 8px;border-top:1px solid var(--line);display:flex;gap:14px;
justify-content:space-between;flex-wrap:wrap;font-size:11.5px;color:var(--muted)}
.shade{position:fixed;inset:0;background:rgba(10,14,20,.45);z-index:35}
@media(max-width:1000px){.grid2{grid-template-columns:1fr}.bc-body{grid-template-columns:1fr}}
@media(max-width:860px){
.sidebar{transform:translateX(-100%);transition:transform .2s ease}
.sidebar.open{transform:none}
.layout{margin-left:0}.menu{display:block}.main{padding:16px}
h1{font-size:23px}.bc-price{text-align:left}}
"""

JS = """(function(){
  var menu=document.getElementById('menu'),side=document.getElementById('sidebar'),
      shade=document.getElementById('shade');
  function toggle(open){
    if(!side)return;
    side.classList.toggle('open',open);
    if(shade)shade.hidden=!open;
    if(menu)menu.setAttribute('aria-expanded',open?'true':'false');
  }
  if(menu)menu.addEventListener('click',function(){toggle(!side.classList.contains('open'));});
  if(shade)shade.addEventListener('click',function(){toggle(false);});
  document.addEventListener('keydown',function(ev){if(ev.key==='Escape')toggle(false);});

  // sortable tables
  Array.prototype.forEach.call(document.querySelectorAll('table.sortable'),function(tbl){
    var ths=tbl.querySelectorAll('thead th');
    Array.prototype.forEach.call(ths,function(th,idx){
      th.setAttribute('role','button');th.setAttribute('tabindex','0');
      function sort(){
        var body=tbl.tBodies[0],rows=Array.prototype.slice.call(body.rows),
            dir=th.getAttribute('data-dir')==='asc'?-1:1;
        Array.prototype.forEach.call(ths,function(o){o.removeAttribute('data-dir');});
        th.setAttribute('data-dir',dir===1?'asc':'desc');
        rows.sort(function(a,b){
          var x=(a.cells[idx]||{}).textContent||'',y=(b.cells[idx]||{}).textContent||'';
          var nx=parseFloat(x.replace(/[^0-9.+-]/g,'')),ny=parseFloat(y.replace(/[^0-9.+-]/g,''));
          if(!isNaN(nx)&&!isNaN(ny)&&x.replace(/[^0-9]/g,'')!==''&&y.replace(/[^0-9]/g,'')!=='')
            return (nx-ny)*dir;
          return x.trim().localeCompare(y.trim())*dir;
        });
        rows.forEach(function(r){body.appendChild(r);});
      }
      th.addEventListener('click',sort);
      th.addEventListener('keydown',function(ev){if(ev.key==='Enter'||ev.key===' '){ev.preventDefault();sort();}});
    });
  });

  // filter box + segmented state filter
  var q=document.getElementById('q'),seg=document.getElementById('seg'),mode='all';
  function apply(){
    var term=(q&&q.value||'').toLowerCase();
    Array.prototype.forEach.call(document.querySelectorAll('table.filterable tbody tr'),function(row){
      var text=row.textContent.toLowerCase(),show=true;
      if(term&&text.indexOf(term)===-1)show=false;
      if(show&&mode==='confirmed'&&text.indexOf('confirmed')===-1)show=false;
      if(show&&mode==='unconfirmed'&&text.indexOf('unconfirmed')===-1)show=false;
      if(show&&mode==='priced'&&row.querySelector('.odds')===null)show=false;
      if(show&&mode==='confirmed'&&text.indexOf('unconfirmed')!==-1)show=false;
      row.hidden=!show;
    });
  }
  if(q)q.addEventListener('input',apply);
  if(seg)seg.addEventListener('click',function(ev){
    var b=ev.target.closest('button');if(!b)return;
    Array.prototype.forEach.call(seg.querySelectorAll('button'),function(o){o.classList.remove('on');});
    b.classList.add('on');mode=b.getAttribute('data-f');apply();
  });
})();
"""


if __name__ == "__main__":
    main()
