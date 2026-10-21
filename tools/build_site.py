#!/usr/bin/env python3
"""Build the aa4e9dbf desk (aa4e9dbf/) and data files (data/*-aa4e9dbf*) from tools/data_*.py.

Single source of truth: the EVENTS_* lists. Run:  python3 tools/build_site.py
Outputs:
  data/sports-aa4e9dbf/<slug>.json   per-sport datasets
  data/matches-aa4e9dbf-olbg1.json  combined dataset
  aa4e9dbf/index.html          landing dashboard
  aa4e9dbf/<slug>.html         per-sport page
  aa4e9dbf/predictions.html    high-confidence write-ups
  aa4e9dbf/flagged.html        flagged-for-review register
  aa4e9dbf/methodology.html    reverse-engineering + methodology
  aa4e9dbf/assets/style.css    shared styles

Namespaced so this desk coexists with the other parallel-session boards
(repo-root dashboard, docs/ board, ebfbd966/ desk) on the same Pages site.
"""
import json, os, re, html, datetime

from data_a import EVENTS_A
from data_b import EVENTS_B
from data_c import EVENTS_C

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "aa4e9dbf")
DATA = os.path.join(ROOT, "data")

CAPTURED = "2026-10-21 05:00-08:00 UTC"
BUILT = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

ALL = EVENTS_A + EVENTS_B + EVENTS_C

SPORTS = [
    ("basketball", "Basketball"), ("tennis", "Tennis"), ("ice-hockey", "Ice Hockey"),
    ("baseball", "Baseball"), ("cricket", "Cricket"), ("rugby-union", "Rugby Union"),
    ("darts", "Darts"), ("snooker", "Snooker"), ("golf", "Golf"), ("handball", "Handball"),
    ("volleyball", "Volleyball"), ("motor-racing", "Motor Racing"), ("rugby-league", "Rugby League"),
    ("esports", "eSports"),
]
EXCLUDED = [
    ("Football (soccer)", "Excluded by requirement"), ("Horse Racing", "Excluded by requirement"),
    ("Boxing / UFC / MMA", "Excluded by requirement"), ("American Football", "Excluded by requirement"),
    ("Cycling", "Excluded by requirement"), ("Hurling", "Excluded by requirement"),
    ("Specials", "Excluded by requirement"),
    ("Gaelic Football", "Excluded - football code (flagged for review)"),
    ("Aussie Rules", "Excluded - football code (flagged for review)"),
    ("Greyhounds", "Excluded by analogy to horse racing - animal racing (flagged for review)"),
]

MARKET_MAP = {
    "Tennis": "Win Match; Set Betting (2-0/2-1 etc.); 1st Set Winner; Games Won (+/- games handicap); Total Games (O/U)",
    "Basketball": "Money Line; Handicap (spread); Game Totals (O/U points)",
    "Ice Hockey": "Money Line (incl. OT/SO); Puck Line; Game Totals (O/U goals)",
    "Baseball": "Money Line; Run Line; Game Totals (O/U runs)",
    "Cricket": "Win Match; plus batter/bowler and innings runs markets",
    "Rugby Union": "To Win (match winner); Handicap; Total Points",
    "Rugby League": "Match winner; handicap; Grand Final winner (outright)",
    "Darts": "Win Match 2-way; Handicap 2-way (legs); Total Legs (O/U)",
    "Snooker": "Win Match; Handicap (frames); Frame Betting; Win Tournament (outright)",
    "Golf": "Win Tournament (outright); top-5/10/20; matchups",
    "Handball": "Money Line (3-way); Match Handicap; Total Goals",
    "Volleyball": "Win Match; Set Score; Total Sets; set handicap",
    "Motor Racing": "Win Race; Fastest Qualifier; Podium; Top 6; Points Finish; Fastest Lap; championship outrights",
    "eSports": "Win Match; map handicap; total maps (none listed at capture)",
}

NAV = "".join(
    f'<a href="{slug}.html">{name}</a>' for slug, name in SPORTS
) + '<a href="predictions.html" class="nav-hi">Predictions</a><a href="flagged.html">Flagged</a><a href="methodology.html">Methodology</a>'

