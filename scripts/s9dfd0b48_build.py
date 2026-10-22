#!/usr/bin/env python3
"""Session 9dfd0b48-olbg1 (task T44) — originate lines, pick winners, write the desk.

Outputs
  data/9dfd0b48/{fixtures,markets,picks,predictions,flags,sources,coverage}.json, matches.csv
  9dfd0b48/*.html (static, relative links, works on GitHub Pages)

Run:  python3 scripts/s9dfd0b48_build.py && python3 scripts/s9dfd0b48_validate.py
"""
from __future__ import annotations

import csv
import html
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s9dfd0b48_data as D  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "9dfd0b48")
SITE = os.path.join(ROOT, "9dfd0b48")
SESSION = "9dfd0b48-olbg1"
TASK = "T44"
VIG = 0.045  # total overround applied symmetrically to two-way markets
WINDOW = (-250, 10000)


# ------------------------------------------------------------------ pricing helpers
def american(p: float) -> int:
    p = min(max(p, 0.005), 0.995)
    if p >= 0.5:
        return -int(round(100 * p / (1 - p)))
    return int(round(100 * (1 - p) / p))


def fmt(a: int | None) -> str:
    if a is None:
        return ""
    return f"{a:+d}" if a > 0 else str(a)


def two_way(p_a: float):
    """Fair prob -> (priceA, priceB) with VIG split evenly."""
    pa = p_a * (1 + VIG) / 1.0
    pb = (1 - p_a) * (1 + VIG)
    s = pa + pb
    pa, pb = pa / s * (1 + VIG), pb / s * (1 + VIG)
    return american(pa / (1 + VIG) + VIG / 2), american(pb / (1 + VIG) + VIG / 2)


def in_window(a: int) -> bool:
    return WINDOW[0] <= a <= WINDOW[1]


def norm_cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def tier(p: float) -> str:
    return "High" if p >= 0.70 else "Medium" if p >= 0.58 else "Low"


# ------------------------------------------------------------------ sport models
def model_tennis(fx):
    ra, rb = D.ATP[fx["a"]], D.ATP[fx["b"]]
    if ra[1] is None or rb[1] is None:
        return None
    k = 0.55
    pa = 1 / (1 + (rb[1] / ra[1]) ** k)
    fav, p = (fx["a"], pa) if pa >= 0.5 else (fx["b"], 1 - pa)
    hcp = 1.5 if p < 0.58 else 2.5 if p < 0.64 else 3.5 if p < 0.70 else 4.5 if p < 0.76 else 5.5
    p_over = 0.5 - (p - 0.5) * 0.45
    mk = [
        ("Match winner", fx["a"], fx["b"], pa),
        ("Game handicap", f"{fav} -{hcp}", f"{(fx['b'] if fav == fx['a'] else fx['a'])} +{hcp}", 0.5 + (p - 0.5) * 0.12),
        ("Total games 22.5", "Over 22.5", "Under 22.5", p_over),
    ]
    inputs = f"ATP {fx['a']} #{ra[0]} ({ra[1]:,} pts) v {fx['b']} #{rb[0]} ({rb[1]:,} pts), list 2026-10-19"
    return pa, mk, inputs


def model_snooker(fx):
    def money(n):
        return D.WST.get(n, (None, None))[1]
    ma, mb = money(fx["a"]), money(fx["b"])
    bounded = False
    if ma is None and mb is None:
        pa = 0.5
        inputs = "Neither player inside the WST top-36 list read; no ranking differential can be verified — even prior"
    else:
        bounded = True
        ua = ma if ma is not None else D.WST_36TH_MONEY
        ub = mb if mb is not None else D.WST_36TH_MONEY
        pa = 1 / (1 + (ub / ua) ** 0.45)
        inputs = (f"WST ranking money: {fx['a']} {'£%s' % format(ma, ',') if ma else '< £198,500 (outside top 36)'} v "
                  f"{fx['b']} {'£%s' % format(mb, ',') if mb else '< £198,500 (outside top 36)'}; unranked side priced at the 36th-place ceiling (bound, not estimate)")
    fav, p = (fx["a"], pa) if pa >= 0.5 else (fx["b"], 1 - pa)
    other = fx["b"] if fav == fx["a"] else fx["a"]
    mk = [
        ("Match winner", fx["a"], fx["b"], pa),
        ("Frame handicap", f"{fav} -1.5", f"{other} +1.5", 0.5 + (p - 0.5) * 0.55 - 0.08),
        ("Total frames 5.5", "Over 5.5", "Under 5.5", 0.5 - (p - 0.5) * 0.4 + 0.04),
    ]
    return pa, mk, inputs


