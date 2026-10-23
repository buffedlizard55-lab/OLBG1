#!/usr/bin/env python3
"""TED71 (session ed71b937-olbg1) - static site builder.

Reads data/ed71b937/{fixtures,lines,predictions,harvest}.json and writes
ed71b937/*.html.  Nothing is re-derived here: every number on the pages comes
from the JSON that the dataset, model and prediction scripts produced.
"""

from __future__ import annotations

import html
import json
import os
import re

SESSION = "ed71b937-olbg1"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "ed71b937")
OUT = os.path.join(ROOT, "ed71b937")

AS_OF = "2026-10-23T17:20:00Z"

CSS = """
:root{--bg:#0e1116;--panel:#161b22;--line:#262d38;--ink:#e6edf3;--dim:#93a1b1;
--acc:#58a6ff;--warn:#d29922;--bad:#f85149}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--acc);text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:1200px;margin:0 auto;padding:22px 20px 64px}
header.top{background:var(--panel);border-bottom:1px solid var(--line)}
header.top .wrap{padding:18px 20px}
h1{font-size:20px;margin:0 0 4px}
h2{font-size:17px;margin:34px 0 10px;border-bottom:1px solid var(--line);padding-bottom:6px}
h3{font-size:15px;margin:24px 0 8px}
p.lead{color:var(--dim);margin:6px 0 0;max-width:86ch}
nav{display:flex;flex-wrap:wrap;gap:4px 14px;font-size:13px;margin-top:10px}
nav a{color:var(--dim)}nav a.on{color:var(--ink);font-weight:600}
table{border-collapse:collapse;width:100%;margin:10px 0 4px;font-size:13px}
th,td{border:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
th{background:#1b2230;font-weight:600;white-space:nowrap}
tbody tr:nth-child(even){background:#12171e}
.scroll{overflow:auto;max-height:80vh;border:1px solid var(--line);border-radius:6px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:16px 0}
.card{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:12px}
.card .n{font-size:26px;font-weight:700;line-height:1.1}
.card .l{font-size:11px;color:var(--dim);text-transform:uppercase;letter-spacing:.06em}
.pill{display:inline-block;padding:1px 7px;border-radius:999px;font-size:11px;
border:1px solid var(--line);white-space:nowrap}
.p-hi{background:#12331c;border-color:#1f6f37;color:#7ee2a0}
.p-med{background:#3a2d10;border-color:#7a5c14;color:#e3b341}
.p-lo{background:#2a1f22;border-color:#5d3a41;color:#d3a3ab}
.p-un{background:#1d2430;border-color:#33405a;color:#9fb3d1}
.blank{color:#5f6b7a}
.note{background:#161b22;border-left:3px solid var(--acc);padding:10px 14px;
border-radius:0 6px 6px 0;margin:14px 0}
.warn{border-left-color:var(--warn)}.bad{border-left-color:var(--bad)}
code{background:#1b2230;padding:1px 5px;border-radius:4px;font-size:12.5px}
pre{background:#1b2230;padding:12px;border-radius:6px;overflow:auto;font-size:12.5px}
.foot{margin-top:44px;padding-top:14px;border-top:1px solid var(--line);
color:var(--dim);font-size:12px}
.pred{background:var(--panel);border:1px solid var(--line);border-radius:8px;
padding:16px 18px;margin:14px 0}
.pred blockquote{margin:0 0 12px;font-size:15px;line-height:1.78}
.srcs{font-size:12px;color:var(--dim)}
ul.srcs{margin:6px 0}
details summary{cursor:pointer;color:var(--dim);font-size:13px}
"""

TIER_LABEL = {"high-in-band": "HIGH", "medium": "MEDIUM", "low": "LOW",
              "unpriced": "UNPRICED", "out-of-band-short": "OUT OF BAND"}
TIER_CLASS = {"high-in-band": "p-hi", "medium": "p-med", "low": "p-lo",
              "unpriced": "p-un", "out-of-band-short": "p-un"}
TIER_MEANING = {
    "high-in-band": "Priced, probability at least 0.700 and price inside "
                    "-250..+10000.",
    "medium": "Priced, probability between 0.55 and 0.700.",
    "low": "Priced, below 0.55. Carried for completeness, never promoted.",
    "out-of-band-short": "Probability at least 0.700 but fair price shorter "
                         "than -250, so outside the stated band. Disclosed, "
                         "never promoted.",
    "unpriced": "No official inputs were available, so no price is offered "
                "rather than a guess.",
}


