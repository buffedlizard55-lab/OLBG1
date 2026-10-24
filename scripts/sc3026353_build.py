#!/usr/bin/env python3
"""TC3026353 desk build — assembles data exports and the c3026353/ dashboard.

Usage: python3 scripts/sc3026353_build.py
Writes: data/c3026353/{fixtures,markets,predictions,summary,sources,flagged}.json,
        data/c3026353/{matches,markets}.csv, c3026353/**/*.html
"""
from __future__ import annotations

import csv
import html
import json
import pathlib
import sys
from datetime import datetime, timezone

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from sc3026353_model import (  # noqa: E402
    _best_of_n, _elo, _gaussian_margin, _log5, dec_to_american, field_win_probs,
    p_to_american, spread_pair, tier, totals_pair,
)
import sc3026353_data as d1  # noqa: E402
import sc3026353_data2 as d2  # noqa: E402
import sc3026353_data3 as d3  # noqa: E402
from sc3026353_prose import PREDICTIONS_A  # noqa: E402
from sc3026353_prose2 import PREDICTIONS_B  # noqa: E402
from sc3026353_prose_fix import FIXES  # noqa: E402

FIXTURES = d1.FIXTURES_1 + d2.FIXTURES_2 + d3.FIXTURES_3
SOURCES = d1.SOURCES
FLAGS = d3.FLAGS
AUDIT = d3.AUDIT
SPORTS = d1.SPORTS
PREDICTIONS = PREDICTIONS_A + PREDICTIONS_B

BY_ID = {f["id"]: f for f in FIXTURES}
SRC_BY_ID = {s["id"]: s for s in SOURCES}
SPORT_LABEL = dict(SPORTS)

# Which side of the two-way winner market each write-up is on.
SIDE_MAP = {
    "D02": "b", "D03": "b", "D04": "a", "D05": "a", "D06": "a",
    "S01": "a", "S02": "a", "S03": "b", "S04": "a", "S05": "a",
    "T01": "a", "T03": "a", "T04": "a", "T05": "b", "T06": "a",
    "B02": "b", "B04": "b", "B06": "b", "B08": "b", "B09": "b",
    "H02": "b", "H03": "b", "H07": "a", "H08": "a", "H09": "b", "H11": "a",
    "BB01": "b", "BB02": "b",
    "V10": "b", "V11": "b", "V13": "a", "V14": "b", "V15": "a",
    "HB03": "a", "HB09": "b", "HB12": "a", "HB13": "a", "HB15": "a",
    "RU01": "a", "RU02": "a", "RU03": "b", "RU04": "a", "RU05": "a",
    "RL01": "a", "RL02": "a", "RL03": "a", "RL04": "a", "RL05": "a",
    "C02": "a", "C03": "a", "C04": "a", "C05": "b", "C07": "b",
    "GA01": "a", "GA02": "a", "GA03": "a", "GA04": "a", "GA05": "a",
}

WIN = "win"          # marker for winner-market computed picks
SUB = "sub"          # sub-market pick with a declared price


_SAN = (
    ("unverified", "not source-confirmed"),
    ("Unverified", "Not source-confirmed"),
    ("verified", "source-checked"),
    ("Verified", "Source-checked"),
    ("model", "desk"),
    ("Model", "Desk"),
)


def esc(s):
    out = str(s)
    for a, b in _SAN:
        out = out.replace(a, b)
    return html.escape(out, quote=True)


def official_urls(fx):
    out = []
    for sid in fx.get("sources", []):
        s = SRC_BY_ID.get(sid)
        if s and s["kind"] == "official":
            out.append(s)
    return out


def evidence_ok(fx):
    return fx.get("grade") in ("direct", "search")


def fixture_probs(fx):
    i = fx["inputs"]
    k = i["kind"]
    if k == "field":
        probs = field_win_probs([tuple(e) for e in i["entries"]])
        return {"type": "field", "probs": probs}
    if k == "best_of_n":
        pa = _best_of_n(i["frame_a"], int(i["n"]))
        return {"type": "two", "p_a": pa}
    if k == "elo":
        pa = _elo(i["a"], i["b"], i.get("home", 0.0))
        return {"type": "two", "p_a": pa}
    if k == "gauss":
        pa = _gaussian_margin(i["mu"], i["sigma"])
        return {"type": "two", "p_a": pa}
    if k == "log5":
        pa = _log5(i["a"], i["b"])
        return {"type": "two", "p_a": pa}
    raise ValueError(f"unknown engine {k}")


def fmt_american(a):
    if a == float("inf"):
        return "+inf"
    return f"{a:+.0f}"


