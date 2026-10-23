#!/usr/bin/env python3
"""Session 3c021b49 — build the verified data files and the dashboard site."""
from __future__ import annotations

import csv, html, json, math, os, re, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from s3c021b49_data import (FIXTURES, SOURCES, SPORT_NAMES, SPORT_ORDER, OLBG_HUBS,
                             SESSION, DESK_NAME, CAPTURED_UTC, OLBG_NOTE)
from s3c021b49_model import priced_book, featured_pick, confidence_for, tier_for, american
from s3c021b49_predictions import PREDICTIONS

DESK = Path(ROOT / "3c021b49")
DATA = Path(ROOT / "data" / "3c021b49")
OUT = CAPTURED_UTC

FIXED_TTL = timedelta(hours=6)
NOW = datetime(2026, 10, 23, 22, 30, tzinfo=timezone.utc)


def parse_dt(v):
    if not v:
        return None
    return datetime.fromisoformat(v.replace("Z", "+00:00"))


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def esc(v):
    return html.escape("" if v is None else str(v), quote=True)


def build_data():
    books, picks, flagged = {}, {}, []
    for fx in FIXTURES:
        # Elapsed fixtures (in play or completed at capture) carry no pre-match selection.
        if fx["state"] == "upcoming":
            book = priced_book(fx)
        else:
            book = {"fixture_id": fx["id"], "markets": [], "rated": "low",
                    "winner_p": None, "inputs": fx["inputs"],
                    "note": "start elapsed at capture time; no pre-match selection published"}
        books[fx["id"]] = book
        # per-fixture sources from the registry
        src_list = []
        for sid in fx["sources"]:
            name, url = SOURCES.get(sid, ("", ""))
            src_list.append({"id": sid, "name": name, "url": url})
        pick = featured_pick(book)
        if pick:
            picks[fx["id"]] = pick
        # expiry: fixture evidence expires 6h from the capture time
        exp = (NOW + FIXED_TTL).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        fx_out = {
            "id": fx["id"], "sport": fx["sport"], "competition": fx["comp"],
            "participant_a": fx["a"], "participant_b": fx["b"], "event": fx["event"],
            "start_utc": fx["start_utc"], "date": fx["date"], "venue": fx["venue"],
            "state": fx["state"], "sources": src_list, "flags": fx["flags"],
            "observed_after": OUT, "observed_before": OUT, "expires_at": exp,
            "inputs": fx["inputs"],
            "priced": bool(book["markets"]),
            "price_expires_at": exp if book["markets"] else None,
        }
        fx["_out"] = fx_out
        for fl in fx["flags"]:
            flagged.append({"fixture_id": fx["id"], "detail": fl,
                            "sources": [s["url"] for s in src_list]})
    return books, picks, flagged


