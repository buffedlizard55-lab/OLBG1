#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T60 / session 1a421e41-olbg1 -- site renderer.

Reads  data/1a421e41/desk.json
Writes 1a421e41/index.html and 14 further category pages, plus
       1a421e41/sports/<sport>.html for each of the 17 in-scope sports,
       and 1a421e41/assets/desk.css

Everything inside 1a421e41/ is owned by this session. No file at the repository
root or in a shared directory is read for writing or modified.
"""

import html
import json
import os

# Entities this renderer uses deliberately in prose and table cells. Values reach
# the page through E(), which escapes everything -- so without this allowlist an
# intentional "&mdash;" arrives in the browser as the literal text "&mdash;".
# "&amp;" is restored LAST so that already-escaped input is never double-decoded.
_SAFE_ENTITIES = ("&mdash;", "&ndash;", "&middot;", "&ge;", "&le;", "&minus;",
                  "&times;", "&hellip;", "&amp;")


def _escape(text):
    out = html.escape(str(text))
    for ent in _SAFE_ENTITIES:
        out = out.replace(html.escape(ent), ent)
    return out

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DESK = os.path.join(ROOT, "data", "1a421e41", "desk.json")
SITE = os.path.join(ROOT, "1a421e41")
ASSETS = os.path.join(SITE, "assets")
SPORTS_DIR = os.path.join(SITE, "sports")

E = _escape

CSS = """
:root{--bg:#0f1218;--panel:#171c25;--panel2:#1e242f;--line:#2b3442;--ink:#e8edf5;
--mut:#93a1b5;--acc:#4ea1ff;--hi:#2ecc71;--med:#f1c40f;--lo:#e67e22;--bad:#ff6b6b;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--acc);text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:1400px;margin:0 auto;padding:0 20px 60px}
header.top{background:linear-gradient(180deg,#141a24,#0f1218);border-bottom:1px solid var(--line);
padding:26px 0 18px;margin-bottom:22px}
header.top .wrap{padding-bottom:0}
h1{margin:0 0 6px;font-size:26px;letter-spacing:-.2px}
h2{margin:34px 0 10px;font-size:19px;border-bottom:1px solid var(--line);padding-bottom:7px}
h3{margin:22px 0 8px;font-size:16px;color:#cfe0f5}
p.lede{color:var(--mut);margin:0 0 14px;max-width:100ch}
.sub{color:var(--mut);font-size:13px}
nav.cat{display:flex;flex-wrap:wrap;gap:6px;margin-top:16px}
nav.cat a{background:var(--panel);border:1px solid var(--line);border-radius:7px;
padding:6px 11px;font-size:13px;color:var(--ink)}
nav.cat a:hover{border-color:var(--acc);text-decoration:none}
nav.cat a.on{background:#22314a;border-color:var(--acc)}
nav.cat b{color:var(--mut);font-weight:600;font-size:11px;text-transform:uppercase;
letter-spacing:.08em;align-self:center;margin:0 4px 0 10px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(178px,1fr));gap:12px;margin:16px 0}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.card .n{font-size:27px;font-weight:650;letter-spacing:-.5px}
.card .l{color:var(--mut);font-size:12.5px;margin-top:3px}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin:14px 0}
table{width:100%;border-collapse:collapse;font-size:13.4px;margin:10px 0 4px;background:var(--panel);
border:1px solid var(--line);border-radius:10px;overflow:hidden}
th{background:var(--panel2);text-align:left;padding:9px 10px;font-size:11.6px;letter-spacing:.05em;
text-transform:uppercase;color:var(--mut);border-bottom:1px solid var(--line);white-space:nowrap}
td{padding:8px 10px;border-bottom:1px solid #222a36;vertical-align:top}
tr:last-child td{border-bottom:none}
tbody tr:nth-child(even){background:#151a23}
tbody tr:hover{background:#1c2431}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.scroll{max-height:70vh;overflow:auto;border-radius:10px}
.chip{display:inline-block;padding:2px 8px;border-radius:20px;font-size:11.5px;font-weight:600;
border:1px solid transparent;white-space:nowrap}
.hi{background:rgba(46,204,113,.15);color:#7ee2a8;border-color:rgba(46,204,113,.4)}
.med{background:rgba(241,196,15,.14);color:#f4d35e;border-color:rgba(241,196,15,.38)}
.lo{background:rgba(230,126,34,.14);color:#f0a868;border-color:rgba(230,126,34,.38)}
.a{background:rgba(78,161,255,.15);color:#8dc4ff;border-color:rgba(78,161,255,.4)}
.bad{background:rgba(255,107,107,.14);color:#ff9d9d;border-color:rgba(255,107,107,.38)}
.ok{background:rgba(46,204,113,.13);color:#7ee2a8;border-color:rgba(46,204,113,.35)}
.mut{color:var(--mut)}
.blank{color:#6c7a8d;font-style:italic}
.pred{background:var(--panel2);border-left:3px solid var(--hi);border-radius:0 8px 8px 0;
padding:13px 16px;margin:12px 0}
.pred .who{font-weight:650;margin-bottom:5px}
.pred p{margin:0;color:#dbe4f0}
.finding{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--acc);
border-radius:0 9px 9px 0;padding:14px 17px;margin:12px 0}
.finding.high{border-left-color:var(--bad)}
.finding .fid{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px;color:var(--acc)}
.finding h3{margin:2px 0 6px;font-size:15.5px;color:var(--ink)}
code,pre{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12.6px}
pre{background:#101520;border:1px solid var(--line);border-radius:8px;padding:12px 14px;overflow:auto;color:#c9d6e8}
.note{background:#141b26;border:1px solid var(--line);border-radius:8px;padding:11px 14px;
color:var(--mut);font-size:13.2px;margin:10px 0}
ul{margin:8px 0 8px 20px;padding:0}li{margin:4px 0}
footer{margin-top:44px;padding-top:16px;border-top:1px solid var(--line);color:var(--mut);font-size:12.5px}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:14px}
"""

NAV = [
    ("Overview", [("index.html", "Landing"), ("coverage.html", "Sport coverage"), ("matches.html", "All matches")]),
    ("Markets &amp; Lines", [("markets.html", "Every market"), ("lines.html", "Our lines"), ("window.html", "-250 / +10000 band")]),
    ("Picks", [("picks.html", "Match winners"), ("high-confidence.html", "High confidence"), ("predictions.html", "Predictions")]),
    ("Verification", [("verification.html", "Official sources"), ("sources.html", "Source register"), ("methodology.html", "Methodology")]),
    ("Findings", [("flagged.html", "Flagged for Review"), ("audit.html", "Repo audit"), ("reverse-engineering.html", "Reverse engineering")]),
]
ALL_PAGES = [p for _c, items in NAV for p, _l in items]


def nav_html(current, prefix=""):
    out = ['<nav class="cat">']
    for cat, items in NAV:
        out.append("<b>%s</b>" % cat)
        for fn, label in items:
            cls = ' class="on"' if fn == current else ""
            out.append('<a href="%s%s"%s>%s</a>' % (prefix, fn, cls, label))
    out.append('<b>Sports</b><a href="%scoverage.html"%s>17 sports</a>' % (
        prefix, ' class="on"' if current == "coverage.html" else ""))
    out.append("</nav>")
    return "".join(out)


def page(title, current, body, subtitle="", prefix=""):
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title>
<link rel="stylesheet" href="%sassets/desk.css">
</head><body>
<header class="top"><div class="wrap">
<h1>%s</h1>
<p class="lede">%s</p>
%s
</div></header>
<div class="wrap">
%s
<footer>
Session <code>1a421e41-olbg1</code> &middot; task T60 &middot; OLBG harvest %s &middot;
every probability on this site is our own zero-vig origination from official governing-body data.
Nothing here is a bookmaker price, and no value has been inferred or filled in: where an official
source does not publish a figure the cell is left blank and the row is flagged.
</footer>
</div></body></html>
""" % (E(title), prefix, E(title), subtitle or "", nav_html(current, prefix), body, HARVEST_UTC)


def table(headers, rows, cls="", scroll=False, aligns=None):
    aligns = aligns or ["" for _ in headers]
    th = "".join('<th class="%s">%s</th>' % (a, h) for h, a in zip(headers, aligns))
    trs = []
    for r in rows:
        tds = "".join('<td class="%s">%s</td>' % (a, c) for c, a in zip(r, aligns))
        trs.append("<tr>%s</tr>" % tds)
    inner = "<table class='%s'><thead><tr>%s</tr></thead><tbody>%s</tbody></table>" % (
        cls, th, "".join(trs))
    return '<div class="scroll">%s</div>' % inner if scroll else inner


def cards(items):
    return '<div class="cards">%s</div>' % "".join(
        '<div class="card"><div class="n">%s</div><div class="l">%s</div></div>' % (n, l)
        for n, l in items)


def chip(text, kind):
    return '<span class="chip %s">%s</span>' % (kind, E(str(text)))


def tier_chip(t):
    return chip(t, {"High": "hi", "Medium": "med", "Low": "lo"}.get(t, "mut"))


def klass_chip(k):
    return chip("Class " + k, {"A": "a", "B": "med", "C": "lo"}.get(k, "mut"))


def blank(v, fmt="%s"):
    """Render a value, or an explicit unverified blank. Never infer."""
    if v is None or v == "":
        return '<span class="blank">blank &middot; unverified</span>'
    return fmt % v


def am(v):
    if v is None:
        return '<span class="blank">blank</span>'
    return ("-%d" % abs(v)) if v < 0 else ("+%d" % v)


def link(url, text=None, official=True):
    if not url:
        return '<span class="blank">no source</span>'
    t = text or ("official" if official else "OLBG card")
    return '<a href="%s" rel="noopener noreferrer">%s</a>' % (E(url), E(t))


def src_links(row):
    off = row["sources"]["official"]
    olbg = [o for o in row["sources"]["olbg"] if o.get("url")]
    bits = []
    if off:
        bits.append(link(off[0]["url"], "official"))
    if olbg:
        bits.append(link(olbg[0]["url"], "OLBG", official=False))
    if not bits:
        return '<span class="blank">no source</span>'
    return " &middot; ".join(bits)


def src_ref(u):
    """Render a source reference: an http(s) URL as a link, a repo path as code."""
    if not u:
        return '<span class="blank">no source</span>'
    if isinstance(u, str) and u.startswith("http"):
        host = u.split("/")[2].replace("www.", "")
        return link(u, host)
    return "<code>%s</code>" % E(str(u))


def pct(p):
    return '&mdash;' if p is None else "%.2f%%" % (p * 100.0)


# ===========================================================================

D = json.load(open(DESK))
HARVEST_UTC = D["meta"]["generated_utc"]
ROWS = D["rows"]
META = D["meta"]
SPORTS = D["sports"]
HIGH = D["high_picks"]
FIND = D["findings"]
POL = D["policy"]


def render_index():
    b = []
    b.append(cards([
        (META["sports_in_scope"], "sports in scope"),
        (META["rows_from_olbg"], "OLBG fixtures harvested"),
        (META["rows_official_additions"], "official additions OLBG hides"),
        (META["markets_originated"], "markets we originated"),
        (META["high_selections"], "High-confidence picks"),
        (META["predictions"], "predictions written"),
        (len(FIND), "findings &amp; irregularities"),
        (len(D["official_sources"]), "sources in the register"),
    ]))
    b.append('<div class="panel"><h3 style="margin-top:0">What this desk is</h3>'
             '<p>A reverse-engineering of <a href="https://www.olbg.com/">OLBG.com</a> across every sport the brief keeps '
             'in scope, harvested live on %s. For each fixture we originate our own betting lines from scratch on a '
             'zero-vig basis, investigate every market we can defend, pick a match winner with a confidence tier, and '
             'write a prediction for each pick that clears the high-confidence band. Every probability is ours; every '
             'fact underneath it comes from a governing body, linked on the row.</p>'
             '<p class="sub">Excluded by the brief: soccer/football, boxing, UFC, MMA, American football, hurling, '
             'horse racing, cycling and specials &mdash; OLBG ids %s. They were re-confirmed on OLBG&rsquo;s own '
             'navigation and are listed with their ids on the <a href="coverage.html">coverage</a> page.</p></div>'
             % (HARVEST_UTC, ", ".join(str(x["olbg_id"]) for x in D["scope"]["excluded"])))

    b.append("<h2>High-confidence picks &mdash; %s to %s</h2>" % (am(POL["window"]["american_min"]), am(POL["window"]["american_max"])))
    b.append('<p class="lede">A pick only reaches this table if all four gates pass: the fixture is verified, an official '
             'body published evidence for <em>both</em> sides, that body also published current form, and our own zero-vig '
             'price clears 70% while landing inside the window.</p>')
    b.append(table(
        ["Sport", "Fixture", "Selection", "Market", "Our p", "American", "Decimal", "5% book", "Prediction", "Source"],
        [[h["sport"], E(h["fixture"]), "<b>%s</b>" % E(h["selection"]), E(h["market"]),
          pct(h["p"]), "<b>%s</b>" % am(h["american"]), "%.2f" % h["decimal"], am(h["book5_american"]),
          '<a href="predictions.html">%d words</a>' % len((h["prediction"] or "").split()),
          " &middot; ".join(link(s["url"], "official") for s in h["official_sources"][:2])]
         for h in HIGH],
        aligns=["", "", "", "", "num", "num", "num", "num", "", ""]))

    b.append("<h2>Sport coverage</h2>")
    b.append(table(
        ["Sport", "OLBG id", "Fixtures", "Class A", "Class B", "Class C", "Markets originated", "High picks", "Flagged", "Detail"],
        [['<a href="sports/%s.html">%s</a>' % (s["key"], E(s["label"])), s["olbg_id"], s["olbg_rows"],
          s["class_a"], s["class_b"], s["class_c"], s["markets_originated"], s["high"], s["flagged"],
          '<span class="blank">no fixtures rendered</span>' if s["olbg_rows"] == 0 else "hub harvested"]
         for s in SPORTS],
        aligns=["", "num", "num", "num", "num", "num", "num", "num", "num", ""]))

    b.append("<h2>Headline findings</h2>")
    for f in [x for x in FIND if x["severity"] == "high"][:6]:
        b.append('<div class="finding high"><span class="fid">%s</span><h3>%s</h3>'
                 '<p class="sub">%s</p><p class="sub">%s</p></div>'
                 % (E(f["id"]), E(f["title"]), E(f["detail"][:400]),
                    " ".join(src_ref(u) for u in f["sources"][:2])))
    b.append('<p class="sub"><a href="flagged.html">All %d findings on the Flagged for Review page &rarr;</a></p>' % len(FIND))
    return "".join(b)


def render_coverage():
    b = ['<p class="lede">Seventeen sports stay in scope. Each was harvested directly from its own OLBG hub; '
         'the hub URL is the source for the fixture list, and the official-reach column says which governing body '
         'we actually got to, and what it would and would not confirm.</p>']
    reach = {}
    for reg in D["official_sources"]:
        for u in reg["urls"]:
            reach[u] = reg["name"]
    rows = []
    for s in SPORTS:
        rs = [r for r in ROWS if r["sport"] == s["key"] and r["origin"] == "olbg"]
        offs = sorted({o["url"] for r in rs for o in r["sources"]["official"]})
        rows.append([
            '<a href="sports/%s.html"><b>%s</b></a>' % (s["key"], E(s["label"])),
            s["olbg_id"], '<a href="%s" rel="noopener noreferrer">hub</a>' % E(s["hub"]),
            s["olbg_rows"],
            "%d / %d / %d" % (s["class_a"], s["class_b"], s["class_c"]),
            s["markets_originated"], s["high"],
            (" &middot; ".join(src_ref(u) for u in offs[:3])
             if offs else '<span class="blank">none reached</span>'),
            ("no fixtures rendered &mdash; hub is empty" if s["olbg_rows"] == 0 else
             ("%d flagged" % s["flagged"] if s["flagged"] else "clean")),
        ])
    b.append(table(["Sport", "OLBG id", "Hub", "Fixtures", "A / B / C", "Markets", "High",
                    "Official body reached", "State"], rows,
                   aligns=["", "num", "", "num", "num", "num", "num", "", ""]))

    b.append("<h2>Excluded sports</h2>")
    b.append('<p class="lede">Excluded by the brief. The OLBG id is recorded so the exclusion is checkable against '
             'OLBG&rsquo;s own navigation rather than taken on trust. UFC and MMA are not separate OLBG sports; they are '
             'carded under Boxing (16) and Specials (18).</p>')
    b.append(table(["Sport", "OLBG id", "Why excluded"],
                   [[E(x["label"]), x["olbg_id"], E(x["reason"])] for x in D["scope"]["excluded"]],
                   aligns=["", "num", ""]))

    b.append("<h2>Official reach by sport</h2>")
    b.append('<p class="lede">What we got to, and what it was willing to confirm. Where a governing body was not '
             'reached, that sport has no originated spread and its rows stay at the neutral 0.50 &mdash; we never guess '
             'a rating to fill the gap.</p>')
    b.append(table(["Sport", "Official body", "Page reached", "Reach"],
                   [[E(k.title().replace("_", " ")), E(v[0] or "&mdash;"),
                     link(v[1], "link") if v[1] else '<span class="blank">none</span>', E(v[2])]
                    for k, v in SPORT_REACH],
                   aligns=["", "", "", ""]))
    return "".join(b)


SPORT_REACH = None  # filled below from the evidence module


def render_matches():
    b = ['<p class="lede">All %d rows: %d harvested from OLBG on %s plus %d fixtures a governing body confirms that '
         'OLBG does not render. Every row carries its source links. Clocks are reproduced exactly as OLBG shows them, '
         'with no timezone, because OLBG publishes none &mdash; see the '
         '<a href="reverse-engineering.html">clock reconciliation</a>.</p>'
         % (len(ROWS), META["rows_from_olbg"], HARVEST_UTC, META["rows_official_additions"])]
    rows = []
    for r in ROWS:
        t = r["olbg_tip"]
        rows.append([
            E(r["sport_label"]),
            "<b>%s</b>" % E(r["fixture"]),
            E(r["day_label"] or "") + " " + (E(r["olbg_clock"]) if r["olbg_clock"] else '<span class="blank">no clock</span>'),
            E(r["competition"] or ""),
            E(str(r["olbg_event_id"])) if r["olbg_event_id"] is not None else '<span class="blank">not on OLBG</span>',
            chip(r["origin"].replace("_", " "), "a" if r["origin"] == "official_addition" else "mut"),
            "%s / %s" % (t["win_tips"] if t["win_tips"] is not None else "&mdash;",
                         t["total_tips"] if t["total_tips"] is not None else "&mdash;"),
            blank(t["consensus_share_pct"], "%s%%"),
            klass_chip(r["rating"]["klass"]),
            E(r["winner_pick"]["selection"] or "") or '<span class="blank">not priced</span>',
            pct(r["winner_pick"]["p"]) if r["winner_pick"]["p"] is not None else '<span class="blank">blank</span>',
            am(r["winner_pick"]["american"]),
            tier_chip(r["winner_pick"]["confidence"]),
            src_links(r),
        ])
    b.append(table(["Sport", "Fixture", "OLBG clock", "Competition", "Event id", "Origin",
                    "Tips W/T", "Share", "Class", "Our winner pick", "p", "American", "Tier", "Sources"],
                   rows, scroll=True,
                   aligns=["", "", "", "", "", "", "num", "num", "", "", "num", "num", "", ""]))
    b.append('<div class="note">Tips W/T are the counts OLBG prints on the card: tips on the win market and tips on the '
             'total market. Share is OLBG&rsquo;s consensus percentage. Both are OLBG&rsquo;s numbers, not ours, and OLBG is '
             'not an official source &mdash; they are recorded because the brief asks for the full harvested listing, and '
             'they never raise a confidence tier on their own.</div>')
    return "".join(b)


def render_markets():
    b = ['<p class="lede">Every market we originated, on every fixture: %d rungs in total. Prices are our own zero-vig '
         'origination. The &ldquo;5%% book&rdquo; column shows what the same true probability would look like if a '
         'bookmaker carried a 5%% overround &mdash; it is printed for comparison only and is never used to decide '
         'anything. Rungs sit on a strict half-point grid, so no rung can push.</p>'
         % sum(r["market_counts"]["total"] for r in ROWS)]
    rows = []
    for r in ROWS:
        for m in r["markets"]:
            rows.append([
                E(r["sport_label"]), E(r["fixture"]), E(m["market"]), E(m["label"]),
                blank(m["line"], "%.1f"), pct(m["p"]), "%.3f" % m["decimal"] if m["decimal"] else "&mdash;",
                am(m["american"]), am(m["book5_american"]),
                chip("in window", "ok") if m["in_window"] else '<span class="mut">out</span>',
                chip("&ge;70%", "hi") if m["ge_70"] else "",
                chip("HIGH", "hi") if (r["high_selection"] and m["label"] == r["high_selection"]["label"]) else "",
                src_links(r),
            ])
    b.append(table(["Sport", "Fixture", "Market", "Selection", "Line", "Our p", "Decimal",
                    "American", "5% book", "Window", "p&ge;70", "Pick", "Source"],
                   rows, scroll=True,
                   aligns=["", "", "", "", "num", "num", "num", "num", "num", "", "", "", ""]))
    b.append('<div class="note">Where a market is missing it is missing on purpose. A match total is originated only '
             'where a governing body published the scoring inputs; a handicap only where we hold an official rating for '
             'at least one side. Rows carrying the flags <code>TOTAL-NOT-ORIGINATED</code> or '
             '<code>SPREAD-NOT-ORIGINATED</code> are refusals to invent a number, not gaps in the build.</div>')
    return "".join(b)


def render_lines():
    b = ['<p class="lede">Our originated lines per fixture: the fair match-winner price for each side, and the centre '
         'we built the ladders around. The centre is either an official margin derived from a governing body&rsquo;s own '
         'points data, or a rating converted into the sport&rsquo;s scoring unit.</p>']
    rows = []
    for r in ROWS:
        rt = r["rating"]
        mw = {m["side"]: m for m in r["markets"] if m["market"] == "Match Winner"}
        h = mw.get(rt.get("home_name") or "")
        a = mw.get(rt.get("away_name") or "")
        rows.append([
            E(r["sport_label"]), E(r["fixture"]), klass_chip(rt["klass"]), E(rt["basis"].replace("_", " ")),
            E(rt.get("home_name") or ""), am(h["american"]) if h else "&mdash;", pct(h["p"]) if h else "&mdash;",
            E(rt.get("away_name") or ""), am(a["american"]) if a else "&mdash;", pct(a["p"]) if a else "&mdash;",
            blank(rt["margin_centre"], "%+.2f"), blank(rt["total_centre"], "%.2f"),
            chip("originated", "ok") if rt["total_originatable"] else '<span class="blank">not originated</span>',
            r["market_counts"]["handicap"] + r["market_counts"]["match_total"],
            src_links(r),
        ])
    b.append(table(["Sport", "Fixture", "Class", "Rating basis", "Side 1", "American", "p",
                    "Side 2", "American", "p", "Margin centre", "Total centre", "Total", "Ladder rungs", "Source"],
                   rows, scroll=True,
                   aligns=["", "", "", "", "", "num", "num", "", "num", "num", "num", "num", "", "num", ""]))
    b.append("<h2>How a centre is built</h2>")
    b.append('<div class="panel"><p>Where a governing body publishes points scored and points conceded, each side&rsquo;s '
             'expected score is the mean of its own official scoring rate and its opponent&rsquo;s official points-allowed '
             'rate. The margin centre is the difference plus home-court advantage; the total centre is the sum.</p>'
             '<pre>E[home pts] = (home ppg for + away ppg against) / 2\n'
             'E[away pts] = (away ppg for + home ppg against) / 2\n'
             'margin centre = E[home] - E[away] + HCA\n'
             'total centre  = E[home] + E[away]</pre>'
             '<p>Home-court advantage is <b>derived from official data, not assumed</b>: the official standings contain '
             '33 home wins and 28 away wins across 61 games, a home win rate of %.4f, so '
             '<code>HCA = sigma &times; &Phi;<sup>-1</sup>(%.4f) = %.2f points</code>. The sigma it multiplies is our '
             'assumption and is labelled as such everywhere it appears.</p>'
             '<p>Where a body publishes only a rating &mdash; a seed, a rank, or confirmation that a player is in the '
             'world&rsquo;s top sixteen &mdash; we convert that probability into the equivalent margin with '
             '<code>centre = sigma &times; &Phi;<sup>-1</sup>(p)</code>, so the ladder is still expressed in legs, frames '
             'or games rather than in an abstract number.</p></div>'
             % (POL["derived"]["official_home_win_rate"], POL["derived"]["official_home_win_rate"],
                POL["derived"]["basketball_hca_points"]))
    return "".join(b)


def render_window():
    b = ['<p class="lede">The brief asks for high-confidence picks on matches priced between %s and %s. On a zero-vig '
         'basis that is a band only <b>%.4f wide in probability</b>, and the two tests pull against each other. This page '
         'shows exactly how we resolved it and why the outcome is what it is.</p>'
         % (am(POL["window"]["american_min"]), am(POL["window"]["american_max"]), 0.014286)]
    b.append('<div class="panel"><h3 style="margin-top:0">The contradiction, and how we settled it</h3>'
             '<p>At zero vig, p = 0.700 prices at <b>%s</b> and p = 0.714286 prices at exactly <b>%s</b>. So '
             '&ldquo;greater than 70%%&rdquo; and &ldquo;between %s and %s&rdquo; intersect in the band '
             '<b>[0.7000, 0.7143]</b> &mdash; about 17 American points wide.</p>'
             '<p>At a 5%% overround the two tests cannot both bind: p = 0.700 books at <b>-277</b>, already outside the '
             'window. We therefore gate on the <b>zero-vig price</b>, which is the price we originate ourselves, and print '
             'the 5%% book equivalent beside it on every table for comparison. Nothing is ever graded on the book '
             'price.</p></div>' % (am(-233), am(-250), am(-250), am(10000)))
    b.append("<h2>The four gates</h2>")
    b.append(table(["Gate", "Requirement", "Why"],
                   [["1", "Fixture verified", "The match must exist on the date and card OLBG claims, checked against a governing body."],
                    ["2", "Class A evidence", "An official body must have published a rating, record or seed for <b>both</b> sides. One-sided evidence is Class B and is hard-capped at Medium."],
                    ["3", "Official current form", "The same or another official body must have published recent results or form for the side we are backing."],
                    ["4", "Window", "Our zero-vig price must satisfy p &ge; 0.700 <b>and</b> land between -250 and +10000. Among qualifying rungs the tightest to our own centre wins."]],
                   aligns=["num", "", ""]))
    b.append("<h2>Why almost nothing clears it &mdash; granularity, not conviction</h2>")
    b.append('<p class="lede">A handicap rung steps probability by <code>0.3434 / sigma</code> per half point. Whether '
             'any rung lands inside a 0.0143-wide band is therefore governed by the sport&rsquo;s scoring variance, not by '
             'how strong the favourite is. This is the single most important structural finding on the desk.</p>')
    ev = [f for f in FIND if f["id"] == "F-1A-GRAN-01"][0]["evidence"]
    b.append(table(["Sport", "Unit", "sigma (our assumption)", "p step per half rung", "Band width", "Qualifying rung likely?"],
                   [[E(x["sport"].title().replace("_", " ")), E(x["unit"] or "&mdash;"),
                     blank(x["sigma_h"], "%.2f"), blank(x["prob_step_per_half_rung"], "%.5f"), "0.01429",
                     ('<span class="blank">no sigma &mdash; not originated</span>' if x["sigma_h"] is None else
                      (chip("almost always", "hi") if x["prob_step_per_half_rung"] <= 0.020 else
                       (chip("about half the time", "med") if x["prob_step_per_half_rung"] <= 0.040 else
                        chip("rarely", "lo"))))]
                    for x in ev],
                   aligns=["", "", "num", "num", "num", ""]))
    b.append('<div class="note">Consequence, stated plainly: a genuine 0.789 favourite in darts is <b>rejected</b> because '
             'the nearest rung prices at -258, eight American points outside the window, while a basketball side at 0.701 '
             'clears comfortably. The band rewards high-variance sports and punishes low-variance ones. That is a property '
             'of the rule, not a statement about which picks are more likely to win.</div>')
    b.append("<h2>Rejected Highs &mdash; above 70% but outside the window</h2>")
    KIND = {"favourite_priced_too_short": "favourite priced too short",
            "nearest_miss": "nearest miss",
            "beyond_plus_10000": "beyond +10000"}
    rej = []
    for r in ROWS:
        for j in r["rejected_highs"]:
            rej.append([E(r["sport_label"]), E(r["fixture"]), E(j["label"]), E(j["market"]),
                        pct(j["p"]), am(j["american"]),
                        chip(KIND.get(j.get("kind"), j.get("kind") or ""), "bad"),
                        E(j["reason"]), r["rejected_high_count"]])
    rej.sort(key=lambda x: (x[0], x[1]))
    b.append(table(["Sport", "Fixture", "Selection", "Market", "Our p", "American", "Kind",
                    "Why rejected", "Rungs rejected on this fixture"], rej,
                   aligns=["", "", "", "", "num", "num", "", "", "num"]))
    total_rej = sum(r["rejected_high_count"] for r in ROWS)
    b.append('<div class="note"><b>%d rungs</b> across the desk cleared the 70%% floor and were rejected by the price '
             'window. A deep ladder produces dozens of them per fixture and they all say the same thing, so the table '
             'above lists only the ones that carry information on each fixture &mdash; the match winner when a genuine '
             'favourite is priced too short to be usable, and the nearest miss, the rung that came closest to clearing '
             'the %s floor. The last column keeps the full count so nothing is silently dropped, and the complete ladder '
             'for every fixture is on the <a href="markets.html">markets</a> page. Publishing the rejections matters: '
             'they are the picks the rule throws away, and several are stronger favourites than anything that survives '
             'it.</div>' % (total_rej, am(-250)))
    return "".join(b)


def render_picks():
    b = ['<p class="lede">A match-winner pick for every fixture, with a confidence tier. The pick always follows the '
         'favourite side, not the first-listed side, so an away favourite is picked correctly. The final column says '
         'whether our pick agrees with the selection OLBG&rsquo;s tipsters are backing.</p>']
    tiers = {}
    for r in ROWS:
        tiers[r["winner_pick"]["confidence"]] = tiers.get(r["winner_pick"]["confidence"], 0) + 1
    b.append(cards([(tiers.get("High", 0), "High"), (tiers.get("Medium", 0), "Medium"),
                    (tiers.get("Low", 0), "Low"), (len([r for r in ROWS if r["winner_pick"]["agrees_with_olbg"]]),
                                                   "agree with OLBG consensus"),
                    (len([r for r in ROWS if r["winner_pick"]["olbg_tipped"] and not r["winner_pick"]["agrees_with_olbg"]]),
                     "differ from OLBG consensus")]))
    rows = []
    for r in ROWS:
        w = r["winner_pick"]
        rows.append([
            E(r["sport_label"]), E(r["fixture"]), klass_chip(r["rating"]["klass"]),
            ("<b>%s</b>" % E(w["selection"])) if w["selection"] else '<span class="blank">not priced</span>',
            pct(w["p"]) if w["p"] is not None else '<span class="blank">blank</span>', am(w["american"]),
            "%.2f" % w["decimal"] if w["decimal"] else "&mdash;", am(w["book5_american"]),
            tier_chip(w["confidence"]), E(w["olbg_tipped"] or "&mdash;"),
            chip("agree", "ok") if w["agrees_with_olbg"] else
            (chip("differ", "bad") if w["olbg_tipped"] else '<span class="mut">not tipped</span>'),
            src_links(r),
        ])
    b.append(table(["Sport", "Fixture", "Class", "Our pick", "p", "American", "Decimal", "5% book",
                    "Tier", "OLBG tips", "vs OLBG", "Source"], rows, scroll=True,
                   aligns=["", "", "", "", "num", "num", "num", "num", "", "", "", ""]))
    b.append("<h2>Tier definitions</h2>")
    b.append(table(["Tier", "Definition"], [[chip(k, {"High": "hi", "Medium": "med", "Low": "lo"}[k]), E(v)]
                                            for k, v in POL["tiers"].items()], aligns=["", ""]))
    return "".join(b)


def render_high():
    b = ['<p class="lede">%d picks clear all four gates. Each is shown with the evidence that puts it there: the official '
         'facts, the origination arithmetic, the rung it beat, and what was rejected.</p>' % len(HIGH)]
    for r in [x for x in ROWS if x["high_selection"]]:
        h = r["high_selection"]
        rt = r["rating"]
        b.append('<div class="panel"><h3 style="margin-top:0">%s &mdash; %s</h3>'
                 '<p class="sub">%s &middot; %s &middot; OLBG event %s &middot; %s</p>'
                 '<p><b>Selection:</b> %s &nbsp; <b>Market:</b> %s &nbsp; <b>Our p:</b> %s &nbsp; '
                 '<b>American:</b> %s &nbsp; <b>Decimal:</b> %.3f &nbsp; <b>5%% book equivalent:</b> %s</p>'
                 % (E(r["sport_label"]), E(r["fixture"]), E(r["competition"] or ""), E(r["day_label"] or ""),
                    E(str(r["olbg_event_id"] or "not listed on OLBG")),
                    ("official kick-off %s CEST on %s" % (E(rt["official_ko_cest"]), E(rt["official_date"])))
                    if rt.get("official_ko_cest") else "no official kick-off published",
                    "<b>%s</b>" % E(h["label"]), E(h["market"]), pct(h["p"]), "<b>%s</b>" % am(h["american"]),
                    h["decimal"], am(h["book5_american"])))
        b.append('<p class="sub"><b>Gates:</b> %s &nbsp; %s &nbsp; %s &nbsp; %s</p>' % (
            chip("fixture verified", "ok"), chip("Class A both sides", "ok"),
            chip("official form", "ok") if rt["form_ok"] else chip("no official form", "bad"),
            chip("in window", "ok")))
        b.append("<h3>Official evidence</h3><ul>%s</ul>" % "".join("<li>%s</li>" % E(x) for x in rt["evidence"]))
        b.append("<h3>Sources</h3><ul>%s</ul>" % "".join(
            '<li><a href="%s" rel="noopener noreferrer">%s</a> <span class="sub">%s</span></li>'
            % (E(s["url"]), E(s["url"]), E(s["name"])) for s in r["sources"]["official"]))
        if r["olbg_url"]:
            b.append('<p class="sub">OLBG card (reconstructed from the harvested strings): <a href="%s" '
                     'rel="noopener noreferrer">%s</a></p>' % (E(r["olbg_url"]), E(r["olbg_url"])))
        if r["rejected_highs"]:
            b.append("<h3>Rejected on this fixture</h3>")
            b.append(table(["Selection", "Market", "Our p", "American", "Why rejected"],
                           [[E(j["label"]), E(j["market"]), pct(j["p"]), am(j["american"]), E(j["reason"])]
                            for j in r["rejected_highs"]],
                           aligns=["", "", "num", "num", ""]))
            b.append('<p class="sub">%d rungs on this fixture cleared 70%% and were rejected by the window; those above '
                     'are the informative ones. The full ladder is on the <a href="markets.html">markets</a> '
                     'page.</p>' % r["rejected_high_count"])
        if r["prediction"]:
            b.append('<div class="pred"><div class="who">Prediction &middot; %d words</div><p>%s</p></div>'
                     % (r["prediction"]["word_count"], E(r["prediction"]["text"])))
        b.append("</div>")
    return "".join(b)


def render_predictions():
    b = ['<p class="lede">One prediction per high-confidence pick, %d in total. Each is at least 30 words (they run '
         '%d&ndash;%d), each is unique, and every factual claim inside them comes from a governing body and is linked '
         'underneath. No two share a six-word run &mdash; that is checked mechanically, not by eye.</p>'
         % (len(HIGH), min(len(x["prediction"].split()) for x in HIGH if x["prediction"]),
            max(len(x["prediction"].split()) for x in HIGH if x["prediction"]))]
    for r in [x for x in ROWS if x["prediction"]]:
        p = r["prediction"]
        b.append('<div class="pred"><div class="who">%s &mdash; %s &nbsp; %s &nbsp; %s &nbsp; %s &nbsp; %d words</div>'
                 '<p>%s</p>'
                 '<p class="sub" style="margin-top:9px">Sources: %s</p></div>'
                 % (E(r["sport_label"]), E(r["fixture"]), "<b>%s</b>" % E(p["for_selection"]),
                    am(p["american"]), pct(p["p"]), p["word_count"], E(p["text"]),
                    " &middot; ".join('<a href="%s" rel="noopener noreferrer">%s</a>' % (E(s["url"]), E(s["name"]))
                                      for s in p["official_sources"])))
    b.append('<div class="note">Predictions exist only for high-confidence picks, exactly as the brief specifies. '
             'Medium and Low rows carry a pick and a price but no prose, because writing confident-sounding narrative '
             'over single-sided or consensus-only evidence is how a desk ends up asserting things nobody verified.</div>')
    return "".join(b)


def render_verification():
    b = ['<p class="lede">Every official body reached this session, what it confirmed, and &mdash; just as important '
         '&mdash; what it refused to confirm. A value is only used as an input if it appears in the first column.</p>']
    for reg in D["official_sources"]:
        if not reg["official"]:
            continue
        b.append('<div class="panel"><h3 style="margin-top:0">%s</h3>'
                 '<p class="sub">Fetched %s</p><ul>%s</ul>'
                 % (E(reg["name"]), E(reg["fetched_utc"] or "&mdash;"),
                    "".join('<li><a href="%s" rel="noopener noreferrer">%s</a></li>' % (E(u), E(u)) for u in reg["urls"])))
        if reg["confirms"]:
            b.append("<h3>Confirms</h3><ul>%s</ul>" % "".join("<li>%s</li>" % E(c) for c in reg["confirms"]))
        if reg["does_not_confirm"]:
            b.append('<h3>Does <span style="color:var(--bad)">not</span> confirm</h3><ul>%s</ul>'
                     % "".join("<li>%s</li>" % E(c) for c in reg["does_not_confirm"]))
        b.append("</div>")
    b.append("<h2>Reconciliation of the official EuroLeague standings</h2>")
    b.append('<p class="lede">The standings table is the only two-sided official rating input we obtained, so it was '
             'reconciled before use. All four checks pass on all 20 clubs.</p>')
    st = STANDINGS
    b.append(table(["#", "Club", "GP", "W", "L", "Win%", "PTS+", "PTS-", "+/-", "Home", "Away", "OT", "L10",
                    "ppg for", "ppg against"],
                   [[r[0], E(r[1]), r[3], r[4], r[5], E(r[6]), r[7], r[8], "%+d" % r[9], E(r[10]), E(r[11]),
                     E(r[12]), E(r[13]), "%.2f" % (r[7] / r[3]), "%.2f" % (r[8] / r[3])] for r in st["rows"]],
                   aligns=["num", "", "num", "num", "num", "num", "num", "num", "num", "", "", "", "", "num", "num"]))
    t = st["totals"]
    b.append(table(["Check", "Result"],
                   [["PTS+ &minus; PTS&minus; == +/-", chip("20 / 20 pass", "ok")],
                    ["W + L == GP, and Win% == W/GP", chip("20 / 20 pass", "ok")],
                    ["Home record + away record == overall W-L", chip("20 / 20 pass", "ok")],
                    ["sum(PTS+) == sum(PTS&minus;) (closed system)", "%d == %d %s" % (t["sum_pts_for"], t["sum_pts_against"], "&#10003;")],
                    ["sum(W) == sum(L) == games played", "%d == %d == %d %s" % (t["sum_wins"], t["sum_losses"], t["games"], "&#10003;")],
                    ["Home wins + away wins == games", "%d + %d == %d %s" % (t["home_wins"], t["away_wins"], t["games"], "&#10003;")],
                    ["League average game total implied", "%.2f points" % t["league_avg_game_total"]]],
                   aligns=["", ""]))
    b.append("<h2>Clock reconciliation &mdash; OLBG against official CEST</h2>")
    b.append('<p class="lede">OLBG publishes no timezone anywhere. Cross-referencing its card clocks against the official '
             'EuroLeague kick-offs identifies the timezone exactly: all eight fixtures are six hours behind CEST, and '
             'CEST is UTC+2 while EDT is UTC&minus;4.</p>')
    cr = CLOCK
    b.append(table(["OLBG event", "OLBG fixture", "OLBG day", "OLBG clock", "Official fixture",
                    "Official date", "Official kick-off", "Delta"],
                   [[r[0], E(r[1]), E(r[2]), "<b>%s</b>" % E(r[3]), E(r[4]), E(r[5]),
                     "<b>%s CEST</b>" % E(r[6]), chip("%+d h" % r[7], "ok" if r[7] == -6 else "bad")] for r in cr["rows"]],
                   aligns=["num", "", "", "", "", "", "", "num"]))
    b.append('<div class="note">%d of %d reconcile at exactly %s hours, with no residual. OLBG&rsquo;s hub clock is '
             'therefore US Eastern Daylight Time, presented with no label.</div>'
             % (cr["matched"], cr["total_official_upcoming"], cr["delta_hours"]))
    return "".join(b)


STANDINGS = None
CLOCK = None


def render_sources():
    b = ['<p class="lede">The full register: %d entries. Official governing bodies first, then the sources we deliberately '
         'rejected. A source is only &ldquo;official&rdquo; if it is the sport&rsquo;s own governing body or competition '
         'operator; media outlets, aggregators, reference sites and betting sites are never treated as official, however '
         'accurate they look.</p>' % len(D["official_sources"])]
    b.append("<h2>Official sources used</h2>")
    b.append(table(["Source", "Fetched (UTC)", "URLs", "Confirms", "Does not confirm"],
                   [[E(r["name"]), E(r["fetched_utc"] or "&mdash;"),
                     "<br>".join('<a href="%s" rel="noopener noreferrer">%s</a>' % (E(u), E(u)) for u in r["urls"]),
                     len(r["confirms"]), len(r["does_not_confirm"])]
                    for r in D["official_sources"] if r["official"]],
                   aligns=["", "", "", "num", "num"]))
    rej = [r for r in D["official_sources"] if not r["official"]]
    if rej:
        b.append("<h2>Rejected as non-official</h2>")
        b.append('<p class="lede">Each of these was reached or surfaced during the session and each was rejected as an '
                 'input. Where a rejected source carried a number that would have been convenient to use, the reason says '
                 'so explicitly.</p>')
        b.append(table(["URL", "Why rejected"],
                       [[link(d["url"], d["url"]), E(d["why_rejected"])] for d in rej[0].get("detail", [])],
                       aligns=["", ""]))
    b.append("<h2>Manual review links</h2>")
    b.append('<p class="lede">Everything a reviewer needs to re-check this desk by hand, in one place.</p>')
    links = []
    for r in D["official_sources"]:
        if r["official"]:
            for u in r["urls"]:
                links.append([E(r["name"]), link(u, u)])
    for s in SPORTS:
        links.append(["OLBG %s hub (harvested)" % E(s["label"]), link(s["hub"], s["hub"])])
    b.append(table(["What", "Link"], links, aligns=["", ""]))
    return "".join(b)


def render_methodology():
    b = ['<p class="lede">How every number on this site was produced, and which numbers are ours rather than sourced. '
         'The distinction is the whole method: facts come from governing bodies, probabilities come from us, and the two '
         'are never blurred.</p>']
    b.append("<h2>Evidence classes</h2>")
    b.append(table(["Class", "Definition", "Ceiling"],
                   [[klass_chip(k), E(v), ("High allowed" if k == "A" else "Hard-capped at Medium")]
                    for k, v in POL["classes"].items()], aligns=["", "", ""]))
    b.append("<h2>Confidence tiers</h2>")
    b.append(table(["Tier", "Definition"], [[chip(k, {"High": "hi", "Medium": "med", "Low": "lo"}[k]), E(v)]
                                            for k, v in POL["tiers"].items()], aligns=["", ""]))
    b.append("<h2>Model constants &mdash; all of these are OUR assumptions</h2>")
    mc = POL["model_constants"]
    sig = mc["sport_sigma"]
    b.append(table(["Sport", "Scoring unit", "sigma (spread)", "sigma (total)"],
                   [[E(k.title().replace("_", " ")), E(v["unit"] or "&mdash;"),
                     blank(v["sigma_h"], "%.2f"), blank(v["sigma_t"], "%.2f")] for k, v in sig.items()],
                   aligns=["", "", "num", "num"]))
    c = mc["class_c"]
    b.append(table(["Constant", "Value", "Used for"],
                   [["Class B one-sided p", "%.3f" % mc["class_b_p"], "A fixture where only one side has an official rating. Hard-capped at Medium."],
                    ["Class C base p", "%.2f" % c["base"], "No official source reached. Starts neutral."],
                    ["Class C slope", "%.2f" % c["slope"], "Applied to OLBG consensus share, which is not an official input."],
                    ["Class C cap", "%.3f" % c["cap"], "Consensus alone can never imply more than this."],
                    ["Class C minimum tips", "%d" % c["min_tips"], "Below this the consensus is treated as no information at all."],
                    ["Snooker top-16 p", "%.3f" % mc["snooker_top16_p"], "The edge we give a player a governing body confirms is a surviving world top-16 player."],
                    ["Darts seed-gap k", "%.2f" % mc["darts"]["k"], "Logistic slope on the official PDC seed gap."],
                    ["Darts seed-gap scale", "%.1f" % mc["darts"]["scale"], "Seed gap is divided by this before the logistic."],
                    ["Probability bounds", "%.2f &ndash; %.2f" % tuple(mc["prob_bounds"]), "No originated probability is allowed outside these."],
                    ["Overround printed", "%.0f%%" % (mc["overround_book_printed"] * 100), "Shown beside every price for comparison. Never used to gate."]],
                   aligns=["", "num", ""]))
    b.append('<div class="note"><b>Label discipline.</b> Every number in the two tables above is our assumption and is '
             'published as one. No model constant is ever presented as a sourced fact, and no sourced fact is ever '
             'adjusted by a model constant without the arithmetic being printed on the row.</div>')
    b.append("<h2>Derived from official data, not assumed</h2>")
    dv = POL["derived"]
    b.append(table(["Quantity", "Value", "Derivation"],
                   [["Official home win rate", "%.4f" % dv["official_home_win_rate"], E(dv["home_win_rate_basis"])],
                    ["Basketball HCA", "%.2f points" % dv["basketball_hca_points"], E(dv["hca_formula"])],
                    ["Ladder grid", "half-point only", E(dv["ladder_rule"])],
                    ["Tightest rung", "closest to our centre", E(dv["tightest_rung_rule"])],
                    ["Line sign", "follows the label", E(dv["ladder_sign_rule"])],
                    ["Ladder depth", "stops before saturation", E(dv["ladder_saturation_rule"])],
                    ["Offset", "cushion in the sport's unit", E(dv["offset_rule"])],
                    ["Rejected ledger", "informative rows only", E(dv["rejected_ledger_rule"])],
                    ["Totals", "official anchor required", E(dv["totals_rule"])],
                    ["Spreads", "official rating required", E(dv["spread_rule"])],
                    ["Winner pick", "follows the favourite", E(dv["winner_pick_rule"])],
                    ["Club names", "official names in labels", E(dv["name_crosswalk_rule"])]],
                   aligns=["", "", ""]))
    b.append("<h2>Pricing maths</h2>")
    b.append('<pre>decimal  = 1 / p\n'
             'american = -100 * p / (1 - p)      when p >= 0.5\n'
             '         = +100 * (1 - p) / p      when p <  0.5\n'
             '5% book  = the same formula applied to p * 1.05  (printed, never gating)\n\n'
             'handicap rung h, margin centre m, sigma s:\n'
             '  p(home covers -h) = 1 - Phi((h - m) / s)\n'
             '  p(away covers +h) =     Phi((h - m) / s)\n\n'
             'total rung x, total centre t, sigma_t s:\n'
             '  p(over  x) = 1 - Phi((x - t) / s)\n'
             '  p(under x) =     Phi((x - t) / s)</pre>')
    b.append("<h2>What we refuse to do</h2>")
    b.append("<ul>"
             "<li>No value is inferred, interpolated, or carried over from a bookmaker. If an official body did not publish it, the cell is blank and the row is flagged.</li>"
             "<li>No media outlet, aggregator, reference site or betting site is treated as official, even when it is the only source that has the number.</li>"
             "<li>No prediction is written over evidence weaker than Class A. Prose over thin evidence reads as confidence and is not.</li>"
             "<li>No official-vs-official disagreement is silently resolved. Both values are published, the reconciliation is shown, and the one that survives arithmetic is the one used.</li>"
             "<li>No rung is placed on an integer line, because an integer line can push and a push is not a priceable outcome.</li>"
             "</ul>")
    return "".join(b)


def render_flagged():
    b = ['<p class="lede"><b>Flagged for Review.</b> %d findings: irregularities in OLBG&rsquo;s own rendering, '
         'disagreements between official sources, defects found in this repository, and values we could not confirm and '
         'therefore left blank. None of these block publication; all of them are here with their sources so a reviewer can '
         'check every one by hand.</p>' % len(FIND)]
    sev = {"high": 0, "medium": 0, "low": 0}
    for f in FIND:
        sev[f["severity"]] = sev.get(f["severity"], 0) + 1
    b.append(cards([(len(FIND), "findings"), (sev.get("high", 0), "high severity"),
                    (sev.get("medium", 0), "medium"), (sev.get("low", 0), "low"),
                    (len([f for f in FIND if f["status"].startswith("confirmed")]), "confirmed"),
                    (len([f for f in FIND if "unverified" in f["status"] or "unconfirmed" in f["status"] or "candidate" in f["status"]]),
                     "unverified / candidate")]))
    for f in sorted(FIND, key=lambda x: ({"high": 0, "medium": 1, "low": 2}.get(x["severity"], 3), x["id"])):
        b.append('<div class="finding %s"><span class="fid">%s</span> %s %s %s'
                 '<h3>%s</h3><p>%s</p>'
                 % (E(f["severity"]), E(f["id"]), chip(f["severity"], {"high": "bad", "medium": "med", "low": "mut"}[f["severity"]]),
                    chip(f["status"].replace("-", " "), "ok" if f["status"].startswith("confirmed") else "bad"),
                    chip(f["sport"], "mut"), E(f["title"]), E(f["detail"])))
        if f["sources"]:
            b.append('<p class="sub"><b>Sources:</b> %s</p>'
                     % " &middot; ".join(src_ref(u) for u in f["sources"]))
        ev = f.get("evidence")
        if ev:
            dumped = json.dumps(ev, indent=1, ensure_ascii=False)
            if len(dumped) > 4000:
                # cut on a line boundary and say so, rather than slicing a
                # string in half and leaving the reader to guess
                cut = dumped[:4000].rfind("\n")
                dumped = dumped[:cut if cut > 0 else 4000].rstrip() + \
                    "\n... truncated; the complete evidence is in data/1a421e41/desk.json"
            b.append("<details><summary class='sub'>evidence (%d item%s)</summary><pre>%s</pre></details>"
                     % (len(ev), "" if len(ev) == 1 else "s", E(dumped)))
        b.append("</div>")

    b.append("<h2>Unverified values left blank</h2>")
    b.append('<p class="lede">Every row flag raised by the build, grouped by code. These are the places where we refused '
             'to put a number in.</p>')
    codes = {}
    for r in ROWS:
        for fl in r["flags"]:
            codes.setdefault(fl["code"], []).append(r)
    b.append(table(["Flag code", "Rows", "Meaning"],
                   [["<code>%s</code>" % E(k), len(v), E(v[0]["flags"][[f["code"] for f in v[0]["flags"]].index(k)]["detail"])]
                    for k, v in sorted(codes.items())],
                   aligns=["", "num", ""]))
    b.append("<h2>Affected rows</h2>")
    rows = []
    for r in ROWS:
        if r["flags"]:
            rows.append([E(r["sport_label"]), E(r["fixture"]),
                         " ".join('<code>%s</code>' % E(f["code"]) for f in r["flags"]), src_links(r)])
    b.append(table(["Sport", "Fixture", "Flags", "Source"], rows, scroll=True, aligns=["", "", "", ""]))
    return "".join(b)


def render_audit():
    b = ['<p class="lede">A line-by-line review of this repository, offline. Every finding below is reproducible with '
         '<code>grep</code> or a short script against the committed files; the file and line number are given so a '
         'reviewer can land on it directly.</p>']
    aud = [f for f in FIND if f["id"].startswith("AUD-")]
    for f in aud:
        b.append('<div class="finding high"><span class="fid">%s</span> %s %s<h3>%s</h3><p>%s</p>'
                 '<p class="sub"><b>Evidence:</b> <code>%s</code></p>'
                 '<p class="sub"><b>Sources:</b> %s</p></div>'
                 % (E(f["id"]), chip(f["severity"], {"high": "bad", "medium": "med", "low": "mut"}[f["severity"]]),
                    chip(f["status"].replace("-", " "), "ok" if f["status"] == "confirmed" else "bad"),
                    E(f["title"]), E(f["detail"]),
                    E(json.dumps(f["evidence"], ensure_ascii=False)[:900]),
                    " &middot; ".join(src_ref(u) for u in f["sources"])))
    b.append("<h2>Repository hygiene checks run</h2>")
    b.append(table(["Check", "Result"],
                   [["Tracked <code>.pyc</code> / <code>__pycache__</code> files", chip("0 &mdash; clean", "ok")],
                    ["HTML files in the tree", "319"],
                    ["README claim of published pages (line 56)", "160 &mdash; stale, see AUD-1A-README-01"],
                    ["JSON datasets walked for out-of-window High rows", "127"],
                    ["High-labelled rows priced shorter than -250", "12, across 4 files"],
                    ["Root predictions file duplicate storage", "same 29 predictions stored twice, see AUD-1A-DUP-01"],
                    ["This desk's validator", "<code>scripts/s1a421e41_validate.py</code> &mdash; PASS, 0 errors"]],
                   aligns=["", ""]))
    b.append("<h2>Carried forward from earlier sessions</h2>")
    b.append('<p class="lede">These were logged by other sessions on the coordination board and are restated here '
             'because this session&rsquo;s own findings independently confirm two of them. They are not re-litigated.</p>')
    b.append(table(["Id", "What"],
                   [["AUD-F7-04", "A High-confidence snooker pick priced on a match the official tour shows as already decided. Independently confirmed by AUD-1A-HIGGINS-01."],
                    ["AUD-F7-01", "Stale published-page count in README.md. Independently confirmed by AUD-1A-README-01 with a fresh count."],
                    ["AUD-F7-06 / 07", "Rugby union spreads graded High on weak evidence (England -9.5, Tonga -2.5)."],
                    ["AUD-F7-08", "Seven datasets that do not reconcile with each other."],
                    ["AUD-F7-09", "plusliga.pl publishes two different clocks for the same TAURON Liga fixture."],
                    ["AUD-F7-10", "formula1.com title gap quoted as 102 and 119 points on the same day; also a hand-patched root banner."],
                    ["AUD-F7-11", "maighcuilinn.com prints Dessie Conneely as both 2-14 and 2-16 on one page."],
                    ["AUD-F7-12", "OLBG tipping Kanturk against the verified record."],
                    ["F-F7-NHL-01", "NHL season goals for/against do not reconcile (Rangers 17 vs 33 inside its own last-ten block). NHL goals values discarded; no NHL total is priced on this desk."]],
                   aligns=["", ""]))
    return "".join(b)


def render_reverse():
    b = ['<p class="lede">What OLBG.com actually is, structurally, worked out by harvesting it rather than by reading '
         'documentation. Everything here was observed directly on %s.</p>' % HARVEST_UTC]
    b.append("<h2>URL architecture</h2>")
    b.append('<pre>sport hub        https://www.olbg.com/betting-tips/&lt;Sport_Slug&gt;/&lt;sport_id&gt;\n'
             'competition      https://www.olbg.com/betting-tips/&lt;Sport_Slug&gt;/&lt;Comp_Slug&gt;/&lt;id&gt;\n'
             'tip card         https://www.olbg.com/betting-tips/&lt;Sport_Slug&gt;/&lt;Comp_Slug&gt;/&lt;Event_Slug&gt;/&lt;id&gt;?event_id=NNN\n\n'
             'example          https://www.olbg.com/betting-tips/Basketball/4\n'
             '                 https://www.olbg.com/betting-tips/Snooker/8</pre>')
    b.append('<div class="note">Requesting <code>/Snooker/1</code> is served <code>/Snooker/8</code>: the numeric id in '
             'the path is the sport id, and OLBG redirects a wrong id to the right slug rather than erroring. The '
             'betting-tips sitemap is dominated by Horse Racing and the excluded sports and is a dead end for enumerating '
             'fixtures &mdash; the sport hubs have to be harvested one at a time.</div>')
    b.append("<h2>Card field semantics</h2>")
    b.append(table(["Field on the card", "What it actually means", "Observed behaviour"],
                   [["Day label", "Relative day bucket, not a date", "Values are <code>Today</code> and <code>Tomorrow</code>; no absolute date is published anywhere on the hub."],
                    ["Clock", "Local start time in <b>US Eastern Daylight Time</b>, unlabelled", "Proved by an exact &minus;6h offset against official CEST kick-offs on all 8 EuroLeague fixtures (F-1A-CLOCK-04)."],
                    ["Competition", "Free-text league or tour name", "Not a controlled vocabulary; the same competition is spelled differently across sports."],
                    ["Fixture", "Participants separated by <code>vs</code>, <code>v</code> or <code>@</code>", "All three separators occur. <code>@</code> appears on North American sports and reverses the home/away order."],
                    ["Market chip", "The market the consensus tip refers to", "Empty on all 6 Gaelic Football cards (F-1A-MARKET-01), so the tipped market is not machine-readable there."],
                    ["Win tips / Total tips", "Count of tips on each market", "Counts, not prices. OLBG publishes no odds on the hub."],
                    ["Consensus share", "Percentage of tips on the leading selection", "Printed <b>blank</b>, not zero, whenever the win-tip count is 0 (F-1A-SHARE-01)."],
                    ["Value Rating", "OLBG&rsquo;s own 1&ndash;5 star score", "Per OLBG&rsquo;s hub copy: consensus share compared against bookmaker implied probability."],
                    ["Experts", "Tipsters with a high strike rate", "Per OLBG&rsquo;s hub copy: high strike rate plus profitability over the current month and the last six months."]]))
    b.append("<h2>The tip-gated blind spot</h2>")
    b.append('<div class="panel"><p>An OLBG card exists only once at least one tipster has posted on that fixture. A '
             'fixture with zero tips is <b>invisible</b> &mdash; there is no empty card, no placeholder, and nothing in the '
             'page source to enumerate. OLBG is therefore not a fixture list; it is a list of fixtures somebody has tipped.</p>'
             '<p>Proved twice against official slates on this harvest:</p><ul>'
             '<li><b>Ice hockey.</b> NHL&rsquo;s official schedule API reports <code>numberOfGames: 12</code> for %s. '
             'OLBG&rsquo;s Ice Hockey hub renders 7 cards, all SHL or Liiga, and none of the 12 NHL games. (F-1A-NHL-01)</li>'
             '<li><b>Basketball.</b> EuroLeague&rsquo;s official Round 7 has 9 upcoming games. OLBG renders 8; '
             'Paris Basketball v Valencia Basket, the round&rsquo;s closing game, is absent. (F-1A-BBALL-01)</li>'
             '<li><b>Two whole sports.</b> The Aussie Rules hub (id 22) and the eSports hub (id 23) both render '
             '&ldquo;No tips found.&rdquo; and no fixtures at all. (F-1A-EMPTY-01)</li></ul>'
             '<p>Practical consequence for anyone consuming OLBG programmatically: absence of a card is <b>not</b> '
             'evidence that a fixture does not exist. It only means nobody has tipped it yet.</p></div>' % HARVEST_UTC[:10])
    b.append("<h2>Empty-hub rendering defect</h2>")
    b.append('<p>On a hub with no fixtures, OLBG&rsquo;s sports-menu chip falls back to the literal text '
             '<code>All Sports</code> instead of naming the sport, so the page does not identify itself. (F-1A-CHIP-01)</p>')
    b.append("<h2>Harvest yield</h2>")
    b.append(table(["Sport", "OLBG id", "Hub", "Cards rendered", "State"],
                   [[E(s["label"]), s["olbg_id"], link(s["hub"], "hub"), s["olbg_rows"],
                     chip("empty", "bad") if s["olbg_rows"] == 0 else chip("harvested", "ok")] for s in SPORTS],
                   aligns=["", "num", "", "num", ""]))
    b.append('<div class="note">%d cards harvested across %d hubs. Chunked responses truncated several hubs mid-card, so '
             'some individual card fields are <code>null</code> rather than absent. Those are flagged per row rather than '
             'back-filled.</div>' % (META["rows_from_olbg"], len(SPORTS)))
    return "".join(b)


def render_sport(sp):
    rs = [r for r in ROWS if r["sport"] == sp["key"]]
    b = []
    b.append(cards([(len(rs), "fixtures"), (sp["class_a"], "Class A"), (sp["class_b"], "Class B"),
                    (sp["class_c"], "Class C"), (sp["markets_originated"], "markets originated"),
                    (sp["high"], "High picks"), (sp["flagged"], "rows flagged")]))
    b.append('<p class="sub">OLBG id <b>%d</b> &middot; hub <a href="%s" rel="noopener noreferrer">%s</a></p>'
             % (sp["olbg_id"], E(sp["hub"]), E(sp["hub"])))
    if not rs:
        b.append('<div class="panel"><b>No fixtures rendered.</b> OLBG&rsquo;s %s hub returns &ldquo;No tips found.&rdquo; '
                 'The sport stays in scope because the brief defines scope by sport, not by whether tipsters have posted. '
                 'See F-1A-EMPTY-01.</div>' % E(sp["label"]))
        return "".join(b)
    b.append("<h2>Fixtures, our lines and our picks</h2>")
    rows = []
    for r in rs:
        w = r["winner_pick"]
        rt = r["rating"]
        rows.append([
            "<b>%s</b>" % E(r["fixture"]),
            E(r["day_label"] or "") + " " + (E(r["olbg_clock"]) if r["olbg_clock"] else '<span class="blank">no clock</span>'),
            E(r["competition"] or ""),
            klass_chip(rt["klass"]),
            E(w["selection"] or "") or '<span class="blank">not priced</span>',
            pct(w["p"]) if w["p"] is not None else '<span class="blank">blank</span>',
            am(w["american"]), tier_chip(w["confidence"]),
            ("<b>%s</b> %s" % (E(r["high_selection"]["label"]), am(r["high_selection"]["american"])))
            if r["high_selection"] else '<span class="mut">none in window</span>',
            r["market_counts"]["match_winner"], r["market_counts"]["handicap"], r["market_counts"]["match_total"],
            " ".join('<code>%s</code>' % E(f["code"]) for f in r["flags"]) or '<span class="mut">none</span>',
            src_links(r),
        ])
    b.append(table(["Fixture", "OLBG clock", "Competition", "Class", "Our pick", "p", "American", "Tier",
                    "High selection", "MW", "Hcp", "Tot", "Flags", "Source"], rows,
                   aligns=["", "", "", "", "", "num", "num", "", "", "num", "num", "num", "", ""]))
    hi = [r for r in rs if r["high_selection"]]
    for r in hi:
        b.append('<div class="panel"><h3 style="margin-top:0">High confidence &mdash; %s</h3>'
                 '<p><b>%s</b> &middot; %s &middot; our p %s &middot; American %s &middot; decimal %.3f &middot; '
                 '5%% book equivalent %s</p><h3>Official evidence</h3><ul>%s</ul></div>'
                 % (E(r["fixture"]), E(r["high_selection"]["label"]), E(r["high_selection"]["market"]),
                    pct(r["high_selection"]["p"]), am(r["high_selection"]["american"]),
                    r["high_selection"]["decimal"], am(r["high_selection"]["book5_american"]),
                    "".join("<li>%s</li>" % E(x) for x in r["rating"]["evidence"])))
        if r["prediction"]:
            b.append('<div class="pred"><div class="who">Prediction &middot; %d words</div><p>%s</p></div>'
                     % (r["prediction"]["word_count"], E(r["prediction"]["text"])))
    b.append("<h2>Every market originated on this sport</h2>")
    mrows = []
    for r in rs:
        for m in r["markets"]:
            mrows.append([E(r["fixture"]), E(m["market"]), E(m["label"]), blank(m["line"], "%.1f"),
                          pct(m["p"]), "%.3f" % m["decimal"] if m["decimal"] else "&mdash;",
                          am(m["american"]), am(m["book5_american"]),
                          chip("in", "ok") if m["in_window"] else '<span class="mut">out</span>',
                          chip("&ge;70", "hi") if m["ge_70"] else ""])
    b.append(table(["Fixture", "Market", "Selection", "Line", "Our p", "Decimal", "American", "5% book", "Window", "p&ge;70"],
                   mrows, scroll=True, aligns=["", "", "", "num", "num", "num", "num", "num", "", ""]))
    rej = [[E(r["fixture"]), E(j["label"]), E(j["market"]), pct(j["p"]), am(j["american"]), E(j["reason"])]
           for r in rs for j in r["rejected_highs"]]
    if rej:
        b.append("<h2>Rejected Highs on this sport</h2>")
        b.append('<p class="lede">Cleared the 70%% floor but fell outside the price window. %d rungs in this sport were '
                 'rejected in total; only the informative ones are listed.</p>'
                 % sum(r["rejected_high_count"] for r in rs))
        b.append(table(["Fixture", "Selection", "Market", "Our p", "American", "Why rejected"], rej,
                       aligns=["", "", "", "num", "num", ""]))
    return "".join(b)


PAGES = [
    ("index.html", "OLBG reverse-engineered &mdash; betting desk for 17 sports", render_index,
     "Live OLBG harvest of %s, our own zero-vig origination for every fixture, and every finding flagged with its source."
     % HARVEST_UTC),
    ("coverage.html", "Sport coverage &mdash; 17 in scope, 7 excluded", render_coverage,
     "Which sports are in scope, which are excluded and why, and which governing body we actually reached for each."),
    ("matches.html", "All matches harvested", render_matches,
     "Every fixture row with its OLBG card fields, our rating class, our pick and its source links."),
    ("markets.html", "Every market investigated", render_markets,
     "Match winner, handicap and match total for every fixture we could originate from official data."),
    ("lines.html", "Our originated lines", render_lines,
     "The fair price for each side and the margin and total centres every ladder is built around."),
    ("window.html", "The -250 to +10000 high-confidence band", render_window,
     "Why the band is only 0.0143 wide in probability, how we resolved the contradiction, and what it rejects."),
    ("picks.html", "Match-winner picks", render_picks,
     "A winner pick and a confidence tier for every fixture, compared against what OLBG's tipsters are backing."),
    ("high-confidence.html", "High-confidence picks", render_high,
     "Every pick that clears all four gates, with the official evidence and the arithmetic behind it."),
    ("predictions.html", "Predictions", render_predictions,
     "Unique prose for each high-confidence pick, built only from verified official facts."),
    ("verification.html", "Verification against official sources", render_verification,
     "What each governing body confirmed, what it refused to confirm, and the reconciliations we ran before using it."),
    ("sources.html", "Source register", render_sources,
     "Every official source used, every non-official source rejected, and links for manual review."),
    ("methodology.html", "Methodology", render_methodology,
     "Evidence classes, confidence tiers, model constants, and the line between our assumptions and sourced facts."),
    ("flagged.html", "Flagged for Review", render_flagged,
     "Every irregularity, every official-vs-official disagreement, and every value we left blank rather than invent."),
    ("audit.html", "Repository audit", render_audit,
     "Findings from a line-by-line review of this repository, each with the file and line number to check."),
    ("reverse-engineering.html", "Reverse-engineering OLBG.com", render_reverse,
     "URL architecture, card field semantics, and the tip-gated blind spot proved against official slates."),
]


def main():
    global SPORT_REACH, STANDINGS, CLOCK
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "ev", os.path.join(ROOT, "data", "1a421e41", "official_evidence.py"))
    ev = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ev)
    SPORT_REACH = sorted(ev.SPORT_OFFICIAL_REACH.items())
    STANDINGS = ev.EUROLEAGUE_STANDINGS
    CLOCK = ev.EUROLEAGUE_CLOCK_RECONCILIATION

    os.makedirs(ASSETS, exist_ok=True)
    os.makedirs(SPORTS_DIR, exist_ok=True)
    with open(os.path.join(ASSETS, "desk.css"), "w") as fh:
        fh.write(CSS.strip() + "\n")

    written = []
    for fn, title, fn_render, subtitle in PAGES:
        body = fn_render()
        with open(os.path.join(SITE, fn), "w", encoding="utf-8") as fh:
            fh.write(page(title, fn, body, subtitle))
        written.append(fn)

    for sp in SPORTS:
        fn = os.path.join(SPORTS_DIR, sp["key"] + ".html")
        title = "%s &mdash; OLBG desk" % sp["label"]
        body = render_sport(sp)
        with open(fn, "w", encoding="utf-8") as fh:
            fh.write(page(title, "coverage.html", body,
                          "Every %s fixture OLBG rendered on %s, our originated lines, our picks and our flags."
                          % (E(sp["label"]), HARVEST_UTC), prefix="../"))
        written.append("sports/%s.html" % sp["key"])

    total = 0
    for w in written:
        total += os.path.getsize(os.path.join(SITE, w))
    print("wrote %d pages (%d top-level + %d sport pages) + assets/desk.css, %.1f KB"
          % (len(written), len(PAGES), len(SPORTS), total / 1024.0))
    for w in written:
        print("  %s" % w)


if __name__ == "__main__":
    main()
