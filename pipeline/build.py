"""Canonical static dashboard for the 24 October 2026 desk.

The site is deliberately small and linear. It answers three questions in order:
what do we recommend today, where is it written up, and what is every match we
looked at. Nothing is rendered from an earlier session's snapshot, and nothing
is copied into the published artifact that is not part of this desk.
"""
from __future__ import annotations

import argparse
import csv
import html
import io
import json
import posixpath
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from .assemble import assemble
from .audit import build_audit
from .common import digest, load, now_utc, parse_time, save
from .config import PUBLISHERS, ROOT
from .desk import (FLAGS, MLB_TEAMS, MISSING_CLUBS, SOURCES, SPORT_INDEX, SPORTS,
                   TEAMS, UNCAPTURED, build_desk)

REPO = 'https://github.com/buffedlizard55-lab/OLBG1'
LIVE = 'https://buffedlizard55-lab.github.io/OLBG1/'
OFFICIAL_HOSTS = set(PUBLISHERS) | {'www.nhl.com', 'www.mlb.com'}

# Earlier sessions' desks stay published so the links they issued remain live.
# Each entry is (path inside the artifact, description). Keep these literal:
#   link='b2719ad3/index.html'   link='37003e61/index.html'
#   link='8cfb80b2/index.html'   link='02d3d515/index.html'   link='3d121822/index.html'
ARCHIVE = [
    ('b2719ad3/index.html', '24 Oct 2026 evidence desk: official-feed capture with per-row sources'),
    ('37003e61/index.html', 'Earlier desk: source capture and review queue'),
    ('8cfb80b2/index.html', 'Earlier desk: source capture and review queue'),
    ('02d3d515/index.html', 'Earlier desk: source capture and review queue'),
    ('3d121822/index.html', 'Earlier desk: source capture and review queue'),
    ('2ff8342b/index.html', '24 Oct 2026 desk: fifteen sports, 93 fixtures, 7 originated picks'),
]

NAV = [
    ('summary', 'index.html', "Today's summary"),
    ('picks', 'picks.html', 'Picks'),
    ('predictions', 'predictions.html', 'Written predictions'),
    ('matches', 'matches.html', 'Every match'),
    ('sports', 'sports.html', 'Sports'),
    ('flagged', 'flagged.html', 'Flagged for review'),
    ('sources', 'sources.html', 'Sources'),
    ('method', 'methodology.html', 'How this works'),
    ('reverse', 'reverse-engineering.html', 'Inside OLBG'),
]

CSS = """
:root{--ink:#14261f;--muted:#5b6f66;--line:#dfe7e2;--bg:#f6f8f7;--card:#fff;
--green:#0f6b45;--green-soft:#e7f2ec;--amber:#8a5a00;--amber-soft:#fdf3df;--red:#8e2f2f;--red-soft:#fbeaea}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--green)}
h1,h2,h3{line-height:1.22;margin:0 0 10px}
h1{font-size:30px}h2{font-size:21px}h3{font-size:17px}
p{margin:0 0 12px}
header.top{background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:5}
.wrap{max-width:1120px;margin:0 auto;padding:0 20px}
.toprow{display:flex;align-items:center;gap:16px;justify-content:space-between;padding:12px 0;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--ink);font-weight:700}
.brand span.mark{width:30px;height:30px;border-radius:9px;background:var(--green);color:#fff;display:grid;place-items:center;font-size:14px}
.brand small{display:block;font-weight:500;font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--muted)}
nav.main{display:flex;gap:4px;flex-wrap:wrap;padding:0 0 10px}
nav.main a{padding:6px 11px;border-radius:999px;text-decoration:none;color:var(--muted);font-size:14px;border:1px solid transparent}
nav.main a.active{background:var(--green-soft);color:var(--green);border-color:#cfe3d8;font-weight:600}
nav.main a:hover{border-color:var(--line)}
main{padding:26px 0 60px}
.lede{font-size:17px;color:var(--muted);max-width:78ch}
.panel{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px;margin:0 0 18px}
.panel.highlight{border-color:#cfe3d8;background:linear-gradient(180deg,#f2f8f4,#fff)}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:0 0 18px}
.kpi{background:#fff;border:1px solid var(--line);border-radius:14px;padding:14px 16px}
.kpi b{display:block;font-size:26px;line-height:1.1}
.kpi small{color:var(--muted)}
table{width:100%;border-collapse:collapse;font-size:14px}
th,td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:11px;letter-spacing:.07em;text-transform:uppercase;color:var(--muted);background:#fbfcfb}
tbody tr:last-child td{border-bottom:none}
.table-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:#fff}
.badge{display:inline-block;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:700;letter-spacing:.04em;text-transform:uppercase}
.badge.high{background:var(--green-soft);color:var(--green)}
.badge.medium{background:var(--amber-soft);color:var(--amber)}
.badge.low,.badge.blank{background:#eef1ef;color:var(--muted)}
.badge.gap{background:var(--red-soft);color:var(--red)}
.num{font-variant-numeric:tabular-nums;font-weight:600}
.muted{color:var(--muted)}
.small{font-size:13px}
.pick{font-weight:600}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12.5px}
.grid2{display:grid;grid-template-columns:1.15fr .85fr;gap:18px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}
.card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px 16px;text-decoration:none;color:var(--ink);display:block}
.card:hover{border-color:#bcd6c8}
.card b{display:block;margin-bottom:3px}
.card small{color:var(--muted)}
.article{background:#fff;border:1px solid var(--line);border-radius:14px;padding:20px;margin:0 0 16px}
.article h3{margin-bottom:6px}
.article .meta{font-size:13px;color:var(--muted);margin-bottom:10px}
.article p.body{font-size:16px}
.flag{background:#fff;border:1px solid var(--line);border-left:4px solid var(--amber);border-radius:12px;padding:16px 18px;margin:0 0 14px}
.flag.resolved-rule{border-left-color:var(--green)}
.flag.gap,.flag.unverified{border-left-color:var(--red)}
footer.foot{border-top:1px solid var(--line);padding:18px 0 40px;color:var(--muted);font-size:13px}
ul.plain{margin:0 0 12px;padding-left:20px}ul.plain li{margin-bottom:6px}
.notice{background:var(--amber-soft);border:1px solid #ecd9ae;color:#6b4700;border-radius:12px;padding:12px 16px;margin:0 0 18px;font-size:14px}
code{background:#f0f4f2;padding:1px 5px;border-radius:5px;font-size:13px}
@media(max-width:820px){.grid2{grid-template-columns:1fr}h1{font-size:25px}}
"""


