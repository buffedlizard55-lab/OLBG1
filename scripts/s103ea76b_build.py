"""Static dashboard for the 26 October 2026 fifteen-sport desk.

Every table that carries a data row also carries a link to the official page the
row's numbers came from. Nothing is rendered that is not in data/103ea76b.
"""
from __future__ import annotations

import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESK = ROOT / 'data' / '103ea76b' / 'desk.json'
OUT = ROOT / '103ea76b'

CONF_LABEL = {'high': 'High', 'medium': 'Medium', 'low': 'Low'}
CONF_CLASS = {'high': 'hi', 'medium': 'md', 'low': 'lo'}


def e(value):
    return html.escape(str(value), quote=True)


def am(v):
    return f'+{v}' if v > 0 else str(v)


class Site:
    def __init__(self, desk):
        self.d = desk
        self.fixtures = {f['id']: f for f in desk['fixtures']}
        self.sources = {s['id']: s for s in desk['sources']}
        self.picks = [self.fixtures[i] for i in desk['picks_sort']]
        self.pages = []
        self.prefix = ''

    # -- helpers ---------------------------------------------------------
    def href(self, target):
        return self.prefix + target

    def src_link(self, sid, label=None):
        s = self.sources[sid]
        text = label or s['publisher']
        return (f'<a class="src" href="{e(s["url"])}" target="_blank" rel="noopener noreferrer">{e(text)}</a>')

    def src_cell(self, ids, only_official=False):
        parts = []
        for sid in ids:
            s = self.sources[sid]
            if only_official and s['role'] != 'official':
                continue
            parts.append(self.src_link(sid))
        return '<span class="srcs">' + ' · '.join(parts) + '</span>'

    def shell(self, page, title, heading, body, lede=''):
        self.prefix = '../' * page.count('/')
        nav = [('index.html', 'Summary'), ('picks.html', 'Picks'), ('predictions.html', 'Predictions'),
               ('matches.html', 'Matches'), ('markets.html', 'Markets'), ('sports.html', 'Sports'),
               ('sources.html', 'Sources'), ('flagged.html', 'Flagged'), ('audit.html', 'Repo audit'),
               ('methodology.html', 'Method')]
        links = ''.join(f'<a href="{self.href(h)}">{e(t)}</a>' for h, t in nav)
        c = dict(self.d['counts'])
        c.update(self.d.get('extras', {}))
        strip = (f'<span><b>{c["picks"]}</b> picks</span><span><b>{c["high"]}</b> High</span>'
                 f'<span><b>{c["medium"]}</b> Medium</span><span><b>{c["sports_with_olbg_capture"]}</b> sports captured</span>'
                 f'<span><b>{c["priced_fixtures"]}</b> priced fixtures</span><span><b>{c["flags"]}</b> flagged</span>')
        doc = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><link rel="stylesheet" href="{self.href('assets/desk.css')}"></head>
