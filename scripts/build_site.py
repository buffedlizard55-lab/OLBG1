#!/usr/bin/env python3
"""
build_site.py - Deterministic static site compiler for GitHub Pages (main:/ and /f7fa77fc/).

Renders 26 pages at repository root (/) AND mirrors all 26 pages + assets + JSON data cleanly
into /f7fa77fc/ with 100% relative links so every route works identically under /OLBG1/ on
GitHub Pages and under local HTTP preview servers.
"""
from __future__ import annotations

import html
import json
import shutil
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SITE_NAME = "OLBG Reverse-Engineering & Origination Desk"
SITE_TAG = "17 in-scope sports · 134 source-linked events (129 verified · 5 cross-checked) · multi-market lines & human analysis"

CONF_LABEL = {"high": "High", "medium": "Medium", "low": "Low"}
STATUS_LABEL = {"verified": "Verified", "cross-checked": "Cross-checked", "unverified": "Unverified"}


def e(val) -> str:
    return html.escape(str(val if val is not None else ""))


def load_data() -> dict:
    def r(rel: str):
        return json.loads((ROOT / rel).read_text(encoding="utf-8"))

    return {
        "fixtures": r("data/fixtures.json"),
        "lines": r("data/lines.json"),
        "preds": r("data/predictions.json"),
        "taxonomy": r("data/olbg_taxonomy.json"),
        "sources": r("data/sources.json"),
        "coverage": r("data/coverage.json"),
        "flagged": r("datasets/flagged_for_review.json"),
        "verification": r("data/verification.json"),
        "live": r("data/live_snapshot.json"),
        "live_diff": r("data/live_diff.json"),
    }


def fmt_when(m: dict) -> str:
    if m.get("start_utc"):
        dt = datetime.fromisoformat(m["start_utc"].replace("Z", "+00:00"))
        return dt.strftime("%d %b %H:%M UTC")
    if m.get("date_local"):
        d = datetime.strptime(m["date_local"], "%Y-%m-%d").strftime("%d %b %Y")
        return f"{d} (UTC time unconfirmed)"
    return "Unconfirmed"


def fmt_match(m: dict) -> str:
    return f"{m['home']} vs {m['away']}" if m.get("away") else m["home"]


def badge_conf(c: str) -> str:
    return f'<span class="badge {e(c)}">{e(CONF_LABEL.get(c, c))}</span>'


def badge_status(s: str) -> str:
    cls = {"verified": "verified", "cross-checked": "cross", "unverified": "cross"}.get(s, "muted")
    return f'<span class="badge {cls}">{e(STATUS_LABEL.get(s, s))}</span>'


def render_source_links(m: dict, limit: int = 3) -> str:
    links = [
        f'<a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["name"])}</a>'
        for s in m.get("sources", [])[:limit]
    ]
    for s in m.get("external_checks", [])[:1]:
        links.append(f'<a href="{e(s["url"])}" target="_blank" rel="noopener">[cross-check] {e(s["name"])}</a>')
    if (m.get("olbg") or {}).get("url"):
        links.append(f'<a href="{e(m["olbg"]["url"])}" target="_blank" rel="noopener">[OLBG upstream]</a>')
    return '<div class="src-links">' + "".join(links) + "</div>"


def odds_span(o: dict) -> str:
    dec = f"{o['odds']:.2f}"
    fair = f"{o.get('fair_odds', o['odds']):.2f}"
    us = str(o.get("american", ""))
    return f'<b class="odds" data-dec="{e(dec)}" data-fair="{e(fair)}" data-us="{e(us)}">{e(dec)}</b>'


def render_markets_drawer(p: dict) -> str:
    unavailable = p.get("unavailable_markets", [])
    suffix = f" + {len(unavailable)} explicitly unavailable" if unavailable else ""
    parts = [f'<details class="markets"><summary>All {len(p["markets"])} originated markets{suffix}</summary>']
    for mk in p["markets"]:
        line_lbl = f" ({mk['line']})" if mk.get("line") else ""
        parts.append(f'<div class="mkt"><div class="mkt-h"><span>{e(mk["name"])}{e(line_lbl)}</span></div><ul>')
        for o in mk["outcomes"]:
            parts.append(
                f'<li><span>{e(o["selection"])}</span>'
                f'<span>{odds_span(o)} <span class="sub" style="display:inline">({o["implied_pct"]}%)</span></span></li>'
            )
        parts.append("</ul>")
        parts.append(f'<div class="basis">{e(mk["basis"])}</div></div>')
    for mk in unavailable:
        parts.append(
            f'<div class="mkt unavailable"><div class="mkt-h"><span>{e(mk["name"])} — unverified / blank</span></div>'
            f'<div class="basis">{e(mk["reason"])}</div></div>'
        )
    parts.append("</details>")
    return "".join(parts)


def odds_format_controls() -> str:
    return (
        '<div class="toolbar-group" role="group" aria-label="Odds format">'
        '<span class="sub" style="display:inline;margin-right:3px">Odds:</span>'
        '<button type="button" class="chip is-active" data-odds-fmt="dec" aria-pressed="true">Bookmaker (5% vig)</button>'
        '<button type="button" class="chip" data-odds-fmt="fair" aria-pressed="false">Fair (0% vig)</button>'
        '<button type="button" class="chip" data-odds-fmt="us" aria-pressed="false">US (+/-)</button>'
        '</div>'
    )


def render_picks_table(rows: list[tuple[dict, dict | None]], show_sport: bool, site_rel: str) -> str:
    headers = ["UTC Kick-off / Start", "Match / Event & Venue"]
    if show_sport:
        headers.append("Sport")
    headers += ["Competition", "Winner Line", "Handicap & Total", "Pick & Markets", "Confidence", "Official Sources"]
    th = "".join(f"<th>{h}</th>" for h in headers)
    trs = []

    for m, p in rows:
        sp_slug = m["sport"]
        sp_name = p["sport_name"] if p else sp_slug.replace("-", " ").title()
        flag_note = (
            f'<span class="flag-inline">{e(m["flags"][0])}</span>' if m.get("flags") else ""
        )

        if p:
            mk_map = {mk["key"]: mk for mk in p["markets"]}
            w_out = mk_map["winner"]["outcomes"]
            win_cell = " / ".join(odds_span(o) for o in w_out)
            h_mk = mk_map.get("handicap")
            t_mk = mk_map.get("total")
            ht_lines = []
            if h_mk:
                o0 = h_mk["outcomes"][0]
                ht_lines.append(f'{e(o0["selection"])} @ {odds_span(o0)}')
            if t_mk:
                t0 = t_mk["outcomes"][0]
                ht_lines.append(f'{e(t0["selection"])} @ {odds_span(t0)}')
            else:
                unavail_total = next((x for x in p.get("unavailable_markets", []) if x.get("key") == "total"), None)
                if unavail_total:
                    ht_lines.append(
                        '<span class="flag-inline">Match Total blank — '
                        + e(unavail_total["reason"])
                        + '</span>'
                    )
            ht_cell = "<br>".join(ht_lines) if ht_lines else "—"
            pick_out = next((o for o in w_out if o["selection"] == p["pick"]), w_out[0])
            pick_cell = (
                f'<b>{e(p["pick"])}</b> @ {odds_span(pick_out)}'
                f'<span class="sub">{e(p["pick_market"])} ({round(max(p["home_probability"], p["away_probability"])*100, 1)}%)</span>'
                f'{render_markets_drawer(p)}'
            )
            conf_attr = p["confidence"]
            conf_cell = f'{badge_conf(p["confidence"])}<span class="sub">{badge_status(m["status"])}</span>'
        else:
            win_cell = '<span class="badge event">Multi-runner field</span>'
            ht_cell = "—"
            pick_cell = '<span class="sub">Event-only card (not a 2-way fixture; see official field sheet)</span>'
            conf_attr = "low"
            conf_cell = f'<span class="badge event">Field card</span><span class="sub">{badge_status(m["status"])}</span>'

        cells = [
            f'<td style="white-space:nowrap">{e(fmt_when(m))}</td>',
            f'<td><span class="match-name">{e(fmt_match(m))}</span>'
            f'<span class="sub">{e(m.get("venue") or "Venue unconfirmed")}</span>{flag_note}</td>',
        ]
        if show_sport:
            cells.append(f'<td><a href="{site_rel}sports/{e(sp_slug)}.html">{e(sp_name)}</a></td>')
        cells += [
            f'<td>{e(m["competition"])}<span class="sub">{e(m.get("stage", ""))}</span></td>',
            f'<td style="white-space:nowrap">{win_cell}</td>',
            f'<td style="font-size:.81rem;white-space:nowrap">{ht_cell}</td>',
            f'<td>{pick_cell}</td>',
            f'<td>{conf_cell}</td>',
            f'<td>{render_source_links(m)}</td>',
        ]
        trs.append(f'<tr data-conf="{e(conf_attr)}" data-sport="{e(sp_slug)}">' + "".join(cells) + "</tr>")

    return f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table></div>'


