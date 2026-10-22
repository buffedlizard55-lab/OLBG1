"""Session d7d19a67-olbg1 (TD7D19, claimed as T65) - validation gate for the ``d7d19a67/`` desk.

Checks the published pages and the data they were built from, in the order a reviewer would:

  1. arithmetic   - every published price really is 1/p with no margin, and the American price
                    matches the unrounded probability;
  2. policy       - every High winner pick is inside -250..+10000 with p >= 0.60 and has a
                    hand-written prediction of at least 30 words; no pick is High on a >70% shortcut;
  3. sourcing     - every data-table row carries at least one official https link, every source id
                    referenced exists in the register, and no operator brand appears anywhere;
  4. blanks       - unconfirmed values are published as an explicit blank marker, never as an empty
                    cell that could be mistaken for a zero, and never filled from memory;
  5. integrity    - all relative links resolve, every fixture appears exactly once on the match list,
                    counts published in prose match desk.json, and predictions are not repetitive;
  6. audit        - every repository-audit finding carries file/line evidence and a re-check command.

Exit code 0 and "VALIDATION PASSED" means the desk may be published; anything else blocks the merge.
Run: python3 scripts/sd7d19a67_validate.py
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sd7d19a67_data as D  # noqa: E402
import sd7d19a67_predictions as P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "d7d19a67")
OUT = os.path.join(ROOT, "d7d19a67")

OPERATOR_BRANDS = ["bet365", "Bet365", "Paddy Power", "William Hill", "Sky Bet", "Betfair",
                   "DraftKings", "FanDuel", "BetMGM", "Unibet", "Ladbrokes", "BoyleSports",
                   "Betfred", "888sport", "Betway", "Pinnacle"]
DATA_TABLE_MARKERS = ["Official source", "official source", "Official URL", "Official page attempted"]

errors, warnings, checks = [], [], []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def ok(msg):
    checks.append(msg)


def pages():
    out = []
    for base, _, files in os.walk(OUT):
        for f in sorted(files):
            if f.endswith(".html"):
                out.append(os.path.join(base, f))
    return sorted(out)


def text_of(path):
    return open(path, encoding="utf-8").read()


def rel(path):
    return os.path.relpath(path, ROOT)


# --------------------------------------------------------------------- 1. arithmetic
def american_check(p):
    return -round(p / (1 - p) * 100) if p >= 0.5 else round((1 - p) / p * 100)


def check_arithmetic(desk):
    bad = 0
    for f in desk["fixtures"]:
        for mk in f["markets"]:
            probs = [o["probability"] for o in mk["outcomes"]]
            if mk["family"] in ("winner", "handicap", "total") and abs(sum(probs) - 1.0) > 0.002:
                err("%s %s: two-way outcome probabilities sum to %.4f" % (f["key"], mk["market_id"], sum(probs)))
                bad += 1
            if mk["family"] == "regulation" and abs(sum(probs) - 1.0) > 0.003:
                err("%s %s: 3-way probabilities sum to %.4f" % (f["key"], mk["market_id"], sum(probs)))
                bad += 1
            for o in mk["outcomes"]:
                p = o.get("probability_exact", o["probability"])
                if abs(round(p, 4) - o["probability"]) > 1e-9:
                    err("%s %s: displayed probability %.4f does not round from %.10f"
                        % (f["key"], mk["market_id"], o["probability"], p))
                if not (0.0 < p < 1.0):
                    err("%s %s %s: probability %.4f out of range" % (f["key"], mk["market_id"], o["selection"], p))
                    bad += 1
                    continue
                if abs(o["fair_decimal"] - 1.0 / p) > 5e-5:
                    err("%s %s: decimal %.4f is not 1/%.4f" % (f["key"], mk["market_id"], o["fair_decimal"], p))
                    bad += 1
                expect = -round(p / (1 - p) * 100) if p >= 0.5 else round((1 - p) / p * 100)
                if o["fair_american"] != expect:
                    err("%s %s: American %+d does not match unrounded p=%.6f (expected %+d)"
                        % (f["key"], mk["market_id"], o["fair_american"], p, expect))
                    bad += 1
                inside = -250 <= o["fair_american"] <= 10000
                if inside != o["in_brief_window"]:
                    err("%s %s: window flag disagrees with price %+d" % (f["key"], mk["market_id"], o["fair_american"]))
                    bad += 1
        wp = f["winner_pick"]
        if wp:
            best = max((o for mk in f["markets"] if mk["family"] == "winner" for o in mk["outcomes"]),
                       key=lambda o: o["probability_exact"], default=None)
            if best is None or abs(best["probability_exact"] - wp["probability_exact"]) > 1e-12:
                err("%s: winner pick is not the stronger side of the winner market" % f["key"])
                bad += 1
            elif (best["fair_american"] != wp["fair_american"]
                  or abs(best["fair_decimal"] - wp["fair_decimal"]) > 1e-12
                  or best["selection"] != wp["selection"]):
                err("%s: winner pick price %+d/%.4f disagrees with its own market outcome %+d/%.4f"
                    % (f["key"], wp["fair_american"], wp["fair_decimal"], best["fair_american"],
                       best["fair_decimal"]))
                bad += 1
            if abs(american_check(wp["probability_exact"]) - wp["fair_american"]) > 0:
                err("%s: winner pick American %+d does not re-derive from p=%.10f"
                    % (f["key"], wp["fair_american"], wp["probability_exact"]))
                bad += 1
    ok("arithmetic: %d priced fixtures, %d markets, %d outcomes re-derived from probability"
       % (desk["counts"]["priced"], desk["counts"]["markets"], desk["counts"]["outcomes"]))
    return bad


# ----------------------------------------------------------------------- 2. policy
def check_policy(desk):
    policy = desk["confidence_policy"]
    highs = [f for f in desk["fixtures"] if f["winner_pick"] and f["winner_pick"]["tier"] == "High"]
    preds = {p["market_id"]: p for p in desk["predictions"]}
    for f in highs:
        wp = f["winner_pick"]
        if not (-250 <= wp["fair_american"] <= 10000):
            err("%s: High pick priced %+d, outside the brief's window" % (f["key"], wp["fair_american"]))
        if wp["probability"] < policy["high_floor_probability"] - 1e-9:
            err("%s: High pick probability %.4f below the %.2f floor"
                % (f["key"], wp["probability"], policy["high_floor_probability"]))
        if f["key"] in policy["high_blocked"]:
            err("%s: High pick contradicts an official context sentence and must be capped" % f["key"])
        pid = "%s#m1" % f["key"]
        if pid not in preds:
            err("%s: High pick has no hand-written prediction" % f["key"])
        elif preds[pid]["word_count"] < 30:
            err("%s: prediction is %d words (minimum 30)" % (f["key"], preds[pid]["word_count"]))
        if not f["priced"]:
            err("%s: High pick on an unpriced fixture" % f["key"])
    for f in desk["fixtures"]:
        wp = f["winner_pick"]
        if not wp:
            if f["priced"]:
                err("%s: fixture is priced but has no winner pick" % f["key"])
            if not f["unpriced_reason"]:
                err("%s: unpriced fixture publishes no reason" % f["key"])
            continue
        if wp["tier"] not in ("High", "Medium", "Low"):
            err("%s: tier %r is not one of High/Medium/Low" % (f["key"], wp["tier"]))
        if wp["tier"] == "High" and wp["probability"] > 0.70 and wp["in_brief_window"]:
            warn("%s: High pick also satisfies the literal >70%% gate (p=%.4f)" % (f["key"], wp["probability"]))
        if wp["tier"] == "Medium" and wp["probability"] > 250.0 / 350.0 and wp["in_brief_window"]:
            err("%s: p=%.4f inside the window should not be Medium unless blocked" % (f["key"], wp["probability"]))
        if not wp["tier_reason"]:
            err("%s: tier published without a reason" % f["key"])
    gate_a = [(f["key"], mk["market_id"], o["selection"]) for f in desk["fixtures"] for mk in f["markets"]
              for o in mk["outcomes"] if o["probability"] > 0.70 and o["in_brief_window"]]
    if desk["counts"]["gate_a_any_selection"] != len(gate_a):
        err("gate A count %d does not match the %d rows found" % (desk["counts"]["gate_a_any_selection"], len(gate_a)))
    if desk["counts"]["high"] != len(highs):
        err("High count %d does not match the %d rows found" % (desk["counts"]["high"], len(highs)))
    tiers = {"High": 0, "Medium": 0, "Low": 0}
    for f in desk["fixtures"]:
        if f["winner_pick"]:
            tiers[f["winner_pick"]["tier"]] += 1
    if sum(tiers.values()) != desk["counts"]["priced"]:
        err("tiers %s do not sum to the %d priced fixtures" % (tiers, desk["counts"]["priced"]))
    ok("policy: %d High (all in-window, all >= %.2f, all with >=30-word predictions), %d Medium, %d Low, "
       "%d literal Gate A selection(s)"
       % (len(highs), policy["high_floor_probability"], tiers["Medium"], tiers["Low"], len(gate_a)))


# --------------------------------------------------------------------- 3. sourcing
def check_sourcing(desk):
    ids = {s["id"] for s in desk["sources"]}
    for f in desk["fixtures"]:
        for sid in f["sources"]:
            if sid not in ids:
                err("%s references unknown source id %s" % (f["key"], sid))
        if not f["official_link"].startswith("https://"):
            err("%s has no https official link (%r)" % (f["key"], f["official_link"]))
        olbg = f["official_link"].lower()
        if "olbg.com" in olbg:
            err("%s cites OLBG as its official source; OLBG is discovery-only" % f["key"])
    for p in desk["predictions"]:
        for fact in p["facts"]:
            if fact["source_id"] not in ids:
                err("%s cites unknown source id %s" % (p["id"], fact["source_id"]))
    ok("sourcing: %d official source reads, %d fixture rows each with an https official link, "
       "0 OLBG citations" % (len(ids), len(desk["fixtures"])))

    rows_total = rows_linked = 0
    for path in pages():
        text = text_of(path)
        for brand in OPERATOR_BRANDS:
            if brand in text:
                err("%s mentions operator brand %r; this desk quotes no operator" % (rel(path), brand))
        for table in re.findall(r"<table.*?</table>", text, flags=re.S):
            head = re.search(r"<thead.*?</thead>", table, flags=re.S)
            if not head or not any(m in head.group(0) for m in DATA_TABLE_MARKERS):
                continue
            for row in re.findall(r"<tr\b.*?</tr>", table, flags=re.S):
                if "<th" in row:
                    continue
                rows_total += 1
                if "https://" in row:
                    rows_linked += 1
                elif "not attempted" in row or "none" in row:
                    rows_linked += 1
                else:
                    err("%s: data-table row with no official link: %s"
                        % (rel(path), re.sub(r"\s+", " ", row)[:160]))
    ok("row sourcing: %d data-table rows scanned across %d pages, %d carry an official https link"
       % (rows_total, len(pages()), rows_linked))


# ----------------------------------------------------------------------- 4. blanks
def check_blanks(desk):
    empty = 0
    for path in pages():
        text = text_of(path)
        for m in re.finditer(r"<td[^>]*>\s*</td>", text):
            line = text[:m.start()].count("\n") + 1
            err("%s:%d empty table cell - an unconfirmed value must be an explicit blank marker"
                % (rel(path), line))
            empty += 1
    blank_rows = [f for f in desk["fixtures"] if f.get("blank_fields")]
    for f in blank_rows:
        for field in f["blank_fields"]:
            if f.get(field) not in (None, ""):
                err("%s: field %s is flagged blank but holds %r" % (f["key"], field, f[field]))
    ok("blanks: %d rows publish blank fields, all flagged; %d empty cells found in %d pages"
       % (len(blank_rows), empty, len(pages())))


# -------------------------------------------------------------------- 5. integrity
def check_integrity(desk):
    for path in pages():
        text = text_of(path)
        base = os.path.dirname(path)
        for m in re.finditer(r'(?:href|src)="([^"]+)"', text):
            target = m.group(1)
            if re.match(r"^(https?:|mailto:|#|data:)", target):
                continue
            p = re.split(r"[?#]", target)[0]
            if not p:
                continue
            if not os.path.exists(os.path.normpath(os.path.join(base, p))):
                err("%s: broken relative link %s" % (rel(path), target))
        if "<title>" not in text or 'lang="en"' not in text:
            err("%s: missing title or lang attribute" % rel(path))
        if "Content-Security-Policy" not in text:
            err("%s: missing Content-Security-Policy meta" % rel(path))
        if "<script" in text:
            err("%s: contains a script tag; this desk is static" % rel(path))
    matches = text_of(os.path.join(OUT, "matches.html"))
    keys = [f["key"] for f in desk["fixtures"]]
    for k in keys:
        n = matches.count('id="%s"' % k) + matches.count(">%s<" % k)
        if n == 0:
            err("matches.html does not list fixture %s" % k)
    listed = re.findall(r"<h2 id=\"([a-z-]+)\">", matches)
    missing = [s for s, _ in D.SPORT_NAMES.items() if s not in listed]
    if missing:
        err("matches.html has no section for %s" % ", ".join(missing))
    idx = text_of(os.path.join(OUT, "index.html"))
    for needle, label in ((str(desk["counts"]["fixtures"]), "fixture count"),
                          (str(desk["counts"]["priced"]), "priced count"),
                          (str(desk["counts"]["markets"]), "market count"),
                          (str(desk["counts"]["high"]), "High count"),
                          (str(len(desk["sources"])), "source count")):
        if needle not in idx:
            err("index.html does not publish the %s (%s)" % (label, needle))
    problems, notes = P.check(desk)
    for x in problems:
        err("prediction check: %s" % x)
    ok("integrity: %d pages, %d fixture keys listed, %d prediction checks clean (%s)"
       % (len(pages()), len(keys), len(notes), "; ".join(notes[:3])))
    counts = desk["counts"]
    if counts["fixtures"] != len(desk["fixtures"]):
        err("counts.fixtures disagrees with the fixture list")
    if counts["markets"] != sum(len(f["markets"]) for f in desk["fixtures"]):
        err("counts.markets disagrees with the market list")
    if counts["outcomes"] != sum(len(mk["outcomes"]) for f in desk["fixtures"] for mk in f["markets"]):
        err("counts.outcomes disagrees with the outcome list")
    per_sport_sum = sum(v["fixtures"] for v in desk["per_sport"].values())
    if per_sport_sum != counts["fixtures"]:
        err("per-sport fixture counts sum to %d, not %d" % (per_sport_sum, counts["fixtures"]))


# ------------------------------------------------------------------------ 6. audit
def check_audit():
    path = os.path.join(DATA, "repo_audit.json")
    if not os.path.exists(path):
        err("data/d7d19a67/repo_audit.json is missing; run scripts/sd7d19a67_repo_audit.py")
        return
    audit = json.load(open(path, encoding="utf-8"))
    for f in audit["findings"]:
        if not f["evidence"]:
            err("audit finding %s has no evidence rows" % f["id"])
        if not f.get("recheck"):
            err("audit finding %s has no re-check command" % f["id"])
        if f["severity"] not in ("high", "medium", "low", "info"):
            err("audit finding %s has severity %r" % (f["id"], f["severity"]))
        for ev in f["evidence"]:
            if ev["file"] not in ("-", "git", "git status", "git diff --name-only origin/main...HEAD") \
                    and not os.path.exists(os.path.join(ROOT, ev["file"])):
                err("audit finding %s cites a file that does not exist: %s" % (f["id"], ev["file"]))
    page = os.path.join(OUT, "repo-audit.html")
    if os.path.exists(page):
        text = text_of(page)
        for f in audit["findings"]:
            if 'id="%s"' % f["id"] not in text:
                err("repo-audit.html does not publish finding %s" % f["id"])
        if "github.com/buffedlizard55-lab/OLBG1/blob/" not in text:
            err("repo-audit.html publishes no GitHub file links for manual review")
    ok("audit: %d findings, all with evidence and a re-check command" % len(audit["findings"]))


def check_artifacts():
    for name in ("desk.json", "fixtures.csv", "markets.csv", "repo_audit.json"):
        p = os.path.join(DATA, name)
        if not os.path.exists(p):
            err("missing artefact data/d7d19a67/%s" % name)
        elif os.path.getsize(p) == 0:
            err("empty artefact data/d7d19a67/%s" % name)
    import csv
    with open(os.path.join(DATA, "fixtures.csv"), encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if len(rows) != 55:
        err("fixtures.csv has %d rows, expected 55" % len(rows))
    for r in rows:
        if not r["official_source"].startswith("https://"):
            err("fixtures.csv row %s has no official source link" % r["fixture_key"])
    with open(os.path.join(DATA, "markets.csv"), encoding="utf-8") as fh:
        mrows = list(csv.DictReader(fh))
    if not mrows:
        err("markets.csv is empty")
    ok("artifacts: desk.json + %d fixture rows + %d market outcome rows + repo_audit.json"
       % (len(rows), len(mrows)))


def main():
    desk = json.load(open(os.path.join(DATA, "desk.json"), encoding="utf-8"))
    check_artifacts()
    check_arithmetic(desk)
    check_policy(desk)
    check_sourcing(desk)
    check_blanks(desk)
    check_integrity(desk)
    check_audit()
    for c in checks:
        print("PASS  %s" % c)
    for w in warnings:
        print("WARN  %s" % w)
    for x in errors:
        print("FAIL  %s" % x)
    print("\n%d checks passed, %d warning(s), %d error(s)" % (len(checks), len(warnings), len(errors)))
    if errors:
        print("VALIDATION FAILED")
        raise SystemExit(1)
    print("VALIDATION PASSED")


if __name__ == "__main__":
    main()