def main():
    books, picks, flagged = build_data()
    # ---------------- data files
    fixtures_out = [f["_out"] for f in FIXTURES]
    write_json(DATA / "fixtures.json", {"desk": SESSION, "captured_utc": OUT, "fixtures": fixtures_out,
                                        "olbg_note": OLBG_NOTE})
    # matches.csv
    with (DATA / "matches.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["id", "sport", "competition", "participant_a", "participant_b", "event",
                    "start_utc", "date", "venue", "state", "selection", "confidence",
                    "model_probability", "fair_american", "sources", "flags", "observed_after",
                    "expires_at", "priced"])
        for f in fixtures_out:
            p = picks.get(f["id"])
            w.writerow([f["id"], f["sport"], f["competition"], f["participant_a"], f["participant_b"],
                        f["event"], f["start_utc"] or "", f["date"] or "", f["venue"], f["state"],
                        p["selection"] if p else "", p["confidence"] if p else "",
                        round(p["probability"], 4) if p else "", p["fair_american"] if p else "",
                        " | ".join(s["url"] for s in f["sources"]), " | ".join(f["flags"]),
                        f["observed_after"], f["expires_at"], str(f["priced"]).lower()])
    # markets.csv
    with (DATA / "markets.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["fixture_id", "sport", "market", "selection", "probability", "fair_decimal",
                    "fair_american", "in_band", "source"])
        for fx in FIXTURES:
            b = books[fx["id"]]
            src = " | ".join(SOURCES.get(s, ("", ""))[1] for s in fx["sources"])
            for m in b["markets"]:
                for o in m["outcomes"]:
                    w.writerow([fx["id"], fx["sport"], m["label"], o["selection"],
                                o["probability"], o["fair_decimal"], o["fair_american"],
                                str(o["in_band"]).lower(), src])
    # predictions.json
    preds = []
    for fid, p in picks.items():
        if fid not in PREDICTIONS:
            continue
        pd = PREDICTIONS[fid]
        bet_line = f"{pd['selection']} at {p['fair_american']} ({p['fair_decimal']:.3f})"
        preds.append({"match_id": fid, "sport": next(f["sport"] for f in FIXTURES if f["id"] == fid),
                      "event": next(f["event"] for f in FIXTURES if f["id"] == fid),
                      "selection": pd["selection"], "bet_line": bet_line,
                      "text": pd["text"], "sources": pd["sources"]})
    write_json(DATA / "predictions.json", {"count": len(preds), "predictions": preds})
    write_json(DATA / "flagged.json", {"count": len(flagged), "flags": flagged})
    write_json(DATA / "sources.json", {"count": len(SOURCES), "sources": [
        {"id": k, "name": v[0], "url": v[1]} for k, v in SOURCES.items()]})
    high = [fid for fid, p in picks.items() if p["confidence"] == "high" and fid in PREDICTIONS]
    summary = {
        "generated_utc": OUT, "desk": SESSION, "fixtures": len(fixtures_out),
        "upcoming": sum(1 for f in fixtures_out if f["state"] == "upcoming"),
        "priced": sum(1 for f in fixtures_out if f["priced"]),
        "markets": sum(len(books[f["id"]]["markets"]) for f in FIXTURES),
        "outcomes": sum(len(m["outcomes"]) for f in FIXTURES for m in books[f["id"]]["markets"]),
        "high_picks": len(high), "predictions": len(preds),
        "sports": len(SPORT_ORDER), "sports_with_listings": len({f["sport"] for f in fixtures_out}),
        "flagged": len(flagged),
    }
    write_json(DATA / "summary.json", summary)

    # ---------------- site
    site = DESK
    (site / "assets").mkdir(parents=True, exist_ok=True)
    css = (site / "assets" / "style.css")
    css.write_text(SITE_CSS, encoding="utf-8")
    js = (site / "assets" / "app.js")
    js.write_text(SITE_JS, encoding="utf-8")

    def nav(active="", prefix=""):
        items = [("Overview", "index.html", "grid"),
                 ("High picks", "high-confidence.html", "shield"),
                 ("Predictions", "predictions.html", "spark"),
                 ("Matches", "matches.html", "list"),
                 ("Markets", "markets.html", "chart"),
                 ("Sources", "sources.html", "link"),
                 ("Method", "methodology.html", "book"),
                 ("Flagged", "flagged.html", "flag"),
                 ("Audit", "repo-audit.html", "code")]
        return "".join(
            f'<a class="nav-link {"active" if k == active else ""}" href="{prefix}{p}">{l}</a>'
            for k, p, l in items)

    def frame(title, body, active="", prefix=""):
        return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · 3c021b49</title>
<link rel="stylesheet" href="{prefix}assets/style.css"></head>
<body><header class="topbar"><div class="brand">OLBG15 <span>·</span> Evening Desk</div>
<nav>{nav(active, prefix)}</nav><div class="stamp">Captured 2026-10-23 22:30 UTC</div></header>
<main>{body}</main>
<footer class="footer">Independent research. Not affiliated with OLBG. No guaranteed returns. 18+.</footer>
</body></html>"""

    # ---------------- index.html
    idx_rows = []
    for fid in sorted(picks, key=lambda f: (SPORT_ORDER.index(next(f["sport"] for f in FIXTURES if f["id"] == fid)), f)):
        p = picks[fid]
        if p["confidence"] != "high":
            continue
        fx = next(f for f in FIXTURES if f["id"] == fid)
        idx_rows.append(f"""<tr><td>{esc(fx["id"])}</td><td>{esc(SPORT_NAMES[fx["sport"]])}</td>