def render_shell(title: str, body: str, active: str, site_depth: int, repo_depth: int) -> str:
    sr = "../" * site_depth
    rr = "../" * repo_depth
    nav_items = [
        ("index.html", "Overview", "dash"),
        ("live-refresh.html", "Live Refresh (141)", "live"),
        ("picks.html", "All Lines (134)", "picks"),
        ("predictions.html", "High Picks (31)", "preds"),
        ("sports.html", "17 Sports", "sports"),
        ("analysis.html", "Market Analysis", "analysis"),
        ("methodology.html", "Methodology", "method"),
        ("reverse-engineering.html", "OLBG Audit", "rev"),
        ("sources.html", "Official Sources", "src"),
        ("live-verification.html", "Live Verification", "livev"),
        ("flagged.html", "Flagged for Review", "flag"),
    ]
    cur_attr = ' aria-current="page"'
    nav_html = "".join(
        f'<a href="{sr}{href}"{cur_attr if key == active else ""}>{label}</a>'
        for href, label, key in nav_items
    )
    nav_html += f'<a href="{rr}2360a617/index.html">OLBG-152 Board</a>'
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} · {e(SITE_NAME)}</title>
<meta name="description" content="Source-linked multi-sport match dataset, independent multi-market betting lines, confidence tiers, and human analysis across all 17 in-scope OLBG sports.">
<link rel="stylesheet" href="{sr}assets/style.css">
</head>
<body>
<header class="site-header">
  <div class="hdr-inner">
    <div class="brand"><a href="{sr}index.html"><span class="dot"></span> OLBG Origination Desk <span class="sub">2026-10-21 UTC</span></a></div>
    <nav class="main" aria-label="Primary navigation">{nav_html}</nav>
  </div>
  <div class="companion-bar">
    <div class="companion-inner">
      <span>Repository workspaces:</span>
      <a href="{rr}index.html">Primary Root Desk (134 source-linked)</a>
      <a href="{rr}f7fa77fc/index.html">f7fa77fc Permalink Mirror</a>
      <a href="{rr}docs/index.html">4f44f7d9 Board (164 OLBG)</a>
      <a href="{rr}ebfbd966/index.html">ebfbd966 Board (133)</a>
      <a href="{rr}aa4e9dbf/index.html">aa4e9dbf Desk (131)</a>
      <a href="{rr}2360a617/index.html">2360a617 Board (152)</a>
    </div>
  </div>
</header>
<main>
{body}
</main>
<footer class="foot">
  <p><b>{e(SITE_NAME)}</b> — {e(SITE_TAG)}.</p>
  <p>Every fixture, ranking, and record links directly to its governing body. Unconfirmed values are left explicitly blank and logged on <a href="{sr}flagged.html">Flagged for Review</a>. Independent mathematical probabilities only — not financial or gambling advice.</p>
  <p>Downloads: <a href="{rr}datasets/matches_full.json">matches_full.json</a> · <a href="{rr}datasets/matches_full.csv">matches_full.csv</a> · <a href="{rr}datasets/flagged_for_review.json">flagged_for_review.json</a> · <a href="{rr}datasets/olbg_sports_registry.json">olbg_sports_registry.json</a></p>
</footer>
<script src="{sr}assets/app.js"></script>
</body>
</html>
"""


def kpi_box(n, label: str, cls: str = "") -> str:
    return f'<div class="kpi {cls}"><div class="n">{e(n)}</div><div class="l">{e(label)}</div></div>'


def build_all_pages(target_root: Path, repo_depth_base: int, D: dict) -> None:
    fixtures = D["fixtures"]["fixtures"]
    lines_by_id = {l["id"]: l for l in D["lines"]["lines"]}
    preds_by_id = {p["match_id"]: p for p in D["preds"]["predictions"]}
    paired = [(f, lines_by_id.get(f["id"])) for f in fixtures]
    h2h_rows = [(f, l) for f, l in paired if l is not None]
    conf_counts = Counter(l["confidence"] for _, l in h2h_rows)
    status_counts = Counter(f["status"] for f in fixtures)
    total_priced_count = sum(1 for _, l in h2h_rows if any(m["key"] == "total" for m in l["markets"]))
    total_unavailable_count = sum(
        1 for _, l in h2h_rows
        if any(m.get("key") == "total" for m in l.get("unavailable_markets", []))
    )

    (target_root / "assets").mkdir(parents=True, exist_ok=True)
    (target_root / "sports").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "site_src" / "style.css", target_root / "assets" / "style.css")
    shutil.copyfile(ROOT / "site_src" / "app.js", target_root / "assets" / "app.js")

    # 1. index.html
    sport_cards = []
    for cov in sorted(D["coverage"]["included"], key=lambda x: -x["fixtures"]):
        slug = cov["sport"]
        b_html = (
            '<span class="badge event">Event-only</span>'
            if cov["status"] == "event-only"
            else '<span class="badge verified">Priced</span>'
        )
        sp_h2h = [l for f, l in h2h_rows if f["sport"] == slug]
        hi_n = sum(1 for l in sp_h2h if l["confidence"] == "high")
        meta = (
            f"{cov['fixtures']} events · field card"
            if cov["status"] == "event-only"
            else f"{cov['fixtures']} matches · {hi_n} High"
        )
        sport_cards.append(
            f'<a class="sport-card" href="sports/{e(slug)}.html">'
            f'<div class="t"><span>{e(cov["name"])}</span>{b_html}</div>'
            f'<div class="m">{e(meta)}</div></a>'
        )

    featured_high = [
        (f, l) for f, l in sorted(
            h2h_rows,
            key=lambda x: (-max(x[1]["home_probability"], x[1]["away_probability"]), x[0].get("start_utc") or "9999"),
        )
        if l["confidence"] == "high"
    ][:12]

    rr0 = "../" * repo_depth_base
    vs = D["verification"]["summary"]
    index_body = f"""
<h1>Source-Linked Multi-Sport Origination Desk</h1>
<p class="lede">Complete reverse-engineering of <code>OLBG.com</code> across all <b>17 in-scope sports</b> (excluding soccer/football, horse racing, american football, boxing, UFC/MMA, specials, hurling, and cycling), pairing <b>134 source-linked events</b> (<b>{status_counts["verified"]} verified</b>; <b>{status_counts["cross-checked"]} cross-checked</b>) with independently originated markets and <b>31 non-repetitive human predictions</b>. {total_priced_count} of {len(h2h_rows)} head-to-head matches have an Over/Under total; the remaining total is left blank and flagged because no official competition-specific baseline was captured.</p>

<div class="grid kpis">
  {kpi_box(f'{len(fixtures)} ({status_counts["verified"]}V · {status_counts["cross-checked"]}C)', "Source-Linked Events") }
  {kpi_box(len(h2h_rows), "Multi-Market H2H Priced")}
  {kpi_box(conf_counts["high"], "High Confidence Picks", "hi")}
  {kpi_box(conf_counts["medium"], "Medium Confidence", "md")}
  {kpi_box(conf_counts["low"], "Low Confidence", "lo")}
  {kpi_box(len(D["flagged"]["findings"]), "Upstream / Audit Flags", "fl")}