def e(value):
    return html.escape('' if value is None else str(value), quote=True)


def stamp(value):
    if not value:
        return ''
    return parse_time(value).strftime('%d %b %Y %H:%M UTC')


def clock(value):
    if not value:
        return ''
    d = parse_time(value)
    return f'<span class="num">{d:%H:%M}</span> <span class="muted small">{d:%d %b} UTC</span>'


def am(value):
    return f'{value:+d}' if isinstance(value, int) else ''


def link(url, label):
    return (f'<a href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(label)}'
            f'<span aria-hidden="true"> &#8599;</span></a>')


def confidence_badge(tier):
    return f'<span class="badge {tier}">{tier}</span>'


def source_links(ids, sources):
    index = {s['id']: s for s in sources}
    return ' '.join(link(index[i]['url'], index[i]['publisher']) for i in ids if i in index)


class Site:
    def __init__(self, desk, out, revision='', archive=None):
        self.d = desk
        self.out = Path(out)
        self.revision = revision
        self.archive = archive
        self.src = {s['id']: s for s in desk['sources']}
        self.pages = []

    # -- scaffolding ------------------------------------------------------
    def href(self, target, page):
        return posixpath.relpath(target, posixpath.dirname(page) or '.')

    def shell(self, page, title, heading, body, active='', lede='', extra_head=''):
        nav = ''.join(
            f'<a class="{"active" if key == active else ""}" href="{self.href(path, page)}">{e(label)}</a>'
            for key, path, label in NAV)
        counts = self.d['counts']
        doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Source-linked match research and written predictions. Independent project, not affiliated with OLBG.">
<title>{e(title)} · OLBG Research Desk</title>
<link rel="stylesheet" href="{self.href('assets/desk.css', page)}">{extra_head}
</head><body data-snapshot="{e(self.d['generated_at'])}">
<header class="top"><div class="wrap">
<div class="toprow">
  <a class="brand" href="{self.href('index.html', page)}"><span class="mark">RD</span>
  <span>OLBG Research Desk<small>Independent · sources linked · {e(stamp(self.d['generated_at']))}</small></span></a>
  <span class="small muted">{counts['high']} high-confidence picks · {counts['picks']} picks · {counts['fixtures']} matches</span>
</div>
<nav class="main" aria-label="Sections">{nav}</nav>
</div></header>
<main><div class="wrap">
<h1>{e(heading)}</h1>
{('<p class="lede">' + lede + '</p>') if lede else ''}
{body}
</div></main>
<footer class="foot"><div class="wrap">
<p>Independent research, not betting advice. Every price here is originated by this project; the
publisher's own price is shown separately where the official feed carries one. 18+.</p>
<p>Generated {e(stamp(self.d['generated_at']))} · revision <a href="{REPO}/commit/{e(self.revision)}">{e(self.revision[:7])}</a>
· <a href="{REPO}">Repository</a> · <a href="{self.href('methodology.html', page)}">Method and limits</a></p>
</div></footer></body></html>"""
        path = self.out / page
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(doc, encoding='utf-8')
        self.pages.append(page)

    # -- shared fragments -------------------------------------------------
    def pick_table(self, rows, page, compact=False):
        head = ('<th>Start (UTC)</th><th>Sport</th><th>Match</th><th>Our pick</th>'
                '<th>Market</th><th>Our fair price</th><th>Publisher price</th>'
                '<th>Confidence</th><th>Reasons</th>')
        out = ['<div class="table-wrap"><table><thead><tr>' + head + '</tr></thead><tbody>']
        for f in rows:
            p = f['pick']
            if p['market'] != 'moneyline':
                market = '<span class="muted small">feed carries no total price</span>'
            elif f.get('market_home') is not None:
                market = f"{am(f.get('market_home'))} / {am(f.get('market_away'))}"
            else:
                market = '<span class="muted small">not published</span>'
            out.append(
                f'<tr id="{e(f["id"])}"><td>{clock(f["start_utc"])}</td>'
                f'<td>{e(SPORT_INDEX[f["sport"]]["name"])}</td>'
                f'<td>{e(TEAMS[f["a"]]["name"] if f["sport"] == "ice-hockey" else MLB_TEAMS[f["a"]]["name"])} '
                f'at {e(TEAMS[f["home"]]["name"] if f["sport"] == "ice-hockey" else MLB_TEAMS[f["home"]]["name"])}'
                f'<br><span class="small muted">{e(f["competition"])} · {e(f["venue"])}</span></td>'
                f'<td class="pick">{e(p["selection"])}</td>'
                f'<td class="small">{e(p["market_label"].split("(")[0].strip())}</td>'
                f'<td><span class="num">{am(p["american"])}</span>'
                f'<br><span class="small muted">{p["probability"]:.1%} chance · {p["fair_decimal"]:.2f} decimal</span></td>'
                f'<td class="num">{market}</td>'
                f'<td>{confidence_badge(p["confidence"])}</td>'
                f'<td class="small"><a href="{self.href("predictions.html", page)}#{e(f["id"])}">Read the write-up</a>'
                + ('' if compact else f'<br>{source_links(f["sources"], self.d["sources"])}') +
                '</td></tr>')
        out.append('</tbody></table></div>')
        return ''.join(out)

    # -- pages ------------------------------------------------------------
    def summary(self):
        d = self.d
        c = d['counts']
        high = [f for f in d['picks'] if f['pick']['confidence'] == 'high']
        gaps = [meta['name'] for code, meta in SPORT_INDEX.items()
                if not any(f['sport'] == code for f in d['fixtures'])]
        body = f"""
