"""Publish source-linked irregularities and a bounded repository review."""
import json
from pathlib import Path
import s2aeea682_data as D

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "2aeea682"
BASE = "cf187e20299b72aa29c3537a9cc624953aaa703b"

def flag(id,severity,title,detail,source_id=None,url=None,fixtures=None):
    if source_id:
        url = D.SOURCE_MAP[source_id]["url"]
    return {"id":id,"severity":severity,"title":title,"detail":detail,
            "source_id":source_id,"url":url,"fixture_ids":fixtures or []}

FLAGS = [
    flag("F-2AEE-01","high","Coverage is verified but partial","71 listings across 10 sports are published; seven category pages have no verified rows and 64 listings are unpriced. This is not a worldwide full-list claim. Empty categories and missing prices remain visible rather than backfilled.","nba"),
    flag("F-2AEE-02","high","Most fixtures cannot be priced responsibly","Only four non-conditional MLB games and three EuroLeague fixtures have paired official model inputs. Every other winner, handicap and total is blank/withheld with a row-level reason.","mlb-schedule"),
    flag("F-2AEE-03","medium","NHL coverage stops after 25 October","All 19 NHL games on 23-25 October were transcribed, but 26-29 October schedule chunks were not. No zero-game inference is made for those dates.","nhl-schedule"),
    flag("F-2AEE-04","medium","NBA pairings did not render","The official NBA calendar reports 12 games on 23 October and eight on 24 October, but its match-card area returned an error. OLBG-only pairings were not promoted.","nba"),
    flag("F-2AEE-05","medium","PDC schedule is behind a privacy interstitial","The official PDC article returned consent text rather than the draw, so no darts fixture or price is claimed as verified.","pdc"),
    flag("F-2AEE-06","medium","Volleyball competition/season needs reconciliation","The PlusLiga URL redirected to TAURON Liga; its title says 2024/2025 while displayed matches are dated October 2026. Rows are withheld until the correct competition page is isolated.","volleyball"),
    flag("F-2AEE-07","low","AFLW match cards absent from extraction","Two official page chunks returned navigation and footer content but no fixtures. No historical AFLW rows were re-stamped.","aflw"),
    flag("F-2AEE-08","low","eSports pairings absent from extraction","The official LoL Esports schedule shell and Worlds link returned without match pairings in the extracted content.","lol"),
    flag("F-2AEE-09","low","No eligible Gaelic football row observed","The GAA page displayed a Shinty-Hurling International, which is excluded. This is not evidence of a worldwide zero-fixture schedule.","gaa"),
    flag("F-2AEE-10","low","Greyhound runner card unavailable","GBGB's page exposed its racing search interface and reports, not a future field. No dog, trap or price was inferred.","gbgb"),
    flag("F-2AEE-11","medium","Bermuda event is already in progress","PGA TOUR marks Round 1 In Progress, so the tournament is excluded from pre-event picks. The correct Bermuda tournament ID is R2026528; R2026028 resolves to the BMW Championship.","pga"),
    flag("F-2AEE-12","medium","World Series Game 5 is conditional","MLB labels game 849799 ifNecessary=Y. Its fixture remains visible but all prices and winner preference are blank.","mlb-schedule",fixtures=["mlb-849799"]),
    flag("F-2AEE-13","medium","High clearance is only 0.04 percentage points","Under 10 with a push has conditional probability 0.700400, just above the strict 70% gate, and fair -234. The model is not calibrated out-of-sample and omits pitchers, lineups, park and postseason effects; High is a rules label, not a guarantee.","mlb-al",fixtures=["mlb-849805","mlb-849802","mlb-849804","mlb-849803"]),
    flag("F-2AEE-14","medium","Games 1-4 have identical MLB model numbers","The same two regular-season team inputs and no venue adjustment produce identical lines for all four non-conditional games. They are separate fixtures, not independent confirmations or four separate betting edges.","mlb-nl",fixtures=["mlb-849805","mlb-849802","mlb-849804","mlb-849803"]),
    flag("F-2AEE-15","low","WST fourth quarter-final is not yet named","Match 60 is officially Winner of match 55 v Winner of match 56. It is excluded from the named match table until the players are official.","wst"),
    flag("F-2AEE-16","low","Leinster venue is TBC","The official URC fixture list says TBC for Leinster v Munster; venue is blank.","urc-fixtures",fixtures=["urc-lei-mun"]),
    flag("F-2AEE-17","info","Ospreys kick-off correction applied","The older full fixture list says 19:45; a later official adjustment says 19:00 UK. The desk uses 19:00 and links the correction.","urc-adjustment",fixtures=["urc-osp-dra"]),
    flag("F-2AEE-18","medium","EHF calendar extraction is incomplete","Eleven fixtures were transcribed from the first EHF calendar chunk. Later chunks were not read, and venue/timezone remain blank on every handball row.","ehf"),
    flag("F-2AEE-19","medium","Unlabelled publication clocks are not converted","WTA, IRL, PCB, WST and EHF rows keep the publisher's display value; UTC remains blank where no timezone is stated. URC keeps its explicitly labelled local-zone clock.","wta-ningbo"),
    flag("F-2AEE-20","info","F1 is an event card, not a match prediction","The race has practice and qualifying before it. No driver line is originated from the schedule alone and track-local time is not converted.","f1",fixtures=["f1-usgp-2026"]),
    flag("F-2AEE-21","info","OLBG tip share is not a market price","The baseball hub showed 16/20 (80%) for Milwaukee, while this desk's independent winner estimate is 55.54%. Tip share was not used as a probability or bookmaker quote.","mlb-schedule",fixtures=["mlb-849805"]),
]


