#!/usr/bin/env python3
"""Build this independent, evidence-gated desk. Never modifies canonical inputs.

Usage: python3 scripts/se455acb16_build.py [--at UTC] [--out DIRECTORY]
--at is only a deterministic evaluation clock, never a retrieval timestamp.
"""
from __future__ import annotations
import argparse
import ast
import csv
import html
import io
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from se455acb16_data import (assemble_inputs,SPORTS,SPORT_NAMES,SPORT_ORDER,OLBG_HUBS,
    OBSERVED_AFTER,OBSERVED_BEFORE,OFFICIAL_HOSTS,digest)
from se455acb16_model import (originate,fixture_state,parse_time,iso,FIXTURE_TTL,ASSUMPTIONS,
    MARKET_REQUIREMENTS,SPORT_MARKETS,VERSION)
from se455acb16_predictions import PREDICTIONS,RESEARCH_NOTES

NAV=[("index.html","Overview"),("matches.html","Match register"),("markets.html","Market explorer"),
     ("high-confidence.html","Top-five & confidence"),("predictions.html","Research notes"),
     ("coverage.html","Sports & coverage"),("flagged.html","Flagged for Review"),
     ("verification.html","Field evidence"),("sources.html","Sources"),
     ("analysis.html","Analysis"),("methodology.html","Methodology"),
     ("reverse-engineering.html","OLBG discovery"),("repo-audit.html","Repository review")]


def esc(x):
    return html.escape("" if x is None else str(x),quote=True)


def official(url):
    return urlsplit(url).scheme=="https" and urlsplit(url).hostname in OFFICIAL_HOSTS


def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def pointer(doc,path):
    value=doc
    for token in path.split("/")[1:]:
        token=token.replace("~1","/").replace("~0","~")
        value=value[int(token)] if isinstance(value,list) else value[token]
    return value


def validate_inputs(observations,fixtures,statistics):
    errors=[];sources={o["id"]:o for o in observations}
    if len(sources)!=len(observations):errors.append("Duplicate observation IDs")
    for o in observations:
        if o["content_sha256"]!=digest({"excerpt":o["excerpt"],"projection":o["projection"]}):
            errors.append(o["id"]+": evidence changed without a matching integrity receipt")
        if parse_time(o["observed_after"])>parse_time(o["observed_before"]):errors.append(o["id"]+": reversed bounds")
        if o["role"]=="official" and not official(o["url"]):errors.append(o["id"]+": not an exact official host")
    for f in fixtures:
        if f["sport"] not in SPORT_ORDER:errors.append(f["id"]+": out-of-scope sport")
        references={ref["field"]:ref for ref in f["field_evidence"]}
        if len(references)!=len(f["field_evidence"]):errors.append(f["id"]+": duplicate field references")
        for field,ref in references.items():
            try:
                src=sources[ref["source_id"]]
                if src["role"]!="official" or pointer(src,ref["pointer"])!=f[field]:raise ValueError("field mismatch")
            except (KeyError,ValueError,IndexError,TypeError):errors.append(f["id"]+"/"+field+": unsupported value")
        for field in ("participant_a","participant_b","start_utc","venue","official_status","source_date","season","if_necessary"):
            if f.get(field) is not None and field not in references:errors.append(f["id"]+"/"+field+": missing reference")
        if f.get("start_utc"):
            try:
                if not f["start_utc"].endswith("Z"):raise ValueError("not UTC")
                parse_time(f["start_utc"])
            except (ValueError,TypeError):errors.append(f["id"]+": invalid exact start")
    for r in statistics:
        src=sources.get(r["source_id"])
        try:
            proof=pointer(src,r["pointer"])
            if any(r[k]!=v for k,v in proof.items()):raise ValueError("record mismatch")
        except (KeyError,ValueError,IndexError,TypeError):errors.append(r["id"]+": unsupported statistic")
    if len({f["id"] for f in fixtures})!=len(fixtures):errors.append("Duplicate fixture IDs")
    return errors


def repository_review():
    """Read-only file/line review, not external recertification of all archives."""
    revision=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    tracked=subprocess.check_output(["git","ls-files"],cwd=ROOT,text=True).splitlines()
    counts=Counter();parse_errors=[]
    for rel in tracked:
        path=ROOT/rel
        if not path.is_file():continue
        if path.suffix not in (".json",".py"):continue
        counts[path.suffix]+=1
        try:
            text=path.read_text(encoding="utf-8")
            json.loads(text) if path.suffix==".json" else ast.parse(text,filename=rel)
        except (ValueError,SyntaxError,UnicodeError) as e:parse_errors.append({"file":rel,"error":str(e)})
    findings=[]
    def finding(fid,path,needle,detail,sid,severity="review"):
        text=(ROOT/path).read_text(encoding="utf-8")
        if needle not in text:raise ValueError(f"Review locator no longer exists: {path}: {needle}")
        line=text[:text.index(needle)].count("\n")+1
        findings.append({"id":fid,"file":path,"line":line,"needle":needle,"sha256":__import__('hashlib').sha256((ROOT/path).read_bytes()).hexdigest(),
            "repository_url":f"https://github.com/buffedlizard55-lab/OLBG1/blob/{revision}/{path}#L{line}",
            "detail":detail,"source_id":sid,"severity":severity,"status":"needs review"})
    finding("A-01","scripts/se496eaf02_model.py","HIGH_B_FLOOR = 0.62",
        "Inherited High-B floor is 62%. Neither the threshold nor a passing arithmetic test establishes held-out calibration. No such tier imported.","nhl-standings","high")
    finding("A-02","data/496eaf02/fixtures.json",'"participant_b": "Marta Kostyuk"',
        "The older Ningbo Fernandez–Kostyuk pairing differs from the newly read order of play, which names Bouzkova. Draw also contains a Kostyuk wrist-injury entry. Replaced only in this namespace; archive not recertified.","wta-ningbo-op","high")
    finding("A-03","data/496eaf02/fixtures.json",'"event": "Li v Boulter',
        "The older Osaka Li–Boulter pairing is not the new order of play: Li faces Krueger, Boulter faces Siniakova. No opponent is inferred from advancing through a bracket.","wta-osaka-op","high")
    finding("A-04","scripts/se496eaf02_data.py","ICC official digital home",
        "ESPNcricinfo is presented as official ICC provenance in an inherited source label. This independent desk accepts league/governing-body/team observations only and does not promote a media report merely because that label says official.","nzc-fixtures","high")
    finding("A-05","data/current/snapshot.json",'"generated_at"',
        "Checked-in canonical snapshot retains a 22-October generation time. Root landing and canonical artifact can be different views. This desk has its own observation window and is not a silent refresh of the root.","nhl-schedule")
    finding("A-06","scripts/se496eaf02_data.py",'"a": "Leylah Fernandez", "b": "Marta Kostyuk"',
        "Historical source-code facts and published rows share the same disputed pairing. Rebuilding an older generator is not independent verification; both the source data and generated table need the same evidence check.","wta-ningbo-op")
    finding("A-07","scripts/se455acb16_data.py","OBSERVED_AFTER =",
        "This branch’s first draft restamped a copied desk without new checks. All of that draft’s observation times, prices, High labels and prose are withdrawn. Replacement observations use the actual 21:34:10–21:44:36Z retrieval window, not the old 21:30 stamp.","nhl-schedule","high")
    return {"revision":revision,"scope":"Every tracked JSON/Python file parsed for syntax; selected semantic findings only. This is NOT a line-by-line factual certification of every archived statement.",
        "counts":{"json_files":counts[".json"],"python_files":counts[".py"],"parse_errors":len(parse_errors),"semantic_findings":len(findings)},
        "parse_errors":parse_errors,"findings":findings}


