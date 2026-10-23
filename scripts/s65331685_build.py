#!/usr/bin/env python3
"""T65331685 site build: render the /65331685/ dashboard from data/65331685 JSON.

Run: python3 scripts/s65331685_build.py
"""
from __future__ import annotations

import html
import json
import os
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "65331685")
SITE = os.path.join(ROOT, "65331685")

with open(os.path.join(DATA, "harvest.json")) as f:
    HARV = json.load(f)
with open(os.path.join(DATA, "fixtures.json")) as f:
    FIX = json.load(f)
with open(os.path.join(DATA, "lines.json")) as f:
    LINES = json.load(f)
with open(os.path.join(DATA, "predictions.json")) as f:
    PRED = json.load(f)
with open(os.path.join(DATA, "desk.json")) as f:
    DESK = json.load(f)

NAV = [
    ("index.html", "Dashboard"), ("sports.html", "Sports"), ("matches.html", "Matches"),
    ("markets.html", "Markets"), ("high-confidence.html", "High Confidence"),
    ("predictions.html", "Predictions"), ("analysis.html", "Analysis"), ("sources.html", "Sources"),
    ("flagged.html", "Flagged"), ("repo-audit.html", "Repo Audit"), ("methodology.html", "Methodology"),
]

CSS = """
body{font-family:Georgia,'Times New Roman',serif;margin:0;background:#f7f4ee;color:#22201c}
header{background:#22201c;color:#f7f4ee;padding:1.2rem 2rem}
header h1{margin:0;font-size:1.5rem;letter-spacing:.03em}
header p{margin:.35rem 0 0;font-size:.92rem;opacity:.85}
nav{background:#3c3830;padding:.55rem 2rem;display:flex;flex-wrap:wrap;gap:1rem}
nav a{color:#f7f4ee;text-decoration:none;font-size:.92rem}
nav a:hover{text-decoration:underline}
main{padding:1.25rem 2rem 3rem}
h2{border-bottom:2px solid #b48a3c;padding-bottom:.3rem}
h3{color:#5c4317}
table{border-collapse:collapse;width:100%;margin:.8rem 0;background:#fff}
th,td{border:1px solid #d8d2c4;padding:.45rem .6rem;font-size:.86rem;text-align:left;vertical-align:top}
th{background:#e9e2d2}
tr:nth-child(even){background:#fbf9f4}
.tag{display:inline-block;padding:.12rem .5rem;border-radius:.28rem;font-size:.72rem;font-weight:bold}
.high{background:#1c6b3d;color:#fff}
.medium{background:#b48a3c;color:#fff}
.low{background:#8a8578;color:#fff}
.chalk{background:#8c2f21;color:#fff}
.oob{background:#8c2f21;color:#fff}
.unv{background:#5b4b8a;color:#fff}
.note{font-size:.83rem;color:#555148}
.summary{background:#fff;border-left:5px solid #b48a3c;padding:.9rem 1.1rem;margin:1rem 0}
footer{background:#22201c;color:#bdb6a8;padding:1rem 2rem;font-size:.8rem}
a{color:#7a4b12}
"""


def esc(x):
    return html.escape(str(x if x is not None else ""))


def page(name, title, body):
    nav = "".join(f'<a href="{u}">{esc(t)}</a>' for u, t in NAV)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} — T65331685 Sports Desk</title>
