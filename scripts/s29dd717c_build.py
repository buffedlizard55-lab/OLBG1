#!/usr/bin/env python3
"""Build the namespaced 29dd717c OLBG research dashboard and data mirrors."""
from __future__ import annotations

import html
import json
import math
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from statistics import NormalDist

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import s29dd717c_data as D  # noqa: E402

OUT = ROOT / "29dd717c"
DATA = ROOT / "data" / "29dd717c"
REPO = "https://github.com/buffedlizard55-lab/OLBG1"
NORM = NormalDist()
SPORT_NAME = {slug: name for slug, name, _url in D.SPORTS}
SOURCE = {s["id"]: s for s in D.SOURCES}


def esc(value):
    return html.escape(str(value if value is not None else ""), quote=True)


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def american(p):
    if p >= 0.5:
        return int(round(-100 * p / (1 - p)))
    return int(round(100 * (1 - p) / p))


def outcome(label, p):
    p = round(float(p), 6)
    return {"label": label, "probability": p, "decimal": round(1 / p, 3),
            "american": american(p)}


def poisson_under(mean, line):
    return sum(math.exp(-mean) * mean ** k / math.factorial(k)
               for k in range(math.floor(line) + 1))


def market(name, unit, outcomes, note):
    return {"market": name, "unit": unit, "outcomes": outcomes,
            "pricing_note": note, "overround": round(sum(o["probability"] for o in outcomes), 6)}


def build_markets(f):
    p = f["pricing"]
    a, b = f["a"], f["b"]
    result = []
    w = p["winner"]
    w_note = f["pricing_note"]
    if "draw" in w:
        outcomes = [outcome(a, w["a"]), outcome("Draw", w["draw"]), outcome(b, w["b"])]
    else:
        outcomes = [outcome(a, w["a"]), outcome(b, w["b"])]
    result.append(market("Match winner", "winner", outcomes, w_note))

    if "spread" in p:
        sp = p["spread"]
        pa, pb = w["a"], w["b"]
        decisive_b = pb / (pa + pb)
        sd = sp["sd"]
        mu_b = NORM.inv_cdf(decisive_b) * sd
        line_a = sp["line_a"]
        line_b = -line_a
        p_b_cover = NORM.cdf((mu_b + line_b) / sd)
        outcomes = [outcome(f"{a} {line_a:+g}", 1 - p_b_cover),
                    outcome(f"{b} {line_b:+g}", p_b_cover)]
        result.append(market("Handicap / spread", "points/games/sets as labelled", outcomes,
                             f"Normal winning-margin assumption, SD {sd:g}; line from side A {line_a:+g}. Push-free half-point lines only."))

    if "total" in p:
        t = p["total"]
        if "over" in t:
            over, under = t["over"], t["under"]
            distribution = "Explicit best-of-five set distribution stated in the pricing note."
        elif t["kind"] == "poisson":
            under = poisson_under(t["mean"], t["line"])
            over = 1 - under
            distribution = f"Poisson count, mean {t['mean']:g}; no-vig complementary prices."
        else:
            under = NORM.cdf((t["line"] - t["mean"]) / t["sd"])
            over = 1 - under
            distribution = f"Normal total, mean {t['mean']:g}, SD {t['sd']:g}; no-vig complementary prices."
        outcomes = [outcome(f"Over {t['line']:g}", over), outcome(f"Under {t['line']:g}", under)]
        result.append(market("Total", "match total", outcomes, distribution))
    return result


def pick_from(f, markets):
    sel = f["selection"]
    target = {"winner": "Match winner", "spread": "Handicap / spread", "total": "Total"}[sel["market"]]
    m = next(x for x in markets if x["market"] == target)
    if sel["market"] == "winner":
        index = {"a": 0, "b": len(m["outcomes"]) - 1, "draw": 1}[sel["key"]]
    elif sel["market"] == "spread":
        index = {"a_cover": 0, "b_cover": 1}[sel["key"]]
    else:
        index = {"over": 0, "under": 1}[sel["key"]]
    o = m["outcomes"][index]
    p = o["probability"]
    words = len(re.findall(r"\b[\w’'-]+\b", f["analysis"]))
    if p >= 0.70 and -250 <= o["american"] <= 10000 and words >= 30:
        tier = "High"
        note = "Meets probability, price-window and written-analysis gates."
    elif p >= 0.56:
        tier = "Medium"
        note = "Medium confidence; probability or price-window gate limits a higher grade."
    else:
        tier = "Low"
        note = "Low confidence: the independent price is close to even or an underdog position."
    if p >= 0.70 and o["american"] < -250:
        tier = "Medium"
        note = "Fair price is shorter than -250, outside the requested High window."
    cap = f.get("max_confidence")
    order = {"Low": 0, "Medium": 1, "High": 2}
    if cap and order[tier] > order[cap]:
        tier = cap
        note = f"Capped at {cap} because of the published evidence limitation."
    winner_market = markets[0]
    winner = max(winner_market["outcomes"], key=lambda x: x["probability"])
    wp = winner["probability"]
    if wp >= 0.70 and -250 <= winner["american"] <= 10000:
        winner_tier = "High"
    elif wp >= 0.56:
        winner_tier = "Medium"
    else:
        winner_tier = "Low"
    if cap and order[winner_tier] > order[cap]:
        winner_tier = cap
    return {"fixture_id": f["id"], "sport": f["sport"], "competition": f["competition"],
            "match": f"{f['a']} v {f['b']}", "start_utc": f["start_utc"],
            "selection": sel["label"], "market": target, "probability": p,
            "american": o["american"], "decimal": o["decimal"], "confidence": tier,
            "confidence_note": note, "match_winner_lean": winner["label"],
            "match_winner_probability": winner["probability"],
            "match_winner_american": winner["american"],
            "match_winner_confidence": winner_tier, "analysis": f["analysis"],
            "analysis_words": words, "source_ids": f["source_ids"],
            "olbg_event_id": f["olbg_event_id"], "olbg_url": f["olbg_url"]}