STATUS_LABEL = {"pre": "Pre-match", "near": "Near start / in play at capture", "n/a": "n/a"}

def slugify(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s

def e(s):
    return html.escape(str(s)) if s else ""

def conf_badge(c):
    if c == "high":
        return '<span class="badge conf-high">HIGH</span>'
    if c == "medium":
        return '<span class="badge conf-med">MEDIUM</span>'
    if c == "low":
        return '<span class="badge conf-low">LOW</span>'
    return '<span class="badge conf-none">-</span>'

def ver_badge(v):
    m = {"verified": ("ver-v", "VERIFIED"), "partial": ("ver-p", "PARTIAL"), "unverified": ("ver-u", "UNVERIFIED")}
    cls, lbl = m.get(v, ("ver-u", "UNVERIFIED"))
    return f'<span class="badge {cls}">{lbl}</span>'

def line_text(line):
    if not line:
        return ""
    parts = []
    if line.get("ml"): parts.append("ML: " + line["ml"])
    if line.get("spread"): parts.append("Spread: " + line["spread"])
    if line.get("puck"): parts.append("Puck line: " + line["puck"])
    if line.get("run"): parts.append("Run line: " + line["run"])
    if line.get("handi"): parts.append("Handicap: " + line["handi"])
    if line.get("sets"): parts.append("Sets: " + line["sets"])
    if line.get("total"): parts.append("Total: " + line["total"])
    if line.get("outright"): parts.append("Outright: " + line["outright"])
    return "<br>".join(e(p) for p in parts)

def source_cell(ev):
    if ev.get("url"):
        return f'<a href="{e(ev["url"])}" target="_blank" rel="noopener">{e(ev.get("src") or "Official source")}</a>'
    return '<span class="blank">blank - unverified</span>'

def pick_cell(ev):
    p = ev.get("pick") or {}
    if not p.get("sel"):
        return '<span class="blank">-</span>'
    note = f'<div class="picknote">{e(p["note"])}</div>' if p.get("note") else ""
    return f'<strong>{e(p["sel"])}</strong><div class="pickmkt">{e(p.get("mkt",""))}</div>{note}'

CSS = """
:root{--bg:#0f1420;--panel:#171e2e;--panel2:#1d2638;--ink:#e8edf6;--mut:#93a0b4;--acc:#4da3ff;
--hi:#22c55e;--med:#eab308;--low:#f97316;--warn:#f87171;--line:#2a3550}
*{box-sizing:border-box;margin:0;padding:0}
body{font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
background:var(--bg);color:var(--ink)}
a{color:var(--acc);text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}
header.site{background:var(--panel);border-bottom:1px solid var(--line);padding:14px 0;position:sticky;top:0;z-index:5}
.brand{display:flex;align-items:center;gap:10px;font-weight:800;font-size:19px;letter-spacing:.3px}
.brand .dot{width:11px;height:11px;border-radius:50%;background:var(--hi);display:inline-block}
nav.top{display:flex;flex-wrap:wrap;gap:4px 14px;margin-top:9px;font-size:13.5px}
nav.top a{color:var(--mut);padding:3px 2px;border-bottom:2px solid transparent}
nav.top a:hover{color:var(--ink);text-decoration:none}
nav.top a.nav-hi{color:var(--hi);font-weight:700}
main{padding:28px 0 60px}
h1{font-size:26px;margin-bottom:6px}h2{font-size:19px;margin:26px 0 10px}h3{font-size:16px;margin:18px 0 8px}
p.lead{color:var(--mut);max-width:840px}
.grid{display:grid;gap:14px}
.cards{grid-template-columns:repeat(auto-fill,minmax(240px,1fr))}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px}
.card h3{margin:0 0 6px;font-size:15.5px}
.card .big{font-size:30px;font-weight:800}
.card .sub{color:var(--mut);font-size:12.5px}
.statrow{display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}
.badge{display:inline-block;font-size:10.5px;font-weight:800;padding:2px 7px;border-radius:20px;letter-spacing:.5px;vertical-align:middle}
.conf-high{background:rgba(34,197,94,.16);color:var(--hi);border:1px solid rgba(34,197,94,.4)}
.conf-med{background:rgba(234,179,8,.14);color:#facc15;border:1px solid rgba(234,179,8,.4)}
.conf-low{background:rgba(249,115,22,.14);color:#fb923c;border:1px solid rgba(249,115,22,.4)}
.conf-none{background:rgba(148,163,184,.12);color:#94a3b8;border:1px solid rgba(148,163,184,.35)}
.ver-v{background:rgba(34,197,94,.14);color:#4ade80;border:1px solid rgba(34,197,94,.4)}
.ver-p{background:rgba(234,179,8,.12);color:#facc15;border:1px solid rgba(234,179,8,.4)}
.ver-u{background:rgba(248,113,113,.13);color:#f87171;border:1px solid rgba(248,113,113,.45)}
table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);
border-radius:12px;overflow:hidden;font-size:13.5px}
th{background:var(--panel2);text-align:left;padding:10px 12px;font-size:12px;text-transform:uppercase;
letter-spacing:.6px;color:var(--mut);border-bottom:1px solid var(--line)}
td{padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}
tr:last-child td{border-bottom:none}
tr.unverified-row td{background:rgba(248,113,113,.05)}
.blank{color:#64748b;font-style:italic}
.picknote{color:var(--hi);font-size:12px;margin-top:3px}
.pickmkt{color:var(--mut);font-size:12px}
.tblwrap{overflow-x:auto;border-radius:12px}
.flagchip{display:inline-block;background:rgba(248,113,113,.12);border:1px solid rgba(248,113,113,.4);
color:#f8a5a5;font-size:11.5px;border-radius:6px;padding:2px 7px;margin:2px 4px 2px 0}
.predict-card{background:var(--panel);border:1px solid var(--line);border-left:4px solid var(--hi);
border-radius:12px;padding:20px;margin-bottom:18px}
.predict-card .meta{color:var(--mut);font-size:12.5px;margin-bottom:8px}
.predict-card p.body{margin:10px 0}
.xboard{background:#12325e;color:#dbe7ff;font-size:13px;padding:9px 0;border-bottom:1px solid #24477f}
.xboard a{color:#9fc3ff;text-decoration:underline}
.facts{margin-top:10px;padding-left:18px;color:var(--mut);font-size:13px}
.facts li{margin:4px 0}
footer{border-top:1px solid var(--line);color:var(--mut);font-size:12.5px;padding:20px 0 40px;margin-top:30px}
.kicker{color:var(--acc);font-size:12px;font-weight:800;letter-spacing:1.2px;text-transform:uppercase}
.pill{display:inline-block;background:var(--panel2);border:1px solid var(--line);border-radius:20px;
padding:4px 12px;font-size:12.5px;color:var(--mut);margin:0 6px 6px 0}
.sportcard{display:flex;flex-direction:column;gap:6px}
.sportcard a.stitle{font-weight:700;font-size:16px}
.counts{font-size:12.5px;color:var(--mut)}
ul.plain{padding-left:20px}ul.plain li{margin:6px 0}
code{background:var(--panel2);border:1px solid var(--line);border-radius:5px;padding:1px 6px;font-size:12.5px}
"""

def is_review_flag(f):
    fU = f.upper()
    return ("UNVERIFIED" in fU or "CONFLICT" in fU or "FINDING" in fU
            or "verify on" in fU or "VERIFY ON" in fU or "verify at" in fU
            or "not captured" in fU or "unconfirmed" in fU or "differ" in fU)

def page(title, body, active=""):
    act = f'class="active-now"' if active else ""
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} | OLBG Coverage</title>
<meta name="description" content="Independently originated betting lines, picks and verified match data for OLBG-listed sports (exclusions applied).">
<link rel="stylesheet" href="assets/style.css">
</head><body>
<header class="site"><div class="wrap">
<div class="brand"><span class="dot"></span> OLBG Coverage Desk <span style="font-weight:400;color:var(--mut);font-size:12.5px">session aa4e9dbf &middot; independent lines &amp; picks</span></div>
<nav class="top"><a href="index.html">Home</a>{NAV}</nav>
</div></header>
<div class="xboard"><div class="wrap">One of four independently built boards from parallel sessions on the same 2026-10-21 snapshot:
<strong>this desk</strong> (131 events, per-fact sources),
<a href="../index.html">root dashboard</a> (49 priced fixtures, governing-body APIs),
<a href="../docs/index.html">docs/ board</a> (164 events, OLBG tip-share model),
<a href="../ebfbd966/index.html">ebfbd966 desk</a> (133 matches). Different methods, no superset &mdash; read both agreement and disagreement as signal.</div></div>
<main class="wrap">{body}</main>
<footer class="wrap">
Data captured from OLBG.com sport hubs on {CAPTURED}. Lines, picks and predictions are our own independent estimates -
not OLBG tips and not bookmaker odds. Every row links to an official source where one was captured; unconfirmed values are left blank and flagged.
Built {BUILT}. 18+ only. Bet responsibly.
</footer></body></html>"""

def sport_table(evs):
    rows = []
    for ev in evs:
        cls = ' class="unverified-row"' if ev.get("ver") == "unverified" else ""
        flags = "".join(f'<span class="flagchip" title="{e(f)}" data-kind="{"review" if is_review_flag(f) else "note"}">{"flag" if is_review_flag(f) else "note"}</span>' for f in ev.get("flags", []))
        facts_ul = ""
        rows.append(f"""<tr{cls}>