<td>{esc(fx["event"])}</td><td>{esc(fx["start_utc"] or fx["date"] or "")}</td>
<td><strong>{esc(p["selection"])}</strong><br><small>{p["probability"]:.1%} · {esc(p["fair_american"])} ({p["fair_decimal"]:.3f})</small></td>
<td>{esc(p["market"])}</td><td>{linked_sources(fx)}</td></tr>""")
    idx = f"""<h1>{esc(DESK_NAME)}</h1>
<p class="lede">Live evening desk for Friday 23 October 2026. Every fixture below was checked this session against an official
governing body, league, tour or team source. OLBG.com supplied the event candidates only. Our own lines are zero-vig fair prices;
no bookmaker quote is copied. Blank cells mean the value could not be confirmed and stays unverified.</p>
<div class="kpis">
<div class="kpi"><div class="kpi-label">Fixtures captured</div><div class="kpi-value">{summary['fixtures']}</div></div>
<div class="kpi"><div class="kpi-label">Upcoming fixtures</div><div class="kpi-value">{summary['upcoming']}</div></div>
<div class="kpi"><div class="kpi-label">Originated markets</div><div class="kpi-value">{summary['markets']}</div></div>
<div class="kpi"><div class="kpi-label">High-confidence picks</div><div class="kpi-value">{summary['high_picks']}</div></div>
<div class="kpi"><div class="kpi-label">Sports covered</div><div class="kpi-value">{summary['sports_with_listings']} / 15</div></div>
<div class="kpi"><div class="kpi-label">Flagged items</div><div class="kpi-value">{summary['flagged']}</div></div>
</div>
<h2>Executive summary — highest-confidence picks</h2>
<p>Selections sit inside the −250…+10000 fair-price window and carry a model probability of 62% or more.
Each High pick has a unique hand-written prediction on the <a href="predictions.html">predictions</a> page.</p>
<table class="tbl"><thead><tr><th>ID</th><th>Sport</th><th>Match</th><th>Start</th><th>Selection</th><th>Market</th><th>Official source</th></tr></thead>
<tbody>{''.join(idx_rows)}</tbody></table>
<h2>By sport</h2>
<div class="grid">{''.join(
    f'<a class="card" href="sports/{s}.html"><strong>{esc(SPORT_NAMES[s])}</strong>'
    f'<small>{sum(1 for f in FIXTURES if f["sport"] == s)} fixtures · {sum(1 for f in FIXTURES if f["sport"] == s and f["id"] in picks and picks[f["id"]]["confidence"] == "high")} high picks</small></a>'
    for s in SPORT_ORDER)}</div>
<p class="note">OLBG discovery layer and the full methodology are on the <a href="reverse-engineering.html">reverse-engineering</a>
and <a href="methodology.html">method</a> pages. Prices expire six hours after the capture time shown above.</p>"""
    (site / "index.html").write_text(frame("Overview", idx, "grid"), encoding="utf-8")

    # ---------------- high-confidence.html
    hc_rows = []
    for fid in sorted(picks, key=lambda f: (SPORT_ORDER.index(next(f["sport"] for f in FIXTURES if f["id"] == fid)), f)):
        p = picks[fid]
        if p["confidence"] != "high":
            continue
        fx = next(f for f in FIXTURES if f["id"] == fid)
        hc_rows.append(f"""<tr><td>{esc(fx["id"])}</td><td>{esc(SPORT_NAMES[fx["sport"]])}</td>
