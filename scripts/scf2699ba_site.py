"""Session cf2699ba-olbg1 — static dashboard generator.

Writes cf2699ba/*.html and cf2699ba/sports/*.html from the JSON in data/cf2699ba/.
No external assets, no JavaScript, no remote fonts: the pages render identically
from file:// and from GitHub Pages.
"""
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "cf2699ba")
SITE = os.path.join(ROOT, "cf2699ba")
SPORTDIR = os.path.join(SITE, "sports")

e = lambda s: html.escape(str(s), quote=True)

CSS = """
:root{--ink:#12181f;--muted:#5b6773;--line:#e2e6ea;--bg:#f6f7f9;--card:#fff;
--accent:#0f5c4d;--accent2:#0b3d66;--high:#8a1c1c;--med:#8a5a00;--low:#3c4a57;
--hi-bg:#fbecec;--me-bg:#fdf3e0;--lo-bg:#eef1f4}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--accent2)}
header.top{background:var(--card);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:10}
.wrap{max-width:1180px;margin:0 auto;padding:0 18px}
.brandbar{display:flex;align-items:center;gap:14px;padding:12px 0;flex-wrap:wrap}
.brand{font-weight:700;letter-spacing:.2px;font-size:17px;text-decoration:none;color:var(--ink)}
.brand span{color:var(--accent)}
.stamp{margin-left:auto;color:var(--muted);font-size:12.5px}
nav.main{display:flex;gap:2px;overflow-x:auto;border-top:1px solid var(--line);padding:0}
nav.main a{padding:11px 12px;font-size:13.5px;text-decoration:none;color:var(--muted);white-space:nowrap;border-bottom:2px solid transparent}
nav.main a:hover{color:var(--ink)}
nav.main a.on{color:var(--accent);border-bottom-color:var(--accent);font-weight:600}
main{padding:26px 0 60px}
h1{font-size:27px;line-height:1.2;margin:0 0 6px}
h2{font-size:19px;margin:34px 0 10px}
h3{font-size:16px;margin:20px 0 8px}
.lede{color:var(--muted);margin:0 0 20px;max-width:78ch}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:18px 0 8px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px}
.kpi b{display:block;font-size:26px;line-height:1.1}
.kpi small{color:var(--muted);font-size:12.5px;display:block;margin-top:4px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:18px;margin:14px 0}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px}
@media(max-width:820px){.grid2{grid-template-columns:1fr}}
table{width:100%;border-collapse:collapse;font-size:13.5px;background:var(--card)}
.tablewrap{overflow-x:auto;border:1px solid var(--line);border-radius:10px}
th,td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{background:#f0f2f4;font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);position:sticky;top:0}
tr:last-child td{border-bottom:none}
tbody tr:nth-child(even){background:#fafbfc}
.num{font-variant-numeric:tabular-nums;white-space:nowrap}
.chip{display:inline-block;padding:2px 8px;border-radius:99px;font-size:11.5px;font-weight:600;letter-spacing:.02em}
.chip.high{background:var(--hi-bg);color:var(--high)}
.chip.medium{background:var(--me-bg);color:var(--med)}
.chip.low{background:var(--lo-bg);color:var(--low)}
.chip.ok{background:#e6f4ee;color:var(--accent)}
.chip.gap{background:#fbecec;color:var(--high)}
.chip.small{font-size:11px;padding:1px 7px}
.pill{display:inline-block;padding:1px 6px;border-radius:5px;font-size:11px;background:#eef1f4;color:var(--muted)}
.note{background:#fff8e6;border:1px solid #f0e0b0;border-radius:10px;padding:14px;margin:16px 0}
.crit{background:#fbecec;border:1px solid #f0c9c9;border-radius:10px;padding:14px;margin:16px 0}
.okbox{background:#e9f5f0;border:1px solid #c4e2d6;border-radius:10px;padding:14px;margin:16px 0}
.blank{color:#9aa5b1}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px;word-break:break-all}
.pred{border-left:3px solid var(--accent);padding-left:14px;margin:16px 0}
.pred h3{margin:0 0 4px}
.meta{color:var(--muted);font-size:12.5px}
.links a{display:inline-block;margin:0 10px 6px 0;font-size:12.5px}
footer{border-top:1px solid var(--line);background:var(--card);padding:18px 0;color:var(--muted);font-size:12.5px}
ul.tight{margin:8px 0;padding-left:20px}
ul.tight li{margin:4px 0}
.tag{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);font-weight:700}
"""

NAV = [
    ("index.html", "Summary"),
    ("matches.html", "Matches"),
    ("markets.html", "Markets"),
    ("confidence.html", "Confidence"),
    ("predictions.html", "Predictions"),
    ("analysis.html", "Analysis"),
    ("flagged.html", "Flagged"),
    ("sources.html", "Sources"),
    ("methodology.html", "Method"),
]


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


def page(filename, title, body, active="", prefix=""):
    navbits = []
    for u, t in NAV:
        cls = ' class="on"' if u == active else ""
        navbits.append(f'<a href="{prefix}{u}"{cls}>{e(t)}</a>')
    nav = "".join(navbits)
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} · OLBG research desk, 23 Oct 2026</title>
<meta name="description" content="Source-linked research desk for 15 OLBG sports, 23 October 2026. Six officially confirmed fixtures, originated prices, explicit gaps.">
<style>{CSS}</style></head>
<body>
<header class="top"><div class="wrap">
<div class="brandbar">
  <a class="brand" href="{prefix}index.html">OLBG<span>·</span>research desk</a>
  <span class="pill">session cf2699ba</span>
  <span class="stamp">Snapshot 23 Oct 2026 · 16:17–16:40 UTC</span>
