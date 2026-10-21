#!/usr/bin/env python3
"""
build_site.py - render the static dashboard into docs/ (GitHub Pages source).

Inputs : data/fixtures.json, data/lines.json, data/predictions.json,
         data/olbg_taxonomy.json, data/sources.json, data/coverage.json
Outputs: docs/**.html, docs/assets/*, docs/data/*.json
"""
from __future__ import annotations

import html
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT                 # Pages is configured to serve main:/ so the site root is the repo root
ASSETS = OUT / "assets"

SITE_NAME = "OLBG Reverse-Engineering"
SITE_TAG = "Originated lines · verified fixtures · confidence tiers"

CONF_LABEL = {"high": "High", "medium": "Medium", "low": "Low"}
STATUS_LABEL = {"verified": "Verified", "cross-checked": "Cross-checked", "unverified": "Unverified"}


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def e(x) -> str:
    return html.escape(str(x if x is not None else ""))


def load():
    def read(p):
        return json.loads((ROOT / p).read_text())
    return {
        "fixtures": read("data/fixtures.json"),
        "lines": read("data/lines.json"),
        "preds": read("data/predictions.json"),
        "taxonomy": read("data/olbg_taxonomy.json"),
        "sources": read("data/sources.json"),
        "coverage": read("data/coverage.json"),
    }


def when(m: dict) -> str:
    if m.get("start_utc"):
        dt = datetime.fromisoformat(m["start_utc"].replace("Z", "+00:00"))
        return dt.strftime("%d %b %H:%M UTC")
    if m.get("date_local"):
        t = m.get("time_as_shown")
        d = datetime.strptime(m["date_local"], "%Y-%m-%d").strftime("%d %b")
        return f"{d}{' · ' + t if t else ''}"
    return "—"


def match_name(m: dict) -> str:
    if m.get("away"):
        return f"{m['home']} v {m['away']}"
    return m["home"]


def conf_badge(c: str) -> str:
    return f'<span class="badge {c}">{CONF_LABEL.get(c, c)}</span>'


def status_badge(s: str) -> str:
    cls = {"verified": "verified", "cross-checked": "cross", "unverified": "cross"}.get(s, "muted")
    return f'<span class="badge {cls}">{STATUS_LABEL.get(s, s)}</span>'


def source_links(m: dict, limit: int = 3) -> str:
    out = []
    for s in m.get("sources", [])[:limit]:
        out.append(f'<a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["name"])}</a>')
    for s in m.get("external_checks", [])[:1]:
        out.append(f'<a href="{e(s["url"])}" target="_blank" rel="noopener">[check] {e(s["name"])}</a>')
    return '<div class="src-links">' + "".join(out) + "</div>"


def market_html(p: dict) -> str:
    parts = ['<details class="markets"><summary>All originated markets</summary>']
    for mk in p["markets"]:
        line = f' · line {mk["line"]}' if mk.get("line") else ""
        parts.append(f'<div class="mkt"><div class="mkt-h"><span>{e(mk["name"])}{e(line)}</span></div><ul>')
        for o in mk["outcomes"]:
            parts.append(
                f'<li><span>{e(o["selection"])}</span>'
                f'<span><b class="odds">{o["odds"]:.2f}</b> '
                f'<span class="sub" style="display:inline">({o["implied_pct"]}%)</span></span></li>'
            )
        parts.append("</ul>")
        if mk.get("alternate"):
            alt = " / ".join(f'{o["selection"]} {o["odds"]:.2f}' for o in mk["alternate"])
            parts.append(f'<div class="basis">Alternate line: {e(alt)}</div>')
        parts.append(f'<div class="basis">{e(mk["basis"])}</div></div>')
    parts.append("</details>")
    return "".join(parts)


def pick_table(rows, show_sport: bool, table_id: str = "") -> str:
    head = ["When", "Match", "Competition", "Our line (H / D / A)", "Selection", "Conf.", "Verified from"]
    if show_sport:
        head.insert(2, "Sport")
    th = "".join(f"<th>{h}</th>" for h in head)
    body = []
    for m, p in rows:
        winner = p["markets"][0]["outcomes"]
        od = " / ".join(f'{o["odds"]:.2f}' for o in winner)
        sport = p["sport_name"]
        cells = [
            f'<td style="white-space:nowrap">{e(when(m))}</td>',
            f'<td><span class="match-name">{e(match_name(m))}</span>'
            f'<span class="sub">{e(m.get("venue",""))}</span></td>',
        ]
        if show_sport:
            cells.append(f'<td><a href="sports/{e(m["sport"])}.html">{e(sport)}</a></td>')
        cells += [
            f'<td>{e(m.get("competition",""))}<span class="sub">{e(m.get("stage",""))}</span></td>',
            f'<td class="odds">{e(od)}</td>',
            f'<td><b>{e(p["pick"])}</b><span class="sub">{e(p["pick_market"])} @ '
            f'{next((o["odds"] for o in winner if o["selection"] == p["pick"]), "")}</span>{market_html(p)}</td>',
            f'<td>{conf_badge(p["confidence"])}<span class="sub">{status_badge(m["status"])}</span></td>',
            f'<td>{source_links(m)}</td>',
        ]
        body.append(f'<tr data-conf="{p["confidence"]}">' + "".join(cells) + "</tr>")
    return (f'<div class="table-wrap"><table id="{table_id}"><thead><tr>{th}</tr></thead>'
            f'<tbody>{"".join(body)}</tbody></table></div>')


