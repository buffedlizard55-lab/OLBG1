#!/usr/bin/env python3
"""T66 / 8f6d7364 — static dashboard builder (writes 8f6d7364/**.html)."""
import json, os, html, re as _re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "8f6d7364")
SITE = os.path.join(ROOT, "8f6d7364")
FX = json.load(open(os.path.join(D, "fixtures.json")))
SRC = json.load(open(os.path.join(D, "sources.json")))
FLG = json.load(open(os.path.join(D, "flagged.json")))
LN = json.load(open(os.path.join(D, "lines.json")))
PR = json.load(open(os.path.join(D, "predictions.json")))
HV = json.load(open(os.path.join(D, "harvest.json")))

SPORTS = [
    ("ice-hockey", "Ice Hockey"), ("baseball", "Baseball"), ("basketball", "Basketball"),
    ("tennis", "Tennis"), ("cricket", "Cricket"), ("rugby-league", "Rugby League"),
    ("rugby-union", "Rugby Union"), ("golf", "Golf"), ("motor-racing", "Motor Racing"),
    ("darts", "Darts"), ("handball", "Handball"), ("volleyball", "Volleyball"),
    ("aussie-rules", "Aussie Rules"), ("esports", "eSports"), ("gaelic-football", "Gaelic Football"),
    ("greyhounds", "Greyhounds"), ("snooker", "Snooker"),
]
EXCLUDED = [("soccer / football", "excluded by brief"), ("American football", "excluded by brief"),
            ("boxing", "excluded by brief"), ("UFC / MMA", "excluded by brief"),
            ("hurling", "excluded by brief"), ("horse racing", "excluded by brief"),
            ("cycling", "excluded by brief"), ("specials", "excluded by brief")]
GEN = FX["generated_at"]
LINES_BY = {f["id"]: f for f in LN["fixtures"]}
FIX_BY = {f["id"]: f for f in FX["fixtures"]}
SRC_BY = {s["id"]: s for s in SRC["sources"]}

CSS = """
:root{--bg:#0f1420;--panel:#171d2c;--panel2:#1d2436;--line:#2a3350;--txt:#e7ecf6;--mut:#9aa7c4;
--acc:#5aa9ff;--ok:#2fbf71;--warn:#e8b03a;--bad:#e05d5d;--high:#ff7a59;--med:#5aa9ff;--low:#8a94ad;}
*{box-sizing:border-box}body{margin:0;font:15px/1.5 system-ui,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--txt)}
a{color:var(--acc);text-decoration:none}a:hover{text-decoration:underline}
header{background:var(--panel);border-bottom:1px solid var(--line);padding:14px 22px;position:sticky;top:0;z-index:5}
header h1{font-size:18px;margin:0}header .sub{color:var(--mut);font-size:12.5px}
nav{background:var(--panel2);border-bottom:1px solid var(--line);padding:8px 22px;position:sticky;top:57px;z-index:4}
nav a{margin-right:14px;font-size:13.5px;color:var(--mut)}nav a.on{color:var(--txt);font-weight:600}
main{max-width:1280px;margin:18px auto;padding:0 18px 60px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;margin:14px 0 20px}
.tile{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.tile b{display:block;font-size:22px}.tile span{color:var(--mut);font-size:12px}
h2{font-size:17px;margin:26px 0 10px}h3{font-size:15px;margin:18px 0 8px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:12px 0}
table{border-collapse:collapse;width:100%;font-size:13.2px;background:var(--panel);border:1px solid var(--line)}
th{background:var(--panel2);text-align:left;padding:8px 9px;border-bottom:1px solid var(--line);position:sticky;top:0}
td{padding:7px 9px;border-bottom:1px solid var(--line);vertical-align:top}
tr:last-child td{border-bottom:none}td.num,th.num{text-align:right;white-space:nowrap}
.bad{display:inline-block;padding:1px 8px;border-radius:10px;font-size:11.5px;font-weight:600;white-space:nowrap}
.v{background:#123826;color:#7ee2b0;border:1px solid #1f5c3f}.u{background:#3a2a12;color:#f3cf7e;border:1px solid #6b4d1d}
.nv{background:#33161a;color:#f0a1a1;border:1px solid #6b2b31}
.high{background:#40201a;color:#ff9c80;border:1px solid #7a3b2e}.med{background:#152a44;color:#9cc7ff;border:1px solid #2b4a75}
.low{background:#242a38;color:#b7c0d6;border:1px solid #3a4258}
.mut{color:var(--mut)}.mono{font-family:ui-monospace,Consolas,monospace;font-size:12.5px}
.note{background:#14203a;border:1px solid #27406e;border-radius:8px;padding:10px 12px;margin:10px 0;font-size:13.4px}
.warnbox{background:#2b2210;border:1px solid #6b541d;border-radius:8px;padding:10px 12px;margin:10px 0;font-size:13.4px}
footer{color:var(--mut);font-size:12px;padding:20px;text-align:center;border-top:1px solid var(--line);margin-top:30px}
.pill{display:inline-block;background:var(--panel2);border:1px solid var(--line);border-radius:8px;padding:8px 11px;margin:4px 6px 4px 0;font-size:12.6px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px}@media(max-width:900px){.grid2{grid-template-columns:1fr}}
@media(max-width:760px){table{font-size:12px}th,td{padding:5px 6px}}
"""