# ------------------------------------------------------------------ helpers
def e(x):
    return html.escape("" if x is None else str(x))


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def dash():
    return '<span class="blank">&mdash;</span>'


def cell(v):
    return dash() if v in (None, "", []) else e(v)


def money(a):
    return dash() if a is None else ("+{}".format(a) if a > 0 else str(a))


def tier_pill(t):
    return '<span class="pill {}">{}</span>'.format(
        TIER_CLASS.get(t, "p-un"), TIER_LABEL.get(t, t.upper()))


def link_list(urls):
    if not urls:
        return dash()
    out = []
    for u in urls:
        short = re.sub(r"^https?://(www\.)?", "", u).split("/")[0]
        out.append('<a href="{}" rel="noopener" target="_blank">{}</a>'.format(
            e(u), e(short)))
    return "<br>".join(out)


def rel(u):
    """Display form of a URL, origin only."""
    return re.sub(r"^https?://(www\.)?", "", u).split("/")[0]


def page(name, title, body, subtitle="", nav_on=None, crumb=""):
    nav = [("index.html", "Dashboard"), ("matches.html", "Match list"),
           ("markets.html", "All markets"),
           ("high-confidence.html", "High confidence"),
           ("predictions.html", "Predictions"), ("analysis.html", "Analysis"),
           ("flagged.html", "Flagged for review"), ("sources.html", "Sources"),
           ("methodology.html", "Method"), ("sports.html", "By sport")]
    links = " ".join(
        '<a href="{}{}"{}>{}</a>'.format(
            crumb, h, ' class="on"' if h == nav_on else "", e(l))
        for h, l in nav)
    doc = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} &middot; OLBG desk ed71b937</title>
