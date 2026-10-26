"""Build the 26 October 2026 desk: data/aa2881ac/desk.json and 25 pages in aa2881ac/.

Usage: python scripts/saa2881ac_build.py
"""
from __future__ import annotations

import html
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import saa2881ac_data as D  # noqa: E402
import saa2881ac_model as M  # noqa: E402
import saa2881ac_content as C  # noqa: E402

ROOT = D.ROOT
OUT = ROOT / 'aa2881ac'
DATA = ROOT / 'data' / 'aa2881ac'
TEMPLATE_CSS = ROOT / 'a394f91e' / 'styles.css'
BUILT_AT = '2026-10-26T05:30Z'
TODAY = '2026-10-26'

NAV = [('index.html', 'Summary'), ('picks.html', 'Picks'), ('predictions.html', 'Predictions'),
       ('matches.html', 'Matches &amp; lines'), ('sports.html', 'Sports'), ('discovery.html', 'OLBG discovery'),
       ('flagged.html', 'Flagged for review'), ('sources.html', 'Sources'), ('audit.html', 'Repo review'),
       ('methodology.html', 'Method')]
SPORT_NAME = {s: v['name'] for s, v in D.SPORT_INDEX.items()}
SPORT_NAME['all'] = 'All sports'


def e(x):
    return html.escape(str(x), quote=True)


def a(url, text=None, cls='src'):
    from urllib.parse import urlsplit
    label = text if text is not None else urlsplit(url).netloc.replace('www.', '')
    return f'<a class="{cls}" href="{e(url)}" target="_blank" rel="noopener">{e(label)}</a>'


def pill(grade):
    return f'<span class="pill {grade.lower()}">{e(grade)}</span>'


def blank(text='not published'):
    return f'<span class="blank">{e(text)}</span>'


def table(head, rows, tight=False):
    th = ''.join(f'<th>{h}</th>' for h in head)
    body = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows)
    cls = ' class="tight"' if tight else ''
    return f'<div class="scroll"><table{cls}><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'


def page(title, body, subtitle='', active='', root=''):
    nav = ''.join(f'<a class="{"on" if h == active else ""}" href="{root}{h}">{n}</a>' for h, n in NAV)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} · OLBG research desk · 26 October 2026</title>
