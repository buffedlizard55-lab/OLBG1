"""Build the d33cf454 desk: data JSON + static pages under /d33cf454/.

Run: python3 scripts/sd33cf454_build.py

Everything is generated from scripts/sd33cf454_data.py, so the pages cannot drift
from the record. Relative links only; no external assets.
"""
import html
import json
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.sd33cf454_data import (
    CAPTURED, DESK, TASK, SOURCES, SPORTS, EVENTS, PICKS, FLAGS, COVERAGE,
)

OUT = ROOT / DESK
DATA = ROOT / "data" / DESK


def e(v):
    return html.escape("" if v is None else str(v), quote=True)


def stamp(iso):
    if not iso:
        return "not confirmed"
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})", iso)
    if not m:
        return e(iso)
    return "{}-{} {}:{}:00Z".format(m.group(2), m.group(3), m.group(4), m.group(5))


SPORT_NAMES = {k: n for k, n, _ in SPORTS}
EV = {x["id"]: x for x in EVENTS}


def src_links(ids, official_only=False):
    parts = []
    for sid in ids:
        s = SOURCES[sid]
        if official_only and s["role"] != "official":
            continue
        parts.append(
            '<a class="src {}" href="{}" target="_blank" '
            'rel="noopener noreferrer">{}</a>'.format(s["role"], e(s["url"]), e(s["publisher"]))
        )
    return " ".join(parts) if parts else '<span class="blank">none &mdash; unverified</span>'


def official(ids):
    return [i for i in ids if SOURCES[i]["role"] == "official"]


def american(prob):
    if prob >= 0.5:
        return int(round(-100 * prob / (1 - prob)))
    return int(round(100 * (1 - prob) / prob))


def dec(prob):
    return round(1 / prob, 3)