<body data-snapshot="{e(self.d['generated_at'])}">
<header class="top"><div class="wrap">
<div class="brand"><a href="{self.href('index.html')}">OLBG research desk</a><span class="date">26 October 2026</span></div>
<nav>{links}</nav></div></header>
<main class="wrap">
<div class="strip">{strip}</div>
<h1>{e(heading)}</h1>
{lede}
{body}
</main>
<footer class="wrap"><p>Independent research. Not affiliated with OLBG. Prices are originated here, not quoted from a bookmaker.
Every number links to the official page it came from; blanks mean the official page did not publish it.
Generated {e(self.d['generated_at'])}.</p></footer>
</body></html>
'''
        path = OUT / page
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(doc, encoding='utf-8')
        self.pages.append(page)

    def pick_rows(self, rows, with_sport=True, compact=False):
        out = []
        for f in rows:
            p = f['pick']
            sport = self.d['sport_order'].index(f['sport'])
            name = self.sport_name(f['sport'])
            out.append(
                '<tr>'
                + (f'<td><a href="{self.href("sports/" + f["sport"] + ".html")}">{e(name)}</a></td>' if with_sport else '')
                + f'<td><a href="{self.href("predictions.html#" + f["id"])}"><b>{e(f["away"])} at {e(f["home"])}</b></a>'
                  f'<div class="sub">{e(f["competition"])}</div></td>'
                + f'<td>{e(p["market_label"])}</td>'
                + f'<td><b>{e(p["selection"])}</b></td>'
                + f'<td class="num">{am(p["american"])}</td>'
                + f'<td class="num">{p["probability"] * 100:.1f}%</td>'
                + f'<td><span class="badge {CONF_CLASS[p["confidence"]]}">{CONF_LABEL[p["confidence"]]}</span></td>'
                + ('' if compact else f'<td><a href="{self.href("predictions.html#" + f["id"])}">Read the pick</a></td>')
                + f'<td>{self.src_cell([s for s in f["sources"] if self.sources[s]["role"] == "official"])}</td>'
                '</tr>')
        return ''.join(out)

    def pick_table(self, rows, with_sport=True, compact=False):
        head = ('<tr>' + ('<th>Sport</th>' if with_sport else '') +
                '<th>Match</th><th>Market</th><th>Selection</th><th>Price</th><th>Chance</th><th>Grade</th>' +
                ('' if compact else '<th>Write-up</th>') + '<th>Official source</th></tr>')
        return f'<div class="scroll"><table class="t">{head}{self.pick_rows(rows, with_sport, compact)}</table></div>'

    def sport_name(self, code):
        for s in self.d['sports']:
            if s['code'] == code:
                return s['name']
        return code

    def sport_hub(self, code):
        for s in self.d['sports']:
            if s['code'] == code:
                return s['official_hub'], s['olbg_url']
        return None, None

    # -- pages -----------------------------------------------------------
    def index(self):
        c = self.d['counts']
        x = self.d['extras']
        high = [f for f in self.picks if f['pick']['confidence'] == 'high']
        med = [f for f in self.picks if f['pick']['confidence'] == 'medium']
        with_picks = sorted({f['sport'] for f in self.picks}, key=self.d['sport_order'].index)
        without = [s for s in self.d['sport_order'] if s not in with_picks]
        cards = ''.join(
            f'<a class="card" href="{self.href("sports/" + code + ".html")}">'
            f'<div class="k">{e(self.sport_name(code))}</div>'
            f'<div class="v">{sum(1 for f in self.picks if f["sport"] == code)} picks</div>'
            f'<div class="s">{sum(len(x["rows"]) for x in self.d["listings_only"] if x["sport"] == code)} OLBG listings</div></a>'
            for code in self.d['sport_order'])
        lede = f'''