</div>
<nav class="main">{nav}</nav>
</div></header>
<main><div class="wrap">{body}</div></main>
<footer><div class="wrap">
Independent research desk. Not affiliated with OLBG. No prices here are bookmaker offers and nothing is a
betting recommendation; 18+. Blank means the value could not be confirmed on an official page and is flagged
for review rather than filled in.
</div></footer>
</body></html>"""
    path = os.path.join(SITE, filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(doc)


def chip(tier):
    if not tier:
        return '<span class="blank">—</span>'
    return f'<span class="chip {tier.lower()}">{e(tier)}</span>'


def am(v):
    if v is None:
        return '<span class="blank">—</span>'
    return f"{v:+d}"


def main():
    os.makedirs(SITE, exist_ok=True)
    os.makedirs(SPORTDIR, exist_ok=True)
    sports = load("sports.json")["sports"]
    sources = load("sources.json")["sources"]
    disc = load("discovery.json")["events"]
    fx = load("fixtures.json")["fixtures"]
    lines = load("lines.json")
    preds = load("predictions.json")["predictions"]
    flags = load("flagged.json")["flags"]
    src_by_id = {s["id"]: s for s in sources}
    sport_name = {s["key"]: s["name"] for s in sports}

    verified_outcomes = sum(len(b["outcomes"]) for l in lines["verified_lines"] for b in l["blocks"])
    verified_priced = sum(1 for l in lines["verified_lines"] for b in l["blocks"]
                          for o in b["outcomes"] if o.get("p"))
    priced_indicative = sum(1 for i in lines["indicative"] if i.get("p"))
    tiers = lines["tier_counts"]
    n_high = sum(1 for f in flags if f["sev"] == "high")
    fx_by_sport = {}
    for f in fx:
        fx_by_sport.setdefault(f["sport"], []).append(f)
    disc_by_sport = {}
    for d in disc:
        disc_by_sport.setdefault(d["sport"], []).append(d)

    def src_links(ids):
        return " ".join(
            f'<a href="{e(src_by_id[i]["url"])}" title="{e(src_by_id[i]["org"])}">{e(i.replace("src-", ""))}</a>'
            for i in ids if i in src_by_id
        )

    # ------------------------------------------------------------------ index
    best = []
    for l in lines["verified_lines"]:
        for b in l["blocks"]:
            for o in b["outcomes"]:
                if o.get("p"):
                    best.append((l, b, o))
    best.sort(key=lambda t: -t[2]["p"])

    board = "".join(
        f"<tr><td>{e(sport_name[l['sport']])}</td><td>{e(l['name'])}<div class='meta'>{e(l['competition'])}"
        f" · {e(l['venue'])}</div></td>"
        f"<td>{e(b['market'])}<div class='meta'>{e(o['selection'])}</div></td>"
        f"<td class='num'>{o['p']*100:.1f}%</td><td class='num'>{o['decimal']:.3f}</td>"
        f"<td class='num'>{am(o['american'])}</td><td>{chip(o['tier'])}</td>"
        f"<td>{src_links(l['sources'])}</td></tr>"
        for l, b, o in best[:8]
    )

    cov_rows = ""
    for s in sports:
        k = s["key"]
        v = len(fx_by_sport.get(k, []))
        n = len(disc_by_sport.get(k, []))
        priced = sum(1 for (l, b, o) in best if l["sport"] == k)
        ind = sum(1 for i in lines["indicative"] if i["sport"] == k and i.get("p"))
        top = max([o["p"] for (l, b, o) in best if l["sport"] == k] or [0])
        status = "confirmed" if v else "discovery only"
        cls = "ok" if v else "gap"
        cov_rows += (
            f"<tr><td><a href='sports/{e(k)}.html'>{e(s['name'])}</a></td>"
            f"<td class='num'>{n}</td><td class='num'>{v}</td>"
            f"<td class='num'>{priced}</td><td class='num'>{ind}</td>"
            f"<td class='num'>{('%.1f%%' % (top*100)) if top else '—'}</td>"
            f"<td><span class='chip {cls}'>{e(status)}</span></td></tr>"
        )

    body = f"""
<h1>Fifteen sports, one honest snapshot</h1>
<p class="lede">Everything on this desk was read from OLBG's public sport hubs and from the governing
body of each competition between 16:17 and 16:40 UTC on 23 October 2026. OLBG tells us which matches
exist; it never tells us what is true about them. A fixture is priced only when an official page
confirmed it and supplied the inputs.</p>

<div class="kpis">
  <div class="kpi"><b>135</b><small>OLBG listings captured across 15 sports</small></div>
  <div class="kpi"><b>6</b><small>fixtures confirmed on an official page</small></div>
  <div class="kpi"><b>{verified_priced}</b><small>priced outcomes from official input</small></div>
  <div class="kpi"><b>{priced_indicative}</b><small>indicative prices, permanently Low</small></div>
  <div class="kpi"><b>{tiers['High']}</b><small>High confidence</small></div>
  <div class="kpi"><b>{tiers['Medium']}</b><small>Medium confidence</small></div>
  <div class="kpi"><b>{len(preds)}</b><small>written predictions, 30+ words each</small></div>
  <div class="kpi"><b>{len(flags)}</b><small>flagged items for review</small></div>
</div>

<div class="crit">
<p style="margin:0 0 6px"><strong>Read this before the numbers.</strong> The brief asks for five High-confidence
picks per sport per day. This desk publishes <strong>zero</strong> High picks for 23 October, and that is the
result, not an omission. The rule as written needs a probability of at least 70% <em>and</em> an American
price no shorter than −250, which leaves an eligible band of 70.0%–71.4%. Only six fixtures could be
confirmed officially, and the strongest of them prices at −567. Details and the excluded selections are on
the <a href="confidence.html">Confidence</a> page.</p>
</div>

