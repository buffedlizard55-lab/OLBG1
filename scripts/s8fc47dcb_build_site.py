"""
s8fc47dcb_build_site.py — renders the T60 desk at /8fc47dcb/ from data/8fc47dcb/*.json.
Static, dependency-free; every fixture table row carries at least one official source link.
"""
from __future__ import annotations

import html
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "8fc47dcb"
OUT = ROOT / "8fc47dcb"
DESK = "8fc47dcb"
DATE = "22 October 2026 (UTC)"

ds = json.loads((DATA / "dataset.json").read_text())
preds = json.loads((DATA / "predictions.json").read_text())["items"]
ver = json.loads((DATA / "verification.json").read_text())["rows"]
flagged = json.loads((DATA / "flagged.json").read_text())["items"]
olbg = json.loads((DATA / "olbg.json").read_text())
rows = ds["rows"]
priced = [r for r in rows if r["priced"]]
counts = ds["counts"]
ver_by_id = {v["match_id"]: v for v in ver}
pred_by_id = {p["match_id"]: p for p in preds}
SPORT_NAMES = {s["slug"].lower().replace("_", "-"): s["name"] for s in olbg["sports"]}

CSS = """:root{--bg:#0b1220;--panel:#121c30;--line:#243352;--txt:#e8eefb;--mut:#9fb0d0;--acc:#5eead4;--hi:#34d399;--med:#fbbf24;--low:#94a3b8;--bad:#f87171}
*{box-sizing:border-box}body{margin:0;font:15px/1.55 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--txt)}
a{color:var(--acc)}header{background:#0e1830;border-bottom:1px solid var(--line);padding:14px 20px;position:sticky;top:0;z-index:5}
header h1{font-size:19px;margin:0 0 4px}header p{margin:0;color:var(--mut);font-size:13px}
nav{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}nav a{background:var(--panel);border:1px solid var(--line);border-radius:999px;padding:4px 12px;text-decoration:none;font-size:13px;color:var(--txt)}
nav a:hover{border-color:var(--acc)}main{max-width:1180px;margin:0 auto;padding:20px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:14px 0}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px}.kpi b{font-size:24px;display:block}.kpi span{color:var(--mut);font-size:12px}
table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);font-size:13.5px}
th,td{border-bottom:1px solid var(--line);padding:7px 9px;text-align:left;vertical-align:top}th{color:var(--mut);font-size:12px;text-transform:uppercase;letter-spacing:.04em}
.badge{display:inline-block;border-radius:999px;padding:1px 9px;font-size:12px;font-weight:700}.high{background:#064e3b;color:var(--hi)}.medium{background:#451a03;color:var(--med)}.low{background:#1e293b;color:var(--low)}
.v-confirmed{color:var(--hi)}.v-corrected{color:var(--med)}.v-not-rechecked{color:var(--bad)}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:12px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px}
.small{color:var(--mut);font-size:12.5px}details summary{cursor:pointer;color:var(--acc);font-size:13px}
input[type=search]{background:var(--panel);border:1px solid var(--line);color:var(--txt);border-radius:8px;padding:8px 12px;width:min(460px,100%)}
select{background:var(--panel);border:1px solid var(--line);color:var(--txt);border-radius:8px;padding:8px}
footer{max-width:1180px;margin:0 auto;padding:18px 20px 34px;color:var(--mut);font-size:12.5px;border-top:1px solid var(--line)}
.warn{border-left:4px solid var(--bad);background:#1c1226;padding:10px 14px;border-radius:6px}
"""


def e(x):
    return html.escape(str(x))


def src_links(fixture, rechecks=None, maxn=2):
    out = []
    for s in (rechecks or [])[:1] + fixture["sources"][:maxn]:
        out.append(f'<a href="{e(s["url"])}" rel="noopener">{e(s["name"])}</a>')
    return "<br>".join(out)