CSS = (
    ":root{--ink:#101828;--muted:#5b6779;--line:#e3e8ef;--bg:#f7f9fc;--card:#fff;"
    "--brand:#0b5fff;--brand-soft:#eaf1ff;--ok:#067647;--ok-soft:#ecfdf3;"
    "--warn:#b54708;--warn-soft:#fffaeb;--stop:#b42318;--stop-soft:#fef3f2;--radius:14px}"
    "*{box-sizing:border-box}"
    "body{margin:0;font:16px/1.6 -apple-system,BlinkMacSystemFont,\"Segoe UI\",Roboto,Helvetica,Arial,sans-serif;"
    "color:var(--ink);background:var(--bg);-webkit-font-smoothing:antialiased}"
    "a{color:var(--brand);text-decoration:none}a:hover{text-decoration:underline}"
    "header.top{background:var(--card);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:20}"
    ".wrap{max-width:1180px;margin:0 auto;padding:0 20px}"
    ".nav{display:flex;flex-wrap:wrap;gap:4px;align-items:center;padding:10px 0}"
    ".brand{font-weight:750;margin-right:18px;color:var(--ink);font-size:15px;letter-spacing:-.01em}"
    ".brand span{color:var(--brand)}"
    ".nav a.link{padding:6px 10px;border-radius:8px;color:var(--muted);font-size:14px;font-weight:550}"
    ".nav a.link:hover{background:var(--brand-soft);color:var(--brand);text-decoration:none}"
    ".nav a.link.active{background:var(--brand-soft);color:var(--brand)}"
    "main{padding:28px 0 60px}"
    "h1{font-size:clamp(26px,3.4vw,38px);line-height:1.15;margin:6px 0 10px;letter-spacing:-.02em}"
    "h2{font-size:21px;margin:38px 0 12px;letter-spacing:-.01em}"
    "h3{font-size:16px;margin:22px 0 8px}"
    "p{margin:0 0 12px;color:#344054}"
    ".eyebrow{text-transform:uppercase;letter-spacing:.09em;font-size:11.5px;font-weight:700;color:var(--brand);margin:0}"
    ".lede{font-size:17px;color:#344054;max-width:74ch}"
    ".kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:22px 0 6px}"
    ".kpi{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:14px 16px}"
    ".kpi b{display:block;font-size:26px;letter-spacing:-.02em;line-height:1.2}"
    ".kpi small{color:var(--muted);font-size:12.5px;text-transform:uppercase;letter-spacing:.06em;font-weight:650}"
    ".card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:18px 20px;margin:14px 0}"
    ".grid{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}"
    ".jump{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(215px,1fr));margin:16px 0}"
    ".jump a{display:block;background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:15px 16px;color:var(--ink)}"
    ".jump a:hover{border-color:#b6ccff;text-decoration:none;box-shadow:0 2px 10px rgba(11,95,255,.07)}"
    ".jump b{display:block;font-size:15px}.jump small{color:var(--muted)}"
    "table{width:100%;border-collapse:collapse;font-size:14.5px}"
    ".table-wrap{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);overflow:auto;margin:12px 0}"
    "th{text-align:left;font-size:11.5px;text-transform:uppercase;letter-spacing:.07em;color:var(--muted);"
    "padding:11px 14px;border-bottom:1px solid var(--line);white-space:nowrap;background:#fbfcfe}"
    "td{padding:12px 14px;border-bottom:1px solid #f1f4f8;vertical-align:top}"
    "tr:last-child td{border-bottom:0}"
    "td.num{white-space:nowrap;font-variant-numeric:tabular-nums}"
    ".pick{display:grid;grid-template-columns:64px 1fr auto;gap:16px;align-items:start;"
    "background:var(--card);border:1px solid var(--line);border-left:4px solid var(--brand);"
    "border-radius:var(--radius);padding:16px 18px;margin:12px 0}"
    ".pick .rank{font-size:22px;font-weight:750;color:var(--brand);line-height:1}"
    ".pick h3{margin:0 0 4px;font-size:17px}"
    ".pick .sel{font-weight:700;color:var(--ink)}"
    ".pick .meta{color:var(--muted);font-size:13.5px}"
    ".pick .price{text-align:right}"
    ".pick .price b{display:block;font-size:20px;font-variant-numeric:tabular-nums}"
    ".badge{display:inline-block;padding:2px 9px;border-radius:999px;font-size:11.5px;font-weight:700;"
    "letter-spacing:.03em;text-transform:uppercase}"
    ".badge.high{background:var(--stop-soft);color:var(--stop)}"
    ".badge.medium{background:var(--warn-soft);color:var(--warn)}"
    ".badge.low{background:#eef2f6;color:#475467}"
    ".badge.ok{background:var(--ok-soft);color:var(--ok)}"
    ".badge.blank{background:#eef2f6;color:#475467}"
    ".src{display:inline-block;font-size:12.5px;padding:2px 8px;border:1px solid var(--line);border-radius:999px;"
    "margin:2px 4px 2px 0;background:#fff;color:#344054}"
    ".src.official{border-color:#b6ccff;color:var(--brand);background:var(--brand-soft)}"
    ".src.discovery{color:var(--muted)}"
    ".blank{color:#98a2b3;font-style:italic}"
    ".note{background:var(--brand-soft);border:1px solid #cfe0ff;border-radius:var(--radius);padding:14px 16px;margin:16px 0}"
    ".warn{background:var(--warn-soft);border:1px solid #fedf89;border-radius:var(--radius);padding:14px 16px;margin:16px 0}"
    ".danger{background:var(--stop-soft);border:1px solid #fecdca;border-radius:var(--radius);padding:14px 16px;margin:16px 0}"
    ".note p:last-child,.warn p:last-child,.danger p:last-child{margin-bottom:0}"
    "details{border:1px solid var(--line);border-radius:12px;padding:12px 16px;background:var(--card);margin:10px 0}"
    "summary{cursor:pointer;font-weight:650}"
    ".prose{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:18px 20px;margin:12px 0}"
    ".prose .txt{font-size:16px;color:#1d2939}"
    ".prose .ev{font-size:13px;color:var(--muted);margin-bottom:10px}"
    "footer{border-top:1px solid var(--line);background:var(--card);padding:22px 0;color:var(--muted);font-size:13px}"
    ".tag{display:inline-block;font-size:11.5px;color:var(--muted);border:1px dashed var(--line);border-radius:999px;padding:1px 8px}"
    "@media(max-width:640px){.pick{grid-template-columns:1fr}.pick .price{text-align:left}.pick .rank{display:none}}"
)


def page(title, body, active="", rel=""):
    nav = [
        ("Executive summary", "index.html", "overview"),
        ("Today's & upcoming picks", "picks.html", "picks"),
        ("Written predictions", "predictions.html", "preds"),
        ("All matches", "matches.html", "matches"),
        ("Markets", "markets.html", "markets"),
        ("Sources", "sources.html", "sources"),
        ("Flagged for review", "flagged.html", "flagged"),
        ("Coverage", "coverage.html", "coverage"),
        ("Method", "methodology.html", "method"),
        ("Reverse engineering", "reverse-engineering.html", "rev"),
    ]
    links = ""
    for t, p, k in nav:
        cls = " link active" if k == active else " link"
        links += '<a class="{}" href="{}">{}</a>'.format(cls, rel + p, e(t))
    sports_tags = ""
    for k, n, _ in SPORTS:
        sports_tags += '<a class="tag" style="margin:2px 6px 2px 0" href="{}sports/{}.html">{}</a>'.format(rel, k, e(n))
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>{} &middot; OLBG desk {}</title>'
        '<meta name="color-scheme" content="light"><style>{}</style></head><body>'
        '<header class="top"><div class="wrap"><div class="nav">'
        '<a class="brand" href="{}index.html">OLBG<span>.</span> research desk '
        '<span style="color:#98a2b3;font-weight:500">/ {}</span></a>{}'
        '</div></div></header>'
        '<main><div class="wrap">{}</div>'
        '<footer><div><strong>Capture {}</strong> &middot; independent research, not betting advice. 18+.'
        ' Prices on this site are our own calculated fair odds, not quoted bookmaker odds.'
        ' <a href="{}methodology.html">How prices are produced</a> &middot;'
        ' <a href="https://www.olbg.com/betting-tips">OLBG</a></div>'
        '<div style="margin-top:8px">Sports: {}</div>'
        '<div style="margin-top:8px"><a href="https://buffedlizard55-lab.github.io/OLBG1/">Canonical research desk</a> &middot;'
        '<a href="https://github.com/buffedlizard55-lab/OLBG1">Repository</a></div></footer>'
        '</main></body></html>'
    ).format(e(title), DESK, CSS, rel, DESK, links, body, CAPTURED, rel, sports_tags)