def model_basketball(fx):
    ha, aw = D.EL[fx["a"]], D.EL[fx["b"]]
    da = 0.6 * (ha[3] - ha[4]) / ha[0]
    db = 0.6 * (aw[3] - aw[4]) / aw[0]
    margin = da - db + 3.0
    pa = norm_cdf(margin / 11.5)
    spread = round(margin * 2) / 2
    total = round(((ha[3] + ha[4]) / ha[0] + (aw[3] + aw[4]) / aw[0]) / 2 * 2) / 2
    fav, other = (fx["a"], fx["b"]) if spread >= 0 else (fx["b"], fx["a"])
    s = abs(spread)
    if s == int(s):
        s += 0.5
    mk = [
        ("Money line", fx["a"], fx["b"], pa),
        ("Point spread", f"{fav} -{s}", f"{other} +{s}", 0.5 + 0.02 * (1 if spread >= 0 else -1)),
        (f"Total points {total}", f"Over {total}", f"Under {total}", 0.5),
    ]
    inputs = (f"EuroLeague: {fx['a']} {ha[1]}-{ha[2]}, {ha[3]}-{ha[4]} pts, home {ha[5]}, L10 {ha[7]}; "
              f"{fx['b']} {aw[1]}-{aw[2]}, {aw[3]}-{aw[4]} pts, away {aw[6]}, L10 {aw[7]}; home edge +3.0, margin sd 11.5")
    return pa, mk, inputs


def model_baseball(fx):
    h, a = D.MLB[fx["a"]], D.MLB[fx["b"]]
    ph = h["rs"] ** 1.83 / (h["rs"] ** 1.83 + h["ra"] ** 1.83)
    pa_ = a["rs"] ** 1.83 / (a["rs"] ** 1.83 + a["ra"] ** 1.83)
    log5 = (ph - ph * pa_) / (ph + pa_ - 2 * ph * pa_)
    p = log5 + 0.035  # home edge
    tot_h = (h["rs"] + h["ra"]) / (h["w"] + h["l"])
    tot_a = (a["rs"] + a["ra"]) / (a["w"] + a["l"])
    total = 8.5
    p_over = 0.5 + ((tot_h + tot_a) / 2 - total) * 0.06
    mk = [
        ("Money line", fx["a"], fx["b"], p),
        ("Run line", f"{fx['a']} -1.5", f"{fx['b']} +1.5", p - 0.19),
        ("Total runs 8.5", "Over 8.5", "Under 8.5", p_over),
    ]
    inputs = (f"2026 regular season: {fx['a']} {h['w']}-{h['l']}, RS {h['rs']} RA {h['ra']}, home {h['home']}, streak {h['streak']}; "
              f"{fx['b']} {a['w']}-{a['l']}, RS {a['rs']} RA {a['ra']}, streak {a['streak']}; Pythagorean (1.83) log5 + 3.5pt home edge")
    return p, mk, inputs


MODELS = {"tennis": model_tennis, "snooker": model_snooker, "basketball": model_basketball, "baseball": model_baseball}

# ------------------------------------------------------------------ High-pick prose (hand-written, >=30 words, unique)
PREDICTIONS = {
    "T03": ("Daniil Medvedev", "Medvedev arrives in Almaty as the top seed and the world number five with 3,660 ranking points on the 19 October list, "
            "while Sho Shimabukuro sits 109th with 555. The Japanese world number 109 has earned his place in the last sixteen, but a ranking gap of more than a hundred "
            "places on a quick indoor court is where Medvedev's return game usually settles matters in straight sets. Selection: Medvedev, taken on the -4.5 game handicap because his outright price is shorter than -250."),
    "T10": ("Flavio Cobolli", "Lyon's top seed Flavio Cobolli, ranked sixth with 3,640 points, meets Stan Wawrinka under the lights on Court Central not "
            "before 19:00 local. Wawrinka is a wildcard ranked 140th on 401 points; the three-time major winner still has the backhand and the crowd, "
            "but across a best-of-three indoors the younger legs and the deeper 2026 résumé should carry the match. Selection: Cobolli, and the -5.5 "
            "game line is the price that sits inside the window."),
    "B04": ("Panathinaikos AKTOR Athens", "Panathinaikos lead the EuroLeague table at 5-1 with a plus-90 point difference across six rounds, 4-1 at the "
            "Telekom Center, and 5-1 over their last ten. Baskonia are bottom at 1-5, minus 60, and 0-2 on the road. The money line is far too short "
            "to be playable, so the originated selection is Panathinaikos -18.5 on the spread, where a double-digit home margin is the model's central case "
            "rather than an outlier."),
}