<h2>Executive summary</h2>
<div class="card">
<p><strong>Today.</strong> Two NHL games, one MLB World Series game and three United Rugby Championship
matches are the entire confirmed slate for the fifteen sports in scope. The strongest selection on it is
<strong>Edinburgh Rugby to beat 10bet Lions</strong> at Hive Stadium (85%, fair price −567): a Medium, because
the price is shorter than the −250 window. <strong>Connacht to beat Zebre</strong> (58.5%, −141) is the best
selection that actually sits inside the window. In North America, <strong>Milwaukee Brewers</strong> are a
56.1% home money line in World Series Game 1 and <strong>Montreal Canadiens</strong> a 60.0% money line at
Chicago.</p>
<p><strong>Upcoming.</strong> The next confirmed event on the board is the Formula 1 United States Grand Prix
at Circuit of The Americas, race start 25 October 16:00 track time (5.513 km, 56 laps, 308.432 km). Gaelic
club finals in Cork and Galway are listed for 25 October and Italian and Polish volleyball for the same day,
but none of those could be tied to an official fixture page today, so they are published as listings only.</p>
<p><strong>What is not here.</strong> No injury or team-news data, no player availability, no league tables for
the club competitions and no verified fixtures at all for golf, rugby league, darts, snooker, cricket, tennis,
basketball, volleyball, handball, Gaelic sports or greyhounds. Each gap is named, sourced and published on the
<a href="flagged.html">Flagged for review</a> page rather than smoothed over.</p>
</div>

<h2>Highest-confidence selections we could actually stand behind</h2>
<p class="lede">Every row below is a fixture whose date, start and inputs came from the governing body or
league. Probability is ours; the price is the fair price implied by it, not a bookmaker quote.</p>
<div class="tablewrap"><table>
<thead><tr><th>Sport</th><th>Fixture</th><th>Market</th><th>p</th><th>Fair decimal</th><th>American</th><th>Tier</th><th>Official source</th></tr></thead>
<tbody>{board}</tbody></table></div>
<p class="meta">Eight of the {verified_priced} officially priced outcomes, ranked by probability. The full
set, including the markets we withheld, is on the <a href="markets.html">Markets</a> page.</p>

<h2>Coverage by sport</h2>
<div class="tablewrap"><table>
<thead><tr><th>Sport</th><th>OLBG listings</th><th>Confirmed fixtures</th><th>Priced outcomes (official input)</th><th>Indicative prices</th><th>Best p</th><th>Status</th></tr></thead>
<tbody>{cov_rows}</tbody></table></div>
<p class="meta">"Discovery only" means OLBG showed matches we could not tie to an official source this
session. Those rows still appear on the match list with blank official fields and a flag, never with guessed
values.</p>

<h2>What this desk will not do</h2>
<div class="grid2">
<div class="card"><span class="tag">No invention</span>
<p>If a start time, venue, record or availability note could not be read on an official page, the field is
blank and the row is flagged. Nothing is filled in from memory, from a preview article or from another
tipster's opinion.</p></div>
<div class="card"><span class="tag">No quota filling</span>
<p>{len(preds)} predictions were written because {len(preds)} selections could be supported by an official
fact trail. Inventing 68 more to reach five per sport would have produced exactly the output the brief
forbids.</p></div>
</div>

<h2>Where the evidence ran out</h2>
<p class="lede">Three of the fifteen sports produced a confirmed fixture. The other twelve are documented
gaps with the specific barrier named: a consent wall on pdc.tv for darts, a client-rendered match
centre for EuroLeague basketball and the WTA, filter-only pages for Cricket Australia and Munster GAA,
a first capture that stops before today's session for snooker, and a golf hub that returned "No tips
found". All nineteen items are on the <a href="flagged.html">Flagged for review</a> page with links.</p>
"""
    page("index.html", "Summary", body, active="index.html")

    # ---------------------------------------------------------------- matches
    rows = ""
    linked = {f["olbg_event_id"]: f for f in fx if f["olbg_event_id"]}
    for l in lines["verified_lines"]:
        rows += (
            f"<tr><td>{e(sport_name[l['sport']])}</td><td>{e(l['competition'])}</td>"
            f"<td><strong>{e(l['name'])}</strong><div class='meta'>{e(l['venue'])}</div></td>"
            f"<td class='num'>{e(l['start'] or 'not published')}"
            f"{('<div class=meta>' + e(l['local_start']) + '</div>') if l.get('local_start') else ''}</td>"
            f"<td class='mono'>{e(l['start'] or '—')}</td>"
            f"<td><span class='chip ok'>confirmed</span><div class='meta'>{e(l['status'])}</div></td>"
            f"<td>{src_links(l['sources'])}</td></tr>"
        )
    for d in disc:
        f = linked.get(d["olbg_event_id"])
        cls = "ok" if f else "gap"
        lab = "confirmed above" if f else "discovery only"
        rows += (
            f"<tr><td>{e(sport_name[d['sport']])}</td><td>{e(d['competition_text'] or 'not published by OLBG')}</td>"
            f"<td>{e(d['name'])}<div class='meta'>OLBG pick: {e(d['olbg_pick'] or '—')} · "
            f"{e(d['olbg_market'] or '—')} · {e(d['olbg_tips'] or '—')} tips</div></td>"
            f"<td class='num'>{e(d['olbg_time_text'])}</td>"
            f"<td class='mono'>{e(f['official_start_utc']) if f and f.get('official_start_utc') else '<span class=blank>not confirmed</span>'}</td>"
            f"<td><span class='chip {cls}'>{lab}</span></td>"
            f"<td><a href='{e(d['olbg_url'])}'>olbg listing</a>"
            f"{(' ' + src_links(f['sources'])) if f else ''}</td></tr>"
        )
    body = f"""
