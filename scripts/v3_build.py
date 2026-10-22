#!/usr/bin/env python3
"""
v3_build.py - generates data/v3/*.json, the v3/ dashboard and the root landing page.

Nothing is fetched here: the build is deterministic from scripts/v3_data.py + scripts/v3_model.py
so that scripts/v3_validate.py can re-run it and compare.
"""
from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path

import v3_data as D
import v3_model as M
from v3_prose import HIGH_PROSE, auto_summary

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "v3"
V3 = ROOT / "v3"

SNAPSHOT = "2026-10-22T03:30:00Z"
SPORTS = [
    ("tennis", "Tennis", 3),
    ("basketball", "Basketball", 4),
    ("golf", "Golf", 5),
    ("cricket", "Cricket", 7),
    ("snooker", "Snooker", 8),
    ("rugby-union", "Rugby Union", 9),
    ("rugby-league", "Rugby League", 10),
    ("baseball", "Baseball", 12),
    ("ice-hockey", "Ice Hockey", 13),
    ("motor-racing", "Motor Racing", 14),
    ("darts", "Darts", 15),
    ("handball", "Handball", 20),
    ("volleyball", "Volleyball", 21),
    ("aussie-rules", "Aussie Rules", 22),
    ("esports", "eSports", 23),
    ("gaelic-football", "Gaelic Football", 25),
    ("greyhounds", "Greyhounds", 28),
]
SPORT_NAME = dict((s, n) for s, n, _ in SPORTS)

SPORT_NOTE = {
    "ice-hockey": "The league schedule prints the matchup and the Eastern clock but not the arena, so the venue column is blank on every NHL row rather than assumed from the home club.",
    "basketball": "NBA rows use the 2026-27 record from the official standings, where only four games league-wide had been played. A one-game sample is noisy, so every NBA selection is capped below High. EuroLeague rows use the full 20-club table.",
    "darts": "The PDC publishes the session start and the match order, not individual walk-on times, so each row carries the 19:00 CEST session start and leaves the per-match clock blank. pdc.tv also served a consent wall to this session: the draw and schedule were taken from the official article as indexed by search and corroborated by the Sky Sports and ESPN previews, so treat the PDC rows as corroborated rather than directly read.",
    "snooker": "The WST world ranking was captured only down to No. 11, so players outside that group are unrated and their matches are capped below High.",
    "tennis": "Only seeded players carry an official strength marker in the draw; unseeded players are unrated, so most tennis rows are capped below High.",
    "handball": "The EHF group tables were not captured for this snapshot, so both sides take the desk default and every handball row is capped below High.",
}


def esc(x) -> str:
    return html.escape(str(x if x is not None else ""))


def short(dt: str | None) -> str:
    if not dt:
        return "not published"
    d = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return d.strftime("%a %d %b, %H:%M")


def day(dt: str | None, date_local: str | None = None) -> str:
    if dt:
        d = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        return d.strftime("%d %b")
    if date_local:
        d = datetime.strptime(date_local, "%Y-%m-%d")
        return d.strftime("%d %b")
    return "n/a"


