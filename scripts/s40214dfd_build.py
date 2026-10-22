"""Build the 40214dfd dashboard, category pages and review pages.

Output is written to 40214dfd/ only. Nothing in this module writes to the canonical root, to
pipeline/, to data/current/ or to another session's namespace.
"""
import json
import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "40214dfd"
DATA = ROOT / "data" / "40214dfd" / "desk.json"

e = html.escape

CSS = """
:root{--ink:#122029;--muted:#5b6b77;--line:#dde5ec;--bg:#f4f7fa;--card:#ffffff;
--navy:#0b2540;--accent:#1f6feb;--high:#0b6b3a;--highbg:#e5f6ec;--med:#8a4b00;--medbg:#fdf1e0;
--low:#40505c;--lowbg:#eef2f6;--flag:#a11b2b;--flagbg:#fdecee}
*{box-sizing:border-box}
body{margin:0;font:15px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:var(--ink);background:var(--bg)}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
header.top{background:var(--navy);color:#fff;padding:16px 22px 12px}
header.top .brand{display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px;align-items:baseline}
header.top h1{font-size:19px;margin:0;font-weight:650;letter-spacing:.2px}
header.top .meta{font-size:12.5px;color:#b9cde0}
nav.main{margin-top:10px;display:flex;flex-wrap:wrap;gap:4px}
nav.main a{color:#d9e8f7;font-size:13.5px;padding:5px 9px;border-radius:6px}
nav.main a:hover{background:#16395c;text-decoration:none}
nav.main a.on{background:#1f4f7d;color:#fff;font-weight:600}
main{max-width:1240px;margin:0 auto;padding:22px 18px 60px}
h2{font-size:17px;margin:26px 0 10px}
h3{font-size:15px;margin:18px 0 8px}
p.lede{font-size:15.5px;color:#31424f;max-width:82ch}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:14px 0}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:13px 14px}
.kpi .n{font-size:24px;font-weight:700;line-height:1.1}
.kpi .l{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin:14px 0}
.wrap{overflow-x:auto;border:1px solid var(--line);border-radius:10px;background:var(--card)}
table{border-collapse:collapse;width:100%;font-size:13.5px}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{background:#eaf1f8;font-size:12px;text-transform:uppercase;letter-spacing:.4px;color:#2c4051;
position:sticky;top:0}
tbody tr:hover{background:#f8fbfd}
td.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.badge{display:inline-block;padding:2px 7px;border-radius:20px;font-size:11.5px;font-weight:700;
letter-spacing:.3px;text-transform:uppercase}
.b-high{background:var(--highbg);color:var(--high)}
.b-med{background:var(--medbg);color:var(--med)}
.b-low{background:var(--lowbg);color:var(--low)}
.b-none{background:#eef0f2;color:#68757f}
.muted{color:var(--muted)}
.small{font-size:12.5px}
.flag{border-left:4px solid var(--flag);background:var(--flagbg);padding:12px 16px;border-radius:8px;margin:12px 0}
.flag h4{margin:0 0 6px;font-size:14.5px;color:var(--flag)}
.note{border-left:4px solid var(--accent);background:#eef5ff;padding:12px 16px;border-radius:8px;margin:12px 0}
.pred{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin:14px 0}
.pred h3{margin:0 0 4px;font-size:16px}
.pred .sel{font-weight:700;color:var(--high)}
.pred .body{font-size:15px;margin:8px 0}
.pred ul{margin:8px 0 0 18px;padding:0}
.pred li{font-size:12.5px;color:var(--muted);margin:2px 0}
footer{max-width:1240px;margin:0 auto;padding:18px;color:var(--muted);font-size:12.5px;
border-top:1px solid var(--line)}
.tag{font-size:11px;padding:2px 6px;border-radius:4px;background:#eef2f6;color:#46596a}
"""

NAV = [
    ("index.html", "Dashboard"),
    ("matches.html", "Matches"),
    ("markets.html", "Markets"),
    ("predictions.html", "High predictions"),
    ("flagged.html", "Flagged for review"),
    ("coverage.html", "Sport coverage"),
    ("methodology.html", "Methodology"),
    ("sources.html", "Sources"),
]

SPORT_NAV = [
    ("ice-hockey.html", "Ice hockey"),
    ("baseball.html", "Baseball"),
    ("basketball.html", "Basketball"),
    ("snooker.html", "Snooker"),
]


def page(title, body, here, prefix=""):
    nav = "".join(
        f'<a class="{"on" if href == here else ""}" href="{prefix}{href}">{e(label)}</a>'
        for href, label in NAV)
    sports = "".join(f'<a href="{prefix}sports/{h}">{e(l)}</a>' for h, l in SPORT_NAV)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} · OLBG evidence desk 40214dfd</title>