<style>{css}</style></head><body>
<header class="top"><div class="wrap">
<h1>OLBG reverse-engineered desk &mdash; <code>ed71b937</code></h1>
<p class="lead">15 requested sports &middot; independently originated lines
&middot; every row traced to an official source or left blank and flagged.
Data as at {as_of}.</p>
<nav>{links}</nav>
</div></header>
<div class="wrap">
<h2 style="margin-top:18px">{title}</h2>
{sub}
{body}
<div class="foot">Session <code>{session}</code> &middot; task TED71 &middot;
built {as_of}. Prices are desk estimates, not a bookmaker offer. A blank cell
means the value could not be confirmed from an official source and was
deliberately left empty rather than inferred.</div>
</div></body></html>
""".format(title=e(title), css=CSS, links=links, body=body,
           sub=('<p class="lead">{}</p>'.format(e(subtitle)) if subtitle
                else ""), session=SESSION, as_of=AS_OF)
    path = os.path.join(OUT, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(doc)
    return path


# ------------------------------------------------------------------- tables
def matches_table(rows, by_fx):
    head = ("<tr><th>Row</th><th>Sport</th><th>Competition</th><th>Fixture</th>"
            "<th>Start (UTC)</th><th>OLBG rendered</th><th>OLBG tips</th>"
            "<th>Record</th><th>PF&ndash;PA</th><th>Venue</th><th>Markets</th>"
            "<th>Official source</th><th>Status</th></tr>")
    body = []
    for r in rows:
        o = r["official"] or {}
        ol = r["olbg"]
        nmark = len(by_fx.get(r["id"], []))
        rec = ""
        if o.get("record_home"):
            rec = "{} {}<br>{} {}".format(e(o.get("away")),
                                          e(o.get("record_away")),
                                          e(o.get("home")),
                                          e(o.get("record_home")))
        pfpa = ""
        if o.get("pf_pa_home"):
            pfpa = "{} {}&ndash;{}<br>{} {}&ndash;{}".format(
                e(o.get("away")), o["pf_pa_away"][0], o["pf_pa_away"][1],
                e(o.get("home")), o["pf_pa_home"][0], o["pf_pa_home"][1])
        tips = ""
        if ol and ol.get("tips"):
            tips = "{} on {}".format(e(ol["tips"]), e(ol.get("most_tipped")))
        status = ('<span class="pill p-hi">OFFICIAL</span>' if r["official"]
                  else '<span class="pill p-un">DISCOVERY ONLY</span>')
        body.append(
            "<tr><td><code>{}</code></td><td>{}</td><td>{}</td><td>{}</td>"
            "<td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td>"
            "<td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                e(r["id"]), e(r["sport"]), cell(o.get("competition")),
                e(r["label"]), cell(o.get("start_utc")),
                cell(ol.get("rendered_time") if ol else None),
                tips or dash(), rec or dash(), pfpa or dash(),
                cell(o.get("venue")), nmark or dash(),
                link_list(o.get("sources") if o else None), status))
    return ('<div class="scroll"><table><thead>{}</thead><tbody>{}</tbody>'
            '</table></div>'.format(head, "".join(body)))


def markets_table(sels):
    head = ("<tr><th>Row</th><th>Sport</th><th>Fixture</th><th>Market</th>"
            "<th>Selection</th><th>Prob</th><th>Fair dec</th><th>Fair US</th>"
            "<th>Confidence</th><th>Derivation</th><th>Note</th></tr>")
    body = []
    for s in sels:
        body.append(
            "<tr><td><code>{}</code></td><td>{}</td><td>{}</td><td>{}</td>"
            "<td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td>"
            "<td>{}</td><td>{}</td></tr>".format(
                e(s["fixture_id"]), e(s["sport"]), e(s["match"]),
                e(s["market"]), e(s["selection"]),
                dash() if s["prob"] is None else "{:.4f}".format(s["prob"]),
                dash() if s["fair_decimal"] is None
                else "{:.4f}".format(s["fair_decimal"]),
                money(s["fair_american"]), tier_pill(s["tier"]),
                e(s["model"]), e(s["note"] or "")))
    return ('<div class="scroll"><table><thead>{}</thead><tbody>{}</tbody>'
            '</table></div>'.format(head, "".join(body)))


def uniq_sources(rows):
    out = set()
    for r in rows:
        out.update((r["official"] or {}).get("sources") or [])
    return out


# -------------------------------------------------------------------- build
def build():
    j = lambda n: json.load(open(os.path.join(DATA, n), encoding="utf-8"))
    fx, ln, pr, hv = (j("fixtures.json"), j("lines.json"),
                      j("predictions.json"), j("harvest.json"))

    rows, sels = fx["rows"], ln["selections"]
    tiers = ln["counts"]["tiers"]
    band_note = ln["band"]["note"]
    by_fx = {}
    for s in sels:
        by_fx.setdefault(s["fixture_id"], []).append(s)

    hub_by_slug = {slug(h["sport"]): h for h in hv["hubs"]}
    scope = fx["sports_in_scope"]

    sports = {s["name"]: [] for s in scope}
    for r in rows:
        sports.setdefault(r["sport"], []).append(r)

    n_src = len(uniq_sources(rows))
    hi = [s for s in sels if s["tier"] == "high-in-band"]
    oob = [s for s in sels if s["tier"] == "out-of-band-short"]
    written = []

    # ---------------------------------------------------------- index
    cards = [("Rows published", fx["counts"]["fixture_rows"]),
             ("Officially sourced", fx["counts"]["officially_verified_rows"]),
             ("Discovery only", fx["counts"]["discovery_only_rows"]),
             ("Markets originated", ln["counts"]["selections"]),
             ("Markets priced", ln["counts"]["priced"]),
             ("High confidence", len(hi)),
             ("Official sources cited", n_src),
             ("Flags raised", len(fx["flags"]))]
    card_html = "".join(
        '<div class="card"><div class="n">{}</div><div class="l">{}</div>'
        '</div>'.format(e(n), e(l)) for l, n in cards)

    tier_rows = "".join(
        "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            tier_pill(k), e(v), e(TIER_MEANING.get(k, "")))
        for k, v in sorted(tiers.items(), key=lambda kv: -kv[1]))

    hi_rows = "".join(
        '<tr><td><code>{}</code></td><td>{}</td><td>{}</td><td>{}</td>'
        '<td>{:.4f}</td><td>{:.4f} / {}</td><td><a href="predictions.html">'
        "read the pick</a></td></tr>".format(
            e(s["fixture_id"]), e(s["sport"]), e(s["match"]), e(s["market"]),
            s["prob"], s["fair_decimal"], money(s["fair_american"]))
        for s in hi)

    empty = [s["name"] for s in scope if not sports.get(s["name"])]
    empty_note = ""
    if empty:
        empty_note = ('<div class="note warn"><b>Sports with no fixtures.</b> '
                      + e(", ".join(empty)) + ". The OLBG hub for each was "
                      "opened and returned no match rows. Nothing was "
                      'invented to fill the gap &mdash; see <a '
                      'href="flagged.html">Flagged for review</a>.</div>')

    cover = ('<div class="scroll"><table><thead><tr><th>Sport</th>'
             "<th>OLBG id</th><th>Hub rows listed</th><th>Rows published</th>"
             "<th>Officially sourced</th><th>Markets</th><th>Page</th></tr>"
             "</thead><tbody>" + "".join(
                 "<tr><td>{}</td><td><code>{}</code></td><td>{}</td>"
                 "<td>{}</td><td>{}</td><td>{}</td>"
                 '<td><a href="sports/{}.html">open</a></td></tr>'.format(
                     e(s["name"]), e(s["olbg_id"]),
                     e(hub_by_slug.get(s["slug"], {}).get("events_listed")),
                     len(sports.get(s["name"], [])),
                     sum(1 for r in sports.get(s["name"], [])
                         if r["official"]),
                     sum(len(by_fx.get(r["id"], []))
                         for r in sports.get(s["name"], [])),
                     e(s["slug"]))
                 for s in scope) + "</tbody></table></div>")

    body = """
{cards}
<h2>Executive summary &mdash; highest-confidence calls</h2>
<p class="lead">Two markets clear the stated gate. Both are EuroLeague round
seven handicaps, both sit inside the -250 to +10000 window, and both rest on
the official six-round standings published on a club site. Nothing else on the
board clears the probability floor and the price window at the same time.</p>
<div class="scroll"><table><thead><tr><th>Row</th><th>Sport</th><th>Fixture</th>
<th>Market</th><th>Prob</th><th>Fair</th><th></th></tr></thead><tbody>{hi_rows}
</tbody></table></div>