def line_of(path,needle):
    lines = path.read_text(encoding="utf-8").splitlines()
    for i,line in enumerate(lines,1):
        if needle in line:
            return i
    return None


def repo_finding(id,severity,title,path,needle,detail):
    line = line_of(ROOT/path,needle)
    locator = f"{path}" + (f":{line}" if line else "")
    url = f"https://github.com/buffedlizard55-lab/OLBG1/blob/{BASE}/{path}" + (f"#L{line}" if line else "")
    return {"id":id,"severity":severity,"title":title,"file":str(path),"line":line,
            "locator":locator,"detail":detail,"url":url}


def repo_audit():
    return [
        repo_finding("A-2AEE-01","high","Stale task-board claims remain open",Path("COORDINATION.md"),"| T9 |","T9 started on 21 October and remains 'in progress'. Other old open rows are also present. This session uses a collision-resistant ID and does not edit those claims; a later board cleanup should reconcile status with merged PRs."),
        repo_finding("A-2AEE-02","medium","A completed desk is still labelled in progress",Path("COORDINATION.md"),"| T-FEC |","The row begins DONE but its status column remains in progress. It is retained verbatim under the append-only coordination rule and flagged for board maintenance."),
        repo_finding("A-2AEE-03","medium","Previous fresh desk has expired",Path("COORDINATION.md"),"The desk expires with its evidence","The d7d19a67 handoff states a six-hour fixture expiry after 12:55Z. At this session's 20:55Z read it must not be presented as current without new official reads."),
        repo_finding("A-2AEE-04","info","Canonical root deliberately has no High picks",Path("README.md"),"zero Medium/High selections","The canonical README says its compatible inputs support only Low preferences. This desk does not overwrite that release; it publishes a separate, fresh evidence window and its own model limitations."),
        repo_finding("A-2AEE-05","medium","Historical evidence is not blanket recertification",Path("README.md"),"Not complete","The repository explicitly says worldwide coverage, all markets, current player context and calibration are incomplete. Any site-wide claim of a fully verified complete list would contradict this limitation."),
        repo_finding("A-2AEE-06","high","Historical NHL game-center links use a broken date format",Path("scripts/sd7d19a67_data.py"),"https://www.nhl.com/gamecenter/mtl-vs-chi/2026-10-23/2026020166","A fresh read of this dashed-date URL redirected to NHL /errors/not-found. The official schedule's slash-date form /2026/10/23/ works. This session corrected all 19 of its own links; the historical desk is left untouched and flagged for its owner."),
    ]


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"flags.json").write_text(json.dumps(FLAGS,indent=1,ensure_ascii=False)+"\n",encoding="utf-8")
    (OUT/"repo_audit.json").write_text(json.dumps(repo_audit(),indent=1,ensure_ascii=False)+"\n",encoding="utf-8")
    print(f"{len(FLAGS)} data/source flags; {len(repo_audit())} repository findings")

if __name__ == "__main__":
    main()