<section class="exec">
<h2>The executive summary</h2>
<p class="big">Today's card carries <b>{c["picks"]} graded picks</b> across <b>{x["sports_with_picks"]} of the 15 requested sports</b>:
<b>{c["high"]} High</b> and <b>{c["medium"]} Medium</b>, every one inside the −250 to +10000 band. The picks are in the table
immediately below, and each row opens the full written prediction on <a href="{self.href('predictions.html')}">the predictions page</a>.</p>
<p class="big warn">The other {len(without)} sports have no priced match today. That is not a gap in effort: OLBG showed no market at all
for golf and snooker, antepost only for rugby union, rugby league and darts, and the remaining sports have listings but no official
fixture data we could read. Each one says exactly what is missing on its sport page and on <a href="{self.href('flagged.html')}">Flagged for review</a>.</p>
</section>
<h2 id="picks">The picks — start here</h2>
<p class="note">Grade High means the selection prices at 60% or better and at −250 or longer. Medium is 55–60%. Nothing shorter than −250 is published, and no pick is a market favourite above 71.4%.</p>
{self.pick_table(self.picks)}
<h2>Where everything is</h2>
<div class="cards">
<a class="card" href="{self.href('picks.html')}"><div class="k">Every pick</div><div class="v">{c["picks"]}</div><div class="s">one table, sorted by grade</div></a>
<a class="card" href="{self.href('predictions.html')}"><div class="k">Written predictions</div><div class="v">{c["predictions"]}</div><div class="s">54–80 words each, selection named</div></a>
<a class="card" href="{self.href('matches.html')}"><div class="k">Matches</div><div class="v">{c["fixtures"]}</div><div class="s">priced, with sources</div></a>
<a class="card" href="{self.href('markets.html')}"><div class="k">Markets</div><div class="v">{c["outcomes"]}</div><div class="s">outcome prices, graded</div></a>
<a class="card" href="{self.href('flagged.html')}"><div class="k">Flagged for review</div><div class="v">{c["flags"]}</div><div class="s">what is missing and why</div></a>
<a class="card" href="{self.href('audit.html')}"><div class="k">Repo audit</div><div class="v">{self.d["audit_findings"]}</div><div class="s">line-by-line findings</div></a>
</div>
<h2>All fifteen sports</h2>
<div class="cards">{cards}</div>
<h2>How the day breaks down</h2>
<div class="scroll"><table class="t">
<tr><th>Sport</th><th>OLBG listings</th><th>Priced fixtures</th><th>Picks</th><th>High</th><th>Status</th><th>Source</th></tr>
{''.join(self.sport_row(code) for code in self.d['sport_order'])}
</table></div>
'''
        self.shell('index.html', 'OLBG research desk · 26 October 2026', 'Today’s picks, in one place', lede)

    def sport_row(self, code):
        fx = [f for f in self.d['fixtures'] if f['sport'] == code]
        pk = [f for f in self.picks if f['sport'] == code]
        rows = sum(len(x['rows']) for x in self.d['listings_only'] if x['sport'] == code)
        hub, _ = self.sport_hub(code)
        status = 'Priced' if fx else 'Listed, not priced'
        return (f'<tr><td><a href="{self.href("sports/" + code + ".html")}">{e(self.sport_name(code))}</a></td>'
                f'<td class="num">{rows if rows else "none"}</td><td class="num">{len(fx) or "–"}</td>'
                f'<td class="num">{len(pk) or "–"}</td><td class="num">{sum(1 for f in pk if f["pick"]["confidence"] == "high") or "–"}</td>'
                f'<td>{status}</td><td><a class="src" href="{e(hub)}" target="_blank" rel="noopener noreferrer">official</a></td></tr>')

    def picks_page(self):
        c = self.d['counts']
        body = f'''
<p class="note">Every published pick, best grade first. The band rule: fair American price between −250 and +10000.
Grade High ≥ 60%, Medium 55–60%, and nothing below 55% is published.</p>
<div class="cards">
<div class="card"><div class="k">High</div><div class="v">{c["high"]}</div><div class="s">60% or better, in band</div></div>
<div class="card"><div class="k">Medium</div><div class="v">{c["medium"]}</div><div class="s">55–60%</div></div>
<div class="card"><div class="k">Published picks</div><div class="v">{c["picks"]}</div><div class="s">of {c["outcomes"]} priced outcomes</div></div>
</div>
<h2>The full pick list</h2>
{self.pick_table(self.picks)}
<h2>Fixtures that carry no pick</h2>
<p class="note">These are priced, but no outcome reached the 55% floor or stayed inside the band.</p>
<div class="scroll"><table class="t"><tr><th>Sport</th><th>Match</th><th>Competition</th><th>Why no pick</th><th>Official source</th></tr>
{''.join(self.nopick_row(f) for f in self.d['fixtures'] if not f['pick'])}
</table></div>
'''
        self.shell('picks.html', 'Every pick · OLBG research desk', 'Every pick on one page', body)

    def nopick_row(self, f):
        return (f'<tr><td>{e(self.sport_name(f["sport"]))}</td><td>{e(f["away"])} at {e(f["home"])}</td>'
                f'<td>{e(f["competition"])}</td><td>{e(f.get("no_pick_reason", ""))}</td>'
                f'<td>{self.src_cell([s for s in f["sources"] if self.sources[s]["role"] == "official"])}</td></tr>')

    def predictions_page(self):
        blocks = []
        for f in self.picks:
            p = f['pick']
            blocks.append(f'''