<meta name="description" content="Independent, source-linked match research for 22 October 2026. Originated fair prices, explicit confidence tiers and a flagged-for-review register.">
<style>{CSS}</style></head><body>
<header class="top"><div class="brand">
<h1>OLBG evidence desk · session 40214dfd</h1>
<span class="meta">As of 2026-10-22 12:45 UTC · 17 sports in scope · prices are originated fair prices, never bookmaker offers</span>
</div>
<nav class="main">{nav}<a href="{prefix}index.html#sports">Sports ▾</a></nav>
<nav class="main small">{sports}</nav>
</header><main>{body}</main>
<footer>Independent research. Not affiliated with OLBG. No guarantee of profit and no staking advice.
Every table row links to the official page its facts came from. Blank means unverified — never zero, never inferred.
Built by session 40214dfd-olbg1 · <a href="../index.html">Canonical project dashboard</a></footer>
</body></html>"""


def tier_badge(tier):
    if not tier:
        return '<span class="badge b-none">unrated</span>'
    return f'<span class="badge b-{ {"high": "high", "medium": "med", "low": "low"}[tier] }">{e(tier)}</span>'


def odds(a):
    if a is None:
        return "—"
    return f"+{a}" if a > 0 else str(a)


def dt(ts):
    if not ts:
        return "—"
    return ts.replace("T", " ").replace(":00Z", "Z")


def main():
    desk = json.loads(DATA.read_text())
    OUT.mkdir(exist_ok=True)
    (OUT / "sports").mkdir(exist_ok=True)
    assets = OUT / "assets"
    assets.mkdir(exist_ok=True)
    (assets / "style.css").write_text(CSS)

    c = desk["counts"]
    fixtures = {f["id"]: f for f in desk["fixtures"]}
    preds = {p["match"]["selection"] + "|" + str(p["match"]["line"]) + "|" + p["fixture_id"]: p
             for p in desk["predictions"]}

    # ------------------------------------------------------------------ dashboard
    top_rows = []
    for h in desk["high_picks"][:7]:
        fx = fixtures[h["fixture_id"]]
        top_rows.append(
            "<tr>"
            f'<td>{e(fx["competition"])}</td>'
            f'<td>{e(fx["away"])} @ {e(fx["home"])}<br><span class="small muted">{e(dt(fx["start_utc"]))}</span></td>'
            f'<td><strong>{e(h["selection"])}</strong><br><span class="small muted">{e(h["market_label"])}</span></td>'
            f'<td class="num">{odds(h["american"])}<br><span class="small muted">{h["probability"]*100:.2f}%</span></td>'
            f'<td>{tier_badge("high")}</td>'
            f'<td><a href="{e(h["source_url"])}" rel="noopener">official source</a></td>'
            "</tr>")
    cov_rows = []
    for r in desk["coverage"]:
        status = r["status"]
        cls = "b-high" if status == "priced" else ("b-med" if "listed" in status else "b-none")
        src = (f'<a href="{e(r["source_url"])}" rel="noopener">official</a>'
               if r["source_url"] else '<span class="muted">none read</span>')
        cov_rows.append(
            f'<tr><td>{e(r["sport"])}</td><td><span class="badge {cls}">{e(status)}</span></td>'
            f'<td class="num">{r["rows"]}</td><td class="small">{e(r["detail"])}</td><td>{src}</td></tr>')

    index_body = f"""
<p class="lede">This desk re-read official league, tour and governing-body pages on 22 October 2026,
originated its own fair prices for every fixture it could verify, graded each selection, and wrote
full predictions only for the selections that clear the brief's two High-confidence rules at the same
time. {17 - c["sports_listed"]} of the seventeen in-scope sports produced no verified row in this
session; each is listed with the reason on the coverage page rather than filled with invention.</p>

<div class="grid">
  <div class="kpi"><div class="n">{c["priced_fixtures"]}</div><div class="l">priced fixtures</div></div>
  <div class="kpi"><div class="n">{c["markets"]}</div><div class="l">markets originated</div></div>
  <div class="kpi"><div class="n">{c["outcomes"]}</div><div class="l">priced outcomes</div></div>
  <div class="kpi"><div class="n">{c["high_selections"]}</div><div class="l">High selections</div></div>
  <div class="kpi"><div class="n">{c["predictions"]}</div><div class="l">written predictions</div></div>
  <div class="kpi"><div class="n">{c["flagged"]}</div><div class="l">flagged findings</div></div>
</div>

<div class="note"><strong>How a High pick is allowed to be labelled.</strong>
American −250 is decimal 1.40, which is 71.43%. A genuine chance above 71.43% always prices
<em>shorter</em> than −250, so the brief's two High rules only overlap between 70.00% and 71.43%.
This desk issues High only inside that overlap, with verified inputs on both sides and a written
prediction, and publishes every near miss separately on the
<a href="flagged.html">Flagged for review</a> page. The arithmetic is worked through on the
<a href="methodology.html">Methodology</a> page.</div>