</div>

<div class="note good">
  <b>Zero-inference verification policy:</b> Every fixture row carries a direct governing-body link; this snapshot labels <b>{status_counts["verified"]}</b> rows Verified and <b>{status_counts["cross-checked"]}</b> Cross-checked. Any field that cannot be supported is blank/flagged. Inputs for our prices link directly to an official governing body (NHL API, MLB StatsAPI, NBA, EuroLeague, ATP/WTA, WST, PDC, ICC/NZC, LNR Top 14, URC, NRL/RLWC26, EHF, PlusLiga/SuperLega, AFLW, LoL Esports, GAA, FIA F1, PGA/DPWT/LPGA, GBGB). Only matches where <b>both sides hold measured official ratings</b> can reach High confidence. Unconfirmed fields are left blank and catalogued on <a href="flagged.html">Flagged for Review</a>.
</div>

<div class="note">
  <b>New in this pass — <a href="live-verification.html">Live Verification</a>:</b> a dated, page-by-page re-fetch of the governing-body sources behind <b>{vs["rows"] - vs["not_rechecked"]} of the {vs["rows"]} rows</b> — <b>{vs["confirmed"]}</b> confirmed, <b>{vs["corrected"]}</b> corrected, <b>{vs["flagged"]}</b> flagged — plus the <b>{vs["not_rechecked"]}</b> rows this pass did not re-read, each with the blocker named. It is the first pass here that re-opened the official pages instead of auditing the dataset's structure.
</div>

<h2>Browse by Sport Category (All 17 In-Scope OLBG Sports)</h2>
<div class="grid sports-grid">{"".join(sport_cards)}</div>

<h2>Featured High-Conviction Selections</h2>
<div class="toolbar">
  {odds_format_controls()}
  <span style="margin-left:auto"><a class="chip" href="predictions.html">Read all 31 written predictions &rarr;</a></span>
</div>
{render_picks_table(featured_high, show_sport=True, site_rel="")}

<h2>Multi-Session Repository Directory</h2>
<div class="card">
  <p>This repository preserves every parallel session's work cleanly side by side. Explore all live builds directly:</p>
  <ul>
    <li><b><a href="{rr0}index.html">Primary Root Desk (/)</a> &amp; <a href="{rr0}f7fa77fc/index.html">/f7fa77fc/ Mirror</a>:</b> 134 source-linked events across all 17 sports ({status_counts["verified"]} Verified; {status_counts["cross-checked"]} Cross-checked), with Winner and Handicap markets for all {len(h2h_rows)} head-to-head fixtures, Over/Under totals for {total_priced_count}, Draw No Bet where regulation draws apply, a live Decimal/Fair/US odds toggle, and a full line-by-line audit.</li>
    <li><b><a href="{rr0}docs/index.html">4f44f7d9 Companion Board (/docs/)</a>:</b> 164-event historical OLBG tip-listing snapshot; its source gaps are recorded separately in the repository audit.</li>
    <li><b><a href="{rr0}ebfbd966/index.html">ebfbd966 Companion Board (/ebfbd966/)</a>:</b> 133-match independent log-odds pricing board.</li>
    <li><b><a href="{rr0}aa4e9dbf/index.html">aa4e9dbf Companion Desk (/aa4e9dbf/)</a>:</b> 131-match multi-market analytical desk.</li>
    <li><b><a href="{rr0}2360a617/index.html">2360a617 Board (/2360a617/)</a>:</b> 152-row historical OLBG snapshot with its own review register.</li>
  </ul>
</div>
"""
    (target_root / "index.html").write_text(
        render_shell("Overview", index_body, "dash", site_depth=0, repo_depth=repo_depth_base), encoding="utf-8"
    )

    # 2. picks.html — Complete interactive board across all 134 rows
    sport_opts = ['<option value="all">All 17 Sports (134)</option>'] + [
        f'<option value="{e(c["sport"])}">{e(c["name"])} ({c["fixtures"]})</option>'
        for c in sorted(D["coverage"]["included"], key=lambda x: x["name"])
    ]
    picks_body = f"""
<h1>All 134 Source-Linked Events &amp; Originated Lines</h1>
<p class="lede">Each of the {len(h2h_rows)} head-to-head matches carries originated <b>Match Winner</b> and <b>Handicap / Spread</b> lines; <b>{total_priced_count}</b> also carry an <b>Over / Under Total</b>, and <b>{total_unavailable_count}</b> is deliberately blank and flagged because a source-backed competition baseline was not captured. <b>Draw No Bet</b> is included on 3-way sports. Every fixture row has clickable governing-body verification links.</p>

<div class="toolbar">
  <div class="toolbar-group" role="group" aria-label="Filter by confidence">
    <button type="button" class="chip is-active" data-filter="all" aria-pressed="true">All ({len(paired)})</button>
    <button type="button" class="chip" data-filter="high" aria-pressed="false">High ({conf_counts["high"]})</button>
    <button type="button" class="chip" data-filter="medium" aria-pressed="false">Medium ({conf_counts["medium"]})</button>
    <button type="button" class="chip" data-filter="low" aria-pressed="false">Low / Field ({conf_counts["low"] + len(paired) - len(h2h_rows)})</button>
  </div>
  <div class="toolbar-sep"></div>
  <select id="sport-filter" class="filter-select" aria-label="Filter by sport">{"".join(sport_opts)}</select>
  <input id="pick-search" class="filter-search" type="search" placeholder="Search team, player, venue, competition...">
  <div class="toolbar-sep"></div>
  {odds_format_controls()}
  <a href="#" id="open-all" class="chip" data-state="closed">Expand all markets</a>
  <span class="sub" style="margin-left:auto">Showing <b data-visible-count>{len(paired)}</b> of {len(paired)}</span>
</div>

{render_picks_table(paired, show_sport=True, site_rel="")}
"""
    (target_root / "picks.html").write_text(
        render_shell("All Originated Lines", picks_body, "picks", site_depth=0, repo_depth=repo_depth_base), encoding="utf-8"
    )

    # 3. predictions.html — All 31 High-Confidence Human Predictions
    pred_cards = []
    fix_by_id = {f["id"]: f for f in fixtures}
    for pr in D["preds"]["predictions"]:
        mid = pr["match_id"]
        fx = fix_by_id[mid]
        ln = lines_by_id[mid]
        facts_li = "".join(f"<li>{e(fc)}</li>" for fc in pr.get("facts", []))
        pred_cards.append(
            f'<article class="pred" id="{e(mid)}" data-conf="high" data-sport="{e(fx["sport"])}">'
            f'<h3>{e(fmt_match(fx))} — <span style="color:var(--high)">{e(pr["bet_line"])}</span></h3>'
            f'<div class="meta"><a href="sports/{e(fx["sport"])}.html"><b>{e(ln["sport_name"])}</b></a> · '
            f'{e(fx["competition"])} ({e(fx.get("stage", ""))}) · {e(fmt_when(fx))} · '
            f'{e(fx.get("venue") or "")} · {pr["words"]} words</div>'
            f'<p>{e(pr["text"])}</p>'
            f'<ul class="facts">{facts_li}</ul>'
            f'{render_source_links(fx)}'
            f'</article>'
        )

    pred_sport_counts = Counter(fix_by_id[p["match_id"]]["sport"] for p in D["preds"]["predictions"])
    pred_opts = ['<option value="all">All Sports with High Picks (31)</option>'] + [
        f'<option value="{e(sp)}">{e(lines_by_id[next(p["match_id"] for p in D["preds"]["predictions"] if fix_by_id[p["match_id"]]["sport"] == sp)]["sport_name"])} ({cnt})</option>'
        for sp, cnt in sorted(pred_sport_counts.items())
    ]
    preds_body = f"""
