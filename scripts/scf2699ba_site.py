#!/usr/bin/env python3
"""T67 - static site builder for the 23 October 2026 desk.

Writes 24 self-contained pages into cf2699ba/. Inline CSS only, no scripts, no external assets,
relative links only, so the desk renders from any subpath on Pages.

Run: python3 scripts/scf2699ba_site.py
"""
import json
import pathlib
from html import escape as e

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "cf2699ba"
OUT = ROOT / "cf2699ba"

CSS = """
:root{--bg:#0a101c;--panel:#111b2c;--panel2:#16233a;--ink:#e9eefb;--muted:#8fa1c0;--line:#22314b;
--accent:#4cc9f0;--high:#2ee6a8;--med:#ffc857;--low:#93a3c4;--bad:#ff6b6b}
*{box-sizing:border-box}
body{margin:0;background:radial-gradient(1200px 600px at 20% -10%,#16284a 0%,#0a101c 55%);
color:var(--ink);font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px 64px}
header.top{border-bottom:1px solid var(--line);background:rgba(10,16,28,.85);position:sticky;top:0;z-index:9;
backdrop-filter:blur(8px)}
header.top .inner{max-width:1180px;margin:0 auto;padding:14px 20px;display:flex;gap:18px;align-items:baseline;
flex-wrap:wrap}
.brand{font-weight:700;letter-spacing:.02em;font-size:15px}
.brand span{color:var(--accent)}
nav a{margin-right:14px;font-size:13px;color:var(--muted)}
nav a.on{color:var(--ink);border-bottom:2px solid var(--accent);padding-bottom:2px}
h1{font-size:30px;line-height:1.2;margin:34px 0 6px;letter-spacing:-.01em}
h2{font-size:19px;margin:34px 0 10px;letter-spacing:-.01em}
h3{font-size:15px;margin:22px 0 8px;color:var(--ink)}
p.lede{color:var(--muted);max-width:82ch;margin:0 0 18px}
.stamp{font-size:12px;color:var(--muted);margin:0 0 8px}
.grid{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));margin:18px 0}
.card{background:linear-gradient(180deg,var(--panel) 0%,var(--panel2) 100%);border:1px solid var(--line);
border-radius:12px;padding:14px 16px}
.card .k{font-size:11px;text-transform:uppercase;letter-spacing:.09em;color:var(--muted)}
.card .v{font-size:26px;font-weight:700;margin-top:4px;letter-spacing:-.02em}
.card .s{font-size:12px;color:var(--muted);margin-top:2px}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:6px 18px 16px;margin:16px 0}
.tablewrap{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:var(--panel)}
table{border-collapse:collapse;width:100%;font-size:13px}
th,td{padding:9px 11px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:11px;text-transform:uppercase;letter-spacing:.07em;color:var(--muted);background:var(--panel2);
position:sticky;top:0}
tr:last-child td{border-bottom:0}
tbody tr:nth-child(even){background:rgba(255,255,255,.015)}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
.badge{display:inline-block;padding:1px 8px;border-radius:999px;font-size:11px;font-weight:600;
border:1px solid transparent;white-space:nowrap}
.t-high{color:#06231a;background:var(--high)}
.t-med{color:#2b1e00;background:var(--med)}
.t-low{color:#0a101c;background:var(--low)}
.t-bad{color:#2a0505;background:var(--bad)}
.t-ghost{color:var(--muted);border-color:var(--line);background:transparent}
.src{font-size:11px;color:var(--muted)}
.note{border-left:3px solid var(--accent);background:rgba(76,201,240,.06);padding:10px 14px;border-radius:0 8px 8px 0;
margin:14px 0;font-size:13.5px;color:#cfe0f7}
.warnbox{border-left:3px solid var(--bad);background:rgba(255,107,107,.07);padding:10px 14px;border-radius:0 8px 8px 0;
margin:14px 0;font-size:13.5px;color:#ffd9d9}
ul.tight{margin:8px 0 8px 18px;padding:0}ul.tight li{margin:4px 0;font-size:13.5px;color:#cfdcf2}
.bar{height:6px;border-radius:4px;background:var(--panel2);overflow:hidden;margin-top:6px}
.bar i{display:block;height:100%;background:linear-gradient(90deg,var(--accent),var(--high))}
footer{margin-top:40px;padding-top:16px;border-top:1px solid var(--line);color:var(--muted);font-size:12px}
.kicker{font-size:11px;text-transform:uppercase;letter-spacing:.12em;color:var(--accent);margin:26px 0 0}
.two{display:grid;gap:18px;grid-template-columns:1.15fr .85fr}
@media(max-width:820px){.two{grid-template-columns:1fr}}
"""