def review_for(f):
    reasons = list(f["flags"])
    if not f["start_utc"] and not any("start" in r.lower() for r in reasons):
        reasons.append("Official start time not captured; field left blank.")
    if not f["venue"]:
        reasons.append("Official venue not captured; field left blank.")
    for m in f["markets_withheld"]:
        reasons.append(f"{m['market']}: {m['reason']}")
    if not reasons:
        return None
    return {"id": "F29-ROW-" + f["id"].upper().replace("_", "-"), "sport": f["sport"],
            "severity": "row-limitation", "title": f"{f['a']} v {f['b']}",
            "detail": " ".join(reasons), "source_ids": f["source_ids"],
            "olbg_url": f["olbg_url"], "event_ids": str(f["olbg_event_id"]),
            "fixture_id": f["id"]}


def prepare():
    fixtures, picks, lines = [], [], []
    for raw in D.FIXTURES:
        f = dict(raw)
        markets = build_markets(f)
        pick = pick_from(f, markets)
        f["markets"] = markets
        f["pick"] = pick
        f["review_reasons"] = (review_for(f) or {}).get("detail", "")
        fixtures.append(f)
        picks.append(pick)
        for m in markets:
            for o in m["outcomes"]:
                lines.append({"fixture_id": f["id"], "sport": f["sport"], "match": pick["match"],
                              "market": m["market"], "selection": o["label"],
                              "probability": o["probability"], "decimal": o["decimal"],
                              "american": o["american"], "source_ids": f["source_ids"],
                              "pricing_note": m["pricing_note"]})
    row_flags = [x for x in (review_for(f) for f in D.FIXTURES) if x]
    flags = D.FLAGS + row_flags
    coverage = []
    for slug, name, url in D.SPORTS:
        fs = [f for f in fixtures if f["sport"] == slug]
        ps = [f["pick"] for f in fs]
        source_ids = []
        for f in fs:
            source_ids.extend(f["source_ids"])
        for flag in D.FLAGS:
            if flag["sport"] == slug:
                source_ids.extend(flag["source_ids"])
        coverage.append({"sport": slug, "name": name, "olbg_url": url,
                         "official_source_ids": list(dict.fromkeys(source_ids)),
                         "fixtures": len(fs), "picks": len(ps),
                         "high": sum(p["confidence"] == "High" for p in ps),
                         "written_predictions": len(ps),
                         "withheld_markets": sum(len(f["markets_withheld"]) for f in fs),
                         "status": "Selections published" if ps else "No supported selection",
                         "note": D.COVERAGE_NOTES[slug]})
    return fixtures, picks, lines, flags, coverage


FIXTURES, PICKS, LINES, FLAGS, COVERAGE = prepare()
PICK_BY_ID = {p["fixture_id"]: p for p in PICKS}