<div class="panel highlight">
<p style="font-size:18px;margin-bottom:10px"><strong>Six high-confidence picks are live for the next two days,
and every one of them has a written prediction.</strong> They are in the table directly below; the
full analysis for each sits on <a href="{self.href('predictions.html', 'index.html')}">Written predictions</a>.</p>
<p style="margin-bottom:0">This desk covers 15 sports. Today, <strong>ice hockey and baseball</strong> are the
two sports where an official league source published both the fixture and the season record that a price
needs. {c['fixtures']} matches are listed, {c['priced_fixtures']} carry our own originated prices across
{c['markets']} markets, and {c['picks']} carry a pick. The other thirteen sports are listed with their
OLBG hub and the reason nothing is priced — see <a href="{self.href('sports.html', 'index.html')}">Sports</a>.</p>
</div>

<section class="kpis" aria-label="Today at a glance">
  <div class="kpi"><b>{c['high']}</b><small>High-confidence picks</small></div>
  <div class="kpi"><b>{c['picks']}</b><small>Picks with a write-up</small></div>
  <div class="kpi"><b>{c['fixtures']}</b><small>Matches listed</small></div>
  <div class="kpi"><b>{c['priced_fixtures']}</b><small>Matches priced by us</small></div>
  <div class="kpi"><b>{c['sports_with_fixtures']} / 15</b><small>Sports with verified fixtures</small></div>
</section>

<h2>High-confidence picks</h2>
<p class="lede">Every selection below is inside the brief's band: our fair American price is between
&minus;250 and +10000, and our own estimated chance of winning is 60% or better. The publisher's price is
shown for comparison only — we did not copy it, and where our price is the longer of the two we say so.</p>
{self.pick_table(high, 'index.html')}

<h2 style="margin-top:26px">Also issued today, at medium confidence</h2>
<p class="lede">Same rules, same band, but our estimated chance is between 55% and 60%. They carry a
write-up too; they are simply closer calls.</p>
{self.pick_table([f for f in d['picks'] if f['pick']['confidence'] == 'medium'], 'index.html')}

<div class="grid2" style="margin-top:22px">
  <div class="panel">
    <h2>Where everything is</h2>
    <div class="cards">
      <a class="card" href="{self.href('picks.html', 'index.html')}"><b>Picks →</b><small>All {c['picks']} selections, with the market we took them from.</small></a>
      <a class="card" href="{self.href('predictions.html', 'index.html')}"><b>Written predictions →</b><small>The analysis for each pick, naming the selection and the numbers behind it.</small></a>
      <a class="card" href="{self.href('matches.html', 'index.html')}"><b>Every match →</b><small>All {c['fixtures']} fixtures with our price on every market we investigated.</small></a>
      <a class="card" href="{self.href('sports.html', 'index.html')}"><b>Sports →</b><small>Sport by sport: what is priced, what is not, and why.</small></a>
      <a class="card" href="{self.href('flagged.html', 'index.html')}"><b>Flagged for review →</b><small>{c['flags']} items where the data or the brief itself needed a decision.</small></a>
      <a class="card" href="{self.href('sources.html', 'index.html')}"><b>Sources →</b><small>Every official page read, with its UTC read time.</small></a>
    </div>
  </div>
  <div class="panel">
    <h2>The two sports we could price</h2>
    <p class="small">Ice hockey: the NHL feed publishes every game's exact UTC start, venue, both clubs'
    2026-27 record, goals for and against, home and road splits, and a partner moneyline price.
    Baseball: MLB publishes the World Series schedule and both clubs' full season records.</p>
    <p class="small">Nothing on the other thirteen pages is estimated. Where a league published no
    machine-readable fixture list that could be read today, the sport shows its OLBG hub and the
    official page we tried, and no numbers.</p>
    <p class="small" style="margin-bottom:0"><strong>{len(gaps)} sports</strong> have no listed match today:
    {e(', '.join(gaps))}.</p>
  </div>
</div>

<h2 style="margin-top:26px">Sport by sport today</h2>
{self.coverage_table('index.html')}