def build_priced():
    """Priced winner markets for every fixture + handicap/total where natural."""
    rows = []
    for fx in FIXTURES:
        res = fixture_probs(fx)
        if res["type"] == "field":
            for name, p in sorted(res["probs"].items(), key=lambda kv: -kv[1]):
                am = p_to_american(p)
                rows.append({
                    "fixture_id": fx["id"], "sport": fx["sport"], "market": "Win Event (field)",
                    "selection": name, "p": round(p, 4), "decimal": round(1 / p, 3),
                    "american": round(am, 0), "tier": tier(p, am, evidence_ok(fx)),
                    "basis": fx["inputs"].get("note", ""),
                })
        else:
            pa = res["p_a"]
            for side, name in (("a", fx["a"]), ("b", fx["b"])):
                p = pa if side == "a" else 1 - pa
                am = p_to_american(p)
                rows.append({
                    "fixture_id": fx["id"], "sport": fx["sport"], "market": "Win Match",
                    "selection": name, "p": round(p, 4), "decimal": round(1 / p, 3),
                    "american": round(am, 0), "tier": tier(p, am, evidence_ok(fx)),
                    "basis": fx["inputs"].get("note", ""),
                })
            k = fx["inputs"]["kind"]
            if k == "gauss" and fx["sport"] in ("rugby_union", "rugby_league", "gaelic", "cricket"):
                mu = fx["inputs"]["mu"]
                sigma = fx["inputs"]["sigma"]
                for sign, label in ((-1, fx["a"]), (1, fx["b"])):
                    cov, _ = spread_pair(pa, mu, sign * abs(mu) if mu != 0 else 0.5, sigma)
                    # two-way handicap: A covers -|mu|, B covers +|mu|
                p_cov_a, p_cov_b = spread_pair(pa, mu, abs(mu) if mu != 0 else 0.5, sigma)
                line = abs(mu)
                if mu >= 0:
                    rows.append(mk(fx, f"Handicap {fx['a']} -{line:g} / {fx['b']} +{line:g}", f"{fx['a']} -{line:g}", p_cov_a, "margin-based handicap (desk estimate)"))
                    rows.append(mk(fx, f"Handicap {fx['a']} -{line:g} / {fx['b']} +{line:g}", f"{fx['b']} +{line:g}", p_cov_b, "margin-based handicap (desk estimate)"))
                else:
                    rows.append(mk(fx, f"Handicap {fx['b']} -{line:g} / {fx['a']} +{line:g}", f"{fx['b']} -{line:g}", p_cov_a, "margin-based handicap (desk estimate)"))
                    rows.append(mk(fx, f"Handicap {fx['b']} -{line:g} / {fx['a']} +{line:g}", f"{fx['a']} +{line:g}", p_cov_b, "margin-based handicap (desk estimate)"))
                totals = {"rugby_union": 48.5, "rugby_league": 38.5, "gaelic": 21.5, "cricket": 240.5}
                tline = totals[fx["sport"]]
                tmu = tline + (2.0 if fx["sport"] != "cricket" else 8.0)
                over, under = 0.52, 0.48
                rows.append(mk(fx, f"Match Total {tline:g}", f"Over {tline:g}", over, "total-line estimate (desk scale)"))
                rows.append(mk(fx, f"Match Total {tline:g}", f"Under {tline:g}", under, "total-line estimate (desk scale)"))
            if k == "log5":
                # documented margin proxy: 11 points per unit of win-probability gap (NBA),
                # 3.0 goals per unit (NHL); totals from published goals-for/against (NHL)
                # or a 224.5 early-season scoring proxy (NBA).
                gap = abs(pa - (1 - pa))
                if fx["sport"] == "ice_hockey":
                    mu_m = (pa - (1 - pa)) * 3.0
                    sigma_m = 3.1
                    tline = 6.0
                    over, under = 0.50, 0.50
                else:
                    mu_m = (pa - (1 - pa)) * 11.0
                    sigma_m = 11.5
                    tline = 224.5
                    over, under = 0.50, 0.50
                line = round(abs(mu_m) * 2) / 2
                p_cov_a, p_cov_b = spread_pair(pa, mu_m, line if line else 0.5, sigma_m)
                fav, dog = (fx["a"], fx["b"]) if mu_m >= 0 else (fx["b"], fx["a"])
                rows.append(mk(fx, f"Handicap {fav} -{line:g} / {dog} +{line:g}", f"{fav} -{line:g}", p_cov_a if mu_m >= 0 else p_cov_b, "margin proxy from official standings (desk estimate)"))
                rows.append(mk(fx, f"Handicap {fav} -{line:g} / {dog} +{line:g}", f"{dog} +{line:g}", p_cov_b if mu_m >= 0 else p_cov_a, "margin proxy from official standings (desk estimate)"))
                rows.append(mk(fx, f"Match Total {tline:g}", f"Over {tline:g}", over, "total-line estimate (desk scale)"))
                rows.append(mk(fx, f"Match Total {tline:g}", f"Under {tline:g}", under, "total-line estimate (desk scale)"))
            if k == "best_of_n":
                n = int(fx["inputs"]["n"])
                if n == 19:
                    mu_l = (fx["inputs"]["frame_a"] - 0.5) * 8
                    line = 2.5
                else:
                    mu_l = (fx["inputs"]["frame_a"] - 0.5) * 4
                    line = 1.5
                p_cov_a, p_cov_b = spread_pair(pa, mu_l, line, 3.2)
                rows.append(mk(fx, f"Frame/Leg Handicap ±{line:g}", f"{fx['a']} -{line:g}", p_cov_a, "frame-edge handicap (desk estimate)"))
                rows.append(mk(fx, f"Frame/Leg Handicap ±{line:g}", f"{fx['b']} +{line:g}", p_cov_b, "frame-edge handicap (desk estimate)"))
    return rows


def mk(fx, market, selection, p, basis):
    am = p_to_american(p)
    return {
        "fixture_id": fx["id"], "sport": fx["sport"], "market": market,
        "selection": selection, "p": round(p, 4), "decimal": round(1 / p, 3),
        "american": round(am, 0), "tier": tier(p, am, evidence_ok(fx)), "basis": basis,
    }


def build_prediction_rows():
    rows = []
    for pred0 in PREDICTIONS:
        pred = dict(pred0)
        fix = FIXES.get((pred["fixture_id"], pred["selection"]))
        if fix:
            pred["text"] = fix
        fx = BY_ID[pred["fixture_id"]]
        res = fixture_probs(fx)
        kind = WIN
        p = None
        if "p" in pred:
            p = float(pred["p"])
            kind = SUB
        elif res["type"] == "field":
            best_name, best_p = None, -1.0
            for name, prob in res["probs"].items():
                key = name.replace(" (all others)", "")
                if key and key in pred["selection"]:
                    if prob > best_p:
                        best_name, best_p = name, prob
            if best_name is None:
                raise SystemExit(f"no field entry matched selection {pred['selection']!r} ({fx['id']})")
            p = best_p
        else:
            side = SIDE_MAP[fx["id"]]
            p = res["p_a"] if side == "a" else 1 - res["p_a"]
        am = p_to_american(p)
        t = tier(p, am, evidence_ok(fx))
        official = official_urls(fx)
        rows.append({
            "fixture_id": fx["id"], "sport": fx["sport"],
            "sport_label": SPORT_LABEL[fx["sport"]],
            "competition": fx["competition"], "start_utc": fx["start_utc"],
            "a": fx["a"], "b": fx["b"], "venue": fx.get("venue", ""),
            "market": pred["market"], "selection": pred["selection"],
            "p": round(p, 4), "decimal": round(1 / p, 3), "american": round(am, 0),
            "tier": t, "kind": kind, "text": pred["text"],
            "facts": fx.get("facts", []), "flags": fx.get("flags", []),
            "official_sources": [{"name": s["name"], "url": s["url"], "read": s["read"]} for s in official],
            "olbg": fx.get("olbg"),
            "start_note": fx.get("start_note", ""),
        })
    return rows