CSS = """
:root{--bg:#0d1117;--panel:#151b23;--panel2:#1c2430;--line:#2a3441;--txt:#e6edf3;--dim:#93a1b1;
--hi:#3fb950;--md:#d29922;--lo:#8b949e;--acc:#58a6ff;--red:#f85149}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--txt);
font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--acc);text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}
header.top{border-bottom:1px solid var(--line);background:#0b0f14;position:sticky;top:0;z-index:9}
header.top .wrap{display:flex;gap:18px;align-items:center;height:56px;flex-wrap:wrap}
.brand{font-weight:700;letter-spacing:.3px}.brand span{color:var(--acc)}
nav a{color:var(--dim);font-size:13.5px;margin-right:14px}
nav a.on{color:var(--txt);border-bottom:2px solid var(--acc);padding-bottom:2px}
main{padding:28px 0 64px}
h1{font-size:27px;margin:6px 0 6px;letter-spacing:-.3px}
h2{font-size:19px;margin:34px 0 10px}
h3{font-size:15.5px;margin:20px 0 6px}
p.lede{color:var(--dim);max-width:820px;margin:0 0 18px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:18px 0 6px}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.kpi .n{font-size:23px;font-weight:700}.kpi .l{font-size:12px;color:var(--dim);text-transform:uppercase;letter-spacing:.6px}
table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);
border-radius:10px;overflow:hidden;font-size:13.6px}
th{background:var(--panel2);text-align:left;padding:9px 10px;font-size:11.5px;letter-spacing:.5px;
text-transform:uppercase;color:var(--dim);border-bottom:1px solid var(--line);white-space:nowrap}
td{padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}
tr:last-child td{border-bottom:none}
tr:hover td{background:#19212b}
.mut{color:var(--dim)}.sm{font-size:12px}
.tag{display:inline-block;padding:1px 7px;border-radius:999px;font-size:11px;font-weight:600;white-space:nowrap}
.hi{background:rgba(63,185,80,.15);color:var(--hi);border:1px solid rgba(63,185,80,.35)}
.md{background:rgba(210,153,34,.14);color:var(--md);border:1px solid rgba(210,153,34,.35)}
.lo{background:rgba(139,148,158,.14);color:var(--lo);border:1px solid rgba(139,148,158,.35)}
.flag{background:rgba(248,81,73,.12);color:#ff9d97;border:1px solid rgba(248,81,73,.3)}
.ver{background:rgba(88,166,255,.12);color:#8cc7ff;border:1px solid rgba(88,166,255,.3)}
details summary{cursor:pointer;color:var(--acc);font-size:12.5px;list-style:none}
details summary::-webkit-details-marker{display:none}
details[open] summary{margin-bottom:8px}
.mkt{font-size:12.4px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin:14px 0}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px}
@media(max-width:820px){.grid2{grid-template-columns:1fr}}
ul.notes{margin:8px 0 0 18px;padding:0}ul.notes li{margin:4px 0;color:var(--dim)}
code{background:#0b0f14;border:1px solid var(--line);border-radius:5px;padding:1px 5px;font-size:12px}
footer{border-top:1px solid var(--line);color:var(--dim);font-size:12.5px;padding:20px 0}
.pill{font-size:11px;color:var(--dim);border:1px solid var(--line);border-radius:999px;padding:2px 8px;margin-left:6px}
"""