NAV = [("index.html", "Dashboard"), ("matches.html", "Matches"), ("markets.html", "Markets"),
       ("high-confidence.html", "High confidence"), ("predictions.html", "Predictions"),
       ("analysis.html", "Analysis"), ("flagged.html", "Flagged"), ("sources.html", "Sources"),
       ("methodology.html", "Methodology")]

def esc(x):
    return html.escape(str(x)) if x is not None else ""

def page(name, title, body, active=None):
    active = active or name
    links = "".join(f'<a href="{h}"{" class=on" if h==active or h.startswith(active.split("/")[0]) else ""}>{esc(t)}</a>'
                    for h, t in NAV)
    sport_links = "".join(f'<a href="sports/{s}.html"{" class=on" if active==f"sports/{s}.html" else ""}>{esc(t)}</a>'
                          for s, t in SPORTS)
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · OLBG desk 8f6d7364 (T66)</title><style>{CSS}</style></head><body>
<header><h1>OLBG research desk · session 8f6d7364 (T66)</h1>
<div class="sub">Fresh 22 Oct 2026 21:00Z harvest · 17 in-scope sports · official-source verified line by line · generated {esc(GEN)} · not affiliated with OLBG · no betting advice</div></header>
<nav>{links}</nav>
<nav style="top:99px">{sport_links}</nav>
<main>{body}</main>
<footer>T66 · <span class="mono">data/8f6d7364</span> · every row links an official source or is flagged unverified · model values are estimates, never sourced facts</footer>
</body></html>"""
    if name.startswith("sports/"):
        doc = _re.sub(r'href="(?!https?://|mailto:|data:|#|\.\./)', r'href="../', doc)
    path = os.path.join(SITE, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(doc)

def badge_ver(f):
    if f["discovery"] == "olbg":
        return '<span class="bad v">official-verified</span>'
    if f["discovery"] == "official-only":
        return '<span class="bad v">official-verified · OLBG gap</span>'
    return '<span class="bad u">unverified — blank + flagged</span>'

def badge_tier(fr):
    if not fr:
        return '<span class="mut">not priced</span>'
    t = fr["tier"]
    cls = {"High": "high", "Medium": "med", "Low": "low"}[t]
    return f'<span class="bad {cls}">{t}</span>'

def src_links(f):
    out = []
    for sid in f["sources"]:
        s = SRC_BY.get(sid)
        if s:
            out.append(f'<a href="{esc(s["url"])}" title="{esc(s["org"])} · observed {esc(s["observed"])}">{esc(sid)}</a>')
    if not out:
        return '<span class="mut">none — discovery only</span>'
    return ", ".join(out)

def olbg_cell(f):
    o = f.get("olbg")
    if not o:
        return '<span class="mut">— (official-only listing)</span>' if f["discovery"] == "official-only" else ""
    return (f'<a href="{esc(o["hub_url"])}">OLBG hub</a> <span class="mono">#{o["event_id"]}</span><br>'
            f'<span class="mut">“{esc(o["time_text"])}” · top pick {esc(o["top_pick"])} ({esc(o["tips"])}, {esc(o["tips_pct"])}%)</span>')

def time_cell(f):
    bits = []
    if f["date"]:
        bits.append(f'<b>{esc(f["date"])}</b>')
    if f["start_utc"]:
        bits.append(f'<span class="mono">{esc(f["start_utc"])}</span>')
    if f["time_text"]:
        bits.append(f'<span class="mut">{esc(f["time_text"])}</span>')
    if f.get("venue"):
        bits.append(f'<span class="mut">{esc(f["venue"])}</span>')
    if not bits:
        return '<span class="bad u">blank</span> <span class="mut">see flags</span>'
    return "<br>".join(bits)

def flag_cell(f):
    if not f["flags"]:
        return ""
    return " ".join(f'<a href="flagged.html#{esc(x)}" class="bad u" title="{esc(x)}">{esc(x.replace("F-8F6D-",""))}</a>'
                    for x in f["flags"])

def match_rows(rows, show_sport=True):
    tr = []
    for f in rows:
        fr = LINES_BY.get(f["id"])
        pick = (f'{esc(fr["pick"])} <span class="mono">{fr["pick_p"]:.3f} ({fr["pick_american"]:+.1f})</span><br>'
                if fr else "")
        comp = esc(f["competition"])
        a, b = esc(f["participant_a"] or "?"), esc(f["participant_b"] or "?")
        match = f"<b>{a}</b> v <b>{b}</b>" if f["participant_a"] and f["participant_b"] else \
                f'<span class="mut">{a if f["participant_a"] else "—"} v {b if f["participant_b"] else "—"}</span>'
        sp = f"<td>{esc(f['sport_name'])}</td>" if show_sport else ""
        tr.append(f'<tr id="{esc(f["id"])}"><td class="mono">{esc(f["id"])}</td>{sp}<td>{comp}<br>{match}</td>'
                  f'<td>{time_cell(f)}</td><td>{olbg_cell(f)}</td>'
                  f'<td>{badge_ver(f)}<br>{src_links(f)}</td>'
                  f'<td>{badge_tier(fr)}<br>{pick}<span class="mut">{esc(fr["priceable_note"]) if fr else esc("; ".join(f["notes"])[:170] or "—")}</span></td>'
                  f'<td>{flag_cell(f)}</td></tr>')
    return ("<table><tr><th>id</th>" + ('<th>sport</th>' if show_sport else "") +
            "<th>competition / match</th><th>official date / start</th><th>OLBG discovery</th>"
            "<th>verification + official source</th><th>our line / pick</th><th>flags</th></tr>"
            + "".join(tr) + "</table>")

os.makedirs(SITE, exist_ok=True)
os.makedirs(os.path.join(SITE, "sports"), exist_ok=True)

# ----------------------------------------------------------------- index ----
ver = sum(1 for f in FX["fixtures"] if f["verified"])
unv = len(FIXTURES_UNVER := [f for f in FX["fixtures"] if not f["verified"]])
c = LN["counts"]
cov_rows = []
for slug, name in SPORTS:
    rows = [f for f in FX["fixtures"] if f["sport"] == slug]
    pr = [f for f in rows if f["id"] in LINES_BY]
    hi = sum(1 for f in pr if LINES_BY[f["id"]]["tier"] == "High")
    st = "no listings from either source — coverage gap (flagged)" if not rows else \
         f"{len(rows)} rows · {sum(1 for f in rows if f['verified'])} official-verified · {len(pr)} priced"
    cov_rows.append(f'<tr><td><a href="sports/{slug}.html">{esc(name)}</a></td><td>{esc(st)}</td>'
                    f'<td class="num">{hi}</td></tr>')
body = f"""
<div class="tiles">
<div class="tile"><b>{len(FX['fixtures'])}</b><span>fixture rows (window 22–29 Oct)</span></div>
<div class="tile"><b>{ver}</b><span>official-verified rows</span></div>
<div class="tile"><b>{unv}</b><span>unverified (blank + flagged)</span></div>
<div class="tile"><b>{c['priced_fixtures']}</b><span>fixtures with our own lines</span></div>
<div class="tile"><b>{c['High']}</b><span>High picks (−250…+10000 gate)</span></div>
<div class="tile"><b>{c['Medium']}</b><span>Medium</span></div>
<div class="tile"><b>{c['Low']}</b><span>Low</span></div>
<div class="tile"><b>{len(PR['predictions'])}</b><span>hand-written predictions</span></div>
<div class="tile"><b>{c['out_of_window_ge70']}</b><span>≥70% but outside window (disclosed)</span></div>
<div class="tile"><b>{SRC['count']}</b><span>official / discovery sources</span></div>
<div class="tile"><b>{FLG['count']}</b><span>flags on the Flagged page</span></div>
<div class="tile"><b>17</b><span>in-scope sports (8 excluded)</span></div>
</div>
<div class="note"><b>What this is.</b> A fresh reverse-engineered discovery pass of OLBG's 17 in-scope sport hubs
(fetched {esc(HV['fetched_window_utc'])}), re-verified line by line against league/governing-body pages fetched by this
session the same evening. OLBG is discovery only — times, picks and tip counts there are never promoted to facts.
Every published value either carries an <a href="sources.html">official source link with its observation window</a>
or is left blank and listed on the <a href="flagged.html">Flagged for Review</a> page. Our prices are model
estimates (<a href="methodology.html">methodology</a>); High = model p ≥ 0.70 with a fair price inside
−250…+10000 on a verified fixture, and every ≥70% favourite that the window excludes is disclosed on
<a href="high-confidence.html">High confidence</a> instead of being quietly dropped.</div>
<h2>Coverage by sport</h2>
<table><tr><th>sport</th><th>status</th><th class="num">High</th></tr>{"".join(cov_rows)}</table>
<h2>Excluded by the brief (not harvested)</h2>
<div>{"".join(f'<span class="pill">{esc(a)} — {esc(b)}</span>' for a,b in EXCLUDED)}</div>
<h2>Start here</h2>
<div class="pill"><a href="matches.html">All 134 matches</a></div>
<div class="pill"><a href="high-confidence.html">High-confidence gate + ≥70% ledgers</a></div>
<div class="pill"><a href="predictions.html">{len(PR['predictions'])} predictions</a></div>
<div class="pill"><a href="markets.html">Every market we investigated</a></div>
<div class="pill"><a href="analysis.html">Analysis &amp; findings</a></div>
<div class="pill"><a href="flagged.html">{FLG['count']} flagged items</a></div>
"""
page("index.html", "Dashboard", body, "index.html")

# --------------------------------------------------------------- matches ----
ordered = sorted(FX["fixtures"], key=lambda f: (f["sport_name"], f["date"] or "9999", f["id"]))
body = (f"<h2>All fixtures — {len(FX['fixtures'])} rows</h2>"
        f'<div class="note">72 rows were discovered on OLBG and then verified against official sources; '
        f'29 rows exist only on official sources (OLBG visible capture missed them, flag F-8F6D-12); '
        f'33 rows could not be confirmed officially and keep blank official fields with flags.</div>'
        + match_rows(ordered))
page("matches.html", "Matches", body)

# --------------------------------------------------------------- markets ----
mrows = []
for fr in LN["fixtures"]:
    f = FIX_BY[fr["id"]]
    for m in fr["markets"]:
        win = '<span class="bad v">in window</span>' if m["in_window"] else '<span class="bad u">outside</span>'
        tier = "high" if (m["p"] >= 0.70 and m["in_window"] and f["verified"]) else ("med" if m["p"] >= .55 else "low")
        mrows.append(f'<tr><td class="mono">{esc(fr["id"])}</td><td>{esc(fr["competition"])}<br>'
                     f'<span class="mut">{esc(f["participant_a"])} v {esc(f["participant_b"])}</span></td>'
                     f'<td>{esc(m["market"])}</td><td><b>{esc(m["selection"])}</b></td>'
                     f'<td class="num">{m["p"]:.4f}</td><td class="num">{m["fair_decimal"]:.4f}</td>'
                     f'<td class="num">{m["fair_american"]:+.1f}</td>'
                     f'<td class="num">{esc(m["line"]) if m["line"] is not None else "—"}</td>'
                     f'<td>{win}</td><td><span class="bad {tier}">{"High" if tier=="high" else ("Medium" if tier=="med" else "Low")}</span></td>'
                     f'<td class="mut">{esc(m["note"])}</td></tr>')
inv_rows = []
for slug, name in SPORTS:
    rows = [f for f in FX["fixtures"] if f["sport"] == slug]
    if not rows:
        inv_rows.append(f'<tr><td>{esc(name)}</td><td class="num">0</td><td class="num">0</td>'
                        f'<td colspan="3">no fixtures from either source — flagged coverage gap</td></tr>')
        continue
    priced = [f for f in rows if f["id"] in LINES_BY]
    mset = sorted({m["market"] for f in priced for m in LINES_BY[f["id"]]["markets"]})
    unpr = [u for u in LN["ledgers"]["unpriced"] if u["sport"] == slug]
    reason = unpr[0]["reason"] if unpr and len(unpr) == len(rows) - 0 and not priced else \
             ("winner priced; other markets per notes" if priced else (unpr[0]["reason"] if unpr else "—"))
    inv_rows.append(f'<tr><td><a href="sports/{slug}.html">{esc(name)}</a></td>'
                    f'<td class="num">{len(rows)}</td><td class="num">{len(priced)}</td>'
                    f'<td>{", ".join(mset) or "—"}</td><td class="mut">{esc(reason)}</td></tr>')
body = f"""
<h2>Market investigation matrix</h2>
<div class="note">The brief asks us to investigate every available market. For each sport we either priced a market
from an official strength input or record it here as <b>investigated, not priced</b> with the missing official input
named — we never invent a line without one.</div>
<table><tr><th>sport</th><th class="num">rows</th><th class="num">priced</th><th>markets we priced</th><th>notes / why not priced</th></tr>
{"".join(inv_rows)}</table>
<h2>Every priced selection ({sum(len(f["markets"]) for f in LN["fixtures"])} outcomes)</h2>
<div class="warnbox">Our prices are <b>model estimates</b> (zero margin, fair 1/p). They are not bookmaker quotes and
are not offered as available anywhere. The only market quotes shown anywhere on this desk are the NHL API's
officially embedded odds, on the <a href="analysis.html">Analysis</a> page, labelled as a cross-check.</div>
<table><tr><th>id</th><th>match</th><th>market</th><th>selection</th><th class="num">p</th><th class="num">fair dec</th>
<th class="num">fair am</th><th class="num">line</th><th>window</th><th>tier</th><th>model note</th></tr>
{"".join(mrows)}</table>
"""
page("markets.html", "Markets", body)

# ------------------------------------------------- high-confidence ----------
hs = []
for h in LN["ledgers"]["high_selections"]:
    f = FIX_BY[h["fixture_id"]]
    pr = next((p for p in PR["predictions"] if p["fixture_id"] == h["fixture_id"]), None)
    hs.append(f'<div class="card"><span class="bad high">HIGH</span> <b>{esc(h["match"])}</b> '
              f'<span class="mut">({esc(h["competition"])})</span><br>'
              f'Selection: <b>{esc(h["selection"])}</b> ({esc(h["market"])})'
              + (f' · line {esc(h["line"])}' if h.get("line") is not None else "") +
              f' · model p = <b>{h["p"]:.6f}</b> · fair <span class="mono">{h["fair_decimal"]:.4f} / {h["fair_american"]:+.1f}</span>'
              f' <span class="bad v">in −250…+10000</span><br>'
              f'<span class="mut">Fixture officially verified via {src_links(f)}</span><br>'
              + (f'<a href="predictions.html#{esc(pr["id"])}">→ prediction {esc(pr["id"])}</a>' if pr else "") +
              f'</div>')
ow = "".join(
    f'<tr><td class="mono">{esc(o["fixture_id"])}</td><td>{esc(o["competition"])}<br>{esc(o["match"])}</td>'
    f'<td>{esc(o["market"])}</td><td><b>{esc(o["selection"])}</b></td><td class="num">{o["p"]:.4f}</td>'
    f'<td class="num">{o["fair_american"]:+.1f}</td>'
    f'<td><span class="bad nv">outside −250 → not High</span></td>'
    f'<td class="mut">p ≥ 0.70 but the fair price is shorter than −250; disclosed per the brief window rule (F-8F6D-16)</td></tr>'
    for o in LN["ledgers"]["out_of_window_ge70_winners"])
nb = "".join(
    f'<tr><td class="mono">{esc(o["fixture_id"])}</td><td>{esc(o["match"])}</td><td><b>{esc(o["selection"])}</b></td>'
    f'<td class="num">{o["p"]:.4f}</td><td class="num">{o["fair_american"]:+.1f}</td>'
    f'<td class="mut">watch list: p in [0.685, 0.700) — below the High gate</td></tr>'
    for o in LN["ledgers"]["near_band_winners_685_700"])
body = f"""
<h2>The High gate</h2>
<div class="note"><b>High = model p ≥ 0.70 AND fair American price inside −250…+10000 AND the fixture is
officially verified.</b> Boundary decisions use p rounded to six decimals. The brief notes that many high-confidence
picks are simply &gt;70% chances between −250 and +10000 — that literal conjunction is narrow by construction:
p ≥ 0.70 maps to −233 or shorter, while the window stops at −250 (p = 71.43%), so a favourite must land between
70.00% and 71.43% to qualify. We publish exactly what lands there, and disclose everything the conjunction
excludes below rather than stretching the gate.</div>
<h2>High picks ({c['High']} fixtures · {c['high_selections']} selections)</h2>
{"".join(hs) if hs else "<p>None.</p>"}
<h2>≥70% winners outside the price window — disclosed, never labelled High ({len(LN['ledgers']['out_of_window_ge70_winners'])})</h2>
<table><tr><th>id</th><th>match</th><th>market</th><th>selection</th><th class="num">p</th><th class="num">fair am</th><th>status</th><th>why</th></tr>{ow}</table>
<h2>Near-band watch list ({len(LN['ledgers']['near_band_winners_685_700'])})</h2>
<table><tr><th>id</th><th>match</th><th>selection</th><th class="num">p</th><th class="num">fair am</th><th>note</th></tr>{nb}</table>
<h2>Market-price reading (official NHL embedded odds)</h2>
<div class="note">The brief also frames confidence as &gt;70% <i>by market prices</i>. The only official market quotes
we hold are the NHL API's embedded odds; after de-vigging the American providers, <b>no
tonight's game reaches 70%</b> (max: New Jersey ≈ 0.66). Full cross-check table on
<a href="analysis.html">Analysis</a>.</div>
"""
page("high-confidence.html", "High confidence", body)

# ------------------------------------------------------------ predictions ----
pcards = []
for p in PR["predictions"]:
    facts = "".join(f'<li>{esc(p_["fact"])} — <a href="{esc(p_["source"])}">official source</a> '
                    f'<span class="mut">(observed {esc(p_["observed"])})</span></li>' for p_ in p["facts"])
    links = " · ".join(f'<a href="{esc(u)}">{esc(u[:64])}{"…" if len(u)>64 else ""}</a>' for u in p["official_links"])
    pcards.append(f"""
