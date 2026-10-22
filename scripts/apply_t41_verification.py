#!/usr/bin/env python3
"""apply_t41_verification.py — record the T41 (session 2ca35f17-olbg1) live re-reads.

`scripts/live_verification.py` (session 72198d3e-olbg1, T20) owns the verification register.
This pass re-read four rows against official sources and must be able to write that evidence
without rewriting that 67 KB generator, so the updates live here and are applied as a
post-processing step:

    python3 scripts/live_verification.py      # base register
    python3 scripts/apply_t41_verification.py # T41 layer on top
    python3 scripts/build_site.py             # publish

Only evidence that was actually fetched on 2026-10-22 is written. Rows that were not re-read
in this pass are left byte-for-byte unchanged, and the summary is recomputed from the rows so
the counts cannot drift.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTER = ROOT / "data" / "verification.json"

CHECKED_AT = "2026-10-22T01:45Z"

UPDATES: dict[str, dict] = {
    "ten-ningbo-rybakina": {
        "status": "confirmed",
        "source_name": "WTA signed singles main draw, Ningbo 2026 (MDS.pdf, released 21 Oct 2026 22:13Z)",
        "source_url": "https://wtafiles.wtatennis.com/pdf/draws/2026/2092/MDS.pdf",
        "evidence": (
            "T41 independent re-read 2026-10-22T01:45Z: the signed WTA draw sheet for tournament "
            "2092 lists '1 1 RYBAKINA, Elena KAZ' with a first-round bye, and '4 Q KUDERMETOVA, "
            "Polina UZB' winning 76(5) 62 against Bucsa. The round of 16 pairing Rybakina v "
            "Kudermetova, the No. 1 seed and the Russian's rank of 1 in the draw's own ranked "
            "player table therefore match the stored row. Kudermetova's world No. 103 ranking is "
            "not printed on the draw and was not re-confirmed in this pass."
        ),
        "action": (
            "No change to the row. Blocker 'WTA draws are client-rendered' (LIVE-F-V7) is resolved "
            "for this tournament: the signed PDF is machine-readable and is now cited."
        ),
    },
    "ten-902093": {
        "status": "confirmed",
        "source_name": "WTA signed singles main draw, Ningbo 2026 (MDS.pdf, released 21 Oct 2026 22:13Z)",
        "source_url": "https://wtafiles.wtatennis.com/pdf/draws/2026/2092/MDS.pdf",
        "evidence": (
            "T41 independent re-read 2026-10-22T01:45Z: the same signed draw sheet lists '5 "
            "BENCIC, Belinda SUI' at rank 12 and 'Q KAWA, Katarzyna POL' beating Snigur 62 64 in "
            "the first round, setting up Kawa v Bencic in the round of 16 exactly as stored. Kawa's "
            "No. 124 ranking is not printed on the draw sheet, so that figure still rests on the "
            "WTA rankings page cited in the row and is not claimed as re-checked here."
        ),
        "action": "No change to the row; signed draw added as the primary evidence.",
    },
    "nhl-2026020154": {
        "status": "confirmed",
        "source_name": "NHL official standings API (2026-10-21, re-read 2026-10-22)",
        "source_url": "https://api-web.nhle.com/v1/standings/2026-10-21",
        "evidence": (
            "T41 independent re-read 2026-10-22T01:20Z: the standings snapshot (standingsDateTimeUtc "
            "2026-10-22T01:20:45Z) returned Boston with gamesPlayed 10, wins 7, losses 2, otLosses 1, "
            "homeWins 3, homeLosses 1, homeOtLosses 0, goalDifferential +14 and pointPctg 0.750 - "
            "matching the stored 7-2-1 / .750 / 3-1-0 home / +14 profile exactly."
        ),
        "action": "No change.",
    },
    "nhl-2026020160": {
        "status": "flagged",
        "source_name": "NHL official standings API (2026-10-21, re-read 2026-10-22)",
        "source_url": "https://api-web.nhle.com/v1/standings/2026-10-21",
        "evidence": (
            "T41 independent re-read 2026-10-22T01:20Z: Vegas now reads 8-3-0 with pointPctg 0.727, "
            "goalDifferential +14, streakCode L and streakCount 1, against the 8-2-0 / .800 / W3 "
            "snapshot this fixture was priced on. The stored input is unchanged and the drift was "
            "already disclosed as F-V5; this pass confirms it persists."
        ),
        "action": (
            "No re-price: the published selection is a labelled pre-game snapshot and re-pricing it "
            "after the game would be worse than disclosing the movement. Both values remain published."
        ),
    },
}


def main() -> None:
    doc = json.loads(REGISTER.read_text())
    rows = doc["rows"]
    touched = 0
    for row in rows:
        update = UPDATES.get(row["id"])
        if not update:
            continue
        row.update(update)
        row["checked_at"] = CHECKED_AT
        row["checked_pass"] = "T41 (session 2ca35f17-olbg1)"
        touched += 1
    missing = set(UPDATES) - {row["id"] for row in rows}
    if missing:
        raise SystemExit(f"verification rows not found: {sorted(missing)}")
    counts = Counter(row["status"] for row in rows)
    doc["summary"] = {
        "rows": len(rows),
        "confirmed": counts.get("confirmed", 0),
        "corrected": counts.get("corrected", 0),
        "flagged": counts.get("flagged", 0),
        "not_rechecked": counts.get("not_rechecked", 0),
    }
    doc.setdefault("passes", []).append({
        "pass": "T41",
        "session": "2ca35f17-olbg1",
        "checked_at": CHECKED_AT,
        "rows_re_read": touched,
        "note": (
            "Targeted re-read of the four high-confidence rows that were still marked "
            "not_rechecked (two WTA, two NHL). Signed WTA draw PDF resolves the JS-draw blocker "
            "for Ningbo. Darts (pdc.tv cookie wall) and EuroLeague (client-rendered game centre) "
            "were re-attempted and remain blocked; those rows keep their previous status."
        ),
    })
    REGISTER.write_text(json.dumps(doc, indent=2) + "\n")
    print(
        f"T41 verification layer applied to {touched} rows; register now "
        f"{doc['summary']['confirmed']} confirmed / {doc['summary']['corrected']} corrected / "
        f"{doc['summary']['flagged']} flagged / {doc['summary']['not_rechecked']} not re-checked."
    )


if __name__ == "__main__":
    main()
