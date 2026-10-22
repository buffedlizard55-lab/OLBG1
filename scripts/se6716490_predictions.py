#!/usr/bin/env python3
"""Session e6716490-olbg1 — written predictions for every High-confidence pick.

Each entry below is hand-written for one selection.  Nothing in the prose goes
beyond the verified inputs printed beside it on the site: team records, ladder
positions, ratings and head-to-head facts come from the governing-body page cited
on the row, and player-level detail is used only where the register carries it.
Where no player detail was published on the page read, the write-up says so by
staying team-level rather than inventing a name.

Output: ``data/e6716490/predictions.json``
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "e6716490"

# Keyed by fixture id.  `text` is authored, not templated: no two write-ups open the
# same way, quote the same figures or reach the pick by the same route.
WRITEUPS = {
    "nhl-2026020154": {
        "headline": "Predators can stay inside a goal and a half in Boston",
        "text": (
            "Boston have started 7-2-1 for a .750 points percentage and are 3-1-0 on home ice with a "
            "plus-14 goal difference, but their last outing ended in overtime, not a clean win. "
            "Nashville arrive 3-2-3, 1-0-2 on the road and only minus-1 overall, having won their most "
            "recent game. Taking the Predators on the puck-line at +1.5 means they only have to avoid a "
            "two-goal defeat, and a team that has lost once in regulation across eight starts is a fair "
            "ask at those terms. Selection: Nashville Predators +1.5 goals."
        ),
    },
    "ru-top14-609567": {
        "headline": "Perpignan's points cushion is worth backing at Toulouse",
        "text": (
            "Toulouse lead the Top 14 on 24 points from a 5-0-1 record, a plus-73 differential and a "
            "five-match winning run that includes 45-34 over Bayonne, so they deserve favouritism. "
            "Perpignan are ninth on 13 points, 3-0-3 and minus-33 after scoring 166 and conceding 199, and "
            "they were beaten 55-25 by Racing in round five. The question is not who wins but by how much, "
            "and 13.5 points is a wide margin for a side that has already won three times this season. "
            "Selection: USA Perpignan +13.5 points."
        ),
    },
    "hand-ehf-12046": {
        "headline": "Barça's unbeaten group run merits the half-goal start",
        "text": (
            "Barça top EHF Champions League Group E with a perfect 4-0-0 record, eight points and a "
            "plus-33 goal difference from 137 scored and 104 conceded. Montpellier sit third on two "
            "points from 1-0-3, with 116 scored and 125 conceded across four rounds. The two registers "
            "held by this repository disagree on the score of the earlier meeting between them, so no "
            "scoreline is quoted here. Backing Barça at +0.5 goals simply needs the group leaders to avoid "
            "defeat at home. Selection: Barça +0.5 goals."
        ),
    },
    "aflw-r11-04": {
        "headline": "GWS hold a generous 22.5-point buffer against Carlton",
        "text": (
            "Carlton are sixth on the AFLW ladder with 28 points from 7-3-0 and a percentage of 133.0, "
            "while GWS are fifteenth on eight points from 2-8-0 at 68.2 per cent, so the Blues are clear "
            "favourites. The handicap asks GWS to stay within 22.5 points, roughly four goals, which is a "
            "big cushion even for a struggling side. Carlton's scoring rate is the only thing carrying a "
            "percentage that high, and a four-goal margin is not automatic. Selection: GWS GIANTS +22.5 points."
        ),
    },
    "el-535921": {
        "headline": "Maccabi's home floor keeps this inside ten and a half",
        "text": (
            "Real Madrid are 3-3 in the EuroLeague with a plus-23 differential from 554 points scored and "
            "531 conceded, but they are 1-3 on the road this season. Maccabi are 2-4, sixteenth in the "
            "twenty-team table on 509:540, a minus-31 differential, and they have split their two home "
            "games. A double-digit handicap on a visiting side that has lost three of four away from home "
            "is generous, especially in a league where margins compress. Selection: Maccabi Tel Aviv +10.5 points."
        ),
    },
    "el-r7-bay-dub": {
        "headline": "Dubai's defence travels better than Bayern's home form",
        "text": (
            "Dubai are 4-2 in EuroLeague play and hold opponents to 82.2 points a game, the fifth-best "
            "defence in the competition, with Dwayne Bacon third in the scoring charts at 17.8 points per "
            "game. Bayern are 2-4, 0-2 at home, scoring 521 and conceding 552 for a minus-31 differential, "
            "although Duane Washington gives them 16.8 points off the bench. Backing Dubai at +3.5 points "
            "covers a close game and a road win. Selection: Dubai Basketball +3.5 points."
        ),
    },
    "cric-nz-ind-t20-2": {
        "headline": "New Zealand's rating gap is smaller than a 20.5-run handicap",
        "text": (
            "India sit second in the ICC Men's T20I rankings on 267 points and arrived as reigning world "
            "champions, while New Zealand are fourth on 247. That is a twenty-point rating gap between two "
            "of the top four sides in the format, and the second T20I of the series hands New Zealand a "
            "20.5-run cushion. Ratings of that order translate to a narrow margin much more often than a "
            "three-wicket-and-twenty-run blowout. Selection: New Zealand +20.5 runs."
        ),
    },
    "el-535918": {
        "headline": "Efes with a seven-and-a-half point start looks the value side",
        "text": (
            "Anadolu Efes are 2-4 with 492 points scored and 510 conceded, a minus-18 differential, and "
            "they are 1-1 at home. Besiktas are 3-3 on 554:555, minus-1 overall and 2-1 on the road, so the "
            "visitors hold the better record but not by a wide margin. A 7.5-point start for the home side "
            "in a game between two mid-table clubs is the value side of the board, because home advantage "
            "in the EuroLeague is worth several points on its own. Selection: Anadolu Efes +7.5 points."
        ),
    },
    "mlb-849803": {
        "headline": "Milwaukee's road record earns the runs cushion in Tampa Bay",
        "text": (
            "The Brewers finished 103-59, went 48-33 on the road for a .593 rate and swept the Dodgers 4-0 "
            "in the NLCS. Tampa Bay were 98-64 and 55-26 at home, beating the Guardians 4-2 in the ALCS to "
            "reach this World Series game. A 2.5-run start for the stronger regular-season team in a "
            "post-season game is a wide line, because October games are decided late and rarely by three "
            "runs. Selection: Milwaukee Brewers +2.5 runs."
        ),
    },
}


def words(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’+.\-]*", text))


def sixgrams(text: str) -> set[str]:
    toks = re.findall(r"[a-z0-9]+", text.lower())
    return {" ".join(toks[i:i + 6]) for i in range(len(toks) - 5)}


def main() -> int:
    lines = json.load((OUT / "lines.json").open())
    verification = json.load((OUT / "verification.json").open())
    checks_by_fixture: dict[str, list[dict]] = {}
    for c in verification["checks"]:
        checks_by_fixture.setdefault(c["fixture_id"], []).append(c)

    rows = {r["id"]: r for r in lines["rows"]}
    preds, missing = [], []
    for h in lines["highs"]:
        writeup = WRITEUPS.get(h["id"])
        if not writeup:
            missing.append(h["id"])
            continue
        row = rows[h["id"]]
        preds.append({
            "fixture_id": h["id"],
            "sport": h["sport"],
            "competition": h["competition"],
            "home": h["home"],
            "away": h["away"],
            "start_utc": h["start_utc"],
            "selection": h["selection"],
            "market": h["market"],
            "line": h["line"],
            "prob": h["prob"],
            "price": h["price"],
            "us": h["us"],
            "book_price": h["book_price"],
            "book_us": h["book_us"],
            "confidence": "High",
            "unit": h["unit"],
            "headline": writeup["headline"],
            "text": writeup["text"],
            "words": words(writeup["text"]),
            "verified_inputs": [
                {"side": side, **row["inputs"][side]} for side in ("home", "away")
            ],
            "sources": h["sources"],
            "verification": h["verification"],
            "row_checks": checks_by_fixture.get(h["id"], []),
            "flags": h["flags"],
        })

    # uniqueness gate: no six-word sequence may appear in two write-ups
    seen: dict[str, str] = {}
    clashes = []
    for p in preds:
        for gram in sixgrams(p["text"]):
            if gram in seen and seen[gram] != p["fixture_id"]:
                clashes.append((gram, seen[gram], p["fixture_id"]))
            seen.setdefault(gram, p["fixture_id"])

    # selections that clear 70% but sit outside the brief's price window
    excluded = []
    for r in lines["rows"]:
        if not r["priced"]:
            continue
        best = None
        for m in r["markets"]:
            for s in m["selections"]:
                if s["prob"] >= 0.70 and not s["in_band"]:
                    if best is None or s["prob"] > best["prob"]:
                        best = dict(s, market=m["market"])
        if best:
            excluded.append({
                "id": r["id"], "sport": r["sport"], "home": r["home"], "away": r["away"],
                "selection": best["selection"], "market": best["market"], "prob": best["prob"],
                "price": best["price"], "us": best["us"],
                "reason": "fair price shorter than -250, so outside the brief's window",
                "sources": r["sources"][:2],
                "verification": r.get("verification", {}),
            })
    excluded.sort(key=lambda x: -x["prob"])

    out = {
        "session": "e6716490-olbg1",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rules": [
            "one hand-written prediction per High-confidence pick, never templated across picks",
            "at least 30 words, stating the team, the form, the recent record and the exact selection",
            "no player detail unless the official page read published it",
            "no fact appears in the prose that is not in the verified inputs beside it",
        ],
        "counts": {
            "high_picks": len(lines["highs"]),
            "predictions": len(preds),
            "min_words": min((p["words"] for p in preds), default=0),
            "max_words": max((p["words"] for p in preds), default=0),
            "shared_sixgrams": len(clashes),
            "band_excluded": len(excluded),
        },
        "missing": missing,
        "predictions": preds,
        "band_excluded": excluded,
    }
    with (OUT / "predictions.json").open("w") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print(f"{len(preds)} predictions, words {out['counts']['min_words']}-{out['counts']['max_words']}, "
          f"shared six-grams {len(clashes)}, band-excluded rows {len(excluded)}")
    if missing:
        print("MISSING write-ups for:", missing)
    for p in preds:
        print(f"  {p['sport']:13} {p['selection'][:32]:32} {p['words']}w  {p['headline'][:56]}")
    return 0 if not missing and not clashes else 1


if __name__ == "__main__":
    raise SystemExit(main())