# ------------------------------------------------------------------ build data
def build():
    fixtures, markets, picks, preds, flags = [], [], [], [], []
    for fx in D.FIXTURES:
        res = MODELS[fx["kind"]](fx)
        row = dict(fx)
        row["sources"] = [{"id": s, "url": D.SOURCES[s]["url"], "title": D.SOURCES[s]["title"], "fetched": D.SOURCES[s]["fetched"]} for s in fx["src"]]
        row["verified"] = True
        if res is None:
            row["priced"] = False
            row["inputs"] = "Ranking points for one player not inside the 191 ATP ranks read this session — left blank"
            flags.append(dict(code="UNPRICED", ref=fx["id"], sport=fx["sport"], label=f"{fx['a']} v {fx['b']}",
                              detail=row["inputs"], url=row["sources"][0]["url"], severity="medium"))
            fixtures.append(row)
            continue
        pa, mk, inputs = res
        row["priced"] = True
        row["inputs"] = inputs
        fixtures.append(row)
        winner_prices = None
        for name, sa, sb, p in mk:
            a1, a2 = two_way(p)
            m = dict(fixture=fx["id"], market=name, sel_a=sa, sel_b=sb, p_a=round(p, 4), p_b=round(1 - p, 4),
                     price_a=a1, price_b=a2, in_window_a=in_window(a1), in_window_b=in_window(a2), source=row["sources"][0]["url"])
            markets.append(m)
            if winner_prices is None:
                winner_prices = m
        pick_side = fx["a"] if pa >= 0.5 else fx["b"]
        p_pick = pa if pa >= 0.5 else 1 - pa
        price = winner_prices["price_a"] if pa >= 0.5 else winner_prices["price_b"]
        t = tier(p_pick)
        featured = dict(market="Match winner" if fx["kind"] in ("tennis", "snooker") else "Money line", selection=pick_side, price=price)
        if t == "High" and not in_window(price):
            spread = [m for m in markets if m["fixture"] == fx["id"]][1]
            featured = dict(market=spread["market"], selection=spread["sel_a"], price=spread["price_a"],
                            note="money line shorter than -250; featured selection moved to the handicap inside the -250/+10000 window")
        picks.append(dict(fixture=fx["id"], sport=fx["sport"], comp=fx["comp"], label=f"{fx['a']} v {fx['b']}", start=fx["start"],
                          pick=pick_side, p=round(p_pick, 4), price=price, in_window=in_window(price), confidence=t,
                          featured=featured, olbg=fx.get("olbg"), olbg_tips=fx.get("olbg_tips"), source=row["sources"][0]["url"]))
        if t == "High":
            who, text = PREDICTIONS[fx["id"]]
            assert who == pick_side, (fx["id"], who, pick_side)
            preds.append(dict(fixture=fx["id"], sport=fx["sport"], label=f"{fx['a']} v {fx['b']}", selection=who,
                              featured=featured, words=len(text.split()), text=text, sources=[s["url"] for s in row["sources"]]))
    # unverified listings -> flags
    for sport, label, start, url, tips, code in D.UNVERIFIED:
        reason, src = D.REASONS[code]
        flags.append(dict(code=code, ref=None, sport=sport, label=label, start=start, detail=reason,
                          url=url, official_attempt=(D.SOURCES[src]["url"] if src else None), olbg_tips=tips,
                          severity="info" if code == "EMPTY" else "medium"))
    flags.append(dict(code="CLOCK", ref=None, sport="All", label="Hub clock conversion",
                      detail="OLBG hub and euroleaguebasketball.net/wst.tv session times were rendered in UTC-4 by the fetch client; all UTC values here add 4h. Each converted time was cross-checked against the official local start (ATP orders of play are published in local time).",
                      url=D.SOURCES["atp_sched_lyon"]["url"], severity="low"))
    for where, what, url in D.REPO_FINDINGS:
        flags.append(dict(code="REPO", ref=where, sport="Repository", label=where, detail=what, url=url, severity="low"))

    sports_all = ["Tennis", "Basketball", "Golf", "Cricket", "Snooker", "Rugby Union", "Rugby League", "Baseball", "Ice Hockey",
                  "Motor Racing", "Darts", "Handball", "Volleyball", "Aussie Rules", "eSports", "Gaelic Football", "Greyhounds"]
    coverage = []
    for s in sports_all:
        v = [f for f in fixtures if f["sport"] == s]
        u = [f for f in flags if f.get("sport") == s and f["code"] not in ("REPO", "CLOCK", "UNPRICED")]
        hub = {"Tennis": "olbg_tennis", "Basketball": "olbg_basketball", "Golf": "olbg_golf", "Cricket": "olbg_cricket", "Snooker": "olbg_snooker",
               "Rugby Union": "olbg_rugbyunion", "Rugby League": "olbg_rugbyleague", "Baseball": "olbg_baseball", "Ice Hockey": "olbg_icehockey",
               "Motor Racing": "olbg_motor", "Darts": "olbg_darts", "Handball": "olbg_handball", "Volleyball": "olbg_volleyball",
               "Aussie Rules": "olbg_aussie", "eSports": "olbg_esports", "Gaelic Football": "olbg_gaelic", "Greyhounds": "olbg_greyhounds"}[s]
        status = "verified+priced" if v and all(f["priced"] for f in v) else "partly priced" if v else ("hub empty" if u and all(f["code"] == "EMPTY" for f in u) else "harvested, unverified")
        coverage.append(dict(sport=s, olbg_hub=D.SOURCES[hub]["url"], verified_fixtures=len(v), priced=sum(1 for f in v if f["priced"]),
                             unverified_listings=len(u), status=status))
    return fixtures, markets, picks, preds, flags, coverage