def shell(title: str, body: str, active: str, depth: int = 0, base: str = "") -> str:
    r = base if base else "../" * depth
    nav = [
        ("index.html", "Dashboard", "dash"),
        ("picks.html", "Picks", "picks"),
        ("predictions.html", "Predictions", "preds"),
        ("sports.html", "Sports", "sports"),
        ("methodology.html", "Methodology", "method"),
        ("reverse-engineering.html", "OLBG analysis", "rev"),
        ("sources.html", "Sources", "src"),
        ("flagged.html", "Flagged", "flag"),
    ]
    anchor = ' aria-current="page"'
    links = "".join(
        '<a href="{r}{href}"{cur}>{label}</a>'.format(
            r=r, href=href, cur=(anchor if key == active else ""), label=label)
        for href, label, key in nav
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} · {e(SITE_NAME)}</title>
<meta name="description" content="Independent reverse-engineering of OLBG: verified fixtures across 17 in-scope sports, originated betting lines, confidence tiers and written predictions.">
<link rel="stylesheet" href="{r}assets/style.css">
</head>
<body>
<header class="site-header">
  <div class="hdr-inner">
    <div class="brand"><span class="dot"></span> OLBG <span class="sub">reverse-engineered</span></div>
    <nav class="main">{links}</nav>
  </div>
</header>
<main>
{body}
</main>
<footer class="foot">
  <p><b>{e(SITE_NAME)}</b> — {e(SITE_TAG)}. Window covered: 21–27 October 2026.
  Every fixture links to the governing body it was read from. Model prices are our own
  estimates, not market prices. Nothing here is betting advice.</p>
  <p><a href="{r}methodology.html">Methodology</a> · <a href="{r}sources.html">Source register</a> ·
  <a href="{r}flagged.html">Flagged for review</a> · <a href="{r}data/fixtures.json">Raw JSON</a></p>
</footer>
<script src="{r}assets/app.js"></script>
</body>
</html>
"""


def kpi(n, label, cls="") -> str:
    return f'<div class="kpi {cls}"><div class="n">{e(n)}</div><div class="l">{e(label)}</div></div>'


# --------------------------------------------------------------------------
# pages
# --------------------------------------------------------------------------
def build_index(D, rows, stats) -> str:
    flagged = sum(1 for m, _ in rows if m.get("flags"))
    sport_cards = []
    for sp in sorted(D["coverage"]["sports"].items(), key=lambda kv: -stats["by_sport"].get(kv[0], 0)):
        slug, cov = sp
        n = stats["by_sport"].get(slug, 0)
        name = next((v["name"] for v in D["model_sports"] if v["slug"] == slug), slug)
        badge = {
            "covered": '<span class="badge verified">Covered</span>',
            "partial": '<span class="badge cross">Partial</span>',
            "event-only": '<span class="badge event">Event only</span>',
            "no-fixtures": '<span class="badge muted">No fixtures</span>',
            "not-investigated": '<span class="badge cross">Not investigated</span>',
        }[cov["status"]]
        sport_cards.append(
            f'<a class="sport-card" href="sports/{e(slug)}.html"><div class="t"><span>{e(name)}</span>{badge}</div>'
            f'<div class="m">{n} priced match{"es" if n != 1 else ""}</div></a>'
        )

    top = sorted(rows, key=lambda r: (-{"high": 3, "medium": 2, "low": 1}[r[1]["confidence"]],
                                      r[0].get("start_utc") or "9999"))[:10]

    body = f"""
<h1>Every in-scope sport, every fixture we could verify.</h1>
<p class="lede">This is an independent reverse-engineering of OLBG's sport taxonomy and match coverage, combined with
our own originated betting lines. Fixtures come from governing-body sources only. Where a value could not be confirmed
on an official page it is left blank and flagged — never filled in.</p>

<div class="grid kpis">
  {kpi(stats['matches'], 'Matches priced')}
  {kpi(stats['sports_covered'], 'Sports in scope')}
  {kpi(stats['high'], 'High confidence', 'hi')}
  {kpi(stats['medium'], 'Medium confidence', 'md')}
  {kpi(stats['low'], 'Low confidence', 'lo')}
  {kpi(stats['sources_verified'], 'Official sources')}
</div>

<div class="note">
  <b>Read the confidence tiers literally.</b> A pick is only rated <b>high</b> when <em>both</em> sides carry a sourced
  strength input — an official league record, an official world ranking, or a sourced “outside the published top 36”
  bound. {stats['both_rated']} of {stats['matches']} matches clear that bar, and {stats['both_measured']} of those
  measure both participants outright. The other {stats['baseline_only']} have no usable strength input at all: they are
  priced from the sport's neutral home baseline and capped at low confidence, and every such row says so. Two of the
  eight high picks lean on the published top-36 snooker bound rather than a measured rank — both are listed on the
  Flagged page for review.
</div>

<h2>Highest-conviction card</h2>
{pick_table(top, show_sport=True)}

<h2>Sports</h2>
<p class="lede">All 17 sports that survive the brief's exclusions. “Not investigated” means exactly that — no official
fixture source was retrieved in this build, and the page says so rather than inventing a schedule.</p>
<div class="grid sports-grid">{''.join(sport_cards)}</div>