<meta name="description" content="T65331685 official-source sports desk: zero-vig multi-market pricing, high-confidence picks, full evidence trail.">
<link rel="stylesheet" href="style.css"></head><body>
<header><h1>OLBG Sports Desk — Session T65331685</h1>
<p>Official-source verification + zero-vig multi-market origination · 15 sports · generated 2026-10-23 20:40 UTC · branch arena/65331685-olbg1</p></header>
<nav>{nav}</nav><main>{body}</main>
<footer>Built from reads logged in <a href="sources.html">Sources</a>. Quotes/availability/edge left blank per repository policy. Nothing is treated as confirmed without an official-source read recorded with its time.</footer>
</body></html>"""


def tier_tag(t):
    cls = {"High": "high", "Medium": "medium", "Low": "low",
           "Chalk (disclosed)": "chalk", "Out-of-band (disclosed)": "oob"}.get(t, "unv")
    return f'<span class="tag {cls}">{esc(t)}</span>'


os.makedirs(SITE, exist_ok=True)
FIXES = {f["id"]: f for f in FIX["fixtures"]}

# ------------------------------------------------------------------ index ----
high = [m for group in LINES["markets"] for m in group["selections"] if m["tier"] == "High"]
chalk = [m for group in LINES["markets"] for m in group["selections"] if m["tier"] == "Chalk (disclosed)"]
counts = FIX["counts"]
rows = []
for m in sorted(high, key=lambda z: -z["prob"]):
    rows.append(f"<tr><td>{esc(m['sport'])}</td><td>{esc(m['match'])}</td><td>{esc(m['market'])}</td>"
                f"<td><b>{esc(m['selection'])}</b></td><td>{m['prob']:.4f}</td><td>{m['fair_decimal']:.3f}</td>"
                f"<td>{m['fair_american']:.1f}</td><td>{tier_tag(m['tier'])}</td><td class='note'>{esc(m['model'])}</td></tr>")
body = f"""
<h2>Executive summary</h2>
<div class="summary"><p>Friday-night desk covering the 15 OLBG hub sports for the 2026-10-23/25 window. Discovery ran through OLBG hub/event routes (hub tip feeds rendered empty in the fetch channel — logged as a platform irregularity; event pages via <code>?event_id=</code> render full tip blocks). Every priced input was read from an official source in this session and logged with a UTC timestamp. The line sheet originated {len(DESK['markets'])} zero-vig prices across {counts['rows']} fixture rows, with {counts['elapsed_rows']} elapsed/in-play rows recorded separately.</p>
<p><b>High-confidence picks tonight: {len(high)}</b> under the strict gate (p&gt;0.70 and fair American between −250 and +10000). Winner-market favourites priced beyond that window are disclosed below and never promoted.</p></div>
<h3>High-confidence selections</h3>
<table><tr><th>Sport</th><th>Match</th><th>Market</th><th>Selection</th><th>Prob</th><th>Dec</th><th>Am</th><th>Tier</th><th>Engine</th></tr>{''.join(rows)}</table>
<h3>Chalk-suppressed ledger (winner markets with p&gt;0.7143 — disclosed, not promoted)</h3>
<table><tr><th>Sport</th><th>Match</th><th>Selection</th><th>Prob</th><th>fair American</th><th>Reason</th></tr>
{''.join(f"<tr><td>{esc(m['sport'])}</td><td>{esc(m['match'])}</td><td>{esc(m['selection'])}</td><td>{m['prob']:.4f}</td><td>{m['fair_american']:.1f}</td><td class='note'>shorter than the −250 floor</td></tr>" for m in chalk)}</table>
<p class="note">Coverage gaps and unconfirmed rows are listed on <a href="flagged.html">Flagged</a>; the evidence table is <a href="sources.html">Sources</a>.</p>
"""
open(os.path.join(SITE, "index.html"), "w").write(page("index.html", "Dashboard", body))

# ------------------------------------------------------------------ sports ---
by_sport_fix = defaultdict(list)
for f in FIX["fixtures"]:
    by_sport_fix[f["sport"]].append(f)
by_sport_pred = defaultdict(list)
for p in PRED["predictions"]:
    by_sport_pred[p["sport"]].append(p)
parts = ["<h2>Sports coverage</h2><p>Each sport lists the OLBG discovery channel, the official sources read in this session, fixture counts, and the written picks.</p>"]
order = ["Ice Hockey", "Baseball", "Basketball", "Rugby Union", "Rugby League", "Cricket", "Tennis", "Snooker",
         "Darts", "Golf", "Gaelic Sports", "Greyhounds", "Motor Racing", "Handball", "Volleyball"]
for sp in order:
    fl = by_sport_fix.get(sp, [])
    pr = by_sport_pred.get(sp, [])
    verified = sum(1 for f in fl if f["official"]["sources"] and f["label"] != "unverified")
    srcs = sorted({s for f in fl for s in f["official"]["sources"]})
    src_html = "".join(f'<li><a href="{esc(u)}">{esc(u)}</a></li>' for u in srcs[:8])
    parts.append(f"""
