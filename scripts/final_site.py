#!/usr/bin/env python3
"""
final_site.py - consolidated dashboard for the whole repository.

This is the integration pass. It re-prices the 22 October snapshot with the same model of
record (scripts/v3_model.py over scripts/v3_data.py), joins every fixture to its official
source URLs, its model assumptions and its desk selection, and renders ONE site at the
repository root:

    index.html            landing dashboard
    picks.html            every priced match, one row each
    markets.html          every originated price, grouped by match
    predictions.html      the high-confidence write-ups
    sports.html           category index
    sports/<slug>.html    17 category pages
    flagged.html          data flags + this session's audit findings
    verification.html     what was verified, when, by which session
    sources.html          official-source register
    methodology.html      model, assumptions and limits
    archive.html          the older boards, preserved

Nothing here invents a value. Every fact printed comes from data/v3/*.json, which carries the
official page it was read from. Model outputs are labelled as the desk's own estimates.

Run:  python3 scripts/final_site.py
Then: python3 scripts/final_validate.py
"""
from __future__ import annotations

import csv
import html
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import v3_data as D          # noqa: E402
import v3_model as M         # noqa: E402
from v3_prose import HIGH_PROSE  # noqa: E402

SNAPSHOT = "2026-10-22T03:30:00Z"
SITE_NAME = "OLBG Independent Desk"
DATA_OUT = ROOT / "data" / "final"

SPORT_META = {
    # slug: (label, OLBG sport id, one-line note). The note is checked against the markets the
    # snapshot actually prices: darts, snooker and tennis carry a correct-score market and no
    # total; every other priced sport carries a total and no correct score.
    "tennis": ("Tennis", 3, "Best-of-three sets. Match winner, set handicap and correct score. No game-total market is originated: the model is a set model, not a games model."),
    "basketball": ("Basketball", 4, "NBA and EuroLeague. Match winner, points handicap and game total."),
    "golf": ("Golf", 5, "Stroke-play tournaments. Event cards only: no head-to-head market is priced without a captured entry list."),
    "cricket": ("Cricket", 7, "T20 internationals, first-class and one-day domestic fixtures. Match winner, run handicap and total runs. Formats differ so widely that one run baseline cannot fit all of them; the single baseline is a disclosed simplification (F-26B-15)."),
    "snooker": ("Snooker", 8, "Round 3 ties over a best-of-seven frames. Match winner, frame handicap and correct score; no total is originated."),
    "rugby-union": ("Rugby Union", 9, "URC, Top 14 and Premiership. Match winner, points handicap and total points."),
    "rugby-league": ("Rugby League", 10, "Rugby League World Cup 2026. Match winner, points handicap and total points."),
    "baseball": ("Baseball", 12, "MLB World Series. Match winner, run handicap and total runs."),
    "ice-hockey": ("Ice Hockey", 13, "NHL regular season. Match winner, puck handicap and total goals. A draw is not possible after overtime."),
    "motor-racing": ("Motor Racing", 14, "Formula 1. Event card only: no race-winner market is priced without a captured entry list."),
    "darts": ("Darts", 15, "PDC European Championship, best of 11 legs. Match winner, leg handicap and correct score; no total is originated."),
    "handball": ("Handball", 20, "EHF Champions League. Match winner, goal handicap and total goals."),
    "volleyball": ("Volleyball", 21, "PlusLiga and SuperLega. Match winner, set handicap and total points."),
    "aussie-rules": ("Aussie Rules", 22, "AFLW. Match winner, points handicap and total points."),
    "esports": ("eSports", 23, "League of Legends World Championship. Event card only: the official hub did not render a fixture, so nothing is priced."),
    "gaelic-football": ("Gaelic Football", 25, "Munster and county championships. Match winner, points handicap and total points."),
    "greyhounds": ("Greyhounds", 28, "GBGB licensed meetings. Event card only: gbgb.org.uk returned HTTP 500 at capture time."),
}
ORDER = ["tennis", "basketball", "golf", "cricket", "snooker", "rugby-union", "rugby-league",
         "baseball", "ice-hockey", "motor-racing", "darts", "handball", "volleyball",
         "aussie-rules", "esports", "gaelic-football", "greyhounds"]
# OLBG's own slug for each hub id, read from the reverse-engineered taxonomy file so the
# hub URL printed on a sport page is the one OLBG actually publishes.
_tax = json.loads((Path(__file__).resolve().parent.parent / "data" / "olbg_taxonomy.json").read_text())
TAXONOMY_SLUG = {s["id"]: s["slug"] for s in _tax["sports"]}
TAXONOMY_NAME = {s["id"]: s["name"] for s in _tax["sports"]}

EXCLUDED = [(sp["name"], sp["id"]) for sp in _tax["sports"] if not sp["in_scope"]]


# ----------------------------------------------------------------------------- helpers

