"""Session d7d19a67-olbg1 (TD7D19, claimed as T65) - static dashboard builder for the ``d7d19a67/`` desk.

Writes a self-contained desk: landing page, match list, market explorer, High-confidence page,
predictions, all-sports index plus one page per in-scope sport, analysis, sources, Flagged for
Review and the repository audit. No external font, script, stylesheet or backend call is used, so
the pages work from GitHub Pages under ``/OLBG1/d7d19a67/`` and from a local file server alike.

Inputs (never re-fetched, never edited here):
    data/d7d19a67/desk.json        built by scripts/sd7d19a67_model.py from scripts/sd7d19a67_data.py
    data/d7d19a67/repo_audit.json  built by scripts/sd7d19a67_repo_audit.py
    data/current/snapshot.json     read-only cross-check of the canonical pipeline's own prices

Run: python3 scripts/sd7d19a67_build_site.py
"""

import html
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sd7d19a67_data as D  # noqa: E402

DATA = os.path.join(ROOT, "data", "d7d19a67")
OUT = os.path.join(ROOT, "d7d19a67")
REPO_URL = "https://github.com/buffedlizard55-lab/OLBG1"

SPORTS = [
    ("tennis", "Tennis"), ("basketball", "Basketball"), ("golf", "Golf"), ("cricket", "Cricket"),
    ("snooker", "Snooker"), ("rugby-union", "Rugby Union"), ("rugby-league", "Rugby League"),
    ("baseball", "Baseball"), ("ice-hockey", "Ice Hockey"), ("motor-racing", "Motor Racing"),
    ("darts", "Darts"), ("handball", "Handball"), ("volleyball", "Volleyball"),
    ("aussie-rules", "Australian Rules"), ("esports", "eSports"),
    ("gaelic-football", "Gaelic Football"), ("greyhounds", "Greyhounds"),
]
EXCLUDED = ["soccer/football", "American football", "boxing", "UFC/MMA", "hurling", "horse racing",
            "cycling", "specials"]

NAV = [("index.html", "Overview"), ("matches.html", "Match list"), ("markets.html", "Market explorer"),
       ("high-confidence.html", "High confidence"), ("predictions.html", "Predictions"),
       ("sports.html", "All sports"), ("analysis.html", "Analysis"), ("sources.html", "Sources"),
       ("flagged.html", "Flagged for review"), ("repo-audit.html", "Repository audit")]

CSS = """
:root{--ink:#101820;--mut:#5b6b7b;--line:#dfe6ec;--bg:#f6f8fa;--card:#fff;--acc:#0b5f8a;
--hi:#0f7b4d;--hi-bg:#e7f6ee;--md:#8a5a00;--md-bg:#fdf3df;--lo:#5b6b7b;--lo-bg:#eef1f4;
--bad:#a02020;--bad-bg:#fdecec}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--acc)}
.skip{position:absolute;left:-9999px}
.skip:focus{left:8px;top:8px;background:#fff;padding:8px;z-index:9}
.topbar{display:flex;flex-wrap:wrap;gap:12px;justify-content:space-between;align-items:center;
background:#0d1b26;color:#eaf1f6;padding:14px 20px}
.brand{display:flex;gap:10px;align-items:center}
.mark{width:12px;height:12px;border-radius:3px;background:#4ea3d1;display:inline-block}
.brand strong{display:block;font-size:16px;letter-spacing:.2px}
.brand small{color:#9fb6c6;font-size:12px}
.meta{font-size:12px;color:#9fb6c6}
.dot{display:inline-block;width:7px;height:7px;border-radius:50%;background:#4ea3d1;margin-right:6px}
.nav{display:flex;flex-wrap:wrap;gap:4px;background:#12283a;padding:8px 16px}
.nav-link{color:#cfe0ec;text-decoration:none;font-size:13px;padding:6px 10px;border-radius:6px}
.nav-link:hover{background:#1b3b52}
.nav-link.active{background:#4ea3d1;color:#08131c;font-weight:600}
main{max-width:1180px;margin:0 auto;padding:22px 20px 60px}
.page-head .eyebrow{color:var(--mut);font-size:12px;text-transform:uppercase;letter-spacing:.08em;margin:0}
h1{font-size:26px;margin:6px 0 8px}
h2{font-size:19px;margin:30px 0 8px;padding-bottom:6px;border-bottom:1px solid var(--line)}
h3{font-size:16px;margin:20px 0 6px}
.lede{color:var(--mut);max-width:80ch;margin:0 0 6px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin:14px 0}
.grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));margin:14px 0}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.kpi b{display:block;font-size:24px;line-height:1.2}
.kpi span{color:var(--mut);font-size:12px}
table{width:100%;border-collapse:collapse;background:var(--card);font-size:13.5px;margin:10px 0}
caption{caption-side:top;text-align:left;color:var(--mut);font-size:12.5px;padding:4px 0}
th,td{border-bottom:1px solid var(--line);padding:7px 8px;text-align:left;vertical-align:top}
th{background:#eef3f7;font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:#33475b}
tbody tr:hover{background:#fafcfe}
.num{text-align:right;font-variant-numeric:tabular-nums}
.wrap{overflow-x:auto}
.badge{display:inline-block;padding:2px 8px;border-radius:999px;font-size:11.5px;font-weight:700;
letter-spacing:.02em;white-space:nowrap}
.t-high{background:var(--hi-bg);color:var(--hi)}
.t-medium{background:var(--md-bg);color:var(--md)}
.t-low{background:var(--lo-bg);color:var(--lo)}
.t-none{background:#fff;color:var(--mut);border:1px dashed var(--line)}
.flag{background:var(--bad-bg);color:var(--bad);border-radius:4px;padding:1px 5px;font-size:11px;
font-weight:700;white-space:nowrap}
.blank{color:var(--mut);font-style:italic}
.note{border-left:3px solid var(--acc);background:#eef6fb;padding:10px 12px;border-radius:0 8px 8px 0;
margin:12px 0;font-size:13.5px}
.warn{border-left:3px solid var(--bad);background:var(--bad-bg);padding:10px 12px;border-radius:0 8px 8px 0;
margin:12px 0;font-size:13.5px}
.ok{border-left:3px solid var(--hi);background:var(--hi-bg);padding:10px 12px;border-radius:0 8px 8px 0;
margin:12px 0;font-size:13.5px}
.pred{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:14px 0}
.pred p.text{font-size:15.5px;line-height:1.65;margin:8px 0 10px}
.pred .who{font-size:12px;color:var(--mut);text-transform:uppercase;letter-spacing:.05em}
ul{margin:8px 0 8px 20px;padding:0}
li{margin:3px 0}
code{background:#eef1f4;border-radius:4px;padding:1px 5px;font-size:12.5px}
pre{background:#0d1b26;color:#dce8f1;padding:10px 12px;border-radius:8px;overflow-x:auto;font-size:12.5px}
.muted{color:var(--mut);font-size:12.5px}
.foot{border-top:1px solid var(--line);margin-top:30px;padding:16px 20px;color:var(--mut);font-size:12.5px;
max-width:1180px;margin-left:auto;margin-right:auto}
.sev-high{color:var(--bad);font-weight:700}
.sev-medium{color:var(--md);font-weight:700}
.sev-low{color:var(--mut);font-weight:700}
.sev-info{color:var(--acc);font-weight:700}
"""


def e(x):
    return html.escape("" if x is None else str(x), quote=True)


def money(a):
    if a in (None, ""):
        return '<span class="blank">—</span>'
    a = int(a)
    return ("+%d" % a) if a > 0 else str(a)


def pct(p):
    return '<span class="blank">—</span>' if p in (None, "") else "%.1f%%" % (100.0 * float(p))


def dec(x):
    return '<span class="blank">—</span>' if x in (None, "") else "%.4f" % float(x)


def badge(t):
    cls = {"High": "t-high", "Medium": "t-medium", "Low": "t-low"}.get(str(t).split(" ")[0], "t-none")
    return '<span class="badge %s">%s</span>' % (cls, e(t or "no pick"))