<div class="card" id="{esc(p['id'])}">
<span class="bad high">HIGH</span> <b>{esc(p['id'])}</b> · {esc(p['match'])} · {esc(p['competition'])}<br>
<span class="mut">Selection: <b>{esc(p['selection'])}</b> · model p {p['model_p']:.6f} · fair {p['fair_american']:+.1f} · kickoff {esc(p.get('kickoff_utc') or p.get('kickoff'))}</span>
<h3>Prediction <span class="mut">({p['word_count']} words, hand-written)</span></h3>
<p style="font-size:15.2px;line-height:1.65">{esc(p['prose'])}</p>
<h3>Facts behind it (each from an official page read this session)</h3>
<ul style="font-size:13.3px">{facts}</ul>
<div class="mut" style="font-size:12.6px">Sources: {links}</div>
</div>""")
body = (f"<h2>High-confidence predictions ({len(PR['predictions'])})</h2>"
        f'<div class="note">One unique prediction per High pick — team, current form, recent match history and an '
        f'explicit selection, with every factual clause mapped to an official source read this session. '
        f'No sentence is shared with any other prediction (six-gram check in the validator).</div>'
        + "".join(pcards))
page("predictions.html", "Predictions", body)

# -------------------------------------------------------------- analysis ----
xrows = "".join(
    f'<tr><td>{esc(x["match"])}</td>'
    f'<td class="num">{x["model"].get(FIX_BY[x["fixture_id"]]["participant_a"], "—"):.3f} / '
    f'{x["model"].get(FIX_BY[x["fixture_id"]]["participant_b"], "—"):.3f}</td>'
    f'<td class="num">{x["official_devig"].get(FIX_BY[x["fixture_id"]]["participant_a"], "—"):.3f} / '
    f'{x["official_devig"].get(FIX_BY[x["fixture_id"]]["participant_b"], "—"):.3f}</td>'
    f'<td class="mut">our model vs de-vigged official embedded odds (providers 7/8/9)</td></tr>'
    for x in LN["ledgers"]["nhl_official_market_cross_check"])
conv = [f["id"] for f in FX["fixtures"] if "F-8F6D-01" in f["flags"]]
body = f"""
<h2>Findings (this session)</h2>
<div class="card"><b>1. OLBG time-zone conventions are inconsistent across sports</b> (F-8F6D-01, high).
Official times were compared against OLBG's displayed text hub by hub: NHL/MLB/tennis/darts text tracks
US Eastern (and carries a small start pad: NBA +10 min, NHL +7 min vs official nominal times), EuroLeague text
equals BST exactly, rugby-union text equals venue-local times exactly. Official UTC values are published;
OLBG text stays in the discovery column. Rows touched: {len(conv)}.</div>
<div class="card"><b>2. The brief's literal High conjunction (≥70% AND −250…+10000) is a knife edge.</b>
Favourites above 71.43% are priced shorter than −250 and therefore excluded; favourites below 70% fail the first
test. Tonight's verified, priced board ({c['priced_fixtures']} fixtures) yields {c['High']} High selections,
{c['out_of_window_ge70']} disclosed ≥70% out-of-window winners and {c['near_band']} near-band watch items.
Nothing was nudged across the boundary.</div>
<div class="card"><b>3. No tonight's NHL game reaches 70% by the official embedded market either</b> —
the strongest de-vigged quote is New Jersey ≈ 0.66. The model and the official market agree on direction in
most games but diverge most on NY Islanders (model 0.78 vs market ≈0.53) and Minnesota (model 0.70 vs ≈0.65);
both readings are shown in the table below, and the model — not the market — decides our tiers.</div>
<div class="card"><b>4. Discovery gaps on both sides.</b> OLBG's visible hub list missed {29} fixtures that official
sources confirm (URC, Top 14, rugby-league World Cup, AFLW, snooker, MLB, GAA Kerry); conversely {unv} discovery
rows could not be confirmed officially and are published blank + flagged instead of quietly kept.</div>
<div class="card"><b>5. Source-health irregularities.</b> hbl.de no longer serves handball content (F-8F6D-06);
pdc.tv walls direct fetches behind consent (F-8F6D-03); nba.com, premrugby.com, WTA rankings and the ICC fixtures
page are JS-rendered and resist line-by-line fetch verification (F-8F6D-04/05); OLBG's own Rathgormack v The Nire
date contradicts the official Munster GAA calendar (F-8F6D-02).</div>
<h2>Model vs official embedded market — NHL (12 games)</h2>
<table><tr><th>match</th><th class="num">model p (a / b)</th><th class="num">official devig (a / b)</th><th>note</th></tr>{xrows}</table>
<h2>Cross-cutting counts</h2>
<div>
<span class="pill">verified rows {ver}</span><span class="pill">unverified rows {unv}</span>
<span class="pill">priced {c['priced_fixtures']}</span><span class="pill">unpriced {c['unpriced']}</span>
<span class="pill">High {c['High']}</span><span class="pill">Medium {c['Medium']}</span><span class="pill">Low {c['Low']}</span>
<span class="pill">markets priced {sum(len(f['markets']) for f in LN['fixtures'])}</span>
<span class="pill">flags {FLG['count']}</span><span class="pill">sources {SRC['count']}</span>
</div>
"""
page("analysis.html", "Analysis", body)

# --------------------------------------------------------------- flagged ----
frows = "".join(
    f'<tr id="{esc(fl["id"])}"><td class="mono"><b>{esc(fl["id"])}</b></td>'
    f'<td><span class="bad {"nv" if fl["severity"]=="high" else "u"}">{esc(fl["severity"])}</span></td>'
    f'<td><b>{esc(fl["title"])}</b><div class="mut" style="font-size:13px">{esc(fl["detail"])}</div>'
    + ('<div style="font-size:12.5px">' + " · ".join(f'<a href="{esc(u)}">source</a>' for u in fl["links"]) + "</div>" if fl["links"] else "")
    + (f'<div class="mut" style="font-size:12px">rows: {esc(", ".join(fl["rows"]))}</div>' if fl["rows"] else "")
    + "</td></tr>"
    for fl in FLG["flags"])
body = (f"<h2>Flagged for review ({FLG['count']})</h2>"
        '<div class="warnbox">Unverified values are <b>blank</b> in the tables, never inferred. Every flag below '
        'carries its official source link(s) so it can be checked by hand. Flagged items do not block publication '
        'of the rest of the desk.</div>'
        f"<table><tr><th>id</th><th>severity</th><th>finding</th></tr>{frows}</table>")
page("flagged.html", "Flagged for Review", body)

# --------------------------------------------------------------- sources ----
srows = "".join(
    f'<tr><td class="mono">{esc(s["id"])}</td><td>{esc(s["org"])}</td>'
    f'<td><a href="{esc(s["url"])}">{esc(s["url"])}</a></td>'
    f'<td><span class="bad {"v" if s["role"]=="official" else "u"}">{esc(s["role"])}</span></td>'
    f'<td class="mono" style="font-size:12px">{esc(s["observed"])}</td>'
    f'<td class="mut" style="font-size:12.5px">{esc(s["method"])}<br>{esc(s["note"])}</td></tr>'
    for s in SRC["sources"])
body = (f"<h2>Sources ({SRC['count']})</h2>"
        '<div class="note">Official = league / governing body / tour / promoter pages, fetched through the Arena '
        'page-fetch tool inside the observation windows shown. Discovery = OLBG (never a source of fact). '
        'Canonical same-day rows were captured by this repository\'s canonical session at 07:17–07:30Z today and '
        'are re-used only with that window disclosed.</div>'
        f"<table><tr><th>id</th><th>organisation</th><th>url</th><th>role</th><th>observed (UTC)</th><th>method / note</th></tr>{srows}</table>")
page("sources.html", "Sources", body)

# ---------------------------------------------------------- methodology ----
body = """
<h2>Methodology (model 8f6d7364-v1.0)</h2>
<div class="card"><b>Discovery.</b> All 17 in-scope OLBG hubs were fetched 22 Oct 20:50–20:57Z (chunk 0 of each
server-rendered page). OLBG event ids, displayed times, most-tipped selections and tip counts are stored as
discovery only. Tip counts are votes, never probabilities.</div>
<div class="card"><b>Verification.</b> Every published row links at least one official page (league, governing body,
tour or promoter) with the observation window recorded in <a href="sources.html">sources.json</a>. Values that
could not be confirmed are blank and listed on <a href="flagged.html">flagged.html</a>. UTC timestamps are either
printed by the source or derived arithmetically from an explicit timezone label (CEST/EDT/ET) or a page-stated
local-time convention with the venue's zone — never guessed; pages that print times with no zone keep text-only
times with a flag.</div>
<div class="card"><b>Origination (zero margin).</b> All prices are fair: decimal = 1/p, American derived from p.
Inputs, in order of preference: official season records (MLB), official standings/table records with Beta(2,2)
shrinkage (NHL, EuroLeague, URC, StarLigue), official table positions (Top 14, Pro D2 linear position model),
official IRL strength percentages (rugby league share model), official draws/seed slots (tennis Bradley-Terry,
γ=0.7 on ranks with documented ordinal defaults for unseeded players). Derived markets: MLB totals/margin from
paired season run rates (Poisson); URC totals/margin from official PF/PA (σ = 12 / 10 points, disclosed);
StarLigue totals/margin (σ = 8 / 6 goals, disclosed). A market without an official strength input is
investigated and recorded as not priced, with the missing input named — never filled in.</div>
<div class="card"><b>Tiers.</b> High = p ≥ 0.70 AND fair American inside −250…+10000 AND fixture official-verified.
Medium = p ≥ 0.55, Low below. Boundary tests use p rounded to six decimals. ≥70% out-of-window and near-band
items are published as ledgers on <a href="high-confidence.html">High confidence</a>. Every High carries one
hand-written ≥30-word prediction with per-clause official facts.</div>
<div class="card"><b>Honesty controls.</b> No bookmaker odds are asserted (the NHL API's embedded official odds
appear once, as a labelled cross-check). No value is inferred across sessions. Expired or unreachable sources
degrade to blank + flag, not to remembered values. This desk makes no claim of worldwide completeness: the OLBG
visible capture excludes XHR-paginated hub pages, which is itself flagged (F-8F6D-12).</div>
"""
page("methodology.html", "Methodology", body)

# --------------------------------------------------------- sport subpages ----
for slug, name in SPORTS:
    rows = [f for f in FX["fixtures"] if f["sport"] == slug]
    olbg_hub = next((h["olbg_url"] for h in HV["hubs"] if h["sport"] == slug), None)
    st = next((h["status"] for h in HV["hubs"] if h["sport"] == slug), "?")
    head = f"""<h2>{esc(name)}</h2>