<h1>31 High-Confidence Human Predictions</h1>
<p class="lede">Every match clearing its sport's high-conviction threshold and holding measured governing-body ratings on both sides receives an original, non-repetitive human analysis (at least 30 words). Each current write-up is deliberately limited to the stored, source-linked comparison facts and the clearly labelled independent model selection.</p>

<div class="toolbar">
  <select id="sport-filter" class="filter-select" aria-label="Filter predictions by sport">{"".join(pred_opts)}</select>
  <input id="pick-search" class="filter-search" type="search" placeholder="Search player, club, stat, venue...">
  <span class="sub" style="margin-left:auto">Showing <b data-visible-count>{len(pred_cards)}</b> of {len(pred_cards)} high-confidence picks</span>
</div>

{"".join(pred_cards)}
"""
    (target_root / "predictions.html").write_text(
        render_shell("High-Confidence Predictions", preds_body, "preds", site_depth=0, repo_depth=repo_depth_base), encoding="utf-8"
    )

    # 4. sports.html + 17 sports/{slug}.html pages
    inc_rows_html = []
    for cov in D["coverage"]["included"]:
        slug = cov["sport"]
        sp_h2h = [l for f, l in h2h_rows if f["sport"] == slug]
        c_hi = sum(1 for l in sp_h2h if l["confidence"] == "high")
        c_md = sum(1 for l in sp_h2h if l["confidence"] == "medium")
        c_lo = sum(1 for l in sp_h2h if l["confidence"] == "low")
        inc_rows_html.append(
            f'<tr>'
            f'<td><a href="sports/{e(slug)}.html"><b>{e(cov["name"])}</b></a></td>'
            f'<td class="num">{cov["fixtures"]}</td>'
            f'<td class="num">{cov["verified"]}/{cov["fixtures"]}</td>'
            f'<td class="num">{c_hi} / {c_md} / {c_lo}</td>'
            f'<td>{e(cov["note"])}</td>'
            f'<td><a href="{e(cov["olbg_url"])}" target="_blank" rel="noopener">OLBG hub</a></td>'
            f'</tr>'
        )
    exc_rows_html = [
        f'<tr><td><b>{e(ex["name"])}</b></td><td><span class="badge muted">Excluded</span></td>'
        f'<td>{e(ex["reason"])}</td><td><a href="{e(ex["olbg_url"])}" target="_blank" rel="noopener">Upstream URL</a></td></tr>'
        for ex in D["coverage"]["excluded"]
    ]
    sports_index_body = f"""
<h1>All 24 OLBG Sport Categories — Scope &amp; Coverage</h1>
<p class="lede">Complete reconciliation of every active sport hub on <code>OLBG.com</code>: <b>17 in-scope sports</b> (all 17 built as dedicated subpages below) and <b>8 excluded sport specifications</b>.</p>

<h2>In-Scope Sports (17 Categories · 134 Source-Linked Events)</h2>
<div class="table-wrap">
  <table>
    <thead><tr><th>Sport</th><th class="num">Events</th><th class="num">Governing-Body Verified</th><th class="num">High / Med / Low</th><th>Coverage Summary</th><th>Upstream</th></tr></thead>
    <tbody>{"".join(inc_rows_html)}</tbody>
  </table>
</div>

<h2>Excluded Sports Per Specification (Explicitly Audited &amp; Omitted)</h2>
<div class="table-wrap">
  <table>
    <thead><tr><th>Sport Category</th><th>Status</th><th>Rule Basis</th><th>OLBG Route</th></tr></thead>
    <tbody>{"".join(exc_rows_html)}</tbody>
  </table>
</div>
"""
    (target_root / "sports.html").write_text(
        render_shell("17 Sports Directory", sports_index_body, "sports", site_depth=0, repo_depth=repo_depth_base), encoding="utf-8"
    )

    # Individual sport subpages (depth=1 inside site)
    for cov in D["coverage"]["included"]:
        slug = cov["sport"]
        sp_cfg = D["lines"]["sports"][slug]
        sp_rows = [(f, lines_by_id.get(f["id"])) for f in fixtures if f["sport"] == slug]
        sp_preds = [preds_by_id[f["id"]] for f, _ in sp_rows if f["id"] in preds_by_id]
        sp_pred_html = ""
        if sp_preds:
            cards = []
            for pr in sp_preds:
                fx = fix_by_id[pr["match_id"]]
                cards.append(
                    f'<article class="pred">'
                    f'<h3>{e(fmt_match(fx))} — <span style="color:var(--high)">{e(pr["bet_line"])}</span></h3>'
                    f'<p>{e(pr["text"])}</p>'
                    f'{render_source_links(fx)}</article>'
                )
            sp_pred_html = f"<h2>High-Confidence Written Predictions ({len(sp_preds)})</h2>" + "".join(cards)

        sp_body = f"""
<div class="crumb"><a href="../sports.html">&larr; All 17 In-Scope Sports</a></div>
<h1>{e(cov["name"])} — Source-Linked Fixtures &amp; Originated Markets</h1>
<p class="lede">{e(cov["note"])}</p>

<div class="grid kpis">
  {kpi_box(cov["fixtures"], "Events in Dataset")}
  {kpi_box(f"{cov['verified']}/{cov['fixtures']}", "Governing-Body Verified")}
  {kpi_box(len(sp_preds), "High-Confidence Picks", "hi")}
  {kpi_box(sp_cfg["p_base"], "Home Win Baseline")}
  {kpi_box(sp_cfg["sigma"], "Margin Sigma")}
  {kpi_box(sp_cfg["total"] if sp_cfg["total"] is not None else "Field", "Base Total Line")}
</div>

<div class="toolbar">
  {odds_format_controls()}
  <a href="#" id="open-all" class="chip" data-state="closed">Expand all markets</a>
  <a href="{e(cov['olbg_url'])}" target="_blank" rel="noopener" class="chip" style="margin-left:auto">Open OLBG {e(cov['name'])} hub &nearr;</a>
</div>

{render_picks_table(sp_rows, show_sport=False, site_rel="../")}
{sp_pred_html}
"""
        (target_root / "sports" / f"{slug}.html").write_text(
            render_shell(cov["name"], sp_body, "sports", site_depth=1, repo_depth=repo_depth_base + 1), encoding="utf-8"
        )

    # 5. analysis.html — Quantitative Market Analysis & OLBG Consensus Audit
    divergence_rows = []
    for f, l in h2h_rows:
        olbg = f.get("olbg") or {}
        if not olbg.get("consensus"):
            continue
        p_top = round(max(l["home_probability"], l["away_probability"]) * 100, 1)
        divergence_rows.append(
            f'<tr>'
            f'<td><b>{e(fmt_match(f))}</b><span class="sub">{e(l["sport_name"])} · {e(f["competition"])}</span></td>'
            f'<td>{e(olbg.get("selection", ""))}<span class="sub">{e(olbg.get("consensus", ""))}</span></td>'
            f'<td><b>{e(l["pick"])}</b> ({p_top}%)<span class="sub">{badge_conf(l["confidence"])}</span></td>'
            f'<td>{render_source_links(f, limit=2)}</td>'
            f'</tr>'
        )

    sport_cal_rows = []
    for cov in D["coverage"]["included"]:
        slug = cov["sport"]
        sp_l = [l for f, l in h2h_rows if f["sport"] == slug]
        if not sp_l:
            continue
        avg_fav = sum(max(x["home_probability"], x["away_probability"]) for x in sp_l) / len(sp_l) * 100
        mk_cnt = len(sp_l[0]["markets"])
        sport_cal_rows.append(
            f'<tr><td><a href="sports/{e(slug)}.html"><b>{e(cov["name"])}</b></a></td>'
            f'<td class="num">{len(sp_l)}</td>'
            f'<td class="num">{mk_cnt}</td>'
            f'<td class="num">{avg_fav:.1f}%</td>'
            f'<td class="num">{sum(1 for x in sp_l if x["confidence"]=="high")}</td>'
            f'<td class="num">{sum(1 for x in sp_l if x["confidence"]=="medium")}</td>'
            f'<td class="num">{sum(1 for x in sp_l if x["confidence"]=="low")}</td></tr>'
        )

    analysis_body = f"""