def shell(title, body, depth=0):
    p = "../" * depth
    nav = "".join(f'<a href="{h if h.startswith("../") else p + h}">{e(t)}</a>' for t, h in [
        ("Overview", "index.html"), ("All picks & markets", "picks.html"), ("Predictions", "predictions.html"),
        ("Sports", "sports.html"), ("Methodology", "methodology.html"), ("Reverse engineering", "reverse-engineering.html"),
        ("Sources", "sources.html"), ("Verification", "verification.html"), ("Flagged for Review", "flagged.html"),
        ("Primary desk", "../" * (depth + 1) + "index.html")])
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} — OLBG1 T60 desk ({DESK})</title><link rel="stylesheet" href="{p}assets/style.css"></head><body>
<header><h1>OLBG1 — Fresh {DATE} desk <span class="small">(T60 · session {DESK})</span></h1>
<p>Future-only fixtures after {ds['cutoff_utc']} · own fair-price lines · strict High = selected-line model probability &ge;70% at fair odds 1.40–101.00 (−250…+10000) · every High re-read on an official page this session. Model output only — not betting advice.</p><nav>{nav}</nav></header>
<main>{body}</main>
<footer>Prices are this desk's own model estimates (fair 0% overround headline; 5%-vig equivalent shown alongside), not market prices and not betting advice. Fixture facts link to official governing-body sources; values that could not be confirmed are blank or flagged, never inferred. <a href="{p}flagged.html">Flagged for Review</a> · <a href="{p}verification.html">Verification register</a> · Data: <code>data/{DESK}/</code> in the repository. Built {DATE}.</footer>
<script src="{p}assets/app.js"></script></body></html>"""


def link_list(sources):
    return "<br>".join('<a href="' + e(s["url"]) + '">' + e(s["name"]) + "</a>" for s in sources)


def conf_badge(c):
    return f'<span class="badge {c}">{c.upper()}</span>'


def markets_details(r, depth=0):
    parts = ['<details><summary>Full originated markets (fair · 5%-vig in brackets)</summary>']
    for mk in r["markets"]:
        ocs = " · ".join(f'{e(o["selection"])} <b>{o["fair_odds"]}</b> ({e(o["fair_american"])}; book {o["book5_odds"]}) {o["implied_pct"]}%' for o in mk["outcomes"])
        parts.append(f'<div class="small"><b>{e(mk["name"])}{(" " + e(mk["line"])) if mk.get("line") else ""}</b> — {ocs}<br><i>{e(mk.get("basis",""))}</i></div>')
    for un in r["unavailable_markets"]:
        parts.append(f'<div class="small"><b>{e(un["name"])}</b> — {e(un["status"])}: {e(un["reason"])} <a href="{"../" * depth}flagged.html">flagged</a></div>')
    parts.append("</details>")
    return "".join(parts)


def pick_row(r, depth=0):
    f = r["fixture"]
    v = ver_by_id.get(f["id"], {})
    sel = r.get("strict_selection") or {}
    sel_txt = (f'{e(sel.get("selection","—"))}<br><span class="small">{e(sel.get("market",""))} · p {sel.get("probability",0):.1%}'
               f' · fair {sel.get("fair_odds","")} ({e(sel.get("fair_american",""))})</span>') if sel else "—"
    onsite = f' <a href="{"../" * depth}predictions.html#{e(f["id"])}">prediction</a>' if f["id"] in pred_by_id else ""
    return (f'<tr data-sport="{e(f["sport"])}" data-conf="{e(r["confidence"])}"><td>{e(f["start_utc"])}<br><span class="small">{e(f["competition"])}</span></td>'
            f'<td><b>{e(f["home"])} v {e(f["away"])}</b><br><span class="small">{e(f["venue"] or "venue not recorded — flagged")} · winner call: <b>{e(r["winner_call"])}</b></span>{markets_details(r, depth)}</td>'
            f'<td>{r["home_probability"]:.1%}{(" / " + format(r["draw_probability"], ".1%") + " / ") if r["draw_probability"] else " / "}{r["away_probability"]:.1%}<br><span class="small">E[margin] {r["expected_margin"]:+.1f} · ratings {r["rating_home"]}–{r["rating_away"]}{"" if r["both_measured"] else " (not both measured)"}</span></td>'
            f'<td>{sel_txt}{onsite}</td><td>{conf_badge(r["confidence"])}<br><span class="small">{"; ".join(map(e, r["tier_reasons"]))}</span></td>'
            f'<td><span class="v-{e(v.get("status","not-rechecked"))}">{e(v.get("status","not-rechecked"))}</span><br>{src_links(f, v.get("recheck_sources"))}</td></tr>')


def picks_table(subset, depth=0):
    return ('<table><thead><tr><th>Start (UTC)</th><th>Match &amp; markets</th><th>Model win %</th><th>Strict-band selection</th><th>Confidence</th><th>Verification &amp; official source</th></tr></thead><tbody>'
            + "".join(pick_row(r, depth) for r in subset) + "</tbody></table>")


def write(name, content, sub=""):
    path = OUT / sub / name if sub else OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    write("assets/style.css", CSS)
    write("assets/app.js", "document.addEventListener('DOMContentLoaded',()=>{const q=document.querySelector('#q'),c=document.querySelector('#conf');function f(){const t=(q?.value||'').toLowerCase(),k=c?.value||'';document.querySelectorAll('tbody tr').forEach(r=>{r.style.display=(!t||r.textContent.toLowerCase().includes(t))&&(!k||r.dataset.conf===k)?'':'none'})}q&&q.addEventListener('input',f);c&&c.addEventListener('change',f)});")

    highs = [r for r in priced if r["confidence"] == "high"]
    by_sport = Counter(r["fixture"]["sport"] for r in rows)
    sport_cards = "".join(
        f'<div class="card"><b><a href="sports/{e(s)}.html">{e(SPORT_NAMES.get(s, s))}</a></b><br><span class="small">{n} future fixture(s) · '
        f'{sum(1 for r in priced if r["fixture"]["sport"]==s and r["confidence"]=="high")} High · '
        f'{sum(1 for r in priced if r["fixture"]["sport"]==s and r["confidence"]=="medium")} Medium · '
        f'{sum(1 for r in priced if r["fixture"]["sport"]==s and r["confidence"]=="low")} Low</span></div>'
        for s, n in sorted(by_sport.items()))
    body = f"""<div class="kpis">