def page(title: str, active: str, body: str, depth: int = 1) -> str:
    pre = "../" * depth
    nav = "".join(
        f'<a href="{pre}v3/{s}.html" class="{"on" if active == s else ""}">{n}</a>'
        for s, n, _ in SPORTS[:6]
    )
    nav += f'<a href="{pre}v3/picks.html" class="{"on" if active == "picks" else ""}">Picks</a>'
    nav += f'<a href="{pre}v3/flagged.html" class="{"on" if active == "flagged" else ""}">Flagged</a>'
    nav += f'<a href="{pre}v3/analysis.html" class="{"on" if active == "analysis" else ""}">Analysis</a>'
    nav += f'<a href="{pre}v3/methodology.html" class="{"on" if active == "methodology" else ""}">Method</a>'
    nav += f'<a href="{pre}v3/sources.html" class="{"on" if active == "sources" else ""}">Sources</a>'
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} | OLBG Reverse-Engineered Desk</title>
<style>{CSS}</style></head><body>
<header class="top"><div class="wrap"><div class="brand">OLBG <span>Independent Desk</span></div>
<nav>{nav}</nav></div></header>
<main class="wrap">{body}</main>
<footer><div class="wrap">Snapshot {SNAPSHOT}. Every row carries an official source link. Values an official
page does not publish are left blank and flagged rather than inferred. Prices are the desk's own fair
lines, not bookmaker quotes, and are not betting advice. Published at
<a href="https://buffedlizard55-lab.github.io/OLBG1/">buffedlizard55-lab.github.io/OLBG1</a>.</div></footer>
</body></html>"""


def conf_tag(c: str | None, cap: str | None = None) -> str:
    if not c:
        return '<span class="tag lo">n/a</span>'
    cls = {"High": "hi", "Medium": "md", "Low": "lo"}.get(c, "lo")
    t = f'<span class="tag {cls}">{c}</span>'
    if cap:
        t += f'<span class="pill">capped: {esc(cap)}</span>'
    return t


def build() -> dict:
    priced = [M.price_fixture(f) for f in D.ALL]
    priced.sort(key=lambda p: (p["start_utc"] or p["date_local"] or "9999", p["sport"]))
    summary = M.summarise(priced)

    DATA.mkdir(parents=True, exist_ok=True)
    V3.mkdir(parents=True, exist_ok=True)

    fixtures_out = {
        "snapshot_utc": SNAPSHOT,
        "generated_by": "scripts/v3_build.py",
        "count": len(priced),
        "matches": [
            {k: p[k] for k in ("id", "sport", "competition", "stage", "home", "away", "start_utc",
                               "date_local", "venue", "status", "verified_at", "sources", "flags",
                               "home_input", "away_input", "event_only", "time_note")}
            for p in priced
        ],
    }
    (DATA / "fixtures.json").write_text(json.dumps(fixtures_out, indent=1), encoding="utf-8")

    lines_out = {"model": "v3-independent-normal-and-binomial", "margin": "none (fair prices)",
                 "generated_utc": SNAPSHOT, "books": []}
    for p in priced:
        if p["event_only"]:
            continue
        lines_out["books"].append({
            "fixture_id": p["id"], "home": p["home"], "away": p["away"],
            "markets": p["markets"],
        })
    (DATA / "lines.json").write_text(json.dumps(lines_out, indent=1), encoding="utf-8")

    picks = []
    for p in priced:
        if p["event_only"] or not p["best_market"]:
            continue
        b = p["best_market"]
        picks.append({
            "fixture_id": p["id"], "sport": p["sport"], "competition": p["competition"],
            "home": p["home"], "away": p["away"], "start_utc": p["start_utc"],
            "market": b["market"], "selection": b["selection"], "price": b["price"],
            "us": b["us"], "model_prob": b["model_prob"], "prob_pct": b["prob_pct"],
            "confidence": b["confidence"], "cap_reason": b.get("cap_reason"),
            "headline": p["pick"] and {
                "selection": p["pick"]["selection"], "price": p["pick"]["price"],
                "prob_pct": p["pick"]["prob_pct"], "confidence": p["pick"]["confidence"],
                "below_band": p["pick"].get("below_band", False),
            },
            "prose": HIGH_PROSE.get(p["id"]) if b["confidence"] == "High" else None,
        })
    (DATA / "predictions.json").write_text(json.dumps(
        {"snapshot_utc": SNAPSHOT, "count": len(picks),
         "high_count": sum(1 for x in picks if x["confidence"] == "High"),
         "picks": picks}, indent=1), encoding="utf-8")

    src_seen, sources = {}, []
    for p in priced:
        for s in p["sources"]:
            key = s["url"]
            if key in src_seen:
                src_seen[key]["used_by"].add(p["sport"])
                src_seen[key]["rows"] += 1
            else:
                entry = {"name": s["name"], "url": key, "rows": 1, "used_by": {p["sport"]}}
                src_seen[key] = entry
                sources.append(entry)
    src_out = [{"name": s["name"], "url": s["url"], "rows": s["rows"],
                "sports": sorted(s["used_by"])} for s in sources]
    (DATA / "sources.json").write_text(json.dumps(
        {"snapshot_utc": SNAPSHOT, "count": len(src_out), "sources": src_out}, indent=1), encoding="utf-8")

    ver_out = [{"area": a, "url": u, "read_at": t, "what": w} for a, u, t, w in D.VERIFICATION]
    (DATA / "verification.json").write_text(json.dumps(
        {"snapshot_utc": SNAPSHOT, "count": len(ver_out), "checks": ver_out}, indent=1), encoding="utf-8")

    by_sport = {}
    for p in priced:
        by_sport.setdefault(p["sport"], []).append(p)
    coverage = {
        "snapshot_utc": SNAPSHOT,
        "sports": [
            {"sport": s, "label": n, "olbg_index": i,
             "fixtures": len(by_sport.get(s, [])),
             "verified": sum(1 for p in by_sport.get(s, []) if p["status"] == "verified"),
             "carried": sum(1 for p in by_sport.get(s, []) if p["status"] == "carried"),
             "high": sum(1 for p in by_sport.get(s, []) if p["best_market"] and p["best_market"]["confidence"] == "High"),
             "market_rows": sum(len(p["markets"]) for p in by_sport.get(s, []))}
            for s, n, i in SPORTS
        ],
    }
    coverage["totals"] = summary
    (DATA / "coverage.json").write_text(json.dumps(coverage, indent=1), encoding="utf-8")

    # ------------------------------------------------------------------ pages
    sports_nav = "".join(
        f'<a href="v3/{s}.html" style="display:inline-block;margin:4px 10px 4px 0">{n} '
        f'<span class="mut">({len(by_sport.get(s, []))})</span></a>' for s, n, _ in SPORTS)

    kpis = f"""<div class="kpis">