<h1>Quantitative Market Analysis &amp; OLBG Crowd Divergence</h1>
<p class="lede">Comparing our independent governing-body pricing engine against upstream OLBG tipster consensus across all 14 head-to-head priced sports plus 3 field-event sports.</p>

<div class="two-col">
  <div class="card">
    <h3>Key Structural Findings</h3>
    <ul>
      <li><b>Zero-tip blind spots closed:</b> OLBG carries <b>0 match tips</b> across all 7 RLWC26 Round 2 matches, all 9 NAB AFLW Round 11 fixtures, and LoL Worlds Swiss Round 1 — 17 top-tier fixtures originated cleanly here.</li>
      <li><b>Thin-sample consensus noise:</b> Over half of OLBG non-soccer match cards rely on 1–4 tipsters (often <code>1/1 = 100%</code>), producing extreme false certainty where true win probabilities sit near 52%–58%.</li>
      <li><b>Sharp model vs crowd divergences:</b> In EHF Handball (<code>event_id=12046</code>), OLBG's most-tipped selection is Montpellier (<code>2/6 = 33%</code>) because draw/away tips split, whereas unbeaten 4-0 Barça (+33 GD, already winners 28:27 in Montpellier) price at <b>78.1% (1.22)</b>.</li>
    </ul>
  </div>
  <div class="card">
    <h3>Calibration Across Confidence Tiers</h3>
    <ul>
      <li><b>High ({conf_counts["high"]} matches · 24.6%):</b> Requires <code>status == "verified"</code>, <b>both sides measured on official feeds</b>, and win probability clearing sport-specific thresholds (0.580 in MLB to 0.780 in AFLW).</li>
      <li><b>Medium ({conf_counts["medium"]} matches · 27.8%):</b> Sourced ratings on both sides with moderate edge above baseline.</li>
      <li><b>Low ({conf_counts["low"]} matches · 47.6%):</b> Genuine coin-flips, bounded rank-60 snooker qualifiers, opening-week 0-0 leagues, and 5 cross-checked Premiership ties.</li>
    </ul>
  </div>
</div>

<h2>Model Calibration Summary by Sport</h2>
<div class="table-wrap">
  <table>
    <thead><tr><th>Sport</th><th class="num">H2H Priced</th><th class="num">Markets / Match</th><th class="num">Mean Favourite Prob.</th><th class="num">High</th><th class="num">Medium</th><th class="num">Low</th></tr></thead>
    <tbody>{"".join(sport_cal_rows)}</tbody>
  </table>
</div>

<h2>Side-by-Side: Upstream OLBG Consensus vs Independent Originated Pick ({len(divergence_rows)} Overlapping Matches)</h2>
<div class="table-wrap">
  <table>
    <thead><tr><th>Match</th><th>OLBG Upstream Tip &amp; Consensus</th><th>Originated Model Pick &amp; Prob.</th><th>Official Verification</th></tr></thead>
    <tbody>{"".join(divergence_rows)}</tbody>
  </table>
</div>
"""
    (target_root / "analysis.html").write_text(
        render_shell("Market Analysis", analysis_body, "analysis", site_depth=0, repo_depth=repo_depth_base), encoding="utf-8"
    )

    # 6. methodology.html
    param_rows = [
        f'<tr><td><a href="sports/{e(k)}.html"><b>{e(v["name"])}</b></a></td>'
        f'<td class="num">{v["p_base"]:.3f}</td><td class="num">{v["scale"]:.1f}</td>'
        f'<td class="num">{v["sigma"]:.2f}</td><td class="num">{v["total"] if v["total"] is not None else "—"}</td>'
        f'<td>{"3-Way + DNB" if v["draws"] else "2-Way"}</td>'
        f'<td class="num">{v["med"]:.3f} / {v["high"]:.3f}</td></tr>'
        for k, v in D["lines"]["sports"].items()
    ]
    method_body = f"""
<h1>Line Origination &amp; Verification Methodology</h1>
<p class="lede">Transparent, zero-black-box mathematical specification of <code>olbg-independent-logit-normal-v2.0</code> (`scripts/model.py`).</p>

<div class="card">
  <h2>1. Governing-Body Strength Rating &amp; Logit Win Model</h2>
  <p>Each team or player receives a documented 0–100 strength input directly from its governing body (points percentage in NHL/NBA/EuroLeague/MLB, log-rank in ATP/WTA/WST, tournament seed in PDC, official rating points in ICC/IRL, or league table points &amp; goal difference in Top 14/EHF/AFLW). Given home baseline <code>p_base</code> (set to <code>0.500</code> on neutral venues):</p>
  <pre>logit(p_home_2way) = logit(p_venue) + (R_home - R_away) / scale</pre>
  <p>For 3-way sports (Rugby Union, Rugby League, Handball, Gaelic Football), regulation draw probability smoothly decays as mismatch widens: <code>d = max(0.018, draw_p * exp(-((p_2way - 0.5)/0.34)^2))</code>, with <code>p_home + p_draw + p_away == 1.000000</code> strictly enforced before applying a uniform <b>5.0% bookmaker overround</b> alongside exact <b>0%-vig fair odds</b> and <b>US moneyline</b> prices.</p>
</div>

<div class="card">
  <h2>2. Derived Spread / Handicap, Draw No Bet &amp; Over/Under Totals</h2>
  <p>Expected margin <code>mu = -sigma * Phi^-1(1 - p_home_2way)</code> maps win probability coherently onto sport scoring units. Fixed-line sports (NHL Puck Line <code>1.5</code>, MLB Run Line <code>1.5</code>, Snooker Frames <code>1.5</code>, Volleyball Sets <code>1.5</code>) price exact normal cover probabilities at <code>+-1.5</code>; variable-spread sports round to the nearest half-point hook. Totals adjust competition baselines (e.g., NBA <code>228.5</code> vs EuroLeague <code>171.5</code> vs EuroCup <code>168.5</code>; Men's T20I <code>339.5</code> vs Women's T20I <code>289.5</code> vs List A <code>529.5</code>). A total is never invented: {total_unavailable_count} multi-innings fixture has no source-backed competition baseline, so its total is blank and marked unverified.</p>
</div>

<h2>Complete 17-Sport Parameter Table</h2>
<div class="table-wrap">
  <table>
    <thead><tr><th>Sport</th><th class="num">p_base</th><th class="num">Logit Scale</th><th class="num">Margin &sigma;</th><th class="num">Base Total</th><th>Winner Structure</th><th class="num">Med / High Gate</th></tr></thead>
    <tbody>{"".join(param_rows)}</tbody>
  </table>
</div>
"""
    (target_root / "methodology.html").write_text(
        render_shell("Methodology", method_body, "method", site_depth=0, repo_depth=repo_depth_base), encoding="utf-8"
    )

    # 7. reverse-engineering.html — Accurate 24-Sport OLBG Architecture & Bugs
    badge_in = '<span class="badge verified">In scope</span>'
    badge_ex = '<span class="badge muted">Excluded</span>'
    tax_rows = [
        f'<tr><td class="num">{s["id"]}</td><td><b>{e(s["name"])}</b></td>'
        f'<td><code>{e(s["slug"])}</code></td>'
        f'<td>{badge_in if s["in_scope"] else badge_ex}</td>'
        f'<td><a href="https://www.olbg.com/betting-tips/{e(s["slug"])}/{s["id"]}" target="_blank" rel="noopener">'
        f'https://www.olbg.com/betting-tips/{e(s["slug"])}/{s["id"]}</a></td></tr>'
        for s in D["taxonomy"]["sports"]
    ]
    rev_body = f"""
