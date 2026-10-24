#!/usr/bin/env python3
"""Desk 37003e61 builder: deterministic data exports and static site."""
from __future__ import annotations

import csv
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from s37003e61_data import (ACCESS_LOG, CAPTURED, FIXTURES, GOLF_NOTE, OLBG_ROUTES,
                            SOURCES, SPORTS, SPORT_NAME, TARGET_PER_SPORT)
from s37003e61_engine import BAND_CEILING, grade_selection, pick_rows, price_book
from s37003e61_predictions import NOT_PICKED, PREDICTIONS

OUT = ROOT / "37003e61"
DATA = ROOT / "data" / "37003e61"


def e(x) -> str:
    return html.escape("" if x is None else str(x), quote=True)


def money(am: int | None) -> str:
    if am is None:
        return "—"
    return f"+{am}" if am > 0 else f"{am}"


def pct(p: float | None) -> str:
    return "—" if p is None else f"{p * 100:.1f}%"


def reason_for(fx) -> str:
    if fx["id"] in NOT_PICKED:
        return NOT_PICKED[fx["id"]]
    if fx["status"] == "olbg_only":
        return "Seen on OLBG only; no official page for this event was read, so no line is issued."
    return SPORT_REASON.get(fx["sport"], "No price originated for this row.")


def when(iso: str) -> str:
    return iso.replace("T", " ").replace(":00Z", "Z") if iso else "—"


# ---------------------------------------------------------------------------
# Compute
# ---------------------------------------------------------------------------
BOOKS = {fx["id"]: price_book(fx) for fx in FIXTURES}
PICKS = {fid: pick_rows(fx, BOOKS[fid]) for fx, fid in ((f, f["id"]) for f in FIXTURES)}
HIGH = []
for fx in FIXTURES:
    b = BOOKS[fx["id"]]
    if b.get("high"):
        HIGH.append(dict(fixture=fx, book=b, high=b["high"]))
HIGH.sort(key=lambda r: (r["fixture"]["start_utc"] or "9999", r["fixture"]["id"]))

TODAY = [h for h in HIGH if h["fixture"]["start_utc"] and h["fixture"]["start_utc"] < "2026-10-25T00:00:00Z"]
UPCOMING = [h for h in HIGH if h not in TODAY]

RATED = [f for f in FIXTURES if BOOKS[f["id"]]["rated"]]
OFFICIAL = [f for f in FIXTURES if f["status"] == "official"]
OLBG_ONLY = [f for f in FIXTURES if f["status"] == "olbg_only"]
MARKETS = sum(len(BOOKS[f["id"]]["markets"]) for f in FIXTURES)
OUTCOMES = sum(len(m["outcomes"]) for f in FIXTURES for m in BOOKS[f["id"]]["markets"])
FLAGS = [(f["id"], fl) for f in FIXTURES for fl in f.get("flags", [])]

BY_SPORT = {}
for slug, name, _, _ in SPORTS:
    rows = [f for f in FIXTURES if f["sport"] == slug]
    BY_SPORT[slug] = dict(
        name=name, fixtures=rows,
        high=[h for h in HIGH if h["fixture"]["sport"] == slug],
    )

SPORTS_ON_TARGET = [s for s in BY_SPORT if len(BY_SPORT[s]["high"]) >= TARGET_PER_SPORT]
SHORT = [s for s in BY_SPORT if 0 < len(BY_SPORT[s]["high"]) < TARGET_PER_SPORT]
ZERO_HIGH = [s for s in BY_SPORT if not BY_SPORT[s]["high"]]
BELOW_TARGET = [s for s in BY_SPORT if len(BY_SPORT[s]["high"]) < TARGET_PER_SPORT]
NO_EVENTS = [s for s in BY_SPORT if not BY_SPORT[s]["fixtures"]]

SPORT_REASON = {
    "ice-hockey": "Two NHL rows lack one opponent's record, so they carry no price; four further rows are priced.",
    "basketball": "All five NBA rows are priced from official standings; every High line is a handicap.",
    "baseball": "Only one MLB game is scheduled (World Series Game 2). Pitcher statistics were not read, so no line is issued.",
    "tennis": "Only finals remain on the ATP card; rankings and service data were not read, so no line is issued.",
    "rugby-union": "Two Top 14 rows are priced from official league positions; the Premiership and international rows lack inputs.",
    "rugby-league": "OLBG surfaces only 2027 outrights; the two World Cup rows come from NRL.com and have unresolved kick-off timezones.",
    "cricket": "OLBG lists nine cards; the official CSA hub carries different formats, so no row could be certified.",
    "snooker": "One semi-final and a final with an undecided opponent; no frame-level data was read.",
    "darts": "Five cards, but the PDC hub returned a consent shell, so no verified draw or order of play exists.",
    "volleyball": "Four SuperLega fixtures were certified on the official calendar; no league table was read.",
    "handball": "Both EHF routes returned 404 and the HBL schedule is behind a reCAPTCHA.",
    "gaelic-sports": "Four club cards from OLBG; the GAA national hub lists only the Shinty-Hurling international.",
    "greyhounds": "OLBG lists daily races, but GBGB publishes results rather than a forward card on the route read.",
    "motor-racing": "One race. Only five drivers were classified in the session read, so the field is incomplete.",
    "golf": "The OLBG Golf hub returned 'No tips found'; no event card existed to price.",
}

SUMMARY = dict(
    desk="37003e61-olbg1",
    captured_utc=CAPTURED,
    sport_count=len(SPORTS),
    fixtures=len(FIXTURES),
    official=len(OFFICIAL),
    olbg_only=len(OLBG_ONLY),
    priced_fixtures=len(RATED),
    markets=MARKETS,
    outcomes=OUTCOMES,
    high=len(HIGH),
    high_today=len(TODAY),
    high_upcoming=len(UPCOMING),
    medium=sum(1 for f in FIXTURES if BOOKS[f["id"]].get("winner", {}) and BOOKS[f["id"]]["winner"].get("confidence") == "Medium"),
    low=sum(1 for f in FIXTURES if BOOKS[f["id"]].get("winner", {}) and BOOKS[f["id"]]["winner"].get("confidence") == "Low"),
    excluded=sum(1 for f in FIXTURES if BOOKS[f["id"]].get("winner", {}) and BOOKS[f["id"]]["winner"].get("confidence") == "Excluded"),
    predictions=len(PREDICTIONS),
    sources_read=sum(1 for s in SOURCES.values() if s["status"] == "read"),
    sources_failed=sum(1 for s in SOURCES.values() if s["status"] == "failed"),
    flags=len(FLAGS),
    band=f"{BAND_CEILING * 100:.1f}%",
)