<h2>What the data says</h2>
<div class="two-col">
  <div class="card">
    <h3>Two thirds of the card has no real edge</h3>
    <p>{stats['both_rated']} of {stats['matches']} fixtures carry a sourced strength input on both sides; only
    {stats['both_measured']} measure both participants outright. Everything
    else is a baseline price. Publishing a confident pick off a 0–0 NBA record or an unretrievable PDC Order of Merit
    would be fabrication dressed up as analysis, so those rows are labelled low and left honest.</p>
  </div>
  <div class="card">
    <h3>Where our model disagrees with OLBG's crowd</h3>
    <p>OLBG's front page carried one in-scope pick for these fixtures: <b>Washington Wizards money line</b> against
    Milwaukee, with 9 of 11 tips (82%) behind it. Our model also makes Washington the home favourite — but only at
    <b>56%</b>. Same side, wildly different conviction. That gap is the thing worth studying, not the pick.</p>
  </div>
  <div class="card">
    <h3>Fatigue, not form, decides Game 2</h3>
    <p>Milwaukee closed out the Dodgers on 14 October and had nine days to set a rotation. Tampa Bay needed six games
    and a postponement to get past Cleveland, finishing on 19 October. The official postseason log makes that gap
    checkable rather than anecdotal.</p>
  </div>
  <div class="card">
    <h3>Nine sports are a genuine coverage gap</h3>
    <p>Gaelic football has a <em>verified negative</em> — the GAA calendar shows nothing between 21 and 25 October. The
    other gaps (rugby league, handball, volleyball, tennis, AFL, esports, greyhounds) are unfilled because no official
    source was retrieved, not because nothing is scheduled. They are listed on the Flagged page.</p>
  </div>
</div>

<h2>Start here</h2>
<ul class="clean">
  <li><a href="picks.html">All picks</a> — filter by confidence, open any row for every originated market.</li>
  <li><a href="predictions.html">Written predictions</a> — one bespoke 30+ word write-up per high-confidence selection.</li>
  <li><a href="reverse-engineering.html">OLBG analysis</a> — all 22 sport IDs, URL patterns and coverage comparison.</li>
  <li><a href="flagged.html">Flagged for review</a> — every unverified value, every gap, every judgement call.</li>
</ul>
"""
    return shell("Dashboard", body, "dash")


def build_picks(D, rows) -> str:
    all_rows = sorted(rows, key=lambda r: ({"high": 0, "medium": 1, "low": 2}[r[1]["confidence"]],
                                           r[0].get("start_utc") or r[0].get("date_local") or ""))
    body = f"""
<div class="crumb">Dashboard / Picks</div>
<h1>All originated picks</h1>
<p class="lede">Every priced match in the 21–27 October window. The H / D / A column is our opening line with the
model's 5% overround applied. Open “All originated markets” on any row for the handicap and match-total lines.</p>

<div class="strip">
  <button class="chip" data-filter="all" aria-pressed="true">All <b>{len(all_rows)}</b></button>
  <button class="chip" data-filter="high" aria-pressed="false">High</button>
  <button class="chip" data-filter="medium" aria-pressed="false">Medium</button>
  <button class="chip" data-filter="low" aria-pressed="false">Low</button>
  <input id="pick-search" type="search" placeholder="Search team, player or competition…"
         style="flex:1;min-width:220px;padding:8px 12px;border:1px solid var(--line);border-radius:8px;font-size:.86rem">
  <a href="#" id="open-all" class="chip">Expand all markets</a>
</div>

{pick_table(all_rows, show_sport=True, table_id='picks')}
<p class="sub">Showing <b data-visible-count>{len(all_rows)}</b> rows.</p>
"""
    return shell("Picks", body, "picks")


def build_predictions(D, rows, preds) -> str:
    by_id = {p["id"]: p for _, p in rows}
    cards = []
    for it in preds["items"]:
        p = by_id.get(it["match_id"], {})
        m = next((x for x, _ in rows if x["id"] == it["match_id"]), {})
        odds = ""
        for o in p.get("markets", [{}])[0].get("outcomes", []):
            if o["selection"] == it["selection"]:
                odds = f'{o["odds"]:.2f}'
        facts = "".join(f"<li>{e(f)}</li>" for f in it["facts"])
        srcs = " ".join(f'<a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["name"])}</a>'
                        for s in it["sources"])
        cards.append(f"""
<article class="pred">
  <h3>{e(match_name(m))}</h3>
  <div class="meta">{e(m.get("competition",""))} · {e(when(m))} · {e(m.get("venue",""))}</div>
  <p><span class="badge high">High confidence</span> <b>{e(it["selection"])}</b>
     <span class="sub" style="display:inline">— {e(it["market"])} @ {e(odds)}</span></p>
  <p>{e(it["text"])}</p>
  <ul class="facts">{facts}</ul>
  <div class="src-links" style="margin-top:9px">{srcs}</div>
</article>""")
    word_counts = [len(it["text"].split()) for it in preds["items"]]
    body = f"""
<div class="crumb">Dashboard / Predictions</div>
<h1>Written predictions — high-confidence selections only</h1>
<p class="lede">One bespoke write-up per high-confidence pick. Each states the selection outright, is built only from
facts that were read on an official source, and runs to at least 30 words. Nothing here is templated: the arguments
differ by match, and where the case is thin the prediction says so.</p>

<div class="strip">
  <span class="chip">{len(preds['items'])} predictions</span>
  <span class="chip">Shortest <b>{min(word_counts)}</b> words</span>
  <span class="chip">Longest <b>{max(word_counts)}</b> words</span>
  <span class="chip">0 templates</span>
</div>

{''.join(cards)}

