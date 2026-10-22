"""Canonical static site. All data and links work without JavaScript.

Legacy desks remain archives. No browser-side external API requests, proxying,
missing-input defaults or inherited certification labels.
"""
from pathlib import Path
from collections import Counter
import argparse,csv,html,io,json,math,os,re,shutil,subprocess
from urllib.parse import urlsplit,urlunsplit
from .common import load,save,now_utc,parse_time,iso,digest
from .config import ROOT,CURRENT,SPORT_INDEX,SPORT_MARKETS,MARKET_REQUIREMENTS
from .assemble import assemble
from .audit import build_audit
REPO='https://github.com/buffedlizard55-lab/OLBG1'
LIVE='https://buffedlizard55-lab.github.io/OLBG1/'
ARCHIVE=Path('archive/root-20261022')
ICONS={
'grid':'<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
'list':'<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
'chart':'<path d="M4 20V10m7 10V4m7 16v-7M2 22h20"/>',
'shield':'<path d="M12 3l8 3v6c0 5-8 9-8 9S4 17 4 12V6zM9 12l2 2 4-5"/>',
'flag':'<path d="M5 21V4c5-4 9 4 14 0v10c-5 4-9-4-14 0"/>',
'book':'<path d="M12 5v16M3 4c3-1 6-1 9 1 3-2 6-2 9-1v15c-3-1-6-1-9 1-3-2-6-2-9-1z"/>',
'archive':'<rect x="3" y="3" width="18" height="5" rx="1"/><path d="M5 8v12h14V8M10 12h4"/>',
'link':'<path d="M10 13a5 5 0 007 0l3-3a5 5 0 00-7-7l-2 2M14 11a5 5 0 00-7 0l-3 3a5 5 0 007 7l2-2"/>',
'external':'<path d="M14 3h7v7M21 3L10 14M10 3H4v17h17v-6"/>',
'arrow':'<path d="M5 12h14M14 7l5 5-5 5"/>',
'download':'<path d="M12 3v12M7 10l5 5 5-5M4 16v5h16v-5"/>',
'clock':'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
'search':'<circle cx="10" cy="10" r="7"/><path d="M15 15l6 6"/>',
'menu':'<path d="M3 6h18M3 12h18M3 18h18"/>',
'alert':'<path d="M12 3L2 21h20zM12 9v5m0 3v.01"/>',
'ball':'<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c-5 5-5 13 0 18M12 3c5 5 5 13 0 18"/>',
'spark':'<path d="M12 3l2.6 6.4L21 12l-6.4 2.6L12 21l-2.6-6.4L3 12l6.4-2.6z"/>',
'code':'<path d="M8 5L2 12l6 7M16 5l6 7-6 7M14 3l-4 18"/>'}
def e(v):return html.escape('' if v is None else str(v),quote=True)
def icon(name,size=18):return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS.get(name,ICONS["ball"])}</svg>'
def badge(text,style='gray'):return f'<span class="badge {e(style)}">{e(text)}</span>'
def american(n):return f'{n:+d}' if n is not None else ''
def stamp(v):return parse_time(v).strftime('%d %b %Y · %H:%M UTC') if v else ''
def ext(url,label):return f'<a class="source-link" href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(label)} {icon("external",11)}</a>'
def publisher(c):
    names={'nhl':'NHL','mlb':'MLB','nba':'NBA','euroleague':'EuroLeague','atp':'ATP PDF','wta':'WTA PDF','wst':'WST','lnr':'LNR','irl':'IRL','pcb':'PCB','ehf':'EHF PDF','aflw':'AFLW','pga':'PGA TOUR','f1':'Formula 1','munster':'Munster GAA','pls':'PLS club','riot':'Riot','gbgb':'GBGB','pdc':'PDC','olbg':'OLBG'}
    return names.get(c['id'].replace('http-','').split('-')[0],urlsplit(c['url']).hostname.replace('www.',''))
def table(head,rows,cls='source-table'):
    return '<div class="panel table-wrap"><table class="'+cls+'"><thead><tr>'+''.join('<th>'+h+'</th>' for h in head)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+v+'</td>' for v in row)+'</tr>' for row in rows)+'</tbody></table></div>'
def section(title,sub='',anchor=''):
    return f'<div class="section-heading"'+(f' id="{anchor}"' if anchor else '')+f'><div><h2>{title}</h2>'+('<p>'+sub+'</p>' if sub else '')+'</div></div>'