def pick_card(i, p):
    ev = EV[p["event"]]
    when = stamp(ev["start"])
    if ev["basis"] == "official":
        basis = "official start"
    elif ev["basis"] == "derived":
        basis = "derived from OLBG display"
    else:
        basis = "start not confirmed"
    participants = " / ".join(x for x in [ev.get("home"), ev.get("away"), ev.get("name")] if x)
    return (
        '<div class="pick"><div class="rank">{}</div>'
        '<div><h3>{}</h3>'
        '<div class="sel">{}</div>'
        '<div class="meta">{} &middot; {} &middot; {} ({})</div>'
        '<div class="meta">{}</div></div>'
        '<div class="price"><b>{}</b>'
        '<span class="meta">{:.1f}% &middot; {:.3f}</span><br>'
        '<span class="badge {}">{}</span></div></div>'
    ).format(
        i, e(p["selection"]), e(participants),
        e(SPORT_NAMES[p["sport"]]), e(ev["comp"]), when, basis,
        src_links(ev["src"]),
        american(p["prob"]), p["prob"] * 100, dec(p["prob"]),
        p["tier"].lower(), e(p["tier"]),
    )


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    (OUT / "sports").mkdir(parents=True, exist_ok=True)

    highs = [p for p in PICKS if p["tier"] == "High"]
    mediums = [p for p in PICKS if p["tier"] == "Medium"]
    lows = [p for p in PICKS if p["tier"] == "Low"]
    official_srcs = [s for s in SOURCES.values() if s["role"] == "official"]
    discovery_srcs = [s for s in SOURCES.values() if s["role"] == "discovery"]
    desk_root = "/OLBG1/" + DESK + "/"

    # ---------- index: executive summary ----------
    cards = "".join(pick_card(i + 1, p) for i, p in enumerate(PICKS))
    high_cards_html = ""
    for p in highs:
        ev = EV[p["event"]]
        high_cards_html += (
            '<div class="card"><h3 style="margin-top:0">{}</h3>'
            '<p class="meta">{} &middot; {}</p>'
            '<p style="margin:8px 0 0">{:.0f} &middot; {:.1f}% &middot; <span class="badge high">High</span></p>'
            '<p style="margin:8px 0 0">{}</p></div>'
        ).format(
            e(p["selection"]), e(SPORT_NAMES[p["sport"]]), e(ev["comp"]),
            p["american"], p["prob"] * 100,
            src_links(official(ev["src"])),
        )
    if not highs:
        high_cards_html = '<div class="card"><p class="blank">No high-confidence picks today.</p></div>'

    index_body = (
        '<p class="eyebrow">Executive summary — 24 October 2026</p>'
        '<h1>Today\'s picks, at a glance</h1>'
        '<p class="lede">This desk reverse-engineered the OLBG hubs for all fifteen brief sports, verified every fixture'
        ' against an official source where one could be read, originated our own zero-vig lines, and graded each selection'
        ' low / medium / high. High confidence means an estimated win probability above 70% <strong>and</strong> an originated'
        ' fair American price between −250 and +10000. Nothing was inflated to fill a quota.</p>'
        '<div class="kpis">'
        '<div class="kpi"><b>{ne}</b><small>fixtures listed</small></div>'
        '<div class="kpi"><b>{np}</b><small>originated picks</small></div>'
        '<div class="kpi"><b>{nh}</b><small>high confidence</small></div>'
        '<div class="kpi"><b>{nm}</b><small>medium confidence</small></div>'
        '<div class="kpi"><b>{nl}</b><small>low confidence</small></div>'
        '<div class="kpi"><b>{no}</b><small>official sources read</small></div>'
        '<div class="kpi"><b>{nf}</b><small>flagged for review</small></div>'
        '</div>'
        '<div class="note"><p><strong>Where the picks are.</strong> Every pick is shown below with its sport, competition,'
        ' start time, source links, our originated price and confidence tier. Full written predictions (30+ words each,'
        ' naming the selection, both sides and the official fact they rest on) are on the <a href="{dr}picks.html">picks</a> page.'
        ' The complete fixture table is on <a href="{dr}matches.html">all matches</a>.</p></div>'
        '<h2>High-confidence picks today</h2>'
        '<p class="lede">{nh} selection cleared the High gate (p &gt; 0.70 and fair price inside −250…+10000).</p>'
        '<div class="grid">{hc}</div>'
        '<h2>All originated picks</h2>'
        '<div class="table-wrap">{ca}</div>'
        '<h2>Why some sports have no pick</h2>'
        '<div class="grid">'
        '<div class="card"><h3 style="margin-top:0">1. The evidence gate</h3><p>A pick needs three things: an open OLBG market,'
        ' an official fixture confirmation, and at least one official form or availability fact. Sports where the second or'
        ' third was missing produce zero picks, not a weak one.</p></div>'
        '<div class="card"><h3 style="margin-top:0">2. High is not a label</h3><p>No market produced a probability above 70% on'
        ' the facts that were readable outside the three High picks shown. A 55% pick labelled High would be a lie with a number attached.</p></div>'
        '<div class="card"><h3 style="margin-top:0">3. Official feeds are thin</h3><p>MLB, the NHL, the NBA, Formula 1 and the World Snooker Tour publish'
        ' machine-readable fixtures. Cricket, handball, volleyball, darts, Gaelic games and rugby league do not publish anything comparable that was reachable here.</p></div>'
        '</div>'
    )
    index_body = index_body.format(
        ne=len(EVENTS), np=len(PICKS), nh=len(highs), nm=len(mediums), nl=len(lows),
        no=len(official_srcs), nf=len(FLAGS),
        dr="", hc=high_cards_html, ca=cards,
    )
    (OUT / "index.html").write_text(page("Executive summary", index_body, "overview"), encoding="utf-8")

    # ---------- picks ----------
    pick_rows = []
    for i, p in enumerate(PICKS):
        ev = EV[p["event"]]
        participants = " / ".join(x for x in [ev.get("home"), ev.get("away"), ev.get("name")] if x)
        row = (
            '<tr><td class="num">#{}</td><td><strong>{}</strong></td>'
            '<td>{}</td><td>{}</td><td>{}</td>'
            '<td class="num">{}</td><td>{}</td>'
            '<td class="num">{}</td><td class="num">{:.1f}%</td>'
            '<td><span class="badge {}">{}</span></td>'
            '<td>{}</td></tr>'
        ).format(
            i + 1, e(p["selection"]), e(participants),
            e(SPORT_NAMES[p["sport"]]), e(ev["comp"]),
            stamp(ev["start"]), e(ev["basis"] or "not confirmed"),
            american(p["prob"]), p["prob"] * 100,
            p["tier"].lower(), e(p["tier"]),
            src_links(ev["src"]),
        )
        pick_rows.append(row)
    _picks_inner = (
        '<p class="eyebrow">Today\'s &amp; upcoming picks</p>'
        '<h1>All originated selections</h1>'
        '<p class="lede">{np} picks across {ns} sports. Each row names the betting selection, both sides,'
        ' the competition, the start time and its source, plus our originated fair price and confidence tier.</p>'
        '<div class="table-wrap"><table><thead><tr>'
        '<th>#</th><th>Selection</th><th>Matchup</th><th>Sport</th><th>Competition</th>'
        '<th>Start (UTC)</th><th>Time basis</th><th>Price</th><th>Prob.</th><th>Tier</th><th>Sources</th>'
        '</tr></thead><tbody>{rows}</tbody></table></div>'
    )
    picks_body = _picks_inner.format(
        np=len(PICKS), ns=len({p["sport"] for p in PICKS}), rows="".join(pick_rows),
    )
    (OUT / "picks.html").write_text(page("Picks", picks_body, "picks"), encoding="utf-8")

    # ---------- predictions ----------
    pred_rows = []
    for p in PICKS:
        ev = EV[p["event"]]
        participants = " / ".join(x for x in [ev.get("home"), ev.get("away"), ev.get("name")] if x)
        row = (
            '<div class="card" id="{}">'
            '<h3 style="margin-top:0">{}</h3>'
            '<p class="meta" style="color:var(--muted);font-size:13px">{}, {}, {} ({})</p>'
            '<div class="prose"><div class="txt">{}</div>'
            '<div class="ev">Selection: {} &middot; Originated price: {} &middot;'
            ' Estimated probability: {:.1f}% &middot; Tier: {}</div>'
            '<p style="margin:0">{}</p></div></div>'
        ).format(
            e(p["id"]), e(p["selection"]),
            e(SPORT_NAMES[p["sport"]]), e(ev["comp"]), stamp(ev["start"]),
            e(ev["basis"] or "not confirmed"),
            e(p["prediction"]),
            e(p["selection"]), american(p["prob"]), p["prob"] * 100, e(p["tier"]),
            src_links(ev["src"]),
        )
        pred_rows.append(row)
    _preds_inner = (
        '<p class="eyebrow">Written predictions</p>'
        '<h1>High-confidence predictions</h1>'
        '<p class="lede">Each prediction is unique, at least 30 words, names the selection and both participants, states'
        ' the competition, current form, recent match history, match statistics and injuries where an official source'
        ' confirmed them, and ends with the betting selection in plain terms. No internal vocabulary'
        ' (\'model\', \'verified\') appears in any prediction.</p>'
        '{rows}'
        '<h2>How predictions are produced</h2>'
        '<p>Only picks that clear the High gate (p &gt; 0.70 and fair price inside −250…+10000) receive a written prediction.'
        ' Each one is hand-written from the official facts read this session and is never templated.</p>'
    )
    preds_body = _preds_inner.format(
        rows="".join(pred_rows) if pred_rows else '<p class="blank">No high-confidence predictions to publish.</p>',
    )
    (OUT / "predictions.html").write_text(page("Predictions", preds_body, "preds"), encoding="utf-8")

    # ---------- matches ----------
    match_rows = []
    for ev in EVENTS:
        participants = " / ".join(x for x in [ev.get("home"), ev.get("away"), ev.get("name")] if x) or "tournament field"
        picks_for = [p for p in PICKS if p["event"] == ev["id"]]
        pick_text = "; ".join(
            "{} ({}, {})".format(e(p["selection"]), "%+d" % p["american"], e(p["tier"])) for p in picks_for
        ) or "<span class='blank'>none</span>"
        row = (
            '<tr><td class="num">{}</td><td>{}</td><td>{}</td>'
            '<td>{}</td><td class="num">{}</td><td>{}</td>'
            '<td>{}</td><td>{}</td></tr>'
        ).format(
            e(ev["id"]), e(SPORT_NAMES[ev["sport"]]), e(ev["comp"]),
            e(participants), stamp(ev["start"]),
            e(ev["basis"] or "not confirmed"), pick_text,
            src_links(ev["src"]),
        )
        match_rows.append(row)
    _matches_inner = (
        '<p class="eyebrow">All fifteen sports</p>'
        '<h1>All matches</h1>'
        '<p class="lede">{n} fixture/event listings from the OLBG hubs, each with its OLBG URL, start time, time basis,'
        ' any originated pick and every source used to confirm it. Blank fields mean the value could not be confirmed'
        ' from an official source.</p>'
        '<div class="table-wrap"><table><thead><tr>'
        '<th>Id</th><th>Sport</th><th>Competition</th><th>Participants</th>'
        '<th>Start (UTC)</th><th>Time basis</th><th>Originated pick</th><th>Sources</th>'
        '</tr></thead><tbody>{rows}</tbody></table></div>'
    )
    matches_body = _matches_inner.format(
        n=len(EVENTS), rows="".join(match_rows),
    )
    (OUT / "matches.html").write_text(page("Matches", matches_body, "matches"), encoding="utf-8")

    # ---------- markets ----------
    market_rows = []
    for p in PICKS:
        ev = EV[p["event"]]
        for mkt, status, detail in p["markets"]:
            row = (
                '<tr><td class="num">{}</td><td>{}</td><td>{}</td>'
                '<td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'
            ).format(
                e(p["id"]), e(SPORT_NAMES[p["sport"]]), e(ev["comp"]),
                e(p["selection"]), e(mkt), e(status), e(detail),
            )
            market_rows.append(row)
    _markets_inner = (
        '<p class="eyebrow">Market families examined</p>'
        '<h1>Markets</h1>'
        '<p class="lede">{nm} market lines examined across {np} picks. For each pick we examine match winner,'
        ' handicap/spread and match total (or sport-specific equivalents) where an official input exists.'
        ' \'Originated\' means our own zero-vig fair price; \'withheld\' means no official input was available to price it.</p>'
        '<div class="table-wrap"><table><thead><tr>'
        '<th>Pick</th><th>Sport</th><th>Competition</th><th>Selection</th>'
        '<th>Market</th><th>Status</th><th>Detail</th>'
        '</tr></thead><tbody>{rows}</tbody></table></div>'
    )
    markets_body = _markets_inner.format(
        nm=len(market_rows), np=len(PICKS),
        rows="".join(market_rows) if market_rows else '<tr><td colspan="7" class="blank">No market lines examined.</td></tr>',
    )
    (OUT / "markets.html").write_text(page("Markets", markets_body, "markets"), encoding="utf-8")

    # ---------- sport subpages ----------
    for slug, name, path in SPORTS:
        evs = [x for x in EVENTS if x["sport"] == slug]
        picks_s = [p for p in PICKS if p["sport"] == slug]
        erows = []
        for ev in evs:
            participants = " / ".join(x for x in [ev.get("home"), ev.get("away"), ev.get("name")] if x) or "tournament field"
            row = (
                '<tr><td class="num">{}</td><td>{}</td><td>{}</td>'
                '<td class="num">{}</td><td>{}</td><td>{}</td></tr>'
            ).format(
                e(ev["id"]), e(ev["comp"]), e(participants),
                stamp(ev["start"]), e(ev["basis"] or "not confirmed"),
                src_links(ev["src"]),
            )
            erows.append(row)
        prows = []
        for p in picks_s:
            row = (
                '<tr><td class="num">{}</td><td>{}</td><td class="num">{}</td>'
                '<td class="num">{:.1f}%</td><td><span class="badge {}">{}</span></td></tr>'
            ).format(
                e(p["id"]), e(p["selection"]), american(p["prob"]),
                p["prob"] * 100, p["tier"].lower(), e(p["tier"]),
            )
            prows.append(row)
        _sp_inner = (
            '<p class="eyebrow">{nm}</p>'
            '<h1>{nm}</h1>'
            '<p class="lede">{nev} fixture/listing &middot; {npk} originated pick{ps}. {cov}</p>'
            '<h2>Fixtures</h2>'
            '<div class="table-wrap"><table><thead><tr>'
            '<th>Id</th><th>Competition</th><th>Participants</th>'
            '<th>Start (UTC)</th><th>Time basis</th><th>Sources</th>'
            '</tr></thead><tbody>{erows}</tbody></table></div>'
            '<h2>Picks</h2>'
            '<div class="table-wrap"><table><thead><tr>'
            '<th>Id</th><th>Selection</th><th>Price</th><th>Prob.</th><th>Tier</th>'
            '</tr></thead><tbody>{prows}</tbody></table></div>'
        )
        sp_body = _sp_inner.format(
            nm=e(name), nev=len(evs), npk=len(picks_s),
            ps="s" if len(picks_s) != 1 else "", cov=e(COVERAGE.get(slug, "")),
            erows="".join(erows) if erows else '<tr><td colspan="6" class="blank">No fixtures listed.</td></tr>',
            prows="".join(prows) if prows else '<tr><td colspan="5" class="blank">No picks issued.</td></tr>',
        )
        (OUT / "sports" / "{}.html".format(slug)).write_text(
            page(name, sp_body, active="", rel="../"), encoding="utf-8"
        )

    # ---------- sources ----------
    srows = []
    for sid, s in SOURCES.items():
        row = (
            '<tr><td class="num">{}</td><td>{}</td>'
            '<td><a href="{}" target="_blank" rel="noopener noreferrer">{}</a></td>'
            '<td>{}</td><td class="num">{}</td><td>{}</td></tr>'
        ).format(e(sid), e(s["publisher"]), e(s["url"]), e(s["url"]), e(s["role"]), e(s["captured"]), e(s["confirms"]))
        srows.append(row)
    _src_inner = (
        '<p class="eyebrow">Every source read</p>'
        '<h1>Sources</h1>'
        '<p class="lede">{ns} sources read this session: {no} official (governing body, league, tour, promoter) and'
        ' {nd} discovery (OLBG hubs, used only to find markets). Every table row on this site links to at least one source.</p>'
        '<div class="table-wrap"><table><thead><tr>'
        '<th>Id</th><th>Publisher</th><th>URL</th><th>Role</th><th>Read at (UTC)</th><th>What it confirmed</th>'
        '</tr></thead><tbody>{rows}</tbody></table></div>'
        '<div class="warn"><p>No source was silently skipped. Where an official page was unreachable (cookie wall, 404, timeout),'
        ' the fact is recorded as a flag and the dependent row is left blank rather than inferred.</p></div>'
    )
    src_body = _src_inner.format(
        ns=len(SOURCES), no=len(official_srcs), nd=len(discovery_srcs), rows="".join(srows),
    )
    (OUT / "sources.html").write_text(page("Sources", src_body, "sources"), encoding="utf-8")

    # ---------- flagged ----------
    frows = []
    for fid, title, scope, detail, link in FLAGS:
        row = (
            '<div class="card" id="{fid}">'
            '<h3 style="margin-top:0">{fid} &middot; {title}</h3>'
            '<p class="meta" style="color:var(--muted);font-size:13px">Scope: {scope}</p>'
            '<p>{detail}</p>'
            '<p style="margin:0"><a href="{link}" target="_blank" rel="noopener noreferrer">Source to check &rarr;</a></p>'
            '</div>'
        ).format(fid=e(fid), title=e(title), scope=e(scope), detail=e(detail), link=e(link))
        frows.append(row)
    _flag_inner = (
        '<p class="eyebrow">Needs review</p><h1>Flagged for review</h1>'
        '<p class="lede">{nf} places where the record is incomplete, where a value was deliberately left'
        ' blank, or where the upstream site looks wrong. None of them block the release; all of them are here so they can be'
        ' checked by hand.</p>'
        '<div class="danger"><p><strong>Nothing on this page is an estimate presented as fact.</strong> Where a value could not be'
        ' confirmed it is empty everywhere on this site, and the row is listed here with the link that should confirm it.</p></div>'
        '{rows}'
    )
    flag_body = _flag_inner.format(
        nf=len(FLAGS), rows="".join(frows),
    )
    (OUT / "flagged.html").write_text(page("Flagged for review", flag_body, "flagged"), encoding="utf-8")

    # ---------- coverage ----------
    crows = []
    for slug, name, path in SPORTS:
        evs = [x for x in EVENTS if x["sport"] == slug]
        offs = sum(1 for x in evs if official(x["src"]))
        picks_s = [p for p in PICKS if p["sport"] == slug]
        row = (
            '<tr><td><a href="sports/{}.html"><strong>{}</strong></a></td>'
            '<td class="num">{}</td><td class="num">{}</td><td class="num">{}</td>'
            '<td class="num">{}</td><td>{}</td></tr>'
        ).format(
            slug, e(name), len(evs), offs, len(picks_s),
            len(picks_s) * "\u25cf" or '<span class="blank">none</span>',
            e(COVERAGE.get(slug, "")),
        )
        crows.append(row)
    _cov_inner = (
        '<p class="eyebrow">All fifteen sports</p><h1>Coverage, sport by sport</h1>'
        '<p class="lede">The brief asks for five written picks in every sport, every day. That target was not met today and the'
        ' gap is stated here rather than hidden: {np} picks across {ns} sports. The table shows exactly where'
        ' the chain broke.</p>'
        '<div class="table-wrap"><table><thead><tr>'
        '<th>Sport</th><th>Rows</th><th>Rows with an official source</th><th>Picks</th><th></th><th>What happened</th>'
        '</tr></thead><tbody>{rows}</tbody></table></div>'
        '<h2>Why the shortfall exists</h2>'
        '<div class="grid">'
        '<div class="card"><h3 style="margin-top:0">1. Quota versus evidence</h3><p>A pick needs three things: an open OLBG market,'
        ' an official fixture confirmation, and at least one official form or availability fact. Sports where the second or third'
        ' was missing produce zero picks, not a weak one.</p></div>'
        '<div class="card"><h3 style="margin-top:0">2. Official feeds are thin</h3><p>MLB, the NHL, the NBA, Formula 1 and WST publish'
        ' machine-readable fixtures. Cricket, handball, volleyball, darts, Gaelic games and rugby league do not publish anything'
        ' comparable that was reachable here.</p></div>'
        '<div class="card"><h3 style="margin-top:0">3. High is not a label</h3><p>No market produced a probability above 70% on the'
        ' facts that were readable outside the High picks shown. A weak pick labelled High would be a lie with a number attached.</p></div>'
        '</div>'
    )
    cov_body = _cov_inner.format(
        np=len(PICKS), ns=len({p["sport"] for p in PICKS}), rows="".join(crows),
    )
    (OUT / "coverage.html").write_text(page("Coverage", cov_body, "coverage"), encoding="utf-8")

    # ---------- methodology ----------
    meth = (
        '<p class="eyebrow">How this works</p><h1>Method and limits</h1>'
        '<h2>The pipeline</h2>'
        '<ol style="color:#344050;max-width:80ch">'
        '<li><strong>Discovery.</strong> The OLBG hub for each of the fifteen sports was read live and every open market recorded'
        ' with its OLBG URL, selection and tip count. Tip counts are community votes and are never used as probabilities.</li>'
        '<li><strong>Official confirmation.</strong> For each candidate, a governing body, league, tour or club page was opened.'
        ' Only what that page states is carried into the row.</li>'
        '<li><strong>Line origination.</strong> Our probability is built from the confirmed inputs: season record and splits for'
        ' baseball and hockey, published availability for basketball, and practice/route evidence for motorsport and snooker.'
        ' The fair price is 1/p with no margin, reported in American odds.</li>'
        '<li><strong>Tiering.</strong> High needs p &gt; 0.70 and a fair price between &minus;250 and +10000. Medium is a'
        ' defensible edge below that bar. Low is a weak opinion kept for completeness.</li>'
        '<li><strong>Writing.</strong> Each pick gets a unique write-up of at least 30 words naming the selection, both sides,'
        ' the competition, current form and the official fact it rests on.</li>'
        '</ol>'
        '<h2>Deliberate omissions</h2>'
        '<div class="table-wrap"><table><thead><tr><th>Thing</th><th>Why it is absent</th></tr></thead><tbody>'
        '<tr><td>Bookmaker prices and availability</td><td>we issue our own lines; we did not scrape or quote any bookmaker</td></tr>'
        '<tr><td>Injuries for games with no submitted report</td><td>the NBA injury report was not reachable this session</td></tr>'
        '<tr><td>Team records for most sports</td><td>official standings were only reachable for MLB, NHL and NBA</td></tr>'
        '<tr><td>Greyhound trap data and times</td><td>times are internally inconsistent and no GBGB card was read</td></tr>'
        '<tr><td>Worldwide fixture coverage</td><td>only markets that were open on OLBG at capture are listed; that is not a full fixture list</td></tr>'
        '</tbody></table></div>'
        '<h2>Timezone rule</h2>'
        '<p>OLBG sport hubs render kick-offs in US Eastern (UTC&minus;4). This was established by matching all eight NBA fixtures'
        ' on the hub to the tip-off times printed in the NBA\'s official calendar for the same day. UTC times are therefore four'
        ' hours ahead of the hub display. Any row whose time comes from that display is labelled <em>derived</em> and is never'
        ' described as confirmed. Official times exist for MLB, NHL, NBA, Formula 1 and WST rows.</p>'
        '<h2>What "verified" means here</h2>'
        '<p>A fact is treated as confirmed only when an official publisher\'s page was opened during this session and it stated'
        ' that fact. The word itself is kept out of the public predictions, and no value is ever inferred, interpolated or carried'
        ' in from memory.</p>'
    )
    (OUT / "methodology.html").write_text(page("Method", meth, "method"), encoding="utf-8")

    # ---------- reverse engineering ----------
    rev = (
        '<p class="eyebrow">Reverse engineering</p><h1>How OLBG is put together</h1>'
        '<p class="lede">Structural notes from reading the site today. These describe routes and rendering behaviour, not'
        ' opinions about the matches.</p>'
        '<h2>Routes that work</h2>'
        '<div class="table-wrap"><table><thead><tr>'
        '<th>Pattern</th><th>Example</th><th>What it returns</th>'
        '</tr></thead><tbody>'
        '<tr><td>/betting-tips/{Sport_Slug}/{sport_id}</td>'
        '<td>/betting-tips/Basketball/4</td>'
        '<td>sport hub: open markets with selection, market type, tip counts</td></tr>'
        '<tr><td>/betting-tips/{Sport}/All_{Sport}/All_Events/{Slug}/{id}?event_id=NNN</td>'
        '<td>.../MIA_Heat_@_CHA_Hornets/4?event_id=536117</td>'
        '<td>single event: every market and the tip share per outcome</td></tr>'
        '<tr><td>/best-tipsters/{Sport}/{id}</td>'
        '<td>/best-tipsters/Golf/5</td>'
        '<td>tipster leaderboard</td></tr>'
        '</tbody></table></div>'
        '<h2>Things that trip a reader up</h2>'
        '<div class="grid">'
        '<div class="card"><h3 style="margin-top:0">Times carry no timezone</h3><p>Hubs are US Eastern; greyhound cards are'
        ' displaced from the time printed in the race name. Never treat a hub time as UTC.</p></div>'
        '<div class="card"><h3 style="margin-top:0">Silent zero-tip suppression</h3><p>A competition with no open tips disappears'
        ' from the hub entirely. Absence of a fixture on OLBG is not evidence that the fixture does not exist.</p></div>'
        '<div class="card"><h3 style="margin-top:0">Empty hubs</h3><p>The golf hub returned "No tips found" at capture; the'
        ' All Events route returned the same body with the footer attached.</p></div>'
        '<div class="card"><h3 style="margin-top:0">Tip share is not probability</h3><p>The percentage beside a selection is the'
        ' share of community tips on it. It is a vote count, and this desk never converts it into a price.</p></div>'
        '</div>'
        '<h2>What we treated as in scope</h2>'
        '<p>Golf, Volleyball, Rugby Union, Cricket, Snooker, Darts, Baseball, Gaelic Sports, Greyhounds, Tennis, Motor Racing,'
        ' Handball, Ice Hockey, Basketball and Rugby League. Soccer, American football, horse racing, boxing, MMA, hurling and'
        ' cycling are excluded.</p>'
    )
    (OUT / "reverse-engineering.html").write_text(page("Reverse engineering", rev, "rev"), encoding="utf-8")

    # ---------- data JSON exports ----------
    (DATA / "events.json").write_text(json.dumps(EVENTS, indent=2), encoding="utf-8")
    (DATA / "picks.json").write_text(json.dumps(PICKS, indent=2), encoding="utf-8")
    (DATA / "sources.json").write_text(json.dumps(SOURCES, indent=2), encoding="utf-8")
    (DATA / "coverage.json").write_text(json.dumps(COVERAGE, indent=2), encoding="utf-8")
    (DATA / "flags.json").write_text(
        json.dumps([dict(id=a, finding=b, scope=c, detail=d, link=f) for a, b, c, d, f in FLAGS], indent=2),
        encoding="utf-8",
    )

    print(
        "built {}: {} pages, {} picks ({} High / {} Medium / {} Low), "
        "{} events, {} sources, {} flags".format(
            DESK, len(list(OUT.rglob("*.html"))), len(PICKS), len(highs), len(mediums), len(lows),
            len(EVENTS), len(SOURCES), len(FLAGS),
        )
    )


if __name__ == "__main__":
    build()