<h1>Match list</h1>
<p class="lede">All {len(disc)} OLBG listings, plus the six fixtures confirmed on an official page. The first
block is the confirmed set; the long block below it is discovery only. OLBG times are reproduced exactly as
published because OLBG prints no timezone and was shown to mix conventions in one capture (flag F-CF-01), so
they are never converted to UTC here. Where an official start exists it is in its own column.</p>
<div class="tablewrap"><table>
<thead><tr><th>Sport</th><th>Competition</th><th>Match</th><th>OLBG time (as printed)</th><th>Official start (UTC)</th><th>Status</th><th>Source</th></tr></thead>
<tbody>{rows}</tbody></table></div>
<p class="meta">Rows marked "discovery only" have no official confirmation and therefore no published price.
The reason for each group of gaps is listed on <a href="flagged.html">Flagged for review</a>.</p>
"""
    page("matches.html", "Matches", body, active="matches.html")

    # ---------------------------------------------------------------- markets
    blocks_html = ""
    for l in lines["verified_lines"]:
        inner = ""
        for b in l["blocks"]:
            orow = ""
            for o in b["outcomes"]:
                orow += (
                    f"<tr><td><strong>{e(o['selection'])}</strong></td>"
                    f"<td class='num'>{('%.1f%%' % (o['p']*100)) if o.get('p') else '<span class=blank>—</span>'}</td>"
                    f"<td class='num'>{('%.3f' % o['decimal']) if o.get('decimal') else '<span class=blank>—</span>'}</td>"
                    f"<td class='num'>{am(o['american'])}</td><td>{chip(o['tier'])}</td>"
                    f"<td class='meta'>{e(o.get('note') or '')}</td></tr>"
                )
            notes = "".join(f"<li>{e(n)}</li>" for n in b.get("notes", []))
            inner += (
                f"<h4 style='margin:16px 0 6px'>{e(b['market'])} "
                f"<span class='pill'>{e(b['class'])} input</span></h4>"
                f"<div class='tablewrap'><table><thead><tr><th>Selection</th><th>p</th><th>Fair decimal</th>"
                f"<th>American</th><th>Tier</th><th>Note</th></tr></thead><tbody>{orow}</tbody></table></div>"
                f"{('<ul class=tight>' + notes + '</ul>') if notes else ''}"
            )
        blocks_html += f"""
<h2>{e(l['name'])}</h2>
<p class="meta">{e(l['competition'])} · {e(l['venue'])} · official start {e(l['start'] or l.get('local_start') or 'n/a')}
· sources {src_links(l['sources'])}</p>
<ul class="tight">{''.join(f"<li><strong>{e(f['k'])}</strong>: {e(f['v'])} <span class='meta'>[{e(f['src'])}]</span></li>" for f in l['facts'])}</ul>
<div class="card">{inner}</div>
"""

    body = f"""
<h1>Markets</h1>
<p class="lede">Eight market families were explicitly considered for every confirmed fixture: money line and
match winner, handicap, run line, puck line, match total, game total, set and frame scoring, and outrights. A market is only priced when an official
input supports it. Where it does not, the market is listed as withheld with the reason rather than filled
with a plausible-looking number.</p>
<div class="note"><strong>What is priced, and from what.</strong> NHL money lines come from the de-vigged
median of the three mutually consistent quote providers embedded in the league's own schedule feed. The MLB
game uses paired official regular-season run rates in an independent-Poisson run model with the draw removed.
URC match winners come from one verified round of results with a declared shrinkage, a declared three-point
home advantage and a declared 14-point standard deviation. Nothing else is priced on official input.</div>
{blocks_html}

<h2>Markets we investigated and withheld</h2>
<div class="tablewrap"><table>
<thead><tr><th>Sport</th><th>Market</th><th>Status</th><th>Reason</th></tr></thead><tbody>
<tr><td>Ice hockey</td><td>Puck line, game total</td><td><span class="chip gap">withheld</span></td><td>The league feed carries no goal-rate input for either club and no official standings rows for them were read.</td></tr>
<tr><td>Rugby Union</td><td>Handicap, match total</td><td><span class="chip gap">withheld</span></td><td>One verified round cannot support a scoring-margin line or a club-level total; only a 54.6-point league mean exists.</td></tr>
<tr><td>Cricket</td><td>All</td><td><span class="chip gap">withheld</span></td><td>No fixture could be tied to a board or tour page; no player or innings data was read.</td></tr>
<tr><td>Darts</td><td>All</td><td><span class="chip gap">withheld</span></td><td>pdc.tv served a consent wall; no draw, no averages, no match list.</td></tr>
<tr><td>Snooker</td><td>All</td><td><span class="chip gap">withheld</span></td><td>Today's session sits beyond the first capture of the WST match list.</td></tr>
<tr><td>Basketball</td><td>All</td><td><span class="chip gap">withheld</span></td><td>EuroLeague game centre is client-rendered; the NBA scoreboard endpoint returned HTTP 500.</td></tr>
<tr><td>Tennis</td><td>All</td><td><span class="chip gap">withheld</span></td><td>OLBG rows carry no tournament and the tours listed different matches at the same time.</td></tr>
<tr><td>Gaelic Sports</td><td>All</td><td><span class="chip gap">withheld</span></td><td>Munster GAA index page only; no fixture detail reached.</td></tr>
<tr><td>Greyhounds</td><td>All</td><td><span class="chip gap">withheld</span></td><td>GBGB publishes meetings, not per-race runners; no runner-level source was read.</td></tr>
<tr><td>Volleyball, Handball</td><td>All</td><td><span class="chip gap">withheld</span></td><td>No league page was reached; indicative prices only, permanently Low.</td></tr>
<tr><td>Golf, Rugby League</td><td>All</td><td><span class="chip gap">withheld</span></td><td>No listings: golf returned "No tips found"; rugby league had only 2027 outrights.</td></tr>
</tbody></table></div>
"""
    page("markets.html", "Markets", body, active="markets.html")

    # ------------------------------------------------------------- confidence
    oob = lines["out_of_band"]
    oob_rows = "".join(
        f"<tr><td>{e(sport_name[o['sport']])}</td><td>{e(o['name'])}</td><td>{e(o['market'])}</td>"
        f"<td>{e(o['selection'])}</td><td class='num'>{o['p']*100:.1f}%</td>"
        f"<td class='num'>{am(o['american'])}</td><td>{chip('Medium')}</td>"
        f"<td class='meta'>excluded from High: shorter than the −250 floor</td></tr>" for o in oob
    )
    near = [(l, b, o) for (l, b, o) in best if 0.55 <= o["p"] < 0.70]
    near_rows = "".join(
        f"<tr><td>{e(sport_name[l['sport']])}</td><td>{e(l['name'])}</td><td>{e(o['selection'])}</td>"
        f"<td class='num'>{o['p']*100:.1f}%</td><td class='num'>{am(o['american'])}</td>"
        f"<td>{chip(o['tier'])}</td></tr>" for l, b, o in near
    )
    body = f"""