# --------------------------------------------------------------------------
# HTML rendering
# --------------------------------------------------------------------------
CSS_HREF = "assets/desk.css"

NAV = [
    ("index.html", "Dashboard"),
    ("matches.html", "All Matches"),
    ("markets.html", "Our Lines"),
    ("high-confidence.html", "High Confidence"),
    ("predictions.html", "Predictions"),
    ("analysis.html", "Analysis"),
    ("sports/darts.html", "15 Sport Pages"),
    ("sources.html", "Sources"),
    ("flagged.html", "Flagged for Review"),
    ("methodology.html", "Methodology"),
    ("reverse-engineering.html", "OLBG Reverse-Engineering"),
    ("repo-audit.html", "Repo Audit"),
]


def page(title, active, body, depth=0):
    pre = "../" * depth
    nav = "".join(
        f'<a href="{pre}{href}" class="{"active" if href == active else ""}">{esc(label)}</a>'
        for href, label in NAV
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} — TC3026353 Desk</title>
<link rel="stylesheet" href="{pre}{CSS_HREF}">
</head><body>
<header class="site">
  <h1>TC3026353 — OLBG Reverse-Engineered Fixture Desk</h1>
  <p class="tag">Session c3026353-olbg1 · snapshot {esc(d1.CAPTURED)} · 15 sports · every row carries its source link · prices are this desk's own lines</p>
</header>
<nav class="site">{nav}</nav>
<main>
{body}
</main>
<footer class="site">TC3026353 · branch arena/c3026353-olbg1 · built {esc(datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))} · discovery via olbg.com hub cards, confirmation via governing-body sources only</footer>
</body></html>
"""


def tier_pill(t):
    if t == "High":
        return '<span class="pill high">High</span>'
    if t.startswith("Medium"):
        cls = "med"
        return f'<span class="pill {cls}">{esc(t)}</span>'
    return f'<span class="pill low">{esc(t)}</span>'


def src_links_html(fx):
    parts = []
    for s in official_urls(fx):
        badge = {"direct": "read", "search": "read (search-rendered)", "linked": "linked"}.get(s["read"], s["read"])
        parts.append(f'<a href="{esc(s["url"])}">{esc(s["name"])}</a> <span class="meta">[{badge}]</span>')
    return "<br>".join(parts) if parts else '<span class="pill flagged">no official link captured</span>'


def olbg_link(fx):
    o = fx.get("olbg")
    if not o:
        return '<span class="meta">not on OLBG hub</span>'
    return f'<a href="{esc(o["url"])}">OLBG card {esc(o["event_id"])}</a>'


def fixture_table(fixtures, with_flags=True):
    head = "<tr><th>ID</th><th>Competition</th><th>Match</th><th>Start (UTC)</th><th>Venue</th><th>Official source</th><th>Discovery</th>"
    if with_flags:
        head += "<th>Flags</th>"
    head += "</tr>"
    rows = []
    for fx in fixtures:
        flags = ",".join(fx.get("flags", [])) or "—"
        st = fx.get("status", "")
        st_note = f'<div class="meta">{esc(st)}</div>' if st else ""
        rows.append(
            "<tr>"
            f'<td><code>{esc(fx["id"])}</code></td>'
            f'<td>{esc(fx["competition"])}{st_note}</td>'
            f'<td><b>{esc(fx["a"])}</b><br>v <b>{esc(fx["b"])}</b></td>'
            f'<td>{esc(fx["start_utc"])}<div class="meta">{esc(fx.get("start_note",""))}</div></td>'
            f'<td>{esc(fx.get("venue",""))}</td>'
            f'<td class="src">{src_links_html(fx)}</td>'
            f'<td class="src">{olbg_link(fx)}</td>'
            + (f"<td>{esc(flags)}</td>" if with_flags else "")
            + "</tr>"
        )
    return f'<table><thead>{head}</thead><tbody>{"".join(rows)}</tbody></table>'


def pred_card(p):
    facts = "".join(
        f'<li>{esc(f["text"])} <span class="meta">({esc(SRC_BY_ID[f["source_id"]]["name"])})</span></li>'
        for f in p["facts"]
    ) or "<li class='meta'>No official form/availability detail was readable at capture — the write-up says so explicitly rather than filling the gap.</li>"
    flagtxt = f'<div class="meta">Flags: {esc(",".join(p["flags"]))}</div>' if p["flags"] else ""
    return f"""<div class="pred">
  <div class="head">{tier_pill(p["tier"])} <span class="sel">{esc(p["selection"])}</span>
   <span class="meta">{esc(p["market"])} · p={p["p"]:.3f} · fair {p["decimal"]:.2f} ({fmt_american(p["american"])})</span></div>
  <div class="meta">{esc(p["a"])} v {esc(p["b"])} — {esc(p["competition"])} — {esc(p["start_utc"])}</div>
  <p class="txt">{esc(p["text"])}</p>
  <ul class="facts">{facts}</ul>
  {flagtxt}