def when(f):
    if f.get("time_utc"):
        dt = datetime.strptime(f["time_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        out = dt.strftime("%a %d %b %Y · %H:%M UTC")
        if f.get("time_local"):
            out += " <span class='muted'>(%s)</span>" % e(f["time_local"])
        return out
    if f.get("time_local"):
        return "%s <span class='muted'>(official clock, no timezone published)</span>" % e(f["time_local"])
    return '<span class="blank">time not published</span>'


def matchup(f):
    a, h = f.get("away"), f.get("home")
    if a and h:
        return "%s <span class='muted'>v</span> %s" % (e(a), e(h))
    if h:
        return '<span class="blank">away not read</span> <span class="muted">at</span> %s' % e(h)
    if a:
        return "%s <span class='muted'>v</span> <span class='blank'>home not read</span>" % e(a)
    return e(f.get("competition") or "—")


def link(url, label=None):
    if not url:
        return '<span class="blank">no official link</span>'
    return '<a href="%s" rel="noopener noreferrer">%s</a>' % (e(url), e(label or url.replace("https://", "")))


def cell(v, fallback="&mdash;"):
    """Render a table cell value; an unconfirmed value becomes an explicit blank marker."""
    if v is None or v == "":
        return '<span class="blank">%s</span>' % fallback
    return e(v)


def flags_cell(flags, prefix=""):
    if not flags:
        return '<span class="muted">none</span>'
    return " ".join('<a class="flag" href="%sflagged.html#%s">%s</a>' % (prefix, e(f), e(f))
                    for f in flags)


class Site:
    def __init__(self):
        self.desk = json.load(open(os.path.join(DATA, "desk.json"), encoding="utf-8"))
        self.audit = json.load(open(os.path.join(DATA, "repo_audit.json"), encoding="utf-8"))
        self.snap = None
        sp = os.path.join(ROOT, "data", "current", "snapshot.json")
        if os.path.exists(sp):
            try:
                self.snap = json.load(open(sp, encoding="utf-8"))
            except Exception:
                self.snap = None
        self.fixtures = self.desk["fixtures"]
        self.counts = self.desk["counts"]
        self.src = {s["id"]: s for s in self.desk["sources"]}
        self.preds = self.desk["predictions"]
        self.preds_by_market = {p["market_id"]: p for p in self.preds}
        self.head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                                   text=True).stdout.strip()[:12]
        self.built_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # ------------------------------------------------------------------ shell
    def page(self, title, active, body, subtitle="", prefix=""):
        nav = "".join('<a class="nav-link%s" href="%s%s">%s</a>'
                      % (" active" if href == active else "", prefix, href, e(label))
                      for href, label in NAV)
        return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'none'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'">
<title>%s · OLBG research desk d7d19a67</title>
<link rel="stylesheet" href="%sassets/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="topbar">
  <div class="brand"><span class="mark" aria-hidden="true"></span>
    <span><strong>OLBG research desk d7d19a67</strong><small>independent · official sources only · lines originated, never copied</small></span>
  </div>
  <div class="meta"><span class="dot"></span> official reads %s · desk assembled %s</div>
</header>
<nav class="nav" aria-label="Desk sections">%s</nav>
<main id="main">
<header class="page-head">
  <p class="eyebrow">Session d7d19a67-olbg1 · task TD7D19 · rolling window %s to %s</p>
  <h1>%s</h1>
  %s
</header>
%s
</main>
<footer class="foot">
  <p>Independent research desk. Not affiliated with OLBG.com; OLBG was used only to enumerate which
  sports exist. No bookmaker price, no availability and no betting edge is claimed anywhere on this
  desk: every number is this desk's own originated fair price (decimal = 1 / probability, no margin).
  Not staking advice. 18+.</p>
  <p class="muted">Official reads %s · desk built %s · repository audit %s · branch
  <code>arena/d7d19a67-olbg1</code> at <code>%s</code></p>
</footer>
</body>
</html>
""" % (e(title), prefix, e(D.DESK_READ_UTC), e(self.built_at), nav,
       e(D.WINDOW_FROM_UTC), e(D.WINDOW_UNTIL_UTC), e(title),
       ('<p class="lede">%s</p>' % subtitle) if subtitle else "", body,
       e(D.DESK_READ_UTC), e(self.built_at), e(self.audit.get("generated_at_utc", "")), e(self.head))

    def write(self, name, text):
        path = os.path.join(OUT, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        return path

    # ------------------------------------------------------------------ index
    def index(self):
        c = self.counts
        kpis = [
            (c["fixtures"], "fixture listings published"),
            (c["priced"], "matches with originated lines"),
            (c["markets"], "markets originated"),
            (c["outcomes"], "priced outcomes"),
            (c["high"], "High-confidence winner picks"),
            (c["medium"], "Medium"),
            (c["low"], "Low"),
            (len(self.preds), "hand-written predictions"),
            (len(self.desk["sources"]), "official source reads"),
            (len(self.desk["gaps"]), "coverage gaps"),
            (len(self.desk["flags"]), "flags for review"),
            (len(self.audit["findings"]), "repository audit findings"),
        ]
        grid = "".join('<div class="kpi"><b>%s</b><span>%s</span></div>' % (e(v), e(l)) for v, l in kpis)
        cov = []
        for slug, name in SPORTS:
            s = self.desk["per_sport"].get(slug)
            gap = next((g for g in self.desk["gaps"] if g["sport"] == slug), None)
            if s:
                cov.append((name, slug, s["fixtures"], s["priced"], s["markets"], s["high"], s["medium"],
                            s["low"], "covered", s.get("olbg_hub")))
            else:
                cov.append((name, slug, 0, 0, 0, 0, 0, 0,
                            "gap — %s" % (gap["status"] if gap else "not attempted"),
                            gap["olbg_hub"] if gap else None))
        rows = "".join(
            "<tr><td><a href=\"sports/%s.html\">%s</a></td>"
            "<td class=\"num\">%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td>"
            "<td class=\"num\">%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td>"
            "<td>%s</td><td>%s</td></tr>"
            % (e(slug), e(name), e(fx or "—"), e(pr or "—"), e(mk or "—"), e(h or "—"), e(m or "—"),
               e(l or "—"), e(status), link(hub, "OLBG hub") if hub else '<span class="blank">—</span>')
            for name, slug, fx, pr, mk, h, m, l, status, hub in cov)
        highs = [f for f in self.fixtures if f["winner_pick"] and f["winner_pick"]["tier"] == "High"]
        hrows = "".join(
            "<tr><td>%s</td><td>%s</td><td>%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td>"
            "<td class=\"num\">%s</td><td>%s</td><td>%s</td></tr>"
            % (when(f), matchup(f), e(f["winner_pick"]["selection"]), pct(f["winner_pick"]["probability"]),
               dec(f["winner_pick"]["fair_decimal"]), money(f["winner_pick"]["fair_american"]),
               badge("High"), link(f["official_link"], "official fixture"))
            for f in highs)
        gateA = [(f, mk, o) for f in self.fixtures for mk in f["markets"] for o in mk["outcomes"]
                 if o["probability"] > 0.70 and o["in_brief_window"]]
        garows = "".join(
            "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td class=\"num\">%s</td>"
            "<td class=\"num\">%s</td><td>%s</td></tr>"
            % (when(f), matchup(f), e(mk["market"]), e(o["selection"]), pct(o["probability"]),
               money(o["fair_american"]), link(f["official_link"], "official fixture"))
            for f, mk, o in gateA)
        body = """
<div class="grid">%s</div>

<div class="card">
<h3>What this desk is</h3>
<p>Every row below was read from an official source during this session - a league or governing body
publishing its own fixtures and statistics - on <strong>%s</strong>, and every price is originated here
from those reads. OLBG.com was used for one purpose only: to enumerate which sports exist and what its
hub URLs are, so the coverage table can be compared against the brief. No tip, no price and no
probability was taken from OLBG or from any operator.</p>
<p>Scope: the seventeen in-scope sports. Excluded as instructed: %s. Fixtures are the ones dated
<strong>%s to %s</strong> on the official page named in each row.</p>
</div>

<div class="warn"><strong>Read this before using any number here.</strong> Three models
(<code>nhl-poisson-v1</code>, <code>mlb-poisson-v1</code>, <code>el-log5-v1</code>) are independent
Poisson or log5 constructions built from official season totals. They are <strong>not calibrated
out-of-sample</strong>, they carry no home-ice or home-field adjustment, and no bookmaker price was
available to compare them with. A &ldquo;High&rdquo; label on this desk means <em>our own price sits
inside the brief&rsquo;s &minus;250&hellip;+10000 window and every input was officially read this
session</em> &mdash; it does not mean a measured 60&nbsp;%% hit rate. See
<a href="analysis.html">Analysis</a> and <a href="flagged.html">Flagged for review</a>.</div>

<h2>Coverage by sport</h2>
<div class="wrap"><table>
<caption>Seventeen in-scope sports. A gap is not a finding that the sport has no fixtures; each gap on
the <a href="flagged.html">Flagged page</a> names the official URL attempted and what failed.</caption>
<thead><tr><th>Sport</th><th class="num">Listings</th><th class="num">Priced</th><th class="num">Markets</th>
<th class="num">High</th><th class="num">Medium</th><th class="num">Low</th><th>Status</th>
<th>OLBG hub (discovery only)</th></tr></thead>
<tbody>%s</tbody></table></div>

<h2>High-confidence picks</h2>
<div class="wrap"><table>
<caption>Winner-market picks whose originated price expresses inside &minus;250&hellip;+10000 and whose
fixture and both sides&rsquo; statistics were read from official pages this session. Each carries a
unique hand-written prediction of at least 30 words.</caption>
<thead><tr><th>Start (UTC)</th><th>Match</th><th>Selection</th><th class="num">Our probability</th>
<th class="num">Fair decimal</th><th class="num">Fair American</th><th>Tier</th>
<th>Official source</th></tr></thead>
<tbody>%s</tbody></table></div>
<p class="muted">Full reasoning, facts used and prose for each: <a href="high-confidence.html">High
confidence</a> and <a href="predictions.html">Predictions</a>.</p>

<h2>The brief&rsquo;s literal rule, applied</h2>
<p>The brief asks for High-confidence picks on matches between &minus;250 and +10000 and notes that many
High picks elsewhere are simply &ldquo;greater than 70&nbsp;%% chance based on market prices&rdquo;. Those
two conditions overlap in a very thin band: a probability above 70&nbsp;%% is a price shorter than
&minus;233, so <em>above 70&nbsp;%% <strong>and</strong> inside &minus;250&hellip;+10000</em> leaves only
&minus;250&hellip;&minus;233 (70.0&ndash;71.4&nbsp;%%). This desk publishes both readings rather than
picking one silently:</p>
<div class="wrap"><table>
<caption>Every selection anywhere on this desk that satisfies the literal rule (probability &gt; 70&nbsp;%%
<strong>and</strong> originated price inside &minus;250&hellip;+10000). Count: %d.</caption>
<thead><tr><th>Start (UTC)</th><th>Match</th><th>Market</th><th>Selection</th>
<th class="num">Probability</th><th class="num">Fair American</th><th>Official source</th></tr></thead>
<tbody>%s</tbody></table></div>
<p>The seven published High picks instead satisfy the brief&rsquo;s <em>window</em> condition plus an
evidence test, at probabilities of 60.0&ndash;69.2&nbsp;%% (prices &minus;150 to &minus;225). Thirteen
further selections are stronger than 71.4&nbsp;%% and therefore <strong>outside</strong> the window: they
are listed as out-of-window favourites on the
<a href="high-confidence.html">High-confidence page</a>, not hidden. The tension itself is flagged as
<a class="flag" href="flagged.html#F-D7D-10">F-D7D-10</a>.</p>

<h2>Cross-check against the canonical pipeline</h2>
%s

<h2>How to read a row</h2>
<ul>
<li><strong>Official source</strong> - the league, tour or governing body page the row was read from,
with the read timestamp on the <a href="sources.html">Sources</a> page. Every row has one.</li>
<li><strong>Blank cells</strong> - a value this desk could not confirm officially is left blank and
flagged. It is never inferred from memory, from another desk or from a search snippet.</li>
<li><strong>Prices</strong> - originated fair prices: decimal = 1 / probability with no margin, American
derived from the unrounded decimal. &ldquo;In window&rdquo; means the fair American price expresses inside
&minus;250&hellip;+10000.</li>
<li><strong>Tiers</strong> - attached to the winner market of each fixture, per the brief&rsquo;s
&ldquo;pick a match winner and label each with a confidence level&rdquo;. Derivative markets (3-way
regulation, handicap, match total) are priced in the
<a href="markets.html">market explorer</a> and explained in
<a class="flag" href="flagged.html#F-D7D-15">F-D7D-15</a>.</li>
<li><strong>Evidence expiry</strong> - fixtures expire 6 hours after the read, statistics 24 hours. This
desk never re-stamps an old read as fresh; the whole desk expires with the timestamps shown above.</li>
</ul>
""" % (grid, e(D.DESK_READ_UTC), e(", ".join(EXCLUDED)), e(D.WINDOW_FROM_UTC[:10]),
       e(D.WINDOW_UNTIL_UTC[:10]), rows, hrows, len(gateA), garows or
       "<tr><td colspan=\"7\" class=\"blank\">none</td></tr>", self.crosscheck_card())
        return self.page("Overview", "index.html", body,
                         subtitle="55 officially-read fixture listings across six sports, 26 of them "
                                  "priced with our own multi-market lines, 7 High-confidence winner picks "
                                  "inside the brief's -250&hellip;+10000 window, 12 coverage gaps and a "
                                  "read-only audit of this repository.")

    # ------------------------------------------------------------- cross-check
    def canonical_id(self, f):
        key = f["key"]
        if key.startswith("el-"):
            return "euroleague-round7-%s" % key.split("-")[-1]
        return key

    def crosscheck_card(self):
        if not self.snap:
            return ('<div class="note">The canonical snapshot <code>data/current/snapshot.json</code> was '
                    'not readable at build time, so no cross-check table is published.</div>')
        prices = {p["fixture_id"]: p for p in self.snap.get("prices", []) if p.get("probability")}
        rows = []
        for f in self.fixtures:
            if not f["winner_pick"]:
                continue
            cp = prices.get(self.canonical_id(f))
            if not cp:
                continue
            mine, theirs = f["winner_pick"], cp
            same_side = mine["selection"].split("(")[0].strip().lower().startswith(
                str(cp["selection"]).split("(")[0].strip().lower()[:12])
            rows.append(
                "<tr><td>%s</td><td>%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td>"
                "<td class=\"num\">%s</td><td class=\"num\">%s</td><td>%s</td><td>%s</td></tr>"
                % (e(f["key"]), matchup(f), pct(mine["probability"]), money(mine["fair_american"]),
                   pct(cp["probability"]), money(cp.get("american_display")),
                   "same side" if same_side else "<span class='flag'>different side</span>",
                   badge(str(cp.get("confidence", "")).capitalize())))
        if not rows:
            return ('<div class="note">No fixture on this desk could be matched to a priced row in the '
                    'canonical snapshot, so no cross-check is published.</div>')
        return """<div class="card">
<p>The repository's own canonical pipeline (<code>data/current/snapshot.json</code>, model
<code>%s</code>, generated %s) priced some of the same fixtures from its own official reads. This desk
treats that file as <strong>discovery only</strong> - no value from it is imported into any row here - but
comparing the two independent originations is a useful check on our arithmetic, and it exposes a policy
difference rather than a data difference.</p>
<div class="wrap"><table>
<caption>Our originated winner price against the canonical pipeline's price for the same fixture id.
%d overlapping fixtures.</caption>
<thead><tr><th>Fixture</th><th>Match</th><th class="num">Our p</th><th class="num">Our American</th>
<th class="num">Canonical p</th><th class="num">Canonical American</th><th>Side</th>
<th>Canonical confidence</th></tr></thead>
<tbody>%s</tbody></table></div>
<p class="muted">Where the two agree to the fourth decimal place (for example Besiktas at 0.6000 /
&minus;150 and Dubai at 0.6923 / &minus;225) both desks are running the same log5 construction on the
same official Round 7 records, which is what convergence should look like. The confidence labels differ
because the canonical model refuses to issue Medium or High without measured calibration, while this
desk follows the brief's window-and-evidence rule; both positions are stated on their own pages and
neither is a correction of the other.</p>
</div>""" % (e(self.snap.get("model_version", "")), e(self.snap.get("generated_at", "")), len(rows), rows)

    # ---------------------------------------------------------------- matches
    def matches(self):
        blocks = []
        for slug, name in SPORTS:
            rows_f = [f for f in self.fixtures if f["sport"] == slug]
            gap = next((g for g in self.desk["gaps"] if g["sport"] == slug), None)
            if not rows_f:
                blocks.append('<h2 id="%s">%s</h2><div class="warn">No rows published. %s Attempted: %s '
                              '(%d attempt(s)). <a href="flagged.html">Flagged for review</a> · '
                              '<a href="sports/%s.html">sport page</a>.</div>'
                              % (e(slug), e(name), e(gap["reason"] if gap else "Not attempted this session."),
                                 link(gap["attempted"]) if gap and gap.get("attempted") else "—",
                                 gap["attempts"] if gap else 0, e(slug)))
                continue
            trs = []
            for f in rows_f:
                wp = f["winner_pick"]
                trs.append(
                    "<tr id=\"%s\"><td><code>%s</code></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>"
                    "<td>%s</td><td>%s</td>"
                    "<td class=\"num\">%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td>"
                    "<td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                    % (e(f["key"]), e(f["key"]), e(f["date"]), when(f), matchup(f),
                       cell(f.get("venue"), "not published"), cell(f.get("status"), "not published"),
                       e(wp["selection"]) if wp else '<span class="blank">not priced</span>',
                       pct(wp["probability"]) if wp else '<span class="blank">&mdash;</span>',
                       dec(wp["fair_decimal"]) if wp else '<span class="blank">&mdash;</span>',
                       money(wp["fair_american"]) if wp else '<span class="blank">&mdash;</span>',
                       ("yes" if wp["in_brief_window"] else "no") if wp else '<span class="blank">&mdash;</span>',
                       badge(wp["tier"]) if wp else '<span class="badge t-none">unpriced</span>',
                       flags_cell(f["flags"]), link(f["official_link"], "official")))
            blocks.append("""<h2 id="%s">%s <span class="muted">(%d listing%s, %d priced)</span></h2>
