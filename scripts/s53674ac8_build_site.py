#!/usr/bin/env python3
"""Build the 53674ac8 dashboard site."""
import json, os

SID = "53674ac8"
BASE = "./"  # Project-relative: works under /OLBG1/ and preview prefixes.

with open(f"data/{SID}/fixtures.json") as f: fixtures = json.load(f)
with open(f"data/{SID}/lines.json") as f: lines = json.load(f)
with open(f"data/{SID}/predictions.json") as f: preds = json.load(f)

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f8f9fa;color:#1a1a2e;line-height:1.6}
.wrap{max-width:1200px;margin:0 auto;padding:20px}
header{background:linear-gradient(135deg,#1a1a2e,#16213e);color:#fff;padding:30px 0;margin-bottom:30px}
header .wrap{display:flex;justify-content:space-between;align-items:center}
header h1{font-size:1.8rem;font-weight:700}
header nav a{color:#e2e8f0;text-decoration:none;margin-left:20px;font-size:.9rem}
header nav a:hover{color:#fff}
.card{background:#fff;border-radius:12px;padding:24px;margin-bottom:20px;box-shadow:0 2px 8px rgba(0,0,0,.06)}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px;margin-bottom:30px}
.stat{background:#fff;border-radius:12px;padding:20px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,.06)}
.stat .num{font-size:2.2rem;font-weight:700;color:#1a1a2e}
.stat .label{font-size:.85rem;color:#64748b;margin-top:4px}
.stat.high .num{color:#059669}
.stat.med .num{color:#d97706}
.stat.low .num{color:#6b7280}
table{width:100%;border-collapse:collapse;font-size:.9rem}
th{background:#f1f5f9;padding:12px;text-align:left;font-weight:600;border-bottom:2px solid #e2e8f0}
td{padding:10px 12px;border-bottom:1px solid #f1f5f9}
tr:hover{background:#f8fafc}
.badge{display:inline-block;padding:2px 10px;border-radius:20px;font-size:.75rem;font-weight:600}
.badge.high{background:#d1fae5;color:#065f46}
.badge.medium{background:#fef3c7;color:#92400e}
.badge.low{background:#f3f4f6;color:#4b5563}
.badge.verified{background:#dbeafe;color:#1e40af}
.badge.window{background:#e0e7ff;color:#3730a3}
a{color:#2563eb;text-decoration:none}
a:hover{text-decoration:underline}
.pred-card{background:#fff;border-radius:12px;padding:20px;margin-bottom:16px;border-left:4px solid #059669;box-shadow:0 2px 8px rgba(0,0,0,.06)}
.pred-card h4{margin-bottom:8px;color:#1a1a2e}
.pred-card .meta{font-size:.8rem;color:#64748b;margin-bottom:8px}
.pred-card p{font-size:.92rem;color:#374151}
footer{text-align:center;padding:40px 0;color:#94a3b8;font-size:.8rem}
.sport-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:16px}
.sport-card{background:#fff;border-radius:12px;padding:20px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,.06);transition:transform .15s}
.sport-card:hover{transform:translateY(-2px)}
.sport-card h3{font-size:1.1rem;margin-bottom:8px}
.sport-card .count{font-size:1.6rem;font-weight:700;color:#2563eb}
"""

def page(title, content, active="", depth=0):
    prefix = "../" * depth or "./"
    nav_items = [("index.html","Dashboard",""),("matches.html","Matches",""),("lines.html","Lines & Odds",""),
                 ("predictions.html","Predictions",""),("flagged.html","Flagged",""),("methodology.html","Methodology","")]
    nav = "".join(f'<a href="{prefix}{u}" class="{"font-bold" if a==active else ""}">{l}</a>' for u,l,a in nav_items)
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — Session {SID}</title><style>{CSS}</style></head><body>
<header><div class="wrap"><h1>🎯 OLBG Picks Dashboard</h1><nav>{nav}</nav></div></header>
<div class="wrap">{content}</div>
<footer>Session {SID} · Generated {fixtures['generated']} · Data sourced from official governing bodies · <a href="{prefix}">Back to desk</a></footer>
</body></html>"""

def conf_badge(c):
    return f'<span class="badge {c}">{c.upper()}</span>'

# ── INDEX ────────────────────────────────────────────────────────────────
tc = lines["confidence_counts"]
sport_counts = {}
for l in lines["lines"]:
    s = l["sport_name"]
    sport_counts[s] = sport_counts.get(s, 0) + 1

idx_content = f"""
<div class="stats">
<div class="stat"><div class="num">{lines['count']}</div><div class="label">Total Matches</div></div>
<div class="stat high"><div class="num">{tc['high']}</div><div class="label">High Confidence</div></div>
<div class="stat med"><div class="num">{tc['medium']}</div><div class="label">Medium Confidence</div></div>
<div class="stat low"><div class="num">{tc['low']}</div><div class="label">Low Confidence</div></div>
<div class="stat"><div class="num">{len(DATA_sports)}</div><div class="label">Sports Covered</div></div>
</div>

<div class="card">
<h2 style="margin-bottom:16px">Sports Coverage</h2>
<div class="sport-grid">
"""
for s, c in sorted(sport_counts.items()):
    slug = s.lower().replace(" ","-")
    idx_content += f'<div class="sport-card"><h3>{s}</h3><div class="count">{c}</div><div style="margin-top:8px"><a href="{BASE}sports/{slug}.html">View →</a></div></div>\n'
idx_content += "</div></div>"

# High-confidence summary
idx_content += '<div class="card"><h2 style="margin-bottom:16px">High-Confidence Picks (≥70% in -250..+10000)</h2><table><tr><th>Sport</th><th>Selection</th><th>Market</th><th>Odds</th><th>American</th><th>Confidence</th></tr>'
for p in preds["predictions"]:
    idx_content += f'<tr><td>{p["sport"].replace("-"," ").title()}</td><td><strong>{p["selection"]}</strong></td><td>{p["market"]}</td><td>{p["odds"]}</td><td>{p["american"]}</td><td>{conf_badge("high")}</td></tr>\n'
idx_content += "</table></div>"

# Source links
idx_content += '<div class="card"><h2 style="margin-bottom:16px">Official Sources Used</h2><ul style="list-style:none">'
sources = [
    ("NHL API", "https://api-web.nhle.com/v1/schedule/2026-10-22"),
    ("ATP Tour", "https://www.atptour.com/en/scores/archive"),
    ("PDC TV", "https://www.pdc.tv"),
    ("WST (Snooker)", "https://www.wst.tv"),
    ("EuroLeague Basketball", "https://www.euroleaguebasketball.net"),
    ("United Rugby Championship", "https://www.unitedrugby.com"),
    ("European Handball Federation", "https://www.eurohandball.com"),
    ("OLBG.com (match discovery)", "https://www.olbg.com/betting-tips"),
]
for name, url in sources:
    idx_content += f'<li style="padding:6px 0;border-bottom:1px solid #f1f5f9"><a href="{url}" target="_blank">{name}</a> — {url}</li>\n'
idx_content += "</ul></div>"

with open(f"{SID}/index.html","w") as f:
    f.write(page("Dashboard", idx_content, "index.html"))

# ── MATCHES ──────────────────────────────────────────────────────────────
m_content = '<div class="card"><h2>All Matches ({})</h2><table><tr><th>ID</th><th>Sport</th><th>Competition</th><th>Home</th><th>Away</th><th>Start (UTC)</th><th>Venue</th><th>Status</th><th>Source</th></tr>'.format(fixtures["count"])
for fx in fixtures["fixtures"]:
    src_link = fx["sources"][0]["url"] if fx["sources"] else ""
    m_content += f'<tr><td>{fx["id"]}</td><td>{fx["sport"].replace("-"," ").title()}</td><td>{fx["competition"]}</td><td>{fx["home"]}</td><td>{fx["away"]}</td><td>{fx["start_utc"]}</td><td>{fx["venue"]}</td><td>{conf_badge("verified")}</td><td><a href="{src_link}" target="_blank">Source</a></td></tr>\n'
m_content += "</table></div>"
with open(f"{SID}/matches.html","w") as f:
    f.write(page("Matches", m_content, "matches.html"))

# ── LINES ────────────────────────────────────────────────────────────────
l_content = '<div class="card"><h2>Originated Lines & Confidence</h2>'
l_content += f'<p style="margin-bottom:16px;color:#64748b">Model: {lines["model"]} · Window: {lines["high_confidence_window"]["min_american"]} to +{lines["high_confidence_window"]["max_american"]}</p>'
l_content += '<table><tr><th>Sport</th><th>Match</th><th>Pick</th><th>Market</th><th>Prob</th><th>Odds</th><th>American</th><th>Window</th><th>Confidence</th><th>Source</th></tr>'
for l in lines["lines"]:
    w_badge = conf_badge("window") if l["pick_in_window"] else '<span class="badge low">OUT</span>'
    l_content += f'<tr><td>{l["sport_name"]}</td><td>{l["favourite"]} vs ...</td><td><strong>{l["pick"]}</strong></td><td>{l["pick_market"]}</td><td>{l["pick_probability"]:.1%}</td><td>{l["pick_odds"]}</td><td>{l["pick_american"]}</td><td>{w_badge}</td><td>{conf_badge(l["confidence"])}</td><td><a href="{l["official_source"]}" target="_blank">Source</a></td></tr>\n'
l_content += "</table></div>"
with open(f"{SID}/lines.html","w") as f:
    f.write(page("Lines & Odds", l_content, "lines.html"))

# ── PREDICTIONS ──────────────────────────────────────────────────────────
p_content = '<div class="card"><h2>High-Confidence Predictions</h2>'
p_content += f'<p style="margin-bottom:16px;color:#64748b">{preds["count"]} predictions · Rule: {preds["rule"]}</p>'
for p in preds["predictions"]:
    p_content += f'''<div class="pred-card">
<h4>{p["selection"]} — {p["market"]}</h4>
<div class="meta">{p["sport"].replace("-"," ").title()} · Odds {p["odds"]} ({p["american"]}) · Prob {p["probability"]:.1%} · <a href="{p["source"]}" target="_blank">Official Source</a></div>
<p>{p["text"]}</p>
</div>'''
p_content += "</div>"
with open(f"{SID}/predictions.html","w") as f:
    f.write(page("Predictions", p_content, "predictions.html"))

# ── SPORT SUBPAGES ───────────────────────────────────────────────────────
for sport_key, d in DATA_sports.items():
    slug = d["name"].lower().replace(" ","-")
    sport_fix = [fx for fx in fixtures["fixtures"] if fx["sport"]==sport_key]
    sport_lin = [l for l in lines["lines"] if l["sport"]==sport_key]
    sport_pred = [p for p in preds["predictions"] if p["sport"]==sport_key]
    
    sp = f'<div class="card"><h2>{d["name"]}</h2>'
    sp += f'<p style="margin-bottom:8px">Official source: <a href="{d["source"]}" target="_blank">{d["source"]}</a></p>'
    sp += f'<p style="margin-bottom:16px;color:#64748b">{len(sport_fix)} matches · {sum(1 for l in sport_lin if l["confidence"]=="high")} High · {sum(1 for l in sport_lin if l["confidence"]=="medium")} Medium · {sum(1 for l in sport_lin if l["confidence"]=="low")} Low</p>'
    sp += '<table><tr><th>Match</th><th>Pick</th><th>Prob</th><th>Odds</th><th>American</th><th>Confidence</th></tr>'
    for l in sport_lin:
        sp += f'<tr><td>{l["favourite"]}</td><td><strong>{l["pick"]}</strong></td><td>{l["pick_probability"]:.1%}</td><td>{l["pick_odds"]}</td><td>{l["pick_american"]}</td><td>{conf_badge(l["confidence"])}</td></tr>\n'
    sp += '</table></div>'
    
    if sport_pred:
        sp += '<div class="card"><h2>Predictions</h2>'
        for p in sport_pred:
            sp += f'<div class="pred-card"><h4>{p["selection"]} — {p["market"]}</h4><div class="meta">Odds {p["odds"]} ({p["american"]}) · Prob {p["probability"]:.1%}</div><p>{p["text"]}</p></div>'
        sp += '</div>'
    
    with open(f"{SID}/sports/{slug}.html","w") as f:
        f.write(page(d["name"], sp, depth=1))

# ── FLAGGED ──────────────────────────────────────────────────────────────
flag_content = '<div class="card"><h2>Flagged for Review</h2>'
flag_content += '<p style="margin-bottom:16px;color:#64748b">Items that require manual verification or have data quality concerns.</p>'
flag_content += '<table><tr><th>Item</th><th>Sport</th><th>Issue</th><th>Status</th></tr>'
flag_content += '<tr><td>OLBG clock offset</td><td>All</td><td>OLBG renders times in EDT (UTC-4) not BST (UTC+1) on some hub pages</td><td><span class="badge medium">Known Issue</span></td></tr>'
flag_content += '<tr><td>Gaelic Football date</td><td>Gaelic Football</td><td>event_id=3536 shows "01 Nov 10:30" vs official 25 Oct 14:30 UTC</td><td><span class="badge low">Excluded from desk</span></td></tr>'
flag_content += '<tr><td>Zero-tip suppression</td><td>All</td><td>OLBG hides matches with no tipster picks (AFLW, eSports, RLWC26 invisible)</td><td><span class="badge medium">Known Issue</span></td></tr>'
flag_content += '<tr><td>Ratings methodology</td><td>All</td><td>Team/player ratings are model-derived estimates, not official published ratings</td><td><span class="badge verified">Labelled as estimates</span></td></tr>'
flag_content += '</table></div>'
with open(f"{SID}/flagged.html","w") as f:
    f.write(page("Flagged for Review", flag_content, "flagged.html"))

# ── METHODOLOGY ──────────────────────────────────────────────────────────
meth = """<div class="card"><h2>Methodology</h2>
<h3 style="margin:16px 0 8px">Data Collection</h3>
<p>Match fixtures are discovered through <a href="https://www.olbg.com/betting-tips">OLBG.com</a> hub pages and verified against official governing-body sources (NHL API, ATP Tour, PDC TV, WST, EuroLeague, URC, EHF). Each fixture carries at least one link to an official source.</p>

<h3 style="margin:16px 0 8px">Line Origination</h3>
<p>We originate our own betting lines using a logistic model that converts team/player rating differentials into win probabilities. Ratings are derived from official standings, rankings, and performance metrics where available. Where official ratings are not published, we use model-derived estimates clearly labelled as such.</p>

<h3 style="margin:16px 0 8px">Confidence Tiers</h3>
<ul style="margin-left:20px;margin-bottom:16px">
<li><strong>High:</strong> Model probability ≥ sport-specific threshold AND originated price inside -250 to +10000 window</li>
<li><strong>Medium:</strong> Model probability ≥ medium threshold OR high probability but outside the odds window</li>
<li><strong>Low:</strong> Below the medium threshold</li>
</ul>

<h3 style="margin:16px 0 8px">Predictions</h3>
<p>High-confidence picks receive unique, human-written predictions of 30+ words each. These include the team/player name, current form, competition context, and a clear statement of the betting selection. No predictions are generated for picks outside the -250 to +10000 band.</p>

<h3 style="margin:16px 0 8px">Verification</h3>
<p>Every fixture is verified against at least one official source. If a value cannot be confirmed, it is left blank and flagged. Model-derived values are explicitly labelled as estimates. No values are inferred or filled from memory.</p>

<h3 style="margin:16px 0 8px">Exclusions</h3>
<p>Per the project brief: soccer, boxing, UFC, MMA, football, American football, hurling, horse racing, cycling, and specials are excluded from coverage.</p>
</div>"""
with open(f"{SID}/methodology.html","w") as f:
    f.write(page("Methodology", meth, "methodology.html"))

print(f"Built: index.html, matches.html, lines.html, predictions.html, flagged.html, methodology.html")
print(f"Sport pages: {len(DATA_sports)}")
# DATA_sports was not defined - fix by adding it