<link rel="stylesheet" href="{root}styles.css"></head>
<body data-desk="aa2881ac" data-built="{BUILT_AT}">
<header class="top"><div class="wide">
<a class="brand" href="{root}index.html">OLBG research desk<span>26 October 2026</span></a>
<nav>{nav}</nav>
</div></header>
<main class="wide">
<h1>{e(title)}</h1>
{f'<p class="lead">{subtitle}</p>' if subtitle else ''}
{body}
</main>
<footer class="wide"><p>Independent research, not affiliated with OLBG. No guaranteed returns and no staking
advice. Every figure is either quoted from the official page linked on the same row or is our own originated
price, labelled as such. Reads taken {e(D.READ_WINDOW)}.</p></footer>
</body></html>
"""


# --------------------------------------------------------------------------
def assemble():
    fixtures = C.fixtures()
    picks = C.picks(fixtures)
    preds = C.predictions(picks)
    flags = C.flags()
    audit = C.audit()
    discovery = [dict(sport=r[0], event=r[1], competition=r[2], label=r[3], tip=r[4], market=r[5],
                      share=r[6], event_id=r[7], olbg_url=D.SPORT_INDEX[r[0]]['olbg_url'])
                 for r in D.DISCOVERY]
    matched = {fx['olbg']['event_id']: fx for fx in fixtures if fx.get('olbg')}
    for row in discovery:
        fx = matched.get(row['event_id'])
        row['official_url'] = fx['sources'][0]['url'] if fx else ''
        row['fixture'] = fx['key'] if fx else ''
    outrights = [dict(sport=s, market=m, tip=t, share=sh, event_id=i,
                      olbg_url=D.SPORT_INDEX[s]['olbg_url']) for s, m, t, sh, i in D.OUTRIGHTS]
    counts = dict(
        sports=len(D.SPORT_INDEX), fixtures=len(fixtures),
        priced=sum(1 for f in fixtures if f.get('priced')),
        markets=sum(len(f['priced']['markets']) for f in fixtures if f.get('priced')),
        picks=len(picks), high=sum(p['grade'] == 'High' for p in picks),
        medium=sum(p['grade'] == 'Medium' for p in picks), low=sum(p['grade'] == 'Low' for p in picks),
        predictions=len(preds), discovery=len(discovery), outrights=len(outrights),
        sources=len(D.SOURCES), flags=len(flags), audit=len(audit),
        sports_with_picks=len({p['sport'] for p in picks}))
    return dict(desk='aa2881ac', generated_for=D.GENERATED_FOR, built_at=BUILT_AT, read_window=D.READ_WINDOW,
                counts=counts, sources=D.SOURCES, fixtures=fixtures, picks=picks, predictions=preds,
                discovery=discovery, outrights=outrights, flags=flags, audit=audit,
                constants=dict(band=[M.BAND_LOW, M.BAND_HIGH], high_min=M.HIGH_MIN, medium_min=M.MEDIUM_MIN,
                               low_min=M.LOW_MIN, nhl_league_gpg=round(M.NHL_LEAGUE_GPG, 3),
                               del_league_gpg=round(M.DEL_LEAGUE_GPG, 3), mlb_league_rpg=round(M.MLB_LEAGUE_RPG, 3),
                               ehf_league_gpg=round(M.EHF_LEAGUE_GPG, 3)))


# --------------------------------------------------------------------------
def pick_rows(picks, root=''):
    rows = []
    for p in picks:
        cap = ' <span class="muted">(capped)</span>' if p['capped'] else ''
        rows.append([pill(p['grade']) + cap, e(SPORT_NAME[p['sport']]),
                     f'<b>{e(p["selection"])}</b><br><span class="muted">{e(p["market"])}</span>',
                     e(p['event']) + f'<br><span class="muted">{e(p["competition"])}</span>',
                     e(p['start']), f'<b>{e(p["price_text"])}</b>', f'{p["prob"] * 100:.1f}%',
                     a(p['source']) + (f' · <a href="{root}predictions.html#{e(p["id"])}">write-up</a>'
                                       if p.get('has_pred') else '')])
    return rows


PICK_HEAD = ['Grade', 'Sport', 'Selection', 'Event', 'Start / date', 'Fair price', 'Our probability', 'Official source']


def fixture_lines(fx):
    if not fx.get('priced'):
        return blank('not priced') + f'<br><span class="muted">{e(fx.get("unpriced") or "")}</span>'
    parts = []
    for m in fx['priced']['markets']:
        outs = ' · '.join(f'{e(o["name"])} <b>{e(M.fmt(o["price"]))}</b> ({o["prob"] * 100:.0f}%)'
                          for o in m['outcomes'])
        parts.append(f'<b>{e(m["name"])}</b>: {outs}')
    return '<br>'.join(parts)


def fixture_rows(fxs):
    rows = []
    for fx in fxs:
        olbg = fx.get('olbg')
        otext = (f'{e(olbg["tip"])} ({e(olbg["market"])}, {e(olbg["share"])} tips, event {olbg["event_id"]})'
                 if olbg else blank('not listed on OLBG'))
        date = e(fx['date']) if fx['date'] else blank('not on an official page')
        src = ' · '.join(a(s['url']) for s in fx['sources'])
        rows.append([e(SPORT_NAME[fx['sport']]), f'<b>{e(fx["event"])}</b><br><span class="muted">'
                     f'{e(fx["competition"])}</span>', date + f'<br><span class="muted">{e(fx["start"])}</span>',
                     fixture_lines(fx), otext, src])
    return rows


FIX_HEAD = ['Sport', 'Event', 'Date / start', 'Our lines (fair price, probability)', 'OLBG most-tipped', 'Official source']


def pred_articles(preds, fixtures_by_key):
    out = []
    for p in preds:
        fx = fixtures_by_key[p['pick'].rsplit('-', 1)[0]]
        out.append(f"""<article class="pred" id="{e(p['pick'])}">
