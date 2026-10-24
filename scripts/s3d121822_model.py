"""Pricing, confidence gating and static site generation for desk 3d121822.

Run:  python3 scripts/s3d121822_build.py
Out:  3d121822/**, data/3d121822/**

Money is never invented: a fixture is priced only when both participants have
a sourced record in s3d121822_data.  Everything else is published blank with a
named missing input.
"""
from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

import s3d121822_data as D

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "3d121822"
DATA = ROOT / "data" / "3d121822"

PRIOR = 2.0            # Beta(2,2) shrinkage on every win rate
NBA_SIGMA = 12.5       # points, documented assumption for the spread family
NHL_SIGMA = 2.0        # goals, documented assumption for the puck line family
HIGH_FLOOR = 0.70      # brief: >70% chance
BAND_FLOOR = 1 / 3.5   # -250 == 1/(1+250/100) == 0.714285...
PICK_FLOOR = 0.55      # below this we publish "no selection"
BAND_TOP = 1 / 10001   # +10000


# ---------------------------------------------------------------- maths
def shrunk_rate(wins: float, losses: float) -> float:
    return (wins + PRIOR) / (wins + losses + 2 * PRIOR)


def log5(pa: float, pb: float) -> float:
    num = pa * (1 - pb)
    return num / (num + (1 - pa) * pb)


def american(p: float) -> str:
    if p <= 0 or p >= 1:
        return ""
    return f"-{round(100 * p / (1 - p))}" if p >= 0.5 else f"+{round(100 * (1 - p) / p)}"


def decimal(p: float) -> float:
    return round(1 / p, 3)


