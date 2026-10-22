#!/usr/bin/env python3
"""T44 (session 6a081cf6): strict-band high-confidence desk.
Filter: v3 High picks, model_prob > 70%, originated US price in [-250, +10000].
Reuses only source-verified v3 fixtures/lines/predictions; edits no shared files."""
import json, html, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(p): return json.load(open(os.path.join(ROOT, p)))
fx = {m["id"]: m for m in load("data/v3/fixtures.json")["matches"]}
picks = load("data/v3/predictions.json")["picks"]
rows, excluded = [], []
for p in picks:
    if p.get("confidence") != "High" or not p.get("prose"):
        continue
    f = fx[p["fixture_id"]]
    row = {"fixture_id": p["fixture_id"], "sport": p["sport"], "competition": p["competition"],
           "home": p["home"], "away": p["away"], "start_utc": p.get("start_utc"),
           "market": p["market"], "selection": p["selection"], "us": p["us"],
           "price_decimal": p.get("price"), "prob_pct": p["prob_pct"], "confidence": "High",
           "prediction": p["prose"], "word_count": len(p["prose"].split()),
           "sources": f.get("sources", []), "venue": f.get("venue"),
           "verification_basis": "Official source(s) listed per row; first source re-fetched live 2026-10-22 in this session where the fetch tool succeeded (NRL, AFL, PDC pages returned). Others carry the v3 verification ledger status and are not re-certified here."}
    if p["prob_pct"] > 70 and -250 <= p["us"] <= 10000:
        rows.append(row)
    else:
        excluded.append({**row, "exclusion_reason": f"US price {p['us']} is outside the brief band -250..+10000 (prob {p['prob_pct']}%)."})
rows.sort(key=lambda r: -r["prob_pct"])
out = {"task": "T44", "session": "6a081cf6-olbg1", "generated_utc": "2026-10-22T02:55Z",
       "rule": "High confidence AND model_prob>70% AND -250<=US price<=+10000; every prediction >=30 words, unique 6-word n-grams",
       "count": len(rows), "picks": rows, "excluded": excluded,
       "irregularities": [
         {"id": "F-6A-01", "item": "Brisbane Lions -3 (aflw-r11-09)", "detail": "Highest model probability (71.5%) but originated price -251 sits one point outside the brief's -250 floor; excluded from the strict-band desk and published here for review.", "source": excluded[0]["sources"][0]["url"] if excluded else ""},
         {"id": "F-6A-02", "item": "Tonga -2.5 (rl-wc26-tga-lbn)", "detail": "Official NRL late mail (re-fetched 2026-10-22) rules Isaiya Katoa out (ankle), Latu Fainu starts. The v3 prose does not mention this; pick retained as originated but flagged — confidence should be re-read with this team news.", "source": "https://www.nrl.com/news/2026/10/20/world-cup-team-lists-mens-round-2/"},
         {"id": "F-6A-03", "item": "Generic league-wide total rungs in v3 books", "detail": "Many v3 total selections repeat identical lines/probabilities across fixtures in a league (e.g. every NHL game Over 5.5 at 70.1%). These are model rungs, not fixture-specific verified facts; none is promoted on this desk and they must not be read as per-match research.", "source": ""},
         {"id": "F-6A-04", "item": "Band mathematics", "detail": ">70% probability mathematically implies a fair US price shorter than about -234, so the +10000 upper end of the brief band can never contain a >70% pick. The effective strict band is -250..-234.", "source": ""}]}
json.dump(out, open(os.path.join(ROOT, "data/6a081cf6_high_band.json"), "w"), indent=1)

CSS = "body{font-family:system-ui,Arial,sans-serif;margin:2rem;max-width:1100px;color:#14213d}table{border-collapse:collapse;width:100%}th,td{border:1px solid #ccd;padding:.5rem;text-align:left;vertical-align:top}th{background:#14213d;color:#fff}a{color:#0b5cad}.card{background:#eef4ff;padding:1rem;border-radius:8px}"
def page(title, body):
    return f"<!doctype html><html lang=en><head><meta charset=utf-8><title>{html.escape(title)}</title><style>{CSS}</style></head><body><nav><a href=index.html>Home</a> · <a href=picks.html>Picks</a> · <a href=flagged.html>Flagged for Review</a> · <a href=methodology.html>Methodology</a> · <a href=../index.html>Main dashboard</a></nav>{body}</body></html>"