<h1>Confidence</h1>
<p class="lede">The grading rule is applied mechanically to every published price. It is deliberately hard to
satisfy, and today nothing satisfies the top tier. This page shows the rule, the distribution, and exactly
which selections fell where and why.</p>
<div class="card">
<h3 style="margin-top:0">The rule, as written</h3>
<ul class="tight">
<li><strong>High</strong> — probability at least 70% <em>and</em> American price between −250 and +10,000
<em>and</em> the inputs came from an official page read this session.</li>
<li><strong>Medium</strong> — probability between 62% and 70%, official inputs.</li>
<li><strong>Low</strong> — everything else, including every indicative price built from tip shares.</li>
</ul>
<p class="meta" style="margin:10px 0 0">Because the price floor and the probability floor meet, the eligible
High band is only 70.0%–71.4%. A 75% shot is too short at roughly −300; a 90% shot is far too short. That is a
property of the brief's own definition, not of this desk.</p>
</div>
<div class="kpis">
<div class="kpi"><b>{tiers['High']}</b><small>High</small></div>
<div class="kpi"><b>{tiers['Medium']}</b><small>Medium</small></div>
<div class="kpi"><b>{tiers['Low']}</b><small>Low</small></div>
<div class="kpi"><b>{len(oob)}</b><small>at 70%+ but outside the price window</small></div>
</div>

<h2>At 70% or better, but excluded by the price floor</h2>
<div class="tablewrap"><table>
<thead><tr><th>Sport</th><th>Fixture</th><th>Market</th><th>Selection</th><th>p</th><th>American</th><th>Actual tier</th><th>Why not High</th></tr></thead>
<tbody>{oob_rows or '<tr><td colspan="8" class="blank">none today</td></tr>'}</tbody></table></div>

<h2>The next band down, 55%–70%</h2>
<div class="tablewrap"><table>
<thead><tr><th>Sport</th><th>Fixture</th><th>Selection</th><th>p</th><th>American</th><th>Tier</th></tr></thead>
<tbody>{near_rows}</tbody></table></div>

<h2>Why the confirmed set is so small</h2>
<p>A fixture only enters this section if an official page named it, dated it and gave us an input. On 23
October that was two NHL games from the league's schedule feed, one MLB World Series game from MLB's schedule
and statistics services, and three United Rugby Championship matches from the competition's own match centre.
Everything else failed one of those three tests, and each failure is recorded by name on
<a href="flagged.html">Flagged for review</a>.</p>
<p>It is worth being blunt about the size of the sample. Six fixtures cannot produce five picks per sport,
and no amount of writing can change that. What the desk can do — and did — is publish 107 clearly labelled
indicative prices so the whole board is visible, keep every one of them at Low, and explain the arithmetic
instead of hiding it.</p>
"""
    page("confidence.html", "Confidence", body, active="confidence.html")

    # ------------------------------------------------------------ predictions
    phtml = ""
    for p in preds:
        facts = "".join(
            f"<li>{e(f['text'])} <a href='{e(src_by_id[f['src']]['url'])}'>[{e(f['src'])}]</a></li>"
            for f in p["facts"]
        )
        gaps = "".join(f"<li>{e(g)}</li>" for g in p["open_gaps"])
        pchip = chip(p["tier"])
        phtml += f"""
<div class="pred">
<h3>{e(p['match'])}</h3>
<p class="meta">{e(p['competition'])} · {e(sport_name[p['sport']])} · {e(p['words'])} words ·
{pchip} · p {p['p']*100:.1f}% · fair decimal {p['decimal']:.3f} · {am(p['american'])}
· <a href="markets.html">market detail</a></p>
<p><strong>Selection: {e(p['selection'])}</strong></p>
<p>{e(p['body'])}</p>
<details><summary class="meta">Evidence trail ({len(p['facts'])} source-linked facts) and open gaps</summary>
<ul class="tight">{facts}</ul>
<p class="meta" style="margin-bottom:2px">Open gaps</p>
<ul class="tight">{gaps}</ul>
</details>
<p class="meta">{e(p['band_note'])}</p>
</div>
"""
    body = f"""