<div class="note">OLBG hub: <a href="{esc(olbg_hub)}">{esc(olbg_hub)}</a> · capture status: <b>{esc(st)}</b>
(fetched {esc(HV['fetched_window_utc'])}, chunk 0 · “Load More” XHR beyond capture, F-8F6D-12).
Rows below: {len(rows)} · official-verified {sum(1 for f in rows if f['verified'])} · priced {sum(1 for f in rows if f['id'] in LINES_BY)}.</div>"""
    if not rows:
        gap = ("No events were listed on the OLBG hub and no match-level fixtures were retrievable from the "
               "official source either — recorded as a coverage gap with flags, not filled in."
               if slug == "esports" else
               "The OLBG hub returned “No tips found” and the official GBGB race cards are JS-rendered; only "
               "official news headlines were readable (F-8F6D-11) — no per-race rows are published.")
        body = head + f'<div class="warnbox">{gap}</div>' + \
               '<p class="mut">See <a href="flagged.html">Flagged</a> and <a href="sources.html">Sources</a>.</p>'
    else:
        mrows = []
        for f in rows:
            fr = LINES_BY.get(f["id"])
            if not fr:
                continue
            for m in fr["markets"]:
                tier = "high" if (m["p"] >= .70 and m["in_window"] and f["verified"]) else ("med" if m["p"] >= .55 else "low")
                mrows.append(f'<tr><td class="mono">{esc(f["id"])}</td><td>{esc(m["market"])}</td>'
                             f'<td><b>{esc(m["selection"])}</b></td><td class="num">{m["p"]:.4f}</td>'
                             f'<td class="num">{m["fair_decimal"]:.4f}</td><td class="num">{m["fair_american"]:+.1f}</td>'
                             f'<td><span class="bad {tier}">{"High" if tier=="high" else ("Medium" if tier=="med" else "Low")}</span></td></tr>')
        mtab = (f'<h3>Our lines</h3><table><tr><th>id</th><th>market</th><th>selection</th><th class="num">p</th>'
                f'<th class="num">fair dec</th><th class="num">fair am</th><th>tier</th></tr>{"".join(mrows)}</table>') \
               if mrows else '<div class="warnbox">No lines published for this sport — see the reason on <a href="markets.html">Markets</a>.</div>'
        body = head + match_rows(sorted(rows, key=lambda f: (f["date"] or "9999", f["id"])), show_sport=False) + mtab
    page(f"sports/{slug}.html", name, body, f"sports/{slug}.html")

print("pages:", sum(len(fs) for _, _, fs in os.walk(SITE)), "files in", SITE)