<div class="predhead">{pill(p['grade'])} <b>{e(p['selection'])}</b> at <b>{e(p['price_text'])}</b>
<span class="muted">{e(p['market'])}</span></div>
<p class="meta">{e(fx['event'])} · {e(fx['competition'])} · {e(fx['start'])}</p>
<p class="prose">{e(p['text'])}</p>
<p class="meta">{e(p['availability'])} Source: {a(p['source'])}</p>
</article>""")
    return '\n'.join(out)


def build():
    desk = assemble()
    fixtures, picks, preds = desk['fixtures'], desk['picks'], desk['predictions']
    by_key = {f['key']: f for f in fixtures}
    pred_ids = {p['pick'] for p in preds}
    for p in picks:
        p['has_pred'] = p['id'] in pred_ids
    c = desk['counts']

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / 'sports').mkdir(parents=True)
    shutil.copy2(TEMPLATE_CSS, OUT / 'styles.css')
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / 'desk.json').write_text(json.dumps(desk, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')

    def write(rel, html_text):
        (OUT / rel).write_text(html_text, encoding='utf-8')

    # ---- index ---------------------------------------------------------
    def is_today(p):
        return by_key[p['fixture']]['date'] == TODAY
    today_high = [p for p in picks if p['grade'] == 'High' and is_today(p)]
    later_high = [p for p in picks if p['grade'] == 'High' and not is_today(p)]
    medium = [p for p in picks if p['grade'] == 'Medium']
    cards = ''.join(f'<div class="card"><b>{n}</b><span>{lab}</span></div>' for n, lab in [
        (c['high'], 'High-confidence picks'), (c['medium'], 'Medium'), (c['low'], 'Low'),
        (c['predictions'], 'Written predictions'), (c['priced'], 'Fixtures we priced'),
        (c['markets'], 'Markets originated'), (c['flags'], 'Items flagged for review'),
        (f"{c['sports_with_picks']} / 15", 'Sports with a pick')])
    nopick = [SPORT_NAME[s] for s in D.SPORT_INDEX if not any(p['sport'] == s for p in picks)]
    links = ''.join(f'<a href="{h}"><b>{n}</b><span>{d}</span></a>' for h, n, d in [
        ('picks.html', 'All picks', f'{c["picks"]} graded selections across {c["sports_with_picks"]} sports'),
        ('predictions.html', 'Written predictions', 'The five strongest picks per sport, in full'),
        ('matches.html', 'Matches &amp; lines', 'Every fixture with win, handicap and total lines'),
        ('sports.html', 'Sport pages', 'All fifteen sports, including those with no pick'),
        ('flagged.html', 'Flagged for review', 'Gaps, conflicts and unverifiable values with links'),
        ('audit.html', 'Repo review', 'Line-linked findings from the repository')])
    def names(slugs):
        names_ = [SPORT_NAME[x] for x in D.SPORT_INDEX if x in slugs]
        return ', '.join(names_[:-1]) + ' and ' + names_[-1] if len(names_) > 1 else ''.join(names_)
    high_sports = {p['sport'] for p in picks if p['grade'] == 'High'}
    other_sports = {p['sport'] for p in picks} - high_sports
    lead_pick = (today_high or later_high)[0]
    hero = f"""<div class="note"><p><strong>Highest-confidence call today: {e(lead_pick['selection'])}