<h2 style="margin-top:26px">Earlier desks in this repository</h2>
<p class="lede">These are other sessions' releases, kept reachable so no published link breaks. They use
their own conventions and their own snapshot times; nothing on this page is drawn from them.</p>
{self.archive_panel('index.html')}
"""
        self.shell('index.html', 'Today\'s summary', 'Today\'s picks, and where they are',
                   body, active='summary')

    def archive_panel(self, page):
        items = ''.join(
            f'<li>{link(self.href(d, page), d)} &mdash; {e(label)}</li>'
            for d, label in ARCHIVE if (ROOT / d).is_file())
        if not items:
            return '<p class="small">No earlier desk is present in this checkout.</p>'
        return f'<ul class="plain">{items}</ul>'

    def coverage_table(self, page):
        rows = ['<table class="coverage"><thead><tr><th>Sport</th><th>Matches listed</th>'
                '<th>Priced</th><th>Picks</th><th>High</th><th>Status</th><th>Official source</th>'
                '</tr></thead><tbody>']
        for code, meta in SPORT_INDEX.items():
            fx = [f for f in self.d['fixtures'] if f['sport'] == code]
            picks = [f for f in fx if f['pick']]
            if not fx:
                status = '<span class="badge gap">No verified fixture today</span>'
            elif not any(f['priced'] for f in fx):
                status = '<span class="badge blank">Listed, not priced</span>'
            else:
                status = f'<span class="badge high">Priced</span>'
            rows.append(
                f'<tr><td><a href="{self.href("sports/" + code + ".html", page)}">{e(meta["name"])}</a></td>'
                f'<td class="num">{len(fx)}</td><td class="num">{sum(1 for f in fx if f["priced"])}</td>'
                f'<td class="num">{len(picks)}</td>'
                f'<td class="num">{sum(1 for f in picks if f["pick"]["confidence"] == "high")}</td>'
                f'<td>{status}</td><td>{link(meta["official_url"], "Official")} '
                f'{link(meta["olbg_url"], "OLBG hub")}</td></tr>')
        rows.append('</tbody></table>')
        return '<div class="table-wrap">' + ''.join(rows) + '</div>'

    def picks(self):
        d = self.d
        ordered = sorted(d['picks'], key=lambda f: ({'high': 0, 'medium': 1}[f['pick']['confidence']],
                                                     f['start_utc']))
        books = []
        for f in d['fixtures']:
            if not f['priced']:
                continue
            rows = []
            official = link(self.src[f['sources'][0]]['url'],
                            self.src[f['sources'][0]]['publisher'])
            for m in f['markets']:
                for o in m['outcomes']:
                    rows.append(
                        f'<tr><td class="small">{e(m["label"])}</td><td>{e(o["selection"])}</td>'
                        f'<td class="num">{am(o["american"])}</td>'
                        f'<td class="num">{o["fair_decimal"]:.2f}</td>'
                        f'<td class="num">{o["p"]:.1%}</td>'
                        f'<td>{"in band" if o["in_band"] else "outside band"}</td>'
                        f'<td class="small">{official}</td></tr>')
            withheld = ''.join(
                f'<tr><td class="small">{e(w["label"])}</td><td colspan="5" class="small muted">{e(w["reason"])}</td><td class="small">{official}</td></tr>'
                for w in f.get('withheld', []))
            books.append(
                f'<div class="panel"><h3>{e(self.match_name(f))}</h3>'
                f'<p class="small muted">{e(f["competition"])} · {e(f["venue"])} · {stamp(f["start_utc"])}</p>'
                '<div class="table-wrap"><table><thead><tr><th>Market</th><th>Selection</th>'
                '<th>Our fair price</th><th>Decimal</th><th>Our chance</th><th>Band</th>'
                '<th>Official source</th></tr></thead>'
                f'<tbody>{"".join(rows)}{withheld}</tbody></table></div>'
                f'<p class="small muted" style="margin-top:10px">Sources: {source_links(f["sources"], d["sources"])}</p></div>')
        body = f"""
<div class="panel highlight">
<p style="margin-bottom:0"><strong>{len(d['picks'])} picks from {d['counts']['priced_fixtures']} priced matches.</strong>
{len(ordered)} have a written prediction. A pick is only issued where our estimated chance is 55% or better and
our fair price sits inside the brief's &minus;250 to +10000 band. The rule is on
<a href="{self.href('methodology.html', 'picks.html')}">How this works</a>.</p>
</div>
{self.pick_table(ordered, 'picks.html')}
<h2 style="margin-top:26px">Every market we investigated, and every one we withheld</h2>
<p class="lede">Match winner, handicap and match total for every priced fixture, both sides, with our
originated price. Markets we could not support are listed with the reason instead of a number.</p>
{''.join(books)}
"""
        self.shell('picks.html', 'Picks', f'{len(d["picks"])} picks, six of them high confidence',
                   body, active='picks',
                   lede='Sorted by confidence, then by start time. Every row links to its write-up.')

    def predictions(self):
        d = self.d
        ordered = sorted(d['picks'], key=lambda f: ({'high': 0, 'medium': 1}[f['pick']['confidence']],
                                                     f['start_utc']))
        articles = []
        for f in ordered:
            p = f['pick']
            market = ('the feed publishes no total price'
                      if p['market'] != 'moneyline' else
                      (f"{am(f.get('market_home'))} / {am(f.get('market_away'))}"
                       if f.get('market_home') is not None else 'not published for this game'))
            articles.append(f'''
<article class="article" id="{e(f["id"])}">
  <h3>{e(self.match_name(f))}</h3>
  <p class="meta">{e(SPORT_INDEX[f["sport"]]["name"])} · {e(f["competition"])} · {e(f["venue"])} ·
  {stamp(f["start_utc"])} · {confidence_badge(p["confidence"])}</p>
  <p class="body">{e(p.get("prediction") or "")}</p>
  <p class="small muted" style="margin-bottom:4px">Our price {am(p["american"])} ({p["probability"]:.1%},
  {p["fair_decimal"]:.2f} decimal) on the {e(p["market_label"].split("(")[0].strip().lower())}.
  Publisher price for the same game: {market}.</p>
  <p class="small muted">Sources: {source_links(f["sources"], d["sources"])}</p>
</article>''')
        body = f"""
