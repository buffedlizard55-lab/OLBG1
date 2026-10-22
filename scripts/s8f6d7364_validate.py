#!/usr/bin/env python3
"""T66 / 8f6d7364 — desk validator (gate for data, predictions and published pages).

Run: python3 scripts/s8f6d7364_validate.py   -> VALIDATION PASSED / FAILED
"""
import json, os, re, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "8f6d7364")
SITE = os.path.join(ROOT, "8f6d7364")
errors, warnings = [], []

def err(m): errors.append(m)
def warn(m): warnings.append(m)

FX = json.load(open(os.path.join(D, "fixtures.json")))
SRC = json.load(open(os.path.join(D, "sources.json")))
FLG = json.load(open(os.path.join(D, "flagged.json")))
LN = json.load(open(os.path.join(D, "lines.json")))
PR = json.load(open(os.path.join(D, "predictions.json")))
HARV = json.load(open(os.path.join(D, "harvest.json")))

SRC_BY = {s["id"]: s for s in SRC["sources"]}
FIX_BY = {f["id"]: f for f in FX["fixtures"]}
FLAG_IDS = {f["id"] for f in FLG["flags"]}

# ---- 1. every row: official source link OR blank+flag ------------------------
for f in FX["fixtures"]:
    if f["verified"]:
        if not f["sources"]:
            err(f'{f["id"]}: verified row without an official source id')
        for sid in f["sources"]:
            if sid not in SRC_BY:
                err(f'{f["id"]}: unknown source id {sid}')
            elif SRC_BY[sid]["role"] == "discovery":
                err(f'{f["id"]}: verified row citing only a discovery source')
        if not f["date"] and not f["time_text"]:
            if not f["flags"]:
                err(f'{f["id"]}: verified row with no date/time and no flag')
    else:
        if not f["flags"]:
            err(f'{f["id"]}: unverified row published without flags')
        if not f["fields_blank"]:
            err(f'{f["id"]}: unverified row does not list blanked fields')
        if f["id"] in {l["id"] for l in LN["fixtures"]}:
            err(f'{f["id"]}: unverified fixture is priced')
    for fl in f["flags"]:
        if fl not in FLAG_IDS:
            err(f'{f["id"]}: unknown flag {fl}')

# ---- 2. source role sanity ---------------------------------------------------
for s in SRC["sources"]:
    if s["role"] == "official" and "olbg.com" in s["url"]:
        err(f'{s["id"]}: OLBG cannot be an official source')
    if not s["observed"]:
        err(f'{s["id"]}: missing observation window')

# ---- 3. prices, tiers, gates -------------------------------------------------
def am_from_p(p):
    p = round(p, 6)
    return round(-100 * p / (1 - p), 1) if p >= 0.5 else round(100 * (1 - p) / p, 1)

def in_win(a): return -250.0 - 1e-9 <= a <= 10000.0

for fr in LN["fixtures"]:
    f = FIX_BY.get(fr["id"])
    if not f:
        err(f'lines entry {fr["id"]}: no fixture'); continue
    if not f["verified"]:
        err(f'{fr["id"]}: priced fixture is not officially verified')
    for m in fr["markets"]:
        p = m["p"]
        if not (0 < p < 1):
            err(f'{fr["id"]}: p out of range {p}'); continue
        if abs(m["fair_decimal"] - 1 / p) > 0.0011:
            err(f'{fr["id"]} {m["selection"]}: fair decimal {m["fair_decimal"]} != 1/p')
        if m["fair_american"] is None or abs(m["fair_american"] - am_from_p(p)) > 0.06:
            err(f'{fr["id"]} {m["selection"]}: american {m["fair_american"]} not re-derivable from p')
        if m["in_window"] != in_win(m["fair_american"]):
            err(f'{fr["id"]} {m["selection"]}: window flag inconsistent')
        tier = "High" if (p >= 0.700000 and in_win(m["fair_american"]) and f["verified"]) else \
               ("Medium" if p >= 0.55 else "Low")
        if m["market"] == "winner":
            pass
    # fixture tier is decided by the winner pick only
    wp = next((m for m in fr["markets"] if m["market"] == "winner" and m["selection"] == fr["pick"]), None)
    if wp is None:
        err(f'{fr["id"]}: pick does not match a winner market')
    else:
        expect = "High" if (wp["p"] >= 0.700000 and in_win(wp["fair_american"]) and f["verified"]) else \
                 ("Medium" if wp["p"] >= 0.55 else "Low")
        if fr["tier"] != expect:
            err(f'{fr["id"]}: tier {fr["tier"]} != expected {expect}')
        if abs(wp["p"] - fr["pick_p"]) > 1e-9:
            err(f'{fr["id"]}: pick_p mismatch')

# ---- 4. High selection gate + ledgers ---------------------------------------
for h in LN["ledgers"]["high_selections"]:
    f = FIX_BY[h["fixture_id"]]
    if h["p"] < 0.700000: err(f'High {h["fixture_id"]}: p below gate')
    if not in_win(h["fair_american"]): err(f'High {h["fixture_id"]}: outside price window')
    if not f["verified"]: err(f'High {h["fixture_id"]}: fixture unverified')
for o in LN["ledgers"]["out_of_window_ge70_winners"]:
    if o["p"] < 0.70 or in_win(o["fair_american"]):
        err(f'out-of-window ledger entry {o["fixture_id"]} inconsistent')
for n in LN["ledgers"]["near_band_winners_685_700"]:
    if not (0.685 <= n["p"] < 0.700000):
        err(f'near-band entry {n["fixture_id"]} inconsistent')

# ---- 5. predictions -----------------------------------------------------------
def wc(t): return len(re.findall(r"[A-Za-z0-9'%-]+", t))
def grams(t, n=6):
    w = re.findall(r"[a-z0-9'%-]+", t.lower())
    return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}

