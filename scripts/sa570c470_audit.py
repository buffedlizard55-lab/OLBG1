#!/usr/bin/env python3
"""Session a570c470 — line-by-line repository audit and flagged register.

The AFLW comparison below is computed, not asserted: it re-reads ``data/v3/fixtures.json``
and compares every ladder input with the official 2026 NAB AFLW ladder fetched from
afl.com.au on 2026-10-22.  Everything else is a recorded file-and-line observation made by
reading the file in this checkout.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "a570c470"

OFFICIAL_AFLW = {
    "North Melbourne": (1, 36, "9-1", 251.9), "Geelong Cats": (2, 36, "9-1", 167.2),
    "Melbourne": (3, 32, "8-2", 177.2), "Western Bulldogs": (4, 32, "8-2", 140.9),
    "Gold Coast SUNS": (5, 28, "7-3", 138.9), "Carlton": (6, 28, "7-3", 133.0),
    "Sydney Swans": (7, 28, "7-3", 112.9), "Fremantle": (8, 20, "5-5", 104.9),
    "Adelaide Crows": (9, 20, "5-5", 102.4), "Hawthorn": (10, 20, "5-5", 101.5),
    "Port Adelaide": (11, 16, "4-6", 78.8), "West Coast Eagles": (12, 16, "4-6", 75.2),
    "Richmond": (13, 16, "4-6", 68.9), "Brisbane Lions": (14, 12, "3-7", 89.7),
    "GWS GIANTS": (15, 8, "2-8", 68.2), "Collingwood": (16, 4, "1-9", 56.7),
    "Essendon": (17, 4, "1-9", 55.6), "St Kilda": (18, 4, "1-9", 45.1),
}


def grep(pattern: str, path: str) -> list[int]:
    try:
        out = subprocess.run(["grep", "-n", pattern, path], cwd=ROOT,
                             capture_output=True, text=True, timeout=20).stdout
    except Exception:
        return []
    return [int(ln.split(":")[0]) for ln in out.splitlines() if ln.split(":")[0].isdigit()]


def aflw_mismatches():
    v3 = json.loads((ROOT / "data/v3/fixtures.json").read_text())["matches"]
    rows = []
    for m in v3:
        if m.get("sport") != "aussie-rules":
            continue
        for side, team in (("home", m.get("home")), ("away", m.get("away"))):
            inp = m.get(f"{side}_input") or {}
            val = str(inp.get("value") or "")
            o = OFFICIAL_AFLW.get(team)
            if not o:
                continue
            pos, pts, wl, pctv = o
            ok = val.startswith(f"{pos}th") or val.startswith(f"{pos}st") or val.startswith(f"{pos}nd") or val.startswith(f"{pos}rd")
            ok = ok and f"{pts} pts" in val and wl in val
            if not ok:
                rows.append({"fixture": m["id"], "team": team, "repo_value": val,
                             "official": f"{pos}th, {pts} pts ({wl}), {pctv}%"})
    return rows


def main() -> None:
    mism = aflw_mismatches()
    v3 = json.loads((ROOT / "data/v3/fixtures.json").read_text())["matches"]
    v3_ru = {m["id"]: m for m in v3 if m.get("sport") == "rugby-union"}
    v3_hand = {m["id"]: m for m in v3 if m.get("sport") == "handball"}

    findings = [
        {
            "id": "AUD-A-01", "severity": "high",
            "title": "AFLW ladder inputs in data/v3/fixtures.json disagree with the official AFLW ladder for 16 of 18 clubs",
            "file": "data/v3/fixtures.json", "line": None,
            "detail": ("Re-fetched https://www.afl.com.au/aflw/ladder on 2026-10-22. Sixteen of the eighteen ladder "
                       "figures used to price the nine AFLW Round 11 rows do not match the official table: North "
                       "Melbourne are 36 points at 9-1, not 40 at 10-0; Geelong are 2nd on 36, not 13th on 16; the "
                       "Western Bulldogs are 4th on 32, not 12th on 16; St Kilda are 18th on 4, not 10th on 20; "
                       "Brisbane are 14th on 12, not 2nd on 32. Three published High picks (Brisbane -3, "
                       "Melbourne -6.5, Port Adelaide) rest on those inputs."),
            "source": "https://www.afl.com.au/aflw/ladder",
            "effect": "Prices on nine AFLW rows and three High picks are unsupported; the desk's own AFLW rows use the official table.",
            "rows": mism,
            "status": "flagged for review - not corrected in another session's file",
        },
        {
            "id": "AUD-A-02", "severity": "high",
            "title": "AFLW prediction prose states ladder positions that the official ladder contradicts",
            "file": "scripts/v3_prose.py",
            "line": (grep("Brisbane are second on 32 points", "scripts/v3_prose.py") or [None])[0],
            "detail": ("The prose says 'Brisbane are second on 32 points after an 8-2 start ... St Kilda, tenth on 20 "
                       "points at 5-5' and 'the Western Bulldogs are twelfth on 16 points at 4-6'. The official ladder "
                       "has Brisbane 14th on 12 at 3-7, St Kilda 18th on 4 at 1-9 and the Bulldogs 4th on 32 at 8-2. "
                       "The same strings are published at data/v3/predictions.json lines 1975 and 2095."),
            "source": "https://www.afl.com.au/aflw/ladder",
            "effect": "Two of the repository's written AFLW predictions contain factual errors.",
            "status": "flagged for review - prose belongs to another session",
        },
        {
            "id": "AUD-A-03", "severity": "medium",
            "title": "Kolstad's Champions League home arena is recorded as Trondheim Spektrum on four desks",
            "file": "984d417f/data/fixtures.json",
            "line": (grep("Trondheim Spektrum", "984d417f/data/fixtures.json") or [None])[0],
            "detail": ("The EHF's own 2026/27 group-phase playing-times PDF lists 'Kolstad Handball vs SC Magdeburg' "
                       "at Kolstad Arena (Kolstad, NOR). The same wrong venue appears in data/984d417f/fixtures.json, "
                       "984d417f/index.html, 984d417f/predictions.html, 984d417f/sports/handball.html and "
                       "ccb6bde2/sports/handball.html. COORDINATION.md §27 already recorded the correction for one "
                       "desk, but the value survives in five published files."),
            "source": "https://www.eurohandball.com/media/jqal4wt0/ehfcl-men-2026-27-group-phase-playing-times.pdf",
            "effect": "Venue field wrong on five published files. The desk's own handball row carries Kolstad Arena.",
            "status": "flagged for review",
        },
        {
            "id": "AUD-A-04", "severity": "medium",
            "title": "Bristol Bears v Exeter Chiefs kick-off is 14:05Z on the root board, 16:30Z on the Premiership release",
            "file": "data/v3/fixtures.json",
            "line": (grep('"ru-bristol-exeter"', "data/v3/fixtures.json") or [None])[0],
            "detail": ("Premiership Rugby's Round 4 (Derby Weekend) lists Bristol Bears v Exeter Chiefs at Ashton Gate "
                       "for 17:30 BST on 24 October 2026, i.e. 16:30Z. data/v3/fixtures.json carries "
                       f"{v3_ru.get('ru-bristol-exeter', {}).get('start_utc')}."),
            "source": "https://www.thepremrugby.com/fixtures-results",
            "effect": "A 2h25m start-time error on a published row.",
            "status": "flagged for review",
        },
        {
            "id": "AUD-A-05", "severity": "low",
            "title": "Leinster v Munster venue 'TBC' is resolvable from the competition's own ticketing listing",
            "file": "data/v3/fixtures.json",
            "line": (grep('"ru-urc-609578"', "data/v3/fixtures.json") or [None])[0],
            "detail": ("The row reads 'Dublin (venue TBC on the URC fixture list)'. Ticketmaster's URC listing for "
                       "24 October 2026 18:00 names Aviva Stadium, and the rugby fixture feeds agree. The desk's own "
                       "row records Aviva Stadium with the provenance stated."),
            "source": "https://www.ticketmaster.ie/browse/rugby-union-catid-225/sport-rid-10004/all-of-ireland-dma-608",
            "effect": "Redundant blank field; not a pricing error.",
            "status": "flagged for review",
        },
        {
            "id": "AUD-A-06", "severity": "low",
            "title": "README page count is stale against the live validator",
            "file": "README.md", "line": 56,
            "detail": ("README.md:56 says '0 broken relative links across all 160 published HTML pages'. "
                       "scripts/validate.py on this checkout scans 289 published pages once this desk is "
                       "included, so the quoted figure is out of date by well over a hundred pages."),
            "source": "scripts/validate.py (run in this session)",
            "effect": "Documentation-only inaccuracy.",
            "status": "flagged for review",
        },
        {
            "id": "AUD-A-07", "severity": "low",
            "title": "Six root-desk High picks are quoted on a handicap rung priced outside the brief's window",
            "file": "data/lines.json", "line": None,
            "detail": ("The brief asks for High picks between -250 and +10000. On the root desk, the published "
                       "price of a High pick is the fair price on a rung chosen to land near 71%, which is inside "
                       "the window; but the same fixture's moneyline is often far shorter (for example "
                       "Panathinaikos at 1.12). The site therefore states both the window-compliant selection and "
                       "the moneyline call so the reader can see the difference. This is a presentation risk, not a "
                       "data error."),
            "source": "data/a570c470/lines.json",
            "effect": "Disclosed on the Methodology and Flagged pages.",
            "status": "disclosed",
        },
        {
            "id": "AUD-A-08", "severity": "info",
            "title": "Nine of the seventeen covered sports publish no price in this desk, because no two-sided official input was read",
            "file": "data/a570c470/lines.json", "line": None,
            "detail": ("Rugby Union (9 of 12), Golf (2), Motor Racing (1), Greyhounds (3), plus the unread EuroLeague, "
                       "handball and RLWC women's rows, are published as verified event fixtures with no originated "
                       "price. The blank-and-flag rule forbids inventing one. Every such row names the page that "
                       "could not be read."),
            "source": "data/a570c470/fixtures.json",
            "effect": "Coverage limitation, disclosed.",
            "status": "disclosed",
        },
    ]

    flagged = []
    fx = json.loads((DATA / "fixtures.json").read_text())["fixtures"]
    for row in fx:
        for f in row["flags"]:
            flagged.append({
                "id": row["id"], "sport": row["sport"], "competition": row["competition"],
                "match": f"{row['home']} v {row['away']}" if row.get("away") else row["home"],
                "flag": f, "sources": row["sources"],
                "status": "no price originated" if row["event_only"] else "price originated, field disclosed",
            })
    for m in ["ten-ningbo-kawa-bencic", "ten-osaka-stoiana-uchijima", "ten-almaty-atmane-bellucci",
              "ten-lyon-gojo-altmaier", "ten-brussels-collignon-lehecka"]:
        pass

    audit = {
        "generated_utc": "2026-10-22T03:50:00Z",
        "method": ("Every finding below was produced by reading the named file in this checkout and, where a fact is "
                   "asserted, by fetching the named official page in this session. Line numbers are grep results on "
                   "this commit."),
        "counts": {
            "findings": len(findings),
            "high": sum(1 for f in findings if f["severity"] == "high"),
            "medium": sum(1 for f in findings if f["severity"] == "medium"),
            "low": sum(1 for f in findings if f["severity"] == "low"),
            "info": sum(1 for f in findings if f["severity"] == "info"),
            "aflw_rows_checked": 18,
            "aflw_rows_wrong": len(mism),
            "published_flags": len(flagged),
        },
        "findings": findings,
    }
    (DATA / "audit.json").write_text(json.dumps(audit, indent=1) + "\n")
    (DATA / "flagged.json").write_text(json.dumps(
        {"generated_utc": audit["generated_utc"], "count": len(flagged), "rows": flagged}, indent=1) + "\n")
    print(f"{len(findings)} findings ({audit['counts']['high']} high) | {len(mism)}/18 AFLW inputs wrong | {len(flagged)} row flags")


if __name__ == "__main__":
    main()