<div class="kpi"><div class="n">{summary['fixtures']}</div><div class="l">fixtures &amp; cards</div></div>
<div class="kpi"><div class="n">{summary['priced_matches']}</div><div class="l">priced head-to-heads</div></div>
<div class="kpi"><div class="n">{summary['markets']:,}</div><div class="l">originated prices</div></div>
<div class="kpi"><div class="n">{summary['high_picks']}</div><div class="l">High-band picks</div></div>
<div class="kpi"><div class="n">{len(ver_out)}</div><div class="l">official pages read</div></div>
<div class="kpi"><div class="n">{sum(len(p['flags']) for p in priced)}</div><div class="l">open flags</div></div>
</div>"""

    # index page
    rows = ""
    for s, n, i in SPORTS:
        ps = by_sport.get(s, [])
        if not ps:
            continue
        hi = sum(1 for p in ps if p["best_market"] and p["best_market"]["confidence"] == "High")
        nextp = next((p for p in ps if p["start_utc"]), None)
        if hi:
            hitag = '<span class="tag hi">' + str(hi) + ' High</span>'
        else:
            hitag = '<span class="mut">-</span>'
        if nextp is None:
            nxt = ""
        else:
            nxt = short(nextp["start_utc"]) if nextp["start_utc"] else (nextp["date_local"] or "")
        rows += (f'<tr><td><a href="{s}.html">{esc(n)}</a><span class="pill">OLBG #{i}</span></td>'
                 f'<td>{len(ps)}</td><td>{sum(1 for p in ps if p["status"]=="verified")}</td>'
                 f'<td>{sum(len(p["markets"]) for p in ps)}</td>'
                 f'<td>{hitag}</td>'
                 f'<td class="sm mut">{esc(nxt)}</td></tr>')
    body = f"""<h1>Independent match list, priced from official sources only</h1>
