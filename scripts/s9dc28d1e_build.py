"""Build the 9dc28d1e desk: data exports plus the static site.

Deterministic: run with --now to pin the generated-at stamp.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
from pathlib import Path

import s9dc28d1e_inputs as I
import s9dc28d1e_model as M
import s9dc28d1e_prose as P

SID = "9dc28d1e"
ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / SID
DATA = ROOT / "data" / SID

WINDOW_START = "2026-10-22T12:11:00Z"
WINDOW_END = "2026-10-25T12:11:00Z"

SPORT_SLUG = {name: slug for slug, name, _rid in I.SPORTS}


def esc(text) -> str:
    return html.escape(str(text), quote=True)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def build_fixtures():
    fixtures = []

    for gid, home, away, start, venue in I.NHL_GAMES:
        fixtures.append(dict(
            id=f"nhl-{gid}", sport="Ice Hockey", sport_slug="ice-hockey",
            competition="NHL", home=home, away=away, start_utc=start, venue=venue,
            status="verified", source_ids=["nhl-schedule", "nhl-standings"],
            note="Participants, home designation and start time read from the NHL schedule feed; "
                 "team rates read from the NHL team summary." if venue else
                 "Participants, home designation and start time read from the NHL schedule feed; "
                 "venue not visible in the rows that were read, so it is left blank.",
        ))

    for gid, home, away, start, venue in I.EL_GAMES:
        fixtures.append(dict(
            id=f"el-{gid}", sport="Basketball", sport_slug="basketball",
            competition="EuroLeague", home=home, away=away, start_utc=start, venue=venue,
            status="verified-time-inherited", source_ids=["el-standings", "el-round7"],
            note="Club records, points for and points against read at 12:08Z. The standings feed "
                 "carries no schedule, so the tip-off time is inherited from the 07:17Z canonical "
                 "observation of the round 7 game centre and is flagged (F-9DC-04).",
        ))

    for gid, home, away, official, start, venue, pitcher in I.MLB_GAMES:
        fixtures.append(dict(
            id=f"mlb-{gid}", sport="Baseball", sport_slug="baseball",
            competition="MLB World Series", home=home, away=away, start_utc=start, venue=venue,
            status="verified", source_ids=["mlb-schedule", "mlb-standings"],
            note=("Probable pitcher announced by the home club: " + pitcher + ".") if pitcher
            else "No probable pitcher had been announced for either club at the time of the read.",
        ))

    # later World Series games: listed, outside the 72-hour window, unpriced
    for gid, date, start, venue, home_side in (
        (849804, "2026-10-26", "2026-10-27T00:00:00Z", "Tropicana Field", False),
        (849803, "2026-10-27", "2026-10-28T00:00:00Z", "Tropicana Field", False),
        (849799, "2026-10-28", "2026-10-29T00:00:00Z", "Tropicana Field", False),
        (849801, "2026-10-30", "2026-10-31T00:00:00Z", "American Family Field", True),
    ):
        fixtures.append(dict(
            id=f"mlb-{gid}", sport="Baseball", sport_slug="baseball",
            competition="MLB World Series",
            home="Milwaukee Brewers" if home_side else "Tampa Bay Rays",
            away="Tampa Bay Rays" if home_side else "Milwaukee Brewers",
            start_utc=start, venue=venue, status="listed-outside-window",
            source_ids=["mlb-schedule"], note="Scheduled but outside the 72-hour pricing window; published unpriced.",
        ))

    return fixtures


def inherited_fixtures(priced_ids):
    """Canonical listings for sports this session did not re-read. Prices stay blank."""
    path = ROOT / "data" / "current" / "matches.csv"
    if not path.exists():
        return []
    out = []
    with path.open(encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            slug = row["sport"].strip()
            if slug in ("ice-hockey", "basketball", "baseball"):
                continue
            out.append(dict(
                id=row["id"], sport=row.get("sport", ""), sport_slug=slug,
                competition=row.get("competition", ""),
                home=row.get("participant_a", ""), away=row.get("participant_b", ""),
                start_utc=row.get("start_utc", ""), venue=row.get("venue", ""),
                status="inherited-unverified", source_ids=[],
                external_url=(row.get("official_urls") or "").split("|")[0],
                note="Carried from the 07:17Z canonical observation window. Not re-read this session; "
                     "prices withheld and the row is marked unverified.",
            ))
    return out


# ---------------------------------------------------------------------------
# Markets and outcomes
# ---------------------------------------------------------------------------

def price_rows(sport_slug, fixture):
    if sport_slug == "ice-hockey":
        return list(M.nhl_selections(fixture["home"], fixture["away"]))
    if sport_slug == "basketball":
        return list(M.el_selections(fixture["home"], fixture["away"]))
    if sport_slug == "baseball":
        return list(M.mlb_selections(fixture["home"], fixture["away"]))
    return []


SETTLEMENT = {
    "winner": "Full game including overtime, shootout or extra innings.",
    "handicap": "Full game including overtime or extra innings; the handicap is applied to the final margin.",
    "total": "Full game, both clubs combined.",
    "team-total": "That club's goals or runs only, full game.",
}


def build_markets(fixtures, predictions):
    markets, outcomes = [], []
    high_keys = {(p["fixture_id"], p["selection"]) for p in predictions}
    for fx in fixtures:
        rows = price_rows(fx["sport_slug"], fx)
        if not rows:
            continue
        by_market = {}
        for key, market_label, selection, prob in rows:
            mk = (key, market_label)
            by_market.setdefault(mk, []).append((selection, prob))
        for (key, market_label), sels in by_market.items():
            mid = f"{fx['id']}::{abs(hash((key, market_label))) % 100000:05d}"
            mid = f"{fx['id']}::{key}::{market_label}".lower().replace(" ", "-").replace(".", "_")
            markets.append(dict(id=mid, fixture_id=fx["id"], key=key, label=market_label,
                                settlement=SETTLEMENT[key], outcomes=len(sels)))
            for selection, prob in sels:
                prob = round(prob, 6)
                dec = M.decimal_from_probability(prob)
                am = M.american_from_probability(prob)
                oid = f"{mid}::{selection}".lower().replace(" ", "-").replace(".", "_")
                tier, reason = M.tier_for(prob, am, (fx["id"], selection) in high_keys)
                low, high = M.sensitivity(fx["sport_slug"], fx["home"], fx["away"], key, selection)
                if fx["status"] != "verified" and fx["status"] != "verified-time-inherited":
                    tier, reason = "UNPRICED", "outside the pricing window"
                outcomes.append(dict(
                    id=oid, market_id=mid, fixture_id=fx["id"], selection=selection,
                    probability=prob, fair_decimal=dec, american=am, tier=tier, reason=reason,
                    sensitivity_low=round(low, 6), sensitivity_high=round(high, 6),
                ))
    return markets, outcomes


# ---------------------------------------------------------------------------
# Data export
# ---------------------------------------------------------------------------

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(now: str):
    fixtures = build_fixtures()
    priced_ids = {f["id"] for f in fixtures}
    fixtures += inherited_fixtures(priced_ids)

    predictions = [dict(p) for p in P.PREDICTIONS]
    markets, outcomes = build_markets([f for f in fixtures if f["status"].startswith("verified")], predictions)

    lookup = {(o["fixture_id"], o["selection"]): o for o in outcomes}
    for p in predictions:
        o = lookup.get((p["fixture_id"], p["selection"]))
        if o is None:
            raise SystemExit(f"prediction does not match a priced selection: {p['fixture_id']} / {p['selection']}")
        if o["tier"] != "HIGH":
            raise SystemExit(f"prediction is not a High selection: {p['selection']} ({o['tier']})")
        p["outcome_id"] = o["id"]
        p["probability"] = o["probability"]
        p["american"] = o["american"]
        p["tier"] = o["tier"]
        p["sensitivity_low"] = o["sensitivity_low"]
        p["sensitivity_high"] = o["sensitivity_high"]

    counts = dict(
        fixtures=len(fixtures),
        priced_matches=sum(1 for f in fixtures if f["status"].startswith("verified")),
        listed_unpriced=sum(1 for f in fixtures if not f["status"].startswith("verified")),
        inherited=sum(1 for f in fixtures if f["status"] == "inherited-unverified"),
        markets=len(markets),
        outcomes=len(outcomes),
        high=sum(1 for o in outcomes if o["tier"] == "HIGH"),
        medium=sum(1 for o in outcomes if o["tier"] == "MEDIUM"),
        low=sum(1 for o in outcomes if o["tier"] == "LOW"),
        above_window=sum(1 for o in outcomes if o["tier"] == "MEDIUM" and o["probability"] > M.HIGH_PROB_FLOOR
                         and not M.in_price_window(o["american"])),
        predictions=len(predictions),
        findings=len(P.FINDINGS),
        sports=len(I.SPORTS),
    )

    desk = dict(
        session=SID,
        generated_at=now,
        window=dict(start=WINDOW_START, end=WINDOW_END),
        observed_at=I.OBSERVED_AT,
        model=dict(
            nhl=f"Poisson goals, shrinkage k={M.NHL_K}, home multiplier {M.NHL_HOME}",
            euroleague=f"Normal margin, shrinkage k={M.EL_K}, rating weight {M.EL_DIFF_WEIGHT}, home edge {M.EL_HOME_EDGE}",
            mlb=f"Pythagorean exponent {M.MLB_PYTH} with log5 and home adjustment",
        ),
        gate=dict(probability_floor=M.HIGH_PROB_FLOOR, short_edge=M.PRICE_SHORT_EDGE,
                  long_edge=M.PRICE_LONG_EDGE),
        counts=counts,
        sources=I.SOURCES,
        fixtures=fixtures,
        markets=markets,
        outcomes=outcomes,
        predictions=predictions,
        findings=P.FINDINGS,
        sports=[dict(slug=s, name=n, route_id=r) for s, n, r in I.SPORTS],
    )

    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "desk.json").write_text(json.dumps(desk, indent=1, sort_keys=False) + "\n")

    with (DATA / "priced.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["fixture_id", "sport", "competition", "home", "away", "start_utc",
                    "market", "selection", "probability", "fair_decimal", "american", "tier"])
        fmap = {f["id"]: f for f in fixtures}
        for o in outcomes:
            f = fmap[o["fixture_id"]]
            w.writerow([o["fixture_id"], f["sport"], f["competition"], f["home"], f["away"],
                        f["start_utc"], o["market_id"].split("::", 1)[1], o["selection"],
                        o["probability"], o["fair_decimal"], o["american"], o["tier"]])

    with (DATA / "predictions.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["fixture_id", "selection", "probability", "american", "headline", "words"])
        for p in predictions:
            w.writerow([p["fixture_id"], p["selection"], p["probability"], p["american"],
                        p["headline"], len(p["body"].split())])
    return desk


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------

NAV = [
    ("index.html", "Desk"),
    ("matches.html", "Matches"),
    ("markets.html", "Markets"),
    ("predictions.html", "Predictions"),
    ("analysis.html", "Gate analysis"),
    ("flagged.html", "Flagged"),
    ("coverage.html", "Coverage"),
    ("sources.html", "Sources"),
    ("methodology.html", "Method"),
]

CSS = """
:root{--ink:#14161a;--muted:#5b6470;--line:#dfe3e8;--bg:#fbfbfa;--accent:#0b5d4b;--warn:#8a4b00;--high:#0b5d4b;--med:#33506e;--low:#6b7280}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
header.site{border-bottom:1px solid var(--line);background:#fff}
.wrap{max-width:1080px;margin:0 auto;padding:0 20px}
header.site .wrap{display:flex;flex-wrap:wrap;gap:8px 18px;align-items:baseline;padding:14px 20px}
header.site a.brand{font-weight:700;color:var(--ink);text-decoration:none;margin-right:8px}
nav a{color:var(--muted);text-decoration:none;font-size:14px}
nav a:hover{color:var(--accent)}
main{padding:28px 0 64px}
h1{font-size:30px;line-height:1.2;margin:6px 0 8px}
h2{font-size:21px;margin:34px 0 10px;border-top:1px solid var(--line);padding-top:18px}
h3{font-size:17px;margin:22px 0 6px}
p.lede{font-size:17px;color:#2b3038;max-width:72ch}
p,li{max-width:80ch}
.small{font-size:13px;color:var(--muted)}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(128px,1fr));gap:12px;margin:22px 0}
.stat{background:#fff;border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.stat b{display:block;font-size:24px;line-height:1.1;margin-bottom:2px}
.stat span{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
table{width:100%;border-collapse:collapse;margin:14px 0;font-size:14px;background:#fff}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);background:#f6f7f8}
tbody tr:hover{background:#fcfcfb}
td.num{text-align:right;font-variant-numeric:tabular-nums}
code{background:#f1f3f4;padding:1px 5px;border-radius:4px;font-size:13px}
.tag{display:inline-block;font-size:11px;letter-spacing:.05em;text-transform:uppercase;border-radius:999px;padding:2px 8px;border:1px solid currentColor}
.tag.HIGH{color:var(--high)}.tag.MEDIUM{color:var(--med)}.tag.LOW{color:var(--low)}.tag.UNPRICED{color:var(--muted)}
.note{background:#fff;border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:8px;padding:14px 16px;margin:18px 0}
.note.warn{border-left-color:var(--warn)}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}
.card{background:#fff;border:1px solid var(--line);border-radius:10px;padding:14px}
.card h4{margin:0 0 4px;font-size:15px}
.card .k{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
.pick{background:#fff;border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin:16px 0}
.pick h3{margin:0 0 4px;font-size:18px}
.pick .meta{font-size:13px;color:var(--muted);margin-bottom:10px}
.pick .price{font-weight:700;color:var(--accent)}
ul.clean{padding-left:18px}
footer{border-top:1px solid var(--line);padding:20px 0 40px;color:var(--muted);font-size:13px}
a{color:var(--accent)}
@media(max-width:640px){h1{font-size:24px}.stat b{font-size:20px}}
"""


def page(path: Path, title: str, body: str, depth: int = 0):
    up = "../" * depth
    nav = " ".join(f'<a href="{up}{href}">{esc(label)}</a>' for href, label in NAV)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · OLBG research desk {SID}</title>
<link rel="stylesheet" href="{up}assets/style.css">
</head><body>
<header class="site"><div class="wrap">
<a class="brand" href="{up}index.html">OLBG research desk</a>
<nav>{nav}</nav>
</div></header>
<main><div class="wrap">
{body}
</div></main>
<footer><div class="wrap">
<p class="small">Desk <code>{SID}</code> · generated {esc(GENERATED_AT)} from official league feeds read between 12:05Z and 12:25Z on 22 October 2026. Zero-margin model prices, not bookmaker quotes. No stake, edge or availability is claimed.</p>
</div></footer>
</body></html>
""")


GENERATED_AT = I.GENERATED_AT


def usd(am):
    if am is None:
        return "—"
    return f"{am:+.0f}" if am > 0 else f"{am:.0f}"


def pct(p):
    return f"{p*100:.1f}%"


def tier_tag(t):
    return f'<span class="tag {t}">{t}</span>'


def fixture_label(f):
    return f'{esc(f["home"])} v {esc(f["away"])}'


def gate_summary(desk):
    above = [o for o in desk["outcomes"] if o["probability"] > M.HIGH_PROB_FLOOR]
    in_band = [o for o in above if M.in_price_window(o["american"])]
    high = [o for o in desk["outcomes"] if o["tier"] == "HIGH"]
    return dict(above=len(above), in_band=len(in_band), high=len(high),
                capped=len(in_band) - len(high))


def render_index(desk):
    c = desk["counts"]
    g = gate_summary(desk)
    highs = [o for o in desk["outcomes"] if o["tier"] == "HIGH"]
    fmap = {f["id"]: f for f in desk["fixtures"]}
    rows = []
    for o in sorted(highs, key=lambda x: -x["probability"]):
        f = fmap[o["fixture_id"]]
        rows.append(
            f'<tr><td><a href="sports/{f["sport_slug"]}.html">{esc(f["sport"])}</a></td>'
            f'<td>{fixture_label(f)}<br><span class="small">{esc(f["start_utc"])}</span></td>'
            f'<td>{esc(o["selection"])}</td><td class="num">{pct(o["probability"])}</td>'
            f'<td class="num">{usd(o["american"])}</td>'
            f'<td class="num">{pct(o["sensitivity_low"])}–{pct(o["sensitivity_high"])}</td>'
            f'<td>{tier_tag(o["tier"])}</td></tr>')

    cards = []
    by_slug = {}
    for f in desk["fixtures"]:
        by_slug.setdefault(f["sport_slug"], []).append(f)
    for s in desk["sports"]:
        fx = by_slug.get(s["slug"], [])
        priced = sum(1 for f in fx if f["status"].startswith("verified"))
        if priced:
            status = f"{priced} priced"
        elif fx:
            status = f"{len(fx)} listed, unpriced"
        else:
            status = "no verified input"
        cards.append(
            f'<div class="card"><h4><a href="sports/{s["slug"]}.html">{esc(s["name"])}</a></h4>'
            f'<div class="k">{status}</div></div>')

    return f"""
<p class="small">22 October 2026 · observation window 12:11Z–25 October 12:11Z</p>
<h1>Twenty-three fixtures priced from official feeds, and an honest verdict on the High-confidence rule</h1>
<p class="lede">This desk re-read the NHL, EuroLeague and MLB feeds, originated zero-margin lines across
winner, handicap, match-total and team-total markets, and applied the brief's High-confidence rule
literally: more than 70% probability <em>and</em> a fair price no shorter than −250. {g['in_band']} selections
clear both tests: {g['high']} carry the player-level evidence the brief also asks for and are published as
High, while {g['capped']} is in-band but capped, with its price published and the reason flagged.</p>

<div class="stats">
  <div class="stat"><b>{c['priced_matches']}</b><span>Priced matches</span></div>
  <div class="stat"><b>{c['markets']}</b><span>Originated markets</span></div>
  <div class="stat"><b>{c['outcomes']}</b><span>Priced selections</span></div>
  <div class="stat"><b>{c['high']}</b><span>High confidence</span></div>
  <div class="stat"><b>{c['medium']}</b><span>Medium</span></div>
  <div class="stat"><b>{c['low']}</b><span>Low</span></div>
  <div class="stat"><b>{c['above_window']}</b><span>Above 70%, price outside window</span></div>
  <div class="stat"><b>{c['predictions']}</b><span>Written predictions</span></div>
</div>

<h2>High-confidence picks</h2>
<table><thead><tr><th>Sport</th><th>Fixture</th><th>Selection</th><th>Model probability</th>
<th>Fair price</th><th>Sensitivity range</th><th>Tier</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
<p class="small">Fair price is 1 ÷ model probability, expressed in American odds, with no margin added.
The sensitivity range re-computes the same selection across the shrinkage and home-advantage grid on the
<a href="methodology.html">method page</a>. A High whose range leaves the 70.00–71.43% window is fragile;
each is discussed on the <a href="analysis.html">gate analysis</a> page.</p>

<div class="note warn">
<p><strong>The rule rejects the best pick on the slate.</strong> Panathinaikos at home to Baskonia prices at
81.8% (−451 fair). It clears the probability test by twelve points and fails the price test by two hundred.
Any rule that requires a price no shorter than −250 while also requiring more than 70% can only ever return
selections inside a 1.43-percentage-point band. <a href="analysis.html">The arithmetic, and what it costs
the reader →</a></p>
</div>

<h2>Categories</h2>
<div class="cards">{''.join(cards)}</div>
<p class="small">The brief's eight excluded categories are not listed anywhere on this desk.</p>

<h2>What is and is not complete</h2>
<table><tbody>
<tr><th>Verified this session</th><td>{c['priced_matches']} fixtures: 12 NHL games, 9 EuroLeague games and 2 World Series games.
Participants, home designation and start time come from the competition's own feed. EuroLeague tip-off times are
inherited from the 07:17Z canonical read because the standings feed publishes no schedule (F-9DC-04).</td></tr>
<tr><th>Listed, unpriced</th><td>{c['listed_unpriced']} fixtures: four later World Series games outside the
72-hour window plus {c['inherited']} canonical listings from categories this session did not re-read. Prices are blank by design.</td></tr>
<tr><th>Withheld on purpose</th><td>MLB totals and run lines beyond the paired-rate model, EuroLeague High tiers
without player evidence, and every category where no official input was obtained.</td></tr>
<tr><th>Never claimed</th><td>Bookmaker availability, edge, stake, injury news or a calibrated probability.
The three models are price generators; their calibration is untested (F-9DC-09).</td></tr>
</tbody></table>
<p><a href="predictions.html">Read the three write-ups →</a> · <a href="flagged.html">All {c['findings']} flagged items →</a></p>
"""


def render_matches(desk):
    fmap = {f["id"]: f for f in desk["fixtures"]}
    groups = {}
    for f in desk["fixtures"]:
        groups.setdefault((f["sport"], f["competition"]), []).append(f)
    blocks = []
    for (sport, comp), fx in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        rows = []
        for f in sorted(fx, key=lambda x: x["start_utc"] or ""):
            outs = [o for o in desk["outcomes"] if o["fixture_id"] == f["id"]]
            best = max(outs, key=lambda o: o["probability"]) if outs else None
            state = {"verified": "verified", "verified-time-inherited": "verified · time inherited",
                     "listed-outside-window": "outside window", "inherited-unverified": "inherited, unverified"}[f["status"]]
            price = "—" if not outs else f'{usd(best["american"])} ({pct(best["probability"])})'
            link = f'<a href="{esc(f["external_url"])}" rel="noopener">source</a>' if f.get("external_url") else ""
            rows.append(
                f'<tr><td>{esc(f["start_utc"] or "—")}</td><td>{esc(f["home"])} v {esc(f["away"])}</td>'
                f'<td>{esc(f["venue"] or "—")}</td><td>{esc(state)}</td>'
                f'<td class="num">{len(outs)}</td><td class="num">{price}</td><td>{link}</td></tr>')
        blocks.append(
            f'<h2>{esc(sport)} · {esc(comp)}</h2><table><thead><tr><th>Start (UTC)</th><th>Fixture</th>'
            f'<th>Venue</th><th>Status</th><th>Selections</th><th>Best price</th><th>Source</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table>')
    return f"""
<h1>Matches</h1>
<p class="lede">Every fixture this desk will talk about, with the exact start time in UTC and the state of
its evidence. Priced fixtures carry between {min((len([o for o in desk['outcomes'] if o['fixture_id']==f['id']]) for f in desk['fixtures'] if f['status'].startswith('verified')), default=0)}
and {max((len([o for o in desk['outcomes'] if o['fixture_id']==f['id']]) for f in desk['fixtures'] if f['status'].startswith('verified')), default=0)}
priced selections; unpriced fixtures carry none.</p>
<p class="small">Blank venues and the "inherited" states are disclosed rather than filled in. The
<a href="flagged.html">Flagged page</a> holds the source-level reason for each gap.</p>
{''.join(blocks)}
"""


def render_markets(desk):
    fmap = {f["id"]: f for f in desk["fixtures"]}
    rows = []
    for o in desk["outcomes"]:
        f = fmap[o["fixture_id"]]
        market = o["market_id"].split("::", 1)[1].replace("::", " · ")
        rows.append(
            f'<tr><td>{esc(f["home"])} v {esc(f["away"])}</td><td>{esc(market)}</td>'
            f'<td>{esc(o["selection"])}</td><td class="num">{pct(o["probability"])}</td>'
            f'<td class="num">{o["fair_decimal"]:.3f}</td><td class="num">{usd(o["american"])}</td>'
            f'<td>{tier_tag(o["tier"])}</td></tr>')
    return f"""
<h1>Markets</h1>
<p class="lede">Every originated market and every priced selection, with the settlement rule applied to it.
Prices are fair prices derived from the model, rounded to three decimals; no margin, no bookmaker quote.</p>
<table><thead><tr><th>Fixture</th><th>Market</th><th>Selection</th><th>Probability</th>
<th>Decimal</th><th>American</th><th>Tier</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<h2>Settlement rules</h2>
<table><tbody>
<tr><th>Match winner</th><td>{esc(SETTLEMENT['winner'])}</td></tr>
<tr><th>Handicap / puck line / run line</th><td>{esc(SETTLEMENT['handicap'])}</td></tr>
<tr><th>Match total</th><td>{esc(SETTLEMENT['total'])}</td></tr>
<tr><th>Team total</th><td>{esc(SETTLEMENT['team-total'])}</td></tr>
</tbody></table>
<p class="small">Settlement rules are stated because a handicap on a hockey game means nothing without them:
a regulation tie always ends with a one-goal margin, so neither side can cover −1.5 from a tie.</p>
"""


def render_predictions(desk):
    blocks = []
    fmap = {f["id"]: f for f in desk["fixtures"]}
    omap = {o["id"]: o for o in desk["outcomes"]}
    for p in desk["predictions"]:
        f = fmap[p["fixture_id"]]
        o = omap[p["outcome_id"]]
        facts = "".join(
            f'<tr><th>{esc(k)}</th><td>{esc(v)}</td>'
            f'<td class="small"><a href="{esc(I.SOURCES[src]["url"])}" rel="noopener">{esc(src)}</a></td></tr>'
            for k, v, src in p["facts"])
        blocks.append(f"""
<article class="pick">
<p class="small">{esc(f["competition"])} · {esc(f["start_utc"])} · <a href="sports/{f['sport_slug']}.html">{esc(f["sport"])}</a></p>
<h3>{esc(p["headline"])}</h3>
<p class="meta">{fixture_label(f)} — <strong>{esc(o["selection"])}</strong> · model {pct(o["probability"])} ·
fair price <span class="price">{usd(o["american"])}</span> · range {pct(o["sensitivity_low"])}–{pct(o["sensitivity_high"])} {tier_tag(o["tier"])}</p>
<p>{esc(p["body"])}</p>
<table><tbody>{facts}</tbody></table>
</article>""")
    g = gate_summary(desk)
    return f"""
<h1>Predictions</h1>
<p class="lede">One written case per High-confidence pick. Each names the club, at least one player whose
season totals were read from the league's own feed this session, and the record and scoring rate the model
is reacting to. Game-level scorelines were not read (F-9DC-05), so "form" here means season-to-date numbers,
not a list of recent results. Every number is checkable against the source table under the case.</p>
{''.join(blocks)}
<h2>Why not more</h2>
<p>The gate is conjunctive: more than 70% and a fair price inside −250…+10000. {g['above']} of the
{desk['counts']['outcomes']} priced selections clear 70%; {g['in_band']} of those also sit inside the price
window. Every in-band selection except one has a write-up above. The exception — Anadolu Efes v Besiktas
over 166.5 points at 71.2% (−247) — has no player-level EuroLeague source available to this session, so it
is published at Medium with its price intact on the <a href="markets.html">markets page</a> and listed on
the <a href="flagged.html">Flagged page</a> (F-9DC-02). Publishing a High without the evidence the brief
asks for would be a worse outcome than publishing one fewer.</p>
"""


def render_analysis(desk):
    highs = [o for o in desk["outcomes"] if o["tier"] == "HIGH"]
    excluded = sorted([o for o in desk["outcomes"]
                       if o["probability"] > M.HIGH_PROB_FLOOR and not M.in_price_window(o["american"])],
                      key=lambda o: -o["probability"])[:12]
    fmap = {f["id"]: f for f in desk["fixtures"]}
    rows = "".join(
        f'<tr><td>{esc(fmap[o["fixture_id"]]["home"])} v {esc(fmap[o["fixture_id"]]["away"])}</td>'
        f'<td>{esc(o["selection"])}</td><td class="num">{pct(o["probability"])}</td>'
        f'<td class="num">{usd(o["american"])}</td><td class="small">{esc(o["reason"])}</td></tr>'
        for o in excluded)
    return f"""
<h1>The High-confidence gate, taken literally</h1>
<p class="lede">The brief asks for picks with more than 70% probability <em>and</em> odds between −250 and
+10000. Those two conditions are not independent, and the interaction is the most important thing on this
desk.</p>

<h2>1. The arithmetic</h2>
<p>A fair American price and a probability are the same number written two ways. For any probability above
50%, the price is <code>−100p/(1−p)</code>. Setting the price to the brief's short edge, −250, and solving
gives p = 0.714286. So:</p>
<table><thead><tr><th>Condition</th><th>Equivalent probability</th><th>Effect</th></tr></thead><tbody>
<tr><td>Price no shorter than −250</td><td>p ≤ 71.43%</td><td>excludes every strong favourite</td></tr>
<tr><td>Probability greater than 70%</td><td>price shorter than −233.33</td><td>excludes everything near a coin flip</td></tr>
<tr><td>Both, together</td><td>70.00% &lt; p ≤ 71.43%</td><td>a window 1.43 percentage points wide</td></tr>
<tr><td>Price of +10000</td><td>p = 0.99%</td><td>unreachable by any of these markets</td></tr>
</tbody></table>
<p>The consequence is stark. Of {desk['counts']['outcomes']} priced selections, {gate_summary(desk)['above']}
clear 70%. {gate_summary(desk)['in_band']} of those also sit inside the price window, and
{gate_summary(desk)['high']} carry the player-level evidence the brief requires. The gate does not select the
best picks; it selects the picks whose prices happen to fall in a narrow band.</p>

<h2>2. What the window throws away</h2>
<table><thead><tr><th>Fixture</th><th>Selection</th><th>Probability</th><th>Fair price</th><th>Why it is not High</th></tr></thead>
<tbody>{rows}</tbody></table>
<p class="small">Full list on the <a href="markets.html">markets page</a>, where every one of these rows is
published with its price and tier.</p>

<h2>3. Everything is fragile at this sample size</h2>
<p>Each club has played between seven and eleven games. The models shrink those rates toward the league mean,
but the choice of shrinkage constant still moves a probability by three to five points — wider than the
1.43-point window itself. The sensitivity column on every High row is the model re-run across that grid.
Two of the three Highs leave the window at one end of it. That is not a defect of the picks; it is a
property of asking for a 71% selection from a ten-game sample.</p>

<h2>4. What would make this desk stronger</h2>
<ul class="clean">
<li>A settled-fixture backtest. None of the priced fixtures had finished when the desk was built, so no
calibration statistic exists (F-9DC-09).</li>
<li>Official player availability. Not published in the feeds used here; a High built on a lineup that
changes at warm-up is not a High.</li>
<li>A league-average run environment for MLB, which would let totals be priced instead of withheld.</li>
</ul>
"""


def render_flagged(desk):
    items = "".join(
        f'<tr><td><code>{esc(f["id"])}</code></td><td><strong>{esc(f["title"])}</strong><br>{esc(f["detail"])}</td>'
        f'<td class="small">{esc(f["impact"])}</td></tr>' for f in desk["findings"])
    return f"""
<h1>Flagged for review</h1>
<p class="lede">Ten things this desk could not verify, chose not to publish, or believes a reader should
weigh before using a number. None of them is hidden in a footnote.</p>
<table><thead><tr><th>ID</th><th>Finding</th><th>What it affects</th></tr></thead><tbody>{items}</tbody></table>
<h2>The two that need a decision</h2>
<p><strong>F-9DC-01</strong> is the gate itself: as written it can only return selections between 70.00% and
71.43%. If the intent was "strong favourites", the −250 floor should be removed or inverted.
<strong>F-9DC-02</strong> is the EuroLeague cap: one selection cleared both tests but had no player-level
source, so it was published at Medium with its price. Both are decisions for the person who wrote the brief,
not for this desk.</p>
"""


def render_coverage(desk):
    by_slug = {}
    for f in desk["fixtures"]:
        by_slug.setdefault(f["sport_slug"], []).append(f)
    rows = []
    for s in desk["sports"]:
        fx = by_slug.get(s["slug"], [])
        priced = sum(1 for f in fx if f["status"].startswith("verified"))
        state = "priced" if priced else ("listed only" if fx else "no verified input")
        rows.append(f'<tr><td><a href="sports/{s["slug"]}.html">{esc(s["name"])}</a></td>'
                    f'<td class="num">{s["route_id"]}</td><td class="num">{len(fx)}</td>'
                    f'<td class="num">{priced}</td><td>{esc(state)}</td></tr>')
    return f"""
<h1>Coverage across the seventeen in-scope categories</h1>
<p class="lede">The brief's seventeen categories, with what this session actually obtained for each. Fourteen
of them have no verified input; that is published as an empty category rather than filled with remembered
fixtures.</p>
<table><thead><tr><th>Category</th><th>OLBG route</th><th>Fixtures listed</th><th>Priced</th><th>State</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
<p class="small">Route ids are OLBG's own taxonomy, reverse-engineered in the T1 investigation. The eight
excluded categories (football, boxing, MMA, politics, TV, specials, athletics, US greyhound racing) appear
nowhere on this desk.</p>
"""


def render_sources(desk):
    rows = "".join(
        f'<tr><td><code>{esc(k)}</code></td><td>{esc(v["publisher"])}</td><td>{esc(v["title"])}'
        f'{"" if not v.get("inherited") else " <em>(inherited)</em>"}</td>'
        f'<td class="small"><a href="{esc(v["url"])}" rel="noopener">{esc(v["url"])}</a></td>'
        f'<td class="small">{esc(v["observed_at"])}</td><td>{esc(v["note"])}</td></tr>'
        for k, v in desk["sources"].items())
    return f"""
<h1>Sources</h1>
<p class="lede">Every number on this desk traces to one of six official reads. The observation timestamp is
the moment the response was received, not the moment the page was written.</p>
<table><thead><tr><th>ID</th><th>Publisher</th><th>Document</th><th>URL</th><th>Observed</th><th>What it supplied</th></tr></thead>
<tbody>{rows}</tbody></table>
<h2>Source discipline</h2>
<ul class="clean">
<li>No secondary aggregator, no social post, no memory: a value that has no row in the table above is not on the desk.</li>
<li>Where a feed does not publish a field — EuroLeague tip-off times, NHL venues for seven of twelve games,
the Tampa Bay Game 1 starter — the field is blank and the gap is flagged, never filled from another source.</li>
<li>Prices are model output, not quotes. Nothing here implies a bookmaker would offer them.</li>
</ul>
"""


def render_methodology(desk):
    return f"""
<h1>Method</h1>
<p class="lede">Three deliberately small models, each with its assumptions printed next to its output. The
goal is a defensible price, not a replica of a betting market.</p>

<h2>Ice hockey</h2>
<p>Goals for and against per game are shrunk toward the league mean with a weight of {M.NHL_K} pseudo-games,
then combined multiplicatively as attack × defence against the opponent, divided by the league mean. Home
advantage multiplies the home expectation by {M.NHL_HOME} and the away expectation by {2 - M.NHL_HOME}.
Independent Poisson goal counts give the margin distribution. A regulation tie is split evenly between the
two clubs for the moneyline and produces a one-goal margin for the puck line, which is why neither side can
cover −1.5 from a tie.</p>

<h2>EuroLeague</h2>
<p>A club's rating is its points differential per game, shrunk toward zero by {M.EL_K} pseudo-games. The
rating gap is multiplied by {M.EL_DIFF_WEIGHT} — a ten-game differential in October is not worth its full
weight — and {M.EL_HOME_EDGE} points of home edge are added. Expected total points come from the two clubs'
combined scoring and conceding rates. Margins are normal with a standard deviation of {M.EL_MARGIN_SD};
totals are normal with {M.EL_TOTAL_SD}.</p>
<p>Everything in this section is an assumption. The shrink weight and the rating multiplier were chosen so
that the largest favourite on the slate prices near 82% rather than 97%, which is what the earlier
multiplicative version produced. That choice is documented because it is a judgement, not a measurement.</p>

<h2>Baseball</h2>
<p>Pythagorean win rates with exponent {M.MLB_PYTH} are combined with log5 and a home adjustment, giving the
moneyline. Run expectations are the mean of the batting side's runs scored and the bowling side's runs
allowed per game, with {M.MLB_HOME_RUNS} runs of home edge; tied nine-inning games are split evenly and the
distribution is renormalised. Totals and run lines use that same Poisson pair.</p>

<h2>The tier rule</h2>
<table><tbody>
<tr><th>HIGH</th><td>probability &gt; 70% <em>and</em> fair American inside −250…+10000 <em>and</em> a written
prediction backed by player-level evidence from an official feed</td></tr>
<tr><th>MEDIUM</th><td>probability ≥ 65%, or one of the two High tests failed. The reason is stored on the
row and shown in the data export.</td></tr>
<tr><th>LOW</th><td>everything else</td></tr>
</tbody></table>
<p>The third High condition is stricter than the brief. It exists because the brief also requires each pick to
name a player, and a pick whose player numbers were never read is not that.</p>

<h2>Sensitivity</h2>
<p>Every selection is re-priced across a grid: for hockey, shrinkage of 6/12/20 games × home multipliers of
1.00/1.045/1.08; for basketball, shrinkage of 2/4/8 × home edge 2.0/2.5/3.0 × margin σ of 10/11/12; for
baseball, exponents of 1.70/1.83/2.00 × home edge of 0/0.15/0.30 runs. The published range is the min and max
across the grid.</p>

<h2>Reproduction</h2>
<p><code>python3 scripts/s9dc28d1e_build.py --now 2026-10-22T12:30:00Z</code> regenerates every table and page
byte-for-byte; <code>python3 scripts/s9dc28d1e_validate.py</code> re-checks the counts, the gate, the writing
rules and the links.</p>
"""


def render_sport(desk, sport):
    fx = [f for f in desk["fixtures"] if f["sport_slug"] == sport["slug"]]
    if not fx:
        return f"""
<h1>{esc(sport['name'])}</h1>
<p class="lede">No fixture in this category was verified from an official source during this session, so
nothing is published here. The category is kept so that the gap is visible rather than silently dropped.</p>
<p><a href="../coverage.html">Coverage across all seventeen categories →</a></p>"""
    fmap = {f["id"]: f for f in fx}
    outs = [o for o in desk["outcomes"] if o["fixture_id"] in fmap]
    rows = "".join(
        f'<tr><td>{esc(fmap[o["fixture_id"]]["home"])} v {esc(fmap[o["fixture_id"]]["away"])}</td>'
        f'<td>{esc(o["market_id"].split("::", 1)[1].replace("::", " · "))}</td>'
        f'<td>{esc(o["selection"])}</td><td class="num">{pct(o["probability"])}</td>'
        f'<td class="num">{usd(o["american"])}</td><td>{tier_tag(o["tier"])}</td></tr>'
        for o in sorted(outs, key=lambda o: -o["probability"]))
    fixtures = "".join(
        f'<tr><td>{esc(f["start_utc"])}</td><td>{esc(f["home"])} v {esc(f["away"])}</td>'
        f'<td>{esc(f["competition"])}</td><td>{esc(f["status"])}</td></tr>'
        for f in sorted(fx, key=lambda x: x["start_utc"] or ""))
    if not outs:
        return f"""
<h1>{esc(sport['name'])}</h1>
<p class="lede">{len(fx)} listings in this category, none of them re-read this session, so no price is
published. They are carried from the canonical 07:17Z observation window and marked unverified.</p>
<table><thead><tr><th>Start (UTC)</th><th>Fixture</th><th>Competition</th><th>Evidence</th></tr></thead>
<tbody>{fixtures}</tbody></table>"""
    return f"""
<h1>{esc(sport['name'])}</h1>
<p class="lede">{len(fx)} fixtures and {len(outs)} priced selections in this category.</p>
<table><thead><tr><th>Start (UTC)</th><th>Fixture</th><th>Competition</th><th>Evidence</th></tr></thead>
<tbody>{fixtures}</tbody></table>
<h2>Priced selections</h2>
<table><thead><tr><th>Fixture</th><th>Market</th><th>Selection</th><th>Probability</th><th>Fair</th><th>Tier</th></tr></thead>
<tbody>{rows}</tbody></table>"""


def render_site(desk):
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "assets").mkdir(parents=True, exist_ok=True)
    (SITE / "assets" / "style.css").write_text(CSS)

    page(SITE / "index.html", "Dashboard", render_index(desk))
    page(SITE / "matches.html", "Matches", render_matches(desk))
    page(SITE / "markets.html", "Markets", render_markets(desk))
    page(SITE / "predictions.html", "Predictions", render_predictions(desk))
    page(SITE / "analysis.html", "Gate analysis", render_analysis(desk))
    page(SITE / "flagged.html", "Flagged for review", render_flagged(desk))
    page(SITE / "coverage.html", "Coverage", render_coverage(desk))
    page(SITE / "sources.html", "Sources", render_sources(desk))
    page(SITE / "methodology.html", "Method", render_methodology(desk))
    for sport in desk["sports"]:
        page(SITE / "sports" / f"{sport['slug']}.html", sport["name"], render_sport(desk, sport), depth=1)

    pages = sorted(p.relative_to(SITE).as_posix() for p in SITE.rglob("*.html"))
    return pages


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--now", default=I.GENERATED_AT)
    args = ap.parse_args()
    global GENERATED_AT
    GENERATED_AT = args.now
    desk = build(args.now)
    pages = render_site(desk)
    print(f"built {len(pages)} pages; counts={desk['counts']}")


if __name__ == "__main__":
    main()