<h2>High-confidence selections</h2>
<div class="wrap"><table><thead><tr><th>Competition</th><th>Fixture (UTC)</th><th>Selection</th>
<th class="num">Price / model</th><th>Tier</th><th>Source</th></tr></thead>
<tbody>{''.join(top_rows)}</tbody></table></div>
<p class="small muted">Full write-ups, each over 30 words and built only from facts read on official
pages, are on <a href="predictions.html">High predictions</a>.</p>

<h2 id="sports">Sport coverage at a glance</h2>
<div class="wrap"><table><thead><tr><th>Sport</th><th>Status</th><th class="num">Rows</th>
<th>What was verified</th><th>Official source</th></tr></thead>
<tbody>{''.join(cov_rows)}</tbody></table></div>
<p class="small muted">Out of scope by the brief: {e(", ".join(desk["excluded"]))}.</p>

<h2>What this desk will not do</h2>
<div class="card"><ul>
<li>It will not turn a −311 favourite into a High pick to fill a quota. That selection is on the flagged page with its price.</li>
<li>It will not print a start time whose timezone the official page does not state. The eight snooker matches are listed with a blank clock.</li>
<li>It will not quote a bookmaker price. Every price here is an originated fair price, and the only market prices shown are the ones NHL.com itself displays, labelled as such.</li>
<li>It will not claim a full fixture list for a sport whose official page did not render one.</li>
</ul></div>
"""
    (OUT / "index.html").write_text(page("Dashboard", index_body, "index.html"))

    # ------------------------------------------------------------------ matches
    mrows = []
    for fx in desk["fixtures"]:
        pk = next((p for p in desk["picks"] if p["fixture_id"] == fx["id"]), None)
        if pk:
            h, w = pk["headline"], pk["winner_view"]
            pick_cell = (f'<strong>{e(h["selection"])}</strong><br>'
                         f'<span class="small muted">{e(odds(h["american"]))} · {h["probability"]*100:.2f}% · {e(h["market"])}</span>')
            tier_cell = tier_badge(h["confidence"])
            win_cell = (f'{e(w["selection"])} <span class="small muted">{e(odds(w["american"]))}</span><br>'
                        f'<span class="small muted">{w["probability"]*100:.1f}% · {e(w["confidence"])}</span>')
        else:
            pick_cell = '<span class="muted">no line originated</span>'
            tier_cell = '<span class="badge b-none">unrated</span>'
            win_cell = '<span class="muted">—</span>'
        mrows.append(
            "<tr>"
            f'<td>{e(fx["sport"])}<br><span class="small muted">{e(fx["competition"])}</span></td>'
            f'<td>{e(dt(fx["start_utc"]))}<br><span class="small muted">{e(fx["start_basis"])}</span></td>'
            f'<td>{e(fx["away"])} @ {e(fx["home"])}'
            + (f'<br><span class="small muted">records {e(fx["away_record"] or "—")} / {e(fx["home_record"] or "—")}</span>' if fx.get("away_record") else '')
            + '</td>'
            f'<td>{pick_cell}</td><td>{tier_cell}</td><td>{win_cell}</td>'
            f'<td><a href="{e(fx["source_urls"][0])}" rel="noopener">source</a></td>'
            "</tr>")
    matches_body = f"""
<p class="lede">Every fixture this desk could verify, with the selection it publishes and the
separate match-winner view. The headline selection is the strongest graded selection that respects
the brief; the winner column is what the record model says about the match result itself.
{desk["priced_fixture_count"]} fixtures carry originated prices; {desk["unpriced_fixture_count"]}
are listed without a price because an official input is missing.</p>
<div class="wrap"><table><thead><tr><th>Sport</th><th>Start (UTC / basis)</th><th>Fixture</th>
<th>Headline selection</th><th>Tier</th><th>Match-winner view</th><th>Source</th></tr></thead>
<tbody>{''.join(mrows)}</tbody></table></div>
<div class="flag"><h4>Time bases are not all equal</h4>
<p>NHL games marked <code>derived_from_declared_offset</code> were printed by NHL.com in Eastern
Daylight Time with a declared −04:00 offset and converted arithmetically; four of the twelve were
also confirmed directly through the NHL schedule API. EuroLeague tips were printed in CEST and
converted at UTC+2. MLB prints “ET” and those rows are marked as such. Snooker clocks carry no
timezone at all and stay blank.</p></div>
"""
    (OUT / "matches.html").write_text(page("Matches", matches_body, "matches.html"))

    # ------------------------------------------------------------------ markets
    mkt_rows = []
    for fx in desk["fixtures"]:
        if not fx["markets"]:
            continue
        name = f'{fx["away"]} @ {fx["home"]}'
        for mk in fx["markets"]:
            for i, o in enumerate(mk["outcomes"]):
                mkt_rows.append(
                    "<tr>"
                    + (f'<td rowspan="{len(mk["outcomes"])}">{e(name)}<br><span class="small muted">{e(fx["competition"])}</span></td>' if i == 0 else "")
                    + (f'<td rowspan="{len(mk["outcomes"])}">{e(mk["label"])}</td>' if i == 0 else "")
                    + (f'<td rowspan="{len(mk["outcomes"])}">{e(mk["settlement"])}</td>' if i == 0 else "")
                    + f'<td>{e(o["selection"])}</td>'
                    f'<td class="num">{o["probability"]*100:.2f}%</td>'
                    f'<td class="num">{o["fair_decimal"]:.3f}</td>'
                    f'<td class="num">{odds(o["american"])}</td>'
                    f'<td>{"yes" if o["fair_price_in_brief_band"] else "no"}</td>'
                    f'<td>{tier_badge(o.get("confidence"))}</td>'
                    f'<td><a href="{e(fx["source_urls"][0])}" rel="noopener">source</a></td>'
                    "</tr>")
    markets_body = f"""