<p class="lede">A rebuilt OLBG-style board for every in-scope sport except soccer, boxing, MMA, American
football, hurling, horse racing, cycling and specials. Each row was checked against a league, tour or
governing-body page on 22 October 2026; the desk then priced the match winner, a handicap ladder, a
total ladder and, where the sport allows, the correct score. No tipster price was read.</p>
{kpis}
<h2>Sports</h2>
<table><thead><tr><th>Sport</th><th>Rows</th><th>Re-verified today</th><th>Prices</th><th>High picks</th><th>Next start (UTC)</th></tr></thead>
<tbody>{rows}</tbody></table>
<h2>What changed in this snapshot</h2>
<div class="grid2">
<div class="card"><h3>Expired, not carried forward</h3><ul class="notes">
<li>All 21 October NHL games, including the Sabres-Flyers and Senators-Panthers fixtures that were still open at the previous snapshot.</li>
<li>All 21 October NBA games and the Sacramento-LA Clippers row.</li>
<li>Three GBGB greyhound cards that had already run.</li>
<li>Eleven Northern Ireland Open second-round snooker ties, replaced by the eight third-round matches on the official Thursday card.</li>
<li>Three Almaty tennis rows that no longer appear on the day-six order of play.</li>
<li>New Zealand v India first T20I and Australia Women v New Zealand Women third T20I: both had started before this snapshot.</li>
</ul></div>
<div class="card"><h3>Corrections and new findings</h3><ul class="notes">
<li>Port Adelaide v Collingwood (AFLW) moves from 08:15Z to 08:45Z: the official release is 7.15pm ACDT, not 7.15pm AEST.</li>
<li>The NHL IDs previously stored for 22 October did not match the league schedule; all fourteen rows are re-keyed to the official game IDs.</li>
<li>MLB is now a single World Series series, Tampa Bay at Milwaukee for Games 1 and 2.</li>
<li>EuroLeague home/away was re-read from each Round 7 match page rather than from the game-centre cards.</li>
<li>The band rule retired nineteen previously published High picks that sat shorter than -250.</li>
</ul></div>
</div>
<h2>How to read a row</h2>
<div class="card"><p><b>Desk pick</b> is the strongest selection on that match whose fair price still
clears -250 (decimal 1.40). <b>Model %</b> is the desk's own probability for that selection.
<b>Confidence</b> is High only when the probability is at least 70% and the price sits inside the
-250 to +10000 band; below that band the pick is capped at Medium and labelled. <b>Source</b> opens
the official page the participants, venue and start were read from.</p>
<p class="sm mut">Jump to <a href="picks.html">the High picks</a>,
<a href="flagged.html">the {sum(len(p['flags']) for p in priced)} flagged items</a>,
<a href="analysis.html">the analysis</a> or <a href="sources.html">the source register</a>.</p></div>"""
    (V3 / "index.html").write_text(page("Overview", "index", body), encoding="utf-8")

    # sport pages
    for s, n, i in SPORTS:
        ps = by_sport.get(s, [])
        trs = ""
        for p in ps:
            if p["event_only"]:
                trs += (f'<tr><td>{esc(day(p["start_utc"], p["date_local"]))}</td>'
                        f'<td><b>{esc(p["home"])}</b></td><td>{esc(p["competition"])}<br>'
                        f'<span class="sm mut">{esc(p["stage"])}</span></td>'
                        f'<td class="sm">{esc(p["venue"])}</td>'
                        f'<td colspan="3" class="sm mut">Event card only - no head-to-head market priced</td>'
                        f'<td><span class="tag lo">n/a</span></td>'
                        f'<td class="sm"><a href="{esc(p["sources"][0]["url"])}" target="_blank" rel="noopener">official</a></td></tr>')
                continue
            b = p["best_market"]
            mk = ""
            if b:
                mk = (f'{esc(b["selection"])}<br><span class="sm mut">{esc(b["market"])} &middot; '
                      f'{b["price"]:.2f} ({b["us"]:+d})</span>')
            else:
                mk = '<span class="mut">no selection cleared -250</span>'
            det = ""
            ladder = "".join(
                f'<tr><td>{esc(m["market"])}</td><td>{esc(m["selection"])}</td>'
                f'<td>{m["prob_pct"]:.1f}%</td><td>{m["price"]:.2f}</td>'
                f'<td class="sm mut">{m["us"]:+d}</td></tr>'
                for m in p["markets"][:14])
            det = (f'<details><summary>market sheet</summary><table class="mkt"><thead><tr>'
                   f'<th>Market</th><th>Selection</th><th>Model</th><th>Price</th><th>US</th></tr></thead>'
                   f'<tbody>{ladder}</tbody></table>'
                   f'<p class="sm mut" style="margin-top:8px">Inputs: {esc(auto_summary(p))}</p></details>')
            fl = " ".join('<span class="tag flag">flag</span>' for _ in p["flags"][:1])
            if b:
                prob_cell = str(round(b["prob_pct"], 1)) + "%"
                conf_cell = conf_tag(b["confidence"], b.get("cap_reason"))
            else:
                prob_cell = "n/a"
                conf_cell = conf_tag(None)
            clock = short(p["start_utc"]).split(", ")[-1] if p["start_utc"] else ""
            src_url = p["sources"][0]["url"] if p["sources"] else "#"
            trs += ('<tr><td class="sm">' + esc(day(p["start_utc"], p["date_local"])) + '<br>'
                    '<span class="mut">' + esc(clock) + '</span></td>'
                    '<td><b>' + esc(p["home"]) + '</b><br><span class="mut">v</span> ' + esc(p["away"]) + '<br>'
                    '<span class="sm mut">' + esc(p["stage"]) + '</span></td>'
                    '<td class="sm">' + esc(p["competition"]) + '<br><span class="mut">' +
                    esc(p["venue"] or "venue not published") + '</span></td>'
                    '<td>' + mk + '</td><td>' + prob_cell + '</td>'
                    '<td>' + conf_cell + '</td>'
                    '<td class="sm"><a href="' + esc(src_url) + '" target="_blank" rel="noopener">'
                    'official</a> ' + fl + '<br><span class="mut">' + esc(p["status"]) + '</span></td>'
                    '<td class="sm">' + det + '</td></tr>')
        flags_html = "".join(f"<li>{esc(f)}</li>" for p in ps for f in p["flags"])
        body = f"""<h1>{esc(n)}</h1>