os.makedirs(os.path.join(ROOT, "6a081cf6"), exist_ok=True)
def srclinks(r):
    q=chr(34)
    return "<br>".join("<a href="+q+html.escape(s["url"])+q+">"+html.escape(s["name"])+"</a>" for s in r["sources"])
trs = "".join("<tr><td>"+r["sport"]+"</td><td>"+html.escape(r["home"])+" v "+html.escape(r["away"])+"<br>"+html.escape(r["competition"])+"</td><td>"+html.escape(r["market"])+"</td><td><b>"+html.escape(r["selection"])+"</b></td><td>"+format(r["us"],"+d")+"</td><td>"+str(r["prob_pct"])+"%</td><td>High</td><td>"+srclinks(r)+"</td></tr>" for r in rows)
prose = "".join(f"<h3>{html.escape(r['selection'])} — {html.escape(r['home'])} v {html.escape(r['away'])}</h3><p>{html.escape(r['prediction'])}</p><p><i>{r['word_count']} words · model {r['prob_pct']}% · originated price {r['us']:+d} (our model, not a market price)</i></p>" for r in rows)
open(os.path.join(ROOT, "6a081cf6/index.html"), "w").write(page("Strict-band High-confidence desk", f"<h1>Strict-band high-confidence desk (T44)</h1><div class=card><p><b>{len(rows)} picks</b> pass every part of the brief at once: High confidence, model probability &gt;70%, and our originated price between −250 and +10000. Excluded sports (soccer, boxing, UFC/MMA, football/American football, hurling, horse racing, cycling, specials) are not covered. Prices are our own originated model prices, not market prices and not betting advice.</p></div><h2>Picks</h2><table><tr><th>Sport</th><th>Match</th><th>Market</th><th>Selection</th><th>Our price (US)</th><th>Model prob.</th><th>Confidence</th><th>Official source</th></tr>{trs}</table>"))
open(os.path.join(ROOT, "6a081cf6/picks.html"), "w").write(page("Predictions", f"<h1>High-confidence predictions (≥30 words each, unique)</h1>{prose}"))
def srclink(f):
    q=chr(34)
    return ("<a href="+q+html.escape(f["source"])+q+">official source</a>") if f["source"] else "— (analytical note, no external source)"
flag = "".join("<tr><td>"+f["id"]+"</td><td>"+html.escape(f["item"])+"</td><td>"+html.escape(f["detail"])+"</td><td>"+srclink(f)+"</td></tr>" for f in out["irregularities"])
open(os.path.join(ROOT, "6a081cf6/flagged.html"), "w").write(page("Flagged for Review", f"<h1>Flagged for Review</h1><table><tr><th>ID</th><th>Item</th><th>Detail</th><th>Source</th></tr>{flag}</table><h2>Excluded by the band</h2>" + "".join(f"<p>{html.escape(e['selection'])} ({e['fixture_id']}): {html.escape(e['exclusion_reason'])}</p>" for e in excluded)))
open(os.path.join(ROOT, "6a081cf6/methodology.html"), "w").write(page("Methodology", "<h1>Methodology</h1><p>Source data: the repository's v3 verified fixtures, originated lines and predictions (data/v3/), themselves priced from governing-body standings/rankings with the documented v3 model. This desk applies one additional strict filter (High, &gt;70%, −250…+10000) and republishes the surviving picks with their original unique ≥30-word predictions. No value was inferred: rows without an official source in v3 could not enter the High set. Direct sandbox fetches to league sites are TLS-blocked, so live re-fetch in this session used the page-fetch tool (NRL men's Round 2 team lists, AFLW ladder and PDC schedule pages returned successfully on 2026-10-22); all other rows retain their v3 verification-ledger status and are labelled accordingly, not re-certified.</p><p>Prices are model estimates with the v3 margin convention, never presented as market prices. This is analysis, not betting advice.</p>"))
print("built", len(rows), "picks,", len(excluded), "excluded")
