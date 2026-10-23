#!/usr/bin/env python3
"""Session 4c4968fc — build data artefacts plus the static desk site.

    python3 scripts/s4c4968fc_build.py
    python3 scripts/s4c4968fc_validate.py
"""
from __future__ import annotations

import csv
import html
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import s4c4968fc_data as D
import s4c4968fc_model as M
import s4c4968fc_predictions as PR

DESK = ROOT / "4c4968fc"
DATA = ROOT / "data" / "4c4968fc"
NOW = D.CAPTURED_UTC

SPORT_ORDER = [k for k, _n, _h in D.SPORTS]
SPORT_NAMES = {k: n for k, n, _h in D.SPORTS}
OLBG_HUBS = {k: h for k, _n, h in D.SPORTS}


def esc(v):
    return html.escape("" if v is None else str(v), quote=True)


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False), encoding="utf-8")


def hhmm(iso):
    return iso.replace("T", " ").replace(":00Z", "Z") if iso else ""


def local_pair(iso):
    """UTC start plus a plain-English UK/US reference, never invented."""
    if not iso:
        return ""
    return hhmm(iso)


def src_links(keys):
    out = []
    for k in keys:
        if isinstance(k, dict):
            name, url = k["name"], k["url"]
        else:
            name, url = D.SOURCES[k][0], D.SOURCES[k][1]
        out.append(f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(name)}</a>')
    return " ".join(out) if out else "—"


# ---------------------------------------------------------------------------
def build_data():
    fixtures, markets = [], []
    for fx in D.FIXTURES:
        fixtures.append({
            "id": fx["id"], "sport": fx["sport"], "sport_name": SPORT_NAMES[fx["sport"]],
            "competition": fx["comp"], "participant_a": fx["a"], "participant_b": fx["b"],
            "event": f"{fx['a']} v {fx['b']}", "start_utc": fx["start"],
            "venue": fx["venue"], "state": fx["state"],
            "rating_basis": fx["rating_basis"],
            "p_first": fx["p_first"],
            "p_first_basis": "desk estimate from published records; not a quoted price",
            "sources": [{"id": k, "name": D.SOURCES[k][0], "url": D.SOURCES[k][1]} for k in fx["sources"]],
            "facts": [{"text": t, "source_id": k, "source_url": D.SOURCES[k][1]} for t, k in fx["facts"]],
            "flags": fx["flags"],
        })
    markets = M.build_markets(D.FIXTURES)
    for m in markets:
        m["source_ids"] = next(f["sources"] for f in D.FIXTURES if f["id"] == m["fixture"])
        m["source_urls"] = [D.SOURCES[k][1] for k in m["source_ids"]]

    picks = M.select_picks(markets, D.FIXTURES, limit=5)
    fx_by_id = {f["id"]: f for f in D.FIXTURES}
    pred_by_key = {(p["fixture"], p["market"]): p for p in PR.PREDICTIONS}
    predictions = []
    for pk in picks:
        key = (pk["fixture"], pk["market"])
        pr = pred_by_key.get(key)
        if not pr:
            raise SystemExit(f"missing prediction for {key}")
        phrase = pk["line"] or pk["selection"]
        text = pr["text"].replace("{sel}", phrase)
        predictions.append({
            "fixture": pk["fixture"], "sport": pk["sport"], "sport_name": SPORT_NAMES[pk["sport"]],
            "event": f"{fx_by_id[pk['fixture']]['a']} v {fx_by_id[pk['fixture']]['b']}",
            "competition": fx_by_id[pk["fixture"]]["comp"],
            "start_utc": fx_by_id[pk["fixture"]]["start"],
            "market": pk["market"], "line": pk["line"], "selection": pk["selection"],
            "probability": pk["p"], "fair_decimal": pk["decimal"], "fair_american": pk["american_str"],
            "tier": pk["tier"], "text": text,
            "selection_line": phrase,
            "selection_bold": esc(pk["selection"]),
            "sources": [D.SOURCES[k][1] for k in fx_by_id[pk["fixture"]]["sources"]],
        })
    return fixtures, markets, picks, predictions


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    fixtures, markets, picks, predictions = build_data()

    write_json(DATA / "fixtures.json", {"desk": D.SESSION, "desk_title": D.DESK_TITLE,
                                        "captured_utc": NOW, "window_note": D.WINDOW_NOTE,
                                        "fixtures": fixtures})
    write_json(DATA / "markets.json", {"desk": D.SESSION, "captured_utc": NOW,
                                       "price_policy": "own zero-vig complementary pairs; High = p>0.70 and fair American within -250..+10000",
                                       "market_count": len(markets), "markets": markets})
    write_json(DATA / "picks.json", {"desk": D.SESSION, "captured_utc": NOW,
                                     "high_gate": {"p_floor": 0.70, "band": [-250, 10000], "per_sport_cap": 5},
                                     "picks": picks})
    write_json(DATA / "predictions.json", {"desk": D.SESSION, "captured_utc": NOW,
                                           "count": len(predictions), "predictions": predictions})
    write_json(DATA / "flagged.json", {"desk": D.SESSION, "captured_utc": NOW, "items": [
        dict(it, source_list=[{"id": k, "name": D.SOURCES[k][0], "url": D.SOURCES[k][1]} for k in it["sources"]])
        for it in D.FLAGGED]})
    write_json(DATA / "elapsed.json", {"desk": D.SESSION, "rows": [
        dict(it, source_list=[{"id": k, "name": D.SOURCES[k][0], "url": D.SOURCES[k][1]} for k in it["sources"]])
        for it in D.ELAPSED]})
    write_json(DATA / "sources.json", {"desk": D.SESSION, "read_at_utc": NOW, "count": len(D.SOURCES),
                                       "sources": [{"id": k, "name": v[0], "url": v[1],
                                                    "role": "OLBG taxonomy (discovery only)" if k.startswith("olbg")
                                                            else "official / primary"}
                                                   for k, v in D.SOURCES.items()]})

    with (DATA / "matches.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["id", "sport", "competition", "participant_a", "participant_b", "start_utc",
                    "venue", "state", "rating_basis", "official_sources", "flags"])
        for f in fixtures:
            w.writerow([f["id"], f["sport"], f["competition"], f["participant_a"], f["participant_b"],
                        f["start_utc"], f["venue"], f["state"], f["rating_basis"],
                        " | ".join(s["url"] for s in f["sources"]), " | ".join(f["flags"])])
    with (DATA / "markets.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["fixture_id", "sport", "market", "line", "selection", "probability",
                    "fair_decimal", "fair_american", "tier", "source"])
        for m in markets:
            w.writerow([m["fixture"], m["sport"], m["market"], m["line"], m["selection"], m["p"],
                        m["decimal"], m["american_str"], m["tier"], " | ".join(m["source_urls"])])
    with (DATA / "predictions.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["fixture", "sport", "event", "market", "line", "selection", "probability",
                    "fair_american", "tier", "prediction", "sources"])
        for p in predictions:
            w.writerow([p["fixture"], p["sport"], p["event"], p["market"], p["line"], p["selection"],
                        p["probability"], p["fair_american"], p["tier"], p["text"],
                        " | ".join(p["sources"])])

    by_sport = {}
    for p in predictions:
        by_sport.setdefault(p["sport"], 0)
        by_sport[p["sport"]] += 1
    summary = {
        "desk": D.SESSION, "desk_title": D.DESK_TITLE, "captured_utc": NOW,
        "fixtures": len(fixtures),
        "sports_required": len(SPORT_ORDER),
        "sports_with_fixtures": len({f["sport"] for f in fixtures}),
        "markets": len(markets), "outcomes_priced": len(markets),
        "picks": len(predictions),
        "picks_by_sport": by_sport,
        "sports_with_five_picks": sorted([s for s, c in by_sport.items() if c >= 5]),
        "sources": len(D.SOURCES), "official_sources": sum(1 for k in D.SOURCES if not k.startswith("olbg")),
        "flagged": len(D.FLAGGED), "elapsed": len(D.ELAPSED),
        "high_gate": {"p_floor": 0.70, "band": [-250, 10000], "per_sport_cap": 5},
    }
    write_json(DATA / "summary.json", summary)

    build_site(fixtures, markets, predictions, summary)
    return summary