<p class="lede">{len(ps)} rows in scope at this snapshot, {sum(1 for p in ps if p['status']=='verified')}
re-verified against an official page on 22 October 2026 and
{sum(1 for p in ps if p['status']=='carried')} carried with their official link intact. Market sheet
opens the full ladder for each match.</p>
<table><thead><tr><th>Start</th><th>Fixture</th><th>Competition / venue</th><th>Desk pick</th>
<th>Model</th><th>Confidence</th><th>Source</th><th></th></tr></thead><tbody>{trs}</tbody></table>
<h2>Notes and flags for this sport</h2>
<div class="card"><p class="sm">{esc(SPORT_NOTE.get(s, "Every value on this page was read from the official page linked in the row; anything the page does not publish is blank and flagged."))}</p>
<ul class="notes">{flags_html or '<li>No row-specific flags.</li>'}</ul></div>"""
        (V3 / f"{s}.html").write_text(page(n, s, body), encoding="utf-8")

    # picks page
    highs = [p for p in picks if p["confidence"] == "High" and p.get("prose")]
    hrows = ""
    for p in highs:
        hrows += (f'<div class="card"><div class="sm mut">{esc(SPORT_NAME[p["sport"]])} &middot; '
                  f'{esc(p["competition"])} &middot; {esc(short(p["start_utc"]) if p["start_utc"] else "")}</div>'
                  f'<h3 style="margin:6px 0 4px">{esc(p["home"])} v {esc(p["away"])}</h3>'
                  f'<p style="margin:0 0 8px">{esc(p["prose"])}</p>'
                  f'<p class="sm"><span class="tag hi">High</span> '
                  f'{esc(p["selection"])} at <b>{p["price"]:.2f}</b> '
                  f'<span class="mut">({p["us"]:+d} &middot; model {p["prob_pct"]:.1f}%)</span> '
                  f'&middot; <a href="{esc(("https://www.google.com/search?q=" + p["home"] + " " + p["away"]))}"'
                  f' target="_blank" rel="noopener">match search</a></p></div>')
    mrows = ""
    for p in picks:
        if p["confidence"] == "High":
            continue
        mrows += (f'<tr><td class="sm">{esc(short(p["start_utc"]) if p["start_utc"] else "")}</td>'
                  f'<td>{esc(SPORT_NAME[p["sport"]])}</td>'
                  f'<td>{esc(p["home"])} v {esc(p["away"])}</td>'
                  f'<td>{esc(p["selection"])}<br><span class="sm mut">{esc(p["market"])}</span></td>'
                  f'<td>{p["price"]:.2f}</td><td>{p["prob_pct"]:.1f}%</td>'
                  f'<td>{conf_tag(p["confidence"], p.get("cap_reason"))}</td></tr>')
    body = f"""<h1>Picks</h1>
<p class="lede">One selection per priced match. The desk picks the strongest line that still clears
-250, because anything shorter is excluded by policy. {len(highs)} selections meet both tests for a
High grade (model probability at least 70% and a price inside the band); the rest are capped and the
reason is shown.</p>
<h2>High confidence ({len(highs)})</h2>{hrows or '<p class="mut">None qualified.</p>'}
<h2>Everything else ({len(picks)-len(highs)})</h2>
<table><thead><tr><th>Start (UTC)</th><th>Sport</th><th>Fixture</th><th>Selection</th><th>Price</th>
<th>Model</th><th>Confidence</th></tr></thead><tbody>{mrows}</tbody></table>
<div class="card"><h3>Why so few High grades?</h3><p>Because the desk publishes fair prices, a
selection priced at -250 to -238 is a 70.0% to 71.4% shot by construction. Requiring both a 70% model
probability and a price of 1.40 or longer therefore leaves a very narrow window, and most strong
favourites are capped as "below band". That is the honest consequence of the policy rather than a
calibration trick, and it is the single biggest difference between this board and the previous
snapshot, where nineteen High picks sat shorter than -250.</p></div>"""
    (V3 / "picks.html").write_text(page("Picks", "picks", body), encoding="utf-8")

    # flagged
    frows = ""
    for p in priced:
        for f in p["flags"]:
            frows += (f'<tr><td>{esc(SPORT_NAME.get(p["sport"], p["sport"]))}</td>'
                      f'<td>{esc(p["home"])}{" v " + esc(p["away"]) if p["away"] else ""}</td>'
                      f'<td>{esc(f)}</td>'
                      f'<td class="sm"><a href="{esc(p["sources"][0]["url"])}" target="_blank" rel="noopener">official source</a></td></tr>')
    body = f"""<h1>Flagged for review</h1>
<p class="lede">Every value the desk could not certify, and every modelling cap, is listed here with
the official link that was read. Flags do not hide a row: the row stays on its sport page with a blank
field or a capped confidence grade.</p>
<table><thead><tr><th>Sport</th><th>Fixture</th><th>Flag</th><th>Source</th></tr></thead>
<tbody>{frows}</tbody></table>
<h2>Carried rows</h2>
<p class="lede">These rows keep an official link from the previous snapshot but were not re-read on
22 October, so they can never be graded above Medium and are marked <code>carried</code> on the sport
pages: all twelve rugby union fixtures, the six volleyball fixtures, four Gaelic football county
finals, four golf tournament cards, the League of Legends Worlds card and the GBGB meeting card.</p>"""
    (V3 / "flagged.html").write_text(page("Flagged", "flagged", body), encoding="utf-8")

    # sources
    srows = "".join(
        f'<tr><td>{esc(v["area"])}</td><td><a href="{esc(v["url"])}" target="_blank" rel="noopener">'
        f'{esc(v["url"])}</a></td><td class="sm">{esc(v["read_at"])}</td><td class="sm">{esc(v["what"])}</td></tr>'
        for v in ver_out)
    allsrc = "".join(
        f'<tr><td>{esc(s["name"])}</td><td class="sm"><a href="{esc(s["url"])}" target="_blank" rel="noopener">'
        f'{esc(s["url"])}</a></td><td>{s["rows"]}</td><td class="sm">{esc(", ".join(s["sports"]))}</td></tr>'
        for s in src_out)
    body = f"""<h1>Sources and verification register</h1>