<div class="wrap"><table>
<caption>Competition: %s. Blank cells are values no official page published; each is flagged, never
inferred. Unpriced rows carry the reason on the <a href="sports/%s.html">sport page</a>.</caption>
<thead><tr><th>Fixture id</th><th>Date</th><th>Start</th><th>Match</th><th>Venue</th><th>Status</th><th>Our pick</th>
<th class="num">p</th><th class="num">Decimal</th><th class="num">American</th><th>In window</th>
<th>Tier</th><th>Flags</th><th>Official source</th></tr></thead>
<tbody>%s</tbody></table></div>""" % (e(slug), e(name), len(rows_f), "" if len(rows_f) == 1 else "s",
                                       sum(1 for f in rows_f if f["priced"]),
                                       e(rows_f[0]["competition"]), e(slug), "".join(trs)))
        body = ('<div class="note">Every row below was read live from the official source linked in its '
                'last column on %s. Prices are this desk&rsquo;s own originated fair prices.</div>'
                % e(D.DESK_READ_UTC)) + "".join(blocks)
        return self.page("Match list", "matches.html", body,
                         subtitle="All 55 officially-read fixture listings in the window 22-29 October "
                                  "2026, with our originated winner line and confidence tier where an "
                                  "official statistical input existed.")

    # ---------------------------------------------------------------- markets
    def markets(self):
        blocks = []
        for f in self.fixtures:
            if not f["markets"]:
                continue
            trs = []
            for mk in f["markets"]:
                first = True
                for o in mk["outcomes"]:
                    trs.append(
                        "<tr>%s<td>%s</td><td>%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td>"
                        "<td class=\"num\">%s</td><td>%s</td></tr>"
                        % (("<td rowspan=\"%d\"><strong>%s</strong><br><span class=\"muted\">%s · %s</span>"
                            "</td>" % (len(mk["outcomes"]), e(mk["market"]), e(mk["family"]), e(mk["model"])))
                           if first else "",
                           e(o["selection"]),
                           '<span class="muted">stronger side</span>' if o["selection"] == mk["stronger_side"]
                           else '<span class="blank">&mdash;</span>',
                           pct(o["probability"]), dec(o["fair_decimal"]), money(o["fair_american"]),
                           "yes" if o["in_brief_window"] else "<span class='flag'>no</span>"))
                    first = False
            withheld = "".join("<li><strong>%s</strong> - %s</li>" % (e(w["market"]), e(w["reason"]))
                               for w in f.get("withheld_markets") or [])
            md = f.get("model_detail") or {}
            detail = " · ".join("%s %s" % (e(k.replace("_", " ")), e(v)) for k, v in sorted(md.items()))
            blocks.append("""<h3>%s · %s</h3>