<td><strong>{e(ev["ev"])}</strong><div style="color:var(--mut);font-size:12px">{e(ev["comp"])}</div></td>
<td>{e(ev.get("dt",""))}<div style="color:var(--mut);font-size:12px">{e(ev.get("vn",""))}</div></td>
<td>{line_text(ev.get("line")) or '<span class="blank">blank</span>'}</td>
<td>{pick_cell(ev)}</td>
<td>{conf_badge((ev.get("pick") or {}).get("conf",""))}</td>
<td>{source_cell(ev)}<div style="margin-top:4px">{ver_badge(ev.get("ver"))} {flags}</div></td>
</tr>""")
    return f"""<div class="tblwrap"><table>
<thead><tr><th>Match / Event</th><th>When &amp; where (official)</th><th>Our originated line</th><th>Our pick</th><th>Confidence</th><th>Official source</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>"""

def build():
    os.makedirs(os.path.join(DATA, "sports-aa4e9dbf"), exist_ok=True)
    os.makedirs(os.path.join(DOCS, "assets"), exist_ok=True)
    with open(os.path.join(DOCS, "assets", "style.css"), "w") as f:
        f.write(CSS)

    # ---------- data files ----------
    for slug, name in SPORTS:
        evs = [x for x in ALL if x["sport"] == name]
        with open(os.path.join(DATA, "sports-aa4e9dbf", slug + ".json"), "w") as f:
            json.dump(dict(sport=name, captured=CAPTURED, events=evs), f, indent=1, ensure_ascii=False)
    with open(os.path.join(DATA, "matches-aa4e9dbf-olbg1.json"), "w") as f:
        json.dump(dict(captured=CAPTURED, events=ALL), f, indent=1, ensure_ascii=False)

    structure = dict(
        captured=CAPTURED,
        sitemap_index="https://www.olbg.com/sitemap.xml",
        sitemap_betting_tips="https://www.olbg.com/sitemap-betting-tips.xml",
        sport_hub_pattern="https://www.olbg.com/betting-tips/{Sport}/{sport_id}",
        event_pattern="https://www.olbg.com/betting-tips/{Sport}/{Region}/{Competition}/{Match}/{market_id}?event_id={event_id}",
        sports=[dict(name=n, sport_id=i, covered=c) for n, i, c in [
            ("Football", 1, False), ("Horse Racing", 2, False), ("Tennis", 3, True), ("Golf", 5, True),
            ("Rugby Union", 9, True), ("Rugby League", 10, True), ("American Football", 11, False),
            ("Baseball", 12, True), ("Ice Hockey", 13, True), ("Motor Racing", 14, True), ("Darts", 15, True),
            ("Boxing", 16, False), ("Cycling", 17, False), ("Handball", 20, True), ("Volleyball", 21, True),
            ("Aussie Rules", 22, False), ("eSports", 23, True), ("Gaelic Football", 25, False),
            ("Greyhounds", 28, False)]],
        markets_by_sport=MARKET_MAP,
    )
    with open(os.path.join(DATA, "olbg-structure-aa4e9dbf.json"), "w") as f:
        json.dump(structure, f, indent=1, ensure_ascii=False)

    # ---------- stats ----------
    n_total = len(ALL)
    n_ver = sum(1 for x in ALL if x["ver"] == "verified")
    n_part = sum(1 for x in ALL if x["ver"] == "partial")
    n_unver = sum(1 for x in ALL if x["ver"] == "unverified")
    hi = [x for x in ALL if (x.get("pick") or {}).get("conf") == "high"]
    n_flagged = sum(1 for x in ALL if any(is_review_flag(f) for f in x.get("flags", [])))
    n_lines = sum(1 for x in ALL if (x.get("line") or {}).get("ml") or (x.get("line") or {}).get("outright"))
    n_picks = sum(1 for x in ALL if (x.get("pick") or {}).get("sel"))

    # ---------- landing ----------
    cards = "".join(f"""<div class="card sportcard">