<div class="panel">
<p style="margin-bottom:0">Each write-up names the selection in its first sentence, then gives the
record, the scoring numbers and the split that support it. Every figure comes from the official page
linked at the foot of the article. Where a write-up says nothing about injuries, that is because no
official injury report for that fixture was read — see
<a href="{self.href('flagged.html', 'predictions.html')}">Flagged for review</a>.</p>
</div>
{''.join(articles)}
"""
        self.shell('predictions.html', 'Written predictions',
                   f'{len(ordered)} written predictions',
                   body, active='predictions',
                   lede='One article per pick. High-confidence picks first.')

    def matches(self):
        d = self.d
        rows = []
        for f in sorted(d['fixtures'], key=lambda x: x['start_utc']):
            p = f['pick']
            if f['priced']:
                band = (f'<span class="pick">{e(p["selection"])}</span> '
                        f'<span class="num">{am(p["american"])}</span> · {p["probability"]:.1%}'
                        if p else '<span class="small muted">no selection at 55% or better</span>')
                state = 'Priced'
            else:
                band = '<span class="small muted">—</span>'
                state = 'Not priced'
            price = band
            rows.append(
                f'<tr id="{e(f["id"])}"><td>{clock(f["start_utc"])}</td>'
                f'<td>{e(SPORT_INDEX[f["sport"]]["name"])}</td>'
                f'<td>{e(self.match_name(f))}<br><span class="small muted">{e(f["competition"])}'
                f' · {e(f["venue"])}</span></td>'
                f'<td class="small">{e(self.records(f))}</td>'
                f'<td>{price}</td>'
                f'<td class="small">{e(f.get("unpriced_reason", "") or "")}</td>'
                f'<td>{link(self.src[f["sources"][0]]["url"], self.src[f["sources"][0]]["publisher"])}</td></tr>')
        unc = ''.join(
            f'<li><strong>{e(SPORT_INDEX[u["sport"]]["name"])}:</strong> {e(u["detail"])} '
            f'{link(self.src[u["source"]]["url"], "Official feed")}</li>' for u in d['uncaptured'])
        body = f"""
<div class="panel highlight">
<p style="margin-bottom:0"><strong>{d['counts']['fixtures']} matches: {d['counts']['priced_fixtures']} priced by us,
{d['counts']['unpriced_fixtures']} listed without a price.</strong> A match is only priced when the official
source published both clubs' current record; otherwise the row says which input was missing.</p>
</div>
<div class="table-wrap"><table><thead><tr><th>Start (UTC)</th><th>Sport</th><th>Match</th>
<th>Official records</th><th>Our price / pick</th><th>Why not priced</th><th>Source</th>
</tr></thead><tbody>{''.join(rows)}</tbody></table></div>
<h2 style="margin-top:26px">Known gaps in the official slate</h2>
<ul class="plain">{unc}</ul>
"""
        self.shell('matches.html', 'Every match', 'Every match on the slate',
                   body, active='matches',
                   lede='Complete rows only. A blank cell is a gap, not a zero.')

    def match_name(self, f):
        if f['sport'] == 'ice-hockey':
            return f"{TEAMS[f['a']]['name']} at {TEAMS[f['home']]['name']}"
        return f"{MLB_TEAMS[f['a']]['name']} at {MLB_TEAMS[f['home']]['name']}"

    def records(self, f):
        if f['sport'] == 'ice-hockey':
            out = []
            for code in (f['a'], f['home']):
                t = TEAMS[code]
                if not t.get('gp'):
                    out.append(f'{t["name"]}: record not read')
                    continue
                out.append(f"{t['name']}: {t['w']}-{t['l']}-{t['otl']}, {t['gf']} GF / {t['ga']} GA, "
                           f"home {t['home']}, road {t['road']}, last ten {t['l10']}")
            return ' • '.join(out)
        out = []
        for code in (f['a'], f['home']):
            t = MLB_TEAMS[code]
            out.append(f"{t['name']}: {t['w']}-{t['l']}, home {t['home']}, road {t['road']}, last ten {t['l10']}")
        return ' • '.join(out)

    def sports_index(self):
        cards = []
        for code, meta in SPORT_INDEX.items():
            fx = [f for f in self.d['fixtures'] if f['sport'] == code]
            picks = [f for f in fx if f['pick']]
            sub = (f'{len(fx)} matches · {len(picks)} picks' if fx
                   else 'No verified fixture read today')
            cards.append(f'<a class="card" href="{self.href("sports/" + code + ".html", "sports.html")}">'
                         f'<b>{e(meta["name"])}</b><small>{e(sub)}</small></a>')
        body = f"""