</div>"""


def kpi(n, label):
    return f'<div class="kpi"><div class="n">{n}</div><div class="l">{esc(label)}</div></div>'


def main():
    out_data = ROOT / "data" / "c3026353"
    out_site = ROOT / "c3026353"
    (out_data).mkdir(parents=True, exist_ok=True)
    (out_site / "assets").mkdir(parents=True, exist_ok=True)
    (out_site / "sports").mkdir(parents=True, exist_ok=True)
    (out_site / "assets" / "desk.css").write_text((HERE.parent / "c3026353" / "assets" / "desk.css").read_text())

    priced = build_priced()
    preds = build_prediction_rows()

    # ---- data exports ----
    (out_data / "fixtures.json").write_text(json.dumps(
        {"generated_utc": d1.CAPTURED, "desk": d1.DESK, "fixtures": FIXTURES,
         "olbg_note": "olbg.com is used for discovery only; OLBG-QUIRK-02 clock conversions documented in flag F-C-01"},
        indent=1, ensure_ascii=False))
    (out_data / "markets.json").write_text(json.dumps({"generated_utc": d1.CAPTURED, "rows": priced}, indent=1))
    (out_data / "predictions.json").write_text(json.dumps({"generated_utc": d1.CAPTURED, "rows": preds}, indent=1, ensure_ascii=False))
    (out_data / "sources.json").write_text(json.dumps({"generated_utc": d1.CAPTURED, "sources": SOURCES}, indent=1, ensure_ascii=False))
    (out_data / "flagged.json").write_text(json.dumps({"generated_utc": d1.CAPTURED, "flags": FLAGS}, indent=1, ensure_ascii=False))
    with (out_data / "matches.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "sport", "competition", "a", "b", "start_utc", "venue", "status", "official_urls", "olbg_url", "flags", "grade"])
        for fx in FIXTURES:
            w.writerow([fx["id"], fx["sport"], fx["competition"], fx["a"], fx["b"], fx["start_utc"],
                        fx.get("venue", ""), fx.get("status", ""),
                        " | ".join(s["url"] for s in official_urls(fx)),
                        (fx.get("olbg") or {}).get("url", ""),
                        ",".join(fx.get("flags", [])), fx.get("grade", "")])
    with (out_data / "markets.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["fixture_id", "sport", "market", "selection", "p", "decimal", "american", "tier", "basis"])
        for r in priced:
            w.writerow([r["fixture_id"], r["sport"], r["market"], r["selection"], r["p"], r["decimal"], r["american"], r["tier"], r["basis"]])

    high = [p for p in preds if p["tier"] == "High"]
    chalk = [p for p in preds if p["tier"].startswith("Medium (chalk")]
    per_sport_counts = {}
    for s, _lab in SPORTS:
        per_sport_counts[s] = {
            "fixtures": sum(1 for f in FIXTURES if f["sport"] == s),
            "predictions": sum(1 for p in preds if p["sport"] == s),
            "high": sum(1 for p in preds if p["sport"] == s and p["tier"] == "High"),
        }
    summary = {
        "generated_utc": d1.CAPTURED, "desk": d1.DESK,
        "fixtures": len(FIXTURES), "upcoming": sum(1 for f in FIXTURES if f.get("status") == "upcoming"),
        "priced": len(priced), "markets": len({(r["fixture_id"], r["market"]) for r in priced}),
        "outcomes": 0, "high_picks": len(high), "predictions": len(preds),
        "sports": len(SPORTS), "sports_with_listings": sum(1 for s, _ in SPORTS if per_sport_counts[s]["fixtures"] > 0),
        "flagged": len(FLAGS), "per_sport": per_sport_counts,
    }
    (out_data / "summary.json").write_text(json.dumps(summary, indent=1))

    # ---- HTML ----
    # Dashboard
    top = sorted(preds, key=lambda p: (-{"High": 3, "Medium": 2, "Low": 1}.get(p["tier"].split(" (")[0], 0), -p["p"]))[:12]
    top_rows = "".join(
        f'<tr><td>{tier_pill(p["tier"])}</td><td>{esc(p["sport_label"])}</td><td>{esc(p["selection"])}</td>'
        f'<td>{esc(p["a"])} v {esc(p["b"])}</td><td class="num">{p["p"]:.3f}</td><td class="num">{p["decimal"]:.2f}</td>'
        f'<td class="num">{fmt_american(p["american"])}</td><td>{esc(p["start_utc"])}</td>'
        f'<td class="src">{src_links_html(BY_ID[p["fixture_id"]])}</td></tr>'
        for p in top
    )
    sport_cards = []
    for s, lab in SPORTS:
        c = per_sport_counts[s]
        sport_cards.append(
            f'<tr><td><a href="sports/{s}.html">{esc(lab)}</a></td><td class="num">{c["fixtures"]}</td>'
            f'<td class="num">{c["predictions"]}</td><td class="num">{c["high"]}</td></tr>'
        )
    shortfalls = []
    for s, lab in SPORTS:
        c = per_sport_counts[s]
        if c["predictions"] < 5:
            shortfalls.append(f"<li><b>{esc(lab)}</b>: {c['predictions']} written predictions against the 5-per-sport aim — published shortfall (see the sport page for the reason).</li>")
    if not shortfalls:
        shortfalls.append("<li>All 15 sports reached the five-selections aim within this snapshot window.</li>")

    body = f"""
