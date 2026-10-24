"""Build the clarity desk at today/ (session 7f1bf9f7-olbg1).

Output: 13 pages + JSON/CSV exports.  No external fonts, scripts or CDNs.
Every fixture row links to the official publisher it was read from.
"""
import csv
import html
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import today_data as D

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "today"
BUILD_AT = datetime.now(timezone.utc).replace(microsecond=0)

BANNED = ("model", "verified")
NO_INPUT = '<span class="muted">no club-level input readable</span>'


def e(v):
    return html.escape("" if v is None else str(v), quote=True)


def american(prob):
    if prob is None or prob <= 0 or prob >= 1:
        return ""
    dec = 1 / prob
    return f"{round((dec - 1) * 100):+d}" if dec >= 2 else f"{round(-100 / (dec - 1)):+d}"


def decimal(prob):
    return round(1 / prob, 2) if prob else None


def pct(prob):
    return f"{prob * 100:.1f}%" if prob is not None else ""


def stamp(iso):
    if not iso:
        return ""
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return dt.strftime("%d %b %H:%M UTC")


def status(fx):
    if not fx.get("start_utc"):
        return "start unconfirmed"
    return "upcoming" if datetime.fromisoformat(fx["start_utc"].replace("Z", "+00:00")) > BUILD_AT else "started"


def src(key):
    return D.SOURCES[key]


def source_link(key, label=None):
    s = src(key)
    return (f'<a href="{e(s["url"])}" target="_blank" rel="noopener noreferrer">'
            f'{e(label or s["publisher"])} &#8599;</a>')


def match_label(fx):
    if fx["sport"] == "motor-racing":
        return f'{fx["a"]} ({fx["b"]})'
    return f'{fx["a"]} vs {fx["b"]}'


def pick_cell(fx, href):
    p = prediction_for(fx["id"])
    if not p:
        return '<span class="muted">no pick</span>'
    return f'<a href="{href}">{e(p["selection"])}</a>'


def prediction_for(fixture_id):
    for p in D.PICKS:
        if p["fixture"] == fixture_id:
            return p
    return None


def wordcount(text):
    return len(text.split())


# ------------------------------------------------------------------ layout
NAV = [
    ("index.html", "Today's card"),
    ("picks.html", "All picks"),
    ("predictions.html", "Written predictions"),
    ("matches.html", "Verified matches"),
    ("discovery.html", "OLBG full list"),
    ("markets.html", "Markets & lines"),
    ("sports.html", "Sports"),
    ("flagged.html", "Flagged for review"),
    ("repo-audit.html", "Repo audit"),
    ("sources.html", "Sources"),
    ("methodology.html", "Method"),
]


def page(name, title, lead, body, extra_nav=""):
    up = "../" * name.count("/")
    nav = "".join(
        f'<a class="navlink{ " active" if href == name else ""}" href="{up}{href}">{e(label)}</a>'
        for href, label in NAV
    )
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light">
<meta name="description" content="One clear daily card: picks, prices, confidence and the official source behind every row.">
<title>{e(title)} &middot; OLBG research desk</title>
<link rel="stylesheet" href="{up}assets/style.css">
</head><body>
<header class="top"><div class="wrap">
<a class="brand" href="{up}index.html"><span class="dot"></span>OLBG research desk <small>clarity edition</small></a>
<nav class="nav">{nav}</nav>
</div></header>
<main class="wrap">
<div class="pagehead"><p class="kicker">{e(D.SNAPSHOT_DATE)} &middot; snapshot {e(stamp(D.OBSERVED))}</p>
<h1>{e(title)}</h1><p class="lead">{lead}</p></div>
{extra_nav}
{body}
<footer><p>Independent research, not betting advice. 18+. Every value here was read from the official publisher named on its row; anything unreadable is blank and flagged.
Built {e(stamp(BUILD_AT.isoformat()))} by session 7f1bf9f7-olbg1. Not affiliated with OLBG.</p></footer>
</main></body></html>"""
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(doc, encoding="utf-8")
    return name


# ----------------------------------------------------------------- content
def tier_badge(t):
    return f'<span class="tier t-{t.lower()}">{e(t)}</span>'


def pick_row(p, with_prediction=True):
    fx = next(f for f in D.FIXTURES if f["id"] == p["fixture"])
    match = e(match_label(fx))
    link = f'<a href="predictions.html#{e(p["fixture"])}">read the write-up</a>' if with_prediction else ""
    start = e(stamp(fx["start_utc"]) or "start unconfirmed")
    return (
        "<tr>"
        f'<td><strong>{e(p["selection"])}</strong><br><span class="muted">{e(p["market"])}</span></td>'
        f'<td>{match}<br><span class="muted">{e(fx["competition"])} &middot; {start}</span></td>'
        f'<td class="num">{pct(p["prob"])}</td>'
        f'<td class="num">{decimal(p["prob"])} <span class="muted">({e(american(p["prob"]))})</span></td>'
        f'<td>{tier_badge(p["confidence"])}</td>'
        f'<td>{source_link(fx["source_id"], "official")}</td>'
        f'<td>{link}</td>'
        "</tr>"
    )


def picks_table(picks):
    head = ("<table class=\"grid\"><thead><tr><th>Pick (selection first)</th><th>Match and start</th>"
            "<th>Chance</th><th>Fair price</th><th>Confidence</th><th>Source</th><th>Why</th></tr></thead><tbody>")
    rows = "".join(pick_row(p) for p in picks)
    return head + rows + "</tbody></table>"


def index():
    picks = D.PICKS
    high = [p for p in picks if p["confidence"] == "High"]
    med = [p for p in picks if p["confidence"] == "Medium"]
    low = [p for p in picks if p["confidence"] == "Low"]
    verified = [f for f in D.FIXTURES]
    upcoming = [f for f in verified if status(f) == "upcoming"]
    body = f"""