<p class="muted">%s · %s · inputs: %s · official source %s%s</p>
<div class="wrap"><table><thead><tr><th>Market</th><th>Outcome</th><th></th><th class="num">p</th>
<th class="num">Fair decimal</th><th class="num">Fair American</th><th>In window</th></tr></thead>
<tbody>%s</tbody></table></div>%s""" % (when(f), matchup(f), e(f["competition"]), detail,
                                          e(f["markets"][0]["inputs"]), link(f["official_link"], "official"),
                                          (" · " + flags_cell(f["flags"])) if f["flags"] else "",
                                          "".join(trs),
                                          ("<p class=\"muted\">Markets investigated but withheld: "
                                           "<ul>%s</ul></p>" % withheld) if withheld else ""))
        unpriced = [f for f in self.fixtures if not f["markets"]]
        up = "".join("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                     % (when(f), matchup(f), e(f["sport_name"]), e(f["unpriced_reason"]),
                        link(f["official_link"], "official")) for f in unpriced)
        body = """<div class="note">Every market below is originated by this desk from official inputs.
No operator price was read, so no margin, no overround and no edge is claimed: the fair decimal is
1&nbsp;/&nbsp;probability and the American price is derived from the unrounded decimal.</div>
%s
<h2>Fixtures investigated but not priced (%d)</h2>
<p>A market is only published where an official input exists for <em>both</em> sides. These rows are
listed with the specific missing input rather than estimated.</p>
<div class="wrap"><table><thead><tr><th>Start</th><th>Match</th><th>Sport</th>
<th>Why no line is originated</th><th>Official source</th></tr></thead><tbody>%s</tbody></table></div>
""" % ("".join(blocks), len(unpriced), up)
        return self.page("Market explorer", "markets.html", body,
                         subtitle="%d originated markets and %d priced outcomes across %d fixtures: "
                                  "match winner, 3-way regulation, handicap and match totals where an "
                                  "official input existed for both sides."
                                  % (self.counts["markets"], self.counts["outcomes"], self.counts["priced"]))

    # ----------------------------------------------------------- high confidence
    def high(self):
        highs = [f for f in self.fixtures if f["winner_pick"] and f["winner_pick"]["tier"] == "High"]
        rows = []
        for f in highs:
            wp, p = f["winner_pick"], self.preds_by_market.get("%s#m1" % f["key"])
            rows.append(
                "<tr><td>%s</td><td>%s</td><td>%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td>"
                "<td class=\"num\">%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                % (when(f), matchup(f), e(wp["selection"]), pct(wp["probability"]), dec(wp["fair_decimal"]),
                   money(wp["fair_american"]), e(wp["model"]),
                   " · ".join([link(f["official_link"], "fixture")] +
                              [link(self.src[sid]["url"], "inputs: " + sid)
                               for sid in f["sources"] if sid in self.src]),
                   ('<a href="predictions.html#%s">%s</a>' % (e(p["id"]), e(p["id"]))) if p else "—"))
        blocked = [(f, f["winner_pick"]) for f in self.fixtures
                   if f["winner_pick"] and f["winner_pick"]["tier"] == "Medium"
                   and f["key"] in ("el-E2026-62", "el-E2026-63")]
        brows = "".join(
            "<tr><td>%s</td><td>%s</td><td>%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td>"
            "<td>%s</td><td>%s</td></tr>"
            % (when(f), matchup(f), e(wp["selection"]), pct(wp["probability"]), money(wp["fair_american"]),
               badge("Medium"), e(wp["tier_reason"])) for f, wp in blocked)
        oow = []
        for f in self.fixtures:
            for mk in f["markets"]:
                for o in mk["outcomes"]:
                    if o["probability"] > 250.0 / 350.0 + 1e-9 and not o["in_brief_window"]:
                        oow.append((f, mk, o))
        orows = "".join(
            "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td class=\"num\">%s</td>"
            "<td class=\"num\">%s</td><td>%s</td></tr>"
            % (when(f), matchup(f), e(mk["market"]), e(o["selection"]), pct(o["probability"]),
               money(o["fair_american"]), link(f["official_link"], "official"))
            for f, mk, o in sorted(oow, key=lambda x: -x[2]["probability"]))
        der = []
        for f in self.fixtures:
            for mk in f["markets"]:
                if mk["family"] == "winner":
                    continue
                o = max(mk["outcomes"], key=lambda x: x["probability"])
                if o["probability"] >= 0.60:
                    der.append((f, mk, o))
        drows = "".join(
            "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td class=\"num\">%s</td>"
            "<td class=\"num\">%s</td><td>%s</td><td>%s</td></tr>"
            % (when(f), matchup(f), e(mk["market"]), e(o["selection"]), pct(o["probability"]),
               money(o["fair_american"]), "yes" if o["in_brief_window"] else "no",
               link(f["official_link"], "official"))
            for f, mk, o in sorted(der, key=lambda x: (-x[2]["probability"], x[0]["key"])))
        gateA = [(f, mk, o) for f in self.fixtures for mk in f["markets"] for o in mk["outcomes"]
                 if o["probability"] > 0.70 and o["in_brief_window"]]
        grows = "".join(
            "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td class=\"num\">%s</td>"
            "<td class=\"num\">%s</td><td>%s</td></tr>"
            % (when(f), matchup(f), e(mk["market"]), e(o["selection"]), pct(o["probability"]),
               money(o["fair_american"]),
               ('<a href="predictions.html#%s">%s</a>' % (e(self.preds_by_market[mk["market_id"]]["id"]),
                                                          e(self.preds_by_market[mk["market_id"]]["id"])))
               if mk["market_id"] in self.preds_by_market else link(f["official_link"], "official"))
            for f, mk, o in gateA)
        body = """
