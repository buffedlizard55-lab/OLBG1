#!/usr/bin/env python3
"""Validate a4803a7b desk against band, word count, banned words, 7-gram uniqueness."""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESK = ROOT / "data/a4803a7b/desk.json"

def load():
    return json.loads(DESK.read_text())

def main():
    j=load()
    fixtures=j["fixtures"]
    ok=True
    # band
    for f in fixtures:
        if f["confidence"]=="High":
            if not (1.40 <= f["decimal"] <= 101.0):
                print(f"FAIL High band {f['id']} dec {f['decimal']}")
                ok=False
            if f["p"] < 0.60 - 1e-9:
                print(f"FAIL High prob {f['id']} p {f['p']}")
                ok=False
        if f["confidence"]=="Medium":
            if not (1.40 <= f["decimal"] <= 101.0):
                print(f"FAIL Medium band {f['id']} dec {f['decimal']}")
                ok=False
            if f["p"] < 0.55 -1e-9:
                print(f"FAIL Medium prob {f['id']} p {f['p']}")
                ok=False
        # 30-word min (we enforce 48)
        wc=len(f["prediction"].split())
        if wc < 48:
            print(f"FAIL word count {f['id']} {wc}")
            ok=False
        if f["selection"] not in f["prediction"]:
            print(f"FAIL selection missing {f['id']}")
            ok=False
        if re.search(r"\b(unsure|perhaps|maybe|might|could be|possibly)\b", f["prediction"], re.I):
            print(f"FAIL banned phrase {f['id']}")
            ok=False
        if not f["official_url"]:
            print(f"FAIL official_url missing {f['id']}")
            ok=False
    # 7-gram
    seen=set()
    for f in fixtures:
        toks=re.findall(r"\w+", f["prediction"].lower())
        grams=set(tuple(toks[i:i+7]) for i in range(len(toks)-6))
        inter=grams & seen
        if inter:
            print(f"FAIL 7-gram dup {f['id']} e.g. {next(iter(inter))}")
            ok=False
        seen|=grams
    # sport coverage
    from collections import Counter
    c=Counter(f["sport"] for f in fixtures)
    for sport, n in c.items():
        if n < 5:
            print(f"FAIL sport count {sport} {n}")
            ok=False
    print(f"Fixtures: {len(fixtures)} Sports: {len(c)} High: {sum(1 for f in fixtures if f['confidence']=='High')} Medium: {sum(1 for f in fixtures if f['confidence']=='Medium')} Low: {sum(1 for f in fixtures if f['confidence']=='Low')}")
    print("VALIDATION","PASSED" if ok else "FAILED")
    sys.exit(0 if ok else 1)

if __name__=="__main__":
    main()