# ------------------------------------------------------------------ site
CSS = """
:root{--bg:#0e1117;--panel:#161b22;--panel2:#1f2630;--line:#2b3440;--txt:#e6edf3;--dim:#9aa7b4;--hi:#3fb950;--md:#d29922;--lo:#8b949e;--acc:#58a6ff;--warn:#f85149}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--txt);font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--acc);text-decoration:none}a:hover{text-decoration:underline}
header{position:sticky;top:0;z-index:5;background:rgba(14,17,23,.97);border-bottom:1px solid var(--line)}
.wrap{max-width:1240px;margin:0 auto;padding:0 20px}header .wrap{display:flex;gap:16px;align-items:center;min-height:56px;flex-wrap:wrap}
.brand{font-weight:700}.brand span{color:var(--acc)}nav{display:flex;gap:14px;flex-wrap:wrap;font-size:13.5px}nav a{color:var(--dim)}nav a.on{color:var(--txt);font-weight:600}
main{padding:26px 0 50px}h1{font-size:26px;margin:0 0 6px}h2{font-size:19px;margin:30px 0 10px;padding-bottom:6px;border-bottom:1px solid var(--line)}
p.lede{color:var(--dim);max-width:900px;margin:0 0 16px}
.grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));margin:16px 0}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 14px}.card .k{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--dim)}.card .v{font-size:24px;font-weight:700}.card .s{font-size:12px;color:var(--dim)}
table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);font-size:13.5px;margin:8px 0}
th,td{padding:7px 9px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}th{background:var(--panel2);font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--dim)}
tbody tr:last-child td{border-bottom:none}td.n{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}
.b{display:inline-block;padding:1px 8px;border-radius:999px;font-size:11px;font-weight:700;text-transform:uppercase}
.High{background:rgba(63,185,80,.15);color:var(--hi)}.Medium{background:rgba(210,153,34,.15);color:var(--md)}.Low{background:rgba(139,148,158,.15);color:var(--lo)}
.ok{color:var(--hi)}.no{color:var(--warn)}.dim{color:var(--dim)}.mono{font-family:ui-monospace,Menlo,monospace;font-size:12.5px}
.note{background:var(--panel);border-left:3px solid var(--md);padding:10px 14px;margin:14px 0;color:var(--dim);font-size:13.5px}.warn{border-left-color:var(--warn)}
.prose{max-width:880px}.prose p{margin:8px 0}footer{border-top:1px solid var(--line);padding:16px 0 36px;color:var(--dim);font-size:12.5px}
ul.t{margin:6px 0 6px 18px;padding:0}ul.t li{margin:3px 0}
"""

NAV = [("index.html", "Overview"), ("picks.html", "Picks"), ("markets.html", "Markets"), ("predictions.html", "Predictions"),
       ("coverage.html", "Coverage"), ("flagged.html", "Flagged for Review"), ("sources.html", "Sources"), ("methodology.html", "Methodology")]
SPORT_PAGES = [("Tennis", "tennis"), ("Snooker", "snooker"), ("Basketball", "basketball"), ("Baseball", "baseball")]


def esc(x):
    return html.escape("" if x is None else str(x))


