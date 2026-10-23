#!/usr/bin/env python3
"""T6B47 site build: static dashboard for the consolidated desk.

Output: 6b47ea39/**  (index, picks, watchlist, predictions, matches, markets,
flagged, sources, methodology, repo-audit, reverse-engineering, 15 sport pages)

Only committed data is rendered. Nothing is fetched.
"""
from __future__ import annotations

import html
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "6b47ea39"
SITE = ROOT / "6b47ea39"
BUILT = "2026-10-23T21:30:00Z"
DASH = '<span class="muted">—</span>'
IN_BADGE = '<span class="badge b-green">in</span>'
OUT_BADGE = '<span class="badge b-gray">out</span>'

SPORT_ORDER = [
    "Golf", "Volleyball", "Rugby Union", "Cricket", "Snooker", "Darts", "Baseball",
    "Gaelic Sports", "Greyhounds", "Tennis", "Motor Racing", "Handball",
    "Ice Hockey", "Basketball", "Rugby League",
]
SLUG = {
    "Golf": "golf", "Volleyball": "volleyball", "Rugby Union": "rugby-union", "Cricket": "cricket",
    "Snooker": "snooker", "Darts": "darts", "Baseball": "baseball", "Gaelic Sports": "gaelic-sports",
    "Greyhounds": "greyhounds", "Tennis": "tennis", "Motor Racing": "motor-racing",
    "Handball": "handball", "Ice Hockey": "ice-hockey", "Basketball": "basketball",
    "Rugby League": "rugby-league",
}

CSS = """
:root{--bg:#0b1220;--panel:#111a2b;--panel2:#16223a;--line:#23324e;--ink:#e8eefc;--muted:#9aabc9;
--accent:#4da3ff;--green:#3ddc97;--amber:#ffb648;--red:#ff6b6b;--gray:#7d8aa3;--radius:14px}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
.layout{display:flex;min-height:100vh}
aside{width:248px;flex:0 0 248px;background:#0a1120;border-right:1px solid var(--line);padding:20px 14px;position:sticky;top:0;height:100vh;overflow:auto}
.brand{display:flex;gap:10px;align-items:center;color:var(--ink);font-weight:700;margin-bottom:18px}
.brand small{display:block;color:var(--muted);font-weight:500;font-size:11px;letter-spacing:.08em}
.navlabel{color:var(--muted);font-size:11px;letter-spacing:.1em;margin:16px 6px 6px}
aside a.nav{display:block;padding:7px 9px;border-radius:8px;color:#cbd8ee;font-size:14px}
aside a.nav:hover{background:#14203a;text-decoration:none}
aside a.nav.active{background:#18284a;color:#fff}
main{flex:1;min-width:0;padding:26px 30px 60px;max-width:1500px}
h1{font-size:26px;margin:0 0 6px}h2{font-size:19px;margin:26px 0 10px}h3{font-size:15px;margin:18px 0 8px}
.eyebrow{color:var(--accent);font-size:11px;letter-spacing:.12em;text-transform:uppercase;margin:0 0 6px}
.lede{color:var(--muted);max-width:900px;margin:0 0 18px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:16px 0 22px}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:14px}
.kpi b{display:block;font-size:24px;letter-spacing:-.02em}
.kpi span{color:var(--muted);font-size:12px}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:16px 18px;margin:14px 0}
.panel h2{margin-top:0}
table{width:100%;border-collapse:collapse;font-size:13.5px}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--muted);font-weight:600;font-size:12px;letter-spacing:.03em;text-transform:uppercase}
tbody tr:hover{background:#141f36}
.wrap{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:var(--panel)}
.badge{display:inline-block;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:600;letter-spacing:.02em}
.b-green{background:rgba(61,220,151,.14);color:var(--green);border:1px solid rgba(61,220,151,.35)}
.b-amber{background:rgba(255,182,72,.14);color:var(--amber);border:1px solid rgba(255,182,72,.35)}
.b-red{background:rgba(255,107,107,.14);color:var(--red);border:1px solid rgba(255,107,107,.35)}
.b-gray{background:rgba(125,138,163,.14);color:var(--gray);border:1px solid rgba(125,138,163,.35)}
.b-blue{background:rgba(77,163,255,.14);color:var(--accent);border:1px solid rgba(77,163,255,.35)}
.mono{font-variant-numeric:tabular-nums}
.muted{color:var(--muted)}
.small{font-size:12.5px}
.notice{border-left:3px solid var(--amber);background:rgba(255,182,72,.07);padding:12px 14px;border-radius:8px;margin:16px 0}
.notice.blue{border-color:var(--accent);background:rgba(77,163,255,.07)}
.notice.red{border-color:var(--red);background:rgba(255,107,107,.07)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}
.card{background:var(--panel2);border:1px solid var(--line);border-radius:12px;padding:14px}
.card h4{margin:0 0 6px;font-size:14px}
.src{font-size:12px}
.pred{background:var(--panel2);border:1px solid var(--line);border-radius:12px;padding:16px;margin:12px 0}
.pred h3{margin:0 0 4px;font-size:16px}
.pred p.body{margin:10px 0;font-size:14.5px}
.tagrow{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0}
input[type=search],select{background:#0d1626;border:1px solid var(--line);color:var(--ink);border-radius:8px;padding:8px 10px;font-size:13px}
footer{color:var(--muted);font-size:12px;border-top:1px solid var(--line);margin-top:34px;padding-top:14px}
@media(max-width:820px){.layout{display:block}aside{position:static;width:auto;height:auto}main{padding:18px}}
"""


def esc(value) -> str:
    return html.escape(str(value if value is not None else ""))


def money(value) -> str:
    if value is None:
        return '<span class="muted">—</span>'
    return f"{value:+.0f}" if value > 0 else f"{value:.0f}"


def pct(value) -> str:
    return f"{value*100:.1f}%"


def tier_badge(tier: str) -> str:
    if tier == "high-in-window":
        return '<span class="badge b-green">High · in window</span>'
    if tier == "out-of-window":
        return '<span class="badge b-amber">High · out of window</span>'
    return '<span class="badge b-gray">Medium</span>'


def state_badge(state: str) -> str:
    return {
        "upcoming": '<span class="badge b-blue">Upcoming</span>',
        "elapsed": '<span class="badge b-gray">Elapsed at build</span>',
        "time not stated": '<span class="badge b-amber">Time not stated</span>',
    }.get(state, esc(state))


def sources_cell(urls, limit=2) -> str:
    if not urls:
        return '<span class="badge b-red">No official link recorded</span>'
    out = []
    for url in urls[:limit]:
        host = re.sub(r"^https?://", "", url).split("/")[0]
        out.append(f'<a class="src" href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(host)} ↗</a>')
    if len(urls) > limit:
        out.append(f'<span class="muted small">+{len(urls)-limit}</span>')
    return "<br>".join(out)