<h2>Gate B - the seven High-confidence winner picks</h2>
<p>Requirements, all four of which must hold: the originated price expresses inside
&minus;250&hellip;+10000; the model probability is at or above 0.60; the fixture <em>and</em> both
sides&rsquo; statistical inputs were read from official pages this session; and a unique hand-written
prediction of at least 30 words exists. Any official sentence read this session that contradicts the lean
caps the pick at Medium - that happened twice, and both downgrades are shown below with the citation.</p>
<div class="wrap"><table>
<thead><tr><th>Start (UTC)</th><th>Match</th><th>Selection</th><th class="num">p</th>
<th class="num">Decimal</th><th class="num">American</th><th>Model</th><th>Official sources</th>
<th>Prediction</th></tr></thead><tbody>%s</tbody></table></div>

<h2>Gate A - the brief&rsquo;s literal rule (&gt;70&nbsp;%% <em>and</em> inside the window)</h2>
<p>Exactly one selection on the whole desk satisfies both literal conditions, and it is a derivative
line rather than a match winner: %d row(s). This is the arithmetic problem behind
<a class="flag" href="flagged.html#F-D7D-10">F-D7D-10</a> - above 70&nbsp;%% means shorter than
&minus;233, and the window starts at &minus;250, so the intersection is a 1.4-point slice of
probability.</p>
<div class="wrap"><table><thead><tr><th>Start (UTC)</th><th>Match</th><th>Market</th><th>Selection</th>
<th class="num">p</th><th class="num">American</th><th>Prediction / source</th></tr></thead>
<tbody>%s</tbody></table></div>

<h2>Downgraded by official context (would otherwise be High)</h2>
<div class="wrap"><table><thead><tr><th>Start (UTC)</th><th>Match</th><th>Model lean</th>
<th class="num">p</th><th class="num">American</th><th>Tier</th><th>Official sentence that capped it</th>
</tr></thead><tbody>%s</tbody></table></div>

<h2>Out-of-window strong favourites (%d)</h2>
<p>These selections are stronger than 71.4&nbsp;%%, so their fair price is shorter than &minus;250 and the
brief&rsquo;s own window excludes them from High. They are published here rather than dropped: an honest
desk shows what its model liked and why the rule rejected it.</p>
<div class="wrap"><table><thead><tr><th>Start (UTC)</th><th>Match</th><th>Market</th><th>Selection</th>
<th class="num">p</th><th class="num">Fair American</th><th>Official source</th></tr></thead>
<tbody>%s</tbody></table></div>

<h2>Derivative markets at or above 0.60 (%d)</h2>
<p>Per the brief, the confidence label attaches to the match-winner pick. Handicap, 3-way regulation and
match-total lines are therefore priced and published without a tier, and only the single Gate A row above
receives prose. This is disclosed as
<a class="flag" href="flagged.html#F-D7D-15">F-D7D-15</a> rather than padded with repetitive
predictions.</p>
<div class="wrap"><table><thead><tr><th>Start (UTC)</th><th>Match</th><th>Market</th>
<th>Stronger side</th><th class="num">p</th><th class="num">Fair American</th><th>In window</th>
<th>Official source</th></tr></thead><tbody>%s</tbody></table></div>
""" % ("".join(rows), len(gateA), grows or '<tr><td colspan="7" class="blank">none</td></tr>',
       "".join(brows), len(oow), orows, len(der), drows)
        return self.page("High-confidence picks", "high-confidence.html", body,
                         subtitle="Seven High winner picks at originated prices of -150 to -225, one "
                                  "literal Gate A derivative, two picks downgraded by official context, "
                                  "and 13 out-of-window favourites disclosed rather than hidden.")

    # ------------------------------------------------------------- predictions
    def _predictions_page(self):
        cards = []
        by_key = {f["key"]: f for f in self.fixtures}
        for p in self.preds:
            f = by_key[p["fixture_key"]]
            facts = "".join('<li>%s &mdash; %s <span class="muted">(read %s)</span></li>'
                            % (e(x["claim"]), link(self.src[x["source_id"]]["url"],
                                                   self.src[x["source_id"]]["publisher"]),
                               e(self.src[x["source_id"]]["read_at_utc"]))
                            for x in p["facts"])
            claims = "".join("<li>%s</li>" % e(c) for c in p["verified_claims"])
            cards.append("""<article class="pred" id="%s">
<p class="who">%s · %s · %s</p>
<h3>%s &mdash; %s</h3>
<p class="muted">Selection <strong>%s</strong> · our probability %s · fair decimal %s · fair American
%s · tier %s · %d words · official fixture %s</p>
<p class="text">%s</p>
<details><summary>Facts used, each with the official page it was read from (%d)</summary>
<ul>%s</ul></details>
<details><summary>Numeric claims re-checked against the official transcription at build time (%d)</summary>
<ul>%s</ul></details>
</article>""" % (e(p["id"]), e(p["fixture_key"]), when(f), e(f["competition"]), matchup(f),
                 e(p["market_id"]), e(p["selection"]), pct(p["probability"]),
                 dec(next((o["fair_decimal"] for mk in f["markets"] if mk["market_id"] == p["market_id"]
                           for o in mk["outcomes"] if o["selection"] == p["selection"]), None)),
                 money(p["fair_american"]), badge(p["tier"]), p["word_count"],
                 link(f["official_link"], "official page"), e(p["text"]), len(p["facts"]), facts,
                 len(p["verified_claims"]), claims))
        body = """<div class="note">Eight predictions: one for each of the seven High-confidence winner
picks and one for the single selection that satisfies the brief's literal rule (probability above
70&nbsp;%% <em>and</em> price inside &minus;250&hellip;+10000). Every text is hand-written for this desk,
at least 30 words long, and uses only facts read from an official page during this session. A build-time
guard rejects any two predictions that share a five-word phrase, and re-checks %d numeric claims against
the official transcription; no player, injury, weather or travel claim appears unless the fact list names
its official source. Ice hockey prose cites club-level official facts only, because no official NHL injury
report was read - see <a class="flag" href="flagged.html#F-D7D-14">F-D7D-14</a>.</div>
%s""" % (sum(len(p["verified_claims"]) for p in self.preds), "".join(cards))
        return self.page("Predictions", "predictions.html", body,
                         subtitle="Hand-written, non-repetitive predictions of 84-116 words each, naming "
                                  "the club or player, current form, recent official results and an "
                                  "unambiguous selection.")

    # ------------------------------------------------------------------ sports
    def sports_index(self):
        rows = []
        for slug, name in SPORTS:
            s = self.desk["per_sport"].get(slug)
            gap = next((g for g in self.desk["gaps"] if g["sport"] == slug), None)
            rows.append("<tr><td><a href=\"sports/%s.html\">%s</a></td><td class=\"num\">%s</td>"
                        "<td class=\"num\">%s</td><td class=\"num\">%s</td><td>%s</td><td>%s</td>"
                        "<td>%s</td></tr>"
                        % (e(slug), e(name), e(s["fixtures"]) if s else "0", e(s["priced"]) if s else "0",
                           e(s["markets"]) if s else "0",
                           "covered" if s else '<span class="flag">gap</span>',
                           e(gap["attempted"]) if gap and gap.get("attempted") else
                           '<span class="blank">not attempted this session</span>',
                           link(s["olbg_hub"], "hub") if s and s.get("olbg_hub") else
                           (link(gap["olbg_hub"], "hub") if gap else '<span class="blank">—</span>')))
        body = """<p>All seventeen in-scope sports. Excluded by the brief: %s.</p>
<div class="wrap"><table><thead><tr><th>Sport</th><th class="num">Listings</th><th class="num">Priced</th>
<th class="num">Markets</th><th>Status</th><th>Official page attempted</th>
<th>OLBG hub (discovery only)</th></tr></thead><tbody>%s</tbody></table></div>
<h2>Excluded sports</h2><p>The brief excludes %s. No row for those sports appears anywhere on this desk,
and no attempt was made to price them.</p>""" % (e(", ".join(EXCLUDED)), "".join(rows),
                                                 e(", ".join(EXCLUDED)))
        return self.page("All sports", "sports.html", body,
                         subtitle="Six sports carry rows; eleven are published as gaps with the official "
                                  "URL attempted and the specific reason nothing could be read.")

    def sport_page(self, slug, name):
        rows_f = [f for f in self.fixtures if f["sport"] == slug]
        gap = next((g for g in self.desk["gaps"] if g["sport"] == slug), None)
        s = self.desk["per_sport"].get(slug)
        if not rows_f:
            body = """<div class="warn"><strong>No rows published for %s.</strong> This is a coverage gap,