({e(lead_pick['event'])}) at {e(lead_pick['price_text'])}.</strong> {c['high']} High picks are live across
{e(names(high_sports).lower())}, all priced between -250 and +10000. {e(names(other_sports))} carry Medium or Low
picks only. {len(nopick)} sports have no pick because no official fixture or no official figure was readable:
{e(', '.join(nopick))}.</p></div>"""
    body = (hero + f'<section class="cards">{cards}</section>'
            + '<h2>High confidence — today (26 October)</h2>'
            + table(PICK_HEAD, pick_rows(today_high))
            + '<h2>High confidence — upcoming (27–29 October)</h2>'
            + table(PICK_HEAD, pick_rows(later_high))
            + '<h2>Medium confidence</h2>' + table(PICK_HEAD, pick_rows(medium))
            + f'<h2>Explore</h2><div class="links">{links}</div>')
    write('index.html', page('Today\'s summary', body,
                             'Our own prices on officially listed fixtures, with OLBG used only to find the events.',
                             'index.html'))

    # ---- picks ---------------------------------------------------------
    body = ''
    for slug in D.SPORT_INDEX:
        rows = [p for p in picks if p['sport'] == slug]
        if rows:
            body += f'<h2 id="{slug}">{e(SPORT_NAME[slug])}</h2>' + table(PICK_HEAD, pick_rows(rows))
    body += (f'<p class="note">Sports with no pick: {e(", ".join(nopick))}. The reason for each is on its '
             f'<a href="sports.html">sport page</a> and on <a href="flagged.html">Flagged for review</a>.</p>')
    write('picks.html', page('All picks', body, f'{c["picks"]} picks: {c["high"]} High, {c["medium"]} Medium, '
                             f'{c["low"]} Low. A pick always backs the side we make the winner.', 'picks.html'))

    # ---- predictions ---------------------------------------------------
    body = ''
    for slug in D.SPORT_INDEX:
        rows = [p for p in preds if p['sport'] == slug]
        if rows:
            body += f'<h2 id="{slug}">{e(SPORT_NAME[slug])}</h2>' + pred_articles(rows, by_key)
    write('predictions.html', page('Written predictions', body,
                                   'Up to five per sport, strongest first. Prices are fair (no margin).',
                                   'predictions.html'))

    # ---- matches -------------------------------------------------------
    body = ''
    for slug in D.SPORT_INDEX:
        rows = [f for f in fixtures if f['sport'] == slug]
        if rows:
            body += f'<h2 id="{slug}">{e(SPORT_NAME[slug])}</h2>' + table(FIX_HEAD, fixture_rows(rows))
    write('matches.html', page('Matches & lines', body,
                               f'{c["fixtures"]} officially confirmed fixtures, {c["priced"]} priced across '
                               f'{c["markets"]} markets. OLBG tips are shown as text for comparison only.',
                               'matches.html'))

    # ---- discovery -----------------------------------------------------
    rows = []
    for r in desk['discovery']:
        off = a(r['official_url']) if r['official_url'] else blank('no official page matched')
        rows.append([e(SPORT_NAME[r['sport']]), e(r['event']), e(r['competition']), e(r['label']),
                     e(r['tip']), e(r['market']), e(r['share']), a(r['olbg_url'], f'OLBG #{r["event_id"]}'), off])
    orow = [[e(SPORT_NAME[o['sport']]), e(o['market']), e(o['tip']), e(o['share']),
             a(o['olbg_url'], f'OLBG #{o["event_id"]}'), blank('outright, not priced')] for o in desk['outrights']]
    body = ('<p>OLBG hub pages were read once each; per-event OLBG addresses were not captured, so each row links '
            'to its sport hub and shows the OLBG event number. Times are OLBG\'s own labels (US Eastern).</p>'
            + table(['Sport', 'Event (OLBG naming)', 'Competition', 'OLBG time label', 'Most-tipped', 'Market',
                     'Tip share', 'OLBG', 'Official page'], rows, tight=True)
            + '<h2>Outrights listed</h2>'
            + table(['Sport', 'Market', 'Most-tipped', 'Tip share', 'OLBG', 'Official page'], orow, tight=True))
    write('discovery.html', page('OLBG discovery', body, f'{c["discovery"]} match markets and {c["outrights"]} '
                                 'outrights as published by OLBG, matched to official pages where possible.',
                                 'discovery.html'))

    # ---- flagged -------------------------------------------------------
    rows = [[e(f['id']), e(SPORT_NAME[f['sport']]), f'<span class="pill sev">{e(f["kind"])}</span>', e(f['text']),
             a(f['url'])] for f in desk['flags']]
    unp = [[e(SPORT_NAME[f['sport']]), e(f['event']), e(f.get('unpriced') or ''), a(f['sources'][0]['url'])]
           for f in fixtures if not f.get('priced')]
    body = (table(['#', 'Sport', 'Type', 'Item', 'Source to recheck'], rows, tight=True)
            + '<h2>Official fixtures we did not price</h2>'
            + table(['Sport', 'Fixture', 'Why not priced', 'Official source'], unp, tight=True)
            + '<p class="note">Flagged items are published, not hidden. None of them blocks the picks above, '
              'because no flagged value is used in a price.</p>')
    write('flagged.html', page('Flagged for review', body, f'{c["flags"]} items to recheck, each with the page '
                               'to recheck it against.', 'flagged.html'))

    # ---- sources -------------------------------------------------------
    rows = [[e(s['publisher']), e(s['role'].replace('_', ' ')), e(s['read_at']), e(s['supports']), a(s['url'])]
            for s in D.SOURCES]
    write('sources.html', page('Sources', table(['Publisher', 'Role', 'Read at', 'What it supports', 'Link'],
                                                rows, tight=True),
                               f'{c["sources"]} pages read this session. OLBG is discovery only; every price input '
                               'comes from an official league, tour or federation page.', 'sources.html'))

    # ---- audit ---------------------------------------------------------
    rows = [[e(r['id']), f'<span class="pill sev-{r["severity"]}">{e(r["severity"])}</span>',
             f'<code>{e(r["path"])}</code>' + (f' {e(r["lines"])}' if r['lines'] else ''), e(r['text']),
             a(r['url'], 'view on GitHub')] for r in desk['audit']]
    body = ('<p>Reviewed at commit <code>90646c8</code> (main after PR #299). Each finding links to the exact '
            'lines. Items marked fixed in this change are noted in the session report.</p>'
            + table(['#', 'Severity', 'File', 'Finding', 'Lines'], rows, tight=True))
    write('audit.html', page('Repo review', body, f'{c["audit"]} findings from a line-by-line read of the build, '
                             'validator, workflow and the previous desk.', 'audit.html'))

    # ---- methodology ---------------------------------------------------
    k = desk['constants']
    body = f"""<div class="prose">
