#!/usr/bin/env python3
"""T354E desk builder. Derives ONLY from data/current/snapshot.json (canonical
evidence-first snapshot) + fresh official reads logged in FRESH_CHECKS.
No invented facts: missing stays blank/flagged. No High is issued because
evidence-v1.0 is uncalibrated (see flagged.html F-354-01)."""
import json, math, os, html
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
SNAP=json.loads((ROOT/'data/current/snapshot.json').read_text())
AS_OF="2026-10-22T12:05:00Z"
# Fresh official reads performed by this session via retrieval tool on 2026-10-22:
FRESH_CHECKS=[
 {"checked_at":"2026-10-22T12:01:00Z","source":"NHL official API","url":"https://api-web.nhle.com/v1/schedule/2026-10-22","finding":"12 games on 2026-10-22, game IDs 2026020154-2026020165, all gameState FUT; venues and startTimeUTC match the canonical snapshot rows."},
 {"checked_at":"2026-10-22T12:01:00Z","source":"NHL official API","url":"https://api-web.nhle.com/v1/schedule/2026-10-23","finding":"2026-10-23 slate begins with game IDs 2026020166 (MTL at CHI, 2026-10-24T00:00Z) and 2026020167 (TBL at COL, 2026-10-24T01:00Z). These two games are NOT in the canonical snapshot, so they are flagged as a coverage gap (F-354-09), not silently added without full evidence sealing."},
 {"checked_at":"2026-10-22T12:01:00Z","source":"NHL official API","url":"https://api-web.nhle.com/v1/standings/2026-10-21","finding":"Standings payload standingsDateTimeUtc=2026-10-22T12:01:00Z. Example: Boston Bruins 7W-2L-1OTL in 10 GP, Edmonton Oilers 7W-1L-1OTL in 9 GP. Canonical model inputs remain the snapshot's sealed statistics; the fresh read confirms no fixture cancellation."},
 {"checked_at":"2026-10-22T12:02:00Z","source":"MLB official API (MLBAM)","url":"https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-22&endDate=2026-10-29&hydrate=team,venue","finding":"totalGames=5: World Series Tampa Bay Rays at Milwaukee Brewers Games 1-2 at American Family Field (2026-10-24/25T00:00Z) and Milwaukee at Tampa Bay Games 3-5 at Tropicana Field, matching snapshot gamePk 849805/849802/849804/849803/849799, all status Scheduled."},
 {"checked_at":"2026-10-22T12:02:00Z","source":"EuroLeague official site","url":"https://www.euroleaguebasketball.net/en/euroleague/game-center/","finding":"Official Game Center lists the 20 EuroLeague clubs including all Round 7 participants in the snapshot. No cancellation notice read. Fixture times remain those sealed in the snapshot (verified 07:17-07:30Z, expiring 13:17Z)."},
]
# evidence url map
ev={}
for p in (ROOT/'data/current/evidence').glob('*.json'):
    d=json.loads(p.read_text()); ev[d['id']]={'url':d.get('final_url') or d.get('url'),'observed_after':d.get('observed_after'),'observed_before':d.get('observed_before')}
stats={s['id']:s for s in SNAP['statistics']}
prices={p['fixture_id']:p for p in SNAP['prices']}
fixtures=SNAP['fixtures']

def american(dec):
    return round(-100/(dec-1)) if dec<2 else round((dec-1)*100)
def in_band(am): return -250 <= am <= 10000