<div class="note warn">
  <b>Why only {len(preds['items'])}?</b> Because only {len(preds['items'])} selections cleared the confidence bar.
  Writing 40 confident-sounding previews when 42 of 50 matches have no strength input would be the exact thing this
  project is meant to avoid. The other matches are priced and labelled low on the <a href="picks.html">Picks</a> page.
</div>
"""
    return shell("Predictions", body, "preds")


def build_sports_index(D, stats) -> str:
    cards = []
    for sp in D["model_sports"]:
        slug = sp["slug"]
        cov = D["coverage"]["sports"].get(slug, {"status": "not-investigated", "detail": ""})
        n = stats["by_sport"].get(slug, 0)
        label = {"covered": "Covered", "partial": "Partial", "event-only": "Event only",
                 "no-fixtures": "No fixtures", "not-investigated": "Not investigated"}[cov["status"]]
        cls = {"covered": "verified", "partial": "cross", "event-only": "event",
               "no-fixtures": "muted", "not-investigated": "cross"}[cov["status"]]
        cards.append(
            f'<a class="sport-card" href="sports/{e(slug)}.html">'
            f'<div class="t"><span>{e(sp["name"])}</span><span class="badge {cls}">{label}</span></div>'
            f'<div class="m">{n} priced match{"es" if n != 1 else ""} · OLBG ID {e(sp.get("id","—"))}</div></a>'
        )
    body = f"""
<div class="crumb">Dashboard / Sports</div>
<h1>The 17 in-scope sports</h1>
<p class="lede">OLBG lists 22 sports in its betting-tips sitemap. After applying the brief's exclusions — football,
boxing, UFC/MMA, American football, hurling, horse racing, cycling and specials — 17 remain. Each has its own page.</p>
<div class="grid sports-grid">{''.join(cards)}</div>
<div class="note">
  <b>On status words.</b> <em>Covered</em> means fixtures were read from the governing body.
  <em>Partial</em> means the governing body's page did not render, so rows are cross-checked only.
  <em>Event only</em> means the event is verified but has no two-sided fixture to price.
  <em>No fixtures</em> is a verified negative. <em>Not investigated</em> is an honest gap.
</div>
"""
    return shell("Sports", body, "sports")


def build_sport_page(D, slug, sport, rows, stats) -> str:
    cov = D["coverage"]["sports"].get(slug, {"status": "not-investigated", "detail": ""})
    srows = [r for r in rows if r[0]["sport"] == slug]
    label = {"covered": "Covered", "partial": "Partial", "event-only": "Event only",
             "no-fixtures": "No fixtures", "not-investigated": "Not investigated"}[cov["status"]]
    cls = {"covered": "verified", "partial": "cross", "event-only": "event",
           "no-fixtures": "muted", "not-investigated": "cross"}[cov["status"]]
    pending = [m for m in D["fixtures"]["matches"]
               if m["sport"] == slug and not m.get("away")]
    if srows:
        conf = {c: sum(1 for _, p in srows if p["confidence"] == c) for c in ("high", "medium", "low")}
        table = pick_table(srows, show_sport=False)
        summary = (f'<div class="strip"><span class="chip">{len(srows)} matches</span>'
                   f'<span class="chip">High <b>{conf["high"]}</b></span>'
                   f'<span class="chip">Medium <b>{conf["medium"]}</b></span>'
                   f'<span class="chip">Low <b>{conf["low"]}</b></span></div>')
    else:
        table = ('<div class="note warn">No priced row is published for this sport in the current window. '
                 'The reason is stated above rather than filled with an invented schedule.</div>')
        summary = ""
    pending_html = ""
    if pending:
        prs = "".join(
            '<tr><td><b>{n}</b></td><td>{d}</td><td>{v}</td><td>{src}</td></tr>'.format(
                n=e(m["home"]), d=e(m.get("stage", "")), v=e(m.get("venue", "")),
                src=source_links(m, 2))
            for m in pending)
        pending_html = ('<h2>Verified event, no priced line</h2>'
                        '<p class="lede">This is a championship round rather than a two-sided fixture, and no '
                        'official entry list was verified in this build. The event is confirmed; it is not priced.</p>'
                        f'<div class="table-wrap"><table><thead><tr><th>Event</th><th>Round</th><th>Venue</th>'
                        f'<th>Source</th></tr></thead><tbody>{prs}</tbody></table></div>')
    body = f"""
<div class="crumb">Dashboard / Sports / {e(sport['name'])}</div>
<h1>{e(sport['name'])} <span class="badge {cls}" style="vertical-align:8px">{label}</span></h1>
<p class="lede">{e(cov['detail'])}</p>
<p class="sub">OLBG sport ID <b>{e(sport.get('id','—'))}</b> ·
OLBG page <a href="https://www.olbg.com/betting-tips/{e(sport.get('olbg_slug',sport['slug']))}/{e(sport.get('id',''))}"
target="_blank" rel="noopener">/betting-tips/{e(sport.get('olbg_slug',sport['slug']))}/{e(sport.get('id',''))}</a></p>
{summary}
{table}
{pending_html}
"""
    return shell(sport["name"], body, "sports", depth=1)


def build_methodology(D, stats) -> str:
    model_rows = "".join(
        "<tr><td>{n}</td><td class='num'>{pb:.2f}</td><td class='num'>{sc:.0f}</td>"
        "<td class='num'>{sg:.1f}</td><td class='num'>{tot}</td><td class='num'>{hi:.2f}</td></tr>".format(
            n=e(c["name"]), pb=c["p_base"], sc=c["scale"], sg=c["sigma"],
            tot=(c["total"] if c["total"] is not None else "—"), hi=c["high"])
        for c in D["model_config"]
    )
    high_bars = ", ".join(
        "{0} {1:.2f}".format(c["name"], c["high"])
        for c in D["model_config"] if c["name"] in ("Baseball", "Snooker", "Ice Hockey")
    )
    body = f"""