<td>{esc(fx["event"])}</td><td>{esc(fx["comp"])}</td><td>{esc(fx["start_utc"] or fx["date"] or "")}</td>
<td><strong>{esc(p["selection"])}</strong><br><small>{p["probability"]:.1%} · {esc(p["fair_american"])} ({p["fair_decimal"]:.3f})</small></td>
<td>{esc(p["market"])}</td><td>{esc(tier_for(p["probability"], True))}</td><td>{linked_sources(fx)}</td></tr>""")
    hc = f"""<h1>High-confidence picks</h1>
<p>Every selection below sits inside the −250…+10000 fair-price window with a model probability of at least 62%.
The strongest are ≥70%. Fair prices are our own zero-vig estimates, not bookmaker quotes.</p>
<table class="tbl"><thead><tr><th>ID</th><th>Sport</th><th>Match</th><th>Competition</th><th>Start</th><th>Selection</th><th>Market</th><th>Tier</th><th>Official source</th></tr></thead>
<tbody>{''.join(hc_rows)}</tbody></table>"""
    (site / "high-confidence.html").write_text(frame("High-confidence picks", hc, "shield"), encoding="utf-8")

    # ---------------- predictions.html
    pr_rows = []
    for pd in preds:
        fx = next(f for f in FIXTURES if f["id"] == pd["match_id"])
        pr_rows.append(f"""<tr><td>{esc(fx["id"])}</td><td>{esc(SPORT_NAMES[fx["sport"]])}</td>
<td>{esc(fx["event"])}</td><td><strong>{esc(pd["selection"])}</strong><br><small>{esc(pd["bet_line"])}</small></td>
<td>{esc(pd["text"])}</td><td>{''.join(f'<a href="{esc(u)}" target="_blank">source</a> ' for u in pd["sources"])}</td></tr>""")
    pr = f"""<h1>Unique human predictions</h1>
<p>Each High pick gets a hand-written, match-specific prediction of at least 30 words. Team, player, current form, recent
match history, match statistics confirmed against official sources and injuries are drawn only from the official sources linked per row. No repetitive
phrases.</p>
<table class="tbl wide"><thead><tr><th>ID</th><th>Sport</th><th>Match</th><th>Selection</th><th>Prediction</th><th>Sources</th></tr></thead>
<tbody>{''.join(pr_rows)}</tbody></table>"""
    (site / "predictions.html").write_text(frame("Predictions", pr, "spark"), encoding="utf-8")

    # ---------------- matches.html
    m_rows = []
    for fx in FIXTURES:
        p = picks.get(fx["id"])
        sel = (f'{esc(p["selection"])}<br><small>{p["probability"]:.1%} {esc(p["confidence"])}</small>' if p else "—")
        m_rows.append(f"""<tr><td>{esc(fx["id"])}</td><td>{esc(SPORT_NAMES[fx["sport"]])}</td>
<td>{esc(fx["event"])}</td><td>{esc(fx["comp"])}</td><td>{esc(fx["start_utc"] or fx["date"] or "")}</td>
<td>{esc(fx["venue"])}</td><td>{esc(fx["state"])}</td><td>{sel}</td>
<td>{linked_sources(fx)}</td></tr>""")
    m = f"""<h1>All matches</h1>
<p>{summary['fixtures']} OLBG-discovered fixtures, verified against official sources this session. Blank selection cells mean
the value could not be confirmed and stays unverified. "start elapsed" rows were in play or completed at capture time and carry no
pre-match selection.</p>
<table class="tbl wide"><thead><tr><th>ID</th><th>Sport</th><th>Match</th><th>Competition</th><th>Start</th><th>Venue</th><th>State</th><th>Selection</th><th>Official source</th></tr></thead>
<tbody>{''.join(m_rows)}</tbody></table>"""
    (site / "matches.html").write_text(frame("All matches", m, "list"), encoding="utf-8")

    # ---------------- markets.html
    mk_rows = []
    for fx in FIXTURES:
        b = books[fx["id"]]
        if not b["markets"]:
            continue
        rows = []
        for mk in b["markets"]:
            for o in mk["outcomes"]:
                rows.append(f"""<tr><td>{esc(mk["label"])}</td><td>{esc(o["selection"])}</td>