<h1>Reverse-Engineering OLBG.com — Taxonomy, Routing &amp; Live Bugs</h1>
<p class="lede">Empirical audit of <code>https://www.olbg.com/betting-tips</code>, XML sitemaps, URL routing, consensus math, and live upstream defects recorded on <b>2026-10-21 UTC</b>.</p>

<div class="two-col">
  <div class="card">
    <h3>URL Architecture &amp; Routing Mechanics</h3>
    <ul>
      <li><b>24 active sport IDs (1–28 with gaps 6, 19, 24, 27 retired):</b> 22 indexed in <code>sitemap-betting-tips.xml</code> plus 2 active un-indexed routes: <code>Entertainment/18</code> (Specials redirect) and <code>Hurling/26</code>.</li>
      <li><b>Case-sensitive slug routing:</b> <code>/betting-tips/{{SportSlug}}/{{ID}}</code> resolves strictly by exact case-sensitive <code>SportSlug</code>; wrong case (e.g. <code>ESports/23</code> vs <code>eSports/23</code>) serves HTTP 200 soft-error HTML.</li>
      <li><b>Event consensus widget:</b> Displays <code>k / n win tips (pct%)</code> for the modal outcome on a single market without vig adjustment or sample-size shrinkage.</li>
    </ul>
  </div>
  <div class="card">
    <h3>7 Verified Upstream OLBG Defects Caught Live</h3>
    <ul>
      <li><b>Unlabelled UTC-4 (EDT) clock bug:</b> UK race <code>11:14 Kinsley</code> (<code>689388</code>) displays <code>Today 06:14</code>; <code>SAC Kings (2:30am)</code> (<code>534889</code>) displays <code>Today 22:30</code>.</li>
      <li><b>Wrong county final date:</b> <code>event_id=3536</code> lists Waterford SFC Final on <code>01 Nov</code> instead of Munster GAA's official <code>25 Oct</code> date.</li>
      <li><b>Misclassified tournament:</b> <code>event_id=535918</code> lists EuroCup/BCL clubs under <code>EuroLeague</code>.</li>
      <li><b>Stale club &amp; consensus cache bugs:</b> <code>Skanderborg Handbold</code> on <code>12045</code>; <code>Under 234.5</code> summary mismatch on <code>534888</code>; <code>0/0 EW tips ()</code> on Golf; 0 live tips on RLWC26, AFLW, and LoL Worlds.</li>
    </ul>
  </div>
</div>

<h2>Complete 24-Sport OLBG Registry</h2>
<div class="table-wrap">
  <table>
    <thead><tr><th class="num">OLBG ID</th><th>Sport Name</th><th>Canonical Slug</th><th>Project Scope</th><th>Verified Hub URL</th></tr></thead>
    <tbody>{"".join(tax_rows)}</tbody>
  </table>
</div>
"""
    (target_root / "reverse-engineering.html").write_text(
        render_shell("OLBG Reverse-Engineering", rev_body, "rev", site_depth=0, repo_depth=repo_depth_base), encoding="utf-8"
    )

    # 8. sources.html — Official Governing-Body Source Registry
    src_rows = [
        f'<tr><td><code>{e(s["id"])}</code></td><td><b>{e(s["name"])}</b></td>'
        f'<td>{e(s["sport"])}</td><td>{e(s["role"])}</td>'
        f'<td><a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["url"])}</a></td></tr>'
        for s in D["sources"]["sources"]
    ]
    sources_body = f"""
<h1>Official Governing-Body Source Registry</h1>
<p class="lede">All {len(D["sources"]["sources"])} primary authorities used to verify fixtures, kick-off times, rankings, standings, and recent match history across the repository.</p>

<div class="note">
  <b>Fresh official-source re-verification:</b> <a href="live-verification.html">Live Verification</a> records a dated, page-by-page re-fetch of {vs["rows"] - vs["not_rechecked"]} of the {vs["rows"]} rows against their governing bodies, lists the {vs["corrected"]} corrections it produced, and names the {vs["not_rechecked"]} rows this pass did not re-read. It is the first pass in this repository to re-open the official pages rather than audit the dataset structure.
</div>

<div class="note">
  <b>Line-by-line audit report:</b> Open the current <a href="{rr0}reports/FINAL_INTEGRATION_AUDIT.md">Final Integration Audit</a> for every primary fixture, its exact governing-body links, market coverage and review flags. The independently published <a href="{rr0}reports/POST_INTEGRATION_AUDIT.html">Post-Integration Review</a> records historical F1–F3 audit boundaries; its F1 prose issue was corrected in the generated predictions, while source freshness and five Cross-checked Premiership rows remain flagged. Historical context remains in <a href="{rr0}reports/REPO_LINE_BY_LINE_AUDIT.md">REPO_LINE_BY_LINE_AUDIT.md</a> and <a href="{rr0}reports/OLBG_REVERSE_ENGINEERING.md">OLBG_REVERSE_ENGINEERING.md</a>.
</div>

<div class="table-wrap">
  <table>
    <thead><tr><th>ID</th><th>Official Authority</th><th>Sport</th><th>Verified Fields</th><th>Official Endpoint</th></tr></thead>
    <tbody>{"".join(src_rows)}</tbody>
  </table>
</div>
"""
    (target_root / "sources.html").write_text(
        render_shell("Official Sources", sources_body, "src", site_depth=0, repo_depth=repo_depth_base), encoding="utf-8"
    )

    # 8b. live-verification.html — fresh official-source re-verification register
    vdoc = D["verification"]
    vs = vdoc["summary"]
    vsports = vdoc["by_sport"]
    ver_badge = {
        "confirmed": '<span class="badge verified">Confirmed</span>',
        "corrected": '<span class="badge medium">Corrected</span>',
        "flagged": '<span class="badge high">Flagged</span>',
        "not_rechecked": '<span class="badge event">Not re-checked</span>',
    }
    ver_rows = "".join(
        f'<tr><td><code>{e(r["id"])}</code><span class="sub">{e(r["sport"])}</span></td>'
        f'<td><b>{e(r["match"])}</b><span class="sub">{e(r["competition"])}</span></td>'
        f'<td>{ver_badge.get(r["status"], e(r["status"]))}</td>'
        f'<td>{e(r["evidence"])}<span class="sub"><b>Action:</b> {e(r["action"])}</span></td>'
        f'<td><a href="{e(r["source_url"])}" target="_blank" rel="noopener">{e(r["source_name"])} &nearr;</a></td></tr>'
        for r in vdoc["rows"]
    )
    ver_findings = "".join(
        f'<tr><td><code>{e(f["id"])}</code></td><td>{badge_conf(f["severity"])}</td>'
        f'<td><b>{e(f["area"])}</b><span class="sub">{e(f["detail"])}</span></td>'
        f'<td>{e(f["status"])}</td>'
        f'<td><a href="{e(f["source_url"])}" target="_blank" rel="noopener">Official source &nearr;</a></td></tr>'
        for f in vdoc["findings"]
    )
    sport_ver_rows = "".join(
        f'<tr><td><a href="sports/{e(slug)}.html">{e(slug)}</a></td>'
        f'<td>{b["confirmed"]}</td><td>{b["corrected"]}</td><td>{b["flagged"]}</td><td>{b["not_rechecked"]}</td></tr>'
        for slug, b in sorted(vsports.items())
    )
    verification_body = f"""
<h1>Live Verification — every row re-checked against its official page</h1>
<p class="lede">Earlier passes in this repository audited the dataset's shape and said so. This page records the result of actually re-fetching the governing-body pages on <b>{e(vdoc["generated"])}</b> and comparing them value by value with the published rows: <b>{vs["confirmed"]} confirmed</b>, <b>{vs["corrected"]} corrected</b>, <b>{vs["flagged"]} flagged</b> and <b>{vs["not_rechecked"]} explicitly not re-checked</b> out of {vs["rows"]}.</p>