<p class="lede">{c["markets"]} originated markets across {c["priced_fixtures"]} fixtures, covering
match winner, handicap / puck line / run line, total and team total. Every outcome shows the model
probability, the fair decimal price, the derived American price and whether that fair price sits
inside the brief's −250…+10000 window.</p>
<div class="note"><strong>These are not bookmaker offers.</strong> Fair decimal is 1/p with no margin,
no limit and no availability. A “no” in the window column does not mean the price is wrong; it means
the fair price of that probability falls outside the brief's band.</div>
<div class="wrap"><table><thead><tr><th>Fixture</th><th>Market</th><th>Settlement</th><th>Selection</th>
<th class="num">Model</th><th class="num">Fair dec.</th><th class="num">American</th><th>In window</th>
<th>Tier</th><th>Source</th></tr></thead><tbody>{''.join(mkt_rows)}</tbody></table></div>
"""
    (OUT / "markets.html").write_text(page("Markets", markets_body, "markets.html"))

    # ------------------------------------------------------------------ predictions
    blocks = []
    for p in desk["predictions"]:
        fx = fixtures[p["fixture_id"]]
        words = len(p["body"].split())
        facts = "".join(f"<li>{e(f)}</li>" for f in p["facts_used"])
        blocks.append(f"""
<div class="pred">
<h3>{e(fx["away"])} @ {e(fx["home"])} · {e(fx["competition"])}</h3>
<p class="sel">Selection: {e(p["selection_label"])} — {odds(p["american"])} fair, {p["probability"]*100:.2f}% modelled.{tier_badge("high")}</p>
<p class="body">{e(p["body"])}</p>
<p class="small muted">{words} words · start {e(dt(fx["start_utc"]))} · <a href="{e(fx["source_urls"][0])}" rel="noopener">official source for every fact below</a></p>
<ul>{facts}</ul>
</div>""")
    pred_body = f"""
<p class="lede">Seven High selections, one written prediction each. Every prediction states the
selection, both participants, the current season form and the recent ten-game record, and at least
one player fact for each side. Each fact is listed underneath with the official page it came from.
Predictions are checked for length and for repetition by the build validator.</p>
{''.join(blocks)}
<div class="note"><strong>Why so few.</strong> The other {c["priced_fixtures"] - c["high_fixtures"]}
priced fixtures have a strongest selection outside the brief's window or a missing official input,
so they carry a tier but no long-form prediction. Their prices, tiers and reasons are on
<a href="matches.html">Matches</a> and <a href="markets.html">Markets</a>; the ones that miss the
window by a single American point are named on <a href="flagged.html">Flagged for review</a>.</div>
"""
    (OUT / "predictions.html").write_text(page("High predictions", pred_body, "predictions.html"))

    # ------------------------------------------------------------------ flagged
    flag_blocks = []
    for f in desk["flagged"]:
        sev = f["severity"]
        flag_blocks.append(f"""
<div class="flag"><h4>{e(f["id"])} · {e(f["title"])} <span class="tag">severity: {e(sev)}</span></h4>
<p>{e(f["detail"])}</p>
<p class="small muted">Evidence: {e(f["source"])}</p></div>""")

    near_rows = []
    for n in desk["near_misses"]:
        near_rows.append(
            f'<tr><td>{e(n["fixture"])}</td><td>{e(n["market"])}</td><td>{e(n["selection"])}</td>'
            f'<td class="num">{n["probability"]*100:.2f}%</td><td class="num">{odds(n["american"])}</td>'
            f'<td class="num">{max(0, abs(n["american"]) - 250) if n["american"] < 0 else "—"}</td>'
            f'<td><a href="{e(n["source_url"])}" rel="noopener">source</a></td></tr>')

    notes = "".join(
        f'<div class="card"><h3>{e(n["label"])}</h3><p>{e(n["detail"])}</p></div>'
        for n in desk["near_miss_notes"])

    gap_rows = "".join(
        f'<tr><td>{e(g["fixture_id"])}</td><td>{e(g["missing"])}</td>'
        f'<td>{e(", ".join(g["missing_sides"]))}</td><td>{e(g["effect"])}</td></tr>'
        for g in desk["gaps"])

    flagged_body = f"""