<h2>What a pick is</h2>
<p>For every officially confirmed fixture with official season figures for both sides we originate fair prices
(no bookmaker margin) for the main result, a handicap and a total. The pick backs the side we make the winner.
If that side's money-line price is shorter than -250, the pick moves to the same side's handicap.</p>
<h2>Confidence</h2>
<ul class="bullets"><li><b>High</b>: our probability at least {k['high_min']:.2f} and fair price inside
{k['band'][0]} to +{k['band'][1]}.</li><li><b>Medium</b>: {k['medium_min']:.2f} to {k['high_min']:.2f}, inside the
band.</li><li><b>Low</b>: {k['low_min']:.2f} to {k['medium_min']:.2f}, inside the band. Fixtures whose date is not on
an official page are capped at Low.</li></ul>
<h2>Pricing by sport</h2>
<ul class="bullets">
<li><b>Ice hockey (NHL, DEL)</b>: goals for and against per game, shrunk toward the league mean with a 10-game
prior (NHL {k['nhl_league_gpg']}, DEL {k['del_league_gpg']} goals per team-game), home edge 0.18 goals, normal
spread of 1.85 on the margin and 2.40 on the total.</li>
<li><b>Baseball</b>: season runs scored and allowed; the allowed rate is 5/9 the probable starter's runs per nine and
4/9 the club's. League baseline {k['mlb_league_rpg']} runs per game (partial, see flags). Margin spread 4.3, total 4.5.</li>
<li><b>Tennis</b>: ATP ranking points ratio for the match; the set handicap uses the per-set probability implied by
a best-of-three match.</li>
<li><b>Handball</b>: goals for and against shrunk with a 3-game prior (league {k['ehf_league_gpg']} per team-game),
home edge 1.5 goals, margin spread 5.5; the draw is the probability the margin rounds to zero.</li>
<li><b>Volleyball</b>: share of rally points won, halved toward 50 percent, converted exactly to set and match
probabilities.</li>
<li><b>Formula 1</b>: share of 2026 race wins with half a win added per winner and two wins for the rest of the
field.</li></ul>
<p>These constants are our own settings, not figures published by any league.</p>
<h2>Predictions</h2>
<p>The five strongest picks per sport get a written prediction of at least thirty words. Every statistic quoted is
in the linked official table. No injury report was read, so none is claimed.</p></div>"""
    write('methodology.html', page('Method', body, 'How prices and grades are produced.', 'methodology.html'))

    # ---- sports --------------------------------------------------------
    cards = []
    for slug, meta in D.SPORT_INDEX.items():
        sp = [p for p in picks if p['sport'] == slug]
        best = max(sp, key=lambda p: (C.GRADE_RANK[p['grade']], p['prob'])) if sp else None
        tag = f'Top: {best["selection"]} ({best["grade"]})' if best else 'No pick — see reasons'
        nfx = sum(f['sport'] == slug for f in fixtures)
        cards.append(f'<a class="sport" href="sports/{slug}.html"><b>{e(meta["name"])}</b>'
                     f'<span>{nfx} official fixtures · {len(sp)} picks</span><em>{e(tag)}</em></a>')
    write('sports.html', page('Sports', f'<div class="grid">{"".join(cards)}</div>',
                              'All fifteen requested sports.', 'sports.html'))

    read_urls = {s['url'] for s in D.SOURCES}
    for slug, meta in D.SPORT_INDEX.items():
        sp = [p for p in picks if p['sport'] == slug]
        sf = [f for f in fixtures if f['sport'] == slug]
        spr = [p for p in preds if p['sport'] == slug]
        sfl = [f for f in desk['flags'] if f['sport'] in (slug, 'all')]
        sd = [r for r in desk['discovery'] if r['sport'] == slug]
        so = [o for o in desk['outrights'] if o['sport'] == slug]
        body = (f'<p>OLBG hub: {a(meta["olbg_url"], "olbg.com/" + meta["olbg_url"].split("tips/")[1])} · '
                + ('Official reference: ' if meta['official_url'] in read_urls else
                 'Official home page (not read this session): ') + f'{a(meta["official_url"])}</p>')
        body += '<h2>Picks</h2>' + (table(PICK_HEAD, pick_rows(sp, '../')) if sp else
                                    '<p class="note">No pick for this sport today. See the flags below.</p>')
        if spr:
            body += '<h2>Written predictions</h2>' + pred_articles(spr, by_key)
        if sf:
            body += '<h2>Official fixtures and our lines</h2>' + table(FIX_HEAD, fixture_rows(sf))
        if sd or so:
            rows = [[e(r['event']), e(r['label']), e(r['tip']), e(r['share']),
                     a(r['olbg_url'], f'OLBG #{r["event_id"]}'),
                     a(r['official_url']) if r['official_url'] else blank('no official page matched')] for r in sd]
            rows += [[e(o['market']), 'outright', e(o['tip']), e(o['share']), a(o['olbg_url'], f'OLBG #{o["event_id"]}'),
                      blank('outright, not priced')] for o in so]
            body += '<h2>What OLBG listed</h2>' + table(['Event', 'OLBG label', 'Most-tipped', 'Share', 'OLBG',
                                                         'Official page'], rows, tight=True)
        body += '<h2>Flags</h2>' + table(['#', 'Item', 'Recheck'], [[e(f['id']), e(f['text']), a(f['url'])]
                                                                     for f in sfl], tight=True)
        html_text = page(meta['name'], body, f'{len(sf)} official fixtures, {len(sp)} picks, {len(spr)} written '
                         'predictions.', 'sports.html', root='../')
        (OUT / 'sports' / f'{slug}.html').write_text(html_text, encoding='utf-8')

    pages = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob('*.html'))
    print(f'built {len(pages)} pages in {OUT.relative_to(ROOT)}; ' + json.dumps(c))
    return desk


if __name__ == '__main__':
    build()