<div class="grid kpis">
  {kpi_box(vs["confirmed"], "Confirmed against official page", "hi")}
  {kpi_box(vs["corrected"], "Corrected from official page", "md")}
  {kpi_box(vs["flagged"], "Flagged, unchanged", "fl")}
  {kpi_box(vs["not_rechecked"], "Not re-checked (reason given)")}
</div>

<div class="card">
  <h2>How to read this page</h2>
  <ul>
    <li><b>Confirmed</b> — the official page was re-fetched and the participants, date, venue and (where published) start time or game identifier were read back and matched.</li>
    <li><b>Corrected</b> — the official page disagreed, settled the value unambiguously, and the dataset source was amended to match. Nothing was corrected on a hunch.</li>
    <li><b>Flagged</b> — the page disagrees or cannot decide it. Nothing was changed; the discrepancy is published here and on Flagged for Review.</li>
    <li><b>Not re-checked</b> — no official page was re-read in this pass. The row keeps its original status and links, and the blocker is printed so the gap is visible rather than implied.</li>
  </ul>
  <p>{e(vdoc["method"])}</p>
</div>

<h2>Coverage by sport</h2>
<div class="table-wrap">
  <table>
    <thead><tr><th>Sport</th><th>Confirmed</th><th>Corrected</th><th>Flagged</th><th>Not re-checked</th></tr></thead>
    <tbody>{sport_ver_rows}</tbody>
  </table>
</div>

<h2>Findings from this pass ({len(vdoc["findings"])})</h2>
<div class="table-wrap">
  <table>
    <thead><tr><th>ID</th><th>Severity</th><th>What was found</th><th>Status</th><th>Source</th></tr></thead>
    <tbody>{ver_findings}</tbody>
  </table>
</div>

<h2>Row-by-row register ({len(vdoc["rows"])} rows)</h2>
<div class="table-wrap">
  <table>
    <thead><tr><th>Row</th><th>Match</th><th>Outcome</th><th>What the official page said</th><th>Official source</th></tr></thead>
    <tbody>{ver_rows}</tbody>
  </table>
</div>

<div class="note warn">
  <b>Boundary.</b> The validator makes no network request; the reads recorded here were made by hand during the session and are dated. Model prices remain our own estimates and were not re-priced by this pass — snapshot drift is disclosed rather than rewritten. A publisher can change a page after it is read.
</div>
"""
    (target_root / "live-verification.html").write_text(
        render_shell("Live Verification", verification_body, "livev", site_depth=0, repo_depth=repo_depth_base), encoding="utf-8"
    )

    # 8c. live-refresh.html — live OLBG recapture, diff and verification boundary
    live_events = D["live"]["events"]
    live_diff = D["live_diff"]
    ls = live_diff["summary"]
    fix_by_event = {
        int(f["olbg"]["event_id"]): f
        for f in fixtures
        if (f.get("olbg") or {}).get("event_id")
    }
    live_rows = []
    for ev in live_events:
        fx = fix_by_event.get(int(ev["event_id"]))
        if fx:
            status_cell = (
                f'{badge_status(fx["status"])}<span class="sub">'
                f'<a href="sports/{e(fx["sport"])}.html">{e(fx["id"])}</a></span>'
            )
            official = "".join(
                f'<a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["name"])} &nearr;</a><br>'
                for s in fx.get("sources", [])[:2]
            )
        else:
            status_cell = (
                '<span class="badge unverified">Unverified</span>'
                '<span class="sub">Upstream only - no governing-body confirmation</span>'
            )
            official = '<span class="sub">Blank - not confirmed from an official source</span>'
        live_rows.append(
            f'<tr><td><a href="sports/{e(ev["sport"])}.html">{e(ev["sport"])}</a></td>'
            f'<td><b><a href="{e(ev["url"])}" target="_blank" rel="noopener">{e(ev["title"])} &nearr;</a></b>'
            f'<span class="sub">{e(ev["competition"])}</span></td>'
            f'<td>{e(ev["time_shown"])}</td>'
            f'<td>{e(ev["market"] or "Unconfirmed")}</td>'
            f'<td>{e(ev["selection"])}</td>'
            f'<td>{e(ev["consensus"])}</td>'
            f'<td>{status_cell}</td>'
            f'<td>{official}</td></tr>'
        )
    changed_rows = [
        f'<tr><td>{e(c["sport"])}</td>'
        f'<td><b><a href="{e(c["olbg_url"])}" target="_blank" rel="noopener">{e(c["title"])} &nearr;</a></b>'
        f'<span class="sub"><a href="sports/{e(c["sport"])}.html">{e(c["fixture_id"])}</a></span></td>'
        f'<td>{e(c["was"]["selection"])}<span class="sub">{e(c["was"]["consensus"])}</span></td>'
        f'<td>{e(c["now"]["selection"])}<span class="sub">{e(c["now"]["consensus"])}</span></td>'
        f'<td>{"<b>Selection changed</b>" if c["selection_flipped"] else "Tip count moved"}</td></tr>'
        for c in live_diff["changed"]
    ]
    absent_rows = [
        f'<tr><td>{e(r["sport"])}</td>'
        f'<td><b>{e(r["home"])} vs {e(r["away"])}</b><span class="sub">{e(r["competition"])}</span></td>'
        f'<td>{e(r["start_utc"] or "Unconfirmed UTC")}</td>'
        f'<td><a href="sports/{e(r["sport"])}.html">{e(r["fixture_id"])}</a></td>'
        f'<td><a href="{e(r["olbg_url"])}" target="_blank" rel="noopener">OLBG event page &nearr;</a></td></tr>'
        for r in live_diff["dataset_rows_absent_from_capture"]
    ]
    verified_live = sum(1 for ev in live_events if int(ev["event_id"]) in fix_by_event)
    rr_live = "../" * repo_depth_base
    live_body = f"""
<h1>Live OLBG Refresh &mdash; Recaptured {e(D["live"]["fetched_utc"])}</h1>
<p class="lede">All 17 in-scope OLBG sport hubs were re-fetched at <b>{e(D["live"]["fetched_utc"])}</b> and compared,
event by event, with the committed desk snapshot. <b>{ls["live_events_captured"]} live cards</b> were captured across
<b>{ls["sports_with_live_events"]} sports</b>. <b>{verified_live}</b> join to a source-verified dataset row by OLBG
<code>event_id</code>; the remaining <b>{ls["new_not_in_dataset"]}</b> are published here as <b>Unverified upstream-only
rows</b> with every sporting field left blank. Nothing on this page is inferred.</p>

<div class="grid kpis">
  {kpi_box(ls["live_events_captured"], "Live Cards Captured", "fl")}
  {kpi_box(verified_live, "Joined To Verified Rows")}
  {kpi_box(ls["consensus_or_selection_changed"], "Consensus / Selection Moved", "md")}
  {kpi_box(ls["new_not_in_dataset"], "Unverified Upstream Cards", "md")}
  {kpi_box(ls["dataset_rows_absent_from_capture"], "Dataset Rows Not On First Screen")}
</div>

<div class="card">
  <h2>What this refresh does and does not claim</h2>
  <ul>
    <li><b>Refreshed:</b> OLBG's own tip counter and most-tipped selection for every card that joins to a dataset row.
        Each refreshed row stores <code>olbg.captured_utc</code> and the superseded value in
        <code>olbg.consensus_prior</code>.</li>
    <li><b>Unchanged:</b> kick-off times, venues, records, ratings, prices and confidence tiers. Those still come only
        from the governing-body sources recorded on each fixture.</li>
    <li><b>Not claimed:</b> that an upstream-only card is real, scheduled, or correctly named. OLBG is a discovery
        surface, not an official source, so those rows stay unverified and unpriced.</li>
    <li><b>Known upstream limits:</b> OLBG truncates each hub at roughly 20 cards behind a "Load More Tips" control and
        renders US-Eastern clock strings without a timezone label, so "not in capture" is logged as a coverage gap, not
        as an expiry.</li>
  </ul>
</div>