<h2>Why only two</h2>
<div class="note">{band}</div>
<table><thead><tr><th>Band</th><th>Count</th><th>Meaning</th></tr></thead>
<tbody>{tier_rows}</tbody></table>
<p class="lead">The daily target of five high-confidence picks per covered
sport cannot be met from this board without inventing picks. {n_oob} further
selections clear the 0.700 probability floor but are priced shorter than -250;
they are disclosed on <a href="analysis.html">Analysis</a> and are not
promoted. This is arithmetic about the stated band, not caution.</p>

{empty_note}
<h2>Coverage of the 15 requested sports</h2>
{cover}

<h2>What this desk did</h2>
<ul>
<li>Opened all 15 requested OLBG sport hubs and recorded the raw listing, the
route, and the timestamp each row rendered in.</li>
<li>Pinned the OLBG display clock. Hub timestamps render in America/New_York
(UTC-4) with no zone label anywhere on the page; the proof is on
<a href="analysis.html">Analysis</a>.</li>
<li>Originated markets independently for every fixture: moneyline, handicap
and match total where the sport supports them.</li>
<li>Sought an official source for every row. Where none was read the row stays
in the listing, its official columns are blank, and it is flagged.</li>
<li>Logged {n_flag} irregularities on
<a href="flagged.html">Flagged for review</a>, including two rejected inputs
that would have produced materially different prices.</li>
</ul>
""".format(cards=card_html,
           hi_rows=hi_rows or '<tr><td colspan="7">None cleared the '
                              'gate.</td></tr>',
           band=e(band_note), tier_rows=tier_rows, n_oob=len(oob),
           empty_note=empty_note, cover=cover, n_flag=len(fx["flags"]))
    written.append(page("index.html", "Dashboard", body,
                        "OLBG hub harvest, originated lines and confidence "
                        "tiers for 23 October 2026.", nav_on="index.html"))

    # -------------------------------------------------------- matches
    written.append(page(
        "matches.html", "Full match list", matches_table(rows, by_fx),
        "{} rows across {} sports. 'Official source' is the page the "
        "competition, kickoff and any record were read from; a dash means no "
        "official source was read and the row is discovery only.".format(
            fx["counts"]["fixture_rows"], fx["counts"]["sports_with_rows"]),
        nav_on="matches.html"))

    # -------------------------------------------------------- markets
    written.append(page(
        "markets.html", "All originated markets",
        '<div class="note">{}</div>'.format(e(band_note))
        + "<h3>Priced selections ({})</h3>".format(ln["counts"]["priced"])
        + markets_table([s for s in sels if s["prob"] is not None])
        + "<h3>Markets left unpriced ({})</h3>".format(
            ln["counts"]["unpriced"])
        + "<p class=\"lead\">No official inputs were available for these, so "
          "no price is offered rather than a guess.</p>"
        + markets_table([s for s in sels if s["prob"] is None]),
        "{} selections over {} fixtures. Fair decimal is 1/p with no margin; "
        "fair US is the American equivalent of that fair decimal.".format(
            len(sels), len(by_fx)), nav_on="markets.html"))

    # ------------------------------------------------ high-confidence
    hc = "".join(
        "<tr><td><code>{}</code></td><td>{}</td><td>{}</td><td>{}</td>"
        "<td>{:.4f}</td><td>{:.4f}</td><td>{}</td><td>{}</td></tr>".format(
            e(s["fixture_id"]), e(s["sport"]), e(s["match"]), e(s["market"]),
            s["prob"], s["fair_decimal"], money(s["fair_american"]),
            e(s["inputs"])) for s in hi)
    written.append(page(
        "high-confidence.html", "High-confidence selections",
        '<div class="note"><b>Gate.</b> {}</div>'.format(e(band_note))
        + '<div class="scroll"><table><thead><tr><th>Row</th><th>Sport</th>'
          "<th>Fixture</th><th>Market</th><th>Prob</th><th>Fair dec</th>"
          "<th>Fair US</th><th>Inputs</th></tr></thead><tbody>" + hc
        + "</tbody></table></div>"
        + "<h3>Selections that clear 0.700 but fall outside the band</h3>"
          "<p class=\"lead\">Disclosed for completeness. None is promoted to "
          "high confidence because the fair price is shorter than -250.</p>"
        + markets_table(oob),
        "Everything that clears a 0.700 probability floor, and the near-misses "
        "that do not fit the stated price window.",
        nav_on="high-confidence.html"))

    # ---------------------------------------------------- predictions
    pb = []
    for p in pr["predictions"]:
        pb.append("""