<article class="pred" id="{e(f['id'])}">
<div class="predhead"><h2>{e(f['away'])} at {e(f['home'])}</h2>
<span class="badge {CONF_CLASS[p['confidence']]}">{CONF_LABEL[p['confidence']]}</span></div>
<p class="meta">{e(self.sport_name(f['sport']))} · {e(f['competition'])} · OLBG time {e(f['olbg_time'])}
{'· start ' + e(f['start_utc']) if f['start_utc'] else '· official UTC start not captured'}</p>
<p class="bet">Selection: <b>{e(p['selection'])}</b> — {e(p['market_label'])} at <b>{am(p['american'])}</b>
({p['probability'] * 100:.1f}% originated chance, fair decimal {p['fair_decimal']:.2f}).</p>
<p class="prose">{e(p['prose'])}</p>
<p class="facts"><b>The numbers behind it:</b> {e(f['facts'])}</p>
<p class="gaps"><b>Not in the write-up:</b> {e(p['gaps'])}</p>
<p class="srcsline">Source: {self.src_cell(f['sources'])}</p>
</article>''')
        body = f'''<p class="note">{len(self.picks)} written predictions, {min(f['pick']['words'] for f in self.picks)}–{max(f['pick']['words'] for f in self.picks)} words each,
unique in wording, each naming its selection and quoting only numbers taken from the official page linked on the same card.</p>
{''.join(blocks)}'''
        self.shell('predictions.html', 'Written predictions · OLBG research desk', 'The written predictions', body)

    def matches_page(self):
        rows = []
        for f in self.d['fixtures']:
            p = f['pick']
            rows.append(
                f'<tr><td>{e(self.sport_name(f["sport"]))}</td>'
                f'<td><b>{e(f["away"])}</b> at <b>{e(f["home"])}</b><div class="sub">{e(f["competition"])}</div></td>'
                f'<td>{e(f["olbg_time"])}</td><td>{e(f["start_utc"] or "–")}</td>'
                f'<td>{e(f["venue"] or "–")}</td>'
                f'<td>{len(f["markets"])} markets · {len(f["markets"]) * 2} outcomes</td>'
                f'<td>{"<b>" + e(p["selection"]) + "</b> " + am(p["american"]) if p else "no pick"}</td>'
                f'<td>{self.src_cell(f["sources"])}</td></tr>')
        listings = []
        for item in self.d['listings_only']:
            code = item['sport']
            hub, olbg = self.sport_hub(code)
            if not item['rows']:
                listings.append(f'<tr><td>{e(self.sport_name(code))}</td><td colspan="5" class="muted">{e(item["reason"])}</td>'
                                f'<td><a class="src" href="{e(hub)}" target="_blank" rel="noopener noreferrer">official</a> · '
                                f'<a class="src" href="{e(olbg)}" target="_blank" rel="noopener noreferrer">OLBG</a></td></tr>')
                continue
            for r in item['rows']:
                listings.append(
                    f'<tr><td>{e(self.sport_name(code))}</td><td>{e(r["match"])}</td><td>{e(r["comp"])}</td>'
                    f'<td>{e(r["time"])}</td><td>{e(r["market"])} — {e(r["sel"])}</td><td>{e(r["tips"])} tips ({e(r["share"])})</td>'
                    f'<td><a class="src" href="{e(hub)}" target="_blank" rel="noopener noreferrer">official</a> · '
                    f'<a class="src" href="{e(olbg)}" target="_blank" rel="noopener noreferrer">OLBG listing</a></td></tr>')
        body = f'''