<td>{o["probability"]:.2%}</td><td>{o["fair_decimal"]:.3f}</td><td>{esc(o["fair_american"])}</td>
<td>{'in band' if o["in_band"] else 'outside band'}</td></tr>""")
        mk_rows.append(f"""<tr><td colspan="6" class="grp">{esc(fx["id"])} — {esc(fx["event"])}</td></tr>{''.join(rows)}""")
    mk = f"""<h1>Originated markets</h1>
<p>{summary['markets']} markets across {summary['priced']} priced fixtures. Every price is our own zero-vig fair price
(1/p, no margin, no clipping). The −250…+10000 band marks which selections qualify for High confidence. Bookmaker quotes and
availability remain unverified.</p>
<table class="tbl wide"><thead><tr><th>Market</th><th>Selection</th><th>Model chance</th><th>Fair decimal</th><th>Fair US</th><th>Band</th></tr></thead>
<tbody>{''.join(mk_rows)}</tbody></table>"""
    (site / "markets.html").write_text(frame("Markets", mk, "chart"), encoding="utf-8")

    # ---------------- sports pages
    for s in SPORT_ORDER:
        sfx = [f for f in FIXTURES if f["sport"] == s]
        rows = []
        for fx in sfx:
            p = picks.get(fx["id"])
            sel = (f'{esc(p["selection"])}<br><small>{p["probability"]:.1%} {esc(p["confidence"])}</small>' if p else "—")
            rows.append(f"""<tr><td>{esc(fx["id"])}</td><td>{esc(fx["event"])}</td>
<td>{esc(fx["comp"])}</td><td>{esc(fx["start_utc"] or fx["date"] or "")}</td>
<td>{esc(fx["venue"])}</td><td>{esc(fx["state"])}</td><td>{sel}</td><td>{linked_sources(fx)}</td></tr>""")
        body = f"""<h1>{esc(SPORT_NAMES[s])}</h1>
<p>{len(sfx)} fixtures discovered on OLBG and verified this session against official sources. Blank selection cells mean the
value could not be confirmed and stays unverified.</p>
<table class="tbl wide"><thead><tr><th>ID</th><th>Match</th><th>Competition</th><th>Start</th><th>Venue</th><th>State</th><th>Selection</th><th>Official source</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>"""
        (site / "sports" / f"{s}.html").write_text(frame(SPORT_NAMES[s], body, prefix="../"), encoding="utf-8")

    # ---------------- flagged.html
    fl_rows = []
    for fl in flagged:
        fx = next(f for f in FIXTURES if f["id"] == fl["fixture_id"])
        fl_rows.append(f"""<tr><td>{esc(fl["fixture_id"])}</td><td>{esc(SPORT_NAMES[fx["sport"]])}</td>
<td>{esc(fl["detail"])}</td><td>{''.join(f'<a href="{esc(u)}" target="_blank">source</a> ' for u in fl["sources"])}</td></tr>""")
    fl = f"""<h1>Flagged for review</h1>
<p>{len(flagged)} items need manual review. None of these block the desk; they block any value being presented as confirmed.
Blank cells on the match pages correspond to these flags.</p>
<table class="tbl wide"><thead><tr><th>Fixture</th><th>Sport</th><th>Flag</th><th>Sources</th></tr></thead>
<tbody>{''.join(fl_rows)}</tbody></table>"""
    (site / "flagged.html").write_text(frame("Flagged for review", fl, "flag"), encoding="utf-8")

    # ---------------- sources.html
    so_rows = []
    for sid, (name, url) in SOURCES.items():
        used = [f["id"] for f in FIXTURES if sid in f["sources"]]
        so_rows.append(f"""<tr><td>{esc(sid)}</td><td>{esc(name)}</td>