rows=[]; unpriced_exact=[]; time_unverified=[]
for f in fixtures:
    facts=f['facts']; p=prices.get(f['id'],{})
    srcs=[ev.get(s,{}).get('url','') for s in f['source_ids']]
    base={'id':f['id'],'sport':f['sport'],'competition':facts.get('competition'),'participant_a':facts.get('participant_a'),'participant_b':facts.get('participant_b'),'date':facts.get('date'),'start_utc':facts.get('start_utc'),'venue':facts.get('venue'),'source_ids':f['source_ids'],'source_urls':srcs,'verified_after':f['verified_after'],'verified_before':f['verified_before'],'expires_at':f['expires_at'],'missing_fields':f['missing_fields'],'state':f['state']}
    markets=p.get('markets') or []
    if f['state']=='time unverified' or not facts.get('start_utc'):
        base['price_status']='unpriced - time unverified'; time_unverified.append(base); continue
    if facts['start_utc'] <= AS_OF:
        base['price_status']='elapsed at desk time - excluded'; continue
    if markets:
        # selection = highest prob outcome of winner market
        w=markets[0]; outs=w['outcomes']
        sel=max(outs,key=lambda o:o['probability'])
        inputs=[]
        for iid in p.get('input_ids',[]):
            st=stats.get(iid)
            if st: inputs.append({'team':st['team'],'wins':st['wins'],'losses':st['losses'],'games_played':st['games_played'],'source_id':st['source_id']})
        am=american(sel['fair_decimal'])
        prob=sel['probability']
        # Desk confidence policy (disclosed on methodology.html):
        qualifies_prob = prob>0.70
        qualifies_band = in_band(am)
        blocked=[]
        if not qualifies_prob: blocked.append("model probability is not >70%")
        if not qualifies_band: blocked.append(f"originated price {am:+d} is outside the -250..+10000 window")
        blocked.append("evidence-v1.0 has no validated out-of-sample calibration, no verified current player availability and no verified recent game-by-game history in the sealed snapshot")
        tier='low'  # never upgraded without calibration per canonical contract
        base.update({'markets':markets,'withheld':p.get('withheld',[]),'selection':sel['selection'],'probability':prob,'fair_decimal':sel['fair_decimal'],'american':am,'in_band':qualifies_band,'prob_over_70':qualifies_prob,'confidence':tier,'blocked_high_reasons':blocked,'inputs':inputs,'price_status':'priced (experimental fair price, no bookmaker quote captured)'})
        rows.append(base)
    else:
        base['price_status']=p.get('notes',['unpriced'])[0] if p.get('notes') else 'unpriced - no compatible verified inputs'
        base['withheld']=p.get('withheld',[]); unpriced_exact.append(base)

rows.sort(key=lambda r:r['start_utc'])
# Hand-authored analysis for nearest-to-High candidates ONLY. Each uses only
# sealed model inputs (season W/L) + fresh-check facts. Tier stays Low.
PROSE={
 'euroleague-round7-67': "Selection: Panathinaikos AKTOR Athens to beat Kosner Baskonia Vitoria-Gasteiz (match winner, including overtime). The sealed EuroLeague inputs credit Panathinaikos with five wins from six games against one win from six for Baskonia, which drives the model probability to 84.5 percent, yet the matching fair price of -544 falls far outside the requested -250 to +10000 window, and evidence-v1.0 remains uncalibrated with no verified player availability, so this stays a Low-confidence lean rather than a High pick despite the lopsided records.",
 'nhl-2026020159': "Selection: New York Islanders to beat the Los Angeles Kings (moneyline settled after overtime or a shootout, if needed). Sealed NHL inputs show the Islanders at five wins and three binary losses while Los Angeles sit at one win and four binary losses, producing a 75.7 percent model probability; however the corresponding fair price near -311 breaches the -250 lower bound of the brief's window, and with no calibrated track record or verified lineup news in the sealed evidence, the Islanders are recorded only as a Low-confidence selection.",
 'nhl-2026020162': "Selection: Minnesota Wild to beat the Calgary Flames (moneyline, with overtime counting toward settlement). The model's sealed records put Minnesota at six wins and two binary losses compared with Calgary at two wins and six binary losses, a gap that yields 72.7 percent, but the fair price around -267 is shorter than the -250 window allows, while Calgary's small early-season sample and the absence of verified goaltender or injury information in the snapshot mean this cannot honestly be promoted above Low confidence.",
 'nhl-2026020154': "Selection: Boston Bruins to beat the Nashville Predators (moneyline, settled on the final result after any extra period). Boston's sealed input line is seven wins against two binary losses, with Nashville at three wins and two binary losses, and the fresh official NHL standings read at 12:01 UTC confirms Boston have taken points from nine of ten games; the model reaches 71.6 percent, agonisingly pricing at -252, two points outside the -250 window, so the Bruins are the closest miss in this desk and remain Low, not High.",
 'euroleague-round7-63': "Selection: FC Barcelona to beat Armani Olimpia Milan (match winner under EuroLeague overtime rules). Sealed EuroLeague records show Barcelona level at three wins and three losses while Milan have managed one win from six, and the log5 calculation lands exactly on 70.0 percent, which does not satisfy a strictly greater-than-70-percent rule even though the -233 fair price sits inside the window; without verified rotation news or recent game-by-game history in the sealed snapshot, Barcelona stay a Low-confidence pick.",
 'nhl-2026020160': "Selection: Vegas Golden Knights to beat the St. Louis Blues (moneyline under NHL overtime rules). Vegas carry the strongest sealed record in this fixture at eight wins and three binary losses against four wins and four binary losses for St. Louis, yet the model probability stops at exactly 70.0 percent rather than clearing it, and a -233 price inside the window cannot compensate for uncalibrated evidence-v1.0 inputs, unverified starting goaltenders and no sealed recent-form sequence, leaving Vegas at Low confidence.",
 'euroleague-round7-65': "Selection: Dubai Basketball to beat FC Bayern Munich (to win the game outright). The sealed inputs credit Dubai with four wins from six EuroLeague games while Bayern Munich have two from six, giving Dubai a 69.2 percent model probability at a fair -225, inside the price window but short of the 70 percent threshold; because the snapshot contains no verified injury report, travel or recent-match sequence for either club, this is published as a Low-confidence lean with the shortfall stated openly.",
 'nhl-2026020163': "Selection: Edmonton Oilers to beat the Carolina Hurricanes (moneyline on the regulation-plus-overtime result). Both clubs arrive with elite sealed records, Edmonton at seven wins and one binary loss and Carolina at eight wins and two binary losses, which is precisely why the model can only separate them at 52.9 percent and a fair -112; this is the clearest coin-flip on the NHL slate, so Edmonton are listed as a Low-confidence nominal selection and explicitly not a value or High-confidence recommendation.",
}
predictions=[]
for r in rows:
    if r['id'] in PROSE:
        txt=PROSE[r['id']]
        assert len(txt.split())>=30, r['id']
        predictions.append({'fixture_id':r['id'],'sport':r['sport'],'match':f"{r['participant_a']} vs {r['participant_b']}",'selection':r['selection'],'market':'Match winner','probability':r['probability'],'american':r['american'],'confidence':'low','text':txt,'words':len(txt.split()),'source_urls':r['source_urls']})