def page(title, body, active, depth=0):
    rr = "../" * depth
    nav = "".join(f'<a href="{rr}{h}" class="{"on" if h == active else ""}">{t}</a>' for h, t in NAV)
    nav += "".join(f'<a href="{rr}sports/{s}.html" class="{"on" if active == "sports/" + s + ".html" else ""}">{n}</a>' for n, s in SPORT_PAGES)
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} — OLBG desk 9dfd0b48</title><link rel="stylesheet" href="{rr}assets/style.css"></head><body>
<header><div class="wrap"><div class="brand">OLBG<span>1</span> · desk 9dfd0b48 · T44</div><nav>{nav}<a href="{rr}../index.html">Root site</a></nav></div></header>
<main><div class="wrap">{body}</div></main>
<footer><div class="wrap">Session {SESSION} · harvest {D.HARVEST_UTC} · all prices are independently originated model estimates, not quotes. Times UTC.</div></footer></body></html>"""


def link(url, text="source"):
    return f'<a href="{esc(url)}" rel="noopener">{esc(text)}</a>'


def t_fixtures(fixtures, picks):
    pk = {p["fixture"]: p for p in picks}
    rows = []
    for f in fixtures:
        p = pk.get(f["id"])
        pickcell = (esc(p['pick']) + ' <span class=mono>' + fmt(p['price']) + '</span> <span class="b ' + p['confidence'] + '">' + p['confidence'] + '</span>') if p else '<span class=no>blank — unpriced</span>'
        rows.append(f"<tr><td class=mono>{f['id']}</td><td>{esc(f['start'])}</td><td>{esc(f['comp'])}</td><td>{esc(f['a'])} v {esc(f['b'])}</td>"
                    f"<td>{pickcell}</td>"
                    f"<td>{esc(f.get('olbg_tips') or '')}{(' · ' + link(f['olbg'], 'OLBG')) if f.get('olbg') else ''}</td>"
                    f"<td>{' · '.join(link(s['url'], s['id']) for s in f['sources'])}</td></tr>")
    return ("<table><thead><tr><th>ID</th><th>Start (UTC)</th><th>Competition</th><th>Fixture</th><th>Pick · price · confidence</th><th>OLBG</th><th>Official source</th></tr></thead><tbody>"
            + "".join(rows) + "</tbody></table>")


def t_markets(markets, fixtures):
    fxm = {f["id"]: f for f in fixtures}
    rows = []
    for m in markets:
        f = fxm[m["fixture"]]
        rows.append(f"<tr><td class=mono>{m['fixture']}</td><td>{esc(f['a'])} v {esc(f['b'])}</td><td>{esc(m['market'])}</td>"
                    f"<td>{esc(m['sel_a'])}</td><td class=n>{m['p_a']*100:.1f}%</td><td class=n>{fmt(m['price_a'])}{'' if m['in_window_a'] else ' <span class=dim>(out)</span>'}</td>"
                    f"<td>{esc(m['sel_b'])}</td><td class=n>{m['p_b']*100:.1f}%</td><td class=n>{fmt(m['price_b'])}{'' if m['in_window_b'] else ' <span class=dim>(out)</span>'}</td>"
                    f"<td>{link(m['source'])}</td></tr>")
    return ("<table><thead><tr><th>ID</th><th>Fixture</th><th>Market</th><th>Side A</th><th>P</th><th>Price</th><th>Side B</th><th>P</th><th>Price</th><th>Source</th></tr></thead><tbody>"
            + "".join(rows) + "</tbody></table>")


def t_flags(flags):
    rows = []
    for f in flags:
        extra = ""
        if f.get("official_attempt"):
            extra = " · " + link(f["official_attempt"], "official attempt")
        rows.append(f"<tr><td class=mono>{esc(f['code'])}</td><td>{esc(f.get('sport'))}</td><td>{esc(f['label'])}{(' <span class=dim>' + esc(f.get('start')) + '</span>') if f.get('start') else ''}</td>"
                    f"<td>{esc(f['detail'])}{(' <span class=dim>OLBG consensus: ' + esc(f['olbg_tips']) + '</span>') if f.get('olbg_tips') else ''}</td>"
                    f"<td>{esc(f['severity'])}</td><td>{link(f['url'], 'link')}{extra}</td></tr>")
    return "<table><thead><tr><th>Code</th><th>Sport</th><th>Item</th><th>Detail</th><th>Severity</th><th>Source</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>"


def write_site(fixtures, markets, picks, preds, flags, coverage):
    os.makedirs(os.path.join(SITE, "assets"), exist_ok=True)
    os.makedirs(os.path.join(SITE, "sports"), exist_ok=True)
    with open(os.path.join(SITE, "assets", "style.css"), "w") as fh:
        fh.write(CSS)
    n_high = sum(1 for p in picks if p["confidence"] == "High")
    n_unv = sum(1 for f in flags if f["code"] not in ("REPO", "CLOCK", "UNPRICED"))
    cards = f"""<div class=grid>
