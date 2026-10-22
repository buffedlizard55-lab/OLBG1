"""Strict structural, provenance-shape, arithmetic, prose and link gate."""
from pathlib import Path
from urllib.parse import urlparse, unquote
import csv
import json
import math
import re
import s2aeea682_data as D
import s2aeea682_predictions as P

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/"data"/"2aeea682"
SITE = ROOT/"2aeea682"
ERRORS=[]
WARNINGS=[]
CHECKS=0

def check(condition,message):
    global CHECKS
    CHECKS += 1
    if not condition:
        ERRORS.append(message)

def official_url(url):
    try:
        p=urlparse(url)
        return p.scheme == "https" and p.netloc in D.OFFICIAL_HOSTS
    except Exception:
        return False


def validate_data(desk,flags,repo):
    check(desk["counts"]["fixtures"] == len(desk["fixtures"]),"fixture count mismatch")
    check(len(desk["coverage"]) == 17,"must have 17 sport coverage rows")
    check({c["sport"] for c in desk["coverage"]} == {s[0] for s in D.SPORTS},"coverage sports differ")
    check(not any(x in " ".join(D.EXCLUDED).lower() for x in ["baseball","tennis"]),"exclusion list corrupted")
    source_map={s["id"]:s for s in desk["sources"]}
    check(len(source_map) == len(desk["sources"]),"source IDs not unique")
    for s in desk["sources"]:
        check(s["url"].startswith("https://"),f"non-HTTPS source {s['id']}")
        if s["official"]:
            check(official_url(s["url"]),f"official source host not allowlisted: {s['id']}")
        else:
            check(s["id"] in {"olbg-sitemap","olbg-baseball","olbg-basketball","olbg-tennis","olbg-hockey"},f"unexpected nonofficial source {s['id']}")
    ids=set()
    for f in desk["fixtures"]:
        fid=f["id"]
        check(fid not in ids,f"duplicate fixture {fid}");ids.add(fid)
        check(f["sport"] in D.SPORT_NAMES,f"unknown sport {fid}")
        check(f["source_id"] in source_map and source_map[f["source_id"]]["official"],f"fixture lacks official source {fid}")
        check(official_url(f["official_link"]),f"fixture official link invalid {fid}: {f['official_link']}")
        if f["sport"] == "ice-hockey":
            check("/gamecenter/" not in f["official_link"] or "/2026/" in f["official_link"],f"NHL link uses rejected dashed-date format {fid}")
        check(f["verification"] == "official-fields-verified",f"verification label missing {fid}")
        check(f["date"] >= "2026-10-23",f"elapsed/date-invalid row {fid}")
        if f["start_utc"]:
            check(f["start_utc"] > desk["read_at_utc"],f"started fixture priced/published as upcoming {fid}")
        for field in f["blank_fields"]:
            if field in {"winner_pick","all_prices"}:
                continue
            check(f.get(field) in (None,""),f"blank-flagged field populated {fid}:{field}")
        if f["priced"]:
            check(bool(f["markets"]),f"priced fixture has no markets {fid}")
            check(f["winner_pick"] is not None,f"priced fixture lacks winner evaluation {fid}")
            check(f["unpriced_reason"] is None,f"priced fixture has unpriced reason {fid}")
        else:
            check(not f["markets"],f"unpriced fixture has markets {fid}")
            check(f["winner_pick"] is None,f"unpriced fixture has winner pick {fid}")
            check(bool(f["unpriced_reason"]),f"unpriced fixture lacks reason {fid}")
        if f.get("if_necessary") == "Y":
            check(not f["priced"],f"conditional MLB game priced {fid}")
        for m in f["markets"]:
            check(m["source_id"] in source_map and source_map[m["source_id"]]["official"],f"market source not official {m['id']}")
            check(official_url(m["official_link"]),f"market official link invalid {m['id']}")
            check(abs(sum(o["probability_exact"] for o in m["outcomes"])-1) < 1e-8,f"probabilities do not sum to 1 {m['id']}")
            for o in m["outcomes"]:
                p=o["probability_exact"]
                check(0 < p < 1,f"probability outside (0,1) {m['id']} {o['selection']}")
                check(abs(o["fair_decimal"]-round(1/p,4)) < 1e-10,f"decimal mismatch {m['id']}")
                expected=-100*p/(1-p) if p>=.5 else 100*(1-p)/p
                check(abs(o["fair_american_exact"]-expected) < 1e-7,f"American exact mismatch {m['id']}")
                check(o["fair_american"] == round(expected),f"American display mismatch {m['id']}")
                check(o["in_brief_window"] == (-250 <= expected <= 10000),f"window mismatch {m['id']}")
                qualifying=p>.70 and -250 <= expected <= 10000
                candidates=[h for h in f["high_candidates"] if h["market_id"]==m["id"] and h["selection"]==o["selection"]]
                check(len(candidates) == int(qualifying),f"High candidate mismatch {m['id']} {o['selection']}")
        if f["featured_high"]:
            eligible=[h for h in f["high_candidates"]]
            check(any(f["featured_high"]["market_id"] == h["market_id"] and f["featured_high"]["selection"] == h["selection"] for h in eligible),f"featured High not in candidate list {fid}")
            check(f["featured_high"]["probability_exact"] == max(h["probability_exact"] for h in eligible),f"featured High is not strongest {fid}")
    for h in desk["featured_high"]:
        check(h["probability_exact"] > .70,f"featured High at/below 70% {h['fixture_id']}")
        check(-250 <= h["fair_american_exact"] <= 10000,f"featured High outside price window {h['fixture_id']}")
        check(h["fixture_id"] in ids,f"featured High missing fixture {h['fixture_id']}")
    problems=P.check(desk)
    for problem in problems:
        check(False,"prediction: "+problem)
    CHECKS_INC=0
    for flag in flags:
        check(flag["id"].startswith("F-2AEE-"),f"bad flag ID {flag['id']}")
        check(official_url(flag["url"]),f"flag lacks official review URL {flag['id']}")
        check(all(x in ids for x in flag["fixture_ids"]),f"flag references missing fixture {flag['id']}")
    for finding in repo:
        check(finding["file"] and finding["line"],f"repo finding lacks file:line {finding['id']}")
        check(finding["url"].startswith("https://github.com/buffedlizard55-lab/OLBG1/blob/"),f"repo finding lacks review link {finding['id']}")
    # CSV joins and blank-field preservation.
    with (DATA/"fixtures.csv").open(encoding="utf-8") as fh:
        rows=list(csv.DictReader(fh))
    check(len(rows)==len(desk["fixtures"]),"fixtures CSV count mismatch")
    by_id={f["id"]:f for f in desk["fixtures"]}
    for row in rows:
        f=by_id.get(row["fixture_id"])
        check(f is not None,f"CSV unknown fixture {row['fixture_id']}")
        if f:
            check(row["official_source"]==f["official_link"],f"CSV source mismatch {f['id']}")
            check(row["start_utc"]==(f["start_utc"] or ""),f"CSV start mismatch {f['id']}")
            check(row["venue"]==(f["venue"] or ""),f"CSV venue mismatch {f['id']}")
    with (DATA/"markets.csv").open(encoding="utf-8") as fh:
        rows=list(csv.DictReader(fh))
    check(len(rows)==desk["counts"]["outcomes"],"markets CSV outcome count mismatch")
    check(sum(r["featured_high"]=="yes" for r in rows)==len(desk["featured_high"]),"CSV featured High count mismatch")
    for row in rows:
        check(official_url(row["official_source"]),f"CSV market source invalid {row['market_id']}")