NAV = [
    ("index.html", "Overview"),
    ("picks.html", "High-confidence picks"),
    ("predictions.html", "Predictions"),
    ("watchlist.html", "Medium watchlist"),
    ("matches.html", "All matches"),
    ("markets.html", "Market explorer"),
    ("flagged.html", "Flagged for review"),
    ("repo-audit.html", "Repository audit"),
    ("reverse-engineering.html", "OLBG discovery"),
    ("sources.html", "Sources"),
    ("methodology.html", "Method & limits"),
]


def page(title: str, current: str, body: str, subtitle: str = "") -> str:
    prefix = "../" if current.startswith("sports/") else ""
    nav = "\n".join(
        f'<a class="nav{" active" if href == current else ""}" href="{prefix}{href}">{esc(label)}</a>'
        for href, label in NAV
    )
    sports = "\n".join(
        f'<a class="nav{" active" if current == f"sports/{SLUG[s]}.html" else ""}" href="{prefix}sports/{SLUG[s]}.html">{esc(s)}</a>'
        for s in SPORT_ORDER
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · OLBG consolidated desk</title>
<meta name="description" content="Independent, source-linked research desk for the 15 sports in the brief. Not affiliated with OLBG.">
<link rel="stylesheet" href="{'../' if current.startswith('sports/') else ''}assets/style.css">
</head><body><div class="layout">
<aside>
<div class="brand"><span>OLBG<span style="font-weight:400">.</span></span><span><small>CONSOLIDATED DESK</small></span></div>
<div class="navlabel">WORKSPACE</div>{nav}
<div class="navlabel">SPORTS · 15</div>{sports}
<div class="navlabel">BUILD</div>
<div class="small muted" style="padding:4px 9px">Build {esc(BUILT)}<br>Evidence captured 23 Oct 2026, 16:45Z–20:40Z<br>Inherited, not re-read this session.</div>
</aside>
<main>
<header><p class="eyebrow">{esc(subtitle or 'Consolidated 15-sport desk')}</p><h1>{esc(title)}</h1></header>
{body}
<footer>Independent research project · not affiliated with OLBG · prices are our own estimates, not bookmaker offers · no betting advice ·
<a href="{prefix}flagged.html">every irregularity is on the review page</a></footer>
</main></div></body></html>"""


def main() -> None:
    slate = json.loads((DATA / "slate.json").read_text(encoding="utf-8"))
    picks_doc = json.loads((DATA / "picks.json").read_text(encoding="utf-8"))
    preds_doc = json.loads((DATA / "predictions.json").read_text(encoding="utf-8"))
    flags_doc = json.loads((DATA / "flags.json").read_text(encoding="utf-8"))
    audit = json.loads((DATA / "audit.json").read_text(encoding="utf-8"))

    events = slate["events"]
    picks = picks_doc["picks"]
    watch = picks_doc["watchlist"]
    preds = {p["pick_id"]: p for p in preds_doc["predictions"]}
    flags = flags_doc["flags"]
    by_sport = defaultdict(list)
    for event in events:
        by_sport[event["sport"]].append(event)

    total_lines = sum(len(e["markets"]) for e in events)
    in_window = [p for p in picks if p["tier"] == "high-in-window"]
    out_window = [p for p in picks if p["tier"] == "out-of-window"]
    today = [e for e in events if e["state"] == "upcoming" and e["start_utc"][:10] == "2026-10-23"]
    tomorrow = [e for e in events if e["state"] == "upcoming" and e["start_utc"][:10] == "2026-10-24"]
    upcoming = [e for e in events if e["state"] == "upcoming"]

    def pick_for(event_id: str):
        return next((p for p in picks if p["event_id"] == event_id), None)

    SITE.mkdir(exist_ok=True)
    (SITE / "assets").mkdir(exist_ok=True)
    (SITE / "sports").mkdir(exist_ok=True)
    (SITE / "assets" / "style.css").write_text(CSS, encoding="utf-8")

    # ------------------------------------------------------------------ overview
    FIELDISH = re.compile(r"\bfield\b|remaining|quarter|contingent|traps? [1-6]|bottom-half|points contenders|qualifying winner|\bsession\b", re.I)

    def exec_rows(rows, limit=12):
        out = []
        rows = sorted(
            [e for e in rows if not FIELDISH.search(e["home"] + " " + e["away"])],
            key=lambda e: e["start_utc"],
        )
        for event in rows:
            pick = pick_for(event["id"])
            if pick:
                pick_cell = esc(pick["selection"]) + (
                    '<br><span class="mono small muted">%s · %s</span>' % (money(pick["american"]), pct(pick["probability"]))
                )
                tier_cell = tier_badge(pick["tier"])
            else:
                pick_cell = '<span class="muted">—</span>'
                tier_cell = '<span class="badge b-gray">No pick</span>'
            out.append(
                "<tr>"
                f'<td class="mono small">{esc(event["start_utc"][5:16].replace("T", " "))}Z</td>'
                f'<td><strong>{esc(event["home"])}</strong> v <strong>{esc(event["away"])}</strong>'
                f'<br><span class="muted small">{esc(event["competition"])}</span></td>'
                f'<td>{esc(event["sport"])}</td>'
                f"<td>{tier_cell}</td>"
                f"<td>{pick_cell}</td>"
                f"<td>{sources_cell(event['official_sources'])}</td>"
                "</tr>"
            )
        return "".join(out[:limit])

    kpis = [
        (len(events), "fixtures in scope"),
        (f"{len(upcoming)}", "still upcoming"),
        (f"{total_lines:,}", "priced market lines"),
        (f"{len(picks)}", f"high picks · {len(in_window)} in window"),
        (f"{len(preds)}", "written predictions"),
        (f"{len(flags)}", "flagged findings"),
    ]
    body = f"""
<p class="lede">One reconciled desk for the 15 sports in the brief. It reads the three retained 23 October desks, re-does their arithmetic,
re-applies the High-confidence rule on their own numbers, and publishes only what survives. Every row links to the governing body, league,
tour or club page that recorded it; nothing was re-fetched in this session, and the whole slate is labelled as inherited.</p>
<div class="kpis">{''.join(f'<div class="kpi"><b>{v}</b><span>{esc(l)}</span></div>' for v, l in kpis)}</div>
<div class="notice red"><strong>Read this before the picks.</strong> The brief asks for selections with a better than 70% win chance priced
between −250 and +10000. A −250 price is decimal 1.40, which is 71.43% implied. The two conditions together therefore describe a band
1.43 probability points wide: {len(in_window)} of this desk's picks fit it, and every stronger favourite falls outside it. Both groups are
published and labelled; neither is relabelled to look like the other. <a href="methodology.html">Method and limits</a>.</div>
<h2>Highest-confidence picks for today — 23 October 2026, remaining kick-offs (UTC)</h2>
<div class="wrap"><table><thead><tr><th>Start</th><th>Match</th><th>Sport</th><th>Tier</th><th>Selection · price</th><th>Official source</th></tr></thead>
<tbody>{exec_rows(today, 8) or '<tr><td colspan="6" class="muted">No in-scope fixture remains today at the 21:30Z build time.</td></tr>'}</tbody></table></div>
<h2>Tomorrow — 24 October 2026</h2>
<div class="wrap"><table><thead><tr><th>Start</th><th>Match</th><th>Sport</th><th>Tier</th><th>Selection · price</th><th>Official source</th></tr></thead>
<tbody>{exec_rows(tomorrow, 12)}</tbody></table></div>
<h2>Where this desk disagrees with the desks it reads</h2>
<div class="grid">
<div class="card"><h4>{len(audit['directional_conflicts'])} fixtures priced with opposite favourites</h4>
<p class="small muted">Two source desks call different winners on the same match. None is used for a pick here.</p>
<a class="small" href="flagged.html">See the register →</a></div>
<div class="card"><h4>51 claimed High picks, 3 that qualify</h4>
<p class="small muted">Desk 496eaf02's headline count is not reproduced by its own price file.</p>
<a class="small" href="flagged.html">See finding F03 →</a></div>
<div class="card"><h4>5 per sport is not reachable</h4>
<p class="small muted">Rules R1–R7 leave {len(picks)} high picks. The per-sport gaps are listed, not filled.</p>
<a class="small" href="picks.html">See coverage →</a></div>
</div>
<h2>How the desk is built</h2>
<div class="grid">
<div class="card"><h4>1 · Reconcile</h4><p class="small muted">Same fixture spelled differently across desks is collapsed, with every alias recorded. 125 fixtures remain from 218 raw rows.</p></div>
<div class="card"><h4>2 · Recompute</h4><p class="small muted">Every price is re-derived from its decimal value. Band membership is recomputed rather than trusted.</p></div>
<div class="card"><h4>3 · Gate</h4><p class="small muted">Seven documented rules decide what is publishable. Each rejection is counted and shown.</p></div>
<div class="card"><h4>4 · Write</h4><p class="small muted">{len(preds)} predictions, all at least 30 words, no shared six-word phrase, no internal vocabulary.</p></div>
</div>
"""
    (SITE / "index.html").write_text(page("Overview", "index.html", body, "Consolidated 15-sport desk · build 23 Oct 2026 21:30Z"), encoding="utf-8")

    # ------------------------------------------------------------------ picks
    def picks_table(rows):
        out = []
        for row in rows:
            pred = preds.get(row["pick_id"])
            link = '<a class="small" href="predictions.html#%s">read</a>' % esc(row["pick_id"]) if pred else '<span class="muted small">—</span>'
            out.append(
                "<tr>"
                f'<td class="mono small">{esc(row["start_utc"][5:16].replace("T"," "))}Z</td>'
                f'<td><strong>{esc(row["match"])}</strong><br><span class="muted small">{esc(row["competition"])}</span></td>'
                f'<td>{esc(row["sport"])}</td>'
                f'<td>{esc(row.get("display_selection") or row["selection"])}<br><span class="muted small">{esc(row["market"])}</span></td>'
                f'<td class="mono">{money(row["american"])}<br><span class="muted small">{pct(row["probability"])}</span></td>'
                f"<td>{tier_badge(row['tier'])}</td>"
                f'<td class="small">{esc(", ".join(row["desks"]))}</td>'
                f"<td>{sources_cell(row['official_sources'])}</td>"
                f"<td>{link}</td>"
                "</tr>"
            )
        return "".join(out)

    shortfall_rows = "".join(
        f"<tr><td>{esc(s['sport'])}</td><td class='mono'>{s['available']}</td><td class='mono'>5</td><td class='small muted'>{esc(s['reason'])}</td></tr>"
        for s in picks_doc["shortfalls"]
    )
    dropped = picks_doc["dropped_first_reason"]
    body = f"""
<p class="lede">Every candidate line in the slate was run through seven rules. What survives is below, split by whether it fits the brief's
price window. The counts of what each rule removed are published so the thinning is visible.</p>
<div class="kpis">
<div class="kpi"><b>{len(picks)}</b><span>high picks published</span></div>
<div class="kpi"><b>{len(in_window)}</b><span>inside −250…+10000</span></div>
<div class="kpi"><b>{len(out_window)}</b><span>stronger than −250</span></div>
<div class="kpi"><b>{len(watch)}</b><span>medium watchlist</span></div>
<div class="kpi"><b>{sum(dropped.values()):,}</b><span>candidate lines rejected</span></div>
</div>
<div class="notice blue"><strong>What "out of window" means.</strong> These selections are estimated above 70% but priced shorter than −250,
so they are outside the range the brief asks for. They are shown because they are the strongest available calls in their sports; they are
never counted as in-window picks.</div>
<h2>Inside the window — {len(in_window)} picks</h2>
<div class="wrap"><table><thead><tr><th>Start (UTC)</th><th>Match</th><th>Sport</th><th>Selection</th><th>Our price</th><th>Tier</th><th>Source desk</th><th>Official source</th><th>Write-up</th></tr></thead>
<tbody>{picks_table(in_window)}</tbody></table></div>
<h2>Stronger than the window allows — {len(out_window)} picks</h2>
<div class="wrap"><table><thead><tr><th>Start (UTC)</th><th>Match</th><th>Sport</th><th>Selection</th><th>Our price</th><th>Tier</th><th>Source desk</th><th>Official source</th><th>Write-up</th></tr></thead>
<tbody>{picks_table(out_window)}</tbody></table></div>
<h2>The five-per-sport target, audited</h2>
<div class="wrap"><table><thead><tr><th>Sport</th><th>High picks found</th><th>Target</th><th>Why the gap exists</th></tr></thead><tbody>{shortfall_rows}</tbody></table></div>
<h2>What the rules removed</h2>
<div class="wrap"><table><thead><tr><th>First rule that rejected the line</th><th>Lines</th></tr></thead><tbody>
{''.join(f'<tr><td>{esc(k)}</td><td class="mono">{v}</td></tr>' for k, v in sorted(dropped.items(), key=lambda kv: -kv[1]))}
</tbody></table></div>
"""
    (SITE / "picks.html").write_text(page("High-confidence picks", "picks.html", body, "Strict re-gate of the brief's rule"), encoding="utf-8")

    # ------------------------------------------------------------------ predictions
    pred_html = []
    for row in sorted(preds.values(), key=lambda r: (SPORT_ORDER.index(r["sport"]), r["start_utc"])):
        fact_links = "".join(
            f'<a class="src" href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(re.sub(r"^https?://", "", url).split("/")[0])} ↗</a> '
            for url in row["official_sources"][:3]
        )
        pred_html.append(f"""
<div class="pred" id="{esc(row['pick_id'])}">
<div class="tagrow">{tier_badge(row['tier'])}<span class="badge b-blue">{esc(row['sport'])}</span>
<span class="badge b-gray">{esc(row['start_utc'][5:16].replace('T',' '))}Z</span>
<span class="badge b-gray">{row['words']} words</span></div>
<h3>{esc(row['match'])}</h3>
<p class="small muted">{esc(row['competition'])} · selection <strong>{esc(row.get('display_selection') or row['selection'])}</strong> at {money(row['american'])} ({pct(row['probability'])})</p>
<p class="body">{esc(row['text'])}</p>
<p class="small">{fact_links}</p>
<p class="small muted">Facts read from the official page at {esc(row['fact_read_utc'] or 'capture time')} by source desk {esc(row['source_desk'])}; inherited here, not re-fetched.</p>
</div>""")
    body = f"""
<p class="lede">{len(preds)} write-ups, one per published high-confidence pick. Each is at least 30 words, names the selection in plain words,
uses only facts recorded in the desk's fact register, and shares no six-word phrase with any other write-up.</p>
<div class="notice blue"><strong>Provenance.</strong> Every match fact below was read from the linked official page by the source desk named on
the card at the timestamp shown. This session could not reach those hosts, so the facts are inherited and labelled as such rather than
presented as freshly observed.</div>
{''.join(pred_html)}
"""
    (SITE / "predictions.html").write_text(page("Predictions", "predictions.html", body, "Unique, source-grounded write-ups"), encoding="utf-8")

    # ------------------------------------------------------------------ watchlist
    rows = "".join(
        "<tr>"
        f'<td class="mono small">{esc(w["start_utc"][5:16].replace("T"," "))}Z</td>'
        f'<td><strong>{esc(w["match"])}</strong><br><span class="muted small">{esc(w["competition"])}</span></td>'
        f'<td>{esc(w["sport"])}</td><td>{esc(w["selection"])}</td>'
        f'<td class="mono">{money(w["american"])}</td><td class="mono">{pct(w["probability"])}</td>'
        f"<td>{tier_badge('medium-watch')}</td><td>{sources_cell(w['official_sources'])}</td></tr>"
        for w in sorted(watch, key=lambda r: (SPORT_ORDER.index(r["sport"]), -r["probability"]))
    )
    body = f"""
<p class="lede">These lines sit between 60% and 70% estimated probability. They are not high-confidence picks and carry no write-up; they are
listed so the sport tables are not empty and so the reader can see the next-best call in each market.</p>
<div class="wrap"><table><thead><tr><th>Start</th><th>Match</th><th>Sport</th><th>Selection</th><th>Our price</th><th>Probability</th><th>Tier</th><th>Official source</th></tr></thead>
<tbody>{rows or '<tr><td colspan="8" class="muted">No qualifying medium line.</td></tr>'}</tbody></table></div>
"""
    (SITE / "watchlist.html").write_text(page("Medium watchlist", "watchlist.html", body, "60–70% — not high confidence"), encoding="utf-8")

    # ------------------------------------------------------------------ matches
    rows = []
    for event in sorted(events, key=lambda e: (e["start_utc"] or "9999", e["sport"])):
        fav = event.get("favourite")
        desks = ", ".join(sorted({p["desk"] for p in event["provenance"]}))
        fav_cell = esc(fav["selection"]) if fav else "<span class='muted'>not priced</span>"
        rows.append(
            "<tr>"
            f'<td class="mono small">{esc((event["start_utc"] or "not stated")[5:16].replace("T"," "))}</td>'
            f'<td><strong>{esc(event["home"])}</strong> v <strong>{esc(event["away"])}</strong>'
            + (f'<br><span class="muted small">also listed as: {esc("; ".join(event["aliases"][1:]))}</span>' if len(event.get("aliases", [])) > 1 else "")
            + f'<br><span class="muted small">{esc(event["competition"])}</span></td>'
            f'<td>{esc(event["sport"])}</td>'
            f'<td>{state_badge(event["state"])}</td>'
            f'<td class="mono">{len(event["markets"])}</td>'
            f"<td class='small'>{fav_cell}</td>"
            f'<td class="small muted">{esc(desks)}</td>'
            f"<td>{sources_cell(event['official_sources'])}</td>"
            "</tr>"
        )
    body = f"""
<p class="lede">All {len(events)} fixtures in the reconciled slate, newest first by start time. A fixture listed with several desk names was
priced by more than one source desk; one with a single name rests on one publication only. Where a desk spelled a club differently, every
alias is shown.</p>
<div class="notice"><strong>Blank means unverified.</strong> A row with no official link is marked as such and carries no pick. No value on
this page was inferred to fill a gap.</div>
<div class="wrap"><table><thead><tr><th>Start (UTC)</th><th>Fixture</th><th>Sport</th><th>State</th><th>Lines</th><th>Top-line favourite</th><th>Source desks</th><th>Official source</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>
"""
    (SITE / "matches.html").write_text(page("All matches", "matches.html", body, f"{len(events)} reconciled fixtures"), encoding="utf-8")

    # ------------------------------------------------------------------ markets
    market_rows = []
    for event in events:
        for line in event["markets"]:
            market_rows.append(
                {
                    "sport": event["sport"],
                    "match": f"{event['home']} v {event['away']}",
                    "start": event["start_utc"] or "",
                    "market": line["market"],
                    "selection": line["selection"],
                    "prob": round(line["probability"], 4),
                    "american": line["american"],
                    "band": line["band"],
                    "desk": line["source_desk"],
                    "divergence": line["divergence"],
                    "state": event["state"],
                }
            )
    table = "".join(
        f"<tr><td>{esc(r['sport'])}</td><td class='small'>{esc(r['match'])}</td><td class='small'>{esc(r['market'])}</td>"
        f"<td class='small'>{esc(r['selection'])}</td><td class='mono'>{money(r['american'])}</td>"
        f"<td class='mono'>{pct(r['prob'])}</td>"
        f"<td>{IN_BADGE if r['band'] == 'in' else OUT_BADGE}</td>"
        f"<td class='small muted'>{esc(r['desk'])}</td></tr>"
        for r in market_rows
    )
    body = f"""
<p class="lede">Every priced line in the slate — {len(market_rows):,} rows across {len(SPORT_ORDER)} sports. Filter by sport or search a team,
market or selection. Prices are this project's own estimates, re-derived from the decimal price, not bookmaker quotes.</p>
<div class="panel" style="display:flex;gap:10px;flex-wrap:wrap">
<select id="sport"><option value="">All sports</option>{''.join(f'<option>{esc(s)}</option>' for s in SPORT_ORDER)}</select>
<input type="search" id="q" placeholder="Search team, player, market or selection" style="min-width:280px;flex:1">
<span class="small muted" id="count" style="align-self:center"></span>
</div>
<div class="wrap" style="max-height:70vh;overflow:auto"><table id="mt"><thead><tr><th>Sport</th><th>Match</th><th>Market</th><th>Selection</th><th>Price</th><th>Probability</th><th>Window</th><th>Source desk</th></tr></thead>
<tbody>{table}</tbody></table></div>
<script>
const sport=document.getElementById('sport'),q=document.getElementById('q'),rows=[...document.querySelectorAll('#mt tbody tr')],c=document.getElementById('count');
function f(){{const s=sport.value.toLowerCase(),t=q.value.toLowerCase();let n=0;rows.forEach(r=>{{const ok=(!s||r.children[0].textContent.toLowerCase()===s)&&(!t||r.textContent.toLowerCase().includes(t));r.style.display=ok?'':'none';if(ok)n++;}});c.textContent=n.toLocaleString()+' rows';}}
sport.addEventListener('change',f);q.addEventListener('input',f);f();
</script>
"""
    (SITE / "markets.html").write_text(page("Market explorer", "markets.html", body, f"{len(market_rows):,} priced lines"), encoding="utf-8")

    # ------------------------------------------------------------------ flagged
    blocks = []
    for flag in flags:
        sev = {"high": "b-red", "medium": "b-amber", "low": "b-gray", "info": "b-blue"}.get(flag["severity"], "b-gray")
        rows_html = "".join(f"<li>{esc(r)}</li>" for r in flag["rows"])
        ref = (
            "<a href='%s' target='_blank' rel='noopener noreferrer'>%s ↗</a>" % (esc(flag["source"]), esc(flag["source"]))
            if str(flag["source"]).startswith("http")
            else "Check: <code>%s</code>" % esc(flag["source"])
        )
        blocks.append(f"""
<div class="pred">
<div class="tagrow"><span class="badge {sev}">{esc(flag['severity'].upper())}</span><span class="badge b-gray">{esc(flag['id'])}</span></div>
<h3>{esc(flag['title'])}</h3>
<p class="body">{esc(flag['detail'])}</p>
{f'<ul class="small muted">{rows_html}</ul>' if rows_html else ''}
<p class="small">{ref}</p>
</div>""")
    conflict_rows = ""
    for conflict in audit["directional_conflicts"]:
        claim = " · ".join(
            f"{desk}: {value['selection']} {value['probability']*100:.1f}%" for desk, value in conflict["favourites"].items()
        )
        conflict_rows += (
            f"<tr><td>{esc(conflict['sport'])}</td><td>{esc(conflict['match'])}</td>"
            f"<td class='mono small'>{esc(conflict['start_utc'])}</td><td class='small'>{esc(claim)}</td></tr>"
        )
    body = f"""
<p class="lede">Everything this desk found that does not add up, cannot be confirmed, or contradicts another publication. Nothing here is
suppressed: the site publishes the finding alongside the data it affects, with the source that supports it. Flagged items do not block
publication, they wait for a human decision.</p>
<div class="kpis">
<div class="kpi"><b>{sum(1 for f in flags if f['severity']=='high')}</b><span>high severity</span></div>
<div class="kpi"><b>{sum(1 for f in flags if f['severity']=='medium')}</b><span>medium</span></div>
<div class="kpi"><b>{sum(1 for f in flags if f['severity']=='info')}</b><span>informational</span></div>
<div class="kpi"><b>{len(audit['directional_conflicts'])}</b><span>opposite-favourite fixtures</span></div>
</div>
{''.join(blocks)}
<h2>Fixtures with opposite favourites, side by side</h2>
<div class="wrap"><table><thead><tr><th>Sport</th><th>Fixture</th><th>Start (UTC)</th><th>What each desk says</th></tr></thead><tbody>
{conflict_rows}
</tbody></table></div>
"""
    (SITE / "flagged.html").write_text(page("Flagged for review", "flagged.html", body, f"{len(flags)} findings + {len(audit['directional_conflicts'])} conflicts"), encoding="utf-8")

    # ------------------------------------------------------------------ sources
    hosts = Counter()
    for event in events:
        for url in event["official_sources"]:
            hosts[re.sub(r"^https?://", "", url).split("/")[0]] += 1
    no_source = [e for e in events if not e["official_sources"]]
    host_rows = "".join(
        f"<tr><td>{esc(h)}</td><td class='mono'>{n}</td><td class='small muted'>{esc(', '.join(sorted({e['sport'] for e in events if any(h in u for u in e['official_sources'])})))}</td></tr>"
        for h, n in hosts.most_common()
    )
    body = f"""
<p class="lede">{len(hosts)} distinct hosts supply the fixture links on this desk. Every host below is a league, tour, governing body, club or
official statistics service, with the exceptions listed on the <a href="flagged.html">review page</a>.</p>
<div class="notice"><strong>What a source link proves here.</strong> It proves which organisation published the fixture the row describes.
It does not prove the price — every price on this site is this project's own estimate — and it does not prove the result.</div>
<h2>Hosts used</h2>
<div class="wrap"><table><thead><tr><th>Host</th><th>Rows</th><th>Sports</th></tr></thead><tbody>{host_rows}</tbody></table></div>
<h2>Rows with no official link</h2>
<div class="wrap"><table><thead><tr><th>Fixture</th><th>Sport</th><th>Source desk</th><th>Status</th></tr></thead><tbody>
{''.join(f"<tr><td>{esc(e['home'])} v {esc(e['away'])}</td><td>{esc(e['sport'])}</td><td class='small'>{esc(', '.join(p['desk'] for p in e['provenance']))}</td><td><span class='badge b-red'>unverified — no pick</span></td></tr>" for e in no_source) or '<tr><td colspan="4" class="muted">Every fixture carries at least one official link.</td></tr>'}
</tbody></table></div>
"""
    (SITE / "sources.html").write_text(page("Sources", "sources.html", body, f"{len(hosts)} official hosts"), encoding="utf-8")

    # ------------------------------------------------------------------ methodology
    body = f"""
<p class="lede">What this desk did, what it could not do, and the arithmetic that decides which picks are labelled High.</p>
<div class="notice red"><strong>Egress limitation, stated first.</strong> This sandbox can reach GitHub, npm and PyPI only. `www.olbg.com`,
`api-web.nhle.com`, `statsapi.mlb.com`, `www.atptour.com`, `www.pdc.tv` and `buffedlizard55-lab.github.io` all failed at TLS during this
session. No official page was re-read and no OLBG page was re-harvested. Every fixture and fact therefore carries the URL and capture
timestamp of the desk that did read it, and is described as inherited.</div>
<h2>The band arithmetic</h2>
<div class="panel"><p>American −250 converts to decimal 1.40, and 1 ÷ 1.40 = 0.7143. So the brief's two conditions — implied probability
above 70%, price between −250 and +10000 — can only both hold between <strong>70.00%</strong> and <strong>71.43%</strong>. That is the whole
window: 1.43 points wide. It explains why the two freshest desks both produced clusters of probabilities at 0.7045–0.7140, why one of them
could claim 51 High picks while only 3 of its own lines qualified, and why five genuine high-confidence picks per sport cannot exist inside
that band. This desk publishes the band for what it is and separates genuinely strong favourites into a second, clearly labelled tier.</p></div>
<h2>The seven selection rules</h2>
<div class="wrap"><table><thead><tr><th>Rule</th><th>Test</th><th>Why</th></tr></thead><tbody>
<tr><td>R1</td><td>Fixture must be upcoming at 21:30Z</td><td>A pick on a match that has started is retrospective, not predictive.</td></tr>
<tr><td>R2</td><td>No cross-desk directional conflict</td><td>If two books call different winners, neither is trustworthy enough to publish.</td></tr>
<tr><td>R3</td><td>A recorded fact note must exist</td><td>Without a form, statistics or availability note, a write-up would be invention.</td></tr>
<tr><td>R4</td><td>Estimated probability above 70%</td><td>The brief's threshold.</td></tr>
<tr><td>R5</td><td>Estimated probability at or below 88%</td><td>Above that, the price pays nothing and the "pick" is meaningless.</td></tr>
<tr><td>R6</td><td>Main lines only</td><td>Alternate spreads where the underdog side carries +5.5 at 83% are artefacts of the line, not opinions.</td></tr>
<tr><td>R7</td><td>One pick per fixture, duplicate bets collapsed</td><td>Two desks pricing the same bet must not look like two opinions.</td></tr>
</tbody></table></div>
<h2>How prices were produced and treated</h2>
<ul class="small">
<li>Every line is this project's own estimate, not a bookmaker quote, and not a claim about the market.</li>
<li>Each American price on this site is recomputed from the decimal price rather than copied, so a stale or transposed figure cannot survive.</li>
<li>Where two desks priced the same bet differently, the freshest observation is used and the older one is shown beside it in the market data.</li>
<li>Two-sided books were checked to sum to 1.000 by the source desks; that check is inherited, not re-run.</li>
</ul>
<h2>What was verified, and what was not</h2>
<div class="wrap"><table><thead><tr><th>Claim</th><th>Status</th><th>Basis</th></tr></thead><tbody>
<tr><td>Fixture identity, competition and start time</td><td><span class="badge b-amber">Inherited</span></td><td>Official URL + capture timestamp from the source desk on each row</td></tr>
<tr><td>Form, statistics and injury notes in predictions</td><td><span class="badge b-amber">Inherited</span></td><td>Fact register in <code>data/8a900c04/desk.json</code>, read 2026-10-23T16:45Z</td></tr>
<tr><td>Prices and probabilities</td><td><span class="badge b-blue">Our estimates</span></td><td>Recomputed from decimal; arithmetic audited this session</td></tr>
<tr><td>Cross-desk agreement</td><td><span class="badge b-green">Computed this session</span></td><td>Independent comparison of the three retained desks</td></tr>
<tr><td>Fresh official re-read of any row</td><td><span class="badge b-red">Not possible</span></td><td>Sandbox egress blocked; disclosed rather than simulated</td></tr>
</tbody></table></div>
<h2>Publication rules</h2>
<p class="small">Every table row carries an official link or is explicitly marked unverified. Blank cells are values no source stated.
Nothing is inferred to fill a gap. The word "model" and the word "verified" are kept out of prediction text; the internal vocabulary rule is
enforced by the build gate in <code>scripts/s6b47ea39_predictions.py</code>.</p>
"""
    (SITE / "methodology.html").write_text(page("Method and limits", "methodology.html", body, "Rules, arithmetic, and honesty about their limits"), encoding="utf-8")

    # ------------------------------------------------------------------ repo audit
    repo_findings = [
        ("Canonical dashboard is stale", "high",
         "The landing page the repository publishes at /index.html shows \"Snapshot 21 Oct 2026\" and embeds data-snapshot=2026-10-22T12:29:50Z, "
         "while data/current/snapshot.json was generated 2026-10-22T12:29:50Z. At this build (2026-10-23T21:30Z) that is 33 hours old against a "
         "configured FIXTURE_TTL_HOURS of 6 in pipeline/config.py:7. A reader landing on the site sees day-old fixtures presented as the current desk.",
         "pipeline/config.py", "https://github.com/buffedlizard55-lab/OLBG1/blob/main/pipeline/config.py"),
        ("Hurling is excluded by the canonical pipeline", "high",
         "pipeline/config.py defines EXCLUDED_IDS = {1, 2, 11, 16, 17, 18, 26} and lists 'hurling' in EXCLUDED_NAMES, yet OLBG route 26 is the hurling "
         "hub and the brief's \"Gaelic Sports\" covers both Gaelic football (25) and hurling (26). The retained 8a900c04 desk uses /betting-tips/Hurling/26 "
         "for Gaelic Sports, so the canonical pipeline and the desk evidence disagree about scope.",
         "pipeline/config.py:36", "https://github.com/buffedlizard55-lab/OLBG1/blob/main/pipeline/config.py#L36"),
        ("Conflict markers were committed inside a Python script (resolved)", "low",
         "scripts/se58210b8_predictions.py carried two nested sets of git conflict markers at this desk's baseline (5cb7c69), which made the module "
         "raise SyntaxError on import and failed tests/pipeline/test_desk_e58210b8.py on main. Peer session 3c021b49-olbg1 restored the known-good "
         "version in PR #194 (merge 95cca9f) while this desk was open. Re-checked after rebase: zero markers remain and the full pipeline suite is green. "
         "Recorded as history, not as an open defect.",
         "scripts/se58210b8_predictions.py", "https://github.com/buffedlizard55-lab/OLBG1/blob/main/scripts/se58210b8_predictions.py"),
        ("Two out-of-scope sports are in the canonical scope", "medium",
         "pipeline/config.py:23-24 carry aussie-rules (OLBG 22) and esports (OLBG 23). Neither is on the user's list of 15 sports, and the canonical "
         "site therefore publishes pages for sports the brief does not cover.",
         "pipeline/config.py:23", "https://github.com/buffedlizard55-lab/OLBG1/blob/main/pipeline/config.py#L23"),
        ("41 desk namespaces duplicate the same job", "medium",
         "The repository root holds 41 eight-character desk directories, each with its own index, sports pages and data. data/ holds 45 namespace "
         "directories and 227 scripts. The same slate has been published dozens of times with different counts; nothing on the root site says which "
         "one a reader should trust.",
         "repository root", "https://github.com/buffedlizard55-lab/OLBG1"),
        ("Repository size and page weight", "low",
         "The working tree is about 105 MB, 41 MB of it data/. markets.html alone is 2.2 MB and verification.html 884 KB, which is heavy for a "
         "GitHub Pages site read over a phone.",
         "markets.html", "https://github.com/buffedlizard55-lab/OLBG1/blob/main/markets.html"),
        ("Conflicting fixture identities between desks", "high",
         "The same clubs appear under different names across desks — 'Papua New Guinea Kumuls' vs 'Papua New Guinea', 'Llanelli Scarlets' vs 'Scarlets', "
         "'Matthew Jarvis v Adrien Rozner' where the other two desks have Casey Jarvis and Antoine Rozner. Identity mismatches like the last one can mean "
         "a pick is attached to the wrong player, so those rows are excluded here.",
         "data/65331685/desk.json", "https://github.com/buffedlizard55-lab/OLBG1/blob/main/data/65331685/desk.json"),
    ]
    body = f"""
<p class="lede">A line-by-line review of what the repository actually contains, as of this build. Each finding names the file and links to it so
the claim can be checked directly. Findings about data are on the <a href="flagged.html">review page</a>; this page is about the repository
itself.</p>
<div class="wrap"><table><thead><tr><th>Severity</th><th>Finding</th><th>Where</th><th>Evidence</th></tr></thead><tbody>
{''.join(f"<tr><td><span class='badge {'b-red' if s=='high' else 'b-amber' if s=='medium' else 'b-gray'}'>{s.upper()}</span></td><td><strong>{esc(t)}</strong><br><span class='small muted'>{esc(d)}</span></td><td class='small'>{esc(w)}</td><td class='small'><a href='{esc(u)}' target='_blank' rel='noopener noreferrer'>open ↗</a></td></tr>" for t, s, d, w, u in repo_findings)}
</tbody></table></div>
<h2>What was checked mechanically this session</h2>
<div class="wrap"><table><thead><tr><th>Check</th><th>Result</th></tr></thead><tbody>
<tr><td>Price arithmetic across all {total_lines:,} lines</td><td>{'<span class="badge b-green">pass</span> — every American price re-derived from decimal; the only mismatches are 3-decimal rounding at prices shorter than −1000'}</td></tr>
<tr><td>Duplicate JSON datasets</td><td><span class="badge b-green">pass</span> — no two data JSON files are byte-identical</td></tr>
<tr><td>Tracked bytecode artefacts</td><td><span class="badge b-green">pass</span> — no .pyc or __pycache__ entries are tracked</td></tr>
<tr><td>Fixture identity collisions across desks</td><td><span class="badge b-red">fail</span> — see the identity finding above; {len(events)} fixtures remain after coalescing 218 raw rows</td></tr>
<tr><td>Cross-desk favourite agreement</td><td><span class="badge b-red">fail</span> — {len(audit['directional_conflicts'])} fixtures have opposite favourites</td></tr>
<tr><td>Official link present on every fixture</td><td>{'<span class="badge b-amber">' + str(len(no_source)) + ' rows have none</span>' if no_source else '<span class="badge b-green">pass</span>'}</td></tr>
<tr><td>Prediction writing rules</td><td><span class="badge b-green">pass</span> — {len(preds)} write-ups, minimum 30 words, no shared six-gram, no internal vocabulary</td></tr>
<tr><td>Full repo test suite on the rebased branch</td><td><span class="badge b-green">pass</span> — 258 tests OK (the two failures present at baseline were fixed upstream in PR #194 before this desk merged)</td></tr>
<tr><td>Live re-read of any official source</td><td><span class="badge b-gray">not possible</span> — egress blocked; disclosed</td></tr>
</tbody></table></div>
<h2>Files this desk owns</h2>
<p class="small"><code>data/6b47ea39/</code> (slate, picks, predictions, flags, audit) · <code>scripts/s6b47ea39_*.py</code> ·
<code>6b47ea39/</code> (this site) · <code>tests/pipeline/test_desk_6b47ea39.py</code>. No other desk's files were edited.</p>
"""
    (SITE / "repo-audit.html").write_text(page("Repository audit", "repo-audit.html", body, "Line-by-line review of the repo as it stands"), encoding="utf-8")

    # ------------------------------------------------------------------ reverse engineering
    olbg = [
        ("Golf", 5, "https://www.olbg.com/betting-tips/Golf/5", "Hub returned no tips; outright tournament markets only"),
        ("Volleyball", 21, "https://www.olbg.com/betting-tips/Volleyball/21", "Event pages under All_Volleyball/All_Events/<slug>/21?event_id="),
        ("Rugby Union", 9, "https://www.olbg.com/betting-tips/Rugby_Union/9", "URC, Top 14, Pro D2 sub-routes"),
        ("Cricket", 7, "https://www.olbg.com/betting-tips/Cricket/7", "All_Cricket/All_Events sub-route"),
        ("Snooker", 8, "https://www.olbg.com/betting-tips/Snooker/8", "All_Snooker/All_Events sub-route"),
        ("Darts", 15, "https://www.olbg.com/betting-tips/Darts/15", "All_Darts/All_Events sub-route"),
        ("Baseball", 12, "https://www.olbg.com/betting-tips/Baseball/12", "MLB sub-route with team-slug event pages"),
        ("Gaelic Sports", 25, "https://www.olbg.com/betting-tips/Hurling/26", "Hurling sits on 26; football on 25"),
        ("Greyhounds", 28, "https://www.olbg.com/betting-tips/Greyhounds/28", "Race cards, not matches"),
        ("Tennis", 3, "https://www.olbg.com/betting-tips/Tennis/3", "All_Tennis/All_Events sub-route"),
        ("Motor Racing", 14, "https://www.olbg.com/betting-tips/Motor_Racing/14", "Race winner, podium, top-6, pole"),
        ("Handball", 20, "https://www.olbg.com/betting-tips/Handball/20", "All_Handball/All_Events sub-route"),
        ("Ice Hockey", 13, "https://www.olbg.com/betting-tips/Ice_Hockey/13", "NHL sub-route"),
        ("Basketball", 4, "https://www.olbg.com/betting-tips/Basketball/4", "NBA and EuroLeague sub-routes"),
        ("Rugby League", 10, "https://www.olbg.com/betting-tips/Rugby_League/10", "NRL and IRL World Cup sub-routes"),
    ]
    body = f"""
<p class="lede">How OLBG is laid out, reconstructed from the routes and identifiers recorded by the retained desks. Nothing here was fetched in
this session; the route structure comes from the URLs stored on the fixtures.</p>
<div class="notice blue"><strong>Route shape.</strong> Every sport is a numbered hub: <code>/betting-tips/&lt;Sport_Name&gt;/&lt;id&gt;</code>.
Individual events hang beneath a competition path and end in an event id:
<code>/betting-tips/Ice_Hockey/NHL/NHL/MTL_Canadiens_@_CHI_Blackhawks/13?event_id=199984</code>. The number in the path is the sport id, not
the event id; the event id is the query parameter.</div>
<h2>The 15 hubs in scope</h2>
<div class="wrap"><table><thead><tr><th>Sport</th><th>OLBG id</th><th>Hub route</th><th>Structure recorded</th></tr></thead><tbody>
{''.join(f"<tr><td><strong>{esc(n)}</strong></td><td class='mono'>{i}</td><td class='small'><a href='{esc(u)}' target='_blank' rel='noopener noreferrer'>{esc(u.replace('https://www.',''))} ↗</a></td><td class='small muted'>{esc(x)}</td></tr>" for n, i, u, x in olbg)}
</tbody></table></div>
<h2>Known platform irregularities</h2>
<ul class="small">
<li><strong>Hub tip feeds returned "No tips found"</strong> on the golf hub and, at various points on 23 October, on several other hubs, while the
same event's page still rendered full tip blocks. Discovery had to go through the sport menu and event pages.</li>
<li><strong>Clock handling.</strong> OLBG renders unlabelled America/New_York times on the hub; one retained desk records a one-hour discrepancy
between the OLBG clock and the LNH calendar for Nantes v Chambery, so every start time on this site comes from the official source where one exists
and is flagged where it does not.</li>
<li><strong>Two-sided markets on multi-runner events.</strong> Several retained rows price a greyhound or a driver against a constructed "Field"
side. OLBG does not publish that market; it is a modelling artefact and is treated as one here.</li>
</ul>
<h2>Markets investigated</h2>
<div class="wrap"><table><thead><tr><th>Family</th><th>Markets seen in the retained books</th></tr></thead><tbody>
<tr><td>Result</td><td>Match winner, match result, 80-minute winner, 2-way winner, teammate head-to-head, race winner, pole position</td></tr>
<tr><td>Line</td><td>Handicap and spread (points, goals, runs, sets, frames, legs, strokes), puck line, run line, alternate lines</td></tr>
<tr><td>Totals</td><td>Match total (points, goals, runs, games, sets, frames, legs), team totals, first-half and period terms</td></tr>
<tr><td>Exotic</td><td>Set betting and set score, 1st set winner, first-try and try-scorer markets, top-5/top-6/top-10 finishes, podium</td></tr>
</tbody></table></div>
<p class="small muted">The full priced inventory is on the <a href="markets.html">market explorer</a>: {total_lines:,} lines across 15 sports.</p>
"""
    (SITE / "reverse-engineering.html").write_text(page("OLBG discovery", "reverse-engineering.html", body, "Route structure and market taxonomy"), encoding="utf-8")

    # ------------------------------------------------------------------ sports
    for sport in SPORT_ORDER:
        rows = sorted(by_sport[sport], key=lambda e: (e["start_utc"] or "9999"))
        sport_picks = [p for p in picks if p["sport"] == sport]
        sport_watch = [w for w in watch if w["sport"] == sport]
        fixture_rows = "".join(
            "<tr>"
            f'<td class="mono small">{esc((e["start_utc"] or "not stated")[5:16].replace("T"," "))}</td>'
            f'<td><strong>{esc(e["home"])}</strong> v <strong>{esc(e["away"])}</strong><br><span class="muted small">{esc(e["competition"])}</span></td>'
            f'<td>{state_badge(e["state"])}</td><td class="mono">{len(e["markets"])}</td>'
            f"<td class='small'>{esc(e['favourite']['selection']) if e.get('favourite') else DASH}</td>"
            f"<td>{sources_cell(e['official_sources'])}</td></tr>"
            for e in rows
        )
        pick_rows = ""
        for p in sport_picks:
            writeup = (
                "<a class='small' href='../predictions.html#%s'>write-up</a>" % esc(p["pick_id"])
                if p["pick_id"] in preds else "<span class='muted small'>—</span>"
            )
            pick_rows += (
                "<tr>"
                f'<td class="mono small">{esc(p["start_utc"][5:16].replace("T"," "))}</td>'
                f'<td><strong>{esc(p["match"])}</strong><br><span class="muted small">{esc(p["market"])}</span></td>'
                f'<td>{esc(p.get("display_selection") or p["selection"])}</td><td class="mono">{money(p["american"])}</td>'
                f'<td class="mono">{pct(p["probability"])}</td><td>{tier_badge(p["tier"])}</td>'
                f'<td>{writeup}</td></tr>'
            )
        watch_rows = "".join(
            f"<tr><td>{esc(w['match'])}</td><td>{esc(w.get('display_selection') or w['selection'])}</td><td class='mono'>{money(w['american'])}</td><td class='mono'>{pct(w['probability'])}</td></tr>"
            for w in sport_watch
        )
        body = f"""
<p class="lede">{len(rows)} fixtures in {esc(sport)}, {sum(len(e['markets']) for e in rows):,} priced lines,
{len(sport_picks)} high-confidence picks and {len(sport_watch)} medium watchlist rows.</p>
<h2>High-confidence picks</h2>
<div class="wrap"><table><thead><tr><th>Start</th><th>Match</th><th>Selection</th><th>Price</th><th>Probability</th><th>Tier</th><th>Write-up</th></tr></thead>
<tbody>{pick_rows or '<tr><td colspan="7" class="muted">No fixture in this sport cleared all seven selection rules. The reason is recorded on the picks page.</td></tr>'}</tbody></table></div>
<h2>Medium watchlist</h2>
<div class="wrap"><table><thead><tr><th>Match</th><th>Selection</th><th>Price</th><th>Probability</th></tr></thead><tbody>{watch_rows or '<tr><td colspan="4" class="muted">None.</td></tr>'}</tbody></table></div>
<h2>Fixtures and official sources</h2>
<div class="wrap"><table><thead><tr><th>Start (UTC)</th><th>Fixture</th><th>State</th><th>Lines</th><th>Top-line favourite</th><th>Official source</th></tr></thead><tbody>{fixture_rows}</tbody></table></div>
"""
        (SITE / "sports" / f"{SLUG[sport]}.html").write_text(
            page(sport, f"sports/{SLUG[sport]}.html", body, f"{sport} · 23 Oct 2026 build"), encoding="utf-8"
        )

    print(f"built {len(list(SITE.rglob('*.html')))} pages")
    print("index", (SITE / 'index.html').stat().st_size, "bytes")


if __name__ == "__main__":
    main()
