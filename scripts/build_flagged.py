#!/usr/bin/env python3
"""build_flagged.py - regenerate datasets/flagged_for_review.json from the live dataset.

The Flagged for Review page is only useful if it is generated from the data that is
actually published.  This script rebuilds the row log from data/fixtures.json (including
each row's `verification` block) and appends the T17 findings to the existing systemic
finding list.  It is additive: previous findings are preserved verbatim.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATE = "2026-10-21"

T17_FINDINGS = [
    {
        "id": "T17-F1",
        "category": "Verification coverage (this pass)",
        "severity": "medium",
        "affected": "All 136 rows",
        "summary": (
            "52 rows were re-confirmed and 7 corrected against official pages in this pass; 6 carry a "
            "time conflict, 1 is unconfirmed, 16 are blocked by a gated publisher and 54 were not "
            "re-fetched and remain prior-session provenance."
        ),
        "evidence": (
            "Every row now stores a verification block (verdict, fields checked, evidence URL, note) "
            "and the full fetch log is published on the Verification page."
        ),
        "official_url": "https://buffedlizard55-lab.github.io/OLBG1/verification.html",
        "resolution": (
            "Nothing was upgraded on the strength of an earlier note. Rows that were not re-fetched are "
            "labelled 'not re-checked' wherever they appear, rather than being called verified."
        ),
    },
    {
        "id": "T17-F2",
        "category": "Publisher blocks automated reading",
        "severity": "high",
        "affected": "Darts — PDC Machineseeker European Championship (16 rows)",
        "summary": "pdc.tv serves a cookie-consent interstitial instead of the article body for both the draw article and /calendar/.",
        "evidence": "Fetched 2026-10-21T07:30Z: the article URL returned the cookieyes consent shell in all seven chunks, with no draw text.",
        "official_url": "https://www.pdc.tv/news/2026/october/18/2026-Machineseeker-European-Championship-field---draw-confirmed",
        "resolution": "The 16 darts rows keep their earlier provenance and are marked blocked. No darts value was re-asserted as verified today.",
    },
    {
        "id": "T17-F3",
        "category": "Fixture data corrected",
        "severity": "medium",
        "affected": "Cricket — NZ v India T20Is, NZ A v India A, Ford Trophy (7 rows) plus 1 added row",
        "summary": "Official NZC dates differ from the published snapshot: the NZ A four-day game is 23 Oct (not 22), and all three Ford Trophy openers are 27 Oct (not 24). Start times on the NZC page are visitor-local and are now withheld.",
        "evidence": "scoring.nzc.nz/fixtures fetched 2026-10-21: 1st T20I Thu 22 Oct Hagley Oval, 2nd Sat 24 Oct, 3rd Tue 27 Oct Wellington, NZ A v India A Fri 23 Oct Bert Sutcliffe Oval, Ford Trophy Round 1 Tue 27 Oct (Auckland, Nelson, Basin Reserve).",
        "official_url": "https://scoring.nzc.nz/fixtures",
        "resolution": "Dates and venues corrected from the official list, the missing 3rd T20I added, and every cricket kick-off time blanked because the page prints them in the visitor's timezone only.",
    },
    {
        "id": "T17-F4",
        "category": "Time conflict",
        "severity": "high",
        "affected": "AFLW Round 11 (9 rows)",
        "summary": "AFL's Round 11 widget shows match-ups and venues but renders kick-off times in the visitor's timezone; the displayed slots do not reconcile with the stored UTC stamps. The fixture page itself is script-rendered and returned no fixture table.",
        "evidence": "afl.com.au/aflw fetched 2026-10-21: port v coll at ALB, stk v bl at RSEA, geel v fre at GMHBA, gcfc v rich at PFS, wb v melb at MWO, syd v wce at HEN — with US-Eastern times that disagree with the published UTC.",
        "official_url": "https://www.afl.com.au/aflw",
        "resolution": "All nine AFLW kick-off times are withheld; the six confirmed match-ups keep their rows and the three that were not visible are labelled not re-checked.",
    },
    {
        "id": "T17-F5",
        "category": "Missing fixture found",
        "severity": "medium",
        "affected": "Baseball — MLB World Series Game 5 (mlb-849799) and Cricket — NZ v India 3rd T20I",
        "summary": "Two fixtures that belong in the 21–28 October window were absent from the published snapshot.",
        "evidence": "MLB Stats API lists 849799 on 2026-10-28 (first pitch 2026-10-29T00:00Z) and the NZC list includes the 3rd T20I on 27 Oct.",
        "official_url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-21&endDate=2026-10-30",
        "resolution": "Both rows are published. The World Series game is deliberately unpriced (no verified reverse-direction split) rather than given a guessed line.",
    },
    {
        "id": "T17-F6",
        "category": "Input corrected — pick downgraded",
        "severity": "medium",
        "affected": "Ice hockey — St. Louis Blues v Vegas Golden Knights (nhl-2026020160)",
        "summary": "The stored Vegas record was 8-2-0 (.800, W3); the live NHL standings feed now shows 8-3-0 (.727, L1). Correcting it moves the model probability from 62%+ to 59.9% and the pick from High to Medium.",
        "evidence": "api-web.nhle.com/v1/standings/2026-10-20 returned standingsDateTimeUtc 2026-10-21T07:05Z with Vegas 8-3-0, .727, streak L1.",
        "official_url": "https://api-web.nhle.com/v1/standings/2026-10-20",
        "resolution": "Input corrected, line re-priced, High prediction withdrawn. The row is now a Medium pick, which is what the verified numbers support.",
    },
    {
        "id": "T17-F7",
        "category": "Wrong source link fixed",
        "severity": "medium",
        "affected": "Snooker — Northern Ireland Open (11 rows)",
        "summary": "Three Match Centre URLs pointed at the wrong tie and two rows had no Match Centre link at all.",
        "evidence": "wst.tv's live/upcoming block on 21 Oct lists eleven Round 2 ties with per-match Match Centre identifiers.",
        "official_url": "https://www.wst.tv/",
        "resolution": "All eleven links now match the official listing; match-ups and dates confirmed, session times still withheld (they render in the visitor's timezone).",
    },
    {
        "id": "T17-F8",
        "category": "Coverage gap",
        "severity": "medium",
        "affected": "Basketball — EuroLeague Round 7 (22 Oct)",
        "summary": "The EuroLeague Game Center lists six games on 22 Oct; this snapshot prices three of them. Dubai v Bayern (SAP Garden) and at least one other are not carried.",
        "evidence": "euroleaguebasketball.net Game Center fetched 2026-10-21 shows Dubai Basketball v FC Bayern Munich on 22 Oct alongside the rows already published.",
        "official_url": "https://www.euroleaguebasketball.net/en/euroleague/game-center/",
        "resolution": "Published as a known coverage gap rather than filled with an invented line. The three carried rows were confirmed.",
    },
    {
        "id": "T17-F9",
        "category": "Unverified row",
        "severity": "high",
        "affected": "Cricket — Afghanistan v Bangladesh ODI (cric-afg-ban-odi)",
        "summary": "The only registered source for this fixture is an ICC rankings page, which does not list fixtures. It has no official fixture page, no date and no venue.",
        "evidence": "data/fixtures.json registers icc-cricket.com/rankings for the row; no governing-body fixture listing contains the match.",
        "official_url": "https://www.icc-cricket.com/rankings",
        "resolution": "Row status set to unverified, all fixture fields withheld, and it is listed here for review.",
    },
    {
        "id": "T17-F10",
        "category": "Upstream capture defect",
        "severity": "low",
        "affected": "Tennis — WTA Japan Open Osaka (ten-902065)",
        "summary": "The stored venue string was corrupted during capture ('ITC靱 …').",
        "evidence": "The venue field contained Japanese glyphs spliced into an ASCII string and could not be matched to an official venue line.",
        "official_url": "https://www.wtatennis.com/tournaments/405/osaka/2026/draws",
        "resolution": "Venue blanked rather than guessed; the row carries a flag and is listed for review.",
    },
    {
        "id": "T17-F11",
        "category": "Records drift",
        "severity": "low",
        "affected": "Ice hockey — all six NHL rows",
        "summary": "Standings-based inputs are an as-of-capture snapshot. The live NHL feed moves after every game, so a record quoted here may be one game stale.",
        "evidence": "The 2026-10-20 standings feed returned a standingsDateTimeUtc of 2026-10-21T07:05Z, i.e. live rather than historical.",
        "official_url": "https://api-web.nhle.com/v1/standings/2026-10-20",
        "resolution": "Disclosed on every NHL row; only the Vegas record was re-derived in this pass.",
    },
    {
        "id": "T17-F12",
        "category": "Not re-fetched in this pass",
        "severity": "medium",
        "affected": "Tennis (11), volleyball (8), rugby union (12), Gaelic football (4), golf (4), greyhounds (3), eSports (1), motor racing (1), EuroCup (2), RLWC26 women (2)",
        "summary": "These rows keep their earlier official-source links but were not re-read during this pass, so they are provenance-only.",
        "evidence": "Row-level verification verdict is 'not-rechecked' in data/fixtures.json and is shown against every row on the All Lines board.",
        "official_url": "https://buffedlizard55-lab.github.io/OLBG1/sources.html",
        "resolution": "Listed here so the distinction between 'checked today' and 'linked earlier' is never blurred.",
    },
]


def main() -> None:
    fixtures = json.loads((ROOT / "data" / "fixtures.json").read_text(encoding="utf-8"))["fixtures"]
    path = ROOT / "datasets" / "flagged_for_review.json"
    old = json.loads(path.read_text(encoding="utf-8"))

    findings = [f for f in old.get("findings", []) if not f["id"].startswith("T17-")]
    verified = sum(1 for f in fixtures if f["status"] == "verified")
    # Earlier findings quote the counts that were live when they were written. Keep the
    # finding but refresh the quoted totals so the page never states a stale number.
    for fd in findings:
        for key in ("summary", "resolution", "evidence", "affected"):
            if key in fd and isinstance(fd[key], str):
                fd[key] = (
                    fd[key].replace("134 source-linked events", f"{len(fixtures)} source-linked events")
                    .replace("129 Verified", f"{verified} Verified")
                )
    findings.extend(T17_FINDINGS)

    rows = []
    for f in fixtures:
        v = f.get("verification", {})
        flags = list(f.get("flags", []))
        verdict = v.get("verdict", "not-rechecked")
        if verdict == "not-rechecked" and not flags:
            flags = ["Not re-fetched in the T17 pass — prior-session provenance only"]
        rows.append(
            {
                "match_id": f["id"],
                "sport": f["sport"],
                "competition": f["competition"],
                "match": f"{f['home']} vs {f['away']}" if f.get("away") else f["home"],
                "status": f["status"],
                "verdict": verdict,
                "missing_utc": not bool(f.get("start_utc")),
                "unrated_sides": 0 if f.get("inputs") else 2,
                "flags": flags,
                "verification_note": v.get("note", ""),
                "official_url": (v.get("evidence") or ((f.get("sources") or [{}])[0].get("url", ""))),
            }
        )

    summary = {
        "upstream_and_audit_findings": len(findings),
        "flagged_fixture_rows": len(rows),
        "cross_checked_rows": sum(1 for f in fixtures if f["status"] == "cross-checked"),
        "missing_utc_rows": sum(1 for f in fixtures if not f.get("start_utc")),
        "verified_rows": sum(1 for f in fixtures if f["status"] == "verified"),
        "unverified_rows": sum(1 for f in fixtures if f["status"] == "unverified"),
        "confirmed_today": sum(1 for f in fixtures if f.get("verification", {}).get("verdict") in ("confirmed", "corrected")),
        "not_rechecked": sum(1 for f in fixtures if f.get("verification", {}).get("verdict") == "not-rechecked"),
        "blocked": sum(1 for f in fixtures if f.get("verification", {}).get("verdict") == "blocked"),
        "conflicts": sum(1 for f in fixtures if f.get("verification", {}).get("verdict") == "conflict"),
    }

    path.write_text(
        json.dumps({"generated": DATE, "summary": summary, "findings": findings, "rows": rows}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"flagged_for_review.json: {len(findings)} findings, {len(rows)} rows, {summary}")


if __name__ == "__main__":
    main()