<div><a class="stitle" href="{slug}.html">{name}</a></div>
<div class="counts">{len([x for x in ALL if x['sport']==name])} events &middot;
{len([x for x in ALL if x['sport']==name and x['ver']=='verified'])} fully verified &middot;
{len([x for x in ALL if x['sport']==name and (x.get('pick') or {}).get('conf')=='high'])} high-confidence</div>
<div>{''.join(f'<span class="pill">{e(m.split(" (")[0])}</span>' for m in (ALL and next((x['mk'][:3] for x in ALL if x['sport']==name), [])))}</div>
</div>""" for slug, name in SPORTS)

    body = f"""
<div class="kicker">Independent coverage of OLBG-listed sports</div>
<h1>Match list, originated lines &amp; confidence-rated picks</h1>
<p class="lead">We reverse-engineered OLBG.com's sport taxonomy and event URLs, harvested every listed event for the
sports we cover (all exclusions applied), re-verified each fixture against official sources, originated our own
betting lines for every market type we cover, and assigned a match-winner pick with a low/medium/high confidence
label. Every table row links to an official source; anything we could not confirm is left blank and flagged.</p>
<div class="grid cards" style="margin-top:18px">
<div class="card"><div class="big">{n_total}</div><div class="sub">events tracked across {len(SPORTS)} sports</div></div>
<div class="card"><div class="big">{n_ver}/{n_total}</div><div class="sub">verified directly from official sources</div></div>
<div class="card"><div class="big">{n_part}</div><div class="sub">partially verified (league page linked, detail cross-checked)</div></div>
<div class="card"><div class="big">{n_unver}</div><div class="sub">unverified &rarr; left blank &amp; <a href="flagged.html">flagged</a></div></div>
<div class="card"><div class="big">{n_lines}</div><div class="sub">events with our own originated line</div></div>
<div class="card"><div class="big">{n_picks}</div><div class="sub">picks with confidence labels</div></div>
<div class="card"><div class="big" style="color:var(--hi)">{len(hi)}</div><div class="sub">high-confidence picks with written predictions (<a href="predictions.html">read</a>)</div></div>
<div class="card"><div class="big" style="color:var(--warn)">{n_flagged}</div><div class="sub">rows carrying flags for review (<a href="flagged.html">review</a>)</div></div>
</div>
<h2>Browse by sport</h2>
<div class="grid cards">{cards}</div>
<h2>Scope decisions at a glance</h2>
<p><strong>Covered:</strong> {", ".join(n for _, n in SPORTS)}.
<strong>Excluded per requirements:</strong> soccer/football, boxing, UFC/MMA, American football, hurling, horse racing, cycling, specials.
<strong>Also excluded (flagged judgment calls):</strong> Gaelic Football, Aussie Rules (football codes), Greyhounds (animal racing).
See the <a href="flagged.html">Flagged for Review</a> page and <a href="methodology.html">Methodology</a> for details.</p>
"""
    with open(os.path.join(DOCS, "index.html"), "w") as f:
        f.write(page("Home", body))

    # ---------- sport pages ----------
    for slug, name in SPORTS:
        evs = [x for x in ALL if x["sport"] == name]
        nv = len([x for x in evs if x["ver"] == "verified"])
        nhi = [x for x in evs if (x.get("pick") or {}).get("conf") == "high"]
        body = f"""