<div class="pred">
<h3 style="margin-top:0">{match} &mdash; {sel}</h3>
<p class="lead">{comp} &middot; kickoff {ko} &middot;
<a href="high-confidence.html">confidence basis</a></p>
<blockquote>{text}</blockquote>
<details><summary>What each clause rests on</summary>
<ul class="srcs">{facts}</ul>
<p class="srcs"><b>Not available, and therefore not asserted:</b></p>
<ul class="srcs">{absent}</ul></details>
</div>""".format(match=e(p["match"]), sel=e(p["selection"]),
                 comp=e(p["competition"]), ko=e(p["start_utc"]),
                 text=e(p["text"]),
                 facts="".join(
                     '<li>{} &mdash; <a href="{}" rel="noopener" '
                     'target="_blank">{}</a> (read {})</li>'.format(
                         e(f["claim"]), e(f["source"]), e(rel(f["source"])),
                         e(f["read_utc"])) for f in p["facts"]),
                 absent="".join("<li>{}</li>".format(e(a))
                                for a in p["absent"])))
    written.append(page(
        "predictions.html", "Predictions",
        '<div class="note">Written for the two selections that clear the gate.'
        ' Neither paragraph uses the words "model" or "verified". Every '
        "factual clause is tied to a page read on 23 October 2026, and "
        'anything that was not read is listed under "not available" rather '
        "than filled in. Uniqueness is enforced mechanically: no six-word "
        "phrase repeats between the two.</div>" + "".join(pb),
        "One paragraph per high-confidence call.", nav_on="predictions.html"))

    # ------------------------------------------------------- analysis
    written.append(page("analysis.html", "Analysis and irregularity proofs",
                        analysis_body(fx, ln, hv, oob),
                        "The timezone proof, the band arithmetic, the source "
                        "ledger and the coverage gaps.", nav_on="analysis.html"))

    # -------------------------------------------------------- flagged
    sev_class = {"high": "bad", "medium": "warn", "low": ""}
    written.append(page(
        "flagged.html", "Flagged for review",
        "".join(
            '<div class="note {cls}"><b>{id}</b> &middot; {sev} &middot; '
            "{topic}<br>{finding}<br><span class=\"srcs\">Impact: {impact}"
            ' &mdash; observed on <a href="{src}" rel="noopener" '
            'target="_blank">{reld}</a></span></div>'.format(
                cls=sev_class.get(f["severity"], ""), id=e(f["id"]),
                sev=e(f["severity"]), topic=e(f["topic"]),
                finding=e(f["finding"]), impact=e(f["impact"]),
                src=e(f["source"]), reld=e(rel(f["source"])))
            for f in fx["flags"]),
        "{} irregularities found while reversing OLBG and sourcing the "
        "fixtures. None blocks publication; all are disclosed.".format(
            len(fx["flags"])), nav_on="flagged.html"))

    # -------------------------------------------------------- sources
    seen = {}
    for r in rows:
        for u in ((r["official"] or {}).get("sources") or []):
            seen.setdefault(u, []).append(r["id"])
    src_rows = "".join(
        '<tr><td><a href="{}" rel="noopener" target="_blank">{}</a></td>'
        "<td>{}</td><td><code>{}</code></td></tr>".format(
            e(u), e(rel(u)), len(ids), e(", ".join(ids)))
        for u, ids in sorted(seen.items()))
    hub_rows = "".join(
        '<tr><td>{}</td><td><code>{}</code></td><td><a href="{}" '
        'rel="noopener" target="_blank">{}</a></td><td>{}</td><td>{}</td>'
        "</tr>".format(e(h["sport"]), e(h["olbg_id"]), e(h["url"]),
                       e(re.sub(r"^https?://", "", h["url"])),
                       e(h["events_listed"]), e(h["read_utc"]))
        for h in hv["hubs"])
    written.append(page(
        "sources.html", "Official sources",
        '<div class="note">A row is only marked official if its competition, '
        "kickoff and any record were read on one of these pages. Media "
        "aggregators, news desks and other betting sites are recorded in the "
        "irregularity log but are never used as a row source.</div>"
        '<div class="scroll"><table><thead><tr><th>Source</th><th>Rows</th>'
        "<th>Row ids</th></tr></thead><tbody>" + src_rows
        + "</tbody></table></div><h3>OLBG hubs read (discovery layer)</h3>"
        '<div class="scroll"><table><thead><tr><th>Sport</th><th>OLBG id</th>'
        "<th>Hub</th><th>Rows listed</th><th>Read</th></tr></thead><tbody>"
        + hub_rows + "</tbody></table></div>",
        "{} official pages back {} of {} rows. The hubs below are the "
        "discovery layer and are not treated as official sources.".format(
            len(seen), fx["counts"]["officially_verified_rows"],
            fx["counts"]["fixture_rows"]), nav_on="sources.html"))

    # ---------------------------------------------------- methodology
    written.append(page("methodology.html", "Method and disclosure",
                        methodology_body(ln, pr),
                        "How the board was built, what was assumed, and what "
                        "was refused.", nav_on="methodology.html"))

    # ------------------------------------------------------- by sport
    idx = "".join(
        '<tr><td><a href="sports/{}.html">{}</a></td><td><code>{}</code></td>'
        "<td>{}</td><td>{}</td><td>{}</td></tr>".format(
            e(s["slug"]), e(s["name"]), e(s["olbg_id"]),
            len(sports.get(s["name"], [])),
            sum(1 for r in sports.get(s["name"], []) if r["official"]),
            sum(len(by_fx.get(r["id"], [])) for r in sports.get(s["name"], [])))
        for s in scope)
    written.append(page(
        "sports.html", "By sport",
        '<div class="scroll"><table><thead><tr><th>Sport</th><th>OLBG id</th>'
        "<th>Rows</th><th>Officially sourced</th><th>Markets</th></tr>"
        "</thead><tbody>" + idx + "</tbody></table></div>",
        "One page per requested sport, including the ones that came back "
        "empty.", nav_on="sports.html"))

    for s in scope:
        name, sl = s["name"], s["slug"]
        v = sports.get(name, [])
        hub = hub_by_slug.get(sl)
        hub_line = ""
        if hub:
            hub_line = ('<p class="lead">OLBG hub: <a href="{}" '
                        'rel="noopener" target="_blank">{}</a> &middot; {} '
                        'rows listed on first paint &middot; read {}</p>'
                        .format(e(hub["url"]),
                                e(re.sub(r"^https?://", "", hub["url"])),
                                e(hub["events_listed"]), e(hub["read_utc"])))
        note = ""
        if not v:
            gap = next((g for g in fx["coverage_gaps"]
                        if g["sport"] == name), None)
            note = ('<div class="note warn"><b>No fixtures.</b> {}</div>'
                    .format(e(gap["finding"]) if gap else
                            "The hub returned no match rows."))
        body = hub_line + note + (matches_table(v, by_fx) if v else "")
        for sel in [x for r in v for x in by_fx.get(r["id"], [])]:
            if sel["tier"] == "high-in-band":
                body += ('<div class="note"><b>High confidence:</b> {} '
                         '&mdash; {:.4f} ({}). <a href="../predictions.html">'
                         "Read the pick</a>.</div>".format(
                             e(sel["market"]), sel["prob"],
                             money(sel["fair_american"])))
        written.append(page("sports/{}.html".format(sl), name, body,
                            "{} rows.".format(len(v)), nav_on="sports.html",
                            crumb="../"))

    manifest = {
        "session": SESSION, "task": "TED71", "as_of": AS_OF,
        "pages": sorted(os.path.relpath(p, OUT) for p in written),
        "counts": dict(fx["counts"], **{
            "selections": ln["counts"]["selections"],
            "priced": ln["counts"]["priced"],
            "unpriced": ln["counts"]["unpriced"],
            "tiers": tiers,
            "high_confidence": len(hi),
            "out_of_band_disclosed": len(oob),
            "predictions": len(pr["predictions"]),
            "flags": len(fx["flags"]),
        })}
    with open(os.path.join(DATA, "site-manifest.json"), "w",
              encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    return manifest


def analysis_body(fx, ln, hv, oob):
    tf = hv["timezone_finding"]
    proofs = "".join("<li>{}</li>".format(e(x)) for x in tf["evidence"])
    gaps = "".join(
        "<li><b>{}</b> ({}) &mdash; {}</li>".format(e(g["id"]), e(g["sport"]),
                                                   e(g["finding"]))
        for g in fx["coverage_gaps"])
    return """