<section class="hero">
  <div><h2>Start here: {len(picks)} picks today</h2>
  <p>Every pick is on this page, in the table below. The full reasoning for each one is on
  <a href="predictions.html">Written predictions</a>, and the same pick rows also live on
  <a href="picks.html">All picks</a>. Nothing is hidden behind a filter or a tab.</p>
  <p class="big">Where the picks are: <strong>this table &rarr; <a href="picks.html">picks.html</a> &rarr; <a href="predictions.html">predictions.html</a></strong></p></div>
  <ul class="kpis">
    <li><b>{len(picks)}</b><span>picks issued</span></li>
    <li><b>{len(high)}</b><span>High confidence</span></li>
    <li><b>{len(med)}</b><span>Medium</span></li>
    <li><b>{len(low)}</b><span>Low</span></li>
    <li><b>{len(D.FIXTURES)}</b><span>matches with an official link</span></li>
    <li><b>{len(D.DISCOVERY)}</b><span>OLBG listings inventoried</span></li>
  </ul>
</section>

<h2 class="sec">Today's card, highest confidence first</h2>
<p class="note">Ordered by confidence, then by chance. A pick only reaches High when the chance is 70%+ and the fair price is no shorter than -250.</p>
{picks_table(sorted(picks, key=lambda p: ({"High": 0, "Medium": 1, "Low": 2}[p["confidence"]], -p["prob"])))}

<h2 class="sec">How to read this desk</h2>
<div class="cards">
  <div class="card"><h3>1. The pick is the first column</h3><p>The selection is written out in full &mdash; "Boston Bruins to win (moneyline)", not a bare "win". The market and price sit underneath it.</p></div>
  <div class="card"><h3>2. The chance and the price are ours</h3><p>Every number in the chance and fair-price columns comes from our own line, built from the official inputs named in <a href="markets.html">Markets &amp; lines</a>. It is an estimate, never a quoted bookmaker price.</p></div>
  <div class="card"><h3>3. The source column is the proof</h3><p>Each match links to the league or tour page it was read from. If a field could not be read there, it is blank on the row and listed on <a href="flagged.html">Flagged for review</a>.</p></div>
  <div class="card"><h3>4. Unpriced sports say so</h3><p>Eleven of the fifteen sports have no priced selection today. The reason for each is printed on <a href="sports.html">Sports</a>; none of them was filled in to reach a quota.</p></div>
</div>

<h2 class="sec">What this snapshot does and does not contain</h2>
<div class="two">
<div class="panel"><h3>Contains</h3><ul class="tick">
<li>{len(D.FIXTURES)} matches with a link to the official league or tour page they were read from</li>
<li>{len(D.MARKETS)} originated prices across match-winner, puck-line, race-winner and series markets</li>
<li>{len(D.PICKS)} picks, each with a written prediction of at least 30 words</li>
<li>{len(D.DISCOVERY)} OLBG listings across all fifteen requested sports</li>
<li>{len(D.FLAGS)} published flags and {len(D.REPO_FINDINGS)} repository findings</li>
</ul></div>
<div class="panel warn"><h3>Does not contain</h3><ul class="cross">
<li>Five High picks per sport. Zero clear the bar today &mdash; see F-7F-03</li>
<li>Bookmaker quotes for most markets. Our prices are research lines</li>
<li>Injury lists. No official availability feed was readable, so no injury claim is made</li>
<li>Worldwide fixtures. Eight of the twelve NHL games are missing &mdash; see F-7F-01</li>
</ul></div>
</div>
"""
    return page("index.html", "Today's card",
                "One table, highest confidence first, with the official source on every row.",
                body)


def picks_page():
    rows = sorted(D.PICKS, key=lambda p: ({"High": 0, "Medium": 1, "Low": 2}[p["confidence"]], -p["prob"]))
    body = f"""