<div class="kicker">Sport</div>
<h1>{e(name)}</h1>
<p class="lead">{len(evs)} events captured from the OLBG {e(name)} hub on {CAPTURED}.
{nv} verified directly from official sources. OLBG markets for this sport: {e(MARKET_MAP.get(name, ''))}.
Our lines below are independently originated fair prices (no bookmaker margin) - see <a href="methodology.html">methodology</a>.</p>
<div class="statrow" style="margin:12px 0 16px">
<span class="pill">{len(evs)} events</span><span class="pill">{nv} verified</span>
<span class="pill">{len(nhi)} high-confidence</span>
<span class="pill">{len([x for x in evs if any(is_review_flag(f) for f in x.get('flags', []))])} flagged for review</span></div>
<h2>Match board</h2>
{sport_table(evs)}
<h2>Notes</h2>
<ul class="plain">
<li>Status column meaning: "Pre-match" = scheduled after capture; "Near start / in play" = listed by OLBG with a morning tip time that had passed or was about to pass at capture - check the source link for the result.</li>
<li>"blank" cells mean the value could not be confirmed from an official source and was deliberately not filled - see <a href="flagged.html">Flagged for Review</a>.</li>
</ul>
"""
        with open(os.path.join(DOCS, slug + ".html"), "w") as f:
            f.write(page(name, body))

    # ---------- predictions ----------
    cards_html = ""
    for ev in hi:
        facts = "".join(f'<li>{e(t)} <a href="{e(u)}" target="_blank" rel="noopener">[source]</a></li>' for t, u in ev.get("facts", []))
        olbg = f'<a href="{e(ev["olbg"])}" target="_blank" rel="noopener">OLBG event</a>' if ev.get("olbg") else ""
        cards_html += f"""<div class="predict-card">