<p class="lede">Everything this desk could not confirm, could not price, or deliberately did not
label High. Nothing here blocks publication; it is the review queue. Each item names the official
source that was read.</p>
<h2>Findings</h2>
{''.join(flag_blocks)}
<h2>Cross-desk review: every High label on the merged 53674ac8 desk</h2>
<p>Read row by row from that desk's own pages, not from any summary. Its 12 High rows are all at or
below the brief's 70% threshold; the highest is exactly 70%. This session did not edit those claims —
they belong to another session — but the finding is published here because it is the same defect the
brief warns about.</p>
<div class="wrap"><table><thead><tr><th>Page</th><th>Selection</th><th class="num">Stated probability</th>
<th class="num">Decimal</th><th class="num">American</th><th>Verdict</th></tr></thead><tbody>
{"".join(
  f'<tr><td><code>{e(r["page"])}</code></td><td>{e(r["selection"])}</td>'
  f'<td class="num">{r["probability_pct"]}%</td><td class="num">{e(r["decimal"])}</td>'
  f'<td class="num">{r["american"]}</td>'
  f'<td>{"below 70% — label overstates" if r["probability_pct"] <= 70 else "clears 70%"}</td></tr>'
  for r in desk["cross_desk"]["high_rows"])}
</tbody></table></div>
<p class="small muted">A repo-wide automated scan was attempted and is deliberately <strong>not</strong>
published: the pattern match was unreliable because single rows can mix several selections and
percentages, so publishing per-desk counts would risk naming a desk on a false positive. Only this desk
was read row by row.</p>

<h2>Named near misses: above 70%, priced shorter than −250</h2>
<p>Of the {c["outcomes"]} priced outcomes, <strong>{desk["over_70"]}</strong> carry a model probability
above 70%. Only <strong>{desk["over_70_in_window"]}</strong> of those also have a fair price inside
−250…+10000, and three of those ten depend on the assumed basketball spread, which leaves the
{c["high_selections"]} High selections on this desk. The table below is ordered by how close each
miss came: the first row is one American point away.</p>
<div class="wrap"><table><thead><tr><th>Fixture</th><th>Market</th><th>Selection</th>
<th class="num">Model</th><th class="num">Fair American</th><th class="num">Points past −250</th>
<th>Source</th></tr></thead><tbody>{''.join(near_rows)}</tbody></table></div>
<h2>The three largest misses, in context</h2>
{notes}
<h2>Blank fields and withheld markets</h2>
<div class="wrap"><table><thead><tr><th>Fixture</th><th>Missing input</th><th>Side</th>
<th>Effect on the desk</th></tr></thead><tbody>{gap_rows}</tbody></table></div>
<p class="small muted">Snooker rows carry no start time, no record and no price for the reasons given
on the <a href="sports/snooker.html">snooker page</a>. Every blank in these tables is a field the
official source did not publish in the retrieved response — not a zero, and not an estimate.</p>
"""
    (OUT / "flagged.html").write_text(page("Flagged for review", flagged_body, "flagged.html"))

    # ------------------------------------------------------------------ coverage
    cov_full = []
    for r in desk["coverage"]:
        status = r["status"]
        cls = "b-high" if status == "priced" else ("b-med" if "listed" in status else "b-none")
        src = (f'<a href="{e(r["source_url"])}" rel="noopener">{e(r["source_url"])}</a>'
               if r["source_url"] else '<span class="muted">no readable official page in this session</span>')
        cov_full.append(
            f'<tr><td><strong>{e(r["sport"])}</strong></td><td><span class="badge {cls}">{e(status)}</span></td>'
            f'<td class="num">{r["rows"]}</td><td>{e(r["detail"])}</td><td class="small">{src}</td></tr>')
    coverage_body = f"""