<div class="crumb">Dashboard / Methodology</div>
<h1>Methodology</h1>
<p class="lede">Everything on this site is either a sourced fact or a labelled assumption. This page separates the two
so you can audit the output without trusting the author.</p>

<h2>1. What counts as a source</h2>
<p>Only the governing body of the competition: the league's own API or site, the tour, the promoter, the federation.
Betting sites, tipster aggregators, Wikipedia and news outlets are never used to confirm a fixture, a record or a
ranking. Every row in every table links to the official page it was read from. The full register is on the
<a href="sources.html">Sources</a> page.</p>

<h2>2. Three verification states</h2>
<table>
<thead><tr><th>State</th><th>Meaning</th></tr></thead>
<tbody>
<tr><td>{status_badge('verified')}</td><td>The value was read directly on an official page or official JSON endpoint.</td></tr>
<tr><td>{status_badge('cross-checked')}</td><td>The official page exists but did not render or publish the value. The row is
corroborated by the competition's official broadcaster and is listed on <a href="flagged.html">Flagged for review</a>.</td></tr>
<tr><td>{status_badge('unverified')}</td><td>Not confirmed on any official source. Published as blank plus a flag — never
as an inferred value.</td></tr>
</tbody></table>

<h2>3. How the lines are originated</h2>
<p>Each match is priced with a Bradley–Terry style model in log-odds space:</p>
<pre style="background:#0f172a;color:#e2e8f0;padding:14px 16px;border-radius:10px;overflow:auto;font-size:.85rem">
logit(p_home) = logit(base_home) + (rating_home − rating_away) / scale
odds(S)       = 1 / (p(S) × 1.05)        # 5% overround
handicap line = sigma × Φ⁻¹(p_home)      # expected margin, rounded to the nearest half
total line    = league baseline          # no match-specific scoring input is sourced
</pre>
<p><b>Ratings are only used when both sides have one.</b> If a single participant is missing a sourced rating, the
model refuses to carry a one-sided edge — using a real rating against a placeholder produces nonsense — and charges
the sport's neutral home baseline instead. That is why the confidence split looks the way it does.</p>

<h3>Rating inputs actually used</h3>
<ul class="clean">
  <li><b>Baseball</b> — each side's official 2026 home/road win percentage (MLB StatsAPI), scaled to 0–100.</li>
  <li><b>Snooker</b> — official WST world-ranking position, mapped by <code>100 − 70·ln(rank)/ln(60)</code>. Players
  outside the published top 36 are placed in a single bounded bucket at rank 60. That is a documented bound, not a
  measurement, and it is flagged on every affected row.</li>
  <li><b>Ice hockey</b> — team points percentage where captured. Only Boston carries one in this build, so all four NHL
  matches fall back to baseline.</li>
  <li><b>Basketball, darts, cricket, rugby union</b> — no rating source retrieved, so baseline only.</li>
</ul>

<h3>Model assumptions (not facts)</h3>
<p>These are choices the model makes. They are listed here so nobody mistakes them for statistics.</p>
<table>
<thead><tr><th>Sport</th><th>Neutral home prob.</th><th>Log-odds scale</th><th>Margin σ</th><th>Baseline total</th><th>High bar</th></tr></thead>
<tbody>
{model_rows}
</tbody></table>

<h2>4. Confidence tiers</h2>
<table>
<thead><tr><th>Tier</th><th>Rule</th></tr></thead>
<tbody>
<tr><td>{conf_badge('high')}</td><td>Both sides carry a sourced rating <em>and</em> the model probability clears the
sport's high bar — {high_bars}. High is <em>relative to the sport's own variance</em>: a 59% baseball favourite
is a bigger edge than a 59% basketball favourite.</td></tr>
<tr><td>{conf_badge('medium')}</td><td>Both sides rated but below the high bar.</td></tr>
<tr><td>{conf_badge('low')}</td><td>At least one side unrated. Capped at low regardless of what the baseline implies.</td></tr>
</tbody></table>
<p>Current distribution: <b>{stats['high']}</b> high · <b>{stats['medium']}</b> medium · <b>{stats['low']}</b> low,
across {stats['matches']} matches.</p>

<h2>5. What is deliberately missing</h2>
<ul class="clean">
  <li>No match-total line is originated for snooker or darts: the governing body's match format was not verified, and a
  total-frames or total-legs line would rest on an assumption about format rather than a fact.</li>
  <li>No correct-score, first-scorer or player-prop markets. There is no sourced input for them.</li>
  <li>No injury, team-news or lineup data. Not retrieved means not claimed.</li>
  <li>No in-play pricing. Everything here is a pre-match opening line.</li>
</ul>
"""
    return shell("Methodology", body, "method")


def build_reverse(D) -> str:
    tax = D["taxonomy"]
    IN = '<span class="badge verified">In scope</span>'
    OUTS = '<span class="badge muted">Excluded</span>'
    rows = "".join(
        "<tr><td>{n}</td><td class='num'>{i}</td><td><code>/betting-tips/{sl}/{i}</code></td>"
        "<td>{st}</td><td>{why}</td></tr>".format(
            n=e(s_["name"]), i=e(s_["id"]), sl=e(s_["slug"]),
            st=(IN if s_["in_scope"] else OUTS),
            why=e(s_.get("exclusion_reason", "")))
        for s_ in tax["sports"]
    )
    ex = tax["sports"]
    body = f"""