<div class="kicker">High-confidence pick</div>
<h2 style="margin:4px 0">{e(ev['ev'])}</h2>
<div class="meta">{e(ev['comp'])} &middot; {e(ev.get('dt',''))} &middot; {e(ev.get('vn',''))}</div>
<div><strong>Selection: {e(ev['pick']['sel'])}</strong> &nbsp;{conf_badge('high')}</div>
<div class="meta">Our line: {line_text(ev.get('line'))}</div>
<p class="body">{e(ev['pred'])}</p>
<ul class="facts">{facts}</ul>
<div class="meta" style="margin-top:8px">Official source: <a href="{e(ev.get('url',''))}" target="_blank" rel="noopener">{e(ev.get('src',''))}</a> &middot; {olbg}</div>
</div>"""
    body = f"""
<div class="kicker">Analysis</div>
<h1>High-confidence predictions</h1>
<p class="lead">Every pick on the sport pages carries a low/medium/high confidence label. The {len(hi)} selections below
earned a <strong>high</strong> label: the supporting facts were verified against official sources or multiple corroborating
listings, and the competitive gap is demonstrable rather than assumed. Each write-up states plainly what the betting
selection is. Medium and low picks deliberately get no write-up - the evidence base is thinner and we won't dress it up.</p>
{cards_html}
"""
    with open(os.path.join(DOCS, "predictions.html"), "w") as f:
        f.write(page("Predictions", body))

    # ---------- flagged ----------
    rows = ""
    for i, ev in enumerate([x for x in ALL if x.get("flags")], 1):
        fl = "".join(f'<li>{e(f)}</li>' for f in ev["flags"])
        src = f'<a href="{e(ev["url"])}" target="_blank" rel="noopener">{e(ev.get("src") or "link")}</a>' if ev.get("url") else '<span class="blank">no official link captured</span>'
        rows += f"""<tr><td>{i}</td><td><strong>{e(ev['ev'])}</strong><div style="color:var(--mut);font-size:12px">{e(ev['sport'])} &middot; {e(ev['comp'])}</div></td>