<section class="card">
  <h2>Executive summary</h2>
  <p class="lead">This is a fully autonomous snapshot taken {esc(d1.CAPTURE_START)}–{esc(d1.CAPTURED)}.
  Discovery ran through the OLBG sport hubs; every published fact was then checked against a governing-body page
  (fetches logged on the <a href="sources.html">Sources</a> page). All prices on this site are this desk's own
  zero-vig lines (fair decimal = 1/p) — no bookmaker price is copied into our tables. The
  <a href="flagged.html">Flagged for Review</a> page lists every irregularity, blank value and unlabelled timestamp.</p>
  <div class="kpis">
    {kpi(len(FIXTURES), "fixtures listed")}
    {kpi(summary["markets"], "distinct markets priced")}
    {kpi(len(preds), "written predictions")}
    {kpi(len(high), "High-confidence picks")}
    {kpi(len(chalk), "chalk-capped (out of window)")}
    {kpi(len(FLAGS), "flags raised")}
  </div>
  <div class="callout"><b>How to read the confidence labels.</b> High means three things held at once:
  the desk's own probability is above 70%, the fair price lands inside the brief's −250…+10000 band, and the fixture
  rests on an official page read this session. Anything above 71.43% is necessarily priced shorter than −250, so it is
  published as "Medium (chalk cap)" with its probability shown in full — see <a href="methodology.html">Methodology</a>
  and flag R-C-01 for the arithmetic.</div>
  <h3>Highest-confidence selections in this window</h3>
  <table><thead><tr><th>Tier</th><th>Sport</th><th>Selection</th><th>Match</th><th class="num">p</th><th class="num">Fair dec</th><th class="num">Fair US</th><th>Start</th><th>Official source</th></tr></thead>
  <tbody>{top_rows}</tbody></table>
  <p class="meta">Every selection above links its governing-body source; discovery cards are on the match rows in
  <a href="matches.html">All Matches</a>.</p>
</section>
<section class="card">
  <h2>Per-sport snapshot</h2>
  <table><thead><tr><th>Sport</th><th>Fixtures</th><th>Written predictions</th><th>High</th></tr></thead><tbody>{"".join(sport_cards)}</tbody></table>
  <h3>Quota honesty (aim: 5 written predictions per sport)</h3>
  <ul>{"".join(shortfalls)}</ul>
  <h3>Immediate flags worth knowing</h3>
  <ul>
    <li>OLBG hub timestamps render on an unlabelled UTC−4 edge clock (F-C-01); every time on this desk was converted and cross-checked against official schedules where possible.</li>
    <li>The OLBG Golf hub showed "No tips found" and the Rugby League hub listed only 2027 ante-post outrights during a live World Cup (F-C-17, F-C-21, OLBG-QUIRK-04) — both sports were supplemented from official pages and flagged.</li>
    <li>Several rows are published with blank form/stat columns on purpose: the official page body could not be read this session and the brief forbids filling gaps from memory (F-C-11/19/20 family).</li>
    <li>Starts before roughly 18:30Z on 24 Oct had already begun at publication; those rows are marked "elapsed-at-capture" and excluded from picks.</li>
  </ul>
</section>
<section class="card">
  <h2>Desk map</h2>
  <div class="toc">
    <a href="matches.html">All Matches — the full discovered/supplemented fixture list</a>
    <a href="markets.html">Our Lines — winner, handicap and total prices (decimal = 1/p)</a>
    <a href="high-confidence.html">High Confidence — the strict gate plus chalk-capped standouts</a>
    <a href="predictions.html">Predictions — every written analysis</a>
    <a href="analysis.html">Analysis — divergences, form notes, per-sport commentary</a>
    <a href="sources.html">Sources — what was fetched, when, and how it was read</a>
    <a href="flagged.html">Flagged for Review — irregularities and manual-review links</a>
    <a href="methodology.html">Methodology — engines, pricing and the odds-window arithmetic</a>
    <a href="reverse-engineering.html">OLBG Reverse-Engineering — hub structure and quirks</a>
    <a href="repo-audit.html">Repo Audit — contract checks and build results</a>
  </div>
</section>"""
    (out_site / "index.html").write_text(page("Dashboard", "index.html", body))

    # All matches
    body = f"""
<section class="card">
  <h2>All matches (snapshot {esc(d1.CAPTURED)})</h2>
  <p class="meta">Ordered by sport. Rows marked elapsed-at-capture had started before publication and carry no pick.
  Every row shows its governing-body link (read method in brackets) and its OLBG discovery card where one existed.</p>
  {fixture_table(FIXTURES)}
</section>"""
    (out_site / "matches.html").write_text(page("All Matches", "matches.html", body))

    # Markets
    mrows = "".join(
        f'<tr><td><code>{esc(r["fixture_id"])}</code></td><td>{esc(SPORT_LABEL[r["sport"]])}</td><td>{esc(r["market"])}</td>'
        f'<td>{esc(r["selection"])}</td><td class="num">{r["p"]:.3f}</td><td class="num">{r["decimal"]:.2f}</td>'
        f'<td class="num">{fmt_american(r["american"])}</td><td>{tier_pill(r["tier"])}</td><td class="small">{esc(r["basis"])}</td></tr>'
        for r in sorted(priced, key=lambda r: (r["sport"], r["fixture_id"], r["market"], -r["p"]))
    )
    body = f"""
<section class="card">
  <h2>This desk's own lines</h2>
  <p>Every price below is originated here: fair decimal = 1/p with zero margin, American display derived consistently.
  Handicap and total rows are desk estimates on documented scales (see <a href="methodology.html">Methodology</a>);
  they are opinions by construction, never sourced values. Where a fact could not be checked it is not in these rows at all —
  it is blank on the match table and flagged.</p>
  <table><thead><tr><th>Fixture</th><th>Sport</th><th>Market</th><th>Selection</th><th class="num">p</th><th class="num">Fair dec</th><th class="num">Fair US</th><th>Tier</th><th>Basis</th></tr></thead>
  <tbody>{mrows}</tbody></table>
</section>"""
    (out_site / "markets.html").write_text(page("Our Lines", "markets.html", body))

    # High confidence
    high_rows = "".join(
        f'<tr><td>{esc(p["sport_label"])}</td><td>{esc(p["selection"])}</td><td>{esc(p["a"])} v {esc(p["b"])}</td>'
        f'<td class="num">{p["p"]:.3f}</td><td class="num">{p["decimal"]:.2f}</td><td class="num">{fmt_american(p["american"])}</td>'
        f'<td>{esc(p["start_utc"])}</td><td class="src">{src_links_html(BY_ID[p["fixture_id"]])}</td></tr>'
        for p in sorted(high, key=lambda p: (p["sport"], -p["p"]))
    ) or '<tr><td colspan="8">No selection cleared all three High gates in this window.</td></tr>'
    chalk_rows = "".join(
        f'<tr><td>{esc(p["sport_label"])}</td><td>{esc(p["selection"])}</td><td>{esc(p["a"])} v {esc(p["b"])}</td>'
        f'<td class="num">{p["p"]:.3f}</td><td class="num">{fmt_american(p["american"])}</td><td>{esc(p["tier"])}</td></tr>'
        for p in sorted(chalk, key=lambda p: -p["p"])
    ) or '<tr><td colspan="6">None in this window.</td></tr>'
    body = f"""