<h1>Predictions</h1>
<p class="lede">{len(preds)} written selections, each at least 30 words, each with a source-linked fact trail a
reader can click through to the governing body. They are written for the selections this desk could support,
not for a quota.</p>
<div class="crit"><p style="margin:0"><strong>Honest framing.</strong> The brief asks for five High-confidence
writes per sport. There are no High selections today (see <a href="confidence.html">Confidence</a>), so these
seven cover the strongest supported picks instead — one Medium and six Low. Treating them as a High set would
be a misrepresentation of their tier, and the tier is printed on every card.</p></div>
{phtml}
<h2>What is missing from these writes</h2>
<p>Three things the brief asks for are absent because no official page published them this session: team news
and injuries, player-level availability, and verified league tables for the clubs involved. Rather than
paraphrase a preview article, those gaps are named on each card. The one exception is baseball, where the
announced starting pitchers are on MLB's own schedule record.</p>
"""
    page("predictions.html", "Predictions", body, active="predictions.html")

    # --------------------------------------------------------------- analysis
    per_sport = "".join(
        f"<tr><td>{e(s['name'])}</td><td class='num'>{len(disc_by_sport.get(s['key'], []))}</td>"
        f"<td class='num'>{len(fx_by_sport.get(s['key'], []))}</td>"
        f"<td class='num'>{sum(1 for i in lines['indicative'] if i['sport'] == s['key'] and i.get('p'))}</td>"
        f"<td>{'official input' if fx_by_sport.get(s['key']) else 'no official input'}</td></tr>"
        for s in sports
    )
    body = f"""
<h1>Analysis</h1>
<p class="lede">What the reverse-engineering pass found, what it could not find, and what would change the
conclusions.</p>

<h2>1. The OLBG surface is a discovery layer, and a leaky one</h2>
<p>Every in-scope sport resolves through the same template: a sport hub keyed on a case-sensitive slug and an
integer id, event cards with a top tip, a market name, a tip count and a percentage, and an event route that
can be opened for the full market list. That structure held for all fifteen hubs. What it does not give you is
anything you can rely on: the tip percentage is a vote share, the time has no timezone, and the list is not
cleaned of games that have already started or, in the NHL's case, games that do not exist on the official
slate (F-CF-04).</p>

<h2>2. Time handling is the sharpest defect</h2>
<p>Inside one capture, OLBG rendered a 17:12 Towcester race as 12:12 (a US-Eastern rendering), a set of URC
matches at 14:45 that the URC itself prints as 14:45 local UK and Irish time, and a Formula 1 race at 16:00
that is 16:00 at the circuit in Austin. Any pipeline that adds a fixed offset to these strings will be wrong
for at least two of the three. This desk publishes the string verbatim and takes UTC only from the governing
body (F-CF-01).</p>

<h2>3. The NHL feed contradicts itself on price</h2>
<p>The league's schedule response embeds six prices per team. For Montreal at Chicago, three of them make
Montreal a −162 to −170 favourite and three make Chicago a 1.59 favourite. There is no way to reconcile them
from the payload, so the desk used only the three American-quote providers, published the contradiction on the
row, and did not use any of it as a probability without saying so (F-CF-03).</p>

<h2>4. Verification yield, by sport</h2>
<div class="tablewrap"><table>
<thead><tr><th>Sport</th><th>OLBG listings</th><th>Officially confirmed</th><th>Indicative prices</th><th>Input class</th></tr></thead>
<tbody>{per_sport}</tbody></table></div>
<p class="meta">Six confirmed fixtures out of 135 listings, a 4.4% yield. That is a property of the sources,
not of the effort: most of the twelve missing sports sit behind a wall that a single fetch cannot pass.</p>

<h2>5. The band problem the brief anticipated</h2>
<p>The brief notes that many "high confidence" picks are simply short-priced favourites and asks for the
−250 to +10,000 window. Applying that window honestly is what produced a zero. The desk's strongest single
selection, Edinburgh at home to the Lions, lands around 85% and prices near −567: exactly the short favourite
the window is designed to exclude. If the intent is "five picks a day that are likely to win", the window is
not the binding constraint and should be relaxed; if the intent is value, then a 70% floor combined with a
−250 floor is close to self-cancelling.</p>

<h2>6. What would change these conclusions</h2>
<ul class="tight">
<li>An official team-news feed for each league, which is the single largest gap (F-CF-16).</li>
<li>Access to pdc.tv and wst.tv session pages, which would unlock darts and snooker pricing immediately.</li>
<li>A league table for the URC, the French and German handball leagues and PlusLiga, which would replace the
one-round shrinkage with a real rating.</li>
<li>A second capture of the OLBG hubs later in the day, since several rows will expire and new ones appear.</li>
</ul>
"""
    page("analysis.html", "Analysis", body, active="analysis.html")

    # ---------------------------------------------------------------- flagged
    rows = ""
    for f in flags:
        rows += (
            f"<tr><td class='mono'>{e(f['id'])}</td>"
            f"<td><span class='chip {'gap' if f['sev']=='high' else ('medium' if f['sev']=='medium' else 'low')}'>"
            f"{e(f['sev'])}</span></td><td>{e(sport_name.get(f['sport'], f['sport']))}</td>"
            f"<td><strong>{e(f['title'])}</strong><div class='meta'>{e(f['detail'])}</div></td>"
            f"<td class='mono'>{e(', '.join(f['rows']))}</td><td>{src_links(f['src'])}</td></tr>"
        )
    body = f"""