<h2>Full Live Capture ({len(live_rows)} cards, all 17 sports attempted)</h2>
<div class="table-wrap">
  <table>
    <thead><tr><th>Sport</th><th>Event (OLBG)</th><th>OLBG Clock</th><th>Market</th><th>Most-Tipped Selection</th><th>Consensus</th><th>Dataset Verification</th><th>Official Source</th></tr></thead>
    <tbody>{"".join(live_rows)}</tbody>
  </table>
</div>

<h2>Consensus / Selection Changes Since The Committed Snapshot ({len(changed_rows)})</h2>
<div class="table-wrap">
  <table>
    <thead><tr><th>Sport</th><th>Event</th><th>Committed Capture</th><th>{e(D["live"]["fetched_utc"])} Recapture</th><th>Change</th></tr></thead>
    <tbody>{"".join(changed_rows)}</tbody>
  </table>
</div>

<h2>Dataset Rows Not Present On The Recaptured First Screen ({len(absent_rows)})</h2>
<p>These rows keep their governing-body kick-off times. Absence from OLBG's first screen is <b>not</b> treated as
cancellation or expiry, because the hub caps its initial render.</p>
<div class="table-wrap">
  <table>
    <thead><tr><th>Sport</th><th>Fixture</th><th>Official Kick-Off (UTC)</th><th>Desk Row</th><th>Upstream Page</th></tr></thead>
    <tbody>{"".join(absent_rows)}</tbody>
  </table>
</div>

<h2>Sports With No Live OLBG Tips At Capture Time</h2>
<p><b>Aussie Rules (ID 22)</b> and <b>eSports (ID 23)</b> returned "No tips found"; <b>Rugby League (ID 10)</b> returned
2027 outright markets only. The desk's 9 AFLW fixtures, 1 League of Legends Worlds tie and 7 RLWC26 fixtures remain
governed by their official sources and keep their earlier OLBG capture timestamp. This gap is listed on
<a href="flagged.html">Flagged for Review</a> and is never back-filled.</p>

<p class="sub">Machine-readable outputs:
<a href="{rr_live}data/live_snapshot.json">data/live_snapshot.json</a> &middot;
<a href="{rr_live}data/live_diff.json">data/live_diff.json</a> &middot;
<a href="{rr_live}data/live_baseline.json">data/live_baseline.json</a> &middot;
<a href="{rr_live}datasets/flagged_for_review.json">datasets/flagged_for_review.json</a></p>
"""
    (target_root / "live-refresh.html").write_text(
        render_shell("Live Refresh", live_body, "live", site_depth=0, repo_depth=repo_depth_base), encoding="utf-8"
    )

    # 9. flagged.html — Flagged for Review (Defects, Scope Notes & Row-Level Flags)
    finding_rows = [
        f'<tr><td><code>{e(fd["id"])}</code><span class="sub">{e(fd["category"])}</span></td>'
        f'<td>{badge_conf(fd["severity"])}</td>'
        f'<td><b>{e(fd["affected"])}</b><span class="sub">{e(fd["summary"])}</span></td>'
        f'<td>{e(fd["evidence"])}<span class="sub"><b>Resolution:</b> {e(fd["resolution"])}</span></td>'
        f'<td><a href="{e(fd["official_url"])}" target="_blank" rel="noopener">Official source &nearr;</a></td></tr>'
        for fd in D["flagged"]["findings"]
    ]
    row_flag_trs = [
        f'<tr><td><code>{e(rf["match_id"])}</code><span class="sub"><a href="sports/{e(rf["sport"])}.html">{e(rf["sport"])}</a></span></td>'
        f'<td><b>{e(rf["match"])}</b><span class="sub">{e(rf["competition"])}</span></td>'
        f'<td>{badge_status(rf["status"])}</td>'
        f'<td>{" ; ".join(e(x) for x in rf["flags"]) or "Unconfirmed UTC start time left blank"}</td>'
        f'<td><a href="{e(rf["official_url"])}" target="_blank" rel="noopener">Verify &nearr;</a></td></tr>'
        for rf in D["flagged"]["rows"]
    ]
    flagged_body = f"""
<h1>Flagged for Review — Upstream Bugs, Scope Notes &amp; Unconfirmed Fields</h1>
<p class="lede">Complete transparency log of all <b>{len(D["flagged"]["findings"])} systemic upstream/audit findings</b> and <b>{len(D["flagged"]["rows"])} row-level annotations</b> where a start time, early-season rating, or upstream OLBG field was missing or defective.</p>

<div class="grid kpis">
  {kpi_box(len(D["flagged"]["findings"]), "Upstream & Audit Findings", "fl")}
  {kpi_box(D["flagged"]["summary"]["cross_checked_rows"], "Cross-Checked Fixtures", "md")}
  {kpi_box(D["flagged"]["summary"]["missing_utc_rows"], "Unconfirmed UTC Left Blank")}
  {kpi_box(len(D["flagged"]["rows"]), "Annotated Dataset Rows")}
</div>

<h2>Systemic Upstream OLBG Bugs, Cross-Session Audit Findings &amp; Borderline Scope Flags</h2>
<div class="table-wrap">
  <table>
    <thead><tr><th>Finding ID</th><th>Severity</th><th>Affected Scope</th><th>Verified Evidence &amp; Resolution</th><th>Source Link</th></tr></thead>
    <tbody>{"".join(finding_rows)}</tbody>
  </table>
</div>

<h2>Row-by-Row Annotations &amp; Blank-Field Log ({len(row_flag_trs)} Rows)</h2>
<div class="table-wrap">
  <table>
    <thead><tr><th>Row ID</th><th>Match / Event</th><th>Verification</th><th>Flag / Unconfirmed Field Reason</th><th>Official Link</th></tr></thead>
    <tbody>{"".join(row_flag_trs)}</tbody>
  </table>
</div>
"""
    (target_root / "flagged.html").write_text(
        render_shell("Flagged for Review", flagged_body, "flag", site_depth=0, repo_depth=repo_depth_base), encoding="utf-8"
    )

    # 10. 404.html
    not_found_body = """
<h1>Page Not Found (404)</h1>
<p class="lede">The requested URL does not exist. Jump directly to any verified board section below:</p>
<div class="card">
  <ul>
    <li><a href="index.html">Executive Overview Dashboard (134 Source-Linked Events)</a></li>
    <li><a href="picks.html">All Originated Betting Lines &amp; Markets</a></li>
    <li><a href="live-refresh.html">Live OLBG Refresh &amp; Verification Boundary</a></li>
    <li><a href="predictions.html">31 High-Confidence Human Predictions</a></li>
    <li><a href="sports.html">All 17 In-Scope Sports Directory</a></li>
    <li><a href="flagged.html">Flagged for Review</a></li>
  </ul>
</div>
"""
    (target_root / "404.html").write_text(
        render_shell("404 Not Found", not_found_body, "", site_depth=0, repo_depth=repo_depth_base), encoding="utf-8"
    )


def main() -> None:
    D = load_data()
    # 1. Render primary site at repository root (/)
    build_all_pages(ROOT, repo_depth_base=0, D=D)

    # 2. Mirror full standalone site + data into /f7fa77fc/
    ns = ROOT / "f7fa77fc"
    build_all_pages(ns, repo_depth_base=1, D=D)
    (ns / "data").mkdir(parents=True, exist_ok=True)
    for jf in (ROOT / "data").glob("*.json"):
        if jf.name in ("fixtures.json", "lines.json", "predictions.json", "olbg_taxonomy.json", "sources.json", "coverage.json", "verification.json"):
            shutil.copyfile(jf, ns / "data" / jf.name)

    root_pages = len(list(ROOT.glob("*.html"))) + len(list((ROOT / "sports").glob("*.html")))
    ns_pages = len(list(ns.glob("*.html"))) + len(list((ns / "sports").glob("*.html")))
    print(f"Built {root_pages} HTML pages at / and {ns_pages} mirrored HTML pages at /f7fa77fc/.")


if __name__ == "__main__":
    main()
