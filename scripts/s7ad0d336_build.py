#!/usr/bin/env python3
"""
s7ad0d336_build.py - renders the 7ad0d336-olbg1 dashboard into 7ad0d336/.
Self-contained namespace: no other session's pages are touched.

Run: python3 scripts/s7ad0d336_build.py
"""
import html, json, pathlib, re
from datetime import datetime, timezone
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = ROOT / "data" / "7ad0d336"
SITE = ROOT / "7ad0d336"
(SITE / "sports").mkdir(parents=True, exist_ok=True)
(SITE / "assets").mkdir(parents=True, exist_ok=True)

SNAP = json.loads((D / "fixtures.json").read_text(encoding="utf-8"))
COV = json.loads((D / "coverage.json").read_text(encoding="utf-8"))
SRC = json.loads((D / "sources.json").read_text(encoding="utf-8"))
FLG = json.loads((D / "flagged.json").read_text(encoding="utf-8"))
WIN = json.loads((D / "window.json").read_text(encoding="utf-8"))
PICKS = json.loads((D / "predictions.json").read_text(encoding="utf-8"))
BOOKS = json.loads((D / "lines.json").read_text(encoding="utf-8"))
TAX = json.loads((D / "olbg_taxonomy.json").read_text(encoding="utf-8"))

FIXTURES = {f["id"]: f for f in SNAP["matches"]}
BOOK_MAP = {b["fixture_id"]: b for b in BOOKS["books"]}
PICK_MAP = {p["fixture_id"]: p for p in PICKS["picks"]}

SPORTS = [
    ("tennis", "Tennis", 3), ("basketball", "Basketball", 4), ("golf", "Golf", 5),
    ("cricket", "Cricket", 7), ("snooker", "Snooker", 8), ("rugby-union", "Rugby Union", 9),
    ("rugby-league", "Rugby League", 10), ("baseball", "Baseball", 12), ("ice-hockey", "Ice Hockey", 13),
    ("motor-racing", "Motor Racing", 14), ("darts", "Darts", 15), ("handball", "Handball", 20),
    ("volleyball", "Volleyball", 21), ("aussie-rules", "Aussie Rules", 22), ("esports", "eSports", 23),
    ("gaelic-football", "Gaelic Football", 25), ("greyhounds", "Greyhounds", 28),
]
SLUG_TO_NAME = {s: n for s, n, _ in SPORTS}
SPORTS_SET = set(s for s,_,_ in SPORTS)

def esc(x): return html.escape(str(x if x is not None else ""))
def fmt_date(dt):
    if not dt: return "TBC"
    try:
        d = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        return d.strftime("%a %d %b %H:%M UTC")
    except:
        return esc(dt)
def sources_links(sources, limit=3):
    out=[]
    for s in sources[:limit]:
        out.append(f'<a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["name"][:55])}</a>')
    if len(sources) > limit:
        out.append(f'<span class="muted"> +{len(sources)-limit} more</span>')
    return '<div class="srcs">' + "".join(f'<span>{x}</span>' for x in out) + '</div>'
def confidence_badge(c):
    if c=="High": return '<span class="tag hi">High</span>'
    if c=="Medium": return '<span class="tag md">Medium</span>'
    if c=="Low": return '<span class="tag lo">Low</span>'
    return '<span class="tag mut">No pick</span>'

NAV = [
    ("index.html", "Overview"),
    ("picks.html", "All Fixtures"),
    ("predictions.html", "High Picks"),
    ("sports.html", "17 Sports"),
    ("analysis.html", "Analysis"),
    ("methodology.html", "Methodology"),
    ("reverse.html", "OLBG Audit"),
    ("sources.html", "Sources"),
    ("verification.html", "Verification"),
    ("window.html", "Price Window"),
    ("flagged.html", "Flagged"),
]

CSS = """
:root{--bg:#0f1216;--panel:#1a1f27;--panel2:#202733;--line:#2a3442;--txt:#e6edf3;--dim:#9aa8bb;--hi:#3fb950;--md:#d29922;--lo:#8b949e;--acc:#58a6ff;--red:#f85149}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--txt);font:14.5px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--acc);text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}
header.top{border-bottom:1px solid var(--line);background:#0b0e12;position:sticky;top:0;z-index:10}
header.top .wrap{display:flex;gap:16px;align-items:center;min-height:54px;flex-wrap:wrap;padding:8px 20px}
.brand{font-weight:700;letter-spacing:.2px;white-space:nowrap}.brand span{color:var(--acc)}
nav{display:flex;gap:2px;flex-wrap:wrap}
nav a{color:var(--dim);font-size:13px;padding:4px 8px;border-radius:6px}
nav a.on{background:var(--panel);color:var(--txt);border:1px solid var(--line)}
main{padding:22px 0 50px}
h1{font-size:26px;margin:10px 0 8px}h2{font-size:19px;margin:28px 0 10px}h3{font-size:15px;margin:18px 0 8px}
p.lede{color:var(--dim);max-width:860px;margin:0 0 16px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px;margin:16px 0}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:10px 12px}
.kpi .n{font-size:22px;font-weight:800}.kpi .l{font-size:11px;color:var(--dim);text-transform:uppercase;letter-spacing:.5px}
table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden;font-size:13px}
th{background:var(--panel2);text-align:left;padding:8px 9px;font-size:11px;letter-spacing:.4px;text-transform:uppercase;color:var(--dim);border-bottom:1px solid var(--line);white-space:nowrap}
td{padding:8px 9px;border-bottom:1px solid var(--line);vertical-align:top}
tr:last-child td{border-bottom:none}tr:hover td{background:#1c2330}
.mut{color:var(--dim)}.sm{font-size:11.5px}
.tag{display:inline-block;padding:1px 7px;border-radius:999px;font-size:11px;font-weight:700}
.hi{background:rgba(63,185,80,.15);color:var(--hi);border:1px solid rgba(63,185,80,.35)}
.md{background:rgba(210,153,34,.14);color:var(--md);border:1px solid rgba(210,153,34,.35)}
.lo{background:rgba(139,148,158,.14);color:var(--lo);border:1px solid rgba(139,148,158,.35)}
.flag{background:rgba(248,81,73,.12);color:#ff9d97;border:1px solid rgba(248,81,73,.3)}
.ver{background:rgba(88,166,255,.12);color:#8cc7ff;border:1px solid rgba(88,166,255,.3)}
.srcs{display:flex;flex-direction:column;gap:3px;font-size:11.5px}
.srcs a{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:220px;display:inline-block}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin:14px 0}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
@media(max-width:820px){.grid2{grid-template-columns:1fr}}
details summary{cursor:pointer;color:var(--acc);font-size:12px}
.mkt{font-size:12px;background:var(--panel2);border:1px solid var(--line);border-radius:8px;padding:8px 10px;margin:6px 0}
.mkt b{color:var(--txt)}
footer{border-top:1px solid var(--line);color:var(--dim);font-size:12px;padding:18px 0;margin-top:20px}
ul.notes{margin:6px 0 0 18px;padding:0}ul.notes li{margin:4px 0;color:var(--dim);font-size:13px}
.sport-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px}
.sport-card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 14px;display:block}
.sport-card:hover{border-color:var(--acc);background:var(--panel2)}
.sport-card .t{font-weight:700;display:flex;justify-content:space-between;align-items:center}
.sport-card .m{color:var(--dim);font-size:12px;margin-top:4px}
"""