DESK_FLAGS = [
    ("F-3700-01", "Band and floor intersect in a 1.4-point window",
     "The brief asks for High confidence above 70% and a fair price between -250 and +10000. A -250 fair price is 71.43%, so any selection above that is excluded by the price rule. Lines are therefore originated at the 70.1-71.3% quantile, and every High price prints between -235 and -248. This is disclosed rather than hidden.",
     "high"),
    ("F-3700-02", "Quota of five High picks per sport is not reached",
     f"{len(HIGH)} High selections exist across {len({h['fixture']['sport'] for h in HIGH})} sports. {len(ZERO_HIGH)} sports have none. The reasons are per-sport: no OLBG event card (golf), blocked or missing official data (darts, handball), too few events (baseball, tennis, motor racing), or the official fixture set not matching the OLBG card (cricket). No pick was invented to fill a quota.",
     "high"),
    ("F-3700-03", "Kick-off timezone unresolved for two Rugby League rows",
     "NRL.com lists New Zealand v Cook Islands at 1:05am and Australia v Fiji at 5:05am on Sunday 25 October without stating the timezone. The UTC cell is left blank on both rows rather than guessed.",
     "high"),
    ("F-3700-04", "Snooker start time differs between two official-adjacent sources",
     "The WST match list prints the semi-final at 14:00 while the OLBG card prints 18:05Z. One clock is being rendered in a different timezone. The UTC cell is flagged and the WST match is still listed.",
     "medium"),
    ("F-3700-05", "OLBG cricket card does not match the official CSA fixture hub",
     "OLBG lists North West Dragons v Northern Cape Heat and Tuskers v Western Province as T20 fixtures. The Cricket South Africa hub for the same date lists Colts three-day matches and a Pro 50 women's game. The rows are published as discovery only, with no line.",
     "high"),
    ("F-3700-06", "Golf hub empty",
     GOLF_NOTE, "high"),
    ("F-3700-07", "Volleyball and handball official routes did not render",
     "The EHF Champions League and EHF matches routes return 404, and both HBL schedule routes return a reCAPTCHA page. The affected rows are discovery-only.",
     "medium"),
    ("F-3700-08", "PDC tournament hub is behind a consent wall",
     "Two fetches of the PDC European Championship hub returned cookie-consent text only. The five dart rows therefore carry no draw, no order of play and no line.",
     "medium"),
    ("F-3700-09", "OLA desk prices are our own estimates, not bookmaker quotes",
     "Every price on this site is a zero-vig fair price derived from the inputs shown on the row. No bookmaker price was copied, and no availability or edge claim is made.",
     "low"),
]

REPO_FINDINGS = [
    ("R-01", "high", "COORDINATION.md",
     "103 task-board rows contain 15 duplicated task IDs (T1-T7, T63, T64, T424375B4, T496E, T65331685, T5821, T7A9B, T9965).",
     "A duplicated ID makes 'who owns what' ambiguous, which is the one thing the board exists to prevent. Detected by regex over table rows.",
     "COORDINATION.md"),
    ("R-02", "high", "data/current/snapshot.json",
     "The canonical root snapshot is stamped 2026-10-22T12:29:50Z with 108 listings, 72 outcomes and 0 High picks, while later desks publish dozens of High picks.",
     "A visitor landing on the root sees a two-day-old desk that reports zero High selections, next to 56 desk directories that report many. This is the presentation inconsistency the brief complains about.",
     "data/current/snapshot.json"),
    ("R-03", "medium", "repository root",
     "56 eight-character desk directories and 20 root HTML pages coexist. Each desk re-publishes its own navigation.",
     "There is no single front door. Any new desk must therefore be self-describing and link back to the root, which this one does.",
     "index.html"),
    ("R-04", "medium", "data/3c021b49/fixtures.json",
     "The 23 October desk lists 'Basilashvili v Tsitsipas' and 'Medvedev v Bublik' as ATP Almaty semi-finals at 10:00Z and 13:00Z on 24 October. The official ATP order of play for Day 9 shows the final as Medvedev v Basilashvili.",
     "Both semi-final pairings cannot still be correct. The rows are stale within 24 hours, which shows why this desk stamps every fixture with a read time and an expiry.",
     "data/3c021b49/fixtures.json"),
    ("R-05", "low", "data/3c021b49/predictions.json",
     "51 predictions, minimum 39 words, no occurrence of the internal terms. This is compliant and is recorded so the good state is not lost.",
     "Positive control: it shows the house style can be met at scale.",
     "data/3c021b49/predictions.json"),
    ("R-06", "low", "root HTML set",
     "No git conflict markers, no tracked .pyc files, and zero broken local links across index, picks, predictions, sports and flagged pages.",
     "Recorded as a clean baseline for the next session.",
     "index.html"),
]

# ---------------------------------------------------------------------------
# HTML shell
# ---------------------------------------------------------------------------
CSS = """
:root{--ink:#12181f;--muted:#5d6b7a;--line:#e2e8ef;--bg:#f6f8fb;--card:#fff;--brand:#12507b;--brand2:#0d7a6a;
--high:#0b6b46;--highbg:#e6f6ee;--med:#8a5a00;--medbg:#fff4db;--low:#4b5563;--lowbg:#eef1f5;--exc:#8c2c2c;--excbg:#fdeaea}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg)}
a{color:var(--brand);text-decoration:none}a:hover{text-decoration:underline}
header.top{position:sticky;top:0;z-index:20;background:rgba(255,255,255,.96);border-bottom:1px solid var(--line);backdrop-filter:blur(6px)}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}
.top .wrap{display:flex;align-items:center;gap:18px;min-height:60px;flex-wrap:wrap}
.brand{font-weight:800;letter-spacing:-.02em;font-size:18px}.brand span{color:var(--brand2)}
nav.main{display:flex;gap:14px;flex-wrap:wrap;font-size:14px}
nav.main a{color:var(--muted);font-weight:600;padding:4px 0;border-bottom:2px solid transparent}
nav.main a.on,nav.main a:hover{color:var(--ink);border-color:var(--brand2);text-decoration:none}
main{padding:28px 0 60px}
.hero{background:linear-gradient(135deg,#0e3a5c,#12507b 55%,#0d7a6a);color:#fff;border-radius:16px;padding:30px 32px;margin-bottom:24px}
.hero h1{margin:0 0 8px;font-size:30px;line-height:1.15;letter-spacing:-.02em}
.hero p{margin:0;color:#d7e7f3;max-width:820px}
.hero .meta{margin-top:14px;font-size:13px;color:#bcd6e6}
.kpis{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin:20px 0 8px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px}
.kpi b{display:block;font-size:24px;letter-spacing:-.02em}.kpi small{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.04em}
section.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px;margin:20px 0}
section.card>h2{margin:0 0 4px;font-size:20px;letter-spacing:-.01em}
section.card>p.sub{margin:0 0 16px;color:var(--muted);font-size:14px}
h3{font-size:16px;margin:22px 0 8px}
.tablewrap{overflow-x:auto;border:1px solid var(--line);border-radius:10px}
table{width:100%;border-collapse:collapse;font-size:13.5px;background:#fff}
th,td{padding:9px 11px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
th{background:#f0f4f8;font-size:11.5px;text-transform:uppercase;letter-spacing:.05em;color:#42505f;white-space:nowrap}
tr:last-child td{border-bottom:0}
tbody tr:hover{background:#fafcfe}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.badge{display:inline-block;padding:2px 8px;border-radius:999px;font-size:11.5px;font-weight:700}
.b-high{background:var(--highbg);color:var(--high)}.b-med{background:var(--medbg);color:var(--med)}
.b-low{background:var(--lowbg);color:var(--low)}.b-exc{background:var(--excbg);color:var(--exc)}
.b-ok{background:#e6f6ee;color:#0b6b46}.b-flag{background:#fdeaea;color:#8c2c2c}.b-info{background:#e8f0f8;color:#12507b}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.nav-card{border:1px solid var(--line);border-radius:12px;padding:16px;background:#fff}
.nav-card h3{margin:0 0 4px;font-size:15px}.nav-card p{margin:0;color:var(--muted);font-size:13px}
.nav-card a{font-weight:700;font-size:14px}
.note{border-left:4px solid var(--brand2);background:#f0f8f6;padding:12px 16px;border-radius:0 10px 10px 0;margin:14px 0;font-size:14px}
.warn{border-left:4px solid #b4451f;background:#fdf3ef;padding:12px 16px;border-radius:0 10px 10px 0;margin:14px 0;font-size:14px}
.pred{display:grid;grid-template-columns:210px 1fr;gap:20px;padding:18px 0;border-bottom:1px solid var(--line)}
.pred:last-child{border-bottom:0}
.pred .sel{font-weight:800;font-size:15px}.pred p{margin:0 0 10px}
ul.basis{margin:0;padding-left:18px;color:var(--muted);font-size:13px}
ul.basis li{margin:2px 0}
.pill{display:inline-block;font-size:12px;color:var(--muted);border:1px solid var(--line);border-radius:999px;padding:2px 9px;margin:0 6px 6px 0}
footer{border-top:1px solid var(--line);color:var(--muted);font-size:12.5px;padding:24px 0 50px}
footer .wrap{display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap}
.small{font-size:12.5px;color:var(--muted)}
.tag{font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted)}
@media(max-width:900px){.kpis{grid-template-columns:repeat(3,1fr)}.grid{grid-template-columns:1fr}.pred{grid-template-columns:1fr}}
@media(max-width:560px){.kpis{grid-template-columns:repeat(2,1fr)}.hero{padding:22px}.hero h1{font-size:23px}}
"""