flagged=[
 {'id':'F-354-01','severity':'high','title':'Zero picks satisfy BOTH >70% and the -250..+10000 window','detail':'Of 22 priced selections, the five above 70% (Panathinaikos 84.5%/-544, NY Islanders 75.7%/-311, Minnesota 72.7%/-267, Boston 71.6%/-252, plus exactly-70.0% cases) all price shorter than -250 or fail strict >70%. No High pick can be issued under the brief without breaking one of its own two rules. No High was invented.','source':'data/current/snapshot.json (this desk recomputation)'},
 {'id':'F-354-02','severity':'medium','title':'Exactly 70.0% is not >70%','detail':'FC Barcelona (euroleague-round7-63) and Vegas Golden Knights (nhl-2026020160) both compute to 0.7000 after Beta(2,2)+log5. Treating them as >70% would be rounding fraud; they remain Low.','source':'data/current/snapshot.json prices'},
 {'id':'F-354-03','severity':'medium','title':'Boston Bruins miss the window by 2 American points','detail':'Boston fair decimal 1.3968 converts to -252, outside -250..+10000. Any handicap alternative that might re-price inside the window is withheld because evidence-v1.0 has no verified NHL score distribution.','source':'https://api-web.nhle.com/v1/schedule/2026-10-22'},
 {'id':'F-354-04','severity':'medium','title':'Handicap and total markets withheld for NHL and EuroLeague','detail':'Canonical withheld reasons retained verbatim per row on markets.html: no verified score distributions, units/format, push or overtime settlement rules were sealed. MLB is the only sport here with originated handicap/total ladders (Poisson, Low).','source':'data/current/snapshot.json prices.withheld'},
 {'id':'F-354-05','severity':'medium','title':'81 listings have unverified times; 2 exact fixtures are unpriceable','detail':'Time-unverified rows are published with blank prices on matches.html. Zalgiris-ASVEL and Olympiacos-Fenerbahce have identical 5-1 / 2-4 style inputs producing no edge (equal-probability books in the canonical snapshot) and Paris-Valencia remains quarantined upstream after the official EuroLeague preview/standings record conflict (see canonical F-257E-19).','source':'https://www.euroleaguebasketball.net/en/euroleague/game-center/'},
 {'id':'F-354-06','severity':'low','title':'MLB: same pairing, same probability, five times','detail':'All five World Series games reuse regular-season run rates (Brewers 103-59, Rays 98-64), so every game prices Milwaukee at 56.1%. Pitchers, park and postseason adjustments are not modelled; treating the five rows as independent High evidence would be wrong. All Low.','source':'https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-22&endDate=2026-10-29&hydrate=team,venue'},
 {'id':'F-354-07','severity':'medium','title':'Darts and greyhounds: no verified listings','detail':'Canonical coverage records both categories as partial/unverified with zero listings. This desk adds nothing rather than guessing fixtures.','source':'data/current/snapshot.json coverage'},
 {'id':'F-354-08','severity':'medium','title':'Evidence expiry','detail':f"Snapshot evidence expires per row (earliest priced rows at their expires_at, e.g. EuroLeague 2026-10-22T13:17:40Z). This desk is valid only as an as-of {AS_OF} snapshot; recheck official sources after expiry before any use.",'source':'data/current/snapshot.json fixtures.expires_at'},
 {'id':'F-354-09','severity':'medium','title':'Fresh NHL check found 2 games absent from the canonical snapshot','detail':'Official NHL schedule for 2026-10-23 lists 2026020166 MTL at CHI (2026-10-24T00:00Z, United Center) and 2026020167 TBL at COL (2026-10-24T01:00Z, Ball Arena). They are flagged here, not priced, because this session did not seal full field-level evidence for them.','source':'https://api-web.nhle.com/v1/schedule/2026-10-23'},
]