class Site:
    def __init__(self,snapshot,audit,out):
        self.s=snapshot;self.audit=audit;self.out=Path(out)
        self.c={p.stem:load(p) for p in sorted((CURRENT/'evidence').glob('*.json'))}
        self.prices={p['fixture_id']:p for p in snapshot['prices']}
        self.fixture_map={r['id']:r for r in snapshot['fixtures']}
        self.rows=[r for r in snapshot['fixtures'] if r['in_window']]
        self.revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    def href(self,target,page):return os.path.relpath(self.out/target,(self.out/page).parent).replace(os.sep,'/')
    def sources(self,row,page,details=True):
        links=[ext(self.c[s]['url'],publisher(self.c[s])) for s in row['source_ids']]
        if details:links.append(f'<a class="source-link" href="{self.href("verification.html",page)}#{e(row["id"])}">Field evidence {icon("arrow",11)}</a>')
        return '<div class="sources-stack">'+''.join(links)+'</div>'
    def notice(self,text):return f'<div class="notice">{icon("alert",17)}<p>{text}</p></div>'
    def frame(self,title,page,body,nav='overview',description='',eyebrow='Research workspace',actions=None):
        r=lambda target:self.href(target,page)
        menus=[('overview','index.html','grid','Overview',''),('matches','picks.html','list','Match list',str(self.s['counts']['current_listings'])),('markets','markets.html','chart','Market explorer',''),('predictions','predictions.html','spark','High-confidence picks',str(self.s['counts']['high'])),('sports','sports.html','ball','All sports','17')]
        research=[('review','flagged.html','flag','Flagged for Review',str(len(self.audit['findings']))),('analysis','analysis.html','chart','Analysis & findings',''),('sources','sources.html','link','Sources & evidence',''),('method','methodology.html','book','Methodology',''),('reverse','reverse-engineering.html','code','OLBG discovery','')]
        def navlinks(items):
            return ''.join(f'<a class="nav-link {"active" if key==nav else ""}" href="{r(path)}"'+(' aria-current="page"' if key==nav else '')+f'>{icon(sym,17)}<span>{label}</span>'+ (f'<span class="count {"warn-count" if key=="review" else ""}">{count}</span>' if count else '')+'</a>' for key,path,sym,label,count in items)
        controls=actions if actions is not None else f'<a class="button" href="{r("data/current/matches.csv")}" download>{icon("download",14)} Export data</a>'
        heading=f'<header class="page-heading"><div><p class="eyebrow">{e(eyebrow)}</p><h1>{e(title)}</h1><p>{description}</p></div><div class="actions">{controls}</div></header>'
        doc=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Independent source-linked match research. Partial fixtures, experimental fair prices and explicit review flags. Not affiliated with OLBG."><meta name="color-scheme" content="light"><meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; object-src 'none'; base-uri 'none'; form-action 'none'; connect-src 'none'"><title>{e(title)} · OLBG Research</title><link rel="icon" href="{r('assets/current-mark.svg')}" type="image/svg+xml"><link rel="stylesheet" href="{r('assets/current-style.css')}"><script defer src="{r('assets/current-app.js')}"></script></head><body data-snapshot="{e(self.s['generated_at'])}"><a class="skip" href="#main">Skip to content</a><div class="sidebar-shade" id="sidebar-shade" hidden></div><aside class="sidebar" id="sidebar" aria-label="Primary navigation"><a class="brand" href="{r('index.html')}"><span class="brand-mark">{icon('chart',24)}</span><span><strong>OLBG<span style="font-weight:400">.</span></strong><small>RESEARCH DESK</small></span></a><nav><div class="nav-label">WORKSPACE</div>{navlinks(menus)}<div class="nav-label">RESEARCH & TRANSPARENCY</div>{navlinks(research)}<div class="nav-label">PROJECT</div>{navlinks([('archive','archive.html','archive','Earlier snapshots','')])}</nav><div class="sidebar-bottom"><div class="status-card"><strong><span class="status-dot"></span> Evidence-first research</strong><p>No default ratings. No invented inputs.<br>Blank means unverified.</p></div><p>Independent project · Not affiliated with OLBG</p></div></aside><div class="layout"><header class="topbar"><button class="mobile-menu" id="menu-button" aria-label="Open navigation" aria-expanded="false" aria-controls="sidebar">{icon('menu',21)}</button><div class="crumb"><span class="workspace-label">Research workspace <span aria-hidden="true">/</span></span><strong>{e(title if len(title)<32 else 'Overview')}</strong></div><div class="topbar-right"><span><span class="status-dot"></span><span class="freshness">Partial coverage</span></span><span class="date">{stamp(self.s['generated_at'])}</span><a href="{REPO}" aria-label="View project on GitHub">{icon('code',17)}</a></div></header><main class="main" id="main">{heading}<div class="notice expiry-alert" id="expiry-alert" role="status" hidden>{icon('clock',17)}<p><strong>Time checks have changed.</strong> Expired or elapsed estimates are withheld. Counts marked — are no longer current. Source facts remain historical observations; check the official status.</p></div>{body}<footer class="footer"><span>Independent research, not betting guarantees. 18+ · Never stake what you cannot afford to lose.</span><span>Built {stamp(self.s['generated_at'])} · <a href="{REPO}/commit/{self.revision}">{self.revision[:7]}</a> · <a href="{r('methodology.html')}">How this works</a></span></footer></main></div></body></html>'''
        path=self.out/page;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(doc,encoding='utf-8')
    def kpis(self):
        c=self.s['counts'];items=[('Source-linked listings',str(c['current_listings']),'list','<span>7-day</span> source-date window',True),('Categories with listings',f'{c["categories_with_listings"]}<small> / 17</small>','ball','All categories remain partial',True),('Experimental price books',str(c['priced_matches']),'chart',f'{c["originated_markets"]} markets · Low only',True),('High-confidence picks',str(c['high']),'shield','No unsupported selections released',False)]
        return '<section class="kpis" aria-label="Snapshot summary">'+''.join(f'<div class="kpi"><div class="kpi-label">{label}<span class="kpi-icon">{icon(sym,16)}</span></div><div class="kpi-value"'+(' data-live-kpi' if live else '')+f'>{value}</div><div class="kpi-foot">{foot}</div></div>' for label,value,sym,foot,live in items)+'</section>'
    def time_cell(self,row):
        f=row['facts']
        if f['start_utc']:
            d=parse_time(f['start_utc']);return f'<span class="time">{d:%d %b}<small>{d:%H:%M} UTC</small></span>'
        if f['date']:return f'<span class="time">{e(f["date"])}<small>UTC time unverified</small></span>'
        return ''
    def match_cell(self,row,page):
        f=row['facts'];title=e(f['event']) if row['kind']=='event' else e(f['participant_a'])+' <span class="versus">vs</span> '+e(f['participant_b'])
        return f'<div class="match"><a href="{self.href("verification.html",page)}#{e(row["id"])}">{title}</a><small>{e(f["competition"])}</small></div>'
    def match_table(self,rows,page,compact=False):
        head='<th aria-sort="ascending"><button class="sort-btn" data-sort="date">Start (UTC) ↕</button></th><th>Match / event</th>'+('' if compact else '<th>Sport</th>')+'<th>Experimental winner</th><th>Fair odds</th>'+('' if compact else '<th>Confidence</th><th>Evidence / status</th><th>Official source</th>')
        out=f'<div class="table-wrap"><table id="match-table" class="{"wide-table" if not compact else "compact-table"}"><caption class="sr-only">Official-source listings. Blank cells are unverified or withheld. Prices are estimates, not bookmaker offers.</caption><thead><tr>{head}</tr></thead><tbody>'
        for row in rows:
            f=row['facts'];p=self.prices[row['id']];state=row['state'];name=f['event'] or f'{f["participant_a"] or ""} {f["participant_b"] or ""}'
            out+=f'<tr id="{e(row["id"])}" data-record data-search="{e(name+" "+str(f["competition"] or ""))}" data-sport="{row["sport"]}" data-state="{e(state)}" data-date="{e(f["date"])}" data-priced="{str(bool(p["markets"])).lower()}" data-expires="{row["expires_at"]}" data-start="{e(f["start_utc"])}"><td>{self.time_cell(row)}</td><td>{self.match_cell(row,page)}{self.sources(row,page,False) if compact else ""}</td>'
            if not compact:out+=f'<td><a class="tiny" href="{self.href("sports/"+row["sport"]+".html",page)}">{e(SPORT_INDEX[row["sport"]]["name"])}</a></td>'
            out+=f'<td><span data-price-value>{e(p["selection"])}</span>'+('<span class="secondary">Experimental · not a betting edge</span>' if p['selection'] and not compact else '')+'</td><td>'
            if p['fair_decimal'] is not None:out+=f'<span class="price number" data-price-value data-american="{american(p["american_display"])}" data-decimal="{e(p["decimal_display"])}">{american(p["american_display"])}</span><span class="secondary number" data-price-value>{p["probability"]:.1%} model chance</span>'
            if compact and p['confidence']=='low':out+='<span class="badge low" data-conf-value>Low</span>'
            out+='</td>'
            if not compact:out+='<td>'+('<span class="badge low" data-conf-value>Low</span>' if p['confidence']=='low' else '')+'</td>'
            if not compact:out+=f'<td><span class="badge {"green" if state=="upcoming" else "amber"}" data-state-label>{e("Time unverified" if state=="time unverified" else state.capitalize())}</span><span class="secondary">'+('Sourced schedule; not full verification' if state=='upcoming' else 'See field-level flags')+'</span></td>'
            if not compact:out+=f'<td>{self.sources(row,page,True)}</td>'
            out+='</tr>'
        return out+'</tbody></table></div>'
    def filters(self,page,sport=None,markets=False):
        options='<option value="">All sports</option>'+''.join(f'<option value="{x["slug"]}">{e(x["name"])}</option>' for x in SPORT_INDEX.values())
        sf='' if sport else f'<label>Sport<select id="sport-filter">{options}</select></label>'
        more='' if markets else '<label>Evidence state<select id="state-filter"><option value="">All states</option><option value="upcoming">Future UTC captured</option><option value="time unverified">Time unverified</option><option value="stale">Stale evidence</option><option value="start elapsed">Start elapsed</option><option value="status not pre-match">Not pre-match</option></select></label><label>Date in source<input id="date-filter" type="date"></label><label class="checkbox"><input id="priced-only" type="checkbox">With experimental prices</label>'
        return f'<form id="filters" class="filterbar" role="search"><label class="search">Search participants, events or competition<input id="search" type="search" placeholder="Search the research desk…" autocomplete="off"></label>{sf}{more}<button class="button" type="button" id="clear-filters">Clear</button></form><div class="filter-meta"><span id="result-count" role="status" aria-live="polite"></span><label>Odds format <select id="odds-format" aria-label="Odds format"><option value="american">American</option><option value="decimal">Decimal</option></select></label></div>'
    def sport_cards(self,limit=None):
        cov={c['slug']:c for c in self.s['coverage']};order=['basketball','ice-hockey','tennis','baseball','rugby-league','rugby-union','snooker','cricket','handball','motor-racing','volleyball','aussie-rules','golf','gaelic-football','esports','darts','greyhounds']
        return '<div class="sport-grid">'+''.join(f'<a class="sport-card" href="sports/{s}.html"><span class="sport-icon">{icon("ball",19)}</span><span><strong>{e(cov[s]["name"])}</strong><small>{cov[s]["listing_count"]} listings · {e(cov[s]["status"])}</small></span><span class="arrow">{icon("arrow",13)}</span></a>' for s in order[:limit])+'</div>'
    def dashboard(self):
        c=self.s['counts'];rows=[r for r in self.rows if r['state']=='upcoming'][:7]
        b=self.notice(f'<strong>Transparency first.</strong> A partial, evidence-backed snapshot—not a complete global match list. {c["unpriced"]} captured listings have no supported price. <a href="flagged.html">See what needs review →</a>')+self.kpis()
        b+='<div class="grid-two"><section class="panel"><header class="panel-head"><div><h2>Next up on the slate</h2><p>Exact UTC starts from official sources · independent fair odds</p></div><a class="text-link" href="picks.html">View all '+icon('arrow',12)+'</a></header>'+self.match_table(rows,'index.html',True)+'<div class="table-note">Schedule facts are sourced; prices are experimental. A source link does not verify every field.</div></section>'
        b+=f'<section class="panel"><header class="panel-head"><h2>Confidence watch</h2>{badge("No High released")}</header><div class="empty-panel"><div class="empty-mark">{icon("shield",24)}</div><h3>Confidence is earned.<br>Not filled in.</h3><p>No selection clears the evidence and calibration gates. We would rather leave a cell blank than invent an advantage.</p><ul class="checklist"><li><span class="ring"></span>Out-of-sample model calibration</li><li><span class="ring"></span>Current player, form & match history</li><li><span class="ring"></span>Verified odds from −250 to +10000</li></ul><a class="button" href="predictions.html">Read the release criteria {icon("arrow",13)}</a></div></section></div>'
        b+='<div class="section-heading"><div><h2>Explore by sport</h2><p>Every category stays visible—even when reliable data is missing.</p></div><a class="text-link" href="sports.html">All 17 categories →</a></div>'+self.sport_cards(8)
        b+=section('Research, with the workings attached','What was read, what was estimated, and what remains unknown.')+'<div class="grid-three">'
        for num,title,text,url,label in [('01','Follow the evidence',f'{c["sources"]} official-source checks. Field observations, timestamps, capture limits and exact source links.','sources.html','Explore sources'),('02','Inspect the model',f'{c["originated_markets"]} independent research markets. No copied bookmaker prices or missing-input defaults.','methodology.html','Read the method'),('03','Review the irregularities',f'{len(self.audit["findings"])} findings and {self.audit["counts"]["row_occurrences"]:,} historical row occurrences inventoried—not recertified.','flagged.html','Open review queue')]:
            b+=f'<article class="step-card"><span class="step-num">{num} / THE PROCESS</span><h3>{title}</h3><p>{text}</p><div class="inline-links"><a href="{url}">{label} →</a></div></article>'
        self.frame('The match research desk.','index.html',b+'</div>',description='Official-source fixtures. Independent lines. A transparent view of what we know—and what we don’t.',eyebrow='OFFICIAL EVIDENCE · INDEPENDENT ESTIMATES',actions='<a class="button" href="data/current/matches.csv" download>'+icon('download',14)+' Export data</a><a class="button primary" href="picks.html">Explore matches '+icon('arrow',14)+'</a>')
    def matches(self,page='picks.html',sport=None):
        rows=[r for r in self.rows if not sport or r['sport']==sport];title=SPORT_INDEX[sport]['name'] if sport else 'Match list'
        b=self.notice('<strong>Blank means unverified.</strong> Every listing has an official source. Missing starts, inputs, markets and selections are deliberately not filled in. Low estimates are not betting recommendations.')
        if sport:
            c=next(c for c in self.s['coverage'] if c['slug']==sport)
            b+=f'<div class="panel pad" style="margin-bottom:20px"><div class="card-topline"><strong>{c["captured_count"]} captured listings · {c["priced_count"]} experimental books</strong>{badge(c["status"],"amber")}</div><p class="tiny">{e(c["note"])}</p><div class="inline-links">{ext(c["official_url"],"Official lookup—not verification")}<a href="../flagged.html#coverage">Coverage gaps →</a></div></div>'
        b+=self.filters(page,sport) if rows else ''
        if rows:b+='<section class="panel">'+self.match_table(rows,page)+'<div class="table-note">A future timestamp verifies the published start only. Venue, live status, odds and form need separate evidence.</div></section>'
        else:b+=f'<div class="hero-empty"><div class="empty-mark">{icon("search",25)}</div><div><h2>No verified match rows in this capture</h2><p>A coverage gap, not a claim of no events. The source did not supply a usable fixture/runner table. Selection, price, date and participants remain blank.</p><div class="inline-links">{ext(SPORT_INDEX[sport]["official_url"],"Official source")}<a href="../flagged.html">Review flag →</a></div></div></div>'
        b+='<p id="no-results" class="no-results" hidden>No entries match these filters. Clear them to see all captured rows.</p>'
        self.frame(title,page,b,'sports' if sport else 'matches',description='A searchable, source-linked register. No row is excluded because its data is incomplete.',actions='<button class="button" type="button" id="export-visible"'+(' disabled title="No verified rows to export"' if not rows else '')+'>'+icon('download',14)+' Export visible</button>')
    def sports(self):
        b=self.notice('<strong>17 categories, no completeness claim.</strong> Captured fixtures do not imply full category coverage. Unsupported categories remain visible.')+self.sport_cards()+section('Scope exclusions')+'<div class="panel pad prose"><p>Soccer, boxing, UFC, MMA, football, American football, hurling, horse racing, cycling and specials are excluded. Gaelic football remains a distinct inherited category—not soccer or American football. Hurling, camogie and shinty entries are not imported.</p><p>OLBG discovery supplies a public route map, not authoritative match facts or worldwide coverage.</p><a href="reverse-engineering.html">Inspect the route analysis →</a></div>'
        self.frame('Explore all sports','sports.html',b,'sports',description='Category listings, official links, market coverage and explicit limits.')
        for slug in SPORT_INDEX:self.matches('sports/'+slug+'.html',slug)
    def markets(self):
        page='markets.html';c=self.s['counts'];b=self.notice(f'<strong>{c["originated_markets"]} research markets, not bookmaker offers.</strong> Zero added margin. Actual odds, availability and betting edge are unverified. All estimates are Low confidence.')+self.filters(page,markets=True)
        for row in self.rows:
            p=self.prices[row['id']]
            if not p['markets']:continue
            f=row['facts'];label=f'{f["participant_a"]} vs {f["participant_b"]}'
            b+=f'<section class="panel market-book" id="{e(row["id"])}" data-record data-search="{e(label+" "+str(f["competition"]))}" data-sport="{row["sport"]}" data-expires="{row["expires_at"]}" data-start="{e(f["start_utc"])}"><header class="panel-head"><div><h2>{e(label)}</h2><p>{e(f["competition"])} · {stamp(f["start_utc"])}</p></div><span class="badge low" data-conf-value>Low · experimental</span></header><div class="table-wrap"><table><thead><tr><th>Market / line</th><th>Selection</th><th>Model chance</th><th>Fair odds</th><th>Fair-price band</th><th>Source</th></tr></thead><tbody>'
            for m in p['markets']:
                for o in m['outcomes']:
                    b+=f'<tr><td>{e(m["market"].title())}'+(f'<span class="secondary">{e(m.get("line"))} {e(m.get("units"))}</span>' if 'line' in m else '')+f'</td><td><span data-price-value>{e(o["selection"])}</span></td><td><span data-price-value>{o["probability"]:.2%}</span></td><td><span class="price number" data-price-value data-american="{american(o["american_display"])}" data-decimal="{o["decimal_display"]}">{american(o["american_display"])}</span><span class="secondary" data-price-value>Decimal {o["decimal_display"]}</span></td><td><span data-price-value>'+badge('Within range' if o['fair_price_in_target_band'] else 'Outside range','green' if o['fair_price_in_target_band'] else 'gray')+f'</span></td><td>{self.sources(row,page,False)}</td></tr>'
            b+='</tbody></table></div><div class="market-foot"><p data-expiry-reason hidden><strong>Estimate withheld: stale evidence or elapsed start.</strong></p><strong>Settlement:</strong> '+e(p['markets'][0]['settlement'])+'. <strong>Bookmaker quote:</strong> unverified.<details><summary>Assumptions, inputs and withheld markets</summary><ul>'+''.join('<li>'+e(n)+'</li>' for n in p['notes'])+'</ul><p>Input IDs: '+e(', '.join(p['input_ids']))+'</p><ul>'+''.join(f'<li><strong>{e(w["market"])}</strong> — {e(w["reason"])}</li>' for w in p['withheld'])+'</ul><div class="inline-links">'+''.join(ext(self.c[s]['url'],publisher(self.c[s])) for s in p['markets'][0]['sources'])+'</div></details></div></section>'
        b+='<p id="no-results" class="no-results" hidden>No priced matches match these filters.</p><div class="panel pad prose"><h2 style="margin-top:0">Why many markets are blank</h2><p>Totals, handicaps, props, sets, frames and placements need distributions and settlement rules. A winner probability cannot supply them. <a href="flagged.html#market-gaps">See every category/market requirement →</a></p></div>'
        self.frame('Market explorer',page,b,'markets',description='Both sides of every supported market. No favorable-line search, hidden margin or price cap.')
    def predictions(self):
        b=f'<section class="hero-empty"><div class="empty-mark">{icon("shield",38)}</div><div><p class="eyebrow">0 HIGH-CONFIDENCE RELEASES</p><h2>No selection passes the release gates.</h2><p>A favorite is not automatically a high-confidence bet. We do not turn tip shares into probabilities, invent player news, or move a handicap until it reaches a desired percentage.</p></div></section><div class="grid-three">'
        for n,t,d in [('01','Independent evidence','Fresh official fixture details, relevant player/lineup availability, current form and recent match history, tied to retained evidence.'),('02','Measured reliability','A temporal holdout evaluation for this exact model and sport. No calibration artifact exists: calculated prices remain Low.'),('03','A real eligible price','Verified available odds and consistent settlement between −250 and +10000. An originated fair price is not an available offer or proof of value.')]:
            b+=f'<article class="step-card"><span class="step-num">GATE {n}</span><h3>{t}</h3><p>{d}</p></article>'
        b+='</div><div class="panel pad prose" style="margin-top:23px"><h2 style="margin-top:0">What will a released prediction contain?</h2><p>A clear selection and market, both participants, at least 30 original words, verified current form and recent match history, relevant player context, and official links. The prose must be specific to the matchup, not recycled. Unsupported details stay blank and prevent release.</p><p>No historical High label or prediction is carried forward. Inspect earlier claims in the <a href="archive.html">archive</a>.</p><div class="inline-links"><a href="markets.html">Low experimental estimates →</a><a href="analysis.html#research-notes">Sourced research notes →</a></div></div>'
        self.frame('High-confidence picks','predictions.html',b,'predictions',description='A deliberately empty release list is more useful than unsupported certainty.')
    def coverage_table(self,page):
        return table(['Category','Coverage','Captured','Price books','Limits / missing evidence','Official source'],[
            [f'<a href="{self.href("sports/"+c["slug"]+".html",page)}">{e(c["name"])}</a>',badge(c['status'],'amber'),str(c['captured_count']),str(c['priced_count']),e(c['note']),ext(c['official_url'],'Official lookup')] for c in self.s['coverage']])
    def review(self):
        page='flagged.html';a=self.audit
        b=self.notice('<strong>Review flags are public, not hidden.</strong> Gaps do not block a working site release. They do block unsupported facts, prices and High selections. Historical claims remain unverified.')
        b+=f'<nav class="subnav" aria-label="Review sections"><a href="#findings">Findings · {len(a["findings"])}</a><a href="#coverage">Coverage · 17</a><a href="#missing-fields">Field gaps</a><a href="#market-gaps">Market gaps</a><a href="audit/rows-01.html">Historic inventory · {a["counts"]["row_occurrences"]:,}</a></nav><section id="findings" class="findings">'
        for f in a['findings']:
            b+=f'<article class="finding" id="{f["id"]}"><div class="finding-top">{badge(f["severity"].title(),"red" if f["severity"]=="high" else "amber")}<span>{f["id"]} · {e(f["status"])}</span></div><h3>{e(f["title"])}</h3><p>{e(f["detail"])}</p><div class="finding-links">{ext(f["official_url"],"Official source / recheck")}'
            if f['repository_url']:b+=ext(f['repository_url'],str(f['file'])+(f':{f["line"]}' if f['line'] else ''))
            b+='</div></article>'
        b+='</section>'+section('Coverage register','Unknown is not zero. Every category remains partial or unverified.','coverage')+self.coverage_table(page)
        b+=section('Field gaps & source qualifications','A blank field has no accepted factual value.','missing-fields')+table(['Listing','Missing factual fields','Qualifications','Official evidence'],[[self.match_cell(r,page),e(', '.join(r['missing_fields'])),e(' '.join(r['notes'])),self.sources(r,page)] for r in self.rows if r['missing_fields'] or r['notes']])
        marketrows=[]
        for sport,markets in SPORT_MARKETS.items():
            counts=Counter(m['market'] for p in self.s['prices'] if self.fixture_map[p['fixture_id']]['sport']==sport for m in p['markets'])
            for market in markets:
                note='Experimental only; no calibration or available quote verified.' if counts[market] else MARKET_REQUIREMENTS[market]
                marketrows.append([e(SPORT_INDEX[sport]['name']),e(market),str(counts[market]),e(note),ext(SPORT_INDEX[sport]['official_url'],'Official lookup')])
        b+=section('Market investigation register','Unsupported market prices and selections stay blank.','market-gaps')+table(['Category','Market family','Originated rows','Missing evidence / constraint','Official lookup'],marketrows)
        self.frame('Flagged for Review',page,b,'review',description='Irregularities, exact repository locations, unconfirmed fields and source checks still needed.')
    def sources_page(self):
        b=self.notice('<strong>Evidence, not green ticks.</strong> Tool captures retain selected normalized excerpts, not complete raw responses or headers. HTTP captures retain byte hashes and JSON locators. Checksums prove stored integrity—not truth.')
        b+='<div class="subnav"><a href="verification.html">Field-by-field evidence</a><a href="#source-register">Source register</a><a href="#network">Refresh attempts</a><a href="data/current/session_import.json">Import JSON</a></div>'
        rows=[]
        for c in self.c.values():
            capture=f'<a class="tiny" href="data/current/evidence/{e(c["id"])}.json">{e(c["id"])}.json</a><span class="secondary">Stored SHA256 {c["sha256"][:12]}…</span>'
            capture+=f'<a class="tiny" href="{e(c["raw_path"])}">Raw response</a>' if c.get('raw_path') and (ROOT/c['raw_path']).is_file() else '<span class="secondary">Raw bytes / headers not retained</span>'
            rows.append([f'<strong>{e(publisher(c))}</strong><span class="secondary">{e(c["role"])} · {e(c["method"])}</span>',f'<span class="tiny">{stamp(c["observed_after"])}<br>through {stamp(c["observed_before"])}</span>',e(c['scope'])+'<span class="secondary">'+e(c.get('notes'))+'</span>',capture,ext(c['url'],publisher(c))])
        b+='<section id="source-register">'+table(['Publisher / role','Observed window (UTC)','Scope actually read','Capture / integrity','Publisher source'],rows)+'</section>'+section('Automated refresh attempts','Failed or unparsed requests never refresh fixture timestamps.','network')
        attempts=self.s['network_attempts']
        if attempts:
            b+=table(['Attempt','Time (UTC)','Status','Result / limitation','Source requested'],[[e(a.get('source_id','robots policy')),stamp(a.get('at')),badge(a['status'],'amber' if a['status']!='read' else 'gray'),e(a.get('error','Response retrieved; see adapter acceptance and field evidence, not a completeness assertion.')),ext(a['url'],'Requested publisher')] for a in attempts])
        else:b+='<div class="panel pad prose"><p>No autonomous HTTP run is attached. This selected import does not certify continuous coverage.</p></div>'
        self.frame('Sources & evidence','sources.html',b,'sources',description='What was read, when it was observed, which fields it supports, and what it does not establish.')
    def verification(self):
        page='verification.html';b=self.notice('<strong>Field-level claims only.</strong> Captured means present in the referenced official extraction. It does not prove live status or validate a model. Empty cells have no accepted value.')
        b+='<div class="inline-links" style="margin-bottom:20px"><a href="sources.html">Source capture register →</a><a href="data/current/snapshot.json">Canonical JSON →</a><a href="audit/rows-01.html">Historical claims (not accepted) →</a></div>'
        for r in self.s['fixtures']:
            f=r['facts'];label=f['event'] or f'{f["participant_a"] or ""} vs {f["participant_b"] or ""}'
            b+=f'<details class="panel row-detail" id="{e(r["id"])}"><summary>{e(label)}<small>{e(r["id"])} · {e(r["state"])}</small></summary>'
            rows=[]
            for k,v in f.items():
                ref=r['field_evidence'].get(k);sid=ref[0].split('#',1)[0] if ref else r['source_ids'][0]
                locator=(ref[0].replace('#',' / ')+' / '+k) if ref else 'No accepted value'
                rows.append([e(k),e(v),badge('Captured' if v is not None else 'Unverified','green' if v is not None else 'amber')+'<span class="secondary">'+e(locator)+'</span>',ext(self.c[sid]['url'],publisher(self.c[sid]))])
            b+=table(['Field','Accepted value','Status / observation locator','Official source'],rows)+f'<div class="quote"><strong>Observation window:</strong> {stamp(r["verified_after"])} through {stamp(r["verified_before"])}. <strong>Expiry:</strong> {stamp(r["expires_at"])}.<p>{e(" ".join(r["notes"]))}</p></div></details>'
        statrows=[]
        for r in self.s['statistics']:
            c=self.c[r['source_id']]
            statrows.append([e(r['team'])+f'<span class="secondary">{e(r["competition"])} · {e(r["as_of"])}</span>',str(r['games_played']),str(r['wins']),str(r['losses']),e(r.get('ot_losses')),f'{r["runs_scored"]} / {r["runs_allowed"]}' if 'runs_scored' in r else '',ext(c['url'],publisher(c))+'<span class="secondary">'+e(r['id'])+'</span>'])
        b+=section('Accepted statistical input observations','Season records—not last-match logs or player-availability claims.','statistics')+table(['Team / period','GP','W','L','OT loss','Runs for / against','Input ID / source'],statrows)
        self.frame('Field-level verification',page,b,'sources',description='Every factual cell is traceable. No blanket verified label is inherited from an old dataset.')
    def methodology(self):
        self.frame('Methodology','methodology.html',(ROOT/'site_templates/methodology.fragment').read_text(),'method',description='From source observation to independent estimate, with every limitation visible.')
    def analysis(self):
        c=self.s['counts'];b=self.kpis()+'<div class="grid-two"><section class="panel"><header class="panel-head"><div><h2>Where inputs support a price</h2><p>Priced books by category—not estimated coverage percentages</p></div></header><div class="chart">'
        maxval=max((x['priced_count'] for x in self.s['coverage']),default=1) or 1
        for x in sorted(self.s['coverage'],key=lambda x:-x['priced_count'])[:8]:
            b+=f'<div class="bar-item"><span>{e(x["name"])}</span><div class="bar-track"><div class="bar-fill" style="width:{x["priced_count"]/maxval*100:.1f}%"></div></div><span>{x["priced_count"]}</span></div>'
        b+=f'</div></section><section class="panel pad prose"><h2 style="margin-top:0">The denominator matters</h2><p>{c["captured_listings"]} captured entries include head-to-heads, doubles and event/session cards. They are not {c["captured_listings"]} verified betting opportunities.</p><p>{c["priced_matches"]} books produce {c["originated_markets"]} two-way markets and {c["originated_outcomes"]} outcome prices. Equal estimates have no arbitrary winner. No empirical calibration or ROI claim is available.</p><a href="data/current/snapshot.json">Complete calculation output →</a></section></div>'
        b+=section('Match-specific research notes','Original context for Low estimates—not High tips or invented recent results.','research-notes')
        notes=[('nhl-2026020154','Boston’s record, with the right denominator','Experimental preference: Boston Bruins, full-game winner including overtime and shootout. The captured NHL table has Boston at seven wins from ten games and Nashville at three wins from eight. Nashville’s three overtime losses count as defeats in this binary market, not extra wins. That distinction corrects an inconsistent archived record, but it does not verify the starting goaltenders or establish a calibrated betting edge. No High selection is released.'),('nhl-2026020163','Two strong records are not a mismatch','Experimental preference: Edmonton Oilers over Carolina Hurricanes, including overtime and shootout. Edmonton’s seven wins in nine games and Carolina’s eight in eleven both support strong season records in the captured table. After shrinking both small samples, the advantage is modest rather than decisive. No recent game-by-game sequence, lineup or goaltender evidence was captured to sharpen that comparison. The estimate remains Low confidence, not a claimed available bet.'),('mlb-849805','A season baseline, not a postseason preview','Experimental preference: Milwaukee Brewers over Tampa Bay Rays in the full-game research model. Captured regular-season totals show Milwaukee at 103–59 with 832 runs scored and 618 allowed; Tampa Bay is 98–64 with 736 scored and 650 allowed. Those aggregates provide a transparent baseline, but they do not tell us who starts this game or how either lineup is currently performing. Postseason form, pitcher availability and a real quote remain unverified.')]
        for fid,title,text in notes:
            row=self.fixture_map.get(fid)
            if not row:continue
            p=self.prices[fid];prefix='mlb-records-2026-' if fid.startswith('mlb') else 'nhl-standings-20261021-'
            # Authored notes may not follow new records without a fresh editorial check.
            if not p['markets'] or not p['input_ids'] or not all(i.startswith(prefix) for i in p['input_ids']):continue
            b+=f'<article class="finding" style="margin-bottom:15px" data-expires="{row["expires_at"]}" data-start="{row["facts"]["start_utc"]}"><div class="finding-top"><span class="badge low" data-conf-value>Low · research note</span><span>Captured records; not live player news</span></div><h3>{title}</h3><p data-price-value>{text}</p><div class="finding-links">'+''.join(ext(self.c[s]['url'],publisher(self.c[s])) for s in p['markets'][0]['sources'])+'</div></article>'
        b+='<div class="panel pad prose"><h2 style="margin-top:0">What the audit found</h2><p>Default ratings, unsupported confidence, clipped prices, timestamp ambiguity, expired schedules and inconsistent records. Fixes do not retroactively certify earlier desks.</p><div class="inline-links"><a href="flagged.html">All findings →</a><a href="audit/rows-01.html">Every detected historical row →</a></div></div>'
        self.frame('Analysis & findings','analysis.html',b,'analysis',description='Observed facts, modeling assumptions and betting confidence are different things.')
    def reverse(self):
        b=self.notice('<strong>Public-surface analysis only.</strong> No private API, member route, hidden JSON feed or access-control workaround. This sample is not an exhaustive live enumeration.')
        b+='''<article class="panel pad prose"><h2 style="margin-top:0">What the public interface exposes</h2><p>The inspected betting-tip sitemap supplies sport routes with category IDs and slugs. Event cards link using an <code>event_id</code> query parameter. A discovery key combines sport ID and event ID; a label is never official fixture verification.</p><pre><code>/betting-tips/{sport}/{sport_id}