<div class="crumb">Dashboard / OLBG analysis</div>
<h1>Reverse-engineering OLBG</h1>
<p class="lede">OLBG's betting-tips hierarchy is exposed cleanly in its XML sitemap. This is the full map, extracted
from <a href="{e(tax['source'])}" target="_blank" rel="noopener">sitemap-betting-tips.xml</a> — not guessed from the
navigation, which is incomplete.</p>

<h2>1. URL grammar</h2>
<pre style="background:#0f172a;color:#e2e8f0;padding:14px 16px;border-radius:10px;overflow:auto;font-size:.85rem">
Sport landing page : https://www.olbg.com/betting-tips/{{Sport_Name}}/{{sport_id}}
Competition page   : https://www.olbg.com/betting-tips/{{Sport}}/{{Region}}/{{Competition}}/{{sport_id}}
Event page         : https://www.olbg.com/betting-tips/{{Sport}}/…/{{Home}}_v_{{Away}}/{{sport_id}}?event_id={{id}}
Tipster league     : https://www.olbg.com/best-tipsters/{{Sport}}/{{sport_id}}
</pre>
<p>The trailing digit is always the sport ID, which makes the whole tree crawlable from a single page per sport.
Event slugs use an underscore-joined <code>Home_v_Away</code> pattern with a numeric <code>event_id</code>.</p>

<h2>2. All 22 sports and their IDs</h2>
<div class="table-wrap"><table>
<thead><tr><th>Sport</th><th class="num">ID</th><th>Canonical path</th><th>Status</th><th>Why</th></tr></thead>
<tbody>{rows}</tbody></table></div>

<h2>3. What the sitemap does not tell you</h2>
<ul class="clean">
  <li><b>Hurling has no ID.</b> Gaelic games are split as “Gaelic Football” (25) with hurling folded into the wider
  Gaelic-sports hub. Anyone scraping by numeric ID will miss hurling entirely.</li>
  <li><b>UFC/MMA is not a sport here.</b> Those markets are filed under Boxing (16).</li>
  <li><b>Specials have no betting-tips page at all.</b> They exist only in the blog taxonomy — TV, politics and awards
  markets are not part of the tips tree.</li>
  <li><b>Greyhounds (28) is inconsistent.</b> It appears in the sitemap and the tipster competition, but is absent from
  the <code>/sitemap</code> navigation block.</li>
</ul>

<h2>4. Market vocabulary OLBG actually uses</h2>
<p>Read off live event pages during this build. The naming matters if you are mapping to a bookmaker feed:</p>
<table>
<thead><tr><th>OLBG label</th><th>Standard name</th><th>Seen on</th></tr></thead>
<tbody>
<tr><td>Full Time Result</td><td>3-way match winner</td><td>Football event pages</td></tr>
<tr><td>Money Line</td><td>2-way match winner (incl. OT)</td><td>NBA event pages</td></tr>
<tr><td>Win Match</td><td>2-way match winner</td><td>Cricket, tennis, snooker</td></tr>
<tr><td>Outright Winner</td><td>Futures / tournament winner</td><td>Cricket series, Big Bash, World Cup</td></tr>
<tr><td>+1.50 / −1.50 style</td><td>Handicap / spread</td><td>Gaelic football event page</td></tr>
<tr><td>Daily Racing</td><td>Per-race selection</td><td>Horse racing (excluded)</td></tr>
</tbody></table>

<h2>5. Coverage comparison — OLBG vs this dataset</h2>
<p>What OLBG had listed for the 21–25 October window versus what could actually be verified against a governing body.</p>
<table>
<thead><tr><th>Sport</th><th>OLBG listing observed</th><th>Our verification</th><th>Result</th></tr></thead>
<tbody>
<tr><td>Cricket</td><td>New Zealand v India, 1st T20I, 22 Oct</td><td>Confirmed on NZC official fixtures — Hagley Oval,
Christchurch</td><td><span class="badge verified">Match</span></td></tr>
<tr><td>Cricket</td><td>Afghanistan v Bangladesh ODI, 23 Oct</td><td>No official board source retrieved in this build</td>
<td><span class="badge cross">Unverified</span></td></tr>
<tr><td>Cricket</td><td>Eastern Storm v Tuskers; North West Dragons v Limpopo Impalas; Northern Cape Heat v Garden
Route Badgers; Mpumalanga Rhinos v South Africa Emerging</td><td>South African domestic fixtures — no official CSA
source retrieved</td><td><span class="badge cross">Unverified</span></td></tr>
<tr><td>Basketball</td><td>Milwaukee Bucks @ Washington Wizards, money line, 9/11 tips (82%)</td>
<td>Confirmed on NBA.com — game 0022600086, 7:00 PM ET</td><td><span class="badge verified">Match</span></td></tr>
<tr><td>Basketball</td><td>Boston Celtics @ Detroit Pistons “today”, Philadelphia @ New York Knicks “tomorrow”</td>
<td>NBA standings corroborate a 20 October Boston/Detroit game (DET 1-0, BOS 0-1) — outside our window</td>
<td><span class="badge muted">Out of window</span></td></tr>
<tr><td>Gaelic football</td><td>St Finbarrs v Nemo Rangers, 25 Oct, draw and Nemo Rangers +1.50</td>
<td>GAA official calendar shows <em>no</em> inter-county fixture that week — this is a club championship game, a tier
the GAA calendar does not carry</td><td><span class="badge cross">Not verifiable</span></td></tr>
<tr><td>Football, horse racing</td><td>Extensive</td><td>Excluded by the brief</td><td><span class="badge muted">N/A</span></td></tr>
</tbody></table>