<div class=card><div class=k>Verified fixtures</div><div class=v>{len(fixtures)}</div><div class=s>{sum(1 for f in fixtures if f['priced'])} priced · {len(fixtures) - sum(1 for f in fixtures if f['priced'])} blank</div></div>
<div class=card><div class=k>Originated selections</div><div class=v>{len(markets) * 2}</div><div class=s>{len(markets)} two-way markets</div></div>
<div class=card><div class=k>Picks</div><div class=v>{len(picks)}</div><div class=s>{n_high} High · {sum(1 for p in picks if p['confidence'] == 'Medium')} Medium · {sum(1 for p in picks if p['confidence'] == 'Low')} Low</div></div>
<div class=card><div class=k>Flagged</div><div class=v>{len(flags)}</div><div class=s>{n_unv} unverified OLBG listings</div></div>
<div class=card><div class=k>Sports covered</div><div class=v>{sum(1 for c in coverage if c['verified_fixtures'])}/17</div><div class=s>hubs harvested 17/17</div></div></div>"""
    intro = f"""<h1>Matchday desk — 22–24 October 2026</h1>
<p class=lede>Session {SESSION} (task {TASK}). Every one of OLBG's 17 in-scope sport hubs was harvested at {D.HARVEST_UTC}; fixtures were then re-read from the governing body
(ATP Tour, World Snooker Tour, EuroLeague, MLB Stats API) before any line was originated. Where the official page could not be read, the row is left blank and sent to
<a href="flagged.html">Flagged for Review</a>. Prices are our own estimates with a {VIG*100:.1f}% overround; High picks are written up only when the featured price sits between -250 and +10000.</p>"""
    high = "".join(f"<li><b>{esc(p['label'])}</b> — {esc(p['featured']['selection'])} ({esc(p['featured']['market'])}) <span class=mono>{fmt(p['featured']['price'])}</span> · {link(p['source'], 'official')}</li>"
                   for p in picks if p["confidence"] == "High")
    body = intro + cards + "<h2>High-confidence board</h2><ul class=t>" + (high or "<li>none</li>") + "</ul><h2>All verified fixtures</h2>" + t_fixtures(fixtures, picks)
    body += "<h2>Coverage by sport</h2>" + t_coverage(coverage)
    open(os.path.join(SITE, "index.html"), "w").write(page("Overview", body, "index.html"))

    body = "<h1>Picks</h1><p class=lede>One match pick per priced fixture. Confidence is the model probability of the pick (High ≥70%, Medium ≥58%). The featured selection moves to the handicap when the money line is shorter than -250.</p>"
    rows = "".join(f"<tr><td class=mono>{p['fixture']}</td><td>{esc(p['start'])}</td><td>{esc(p['sport'])}</td><td>{esc(p['label'])}</td><td>{esc(p['pick'])}</td><td class=n>{p['p']*100:.1f}%</td>"
                   f"<td class=n>{fmt(p['price'])}{'' if p['in_window'] else ' <span class=dim>(out)</span>'}</td><td><span class=\"b {p['confidence']}\">{p['confidence']}</span></td>"
                   f"<td>{esc(p['featured']['selection'])} · {esc(p['featured']['market'])} <span class=mono>{fmt(p['featured']['price'])}</span></td>"
                   f"<td>{esc(p.get('olbg_tips') or '')}{(' · ' + link(p['olbg'], 'OLBG')) if p.get('olbg') else ''}</td><td>{link(p['source'])}</td></tr>" for p in picks)
    body += "<table><thead><tr><th>ID</th><th>Start</th><th>Sport</th><th>Fixture</th><th>Pick</th><th>P</th><th>Price</th><th>Conf.</th><th>Featured</th><th>OLBG</th><th>Source</th></tr></thead><tbody>" + rows + "</tbody></table>"
    open(os.path.join(SITE, "picks.html"), "w").write(page("Picks", body, "picks.html"))

    body = "<h1>Markets</h1><p class=lede>Winner, handicap and total for every priced fixture. '(out)' marks a price outside the -250/+10000 window.</p>" + t_markets(markets, fixtures)
    open(os.path.join(SITE, "markets.html"), "w").write(page("Markets", body, "markets.html"))

    body = "<h1>Predictions</h1><p class=lede>Written for every High pick; each uses only facts read from the cited official pages and names the selection outright.</p>"
    for p in preds:
        body += (f"<div class=prose><h2>{esc(p['label'])} — {esc(p['selection'])}</h2><p>{esc(p['text'])}</p>"
                 f"<p class=dim>{p['words']} words · featured: {esc(p['featured']['market'])} {esc(p['featured']['selection'])} <span class=mono>{fmt(p['featured']['price'])}</span> · "
                 + " · ".join(link(u, "source") for u in p["sources"]) + "</p></div>")
    body += "<h2>Summary table</h2><table><thead><tr><th>Fixture</th><th>Selection</th><th>Words</th><th>Source</th></tr></thead><tbody>" + "".join(
        f"<tr><td>{esc(p['label'])}</td><td>{esc(p['selection'])}</td><td class=n>{p['words']}</td><td>{link(p['sources'][0])}</td></tr>" for p in preds) + "</tbody></table>"
    open(os.path.join(SITE, "predictions.html"), "w").write(page("Predictions", body, "predictions.html"))

    body = "<h1>Coverage</h1><p class=lede>All 17 in-scope OLBG sports. 'Harvested, unverified' means the OLBG listing exists but no official page was read this session — those rows are on the flag page without prices.</p>" + t_coverage(coverage)
    open(os.path.join(SITE, "coverage.html"), "w").write(page("Coverage", body, "coverage.html"))

    body = f"<h1>Flagged for Review</h1><p class=lede>{len(flags)} items: unverified OLBG listings (blank, no price), unpriced verified fixtures, clock conversions and repository findings. None of these block publication; all are disclosed.</p>" + t_flags(flags)
    open(os.path.join(SITE, "flagged.html"), "w").write(page("Flagged for Review", body, "flagged.html"))

    rows = "".join(f"<tr><td class=mono>{esc(k)}</td><td>{esc(v['title'])}</td><td>{esc(v['fetched'])}</td><td>{link(v['url'], v['url'][:70])}</td></tr>" for k, v in D.SOURCES.items())
    body = "<h1>Sources</h1><p class=lede>Every page read this session, with the UTC fetch time. OLBG hubs are discovery sources only; they never verify a sporting fact here.</p><table><thead><tr><th>ID</th><th>Page</th><th>Fetched</th><th>URL</th></tr></thead><tbody>" + rows + "</tbody></table>"
    open(os.path.join(SITE, "sources.html"), "w").write(page("Sources", body, "sources.html"))

    body = """<h1>Methodology</h1><div class=prose>