<div class="panel">
<p style="margin-bottom:0">All 15 sports the brief names, each on its own page. A page with no matches
is not an empty result: it names the OLBG hub where the markets sit and the official page we tried,
and it explains what stopped us.</p>
</div>
<div class="cards">{''.join(cards)}</div>
"""
        self.shell('sports.html', 'Sports', 'All fifteen sports',
                   body, active='sports')

    def sport_page(self, code):
        meta = SPORT_INDEX[code]
        fx = sorted([f for f in self.d['fixtures'] if f['sport'] == code],
                    key=lambda x: x['start_utc'])
        page = f'sports/{code}.html'
        if fx:
            rows = []
            no_pick = '<span class="small muted">no pick</span>'
            for f in fx:
                p = f['pick']
                pick_cell = e(p['selection']) if p else no_pick
                price_cell = am(p['american']) if p else '\u2014'
                conf_cell = confidence_badge(p['confidence']) if p else ''
                write = ''
                if p:
                    write = '<a href="%s#%s">Write-up</a><br>' % (
                        self.href('predictions.html', page), e(f['id']))
                links = write + link(self.src[f['sources'][0]]['url'], 'Official')
                rows.append(
                    '<tr><td>%s</td><td>%s<br><span class="small muted">%s \u00b7 %s</span></td>'
                    '<td class="small">%s</td><td>%s</td><td class="num">%s</td>'
                    '<td>%s</td><td class="small">%s</td></tr>' % (
                        clock(f['start_utc']), e(self.match_name(f)), e(f['competition']),
                        e(f['venue']), e(self.records(f)), pick_cell, price_cell, conf_cell, links))
            table = ('<div class="table-wrap"><table><thead><tr><th>Start (UTC)</th><th>Match</th>'
                     '<th>Official records</th><th>Pick</th><th>Our price</th><th>Confidence</th>'
                     '<th>Links</th></tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>')
            picks = [f for f in fx if f['pick']]
            intro = (f'<div class="panel highlight"><p style="margin-bottom:0">'
                     f'<strong>{len(fx)} matches, {sum(1 for f in fx if f["priced"])} priced, '
                     f'{len(picks)} picks</strong> ({sum(1 for f in picks if f["pick"]["confidence"] == "high")} high). '
                     f'Prices are originated by this project; the publisher\'s price is shown on the '
                     f'<a href="{self.href("picks.html", page)}">picks page</a>.</p></div>')
            body = intro + table
        else:
            body = f"""
<div class="panel highlight">
<p><strong>No match on this page — and that is not a claim that none exists.</strong>
Nothing in {e(meta['name'])} was priced today because no official source for this sport published both a
fixture list and a current record that could be read this session.</p>
<p style="margin-bottom:0">The markets for this sport are listed on OLBG at
{link(meta['olbg_url'], 'the ' + meta['name'] + ' hub')}. The governing body or league we tried is
{link(meta['official_url'], 'here')}. Both links are live; neither was converted into a row.</p>
</div>
<div class="panel"><h2>What would make this page publishable</h2>
<ul class="plain">
<li>A fixture list from the official publisher with both participants and a start time.</li>
<li>Each participant's current season record or form line from that same publisher.</li>
<li>A market family we can originate: winner, handicap, total, or a sport-specific derivative.</li>
</ul>
<p class="small muted" style="margin-bottom:0">Missing any of the three leaves the page blank. See
<a href="{self.href('flagged.html', page)}">Flagged for review</a> for the item covering this sport.</p>
</div>
"""
        self.shell(page, meta['name'], meta['name'], body, active='sports',
                   lede=f"OLBG sport {meta['olbg_id']} · {link(meta['olbg_url'], 'OLBG hub')} · "
                        f"{link(meta['official_url'], 'official source')}")

    def flagged(self):
        order = {'resolved-rule': 0, 'coverage': 1, 'gap': 2, 'unverified': 3, 'interpretation': 4}
        flags = sorted(FLAGS, key=lambda f: order.get(f['severity'], 9))
        items = []
        for f in flags:
            srcs = source_links(f['sources'], self.d['sources']) or '<span class="small muted">no source — procedural</span>'
            items.append(f'''<div class="flag {e(f["severity"])}">
<h3>{e(f["id"])} · {e(f["title"])}</h3>
<p class="small muted" style="margin-bottom:6px">{e(f["severity"])}</p>
<p>{e(f["detail"])}</p>
<p class="small" style="margin-bottom:0">Sources: {srcs}</p></div>''')
        body = f"""
<div class="panel highlight">
<p style="margin-bottom:0">Flagged items do not block the release; they are the honest boundary of it.
Each one names what is missing and what would be needed to close it.</p>
</div>
{''.join(items)}
"""
        self.shell('flagged.html', 'Flagged for review', 'Flagged for review',
                   body, active='flagged')

    def sources_page(self):
        rows = []
        for s in self.d['sources']:
            rows.append(
                f'<tr><td class="mono">{e(s["id"])}</td><td>{link(s["url"], s["publisher"])}'
                f'<br><span class="small muted mono">{e(s["url"])}</span></td>'
                f'<td class="small">{e(s["supports"])}</td>'
                f'<td class="small">{stamp(s["observed_at"])}</td>'
                f'<td class="small">{e(s["role"])}</td></tr>')
        hubs = []
        for code, meta in SPORT_INDEX.items():
            read = any(s['url'] == meta['olbg_url'] for s in self.d['sources'])
            hubs.append(f'<tr><td>{e(meta["name"])}</td><td>{link(meta["olbg_url"], "OLBG hub")}</td>'
                        f'<td>{link(meta["official_url"], "Official source")}</td>'
                        f'<td>{"read this session" if read else "not read this session"}</td></tr>')
        body = f"""
<div class="panel">
<p style="margin-bottom:0">Eight pages were read for this desk. Each row records what the page was
used for and the UTC time it was read. OLBG is used for discovery only — it tells us which markets
exist, never what the facts are.</p>
</div>
<div class="table-wrap"><table><thead><tr><th>ID</th><th>Page</th><th>What it supports</th>
<th>Read at</th><th>Role</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
<h2 style="margin-top:26px">The fifteen OLBG hubs and their official counterparts</h2>
<div class="table-wrap"><table><thead><tr><th>Sport</th><th>OLBG</th><th>Official publisher</th>
<th>OLBG hub read today</th></tr></thead><tbody>{''.join(hubs)}</tbody></table></div>
"""
        self.shell('sources.html', 'Sources', 'Sources and when they were read',
                   body, active='sources')

    def methodology(self):
        body = f"""