<h3>{esc(sp)}</h3>
<p class="note">Fixtures: {len(fl)} ({verified} with official reads) · written picks: {len(pr)} · OLBG hub route checked this session (discovery only).</p>
<ul class="note">{src_html}</ul>
<table><tr><th>Start (UTC)</th><th>Fixture</th><th>Competition</th><th>Status</th><th>Records read</th></tr>
{''.join(f"<tr><td>{esc(f['start_utc'])}</td><td>{esc(f['away'])} @ {esc(f['home'])}</td><td>{esc(f['competition'])}</td><td>{tier_tag('unv') if f['label']=='unverified' else 'official read' if f['official']['sources'] else 'discovery only'}</td><td class='note'>{esc(f['official']['record_home'])} / {esc(f['official']['record_away'])}</td></tr>" for f in fl)}</table>""")
open(os.path.join(SITE, "sports.html"), "w").write(page("sports.html", "Sports", "".join(parts)))

# ----------------------------------------------------------------- matches ---
rows = []
for f in sorted(FIX["fixtures"], key=lambda z: (z["start_utc"], z["sport"])):
    src = f["official"]["sources"][0] if f["official"]["sources"] else ""
    src_cell = f'<a href="{esc(src)}">{esc(src[:60])}…</a>' if src else '<span class="tag unv">unverified</span>'
    rows.append(f"<tr><td>{esc(f['start_utc'])}</td><td>{esc(f['sport'])}</td><td>{esc(f['competition'])}</td>"
                f"<td>{esc(f['away'])} @ {esc(f['home'])}</td><td>{esc(f['venue'])}</td>"
                f"<td class='note'>{esc(f['official']['record_away'])} / {esc(f['official']['record_home'])}</td>"
                f"<td>{src_cell}</td><td class='note'>{esc(f['note'])}</td></tr>")
el = "".join(f"<tr class='elrow'><td>{esc(e['start_utc'])}</td><td>{esc(e['sport'])}</td><td>{esc(e['competition'])}</td><td>{esc(e['away'])} @ {esc(e['home'])}</td><td class='note'>{esc(e['note'])}</td></tr>" for e in FIX["elapsed"])
body = f"""<h2>Full match list</h2>
<p class="note">Upcoming fixtures ({len(FIX['fixtures'])} rows) sorted by start time; every row carries a source link. Elapsed and in-play rows recorded at read time follow.</p>
<table><tr><th>Start (UTC)</th><th>Sport</th><th>Competition</th><th>Fixture</th><th>Venue</th><th>Records (away / home)</th><th>Official source</th><th>Notes</th></tr>{''.join(rows)}</table>
<h3>Elapsed / in play at read time</h3>
<table><tr><th>Start (UTC)</th><th>Sport</th><th>Competition</th><th>Fixture</th><th>Read-time note</th></tr>{el}</table>"""
open(os.path.join(SITE, "matches.html"), "w").write(page("matches.html", "Matches", body))

# ----------------------------------------------------------------- markets ---
parts = ["<h2>Multi-market pricing</h2>",
         f"<p class='note'>All {len(DESK['markets'])} originated prices are zero-vig (each two-sided market sums to 1.000). "
         "Winner markets, handicaps/spreads, and totals ladders per fixture. Unrounded probabilities decide tier flags.</p>"]
for group in sorted(LINES["markets"], key=lambda g: g["fixture_id"]):
    fid = group["fixture_id"]
    f = FIXES.get(fid, {})
    match = f"{f.get('away','')} @ {f.get('home','')}" if f else fid
    rowsm = "".join(
        f"<tr><td>{esc(m['market'])}</td><td>{esc(m['selection'])}</td><td>{m['prob']:.4f}</td>"
        f"<td>{m['fair_decimal']:.3f}</td><td>{m['fair_american']:.1f}</td><td>{tier_tag(m['tier'])}</td>"
        f"<td class='note'>{esc(m['model'])}</td><td class='note'>{esc(m['note'])}</td></tr>"
        for m in group["selections"])
    parts.append(f"<h3>{esc(fid)} — {esc(match)} <span class='note'>({esc(f.get('start_utc',''))})</span></h3>"
                 f"<table><tr><th>Market</th><th>Selection</th><th>Prob</th><th>Dec</th><th>Am</th><th>Tier</th><th>Engine</th><th>Note</th></tr>{rowsm}</table>")
open(os.path.join(SITE, "markets.html"), "w").write(page("markets.html", "Markets", "".join(parts)))

# ------------------------------------------------------- high-confidence ----
rows = "".join(
    f"<tr><td>{esc(m['sport'])}</td><td>{esc(m['match'])}</td><td>{esc(m['market'])}</td><td><b>{esc(m['selection'])}</b></td>"
    f"<td>{m['prob']:.4f}</td><td>{m['fair_decimal']:.3f}</td><td>{m['fair_american']:.1f}</td><td class='note'>{esc(m['model'])}</td></tr>"
    for m in sorted(high, key=lambda z: -z["prob"]))
body = f"""<h2>High confidence</h2>
<div class="summary"><p>Gate: unrounded p &gt; 0.70 <b>and</b> fair American between −250 and +10000 (float tolerance 1e-6). Picks outside the window are listed on the chalk ledger of the dashboard and are never promoted. Tonight's strict-gate count: <b>{len(high)}</b>.</p></div>
<table><tr><th>Sport</th><th>Match</th><th>Market</th><th>Selection</th><th>Prob</th><th>Dec</th><th>Am</th><th>Engine</th></tr>{rows}</table>
<h3>Chalk-suppressed (p&gt;0.7143, winner markets)</h3>
<table><tr><th>Sport</th><th>Match</th><th>Selection</th><th>Prob</th><th>fair American</th></tr>
{''.join(f"<tr><td>{esc(m['sport'])}</td><td>{esc(m['match'])}</td><td>{esc(m['selection'])}</td><td>{m['prob']:.4f}</td><td>{m['fair_american']:.1f}</td></tr>" for m in chalk)}</table>"""
open(os.path.join(SITE, "high-confidence.html"), "w").write(page("high-confidence.html", "High Confidence", body))

# ------------------------------------------------------------ predictions ----
by_sp = defaultdict(list)
for p in PRED["predictions"]:
    by_sp[p["sport"]].append(p)
parts = ["<h2>Predictions</h2>", "<p class='note'>Hand-written write-ups (min 30 words, unique 6-grams, banned-word clean) for the day's highest-confidence selections in each sport. Every factual clause carries its source and read time in the <a href='analysis.html'>analysis</a> fact tables.</p>"]
for sp in order:
    for p in by_sp.get(sp, []):
        facts = "".join(f"<li class='note'>{esc(fc['claim'])} — <a href='{esc(fc['source'])}'>source</a> ({esc(fc['read_utc'])})</li>" for fc in p["facts"])
        parts.append(f"""
