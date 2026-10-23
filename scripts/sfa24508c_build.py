#!/usr/bin/env python3
"""Session fa24508c-olbg1 — line origination, confidence grading and site build.

Run:  python3 scripts/sfa24508c_build.py
Writes data/fa24508c/desk.json and the whole /fa24508c/ dashboard.
No network access.  Every number below is computed from a value read from an
official publisher and recorded in scripts/sfa24508c_data.py.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import sfa24508c_data as DATA

ROOT = Path(__file__).resolve().parent.parent
DESK = ROOT / "fa24508c"
DATA_DIR = ROOT / "data" / "fa24508c"

SPORTS = [
    ("Golf", "golf"),
    ("Volleyball", "volleyball"),
    ("Rugby Union", "rugby-union"),
    ("Cricket", "cricket"),
    ("Snooker", "snooker"),
    ("Darts", "darts"),
    ("Baseball", "baseball"),
    ("Gaelic Sports", "gaelic-sports"),
    ("Greyhounds", "greyhounds"),
    ("Tennis", "tennis"),
    ("Motor Racing", "motor-racing"),
    ("Handball", "handball"),
    ("Ice Hockey", "ice-hockey"),
    ("Basketball", "basketball"),
    ("Rugby League", "rugby-league"),
]
SLUG = dict(SPORTS)


# --------------------------------------------------------------------------
# maths
# --------------------------------------------------------------------------
def american(decimal: float) -> int:
    if decimal >= 2.0:
        return int(round((decimal - 1.0) * 100))
    return int(round(-100.0 / (decimal - 1.0)))


def fmt_am(dec: float) -> str:
    a = american(dec)
    return f"+{a}" if a > 0 else str(a)


def poisson_pmf(k: int, lam: float) -> float:
    return math.exp(-lam) * lam ** k / math.factorial(k)


def poisson_cdf(k: int, lam: float) -> float:
    return sum(poisson_pmf(i, lam) for i in range(0, k + 1))


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def log5(pa: float, pb: float) -> float:
    return (pa - pa * pb) / (pa + pb - 2 * pa * pb)


def shrink(w: int, n: int) -> float:
    """Beta(2,2) shrinkage, as disclosed on the methodology page."""
    return (w + 2.0) / (n + 4.0)


def tier(p: float) -> str:
    if p >= 0.70:
        return "High"
    if p >= 0.60:
        return "Medium"
    return "Low"


def in_band(dec: float) -> bool:
    return 1.40 - 1e-9 <= dec <= 101.0 + 1e-9


# --------------------------------------------------------------------------
# model
# --------------------------------------------------------------------------
MARKETS = []      # every originated market row
FIXTURES = {}     # id -> enriched fixture


def add_market(fid, market, selection, p, basis, note=None):
    dec = 1.0 / p
    MARKETS.append({
        "fixture_id": fid, "market": market, "selection": selection,
        "p": round(p, 6), "decimal": round(dec, 4), "american": american(dec),
        "american_display": fmt_am(dec), "confidence": tier(p),
        "in_band": in_band(dec), "basis": basis, "note": note,
    })


def build_model():
    # ---- MLB -------------------------------------------------------------
    tb, mil = DATA.MLB["TB"], DATA.MLB["MIL"]
    n = 162.0
    p_mil = shrink(mil["w"], mil["w"] + mil["l"])
    p_tb = shrink(tb["w"], tb["w"] + tb["l"])
    p_home = log5(p_mil, p_tb)
    f = "BB-001"
    FIXTURES[f] = dict(next(x for x in DATA.VERIFIED if x["id"] == f))
    add_market(f, "Money Line", "Milwaukee Brewers", p_home,
               "log5 on Beta(2,2)-shrunk 162-game records (MIL .633 vs TB .602)")
    add_market(f, "Money Line", "Tampa Bay Rays", 1 - p_home,
               "complement of the Brewers price (no margin applied)")
    lam_h = (mil["rs"] / n + tb["ra"] / n) / 2
    lam_a = (tb["rs"] / n + mil["ra"] / n) / 2
    total = lam_h + lam_a
    line = 8.5
    p_over = 1.0 - poisson_cdf(int(line), total)
    add_market(f, "Game Total 8.5 (model line)", "Over 8.5 runs", p_over,
               f"independent Poisson, λ MIL {lam_h:.2f} + TB {lam_a:.2f} = {total:.2f}; not pitcher-adjusted")
    add_market(f, "Game Total 8.5 (model line)", "Under 8.5 runs", 1 - p_over,
               "complement of the Over price")
    p_hw2 = 0.0
    for a in range(0, 16):
        for b in range(0, 16):
            if a - b >= 2:
                p_hw2 += poisson_pmf(a, lam_h) * poisson_pmf(b, lam_a)
    add_market(f, "Run Line (model line)", "Milwaukee −1.5", p_hw2,
               "independent Poisson margin distribution; model line, not a quoted handicap")
    add_market(f, "Run Line (model line)", "Tampa Bay +1.5", 1 - p_hw2,
               "complement of the −1.5 price")
    FIXTURES[f]["derived"] = {"lam_home": round(lam_h, 3), "lam_away": round(lam_a, 3),
                              "total_mean": round(total, 3)}

    # ---- NHL -------------------------------------------------------------
    for fid, home, away, game in [
        ("IH-001", "CHI", "MTL", "2026020166"),
        ("IH-002", "COL", "TBL", "2026020167"),
    ]:
        FIXTURES[fid] = dict(next(x for x in DATA.VERIFIED if x["id"] == fid))
        h, a = DATA.NHL[home], DATA.NHL[away]
        ph = shrink(h["w"], h["gp"])
        pa = shrink(a["w"], a["gp"])
        p_home = log5(ph, pa)
        label_h = FIXTURES[fid]["home"]
        label_a = FIXTURES[fid]["away"]
        note = "OT and shootout defeats counted as defeats; beta(2,2) shrinkage over a 9-10 game sample."
        add_market(fid, "Money Line", label_h, p_home, note)
        add_market(fid, "Money Line", label_a, 1 - p_home, note)
        lam_h = (h["gf"] / h["gp"] + a["ga"] / a["gp"]) / 2
        lam_a = (a["gf"] / a["gp"] + h["ga"] / h["gp"]) / 2
        total = lam_h + lam_a
        line = 6.5
        p_over = 1.0 - poisson_cdf(int(line), total)
        add_market(fid, "Game Total 6.5 (model line)", "Over 6.5 goals", p_over,
                   f"independent Poisson, λ {lam_h:.2f} + {lam_a:.2f} = {total:.2f}")
        add_market(fid, "Game Total 6.5 (model line)", "Under 6.5 goals", 1 - p_over,
                   "complement of the Over price")
        fav_p = max(p_home, 1 - p_home)
        fav = label_h if p_home >= 0.5 else label_a
        p_puck = 0.0
        for x in range(0, 16):
            for y in range(0, 16):
                if (x - y) >= 2:
                    p_puck += poisson_pmf(x, lam_h) * poisson_pmf(y, lam_a)
        if fav == label_a:
            p_puck = 1 - (p_puck + sum(poisson_pmf(a_, lam_h) * poisson_pmf(b_, lam_a)
                                       for a_ in range(0, 16) for b_ in range(0, 16)
                                       if a_ - b_ == 1) + sum(poisson_pmf(a_, lam_h) * poisson_pmf(b_, lam_a)
                                                              for a_ in range(0, 16) for b_ in range(0, 16)
                                                              if a_ == b_))
        add_market(fid, "Puck Line −1.5 (model line)", f"{fav} −1.5", p_puck,
                   "Poisson margin distribution; model line, not a quoted handicap")
        FIXTURES[fid]["derived"] = {"lam_home": round(lam_h, 3), "lam_away": round(lam_a, 3),
                                    "total_mean": round(total, 3), "game_id": game}

    # ---- NBA (prior-driven, disclosed) -----------------------------------
    for fid, home, away, game in DATA.NBA_GAMES:
        FIXTURES[fid] = dict(next(x for x in DATA.VERIFIED if x["id"] == fid))
        add_market(fid, "Money Line (prior-driven)", home, 0.55,
                   "single disclosed league-average home prior (0.55); no team-specific input exists after one game")
        add_market(fid, "Money Line (prior-driven)", away, 0.45,
                   "complement of the home prior")

    # ---- Rugby Union -----------------------------------------------------
    team_margins = {}
    matches = {}
    for rnd, rows in DATA.URC_RESULTS.items():
        for (h, a, hs, as_) in rows:
            team_margins.setdefault(h, []).append(hs - as_)
            team_margins.setdefault(a, []).append(as_ - hs)
            matches.setdefault((h, a), []).append(f"{h} {hs}-{as_} {a} (R{rnd})")
    def strength(team):
        vals = team_margins.get(team, [])
        if not vals:
            return None, 0
        raw = sum(vals) / len(vals)
        return raw * len(vals) / (len(vals) + 4.0), len(vals)   # n/(n+4) shrinkage

    SIGMA = 13.0
    for fid, home, away in [
        ("RU-001", "Cardiff", "Sharks"),
        ("RU-002", "Connacht", "Zebre"),
        ("RU-003", "Edinburgh", "Lions"),
        ("RU-004", "Bulls", "Ulster"),
        ("RU-005", "Stormers", "Scarlets"),
    ]:
        FIXTURES[fid] = dict(next(x for x in DATA.VERIFIED if x["id"] == fid))
        sh, nh = strength(home)
        sa, na = strength(away)
        if sh is None or sa is None:
            continue
        edge = sh - sa
        p_home = norm_cdf(edge / SIGMA)
        note = (f"shrunk mean points margin from the {nh} matches read for {home} and {na} for {away}; "
                f"normal distribution with σ={SIGMA:.0f} points")
        add_market(fid, "Match Winner", FIXTURES[fid]["home"], p_home, note)
        add_market(fid, "Match Winner", FIXTURES[fid]["away"], 1 - p_home, note)
        hcap = round(edge * 2) / 2.0
        if hcap == 0:
            hcap = -0.5
        p_cover = norm_cdf((edge - hcap) / SIGMA)
        add_market(fid, f"Handicap {-hcap:+.1f} (model line)",
                   f"{FIXTURES[fid]['home']} {-hcap:+.1f}", p_cover,
                   "handicap set at our own expected margin; cover probability from the same normal model")
        add_market(fid, f"Handicap {-hcap:+.1f} (model line)",
                   f"{FIXTURES[fid]['away']} {hcap:+.1f}", 1 - p_cover,
                   "complement of the home handicap price")
        FIXTURES[fid]["derived"] = {
            "edge_points": round(edge, 2),
            "sample": {"home": nh, "away": na},
            "margin_home_raw": round(team_margins[home] and sum(team_margins[home]) / len(team_margins[home]), 2),
            "margin_away_raw": round(team_margins[away] and sum(team_margins[away]) / len(team_margins[away]), 2),
            "handicap": hcap,
        }

    # ---- Snooker / Motor racing: verified fixtures, no price -------------
    for fid in ("SN-001", "SN-002", "MR-001"):
        FIXTURES[fid] = dict(next(x for x in DATA.VERIFIED if x["id"] == fid))

    for m in MARKETS:
        m["fixture"] = FIXTURES[m["fixture_id"]]["home"] + " v " + FIXTURES[m["fixture_id"]]["away"]
        m["sport"] = FIXTURES[m["fixture_id"]]["sport"]


# --------------------------------------------------------------------------
# HTML
# --------------------------------------------------------------------------
CSS = """
:root{--bg:#0b1020;--panel:#131a2e;--panel2:#18213a;--line:#25324f;--ink:#e8eefc;--muted:#9aa8c7;
--accent:#5b9dff;--good:#38c172;--warn:#e3a008;--bad:#ef5b5b;--hi:#7c5cff}
*{box-sizing:border-box}
body{margin:0;font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
background:var(--bg);color:var(--ink)}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
header.top{position:sticky;top:0;z-index:10;background:rgba(11,16,32,.95);border-bottom:1px solid var(--line);
backdrop-filter:blur(6px)}
.wrap{max-width:1180px;margin:0 auto;padding:0 18px}
.bar{display:flex;flex-wrap:wrap;gap:6px;align-items:center;padding:10px 0}
.brand{font-weight:700;letter-spacing:.3px;margin-right:14px;color:#fff}
.brand span{color:var(--accent)}
nav a{padding:6px 10px;border-radius:8px;color:var(--muted);font-size:14px}
nav a:hover{background:var(--panel2);color:#fff;text-decoration:none}
nav a.on{background:var(--panel2);color:#fff}
main{padding:26px 0 60px}
h1{font-size:28px;margin:0 0 6px;letter-spacing:-.3px}
h2{font-size:19px;margin:30px 0 10px}
h3{font-size:15px;margin:20px 0 8px;color:var(--muted);text-transform:uppercase;letter-spacing:.7px}
p.lede{color:var(--muted);margin:0 0 18px;max-width:900px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:18px 0 8px}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px}
.kpi b{display:block;font-size:24px;line-height:1.1}
.kpi span{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.6px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px;margin:12px 0}
table{width:100%;border-collapse:collapse;font-size:13.5px}
th,td{text-align:left;padding:8px 9px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--muted);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.5px;
position:sticky;top:44px;background:var(--panel)}
tbody tr:hover{background:var(--panel2)}
.scroll{overflow-x:auto;border:1px solid var(--line);border-radius:12px}
.tag{display:inline-block;padding:1px 7px;border-radius:999px;font-size:11px;font-weight:600;
letter-spacing:.3px;border:1px solid var(--line)}
.tag.high{background:rgba(124,92,255,.18);border-color:#7c5cff;color:#cfc4ff}
.tag.medium{background:rgba(227,160,8,.15);border-color:#e3a008;color:#ffd98a}
.tag.low{background:rgba(154,168,199,.12);color:#c3cde6}
.tag.ok{background:rgba(56,193,114,.14);border-color:#38c172;color:#9ff0c0}
.tag.no{background:rgba(239,91,91,.14);border-color:#ef5b5b;color:#ffb3b3}
.num{font-variant-numeric:tabular-nums}
.muted{color:var(--muted)}
.small{font-size:12.5px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px}
@media(max-width:820px){.grid2{grid-template-columns:1fr}}
.pred{border-left:3px solid var(--hi);background:var(--panel);border-radius:0 12px 12px 0;padding:14px 16px;margin:14px 0}
.pred blockquote{margin:8px 0 0;padding:0;font-size:14.5px}
.pred .meta{color:var(--muted);font-size:12.5px}
footer{border-top:1px solid var(--line);color:var(--muted);font-size:12.5px;padding:18px 0 40px}
footer a{color:var(--muted)}
.note{background:var(--panel2);border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin:12px 0}
.warn{border-left:3px solid var(--warn)}
.bad{border-left:3px solid var(--bad)}
code{background:#0e1526;padding:1px 5px;border-radius:5px;font-size:12.5px}
"""

NAV = [
    ("index.html", "Overview"),
    ("matches.html", "Matches"),
    ("markets.html", "Markets"),
    ("high-confidence.html", "High confidence"),
    ("predictions.html", "Predictions"),
    ("analysis.html", "Analysis"),
    ("flagged.html", "Flagged for review"),
    ("sources.html", "Sources"),
    ("methodology.html", "Methodology"),
]


def page(title, current, body, root=""):
    nav = "".join(
        f'<a class="{"on" if href == current else ""}" href="{root}{href}">{label}</a>'
        for href, label in NAV
    )
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · OLBG 15-sport desk · 23 Oct 2026</title>
<style>{CSS}</style></head>
<body>
<header class="top"><div class="wrap"><div class="bar">
<div class="brand">OLBG<span>·</span>desk <span style="font-weight:400;color:#9aa8c7">23 Oct 2026</span></div>
<nav>{nav}</nav></div></div></header>
<main><div class="wrap">{body}</div></main>
<footer><div class="wrap">
<p>Session <code>fa24508c-olbg1</code> · 15 covered sports · observation window
{SESSION_WINDOW} UTC. This is a research dashboard, not betting advice. OLBG is used for event discovery only and is
not an official source for any sporting fact. Every price here is an independent estimate, not a bookmaker quote.</p>
<p><a href="{root}index.html">Desk overview</a> · <a href="{root}flagged.html">Flagged for review</a> ·
<a href="/OLBG1/archive.html">All desks</a></p>
</div></footer></body></html>"""


SESSION_WINDOW = f"{DATA.SESSION['window_start_utc']} – {DATA.SESSION['window_end_utc']}"


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# --------------------------------------------------------------------------
# derived stats
# --------------------------------------------------------------------------
def stats():
    by_sport = {}
    for s, slug in SPORTS:
        by_sport[s] = {
            "discovered": sum(1 for d in DATA.D if d["sport"] == s),
            "verified": sum(1 for f in FIXTURES.values() if f["sport"] == s),
            "markets": sum(1 for m in MARKETS if m["sport"] == s),
            "high": sum(1 for m in MARKETS if m["sport"] == s and m["confidence"] == "High"),
            "medium": sum(1 for m in MARKETS if m["sport"] == s and m["confidence"] == "Medium"),
            "low": sum(1 for m in MARKETS if m["sport"] == s and m["confidence"] == "Low"),
            "preds": sum(1 for p in DATA.PREDICTIONS
                         if FIXTURES[p["fixture_id"]]["sport"] == s),
        }
    return by_sport


def write_json():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "session": DATA.SESSION,
        "sports": [{"name": s, "slug": slug} for s, slug in SPORTS],
        "sources": DATA.SOURCES,
        "discovery": DATA.D,
        "fixtures": list(FIXTURES.values()),
        "markets": MARKETS,
        "predictions": DATA.PREDICTIONS,
        "flags": DATA.FLAGS,
        "counts": {
            "discovered": len(DATA.D),
            "verified_fixtures": len(FIXTURES),
            "markets": len(MARKETS),
            "high": sum(1 for m in MARKETS if m["confidence"] == "High"),
            "medium": sum(1 for m in MARKETS if m["confidence"] == "Medium"),
            "low": sum(1 for m in MARKETS if m["confidence"] == "Low"),
            "high_in_band": sum(1 for m in MARKETS if m["confidence"] == "High" and m["in_band"]),
            "predictions": len(DATA.PREDICTIONS),
            "flags": len(DATA.FLAGS),
        },
    }
    (DATA_DIR / "desk.json").write_text(json.dumps(payload, indent=2) + "\n")


def write_site():
    S = stats()
    counts = {
        "discovered": len(DATA.D),
        "verified": len(FIXTURES),
        "markets": len(MARKETS),
        "high": sum(1 for m in MARKETS if m["confidence"] == "High"),
        "medium": sum(1 for m in MARKETS if m["confidence"] == "Medium"),
        "low": sum(1 for m in MARKETS if m["confidence"] == "Low"),
        "in_band": sum(1 for m in MARKETS if m["confidence"] == "High" and m["in_band"]),
        "preds": len(DATA.PREDICTIONS),
        "flags": len(DATA.FLAGS),
        "sources": len(DATA.SOURCES),
    }
    (DESK / "sports").mkdir(parents=True, exist_ok=True)

    # ---------- index ----------
    hi = [m for m in MARKETS if m["confidence"] == "High"]
    hi.sort(key=lambda m: -m["p"])
    rows = "".join(
        f"<tr><td>{esc(m['fixture'])}</td><td>{esc(m['selection'])}</td>"
        f"<td class='num'>{m['p']*100:.1f}%</td><td class='num'>{esc(m['american_display'])}</td>"
        f"<td>{'in band' if m['in_band'] else '<span class=muted>outside −250 cap</span>'}</td></tr>"
        for m in hi
    )
    coverage = "".join(
        f"<tr><td><a href='sports/{slug}.html'>{esc(s)}</a></td>"
        f"<td class='num'>{S[s]['discovered']}</td>"
        f"<td class='num'>{S[s]['verified']}</td>"
        f"<td class='num'>{S[s]['markets']}</td>"
        f"<td class='num'>{S[s]['high']}</td>"
        f"<td class='num'>{S[s]['medium']}</td>"
        f"<td class='num'>{S[s]['preds']}</td>"
        f"<td class='num'>{S[s]['high']} / 5</td>"
        f"<td>{'<span class=tag ok>official fixture</span>' if S[s]['verified'] else '<span class=tag no>discovery only</span>'}</td></tr>"
        for s, slug in SPORTS
    )
    index = f"""
<h1>Executive summary — 23 October 2026</h1>
<p class="lede">Fifteen covered sports, harvested from the OLBG hubs inside a
{SESSION_WINDOW} UTC window, then checked line by line against the league, tour or governing body
that actually publishes the fixture. Five sports, plus the Formula 1 race weekend, survived that check. The rest
are listed with every official field blank and a stated reason.</p>
<div class="kpis">
  <div class="kpi"><b>{counts['discovered']}</b><span>OLBG events found</span></div>
  <div class="kpi"><b>{counts['verified']}</b><span>Officially verified fixtures</span></div>
  <div class="kpi"><b>{counts['markets']}</b><span>Originated prices</span></div>
  <div class="kpi"><b>{counts['high']}</b><span>High confidence</span></div>
  <div class="kpi"><b>{counts['in_band']}</b><span>High, inside −250…+10000</span></div>
  <div class="kpi"><b>{counts['preds']}</b><span>Written predictions</span></div>
  <div class="kpi"><b>{counts['flags']}</b><span>Flagged items</span></div>
</div>

<div class="note warn"><b>Read this before the picks.</b> The brief asks for selections at 70%+ probability
<i>and</i> at odds between −250 and +10000. Those two rules barely intersect: −250 already implies 71.4%,
so the permitted window for a High pick is 70.0%–71.4%. This desk applies both rules literally. Nothing
this window lands inside that 1.4-point window, so {counts['high']} High selections are published below
in a clearly marked out-of-band ledger, with their true prices, rather than being relabelled to fit.
See <a href="flagged.html#F-13">F-13</a>.</div>

<h2>Highest-confidence selections found today</h2>
<div class="scroll"><table>
<thead><tr><th>Fixture</th><th>Selection</th><th>Our probability</th><th>Fair price</th><th>Band</th></tr></thead>
<tbody>{rows}</tbody></table></div>
<p class="small muted">Fair price = 1 ÷ our probability, with no margin. These are our own lines; they are not
bookmaker quotes and no bookmaker price was read.</p>

<h2>Coverage by sport</h2>
<div class="scroll"><table>
<thead><tr><th>Sport</th><th>OLBG events</th><th>Verified fixtures</th><th>Prices</th>
<th>High</th><th>Medium</th><th>Write-ups</th><th>High target</th><th>Fixture evidence</th></tr></thead>
<tbody>{coverage}</tbody></table></div>
<p class="small muted">A verified fixture means the match, its participants and its published start were read on the
organiser's own site during the window. It does not mean the rest of the sport is covered.</p>

<h2>What is genuinely new today</h2>
<div class="grid2">
<div class="card"><h3 style="margin-top:0">Confirmed today</h3>
<ul class="small">
<li>MLB World Series Game 1 is Tampa Bay at Milwaukee, 2026-10-24T00:00Z, American Family Field, game 849805, with <code>ifNecessary=N</code>.</li>
<li>The NHL plays two games tonight, and the league's own feed publishes de-vigged-eable quotes for both.</li>
<li>URC Round 4 has three Friday fixtures, all 14:45 local, including an unbeaten Edinburgh hosting a Lions side beaten 57-15 in round three.</li>
<li>The Northern Ireland Open quarter-finals are Jak Jones v Scott Donaldson and David Gilbert v Mark Williams, 14:00.</li>
<li>The United States Grand Prix race is Sunday 25 October, 16:00 track time, 56 laps at COTA.</li>
</ul></div>
<div class="card"><h3 style="margin-top:0">Confirmed absent</h3>
<ul class="small">
<li>Golf: the OLBG hub returned "No tips found" — no fixtures to price.</li>
<li>Rugby league: only 2027 outright markets, no matches.</li>
<li>Darts, tennis, handball, volleyball, greyhounds, Gaelic: events exist on OLBG, but their governing bodies could not be read, so nothing was priced.</li>
</ul></div>
</div>
"""
    (DESK / "index.html").write_text(page("Overview", "index.html", index))

    # ---------- matches ----------
    vrows = []
    for f in sorted(FIXTURES.values(), key=lambda x: (x["sport"], x["id"])):
        links = " ".join(
            f"<a href='{u}'>{i+1}</a>" for i, u in enumerate([f["official_url"]] + f["extra_urls"])
        )
        vrows.append(
            f"<tr><td>{esc(f['sport'])}</td><td>{esc(f['competition'])}</td>"
            f"<td><b>{esc(f['home'])}</b> v <b>{esc(f['away'])}</b></td>"
            f"<td>{esc(f['start_utc'] or '')}</td>"
            f"<td>{esc(f['start_local'])}</td><td>{esc(f['venue'] or '')}</td>"
            f"<td><span class='tag ok'>verified</span></td><td class='num'>{links}</td></tr>"
        )
    drows = "".join(
        f"<tr><td>{esc(d['sport'])}</td><td>{esc(d['competition'])}</td><td>{esc(d['label'])}</td>"
        f"<td>{esc(d['olbg_start'])}</td><td>{esc(d['selection'] or '')}</td>"
        f"<td>{esc(d['market'])}</td>"
        f"<td class='num'>{'' if d['tip_share'] is None else str(d['tip_share']) + '%'}</td>"
        f"<td><span class='tag no'>unverified</span></td>"
        f"<td><a href='{d['url']}'>OLBG</a></td></tr>"
        for d in DATA.D
    )
    matches = f"""
<h1>Match and event list</h1>
<p class="lede">Two tables. The first contains only fixtures whose participants, start and venue were read on an
official publisher. The second is the raw OLBG discovery list — useful for knowing what exists, useless as evidence,
because OLBG's row is a tipster-led listing, not a governing-body record.</p>
<h2>Officially verified fixtures ({len(FIXTURES)})</h2>
<div class="scroll"><table>
<thead><tr><th>Sport</th><th>Competition</th><th>Fixture</th><th>Start (UTC)</th><th>Start (source)</th>
<th>Venue</th><th>Status</th><th>Source</th></tr></thead>
<tbody>{''.join(vrows)}</tbody></table></div>
<p class="small muted">Blank UTC cells mean the official page printed a local time with no offset. We do not guess
offsets; the source's own wording is kept in the next column. Links are numbered in the order of the source list on
the <a href="sources.html">Sources</a> page.</p>

<h2>OLBG discovery list ({len(DATA.D)} events)</h2>
<div class="scroll"><table>
<thead><tr><th>Sport</th><th>Competition as listed</th><th>Event</th><th>OLBG time</th>
<th>Most-tipped selection</th><th>Market</th><th>Tip share</th><th>Evidence</th><th>Link</th></tr></thead>
<tbody>{drows}</tbody></table></div>
<p class="small muted">Tip share is the percentage of that market's community tips on the selection. It is a
crowd vote, not a probability, and is never used as one in this desk.</p>
"""
    (DESK / "matches.html").write_text(page("Matches", "matches.html", matches))

    # ---------- markets ----------
    mrows = ""
    for m in sorted(MARKETS, key=lambda x: (x["sport"], x["fixture_id"], -x["p"])):
        cls = m["confidence"].lower()
        mrows += (
            f"<tr><td>{esc(m['sport'])}</td><td>{esc(m['fixture'])}</td><td>{esc(m['market'])}</td>"
            f"<td>{esc(m['selection'])}</td><td class='num'>{m['p']*100:.1f}%</td>"
            f"<td class='num'>{m['decimal']:.3f}</td><td class='num'>{esc(m['american_display'])}</td>"
            f"<td><span class='tag {cls}'>{m['confidence']}</span></td>"
            f"<td class='num'>{'yes' if m['in_band'] else 'no'}</td>"
            f"<td class='small muted'>{esc(m['basis'])}</td></tr>"
        )
    markets = f"""
<h1>Markets explorer — every price we originated</h1>
<p class="lede">One row per selection. Winner markets, handicaps and totals are all here, including the model lines
that no bookmaker publishes. Probability comes from a stated calculation; the price is simply 1 ÷ probability, so
every row is margin-free by construction.</p>
<div class="scroll"><table>
<thead><tr><th>Sport</th><th>Fixture</th><th>Market</th><th>Selection</th><th>Probability</th>
<th>Decimal</th><th>American</th><th>Confidence</th><th>In band</th><th>Basis</th></tr></thead>
<tbody>{mrows}</tbody></table></div>
<h2>How to read the confidence column</h2>
<div class="card">
<p><b>High</b> — our probability is 70% or more. <b>Medium</b> — 60% to 69.9%. <b>Low</b> — below 60%.</p>
<p class="small muted">Confidence describes the size of our number, not how much we trust the sample. Sample sizes
are printed in the basis column; a 70% estimate built on two matches is still a 70% estimate built on two matches,
which is why every sample size is disclosed rather than hidden behind the label.</p>
</div>
"""
    (DESK / "markets.html").write_text(page("Markets", "markets.html", markets))

    # ---------- high confidence ----------
    out_band = [m for m in hi if not m["in_band"]]
    near = [m for m in MARKETS if 0.65 <= m["p"] < 0.70]
    near.sort(key=lambda m: -m["p"])
    ob = "".join(
        f"<tr><td>{esc(m['fixture'])}</td><td>{esc(m['selection'])}</td>"
        f"<td class='num'>{m['p']*100:.1f}%</td><td class='num'>{esc(m['american_display'])}</td>"
        f"<td>{esc(m['basis'])}</td></tr>" for m in out_band)
    nr = "".join(
        f"<tr><td>{esc(m['fixture'])}</td><td>{esc(m['selection'])}</td>"
        f"<td class='num'>{m['p']*100:.1f}%</td><td class='num'>{esc(m['american_display'])}</td>"
        f"<td>{esc(m['basis'])}</td></tr>" for m in near)
    hc = f"""
<h1>High confidence</h1>
<p class="lede">The brief's rule, applied literally: probability at 70% or above <i>and</i> a price between −250 and
+10000. Both conditions are checked on every row below.</p>
<div class="kpis">
  <div class="kpi"><b>{counts['high']}</b><span>High (p ≥ 70%)</span></div>
  <div class="kpi"><b>{counts['in_band']}</b><span>Also inside the band</span></div>
  <div class="kpi"><b>{len(near)}</b><span>Near-miss watchlist</span></div>
</div>
<div class="note bad"><b>Zero High selections are inside the band today, and that is an arithmetic result, not an
omission.</b> A price of −250 is 71.4%; a price of −233 is 70.0%. Requiring p ≥ 70% therefore restricts the band to
70.0%–71.4%. Our two High selections — Edinburgh at 79.1% and Vodacom Bulls at 85.0% — are far above 70% and are
correspondingly priced shorter than −250. Relabelling them, or shaving their probability to fit the band, would be
fabrication. They are published below as a disclosed out-of-band ledger. See <a href="flagged.html#F-13">F-13</a>.</div>

<h2>High selections, outside the −250 cap (disclosed)</h2>
<div class="scroll"><table>
<thead><tr><th>Fixture</th><th>Selection</th><th>Probability</th><th>Our price</th><th>Basis</th></tr></thead>
<tbody>{ob}</tbody></table></div>

<h2>Near-miss watchlist (65%–69.9%)</h2>
<p class="small muted">Selections that would enter the 70%+ tier with any further evidence in their favour. They are
not High and no prediction was written for them.</p>
<div class="scroll"><table>
<thead><tr><th>Fixture</th><th>Selection</th><th>Probability</th><th>Our price</th><th>Basis</th></tr></thead>
<tbody>{nr}</tbody></table></div>
"""
    (DESK / "high-confidence.html").write_text(page("High confidence", "high-confidence.html", hc))

    # ---------- predictions ----------
    preds_html = ""
    for p in DATA.PREDICTIONS:
        f = FIXTURES[p["fixture_id"]]
        wc = len(p["body"].split())
        preds_html += f"""
<div class="pred">
<div class="meta">{esc(f['sport'])} · {esc(f['competition'])} · {esc(f['home'])} v {esc(f['away'])}
· {esc(f['start_local'])} · <span class="tag {p['confidence'].lower()}">{p['confidence']}</span></div>
<h3 style="margin:8px 0 4px;color:#fff;text-transform:none;letter-spacing:0;font-size:16px">{esc(p['selection'])}</h3>
<blockquote>{esc(p['body'])}</blockquote>
<div class="meta" style="margin-top:10px">{wc} words · our price {esc(p['price'])} ·
probability {p['probability']*100:.1f}% ·
evidence <a href="{f['official_url']}">{esc(f['official_url'].split('/')[2])}</a>
{' · '.join(f"<a href='{u}'>{esc(u.split('/')[2])}</a>" for u in f['extra_urls'])}</div>
</div>"""
    pred_page = f"""
<h1>Written predictions</h1>
<p class="lede">Five selections, each at least thirty words, each naming the competition, the participants, the
selection and the specific results that support it. Every factual clause traces to a page read in this window and
linked beneath the write-up. No two write-ups share a structure or a sentence.</p>
{preds_html}
<div class="note"><b>Why only five?</b> Write-ups are attached to selections that clear the High bar and to the
strongest Medium selections. Twelve NBA games, two snooker quarter-finals and the United States Grand Prix were
verified but produced no selection worth a written argument, so none was written. The target of five per sport
(seventy-five in total) is not met and could not be met honestly from today's verified evidence; per-sport shortfalls
are listed on each sport page.</div>
"""
    (DESK / "predictions.html").write_text(page("Predictions", "predictions.html", pred_page))

    # ---------- analysis ----------
    analysis = f"""
<h1>Analysis</h1>
<p class="lede">What today's numbers actually show, including the parts that do not flatter the desk.</p>

<h2>1. The band rule and the probability rule point in opposite directions</h2>
<div class="card">
<p>Converting the brief's odds window to probabilities: −250 = 71.4%, +10000 = 0.99%. A 70% minimum therefore leaves
a sliver of 1.4 percentage points. In practice a genuine 70%–71.4% favourite is a coin-flip-plus-a-nudge, exactly the
price range where bookmakers hold their margin and where our own estimate is least distinguishable from the market.
Today we found two selections above 70% and both are far above it, so both fall outside the cap.</p>
<p class="small muted">This is worth a decision from the desk owner: either the band is a display preference (publish
picks at any price and show the band), or the 70% rule is a preference (publish ≥70% and ignore the cap). Keeping both
as hard filters produces an empty set most days.</p>
</div>

<h2>2. Where our number and the market disagree</h2>
<div class="card">
<p><b>Tampa Bay @ Colorado.</b> Our record-based estimate gives Tampa Bay 69.2%; the NHL's own published quotes
de-vig to about 46.4% for the same team. The gap is 22.8 points. Two readings are on the table: the Lightning are
7-2-0 and the Avalanche 5-4-1, but Colorado have outscored opponents 41-31 while Tampa Bay's goal difference is only
+8, and the market is reacting to underlying play rather than the win column. We publish the disagreement instead of
picking a winner between the two.</p>
</div>

<h2>3. Sample sizes are the real limit on confidence</h2>
<div class="card">
<p>URC form is built on two or three matches per club. Our margins are shrunk by n ÷ (n+4) precisely because two
matches is not evidence of a season-long level; a club that has played two matches keeps only a third of its raw
margin. MLB, by contrast, is built on 162 games, which is why the Brewers' 103-59 record moves their price and a
9-game NHL record barely does.</p>
</div>

<h2>4. What the discovery layer cannot do</h2>
<div class="card">
<p>Nine of fifteen sports failed verification. In every case the failure was mechanical, not judgemental: a consent
wall on pdc.tv, a client-rendered scores page on atptour.com, a 404 on the GBGB race card, an empty tip list for golf,
outright-only markets for rugby league. Publishing prices for those events would have meant inventing the inputs.
They are listed, blank, and flagged.</p>
</div>

<h2>5. Reading the two High selections carefully</h2>
<div class="card">
<p><b>Edinburgh (79.1%).</b> Three wins from three, including a 29-12 win in Parma. The Lions' 57-15 defeat at Loftus
is the single largest margin conceded by any side in the matches we read. The caveat is that the Lions' round-two
result was not captured, so their number rests on two matches.</p>
<p><b>Vodacom Bulls (85.0%).</b> Two matches, 104 points scored, 28 conceded. Ulster's draw with Munster is the only
league point they have taken. The caveat is the sample: two matches, and the shrinkage factor n ÷ (n+4) keeps only a
third of the raw margin precisely because two matches is thin.</p>
</div>
"""
    (DESK / "analysis.html").write_text(page("Analysis", "analysis.html", analysis))

    # ---------- flagged ----------
    frows = ""
    for f in DATA.FLAGS:
        sev = f["severity"]
        tagcls = "no" if sev == "high" else ("medium" if sev == "medium" else "low")
        frows += (
            f"<tr id='{f['id']}'><td><b>{f['id']}</b></td><td><span class='tag {tagcls}'>{sev}</span></td>"
            f"<td>{esc(f['area'])}</td><td>{esc(f['detail'])}</td>"
            f"<td><a href='{esc(f['source'])}'>source</a></td></tr>"
        )
    flat = f"""
<h1>Flagged for review</h1>
<p class="lede">Everything the desk could not confirm, could not price, or found internally inconsistent. Nothing on
this page is hidden elsewhere on the site; these are the items that need a human decision, not more automation.</p>
<div class="scroll"><table>
<thead><tr><th>ID</th><th>Severity</th><th>Area</th><th>What happened</th><th>Link</th></tr></thead>
<tbody>{frows}</tbody></table></div>
<h2>Unverified events, listed blank</h2>
<p class="small muted">The following categories have OLBG events with no official confirmation, so every official
field is empty: Tennis (9 events), Darts (12), Cricket (7), Handball (15), Volleyball (14), Greyhounds (15),
Gaelic Sports (4), Golf (0 discovered), Rugby League (3 outright markets only). They appear on the
<a href="matches.html">match list</a> with an "unverified" tag and no price.</p>
"""
    (DESK / "flagged.html").write_text(page("Flagged for review", "flagged.html", flat))

    # ---------- sources ----------
    srows = ""
    for s in DATA.SOURCES:
        cls = {"read": "ok", "partial": "medium", "blocked": "no"}[s["status"]]
        srows += (
            f"<tr><td><b>{s['id']}</b></td><td>{esc(s['publisher'])}</td><td>{esc(s['name'])}</td>"
            f"<td><a href='{esc(s['url'])}'>{esc(s['url'])}</a></td><td>{esc(s['read_utc'])}</td>"
            f"<td><span class='tag {cls}'>{s['status']}</span></td><td class='small'>{esc(s['used_for'])}</td></tr>"
        )
    src = f"""
<h1>Sources</h1>
<p class="lede">Every page this desk read, what it was used for, and when. Status <b>read</b> means the content was
returned and used; <b>partial</b> means the page loaded but the relevant section was truncated or absent;
<b>blocked</b> means the publisher served no usable content and the attempt is recorded as a gap.</p>
<div class="scroll"><table>
<thead><tr><th>ID</th><th>Publisher</th><th>Page</th><th>URL</th><th>Read (UTC)</th><th>Status</th><th>Used for</th></tr></thead>
<tbody>{srows}</tbody></table></div>
<h2>Discovery source</h2>
<div class="card"><p>The OLBG sport hubs (<a href="https://www.olbg.com/betting-tips">olbg.com/betting-tips</a>,
one page per sport) supplied the event list, tip counts and tip shares. OLBG is a community tipping site: it
establishes that a market exists, never that a fixture is real. No sporting fact on this site is sourced to it.</p></div>
"""
    (DESK / "sources.html").write_text(page("Sources", "sources.html", src))

    # ---------- methodology ----------
    method = f"""
<h1>Methodology</h1>
<p class="lede">The contract this desk works to, stated plainly enough to be checked.</p>

<h2>Evidence rules</h2>
<div class="card"><ul>
<li>A fixture is <b>verified</b> only when its participants, competition and published start were read on the
organiser's own site during the observation window.</li>
<li>If a value cannot be confirmed, the cell stays empty and an entry appears on the
<a href="flagged.html">flagged page</a>. Nothing is inferred, interpolated or filled from memory.</li>
<li>OLBG is discovery only. A tip share is a crowd percentage and is never treated as a probability.</li>
<li>Hashes and timestamps record what we read. They prove integrity, not truth.</li>
</ul></div>

<h2>Price construction</h2>
<div class="card"><ul>
<li>Fair decimal = 1 ÷ p, with no margin, no clipping and no overround.</li>
<li>American prices are derived from the decimal and are shown to the nearest integer.</li>
<li><b>Records</b> (MLB, NHL) use Beta(2,2) shrinkage of win percentage and a log5 combination. No home-field term
is added by default; the exception is the NBA, where a single league-average 0.55 home prior is used and disclosed
as such.</li>
<li><b>Rugby union</b> uses the mean points margin over the matches actually read, shrunk by n ÷ (n+4), fed into a
normal model with σ = 13 points. Handicap lines are set to our own expected margin.</li>
<li><b>Totals</b> (MLB, NHL) use independent Poisson scoring rates derived from goals/runs for and against per game.
MLB totals are not pitcher-adjusted.</li>
<li>Every basis string on the <a href="markets.html">markets page</a> states the calculation and the sample size.</li>
</ul></div>

<h2>Confidence rules</h2>
<div class="card"><ul>
<li><b>High</b>: p ≥ 0.70. <b>Medium</b>: 0.60 ≤ p &lt; 0.70. <b>Low</b>: p &lt; 0.60.</li>
<li>The brief's odds band is checked separately and shown in its own column. High-plus-in-band requires p between
0.700 and 0.714; today nothing lands there (F-13).</li>
<li>Confidence labels describe the estimate, not the sample. Sample sizes are always printed alongside.</li>
</ul></div>

<h2>Prediction rules</h2>
<div class="card"><ul>
<li>At least 30 words, unique wording, no template reuse.</li>
<li>Must name the competition, both participants and the selection.</li>
<li>Every factual clause must be traceable to a source read in this window, linked beneath the write-up.</li>
<li>No claim about injuries, team news or player availability is made unless an official page published it. Today no
official page did, so no injury claim appears anywhere on this site.</li>
</ul></div>

<h2>Known limitations</h2>
<div class="card"><ul>
<li>Coverage is what one person could read in roughly thirty-five minutes; it is a sample of the day, not the day.</li>
<li>No bookmaker price was read, so no edge, no overround and no availability claim is made.</li>
<li>Model lines (handicaps and totals) are ours alone and do not correspond to any published market.</li>
</ul></div>
"""
    (DESK / "methodology.html").write_text(page("Methodology", "methodology.html", method))

    # ---------- sport pages ----------
    for sport, slug in SPORTS:
        fx = [f for f in FIXTURES.values() if f["sport"] == sport]
        mk = [m for m in MARKETS if m["sport"] == sport]
        ds = [d for d in DATA.D if d["sport"] == sport]
        pr = [p for p in DATA.PREDICTIONS if FIXTURES[p["fixture_id"]]["sport"] == sport]
        fblock = ""
        if fx:
            frows2 = "".join(
                f"<tr><td><b>{esc(f['home'])}</b> v <b>{esc(f['away'])}</b></td>"
                f"<td>{esc(f['competition'])}</td><td>{esc(f['start_local'])}</td>"
                f"<td>{esc(f['start_utc'] or '')}</td><td>{esc(f['venue'] or '')}</td>"
                f"<td><a href='{f['official_url']}'>official</a></td></tr>" for f in fx)
            fblock = f"""<h2>Verified fixtures</h2><div class="scroll"><table>
<thead><tr><th>Fixture</th><th>Competition</th><th>Start (source)</th><th>Start (UTC)</th><th>Venue</th><th>Source</th></tr></thead>
<tbody>{frows2}</tbody></table></div>"""
        mblock = ""
        if mk:
            mrows2 = "".join(
                f"<tr><td>{esc(m['fixture'])}</td><td>{esc(m['market'])}</td><td>{esc(m['selection'])}</td>"
                f"<td class='num'>{m['p']*100:.1f}%</td><td class='num'>{esc(m['american_display'])}</td>"
                f"<td><span class='tag {m['confidence'].lower()}'>{m['confidence']}</span></td>"
                f"<td class='small muted'>{esc(m['basis'])}</td></tr>" for m in mk)
            mblock = f"""<h2>Our prices</h2><div class="scroll"><table>
<thead><tr><th>Fixture</th><th>Market</th><th>Selection</th><th>Probability</th><th>Price</th>
<th>Confidence</th><th>Basis</th></tr></thead><tbody>{mrows2}</tbody></table></div>"""
        pblock = ""
        for p in pr:
            f = FIXTURES[p["fixture_id"]]
            pblock += f"""<div class="pred"><div class="meta">{esc(f['home'])} v {esc(f['away'])} ·
<span class="tag {p['confidence'].lower()}">{p['confidence']}</span></div>
<h3 style="margin:8px 0 4px;color:#fff;text-transform:none;letter-spacing:0;font-size:16px">{esc(p['selection'])}</h3>
<blockquote>{esc(p['body'])}</blockquote></div>"""
        facts = ""
        for f in fx:
            if f.get("facts"):
                facts += f"<h3>{esc(f['home'])} v {esc(f['away'])}</h3><ul class='small'>" + \
                         "".join(f"<li>{esc(x)}</li>" for x in f["facts"]) + "</ul>"
        if f.get("note"):
            facts += f"<p class='small muted'>{esc(f['note'])}</p>"
        if not ds:
            dblock = '<div class="note warn">The OLBG hub for this sport returned no events inside the observation window.</div>'
        else:
            dblock = f"""<h2>OLBG discovery rows ({len(ds)})</h2>
<div class="scroll"><table><thead><tr><th>Event</th><th>OLBG time</th><th>Most-tipped</th><th>Market</th>
<th>Tip share</th><th>Link</th></tr></thead><tbody>{''.join(
    f"<tr><td>{esc(d['label'])}</td><td>{esc(d['olbg_start'])}</td><td>{esc(d['selection'] or '')}</td>"
    f"<td>{esc(d['market'])}</td><td class='num'>{'' if d['tip_share'] is None else str(d['tip_share'])+'%'}</td>"
    f"<td><a href='{d['url']}'>OLBG</a></td></tr>" for d in ds)}</tbody></table></div>"""
        status = ("Fixture evidence: <span class='tag ok'>official source read</span>"
                  if fx else "Fixture evidence: <span class='tag no'>none — discovery only</span>")
        body = f"""
<h1>{esc(sport)}</h1>
<p class="lede">{status} · {len(ds)} OLBG events · {len(mk)} prices originated · {len(pr)} written predictions.</p>
{('<div class="note warn">No selection was originated for this sport. The events below are unverified OLBG discovery '
  'rows; pricing them would require inputs nobody published.</div>') if not mk else ''}
{fblock}
{mblock}
{facts}
{'<h2>Predictions</h2>' + pblock if pblock else ''}
{dblock}
<p class="small"><a href="../matches.html">Back to all matches</a> · <a href="../flagged.html">Flagged for review</a></p>
"""
        (DESK / "sports" / f"{slug}.html").write_text(
            page(sport, f"sports/{slug}.html", body, root="../"))


def main():
    build_model()
    write_json()
    write_site()
    hi = [m for m in MARKETS if m["confidence"] == "High"]
    print(f"fixtures={len(FIXTURES)} markets={len(MARKETS)} high={len(hi)} "
          f"in_band={sum(1 for m in hi if m['in_band'])} "
          f"medium={sum(1 for m in MARKETS if m['confidence']=='Medium')} "
          f"predictions={len(DATA.PREDICTIONS)} flags={len(DATA.FLAGS)}")
    for m in sorted(MARKETS, key=lambda x: -x["p"])[:6]:
        print(f"  {m['p']*100:5.1f}%  {m['american_display']:>7}  {m['confidence']:<6} {m['fixture']} — {m['selection']}")


if __name__ == "__main__":
    main()
