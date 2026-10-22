#!/usr/bin/env python3
"""Build desk.json, CSVs, and repo audit for a0b04058."""
import json
import csv
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))

import sa0b04058_data as D
import sa0b04058_model as M
import sa0b04058_predictions as P

DATA_DIR = ROOT / "data" / "a0b04058"
RAW_DIR = DATA_DIR / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)
RAW_DIR.mkdir(parents=True, exist_ok=True)

def main():
    # Validate predictions
    P.check_all()

    desk = M.assemble_desk()

    # Inject predictions into desk counts
    desk["counts"]["predictions"] = len(P.ALL_PREDICTIONS)
    # Build predictions list with full details
    pred_list = []
    # Map fixture_key to winner_pick and markets
    fixture_map = {f["fixture"]["key"]: f for f in desk["fixtures"]}

    for pred in P.ALL_PREDICTIONS:
        fkey = pred["fixture_key"]
        f_entry = fixture_map.get(fkey)
        if not f_entry:
            # For golf-bermuda etc where multiple predictions share same fixture, allow
            # Use first fixture that matches sport and contains player
            # Find by sport
            candidates = [x for x in desk["fixtures"] if x["fixture"]["sport"] == pred["sport"] and x["fixture"]["key"] == fkey]
            if not candidates:
                # For conditional Game5, fixture exists
                print(f"Warning: fixture {fkey} not found for prediction {pred['id']}")
                continue
            f_entry = candidates[0]

        # Build full prediction record
        prob_exact = f_entry["winner_pick"]["probability_exact"] if f_entry["priced"] and f_entry["winner_pick"] else pred["probability"]
        # For outright markets where selection is tournament winner, use pred probability
        # For those, winner_pick selection may differ from pred selection (e.g., Chandler Blanchet vs Ben Kohles share same fixture)
        # So we use pred's own probability for display, but keep official link
        pred_rec = {
            "id": pred["id"],
            "fixture_key": fkey,
            "sport": pred["sport"],
            "market": pred["market"],
            "selection": pred["selection"],
            "probability": pred["probability"],
            "probability_exact": pred.get("probability", prob_exact),
            "fair_american": pred["fair_american"],
            "fair_decimal": round(1.0/pred["probability"], 4) if pred["probability"]>0 else None,
            "tier": pred["tier"],
            "prediction_text": pred["prediction"],
            "word_count": len(pred["prediction"].split()),
            "sources": pred["sources"],
            "official_link": pred.get("official_link", f_entry["fixture"]["official_link"]),
            "olbg_hub": f_entry["fixture"]["olbg_hub"],
            "players": pred.get("players", []),
            "form": pred.get("form", ""),
            "recent_history": pred.get("recent_history", ""),
            "context": f_entry["fixture"]["context"],
            "model": f_entry["markets"][0]["model"] if f_entry["priced"] and f_entry["markets"] else pred.get("model", "unknown"),
            "rank_in_sport": pred.get("rank_in_sport", None),
        }
        # For outright where multiple predictions share fixture, we need to ensure selection matches an outcome
        # If not, we still keep but flag
        pred_list.append(pred_rec)

    desk["predictions"] = pred_list
    desk["counts"]["predictions"] = len(pred_list)

    # Per-sport top-5 daily slate
    from collections import defaultdict
    by_sport = defaultdict(list)
    for pr in pred_list:
        by_sport[pr["sport"]].append(pr)
    daily_top5 = {}
    for sport, lst in by_sport.items():
        # sort by probability descending
        sorted_lst = sorted(lst, key=lambda x: x["probability"], reverse=True)
        daily_top5[sport] = sorted_lst[:5]

    desk["daily_top5"] = {k: [x["id"] for x in v] for k, v in daily_top5.items()}

    # Flags for review
    flags = []
    # Unpriced reasons
    for f in desk["fixtures"]:
        if not f["priced"]:
            flags.append({
                "id": f"FLAG-{f['fixture']['key']}",
                "fixture_key": f["fixture"]["key"],
                "sport": f["fixture"]["sport"],
                "reason": f["unpriced_reason"],
                "official_link": f["fixture"]["official_link"],
                "olbg_hub": f["fixture"]["olbg_hub"],
            })
    # Out-of-window strong favorites
    for f in desk["fixtures"]:
        if f["priced"] and f["winner_pick"]:
            if not f["winner_pick"]["gate_a_literal"] and f["winner_pick"]["probability_exact"] > M.WINDOW_EDGE_PROB:
                flags.append({
                    "id": f"FLAG-OOW-{f['fixture']['key']}",
                    "fixture_key": f["fixture"]["key"],
                    "sport": f["fixture"]["sport"],
                    "reason": f["winner_pick"]["reason"],
                    "selection": f["winner_pick"]["selection"],
                    "probability": f["winner_pick"]["probability"],
                    "fair_american": M.american_from_prob(f["winner_pick"]["probability_exact"])[0],
                    "official_link": f["fixture"]["official_link"],
                    "olbg_hub": f["fixture"]["olbg_hub"],
                })
    # High blocked
    for k, reason in M.HIGH_BLOCKED.items():
        flags.append({
            "id": f"FLAG-BLOCKED-{k}",
            "fixture_key": k,
            "sport": "basketball",
            "reason": reason,
            "official_link": "https://www.euroleaguebasketball.net/en/euroleague/news/injury-report-round-7-fantasy/",
            "olbg_hub": "https://www.olbg.com/betting-tips/Basketball/4",
        })
    # Coverage gaps: sports with <5 priced fixtures
    for slug, stats in desk["per_sport"].items():
        if stats["fixtures"] < 5:
            flags.append({
                "id": f"FLAG-GAP-{slug}",
                "sport": slug,
                "reason": f"Only {stats['fixtures']} fixtures verified for {slug}, less than 5 daily target, gap disclosed",
                "official_link": D.SOURCES[0]["url"] if D.SOURCES else "",
                "olbg_hub": f"https://www.olbg.com/betting-tips/{slug}/X",
            })
        if stats["priced"] < 5:
            flags.append({
                "id": f"FLAG-PRICED-GAP-{slug}",
                "sport": slug,
                "reason": f"Only {stats['priced']} priced fixtures for {slug}, less than 5 daily high-confidence target, remaining unpriced and flagged",
                "official_link": next((s["url"] for s in D.SOURCES if s["sport"]==slug), ""),
                "olbg_hub": f"https://www.olbg.com/betting-tips/{slug}/X",
            })

    desk["flags"] = flags
    desk["counts"]["flagged"] = len(flags)
    desk["counts"]["sources"] = len(D.SOURCES)
    desk["counts"]["audit"] = len(D.REPO_AUDIT_FINDINGS)

    # Write desk.json
    (DATA_DIR / "desk.json").write_text(json.dumps(desk, indent=2), encoding="utf-8")

    # Write fixtures.csv
    with open(DATA_DIR / "fixtures.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["key","sport","sport_name","competition","away","home","away_name","home_name","date","time_utc","venue","status","event_id","priced","tier","selection","probability","fair_decimal","fair_american","official_link","olbg_hub","unpriced_reason"])
        for fp in desk["fixtures"]:
            fi = fp["fixture"]
            wp = fp["winner_pick"]
            if wp:
                sel = wp["selection"]
                prob = wp["probability"]
                amer = M.american_from_prob(wp["probability_exact"])[0]
                dec = round(1.0/wp["probability_exact"],4)
                tier = wp["tier"]
            else:
                sel = ""
                prob = ""
                amer = ""
                dec = ""
                tier = ""
            writer.writerow([
                fi["key"], fi["sport"], fi["sport_name"], fi["competition"],
                fi["away"], fi["home"], fi.get("away_name",""), fi.get("home_name",""),
                fi["date"], fi["time_utc"], fi["venue"], fi["status"], fi["event_id"],
                fp["priced"], tier, sel, prob, dec, amer,
                fi["official_link"], fi["olbg_hub"], fp["unpriced_reason"] or ""
            ])

    # Write markets.csv
    with open(DATA_DIR / "markets.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["fixture_key","sport","market","family","model","inputs","selection","probability","probability_exact","fair_decimal","fair_american","in_window"])
        for fp in desk["fixtures"]:
            if not fp["priced"]:
                continue
            for m in fp["markets"]:
                for o in m["outcomes"]:
                    writer.writerow([
                        fp["fixture"]["key"], fp["fixture"]["sport"],
                        m["market"], m["family"], m["model"], m["inputs"],
                        o["selection"], o["probability"], o["probability_exact"],
                        o["fair_decimal"], o["fair_american"], o["in_brief_window"]
                    ])

    # Write repo_audit.json
    (DATA_DIR / "repo_audit.json").write_text(json.dumps(D.REPO_AUDIT_FINDINGS, indent=2), encoding="utf-8")

    # Write sources.json
    (DATA_DIR / "sources.json").write_text(json.dumps({"as_of_utc": D.AS_OF_UTC, "count": len(D.SOURCES), "sources": D.SOURCES}, indent=2), encoding="utf-8")

    print(f"Built desk: {desk['counts']}")
    return desk

if __name__ == "__main__":
    main()