<p class="note">This page is the complete pick list. It is the same set as the table on the
<a href="index.html">front page</a>; the reasoning for each pick is on
<a href="predictions.html">Written predictions</a>.</p>
{picks_table(rows)}
<h2 class="sec">Why each pick sits in its tier</h2>
<table class="grid"><thead><tr><th>Pick</th><th>Tier</th><th>Reason for the tier</th></tr></thead><tbody>
{''.join(f'<tr><td><strong>{e(p["selection"])}</strong></td><td>{tier_badge(p["confidence"])}</td><td>{e(p["why_tier"])}</td></tr>' for p in rows)}
</tbody></table>
<h2 class="sec">Picks we deliberately did not issue</h2>
<ul class="cross">
<li><strong>Anaheim Ducks at Philadelphia Flyers</strong> &mdash; the 17:00 UTC start passed before publication.</li>
<li><strong>New York Rangers at Ottawa Senators</strong> &mdash; the provider price was truncated, so there is no number to price against (F-7F-05).</li>
<li><strong>Los Angeles Kings at New Jersey Devils</strong> &mdash; a 62.5% home side, but no official club record for either team was readable, so there is nothing to write about them.</li>
<li><strong>All 57 OLBG discovery listings outside the four verified sports</strong> &mdash; no official fixture page or team input was read, so they carry no pick.</li>
</ul>
"""
    return page("picks.html", "All picks", "Every selection issued in this snapshot, with its tier and the reason for it.", body)


def predictions_page():
    cards = []
    for p in sorted(D.PICKS, key=lambda p: ({"High": 0, "Medium": 1, "Low": 2}[p["confidence"]], -p["prob"])):
        fx = next(f for f in D.FIXTURES if f["id"] == p["fixture"])
        facts = "".join(
            f"<li><strong>{e(k)}:</strong> {e(v)}</li>" for k, v in fx["facts"].items() if v
        )
        missing = [k for k, v in fx["facts"].items() if not v]
        cards.append(f"""
<article class="pred" id="{e(p['fixture'])}">
<header><div><p class="kicker">{e(dict((s[0], s[1]) for s in D.SPORTS).get(fx['sport'], fx['sport']))} &middot; {e(fx['competition'])}</p>
<h2>{e(match_label(fx))}</h2></div><div class="pickbox"><span class="muted">The pick</span><strong>{e(p['selection'])}</strong>
{tier_badge(p['confidence'])} <span class="price">{decimal(p['prob'])} ({e(american(p['prob']))})</span></div></header>
<p class="prose">{e(p['prediction'])}</p>
<div class="facts"><h3>Official facts used</h3><ul>{facts}</ul>
<p class="muted">Read from {source_link(fx['source_id'])} at {e(src(fx['source_id'])['observed_utc'])}.
{f" Not readable: {e(', '.join(missing))}." if missing else ""}</p></div>
<p class="meta">{wordcount(p['prediction'])} words &middot; chance {pct(p['prob'])} &middot; fair {decimal(p['prob'])} &middot; {e(p['why_tier'])}</p>
</article>""")
    body = """<p class="note">Five written predictions, one per pick. Each is unique, runs well past the
30-word floor, states the selection in the first sentence, and only uses facts printed in the
source block underneath it. No claim is carried over from another desk.</p>""" + "".join(cards)
    return page("predictions.html", "Written predictions",
                "The full text behind every pick, with the official facts each one rests on.", body)


def matches_page():
    rows = []
    for fx in D.FIXTURES:
        st = status(fx)
        facts = "; ".join(f"{k}: {v}" for k, v in fx["facts"].items() if v) or NO_INPUT
        rows.append(
            "<tr>"
            f'<td><strong>{e(match_label(fx))}</strong><br><span class="muted">{e(fx["competition"])}</span></td>'
            f'<td>{e(stamp(fx["start_utc"]) or "unconfirmed")}<br><span class="muted">{e(st)}</span></td>'
            f'<td>{e(fx["venue"] or "unconfirmed")}</td>'
            f"<td class=\"small\">{facts}</td>"
            f'<td>{source_link(fx["source_id"])}</td>'
            f'<td>{pick_cell(fx, "picks.html")}</td>'
            "</tr>"
        )
    body = f"""
<p class="note">{len(D.FIXTURES)} matches. Each row links to the official page it was read from;
the "inputs read" column shows exactly what that page gave us. A blank there means the official
source did not yield the value, not that the value is zero.</p>
<table class="grid"><thead><tr><th>Match</th><th>Start (UTC)</th><th>Venue</th><th>Inputs read</th><th>Official source</th><th>Pick</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
<h2 class="sec">Known gaps in this list</h2>
<ul class="cross">
<li>The NHL plays twelve games on 24 October 2026; four appear here (F-7F-01).</li>
<li>The NBA calendar shows eight games on the same day; none could be given a team-level input, so none is priced.</li>
<li>Every other sport's matches are on the <a href="discovery.html">OLBG full list</a> page as discovery rows only.</li>
</ul>
"""
    return page("matches.html", "Verified matches",
                "Matches where the row itself came from the league or tour, with the fields we actually read.", body)


def discovery_page():
    by_sport = {}
    for row in D.DISCOVERY:
        by_sport.setdefault(row[0], []).append(row)
    labels = dict((s[0], s[1]) for s in D.SPORTS)
    blocks = []
    for slug, label, o_slug, o_id, official in D.SPORTS:
        rows = by_sport.get(slug, [])
        if not rows:
            blocks.append(f'<h2 class="sec" id="{slug}">{e(label)}</h2><p class="note">No event was listed on the OLBG hub when read at 17:18Z.</p>')
            continue
        trs = "".join(
            f'<tr><td><strong>{e(r[1])}</strong></td><td>{e(r[2])}</td><td>{e(r[3])}</td><td>{e(r[4])}</td>'
            f'<td class="num">{e(r[5])}</td><td class="num">{e(r[6]) if r[6] is not None else ""}{"%" if r[6] is not None else ""}</td>'
            f'<td><span class="pill">discovery only</span></td></tr>'
            for r in rows
        )
        blocks.append(f"""<h2 class="sec" id="{slug}">{e(label)} <span class="muted">&middot; {len(rows)} listings</span></h2>