def phi(z: float) -> float:
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def inv_phi(p: float) -> float:
    lo, hi = -8.0, 8.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if phi(mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def confidence(p: float) -> tuple[str, str]:
    """Return (label, reason)."""
    if HIGH_FLOOR <= p <= BAND_FLOOR:
        return "High", "at or above the 70% floor and inside the -250 band"
    if p > BAND_FLOOR:
        return "Medium", "stronger than -250, so outside the stated price window"
    if p >= PICK_FLOOR:
        return "Medium", "between 55% and 70% fair"
    if p >= 0.5:
        return "Low", "only a marginal edge"
    return "Low", "below even money"


# ---------------------------------------------------------------- pricing
def nba_prices(fx: dict) -> dict | None:
    a, b = fx["a"], fx["b"]
    if a not in D.NBA or b not in D.NBA:
        return None
    aw, al = D.NBA[a][0], D.NBA[a][1]
    hw, hl = D.NBA[b][0], D.NBA[b][1]
    pa, ph = shrunk_rate(aw, al), shrunk_rate(hw, hl)
    p_home = log5(ph, pa)
    spread = -round(inv_phi(min(max(p_home, 0.05), 0.95)) * NBA_SIGMA * 2) / 2
    return dict(kind="nba", p_home=p_home, p_away=1 - p_home, sigma=NBA_SIGMA,
                spread=spread, rec_away=D.NBA[a], rec_home=D.NBA[b],
                label_away="Money Line", label_home="Money Line",
                spread_label="Pointspread")


def nhl_prices(fx: dict) -> dict | None:
    a, b = fx["a"], fx["b"]
    if a not in D.NHL or b not in D.NHL:
        return None
    aw, al, ao = D.NHL[a]
    hw, hl, ho = D.NHL[b]
    pa = shrunk_rate(2 * aw + ao, 2 * al + 0)
    ph = shrunk_rate(2 * hw + ho, 2 * hl + 0)
    p_home = log5(ph, pa)
    spread = -round(inv_phi(min(max(p_home, 0.05), 0.95)) * NHL_SIGMA * 2) / 2
    return dict(kind="nhl", p_home=p_home, p_away=1 - p_home, sigma=NHL_SIGMA,
                spread=spread, rec_away=D.NHL[a], rec_home=D.NHL[b],
                label_away="Money Line", label_home="Money Line",
                spread_label="Puck Line")


def build_prices() -> dict:
    prices = {}
    for fx in D.fixture_rows():
        calc = nba_prices(fx) if fx["sport"] == "basketball" else (
            nhl_prices(fx) if fx["sport"] == "ice_hockey" else None)
        if not calc:
            continue
        p_home = calc["p_home"]
        # pick the side that clears the floor, if either does
        side, p_pick = None, 0.0
        if p_home >= PICK_FLOOR:
            side, p_pick = fx["b"], p_home
        elif (1 - p_home) >= PICK_FLOOR:
            side, p_pick = fx["a"], 1 - p_home
        written = fx["id"] in D.PREDICTIONS
        conf, reason = confidence(p_pick) if side else ("", "")
        prices[fx["id"]] = dict(
            calc=calc, p_home=p_home, p_away=1 - p_home,
            side=side if written else None, p_pick=p_pick,
            conf=conf if (side and written) else "",
            conf_reason=reason,
            selection=(f"{side} to win" if side else ""),
            decimal=(decimal(p_pick) if side else None),
            american=(american(p_pick) if side else ""),
            in_band=(BAND_TOP <= p_pick <= BAND_FLOOR) if side else None,
            spread_prob=phi((calc["spread"] * -1 - (-inv_phi(p_home) * calc["sigma"])) / calc["sigma"]),
            written=written,
            has_side=bool(side),
        )
    return prices


def market_rows(fx: dict, price: dict) -> list[dict]:
    calc = price["calc"]
    p_home, p_away = price["p_home"], price["p_away"]
    rec_a, rec_b = calc["rec_away"], calc["rec_home"]
    rows = [
        dict(market="Money Line", selection=fx["a"], price=decimal(p_away),
             american=american(p_away), prob=p_away, basis=f"record {rec_a[0]}-{rec_a[1]}" +
             (f"-{rec_a[2]}" if len(rec_a) > 2 else "")),
        dict(market="Money Line", selection=fx["b"], price=decimal(p_home),
             american=american(p_home), prob=p_home, basis=f"record {rec_b[0]}-{rec_b[1]}" +
             (f"-{rec_b[2]}" if len(rec_b) > 2 else "")),
    ]
    line = calc["spread"]
    p_away_spread = 1 - phi((line - (-inv_phi(p_home) * calc["sigma"])) / calc["sigma"])
    rows.append(dict(market=calc["spread_label"], selection=f"{fx['a']} {line:+.1f}",
                     price=decimal(p_away_spread), american=american(p_away_spread),
                     prob=p_away_spread, basis="margin family, sigma " + str(calc["sigma"])))
    rows.append(dict(market=calc["spread_label"], selection=f"{fx['b']} {-line:+.1f}",
                     price=decimal(1 - p_away_spread), american=american(1 - p_away_spread),
                     prob=1 - p_away_spread, basis="margin family, sigma " + str(calc["sigma"])))
    return rows


# ---------------------------------------------------------------- html
CSS = """
:root{--ink:#10241c;--muted:#5c6f66;--line:#e3e9e5;--bg:#f5f7f6;--card:#fff;
--accent:#0f5132;--accent-soft:#e7f1ec;--amber:#8a5a00;--amber-soft:#fdf3e0;--red:#9c2b32;--red-soft:#fbeaeb}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--accent)}
.wrap{max-width:1120px;margin:0 auto;padding:0 20px}
header.top{background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:5}
.top .wrap{display:flex;align-items:center;gap:16px;min-height:64px;flex-wrap:wrap}
.brand{font-weight:700;letter-spacing:-.02em;text-decoration:none;color:var(--ink);font-size:17px}
.brand span{color:var(--muted);font-weight:500}
.top .meta{margin-left:auto;font-size:13px;color:var(--muted);display:flex;gap:14px;flex-wrap:wrap}
nav.tabs{background:#fff;border-bottom:1px solid var(--line)}
nav.tabs .wrap{display:flex;gap:4px;overflow-x:auto}
nav.tabs a{padding:12px 14px;text-decoration:none;color:var(--muted);font-size:14px;font-weight:600;border-bottom:2px solid transparent;white-space:nowrap}
nav.tabs a:hover{color:var(--accent)}
nav.tabs a[aria-current=page]{color:var(--accent);border-bottom-color:var(--accent)}
main{padding:28px 0 60px}
h1{font-size:34px;line-height:1.15;letter-spacing:-.025em;margin:0 0 10px}
h2{font-size:21px;letter-spacing:-.01em;margin:34px 0 12px}
h3{font-size:16px;margin:22px 0 8px}
p.lede{font-size:17px;color:var(--muted);margin:0 0 22px;max-width:72ch}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px 22px}
.card+.card{margin-top:14px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:20px 0 26px}
.kpi{background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.kpi b{display:block;font-size:24px;letter-spacing:-.02em}
.kpi small{color:var(--muted);font-size:12.5px;text-transform:uppercase;letter-spacing:.06em}
.picks{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px}
.pick{background:#fff;border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:12px;padding:16px 18px}
.pick .where{font-size:12.5px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}
.pick .sel{font-size:19px;font-weight:700;letter-spacing:-.01em;margin:6px 0 4px}
.pick .mkt{font-size:13.5px;color:var(--muted)}
.pick .foot{display:flex;align-items:center;gap:10px;margin-top:12px;flex-wrap:wrap;font-size:13.5px}
.pick .price{font-variant-numeric:tabular-nums;font-weight:600}
.chip{display:inline-block;padding:2px 9px;border-radius:999px;font-size:12px;font-weight:700;letter-spacing:.02em}
.chip.high{background:#e6f4ec;color:#0b6b3a}
.chip.med{background:var(--amber-soft);color:var(--amber)}
.chip.low{background:#eef1f0;color:#54635c}
.chip.none{background:var(--red-soft);color:var(--red)}
table{width:100%;border-collapse:collapse;background:#fff;border:1px solid var(--line);border-radius:12px;overflow:hidden;font-size:14px}
th,td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}
th{background:#fafbfa;font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted)}
tbody tr:last-child td{border-bottom:0}
tbody tr:hover{background:#fcfdfc}
td.num{font-variant-numeric:tabular-nums;white-space:nowrap}
.pickcell b{display:block;font-size:14.5px}
.pickcell small{color:var(--muted)}
.muted{color:var(--muted)}
.small{font-size:13px}
.note{background:var(--accent-soft);border:1px solid #cfe3d8;border-radius:12px;padding:14px 18px;margin:18px 0;font-size:14.5px}
.warn{background:var(--amber-soft);border:1px solid #f0dcaf;border-radius:12px;padding:14px 18px;margin:18px 0;font-size:14.5px}
.blank{color:#9aa7a1;font-style:italic}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px}
@media(max-width:820px){.grid2{grid-template-columns:1fr}h1{font-size:27px}table{font-size:13px}th,td{padding:8px 9px}}
.badge{display:inline-block;background:#fff;border:1px solid var(--line);border-radius:999px;padding:3px 10px;font-size:12px;color:var(--muted)}
ul.tight{margin:8px 0;padding-left:20px}
ul.tight li{margin:4px 0}
.prose{max-width:78ch}
.prose p{margin:0 0 12px}
.pred{background:#fff;border:1px solid var(--line);border-radius:14px;padding:20px 22px}
.pred+.pred{margin-top:14px}
.pred h3{margin:0 0 4px;font-size:17px}
.pred .sel{color:var(--accent);font-weight:700}
.pred .body{font-size:15.5px}
.pred .src{font-size:13px;color:var(--muted);margin-top:12px;border-top:1px dashed var(--line);padding-top:10px}
footer{border-top:1px solid var(--line);background:#fff;padding:22px 0;color:var(--muted);font-size:13px}
footer .wrap{display:flex;gap:18px;flex-wrap:wrap;justify-content:space-between}
.skip{position:absolute;left:-999px}
"""

NAV = [("index.html", "Overview"), ("picks.html", "Picks"), ("matches.html", "Matches"),
       ("predictions.html", "Written predictions"), ("markets.html", "Markets"),
       ("sports/index.html", "Sports"), ("flagged.html", "Flagged for review"),
       ("sources.html", "Sources"), ("method.html", "Method"),
       ("repo-review.html", "Repo review")]


def esc(v) -> str:
    return (str(v).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def src_link(sid: str) -> str:
    url, pub, _what, _at = D.SOURCES[sid]
    return f'<a href="{esc(url)}" rel="noopener">{esc(pub)}</a>'


def page(title: str, body: str, current: str, prefix: str = "", lede: str = "") -> str:
    nav = "".join(
        f'<a href="{prefix}{href}"{" aria-current=page" if href == current else ""}>{esc(label)}</a>'
        for href, label in NAV)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · OLBG research desk · 24 Oct 2026</title>
<meta name="description" content="Independent, source-linked match research for 24 October 2026. Not affiliated with OLBG.">
<link rel="stylesheet" href="{prefix}assets/desk.css">
</head><body>
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap">
  <a class="brand" href="{prefix}index.html">OLBG research desk <span>· 24 October 2026</span></a>
  <div class="meta"><span>Independent · not affiliated with OLBG</span><span>Data read 17:05–17:12 UTC</span></div>
</div></header>
<nav class="tabs"><div class="wrap">{nav}</div></nav>
<main id="main"><div class="wrap">
{body}
</div></main>
<footer><div class="wrap">
  <span>Every row links an official source. Blank means not confirmed — never guessed.</span>
  <span>18+ · Research, not betting advice. No returns are promised.</span>
</div></footer>
</body></html>"""


def conf_chip(label: str) -> str:
    if not label:
        return '<span class="chip none">No pick</span>'
    cls = {"High": "high", "Medium": "med", "Low": "low"}[label]
    return f'<span class="chip {cls}">{label}</span>'


def kickoff(fx) -> str:
    out = esc(fx["ko"])
    if fx.get("utc"):
        out += f'<br><span class="small muted">{esc(fx["utc"])} official</span>'
    else:
        out += '<br><span class="small muted">clock as shown by OLBG</span>'
    return out


def decimal_text(p: float) -> str:
    return f"{p:.2f}"
