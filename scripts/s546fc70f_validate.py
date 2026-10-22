"""Validation gate for the 546fc70f desk. Exits non-zero on any error."""
import json, os, re, sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "546fc70f")
DATA = os.path.join(ROOT, "data", "546fc70f")
OFFICIAL_HOSTS = ("api-live.euroleague.net", "api-web.nhle.com", "statsapi.mlb.com", "cdn.nba.com", "www.atptour.com")
errors, warnings = [], []


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs, self.rows, self.in_tr, self.row_links, self.row_text = [], [], False, [], []
        self.in_table_row_has_td = False
        self.cur = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and "href" in a:
            self.hrefs.append(a["href"])
            if self.in_tr:
                self.row_links.append(a["href"])
        if tag == "tr":
            self.in_tr = True
            self.row_links = []
            self.row_td = 0
        if tag == "td":
            self.row_td = getattr(self, "row_td", 0) + 1

    def handle_endtag(self, tag):
        if tag == "tr" and self.in_tr:
            if getattr(self, "row_td", 0) > 0:          # data rows only (skip header rows made of <th>)
                self.rows.append(list(self.row_links))
            self.in_tr = False


def check_links(path):
    p = Parser()
    p.feed(open(path, encoding="utf-8").read())
    base = os.path.dirname(path)
    for h in p.hrefs:
        if h.startswith(("http://", "https://", "mailto:")) or h.startswith("#"):
            continue
        target = h.split("#")[0]
        if not os.path.exists(os.path.normpath(os.path.join(base, target))):
            errors.append(f"broken relative link {h} in {os.path.relpath(path, ROOT)}")
    return p


def main():
    model = json.load(open(os.path.join(DATA, "model_output.json"), encoding="utf-8"))
    preds = json.load(open(os.path.join(DATA, "predictions.json"), encoding="utf-8"))

    # 1. pages exist and internal links resolve
    pages = []
    for dp, _, fs in os.walk(OUT):
        for f in fs:
            if f.endswith(".html"):
                pages.append(os.path.join(dp, f))
    for pg in pages:
        p = check_links(pg)
        rel = os.path.relpath(pg, OUT)
        if rel in ("matches.html", "markets.html") or rel.startswith("sports" + os.sep):
            for i, row in enumerate(p.rows):
                if not any(any(h.startswith("https://" + x) for x in OFFICIAL_HOSTS) for h in row):
                    if rel.startswith("sports" + os.sep) and os.path.basename(rel) == "tennis.html":
                        continue
                    errors.append(f"{rel}: data row {i} has no official-host source link")
    # 2. predictions: word count, team names, tier gate, numbers match the model
    fix = {}
    by_game = {}
    for f in model["fixtures"]:
        by_game[str(f["game_no"])] = f
        for k in f["markets"]:
            if k["market"].startswith("Match winner"):
                fix.setdefault(str(f["game_no"]), {})[k["selection"]] = k
    for p in preds:
        words = len(re.findall(r"\S+", p["text"]))
        if words < 30:
            errors.append(f"{p['id']} has {words} words (<30)")
        if p["selection"].split(" to beat")[0] not in p["text"]:
            errors.append(f"{p['id']} selection team not named in text")
        if not all(s.startswith("https://") for s in p["sources"]):
            errors.append(f"{p['id']} source not https")
        key = str(p["game_key"])
        if key not in fix:
            errors.append(f"{p['id']} game {key} not found in model output")
            continue
        mf = by_game[key]
        NHL_NAME = {"BOS": "Boston Bruins", "OTT": "Ottawa Senators", "NYR": "New York Rangers", "NJD": "New Jersey Devils",
                    "TOR": "Toronto Maple Leafs", "NSH": "Nashville Predators", "SJS": "San Jose Sharks", "ANA": "Anaheim Ducks"}
        def model_name(code):
            return NHL_NAME.get(code, code).upper()
        def same(model_code, pred_name):
            mn = model_name(model_code) if mf["sport"].startswith("NHL") else model_code.upper()
            return pred_name.upper().startswith(mn) or mn.startswith(pred_name.upper())
        if not (same(mf["home"], p["home"]) and same(mf["away"], p["away"])):
            errors.append(f"{p['id']} teams differ from model fixture {mf['home']} v {mf['away']}")
        sel_name = p["selection"].split(" to beat")[0]
        cands = [kk for kk in fix[key].keys() if same(kk, sel_name)] if not mf["sport"].startswith("NHL") else [kk for kk in fix[key].keys() if kk == next((c for c, n in NHL_NAME.items() if n == sel_name), "")]
        k = fix[key][cands[0]] if cands else None
        if k is None:
            errors.append(f"{p['id']} selection not a winner row in model")
            continue
        if abs(round(k["p"], 4) - p["model_p"]) > 1e-4 or k["american"] != p["fair_american"]:
            errors.append(f"{p['id']} numbers disagree with model_output ({k['p']} {k['american']})")
        if p["tier"] == "High" and not (k["p"] > 0.70 and -250 <= k["american"] <= 10000):
            errors.append(f"{p['id']} labelled High but fails the strict gate")
        if p["tier"] != k["tier"]:
            errors.append(f"{p['id']} tier {p['tier']} disagrees with model tier {k['tier']}")
    # 3. High picks: none may appear on pages unless the gate passes
    hc = open(os.path.join(OUT, "index.html"), encoding="utf-8").read()
    m = re.search(r'<div class="kpi"><b>(\d+)</b>High picks', hc)
    if not m or int(m.group(1)) != sum(1 for f in model["fixtures"] for k in f["markets"] if k["market"].startswith("Match winner") and k["tier"] == "High"):
        errors.append("index High KPI disagrees with model output")
    # 4. warnings (not blocking): near-boundary items
    for f in model["fixtures"]:
        for k in f["markets"]:
            if k["market"].startswith("Match winner") and 0.695 < k["p"] <= 0.705:
                warnings.append(f"{f['home']} v {f['away']} winner p near 70%: {k['p']}")

    print(f"pages checked: {len(pages)}; predictions checked: {len(preds)}; markets: {sum(len(f['markets']) for f in model['fixtures'])}")
    for w in warnings:
        print("WARN", w)
    for e in errors:
        print("ERROR", e)
    print("VALIDATION", "PASSED" if not errors else "FAILED", f"({len(errors)} errors, {len(warnings)} warnings)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