<td><ul class="plain" style="margin:0">{fl}</ul></td><td>{src}</td></tr>"""
    body = f"""
<div class="kicker">Transparency</div>
<h1>Flagged for Review</h1>
<p class="lead">Nothing on this page blocks anything - it exists so you can audit our judgment calls and every value we
could not confirm from an official source. Items marked UNVERIFIED have blank data fields by design: we never infer
or fill in values.</p>
<h2>Interpretation decisions (exclusion list)</h2>
<table><thead><tr><th>OLBG sport</th><th>Decision</th></tr></thead><tbody>
{''.join(f'<tr><td>{e(n)}</td><td>{e(d)}</td></tr>' for n, d in EXCLUDED)}
</tbody></table>
<h2>Site irregularities found while reverse-engineering OLBG</h2>
<ul class="plain">
<li><strong>OLBG start-time bug (systematic):</strong> OLBG's displayed event times are inconsistent across sports. Examples captured on 21 Oct 2026:
NBA Bucks@Wizards shown "Today 19:10" vs official 7:00 PM ET (= midnight UK); NHL Flyers@Sabres shown "Tomorrow 00:37" vs official 7:30 PM ET (= 00:30 UK);
F1 US GP shown "25 Oct 16:00" vs official 20:00 GMT; darts shown "Tomorrow 13:15" vs ~18:00 UK session start; snooker shown "05:00" vs 10:00 UK.
By contrast, Austrian ICEHL and several tennis times matched UK time exactly. Treat OLBG times as unreliable; all times on this site come from official sources.</li>
<li><strong>Expired/in-play listings:</strong> the OLBG tennis hub listed matches with tip times that had already passed at capture (site has a "Show Expired Events" toggle). Statuses are marked accordingly.</li>
<li><strong>eSports hub empty:</strong> OLBG's eSports page showed "No tips found" on 21 Oct 2026 - no esports events included.</li>
<li><strong>Rugby League:</strong> no match-level events listed; only 2027 futures (Super League, NRL, State of Origin).</li>
<li><strong>EuroCup fixture conflict:</strong> OLBG lists U-BT Cluj-Napoca vs London Lions on 21 Oct while contemporaneous EuroCup schedules list London Lions vs Cedevita Olimpija that evening - flagged for review.</li>
<li><strong>OLBG Motor Racing content claim:</strong> OLBG's own F1 calendar text states the Bahrain Grand Prix is staged at Sepang in Malaysia for 2026 - an unusual claim we did not attempt to verify (irrelevant to the US GP pick) and flag purely as site-content irregularity.</li>
<li><strong>OLBG odd club name:</strong> OLBG lists a PlusLiga volleyball side as "Jelcz Laskowice", which does not match known 2026/27 PlusLiga club names - fixture identity flagged.</li>
</ul>
<h2>Row-level flags ({n_flagged} rows)</h2>
<div class="tblwrap"><table>
<thead><tr><th>#</th><th>Event</th><th>Flags</th><th>Official source (for review)</th></tr></thead>
<tbody>{rows}</tbody></table></div>
"""
    with open(os.path.join(DOCS, "flagged.html"), "w") as f:
        f.write(page("Flagged for Review", body))

    # ---------- methodology ----------
    body = f"""