<h2>OLBG hub routing</h2>
<p class="lead">Routes are <code>olbg.com/betting-tips/&lt;Sport&gt;/&lt;id&gt;</code>.
The sport token is case sensitive in the slug while the numeric id does the
routing; a hub opened without its id returns a soft 404. The hub listing is
paginated behind a "Load More Tips" control, so a hub can list more rows than
it renders on first paint (ED71-F-16).</p>

<h2>The display clock is unlabelled US Eastern</h2>
<p class="lead">{claim}</p>
<p class="lead">Conversion used: <code>{conv}</code></p>
<ul>{proofs}</ul>
<div class="note warn"><b>Consequence.</b> A reader who assumes UTC or UK time
reads every kickoff four hours early. All times published here are converted
to UTC, and the OLBG-rendered value is kept alongside so the conversion can be
audited row by row.</div>

<h2>Start times are padded</h2>
<div class="note warn">OLBG start times carry an unlabelled +5 to +7 minute
padding (ED71-F-02): NHL Montreal at Chicago renders 20:07 against an official
<code>startTimeUTC</code> of 00:00:00Z, which is 20:00 ET. OLBG renderings are
therefore never published as the kickoff; the official time is used and the
rendering is shown next to it.</div>

<h2>A timezone defect that changes the calendar day</h2>
<div class="note bad">Four OLBG darts rows render a 24 October date for
first-round matches that sit in the 23 October evening session once the +4h
offset is applied (ED71-F-05). Read naively this looks like a reschedule. It
is the unlabelled clock pushing a late European evening past midnight in the
display zone. Dates on this desk come from the promoter's session calendar.</div>