<p class="note">Two tables. The first is every fixture we priced: {len(self.d['fixtures'])} matches, all with a start time from an official feed
or an explicit note that none was captured. The second is every OLBG listing we could not price, with the reason.</p>
<h2>Priced fixtures</h2>
<div class="scroll"><table class="t"><tr><th>Sport</th><th>Match</th><th>OLBG clock</th><th>Official start (UTC)</th><th>Venue</th><th>Book</th><th>Pick</th><th>Sources</th></tr>
{''.join(rows)}</table></div>
<h2>OLBG listings without a price</h2>
<div class="scroll"><table class="t"><tr><th>Sport</th><th>Match</th><th>Competition</th><th>OLBG clock</th><th>OLBG market</th><th>Tips</th><th>Source</th></tr>
{''.join(listings)}</table></div>
'''
        self.shell('matches.html', 'Matches · OLBG research desk', 'Every match, priced or not', body)

    def markets_page(self):
        groups = []
        for f in self.d['fixtures']:
            rows = []
            for m in f['markets']:
                for o in m['outcomes']:
                    rows.append(
                        f'<tr><td>{e(f["away"])} at {e(f["home"])}</td><td>{e(m["label"])}</td>'
                        f'<td>{e(o["sel"])}</td><td class="num">{am(o["american"])}</td>'
                        f'<td class="num">{o["fair_decimal"]:.2f}</td><td class="num">{o["p"] * 100:.1f}%</td>'
                        f'<td><span class="badge {CONF_CLASS[o["grade"]]}">{CONF_LABEL[o["grade"]]}</span></td>'
                        f'<td>{"yes" if o["in_band"] else "no"}</td>'
                        f'<td>{self.src_cell([s for s in f["sources"] if self.sources[s]["role"] == "official"])}</td></tr>')
            groups.append(''.join(rows))
        withheld = ''.join(
            f'<tr><td>{e(self.sport_name(f["sport"]))}</td><td>{e(f["away"])} at {e(f["home"])}</td><td>{e(w)}</td>'
            f'<td>{self.src_cell([s for s in f["sources"] if self.sources[s]["role"] == "official"])}</td></tr>'
            for f in self.d['fixtures'] for w in f['withheld'])
        body = f'''
<p class="note">Every originated outcome: {self.d["counts"]["markets"]} markets, {self.d["counts"]["outcomes"]} prices.
Winner, handicap and total are originated on each fixture where the official page published scoring rates. Everything else is withheld with a reason.</p>
<h2>Outcome prices</h2>
<div class="scroll"><table class="t"><tr><th>Match</th><th>Market</th><th>Selection</th><th>Price</th><th>Fair decimal</th><th>Chance</th><th>Grade</th><th>In band</th><th>Source</th></tr>
{''.join(groups)}</table></div>
<h2>Markets investigated and withheld</h2>
<div class="scroll"><table class="t"><tr><th>Sport</th><th>Match</th><th>Why withheld</th><th>Source</th></tr>{withheld}</table></div>
'''
        self.shell('markets.html', 'Markets · OLBG research desk', 'Every market we originated', body)

    def sports_index(self):
        cards = ''.join(
            f'<a class="card" href="{self.href("sports/" + s["code"] + ".html")}">'
            f'<div class="k">{e(self.sport_name(s["code"]))}</div>'
            f'<div class="v">{sum(1 for f in self.picks if f["sport"] == s["code"])} picks</div>'
            f'<div class="s">{sum(len(x["rows"]) for x in self.d["listings_only"] if x["sport"] == s["code"])} OLBG listings</div></a>'
            for s in self.d['sports'])
        body = f'<p class="note">All fifteen requested sports, in the order the brief lists them. Each page shows the OLBG capture, our prices and picks, or the reason there are none.</p><div class="cards">{cards}</div>'
        self.shell('sports.html', 'Sports · OLBG research desk', 'Fifteen sports', body)

    def sport_page(self, code):
        name = self.sport_name(code)
        hub, olbg = self.sport_hub(code)
        fx = [f for f in self.d['fixtures'] if f['sport'] == code]
        pk = [f for f in self.picks if f['sport'] == code]
        item = next((x for x in self.d['listings_only'] if x['sport'] == code), None)
        listing_rows = ''
        if item and item['rows']:
            listing_rows = ''.join(
                f'<tr><td>{e(r["match"])}</td><td>{e(r["comp"])}</td><td>{e(r["time"])}</td>'
                f'<td>{e(r["market"])} — {e(r["sel"])}</td><td>{e(r["tips"])} ({e(r["share"])})</td>'
                f'<td><a class="src" href="{e(hub)}" target="_blank" rel="noopener noreferrer">official</a></td></tr>'
                for r in item['rows'])
        body = f'''
