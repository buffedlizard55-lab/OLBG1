"""Gate for the T2988 desk. Re-derives every published price from the published inputs."""
import json
import math
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "2988bd19"
DESK = ROOT / "data" / "2988bd19" / "desk.json"

errors = []
warnings = []


def err(m):
    errors.append(m)


def warn(m):
    warnings.append(m)


def poisson(lam, n=26):
    return [math.exp(-lam) * lam ** k / math.factorial(k) for k in range(n)]


def rederive(lh, la, key):
    n = 26
    dh, da = poisson(lh, n), poisson(la, n)
    win = sum(dh[i] * da[j] for i in range(n) for j in range(n) if i > j) + 0.5 * sum(dh[i] * da[i] for i in range(n))
    hm1 = sum(dh[i] * da[j] for i in range(n) for j in range(n) if i - j >= 2)
    hm2 = sum(dh[i] * da[j] for i in range(n) for j in range(n) if i - j >= 3)
    am1 = sum(dh[i] * da[j] for i in range(n) for j in range(n) if j - i >= 2)
    am2 = sum(dh[i] * da[j] for i in range(n) for j in range(n) if j - i >= 3)
    fixed = {"home_ml": win, "away_ml": 1 - win,
             "home_-1.5": hm1, "away_+1.5": 1 - hm1, "home_+1.5": 1 - am1, "away_-1.5": am1,
             "home_-2.5": hm2, "away_+2.5": 1 - hm2, "home_+2.5": 1 - am2, "away_-2.5": am2}
    if key in fixed:
        return fixed[key]
    m = re.fullmatch(r"(p1_)?(home|away)?_?(over|under)_(\d+\.5)", key)
    if not m:
        raise KeyError(key)
    p1, side, direction, line = m.group(1), m.group(2), m.group(3), float(m.group(4))
    if p1:
        lh, la = lh / 3, la / 3
        n = 9
        dh, da = poisson(lh, n), poisson(la, n)
        over = 1 - sum(dh[i] * da[j] for i in range(n) for j in range(n) if i + j <= int(line))
    elif side is None:
        over = 1 - sum(dh[i] * da[j] for i in range(n) for j in range(n) if i + j <= int(line))
    else:
        d = dh if side == "home" else da
        over = 1 - sum(d[:int(line) + 1])
    return over if direction == "over" else 1 - over