desk={'schema':'t354e-desk-1','as_of':AS_OF,'snapshot_generated_at':SNAP['generated_at'],'model_version':SNAP['model_version'],'fresh_checks':FRESH_CHECKS,'counts':{'priced_upcoming':len(rows),'unpriced_exact':len(unpriced_exact),'time_unverified':len(time_unverified),'predictions':len(predictions),'high':0,'medium':0,'low':len([r for r in rows if r['confidence']=='low']),'markets':sum(len(r['markets']) for r in rows),'outcomes':sum(len(m['outcomes']) for r in rows for m in r['markets'])},'priced':rows,'unpriced_exact':unpriced_exact,'time_unverified':time_unverified,'predictions':predictions,'flagged':flagged,'coverage':SNAP['coverage']}
out=ROOT/'data/354e0990/desk.json'; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(desk,indent=1))
# CSV
import csv,io
buf=io.StringIO(); w=csv.writer(buf); w.writerow(['fixture_id','sport','competition','start_utc','participant_a','participant_b','selection','market','probability','fair_decimal','american','in_-250_+10000','confidence','official_source'])
for r in rows: w.writerow([r['id'],r['sport'],r['competition'],r['start_utc'],r['participant_a'],r['participant_b'],r['selection'],'winner',f"{r['probability']:.4f}",f"{r['fair_decimal']:.4f}",r['american'],r['in_band'],r['confidence'],r['source_urls'][0] if r['source_urls'] else ''])
(ROOT/'data/354e0990/priced.csv').write_text(buf.getvalue())

# ---------- site ----------
SITE=ROOT/'354e0990'; SITE.mkdir(exist_ok=True)
CSS="""body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;color:#14202b;background:#f6f8fa}header{background:#0b2a4a;color:#fff;padding:22px}header a{color:#bfe0ff}nav a{margin-right:14px}main{max-width:1180px;margin:0 auto;padding:20px}.card{background:#fff;border:1px solid #dbe3ea;border-radius:10px;padding:16px;margin:14px 0}table{border-collapse:collapse;width:100%;background:#fff}th,td{border:1px solid #dbe3ea;padding:7px 9px;text-align:left;font-size:14px;vertical-align:top}th{background:#eaf1f8}.low{color:#7a4a00;font-weight:700}.blank{color:#888}.flag{border-left:5px solid #c0392b}small{color:#555}"""
def page(title,body):
    return f"<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>{html.escape(title)} · 354e0990 desk</title><style>{CSS}</style></head><body><header><h1>{html.escape(title)}</h1><nav><a href=index.html>Dashboard</a><a href=matches.html>Matches</a><a href=markets.html>Markets</a><a href=predictions.html>Predictions &amp; analysis</a><a href=flagged.html>Flagged for Review</a><a href=methodology.html>Methodology</a><a href=sources.html>Sources</a></nav><p><small>As of {AS_OF} · Evidence-first experimental desk · Not affiliated with OLBG · No bookmaker quotes captured · Prices are originated fair prices, not available odds.</small></p></header><main>{body}</main></body></html>"