<h1>Flagged for review</h1>
<p class="lede">{len(flags)} items, of which {n_high} are high severity. Each carries the rows it affects and
the source it was checked against. Nothing here blocks the release; it is the list of things a human should
look at before treating any number on this site as settled.</p>
<div class="tablewrap"><table>
<thead><tr><th>ID</th><th>Severity</th><th>Sport</th><th>Finding</th><th>Rows</th><th>Source</th></tr></thead>
<tbody>{rows}</tbody></table></div>
<h2>How to read a flag</h2>
<p>A flag is not an error in the arithmetic. It is a statement that the underlying evidence is missing,
contradictory or inaccessible. Some flags (F-CF-01, F-CF-03, F-CF-05) describe defects in the sources
themselves; others (F-CF-08 to F-CF-13) describe barriers that stopped this session short. Fixing them is
future work, not a correction to today's numbers.</p>
"""
    page("flagged.html", "Flagged for review", body, active="flagged.html")

    # ---------------------------------------------------------------- sources
    srows = "".join(
        f"<tr><td class='mono'>{e(s['id'])}</td><td>{e(s['org'])}</td>"
        f"<td><a href='{e(s['url'])}'>{e(s['url'][:92])}{'…' if len(s['url'])>92 else ''}</a></td>"
        f"<td><span class='chip {'ok' if s['role'].startswith('official') else 'low'}'>{e(s['role'])}</span></td>"
        f"<td class='num'>{e(s['observed'])}</td><td class='meta'>{e(s['method'])}<br>{e(s['note'])}</td></tr>"
        for s in sorted(sources, key=lambda x: (not x["role"].startswith("official"), x["id"]))
    )
    body = f"""
<h1>Sources</h1>
<p class="lede">{len(sources)} sources were read this session. Sixteen entries, because some topics needed
more than one page and some were opened only to record that they failed. The observation window is the
session's 16:17–16:40 UTC; the "observed" column is the tighter window per source.</p>
<div class="tablewrap"><table>
<thead><tr><th>ID</th><th>Organisation</th><th>URL</th><th>Role</th><th>Observed (UTC)</th><th>Method and what it contained</th></tr></thead>
<tbody>{srows}</tbody></table></div>
<h2>What counts as official, and what does not</h2>
<p>A league, governing body, tour or club is official. A newspaper, a preview blog, an odds comparison site
and OLBG itself are not, no matter how accurate they usually are. OLBG appears in this table only in the
discovery role, because it is the only place where the brief's fifteen sports are enumerated in one list.</p>
"""
    page("sources.html", "Sources", body, active="sources.html")

    # ------------------------------------------------------------ methodology
    body = f"""
<h1>Method</h1>
<p class="lede">Short enough to audit in five minutes. If a number on this site cannot be reproduced from the
rules below and the linked source, it should not be trusted.</p>

<h2>Discovery versus fact</h2>
<p>OLBG says which matches exist. It is never the source of a date, a venue, a record, a price or a result.
Every fact on this site traces to a source id on the <a href="sources.html">Sources</a> page, and the role
column marks which of those are official.</p>

<h2>Two input classes, never mixed</h2>
<div class="grid2">
<div class="card"><span class="tag">market class</span>
<p>An official page confirmed the fixture and supplied a quantitative input. Only these rows can be graded
Medium or High. Today: two NHL games, one MLB game, three URC matches.</p></div>
<div class="card"><span class="tag">consensus class</span>
<p>No official input exists; the only available signal is OLBG's public tip share. The share is shrunk 50%
toward 0.5, capped into 0.50–0.90, published with the word "indicative", and permanently graded Low. It is a
map of the board, not a probability.</p></div>
</div>

<h2>Price arithmetic</h2>
<ul class="tight">
<li>Fair decimal = 1 / p. American = −100p/(1−p) above 50% and +100(1−p)/p below it. No margin, no clipping.</li>
<li>Probability is never rounded before the American conversion, so the price band test uses the unrounded value.</li>
<li>NHL: the American-quote providers in the league feed (−170 / −170 / −162 against +138 / +142 / +134, and
+105 / +105 / +106 against −129 / −125 / −128) are de-vigged pairwise per provider, then the median of the
three normalised probabilities is taken.</li>
<li>MLB: expected runs for each side are the mean of that side's scoring rate and the opponent's concession
rate, over 162 games. Independent Poisson scores, tie mass removed, then read off for the money line, the 1.5
run line and a half-run total centred on the expectation. A log5 calculation on season win percentages is
printed alongside as a cross-check.</li>
<li>URC: each club's verified Round 3 margin is shrunk 25% toward zero, a declared three-point home advantage
is added, and the result is mapped through a normal with a declared 14-point standard deviation. Output is
capped at 85% so that a one-round sample cannot manufacture a false certainty.</li>
</ul>

<h2>Grading</h2>
<p>High needs p ≥ 0.70, an American price no shorter than −250, and market-class inputs. Medium is 0.62–0.70 on
market-class inputs. Everything else is Low. The rule is applied mechanically; there is no manual override and
no discretionary promotion.</p>

<h2>Expiry and staleness</h2>
<p>This is a single snapshot taken between 16:17 and 16:40 UTC on 23 October 2026. Prices describe that moment.
Fixtures move, starting pitchers change and lines shift. Every page carries the snapshot stamp; nothing here
refreshes itself.</p>

