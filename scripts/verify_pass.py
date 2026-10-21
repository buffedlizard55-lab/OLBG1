#!/usr/bin/env python3
"""verify_pass.py - apply the 2026-10-21 fresh official-source re-verification to data/fixtures.json.

Every change in this file is traceable to a page that was actually fetched during the
T17 pass (session b95dbd01-olbg1).  The fetch log itself lives in data/verification.json
and is rendered on verification.html.

Rules applied:
  * a field is only changed when the fetched official page states the new value;
  * a field the fetched page does not state is set to null (never guessed);
  * every row receives a `verification` block recording what was and was not checked.

The script is idempotent: running it twice produces the same file.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATE = "2026-10-21"
CHECKED_UTC = "2026-10-21T07:40:00Z"

# ---------------------------------------------------------------------------
# Official match-centre URLs read from https://www.wst.tv/ (21 Oct 2026 listing)
# ---------------------------------------------------------------------------
WST_MATCH_CENTRE = {
    "snk-pang-davies": "https://www.wst.tv/match-centre/67133698-e8a4-4b37-9266-452a97df8584",
    "snk-cheung-bingham": "https://www.wst.tv/match-centre/3d53c559-9bd7-4bc4-8e1d-a6c2b7459528",
    "snk-higgins-jones": "https://www.wst.tv/match-centre/eba55492-fba6-4a53-90be-a04b3560ae65",
    "snk-wells-day": "https://www.wst.tv/match-centre/e9c15ae6-b9b8-4cea-a83a-49c58eb14046",
    "snk-craigie-xu": "https://www.wst.tv/match-centre/afb42fc9-9654-479e-997e-d33d8a1a6888",
    "snk-zhang-williams": "https://www.wst.tv/match-centre/480e5abf-5766-44ad-9918-f822ceefd4a5",
    "snk-holt-brown": "https://www.wst.tv/match-centre/e58a00e5-e6a7-479b-98d0-5c7867af28a8",
    "snk-gao-gilbert": "https://www.wst.tv/match-centre/4fb27af0-7db4-4ec2-b93b-137de3f66135",
    "snk-noppon-donaldson": "https://www.wst.tv/match-centre/3a24076e-455c-497b-abd5-976e194abc5e",
    "snk-brecel-odonnell": "https://www.wst.tv/match-centre/0c49ba0c-2d21-481e-a2ac-fbece616f591",
    "snk-slessor-jones": "https://www.wst.tv/match-centre/f6536f1f-6c2d-47cd-b802-a81e6f04e4cc",
}

NBA_PAGE = "https://www.nba.com/games?date=2026-10-21"
NBA_GAME_IDS = {
    "nba-0022600085": "0022600085",
    "nba-0022600086": "0022600086",
    "nba-0022600004": "0022600004",
    "nba-0022600087": "0022600087",
    "nba-0022600088": "0022600088",
    "nba-0022600090": "0022600090",
    "nba-0022600089": "0022600089",
    "nba-0022600091": "0022600091",
    "nba-0022600005": "0022600005",
    "nba-0022600092": "0022600092",
    "nba-sac-lac-20261021": "0022600093",
}

NZC = "https://scoring.nzc.nz/fixtures"
EHF_PDF = "https://www.eurohandball.com/media/jqal4wt0/ehfcl-men-2026-27-group-phase-playing-times.pdf"
NRL = "https://www.nrl.com/draw/?competition=175&round=2&season=2026"
EL = "https://www.euroleaguebasketball.net/en/euroleague/game-center/"
MLB_SCHEDULE = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-21&endDate=2026-10-30"
NHL_SCHEDULE = "https://api-web.nhle.com/v1/schedule/2026-10-21"
NHL_STANDINGS = "https://api-web.nhle.com/v1/standings/2026-10-20"
AFLW = "https://www.afl.com.au/aflw"
PDC_DRAW = "https://www.pdc.tv/news/2026/october/18/2026-Machineseeker-European-Championship-field---draw-confirmed"


CORRECTED_IDS = {
    "cric-nz-ind-t20-1",
    "cric-nz-ind-t20-2",
    "cric-ausw-nzw-t20-3",
    "cric-nza-inda-fc1",
    "cric-ford-auck-cant",
    "cric-ford-cds-nd",
    "cric-ford-wgtn-otago",
}


def ver(verdict: str, fields: list[str], evidence: str, note: str) -> dict:
    return {
        "checked_utc": CHECKED_UTC,
        "by": "b95dbd01-olbg1",
        "verdict": verdict,
        "fields": fields,
        "evidence": evidence,
        "note": note,
    }


def find(fixtures: list[dict], fid: str) -> dict | None:
    for f in fixtures:
        if f["id"] == fid:
            return f
    return None


def main() -> None:
    doc = json.loads((ROOT / "data" / "fixtures.json").read_text(encoding="utf-8"))
    fixtures: list[dict] = doc["fixtures"]

    # ---------------------------------------------------------------- snooker
    for fid, url in WST_MATCH_CENTRE.items():
        f = find(fixtures, fid)
        if not f:
            continue
        f["sources"] = [
            {"name": "World Snooker Tour — live and upcoming matches (21 Oct 2026)", "url": "https://www.wst.tv/"},
            {"name": "WST world rankings", "url": "https://www.wst.tv/rankings/abfba8fe-1423-5a2a-a96b-d77e8b413ca8"},
            {"name": "WST Match Centre", "url": url},
        ]
        f["date_local"] = "2026-10-21"
        f["venue"] = "Waterfront Hall, Belfast"
        f["verification"] = ver(
            "confirmed",
            ["home", "away", "competition", "round", "date_local"],
            "https://www.wst.tv/",
            "Match-up and 21 Oct date read directly from the WST live/upcoming block; session start times render in the visitor's timezone, so UTC is withheld.",
        )

    # ---------------------------------------------------------------- cricket
    cricket_fixes = {
        "cric-nz-ind-t20-1": dict(
            start_utc=None, date_local="2026-10-22", venue="Hagley Oval, Christchurch",
            note="NZC lists the 1st T20I at Hagley Oval on Thu 22 Oct; the page shows '3:00am' in the visitor's timezone with no UTC or zone label, so the start time is withheld.",
        ),
        "cric-nz-ind-t20-2": dict(
            start_utc=None, date_local="2026-10-24", venue="Hagley Oval, Christchurch",
            note="NZC lists the 2nd T20I at Hagley Oval on Sat 24 Oct; UTC start not stated on the page.",
        ),
        "cric-nz-ind-t20-3": dict(
            start_utc=None, date_local="2026-10-27", venue="Hnry Stadium, Wellington",
            note="NZC lists the 3rd T20I at Wellington on Tue 27 Oct; this fixture was missing from the previous snapshot and has been added.",
        ),
        "cric-ausw-nzw-t20-3": dict(
            start_utc=None, date_local="2026-10-22", venue="North Sydney Oval, Sydney",
            note="NZC lists the 3rd women's T20I at North Sydney Oval on Thu 22 Oct; the stored 08:15Z timestamp could not be reproduced from the page, so it is withheld.",
        ),
        "cric-nza-inda-fc1": dict(
            start_utc=None, date_local="2026-10-23", venue="Bert Sutcliffe Oval, Lincoln University",
            note="NZC date is Fri 23 Oct (the previous snapshot published 22 Oct, which the official page does not support).",
        ),
        "cric-ford-auck-cant": dict(
            start_utc=None, date_local="2026-10-27", venue="Kennards Hire Community Oval, Auckland",
            note="NZC Ford Trophy Round 1 is Tue 27 Oct (previous snapshot published 24 Oct).",
        ),
        "cric-ford-cds-nd": dict(
            start_utc=None, date_local="2026-10-27", venue="Saxton Oval, Nelson",
            note="NZC Ford Trophy Round 1 is Tue 27 Oct (previous snapshot published 24 Oct).",
        ),
        "cric-ford-wgtn-otago": dict(
            start_utc=None, date_local="2026-10-27", venue="Cello Basin Reserve, Wellington",
            note="NZC Ford Trophy Round 1 is Tue 27 Oct (previous snapshot published 24 Oct).",
        ),
    }
    for fid, fx in cricket_fixes.items():
        f = find(fixtures, fid)
        if not f:
            continue
        f["start_utc"] = fx["start_utc"]
        f["date_local"] = fx["date_local"]
        f["venue"] = fx["venue"]
        f["status"] = "verified"
        f["verification"] = ver(
            "corrected" if fid in CORRECTED_IDS else "confirmed",
            ["home", "away", "competition", "date_local", "venue"],
            NZC,
            fx["note"],
        )

    afg = find(fixtures, "cric-afg-ban-odi")
    if afg:
        afg["status"] = "unverified"
        afg["verification"] = ver(
            "unconfirmed",
            [],
            "https://www.icc-cricket.com/rankings",
            "No official fixture page has been produced for an Afghanistan v Bangladesh ODI: the only registered URL is an ICC rankings page, which does not list fixtures. Date, venue and start are withheld; the row is published as unverified.",
        )

    # new: 3rd T20I (NZ v India) was missing from the snapshot
    if find(fixtures, "cric-nz-ind-t20-3") is None:
        fixtures.append(
            {
                "id": "cric-nz-ind-t20-3",
                "sport": "cricket",
                "competition": "Men's T20I Series",
                "stage": "3rd T20I",
                "start_utc": None,
                "date_local": "2026-10-27",
                "home": "New Zealand",
                "away": "India",
                "venue": "Hnry Stadium, Wellington",
                "neutral": False,
                "status": "verified",
                "sources": [
                    {"name": "New Zealand Cricket official fixtures service", "url": NZC},
                    {"name": "ICC rankings (rating input only)", "url": "https://www.icc-cricket.com/rankings"},
                ],
                "inputs": {
                    "home": {"label": "ICC Men's T20I rating", "value": "No. 4 (247 rating)", "rating": 68.5},
                    "away": {"label": "ICC Men's T20I rating", "value": "No. 2 (267 rating)", "rating": 81.5},
                },
                "flags": ["UTC start not published on the NZC fixtures page", "Row added during the T17 re-verification pass"],
                "verification": ver(
                    "confirmed",
                    ["home", "away", "competition", "date_local", "venue"],
                    NZC,
                    "Added from the official NZC fixture list; the previous snapshot omitted this fixture.",
                ),
            }
        )

    # ------------------------------------------------------------------ AFLW
    aflw_note = (
        "AFL's Round 11 listing renders kick-off times in the visitor's timezone (site geolocates to the USA) "
        "and the fixture page itself is script-rendered, so the stored UTC stamps could not be reproduced. "
        "Kick-off times are withheld; the match-up and round are retained."
    )
    aflw_confirmed = {
        "aflw-r11-02", "aflw-r11-03", "aflw-r11-06", "aflw-r11-07", "aflw-r11-08", "aflw-r11-09",
    }
    for f in fixtures:
        if f["sport"] != "aussie-rules":
            continue
        # Keep the calendar date that the withdrawn UTC stamp implied; only the clock is lost.
        kept_date = f.get("date_local") or (f["start_utc"][:10] if f.get("start_utc") else None)
        f["start_utc"] = None
        f["date_local"] = kept_date
        flags = [x for x in f.get("flags", []) if "kick-off" not in x.lower()]
        flags.append("Kick-off time withheld: AFL Round 11 listing shows times only in the visitor's timezone")
        f["flags"] = flags
        if f["id"] in aflw_confirmed:
            f["verification"] = ver("conflict", ["home", "away", "round", "venue"], AFLW, aflw_note)
        else:
            f["verification"] = ver(
                "not-rechecked", [], AFLW,
                "This Round 11 match was not visible in the fetched AFL listing; match-up and venue remain prior-session provenance and are flagged for review.",
            )

    # ------------------------------------------------------------------ NBA
    for fid, gid in NBA_GAME_IDS.items():
        f = find(fixtures, fid)
        if not f:
            continue
        f["provider_game_id"] = gid
        f["sources"] = [
            {"name": f"NBA official games page (2026-10-21) — game {gid}", "url": NBA_PAGE},
            {"name": "NBA standings (rating input)", "url": "https://www.nba.com/standings"},
        ]
        f["verification"] = ver(
            "confirmed",
            ["home", "away", "competition", "provider_game_id", "tip-off order"],
            NBA_PAGE,
            "Match-up, game ID and tip-off slot read from nba.com/games?date=2026-10-21. Arena naming on the row comes from the league game page and was not re-fetched in this pass.",
        )

    # ------------------------------------------------------------- EuroLeague
    for fid in ("el-535919", "el-535918", "el-535921"):
        f = find(fixtures, fid)
        if not f:
            continue
        f["verification"] = ver(
            "confirmed",
            ["home", "away", "competition", "round", "date_local", "venue"],
            EL,
            "Round 7 match-up, date and arena read from the EuroLeague Game Center; the page clock is visitor-local and the stored UTC agrees with the converted value.",
        )

    # -------------------------------------------------------------- handball
    for f in fixtures:
        if f["sport"] != "handball":
            continue
        f["verification"] = ver(
            "confirmed",
            ["home", "away", "competition", "round", "date_local", "start_utc", "venue"],
            EHF_PDF,
            "Round 5 pairing, date, CEST throw-off time and hall read from the EHF Champions League playing-times PDF (status 29 July 2026); UTC derived from CEST.",
        )

    # --------------------------------------------------------- rugby league
    for f in fixtures:
        if f["sport"] != "rugby-league":
            continue
        if f["competition"].startswith("RLWC26 Men"):
            f["verification"] = ver(
                "confirmed",
                ["home", "away", "competition", "round", "date_local", "venue"],
                NRL,
                "Round 2 pairing, date and venue read from the NRL draw; the page clock is visitor-local, so the stored UTC is a conversion of the displayed time.",
            )
        else:
            f["verification"] = ver(
                "not-rechecked", [], "https://www.nrl.com/draw/?competition=176&round=2&season=2026",
                "Women's tournament draw was not fetched in this pass.",
            )

    # ------------------------------------------------------------ ice hockey
    nhl_confirmed = {
        "nhl-2026020152": "PHI @ BUF, 2026-10-21T23:30Z, KeyBank Center",
        "nhl-2026020153": "FLA @ OTT, 2026-10-21T23:30Z, Canadian Tire Centre",
        "nhl-2026020154": "NSH @ BOS, 2026-10-22T23:00Z, TD Garden",
        "nhl-2026020155": "NYR @ TOR, 2026-10-22T23:00Z, Scotiabank Arena",
    }
    for f in fixtures:
        if f["sport"] != "ice-hockey":
            continue
        if f["id"] in nhl_confirmed:
            f["verification"] = ver(
                "confirmed", ["home", "away", "competition", "start_utc", "venue"], NHL_SCHEDULE,
                f"NHL schedule API returns {nhl_confirmed[f['id']]}.",
            )
        else:
            f["verification"] = ver(
                "not-rechecked", [], NHL_SCHEDULE,
                "Game sits later in the same week block that was only partially read in this pass; row remains prior-session provenance.",
            )

    # Vegas record corrected against the live standings feed (standingsDateTimeUtc 2026-10-21T07:05Z)
    vgk = find(fixtures, "nhl-2026020160")
    if vgk:
        vgk["inputs"]["away"] = {"label": "Points percentage", "value": "0.727 (8-3-0, L1 streak)", "rating": 72.7}
        vgk["flags"] = [x for x in vgk.get("flags", []) if "standings" not in x.lower()]
        vgk["flags"].append(
            "Away record corrected 2026-10-21: official standings now show 8-3-0 (.727, L1); the stored 8-2-0 (.800, W3) predates the 20 Oct result."
        )
    for f in fixtures:
        if f["sport"] != "ice-hockey":
            continue
        if not f.get("verification", {}).get("fields") or "start_utc" not in f["verification"]["fields"]:
            f.setdefault("flags", []).append(
                "Record inputs are an as-of-capture snapshot; the live NHL standings feed has since moved."
            )

    # ---------------------------------------------------------------- baseball
    for f in fixtures:
        if f["sport"] != "baseball":
            continue
        f["verification"] = ver(
            "confirmed",
            ["home", "away", "competition", "start_utc", "venue", "series game number"],
            MLB_SCHEDULE,
            "World Series game number, first pitch (UTC) and venue read from the MLB Stats API schedule.",
        )

    # add World Series Game 5, which the previous snapshot omitted
    if find(fixtures, "mlb-849799") is None:
        fixtures.append(
            {
                "id": "mlb-849799",
                "sport": "baseball",
                "competition": "MLB World Series",
                "stage": "World Series Game 5",
                "start_utc": "2026-10-29T00:00:00Z",
                "home": "Tampa Bay Rays",
                "away": "Milwaukee Brewers",
                "venue": "Tropicana Field, St. Petersburg",
                "neutral": False,
                "status": "verified",
                "sources": [
                    {"name": "MLB official schedule API (World Series)", "url": MLB_SCHEDULE},
                    {"name": "MLB.com Gameday 849799", "url": "https://www.mlb.com/gameday/849799"},
                ],
                "flags": [
                    "Unpriced: the snapshot holds no verified regular-season home/road split for this pairing in the reverse direction, so no line is published rather than a guessed one."
                ],
                "verification": ver(
                    "confirmed",
                    ["home", "away", "competition", "start_utc", "venue", "series game number"],
                    MLB_SCHEDULE,
                    "Game 5 of the World Series (official date 2026-10-28, first pitch 00:00Z on 29 Oct) was missing from the previous snapshot and has been added.",
                ),
            }
        )

    # ----------------------------------------------------------------- tennis
    for f in fixtures:
        if f["sport"] != "tennis":
            continue
        if f.get("venue", "").startswith("ITC"):
            f["venue"] = ""
            f["flags"] = f.get("flags", []) + [
                "Venue text was corrupted in the capture ('ITC靱 …'); the field is now blank pending a clean official read."
            ]
        f["verification"] = ver(
            "not-rechecked", [], f["sources"][0]["url"] if f.get("sources") else "",
            "Draw and ranking pages were not re-fetched in this pass; the row remains prior-session provenance and is listed on the Flagged page.",
        )

    # ------------------------------------------------------------------ darts
    for f in fixtures:
        if f["sport"] != "darts":
            continue
        f["verification"] = ver(
            "blocked", [], PDC_DRAW,
            "pdc.tv serves a cookie-consent interstitial instead of the article body, so the draw could not be re-read today. The row keeps prior-session provenance and is flagged.",
        )

    # de-duplicate flag strings added by repeated runs of this script
    for f in fixtures:
        if f.get("flags"):
            seen = []
            for x in f["flags"]:
                if x not in seen:
                    seen.append(x)
            f["flags"] = seen

    # ------------------------------------------------------------------- rest
    for f in fixtures:
        if "verification" in f:
            continue
        url = (f.get("sources") or [{}])[0].get("url", "")
        f["verification"] = ver(
            "not-rechecked", [], url,
            "Not re-fetched during the T17 pass; retained as prior-session provenance and listed on the Flagged page.",
        )

    # World Series Game 5 is published but deliberately not priced: the snapshot holds no
    # verified reverse-direction split to price it from, so no line is invented.
    g5 = find(fixtures, "mlb-849799")
    if g5:
        g5["unpriced"] = True

    doc["count"] = len(fixtures)
    doc["h2h_count"] = sum(1 for f in fixtures if f.get("away") and f["sport"] not in ("golf", "motor-racing", "greyhounds"))
    (ROOT / "data" / "fixtures.json").write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")

    # ------------------------------------------------- verification.json log
    log = {
        "generated": DATE,
        "session": "b95dbd01-olbg1",
        "method": (
            "Every URL below was fetched during this session. A row is only marked confirmed or corrected when the "
            "fetched page states the value; where a page is silent, script-rendered, geolocated or gated the value is "
            "withheld and the row is flagged instead of being inferred."
        ),
        "fetches": [
            {
                "url": NHL_SCHEDULE,
                "read_utc": CHECKED_UTC,
                "what_the_page_showed": "2 games on 2026-10-21 (PHI@BUF 23:30Z, FLA@OTT 23:30Z) and 12 on 2026-10-22 including NSH@BOS and NYR@TOR at 23:00Z, with venues.",
                "outcome": "Confirmed 4 NHL fixtures. Games 2026020158/160 sit in later chunks that were not read.",
            },
            {
                "url": NHL_STANDINGS,
                "read_utc": CHECKED_UTC,
                "what_the_page_showed": "Live standings feed (standingsDateTimeUtc 2026-10-21T07:05Z): Boston 7-2-1 (.750, OT1) and Vegas 8-3-0 (.727, L1).",
                "outcome": "Boston input matched. Vegas input was stale (8-2-0, .800, W3) and has been corrected.",
            },
            {
                "url": NBA_PAGE,
                "read_utc": CHECKED_UTC,
                "what_the_page_showed": "11 games on 2026-10-21 with game IDs 0022600085–0022600093 and tip times; the Clippers game is sac-vs-lac-0022600093.",
                "outcome": "All 11 NBA fixtures confirmed; the synthetic Clippers row ID now carries the official game ID.",
            },
            {
                "url": MLB_SCHEDULE,
                "read_utc": CHECKED_UTC,
                "what_the_page_showed": "Six 2026 World Series games: G1 849805 (24 Oct 00:00Z), G2 849802 (25 Oct), G3 849804 (27 Oct), G4 849803 (28 Oct), G5 849799 (29 Oct, if-necessary N), G6 849801 (31 Oct, if-necessary Y).",
                "outcome": "Four published rows confirmed; G5 was missing from the snapshot and has been added unpriced. G6 falls outside the 21–28 Oct window.",
            },
            {
                "url": "https://www.wst.tv/",
                "read_utc": CHECKED_UTC,
                "what_the_page_showed": "Eleven Northern Ireland Open Round 2 matches on 21 Oct with per-match Match Centre links (Pang–Davies, Cheung–Bingham, Higgins–Jones, Wells–Day, Craigie–Xu, Zhang–Williams, Holt–Brown, Gao–Gilbert, Noppon–Donaldson, Brecel–O'Donnell, Slessor–Jones).",
                "outcome": "All 11 match-ups confirmed. Three stored Match Centre links were wrong and two were missing; all 11 now point at the official links. Session times render in the visitor's timezone, so UTC stays blank.",
            },
            {
                "url": EHF_PDF,
                "read_utc": CHECKED_UTC,
                "what_the_page_showed": "EHF Champions League Men 2026/27 Round 5: twelve fixtures across 21–22 Oct with halls and 18:45/20:45 CEST throw-offs.",
                "outcome": "All 12 handball fixtures confirmed, including UTC conversion and venue.",
            },
            {
                "url": NRL,
                "read_utc": CHECKED_UTC,
                "what_the_page_showed": "RLWC26 Round 2: Tonga–Lebanon (CommBank), PNG–Samoa (Santos NFS), England–France (HBF Park), New Zealand–Cook Islands (One NZ Stadium), Australia–Fiji (Suncorp).",
                "outcome": "All five men's fixtures confirmed.",
            },
            {
                "url": EL,
                "read_utc": CHECKED_UTC,
                "what_the_page_showed": "EuroLeague Round 7: Hapoel–Virtus at Arena 8888 Sofia on 21 Oct; Efes–Besiktas, Dubai–Bayern, Maccabi–Real Madrid and others on 22 Oct with arenas.",
                "outcome": "Three published rows confirmed. The page also shows EuroLeague games on 22 Oct (Dubai–Bayern and at least one more) that this snapshot does not carry.",
            },
            {
                "url": NZC,
                "read_utc": CHECKED_UTC,
                "what_the_page_showed": "NZ v India 1st/2nd/3rd T20Is (Hagley Oval 22 & 24 Oct; Wellington 27 Oct), Australia Women v White Ferns 3rd T20I (North Sydney Oval, 22 Oct), NZ A v India A four-day (Bert Sutcliffe Oval, 23 Oct), and Ford Trophy Round 1 on 27 Oct at Auckland, Nelson and the Basin Reserve.",
                "outcome": "Eight cricket rows checked: three dates corrected, one date corrected from 24 to 27 Oct for the Ford Trophy games, one fixture (3rd T20I) added, and every start time withheld because the page prints them in the visitor's timezone only.",
            },
            {
                "url": AFLW,
                "read_utc": CHECKED_UTC,
                "what_the_page_showed": "AFLW Round 11 widget with match-ups and venues (port v coll at ALB, stk v bl at RSEA, geel v fre at GMHBA, gcfc v rich at PFS, wb v melb at MWO, syd v wce at HEN) and times in US Eastern.",
                "outcome": "Six match-ups confirmed but the displayed times do not reconcile with the stored UTC stamps; all nine AFLW kick-off times are withheld and the round is flagged. The afl.com.au fixture page is script-rendered and returned no fixture table.",
            },
            {
                "url": PDC_DRAW,
                "read_utc": CHECKED_UTC,
                "what_the_page_showed": "Cookie-consent interstitial (cookieyes) instead of the article body; the same happens on /calendar/.",
                "outcome": "All 16 darts fixtures remain unverified in this pass and are flagged.",
            },
        ],
        "verdict_counts": {},
    }
    counts: dict[str, int] = {}
    for f in fixtures:
        v = f["verification"]["verdict"]
        counts[v] = counts.get(v, 0) + 1
    log["verdict_counts"] = counts
    log["row_verdicts"] = {f["id"]: f["verification"]["verdict"] for f in fixtures}
    (ROOT / "data" / "verification.json").write_text(json.dumps(log, indent=2) + "\n", encoding="utf-8")

    print("fixtures:", len(fixtures), "verdicts:", counts)


if __name__ == "__main__":
    main()