high_ids = {h["fixture_id"] for h in LN["ledgers"]["high_selections"]}
pred_ids = [p["fixture_id"] for p in PR["predictions"]]
if set(pred_ids) != high_ids:
    err(f'predictions {sorted(pred_ids)} != High fixtures {sorted(high_ids)}')
seen = set()
for p in PR["predictions"]:
    if wc(p["prose"]) < 30:
        err(f'{p["id"]}: prose {wc(p["prose"])} words < 30')
    g = grams(p["prose"])
    if seen & g:
        err(f'{p["id"]}: shares a 6-gram with another prediction')
    seen |= g
    if p["tier"] != "High":
        err(f'{p["id"]}: tier not High')
    h = next(x for x in LN["ledgers"]["high_selections"] if x["fixture_id"] == p["fixture_id"])
    if h["selection"] != p["selection"].split(" (")[0] and h["selection"] not in p["selection"]:
        err(f'{p["id"]}: selection text does not contain the model selection "{h["selection"]}"')
    if abs(h["p"] - p["model_p"]) > 1e-6:
        err(f'{p["id"]}: model_p mismatch')
    for fact in p["facts"]:
        src = fact.get("source", "")
        if "olbg.com" in src:
            err(f'{p["id"]}: fact cites OLBG — OLBG is not a fact source')
        if not src.startswith("https://"):
            err(f'{p["id"]}: fact source not an absolute official URL')
    if len(p["official_links"]) < 2:
        err(f'{p["id"]}: too few official links')

# ---- 6. harvest sanity ---------------------------------------------------------
if len(HARV["hubs"]) != 17:
    err(f'harvest hubs {len(HARV["hubs"])} != 17')
for h in HARV["hubs"]:
    if not h["olbg_url"].startswith("https://www.olbg.com/"):
        err(f'hub {h["sport"]}: not an OLBG discovery URL')

# ---- 7. site integrity ---------------------------------------------------------
expected = ["index.html", "matches.html", "markets.html", "high-confidence.html",
            "predictions.html", "analysis.html", "flagged.html", "sources.html",
            "methodology.html"] + [f"sports/{s}.html" for s, _ in
                                   [("ice-hockey",1),("baseball",1),("basketball",1),("tennis",1),
                                    ("cricket",1),("rugby-league",1),("rugby-union",1),("golf",1),
                                    ("motor-racing",1),("darts",1),("handball",1),("volleyball",1),
                                    ("aussie-rules",1),("esports",1),("gaelic-football",1),
                                    ("greyhounds",1),("snooker",1)]]
for rel in expected:
    if not os.path.exists(os.path.join(SITE, rel)):
        err(f'missing page: 8f6d7364/{rel}')

files = glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True)
for path in files:
    rel_dir = os.path.dirname(path)
    txt = open(path, encoding="utf-8").read()
    for bad in ("TODO", "lorem", "%%", "FIXME", "PLACEHOLDER"):
        if bad in txt:
            err(f'{os.path.relpath(path, ROOT)}: placeholder text {bad!r} present')
    for m in re.finditer(r'(?:href|src)="([^"#][^"]*)"', txt):
        href = m.group(1)
        if href.startswith(("http://", "https://", "mailto:", "data:")):
            continue
        target = os.path.normpath(os.path.join(rel_dir, href.split("#")[0]))
        if not os.path.exists(target):
            err(f'{os.path.relpath(path, ROOT)}: broken local link {href}')
    for m in re.finditer(r'href="([^"]*#[^"]+)"', txt):
        frag = m.group(1)
        if frag.startswith(("http", "mailto")):
            continue
        fpath, anchor = frag.split("#", 1)
        tgt = os.path.normpath(os.path.join(rel_dir, fpath)) if fpath else path
        if not os.path.exists(tgt):
            continue  # already reported above
        if anchor and f" id=\"{anchor}\"" not in open(tgt, encoding="utf-8").read() \
                and f"id={anchor}" not in open(tgt, encoding="utf-8").read():
            # flagged.html anchors
            if not re.search(rf'id="{re.escape(anchor)}"', open(tgt, encoding="utf-8").read()):
                err(f'{os.path.relpath(path, ROOT)}: missing anchor {frag}')

# matches count agreement
idx_txt = open(os.path.join(SITE, "index.html"), encoding="utf-8").read()
if f'>{len(FX["fixtures"])}</b><span>fixture rows' not in idx_txt:
    err('index tile fixture count mismatch')
mtch = open(os.path.join(SITE, "matches.html"), encoding="utf-8").read()
for f in FX["fixtures"]:
    if f'id="{f["id"]}"' not in mtch:
        err(f'matches.html missing row anchor {f["id"]}')

# predictions page anchors
pr_txt = open(os.path.join(SITE, "predictions.html"), encoding="utf-8").read()
for p in PR["predictions"]:
    if f'id="{p["id"]}"' not in pr_txt:
        err(f'predictions.html missing {p["id"]}')
    if p["prose"].split()[0] not in pr_txt:
        err(f'predictions.html missing prose for {p["id"]}')

print(f'checked: fixtures={len(FX["fixtures"])} sources={len(SRC["sources"])} flags={len(FLG["flags"])} '
      f'priced={len(LN["fixtures"])} high={len(LN["ledgers"]["high_selections"])} preds={len(PR["predictions"])} pages={len(files)}')
for w in warnings:
    print("WARN:", w)
for e in errors:
    print("ERROR:", e)
if errors:
    print(f"VALIDATION FAILED ({len(errors)} errors)")
    sys.exit(1)
print("VALIDATION PASSED (0 errors)")