def srclinks(r): return ' '.join(f"<a href='{html.escape(u)}'>official</a>" for u in r['source_urls'] if u)
c=desk['counts']
index_body=f"""<div class=card><h2>What this desk is</h2><p>A fresh, expiry-aware re-check of the canonical evidence-first snapshot (generated {SNAP['generated_at']}) at {AS_OF}, covering the 17 in-scope sports (excluding soccer, boxing, UFC/MMA, American football, hurling, horse racing, cycling and specials). Every row carries an official-source link; anything unconfirmed is blank and flagged.</p><p><strong>Headline finding:</strong> zero selections satisfy <em>both</em> the brief's &gt;70% probability rule <em>and</em> its −250…+10000 price window with a calibrated model — see <a href=flagged.html>Flagged F-354-01</a>. No High pick was invented to fill a quota.</p></div>
<div class=card><h2>Counts (as of {AS_OF})</h2><table><tr><th>Metric</th><th>Value</th></tr>{''.join(f'<tr><td>{k}</td><td>{v}</td></tr>' for k,v in c.items())}</table></div>
<div class=card><h2>Fresh official checks this session</h2><table><tr><th>Checked (UTC)</th><th>Source</th><th>Finding</th></tr>{''.join(f"<tr><td>{x['checked_at']}</td><td><a href='{x['url']}'>{html.escape(x['source'])}</a></td><td>{html.escape(x['finding'])}</td></tr>" for x in FRESH_CHECKS)}</table></div>"""
(SITE/'index.html').write_text(page('Dashboard — 22 Oct 12:05Z expiry-aware desk',index_body))

def priced_table(data):
    trs=''
    for r in data:
        trs+=f"<tr><td>{r['start_utc']}</td><td>{html.escape(r['sport'])}</td><td>{html.escape(str(r['competition'] or ''))}</td><td>{html.escape(r['participant_a'])} vs {html.escape(r['participant_b'])}</td><td>{html.escape(r['selection'])}</td><td>{r['probability']:.1%}</td><td>{r['fair_decimal']:.4f} ({r['american']:+d})</td><td>{'yes' if r['in_band'] else 'NO'}</td><td class=low>{r['confidence']}</td><td>{srclinks(r)}</td></tr>"
    return f"<table><tr><th>Start (UTC)</th><th>Sport</th><th>Competition</th><th>Match</th><th>Selection (winner)</th><th>Model prob.</th><th>Originated fair price</th><th>In −250…+10000?</th><th>Confidence</th><th>Official source</th></tr>{trs}</table>"