<p class="lede">OLBG hub: <a href="{e(olbg)}" target="_blank" rel="noopener noreferrer">{e(olbg)}</a> ·
Official starting point: <a href="{e(hub)}" target="_blank" rel="noopener noreferrer">{e(hub)}</a></p>
{('<p class="warn big"><b>No price today.</b> ' + e(item['reason']) + '</p>') if item else ''}
{('<h2>Picks</h2>' + self.pick_table(pk, with_sport=False)) if pk else ''}
{('<h2>OLBG listings captured</h2><div class="scroll"><table class="t"><tr><th>Match</th><th>Competition</th><th>OLBG clock</th><th>OLBG market</th><th>Tips</th><th>Source</th></tr>' + listing_rows + '</table></div>') if listing_rows else ''}
{('<h2>Priced fixtures</h2>' + self.fixture_table(fx)) if fx else ''}
'''
        self.shell('sports/%s.html' % code, f'{name} · OLBG research desk', name, body)

    def fixture_table(self, rows):
        out = ''.join(
            f'<tr><td>{e(f["away"])} at {e(f["home"])}<div class="sub">{e(f["competition"])}</div></td>'
            f'<td>{e(f["olbg_time"])}</td><td>{e(f["start_utc"] or "not captured")}</td>'
            f'<td>{len(f["markets"])} markets</td>'
            f'<td>{"<b>" + e(f["pick"]["selection"]) + "</b> " + am(f["pick"]["american"]) + " · " + CONF_LABEL[f["pick"]["confidence"]] if f["pick"] else "no pick"}</td>'
            f'<td>{self.src_cell(f["sources"])}</td></tr>'
            for f in rows)
        return f'<div class="scroll"><table class="t"><tr><th>Match</th><th>OLBG clock</th><th>Official start</th><th>Book</th><th>Pick</th><th>Sources</th></tr>{out}</table></div>'

    def sources_page(self):
        rows = ''.join(
            f'<tr id="{e(s["id"])}"><td>{e(s["id"])}</td><td>{e(s["publisher"])}</td><td>{e(s["role"])}</td>'
            f'<td><a class="src" href="{e(s["url"])}" target="_blank" rel="noopener noreferrer">{e(s["url"])}</a></td>'
            f'<td>{e(s["observed_at"])}</td><td>{e(s["supports"])}</td></tr>'
            for s in self.d['sources'])
        body = f'''
<p class="note">Every page read for this desk, with the exact URL and the UTC time of the read.
Official sources carry the facts; OLBG is used only for its own listings and is never treated as an official source.</p>
<div class="scroll"><table class="t"><tr><th>ID</th><th>Publisher</th><th>Role</th><th>URL</th><th>Read at (UTC)</th><th>What it supports</th></tr>{rows}</table></div>
'''
        self.shell('sources.html', 'Sources · OLBG research desk', 'Every source, with its read time', body)

    def flagged_page(self):
        cards = ''.join(f"""
<article class="flag">
<div class="predhead"><h2>{e(x['topic'])}</h2>
<span class="badge {'hi' if x['severity'] == 'high' else 'md' if x['severity'] == 'medium' else 'lo'}">{e(x['severity'].title())}</span></div>
<p>{e(x['detail'])}</p>
<p class="gaps"><b>What would close it:</b> {e(x['recheck'])}</p>
<p class="srcsline">Pages involved: {self.src_cell(x['source_ids'])}</p>
</article>""" for x in self.d['flags'])
        body = f'''