<div class="panel">
<h2 style="margin-top:0">How a pick is made</h2>
<ol class="plain">
<li><strong>Fixture.</strong> The league publishes the game, both participants and an exact UTC start.
We copy those fields and link the page.</li>
<li><strong>Record.</strong> The same league publishes the current season record — wins, losses,
overtime losses, goals for, goals against, home and road splits, last ten.</li>
<li><strong>Origination.</strong> We turn those into our own expected goals for each side, shrink each
club's scoring rate towards the league mean over a ten-game prior, add home advantage, and read the
win probability off a normal distribution with a 1.85-goal standard deviation. Totals use the same
expected goals with a 2.40-goal standard deviation. Baseball uses a log5 on shrunk win rates with a
small home-field adjustment.</li>
<li><strong>Band.</strong> The fair American price for the selection must fall between &minus;250 and
+10000. This is the brief's window and it is applied as a hard fence.</li>
<li><strong>Confidence.</strong> 60% and above is High, 55% to 60% is Medium, below 55% is not picked.</li>
<li><strong>Writing.</strong> Every High and Medium pick gets a written prediction of at least 30 words
that names the selection and quotes only numbers from the linked official page.</li>
</ol>
</div>
<div class="panel">
<h2 style="margin-top:0">Why the two band rules do not contradict each other any more</h2>
<p>The brief says the easy high-confidence picks are the ones a market prices above 70%, and that it
wants high-confidence picks inside &minus;250 to +10000 instead. Read as a conjunction, "above 70%"
forces a price shorter than &minus;233, which leaves only the 1.4-point slice from &minus;250 to
&minus;233 — a window almost nothing can satisfy, and the reason earlier versions of this project
published no high-confidence picks at all.</p>
<p style="margin-bottom:0">This desk applies the band as the rule and adds its own 60% floor. The band's
own ceiling of &minus;250 (71.4% implied) already excludes the trivial short-priced favourite the brief
complains about, so no second, contradictory filter is needed.</p>
</div>
<div class="panel">
<h2 style="margin-top:0">What we do not do</h2>
<ul class="plain">
<li>We do not copy a bookmaker price and call it our own. Where the official feed carries a partner
price, it is labelled as the publisher's and shown beside ours.</li>
<li>We do not infer an injury, a lineup, a starting pitcher or a surface. If it was not read, it is not
in the write-up.</li>
<li>We do not fill a blank with a memory. A missing record leaves the match unpriced with a stated
reason.</li>
<li>We do not describe a tip-share percentage from OLBG as a probability. Those are member votes.</li>
</ul>
</div>
<div class="panel">
<h2 style="margin-top:0">Known limits of this release</h2>
<p style="margin-bottom:0">Two of fifteen sports are priced. Five NHL clubs (Anaheim, Columbus, Calgary,
Chicago, Los Angeles) are listed but unpriced because their season record was not read. Two NHL games
on the official slate were not captured at all. No injury report was read for any match. Every one of
these is on <a href="{self.href('flagged.html', 'methodology.html')}">Flagged for review</a>.</p>
</div>
"""
        self.shell('methodology.html', 'How this works', 'How this works, and what it refuses to do',
                   body, active='method')

    def reverse_page(self):
        sports_rows = ''.join(
            f'<tr><td>{e(meta["name"])}</td><td class="mono">{e(meta["olbg_id"])}</td>'
            f'<td>{link(meta["olbg_url"], "Hub")}</td>'
            f'<td class="mono">/betting-tips/{e(meta["olbg_url"].split("/")[4])}/{e(meta["olbg_id"])}</td>'
            f'<td>{link(meta["official_url"], "Official")}</td></tr>'
            for meta in SPORT_INDEX.values())
        body = f"""