<h3>{esc(p['match'])} — <b>{esc(p['selection'])}</b> <span class='note'>{esc(p['sport'])} · {esc(p['competition'])} · {esc(p['start_utc'])}</span></h3>
<p>{esc(p['text'])}</p><ul>{facts}</ul>""")
open(os.path.join(SITE, "predictions.html"), "w").write(page("predictions.html", "Predictions", "".join(parts)))

# --------------------------------------------------------------- analysis ----
cons = "".join(f"<tr><td>{esc(k)}</td><td>{esc(v)}</td></tr>" for k, v in LINES["constants"].items())
body = f"""<h2>Analysis</h2>
<h3>Pricing constants (disclosed)</h3>
<table><tr><th>Constant</th><th>Value</th></tr>{cons}</table>
<h3>Method in brief</h3>
<p>Record inputs are shrunk toward .500 with a Beta(2,2) prior and combined with log5; NHL overtime losses count as defeats and rugby draws split 0.5/0.5 (both disclosed). Runs, goals and points come from paired per-game rates with independent Poisson scores conditioned on no tie; fixed half-point ladders keep every two-sided market zero-vig. Handicap and total rungs use gaussian margins with the disclosed sport deviations. Greyhound prices normalize the read semi-final clocks; rugby league prices use the elite-spine representation index; tennis prices use the rank-Elo proxy shown in the constants table.</p>
<h3>Decision notes</h3>
<ul>
<li>The Edmonton Oilers moneyline sits exactly on the −250 floor (p=0.7143) and is included under inclusive band edges; the float tolerance is documented in the constants.</li>
<li>NBA probabilities barely clear .69 on one-game records; nothing crossed 0.70, so no basketball selection is tagged High tonight.</li>
<li>Heavy favourites (Glasgow, Samoa, England, New Zealand, Australia, Pakistan, Nantes, Paris) run shorter than −250 and are listed only on the chalk ledger.</li>
<li>OLBG hub tip feeds rendered "No tips found." in the fetch channel all evening while event pages rendered full tip blocks; the discovery record is preserved and the irregularity is logged under Flagged.</li>
<li>OLBG hub clocks render America/New_York times without labels; conversions are flagged on affected rows (Nantes kickoff shows a one-hour disagreement with the official LNH calendar).</li>
</ul>
<h3>Tier distribution</h3>
<p class="note">{len(high)} High · {sum(1 for g in LINES['markets'] for m in g['selections'] if m['tier']=='Medium')} Medium · {sum(1 for g in LINES['markets'] for m in g['selections'] if m['tier']=='Low')} Low · {len(chalk)} chalk-disclosed · {sum(1 for g in LINES['markets'] for m in g['selections'] if m['tier']=='Out-of-band (disclosed)')} other out-of-band.</p>"""
open(os.path.join(SITE, "analysis.html"), "w").write(page("analysis.html", "Analysis", body))

# ---------------------------------------------------------------- sources ----
rows = "".join(f"<tr><td>{esc(r['read_utc'])}</td><td><a href='{esc(r['url'])}'>{esc(r['url'])}</a></td><td class='note'>{esc(r['takeaway'])}</td></tr>" for r in HARV["reads"])
body = f"""<h2>Sources</h2>
<p class="note">{len(HARV['reads'])} reads through the Arena fetch/search layer on 2026-10-23, each with URL and UTC read time. Search-layer reads of pdc.tv are marked as such in their takeaways.</p>
<table><tr><th>Read (UTC)</th><th>URL</th><th>Takeaway used</th></tr>{rows}</table>"""
open(os.path.join(SITE, "sources.html"), "w").write(page("sources.html", "Sources", body))

# ---------------------------------------------------------------- flagged ----
flags = [f for f in FIX["fixtures"] if f["label"] == "unverified" or not f["official"]["sources"]]
rows = "".join(f"<tr><td>{esc(f['id'])}</td><td>{esc(f['sport'])}</td><td>{esc(f['away'])} @ {esc(f['home'])}</td><td class='note'>{esc(f['note'] or 'no official read captured')}</td></tr>" for f in flags)
body = f"""<h2>Flagged / unverified</h2>
<p class="note">Rows published for coverage but not confirmed by an official read this session, or carrying known input gaps. Values stay blank rather than being filled by guesswork.</p>
<table><tr><th>Row</th><th>Sport</th><th>Fixture</th><th>Flag</th></tr>{rows}</table>
<h3>Standing irregularities</h3>
<ul>
<li>OLBG hub tip feeds returned "No tips found." across all tested hub routes in the fetch channel on 2026-10-23 while event pages rendered full tip blocks — logged as a platform irregularity; earlier hub listings remain the discovery record.</li>
<li>OLBG hub times render in unlabeled America/New_York; Nantes v Chambéry shows an OLBG/official one-hour disagreement.</li>
<li>PDC article bodies sat behind a consent wall in direct fetches; schedule and results were taken from search-layer reads of pdc.tv pages.</li>
<li>URC table values are cross-referenced (official match centre plus BBC Sport table); the Leinster points total differs between trackers and is noted on the row.</li>
<li>Golf matchup rows for the Genesis Championship and any tournament without a read leaderboard remain unpriced.</li>
<li>WTA/ATP start times for the weekend sessions come from OLBG renders and are flagged until the order of play pages confirm them.</li>
</ul>"""
open(os.path.join(SITE, "flagged.html"), "w").write(page("flagged.html", "Flagged", body))

# ------------------------------------------------------------- repo-audit ----
body = f"""<h2>Repo audit</h2>
<table><tr><th>Check</th><th>Result</th></tr>
<tr><td>Working branch</td><td>arena/65331685-olbg1 (session-scoped; no other branch touched)</td></tr>
<tr><td>Root shared files</td><td>README.md and COORDINATION.md modified only for claim + receipts (append-only in §73)</td></tr>
<tr><td>Namespaced outputs</td><td>all generated artifacts under <code>65331685/</code>, <code>data/65331685/</code>, <code>scripts/s65331685_*</code>, <code>tests/pipeline/test_s65331685.py</code></td></tr>
<tr><td>Shared pipeline</td><td>not modified; this desk stands alone and reuses only the canonical pricing conventions (Beta(2,2)+log5, zero-vig, no home edge)</td></tr>
<tr><td>Two-sided zero-vig markets</td><td>every market pair sums to 1.000 by construction (checks in <code>scripts/s65331685_validate.py</code>)</td></tr>
<tr><td>Source link per data row</td><td>fixtures/markets tables carry source links; unlinked rows are listed under Flagged</td></tr>
<tr><td>Quote policy</td><td>bookmaker quotes, availability and edge left blank even where an odds column existed on a read page (PGA Tour leaderboard)</td></tr>
<tr><td>Validator</td><td><code>python3 scripts/s65331685_validate.py</code> gates schema, band logic, zero-vig pairs, banned words, 6-gram uniqueness, min-word counts, and source-link presence</td></tr>
<tr><td>Tests</td><td><code>python3 -m unittest discover -s tests/pipeline</code> includes <code>test_s65331685.py</code></td></tr>
</table>"""
open(os.path.join(SITE, "repo-audit.html"), "w").write(page("repo-audit.html", "Repo Audit", body))

# ----------------------------------------------------------- methodology -----
body = """<h2>Methodology</h2>
<h3>Verification rule</h3>
<p>Nothing counts as confirmed until the official body's page (or its stats endpoint) has been fetched through the Arena layer in this session and logged with a UTC time in Sources. Third-party trackers are used only as cross-references and the rows they support are marked accordingly. Where an input cannot be confirmed, the cell stays blank and the row is listed under Flagged.</p>
<h3>Line origination</h3>
<ul>
<li><b>Record markets</b>: Beta(2,2) shrinkage on raw win rates (NHL: W/(W+L+OTL); rugby: (W+0.5D)/P), combined with log5, no home edge.</li>
<li><b>Runs/goals/points</b>: paired per-game rates (attack v defence averages), independent Poisson scores conditioned on no tie for the win market, half-point totals ladders.</li>
<li><b>Handicaps and spreads</b>: gaussian margins with disclosed sport deviations (NBA 11.5, NHL 1.9, rugby 14, handball 4, MLB 4.3 runs).</li>
<li><b>Specialist links</b>: rank-Elo proxy for tennis, semi-clock logistic for the dogs, elite-spine index for league internationals, tournament frame share for snooker — each listed in the constants table.</li>
</ul>
<h3>Confidence gate</h3>
<p>High requires an unrounded probability above 0.70 with the fair American price inside −250…+10000. Favourites shorter than the floor are chalk-suppressed and disclosed. Medium covers 0.55–0.70; Low covers the rest.</p>
<h3>Language policy</h3>
<p>Prediction write-ups run 30+ words, avoid the banned vocabulary list, and share no repeated 6-gram. Factual clauses name their source; judgment calls read as opinion.</p>"""
open(os.path.join(SITE, "methodology.html"), "w").write(page("methodology.html", "Methodology", body))

with open(os.path.join(SITE, "style.css"), "w") as f:
    f.write(CSS)
print("site written:", sorted(os.listdir(SITE)))