NAV = [
    ("index.html", "Overview"),
    ("picks.html", "Picks"),
    ("predictions.html", "Write-ups"),
    ("matches.html", "All matches"),
    ("markets.html", "Markets"),
    ("sports.html", "Sports"),
    ("flagged.html", "Flagged"),
    ("sources.html", "Sources"),
    ("methodology.html", "Method"),
    ("reverse-engineering.html", "OLBG map"),
    ("repo-audit.html", "Repo audit"),
]


def page(title: str, body: str, active: str = "", base: str = "") -> str:
    nav = "".join(
        f'<a class="{"on" if f == active else ""}" href="{base}{f}">{e(t)}</a>' for f, t in NAV)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} · OLBG research desk 37003e61</title>
<meta name="description" content="Independent, source-linked OLBG coverage of 15 sports for 24 October 2026: fixtures, originated lines, High-confidence selections and a review register.">
<style>{CSS}</style></head><body>
<header class="top"><div class="wrap"><a class="brand" href="{base}index.html">OLBG<span>.</span> desk 37003e61</a>
<nav class="main">{nav}</nav></div></header>
<main><div class="wrap">{body}</div></main>
<footer><div class="wrap"><span>Independent research desk · not affiliated with OLBG · no guaranteed returns · 18+</span>
<span>Captured {e(CAPTURED)} · <a href="{base}methodology.html">method</a> · <a href="{base}flagged.html">review register</a></span></div></footer>
</body></html>"""


def table(headers, rows, cls="") -> str:
    head = "".join(f'<th class="{c}">{e(h)}</th>' for h, c in headers)
    body = "".join("<tr>" + "".join(f'<td class="{c}">{v}</td>' for v, c in r) + "</tr>" for r in rows)
    return f'<div class="tablewrap"><table class="{cls}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def src_links(ids) -> str:
    out = []
    for sid in ids:
        s = SOURCES.get(sid)
        if not s:
            continue
        cls = "b-ok" if s["status"] == "read" else "b-flag"
        out.append(f'<a class="{cls} badge" href="{e(s["url"])}" rel="noreferrer">{e(s["name"].split("—")[0].strip())}</a>')
    return " ".join(out)


def badge(conf: str) -> str:
    cls = {"High": "b-high", "Medium": "b-med", "Low": "b-low", "Excluded": "b-exc"}.get(conf, "b-info")
    return f'<span class="badge {cls}">{e(conf)}</span>'


# ---------------------------------------------------------------------------
# Data exports
# ---------------------------------------------------------------------------
def export_data():
    DATA.mkdir(parents=True, exist_ok=True)
    fixtures = []
    for fx in FIXTURES:
        b = BOOKS[fx["id"]]
        fixtures.append(dict(
            id=fx["id"], sport=fx["sport"], sport_name=SPORT_NAME[fx["sport"]],
            competition=fx["comp"], home=fx["home"], away=fx["away"],
            start_utc=fx["start_utc"], start_note=fx.get("start_note", ""), venue=fx.get("venue", ""),
            status=fx["status"], facts=fx["facts"], flags=fx.get("flags", []),
            sources=[dict(id=s, **SOURCES[s]) for s in fx["sources"] if s in SOURCES],
            priced=b["rated"], pick=b.get("winner"), high=b.get("high"), markets=b["markets"],
        ))
    (DATA / "fixtures.json").write_text(json.dumps(dict(desk="37003e61-olbg1", captured_utc=CAPTURED,
                                                        fixtures=fixtures), indent=1))
    (DATA / "markets.json").write_text(json.dumps(
        [dict(fixture_id=f["id"], sport=f["sport"], home=f["home"], away=f["away"],
              market=m["name"], line=m["line"], outcomes=m["outcomes"])
         for f in FIXTURES for m in BOOKS[f["id"]]["markets"]], indent=1))
    (DATA / "picks.json").write_text(json.dumps(
        [dict(fixture_id=h["fixture"]["id"], sport=h["fixture"]["sport"],
              competition=h["fixture"]["comp"], match=f'{h["fixture"]["home"]} v {h["fixture"]["away"]}',
              start_utc=h["fixture"]["start_utc"], market=h["high"]["market"],
              selection=h["high"]["selection"], probability=h["high"]["probability"],
              fair_decimal=h["high"]["fair_decimal"], fair_american=h["high"]["fair_american"],
              confidence="High") for h in HIGH], indent=1))
    (DATA / "predictions.json").write_text(json.dumps(
        [dict(fixture_id=k, **v) for k, v in PREDICTIONS.items()], indent=1))
    (DATA / "sources.json").write_text(json.dumps(
        dict(sources=SOURCES, access_log=[dict(url=u, result=r, what=w) for u, r, w in ACCESS_LOG],
             olbg_routes=[dict(sport=s, sport_id=i, url=u, observed=o) for s, i, u, o in OLBG_ROUTES]), indent=1))
    (DATA / "flagged.json").write_text(json.dumps(
        dict(desk_flags=[dict(id=a, title=b, detail=c, severity=d) for a, b, c, d in DESK_FLAGS],
             row_flags=[dict(fixture_id=f, flag=t) for f, t in FLAGS],
             repo_findings=[dict(id=a, severity=b, path=c, finding=d, why=e_, evidence=f) for a, b, c, d, e_, f in REPO_FINDINGS]),
        indent=1))
    (DATA / "summary.json").write_text(json.dumps(SUMMARY, indent=1))
    with (DATA / "matches.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "sport", "competition", "home", "away", "start_utc", "status",
                    "high_selection", "high_price", "high_probability", "source_url"])
        for fx in FIXTURES:
            b = BOOKS[fx["id"]]
            h = b.get("high") or {}
            first = SOURCES.get(fx["sources"][0], {}) if fx["sources"] else {}
            w.writerow([fx["id"], fx["sport"], fx["comp"], fx["home"], fx["away"], fx["start_utc"],
                        fx["status"], h.get("selection", ""), h.get("fair_american", ""),
                        h.get("probability", ""), first.get("url", "")])


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
def high_row(h, show_sport=True) -> list:
    fx, hi = h["fixture"], h["high"]
    cells = []
    if show_sport:
        cells.append((f'<a href="sports/{fx["sport"]}.html">{e(SPORT_NAME[fx["sport"]])}</a>', ""))
    cells += [
        (f'<a href="predictions.html#{fx["id"]}"><strong>{e(fx["home"])} v {e(fx["away"])}</strong></a>'
         f'<br><span class="small">{e(fx["comp"])}</span>', ""),
        (e(when(fx["start_utc"])), ""),
        (f'<strong>{e(hi["selection"])}</strong><br><span class="small">{e(hi["market"])}</span>', ""),
        (money(hi["fair_american"]), "num"),
        (pct(hi["probability"]), "num"),
        (badge("High"), ""),
        (src_links(fx["sources"][:1]), ""),
    ]
    return cells


def index_page() -> str:
    today_rows = [high_row(h) for h in TODAY]
    up_rows = [high_row(h) for h in UPCOMING]
    headers = [("Sport", ""), ("Match", ""), ("Start (UTC)", ""), ("Selection", ""),
               ("Fair price", "num"), ("Chance", "num"), ("Tier", ""), ("Source", "")]

    cov = []
    for slug, name, _, _ in SPORTS:
        d = BY_SPORT[slug]
        n, nh = len(d["fixtures"]), len(d["high"])
        state = "On target" if nh >= TARGET_PER_SPORT else ("No events" if n == 0 else "Short")
        cls = "b-ok" if state == "On target" else ("b-flag" if state != "No events" else "b-low")
        cov.append([(f'<a href="sports/{slug}.html"><strong>{e(name)}</strong></a>', ""),
                    (str(n), "num"), (str(nh), "num"), (f"{nh}/{TARGET_PER_SPORT}", "num"),
                    (f'<span class="badge {cls}">{state}</span>', ""),
                    (e(SPORT_REASON[slug]), "small")])

    body = f"""