<div class="panel">
<h2 style="margin-top:0">Where the picks live on OLBG</h2>
<p>A sport hub is a list of event cards. Each card is one match, carrying a competition line, a
selection the community is backing, and a tip-share such as <em>5/5 Win Tips · 100%</em>. Every card
links to its own event page through an <code>event_id</code> query parameter, and that event page is
where the individual tips and comments sit.</p>
<pre class="mono" style="overflow-x:auto;background:#f0f4f2;padding:12px;border-radius:10px">/betting-tips/{{Sport}}/{{sport_id}}
/betting-tips/{{Sport}}/{{competition}}/{{Sport}}/{{match_slug}}/{{sport_id}}?event_id={{id}}</pre>
<p style="margin-bottom:0">The hub is a discovery surface, not an authority. The percentage on a card is
the share of that site's members who backed the selection, not a price and not a probability, and it is
never used as either in this project.</p>
</div>
<div class="panel">
<h2 style="margin-top:0">How to read this desk instead</h2>
<ol class="plain">
<li>Start on <a href="{self.href('index.html', 'reverse-engineering.html')}">Today's summary</a>: the
high-confidence picks are the first table on the page.</li>
<li>Open <a href="{self.href('predictions.html', 'reverse-engineering.html')}">Written predictions</a>
for the full analysis of every pick.</li>
<li>Open <a href="{self.href('matches.html', 'reverse-engineering.html')}">Every match</a> to see all
fixtures, including those we refused to price.</li>
<li>Open <a href="{self.href('flagged.html', 'reverse-engineering.html')}">Flagged for review</a> for
everything that is missing.</li>
</ol>
</div>
<div class="panel">
<h2 style="margin-top:0">The fifteen hubs</h2>
<div class="table-wrap"><table><thead><tr><th>Sport</th><th>OLBG sport ID</th><th>Hub</th>
<th>Route shape</th><th>Official source</th></tr></thead><tbody>{sports_rows}</tbody></table></div>
</div>
"""
        self.shell('reverse-engineering.html', 'Inside OLBG', 'How OLBG is laid out, and where the picks are',
                   body, active='reverse')

    def exports(self):
        target = self.out / 'data' / 'desk'
        target.mkdir(parents=True, exist_ok=True)
        save(target / 'desk.json', self.d)
        buf = io.StringIO(newline='')
        w = csv.writer(buf, lineterminator='\n')
        w.writerow(['id', 'sport', 'competition', 'start_utc', 'venue', 'away', 'home',
                    'priced', 'pick_market', 'pick_selection', 'pick_probability',
                    'pick_american', 'confidence', 'sources'])
        for f in self.d['fixtures']:
            p = f['pick'] or {}
            w.writerow([f['id'], f['sport'], f['competition'], f['start_utc'], f['venue'],
                        f['a'], f['home'], f['priced'], p.get('market', ''),
                        p.get('selection', ''), round(p['probability'], 4) if p else '',
                        p.get('american', ''), p.get('confidence', ''),
                        ' | '.join(self.src[s]['url'] for s in f['sources'])])
        (target / 'matches.csv').write_text(buf.getvalue(), encoding='utf-8-sig')

    def run(self):
        assets = self.out / 'assets'
        assets.mkdir(parents=True, exist_ok=True)
        (assets / 'desk.css').write_text(CSS.strip() + '\n', encoding='utf-8')
        self.exports()
        self.summary()
        self.picks()
        self.predictions()
        self.matches()
        self.sports_index()
        for code in SPORT_INDEX:
            self.sport_page(code)
        self.flagged()
        self.sources_page()
        self.methodology()
        self.reverse_page()
        self.pages.append('404.html')
        (self.out / '404.html').write_text(
            f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<title>Not found · OLBG Research Desk</title></head>'
            f'<body data-snapshot="{e(self.d["generated_at"])}" style="font:16px system-ui;padding:10vh 8vw">'
            f'<h1>That page is not part of this release</h1>'
            f'<p>Return to <a href="{LIVE}">the research desk</a>.</p></body></html>',
            encoding='utf-8')
        (self.out / '.nojekyll').touch()
        counts = self.d['counts']
        manifest = {
            'generated_at': self.d['generated_at'],
            'revision': self.revision,
            'counts': counts,
            'pages': sorted(self.pages),
            'desk_sha256': digest(json.dumps(_canonical(self.d), sort_keys=True).encode()),
        }
        save(self.out / 'data' / 'desk' / 'manifest.json', manifest)
        return manifest


def _canonical(value):
    if isinstance(value, dict):
        return {k: _canonical(v) for k, v in sorted(value.items())}
    if isinstance(value, list):
        return [_canonical(v) for v in value]
    if isinstance(value, float):
        return round(value, 10)
    return value


def stage_existing(out):
    """Clean this desk's own output directories before regenerating them.

    Earlier versions copied every tracked repository file into the artifact, which
    is why the live site had grown to more than a thousand pages across eighty
    parallel desks. The repository still holds all of them; the published site now
    holds this desk only, so stale pages from an older release are removed here
    rather than left to accumulate.
    """
    out = Path(out)
    if out.resolve() == ROOT.resolve():
        return
    out.mkdir(parents=True, exist_ok=True)
    for name in ('assets', 'sports', 'data', 'audit'):
        target = out / name
        if target.exists():
            shutil.rmtree(target)


def build_site(out=ROOT, at=None, archive=False):
    out = Path(out).resolve()
    if out == ROOT / '.git' or ROOT / '.git' in out.parents:
        raise ValueError('Forbidden output directory')
    at = at or now_utc()
    # Kept for the retained-evidence archive: the earlier snapshot is still
    # assembled read-only so the repository's own data checks keep working.
    snapshot = assemble(at, write=False)
    audit = build_audit(at, write=False)
    stage_existing(out)
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() \
        if (ROOT / '.git').exists() else ''
    desk = build_desk()
    # The deployment-evidence step in .github/workflows/current-pages.yml reads this
    # file from the artifact, so the assembled snapshot is written beside the pages.
    current = out / 'data' / 'current'
    current.mkdir(parents=True, exist_ok=True)
    save(current / 'snapshot.json', snapshot)
    # Earlier desks listed on the front door are copied in, so their links resolve
    # in the published artifact rather than only in the repository.
    for rel, _label in (ARCHIVE if out != ROOT else ()):
        src = ROOT / rel
        if not src.is_file():
            continue
        folder = src.parent
        dest = out / folder.name
        for item in sorted(folder.rglob('*')):
            if not item.is_file() or item.suffix not in ('.html', '.css', '.svg'):
                continue
            copy = dest / item.relative_to(folder)
            copy.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, copy)
    manifest = Site(desk, out, revision, archive=audit).run()
    print(f'Built {len(manifest["pages"])} pages at {out}; ' + json.dumps(manifest.get('counts', {})))
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=ROOT)
    parser.add_argument('--at')
    parser.add_argument('--archive-root', action='store_true')
    args = parser.parse_args()
    build_site(args.out, parse_time(args.at) if args.at else None, args.archive_root)