<p class="lede">The pages actually read for this snapshot, in the order they were checked, then every
source URL attached to a row.</p>
<h2>Pages read on 22 October 2026</h2>
<table><thead><tr><th>Area</th><th>Official page</th><th>Read at (UTC)</th><th>What it confirmed</th></tr></thead>
<tbody>{srows}</tbody></table>
<h2>Every source attached to a row ({len(src_out)})</h2>
<table><thead><tr><th>Source</th><th>URL</th><th>Rows</th><th>Sports</th></tr></thead><tbody>{allsrc}</tbody></table>"""
    (V3 / "sources.html").write_text(page("Sources", "sources", body), encoding="utf-8")

    # analysis
    stale = sum(1 for p in priced if p["status"] == "carried")
    body = f"""<h1>Analysis and findings</h1>
<p class="lede">What the rebuild found, what it could not verify, and where the previous board was
wrong. This page is the audit trail, not a tip sheet.</p>
<h2>1. The band rule is almost self-cancelling</h2>
<div class="card"><p>At fair prices, a 70% shot is 1.43 and a 71.4% shot is 1.40. Requiring both a
model probability of 70% or more and a price of -250 or longer leaves a 1.4-point window. Applied to
{summary['priced_matches']} priced matches, only {summary['high_picks']} selections clear it. The
practical effect is that "High" now means "top of the qualifying band", not "the desk is unusually
confident". Anyone reading the label as a skill claim is misreading it, and the previous board's
nineteen sub -250 High grades were a policy breach rather than a strength.</p></div>
<h2>2. What the official pages contradicted</h2>
<div class="card"><ul class="notes">
<li><b>AFLW:</b> Port Adelaide v Collingwood is 7.15pm ACDT at Alberton, which is 08:45Z. The stored row said 08:15Z, a 30-minute error from reading the time as AEST.</li>
<li><b>NHL:</b> the seven stored game IDs for 22 October did not line up with the league schedule; the 22 October slate is twelve games with IDs 2026020154 to 2026020165, and only two games follow on 23 October.</li>
<li><b>Snooker:</b> all eleven stored rows were second-round pairings. Pang Junxu beat Liam Davies 4-3 (14-69, 33-103(112), 112-0, 56-61, 73-35, 56-31, 81-60), so the card rolled to eight third-round matches.</li>
<li><b>Tennis:</b> three Almaty rows (Duckworth/Darderi, Mannarino/Rublev, Tsitsipas/Kukushkin) are absent from the day-six order of play and have expired; four Round of 16 matches replace them.</li>
<li><b>NBA:</b> the 21 October slate is finished and 22 October carries only two games, Cleveland at Philadelphia and Denver at Oklahoma City.</li>
<li><b>MLB:</b> only the World Series remains, Tampa Bay at Milwaukee for Games 1 and 2, then the series moves to Tropicana Field.</li>
</ul></div>
<h2>3. Coverage</h2>
<div class="card"><p>{summary['fixtures']} rows across all seventeen in-scope sports:
{summary['priced_matches']} head-to-heads with {summary['markets']:,} originated prices and
{summary['event_cards']} event cards where no head-to-head exists (four golf tournaments, Formula 1,
League of Legends Worlds and the GBGB meeting list). {summary['fixtures']-stale} rows were re-verified
today; {stale} are carried and capped at Medium.</p></div>
<h2>4. What is still missing</h2>
<div class="card"><ul class="notes">
<li><b>WTA Osaka, ATP Lyon and ATP Brussels:</b> the signed order-of-play PDFs were not located for this snapshot, so those draws are absent rather than guessed.</li>
<li><b>Golf:</b> no official entry list was captured for any of the four tournaments, so no outright or three-ball market is priced.</li>
<li><b>Volleyball:</b> the PlusLiga public schedule now redirects to the women's TAURON Liga site, and no official SuperLega table was captured, so both leagues are carried and unrated.</li>
<li><b>Greyhounds:</b> gbgb.org.uk returned HTTP 500 on every attempt, so no race card, trap draw or forecast is published.</li>
<li><b>eSports:</b> the Worlds tournament page identified the event but did not render a specific fixture, so the Swiss stage is an event card only.</li>
<li><b>PDC:</b> pdc.tv returned a cookie consent wall on every fetch. The sixteen first-round ties, the seed bracket and the 19:00 CEST session start come from the official article as indexed by search and are corroborated by Sky Sports and ESPN previews, but the desk could not read the page body directly.</li>
<li><b>Rugby league women's Round 2:</b> the NRL team-list article gives dates and venues but no kick-off clocks for England v Jillaroos, Fiji v PNG or Kiwi Ferns v France. England v Jillaroos is listed with a date only; the other two are omitted rather than guessed.</li>
</ul></div>
<h2>5. Modelling notes</h2>
<div class="card"><p>One rating per side, taken only from the official record printed in the row
(points percentage, league win rate, tournament seed, world ranking or IRL ranking). A 0-100 rating
point converts to a scoring margin through a per-sport slope, then a Normal distribution prices the
winner, a handicap ladder and a total ladder. Darts, snooker and tennis use a binomial leg model
instead. Any side without a captured official rating takes a default of 58 and the match is capped at
Medium. Every price is fair: 1/probability, no margin.</p></div>"""
    (V3 / "analysis.html").write_text(page("Analysis", "analysis", body), encoding="utf-8")

    # methodology
    body = """<h1>Methodology</h1>