not a finding that the sport has no fixtures in the window.</div>
<div class="wrap"><table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>
<tr><td>OLBG hub (discovery only)</td><td>%s</td></tr>
<tr><td>Official page attempted</td><td>%s</td></tr>
<tr><td>Attempts</td><td>%s</td></tr>
<tr><td>What happened</td><td>%s</td></tr>
<tr><td>Status</td><td>%s</td></tr>
</tbody></table></div>
<p class="muted">A gap row is published blank rather than filled from memory. If the official page becomes
machine-readable, the row can be added without changing any other sport's page.</p>""" % (
                e(name), link(gap["olbg_hub"]) if gap else '<span class="blank">—</span>',
                link(gap["attempted"]) if gap and gap.get("attempted") else
                '<span class="blank">not attempted this session</span>',
                e(gap["attempts"]) if gap else "0", e(gap["reason"]) if gap else
                "Not attempted during this session's read budget.",
                e(gap["status"]) if gap else "not attempted")
            return self.page(name, "sports.html", body, prefix="../",
                             subtitle="Gap page: no official rows could be read for this sport during "
                                      "this session.")
        trs = []
        for f in rows_f:
            wp = f["winner_pick"]
            trs.append("<tr id=\"%s\"><td><code>%s</code></td><td>%s</td><td>%s</td><td>%s</td>"
                       "<td>%s</td><td class=\"num\">%s</td>"
                       "<td class=\"num\">%s</td><td class=\"num\">%s</td><td>%s</td><td>%s</td>"
                       "<td>%s</td></tr>"
                       % (e(f["key"]), e(f["key"]), when(f), matchup(f),
                          cell(f.get("venue"), "not published"),
                          e(wp["selection"]) if wp else '<span class="blank">not priced</span>',
                          pct(wp["probability"]) if wp else '<span class="blank">&mdash;</span>',
                          money(wp["fair_american"]) if wp else '<span class="blank">&mdash;</span>',
                          dec(wp["fair_decimal"]) if wp else '<span class="blank">&mdash;</span>',
                          badge(wp["tier"]) if wp else '<span class="badge t-none">unpriced</span>',
                          e(wp["tier_reason"]) if wp else e(f["unpriced_reason"]),
                          flags_cell(f["flags"], prefix="../") + " " + link(f["official_link"], "official")))
        mk_rows = []
        for f in rows_f:
            if f["markets"]:
                for mk in f["markets"]:
                    mk_rows.append(
                        "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td class=\"num\">%s</td>"
                        "<td class=\"num\">%s</td><td>%s</td></tr>"
                        % (matchup(f), e(mk["market"]), e(mk["family"]), e(mk["model"]),
                           pct(mk["stronger_probability"]), money(mk["stronger_american"]),
                           link(f["official_link"], "official")))
            else:
                dash = '<span class="blank">&mdash;</span>'
                mk_rows.append(
                    "<tr><td>%s</td><td><span class=\"blank\">no market originated</span> &mdash; %s</td>"
                    "<td>%s</td><td>%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td>"
                    "<td>%s</td></tr>"
                    % (matchup(f), e(f["unpriced_reason"]), dash, dash, dash, dash,
                       link(f["official_link"], "official")))
        mk_rows = "".join(mk_rows)
        ctx = "".join("<li><strong>%s</strong> %s<ul>%s</ul></li>"
                      % (matchup(f), link(f["official_link"], "official page"),
                         "".join("<li>%s</li>" % e(c) for c in f["context"]))
                      for f in rows_f if f["context"])
        body = """<div class="wrap"><table>
<caption>%d listing%s read from official pages on %s; %d priced.</caption>
<thead><tr><th>Fixture id</th><th>Start</th><th>Match</th><th>Venue</th><th>Our pick</th><th class="num">p</th>
<th class="num">American</th><th class="num">Decimal</th><th>Tier</th><th>Reason / flags</th>
<th>Official source</th></tr></thead><tbody>%s</tbody></table></div>
<h2>Markets originated</h2>
<div class="wrap"><table><thead><tr><th>Match</th><th>Market</th><th>Family</th><th>Model</th>
<th class="num">Stronger side p</th><th class="num">Fair American</th><th>Official source</th></tr></thead>
<tbody>%s</tbody></table></div>
%s""" % (len(rows_f), "" if len(rows_f) == 1 else "s", e(D.DESK_READ_UTC),
         sum(1 for f in rows_f if f["priced"]), "".join(trs),
         mk_rows or '<tr><td colspan="7" class="blank">no market could be originated</td></tr>',
         ("<h2>Official context read for these fixtures</h2><ul>%s</ul>" % ctx) if ctx else "")
        sub = ("%d listings, %d priced, %d markets originated." % (len(rows_f), sum(1 for f in rows_f if f["priced"]),
                                                                   s["markets"])) if s else ""
        return self.page(name, "sports.html", body, prefix="../", subtitle=sub)

    # ---------------------------------------------------------------- analysis
    def analysis(self):
        lam = []
        for f in self.fixtures:
            md = f.get("model_detail") or {}
            if "lambda_away" in md:
                lam.append((f, md))
        lrows = "".join("<tr><td>%s</td><td>%s</td><td>%s</td><td class=\"num\">%.4f</td>"
                        "<td class=\"num\">%.4f</td><td class=\"num\">%.4f</td><td class=\"num\">%s</td>"
                        "<td class=\"num\">%s</td><td>%s</td></tr>"
                        % (e(f["key"]), matchup(f), e(f["winner_pick"]["model"]), md["lambda_away"],
                           md["lambda_home"], md["expected_total"], pct(f["winner_pick"]["probability"]),
                           money(f["winner_pick"]["fair_american"]), link(f["official_link"], "official"))
                        for f, md in lam)
        # log5 cross-check on NHL points percentage
        xrows = []
        for f in self.fixtures:
            if f["sport"] != "ice-hockey" or not f["priced"]:
                continue
            st = f["standings"]
            a, h = st["away"], st["home"]
            pa = (a["points"] + 2.0) / (2.0 * a["gp"] + 4.0)   # Beta(2,2) shrinkage of points %
            ph = (h["points"] + 2.0) / (2.0 * h["gp"] + 4.0)
            denom = pa + ph - 2 * pa * ph
            p5 = (pa - pa * ph) / denom
            pw = f["winner_pick"]["probability"]
            xrows.append("<tr><td>%s</td><td>%s</td><td>%s</td><td class=\"num\">%s</td>"
                         "<td class=\"num\">%.4f</td><td class=\"num\">%+.4f</td><td>%s</td></tr>"
                         % (e(f["key"]), matchup(f), e(f["winner_pick"]["selection"]), pct(pw), p5,
                            pw - p5, "same side" if (p5 >= 0.5) == (pw >= 0.5) else
                            "<span class='flag'>different side</span>"))
        band = []
        for p in (0.55, 0.58, 0.60, 0.62, 0.65, 0.68, 0.6923, 0.70, 0.7143, 0.72, 0.75, 0.845):
            amer = -round(p / (1 - p) * 100) if p >= 0.5 else round((1 - p) / p * 100)
            band.append("<tr><td class=\"num\">%.4f</td><td class=\"num\">%.4f</td><td class=\"num\">%s</td>"
                        "<td>%s</td><td>%s</td><td>%s</td></tr>"
                        % (p, 1 / p, money(amer), "yes" if -250 <= amer <= 10000 else "no",
                           "yes" if p > 0.70 else "no",
                           "yes" if (p > 0.70 and -250 <= amer <= 10000) else "no"))
        unpriced = {}
        for f in self.fixtures:
            if not f["priced"]:
                unpriced.setdefault(f["sport_name"], []).append(f)
        uprows = "".join("<tr><td>%s</td><td class=\"num\">%d</td><td>%s</td></tr>"
                         % (e(k), len(v), e(v[0]["unpriced_reason"])) for k, v in sorted(unpriced.items()))
        body = """
<h2>1. What was read, and what that makes possible</h2>
<p>Sixteen official reads were made on %s (see <a href="sources.html">Sources</a>). Three of them carried
the statistics a line needs for <em>both</em> sides of a fixture: the NHL standings for 2026-10-21 (all
32 clubs, goals for and against, games played, points and streak codes), the MLB standings for the Rays
and the Brewers (2026 regular-season runs scored and allowed), and the EuroLeague Round 7 Game Center
(all 18 clubs' records plus points-for/against ranks, injuries and head-to-head notes). That is why 26 of
55 listings are priced and 29 are not: the other sports' official pages publish fixtures without any
statistical input, and inventing one is exactly what the brief forbids.</p>

<h2>2. The models</h2>
<div class="card">
<h3>nhl-poisson-v1</h3>
<p>Independent Poisson goal counts, 0&hellip;12 per club:</p>
<pre>rate_for(A)    = goalFor(A) / gamesPlayed(A)          [official NHL standings, 2026-10-21]
rate_against(A)= goalAgainst(A) / gamesPlayed(A)
lambda_A       = (rate_for(A) + rate_against(B)) / 2
lambda_B       = (rate_for(B) + rate_against(A)) / 2
P(A wins incl. OT) = P(A &gt; B) + P(A = B) * lambda_A / (lambda_A + lambda_B)</pre>
<p>No home-ice advantage is inserted: none was measured this session. The overtime split is proportional
to lambda, which is a disclosed model assumption, not an official statistic. Markets derived from the same
matrix: 3-way regulation, A &minus;1.5 / B +1.5, and totals at 5.5 and 6.5 goals.</p>
<h3>mlb-poisson-v1</h3>
<p>The identical construction on runs: <code>rate = runs / 162</code> from the official 2026
regular-season totals (Rays 736 scored / 650 allowed; Brewers 832 / 618). Markets: winner including extra
innings, &minus;1.5 / +1.5 run line, totals at 7.5, 8.5 and 9.5 runs. No pitcher, park, lineup, rest or
postseason adjustment exists in the inputs, so none is claimed - which is why all five World Series games
originate the same line
(<a class="flag" href="flagged.html#F-D7D-13">F-D7D-13</a>).</p>
<h3>el-log5-v1</h3>
<p>Beta(2,2)-shrunk win rates from the official Round 7 records, combined with log5:</p>
<pre>p_shrunk(X) = (wins(X) + 2) / (wins(X) + losses(X) + 4)
P(A beats B) = (pA - pA*pB) / (pA + pB - 2*pA*pB)</pre>
<p>Winner market only. Handicap and total lines are withheld because the official preview publishes no
margin distribution for either club; the points-per-game ranks it does publish are quoted as context on
the predictions page instead of being turned into a line.</p>
</div>

<h2>3. Originated rates per fixture</h2>
<div class="wrap"><table><thead><tr><th>Fixture</th><th>Match</th><th>Model</th>
<th class="num">&lambda; away</th><th class="num">&lambda; home</th><th class="num">expected total</th>
<th class="num">winner p</th><th class="num">fair American</th><th>Official source</th></tr></thead>
<tbody>%s</tbody></table></div>

<h2>4. Independent cross-check on the hockey rows</h2>
<p>A second, different construction - log5 on Beta(2,2)-shrunk <em>points percentage</em>
(<code>(points + 2) / (2 * games played + 4)</code>) rather than goals - is run over the same official standings. It is not used to set any price; it exists to show
whether the published Poisson leans survive a different reading of the same numbers.</p>
<div class="wrap"><table><thead><tr><th>Fixture</th><th>Match</th><th>Poisson pick</th>
<th class="num">Poisson p</th><th class="num">log5 points-%% p</th><th class="num">difference</th>
<th>Agreement</th></tr></thead><tbody>%s</tbody></table></div>

<h2>5. Why the brief's two High rules barely overlap</h2>
<p>&ldquo;A lot of the high confidence picks are just picks that have a greater than 70&nbsp;%% chance to
win based on market prices. We need to focus on generating high confidence picks for matches that sit
between &minus;250 and +10000 odds.&rdquo; Those two conditions fight each other: 70&nbsp;%% is
&minus;233, and prices get <em>shorter</em> as probability rises, so the only prices satisfying both are
&minus;250 to &minus;233.</p>
<div class="wrap"><table><caption>Fair-price arithmetic (decimal = 1 / p, no margin).</caption>
<thead><tr><th class="num">p</th><th class="num">fair decimal</th><th class="num">fair American</th>
<th>inside &minus;250&hellip;+10000</th><th>above 70&nbsp;%%</th><th>satisfies both (Gate A)</th>
</tr></thead><tbody>%s</tbody></table></div>
<p>Research done to resolve it, rather than paper over it: (a) both gates are published side by side, so a
reviewer can see the literal intersection is one derivative line (Pittsburgh +1.5 goals at &minus;236,
70.21&nbsp;%%); (b) the High tier is earned on the window condition plus an evidence test at
0.60&ndash;0.714, which keeps every published High inside the brief's price band; (c) the thirteen
selections stronger than 71.4&nbsp;%% are listed as out-of-window on the
<a href="high-confidence.html">High-confidence page</a> instead of being quietly relabelled; (d) the two
picks that official context contradicts are downgraded with the citation.</p>

<h2>6. Why 29 listings carry no line</h2>
<div class="wrap"><table><thead><tr><th>Sport</th><th class="num">Listings</th>
<th>Missing official input</th></tr></thead><tbody>%s</tbody></table></div>
<p>Tennis orders of play publish names, seeds and start order; the PCB tournament page publishes dates,
teams and grounds; IRL publishes teams, clocks and venues. None of them publishes a form, ranking or
points input for both sides, and no ranking or results page was read this session for those players or
teams. A price invented from memory would be a hallucination, so those rows stay blank and flagged.</p>

<h2>7. Known weaknesses of this desk</h2>
<ul>
<li>Uncalibrated models: no out-of-sample hit rate exists for any of the three constructions, so a
&ldquo;High&rdquo; label is a statement about inputs and price band, not a measured success rate.</li>
<li>Independent-Poisson artefacts: totals and handicaps inherit an expected total of 5.43&ndash;6.72 goals
in hockey and 8.75 runs in baseball, which is higher than typical scoring environments; no correlation
between the two sides is modelled.</li>
<li>Small samples: early-season NHL rates come from 7&ndash;12 games per club, and EuroLeague log5 from six
rounds, which is why the Beta(2,2) shrinkage is applied to the basketball rows.</li>
<li>Two NHL rows have no away club (the official schedule chunk did not reach it) and all nine basketball
rows have no venue (the official preview does not publish one).</li>
<li>No operator price was available, so no comparison of our lines to the market, and therefore no edge
claim, is possible anywhere on this desk.</li>
</ul>
""" % (e(D.DESK_READ_UTC), lrows, "".join(xrows), "".join(band), uprows)
        return self.page("Analysis", "analysis.html", body,
                         subtitle="Models and formulas, originated rates per fixture, an independent log5 "
                                  "cross-check, the arithmetic behind the brief's High-confidence window, "
                                  "and the desk's own weaknesses.")

    # ----------------------------------------------------------------- sources
    def _sources_page(self):
        rows = "".join(
            "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
            % (e(s["id"]), e(s["publisher"]), link(s["url"], "open official page"), e(s["kind"]),
               e(s["read_at_utc"]), e(s["role"]), e(s.get("read", "")))
            for s in self.desk["sources"])
        lims = "".join("<tr><td>%s</td><td>%s</td></tr>" % (link(s["url"], s["id"]), e(s["limitation"]))
                       for s in self.desk["sources"] if s.get("limitation"))
        hubs = "".join("<tr><td>%s</td><td>%s</td><td>%s</td></tr>"
                       % (e(n), link(D.SPORT_OLBG.get(s), "hub"), e(s))
                       for s, n in SPORTS)
        body = """<p>Every official page this desk read, in the order it was read, with the read timestamp
and exactly what was and was not obtained. Reads were made on %s. Nothing on this desk cites a source that
is not in this table, and no value in any row comes from memory, a search snippet or another session's
data.</p>
<div class="wrap"><table>
<thead><tr><th>Source id</th><th>Publisher</th><th>Official URL</th><th>Kind</th><th>Read at (UTC)</th>
<th>Role on this desk</th><th>What was read</th></tr></thead><tbody>%s</tbody></table></div>
<h2>Limitations recorded at read time</h2>
<div class="wrap"><table><thead><tr><th>Source</th><th>Limitation (what could not be read)</th></tr></thead>
<tbody>%s</tbody></table></div>
<h2>OLBG hubs - discovery only</h2>
<p>OLBG.com was used to enumerate the sports and their hub URLs so that coverage could be compared against
the brief. No tip, price, probability or fixture from OLBG appears in any row on this desk, and OLBG is
never cited as verification of anything.</p>
<div class="wrap"><table><thead><tr><th>Sport</th><th>OLBG hub</th><th>Desk slug</th></tr></thead>
<tbody>%s</tbody></table></div>
<h2>Canonical repository data - cross-check only</h2>
<p><code>data/current/snapshot.json</code> (model <code>%s</code>, generated %s) and its 34 network-attempt
logs under <code>data/current/evidence/</code> were read for two purposes: to find official URLs a previous
session had already located, and to compare our originated prices with the canonical pipeline's for the
same fixture ids. No value from either file is imported into a row here. The attempt logs record the URL
and transport outcome of a previous session's fetch - they are not verification of any fixture or price,
which is recorded as audit finding <a href="repo-audit.html#A-D7D-12">A-D7D-12</a>.</p>""" % (
            e(D.DESK_READ_UTC), rows, lims, hubs,
            e(self.snap.get("model_version", "") if self.snap else ""),
            e(self.snap.get("generated_at", "") if self.snap else ""))
        return self.page("Sources", "sources.html", body,
                         subtitle="16 official source reads with timestamps, roles and recorded "
                                  "limitations; OLBG listed separately as discovery only.")

    # ----------------------------------------------------------------- flagged
    def flagged(self):
        frows = "".join(
            '<tr id="%s"><td><strong>%s</strong></td><td>%s</td><td>%s</td></tr>'
            % (e(fid), e(fid), e(text),
               " · ".join(sorted({f["key"] for f in self.fixtures if fid in (f.get("flags") or [])})) or
               '<span class="muted">desk-wide</span>')
            for fid, text in sorted(self.desk["flags"].items()))
        grows = "".join(
            "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td class=\"num\">%s</td><td>%s</td>"
            "<td>%s</td></tr>"
            % (e(g["name"]), e(g["sport"]), link(g.get("olbg_hub"), "OLBG hub"),
               link(g.get("attempted"), "official page attempted"), e(g.get("attempts", 0)),
               e(g["reason"]), e(g["status"])) for g in self.desk["gaps"])
        blanks = [f for f in self.fixtures if f.get("blank_fields")]
        brows = "".join("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                        % (e(f["key"]), e(f["sport_name"]), matchup(f),
                           ", ".join(e(b) for b in f["blank_fields"]), flags_cell(f["flags"]),
                           link(f["official_link"], "official")) for f in blanks)
        unverified = [f for f in self.fixtures if not f["priced"]]
        urows = "".join("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                        % (e(f["key"]), e(f["sport_name"]), when(f), e(f["unpriced_reason"]),
                           link(f["official_link"], "official")) for f in unverified)
        body = """<div class="warn"><strong>Flagged for review.</strong> Everything on this page is
unverified, blank, contradictory or otherwise outside what this desk could confirm from an official source.
None of it blocks publication: the brief requires flagged items to be visible, not hidden, and requires
that unconfirmable values stay blank rather than be inferred.</div>
<h2>Flags (%d)</h2>
<div class="wrap"><table><thead><tr><th>Id</th><th>What is flagged</th><th>Rows affected</th></tr></thead>
<tbody>%s</tbody></table></div>
<h2>Coverage gaps (%d of 17 in-scope sports)</h2>
<div class="wrap"><table><thead><tr><th>Sport</th><th>Slug</th><th>OLBG hub</th>
<th>Official page attempted</th><th class="num">Attempts</th><th>Why nothing could be read</th>
<th>Status</th></tr></thead><tbody>%s</tbody></table></div>
<h2>Blank fields on published rows (%d)</h2>
<p>Each blank below is a field the official page did not publish, or that this desk's read of it did not
reach. No blank is filled from another source.</p>
<div class="wrap"><table><thead><tr><th>Fixture</th><th>Sport</th><th>Match</th><th>Blank field(s)</th>
<th>Flags</th><th>Official source</th></tr></thead><tbody>%s</tbody></table></div>
<h2>Fixtures published without a line (%d)</h2>
<p>These rows are verified as fixtures - date, teams and official link - but carry no originated price,
because no official statistical input existed for both sides. They are listed with the specific missing
input.</p>
<div class="wrap"><table><thead><tr><th>Fixture</th><th>Sport</th><th>Start</th>
<th>Missing official input</th><th>Official source</th></tr></thead><tbody>%s</tbody></table></div>
<h2>Repository irregularities</h2>
<p>The line-by-line audit of this repository produced %d findings, published with file and line references
on <a href="repo-audit.html">Repository audit</a>.</p>""" % (
            len(self.desk["flags"]), frows, len(self.desk["gaps"]), grows, len(blanks), brows,
            len(unverified), urows, len(self.audit["findings"]))
        return self.page("Flagged for review", "flagged.html", body,
                         subtitle="16 flags, 12 coverage gaps, every blank field on a published row and "
                                  "every fixture that could not be priced - all labelled, none blocking.")

    # -------------------------------------------------------------- repo audit
    def repo_audit(self):
        order = {"high": 0, "medium": 1, "low": 2, "info": 3}
        finds = sorted(self.audit["findings"], key=lambda f: (order.get(f["severity"], 9), f["id"]))
        blocks = []
        for f in finds:
            ev = []
            for x in f["evidence"]:
                fname, line, quote = x["file"], x["line"], x["quote"]
                if fname and fname not in ("-", "git", "git status") and os.path.exists(os.path.join(ROOT, fname)):
                    url = "%s/blob/%s/%s%s" % (REPO_URL, self.audit.get("head", self.head), fname,
                                               ("#L%d" % line) if line else "")
                    loc = '<a href="%s" rel="noopener noreferrer">%s:%s</a>' % (e(url), e(fname), e(line or 1))
                else:
                    loc = "%s%s" % (e(fname), (":%s" % e(line)) if line else "")
                ev.append("<tr><td>%s</td><td>%s</td></tr>" % (loc, e(quote)))
            blocks.append("""<article class="card" id="%s">
<h3>%s &mdash; %s</h3>
<p class="muted"><span class="sev-%s">%s</span> · area %s · status %s · found %s</p>
<p>%s</p>
<div class="wrap"><table><thead><tr><th>Where (links open the file on GitHub at the audited commit)</th>
<th>What was found</th></tr></thead><tbody>%s</tbody></table></div>
<p class="muted"><strong>Re-check:</strong> <code>%s</code></p>
</article>""" % (e(f["id"]), e(f["id"]), e(f["title"]), e(f["severity"]), e(f["severity"].upper()),
                 e(f["area"]), e(f["status"]), e(f["found_at_utc"]), e(f["why_it_matters"]),
                 "".join(ev), e(f["recheck"])))
        sev = {}
        for f in finds:
            sev[f["severity"]] = sev.get(f["severity"], 0) + 1
        body = """<p>Read-only, offline audit of this repository, run at %s on branch <code>%s</code> at
commit <code>%s</code>. Every finding is computed from files in the working tree at build time and quotes
the line it found, so nothing is asserted from memory; the links open the exact file and line on GitHub at
the audited commit for manual review. No file outside this session's claimed scope was modified - that is
itself checked (<a href="#A-D7D-14">A-D7D-14</a>).</p>
<div class="grid">%s</div>
%s""" % (e(self.audit["generated_at_utc"]), e(self.audit.get("branch", "")), e(self.audit.get("head", "")),
         "".join('<div class="kpi"><b>%d</b><span>%s severity</span></div>' % (n, e(k))
                 for k, n in sorted(sev.items(), key=lambda x: order.get(x[0], 9))),
         "".join(blocks))
        return self.page("Repository audit", "repo-audit.html", body,
                         subtitle="%d findings with file:line evidence and GitHub links: coordination-board "
                                  "numbering and stale claims, duplicate task ids, page weights, link and "
                                  "source-link integrity, evidence naming, and this session's own scope "
                                  "compliance." % len(finds))

    # -------------------------------------------------------------------- run
    def build(self):
        os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
        with open(os.path.join(OUT, "assets", "style.css"), "w", encoding="utf-8") as fh:
            fh.write(CSS.strip() + "\n")
        written = [self.write("index.html", self.index()),
                   self.write("matches.html", self.matches()),
                   self.write("markets.html", self.markets()),
                   self.write("high-confidence.html", self.high()),
                   self.write("predictions.html", self._predictions_page()),
                   self.write("sports.html", self.sports_index()),
                   self.write("analysis.html", self.analysis()),
                   self.write("sources.html", self._sources_page()),
                   self.write("flagged.html", self.flagged()),
                   self.write("repo-audit.html", self.repo_audit())]
        for slug, name in SPORTS:
            written.append(self.write(os.path.join("sports", slug + ".html"), self.sport_page(slug, name)))
        return written


def main():
    site = Site()
    written = site.build()
    total = sum(os.path.getsize(p) for p in written)
    print("wrote %d pages (%.0f KB) under d7d19a67/" % (len(written), total / 1024.0))
    for p in written:
        print("  %-44s %6.1f KB" % (os.path.relpath(p, ROOT), os.path.getsize(p) / 1024.0))


if __name__ == "__main__":
    main()