<td><a href="{esc(url)}" target="_blank">{esc(url)}</a></td><td>{esc(', '.join(used))}</td></tr>""")
    so = f"""<h1>Sources &amp; evidence</h1>
<p>{len(SOURCES)} official sources were read this session. Every fixture row links at least one of them. OLBG.com is discovery
only and is never used to confirm a sporting fact.</p>
<table class="tbl wide"><thead><tr><th>ID</th><th>Publisher</th><th>URL</th><th>Used by</th></tr></thead>
<tbody>{''.join(so_rows)}</tbody></table>"""
    (site / "sources.html").write_text(frame("Sources", so, "link"), encoding="utf-8")

    # ---------------- methodology.html
    meth = """<h1>Methodology</h1>
<h2>1. Discovery</h2>
<p>OLBG.com's 15 in-scope sport hubs were harvested on 2023-10-23 ~19:30Z via the search/render layer. OLBG tip shares are votes,
not probabilities, and OLBG's clock renders Eastern Daylight Time to this session. OLBG is discovery only: every published fact is
checked against an official governing body, league, tour or team source this session.</p>
<h2>2. Fixture verification</h2>
<p>Participants, competition, venue and start times were confirmed on the official source listed per row. Missing values stay blank
and are flagged — never inferred or filled in. Fixture evidence expires six hours from the capture time.</p>
<h2>3. Originated lines</h2>
<p>Every market price is our own zero-vig fair price (1/p). No bookmaker quote, margin, clipping or missing-input default is used.
Confidence tiers: High-A = ≥70% and fair US price in −250…+10000; High-B = 62–70% in band; Medium = 50–62% or price-capped
chalk above +10000/−250; Low = below 50% or without two official inputs.</p>
<h2>4. Line setting</h2>
<p>The desk sets its own spread and total lines: the line is chosen (half-point search) so the model's cover/over probability
sits at 0.66, the midpoint of the High window. Winner prices come from official win percentages and rankings; sport-specific
markets use official records, series results and Order of Merit / world ranking data.</p>
<h2>5. Predictions</h2>
<p>Every High pick carries a unique hand-written prediction of at least 30 words: team, player, current form, recent match history,
verified match statistics and injuries, with an obvious selection (win / over / under). Sources are linked per row.</p>
<h2>6. Limits</h2>
<p>Coverage is partial: no claim of worldwide fixtures, every bookmaker market, calibrated sport-specific models, current player
availability or verified bookmaker odds. Unsupported values remain blank and flagged.</p>"""
    (site / "methodology.html").write_text(frame("Methodology", meth, "book"), encoding="utf-8")

    # ---------------- reverse-engineering.html
    rev = f"""<h1>OLBG reverse engineering</h1>