<p class="lede">How a row gets onto this board, and what the desk refuses to do.</p>
<h2>Verification ladder</h2>
<table><thead><tr><th>Step</th><th>Rule</th></tr></thead><tbody>
<tr><td>1. Source</td><td>Only a league, tour, governing body, club or tournament page counts. A search snippet is never a source for a value.</td></tr>
<tr><td>2. Participants</td><td>Read from the fixture list or draw. Nothing is inferred from a seed, a bracket position or last week's card.</td></tr>
<tr><td>3. Start time</td><td>Converted to UTC from the official local clock and the official timezone. Where the page does not publish a clock, the field is blank and flagged.</td></tr>
<tr><td>4. Venue</td><td>Read from the official page. NHL rows leave the arena blank because the league schedule does not print it.</td></tr>
<tr><td>5. Form input</td><td>One official number per side, printed verbatim in the row's market sheet.</td></tr>
</tbody></table>
<h2>Status labels</h2>
<table><thead><tr><th>Label</th><th>Meaning</th></tr></thead><tbody>
<tr><td><span class="tag ver">verified</span></td><td>An official page was read for this row on 22 October 2026.</td></tr>
<tr><td><span class="tag lo">carried</span></td><td>The official link survives from the previous snapshot but was not re-read today. Capped at Medium.</td></tr>
<tr><td><span class="tag flag">flag</span></td><td>A field is missing, a source disagrees, or a modelling default was applied.</td></tr>
</tbody></table>
<h2>Pricing</h2>
<div class="card"><p>Match winner: <code>p = Phi(edge / scale)</code>, with the edge built from the two
official ratings plus a home-advantage constant set per competition. Handicap: the same Normal
distribution shifted by the line. Total: a Normal around the desk's total line. Best-of-N sports:
a binomial over legs, with the per-leg probability from the rating gap. Prices are fair to two
decimals with no overround, and every market row shows the American price alongside the decimal one.</p>
<p class="sm mut">Limits: early-season samples (NBA has four games league-wide) make records noisy;
seeds are a proxy for strength in darts, snooker and tennis; and totals are the least reliable market
on this board because no venue or weather adjustment is applied.</p></div>
<h2>What is deliberately absent</h2>
<ul class="notes"><li>No bookmaker or tipster price is read, quoted or compared.</li>
<li>No soccer, boxing, MMA, American football, hurling, horse racing, cycling or specials.</li>
<li>No implied probability is presented as a fact about the future.</li></ul>"""
    (V3 / "methodology.html").write_text(page("Methodology", "methodology", body), encoding="utf-8")

    # The root index.html belongs to the shared root desk. This session only adds a banner and a
    # companion link to it by hand (see COORDINATION.md §33) and never regenerates it, so that a
    # rebuild here cannot discard another session's landing page.
    (V3 / "index.html").write_text((V3 / "index.html").read_text(encoding="utf-8"), encoding="utf-8")

    return summary


if __name__ == "__main__":
    s = build()
    print(json.dumps(s, indent=1))