<div class="hero"><h1>15 sports. {len(HIGH)} High-confidence selections. Every row has a source.</h1>
<p>This is the executive summary for 24 October 2026. The table below is the answer to “what are the picks”:
each row names the match, the exact selection, the fair price and the official page it came from. The full
write-up for each selection is on <a style="color:#fff;text-decoration:underline" href="predictions.html">Write-ups</a>.</p>
<div class="meta">Captured {e(CAPTURED)} · {len(FIXTURES)} fixtures · {MARKETS} originated markets · {OUTCOMES} priced outcomes · {len(HIGH)} High selections inside the -250 to +10000 window</div></div>

<div class="kpis">
<div class="kpi"><b>{len(FIXTURES)}</b><small>Fixtures</small></div>
<div class="kpi"><b>{MARKETS}</b><small>Markets</small></div>
<div class="kpi"><b>{OUTCOMES}</b><small>Priced outcomes</small></div>
<div class="kpi"><b>{len(HIGH)}</b><small>High picks</small></div>
<div class="kpi"><b>{len(OFFICIAL)}</b><small>Official reads</small></div>
<div class="kpi"><b>{len(FLAGS) + len(DESK_FLAGS)}</b><small>Flagged items</small></div>
</div>

<section class="card"><h2>Today's High-confidence picks</h2>
<p class="sub">Start time before 00:00 UTC on 25 October. Selection, price and probability are all on the row; the source link opens the official page used.</p>
{table(headers, today_rows) if today_rows else '<p>No High selection starts today.</p>'}
</section>

<section class="card"><h2>Upcoming High-confidence picks</h2>
<p class="sub">Fixtures after midnight UTC, same rules.</p>
{table(headers, up_rows) if up_rows else '<p>No further High selections in the window.</p>'}
</section>

<section class="card"><h2>Where everything lives</h2>
<p class="sub">Six destinations, in the order most people need them.</p>
<div class="grid">
<div class="nav-card"><h3>The picks</h3><p>Every High selection and every match-winner call, with price and probability.</p><a href="picks.html">Open picks →</a></div>
<div class="nav-card"><h3>The write-ups</h3><p>One unique passage per High selection, with the official facts underneath.</p><a href="predictions.html">Open write-ups →</a></div>
<div class="nav-card"><h3>All matches</h3><p>All {len(FIXTURES)} fixtures, including the ones with no line and the reason why.</p><a href="matches.html">Open matches →</a></div>
<div class="nav-card"><h3>Markets</h3><p>Every originated market and outcome, with fair decimal and American prices.</p><a href="markets.html">Open markets →</a></div>
<div class="nav-card"><h3>Flagged for review</h3><p>Unverified rows, source failures and time conflicts, each with its link.</p><a href="flagged.html">Open the register →</a></div>
<div class="nav-card"><h3>OLBG map</h3><p>The 15 routes, sport IDs, market types and what the platform actually lists today.</p><a href="reverse-engineering.html">Open the map →</a></div>
</div></section>

<section class="card"><h2>Coverage against the five-per-sport target</h2>
<p class="sub">The target is five High selections per sport. This table states, per sport, what was found and why a shortfall exists.</p>
{table([("Sport", ""), ("Fixtures", "num"), ("High", "num"), ("Target", "num"), ("State", ""), ("Reason / note", "")], cov)}
<div class="note"><strong>Read this before the counts.</strong> {len(BELOW_TARGET)} sports fall short of five because the platform or the official route did not provide what a priced pick needs: an event card, a draw, a table or a rule set. {len(ZERO_HIGH)} sports carry no High selection at all. The shortfall is published, not padded. Golf has zero events because OLBG itself returned “No tips found”.</div>
</section>