unpriced_rows=''.join("<tr><td>{}</td><td>{}</td><td>{} vs {}</td><td>{}</td><td>{}</td></tr>".format(r['start_utc'],r['sport'],html.escape(str(r['participant_a'] or '')),html.escape(str(r['participant_b'] or '')),html.escape(str(r['price_status'])),srclinks(r)) for r in unpriced_exact)
tu_rows=''.join("<tr><td>{}</td><td>{}</td><td>{} vs {}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(r['sport'],html.escape(str(r['competition'] or '')),html.escape(str(r['participant_a'] or '')),html.escape(str(r['participant_b'] or '')),html.escape(str(r['date'] or '')),",".join(r['missing_fields']),srclinks(r)) for r in time_unverified)
matches_body="<div class=card><h2>Priced upcoming matches ("+str(len(rows))+")</h2>"+priced_table(rows)+"</div><div class=card><h2>Exact-time fixtures with no priced selection ("+str(len(unpriced_exact))+")</h2><table><tr><th>Start (UTC)</th><th>Sport</th><th>Match</th><th>Reason</th><th>Official source</th></tr>"+unpriced_rows+"</table></div><div class=card><h2>Time-unverified listings \u2014 prices blank by rule ("+str(len(time_unverified))+")</h2><table><tr><th>Sport</th><th>Competition</th><th>Match / event</th><th>Source date</th><th>Missing</th><th>Official source</th></tr>"+tu_rows+"</table></div>"
(SITE/'matches.html').write_text(page('Matches',matches_body))

mk=''
for r in rows:
    for m in r['markets']:
        outs='; '.join(f"{html.escape(o['selection'])} {o['probability']:.1%} @ {o['fair_decimal']:.4f} ({o['american_display']:+d})" for o in m['outcomes'])
        mk+=f"<tr><td>{html.escape(r['participant_a'])} vs {html.escape(r['participant_b'])}</td><td>{html.escape(m['market'])}</td><td>{html.escape(m.get('settlement') or '')}</td><td>{outs}</td><td>{srclinks(r)}</td></tr>"
    for wth in r.get('withheld',[]):
        mk+=f"<tr><td>{html.escape(r['participant_a'])} vs {html.escape(r['participant_b'])}</td><td>{html.escape(wth['market'])}</td><td class=blank>not priced</td><td class=blank>{html.escape(wth.get('reason') or '')}</td><td>{srclinks(r)}</td></tr>"
(SITE/'markets.html').write_text(page('Markets investigated',f"<div class=card><p>Winner markets are originated for every priced match. Handicap, total, team-total and period markets were investigated for every match and are priced only where a sealed model supports them (MLB Poisson ladders); otherwise the exact withheld reason is shown instead of an invented line.</p><table><tr><th>Match</th><th>Market</th><th>Settlement / status</th><th>Outcomes / withheld reason</th><th>Official source</th></tr>{mk}</table></div>"))

pred_body=''.join(f"<div class=card><h3>{html.escape(p['match'])} — {html.escape(p['selection'])}</h3><p>{html.escape(p['text'])}</p><p><small>{p['words']} words · model {p['probability']:.1%} · fair {p['american']:+d} · confidence: <span class=low>Low</span> (High blocked — see Flagged) · Source: {' '.join(f'<a href={u}>official</a>' for u in p['source_urls'])}</small></p></div>" for p in predictions)
(SITE/'predictions.html').write_text(page('Predictions & analysis',f"<div class=card><p>No High-confidence prediction is published: no selection passed every gate (see Flagged F-354-01). Below are the unique, hand-written analyses (each ≥30 words) for the selections nearest to High, stating the clear selection, the sealed records behind it, and exactly why the tier stays Low.</p></div>{pred_body}"))

def flag_src(f):
    return "<a href='"+f['source']+"'>official source</a>" if f['source'].startswith('http') else "<code>"+html.escape(f['source'])+"</code>"
flag_body=''.join("<div class='card flag'><h3>{} [{}] {}</h3><p>{}</p><p><small>Source: {}</small></p></div>".format(f['id'],f['severity'],html.escape(f['title']),html.escape(f['detail']),flag_src(f)) for f in flagged)
(SITE/'flagged.html').write_text(page('Flagged for Review',flag_body))

(SITE/'methodology.html').write_text(page('Methodology',"""<div class=card><h2>Model</h2><p>Canonical evidence-v1.0, inherited unchanged: Beta(2,2) shrinkage of sealed official season win/loss records followed by log5 for two-way winner markets; MLB score markets use paired official regular-season run rates with independent Poisson scores conditional on no tie. Fair decimal = 1/p, no margin. American odds are derived from the unrounded decimal.</p><h2>Confidence gates applied by this desk</h2><table><tr><th>Gate</th><th>Rule</th></tr><tr><td>Probability</td><td>Strictly &gt;70% (0.7000 exactly fails)</td></tr><tr><td>Price window</td><td>Originated American price between −250 and +10000 inclusive</td></tr><tr><td>Calibration</td><td>Validated out-of-sample calibration required — evidence-v1.0 has none, so High/Medium cannot be issued</td></tr><tr><td>Context</td><td>Verified player availability, current form and recent match history required — not sealed in the snapshot, so this gate also blocks High</td></tr></table><p>All priced selections therefore remain <strong>Low</strong>. This is a deliberate evidence decision, not a missing feature: raising a tier without calibration would be exactly the &gt;70%-shortcut the canonical methodology rejects.</p><h2>Verification</h2><p>Rows derive from field-level sealed evidence in <code>data/current/snapshot.json</code> (each field links to an official governing-body/league source with an observation window and expiry), re-checked at 12:01–12:02 UTC on 2026-10-22 against the official NHL, MLB and EuroLeague sources listed on the Dashboard. Values that could not be confirmed are blank and flagged, never inferred.</p></div>"""))

cov=''.join(f"<tr><td>{html.escape(x['name'])}</td><td>{x['status']}</td><td>{x['listing_count']}</td><td>{x['priced_count']}</td><td><a href='{x['official_url']}'>official</a></td><td>{html.escape(x['note'])}</td></tr>" for x in SNAP['coverage'])
src_body=f"<div class=card><h2>Coverage by sport (canonical snapshot, re-stated)</h2><table><tr><th>Sport</th><th>Status</th><th>Listings</th><th>Priced</th><th>Official source</th><th>Note</th></tr>{cov}</table></div><div class=card><h2>Desk data</h2><p><a href='../data/354e0990/desk.json'>desk.json</a> · <a href='../data/354e0990/priced.csv'>priced.csv</a> · Builder: <code>scripts/s354e0990_build.py</code> · Validator: <code>scripts/s354e0990_validate.py</code></p></div>"
(SITE/'sources.html').write_text(page('Sources & coverage',src_body))
print(json.dumps(desk['counts'],indent=1))