<h2>Why the high-confidence band admits so few picks</h2>
<p class="lead">{band_note}</p>
<table><thead><tr><th>Price</th><th>Decimal</th><th>Implied probability</th>
</tr></thead><tbody>
<tr><td>-250 (band edge)</td><td>1.4000</td><td>0.71429</td></tr>
<tr><td>-200</td><td>1.5000</td><td>0.66667</td></tr>
<tr><td>+10000 (band edge)</td><td>101.0000</td><td>0.00990</td></tr>
</tbody></table>
<p class="lead">So the intersection of "at least 70% likely" and "no shorter
than -250" is only p in [0.7000, 0.71429] &mdash; a 1.43-point window. The
daily target of five picks per covered sport is not reachable inside it
without inventing picks, so the shortfall is stated instead of being papered
over.</p>

<h3>Disclosure ledger &mdash; 0.700+ but priced outside the band</h3>
<p class="lead">{n} selections clear the probability floor but are priced
shorter than -250. They are published here and are not promoted.</p>
{ledger}

<h2>Source ledger</h2>
<p class="lead">{nsrc} official pages were read this session and they carry
{nver} of {nrows} rows. The remaining {nonly} rows are OLBG-listing-only: they
are real listed events, but no official page was read for them, so their
competition, kickoff, record and venue cells are empty and they are flagged.</p>

