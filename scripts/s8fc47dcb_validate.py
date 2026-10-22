"""
s8fc47dcb_validate.py — gate for the T57 desk. Fails (exit 1) on any error.
Checks data integrity, strict-High rules, prose rules, per-row official
sources, and internal link integrity across the generated namespace.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "8fc47dcb"
SITE = ROOT / "8fc47dcb"
errors, warnings = [], []


def err(msg):
    errors.append(msg)


def main():
    ds = json.loads((DATA / "dataset.json").read_text())
    preds = json.loads((DATA / "predictions.json").read_text())["items"]
    ver = json.loads((DATA / "verification.json").read_text())["rows"]
    rows = ds["rows"]
    cutoff = ds["cutoff_utc"]
    ver_ids = {v["match_id"] for v in ver}

    if len(rows) != ds["counts"]["future"] or len(ver) != len(rows):
        err(f"count mismatch rows={len(rows)} verification={len(ver)} future={ds['counts']['future']}")
    for r in rows:
        f = r["fixture"]
        if (f.get("start_utc") or "") < cutoff:
            err(f"{f['id']}: expired/undated row in future desk")
        if f["id"] not in ver_ids:
            err(f"{f['id']}: missing verification row")
        if not f["sources"] or not all(s.get("url", "").startswith("https://") for s in f["sources"]):
            err(f"{f['id']}: missing official source link(s)")
        if not r["priced"]:
            continue
        psum = sum(o["probability"] for mk in r["markets"] if mk["key"] == "winner" for o in mk["outcomes"])
        if abs(psum - 1.0) > 2e-3:
            err(f"{f['id']}: winner probabilities sum {psum}")
        for mk in r["markets"]:
            s = sum(o["probability"] for o in mk["outcomes"])
            if abs(s - 1.0) > 2e-3:
                err(f"{f['id']}/{mk['key']}: market probabilities sum {s}")
            for o in mk["outcomes"]:
                if not (1.01 <= o["fair_odds"] <= 99.0):
                    err(f"{f['id']}/{mk['key']}: fair odds out of range {o['fair_odds']}")
        if r["confidence"] == "high":
            sel = r["strict_selection"]
            if not sel:
                err(f"{f['id']}: High without strict selection")
                continue
            if not (0.70 <= sel["probability"] <= 1 / 1.40 + 1e-9):
                err(f"{f['id']}: High probability {sel['probability']} outside exact 70-71.4286% band")
            if not (1.40 <= sel["fair_odds"] <= 101.0):
                err(f"{f['id']}: High fair odds {sel['fair_odds']} outside 1.40-101 window (-250..+10000)")
            if not all(r["gates"].values()):
                err(f"{f['id']}: High with failed gate(s) {r['gates']}")
            if r["verification_status"] not in ("confirmed", "corrected"):
                err(f"{f['id']}: High not re-verified this session")
        elif r["strict_selection"] and all(r["gates"].values()):
            err(f"{f['id']}: passes all gates but tier is {r['confidence']}")

    high_ids = {r["fixture"]["id"] for r in rows if r.get("confidence") == "high"}
    if {p["match_id"] for p in preds} != high_ids:
        err(f"prediction ids != high ids: {sorted({p['match_id'] for p in preds} ^ high_ids)}")
    texts = []
    for p in preds:
        w = len(p["text"].split())
        if w < 30 or w != p["words"]:
            err(f"{p['match_id']}: prediction words {w} (stored {p['words']})")
        if p["selection"].split(" +")[0].split(" -")[0] not in p["text"]:
            err(f"{p['match_id']}: selected team/player not named in prose")
        if not any(k in p["text"] for k in ("selection is", "bet is", "play is", "Back ", "take ")):
            err(f"{p['match_id']}: betting selection not obvious in prose")
        if not p["recheck_sources"]:
            err(f"{p['match_id']}: prediction without in-session official source")
        texts.append(p["text"].lower())
    def ngrams(t, n=6):
        words = re.sub(r"[^a-z0-9 ]", " ", t).split()
        return {" ".join(words[i:i + n]) for i in range(len(words) - n + 1)}
    seen = {}
    for p, t in zip(preds, texts):
        for g in ngrams(t):
            if g in seen:
                err(f"duplicate 6-gram between {seen[g]} and {p['match_id']}: '{g}'")
            seen[g] = p["match_id"]

    pages = sorted(SITE.rglob("*.html"))
    if len(pages) < 20:
        err(f"too few pages: {len(pages)}")
    broken = 0
    for page in pages:
        txt = page.read_text()
        for href in re.findall(r'href="([^"#]+)', txt):
            if href.startswith(("http://", "https://", "mailto:")):
                continue
            target = (page.parent / href.split("#")[0]).resolve()
            # links escaping the namespace (primary desk) resolve against repo root files
            if not target.exists():
                err(f"{page.relative_to(SITE)}: broken internal link {href}")
                broken += 1
    idx = (SITE / "index.html").read_text()
    for needle in ("strict High", "Flagged for Review", "not betting advice"):
        if needle not in idx:
            warnings.append(f"index missing '{needle}'")

    print(f"rows={len(rows)} priced={sum(1 for r in rows if r['priced'])} high={len(high_ids)} preds={len(preds)} pages={len(pages)} broken_links={broken}")
    for w in warnings:
        print("WARN:", w)
    for m in errors:
        print("ERROR:", m)
    print("VALIDATION PASSED" if not errors else f"VALIDATION FAILED ({len(errors)} errors)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