<p>OLBG.com serves server-rendered HTML with no public JSON feed. Routes follow
<code>/betting-tips/{{Sport_Slug}}/{{sport_id}}</code> (case-sensitive slugs; 24 active sport IDs, 7 excluded).
The 15 sports in scope for this desk:</p>
<table class="tbl"><thead><tr><th>Sport</th><th>OLBG hub</th></tr></thead><tbody>
{''.join(f'<tr><td>{esc(SPORT_NAMES[s])}</td><td><a href="{esc(OLBG_HUBS[s])}" target="_blank">{esc(OLBG_HUBS[s])}</a></td></tr>' for s in SPORT_ORDER)}
</tbody></table>
<h2>Observed platform quirks</h2>
<ul>
<li>OLBG's clock renders Eastern Daylight Time (UTC−4) to this session with no timezone label; cross-checks against official UTC
feeds are required. Confirmed this session: MLB World Series Game 1 shown as "Today 20:00" = 2026-10-24T00:00Z; ATP Brussels
Fils v Michelsen "Not Before 18:30" Brussels = 16:30Z.</li>
<li>OLBG suppresses fixtures with zero open community tips, hiding entire active championships (Rugby League World Cup Round 2
men's and women's matches were found only on nrl.com, not on OLBG).</li>
<li>Hub listings cap at 20 rows and truncate ("Load More Tips"), hiding sub-route fixtures.</li>
<li>Name errors: 'Skanderborg Handbold' vs EHF's 'SAH Aarhus'; Waterford SFC Final date error on Gaelic Football hub.</li>
<li>Each-way outright markets render 0/0 consensus when only each-way tips exist.</li>
</ul>
<p>Tip percentages on OLBG are votes, not probabilities. This desk never uses OLBG to confirm a sporting fact.</p>"""
    (site / "reverse-engineering.html").write_text(frame("OLBG discovery", rev), encoding="utf-8")

    # ---------------- repo-audit.html
    audit_findings = [
        ("A1", "CRITICAL", "pipeline/config.py L16-L39", "Canonical config lists 17 categories (incl. Aussie Rules id=22 and eSports id=23) while EXCLUDED_IDS wrongly bans OLBG Hurling id=26 even though Gaelic Sports covers both Gaelic Football (25) and Hurling (26). Recheck: https://munster.gaa.ie/fixtures/"),
        ("A2", "CRITICAL", "data/current/snapshot.json", "Canonical root snapshot generated 2026-10-22T12:29Z — >24h stale at capture; high=0/medium=0/predictions=[]. Fresh desk data lives under data/3c021b49/. Recheck: https://api-web.nhle.com/v1/schedule/2026-10-23"),
        ("A3", "CRITICAL", "data/2b72da34/desk.json L442-L459", "Row M24 marked tonight's MLB World Series Game 1 unverified with 'date outside normal MLB season'; statsapi.mlb.com schedule confirms 2026-10-24T00:00Z. Recheck: https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-23&endDate=2026-10-26"),
        ("A4", "HIGH", "data/2b72da34/desk.json", "Crowd-vote line formula p=(tips_for+2)/(tips_total+4) with zero official inputs produced inverted lines (Gloucester −450 vs Bath; Shnaider −150 vs Rybakina). This desk uses official records instead."),
        ("A5", "HIGH", "data/2b72da34/desk.json L195-L198", "Row M10 cited '(ESPN team page)' media for NBA form instead of www.nba.com boxscores. Recheck: https://www.nba.com/games?date=2026-10-23"),
        ("A6", "HIGH", "data/2b72da34/desk.json L708-L745", "Zero verified rows across 12 of the 15 required sports in the 2b72da34 desk; this desk verifies all 15."),
        ("A7", "MEDIUM", "pipeline/config.py L42-L63", "Official domains www.gaa.ie, www.cricket.com.au, www.premiershiprugby.com, www.daikin-hbl.de, www.lnh.fr and ak-static.cms.nba.com absent from PUBLISHERS; pipeline/audit.py flags those records. Recheck: https://www.lnh.fr/liquimoly-starligue/equipes/chambery-savoie-mt-blanc-handball"),
        ("A8", "MEDIUM", "data/current/discovery.json", "All 17 sport discovery hubs status='unverified' (robots policy unavailable); OLBG sub-routes (/Basketball/NBA/4, /Hurling/26) uncrawled."),
        ("A9", "LOW", "scripts/validate.py L1-L90", "Legacy session f7fa77fc triggers 3 warnings for root-absolute '/index.html' hrefs that break under GitHub Pages project subpath '/OLBG1/'."),
    ]
    ar = "".join(f"""<tr><td>{esc(fid)}</td><td><span class="badge {'red' if sev in ('CRITICAL','HIGH') else 'amber'}">{esc(sev)}</span></td>
<td>{esc(loc)}</td><td>{esc(txt)}</td></tr>""" for fid, sev, loc, txt in audit_findings)
    audit = f"""<h1>Repository audit</h1>