<div class="kpi"><b>{counts['future']}</b><span>future fixtures after cutoff</span></div>
<div class="kpi"><b>{counts['priced']}</b><span>two-sided matches priced (own lines)</span></div>
<div class="kpi"><b>{counts['high']}</b><span>strict High picks (&ge;70% in window)</span></div>
<div class="kpi"><b>{counts['medium']} / {counts['low']}</b><span>Medium / Low</span></div>
<div class="kpi"><b>{sum(1 for v in ver if v['status']=='confirmed')} / {sum(1 for v in ver if v['status']=='corrected')} / {sum(1 for v in ver if v['status']=='not-rechecked')}</b><span>confirmed / corrected / not re-checked (this session)</span></div>
<div class="kpi"><b>{counts['expired']} + {counts['undated']}</b><span>expired + undated (Flagged page)</span></div></div>
<div class="warn"><b>How to read this desk.</b> The primary desk's 134-row snapshot was re-cut at {ds['cutoff_utc']}: {counts['expired']} started rows expired, {counts['undated']} undated rows cannot be listed as upcoming. Every candidate High was re-read on its governing body's site today; {sum(1 for v in ver if v['status']=='corrected')} rows needed correcting first (including EuroLeague records, the Vegas Golden Knights points percentage and four IRL world ranks). Anything not re-read is capped below High with the blocker named.</div>
<h2>Strict High-confidence picks</h2>{picks_table(highs)}
<h2>Sports</h2><div class="grid">{sport_cards}</div>
<p class="small">Other in-scope OLBG sports (tennis, snooker, golf, eSports, greyhounds) have no dated future fixture on the primary desk after the cutoff — their rows are undated or expired and are listed on the <a href="flagged.html">Flagged for Review</a> page rather than priced on a guess.</p>"""
    write("index.html", shell("Overview", body))

    body = ('<h2>All priced matches — winner call, handicap &amp; total ladders per match</h2>'
            '<p><input type="search" id="q" placeholder="Filter team, competition…"> <select id="conf"><option value="">All confidence</option><option>high</option><option>medium</option><option>low</option></select></p>'
            + picks_table(priced))
    write("picks.html", shell("All picks & markets", body))

    cards = ""
    for p in preds:
        r = next(x for x in priced if x["fixture"]["id"] == p["match_id"])
        v = ver_by_id[p["match_id"]]
        cards += (f'<article class="card" id="{e(p["match_id"])}"><h3>{e(p["match"])} — {e(p["selection"])}</h3>'
                  f'<p class="small">{e(p["start_utc"])} · {e(p["competition"])} · {e(p["market"])} · model probability {p["probability"]:.1%} · fair {p["fair_odds"]} ({e(p["fair_american"])}) — inside −250…+10000 · match-winner call: <b>{e(p["winner_call"])}</b> · verification: <span class="v-{e(v["status"])}">{e(v["status"])}</span></p>'
                  f'<p>{e(p["text"])}</p><p class="small">{p["words"]} words · Official sources read this session: '
                  + "; ".join(f'<a href="{e(s["url"])}">{e(s["name"])}</a>' for s in p["recheck_sources"])
                  + ' · Recorded fixture sources: ' + "; ".join(f'<a href="{e(s["url"])}">{e(s["name"])}</a>' for s in p["sources"]) + "</p></article>")
    write("predictions.html", shell("High-confidence predictions",
          f"<h2>{len(preds)} high-confidence predictions</h2><p>Each is an original, hand-written preview of at least 30 words, names the exact selection, and uses only facts read on official pages today (linked under each card). Prices are structured fields, never baked into the prose.</p>" + cards))

    sbody = "<h2>Sport categories</h2><div class='grid'>" + "".join(
        f'<div class="card"><b><a href="sports/{e(s)}.html">{e(SPORT_NAMES.get(s, s))}</a></b><br><span class="small">{sum(1 for r in rows if r["fixture"]["sport"]==s)} future fixture(s)</span></div>'
        for s in sorted(by_sport)) + "</div>"
    write("sports.html", shell("Sports", sbody))
    for s in sorted(by_sport):
        sub = [r for r in priced if r["fixture"]["sport"] == s]
        write(f"sports/{s}.html", shell(SPORT_NAMES.get(s, s), f"<h2>{e(SPORT_NAMES.get(s, s))}</h2>" + picks_table(sub, depth=1), depth=1))

    meth = """<h2>Methodology — our own lines, stated in full</h2>