<h2>What is deliberately absent</h2>
<ul class="tight">
<li>Injury, suspension and team-news data: none was published on the pages reached, so none is asserted.</li>
<li>Bookmaker quotes, availability and edge: this desk publishes fair prices, not offers.</li>
<li>Staking advice, guaranteed returns, or any suggestion that a Low selection is a strong one.</li>
</ul>
"""
    page("methodology.html", "Method", body, active="methodology.html")

    # ------------------------------------------------------------ sport pages
    for s in sports:
        k = s["key"]
        sport_fx = fx_by_sport.get(k, [])
        sport_disc = disc_by_sport.get(k, [])
        indic = [i for i in lines["indicative"] if i["sport"] == k]
        priced = [i for i in indic if i.get("p")]
        t5 = lines["top5_by_sport"].get(k, [])
        verified_block = ""
        for l in lines["verified_lines"]:
            if l["sport"] != k:
                continue
            orows = ""
            for b in l["blocks"]:
                for o in b["outcomes"]:
                    orows += (
                        f"<tr><td>{e(b['market'])}</td><td>{e(o['selection'])}</td>"
                        f"<td class='num'>{('%.1f%%' % (o['p']*100)) if o.get('p') else '<span class=blank>—</span>'}</td>"
                        f"<td class='num'>{('%.3f' % o['decimal']) if o.get('decimal') else '<span class=blank>—</span>'}</td>"
                        f"<td class='num'>{am(o['american'])}</td><td>{chip(o['tier'])}</td>"
                        f"<td class='meta'>{e(o.get('note') or '')}</td></tr>"
                    )
            verified_block += f"""
<h3>{e(l['name'])}</h3>
<p class="meta">{e(l['competition'])} · {e(l['venue'])} · {e(l['start'] or l.get('local_start') or '')} ·
{src_links(l['sources'])}</p>
<div class="tablewrap"><table>
<thead><tr><th>Market</th><th>Selection</th><th>p</th><th>Fair decimal</th><th>American</th><th>Tier</th><th>Note</th></tr></thead>
<tbody>{orows}</tbody></table></div>"""

        if not verified_block:
            verified_block = ('<div class="crit"><p style="margin:0"><strong>No fixture in this sport could be '
                              'confirmed on an official page this session.</strong> The listings below are '
                              'discovery only. Indicative prices exist so the board is visible, but they are '
                              'a shrunk tip share, are graded Low, and are not evidence.</p></div>')

        drows = ""
        linked = {f["olbg_event_id"]: f for f in sport_fx if f["olbg_event_id"]}
        for d in sport_disc:
            ip = next((i for i in indic if i["olbg_event_id"] == d["olbg_event_id"]), None)
            f = linked.get(d["olbg_event_id"])
            pm = (f"{ip['p']*100:.1f}%" if ip and ip.get("p") else '<span class="blank">—</span>')
            pr = (am(ip["american"]) if ip and ip.get("american") is not None else '<span class="blank">—</span>')
            stat = ('<span class="chip ok">official</span>' if f
                    else '<span class="chip gap">unconfirmed</span>')
            drows += (
                f"<tr><td>{e(d['name'])}<div class='meta'>{e(d['competition_text'] or 'competition not published')}</div></td>"
                f"<td class='num'>{e(d['olbg_time_text'])}</td><td>{e(d['olbg_pick'] or '—')}</td>"
                f"<td class='meta'>{e(d['olbg_market'] or '—')}</td><td class='num'>{e(d['olbg_tips'] or '—')}</td>"
                f"<td class='num'>{e(str(d['olbg_pct']) + '%') if d['olbg_pct'] is not None else '<span class=blank>—</span>'}</td>"
                f"<td class='num'>{pm}</td><td class='num'>{pr}</td>"
                f"<td>{stat}</td>"
                f"<td><a href='{e(d['olbg_url'])}'>OLBG</a></td></tr>"
            )
        t5rows = "".join(
            f"<tr><td class='num'>{i+1}</td><td>{e(r['name'])}</td><td>{e(r['market'])}</td>"
            f"<td>{e(r['selection'])}</td><td class='num'>{r['p']*100:.1f}%</td>"
            f"<td class='num'>{am(r['american'])}</td><td>{chip(r['tier'])}</td>"
            f"<td class='meta'>{'official input' if r['class'] == 'market' else 'indicative only'}</td></tr>"
            for i, r in enumerate(t5)
        ) or '<tr><td colspan="8" class="blank">No priced row for this sport today.</td></tr>'

        body = f"""
<h1>{e(s['name'])}</h1>
<p class="lede">OLBG sport id {s['olbg_id']} · {len(sport_disc)} listings captured ·
{len(sport_fx)} officially confirmed · {len(priced)} indicative prices · best originated probability
{('%.1f%%' % (t5[0]['p']*100)) if t5 else '—'}.
<a href="https://www.olbg.com/betting-tips/{e(s['olbg_slug'])}/{s['olbg_id']}">OLBG hub</a></p>

<h2>Top five by originated probability</h2>
<div class="tablewrap"><table>
<thead><tr><th>#</th><th>Match / event</th><th>Market</th><th>Selection</th><th>p</th><th>American</th><th>Tier</th><th>Input</th></tr></thead>
<tbody>{t5rows}</tbody></table></div>
<p class="meta">This is the desk's answer to "the five highest-confidence picks for this sport". Where the
input column says "indicative only", the selection cannot be graded above Low no matter how high its
probability looks — the number is a shrunk tip share, not a measurement.</p>

<h2>Officially confirmed fixtures and originated markets</h2>
{verified_block}

<h2>All {s['name']} listings captured from OLBG</h2>
<div class="tablewrap"><table>
<thead><tr><th>Match / event</th><th>OLBG time</th><th>OLBG pick</th><th>Market</th><th>Tips</th><th>Share</th><th>Our p</th><th>American</th><th>Status</th><th>Link</th></tr></thead>
<tbody>{drows or '<tr><td colspan="10" class="blank">No listings were published on this hub.</td></tr>'}</tbody></table></div>
"""
        page(f"sports/{k}.html", s["name"], body, active="", prefix="../")

    # cross-link sport pages from index? already in coverage table
    print("pages written:", 9 + len(sports))


if __name__ == "__main__":
    main()