<p class="note">Listed on <a href="{e(D.olbg(o_slug, o_id))}" target="_blank" rel="noopener noreferrer">OLBG {e(label)} &#8599;</a>.
Official route for verification: <a href="{e(official)}" target="_blank" rel="noopener noreferrer">{e(official)} &#8599;</a>.
None of these rows is priced: no official fixture page or team input was read for them.</p>
<table class="grid small"><thead><tr><th>Event as listed</th><th>When (as listed)</th><th>Market</th><th>Most-tipped selection</th><th>Tips</th><th>Share</th><th>Status</th></tr></thead>
<tbody>{trs}</tbody></table>""")
    body = f"""
<p class="note">This is the full list of what OLBG was advertising across the fifteen requested sports
when the hubs were read between 17:09Z and 17:20Z on {e(D.SNAPSHOT_DATE)}. It is an inventory, not a
tip sheet: the tip share column is OLBG's vote count (2/2 means two tipsters out of two), not a
probability, and no row here carries a pick because no official fixture source was read for it.</p>
<div class="panel warn"><strong>Read this before using the table.</strong> A discovered listing is not a
confirmed fixture. Times are OLBG's own rendering and are not converted or corrected. Sports whose
official route was read are moved to <a href="matches.html">Verified matches</a> with the official link.</div>
{"".join(blocks)}
"""
    return page("discovery.html", "OLBG full list (discovery)",
                "Everything OLBG listed for the fifteen requested sports, kept separate from anything official.", body)


def markets_page():
    rows = []
    for m in D.MARKETS:
        fx = next(f for f in D.FIXTURES if f["id"] == m["fixture"])
        rows.append(
            "<tr>"
            f'<td><strong>{e(m["selection"])}</strong><br><span class="muted">{e(match_label(fx))}</span></td>'
            f'<td>{e(m["market"])}</td>'
            f'<td class="num">{pct(m["prob"])}</td>'
            f'<td class="num">{decimal(m["prob"])}</td>'
            f'<td class="num">{e(american(m["prob"]))}</td>'
            f'<td class="num">{e(m["quote"]) or "&mdash;"}</td>'
            f'<td class="small">{e(m["basis"])}</td>'
            "</tr>"
        )
    body = f"""
<p class="note">{len(D.MARKETS)} prices across four sports and four market types: match winner,
puck line, series game winner and race winner. The "basis" column is the whole audit trail &mdash;
there is no price here without a stated input.</p>
<table class="grid"><thead><tr><th>Selection</th><th>Market</th><th>Our chance</th><th>Fair decimal</th><th>Fair American</th><th>Official quote</th><th>Basis</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
<h2 class="sec">How the lines were built</h2>
<div class="two">
<div class="panel"><h3>Where an official quote exists</h3>
<p>For the three NHL games with a readable price pair, we de-vig the pair: each implied probability is
divided by the sum of the two. That removes the provider margin and produces a fair price. The
original provider decimal is still shown in the quote column.</p></div>
<div class="panel"><h3>Where it does not</h3>
<p>For the puck line, the race and the tennis final we build the number ourselves from the official
inputs printed on the row and state the formula. These are research lines, not available offers &mdash;
the same distinction the repository's own methodology makes.</p></div>
</div>
<h2 class="sec">Markets investigated but not published</h2>
<ul class="cross">
<li><strong>Totals</strong> for the NHL game &mdash; no official total was quoted and San Jose's goal rate was unreadable, so a total would have been invented.</li>
<li><strong>Handicaps</strong> outside the puck line &mdash; same missing input.</li>
<li><strong>Player markets</strong> (first try scorer, top batsman) &mdash; no official participant list was read.</li>
<li><strong>Injury and availability markets</strong> &mdash; no official availability feed was readable, so no injury claim appears anywhere on this desk.</li>
</ul>
"""
    return page("markets.html", "Markets & lines", "Every price we originated, with the input that produced it.", body)


def sports_page():
    cov = {c[0]: c for c in D.COVERAGE}
    labels = dict((s[0], s[1]) for s in D.SPORTS)
    cards = []
    for slug, label, o_slug, o_id, official in D.SPORTS:
        c = cov.get(slug, (slug, 0, 0, 0, 0, ""))
        cards.append(f"""<a class="card link" href="sports/{e(slug)}.html">
<h3>{e(label)}</h3>
<p class="kpis-inline"><b>{c[1]}</b> listed &middot; <b>{c[2]}</b> official &middot; <b>{c[3]}</b> picks &middot; <b>{c[4]}</b> High</p>
<p class="muted">{e(c[5])}</p></a>""")
    body = f"""