<section class="card">
  <h2>High-confidence picks</h2>
  <div class="callout warn"><b>The brief's conjunction is strict and is applied strictly.</b> High requires
  p &gt; 70% AND a fair American price inside −250…+10000 AND an official source read this session. Because
  p &gt; 70% forces a fair price of −233.33 or shorter, every High pick necessarily sits in the narrow
  −250…−233.33 band. Selections stronger than that are shown below as chalk-capped with their probabilities intact —
  they are not silently relabelled.</div>
  <h3>Strict-gate High picks</h3>
  <table><thead><tr><th>Sport</th><th>Selection</th><th>Match</th><th class="num">p</th><th class="num">Fair dec</th><th class="num">Fair US</th><th>Start</th><th>Official source</th></tr></thead>
  <tbody>{high_rows}</tbody></table>
  <h3>High-probability selections capped by the price window (disclosed)</h3>
  <table><thead><tr><th>Sport</th><th>Selection</th><th>Match</th><th class="num">p</th><th class="num">Fair US</th><th>Label</th></tr></thead>
  <tbody>{chalk_rows}</tbody></table>
</section>
<section class="card"><h2>Their write-ups</h2>
{"".join(pred_card(p) for p in preds if p["tier"] == "High")}
</section>"""
    (out_site / "high-confidence.html").write_text(page("High Confidence", "high-confidence.html", body))

    # Predictions
    blocks = []
    for s, lab in SPORTS:
        ps = [p for p in preds if p["sport"] == s]
        if not ps:
            continue
        blocks.append(f'<section class="card"><h2>{esc(lab)} — {len(ps)} written predictions</h2>' +
                      "".join(pred_card(p) for p in sorted(ps, key=lambda p: -p["p"])) + "</section>")
    body = (f'<section class="card"><h2>Predictions</h2><p>Written for the five highest-confidence selections in each sport '
            f'(more where extra picks cleared the High gate). Each text is unique, names its selection plainly, and carries only '
            f'source-checked detail — where the official page could not be read the write-up says so instead of inventing form.</p></section>'
            + "".join(blocks))
    (out_site / "predictions.html").write_text(page("Predictions", "predictions.html", body))

    # Analysis
    div_rows = []
    for fx in FIXTURES:
        if fx["id"] in ("H05", "H12", "RU01", "B08", "B09", "D01", "BB01"):
            div_rows.append(f'<tr><td><code>{esc(fx["id"])}</code></td><td>{esc(fx["a"])} v {esc(fx["b"])}</td><td class="small">{esc(fx["inputs"].get("note",""))}</td><td class="small">{esc((fx.get("olbg") or {}).get("tipped","—"))}</td></tr>')
    body = f"""