<p class="lede">Seventeen sports are in scope once soccer, American football, boxing, UFC/MMA,
hurling, horse racing, cycling and specials are removed. This table records exactly what was
achieved for each one, so a missing sport is visible as a gap instead of being silently absent.</p>
<div class="wrap"><table><thead><tr><th>Sport</th><th>Status</th><th class="num">Rows published</th>
<th>What was verified</th><th>Official page</th></tr></thead><tbody>{''.join(cov_full)}</tbody></table></div>
<h2>Why eleven sports have no rows</h2>
<div class="card"><p>Eleven of the seventeen sports produced no publishable row because an official
page did not yield a verifiable fixture list or a verifiable form input in this session:</p>
<ul>
<li><strong>Tennis</strong> — the ATP tour scores page returns live cards and completed results, not a future order of play, and the rankings table did not render.</li>
<li><strong>Darts</strong> — the PDC tournaments page returned a consent wall and no fixture text.</li>
<li><strong>Australian rules</strong> — the AFLW fixture and ladder widgets are JavaScript-only; the retrieved HTML contained no rows.</li>
<li><strong>Rugby union</strong> — the United Rugby Championship fixtures URL returned a 404.</li>
<li><strong>Cricket</strong> — the ICC matches URL returned a 404.</li>
<li><strong>Rugby league, handball, volleyball, golf, motor racing, eSports, greyhounds</strong> — no official fixture page was read, so no row and no price is claimed.</li>
</ul>
<p>Each of these is a coverage failure, not a finding about the sport. Filling them from memory or
from an aggregator would break the verification rule this desk is built on.</p></div>
"""
    (OUT / "coverage.html").write_text(page("Sport coverage", coverage_body, "coverage.html"))

    # ------------------------------------------------------------------ methodology
    a = desk["assumptions"]
    methodology_body = f"""
<p class="lede">The desk originates its own prices from statistics it read on official pages. This
page states the model, the parameters, the confidence rule and the limits, so a reader can decide
how much weight to give any row.</p>

<h2>1. The rule collision at the heart of the brief</h2>
<div class="card"><p>The brief asks for two things at once: a selection with a greater than 70% chance,
and a price between −250 and +10000.</p>
<p>American −250 converts to decimal 1.40 (<code>(100/250)+1</code>). A 70% chance converts to decimal
1.4286. A 71.43% chance is exactly decimal 1.40. A 75% chance is decimal 1.333, which is −300. In
other words, the higher the chance, the <em>shorter</em> the price, and every chance above 71.43%
prices beyond the −250 floor.</p>
<p>The two rules therefore overlap on one narrow interval: <strong>70.0000% &lt; p ≤ 71.4286%</strong>.
This desk publishes High only there. It does not describe a −311 or −544 selection as in-window,
and it does not shade a probability to fit. Those selections are listed with their true prices on
<a href="flagged.html">Flagged for review</a>.</p></div>

<h2>2. How the prices are made</h2>
<div class="card"><ul>
<li><strong>Win rate:</strong> {e(a["record_model"])}</li>
<li><strong>NHL settlement:</strong> {e(a["nhl_winner"])}</li>
<li><strong>Goals and runs:</strong> {e(a["nhl_goal_model"])} {e(a["mlb_run_model"])}</li>
<li><strong>Basketball handicaps:</strong> {e(a["basketball_handicap"])}</li>
<li><strong>Basketball totals:</strong> {e(a["basketball_totals"])}</li>
<li><strong>Lines:</strong> {e(a["handicaps"])}</li>
<li><strong>Price:</strong> fair decimal = 1/p, then the American form is derived with the standard
conversion. There is no margin, no limit and no availability claim.</li>
</ul></div>

<h2>3. The confidence rule, exactly as implemented</h2>
<div class="card"><p>{e(a["high_rule"])}</p>
<p><strong>High</strong> needs all of: p above 70.00%; p at or below 71.4286% so the fair price stays
inside −250; verified inputs on both sides; a verified settlement definition; no assumed-only
parameter carrying the number; and an attached written prediction of at least 30 words.</p>
<p><strong>Medium</strong> covers a strong view that is priced shorter than −250, or a selection whose
inputs are complete but which lacks a written prediction or depends on the assumed basketball spread.</p>
<p><strong>Low</strong> is everything else, including every baseball row, because starting pitchers and
bullpens are not captured.</p></div>

<h2>4. Selection of lines, disclosed</h2>
<div class="card"><p>For each fixture the desk generated a ladder of alternate lines in half-point
steps around the model expectation: totals, team totals, puck lines and run lines. A High selection
is a rung of that ladder whose model probability lands inside the 70.00–71.43% interval. That is a
deliberate choice of line, not a discovered edge, and it is why F-402-02 is published. The
match-winner view for the same fixture is shown separately on <a href="matches.html">Matches</a> and
keeps its own tier.</p></div>