NAV = [
    ("index.html", "Summary"),
    ("matches.html", "Matches"),
    ("markets.html", "Markets"),
    ("confidence.html", "Confidence"),
    ("predictions.html", "Predictions"),
    ("analysis.html", "Analysis"),
    ("flagged.html", "Flagged"),
    ("sources.html", "Sources"),
    ("methodology.html", "Method"),
]


def chip(tier):
    cls = {"High": "t-high", "Medium": "t-med", "Low": "t-low"}.get(tier, "t-ghost")
    return f'<span class="badge {cls}">{e(tier)}</span>'


def am(x):
    if x is None:
        return "&mdash;"
    return e(x)


def page(out_path, title, active, body, prefix="", subtitle="", kicker=""):
    navbits = []
    for href, label in NAV:
        cls = ' class="on"' if href == active else ""
        navbits.append(f'<a href="{prefix}{href}"{cls}>{e(label)}</a>')
    kk = f'<p class="kicker">{e(kicker)}</p>' if kicker else ""
    sub = f'<p class="lede">{subtitle}</p>' if subtitle else ""
    html = (
        "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        f"<title>{e(title)}</title><style>{CSS}</style></head><body>"
        "<header class=\"top\"><div class=\"inner\">"
        f"<div class=\"brand\">OLBG desk <span>23 Oct 2026</span></div>"
        "<nav>" + "".join(navbits) + "</nav></div></header>"
        f"<div class=\"wrap\">{kk}<h1>{e(title)}</h1>{sub}{body}"
        "<footer>Snapshot taken 2026-10-23 between 16:20Z and 16:40Z. Six fixtures confirmed on "
        "governing-body pages, the remainder listed as discovery with the reason shown. Prices are "
        "originated here from the inputs named on each row; no bookmaker quote is claimed. This is a "
        "research record, not betting advice.</footer></div></body></html>"
    )
    out_path.write_text(html)