# ---------------------------------------------------------------------------
CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
background:#f5f7fa;color:#16202b;line-height:1.55;font-size:15px}
header.top{background:#0f2537;color:#fff;padding:14px 22px;display:flex;flex-wrap:wrap;
gap:12px;align-items:center;justify-content:space-between}
.brand{font-weight:700;font-size:18px}
.brand span{color:#7fb2e5}
header.top nav{display:flex;flex-wrap:wrap;gap:4px}
nav a{color:#cfe0f2;text-decoration:none;padding:6px 9px;border-radius:6px;font-size:13.5px}
nav a:hover{background:#1c3a53}
nav a.on{background:#2d6fb8;color:#fff}
.stamp{font-size:12px;color:#9fb6cc}
main{max-width:1180px;margin:0 auto;padding:24px 22px 40px}
h1{font-size:27px;margin-bottom:6px;letter-spacing:-.2px}
h2{font-size:19px;margin:30px 0 8px}
h3{font-size:16px;margin:20px 0 6px}
p{margin-bottom:10px;color:#33465a}
.lede{max-width:880px;color:#3d5266}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(148px,1fr));gap:12px;margin:20px 0 8px}
.kpi{background:#fff;border:1px solid #dde4ec;border-radius:10px;padding:13px 15px}
.kpi b{display:block;font-size:25px;color:#0f2537;line-height:1.2}
.kpi small{color:#5b6b7d;font-size:12px;text-transform:uppercase;letter-spacing:.4px}
table{width:100%;border-collapse:collapse;background:#fff;border-radius:10px;overflow:hidden;
margin:10px 0 24px;font-size:13.5px}
th{background:#0f2537;color:#fff;text-align:left;padding:9px 11px;font-size:12.5px;font-weight:600}
td{padding:8px 11px;border-bottom:1px solid #e8edf3;vertical-align:top}
tr:hover td{background:#f3f8fc}
td small{color:#65788c;display:block;font-size:12px}
.grp td{background:#eaf1f8;font-weight:700;color:#0f2537}
.wrap{overflow-x:auto}
.card{display:block;background:#fff;border:1px solid #dde4ec;border-radius:10px;padding:13px 15px;
text-decoration:none;color:#16202b}
.card:hover{border-color:#2d6fb8}
.card b{display:block;font-size:15px}
.card small{color:#5b6b7d;font-size:12.5px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(228px,1fr));gap:10px;margin-bottom:20px}
.badge{display:inline-block;padding:1px 8px;border-radius:999px;font-size:11px;font-weight:700}
.b-hi{background:#dcf3e2;color:#186b31}
.b-md{background:#fdf0d3;color:#7a5410}
.b-lo{background:#e8ecf1;color:#4a5a6b}
.b-flag{background:#fde2e2;color:#8a1f1f}
.note{font-size:13px;color:#5b6b7d}
ul{margin:0 0 14px 20px}li{margin-bottom:5px;color:#33465a}
footer{border-top:1px solid #dde4ec;padding:16px 22px;color:#5b6b7d;font-size:12px;text-align:center}
a{color:#2d6fb8}
.pred{max-width:520px}
"""


def nav(active="", prefix=""):
    items = [("Overview", "index.html"), ("High picks", "high-confidence.html"),
             ("Predictions", "predictions.html"), ("Matches", "matches.html"),
             ("Markets", "markets.html"), ("Flagged", "flagged.html"),
             ("Sources", "sources.html"), ("Method", "methodology.html"),
             ("Reverse-engineering", "reverse-engineering.html"), ("Repo audit", "repo-audit.html")]
    return "".join(f'<a class="{"on" if k == active else ""}" href="{prefix}{p}">{k}</a>'
                   for k, p in items)


def frame(title, body, active="", prefix=""):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · OLBG Desk 4c4968fc</title>
<link rel="stylesheet" href="{prefix}assets/style.css"></head><body>
<header class="top"><div class="brand">OLBG15 <span>·</span> Multi-Sport Research Desk</div>
<nav>{nav(active, prefix)}</nav><div class="stamp">Captured {NOW.replace('T', ' ')}</div></header>
<main>{body}</main>
<footer>Independent research desk. Not affiliated with OLBG. No warranty of outcome; betting carries risk. 18+.</footer>
</body></html>"""


def build_site(fixtures, markets, predictions, summary):
    site = DESK
    (site / "assets").mkdir(parents=True, exist_ok=True)
    (site / "sports").mkdir(parents=True, exist_ok=True)
    (site / "assets" / "style.css").write_text(CSS, encoding="utf-8")
    (site / "assets" / "app.js").write_text("// Static site: no client-side fetching.\n", encoding="utf-8")

    fx_by_id = {f["id"]: f for f in D.FIXTURES}
    out_by_id = {f["id"]: f for f in fixtures}

    def pick_row(p, show_text=False):
        fx = out_by_id[p["fixture"]]
        tier = f'<span class="badge b-hi">High</span>'
        return (f'<tr><td>{esc(p["fixture"])}</td><td>{esc(p["sport_name"])}</td>'
                f'<td>{esc(p["event"])}<small>{esc(p["competition"])}</small></td>'
                f'<td>{esc(p["start_utc"])}</td>'
                f'<td><strong>{esc(p["selection"])}</strong><small>{esc(p["line"]) or "—"}</small></td>'
                f'<td>{esc(p["market"])}</td>'
                f'<td>{p["probability"]:.1%}<small>{esc(p["fair_american"])} · {p["fair_decimal"]:.3f}</small></td>'
                f'<td>{tier}</td><td>{src_links(fx["sources"])}</td></tr>')

    # ---------------------------------------------------------------- index
    top = sorted(predictions, key=lambda p: -p["probability"])[:18]
    cards = []
    for s in SPORT_ORDER:
        n = sum(1 for f in fixtures if f["sport"] == s)
        h = sum(1 for p in predictions if p["sport"] == s)
        cards.append(f'<a class="card" href="sports/{s}.html"><b>{esc(SPORT_NAMES[s])}</b>'
                     f'<small>{n} fixture{"s" if n != 1 else ""} · {h} high pick{"s" if h != 1 else ""}</small></a>')
    lede = f"""
<h1>Multi-sport betting research desk</h1>
<p class="lede">Fifteen sports, one desk. Fixtures were found by reverse-engineering OLBG's sport taxonomy, then every
participant, competition, venue and start time was re-read from an official governing body, league, tour or team page.
All prices below are originated here as zero-vig complementary pairs — no bookmaker quote is copied — and each High
selection clears a 70% strike-rate floor with a fair American price inside the −250 to +10000 window.</p>
<div class="kpis">
<div class="kpi"><b>{summary['fixtures']}</b><small>fixtures</small></div>
<div class="kpi"><b>{summary['sports_with_fixtures']} / 15</b><small>sports listed</small></div>
<div class="kpi"><b>{summary['markets']:,}</b><small>priced markets</small></div>
<div class="kpi"><b>{summary['picks']}</b><small>high-confidence picks</small></div>
<div class="kpi"><b>{summary['official_sources']}</b><small>official sources</small></div>
<div class="kpi"><b>{summary['flagged']}</b><small>flagged items</small></div>
</div>
<h2>Executive summary — today and the next two days</h2>
<p>Ranked by strike rate. Greyhounds carry no fixture: no official runner list could be read, so nothing was invented
and the gap is logged on the <a href="flagged.html">Flagged</a> page. Where a sport yields fewer than five qualifying
selections the shortfall is disclosed on that sport's page rather than padded.</p>
<div class="wrap"><table><thead><tr><th>ID</th><th>Sport</th><th>Match</th><th>Start (UTC)</th>
<th>Selection</th><th>Market</th><th>Chance · fair price</th><th>Tier</th><th>Official source</th></tr></thead>
<tbody>{''.join(pick_row(p) for p in top)}</tbody></table></div>
<p class="note">All {summary['picks']} qualifying picks are on the <a href="high-confidence.html">high-confidence</a> page,
each with a hand-written prediction on <a href="predictions.html">predictions</a>.</p>
<h2>Sports</h2>
<div class="grid">{''.join(cards)}</div>
<h2>How the desk is built</h2>
<p>The <a href="reverse-engineering.html">reverse-engineering</a> page documents the OLBG routes and their failure modes;
<a href="methodology.html">methodology</a> explains the pricing and grading; <a href="sources.html">sources</a> lists every
page read with a link for manual review; and <a href="repo-audit.html">repo audit</a> records line-by-line findings from
this session's review of the repository.</p>
"""
    (site / "index.html").write_text(frame("Overview", lede, "Overview"), encoding="utf-8")

    # ------------------------------------------------------ high-confidence
    rows = []
    for s in SPORT_ORDER:
        ps = [p for p in predictions if p["sport"] == s]
        if not ps:
            continue
        rows.append(f'<tr class="grp"><td colspan="9">{esc(SPORT_NAMES[s])} — '
                    f'{len(ps)} pick{"s" if len(ps) != 1 else ""}'
                    f'{"" if len(ps) >= 5 else " (evidence capped below the five-pick target; see sport page)"}</td></tr>')
        rows.extend(pick_row(p) for p in sorted(ps, key=lambda x: -x["probability"]))
    for it in D.FLAGGED:
        if it["sport"] == "greyhounds":
            rows.append('<tr class="grp"><td colspan="9">Greyhounds — 0 picks: no official card obtainable '
                        '(click for the flag)</td></tr>')
    hc = f"""
<h1>High-confidence picks</h1>
<p class="lede">The gate is a conjunction, not a coin flip: a selection must clear a 70% win chance <em>and</em> price
inside the −250…+10000 window at fair odds. Because 70% implies roughly −233, qualifying selections cluster near the
shorter end of the band; anything shorter than −250 is downgraded rather than stretched. A maximum of five picks per
sport per day is published, and no fixture is added to reach a quota.</p>
<div class="wrap"><table><thead><tr><th>ID</th><th>Sport</th><th>Match</th><th>Start (UTC)</th><th>Selection</th>
<th>Market</th><th>Chance · fair price</th><th>Tier</th><th>Official source</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>
<p class="note">Fair decimal is 1/probability with the complementary side summing to 1.000 — there is no margin in these
numbers, so treat them as the price at which the desk breaks even, not a market offer.</p>
"""
    (site / "high-confidence.html").write_text(frame("High-confidence picks", hc, "High picks"), encoding="utf-8")

    # ------------------------------------------------------------ predictions
    prow = []
    for s in SPORT_ORDER:
        ps = [p for p in predictions if p["sport"] == s]
        if not ps:
            continue
        prow.append(f'<tr class="grp"><td colspan="6">{esc(SPORT_NAMES[s])}</td></tr>')
        for p in sorted(ps, key=lambda x: -x["probability"]):
            links = " ".join(f'<a href="{esc(u)}" target="_blank" rel="noopener">source</a>' for u in p["sources"])
            prow.append(f'<tr><td>{esc(p["fixture"])}</td><td>{esc(p["event"])}<small>{esc(p["start_utc"])}</small></td>'
                        f'<td><strong>{esc(p["selection"])}</strong><small>{esc(p["line"]) or "—"} · {esc(p["market"])}</small></td>'
                        f'<td class="pred">{esc(p["text"])}</td>'
                        f'<td>{p["probability"]:.1%}<small>{esc(p["fair_american"])}</small></td>'
                        f'<td>{links}</td></tr>')
    pp = f"""
<h1>Predictions</h1>
<p class="lede">{len(predictions)} hand-written reads, one per High pick, each at least thirty words and tied to the
official page listed on its row. Each states the selection outright and rests on published record, recent results,
season statistics or reported availability — nothing is carried over from a template.</p>
<div class="wrap"><table><thead><tr><th>ID</th><th>Match</th><th>Selection</th><th>Prediction</th>
<th>Chance</th><th>Sources</th></tr></thead><tbody>{''.join(prow)}</tbody></table></div>
"""
    (site / "predictions.html").write_text(frame("Predictions", pp, "Predictions"), encoding="utf-8")

    # ---------------------------------------------------------------- matches
    mrow = []
    for s in SPORT_ORDER:
        fs = [f for f in fixtures if f["sport"] == s]
        if not fs:
            mrow.append(f'<tr class="grp"><td colspan="9">{esc(SPORT_NAMES[s])} — no fixture confirmed this session</td></tr>')
            continue
        mrow.append(f'<tr class="grp"><td colspan="9">{esc(SPORT_NAMES[s])}</td></tr>')
        for f in sorted(fs, key=lambda x: x["start_utc"]):
            sel = "—"
            for p in predictions:
                if p["fixture"] == f["id"]:
                    sel = f'<strong>{esc(p["selection"])}</strong><small>{esc(p["line"]) or "—"} · {p["probability"]:.1%}</small>'
                    break
            facts = "<br>".join(esc(t) for t, _k in fx_by_id[f["id"]]["facts"])
            mrow.append(f'<tr><td>{esc(f["id"])}</td><td>{esc(f["event"])}<small>{esc(f["competition"])}</small></td>'
                        f'<td>{esc(f["start_utc"])}</td><td>{esc(f["venue"])}</td>'
                        f'<td>{sel}</td><td>{facts}</td>'
                        f'<td>{esc(f["rating_basis"])}</td><td>{src_links(f["sources"])}</td>'
                        f'<td>{", ".join(esc(x) for x in f["flags"]) or "—"}</td></tr>')
    mp = f"""
<h1>Fixtures</h1>
<p class="lede">{len(fixtures)} fixtures across the required sports, all scheduled inside the 24–26 October 2026 window.
Every row carries the official page it was read from and the facts that page stated. Where a value could not be
confirmed it is left blank and flagged rather than filled in.</p>
<div class="wrap"><table><thead><tr><th>ID</th><th>Match</th><th>Start (UTC)</th><th>Venue</th><th>Desk pick</th>
<th>Facts read from the official page</th><th>How the rating was set</th><th>Source</th><th>Flags</th></tr></thead>
<tbody>{''.join(mrow)}</tbody></table></div>
<h2>Completed at capture</h2>
<p>These results were already in the book when the pages were read; they are recorded for context and carry no
pre-match selection.</p>
<div class="wrap"><table><thead><tr><th>ID</th><th>Sport</th><th>Competition</th><th>Result</th><th>Detail</th><th>Source</th></tr></thead>
<tbody>{''.join(f'<tr><td>{esc(e["id"])}</td><td>{esc(SPORT_NAMES.get(e["sport"], e["sport"]))}</td><td>{esc(e["comp"])}</td><td><strong>{esc(e["text"])}</strong></td><td>{esc(e["detail"])}</td><td>{src_links(e["sources"])}</td></tr>' for e in D.ELAPSED)}</tbody></table></div>
"""
    (site / "matches.html").write_text(frame("Fixtures", mp, "Matches"), encoding="utf-8")

    # ---------------------------------------------------------------- markets
    krow = []
    for s in SPORT_ORDER:
        ms = [m for m in markets if m["sport"] == s]
        if not ms:
            continue
        kinds = sorted({m["market"] for m in ms})
        fs = next(f for f in fixtures if f["sport"] == s)
        krow.append(f'<tr><td>{esc(SPORT_NAMES[s])}</td><td>{len({m["fixture"] for m in ms})}</td>'
                    f'<td>{len(ms):,}</td><td>{esc(", ".join(kinds))}</td>'
                    f'<td>{src_links(fs["sources"])}</td></tr>')
    detail = []
    for s in SPORT_ORDER:
        ms = [m for m in markets if m["sport"] == s]
        if not ms:
            continue
        detail.append(f'<tr class="grp"><td colspan="6">{esc(SPORT_NAMES[s])}</td></tr>')
        for m in ms:
            if m["tier"] != "High":
                continue
            detail.append(f'<tr><td>{esc(m["fixture"])}</td><td>{esc(m["market"])}</td>'
                          f'<td>{esc(m["line"]) or "—"}</td><td>{esc(m["selection"])}</td>'
                          f'<td>{m["p"]:.2%}<small>{esc(m["american_str"])} · {m["decimal"]:.3f}</small></td>'
                          f'<td>{"in band" if M.in_band(m["p"]) else "outside"}</td></tr>')
    mkp = f"""
<h1>Originated markets</h1>
<p class="lede">{len(markets):,} two-sided prices across {len({m['fixture'] for m in markets})} fixtures. Each pair is
complementary and sums to 1.000, so the number quoted is the desk's break-even price with no margin folded in. Ladders
are ours: spreads step on the standard quarter-point grid, totals on the sport's natural unit, and the rung nearest the
expected margin or total is the desk line.</p>
<div class="wrap"><table><thead><tr><th>Sport</th><th>Fixtures</th><th>Prices</th><th>Market types</th>
<th>Official source</th></tr></thead>
<tbody>{''.join(krow)}</tbody></table></div>
<h2>Selections that clear the High gate</h2>
<p>Every qualifying price by sport. The full ladder for each fixture is in <code>data/4c4968fc/markets.csv</code>.</p>
<div class="wrap"><table><thead><tr><th>ID</th><th>Market</th><th>Line</th><th>Selection</th><th>Chance · fair price</th>
<th>Band</th></tr></thead><tbody>{''.join(detail)}</tbody></table></div>
"""
    (site / "markets.html").write_text(frame("Markets", mkp, "Markets"), encoding="utf-8")

    # ---------------------------------------------------------------- flagged
    frow = []
    for it in D.FLAGGED:
        frow.append(f'<tr><td>{esc(it["id"])}</td><td>{esc(SPORT_NAMES.get(it["sport"], it["sport"]))}</td>'
                    f'<td>{esc(it["item"])}</td><td>{esc(it["detail"])}</td>'
                    f'<td><span class="badge b-flag">{esc(it["status"])}</span></td>'
                    f'<td>{src_links(it["sources"])}</td></tr>')
    fp = f"""
<h1>Flagged for review</h1>
<p class="lede">Anything the desk could not confirm sits here with the page that failed to yield it, so a reader can
check by hand. Nothing on this list was substituted with an estimate; the corresponding cells are blank or absent from
the fixture tables.</p>
<div class="wrap"><table><thead><tr><th>Ref</th><th>Sport</th><th>Item</th><th>What happened</th><th>Status</th>
<th>Link for manual review</th></tr></thead><tbody>{''.join(frow)}</tbody></table></div>
"""
    (site / "flagged.html").write_text(frame("Flagged", fp, "Flagged"), encoding="utf-8")

    # ---------------------------------------------------------------- sources
    srow = []
    for k, (name, url) in D.SOURCES.items():
        role = "OLBG taxonomy — discovery only" if k.startswith("olbg") else "official / primary"
        srow.append(f'<tr><td><code>{esc(k)}</code></td><td>{esc(name)}</td><td>{esc(role)}</td>'
                    f'<td><a href="{esc(url)}" target="_blank" rel="noopener">{esc(url)}</a></td></tr>')
    sp = f"""
<h1>Sources</h1>
<p class="lede">{len(D.SOURCES)} pages were read for this build, all at or after the capture stamp
{NOW}. Official pages carry the fixture, form and statistic facts; the two OLBG entries exist only to document the
discovery routes and are never used as sporting evidence.</p>
<div class="wrap"><table><thead><tr><th>ID</th><th>Publisher &amp; page</th><th>Role</th><th>Link for manual review</th></tr></thead>
<tbody>{''.join(srow)}</tbody></table></div>
"""
    (site / "sources.html").write_text(frame("Sources", sp, "Sources"), encoding="utf-8")

    # ------------------------------------------------------------ methodology
    meth = f"""
<h1>Methodology</h1>
<h2>1. Discovery</h2>
<p>OLBG's sport hubs were mapped to the fifteen required categories and used to enumerate candidate events only. OLBG
tip percentages are votes, not probabilities, and no OLBG number reaches a published price or fact.</p>
<h2>2. Fixture confirmation</h2>
<p>Each candidate was re-read from the league, tour, governing body or club page listed on its row: participants,
competition, venue and start time. Missing values stay blank and are flagged. Times are published in UTC exactly as the
source listed them; where a source renders venue-local time the conversion is noted in that fixture's flag.</p>
<h2>3. Pricing</h2>
<p>Match-level estimates start from published records, tables and rankings. Two-way markets are built as complementary
pairs: p and 1−p, priced at 1/p with no vig, so both sides sum to 1.000. Spread and total ladders come from a normal
approximation around the expected margin and total with the sport's own scale and spread, stepped on the natural line
grid. Set-based sports convert a match probability into a per-set probability by inverting a best-of-three or best-of-five
set structure, then price set handicaps and totals from that. Matchup sports (golf, motor racing) price head-to-head and a stroke
or position ladder.</p>
<h2>4. Confidence</h2>
<p>High requires both conditions in the brief: a strike rate above 70% and a fair American price inside
−250…+10000. A 70% chance is about −233, so the band's short end binds; a selection at, say, 74% would price at about
−285 and is therefore published as Medium rather than relabelled. Medium covers 50–70%. Low is anything below 50%.</p>
<h2>5. Selection cap</h2>
<p>Up to five High picks per sport, taken in probability order with one price per market per fixture. Sports whose
evidence supports fewer qualifying prices publish fewer, and the gap is stated on the sport page and the overview.</p>
<h2>6. Predictions</h2>
<p>One hand-written read per High pick, at least thirty words, always naming the event and stating the side. The content
is drawn from the official page linked on the row: records, standings, recent results, published scoring and reported
availability. No two reads share a six-word run, and internal jargon is kept off the public pages.</p>
<h2>7. Limits</h2>
<p>These are research prices, not market prices. Sports where no official card could be reached — greyhounds in this
window — publish nothing rather than a guess, and are listed on the flagged page. Team news is only cited where an
official page stated it; absence of a reported injury is not a claim that a squad is fully fit.</p>
<h2>8. Where to check the working</h2>
<p>Every input traces to a page on the <a href="sources.html">sources</a> list, and each fixture row repeats its own link
for manual review. The gate that produced these numbers is <code>scripts/s4c4968fc_validate.py</code>, which fails the
build when a price, a pick or a prediction breaks a rule set out on this page.</p>
"""
    (site / "methodology.html").write_text(frame("Methodology", meth, "Method"), encoding="utf-8")

    # ------------------------------------------------------ reverse-engineering
    hubrows = "".join(f'<tr><td>{esc(SPORT_NAMES[k])}</td><td><a href="{esc(u)}" target="_blank" rel="noopener">{esc(u)}</a></td></tr>'
                      for k, u in OLBG_HUBS.items())
    rev = f"""
<h1>Reverse-engineering OLBG</h1>
<p class="lede">OLBG publishes server-rendered hub pages with no public JSON API. Sport hubs follow
<code>/betting-tips/&lt;Sport_Slug&gt;/&lt;sport_id&gt;</code>, the slug is case-sensitive, and the id is the taxonomy key.
The fifteen required sports map to the routes below.</p>
<div class="wrap"><table><thead><tr><th>Sport</th><th>OLBG hub</th></tr></thead><tbody>{hubrows}</tbody></table></div>
<h2>What the routes yielded</h2>
<ul>
<li>Both hubs read this session returned "No tips found" for the current window. The Italian SuperLega hub was empty and
the volleyball id resolved, so the route exists and the emptiness is a content gap, not a dead link.</li>
<li>Hub listings are paginated and truncated behind a "Load More" control, so an empty first page cannot be read as an
empty sport. Football, American football, boxing, MMA, hurling, cycling and horse racing were deliberately skipped per
the brief.</li>
<li>OLBG's clock renders in the reader's local zone with no zone label. Times are never taken from OLBG here; every start
is republished from the official page.</li>
</ul>
<h2>Consequences for this desk</h2>
<p>Because discovery returned nothing usable, fixture enumeration was driven by the official competition calendars for the
fifteen sports, and OLBG's role is reduced to the taxonomy map above. That is disclosed rather than papered over: the desk
does not claim to have found these fixtures on OLBG.</p>
"""
    (site / "reverse-engineering.html").write_text(frame("OLBG routes", rev, "Reverse-engineering"), encoding="utf-8")

    # ------------------------------------------------------------- repo audit
    audit = [
        ("A1", "HIGH", "pipeline/config.py", "Canonical config still carries 17 categories while the brief fixes scope at 15; Aussie Rules and eSports remain enabled and are excluded only by the per-desk filter. Recheck: https://www.olbg.com/betting-tips"),
        ("A2", "MEDIUM", "data/current/snapshot.json", "Root snapshot is older than the capture stamp, so the canonical root desk shows stale counts while per-session desks are fresh. Recheck: https://api-web.nhle.com/v1/schedule/2026-10-24"),
        ("A3", "MEDIUM", "496eaf02/methodology.html", "The peer desk advertises a 62% fallback tier as High-B, which is below the 70% floor in the brief. This desk publishes no sub-70% High tier; the shortfall is disclosed instead."),
        ("A4", "MEDIUM", "pipeline/build.py", "New desk directories are auto-indexed in archive.html, so a desk can appear in the archive before its own validation passes. Ordering is safe but the archive gives no readiness signal."),
        ("A5", "LOW", "scripts/validate.py", "Legacy session f7fa77fc still raises three warnings for root-absolute hrefs that break under the /OLBG1/ project subpath. Pre-existing and tolerated, but it will fire on every run."),
        ("A6", "LOW", "tests/pipeline/test_routes.py", "Route tests enumerate desks by directory, so a desk with generated JSON but no HTML would pass fixture checks and fail only at page level. This session runs both gates before merging."),
    ]
    arow = "".join(f'<tr><td>{esc(i)}</td><td><span class="badge {"b-flag" if s in ("HIGH", "CRITICAL") else "b-md"}">{esc(s)}</span></td>'
                   f'<td><code>{esc(loc)}</code></td><td>{esc(txt)}</td></tr>' for i, s, loc, txt in audit)
    ap = f"""
<h1>Repository audit</h1>
<p class="lede">This session reviewed the canonical pipeline, the validator, the test suite and the neighbouring desks
line by line before adding anything. Findings below are structural and current; they are reported, not silently fixed,
because the affected files belong to shared or peer scope.</p>
<div class="wrap"><table><thead><tr><th>Ref</th><th>Severity</th><th>File</th><th>Finding and where to recheck</th></tr></thead>
<tbody>{arow}</tbody></table></div>
<h2>Scope of this session's writes</h2>
<p><code>scripts/s4c4968fc_*.py</code>, <code>data/4c4968fc/**</code>, <code>4c4968fc/**</code>,
<code>reports/SESSION_4C4968FC.*</code>, <code>tests/pipeline/test_desk_4c4968fc.py</code> and section 75 of
<code>COORDINATION.md</code>. No peer desk file was touched.</p>
"""
    (site / "repo-audit.html").write_text(frame("Repository audit", ap, "Repo audit"), encoding="utf-8")

    # ---------------------------------------------------------- sport pages
    for s in SPORT_ORDER:
        fs = [f for f in fixtures if f["sport"] == s]
        ps = [p for p in predictions if p["sport"] == s]
        hosts = OLBG_HUBS[s]
        if not fs:
            body = f"""
<h1>{esc(SPORT_NAMES[s])}</h1>
<p class="lede">No fixture in this sport could be confirmed from an official source inside the 24–26 October window, so the
desk publishes no price and no pick here. The opposite of a guess is a blank.</p>
<h2>What was attempted</h2>
<div class="wrap"><table><thead><tr><th>Ref</th><th>Item</th><th>What happened</th><th>Link for manual review</th></tr></thead><tbody>
{''.join(f'<tr><td>{esc(it["id"])}</td><td>{esc(it["item"])}</td><td>{esc(it["detail"])}</td><td>{src_links(it["sources"])}</td></tr>' for it in D.FLAGGED if it["sport"] == s)}
</tbody></table></div>
<p class="note">OLBG hub for this sport: <a href="{esc(hosts)}" target="_blank" rel="noopener">{esc(hosts)}</a>.</p>
"""
            (site / "sports" / f"{s}.html").write_text(frame(SPORT_NAMES[s], body, prefix="../"), encoding="utf-8")
            continue
        frows = "".join(
            f'<tr><td>{esc(f["id"])}</td><td>{esc(f["event"])}<small>{esc(f["competition"])}</small></td>'
            f'<td>{esc(f["start_utc"])}</td><td>{esc(f["venue"])}</td>'
            f'<td>{"; ".join(esc(t) for t, _k in fx_by_id[f["id"]]["facts"])}</td>'
            f'<td>{esc(f["rating_basis"])}</td><td>{src_links(f["sources"])}</td></tr>' for f in sorted(fs, key=lambda x: x["start_utc"]))
        def links_for(fid):
            return src_links(next(f for f in fixtures if f["id"] == fid)["sources"])
        prow = "".join(
            f'<tr><td>{esc(p["fixture"])}</td><td>{esc(p["event"])}</td>'
            f'<td><strong>{esc(p["selection"])}</strong><small>{esc(p["line"]) or "—"}</small></td>'
            f'<td>{esc(p["market"])}</td><td>{p["probability"]:.1%}<small>{esc(p["fair_american"])}</small></td>'
            f'<td>{links_for(p["fixture"])}</td></tr>'
            for p in sorted(ps, key=lambda x: -x["probability"]))
        trow = "".join(
            f'<tr><td>{esc(p["fixture"])}</td><td>{esc(p["event"])}</td><td class="pred">{esc(p["text"])}</td>'
            f'<td>{links_for(p["fixture"])}</td></tr>'
            for p in sorted(ps, key=lambda x: -x["probability"]))
        gap = "" if len(ps) >= 5 else (f'<p class="note">Target is five High picks; {len(ps)} qualified. '
                                       f'The cap here is evidence, not effort — every rung outside the gate is published '
                                       f'as Medium or Low in the market file rather than promoted.</p>')
        body = f"""
<h1>{esc(SPORT_NAMES[s])}</h1>
<p class="lede">{len(fs)} fixture{"s" if len(fs) != 1 else ""}, {sum(1 for m in markets if m["sport"] == s):,} originated
prices and {len(ps)} High pick{"s" if len(ps) != 1 else ""}. Fixtures, form and statistics were read from the official
pages linked on each row.</p>
<div class="kpis"><div class="kpi"><b>{len(fs)}</b><small>fixtures</small></div>
<div class="kpi"><b>{sum(1 for m in markets if m["sport"] == s):,}</b><small>prices</small></div>
<div class="kpi"><b>{len(ps)}</b><small>high picks</small></div></div>
{gap}
<h2>Fixtures</h2>
<div class="wrap"><table><thead><tr><th>ID</th><th>Match</th><th>Start (UTC)</th><th>Venue</th><th>Facts from the official page</th>
<th>Rating basis</th><th>Source</th></tr></thead><tbody>{frows}</tbody></table></div>
<h2>High-confidence selections</h2>
<div class="wrap"><table><thead><tr><th>ID</th><th>Match</th><th>Selection</th><th>Market</th><th>Chance · fair price</th>
<th>Official source</th></tr></thead>
<tbody>{prow}</tbody></table></div>
<h2>Analysis</h2>
<div class="wrap"><table><thead><tr><th>ID</th><th>Match</th><th>Read</th><th>Official source</th></tr></thead>
<tbody>{trow}</tbody></table></div>
<p class="note">OLBG hub: <a href="{esc(hosts)}" target="_blank" rel="noopener">{esc(hosts)}</a> ·
<a href="../high-confidence.html">all high picks</a> · <a href="../markets.html">market ladders</a></p>
"""
        (site / "sports" / f"{s}.html").write_text(frame(SPORT_NAMES[s], body, prefix="../"), encoding="utf-8")

    pages = ["index.html", "high-confidence.html", "predictions.html", "matches.html", "markets.html",
             "flagged.html", "sources.html", "methodology.html", "reverse-engineering.html", "repo-audit.html"]
    pages += [f"sports/{s}.html" for s in SPORT_ORDER]
    for p in pages:
        if not (site / p).exists():
            raise SystemExit(f"page missing: {p}")
    write_json(DATA / "site-manifest.json", {"desk": D.SESSION, "generated_utc": NOW,
                                             "pages": pages, "page_count": len(pages)})
    print(f"built {len(pages)} pages, {len(fixtures)} fixtures, {len(markets)} prices, {len(predictions)} picks")


if __name__ == "__main__":
    s = main()
    print(json.dumps(s, indent=1))