CSS = r"""
:root{--bg:#f4f6f8;--paper:#fff;--ink:#172033;--muted:#5b6475;--line:#dfe4eb;--green:#126548;--soft:#e8f3ed;--amber:#875500;--amber-soft:#fff4dc;--red:#a02a2a;--red-soft:#fcecec;--navy:#254a73;--blue-soft:#eaf1f8}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.58 system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}a{color:var(--green);text-decoration:none}a:hover{text-decoration:underline}.wrap{max-width:1240px;margin:auto;padding:0 22px}.top{background:var(--paper);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:10}.toprow{min-height:66px;display:flex;align-items:center;gap:18px;flex-wrap:wrap;padding:10px 0}.brand{font-weight:800;color:var(--ink);letter-spacing:-.02em}.brand span{display:inline-grid;place-items:center;background:var(--green);color:#fff;width:32px;height:32px;border-radius:8px;margin-right:8px}.brand small{display:block;margin-left:44px;margin-top:-8px;color:var(--muted);font-size:10px;letter-spacing:.1em;text-transform:uppercase}.nav{margin-left:auto;display:flex;gap:3px;flex-wrap:wrap}.nav a{font-size:13px;font-weight:650;color:var(--muted);padding:6px 9px;border-radius:7px}.nav a.active,.nav a:hover{background:var(--soft);color:var(--green);text-decoration:none}main{padding:30px 0 64px}.eyebrow{font-size:12px;letter-spacing:.13em;text-transform:uppercase;color:var(--green);font-weight:750;margin:0 0 7px}h1{font-size:clamp(30px,4vw,45px);line-height:1.12;letter-spacing:-.035em;margin:0 0 12px}h2{font-size:24px;line-height:1.25;letter-spacing:-.02em;margin:0 0 10px}h3{font-size:18px;line-height:1.35;margin:0 0 8px}.lede{font-size:18px;color:var(--muted);max-width:82ch;margin:0 0 10px}.stamp,.small,.sub{font-size:13px;color:var(--muted)}.sub{display:block}.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:12px;margin:24px 0}.kpi,.panel,.tile,.prediction{background:var(--paper);border:1px solid var(--line);border-radius:12px}.kpi{padding:14px 16px}.kpi b{display:block;font-size:28px;line-height:1.15}.kpi span{font-size:11px;text-transform:uppercase;letter-spacing:.07em;color:var(--muted)}section{margin:34px 0}.panel{padding:20px;margin:16px 0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px}.tile{padding:17px}.tile h3{margin-bottom:5px}.tile .count{font-size:28px;font-weight:780;float:right}.actions{display:flex;gap:9px;flex-wrap:wrap;margin:18px 0}.button{display:inline-block;padding:9px 13px;background:var(--green);color:#fff;border-radius:8px;font-weight:700;font-size:14px}.button.secondary{background:var(--paper);color:var(--green);border:1px solid #bcd5c8}.button:hover{text-decoration:none}.note{padding:14px 17px;border:1px solid #e6d29c;background:var(--amber-soft);border-radius:10px;margin:15px 0}.note.ok{background:var(--soft);border-color:#b9d9c8}.note.bad{background:var(--red-soft);border-color:#edbaba}.table-wrap{overflow-x:auto;background:var(--paper);border:1px solid var(--line);border-radius:12px;margin:14px 0}table{width:100%;border-collapse:collapse;font-size:14px}th,td{text-align:left;vertical-align:top;padding:11px 13px;border-bottom:1px solid var(--line)}th{background:#f8f9fb;color:#4d5768;font-size:11px;text-transform:uppercase;letter-spacing:.055em;white-space:nowrap}tr:last-child td{border-bottom:0}.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}.pick{font-weight:760}.badge{display:inline-block;border-radius:999px;padding:2px 9px;font-size:11px;font-weight:760;white-space:nowrap;border:1px solid transparent}.badge.High{background:var(--soft);color:var(--green);border-color:#a9d1bd}.badge.Medium{background:var(--amber-soft);color:var(--amber);border-color:#ead099}.badge.Low{background:#eef0f3;color:#4d5768;border-color:#d9dee5}.badge.red{background:var(--red-soft);color:var(--red)}.badge.blue{background:var(--blue-soft);color:var(--navy)}.sources{display:flex;flex-direction:column;gap:3px;min-width:170px}.sources a{font-size:12px;font-weight:620}.prediction{padding:20px;margin:15px 0;scroll-margin-top:100px}.prediction header{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;border-bottom:1px solid var(--line);padding-bottom:12px;margin-bottom:12px}.prediction .prose{font-size:16px;max-width:92ch}.facts{padding-left:20px;font-size:14px}.facts li{margin:4px 0}.market-title{background:#f8f9fb}.missing{color:var(--red);font-weight:650}.footer{border-top:1px solid var(--line);padding:20px 0;color:var(--muted);font-size:13px}.anchor{scroll-margin-top:100px}.checklist li{margin:7px 0}.code{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:12px;word-break:break-all}.two{display:grid;grid-template-columns:1fr 1fr;gap:16px}@media(max-width:760px){.two{grid-template-columns:1fr}.nav{margin-left:0}.wrap{padding:0 14px}th,td{padding:9px 10px}.kpi b{font-size:24px}}
"""

NAV = [("index.html", "Summary", "summary"), ("picks.html", "Selections", "picks"),
       ("predictions.html", "Predictions", "predictions"), ("matches.html", "Matches", "matches"),
       ("sports.html", "15 sports", "sports"), ("flagged.html", "Flagged for Review", "flagged"),
       ("sources.html", "Official sources", "sources"), ("methodology.html", "Method", "method"),
       ("reverse-engineering.html", "OLBG coverage", "reverse"),
       ("repository-audit.html", "Repository audit", "repo")]


def links(ids):
    unique = list(dict.fromkeys(ids))
    return '<div class="sources">' + "".join(
        f'<a href="{esc(SOURCE[s]["url"])}" target="_blank" rel="noopener noreferrer">{esc(SOURCE[s]["label"])} ↗</a>'
        for s in unique) + "</div>"


def page(title, active, body, prefix=""):
    nav = "".join(f'<a href="{prefix}{href}" class="{"active" if key == active else ""}">{label}</a>'
                  for href, label, key in NAV)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · OLBG Research Desk</title><meta name="description" content="Independent upcoming-match lines, written selections and official-source review across 15 sports.">