/betting-tips/{sport}/{competition}/{sport_id}?event_id={event_id}</code></pre><p>Competition routes and pagination must be followed when explicitly linked. A hub is not the full competition universe. The bounded collector records unvisited links; blocked or JavaScript-only extraction does not prove zero fixtures.</p><h3>Tip shares are not probabilities</h3><p>The observed darts card displayed Gerwyn Price with 16 of 20 win tips (80%), and Niels Zonneveld with 14 of 18 (78% rounded). These are community selections, not calibrated likelihoods or bookmaker prices. They never feed the model.</p><h3>Respect robots</h3><p>The read policy disallows <code>/api/</code>, <code>/storage/app/json_data/</code>, private routes and <code>Python-urllib</code>. The Python client advertises and honors that identity. It declines denied requests rather than replacing its user agent or using a hidden endpoint. Retrieval-tool observations are a selected historical sample, not an automatic-refresh claim.</p><div class="inline-links">'''+ext('https://www.olbg.com/robots.txt','OLBG robots.txt')+ext('https://www.olbg.com/sitemap-betting-tips.xml','Public sitemap')+ext('https://www.olbg.com/betting-tips/Darts/15','Inspected darts cards')+'</div></article>'
        b+=section('Discovery-only events','Observed labels are claims. Accepted participant/start/selection fields remain blank.')
        discovery=load(CURRENT/'discovery.json') if (CURRENT/'discovery.json').exists() else {'events':[]}
        events=discovery.get('events',[]) or [{'event_id':'32325','sport':'darts','observed_label':'Gerwyn Price vs Rob Cross','url':'https://www.olbg.com/betting-tips/Darts/15?event_id=32325','official_source_url':SPORT_INDEX['darts']['official_url']},{'event_id':'32334','sport':'darts','observed_label':'Niels Zonneveld vs Cameron Menzies','url':'https://www.olbg.com/betting-tips/Darts/15?event_id=32334','official_source_url':SPORT_INDEX['darts']['official_url']}]
        b+=table(['Discovery label (unverified claim)','Sport / event ID','Accepted participants','Accepted UTC start','Selection / confidence','Publisher & official check'],[[e(ev['observed_label']),e(ev['sport'])+' / '+e(ev['event_id']),'','','','<div class="sources-stack">'+ext(ev['url'],'OLBG discovery claim')+ext(ev['official_source_url'],'Official lookup—not verified')+'</div>'] for ev in events])
        b+=section('Sport route map')+table(['Category','OLBG sport ID','Public discovery route','Official verification target'],[[e(s['name']),str(s['olbg_id']),ext(s['olbg_url'],'Public sport page'),ext(s['official_url'],'Official publisher')] for s in SPORT_INDEX.values()])
        self.frame('OLBG public discovery','reverse-engineering.html',b,'reverse',description='Public routes and tip-card semantics—not a hidden API integration.')
    def audit_pages(self):
        rows=self.audit['rows'];size=200;pages=max(1,math.ceil(len(rows)/size))
        for index in range(pages):
            page=f'audit/rows-{index+1:02d}.html';pager='<nav class="pager" aria-label="Audit pages">'+''.join(f'<span aria-current="page">{i+1}</span>' if i==index else f'<a href="rows-{i+1:02d}.html" aria-label="Audit page {i+1}">{i+1}</a>' for i in range(pages))+'</nav>'
            b=self.notice(f'<strong>Historical claims, not recertified facts.</strong> {len(rows):,} row occurrences across data, price books and mirrors. JSON aliases are labelled. Accepted current facts and selections remain blank.')
            b+=f'<div class="inline-links"><a href="../flagged.html">← Findings</a><a href="../data/current/audit.json">Full inventory JSON</a><a href="files.html">Every inspected file</a></div>{pager}<div class="filter-meta"><span>Rows {index*size+1:,}–{min((index+1)*size,len(rows)):,} of {len(rows):,}</span><span>Exact JSON pointers; file lines where located</span></div>'
            output=[]
            for r in rows[index*size:(index+1)*size]:
                url=(r['official_urls'][0] if r['official_urls'] else r['lookup_url']) or 'https://www.olbg.com/betting-tips'
                loc=f'<div class="path"><a href="{e(r["repository_url"])}">{e(r["file"])}'+(f':{r["line"]}' if r['line'] else '')+f'</a><span class="secondary">{e(r["pointer"])}</span>'+ (f'<span class="alias">Alias of {e(r["alias_of"])}</span>' if r['alias_of'] is not None else '')+'</div>'
                output.append([loc,'<div class="claim">'+e(r['observed_label'])+'<span class="secondary">'+e(r['record_id'])+' · '+e(r['kind'])+'</span></div>',e(r['observed_start_utc'])+'<span class="secondary">'+e(r['current_verification'])+'</span>'+ (badge('Stored start elapsed','amber') if r['stored_start_elapsed'] else ''),'',ext(url,'Cited source' if r['official_urls'] else 'Lookup only; not evidence')])
            b+=table(['File / exact location','Observed legacy claim','Stored start / current verification','Accepted facts / pick','Official source / lookup'],output,'audit-table')+pager
            self.frame('Historical row inventory',page,b,'review',description=f'Page {index+1} of {pages}. All entries remain inspectable, including duplicates and unresolved claims.',actions='<a class="button" href="../data/current/audit.json" download>'+icon('download',14)+' Full audit JSON</a>')
        b=self.notice('<strong>Structural checks are not source verification.</strong> Every tracked legacy JSON was decoded and Python file parsed. This does not certify every sentence; exact findings and evidence limits are public.')
        b+=table(['Inspected file','Lines','Detected rows','Parse status','Integrity hash','Official project source'],[[e(f['path']),str(f['line_count']),str(f['records']),e(f['status']),f['sha256'][:20]+'…',ext(f'{REPO}/blob/{self.audit["baseline"]}/{f["path"]}','Repository source')] for f in self.audit['files']])
        self.frame('Inspected file inventory','audit/files.html',b,'review',description=f'{len(self.audit["files"])} legacy JSON/Python files. Paths, counts and checksums—not factual green ticks.')
    def archive(self):
        entries=[('Prior main-root desk',str(ARCHIVE/'index.html'),'Root before canonical integration. Prior data and claims retained.'),('Release audit','release-review.html','Independent primary-row warnings from PR #74.'),('v3 research desk','v3/index.html','Historical model and predictions—not current.'),('Original desk mirror','f7fa77fc/index.html','Preserved legacy root mirror.'),('Documentation desk','docs/index.html','Earlier documentation/Pages build.')]
        for folder in ('2360a617','6a081cf6','7a5b5360','984d417f','9dfd0b48','a570c470','aa4e9dbf','c17a9192','ccb6bde2','ebfbd966','f71557b5'):entries.append(('Session '+folder,folder+'/index.html','Historical independent snapshot. Not recertified.'))
        for folder in sorted(ROOT.iterdir()):
            path=folder.name+'/index.html'
            if folder.is_dir() and not folder.name.startswith(('.', '_')) and folder.name not in ('site_templates','node_modules','archive') and (folder/'index.html').is_file() and not any(x[1]==path for x in entries):
                entries.append(('Preserved '+folder.name,path,'Additional historical namespace; not recertified.'))
        for report in sorted((ROOT/'reports').glob('*.html')):entries.append((report.stem.replace('_',' '),report.relative_to(ROOT).as_posix(),'Preserved parallel audit; inspect its own scope and as-of time.'))
        b=self.notice('<strong>Archive—not current picks.</strong> Older verified, High and upcoming labels are historical claims. Return to the canonical match list for this release.')
        b+=table(['Preserved desk / report','What it represents','Official project provenance'],[[f'<a href="{e(path)}">{e(name)} →</a>',e(note),ext(REPO+'/tree/'+self.revision+'/'+path,'Repository source')] for name,path,note in entries if (ROOT/path).is_file() or (self.out/path).is_file()])
        b+='<div class="panel pad prose" style="margin-top:20px"><h2 style="margin-top:0">No silent deletion or recertification</h2><p>The prior root HTML is copied to a dated archive with rewritten relative links and a warning. Original hashes are in its manifest. Parallel desks, datasets and code remain untouched.</p><p>The canonical workflow does not run old generators. The root <code>scripts/build_site.py</code> entrypoint delegates to the evidence-first build; it cannot silently reinstate historical picks.</p></div>'
        self.frame('Earlier snapshots','archive.html',b,'archive',description='Preserved work, separated from the current evidence-backed release.')
    def exports(self):
        path=self.out/'data/current';path.mkdir(parents=True,exist_ok=True)
        for p in CURRENT.rglob('*'):
            if not p.is_file() or p.suffix=='.tmp':continue
            target=path/p.relative_to(CURRENT)
            if p.resolve()!=target.resolve():target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
        output=io.StringIO(newline='');writer=csv.writer(output)
        writer.writerow(['id','sport','participant_a','participant_b','event','competition','date_in_source','start_utc','venue','evidence_state','experimental_selection','confidence','model_probability','fair_decimal','american_display','bookmaker_quote','official_urls','observed_after','observed_before','expires_at'])
        def safe(v):return "'"+v if isinstance(v,str) and v and v[0] in '=+-@\t\r' else v
        for r in self.s['fixtures']:
            f=r['facts'];p=self.prices[r['id']]
            writer.writerow([safe(v) for v in [r['id'],r['sport'],f['participant_a'],f['participant_b'],f['event'],f['competition'],f['date'],f['start_utc'],f['venue'],r['state'],p['selection'],p['confidence'],p['probability'],p['fair_decimal'],p['american_display'],None,' | '.join(self.c[s]['url'] for s in r['source_ids']),r['verified_after'],r['verified_before'],r['expires_at']]])
        (path/'matches.csv').write_text(output.getvalue(),encoding='utf-8-sig')
    def run(self):
        assets=self.out/'assets';assets.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'site_templates/current.css',assets/'current-style.css');shutil.copyfile(ROOT/'site_templates/current.js',assets/'current-app.js')
        (assets/'current-mark.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40"><rect width="40" height="40" rx="11" fill="#12563d"/><path d="M11 28V18m9 10V10m9 18V16" stroke="#fff" stroke-width="3" stroke-linecap="round"/></svg>')
        self.exports();self.dashboard();self.matches();self.sports();self.markets();self.predictions();self.review();self.sources_page();self.verification();self.methodology();self.analysis();self.reverse();self.audit_pages();self.archive()
        for alias,target in [('matches.html','picks.html'),('all.html','picks.html'),('coverage.html','flagged.html#coverage')]:self.frame('Research desk',alias,'<div class="hero-empty"><div><h2>This view has a canonical home.</h2><p><a href="'+target+'">Continue to the current research view →</a></p></div></div>','matches',description='Legacy route preserved; no old predictions reinstated.')
        (self.out/'.nojekyll').touch()
        (self.out/'404.html').write_text(f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Page not found · OLBG Research</title><body style="font:16px system-ui;background:#f5f8f6;color:#19362b;padding:10vh 8vw"><h1>That page is not in this snapshot.</h1><p>A missing page implies no result or betting selection.</p><p><a href="{LIVE}">Return to the research desk →</a></p></body></html>')
        pages=['index.html','picks.html','markets.html','predictions.html','sports.html','flagged.html','sources.html','verification.html','methodology.html','analysis.html','reverse-engineering.html','archive.html','matches.html','all.html','coverage.html','404.html']
        pages += [p.relative_to(self.out).as_posix() for p in (self.out/'sports').glob('*.html')]+[p.relative_to(self.out).as_posix() for p in (self.out/'audit').glob('*.html')]
        manifest={'generated_at':self.s['generated_at'],'revision':self.revision,'canonical':True,'complete':False,'counts':self.s['counts'],'input_sha256':self.s['input_sha256'],'audit_sha256':digest(self.audit),'pages':sorted(pages)}
        save(self.out/'data/current/site-manifest.json',manifest);return manifest


def archive_root():
    dest=ROOT/ARCHIVE
    if (dest/'manifest.json').exists():return
    if not (ROOT/'index.html').exists():raise ValueError('No prior root to archive')
    if 'current-style.css' in (ROOT/'index.html').read_text():raise ValueError('Refusing to archive canonical output as legacy')
    paths=list(ROOT.glob('*.html'))+list((ROOT/'sports').glob('*.html'))+[p for p in (ROOT/'assets').rglob('*') if p.is_file() and not p.name.startswith('current-')]
    mapping={p.resolve():dest/p.relative_to(ROOT) for p in paths};manifest=[]
    for p,target in mapping.items():
        target.parent.mkdir(parents=True,exist_ok=True);raw=p.read_bytes()
        if p.suffix=='.html':
            def rewrite(m):
                attr,q,value=m[1],m[2],html.unescape(m[3]);u=urlsplit(value)
                if u.scheme or u.netloc or not u.path:return m[0]
                original=(ROOT/u.path.lstrip('/') if u.path.startswith('/') else p.parent/u.path).resolve()
                try:original.relative_to(ROOT)
                except ValueError:return m[0]
                new=mapping.get(original,original);rel=os.path.relpath(new,target.parent).replace(os.sep,'/')
                return f'{attr}={q}{html.escape(urlunsplit(("","",rel,u.query,u.fragment)),quote=True)}{q}'
            text=re.sub(r'\b(href|src)\s*=\s*(["\'])(.*?)\2',rewrite,raw.decode('utf-8'),flags=re.I)
            back=os.path.relpath(ROOT/'index.html',target.parent).replace(os.sep,'/')
            warning=f'<aside style="padding:14px 22px;background:#fff0d6;color:#653d10;border-bottom:2px solid #e0ba77;font:14px/1.5 system-ui"><strong>Historical archive — not current picks.</strong> Original claims have not been recertified. <a href="{back}" style="color:#254b3b">Canonical research desk →</a></aside>'
            text=re.sub(r'(<body\b[^>]*>)',lambda m:m[1]+warning,text,count=1,flags=re.I);target.write_text(text)
        else:target.write_bytes(raw)
        manifest.append({'original':p.relative_to(ROOT).as_posix(),'archive':target.relative_to(ROOT).as_posix(),'original_sha256':digest(raw),'archived_sha256':digest(target.read_bytes())})
    save(dest/'manifest.json',{'at':iso(now_utc()),'revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'note':'HTML links rewritten and archive warning inserted. Other assets copied verbatim. Legacy data stays at original paths.','files':manifest})


def stage_existing(out):
    if out.resolve()==ROOT.resolve():return
    if out.resolve()==(ROOT/'_site').resolve() and out.exists():shutil.rmtree(out)
    out.mkdir(parents=True,exist_ok=True)
    for rel in subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines():
        source=ROOT/rel
        if not source.is_file() or rel.startswith(('.git','node_modules/','_site/')):continue
        target=out/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
    if (ROOT/ARCHIVE).exists():shutil.copytree(ROOT/ARCHIVE,out/ARCHIVE,dirs_exist_ok=True)


def build_site(out=ROOT,at=None,archive=False):
    out=Path(out).resolve()
    if out==ROOT/'.git' or ROOT/'.git' in out.parents:raise ValueError('Forbidden output directory')
    if archive:archive_root()
    at=at or now_utc();snapshot=assemble(at);audit=build_audit(at);stage_existing(out)
    manifest=Site(snapshot,audit,out).run()
    print(f'Built {len(manifest["pages"])} canonical pages at {out}; '+json.dumps(snapshot['counts']));return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT);p.add_argument('--at');p.add_argument('--archive-root',action='store_true');a=p.parse_args()
    build_site(a.out,parse_time(a.at) if a.at else None,a.archive_root)