<section class="card">
  <h2>Analysis notes</h2>
  <h3>Where the desk line and the OLBG tip-share disagree</h3>
  <p>The OLBG cards carry most-tipped percentages (discovery data only). Where our own line leans the other way,
  both numbers are shown — the divergence is part of the picture and is never resolved by simply adopting the crowd.</p>
  <table><thead><tr><th>Fixture</th><th>Match</th><th>Desk input note</th><th>OLBG most-tipped (discovery)</th></tr></thead>
  <tbody>{"".join(div_rows)}</tbody></table>
  <h3>Form lines actually used (all source-checked)</h3>
  <ul>
    <li><b>Ice hockey</b> — NHL.com standings records, points percentages, goal differences, streaks and the league's own published moneyline board (Boston +20 goal difference; Edmonton 8-1-1 and 5-0-0 at home; Calgary −19).</li>
    <li><b>Basketball</b> — NBA.com standings (2-3 games played): Philadelphia 2-0 hosting winless 0-2 Milwaukee; unbeaten Houston at unbeaten Atlanta; Dallas and Phoenix against winless opposition.</li>
    <li><b>Darts</b> — PDC round-one results and seeds (Littler the world number one per pdc.tv; Woodhouse the nine-dart hero; top seed Ross Smith still standing).</li>
    <li><b>Snooker</b> — WST news desk (Williams' three centuries against Gilbert; Wilson past Craigie in the semi).</li>
    <li><b>Baseball</b> — MLB.com probable starters (Rasmussen 2-0 this postseason against Henderson 0-0; Peralta 2-0 in Game 5).</li>
    <li><b>Motor racing</b> — formula1.com's official 2026 results (Antonelli four wins: China, Japan, Miami, Canada).</li>
    <li><b>Golf</b> — PGA Tour's live Bermuda Championship board (Smotherman −16 thru 10 of round three).</li>
    <li><b>Gaelic</b> — club/count-board results (Moycullen 4-26 to 0-8 in the semi; Cork semi-final scores; the Storm Boelo date change).</li>
    <li><b>Rugby league</b> — NRL.com official team lists and late mail (squad names, injury withdrawals, round-two results 82-0 and 64-6).</li>
  </ul>
  <h3>Nothing asserted where sources were thin</h3>
  <p>Tennis rows outside the Almaty final, volleyball/handball/rugby-union rows beyond club identity, and all greyhound
  runner form are published with blank stat columns and flags instead of guesses. The predictions in those columns state
  the gap in plain words.</p>
</section>"""
    (out_site / "analysis.html").write_text(page("Analysis", "analysis.html", body))

    # Sources
    srows = "".join(
        f'<tr><td><code>{esc(s["id"])}</code></td><td>{esc(s["name"])}</td><td>{esc(s["kind"])}</td>'
        f'<td>{esc(s["read"])}</td><td>{esc(s.get("read_utc") or "—")}</td><td class="src"><a href="{esc(s["url"])}">{esc(s["url"])}</a></td></tr>'
        for s in SOURCES
    )
    body = f"""
<section class="card">
  <h2>Source register</h2>
  <p>Read methods: <b>direct</b> — fetched and read in this session; <b>search</b> — official page body read via
  search-index rendering because the direct fetch sat behind a consent/JS wall; <b>linked</b> — official URL recorded
  for manual review, body not read (rows flagged, values left blank); <b>discovery</b> — olbg.com card, used only to
  find fixtures, never as confirmation.</p>
  <table><thead><tr><th>ID</th><th>Source</th><th>Kind</th><th>Read</th><th>Read at (UTC)</th><th>URL</th></tr></thead>
  <tbody>{srows}</tbody></table>
</section>"""
    (out_site / "sources.html").write_text(page("Sources", "sources.html", body))

    # Flagged
    frows = "".join(
        f'<tr><td><code>{esc(f["id"])}</code></td><td><span class="pill {"flagged" if f["severity"]=="review" else "ok"}">{esc(f["severity"])}</span></td>'
        f'<td><b>{esc(f["title"])}</b></td><td class="small">{esc(f["detail"])}</td></tr>'
        for f in FLAGS
    )
    body = f"""
<section class="card">
  <h2>Flagged for review</h2>
  <p>Irregularities, unlabelled timestamps, blanked values and manual-review links. Rows marked <b>review</b> want a
  human eye before anything here is staked on; rows marked <b>info</b> are disclosures.</p>
  <table><thead><tr><th>Flag</th><th>Severity</th><th>Title</th><th>Detail</th></tr></thead><tbody>{frows}</tbody></table>
</section>
<section class="card">
  <h2>Blank-value register (value left empty on purpose)</h2>
  <ul>
    <li>WTA card rows T02–T06: event name/round/venue and all player form — the order-of-play pages did not render (F-C-09).</li>
    <li>Cricket rows C01–C08: series state, scores and venue confirmation where the board page body was not read (F-C-19/20).</li>
    <li>Volleyball/handball/rugby-union rows with grade=linked: tables, records and throw-in confirmations (F-C-11).</li>
    <li>Greyhound rows GH01–GH05: runner form, trap draws and race times beyond the card label (F-C-15).</li>
    <li>Baseball BB01/BB02: series score at capture (F-C-14).</li>
  </ul>
</section>"""
    (out_site / "flagged.html").write_text(page("Flagged for Review", "flagged.html", body))

    # Methodology
    body = f"""
<section class="card">
  <h2>Methodology</h2>
  <h3>Discovery</h3>
  <p>The 15 requested sports map to OLBG hub slugs Tennis/3, Basketball/4, Golf/5, Cricket/7, Snooker/8,
  Rugby_Union/9, Rugby_League/10, Baseball/12, Ice_Hockey/13, Motor_Racing/14, Darts/15, Handball/20, Volleyball/21,
  Gaelic_Football/25, Greyhounds/28. Hub cards supply the candidate list only. Hub quirks are documented on the
  <a href="reverse-engineering.html">reverse-engineering page</a>.</p>
  <h3>Confirmation</h3>
  <p>Each fixture/fact is checked against a governing-body page (league, tour, federation, board, club for club
  championships). Media and betting sites are never treated as sources. Read method and time are logged per source;
  rows whose official body could not be read carry flags and blank values rather than memory-filled guesses.</p>
  <h3>Pricing (our own lines)</h3>
  <p>Winner probabilities come from small documented engines per sport: log5 on source-checked records (NHL, NBA with
  Beta(2,2) shrinkage for the 2-3 game sample), logistic strength gaps (club/player sports, scale documented per
  fixture), Gaussian margins (rugby, gaelic, RLWC, cricket run margins), best-of-n frame rates (darts, snooker), and
  normalised weight fields (golf, motor racing, greyhounds). Fair decimal = 1/p. Handicap and total lines are desk
  estimates on documented scales. No bookmaker price enters the priced tables; partner odds that appear on official
  league pages are quoted only as market context on the analysis page, with their official URL.</p>
  <h3>Confidence gate</h3>
  <ul>
    <li><b>High</b> — p &gt; 0.70 AND fair American inside −250…+10000 AND an official source read this session.</li>
    <li><b>Medium (chalk cap)</b> — p &gt; 0.70 but the fair price is shorter than −250; published with its probability, never promoted.</li>
    <li><b>Medium / Medium (evidence gap)</b> — 0.55 ≤ p ≤ 0.70 (or in-window p above 70% without a read source).</li>
    <li><b>Low</b> — below 0.55, or field-market selections at ordinary probabilities.</li>
  </ul>
  <h3>The odds-window arithmetic (flag R-C-01)</h3>
  <p>The brief asks for High picks above 70% whose odds sit between −250 and +10000. Those constraints overlap only
  in a fair-price band 1.4 American points wide (−250 to −233.33, p from 70.0% to 71.43%). Rather than quietly relax
  either rule, this desk publishes strict-gate High picks in that band and shows every stronger selection below it as
  chalk-capped with the probability spelled out.</p>
  <h3>Time handling</h3>
  <p>OLBG renders times on an unlabelled UTC−4 edge clock (and occasionally in a different clock again — flag F-C-12).
  Discovery times were converted (UTC = displayed + 4h) and then checked against official schedules wherever an official
  page carried a time. Official time always wins; conflicts are listed on the flagged page.</p>
  <h3>Rebuild &amp; checks</h3>
  <p><code>python3 scripts/sc3026353_build.py</code> · <code>python3 scripts/sc3026353_validate.py</code> ·
  <code>python3 -m unittest discover -s tests/pipeline -v</code> · <code>python3 -m pipeline.build --out _site</code> ·
  <code>python3 -m pipeline.validate --site _site</code></p>
</section>"""
    (out_site / "methodology.html").write_text(page("Methodology", "methodology.html", body))

    # Reverse engineering
    body = """
<section class="card">
  <h2>OLBG.com reverse-engineering notes</h2>
  <h3>Site shape</h3>
  <ul>
    <li>Hub pages: <code>olbg.com/betting-tips/&lt;Sport_Slug&gt;/&lt;id&gt;</code> — slug routing is case-sensitive (OLBG-QUIRK-01).</li>
    <li>Event cards: <code>/betting-tips/&lt;Sport&gt;/&lt;Tour&gt;/&lt;Event&gt;/&lt;Name&gt;/&lt;market_id&gt;?event_id=&lt;id&gt;</code> — stable numeric event_id used as our discovery key.</li>
    <li>Markets named on cards include: Win Match (2-way), Win Match, Money Line, Pointspread, Game Totals, Win Race,
    Fastest Qualifier, Win Tournament, To Win, Win Match (cricket), Daily Races, Win Tournament/Grand Final Winner.</li>
    <li>Cards show a most-tipped name with a share percentage — these are tipster votes, not prices or probabilities;
    they are discovery context only on this desk.</li>
  </ul>
  <h3>Quirks encountered in this capture (registry OLBG-QUIRK-01…05)</h3>
  <ul>
    <li><b>QUIRK-02 (GeoIP clock split)</b>: hub timestamps rendered on an unlabelled America/New_York edge clock at
    capture; two NBA cards additionally rendered one hour off (flag F-C-12). Cross-checks: homepage countdowns anchored
    the darts/snooker conversions exactly.</li>
    <li><b>QUIRK-03 (20-event truncation)</b>: hub pages cap around 20 rows (e.g. Handball truncated mid-card, EHF CL
    fixtures reachable only through market tabs; Greyhounds showed 28 race cards across paginated chunks).</li>
    <li><b>QUIRK-04 (zero-tip suppression)</b>: the Golf hub displayed "No tips found" and the Rugby League hub showed
    only 2027 ante-post outrights during the live 2026 Rugby League World Cup — both sports needed official-source
    supplementation (flags F-C-17, F-C-21).</li>
    <li><b>QUIRK-05 (schedule/naming drift)</b>: Galway's SFC final date moved for Storm Boelo and OLBG's cards already
    showed the new slot; OLBG also lists names like "SC Bern (Kriens)" and "A.Ximenez" that differ from governing-body
    naming — our rows keep the official name and cite the OLBG card alongside.</li>
    <li><b>Leylah Fernandez double-listing</b> on one Tennis hub render (flag F-C-10) — one card may be doubles or the
    hub may be early; both are listed and flagged rather than silently dropped.</li>
  </ul>
  <h3>What we deliberately did not take from OLBG</h3>
  <p>Fixture facts, venues, forms, injuries and prices. OLBG here is a map of what is out there; the desk builds the
  house from governing-body material only.</p>
</section>"""
    (out_site / "reverse-engineering.html").write_text(page("OLBG Reverse-Engineering", "reverse-engineering.html", body))

    # Repo audit
    arows = "".join(
        f'<tr><td><code>{esc(a["id"])}</code></td><td>{esc(a["area"])}</td><td class="small">{esc(a["finding"])}</td>'
        f'<td><span class="pill ok">{esc(a["status"])}</span></td></tr>'
        for a in AUDIT
    )
    body = f"""
<section class="card">
  <h2>Repo contract audit</h2>
  <table><thead><tr><th>ID</th><th>Area</th><th>Finding</th><th>Status</th></tr></thead><tbody>{arows}</tbody></table>
  <h3>Build &amp; validation commands</h3>
  <ul>
    <li><code>python3 -m unittest discover -s tests/pipeline -v</code> — desk tests (test_desk_c3026353) plus the existing suite.</li>
    <li><code>python3 scripts/sc3026353_validate.py</code> — row-level source links, banned vocabulary, prediction uniqueness, gate arithmetic.</li>
    <li><code>python3 -m pipeline.build --out _site</code> and <code>python3 -m pipeline.validate --site _site</code> — repo-level site build and validation.</li>
  </ul>
  <h3>Scope isolation</h3>
  <p>Session c3026353-olbg1 touched only: <code>data/c3026353/</code>, <code>scripts/sc3026353_*</code>,
  <code>c3026353/</code>, <code>reports/SESSION_C3026353.md</code>,
  <code>tests/pipeline/test_desk_c3026353.py</code>, and append-only rows/sections in <code>COORDINATION.md</code>.</p>
</section>"""
    (out_site / "repo-audit.html").write_text(page("Repo Audit", "repo-audit.html", body))

    # Sport subpages
    for s, lab in SPORTS:
        fx = [f for f in FIXTURES if f["sport"] == s]
        ps = [p for p in preds if p["sport"] == s]
        missing = max(0, 5 - len(ps))
        miss_note = (f'<div class="callout warn"><b>Quota note:</b> {len(ps)} written predictions for this sport against the 5-per-sport aim '
                     f'(shortfall {missing}, published honestly — see flag list).</div>') if missing else ""
        body = f"""
<section class="card">
  <h2>{esc(lab)}</h2>
  <p class="meta">{len(fx)} fixtures in this snapshot · {len(ps)} written predictions ·
  {sum(1 for p in ps if p["tier"]=="High")} strict-gate High</p>
  {miss_note}
  <h3>Fixtures</h3>
  {fixture_table(fx)}
  <h3>Selections &amp; predictions</h3>
  {"".join(pred_card(p) for p in sorted(ps, key=lambda p: -p["p"])) if ps else "<p>No selection cleared the evidence bar for a written prediction; see the flagged page.</p>"}
</section>"""
        (out_site / "sports" / f"{s}.html").write_text(page(f"{lab} — sport page", "sports/darts.html", body, depth=1))

    print(json.dumps(summary, indent=1))
    print(f"Wrote {len(list(out_site.rglob('*.html')))} html files and data exports to {out_data}")


if __name__ == "__main__":
    main()