<link rel="stylesheet" href="{prefix}assets/style.css"></head><body>
<header class="top"><div class="wrap toprow"><a class="brand" href="{prefix}index.html"><span>29</span>OLBG Research Desk<small>Independent prices · official evidence</small></a><nav class="nav" aria-label="Dashboard">{nav}</nav></div></header>
<main class="wrap">{body}</main><footer class="footer"><div class="wrap">Snapshot {esc(D.SNAPSHOT)} · <a href="{prefix}flagged.html">Review limitations</a> · <a href="{REPO}/tree/arena/29dd717c-olbg1/29dd717c" target="_blank" rel="noopener noreferrer">Repository folder ↗</a><br>Prices are analytical estimates, not bookmaker offers. OLBG is used for discovery only. Please bet responsibly.</div></footer></body></html>"""


def when(iso):
    if not iso:
        return '<span class="missing">Not published</span>'
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return esc(dt.strftime("%d %b · %H:%M UTC"))


def price(p):
    return f"{p['american']:+d} / {p['decimal']:.3f} / {p['probability']*100:.1f}%"


def badge(t):
    return f'<span class="badge {esc(t)}">{esc(t)}</span>'


def pick_table(picks, analysis_prefix=""):
    rows = []
    for p in sorted(picks, key=lambda x: ({"High": 0, "Medium": 1, "Low": 2}[x["confidence"]], -x["probability"], x["fixture_id"])):
        rows.append(f"<tr><td><strong>{esc(p['match'])}</strong><span class='sub'>{esc(SPORT_NAME[p['sport']])} · {esc(p['competition'])}<br>{when(p['start_utc'])}</span></td>"
                    f"<td class='pick'>{esc(p['selection'])}<span class='sub'>Winner: {esc(p['match_winner_lean'])} · {esc(p['match_winner_confidence'])}</span></td>"
                    f"<td class='num'><strong>{p['american']:+d}</strong><span class='sub'>{p['decimal']:.3f} · {p['probability']*100:.1f}%</span></td>"
                    f"<td>{badge(p['confidence'])}<span class='sub'>{esc(p['confidence_note'])}</span></td>"
                    f"<td><a href='{analysis_prefix}predictions.html#prediction-{esc(p['fixture_id'])}'>Read prediction</a><br><a href='{analysis_prefix}sports/{esc(p['sport'])}.html#{esc(p['fixture_id'])}'>All markets</a></td>"
                    f"<td>{links(p['source_ids'])}</td></tr>")
    return """<div class="table-wrap"><table><thead><tr><th>Match / start</th><th>Selection</th><th>Fair price</th><th>Confidence</th><th>Prediction & markets</th><th>Official review links</th></tr></thead><tbody>""" + "".join(rows) + "</tbody></table></div>"


def prediction_card(f, prefix=""):
    p = f["pick"]
    facts = "".join(f"<li>{esc(x)}</li>" for x in f["facts"])
    review = f"<p class='small'><strong>Review:</strong> {esc(f['review_reasons'])}</p>" if f["review_reasons"] else ""
    return f"""<article class="prediction" id="prediction-{esc(f['id'])}"><header><div><span class="eyebrow">{esc(SPORT_NAME[f['sport']])} · {esc(f['competition'])}</span><h3>{esc(f['a'])} v {esc(f['b'])}</h3><span class="small">{when(f['start_utc'])} · {esc(f['venue'] or 'Venue not published')}</span></div><div>{badge(p['confidence'])} <span class="code">OLBG {esc(f['olbg_event_id'])}</span></div></header>
<p class="prose">{esc(f['analysis'])}</p><div class="two"><div><h3>Official evidence</h3><ul class="facts">{facts}</ul><p class="small"><strong>Availability boundary:</strong> {esc(f['availability'])}</p></div><div><h3>Price & locations</h3><p><strong>{esc(p['selection'])}</strong><br>{p['american']:+d} American · {p['decimal']:.3f} decimal · {p['probability']*100:.1f}% probability</p><p class="small">Match-winner lean: <strong>{esc(p['match_winner_lean'])}</strong> ({p['match_winner_probability']*100:.1f}%, {p['match_winner_american']:+d}) · {badge(p['match_winner_confidence'])}<br>{esc(p['confidence_note'])}</p><p><a href="{prefix}sports/{esc(f['sport'])}.html#{esc(f['id'])}">Every originated market for this match</a> · <a href="{prefix}reverse-engineering.html#{esc(f['sport'])}">OLBG discovery mapping</a></p></div></div>{review}{links(f['source_ids'])}</article>"""


def fixture_markets(f):
    chunks = []
    for m in f["markets"]:
        rows = "".join(f"<tr><td>{esc(o['label'])}</td><td class='num'>{o['american']:+d}</td><td class='num'>{o['decimal']:.3f}</td><td class='num'>{o['probability']*100:.1f}%</td><td>{links(f['source_ids'])}</td></tr>" for o in m["outcomes"])
        chunks.append(f"<h4>{esc(m['market'])}</h4><p class='small'>{esc(m['pricing_note'])}</p><div class='table-wrap'><table><thead><tr><th>Outcome</th><th>American</th><th>Decimal</th><th>Probability</th><th>Official review links</th></tr></thead><tbody>{rows}</tbody></table></div>")
    for m in f["markets_withheld"]:
        chunks.append(f"<p class='note'><strong>{esc(m['market'])} — blank:</strong> {esc(m['reason'])}</p>")
    return "".join(chunks)


def render_index():
    highs = [p for p in PICKS if p["confidence"] == "High"]
    active = sum(bool(c["picks"]) for c in COVERAGE)
    body = f"""<p class="eyebrow">Saturday 24 October 2026 · late-card edition</p><h1>Upcoming-match research,<br>picks first.</h1><p class="lede">Independent match-winner, handicap and total prices across the exact 15 requested sports. Every retained match has written analysis and direct official review links; unsupported fields stay blank and visible.</p><p class="stamp">Evidence snapshot {esc(D.SNAPSHOT)} · publication cutoff {esc(D.CUTOFF)} · started fixtures rejected</p>