<h2>5. Market families investigated</h2>
<div class="wrap"><table><thead><tr><th>Market family</th><th>Status here</th><th>Why</th></tr></thead><tbody>
<tr><td>Match winner</td><td>originated for all {c["priced_fixtures"]} priced fixtures</td><td>Record-based with Beta shrinkage and log5.</td></tr>
<tr><td>Handicap / puck line / run line</td><td>originated for {sum(1 for f in desk["fixtures"] if f.get("goal_inputs_complete"))} goal- or run-based fixtures and all 9 EuroLeague games</td><td>Poisson margin grid where goals or runs are verified; assumed 12.0-point normal spread for basketball, which caps those rows below High.</td></tr>
<tr><td>Total</td><td>originated for 12 NHL and 5 MLB fixtures</td><td>Withheld for EuroLeague: the official preview published scoring averages for only one side in most games, so a total could not be originated without inventing the other side.</td></tr>
<tr><td>Team total</td><td>originated for 12 NHL and 5 MLB fixtures</td><td>Same Poisson inputs as the total.</td></tr>
<tr><td>Period / half / quarter markets</td><td>withheld</td><td>No period-level official data was read, so a period split would be an assumption presented as a fact.</td></tr>
<tr><td>Correct score</td><td>withheld</td><td>The Poisson grid exists, but a correct-score market needs an exact-score tail the model is not validated for.</td></tr>
<tr><td>Player props</td><td>withheld</td><td>Confirmed availability, rotation and usage were not verified for any fixture.</td></tr>
<tr><td>Outrights / futures</td><td>out of scope</td><td>Multi-runner markets need a field and a ranking table; neither was read for golf, motor racing or greyhounds.</td></tr>
</tbody></table></div>

<h2>6. What is not modelled</h2>
<div class="card"><ul>
<li>Starting pitchers, bullpens, rest, travel, park factors and weather.</li>
<li>Injuries, suspensions, line combinations and confirmed starting goaltenders.</li>
<li>Home advantage: no home-field term is added, so a home row is not flattered.</li>
<li>Market prices: no sportsbook was queried. The moneylines printed by NHL.com are shown as a
reference on the fixtures and are labelled as that site's odds partner, not as our input.</li>
<li>Correlation between selections. Two High selections in the Utah–Seattle game are separate markets,
not independent bets, and no staking combination is suggested.</li>
</ul></div>

<h2>7. Verification method</h2>
<div class="card"><p>Each harvest file records the URL, the publisher, the exact fields read, the
observation window and — deliberately — what was <em>not</em> read. Facts were transcribed from the
official page in the same session, and anything the page did not publish was left null. The build
validator refuses to publish a row without an official link, a prediction under 30 words, a duplicate
prediction, a price that does not equal 1/p, or a High label outside the interval.</p></div>
"""
    (OUT / "methodology.html").write_text(page("Methodology", methodology_body, "methodology.html"))

    # ------------------------------------------------------------------ sources
    src_cards = []
    for s in desk["sources"]:
        sup = "".join(f'<li><a href="{e(u)}" rel="noopener">{e(u)}</a></li>' for u in s["supporting"])
        src_cards.append(f"""
<div class="card"><h3>{e(s["publisher"])} <span class="tag">official</span></h3>
<p><a href="{e(s["url"])}" rel="noopener">{e(s["url"])}</a></p>
<p class="small muted">Read {e(s["observed_from"])} → {e(s["observed_to"])}</p>
<p><strong>Read:</strong> {e(s["read"])}</p>
<p><strong>Not read:</strong> {e(s["not_read"])}</p>
{"<p class='small'>Supporting official endpoints:</p><ul class='small'>" + sup + "</ul>" if sup else ""}
</div>""")
    sources_body = f"""
