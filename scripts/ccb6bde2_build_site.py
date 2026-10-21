#!/usr/bin/env python3
"""
ccb6bde2_build_site.py — render the /ccb6bde2/ desk (static, self-contained).

Pages: index (dashboard), markets (taxonomy explorer), sports/<slug> x17,
predictions, calibration, flagged, methodology. Every match row carries its
official governing-body source link. Prices are our model output (v2.1),
never market prices and never betting advice.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "ccb6bde2"

CSS = """
:root{--ink:#182230;--mut:#5b6b7e;--line:#d9e0ea;--bg:#f6f8fb;--card:#fff;
--acc:#0b5394;--hi:#0a7d43;--med:#b7791f;--lo:#8a93a3;--flag:#b3261e}
*{box-sizing:border-box}body{margin:0;font:15px/1.55 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg)}
a{color:var(--acc);text-decoration:none}a:hover{text-decoration:underline}
header.top{background:#10243e;color:#eaf1f9;padding:18px 0 12px}
header.top .wrap,main.wrap,footer .wrap{max-width:1180px;margin:0 auto;padding:0 16px}
header.top h1{margin:0 0 2px;font-size:22px}header.top p{margin:0;color:#b9cadd;font-size:13px}
nav.main{background:#0b1b30;padding:0}nav.main .wrap{max-width:1180px;margin:0 auto;padding:0 16px;display:flex;flex-wrap:wrap;gap:2px}
nav.main a{color:#cfe1f2;padding:9px 12px;font-size:13px;display:inline-block}
nav.main a:hover{background:#12325a;text-decoration:none}
nav.main a.on{background:#eaf1f9;color:#10243e;font-weight:600}
main{padding:20px 0 40px}
h2{font-size:19px;margin:22px 0 8px}h3{font-size:16px;margin:18px 0 6px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:14px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:14px}
.card .n{font-size:26px;font-weight:700}.card .t{color:var(--mut);font-size:12.5px}
table{border-collapse:collapse;width:100%;background:var(--card);border:1px solid var(--line);margin:10px 0;font-size:13.5px}
th,td{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
th{background:#eef3f9;font-size:12.5px;color:#33465e}
tr:last-child td{border-bottom:none}
.conf{font-weight:700;padding:1px 7px;border-radius:9px;font-size:11.5px;white-space:nowrap}
.c-high{background:#e2f4e9;color:var(--hi)}.c-medium{background:#fdf1d7;color:var(--med)}.c-low{background:#eef0f4;color:var(--lo)}
.match{background:var(--card);border:1px solid var(--line);border-radius:8px;margin:14px 0;padding:12px 14px}
.match h3{margin:2px 0 4px;font-size:15.5px}
.meta{color:var(--mut);font-size:12.5px;margin:2px 0 8px}
details{border-top:1px solid var(--line);margin-top:8px;padding-top:6px}
summary{cursor:pointer;font-weight:600;font-size:13px;color:#24354a;padding:3px 0}
.mkt{margin:8px 0 2px;font-weight:600;font-size:13px}.basis{color:var(--mut);font-size:12px;margin:2px 0 6px}
.odds td.num,.odds th.num{text-align:right;font-variant-numeric:tabular-nums}
.note{background:#fff8e6;border:1px solid #eadfae;border-radius:8px;padding:10px 14px;font-size:13.5px;margin:12px 0}
.flagbox{background:#fdf0ef;border:1px solid #efc4c0;border-radius:8px;padding:10px 14px;margin:12px 0}
.flagbox h3{color:var(--flag);margin-top:0}
.pred{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--hi);border-radius:8px;padding:12px 16px;margin:14px 0}
.pred p{margin:6px 0}.pred .facts{color:var(--mut);font-size:12.5px}
footer{background:#10243e;color:#b9cadd;padding:18px 0;font-size:12.5px}
small.mut{color:var(--mut)} .up{color:var(--hi)} .down{color:var(--flag)}
code{background:#eef3f9;padding:0 4px;border-radius:3px;font-size:12.5px}
"""

NAV = [
    ("index.html", "Dashboard"), ("markets.html", "Markets Explorer"),
    ("predictions.html", "High-Confidence Predictions"),
    ("calibration.html", "Calibration Audit"), ("flagged.html", "Flagged for Review"),
    ("methodology.html", "Methodology"),
]


def esc(x) -> str:
    return html.escape(str(x if x is not None else ""))


def page(title: str, active: str, body: str, depth: int = 0) -> str:
    up = "../" * depth
    nav_parts = []
    for h, t in NAV:
        on = ' class="on"' if h == active else ''
        nav_parts.append(f'<a href="{up}{h}"{on}>{t}</a>')
    nav = "".join(nav_parts)
    sports_nav = ""  # inserted by caller where needed
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} — OLBG1 Markets Desk (ccb6bde2)</title><style>{CSS}</style></head>
<body>
<header class="top"><div class="wrap">
<h1>OLBG1 — Deep Markets Desk</h1>
<p>Reverse-engineered OLBG coverage for 17 sports (football/soccer, horse racing, boxing, UFC/MMA, American football, hurling, cycling &amp; specials excluded). Recalibrated own lines (model v2.1) across every derivable market. Snapshot 21 Oct 2026.</p>
</div></header>
<nav class="main"><div class="wrap">{nav}
<a href="{up}../">Root dashboard</a><a href="{up}../docs/">164-event board</a><a href="{up}../ebfbd966/">Crowd desk</a><a href="{up}../aa4e9dbf/">131-event desk</a><a href="{up}../2360a617/">152-event board</a>
</div></nav>
<main><div class="wrap">
{body}
</div></main>
<footer><div class="wrap">Model output only — originated estimates with a documented 5% overround, not market prices and not betting advice. Facts are from official governing-body sources linked on every row; anything that could not be verified is on the Flagged for Review page.</div></footer>
</body></html>"""


def conf_badge(c: str) -> str:
    return f'<span class="conf c-{esc(c)}">{esc(c.upper())}</span>'


def odds_table(m: dict) -> str:
    rows = "".join(
        f'<tr><td>{esc(o["selection"])}</td><td class="num">{o["probability"]*100:.1f}%</td>'
        f'<td class="num">{o["odds"]:.2f}</td><td class="num">{esc(o["american"])}</td>'
        f'<td class="num">{o["fair_odds"]:.2f}</td></tr>' for o in m["outcomes"])
    return (f'<div class="mkt">{esc(m["name"])}{" — line " + esc(m["line"]) if m.get("line") else ""}</div>'
            f'<div class="basis">{esc(m.get("basis",""))}</div>'
            f'<table class="odds"><tr><th>Selection</th><th class="num">Model %</th>'
            f'<th class="num">Book (5% vig)</th><th class="num">US</th><th class="num">Fair</th></tr>{rows}</table>')


def winner_row(r: dict) -> str:
    v21 = r["v21"]
    outs = v21["core_markets"][0]["outcomes"]
    cells = " · ".join(f'{esc(o["selection"])} <b>{o["odds"]:.2f}</b>' for o in outs)
    return cells


def match_block(r: dict) -> str:
    v20, v21 = r["v20"], r["v21"]
    src = r.get("official_source") or {}
    when = (r.get("start_utc") or "").replace("T", " ").replace("Z", " UTC") or r.get("date_local") or "time TBC"
    if not r.get("start_utc"):
        when += " <i>(exact UTC start not published by the governing body — flagged)</i>"
    chg = ""
    if r.get("calibration_changes"):
        items = "".join(f"<li>{esc(c['detail'])}</li>" for c in r["calibration_changes"])
        chg = f'<div class="meta">v2.1 calibration applied:<ul>{items}</ul></div>'
    tier_arrow = ""
    if v20["confidence"] != v21["confidence"]:
        tier_arrow = f' <small class="mut">(v2.0: {esc(v20["confidence"])})</small>'
    pick_arrow = ""
    if v20["pick"] != v21["pick"]:
        pick_arrow = f' <small class="mut">(v2.0 pick: {esc(v20["pick"])} — changed, see Calibration)</small>'
    pp = max(v21["home_probability"], v21["away_probability"])
    core = "".join(odds_table(m) for m in v21["core_markets"])
    groups: dict[str, list[dict]] = {}
    for m in r["expanded_markets"]:
        groups.setdefault(m["group"], []).append(m)
    exp_html = ""
    for g in sorted(groups):
        body = "".join(odds_table(m) for m in groups[g])
        exp_html += f'<details><summary>{esc(g)} ({len(groups[g])} markets)</summary>{body}</details>'
    olbg = r.get("olbg") or {}
    olbg_line = ""
    if olbg.get("url"):
        olbg_line = (f'<div class="meta">OLBG listing: <a href="{esc(olbg["url"])}">event page</a>'
                     f' — tipster consensus: {esc(olbg.get("selection",""))} {esc(olbg.get("consensus",""))}'
                     f' <small>(small samples common — see Flagged F-CCB-09)</small></div>')
    flags = ""
    if r.get("flags"):
        flags = '<div class="meta">Flags: ' + "; ".join(esc(f) for f in r["flags"]) + "</div>"
    inp = r.get("inputs_v21") or {}
    inp_line = ""
    if inp:
        bits = []
        for side in ("home", "away"):
            i = inp.get(side) or {}
            if i.get("label"):
                bits.append(f'{esc(r[side])}: {esc(i.get("label"))} = {esc(i.get("value"))}'
                            + (f' (rating {i.get("rating")})' if i.get("rating") is not None else ""))
        if bits:
            inp_line = '<div class="meta">Sourced inputs: ' + " · ".join(bits) + "</div>"
    else:
        inp_line = '<div class="meta">Sourced inputs: <i>none verified for either side — priced at the neutral venue baseline and capped at LOW (flagged)</i></div>'
    return f"""<div class="match">
<h3>{esc(r["home"])} v {esc(r["away"])} {conf_badge(v21["confidence"])}{tier_arrow}</h3>
<div class="meta">{esc(r["competition"])}{" — " + esc(r["stage"]) if r.get("stage") else ""} · {when} · {esc(r.get("venue",""))}</div>
<div class="meta">Official source: <a href="{esc(src.get("url",""))}">{esc(src.get("name",""))}</a> · status {esc(r["status"])}</div>
{inp_line}{olbg_line}{flags}{chg}
<div><b>Pick:</b> {esc(v21["pick"])}{pick_arrow} — model probability {pp*100:.1f}% · <b>Winner:</b> {winner_row(r)}</div>
<details><summary>Core markets (winner / DNB / handicap / total)</summary>{core}</details>
{exp_html}
</div>"""


SPORT_ORDER = ["tennis", "basketball", "ice-hockey", "baseball", "cricket", "snooker",
               "darts", "rugby-union", "rugby-league", "handball", "volleyball",
               "aussie-rules", "gaelic-football", "esports", "golf", "greyhounds",
               "motor-racing"]
SPORT_NAMES = {"tennis": "Tennis", "basketball": "Basketball", "ice-hockey": "Ice Hockey",
               "baseball": "Baseball", "cricket": "Cricket", "snooker": "Snooker",
               "darts": "Darts", "rugby-union": "Rugby Union", "rugby-league": "Rugby League",
               "handball": "Handball", "volleyball": "Volleyball",
               "aussie-rules": "Aussie Rules (AFLW)", "gaelic-football": "Gaelic Football",
               "esports": "eSports", "golf": "Golf", "greyhounds": "Greyhounds",
               "motor-racing": "Motor Racing"}


def main() -> None:
    exp = json.loads((ROOT / "data" / "market_expansion-ccb6bde2.json").read_text())
    tax = json.loads((ROOT / "data" / "market_taxonomy-ccb6bde2.json").read_text())
    cal = json.loads((ROOT / "data" / "model_calibration-ccb6bde2.json").read_text())
    fresh = {p["match_id"]: p for p in
             json.loads((ROOT / "data" / "predictions-ccb6bde2.json").read_text())["items"]}
    fixtures = {f["id"]: f for f in
                json.loads((ROOT / "data" / "fixtures.json").read_text())["fixtures"]}
    tax_by = {s["sport"]: s for s in tax["sports"]}
    matches = [r for r in exp["matches"] if not r.get("field_event")]
    fields = [r for r in exp["matches"] if r.get("field_event")]
    by_sport: dict[str, list[dict]] = {}
    for r in matches:
        by_sport.setdefault(r["sport"], []).append(r)
    (OUT / "sports").mkdir(parents=True, exist_ok=True)

    # ---------- landing ----------
    total_markets = sum(r["expanded_market_count"] for r in matches)
    highs = [r for r in matches if r["v21"]["confidence"] == "high"]
    sport_rows = ""
    for slug in SPORT_ORDER:
        rows = by_sport.get(slug, [])
        flds = [f for f in fields if f["sport"] == slug]
        nh = sum(1 for r in rows if r["v21"]["confidence"] == "high")
        nm = sum(1 for r in rows if r["v21"]["confidence"] == "medium")
        nl = sum(1 for r in rows if r["v21"]["confidence"] == "low")
        em = sum(r["expanded_market_count"] for r in rows)
        sport_rows += (f'<tr><td><a href="sports/{slug}.html">{SPORT_NAMES[slug]}</a></td>'
                       f'<td>{len(rows)}</td><td>{len(flds)}</td><td>{em}</td>'
                       f'<td>{nh}</td><td>{nm}</td><td>{nl}</td></tr>')
    high_rows = ""
    for r in sorted(highs, key=lambda r: -max(r["v21"]["home_probability"], r["v21"]["away_probability"])):
        src = r.get("official_source") or {}
        pp = max(r["v21"]["home_probability"], r["v21"]["away_probability"])
        high_rows += (f'<tr><td>{SPORT_NAMES[r["sport"]]}</td><td>{esc(r["home"])} v {esc(r["away"])}</td>'
                      f'<td><b>{esc(r["v21"]["pick"])}</b></td><td>{pp*100:.0f}%</td>'
                      f'<td><a href="sports/{r["sport"]}.html">full book</a> · <a href="{esc(src.get("url",""))}">official source</a></td></tr>')
    body = f"""
<h2>Dashboard — 21 October 2026 snapshot</h2>
<div class="note">This desk builds on the repo's verified 134-event governing-body dataset (21–28 Oct 2026). It <b>recalibrates</b> the v2.0 pricing model (small-sample shrinkage, a baseball venue fix, official ATP re-verification) and <b>originates {total_markets} additional markets</b> — correct scores, winning-margin bands, team totals, alternate ladders, set/frame/leg betting, regulation &amp; first-half markets — each derived exactly from the same sourced inputs. Markets that would need an unverified statistic are <a href="flagged.html">flagged, not priced</a>.</div>
<div class="cards">
<div class="card"><div class="n">{len(matches)+len(fields)}</div><div class="t">verified events across 17 in-scope sports</div></div>
<div class="card"><div class="n">{len(matches)}</div><div class="t">two-sided matches repriced (v2.1)</div></div>
<div class="card"><div class="n">{total_markets}</div><div class="t">expanded markets originated (plus 3–4 core markets per match)</div></div>
<div class="card"><div class="n">{len(highs)}</div><div class="t">high-confidence picks after recalibration (31 before)</div></div>
<div class="card"><div class="n">{len(cal["findings"])}</div><div class="t">audit findings published for review</div></div>
</div>
<h2>Sports</h2>
<table><tr><th>Sport</th><th>Matches</th><th>Field events</th><th>Expanded markets</th><th>High</th><th>Medium</th><th>Low</th></tr>{sport_rows}</table>
<h2>High-confidence picks (v2.1)</h2>
<p>High requires a verified fixture, measured governing-body ratings on <b>both</b> sides, and a pick probability over the sport's documented bar — now computed on shrinkage-adjusted ratings. Full written predictions: <a href="predictions.html">predictions page</a>.</p>
<table><tr><th>Sport</th><th>Match</th><th>Pick</th><th>Model %</th><th>Links</th></tr>{high_rows}</table>
<h2>What changed vs the root dashboard (v2.0)</h2>
<ul>
<li><b>R1 — small-sample shrinkage:</b> 56 ratings were built from ≤12 games (EuroLeague 6, handball groups 4, NHL 8–11). At face value they manufactured false certainty — a 74% “high” on Real Madrid from six games. v2.1 shrinks record ratings toward neutral; 12 of 31 v2.0 highs demote.</li>
<li><b>R2 — baseball venue fix:</b> home/road split ratings already contain home advantage; v2.0 added it twice.</li>
<li><b>R3 — official ATP re-verification:</b> Tommy Paul No.15 / Benjamin Bonzi No.100 (atptour.com, 19 Oct 2026) turns a 50/50 baseline row into a rated high-confidence pick. Four fixture ranking labels corrected; WTA rows that could not be verified stay blank.</li>
<li><b>Market depth:</b> from 4 market families to a full book per match — see the <a href="markets.html">Markets Explorer</a>.</li>
</ul>
<p>Excluded per brief (not covered anywhere in this repo): soccer/football, horse racing, boxing, UFC/MMA, American football, hurling, cycling, specials/entertainment.</p>
"""
    (OUT / "index.html").write_text(page("Dashboard", "index.html", body))

    # ---------- per-sport pages ----------
    for slug in SPORT_ORDER:
        rows = sorted(by_sport.get(slug, []),
                      key=lambda r: (r.get("start_utc") or r.get("date_local") or "9", r["id"]))
        flds = [f for f in fields if f["sport"] == slug]
        t = tax_by[slug]
        blocks = "".join(match_block(r) for r in rows)
        field_html = ""
        for f in flds:
            fx = fixtures[f["id"]]
            src = fx["sources"][0] if fx.get("sources") else {}
            np_ = "".join(f'<li><b>{esc(x["market"])}</b> — not originated: {esc(x["missing_official_input"])}</li>'
                          for x in t["investigated_not_priced"])
            field_html += f"""<div class="match"><h3>{esc(fx["home"])} — field event</h3>
<div class="meta">{esc(fx["competition"])} · {esc(fx.get("stage",""))} · {esc(fx.get("date_local") or "")} · {esc(fx.get("venue",""))}</div>
<div class="meta">Official source: <a href="{esc(src.get("url",""))}">{esc(src.get("name",""))}</a> · status {esc(fx["status"])}</div>
<div class="meta">Verified event, not a two-sided match. Standard markets were investigated but are <b>not originated</b> — pricing a full field honestly needs sourced per-entrant ratings this dataset does not contain:</div><ul>{np_}</ul></div>"""
        if not rows and not flds:
            blocks = '<p>No verified fixtures for this sport in the 21–28 Oct 2026 window.</p>'
        nav_sports = " · ".join(
            f'<a href="{s}.html">{SPORT_NAMES[s]}</a>' for s in SPORT_ORDER)
        b = f"""<h2>{SPORT_NAMES[slug]}</h2>
<p><small class="mut">All sports: {nav_sports}</small></p>
<p>{len(rows)} matches repriced under model v2.1 · {sum(r["expanded_market_count"] for r in rows)} expanded markets · market investigation for this sport: <a href="../markets.html#{slug}">Markets Explorer</a></p>
{blocks}{field_html}"""
        (OUT / "sports" / f"{slug}.html").write_text(
            page(SPORT_NAMES[slug], "", b, depth=1))

    # ---------- markets explorer ----------
    exp_rows = ""
    for slug in SPORT_ORDER:
        t = tax_by[slug]
        priced = "".join(f'<li><b>{esc(p["family"])}</b> — {esc(p["derivation"])}</li>'
                         for p in t["expansion_priced_here"]) or "<li>—</li>"
        notp = "".join(f'<li><b>{esc(x["market"])}</b> — {esc(x["missing_official_input"])}</li>'
                       for x in t["investigated_not_priced"]) or "<li>—</li>"
        claimed = "".join(f"<li>{esc(c)}</li>" for c in t["catalog_claimed_originated"]) or "<li>—</li>"
        olbg = "".join(f"<li>{esc(c)}</li>" for c in t["olbg_markets_observed"]) or "<li>—</li>"
        exp_rows += f"""<h3 id="{slug}">{SPORT_NAMES[slug]} <small class="mut">({t["expanded_markets_originated"]} expanded markets originated · <a href="sports/{slug}.html">match books</a>)</small></h3>
<table><tr><th style="width:24%">Market families OLBG lists</th><th style="width:24%">Claimed as “originated” in markets_catalog.json</th><th style="width:26%">Originated on this desk (beyond the 4 v2.0 core markets)</th><th style="width:26%">Investigated — NOT priced (missing official input)</th></tr>
<tr><td><ul>{olbg}</ul></td><td><ul>{claimed}</ul></td><td><ul>{priced}</ul></td><td><ul>{notp}</ul></td></tr></table>"""
    b = f"""<h2>Markets Explorer — every market investigated, sport by sport</h2>
<div class="note"><b>The rule:</b> a market is originated only when its probabilities are exact mathematical consequences of sourced inputs already in the verified dataset (governing-body ratings, documented margin/total distributions, official race formats). A market that needs a statistic we do not have from an official source is listed as <b>investigated — not priced</b> with the missing input named. We never invent a rate to fill a market.</div>
<p>v2.0 priced four families per match (Winner, Draw No Bet, one Handicap line, one Total). The repo's markets catalog claimed much wider “originated” coverage that the delivered lines file did not contain (finding F-CCB-02). This desk closes the derivable gap: <b>{total_markets} expanded markets</b> across {len(matches)} matches.</p>
{exp_rows}"""
    (OUT / "markets.html").write_text(page("Markets Explorer", "markets.html", b))

    # ---------- predictions ----------
    pred_blocks = ""
    for r in sorted(highs, key=lambda r: (r["sport"], r["id"])):
        p = fresh.get(r["id"]) or r.get("prediction_v20")
        src = r.get("official_source") or {}
        newtag = ' <span class="conf c-high">NEW v2.1</span>' if r["id"] in fresh else ''
        facts = "".join(f"<li>{esc(f)}</li>" for f in p.get("facts", []))
        srcs = p.get("sources") or [src]
        src_links = " · ".join(f'<a href="{esc(s.get("url",""))}">{esc(s.get("name","official source"))}</a>'
                                for s in srcs)
        pred_blocks += f"""<div class="pred">
<h3>{esc(r["home"])} v {esc(r["away"])} — {esc(p["bet_line"])}{newtag}</h3>
<div class="meta">{SPORT_NAMES[r["sport"]]} · {esc(r["competition"])} · <a href="sports/{r["sport"]}.html">full market book</a></div>
<p>{esc(p["text"])}</p>
<div class="facts"><b>Verified facts used:</b><ul>{facts}</ul>Sources: {src_links}</div>
</div>"""
    demoted = [tc for tc in exp["tier_changes"] if tc["from"] == "high"]
    dem_rows = "".join(
        f'<tr><td>{esc(tc["id"])}</td><td>{SPORT_NAMES.get(tc["sport"], tc["sport"])}</td>'
        f'<td>{tc["p_pick_old"]*100:.0f}%</td><td>{tc["p_pick_new"]*100:.0f}%</td><td>{esc(tc["to"])}</td></tr>'
        for tc in demoted)
    b = f"""<h2>High-confidence predictions (v2.1)</h2>
<p>{len(highs)} picks clear the high bar after recalibration. Each has a unique written prediction of 30+ words naming the selection, built only from facts in the sourced fixture inputs (plus, for Tommy Paul, this session's official ATP verification). Prices quoted are this desk's v2.1 originated prices; the validator re-checks every quoted winner price against the v2.1 book.</p>
{pred_blocks}
<h2>Demoted by recalibration</h2>
<p>These {len(demoted)} picks were “high” under v2.0 only because tiny early-season samples were taken at face value (finding F-CCB-03). Their v2.0 write-ups remain on the root dashboard's predictions page for the audit trail; this desk no longer presents them as high confidence.</p>
<table><tr><th>Match ID</th><th>Sport</th><th>v2.0 pick %</th><th>v2.1 pick %</th><th>New tier</th></tr>{dem_rows}</table>"""
    (OUT / "predictions.html").write_text(page("Predictions", "predictions.html", b))

    # ---------- calibration ----------
    def pair_rows(pairs, la, lb):
        return "".join(
            f'<tr><td>#{p["rank_a"]} v #{p["rank_b"]}</td><td>{p["rating_a"]}</td><td>{p["rating_b"]}</td><td>{p["p_favourite"]*100:.1f}%</td></tr>'
            for p in pairs)
    thr = cal["confidence_threshold_range"]["by_sport"]
    thr_rows = "".join(f'<tr><td>{esc(k)}</td><td>{v["high"]:.3f}</td><td>{v["med"]:.3f}</td></tr>'
                       for k, v in sorted(thr.items()))
    tier_rows = "".join(
        f'<tr><td>{esc(tc["id"])}</td><td>{SPORT_NAMES.get(tc["sport"],tc["sport"])}</td>'
        f'<td>{esc(tc["from"])} → {esc(tc["to"])}</td><td>{tc["p_pick_old"]*100:.1f}% → {tc["p_pick_new"]*100:.1f}%</td></tr>'
        for tc in exp["tier_changes"])
    pick_rows = "".join(
        f'<tr><td>{esc(pc["id"])}</td><td>{SPORT_NAMES.get(pc["sport"],pc["sport"])}</td>'
        f'<td>{esc(pc["old_pick"])}</td><td>{esc(pc["new_pick"])}</td></tr>'
        for pc in exp["pick_changes"])
    chg_rows = "".join(
        f'<tr><td>{esc(c["match_id"])}</td><td>{esc(c["change"])}</td><td>{esc(c["detail"])}</td></tr>'
        for c in exp["calibration_change_log"])
    fav_rows = "".join(
        f'<tr><td>{esc(s["id"])}</td><td>{esc(s["sport"])}</td><td>{esc(s["pick"])}</td><td>{s["p"]*100:.1f}%</td><td>{esc(s["confidence"])}</td></tr>'
        for s in cal["strongest_favourites"])
    b = f"""<h2>Calibration audit — model v2.0 measured, then fixed (v2.1)</h2>
<p>Line-by-line audit of the delivered model (<code>olbg-independent-logit-normal-v2.0</code>): data integrity first (126/126 lines, every market sums to 1, every fixture carries an official source link, 0 integrity errors), then calibration. Full machine-readable audit: <code>data/model_calibration-ccb6bde2.json</code>.</p>
<h3>What the audit refuted</h3>
<p>The ranking-to-probability curves for individual sports are <b>not</b> too flat. Measured from the shipped code:</p>
<table><tr><th>Tennis (ATP/WTA)</th><th>Rating A</th><th>Rating B</th><th>P(favourite)</th></tr>{pair_rows(cal["tennis_rank_pairs"],"a","b")}</table>
<table><tr><th>Snooker (WST)</th><th>Rating A</th><th>Rating B</th><th>P(favourite)</th></tr>{pair_rows(cal["snooker_rank_pairs"],"a","b")}</table>
<p>Tennis reads sensibly top to bottom. Snooker is hot only at the extreme tail (#{1} v #{57} = 92.8% in a race to 4 — F-CCB-08); without outcome data we flag it rather than invent a new slope.</p>
<h3>What was actually broken</h3>
<ul>
<li><b>Small samples at face value (F-CCB-03):</b> 56 ratings came from ≤12 games. A 4-2 vs 2-4 EuroLeague start became a 33-point rating chasm. Fix R1 shrinks record ratings toward 50 by n/(n+10) (composite standings ratings count games double, as they already embed margin information).</li>
<li><b>Baseball double-count (F-CCB-04):</b> home/road splits plus a separate home logit. Fix R2 neutralises the venue term for split inputs.</li>
<li><b>Missing/stale tennis ratings (F-CCB-06):</b> fixed from the official ATP list of 2026-10-19, read this session.</li>
<li><b>Confidence bars are inconsistent (F-CCB-05)</b> — left unchanged for comparability, displayed openly:</li>
</ul>
<table><tr><th>Sport</th><th>High ≥</th><th>Medium ≥</th></tr>{thr_rows}</table>
<h3>Effect of v2.1</h3>
<p>Confidence counts: v2.0 {esc(exp["confidence_counts_v20"])} → v2.1 {esc(exp["confidence_counts_v21"])}. {len(exp["tier_changes"])} tier changes, {len(exp["pick_changes"])} pick changes, {len(exp["calibration_change_log"])} individual rating adjustments logged.</p>
<table><tr><th>Match</th><th>Sport</th><th>Tier</th><th>Pick probability</th></tr>{tier_rows}</table>
<h3>Pick changes</h3>
<table><tr><th>Match</th><th>Sport</th><th>v2.0 pick</th><th>v2.1 pick</th></tr>{pick_rows}</table>
<p>Two of the three are sub-52% coin flips where shrinkage lets home advantage nose ahead (both low confidence — F-CCB-11). The third is a data fix, not shrinkage: Tommy Paul (official No.15) replaces a baseline coin flip.</p>
<details><summary>Full calibration change log ({len(exp["calibration_change_log"])} entries)</summary>
<table><tr><th>Match</th><th>Change</th><th>Detail</th></tr>{chg_rows}</table></details>
<h3>Strongest v2.0 favourites (audit snapshot)</h3>
<table><tr><th>Match</th><th>Sport</th><th>Pick</th><th>P</th><th>Tier</th></tr>{fav_rows}</table>"""
    (OUT / "calibration.html").write_text(page("Calibration Audit", "calibration.html", b))

    # ---------- flagged ----------
    find_blocks = ""
    for f in cal["findings"]:
        ev = "".join(f'<li>{esc(e)}</li>' for e in f.get("evidence", []))
        find_blocks += f"""<div class="flagbox"><h3>{esc(f["id"])} · {esc(f["title"])}</h3>
<p><b>Severity:</b> {esc(f["severity"])}</p><p>{esc(f["detail"])}</p>
<div class="meta">Evidence / where to review:<ul>{ev}</ul></div></div>"""
    missing = cal.get("missing_start_utc", [])
    unrated = [r for r in matches if not r["v21"].get("both_measured")
               and (r["v21"].get("rating_home") is None or r["v21"].get("rating_away") is None)]
    unrated_rows = "".join(
        f'<tr><td>{esc(r["id"])}</td><td>{SPORT_NAMES[r["sport"]]}</td>'
        f'<td>{esc(r["home"])} v {esc(r["away"])}</td>'
        f'<td>{conf_badge(r["v21"]["confidence"])}</td>'
        f'<td><a href="{esc((r.get("official_source") or {}).get("url",""))}">official source</a></td></tr>'
        for r in unrated)
    b = f"""<h2>Flagged for Review</h2>
<p>Nothing here blocks publication; everything here deserves your eyes. Values that could not be confirmed from an official source were left blank or baseline-priced — never inferred. The root dashboard's <a href="../flagged.html">flagged page</a> carries the earlier sessions' register; this page adds this session's calibration and market findings.</p>
{find_blocks}
<h2>Rows priced without two measured ratings ({len(unrated)})</h2>
<p>These matches carry a verified fixture but lack a sourced numeric rating for at least one side (or use a bounded placeholder). They are priced at the neutral venue baseline with only the documented market structure applied, and confidence is capped per model rules — treat every price in these rows as market-structure-only.</p>
<table><tr><th>ID</th><th>Sport</th><th>Match</th><th>Tier</th><th>Review</th></tr>{unrated_rows}</table>
<h2>Blank kick-off times ({len(missing)})</h2>
<p>{len(missing)} fixtures have a verified date but no official UTC start time (rolling order of play / script-rendered schedules). Start times are left blank rather than inferred: {esc(", ".join(missing[:12]))}{"…" if len(missing)>12 else ""} — full list in <code>data/model_calibration-ccb6bde2.json</code>.</p>"""
    (OUT / "flagged.html").write_text(page("Flagged for Review", "flagged.html", b))

    # ---------- methodology ----------
    b = """<h2>Methodology — how every price on this desk is derived</h2>
<h3>Inputs (sourced facts only)</h3>
<p>Fixtures, rankings, records and seeds come from governing bodies (league/tour/federation sites and APIs) as recorded per-row in <code>data/fixtures.json</code>, plus this session's ATP re-verification from the official PIF ATP Rankings of 2026-10-19. Every match block links its official source. If a value could not be confirmed, it is blank and flagged — e.g. the WTA rankings table returned no rows (script-rendered), so Leylah Fernandez, Aliaksandra Sasnovich and Bejlek stay unrated on this desk.</p>
<h3>Winner model (v2.1)</h3>
<p>Logistic in rating points: <code>p_home = sigmoid(logit(p_venue) + (r_home − r_away)/scale)</code>, per-sport scale and venue baselines in <code>scripts/model.py</code>, draw mass for draw-sports as in v2.0. A strength edge is applied only when <b>both</b> sides carry a sourced rating; otherwise the match is priced at the venue baseline and capped at LOW.</p>
<h3>Recalibration R1–R3</h3>
<ul>
<li><b>R1 shrinkage:</b> record-derived ratings from ≤40 games are shrunk toward 50 by <code>n/(n+10)</code> (composite standings-mapped ratings count each game double). Rankings that aggregate long histories (ATP/WTA/WST/PDC/ICC/IRL) are not shrunk.</li>
<li><b>R2 baseball:</b> home/road split inputs priced at a neutral 0.500 venue term (splits already embed venue).</li>
<li><b>R3 tennis:</b> ratings re-derived from the official ATP list of 2026-10-19.</li>
<li><b>Not changed:</b> logit scales, confidence thresholds. The audit found the scales plausible (Calibration page) and refitting without outcome data would be invention, not calibration.</li>
</ul>
<h3>Expanded-market derivations</h3>
<ul>
<li><b>Race formats</b> (darts Bo11 legs, snooker Bo7 frames, tennis Bo3 sets, volleyball Bo5 sets): the per-unit win probability q is solved from the match price by inverting the negative-binomial race formula, so correct scores, total-unit ladders and unit handicaps are exactly consistent with the winner price. Units are assumed i.i.d. (A2).</li>
<li><b>Margin/total sports:</b> margin and total are independent normals with the sport's documented sigmas (A1). Winning-margin bands, alternate ladders, and team totals (score = (Total ± Margin)/2) are closed-form integrals of those normals.</li>
<li><b>Tennis games</b> (A3): expected sets from the exact set distribution × 9.7 games/set, blended 50/50 with the documented baseline total; <b>volleyball points</b> (A4): set distribution × 44.0 points/set.</li>
<li><b>Half / First-5 markets</b> (A5): expectation split pro-rata, sigma by the square root of the time share.</li>
<li><b>Hockey regulation:</b> continuity-corrected normal margin (|margin| &lt; 0.5 goals = regulation draw).</li>
</ul>
<h3>What is deliberately not priced</h3>
<p>Any market needing a per-player rate we cannot source officially — 180s, centuries, aces, top batter, anytime scorers, player props, full-field golf/greyhound/F1 books. Each is listed in the <a href="markets.html">Markets Explorer</a> with the missing official input named. An empty price is honest; an invented one is not.</p>
<h3>Odds conventions</h3>
<p>Book prices include a symmetric 5% overround (fair and US formats shown alongside). Every market is a true partition: probabilities sum to 1 (validated). Lines end in .5 — no pushes.</p>
<h3>Reproduce</h3>
<p><code>python3 scripts/ccb6bde2_audit.py</code> → <code>python3 scripts/ccb6bde2_expand_markets.py</code> → <code>python3 scripts/ccb6bde2_taxonomy.py</code> → <code>python3 scripts/ccb6bde2_build_site.py</code> → <code>python3 scripts/ccb6bde2_validate.py</code></p>"""
    (OUT / "methodology.html").write_text(page("Methodology", "methodology.html", b))

    print(f"built {OUT}: index, markets, predictions, calibration, flagged, methodology, "
          f"{len(SPORT_ORDER)} sport pages")


if __name__ == "__main__":
    main()