<p class="note">Everything this desk could not confirm, each with the page involved and the step that would close it.
Nothing here blocks publication of the picks that do exist, and nothing missing here has been filled in by guesswork.</p>
<div class="cards mini">{self.flag_cards()}</div>
{cards}
'''
        self.shell('flagged.html', 'Flagged for review · OLBG research desk', 'Flagged for review', body)

    def flag_cards(self):
        c = {}
        for x in self.d['flags']:
            c[x['severity']] = c.get(x['severity'], 0) + 1
        return ''.join(f'<div class="card"><div class="k">{k.title()}</div><div class="v">{v}</div>'
                       f'<div class="s">items</div></div>' for k, v in sorted(c.items()))

    def audit_page(self):
        cards = ''.join(f"""
<article class="flag" id="{e(x['id'])}">
<div class="predhead"><h2>{e(x['area'])}</h2>
<span class="badge {'hi' if x['severity'] == 'high' else 'md' if x['severity'] == 'medium' else 'lo'}">{e(x['severity'].title())}</span></div>
<p>{e(x['finding'])}</p>
<p class="mono">Evidence: {e(x['evidence'])}</p>
<p class="srcsline">Where to look: <a class="src" href="https://github.com/buffedlizard55-lab/OLBG1/blob/main/{e(x['review'])}" target="_blank" rel="noopener noreferrer">{e(x['review'])}</a></p>
</article>""" for x in self.d['audit'])
        body = f'''
<p class="note">A line-by-line read of the committed repository as it stood at the base of this session.
Each finding names the file, the value read and the place to look. These are irregularities in earlier work, not in today's picks.</p>
{cards}
'''
        self.shell('audit.html', 'Repository audit · OLBG research desk', 'Repository audit', body)

    def methodology_page(self):
        m = self.d['method']
        counts = dict(self.d['counts'])
        counts.update(self.d['extras'])
        items = ''.join(f'<div class="kv"><dt>{e(k.replace("_", " "))}</dt><dd>{e(v)}</dd></div>'
                        for k, v in counts.items())
        rules = ''.join(f'<div class="rule"><h3>{e(k.replace("_", " ").title())}</h3><p>{e(v)}</p></div>'
                        for k, v in m.items())
        body = f'''