<p class="lede">Five official publishers were read in this session. No media outlet, tipster site,
aggregator or sportsbook is used as a source anywhere in this desk.</p>
{''.join(src_cards)}
<h2>What “official” means here</h2>
<div class="card"><p>The publisher must be the league, tour, governing body or event organiser itself:
NHL.com, MLB.com, EuroLeague Basketball, the World Snooker Tour and the GAA. A page that merely
reports on those bodies does not qualify, however reliable it is, because the desk cannot verify that
the report matches the primary record.</p></div>
<h2>Pages that were attempted and did not yield a verifiable row</h2>
<div class="card"><ul>
<li>atptour.com/en/scores/current — live cards only, no future order of play.</li>
<li>pdc.tv/tournaments — consent wall, no fixture text.</li>
<li>afl.com.au/aflw/fixture and /ladder — JavaScript-only widgets, no rows in the response.</li>
<li>unitedrugby.com/fixtures — 404.</li>
<li>icc-cricket.com/matches — 404.</li>
<li>nba.com/games — the page returned an error state instead of the day's schedule.</li>
<li>gaa.ie/fixtures-results — one fixture only, and it is shinty-hurling, an excluded category.</li>
</ul></div>
"""
    (OUT / "sources.html").write_text(page("Sources", sources_body, "sources.html"))

    # ------------------------------------------------------------------ sport pages
    for slug, label in [("ice-hockey", "Ice hockey"), ("baseball", "Baseball"),
                        ("basketball", "Basketball"), ("snooker", "Snooker")]:
        rows = [f for f in desk["fixtures"] if f["sport_key"] == slug]
        if not rows:
            continue
        body_rows = []
        for fx in rows:
            pk = next((p for p in desk["picks"] if p["fixture_id"] == fx["id"]), None)
            h = pk["headline"] if pk else None
            sel = (f'{e(h["selection"])} <span class="small muted">{e(odds(h["american"]))}</span>'
                   if h else '<span class="muted">no line</span>')
            body_rows.append(
                "<tr>"
                f'<td>{e(dt(fx["start_utc"]))}</td>'
                f'<td>{e(fx["away"])} @ {e(fx["home"])}</td>'
                f'<td class="small">{e(fx.get("away_record") or "—")} / {e(fx.get("home_record") or "—")}</td>'
                f'<td>{sel}</td>'
                f'<td>{tier_badge(h["confidence"] if h else None)}</td>'
                f'<td class="num">{len(fx["markets"])}</td>'
                f'<td><a href="{e(fx["source_urls"][0])}" rel="noopener">source</a></td>'
                "</tr>")
        hi = [p for p in desk["predictions"] if fixtures[p["fixture_id"]]["sport_key"] == slug]
        pred_html = "".join(
            f'<div class="pred"><h3>{e(p["selection_label"])}</h3>'
            f'<p class="body">{e(p["body"])}</p>'
            f'<p class="small muted">{e(odds(p["american"]))} · {p["probability"]*100:.2f}% · '
            f'<a href="{e(fixtures[p["fixture_id"]]["source_urls"][0])}" rel="noopener">official source</a></p></div>'
            for p in hi)
        note = {
            "ice-hockey": "Twelve NHL games on 22 October, read on the league's own scores and standings pages.",
            "baseball": "The 2026 World Series, games 1-5, from the official MLB bracket and the final regular-season table. Every row is Low because pitching is not captured.",
            "basketball": "EuroLeague Round 7, 22-23 October. Handicaps depend on an assumed 12.0-point spread and are capped below High.",
            "snooker": "Round 3 pairings at the Northern Ireland Open. The official page prints no timezone, so no clock, record or price is published.",
        }[slug]
        market_block = ""
        if slug == "ice-hockey":
            mrows = []
            for fx in rows:
                ref = fx.get("displayed_market_reference") or {}
                if not ref:
                    continue
                def implied(a):
                    return (-a) / (-a + 100) if a < 0 else 100 / (a + 100)
                ih, ia = implied(ref["home_american"]), implied(ref["away_american"])
                pk = next(p for p in desk["picks"] if p["fixture_id"] == fx["id"])
                model_home = pk["winner_view"]["probability"] if pk["winner_view"]["selection"] == fx["home"] else 1 - pk["winner_view"]["probability"]
                mrows.append(
                    f'<tr><td>{e(fx["away"])} @ {e(fx["home"])}</td>'
                    f'<td class="num">{ia*100:.1f}% / {ih*100:.1f}%</td>'
                    f'<td class="num">{(ia+ih-1)*100:.1f}%</td>'
                    f'<td class="num">{model_home*100:.1f}%</td>'
                    f'<td class="num">{(model_home-ih)*100:+.1f} pts</td>'
                    f'<td><a href="https://www.nhl.com/scores/2026-10-22" rel="noopener">NHL.com</a></td></tr>')
            market_block = f"""
<h2>Model versus the price NHL.com displays</h2>
<p>NHL.com prints its odds partner's moneyline on the scores page. Those prices contain a margin, so
the two implied probabilities add to more than 100%; the overround column is that gap. The last
numeric column is our home probability minus the market's home implied probability, in points.</p>
<div class="wrap"><table><thead><tr><th>Fixture</th><th class="num">Market away / home</th>
<th class="num">Overround</th><th class="num">Model home</th><th class="num">Edge vs market</th>
<th>Source</th></tr></thead><tbody>{''.join(mrows)}</tbody></table></div>
<p class="small muted">This is a comparison, not an edge claim: our model ignores goaltenders, injuries
and rest, and the market does not. A positive gap is where the two disagree, nothing more.</p>
"""
        sp_body = f"""
<p class="lede">{e(note)}</p>
{market_block}
<div class="wrap"><table><thead><tr><th>Start (UTC)</th><th>Fixture</th><th>Records</th>
<th>Headline selection</th><th>Tier</th><th class="num">Markets</th><th>Source</th></tr></thead>
<tbody>{''.join(body_rows)}</tbody></table></div>
<h2>Written predictions in this category</h2>
{pred_html or '<p class="muted">No High selection in this category, so no long-form prediction is published for it.</p>'}
<p class="small"><a href="../coverage.html">Back to coverage</a> · <a href="../markets.html">All markets</a></p>
"""
        (OUT / "sports" / f"{slug}.html").write_text(
            page(label, sp_body, f"sports/{slug}.html", prefix="../"))

    print("built pages:", sorted(p.name for p in OUT.glob("*.html")),
          sorted(p.name for p in (OUT / "sports").glob("*.html")))


if __name__ == "__main__":
    main()
