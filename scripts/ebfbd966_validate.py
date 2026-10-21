#!/usr/bin/env python3
"""Validation gate: fails loudly if any publishing rule is broken.
Rules: every match has OLBG + official links; every HIGH has a >=30-word unique writeup naming
its selection; no excluded sport present; probabilities sane; all internal site links resolve;
no linear-gradient CSS (design rule); flagged/contested rows are LOW; blank stays blank
(None tips never become numbers); CSV row count matches JSON.
"""
import json, pathlib, re, sys, csv, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT/"ebfbd966"
M = json.loads((ROOT/"data"/"ebfbd966_matches.json").read_text())
L = json.loads((ROOT/"data"/"ebfbd966_lines.json").read_text())["lines"]
W = json.loads((ROOT/"data"/"ebfbd966_writeups.json").read_text())["writeups"]
errors, warns = [], []
EXCLUDED = ["football","soccer","boxing","ufc","mma","american football","hurling","horse racing","cycling","specials"]

for m in M["matches"]:
    i = m["id"]; ln = L.get(i)
    if not ln: errors.append(f"{i}: no originated line"); continue
    if not m["olbg_url"].startswith("https://www.olbg.com/betting-tips/"): errors.append(f"{i}: bad OLBG url")
    if not m["official_url"].startswith("https://"): errors.append(f"{i}: bad official url")
    if not m["official_label"].strip(): errors.append(f"{i}: blank official label")
    if ln["confidence"] not in ("LOW","MEDIUM","HIGH"): errors.append(f"{i}: bad confidence")
    if not (0 < ln["pick_prob"] < 1): errors.append(f"{i}: bad probability")
    s = ln["pick_prob"] + ln["other_prob"] + (ln["draw_prob"] or 0)
    if abs(s-1) > 0.01: errors.append(f"{i}: probabilities sum to {s:.3f}")
    if m.get("verification")=="CONTESTED" and ln["confidence"]!="LOW": errors.append(f"{i}: CONTESTED but not LOW")
    if m.get("tips_for") is None and ln["confidence"]!="LOW": errors.append(f"{i}: unverified tips but not LOW")
    if any(f.startswith("IRREGULARITY") for f in m.get("flags",[])) and ln["confidence"]=="HIGH": errors.append(f"{i}: irregularity flagged but HIGH")
    sport_l = m["sport"].lower()
    if sport_l in EXCLUDED: errors.append(f"{i}: excluded sport present: {m['sport']}")
    if m["sport"]=="Cricket" and (ln["handicap_line"] is not None or ln["total_line"] is not None):
        errors.append(f"{i}: cricket handicap/total must be n/a")
    if ln["confidence"]=="HIGH":
        w = W.get(i)
        if not w: errors.append(f"{i}: HIGH without writeup")
        else:
            wc = len(w["text"].split())
            if wc < 30: errors.append(f"{i}: writeup only {wc} words (<30)")
            if ln["pick"].split()[0] not in w["text"] and ln["pick"] not in w["text"]:
                warns.append(f"{i}: writeup may not name pick '{ln['pick']}' — manual read")
            if "selection is" not in w["text"].lower(): warns.append(f"{i}: writeup lacks explicit 'selection is' statement")
# uniqueness of writeups
texts = [w["text"] for w in W.values()]
if len(set(texts)) != len(texts): errors.append("duplicate writeup text")
# generic-phrase repetition guard: no 8-word shingle shared across writeups
def shingles(t, n=8):
    words = t.lower().split(); return {" ".join(words[i:i+n]) for i in range(len(words)-n+1)}
owner = {}
for k, w in W.items():
    for sh in shingles(w["text"]):
        if sh in owner and owner[sh] != k: errors.append(f"repeated 8-word passage in {k} and {owner[sh]}: '{sh}…'")
        owner[sh] = k
# internal links
pages = list(DOCS.rglob("*.html"))
existing = {str(p.relative_to(DOCS)).replace("\\","/") for p in DOCS.rglob("*") if p.is_file()}
for p in pages:
    html = p.read_text()
    for href in re.findall(r'href="([^"#]+)"', html):
        if href.startswith(("http://","https://","mailto:")): continue
        target = href
        base = str(p.parent.relative_to(DOCS)).replace("\\","/")
        parts = [] if base=="." else base.split("/")
        for seg in target.split("/"):
            if seg=="..": parts and parts.pop()
            elif seg not in ("","."): parts.append(seg)
        rel = "/".join(parts)
        if rel not in existing: errors.append(f"{p.name}: broken internal link '{href}' -> '{rel}'")
css = (DOCS/"assets"/"style.css").read_text()
if "linear-gradient" in css: errors.append("linear-gradient present in CSS (design rule)")
rows = list(csv.DictReader(open(DOCS/"data"/"matches.csv")))
if len(rows) != len(M["matches"]): errors.append(f"CSV rows {len(rows)} != matches {len(M['matches'])}")
print(f"Matches: {len(M['matches'])} | HIGH/MED/LOW: {collections.Counter(L[m['id']]['confidence'] for m in M['matches'])}")
print(f"Pages: {len(pages)} | Writeups: {len(W)} (words: {[len(w['text'].split()) for w in W.values()]})")
for w_ in warns: print("WARN:", w_)
if errors:
    print(f"\n{len(errors)} ERRORS:"); [print(" -", e) for e in errors]; sys.exit(1)
print("VALIDATION PASSED")