<div class="kicker">How this was built</div>
<h1>Methodology &amp; OLBG reverse-engineering</h1>
<h2>1. Reverse-engineering OLBG.com</h2>
<ul class="plain">
<li>Sitemap index: <code>https://www.olbg.com/sitemap.xml</code> &rarr; sub-sitemaps including <code>sitemap-betting-tips.xml</code>.</li>
<li>Sport hub pattern: <code>https://www.olbg.com/betting-tips/{{Sport}}/{{sport_id}}</code> (e.g. <code>/betting-tips/Basketball/4</code>).</li>
<li>Event pattern: <code>https://www.olbg.com/betting-tips/{{Sport}}/{{Region}}/{{Competition}}/{{Match}}/{{market_id}}?event_id={{id}}</code>.</li>
<li>20+ sports identified with stable IDs: Football 1, Horse Racing 2, Tennis 3, Golf 5, Rugby Union 9, Rugby League 10,
American Football 11, Baseball 12, Ice Hockey 13, Motor Racing 14, Darts 15, Boxing 16, Cycling 17, Handball 20,
Volleyball 21, Aussie Rules 22, eSports 23, Gaelic Football 25, Greyhounds 28.</li>
<li>Per-sport market maps were extracted from OLBG's own help text and event pages (e.g. a tennis event page exposes
Win Match, Set Betting, 1st Set Winner, Games Won handicap and Total Games markets). Full map: <code>data/olbg-structure-aa4e9dbf.json</code>.</li>
<li>Harvest: each covered sport's hub page was read on {CAPTURED} and every listed event recorded with its OLBG event URL.</li>
</ul>
<h2>2. Verification standard</h2>
<ul class="plain">
<li><strong>verified</strong> - fixture confirmed on an official source (league/tour/federation/club site) whose content we captured.</li>
<li><strong>partial</strong> - competition/date confirmed via multiple independent listings with an official league page linked; some detail (exact tip time, standings) not captured.</li>
<li><strong>unverified</strong> - could not be confirmed from an official source: data fields left blank and the row flagged. We never infer or fill values.</li>
<li>Every fact used in a written prediction carries its own source link. Facts that only appear in secondary coverage (e.g. NHL team records from game previews) are marked as such in notes.</li>
</ul>
<h2>3. Originating our own lines</h2>
<ul class="plain">
<li>We do <strong>not</strong> copy bookmaker or exchange prices. Lines are fair (vig-free) estimates produced from verified inputs:
official standings and records, recent verified results, head-to-head records, seedings/rankings, and home advantage.</li>
<li>Method per market: win probability from a simple power rating built on the verified form above; expected margin &rarr; handicap line
(rounded to market-standard increments); expected scoring &rarr; totals line. Decimal prices = 1 / estimated probability.</li>
<li>Where verified inputs are thin (season openers, minor leagues), lines are labelled as indicative and the pick confidence drops accordingly - that is deliberate.</li>
<li>Outright markets (golf tournaments, F1 race/championship) use verified form (defending champions, standings, seedings) and are always low-to-medium confidence.</li>
</ul>
<h2>4. Confidence rubric</h2>
<ul class="plain">
<li><strong>High</strong> - multiple verified facts point the same way with a demonstrable gap (used for {len(hi)} picks; each has a written prediction).</li>
<li><strong>Medium</strong> - verified evidence favours the pick but with real competitive uncertainty.</li>
<li><strong>Low</strong> - thin evidence, coin-flip matchup, long-dated outright, or unverified fixture context. No write-up.</li>
</ul>
<h2>5. Limitations</h2>
<ul class="plain">
<li>Snapshot dataset: captured {CAPTURED}; fixtures/results move fast - always confirm at the linked official source.</li>
<li>NBA openers have no 2026-27 form data yet (season began 20-21 Oct 2026), so those picks are capped at medium/low.</li>
<li>OLBG's own displayed times are unreliable (see <a href="flagged.html">flagged irregularities</a>); all times here are from official sources where captured.</li>
<li>Generated predictions are betting analysis, not guarantees. 18+; bet responsibly.</li>
</ul>
"""
    with open(os.path.join(DOCS, "methodology.html"), "w") as f:
        f.write(page("Methodology", body))

    print(f"events={n_total} verified={n_ver} partial={n_part} unverified={n_unver} lines={n_lines} picks={n_picks} high={len(hi)} flaggedrows={n_flagged}")

if __name__ == "__main__":
    build()