<div class="note warn">
  <b>The interesting finding.</b> OLBG's public tips board is dominated by football and racing, and its non-football
  coverage is thin, uneven and partly unverifiable. Of the six cricket fixtures OLBG listed for this window, exactly one
  could be confirmed on a governing body's own site. Meanwhile OLBG carried <em>nothing</em> for the two BLACKCAPS v India
  T20s that NZC had published months in advance, nor for any of the four World Series games.
</div>

<h2>6. Structural lessons for a scraper</h2>
<ul class="clean">
  <li>Enumerate sports from the sitemap, not the nav — the nav omits Greyhounds and never lists the IDs.</li>
  <li>Do not assume sport IDs are contiguous: 1–5, 7–17, 20–23, 25, 28. Six IDs in the range are unused or retired.</li>
  <li>Tipster consensus lives on the event page as “<code>9/11 Win Tips</code>”, i.e. selections ÷ tips — parse the
  fraction, not the percentage, because the percentage is rounded and can hide small samples.</li>
  <li>There is no public JSON API. Everything is server-rendered HTML, which is why the sitemap is the reliable entry
  point.</li>
</ul>
"""
    return shell("OLBG analysis", body, "rev")


def build_sources(D) -> str:
    rows = []
    for s in D["sources"]["sources"]:
        st = s["status"]
        badge = {"verified": '<span class="badge verified">Verified</span>',
                 "unverified": '<span class="badge cross">Unverified</span>',
                 "reference": '<span class="badge muted">Reference</span>'}[st]
        rows.append(
            f'<tr><td><b>{e(s["name"])}</b><span class="sub">{e(s["publisher"])}</span></td>'
            f'<td><a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["url"])}</a></td>'
            f'<td>{e(s["covers"])}<span class="sub">{e(s.get("note",""))}</span></td><td>{badge}</td></tr>'
        )
    body = f"""
<div class="crumb">Dashboard / Sources</div>
<h1>Source register</h1>
<p class="lede">Every source used in the build, with the exact URL. “Verified” means data was read from it for this
dataset. “Unverified” means the source is official but the page would not render, and rows depending on it are
flagged. “Reference” marks the subject of the reverse-engineering exercise.</p>
<div class="table-wrap"><table>
<thead><tr><th>Source</th><th>URL</th><th>What it was used for</th><th>Status</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>
<p class="sub">Register generated {e(D['sources']['generated'])}.</p>
"""
    return shell("Sources", body, "src")


def build_flagged(D, rows) -> str:
    flag_rows = []
    for m, p in rows:
        for f in m.get("flags", []):
            flag_rows.append(
                f'<tr><td><span class="match-name">{e(match_name(m))}</span>'
                f'<span class="sub">{e(m["competition"])} · {e(when(m))}</span></td>'
                f'<td>{e(m["sport"])}</td><td>{e(f)}</td><td>{status_badge(m["status"])}</td>'
                f'<td>{source_links(m, 2)}</td></tr>'
            )
    gaps = []
    for slug, cov in D["coverage"]["sports"].items():
        if cov["status"] in ("not-investigated", "partial", "event-only", "no-fixtures"):
            gaps.append(
                f'<tr><td><b>{e(slug)}</b></td><td>{e(cov["status"])}</td><td>{e(cov["detail"])}</td>'
                f'<td><a href="sports/{e(slug)}.html">sport page</a></td></tr>'
            )
    body = f"""
<div class="crumb">Dashboard / Flagged</div>
<h1>Flagged for review</h1>
<p class="lede">Nothing on this page blocks publication — the brief says flagged irregularities ship with the site so
they can be reviewed afterwards. Everything below is something a human should check.</p>

<div class="strip">
  <span class="chip">{len(flag_rows)} row-level flags</span>
  <span class="chip">{len(gaps)} coverage gaps</span>
  <span class="chip">{sum(1 for m,_ in rows if m['status']=='cross-checked')} cross-checked rows</span>
</div>

<h2>1. Row-level flags</h2>
<div class="table-wrap"><table>
<thead><tr><th>Match</th><th>Sport</th><th>Flag</th><th>Row status</th><th>Source</th></tr></thead>
<tbody>{''.join(flag_rows)}</tbody></table></div>

<h2>2. Coverage gaps</h2>
<div class="table-wrap"><table>
<thead><tr><th>Sport</th><th>Status</th><th>Detail</th><th></th></tr></thead>
<tbody>{''.join(gaps)}</tbody></table></div>

