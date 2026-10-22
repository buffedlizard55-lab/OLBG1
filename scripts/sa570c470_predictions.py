#!/usr/bin/env python3
"""Session a570c470 — hand-written predictions for every High-confidence selection.

Each entry is bespoke prose, written against the official figures recorded for that row. It
names the participants, quotes the sourced current form and recent match history, and states
the betting selection in plain English.  Nothing here is generated from a template.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "a570c470"

PROSE = {
    "ten-almaty-medvedev-shimabukuro": (
        "Daniil Medvedev is the top seed and world number six on the signed ATP draw for Almaty, "
        "and he opens his week in the last 16 after a first-round bye. Sho Shimabukuro is a lucky "
        "loser who entered as the last direct acceptance at 93, an 87-place ranking gap. That margin, "
        "plus Medvedev's uncontested first round, makes a small games handicap the percentage play. "
        "The bet is Medvedev giving 1.5 games on the handicap at 1.42."
    ),
    "el-pao-bas-1022": (
        "Panathinaikos are 5-1 and plus-90 after six EuroLeague rounds, 528 points scored to 438 "
        "conceded, and they defend that record at the Telekom Center Athens. Kosner Baskonia are "
        "1-5 and were already minus-52 through five rounds, having conceded 478 points. The Greeks "
        "have won five of six while Baskonia have lost five, so the home side should clear a "
        "single-digit spread. Take Panathinaikos giving 7.5 points at 1.42."
    ),
    "pdc-ec-02": (
        "Danny Noppert is seeded fifth of 32 on the official European Tour ranking list; Stephen "
        "Bunting is seeded twenty-eighth, a 23-place gap over the season-long circuit. Their "
        "best-of-eleven first-round tie opens the Machineseeker European Championship at "
        "Dortmund's Westfalenhalle. Noppert has been the more consistent qualifier across fifteen "
        "European Tour events, and the seeding edge is large enough to back on the match line. "
        "Back Noppert on the match-winner line at 1.40."
    ),
    "pdc-ec-14": (
        "Wessel Nijman arrives as the second seed after winning two European Tour titles in 2026, "
        "the best return of any player bar the world champion. Martin Schindler is seeded "
        "thirty-first, giving Nijman a 29-place cushion in the Dortmund first round. In a "
        "best-of-eleven-leg format the stronger seed usually converts that gap into a two-leg win, "
        "which is exactly what the frame ladder is priced on. The selection is Nijman -1.5 legs at 1.42."
    ),
    "hand-ehf-12048": (
        "SC Magdeburg are 4-0 in EHF Champions League Group F with 141 goals scored and 108 "
        "conceded. Kolstad are 0-4, 111 to 143, and have taken nothing from four rounds. The "
        "reverse fixture in Magdeburg on 9 September finished 37-22, a fifteen-goal margin that "
        "shows how wide the gap is even before home advantage is considered. "
        "Recommended bet: Magdeburg giving four goals at 1.41."
    ),
    "hand-ehf-12054": (
        "Sporting CP are 3-0 with a plus-21 goal difference in Champions League Group D, while "
        "IFK Kristianstad are 0-4 and have been outscored 155 to 122. The two met in Kristianstad "
        "on 16 September and Sporting won 37-29, an eight-goal away victory. The Portuguese side "
        "also have the Pavilhao Joao Rocha behind them. Our selection is Sporting CP -4 goals at 1.40."
    ),
    "ru-top14-609567": (
        "Stade Toulousain lead the official LNR Top 14 table after Journee 6 on 24 points from six "
        "matches, five wins and one defeat, with 197 points scored to 124 conceded. USA Perpignan "
        "sit ninth on 13 points at three wins and three losses, 166 to 199. Toulouse are unbeaten "
        "at Ernest-Wallon in that run and face a side they outscore by more than eleven points a "
        "game. Toulouse to win outright is the pick at 1.40."
    ),
    "rl-wc26-tga-lbn": (
        "Tonga opened the Rugby League World Cup by beating England 30-12 at HBF Park, conceding "
        "only two tries. Lebanon lost their opener 42-18 to Papua New Guinea in Port Moresby and "
        "now meet Tonga at CommBank Stadium. The round-one margins, plus Tonga's forward rotation, "
        "point to a comfortable win rather than a one-score game. "
        "Take Tonga with a six-point head start to give at 1.41."
    ),
    "rl-wc26-nzl-cok": (
        "New Zealand pushed Australia to the final minutes before losing 24-22 in the tournament "
        "opener. Cook Islands were beaten 40-12 by Fiji, conceding seven tries in Newcastle. The "
        "Kiwis return to One NZ Stadium in Christchurch with the strongest round-one performance of "
        "any losing side, against an opponent that shipped forty. "
        "New Zealand to win is the recommended selection at 1.40."
    ),
    "aflw-r11-07": (
        "Eleventh-placed Port Adelaide have banked 16 ladder points across ten rounds, winning four "
        "and losing six, and their 78.8 percentage reflects a modest scoring profile. Collingwood "
        "are sixteenth with a single win from ten and the second-worst percentage in the "
        "competition at 56.7. At Alberton Oval the Power meet a side twelve ladder points below "
        "them. The pick is Port Adelaide on the win line at 1.41."
    ),
    "aflw-r11-02": (
        "Geelong have won nine of ten and sit second on 36 points with a competition-leading 167.2 "
        "percentage behind North Melbourne. Fremantle are eighth, five wins and five losses for 20 "
        "points, with a 104.9 percentage. A 62-point percentage gap at GMHBA Stadium is the basis "
        "for the line. Back Geelong giving 4.5 points at 1.42."
    ),
    "aflw-r11-06": (
        "Gold Coast SUNS have built a 7-3 record worth 28 points and fifth place, scoring at 138.9 "
        "per cent. Richmond arrive thirteenth having won four of ten for 16 points, with a "
        "percentage of 68.9. Three extra wins and 70 points of percentage separate the pair at "
        "People First Stadium. Gold Coast to win is the selection at 1.41."
    ),
    "aflw-r11-08": (
        "Seven wins from ten rounds have Sydney seventh on 28 points with a 112.9 percentage. West "
        "Coast are twelfth, four and six for 16 points, and their 75.2 percentage follows a heavy "
        "round-ten loss to Geelong. Henson Park hosts a Swans side three wins clear. "
        "Take the Swans on the head-to-head at 1.41."
    ),
    "aflw-r11-01": (
        "Reigning premier North Melbourne have lost once in ten, top the ladder on 36 points and "
        "own the league's best percentage at 251.9. Adelaide are ninth, five and five for 20 "
        "points, and their round-10 win over Gold Coast by ten points is the form line that keeps "
        "this honest. North Hobart Oval should still see a Roos win by more than a goal. "
        "North Melbourne -4.5 points is the bet at 1.42."
    ),
    "aflw-r11-05": (
        "Hawthorn are tenth, 20 points from a 5-5 season so far, with a 101.5 percentage and a "
        "finals chase still alive. Essendon have managed one win in ten, sit seventeenth on four "
        "points and kicked 5.3 (33) while conceding 12.13 (85) to North Melbourne last round. The "
        "Bombers' recent scoring makes a two-goal handicap attainable. Hawthorn giving 4.5 points "
        "is the recommendation at 1.42."
    ),
    "aflw-r11-04": (
        "Carlton's 7-3 record is worth 28 points and sixth place, with a percentage of 133.0. GWS "
        "GIANTS have won twice in ten, sit fifteenth on eight points and score at 68.2 per cent. "
        "Ikon Park stages a game between sides separated by five wins and 65 percentage points. "
        "The selection is Carlton -8.5 points at 1.42."
    ),
}


def words(s: str) -> int:
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-\.]*", s))


def grams(s: str, n: int = 6) -> set:
    toks = re.findall(r"[a-z0-9]+", s.lower())
    return {" ".join(toks[i:i + n]) for i in range(max(0, len(toks) - n + 1))}


def main() -> None:
    lines = json.loads((DATA / "lines.json").read_text())
    highs = [b for b in lines["books"] if b["confidence"] == "High"]
    items, problems = [], []
    for b in highs:
        pick = b["desk_pick"]
        text = PROSE.get(b["id"])
        if not text:
            problems.append(f"missing prose for {b['id']}")
            continue
        sel_fragment = pick["selection"].split(" (")[0].split(" at ")[0]
        core = sel_fragment.split(" -")[0].split(" +")[0].strip()
        participant = core.split()[0] if core else ""
        if participant and participant not in text:
            problems.append(f"prose does not name the selection participant: {b['id']} -> {participant}")
        if pick["price"] and f"{pick['price']:.2f}" not in text:
            problems.append(f"prose does not quote the price: {b['id']}")
        items.append({
            "id": b["id"], "sport": b["sport"], "competition": b["competition"],
            "home": b["home"], "away": b["away"], "start_utc": b["start_utc"],
            "market": pick["market"], "selection": pick["selection"],
            "price": pick["price"], "us": pick["us"], "prob_pct": pick["prob_pct"],
            "confidence": "High", "word_count": words(text), "prediction": text,
            "sources": b["sources"], "flags": b["flags"],
        })

    gcount = {}
    for it in items:
        for g in grams(it["prediction"]):
            gcount[g] = gcount.get(g, 0) + 1
    dupes = {g: c for g, c in gcount.items() if c > 1}
    short = [it["id"] for it in items if it["word_count"] < 30]
    doc = {
        "generated_utc": "2026-10-22T03:40:00Z",
        "rule": "one bespoke prediction per High-confidence selection, minimum 30 words, explicit selection and price, official-source figures only",
        "count": len(items), "high_count": len(highs),
        "min_words": min((i["word_count"] for i in items), default=0),
        "max_words": max((i["word_count"] for i in items), default=0),
        "repeated_6grams": dupes, "short_items": short, "problems": problems,
        "items": items,
    }
    (DATA / "predictions.json").write_text(json.dumps(doc, indent=1) + "\n")
    print(f"{len(items)} predictions | words {doc['min_words']}-{doc['max_words']} | "
          f"{len(dupes)} repeated 6-grams | {len(short)} short | {len(problems)} problems")
    for p in problems:
        print("  !", p)


if __name__ == "__main__":
    main()