def main():
    desk = json.loads(DESK.read_text())
    sources = {s["id"]: s for s in desk["sources"]}

    # --- sources
    for s in desk["sources"]:
        if not str(s["url"]).startswith("http"):
            err(f"source {s['id']} has no http URL")
        if not re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z$", s["read_at"]):
            err(f"source {s['id']} read_at is not an ISO UTC stamp: {s['read_at']}")

    # --- fixtures
    for f in desk["fixtures"]:
        if not f["sources"]:
            err(f"fixture {f['id']} has no source ids")
        for sid in f["sources"]:
            if sid not in sources:
                err(f"fixture {f['id']} cites unknown source {sid}")
        if f["verification"] == "official":
            if not f.get("official_url"):
                err(f"official fixture {f['id']} has no official URL")
            if not f.get("start_utc"):
                err(f"official fixture {f['id']} has no UTC start")
        else:
            if f.get("priced"):
                err(f"discovery fixture {f['id']} must not be priced")
            if f.get("official_url"):
                err(f"discovery fixture {f['id']} must not claim an official URL")

    # --- prices re-derived
    checked = 0
    markets = {m["id"]: m for m in desk["markets"]}
    for m in desk["markets"]:
        for g in m["groups"]:
            for s in g["selections"]:
                key = s["id"].split(":", 1)[1]
                p = rederive(m["lambda_home"], m["lambda_away"], key)
                if abs(p - s["p"]) > 2e-6:
                    err(f"price mismatch {s['id']}: published {s['p']} re-derived {p:.6f}")
                if abs(s["fair_decimal"] - round(1 / s["p"], 4)) > 1e-9:
                    err(f"fair decimal mismatch {s['id']}")
                am = -100 * s["p"] / (1 - s["p"]) if s["p"] >= 0.5 else 100 * (1 - s["p"]) / s["p"]
                if abs(am - s["american"]) > 0.01:
                    err(f"american mismatch {s['id']}: {s['american']} vs {am:.2f}")
                checked += 1

    # --- high gate
    high = desk["high_selections"]
    if not high:
        warn("no High selections published")
    pred_sel = {p["selection"] for p in desk["predictions"]}
    for s in high:
        if not (0.70 < s["p"] <= 0.7142857 + 1e-9):
            err(f"High selection {s['id']} is outside the window: {s['p']}")
        if s["id"] not in pred_sel:
            err(f"High selection {s['id']} has no written prediction")
        if 1.40 < s["fair_decimal"] < 1.41:
            warn(f"High selection {s['id']} is within 0.01 of the -250 decimal floor")
    for s in desk["capped_in_band"]:
        if s["tier"] == "High":
            err(f"capped selection {s['id']} is labelled High")

    # --- predictions
    bodies = []
    for p in desk["predictions"]:
        words = len(p["body"].split())
        if words < 30:
            err(f"prediction {p['id']} is only {words} words")
        if p["selection"] not in {s["id"] for m in desk["markets"] for g in m["groups"] for s in g["selections"]}:
            err(f"prediction {p['id']} points at an unknown selection")
        for _, sid in p["facts"]:
            if sid not in sources:
                err(f"prediction {p['id']} cites unknown source {sid}")
        for term in ("Selection:",):
            if term not in p["body"]:
                err(f"prediction {p['id']} does not state the selection explicitly")
        bodies.append((p["id"], p["body"].lower()))

    def shingles(text, k=8):
        w = re.findall(r"[a-z0-9']+", text)
        return {" ".join(w[i:i + k]) for i in range(len(w) - k + 1)}

    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            overlap = shingles(bodies[i][1]) & shingles(bodies[j][1])
            if overlap:
                err(f"predictions {bodies[i][0]} and {bodies[j][0]} share {len(overlap)} eight-word phrases")

    # --- coverage and counts
    cov = desk["coverage"]
    if len(cov) != 17:
        err(f"coverage lists {len(cov)} sports, expected 17")
    priced_fixtures = sum(1 for f in desk["fixtures"] if f.get("priced"))
    if desk["counts"]["priced_fixtures"] != priced_fixtures:
        err("count mismatch: priced fixtures")
    if desk["counts"]["priced_selections"] != checked:
        err("count mismatch: priced selections")
    for c in cov:
        if c["priced"] > c["verified"]:
            err(f"coverage for {c['sport']} prices more than it verifies")

    # --- HTML link and anchor integrity
    pages = list(SITE.rglob("*.html"))
    ids = {}
    for p in pages:
        text = p.read_text(encoding="utf-8")
        ids[p.resolve()] = set(re.findall(r'id="([^"]+)"', text))
    link_count = 0
    for p in pages:
        text = p.read_text(encoding="utf-8")
        for href in re.findall(r'href="([^"]+)"', text):
            if href.startswith(("http://", "https://", "mailto:", "#")):
                continue
            link_count += 1
            target = (p.parent / href.split("#")[0]).resolve()
            if not target.exists():
                err(f"{p.relative_to(ROOT)}: broken link {href}")
                continue
            if "#" in href:
                frag = href.split("#", 1)[1]
                if target.suffix == ".html" and frag not in ids.get(target, set()):
                    err(f"{p.relative_to(ROOT)}: unresolved anchor {href}")

    # --- no placeholder wording
    bad = re.compile(r"\b(TBD|TODO|lorem ipsum|placeholder|XXX)\b", re.I)
    for p in pages:
        if bad.search(p.read_text(encoding="utf-8")):
            err(f"{p.relative_to(ROOT)} contains placeholder wording")

    # --- summary
    print(f"pages={len(pages)} links={link_count} prices_rederived={checked} "
          f"high={len(high)} predictions={len(desk['predictions'])} flags={len(desk['flags'])}")
    for w in warnings:
        print("  WARN:", w)
    if errors:
        print("T2988 VALIDATION FAILED")
        for m in errors[:40]:
            print("  ERR:", m)
        sys.exit(1)
    print("T2988 VALIDATION PASSED — 0 errors,", len(warnings), "warnings")


if __name__ == "__main__":
    main()