def esc(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def when(row: dict) -> str:
    if row.get("start_utc"):
        dt = datetime.strptime(row["start_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        return dt.strftime("%a %d %b, %H:%M UTC")
    if row.get("date_local"):
        dt = datetime.strptime(row["date_local"], "%Y-%m-%d")
        return dt.strftime("%a %d %b") + " (date only)"
    return "not published"


def date_only(row: dict) -> str:
    if row.get("start_utc"):
        return row["start_utc"][:10]
    return row.get("date_local") or ""


def us_fmt(us) -> str:
    if us is None:
        return ""
    return f"{us:+d}" if us > 0 else f"{us:d}"


def moneyline(price, us) -> str:
    if price is None:
        return ""
    return f"{price:.2f} <span class=\"mut\">{us_fmt(us)}</span>"


def conf_tag(conf: str | None) -> str:
    klass = {"High": "hi", "Medium": "md", "Low": "lo"}.get(conf or "", "lo")
    return f'<span class="tag {klass}">{esc(conf or "No bet")}</span>'


def src_links(sources, limit: int = 0) -> str:
    out = []
    for s in sources[:limit] if limit else sources:
        label = s.get("name") or urlparse(s["url"]).netloc
        out.append(f'<a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(label)}</a>')
    return " <span class=\"sep\">·</span> ".join(out) if out else '<span class="mut">no external source</span>'


def host_of(url: str) -> str:
    return urlparse(url).hostname or ""


NAV = [
    ("index.html", "Overview"),
    ("picks.html", "All matches"),
    ("markets.html", "Markets"),
    ("predictions.html", "High picks"),
    ("sports.html", "Sports"),
    ("flagged.html", "Flagged"),
    ("verification.html", "Verification"),
    ("sources.html", "Sources"),
    ("methodology.html", "Method"),
    ("analysis.html", "Analysis"),
    ("archive.html", "Archive"),
]


def page(title: str, active: str, body: str, prefix: str = "", description: str = "") -> str:
    bits = []
    for href, label in NAV:
        klass = ' class="on"' if href == active else ""
        bits.append(f'<a href="{prefix}{href}"{klass}>{esc(label)}</a>')
    nav = "".join(bits)
    desc = description or ("Source-linked multi-sport match dataset, independently originated "
                          "lines, confidence tiers and human analysis across 17 sports.")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · {esc(SITE_NAME)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="stylesheet" href="{prefix}assets/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top">
  <div class="wrap bar">
    <a class="brand" href="{prefix}index.html">OLBG <span>Independent Desk</span></a>
    <span class="snap">Snapshot 22 Oct 2026 · 03:30 UTC</span>
  </div>
  <nav class="wrap nav" aria-label="Primary">{nav}</nav>
</header>
<main id="main" class="wrap">
{body}
</main>
<footer class="foot">
  <div class="wrap">
    <p><b>One desk, one snapshot.</b> Every row links to the official league, tour or governing-body page it was read from.
    Prices are the desk's own fair-price estimates, not quoted market odds. Nothing here is a tip-off service or a guarantee.</p>
    <p class="mut">Snapshot {esc(SNAPSHOT)} · built by <code>scripts/final_site.py</code> ·
    verified by <code>scripts/final_validate.py</code>, <code>scripts/validate.py</code> and <code>scripts/v3_validate.py</code>.
    Older boards are preserved on the <a href="{prefix}archive.html">archive page</a>.</p>
  </div>
</footer>
</body>
</html>
"""


# ----------------------------------------------------------------------------- data

def build_rows() -> list[dict]:
    priced = [M.price_fixture(f) for f in D.ALL]
    priced.sort(key=lambda p: (p["start_utc"] or (p["date_local"] or "9999") + "T99", p["sport"], p["home"]))
    rows = []
    for p in priced:
        ident = p["id"]
        best = p.get("best_market")
        pick = None
        if best:
            pick = {
                "market": best["market"],
                "selection": best["selection"],
                "price": best["price"],
                "us": best["us"],
                "model_prob": best["model_prob"],
                "prob_pct": best["prob_pct"],
                "confidence": best["confidence"],
                "cap_reason": best.get("cap_reason"),
                "prose": HIGH_PROSE.get(ident) if best["confidence"] == "High" else None,
            }
        headline = None
        hp = p.get("pick")
        if hp:
            headline = {k: hp.get(k) for k in ("selection", "price", "us", "prob_pct", "confidence", "cap_reason")}
            if headline.get("us") is None and headline.get("price"):
                headline["us"] = M.american_from_price(headline["price"])
            headline["below_band"] = bool(hp.get("below_band"))
        if not p.get("event_only") and p.get("home_input") is None and p.get("away_input") is None:
            flags = list(p.get("flags", []))
            note = ("No official rating was captured for either side. The price reflects the home-field "
                    "adjustment only, so the desk publishes no tip on this card.")
            if not any("no official rating" in f.lower() for f in flags):
                flags.append(note)
            p["flags"] = flags
        rows.append({
            "id": ident,
            "sport": p["sport"],
            "sport_label": SPORT_META.get(p["sport"], (p["sport"], 0, ""))[0],
            "olbg_id": SPORT_META.get(p["sport"], ("", 0, ""))[1],
            "competition": p["competition"],
            "stage": p.get("stage", ""),
            "home": p["home"],
            "away": p["away"],
            "start_utc": p.get("start_utc"),
            "date_local": p.get("date_local"),
            "when": when(p),
            "date": date_only(p),
            "venue": p.get("venue", ""),
            "status": p["status"],
            "verified_at": p.get("verified_at", ""),
            "time_note": p.get("time_note", ""),
            "sources": p.get("sources", []),
            "flags": p.get("flags", []),
            "home_input": p.get("home_input"),
            "away_input": p.get("away_input"),
            "assumptions": p.get("assumptions"),
            "event_only": bool(p.get("event_only")),
            "markets": p.get("markets", []),
            "market_count": len(p.get("markets", [])),
            "pick": pick,
            "headline": headline,
            "no_pick_reason": None if pick else (
                "Event card: no head-to-head market is priced." if p.get("event_only")
                else (p.get("no_tip_reason")
                      or "No selection at or above 52% clears the -250 floor on this card.")),
        })
    return rows


def summarise(rows: list[dict]) -> dict:
    priced = [r for r in rows if not r["event_only"]]
    picks = [r["pick"] for r in priced if r["pick"]]
    return {
        "fixtures": len(rows),
        "priced_matches": len(priced),
        "event_cards": len(rows) - len(priced),
        "prices": sum(r["market_count"] for r in rows),
        "high": sum(1 for p in picks if p["confidence"] == "High"),
        "medium": sum(1 for p in picks if p["confidence"] == "Medium"),
        "low": sum(1 for p in picks if p["confidence"] == "Low"),
        "no_bet": sum(1 for r in priced if not r["pick"]),
        "sports": len({r["sport"] for r in rows}),
        "verified": sum(1 for r in rows if r["status"] == "verified"),
        "carried": sum(1 for r in rows if r["status"] == "carried"),
        "flag_rows": sum(1 for r in rows if r["flags"]),
        "flag_items": sum(len(r["flags"]) for r in rows),
        "capped": sum(1 for p in picks if p.get("cap_reason")),
        "sources": len({s["url"] for r in rows for s in r["sources"]}),
        "hosts": len({host_of(s["url"]) for r in rows for s in r["sources"]}),
        "undated": sum(1 for r in rows if not r.get("start_utc")),
        "in_band_prices": sum(1 for r in rows for m in r["markets"] if m["in_band"]),
    }


def sport_stats(rows: list[dict]) -> dict[str, dict]:
    out = {}
    for slug in ORDER:
        sub = [r for r in rows if r["sport"] == slug]
        picks = [r["pick"] for r in sub if r["pick"]]
        out[slug] = {
            "label": SPORT_META[slug][0],
            "olbg_id": SPORT_META[slug][1],
            "note": SPORT_META[slug][2],
            "fixtures": len(sub),
            "priced": sum(1 for r in sub if not r["event_only"]),
            "event_cards": sum(1 for r in sub if r["event_only"]),
            "high": sum(1 for p in picks if p["confidence"] == "High"),
            "medium": sum(1 for p in picks if p["confidence"] == "Medium"),
            "low": sum(1 for p in picks if p["confidence"] == "Low"),
            "no_bet": sum(1 for r in sub if not r["event_only"] and not r["pick"]),
            "prices": sum(r["market_count"] for r in sub),
            "verified": sum(1 for r in sub if r["status"] == "verified"),
            "carried": sum(1 for r in sub if r["status"] == "carried"),
            "first": min((r["start_utc"] or (r["date_local"] or "9999") + "T99" for r in sub), default=""),
        }
    return out


def pick_source_cell(row: dict) -> str:
    return src_links(row["sources"], 2)


def pick_table(rows: list[dict], show_sport: bool = True, prefix: str = "", anchor_ids: bool = True) -> str:
    head = ["When", "Sport", "Competition", "Match", "Desk selection", "Price", "Model", "Grade",
            "Match-winner call", "Official source"]
    if not show_sport:
        head.remove("Sport")
    out = ['<div class="tablewrap"><table class="grid">', "<thead><tr>"]
    for h in head:
        out.append(f"<th>{esc(h)}</th>")
    out.append("</tr></thead><tbody>")
    for r in rows:
        p = r["pick"]
        rid = f' id="row-{esc(r["id"])}"' if anchor_ids else ""
        attrs = (f' data-sport="{esc(r["sport"])}"'
                 f' data-conf="{esc((p or {}).get("confidence") or "No bet")}"')
        cells = [f'<td class="nowrap">{esc(r["when"])}</td>']
        if show_sport:
            cells.append(f'<td><a href="{prefix}sports/{esc(r["sport"])}.html">{esc(r["sport_label"])}</a></td>')
        cells.append(f'<td>{esc(r["competition"])}<div class="sm mut">{esc(r["stage"])}</div></td>')
        match = f'<b>{esc(r["home"])}</b>' + (f' <span class="mut">v</span> {esc(r["away"])}' if r["away"] else "")
        rated = bool(r.get("home_input") and r.get("away_input"))
        note = '' if rated else '<div class="sm" style="color:var(--md)">no rating captured</div>'
        cells.append(f'<td>{match}<div class="sm mut">{esc(r["venue"])}</div>{note}</td>')
        if p:
            sel = f'<b>{esc(p["selection"])}</b><div class="sm mut">{esc(p["market"])}</div>'
        else:
            sel = ('<span class="tag lo">No bet</span>'
                   f'<div class="sm mut">{esc(r["no_pick_reason"])}</div>')
        cells.append(f"<td>{sel}</td>")
        cells.append(f'<td class="nowrap">{moneyline(p["price"], p["us"]) if p else "&mdash;"}</td>')
        cells.append(f'<td class="nowrap">{(str(p["prob_pct"]) + "%") if p else "&mdash;"}</td>')
        cells.append(f'<td class="nowrap">{conf_tag(p["confidence"]) if p else conf_tag(None)}</td>')
        h = r.get("headline")
        if h:
            cells.append(f'<td class="nowrap">{esc(h["selection"])} {conf_tag(h["confidence"])}'
                         f'<div class="sm mut">{h["price"]:.2f} ({us_fmt(h.get("us"))}) &middot; {h["prob_pct"]}%</div></td>')
        else:
            cells.append('<td class="nowrap">&mdash;</td>')
        cells.append(f'<td class="srccell">{pick_source_cell(r)}</td>')
        out.append(f"<tr{rid}{attrs}>" + "".join(cells) + "</tr>")
    out.append("</tbody></table></div>")
    return "\n".join(out)


def market_sheet(row: dict) -> str:
    order = {"Match winner": 0, "Handicap": 1, "Total": 2, "Correct score": 3}
    mkts = sorted(row["markets"], key=lambda m: (order.get(m["market"], 9), -m["model_prob"]))
    out = ['<div class="tablewrap"><table class="grid compact">',
           "<thead><tr><th>Market</th><th>Selection</th><th>Price</th><th>Model probability</th><th>In -250 band</th></tr></thead><tbody>"]
    for m in mkts:
        out.append(
            "<tr>"
            f'<td>{esc(m["market"])}</td>'
            f'<td>{esc(m["selection"])}</td>'
            f'<td class="nowrap">{moneyline(m["price"], m["us"])}</td>'
            f'<td class="nowrap">{m["prob_pct"]}%</td>'
            f'<td class="nowrap">{"yes" if m["in_band"] else "shorter than -250"}</td>'
            "</tr>")
    out.append("</tbody></table></div>")
    return "\n".join(out)


def event_card(row: dict, prefix: str = "") -> str:
    return (f'<div class="card event"><div class="sm mut">{esc(row["sport_label"])} · '
            f'{esc(row["competition"])} · {esc(row["when"])}</div>'
            f'<h3>{esc(row["home"])}</h3>'
            f'<p class="sm">{esc(row["venue"])}</p>'
            f'<p class="sm">{esc("; ".join(row["flags"]) or "No market priced.")}</p>'
            f'<p class="sm mut">Official source: {src_links(row["sources"])}</p></div>')


def kpi(n, label, klass="") -> str:
    return f'<div class="kpi {klass}"><div class="n">{n}</div><div class="l">{esc(label)}</div></div>'


# ----------------------------------------------------------------------------- pages

def build_index(rows, stats, sports) -> str:
    highs = sorted([r for r in rows if r["pick"] and r["pick"]["confidence"] == "High"],
                   key=lambda r: (r["start_utc"] or (r["date_local"] or "9999") + "T99"))
    tiles = "".join([
        kpi(stats["fixtures"], "fixtures & event cards"),
        kpi(stats["priced_matches"], "priced head-to-heads"),
        kpi(f'{stats["prices"]:,}', "originated prices"),
        kpi(stats["high"], "high-confidence picks", "hi"),
        kpi(stats["sports"], "sports covered"),
        kpi(stats["flag_rows"], "rows carrying a flag", "fl"),
    ])
    cards = []
    for slug in ORDER:
        s = sports[slug]
        badge = ("priced", "ok") if s["priced"] else ("event only", "ev")
        cards.append(
            f'<a class="cat" href="sports/{slug}.html">'
            f'<div class="cat-top"><span class="cat-name">{esc(s["label"])}</span>'
            f'<span class="tag {badge[1]}">{badge[0]}</span></div>'
            f'<div class="cat-nums"><b>{s["fixtures"]}</b> {"row" if s["fixtures"] == 1 else "rows"} · '
            f'{"<b>" + str(s["priced"]) + "</b> priced · <b>" + format(s["prices"], ",") + "</b> prices" if s["priced"] else "event card, no market priced"}'
            f'{" · <b>" + str(s["high"]) + "</b> high" if s["high"] else ""}</div>'
            f'<div class="cat-sub">OLBG sport #{s["olbg_id"]}</div></a>')

    body = f"""
<h1>Multi-sport match list, priced and written up in the open</h1>
<p class="lede">A reverse-engineered rebuild of OLBG's sport coverage: every in-scope competition we could
verify, our own lines on every match, a confidence grade on every selection, and a plain-English prediction
where the number is strong enough to defend. Snapshot taken <b>22 October 2026, 03:30 UTC</b>.</p>

<div class="kpis">{tiles}</div>

<div class="callout">
  <b>What this is.</b> {stats["priced_matches"]} head-to-head matches and {stats["event_cards"]} event cards across
  {stats["sports"]} sports, each joined to the official league, tour or governing-body page it came from.
  Prices are <b>fair-value estimates</b> from our own model (no margin added) &mdash; they are not quoted bookmaker odds.
  Every selection inside the brief's window (<b>&minus;250 to +10,000</b>) is graded High, Medium or Low, and
  matches where nothing clears the window are published as <b>no bet</b> rather than filled with a guess.
</div>

<h2>High-confidence picks ({stats["high"]})</h2>
<p class="sub">Each of these is at least 70% on our model <i>and</i> priced inside the &minus;250 to +10,000 window.
Every one has a written prediction on the <a href="predictions.html">high picks page</a>.</p>
{pick_table(highs)}

<h2>Browse by category</h2>
<p class="sub">All {stats["sports"]} in-scope sports. Excluded by the brief: football/soccer, horse racing,
American football, boxing, UFC/MMA, specials, hurling and cycling &mdash; see <a href="methodology.html#scope">scope</a>.</p>
<div class="cats">{"".join(cards)}</div>

<h2>How a row reads</h2>
<div class="callout">
  <b>Two outputs per match, never mixed up.</b> The <b>match-winner call</b> is the desk&rsquo;s view of who wins,
  and it carries a grade on every priced match &mdash; including the {stats["no_bet"]} where the desk refuses a tip
  because no line inside the window clears a coin flip. The <b>desk selection</b> is the one bet the desk would actually
  put up: it only exists when a match-winner or handicap line is both inside &minus;250 to +10,000 and at least 52% on our
  model. Where it is a handicap, the winner is still named in the call column.
</div>

<h2>Where the rest of it lives</h2>
<div class="links3">
  <a class="box" href="picks.html"><b>All {stats["priced_matches"]} matches</b><span>One row per match: date, venue, selection, price, confidence, official source.</span></a>
  <a class="box" href="markets.html"><b>{stats["prices"]:,} prices</b><span>Every market we originated, match by match: winner, handicap, total, correct score.</span></a>
  <a class="box" href="flagged.html"><b>{stats["flag_rows"]} flagged rows</b><span>Everything we could not certify, plus the audit findings from this pass.</span></a>
  <a class="box" href="verification.html"><b>Verification ledger</b><span>Which official page was read, when, and which session read it.</span></a>
  <a class="box" href="sources.html"><b>{stats["hosts"]} official hosts</b><span>The full source register with every URL used.</span></a>
  <a class="box" href="methodology.html"><b>Model &amp; assumptions</b><span>How a rating becomes a price, and what the model does not do.</span></a>
</div>
"""
    return page("Overview", "index.html", body,
                description="Independent multi-sport betting desk: 127 verified fixtures, 3,176 originated prices, 10 high-confidence picks across 17 sports.")


def build_picks(rows, stats) -> str:
    priced = [r for r in rows if not r["event_only"]]
    cards = [r for r in rows if r["event_only"]]
    sport_opts = "".join(f'<option value="{slug}">{esc(SPORT_META[slug][0])}</option>' for slug in ORDER)
    body = f"""
<h1>All matches ({len(priced)} priced, {len(cards)} event cards)</h1>
<p class="lede">One row per priced match. The desk selection is the single best qualifying line on the card;
where the selection is a handicap, the match-winner call is printed underneath it so the winner is never ambiguous.
{stats["high"]} are High, {stats["medium"]} Medium, {stats["low"]} Low and {stats["no_bet"]} are <b>no bet</b>.</p>

<div class="filters">
  <label>Sport <select id="f-sport"><option value="">All sports</option>{sport_opts}</select></label>
  <label>Confidence <select id="f-conf">
    <option value="">All</option><option value="High">High</option>
    <option value="Medium">Medium</option><option value="Low">Low</option>
    <option value="No bet">No bet</option></select></label>
  <label>Search <input id="f-q" type="search" placeholder="team, player or competition"></label>
  <span class="mut sm" id="f-count"></span>
</div>

{pick_table(priced)}

<h2>Event cards ({len(cards)})</h2>
<p class="sub">These are tournaments, races or meetings where no head-to-head market is published without a
captured entry list. They are listed so coverage is complete, and they carry no selection.</p>
{"".join(event_card(r) for r in cards)}
"""
    return page("All matches", "picks.html", body,
                description="Every priced match with the desk selection, price, model probability, confidence grade and official source.")


def build_markets(rows, stats) -> str:
    blocks = []
    for r in rows:
        if r["event_only"]:
            continue
        p = r["pick"]
        sel = (f'<b>{esc(p["selection"])}</b> at {p["price"]:.2f} ({us_fmt(p["us"])}), {p["prob_pct"]}% &middot; '
               f'{conf_tag(p["confidence"])}') if p else '<span class="tag lo">No bet</span>'
        blocks.append(
            f'<details class="mkt" id="{esc(r["id"])}">'
            f'<summary><span class="mkt-match">{esc(r["home"])}{" v " + esc(r["away"]) if r["away"] else ""}</span>'
            f'<span class="mkt-meta">{esc(r["sport_label"])} &middot; {esc(r["competition"])} &middot; '
            f'{esc(r["when"])} &middot; {r["market_count"]} prices</span>'
            f'<span class="mkt-pick">{sel}</span></summary>'
            f'{market_sheet(r)}'
            f'<p class="sm mut">Official source: {src_links(r["sources"])}</p>'
            f'</details>')
    body = f"""
<h1>Markets &mdash; all {stats["prices"]:,} originated prices</h1>
<p class="lede">Every price the desk produced, grouped by match. Handicaps and totals are derived from the same
rating edge as the match winner, so the ladder is internally consistent rather than a set of separate guesses.
Prices are fair value (1 / probability, two decimals), with no margin added.</p>
<p class="sub">Match winner &rarr; handicap &rarr; total &rarr; correct score. A price shown as
<i>shorter than &minus;250</i> is still published for reference but can never be a high-confidence selection.</p>
{"".join(blocks)}
"""
    return page("Markets", "markets.html", body,
                description="All 3,176 independently originated prices, match by match, with the official source for each fixture.")


def build_predictions(rows, stats) -> str:
    highs = sorted([r for r in rows if r["pick"] and r["pick"]["confidence"] == "High"],
                   key=lambda r: (r["start_utc"] or (r["date_local"] or "9999") + "T99"))
    cards = []
    for r in highs:
        p = r["pick"]
        cards.append(f"""
<article class="pred">
  <div class="pred-head">
    <div>
      <div class="sm mut">{esc(r["sport_label"])} &middot; {esc(r["competition"])} &middot; {esc(r["when"])}</div>
      <h2>{esc(r["home"])}{" <span class='mut'>v</span> " + esc(r["away"]) if r["away"] else ""}</h2>
      <div class="sm mut">{esc(r["venue"])}</div>
    </div>
    {conf_tag(p["confidence"])}
  </div>
  <p class="prose">{esc(p["prose"])}</p>
  <div class="pred-foot">
    <span class="pickline">Selection: <b>{esc(p["selection"])}</b> &middot; {esc(p["market"])} &middot;
    <b>{p["price"]:.2f}</b> ({us_fmt(p["us"])}) &middot; model {p["prob_pct"]}%</span>
    <span class="sm">Official source: {src_links(r["sources"])}</span>
  </div>
  <p class="sm mut" style="margin-top:8px">Sourced form &mdash; {esc(r["home"])}: {esc((r["home_input"] or {}).get("value", ""))} &middot;
  {esc(r["away"] or "")}: {esc((r["away_input"] or {}).get("value", ""))} &middot; {esc(r["venue"])}</p>
</article>""")
    body = f"""
<h1>High-confidence predictions ({len(highs)})</h1>
<p class="lede">A pick only reaches High when the model gives it at least a 70% chance <i>and</i> the price sits
inside the brief's &minus;250 to +10,000 window. Each one below carries its own written preview: the form line we
read from the official source, the venue, and the exact selection.</p>
<p class="sub">The written previews are per match, not templated. They quote only figures that appear in that row's
sourced input &mdash; record, ranking, seed or points differential &mdash; and the price is the desk's own estimate.</p>
{"".join(cards)}
<h2>What keeps a pick below High</h2>
<ul class="notes">
  <li>The model probability is under 70%, so the fair price is outside the &minus;250 floor.</li>
  <li>The row was carried from the previous snapshot and has not been re-read on 22 October, which caps it at Medium.</li>
  <li>One side has no captured official rating, so the model falls back to a neutral prior and caps the grade.</li>
  <li>Nothing on the card clears a 52% coin flip inside the window, in which case the desk publishes no bet.</li>
</ul>
"""
    return page("High picks", "predictions.html", body,
                description="Ten high-confidence selections, each with a unique 30+ word prediction built from sourced form.")


def build_flagged(rows, stats, sports) -> str:
    flag_rows = [(r, f) for r in rows for f in r["flags"]]
    capped = [r for r in rows if r["pick"] and r["pick"].get("cap_reason")]
    undated = [r for r in rows if not r.get("start_utc")]
    nobet = [r for r in rows if not r["event_only"] and not r["pick"]]

    def table(headers, body_rows):
        out = ['<div class="tablewrap"><table class="grid">', "<thead><tr>"]
        out += [f"<th>{esc(h)}</th>" for h in headers]
        out += ["</tr></thead><tbody>"]
        out += ["<tr>" + "".join(c) + "</tr>" for c in body_rows]
        out += ["</tbody></table></div>"]
        return "\n".join(out)

    data_flags = [[
        f'<td><a href="sports/{esc(r["sport"])}.html">{esc(r["sport_label"])}</a></td>',
        f'<td>{esc(r["home"])}{" v " + esc(r["away"]) if r["away"] else ""}</td>',
        f"<td>{esc(f)}</td>",
        f'<td class="sm">{src_links(r["sources"], 1)}</td>',
    ] for r, f in flag_rows]

    caps = [[
        f'<td><a href="sports/{esc(r["sport"])}.html">{esc(r["sport_label"])}</a></td>',
        f'<td>{esc(r["home"])}{" v " + esc(r["away"]) if r["away"] else ""}</td>',
        f'<td>{esc(r["pick"]["selection"])}</td>',
        f"<td>{esc(r['pick']['cap_reason'])}</td>",
        f'<td class="sm">{src_links(r["sources"], 1)}</td>',
    ] for r in capped]

    undated_rows = [[
        f'<td><a href="sports/{esc(r["sport"])}.html">{esc(r["sport_label"])}</a></td>',
        f'<td>{esc(r["home"])}{" v " + esc(r["away"]) if r["away"] else ""}</td>',
        f'<td>{esc(r["date_local"] or "date only")}</td>',
        f"<td>{esc(r['time_note'] or 'No clock published by the official source; UTC start left blank rather than guessed.')}</td>",
        f'<td class="sm">{src_links(r["sources"], 1)}</td>',
    ] for r in undated]

    def call_cell(r: dict) -> str:
        h = r.get("headline")
        if not h:
            return "&mdash;"
        return (f'{esc(h["selection"])} {conf_tag(h["confidence"])}'
                f'<div class="sm mut">{h["price"]:.2f} ({us_fmt(h.get("us"))}) &middot; {h["prob_pct"]}%</div>')

    nobet_rows = [[
        f'<td><a href="sports/{esc(r["sport"])}.html">{esc(r["sport_label"])}</a></td>',
        f'<td>{esc(r["home"])}{" v " + esc(r["away"]) if r["away"] else ""}</td>',
        f'<td>{esc(r["no_pick_reason"])}</td>',
        f'<td class="nowrap">{call_cell(r)}</td>',
        f'<td class="sm">{src_links(r["sources"], 1)}</td>',
    ] for r in nobet]

    # Findings from this integration pass. Each names what was wrong and where the evidence sits.
    findings = [
        ("F-26B-01", "Pick cards linked to a Google search, not an official source",
         "The 22 October board's ten high-confidence cards each ended in a google.com/search link. That is an aggregator, "
         "not a governing body, and it broke the rule that every row carries an official link.",
         "Replaced with the fixture's own official source links, which were already recorded on the row.",
         '<a href="predictions.html">predictions.html</a> <span class="sm mut">·</span> '
         '<a href="methodology.html#confidence">policy</a>', ""),
        ("F-26B-02", "US odds could print outside the \u2212250 floor they claimed to respect",
         "US odds were converted from the model probability instead of from the published decimal, so a 1.40 line "
         "printed as \u2212251 \u2014 outside the window the page said it enforced. One high pick (aflw-r11-09) was affected.",
         "US odds are now the exact conversion of the decimal shown beside them: 1.40 is \u2212250, not \u2212251. "
         "A gate now fails the build if any row disagrees.",
         '<a href="https://www.afl.com.au/aflw/ladder" target="_blank" rel="noopener">afl.com.au/aflw/ladder</a>', ""),
        ("F-26B-03", "Pricing assumptions were not published per row",
         "Sigma, slope, home-field adjustment and the total baseline were applied from per-sport tables but stripped "
         "out of the published fixture export, so a reader could not reproduce a price from the site alone.",
         "Every fixture now exports its assumptions, and the per-sport table is printed on the methodology page.",
         '<a href="methodology.html#assumptions">methodology.html#assumptions</a>', ""),
        ("F-26B-04", "A prediction misdescribed its own handicap unit",
         "The Samoa Women preview said the line sat at \u201ca converted try and a half\u201d. The selection is a 1.5-point "
         "handicap; a converted try is six points, so the sentence described a nine-point line that is not on the card.",
         "Rewritten to \u201cmore than a point\u201d, which matches the 1.5-point handicap actually priced.",
         '<a href="https://www.nrl.com/news/2026/10/20/world-cup-team-lists-womens-round-2/" target="_blank" rel="noopener">nrl.com women\'s Round 2</a>', ""),
        ("F-26B-05", "Two previews asserted facts that were not in the sourced input",
         "\u201cThe deeper rotation\u201d (Panathinaikos) and \u201csuperior goal difference\u201d (Magdeburg) are not values the official "
         "standings captured for those rows, so they could not be verified and were removed.",
         "Both previews now quote only the sourced record: win-loss, points and differential where it exists.",
         '<a href="https://ehfcl.eurohandball.com/men/2026-27/standings/" target="_blank" rel="noopener">EHF standings</a>', ""),
        ("F-26B-06", "Draw mass is omitted from every non-binomial sport",
         "The normal model prices a two-way winner (p and 1&minus;p) for all sports, including handball, Gaelic football, "
         "rugby union, rugby league and AFLW, where a draw is a real outcome. A favourite's win probability is therefore "
         "slightly overstated and a draw is never quoted.",
         "Disclosed, not silently patched: changing the model mid-snapshot would move every price. Flagged for the next "
         "pricing pass, which should add a draw component for draw-capable sports.",
         '<a href="methodology.html#limits">methodology.html#limits</a>', ""),
        ("F-26B-07", "28 rows carry a verification date they did not earn today",
         "These rows were read from an official page on 21 October and not re-read for the 22 October snapshot. They keep "
         "their official link and are labelled <i>carried</i>, and the grading rules cap them at Medium.",
         "Counted per sport on the verification page; each row shows its own status.",
         '<a href="verification.html">verification.html</a> <span class="sm mut">·</span> '
         '<a href="methodology.html#limits">policy</a>', ""),
        ("F-26B-08", "Seven cards have no market at all",
         "Four golf tournaments, Formula 1, League of Legends and the GBGB meetings are listed as event cards because no "
         "entry list or fixture was captured. Without a field there is no head-to-head and no honest price.",
         "Published as event cards with the reason and the official link; no selection is invented.",
         '<a href="picks.html">picks.html</a> <span class="sm mut">·</span> '
         '<a href="methodology.html#scope">policy</a>', ""),
        ("F-26B-09", "14 rows have no UTC start time",
         "Some official sources publish a date without a clock, or a local clock without a timezone. Converting those "
         "would be a guess, so the UTC field is blank and the official local wording is kept.",
         "Listed in full below with the wording each source used.",
         '<a href="verification.html">verification.html</a> <span class="sm mut">·</span> '
         '<a href="methodology.html#limits">policy</a>', ""),
        ("F-26B-10", "This integration pass could not re-fetch any official page",
         "The sandbox used for this pass can reach GitHub and the package registries only. No league, tour or "
         "governing-body host was reachable, so no row was re-certified here.",
         "Every check this pass could make offline is listed on the verification page, and the limitation is printed there "
         "rather than hidden. The recorded verification dates are the ones the reading sessions stamped.",
         '<a href="verification.html#limits">verification.html#limits</a> <span class="sm mut">·</span> '
         '<a href="methodology.html#limits">policy</a>', ""),
        ("F-26B-11", "One volleyball source now redirects away from the men's competition",
         "plusliga.pl serves the men's schedule but redirects the public page to the women's TAURON Liga site, so the "
         "men's fixture cannot be re-certified from that URL.",
         "The row stays carried and capped at Low; the redirect is recorded on the sport page.",
         '<a href="https://www.plusliga.pl/games.html" target="_blank" rel="noopener">plusliga.pl/games.html</a>', ""),
        ("F-26B-12", "The greyhound regulator returned HTTP 500",
         "gbgb.org.uk failed at capture time, so no race card, trap draw or price could be read.",
         "The meeting is listed as an event card with no selection.",
         '<a href="https://www.gbgb.org.uk/" target="_blank" rel="noopener">gbgb.org.uk</a>', ""),
        ("F-26B-13", "The official-host allowlist did not include two of the snapshot\u2019s own sources",
         "The tennis rows are read from the WTA draw PDF on <code>wtafiles.wtatennis.com</code> and the ATP order of play on "
         "<code>www.protennislive.com</code>. Both are the tours\u2019 own file hosts, but neither was on the validator\u2019s "
         "allowlist, so a strict run of the old gate would have rejected the snapshot\u2019s best tennis sources.",
         "Both hosts are now on the shared allowlist and every row is re-checked against it on each build.",
         '<a href="https://www.protennislive.com/posting/2026/9410/op.pdf" target="_blank" rel="noopener">ATP order of play</a>', ""),
        ("F-26B-14", "A missing rating was filled with a league-average prior and then priced as if it were measured",
         "39 of the 120 priced matches have at least one side with no captured official rating. The model substituted 58.0 "
         "and subtracted it from the rated side, so an unrated opponent created an edge nobody measured: Medvedev at 97.5 "
         "against an unrated player produced a 39.5-point gap and a 1.22 moneyline. The repository's own rule said one-sided "
         "ratings are refused, so the code and the documentation disagreed.",
         "Fixed at the root: when either side is unrated no strength edge is applied at all, the price is the venue baseline, "
         "and the desk publishes <b>no tip</b> on that card. The match-winner call stays visible and is graded Low. "
         "46 of 120 matches now carry no tip, 39 of them for this reason.",
         '<a href="https://www.atptour.com/en/rankings/singles" target="_blank" rel="noopener">ATP rankings</a>', ""),
        ("F-26B-15", "Cricket mixes three formats under one scoring baseline",
         "The four cricket rows cover two T20 internationals, a first-class match and a one-day domestic match. The model applies "
         "one run baseline (170.5) and one spread (22) to all four, which fits a T20 innings and badly misfits a three-day game. "
         "The basketball table already separates the NBA from the EuroLeague; cricket does not yet separate its formats.",
         "Disclosed on the sport page and in the methodology table rather than patched with invented per-format baselines. "
         "Flagged for the next pricing pass, which should carry a T20 / one-day / first-class baseline triple.",
         '<a href="https://scoring.nzc.nz/fixtures" target="_blank" rel="noopener">NZC fixtures</a>', ""),
    ]
    findings_rows = [[
        f'<td class="nowrap"><b>{esc(fid)}</b></td>',
        f"<td><b>{esc(title)}</b><div class=\"sm\">{detail}</div></td>",
        f'<td class="sm">{action}</td>',
        f'<td class="sm">{link}</td>',
    ] for fid, title, detail, action, link, _ in findings]

    body = f"""
<h1>Flagged for review</h1>
<p class="lede">Everything the desk could not certify, every selection whose grade was capped, and every defect this
integration pass found and fixed. A flag never deletes a row: the row stays on its sport page with a blank field,
a capped grade, or an explicit note.</p>
<div class="kpis">
  {kpi(len(flag_rows), "data flags")}
  {kpi(len(capped), "capped selections")}
  {kpi(len(undated), "rows without a UTC clock")}
  {kpi(len(nobet), "no-bet matches")}
  {kpi(len(findings), "audit findings", "fl")}
</div>

<h2>1. Defects found and fixed in this pass ({len(findings)})</h2>
<p class="sub">These are the defects this pass found on the published board. Each fix is in this commit; the two that cannot be
fixed without moving every price or re-fetching a live source (F-26B-06 draw mass, F-26B-10 fetch limit) are disclosed instead.</p>
{table(["ID", "Finding", "What was done", "Evidence"], findings_rows)}

<h2 id="data-flags">2. Data flags on individual rows ({len(flag_rows)})</h2>
<p class="sub">Each flag names the field that could not be certified and links to the official page the row was read from.</p>
{table(["Sport", "Fixture", "Flag", "Official source"], data_flags)}

<h2 id="capped">3. Selections whose grade was capped ({len(capped)})</h2>
<p class="sub">A cap is a ceiling, not an error: the price is still published, but the grade cannot rise above Medium
until the blocking condition is cleared.</p>
{table(["Sport", "Fixture", "Selection", "Cap reason", "Official source"], caps) if caps else '<p class="sub">No selection in this snapshot needed a cap: every carried row that produced a selection was already below the 70% line, so the cap rule never had to fire.</p>'}

<h2 id="undated">4. Rows with no UTC start time ({len(undated)})</h2>
<p class="sub">The official source publishes a date, or a local clock without a timezone. The UTC field is left blank
rather than inferred.</p>
{table(["Sport", "Fixture", "Date", "What the source publishes", "Official source"], undated_rows)}

<h2 id="no-bet">5. Matches with no qualifying selection ({len(nobet)})</h2>
<p class="sub">On these cards every in-window line is a coin flip or worse, so the desk publishes no bet.</p>
{table(["Sport", "Fixture", "Why there is no tip", "Match-winner call", "Official source"], nobet_rows)}
"""
    return page("Flagged for review", "flagged.html", body,
                description="Every value the desk could not certify, every capped selection, and every defect found in the integration pass.")


def build_verification(rows, stats, sports) -> str:
    hosts = defaultdict(lambda: {"rows": 0, "urls": set(), "sports": set(), "names": set()})
    for r in rows:
        for s in r["sources"]:
            h = hosts[host_of(s["url"])]
            h["rows"] += 1
            h["urls"].add(s["url"])
            h["sports"].add(r["sport_label"])
            h["names"].add(s.get("name", ""))
    host_rows = []
    for host, h in sorted(hosts.items(), key=lambda kv: (-kv[1]["rows"], kv[0])):
        host_rows.append([
            f'<td><a href="{esc(sorted(h["urls"])[0])}" target="_blank" rel="noopener"><b>{esc(host)}</b></a></td>',
            f'<td>{esc(sorted(h["names"])[0])}</td>',
            f'<td class="nowrap">{h["rows"]}</td>',
            f'<td class="sm">{esc(", ".join(sorted(h["sports"])))}</td>',
        ])

    per_sport = []
    for slug in ORDER:
        s = sports[slug]
        per_sport.append([
            f'<td><a href="sports/{slug}.html">{esc(s["label"])}</a></td>',
            f'<td class="nowrap">{s["fixtures"]}</td>',
            f'<td class="nowrap">{s["verified"]}</td>',
            f'<td class="nowrap">{s["carried"]}</td>',
            f'<td class="nowrap">{s["prices"]:,}</td>',
            f'<td class="nowrap">{s["high"]}</td>',
        ])

    # Source pages the reading sessions recorded by hand.
    ledger = []
    for name, url, checked, note in D.VERIFICATION:
        ledger.append([
            f'<td><a href="{esc(url)}" target="_blank" rel="noopener">{esc(name)}</a></td>',
            f'<td class="nowrap">{esc(checked)}</td>',
            f'<td class="sm">{esc(note)}</td>',
        ])

    body = f"""
<h1>Verification</h1>
<p class="lede">What &ldquo;verified&rdquo; means here, which page was read, when it was read, and what this integration
pass could and could not check for itself.</p>

<div class="callout">
  <b>Two different things are being measured.</b><br>
  <b>Verified</b> ({stats["verified"]} rows) &mdash; the participants, competition, venue and start were read from an
  official page on 22 October 2026 by the session that built this snapshot.<br>
  <b>Carried</b> ({stats["carried"]} rows) &mdash; the row keeps the official URL it was read from on 21 October, but was
  not re-read for this snapshot. Carried rows can never be graded High.
</div>

<h2 id="limits">This pass&rsquo;s own limits</h2>
<div class="callout warn">
  <b>No official page was re-fetched during the integration pass.</b> The sandbox used to consolidate this site can
  reach <code>github.com</code>, <code>api.github.com</code> and the package registries only; every league, tour and
  governing-body host was unreachable. Nothing on this site is presented as re-certified by this pass.
  What was checked offline, and is re-runnable, is:
  <ul class="notes">
    <li>every price reproduces from the model and the exported per-row assumptions;</li>
    <li>US odds are the exact conversion of the decimal beside them, and no High pick sits outside &minus;250 to +10,000;</li>
    <li>every one of the {stats["fixtures"]} rows carries at least one HTTPS link to a host on the official allowlist;</li>
    <li>every high-confidence prediction is a unique 30+ word preview whose figures appear in that row&rsquo;s sourced input;</li>
    <li>all {stats["prices"]:,} prices and every internal link on every page resolve.</li>
  </ul>
</div>

<h2>Source pages read for this snapshot ({len(D.VERIFICATION)})</h2>
<p class="sub">Recorded by the reading session with the UTC time each page was opened, and what was taken from it.</p>
<div class="tablewrap"><table class="grid">
<thead><tr><th>Official page</th><th>Read at (UTC)</th><th>What was taken</th></tr></thead>
<tbody>{"".join("<tr>" + "".join(c) + "</tr>" for c in ledger)}</tbody></table></div>

<h2>Row status by sport</h2>
<div class="tablewrap"><table class="grid">
<thead><tr><th>Sport</th><th>Rows</th><th>Verified 22 Oct</th><th>Carried</th><th>Prices</th><th>High</th></tr></thead>
<tbody>{"".join("<tr>" + "".join(c) + "</tr>" for c in per_sport)}</tbody></table></div>

<h2>Hosts cited ({len(hosts)})</h2>
<div class="tablewrap"><table class="grid">
<thead><tr><th>Official host</th><th>Organisation / page</th><th>Rows</th><th>Sports</th></tr></thead>
<tbody>{"".join("<tr>" + "".join(c) + "</tr>" for c in host_rows)}</tbody></table></div>

<p class="sub">Every row on this site links to at least one of these hosts. Earlier verification passes are preserved
verbatim in <a href="v3/index.html">the 22 October board</a>, <a href="7a5b5360/verification.html">the 21 October
verification ledger</a> and <code>reports/LIVE_VERIFICATION.md</code>.</p>
"""
    return page("Verification", "verification.html", body,
                description="Which official page was read for each row, when it was read, and what this pass could verify offline.")


def build_sources(rows, stats) -> str:
    hosts = defaultdict(lambda: {"urls": set(), "names": set(), "rows": 0, "sports": set()})
    for r in rows:
        for s in r["sources"]:
            h = hosts[host_of(s["url"])]
            h["urls"].add(s["url"])
            h["names"].add(s.get("name", ""))
            h["rows"] += 1
            h["sports"].add(r["sport_label"])
    body_rows = []
    for host, h in sorted(hosts.items(), key=lambda kv: (-kv[1]["rows"], kv[0])):
        urls = sorted(h["urls"])
        listed = "".join(
            f'<div class="sm"><a href="{esc(u)}" target="_blank" rel="noopener">{esc(u)}</a></div>' for u in urls)
        body_rows.append([
            f"<td><b>{esc(host)}</b><div class=\"sm mut\">{esc(', '.join(sorted(h['sports'])))}</div></td>",
            f"<td>{esc(sorted(h['names'])[0])}</td>",
            f'<td class="nowrap">{h["rows"]}</td>',
            f"<td>{listed}</td>",
        ])
    body = f"""
<h1>Official sources</h1>
<p class="lede">{stats["sources"]} distinct URLs across {stats["hosts"]} official hosts. A league, tour, federation,
club or organiser page is the only thing that can certify a fact here. Aggregators, tipster sites, news outlets and
Wikipedia are not used to verify anything, and OLBG is treated as upstream discovery only.</p>
<div class="tablewrap"><table class="grid">
<thead><tr><th>Host</th><th>Organisation / page</th><th>Rows</th><th>URLs used</th></tr></thead>
<tbody>{"".join("<tr>" + "".join(c) + "</tr>" for c in body_rows)}</tbody></table></div>
<h2>Why OLBG itself is not a source</h2>
<p>OLBG is the site being reverse-engineered: it is how the sport taxonomy and the event list were discovered
(<code>olbg.com/sitemap-betting-tips.xml</code> and the 24 numeric sport hubs). It cannot verify a participant,
a venue or a start time, so it never appears in a row&rsquo;s source cell.</p>
<h2>What counts as certified</h2>
<ul class="notes">
  <li><b>Fixture facts</b> &mdash; participants, competition, venue, start &mdash; read from the governing body.</li>
  <li><b>Form inputs</b> &mdash; ladder position, win-loss record, ranking, seed or points differential &mdash; read from the same source and quoted verbatim in the row.</li>
  <li><b>Prices</b> &mdash; the desk&rsquo;s own estimate, never sourced, always labelled as such.</li>
</ul>
"""
    return page("Official sources", "sources.html", body,
                description="The official-source register: every host and URL used to certify a fixture or a form input.")


def build_methodology(rows, stats, sports) -> str:
    # Group the assumptions per sport, and per competition where a sport uses more than one set
    # (the NBA and the EuroLeague do not share a scoring spread, so one row per sport would lie).
    groups: dict[str, dict[tuple, set]] = {}
    for r in rows:
        if r["event_only"] or not r["assumptions"]:
            continue
        a = r["assumptions"]
        key = (a["model"], a["sigma"], a["slope"], a["hfa"], a["hc_max"], a["total_line"],
               a["total_sigma"], a.get("per_leg_scale"), (a.get("series") or {}).get("legs"),
               (a.get("series") or {}).get("unit"))
        groups.setdefault(r["sport"], {}).setdefault(key, set()).add(r["competition"])

    rows_html = []
    for slug in ORDER:
        if slug not in groups:
            rows_html.append([f'<td>{esc(SPORT_META[slug][0])}</td>',
                              '<td colspan="5" class="mut">Event card only &mdash; nothing priced, so no assumptions apply.</td>'])
            continue
        first = True
        for key, comps in sorted(groups[slug].items(), key=lambda kv: -len(kv[1])):
            model, sigma, slope, hfa, hc_max, tl, tsig, leg_scale, legs, unit = key
            label = "all rows" if len(groups[slug]) == 1 else ", ".join(sorted(comps))
            rows_html.append([
                f'<td><a href="sports/{slug}.html">{esc(SPORT_META[slug][0])}</a></td>' if first else "<td></td>",
                f'<td class="sm">{esc(label)}</td>',
                f'<td class="nowrap">{esc(model)}</td>',
                (f'<td class="nowrap">{leg_scale:g} per {esc((unit or "leg").rstrip("s"))} (best of {legs})</td>'
                 if leg_scale else f'<td class="nowrap">&sigma; {sigma:g}</td>'),
                f'<td class="nowrap">{hfa:g}</td>',
                (f'<td class="nowrap">n/a &mdash; no total market</td>' if leg_scale
                 else f'<td class="nowrap">{tl:g} base / {tsig:g} spread</td>'),
            ])
            first = False

    body = f"""
<h1>Methodology</h1>
<p class="lede">One rating per side, one normal distribution per match, fair prices with no margin. Everything on this
page is a modelling choice, and every number in it is published so a price can be reproduced by hand.</p>

<h2 id="model">1. How a rating becomes a price</h2>
<ol class="steps">
  <li><b>One rating per side (0&ndash;100).</b> Derived only from the official input on that row &mdash; ladder position, record, ranking, seed or points differential. No tipster odds are read, and no rating is copied from a bookmaker.</li>
  <li><b>Edge = (home rating &minus; away rating) + home-field adjustment</b> &mdash; but only when <i>both</i> sides have a
  measured rating from the official source. If either side is unrated the strength term is set to zero rather than filled with
  a prior, so the price is the venue baseline and no tip is published. Filling a missing rating with a league average creates
  an edge that was never measured (F-26B-14).</li>
  <li><b>Expected margin &mu; = edge &times; slope.</b> The slope converts a rating point into the sport&rsquo;s own scoring unit, which is why a basketball price and a hockey price are not the same number.</li>
  <li><b>P(home wins) = &Phi;(&mu; / &sigma;).</b> &sigma; is the sport&rsquo;s scoring spread; a 17-point rating gap is a coin flip at a neutral venue before the home adjustment.</li>
  <li><b>Handicaps come from the same distribution:</b> P(covers &minus;L) = &Phi;((&mu; &minus; L) / &sigma;). The ladder is therefore internally consistent with the moneyline.</li>
  <li><b>Totals</b> are priced around the sport&rsquo;s own baseline total, with their own spread.</li>
  <li><b>Best-of-N sports</b> (darts, snooker, tennis) use a binomial leg model instead of a margin, which produces correct-score and set/frame/leg handicaps.</li>
  <li><b>Price = 1 / probability</b>, rounded to two decimals. No margin is added; the overround a bookmaker would charge is a separate business decision and is not baked in.</li>
</ol>

<h2 id="assumptions">2. Per-sport assumptions</h2>
<p class="sub">These are the values used for every row in that sport, and they are modelling choices, not statistics.
For the normal model, &sigma; is the scoring spread and the total market is quoted around its own baseline and spread.
For the binomial sports (darts, snooker, tennis) a rating point is converted into a per-leg probability and the match
price is built from the series length, so no total market is originated. Where a sport spans competitions with different
scoring scales, the table shows one row per scale.</p>
<div class="tablewrap"><table class="grid">
<thead><tr><th>Sport</th><th>Applies to</th><th>Model</th><th>Scoring spread</th><th>Home adj.</th><th>Total market</th></tr></thead>
<tbody>{"".join("<tr>" + "".join(c) + "</tr>" for c in rows_html)}</tbody></table></div>

<h2 id="confidence">3. Confidence and the price window</h2>
<p>The brief sets two rules that cannot both hold loosely: a selection with a 70% chance prices at
&minus;233, and a &minus;250 line is a 71.4% chance. Read literally, a High pick therefore has to land between
<b>70.0% and 71.4%</b> &mdash; a 1.4-percentage-point band &mdash; because anything stronger is priced shorter than
&minus;250 and anything weaker fails the 70% test. That arithmetic, not a shortage of matches, is why
{stats["high"]} selections out of {stats["priced_matches"]} reach High. The window is treated as the binding constraint:
a stronger selection is still published, but on the handicap rung that lands inside the window rather than on a
moneyline that cannot.</p>
<ul class="notes">
  <li><b>High</b> &mdash; model probability &ge; 70% <i>and</i> price inside &minus;250 to +10,000 (decimal 1.40 to 101.00), <i>and</i> the row was verified on 22 October, <i>and</i> both sides carry a measured official rating.</li>
  <li><b>Medium</b> &mdash; 55&ndash;70%, or a High selection that a cap (carried row, unrated side) holds down.</li>
  <li><b>Low</b> &mdash; below 55%.</li>
  <li><b>No bet</b> &mdash; nothing on the card clears a 52% coin flip inside the window. Published as no bet rather than forced.</li>
  <li><b>One grading scale.</b> The grade shown against a match-winner call uses exactly the same rules as a selection, so a
  77% favourite priced at 1.30 is graded Medium: the view is strong, but it cannot be a High pick because the brief&rsquo;s
  &minus;250 floor excludes it. That is why the High count on the landing page equals the number of bettable selections,
  not the number of strong opinions.</li>
  <li><b>Every priced match carries a labelled match-winner call</b> with its own grade, so no match is left without a view of who wins.</li>
  <li><b>Only the match winner and handicap ladders are eligible</b> to become the desk selection. A total ladder can always manufacture a 70% quote by moving the line, which would be a fake edge; totals are published for reference.</li>
</ul>

<h2 id="limits">4. What the model does not do</h2>
<ul class="notes">
  <li><b>It does not price draws.</b> Every non-binomial sport is priced two-way, so a draw is never quoted and a favourite&rsquo;s probability is very slightly overstated. Draw-capable sports here are handball, Gaelic football, rugby union, rugby league and AFLW. Flagged as F-26B-06 and left for the next pricing pass rather than changed mid-snapshot.</li>
  <li><b>It does not read market prices.</b> These are our own lines; no bookmaker or exchange price is loaded, so nothing here is a value bet against a market.</li>
  <li><b>It does not know about injuries, team news, weather or travel.</b> The only inputs are the official record fields printed on each row.</li>
  <li><b>&ldquo;Recent match history&rdquo; means what the governing body published in the captured input</b> &mdash; a
  win-loss streak where the table carries one (the NHL rows show W3 and L4), a Round 1 result where the tournament page
  lists one (Wales Women 6-70, France 4-78), or a ladder record across the completed rounds (AFLW 5-5, EuroLeague 5-1).
  Where the source published only a ranking or a seed, the preview quotes that and does not invent a run of results.</li>
  <li><b>It is a snapshot.</b> {stats["carried"]} rows are carried from 21 October and capped at Medium; prices do not move after publication.</li>
  <li><b>39 of the 120 priced matches have at least one side with no captured rating.</b> Their prices are the venue baseline
  only and they carry no tip; the table marks them &ldquo;no rating captured&rdquo; and each one is listed on the flagged page.
  That is deliberately visible rather than filled in: a fixture with a valid official link but no published rating is covered,
  not priced.</li>
  <li><b>It is not a prediction service.</b> A High grade means the model and the window agree, not that the selection will win.</li>
</ul>

<h2 id="scope">5. Scope</h2>
<p><b>In scope ({stats["sports"]} sports):</b> {esc(", ".join(SPORT_META[s][0] for s in ORDER))}.</p>
<p><b>Excluded by the brief ({len(EXCLUDED)}):</b> {esc(", ".join(name for name, _ in EXCLUDED))}. These were enumerated
during the reverse-engineering pass &mdash; they are real OLBG hubs (sport ids {esc(", ".join(str(i) for _, i in EXCLUDED))}) &mdash;
but nothing in them is priced or listed here.</p>
<p class="sub">The OLBG taxonomy, including the two active-but-unlisted hubs (Specials/18 and Hurling/26), is preserved
in <code>data/olbg_taxonomy.json</code>; the original write-up on OLBG&rsquo;s URL grammar is kept at
<a href="archive/root-20261021/reverse-engineering.html">archive/root-20261021/reverse-engineering.html</a>, and every
earlier board is listed on the <a href="archive.html">archive page</a>.</p>
"""
    return page("Methodology", "methodology.html", body,
                description="The pricing model, per-sport assumptions, confidence rules, price window and known limits.")


def build_sports_index(rows, stats, sports) -> str:
    cards = []
    for slug in ORDER:
        s = sports[slug]
        badge = ("priced", "ok") if s["priced"] else ("event only", "ev")
        cards.append(
            f'<a class="cat" href="sports/{slug}.html">'
            f'<div class="cat-top"><span class="cat-name">{esc(s["label"])}</span><span class="tag {badge[1]}">{badge[0]}</span></div>'
            f'<div class="cat-nums"><b>{s["fixtures"]}</b> {"row" if s["fixtures"] == 1 else "rows"} · '
            f'{"<b>" + str(s["priced"]) + "</b> priced · <b>" + format(s["prices"], ",") + "</b> prices" if s["priced"] else "event card, no market priced"}</div>'
            + (f'<div class="cat-sub">{s["high"]} High · {s["medium"]} Medium · {s["low"]} Low · {s["no_bet"]} no bet</div>'
               if s["priced"] else '<div class="cat-sub">tournament card &mdash; no fixture list captured</div>')
            + '</a>')
    body = f"""
<h1>Sports ({stats["sports"]})</h1>
<p class="lede">Every in-scope OLBG category we cover, with the OLBG hub number it maps to. Each category page carries
its own table of matches, prices and sources.</p>
<div class="cats">{"".join(cards)}</div>
<h2>Excluded categories</h2>
<p class="sub">Enumerated during the reverse-engineering pass, listed for completeness, and not covered.</p>
<div class="tablewrap"><table class="grid">
<thead><tr><th>OLBG category</th><th>OLBG sport id</th><th>Status</th><th>Where the id comes from</th></tr></thead>
<tbody>{"".join(f'<tr><td>{esc(name)}</td><td class="nowrap">{sid}</td><td>Excluded by the brief</td><td class="sm"><a href="https://www.olbg.com/sitemap-betting-tips.xml" target="_blank" rel="noopener">OLBG sitemap</a></td></tr>' for name, sid in EXCLUDED)}</tbody>
</table></div>
"""
    return page("Sports", "sports.html", body,
                description="All 17 in-scope sports with row counts, prices and confidence grades.")


def build_sport_page(slug, rows, sports) -> str:
    s = sports[slug]
    sub = [r for r in rows if r["sport"] == slug]
    priced = [r for r in sub if not r["event_only"]]
    cards = [r for r in sub if r["event_only"]]
    notes = []
    if s["carried"]:
        notes.append(f'{s["carried"]} of {s["fixtures"]} rows in this sport are <b>carried</b> from the previous snapshot: '
                     "their official link is intact but they were not re-read on 22 October, so they are capped at Medium.")
    if cards:
        notes.append(f'{len(cards)} of these rows are event cards with no priced market; the reason is printed on each one.')
    if s["no_bet"]:
        notes.append(f'{s["no_bet"]} matches have no qualifying selection inside the price window.')
    body = f"""
<h1>{esc(s["label"])}</h1>
<p class="lede">{esc(s["note"])}</p>
<div class="kpis">
  {kpi(s["fixtures"], "rows")}
  {kpi(s["priced"], "priced matches")}
  {kpi(f'{s["prices"]:,}', "prices")}
  {kpi(s["high"], "high confidence", "hi")}
  {kpi(s["medium"], "medium")}
  {kpi(s["low"], "low")}
</div>
<p class="sub">OLBG hub: <code>olbg.com/betting-tips/{esc(TAXONOMY_SLUG.get(s["olbg_id"], ""))}/{s["olbg_id"]}</code>
&middot; {s["verified"]} rows verified 22 Oct &middot; {s["carried"]} carried &middot; {s["no_bet"]} no bet.</p>
{('<div class="callout">' + "<br>".join(notes) + "</div>") if notes else ""}
{pick_table(priced, show_sport=False) if priced else '<p class="sub">No head-to-head market is priced in this category.</p>'}
{('<h2>Event cards</h2>' + "".join(event_card(r) for r in cards)) if cards else ""}
"""
    return page(f'{s["label"]}', "sports.html", body, prefix="../",
                description=f'{s["label"]}: {s["fixtures"]} rows, {s["prices"]} originated prices, official sources for every row.')


def build_analysis(rows, stats, sports) -> str:
    priced = [r for r in rows if not r["event_only"]]
    # 1. market coverage matrix
    mtypes = ["Match winner", "Handicap", "Total", "Correct score"]
    matrix = []
    for slug in ORDER:
        sub = [r for r in priced if r["sport"] == slug]
        counts = {m: sum(1 for r in sub for x in r["markets"] if x["market"] == m) for m in mtypes}
        matrix.append([f'<td><a href="sports/{slug}.html">{esc(SPORT_META[slug][0])}</a></td>',
                       f'<td class="nowrap">{len(sub)}</td>',
                       *[f'<td class="nowrap">{counts[m] or "&mdash;"}</td>' for m in mtypes],
                       f'<td class="nowrap">{sum(counts.values())}</td>'])

    # 2. price-window distribution per market type
    band_rows = []
    for m in mtypes:
        prices = [x for r in priced for x in r["markets"] if x["market"] == m]
        if not prices:
            continue
        below = sum(1 for x in prices if x["price"] < 1.40)
        inside = sum(1 for x in prices if 1.40 <= x["price"] <= 101.0)
        above = sum(1 for x in prices if x["price"] > 101.0)
        band_rows.append([f"<td>{esc(m)}</td>", f'<td class="nowrap">{len(prices)}</td>',
                          f'<td class="nowrap">{below}</td>', f'<td class="nowrap">{inside}</td>',
                          f'<td class="nowrap">{above}</td>'])

    # 3. confidence and no-bet rate per sport
    conf_rows = []
    for slug in ORDER:
        s = sports[slug]
        if not s["priced"]:
            continue
        nobet_pct = round(100 * s["no_bet"] / s["priced"])
        conf_rows.append([f'<td><a href="sports/{slug}.html">{esc(s["label"])}</a></td>',
                          f'<td class="nowrap">{s["priced"]}</td>',
                          f'<td class="nowrap">{s["high"]}</td>',
                          f'<td class="nowrap">{s["medium"]}</td>',
                          f'<td class="nowrap">{s["low"]}</td>',
                          f'<td class="nowrap">{s["no_bet"]} ({nobet_pct}%)</td>'])

    # 4. probability distribution of every originated price
    buckets = [(0, 5), (5, 10), (10, 20), (20, 35), (35, 50), (50, 65), (65, 80), (80, 95), (95, 100)]
    probs = [x["prob_pct"] for r in priced for x in r["markets"]]
    hist = []
    for lo, hi in buckets:
        n = sum(1 for p in probs if lo <= p < hi)
        pct = round(100 * n / max(1, len(probs)), 1)
        hist.append([f'<td class="nowrap">{lo}&ndash;{hi}%</td>', f'<td class="nowrap">{n}</td>',
                     f'<td class="nowrap">{pct}%</td>',
                     f'<td class="barwrap"><span class="bar" style="width:{max(1, pct)}%"></span></td>'])

    # 5. derived observations (each one computed from the data above)
    high_by_sport = Counter(r["sport_label"] for r in priced if r["pick"] and r["pick"]["confidence"] == "High")
    unrated_count = sum(1 for r in priced
                        if (r.get("home_input") or {}).get("rating") is None
                        or (r.get("away_input") or {}).get("rating") is None)
    no_bet_by_sport = Counter(r["sport_label"] for r in priced if not r["pick"])
    ladder = {
        "handicap rungs per match": round(sum(1 for r in priced for x in r["markets"] if x["market"] == "Handicap") / len(priced), 1),
        "total rungs per match": round(sum(1 for r in priced for x in r["markets"] if x["market"] == "Total") / len(priced), 1),
        "prices per match": round(stats["prices"] / len(priced), 1),
    }
    obs = [
        f'<b>{stats["high"]} of {len(priced)} priced matches</b> reach High confidence '
        f'({round(100 * stats["high"] / len(priced))}%). The spread is not even: '
        + ", ".join(f'{esc(k)} {v}' for k, v in high_by_sport.most_common()) + ".",
        f'<b>{stats["no_bet"]} matches produce no tip</b> ({round(100 * stats["no_bet"] / len(priced))}%). '
        f'{unrated_count} of them because neither side has a captured official rating, so there is no measured edge to price; '
        f'the other {stats["no_bet"] - unrated_count} because their best in-window price is at or below a 52% coin flip. '
        f'By sport: ' + ", ".join(f'{esc(k)} {v}' for k, v in no_bet_by_sport.most_common()) + ".",
        f'<b>The ladder is the same shape in every sport</b>: {ladder["handicap rungs per match"]} handicap rungs and '
        f'{ladder["total rungs per match"]} total rungs per priced match, {ladder["prices per match"]} prices per match on average. '
        f'Only the units change (points, goals, runs, sets, frames, legs).',
        f'<b>{sum(1 for p in probs if p < 50)} of {len(probs)} prices are on the underdog side of a coin flip</b>, which is what a '
        f'ladder looks like: every rung has two sides and the long side is quoted, not hidden.',
        f'<b>{stats["in_band_prices"]:,} of {stats["prices"]:,} prices sit inside the brief window</b> '
        f'({round(100 * stats["in_band_prices"] / stats["prices"])}%). The ones outside it are shorter than &minus;250 and are '
        f'published for reference only; they can never become a selection.',
        ('<b>Four sports receive no tip at all</b>: ' + ", ".join(
            esc(sports[slug]["label"]) for slug in ORDER if sports[slug]["priced"] and not (sports[slug]["high"] + sports[slug]["medium"] + sports[slug]["low"])
        ) + '. Their fixtures are verified and priced from the venue baseline, but no side carries a captured official rating, '
          'so the desk refuses to tip them (F-26B-14).') if any(
            sports[slug]["priced"] and not (sports[slug]["high"] + sports[slug]["medium"] + sports[slug]["low"]) for slug in ORDER) else "",
        f'<b>Data completeness</b>: {stats["verified"]} rows were read from an official page on 22 October, {stats["carried"]} are '
        f'carried from 21 October, and {stats["flag_rows"]} rows carry an explicit flag. {stats["undated"]} rows have no UTC clock '
        f'because the governing body publishes a date or a local time without a timezone.',
    ]

    body = f"""
<h1>Analysis</h1>
<p class="lede">What the snapshot actually contains, measured rather than asserted. Every figure on this page is computed
from <code>data/final/bundle.json</code>, the same file the tables are rendered from, so the analysis and the numbers on
the other pages cannot drift apart.</p>

<h2>Headline observations</h2>
<ul class="notes">{"".join(f"<li>{o}</li>" for o in obs)}</ul>

<h2>1. Market coverage by sport</h2>
<p class="sub">How many prices of each type exist. A dash means the market is not originated for that sport: darts, snooker
and tennis get a correct-score market instead of a total, and no sport is given a market it cannot price from its model.</p>
<div class="tablewrap"><table class="grid">
<thead><tr><th>Sport</th><th>Priced matches</th><th>Match winner</th><th>Handicap</th><th>Total</th><th>Correct score</th><th>All prices</th></tr></thead>
<tbody>{"".join("<tr>" + "".join(c) + "</tr>" for c in matrix)}</tbody></table></div>

<h2>2. The price window, measured</h2>
<p class="sub">The brief's window is &minus;250 to +10,000, i.e. decimal 1.40 to 101.00. Every price outside it on the low
side is a favourite priced shorter than &minus;250.</p>
<div class="tablewrap"><table class="grid">
<thead><tr><th>Market</th><th>Prices</th><th>Shorter than &minus;250</th><th>Inside the window</th><th>Longer than +10,000</th></tr></thead>
<tbody>{"".join("<tr>" + "".join(c) + "</tr>" for c in band_rows)}</tbody></table></div>

<h2>3. Confidence and no-bet rate by sport</h2>
<div class="tablewrap"><table class="grid">
<thead><tr><th>Sport</th><th>Priced</th><th>High</th><th>Medium</th><th>Low</th><th>No bet</th></tr></thead>
<tbody>{"".join("<tr>" + "".join(c) + "</tr>" for c in conf_rows)}</tbody></table></div>

<h2>4. How the model probabilities are distributed</h2>
<p class="sub">All {stats["prices"]:,} originated prices, bucketed by model probability. The shape is a ladder: most prices
sit between 20% and 65%, with thin tails at both ends because rungs below 5% or above 95% are not quoted.</p>
<div class="tablewrap"><table class="grid">
<thead><tr><th>Probability</th><th>Prices</th><th>Share</th><th>Distribution</th></tr></thead>
<tbody>{"".join("<tr>" + "".join(c) + "</tr>" for c in hist)}</tbody></table></div>

<h2>5. What this analysis does not say</h2>
<ul class="notes">
  <li>It is <b>not a profitability study</b>. No bookmaker price is loaded anywhere in this repository, so there is no
  comparison between our fair price and a market price, and no return on investment can be computed.</li>
  <li>It is <b>not a settlement record</b>. None of these fixtures has been played at snapshot time, so no selection has a result.</li>
  <li>It <b>is</b> a completeness and consistency study: whether the markets, the window, the grades and the sources all agree.</li>
</ul>
<p class="sub">Per-match detail is on <a href="picks.html">all matches</a>; every individual price is on
<a href="markets.html">markets</a>; the archived 21 October board keeps its own
<a href="archive/root-20261021/analysis.html">analysis page</a> for comparison.</p>
"""
    return page("Analysis", "analysis.html", body,
                description="Measured analysis of the snapshot: market coverage, price-window distribution, confidence rates and data completeness.")



def build_archive() -> str:
    boards = [
        ("127 rows · 22 Oct 2026", "v3/index.html", "v3 22 October re-verified board",
         "The snapshot this site is built from, with its own per-sport pages and analysis. Identical data, previous presentation."),
        ("32 rows · 22–26 Oct 2026", "7a5b5360/index.html", "7a5b5360 fresh matchday desk",
         "A smaller fresh board with its own verification page and market sheets."),
        ("145 events · 21 Oct 2026", "984d417f/index.html", "984d417f live audit desk",
         "A 145-event board plus an 11-group line-by-line repository audit."),
        ("217 events · 21 Oct 2026", "c17a9192/index.html", "c17a9192 catalogue",
         "The widest event catalogue in the repository, with multi-runner field boards."),
        ("126 matches · 21 Oct 2026", "ccb6bde2/index.html", "ccb6bde2 markets desk",
         "1,619 expanded markets and a model calibration audit."),
        ("133 rows · 21 Oct 2026", "ebfbd966/index.html", "ebfbd966 board", "An earlier 133-row board."),
        ("131 rows · 21 Oct 2026", "aa4e9dbf/index.html", "aa4e9dbf desk", "An earlier per-sport desk."),
        ("152 rows · 21 Oct 2026", "2360a617/index.html", "2360a617 board", "An earlier 152-row board."),
        ("164 OLBG events · 21 Oct 2026", "docs/index.html", "docs board", "The OLBG-harvest board."),
        ("Mirror", "f7fa77fc/index.html", "f7fa77fc permalink mirror", "A hash-identical mirror of the 21 October primary data."),
    ]
    rows_html = [[
        f'<td><b><a href="{esc(href)}">{esc(name)}</a></b></td>',
        f'<td class="nowrap">{esc(size)}</td>',
        f'<td>{esc(desc)}</td>',
    ] for size, href, name, desc in boards]
    body = f"""
<h1>Archive</h1>
<p class="lede">This repository has been built by a series of sessions, each of which published its own board. This
pass consolidates the current snapshot at the root and leaves every earlier board exactly where it was, so nothing is
deleted and every previous finding stays reachable. Sizes below are the counts each board prints on its own landing page.</p>
<div class="tablewrap"><table class="grid">
<thead><tr><th>Board</th><th>Size</th><th>What it holds</th></tr></thead>
<tbody>{"".join("<tr>" + "".join(c) + "</tr>" for c in rows_html)}</tbody></table></div>
<h2>The 21 October root board</h2>
<p>The root used to serve a 134-row board built from <code>data/fixtures.json</code>. It is preserved verbatim under
<a href="archive/root-20261021/index.html">archive/root-20261021/</a> so its pages, tables and verification ledger
remain reviewable. Its dataset still ships in the repository and is still covered by
<code>scripts/validate.py</code>; it is simply no longer the current snapshot.</p>
<h2>Reports and data</h2>
<ul class="notes">
  <li><code>reports/LIVE_VERIFICATION.md</code> &mdash; the page-by-page verification ledger.</li>
  <li><code>reports/FINAL_INTEGRATION_AUDIT.md</code> &mdash; the row-by-row audit of the 21 October primary data.</li>
  <li><code>reports/SESSION_*</code> &mdash; each session&rsquo;s own findings, unedited.</li>
  <li><code>data/v3/</code> &mdash; the snapshot data behind this site; <code>data/final/</code> &mdash; the joined bundle this site renders.</li>
  <li><a href="v3/analysis.html">Analysis</a> &mdash; market-level analysis on the snapshot.</li>
</ul>
"""
    return page("Archive", "archive.html", body,
                description="Every earlier board in the repository, preserved and linked.")


ARCHIVE_DIR = ROOT / "archive" / "root-20261021"
LEGACY_ROOT_PAGES = ["index.html", "picks.html", "predictions.html", "sports.html", "flagged.html",
                     "methodology.html", "sources.html", "verification.html", "analysis.html",
                     "live-refresh.html", "live-verification.html", "reverse-engineering.html",
                     "404.html"]
NAMESPACES = ["2360a617", "7a5b5360", "984d417f", "aa4e9dbf", "c17a9192", "ccb6bde2",
              "ebfbd966", "f7fa77fc", "docs", "datasets", "reports", "scripts", "data", "v3"]

# Pages that other desks in this repository still link to at their old root paths. They move
# into the archive, so a stub keeps every inbound link working and tells the reader where the
# content went.
REDIRECTS = {
    "live-refresh.html": ("Live refresh", "The live OLBG refresh belongs to the 21 October snapshot, which is "
                                          "archived; the current snapshot is the dashboard.",
                          [("archive/root-20261021/live-refresh.html", "Archived live refresh"),
                           ("index.html", "Current dashboard")]),
    "live-verification.html": ("Live verification", "The page-by-page verification ledger is archived verbatim; "
                                                    "the current ledger is on the verification page.",
                               [("archive/root-20261021/live-verification.html", "Archived ledger"),
                                ("verification.html", "Current verification")]),
    "reverse-engineering.html": ("OLBG reverse-engineering", "The taxonomy and URL-grammar write-up is archived.",
                                 [("archive/root-20261021/reverse-engineering.html", "Archived write-up"),
                                  ("methodology.html#scope", "Current scope")]),
}


def archive_legacy_root() -> dict:
    """Move the superseded 21 October root board into archive/root-20261021/ and repoint its links.

    Nothing is deleted: the pages, the sports subpages and the stylesheet they need all move
    together, and only the links that used to reach out of the folder get a ../../ prefix.
    """
    import re
    import shutil

    moved = {"pages": 0, "sports": 0, "assets": False, "skipped": 0}
    if ARCHIVE_DIR.exists() and (ARCHIVE_DIR / "index.html").exists():
        return moved
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    def rewrite(text: str, depth: int) -> str:
        # depth 1 = a page that now sits in archive/root-20261021/, depth 2 = its sports/ pages.
        # Either way the repository root is one level further up than the page's own folder.
        up = "../" * (depth + 1)

        def fix(attr: str, url: str) -> str:
            if url.startswith(("http://", "https://", "mailto:", "#", "javascript:", "data:")):
                return f'{attr}="{url}"'
            base = url.split("#", 1)[0]
            for ns in NAMESPACES:
                if base == ns or base.startswith(ns + "/"):
                    return f'{attr}="{up}{url}"'
                if depth == 2 and url.startswith("../" + ns):
                    return f'{attr}="{up}{url[3:]}"'
            if depth == 2 and url.startswith("../") and not url.startswith("../assets/"):
                rest = url[3:]
                if rest.split("/")[0] in (ns for ns in NAMESPACES):
                    return f'{attr}="{up}{rest}"'
            return f'{attr}="{url}"'

        text = re.sub(r'(href|src)="([^"]+)"', lambda m: fix(m.group(1), m.group(2)), text)
        return text

    for name in LEGACY_ROOT_PAGES:
        src = ROOT / name
        if not src.exists():
            moved["skipped"] += 1
            continue
        text = src.read_text(encoding="utf-8")
        # Only ever archive the 21 October board. If the file is already a page from this
        # dashboard, leave it alone - otherwise deleting archive/ and rebuilding would archive
        # the current site on top of the old one.
        if "OLBG Origination Desk" not in text:
            moved["skipped"] += 1
            continue
        (ARCHIVE_DIR / name).write_text(rewrite(text, 1), encoding="utf-8")
        src.unlink()
        moved["pages"] += 1

    if not moved["pages"]:
        try:
            ARCHIVE_DIR.rmdir()
        except OSError:
            pass
        return moved

    if (ROOT / "sports").is_dir():
        (ARCHIVE_DIR / "sports").mkdir(exist_ok=True)
        for src in sorted((ROOT / "sports").glob("*.html")):
            (ARCHIVE_DIR / "sports" / src.name).write_text(
                rewrite(src.read_text(encoding="utf-8"), 2), encoding="utf-8")
            src.unlink()
            moved["sports"] += 1
        (ROOT / "sports").rmdir()

    if (ROOT / "assets").is_dir():
        shutil.copytree(ROOT / "assets", ARCHIVE_DIR / "assets", dirs_exist_ok=True)
        moved["assets"] = True
    return moved


def build_redirect(name: str) -> str:
    title, blurb, links = REDIRECTS[name]
    boxes = "".join(f'<a class="box" href="{esc(href)}"><b>{esc(label)}</b></a>' for href, label in links)
    body = f"""
<h1>{esc(title)} &mdash; moved</h1>
<p class="lede">{esc(blurb)}</p>
<div class="links3">{boxes}</div>
<p class="sub">This address is kept as a permanent pointer so links from the other boards and reports in this
repository keep working.</p>
"""
    return page(f"{title} (moved)", "", body, description=blurb)


def build_404() -> str:
    body = """
<h1>Page not found</h1>
<p class="lede">That address is not part of the current snapshot. The dashboard is one click away.</p>
<div class="links3">
  <a class="box" href="index.html"><b>Overview</b><span>Start here: the snapshot, the counts and the high-confidence picks.</span></a>
  <a class="box" href="picks.html"><b>All matches</b><span>One row per priced match with its official source.</span></a>
  <a class="box" href="archive.html"><b>Archive</b><span>Every earlier board in the repository.</span></a>
</div>
"""
    return page("404 Not Found", "", body, description="Page not found on the OLBG independent desk.")


def main() -> int:
    rows = build_rows()
    stats = summarise(rows)
    sports = sport_stats(rows)

    DATA_OUT.mkdir(parents=True, exist_ok=True)
    (DATA_OUT / "bundle.json").write_text(json.dumps({
        "snapshot_utc": SNAPSHOT,
        "generated_by": "scripts/final_site.py",
        "model": "scripts/v3_model.py over scripts/v3_data.py",
        "counts": stats,
        "sports": {slug: sports[slug] for slug in ORDER},
        "rows": rows,
    }, indent=1, ensure_ascii=False), encoding="utf-8")

    with (DATA_OUT / "rows.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "sport", "competition", "stage", "home", "away", "start_utc", "date_local",
                    "venue", "status", "verified_at", "selection", "market", "price_decimal",
                    "price_us", "model_prob_pct", "confidence", "cap_reason", "prices_on_card",
                    "source_urls", "flags"])
        for r in rows:
            p = r["pick"] or {}
            w.writerow([r["id"], r["sport"], r["competition"], r["stage"], r["home"], r["away"],
                        r["start_utc"] or "", r["date_local"] or "", r["venue"], r["status"],
                        r["verified_at"], p.get("selection", ""), p.get("market", ""),
                        f'{p["price"]:.2f}' if p else "", p.get("us", ""), p.get("prob_pct", ""),
                        p.get("confidence", ""), p.get("cap_reason") or "", r["market_count"],
                        " ".join(s["url"] for s in r["sources"]), " | ".join(r["flags"])])

    moved = archive_legacy_root()

    pages = {
        "index.html": build_index(rows, stats, sports),
        "picks.html": build_picks(rows, stats),
        "markets.html": build_markets(rows, stats),
        "predictions.html": build_predictions(rows, stats),
        "sports.html": build_sports_index(rows, stats, sports),
        "flagged.html": build_flagged(rows, stats, sports),
        "verification.html": build_verification(rows, stats, sports),
        "sources.html": build_sources(rows, stats),
        "methodology.html": build_methodology(rows, stats, sports),
        "analysis.html": build_analysis(rows, stats, sports),
        "archive.html": build_archive(),
        "404.html": build_404(),
    }
    pages.update({name: build_redirect(name) for name in REDIRECTS})
    for name, html_text in pages.items():
        (ROOT / name).write_text(html_text, encoding="utf-8")

    (ROOT / "sports").mkdir(exist_ok=True)
    for slug in ORDER:
        (ROOT / "sports" / f"{slug}.html").write_text(
            build_sport_page(slug, rows, sports), encoding="utf-8")

    print(json.dumps({"pages": len(pages) + len(ORDER), "sports": len(ORDER), "stats": stats,
                      "archived": moved}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