<h2>The rule, in one line</h2>
<p class="big">High is 60% or better, Medium is 55–60%, and a pick must sit between −250 and +10000.
Nothing shorter than −250 is published, which is the brief's objection to short-priced favourites turned into a filter.
The chance shown is the originated probability, not a bookmaker's, because no bookmaker price was read.</p>
<h2>Method</h2>
{rules}
<h2>What this desk contains</h2>
<div class="kvbox">{items}</div>
'''
        self.shell('methodology.html', 'Methodology · OLBG research desk', 'How the prices are made', body)

    def run(self):
        if OUT.exists():
            shutil.rmtree(OUT)
        OUT.mkdir(parents=True)
        (OUT / 'assets').mkdir()
        (OUT / 'assets' / 'desk.css').write_text(CSS, encoding='utf-8')
        self.index()
        self.picks_page()
        self.predictions_page()
        self.matches_page()
        self.markets_page()
        self.sports_index()
        for code in self.d['sport_order']:
            self.sport_page(code)
        self.sources_page()
        self.flagged_page()
        self.audit_page()
        self.methodology_page()
        manifest = dict(generated_at=self.d['generated_at'], counts=self.d['counts'], pages=sorted(self.pages),
                        desk='103ea76b', session='103ea76b-olbg1', extras=self.d['extras'])
        (OUT / 'data' / 'desk').mkdir(parents=True, exist_ok=True)
        (OUT / 'data' / 'desk' / 'manifest.json').write_text(json.dumps(manifest, indent=1) + '\n', encoding='utf-8')
        (OUT / 'data' / 'desk' / 'desk.json').write_text(json.dumps(self.d, indent=1) + '\n', encoding='utf-8')
        (OUT / '.nojekyll').touch()
        print(f'built {len(self.pages)} pages in {OUT}')


CSS = '''
:root{--ink:#16202b;--mut:#5b6b7c;--line:#dfe6ee;--bg:#f6f8fb;--card:#fff;--hi:#0b7a3b;--md:#9a6400;--lo:#5b6b7c;--acc:#1a4fa0}
*{box-sizing:border-box}
body{margin:0;font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg)}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}
header.top{background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:5}
header.top .wrap{display:flex;flex-wrap:wrap;gap:10px 24px;align-items:center;justify-content:space-between;padding-top:10px;padding-bottom:10px}
.brand a{font-weight:800;color:var(--ink);text-decoration:none;font-size:18px}
.brand .date{margin-left:10px;color:var(--mut);font-size:13px}
nav a{margin-right:14px;color:var(--acc);text-decoration:none;font-size:14px;font-weight:600}
nav a:hover{text-decoration:underline}
.strip{display:flex;gap:18px;flex-wrap:wrap;margin:18px 0 4px;color:var(--mut);font-size:14px}
.strip b{color:var(--ink)}
h1{font-size:34px;line-height:1.15;margin:10px 0 16px}
h2{font-size:21px;margin:34px 0 10px}
h3{font-size:17px;margin:22px 0 8px}
p{margin:10px 0}
.big{font-size:17px}
.warn{background:#fff8e6;border-left:4px solid #d69e00;padding:12px 14px;border-radius:6px}
.note{color:var(--mut);font-size:14px}
.lede{color:var(--mut)}
.scroll{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:10px}
table.t{border-collapse:collapse;width:100%;font-size:14px;min-width:640px}
table.t th{text-align:left;background:#eef3f9;color:var(--ink);font-size:12px;text-transform:uppercase;letter-spacing:.04em;padding:10px 12px;border-bottom:1px solid var(--line);white-space:nowrap}
table.t td{padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}
table.t tr:last-child td{border-bottom:none}
table.t a{color:var(--acc);text-decoration:none}
table.t a:hover{text-decoration:underline}
.num{white-space:nowrap;font-variant-numeric:tabular-nums}
.sub{color:var(--mut);font-size:12px}
.muted{color:var(--mut)}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px;color:var(--mut)}
.badge{display:inline-block;padding:2px 8px;border-radius:999px;font-size:12px;font-weight:700;color:#fff}
.badge.hi{background:var(--hi)}.badge.md{background:var(--md)}.badge.lo{background:var(--lo)}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:12px;margin:14px 0}
.card{display:block;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px;text-decoration:none;color:var(--ink)}
.card:hover{border-color:var(--acc)}
.card .k{font-weight:700;font-size:14px}
.card .v{font-size:24px;font-weight:800;margin:4px 0}
.card .s{color:var(--mut);font-size:12px}
.exec{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:6px 20px 16px}
.pred{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:6px 20px 16px;margin:18px 0}
.predhead{display:flex;justify-content:space-between;align-items:center;gap:12px}
.predhead h2{margin:14px 0 2px;font-size:19px}
.meta{color:var(--mut);font-size:13px;margin:2px 0 10px}
.bet{background:#eef6ff;border-left:4px solid var(--acc);padding:10px 12px;border-radius:6px}
.prose{font-size:16px}
.facts,.gaps{font-size:14px}
.gaps{color:var(--mut)}
.srcsline{font-size:13px}
.srcs a.src{margin-right:2px}
.flag{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:4px 20px 14px;margin:14px 0}
.flag h2{font-size:18px}
.kvbox{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:6px 18px}
.kv{display:flex;justify-content:space-between;gap:16px;border-bottom:1px solid var(--line);padding:8px 0;font-size:14px}
.kv:last-child{border-bottom:none}
.kv dt{color:var(--mut);text-transform:capitalize}
.kv dd{margin:0;font-weight:700;font-variant-numeric:tabular-nums}
.rule{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:2px 18px 8px;margin:12px 0}
.rule h3{font-size:15px}
.rule p{font-size:14px;color:var(--mut)}
footer{border-top:1px solid var(--line);margin-top:50px;padding:18px 20px 40px;color:var(--mut);font-size:13px}
'''


def main():
    desk = json.loads(DESK.read_text(encoding='utf-8'))
    Site(desk).run()


if __name__ == '__main__':
    main()