<p><b>Harvest.</b> The 17 in-scope OLBG hubs were read in one pass (see Sources). Event IDs, listed times and the visible tip consensus were recorded verbatim. OLBG times render in US Eastern (UTC-4) without a label; every conversion was cross-checked against an official local start time.</p>
<p><b>Verification.</b> A fixture is published only if the pairing and start were read from the governing body's own page: ATP orders of play, the WST match list, the EuroLeague Game Center and the MLB Stats API. Anything else is blank and flagged.</p>
<p><b>Tennis.</b> P(A) = 1 / (1 + (ptsB/ptsA)^0.55) from the 19 Oct ATP list. Game handicap steps with the favourite's probability (1.5 → 5.5); total games 22.5 leans under as the match gets more lopsided. No surface, injury or head-to-head adjustment is made because none was read from an official source.</p>
<p><b>Snooker.</b> Same power-ratio form on official ranking money (exponent 0.45). Players outside the 36-name list are priced at the 36th-place ceiling, so the favourite's probability is a lower bound. Where neither player is on the list the market opens even and the pick is Low.</p>
<p><b>EuroLeague.</b> Margin = 0.6 × (home point differential per game − away differential per game) + 3.0 home edge; win probability from a normal with σ 11.5; spread rounded to the half point; total from the two teams' average combined scoring.</p>
<p><b>MLB.</b> Pythagorean win rate (exponent 1.83) from 2026 regular-season runs, combined by log5, plus 3.5 points for the home side; run line at −19 points; total 8.5 leaning with combined runs per game.</p>
<p><b>Prices.</b> American odds with a 4.5% overround split across both sides. Confidence: High ≥70%, Medium ≥58%, otherwise Low. If a High pick's money line is shorter than −250 the featured selection moves to the handicap so that every written-up play sits inside the −250/+10000 window.</p>
<p><b>Limits.</b> This is a model, not a market. Prices are estimates for comparison, not quotes. See <a href="flagged.html">Flagged for Review</a> for everything that could not be verified.</p></div>"""
    open(os.path.join(SITE, "methodology.html"), "w").write(page("Methodology", body, "methodology.html"))

    for name, slug in SPORT_PAGES:
        fx = [f for f in fixtures if f["sport"] == name]
        mk = [m for m in markets if m["fixture"] in {f["id"] for f in fx}]
        pr = [p for p in preds if p["sport"] == name]
        fl = [f for f in flags if f.get("sport") == name and f["code"] not in ("REPO",)]
        body = f"<h1>{esc(name)}</h1><p class=lede>{len(fx)} verified fixtures · {len(mk)} markets · {len(fl)} flagged items.</p><h2>Fixtures and picks</h2>" + t_fixtures(fx, picks)
        body += "<h2>Model inputs</h2><table><thead><tr><th>ID</th><th>Inputs (verified)</th><th>Source</th></tr></thead><tbody>" + "".join(
            f"<tr><td class=mono>{f['id']}</td><td>{esc(f['inputs'])}<br><span class=dim>{esc(f['note'])}</span></td><td>{' · '.join(link(s['url'], s['id']) for s in f['sources'])}</td></tr>" for f in fx) + "</tbody></table>"
        body += "<h2>Markets</h2>" + t_markets(mk, fixtures)
        if pr:
            body += "<h2>Predictions</h2>" + "".join(f"<div class=prose><h3>{esc(p['label'])} — {esc(p['selection'])}</h3><p>{esc(p['text'])}</p><p class=dim>{' · '.join(link(u, 'source') for u in p['sources'])}</p></div>" for p in pr)
        if fl:
            body += "<h2>Flagged</h2>" + t_flags(fl)
        open(os.path.join(SITE, "sports", f"{slug}.html"), "w").write(page(name, body, f"sports/{slug}.html", depth=1))


def t_coverage(coverage):
    sp = dict((n, s) for n, s in SPORT_PAGES)
    def sl(c):
        return (' · <a href="sports/' + sp[c['sport']] + '.html">page</a>') if c['sport'] in sp else ''
    rows = "".join(f"<tr><td>{esc(c['sport'])}{sl(c)}</td><td class=n>{c['verified_fixtures']}</td><td class=n>{c['priced']}</td><td class=n>{c['unverified_listings']}</td><td>{esc(c['status'])}</td><td>{link(c['olbg_hub'], 'OLBG hub')}</td></tr>" for c in coverage)
    return "<table><thead><tr><th>Sport</th><th>Verified</th><th>Priced</th><th>Unverified listings</th><th>Status</th><th>Hub</th></tr></thead><tbody>" + rows + "</tbody></table>"


def main():
    fixtures, markets, picks, preds, flags, coverage = build()
    os.makedirs(DATA, exist_ok=True)
    meta = dict(session=SESSION, task=TASK, harvest_utc=D.HARVEST_UTC, generator="scripts/s9dfd0b48_build.py")
    for name, obj in (("fixtures", fixtures), ("markets", markets), ("picks", picks), ("predictions", preds), ("flags", flags), ("coverage", coverage)):
        json.dump(dict(meta, count=len(obj), items=obj), open(os.path.join(DATA, f"{name}.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(dict(meta, items=D.SOURCES), open(os.path.join(DATA, "sources.json"), "w"), indent=1)
    with open(os.path.join(DATA, "matches.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "sport", "competition", "start_utc", "a", "b", "pick", "p", "price", "confidence", "official_source", "olbg_url"])
        pk = {p["fixture"]: p for p in picks}
        for f in fixtures:
            p = pk.get(f["id"], {})
            w.writerow([f["id"], f["sport"], f["comp"], f["start"], f["a"], f["b"], p.get("pick", ""), p.get("p", ""), fmt(p.get("price")), p.get("confidence", ""), f["sources"][0]["url"], f.get("olbg") or ""])
    write_site(fixtures, markets, picks, preds, flags, coverage)
    print(f"fixtures {len(fixtures)} (priced {sum(1 for f in fixtures if f['priced'])}) markets {len(markets)} picks {len(picks)} "
          f"high {sum(1 for p in picks if p['confidence']=='High')} preds {len(preds)} flags {len(flags)}")
    for p in picks:
        print(f"  {p['fixture']} {p['label'][:42]:42} {p['pick'][:28]:28} {p['p']*100:5.1f}% {fmt(p['price']):>6} {p['confidence']}")


if __name__ == "__main__":
    main()