<div class="actions"><a class="button" href="picks.html">See all {len(PICKS)} selections</a><a class="button secondary" href="predictions.html">Read every prediction</a><a class="button secondary" href="flagged.html">Open Flagged for Review</a></div>
<div class="kpis"><div class="kpi"><b>{len(PICKS)}</b><span>Retained selections</span></div><div class="kpi"><b>{len(highs)}</b><span>High selections</span></div><div class="kpi"><b>{active}/15</b><span>Sports with picks</span></div><div class="kpi"><b>{len(LINES)}</b><span>Zero-vig outcomes</span></div><div class="kpi"><b>{len(FLAGS)}</b><span>Review entries</span></div></div>
<section><h2>Executive summary</h2><p class="lede">The late NHL and NBA slates avoid fixtures already due to begin. Italian volleyball, Swedish and French handball, Gaelic finals, two ATP title matches and World Series Game 2 add depth. Six sports have no supported selection and say so plainly. The {len(highs)} High selections meet both the fair-price window and the written-analysis gate.</p></section>
<section><h2>High-confidence selections</h2>{pick_table(highs)}</section>
<section><h2>All sports at a glance</h2><div class="grid">"""
    for c in COVERAGE:
        body += f"<article class='tile'><span class='count'>{c['picks']}</span><h3><a href='sports/{c['sport']}.html'>{esc(c['name'])}</a></h3><span class='badge {'blue' if c['picks'] else 'red'}'>{esc(c['status'])}</span><p class='small'>{c['fixtures']} fixtures · {c['high']} High · {c['written_predictions']} written predictions</p><p class='small'>{esc(c['note'])}</p></article>"
    body += """</div></section><section><div class="panel"><h2>Where everything lives</h2><p><strong>Selections</strong> are on the picks page; <strong>full prose</strong> is on Predictions; <strong>every fixture and market</strong> is under Matches and the sport subpages. <strong>Flagged for Review</strong> combines contradictions, expired events, missing fields and withheld markets. Official sources include timestamps and limitations.</p><div class="actions"><a href="matches.html">Every match</a> · <a href="sources.html">Source register</a> · <a href="methodology.html">Pricing method</a> · <a href="reverse-engineering.html">OLBG mapping</a> · <a href="repository-audit.html">Repository audit</a></div></div></section>"""
    return page("Executive summary", "summary", body)


def render_picks():
    body = f"<p class='eyebrow'>All retained matches</p><h1>Selections</h1><p class='lede'>One strongest position per retained match, sorted by confidence and independent probability. American / decimal / probability are zero-vig fair prices, not OLBG odds.</p><div class='note ok'>High requires at least 70% probability, a fair American price no shorter than -250, and at least 30 unique written words. Caps and evidence limitations can downgrade a selection.</div>{pick_table(PICKS)}"
    return page("Selections", "picks", body)


def render_predictions():
    body = f"<p class='eyebrow'>Full written analysis</p><h1>Predictions</h1><p class='lede'>Every retained match has a unique write-up, not just a winner list. High selections appear first within each sport. Official facts, availability boundaries and prediction locations remain beside the prose.</p>"
    for slug, name, _ in D.SPORTS:
        fs = [f for f in FIXTURES if f["sport"] == slug]
        if not fs:
            continue
        body += f"<section class='anchor' id='{slug}'><h2>{esc(name)} <span class='sub'>{len(fs)} predictions</span></h2>"
        for f in sorted(fs, key=lambda x: ({"High": 0, "Medium": 1, "Low": 2}[x["pick"]["confidence"]], -x["pick"]["probability"])):
            body += prediction_card(f)
        body += "</section>"
    return page("Written predictions", "predictions", body)


def render_matches():
    rows = []
    for f in sorted(FIXTURES, key=lambda x: (x["start_utc"] == "", x["start_utc"], x["sport"])):
        p = f["pick"]
        rows.append(f"<tr><td>{when(f['start_utc'])}<span class='sub'>{esc(f['venue'])}</span></td><td><strong>{esc(f['a'])} v {esc(f['b'])}</strong><span class='sub'>{esc(SPORT_NAME[f['sport']])} · {esc(f['competition'])}<br>Official ID: {esc(f['official_id'])}</span></td><td>{esc(p['match_winner_lean'])}<span class='sub'>{p['match_winner_probability']*100:.1f}% · {p['match_winner_american']:+d} · {esc(p['match_winner_confidence'])}</span></td><td>{esc(p['selection'])}<span class='sub'>{p['american']:+d} · {badge(p['confidence'])}</span></td><td><a href='sports/{f['sport']}.html#{f['id']}'>Markets</a> · <a href='predictions.html#prediction-{f['id']}'>Prediction</a><span class='sub'>{'Review notes attached' if f['review_reasons'] else 'No row-specific review note'}</span></td><td>{links(f['source_ids'])}</td></tr>")
    body = f"<p class='eyebrow'>Complete retained card</p><h1>Every match</h1><p class='lede'>All {len(FIXTURES)} retained fixtures, including low-confidence and blank-time entries. Rejected, contradictory and started discoveries are listed on Flagged for Review rather than hidden here as live picks.</p><div class='table-wrap'><table><thead><tr><th>Start / venue</th><th>Match / IDs</th><th>Winner lean</th><th>Selection</th><th>Findings</th><th>Official review links</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>"
    return page("Every match", "matches", body)


def render_sports():
    rows = []
    for c in COVERAGE:
        rows.append(f"<tr><td><a href='sports/{c['sport']}.html'><strong>{esc(c['name'])}</strong></a></td><td class='num'>{c['fixtures']}</td><td class='num'>{c['picks']}</td><td class='num'>{c['high']}</td><td class='num'>{c['written_predictions']}</td><td class='num'>{c['withheld_markets']}</td><td>{esc(c['note'])}</td><td>{links(c['official_source_ids'])}</td></tr>")
    body = f"<p class='eyebrow'>Exact requested scope</p><h1>15 sports</h1><p class='lede'>No sport is silently omitted. A zero means no supported selection survived the evidence and start-time gates, not that the category was forgotten.</p><div class='table-wrap'><table><thead><tr><th>Category</th><th>Fixtures</th><th>Picks</th><th>High</th><th>Written</th><th>Blank markets</th><th>Coverage finding</th><th>Official review links</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>"
    return page("15 sports", "sports", body)


def render_sport(slug):
    c = next(x for x in COVERAGE if x["sport"] == slug)
    fs = [f for f in FIXTURES if f["sport"] == slug]
    body = f"<p class='eyebrow'><a href='../sports.html'>15 sports</a> / {esc(c['name'])}</p><h1>{esc(c['name'])}</h1><p class='lede'>{esc(c['note'])}</p><div class='kpis'><div class='kpi'><b>{c['fixtures']}</b><span>Fixtures</span></div><div class='kpi'><b>{c['picks']}</b><span>Picks</span></div><div class='kpi'><b>{c['high']}</b><span>High</span></div><div class='kpi'><b>{c['withheld_markets']}</b><span>Blank markets</span></div></div>"
    if not fs:
        related = [f for f in FLAGS if f["sport"] == slug]
        body += "<div class='note bad'><strong>No supported selection published.</strong> The reasons and official review links below are part of the result.</div>"
        for f in related:
            body += f"<div class='panel'><h3>{esc(f['title'])}</h3><p>{esc(f['detail'])}</p><p class='small'>OLBG event/listing: {esc(f['event_ids'])}</p>{links(f['source_ids'])}</div>"
        return page(c["name"], "sports", body, "../")
    body += pick_table([f["pick"] for f in fs], "../")
    for f in fs:
        p = f["pick"]
        facts = "".join(f"<li>{esc(x)}</li>" for x in f["facts"])
        body += f"""<section class="anchor" id="{esc(f['id'])}"><div class="panel"><span class="eyebrow">{esc(f['competition'])} · OLBG {esc(f['olbg_event_id'])}</span><h2>{esc(f['a'])} v {esc(f['b'])}</h2><p>{when(f['start_utc'])} · {esc(f['venue'] or 'Venue not published')}<br><strong>Official event reference:</strong> {esc(f['official_id'])}</p><p><strong>Selection: {esc(p['selection'])}</strong> · {p['american']:+d} · {p['probability']*100:.1f}% · {badge(p['confidence'])}</p><p>{esc(f['analysis'])}</p><p><a href="../predictions.html#prediction-{esc(f['id'])}">Prediction location</a> · <a href="{esc(f['olbg_url'])}" target="_blank" rel="noopener noreferrer">OLBG discovery listing ↗</a> <span class="small">({esc(f['olbg_tip'])})</span></p><h3>Official facts used</h3><ul class="facts">{facts}</ul><p class="small"><strong>Availability:</strong> {esc(f['availability'])}</p><p class="small"><strong>Review:</strong> {esc(f['review_reasons'] or 'No row-specific limitation beyond the source notes.')}</p>{links(f['source_ids'])}</div>{fixture_markets(f)}</section>"""
    return page(c["name"], "sports", body, "../")


def render_flagged():
    rows = []
    for f in FLAGS:
        target = f"<a href='sports/{f['sport']}.html#{f['fixture_id']}'>Fixture</a> · " if f.get("fixture_id") else ""
        rows.append(f"<tr id='{esc(f['id'])}'><td><span class='badge {'red' if f['severity'] in ('expired','contradiction','unconfirmed') else 'Medium'}'>{esc(f['severity'])}</span></td><td><strong>{esc(f['title'])}</strong><span class='sub'>{esc(SPORT_NAME[f['sport']])} · {esc(f['id'])}</span></td><td>{esc(f['detail'])}<span class='sub'>{target}<a href='{esc(f['olbg_url'])}' target='_blank' rel='noopener noreferrer'>OLBG discovery ↗</a> · IDs: {esc(f['event_ids'])}</span></td><td>{links(f['source_ids'])}</td></tr>")
    body = f"<p class='eyebrow'>Irregularities, blanks and exclusions</p><h1>Flagged for Review</h1><p class='lede'>These notes do not block publication. They make uncertainty inspectable: {len(D.FLAGS)} desk-level findings plus one consolidated row for every retained fixture with a blank or withheld field.</p><div class='note bad'><strong>Do not treat blank as zero.</strong> Missing starts, venues, totals, player markets and availability boundaries remain unpublished. Started fixtures and contradictory pairings are excluded from selections.</div><div class='table-wrap'><table><thead><tr><th>Severity</th><th>Finding</th><th>Detail / discovery ID</th><th>Official review links</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>"
    return page("Flagged for Review", "flagged", body)


def render_sources():
    rows = "".join(f"<tr><td><strong>{esc(s['label'])}</strong><span class='sub'>{esc(s['publisher'])} · official</span></td><td>{esc(s['observed_at'])}</td><td>{esc(s['supports'])}</td><td>{esc(s['limitation'])}</td><td><span class='code'>{esc(s['external_ids'])}</span></td><td><a href='{esc(s['url'])}' target='_blank' rel='noopener noreferrer'>Open official source ↗</a></td></tr>" for s in D.SOURCES)
    body = f"<p class='eyebrow'>Manual review register</p><h1>Official sources</h1><p class='lede'>{len(D.SOURCES)} official references with read timestamps, supported fields, external IDs and limitations. OLBG links live separately on the coverage-mapping page.</p><div class='table-wrap'><table><thead><tr><th>Source / publisher</th><th>Observed UTC</th><th>What it supports</th><th>Read limitation</th><th>External IDs</th><th>Direct link</th></tr></thead><tbody>{rows}</tbody></table></div>"
    return page("Official sources", "sources", body)


def render_method():
    body = f"""<p class="eyebrow">How the desk works</p><h1>Pricing & evidence method</h1><p class="lede">Facts and estimates are separate fields. Official sources establish the fixture and input facts; the desk originates its own probabilities and fair prices. OLBG supplies discovery listings and tip-share metadata only.</p>