def create_dataset(at):
    observations,fixtures,statistics=assemble_inputs()
    errors=validate_inputs(observations,fixtures,statistics)
    if errors:raise ValueError("\n".join(errors))
    sources={s["id"]:s for s in observations}
    flags=[]
    def flag(fid,title,detail,ids,fixture_id=None,severity="review"):
        flags.append({"id":fid,"title":title,"detail":detail,"source_ids":ids,"fixture_id":fixture_id,"severity":severity,"status":"needs review"})
    flag("F-01","Partial collection, not the full OLBG event universe",
        "All 15 brief categories have source checks. No category is globally complete. Returned hub cards were empty in this retrieval channel; neither live OLBG tip eligibility nor bookmaker availability has been confirmed for these official fixtures.",["olbg-baseball","nhl-schedule"],severity="high")
    flag("F-02","Initial draft claims withdrawn",
        "The first draft copied an earlier desk, changed timestamps and asserted fresh verification without actual reads. Its 81-fixture/51-High/51-prediction claims and copied prose are withdrawn. Passing structure checks did not validate those facts. Replacement data use only the retained new observations.",["nhl-schedule"],severity="high")
    flag("F-03","No supported Medium or High tier",
        "This version has no measured held-out calibration, complete current availability/form/history checks or confirmed eligible quote. All experimental prices stay Low. The five-per-sport daily High target has a shortfall of 75; no lower threshold or tuned handicap is used to fill it.",["nhl-standings","mlb-standings"],severity="high")
    flag("F-04","Ningbo opponent and availability conflict",
        "New official order of play pairs Fernandez with Bouzkova, not Kostyuk. Official draw notes a Kostyuk right-wrist injury. Previously copied Fernandez–Kostyuk data and prediction removed.",["wta-ningbo-op","wta-ningbo-draw"],severity="high")
    flag("F-05","Osaka pairings corrected",
        "Official order of play lists Ann Li–Ashlyn Krueger and Katie Boulter–Katerina Siniakova. The older Li–Boulter matchup is not accepted.",["wta-osaka-op"],severity="high")
    flag("F-06","Polish volleyball redirect conflict",
        "PlusLiga request resolved to TAURON Liga with men's team names. The competition identity conflict is retained, not silently repaired. No rows/prices imported from that response; independently read Italian SuperLega rows are separate.",["plusliga-redirect","lega-calendar"])
    flag("F-07","NBA collection failed/partial",
        "NBA games page returned a refresh error and the public scoreboard JSON attempt failed HTTP 500. Three pairings from the official newsletter are retained as schedule text only. The other nine Friday games are unknown, not zero. No early-season strength is invented.",["nba-games-check","nba-json-check","nba-news"])
    flag("F-08","Conditional MLB games withheld",
        "MLB ifNecessary=Y for World Series Games 5 and 6. Scheduled is not confirmation they will be needed. Every price and selection is withheld; Game 6 is also beyond the exact rolling window.",["mlb-schedule"])
    flag("F-09","Regular-season MLB inputs are not playoff form",
        "Run aggregates retain the 2026 regular-season period and original provider update timestamps. No probable pitcher, bullpen, park, lineup, injury or postseason adjustment has been measured. Four games sharing the same simplified price is a limitation, not four fresh independent analyses.",["mlb-standings","mlb-schedule"])
    flag("F-10","Gaelic Sports scope made explicit",
        "Fresh OLBG Hurling page explicitly describes Gaelic Sports as Football and Hurling. Both are grouped under the one requested category, with separate competitions. This supersedes the inherited football-only assumption; no hybrid shinty/camogie game or cross-code strength comparison is imported.",["olbg-hurling","munster-calendar"])
    flag("F-11","Automatic freshness is not automatic collection",
        "This desk is a selected session import. Its browser and rebuild gates withdraw estimates on expiry but do not collect new source facts. The repository's canonical scheduled collectors are separate and partial; this namespace is not falsely labelled continuously updated.",["nhl-schedule","mlb-schedule"],severity="high")
    flag("F-12","No hidden-feed workaround",
        "OLBG robots restricts /api/, /storage/app/json_data/* and Python-urllib. Only public pages and competition routes were checked through fetch_page. Empty extraction is not proof of zero matches or a proven zero-tip suppression mechanism.",["olbg-robots","olbg-nhl","olbg-mlb"])
    flag("F-13","Date-only and not-before times",
        "Unlabelled, Not Before and switchable display clocks never become invented exact UTC starts. Those fields remain null with source calendar dates and published text shown separately. Such entries cannot generate pre-match estimates.",["atp-almaty","nzc-fixtures","f1-hub"])
    for f in fixtures:
        f["official_urls"]=[sources[s]["url"] for s in f["source_ids"]]
        f["expires_at"]=iso(parse_time(f["observed_after"])+FIXTURE_TTL)
        f["state"]=fixture_state(f,at)
        missing=[]
        if not f["start_utc"]:missing.append("Exact UTC start unverified")
        if not f["official_status"]:missing.append("Current official match status unverified")
        if not f["venue"]:missing.append("Venue unverified")
        if not f["participant_a"] or not f["participant_b"]:missing.append("Participants/complete field unverified")
        missing += ["OLBG tip eligibility unverified","Available bookmaker quote unverified"]
        if f["if_necessary"]=="Y":missing.append("Conditional game; no prices")
        if f["source_note"]:missing.append(f["source_note"])
        f["flags"]=missing
        flag("ROW-"+f["id"],"Unconfirmed fields / placement gap", "; ".join(missing),f["source_ids"],f["id"])
    for s in statistics:s["official_url"]=sources[s["source_id"]]["url"]
    books=[originate(f,statistics,at) for f in fixtures]
    for b in books:
        b["official_urls"]=list(dict.fromkeys(sources[s]["url"] for m in b["markets"] for s in m["source_ids"]))
    by_book={b["fixture_id"]:b for b in books}
    approved=[p for p in PREDICTIONS if by_book.get(p["fixture_id"],{}).get("confidence")=="high"]
    if PREDICTIONS!=approved:raise ValueError("Unapproved High prose cannot be published")
    notes=[n for n in RESEARCH_NOTES if by_book.get(n["fixture_id"],{}).get("selection")]
    counts={"listings":len(fixtures),"match_listings":sum(f["kind"]=="match" for f in fixtures),
        "field_event_listings":sum(f["kind"]=="field-event" for f in fixtures),
        "exact_upcoming":sum(f["state"]=="upcoming" for f in fixtures),
        "calendar_or_status_gaps":sum("unverified" in f["state"] for f in fixtures),
        "priced_matches":sum(bool(b["markets"]) for b in books),"markets":sum(len(b["markets"]) for b in books),
        "outcomes":sum(len(m["outcomes"]) for b in books for m in b["markets"]),
        "high":sum(b["confidence"]=="high" for b in books),"medium":sum(b["confidence"]=="medium" for b in books),
        "low":sum(b["confidence"]=="low" for b in books),"predictions":len(approved),"research_notes":len(notes),
        "official_observations":sum(s["role"]=="official" and s.get("result")!="failed" for s in observations),
        "discovery_observations":sum(s["role"]=="discovery" for s in observations),"flagged":len(flags),
        "categories":len(SPORTS),"complete_categories":0}
    coverage=[]
    for slug,name,oid,route,source_id in SPORTS:
        rows=[f for f in fixtures if f["sport"]==slug]
        priced=[by_book[f["id"]] for f in rows if by_book[f["id"]]["markets"]]
        ranked=sorted((b for b in priced if b["selection"] and 1/101<=b["probability"]<=5/7),key=lambda b:(-b["probability"],b["fixture_id"]))[:5]
        coverage.append({"sport":slug,"name":name,"olbg_id":oid,"olbg_url":OLBG_HUBS[slug],
            "additional_olbg_ids":[26] if slug=="gaelic-sports" else [],"official_url":sources[source_id]["url"],
            "source_id":source_id,"scope_complete":False,"status":"partial", "listings":len(rows),
            "priced_matches":len(priced),"high":0,"daily_high_target":5,"high_shortfall":5,
            "top_research_ids":[b["fixture_id"] for b in ranked],
            "gap":"Partial official schedule; current OLBG submission eligibility, quote and complete confidence context unverified."})
    return {"schema_version":2,"session":"455acb16","generated_at":iso(at),
        "observation_window":{"after":OBSERVED_AFTER,"before":OBSERVED_BEFORE},
        "complete":False,"window":{"utc_from":iso(at),"utc_until_exclusive":iso(at+__import__('datetime').timedelta(days=7)),
             "date_only_policy":"Source calendar only; no timezone inference and no pre-match pricing."},
        "version":VERSION,"assumptions":ASSUMPTIONS,"counts":counts,"observations":observations,"fixtures":fixtures,
        "statistics":statistics,"books":books,"coverage":coverage,"predictions":approved,"research_notes":notes,"flags":flags}