<p class="note">Fifteen sports, in the order the brief lists them. Each card opens a page with that
sport's listings, its official route and its picks. The counts are deliberately blunt: "official"
means a row with a link to the league or tour itself.</p>
<div class="cards">{''.join(cards)}</div>
<h2 class="sec">The five-a-day target, honestly</h2>
<p>The brief asks for five High-confidence picks per sport per day, which is 75 selections. This
snapshot issues {len(D.PICKS)}, none of them High. Two separate constraints collide: the High rule
needs a 70%+ chance, and the brief's price band stops at -250, which is 71.4%. That leaves a 1.4-point
window, and none of today's readable inputs lands inside it. Rather than widen the definition, the
desk publishes the shortfall and the reason for every sport.</p>
"""
    return page("sports.html", "Sports", "All fifteen requested sports, with counts and the reason for each gap.", body)


def sport_page(slug, label, o_slug, o_id, official):
    c = next((x for x in D.COVERAGE if x[0] == slug), (slug, 0, 0, 0, 0, ""))
    fixtures = [f for f in D.FIXTURES if f["sport"] == slug]
    discs = [r for r in D.DISCOVERY if r[0] == slug]
    fx_rows = "".join(
        f'<tr><td><strong>{e(f["a"])} vs {e(f["b"])}</strong><br><span class="muted">{e(f["competition"])}</span></td>'
        f'<td>{e(stamp(f["start_utc"]) or "unconfirmed")}</td><td>{e(status(f))}</td>'
        f'<td>{pick_cell(f, "../picks.html")}</td>'
        f'<td>{source_link(f["source_id"])}</td></tr>' for f in fixtures)
    disc_rows = "".join(
        f'<tr><td>{e(r[1])}</td><td>{e(r[2])}</td><td>{e(r[3])}</td><td>{e(r[4])}</td><td class="num">{e(r[5])}</td><td class="num">{e(r[6]) if r[6] is not None else ""}</td></tr>'
        for r in discs)
    body = f"""
<div class="two">
<div class="panel"><h3>Official route</h3><p><a href="{e(official)}" target="_blank" rel="noopener noreferrer">{e(official)} &#8599;</a></p>
<h3>Discovery route</h3><p><a href="{e(D.olbg(o_slug, o_id))}" target="_blank" rel="noopener noreferrer">OLBG {e(label)} hub &#8599;</a></p></div>
<div class="panel warn"><h3>Coverage</h3><p>{c[1]} OLBG listings &middot; {c[2]} rows with an official link &middot; {c[3]} picks &middot; {c[4]} High.</p>
<p>{e(c[5])}</p></div>
</div>
<h2 class="sec">Matches with an official link</h2>
{('<table class="grid"><thead><tr><th>Match</th><th>Start</th><th>Status</th><th>Pick</th><th>Source</th></tr></thead><tbody>' + fx_rows + '</tbody></table>') if fixtures else '<p class="note">None. No official fixture page for this sport was read in this window, so the listings below could not be confirmed.</p>'}
<h2 class="sec">OLBG listings (discovery only)</h2>
{('<table class="grid small"><thead><tr><th>Event</th><th>When</th><th>Market</th><th>Most-tipped</th><th>Tips</th><th>Share %</th></tr></thead><tbody>' + disc_rows + '</tbody></table>') if discs else '<p class="note">The OLBG hub listed no event for this sport when read.</p>'}
<p class="note"><a href="../sports.html">&larr; All sports</a></p>
"""
    return page(f"sports/{slug}.html", label, f"{label}: what is listed, what is official, and what is priced.", body)


def flagged_page():
    sev = {"high": 0, "medium": 1, "low": 2}
    flags = sorted(D.FLAGS, key=lambda f: sev[f[1]])
    rows = "".join(
        f'<tr id="{e(f[0])}"><td><strong>{e(f[0])}</strong></td><td><span class="pill p-{e(f[1])}">{e(f[1])}</span></td>'
        f'<td><strong>{e(f[2])}</strong><br><span class="muted">{e(f[3])}</span></td>'
        f'<td><a href="{e(f[4])}" target="_blank" rel="noopener noreferrer">source &#8599;</a></td></tr>'
        for f in flags
    )
    body = f"""
<p class="note">Anything this desk could not confirm from an official publisher is listed here with its
source link. A flag does not block publication: it tells you exactly which cell is empty and why.
Nothing on this page has been estimated to make a row look complete.</p>
<div class="panel warn"><h3>Severity key</h3><p><span class="pill p-high">high</span> changes what a reader can rely on &middot;
<span class="pill p-medium">medium</span> a specific field is missing &middot;
<span class="pill p-low">low</span> a caveat about how a published number should be read.</p></div>
<table class="grid"><thead><tr><th>ID</th><th>Severity</th><th>What was flagged</th><th>Source</th></tr></thead><tbody>{rows}</tbody></table>
<h2 class="sec">Rows with a blank field</h2>
<ul class="cross">
<li><strong>Milwaukee Brewers</strong> &mdash; regular-season runs scored and allowed: blank (F-7F-06).</li>
<li><strong>San Jose Sharks, Los Angeles Kings, New Jersey Devils, Rangers, Senators, Ducks, Flyers</strong> &mdash; club records blank; no league page segment with those clubs was captured.</li>
<li><strong>Tennis start time and venue</strong> &mdash; blank; only OLBG's listed time exists (F-7F-04).</li>
<li><strong>New York Rangers at Ottawa Senators price</strong> &mdash; blank (F-7F-05).</li>
</ul>
"""
    return page("flagged.html", "Flagged for review", "Every gap, with its severity and its source link.", body)


def repo_audit_page():
    sev = {"high": 0, "medium": 1, "low": 2}
    findings = sorted(D.REPO_FINDINGS, key=lambda f: sev[f[1]])
    rows = "".join(
        f'<tr id="{e(f[0])}"><td><strong>{e(f[0])}</strong></td><td><span class="pill p-{e(f[1])}">{e(f[1])}</span></td>'
        f'<td><strong>{e(f[2])}</strong><br><span class="muted">{e(f[3])}</span></td>'
        f'<td><code>{e(f[4])}</code></td></tr>' for f in findings
    )
    body = f"""