def validate_site():
    pages=sorted(SITE.rglob("*.html"))
    check(len(pages)==30,f"expected 30 pages, got {len(pages)}")
    for slug,_,_,_ in D.SPORTS:
        check((SITE/"sports"/f"{slug}.html").exists(),f"missing sport page {slug}")
    ids_by_page={}
    for page in pages:
        text=page.read_text(encoding="utf-8")
        ids_by_page[page.resolve()]=set(re.findall(r'\bid="([^"]+)"',text))
        check("%%" not in text,f"render artifact %% in {page.relative_to(ROOT)}")
        check(">None<" not in text,f"None rendered in {page.relative_to(ROOT)}")
        for tbody in re.findall(r"<tbody>(.*?)</tbody>",text,flags=re.S):
            for row in re.findall(r"<tr\b.*?</tr>",tbody,flags=re.S):
                check("data-source-row" in row,f"table row lacks source marker in {page.relative_to(ROOT)}")
                check("source-link" in row and "https://" in row,f"table row lacks review link in {page.relative_to(ROOT)}")
        for attr,url in re.findall(r'\b(href|src)="([^"]+)"',text):
            if url.startswith(("https://","http://","mailto:","tel:","data:","javascript:")):
                continue
            if url.startswith("#"):
                check(url[1:] in ids_by_page[page.resolve()],f"missing local anchor {url} in {page.relative_to(ROOT)}")
                continue
            clean=unquote(url.split("#")[0].split("?")[0])
            if not clean:
                continue
            target=(page.parent/clean).resolve()
            check(str(target).startswith(str(ROOT.resolve())),f"link escapes repository {url} in {page.relative_to(ROOT)}")
            if clean.endswith("/") or not target.suffix:
                target=target/"index.html"
            check(target.exists(),f"broken local link {url} in {page.relative_to(ROOT)} -> {target}")
            if "#" in url and target.exists() and target.suffix==".html":
                # Filled in the second pass below.
                continue
    # Fragment targets need all pages' IDs, so run separately.
    for page in pages:
        text=page.read_text(encoding="utf-8")
        for url in re.findall(r'\bhref="([^"]+)"',text):
            if url.startswith(("https://","http://","#","mailto:","tel:","data:","javascript:")) or "#" not in url:
                continue
            clean,fragment=url.split("#",1)
            target=(page.parent/unquote(clean)).resolve()
            if target.exists() and fragment:
                check(fragment in ids_by_page.get(target,set()),f"missing fragment {url} in {page.relative_to(ROOT)}")


def main():
    desk=json.loads((DATA/"desk.json").read_text(encoding="utf-8"))
    flags=json.loads((DATA/"flags.json").read_text(encoding="utf-8"))
    repo=json.loads((DATA/"repo_audit.json").read_text(encoding="utf-8"))
    validate_data(desk,flags,repo)
    validate_site()
    report={"session":D.SESSION,"status":"passed" if not ERRORS else "failed","checks":CHECKS,
            "errors":ERRORS,"warnings":WARNINGS,"counts":{"html_pages":len(list(SITE.rglob('*.html'))),"fixtures":len(desk["fixtures"]),"markets":desk["counts"]["markets"],"outcomes":desk["counts"]["outcomes"],"predictions":len(desk["predictions"]),"flags":len(flags),"repo_findings":len(repo)}}
    (DATA/"validation.json").write_text(json.dumps(report,indent=1,ensure_ascii=False)+"\n",encoding="utf-8")
    if ERRORS:
        print("VALIDATION FAILED")
        for e in ERRORS:
            print(" -",e)
        raise SystemExit(1)
    print(f"VALIDATION PASSED · {CHECKS} checks · {report['counts']} · 0 errors / {len(WARNINGS)} warnings")

if __name__ == "__main__":
    main()