<h2>3. Known irregularities in the source material</h2>
<ul class="clean">
  <li><b>Premiership Rugby.</b> <code>premrugby.com/fixtures-results</code> is client-rendered and returned zero
  fixture rows. All five rugby union rows are cross-checked against the competition's official broadcaster and are
  marked accordingly. They should be re-checked against the club sites before being promoted to verified.</li>
  <li><b>PDC.</b> <code>pdc.tv</code> serves a cookie-consent interstitial in place of article bodies. The European
  Championship first-round draw was read from the publisher's own indexed copy of the PDC schedule release. The
  eighth Thursday tie (<em>Ross Smith v …</em>) was truncated and is therefore omitted rather than guessed.</li>
  <li><b>Snooker session times.</b> WST renders times in the viewer's local timezone. Only the date is recorded; the
  displayed times are reproduced verbatim with no timezone claim.</li>
  <li><b>Snooker venue.</b> The Waterfront Hall is the Northern Ireland Open's long-standing venue but is not stated on
  the fetched schedule block. It is flagged on every snooker row.</li>
  <li><b>Formula 1.</b> Round 18 (United States Grand Prix, 23–25 October) is verified, but the circuit name and race
  start time were not captured. Both are left blank rather than assumed.</li>
  <li><b>NBA.</b> The eleventh game on 21 October (Sacramento at LA Clippers) had its game ID and arena truncated on the
  source page. The fixture is verified; the ID is not, so the row links to the day's games page instead.</li>
  <li><b>MLB Game 5 onward.</b> Games 5–7 are conditional (“if necessary”) and are excluded from the priced set.</li>
</ul>

<h2>4. Judgement calls</h2>
<ul class="clean">
  <li><b>Unranked snooker players.</b> WST publishes a top-36 table on the fetched page; everyone below it is placed in
  one bounded bucket at rank 60. This is a conservative bound, not a measured ranking, and it is disclosed on every
  affected row.</li>
  <li><b>Match totals.</b> Every total line is the league baseline assumption. It is priced pick'em precisely because no
  match-specific scoring input was sourced. Do not read those prices as a view.</li>
  <li><b>Confidence tiers are sport-relative.</b> A 59% baseball favourite is tiered high; a 59% basketball favourite is
  not. The thresholds are printed on the Methodology page.</li>
</ul>
"""
    return shell("Flagged for review", body, "flag")


def build_404() -> str:
    body = """
<h1>Page not found</h1>
<p class="lede">That page does not exist. Try the <a href="/OLBG1/index.html">dashboard</a> or the
<a href="/OLBG1/sports.html">sport index</a>.</p>
"""
    return shell("Not found", body, "", base="/OLBG1/")


# --------------------------------------------------------------------------
def main() -> int:
    D = load()
    fixtures = D["fixtures"]
    lines = D["lines"]
    preds = D["preds"]

    by_id = {p["id"]: p for p in lines["lines"]}
    rows = [(m, by_id[m["id"]]) for m in fixtures["matches"] if m["id"] in by_id]

    from model import SPORTS as _S  # noqa
    D["model_config"] = [dict(slug=k, **v) for k, v in _S.items()]
    tax_sports = {s["slug"]: s for s in D["taxonomy"]["sports"]}
    slug_map = {
        "ice-hockey": "Ice_Hockey", "basketball": "Basketball", "baseball": "Baseball",
        "snooker": "Snooker", "darts": "Darts", "cricket": "Cricket",
        "rugby-union": "Rugby_Union", "motor-racing": "Motor_Racing",
    }
    D["model_sports"] = []
    for s in D["taxonomy"]["sports"]:
        if not s["in_scope"]:
            continue
        reverse = {v: k for k, v in slug_map.items()}
        slug = reverse.get(s["slug"]) or s["name"].lower().replace(" ", "-")
        D["model_sports"].append({"name": s["name"], "slug": slug, "id": s["id"],
                                  "olbg_slug": s["slug"]})

    stats = {
        "matches": len(rows),
        "sports_covered": sum(1 for s in D["model_sports"]),
        "high": sum(1 for _, p in rows if p["confidence"] == "high"),
        "medium": sum(1 for _, p in rows if p["confidence"] == "medium"),
        "low": sum(1 for _, p in rows if p["confidence"] == "low"),
        "both_rated": sum(1 for _, p in rows if p["both_rated"]),
        "both_measured": sum(1 for _, p in rows if p.get("both_measured")),
        "bounded_only": sum(1 for _, p in rows if p["both_rated"] and not p.get("both_measured")),
        "baseline_only": sum(1 for _, p in rows if not p["both_rated"]),
        "sources_verified": sum(1 for x in D["sources"]["sources"] if x["status"] == "verified"),
        "by_sport": {},
    }
    for m, _ in rows:
        stats["by_sport"][m["sport"]] = stats["by_sport"].get(m["sport"], 0) + 1

    (OUT / "sports").mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)

    shutil.copy(ROOT / "site_src/style.css", ASSETS / "style.css")
    shutil.copy(ROOT / "site_src/app.js", ASSETS / "app.js")
    (OUT / ".nojekyll").write_text("")

    def write(rel, html_text):
        (OUT / rel).write_text(html_text, encoding="utf-8")
        print("  wrote", rel)

    write("index.html", build_index(D, rows, stats))
    write("picks.html", build_picks(D, rows))
    write("predictions.html", build_predictions(D, rows, preds))
    write("sports.html", build_sports_index(D, stats))
    write("methodology.html", build_methodology(D, stats))
    write("reverse-engineering.html", build_reverse(D))
    write("sources.html", build_sources(D))
    write("flagged.html", build_flagged(D, rows))
    write("404.html", build_404())

    for sp in D["model_sports"]:
        write(f"sports/{sp['slug']}.html", build_sport_page(D, sp["slug"], sp, rows, stats))

    pages = [p for p in OUT.glob("*.html")] + list((OUT / "sports").glob("*.html"))
    print(f"\n{len(pages)} html files, {stats['matches']} priced matches")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