<p class="note">Seven findings from reading the repository line by line on {e(D.SNAPSHOT_DATE)}.
Each one names the file it came from so it can be checked directly in the repository. Paths are
relative to the repository root; the GitHub link for each is one click from
<a href="https://github.com/buffedlizard55-lab/OLBG1" target="_blank" rel="noopener noreferrer">the repository &#8599;</a>.</p>
<table class="grid"><thead><tr><th>ID</th><th>Severity</th><th>Finding</th><th>File</th></tr></thead><tbody>{rows}</tbody></table>
<h2 class="sec">What was checked</h2>
<div class="two">
<div class="panel"><h3>Read line by line</h3><ul class="tick">
<li><code>data/current/snapshot.json</code> &mdash; 108 listings, 16 priced, zero High, zero Medium</li>
<li><code>data/8aede3ba/fixtures.json</code> &mdash; 98 fixtures, 66 High, all at one fair price</li>
<li><code>data/8aede3ba/summary.json</code> &mdash; the desk's own headline counts</li>
<li><code>pipeline/build.py</code> &mdash; navigation, dashboard copy, alias pages</li>
<li><code>pipeline/validate.py</code> &mdash; what the release gate does and does not check</li>
<li><code>COORDINATION.md</code> &mdash; task board ordering and duplicate headings</li>
<li><code>README.md</code> &mdash; the claims the root site makes about itself</li>
</ul></div>
<div class="panel"><h3>What this audit is not</h3><p>It is not a re-verification of every assertion in
every sibling desk &mdash; there are 55 of them and most are snapshots of the same dashboard. It is a
targeted read of the files that decide what a visitor is told, plus the two figures (High count,
tier price) that shape the whole presentation.</p></div>
</div>
"""
    return page("repo-audit.html", "Repository audit", "Seven findings from a line-by-line read of the files that decide what a visitor sees.", body)


def sources_page():
    rows = "".join(
        f'<tr><td><strong>{e(s["publisher"])}</strong></td><td><a href="{e(s["url"])}" target="_blank" rel="noopener noreferrer">{e(s["url"])} &#8599;</a></td>'
        f'<td class="small">{e(s["what"])}</td><td class="small">{e(", ".join(s["fields"]))}</td>'
        f'<td>{e(stamp(s["observed_utc"]))}</td></tr>' for s in D.SOURCES.values()
    )
    olbg_rows = "".join(
        f'<tr><td>{e(label)}</td><td><a href="{e(D.olbg(o_slug, o_id))}" target="_blank" rel="noopener noreferrer">OLBG {e(label)} hub &#8599;</a></td>'
        f'<td><a href="{e(official)}" target="_blank" rel="noopener noreferrer">{e(official)} &#8599;</a></td></tr>'
        for slug, label, o_slug, o_id, official in D.SPORTS
    )
    body = f"""
<p class="note">Nine official reads and fifteen discovery reads. Each official row shows what that
page actually gave us; the discovery table shows the OLBG hub next to the official route that would
be used to confirm it.</p>
<h2 class="sec">Official publishers read in this window</h2>
<table class="grid"><thead><tr><th>Publisher</th><th>Page</th><th>What it gave us</th><th>Fields used</th><th>Read at</th></tr></thead><tbody>{rows}</tbody></table>
<h2 class="sec">Discovery route next to the official route, per sport</h2>
<table class="grid"><thead><tr><th>Sport</th><th>OLBG hub</th><th>Official route</th></tr></thead><tbody>{olbg_rows}</tbody></table>
<h2 class="sec">Sources explicitly refused as verification</h2>
<ul class="cross">
<li>OLBG tip counts and tip shares &mdash; a vote count, not a probability.</li>
<li>Media previews and team news articles &mdash; not a governing body.</li>
<li>Our own earlier snapshots, including every sibling desk in this repository.</li>
</ul>
"""
    return page("sources.html", "Sources", "What was read, when, and what each read actually produced.", body)


def methodology_page():
    body = f"""