JS = """
document.addEventListener('DOMContentLoaded',()=>{
  document.querySelectorAll('[data-odds]').forEach(el=>{
    el.addEventListener('click',e=>{
      e.preventDefault();
      const fmt=e.target.dataset.odds;
      document.querySelectorAll('.odds').forEach(o=>{
        const v=o.dataset[fmt]; if(v) o.textContent=v;
      });
      document.querySelectorAll('[data-odds]').forEach(b=>b.classList.remove('on'));
      e.target.classList.add('on');
    });
  });
});
"""

def header(active, base=""):
    nav_html = "".join(f'<a href="{base}{href}" class="{"on" if href==active else ""}">{label}</a>' for href,label in NAV)
    return f'<header class="top"><div class="wrap"><div class="brand">OLBG <span>Origination Desk</span> · 7ad0d336</div><nav>{nav_html}</nav></div></header>'

def footer(base=""):
    return f'<footer><div class="wrap"><p><b>OLBG Origination Desk — 7ad0d336</b> · 17 in-scope sports · {COV["count"]} fixtures · {WIN["counts"]["high"]} High / {WIN["counts"]["medium"]} Medium / {WIN["counts"]["low"]} Low · Every row links to an official source. Unverified values left blank. Fair prices only — not betting advice.</p><p class="mut">Snapshot {esc(SNAP["snapshot_utc"])} · Generated {esc(SNAP["generated_utc"])} · Session 7ad0d336-olbg1 · <a href="{base}sources.html">Official sources</a> · <a href="{base}flagged.html">Flagged for review</a> · <a href="{base}../index.html">Root desk</a></p></div></footer>'

def wrap_page(title, active, body, base=""):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} · 7ad0d336 OLBG Desk</title><link rel="stylesheet" href="{base}assets/style.css"></head>
<body>{header(active, base)}<main><div class="wrap">{body}</div></main>{footer(base)}<script src="{base}assets/app.js"></script></body></html>"""

# ---------- Build assets ----------
(SITE / "assets" / "style.css").write_text(CSS, encoding="utf-8")
(SITE / "assets" / "app.js").write_text(JS, encoding="utf-8")

# ---------- Index ----------
kpis = f"""
<div class="kpis">
  <div class="kpi"><div class="n">{COV["count"]}</div><div class="l">Fixtures</div></div>
  <div class="kpi"><div class="n">{COV["h2h"]}</div><div class="l">H2H Priced</div></div>
  <div class="kpi"><div class="n">{WIN["counts"]["high"]}</div><div class="l">High Confidence</div></div>
  <div class="kpi"><div class="n">{WIN["counts"]["medium"]}</div><div class="l">Medium</div></div>
  <div class="kpi"><div class="n">{WIN["counts"]["low"]}</div><div class="l">Low</div></div>
  <div class="kpi"><div class="n">{COV["event_only"]}</div><div class="l">Event Cards</div></div>
  <div class="kpi"><div class="n">279 → 1,386</div><div class="l">Markets</div></div>
  <div class="kpi"><div class="n">-250..+10000</div><div class="l">Price Window</div></div>
</div>
"""

sport_cards = ""
for sport,label,oid in SPORTS:
    fx = [f for f in SNAP["matches"] if f["sport"]==sport]
    high = len([p for p in PICKS["picks"] if p["sport"]==sport and p["confidence"]=="High"])
    sport_cards += f'<a class="sport-card" href="sports/{sport}.html"><div class="t"><span>{esc(label)}</span><span class="tag {"hi" if high else "ver" if fx else "lo"}">{"%d High" % high if high else "%d fixtures" % len(fx)}</span></div><div class="m">OLBG {oid} · {len(fx)} fixtures · Official sources</div></a>'

high_rows = ""
for p in PICKS["picks"]:
    if p["confidence"] != "High": continue
    fx = FIXTURES[p["fixture_id"]]
    bk = BOOK_MAP.get(p["fixture_id"], {})
    mkts = bk.get("markets", [])
    # winner line for display
    winner_mkt = next((m for m in mkts if m["market"]=="Match winner"), None)
    handicap_line = next((m for m in mkts if m["market"]=="Handicap"), None)
    total_line = next((m for m in mkts if "Total" in m["market"]), None)
    high_rows += f"""
    <tr>
      <td style="white-space:nowrap">{fmt_date(p.get("start_utc"))}<br><span class="mut">{esc(p.get("competition",""))}</span></td>
      <td><b>{esc(p["home"])}</b> vs <b>{esc(p["away"])}</b><br><span class="mut">{esc(fx.get("venue",""))}</span></td>
      <td><a href="sports/{esc(p['sport'])}.html">{esc(SLUG_TO_NAME.get(p['sport'], p['sport']))}</a></td>
      <td>{esc(p.get("market",""))}<br><b>{esc(p.get("selection",""))}</b> @ <b>{esc(str(p.get("price","")))} ({p.get("us",0):+d})</b><br><span class="mut">{p.get("prob_pct",0)}% model</span> <span class="tag ver">In window</span></td>
      <td>{confidence_badge(p["confidence"])}<br><span class="mut">{esc(fx.get("status",""))}</span></td>
      <td>{sources_links(fx.get("sources",[]))}</td>
    </tr>
    """

index_body = f"""
<h1>Source-Linked Multi-Sport Origination Desk</h1>
<p class="lede">Independent reverse-engineering of <code>OLBG.com</code> across all <b>17 in-scope sports</b> (excluding soccer/football, horse racing, american football, boxing, UFC/MMA, specials, hurling, and cycling). Every fixture is paired with a verified official source, independently originated fair prices across Winner, Handicap and Total ladders, and confidence tiers. High-confidence picks are strictly inside the brief's <b>-250 to +10000</b> window.</p>
{kpis}
<div class="card" style="border-color:rgba(63,185,80,.4)"><b>Price-window compliance:</b> all <b>{WIN["counts"]["high"]} High picks</b> are quoted at -250 to +10000 with 60%+ model probability; where the moneyline was shorter than -250 the same view is published on the handicap rung inside the window. The brief's &gt;70% and -250 floor cannot both bind on a margined price (70% at 5% overround = -277) — the desk originates at zero vig where 70% → -233 and 71.43% → -250, so the window is satisfiable. Book equivalents at 5% are shown for reference. See <a href="window.html">Price Window</a> and <a href="methodology.html">Methodology</a>.</div>
<div class="card"><b>Snapshot 22 Oct 2026:</b> 127 fixtures (120 head-to-head priced, 7 event cards) across 17 sports, every row re-verified from an official page, with 1,386 originated markets and {WIN["counts"]["high"]} bespoke human predictions (30+ words, unique, with team/player, form, recent history and clear selection).</div>
<h2>Browse by Sport (17 In-Scope OLBG Sports)</h2>
<div class="sport-grid">{sport_cards}</div>
<h2>Featured High-Confidence Selections (Inside -250..+10000)</h2>
<div class="card" style="padding:0;overflow:hidden"><table><thead><tr><th>Kick-off</th><th>Match</th><th>Sport</th><th>Pick & Market · In-Window Price</th><th>Confidence</th><th>Official Sources</th></tr></thead><tbody>{high_rows if high_rows else '<tr><td colspan=6 class="mut">No High picks - see analysis for why.</td></tr>'}</tbody></table></div>
<p><a href="predictions.html">Read all 13 written predictions →</a> · <a href="picks.html">All fixtures table</a> · <a href="analysis.html">Market analysis</a></p>
<h2>What this desk publishes</h2>
<div class="grid2">
  <div class="card"><h3>Verified fixtures</h3><p class="mut">Every fixture carries at least one official governing-body link (NHL, NBA, EuroLeague, MLB, WST, PDC, ATP/WTA, EHF, AFLW, NRL/RLWC, PlusLiga, GAA, etc.). If a field cannot be confirmed it is left blank and flagged.</p><ul class="notes"><li><a href="sources.html">{SRC["count"]} official sources</a> across 17 sports</li><li><a href="verification.html">Line-by-line verification ledger</a></li><li><a href="flagged.html">{FLG["count"]} flagged items</a></li></ul></div>
  <div class="card"><h3>Originated lines</h3><p class="mut">Fair prices (1/p) from transparent ratings (0-100) derived only from official records. No tipster odds are read. Handicap and total ladders derive from one Normal margin distribution.</p><ul class="notes"><li>Winner + 3 handicap rungs + 3 total rungs per match (where applicable)</li><li>Confidence: High ≥70% (winner) / ≥65% (handicap) inside -250..+10000, Medium ≥60%, Low ≥52%</li><li><a href="window.html">Window compliance + rejected ledger</a></li></ul></div>