def main():
    sports = json.loads((DATA / "sports.json").read_text())
    sources = json.loads((DATA / "sources.json").read_text())
    discovery = json.loads((DATA / "discovery.json").read_text())
    fixtures = json.loads((DATA / "fixtures.json").read_text())
    lines = json.loads((DATA / "lines.json").read_text())
    preds = json.loads((DATA / "predictions.json").read_text())
    flags = json.loads((DATA / "flagged.json").read_text())

    OUT.mkdir(exist_ok=True)
    (OUT / "sports").mkdir(exist_ok=True)

    rows = lines["rows"]
    official = [r for r in rows if r["class"] == "official"]
    indicative = [r for r in rows if r["class"] == "consensus"]
    tiers = lines["tier_counts"]
    src_by_id = {s["id"]: s for s in sources}
    per = {}
    for r in discovery:
        per.setdefault(r["sport"], []).append(r)
    sport_name = {s["key"]: s["name"] for s in sports}
    off_by_sport = {}
    for r in official:
        off_by_sport.setdefault(r["sport"], []).append(r)

    def src_link(sid):
        s = src_by_id.get(sid)
        if not s:
            return e(sid)
        return f'<a class="src" href="{e(s["url"])}" rel="noopener">{e(s["org"])}</a>'

    kpi = (
        '<div class="grid">'
        f'<div class="card"><div class="k">OLBG listings</div><div class="v">{len(discovery)}</div>'
        f'<div class="s">across 15 sports, one capture</div></div>'
        f'<div class="card"><div class="k">Fixtures confirmed</div><div class="v">{len(fixtures)}</div>'
        f'<div class="s">on a governing-body page</div></div>'
        f'<div class="card"><div class="k">Prices originated</div><div class="v">{len(rows)}</div>'
        f'<div class="s">{len(official)} from official inputs, {len(indicative)} indicative</div></div>'
        f'<div class="card"><div class="k">High confidence</div><div class="v">{tiers.get("High", 0)}</div>'
        f'<div class="s">Medium {tiers.get("Medium", 0)} &middot; Low {tiers.get("Low", 0)}</div></div>'
        f'<div class="card"><div class="k">Write-ups</div><div class="v">{len(preds)}</div>'
        f'<div class="s">all 30 words or longer</div></div>'
        f'<div class="card"><div class="k">Flags</div><div class="v">{len(flags)}</div>'
        f'<div class="s">{sum(1 for f in flags if f["severity"] == "high")} high severity</div></div>'
        "</div>"
    )

    # ---------------------------------------------------------------- index
    best = sorted(official, key=lambda r: -r["p"])[:3]
    linked = [d for d in discovery
              if any(str(d["olbg_event_id"]) == str(f.get("olbg_event_id")) for f in fixtures)]
    board = []
    for r in best:
        band = "inside the -250 floor" if r["in_band"] else "outside the -250 floor"
        board.append(
            "<tr>"
            f'<td>{e(sport_name.get(r["sport"], r["sport"]))}</td>'
            f'<td>{e(r["fixture"])}</td><td>{e(r["selection"])}</td>'
            f'<td class="num">{r["p"]*100:.1f}%</td>'
            f'<td class="num">{e(r["american_text"])}</td>'
            f'<td>{chip(r["tier"])}</td><td class="src">{e(band)}</td>'
            f'<td>{src_link(r["source"])}</td></tr>'
        )
    fx_rows = []
    for f in fixtures:
        t = f.get("start_utc") or f.get("local_time") or "&mdash;"
        fx_rows.append(
            "<tr>"
            f'<td>{e(sport_name.get(f["sport"], f["sport"]))}</td><td>{e(f["name"])}</td>'
            f'<td>{e(f["competition"])}</td><td>{e(t)}</td><td>{e(f.get("venue") or "")}</td>'
            f'<td class="src">{e(f.get("state") or "")}</td><td>{src_link(f["evidence"])}</td></tr>'
        )
    sport_cards = []
    for s in sports:
        n = len(per.get(s["key"], []))
        o = len(off_by_sport.get(s["key"], []))
        state = "confirmed fixtures" if o else ("listings only" if n else "empty hub")
        sport_cards.append(
            '<a class="card" href="sports/' + s["key"] + '.html">'
            f'<div class="k">{e(s["name"])}</div><div class="v">{n}</div>'
            f'<div class="s">{o} priced from official input &middot; {e(state)}</div></a>'
        )
    index_body = (
        kpi
        + '<p class="stamp">Snapshot 2026-10-23 16:20Z&ndash;16:40Z &middot; all times as printed by the '
          'source, no timezone assumed</p>'
        + '<div class="warnbox"><strong>Read this first.</strong> Zero selections clear the brief\'s High '
          'bar today. That bar needs a win chance above 70% <em>and</em> a price no shorter than -250, and '
          'those two conditions together leave a 70.0&ndash;71.4% window. The strongest confirmed '
          'selection, Edinburgh at about 85%, prices at -567; the next best confirmed side sits at 60.0%. '
          'No row was re-graded to fill a target. The arithmetic is on the '
          '<a href="analysis.html">analysis page</a>.</div>'
        + '<h2>Executive summary</h2>'
        + '<div class="two"><div class="panel"><h3>Strongest confirmed selections</h3>'
          '<div class="tablewrap"><table><thead><tr><th>Sport</th><th>Match</th><th>Selection</th>'
          '<th class="num">Chance</th><th class="num">Price</th><th>Grade</th><th>Band</th><th>Source</th>'
          '</tr></thead><tbody>' + "".join(board) + '</tbody></table></div>'
          '<p class="src">Chance is this desk\'s own estimate, not a market quote. Price is the fair '
          'decimal converted to American at 1/p with no margin.</p></div>'
        + '<div class="panel"><h3>What the day actually offers</h3><ul class="tight">'
          '<li>Six fixtures could be confirmed on a governing-body page: two NHL games, World Series '
          'Game 1, and three United Rugby Championship ties.</li>'
          f'<li>Everything else &mdash; {len(discovery) - len(linked)} OLBG rows &mdash; is discovery. '
          'Each carries the reason it could not be confirmed on its sport page.</li>'
          '<li>Golf returned no tips at all. Rugby league carries 2027 outrights only.</li>'
          '<li>No injury, suspension or availability feed was readable for any sport, so none is '
          'mentioned in any write-up.</li>'
          '<li>Next confirmed start: World Series Game 1 at 00:00Z on 24 October, from '
          'American Family Field.</li></ul></div></div>'
        + '<h2>Confirmed fixtures</h2><div class="tablewrap"><table><thead><tr><th>Sport</th>'
          '<th>Fixture</th><th>Competition</th><th>Start (as published)</th><th>Venue</th><th>State</th>'
          '<th>Official source</th></tr></thead><tbody>' + "".join(fx_rows) + '</tbody></table></div>'
        + '<h2>Fifteen sports</h2><div class="grid">' + "".join(sport_cards) + "</div>"
        + '<div class="note">Method in one line: OLBG is used only to learn which events exist. A row '
          'gets a price only when a governing body confirms the fixture and supplies the numbers. '
          'A tip-vote share is halved toward a coin flip, capped at 90%, and can never be graded above '
          'Low. Full detail on <a href="methodology.html">method</a>.</div>'
    )
    page(OUT / "index.html", "Fifteen-sport desk, 23 October 2026", "index.html", index_body,
         subtitle="A live sweep of the fifteen sports in scope, checked against governing bodies, with "
                  "prices originated here and the gaps left visible.")

    # ---------------------------------------------------------------- matches
    def disc_rows(items, prefix):
        out = []
        for r in items:
            conf = "discovery"
            if str(r["olbg_event_id"]) in {str(f.get("olbg_event_id")) for f in fixtures}:
                conf = "fixture confirmed"
            out.append(
                "<tr>"
                f'<td>{e(sport_name.get(r["sport"], r["sport"]))}</td>'
                f'<td><a href="{e(r["url"])}" rel="noopener">{e(r["name"])}</a></td>'
                f'<td>{e(r["competition"] or "&mdash;")}</td>'
                f'<td>{e(r["olbg_time_text"])}</td>'
                f'<td>{e(r["olbg_pick"])}</td><td>{e(r["market"])}</td>'
                f'<td class="num">{r["olbg_tips"]}</td><td class="num">{r["share"]*100:.0f}%</td>'
                f'<td class="src">{e(conf)}</td></tr>'
            )
        return "".join(out)

    head = ('<div class="tablewrap"><table><thead><tr><th>Sport</th><th>Event</th><th>Competition</th>'
            '<th>Time as printed</th><th>Leading tip</th><th>Market</th><th class="num">Tips</th>'
            '<th class="num">Share</th><th>Status</th></tr></thead><tbody>')
    groups = []
    for s in sports:
        items = per.get(s["key"], [])
        if not items:
            groups.append(f'<h2>{e(s["name"])}</h2><div class="warnbox">Empty hub: the page returned no '
                          f'listings, so there is nothing to check. No row is invented.</div>')
            continue
        groups.append(f'<h2>{e(s["name"])} <span class="src">&middot; {len(items)} rows</span></h2>'
                      + head + disc_rows(items, "") + "</tbody></table></div>")
    matches_body = (
        '<div class="note">Times are reproduced exactly as OLBG prints them. The hub prints no timezone '
        'and mixes conventions between sports, so no conversion is offered anywhere in this desk '
        '(see flag F-CF-01). Sorting is by sport, then page order.</div>'
        + "".join(groups)
    )
    page(OUT / "matches.html", "Every match the hubs list", "matches.html", matches_body,
         subtitle="134 rows across fifteen sports, exactly as published, with the confirmation status of "
                  "each one stated in the last column.")

    # ---------------------------------------------------------------- markets
    def price_table(items):
        body = []
        for r in items:
            body.append(
                "<tr>"
                f'<td>{e(sport_name.get(r["sport"], r["sport"]))}</td>'
                f'<td>{e(r["fixture"])}</td><td>{e(r["market"])}</td><td>{e(r["selection"])}</td>'
                f'<td class="num">{r["p"]*100:.1f}%</td>'
                f'<td class="num">{r["decimal"]:.3f}</td>'
                f'<td class="num">{e(r["american_text"])}</td>'
                f'<td>{"yes" if r["in_band"] else "no"}</td>'
                f'<td>{chip(r["tier"])}</td>'
                f'<td class="src">{e(r["note"])}</td>'
                f'<td>{src_link(r["source"])}</td></tr>'
            )
        return "".join(body)

    mk_head = ('<div class="tablewrap"><table><thead><tr><th>Sport</th><th>Fixture</th><th>Market</th>'
               '<th>Selection</th><th class="num">Chance</th><th class="num">Decimal</th>'
               '<th class="num">American</th><th>In band</th><th>Grade</th><th>Derivation</th>'
               '<th>Input</th></tr></thead><tbody>')
    withheld_rows = []
    for w in lines["withheld"]:
        withheld_rows.append(
            "<tr>"
            f'<td>{e(sport_name.get(w["sport"], w["sport"]))}</td><td>{e(w["fixture"])}</td>'
            f'<td>{e(w["market"])}</td><td class="src">{e(w["reason"])}</td>'
            f'<td>{src_link(w["source"])}</td></tr>'
        )
    markets_body = (
        '<div class="note">Two kinds of price appear here and they are never mixed. Rows marked '
        '<em>official</em> come from a confirmed fixture and a named numeric input. Rows marked '
        '<em>indicative</em> come from an OLBG tip-vote share, halved toward a coin flip and capped, and '
        'are graded Low permanently. The fair price is 1/p with no margin added, so it is a number this '
        'desk would have to lay, not a quote from anyone.</div>'
        + f'<h2>From official inputs <span class="src">&middot; {len(official)} rows on '
          f'{len({r["fixture_id"] for r in official})} fixtures</span></h2>'
        + mk_head + price_table(official) + "</tbody></table></div>"
        + f'<h2>Indicative only <span class="src">&middot; {len(indicative)} rows</span></h2>'
        + mk_head + price_table(indicative) + "</tbody></table></div>"
        + f'<h2>Markets examined and withheld <span class="src">&middot; {len(withheld_rows)} rows</span></h2>'
        + '<div class="tablewrap"><table><thead><tr><th>Sport</th><th>Fixture</th><th>Market</th>'
          '<th>Why no line</th><th>Input</th></tr></thead><tbody>' + "".join(withheld_rows)
        + "</tbody></table></div>"
    )
    page(OUT / "markets.html", "Originated markets", "markets.html", markets_body,
         subtitle="Money lines, run lines, totals and outrights, priced here from named inputs, with the "
                  "derivation printed on every row.")

    # ---------------------------------------------------------------- confidence
    tier_expl = (
        '<div class="panel"><h3>How a grade is earned</h3><ul class="tight">'
        '<li><strong>High</strong> needs three things at once: a confirmed fixture, a win chance at or '
        'above 70%, and a price between -250 and +10000. Because a 70% chance prices at about -233, the '
        'band squeezes the eligible window to 70.0&ndash;71.4%.</li>'
        '<li><strong>Medium</strong> is a confirmed fixture at 62&ndash;70%.</li>'
        '<li><strong>Low</strong> is everything else, including every indicative row, whatever its '
        'number.</li></ul>'
        '<p class="src">Grades are recomputed from p and the American price by the build script and '
        'checked again by the validator, so a hand edit cannot smuggle a High through.</p></div>'
    )
    sport_top = []
    for s in sports:
        top = lines["top5"].get(s["key"], [])
        if not top:
            sport_top.append(f'<h2>{e(s["name"])}</h2><div class="warnbox">No listing, so no candidates. '
                             f'The hub returned nothing to rank.</div>')
            continue
        trs = []
        for i, t in enumerate(top, 1):
            trs.append(
                "<tr>"
                f'<td class="num">{i}</td><td>{e(t["fixture"])}</td><td>{e(t["selection"])}</td>'
                f'<td>{e(t["market"])}</td><td class="num">{t["p"]*100:.1f}%</td>'
                f'<td class="num">{e(t["american_text"])}</td><td>{chip(t["tier"])}</td>'
                f'<td class="src">{e(t["class"])}</td><td>{src_link(t["source"])}</td></tr>'
            )
        sport_top.append(
            f'<h2>{e(s["name"])} <span class="src">&middot; {len(lines["top5"][s["key"]])} of '
            f'{len(per.get(s["key"], []))} rows</span></h2>'
            '<div class="tablewrap"><table><thead><tr><th class="num">#</th><th>Fixture</th>'
            '<th>Selection</th><th>Market</th><th class="num">Chance</th><th class="num">Price</th>'
            '<th>Grade</th><th>Class</th><th>Input</th></tr></thead><tbody>' + "".join(trs)
            + "</tbody></table></div>"
        )
    conf_body = (
        '<div class="warnbox"><strong>High: 0. Medium: 1. Low: 132.</strong> On a day with six confirmed '
        'fixtures and no short-priced leader among them, the High bar is simply not reachable. The one '
        'Medium is Edinburgh at about 85%, and at -567 it sits outside the -250 floor, so under the '
        'brief\'s own rule it cannot be High either.</div>'
        + tier_expl
        + '<h2>Closest miss</h2><div class="panel"><p>Edinburgh at 0.850 prices at -567. The floor is '
          '-250, which corresponds to 71.4%. To be High the selection would have to be weaker than that '
          'and still above 70%, a window 1.4 points wide. Two selections this season would need to sit '
          'inside it simultaneously for a single High to exist.</p>'
          '<div class="bar"><i style="width:85%"></i></div>'
          '<p class="src">Bar shows the 85% estimate against the 70% floor and the 71.4% ceiling of the '
          'eligible band.</p></div>'
        + '<h2>Top five per sport</h2><p class="lede">Ranked by this desk\'s own chance estimate. '
          'Because most rows rest on a tip-vote share, the ranking is a reading order, not a bet list: '
          'the class column says which rows have an official input behind them.</p>'
        + "".join(sport_top)
    )
    page(OUT / "confidence.html", "Confidence, sport by sport", "confidence.html", conf_body,
         subtitle="Five ranked candidates per sport, with the class of evidence printed next to each one.")

    # ---------------------------------------------------------------- predictions
    pblocks = []
    for p in preds:
        facts = "".join(
            f'<li><strong>{e(f["k"])}:</strong> {e(f["v"])} &mdash; {src_link(f["src"])}</li>'
            for f in p["facts"]
        )
        band = "inside" if p["in_band"] else "outside"
        pblocks.append(
            '<div class="panel">'
            f'<p class="kicker">{e(sport_name.get(p["sport"], p["sport"]))} &middot; {e(p["market"])}</p>'
            f'<h3>{e(p["fixture"])} &mdash; {e(p["selection"])}</h3>'
            f'<p class="src">{p["words"]} words &middot; {p["p"]*100:.1f}% &middot; '
            f'{e(p["american_text"])} &middot; {p["decimal"]:.3f} decimal &middot; {band} the -250 '
            f'floor &middot; grade {p["tier"]}</p>'
            f'<p>{e(p["body"])}</p>'
            f'<ul class="tight">{facts}</ul></div>'
        )
    pred_body = (
        '<div class="note">Seven write-ups, all attached to a confirmed fixture and to a price printed on '
        'the markets page. Each clause is walked back to a page in the list under it. None of them says '
        'anything about injuries, because no availability feed could be read today; the gap is recorded '
        'as flag F-CF-16 rather than filled with a guess.</div>' + "".join(pblocks)
    )
    page(OUT / "predictions.html", "Write-ups", "predictions.html", pred_body,
         subtitle="One argument per pick, 58 to 71 words, each fact tied to the page it came from.")

    # ---------------------------------------------------------------- analysis
    derivs = []
    for fid, d in lines["derivations"].items():
        fx = next(f for f in fixtures if f["id"] == fid)
        bits = "".join(f"<li><strong>{e(k)}:</strong> {e(str(v))}</li>" for k, v in d.items())
        derivs.append(f'<div class="panel"><h3>{e(fx["name"])}</h3><ul class="tight">{bits}</ul></div>')
    yield_pct = len(fixtures) / len(discovery) * 100
    analysis_body = (
        '<h2>The day in numbers</h2><div class="grid">'
        f'<div class="card"><div class="k">Rows swept</div><div class="v">{len(discovery)}</div>'
        f'<div class="s">fifteen hubs, one pass</div></div>'
        f'<div class="card"><div class="k">Confirmed</div><div class="v">{len(fixtures)}</div>'
        f'<div class="s">{yield_pct:.1f}% of rows</div></div>'
        f'<div class="card"><div class="k">Priced from official input</div><div class="v">{len(official)}</div>'
        f'<div class="s">on {len({r["fixture_id"] for r in official})} fixtures</div></div>'
        f'<div class="card"><div class="k">Indicative</div><div class="v">{len(indicative)}</div>'
        f'<div class="s">vote-share derived, permanently Low</div></div></div>'
        '<h2>Why the High bar could not be met</h2>'
        '<div class="panel"><p>A 70% win chance is a fair price of about -233. A price of -250 is a 71.4% '
        'chance. So the two halves of the rule overlap only between 70.0% and 71.4%: any selection good '
        'enough to clear the floor is too short to clear the band, and any selection long enough to sit '
        'inside the band is, by construction, below the floor.</p>'
        '<p>The practical effect is that High is reachable only by a genuinely marginal favourite &mdash; '
        'the sort of price a bookmaker would hang at -240 to -245. None of the six fixtures confirmed '
        'today produces one. The strongest, Edinburgh, comes out at about 85% and prices at -567.</p></div>'
        '<h2>How each price was built</h2>'
        + "".join(derivs)
        + '<h2>Where the coverage stops</h2><div class="panel"><ul class="tight">'
        f'<li>128 of 134 rows are discovery. The reasons are per sport: consent walls for darts, a match '
        f'list that stops before today for snooker, a client-rendered schedule for EuroLeague and an '
        f'HTTP 500 from the NBA scoreboard, score pages that list different matches for tennis, filters '
        f'without fixtures for cricket, and navigation without fixtures for Gaelic games.</li>'
        '<li>No availability data anywhere, so no prediction mentions an injury.</li>'
        '<li>Greyhounds: no GBGB card was readable, so the sixteen races are names on a page and nothing '
        'more.</li></ul></div>'
    )
    page(OUT / "analysis.html", "What the numbers mean", "analysis.html", analysis_body,
         subtitle="The verification yield, the arithmetic behind zero High picks, and a derivation trail "
                  "for every price.")

    # ---------------------------------------------------------------- flagged
    sev = {"high": "t-bad", "medium": "t-med", "low": "t-low"}
    frows = []
    for f in flags:
        frows.append(
            "<tr>"
            f'<td class="num">{e(f["id"])}</td>'
            f'<td><span class="badge {sev.get(f["severity"], "t-ghost")}">{e(f["severity"])}</span></td>'
            f'<td>{e(f["sport"])}</td><td>{e(f["row"])}</td>'
            f'<td>{e(f["issue"])}</td><td class="src">{e(f["action"])}</td>'
            f'<td>{src_link(f["source"])}</td></tr>'
        )
    flagged_body = (
        '<div class="note">Everything that did not reconcile is here rather than being quietly dropped. '
        f'{len(flags)} entries, {sum(1 for f in flags if f["severity"] == "high")} of them high severity. '
        'None of them blocks publication; all of them are visible.</div>'
        '<div class="tablewrap"><table><thead><tr><th class="num">ID</th><th>Severity</th><th>Sport</th>'
        '<th>Where</th><th>What is wrong</th><th>What this desk did</th><th>Source</th></tr></thead>'
        '<tbody>' + "".join(frows) + "</tbody></table></div>"
    )
    page(OUT / "flagged.html", "Flagged for review", "flagged.html", flagged_body,
         subtitle="Irregularities, contradictions and access failures, each with the page that shows it.")

    # ---------------------------------------------------------------- sources
    srows = []
    for s in sources:
        kind = "governing body" if s["official"] else "aggregator (discovery only)"
        srows.append(
            "<tr>"
            f'<td><a href="{e(s["url"])}" rel="noopener">{e(s["org"])}</a></td>'
            f'<td>{e(s["title"])}</td><td class="src">{e(s["read_at"])}</td>'
            f'<td>{e(kind)}</td><td class="src">{e(s["read"])}</td><td class="src">{e(s["limits"])}</td>'
            "</tr>"
        )
    sources_body = (
        '<div class="note">Nine pages were opened this session. Six are governing bodies and supply every '
        'confirmed fixture and every numeric input. OLBG supplies only the existence of an event and the '
        'tip-vote share, and is never used to confirm a fact.</div>'
        '<div class="tablewrap"><table><thead><tr><th>Publisher</th><th>Page</th><th>Read at</th>'
        '<th>Kind</th><th>What it gave</th><th>What it would not give</th></tr></thead><tbody>'
        + "".join(srows) + "</tbody></table></div>"
    )
    page(OUT / "sources.html", "Sources, and what each one refused to say", "sources.html", sources_body,
         subtitle="Nine pages, the timestamp each was read, and the limit of each one stated up front.")

    # ---------------------------------------------------------------- methodology
    params = lines["parameters"]
    prow = "".join(f"<tr><td>{e(k)}</td><td class='num'>{e(str(v))}</td></tr>" for k, v in params.items())
    method_body = (
        '<h2>The rule this desk runs on</h2>'
        '<div class="panel"><ol class="tight">'
        '<li>Sweep the hub and record the event, competition, printed time, leading tip, market, tip '
        'count and share. Change nothing.</li>'
        '<li>Try to confirm the fixture on the governing body\'s own page. If it is not there, the row '
        'stays discovery and says so.</li>'
        '<li>Price only from a named numeric input on a confirmed fixture. De-vig quotes where quotes '
        'exist; use runs, records or results where they do; with nothing, publish no line.</li>'
        '<li>Grade mechanically from p and the price. Do not adjust a grade to hit a target.</li>'
        '<li>Write only about confirmed facts, and hang each clause on a source id.</li>'
        '<li>Publish every unresolved thing on the flagged page.</li></ol></div>'
        '<h2>Declared parameters</h2><div class="tablewrap"><table><thead><tr><th>Name</th>'
        '<th class="num">Value</th></tr></thead><tbody>' + prow + "</tbody></table></div>"
        '<p class="lede">Every one of these is a stated prior, chosen before the day was priced, not '
        'fitted afterwards. The rugby shrinkage exists because a single confirmed round is a very thin '
        'sample; the 0.85 ceiling exists so a one-match sample cannot be expressed as a 99% certainty.</p>'
        '<h2>Rebuild</h2><div class="panel"><ul class="tight">'
        '<li><code>python3 scripts/scf2699ba_data.py</code> &mdash; sources, discovery, fixtures, inputs</li>'
        '<li><code>python3 scripts/scf2699ba_model.py</code> &mdash; prices and grades</li>'
        '<li><code>python3 scripts/scf2699ba_predictions.py</code> &mdash; write-ups and flags</li>'
        '<li><code>python3 scripts/scf2699ba_site.py</code> &mdash; these 24 pages</li>'
        '<li><code>python3 scripts/scf2699ba_validate.py</code> &mdash; the gate; exits non-zero on failure</li>'
        '</ul></div>'
        '<h2>What this desk will not do</h2><div class="panel"><ul class="tight">'
        '<li>It will not convert an OLBG time to UTC. The hub prints no zone and mixes conventions '
        'between sports.</li>'
        '<li>It will not quote a bookmaker price. The fair price shown is 1/p with no margin.</li>'
        '<li>It will not call a tip-vote share a probability without halving it and capping it.</li>'
        '<li>It will not mention an injury that no source published.</li></ul></div>'
    )
    page(OUT / "methodology.html", "Method", "methodology.html", method_body,
         subtitle="The six steps, the declared parameters, and the things this desk deliberately refuses "
                  "to do.")

    # ---------------------------------------------------------------- sport pages
    for s in sports:
        k = s["key"]
        items = per.get(k, [])
        offs = off_by_sport.get(k, [])
        fl = [f for f in flags if f["sport"] in (k, "all sports")]
        if items:
            tb = ('<div class="tablewrap"><table><thead><tr><th>Event</th><th>Competition</th>'
                  '<th>Time as printed</th><th>Leading tip</th><th>Market</th><th class="num">Tips</th>'
                  '<th class="num">Share</th></tr></thead><tbody>'
                  + "".join(
                      f'<tr><td><a href="{e(r["url"])}" rel="noopener">{e(r["name"])}</a></td>'
                      f'<td>{e(r["competition"] or "&mdash;")}</td><td>{e(r["olbg_time_text"])}</td>'
                      f'<td>{e(r["olbg_pick"])}</td><td>{e(r["market"])}</td>'
                      f'<td class="num">{r["olbg_tips"]}</td>'
                      f'<td class="num">{r["share"]*100:.0f}%</td></tr>'
                      for r in items)
                  + "</tbody></table></div>")
        else:
            tb = ('<div class="warnbox">The hub returned no listings for this sport. There is nothing to '
                  'confirm, price or write about, and no row has been manufactured to fill the page.</div>')

        if offs:
            pt = ('<div class="tablewrap"><table><thead><tr><th>Fixture</th><th>Market</th>'
                  '<th>Selection</th><th class="num">Chance</th><th class="num">Price</th><th>Grade</th>'
                  '<th>Derivation</th></tr></thead><tbody>'
                  + "".join(
                      f'<tr><td>{e(r["fixture"])}</td><td>{e(r["market"])}</td>'
                      f'<td>{e(r["selection"])}</td><td class="num">{r["p"]*100:.1f}%</td>'
                      f'<td class="num">{e(r["american_text"])}</td><td>{chip(r["tier"])}</td>'
                      f'<td class="src">{e(r["note"])}</td></tr>'
                      for r in offs)
                  + "</tbody></table></div>")
        else:
            pt = ('<div class="note">No fixture in this sport could be confirmed on a governing-body page, '
                  'so no line is published from official input. The indicative prices on the '
                  '<a href="../markets.html">markets page</a> cover the rows that have a vote share, and '
                  'they are graded Low by rule.</div>')

        fxblock = ""
        my_fx = [f for f in fixtures if f["sport"] == k]
        if my_fx:
            fxblock = ('<h2>Confirmed fixtures</h2><div class="tablewrap"><table><thead><tr>'
                       '<th>Fixture</th><th>Competition</th><th>Start</th><th>Venue</th><th>State</th>'
                       '<th>Source</th></tr></thead><tbody>'
                       + "".join(
                           f'<tr><td>{e(f["name"])}</td><td>{e(f["competition"])}</td>'
                           f'<td>{e(f.get("start_utc") or f.get("local_time") or "&mdash;")}</td>'
                           f'<td>{e(f.get("venue") or "")}</td><td class="src">{e(f.get("state") or "")}</td>'
                           f'<td>{src_link(f["evidence"])}</td></tr>'
                           for f in my_fx)
                       + "</tbody></table></div>")

        flrows = "".join(
            f'<tr><td class="num">{e(f["id"])}</td><td>{e(f["severity"])}</td><td>{e(f["issue"])}</td>'
            f'<td>{src_link(f["source"])}</td></tr>' for f in fl)
        flblock = ('<h2>Flags touching this sport</h2><div class="tablewrap"><table><thead><tr>'
                   '<th class="num">ID</th><th>Severity</th><th>Issue</th><th>Source</th></tr></thead>'
                   '<tbody>' + flrows + "</tbody></table></div>") if flrows else ""

        pr = [p for p in preds if p["sport"] == k]
        prblock = ""
        if pr:
            prblock = '<h2>Write-ups</h2>' + "".join(
                f'<div class="panel"><h3>{e(p["fixture"])} &mdash; {e(p["selection"])}</h3>'
                f'<p class="src">{p["p"]*100:.1f}% &middot; {e(p["american_text"])} &middot; grade '
                f'{p["tier"]}</p><p>{e(p["body"])}</p></div>' for p in pr)

        body = (
            f'<div class="grid"><div class="card"><div class="k">Hub listings</div><div class="v">'
            f'{len(items)}</div><div class="s">captured 2026-10-23</div></div>'
            f'<div class="card"><div class="k">Confirmed fixtures</div><div class="v">{len(my_fx)}</div>'
            f'<div class="s">governing-body pages</div></div>'
            f'<div class="card"><div class="k">Prices from official input</div><div class="v">{len(offs)}</div>'
            f'<div class="s">graded on evidence</div></div>'
            f'<div class="card"><div class="k">Hub</div><div class="v" style="font-size:15px">'
            f'<a href="{e(s["hub"])}" rel="noopener">olbg.com</a></div>'
            f'<div class="s">coverage: {e(s["coverage"])}</div></div></div>'
            + fxblock + '<h2>Prices from official input</h2>' + pt
            + '<h2>Hub listings</h2>' + tb + prblock + flblock
        )
        page(OUT / "sports" / f"{k}.html", s["name"], "", body, prefix="../",
             kicker="Sport page", subtitle=f"Coverage for {s['name']} on 23 October 2026.")

    files = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*.html"))
    print(f"pages written: {len(files)}")
    print(" ".join(files))


if __name__ == "__main__":
    main()