<div class="grid"><div class="panel"><h2>1 · Discovery</h2><p>Read all 15 relevant OLBG hubs and preserve event IDs, listed market labels and vote shares. A listing never confirms a sporting fact.</p></div><div class="panel"><h2>2 · Official check</h2><p>Confirm participants and scheduling with league, federation, broadcaster-owned competition or official data endpoints. Record URLs, timestamps, external IDs and read limitations.</p></div><div class="panel"><h2>3 · Publication gate</h2><p>Exclude events whose official start precedes {esc(D.CUTOFF)}. Blank start fields are permitted only with a review note; started events cannot receive picks.</p></div><div class="panel"><h2>4 · Independent prices</h2><p>Winner prices use current records, rankings, scoring or recent results with shrinkage and venue adjustments. Handicaps use explicit sport-specific margin distributions. Totals use Poisson or normal assumptions only where an official scoring baseline exists.</p></div><div class="panel"><h2>5 · Zero-vig presentation</h2><p>Outcome probabilities in each published market sum to 100%. Decimal price is 1/p. American price is -100p/(1-p) at 50% or above and +100(1-p)/p below 50%. These are fair estimates, not offers.</p></div><div class="panel"><h2>6 · Confidence</h2><p><strong>High:</strong> at least 70%, fair price no shorter than -250 and at least 30 unique written words, with no lower evidence cap. <strong>Medium:</strong> generally 56% upward or a shorter-than-window price. <strong>Low:</strong> close matchups, underdogs or materially incomplete evidence.</p></div></div>
<section><h2>Sport-specific assumptions</h2><div class="panel"><ul class="checklist"><li><strong>NHL:</strong> points share, team GAA and home advantage; margin SD 2.15; Poisson totals from combined team GAA.</li><li><strong>NBA:</strong> heavily shrunk early records, home advantage and official availability; margin SD 12. Totals stay blank without official scoring averages.</li><li><strong>MLB:</strong> season offence, run prevention and probable-starter ERA; Poisson total and a 3.6-run margin SD.</li><li><strong>Volleyball:</strong> round-one sets/points with heavy one-round shrinkage; 1.25-set margin SD and explicit best-of-five total-set assumptions.</li><li><strong>Rugby and handball:</strong> table points, scoring differential and venue; normal margin/total assumptions are printed beside each market.</li><li><strong>Tennis:</strong> ranking, surface form, tournament/head-to-head history and semi-final workload; 5.4-game margin SD.</li><li><strong>Gaelic sports:</strong> official final history and recent margins; totals stay blank where only margins, not scoring averages, are available.</li><li><strong>Cricket:</strong> only supported series/form/home information. Runs handicaps, totals and player props stay blank without an official scoring distribution.</li></ul></div></section>
<section><h2>Known boundaries</h2><p class="lede">Small samples are not presented as established trends. Listed goalies are not called starters unless officially designated. Silence on an injury page is not a clean bill of health. Dynamic shells, unavailable rankings and unread brackets create blanks, not guesses. Prediction prose never uses the two prohibited publication terms.</p></section>"""
    return page("Methodology", "method", body)


def render_reverse():
    rows = []
    for obs, c in zip(D.OLBG_OBSERVATIONS, COVERAGE):
        retained = ", ".join(obs["retained_fixture_ids"]) or "No retained fixtures"
        rows.append(f"<tr id='{obs['sport']}'><td><strong>{esc(c['name'])}</strong><span class='sub'><a href='{esc(obs['url'])}' target='_blank' rel='noopener noreferrer'>OLBG hub ↗</a> · {esc(obs['observed_at'])}</span></td><td>{esc(obs['role'])}</td><td><span class='code'>{esc(retained)}</span><span class='sub'>{esc(obs['note'])}</span></td><td>{links(c['official_source_ids'])}</td></tr>")
    event_rows = "".join(f"<tr><td>{esc(f['a'])} v {esc(f['b'])}</td><td><span class='code'>{esc(f['olbg_event_id'])}</span></td><td>{esc(f['olbg_tip'])}</td><td><a href='{esc(f['olbg_url'])}' target='_blank' rel='noopener noreferrer'>Discovery listing ↗</a></td><td>{links(f['source_ids'])}</td></tr>" for f in FIXTURES)
    body = f"<p class='eyebrow'>Reverse-engineered coverage</p><h1>Inside the OLBG listings</h1><p class='lede'>The discovery layer is separated from official evidence. This page preserves all 16 relevant hub reads across the 15 sports (football and hurling combine under Gaelic Sports), event IDs, listed leans and the official links used to accept or reject each row.</p><h2>Hub coverage</h2><div class='table-wrap'><table><thead><tr><th>Sport / observed</th><th>Role</th><th>Retained mapping</th><th>Official review links</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div><h2>Retained event IDs and listed leans</h2><p>Tip shares are observations, not probabilities and not inputs to the fair prices.</p><div class='table-wrap'><table><thead><tr><th>Match</th><th>OLBG event</th><th>Observed listing</th><th>Discovery</th><th>Official review links</th></tr></thead><tbody>{event_rows}</tbody></table></div>"
    return page("OLBG coverage mapping", "reverse", body)


def render_repo_audit():
    path = DATA / "repo-audit.json"
    if path.exists():
        audit = json.loads(path.read_text())
    else:
        audit = {"snapshot": D.SNAPSHOT, "tracked_files": 0, "text_files_scanned": 0,
                 "lines_scanned": 0, "binary_files_skipped": 0, "findings": [],
                 "scope": "Audit has not yet been run.", "limitations": []}
    findings = audit.get("findings", [])
    rows = "".join(f"<tr><td>{esc(x['severity'])}</td><td><span class='code'>{esc(x['path'])}:{x['line']}</span></td><td>{esc(x['check'])}</td><td>{esc(x['excerpt'])}</td><td><a href='{REPO}/blob/arena/29dd717c-olbg1/{esc(x['path'])}#L{x['line']}' target='_blank' rel='noopener noreferrer'>Open line ↗</a></td></tr>" for x in findings)
    if not rows:
        rows = "<tr><td colspan='5'>No release-relevant findings in the completed scan.</td></tr>"
    limitations = "".join(f"<li>{esc(x)}</li>" for x in audit.get("limitations", []))
    body = f"""<p class="eyebrow">Line-by-line release audit</p><h1>Repository audit</h1><p class="lede">{esc(audit.get('scope',''))}</p><div class="kpis"><div class="kpi"><b>{audit.get('tracked_files',0)}</b><span>Files inventoried</span></div><div class="kpi"><b>{audit.get('text_files_scanned',0)}</b><span>Text files scanned</span></div><div class="kpi"><b>{audit.get('lines_scanned',0):,}</b><span>Lines read</span></div><div class="kpi"><b>{len(findings)}</b><span>Published findings</span></div></div><div class="panel"><h2>Checks and boundaries</h2><p>Every tracked text file is read line by line for unresolved conflict markers. Release-critical integration files and this desk additionally receive placeholder, localhost, prohibited-prose and local-link checks. Historical desks are inventoried but not rewritten.</p><ul>{limitations}</ul><p class="small">Scan snapshot {esc(audit.get('snapshot',D.SNAPSHOT))}. Generated HTML link validation and data/probability gates are also enforced by the desk test suite.</p></div><div class="table-wrap"><table><thead><tr><th>Severity</th><th>Location</th><th>Check</th><th>Excerpt</th><th>Repository line</th></tr></thead><tbody>{rows}</tbody></table></div>"""
    return page("Repository audit", "repo", body)


def write_data():
    DATA.mkdir(parents=True, exist_ok=True)
    dump(DATA / "fixtures.json", {"generated_at": D.SNAPSHOT, "fixtures": FIXTURES})
    dump(DATA / "lines.json", {"generated_at": D.SNAPSHOT, "method": "Independent zero-vig fair prices", "lines": LINES})
    dump(DATA / "picks.json", {"generated_at": D.SNAPSHOT, "picks": PICKS})
    dump(DATA / "predictions.json", {"generated_at": D.SNAPSHOT, "predictions": PICKS})
    dump(DATA / "sources.json", {"generated_at": D.SNAPSHOT, "sources": D.SOURCES})
    dump(DATA / "flags.json", {"generated_at": D.SNAPSHOT, "flags": FLAGS})
    dump(DATA / "coverage.json", {"generated_at": D.SNAPSHOT, "coverage": COVERAGE})
    dump(DATA / "olbg.json", {"generated_at": D.SNAPSHOT, "role": "discovery only", "observations": D.OLBG_OBSERVATIONS})
    manifest = {"desk": "29dd717c", "generated_at": D.SNAPSHOT, "cutoff": D.CUTOFF,
                "counts": {"sports": 15, "active_sports": sum(bool(c["picks"]) for c in COVERAGE),
                           "fixtures": len(FIXTURES), "picks": len(PICKS),
                           "predictions": len(PICKS), "lines": len(LINES),
                           "high": sum(p["confidence"] == "High" for p in PICKS),
                           "sources": len(D.SOURCES), "flags": len(FLAGS)},
                "files": ["fixtures.json", "lines.json", "picks.json", "predictions.json", "sources.json", "flags.json", "coverage.json", "olbg.json", "repo-audit.json"]}
    dump(DATA / "manifest.json", manifest)


def write_site():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "assets").mkdir(exist_ok=True)
    (OUT / "assets" / "style.css").write_text(CSS, encoding="utf-8")
    (OUT / "sports").mkdir(exist_ok=True)
    pages = {"index.html": render_index(), "picks.html": render_picks(),
             "predictions.html": render_predictions(), "matches.html": render_matches(),
             "sports.html": render_sports(), "flagged.html": render_flagged(),
             "sources.html": render_sources(), "methodology.html": render_method(),
             "reverse-engineering.html": render_reverse(), "repository-audit.html": render_repo_audit()}
    for slug, _name, _url in D.SPORTS:
        pages[f"sports/{slug}.html"] = render_sport(slug)
    for rel, text in pages.items():
        (OUT / rel).write_text(text, encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    return pages


def main():
    write_data()
    pages = write_site()
    print(json.dumps({"desk": "29dd717c", "pages": len(pages), "fixtures": len(FIXTURES),
                      "picks": len(PICKS), "high": sum(p["confidence"] == "High" for p in PICKS),
                      "lines": len(LINES), "flags": len(FLAGS), "sources": len(D.SOURCES)}, indent=2))


if __name__ == "__main__":
    main()