<section class="card"><h2>How to read a pick</h2>
<p><strong>Selection</strong> is the exact bet, including any handicap line, so “Edmonton Oilers -0.75” is not shortened to “Edmonton”.
<strong>Fair price</strong> is our own zero-vig price. <strong>Chance</strong> is the probability implied by that price.
<strong>Tier</strong> is High only when the chance is above 70% <em>and</em> the fair price is inside -250 to +10000.</p>
<p class="small">The two rules intersect in a 1.4-point window, so High prices cluster between -235 and -248. That is a property of the brief, disclosed in <a href="flagged.html#F-3700-01">F-3700-01</a>.</p>
</section>
"""
    return page("Executive summary", body, "index.html")


def picks_page() -> str:
    hi_headers = [("Sport", ""), ("Match", ""), ("Start (UTC)", ""), ("Selection", ""),
                  ("Market", ""), ("Fair price", "num"), ("Decimal", "num"), ("Chance", "num"), ("Tier", ""), ("Write-up", "")]
    hi_rows = []
    for h in HIGH:
        fx, hi = h["fixture"], h["high"]
        hi_rows.append([
            (f'<a href="sports/{fx["sport"]}.html">{e(SPORT_NAME[fx["sport"]])}</a>', ""),
            (f'<strong>{e(fx["home"])} v {e(fx["away"])}</strong><br><span class="small">{e(fx["comp"])}</span>', ""),
            (e(when(fx["start_utc"])), ""), (f'<strong>{e(hi["selection"])}</strong>', ""),
            (e(hi["market"]), ""), (money(hi["fair_american"]), "num"),
            (f'{hi["fair_decimal"]:.3f}', "num"), (pct(hi["probability"]), "num"),
            (badge("High"), ""),
            (f'<a href="predictions.html#{fx["id"]}">Read →</a>', ""),
        ])
    win_headers = [("Sport", ""), ("Match", ""), ("Winner pick", ""), ("Fair price", "num"),
                   ("Chance", "num"), ("Tier", ""), ("Why not High", "")]
    win_rows = []
    for fx in FIXTURES:
        b = BOOKS[fx["id"]]
        w = b.get("winner")
        if not w:
            continue
        why = ""
        if w.get("confidence") != "High":
            if w.get("confidence") == "Excluded":
                why = f"Price is shorter than the -250 floor ({money(w['fair_american'])})."
            elif b.get("high"):
                why = f"High selection is the handicap: {e(b['high']['selection'])}."
            else:
                why = e(NOT_PICKED.get(fx["id"], ""))
        win_rows.append([
            (f'<a href="sports/{fx["sport"]}.html">{e(SPORT_NAME[fx["sport"]])}</a>', ""),
            (f'<strong>{e(fx["home"])} v {e(fx["away"])}</strong>', ""),
            (e(w["selection"]), ""), (money(w["fair_american"]), "num"),
            (pct(w["probability"]), "num"), (badge(w.get("confidence", "Low")), ""),
            (f'<span class="small">{why}</span>', ""),
        ])
    body = f"""
<div class="hero"><h1>The picks</h1><p>Two tables: the High selections that satisfy both of the brief's gates, then the match-winner call for every fixture we could price.</p>
<div class="meta">{len(HIGH)} High selections · {len(win_rows)} priced fixtures · fair prices are our own zero-vig estimates</div></div>
<section class="card"><h2>High-confidence selections</h2>
<p class="sub">All rows satisfy chance &gt; 70% and a fair American price between -250 and +10000. Written analysis exists for every row.</p>
{table(hi_headers, hi_rows)}</section>
<section class="card"><h2>Match-winner calls</h2>
<p class="sub">The winner we make for every fixture with a price book, including those where the High selection is a handicap rather than the money line.</p>
{table(win_headers, win_rows)}</section>
"""
    return page("Picks", body, "picks.html")


def predictions_page() -> str:
    blocks = []
    for h in HIGH:
        fx, hi = h["fixture"], h["high"]
        p = PREDICTIONS[fx["id"]]
        basis = "".join(f"<li><strong>{e(k)}</strong> — {e(v)}</li>" for k, v in p["basis"])
        blocks.append(f"""
<article class="pred" id="{e(fx['id'])}">
<div><div class="sel">{e(hi['selection'])}</div>
<div class="small" style="margin:4px 0 8px">{money(hi['fair_american'])} · {pct(hi['probability'])} · {e(hi['market'])}</div>
<div class="tag">{e(SPORT_NAME[fx['sport']])}</div>
<div class="small">{e(fx['home'])} v {e(fx['away'])}<br>{e(when(fx['start_utc']))}</div></div>
<div><p>{e(p['text'])}</p>
<div class="small" style="margin-bottom:4px">Official facts behind this write-up</div>
<ul class="basis">{basis}</ul>
<div style="margin-top:10px">{src_links(fx['sources'])}</div></div>
</article>""")
    body = f"""
<div class="hero"><h1>Write-ups</h1><p>One unique passage per High selection, at least 30 words, each factual clause tied to an official page.</p>
<div class="meta">{len(PREDICTIONS)} write-ups · no repeated seven-word phrase · neither internal term appears</div></div>
<section class="card">{''.join(blocks)}</section>
<section class="card"><h2>Fixtures with no write-up</h2>
<p class="sub">A row appears here when a price could not be originated from official inputs. The reason is stated rather than filled with generic prose.</p>
{table([("Fixture", ""), ("Reason", "")], [[(f'<strong>{e(f["home"])} v {e(f["away"])}</strong><br><span class="small">{e(SPORT_NAME[f["sport"]])}</span>', ""), (e(reason_for(f)), "")] for f in FIXTURES if not BOOKS[f["id"]].get("winner")])}
</section>
"""
    return page("Write-ups", body, "predictions.html")


def matches_page() -> str:
    rows = []
    for fx in FIXTURES:
        b = BOOKS[fx["id"]]
        h = b.get("high")
        status = ('<span class="badge b-ok">Official read</span>' if fx["status"] == "official"
                  else '<span class="badge b-flag">OLBG only</span>')
        pick = f'{e(h["selection"])} <span class="small">{money(h["fair_american"])}</span>' if h else "—"
        rows.append([
            (e(fx["id"]), ""), (f'<a href="sports/{fx["sport"]}.html">{e(SPORT_NAME[fx["sport"]])}</a>', ""),
            (f'<strong>{e(fx["home"])} v {e(fx["away"])}</strong><br><span class="small">{e(fx["comp"])}</span>', ""),
            (e(when(fx["start_utc"])), ""), (e(fx.get("venue", "")) or "—", ""),
            (status, ""), (pick, ""), (src_links(fx["sources"]), ""),
        ])
    body = f"""