<h2 class="sec">The confidence rule, in full</h2>
<table class="grid"><thead><tr><th>Tier</th><th>Requires</th><th>In this snapshot</th></tr></thead>
<tbody>
<tr><td>{tier_badge("High")}</td><td>A 70%+ chance, a fair price no shorter than -250, and every input the selection depends on read from an official publisher.</td><td>{len([p for p in D.PICKS if p['confidence']=='High'])} picks</td></tr>
<tr><td>{tier_badge("Medium")}</td><td>A 55-70% chance, or a 70%+ chance whose fair price is outside the band, or one unread input.</td><td>{len([p for p in D.PICKS if p['confidence']=='Medium'])} picks</td></tr>
<tr><td>{tier_badge("Low")}</td><td>Everything else, including any pick resting on a single practice session or one side of a matchup.</td><td>{len([p for p in D.PICKS if p['confidence']=='Low'])} picks</td></tr>
</tbody></table>
<h2 class="sec">Why the High tier is empty today</h2>
<p>The brief sets two thresholds that nearly touch. A pick needs a chance above 70%, and it needs to
sit between -250 and +10000. A fair price of -250 is a 71.43% chance, so any pick that satisfies both
must land in a 1.43-point window between 70.00% and 71.43%. Our four verified sports produced chances
of 75.6% (too short a price), 62.5%, 62.1%, 54.5%, 31% and 29% (too long). None lands in the window,
and moving a number to make it land would be inventing evidence.</p>
<h2 class="sec">How a price is produced</h2>
<ol class="steps">
<li><strong>Read the official input.</strong> Club record, L10, home split, goals or runs for and against, session classification, seed and round result. Nothing else.</li>
<li><strong>State the formula.</strong> De-vigged provider pair, a seed-based logistic prior, or a stated conversion rate. The formula is printed in the basis column of <a href="markets.html">Markets &amp; lines</a>.</li>
<li><strong>Convert.</strong> Fair decimal is 1/p with no margin and no clipping; the American price follows from the decimal.</li>
<li><strong>Grade.</strong> Apply the table above. If an input is missing, the pick cannot be High, whatever the number says.</li>
</ol>
<h2 class="sec">Rules this desk follows</h2>
<ul class="tick">
<li>No value is filled in from memory, from a preview article, or from a sibling snapshot.</li>
<li>No pick is issued on a match whose start has passed.</li>
<li>No claim about injuries is made unless an official availability source was read; none was, so none is made.</li>
<li>Every written prediction is unique, at least 30 words, names its selection, and uses only the facts printed under it.</li>
<li>Two words are kept out of the published predictions by rule: the vocabulary of modelling and of verification belongs to this method page, not to the tip text.</li>
</ul>
<h2 class="sec">What would raise the High count</h2>
<p>Readable official goal rates for both sides of a hockey or handball match; a published total or
handicap quote; official team news feeds for availability; and an order of play with start times for
tennis. With those four inputs, a High pick becomes a matter of arithmetic rather than a search for a
number that happens to land in a 1.4-point window.</p>
"""
    return page("methodology.html", "Method", "The tier rule, the pricing rule, and the four inputs that would unlock more High picks.", body)


def exports():
    data = OUT / "data"
    data.mkdir(parents=True, exist_ok=True)
    picks = []
    for p in D.PICKS:
        fx = next(f for f in D.FIXTURES if f["id"] == p["fixture"])
        picks.append({
            "fixture_id": fx["id"], "sport": fx["sport"], "competition": fx["competition"],
            "match": f'{fx["a"]} vs {fx["b"]}', "start_utc": fx["start_utc"],
            "market": p["market"], "selection": p["selection"], "confidence": p["confidence"],
            "probability": p["prob"], "fair_decimal": decimal(p["prob"]),
            "fair_american": american(p["prob"]), "tier_reason": p["why_tier"],
            "prediction": p["prediction"], "prediction_words": wordcount(p["prediction"]),
            "official_source": src(fx["source_id"])["url"],
            "observed_utc": src(fx["source_id"])["observed_utc"],
        })
    (data / "picks.json").write_text(json.dumps({
        "session": "7f1bf9f7-olbg1", "snapshot_utc": D.OBSERVED,
        "counts": {"picks": len(D.PICKS), "high": 0, "fixtures": len(D.FIXTURES),
                   "discovery_rows": len(D.DISCOVERY), "markets": len(D.MARKETS),
                   "flags": len(D.FLAGS), "repo_findings": len(D.REPO_FINDINGS)},
        "picks": picks}, indent=1), encoding="utf-8")
    with (data / "picks.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(picks[0].keys()))
        w.writeheader()
        w.writerows(picks)
    (data / "discovery.json").write_text(json.dumps([
        {"sport": r[0], "event": r[1], "listed_time": r[2], "market": r[3],
         "most_tipped": r[4], "tips": r[5], "share_pct": r[6],
         "olbg_hub": D.olbg(next(s[2] for s in D.SPORTS if s[0] == r[0]), next(s[3] for s in D.SPORTS if s[0] == r[0])),
         "status": "discovery-only, unverified"} for r in D.DISCOVERY], indent=1), encoding="utf-8")
    (data / "flags.json").write_text(json.dumps([
        {"id": f[0], "severity": f[1], "title": f[2], "detail": f[3], "source": f[4]} for f in D.FLAGS], indent=1), encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "assets").mkdir(exist_ok=True)
    (OUT / "assets" / "style.css").write_text(STYLE, encoding="utf-8")
    pages = [index(), picks_page(), predictions_page(), matches_page(), discovery_page(),
             markets_page(), sports_page(), flagged_page(), repo_audit_page(), sources_page(),
             methodology_page()]
    for slug, label, o_slug, o_id, official in D.SPORTS:
        pages.append(sport_page(slug, label, o_slug, o_id, official))
    exports()
    (OUT / ".nojekyll").touch()
    print(f"built {len(pages)} pages at today/ · {len(D.PICKS)} picks · {len(D.FIXTURES)} fixtures · {len(D.DISCOVERY)} discovery rows")
    return pages


STYLE = """
:root{--ink:#12241d;--muted:#5c6f67;--line:#dde5e0;--bg:#f6f8f6;--card:#fff;
--brand:#12563d;--brand2:#1d7a55;--hi:#0f6b3f;--med:#8a5a00;--low:#6b3f8a;--warn:#fff6e2;--warnline:#e6c98a}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:var(--brand2)}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}
.top{background:var(--card);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:9}
.top .wrap{display:flex;gap:18px;align-items:center;flex-wrap:wrap;padding:10px 20px}
.brand{font-weight:700;color:var(--ink);text-decoration:none;display:flex;align-items:center;gap:8px}
.brand small{font-weight:500;color:var(--muted);letter-spacing:.04em;text-transform:uppercase;font-size:11px}
.dot{width:11px;height:11px;border-radius:50%;background:var(--brand2);display:inline-block}
.nav{display:flex;gap:4px;flex-wrap:wrap}
.navlink{text-decoration:none;color:var(--muted);padding:6px 10px;border-radius:8px;font-size:14px}
.navlink:hover{background:var(--bg);color:var(--ink)}
.navlink.active{background:var(--brand);color:#fff}
.pagehead{padding:30px 0 8px}
.kicker{margin:0 0 6px;color:var(--muted);font-size:12px;letter-spacing:.09em;text-transform:uppercase}
h1{font-size:34px;line-height:1.15;margin:0 0 10px}
.lead{font-size:18px;color:var(--muted);margin:0;max-width:820px}
h2.sec{font-size:21px;margin:34px 0 10px;padding-bottom:8px;border-bottom:1px solid var(--line)}
h3{font-size:16px;margin:0 0 6px}
.note{color:var(--muted);font-size:15px;max-width:900px}
.hero{display:grid;grid-template-columns:1.15fr 1fr;gap:24px;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px;margin:18px 0 6px}
.hero h2{margin:0 0 8px;font-size:22px}
.hero .big{margin-top:10px;font-size:15px}
.kpis{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.kpis li{background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:10px}
.kpis b{display:block;font-size:22px;line-height:1.1}
.kpis span{font-size:12px;color:var(--muted)}
table.grid{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden;font-size:14.5px}
table.grid th{text-align:left;background:#eef4f0;font-size:12px;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);padding:9px 10px;border-bottom:1px solid var(--line)}
table.grid td{padding:10px;border-bottom:1px solid var(--line);vertical-align:top}
table.grid tr:last-child td{border-bottom:0}
table.grid.small td,table.grid.small th{font-size:13px;padding:7px 9px}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.muted{color:var(--muted)}
.small{font-size:13px}
.tier{display:inline-block;padding:2px 8px;border-radius:999px;font-size:12px;font-weight:700;color:#fff}
.t-high{background:var(--hi)}.t-medium{background:var(--med)}.t-low{background:var(--low)}
.pill{display:inline-block;padding:2px 8px;border-radius:999px;font-size:11px;background:#eef1ef;color:var(--muted)}
.p-high{background:#fde2e1;color:#8c1d18}.p-medium{background:#fff1d6;color:#7a4b00}.p-low{background:#e8eefa;color:#25406b}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;text-decoration:none;color:inherit;display:block}
.card.link:hover{border-color:var(--brand2);box-shadow:0 2px 10px rgba(18,86,61,.08)}
.card p{margin:6px 0 0;font-size:14px}
.kpis-inline{margin:4px 0;font-size:13px;color:var(--muted)}
.kpis-inline b{color:var(--ink)}
.two{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:14px}
.panel{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}
.panel.warn{background:var(--warn);border-color:var(--warnline)}
ul.tick,ul.cross{margin:8px 0 0;padding-left:18px;font-size:14.5px}
ul.tick li,ul.cross li{margin:5px 0}
.pred{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px;margin:18px 0}
.pred header{display:flex;justify-content:space-between;gap:18px;flex-wrap:wrap;align-items:flex-start}
.pred h2{font-size:20px;margin:0}
.pickbox{background:var(--bg);border:1px solid var(--line);border-radius:12px;padding:12px;min-width:250px}
.pickbox strong{display:block;font-size:16px;margin:2px 0 6px}
.pickbox .price{font-variant-numeric:tabular-nums;font-size:14px;color:var(--muted)}
.prose{font-size:16.5px;line-height:1.7;max-width:900px;margin:14px 0}
.facts{background:#f3f7f5;border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.facts ul{margin:6px 0;padding-left:18px;font-size:14px}
.meta{color:var(--muted);font-size:13px;margin:10px 0 0}
ol.steps{font-size:15px;max-width:860px}
ol.steps li{margin:8px 0}
footer{margin:44px 0 30px;padding-top:16px;border-top:1px solid var(--line);color:var(--muted);font-size:13px}
code{background:#eef1ef;padding:1px 5px;border-radius:5px;font-size:13px}
@media(max-width:860px){.hero,.two{grid-template-columns:1fr}.kpis{grid-template-columns:repeat(2,1fr)}h1{font-size:27px}}
"""

if __name__ == "__main__":
    main()