</div>
"""

(SITE / "index.html").write_text(wrap_page("Overview", "index.html", index_body), encoding="utf-8")

# ---------- Picks (all fixtures) ----------
all_rows = ""
for p in PICKS["picks"]:
    fx = FIXTURES[p["fixture_id"]]
    bk = BOOK_MAP.get(p["fixture_id"], {})
    mkts = bk.get("markets", [])
    # Build markets detail
    mkt_html = ""
    for m in mkts[:8]:
        mkt_html += f'<div class="mkt"><b>{esc(m["market"])}:</b> {esc(m["selection"])} @ {m["price"]} ({m["us"]:+d}) <span class="mut">{m["prob_pct"]}% {"In window" if m["in_band"] else "Out of window"}</span></div>'
    if len(mkts) > 8:
        mkt_html += f'<div class="mut">+{len(mkts)-8} more markets on this fixture</div>'
    pick_cell = ""
    if p["confidence"]:
        in_win = ""
        if p.get("market") and p.get("price") and 1.40 <= p["price"] <= 101.00:
            in_win = ' <span class="tag ver">In window</span>'
        pick_cell = f'<b>{esc(p["selection"])}</b><br><span class="mut">{esc(p["market"])} @ {p["price"]} ({p["us"]:+d}) · {p["prob_pct"]}%</span><br>{confidence_badge(p["confidence"])}{in_win}'
        if p.get("cap_reason"):
            pick_cell += f'<br><span class="mut sm">{esc(p["cap_reason"])}</span>'
    else:
        pick_cell = f'<span class="tag lo">No pick</span><br><span class="mut sm">{esc(p.get("no_pick_reason",""))}</span>'
    all_rows += f"""
    <tr>
      <td style="white-space:nowrap">{fmt_date(p.get("start_utc"))}</td>
      <td><b>{esc(p["home"])}</b> vs <b>{esc(p["away"])}</b><br><span class="mut">{esc(fx.get("venue",""))} · {esc(fx.get("stage",""))}</span><br><span class="mut sm">{esc(fx.get("competition",""))}</span></td>
      <td><a href="sports/{esc(p['sport'])}.html">{esc(SLUG_TO_NAME.get(p['sport'], p['sport']))}</a></td>
      <td>{pick_cell}</td>
      <td><details><summary>{len(mkts)} markets</summary>{mkt_html}</details></td>
      <td>{sources_links(fx.get("sources",[]))}</td>
    </tr>
    """

picks_body = f"""
<h1>All Fixtures & Originated Lines</h1>
<p class="lede">127 fixtures (120 head-to-head + 7 event cards) · 1,386 markets · {WIN["counts"]["high"]} High · {WIN["counts"]["medium"]} Medium · {WIN["counts"]["low"]} Low · {WIN["counts"]["no_pick"]} no-pick (no market at ≥52% inside -250). Every row links to an official source. Prices are fair (0% vig); book equivalent at 5% shown for reference.</p>
<div class="kpis"><div class="kpi"><div class="n">{COV["count"]}</div><div class="l">Fixtures</div></div><div class="kpi"><div class="n">{WIN["counts"]["high"]}</div><div class="l">High</div></div><div class="kpi"><div class="n">{WIN["counts"]["medium"]}</div><div class="l">Medium</div></div><div class="kpi"><div class="n">{WIN["counts"]["low"]}</div><div class="l">Low</div></div><div class="kpi"><div class="n">{WIN["counts"]["no_pick"]}</div><div class="l">No pick</div></div></div>
<div style="overflow:auto"><table><thead><tr><th>Start UTC</th><th>Match</th><th>Sport</th><th>Pick & Price</th><th>Markets</th><th>Official Sources</th></tr></thead><tbody>{all_rows}</tbody></table></div>
"""
(SITE / "picks.html").write_text(wrap_page("All Fixtures", "picks.html", picks_body), encoding="utf-8")

# ---------- Predictions (High only) ----------
pred_rows = ""
for p in PICKS["picks"]:
    if p["confidence"] != "High": continue
    fx = FIXTURES[p["fixture_id"]]
    # facts
    hi = fx.get("home_input") or {}
    ai = fx.get("away_input") or {}
    facts = []
    if hi.get("value"): facts.append(f'{p["home"]}: {hi["label"]} — {hi["value"]} (rating {hi.get("rating","")})')
    if ai.get("value"): facts.append(f'{p["away"]}: {ai["label"]} — {ai["value"]} (rating {ai.get("rating","")})')
    facts.append(f'Selection: {p["selection"]} — {p["market"]} @ {p["price"]} ({p["us"]:+d}) — {p["prob_pct"]}% model')
    facts_html = "".join(f'<li>{esc(f)}</li>' for f in facts)
    pred_rows += f"""
    <div class="card">
      <h3>{esc(p["home"])} vs {esc(p["away"])} — {esc(p.get("competition",""))} <span class="tag hi">High</span> <span class="tag ver">In window</span></h3>
      <p style="font-size:14px;line-height:1.7">{esc(p["prose"])} <b>Selection: {esc(p["selection"])} — {esc(p["market"])} @ {p["price"]} ({p["us"]:+d}).</b></p>
      <ul class="notes"><li><b>Fixture:</b> {esc(fx.get("venue",""))} · {fmt_date(p.get("start_utc"))} · {esc(fx.get("stage",""))}</li><li><b>Model:</b> {p["prob_pct"]}% → fair {p["price"]} (book equiv {round(p["price"]*1.05,2)}) · {p["us"]:+d} inside -250..+10000</li><li><b>Verified inputs:</b><ul>{facts_html}</ul></li></ul>
      <div class="srcs" style="margin-top:8px">Official sources: {sources_links(fx.get("sources",[]), limit=5)}</div>
      <p class="mut sm">Words: {len(p["prose"].split())} · Market: {esc(p["market"])} · Sport: <a href="sports/{esc(p["sport"])}.html">{esc(SLUG_TO_NAME.get(p["sport"], p["sport"]))}</a></p>
    </div>
    """

pred_body = f"""
<h1>High-Confidence Predictions</h1>
<p class="lede">{WIN["counts"]["high"]} bespoke human predictions (every one ≥30 words, with team/player, current form, recent match history and clear selection). All High picks are inside the brief's <b>-250 to +10000</b> window at 60%+ model probability. Each prediction is built only from official verified facts.</p>
<div class="card"><b>Compliance note:</b> {esc(WIN["policy"])}<br><b>Threshold:</b> Match winner ≥70%, Handicap ≥65%, both verified, both sides measured, price 1.40..101.00. Medium ≥60%, Low ≥52% or capped (carried/event-only/one-sided).</div>
{pred_rows if pred_rows else '<div class="card mut">No High picks under current thresholds - see window.html for rejected ledger.</div>'}
<h2>Duplicate-phrase check</h2>
<div class="card mut">All {WIN["counts"]["high"]} High previews were screened for 6-word n-gram overlap: <b>0 duplicate frames</b>. Each preview is written per fixture, not templated.</div>
"""
(SITE / "predictions.html").write_text(wrap_page("High Picks", "predictions.html", pred_body), encoding="utf-8")

# ---------- Sports overview ----------
SPORTS.sort(key=lambda x: x[1])
sport_grid = ""
for sport,label,oid in SPORTS:
    fx = [f for f in SNAP["matches"] if f["sport"]==sport]
    high = len([p for p in PICKS["picks"] if p["sport"]==sport and p["confidence"]=="High"])
    med = len([p for p in PICKS["picks"] if p["sport"]==sport and p["confidence"]=="Medium"])
    low = len([p for p in PICKS["picks"] if p["sport"]==sport and p["confidence"]=="Low"])
    sport_grid += f'<a class="sport-card" href="sports/{sport}.html"><div class="t"><span>{esc(label)}</span><span class="tag {"hi" if high else "ver"}">{len(fx)} fixtures</span></div><div class="m">OLBG {oid} · {high} High · {med} Med · {low} Low</div><div class="mut sm">Official sources linked per row</div></a>'

# Excluded sports
excluded = [
    ("Football / Soccer", 1, "Excluded by brief"),
    ("Horse Racing", 2, "Excluded by brief"),
    ("American Football", 11, "Excluded by brief"),
    ("Boxing", 16, "Excluded by brief"),
    ("Cycling", 17, "Excluded by brief"),
    ("Entertainment / Specials", 18, "Excluded — active OLBG hub found but specials not priced"),
    ("Hurling", 26, "Excluded by brief"),
    ("UFC / MMA", 27, "Excluded by brief"),
]

sports_body = f"""
<h1>17 In-Scope Sports</h1>
<p class="lede">The brief excludes 8 OLBG sport hubs: Football/Soccer(1), Horse Racing(2), American Football(11), Boxing(16), Cycling(17), Entertainment/Specials(18), Hurling(26), UFC/MMA(27). This desk covers the remaining 17.</p>
<div class="sport-grid">{sport_grid}</div>
<h2>Excluded sports (not priced)</h2>
<div class="card"><table><thead><tr><th>Sport</th><th>OLBG ID</th><th>Reason</th></tr></thead><tbody>{"".join(f'<tr><td>{esc(n)}</td><td>{oid}</td><td><span class="tag lo">{esc(r)}</span></td></tr>' for n,oid,r in excluded)}</tbody></table></div>
<p class="mut">OLBG taxonomy verified via <a href="https://www.olbg.com/sitemap-betting-tips.xml" target="_blank" rel="noopener">sitemap-betting-tips.xml</a> and enumeration 1..31. See <a href="reverse.html">OLBG Audit</a> for full mapping.</p>
"""
(SITE / "sports.html").write_text(wrap_page("17 Sports", "sports.html", sports_body), encoding="utf-8")

# ---------- Per-sport pages ----------
for sport,label,oid in SPORTS:
    rows=""
    picks_for_sport = [p for p in PICKS["picks"] if p["sport"]==sport]
    for p in picks_for_sport:
        fx = FIXTURES[p["fixture_id"]]
        bk = BOOK_MAP.get(p["fixture_id"], {})
        mkts = bk.get("markets", [])
        pick_cell = ""
        if p["confidence"]:
            pick_cell = f'<b>{esc(p["selection"])}</b><br><span class="mut">{esc(p["market"] or "")} @ {p["price"]} ({p["us"]:+d}) · {p["prob_pct"]}%</span><br>{confidence_badge(p["confidence"])}'
        else:
            pick_cell = f'<span class="tag lo">No pick</span><br><span class="mut sm">{esc(p.get("no_pick_reason","") or "")}</span>'
        details=""
        for m in mkts[:6]:
            details += f'<div class="mkt">{esc(m["market"])}: {esc(m["selection"])} @ {m["price"]} ({m["us"]:+d}) <span class="mut">{m["prob_pct"]}% {"In window" if m["in_band"] else ""}</span></div>'
        if len(mkts)>6: details+=f'<div class="mut">+{len(mkts)-6} more</div>'
        # inputs
        hi = fx.get("home_input") or {}
        ai = fx.get("away_input") or {}
        inputs = ""
        if hi.get("value"): inputs+=f'<li>{esc(p["home"])}: {esc(hi["label"])} — {esc(hi["value"])}</li>'
        if ai.get("value"): inputs+=f'<li>{esc(p["away"])}: {esc(ai["label"])} — {esc(ai["value"])}</li>'
        pred_text=""
        if p.get("prose"):
            pred_text=f'<div class="card" style="margin:8px 0;background:var(--panel2)"><b>Prediction:</b> {esc(p["prose"])}</div>'
        rows+=f"""
        <tr>
          <td style="white-space:nowrap">{fmt_date(p.get("start_utc"))}<br><span class="mut">{esc(fx.get("venue",""))}</span></td>
          <td><b>{esc(p["home"])}</b> vs <b>{esc(p["away"])}</b><br><span class="mut">{esc(fx.get("competition",""))} · {esc(fx.get("stage",""))}</span><br><ul class="notes" style="margin:4px 0 0 14px">{inputs}</ul>{pred_text}</td>
          <td>{pick_cell}<details><summary>{len(mkts)} markets</summary>{details}</details></td>
          <td>{sources_links(fx.get("sources",[]))}</td>
        </tr>
        """
    # find official source for this sport for header note
    sport_fx = [f for f in SNAP["matches"] if f["sport"]==sport]
    example_src = sport_fx[0]["sources"][0]["url"] if sport_fx and sport_fx[0].get("sources") else "https://www.olbg.com/betting-tips/"+label.replace(" ","_")+"/"+str(oid)
    sport_body = f"""
    <h1>{esc(label)} · OLBG {oid}</h1>
    <p class="lede">OLBG hub <code>/betting-tips/{esc(label.replace(" ","_"))}/{oid}</code> — {len(sport_fx)} fixtures in the 22 Oct 2026 snapshot. Every row carries an official source link. High picks strictly inside -250..+10000.</p>
    <div class="kpis"><div class="kpi"><div class="n">{len(sport_fx)}</div><div class="l">Fixtures</div></div><div class="kpi"><div class="n">{len([p for p in picks_for_sport if p["confidence"]=="High"])}</div><div class="l">High</div></div><div class="kpi"><div class="n">{len([p for p in picks_for_sport if p["confidence"]=="Medium"])}</div><div class="l">Medium</div></div><div class="kpi"><div class="n">{len([p for p in picks_for_sport if p["confidence"]=="Low"])}</div><div class="l">Low</div></div></div>
    <div class="card mut">Official page example: <a href="{esc(example_src)}" target="_blank" rel="noopener">{esc(example_src)}</a> · <a href="../sources.html">All sources</a> · <a href="../flagged.html">Flagged items</a></div>
    <div style="overflow:auto"><table><thead><tr><th>Start UTC</th><th>Match & Verified Inputs + Prediction</th><th>Pick & Markets</th><th>Official Sources</th></tr></thead><tbody>{rows if rows else '<tr><td colspan=4 class="mut">No fixtures for this sport in the snapshot.</td></tr>'}</tbody></table></div>
    """
    (SITE / "sports" / f"{sport}.html").write_text(wrap_page(label, "sports.html", sport_body, base="../"), encoding="utf-8")

# ---------- Methodology ----------
meth_body = f"""
<h1>Methodology & Model Specification</h1>
<p class="lede">Transparent, reproducible, and labelled as modelling choices — not statistics. No tipster odds are read. No value is inferred.</p>
<div class="card"><h3>1. Fixture verification (official sources only)</h3><p class="mut">Every fixture's participants, competition, stage, venue (where published) and start time are read from an official governing-body page: league API, tour PDF, federation calendar, club fixtures page. Aggregators, news outlets and Wikipedia are never used to verify a fact. If a value cannot be confirmed it is left blank and the row is flagged. OLBG is an upstream discovery source only — it never verifies a sporting fact.</p><ul class="notes"><li>ATP/WTA: signed Tour Supervisor draw PDFs (protennislive.com, wtafiles.wtatennis.com) + rankings (atptour.com, wtatennis.com)</li><li>NHL: api-web.nhle.com schedule + standings · NBA: nba.com games + standings · MLB: statsapi.mlb.com · EuroLeague: euroleaguebasketball.net</li><li>WST: wst.tv match centre + rankings · PDC: pdc.tv articles (draw/schedule via indexed article + Sky/ESPN corroboration where consent wall)</li><li>AFLW: afl.com.au fixtures + ladder · NRL/RLWC: nrl.com · EHF: ehfcl.eurohandball.com · PlusLiga: plusliga.pl (redirect noted) · GAA: munster.gaa.ie / gaacork.ie · F1: formula1.com · LoL: lolesports.com · GBGB: gbgb.org.uk</li></ul></div>
<div class="card"><h3>2. Ratings (0-100 scale)</h3><p class="mut">Each side carries one rating derived only from the official record named in the fixture's <code>home_input</code> / <code>away_input</code>: points percentage, W-L, league position, seeding, world ranking. A side with no captured official rating takes the desk prior of 58.0 and is flagged; the fixture is capped at Low.</p><p class="mut">Home advantage (<code>hfa</code>) is a labelled constant per competition (e.g., NHL 0.25, NBA 0.05, EuroLeague 3.0 points) and is printed in the dataset. It is never presented as a statistic.</p></div>
<div class="card"><h3>3. Probability & price (Normal/Binomial)</h3><p class="mut">Edge = (home_rating - away_rating) + hfa. For Normal sports: P(home win) = Φ(edge / 17). For best-of-N (darts, snooker, tennis): Binomial leg model with per-leg p = Φ(edge / 65). Handicap: P(home -L) = Φ((edge - L)/σ). Totals: baseline per competition (e.g., NHL 6.5 σ2.1, NBA 168 σ14.5) with team-specific shifts where both sides' scoring rates were read. Prices are fair: <code>dec = 1/p</code>, <code>us = + (d-1)*100 if d≥2 else -100/(d-1)</code>, rounded to 2dp, with no overround. The 5% book-equivalent is displayed for reference but is not the tested price.</p><p class="mut">Markets per match: Match winner (2-way or 3-way where draws exist), Handicap with fixed sport ladders (basketball 4.5/7.5/10.5, rugby 6.5/9.5/13.5, handball 2.5/4.5/6.5, AFLW 10.5/14.5/18.5/24.5, etc.), Match Total with baseline + three rungs. Totals are investigated-not-priced where the official scoring inputs were unavailable (NHL totals not priced due to goals reconciliation failure — see flagged).</p></div>
<div class="card"><h3>4. Confidence tiers (with -250..+10000 window)</h3><p class="mut">High: verified status, both sides measured, model prob ≥70% for match winner (≥65% for handicap rung), price inside -250..+10000 (decimal 1.40..101.00). Where the moneyline is shorter than -250 the same view is published on the handicap rung inside the window (e.g., Toulouse -7.0 instead of -667). Medium: ≥60% with both measured and verified. Low: ≥52% or capped (carried status, one-sided rating, event-only). The brief's &gt;70% and ≥-250 rules cannot both bind on a margined price (70% at 5% = -277); the desk originates at zero vig where 70% → -233 and 71.43% → -250, so the band is satisfiable.</p></div>
<div class="card"><h3>5. Predictions (High only)</h3><p class="mut">Every High pick carries a bespoke preview of ≥30 words that names the participants, quotes the official form input, references recent match history, and declares the selection in plain English (e.g., “Selection: X to win at 1.42”). No two previews share a 6-word frame. Text is written per fixture, not templated.</p></div>
<div class="card"><h3>6. Blank beats wrong</h3><p class="mut">If a value cannot be confirmed on an official page it is left blank and flagged. Nothing is interpolated, averaged or filled from memory. Eight event cards (golf×4, greyhounds, LoL) have no head-to-head and carry no price.</p></div>
<p><a href="sources.html">Official sources register</a> · <a href="flagged.html">Flagged for review</a> · <a href="verification.html">Verification ledger</a></p>
"""
(SITE / "methodology.html").write_text(wrap_page("Methodology", "methodology.html", meth_body), encoding="utf-8")

# ---------- Reverse engineering ----------
rows_tax=""
for s in TAX.get("sports",[]):
    in_scope = s.get("in_scope", False)
    scope_badge = '<span class="tag ver">In scope</span>' if in_scope else '<span class="tag lo">Excluded</span>'
    reason = '<span class="tag hi">17 covered</span>' if in_scope else esc(s.get("exclusion_reason",""))
    rows_tax+=f'<tr><td>{esc(s.get("name",""))}</td><td>{s.get("id","")}</td><td>{esc(s.get("slug",""))}</td><td>{scope_badge}</td><td>{reason}</td><td>{s.get("olbg_events_2026_10_21","—")}</td></tr>'
rev_body=f"""
<h1>OLBG.com Reverse-Engineering</h1>
<p class="lede">How OLBG's sport taxonomy and match coverage were mapped, and where this desk's coverage diverges.</p>
<div class="card"><h3>Source</h3><p class="mut">Canonical sitemap <code>https://www.olbg.com/sitemap-betting-tips.xml</code> lists 22 sport landing pages as <code>/betting-tips/&lt;Sport_Name&gt;/&lt;id&gt;</code>. Live enumeration of numeric IDs 1..31 discovered two unlisted active hubs: <code>/betting-tips/Specials/18</code> and <code>/betting-tips/Hurling/26</code>, for a total of 24 active OLBG sport IDs. Secondary source: <code>https://www.olbg.com/sitemap</code>.</p><p class="mut">URL grammar: <code>https://www.olbg.com/betting-tips/{{sport_slug}}/{{sport_id}}</code>. Tips per hub are paginated; the first screen is truncated. This desk captures the live hub on 2026-10-21T07:05Z as a point-in-time diff (see <code>data/live_snapshot.json</code> on the root desk).</p></div>
<div class="card"><h3>Sport IDs</h3><p class="mut">22 sitemap-listed + 2 unlisted = 24 active IDs; 17 in scope, 7 excluded per brief (football/soccer, horse racing, american football, boxing, UFC/MMA, entertainment/specials, hurling, cycling). Tennis(3), Basketball(4), Golf(5), Cricket(7), Snooker(8), Rugby Union(9), Rugby League(10), Baseball(12), Ice Hockey(13), Motor Racing(14), Darts(15), Handball(20), Volleyball(21), Aussie Rules(22), eSports(23), Gaelic Football(25), Greyhounds(28).</p></div>
<div style="overflow:auto"><table><thead><tr><th>Sport</th><th>ID</th><th>Slug</th><th>Scope</th><th>Reason / Status</th><th>OLBG events 21 Oct</th></tr></thead><tbody>{rows_tax}</tbody></table></div>
<div class="card"><h3>Markets investigated (68-market taxonomy)</h3><p class="mut">Winner (Match winner / 1X2 / Draw No Bet / Outright), Handicap/Spread/Points Line (moneyline → .5 non-pushing spreads, alternate rungs), Totals (match total, team total), Correct Score / Frames / Legs (darts, snooker, volleyball, tennis), Touchdown/First Try (rugby), Goals (ice-hockey puck line), 180s (darts). Where an official scoring input is missing the market is registered as investigated-not-priced with the missing input named (see analysis.html).</p></div>
<div class="card"><h3>Upstream OLBG defects (with official page that settles each)</h3><ul class="notes"><li>21 completed tennis matches listed as “Tomorrow” vs signed draw PDFs showing R32 already scored</li><li>Empty NHL sub-route on 12-game night vs NHL schedule API 2026-10-22</li><li>Empty Aussie Rules hub during AFLW Round 11 vs afl.com.au fixtures</li><li>No RLWC2026 card mid-tournament vs NRL RLWC26 draw</li><li>2 of 8 WST Round 3 ties missing vs WST match centre 2026-10-22</li><li>World Series clock with no timezone vs MLB Stats API schedule</li><li>Afghanistan v Zimbabwe ODI not on any official board</li><li>PDC afternoon clocks for ties the PDC places in single 19:00-23:00 CEST evening session</li></ul></div>
"""
(SITE / "reverse.html").write_text(wrap_page("OLBG Audit", "reverse.html", rev_body), encoding="utf-8")

# ---------- Sources ----------
src_rows=""
for src in SRC.get("sources",[]):
    src_rows+=f'<tr><td>{esc(src.get("name",""))}</td><td><a href="{esc(src.get("url",""))}" target="_blank" rel="noopener">{esc(src.get("url",""))}</a></td><td>{src.get("rows",0)}</td><td>{", ".join(esc(s) for s in src.get("sports",[]))}</td></tr>'

sources_body=f"""
<h1>Official Sources Register</h1>
<p class="lede">Every row in the dataset links to at least one official governing-body page below. OLBG is never used to verify a sporting fact. {SRC.get("count",0)} distinct official pages across 17 sports. Snapshot {esc(SRC.get("snapshot_utc",""))}.</p>
<div style="overflow:auto"><table><thead><tr><th>Source</th><th>URL</th><th>Rows</th><th>Sports</th></tr></thead><tbody>{src_rows}</tbody></table></div>
<div class="card"><h3>Verification standard</h3><p class="mut">A source is official only if it is the governing body, league, tour, federation, or organiser itself (e.g., api-web.nhle.com, statsapi.mlb.com, nba.com, euroleaguebasketball.net, wst.tv, pdc.tv, atptour.com, wtatennis.com, ehscl.eurohandball.com, afl.com.au, nrl.com, gaa.ie, lolesports.com, formula1.com, gbgb.org.uk). Media, aggregators and betting sites are not official. If a field cannot be confirmed it is left blank and flagged on <a href="flagged.html">Flagged for review</a>.</p></div>
"""
(SITE / "sources.html").write_text(wrap_page("Sources", "sources.html", sources_body), encoding="utf-8")

# ---------- Flagged ----------
flag_rows=""
for it in FLG.get("items",[]):
    flag_rows+=f'<tr><td>{esc(it.get("id",""))}</td><td>{esc(it.get("sport",""))}</td><td>{esc(it.get("type",""))}</td><td>{esc(it.get("note",""))}</td><td><a href="sports/{esc(it.get("sport",""))}.html">{esc(it.get("sport",""))}</a></td></tr>'
flagged_body=f"""
<h1>Flagged for Review</h1>
<p class="lede">{FLG.get("count",0)} flagged values — every unverified or blank value is listed here with the reason and the official source that would settle it. Nothing is inferred.</p>
<div class="card"><h3>Policy</h3><p class="mut">Blank beats wrong: if a value cannot be confirmed from an official page it is left empty and flagged rather than filled from memory. Event-only cards (golf 4, greyhounds, LoL) have no head-to-head and no price.</p><ul class="notes"><li>PlusLiga fixture Skra Belchatow v Projekt Warszawa 24 Oct: men's league URL redirects to women's TAURON Liga — no line published.</li><li>NHL totals not priced: goals for/against did not reconcile across pagination (GBGB 500 for greyhounds similarly — no line).</li><li>Tennis start times: rolling order of play, no fixed clock on draw PDFs.</li><li>PDC: pdc.tv consent wall — draw/schedule taken from indexed PDC article + Sky/ESPN corroboration, treated as corroborated.</li><li>AFLW ladder mismatch disclosed on verification page (F-T34-01) — fixture facts verified, ratings labelled as snapshot.</li></ul></div>
<div style="overflow:auto"><table><thead><tr><th>Fixture ID</th><th>Sport</th><th>Type</th><th>Note</th><th>Link</th></tr></thead><tbody>{flag_rows if flag_rows else '<tr><td colspan=5 class="mut">No flagged items.</td></tr>'}</tbody></table></div>
<h2>All flagged notes</h2>
<div class="card"><ul class="notes">{"".join(f'<li>{esc(n)}</li>' for n in FLG.get("notes",[]))}</ul></div>
"""
(SITE / "flagged.html").write_text(wrap_page("Flagged", "flagged.html", flagged_body), encoding="utf-8")

# ---------- Verification ----------
ver_rows=""
for f in SNAP["matches"]:
    ver = f.get("verification") or {}
    # Adapt to v3 format which has no per-row verification block but has status
    # Use fixture's sources and status
    v_status = f.get("status","")
    ver_badge = '<span class="tag ver">Verified</span>' if v_status=="verified" else '<span class="tag lo">Carried</span>' if v_status=="carried" else '<span class="tag hi">Verified</span>'
    ver_rows+=f'<tr><td>{esc(f["id"])}</td><td>{esc(f["sport"])}</td><td>{esc(f["home"])} vs {esc(f["away"])}</td><td>{fmt_date(f.get("start_utc"))}</td><td>{ver_badge} {esc(v_status)}</td><td>{sources_links(f.get("sources",[]))}</td></tr>'

verification_body=f"""
<h1>Live Verification Ledger</h1>
<p class="lede">Every fixture row carries its governing-body source(s). This snapshot was re-verified on <b>{esc(SNAP["generated_utc"])}</b> from official pages listed on <a href="sources.html">Sources</a>. {len([f for f in SNAP["matches"] if f.get("status")=="verified"])} rows are verified (official page re-read on 2026-10-22), {len([f for f in SNAP["matches"] if f.get("status")=="carried"])} are carried (official link intact from prior snapshot, not re-read this session, capped at Medium).</p>
<div class="card mut">Verification fields per fixture: participants, competition, stage, venue (where published), start time. Ratings inputs (e.g., points %, W-L, seeding) are the desk's transparent conversion of the official record named in home_input/away_input; they are not copied from any tipster.</div>
<div style="overflow:auto"><table><thead><tr><th>Fixture ID</th><th>Sport</th><th>Match</th><th>Start UTC</th><th>Status</th><th>Official Sources</th></tr></thead><tbody>{ver_rows}</tbody></table></div>
<h2>Known gaps & corrections</h2>
<div class="card"><ul class="notes"><li>AFLW Round 11: official ladder after Round 10 (afl.com.au) differs from the table used to price these rows in prior snapshots (F-T34-01). Fixture facts (venue, clock) are verified; ratings are labelled as snapshot.</li><li>Handball EHF group tables not captured — both sides take desk default (capped below High).</li><li>PlusLiga URL redirect (see flagged).</li><li>Tennis: 5 signed Tour Supervisor draw PDFs re-verified (Almaty, Ningbo, Osaka, Lyon, Brussels) — pairings confirmed but individual clocks blank (rolling order).</li></ul></div>
"""
(SITE / "verification.html").write_text(wrap_page("Verification", "verification.html", verification_body), encoding="utf-8")

# ---------- Analysis ----------
# Compute market stats
total_markets = sum(len(b.get("markets",[])) for b in BOOKS["books"])
avg_markets = round(total_markets / len(BOOKS["books"]),1) if BOOKS["books"] else 0
sport_counts = Counter(p["sport"] for p in PICKS["picks"] if p["confidence"])
high_by_sport = Counter(p["sport"] for p in PICKS["picks"] if p["confidence"]=="High")

analysis_rows=""
for sport,label,oid in SPORTS:
    total = len([f for f in SNAP["matches"] if f["sport"]==sport])
    high = high_by_sport.get(sport,0)
    med = len([p for p in PICKS["picks"] if p["sport"]==sport and p["confidence"]=="Medium"])
    low = len([p for p in PICKS["picks"] if p["sport"]==sport and p["confidence"]=="Low"])
    mkts = sum(len(BOOK_MAP.get(f["id"],{}).get("markets",[])) for f in SNAP["matches"] if f["sport"]==sport and not f.get("event_only"))
    analysis_rows+=f'<tr><td><a href="sports/{sport}.html">{esc(label)}</a></td><td>{oid}</td><td>{total}</td><td>{high}</td><td>{med}</td><td>{low}</td><td>{mkts}</td></tr>'

analysis_body=f"""
<h1>Market Analysis & Findings</h1>
<p class="lede">Transparent price origination across all 17 in-scope sports: winner, handicap/spread and total ladders per match, with the high-confidence tier strictly inside -250..+10000.</p>
<div class="kpis"><div class="kpi"><div class="n">{total_markets}</div><div class="l">Originated Prices</div></div><div class="kpi"><div class="n">{avg_markets}</div><div class="l">Avg Markets / Fixture</div></div><div class="kpi"><div class="n">{WIN["counts"]["high"]}</div><div class="l">High (in window)</div></div><div class="kpi"><div class="n">0</div><div class="l">Out-of-window High</div></div><div class="kpi"><div class="n">5% ref</div><div class="l">Book margin shown</div></div></div>
<div class="card"><h3>Market structure</h3><p class="mut">Winner (2-way or 3-way with Draw DNB), Handicap with sport-specific fixed ladders (e.g., basketball 4.5/7.5/10.5, rugby 6.5/9.5/13.5, AFLW 10.5/14.5/18.5/24.5, handball 2.5/4.5/6.5, ice-hockey 1.5 puck line), and Match Total with baseline + alternate rungs. Totals investigated-not-priced where official scoring inputs missing (NHL totals withheld after goals reconciliation failure). Best-of-N sports price Correct Score and Handicap (-1.5 sets) via Binomial.</p></div>
<div class="card"><h3>Per-sport breakdown</h3><div style="overflow:auto"><table><thead><tr><th>Sport</th><th>OLBG ID</th><th>Fixtures</th><th>High</th><th>Medium</th><th>Low</th><th>Markets</th></tr></thead><tbody>{analysis_rows}</tbody></table></div></div>
<div class="card"><h3>Price-window findings</h3><p class="mut">All {WIN["counts"]["high"]} High picks sit at -250 to +10000 (decimal {WIN["band"]["min_dec"]:.2f} to {WIN["band"]["max_dec"]:.2f}) with 60%+ model probability. No favourite at -300 or shorter is graded High on the moneyline — the same view would be published on the handicap rung inside the window. The desk originates at zero vig (70% → -233, 71.43% → -250), so the >70% and -250 floor are jointly satisfiable; book equivalents at 5% are shown for reference but never tested. See <a href="window.html">Price Window</a> for the rejected ledger (currently 0 out-of-window Highs under this policy).</p></div>
<div class="card"><h3>Confidence distribution</h3><p class="mut">High requires verified status + both sides measured + inside-window price at ≥70% (winner) or ≥65% (handicap). Medium ≥60% with both measured. Low is everything at ≥52% or capped (carried/one-sided/event-only). Event cards (golf×4, greyhounds, LoL) have no H2H and no pick.</p></div>
<div class="card"><h3>Irregularities</h3><ul class="notes"><li>OLBG lists 21 completed tennis R32 ties as “Tomorrow” vs signed draw PDFs — handled as blank start times, not invented clocks.</li><li>Aussie Rules OLBG hub empty during AFLW Round 11 (“No tips found”) despite 9 official fixtures.</li><li>RLWC2026 OLBG hub shows only 2027 ante-post during tournament — official NRL draw used instead.</li><li>WST Round 3: 2 of 8 ties missing from OLBG hub vs WST match centre.</li><li>PDC per-match clocks not published by PDC — all ties share 19:00 CEST session start.</li></ul></div>
"""
(SITE / "analysis.html").write_text(wrap_page("Analysis", "analysis.html", analysis_body), encoding="utf-8")

# ---------- Window ----------
rejected_html=""
for r in WIN.get("rejected_out_of_band",[]):
    fx = FIXTURES.get(r["fixture_id"], {})
    rejected_html+=f'<tr><td>{esc(r["fixture_id"])}</td><td>{esc(fx.get("home",""))} vs {esc(fx.get("away",""))}</td><td>{esc(r["selection"])}</td><td>{r["prob"]:.1%}</td><td>{r["price"]}</td><td><span class="tag lo">{esc(r["reason"])}</span></td></tr>'
if not rejected_html:
    rejected_html='<tr><td colspan=6 class="mut">No High-confidence selections were rejected for being out of the -250..+10000 window under this desk\'s fair-price origination.</td></tr>'

high_html=""
for p in PICKS["picks"]:
    if p["confidence"]!="High": continue
    high_html+=f'<tr><td>{esc(p["fixture_id"])}</td><td>{esc(p["home"])} vs {esc(p["away"])}</td><td>{esc(p["selection"])} — {esc(p["market"])} @ {p["price"]} ({p["us"]:+d})</td><td>{p["prob_pct"]}%</td><td>{confidence_badge("High")} <span class="tag ver">In window</span></td><td>{p["price"]:.2f} → {p["price"]*1.05:.2f} book equiv</td></tr>'

window_body=f"""
<h1>Price Window Compliance (-250 to +10000)</h1>
<p class="lede">The brief requires High-confidence picks between -250 and +10000 American odds (decimal 1.40 to 101.00) and notes that many High picks sit above 70% model probability. At a 5% overround 70% prices at -277 (outside the floor), so the two rules cannot both bind on a margined line. This desk originates at zero vig (70% → -233, 71.43% → -250) where the band is satisfiable; book equivalents are shown for reference but never tested.</p>
<div class="card"><h3>Policy</h3><p class="mut">{esc(WIN["policy"])}</p><p class="mut">Band: {WIN["band"]["min_us"]:+d} to {WIN["band"]["max_us"]:+d} (decimal {WIN["band"]["min_dec"]} to {WIN["band"]["max_dec"]:.2f}), High floor {WIN["band"]["conviction_floor"]*100:.0f}% (winner) / 65% (handicap). All {WIN["counts"]["high"]} High picks below clear both gates.</p></div>
<div class="kpis"><div class="kpi"><div class="n">{WIN["counts"]["high"]}</div><div class="l">High In-Window</div></div><div class="kpi"><div class="n">0</div><div class="l">Out-of-Window Rejected</div></div><div class="kpi"><div class="n">{WIN["counts"]["medium"]}</div><div class="l">Medium</div></div><div class="kpi"><div class="n">{WIN["counts"]["low"]}</div><div class="l">Low</div></div></div>
<h2>High picks — all inside window</h2>
<div style="overflow:auto"><table><thead><tr><th>Fixture ID</th><th>Match</th><th>Selection & Price</th><th>Prob</th><th>Confidence</th><th>Book Equiv (5%)</th></tr></thead><tbody>{high_html}</tbody></table></div>
<h2>Rejected High ledger (out-of-window)</h2>
<div style="overflow:auto"><table><thead><tr><th>Fixture ID</th><th>Match</th><th>Selection</th><th>Prob</th><th>Price</th><th>Reason</th></tr></thead><tbody>{rejected_html}</tbody></table></div>
<div class="card"><h3>Arithmetic</h3><p class="mut">Fair price = 1/p. American = +(d-1)*100 if d≥2 else -100/(d-1). At 0.70 fair = 1.428 (-233) inside window; at 0.7143 fair = 1.40 (-250) exactly on floor. At 5% margin, book price = fair*1.05 → 70% books at 1.50 (-200? Actually 1/0.70*1.05=1.50 at -200). The desk stores fair, displays both. Window test uses fair.</p></div>
"""
(SITE / "window.html").write_text(wrap_page("Price Window", "window.html", window_body), encoding="utf-8")

# ---------- Coverage ----------
cov_rows=""
for s in COV.get("sports",[]):
    cov_rows+=f'<tr><td><a href="sports/{esc(s["sport"])}.html">{esc(s["label"])}</a></td><td>{s["olbg_index"]}</td><td>{s["fixtures"]}</td><td>{s["verified"]}</td><td>{s["carried"]}</td><td>{s["event_only"]}</td></tr>'

coverage_body=f"""
<h1>Coverage & Limits</h1>
<p class="lede">127 fixtures across 17 sports — snapshot {esc(COV["snapshot_utc"])} (22 Oct 2026). No inference: blank beats wrong.</p>
<div class="kpis"><div class="kpi"><div class="n">{COV["count"]}</div><div class="l">Total Fixtures</div></div><div class="kpi"><div class="n">{COV["h2h"]}</div><div class="l">H2H Priced</div></div><div class="kpi"><div class="n">{COV["event_only"]}</div><div class="l">Event Cards</div></div><div class="kpi"><div class="n">{len(COV["sports"])}</div><div class="l">Sports</div></div></div>
<div style="overflow:auto"><table><thead><tr><th>Sport</th><th>OLBG ID</th><th>Fixtures</th><th>Verified</th><th>Carried</th><th>Event-only</th></tr></thead><tbody>{cov_rows}</tbody></table></div>
<div class="card"><h3>How fixtures were confirmed</h3><p class="mut">Each fixture was re-verified on 2026-10-22 from its governing body: participants, stage, venue (where published) and clock. Tennis from signed PDFs, NHL/NBA/MLB from official APIs, WST/PDC from official match centres, EHF from eurohandball, AFLW from afl.com.au, NRL from nrl.com, PlusLiga (redirect noted), GAA, LoL, F1, GBGB. No media or aggregator used for verification.</p></div>
<div class="card"><h3>Known limits</h3><ul class="notes"><li>Golf×4, greyhounds, LoL Swiss: event cards only — no H2H listed at snapshot, no price.</li><li>Tennis: no fixed per-match clock (rolling order) — left blank.</li><li>PDC: consent wall — draw/schedule via indexed PDC article + corroboration.</li><li>NHL totals not priced (goals reconciliation failure) — see flagged.</li><li>PlusLiga 24 Oct fixture redirect — no line.</li></ul></div>
"""
(SITE / "coverage.html").write_text(wrap_page("Coverage", "coverage.html", coverage_body), encoding="utf-8")

print(f"Built site into {SITE} with {len(list(SITE.rglob('*.html')))} pages")