<div class="hero"><h1>All matches</h1><p>Every row this desk captured, including the ones it refused to price.</p>
<div class="meta">{len(FIXTURES)} rows · {len(OFFICIAL)} read from an official source · {len(OLBG_ONLY)} discovery only</div></div>
<section class="card"><h2>Fixture register</h2>
<p class="sub">“Official read” means a governing body, league or tour page was fetched this session and the fixture appears on it. “OLBG only” means the event was seen on OLBG but no official page was read.</p>
{table([("ID", ""), ("Sport", ""), ("Match", ""), ("Start (UTC)", ""), ("Venue", ""), ("Status", ""), ("High pick", ""), ("Source", "")], rows)}</section>
<div class="warn"><strong>Blank is not zero.</strong> A blank start time means the timezone could not be resolved from the source, not that the time is unknown to the organisers. A missing High pick means no eligible selection existed, not that the match is unimportant.</div>
"""
    return page("All matches", body, "matches.html")


def markets_page() -> str:
    rows = []
    for fx in FIXTURES:
        for m in BOOKS[fx["id"]]["markets"]:
            for o in m["outcomes"]:
                rows.append([
                    (e(fx["id"]), ""), (e(fx["home"]) + " v " + e(fx["away"]), ""),
                    (e(m["name"]), ""), (e(o["selection"]), ""),
                    (f'{o["probability"] * 100:.1f}%', "num"), (f'{o["fair_decimal"]:.3f}', "num"),
                    (money(o["fair_american"]), "num"),
                    ('<span class="badge b-ok">In band</span>' if o["in_band"] else '<span class="badge b-low">Outside</span>', ""),
                ])
    body = f"""
<div class="hero"><h1>Markets</h1><p>Every originated market and outcome. Prices are zero-vig: decimal equals one divided by the probability.</p>
<div class="meta">{MARKETS} markets · {OUTCOMES} outcomes · no margin, no clipping</div></div>
<section class="card"><h2>Outcome book</h2>
<p class="sub">“Outside” means the fair price sits outside the brief's -250 to +10000 band; it is shown for completeness and is never presented as a High pick.</p>
{table([("Fixture", ""), ("Match", ""), ("Market", ""), ("Selection", ""), ("Chance", "num"), ("Decimal", "num"), ("American", "num"), ("Band", "")], rows)}</section>
<section class="card"><h2>What we originated, market by market</h2>
<ul class="basis">
<li><strong>Match Winner</strong> — every priced fixture, two-way.</li>
<li><strong>Handicap</strong> — a quarter or half line set where the selection's chance lands inside the brief's window; the line value is published on the row.</li>
<li><strong>Match Total</strong> — NHL only, where the expected total comes from official goals for and against per game.</li>
<li><strong>Win Race</strong> — the United States Grand Prix, five drivers classified in the session read.</li>
</ul></section>
"""
    return page("Markets", body, "markets.html")


def sports_page() -> str:
    rows = []
    for slug, name, _, sid in SPORTS:
        d = BY_SPORT[slug]
        rows.append([
            (f'<a href="sports/{slug}.html"><strong>{e(name)}</strong></a>', ""),
            (str(sid), "num"), (f'<a href="https://www.olbg.com/betting-tips/{SPORTS[[s[0] for s in SPORTS].index(slug)][2]}/{sid}">OLBG hub</a>', ""),
            (str(len(d["fixtures"])), "num"), (str(len(d["high"])), "num"),
            (e(SPORT_REASON[slug]), "small"),
        ])
    body = f"""
<div class="hero"><h1>15 sports</h1><p>Each sport page carries its fixtures, picks and the specific reason for any shortfall.</p></div>
<section class="card">{table([("Sport", ""), ("OLBG ID", "num"), ("Route", ""), ("Fixtures", "num"), ("High", "num"), ("Note", "")], rows)}</section>
"""
    return page("Sports", body, "sports.html")


def sport_page(slug: str) -> str:
    name = SPORT_NAME[slug]
    d = BY_SPORT[slug]
    fx_rows = []
    for fx in d["fixtures"]:
        b = BOOKS[fx["id"]]
        w = b.get("winner")
        h = b.get("high")
        fx_rows.append([
            (f'<strong>{e(fx["home"])} v {e(fx["away"])}</strong><br><span class="small">{e(fx["comp"])}</span>', ""),
            (e(when(fx["start_utc"])), ""), (e(fx.get("start_note", "")) or "—", "small"),
            (f'{e(w["selection"])} {money(w["fair_american"])} {badge(w.get("confidence", "Low"))}' if w else "—", ""),
            (f'{e(h["selection"])} <span class="small">{money(h["fair_american"])}</span>' if h else "—", ""),
            (src_links(fx["sources"]), ""),
        ])
    preds = "".join(
        f'<article class="pred" id="{e(h["fixture"]["id"])}"><div><div class="sel">{e(h["high"]["selection"])}</div>'
        f'<div class="small">{money(h["high"]["fair_american"])} · {pct(h["high"]["probability"])}</div></div>'
        f'<div><p>{e(PREDICTIONS[h["fixture"]["id"]]["text"])}</p>'
        f'<div>{src_links(h["fixture"]["sources"])}</div></div></article>'
        for h in d["high"])
    flag_rows = [[(e(f["id"]), ""), (e(t), "")] for f in d["fixtures"] for t in f.get("flags", [])]
    body = f"""
<div class="hero"><h1>{e(name)}</h1><p>{e(SPORT_REASON[slug])}</p>
<div class="meta">{len(d['fixtures'])} fixtures · {len(d['high'])} High selections · OLBG sport ID {SPORTS[[s[0] for s in SPORTS].index(slug)][3]}</div></div>
<section class="card"><h2>Fixtures and picks</h2>
{table([("Match", ""), ("Start (UTC)", ""), ("Time note", ""), ("Winner call", ""), ("High selection", ""), ("Source", "")], fx_rows) if fx_rows else '<p>No fixture was captured for this sport.</p>'}</section>
{'<section class="card"><h2>Write-ups</h2>' + preds + '</section>' if preds else ''}
{'<section class="card"><h2>Flags on this sport</h2>' + table([("Row", ""), ("Flag", "")], flag_rows) + '</section>' if flag_rows else ''}
<p><a href="../sports.html">← All sports</a> · <a href="../picks.html">All picks</a> · <a href="../flagged.html">Review register</a></p>
"""
    return page(name, body, "sports.html", base="../")


def sources_page() -> str:
    rows = []
    for sid, s in sorted(SOURCES.items(), key=lambda kv: (kv[1]["status"] != "read", kv[1]["name"])):
        rows.append([
            (f'<strong>{e(s["name"])}</strong>', ""),
            (f'<a href="{e(s["url"])}" rel="noreferrer">{e(s["url"])}</a>', "small"),
            (e(s["read_at"]), ""),
            (f'<span class="badge {"b-ok" if s["status"] == "read" else "b-flag"}">{e(s["status"])}</span>', ""),
            (e(s["what"]), "small"),
        ])
    acc = [[(e(u), "small"), (f'<span class="badge {"b-ok" if r == "read" else "b-flag"}">{e(r)}</span>', ""), (e(w), "small")]
           for u, r, w in ACCESS_LOG]
    routes = [[(f'<strong>{e(s)}</strong>', ""), (str(i), "num"), (f'<a href="{u}">{e(u)}</a>', "small"), (e(o), "small")]
              for s, i, u, o in OLBG_ROUTES]
    body = f"""