<div class="card"><h3>Inputs</h3><p>Fixture facts and strength inputs come from the primary desk's recorded governing-body sources, corrected where today's re-read superseded them (see <a href="verification.html">Verification</a>). A strength edge is applied <b>only when both sides carry a measured official rating</b>; otherwise the model uses the sport's neutral venue baseline and confidence is capped at Low. For re-verified rugby-league rows the rating is the official IRL ranking percentage read live today; for NHL/EuroLeague it is the official points/win percentage ×100.</p></div>
<div class="card"><h3>Model (assumptions labelled)</h3><p>Win probability: logit(venue base) + (rating gap ÷ sport scale), using the root model's published constants (<code>scripts/model.py</code>: per-sport <i>p_base, scale, sigma</i>). Margin ~ Normal(E[M], sigma); totals use the published assumed competition baselines — <b>modelling assumptions, not sourced team statistics</b> — so no total-market selection can be High on this desk. Half-point handicap rungs target 50/60/70/80% favourite cover with the exact probability recomputed at the snapped line. In ice hockey, +0.5 puck-line selections are model-margin lines (they win when the selection avoids a modelled defeat; settlement semantics would be regulation +0.5).</p></div>
<div class="card"><h3>The −250…+10000 window and &gt;70% — the arithmetic</h3><p>Fair odds 1.40 = −250 and imply 71.43%. A strict High therefore needs an exact model probability in the narrow band <b>70.00%–71.43%</b> at fair (0% overround) prices. With a 5% margin the band is empty (70% would price at 1.36/−277), which is why the root desk's 68%-rung ladder contains zero &gt;70% picks. This desk originates <b>fair prices</b> as the headline and prints the 5%-vig equivalent next to every quote; band membership is judged on the exact probability (≤71.4286%), not on rounded odds — a 71.5% line that rounds to 1.40 is rejected (Panathinaikos and England (RL) failed on exactly this today and sit at Medium).</p></div>
<div class="card"><h3>Confidence gates (all must pass for High)</h3><p>1) fixture status <i>verified</i> on the primary desk; 2) measured ratings on both sides; 3) two-way win probability ≥60% (a coin flip cannot manufacture a High through a plus-handicap); 4) a favourite winner/handicap line in the exact band above (cricket: match-winner market only); 5) the row was re-read on an official page <b>this session</b> (confirmed or corrected). Medium = both measured, verified, clears the sport's root medium floor. Low = everything else. Each row on the picks page prints which gate failed.</p></div>
<div class="card"><h3>Markets investigated</h3><p>Priced per match where derivable: Match Winner (2/3-way), Draw No Bet, Handicap/Spread ladder (up to 4 rungs), Match Total ladder (up to 5 rungs). Investigated but not priced — named on every row with the missing official input: Correct Score/Exact Margin, Player Props, Period/Half/Set/Leg sub-markets, and totals where no official baseline exists.</p></div>"""
    write("methodology.html", shell("Methodology", meth))

    tax_rows = "".join(
        f'<tr><td>{e(s["name"])}</td><td>{s["id"]}</td><td><a href="https://www.olbg.com/betting-tips/{e(s["slug"])}/{s["id"]}">OLBG hub</a></td>'
        f'<td>{"in scope" if s["in_scope"] else "excluded"}</td><td class="small">{e(s.get("exclusion_reason") or s.get("borderline_scope_flag") or "")}</td></tr>'
        for s in olbg["sports"])
    hub_ev = "".join(f'<div class="card"><b>{e(h["hub"])}</b> — <a href="{e(h["url"])}">{e(h["url"])}</a> (read {e(h["read"])})<p class="small">{e(h["observation"])}</p></div>' for h in olbg["live_hub_evidence"])
    write("reverse-engineering.html", shell("Reverse engineering OLBG",
          f"""<h2>OLBG taxonomy — re-read {DATE}</h2><p>{e(olbg['reread'])}</p><p class="small">{e(olbg['excluded_note'])} Excluded hubs are listed for completeness of the map; no excluded-sport fixture is priced anywhere on this desk. Hub URLs below are OLBG's own pages (the subject of the reverse engineering), not governing-body evidence for sporting facts.</p>