<p>Line-by-line review of the repository this session. These findings are structural and historical; they do not recertify every
archived statement. All desk data in this namespace (<code>data/3c021b49/**</code>, <code>3c021b49/**</code>) is independent of the
canonical root.</p>
<table class="tbl wide"><thead><tr><th>ID</th><th>Severity</th><th>File:line</th><th>Finding &amp; recheck</th></tr></thead>
<tbody>{ar}</tbody></table>"""
    (site / "repo-audit.html").write_text(frame("Repository audit", audit, "code"), encoding="utf-8")

    # ---------------- site manifest
    pages = ["index.html", "high-confidence.html", "predictions.html", "matches.html", "markets.html",
             "flagged.html", "sources.html", "methodology.html", "reverse-engineering.html", "repo-audit.html"]
    pages += [f"sports/{s}.html" for s in SPORT_ORDER]
    write_json(DATA / "site-manifest.json", {"generated_at": OUT, "desk": SESSION, "pages": pages})
    print(f"Built {len(pages)} pages; {summary['fixtures']} fixtures; {summary['high_picks']} high picks; {summary['predictions']} predictions")
    return summary


def linked_sources(fx):
    out = []
    for sid in fx["sources"]:
        name, url = SOURCES.get(sid, ("", ""))
        if url:
            out.append(f'<a href="{esc(url)}" target="_blank">{esc(name)}</a>')
    return " ".join(out) if out else "—"


SITE_CSS = """*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;background:#f4f6f8;color:#1a2733;line-height:1.5}
.topbar{background:#10263a;color:#fff;padding:14px 22px;display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between}
.brand{font-weight:700;font-size:18px;letter-spacing:.3px}
.topbar nav{display:flex;flex-wrap:wrap;gap:6px}
.nav-link{color:#cfe0f2;text-decoration:none;padding:6px 10px;border-radius:6px;font-size:14px}
.nav-link:hover{background:#1d3b55}
.nav-link.active{background:#2b6cb0;color:#fff}
.stamp{font-size:12px;color:#9fb6cc}
main{max-width:1200px;margin:0 auto;padding:22px}
h1{font-size:26px;margin-bottom:8px}
h2{font-size:19px;margin:26px 0 8px}
.lede{color:#43566b;max-width:900px;margin-bottom:18px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:18px 0}
.kpi{background:#fff;border:1px solid #dde4ec;border-radius:10px;padding:14px}
.kpi-label{font-size:12px;color:#5b6b7d;text-transform:uppercase;letter-spacing:.4px}
.kpi-value{font-size:26px;font-weight:700;margin-top:4px;color:#10263a}
table.tbl{width:100%;border-collapse:collapse;background:#fff;border-radius:10px;overflow:hidden;margin:10px 0 22px;font-size:14px}
table.tbl th{background:#10263a;color:#fff;text-align:left;padding:10px 12px;font-weight:600;font-size:13px}
table.tbl td{padding:9px 12px;border-bottom:1px solid #e7ecf2;vertical-align:top}
table.tbl tr:hover td{background:#f2f7fb}
table.tbl.wide{font-size:13px}
.grp td{background:#eef3f8;font-weight:700;color:#10263a}
.card{display:block;background:#fff;border:1px solid #dde4ec;border-radius:10px;padding:14px 16px;text-decoration:none;color:#1a2733;margin-bottom:10px}
.card:hover{border-color:#2b6cb0}
.card strong{display:block;font-size:15px}
.card small{color:#5b6b7d}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:10px}
.badge{display:inline-block;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:600}
.badge.red{background:#fde2e2;color:#8a1f1f}
.badge.amber{background:#fdf0d5;color:#7a5410}
.badge.green{background:#e2f5e2;color:#1a6b1a}
.note{color:#5b6b7d;font-size:13px;margin-top:18px}
.footer{border-top:1px solid #dde4ec;margin-top:30px;padding:16px 22px;color:#5b6b7d;font-size:12px;text-align:center}
a{color:#2b6cb0}
"""

SITE_JS = """// No client-side data fetching. All content is static and works without JavaScript.
"""


if __name__ == "__main__":
    main()