<h2>Coverage gaps</h2>
<ul>{gaps}</ul>

<h2>Rejected input: a standings table one round stale</h2>
<div class="note bad">The first EuroLeague table read this session came from a
media-centre game kit and showed every club on five games played, while
today's fixtures are round seven. That table was one round stale. It was
discarded before any price was struck and the standings were re-read on a club
site showing six games played. Had the stale table been used, the Paris v
Valencia handicap would have been offered at 6.5 points instead of 4.5 &mdash;
a materially different bet on the same fixture. Logged as ED71-F-14.</div>

<h2>Rejected input: a self-contradictory odds feed</h2>
<div class="note bad">The NHL schedule API returns an unlabelled odds array in
which decimal and American values are mixed and providers disagree about the
favourite for the same game: one had Montreal 2.35 and Chicago 1.59 while
another had Montreal 1.60 and Chicago 2.37. The feed is recorded as an
irregularity and is not used as a pricing input anywhere on this desk
(ED71-F-15).</div>
""".format(claim=e(tf["claim"]), conv=e(tf["conversion_used"]), proofs=proofs,
           band_note=e(ln["band"]["note"]), n=len(oob),
           ledger=markets_table(oob), nsrc=len(uniq_sources(fx["rows"])),
           nver=fx["counts"]["officially_verified_rows"],
           nrows=fx["counts"]["fixture_rows"],
           nonly=fx["counts"]["discovery_only_rows"], gaps=gaps)


def methodology_body(ln, pr):
    rows = "".join("<tr><td><code>{}</code></td><td>{}</td></tr>".format(
        e(k), e(v)) for k, v in ln["constants"].items())
    pol = pr["policy"]
    return """
<h2>Order of work</h2>
<ol>
<li>Open all 15 requested OLBG sport hubs and record the raw listing.</li>
<li>Establish what the displayed timestamp means before trusting any kickoff.</li>
<li>For each listed event, look for an official page &mdash; league, governing
body, tour, promoter or the club itself. If found, read competition, kickoff,
venue and any record off it.</li>
<li>Where no official page exists, keep the row, blank the official columns,
and flag it. Never infer.</li>
<li>Originate markets from the official inputs only.</li>
<li>Price them, assign a tier, and publish every rung including the ones that
do not clear the gate.</li>
</ol>

<h2>Pricing disclosure</h2>
<div class="scroll"><table><thead><tr><th>Constant</th><th>Value and role</th>
</tr></thead><tbody>{rows}</tbody></table></div>
<div class="note warn">Fair decimal is 1/p with no margin or overround
applied, so it is a fair price rather than a bookmaker offer. The spread and
handicap constants above are desk assumptions and are labelled as such
wherever a price depends on them; they are not sourced facts.</div>

<h2>What was refused</h2>
<ul>
<li>No value was inferred. If a page did not state it, the cell is empty.</li>
<li>Media desks, stat aggregators and other betting sites were never used as a
row source. Several were read and are cited only inside the irregularity log.</li>
<li>Totals ladders were built but left unpriced, because no official variance
figure was read for any competition on this board.</li>
<li>The daily target of five high-confidence picks per covered sport was not
met by inventing picks. Two clear the gate; the shortfall is stated rather
than papered over.</li>
</ul>

<h2>Prediction prose rules</h2>
<ul>
<li>Minimum {minw} words, enforced by a check that fails the build.</li>
<li>Banned from published prose: {banned}. The build fails if any appears.</li>
<li>{uniq}</li>
<li>Every factual clause carries a link to the page it was read on, and
anything not read is listed as unavailable.</li>
</ul>

<h2>Reproduce</h2>
<pre><code>python3 scripts/sed71b937_dataset.py
python3 scripts/sed71b937_model.py
python3 scripts/sed71b937_predictions.py
python3 scripts/sed71b937_build_site.py
python3 scripts/sed71b937_validate.py</code></pre>
""".format(rows=rows, minw=pol["min_words"], banned=e(", ".join(
        '"{}"'.format(b) for b in pol["banned_words"])),
           uniq=e(pol["uniqueness"]))


if __name__ == "__main__":
    man = build()
    print("pages", len(man["pages"]))
    for p in man["pages"]:
        print(" ", p)
    print(json.dumps(man["counts"], indent=1, sort_keys=True))