<table><thead><tr><th>Sport</th><th>OLBG ID</th><th>Hub</th><th>Scope</th><th>Note</th></tr></thead><tbody>{tax_rows}</tbody></table>
<h2>Live hub evidence (read this session)</h2>{hub_ev}
<p>URL grammar: <code>https://www.olbg.com/betting-tips/{{Sport}}/{{id}}</code> with competition sub-routes beneath it (e.g. <code>/Basketball/European/Euroleague/…?event_id=535923</code>). Card fields observed today: pairing, competition, unlabelled local-clock start, tipster-consensus selection, market name (“Money Line”), win-tips fraction and percentage. OLBG is a tipster aggregator, so none of its values are used to verify a fixture, rating or start time here.</p>"""))

    reg = {}
    for v in ver:
        for s in v["recheck_sources"]:
            reg[s["url"]] = (s["name"], "re-read this session (2026-10-22)")
    for r in rows:
        for s in r["fixture"]["sources"]:
            reg.setdefault(s["url"], (s["name"], "recorded on primary desk; not re-fetched this session"))
    srows = "".join(f'<tr><td>{e(n)}</td><td><a href="{e(u)}">{e(u)}</a></td><td class="small">{e(t)}</td></tr>' for u, (n, t) in sorted(reg.items(), key=lambda kv: kv[1][1]))
    write("sources.html", shell("Official sources",
          f"<h2>Source register ({len(reg)} URLs)</h2><p>Only governing bodies, leagues, tours and tournament organisers verify sporting facts on this desk. OLBG pages appear solely as the subject of the reverse-engineering map.</p><table><thead><tr><th>Source</th><th>URL</th><th>Status</th></tr></thead><tbody>{srows}</tbody></table>"))

    vrows = "".join(
        '<tr><td>' + e(v["start_utc"]) + '</td><td><b>' + e(v["match"]) + '</b><br><span class="small">' + e(v["sport"]) + '</span></td>'
        '<td><span class="v-' + e(v["status"]) + '"><b>' + e(v["status"]) + '</b></span></td><td class="small">' + e(v["evidence"]) + '</td>'
        '<td>' + link_list(v["recheck_sources"] or v["recorded_sources"]) + '</td></tr>'
        for v in ver)
    write("verification.html", shell("Verification register",
          f"<h2>Line-by-line verification — {len(ver)} future rows</h2><p>Checked {DATE} in this session against official pages. <b>confirmed</b> = priced facts match; <b>corrected</b> = official page superseded a stored value and the price was rebuilt; <b>not-rechecked</b> = blocker named, stored snapshot retained, capped below High.</p><table><thead><tr><th>Start (UTC)</th><th>Match</th><th>Status</th><th>Evidence / blocker</th><th>Official link(s)</th></tr></thead><tbody>{vrows}</tbody></table>"))

    frows = "".join(
        '<tr><td>' + e(f["kind"]) + '</td><td><b>' + e(f["match"]) + '</b><br><span class="small">' + e(f["match_id"]) + '</span></td><td class="small">' + e(f["detail"]) + '</td>'
        '<td>' + (link_list(f["sources"]) or "—") + '</td></tr>' for f in flagged)
    write("flagged.html", shell("Flagged for Review",
          f"""<h2>Flagged for Review ({len(flagged)} items)</h2><p>Nothing here blocks publication. Corrected rows show what today's official-page re-read changed; not-rechecked rows name the exact blocker; expired and undated rows are excluded from pricing by the explicit cutoff ({ds['cutoff_utc']}) — expiry is timestamp arithmetic, never an asserted result.</p>
<table><thead><tr><th>Kind</th><th>Item</th><th>Detail</th><th>Official link(s) for manual review</th></tr></thead><tbody>{frows}</tbody></table>"""))

    print(f"pages built under {OUT}")


if __name__ == "__main__":
    main()