<div class="hero"><h1>Sources</h1><p>Every page this desk opened, what it supplied, and every route that failed.</p>
<div class="meta">{SUMMARY['sources_read']} official pages read · {SUMMARY['sources_failed']} official routes failed · {len(OLBG_ROUTES)} OLBG routes mapped</div></div>
<section class="card"><h2>Source register</h2>
{table([("Source", ""), ("URL", ""), ("Read (UTC)", ""), ("Status", ""), ("What it supplied", "")], rows)}</section>
<section class="card"><h2>Access log</h2>
<p class="sub">A failed route is published here so that a blank row on another page can be traced to its cause.</p>
{table([("URL", ""), ("Result", ""), ("Note", "")], acc)}</section>
<section class="card"><h2>OLBG discovery routes</h2>
{table([("Sport", ""), ("ID", "num"), ("Route", ""), ("What the page showed", "")], routes)}</section>
"""
    return page("Sources", body, "sources.html")


def flagged_page() -> str:
    desk = "".join(
        f'<article class="pred" id="{e(a)}"><div><div class="sel">{e(a)}</div>'
        f'<div class="small">{badge("Excluded" if d == "high" else ("Medium" if d == "medium" else "Low"))} {e(d)} severity</div></div>'
        f'<div><h3 style="margin-top:0">{e(b)}</h3><p>{e(c)}</p></div></article>'
        for a, b, c, d in DESK_FLAGS)
    rowflags = [[(e(fid), ""), (e(t), "")] for fid, t in FLAGS]
    repo = [[(e(a), ""), (badge("Excluded" if b == "high" else ("Medium" if b == "medium" else "Low")), ""),
             (e(c), "small"), (e(d), ""), (e(e_), "small")] for a, b, c, d, e_, _ in REPO_FINDINGS]
    body = f"""
<div class="hero"><h1>Flagged for review</h1><p>Everything this desk could not certify, every source that failed, and every conflict between sources. Nothing here blocks publication; it tells you what to check.</p>
<div class="meta">{len(DESK_FLAGS)} desk findings · {len(FLAGS)} row flags · {len(REPO_FINDINGS)} repository findings</div></div>
<section class="card"><h2>Desk findings</h2>{desk}</section>
<section class="card"><h2>Row-level flags</h2>
{table([("Row", ""), ("Flag", "")], rowflags) if rowflags else '<p>No row-level flags.</p>'}</section>
<section class="card"><h2>Repository findings</h2>
<p class="sub">Read line by line during this session; evidence paths are given for each.</p>
{table([("ID", ""), ("Severity", ""), ("Path", ""), ("Finding", ""), ("Why it matters", "")], repo)}</section>
<section class="card"><h2>What is not on this page</h2>
<p>Matches that simply had no eligible price are <em>not</em> irregularities; they are listed with reasons on <a href="picks.html">Picks</a>. This page is for things a human should check: a source that would not load, two sources that disagree, or a quota that could not be met.</p></section>
"""
    return page("Flagged for review", body, "flagged.html")


def methodology_page() -> str:
    body = """
<div class="hero"><h1>Method</h1><p>What the numbers mean, how a line is originated, and the exact gates a pick must pass.</p></div>
<section class="card"><h2>The two gates</h2>
<p><strong>High confidence</strong> requires both conditions at once:</p>
<ul class="basis">
<li>our fair probability is greater than 70.0%;</li>
<li>the fair American price is between -250 and +10000.</li>
</ul>
<p>A fair price of -250 is 71.43%, so the two rules intersect in a 1.4-point window. In practice a High price prints between -235 and -248. Selections stronger than that are labelled <span class="badge b-exc">Excluded</span> and shown on the Picks page with the reason.</p>
<h3>What Strong, Medium and Low mean</h3>
<ul class="basis">
<li><span class="badge b-high">High</span> both gates passed, and a written analysis exists.</li>
<li><span class="badge b-med">Medium</span> chance between 60% and 70%, or stronger than the band allows.</li>
<li><span class="badge b-low">Low</span> chance below 60%.</li>
<li><span class="badge b-exc">Excluded</span> a strong favourite whose price is shorter than -250.</li>
</ul></section>
<section class="card"><h2>How a price is made</h2>
<p>Prices are zero-vig. Decimal is one divided by the probability; American is derived from decimal. No margin is added and nothing is clipped, so the probability printed on a row is exactly what the price implies.</p>
<h3>Inputs by sport</h3>
<ul class="basis">
<li><strong>NHL</strong> — points percentage from the official standings, plus goals for and against per game for the total.</li>
<li><strong>NBA</strong> — win-loss record with a four-game prior so that a 2-0 start does not imply certainty.</li>
<li><strong>Rugby Union</strong> — official league position.</li>
<li><strong>Rugby League</strong> — official group position.</li>
<li><strong>Formula 1</strong> — the five drivers classified in the session read, weighted by lap-time gap.</li>
</ul>
<h3>Line origination</h3>
<p>The handicap line is not copied from a bookmaker. It is set at the quantile where the selection's chance lands inside the brief's window, rounded to a real quarter or half line. That is why the same fixture can show a money-line pick at 58% and a High handicap pick at 70.6%: they are different selections on the same match.</p></section>
<section class="card"><h2>What we refuse to do</h2>
<ul class="basis">
<li>We do not fill a blank with a league average and call it a line.</li>
<li>We do not present a bookmaker price as our own.</li>
<li>We do not write a prediction for a row whose inputs were not read.</li>
<li>We do not treat an OLBG listing as an official fixture confirmation.</li>
</ul></section>
<section class="card"><h2>Freshness</h2>
<p>This is a snapshot, captured 2026-10-24T17:40Z. Start times move; selections do not auto-refresh. Re-check the official link on the row before acting. The desk does not publish a live price feed.</p></section>
"""
    return page("Method", body, "methodology.html")


def reverse_page() -> str:
    routes = [[(f'<strong>{e(s)}</strong>', ""), (str(i), "num"),
               (f'<a href="{u}">{e(u)}</a>', "small"), (e(o), "small")] for s, i, u, o in OLBG_ROUTES]
    body = f"""