def build(at,out):
    d=create_dataset(at)
    audit=repository_review()
    sources={s["id"]:s for s in d["observations"]}
    fixtures={f["id"]:f for f in d["fixtures"]};books={b["fixture_id"]:b for b in d["books"]}
    counts=d["counts"]
    data=out/"data"/"455acb16";site=out/"455acb16"
    data.mkdir(parents=True,exist_ok=True);site.mkdir(parents=True,exist_ok=True)
    save(data/"desk.json",d)
    save(data/"observations.json",{"window":d["observation_window"],"observations":d["observations"]})
    save(data/"fixtures.json",{"schema_version":2,"desk":"455acb16","generated_at":d["generated_at"],"fixtures":d["fixtures"]})
    save(data/"statistics.json",d["statistics"])
    save(data/"books.json",d["books"])
    save(data/"predictions.json",{"count":len(d["predictions"]),"predictions":d["predictions"],"research_notes":d["research_notes"]})
    save(data/"sources.json",{"count":len(sources),"sources":d["observations"]})
    save(data/"flagged.json",{"count":len(d["flags"]),"flags":d["flags"]})
    save(data/"summary.json",{"generated_at":d["generated_at"],"observation_window":d["observation_window"],"counts":counts})
    save(data/"repo-audit.json",audit)
    def csv_write(path,headers,rows):
        with path.open("w",encoding="utf-8-sig",newline="") as fh:
            w=csv.writer(fh,lineterminator="\n");w.writerow(headers);w.writerows(rows)
    csv_write(data/"matches.csv",["id","sport","event","participant_a","participant_b","source_date","published_clock","start_utc","official_status","venue","state","selection","confidence","probability","expires_at","quote","olbg_eligibility","official_sources","flags"],
        [[f["id"],f["sport"],f["event"],f["participant_a"],f["participant_b"],f["source_date"],f["published_clock"],f["start_utc"],f["official_status"],f["venue"],f["state"],books[f["id"]]["selection"],books[f["id"]]["confidence"],books[f["id"]]["probability"],books[f["id"]]["expires_at"],None,None," | ".join(f["official_urls"])," | ".join(f["flags"])] for f in d["fixtures"]])
    csv_write(data/"markets.csv",["fixture_id","family","line","selection","probability","fair_decimal","fair_american","in_band","confidence","expires_at","quote","official_sources","settlement"],
        [[b["fixture_id"],m["family"],m["line"],o["selection"],o["probability"],o["fair_decimal"],o["fair_american"],o["in_band"],o["confidence"],m["expires_at"],None," | ".join(sources[s]["url"] for s in m["source_ids"]),m["settlement"]] for b in d["books"] for m in b["markets"] for o in m["outcomes"]])

    def links(ids,prefix="",proof=True):
        result=[]
        for sid in dict.fromkeys(ids):
            s=sources[sid]
            label=s["publisher"]+" ↗"
            result.append(f'<a class="source" href="{esc(s["url"])}" target="_blank" rel="noopener noreferrer">{esc(label)}</a>')
        if proof and ids:result.append(f'<a class="proof" href="{prefix}sources.html#{esc(ids[0])}">Retained excerpt</a>')
        return '<div class="sources">'+"".join(result)+'</div>'
    def match_name(f):
        return f'{esc(f["participant_a"])} <span class="vs">vs</span> {esc(f["participant_b"])}' if f["participant_a"] and f["participant_b"] else esc(f["event"])
    def table(headers,rows,classes="",tid=""):
        return f'<div class="table-wrap"><table class="{classes}"{(" id="+chr(34)+tid+chr(34)) if tid else ""}><thead><tr>'+"".join(f'<th scope="col">{h}</th>' for h in headers)+'</tr></thead><tbody>'+"".join(rows)+'</tbody></table></div>'
    def badge(label,style="neutral"):
        return f'<span class="badge {style}">{esc(label)}</span>'
    def time_cell(f):
        if f["start_utc"]:return f'<time class="start" datetime="{f["start_utc"]}" data-clock="{f["start_utc"]}">{f["start_utc"].replace("T"," ").replace(":00Z"," UTC")}</time>'
        return f'<span class="calendar-date">{esc(f["source_date"])}</span><small>Source calendar · UTC unconfirmed</small><small>{esc(f["published_clock"])}</small>'
    def price_markup(b,outcome=None):
        if not b["markets"] or not b["selection"]:return '<span class="withheld">Withheld</span>'
        o=outcome or max(b["markets"][0]["outcomes"],key=lambda x:x["probability"])
        raw=o["fair_american"]
        band="In target band" if o["in_band"] else "Outside target band"
        return f'<span class="estimate" data-estimate data-deadline="{esc(b["expires_at"])}"><strong>{esc(o["selection"])}</strong><small>{o["probability"]*100:.2f}% · <span data-odds data-us="{raw:+d}" data-dec="{o["fair_decimal"]:.4f}">{raw:+d}</span> · Low</small><small class="band">{band} · experimental</small></span><span class="expired-value" hidden>Withheld — expired</span>'
    def filters(sport=True):
        options='<option value="">All sports</option>'+"".join(f'<option value="{slug}">{name}</option>' for slug,name,*_ in SPORTS)
        return f'<div class="filters"><label>Search<input type="search" class="search" placeholder="Team, player or event…"></label>'+(f'<label>Sport<select class="sport-filter">{options}</select></label>' if sport else '')+'<label>Status<select class="state-filter"><option value="">All recorded states</option><option value="upcoming">Exact upcoming</option><option value="calendar">Calendar / time gaps</option><option value="conditional">Conditional</option><option value="stale">Expired</option></select></label><label>Prices<select class="price-filter"><option value="">All rows</option><option value="priced">Priced only</option></select></label><button type="button" class="reset">Reset</button><button type="button" class="export">Export visible CSV</button><span class="filter-count" aria-live="polite"></span></div>'
    def fixture_table(rows,prefix="",sport_filter=True):
        trs=[]
        for f in rows:
            b=books[f["id"]]
            trs.append(f'<tr id="{f["id"]}" data-row data-sport="{f["sport"]}" data-state="{esc(f["state"])}" data-start="{esc(f["start_utc"])}" data-fresh-until="{f["expires_at"]}" data-priced="{str(bool(b["markets"])).lower()}"><td>{time_cell(f)}</td><td><a class="match" href="{prefix}verification.html#{f["id"]}">{match_name(f)}</a><small>{SPORT_NAMES[f["sport"]]} · {esc(f["competition"])}{(" · "+esc(f["event"])) if f["event"] and f["participant_a"] else ""}</small><small>{esc(f["venue"])}</small></td><td><span data-state-label>{badge(f["state"],"blue" if f["state"]=="upcoming" else "neutral")}</span><small>{esc(f["official_status"])}</small></td><td>{price_markup(b)}</td><td class="missing" aria-label="Available quote unverified"></td><td>{links(f["source_ids"],prefix)}<a class="proof" href="{prefix}flagged.html#ROW-{f["id"]}">Unconfirmed fields</a></td></tr>')
        if not trs:return '<div class="empty"><strong>No accepted rows in this view.</strong><p>This does not establish that no fixtures exist.</p></div>'
        return '<section class="filter-section">'+filters(sport_filter)+table(['<button class="sort" type="button">Start / date ↕</button>','Match / event','Source state','Our fair winner estimate','Bookmaker quote','Official source'],trs,"fixture-table")+'<p class="no-results" hidden>No matches fit these filters. Reset to show the recorded rows.</p></section>'
    def coverage_table(prefix=""):
        rows=[]
        for c in d["coverage"]:
            rows.append(f'<tr><td><a class="match" href="{prefix}sports/{c["sport"]}.html">{c["name"]} →</a></td><td>{c["listings"]}</td><td>{c["priced_matches"]}</td><td>{c["high"]} / 5</td><td>{badge("Partial","amber")}<small>Not globally enumerated · placement unconfirmed</small></td><td>{links([c["source_id"]],prefix)}</td></tr>')
        return table(["Sport","Recorded listings","Priced matches","High target","Coverage","Official recheck"],rows,"coverage-table")
    def shell(filename,title,body,prefix=""):
        menu="".join(f'<a href="{prefix}{url}"{(" aria-current="+chr(34)+"page"+chr(34)) if filename==url else ""}>{esc(label)}</a>' for url,label in NAV)
        return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Independent source-linked sports research. Partial collection; unconfirmed facts blank, estimates experimental."><title>{esc(title)} · OLBG Research 455acb16</title><link rel="icon" href="{prefix}assets/mark.svg" type="image/svg+xml"><link rel="stylesheet" href="{prefix}assets/style.css"><script defer src="{prefix}assets/app.js"></script></head><body data-generated="{d["generated_at"]}"><a class="skip" href="#main">Skip to content</a><button class="menu-button" aria-controls="sidebar" aria-expanded="false" type="button">☰ <span>Menu</span></button><aside id="sidebar"><a class="brand" href="{prefix}index.html"><span class="mark">O</span><span>OLBG<span class="brand-light"> / Research</span><small>INDEPENDENT MATCH DESK</small></span></a><p class="nav-label">RESEARCH WORKSPACE</p><nav aria-label="Primary navigation">{menu}</nav><div class="sidebar-note"><span class="status-dot"></span> Evidence before confidence<p>Own fair prices, never copied odds.<br>Blank means unconfirmed.</p><a href="{prefix}../index.html">Repository home ↗</a></div></aside><div class="layout"><header class="topbar"><div>Research desk <span>/</span> <strong>{esc(title)}</strong></div><div class="display-options"><label>Display time<select id="timezone"><option value="America/Los_Angeles">Los Angeles</option><option value="UTC">UTC</option></select></label><label>Odds<select id="odds-format"><option value="american">American</option><option value="decimal">Decimal</option></select></label></div></header><main id="main"><div class="release"><span class="status-dot"></span> 23 OCT 2026 · SOURCE WINDOW 21:34–21:44 UTC <span class="version">CHECKED EXCERPTS · PARTIAL COVERAGE</span></div><h1>{esc(title)}</h1><p id="freshness" class="freshness">Source observations expire six hours from 21:34:10 UTC, not from the time this page is opened.</p><div id="expiry-alert" class="notice danger" hidden>Evidence has expired. Pre-match estimates and selections have been withheld. Official links remain for rechecking.</div><noscript><div class="notice amber">Estimates withheld without JavaScript: runtime expiry cannot be enforced. Official source facts remain as an explicitly dated snapshot.</div></noscript>{body}<footer><span>Independent research · Not affiliated with OLBG · 18+ · No guaranteed returns.</span><span>Built {d["generated_at"]} · Source times never renewed by a build.</span></footer></main></div></body></html>'''
    pages=[]
    def write(filename,title,body,prefix=""):
        path=site/filename;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(shell(filename,title,body,prefix),encoding="utf-8");pages.append(filename)
    def panel(title,content,meta=""):
        return f'<section class="panel"><div class="panel-head"><div><h2>{title}</h2>{("<p>"+meta+"</p>") if meta else ""}</div></div>{content}</section>'
    def intro(text):return '<p class="lede">'+text+'</p>'
    pending='<div class="empty"><span class="empty-icon">○</span><h3>No supported High-confidence picks</h3><p>Official fixture facts are not the same as a reliable betting edge. Current OLBG eligibility, eligible bookmaker quotes and the full calibration/context gate are missing. The 75-pick daily High target remains unfilled.</p><a class="button" href="flagged.html#F-03">See the confidence gap →</a></div>'
    kpis='<div class="kpis">'+"".join(f'<div class="kpi"><p>{label}</p><strong>{value}</strong><small>{sub}</small></div>' for label,value,sub in [
        ("Recorded listings",counts["listings"],f'{counts["match_listings"]} match listings + {counts["field_event_listings"]} field sessions/events'),
        ("Price books · as of build",counts["priced_matches"],f'{counts["markets"]} markets · {counts["outcomes"]} outcomes · all Low'),
        ("High-confidence picks",counts["high"],"0 of the 75 daily target supported"),
        ("Brief categories","15",f'0 complete · {counts["flagged"]} review entries'),])+'</div>'
    # Today in the user's location; exact starts only. Runtime controls adjust the view.
    from zoneinfo import ZoneInfo
    today=at.astimezone(ZoneInfo("America/Los_Angeles")).date()
    exact=[f for f in d["fixtures"] if f["state"]=="upcoming"]
    tonight=[f for f in exact if parse_time(f["start_utc"]).astimezone(ZoneInfo("America/Los_Angeles")).date()==today]
    research_ids={fid for c in d["coverage"] for fid in c["top_research_ids"]}
    upcoming=[f for f in exact if f["id"] in research_ids and f not in tonight]
    order=lambda f:(-books[f["id"]]["probability"], f["start_utc"], f["id"])
    tonight.sort(key=order)
    upcoming.sort(key=order)
    write("index.html","The match research desk",intro("A clear view of the evidence, the prices we can actually calculate, and the gaps we cannot fill. Exactly the 15 sports in your brief. Every accepted sporting field is linked to a retained official-source observation; no inherited High label is carried forward.")+kpis+
        '<div class="notice amber"><strong>Important: this is a partial research release, not a complete live OLBG list.</strong> Official fixtures and current tip-submission availability are separate checks. The live OLBG cards did not render in this retrieval channel. Unknown values stay blank and flagged.</div>'+
        panel("Executive summary · High confidence",pending,"Today and upcoming — no supported High selection, no quota-driven predictions.")+
        panel("Today in Los Angeles · experimental winner preferences",fixture_table(tonight),"Exact future starts only. These Low-confidence research estimates are not confirmed available wagers.")+
        panel("Upcoming research shortlist",fixture_table(upcoming),"Up to five distinct in-band winner preferences per sport, sorted by estimated chance. Not the High tier.")+
        panel("Explore the 15 sports",coverage_table())+
        '<div class="notice neutral"><strong>Correction record.</strong> An initial draft incorrectly restamped copied data and claimed 51 High picks. Those claims and predictions have been withdrawn. This release is built only from the new observation window. <a href="flagged.html#F-02">Read the correction</a>.</div>')
    write("matches.html","Match register",intro("All retained listings, including conditional games, date-only schedule entries and field-event calendars. Blank values have not been inferred. Source-calendar dates are not silently converted to UTC. All direct official links and field-level locators are preserved.")+
        '<p class="downloads"><a href="../data/455acb16/matches.csv" download>Download as-of match CSV ↧</a><a href="../data/455acb16/desk.json" download>Full evidence JSON ↧</a><span>Downloads are dated research artifacts, not live price quotes.</span></p>'+fixture_table(d["fixtures"]))
    sportcards='<div class="sport-grid">'+"".join(f'<a class="sport-card" href="sports/{c["sport"]}.html"><span class="sport-number">{i:02d}</span><strong>{c["name"]}</strong><small>{c["listings"]} listings · {c["priced_matches"]} priced</small><span>View research →</span></a>' for i,c in enumerate(d["coverage"],1))+'</div>'
    write("coverage.html","Sports & coverage",intro("A source check is not a claim of complete coverage. Every category below is partial. The target is five distinct qualifying matches per sport per day; additional markets on one event do not count as extra matches.")+sportcards+panel("Coverage and daily shortfall",coverage_table())+
        '<div class="notice neutral">Gaelic Sports groups Gaelic Football (OLBG 25) and Hurling (26), as OLBG explicitly describes them. Their competition identities and scoring rules stay separate. Australian Rules and eSports are outside this 15-category brief.</div>')
    def market_blocks(fs,prefix=""):
        blocks=[]
        for f in fs:
            b=books[f["id"]]
            rows=[]
            for m in b["markets"]:
                for o in m["outcomes"]:
                    rows.append('<tr><td>'+esc(m["family"])+f'<small>{esc(m["line"])}</small></td><td>{price_markup(b,o)}</td><td class="missing" aria-label="Quote unverified"></td><td>'+esc(m["settlement"])+f'</td><td>{links(m["source_ids"],prefix)}</td></tr>')
            for investigation in b["investigated"]:
                if investigation["status"]=="withheld":rows.append(f'<tr><td>{esc(investigation["family"])}</td><td class="missing" aria-label="Selection and price withheld"></td><td class="missing" aria-label="Quote unverified"></td><td>{esc(investigation["reason"])}</td><td>{links(investigation["source_ids"],prefix)}</td></tr>')
            blocks.append(f'<section class="panel market-block" data-market-block data-sport="{f["sport"]}"><div class="panel-head"><div><h2>{match_name(f)}</h2><p>{esc(f["event"] or f["competition"])} · {f["id"]}</p></div>{badge("Low research" if b["markets"] else "Withheld")}</div>'+table(["Market / own line","Selection · chance · fair price","Available quote","Settlement / withholding reason","Official inputs"],rows)+f'<p class="panel-note">'+esc(" ".join(b["notes"]))+'</p></section>')
        return "".join(blocks)
    write("markets.html","Market explorer",intro("Winner, handicap, totals and sport-specific derivatives investigated for every retained listing. Prices below are our own experimental zero-margin calculations, not observed bookmaker offers. Unpriced markets remain blank with the missing requirements named.")+
        '<p class="downloads"><a href="../data/455acb16/markets.csv" download>Download as-of markets CSV ↧</a><a href="methodology.html">Pricing method & settlement →</a></p><label class="market-search-label">Find a match or market<input id="market-search" type="search" placeholder="Type a participant, event or market…"></label>'+market_blocks(d["fixtures"]))
    ranks=[]
    for c in d["coverage"]:
        for rank,fid in enumerate(c["top_research_ids"],1):
            f=fixtures[fid];b=books[fid]
            ranks.append(f'<tr><td>{c["name"]}<small>Research rank {rank} / up to 5</small></td><td><a href="verification.html#{fid}">{match_name(f)}</a></td><td>{time_cell(f)}</td><td>{price_markup(b)}</td><td>{links(f["source_ids"])}</td></tr>')
    write("high-confidence.html","Top-five & confidence",intro("High confidence is earned by evidence, not by a favourite’s price alone. The requested −250…+10000 window is applied to unrounded fair prices without clipping. This version does not have the calibration or full contextual checks needed to issue Medium or High.")+panel("Approved High selections",pending)+
        panel("Highest estimated chances within the target band · all Low",table(["Sport / research rank","Match","Start","Experimental winner preference","Official source"],ranks),"This is a research shortlist only. A greater-than-70% chance combined with the fair-price band would allow only 70%…71.4286%; that narrow arithmetic overlap does not establish confidence.")+panel("Five-per-sport target",coverage_table()))
    note_rows=[]
    for n in d["research_notes"]:
        f=fixtures[n["fixture_id"]];b=books[n["fixture_id"]]
        note_rows.append(f'<tr><td>{match_name(f)}<small>{SPORT_NAMES[f["sport"]]} · Low</small></td><td>{price_markup(b)}</td><td class="research-prose">{esc(n["text"])}</td><td>{links(n["source_ids"])}</td></tr>')
    write("predictions.html","Research notes",intro("No approved High predictions are published. The six notes below are newly written Low-confidence context, not quota-filling High recommendations. They do not claim complete recent-history or injury coverage. An unknown injury report is not a claim that a player is healthy.")+panel("Approved High predictions",pending)+panel("Low-confidence research context",table(["Match","Tentative preference","Match-specific context","Official sources"],note_rows)))
    for c in d["coverage"]:
        fs=[f for f in d["fixtures"] if f["sport"]==c["sport"]]
        write(f'sports/{c["sport"]}.html',c["name"],intro(f'{c["listings"]} retained listings, {c["priced_matches"]} price books and no supported High picks. This is partial official-source research, not the complete global or OLBG event list.')+
            f'<div class="notice amber">Five High matches targeted; five still unsupported for this category. <a href="../flagged.html#F-03">Confidence gap</a> · <a href="{esc(c["olbg_url"])}" target="_blank" rel="noopener noreferrer">OLBG discovery hub ↗</a> · {links([c["source_id"]],"../")}</div>'+
            panel("Fixture / event register",fixture_table(fs,"../",False))+panel("Market investigation",market_blocks(fs,"../")),"../")
    flag_rows=[]
    for f in d["flags"]:
        flag_rows.append(f'<tr id="{esc(f["id"])}"><td>{esc(f["id"])}<small>{badge(f["severity"],"amber")}</small></td><td><strong>{esc(f["title"])}</strong><p>{esc(f["detail"])}</p></td><td>{("<a href="+chr(34)+"verification.html#"+esc(f["fixture_id"])+chr(34)+">Field ledger →</a>") if f["fixture_id"] else "Needs review"}</td><td>{links(f["source_ids"])}</td></tr>')
    write("flagged.html","Flagged for Review",intro("Coverage gaps and unconfirmed values are published here, not filled with guesses. Needs review does not block an otherwise working site; source contradictions still block affected prices and predictions.")+table(["ID / priority","Finding","Affected row","Source / recheck"],flag_rows))
    src_parts=[]
    for s in d["observations"]:
        ref=f'../data/455acb16/observations.json'
        src_parts.append(f'<details class="evidence" id="{s["id"]}"><summary><span>{esc(s["publisher"])}</span><strong>{esc(s["id"])}</strong>{badge(s.get("result","selected excerpt") if s["role"]=="official" else "Discovery only")}</summary><div><p><a class="source" href="{esc(s["url"])}" target="_blank" rel="noopener noreferrer">{esc(s["url"])}</a></p>'+ (f'<p>Resolved URL: <a href="{esc(s["resolved_url"])}">{esc(s["resolved_url"])}</a></p>' if s["url"]!=s["resolved_url"] else '')+f'<p><strong>Observation window:</strong> {s["observed_after"]} – {s["observed_before"]} · chunks {esc(s["chunks_read"])}</p><p>{esc(s["note"])}</p><blockquote>{esc(s["excerpt"])}</blockquote><p class="tiny">{esc(s["retention"])} Hashes prove retained-content integrity, not external truth or original transport bytes.</p><p class="hash">SHA-256 {s["content_sha256"]}</p><a href="{ref}">Machine-readable excerpt & projection →</a></div></details>')
    write("sources.html","Sources & retained excerpts",intro("Every sporting field points into one of these explicitly bounded official observations. These are selected tool-rendered excerpts and manually transcribed field projections—not a claim to have retained full HTTP bodies, headers or every page chunk. Discovery observations can establish OLBG route/market documentation, never sporting truth.")+"".join(src_parts))
    verification=[]
    for f in d["fixtures"]:
        rows=[]
        fields=("competition","event","participant_a","participant_b","source_date","published_clock","start_utc","venue","official_status","season","if_necessary")
        for field in fields:
            ref=next((r for r in f["field_evidence"] if r["field"]==field),None)
            rows.append(f'<tr><td>{field}</td><td>{esc(f.get(field))}</td><td>{esc(ref["pointer"]) if ref else badge("Unverified / not stated","amber")}</td><td>{links([ref["source_id"]] if ref else f["source_ids"])}</td></tr>')
        for field in ("market_quote","olbg_eligibility"):
            rows.append(f'<tr><td>{field}</td><td class="missing" aria-label="Unverified"></td><td>{badge("Unverified","amber")}</td><td>{links(f["source_ids"])}</td></tr>')
        verification.append(f'<details class="evidence" id="{f["id"]}"><summary><strong>{match_name(f)}</strong><span>{f["id"]}</span></summary><div><p>Observed {f["observed_after"]} – {f["observed_before"]}; evidence expires {f["expires_at"]}.</p>'+table(["Field","Accepted value","JSON pointer / gap","Official observation"],rows)+f'<p>{esc(" ".join(f["flags"]))}</p></div></details>')
    write("verification.html","Field evidence ledger",intro("Non-null accepted values must exactly match their retained official projection. Blank source facts stay blank. Source calendar clocks, computation timestamps, current status and OLBG eligibility are separate fields.")+"".join(verification))
    statistic_rows=[]
    for s in d["statistics"]:
        score=f'{s["runs_scored"]} / {s["runs_allowed"]}' if "runs_scored" in s else f'{s["goals_for"]} / {s["goals_against"]}'
        statistic_rows.append(f'<tr><td>{esc(s["team"])}</td><td>{esc(s["period"])}</td><td>{s["games_played"]}</td><td>{s["wins"]}-{s["losses"]}-{s["ot_losses"]}</td><td>{score}</td><td>{esc(s.get("last_ten"))}<small>{esc(s.get("streak"))}</small></td><td>{links([s["source_id"]])}</td></tr>')
    write("analysis.html","Analysis & statistical inputs",intro("Win probability is an estimate; confidence is a separate judgment about evidence and reliability. All stats below retain their official period. NHL overtime defeats are losses for a binary winner market, not half-wins. MLB regular-season runs are not described as current postseason form.")+
        panel("Accepted paired-performance inputs",table(["Team","Period","GP","W-L-OTL","Scored / allowed","Last ten / streak","Official source"],statistic_rows))+
        panel("Price and confidence interpretation",'<div class="prose"><p>Fair decimal = 1 / p; American is derived from the unrounded chance and rounded only for display. The target window is 1.40…101.00 decimal (−250…+10000 American). Nothing is clipped or renormalized to get into that window.</p><p>With an additional p &gt; 70% requirement, the overlap is only 70%…71.4286%. This desk does not invent an alternate spread, generic scoring total or small variance to hit that narrow range. The strongest estimate can remain Low or lie outside the target band.</p><p>There is no edge calculation without an available, time-stamped quote and matching settlement. A blank quote is not zero margin or a recommendation to bet.</p></div>'))
    write("methodology.html","Methodology & limits",intro("Reproducible calculations, deliberately conservative evidence gates, and no hidden fallback ratings.")+panel("What is—and is not—supported",'<div class="prose"><ol><li>Public OLBG pages discover routes and documented market types. Empty retrieved cards do not prove a zero-event schedule, market closure, or a zero-tip suppression mechanism.</li><li>Only non-null fields transcribed from actual official reads are accepted. Unlabelled clocks and Not Before bounds never become exact UTC. A season schedule is not automatically a current match-state check.</li><li>Evidence lasts six hours from the lower observation bound, statistics 24 hours. A price ends at the earliest fixture deadline, statistical deadline or match start. Rebuilds do not refresh evidence.</li><li>NHL winner uses Beta(2,2) shrinkage plus log5 on compatible W/L/OTL. No home advantage or injury coefficient is guessed. Handicap/totals remain withheld without an appropriate score/settlement treatment.</li><li>MLB research uses independent Poisson score rates averaging a team’s own runs/game and its opponent’s runs-allowed/game, conditional on no tied final score. All MLB prices require ifNecessary=N. Fixed ±1.5 run lines and a mechanical three-point half-run totals ladder are research lines, not available quotes.</li><li>All originated estimates are Low. Medium/High require a future version with measured temporal hold-out calibration, full current match context and confirmed placement/quote evidence—not a boolean flag or price alone.</li><li>Any future High write-up must be unique, at least 30 words, name the betting selection and participants, support current form/recent history/statistical/player claims and relevant injuries with official references, and omit internal processing terminology. Missing information blocks prose; it is never filled to reach a word or match quota.</li><li>This namespace is a selected session import, not a daily automated feed. Browser expiry is automatic. The repository’s existing scheduled refresh remains separate and partial. No promise of five picks or complete continuous coverage is made.</li></ol><p>Unknown values are null in JSON and blank in source-value cells, with explicit flags. CSVs are dated as-of artifacts; live claims require a new official observation, not a file timestamp.</p></div>')+panel("Source and collector boundaries",'<p class="panel-note">No OLBG private API, restricted JSON storage, proxy, agent impersonation or credential collection. No paid feed or API key is required. '+links(["olbg-robots","nhl-schedule","mlb-schedule"])+ '</p>'))
    discovery_rows=[]
    for c in d["coverage"]:
        s=sources["olbg-"+c["sport"]]
        discovery_rows.append(f'<tr><td>{c["name"]}<small>OLBG {c["olbg_id"]}{" + 26 Hurling" if c["sport"]=="gaelic-sports" else ""}</small></td><td><a href="{c["olbg_url"]}">{esc(c["olbg_url"])}</a></td><td>{esc(s["excerpt"])}</td><td>Card extraction gap · eligibility unverified</td><td>{links([c["source_id"]])}</td></tr>')
    write("reverse-engineering.html","OLBG discovery & market scope",intro("The public sport routes use /betting-tips/{sport-name}/{sport-id}, with additional competition paths such as /Ice_Hockey/NHL/13 and /Baseball/MLB/12. These identify the discovery surface, not a complete live event feed.")+table(["Requested category","Public OLBG route","Observed retrieval text","Conclusion","Official sporting recheck"],discovery_rows)+
        panel("Market investigation—not assumed availability",'<div class="prose"><p>OLBG’s public guides describe winner, handicap and totals for several team sports; tennis adds set betting, first-set and games markets; darts documents legs/sets, correct-score and 180s; field sports use outright and placement markets. These descriptions are not evidence that any particular line is currently open.</p><p>Each listing’s market panel separately records the missing inputs for winner, handicap, total and sport-specific derivatives. Golf/F1/greyhound fields are never replaced by a fabricated two-participant contest. Team totals or player props are not labelled OLBG-supported without a live event check.</p><p>All 15 main hubs plus Hurling, NHL and MLB subroutes were actually checked. The retriever exposed no live card rows. The cause is unknown; a location, tip-count or hidden-feed explanation has not been established.</p>'+links(["olbg-robots","olbg-hurling","olbg-nhl","olbg-mlb"])+ '</div>'))
    audit_rows=[]
    for r in audit["findings"]:
        audit_rows.append(f'<tr><td>{r["id"]}<small>{badge(r["severity"],"amber")}</small></td><td><a href="{r["repository_url"]}">{esc(r["file"])}:{r["line"]}</a><small class="hash">{r["sha256"]}</small></td><td>{esc(r["detail"])}</td><td>{links([r["source_id"]])}</td></tr>')
    write("repo-audit.html","Repository review",intro(audit["scope"])+f'<p class="panel-note">Syntax inventory: {audit["counts"]["json_files"]} JSON files, {audit["counts"]["python_files"]} Python files; {audit["counts"]["parse_errors"]} parse errors. Hashes/line locators are structural evidence, not proof that a sporting claim is true. Other sessions’ archives and root data are not rewritten.</p>'+table(["Finding","Repository file / line / SHA-256","Observed issue","Official comparison / recheck"],audit_rows))
    assets=site/"assets";assets.mkdir(exist_ok=True)
    (assets/"style.css").write_text(CSS,encoding="utf-8")
    (assets/"app.js").write_text(JS,encoding="utf-8")
    (assets/"mark.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect rx="16" width="64" height="64" fill="#174d45"/><circle cx="32" cy="32" r="16" fill="none" stroke="#fff" stroke-width="7"/><circle cx="48" cy="16" r="5" fill="#81d9b0"/></svg>')
    save(data/"site-manifest.json",{"schema_version":2,"desk":"455acb16","generated_at":d["generated_at"],"pages":pages})
    print(f'Built {len(pages)} pages at {site}; '+json.dumps(counts,sort_keys=True))
    return d

CSS = r'''
:root{--bg:#f3f5f7;--ink:#182a37;--muted:#62717e;--line:#e4e9ed;--green:#1b6355;--sidebar:#132d35;--amber:#925709;--font:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.55 var(--font)}a{color:var(--green);text-decoration:none}a:hover{text-decoration:underline}button,input,select{font:inherit}button,select{cursor:pointer}button:focus-visible,a:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid #328dc4;outline-offset:3px}.skip{position:fixed;top:-50px;background:#fff;z-index:20;padding:12px}.skip:focus{top:0}#sidebar{position:fixed;inset:0 auto 0 0;width:232px;padding:32px 20px;background:var(--sidebar);color:#d6e4e7;display:flex;flex-direction:column;overflow-y:auto;z-index:10}.brand{display:flex;gap:12px;align-items:center;color:#fff;font-size:20px;font-weight:700;letter-spacing:-.5px}.brand:hover{text-decoration:none}.mark{background:#286656;border-radius:11px;display:grid;place-items:center;width:36px;height:39px;font-size:25px;font-weight:800;flex-shrink:0}.brand-light{font-size:12px;font-weight:400;color:#c0d3d8;letter-spacing:0}.brand small{display:block;font-size:8px;letter-spacing:1.8px;margin-top:2px;color:#adc4c8}.nav-label{font-size:9px;letter-spacing:1.6px;margin:40px 12px 12px;color:#8ca8af}nav{display:grid;gap:3px}nav a{padding:9px 12px;color:#c3d6db;border-radius:6px;font-size:12px}nav a[aria-current=page]{color:#fff;background:#2b5056;border-left:3px solid #7dcdac;padding-left:9px}nav a:hover{background:#22434c;text-decoration:none}.sidebar-note{margin-top:auto;padding-top:30px;font-size:11px;color:#b2cbd0}.sidebar-note p{font-size:10px;color:#8ca9b0}.sidebar-note a{color:#b7d8da}.status-dot{display:inline-block;width:6px;height:6px;background:#68b99a;border-radius:50%;margin-right:8px}.layout{margin-left:232px}.topbar{display:flex;justify-content:space-between;align-items:center;padding:17px 36px;background:#fff;border-bottom:1px solid var(--line);font-size:12px;gap:16px}.topbar span{margin:0 14px;color:#cad3da}.display-options{display:flex;gap:14px}.display-options label{font-size:10px;color:var(--muted)}.display-options select{display:block;border:0;background:#f0f4f5;color:var(--ink);padding:4px 9px;border-radius:4px;font-size:11px}main{padding:32px 36px 0;max-width:1700px;margin:auto;min-width:0}.release{font-size:9px;color:#627880;letter-spacing:1.3px;display:flex;align-items:center;flex-wrap:wrap;gap:4px}.version{margin-left:auto;color:#7a8b94;font-size:8px}h1{font-size:32px;line-height:1.2;letter-spacing:-1px;font-weight:650;margin:18px 0 12px}h2{font-size:16px;line-height:1.35;margin:0;font-weight:650;letter-spacing:-.2px}h3{font-size:18px;margin:12px 0}.lede{font-size:14px;color:#5c6c78;max-width:940px;line-height:1.75;margin-bottom:24px}.freshness{font-size:10px;color:#6d7f89;margin-bottom:22px}.kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:17px;margin:24px 0}.kpi{background:#fff;border:1px solid var(--line);border-radius:9px;padding:20px}.kpi p{margin:0;color:#687b86;font-size:11px}.kpi strong{font-size:33px;font-weight:650;letter-spacing:-1px;display:block;margin:9px 0}.kpi small{font-size:10px;color:#788790;display:block}.notice{padding:16px 19px;border-radius:7px;font-size:12px;margin:22px 0;border:1px solid var(--line)}.notice strong{display:block;margin-bottom:5px}.notice.amber{background:#fff8ea;border-color:#eddfb8;color:#71521e}.notice.neutral{background:#edf4f3;color:#3e6661}.notice.danger{background:#fceeee;border-color:#edc4c4;color:#914040}.panel{background:#fff;border:1px solid var(--line);border-radius:9px;overflow:hidden;margin:24px 0}.panel-head{padding:22px 23px;border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;gap:18px}.panel-head p{font-size:11px;margin:5px 0 0;color:#7a8993}.table-wrap{overflow-x:auto;max-width:100%;overscroll-behavior-x:contain}table{border-collapse:collapse;width:100%;text-align:left;font-size:12px}th{font-size:9px;font-weight:650;text-transform:uppercase;letter-spacing:.6px;color:#6b7a85;background:#f9fafb;border-bottom:1px solid var(--line);padding:13px 18px;white-space:nowrap}td{padding:18px;border-bottom:1px solid #edf0f2;vertical-align:top;line-height:1.6;max-width:570px;overflow-wrap:anywhere}tr:last-child td{border-bottom:0}tbody tr:hover{background:#fbfdfc}.fixture-table{min-width:820px}.match{font-weight:600;font-size:12px;color:#223a43}.vs{color:#a3adb5;font-weight:400;font-size:10px;margin:0 3px}td small{display:block;color:#8a969f;font-size:10px;margin-top:5px}.start{font-size:11px;white-space:nowrap;color:#355061}.calendar-date{white-space:nowrap;font-size:11px}.badge{display:inline-block;font-size:9px;line-height:1.35;border-radius:4px;padding:5px 7px;font-weight:500;max-width:170px}.badge.neutral{background:#f0f3f5;color:#5e7280}.badge.blue{background:#e9f1f7;color:#30608c}.badge.amber{background:#fff3d9;color:#8a610f}.sources{display:grid;gap:4px}.source{font-size:10px;color:#27695d}.proof{font-size:9px;color:#83929d}.missing:empty{min-width:52px;background:repeating-linear-gradient(-45deg,#fafbfc,#fafbfc 4px,#fff 4px,#fff 9px)}.withheld{color:#a0aab1;font-size:10px}.estimate{visibility:hidden;display:none}.js-ready .estimate{visibility:visible;display:block}.estimate strong{font-size:11px;font-weight:600}.estimate small{color:#577f75}.estimate .band{font-size:9px;color:#8c999f}.expired-value{font-size:10px;color:#a05e46}.empty{padding:34px;text-align:center;color:#71828d;max-width:750px;margin:auto}.empty h3{color:#2a454d;font-size:18px}.empty p{font-size:12px;max-width:590px;margin:10px auto 22px}.empty-icon{font-size:38px;color:#88aca4;font-weight:200}.button{display:inline-block;background:#1e6657;border:1px solid #1e6657;color:white;border-radius:5px;font-size:11px;padding:9px 15px}.filters{padding:16px 18px;background:white;display:flex;align-items:end;gap:10px;flex-wrap:wrap;border-bottom:1px solid var(--line)}.filters label{font-size:9px;text-transform:uppercase;color:#6c7d87;display:block;letter-spacing:.4px}.filters input,.filters select{display:block;width:100%;min-width:115px;max-width:230px;border:1px solid #dfe6ea;border-radius:5px;padding:8px 9px;margin-top:5px;font-size:11px;background:#fff;color:#46616a}.filters input{min-width:205px}.filters button,.sort{border:1px solid #dfe6ea;background:white;border-radius:5px;padding:8px 12px;color:#5c7580;font-size:10px}.sort{border:0;padding:0;font-size:9px;text-transform:uppercase}.filter-count{font-size:10px;color:#81909a;margin-left:auto;align-self:center}.no-results{padding:26px;color:#778a94;text-align:center}.downloads{display:flex;align-items:center;gap:22px;flex-wrap:wrap;font-size:11px;color:#8b98a1;margin:22px 0}.downloads span{font-size:10px}.sport-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:15px}.sport-card{padding:23px;background:#fff;border:1px solid var(--line);border-radius:8px;display:grid;color:var(--ink);transition:transform .15s,border .15s}.sport-card:hover{text-decoration:none;border-color:#9fbdb7;transform:translateY(-2px)}.sport-card .sport-number{font-size:10px;color:#a4b3bc;margin-bottom:14px}.sport-card strong{font-size:15px}.sport-card small{font-size:10px;color:#7c8b95;margin-top:5px}.sport-card>span:last-child{font-size:10px;color:#377567;margin-top:20px}.coverage-table{min-width:800px}.coverage-table :is(td,th):first-child{min-width:145px;overflow-wrap:normal}.coverage-table :is(td,th):nth-child(5){min-width:210px}.coverage-table :is(td,th):last-child{min-width:135px}.panel-note{font-size:11px;color:#7a8992;padding:15px 22px;margin:0}.research-prose{min-width:270px;font-size:12px;line-height:1.85;color:#4e6570}.market-search-label{display:block;color:#5d747f;font-size:11px}.market-search-label input{display:block;max-width:550px;width:100%;padding:12px;margin-top:8px;border:1px solid #d6e1e5;border-radius:6px}.market-block{min-width:0}.market-block table{min-width:700px}.prose{padding:22px 26px;color:#556d78;font-size:12px;line-height:1.9}.prose ol{padding-left:20px;margin:0}.prose li{margin-bottom:13px}.evidence{background:#fff;border:1px solid var(--line);border-radius:8px;margin:12px 0;scroll-margin-top:15px;overflow:hidden}.evidence summary{display:flex;flex-wrap:wrap;align-items:center;gap:15px;padding:17px 20px;cursor:pointer;font-size:12px;list-style-position:inside}.evidence summary:before{content:'+';color:#6d8b91}.evidence[open] summary:before{content:'−'}.evidence summary .badge{margin-left:auto}.evidence>div{border-top:1px solid var(--line);padding:18px 21px;color:#69808b;font-size:11px}.evidence a{overflow-wrap:anywhere}.evidence table{min-width:620px}.evidence .table-wrap{margin:0 -21px}blockquote{white-space:pre-wrap;margin:18px 0;background:#f5f8f8;border-left:3px solid #9cbeb4;padding:14px 16px;font:11px/1.7 ui-monospace,SFMono-Regular,monospace;color:#41696b}.hash{font:9px/1.6 ui-monospace,SFMono-Regular,monospace;word-break:break-all;color:#8a999f}.tiny{font-size:10px;color:#8b9aa2}.menu-button{display:none}footer{font-size:9px;color:#8b9ca6;display:flex;justify-content:space-between;gap:20px;border-top:1px solid #dde5e8;padding:25px 0;margin-top:38px}
[hidden]{display:none!important}@media(min-width:1700px){main{padding-left:50px;padding-right:50px}}@media(max-width:1180px){#sidebar{width:210px;padding:27px 15px}.layout{margin-left:210px}main{padding:28px 24px 0}.topbar{padding:16px 24px}.kpis{gap:10px}.kpi{padding:16px}.kpi strong{font-size:28px}.version{display:none}.sport-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:800px){#sidebar{transform:translateX(-100%);transition:transform .15s;width:235px}#sidebar.open{transform:translateX(0)}.layout{margin-left:0}.menu-button{display:flex;gap:6px;align-items:center;position:fixed;top:12px;left:12px;border:1px solid #dae3e8;background:white;border-radius:5px;z-index:15;font-size:12px;padding:7px 10px;color:#405e67}.topbar{padding:14px 14px 14px 95px;min-height:62px}.topbar>div:first-child{display:none}.display-options{margin-left:auto;gap:10px}.display-options label{font-size:8px}.display-options select{font-size:10px;padding:3px 5px}main{padding:24px 15px 0}.release{font-size:8px;letter-spacing:.7px}h1{font-size:27px;margin-top:16px}.lede{font-size:12px}.kpis{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.kpi{padding:16px}.kpi p{font-size:10px}.kpi strong{font-size:30px}.kpi small{font-size:9px}.panel-head{padding:18px}.panel-head h2{font-size:14px}.panel-head p{font-size:10px}.notice{font-size:11px;padding:15px}.filters{padding:12px;gap:9px}.filters label{width:calc(50% - 5px)}.filters label:first-child{width:100%}.filters input,.filters select{min-width:0;max-width:none;padding:7px}.filter-count{margin-left:0}.sport-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.sport-card{padding:17px}.sport-card strong{font-size:12px}.sport-card small{font-size:9px}.empty{padding:25px 18px}.evidence summary{padding:15px;font-size:11px}.evidence summary .badge{margin-left:0}footer{flex-direction:column;gap:8px}.prose{padding:17px}.downloads{gap:10px}.evidence>div{padding:16px}.hash{max-width:180px}}
@media(prefers-reduced-motion:reduce){*{transition:none!important}}@media print{#sidebar,.topbar,.filters,.menu-button{display:none}.layout{margin:0}main{padding:0}.estimate{display:none!important}table{font-size:9px}}
'''

JS = r'''/* Independent desk. No external calls, tracking, hidden data refresh or localhost backend. */
(() => {
'use strict';
const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];
let timezone='America/Los_Angeles';
const generated=Date.parse(document.body.dataset.generated);
function day(d,z){return new Intl.DateTimeFormat('en-CA',{timeZone:z,year:'numeric',month:'2-digit',day:'2-digit'}).format(d);}
function expire(){
  let expired=false;
  $$('[data-estimate]').forEach(el=>{
    const deadline=Date.parse(el.dataset.deadline);
    if(!Number.isFinite(deadline)||Date.now()>=deadline){
      el.replaceChildren();el.hidden=true;
      if(el.nextElementSibling?.classList.contains('expired-value'))el.nextElementSibling.hidden=false;
      const row=el.closest('[data-row]');if(row)row.dataset.priced='false';expired=true;
    }
  });
  $$('[data-row]').forEach(row=>{
    const start=Date.parse(row.dataset.start),deadline=Date.parse(row.dataset.freshUntil);
    if((Number.isFinite(start)&&Date.now()>=start)||Date.now()>=deadline){
      row.dataset.state=Date.now()>=deadline?'stale':'start elapsed';
      const label=$('[data-state-label]',row);if(label)label.textContent=row.dataset.state;
    }
  });
  // Imports can be entirely stale even on pages without any price element.
  if(Date.now()>=Date.parse('2026-10-24T03:34:10Z'))expired=true;
  if(expired){const alert=$('#expiry-alert');if(alert)alert.hidden=false;}
  $$('.filter-section').forEach(filterSection);
}
function clocks(){
  $$('[data-clock]').forEach(el=>{
    const date=new Date(el.dataset.clock);
    el.textContent=new Intl.DateTimeFormat('en-US',{timeZone:timezone,month:'short',day:'numeric',hour:'numeric',minute:'2-digit',timeZoneName:'short'}).format(date);
    el.title=el.dataset.clock;
  });
}
function odds(){
  const format=$('#odds-format')?.value||'american';
  $$('[data-odds]').forEach(el=>{el.textContent=format==='decimal'?el.dataset.dec:el.dataset.us;});
}
function filterSection(section){
  const search=($('.search',section)?.value||'').trim().toLowerCase();
  const sport=$('.sport-filter',section)?.value||'';
  const state=$('.state-filter',section)?.value||'';
  const priced=$('.price-filter',section)?.value||'';
  let n=0;
  $$('[data-row]',section).forEach(row=>{
    const stateMatch=!state||(state==='calendar'?/calendar|status unverified/.test(row.dataset.state):row.dataset.state.includes(state));
    row.hidden=!!((search&&!row.textContent.toLowerCase().includes(search))||(sport&&row.dataset.sport!==sport)||!stateMatch||(priced&&row.dataset.priced!=='true'));
    if(!row.hidden)n++;
  });
  const empty=$('.no-results',section);if(empty)empty.hidden=n!==0;
  const count=$('.filter-count',section);if(count)count.textContent=n+' rows';
}
function exportCSV(section){
  const table=$('table',section);if(!table)return;
  // Guard against formula execution when users open exports in spreadsheets.
  const cell=s=>{s=s.replace(/\s+/g,' ').trim();if(/^[=+@-]/.test(s))s="'"+s;return '"'+s.replace(/"/g,'""')+'"';};
  const rows=$$('tr',table).filter(r=>!r.hidden).map(row=>$$('th,td',row).map(td=>cell(td.innerText)).join(','));
  const blob=new Blob(['\ufeff'+rows.join('\r\n')],{type:'text/csv;charset=utf-8'});
  const link=document.createElement('a');link.href=URL.createObjectURL(blob);link.download='455acb16-visible-as-of.csv';document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(link.href),1000);
}
$$('.filter-section').forEach(section=>{
  $$('input,select',section).forEach(el=>el.addEventListener('input',()=>filterSection(section)));
  $('.reset',section)?.addEventListener('click',()=>{$$('input,select',section).forEach(el=>{el.value='';});filterSection(section);});
  $('.export',section)?.addEventListener('click',()=>exportCSV(section));
  $('.sort',section)?.addEventListener('click',event=>{
    const tbody=$('tbody',section),ascending=event.currentTarget.dataset.direction!=='ascending';
    event.currentTarget.dataset.direction=ascending?'ascending':'descending';
    event.currentTarget.closest('th').setAttribute('aria-sort',ascending?'ascending':'descending');
    const value=r=>r.dataset.start||'9999';
    $$('[data-row]',section).sort((a,b)=>value(a).localeCompare(value(b))*(ascending?1:-1)).forEach(r=>tbody.append(r));
  });
  filterSection(section);
});
$('#timezone')?.addEventListener('change',event=>{timezone=event.target.value;clocks();});
$('#odds-format')?.addEventListener('change',odds);
$('#market-search')?.addEventListener('input',event=>{
  const term=event.target.value.toLowerCase().trim();$$('[data-market-block]').forEach(b=>{b.hidden=!!(term&&!b.textContent.toLowerCase().includes(term));});
});
$('.menu-button')?.addEventListener('click',event=>{
  const button=event.currentTarget,open=button.getAttribute('aria-expanded')!=='true';
  button.setAttribute('aria-expanded',String(open));$('#sidebar')?.classList.toggle('open',open);
});
document.addEventListener('keydown',event=>{if(event.key==='Escape'){$('#sidebar')?.classList.remove('open');$('.menu-button')?.setAttribute('aria-expanded','false');}});
function openHash(){try{const item=document.getElementById(decodeURIComponent(location.hash.slice(1)));if(item?.tagName==='DETAILS')item.open=true;}catch{}}
window.addEventListener('hashchange',openHash);openHash();
// Withhold first, then reveal only values whose deadline has passed the check.
expire();clocks();odds();document.documentElement.classList.add('js-ready');
setInterval(expire,15000);
})();
'''

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--at",help="Deterministic evaluation time only, never a source time")
    parser.add_argument("--out",type=Path,default=ROOT,help="Output repository-shaped directory")
    args=parser.parse_args()
    at=parse_time(args.at) if args.at else datetime.now(timezone.utc).replace(microsecond=0)
    build(at,args.out.resolve())