<div class="hero"><h1>OLBG reverse-engineering map</h1><p>The 15 requested routes, their numeric IDs, the markets each page documents, and what the page actually rendered at capture time.</p>
<div class="meta">Route pattern: /betting-tips/&lt;Sport_Name&gt;/&lt;ID&gt; · captured {e(CAPTURED)}</div></div>
<section class="card"><h2>Routes and IDs</h2>
{table([("Sport", ""), ("ID", "num"), ("Route", ""), ("Observed content", "")], routes)}</section>
<section class="card"><h2>Findings that change how the data must be read</h2>
<h3>1. The clock is Eastern Time, not UK time</h3>
<p>Greyhound cards are named with the UK race time (6:01 Newcastle) but displayed as 13:01 — a seven-hour offset. NHL games at 17:00Z display as 13:07. Both are consistent with the page rendering US Eastern time. Every OLBG clock in this desk was therefore converted from ET, and converted again only where an official page gave the local time.</p>
<h3>2. Golf renders an empty board</h3>
<p>The Golf hub returns “No tips found” while still documenting outright, first-round-leader and top-region markets. This is a platform-availability fact, not evidence that no golf is being played.</p>
<h3>3. Rugby League has no match-level card</h3>
<p>The Rugby League hub shows only three 2027 outrights. The World Cup fixtures on this site come from NRL.com, not from OLBG.</p>
<h3>4. Snooker shows one match</h3>
<p>Only Mark Williams v Jak Jones appears, even though the tournament is at semi-final stage.</p>
<h3>5. The cricket card conflicts with the official fixture hub</h3>
<p>OLBG lists two CSA T20 fixtures for 25 October. Cricket South Africa's hub for the same window lists Colts three-day matches and a Pro 50 women's game. Both cannot be the same competition, so the rows are flagged.</p>
<h3>6. Listed times can be wrong by an hour across a clock change</h3>
<p>France moves from CEST to CET on 25 October. Top 14's own page shows 21:05 local for La Rochelle v Bordeaux-Bègles, which is 20:05Z; the OLBG card shows 16:05 ET, which is also 20:05Z. The two agree only once the clock change is applied. A desk that converted naively would publish 19:05Z.</p>
</section>
<section class="card"><h2>Market vocabulary by sport</h2>
{table([("Sport", ""), ("Markets OLBG documents", "")], [
 [("Ice Hockey", ""), ("Money Line, Game Totals", "")],
 [("Basketball", ""), ("Money Line, Pointspread", "")],
 [("Baseball", ""), ("Money Line, Run Line, Game Totals, Ante-post", "")],
 [("Tennis", ""), ("Win Match, Set Betting, Total Games, 1st Set Winner, Games Won handicaps", "")],
 [("Rugby Union", ""), ("To Win, Win Tournament, handicap", "")],
 [("Rugby League", ""), ("Win Tournament, Grand Final Winner", "")],
 [("Cricket", ""), ("Win Match, Draw No Bet, Top Team1 Batsman, Outright Winner", "")],
 [("Snooker", ""), ("Win Match, Handicap Betting, Frame Betting, Win Tournament", "")],
 [("Darts", ""), ("Win Match 2-way, Win Tournament", "")],
 [("Volleyball", ""), ("Win Match", "")],
 [("Handball", ""), ("Money Line", "")],
 [("Gaelic Sports", ""), ("Match winner, handicap", "")],
 [("Greyhounds", ""), ("Daily Races", "")],
 [("Motor Racing", ""), ("Fastest Qualifier, Win Race, Podium, Top 6, Points Finish, Fastest Lap, Win Tournament", "")],
 [("Golf", ""), ("Outright, Each Way, First Round Leader, Top American / European / GB & Ireland, team-event markets", "")],
])}</section>
"""
    return page("OLBG map", body, "reverse-engineering.html")


def audit_page() -> str:
    rows = [[(e(a), ""), (badge("Excluded" if b == "high" else ("Medium" if b == "medium" else "Low")), ""),
             (f'<code>{e(c)}</code>', "small"), (e(d), ""), (e(e_), "small"),
             (f'<a href="https://github.com/buffedlizard55-lab/OLBG1/blob/main/{e(f)}">evidence</a>', "small")] for a, b, c, d, e_, f in REPO_FINDINGS]
    body = f"""
<div class="hero"><h1>Repository audit</h1><p>Line-by-line checks run before this desk was published, with the evidence path for each finding.</p>
<div class="meta">{len(REPO_FINDINGS)} findings · 5 files and directories inspected · no peer desk was modified</div></div>
<section class="card"><h2>Findings</h2>
{table([("ID", ""), ("Severity", ""), ("Path", ""), ("Finding", ""), ("Why it matters", ""), ("Evidence", "")], rows)}</section>
<section class="card"><h2>Checks that passed</h2>
<ul class="basis">
<li>No unresolved git conflict markers in <code>.py</code>, <code>.html</code>, <code>.json</code> or <code>.md</code> files.</li>
<li>No tracked <code>.pyc</code> files.</li>
<li>Zero broken local links across the five main root pages, measured by resolving every relative <code>href</code>.</li>
<li>The 23 October predictions file has 51 entries with a minimum of 39 words and no occurrence of either internal term.</li>
</ul></section>
<section class="card"><h2>Scope</h2>
<p>This session wrote only to <code>data/37003e61/</code>, <code>scripts/s37003e61_*.py</code>, <code>37003e61/</code>, <code>reports/SESSION_37003E61.*</code>, <code>tests/pipeline/test_desk_37003e61.py</code> and append-only sections of <code>COORDINATION.md</code>. No canonical pipeline, root page, asset or peer desk was edited.</p></section>
"""
    return page("Repository audit", body, "repo-audit.html")


def notfound_page() -> str:
    body = """<div class="hero"><h1>Page not found</h1><p>That path is not part of this desk.</p>
<div class="meta"><a style="color:#fff;text-decoration:underline" href="index.html">Return to the executive summary</a></div></div>"""
    return page("Not found", body)


def build():
    export_data()
    OUT.mkdir(exist_ok=True)
    (OUT / "sports").mkdir(exist_ok=True)
    (OUT / "assets").mkdir(exist_ok=True)
    (OUT / "assets" / "style.css").write_text(CSS)
    (OUT / "index.html").write_text(index_page())
    (OUT / "picks.html").write_text(picks_page())
    (OUT / "predictions.html").write_text(predictions_page())
    (OUT / "matches.html").write_text(matches_page())
    (OUT / "markets.html").write_text(markets_page())
    (OUT / "sports.html").write_text(sports_page())
    (OUT / "sources.html").write_text(sources_page())
    (OUT / "flagged.html").write_text(flagged_page())
    (OUT / "methodology.html").write_text(methodology_page())
    (OUT / "reverse-engineering.html").write_text(reverse_page())
    (OUT / "repo-audit.html").write_text(audit_page())
    (OUT / "404.html").write_text(notfound_page())
    for slug, _, _, _ in SPORTS:
        (OUT / "sports" / f"{slug}.html").write_text(sport_page(slug))
    print(f"built {len(list(OUT.rglob('*.html')))} pages; "
          f"{SUMMARY['fixtures']} fixtures; {SUMMARY['high']} High picks")


if __name__ == "__main__":
    build()
